"""BCRP semantic canonicalization, canonical JSON, equality, and fingerprints."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import re
import unicodedata
from typing import Any

from .graph import reconstruct_graph
from .loader import BundleLoadError, loads_json_bytes
from .model import (
    BCRPBundle,
    BCRPRecord,
    BUNDLE_FORMAT,
    CANONICALIZATION_ID,
    Fingerprint,
    PROFILE_ID,
)
from .structure import validate_structure

ORDERED_LIST_KEYS = {
    "children",
    "executed_layers",
    "fallback_refs",
    "lifecycle_events",
    "narrative_sequence",
    "print_expression",
    "state_ids",
    "statement_ids",
    "statements",
    "static_expression",
}
OWNED_TIMESTAMP_KEYS = {
    "conformance_time",
    "event_time",
    "intake_time",
    "invocation_time",
    "manifest_time",
    "publication_time",
    "readiness_time",
    "validation_time",
}
DOMAINS = {
    "candidate-semantic",
    "profile-instance",
    "release-semantic",
    "artifact-bytes",
    "manifest-instance",
}
_TIMESTAMP_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})T(?P<time>\d{2}:\d{2}:\d{2})(?P<fraction>\.\d{1,6})?(?P<offset>Z|[+-]\d{2}:\d{2})$"
)


def canonicalize_exact_decimal(value: dict[str, Any]) -> dict[str, Any]:
    """Return exact coefficient-and-scale normal form without binary floating point."""

    if set(value) != {"coefficient", "scale"}:
        raise ValueError("exact decimal requires exactly coefficient and scale")
    coefficient = value["coefficient"]
    scale = value["scale"]
    if not isinstance(coefficient, str) or not re.fullmatch(r"-?[0-9]+", coefficient):
        raise ValueError("exact-decimal coefficient must be an integer string")
    if not isinstance(scale, int) or isinstance(scale, bool) or scale < 0:
        raise ValueError("exact-decimal scale must be a non-negative integer")
    integer = int(coefficient)
    if integer == 0:
        return {"coefficient": "0", "scale": 0}
    while scale > 0 and integer % 10 == 0:
        integer //= 10
        scale -= 1
    return {"coefficient": str(integer), "scale": scale}


def canonicalize_timestamp(value: str) -> str:
    """Normalize an admitted BriefForge-owned timestamp to UTC."""

    if not isinstance(value, str) or not _TIMESTAMP_RE.fullmatch(value):
        raise ValueError("BCRP timestamp requires seconds and an explicit offset")
    normalized_input = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized_input)
    except ValueError as exc:
        raise ValueError(f"invalid BCRP timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        raise ValueError("BCRP timestamp requires an explicit offset")
    utc = parsed.astimezone(timezone.utc)
    base = utc.strftime("%Y-%m-%dT%H:%M:%S")
    if utc.microsecond:
        fraction = f"{utc.microsecond:06d}".rstrip("0")
        base += f".{fraction}"
    return base + "Z"


def _normal_text(value: str) -> str:
    return unicodedata.normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n"))


def _sort_token(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _canonicalize(value: Any, *, key: str = "", semantic_domain: bool = False) -> Any:
    if isinstance(value, str):
        if key in OWNED_TIMESTAMP_KEYS:
            return canonicalize_timestamp(value)
        return _normal_text(value)
    if isinstance(value, bool) or isinstance(value, int):
        return value
    if isinstance(value, float) or value is None:
        raise ValueError("BCRP canonical form does not admit float or null")
    if isinstance(value, dict):
        if set(value) == {"coefficient", "scale"}:
            return canonicalize_exact_decimal(value)
        result: dict[str, Any] = {}
        for child_key, child in value.items():
            if child_key in {"comments", "comment", "locator", "transport_location", "transport_sha256", "derived_reverse_index"}:
                continue
            result[_normal_text(child_key)] = _canonicalize(child, key=child_key, semantic_domain=semantic_domain)
        return {name: result[name] for name in sorted(result)}
    if isinstance(value, (list, tuple)):
        items = [_canonicalize(child, key=key, semantic_domain=semantic_domain) for child in value]
        if key not in ORDERED_LIST_KEYS:
            items.sort(key=_sort_token)
        return items
    raise ValueError(f"unsupported BCRP canonical value {type(value).__name__}")


def _canonical_extensions(extensions: list[dict[str, Any]], *, semantic_domain: bool) -> list[dict[str, Any]]:
    admitted = []
    for extension in extensions:
        if semantic_domain and extension.get("character") == "display-only":
            continue
        admitted.append(_canonicalize(extension, key="extensions", semantic_domain=semantic_domain))
    admitted.sort(
        key=lambda item: (
            item.get("owner_namespace", ""),
            item.get("name", ""),
            item.get("version", ""),
            item.get("scope", ""),
            _sort_token(item.get("target_refs", [])),
        )
    )
    return admitted


def _canonical_record(record: BCRPRecord, *, semantic_domain: bool) -> dict[str, Any]:
    return {
        "extensions": _canonical_extensions(record.extensions, semantic_domain=semantic_domain),
        "identity": _normal_text(record.identity),
        "profile": {"identity": PROFILE_ID, "version": record.profile_version},
        "record_kind": record.kind,
        "semantic": _canonicalize(record.semantic, key="semantic", semantic_domain=semantic_domain),
    }


def _domain_records(bundle: BCRPBundle, domain: str) -> tuple[BCRPRecord, ...]:
    if domain == "profile-instance":
        return bundle.records
    if domain == "candidate-semantic":
        candidates = bundle.records_of_kind("CandidatePresentationPackageRecord")
        if len(candidates) != 1:
            raise ValueError("candidate-semantic domain requires exactly one Candidate record")
        candidate = candidates[0]
        dependencies = {candidate.identity, candidate.semantic.get("brief_ref")}
        dependencies.update(candidate.semantic.get("material_refs", []))
        return tuple(record for record in bundle.records if record.identity in dependencies)
    if domain == "release-semantic":
        return bundle.records_of_kind("PublicationReleaseRecord")
    if domain == "manifest-instance":
        return bundle.records_of_kind("PublicationManifestRecord")
    if domain == "artifact-bytes":
        return bundle.records_of_kind("GeneratedArtifactAuditRecord")
    raise ValueError(f"unknown fingerprint/canonicalization domain {domain!r}")


def canonical_json_bytes(
    bundle: BCRPBundle,
    *,
    domain: str = "profile-instance",
    require_valid: bool = True,
) -> bytes:
    """Serialize a named BCRP equality domain to deterministic canonical JSON bytes."""

    if domain not in DOMAINS:
        raise ValueError(f"unknown BCRP canonicalization domain: {domain!r}")
    if require_valid:
        structural_findings = validate_structure(bundle)
        if structural_findings:
            raise ValueError("canonicalization prerequisites failed: structural validation did not pass")
        reconstruct_graph(bundle)
    semantic_domain = domain in {"candidate-semantic", "release-semantic"}
    records = [_canonical_record(record, semantic_domain=semantic_domain) for record in _domain_records(bundle, domain)]
    records.sort(key=lambda record: (record["record_kind"], record["identity"]))
    document = {
        "format": "briefforge-bcrp-canonical-json-v1",
        "profile": {"identity": bundle.profile_identity, "version": bundle.profile_version},
        "domain": domain,
        "records": records,
    }
    return json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def bundle_from_canonical_json(data: bytes) -> BCRPBundle:
    """Reload a canonical profile-instance serialization without transport locators."""

    document = loads_json_bytes(data, source="canonical BCRP JSON")
    if not isinstance(document, dict) or document.get("format") != "briefforge-bcrp-canonical-json-v1":
        raise BundleLoadError("unsupported canonical BCRP JSON document")
    if document.get("domain") != "profile-instance":
        raise BundleLoadError("only a profile-instance canonical document can reconstruct a complete bundle")
    profile = document.get("profile", {})
    records = document.get("records")
    if not isinstance(records, list):
        raise BundleLoadError("canonical BCRP JSON requires records")
    instance = BCRPBundle(
        profile_identity=profile.get("identity", ""),
        profile_version=profile.get("version", ""),
        records=tuple(BCRPRecord.from_document(record) for record in records),
        index={"format": BUNDLE_FORMAT, "canonical_reload": True},
    )
    structural = validate_structure(instance)
    if structural:
        raise BundleLoadError(f"canonical BCRP JSON failed structure validation: {structural[0].message}")
    reconstruct_graph(instance)
    return instance


def _root_identity(bundle: BCRPBundle, domain: str) -> str:
    kind_by_domain = {
        "candidate-semantic": "CandidatePresentationPackageRecord",
        "release-semantic": "PublicationReleaseRecord",
        "manifest-instance": "PublicationManifestRecord",
        "artifact-bytes": "GeneratedArtifactAuditRecord",
    }
    if domain == "profile-instance":
        return f"profile:{bundle.profile_identity}:{bundle.profile_version}"
    records = bundle.records_of_kind(kind_by_domain[domain])
    if len(records) != 1:
        raise ValueError(f"{domain} requires exactly one root record")
    return records[0].identity


def fingerprint_bundle(bundle: BCRPBundle, *, domain: str, require_valid: bool = True) -> Fingerprint:
    """Compute a SHA-256 digest with explicit equality domain and scope metadata."""

    if require_valid:
        from .validation import validate_bundle

        result = validate_bundle(bundle, through_layer="L2" if domain == "candidate-semantic" else None)
        if result.blocking:
            raise ValueError("fingerprint prerequisites failed: blocking validation findings exist")
    canonical = canonical_json_bytes(bundle, domain=domain, require_valid=require_valid)
    root = _root_identity(bundle, domain)
    scopes = {
        "candidate-semantic": "Candidate and transitive canonical Brief/Material semantic dependencies; derivative lifecycle, renderer, artifact, and manifest records excluded",
        "profile-instance": "All retained BCRP records and preservable extensions; transport index, locators, comments, and reverse indexes excluded",
        "release-semantic": "Release identity/version, Ready fingerprint, evidence snapshots, authority, and lifecycle substance; artifacts/manifests excluded",
        "artifact-bytes": "Generated artifact identity and declared byte digest inventory",
        "manifest-instance": "Derivative manifest profile content under its declared projection version",
    }
    return Fingerprint(
        domain=domain,
        root_identity=root,
        profile_identity=bundle.profile_identity,
        profile_version=bundle.profile_version,
        canonicalization=CANONICALIZATION_ID,
        algorithm="sha256",
        digest=hashlib.sha256(canonical).hexdigest(),
        scope=scopes[domain],
    )


def semantic_equal(left: BCRPBundle, right: BCRPBundle) -> bool:
    return canonical_json_bytes(left, domain="candidate-semantic", require_valid=False) == canonical_json_bytes(
        right, domain="candidate-semantic", require_valid=False
    )


def profile_instance_equal(left: BCRPBundle, right: BCRPBundle) -> bool:
    return canonical_json_bytes(left, domain="profile-instance", require_valid=False) == canonical_json_bytes(
        right, domain="profile-instance", require_valid=False
    )


def artifact_equal(left: dict[str, bytes], right: dict[str, bytes]) -> bool:
    if set(left) != set(right):
        return False
    return all(left[path] == right[path] for path in left)


def presentation_equivalent(bundle: BCRPBundle, conformance_identity: str) -> bool:
    """Return an existing validation claim; canonical bytes alone never establish it."""

    matches = [record for record in bundle.records if record.identity == conformance_identity]
    if len(matches) != 1 or matches[0].kind != "SemanticArtifactConformanceRecord":
        return False
    record = matches[0]
    return bool(record.semantic.get("audit_link_pass") and record.semantic.get("semantic_pass") and record.semantic.get("evidence"))
