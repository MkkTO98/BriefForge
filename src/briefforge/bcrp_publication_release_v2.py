"""Fail-closed governed BCRP Publication Release production.

This module is intentionally outside :mod:`briefforge.bcrp`: native BCRP
technical validation has no Release authority.  One production act composes the
TASK-047 compatibility verifier with an exact Release authorization contract.
It never renders, emits a manifest, distributes, or creates lifecycle events.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime
import hashlib
import json
import re
from typing import Any

from .bcrp.canonical import canonical_json_bytes, canonicalize_timestamp, fingerprint_bundle
from .bcrp.model import BCRPBundle, BCRPRecord, Fingerprint, PROFILE_ID, PROFILE_VERSION
from .bcrp.validation import validate_bundle
from .bcrp_legacy_compatibility import CompatibilityRejected, verify_mapped_legacy_ready
from .bcrp_publication_governance import (
    NativeGovernanceRejected, VerifiedNativeReady, verify_native_ready,
    PersistedNativeReadyBinding, verify_persisted_native_ready_binding,
)

RELEASE_POLICY_ID = "briefforge-publication-release-policy:1.0.0"
AUTHORIZATION_CONTRACT = "briefforge:publication-release-authorization:1.0.0"
NATIVE_AUTHORIZATION_CONTRACT = "briefforge:publication-release-authorization:2.0.0"
NATIVE_RELEASE_POLICY_ID = "briefforge-native-bcrp-publication-release-policy:2.0.0"
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
class NativePublicationReleaseAuthorization:
    """Exact v2 authorization for an accepted native governed Ready closure."""

    identity: str
    policy_identity: str
    authority_identity: str
    authority_owner: str
    authority_role: str
    authorization_time: str
    publication_identity: str
    publication_version: str
    candidate_identity: str
    candidate_semantic_fingerprint: str
    subject_closure_fingerprint: str
    judgment_identity: str
    judgment_fingerprint: str
    ready_identity: str
    ready_fingerprint: str
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
    authorization: PublicationReleaseAuthorization | NativePublicationReleaseAuthorization
    evidence_snapshot: EvidenceSnapshot
    executed_layers: tuple[str, ...]

    @property
    def serialized_bundle(self) -> str:
        """Immutable deterministic persisted representation for exact cross-binding."""
        return self._bundle_document

    @property
    def bundle(self) -> BCRPBundle:
        """Return a detached copy; native v2 exposes the frozen terminal authority projection."""

        bundle = _deserialize_bundle(self._bundle_document)
        if type(self.authorization) is NativePublicationReleaseAuthorization:
            from briefforge_terminal_profile.profile import TERMINAL_OPERATIONAL_IDENTITIES
            material = bundle.one("PortablePresentationMaterialRecord")
            authorities = material.semantic.get("authorities")
            if type(authorities) is list and all(type(item) is dict for item in authorities):
                by_identity = {item.get("id"): item for item in authorities}
                operational = [deepcopy(by_identity[identity]) for identity in TERMINAL_OPERATIONAL_IDENTITIES
                               if identity in by_identity]
                content = sorted((deepcopy(item) for item in authorities
                                  if item.get("id") not in set(TERMINAL_OPERATIONAL_IDENTITIES)),
                                 key=lambda item: item.get("id", ""))
                material.semantic["authorities"] = operational + content
        return bundle

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

    extension_tuple = tuple(release.extensions[0].get(key) for key in
        ("owner_namespace", "name", "version", "validation_contract")) if type(release.extensions[0]) is dict else ()
    native_tuple = ("briefforge-publication-release", "native-publication-release-authorization",
                    "2.0.0", NATIVE_AUTHORIZATION_CONTRACT)
    legacy_tuple = (_EXTENSION_OWNER, _EXTENSION_NAME, _EXTENSION_VERSION, AUTHORIZATION_CONTRACT)
    if extension_tuple == native_tuple:
        return _verify_native_publication_release(persisted, snapshot,
            expected_release_fingerprint=expected_release_fingerprint)
    if extension_tuple != legacy_tuple:
        raise ReleaseRejected("Release authorization extension family/version is unknown or mixed.")

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


def produce_native_publication_release(
    *, governed_ready: VerifiedNativeReady, evidence_snapshot: EvidenceSnapshot,
    authorization: NativePublicationReleaseAuthorization,
    publication_identity: str, publication_version: str, release_identity: str,
    release_time: str, distribution_constraints: tuple[str, ...],
    includes_recommendations: bool,
) -> VerifiedPublicationRelease:
    """Create native v2 Release without fabricating legacy lineage."""
    if type(governed_ready) is not VerifiedNativeReady or type(authorization) is not NativePublicationReleaseAuthorization:
        raise ReleaseRejected("Native v2 Release requires exact verified native Ready and authorization.")
    try:
        ready = verify_native_ready(governed_ready.bundle, governed_ready.judgment_result)
    except NativeGovernanceRejected as exc:
        raise ReleaseRejected("Native Ready closure failed independent verification.") from exc
    snapshot = deepcopy(evidence_snapshot); _verify_snapshot(snapshot)
    auth = deepcopy(authorization)
    normalized_time = _normalize_time(release_time, "Release time")
    constraints = _verify_constraints(distribution_constraints, "Release distribution constraints")
    _verify_native_release_authorization(auth, ready, snapshot, publication_identity,
        publication_version, release_identity, normalized_time, constraints, includes_recommendations)
    ready_record = ready.ready
    payload = {
        "contract_version": "2.0.0",
        "authorization": _native_auth_document(auth),
        "candidate": {"identity": ready.subject.candidate_identity,
            "candidate_semantic_fingerprint": ready.subject.candidate_semantic_fingerprint,
            "subject_closure_fingerprint": ready.subject.closure_fingerprint,
            "profile_instance_fingerprint": ready.subject.profile_instance_fingerprint,
            "profile_sha256": hashlib.sha256(ready.subject.profile_bytes).hexdigest()},
        "judgment": {"identity": ready.judgment_result.judgment.identity,
                     "fingerprint": ready.judgment_result.fingerprint.digest},
        "ready": {"identity": ready_record.identity, "fingerprint": ready.fingerprint.digest,
                  "core_ready_fingerprint": ready_record.semantic["ready_fingerprint"]},
        "governed_ready_closure_fingerprint": ready.fingerprint.digest,
        "evidence_snapshot": {"identity": snapshot.identity, "version": snapshot.version,
                              "inventory_digest": snapshot.inventory_digest},
        "authority_constraints": {"initial_state": _INITIAL_STATE,
            "distribution_constraints": list(constraints),
            "excluded_authorities": ["renderer", "artifact", "manifest", "distribution-execution"]},
    }
    extension = {"owner_namespace": "briefforge-publication-release",
        "name": "native-publication-release-authorization", "version": "2.0.0",
        "authority_ref": auth.authority_identity, "scope": "native-bcrp-publication-release",
        "target_refs": [release_identity, ready_record.identity, ready.judgment_result.judgment.identity,
                        ready.subject.candidate_identity],
        "criticality": "required", "character": "semantic",
        "validation_contract": NATIVE_AUTHORIZATION_CONTRACT, "preservation": "must-preserve",
        "payload": payload}
    record = BCRPRecord("PublicationReleaseRecord", release_identity, PROFILE_VERSION, {
        "publication_lineage_id": publication_identity,
        "semantic_publication_version": publication_version,
        "ready_ref": ready_record.identity,
        "ready_fingerprint": ready_record.semantic["ready_fingerprint"],
        "evidence_snapshot_refs": [snapshot.identity],
        "evidence_snapshot_versions": {snapshot.identity: snapshot.version},
        "release_authority_ref": auth.authority_identity,
        "lifecycle_status": _INITIAL_STATE, "publication_time": normalized_time,
        "distribution_authorized": True, "distribution_scope": _DISTRIBUTION_SCOPE,
        "includes_recommendations": includes_recommendations,
    }, [extension])
    output = ready.bundle; output.records += (record,)
    return verify_publication_release(output, evidence_snapshot=snapshot)


def _native_auth_document(auth: NativePublicationReleaseAuthorization) -> dict[str, Any]:
    value = asdict(auth)
    value["distribution_constraints"] = list(auth.distribution_constraints)
    value["release_distribution_constraints"] = list(auth.release_distribution_constraints)
    return value


def _native_auth_from_document(value: Any) -> NativePublicationReleaseAuthorization:
    if type(value) is not dict or set(value) != set(NativePublicationReleaseAuthorization.__dataclass_fields__):
        raise ReleaseRejected("Native v2 persisted authorization is malformed.")
    value = deepcopy(value)
    if type(value["distribution_constraints"]) is not list or type(value["release_distribution_constraints"]) is not list:
        raise ReleaseRejected("Native v2 constraints must be persisted arrays.")
    value["distribution_constraints"] = tuple(value["distribution_constraints"])
    value["release_distribution_constraints"] = tuple(value["release_distribution_constraints"])
    return NativePublicationReleaseAuthorization(**value)


def _verify_native_release_authorization(auth: NativePublicationReleaseAuthorization,
        ready: VerifiedNativeReady, snapshot: EvidenceSnapshot, publication_identity: str,
        publication_version: str, release_identity: str, release_time: str,
        constraints: tuple[str, ...], includes_recommendations: bool) -> None:
    if type(auth) is not NativePublicationReleaseAuthorization:
        raise ReleaseRejected("Exact native v2 Release authorization is required.")
    _require_identity(auth.identity, "authorization identity")
    _require_identity(publication_identity, "publication identity"); _require_semver(publication_version)
    _require_identity(release_identity, "Release identity")
    subject = ready.subject; judgment = ready.judgment_result
    expected = (NATIVE_RELEASE_POLICY_ID, ACCEPTED_AUTHORITY_IDENTITY, ACCEPTED_AUTHORITY_OWNER,
        ACCEPTED_AUTHORITY_ROLE, publication_identity, publication_version,
        subject.candidate_identity, subject.candidate_semantic_fingerprint, subject.closure_fingerprint,
        judgment.judgment.identity, judgment.fingerprint.digest, ready.ready.identity,
        ready.ready.semantic["ready_fingerprint"], ready.fingerprint.digest,
        snapshot.identity, snapshot.version, snapshot.inventory_digest, _INITIAL_STATE,
        release_identity, release_time, includes_recommendations)
    actual = (auth.policy_identity, auth.authority_identity, auth.authority_owner, auth.authority_role,
        auth.publication_identity, auth.publication_version, auth.candidate_identity,
        auth.candidate_semantic_fingerprint, auth.subject_closure_fingerprint,
        auth.judgment_identity, auth.judgment_fingerprint, auth.ready_identity, auth.ready_fingerprint,
        auth.governed_ready_closure_fingerprint, auth.evidence_snapshot_identity,
        auth.evidence_snapshot_version, auth.evidence_inventory_digest, auth.initial_release_state,
        auth.release_identity, _normalize_time(auth.release_time, "authorized Release time"),
        auth.includes_recommendations)
    if actual != expected:
        raise ReleaseRejected("Native v2 authorization targets another complete governed closure or Release act.")
    allowed = _verify_constraints(auth.distribution_constraints, "authorized distribution constraints")
    exact = _verify_constraints(auth.release_distribution_constraints, "authorized exact Release constraints")
    if constraints != exact or not set(exact).issubset(allowed):
        raise ReleaseRejected("Native v2 Release constraints differ from authorization.")
    auth_time = _parse_time(_normalize_time(auth.authorization_time, "authorization time"))
    ready_time = _parse_time(ready.ready.semantic["readiness_time"])
    snapshot_time = _parse_time(_normalize_time(snapshot.snapshot_time, "evidence snapshot time"))
    if max(ready_time, snapshot_time) > auth_time or auth_time > _parse_time(release_time):
        raise ReleaseRejected("Native v2 Release authorization chronology is stale or reversed.")


def _verify_native_persisted_release_authorization(auth: NativePublicationReleaseAuthorization,
        ready: PersistedNativeReadyBinding, snapshot: EvidenceSnapshot, publication_identity: str,
        publication_version: str, release_identity: str, release_time: str,
        constraints: tuple[str, ...], includes_recommendations: bool) -> None:
    """Verify v2 authorization against independently reconstructed persisted bindings."""
    if type(auth) is not NativePublicationReleaseAuthorization:
        raise ReleaseRejected("Exact native v2 persisted authorization is required.")
    _require_identity(auth.identity, "authorization identity")
    _require_identity(publication_identity, "publication identity"); _require_semver(publication_version)
    _require_identity(release_identity, "Release identity")
    expected = (NATIVE_RELEASE_POLICY_ID, ACCEPTED_AUTHORITY_IDENTITY, ACCEPTED_AUTHORITY_OWNER,
        ACCEPTED_AUTHORITY_ROLE, publication_identity, publication_version,
        ready.candidate_identity, ready.candidate_semantic_fingerprint, ready.subject_closure_fingerprint,
        ready.judgment_identity, ready.judgment_fingerprint, ready.ready_identity,
        ready.core_ready_fingerprint, ready.ready_fingerprint,
        snapshot.identity, snapshot.version, snapshot.inventory_digest, _INITIAL_STATE,
        release_identity, release_time, includes_recommendations)
    actual = (auth.policy_identity, auth.authority_identity, auth.authority_owner, auth.authority_role,
        auth.publication_identity, auth.publication_version, auth.candidate_identity,
        auth.candidate_semantic_fingerprint, auth.subject_closure_fingerprint,
        auth.judgment_identity, auth.judgment_fingerprint, auth.ready_identity, auth.ready_fingerprint,
        auth.governed_ready_closure_fingerprint, auth.evidence_snapshot_identity,
        auth.evidence_snapshot_version, auth.evidence_inventory_digest, auth.initial_release_state,
        auth.release_identity, _normalize_time(auth.release_time, "authorized Release time"),
        auth.includes_recommendations)
    if actual != expected:
        raise ReleaseRejected("Native v2 persisted authorization targets another transitive closure.")
    allowed = _verify_constraints(auth.distribution_constraints, "authorized distribution constraints")
    exact = _verify_constraints(auth.release_distribution_constraints, "authorized exact Release constraints")
    if constraints != exact or not set(exact).issubset(allowed):
        raise ReleaseRejected("Native v2 persisted Release constraints differ from authorization.")
    auth_time = _parse_time(_normalize_time(auth.authorization_time, "authorization time"))
    ready_time = _parse_time(_normalize_time(ready.readiness_time, "persisted Ready time"))
    snapshot_time = _parse_time(_normalize_time(snapshot.snapshot_time, "evidence snapshot time"))
    if max(ready_time, snapshot_time) > auth_time or auth_time > _parse_time(release_time):
        raise ReleaseRejected("Native v2 persisted Release chronology is stale or reversed.")


def _verify_native_publication_release(bundle: BCRPBundle, snapshot: EvidenceSnapshot,
        *, expected_release_fingerprint: str | None) -> VerifiedPublicationRelease:
    if (type(bundle) is not BCRPBundle or type(bundle.records) is not tuple or
            any(type(item) is not BCRPRecord or item.profile_version != PROFILE_VERSION
                for item in bundle.records)):
        raise ReleaseRejected("Native v2 Release requires exact BCRP record and bundle types.")
    release = bundle.one("PublicationReleaseRecord"); extension = release.extensions[0]
    required_ext = {"owner_namespace", "name", "version", "authority_ref", "scope", "target_refs",
                    "criticality", "character", "validation_contract", "preservation", "payload"}
    if set(extension) != required_ext or tuple(extension.get(k) for k in (
            "owner_namespace", "name", "version", "authority_ref", "scope", "criticality",
            "character", "validation_contract", "preservation")) != (
            "briefforge-publication-release", "native-publication-release-authorization", "2.0.0",
            ACCEPTED_AUTHORITY_IDENTITY, "native-bcrp-publication-release", "required", "semantic",
            NATIVE_AUTHORIZATION_CONTRACT, "must-preserve"):
        raise ReleaseRejected("Native v2 Release extension is unknown, mixed, or incomplete.")
    payload = extension.get("payload")
    payload_keys = {"contract_version", "authorization", "candidate", "judgment", "ready",
        "governed_ready_closure_fingerprint", "evidence_snapshot",
        "authority_constraints"}
    if type(payload) is not dict or set(payload) != payload_keys or payload.get("contract_version") != "2.0.0":
        raise ReleaseRejected("Native v2 Release payload is incomplete or contains undeclared fields.")
    ready_bundle = BCRPBundle(bundle.profile_identity, bundle.profile_version,
                              tuple(deepcopy(item) for item in bundle.records[:5]))
    try:
        binding = verify_persisted_native_ready_binding(ready_bundle)
    except (NativeGovernanceRejected, TypeError, ValueError) as exc:
        raise ReleaseRejected("Native v2 predecessor closure failed independent semantic binding verification.") from exc
    auth = _native_auth_from_document(payload["authorization"])
    constraints = auth.release_distribution_constraints
    _verify_native_persisted_release_authorization(auth, binding, snapshot,
        release.semantic.get("publication_lineage_id"), release.semantic.get("semantic_publication_version"),
        release.identity, _normalize_time(release.semantic.get("publication_time"), "Release time"),
        constraints, release.semantic.get("includes_recommendations"))
    expected_targets = [release.identity, binding.ready_identity, binding.judgment_identity, binding.candidate_identity]
    if extension.get("target_refs") != expected_targets:
        raise ReleaseRejected("Native v2 Release targets another Candidate/Judgment/Ready closure.")
    expected_payload = {
        "contract_version": "2.0.0", "authorization": _native_auth_document(auth),
        "candidate": {"identity": binding.candidate_identity,
            "candidate_semantic_fingerprint": binding.candidate_semantic_fingerprint,
            "subject_closure_fingerprint": binding.subject_closure_fingerprint,
            "profile_instance_fingerprint": binding.profile_instance_fingerprint,
            "profile_sha256": hashlib.sha256(canonical_json_bytes(BCRPBundle(bundle.profile_identity,
                bundle.profile_version, tuple(deepcopy(item) for item in bundle.records[:3])),
                domain="profile-instance", require_valid=False)).hexdigest()},
        "judgment": {"identity": binding.judgment_identity, "fingerprint": binding.judgment_fingerprint},
        "ready": {"identity": binding.ready_identity, "fingerprint": binding.ready_fingerprint,
                  "core_ready_fingerprint": binding.core_ready_fingerprint},
        "governed_ready_closure_fingerprint": binding.ready_fingerprint,
        "evidence_snapshot": {"identity": snapshot.identity, "version": snapshot.version,
                              "inventory_digest": snapshot.inventory_digest},
        "authority_constraints": {"initial_state": _INITIAL_STATE,
            "distribution_constraints": list(constraints),
            "excluded_authorities": ["renderer", "artifact", "manifest", "distribution-execution"]},
    }
    if payload != expected_payload:
        raise ReleaseRejected("Native v2 complete Candidate/Judgment/Ready/snapshot closure drifted.")
    ready_record = bundle.one("ReadyPresentationPackageRecord")
    _verify_release_core(release, ready=ready_record, snapshot=snapshot, authorization=auth)
    fp = fingerprint_bundle(bundle, domain="release-semantic", require_valid=False)
    if expected_release_fingerprint is not None:
        if type(expected_release_fingerprint) is not str or not _DIGEST_RE.fullmatch(expected_release_fingerprint):
            raise ReleaseRejected("Expected Release fingerprint is missing or malformed.")
        if fp.digest != expected_release_fingerprint:
            raise ReleaseRejected("Persisted Release fingerprint does not match the accepted exact binding.")
    generic = validate_bundle(bundle, through_layer="L4")
    expected_unknown = {(binding.judgment_identity, "/extensions/0"),
                        (binding.ready_identity, "/extensions/0"), (release.identity, "/extensions/0")}
    # Core graph validation cannot resolve the dedicated policy authorities or
    # the external snapshot identity. Reconcile only these exact findings after
    # the specialized verifier above has authenticated all of those bindings.
    expected_absent = {
        ("L1", binding.judgment_identity, binding.judgment_identity,
         "Canonical reference targets absent identity 'authority:briefforge-publication-judgment'."),
        ("L1", binding.ready_identity, binding.ready_identity,
         "Canonical reference targets absent identity 'authority:briefforge-publication-readiness'."),
        ("L1", release.identity, release.identity,
         f"Canonical reference targets absent identity '{snapshot.identity}'."),
        ("L2", binding.judgment_identity, binding.judgment_identity,
         "Semantic reference targets absent identity 'authority:briefforge-publication-judgment'."),
        ("L2", binding.ready_identity, binding.ready_identity,
         "Semantic reference targets absent identity 'authority:briefforge-publication-readiness'."),
        ("L2", release.identity, release.identity,
         f"Semantic reference targets absent identity '{snapshot.identity}'."),
    }
    observed_unknown = set()
    observed_absent = set()
    unrelated = []
    for item in generic.findings:
        unknown = (item.layer == "L1" and item.family == "extension-boundary" and
            item.severity == "blocking" and
            item.message == "Unknown required semantic extension cannot be processed." and
            (item.semantic_identity, item.location) in expected_unknown)
        absent_key = (item.layer, item.semantic_identity, item.location, item.message)
        absent = (item.family == "identity-or-reference-integrity" and
                  item.severity == "blocking" and absent_key in expected_absent)
        if unknown:
            observed_unknown.add((item.semantic_identity, item.location))
        elif absent:
            observed_absent.add(absent_key)
        else:
            unrelated.append(item)
    if unrelated or observed_unknown != expected_unknown or observed_absent != expected_absent:
        raise ReleaseRejected("Dedicated native Release validation found unrelated or incomplete findings.")
    return VerifiedPublicationRelease(_serialize_bundle(bundle), fp, auth, deepcopy(snapshot), generic.executed_layers)



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
