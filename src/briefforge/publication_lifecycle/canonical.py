"""Canonical event bytes and domain-separated lifecycle-event fingerprints."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import re
import unicodedata
from typing import Any

from .model import (
    CANONICALIZATION_ID,
    PROFILE_ID,
    PROFILE_VERSION,
    LifecycleFingerprint,
    PublicationLifecycleEvent,
)

_TIMESTAMP_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})T(?P<time>\d{2}:\d{2}:\d{2})(?P<fraction>\.\d{1,6})?(?P<offset>Z|[+-]\d{2}:\d{2})$"
)


def canonicalize_timestamp(value: str) -> str:
    if not isinstance(value, str) or not _TIMESTAMP_RE.fullmatch(value):
        raise ValueError("lifecycle timestamp requires seconds and an explicit offset")
    parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    utc = parsed.astimezone(timezone.utc)
    base = utc.strftime("%Y-%m-%dT%H:%M:%S")
    if utc.microsecond:
        base += "." + f"{utc.microsecond:06d}".rstrip("0")
    return base + "Z"


def _text(value: str) -> str:
    return unicodedata.normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n"))


def _sort_token(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


_UNORDERED_SEQUENCE_PATHS = {
    ("record", "semantic", "predecessor_event_refs"),
    ("record", "extensions"),
    ("record", "extensions", "[]", "target_refs"),
}


def _normalize(value: Any, *, path: tuple[str, ...] = ()) -> Any:
    key = path[-1] if path else ""
    if isinstance(value, str):
        return canonicalize_timestamp(value) if key == "event_time" else _text(value)
    if isinstance(value, bool) or isinstance(value, int):
        return value
    if value is None or isinstance(value, float):
        raise ValueError("lifecycle canonical form does not admit null or float")
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        original_keys: dict[str, str] = {}
        for name, child in value.items():
            if not isinstance(name, str):
                raise ValueError("lifecycle canonical object keys must be strings")
            normalized_name = _text(name)
            if normalized_name in normalized:
                raise ValueError(
                    f"Unicode normalization creates a duplicate object key: {original_keys[normalized_name]!r} and {name!r}"
                )
            original_keys[normalized_name] = name
            normalized[normalized_name] = _normalize(child, path=path + (normalized_name,))
        return {name: normalized[name] for name in sorted(normalized)}
    if isinstance(value, (list, tuple)):
        normalized = [_normalize(item, path=path + ("[]",)) for item in value]
        if path in _UNORDERED_SEQUENCE_PATHS:
            normalized.sort(key=_sort_token)
        return normalized
    raise ValueError(f"unsupported lifecycle canonical value {type(value).__name__}")


def event_document(event: PublicationLifecycleEvent) -> dict[str, Any]:
    semantic: dict[str, Any] = {
        "publication_identity": event.publication_identity,
        "event_type": event.event_type,
        "target_release": {"identity": event.target_release.identity, "fingerprint": event.target_release.fingerprint},
        "reason_classification": event.reason_classification,
        "reason_detail": event.reason_detail,
        "authority": {
            "identity": event.authority.identity,
            "owner": event.authority.owner,
            "role": event.authority.role,
        },
        "policy_identity": event.policy_identity,
        "event_time": event.event_time,
        "predecessor_event_refs": list(event.predecessor_event_refs),
        "distribution_consequence": event.distribution_consequence,
    }
    if event.predecessor_release is not None:
        semantic["predecessor_release"] = {
            "identity": event.predecessor_release.identity,
            "fingerprint": event.predecessor_release.fingerprint,
        }
    if event.successor_release is not None:
        semantic["successor_release"] = {
            "identity": event.successor_release.identity,
            "fingerprint": event.successor_release.fingerprint,
        }
    extensions = [json.loads(document) for document in event.extension_documents]
    return {
        "record_kind": "PublicationLifecycleEventRecord",
        "identity": event.identity,
        "profile": {"identity": event.profile_identity, "version": event.profile_version},
        "semantic": semantic,
        "extensions": extensions,
    }


def canonical_event_bytes(event: PublicationLifecycleEvent) -> bytes:
    if event.profile_identity != PROFILE_ID or event.profile_version != PROFILE_VERSION:
        raise ValueError("unsupported lifecycle profile identity or version")
    canonical = {
        "domain": "lifecycle-event-semantic",
        "format": "briefforge-publication-lifecycle-event-canonical-json-v1",
        "profile": {"identity": event.profile_identity, "version": event.profile_version},
        "record": _normalize(event_document(event), path=("record",)),
    }
    return json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def fingerprint_event(event: PublicationLifecycleEvent) -> LifecycleFingerprint:
    canonical = canonical_event_bytes(event)
    return LifecycleFingerprint(
        domain="lifecycle-event-semantic",
        root_identity=event.identity,
        profile_identity=event.profile_identity,
        profile_version=event.profile_version,
        canonicalization=CANONICALIZATION_ID,
        algorithm="sha256",
        digest=hashlib.sha256(canonical).hexdigest(),
        scope="One immutable lifecycle event, exact Release bindings, authority, policy, causal references, consequence, and preservable extensions",
    )
