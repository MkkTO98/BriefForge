"""Secure, bounded, local-only BCRP JSON bundle loading."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

from .model import BCRPBundle, BCRPRecord, BUNDLE_FORMAT, PROFILE_ID, PROFILE_VERSION

MAX_DOCUMENT_BYTES = 1_000_000
MAX_RECORDS = 128
MAX_NESTING = 64
MAX_CONTAINER_ITEMS = 20_000


class BundleLoadError(ValueError):
    """Raised when transport admission cannot safely produce a profile instance."""


def _reject_constant(value: str) -> None:
    raise BundleLoadError(f"non-standard JSON constant is prohibited: {value}")


def _reject_float(value: str) -> None:
    raise BundleLoadError(f"floating-point JSON number is prohibited; use a structured exact decimal: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BundleLoadError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def loads_json_bytes(data: bytes, *, source: str = "JSON document") -> Any:
    if len(data) > MAX_DOCUMENT_BYTES:
        raise BundleLoadError(f"{source} exceeds the {MAX_DOCUMENT_BYTES}-byte bound")
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise BundleLoadError(f"{source} is not strict UTF-8") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
            parse_float=_reject_float,
        )
    except BundleLoadError:
        raise
    except (json.JSONDecodeError, RecursionError) as exc:
        message = "excessive JSON nesting" if isinstance(exc, RecursionError) else f"malformed JSON: {exc.msg}"
        raise BundleLoadError(f"{source}: {message}") from exc
    _inspect_transport_value(value, source=source)
    return value


def _inspect_transport_value(value: Any, *, source: str, depth: int = 0) -> int:
    if depth > MAX_NESTING:
        raise BundleLoadError(f"{source} exceeds the permitted JSON nesting depth")
    if value is None:
        raise BundleLoadError(f"{source} contains transport null; semantic states must be explicit")
    if isinstance(value, float):
        raise BundleLoadError(f"{source} contains a floating-point JSON number")
    if isinstance(value, str):
        try:
            value.encode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise BundleLoadError(f"{source} contains malformed Unicode") from exc
        return 1
    if isinstance(value, dict):
        count = len(value)
        for key, child in value.items():
            count += _inspect_transport_value(key, source=source, depth=depth + 1)
            count += _inspect_transport_value(child, source=source, depth=depth + 1)
            if count > MAX_CONTAINER_ITEMS:
                raise BundleLoadError(f"{source} exceeds the permitted container-item bound")
        return count
    if isinstance(value, list):
        count = len(value)
        for child in value:
            count += _inspect_transport_value(child, source=source, depth=depth + 1)
            if count > MAX_CONTAINER_ITEMS:
                raise BundleLoadError(f"{source} exceeds the permitted container-item bound")
        return count
    if isinstance(value, (bool, int)):
        return 1
    raise BundleLoadError(f"{source} contains unsupported transport value {type(value).__name__}")


def _supported_profile(identity: str, version: str) -> None:
    if identity != PROFILE_ID:
        raise BundleLoadError(f"unsupported profile identity: {identity!r}")
    try:
        major = int(version.split(".", 1)[0])
    except (ValueError, AttributeError) as exc:
        raise BundleLoadError(f"invalid profile version: {version!r}") from exc
    if major != int(PROFILE_VERSION.split(".", 1)[0]):
        raise BundleLoadError(f"unsupported profile major version: {version!r}")


def _safe_location(root: Path, location: str) -> Path:
    if not isinstance(location, str) or not location:
        raise BundleLoadError("record location must be a non-empty bundle-relative path")
    posix = PurePosixPath(location)
    if posix.is_absolute() or ".." in posix.parts or "." in posix.parts or "\\" in location:
        raise BundleLoadError(f"record location must be a safe bundle-relative path: {location!r}")
    resolved_root = root.resolve()
    resolved = (resolved_root / Path(*posix.parts)).resolve()
    if not resolved.is_relative_to(resolved_root):
        raise BundleLoadError(f"record location escapes bundle root and is not bundle-relative: {location!r}")
    return resolved


def _collect_defined_identities(records: list[BCRPRecord]) -> None:
    seen: set[str] = set()

    def visit(value: Any, location: str) -> None:
        if isinstance(value, dict):
            object_id = value.get("id")
            if isinstance(object_id, str):
                if object_id in seen:
                    raise BundleLoadError(f"duplicate semantic identity: {object_id!r} at {location}")
                seen.add(object_id)
            for key, child in value.items():
                visit(child, f"{location}/{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{location}/{index}")

    for record in records:
        if record.identity in seen:
            raise BundleLoadError(f"duplicate semantic identity: {record.identity!r}")
        seen.add(record.identity)
        visit(record.semantic, record.identity)
        visit(record.extensions, f"{record.identity}/extensions")


def load_bundle(root: str | Path) -> BCRPBundle:
    """Load one deterministic local BCRP bundle without following external references."""

    bundle_root = Path(root)
    index_path = bundle_root / "bundle.json"
    try:
        index_data = index_path.read_bytes()
    except OSError as exc:
        raise BundleLoadError(f"cannot read bundle index {index_path}: {exc}") from exc
    index = loads_json_bytes(index_data, source="bundle index")
    if not isinstance(index, dict):
        raise BundleLoadError("bundle index must be a JSON object")
    if index.get("format") != BUNDLE_FORMAT:
        raise BundleLoadError(f"unsupported bundle format: {index.get('format')!r}")
    profile = index.get("profile")
    if not isinstance(profile, dict):
        raise BundleLoadError("bundle index requires a profile declaration")
    _supported_profile(profile.get("identity", ""), profile.get("version", ""))
    entries = index.get("records")
    if not isinstance(entries, list) or not entries:
        raise BundleLoadError("bundle index requires a non-empty records inventory")
    if len(entries) > MAX_RECORDS:
        raise BundleLoadError(f"bundle contains more than {MAX_RECORDS} records")

    locations: set[str] = set()
    identities: set[str] = set()
    records: list[BCRPRecord] = []
    for position, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise BundleLoadError(f"bundle record inventory entry {position} must be an object")
        location = entry.get("location")
        if location in locations:
            raise BundleLoadError(f"duplicate transport location: {location!r}")
        locations.add(location)
        declared_identity = entry.get("identity")
        if declared_identity in identities:
            raise BundleLoadError(f"duplicate semantic identity: {declared_identity!r}")
        identities.add(declared_identity)
        if entry.get("profile_version") != profile["version"]:
            raise BundleLoadError(f"record inventory profile-version mismatch for {declared_identity!r}")
        path = _safe_location(bundle_root, location)
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise BundleLoadError(f"cannot read indexed record {location!r}: {exc}") from exc
        declared_digest = entry.get("transport_sha256")
        if declared_digest and hashlib.sha256(data).hexdigest() != declared_digest:
            raise BundleLoadError(f"transport integrity mismatch for {location!r}")
        document = loads_json_bytes(data, source=f"record {location}")
        if not isinstance(document, dict):
            raise BundleLoadError(f"record {location!r} must be a JSON object")
        record = BCRPRecord.from_document(document)
        if record.kind != entry.get("record_kind"):
            raise BundleLoadError(f"record-kind declaration mismatch for {location!r}")
        if record.identity != declared_identity:
            raise BundleLoadError(f"record identity declaration mismatch for {location!r}")
        record_profile = document.get("profile", {})
        if record_profile.get("identity") != profile["identity"] or record_profile.get("version") != profile["version"]:
            raise BundleLoadError(f"record profile declaration mismatch for {location!r}")
        records.append(record)

    _collect_defined_identities(records)
    records.sort(key=lambda record: (record.kind, record.identity))
    return BCRPBundle(
        profile_identity=profile["identity"],
        profile_version=profile["version"],
        records=tuple(records),
        index=index,
        source_root=bundle_root.resolve(),
    )
