"""Independent semantic assessor for the fixed representative artifact."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import stat
import sys

from .bcrp.canonical import fingerprint_bundle
from .bcrp.model import BCRPBundle, BCRPRecord, Fingerprint, PROFILE_VERSION
from .bcrp.validation import validate_bundle
from .representative_controlled_invocation import (
    RepresentativeRendererInvocationAuthorization,
    representative_renderer_implementation_digest,
    verify_persisted_representative_renderer_invocation,
)
from .representative_projection import RepresentativeProjection
from .publication_release import verify_publication_release
from .renderer_compatibility_planning import verify_renderer_compatibility_plan

ASSESSOR_IMPLEMENTATION="briefforge.representative_semantic_artifact_conformance"
ASSESSOR_VERSION="2.0.0"
CONFORMANCE_EVIDENCE_CONTRACT="briefforge:semantic-artifact-conformance-evidence:2.0.0"
SEMANTIC_PROFILE_ID="briefforge-static-html-semantic-realization-profile:2.0.0"
SEMANTIC_PROFILE_VERSION="2.0.0"
CONFORMANCE_POLICY_ID="briefforge-semantic-conformance-assessment-policy:1.0.0"
ACCEPTED_ASSESSOR_IDENTITY="authority:briefforge-semantic-artifact-conformance"
ACCEPTED_ASSESSOR_OWNER="project:BriefForge"
ACCEPTED_ASSESSOR_ROLE="semantic-artifact-conformance-assessor"
OUTPUT_CLASS="standalone-representative-static-html-semantic-realization"
_EXCLUSIONS=("manifest-authority","distribution-authority","successful-publication-authority","external-assets","active-content")
_DIGEST=re.compile(r"^[0-9a-f]{64}$")
_IDENTITY=re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*$")

class RepresentativeConformanceRejected(ValueError): pass

@dataclass(frozen=True,order=True)
class RepresentativeConformanceFinding:
    code: str; location: str; message: str
@dataclass(frozen=True)
class RepresentativeExactAssessment:
    status: str
    evidence: dict|None
    findings: tuple[RepresentativeConformanceFinding,...]
    record: object|None
@dataclass(frozen=True)
class RepresentativeSemanticArtifactConformanceAuthorization:
    identity: str
    policy_identity: str
    authority_identity: str
    authority_owner: str
    authority_role: str
    authorization_time: str
    profile_identity: str
    profile_version: str
    assessor_identity: str
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
    projection_fingerprint: str
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
class VerifiedRepresentativeSemanticArtifactConformance:
    _bundle_document: str
    evidence_path: Path
    fingerprint: Fingerprint
    @classmethod
    def _admitted(cls, document, evidence_path, fingerprint):
        value=object.__new__(cls)
        object.__setattr__(value,"_bundle_document",document)
        object.__setattr__(value,"evidence_path",evidence_path)
        object.__setattr__(value,"fingerprint",fingerprint)
        return value
    @property
    def bundle(self): return _deserialize_bundle(self._bundle_document)
    @property
    def evidence(self):
        return self.bundle.one("SemanticArtifactConformanceRecord").extensions[0]["payload"]
@dataclass(frozen=True)
class RepresentativeSemanticConformanceResult:
    findings: tuple[RepresentativeConformanceFinding,...]
    verified: VerifiedRepresentativeSemanticArtifactConformance|None
    @property
    def blocked(self): return self.verified is None

def _canonical(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
def _projection_fingerprint_ok(p):
    if type(p) is not RepresentativeProjection: return False
    d=asdict(p); supplied=d.pop("fingerprint")
    return supplied==hashlib.sha256(_canonical(d)).hexdigest()
def compute_representative_conformance_authorization_fingerprint(authorization):
    if type(authorization) is not RepresentativeSemanticArtifactConformanceAuthorization: raise TypeError("exact authorization required")
    d=asdict(authorization); d.pop("fingerprint")
    return hashlib.sha256(_canonical(d)).hexdigest()
def representative_assessor_implementation_digest():
    """Bind the assessor's complete local executable closure and interpreter."""
    base=Path(__file__).parent
    names=tuple(path.relative_to(base).as_posix() for path in sorted(base.rglob("*.py")))
    measured=bytearray(b"briefforge-representative-assessor-closure-v1\0")
    for name in names:
        measured.extend(name.encode("ascii")+b"\0"+(base/name).read_bytes()+b"\0")
    measured.extend(b"interpreter\0"+_canonical({
        "executable_realpath":os.path.realpath(sys.executable),"version":sys.version,
        "implementation":sys.implementation.name,"cache_tag":sys.implementation.cache_tag})+b"\0")
    return hashlib.sha256(measured).hexdigest()
def _e(v): return escape(str(v),quote=True)
def _display(v):
    if v.value_state in {"present","explicit-zero"}:
        result=f"{_e(v.coefficient)} scale={v.scale}"
        if v.approximate: result+=f" approximate={_e(v.approximation_method)} bound={_e(v.approximation_bound)}"
        return result
    return _e(v.reason)

_EDGE_ROLES={"brief_ref","material_refs","organizing_purpose_ref","audience_refs","distribution_ref","exhibit_refs",
    "brief_purpose_ref","brief_audience_ref","children","purpose_ref","authority_ref","upstream_refs","value_ref",
    "source_ref","target_ref","primary_ref","comparison_ref","provenance_ref","snapshot_ref","target_refs","value_ids",
    "required_value_ids","unit_ref","semantic_type_ref"}

def _authority_inventory(p):
    """Assessor-owned traversal; this deliberately shares no renderer code."""
    half=len(p.audiences)//2
    entities={p.brief_identity:{"identity":p.brief_identity,"organizing_purpose_ref":p.brief_purpose.identity,
        "audience_refs":tuple(x.identity for x in p.audiences[:half]),"scope":p.brief_scope,"non_scope":p.brief_non_scope},
        p.package_identity:{"identity":p.package_identity,"brief_ref":p.brief_identity,"material_refs":p.material_identities,
        "organizing_purpose_ref":p.candidate_purpose.identity,"audience_refs":tuple(x.identity for x in p.audiences[half:]),
        "scope":p.candidate_scope,"non_scope":p.candidate_non_scope,"distribution_ref":p.distribution.identity,
        "exhibit_refs":(p.exhibit.identity,)}}
    for identity in p.material_identities: entities[identity]={"identity":identity,"required_value_ids":p.required_value_ids}
    for collection in (p.sections,p.statements,p.qualifications,p.case_bindings,p.values,p.provenance,p.evidence_snapshots,
                       p.external_references,p.units,p.semantic_types,p.obligations,p.content_authorities,p.audiences):
        for item in collection: entities[item.identity]=asdict(item)
    for item in (p.brief_purpose,p.candidate_purpose,p.exhibit,p.distribution): entities[item.identity]=asdict(item)
    fields=[]; edges=[]
    for identity in sorted(entities):
        for role,value in sorted(entities[identity].items()):
            if value is None: continue
            values=list(value) if role in _EDGE_ROLES and isinstance(value,(tuple,list)) else [value]
            if role in _EDGE_ROLES:
                for ordinal,target in enumerate(values): edges.append((f"edge:{identity}:{role}:{ordinal:04d}",identity,role,ordinal,target))
            else:
                # HTML semantic markers carry canonical JSON values. Normalize
                # tuple-backed projection fields to their measured JSON form so
                # assessor expectations compare like-for-like without borrowing
                # renderer implementation details.
                measured_value=json.loads(_canonical(value))
                fields.append((f"field:{identity}:{role}",identity,role,measured_value))
    return fields,edges

def _independently_expected_bytes(p):
    # Independently specify the fixed document and place each measured field or
    # edge in exactly one visible authoritative element.
    fields,edges=_authority_inventory(p)
    entries={key:("field",value) for key,_,_,value in fields}
    entries.update({key:("edge",target) for key,_,_,_,target in edges})
    emitted=set()
    def node(key):
        role,value=entries[key]; emitted.add(key)
        canonical=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
        return f'<span data-semantic-key="{_e(key)}" data-semantic-role="{role}">{_e(canonical)}</span>'
    def matching(prefix):
        return " ".join(node(key) for key in sorted(entries) if key.startswith(prefix) and key not in emitted)
    out=["<!doctype html>",'<html lang="en">',"<head>",'<meta charset="utf-8">',
         '<title>BriefForge representative projection</title>',"</head>","<body>","<main>",
         "<h1>BriefForge representative projection</h1>"]
    values={item.identity:item for item in p.values}; sections={item.identity:item for item in p.sections}
    statements={item.identity:item for item in p.statements}
    def emit_table():
        out.extend(('<section data-region="fixed-table"><h4>Authored paired cases</h4>',
                    "<p>"+matching(f"field:{p.exhibit.identity}:")+" "+matching(f"edge:{p.exhibit.identity}:")+"</p>",
                    '<table><thead><tr><th>case + slot</th><th>value/state</th><th>unit</th><th>type</th><th>source</th></tr></thead><tbody>'))
        for case in p.case_bindings:
            for slot,ref in (("primary",case.primary_ref),("comparison",case.comparison_ref)):
                case_prefix=f"field:{case.identity}:" if slot=="primary" else ""
                edge=f"edge:{case.identity}:{slot}_ref:0000"; value=values[ref]
                case_fields=matching(case_prefix) if case_prefix else ""
                out.append("<tr><td>"+case_fields+node(edge)+
                    "</td><td>"+matching(f"field:{value.identity}:")+"</td><td>"+
                    node(f"edge:{value.identity}:unit_ref:0000")+"</td><td>"+
                    node(f"edge:{value.identity}:semantic_type_ref:0000")+"</td><td>"+
                    node(f"edge:{value.identity}:source_ref:0000")+"</td></tr>")
        out.append("</tbody></table></section>")
    root=sections[p.section_preorder[0]]
    out.extend(('<section data-region="authored-root-section"><h2>Authored root section</h2>',
                "<p>"+matching(f"field:{root.identity}:")+" "+matching(f"edge:{root.identity}:")+"</p>"))
    for leaf_identity in root.children:
        leaf=sections[leaf_identity]
        out.extend(('<section data-region="authored-leaf-section"><h3>Authored leaf section</h3>',
                    "<p>"+matching(f"field:{leaf.identity}:")+" "+matching(f"edge:{leaf.identity}:")+"</p>"))
        for child_identity in leaf.children:
            if child_identity in statements:
                out.append('<article data-region="authored-statement">'+matching(f"field:{child_identity}:")+
                           " "+matching(f"edge:{child_identity}:")+"</article>")
            elif child_identity==p.exhibit_identity:
                emit_table()
            else:
                raise RepresentativeConformanceRejected("authority section child is outside fixed closure")
        out.append("</section>")
    out.extend(("</section>",'<section data-region="semantic-closure"><h2>Remaining governed semantic content</h2><ol>'))
    for key in sorted(entries):
        if key not in emitted: out.append(f"<li>{node(key)}</li>")
    out.extend(("</ol></section>","</main>","</body>","</html>"))
    return "\n".join(out).encode("utf-8")

class _Shape(HTMLParser):
    _TAGS={"html","head","meta","title","body","main","h1","h2","h3","h4","p","section","dl","dt","dd","ol","li","article","table","thead","tbody","tr","th","td","span"}
    _ATTRS={"lang","charset","name","content","data-role","data-region","data-audience-id","data-snapshot-id",
        "data-unit-id","data-semantic-type-id","data-exhibit-definition","data-distribution-id","data-section-id",
        "data-statement-id","data-exhibit-id","data-case-id","data-value-id","data-relation-id","data-provenance-id",
        "data-reference-id","data-obligation-id","data-authority-id","data-semantic-key","data-semantic-role"}
    def __init__(self):
        super().__init__(convert_charrefs=True); self.stack=[]; self.doctypes=0; self.roots=0
        self.semantic={}; self._capture=None
        # Assessor-owned parsed realization sequence. Comparing this sequence,
        # rather than renderer bytes, measures every presented non-marker
        # element, attribute, textual value, hierarchy, and authored order.
        self.realizations=[]
    def handle_decl(self,d):
        if d.lower()!="doctype html": raise ValueError("invalid declaration")
        self.doctypes+=1
    def handle_starttag(self,t,a):
        if t not in self._TAGS: raise ValueError("nonallowlisted HTML tag")
        names=[n for n,_ in a]
        if len(names)!=len(set(names)) or any(n not in self._ATTRS for n in names): raise ValueError("nonallowlisted HTML attribute")
        attrs=dict(a); key=attrs.get("data-semantic-key")
        if key is None:
            self.realizations.append(("element",t,tuple(sorted(a))))
        if key is not None:
            if t!="span" or key in self.semantic or attrs.get("data-semantic-role") not in {"field","edge"}: raise ValueError("invalid semantic marker")
            self._capture=[key,attrs["data-semantic-role"],""]
        if t=="html": self.roots+=1
        if t!="meta": self.stack.append(t)
    def handle_data(self,d):
        if self._capture is None and d and d.strip():
            self.realizations.append(("text",self.stack[-1] if self.stack else "",d))
        if self._capture is not None: self._capture[2]+=d
    def handle_endtag(self,t):
        if not self.stack or self.stack.pop()!=t: raise ValueError("unbalanced HTML")
        if t=="span" and self._capture is not None:
            key,role,text=self._capture
            try: value=json.loads(text)
            except Exception as exc: raise ValueError("semantic value is not canonical JSON") from exc
            if text!=_canonical(value).decode("utf-8"): raise ValueError("semantic value is not canonical")
            self.semantic[key]=(role,value); self._capture=None
    def handle_comment(self,d): raise ValueError("comments prohibited")
    def handle_pi(self,d): raise ValueError("processing instructions prohibited")
    def unknown_decl(self,d): raise ValueError("unknown declarations prohibited")

def _well_formed(b):
    if type(b) is not bytes or len(b)>1_000_000: raise ValueError("artifact type or bound invalid")
    text=b.decode("utf-8")
    if not text.startswith("<!doctype html>\n<html lang=\"en\">") or not text.endswith("</html>") or "\r" in text or "\x00" in text: raise ValueError("incomplete HTML envelope")
    parser=_Shape(); parser.feed(text); parser.close()
    if parser.stack or parser.doctypes!=1 or parser.roots!=1: raise ValueError("incomplete HTML structure")
    return parser

def _evidence(b,p):
    parser=_well_formed(b)
    fields,edges=_authority_inventory(p)
    target_requirements={}
    for mapping in p.requirement_mappings:
        for identity in mapping.target_refs: target_requirements.setdefault(identity,set()).add(mapping.requirement_id)
    expected={key:("field",value) for key,_,_,value in fields}
    expected.update({key:("edge",target) for key,_,_,_,target in edges})
    if parser.semantic != expected:
        missing=sorted(set(expected)-set(parser.semantic)); extra=sorted(set(parser.semantic)-set(expected))
        changed=sorted(k for k in set(expected)&set(parser.semantic) if expected[k]!=parser.semantic[k])
        raise RepresentativeConformanceRejected(f"measured semantic inventory mismatch: missing={missing} extra={extra} changed={changed}")
    field_entries=[]; edge_entries=[]; element_entries=[]
    for key,identity,role,value in fields:
        requirements=sorted(target_requirements.get(identity,()))
        base={"identity":identity,"field_role":role,"canonical_value":value,"requirement_ids":requirements,
              "planned_count":1,"realized_count":int(parser.semantic.get(key)==("field",value))}
        base["value_digest"]=hashlib.sha256(_canonical(base)).hexdigest(); field_entries.append(base)
        element_entries.append({"identity":key,"projection_rule":"measured-semantic-field","requirement_ids":requirements,
                                "planned_count":1,"realized_count":base["realized_count"]})
    for key,identity,role,ordinal,target in edges:
        requirements=sorted(target_requirements.get(identity,()))
        base={"source_identity":identity,"edge_role":role,"ordinal":ordinal,"target_identity":target,
              "requirement_ids":requirements,"planned_count":1,
              "realized_count":int(parser.semantic.get(key)==("edge",target))}
        base["edge_digest"]=hashlib.sha256(_canonical(base)).hexdigest(); edge_entries.append(base)
        element_entries.append({"identity":key,"projection_rule":"measured-directed-semantic-edge","requirement_ids":requirements,
                                "planned_count":1,"realized_count":base["realized_count"]})
    for authority in p.operational_authority_exclusions:
        element_entries.append({"identity":authority.identity,"projection_rule":"operational-authority-exclusion",
                                "requirement_ids":[],"planned_count":0,"realized_count":0})
    requirement_entries=[]
    for mapping in p.requirement_mappings:
        selected_fields=[x for x in field_entries if mapping.requirement_id in x["requirement_ids"]]
        selected_edges=[x for x in edge_entries if mapping.requirement_id in x["requirement_ids"]]
        item={"requirement_id":mapping.requirement_id,"outcome":"conformant",
              "planned_field_count":sum(x["planned_count"] for x in selected_fields),
              "realized_field_count":sum(x["realized_count"] for x in selected_fields),
              "planned_edge_count":sum(x["planned_count"] for x in selected_edges),
              "realized_edge_count":sum(x["realized_count"] for x in selected_edges)}
        item["accounting_digest"]=hashlib.sha256(_canonical(item)).hexdigest(); requirement_entries.append(item)
    accounting={"schema_identity":"briefforge:representative-field-edge-accounting:1.0.0",
        "requirement_ids":[x.requirement_id for x in p.requirement_mappings],"expected_requirements":requirement_entries,
        "element_entries":element_entries,"field_entries":field_entries,"edge_entries":edge_entries,
        "unplanned_realization_count":len(set(parser.semantic)-set(expected))}
    accounting["accounting_digest"]=hashlib.sha256(_canonical(accounting)).hexdigest()
    return {"assessment_status":"conforming","aggregate_verdict":"approved","artifact_sha256":hashlib.sha256(b).hexdigest(),
            "projection_fingerprint":p.fingerprint,"requirement_accounting":accounting}

def verify_exact_representative_html(artifact_bytes, projection):
    if type(projection) is not RepresentativeProjection: raise RepresentativeConformanceRejected("exact projection required")
    if not _projection_fingerprint_ok(projection): raise RepresentativeConformanceRejected("projection fingerprint is stale or forged")
    try: measured=_well_formed(artifact_bytes)
    except Exception as exc: raise RepresentativeConformanceRejected(str(exc)) from exc
    # Compare independently parsed realization inventories, not renderer bytes.
    # Complete semantic-marker equality is additionally enforced by _evidence.
    expected=_well_formed(_independently_expected_bytes(projection))
    if measured.realizations!=expected.realizations:
        raise RepresentativeConformanceRejected(
            "parsed semantic realization sequence differs from independent expectation")
    return _evidence(artifact_bytes,projection)
def assess_exact_representative_html(artifact_bytes, projection):
    try: _well_formed(artifact_bytes)
    except Exception as exc: return RepresentativeExactAssessment("indeterminate",None,(RepresentativeConformanceFinding("indeterminate","/artifact",str(exc)),),None)
    try:
        evidence=verify_exact_representative_html(artifact_bytes,projection)
        return RepresentativeExactAssessment("conforming",evidence,(),evidence)
    except Exception as exc: return RepresentativeExactAssessment("non-conforming",None,(RepresentativeConformanceFinding("nonconforming","/artifact",str(exc)),),None)

def _serialize_bundle(bundle):
    return _canonical({"profile_identity":bundle.profile_identity,"profile_version":bundle.profile_version,
                       "records":[record.to_document() for record in bundle.records]}).decode("utf-8")

def _deserialize_bundle(text):
    document=json.loads(text)
    if type(document) is not dict or set(document)!={"profile_identity","profile_version","records"} or type(document["records"]) is not list:
        raise RepresentativeConformanceRejected("conformance evidence envelope malformed")
    return BCRPBundle(document["profile_identity"],document["profile_version"],
                      tuple(BCRPRecord.from_document(item) for item in document["records"]))

def _open_directory(path):
    descriptor=os.open(path,os.O_RDONLY|getattr(os,"O_DIRECTORY",0)|getattr(os,"O_NOFOLLOW",0))
    info=os.fstat(descriptor)
    if not stat.S_ISDIR(info.st_mode): os.close(descriptor); raise RepresentativeConformanceRejected("destination is not a directory")
    return descriptor,(info.st_dev,info.st_ino)

def _write_exclusive_at(directory_fd,name,data,created=None):
    if not name or name in {".",".."} or "/" in name or os.sep in name:
        raise RepresentativeConformanceRejected("unsafe descriptor-relative filename")
    descriptor=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,"O_NOFOLLOW",0),0o600,dir_fd=directory_fd)
    opened=os.fstat(descriptor); owned_identity=(opened.st_dev,opened.st_ino)
    try:
        view=memoryview(data)
        while view:
            count=os.write(descriptor,view)
            if count<=0: raise OSError("short write")
            view=view[count:]
        os.fsync(descriptor)
        info=os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_size!=len(data): raise RepresentativeConformanceRejected("incomplete durable write")
        os.fsync(directory_fd)
        if created is not None: created[0]=owned_identity
    except BaseException:
        raise
    finally: os.close(descriptor)

def _unlink_owned_at(directory_fd,name,owned_identity):
    current=os.stat(name,dir_fd=directory_fd,follow_symlinks=False)
    if (current.st_dev,current.st_ino)!=owned_identity: return
    os.unlink(name,dir_fd=directory_fd); os.fsync(directory_fd)

def _read_regular_at(directory_fd,name,maximum):
    descriptor=os.open(name,os.O_RDONLY|getattr(os,"O_NOFOLLOW",0),dir_fd=directory_fd)
    try:
        info=os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_size>maximum: raise RepresentativeConformanceRejected("persisted evidence is unsafe or oversized")
        result=bytearray()
        while len(result)<info.st_size:
            chunk=os.read(descriptor,min(65536,info.st_size-len(result)))
            if not chunk: raise RepresentativeConformanceRejected("persisted evidence was truncated")
            result.extend(chunk)
        after=os.fstat(descriptor)
        if (after.st_dev,after.st_ino,after.st_size)!=(info.st_dev,info.st_ino,info.st_size):
            raise RepresentativeConformanceRejected("persisted evidence changed while read")
        return bytes(result)
    finally: os.close(descriptor)

def _authority_key(a): return hashlib.sha256(a.identity.encode("utf-8")).hexdigest()
def _consumption_name(a): return f"{_authority_key(a)}.conformance-assessment-consumed"
def _commitment_name(a): return f"{a.fingerprint}.conformance-admitted"
def _consumption_bytes(a):
    return _canonical({"contract_identity":"briefforge:representative-semantic-conformance-assessment-consumption:1.0.0",
                       "authorization_identity":a.identity,"authorization_fingerprint":a.fingerprint,
                       "assessment_scope":"exactly-one-semantic-assessment-act"})
def _commitment_bytes(a,evidence):
    return _canonical({"contract_identity":"briefforge:representative-semantic-conformance-admission-commitment:1.0.0",
                       "authorization_fingerprint":a.fingerprint,"artifact_sha256":a.artifact_sha256,
                       "invocation_evidence_fingerprint":a.invocation_evidence_fingerprint,
                       "conformance_evidence_sha256":hashlib.sha256(evidence).hexdigest(),
                       "conformance_evidence_byte_length":len(evidence)})

def _safe_directory(value):
    path=Path(value)
    return path.is_absolute() and str(path.resolve())==value and path.is_dir() and not path.is_symlink()

def _authorization_findings(a,*,invocation,projection,release,scope,declaration,plan,invocation_authorization,artifact):
    if type(a) is not RepresentativeSemanticArtifactConformanceAuthorization:
        return (RepresentativeConformanceFinding("missing-authorization","/authorization","exact authorization required"),)
    audit=invocation.bundle.one("GeneratedArtifactAuditRecord")
    artifact_document=audit.semantic["artifact"]
    authorities=release.bundle.one("PortablePresentationMaterialRecord").semantic.get("authorities",[])
    accepted={"id":ACCEPTED_ASSESSOR_IDENTITY,"owner_identity":ACCEPTED_ASSESSOR_OWNER,
              "role":ACCEPTED_ASSESSOR_ROLE,"scope":"one-semantic-artifact-conformance-assessment"}
    problems=[]
    if [item for item in authorities if item.get("id")==ACCEPTED_ASSESSOR_IDENTITY]!=[accepted]:
        problems.append(("unreleased-assessor-authority","/release/authorities"))
    expected={
        "policy_identity":CONFORMANCE_POLICY_ID,"authority_identity":ACCEPTED_ASSESSOR_IDENTITY,
        "authority_owner":ACCEPTED_ASSESSOR_OWNER,"authority_role":ACCEPTED_ASSESSOR_ROLE,
        "profile_identity":SEMANTIC_PROFILE_ID,"profile_version":SEMANTIC_PROFILE_VERSION,
        "assessor_identity":ACCEPTED_ASSESSOR_IDENTITY,"release_identity":release.release.identity,
        "release_fingerprint":release.fingerprint.digest,"lifecycle_inventory_digest":scope.inventory_digest,
        "plan_identity":plan.plan.identity,"plan_fingerprint":plan.fingerprint.digest,
        "capability_identity":declaration.identity,"capability_fingerprint":declaration.fingerprint,
        "invocation_authorization_identity":invocation_authorization.identity,
        "invocation_authorization_fingerprint":invocation_authorization.fingerprint,
        "invocation_evidence_fingerprint":invocation.fingerprint.digest,
        "artifact_identity":artifact_document["id"],"artifact_sha256":hashlib.sha256(artifact).hexdigest(),
        "artifact_filename":artifact_document["filename"],"artifact_media_type":artifact_document["media_type"],
        "artifact_byte_length":len(artifact),"projection_fingerprint":projection.fingerprint,
        "renderer_identity":invocation_authorization.renderer_identity,
        "renderer_version":invocation_authorization.renderer_version,
        "renderer_implementation_digest":representative_renderer_implementation_digest(),
        "assessor_implementation":ASSESSOR_IMPLEMENTATION,"assessor_version":ASSESSOR_VERSION,
        "assessor_implementation_digest":representative_assessor_implementation_digest(),
        "output_class":OUTPUT_CLASS,"maximum_artifact_bytes":invocation_authorization.maximum_output_bytes,
        "exclusions":_EXCLUSIONS,"artifact_destination":str(invocation.artifact_path),
        "invocation_evidence_destination":str(invocation.evidence_path),
    }
    problems.extend(("authorization-binding-mismatch",f"/authorization/{name}") for name,value in expected.items() if getattr(a,name,None)!=value)
    document=asdict(a)
    for name,value in document.items():
        valid=(type(value) is int if name in {"artifact_byte_length","maximum_artifact_bytes"} else
               type(value) is tuple and all(type(x) is str for x in value) if name=="exclusions" else type(value) is str)
        if not valid: problems.append(("invalid-authorization-type",f"/authorization/{name}"))
    if type(a.identity) is str and not _IDENTITY.fullmatch(a.identity): problems.append(("invalid-authorization-identity","/authorization/identity"))
    if type(a.record_identity) is str and not _IDENTITY.fullmatch(a.record_identity): problems.append(("invalid-authorization-identity","/authorization/record_identity"))
    try:
        parsed=datetime.strptime(a.authorization_time,"%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if parsed.isoformat().replace("+00:00","Z")!=a.authorization_time: raise ValueError
        predecessor_times=(release.release.semantic["publication_time"],declaration.declaration_time,
                           invocation_authorization.authorization_time,audit.semantic["invocation_time"])
        if any(parsed < datetime.strptime(value,"%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
               for value in predecessor_times):
            problems.append(("conformance-time-contradiction","/authorization/authorization_time"))
    except (KeyError,TypeError,ValueError): problems.append(("invalid-authorization-time","/authorization/authorization_time"))
    if a.fingerprint!=compute_representative_conformance_authorization_fingerprint(a) or not _DIGEST.fullmatch(a.fingerprint): problems.append(("authorization-fingerprint-mismatch","/authorization/fingerprint"))
    if not _safe_directory(a.evidence_directory): problems.append(("invalid-evidence-directory","/authorization/evidence_directory"))
    if not _safe_directory(a.commitment_ledger_directory): problems.append(("invalid-commitment-ledger","/authorization/commitment_ledger_directory"))
    if a.evidence_filename!="semantic-conformance-evidence.json": problems.append(("unauthorized-evidence-filename","/authorization/evidence_filename"))
    return tuple(RepresentativeConformanceFinding(code,location,"authorization is stale, unsafe, or contradictory") for code,location in sorted(set(problems)))

def _v2_accounting(projection, basic):
    """Convert the independently derived field/edge inventory to the fixed v2 evidence schema."""
    old=basic["requirement_accounting"]
    requirement_ids=[item.requirement_id for item in projection.requirement_mappings]
    by_value={item.identity:item for item in projection.values}
    by_qualification={item.identity:item for item in projection.qualifications}
    by_obligation={item.identity:item for item in projection.obligations}
    parent={child:section.identity for section in projection.sections for child in section.children}
    entries=[]
    def append(*,key,requirements,source,rule,role,order=-1,parent_identity="",text=b""):
        value=by_value.get(source); qualification=by_qualification.get(source); obligation=by_obligation.get(source)
        entries.append({
            "key":key,"requirement_ids":[rid for rid in requirement_ids if rid in requirements],
            "source_identity":source,"projection_rule":rule,"role":role,"planned_count":1,
            "realized_count":1,"order":order,"parent_identity":parent_identity,
            "text_sha256":hashlib.sha256(text).hexdigest(),
            "value_state":value.value_state if value else "",
            "coefficient":value.coefficient if value and value.coefficient is not None else "",
            "scale":value.scale if value and value.scale is not None else -1,
            "unit_identity":value.unit_ref if value else "",
            "qualification_target_identity":qualification.target_ref if qualification else "",
            "provenance_identity":value.source_ref if value else "",
            "obligation_target_identities":list(obligation.target_refs) if obligation else [],
            "duplication_policy":"one-shared-realization-for-overlapping-requirements",
        })
    for item in old["field_entries"]:
        append(key=f"field:{item['identity']}:{item['field_role']}",requirements=item["requirement_ids"],
               source=item["identity"],rule="semantic-field",role=item["field_role"],
               parent_identity=parent.get(item["identity"],""),text=_canonical(item["canonical_value"]))
    for item in old["edge_entries"]:
        append(key=f"edge:{item['source_identity']}:{item['edge_role']}:{item['ordinal']:04d}",
               requirements=item["requirement_ids"],source=item["source_identity"],rule="directed-semantic-edge",
               role=item["edge_role"],order=item["ordinal"],parent_identity=item["target_identity"],
               text=_canonical(item["target_identity"]))
    for authority in projection.operational_authority_exclusions:
        entry={"key":f"exclusion:{authority.identity}","requirement_ids":[],"source_identity":authority.identity,
               "projection_rule":"operational-authority-exclusion","role":"excluded-operational-authority",
               "planned_count":0,"realized_count":0,"order":-1,"parent_identity":"",
               "text_sha256":hashlib.sha256(_canonical(asdict(authority))).hexdigest(),"value_state":"",
               "coefficient":"","scale":-1,"unit_identity":"","qualification_target_identity":"",
               "provenance_identity":"","obligation_target_identities":[],
               "duplication_policy":"planned-zero-not-rendered"}
        entries.append(entry)
    entries.sort(key=lambda item:item["key"])
    expected=[]
    for rid in requirement_ids:
        subset=[item for item in entries if rid in item["requirement_ids"]]
        expected.append({"id":rid,"outcome":"conformant",
                         "planned_count":sum(item["planned_count"] for item in subset),
                         "realized_count":sum(item["realized_count"] for item in subset),
                         "element_evidence_sha256":hashlib.sha256(_canonical(subset)).hexdigest()})
    if any(item["planned_count"]<=0 or item["planned_count"]!=item["realized_count"] for item in expected):
        raise RepresentativeConformanceRejected("requirement accounting is incomplete")
    return {"profile_identity":SEMANTIC_PROFILE_ID,"profile_version":SEMANTIC_PROFILE_VERSION,
            "projection_closure_fingerprint":projection.fingerprint,"requirement_ids":requirement_ids,
            "expected_requirements":expected,"element_entries":entries,"unplanned_realization_count":0}

def _semantic_evidence(artifact,projection):
    basic=verify_exact_representative_html(artifact,projection)
    return {"assessment_status":"conforming","aggregate_verdict":"approved",
            "artifact_sha256":basic["artifact_sha256"],"projection_fingerprint":projection.fingerprint,
            "requirement_accounting":_v2_accounting(projection,basic)}

def _conformance_record(invocation,a,semantic_evidence):
    bundle=invocation.bundle; audit=bundle.one("GeneratedArtifactAuditRecord"); ready=bundle.one("ReadyPresentationPackageRecord")
    accounting=semantic_evidence["requirement_accounting"]
    payload={"contract_identity":CONFORMANCE_EVIDENCE_CONTRACT,"policy_identity":CONFORMANCE_POLICY_ID,
             "profile_identity":a.profile_identity,"profile_version":a.profile_version,
             "assessor":{"identity":a.assessor_identity,"owner":a.authority_owner,"role":a.authority_role},
             "authorization_identity":a.identity,"authorization_fingerprint":a.fingerprint,
             "release_fingerprint":a.release_fingerprint,"lifecycle_inventory_digest":a.lifecycle_inventory_digest,
             "plan_fingerprint":a.plan_fingerprint,"capability_fingerprint":a.capability_fingerprint,
             "invocation_authorization_identity":a.invocation_authorization_identity,
             "invocation_authorization_fingerprint":a.invocation_authorization_fingerprint,
             "invocation_evidence_fingerprint":a.invocation_evidence_fingerprint,
             "artifact_identity":a.artifact_identity,"artifact_sha256":a.artifact_sha256,
             "assessment_status":"conforming","requirement_accounting":accounting,
             "authority_scope":"semantic-artifact-conformance-only","manifest_authority":"absent",
             "distribution_authority":"absent","successful_publication":"not-asserted"}
    return BCRPRecord(kind="SemanticArtifactConformanceRecord",identity=a.record_identity,profile_version=PROFILE_VERSION,
        semantic={"audit_ref":audit.identity,"ready_ref":ready.identity,"audit_link_pass":True,"semantic_pass":True,
                  "evidence":{"profile":SEMANTIC_PROFILE_ID,"aggregate_verdict":"approved",
                              "requirement_count":len(accounting["requirement_ids"]),
                              "evidence_sha256":hashlib.sha256(_canonical(semantic_evidence)).hexdigest()}},
        extensions=[{"owner_namespace":"briefforge-representative-semantic-artifact-conformance",
                     "name":"semantic-realization-evidence","version":"2.0.0","authority_ref":a.authority_identity,
                     "scope":"semantic-artifact-conformance-only",
                     "target_refs":[bundle.one("PublicationReleaseRecord").identity,ready.identity,audit.identity,
                                    bundle.one("RendererCompatibilityPlanRecord").identity,
                                    bundle.one("RendererCapabilityDeclarationRecord").identity,a.artifact_identity],
                     "criticality":"required","character":"semantic","validation_contract":CONFORMANCE_EVIDENCE_CONTRACT,
                     "preservation":"must-preserve","payload":payload}])

def _verify_closure(bundle,invocation,a,semantic_evidence,path):
    kinds=("PresentationBriefRecord","PortablePresentationMaterialRecord","CandidatePresentationPackageRecord",
           "ValidationJudgmentRecord","ReadyPresentationPackageRecord","PublicationReleaseRecord",
           "RendererCapabilityDeclarationRecord","RendererCompatibilityPlanRecord","GeneratedArtifactAuditRecord",
           "SemanticArtifactConformanceRecord")
    if len(bundle.records)!=10 or tuple(record.kind for record in bundle.records)!=kinds:
        raise RepresentativeConformanceRejected("exact ten-record conformance closure required")
    if tuple(record.to_document() for record in bundle.records[:9])!=tuple(record.to_document() for record in invocation.bundle.records):
        raise RepresentativeConformanceRejected("nine-record invocation predecessor changed")
    expected_record=_conformance_record(invocation,a,semantic_evidence).to_document()
    if bundle.records[-1].to_document()!=expected_record:
        actual=bundle.records[-1].to_document()
        differing=sorted(key for key in set(actual)|set(expected_record) if actual.get(key)!=expected_record.get(key))
        if differing==["extensions"]:
            ap=actual["extensions"][0]["payload"]; ep=expected_record["extensions"][0]["payload"]
            differing=["extensions.payload."+key for key in sorted(set(ap)|set(ep)) if ap.get(key)!=ep.get(key)]
        raise RepresentativeConformanceRejected("conformance record is not independently reproducible: "+",".join(differing))
    # The exact v2 payload is reproduced above. Generic BCRP validates its
    # extension envelope but must not reinterpret downstream payload members as
    # core semantic objects.
    # BCRPRecord.to_document intentionally exposes nested semantic/extension
    # values without deep-copying them.  Generic-envelope validation must not
    # mutate the authoritative record while replacing the specialized payload.
    generic_documents=json.loads(json.dumps(
        [record.to_document() for record in bundle.records],
        ensure_ascii=False,allow_nan=False))
    generic_documents[-1]["extensions"][0]["payload"]={}
    generic_bundle=BCRPBundle(bundle.profile_identity,bundle.profile_version,
                              tuple(BCRPRecord.from_document(item) for item in generic_documents))
    generic=validate_bundle(generic_bundle,through_layer="L5")
    specialized={record.identity for record in bundle.records[3:]}
    conformance_identity=bundle.records[-1].identity
    unexpected=[finding for finding in generic.findings if not (
        (finding.layer=="L1" and finding.family=="extension-boundary" and finding.severity=="blocking"
         and finding.blocking_consequence=="all dependent processing" and finding.semantic_identity in specialized
         and finding.location=="/extensions/0"
         and finding.message=="Unknown required semantic extension cannot be processed."
         and finding.referenced_identities==())
    )]
    if unexpected:
        details="; ".join(f"{finding.family}:{finding.semantic_identity}{finding.location}:{finding.message}" for finding in unexpected)
        raise RepresentativeConformanceRejected("ten-record evidence fails generic BCRP validation: "+details)
    return VerifiedRepresentativeSemanticArtifactConformance._admitted(
        _serialize_bundle(bundle),path,fingerprint_bundle(bundle,domain="profile-instance",require_valid=False))

def _compare_projection_to_authority(p,bundle,plan):
    """Independently reconstruct every projected DTO member from record bytes."""
    brief_record=bundle.one("PresentationBriefRecord"); material_record=bundle.one("PortablePresentationMaterialRecord")
    candidate_record=bundle.one("CandidatePresentationPackageRecord")
    brief=brief_record.semantic; material=material_record.semantic; candidate=candidate_record.semantic
    section_by={item["id"]:item for item in candidate["sections"]}
    roots=[item for item in candidate["sections"] if any(child in section_by for child in item["children"])]
    if len(roots)!=1: raise RepresentativeConformanceRejected("authority section root is ambiguous")
    preorder=[roots[0]["id"],*roots[0]["children"]]
    statement_by={item["id"]:item for item in candidate["statements"]}
    statement_order=[child for sid in preorder[1:] for child in section_by[sid]["children"] if child in statement_by]
    exhibit=candidate["exhibits"][0]
    operational={"authority:briefforge-bcrp-validation","authority:briefforge-publication-release",
        "authority:briefforge-controlled-renderer-invocation","authority:briefforge-semantic-artifact-conformance",
        "authority:briefforge-publication-manifest-projector"}
    def docs(items): return [asdict(item) for item in items]
    def authority_doc(item): return {"identity":item["id"],"owner_identity":item["owner_identity"],"role":item["role"],"scope":item["scope"]}
    expected={
      "brief_identity":brief_record.identity,"material_identities":(material_record.identity,),
      "package_identity":candidate_record.identity,
      "brief_purpose":{"identity":brief["organizing_purpose"]["id"],"statement":brief["organizing_purpose"]["statement"],"brief_purpose_ref":None},
      "candidate_purpose":{"identity":candidate["organizing_purpose"]["id"],"statement":candidate["organizing_purpose"]["statement"],"brief_purpose_ref":candidate["organizing_purpose"]["brief_purpose_ref"]},
      "audiences":[{"identity":item["id"],"description":item["description"],"brief_audience_ref":None}
                   for owner in (brief,candidate) for item in sorted(owner["audiences"],key=lambda x:x["id"])],
      "sections":[{"identity":sid,"title":section_by[sid]["title"],"children":tuple(section_by[sid]["children"])} for sid in preorder],
      "statements":[dict(identity=statement_by[sid]["id"],text=statement_by[sid]["text"],posture=statement_by[sid]["posture"],
          communication_functions=tuple(statement_by[sid]["communication_functions"]),attention=statement_by[sid]["attention"],
          purpose_ref=statement_by[sid]["purpose_ref"],authority_ref=statement_by[sid]["authority_ref"],
          upstream_refs=tuple(statement_by[sid]["upstream_refs"]),value_ref=statement_by[sid].get("value_ref"),
          requires_comparison_universe=False) for sid in statement_order],
      "qualifications":[{"identity":x["id"],"kind":x["kind"],"source_ref":x["source_ref"],"target_ref":x["target_ref"],"authority_ref":x["authority_ref"]} for x in sorted(candidate["relations"],key=lambda x:x["id"])],
      "case_bindings":[{"identity":x["id"],"order":x["order"],"primary_ref":x["primary_ref"],"comparison_ref":x["comparison_ref"]} for x in sorted(exhibit["case_bindings"],key=lambda x:x["order"])],
      "provenance":[{"identity":x["id"],"citation":x["citation"],"authority_ref":x["authority_ref"]} for x in sorted(material["provenance"],key=lambda x:x["id"])],
      "evidence_snapshots":[{"identity":x["id"],"version":x["version"],"content_fingerprint":x["content_fingerprint"],"provenance_ref":x["provenance_ref"]} for x in sorted(material["evidence_snapshots"],key=lambda x:x["id"])],
      "external_references":[{"identity":x["id"],"reference_kind":x["reference_kind"],"upstream_object_identity":x["upstream_object_identity"],"snapshot_ref":x["snapshot_ref"],"provenance_ref":x["provenance_ref"],"authority_ref":x["authority_ref"]} for x in sorted(material["external_references"],key=lambda x:x["id"])],
      "units":[{"identity":x["id"],"description":x["description"]} for x in sorted(material["units"],key=lambda x:x["id"])],
      "semantic_types":[{"identity":x["id"],"description":x["description"]} for x in sorted(material["semantic_types"],key=lambda x:x["id"])],
      "obligations":[{"identity":x["id"],"kind":x["kind"],"authority_ref":x["authority_ref"],"target_refs":tuple(sorted(x["target_refs"]))} for x in sorted(candidate["obligations"],key=lambda x:x["id"])],
      "content_authorities":[authority_doc(x) for x in sorted((x for x in material["authorities"] if x["id"] not in operational),key=lambda x:x["id"])],
      "operational_authority_exclusions":[authority_doc(next(x for x in material["authorities"] if x["id"]==identity)) for identity in (
        "authority:briefforge-bcrp-validation","authority:briefforge-publication-release","authority:briefforge-controlled-renderer-invocation","authority:briefforge-semantic-artifact-conformance","authority:briefforge-publication-manifest-projector")],
    }
    expected_values=[]
    for x in sorted(material["values"],key=lambda x:x["id"]):
        payload=x.get("payload",{}); approximation=x.get("approximation",{})
        expected_values.append(dict(identity=x["id"],value_state=x["value_state"],coefficient=payload.get("coefficient"),scale=payload.get("scale"),reason=x.get("reason"),unit_ref=x["unit_ref"],semantic_type_ref=x["semantic_type_ref"],source_ref=x["source_ref"],authority_ref=x["authority_ref"],approximate=x.get("approximate",False),approximation_method=approximation.get("method"),approximation_bound=approximation.get("bound")))
    expected["values"]=expected_values
    actual={name:(docs(getattr(p,name)) if isinstance(expected_value,list) else asdict(getattr(p,name)) if isinstance(expected_value,dict) else getattr(p,name)) for name,expected_value in expected.items()}
    for name,value in expected.items():
        if actual[name]!=value: raise RepresentativeConformanceRejected(f"caller projection {name} differs from reverified authority")
    expected_exhibit={"identity":exhibit["id"],"kind":exhibit["kind"],"purpose_ref":exhibit["purpose_ref"],
                      "value_ids":tuple(sorted(exhibit["value_ids"]))}
    distribution=candidate["distribution"]
    expected_distribution={"identity":distribution["id"],"designation":distribution["designation"],
                           "authority_ref":distribution["authority_ref"]}
    requirements={item["id"]:item for item in candidate["renderer_requirements"]}
    mappings={item["requirement_id"]:item for item in json.loads(plan.mappings_document)}
    expected_mappings=[]
    for requirement_id in ("requirement:representative-section-hierarchy",
        "requirement:representative-ordered-statements","requirement:representative-exact-quantitative-values",
        "requirement:representative-qualification-attachments","requirement:representative-provenance-references",
        "requirement:representative-complete-obligations","requirement:representative-fixed-static-table"):
        requirement=requirements[requirement_id]; mapping=mappings[requirement_id]
        expected_mappings.append({"requirement_id":requirement_id,"capability_id":requirement["capability"],
            "expression_mode":mapping["selected_expression_mode"],"target_refs":tuple(requirement["target_refs"]),
            "constraints":tuple(requirement["required_constraints"]),"mandatory":requirement["mandatory"],
            "criticality":requirement["criticality"],"authority_label_refs":tuple(requirement["authority_label_refs"]),
            "caveat_refs":tuple(requirement["caveat_refs"]),
            "permitted_transformations":tuple(requirement["permitted_transformations"]),
            "fallback_refs":tuple(requirement["fallback_refs"]),"unsupported_allowed":requirement["unsupported_allowed"]})
    if asdict(p.exhibit)!=expected_exhibit or asdict(p.distribution)!=expected_distribution:
        raise RepresentativeConformanceRejected("projection exhibit or distribution differs from reverified authority")
    if [asdict(item) for item in p.requirement_mappings]!=expected_mappings:
        raise RepresentativeConformanceRejected("projection mappings differ from reverified Plan authority")
    fixed=("briefforge:representative-static-html-projection-profile:1.0.0","1.0.0",
           "renderer:representative-static-html","1.0.0","representative-static-html-renderer")
    if (p.profile_identity,p.profile_version,p.renderer_identity,p.renderer_version,p.renderer_adapter_id)!=fixed:
        raise RepresentativeConformanceRejected("projection implementation identity differs from fixed profile")
    if (p.title,p.purpose,p.audience,p.scope,p.non_scope)!=(roots[0]["title"],candidate["organizing_purpose"]["statement"],
            sorted(candidate["audiences"],key=lambda x:x["id"])[0]["description"],candidate["scope"],candidate["non_scope"]):
        raise RepresentativeConformanceRejected("projection presentation summary differs from reverified authority")
    if (p.exhibit_identity,p.output_filename,p.media_type)!=(exhibit["id"],"brief.html","text/html"):
        raise RepresentativeConformanceRejected("projection output boundary differs from fixed profile")
    if any((p.fallbacks,p.comparison_universes,p.selection_sets,p.consistency_assertions,p.state_validations)):
        raise RepresentativeConformanceRejected("projection prohibited inventory is nonempty")
    if (p.brief_scope,p.brief_non_scope,p.candidate_scope,p.candidate_non_scope)!=(brief["scope"],brief["non_scope"],candidate["scope"],candidate["non_scope"]):
        raise RepresentativeConformanceRejected("projection scope differs from reverified authority")
    if (p.section_preorder,p.case_order,p.required_value_ids)!=(tuple(preorder),tuple(x["id"] for x in sorted(exhibit["case_bindings"],key=lambda x:x["order"])),tuple(sorted(material["required_value_ids"]))):
        raise RepresentativeConformanceRejected("projection authored ordering/inventory differs from authority")


def _independent_inputs(*,artifact_path,invocation_evidence_path,evidence_snapshot,verified_release,lifecycle_scope,
                        declaration,planning_authorization,verified_plan,invocation_authorization,authority_projection):
    invocation=verify_persisted_representative_renderer_invocation(
        artifact_path=artifact_path,evidence_path=invocation_evidence_path,verified_release=verified_release,
        evidence_snapshot=evidence_snapshot,lifecycle_scope=lifecycle_scope,declaration=declaration,
        planning_authorization=planning_authorization,verified_plan=verified_plan,authorization=invocation_authorization)
    if type(authority_projection) is not RepresentativeProjection or not _projection_fingerprint_ok(authority_projection):
        raise RepresentativeConformanceRejected("exact governed projection required for authority traversal")
    release=verify_publication_release(verified_release.bundle,evidence_snapshot=evidence_snapshot,
        expected_release_fingerprint=verified_release.fingerprint.digest)
    plan=verify_renderer_compatibility_plan(verified_plan.bundle,evidence_snapshot=evidence_snapshot,
        lifecycle_scope=lifecycle_scope,declaration=declaration,authorization=planning_authorization,
        expected_plan_fingerprint=verified_plan.fingerprint.digest)
    closure=hashlib.sha256(_canonical([r.to_document() for r in release.bundle.records[:3]])).hexdigest()
    if (authority_projection.release_fingerprint!=release.fingerprint.digest or
        authority_projection.plan_fingerprint!=plan.fingerprint.digest or
        authority_projection.content_closure_fingerprint!=closure or
        invocation_authorization.projection_fingerprint!=authority_projection.fingerprint):
        raise RepresentativeConformanceRejected("projection differs from independently traversed BCRP authority")
    _compare_projection_to_authority(authority_projection,release.bundle,plan)
    _authority_inventory(authority_projection)
    return invocation,authority_projection,invocation.artifact_bytes

def assess_representative_semantic_artifact_conformance(*,artifact_path,invocation_evidence_path,evidence_snapshot,
        verified_release,lifecycle_scope,declaration,planning_authorization,verified_plan,invocation_authorization,
        authorization,projection=None,invocation_evidence_fingerprint=None):
    try:
        invocation,derived,artifact=_independent_inputs(artifact_path=artifact_path,
            invocation_evidence_path=invocation_evidence_path,evidence_snapshot=evidence_snapshot,
            verified_release=verified_release,lifecycle_scope=lifecycle_scope,declaration=declaration,
            planning_authorization=planning_authorization,verified_plan=verified_plan,
            invocation_authorization=invocation_authorization,authority_projection=projection)
    except Exception as exc:
        return RepresentativeSemanticConformanceResult((RepresentativeConformanceFinding("upstream-reverification-failed","/inputs",str(exc)),),None)
    if projection is not None and (type(projection) is not RepresentativeProjection or projection.fingerprint!=derived.fingerprint):
        return RepresentativeSemanticConformanceResult((RepresentativeConformanceFinding("forged-projection","/inputs/projection","caller projection differs from governed derivation"),),None)
    if invocation_evidence_fingerprint is not None:
        supplied=getattr(invocation_evidence_fingerprint,"digest",invocation_evidence_fingerprint)
        if supplied!=invocation.fingerprint.digest:
            return RepresentativeSemanticConformanceResult((RepresentativeConformanceFinding("stale-invocation-fingerprint","/inputs/invocation_evidence_fingerprint","fingerprint differs from persisted invocation"),),None)
    findings=_authorization_findings(authorization,invocation=invocation,projection=derived,release=verified_release,
        scope=lifecycle_scope,declaration=declaration,plan=verified_plan,
        invocation_authorization=invocation_authorization,artifact=artifact)
    if findings: return RepresentativeSemanticConformanceResult(findings,None)
    evidence_fd=ledger_fd=-1
    try:
        evidence_fd,evidence_identity=_open_directory(Path(authorization.evidence_directory))
        ledger_fd,ledger_identity=_open_directory(Path(authorization.commitment_ledger_directory))
        _write_exclusive_at(ledger_fd,_consumption_name(authorization),_consumption_bytes(authorization)); os.fsync(ledger_fd)
    except Exception as exc:
        if evidence_fd>=0: os.close(evidence_fd)
        if ledger_fd>=0: os.close(ledger_fd)
        code=("assessment-authorization-identity-consumed" if isinstance(exc,FileExistsError)
              else "assessment-authorization-consumed")
        return RepresentativeSemanticConformanceResult((RepresentativeConformanceFinding(code,"/authorization/identity",str(exc)),),None)
    try: semantic_evidence=_semantic_evidence(artifact,derived)
    except Exception as exc:
        os.close(evidence_fd); os.close(ledger_fd)
        status="indeterminate" if "HTML" in str(exc) or "artifact" in str(exc) else "nonconforming"
        return RepresentativeSemanticConformanceResult((RepresentativeConformanceFinding(status,"/artifact",str(exc)),),None)
    path=Path(authorization.evidence_directory)/authorization.evidence_filename
    bundle=BCRPBundle(invocation.bundle.profile_identity,invocation.bundle.profile_version,
                      invocation.bundle.records+(_conformance_record(invocation,authorization,semantic_evidence),))
    try: verified=_verify_closure(bundle,invocation,authorization,semantic_evidence,path)
    except Exception as exc:
        os.close(evidence_fd); os.close(ledger_fd)
        return RepresentativeSemanticConformanceResult((RepresentativeConformanceFinding("conformance-closure-failed","/closure",str(exc)),),None)
    evidence=verified._bundle_document.encode("utf-8"); evidence_state=[False]; commitment_state=[False]
    try:
        _write_exclusive_at(evidence_fd,authorization.evidence_filename,evidence,evidence_state)
        if (os.fstat(evidence_fd).st_dev,os.fstat(evidence_fd).st_ino)!=evidence_identity or (os.fstat(ledger_fd).st_dev,os.fstat(ledger_fd).st_ino)!=ledger_identity:
            raise RepresentativeConformanceRejected("authorized directory identity changed")
        for pathname,expected_identity in ((Path(authorization.evidence_directory),evidence_identity),
                                           (Path(authorization.commitment_ledger_directory),ledger_identity)):
            check,actual_identity=_open_directory(pathname)
            os.close(check)
            if actual_identity!=expected_identity:
                raise RepresentativeConformanceRejected("authorized directory identity changed")
        persisted=_read_regular_at(evidence_fd,authorization.evidence_filename,8*1024*1024)
        try: persisted_text=persisted.decode("utf-8")
        except UnicodeDecodeError as exc: raise RepresentativeConformanceRejected("evidence is not UTF-8") from exc
        persisted_bundle=_deserialize_bundle(persisted_text)
        if persisted_text!=_serialize_bundle(persisted_bundle):
            raise RepresentativeConformanceRejected("evidence is not canonical")
        reloaded=_verify_closure(persisted_bundle,invocation,authorization,semantic_evidence,path)
        _write_exclusive_at(ledger_fd,_commitment_name(authorization),
                            _commitment_bytes(authorization,persisted),commitment_state)
        return RepresentativeSemanticConformanceResult((),reloaded)
    except Exception as exc:
        # Uncommitted evidence is retained but unusable.  Admission is written
        # last, avoiding destructive rollback races with replaced pathnames.
        return RepresentativeSemanticConformanceResult((RepresentativeConformanceFinding("conformance-persistence-failed","/evidence",str(exc)),),None)
    finally:
        if evidence_fd>=0: os.close(evidence_fd)
        if ledger_fd>=0: os.close(ledger_fd)

def verify_persisted_representative_semantic_artifact_conformance(*,artifact_path,invocation_evidence_path,
        evidence_snapshot,verified_release,lifecycle_scope,declaration,planning_authorization,verified_plan,
        invocation_authorization,authorization,projection=None,invocation_evidence_fingerprint=None):
    invocation,derived,artifact=_independent_inputs(artifact_path=artifact_path,
        invocation_evidence_path=invocation_evidence_path,evidence_snapshot=evidence_snapshot,
        verified_release=verified_release,lifecycle_scope=lifecycle_scope,declaration=declaration,
        planning_authorization=planning_authorization,verified_plan=verified_plan,
        invocation_authorization=invocation_authorization,authority_projection=projection)
    if projection is not None and projection.fingerprint!=derived.fingerprint: raise RepresentativeConformanceRejected("caller projection differs from governed derivation")
    supplied=getattr(invocation_evidence_fingerprint,"digest",invocation_evidence_fingerprint)
    if supplied is not None and supplied!=invocation.fingerprint.digest: raise RepresentativeConformanceRejected("invocation fingerprint mismatch")
    if _authorization_findings(authorization,invocation=invocation,projection=derived,release=verified_release,
            scope=lifecycle_scope,declaration=declaration,plan=verified_plan,
            invocation_authorization=invocation_authorization,artifact=artifact):
        raise RepresentativeConformanceRejected("persisted conformance authorization is stale")
    semantic_evidence=_semantic_evidence(artifact,derived); path=Path(authorization.evidence_directory)/authorization.evidence_filename
    evidence_fd,evidence_identity=_open_directory(path.parent); ledger_fd,ledger_identity=_open_directory(Path(authorization.commitment_ledger_directory))
    try:
        evidence=_read_regular_at(evidence_fd,path.name,8*1024*1024)
        consumption=_read_regular_at(ledger_fd,_consumption_name(authorization),4096)
        commitment=_read_regular_at(ledger_fd,_commitment_name(authorization),4096)
        if (os.fstat(evidence_fd).st_dev,os.fstat(evidence_fd).st_ino)!=evidence_identity or (os.fstat(ledger_fd).st_dev,os.fstat(ledger_fd).st_ino)!=ledger_identity:
            raise RepresentativeConformanceRejected("authorized directory identity changed")
    finally: os.close(evidence_fd); os.close(ledger_fd)
    try: text=evidence.decode("utf-8")
    except UnicodeDecodeError as exc: raise RepresentativeConformanceRejected("evidence is not UTF-8") from exc
    bundle=_deserialize_bundle(text)
    if text!=_serialize_bundle(bundle): raise RepresentativeConformanceRejected("evidence is not canonical")
    verified=_verify_closure(bundle,invocation,authorization,semantic_evidence,path)
    if consumption!=_consumption_bytes(authorization) or commitment!=_commitment_bytes(authorization,evidence):
        raise RepresentativeConformanceRejected("assessment consumption or admission commitment mismatch")
    return verified
