"""Fail-closed publication-manifest admission for an exact artifact inventory.

The module is intentionally a leaf boundary.  It reuses persisted semantic
conformance evidence, appends one existing BCRP record kind, and grants no
publication execution or distribution authority.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import stat
import unicodedata
from datetime import datetime
from typing import Any

from .bcrp.canonical import fingerprint_bundle
from .bcrp.model import BCRPBundle, BCRPRecord, Fingerprint, PROFILE_VERSION
from .bcrp.validation import validate_bundle
from .publication_lifecycle import derive_current_state, validate_lifecycle
from .renderer_compatibility_planning import compute_lifecycle_inventory_digest
from .controlled_renderer_invocation import renderer_implementation_digest
from .semantic_artifact_conformance import verify_persisted_semantic_artifact_conformance
from .representative_controlled_invocation import representative_renderer_implementation_digest
from .representative_projection import build_representative_projection
from .representative_semantic_conformance import (
    verify_persisted_representative_semantic_artifact_conformance,
)

_POLICY = "briefforge-publication-manifest-admission-policy:1.0.0"
_PROFILE = "briefforge-publication-manifest-admission-profile:1.0.0"
_PROJECTOR_ID = "authority:briefforge-publication-manifest-projector"
_PROJECTOR_OWNER = "project:BriefForge"
_PROJECTOR_ROLE = "publication-manifest-projector"
_PROJECTOR_SCOPE = "one-publication-manifest-production"
_IMPLEMENTATION = "briefforge.publication_manifest_admission"
_IMPLEMENTATION_VERSION = "1.0.0"
_EXTENSION_CONTRACT = "briefforge:publication-manifest-admission-authority:1.0.0"
_EXCLUSIONS = (
    "distribution-authority", "distribution-execution", "successful-publication-authority",
    "deployment-authority", "atlasforge-authority", "browser-behavior-certification",
    "accessibility-certification", "editorial-certification", "visual-certification",
    "factual-reassessment",
)
_MAX_EVIDENCE = 8 * 1024 * 1024
_ARTIFACT_ROLES = ("primary-semantic-publication",)
_ADMISSION_REQUIREMENTS = (
    "manifest-projector-authority",
    "release-and-current-lifecycle",
    "compatibility-plan-and-capability",
    "controlled-invocation-and-artifact-evidence",
    "semantic-conformance-and-audit-link-closure",
    "artifact-set-identity-and-exact-closure",
    "artifact-role-filename-media-order-and-bytes",
    "manifest-authorization-binding-and-one-act-consumption",
    "predecessor-record-closure-and-immutability",
    "manifest-record-canonicalization-and-specialized-validation",
    "manifest-evidence-persistence-and-external-commitment",
    "distribution-and-successful-publication-authority-separation",
)
_HEX = frozenset("0123456789abcdef")
_PREDECESSOR_KINDS = (
    "PresentationBriefRecord", "PortablePresentationMaterialRecord",
    "CandidatePresentationPackageRecord", "ValidationJudgmentRecord",
    "ReadyPresentationPackageRecord", "PublicationReleaseRecord",
    "RendererCapabilityDeclarationRecord", "RendererCompatibilityPlanRecord",
    "GeneratedArtifactAuditRecord", "SemanticArtifactConformanceRecord",
)
_V1_INVOCATION_CONTRACT = "briefforge:controlled-renderer-invocation-evidence:1.0.0"
_V2_INVOCATION_CONTRACT = "briefforge:representative-controlled-renderer-invocation-evidence:1.0.0"
_V1_CONFORMANCE_CONTRACT = "briefforge:semantic-artifact-conformance-evidence:1.0.0"
_V2_CONFORMANCE_CONTRACT = "briefforge:semantic-artifact-conformance-evidence:2.0.0"


@dataclass(frozen=True)
class ManifestArtifactAdmission:
    identity: str
    role: str
    logical_filename: str
    media_type: str
    byte_length: int
    sha256: str
    order: int
    source_path: str
    release_identity: str
    release_fingerprint: str
    plan_identity: str
    plan_fingerprint: str
    renderer_identity: str
    renderer_version: str
    invocation_authorization_identity: str
    invocation_evidence_fingerprint: str
    conformance_authorization_identity: str
    conformance_evidence_fingerprint: str
    dependency_identities: tuple[str, ...]


@dataclass(frozen=True, order=True)
class ManifestFinding:
    code: str
    location: str
    message: str


@dataclass(frozen=True)
class PublicationManifestAuthorization:
    identity: str
    policy_identity: str
    profile_identity: str
    profile_version: str
    authority_identity: str
    authority_owner: str
    authority_role: str
    authorization_time: str
    release_identity: str
    release_fingerprint: str
    lifecycle_inventory_digest: str
    plan_identity: str
    plan_fingerprint: str
    capability_identity: str
    capability_fingerprint: str
    renderer_identity: str
    renderer_version: str
    renderer_implementation_digest: str
    invocation_authorization_identity: str
    invocation_authorization_fingerprint: str
    invocation_evidence_fingerprint: str
    conformance_authorization_identity: str
    conformance_authorization_fingerprint: str
    conformance_profile_identity: str
    conformance_profile_version: str
    assessor_identity: str
    conformance_evidence_fingerprint: str
    conformance_verdict: str
    predecessor_closure_fingerprint: str
    artifact_inventory: tuple[ManifestArtifactAdmission, ...]
    artifact_set_fingerprint: str
    manifest_identity: str
    manifest_version: str
    manifest_time: str
    projector_implementation: str
    projector_version: str
    evidence_directory: str
    evidence_filename: str
    commitment_ledger_directory: str
    record_identity: str
    exclusions: tuple[str, ...]
    fingerprint: str


_VERIFIED_MARKER = object()


@dataclass(frozen=True, init=False)
class VerifiedPublicationManifest:
    _bundle_document: str
    fingerprint: Fingerprint
    _marker: object

    @classmethod
    def _admitted(cls, document: str, fingerprint: Fingerprint) -> "VerifiedPublicationManifest":
        value = object.__new__(cls)
        object.__setattr__(value, "_bundle_document", document)
        object.__setattr__(value, "fingerprint", fingerprint)
        object.__setattr__(value, "_marker", _VERIFIED_MARKER)
        return value

    @property
    def bundle(self) -> BCRPBundle:
        return _deserialize_bundle(self._bundle_document)


@dataclass(frozen=True)
class PublicationManifestResult:
    findings: tuple[ManifestFinding, ...]
    verified: VerifiedPublicationManifest | None

    @property
    def blocked(self) -> bool:
        return self.verified is None


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _serialize_bundle(bundle: BCRPBundle) -> str:
    return _canonical_bytes({
        "profile_identity": bundle.profile_identity,
        "profile_version": bundle.profile_version,
        "records": [record.to_document() for record in bundle.records],
    }).decode("utf-8")


def _deserialize_bundle(text: str) -> BCRPBundle:
    document = json.loads(text)
    if type(document) is not dict or set(document) != {"profile_identity", "profile_version", "records"} or type(document["records"]) is not list:
        raise ValueError("Manifest evidence envelope is malformed.")
    return BCRPBundle(document["profile_identity"], document["profile_version"],
                      tuple(BCRPRecord.from_document(item) for item in document["records"]))


def _finding(code: str, location: str, message: str) -> ManifestFinding:
    return ManifestFinding(code, location, message)


def _sorted(findings: list[ManifestFinding] | tuple[ManifestFinding, ...]) -> tuple[ManifestFinding, ...]:
    return tuple(sorted(set(findings)))


def _stable_text(value: object) -> bool:
    return type(value) is str and bool(value.strip()) and value == value.strip()


def _digest(value: object) -> bool:
    return type(value) is str and len(value) == 64 and all(character in _HEX for character in value)


def _parse_offset_time(value: object) -> datetime:
    if type(value) is not str or "T" not in value:
        raise ValueError("Time is not an offset timestamp.")
    parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Time has no explicit offset.")
    return parsed


def _offset_time(value: object) -> bool:
    try:
        _parse_offset_time(value)
        return True
    except (TypeError, ValueError, OverflowError):
        return False


def _artifact_document(item: ManifestArtifactAdmission) -> dict[str, Any]:
    document = asdict(item)
    document.pop("source_path", None)
    document["dependency_identities"] = list(item.dependency_identities)
    return document


def compute_artifact_set_fingerprint(inventory: tuple[ManifestArtifactAdmission, ...]) -> str:
    """Bind the ordered governed inventory, excluding only its local source path."""
    if type(inventory) is not tuple or any(type(item) is not ManifestArtifactAdmission for item in inventory):
        raise TypeError("An exact immutable artifact inventory is required.")
    return hashlib.sha256(_canonical_bytes([_artifact_document(item) for item in inventory])).hexdigest()


def compute_manifest_authorization_fingerprint(authorization: PublicationManifestAuthorization) -> str:
    if type(authorization) is not PublicationManifestAuthorization:
        raise TypeError("Exact immutable Manifest authorization is required.")
    document = asdict(authorization)
    document.pop("fingerprint", None)
    return hashlib.sha256(_canonical_bytes(document)).hexdigest()


def _safe_filename(name: object) -> bool:
    return (type(name) is str and bool(name) and name not in {".", ".."}
            and "\x00" not in name and "/" not in name and "\\" not in name
            and not Path(name).is_absolute() and Path(name).name == name)


def _read_regular_path(path: Path, maximum: int = 100_000_000) -> bytes:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_size > maximum:
            raise ValueError("Artifact is not a bounded regular file.")
        chunks: list[bytes] = []
        remaining = info.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1024 * 1024))
            if not chunk:
                raise ValueError("Artifact changed or was truncated while read.")
            chunks.append(chunk)
            remaining -= len(chunk)
        after = os.fstat(descriptor)
        if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) != (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns):
            raise ValueError("Artifact changed while read.")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def validate_artifact_set_closure(
    inventory: tuple[ManifestArtifactAdmission, ...], artifact_paths: tuple[Path, ...]
) -> tuple[ManifestFinding, ...]:
    """Completely reconcile authorization inventory against supplied exact paths."""
    findings: list[ManifestFinding] = []
    if type(inventory) is not tuple or any(type(item) is not ManifestArtifactAdmission for item in inventory):
        return (_finding("invalid-artifact-inventory", "/artifacts", "Exact immutable artifact admissions are required."),)
    if type(artifact_paths) is not tuple:
        return (_finding("invalid-artifact-paths", "/artifact-paths", "Exact ordered artifact paths are required."),)
    if len(inventory) > len(artifact_paths):
        findings.append(_finding("artifact-omitted", "/artifact-paths", "One or more authorized artifacts are omitted."))
    if len(artifact_paths) > len(inventory):
        findings.append(_finding("unexpected-artifact", "/artifact-paths", "One or more supplied artifacts are not authorized."))

    fields = (("identity", "duplicate-artifact-identity"), ("role", "duplicate-artifact-role"),
              ("logical_filename", "duplicate-artifact-filename"), ("order", "duplicate-artifact-order"))
    for field, code in fields:
        counts = Counter(getattr(item, field) for item in inventory)
        if any(count > 1 for count in counts.values()):
            findings.append(_finding(code, f"/artifacts/{field}", f"Artifact {field} is duplicated."))
    by_identity: dict[str, set[str]] = {}
    for item in inventory:
        by_identity.setdefault(item.identity, set()).add(item.role)
    if any(len(roles) > 1 for roles in by_identity.values()):
        findings.append(_finding("conflicting-artifact-role", "/artifacts/role", "One artifact identity has conflicting roles."))
    normalized = [unicodedata.normalize("NFC", item.logical_filename).casefold() for item in inventory
                  if type(item.logical_filename) is str]
    if len(normalized) != len(set(normalized)):
        findings.append(_finding("artifact-filename-collision", "/artifacts/logical_filename", "Artifact filenames collide under portable Unicode/case normalization."))
    for index, item in enumerate(inventory):
        location = f"/artifacts/{index}"
        if not _safe_filename(item.logical_filename):
            findings.append(_finding("unsafe-artifact-filename", location + "/logical_filename", "Artifact filename is not one safe portable basename."))
        if type(item.order) is not int or item.order != index:
            findings.append(_finding("artifact-order-mismatch", location + "/order", "Artifact order is not exact contiguous encounter order."))
        if type(item.dependency_identities) is not tuple or any(type(value) is not str for value in item.dependency_identities):
            findings.append(_finding("invalid-artifact-binding", location + "/dependency_identities", "Artifact dependency inventory is malformed."))
        if index >= len(artifact_paths):
            continue
        try:
            path = Path(artifact_paths[index])
            expected = Path(item.source_path)
            if (not path.is_absolute() or str(path.resolve()) != str(path)
                    or not expected.is_absolute() or str(expected.resolve()) != item.source_path):
                raise ValueError("Artifact path is not canonical absolute input.")
            if path != expected:
                findings.append(_finding("artifact-order-mismatch", f"/artifact-paths/{index}", "Supplied artifact path differs from authorized order/path."))
            data = _read_regular_path(path)
            if len(data) != item.byte_length:
                findings.append(_finding("artifact-length-mismatch", location + "/byte_length", "Artifact byte length differs from authorization."))
            if hashlib.sha256(data).hexdigest() != item.sha256:
                findings.append(_finding("artifact-digest-mismatch", location + "/sha256", "Artifact digest differs from authorization."))
            if path.name != item.logical_filename:
                findings.append(_finding("artifact-filename-mismatch", location + "/logical_filename", "Artifact basename differs from authorization."))
        except Exception:
            findings.append(_finding("artifact-unreadable", f"/artifact-paths/{index}", "Artifact path is absent, unsafe, non-canonical, unreadable, or changed during inspection."))
    return _sorted(findings)


def _lifecycle_current(lifecycle_scope: Any, release_identity: str) -> bool:
    if getattr(lifecycle_scope, "inventory_complete", None) is not True:
        return False
    if compute_lifecycle_inventory_digest(lifecycle_scope) != lifecycle_scope.inventory_digest:
        return False
    validation = validate_lifecycle(lifecycle_scope.bundle, lifecycle_scope.releases, lifecycle_scope.policies)
    if validation.findings:
        return False
    state = derive_current_state(lifecycle_scope.bundle, lifecycle_scope.releases, lifecycle_scope.policies)
    return state.current_release_identity == release_identity and dict(state.release_states).get(release_identity) == "current"


def _authorization_findings(authorization: PublicationManifestAuthorization, *, persisted: Any,
                            verified_release: Any, lifecycle_scope: Any, declaration: Any,
                            planning_authorization: Any, verified_plan: Any, invocation_authorization: Any,
                            conformance_authorization: Any,
                            artifact_paths: tuple[Path, ...]) -> tuple[ManifestFinding, ...]:
    if type(authorization) is not PublicationManifestAuthorization:
        return (_finding("missing-manifest-authorization", "/authorization", "Exact immutable Manifest authorization is required."),)
    findings: list[ManifestFinding] = []
    for name in (
        "identity", "policy_identity", "profile_identity", "profile_version", "authority_identity",
        "authority_owner", "authority_role", "release_identity", "plan_identity", "capability_identity",
        "renderer_identity", "renderer_version", "invocation_authorization_identity",
        "conformance_authorization_identity", "conformance_profile_identity", "conformance_profile_version",
        "assessor_identity", "manifest_identity", "manifest_version", "projector_implementation",
        "projector_version", "record_identity",
    ):
        if not _stable_text(getattr(authorization, name, None)):
            findings.append(_finding("invalid-manifest-authorization-field", f"/authorization/{name}", "Manifest authorization field requires one nonempty stable string."))
    for name in (
        "release_fingerprint", "lifecycle_inventory_digest", "plan_fingerprint", "capability_fingerprint",
        "renderer_implementation_digest", "invocation_authorization_fingerprint", "invocation_evidence_fingerprint",
        "conformance_authorization_fingerprint", "conformance_evidence_fingerprint",
        "predecessor_closure_fingerprint", "artifact_set_fingerprint", "fingerprint",
    ):
        if not _digest(getattr(authorization, name, None)):
            findings.append(_finding("invalid-manifest-digest", f"/authorization/{name}", "Manifest digest requires exactly 64 lowercase hexadecimal characters."))
    for name in ("authorization_time", "manifest_time"):
        if not _offset_time(getattr(authorization, name, None)):
            findings.append(_finding("invalid-manifest-time", f"/authorization/{name}", "Manifest time requires RFC3339/ISO-8601 with an explicit offset."))
    try:
        predecessor_times = (
            _parse_offset_time(verified_release.release.semantic["publication_time"]),
            _parse_offset_time(declaration.declaration_time),
            _parse_offset_time(planning_authorization.planning_time),
            _parse_offset_time(invocation_authorization.authorization_time),
            _parse_offset_time(conformance_authorization.authorization_time),
        )
        authorization_time = _parse_offset_time(authorization.authorization_time)
        manifest_time = _parse_offset_time(authorization.manifest_time)
        if max(predecessor_times) > authorization_time or authorization_time > manifest_time:
            findings.append(_finding(
                "manifest-authorization-chronology-invalid", "/authorization/authorization_time",
                "Manifest authorization must follow every bound predecessor act and must not follow Manifest creation.",
            ))
    except (AttributeError, TypeError, ValueError, OverflowError):
        findings.append(_finding(
            "manifest-authorization-chronology-invalid", "/authorization/authorization_time",
            "Manifest authorization chronology cannot be independently established.",
        ))
    if (authorization.manifest_identity == authorization.identity
            or authorization.record_identity == authorization.identity
            or authorization.record_identity == authorization.manifest_identity):
        findings.append(_finding("manifest-identity-conflict", "/authorization/manifest_identity", "Authorization, Manifest, and record identities must be distinct."))
    inventory = authorization.artifact_inventory if type(authorization.artifact_inventory) is tuple else ()
    if len(inventory) != 1:
        findings.append(_finding("production-artifact-count-mismatch", "/artifacts", "Production requires exactly one artifact proven by the controlled-invocation and semantic-conformance chain."))
    expected = {
        "policy_identity": _POLICY, "profile_identity": _PROFILE, "profile_version": "1.0.0",
        "authority_identity": _PROJECTOR_ID, "authority_owner": _PROJECTOR_OWNER,
        "authority_role": _PROJECTOR_ROLE,
        "release_identity": verified_release.release.identity,
        "release_fingerprint": verified_release.fingerprint.digest,
        "lifecycle_inventory_digest": lifecycle_scope.inventory_digest,
        "plan_identity": verified_plan.plan.identity, "plan_fingerprint": verified_plan.fingerprint.digest,
        "capability_identity": declaration.identity, "capability_fingerprint": declaration.fingerprint,
        "renderer_identity": invocation_authorization.renderer_identity,
        "renderer_version": invocation_authorization.renderer_version,
        "renderer_implementation_digest": invocation_authorization.renderer_implementation_digest,
        "invocation_authorization_identity": invocation_authorization.identity,
        "invocation_authorization_fingerprint": invocation_authorization.fingerprint,
        "conformance_authorization_identity": conformance_authorization.identity,
        "conformance_authorization_fingerprint": conformance_authorization.fingerprint,
        "conformance_profile_identity": conformance_authorization.profile_identity,
        "conformance_profile_version": conformance_authorization.profile_version,
        "assessor_identity": conformance_authorization.assessor_identity,
        "conformance_evidence_fingerprint": persisted.fingerprint.digest,
        "predecessor_closure_fingerprint": fingerprint_bundle(
            persisted.bundle, domain="profile-instance", require_valid=False
        ).digest,
        "projector_implementation": _IMPLEMENTATION, "projector_version": _IMPLEMENTATION_VERSION,
        "exclusions": _EXCLUSIONS,
    }
    try:
        expected["artifact_set_fingerprint"] = compute_artifact_set_fingerprint(inventory)
    except (TypeError, ValueError):
        findings.append(_finding("invalid-artifact-inventory", "/artifacts", "Artifact inventory cannot be canonically fingerprinted."))
    # This evidence fingerprint is independently established by the persisted verifier.
    invocation_fp = persisted.bundle.one("SemanticArtifactConformanceRecord").extensions[0]["payload"].get("invocation_evidence_fingerprint")
    expected["invocation_evidence_fingerprint"] = invocation_fp
    for name, value in expected.items():
        if getattr(authorization, name, None) != value:
            findings.append(_finding("manifest-authorization-binding-mismatch", f"/authorization/{name}", f"Manifest authorization binds stale or different {name}."))
    if authorization.conformance_verdict != "approved":
        findings.append(_finding("unsupported-conformance-status", "/authorization/conformance_verdict", "Only the exact approved conformance verdict is supported."))
    try:
        computed_fingerprint = compute_manifest_authorization_fingerprint(authorization)
    except (TypeError, ValueError):
        computed_fingerprint = None
    if authorization.fingerprint != computed_fingerprint:
        findings.append(_finding("manifest-authorization-fingerprint-mismatch", "/authorization/fingerprint", "Manifest authorization fingerprint is stale or malformed."))
    authorities = verified_release.bundle.one("PortablePresentationMaterialRecord").semantic.get("authorities", [])
    projector = {"id": _PROJECTOR_ID, "owner_identity": _PROJECTOR_OWNER, "role": _PROJECTOR_ROLE, "scope": _PROJECTOR_SCOPE}
    if [item for item in authorities if item.get("id") == _PROJECTOR_ID] != [projector]:
        findings.append(_finding("unreleased-manifest-projector-authority", "/release/authorities", "Verified released material lacks exactly one accepted Manifest projector authority."))
    if not _lifecycle_current(lifecycle_scope, authorization.release_identity):
        findings.append(_finding("manifest-release-not-current", "/lifecycle", "Manifest production requires one complete current Release lifecycle."))
    if len(persisted.bundle.records) != 10 or persisted.bundle.records[-1].kind != "SemanticArtifactConformanceRecord":
        findings.append(_finding("invalid-predecessor-closure", "/predecessor", "Manifest requires the exact ten-record conformance profile."))
    if authorization.record_identity in persisted.bundle.by_identity():
        findings.append(_finding("manifest-record-identity-conflict", "/authorization/record_identity", "Manifest record identity conflicts with predecessor closure."))
    if authorization.evidence_filename != "publication-manifest.json":
        findings.append(_finding("unauthorized-manifest-filename", "/authorization/evidence_filename", "Manifest evidence filename differs from policy."))
    for label, text in (("evidence_directory", authorization.evidence_directory),
                        ("commitment_ledger_directory", authorization.commitment_ledger_directory)):
        try:
            path = Path(text)
            if not path.is_absolute() or str(path.resolve()) != text or path.is_symlink():
                raise ValueError
            if label == "evidence_directory" and not path.is_dir():
                raise ValueError
            if label == "commitment_ledger_directory" and path.exists() and not path.is_dir():
                raise ValueError
        except Exception:
            findings.append(_finding("invalid-manifest-persistence-boundary", f"/authorization/{label}", "Manifest persistence boundary is absent, non-canonical, or unsafe."))
    findings.extend(validate_artifact_set_closure(inventory, artifact_paths))
    audit = persisted.bundle.one("GeneratedArtifactAuditRecord")
    audit_artifact = audit.semantic.get("artifact", {})
    audit_payload = audit.extensions[0].get("payload", {})
    conformance_record = persisted.bundle.one("SemanticArtifactConformanceRecord")
    conformance_payload = conformance_record.extensions[0].get("payload", {})
    output_directory = audit_payload.get("output_directory")
    governed_source = ""
    if conformance_record.extensions[0].get("validation_contract") == _V2_CONFORMANCE_CONTRACT:
        governed_source = getattr(conformance_authorization, "artifact_destination", "")
    elif type(output_directory) is str and type(audit_artifact.get("filename")) is str:
        governed_source = str((Path(output_directory) / audit_artifact["filename"]).resolve())
    governed = {
        "identity": audit_artifact.get("id"), "logical_filename": audit_artifact.get("filename"),
        "media_type": audit_artifact.get("media_type"), "byte_length": audit_artifact.get("byte_length"),
        "sha256": audit_artifact.get("sha256"), "source_path": governed_source,
        "release_identity": audit.semantic.get("release_ref"), "release_fingerprint": authorization.release_fingerprint,
        "plan_identity": audit.semantic.get("plan_ref"), "plan_fingerprint": audit_payload.get("plan_fingerprint"),
        "renderer_identity": audit_payload.get("renderer_identity"), "renderer_version": audit_payload.get("renderer_version"),
        "invocation_authorization_identity": audit_payload.get("authorization_identity"),
        "invocation_evidence_fingerprint": conformance_payload.get("invocation_evidence_fingerprint"),
        "conformance_authorization_identity": conformance_payload.get("authorization_identity"),
        "conformance_evidence_fingerprint": persisted.fingerprint.digest,
    }
    for index, item in enumerate(inventory):
        if type(item) is not ManifestArtifactAdmission:
            continue
        if item.role not in _ARTIFACT_ROLES:
            findings.append(_finding("unauthorized-artifact-role", f"/artifacts/{index}/role", "Artifact role is outside the governed production allowlist."))
        if item.dependency_identities != ():
            findings.append(_finding("unauthorized-artifact-dependencies", f"/artifacts/{index}/dependency_identities", "Production artifact dependencies must be the exact empty tuple."))
        for name, value in governed.items():
            if getattr(item, name, None) != value:
                findings.append(_finding("artifact-governed-evidence-mismatch", f"/artifacts/{index}/{name}", f"Artifact {name} differs from persisted governed evidence."))
        bindings = {
            "release_identity": authorization.release_identity, "release_fingerprint": authorization.release_fingerprint,
            "plan_identity": authorization.plan_identity, "plan_fingerprint": authorization.plan_fingerprint,
            "renderer_identity": authorization.renderer_identity, "renderer_version": authorization.renderer_version,
            "invocation_authorization_identity": authorization.invocation_authorization_identity,
            "invocation_evidence_fingerprint": authorization.invocation_evidence_fingerprint,
            "conformance_authorization_identity": authorization.conformance_authorization_identity,
            "conformance_evidence_fingerprint": authorization.conformance_evidence_fingerprint,
        }
        for name, value in bindings.items():
            if getattr(item, name) != value:
                findings.append(_finding("artifact-authority-binding-mismatch", f"/artifacts/{index}/{name}", f"Artifact binds stale or different {name}."))
    return _sorted(findings)


def _manifest_record(predecessor: BCRPBundle, authorization: PublicationManifestAuthorization) -> BCRPRecord:
    audit = predecessor.one("GeneratedArtifactAuditRecord")
    conformance = predecessor.one("SemanticArtifactConformanceRecord")
    release = predecessor.one("PublicationReleaseRecord")
    artifact_documents = [_artifact_document(item) for item in authorization.artifact_inventory]
    conformance_payload = conformance.extensions[0]["payload"]
    semantic_requirement_outcomes = [
        {"requirement_id": item["id"], "outcome": item["outcome"]}
        for item in conformance_payload["requirement_accounting"]["expected_requirements"]
    ]
    admission_outcomes = [
        {"requirement_id": requirement, "outcome": "conformant"}
        for requirement in _ADMISSION_REQUIREMENTS
    ]
    authority_audit_links = [
        {"role": "manifest-to-release", "source_identity": authorization.record_identity,
         "target_identity": release.identity},
        {"role": "manifest-to-generated-artifact-audit", "source_identity": authorization.record_identity,
         "target_identity": audit.identity},
        {"role": "manifest-to-semantic-conformance", "source_identity": authorization.record_identity,
         "target_identity": conformance.identity},
        {"role": "manifest-to-compatibility-plan", "source_identity": authorization.record_identity,
         "target_identity": predecessor.one("RendererCompatibilityPlanRecord").identity},
        {"role": "manifest-to-capability-declaration", "source_identity": authorization.record_identity,
         "target_identity": predecessor.one("RendererCapabilityDeclarationRecord").identity},
        {"role": "manifest-to-admitted-artifact", "source_identity": authorization.record_identity,
         "target_identity": authorization.artifact_inventory[0].identity},
    ]
    catalog = [{
        "artifact_identity": item.identity, "role": item.role, "order": item.order,
        "logical_filename": item.logical_filename, "media_type": item.media_type,
        "byte_length": item.byte_length, "sha256": item.sha256,
    } for item in authorization.artifact_inventory]
    payload = {
        "contract_identity": _EXTENSION_CONTRACT,
        "policy_identity": authorization.policy_identity,
        "profile_identity": authorization.profile_identity,
        "profile_version": authorization.profile_version,
        "authorization_identity": authorization.identity,
        "authorization_fingerprint": authorization.fingerprint,
        "manifest_identity": authorization.manifest_identity,
        "manifest_version": authorization.manifest_version,
        "manifest_time": authorization.manifest_time,
        "projector_implementation": authorization.projector_implementation,
        "projector_version": authorization.projector_version,
        "release_fingerprint": authorization.release_fingerprint,
        "lifecycle_inventory_digest": authorization.lifecycle_inventory_digest,
        "predecessor_closure_fingerprint": authorization.predecessor_closure_fingerprint,
        "artifact_set_fingerprint": authorization.artifact_set_fingerprint,
        "artifact_inventory": artifact_documents,
        "semantic_requirement_outcomes": semantic_requirement_outcomes,
        "admission_requirement_ids": list(_ADMISSION_REQUIREMENTS),
        "admission_requirement_outcomes": admission_outcomes,
        "authority_audit_links": authority_audit_links,
        "aggregate_manifest_verdict": "approved",
        "verification_status": "verified",
        "authority_exclusions": list(authorization.exclusions),
        "distribution_authority": "absent", "distribution_execution": "not-performed",
        "successful_publication": "not-asserted", "deployment_authority": "absent",
        "atlasforge_authority": "absent",
    }
    return BCRPRecord(
        kind="PublicationManifestRecord", identity=authorization.record_identity, profile_version=PROFILE_VERSION,
        semantic={
            "release_ref": release.identity, "lifecycle_status": release.semantic["lifecycle_status"],
            "artifact_audit_refs": [audit.identity], "conformance_refs": [conformance.identity],
            "artifact_ids": [item.identity for item in authorization.artifact_inventory],
            "manifest_identity": authorization.manifest_identity,
            "manifest_version": authorization.manifest_version,
            "policy_identity": authorization.policy_identity,
            "profile_identity": authorization.profile_identity,
            "profile_version": authorization.profile_version,
            "authorization_time": authorization.authorization_time,
            "manifest_time": authorization.manifest_time,
            "artifact_catalog": catalog,
        },
        extensions=[{
            "owner_namespace": "briefforge-publication-manifest-admission", "name": "exact-artifact-admission",
            "version": "1.0.0", "authority_ref": authorization.authority_identity,
            "scope": "publication-manifest-admission-only",
            "target_refs": [release.identity, audit.identity, conformance.identity] + [item.identity for item in authorization.artifact_inventory],
            "criticality": "required", "character": "semantic", "validation_contract": _EXTENSION_CONTRACT,
            "preservation": "must-preserve", "payload": payload,
        }],
    )


def _verify_bundle(bundle: BCRPBundle, predecessor: BCRPBundle,
                   authorization: PublicationManifestAuthorization) -> VerifiedPublicationManifest:
    if len(bundle.records) != 11 or len(bundle.records_of_kind("PublicationManifestRecord")) != 1:
        raise ValueError("Manifest closure requires the exact ten-record predecessor and one Manifest record.")
    if tuple(record.to_document() for record in bundle.records[:10]) != tuple(record.to_document() for record in predecessor.records):
        raise ValueError("Manifest does not preserve exact predecessor evidence.")
    expected_record = _manifest_record(predecessor, authorization).to_document()
    actual_record = bundle.records[-1].to_document()
    if actual_record != expected_record:
        differing = sorted(key for key in set(actual_record) | set(expected_record)
                           if actual_record.get(key) != expected_record.get(key))
        raise ValueError(f"Manifest record differs from independently reproduced admission evidence: {differing}; actual={actual_record.get('extensions')!r}; expected={expected_record.get('extensions')!r}.")
    audit_contract = predecessor.one("GeneratedArtifactAuditRecord").extensions[0].get("validation_contract")
    conformance_contract = predecessor.one("SemanticArtifactConformanceRecord").extensions[0].get("validation_contract")
    if (audit_contract, conformance_contract) not in {
        (_V1_INVOCATION_CONTRACT, _V1_CONFORMANCE_CONTRACT),
        (_V2_INVOCATION_CONTRACT, _V2_CONFORMANCE_CONTRACT),
    }:
        raise ValueError("Manifest predecessor contract pair is not allowlisted.")
    generic_bundle = bundle
    if conformance_contract == _V2_CONFORMANCE_CONTRACT:
        # Isolate generic-envelope validation from the authoritative predecessor;
        # BCRPRecord.to_document does not deep-copy nested extension payloads.
        documents = json.loads(json.dumps(
            [record.to_document() for record in bundle.records],
            ensure_ascii=False, allow_nan=False))
        documents[9]["extensions"][0]["payload"] = {}
        generic_bundle = BCRPBundle(bundle.profile_identity, bundle.profile_version,
                                    tuple(BCRPRecord.from_document(item) for item in documents))
    generic = validate_bundle(generic_bundle, through_layer="L6")
    contracts = {
        "ValidationJudgmentRecord": "briefforge:legacy-lifecycle-compatibility:1.0.0",
        "ReadyPresentationPackageRecord": "briefforge:legacy-lifecycle-compatibility:1.0.0",
        "PublicationReleaseRecord": "briefforge:publication-release-authorization:1.0.0",
        "RendererCapabilityDeclarationRecord": "briefforge:renderer-capability-declaration:1.0.0",
        "RendererCompatibilityPlanRecord": "briefforge:renderer-compatibility-plan:1.0.0",
        "GeneratedArtifactAuditRecord": audit_contract,
        "SemanticArtifactConformanceRecord": conformance_contract,
        "PublicationManifestRecord": _EXTENSION_CONTRACT,
    }
    allowed = {record.identity for record in bundle.records if record.kind in contracts
               and len(record.extensions) == 1
               and record.extensions[0].get("criticality") == "required"
               and record.extensions[0].get("preservation") == "must-preserve"
               and record.extensions[0].get("validation_contract") == contracts[record.kind]}
    conformance_identity = predecessor.one("SemanticArtifactConformanceRecord").identity
    unexpected = [item for item in generic.findings if not (
        (item.layer == "L1" and item.family == "extension-boundary" and item.severity == "blocking"
         and item.blocking_consequence == "all dependent processing" and item.semantic_identity in allowed
         and item.location == "/extensions/0"
         and item.message == "Unknown required semantic extension cannot be processed."
         and item.referenced_identities == ())
    )]
    if unexpected:
        raise ValueError("Manifest closure fails generic BCRP validation: " + "; ".join(
            f"{item.semantic_identity}{item.location}:{item.message}" for item in unexpected))
    fingerprint = fingerprint_bundle(bundle, domain="profile-instance", require_valid=False)
    return VerifiedPublicationManifest._admitted(_serialize_bundle(bundle), fingerprint)


def _open_directory(path: Path) -> tuple[int, tuple[int, int]]:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    info = os.fstat(descriptor)
    if not stat.S_ISDIR(info.st_mode):
        os.close(descriptor); raise ValueError("Persistence path is not a directory.")
    return descriptor, (info.st_dev, info.st_ino)


def _write_exclusive(directory_fd: int, name: str, content: bytes) -> None:
    if not _safe_filename(name):
        raise ValueError("Persistence filename is unsafe.")
    descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=directory_fd)
    try:
        view = memoryview(content)
        while view:
            written = os.write(descriptor, view)
            if written <= 0: raise OSError("Short write made no progress.")
            view = view[written:]
        os.fsync(descriptor)
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_size != len(content):
            raise ValueError("Persisted object is not one complete regular file.")
    except BaseException:
        try: os.unlink(name, dir_fd=directory_fd); os.fsync(directory_fd)
        except OSError: pass
        raise
    finally:
        os.close(descriptor)


def _read_regular(directory_fd: int, name: str, maximum: int) -> bytes:
    descriptor = os.open(name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory_fd)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_size > maximum: raise ValueError("Persisted object is unsafe or oversized.")
        data = bytearray()
        while len(data) < info.st_size:
            chunk = os.read(descriptor, info.st_size - len(data))
            if not chunk: raise ValueError("Persisted object was truncated.")
            data.extend(chunk)
        return bytes(data)
    finally: os.close(descriptor)


def _consumption_name(authorization: PublicationManifestAuthorization) -> str:
    # The filename is independently keyed by governed authorization identity;
    # its content binds the particular fingerprint presented for that identity.
    identity_key = hashlib.sha256(authorization.identity.encode("utf-8")).hexdigest()
    return identity_key + ".manifest-authorization-identity-consumed"


def _commitment_name(authorization: PublicationManifestAuthorization) -> str:
    return authorization.fingerprint + ".publication-manifest-admitted"


def _consumption_bytes(authorization: PublicationManifestAuthorization) -> bytes:
    return _canonical_bytes({"contract_identity": "briefforge:publication-manifest-consumption:1.0.0",
                             "authorization_identity": authorization.identity,
                             "authorization_fingerprint": authorization.fingerprint,
                             "artifact_set_fingerprint": authorization.artifact_set_fingerprint,
                             "predecessor_closure_fingerprint": authorization.predecessor_closure_fingerprint,
                             "scope": "exactly-one-publication-manifest-act"})


def _commitment_bytes(authorization: PublicationManifestAuthorization, evidence: bytes) -> bytes:
    return _canonical_bytes({"contract_identity": "briefforge:publication-manifest-admission-commitment:1.0.0",
                             "authorization_fingerprint": authorization.fingerprint,
                             "artifact_set_fingerprint": authorization.artifact_set_fingerprint,
                             "predecessor_closure_fingerprint": authorization.predecessor_closure_fingerprint,
                             "manifest_evidence_sha256": hashlib.sha256(evidence).hexdigest(),
                             "manifest_evidence_byte_length": len(evidence)})


def _reserve_authorization(authorization: PublicationManifestAuthorization) -> None:
    ledger = Path(authorization.commitment_ledger_directory)
    try:
        ledger.mkdir(mode=0o700)
    except FileExistsError:
        pass
    fd, identity = _open_directory(ledger)
    try:
        _write_exclusive(fd, _consumption_name(authorization), _consumption_bytes(authorization))
        os.fsync(fd)
        info = os.fstat(fd)
        if (info.st_dev, info.st_ino) != identity: raise ValueError("Ledger identity changed during reservation.")
    finally: os.close(fd)


def _persist_manifest_transaction(authorization: PublicationManifestAuthorization, evidence: bytes) -> None:
    """Persist evidence, then commitment; roll evidence back before commitment on failure."""
    evidence_fd, evidence_identity = _open_directory(Path(authorization.evidence_directory))
    ledger_fd, ledger_identity = _open_directory(Path(authorization.commitment_ledger_directory))
    evidence_created = commitment_created = False
    try:
        _write_exclusive(evidence_fd, authorization.evidence_filename, evidence); evidence_created = True
        os.fsync(evidence_fd)
        try:
            _write_exclusive(ledger_fd, _commitment_name(authorization), _commitment_bytes(authorization, evidence)); commitment_created = True
            os.fsync(ledger_fd)
        except BaseException:
            os.unlink(authorization.evidence_filename, dir_fd=evidence_fd); os.fsync(evidence_fd); evidence_created = False
            raise
        ei, li = os.fstat(evidence_fd), os.fstat(ledger_fd)
        if (ei.st_dev, ei.st_ino) != evidence_identity or (li.st_dev, li.st_ino) != ledger_identity:
            raise ValueError("Authorized directory identity changed during persistence.")
    except BaseException:
        if commitment_created:
            try: os.unlink(_commitment_name(authorization), dir_fd=ledger_fd); os.fsync(ledger_fd)
            except OSError: pass
        if evidence_created:
            try: os.unlink(authorization.evidence_filename, dir_fd=evidence_fd); os.fsync(evidence_fd)
            except OSError: pass
        raise
    finally:
        os.close(evidence_fd); os.close(ledger_fd)


def _dispatch_profile(*, conformance_evidence_path: Path, invocation_authorization: Any,
                      conformance_authorization: Any) -> str:
    """Select one fixed verifier solely from an exact, untrusted closure tuple.

    This deliberately does not ask either verifier to identify its own input.
    Consequently malformed, mixed, or merely caller-claimed profiles cannot
    enter either verifier boundary.
    """
    expected_path = (Path(conformance_authorization.evidence_directory) /
                     conformance_authorization.evidence_filename)
    if Path(conformance_evidence_path) != expected_path:
        raise ValueError("Conformance evidence path differs from its authorization.")
    raw = _read_regular_path(Path(conformance_evidence_path), _MAX_EVIDENCE)
    try:
        closure = _deserialize_bundle(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise ValueError("Conformance evidence is not one parseable ten-record closure.") from exc
    if (len(closure.records) != 10
            or tuple(record.kind for record in closure.records) != _PREDECESSOR_KINDS):
        raise ValueError("Conformance evidence has an unsupported record topology.")
    audit, conformance = closure.records[8], closure.records[9]
    if len(audit.extensions) != 1 or len(conformance.extensions) != 1:
        raise ValueError("Dispatch records require exactly one extension each.")
    audit_extension, conformance_extension = audit.extensions[0], conformance.extensions[0]
    if type(audit_extension) is not dict or type(conformance_extension) is not dict:
        raise ValueError("Dispatch extensions are malformed.")
    audit_payload = audit_extension.get("payload")
    conformance_payload = conformance_extension.get("payload")
    assessor = conformance_payload.get("assessor") if type(conformance_payload) is dict else None
    evidence_summary = conformance.semantic.get("evidence") if type(conformance.semantic) is dict else None
    if (type(audit_payload) is not dict or type(conformance_payload) is not dict
            or type(assessor) is not dict or set(assessor) != {"identity", "owner", "role"}
            or type(evidence_summary) is not dict
            or set(conformance.semantic) != {"audit_ref", "ready_ref", "audit_link_pass",
                                              "semantic_pass", "evidence"}
            or set(evidence_summary) != {"profile", "aggregate_verdict", "requirement_count",
                                         "evidence_sha256"}
            or conformance.semantic.get("audit_link_pass") is not True
            or conformance.semantic.get("semantic_pass") is not True
            or evidence_summary.get("aggregate_verdict") != "approved"):
        raise ValueError("Conformance dispatch topology or verdict is malformed.")

    dispatch_tuple = (
        audit_extension.get("validation_contract"), audit_payload.get("contract_identity"),
        audit_payload.get("renderer_identity"), audit_payload.get("renderer_adapter_id"),
        audit_payload.get("renderer_version"), audit_payload.get("renderer_implementation_digest"),
        conformance_extension.get("validation_contract"), conformance_payload.get("contract_identity"),
        conformance_payload.get("profile_identity"), conformance_payload.get("profile_version"),
        assessor.get("identity"), evidence_summary.get("profile"),
        getattr(invocation_authorization, "renderer_identity", None),
        getattr(invocation_authorization, "renderer_adapter_id", None),
        getattr(invocation_authorization, "renderer_version", None),
        getattr(invocation_authorization, "renderer_implementation_digest", None),
        getattr(conformance_authorization, "profile_identity", None),
        getattr(conformance_authorization, "profile_version", None),
        getattr(conformance_authorization, "assessor_identity", None),
        getattr(conformance_authorization, "assessor_implementation", None),
        getattr(conformance_authorization, "assessor_version", None),
    )
    common_assessor = "authority:briefforge-semantic-artifact-conformance"
    v1 = (
        _V1_INVOCATION_CONTRACT, _V1_INVOCATION_CONTRACT,
        "renderer:minimal-html", "minimal-html-renderer", "0.2.0",
        renderer_implementation_digest(),
        _V1_CONFORMANCE_CONTRACT, _V1_CONFORMANCE_CONTRACT,
        "briefforge-static-html-semantic-realization-profile", "1.0.0",
        common_assessor, "briefforge-static-html-semantic-realization-profile:1.0.0",
        "renderer:minimal-html", "minimal-html-renderer", "0.2.0",
        renderer_implementation_digest(),
        "briefforge-static-html-semantic-realization-profile", "1.0.0", common_assessor,
        "briefforge.semantic_artifact_conformance", "1.0.0",
    )
    v2 = (
        _V2_INVOCATION_CONTRACT, _V2_INVOCATION_CONTRACT,
        "renderer:representative-static-html", "representative-static-html-renderer", "1.0.0",
        representative_renderer_implementation_digest(),
        _V2_CONFORMANCE_CONTRACT, _V2_CONFORMANCE_CONTRACT,
        "briefforge-static-html-semantic-realization-profile:2.0.0", "2.0.0",
        common_assessor, "briefforge-static-html-semantic-realization-profile:2.0.0",
        "renderer:representative-static-html", "representative-static-html-renderer", "1.0.0",
        representative_renderer_implementation_digest(),
        "briefforge-static-html-semantic-realization-profile:2.0.0", "2.0.0", common_assessor,
        "briefforge.representative_semantic_artifact_conformance", "2.0.0",
    )
    if dispatch_tuple == v1:
        return "v1"
    if dispatch_tuple == v2:
        return "v2"
    raise ValueError("Conformance evidence and authorization tuple is not allowlisted.")


def _persisted_conformance(*, artifact_path: Path, invocation_evidence_path: Path,
                           conformance_evidence_path: Path, evidence_snapshot: Any,
                           verified_release: Any, lifecycle_scope: Any, declaration: Any,
                           planning_authorization: Any, verified_plan: Any,
                           invocation_authorization: Any, conformance_authorization: Any) -> Any:
    profile = _dispatch_profile(
        conformance_evidence_path=conformance_evidence_path,
        invocation_authorization=invocation_authorization,
        conformance_authorization=conformance_authorization,
    )
    common = dict(
        artifact_path=artifact_path, invocation_evidence_path=invocation_evidence_path,
        evidence_snapshot=evidence_snapshot, verified_release=verified_release,
        lifecycle_scope=lifecycle_scope, declaration=declaration,
        planning_authorization=planning_authorization, verified_plan=verified_plan,
        invocation_authorization=invocation_authorization, authorization=conformance_authorization,
    )
    if profile == "v1":
        return verify_persisted_semantic_artifact_conformance(
            conformance_evidence_path=conformance_evidence_path, **common)
    # The assessor deliberately does not import the projection builder.  This
    # orchestration boundary reproduces the governed projection from the
    # independently reverified Release/Plan inputs and supplies it for exact
    # authority traversal during persisted conformance verification.
    projection = build_representative_projection(
        verified_release=verified_release, evidence_snapshot=evidence_snapshot,
        lifecycle_scope=lifecycle_scope, declaration=declaration,
        planning_authorization=planning_authorization, verified_plan=verified_plan,
    )
    return verify_persisted_representative_semantic_artifact_conformance(
        projection=projection, **common)


def _independent_failure_findings(authorization: object, artifact_path: object) -> list[ManifestFinding]:
    findings: list[ManifestFinding] = []
    if type(authorization) is not PublicationManifestAuthorization:
        return [_finding("missing-manifest-authorization", "/authorization", "Exact immutable Manifest authorization is required.")]
    for name, expected in (("policy_identity", _POLICY), ("profile_identity", _PROFILE),
                           ("profile_version", "1.0.0"), ("authority_role", _PROJECTOR_ROLE)):
        if getattr(authorization, name, None) != expected:
            findings.append(_finding("manifest-authorization-binding-mismatch", f"/authorization/{name}", f"Manifest authorization binds stale or different {name}."))
    inventory = authorization.artifact_inventory if type(authorization.artifact_inventory) is tuple else ()
    if len(inventory) != 1:
        findings.append(_finding("production-artifact-count-mismatch", "/artifacts", "Production requires exactly one artifact proven by the controlled-invocation and semantic-conformance chain."))
    try:
        findings.extend(validate_artifact_set_closure(inventory, (Path(artifact_path),)))
    except Exception:
        findings.append(_finding("invalid-artifact-paths", "/artifact-paths", "Artifact path input is malformed."))
    return findings


def produce_publication_manifest(*, evidence_snapshot: Any, verified_release: Any, lifecycle_scope: Any,
                                 declaration: Any, planning_authorization: Any, verified_plan: Any,
                                 invocation_authorization: Any, artifact_path: Path,
                                 invocation_evidence_path: Path, conformance_authorization: Any,
                                 conformance_evidence_path: Path,
                                 authorization: PublicationManifestAuthorization) -> PublicationManifestResult:
    """Consume one valid authorization and persist one independently reloadable Manifest."""
    try:
        persisted = _persisted_conformance(
            artifact_path=artifact_path, invocation_evidence_path=invocation_evidence_path,
            conformance_evidence_path=conformance_evidence_path, evidence_snapshot=evidence_snapshot,
            verified_release=verified_release, lifecycle_scope=lifecycle_scope, declaration=declaration,
            planning_authorization=planning_authorization, verified_plan=verified_plan,
            invocation_authorization=invocation_authorization, conformance_authorization=conformance_authorization)
    except Exception:
        findings = _independent_failure_findings(authorization, artifact_path)
        findings.extend((
            _finding("persisted-conformance-invalid", "/conformance", "Persisted semantic-conformance evidence failed independent verification."),
            _finding("governed-artifact-derivation-indeterminate", "/artifacts", "Artifact authority derivation is indeterminate because persisted semantic-conformance verification failed."),
        ))
        return PublicationManifestResult(_sorted(findings), None)
    artifact_paths = (Path(artifact_path),)
    findings = _authorization_findings(authorization, persisted=persisted, verified_release=verified_release,
                                       lifecycle_scope=lifecycle_scope, declaration=declaration,
                                       planning_authorization=planning_authorization,
                                       verified_plan=verified_plan, invocation_authorization=invocation_authorization,
                                       conformance_authorization=conformance_authorization,
                                       artifact_paths=artifact_paths)
    if findings: return PublicationManifestResult(findings, None)
    try:
        _reserve_authorization(authorization)
    except FileExistsError:
        return PublicationManifestResult((_finding("manifest-authorization-consumed", "/authorization/fingerprint", "Manifest authorization has already been consumed."),), None)
    except Exception:
        return PublicationManifestResult((_finding("manifest-authorization-consumption-failed", "/authorization/fingerprint", "Authorization reservation could not be durably completed."),), None)
    try:
        bundle = BCRPBundle(persisted.bundle.profile_identity, persisted.bundle.profile_version,
                            persisted.bundle.records + (_manifest_record(persisted.bundle, authorization),))
        verified = _verify_bundle(bundle, persisted.bundle, authorization)
        _persist_manifest_transaction(authorization, verified._bundle_document.encode("utf-8"))
        reloaded = verify_persisted_publication_manifest(
            manifest_evidence_path=Path(authorization.evidence_directory) / authorization.evidence_filename,
            evidence_snapshot=evidence_snapshot, verified_release=verified_release,
            lifecycle_scope=lifecycle_scope, declaration=declaration,
            planning_authorization=planning_authorization, verified_plan=verified_plan,
            invocation_authorization=invocation_authorization,
            conformance_authorization=conformance_authorization,
            artifact_paths=artifact_paths, authorization=authorization)
        return PublicationManifestResult((), reloaded)
    except Exception:
        # The transaction helper performs rollback for persistence failures.  If
        # independent reload fails afterward, remove only this exact transaction.
        evidence = Path(authorization.evidence_directory) / authorization.evidence_filename
        commitment = Path(authorization.commitment_ledger_directory) / _commitment_name(authorization)
        for path in (commitment, evidence):
            try:
                if path.is_file() and not path.is_symlink(): path.unlink()
            except OSError: pass
        return PublicationManifestResult((_finding("manifest-persistence-failed", "/evidence", "Manifest transaction or independent persisted reload failed."),), None)


def verify_persisted_publication_manifest(*, manifest_evidence_path: Path, evidence_snapshot: Any,
                                          verified_release: Any, lifecycle_scope: Any, declaration: Any,
                                          planning_authorization: Any, verified_plan: Any,
                                          invocation_authorization: Any, conformance_authorization: Any,
                                          artifact_paths: tuple[Path, ...],
                                          authorization: PublicationManifestAuthorization) -> VerifiedPublicationManifest:
    """Reload canonical bytes, commitments, predecessor, and all current admission bindings."""
    expected_path = Path(authorization.evidence_directory) / authorization.evidence_filename
    if manifest_evidence_path != expected_path: raise ValueError("Manifest evidence path differs from authorization.")
    if type(artifact_paths) is not tuple or len(artifact_paths) != 1:
        raise ValueError("Production persisted verification requires exactly one governed artifact path.")
    representative = (
        getattr(conformance_authorization, "assessor_implementation", None)
        == "briefforge.representative_semantic_artifact_conformance"
    )
    if representative:
        artifact_path = Path(conformance_authorization.artifact_destination)
        invocation_evidence_path = Path(conformance_authorization.invocation_evidence_destination)
    else:
        artifact_path = Path(artifact_paths[0])
        invocation_evidence_path = (Path(invocation_authorization.output_directory) /
                                    invocation_authorization.evidence_filename)
    if artifact_path != Path(artifact_paths[0]):
        raise ValueError("Governed artifact path differs from conformance authorization.")
    persisted = _persisted_conformance(
        artifact_path=artifact_path, invocation_evidence_path=invocation_evidence_path,
        conformance_evidence_path=Path(conformance_authorization.evidence_directory) / conformance_authorization.evidence_filename,
        evidence_snapshot=evidence_snapshot, verified_release=verified_release, lifecycle_scope=lifecycle_scope,
        declaration=declaration, planning_authorization=planning_authorization, verified_plan=verified_plan,
        invocation_authorization=invocation_authorization, conformance_authorization=conformance_authorization)
    findings = _authorization_findings(authorization, persisted=persisted, verified_release=verified_release,
                                       lifecycle_scope=lifecycle_scope, declaration=declaration,
                                       planning_authorization=planning_authorization,
                                       verified_plan=verified_plan, invocation_authorization=invocation_authorization,
                                       conformance_authorization=conformance_authorization, artifact_paths=artifact_paths)
    if findings: raise ValueError("Persisted Manifest authorization or artifact closure is stale or contradictory.")
    evidence_fd, evidence_identity = _open_directory(Path(authorization.evidence_directory))
    ledger_fd, ledger_identity = _open_directory(Path(authorization.commitment_ledger_directory))
    try:
        evidence = _read_regular(evidence_fd, authorization.evidence_filename, _MAX_EVIDENCE)
        consumption = _read_regular(ledger_fd, _consumption_name(authorization), 8192)
        commitment = _read_regular(ledger_fd, _commitment_name(authorization), 8192)
        ei, li = os.fstat(evidence_fd), os.fstat(ledger_fd)
        if (ei.st_dev, ei.st_ino) != evidence_identity or (li.st_dev, li.st_ino) != ledger_identity:
            raise ValueError("Authorized directory identity changed during reload.")
    finally: os.close(evidence_fd); os.close(ledger_fd)
    try: text = evidence.decode("utf-8")
    except UnicodeDecodeError as exc: raise ValueError("Manifest evidence is not UTF-8.") from exc
    bundle = _deserialize_bundle(text)
    if text != _serialize_bundle(bundle): raise ValueError("Manifest evidence bytes are not canonical.")
    verified = _verify_bundle(bundle, persisted.bundle, authorization)
    if consumption != _consumption_bytes(authorization): raise ValueError("Manifest authorization consumption commitment is absent or mismatched.")
    if commitment != _commitment_bytes(authorization, evidence): raise ValueError("External Manifest admission commitment is absent or mismatched.")
    return verified


def verify_manifest_current_eligibility(verified: VerifiedPublicationManifest, *, lifecycle_scope: Any) -> PublicationManifestResult:
    """Evaluate present lifecycle eligibility without changing historical evidence."""
    if type(verified) is not VerifiedPublicationManifest or verified._marker is not _VERIFIED_MARKER:
        return PublicationManifestResult((_finding("invalid-verified-manifest", "/manifest", "Exact admitted Manifest proof is required."),), None)
    release_identity = verified.bundle.one("PublicationManifestRecord").semantic["release_ref"]
    try: eligible = _lifecycle_current(lifecycle_scope, release_identity)
    except Exception: eligible = False
    if not eligible:
        return PublicationManifestResult((_finding("manifest-not-currently-eligible", "/lifecycle", "Manifest Release is no longer the sole complete current lifecycle state."),), None)
    return PublicationManifestResult((), verified)
