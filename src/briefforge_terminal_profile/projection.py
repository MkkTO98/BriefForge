"""Closed successor projection for the terminal representative profile."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, fields
import hashlib
import json
from pathlib import Path
from typing import Any

from briefforge.bcrp.model import BCRPBundle
from briefforge.publication_release import VerifiedPublicationRelease, verify_publication_release
from briefforge.renderer_compatibility_planning import (
    VerifiedRendererCompatibilityPlan,
    verify_renderer_compatibility_plan,
)
from briefforge import representative_projection as legacy

from .profile import (
    PROFILE_IDENTITY,
    PROFILE_VERSION,
    TERMINAL_OPERATIONAL_IDENTITIES,
    TerminalAuthorityProfile,
    verify_material_authority_profile,
)

PROJECTION_IDENTITY = "briefforge:representative-terminal-static-html-projection:2.0.0"
PROJECTION_VERSION = "2.0.0"
PROJECTION_IMPLEMENTATION_IDENTITY = "briefforge_terminal_profile.projection"
PROJECTION_IMPLEMENTATION_VERSION = "1.0.0"
RENDERER_IDENTITY = legacy.RENDERER_IDENTITY
RENDERER_VERSION = legacy.RENDERER_VERSION
ADAPTER_IDENTITY = "adapter:briefforge-terminal-to-representative-static-html"
ADAPTER_VERSION = "1.0.0"


class TerminalProjectionRejected(ValueError):
    pass


@dataclass(frozen=True)
class TerminalRepresentativeProjection(legacy.RepresentativeProjection):
    """Successor DTO: the complete semantic DTO plus truthful adapter routing."""

    adapter_identity: str
    adapter_version: str
    adapter_source_digest: str


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def projection_implementation_digest() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def terminal_projection_document(projection: TerminalRepresentativeProjection) -> dict[str, Any]:
    if type(projection) is not TerminalRepresentativeProjection:
        raise TerminalProjectionRejected("exact terminal projection required")
    document = asdict(projection)
    document.pop("fingerprint")
    return document


def compute_terminal_projection_fingerprint(projection: TerminalRepresentativeProjection) -> str:
    return hashlib.sha256(_canonical(terminal_projection_document(projection))).hexdigest()


def verify_terminal_projection(projection: TerminalRepresentativeProjection) -> None:
    if type(projection) is not TerminalRepresentativeProjection:
        raise TerminalProjectionRejected("exact terminal projection required")
    from .renderer_adapter import adapter_source_digest
    expected = (
        PROJECTION_IDENTITY, PROJECTION_VERSION, RENDERER_IDENTITY, RENDERER_VERSION,
        ADAPTER_IDENTITY, ADAPTER_IDENTITY, ADAPTER_VERSION, adapter_source_digest(),
    )
    actual = (
        projection.profile_identity, projection.profile_version,
        projection.renderer_identity, projection.renderer_version,
        projection.renderer_adapter_id, projection.adapter_identity,
        projection.adapter_version, projection.adapter_source_digest,
    )
    if actual != expected:
        raise TerminalProjectionRejected("successor projection routing tuple mismatch")
    if tuple(item.identity for item in projection.operational_authority_exclusions) != TERMINAL_OPERATIONAL_IDENTITIES:
        raise TerminalProjectionRejected("all eight operational exclusions are required in exact order")
    if projection.fingerprint != compute_terminal_projection_fingerprint(projection):
        raise TerminalProjectionRejected("terminal projection fingerprint is stale or forged")


def _legacy_admission_view(bundle: BCRPBundle) -> BCRPBundle:
    """Create an isolated v1 admission view; never mutate released bytes."""
    copied = deepcopy(bundle)
    material = copied.one("PortablePresentationMaterialRecord").semantic
    material["authorities"] = [
        item for item in material["authorities"]
        if item["id"] not in set(TERMINAL_OPERATIONAL_IDENTITIES[5:])
    ]
    return copied


def admit_terminal_representative_release_content(
    bundle: BCRPBundle, profile: TerminalAuthorityProfile
) -> legacy.AdmittedRepresentativeContent:
    if type(bundle) is not BCRPBundle:
        raise TerminalProjectionRejected("exact BCRP bundle required")
    material = bundle.one("PortablePresentationMaterialRecord").semantic
    verify_material_authority_profile(material.get("authorities"), profile)
    try:
        # The historical semantic classifier is not used for authority
        # classification: profile verification above has already closed the two
        # sets.  Its mature semantic closure checks run only on an isolated view.
        return legacy.admit_representative_release_content(_legacy_admission_view(bundle))
    except Exception as exc:
        raise TerminalProjectionRejected(str(exc)) from exc


def _semantic_projection(d: dict[str, Any], release, plan, mapped) -> legacy.RepresentativeProjection:
    root=d["roots"][0]
    preorder=(root,*d["section_by"][root]["children"])
    statement_order=[x for sid in preorder[1:] for x in d["section_by"][sid]["children"] if x in d["statement_by"]]
    vals=[]
    for v in sorted(d["values"],key=lambda x:x["id"]):
        payload=v.get("payload",{}); approximation=v.get("approximation",{})
        vals.append(legacy.ExactValue(v["id"],v["value_state"],payload.get("coefficient"),payload.get("scale"),v.get("reason"),v["unit_ref"],v["semantic_type_ref"],v["source_ref"],v["authority_ref"],v.get("approximate",False),approximation.get("method"),approximation.get("bound")))
    def authorities(ids):
        return tuple(legacy.Authority(i,d["authorities"][i]["owner_identity"],d["authorities"][i]["role"],d["authorities"][i]["scope"]) for i in ids)
    bp=d["brief"]["organizing_purpose"]; cp=d["candidate"]["organizing_purpose"]
    audiences=[]
    for owner in (d["brief"],d["candidate"]):
        audiences.extend(legacy.Audience(x["id"],x["description"],None) for x in sorted(owner["audiences"],key=lambda x:x["id"]))
    req=d["req_by"]
    preliminary=dict(
        profile_identity=legacy.PROJECTION_PROFILE_ID,profile_version=legacy.PROJECTION_PROFILE_VERSION,
        renderer_identity=RENDERER_IDENTITY,renderer_version=RENDERER_VERSION,renderer_adapter_id=legacy.RENDERER_ADAPTER_ID,
        brief_identity=d["brief_id"],material_identities=(d["material_id"],),package_identity=d["candidate_id"],
        brief_purpose=legacy.Purpose(bp["id"],bp["statement"],None),candidate_purpose=legacy.Purpose(cp["id"],cp["statement"],cp["brief_purpose_ref"]),audiences=tuple(audiences),
        brief_scope=d["brief"]["scope"],brief_non_scope=d["brief"]["non_scope"],candidate_scope=d["candidate"]["scope"],candidate_non_scope=d["candidate"]["non_scope"],
        title=d["section_by"][root]["title"],purpose=cp["statement"],audience=d["candidate"]["audiences"][0]["description"],scope=d["candidate"]["scope"],non_scope=d["candidate"]["non_scope"],
        sections=tuple(legacy.Section(i,d["section_by"][i]["title"],tuple(d["section_by"][i]["children"])) for i in preorder),
        statements=tuple(legacy.Statement(i,d["statement_by"][i]["text"],d["statement_by"][i]["posture"],tuple(d["statement_by"][i]["communication_functions"]),d["statement_by"][i]["attention"],d["statement_by"][i]["purpose_ref"],d["statement_by"][i]["authority_ref"],tuple(d["statement_by"][i]["upstream_refs"]),d["statement_by"][i].get("value_ref"),False) for i in statement_order),
        qualifications=tuple(legacy.Qualification(r["id"],r["kind"],r["source_ref"],r["target_ref"],r["authority_ref"]) for r in sorted(d["relations"],key=lambda x:x["id"])),
        case_bindings=tuple(legacy.CaseBinding(c["id"],c["order"],c["primary_ref"],c["comparison_ref"]) for c in sorted(d["cases"],key=lambda x:x["order"])),values=tuple(vals),
        provenance=tuple(legacy.Provenance(x["id"],x["citation"],x["authority_ref"]) for x in sorted(d["provenance"].values(),key=lambda x:x["id"])),
        evidence_snapshots=tuple(legacy.EvidenceSnapshot(x["id"],x["version"],x["content_fingerprint"],x["provenance_ref"]) for x in sorted(d["snapshots"].values(),key=lambda x:x["id"])),
        external_references=tuple(legacy.ExternalReference(x["id"],x["reference_kind"],x["upstream_object_identity"],x["snapshot_ref"],x["provenance_ref"],x["authority_ref"]) for x in sorted(d["external"].values(),key=lambda x:x["id"])),
        units=tuple(legacy.DescribedIdentity(x["id"],x["description"]) for x in sorted(d["units"].values(),key=lambda x:x["id"])),semantic_types=tuple(legacy.DescribedIdentity(x["id"],x["description"]) for x in sorted(d["types"].values(),key=lambda x:x["id"])),
        obligations=tuple(legacy.Obligation(x["id"],x["kind"],x["authority_ref"],tuple(sorted(x["target_refs"]))) for x in sorted(d["obligations"],key=lambda x:x["id"])),
        content_authorities=authorities(sorted(d["content"])),operational_authority_exclusions=authorities(TERMINAL_OPERATIONAL_IDENTITIES),
        requirement_mappings=tuple(legacy.RequirementMapping(rid,req[rid]["capability"],mapped[rid]["selected_expression_mode"],tuple(req[rid]["target_refs"]),tuple(req[rid]["required_constraints"]),req[rid]["mandatory"],req[rid]["criticality"],tuple(req[rid]["authority_label_refs"]),tuple(req[rid]["caveat_refs"]),tuple(req[rid]["permitted_transformations"]),tuple(req[rid]["fallback_refs"]),req[rid]["unsupported_allowed"]) for rid in (f"requirement:representative-{stem}" for stem,_ in legacy._RULES)),
        exhibit=legacy.Exhibit(d["exhibit"]["id"],d["exhibit"]["kind"],d["exhibit"]["purpose_ref"],tuple(sorted(d["exhibit"]["value_ids"]))),distribution=legacy.Distribution(d["candidate"]["distribution"]["id"],d["candidate"]["distribution"]["designation"],d["candidate"]["distribution"]["authority_ref"]),
        required_value_ids=tuple(sorted(d["material"]["required_value_ids"])),exhibit_identity=d["exhibit"]["id"],output_filename="brief.html",media_type="text/html",
        fallbacks=(),comparison_universes=(),selection_sets=(),consistency_assertions=(),state_validations=(),section_preorder=tuple(preorder),case_order=tuple(x["id"] for x in sorted(d["cases"],key=lambda x:x["order"])),release_fingerprint=release.fingerprint.digest,plan_fingerprint=plan.fingerprint.digest,
        content_closure_fingerprint=hashlib.sha256(_canonical([r.to_document() for r in release.bundle.records[:3]])).hexdigest())
    provisional=legacy.RepresentativeProjection(**preliminary,fingerprint="")
    return legacy.RepresentativeProjection(**preliminary,fingerprint=legacy.compute_representative_projection_fingerprint(provisional))


def build_terminal_representative_projection(*, verified_release, evidence_snapshot,
        lifecycle_scope, declaration, planning_authorization, verified_plan,
        authority_profile: TerminalAuthorityProfile) -> TerminalRepresentativeProjection:
    """Build the explicitly selected successor; cardinality never selects it."""
    try:
        if type(verified_release) is not VerifiedPublicationRelease or type(verified_plan) is not VerifiedRendererCompatibilityPlan:
            raise ValueError("exact verified inputs required")
        release=verify_publication_release(verified_release.bundle,evidence_snapshot=evidence_snapshot,expected_release_fingerprint=verified_release.fingerprint.digest)
        plan=verify_renderer_compatibility_plan(verified_plan.bundle,evidence_snapshot=evidence_snapshot,lifecycle_scope=lifecycle_scope,declaration=declaration,authorization=planning_authorization,expected_plan_fingerprint=verified_plan.fingerprint.digest)
        if tuple(r.to_document() for r in plan.bundle.records[:6]) != tuple(r.to_document() for r in release.bundle.records):
            raise ValueError("release/plan mismatch")
        if declaration.renderer_identity!=RENDERER_IDENTITY or declaration.renderer_version!=RENDERER_VERSION or declaration.renderer_owner!="project:BriefForge" or declaration.renderer_role!="bounded-publication-renderer" or declaration.unsupported_capabilities or declaration.inventory_complete is not True:
            raise ValueError("renderer declaration mismatch")
        verify_material_authority_profile(release.bundle.one("PortablePresentationMaterialRecord").semantic.get("authorities"), authority_profile)
        view=_legacy_admission_view(release.bundle)
        d=legacy._admit(view)
        mappings=json.loads(plan.mappings_document)
        req=d["req_by"]
        if len(mappings)!=7 or {m.get("requirement_id") for m in mappings}!=set(req):
            raise ValueError("exact seven mappings required")
        mapped={m["requirement_id"]:m for m in mappings}
        for rid,r in req.items():
            m=mapped[rid]
            if m.get("selected_expression_mode")!="native" or m.get("capability_id")!=r["capability"] or m.get("affected_semantic_identities")!=r["target_refs"]:
                raise ValueError("mapping mismatch")
        # Restore all eight exact authorities into the admitted construction data.
        d["authorities"]={x["id"]:x for x in release.bundle.one("PortablePresentationMaterialRecord").semantic["authorities"]}
        d["content"]=set(d["authorities"])-set(TERMINAL_OPERATIONAL_IDENTITIES)
        base=_semantic_projection(d,release,plan,mapped)
        from .renderer_adapter import adapter_source_digest
        values={f.name:getattr(base,f.name) for f in fields(legacy.RepresentativeProjection)}
        values.update(profile_identity=PROJECTION_IDENTITY,profile_version=PROJECTION_VERSION,
                      renderer_adapter_id=ADAPTER_IDENTITY,fingerprint="",
                      adapter_identity=ADAPTER_IDENTITY,adapter_version=ADAPTER_VERSION,
                      adapter_source_digest=adapter_source_digest())
        provisional=TerminalRepresentativeProjection(**values)
        result=TerminalRepresentativeProjection(**(values | {"fingerprint":compute_terminal_projection_fingerprint(provisional)}))
        verify_terminal_projection(result)
        return result
    except TerminalProjectionRejected:
        raise
    except Exception as exc:
        raise TerminalProjectionRejected(str(exc)) from exc
