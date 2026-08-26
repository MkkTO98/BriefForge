"""Controlled successor invocation and immutable evidence boundary."""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import threading
from typing import Any

from briefforge.bcrp.canonical import fingerprint_bundle
from briefforge.bcrp.model import BCRPBundle, BCRPRecord, Fingerprint, PROFILE_VERSION
from briefforge.publication_release import verify_publication_release
from briefforge.renderer_compatibility_planning import verify_renderer_compatibility_plan
from briefforge.representative_controlled_invocation import (
    _FIXED_ENVIRONMENT, _FIXED_FLAGS, _open_directory, _read_regular,
    _read_regular_at, _render_in_subprocess, _serialize_bundle, _deserialize_bundle,
    _write_exclusive_at, representative_renderer_implementation_digest,
)
from briefforge.representative_renderer import render_representative_html

from .profile import TerminalAuthorityProfile
from .projection import (
    ADAPTER_IDENTITY, ADAPTER_VERSION, PROJECTION_IDENTITY, PROJECTION_VERSION,
    RENDERER_IDENTITY, RENDERER_VERSION, TerminalRepresentativeProjection,
    build_terminal_representative_projection, verify_terminal_projection,
)
from .renderer_adapter import adapt_terminal_projection, adapter_source_digest

INVOCATION_EVIDENCE_CONTRACT = "briefforge:terminal-controlled-renderer-invocation-evidence:1.0.0"
CONTROLLED_INVOCATION_POLICY_ID = "briefforge-terminal-controlled-renderer-invocation-policy:1.0.0"
AUTHORITY_IDENTITY = "authority:briefforge-controlled-renderer-invocation"
AUTHORITY_OWNER = "project:BriefForge"
AUTHORITY_ROLE = "renderer-invocation-authority"
INVOCATION_MODE = "one-artifact-with-determinism-replay"
_FIXED_EXCLUSIONS = (
    "authority:briefforge-bcrp-validation", "authority:briefforge-publication-release",
    "authority:briefforge-controlled-renderer-invocation", "authority:briefforge-semantic-artifact-conformance",
    "authority:briefforge-publication-manifest-projector", "authority:briefforge-controlled-local-delivery",
    "authority:briefforge-bounded-loopback-deployment", "authority:briefforge-technical-publication-verifier",
)
_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*$")
_LOCK = threading.Lock()


class TerminalInvocationRejected(ValueError): pass


@dataclass(frozen=True)
class TerminalRendererInvocationAuthorization:
    identity: str
    policy_identity: str
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
    successor_projection_fingerprint: str
    translated_projection_fingerprint: str
    adapter_identity: str
    adapter_version: str
    adapter_implementation_digest: str
    renderer_identity: str
    renderer_version: str
    renderer_implementation_digest: str
    authorization_ledger_directory: str
    output_directory: str
    output_filename: str
    output_count: int
    maximum_output_bytes: int
    media_type: str
    environment: tuple[tuple[str, str], ...]
    external_assets: tuple[str, ...]
    invocation_mode: str
    timeout_seconds: int
    evidence_filename: str
    fingerprint: str


@dataclass(frozen=True)
class VerifiedTerminalRendererInvocation:
    _bundle_document: str
    artifact_bytes: bytes
    evidence_bytes: bytes
    artifact_path: Path
    evidence_path: Path
    fingerprint: Fingerprint
    @property
    def bundle(self): return _deserialize_bundle(self._bundle_document)


@dataclass(frozen=True)
class TerminalInvocationResult:
    findings: tuple[str, ...]
    verified: VerifiedTerminalRendererInvocation | None
    @property
    def blocked(self): return self.verified is None


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def _sha(data: bytes) -> str: return hashlib.sha256(data).hexdigest()


def compute_terminal_invocation_authorization_fingerprint(a):
    if type(a) is not TerminalRendererInvocationAuthorization: raise TypeError("exact terminal authorization required")
    document=asdict(a); document.pop("fingerprint")
    return _sha(_canonical(document))


def terminal_invocation_implementation_digest() -> str:
    """Dependency-aware digest of successor invocation, adapter, projection and fixed old boundary."""
    from briefforge import representative_controlled_invocation as boundary
    files=(Path(__file__), Path(__file__).with_name("projection.py"), Path(__file__).with_name("renderer_adapter.py"),
           Path(boundary.__file__))
    measured=bytearray(b"briefforge-terminal-invocation-closure-v1\0")
    for path in files: measured.extend(path.name.encode()+b"\0"+path.read_bytes()+b"\0")
    measured.extend(representative_renderer_implementation_digest().encode())
    return _sha(bytes(measured))


def render_terminal_in_isolation(projection: TerminalRepresentativeProjection, timeout_seconds=5) -> bytes:
    verify_terminal_projection(projection)
    translated=adapt_terminal_projection(projection)
    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 30:
        raise TerminalInvocationRejected("timeout bound invalid")
    digest=representative_renderer_implementation_digest()
    with _LOCK, tempfile.TemporaryDirectory(prefix="terminal-render-a-") as a, tempfile.TemporaryDirectory(prefix="terminal-render-b-") as b:
        first=_render_in_subprocess(translated,timeout_seconds,Path(a),digest)
        second=_render_in_subprocess(translated,timeout_seconds,Path(b),digest)
    if first != second: raise TerminalInvocationRejected("independent renderer runs are nondeterministic")
    if len(first)>1_000_000: raise TerminalInvocationRejected("artifact exceeds fixed bound")
    return first


def _paths(a):
    root=Path(a.output_directory)
    return root,root/a.output_filename,root/a.evidence_filename


def _safe_dir(text):
    path=Path(text)
    return path.is_absolute() and str(path.resolve())==text and path.is_dir() and not path.is_symlink()


def _time(text):
    try:
        parsed=datetime.strptime(text,"%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return parsed.isoformat().replace("+00:00","Z")==text
    except Exception: return False


def _problems(a,projection,translated,release,scope,declaration,plan,planning_authorization):
    if type(a) is not TerminalRendererInvocationAuthorization: return ["exact terminal authorization required"]
    expected={
        "policy_identity":CONTROLLED_INVOCATION_POLICY_ID,"authority_identity":AUTHORITY_IDENTITY,
        "authority_owner":AUTHORITY_OWNER,"authority_role":AUTHORITY_ROLE,
        "release_identity":release.release.identity,"release_fingerprint":release.fingerprint.digest,
        "lifecycle_inventory_digest":scope.inventory_digest,"plan_identity":plan.plan.identity,
        "plan_fingerprint":plan.fingerprint.digest,"capability_identity":declaration.identity,
        "capability_fingerprint":declaration.fingerprint,"successor_projection_fingerprint":projection.fingerprint,
        "translated_projection_fingerprint":translated.fingerprint,"adapter_identity":ADAPTER_IDENTITY,
        "adapter_version":ADAPTER_VERSION,"adapter_implementation_digest":adapter_source_digest(),
        "renderer_identity":RENDERER_IDENTITY,"renderer_version":RENDERER_VERSION,
        "renderer_implementation_digest":representative_renderer_implementation_digest(),"output_count":1,
        "media_type":"text/html","environment":_FIXED_ENVIRONMENT,"external_assets":(),
        "invocation_mode":INVOCATION_MODE,
    }
    result=[f"authorization {name} binding mismatch" for name,value in expected.items() if getattr(a,name,None)!=value]
    if not _ID.fullmatch(a.identity or "") or not _time(a.authorization_time): result.append("authorization identity/time invalid")
    else:
        current=datetime.strptime(a.authorization_time,"%Y-%m-%dT%H:%M:%SZ")
        times=(release.release.semantic["publication_time"],declaration.declaration_time,
               planning_authorization.authorization_time,planning_authorization.planning_time)
        if any(current < datetime.strptime(x,"%Y-%m-%dT%H:%M:%SZ") for x in times): result.append("authorization predates predecessor")
    if a.fingerprint!=compute_terminal_invocation_authorization_fingerprint(a): result.append("authorization fingerprint stale")
    if type(a.maximum_output_bytes) is not int or not 1<=a.maximum_output_bytes<=1_000_000 or type(a.timeout_seconds) is not int or not 1<=a.timeout_seconds<=30: result.append("resource bound invalid")
    if a.output_filename!="artifact/brief.html" or a.evidence_filename!="evidence/terminal-invocation-evidence.json": result.append("fixed output inventory mismatch")
    if not _safe_dir(a.output_directory) or not _safe_dir(a.authorization_ledger_directory): result.append("unsafe directory")
    return result


def _consumption_name(a): return _sha(a.identity.encode())+".terminal-invocation-consumed"
def _commitment_name(a): return a.fingerprint+".terminal-invocation-admitted"
def _commitment(a,artifact,evidence):
    return _canonical({"contract_identity":"briefforge:terminal-invocation-admission-commitment:1.0.0",
        "authorization_fingerprint":a.fingerprint,"artifact_sha256":_sha(artifact),"evidence_sha256":_sha(evidence),
        "artifact_byte_length":len(artifact),"evidence_byte_length":len(evidence)})


def _audit(plan,declaration,a,p,t,artifact):
    suffix=a.identity.split(":",1)[-1]; digest=_sha(artifact)
    payload={"contract_identity":INVOCATION_EVIDENCE_CONTRACT,"policy_identity":CONTROLLED_INVOCATION_POLICY_ID,
        "authorization_identity":a.identity,"authorization_fingerprint":a.fingerprint,
        "lifecycle_inventory_digest":a.lifecycle_inventory_digest,"plan_fingerprint":a.plan_fingerprint,
        "capability_fingerprint":a.capability_fingerprint,"successor_projection_identity":PROJECTION_IDENTITY,
        "successor_projection_version":PROJECTION_VERSION,"successor_projection_fingerprint":p.fingerprint,
        "translated_projection_fingerprint":t.fingerprint,"adapter_identity":ADAPTER_IDENTITY,
        "adapter_version":ADAPTER_VERSION,"adapter_implementation_digest":a.adapter_implementation_digest,
        "renderer_identity":RENDERER_IDENTITY,"renderer_version":RENDERER_VERSION,
        "renderer_implementation_digest":a.renderer_implementation_digest,
        "operational_authority_exclusions":[{"identity":x,"planned_count":0,"realized_count":0} for x in _FIXED_EXCLUSIONS],
        "execution_digests":[digest,digest],"execution_byte_lengths":[len(artifact),len(artifact)],
        "environment":[list(x) for x in _FIXED_ENVIRONMENT],"interpreter_flags":list(_FIXED_FLAGS),
        "external_assets":[],"network_access":"prohibited","database_access":"prohibited",
        "dynamic_callable_selection":"prohibited","invocation_outcome":"completed-deterministically",
        "semantic_conformance":"unassessed","manifest_authority":"absent","distribution_authority":"absent",
        "successful_publication":"not-asserted"}
    release=plan.bundle.one("PublicationReleaseRecord"); ready=plan.bundle.one("ReadyPresentationPackageRecord")
    return BCRPRecord("GeneratedArtifactAuditRecord",f"artifact-audit:{suffix}",PROFILE_VERSION,
        {"release_ref":release.identity,"ready_ref":ready.identity,"ready_fingerprint":ready.semantic["ready_fingerprint"],
         "plan_ref":plan.plan.identity,"renderer_capability_ref":declaration.identity,
         "artifact":{"id":f"artifact:{suffix}","filename":"brief.html","media_type":"text/html","sha256":digest,"byte_length":len(artifact)},
         "audit_links_pass":True,"invocation_time":a.authorization_time},
        [{"owner_namespace":"briefforge-terminal-controlled-renderer-invocation","name":"invocation-and-artifact-evidence",
          "version":"1.0.0","authority_ref":AUTHORITY_IDENTITY,"scope":"artifact-existence-and-invocation-audit-links-only",
          "target_refs":[release.identity,ready.identity,plan.plan.identity,declaration.identity,f"artifact:{suffix}"],
          "criticality":"required","character":"semantic","validation_contract":INVOCATION_EVIDENCE_CONTRACT,
          "preservation":"must-preserve","payload":payload}])


def _independent(*,verified_release,evidence_snapshot,lifecycle_scope,declaration,planning_authorization,verified_plan,authority_profile):
    release=verify_publication_release(verified_release.bundle,evidence_snapshot=evidence_snapshot,expected_release_fingerprint=verified_release.fingerprint.digest)
    plan=verify_renderer_compatibility_plan(verified_plan.bundle,evidence_snapshot=evidence_snapshot,lifecycle_scope=lifecycle_scope,
        declaration=declaration,authorization=planning_authorization,expected_plan_fingerprint=verified_plan.fingerprint.digest)
    projection=build_terminal_representative_projection(verified_release=release,evidence_snapshot=evidence_snapshot,
        lifecycle_scope=lifecycle_scope,declaration=declaration,planning_authorization=planning_authorization,
        verified_plan=plan,authority_profile=authority_profile)
    return release,plan,projection,adapt_terminal_projection(projection)


def _verify_bytes(artifact,evidence,*,authorization,verified_release,evidence_snapshot,lifecycle_scope,declaration,planning_authorization,verified_plan,authority_profile):
    release,plan,p,t=_independent(verified_release=verified_release,evidence_snapshot=evidence_snapshot,lifecycle_scope=lifecycle_scope,
        declaration=declaration,planning_authorization=planning_authorization,verified_plan=verified_plan,authority_profile=authority_profile)
    if _problems(authorization,p,t,release,lifecycle_scope,declaration,plan,planning_authorization): raise TerminalInvocationRejected("persisted authorization stale")
    text=evidence.decode(); bundle=_deserialize_bundle(text)
    if text!=_serialize_bundle(bundle): raise TerminalInvocationRejected("evidence not canonical")
    if len(bundle.records)!=9 or bundle.records[:8]!=plan.bundle.records: raise TerminalInvocationRejected("exact Plan predecessor closure required")
    if bundle.records[8].to_document()!=_audit(plan,declaration,authorization,p,t,artifact).to_document(): raise TerminalInvocationRejected("invocation evidence independently differs")
    if artifact!=render_representative_html(t): raise TerminalInvocationRejected("artifact differs from independently reproduced real renderer output")
    return bundle,fingerprint_bundle(bundle,domain="profile-instance",require_valid=False)


def invoke_controlled_terminal_renderer(*,verified_release,evidence_snapshot,lifecycle_scope,declaration,planning_authorization,verified_plan,authority_profile,authorization):
    fds=[]
    try:
        release,plan,p,t=_independent(verified_release=verified_release,evidence_snapshot=evidence_snapshot,lifecycle_scope=lifecycle_scope,
            declaration=declaration,planning_authorization=planning_authorization,verified_plan=verified_plan,authority_profile=authority_profile)
        problems=_problems(authorization,p,t,release,lifecycle_scope,declaration,plan,planning_authorization)
        if problems: raise TerminalInvocationRejected("; ".join(problems))
        root,artifact_path,evidence_path=_paths(authorization)
        artifact_path.parent.mkdir(exist_ok=False); evidence_path.parent.mkdir(exist_ok=False)
        if any(root.iterdir()):
            # only the exact freshly-created empty two directories may exist
            if {x.name for x in root.iterdir()}!={"artifact","evidence"}: raise TerminalInvocationRejected("output inventory unsafe")
        afd=_open_directory(artifact_path.parent); efd=_open_directory(evidence_path.parent); lfd=_open_directory(Path(authorization.authorization_ledger_directory)); fds=[afd,efd,lfd]
        if len({(os.fstat(x).st_dev,os.fstat(x).st_ino) for x in fds})!=3: raise TerminalInvocationRejected("directories must be distinct")
        _write_exclusive_at(lfd,_consumption_name(authorization),authorization.fingerprint.encode())
        artifact=render_terminal_in_isolation(p,authorization.timeout_seconds)
        if len(artifact)>authorization.maximum_output_bytes: raise TerminalInvocationRejected("artifact exceeds authorization")
        bundle=BCRPBundle(plan.bundle.profile_identity,plan.bundle.profile_version,plan.bundle.records+(_audit(plan,declaration,authorization,p,t,artifact),))
        evidence=_serialize_bundle(bundle).encode()
        _verify_bytes(artifact,evidence,authorization=authorization,verified_release=verified_release,evidence_snapshot=evidence_snapshot,
            lifecycle_scope=lifecycle_scope,declaration=declaration,planning_authorization=planning_authorization,verified_plan=verified_plan,authority_profile=authority_profile)
        _write_exclusive_at(afd,artifact_path.name,artifact); _write_exclusive_at(efd,evidence_path.name,evidence)
        persisted_artifact=_read_regular_at(afd,artifact_path.name,authorization.maximum_output_bytes); persisted_evidence=_read_regular_at(efd,evidence_path.name,10_000_000)
        reloaded,fp=_verify_bytes(persisted_artifact,persisted_evidence,authorization=authorization,verified_release=verified_release,evidence_snapshot=evidence_snapshot,
            lifecycle_scope=lifecycle_scope,declaration=declaration,planning_authorization=planning_authorization,verified_plan=verified_plan,authority_profile=authority_profile)
        _write_exclusive_at(lfd,_commitment_name(authorization),_commitment(authorization,persisted_artifact,persisted_evidence))
        return TerminalInvocationResult((),VerifiedTerminalRendererInvocation(_serialize_bundle(reloaded),persisted_artifact,persisted_evidence,artifact_path,evidence_path,fp))
    except Exception as exc: return TerminalInvocationResult((str(exc),),None)
    finally:
        for fd in fds: os.close(fd)


def verify_persisted_terminal_renderer_invocation(*,artifact_path,evidence_path,verified_release,evidence_snapshot,lifecycle_scope,declaration,planning_authorization,verified_plan,authority_profile,authorization):
    _,expected_artifact,expected_evidence=_paths(authorization)
    if artifact_path!=expected_artifact or evidence_path!=expected_evidence: raise TerminalInvocationRejected("persisted path mismatch")
    artifact=_read_regular(artifact_path,authorization.maximum_output_bytes); evidence=_read_regular(evidence_path,10_000_000)
    bundle,fp=_verify_bytes(artifact,evidence,authorization=authorization,verified_release=verified_release,evidence_snapshot=evidence_snapshot,
        lifecycle_scope=lifecycle_scope,declaration=declaration,planning_authorization=planning_authorization,verified_plan=verified_plan,authority_profile=authority_profile)
    ledger=Path(authorization.authorization_ledger_directory)
    if _read_regular(ledger/_consumption_name(authorization),4096)!=authorization.fingerprint.encode(): raise TerminalInvocationRejected("consumption mismatch")
    if _read_regular(ledger/_commitment_name(authorization),4096)!=_commitment(authorization,artifact,evidence): raise TerminalInvocationRejected("commitment mismatch")
    return VerifiedTerminalRendererInvocation(_serialize_bundle(bundle),artifact,evidence,artifact_path,evidence_path,fp)
