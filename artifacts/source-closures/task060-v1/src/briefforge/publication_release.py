"""Fail-closed governed BCRP Publication Release production.

This module is intentionally outside :mod:`briefforge.bcrp`: native BCRP
technical validation has no Release authority.  One production act composes the
TASK-047 compatibility verifier with an exact Release authorization contract.
It never renders, emits a manifest, distributes, or creates lifecycle events.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re
from typing import Any

from .bcrp.canonical import canonicalize_timestamp, fingerprint_bundle
from .bcrp.model import BCRPBundle, BCRPRecord, Fingerprint, PROFILE_ID, PROFILE_VERSION
from .bcrp.validation import validate_bundle
from .bcrp_legacy_compatibility import CompatibilityRejected, verify_mapped_legacy_ready

RELEASE_POLICY_ID = "briefforge-publication-release-policy:1.0.0"
AUTHORIZATION_CONTRACT = "briefforge:publication-release-authorization:1.0.0"
ACCEPTED_AUTHORITY_IDENTITY = "authority:briefforge-publication-release"
ACCEPTED_AUTHORITY_OWNER = "project:BriefForge"
ACCEPTED_AUTHORITY_ROLE = "publication-release-authority"
_INITIAL_STATE = "active"
_DISTRIBUTION_SCOPE = "bounded-explicit-constraints"
_EXTENSION_OWNER = "briefforge-publication-release"
_EXTENSION_NAME = "publication-release-authorization"
_EXTENSION_VERSION = "1.0.0"
_EXTENSION_SCOPE = "publication-release-authorization"
_AUTHORITY_SCOPE = "fixed-evidence-publication-release"
_EXCLUDED_AUTHORITIES = [
    "candidate-authoring",
    "technical-validation",
    "governance-judgment",
    "ready-promotion",
    "legacy-compatibility-mapping",
    "lifecycle-event",
    "renderer",
    "artifact",
    "manifest",
    "distribution-execution",
]
_REQUIRED_KINDS = (
    "PresentationBriefRecord",
    "PortablePresentationMaterialRecord",
    "CandidatePresentationPackageRecord",
    "ValidationJudgmentRecord",
    "ReadyPresentationPackageRecord",
    "PublicationReleaseRecord",
)
_RELEASE_SEMANTIC_KEYS = {
    "publication_lineage_id",
    "semantic_publication_version",
    "ready_ref",
    "ready_fingerprint",
    "evidence_snapshot_refs",
    "evidence_snapshot_versions",
    "release_authority_ref",
    "lifecycle_status",
    "publication_time",
    "distribution_authorized",
    "distribution_scope",
    "includes_recommendations",
}
_EXTENSION_KEYS = {
    "owner_namespace",
    "name",
    "version",
    "authority_ref",
    "scope",
    "target_refs",
    "criticality",
    "character",
    "validation_contract",
    "preservation",
    "payload",
}
_PAYLOAD_KEYS = {
    "contract_version",
    "authorization_identity",
    "authorization_policy",
    "authority",
    "authority_basis",
    "authorization_time",
    "authorized_publication_identity",
    "authorized_publication_version",
    "authorized_ready_identity",
    "authorized_candidate_semantic_fingerprint",
    "authorized_governed_ready_closure_fingerprint",
    "authorized_evidence_snapshot",
    "authorized_initial_release_state",
    "authorized_distribution_constraints",
    "authorized_release_identity",
    "authorized_release_time",
    "authorized_includes_recommendations",
    "release_distribution_constraints",
    "compatibility_lineage",
    "excluded_authorities",
}
_AUTHORITY_KEYS = {"identity", "owner", "role"}
_SNAPSHOT_BINDING_KEYS = {"identity", "version", "inventory_digest"}
_LINEAGE_KEYS = {
    "legacy_domain",
    "legacy_digest",
    "bcrp_domain",
    "bcrp_digest",
    "relationship",
    "compatibility_inventory_digest",
    "mapping_attestation_identity",
}
_IDENTITY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*$")
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_TAGGED_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_SEMVER_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


class ReleaseRejected(ValueError):
    """Raised when no authoritative Release result may be returned."""


@dataclass(frozen=True, order=True)
class EvidenceInventoryItem:
    identity: str
    digest: str


@dataclass(frozen=True)
class EvidenceSnapshot:
    identity: str
    version: str
    scope_identity: str
    snapshot_time: str
    inventory_complete: bool
    closure_status: str
    inventory: tuple[EvidenceInventoryItem, ...]
    inventory_digest: str


@dataclass(frozen=True)
class PublicationReleaseAuthorization:
    """Authority-issued input at the trusted BriefForge Release process boundary.

    This record makes the authorization decision explicit and exactly targeted;
    it is not a cryptographic credential or proof of a human identity.
    """

    identity: str
    policy_identity: str
    authority_identity: str
    authority_owner: str
    authority_role: str
    authorization_time: str
    publication_identity: str
    publication_version: str
    ready_identity: str
    candidate_fingerprint: str
    governed_ready_closure_fingerprint: str
    evidence_snapshot_identity: str
    evidence_snapshot_version: str
    evidence_inventory_digest: str
    initial_release_state: str
    distribution_constraints: tuple[str, ...]
    release_identity: str
    release_time: str
    release_distribution_constraints: tuple[str, ...]
    includes_recommendations: bool


@dataclass(frozen=True)
class VerifiedPublicationRelease:
    _bundle_document: str
    fingerprint: Fingerprint
    authorization: PublicationReleaseAuthorization
    evidence_snapshot: EvidenceSnapshot
    executed_layers: tuple[str, ...]

    @property
    def bundle(self) -> BCRPBundle:
        """Return a detached copy; verified state is stored as immutable text."""

        return _deserialize_bundle(self._bundle_document)

    @property
    def release(self) -> BCRPRecord:
        """Return a detached Release record copy."""

        return self.bundle.one("PublicationReleaseRecord")


def compute_evidence_inventory_digest(
    *,
    identity: str,
    version: str,
    scope_identity: str,
    snapshot_time: str,
    inventory_complete: bool,
    closure_status: str,
    inventory: tuple[EvidenceInventoryItem, ...],
) -> str:
    """Digest one explicit closed inventory without consulting external state."""

    try:
        normalized_time = canonicalize_timestamp(snapshot_time)
    except (TypeError, ValueError) as exc:
        raise ReleaseRejected("Evidence snapshot time must be explicit and canonicalizable.") from exc
    if not isinstance(inventory, tuple) or not all(type(item) is EvidenceInventoryItem for item in inventory):
        raise ReleaseRejected("Evidence inventory must be an explicit tuple of exact inventory items.")
    document = {
        "identity": identity,
        "version": version,
        "scope_identity": scope_identity,
        "snapshot_time": normalized_time,
        "inventory_complete": inventory_complete,
        "closure_status": closure_status,
        "inventory": [
            {"identity": item.identity, "digest": item.digest}
            for item in sorted(inventory, key=lambda value: value.identity)
        ],
    }
    encoded = json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def produce_publication_release(
    *,
    governed_ready: BCRPBundle,
    evidence_snapshot: EvidenceSnapshot,
    authorization: PublicationReleaseAuthorization,
    publication_identity: str,
    publication_version: str,
    release_identity: str,
    release_time: str,
    distribution_constraints: tuple[str, ...],
    includes_recommendations: bool,
) -> VerifiedPublicationRelease:
    """Create one Release only after every earlier and current authority closes."""

    try:
        ready_copy = deepcopy(governed_ready)
        snapshot_copy = deepcopy(evidence_snapshot)
        authorization_copy = deepcopy(authorization)
    except Exception as exc:  # defensive: authority processing never returns a partial output
        raise ReleaseRejected("Release inputs must be safely copyable immutable semantic material.") from exc

    _verify_snapshot(snapshot_copy)
    try:
        verify_mapped_legacy_ready(ready_copy)
    except CompatibilityRejected as exc:
        raise ReleaseRejected("Release requires an exact successfully verified TASK-047 governed Ready closure.") from exc

    _require_identity(publication_identity, "publication identity")
    _require_semver(publication_version)
    _require_identity(release_identity, "Release identity")
    normalized_release_time = _normalize_time(release_time, "Release time")
    if type(includes_recommendations) is not bool:
        raise ReleaseRejected("Recommendation inclusion state must be explicit Boolean material.")
    requested_constraints = _verify_constraints(distribution_constraints, "Release distribution constraints")

    candidate = ready_copy.one("CandidatePresentationPackageRecord")
    ready = ready_copy.one("ReadyPresentationPackageRecord")
    candidate_digest = fingerprint_bundle(ready_copy, domain="candidate-semantic", require_valid=False).digest
    governed_ready_closure_digest = fingerprint_bundle(
        ready_copy, domain="profile-instance", require_valid=False
    ).digest
    _verify_authorization(
        authorization_copy,
        bundle=ready_copy,
        snapshot=snapshot_copy,
        publication_identity=publication_identity,
        publication_version=publication_version,
        ready_identity=ready.identity,
        candidate_digest=candidate_digest,
        governed_ready_closure_digest=governed_ready_closure_digest,
        release_identity=release_identity,
        release_time=normalized_release_time,
        requested_constraints=requested_constraints,
        includes_recommendations=includes_recommendations,
    )

    extension = _authorization_extension(
        release_identity=release_identity,
        ready=ready,
        authorization=authorization_copy,
        snapshot=snapshot_copy,
        requested_constraints=requested_constraints,
    )
    release = BCRPRecord(
        kind="PublicationReleaseRecord",
        identity=release_identity,
        profile_version=PROFILE_VERSION,
        semantic={
            "publication_lineage_id": publication_identity,
            "semantic_publication_version": publication_version,
            "ready_ref": ready.identity,
            "ready_fingerprint": ready.semantic.get("ready_fingerprint"),
            "evidence_snapshot_refs": [snapshot_copy.identity],
            "evidence_snapshot_versions": {snapshot_copy.identity: snapshot_copy.version},
            "release_authority_ref": authorization_copy.authority_identity,
            "lifecycle_status": _INITIAL_STATE,
            "publication_time": normalized_release_time,
            "distribution_authorized": True,
            "distribution_scope": _DISTRIBUTION_SCOPE,
            "includes_recommendations": includes_recommendations,
        },
        extensions=[extension],
    )
    output = deepcopy(ready_copy)
    output.records = output.records + (release,)
    output.index = {"publication_release_produced_in_memory": True}
    output.source_root = None
    output.derived_reverse_index = {}
    return verify_publication_release(output, evidence_snapshot=snapshot_copy)


def verify_publication_release(
    bundle: BCRPBundle,
    *,
    evidence_snapshot: EvidenceSnapshot,
    expected_release_fingerprint: str | None = None,
) -> VerifiedPublicationRelease:
    """Independently verify persisted six-record Release content fail closed."""

    if not isinstance(bundle, BCRPBundle):
        raise ReleaseRejected("Persisted Release verification requires a BCRPBundle.")
    persisted = deepcopy(bundle)
    snapshot = deepcopy(evidence_snapshot)
    _verify_snapshot(snapshot)
    if persisted.profile_identity != PROFILE_ID or persisted.profile_version != PROFILE_VERSION:
        raise ReleaseRejected("Release uses an unsupported BCRP profile identity or version.")
    if len(persisted.records) != 6 or any(len(persisted.records_of_kind(kind)) != 1 for kind in _REQUIRED_KINDS):
        raise ReleaseRejected("Release closure must contain exactly one governed Ready topology and one Release root.")
    if any(record.kind not in _REQUIRED_KINDS for record in persisted.records):
        raise ReleaseRejected("Release closure contains renderer, artifact, Manifest, event, or undeclared records.")

    release = persisted.one("PublicationReleaseRecord")
    if set(release.semantic) != _RELEASE_SEMANTIC_KEYS:
        raise ReleaseRejected("Persisted Release semantic payload is incomplete or contains undeclared fields.")
    if len(release.extensions) != 1:
        raise ReleaseRejected("Persisted Release requires exactly one authorization extension.")

    mapped = BCRPBundle(
        profile_identity=persisted.profile_identity,
        profile_version=persisted.profile_version,
        records=tuple(deepcopy(record) for record in persisted.records if record.kind != "PublicationReleaseRecord"),
        index={"release_verification_projection": True},
    )
    try:
        verify_mapped_legacy_ready(mapped)
    except CompatibilityRejected as exc:
        raise ReleaseRejected("Persisted Release no longer binds an exact TASK-047 governed Ready closure.") from exc

    candidate = mapped.one("CandidatePresentationPackageRecord")
    ready = mapped.one("ReadyPresentationPackageRecord")
    candidate_digest = fingerprint_bundle(mapped, domain="candidate-semantic", require_valid=False).digest
    governed_ready_closure_digest = fingerprint_bundle(
        mapped, domain="profile-instance", require_valid=False
    ).digest
    authorization, requested_constraints = _authorization_from_extension(
        release.extensions[0],
        release=release,
        ready=ready,
        candidate_digest=candidate_digest,
        governed_ready_closure_digest=governed_ready_closure_digest,
        snapshot=snapshot,
    )
    normalized_release_time = _normalize_time(release.semantic.get("publication_time"), "Release time")
    _verify_authorization(
        authorization,
        bundle=mapped,
        snapshot=snapshot,
        publication_identity=release.semantic.get("publication_lineage_id"),
        publication_version=release.semantic.get("semantic_publication_version"),
        ready_identity=ready.identity,
        candidate_digest=candidate_digest,
        governed_ready_closure_digest=governed_ready_closure_digest,
        release_identity=release.identity,
        release_time=normalized_release_time,
        requested_constraints=requested_constraints,
        includes_recommendations=release.semantic.get("includes_recommendations"),
    )
    _verify_release_core(release, ready=ready, snapshot=snapshot, authorization=authorization)

    generic = validate_bundle(persisted, through_layer="L4")
    expected_unsupported = {
        (mapped.one("ValidationJudgmentRecord").identity, "/extensions/0"),
        (ready.identity, "/extensions/0"),
        (release.identity, "/extensions/0"),
    }
    reconciled: set[tuple[str, str]] = set()
    unrelated = []
    for finding in generic.findings:
        key = (finding.semantic_identity, finding.location)
        exact = (
            finding.layer == "L1"
            and finding.family == "extension-boundary"
            and finding.severity == "blocking"
            and finding.message == "Unknown required semantic extension cannot be processed."
            and key in expected_unsupported
        )
        if exact:
            reconciled.add(key)
        else:
            unrelated.append(finding)
    if reconciled != expected_unsupported or unrelated:
        raise ReleaseRejected("Dedicated Release validation found unrelated or incomplete BCRP findings.")

    fingerprint = fingerprint_bundle(persisted, domain="release-semantic", require_valid=False)
    if expected_release_fingerprint is not None:
        if not isinstance(expected_release_fingerprint, str) or not _DIGEST_RE.fullmatch(expected_release_fingerprint):
            raise ReleaseRejected("Expected Release fingerprint is missing or malformed.")
        if fingerprint.digest != expected_release_fingerprint:
            raise ReleaseRejected("Persisted Release fingerprint does not match the accepted exact binding.")
    return VerifiedPublicationRelease(
        _bundle_document=_serialize_bundle(persisted),
        fingerprint=fingerprint,
        authorization=authorization,
        evidence_snapshot=snapshot,
        executed_layers=generic.executed_layers,
    )


def release_binding_from_verified_release(verified: VerifiedPublicationRelease):
    """Adapt one already-verified immutable Release to TASK-049 without an event."""

    if type(verified) is not VerifiedPublicationRelease:
        raise ReleaseRejected("Lifecycle anchoring requires an independently verified Release result.")
    reverified = verify_publication_release(
        verified.bundle,
        evidence_snapshot=verified.evidence_snapshot,
        expected_release_fingerprint=verified.fingerprint.digest,
    )
    from .publication_lifecycle import ReleaseBinding

    fingerprint = reverified.fingerprint
    release = reverified.release
    if fingerprint.root_identity != release.identity or fingerprint.domain != "release-semantic":
        raise ReleaseRejected("Verified Release fingerprint metadata cannot anchor lifecycle processing.")
    return ReleaseBinding(
        identity=release.identity,
        fingerprint=fingerprint.digest,
        fingerprint_domain=fingerprint.domain,
        fingerprint_profile_identity=fingerprint.profile_identity,
        fingerprint_profile_version=fingerprint.profile_version,
        fingerprint_canonicalization=fingerprint.canonicalization,
        fingerprint_algorithm=fingerprint.algorithm,
        fingerprint_root_identity=fingerprint.root_identity,
        publication_identity=release.semantic["publication_lineage_id"],
        semantic_publication_version=release.semantic["semantic_publication_version"],
        publication_time=release.semantic["publication_time"],
    )


def _verify_snapshot(snapshot: EvidenceSnapshot) -> None:
    if type(snapshot) is not EvidenceSnapshot:
        raise ReleaseRejected("An explicit immutable evidence snapshot is required.")
    _require_identity(snapshot.identity, "evidence snapshot identity")
    _require_identity(snapshot.scope_identity, "evidence snapshot scope identity")
    if not isinstance(snapshot.version, str) or not snapshot.version:
        raise ReleaseRejected("Evidence snapshot version is required.")
    _normalize_time(snapshot.snapshot_time, "evidence snapshot time")
    if snapshot.inventory_complete is not True or snapshot.closure_status != "closed":
        raise ReleaseRejected("Evidence snapshot inventory must be explicitly complete and closed.")
    if not isinstance(snapshot.inventory, tuple) or not all(type(item) is EvidenceInventoryItem for item in snapshot.inventory):
        raise ReleaseRejected("Evidence snapshot inventory has undeclared material.")
    if tuple(sorted(snapshot.inventory, key=lambda item: item.identity)) != snapshot.inventory:
        raise ReleaseRejected("Evidence snapshot inventory ordering must be deterministic by identity.")
    identities = [item.identity for item in snapshot.inventory]
    if len(identities) != len(set(identities)):
        raise ReleaseRejected("Evidence snapshot inventory identities must be unique.")
    for item in snapshot.inventory:
        _require_identity(item.identity, "evidence inventory identity")
        if not isinstance(item.digest, str) or not _TAGGED_DIGEST_RE.fullmatch(item.digest):
            raise ReleaseRejected("Evidence inventory digests must be exact tagged SHA-256 values.")
    expected = compute_evidence_inventory_digest(
        identity=snapshot.identity,
        version=snapshot.version,
        scope_identity=snapshot.scope_identity,
        snapshot_time=snapshot.snapshot_time,
        inventory_complete=snapshot.inventory_complete,
        closure_status=snapshot.closure_status,
        inventory=snapshot.inventory,
    )
    if not isinstance(snapshot.inventory_digest, str) or snapshot.inventory_digest != expected:
        raise ReleaseRejected("Evidence snapshot inventory digest is absent, stale, or wrong.")


def _verify_authorization(
    authorization: PublicationReleaseAuthorization,
    *,
    bundle: BCRPBundle,
    snapshot: EvidenceSnapshot,
    publication_identity: str,
    publication_version: str,
    ready_identity: str,
    candidate_digest: str,
    governed_ready_closure_digest: str,
    release_identity: str,
    release_time: str,
    requested_constraints: tuple[str, ...],
    includes_recommendations: bool,
) -> None:
    if type(authorization) is not PublicationReleaseAuthorization:
        raise ReleaseRejected("Explicit immutable Publication Release authorization is required.")
    _verify_material_snapshot(bundle, snapshot)
    _require_identity(authorization.identity, "authorization identity")
    _require_identity(publication_identity, "publication identity")
    _require_semver(publication_version)
    if authorization.policy_identity != RELEASE_POLICY_ID:
        raise ReleaseRejected("Unknown Publication Release policy.")
    if (
        authorization.authority_identity != ACCEPTED_AUTHORITY_IDENTITY
        or authorization.authority_owner != ACCEPTED_AUTHORITY_OWNER
        or authorization.authority_role != ACCEPTED_AUTHORITY_ROLE
    ):
        raise ReleaseRejected("Release authority identity, owner, or role is not accepted by the policy.")
    authority_objects = {
        item.get("id"): item
        for item in bundle.one("PortablePresentationMaterialRecord").semantic.get("authorities", [])
        if isinstance(item, dict)
    }
    declared = authority_objects.get(authorization.authority_identity)
    if declared != {
        "id": ACCEPTED_AUTHORITY_IDENTITY,
        "owner_identity": ACCEPTED_AUTHORITY_OWNER,
        "role": ACCEPTED_AUTHORITY_ROLE,
        "scope": _AUTHORITY_SCOPE,
    }:
        raise ReleaseRejected("Exact BriefForge Release authority declaration is absent from admitted material.")
    if (
        authorization.publication_identity != publication_identity
        or authorization.publication_version != publication_version
        or authorization.ready_identity != ready_identity
        or authorization.candidate_fingerprint != candidate_digest
        or authorization.governed_ready_closure_fingerprint != governed_ready_closure_digest
    ):
        raise ReleaseRejected(
            "Release authorization targets another publication, version, Ready, Candidate, or governed closure."
        )
    if (
        authorization.evidence_snapshot_identity != snapshot.identity
        or authorization.evidence_snapshot_version != snapshot.version
        or authorization.evidence_inventory_digest != snapshot.inventory_digest
    ):
        raise ReleaseRejected("Release authorization targets another evidence snapshot closure.")
    if authorization.initial_release_state != _INITIAL_STATE:
        raise ReleaseRejected("Only the initial active Release state is supported.")
    if (
        authorization.release_identity != release_identity
        or _normalize_time(authorization.release_time, "authorized Release time") != release_time
        or authorization.includes_recommendations is not includes_recommendations
    ):
        raise ReleaseRejected("Release authorization does not target this exact Release identity, time, or recommendation state.")
    authorized_constraints = _verify_constraints(authorization.distribution_constraints, "authorized distribution constraints")
    authorized_release_constraints = _verify_constraints(
        authorization.release_distribution_constraints, "authorized exact Release constraints"
    )
    if requested_constraints != authorized_release_constraints:
        raise ReleaseRejected("Release constraints differ from the exact authorized Release act.")
    if not set(requested_constraints).issubset(authorized_constraints):
        raise ReleaseRejected("Release distribution constraints exceed explicit authorization.")

    authorization_time = _normalize_time(authorization.authorization_time, "authorization time")
    ready_payload = bundle.one("ReadyPresentationPackageRecord").extensions[0].get("payload", {})
    readiness_time = _normalize_time(ready_payload.get("lifecycle_times", {}).get("readiness_time"), "Ready time")
    snapshot_time = _normalize_time(snapshot.snapshot_time, "evidence snapshot time")
    if _parse_time(snapshot_time) > _parse_time(authorization_time) or _parse_time(readiness_time) > _parse_time(authorization_time):
        raise ReleaseRejected("Release authorization predates its governed Ready or evidence snapshot.")
    if _parse_time(authorization_time) > _parse_time(release_time):
        raise ReleaseRejected("Release time predates explicit authorization.")


def _verify_release_core(
    release: BCRPRecord,
    *,
    ready: BCRPRecord,
    snapshot: EvidenceSnapshot,
    authorization: PublicationReleaseAuthorization,
) -> None:
    _require_identity(release.identity, "Release identity")
    _require_identity(release.semantic.get("publication_lineage_id"), "publication identity")
    _require_semver(release.semantic.get("semantic_publication_version"))
    if release.semantic.get("ready_ref") != ready.identity or release.semantic.get("ready_fingerprint") != ready.semantic.get("ready_fingerprint"):
        raise ReleaseRejected("Release does not bind the exact governed Ready identity and fingerprint.")
    if release.semantic.get("evidence_snapshot_refs") != [snapshot.identity]:
        raise ReleaseRejected("Release must bind exactly one declared evidence snapshot identity.")
    if release.semantic.get("evidence_snapshot_versions") != {snapshot.identity: snapshot.version}:
        raise ReleaseRejected("Release evidence snapshot version binding is absent or drifted.")
    if release.semantic.get("release_authority_ref") != authorization.authority_identity:
        raise ReleaseRejected("Release core authority reference contradicts its authorization.")
    if release.semantic.get("lifecycle_status") != _INITIAL_STATE:
        raise ReleaseRejected("Release core state is not the supported immutable initial state.")
    if release.semantic.get("distribution_authorized") is not True or release.semantic.get("distribution_scope") != _DISTRIBUTION_SCOPE:
        raise ReleaseRejected("Release distribution authority is absent or implicitly broadened.")
    if type(release.semantic.get("includes_recommendations")) is not bool:
        raise ReleaseRejected("Release recommendation inclusion state is not explicit.")


def _authorization_extension(
    *,
    release_identity: str,
    ready: BCRPRecord,
    authorization: PublicationReleaseAuthorization,
    snapshot: EvidenceSnapshot,
    requested_constraints: tuple[str, ...],
) -> dict[str, Any]:
    compatibility = ready.extensions[0]["payload"]
    lineage = compatibility["fingerprint_lineage"]
    attestation = compatibility["mapping_attestation"]
    payload = {
        "contract_version": _EXTENSION_VERSION,
        "authorization_identity": authorization.identity,
        "authorization_policy": authorization.policy_identity,
        "authority": {
            "identity": authorization.authority_identity,
            "owner": authorization.authority_owner,
            "role": authorization.authority_role,
        },
        "authority_basis": "policy-backed-system",
        "authorization_time": canonicalize_timestamp(authorization.authorization_time),
        "authorized_publication_identity": authorization.publication_identity,
        "authorized_publication_version": authorization.publication_version,
        "authorized_ready_identity": authorization.ready_identity,
        "authorized_candidate_semantic_fingerprint": authorization.candidate_fingerprint,
        "authorized_governed_ready_closure_fingerprint": authorization.governed_ready_closure_fingerprint,
        "authorized_evidence_snapshot": {
            "identity": snapshot.identity,
            "version": snapshot.version,
            "inventory_digest": snapshot.inventory_digest,
        },
        "authorized_initial_release_state": authorization.initial_release_state,
        "authorized_distribution_constraints": list(authorization.distribution_constraints),
        "authorized_release_identity": authorization.release_identity,
        "authorized_release_time": canonicalize_timestamp(authorization.release_time),
        "authorized_includes_recommendations": authorization.includes_recommendations,
        "release_distribution_constraints": list(requested_constraints),
        "compatibility_lineage": {
            "legacy_domain": lineage["legacy_domain"],
            "legacy_digest": lineage["legacy_digest"],
            "bcrp_domain": lineage["bcrp_domain"],
            "bcrp_digest": lineage["bcrp_digest"],
            "relationship": lineage["relationship"],
            "compatibility_inventory_digest": attestation["inventory_digest"],
            "mapping_attestation_identity": attestation["attestation_identity"],
        },
        "excluded_authorities": list(_EXCLUDED_AUTHORITIES),
    }
    return {
        "owner_namespace": _EXTENSION_OWNER,
        "name": _EXTENSION_NAME,
        "version": _EXTENSION_VERSION,
        "authority_ref": authorization.authority_identity,
        "scope": _EXTENSION_SCOPE,
        "target_refs": [release_identity, ready.identity],
        "criticality": "required",
        "character": "semantic",
        "validation_contract": AUTHORIZATION_CONTRACT,
        "preservation": "must-preserve",
        "payload": payload,
    }


def _authorization_from_extension(
    extension: dict[str, Any],
    *,
    release: BCRPRecord,
    ready: BCRPRecord,
    candidate_digest: str,
    governed_ready_closure_digest: str,
    snapshot: EvidenceSnapshot,
) -> tuple[PublicationReleaseAuthorization, tuple[str, ...]]:
    if not isinstance(extension, dict) or set(extension) != _EXTENSION_KEYS:
        raise ReleaseRejected("Release authorization extension envelope contains unknown or missing fields.")
    expected_envelope = {
        "owner_namespace": _EXTENSION_OWNER,
        "name": _EXTENSION_NAME,
        "version": _EXTENSION_VERSION,
        "authority_ref": ACCEPTED_AUTHORITY_IDENTITY,
        "scope": _EXTENSION_SCOPE,
        "target_refs": [release.identity, ready.identity],
        "criticality": "required",
        "character": "semantic",
        "validation_contract": AUTHORIZATION_CONTRACT,
        "preservation": "must-preserve",
    }
    if any(extension.get(key) != value for key, value in expected_envelope.items()):
        raise ReleaseRejected("Release authorization extension is unknown, optional, mistargeted, or unauthorized.")
    payload = extension.get("payload")
    if not isinstance(payload, dict) or set(payload) != _PAYLOAD_KEYS:
        raise ReleaseRejected("Release authorization payload is incomplete or contains undeclared fields.")
    authority = payload.get("authority")
    snapshot_binding = payload.get("authorized_evidence_snapshot")
    lineage = payload.get("compatibility_lineage")
    if not isinstance(authority, dict) or set(authority) != _AUTHORITY_KEYS:
        raise ReleaseRejected("Release authorization authority material is malformed.")
    if not isinstance(snapshot_binding, dict) or set(snapshot_binding) != _SNAPSHOT_BINDING_KEYS:
        raise ReleaseRejected("Release authorization snapshot binding is malformed.")
    if not isinstance(lineage, dict) or set(lineage) != _LINEAGE_KEYS:
        raise ReleaseRejected("Release compatibility lineage is malformed or incomplete.")
    ready_compatibility = ready.extensions[0].get("payload", {})
    ready_lineage = ready_compatibility.get("fingerprint_lineage", {})
    ready_attestation = ready_compatibility.get("mapping_attestation", {})
    expected_lineage = {
        "legacy_domain": ready_lineage.get("legacy_domain"),
        "legacy_digest": ready_lineage.get("legacy_digest"),
        "bcrp_domain": ready_lineage.get("bcrp_domain"),
        "bcrp_digest": candidate_digest,
        "relationship": ready_lineage.get("relationship"),
        "compatibility_inventory_digest": ready_attestation.get("inventory_digest"),
        "mapping_attestation_identity": ready_attestation.get("attestation_identity"),
    }
    if lineage != expected_lineage:
        raise ReleaseRejected("Release compatibility inventory or fingerprint lineage drifted.")
    if payload.get("contract_version") != _EXTENSION_VERSION or payload.get("authority_basis") != "policy-backed-system":
        raise ReleaseRejected("Release authorization contract or authority basis is unknown.")
    if payload.get("excluded_authorities") != _EXCLUDED_AUTHORITIES:
        raise ReleaseRejected("Release authorization implicitly grants excluded downstream authority.")
    if snapshot_binding != {
        "identity": snapshot.identity,
        "version": snapshot.version,
        "inventory_digest": snapshot.inventory_digest,
    }:
        raise ReleaseRejected("Persisted authorization binds another evidence snapshot.")
    authorized_constraints = _constraints_from_payload(payload.get("authorized_distribution_constraints"), "authorized constraints")
    requested_constraints = _constraints_from_payload(payload.get("release_distribution_constraints"), "Release constraints")
    authorization = PublicationReleaseAuthorization(
        identity=payload.get("authorization_identity"),
        policy_identity=payload.get("authorization_policy"),
        authority_identity=authority.get("identity"),
        authority_owner=authority.get("owner"),
        authority_role=authority.get("role"),
        authorization_time=payload.get("authorization_time"),
        publication_identity=payload.get("authorized_publication_identity"),
        publication_version=payload.get("authorized_publication_version"),
        ready_identity=payload.get("authorized_ready_identity"),
        candidate_fingerprint=payload.get("authorized_candidate_semantic_fingerprint"),
        governed_ready_closure_fingerprint=payload.get("authorized_governed_ready_closure_fingerprint"),
        evidence_snapshot_identity=snapshot_binding.get("identity"),
        evidence_snapshot_version=snapshot_binding.get("version"),
        evidence_inventory_digest=snapshot_binding.get("inventory_digest"),
        initial_release_state=payload.get("authorized_initial_release_state"),
        distribution_constraints=authorized_constraints,
        release_identity=payload.get("authorized_release_identity"),
        release_time=payload.get("authorized_release_time"),
        release_distribution_constraints=requested_constraints,
        includes_recommendations=payload.get("authorized_includes_recommendations"),
    )
    return authorization, requested_constraints


def _verify_material_snapshot(bundle: BCRPBundle, snapshot: EvidenceSnapshot) -> None:
    material = bundle.one("PortablePresentationMaterialRecord")
    snapshots = material.semantic.get("evidence_snapshots")
    if not isinstance(snapshots, list) or len(snapshots) != 1 or not isinstance(snapshots[0], dict):
        raise ReleaseRejected("Admitted Material must declare exactly one fixed evidence snapshot closure.")
    item = snapshots[0]
    if item.get("id") != snapshot.identity or item.get("version") != snapshot.version:
        raise ReleaseRejected("Material evidence snapshot identity or version differs from admitted closure.")
    if item.get("content_fingerprint") != f"sha256:{snapshot.inventory_digest}":
        raise ReleaseRejected("Material evidence snapshot content fingerprint differs from complete inventory digest.")


def _verify_constraints(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, tuple) or not value or not all(isinstance(item, str) and item for item in value):
        raise ReleaseRejected(f"{label} must be an explicit non-empty tuple.")
    if len(value) != len(set(value)) or tuple(sorted(value)) != value:
        raise ReleaseRejected(f"{label} must be unique and deterministically ordered.")
    return value


def _constraints_from_payload(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ReleaseRejected(f"Persisted {label} must be a list.")
    return _verify_constraints(tuple(value), label)


def _require_identity(value: Any, label: str) -> None:
    if not isinstance(value, str):
        raise ReleaseRejected(f"Explicit {label} is required.")
    try:
        ascii_value = value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ReleaseRejected(f"{label} must use canonical ASCII identity syntax.") from exc
    if not ascii_value or not _IDENTITY_RE.fullmatch(value):
        raise ReleaseRejected(f"{label} must use canonical ASCII identity syntax.")


def _require_semver(value: Any) -> None:
    if not isinstance(value, str) or not _SEMVER_RE.fullmatch(value):
        raise ReleaseRejected("Publication semantic version must be explicit canonical SemVer.")


def _normalize_time(value: Any, label: str) -> str:
    try:
        return canonicalize_timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ReleaseRejected(f"{label} must be explicit and canonicalizable.") from exc


def _parse_time(value: str) -> datetime:
    normalized = canonicalize_timestamp(value)
    return datetime.fromisoformat(normalized[:-1] + "+00:00")


def _serialize_bundle(bundle: BCRPBundle) -> str:
    document = {
        "profile_identity": bundle.profile_identity,
        "profile_version": bundle.profile_version,
        "records": [record.to_document() for record in bundle.records],
    }
    return json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _deserialize_bundle(document_text: str) -> BCRPBundle:
    try:
        document = json.loads(document_text)
        records = document["records"]
        if not isinstance(records, list):
            raise TypeError("records must be a list")
        return BCRPBundle(
            profile_identity=document["profile_identity"],
            profile_version=document["profile_version"],
            records=tuple(BCRPRecord.from_document(record) for record in records),
            index={"verified_release_detached_copy": True},
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ReleaseRejected("Stored verified Release representation is invalid.") from exc
