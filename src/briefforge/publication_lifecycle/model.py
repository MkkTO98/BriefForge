"""Immutable model for the separately negotiated publication lifecycle profile."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

PROFILE_ID = "briefforge-publication-lifecycle-event-profile"
PROFILE_VERSION = "1.0.0"
BUNDLE_FORMAT = "briefforge-publication-lifecycle-event-json-bundle-v1"
CANONICALIZATION_ID = "publication-lifecycle-event-canonicalization:1.0.0"
EVENT_KIND = "PublicationLifecycleEventRecord"
BCRP_PROFILE_ID = "briefforge-core-representation-profile"
BCRP_CANONICALIZATION_ID = "bcrp-semantic-canonicalization:1.0.0"


@dataclass(frozen=True)
class ReleaseReference:
    identity: str
    fingerprint: str


@dataclass(frozen=True)
class EventAuthority:
    identity: str
    owner: str
    role: str


@dataclass(frozen=True)
class PublicationLifecycleEvent:
    identity: str
    profile_identity: str
    profile_version: str
    publication_identity: str
    event_type: str
    target_release: ReleaseReference
    predecessor_release: ReleaseReference | None
    successor_release: ReleaseReference | None
    reason_classification: str
    reason_detail: str
    authority: EventAuthority
    policy_identity: str
    event_time: str
    predecessor_event_refs: tuple[str, ...]
    distribution_consequence: str
    extension_documents: tuple[str, ...]


@dataclass(frozen=True)
class LifecycleBundle:
    profile_identity: str
    profile_version: str
    events: tuple[PublicationLifecycleEvent, ...]


@dataclass(frozen=True)
class ReleaseBinding:
    """Accepted exact BCRP Release identity/fingerprint metadata supplied out of band."""

    identity: str
    fingerprint: str
    fingerprint_domain: str
    fingerprint_profile_identity: str
    fingerprint_profile_version: str
    fingerprint_canonicalization: str
    fingerprint_algorithm: str
    fingerprint_root_identity: str
    publication_identity: str
    semantic_publication_version: str
    publication_time: str


@dataclass(frozen=True)
class LifecyclePolicy:
    identity: str
    allowed_authorities: tuple[tuple[str, str, str], ...]
    allowed_event_types: tuple[str, ...]
    allowed_reason_classifications: tuple[str, ...]
    distribution_consequences: tuple[tuple[str, str], ...]


@dataclass(frozen=True, order=True)
class LifecycleFinding:
    code: str
    event_identity: str
    location: str
    message: str
    blocking: bool = True


@dataclass(frozen=True)
class LifecycleValidationResult:
    findings: tuple[LifecycleFinding, ...]

    @property
    def blocking(self) -> bool:
        return any(finding.blocking for finding in self.findings)


@dataclass(frozen=True)
class LifecycleFingerprint:
    domain: str
    root_identity: str
    profile_identity: str
    profile_version: str
    canonicalization: str
    algorithm: str
    digest: str
    scope: str


@dataclass(frozen=True)
class DerivedLifecycleState:
    publication_identity: str
    current_release_identity: str | None
    release_states: tuple[tuple[str, str], ...]
    applied_event_identities: tuple[str, ...]


_TOP_LEVEL_KEYS = {"record_kind", "identity", "profile", "semantic", "extensions"}
_SEMANTIC_KEYS = {
    "publication_identity", "event_type", "target_release", "predecessor_release", "successor_release",
    "reason_classification", "reason_detail", "authority", "policy_identity", "event_time",
    "predecessor_event_refs", "distribution_consequence",
}
_STRING_SEMANTIC_KEYS = {
    "publication_identity", "event_type", "reason_classification", "reason_detail", "policy_identity",
    "event_time", "distribution_consequence",
}


def _exact_keys(value: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = set(value) - allowed
    if unknown:
        raise ValueError(f"{label} contains undeclared keys: {sorted(unknown)}")


def _reference(value: Any, label: str) -> ReleaseReference:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    _exact_keys(value, {"identity", "fingerprint"}, label)
    identity = value.get("identity", "")
    fingerprint = value.get("fingerprint", "")
    if not isinstance(identity, str) or not isinstance(fingerprint, str):
        raise ValueError(f"{label} identity and fingerprint must be strings")
    return ReleaseReference(identity, fingerprint)


def _assert_json_transport(value: Any, label: str) -> None:
    if value is None or isinstance(value, float):
        raise ValueError(f"{label} cannot contain null or floating-point values")
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError(f"{label} object keys must be strings")
        for key, item in value.items():
            _assert_json_transport(item, f"{label}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _assert_json_transport(item, f"{label}/{index}")
    elif not isinstance(value, (str, int, bool)):
        raise ValueError(f"{label} contains an unsupported value type")


def event_from_document(document: dict[str, Any]) -> PublicationLifecycleEvent:
    """Strictly parse one event after exact, explicit profile negotiation."""

    if not isinstance(document, dict):
        raise ValueError("lifecycle event document must be an object")
    _exact_keys(document, _TOP_LEVEL_KEYS, "event document")
    if set(document) != _TOP_LEVEL_KEYS:
        raise ValueError("event document is missing required top-level fields")
    if document.get("record_kind") != EVENT_KIND:
        raise ValueError("unsupported lifecycle record kind")
    identity = document.get("identity")
    if not isinstance(identity, str):
        raise ValueError("event identity must be a string")
    profile = document.get("profile")
    if not isinstance(profile, dict):
        raise ValueError("profile must be an object")
    _exact_keys(profile, {"identity", "version"}, "profile")
    if set(profile) != {"identity", "version"} or profile.get("identity") != PROFILE_ID or profile.get("version") != PROFILE_VERSION:
        raise ValueError("unsupported lifecycle profile identity or version")
    semantic = document.get("semantic")
    if not isinstance(semantic, dict):
        raise ValueError("semantic must be an object")
    _exact_keys(semantic, _SEMANTIC_KEYS, "semantic")
    for key in _STRING_SEMANTIC_KEYS:
        if key in semantic and not isinstance(semantic[key], str):
            raise ValueError(f"semantic.{key} must be a string")

    authority_value = semantic.get("authority", {})
    if not isinstance(authority_value, dict):
        raise ValueError("semantic.authority must be an object")
    _exact_keys(authority_value, {"identity", "owner", "role"}, "semantic.authority")
    for key, value in authority_value.items():
        if not isinstance(value, str):
            raise ValueError(f"semantic.authority.{key} must be a string")

    predecessor_refs = semantic.get("predecessor_event_refs", [])
    if not isinstance(predecessor_refs, list) or not all(isinstance(item, str) for item in predecessor_refs):
        raise ValueError("semantic.predecessor_event_refs must be a list of strings")

    extensions = document.get("extensions")
    if not isinstance(extensions, list) or not all(isinstance(extension, dict) for extension in extensions):
        raise ValueError("extensions must be a list of objects")
    for index, extension in enumerate(extensions):
        _assert_json_transport(extension, f"extensions/{index}")
    extension_documents = tuple(
        json.dumps(extension, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
        for extension in extensions
    )

    predecessor = semantic.get("predecessor_release")
    successor = semantic.get("successor_release")
    return PublicationLifecycleEvent(
        identity=identity,
        profile_identity=profile["identity"],
        profile_version=profile["version"],
        publication_identity=semantic.get("publication_identity", ""),
        event_type=semantic.get("event_type", ""),
        target_release=_reference(semantic.get("target_release", {}), "semantic.target_release"),
        predecessor_release=_reference(predecessor, "semantic.predecessor_release") if predecessor is not None else None,
        successor_release=_reference(successor, "semantic.successor_release") if successor is not None else None,
        reason_classification=semantic.get("reason_classification", ""),
        reason_detail=semantic.get("reason_detail", ""),
        authority=EventAuthority(
            authority_value.get("identity", ""), authority_value.get("owner", ""), authority_value.get("role", "")
        ),
        policy_identity=semantic.get("policy_identity", ""),
        event_time=semantic.get("event_time", ""),
        predecessor_event_refs=tuple(predecessor_refs),
        distribution_consequence=semantic.get("distribution_consequence", ""),
        extension_documents=extension_documents,
    )
