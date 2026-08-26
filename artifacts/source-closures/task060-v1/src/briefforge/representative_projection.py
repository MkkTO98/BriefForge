"""Fixed representative projection from independently verified BCRP authority."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from typing import Any

from .publication_release import VerifiedPublicationRelease, verify_publication_release
from .renderer_compatibility_planning import (
    LifecyclePlanningScope, PlanningAuthorization, RendererCapabilityDeclaration,
    VerifiedRendererCompatibilityPlan, verify_renderer_compatibility_plan,
)

PROJECTION_PROFILE_ID = "briefforge:representative-static-html-projection-profile:1.0.0"
PROJECTION_PROFILE_VERSION = "1.0.0"
RENDERER_IDENTITY = "renderer:representative-static-html"
RENDERER_VERSION = "1.0.0"
RENDERER_ADAPTER_ID = "representative-static-html-renderer"
_GLOBAL = "constraint:representative-static-html-profile-1.0.0"
_RULES = (
    ("section-hierarchy", "fixed-two-level-section-hierarchy"),
    ("ordered-statements", "full-text-ordered-statements"),
    ("exact-quantitative-values", "exact-decimal-value-preservation"),
    ("qualification-attachments", "statement-targeted-qualification-edges"),
    ("provenance-references", "offline-complete-provenance"),
    ("complete-obligations", "complete-obligation-edges"),
    ("fixed-static-table", "fixed-five-column-paired-case-table"),
)
_OPERATIONAL = (
    ("authority:briefforge-bcrp-validation", "validation-authority", "BCRP-L0-L6"),
    ("authority:briefforge-publication-release", "publication-release-authority", "fixed-evidence-publication-release"),
    ("authority:briefforge-controlled-renderer-invocation", "renderer-invocation-authority", "one-controlled-renderer-invocation-act"),
    ("authority:briefforge-semantic-artifact-conformance", "semantic-artifact-conformance-assessor", "one-semantic-artifact-conformance-assessment"),
    ("authority:briefforge-publication-manifest-projector", "publication-manifest-projector", "one-publication-manifest-production"),
)
_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*$")

class RepresentativeProjectionRejected(ValueError):
    pass

@dataclass(frozen=True)
class Authority:
    identity: str; owner_identity: str; role: str; scope: str
@dataclass(frozen=True)
class Purpose:
    identity: str; statement: str; brief_purpose_ref: str | None
@dataclass(frozen=True)
class Audience:
    identity: str; description: str; brief_audience_ref: str | None
@dataclass(frozen=True)
class EvidenceSnapshot:
    identity: str; version: str; content_fingerprint: str; provenance_ref: str
@dataclass(frozen=True)
class DescribedIdentity:
    identity: str; description: str
@dataclass(frozen=True)
class Exhibit:
    identity: str; kind: str; purpose_ref: str; value_ids: tuple[str, ...]
@dataclass(frozen=True)
class Distribution:
    identity: str; designation: str; authority_ref: str
@dataclass(frozen=True)
class Section:
    identity: str; title: str; children: tuple[str, ...]
@dataclass(frozen=True)
class Statement:
    identity: str; text: str; posture: str; communication_functions: tuple[str, ...]; attention: str
    purpose_ref: str; authority_ref: str; upstream_refs: tuple[str, ...]; value_ref: str | None
    requires_comparison_universe: bool
@dataclass(frozen=True)
class Qualification:
    identity: str; kind: str; source_ref: str; target_ref: str; authority_ref: str
@dataclass(frozen=True)
class ExactValue:
    identity: str; value_state: str; coefficient: str | None; scale: int | None; reason: str | None
    unit_ref: str; semantic_type_ref: str; source_ref: str; authority_ref: str
    approximate: bool; approximation_method: str | None; approximation_bound: str | None
@dataclass(frozen=True)
class CaseBinding:
    identity: str; order: int; primary_ref: str; comparison_ref: str
@dataclass(frozen=True)
class Provenance:
    identity: str; citation: str; authority_ref: str
@dataclass(frozen=True)
class ExternalReference:
    identity: str; reference_kind: str; upstream_object_identity: str; snapshot_ref: str; provenance_ref: str; authority_ref: str
@dataclass(frozen=True)
class Obligation:
    identity: str; kind: str; authority_ref: str; target_refs: tuple[str, ...]
@dataclass(frozen=True)
class RequirementMapping:
    requirement_id: str; capability_id: str; expression_mode: str; target_refs: tuple[str, ...]; constraints: tuple[str, ...]
    mandatory: bool; criticality: str; authority_label_refs: tuple[str, ...]; caveat_refs: tuple[str, ...]
    permitted_transformations: tuple[str, ...]; fallback_refs: tuple[str, ...]; unsupported_allowed: bool
@dataclass(frozen=True)
class AdmittedRepresentativeContent:
    section_preorder: tuple[str, ...]; case_order: tuple[str, ...]
@dataclass(frozen=True)
class RepresentativeProjection:
    profile_identity: str; profile_version: str; renderer_identity: str; renderer_version: str; renderer_adapter_id: str
    brief_identity: str; material_identities: tuple[str, ...]; package_identity: str
    brief_purpose: Purpose; candidate_purpose: Purpose; audiences: tuple[Audience, ...]
    brief_scope: str; brief_non_scope: str; candidate_scope: str; candidate_non_scope: str
    title: str; purpose: str; audience: str; scope: str; non_scope: str
    sections: tuple[Section, ...]; statements: tuple[Statement, ...]; qualifications: tuple[Qualification, ...]
    case_bindings: tuple[CaseBinding, ...]; values: tuple[ExactValue, ...]
    provenance: tuple[Provenance, ...]; evidence_snapshots: tuple[EvidenceSnapshot, ...]
    external_references: tuple[ExternalReference, ...]; units: tuple[DescribedIdentity, ...]
    semantic_types: tuple[DescribedIdentity, ...]; obligations: tuple[Obligation, ...]
    content_authorities: tuple[Authority, ...]; operational_authority_exclusions: tuple[Authority, ...]
    requirement_mappings: tuple[RequirementMapping, ...]; exhibit: Exhibit; distribution: Distribution
    required_value_ids: tuple[str, ...]; exhibit_identity: str; output_filename: str; media_type: str
    fallbacks: tuple[str, ...]; comparison_universes: tuple[str, ...]; selection_sets: tuple[str, ...]
    consistency_assertions: tuple[str, ...]; state_validations: tuple[str, ...]
    section_preorder: tuple[str, ...]; case_order: tuple[str, ...]
    release_fingerprint: str; plan_fingerprint: str; content_closure_fingerprint: str; fingerprint: str


def _keys(value: Any, expected: set[str], where: str) -> None:
    if type(value) is not dict or set(value) != expected:
        raise RepresentativeProjectionRejected(f"{where} has an unexpected exact schema")
def _seq(value: Any, low: int, high: int, where: str) -> list:
    if type(value) is not list or not low <= len(value) <= high:
        raise RepresentativeProjectionRejected(f"{where} violates cardinality")
    return value
def _text(value: Any, where: str, *, identity: bool=False, long: bool=False) -> str:
    limit = 4096 if long else 200
    if type(value) is not str or not value or len(value.encode("utf-8")) > limit or (identity and not _ID.fullmatch(value)):
        raise RepresentativeProjectionRejected(f"{where} is malformed")
    return value
def _unique(items: list[dict], where: str) -> dict[str, dict]:
    result = {}
    for item in items:
        identity = _text(item.get("id"), where, identity=True) if type(item) is dict else ""
        if identity in result: raise RepresentativeProjectionRejected(f"duplicate {where}")
        result[identity] = item
    return result


def _admit(bundle) -> dict[str, Any]:
    try:
        brief = bundle.one("PresentationBriefRecord").semantic
        material = bundle.one("PortablePresentationMaterialRecord").semantic
        candidate = bundle.one("CandidatePresentationPackageRecord").semantic
    except Exception as exc: raise RepresentativeProjectionRejected("release closure is incomplete") from exc
    _keys(brief, {"organizing_purpose","audiences","scope","non_scope"}, "brief")
    _keys(candidate, {"brief_ref","material_refs","organizing_purpose","audiences","scope","non_scope","statements","sections","obligations","renderer_requirements","fallbacks","exhibits","relations","distribution","comparison_universes","selection_sets"}, "candidate")
    _keys(material, {"authorities","provenance","evidence_snapshots","external_references","units","semantic_types","values","required_value_ids","consistency_assertions","state_validations"}, "material")
    if (candidate["fallbacks"] != [] or candidate["comparison_universes"] != [] or
        candidate["selection_sets"] != [] or material["consistency_assertions"] != [] or
        material["state_validations"] != []):
        raise RepresentativeProjectionRejected("prohibited inventory must be exactly empty")
    for owner,name in ((brief,"brief"),(candidate,"candidate")):
        _keys(owner["organizing_purpose"], {"id","statement"} if name=="brief" else {"id","statement","brief_purpose_ref"}, name+" purpose")
        audiences=_seq(owner["audiences"],1,8,name+" audiences")
        for a in audiences:
            _keys(a,{"id","description"},name+" audience")
            _text(a["id"],"audience id",identity=True); _text(a["description"],"audience",long=True)
        _text(owner["scope"],"scope"); _text(owner["non_scope"],"non_scope")
        _text(owner["organizing_purpose"]["statement"],"purpose statement",long=True)
    sections=_seq(candidate["sections"],2,8,"sections"); section_by=_unique(sections,"section")
    for s in sections: _keys(s,{"id","title","children"},"section"); _text(s["title"],"title"); _seq(s["children"],1,17,"section children")
    statements=_seq(candidate["statements"],2,32,"statements"); statement_by=_unique(statements,"statement")
    statement_allowed={"id","text","posture","communication_functions","attention","purpose_ref","authority_ref","upstream_refs","requires_comparison_universe"}
    for s in statements:
        if set(s) not in (statement_allowed, statement_allowed|{"value_ref"}): raise RepresentativeProjectionRejected("statement has unexpected schema")
        _text(s["text"],"statement text",long=True); _seq(s["communication_functions"],1,4,"communication functions"); _seq(s["upstream_refs"],1,16,"upstream refs")
        if s["requires_comparison_universe"] is not False: raise RepresentativeProjectionRejected("comparison universe prohibited")
        if (s["posture"] not in {"observation","caveat","uncertainty"} or
            s["attention"] not in {"primary","supporting"} or
            any(x not in {"orient","summarize","compare","qualify","trace"} for x in s["communication_functions"]) or
            len(s["communication_functions"]) != len(set(s["communication_functions"])) or
            len(s["upstream_refs"]) != len(set(s["upstream_refs"]))):
            raise RepresentativeProjectionRejected("statement enum or set inventory malformed")
    declared_exhibits=_seq(candidate["exhibits"],1,1,"exhibits")
    if type(declared_exhibits[0]) is not dict or type(declared_exhibits[0].get("id")) is not str: raise RepresentativeProjectionRejected("exhibit malformed")
    declared_exhibit_id=declared_exhibits[0]["id"]
    roots=[]; seen_children=[]; encounter=[]
    for s in sections:
        child_sections=[x for x in s["children"] if x in section_by]; child_statements=[x for x in s["children"] if x in statement_by]
        unknown=set(s["children"])-set(section_by)-set(statement_by)-{declared_exhibit_id}
        if unknown: raise RepresentativeProjectionRejected("unknown section child")
        if child_sections: roots.append(s["id"])
        else:
            if not 1<=len(child_statements)<=16: raise RepresentativeProjectionRejected("leaf statement bound")
            encounter.extend(child_statements)
        seen_children.extend(child_sections)
    if len(roots)!=1 or set(seen_children)!=set(section_by)-set(roots) or len(seen_children)!=len(set(seen_children)) or set(section_by[roots[0]]["children"])!=set(section_by)-set(roots): raise RepresentativeProjectionRejected("hierarchy must be exact depth two")
    if len(encounter)!=len(statement_by) or set(encounter)!=set(statement_by): raise RepresentativeProjectionRejected("statements must occur exactly once")
    exhibits=declared_exhibits; exhibit=exhibits[0]; _keys(exhibit,{"id","kind","purpose_ref","case_bindings","value_ids"},"exhibit")
    _text(exhibit["id"],"exhibit id",identity=True)
    if exhibit["kind"]!="fixed-static-table": raise RepresentativeProjectionRejected("fixed exhibit required")
    if sum(s["children"].count(exhibit["id"]) for s in sections)!=1: raise RepresentativeProjectionRejected("exhibit must occur as exactly one section child")
    cases=_seq(exhibit["case_bindings"],1,16,"cases"); case_by=_unique(cases,"case")
    for c in cases:
        _keys(c,{"id","order","primary_ref","comparison_ref"},"case")
        if type(c["order"]) is not int or type(c["order"]) is bool: raise RepresentativeProjectionRejected("case order malformed")
    orders=[c["order"] for c in cases]
    if set(orders)!=set(range(1,len(cases)+1)) or len(orders)!=len(set(orders)): raise RepresentativeProjectionRejected("case order incomplete")
    values=_seq(material["values"],2,32,"values"); value_by=_unique(values,"value")
    common={"id","value_state","unit_ref","semantic_type_ref","source_ref","authority_ref"}
    for v in values:
        state=v.get("value_state")
        allowed=common|({"payload"} if state in {"present","explicit-zero"} else {"reason"})
        if state in {"present","explicit-zero"} and v.get("approximate") is True: allowed|={"approximate","approximation"}
        _keys(v,allowed,"value")
        if state not in {"present","explicit-zero","missing-not-provided","unavailable","not-applicable"}: raise RepresentativeProjectionRejected("value state malformed")
        if "payload" in v:
            _keys(v["payload"],{"coefficient","scale"},"value payload")
            coefficient=v["payload"]["coefficient"]; scale=v["payload"]["scale"]
            if type(coefficient) is not str or not re.fullmatch(r"-?(?:0|[1-9][0-9]*)",coefficient) or type(scale) is not int or type(scale) is bool or not 0<=scale<=18: raise RepresentativeProjectionRejected("decimal malformed")
            if state=="explicit-zero" and (coefficient!="0" or scale!=0): raise RepresentativeProjectionRejected("explicit zero malformed")
            if state=="present" and int(coefficient)==0: raise RepresentativeProjectionRejected("present zero must use explicit-zero state")
        else: _text(v["reason"],"absence reason",long=True)
        if "approximation" in v:
            _keys(v["approximation"],{"method","bound"},"approximation")
            _text(v["approximation"]["method"],"approximation method",long=True); _text(v["approximation"]["bound"],"approximation bound",long=True)
    if (len(values)!=2*len(cases) or set(exhibit["value_ids"])!=set(value_by) or
        len(exhibit["value_ids"])!=len(value_by) or
        set(material["required_value_ids"])!=set(exhibit["value_ids"]) or
        len(material["required_value_ids"])!=len(value_by)):
        raise RepresentativeProjectionRejected("value closure mismatch")
    for c in cases:
        if c["primary_ref"] not in value_by or c["comparison_ref"] not in value_by or c["primary_ref"]==c["comparison_ref"]: raise RepresentativeProjectionRejected("case ref malformed")
    if len({r for c in cases for r in (c["primary_ref"],c["comparison_ref"])})!=len(values): raise RepresentativeProjectionRejected("value pairing not exact")
    units=_unique(_seq(material["units"],1,16,"units"),"unit"); types=_unique(_seq(material["semantic_types"],1,16,"types"),"type")
    for x in list(units.values())+list(types.values()): _keys(x,{"id","description"},"unit/type"); _text(x["description"],"unit/type description",long=True)
    authorities=_unique(_seq(material["authorities"],6,13,"authorities"),"authority")
    for x in authorities.values():
        _keys(x,{"id","owner_identity","role","scope"},"authority")
        _text(x["owner_identity"],"authority owner",identity=True); _text(x["role"],"authority role"); _text(x["scope"],"authority scope")
    for identity,role,scope in _OPERATIONAL:
        if authorities.get(identity)!={"id":identity,"owner_identity":"project:BriefForge","role":role,"scope":scope}: raise RepresentativeProjectionRejected("operational authority mismatch")
    content=set(authorities)-{x[0] for x in _OPERATIONAL}
    if not 1<=len(content)<=8: raise RepresentativeProjectionRejected("content authority bound")
    provenance=_unique(_seq(material["provenance"],1,16,"provenance"),"provenance")
    snapshots=_unique(_seq(material["evidence_snapshots"],1,16,"snapshots"),"snapshot")
    external=_unique(_seq(material["external_references"],1,16,"external"),"external")
    for x in provenance.values(): _keys(x,{"id","citation","authority_ref"},"provenance"); _text(x["citation"],"citation",long=True)
    for x in snapshots.values():
        _keys(x,{"id","version","content_fingerprint","provenance_ref"},"snapshot"); _text(x["version"],"snapshot version"); _text(x["content_fingerprint"],"snapshot fingerprint")
    for x in external.values():
        _keys(x,{"id","reference_kind","upstream_object_identity","snapshot_ref","provenance_ref","authority_ref"},"external")
        _text(x["reference_kind"],"reference kind"); _text(x["upstream_object_identity"],"upstream object identity")
    for v in values:
        if v["unit_ref"] not in units or v["semantic_type_ref"] not in types or v["source_ref"] not in external or v["authority_ref"] not in content: raise RepresentativeProjectionRejected("value refs unresolved")
    relations=_seq(candidate["relations"],1,16,"relations"); relation_by=_unique(relations,"relation")
    for x in relations: _keys(x,{"id","kind","source_ref","target_ref","authority_ref"},"relation")
    qualifications=[s for s in statements if s["posture"] in {"caveat","uncertainty"}]
    if not 1<=len(qualifications)<=16 or len(relations)!=len(qualifications): raise RepresentativeProjectionRejected("qualification cardinality")
    observations={s["id"] for s in statements if s["posture"]=="observation"}
    if any(r["kind"]!="limits-target" or r["source_ref"] not in {s["id"] for s in qualifications} or r["target_ref"] not in observations for r in relations) or len({r["source_ref"] for r in relations})!=len(relations): raise RepresentativeProjectionRejected("qualification relation malformed")
    obligations=_seq(candidate["obligations"],1,16,"obligations"); _unique(obligations,"obligation")
    for x in obligations:
        _keys(x,{"id","kind","authority_ref","target_refs"},"obligation"); targets=_seq(x["target_refs"],1,16,"obligation targets")
        if x["kind"] not in {"label","qualification-required","source-display"}: raise RepresentativeProjectionRejected("obligation kind prohibited")
        if len(targets)!=len(set(targets)): raise RepresentativeProjectionRejected("duplicate obligation target")
    requirements=_seq(candidate["renderer_requirements"],7,7,"requirements"); req_by=_unique(requirements,"requirement")
    req_keys={"id","capability","mandatory","criticality","target_refs","authority_label_refs","caveat_refs","required_constraints","permitted_transformations","fallback_refs","unsupported_allowed"}
    for stem,specific in _RULES:
        identity=f"requirement:representative-{stem}"; r=req_by.get(identity)
        if not r: raise RepresentativeProjectionRejected("missing exact requirement")
        _keys(r,req_keys,"requirement")
        if r["capability"]!=f"capability:representative-{stem}" or r["mandatory"] is not True or r["criticality"]!="required" or r["required_constraints"]!=sorted((_GLOBAL,f"constraint:{specific}")) or r["permitted_transformations"]!=[] or r["fallback_refs"]!=[] or r["unsupported_allowed"] is not False: raise RepresentativeProjectionRejected("requirement policy mismatch")
    # Close all directed references and exact per-capability semantic inventories.
    candidate_id=bundle.one("CandidatePresentationPackageRecord").identity
    brief_id=bundle.one("PresentationBriefRecord").identity
    material_id=bundle.one("PortablePresentationMaterialRecord").identity
    purpose_id=candidate["organizing_purpose"]["id"]
    _keys(candidate["distribution"],{"id","designation","authority_ref"},"distribution")
    audience_ids={x["id"] for x in brief["audiences"]+candidate["audiences"]}
    if candidate["brief_ref"]!=brief_id or candidate["material_refs"]!=[material_id] or candidate["organizing_purpose"]["brief_purpose_ref"]!=brief["organizing_purpose"]["id"] or exhibit["purpose_ref"]!=purpose_id:
        raise RepresentativeProjectionRejected("brief/material/purpose closure mismatch")
    if (candidate["organizing_purpose"]["statement"] != brief["organizing_purpose"]["statement"] or
        candidate["scope"] != brief["scope"] or candidate["non_scope"] != brief["non_scope"] or
        sorted(x["description"] for x in candidate["audiences"]) != sorted(x["description"] for x in brief["audiences"])
        or len(candidate["audiences"]) != len(brief["audiences"])):
        raise RepresentativeProjectionRejected("brief and candidate authored semantics differ")
    for s in statements:
        if s["purpose_ref"]!=purpose_id or s["authority_ref"] not in content or any(x not in external for x in s["upstream_refs"]) or ("value_ref" in s and s["value_ref"] not in value_by):
            raise RepresentativeProjectionRejected("statement reference closure mismatch")
    for x in provenance.values():
        if x["authority_ref"] not in content: raise RepresentativeProjectionRejected("provenance authority unresolved")
    for x in snapshots.values():
        if x["provenance_ref"] not in provenance: raise RepresentativeProjectionRejected("snapshot provenance unresolved")
    for x in external.values():
        if x["snapshot_ref"] not in snapshots or x["provenance_ref"] not in provenance or x["authority_ref"] not in content: raise RepresentativeProjectionRejected("external reference closure mismatch")
    for x in relations:
        if x["authority_ref"] not in content: raise RepresentativeProjectionRejected("relation authority unresolved")
    known_targets=set(statement_by)|set(external)|set(value_by)|set(case_by)|set(section_by)|set(authorities)|set(relation_by)|set(units)|set(types)|set(provenance)|set(snapshots)|set(audience_ids)|{brief_id,candidate_id,material_id,purpose_id,brief["organizing_purpose"]["id"],exhibit["id"],candidate["distribution"]["id"]}
    for x in obligations:
        if x["authority_ref"] not in content or any(t not in known_targets - {item[0] for item in _OPERATIONAL} for t in x["target_refs"]): raise RepresentativeProjectionRejected("obligation closure mismatch")
    _keys(candidate["distribution"],{"id","designation","authority_ref"},"distribution")
    if candidate["distribution"]["authority_ref"] not in content: raise RepresentativeProjectionRejected("distribution authority unresolved")
    _text(candidate["distribution"]["designation"],"distribution designation")
    if {v["unit_ref"] for v in values} != set(units) or {v["semantic_type_ref"] for v in values} != set(types): raise RepresentativeProjectionRejected("orphan unit or semantic type")
    if ({v["source_ref"] for v in values} | {u for s in statements for u in s["upstream_refs"]}) != set(external):
        raise RepresentativeProjectionRejected("orphan external reference")
    if {x["snapshot_ref"] for x in external.values()} != set(snapshots):
        raise RepresentativeProjectionRejected("orphan evidence snapshot")
    if ({x["provenance_ref"] for x in external.values()} | {x["provenance_ref"] for x in snapshots.values()}) != set(provenance):
        raise RepresentativeProjectionRejected("orphan provenance")
    referenced_content={v["authority_ref"] for v in values}|{s["authority_ref"] for s in statements}|{x["authority_ref"] for x in provenance.values()}|{x["authority_ref"] for x in external.values()}|{x["authority_ref"] for x in relations}|{x["authority_ref"] for x in obligations}|{candidate["distribution"]["authority_ref"]}
    if referenced_content != content: raise RepresentativeProjectionRejected("orphan content authority")
    caveat_ids=sorted(s["id"] for s in qualifications)
    expected_targets={
        "section-hierarchy": {brief_id,candidate_id,brief["organizing_purpose"]["id"],purpose_id,*audience_ids,*section_by,candidate["distribution"]["id"]},
        "ordered-statements": set(statement_by),
        "exact-quantitative-values": set(case_by)|set(value_by)|set(units)|set(types),
        "qualification-attachments": set(caveat_ids)|set(relation_by),
        "provenance-references": {material_id}|set(content)|set(provenance)|set(snapshots)|set(external),
        "complete-obligations": {x["id"] for x in obligations},
        "fixed-static-table": {exhibit["id"]}|set(case_by)|set(value_by),
    }
    for stem,_ in _RULES:
        r=req_by[f"requirement:representative-{stem}"]
        expected_caveats=caveat_ids if stem in {"ordered-statements","qualification-attachments"} else []
        if r["target_refs"]!=sorted(expected_targets[stem]) or r["authority_label_refs"]!=sorted(content) or r["caveat_refs"]!=expected_caveats:
            raise RepresentativeProjectionRejected("requirement semantic inventory mismatch")
    return locals()


def admit_representative_release_content(bundle) -> AdmittedRepresentativeContent:
    d=_admit(bundle); root=d["roots"][0]; preorder=(root,*d["section_by"][root]["children"])
    ordered=tuple(x["id"] for x in sorted(d["cases"],key=lambda x:x["order"]))
    return AdmittedRepresentativeContent(tuple(preorder),ordered)


def _canonical(value: Any) -> bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()

def representative_projection_document(projection: RepresentativeProjection) -> dict[str, Any]:
    if type(projection) is not RepresentativeProjection:
        raise RepresentativeProjectionRejected("exact representative projection required")
    document=asdict(projection); document.pop("fingerprint")
    return document

def compute_representative_projection_fingerprint(projection: RepresentativeProjection) -> str:
    return hashlib.sha256(_canonical(representative_projection_document(projection))).hexdigest()

def verify_representative_projection(projection: RepresentativeProjection) -> None:
    if type(projection) is not RepresentativeProjection or projection.fingerprint != compute_representative_projection_fingerprint(projection):
        raise RepresentativeProjectionRejected("projection fingerprint is stale or forged")

def build_representative_projection(*, verified_release, evidence_snapshot, lifecycle_scope, declaration, planning_authorization, verified_plan) -> RepresentativeProjection:
    try:
        if type(verified_release) is not VerifiedPublicationRelease or type(verified_plan) is not VerifiedRendererCompatibilityPlan: raise ValueError("exact verified inputs required")
        release=verify_publication_release(verified_release.bundle,evidence_snapshot=evidence_snapshot,expected_release_fingerprint=verified_release.fingerprint.digest)
        plan=verify_renderer_compatibility_plan(verified_plan.bundle,evidence_snapshot=evidence_snapshot,lifecycle_scope=lifecycle_scope,declaration=declaration,authorization=planning_authorization,expected_plan_fingerprint=verified_plan.fingerprint.digest)
        if tuple(r.to_document() for r in plan.bundle.records[:6])!=tuple(r.to_document() for r in release.bundle.records): raise ValueError("release/plan mismatch")
        if declaration.renderer_identity!=RENDERER_IDENTITY or declaration.renderer_version!=RENDERER_VERSION or declaration.renderer_owner!="project:BriefForge" or declaration.renderer_role!="bounded-publication-renderer" or declaration.unsupported_capabilities or declaration.inventory_complete is not True: raise ValueError("renderer declaration mismatch")
        d=_admit(release.bundle)
        mappings=json.loads(plan.mappings_document); req=d["req_by"]
        if len(mappings)!=7 or {m.get("requirement_id") for m in mappings}!=set(req): raise ValueError("exact seven mappings required")
        mapped={m["requirement_id"]:m for m in mappings}
        for rid,r in req.items():
            m=mapped[rid]
            if m.get("selected_expression_mode")!="native" or m.get("capability_id")!=r["capability"] or m.get("affected_semantic_identities")!=r["target_refs"]: raise ValueError("mapping mismatch")
    except RepresentativeProjectionRejected: raise
    except Exception as exc: raise RepresentativeProjectionRejected(str(exc)) from exc
    root=d["roots"][0]
    preorder=(root,*d["section_by"][root]["children"])
    statement_order=[x for sid in preorder[1:] for x in d["section_by"][sid]["children"] if x in d["statement_by"]]
    vals=[]
    for v in sorted(d["values"],key=lambda x:x["id"]):
        payload=v.get("payload",{}); approximation=v.get("approximation",{})
        vals.append(ExactValue(v["id"],v["value_state"],payload.get("coefficient"),payload.get("scale"),v.get("reason"),v["unit_ref"],v["semantic_type_ref"],v["source_ref"],v["authority_ref"],v.get("approximate",False),approximation.get("method"),approximation.get("bound")))
    def authorities(ids):
        return tuple(Authority(i,d["authorities"][i]["owner_identity"],d["authorities"][i]["role"],d["authorities"][i]["scope"]) for i in ids)
    bp=d["brief"]["organizing_purpose"]; cp=d["candidate"]["organizing_purpose"]
    all_audiences=[]
    for owner in (d["brief"],d["candidate"]):
        all_audiences.extend(Audience(x["id"],x["description"],None)
                             for x in sorted(owner["audiences"], key=lambda item:item["id"]))
    preliminary=dict(
        profile_identity=PROJECTION_PROFILE_ID,profile_version=PROJECTION_PROFILE_VERSION,
        renderer_identity=RENDERER_IDENTITY,renderer_version=RENDERER_VERSION,renderer_adapter_id=RENDERER_ADAPTER_ID,
        brief_identity=d["brief_id"],material_identities=(d["material_id"],),package_identity=d["candidate_id"],
        brief_purpose=Purpose(bp["id"],bp["statement"],None),candidate_purpose=Purpose(cp["id"],cp["statement"],cp["brief_purpose_ref"]),audiences=tuple(all_audiences),
        brief_scope=d["brief"]["scope"],brief_non_scope=d["brief"]["non_scope"],candidate_scope=d["candidate"]["scope"],candidate_non_scope=d["candidate"]["non_scope"],
        title=d["section_by"][root]["title"],purpose=cp["statement"],audience=d["candidate"]["audiences"][0]["description"],scope=d["candidate"]["scope"],non_scope=d["candidate"]["non_scope"],
        sections=tuple(Section(i,d["section_by"][i]["title"],tuple(d["section_by"][i]["children"])) for i in preorder),
        statements=tuple(Statement(i,d["statement_by"][i]["text"],d["statement_by"][i]["posture"],tuple(d["statement_by"][i]["communication_functions"]),d["statement_by"][i]["attention"],d["statement_by"][i]["purpose_ref"],d["statement_by"][i]["authority_ref"],tuple(d["statement_by"][i]["upstream_refs"]),d["statement_by"][i].get("value_ref"),False) for i in statement_order),
        qualifications=tuple(Qualification(r["id"],r["kind"],r["source_ref"],r["target_ref"],r["authority_ref"]) for r in sorted(d["relations"],key=lambda x:x["id"])),
        case_bindings=tuple(CaseBinding(c["id"],c["order"],c["primary_ref"],c["comparison_ref"]) for c in sorted(d["cases"],key=lambda x:x["order"])),values=tuple(vals),
        provenance=tuple(Provenance(x["id"],x["citation"],x["authority_ref"]) for x in sorted(d["provenance"].values(),key=lambda x:x["id"])),
        evidence_snapshots=tuple(EvidenceSnapshot(x["id"],x["version"],x["content_fingerprint"],x["provenance_ref"]) for x in sorted(d["snapshots"].values(),key=lambda x:x["id"])),
        external_references=tuple(ExternalReference(x["id"],x["reference_kind"],x["upstream_object_identity"],x["snapshot_ref"],x["provenance_ref"],x["authority_ref"]) for x in sorted(d["external"].values(),key=lambda x:x["id"])),
        units=tuple(DescribedIdentity(x["id"],x["description"]) for x in sorted(d["units"].values(),key=lambda x:x["id"])),semantic_types=tuple(DescribedIdentity(x["id"],x["description"]) for x in sorted(d["types"].values(),key=lambda x:x["id"])),
        obligations=tuple(Obligation(x["id"],x["kind"],x["authority_ref"],tuple(sorted(x["target_refs"]))) for x in sorted(d["obligations"],key=lambda x:x["id"])),
        content_authorities=authorities(sorted(d["content"])),operational_authority_exclusions=authorities([x[0] for x in _OPERATIONAL]),
        requirement_mappings=tuple(RequirementMapping(rid,req[rid]["capability"],mapped[rid]["selected_expression_mode"],tuple(req[rid]["target_refs"]),tuple(req[rid]["required_constraints"]),req[rid]["mandatory"],req[rid]["criticality"],tuple(req[rid]["authority_label_refs"]),tuple(req[rid]["caveat_refs"]),tuple(req[rid]["permitted_transformations"]),tuple(req[rid]["fallback_refs"]),req[rid]["unsupported_allowed"]) for rid in (f"requirement:representative-{stem}" for stem,_ in _RULES)),
        exhibit=Exhibit(d["exhibit"]["id"],d["exhibit"]["kind"],d["exhibit"]["purpose_ref"],tuple(sorted(d["exhibit"]["value_ids"]))),distribution=Distribution(d["candidate"]["distribution"]["id"],d["candidate"]["distribution"]["designation"],d["candidate"]["distribution"]["authority_ref"]),
        required_value_ids=tuple(sorted(d["material"]["required_value_ids"])),exhibit_identity=d["exhibit"]["id"],output_filename="brief.html",media_type="text/html",
        fallbacks=(),comparison_universes=(),selection_sets=(),consistency_assertions=(),state_validations=(),
        section_preorder=tuple(preorder),case_order=tuple(x["id"] for x in sorted(d["cases"],key=lambda x:x["order"])),release_fingerprint=release.fingerprint.digest,plan_fingerprint=plan.fingerprint.digest,
        content_closure_fingerprint=hashlib.sha256(_canonical([r.to_document() for r in release.bundle.records[:3]])).hexdigest())
    provisional=RepresentativeProjection(**preliminary,fingerprint="")
    return RepresentativeProjection(**preliminary,fingerprint=compute_representative_projection_fingerprint(provisional))
