"""Independent parsed semantic conformance for the terminal-profile successor."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any

from briefforge.bcrp.canonical import fingerprint_bundle
from briefforge.bcrp.model import BCRPBundle, BCRPRecord, Fingerprint, PROFILE_VERSION
from briefforge.representative_controlled_invocation import (
    _deserialize_bundle, _open_directory, _read_regular, _read_regular_at, _serialize_bundle, _write_exclusive_at,
    representative_renderer_implementation_digest,
)
# This is an assessor dependency, not a renderer oracle. _well_formed parses the
# supplied bytes and _authority_inventory traverses the governed DTO independently.
from briefforge import representative_semantic_conformance as independent_parser

from .controlled_invocation import (
    TerminalRendererInvocationAuthorization, verify_persisted_terminal_renderer_invocation,
)
from .profile import TERMINAL_OPERATIONAL_IDENTITIES, TerminalAuthorityProfile
from .projection import (
    ADAPTER_IDENTITY, ADAPTER_VERSION, PROJECTION_IDENTITY, PROJECTION_VERSION,
    RENDERER_IDENTITY, RENDERER_VERSION, TerminalRepresentativeProjection,
    build_terminal_representative_projection, verify_terminal_projection,
)
from .renderer_adapter import adapt_terminal_projection, adapter_source_digest

ASSESSOR_IMPLEMENTATION="briefforge_terminal_profile.semantic_conformance"
ASSESSOR_VERSION="1.0.0"
SEMANTIC_PROFILE_ID="briefforge:terminal-static-html-semantic-realization-profile:1.0.0"
SEMANTIC_PROFILE_VERSION="1.0.0"
CONFORMANCE_POLICY_ID="briefforge-terminal-semantic-conformance-assessment-policy:1.0.0"
CONFORMANCE_EVIDENCE_CONTRACT="briefforge:terminal-semantic-artifact-conformance-evidence:1.0.0"
AUTHORITY_IDENTITY="authority:briefforge-semantic-artifact-conformance"
AUTHORITY_OWNER="project:BriefForge"
AUTHORITY_ROLE="semantic-artifact-conformance-assessor"
OUTPUT_CLASS="standalone-terminal-representative-static-html-semantic-realization"
EXCLUSIONS=("manifest-authority","distribution-authority","delivery-authority","deployment-authority",
            "technical-publication-authority","successful-publication-authority","external-assets","active-content")
_ID=re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*$")

class TerminalConformanceRejected(ValueError): pass

@dataclass(frozen=True,order=True)
class TerminalConformanceFinding:
    code: str; location: str; message: str

@dataclass(frozen=True)
class TerminalSemanticArtifactConformanceAuthorization:
    identity: str
    policy_identity: str
    authority_identity: str
    authority_owner: str
    authority_role: str
    authorization_time: str
    profile_identity: str
    profile_version: str
    release_identity: str
    release_fingerprint: str
    lifecycle_inventory_digest: str
    plan_identity: str
    plan_fingerprint: str
    capability_identity: str
    capability_fingerprint: str
    invocation_authorization_identity: str
    invocation_authorization_fingerprint: str
    invocation_evidence_fingerprint: str
    artifact_identity: str
    artifact_sha256: str
    artifact_filename: str
    artifact_media_type: str
    artifact_byte_length: int
    successor_projection_fingerprint: str
    translated_projection_fingerprint: str
    adapter_identity: str
    adapter_version: str
    adapter_implementation_digest: str
    renderer_identity: str
    renderer_version: str
    renderer_implementation_digest: str
    assessor_implementation: str
    assessor_version: str
    assessor_implementation_digest: str
    output_class: str
    maximum_artifact_bytes: int
    exclusions: tuple[str,...]
    artifact_destination: str
    invocation_evidence_destination: str
    evidence_directory: str
    evidence_filename: str
    commitment_ledger_directory: str
    record_identity: str
    fingerprint: str

@dataclass(frozen=True,init=False)
class VerifiedTerminalSemanticArtifactConformance:
    _bundle_document: str; evidence_path: Path; fingerprint: Fingerprint
    @classmethod
    def _make(cls,text,path,fp):
        value=object.__new__(cls); object.__setattr__(value,"_bundle_document",text)
        object.__setattr__(value,"evidence_path",path); object.__setattr__(value,"fingerprint",fp); return value
    @property
    def bundle(self): return _deserialize_bundle(self._bundle_document)
    @property
    def evidence(self): return self.bundle.records[-1].extensions[0]["payload"]

@dataclass(frozen=True)
class TerminalSemanticConformanceResult:
    findings: tuple[TerminalConformanceFinding,...]
    verified: VerifiedTerminalSemanticArtifactConformance|None
    @property
    def blocked(self): return self.verified is None


def _canonical(value: Any): return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
def _sha(value: bytes): return hashlib.sha256(value).hexdigest()

def compute_terminal_conformance_authorization_fingerprint(a):
    if type(a) is not TerminalSemanticArtifactConformanceAuthorization: raise TypeError("exact terminal conformance authorization required")
    document=asdict(a); document.pop("fingerprint"); return _sha(_canonical(document))

def terminal_assessor_implementation_digest():
    """Explicit dependency-aware assessor closure (parser, projection and adapter)."""
    files=(Path(__file__),Path(__file__).with_name("controlled_invocation.py"),
           Path(__file__).with_name("profile.py"),Path(__file__).with_name("projection.py"),
           Path(__file__).with_name("renderer_adapter.py"),Path(independent_parser.__file__))
    measured=bytearray(b"briefforge-terminal-assessor-closure-v1\0")
    for path in files: measured.extend(path.name.encode()+b"\0"+path.read_bytes()+b"\0")
    # The historical assessor digest closes its own complete source dependency
    # tree and exact interpreter; bind that closure as an explicit dependency.
    measured.extend(independent_parser.representative_assessor_implementation_digest().encode()+b"\0")
    return _sha(bytes(measured))


def _independent_projection(*,verified_release,evidence_snapshot,lifecycle_scope,declaration,planning_authorization,verified_plan,authority_profile):
    return build_terminal_representative_projection(verified_release=verified_release,evidence_snapshot=evidence_snapshot,
        lifecycle_scope=lifecycle_scope,declaration=declaration,planning_authorization=planning_authorization,
        verified_plan=verified_plan,authority_profile=authority_profile)


def verify_exact_terminal_html(artifact_bytes,projection):
    """Parse every HTML realization and compare with independently reconstructed semantics."""
    if type(projection) is not TerminalRepresentativeProjection: raise TerminalConformanceRejected("exact successor projection required")
    verify_terminal_projection(projection)
    translated=adapt_terminal_projection(projection)
    try:
        measured=independent_parser._well_formed(artifact_bytes)
        expected=independent_parser._well_formed(independent_parser._independently_expected_bytes(translated))
        if measured.realizations!=expected.realizations:
            raise TerminalConformanceRejected("visible semantic realization differs from independent expectation")
        basic=independent_parser._evidence(artifact_bytes,translated)
    except Exception as exc: raise TerminalConformanceRejected(str(exc)) from exc
    accounting=independent_parser._v2_accounting(translated,basic)
    exclusions=[x for x in accounting["element_entries"] if x["projection_rule"]=="operational-authority-exclusion"]
    if {x["source_identity"] for x in exclusions}!=set(TERMINAL_OPERATIONAL_IDENTITIES) or len(exclusions)!=8 or any(x["planned_count"] or x["realized_count"] for x in exclusions):
        raise TerminalConformanceRejected("all eight operational authorities require exact planned-zero accounting")
    accounting["profile_identity"]=SEMANTIC_PROFILE_ID; accounting["profile_version"]=SEMANTIC_PROFILE_VERSION
    accounting["projection_closure_fingerprint"]=projection.fingerprint
    return {"assessment_status":"conforming","aggregate_verdict":"approved","artifact_sha256":_sha(artifact_bytes),
        "successor_projection_fingerprint":projection.fingerprint,"translated_projection_fingerprint":translated.fingerprint,
        "adapter_identity":ADAPTER_IDENTITY,"adapter_version":ADAPTER_VERSION,
        "adapter_implementation_digest":adapter_source_digest(),"renderer_identity":RENDERER_IDENTITY,
        "renderer_version":RENDERER_VERSION,"renderer_implementation_digest":representative_renderer_implementation_digest(),
        "requirement_accounting":accounting}


def _safe_dir(text):
    path=Path(text); return path.is_absolute() and str(path.resolve())==text and path.is_dir() and not path.is_symlink()
def _consumption_name(a): return _sha(a.identity.encode())+".terminal-conformance-consumed"
def _commitment_name(a): return a.fingerprint+".terminal-conformance-admitted"
def _consumption(a): return _canonical({"contract_identity":"briefforge:terminal-conformance-consumption:1.0.0","authorization_identity":a.identity,"authorization_fingerprint":a.fingerprint})
def _commitment(a,evidence): return _canonical({"contract_identity":"briefforge:terminal-conformance-admission:1.0.0","authorization_fingerprint":a.fingerprint,"evidence_sha256":_sha(evidence),"evidence_byte_length":len(evidence)})


def _authorization_findings(a,invocation,p,t,release,scope,declaration,plan,ia,artifact):
    if type(a) is not TerminalSemanticArtifactConformanceAuthorization: return ["exact authorization required"]
    audit=invocation.bundle.records[-1]; ad=audit.semantic["artifact"]
    expected={"policy_identity":CONFORMANCE_POLICY_ID,"authority_identity":AUTHORITY_IDENTITY,"authority_owner":AUTHORITY_OWNER,
      "authority_role":AUTHORITY_ROLE,"profile_identity":SEMANTIC_PROFILE_ID,"profile_version":SEMANTIC_PROFILE_VERSION,
      "release_identity":release.release.identity,"release_fingerprint":release.fingerprint.digest,"lifecycle_inventory_digest":scope.inventory_digest,
      "plan_identity":plan.plan.identity,"plan_fingerprint":plan.fingerprint.digest,"capability_identity":declaration.identity,
      "capability_fingerprint":declaration.fingerprint,"invocation_authorization_identity":ia.identity,
      "invocation_authorization_fingerprint":ia.fingerprint,"invocation_evidence_fingerprint":invocation.fingerprint.digest,
      "artifact_identity":ad["id"],"artifact_sha256":_sha(artifact),"artifact_filename":ad["filename"],
      "artifact_media_type":ad["media_type"],"artifact_byte_length":len(artifact),"successor_projection_fingerprint":p.fingerprint,
      "translated_projection_fingerprint":t.fingerprint,"adapter_identity":ADAPTER_IDENTITY,"adapter_version":ADAPTER_VERSION,
      "adapter_implementation_digest":adapter_source_digest(),"renderer_identity":RENDERER_IDENTITY,"renderer_version":RENDERER_VERSION,
      "renderer_implementation_digest":representative_renderer_implementation_digest(),"assessor_implementation":ASSESSOR_IMPLEMENTATION,
      "assessor_version":ASSESSOR_VERSION,"assessor_implementation_digest":terminal_assessor_implementation_digest(),
      "output_class":OUTPUT_CLASS,"maximum_artifact_bytes":ia.maximum_output_bytes,"exclusions":EXCLUSIONS,
      "artifact_destination":str(invocation.artifact_path),"invocation_evidence_destination":str(invocation.evidence_path)}
    result=[f"{name} binding mismatch" for name,value in expected.items() if getattr(a,name,None)!=value]
    if not _ID.fullmatch(a.identity or "") or not _ID.fullmatch(a.record_identity or ""): result.append("identity invalid")
    try:
        now=datetime.strptime(a.authorization_time,"%Y-%m-%dT%H:%M:%SZ")
        if now<datetime.strptime(ia.authorization_time,"%Y-%m-%dT%H:%M:%SZ"): result.append("authorization predates invocation")
    except Exception: result.append("time invalid")
    if a.fingerprint!=compute_terminal_conformance_authorization_fingerprint(a): result.append("fingerprint stale")
    if not _safe_dir(a.evidence_directory) or not _safe_dir(a.commitment_ledger_directory): result.append("unsafe directory")
    if a.evidence_filename!="terminal-semantic-conformance-evidence.json": result.append("filename mismatch")
    return result


def _record(invocation,a,semantic):
    audit=invocation.bundle.records[-1]; ready=invocation.bundle.one("ReadyPresentationPackageRecord")
    payload={"contract_identity":CONFORMANCE_EVIDENCE_CONTRACT,"policy_identity":CONFORMANCE_POLICY_ID,
      "profile_identity":SEMANTIC_PROFILE_ID,"profile_version":SEMANTIC_PROFILE_VERSION,
      "assessor":{"identity":AUTHORITY_IDENTITY,"owner":AUTHORITY_OWNER,"role":AUTHORITY_ROLE,
                  "implementation":ASSESSOR_IMPLEMENTATION,"version":ASSESSOR_VERSION,"implementation_digest":a.assessor_implementation_digest},
      "authorization_identity":a.identity,"authorization_fingerprint":a.fingerprint,"release_fingerprint":a.release_fingerprint,
      "lifecycle_inventory_digest":a.lifecycle_inventory_digest,"plan_fingerprint":a.plan_fingerprint,
      "capability_fingerprint":a.capability_fingerprint,"invocation_authorization_identity":a.invocation_authorization_identity,
      "invocation_authorization_fingerprint":a.invocation_authorization_fingerprint,"invocation_evidence_fingerprint":a.invocation_evidence_fingerprint,
      "artifact_identity":a.artifact_identity,"artifact_sha256":a.artifact_sha256,"successor_projection_fingerprint":a.successor_projection_fingerprint,
      "translated_projection_fingerprint":a.translated_projection_fingerprint,"adapter_identity":a.adapter_identity,
      "adapter_version":a.adapter_version,"adapter_implementation_digest":a.adapter_implementation_digest,
      "renderer_identity":a.renderer_identity,"renderer_version":a.renderer_version,"renderer_implementation_digest":a.renderer_implementation_digest,
      "assessment_status":"conforming","requirement_accounting":semantic["requirement_accounting"],
      "operational_authority_realization":"all-eight-planned-zero","authority_scope":"semantic-artifact-conformance-only",
      "manifest_authority":"absent","distribution_authority":"absent","successful_publication":"not-asserted"}
    return BCRPRecord("SemanticArtifactConformanceRecord",a.record_identity,PROFILE_VERSION,
      {"audit_ref":audit.identity,"ready_ref":ready.identity,"audit_link_pass":True,"semantic_pass":True,
       "evidence":{"profile":SEMANTIC_PROFILE_ID,"aggregate_verdict":"approved","requirement_count":7,"evidence_sha256":_sha(_canonical(semantic))}},
      [{"owner_namespace":"briefforge-terminal-semantic-artifact-conformance","name":"semantic-realization-evidence","version":"1.0.0",
        "authority_ref":AUTHORITY_IDENTITY,"scope":"semantic-artifact-conformance-only",
        "target_refs":[audit.identity,ready.identity,a.artifact_identity],"criticality":"required","character":"semantic",
        "validation_contract":CONFORMANCE_EVIDENCE_CONTRACT,"preservation":"must-preserve","payload":payload}])


def _verify_closure(bundle,invocation,a,semantic,path):
    if len(bundle.records)!=10 or bundle.records[:9]!=invocation.bundle.records: raise TerminalConformanceRejected("exact invocation predecessor closure required")
    if bundle.records[-1].to_document()!=_record(invocation,a,semantic).to_document(): raise TerminalConformanceRejected("conformance evidence differs from independent reproduction")
    return VerifiedTerminalSemanticArtifactConformance._make(_serialize_bundle(bundle),path,fingerprint_bundle(bundle,domain="profile-instance",require_valid=False))


def _inputs(*,artifact_path,invocation_evidence_path,evidence_snapshot,verified_release,lifecycle_scope,declaration,planning_authorization,verified_plan,authority_profile,invocation_authorization,projection):
    invocation=verify_persisted_terminal_renderer_invocation(artifact_path=artifact_path,evidence_path=invocation_evidence_path,
      verified_release=verified_release,evidence_snapshot=evidence_snapshot,lifecycle_scope=lifecycle_scope,declaration=declaration,
      planning_authorization=planning_authorization,verified_plan=verified_plan,authority_profile=authority_profile,authorization=invocation_authorization)
    derived=_independent_projection(verified_release=verified_release,evidence_snapshot=evidence_snapshot,lifecycle_scope=lifecycle_scope,
      declaration=declaration,planning_authorization=planning_authorization,verified_plan=verified_plan,authority_profile=authority_profile)
    if type(projection) is not TerminalRepresentativeProjection or projection!=derived: raise TerminalConformanceRejected("caller projection differs from independently reconstructed successor truth")
    return invocation,derived,adapt_terminal_projection(derived),invocation.artifact_bytes


def assess_terminal_semantic_artifact_conformance(*,artifact_path,invocation_evidence_path,evidence_snapshot,verified_release,lifecycle_scope,declaration,planning_authorization,verified_plan,authority_profile,invocation_authorization,authorization,projection,invocation_evidence_fingerprint=None):
    try:
      invocation,p,t,artifact=_inputs(artifact_path=artifact_path,invocation_evidence_path=invocation_evidence_path,evidence_snapshot=evidence_snapshot,
        verified_release=verified_release,lifecycle_scope=lifecycle_scope,declaration=declaration,planning_authorization=planning_authorization,
        verified_plan=verified_plan,authority_profile=authority_profile,invocation_authorization=invocation_authorization,projection=projection)
      supplied=getattr(invocation_evidence_fingerprint,"digest",invocation_evidence_fingerprint)
      if supplied is not None and supplied!=invocation.fingerprint.digest: raise TerminalConformanceRejected("stale invocation fingerprint")
      problems=_authorization_findings(authorization,invocation,p,t,verified_release,lifecycle_scope,declaration,verified_plan,invocation_authorization,artifact)
      if problems: raise TerminalConformanceRejected("; ".join(problems))
      semantic=verify_exact_terminal_html(artifact,p)
      efd=_open_directory(Path(authorization.evidence_directory)); lfd=_open_directory(Path(authorization.commitment_ledger_directory))
      try:
        _write_exclusive_at(lfd,_consumption_name(authorization),_consumption(authorization))
        path=Path(authorization.evidence_directory)/authorization.evidence_filename
        bundle=BCRPBundle(invocation.bundle.profile_identity,invocation.bundle.profile_version,invocation.bundle.records+(_record(invocation,authorization,semantic),))
        verified=_verify_closure(bundle,invocation,authorization,semantic,path); evidence=verified._bundle_document.encode()
        _write_exclusive_at(efd,path.name,evidence); persisted=_read_regular_at(efd,path.name,10_000_000)
        parsed=_deserialize_bundle(persisted.decode())
        if persisted.decode()!=_serialize_bundle(parsed): raise TerminalConformanceRejected("evidence not canonical")
        reloaded=_verify_closure(parsed,invocation,authorization,semantic,path)
        _write_exclusive_at(lfd,_commitment_name(authorization),_commitment(authorization,persisted))
        return TerminalSemanticConformanceResult((),reloaded)
      finally: os.close(efd); os.close(lfd)
    except Exception as exc: return TerminalSemanticConformanceResult((TerminalConformanceFinding("blocked","/assessment",str(exc)),),None)


def verify_persisted_terminal_semantic_artifact_conformance(*,artifact_path,invocation_evidence_path,evidence_snapshot,verified_release,lifecycle_scope,declaration,planning_authorization,verified_plan,authority_profile,invocation_authorization,authorization,projection,invocation_evidence_fingerprint=None):
    invocation,p,t,artifact=_inputs(artifact_path=artifact_path,invocation_evidence_path=invocation_evidence_path,evidence_snapshot=evidence_snapshot,
      verified_release=verified_release,lifecycle_scope=lifecycle_scope,declaration=declaration,planning_authorization=planning_authorization,
      verified_plan=verified_plan,authority_profile=authority_profile,invocation_authorization=invocation_authorization,projection=projection)
    supplied=getattr(invocation_evidence_fingerprint,"digest",invocation_evidence_fingerprint)
    if supplied is not None and supplied!=invocation.fingerprint.digest: raise TerminalConformanceRejected("stale invocation fingerprint")
    if _authorization_findings(authorization,invocation,p,t,verified_release,lifecycle_scope,declaration,verified_plan,invocation_authorization,artifact): raise TerminalConformanceRejected("authorization stale")
    semantic=verify_exact_terminal_html(artifact,p); path=Path(authorization.evidence_directory)/authorization.evidence_filename
    evidence=_read_regular(path,10_000_000); bundle=_deserialize_bundle(evidence.decode())
    if evidence.decode()!=_serialize_bundle(bundle): raise TerminalConformanceRejected("evidence not canonical")
    verified=_verify_closure(bundle,invocation,authorization,semantic,path); ledger=Path(authorization.commitment_ledger_directory)
    if _read_regular(ledger/_consumption_name(authorization),4096)!=_consumption(authorization) or _read_regular(ledger/_commitment_name(authorization),4096)!=_commitment(authorization,evidence): raise TerminalConformanceRejected("consumption or commitment mismatch")
    return verified
