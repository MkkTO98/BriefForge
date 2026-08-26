"""Fail-closed legacy lifecycle authority representation for BCRP.

This module intentionally sits outside ``briefforge.bcrp`` because it depends on
legacy runtime, validation, and promotion types. It grants no authority: it can
only verify one exact already-governed legacy Candidate/Judgment/Ready closure
and represent that closure with existing BCRP Judgment and Ready record kinds.
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
from .bcrp.model import BCRPBundle, BCRPRecord, PROFILE_VERSION
from .bcrp.validation import validate_bundle
from .promotion import ReadyPresentationPackage
from .runtime import CandidatePresentationPackage, semantic_fingerprint
from .validation import CURRENT_VALIDATION_POLICY_ID, ValidationJudgment

_EXTENSION_OWNER = "briefforge-legacy-lifecycle-compatibility"
_EXTENSION_NAME = "governed-lifecycle-lineage"
_EXTENSION_VERSION = "1.0.0"
_EXTENSION_SCOPE = "legacy-to-bcrp-lifecycle-representation"
_EXTENSION_CONTRACT = "briefforge:legacy-lifecycle-compatibility:1.0.0"
_ACCEPTED_BCRP_POLICY_ID = "bcrp-legacy-compatibility-policy:1.0.0"
_ACCEPTED_AUTHORITY_OWNER = "project:BriefForge"
_ACCEPTED_AUTHORITY_ROLE = "validation-authority"
_EXCLUDED_AUTHORITIES = ["publication-release", "renderer", "artifact", "manifest"]
_CANDIDATE_KINDS = (
    "PresentationBriefRecord",
    "PortablePresentationMaterialRecord",
    "CandidatePresentationPackageRecord",
)
_PROHIBITED_EXISTING_KINDS = (
    "ValidationJudgmentRecord",
    "ReadyPresentationPackageRecord",
    "PublicationReleaseRecord",
    "RendererCapabilityDeclarationRecord",
    "RendererCompatibilityPlanRecord",
    "GeneratedArtifactAuditRecord",
    "SemanticArtifactConformanceRecord",
    "PublicationManifestRecord",
)


class CompatibilityRejected(ValueError):
    """Raised before any mapped authority record is returned."""


@dataclass(frozen=True)
class EvidenceIdentityAndTime:
    scope_identity: str
    legacy_candidate_evidence_identity: str
    legacy_judgment_evidence_identity: str
    legacy_ready_evidence_identity: str
    validation_time: str
    readiness_time: str
    inventory_complete: bool
    competing_lifecycle_evidence_identities: tuple[str, ...]
    inventory_digest: str
    mapping_attestation_identity: str
    mapping_attestation_time: str
    mapping_attested_by_authority_identity: str


@dataclass(frozen=True)
class IdentityMapping:
    legacy_candidate_identity: str
    bcrp_candidate_identity: str
    bcrp_judgment_identity: str
    bcrp_ready_identity: str


@dataclass(frozen=True)
class PolicyTranslation:
    legacy_policy_identity: str
    bcrp_policy_identity: str
    authority_basis: str
    bcrp_authority_identity: str


@dataclass(frozen=True)
class FingerprintLineage:
    legacy_domain: str
    legacy_digest: str
    bcrp_domain: str
    bcrp_digest: str
    relationship: str


@dataclass(frozen=True)
class LegacyCompatibilityMapping:
    evidence: EvidenceIdentityAndTime
    identities: IdentityMapping
    policy: PolicyTranslation
    fingerprints: FingerprintLineage
    all_bcrp_semantic_material_explicit: bool


def map_legacy_ready_to_bcrp(
    *,
    legacy_candidate: CandidatePresentationPackage,
    legacy_judgment: ValidationJudgment,
    legacy_ready: ReadyPresentationPackage,
    bcrp_candidate_bundle: BCRPBundle,
    mapping: LegacyCompatibilityMapping,
) -> BCRPBundle:
    """Represent one verified governed legacy Ready closure in BCRP.

    Every semantic and identity bridge is explicit. Inputs are never mutated and
    no partial Judgment is returned on failure.
    """

    _verify_mapping_material_types(mapping)
    legacy_digest = _verify_legacy_closure(
        legacy_candidate,
        legacy_judgment,
        legacy_ready,
        mapping,
    )
    _verify_policy_authority(bcrp_candidate_bundle, legacy_judgment, legacy_ready, mapping.policy)
    normalized_validation_time, normalized_readiness_time, normalized_attestation_time = _verify_evidence(
        mapping.evidence,
        legacy_digest=legacy_digest,
        legacy_policy_identity=mapping.policy.legacy_policy_identity,
        attesting_authority_identity=mapping.policy.bcrp_authority_identity,
    )
    candidate, bcrp_digest = _verify_bcrp_candidate(bcrp_candidate_bundle, mapping)
    _verify_lineage(mapping.fingerprints, legacy_digest, bcrp_digest)

    payload = {
        "contract_version": _EXTENSION_VERSION,
        "authority_basis": mapping.policy.authority_basis,
        "policy_translation": {
            "legacy_policy_identity": mapping.policy.legacy_policy_identity,
            "bcrp_policy_identity": mapping.policy.bcrp_policy_identity,
        },
        "legacy_evidence_identities": {
            "candidate": mapping.evidence.legacy_candidate_evidence_identity,
            "judgment": mapping.evidence.legacy_judgment_evidence_identity,
            "ready": mapping.evidence.legacy_ready_evidence_identity,
        },
        "identity_mapping": {
            "legacy_candidate_identity": mapping.identities.legacy_candidate_identity,
            "bcrp_candidate_identity": mapping.identities.bcrp_candidate_identity,
            "bcrp_judgment_identity": mapping.identities.bcrp_judgment_identity,
            "bcrp_ready_identity": mapping.identities.bcrp_ready_identity,
        },
        "fingerprint_lineage": {
            "legacy_domain": mapping.fingerprints.legacy_domain,
            "legacy_digest": legacy_digest,
            "bcrp_domain": mapping.fingerprints.bcrp_domain,
            "bcrp_digest": bcrp_digest,
            "relationship": mapping.fingerprints.relationship,
        },
        "lifecycle_times": {
            "validation_time": normalized_validation_time,
            "readiness_time": normalized_readiness_time,
        },
        "mapping_attestation": {
            "scope_identity": mapping.evidence.scope_identity,
            "inventory_complete": True,
            "competing_lifecycle_evidence_identities": [],
            "inventory_digest": mapping.evidence.inventory_digest,
            "attestation_identity": mapping.evidence.mapping_attestation_identity,
            "attestation_time": normalized_attestation_time,
            "attested_by_authority_identity": mapping.evidence.mapping_attested_by_authority_identity,
        },
        "all_bcrp_semantic_material_explicit": True,
        "downstream_eligibility": "explicit-compatibility-verifiers-only",
        "excluded_authorities": list(_EXCLUDED_AUTHORITIES),
    }

    judgment_payload = deepcopy(payload)
    judgment_payload["status"] = "mapped-governed-judgment-representation"
    judgment = BCRPRecord(
        kind="ValidationJudgmentRecord",
        identity=mapping.identities.bcrp_judgment_identity,
        profile_version=PROFILE_VERSION,
        semantic={
            "candidate_ref": candidate.identity,
            "candidate_fingerprint": bcrp_digest,
            "policy_id": mapping.policy.bcrp_policy_identity,
            "executed_layers": ["legacy-governed-validation"],
            "findings": [],
            "valid": True,
            "validation_time": normalized_validation_time,
        },
        extensions=[_extension(mapping.policy.bcrp_authority_identity, candidate.identity, judgment_payload)],
    )

    ready_digest = hashlib.sha256(
        f"{mapping.identities.bcrp_ready_identity}|{bcrp_digest}".encode("utf-8")
    ).hexdigest()
    ready_payload = deepcopy(payload)
    ready_payload["status"] = "mapped-governed-ready-representation"
    ready = BCRPRecord(
        kind="ReadyPresentationPackageRecord",
        identity=mapping.identities.bcrp_ready_identity,
        profile_version=PROFILE_VERSION,
        semantic={
            "candidate_ref": candidate.identity,
            "candidate_fingerprint": bcrp_digest,
            "judgment_ref": judgment.identity,
            "readiness_time": normalized_readiness_time,
            "ready_fingerprint": ready_digest,
        },
        extensions=[_extension(mapping.policy.bcrp_authority_identity, candidate.identity, ready_payload)],
    )

    mapped = deepcopy(bcrp_candidate_bundle)
    mapped.records = mapped.records + (judgment, ready)
    mapped.index = {"mapped_in_memory": True}
    mapped.source_root = None
    mapped.derived_reverse_index = {}
    return verify_mapped_legacy_ready(mapped)


def verify_mapped_legacy_ready(bundle: BCRPBundle) -> BCRPBundle:
    """Fail closed if a mapped BCRP Ready representation has drifted or is incomplete."""

    if not isinstance(bundle, BCRPBundle):
        raise CompatibilityRejected("Mapped lifecycle verification requires a BCRPBundle.")
    expected_counts = {kind: 1 for kind in _CANDIDATE_KINDS + ("ValidationJudgmentRecord", "ReadyPresentationPackageRecord")}
    if any(len(bundle.records_of_kind(kind)) != count for kind, count in expected_counts.items()):
        raise CompatibilityRejected("Mapped lifecycle closure is incomplete or competing.")
    if len(bundle.records) != 5 or any(bundle.records_of_kind(kind) for kind in _PROHIBITED_EXISTING_KINDS[2:]):
        raise CompatibilityRejected("Mapped lifecycle closure contains competing or unauthorized records.")

    result = validate_bundle(bundle, through_layer="L2")
    compatibility_findings = tuple(
        finding
        for finding in result.findings
        if finding.layer == "L1"
        and finding.family == "extension-boundary"
        and finding.semantic_identity in {
            bundle.one("ValidationJudgmentRecord").identity,
            bundle.one("ReadyPresentationPackageRecord").identity,
        }
        and finding.location == "/extensions/0"
        and finding.message == "Unknown required semantic extension cannot be processed."
    )
    other_blocking = tuple(
        finding for finding in result.findings if finding.severity == "blocking" and finding not in compatibility_findings
    )
    if len(compatibility_findings) != 2 or other_blocking:
        raise CompatibilityRejected("Mapped lifecycle closure fails BCRP technical or compatibility-envelope validation.")

    candidate = bundle.one("CandidatePresentationPackageRecord")
    judgment = bundle.one("ValidationJudgmentRecord")
    ready = bundle.one("ReadyPresentationPackageRecord")
    digest = fingerprint_bundle(bundle, domain="candidate-semantic", require_valid=False).digest
    if judgment.semantic.get("candidate_ref") != candidate.identity or judgment.semantic.get("candidate_fingerprint") != digest:
        raise CompatibilityRejected("Mapped Judgment has Candidate identity or fingerprint drift.")
    if not judgment.semantic.get("valid") or judgment.semantic.get("findings"):
        raise CompatibilityRejected("Mapped Judgment no longer represents successful governed evidence.")
    if ready.semantic.get("candidate_ref") != candidate.identity or ready.semantic.get("candidate_fingerprint") != digest:
        raise CompatibilityRejected("Mapped Ready has Candidate identity or fingerprint drift.")
    if ready.semantic.get("judgment_ref") != judgment.identity:
        raise CompatibilityRejected("Mapped Ready does not bind the mapped Judgment.")
    expected_ready_digest = hashlib.sha256(f"{ready.identity}|{digest}".encode("utf-8")).hexdigest()
    if ready.semantic.get("ready_fingerprint") != expected_ready_digest:
        raise CompatibilityRejected("Mapped Ready fingerprint drifted.")

    judgment_payload = _verified_extension_payload(judgment, candidate.identity)
    ready_payload = _verified_extension_payload(ready, candidate.identity)
    if judgment.extensions[0]["authority_ref"] != ready.extensions[0]["authority_ref"]:
        raise CompatibilityRejected("Mapped Judgment and Ready disagree on compatibility authority.")
    if judgment_payload.get("status") != "mapped-governed-judgment-representation":
        raise CompatibilityRejected("Mapped Judgment compatibility status is absent or ambiguous.")
    if ready_payload.get("status") != "mapped-governed-ready-representation":
        raise CompatibilityRejected("Mapped Ready compatibility status is absent or ambiguous.")
    judgment_shared = deepcopy(judgment_payload)
    ready_shared = deepcopy(ready_payload)
    judgment_shared.pop("status", None)
    ready_shared.pop("status", None)
    if judgment_shared != ready_shared:
        raise CompatibilityRejected("Mapped Judgment and Ready compatibility evidence is contradictory.")
    _verify_persisted_payload(
        judgment_payload,
        candidate_identity=candidate.identity,
        judgment_identity=judgment.identity,
        ready_identity=ready.identity,
        bcrp_digest=digest,
        judgment=judgment,
        ready=ready,
        authority_identity=judgment.extensions[0]["authority_ref"],
        bundle=bundle,
    )

    return bundle


def _verify_mapping_material_types(mapping: LegacyCompatibilityMapping) -> None:
    if not isinstance(mapping, LegacyCompatibilityMapping):
        raise CompatibilityRejected("Explicit governed compatibility mapping material is required.")
    if not isinstance(mapping.evidence, EvidenceIdentityAndTime):
        raise CompatibilityRejected("Explicit legacy evidence identity and time material is required.")
    if not isinstance(mapping.identities, IdentityMapping):
        raise CompatibilityRejected("Explicit identity mapping is required.")
    if not isinstance(mapping.policy, PolicyTranslation):
        raise CompatibilityRejected("Explicit policy translation is required.")
    if not isinstance(mapping.fingerprints, FingerprintLineage):
        raise CompatibilityRejected("Explicit fingerprint lineage is required.")
    if mapping.all_bcrp_semantic_material_explicit is not True:
        raise CompatibilityRejected("All required BCRP semantic material must be supplied explicitly.")


def _verify_legacy_closure(
    candidate: CandidatePresentationPackage,
    judgment: ValidationJudgment,
    ready: ReadyPresentationPackage,
    mapping: LegacyCompatibilityMapping,
) -> str:
    if type(candidate) is not CandidatePresentationPackage or type(judgment) is not ValidationJudgment or type(ready) is not ReadyPresentationPackage:
        raise CompatibilityRejected("Exact governed legacy Candidate, Judgment, and Ready types are required.")
    if ready.candidate != candidate or ready.validation_judgment != judgment:
        raise CompatibilityRejected("Legacy Candidate/Judgment/Ready closure is stale or mismatched.")
    if not judgment.valid or judgment.findings:
        raise CompatibilityRejected("Legacy Judgment is not successful and finding-free.")
    if candidate.identity is None or judgment.candidate_package_id != candidate.identity.package_id:
        raise CompatibilityRejected("Legacy Judgment does not bind the exact Candidate identity.")
    if mapping.identities.legacy_candidate_identity != candidate.identity.package_id:
        raise CompatibilityRejected("Explicit legacy Candidate identity mapping is wrong.")

    digest = semantic_fingerprint(candidate)
    if judgment.candidate_semantic_fingerprint != digest or ready.semantic_fingerprint != digest:
        raise CompatibilityRejected("Legacy Candidate/Judgment/Ready fingerprint closure is stale or drifted.")
    if mapping.fingerprints.legacy_digest != digest:
        raise CompatibilityRejected("Declared legacy-domain fingerprint does not match recomputed legacy Candidate.")
    return digest


def lifecycle_evidence_inventory_digest(
    *,
    scope_identity: str,
    candidate_evidence_identity: str,
    judgment_evidence_identity: str,
    ready_evidence_identity: str,
    validation_time: str,
    readiness_time: str,
    legacy_candidate_digest: str,
    legacy_policy_identity: str,
    competing_lifecycle_evidence_identities: tuple[str, ...],
) -> str:
    """Bind one explicitly complete legacy lifecycle evidence inventory."""

    document = {
        "scope_identity": scope_identity,
        "candidate_evidence_identity": candidate_evidence_identity,
        "judgment_evidence_identity": judgment_evidence_identity,
        "ready_evidence_identity": ready_evidence_identity,
        "validation_time": validation_time,
        "readiness_time": readiness_time,
        "legacy_candidate_digest": legacy_candidate_digest,
        "legacy_policy_identity": legacy_policy_identity,
        "competing_lifecycle_evidence_identities": list(competing_lifecycle_evidence_identities),
    }
    encoded = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _verify_evidence(
    evidence: EvidenceIdentityAndTime,
    *,
    legacy_digest: str,
    legacy_policy_identity: str,
    attesting_authority_identity: str,
) -> tuple[str, str, str]:
    identities = (
        evidence.legacy_candidate_evidence_identity,
        evidence.legacy_judgment_evidence_identity,
        evidence.legacy_ready_evidence_identity,
    )
    if not all(_nonempty(value) for value in identities) or len(set(identities)) != 3:
        raise CompatibilityRejected("Distinct explicit Candidate/Judgment/Ready evidence identities are required.")
    if not _nonempty(evidence.scope_identity) or evidence.inventory_complete is not True:
        raise CompatibilityRejected("A complete governed lifecycle evidence scope inventory is required.")
    if not isinstance(evidence.competing_lifecycle_evidence_identities, tuple) or evidence.competing_lifecycle_evidence_identities:
        raise CompatibilityRejected("Competing lifecycle evidence makes authority ambiguous.")
    validation_time = _normalize_time(evidence.validation_time)
    readiness_time = _normalize_time(evidence.readiness_time)
    attestation_time = _normalize_time(evidence.mapping_attestation_time)
    if _parse_time(validation_time) > _parse_time(readiness_time) or _parse_time(readiness_time) > _parse_time(attestation_time):
        raise CompatibilityRejected("Legacy lifecycle or mapping-attestation timestamps are stale or reversed.")
    if not _nonempty(evidence.mapping_attestation_identity):
        raise CompatibilityRejected("Explicit mapping-attestation identity is required.")
    if evidence.mapping_attested_by_authority_identity != attesting_authority_identity:
        raise CompatibilityRejected("Mapping attestation is not issued by the declared compatibility authority.")
    expected_digest = lifecycle_evidence_inventory_digest(
        scope_identity=evidence.scope_identity,
        candidate_evidence_identity=evidence.legacy_candidate_evidence_identity,
        judgment_evidence_identity=evidence.legacy_judgment_evidence_identity,
        ready_evidence_identity=evidence.legacy_ready_evidence_identity,
        validation_time=validation_time,
        readiness_time=readiness_time,
        legacy_candidate_digest=legacy_digest,
        legacy_policy_identity=legacy_policy_identity,
        competing_lifecycle_evidence_identities=evidence.competing_lifecycle_evidence_identities,
    )
    if evidence.inventory_digest != expected_digest:
        raise CompatibilityRejected("Lifecycle evidence inventory digest is absent, stale, or wrong.")
    return validation_time, readiness_time, attestation_time


def _verify_bcrp_candidate(
    bundle: BCRPBundle,
    mapping: LegacyCompatibilityMapping,
) -> tuple[BCRPRecord, str]:
    if not isinstance(bundle, BCRPBundle):
        raise CompatibilityRejected("Explicit BCRP Candidate bundle is required.")
    if any(len(bundle.records_of_kind(kind)) != 1 for kind in _CANDIDATE_KINDS) or len(bundle.records) != 3:
        raise CompatibilityRejected("BCRP mapping input must be one exact Candidate-stage closure.")
    if any(bundle.records_of_kind(kind) for kind in _PROHIBITED_EXISTING_KINDS):
        raise CompatibilityRejected("BCRP mapping input already contains competing lifecycle or downstream records.")
    result = validate_bundle(bundle, through_layer="L2")
    if result.blocking:
        raise CompatibilityRejected("BCRP Candidate material is technically invalid or incomplete.")
    candidate = bundle.one("CandidatePresentationPackageRecord")
    if mapping.identities.bcrp_candidate_identity != candidate.identity:
        raise CompatibilityRejected("Explicit BCRP Candidate identity mapping is wrong.")
    digest = fingerprint_bundle(bundle, domain="candidate-semantic").digest
    if mapping.fingerprints.bcrp_digest != digest:
        raise CompatibilityRejected("Declared BCRP Candidate fingerprint is stale or wrong.")
    return candidate, digest


def _verify_lineage(lineage: FingerprintLineage, legacy_digest: str, bcrp_digest: str) -> None:
    if lineage.legacy_domain != "legacy-candidate-semantic" or lineage.bcrp_domain != "candidate-semantic":
        raise CompatibilityRejected("Fingerprint domains are unknown or incorrectly equated.")
    if lineage.relationship != "explicit-governed-mapping":
        raise CompatibilityRejected("Explicit cross-domain fingerprint lineage is required.")
    if lineage.legacy_digest != legacy_digest or lineage.bcrp_digest != bcrp_digest:
        raise CompatibilityRejected("Fingerprint lineage does not bind both exact digest domains.")


def _verify_policy_authority(
    bundle: BCRPBundle,
    judgment: ValidationJudgment,
    ready: ReadyPresentationPackage,
    policy: PolicyTranslation,
) -> None:
    if not all(
        _nonempty(value)
        for value in (
            policy.legacy_policy_identity,
            policy.bcrp_policy_identity,
            policy.bcrp_authority_identity,
        )
    ):
        raise CompatibilityRejected("Complete policy and authority translation evidence is required.")
    if policy.authority_basis != "policy-backed-system":
        raise CompatibilityRejected("Only honest policy-backed system authority is admitted.")
    if (
        policy.legacy_policy_identity != CURRENT_VALIDATION_POLICY_ID
        or policy.bcrp_policy_identity != _ACCEPTED_BCRP_POLICY_ID
        or judgment.validation_policy_id != policy.legacy_policy_identity
        or ready.validation_policy_id != policy.legacy_policy_identity
    ):
        raise CompatibilityRejected("Unknown or mismatched policy translation.")
    authority = _authority_objects(bundle).get(policy.bcrp_authority_identity)
    if not authority:
        raise CompatibilityRejected("Mapped BCRP authority identity is absent from explicit Candidate material.")
    if authority.get("role") != _ACCEPTED_AUTHORITY_ROLE or authority.get("owner_identity") != _ACCEPTED_AUTHORITY_OWNER:
        raise CompatibilityRejected("Mapped authority is not the accepted BriefForge validation authority role.")


def _authority_objects(bundle: BCRPBundle) -> dict[str, dict[str, Any]]:
    authorities_by_identity: dict[str, dict[str, Any]] = {}
    for record in bundle.records:
        authorities = record.semantic.get("authorities", [])
        if isinstance(authorities, list):
            for authority in authorities:
                if isinstance(authority, dict) and isinstance(authority.get("id"), str):
                    authorities_by_identity[authority["id"]] = authority
    return authorities_by_identity


def _verify_persisted_payload(
    payload: dict[str, Any],
    *,
    candidate_identity: str,
    judgment_identity: str,
    ready_identity: str,
    bcrp_digest: str,
    judgment: BCRPRecord,
    ready: BCRPRecord,
    authority_identity: str,
    bundle: BCRPBundle,
) -> None:
    expected_keys = {
        "contract_version",
        "status",
        "authority_basis",
        "policy_translation",
        "legacy_evidence_identities",
        "identity_mapping",
        "fingerprint_lineage",
        "lifecycle_times",
        "mapping_attestation",
        "all_bcrp_semantic_material_explicit",
        "downstream_eligibility",
        "excluded_authorities",
    }
    if set(payload) != expected_keys:
        raise CompatibilityRejected("Compatibility payload is incomplete or contains undeclared fields.")
    if payload["contract_version"] != _EXTENSION_VERSION or payload["authority_basis"] != "policy-backed-system":
        raise CompatibilityRejected("Compatibility contract or authority basis is wrong.")
    if payload["all_bcrp_semantic_material_explicit"] is not True:
        raise CompatibilityRejected("Mapped lifecycle lacks explicit BCRP semantic material declaration.")
    if payload["downstream_eligibility"] != "explicit-compatibility-verifiers-only":
        raise CompatibilityRejected("Mapped Ready downstream eligibility is ambiguous.")
    if payload["excluded_authorities"] != _EXCLUDED_AUTHORITIES:
        raise CompatibilityRejected("Mapped Ready incorrectly grants release, renderer, artifact, or manifest authority.")

    policy = payload["policy_translation"]
    if not isinstance(policy, dict) or set(policy) != {"legacy_policy_identity", "bcrp_policy_identity"}:
        raise CompatibilityRejected("Persisted policy translation is incomplete or undeclared.")
    if policy != {
        "legacy_policy_identity": CURRENT_VALIDATION_POLICY_ID,
        "bcrp_policy_identity": _ACCEPTED_BCRP_POLICY_ID,
    } or judgment.semantic.get("policy_id") != _ACCEPTED_BCRP_POLICY_ID:
        raise CompatibilityRejected("Persisted policy translation is unknown or contradicts the Judgment.")

    identities = payload["identity_mapping"]
    expected_identity_keys = {
        "legacy_candidate_identity",
        "bcrp_candidate_identity",
        "bcrp_judgment_identity",
        "bcrp_ready_identity",
    }
    if not isinstance(identities, dict) or set(identities) != expected_identity_keys:
        raise CompatibilityRejected("Persisted identity mapping is incomplete or undeclared.")
    if (
        not _nonempty(identities["legacy_candidate_identity"])
        or identities["bcrp_candidate_identity"] != candidate_identity
        or identities["bcrp_judgment_identity"] != judgment_identity
        or identities["bcrp_ready_identity"] != ready_identity
    ):
        raise CompatibilityRejected("Persisted identity mapping drifted.")

    evidence = payload["legacy_evidence_identities"]
    if not isinstance(evidence, dict) or set(evidence) != {"candidate", "judgment", "ready"}:
        raise CompatibilityRejected("Persisted lifecycle evidence identities are incomplete or undeclared.")
    if not all(_nonempty(value) for value in evidence.values()) or len(set(evidence.values())) != 3:
        raise CompatibilityRejected("Persisted lifecycle evidence identities are absent or ambiguous.")

    lineage = payload["fingerprint_lineage"]
    expected_lineage_keys = {"legacy_domain", "legacy_digest", "bcrp_domain", "bcrp_digest", "relationship"}
    if not isinstance(lineage, dict) or set(lineage) != expected_lineage_keys:
        raise CompatibilityRejected("Persisted fingerprint lineage is incomplete or undeclared.")
    if (
        lineage["legacy_domain"] != "legacy-candidate-semantic"
        or lineage["bcrp_domain"] != "candidate-semantic"
        or lineage["bcrp_digest"] != bcrp_digest
        or lineage["relationship"] != "explicit-governed-mapping"
        or not _digest(lineage["legacy_digest"])
    ):
        raise CompatibilityRejected("Fingerprint lineage is missing, cross-domain ambiguous, or drifted.")

    times = payload["lifecycle_times"]
    if not isinstance(times, dict) or set(times) != {"validation_time", "readiness_time"}:
        raise CompatibilityRejected("Persisted lifecycle times are incomplete or undeclared.")
    validation_time = _normalize_time(times["validation_time"])
    readiness_time = _normalize_time(times["readiness_time"])
    if validation_time != judgment.semantic.get("validation_time") or readiness_time != ready.semantic.get("readiness_time"):
        raise CompatibilityRejected("Persisted lifecycle times contradict core mapped records.")
    if _parse_time(validation_time) > _parse_time(readiness_time):
        raise CompatibilityRejected("Persisted lifecycle times are reversed.")

    attestation = payload["mapping_attestation"]
    expected_attestation_keys = {
        "scope_identity",
        "inventory_complete",
        "competing_lifecycle_evidence_identities",
        "inventory_digest",
        "attestation_identity",
        "attestation_time",
        "attested_by_authority_identity",
    }
    if not isinstance(attestation, dict) or set(attestation) != expected_attestation_keys:
        raise CompatibilityRejected("Persisted mapping attestation is incomplete or undeclared.")
    if (
        not _nonempty(attestation["scope_identity"])
        or attestation["inventory_complete"] is not True
        or attestation["competing_lifecycle_evidence_identities"] != []
        or not _nonempty(attestation["attestation_identity"])
        or attestation["attested_by_authority_identity"] != authority_identity
    ):
        raise CompatibilityRejected("Persisted mapping attestation is incomplete, competing, or unauthorized.")
    authority = _authority_objects(bundle).get(authority_identity)
    if not authority or authority.get("role") != _ACCEPTED_AUTHORITY_ROLE or authority.get("owner_identity") != _ACCEPTED_AUTHORITY_OWNER:
        raise CompatibilityRejected("Persisted mapping authority is not the accepted BriefForge validation role.")
    attestation_time = _normalize_time(attestation["attestation_time"])
    if _parse_time(readiness_time) > _parse_time(attestation_time):
        raise CompatibilityRejected("Persisted mapping attestation predates Ready evidence.")
    expected_inventory_digest = lifecycle_evidence_inventory_digest(
        scope_identity=attestation["scope_identity"],
        candidate_evidence_identity=evidence["candidate"],
        judgment_evidence_identity=evidence["judgment"],
        ready_evidence_identity=evidence["ready"],
        validation_time=validation_time,
        readiness_time=readiness_time,
        legacy_candidate_digest=lineage["legacy_digest"],
        legacy_policy_identity=policy["legacy_policy_identity"],
        competing_lifecycle_evidence_identities=(),
    )
    if attestation["inventory_digest"] != expected_inventory_digest:
        raise CompatibilityRejected("Persisted lifecycle inventory digest drifted.")


def _extension(authority_identity: str, candidate_identity: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "owner_namespace": _EXTENSION_OWNER,
        "name": _EXTENSION_NAME,
        "version": _EXTENSION_VERSION,
        "authority_ref": authority_identity,
        "scope": _EXTENSION_SCOPE,
        "target_refs": [candidate_identity],
        "criticality": "required",
        "character": "semantic",
        "validation_contract": _EXTENSION_CONTRACT,
        "preservation": "must-preserve",
        "payload": payload,
    }


def _verified_extension_payload(record: BCRPRecord, candidate_identity: str) -> dict[str, Any]:
    if len(record.extensions) != 1:
        raise CompatibilityRejected("Exactly one compatibility lineage extension is required.")
    extension = record.extensions[0]
    expected = {
        "owner_namespace": _EXTENSION_OWNER,
        "name": _EXTENSION_NAME,
        "version": _EXTENSION_VERSION,
        "scope": _EXTENSION_SCOPE,
        "target_refs": [candidate_identity],
        "criticality": "required",
        "character": "semantic",
        "validation_contract": _EXTENSION_CONTRACT,
        "preservation": "must-preserve",
    }
    if any(extension.get(key) != value for key, value in expected.items()) or not _nonempty(extension.get("authority_ref")):
        raise CompatibilityRejected("Compatibility lineage extension is incomplete or ambiguous.")
    payload = extension.get("payload")
    if not isinstance(payload, dict):
        raise CompatibilityRejected("Compatibility lineage payload is absent.")
    return payload


def _normalize_time(value: str) -> str:
    try:
        return canonicalize_timestamp(value)
    except (TypeError, ValueError) as exc:
        raise CompatibilityRejected("Explicit governed lifecycle timestamps with offsets are required.") from exc


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _digest(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())
