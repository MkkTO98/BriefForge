"""Additive v3 Publication Manifest admission for the paired terminal profile.

Evidence issued here is integrity evidence inside a trusted BriefForge process.  It
is not authentication against a hostile interpreter or modified process runtime,
and it grants no distribution, deployment, or successful-publication authority.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from typing import Any

from briefforge.bcrp.model import BCRPBundle, BCRPRecord, Fingerprint, PROFILE_VERSION
from briefforge.publication_manifest_admission import (
    ManifestArtifactAdmission, ManifestFinding, PublicationManifestAuthorization,
    PublicationManifestResult, VerifiedPublicationManifest,
    compute_artifact_set_fingerprint, compute_manifest_authorization_fingerprint,
)
import briefforge.publication_manifest_admission as manifest_core

from .controlled_invocation import (
    PairedTerminalRendererInvocationAuthorization, VerifiedPairedRendererInvocation,
    compute_paired_invocation_authorization_fingerprint,
    paired_renderer_implementation_digest,
    verify_persisted_paired_renderer_invocation,
)
from .profile import (
    PAIRED_CAPABILITY_TUPLE, PairedUpstreamAdmissionToken,
    paired_predecessor_prefix_fingerprint, paired_upstream_predecessor_bindings,
    verify_paired_upstream_admission_token,
)
from .projection import (
    compute_projection_fingerprint, paired_projection_implementation_digest,
)
from .schema import PairedEditorialProjection, PairedSemanticInput, validate_paired_projection
from .semantic_conformance import (
    ASSESSOR_IMPLEMENTATION, CONFORMANCE_PROFILE_IDENTITY, CONFORMANCE_PROFILE_VERSION,
    PairedTerminalSemanticArtifactConformanceAuthorization,
    VerifiedPairedSemanticArtifactConformance, paired_assessor_source_digest,
    compute_paired_conformance_authorization_fingerprint,
    verify_persisted_paired_semantic_artifact_conformance,
)

PAIRED_MANIFEST_POLICY_IDENTITY = "briefforge-paired-terminal-publication-manifest-admission-policy:3.0.0"
PAIRED_MANIFEST_PROFILE_IDENTITY = "briefforge:paired-terminal-publication-manifest-admission-profile:3.0.0"
PAIRED_MANIFEST_VERSION = "3.0.0"
PAIRED_MANIFEST_CONTRACT = "briefforge:paired-terminal-publication-manifest-admission-authority:3.0.0"
PAIRED_MANIFEST_IMPLEMENTATION = "briefforge_paired_terminal_profile.manifest_admission:1.0.0"
_PROJECTOR = "authority:briefforge-publication-manifest-projector"
_OWNER = "project:BriefForge"
_ROLE = "publication-manifest-projector"
_EXCLUSIONS = manifest_core._EXCLUSIONS
_KINDS = manifest_core._PREDECESSOR_KINDS
_MAX_EVIDENCE = 8 * 1024 * 1024

CAPABILITY_TUPLE = PAIRED_CAPABILITY_TUPLE


class PairedManifestRejected(ValueError):
    """An incomplete, stale, mixed-version, or unsafe paired Manifest act failed."""


def validate_paired_manifest_capability_tuple(value: object) -> None:
    if type(value) is not tuple or len(value) != 17:
        raise PairedManifestRejected("exact seventeen-entry paired capability tuple required")
    if any(type(item) is not tuple or len(item) != 2 or
           type(item[0]) is not str or type(item[1]) is not str for item in value):
        raise PairedManifestRejected("paired capability entries require exact immutable text pairs")
    if value != CAPABILITY_TUPLE:
        raise PairedManifestRejected("unknown, mixed, reordered, or incomplete paired capability tuple")


def paired_renderer_source_digest() -> str:
    """Backward-compatible spelling for the exact renderer implementation closure."""
    return paired_renderer_implementation_digest()


def paired_manifest_implementation_digest() -> str:
    """Digest the exact paired Manifest implementation source."""
    return hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest()


def _closure_digest(bundle: BCRPBundle) -> str:
    document = {"profile_identity": bundle.profile_identity,
                "profile_version": bundle.profile_version,
                "records": [record.to_document() for record in bundle.records]}
    return hashlib.sha256(json.dumps(document, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _predecessor(value: object, release_identity: str,
                 upstream_admission: PairedUpstreamAdmissionToken) -> BCRPBundle:
    if type(value) is not BCRPBundle or len(value.records) != 10:
        raise PairedManifestRejected("exact ten-record BCRP predecessor closure required")
    if tuple(record.kind for record in value.records) != _KINDS:
        raise PairedManifestRejected("paired predecessor kind/order closure differs")
    if value.one("PublicationReleaseRecord").identity != release_identity:
        raise PairedManifestRejected("predecessor Release differs from admitted Release")
    plan_documents, admitted_plan_fingerprint, capability_tuple = \
        paired_upstream_predecessor_bindings(upstream_admission)
    if capability_tuple != CAPABILITY_TUPLE:
        raise PairedManifestRejected("upstream admission capability tuple differs")
    actual_prefix = tuple(record.to_document() for record in value.records[:8])
    if actual_prefix != plan_documents:
        raise PairedManifestRejected("predecessor is not the exact admitted Plan closure")
    if paired_predecessor_prefix_fingerprint(actual_prefix) != admitted_plan_fingerprint:
        raise PairedManifestRejected("admitted Plan predecessor fingerprint differs")
    candidate = value.one("CandidatePresentationPackageRecord")
    judgment = value.one("ValidationJudgmentRecord")
    ready = value.one("ReadyPresentationPackageRecord")
    release = value.one("PublicationReleaseRecord")
    capability = value.one("RendererCapabilityDeclarationRecord")
    plan = value.one("RendererCompatibilityPlanRecord")
    audit = value.one("GeneratedArtifactAuditRecord")
    conformance = value.one("SemanticArtifactConformanceRecord")
    if (judgment.semantic.get("candidate_ref") != candidate.identity
            or judgment.semantic.get("valid") is not True
            or ready.semantic.get("candidate_ref") != candidate.identity
            or ready.semantic.get("judgment_ref") != judgment.identity
            or release.semantic.get("ready_ref") != ready.identity
            or plan.semantic.get("ready_ref") != ready.identity
            or plan.semantic.get("renderer_capability_ref") != capability.identity
            or audit.semantic.get("release_ref") != release.identity
            or audit.semantic.get("ready_ref") != ready.identity
            or audit.semantic.get("plan_ref") != plan.identity
            or audit.semantic.get("renderer_capability_ref") != capability.identity
            or audit.semantic.get("audit_links_pass") is not True
            or conformance.semantic.get("audit_ref") != audit.identity
            or conformance.semantic.get("ready_ref") != ready.identity
            or conformance.semantic.get("audit_link_pass") is not True
            or conformance.semantic.get("semantic_pass") is not True):
        raise PairedManifestRejected(
            "predecessor Candidate/Judgment/Ready/Release/Plan/Audit/Conformance lineage differs")
    authorities = value.one("PortablePresentationMaterialRecord").semantic.get("authorities")
    projector = {"id": _PROJECTOR, "owner_identity": _OWNER, "role": _ROLE,
                 "scope": "one-publication-manifest-production"}
    if type(authorities) is not list or [item for item in authorities
            if type(item) is dict and item.get("id") == _PROJECTOR] != [projector]:
        raise PairedManifestRejected("released paired Manifest projector authorization is absent")
    return value


def _active(lifecycle_scope: object, release_identity: str, fingerprint: str) -> None:
    if getattr(lifecycle_scope, "inventory_digest", None) != fingerprint:
        raise PairedManifestRejected("lifecycle scope differs from admitted Release scope")
    try:
        current = manifest_core._lifecycle_current(lifecycle_scope, release_identity)
    except Exception as exc:
        raise PairedManifestRejected("lifecycle active scope could not be independently verified") from exc
    if not current:
        raise PairedManifestRejected("admitted Release is not the sole current active Release")


def _reverify_inputs(*, admitted_semantics: PairedSemanticInput,
        upstream_admission: PairedUpstreamAdmissionToken,
        projection: PairedEditorialProjection, projection_evidence: object,
        invocation_authorization: PairedTerminalRendererInvocationAuthorization,
        verified_invocation: VerifiedPairedRendererInvocation,
        conformance_authorization: PairedTerminalSemanticArtifactConformanceAuthorization,
        verified_conformance: VerifiedPairedSemanticArtifactConformance) -> tuple[VerifiedPairedRendererInvocation, VerifiedPairedSemanticArtifactConformance]:
    if type(admitted_semantics) is not PairedSemanticInput:
        raise PairedManifestRejected("exact admitted Release semantic object required")
    if type(upstream_admission) is not PairedUpstreamAdmissionToken:
        raise PairedManifestRejected("exact admitted Release semantic token required")
    if type(projection) is not PairedEditorialProjection:
        raise PairedManifestRejected("exact paired projection required")
    validate_paired_projection(projection)
    if projection.projection_fingerprint != compute_projection_fingerprint(projection):
        raise PairedManifestRejected("paired projection fingerprint is stale")
    verify_paired_upstream_admission_token(upstream_admission, projection=projection)
    if type(invocation_authorization) is not PairedTerminalRendererInvocationAuthorization:
        raise PairedManifestRejected("exact paired invocation authorization required")
    if type(conformance_authorization) is not PairedTerminalSemanticArtifactConformanceAuthorization:
        raise PairedManifestRejected("exact paired conformance authorization required")
    if type(verified_invocation) is not VerifiedPairedRendererInvocation:
        raise PairedManifestRejected("exact persisted paired invocation proof required")
    if type(verified_conformance) is not VerifiedPairedSemanticArtifactConformance:
        raise PairedManifestRejected("exact persisted paired conformance proof required")
    invocation = verify_persisted_paired_renderer_invocation(
        projection=projection, authorization=invocation_authorization,
        upstream_admission=upstream_admission, projection_evidence=projection_evidence,
        artifact_path=verified_invocation.artifact_path,
        evidence_path=verified_invocation.evidence_path)
    if invocation != verified_invocation:
        raise PairedManifestRejected("supplied invocation proof differs from persisted bytes")
    conformance = verify_persisted_paired_semantic_artifact_conformance(
        admitted_semantics=admitted_semantics, upstream_admission=upstream_admission,
        projection_evidence=projection_evidence, invocation=invocation,
        invocation_authorization=invocation_authorization,
        authorization=conformance_authorization,
        evidence_path=verified_conformance.evidence_path)
    if conformance != verified_conformance:
        raise PairedManifestRejected("supplied conformance proof differs from persisted bytes")
    return invocation, conformance


def _expected_inventory(a: PublicationManifestAuthorization, projection: PairedEditorialProjection,
                        ia: PairedTerminalRendererInvocationAuthorization,
                        invocation: VerifiedPairedRendererInvocation,
                        ca: PairedTerminalSemanticArtifactConformanceAuthorization,
                        conformance: VerifiedPairedSemanticArtifactConformance) -> tuple[ManifestArtifactAdmission, ...]:
    supplied = a.artifact_inventory
    if type(supplied) is not tuple or len(supplied) != 1 or type(supplied[0]) is not ManifestArtifactAdmission:
        raise PairedManifestRejected("exactly one standard Manifest artifact admission required")
    item = supplied[0]
    expected = {
        "role": "primary-semantic-publication", "logical_filename": ia.output_filename,
        "media_type": ia.media_type, "byte_length": len(invocation.artifact_bytes),
        "sha256": hashlib.sha256(invocation.artifact_bytes).hexdigest(), "order": 0,
        "source_path": str(invocation.artifact_path),
        "release_identity": projection.release_identity, "release_fingerprint": projection.release_fingerprint,
        "plan_identity": projection.plan_identity, "plan_fingerprint": projection.plan_fingerprint,
        "renderer_identity": ia.renderer_identity, "renderer_version": ia.renderer_version,
        "invocation_authorization_identity": ia.identity,
        "invocation_evidence_fingerprint": invocation.fingerprint,
        "conformance_authorization_identity": ca.identity,
        "conformance_evidence_fingerprint": conformance.fingerprint,
        "dependency_identities": (),
    }
    if not manifest_core._stable_text(item.identity) or any(getattr(item, k, None) != v for k, v in expected.items()):
        raise PairedManifestRejected("artifact admission differs from persisted paired evidence")
    return supplied


def _validate_authorization(a: object, *, projection: PairedEditorialProjection,
        predecessor: BCRPBundle, lifecycle_scope: object,
        ia: PairedTerminalRendererInvocationAuthorization,
        invocation: VerifiedPairedRendererInvocation,
        ca: PairedTerminalSemanticArtifactConformanceAuthorization,
        conformance: VerifiedPairedSemanticArtifactConformance) -> PublicationManifestAuthorization:
    if type(a) is not PublicationManifestAuthorization:
        raise PairedManifestRejected("exact PublicationManifestAuthorization required")
    if ia.fingerprint != compute_paired_invocation_authorization_fingerprint(ia):
        raise PairedManifestRejected("paired invocation authorization fingerprint is stale")
    if ca.fingerprint != compute_paired_conformance_authorization_fingerprint(ca):
        raise PairedManifestRejected("paired conformance authorization fingerprint is stale")
    _active(lifecycle_scope, projection.release_identity, projection.lifecycle_scope_fingerprint)
    inventory = _expected_inventory(a, projection, ia, invocation, ca, conformance)
    closure = _closure_digest(predecessor)
    expected = {
        "policy_identity": PAIRED_MANIFEST_POLICY_IDENTITY,
        "profile_identity": PAIRED_MANIFEST_PROFILE_IDENTITY, "profile_version": PAIRED_MANIFEST_VERSION,
        "authority_identity": _PROJECTOR, "authority_owner": _OWNER, "authority_role": _ROLE,
        "release_identity": projection.release_identity, "release_fingerprint": projection.release_fingerprint,
        "lifecycle_inventory_digest": projection.lifecycle_scope_fingerprint,
        "plan_identity": projection.plan_identity, "plan_fingerprint": projection.plan_fingerprint,
        "capability_identity": projection.capability_declaration_identity,
        "capability_fingerprint": projection.capability_declaration_fingerprint,
        "renderer_identity": ia.renderer_identity, "renderer_version": ia.renderer_version,
        "renderer_implementation_digest": paired_renderer_source_digest(),
        "invocation_authorization_identity": ia.identity,
        "invocation_authorization_fingerprint": ia.fingerprint,
        "invocation_evidence_fingerprint": invocation.fingerprint,
        "conformance_authorization_identity": ca.identity,
        "conformance_authorization_fingerprint": ca.fingerprint,
        "conformance_profile_identity": CONFORMANCE_PROFILE_IDENTITY,
        "conformance_profile_version": CONFORMANCE_PROFILE_VERSION,
        "assessor_identity": ASSESSOR_IMPLEMENTATION,
        "conformance_evidence_fingerprint": conformance.fingerprint,
        "conformance_verdict": "approved", "predecessor_closure_fingerprint": closure,
        "artifact_inventory": inventory,
        "artifact_set_fingerprint": compute_artifact_set_fingerprint(inventory),
        "manifest_version": PAIRED_MANIFEST_VERSION,
        "projector_implementation": PAIRED_MANIFEST_IMPLEMENTATION,
        "projector_version": "1.0.0", "exclusions": _EXCLUSIONS,
    }
    mismatches = [name for name, value in expected.items() if getattr(a, name, None) != value]
    if mismatches:
        raise PairedManifestRejected("paired Manifest atomic authorization mismatch: " + ",".join(mismatches))
    if a.fingerprint != compute_manifest_authorization_fingerprint(a):
        raise PairedManifestRejected("paired Manifest authorization fingerprint is stale")
    if a.evidence_filename != "publication-manifest.json":
        raise PairedManifestRejected("paired Manifest evidence filename differs")
    if a.record_identity in predecessor.by_identity() or len({a.identity, a.manifest_identity, a.record_identity}) != 3:
        raise PairedManifestRejected("paired Manifest identities are not unique")
    for value, existing in ((a.evidence_directory, True), (a.commitment_ledger_directory, False)):
        path = Path(value)
        if not path.is_absolute() or str(path.resolve()) != value or path.is_symlink() or (existing and not path.is_dir()):
            raise PairedManifestRejected("unsafe paired Manifest persistence boundary")
    try:
        before = manifest_core._parse_offset_time(ia.authorization_time)
        assessed = manifest_core._parse_offset_time(ca.authorization_time)
        authorized = manifest_core._parse_offset_time(a.authorization_time)
        created = manifest_core._parse_offset_time(a.manifest_time)
        if before > assessed or assessed > authorized or authorized > created:
            raise ValueError
    except Exception as exc:
        raise PairedManifestRejected("paired Manifest chronology is invalid") from exc
    return a


def _record(predecessor: BCRPBundle, a: PublicationManifestAuthorization,
            projection: PairedEditorialProjection,
            ia: PairedTerminalRendererInvocationAuthorization,
            invocation: VerifiedPairedRendererInvocation,
            ca: PairedTerminalSemanticArtifactConformanceAuthorization,
            conformance: VerifiedPairedSemanticArtifactConformance) -> BCRPRecord:
    release = predecessor.one("PublicationReleaseRecord")
    audit = predecessor.one("GeneratedArtifactAuditRecord")
    semantic_conformance = predecessor.one("SemanticArtifactConformanceRecord")
    artifacts = [manifest_core._artifact_document(x) for x in a.artifact_inventory]
    atomic = {
        "capability_tuple": [list(item) for item in CAPABILITY_TUPLE],
        "projection_fingerprint": projection.projection_fingerprint,
        "content_closure_fingerprint": projection.content_closure_fingerprint,
        "projection_implementation_digest": paired_projection_implementation_digest(),
        "renderer_implementation_digest": a.renderer_implementation_digest,
        "invocation_implementation_digest": ia.renderer_implementation_digest,
        "invocation_authorization_fingerprint": ia.fingerprint,
        "invocation_evidence_fingerprint": invocation.fingerprint,
        "invocation_evidence_sha256": hashlib.sha256(invocation.evidence_bytes).hexdigest(),
        "assessor_source_digest": paired_assessor_source_digest(),
        "assessor_authorized_digest": ca.assessor_implementation_digest,
        "manifest_implementation_digest": paired_manifest_implementation_digest(),
        "conformance_authorization_fingerprint": ca.fingerprint,
        "conformance_evidence_fingerprint": conformance.fingerprint,
        "conformance_evidence_sha256": hashlib.sha256(conformance.evidence_bytes).hexdigest(),
        "predecessor_closure_fingerprint": a.predecessor_closure_fingerprint,
        "artifact_set_fingerprint": a.artifact_set_fingerprint,
    }
    payload = {
        "contract_identity": PAIRED_MANIFEST_CONTRACT,
        "policy_identity": a.policy_identity, "profile_identity": a.profile_identity,
        "profile_version": a.profile_version, "authorization_identity": a.identity,
        "authorization_fingerprint": a.fingerprint, "manifest_identity": a.manifest_identity,
        "manifest_version": a.manifest_version, "manifest_time": a.manifest_time,
        "lifecycle_inventory_digest": a.lifecycle_inventory_digest,
        "artifact_inventory": artifacts, "paired_atomic_tuple": atomic,
        "aggregate_manifest_verdict": "approved", "verification_status": "verified",
        "authority_exclusions": list(a.exclusions), "manifest_authority": "admission-only",
        "distribution_authority": "absent", "distribution_execution": "not-performed",
        "successful_publication": "not-asserted", "deployment_authority": "absent",
        "trusted_process_limitation": "no security claim against a hostile interpreter",
    }
    catalog = [{k: d[k] for k in ("identity", "role", "order", "logical_filename",
                                   "media_type", "byte_length", "sha256")} for d in artifacts]
    return BCRPRecord("PublicationManifestRecord", a.record_identity, PROFILE_VERSION, {
        "release_ref": release.identity, "lifecycle_status": release.semantic["lifecycle_status"],
        "artifact_audit_refs": [audit.identity], "conformance_refs": [semantic_conformance.identity],
        "artifact_ids": [x.identity for x in a.artifact_inventory],
        "manifest_identity": a.manifest_identity, "manifest_version": a.manifest_version,
        "policy_identity": a.policy_identity, "profile_identity": a.profile_identity,
        "profile_version": a.profile_version, "authorization_time": a.authorization_time,
        "manifest_time": a.manifest_time, "artifact_catalog": catalog,
    }, [{
        "owner_namespace": "briefforge-paired-terminal-publication-manifest-admission",
        "name": "exact-paired-artifact-admission", "version": PAIRED_MANIFEST_VERSION,
        "authority_ref": _PROJECTOR, "scope": "publication-manifest-admission-only",
        "target_refs": [release.identity, audit.identity, semantic_conformance.identity] +
                       [x.identity for x in a.artifact_inventory],
        "criticality": "required", "character": "semantic",
        "validation_contract": PAIRED_MANIFEST_CONTRACT,
        "preservation": "must-preserve", "payload": payload,
    }])


def _verify_bundle(bundle: BCRPBundle, predecessor: BCRPBundle, a: PublicationManifestAuthorization,
                   projection: PairedEditorialProjection, ia, invocation, ca, conformance) -> VerifiedPublicationManifest:
    if len(bundle.records) != 11 or tuple(x.kind for x in bundle.records[:10]) != _KINDS or bundle.records[-1].kind != "PublicationManifestRecord":
        raise PairedManifestRejected("paired Manifest requires exact eleven-kind BCRP closure")
    if tuple(x.to_document() for x in bundle.records[:10]) != tuple(x.to_document() for x in predecessor.records):
        raise PairedManifestRejected("paired Manifest changed predecessor closure")
    expected = _record(predecessor, a, projection, ia, invocation, ca, conformance)
    if bundle.records[-1].to_document() != expected.to_document():
        raise PairedManifestRejected("paired Manifest differs from independent reproduction")
    digest = _closure_digest(bundle)
    fingerprint = Fingerprint("manifest-instance", bundle.records[0].identity,
        bundle.profile_identity, bundle.profile_version,
        "canonical-json-rfc8785-subset-v1", "sha256", digest,
        "exact paired eleven-record Manifest closure")
    return VerifiedPublicationManifest._admitted(manifest_core._serialize_bundle(bundle), fingerprint)


def _common(kwargs: dict[str, Any]):
    if "capability_tuple" not in kwargs:
        raise PairedManifestRejected("explicit frozen paired capability tuple required")
    validate_paired_manifest_capability_tuple(kwargs["capability_tuple"])
    projection = kwargs["projection"]
    invocation, conformance = _reverify_inputs(
        admitted_semantics=kwargs["admitted_semantics"], upstream_admission=kwargs["upstream_admission"],
        projection=projection, projection_evidence=kwargs["projection_evidence"],
        invocation_authorization=kwargs["invocation_authorization"],
        verified_invocation=kwargs["verified_invocation"],
        conformance_authorization=kwargs["conformance_authorization"],
        verified_conformance=kwargs["verified_conformance"])
    predecessor = _predecessor(kwargs["predecessor_bundle"], projection.release_identity,
                               kwargs["upstream_admission"])
    a = _validate_authorization(kwargs["authorization"], projection=projection,
        predecessor=predecessor, lifecycle_scope=kwargs["lifecycle_scope"],
        ia=kwargs["invocation_authorization"], invocation=invocation,
        ca=kwargs["conformance_authorization"], conformance=conformance)
    return predecessor, a, projection, invocation, conformance


def produce_paired_terminal_publication_manifest(**kwargs: Any) -> PublicationManifestResult:
    """Consume one authorization, persist canonical evidence, and independently reload it."""
    try:
        predecessor, a, projection, invocation, conformance = _common(dict(kwargs))
        manifest_core._reserve_authorization(a)
        bundle = BCRPBundle(predecessor.profile_identity, predecessor.profile_version,
                            predecessor.records + (_record(predecessor, a, projection,
                            kwargs["invocation_authorization"], invocation,
                            kwargs["conformance_authorization"], conformance),))
        verified = _verify_bundle(bundle, predecessor, a, projection,
            kwargs["invocation_authorization"], invocation,
            kwargs["conformance_authorization"], conformance)
        manifest_core._persist_manifest_transaction(a, verified._bundle_document.encode("utf-8"))
        reloaded = verify_persisted_paired_terminal_publication_manifest(
            manifest_evidence_path=Path(a.evidence_directory) / a.evidence_filename, **kwargs)
        return PublicationManifestResult((), reloaded)
    except Exception as exc:
        return PublicationManifestResult((ManifestFinding(
            "paired-manifest-admission-blocked", "/manifest", str(exc)),), None)


def verify_persisted_paired_terminal_publication_manifest(*,
        manifest_evidence_path: Path, **kwargs: Any) -> VerifiedPublicationManifest:
    """Reverify all upstream bytes, canonical Manifest bytes, and external commitments."""
    predecessor, a, projection, invocation, conformance = _common(dict(kwargs))
    expected = Path(a.evidence_directory) / a.evidence_filename
    if not isinstance(manifest_evidence_path, Path) or manifest_evidence_path != expected:
        raise PairedManifestRejected("paired Manifest evidence path differs from authorization")
    evidence = manifest_core._read_regular_path(expected, _MAX_EVIDENCE)
    try:
        text = evidence.decode("utf-8")
        bundle = manifest_core._deserialize_bundle(text)
    except Exception as exc:
        raise PairedManifestRejected("paired Manifest evidence is malformed") from exc
    if text != manifest_core._serialize_bundle(bundle):
        raise PairedManifestRejected("paired Manifest evidence bytes are noncanonical")
    verified = _verify_bundle(bundle, predecessor, a, projection,
        kwargs["invocation_authorization"], invocation,
        kwargs["conformance_authorization"], conformance)
    ledger = Path(a.commitment_ledger_directory)
    if manifest_core._read_regular_path(ledger / manifest_core._consumption_name(a), 8192) != manifest_core._consumption_bytes(a):
        raise PairedManifestRejected("paired Manifest authorization consumption differs")
    if manifest_core._read_regular_path(ledger / manifest_core._commitment_name(a), 8192) != manifest_core._commitment_bytes(a, evidence):
        raise PairedManifestRejected("paired Manifest external commitment differs")
    return verified


def verify_paired_manifest_current_eligibility(verified: object, *, lifecycle_scope: object) -> PublicationManifestResult:
    """Re-evaluate current lifecycle state without changing historical evidence."""
    if type(verified) is not VerifiedPublicationManifest or verified._marker is not manifest_core._VERIFIED_MARKER:
        return PublicationManifestResult((ManifestFinding(
            "invalid-verified-paired-manifest", "/manifest", "exact admitted paired Manifest required"),), None)
    record = verified.bundle.one("PublicationManifestRecord")
    if len(record.extensions) != 1 or record.extensions[0].get("validation_contract") != PAIRED_MANIFEST_CONTRACT:
        return PublicationManifestResult((ManifestFinding(
            "invalid-verified-paired-manifest", "/manifest", "exact paired Manifest contract required"),), None)
    release_identity = record.semantic["release_ref"]
    fingerprint = record.extensions[0]["payload"]["lifecycle_inventory_digest"]
    try:
        _active(lifecycle_scope, release_identity, fingerprint)
    except Exception:
        return PublicationManifestResult((ManifestFinding(
            "manifest-not-currently-eligible", "/lifecycle", "paired Manifest Release is not currently active"),), None)
    return PublicationManifestResult((), verified)
