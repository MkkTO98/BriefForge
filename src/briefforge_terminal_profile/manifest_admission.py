"""Closed terminal-profile Manifest-v2 admission and fixed historical/successor selector.

There is deliberately no registry, hook, callable argument, import string, or
fallback.  Selection is made from exact authorization classes and persisted
record contracts before either verifier is entered.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from briefforge.bcrp.canonical import fingerprint_bundle
from briefforge.bcrp.model import BCRPBundle, BCRPRecord, PROFILE_VERSION
from briefforge.publication_manifest_admission import (
    ManifestArtifactAdmission, ManifestFinding, PublicationManifestAuthorization,
    PublicationManifestResult, VerifiedPublicationManifest,
    compute_artifact_set_fingerprint, compute_manifest_authorization_fingerprint,
)
import briefforge.publication_manifest_admission as historical

# Successor imports are deliberately deferred: the delivery module imports this selector
# while its own module is still initializing, and the profile's public scope
# constructor depends on the delivery module. Deferral removes that import cycle without
# introducing dynamic selection.
_TERMINAL_PROFILE_ID = "briefforge:representative-terminal-static-html-profile:2.0.0"
_TERMINAL_PROFILE_VERSION = "2.0.0"

MANIFEST_POLICY_ID = "briefforge-terminal-publication-manifest-admission-policy:2.0.0"
MANIFEST_PROFILE_ID = "briefforge:terminal-publication-manifest-admission-profile:2.0.0"
MANIFEST_VERSION = "2.0.0"
MANIFEST_IMPLEMENTATION = "briefforge_terminal_profile.manifest_admission"
MANIFEST_CONTRACT = "briefforge:terminal-publication-manifest-admission-authority:2.0.0"
_PROJECTOR = "authority:briefforge-publication-manifest-projector"
_OWNER = "project:BriefForge"
_ROLE = "publication-manifest-projector"
_SCOPE = "one-publication-manifest-production"
_EXCLUSIONS = historical._EXCLUSIONS
_KINDS = historical._PREDECESSOR_KINDS
_MAX = 8 * 1024 * 1024
_ARCHIVE_MANIFEST_DIGEST = "2e9532f68c43c62a26863001b574f2f175d5a0a36332204a3eefea2ea558c5a1"
_ACTIVE_DELIVERY_DIGEST = "b75bbf3bd0c219595a9f93c4cc0409dd7e1665a8425a62ce80293affe355d5b3"
_ARCHIVE_PATHS = (
    "__init__.py", "_controlled_renderer_worker.py", "_representative_renderer_worker.py",
    "bcrp/__init__.py", "bcrp/authoring.py", "bcrp/canonical.py", "bcrp/corpus.py",
    "bcrp/graph.py", "bcrp/loader.py", "bcrp/model.py", "bcrp/structure.py",
    "bcrp/validation.py", "bcrp_legacy_compatibility.py", "bounded_loopback_deployment.py",
    "builder.py", "communication_intent_experiment.py", "communication_intent_renderer_experiment.py",
    "controlled_renderer_invocation.py", "downstream.py", "presentation_models.py", "promotion.py",
    "publication_distribution_delivery.py", "publication_lifecycle/__init__.py",
    "publication_lifecycle/canonical.py", "publication_lifecycle/loader.py",
    "publication_lifecycle/model.py", "publication_lifecycle/validation.py",
    "publication_manifest_admission.py", "publication_release.py", "renderer_adapter.py",
    "renderer_compatibility_planning.py", "representative_controlled_invocation.py",
    "representative_projection.py", "representative_renderer.py",
    "representative_semantic_conformance.py", "runtime.py", "semantic_artifact_conformance.py",
    "technical_publication_verification.py", "validation.py",
)

# The successor intentionally retains the accepted immutable inventory and
# authorization envelopes.  The exact profile/version and atomic evidence tuple
# distinguish it; aliases avoid creating a parallel delivery data model.
TerminalManifestArtifactAdmission = ManifestArtifactAdmission
TerminalPublicationManifestAuthorization = PublicationManifestAuthorization
TerminalVerifiedPublicationManifest = VerifiedPublicationManifest
TerminalPublicationManifestResult = PublicationManifestResult
compute_terminal_artifact_set_fingerprint = compute_artifact_set_fingerprint
compute_terminal_manifest_authorization_fingerprint = compute_manifest_authorization_fingerprint


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _profile_from_release(verified_release: Any) -> TerminalAuthorityProfile:
    from .profile import TerminalAuthorityProfile, verify_terminal_authority_profile
    authorities = verified_release.bundle.one("PortablePresentationMaterialRecord").semantic["authorities"]
    if type(authorities) is not list or len(authorities) < 8:
        raise ValueError("terminal Release authority inventory is incomplete")
    profile = TerminalAuthorityProfile(_TERMINAL_PROFILE_ID, _TERMINAL_PROFILE_VERSION,
                                       tuple(dict(x) for x in authorities[:8]),
                                       tuple(dict(x) for x in authorities[8:]))
    verify_terminal_authority_profile(profile)
    if tuple(authorities) != profile.authorities:
        raise ValueError("terminal Release authority order differs from closed profile")
    return profile


def _persisted_terminal_conformance(*, evidence_snapshot, verified_release, lifecycle_scope,
        declaration, planning_authorization, verified_plan, invocation_authorization,
        conformance_authorization):
    from .controlled_invocation import TerminalRendererInvocationAuthorization
    from .projection import build_terminal_representative_projection
    from .semantic_conformance import (TerminalSemanticArtifactConformanceAuthorization,
        verify_persisted_terminal_semantic_artifact_conformance)
    if type(invocation_authorization) is not TerminalRendererInvocationAuthorization:
        raise ValueError("exact successor invocation authorization required")
    if type(conformance_authorization) is not TerminalSemanticArtifactConformanceAuthorization:
        raise ValueError("exact successor conformance authorization required")
    profile = _profile_from_release(verified_release)
    projection = build_terminal_representative_projection(
        verified_release=verified_release, evidence_snapshot=evidence_snapshot,
        lifecycle_scope=lifecycle_scope, declaration=declaration,
        planning_authorization=planning_authorization, verified_plan=verified_plan,
        authority_profile=profile)
    return verify_persisted_terminal_semantic_artifact_conformance(
        artifact_path=Path(conformance_authorization.artifact_destination),
        invocation_evidence_path=Path(conformance_authorization.invocation_evidence_destination),
        evidence_snapshot=evidence_snapshot, verified_release=verified_release,
        lifecycle_scope=lifecycle_scope, declaration=declaration,
        planning_authorization=planning_authorization, verified_plan=verified_plan,
        authority_profile=profile, invocation_authorization=invocation_authorization,
        authorization=conformance_authorization, projection=projection)


def _expected_inventory(persisted, authorization, conformance_authorization):
    audit = persisted.bundle.one("GeneratedArtifactAuditRecord")
    artifact = audit.semantic["artifact"]
    return (ManifestArtifactAdmission(
        identity=artifact["id"], role="primary-semantic-publication",
        logical_filename=artifact["filename"], media_type=artifact["media_type"],
        byte_length=artifact["byte_length"], sha256=artifact["sha256"], order=0,
        source_path=str(Path(conformance_authorization.artifact_destination).resolve()),
        release_identity=authorization.release_identity, release_fingerprint=authorization.release_fingerprint,
        plan_identity=authorization.plan_identity, plan_fingerprint=authorization.plan_fingerprint,
        renderer_identity=conformance_authorization.renderer_identity,
        renderer_version=conformance_authorization.renderer_version,
        invocation_authorization_identity=conformance_authorization.invocation_authorization_identity,
        invocation_evidence_fingerprint=conformance_authorization.invocation_evidence_fingerprint,
        conformance_authorization_identity=conformance_authorization.identity,
        conformance_evidence_fingerprint=persisted.fingerprint.digest,
        dependency_identities=()),)


def _validate_authorization(a, *, persisted, verified_release, lifecycle_scope, declaration,
                            planning_authorization, verified_plan, invocation_authorization, conformance_authorization,
                            artifact_paths):
    if type(a) is not PublicationManifestAuthorization:
        raise ValueError("exact immutable Manifest authorization required")
    if len(persisted.bundle.records) != 10 or tuple(x.kind for x in persisted.bundle.records) != _KINDS:
        raise ValueError("exact ten-kind successor predecessor required")
    for name in (
        "identity", "policy_identity", "profile_identity", "profile_version", "authority_identity",
        "authority_owner", "authority_role", "release_identity", "plan_identity", "capability_identity",
        "renderer_identity", "renderer_version", "invocation_authorization_identity",
        "conformance_authorization_identity", "conformance_profile_identity", "conformance_profile_version",
        "assessor_identity", "manifest_identity", "manifest_version", "projector_implementation",
        "projector_version", "record_identity",
    ):
        if not historical._stable_text(getattr(a, name, None)):
            raise ValueError(f"invalid stable successor Manifest field: {name}")
    for name in ("authorization_time", "manifest_time"):
        if not historical._offset_time(getattr(a, name, None)):
            raise ValueError(f"invalid successor Manifest timestamp: {name}")
    try:
        predecessor_times = (
            historical._parse_offset_time(verified_release.release.semantic["publication_time"]),
            historical._parse_offset_time(declaration.declaration_time),
            historical._parse_offset_time(planning_authorization.planning_time),
            historical._parse_offset_time(invocation_authorization.authorization_time),
            historical._parse_offset_time(conformance_authorization.authorization_time),
        )
        authorization_time = historical._parse_offset_time(a.authorization_time)
        manifest_time = historical._parse_offset_time(a.manifest_time)
        if max(predecessor_times) > authorization_time or authorization_time > manifest_time:
            raise ValueError
    except (AttributeError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError("successor Manifest authorization chronology invalid") from exc
    if (a.manifest_identity == a.identity or a.record_identity == a.identity
            or a.record_identity == a.manifest_identity
            or a.record_identity in persisted.bundle.by_identity()):
        raise ValueError("successor Manifest identities are not unique")
    inventory = _expected_inventory(persisted, a, conformance_authorization)
    expected = {
        "policy_identity": MANIFEST_POLICY_ID, "profile_identity": MANIFEST_PROFILE_ID,
        "profile_version": MANIFEST_VERSION, "authority_identity": _PROJECTOR,
        "authority_owner": _OWNER, "authority_role": _ROLE,
        "release_identity": verified_release.release.identity,
        "release_fingerprint": verified_release.fingerprint.digest,
        "lifecycle_inventory_digest": lifecycle_scope.inventory_digest,
        "plan_identity": verified_plan.plan.identity, "plan_fingerprint": verified_plan.fingerprint.digest,
        "capability_identity": declaration.identity, "capability_fingerprint": declaration.fingerprint,
        "renderer_identity": conformance_authorization.renderer_identity,
        "renderer_version": conformance_authorization.renderer_version,
        "renderer_implementation_digest": conformance_authorization.renderer_implementation_digest,
        "invocation_authorization_identity": invocation_authorization.identity,
        "invocation_authorization_fingerprint": invocation_authorization.fingerprint,
        "invocation_evidence_fingerprint": conformance_authorization.invocation_evidence_fingerprint,
        "conformance_authorization_identity": conformance_authorization.identity,
        "conformance_authorization_fingerprint": conformance_authorization.fingerprint,
        "conformance_profile_identity": conformance_authorization.profile_identity,
        "conformance_profile_version": conformance_authorization.profile_version,
        "assessor_identity": conformance_authorization.authority_identity,
        "conformance_evidence_fingerprint": persisted.fingerprint.digest,
        "predecessor_closure_fingerprint": fingerprint_bundle(persisted.bundle, domain="profile-instance", require_valid=False).digest,
        "artifact_inventory": inventory, "artifact_set_fingerprint": compute_artifact_set_fingerprint(inventory),
        "manifest_version": MANIFEST_VERSION, "projector_implementation": MANIFEST_IMPLEMENTATION,
        "projector_version": MANIFEST_VERSION, "exclusions": _EXCLUSIONS,
    }
    mismatches = [name for name, value in expected.items() if getattr(a, name, None) != value]
    if mismatches:
        raise ValueError("successor Manifest atomic binding mismatch: " + ",".join(mismatches))
    if a.conformance_verdict != "approved" or a.evidence_filename != "publication-manifest.json":
        raise ValueError("successor Manifest verdict or filename differs")
    if a.fingerprint != compute_manifest_authorization_fingerprint(a):
        raise ValueError("successor Manifest authorization fingerprint stale")
    if (type(artifact_paths) is not tuple or len(artifact_paths) != 1
            or artifact_paths != (Path(conformance_authorization.artifact_destination),)):
        raise ValueError("successor artifact path closure differs")
    data = historical._read_regular_path(artifact_paths[0])
    if len(data) != inventory[0].byte_length or hashlib.sha256(data).hexdigest() != inventory[0].sha256:
        raise ValueError("successor artifact bytes differ")
    if not historical._lifecycle_current(lifecycle_scope, a.release_identity):
        raise ValueError("successor Release is not current")
    authorities = verified_release.bundle.one("PortablePresentationMaterialRecord").semantic["authorities"]
    exact = {"id": _PROJECTOR, "owner_identity": _OWNER, "role": _ROLE, "scope": _SCOPE}
    if [x for x in authorities if x.get("id") == _PROJECTOR] != [exact]:
        raise ValueError("successor projector authority absent")
    for text, must_exist in ((a.evidence_directory, True), (a.commitment_ledger_directory, False)):
        path = Path(text)
        if not path.is_absolute() or str(path.resolve()) != text or path.is_symlink() or (must_exist and not path.is_dir()):
            raise ValueError("unsafe successor Manifest persistence boundary")


def _record(predecessor, a, conformance_authorization):
    audit = predecessor.one("GeneratedArtifactAuditRecord")
    conformance = predecessor.one("SemanticArtifactConformanceRecord")
    release = predecessor.one("PublicationReleaseRecord")
    artifacts = [historical._artifact_document(x) for x in a.artifact_inventory]
    atomic = {
        "successor_profile_identity": _TERMINAL_PROFILE_ID,
        "successor_profile_version": _TERMINAL_PROFILE_VERSION,
        "successor_projection_fingerprint": conformance_authorization.successor_projection_fingerprint,
        "translated_projection_fingerprint": conformance_authorization.translated_projection_fingerprint,
        "adapter_identity": conformance_authorization.adapter_identity,
        "adapter_version": conformance_authorization.adapter_version,
        "adapter_implementation_digest": conformance_authorization.adapter_implementation_digest,
        "renderer_identity": conformance_authorization.renderer_identity,
        "renderer_version": conformance_authorization.renderer_version,
        "renderer_implementation_digest": conformance_authorization.renderer_implementation_digest,
        "invocation_authorization_identity": conformance_authorization.invocation_authorization_identity,
        "invocation_authorization_fingerprint": conformance_authorization.invocation_authorization_fingerprint,
        "invocation_evidence_fingerprint": conformance_authorization.invocation_evidence_fingerprint,
        "conformance_authorization_identity": conformance_authorization.identity,
        "conformance_authorization_fingerprint": conformance_authorization.fingerprint,
        "conformance_evidence_fingerprint": a.conformance_evidence_fingerprint,
    }
    payload = {"contract_identity": MANIFEST_CONTRACT, "policy_identity": a.policy_identity,
        "profile_identity": a.profile_identity, "profile_version": a.profile_version,
        "authorization_identity": a.identity, "authorization_fingerprint": a.fingerprint,
        "manifest_identity": a.manifest_identity, "manifest_version": a.manifest_version,
        "manifest_time": a.manifest_time, "release_fingerprint": a.release_fingerprint,
        "lifecycle_inventory_digest": a.lifecycle_inventory_digest,
        "predecessor_closure_fingerprint": a.predecessor_closure_fingerprint,
        "artifact_set_fingerprint": a.artifact_set_fingerprint, "artifact_inventory": artifacts,
        "atomic_successor_tuple": atomic, "aggregate_manifest_verdict": "approved",
        "verification_status": "verified", "authority_exclusions": list(a.exclusions),
        "distribution_authority": "absent", "distribution_execution": "not-performed",
        "successful_publication": "not-asserted", "deployment_authority": "absent"}
    catalog = [{k: d[k] for k in ("identity","role","order","logical_filename","media_type","byte_length","sha256")} for d in artifacts]
    return BCRPRecord("PublicationManifestRecord", a.record_identity, PROFILE_VERSION,
        {"release_ref": release.identity, "lifecycle_status": release.semantic["lifecycle_status"],
         "artifact_audit_refs": [audit.identity], "conformance_refs": [conformance.identity],
         "artifact_ids": [x.identity for x in a.artifact_inventory], "manifest_identity": a.manifest_identity,
         "manifest_version": a.manifest_version, "policy_identity": a.policy_identity,
         "profile_identity": a.profile_identity, "profile_version": a.profile_version,
         "authorization_time": a.authorization_time, "manifest_time": a.manifest_time,
         "artifact_catalog": catalog},
        [{"owner_namespace":"briefforge-terminal-publication-manifest-admission","name":"exact-successor-artifact-admission",
          "version":MANIFEST_VERSION,"authority_ref":_PROJECTOR,"scope":"publication-manifest-admission-only",
          "target_refs":[release.identity,audit.identity,conformance.identity]+[x.identity for x in a.artifact_inventory],
          "criticality":"required","character":"semantic","validation_contract":MANIFEST_CONTRACT,
          "preservation":"must-preserve","payload":payload}])


def _verify_bundle(bundle, predecessor, a, ca):
    if len(bundle.records) != 11 or tuple(x.kind for x in bundle.records[:10]) != _KINDS or bundle.records[-1].kind != "PublicationManifestRecord":
        raise ValueError("successor Manifest requires exact eleven-kind BCRP closure")
    if tuple(x.to_document() for x in bundle.records[:10]) != tuple(x.to_document() for x in predecessor.records):
        raise ValueError("successor Manifest changed predecessor bytes")
    if bundle.records[-1].to_document() != _record(predecessor, a, ca).to_document():
        raise ValueError("successor Manifest record differs from independent reproduction")
    fp = fingerprint_bundle(bundle, domain="profile-instance", require_valid=False)
    return VerifiedPublicationManifest._admitted(historical._serialize_bundle(bundle), fp)


def _common(kwargs):
    ca = kwargs["conformance_authorization"]
    persisted = _persisted_terminal_conformance(**{k: kwargs[k] for k in (
        "evidence_snapshot","verified_release","lifecycle_scope","declaration","planning_authorization",
        "verified_plan","invocation_authorization","conformance_authorization")})
    if "artifact_paths" not in kwargs:
        raise ValueError("exact successor artifact_paths tuple required")
    paths = kwargs["artifact_paths"]
    _validate_authorization(kwargs["authorization"], persisted=persisted,
        verified_release=kwargs["verified_release"], lifecycle_scope=kwargs["lifecycle_scope"],
        declaration=kwargs["declaration"], planning_authorization=kwargs["planning_authorization"],
        verified_plan=kwargs["verified_plan"],
        invocation_authorization=kwargs["invocation_authorization"], conformance_authorization=ca,
        artifact_paths=paths)
    return persisted, paths


def produce_terminal_publication_manifest(**kwargs):
    try:
        kwargs = dict(kwargs)
        if "artifact_paths" not in kwargs:
            kwargs["artifact_paths"] = (Path(kwargs["artifact_path"]),)
        persisted, _ = _common(kwargs); a=kwargs["authorization"]; ca=kwargs["conformance_authorization"]
        historical._reserve_authorization(a)
        bundle=BCRPBundle(persisted.bundle.profile_identity,persisted.bundle.profile_version,
                          persisted.bundle.records+(_record(persisted.bundle,a,ca),))
        verified=_verify_bundle(bundle,persisted.bundle,a,ca)
        historical._persist_manifest_transaction(a,verified._bundle_document.encode())
        reloaded=verify_persisted_terminal_publication_manifest(
            manifest_evidence_path=Path(a.evidence_directory)/a.evidence_filename, **{k:v for k,v in kwargs.items() if k not in {"artifact_path","manifest_evidence_path"}})
        return PublicationManifestResult((),reloaded)
    except Exception as exc:
        return PublicationManifestResult((ManifestFinding("terminal-manifest-admission-blocked","/manifest",str(exc)),),None)


def verify_persisted_terminal_publication_manifest(*, manifest_evidence_path, **kwargs):
    persisted, _ = _common(kwargs); a=kwargs["authorization"]; ca=kwargs["conformance_authorization"]
    expected=Path(a.evidence_directory)/a.evidence_filename
    if Path(manifest_evidence_path)!=expected: raise ValueError("successor Manifest path differs")
    evidence=historical._read_regular_path(expected,_MAX)
    text=evidence.decode(); bundle=historical._deserialize_bundle(text)
    if text!=historical._serialize_bundle(bundle): raise ValueError("successor Manifest bytes are noncanonical")
    verified=_verify_bundle(bundle,persisted.bundle,a,ca)
    ledger=Path(a.commitment_ledger_directory)
    if historical._read_regular_path(ledger/historical._consumption_name(a),8192)!=historical._consumption_bytes(a): raise ValueError("Manifest consumption differs")
    if historical._read_regular_path(ledger/historical._commitment_name(a),8192)!=historical._commitment_bytes(a,evidence): raise ValueError("Manifest commitment differs")
    return verified


def verify_terminal_manifest_current_eligibility(verified, *, lifecycle_scope):
    if type(verified) is not VerifiedPublicationManifest or verified._marker is not historical._VERIFIED_MARKER:
        return PublicationManifestResult((ManifestFinding("invalid-verified-manifest","/manifest","Exact admitted Manifest required"),),None)
    record=verified.bundle.one("PublicationManifestRecord")
    if record.extensions[0].get("validation_contract")!=MANIFEST_CONTRACT:
        return PublicationManifestResult((ManifestFinding("invalid-verified-manifest","/manifest","Successor Manifest contract required"),),None)
    try: eligible=historical._lifecycle_current(lifecycle_scope,record.semantic["release_ref"])
    except Exception: eligible=False
    if not eligible: return PublicationManifestResult((ManifestFinding("manifest-not-currently-eligible","/lifecycle","Manifest Release is not current"),),None)
    return PublicationManifestResult((),verified)


def _manifest_contract(path):
    raw=historical._read_regular_path(Path(path),_MAX)
    bundle=historical._deserialize_bundle(raw.decode())
    if len(bundle.records)!=11 or tuple(x.kind for x in bundle.records[:10])!=_KINDS or bundle.records[-1].kind!="PublicationManifestRecord":
        raise ValueError("unsupported Manifest topology")
    extensions=bundle.records[-1].extensions
    if len(extensions)!=1 or type(extensions[0]) is not dict: raise ValueError("unsupported Manifest extension topology")
    return extensions[0].get("validation_contract")


def _verify_archived_historical_closure():
    """Prove genuine archived bytes; never assign their digest to changed active bytes."""
    root=Path(__file__).resolve().parents[2]
    archive=root/"artifacts/source-closures/task060-v1"
    manifest_bytes=(archive/"manifest.json").read_bytes()
    document=json.loads(manifest_bytes)
    expected_keys={"closure_identity","closure_version","domains","file_count","files","historical_digests",
                   "interpreter","manifest_sha256","ordering","source_root"}
    if type(document) is not dict or set(document)!=expected_keys:
        raise ValueError("historical source closure manifest malformed")
    root_document=dict(document); supplied_root=root_document.pop("manifest_sha256")
    computed_root=hashlib.sha256(_canonical(root_document)).hexdigest()
    if supplied_root!=_ARCHIVE_MANIFEST_DIGEST or computed_root!=_ARCHIVE_MANIFEST_DIGEST:
        raise ValueError("historical source closure root differs")
    if (document["closure_identity"]!="briefforge:task060-historical-source-closure:1.0.0"
            or document["closure_version"]!="1.0.0"
            or document["source_root"]!="src/briefforge" or document["ordering"]!="ascending-relative-posix-path"
            or document["file_count"]!=39 or type(document["files"]) is not list):
        raise ValueError("historical source closure manifest malformed")
    paths=tuple(item.get("path") if type(item) is dict else None for item in document["files"])
    if paths!=_ARCHIVE_PATHS or paths!=tuple(sorted(set(paths))):
        raise ValueError("historical source closure path inventory differs")
    interpreter={"cache_tag":"cpython-312", "executable_realpath":"/usr/bin/python3.12",
                 "implementation":"cpython",
                 "version":"3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0]"}
    if document["interpreter"]!=interpreter:
        raise ValueError("historical interpreter descriptor differs")
    measured={
        "renderer":bytearray(b"briefforge-representative-renderer-closure-v1\0"),
        "assessor":bytearray(b"briefforge-representative-assessor-closure-v1\0"),
    }
    for item in document["files"]:
        if set(item)!={"path","byte_length","sha256"} or type(item["path"]) is not str:
            raise ValueError("historical source closure item malformed")
        relative=Path(item["path"])
        if relative.is_absolute() or relative.as_posix()!=item["path"] or any(part in {"", ".", ".."} for part in relative.parts):
            raise ValueError("historical source closure path unsafe")
        archived=archive/"src/briefforge"/item["path"]
        data=historical._read_regular_path(archived,_MAX)
        if type(item["byte_length"]) is not int or type(item["sha256"]) is not str or len(data)!=item["byte_length"] or hashlib.sha256(data).hexdigest()!=item["sha256"]:
            raise ValueError("archived historical source closure changed")
        for closure in measured.values():
            closure.extend(item["path"].encode("ascii")+b"\0"+data+b"\0")
        # Delivery is the one architecture-authorized additive dispatch seam.
        if item["path"]!="publication_distribution_delivery.py":
            active=root/"src/briefforge"/item["path"]
            if hashlib.sha256(historical._read_regular_path(active,_MAX)).hexdigest()!=item["sha256"]:
                raise ValueError("active historical implementation differs from archived closure")
    interpreter_bytes=_canonical(interpreter)
    for closure in measured.values(): closure.extend(b"interpreter\0"+interpreter_bytes+b"\0")
    if document["domains"]!={"assessor":"briefforge-representative-assessor-closure-v1",
                              "renderer":"briefforge-representative-renderer-closure-v1"}:
        raise ValueError("historical closure domains differ")
    actual={name:hashlib.sha256(value).hexdigest() for name,value in measured.items()}
    if document["historical_digests"]!=actual:
        raise ValueError("historical renderer or assessor closure digest differs")
    active_delivery=historical._read_regular_path(root/"src/briefforge/publication_distribution_delivery.py",_MAX)
    if hashlib.sha256(active_delivery).hexdigest()!=_ACTIVE_DELIVERY_DIGEST:
        raise ValueError("active additive delivery dispatch file differs")


def verify_persisted_publication_manifest(**kwargs):
    from .controlled_invocation import TerminalRendererInvocationAuthorization
    from .semantic_conformance import TerminalSemanticArtifactConformanceAuthorization
    from briefforge_paired_terminal_profile.controlled_invocation import PairedTerminalRendererInvocationAuthorization
    from briefforge_paired_terminal_profile.semantic_conformance import PairedTerminalSemanticArtifactConformanceAuthorization
    from briefforge_paired_terminal_profile.manifest_admission import verify_persisted_paired_terminal_publication_manifest
    from briefforge.controlled_renderer_invocation import RendererInvocationAuthorization
    from briefforge.semantic_artifact_conformance import SemanticArtifactConformanceAuthorization
    from briefforge.representative_controlled_invocation import RepresentativeRendererInvocationAuthorization
    from briefforge.representative_semantic_conformance import RepresentativeSemanticArtifactConformanceAuthorization
    contract=_manifest_contract(kwargs["manifest_evidence_path"])
    ia,ca,a=kwargs.get("invocation_authorization"),kwargs.get("conformance_authorization"),kwargs.get("authorization")
    successor=(type(ia) is TerminalRendererInvocationAuthorization and type(ca) is TerminalSemanticArtifactConformanceAuthorization
               and type(a) is PublicationManifestAuthorization and contract==MANIFEST_CONTRACT)
    paired=(type(ia) is PairedTerminalRendererInvocationAuthorization
            and type(ca) is PairedTerminalSemanticArtifactConformanceAuthorization
            and type(a) is PublicationManifestAuthorization
            and contract=="briefforge:paired-terminal-publication-manifest-admission-authority:3.0.0")
    historical_v1=(type(a) is PublicationManifestAuthorization
                   and type(ia) is RendererInvocationAuthorization
                   and type(ca) is SemanticArtifactConformanceAuthorization
                   and contract==historical._EXTENSION_CONTRACT)
    historical_v2=(type(a) is PublicationManifestAuthorization
                   and type(ia) is RepresentativeRendererInvocationAuthorization
                   and type(ca) is RepresentativeSemanticArtifactConformanceAuthorization
                   and contract==historical._EXTENSION_CONTRACT)
    if successor: return verify_persisted_terminal_publication_manifest(**kwargs)
    if paired: return verify_persisted_paired_terminal_publication_manifest(**kwargs)
    if historical_v1 or historical_v2:
        _verify_archived_historical_closure()
        return historical.verify_persisted_publication_manifest(**kwargs)
    raise ValueError("Manifest selector rejected mixed or unknown tuple")


def verify_manifest_current_eligibility(verified, *, lifecycle_scope):
    if type(verified) is not VerifiedPublicationManifest or verified._marker is not historical._VERIFIED_MARKER:
        return historical.verify_manifest_current_eligibility(verified,lifecycle_scope=lifecycle_scope)
    contract=verified.bundle.one("PublicationManifestRecord").extensions[0].get("validation_contract")
    if contract==MANIFEST_CONTRACT: return verify_terminal_manifest_current_eligibility(verified,lifecycle_scope=lifecycle_scope)
    if contract=="briefforge:paired-terminal-publication-manifest-admission-authority:3.0.0":
        from briefforge_paired_terminal_profile.manifest_admission import verify_paired_manifest_current_eligibility
        return verify_paired_manifest_current_eligibility(verified,lifecycle_scope=lifecycle_scope)
    if contract==historical._EXTENSION_CONTRACT: return historical.verify_manifest_current_eligibility(verified,lifecycle_scope=lifecycle_scope)
    raise ValueError("Manifest eligibility selector rejected unknown contract")

# Public facade names for successor callers; delivery imports the selector names.
produce_publication_manifest = produce_terminal_publication_manifest
