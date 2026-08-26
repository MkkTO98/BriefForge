#!/usr/bin/env python3
"""Build TASK-076 non-production contract bytes and deterministic fixtures.

This tool specifies and verifies contract artifacts only. It is not imported by
production code and cannot issue a governed handle or lifecycle artifact.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/contracts/task076"
PROFILE = ROOT / "artifacts/pilots/candidate-authoring-output/attempt:task071-representative-campaign-002/profile.json"
CANDIDATE_FP = "b1c29473241648c68dfb7bb737715645b396c149094eeb70cef34feb52fb95b2"
PROFILE_SHA = "62cbe5294b123c9b4043e9f721a1b2585c70a5380e2121a39e8558b5c73b1898"
HEX = re.compile(r"^[0-9a-f]{64}$")
ID = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*$")


def cbytes(value: Any, newline: bool = False) -> bytes:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return data + (b"\n" if newline else b"")


def h(tag: str, value: Any, raw: bool = False) -> str:
    body = value if raw else cbytes(value)
    if not isinstance(body, bytes):
        raise TypeError("raw digest input must be bytes")
    return hashlib.sha256(tag.encode("ascii") + b"\0" + body).hexdigest()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(name: str, value: Any, canonical: bool = False) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    data = cbytes(value) if canonical else (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    (OUT / name).write_bytes(data)


def ptr_escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def registry() -> dict[str, Any]:
    records = [
        "PresentationBriefRecord", "PortablePresentationMaterialRecord", "CandidatePresentationPackageRecord",
        "ValidationJudgmentRecord", "ReadyPresentationPackageRecord", "PublicationReleaseRecord",
        "RendererCapabilityDeclarationRecord", "RendererCompatibilityPlanRecord", "GeneratedArtifactAuditRecord",
        "SemanticArtifactConformanceRecord", "PublicationManifestRecord",
    ]
    nested = [
        ("OrganizingPurpose", ["PresentationBriefRecord", "CandidatePresentationPackageRecord"], ["/semantic/organizing_purpose"], "id", False, "identity-keyed"),
        ("Audience", ["PresentationBriefRecord", "CandidatePresentationPackageRecord"], ["/semantic/audiences/{index}"], "id", False, "identity-keyed"),
        ("ContentAuthority", ["PortablePresentationMaterialRecord"], ["/semantic/authorities/{index}"], "id", True, "identity-keyed"),
        ("EvidenceSnapshot", ["PortablePresentationMaterialRecord"], ["/semantic/evidence_snapshots/{index}"], "id", True, "identity-keyed"),
        ("ExternalReference", ["PortablePresentationMaterialRecord"], ["/semantic/external_references/{index}"], "id", True, "identity-keyed"),
        ("Unit", ["PortablePresentationMaterialRecord"], ["/semantic/units/{index}"], "id", True, "identity-keyed"),
        ("SemanticType", ["PortablePresentationMaterialRecord"], ["/semantic/semantic_types/{index}"], "id", True, "identity-keyed"),
        ("MaterializedValue", ["PortablePresentationMaterialRecord"], ["/semantic/values/{index}"], "id", True, "identity-keyed"),
        ("MaterialProvenance", ["PortablePresentationMaterialRecord"], ["/semantic/provenance/{index}"], "id", True, "identity-keyed"),
        ("ConsistencyAssertion", ["PortablePresentationMaterialRecord"], ["/semantic/consistency_assertions/{index}"], "id", False, "identity-keyed"),
        ("StateValidation", ["PortablePresentationMaterialRecord"], ["/semantic/state_validations/{index}"], "id", False, "identity-keyed"),
        ("PresentationStatement", ["CandidatePresentationPackageRecord"], ["/semantic/statements/{index}"], "id", True, "identity-keyed"),
        ("Section", ["CandidatePresentationPackageRecord"], ["/semantic/sections/{index}"], "id", True, "identity-keyed-array-position-nonauthoritative-children-order-authoritative"),
        ("Obligation", ["CandidatePresentationPackageRecord"], ["/semantic/obligations/{index}"], "id", True, "identity-keyed"),
        ("RendererRequirement", ["CandidatePresentationPackageRecord"], ["/semantic/renderer_requirements/{index}"], "id", False, "owner-authored-order"),
        ("Fallback", ["CandidatePresentationPackageRecord"], ["/semantic/fallbacks/{index}"], "id", False, "owner-authored-order"),
        ("SelectionSet", ["CandidatePresentationPackageRecord"], ["/semantic/selection_sets/{index}"], "id", False, "identity-keyed"),
        ("SelectionState", ["CandidatePresentationPackageRecord"], ["/semantic/selection_sets/{set_index}/states/{index}"], "id", False, "owner-authored-order"),
        ("PresentationStateProjection", ["CandidatePresentationPackageRecord"], ["/semantic/selection_sets/{set_index}/projections/{index}"], "id", False, "identity-keyed"),
        ("Exhibit", ["CandidatePresentationPackageRecord"], ["/semantic/exhibits/{index}"], "id", True, "identity-keyed"),
        ("CaseBinding", ["CandidatePresentationPackageRecord"], ["/semantic/exhibits/{exhibit_index}/case_bindings/{index}"], "id", True, "identity-keyed-array-position-nonauthoritative-order-field-authoritative"),
        ("TypedRelation", ["CandidatePresentationPackageRecord"], ["/semantic/relations/{index}"], "id", True, "identity-keyed"),
        ("ComparisonUniverse", ["CandidatePresentationPackageRecord"], ["/semantic/comparison_universes/{index}"], "id", False, "identity-keyed"),
        ("DistributionAssertion", ["CandidatePresentationPackageRecord"], ["/semantic/distribution"], "id", False, "identity-keyed"),
        ("GeneratedArtifact", ["GeneratedArtifactAuditRecord"], ["/semantic/artifact"], "id", False, "identity-keyed"),
        ("ConformanceEvidence", ["SemanticArtifactConformanceRecord"], ["/semantic/evidence"], "id", False, "identity-keyed"),
    ]
    entries: list[dict[str, Any]] = []
    for kind in records:
        entries.append({
            "kind": kind, "owning_profile": ["briefforge-core-representation-profile", "1.0.0"],
            "owning_record_kinds": [kind], "canonical_locations": ["/records/{record_index}"],
            "identity_field": "identity", "locator_syntax": "RFC6901-JSON-Pointer-with-decimal-array-index",
            "traversable": True, "counterpart_target": False, "planner_coverage_obligation": False,
            "uniqueness_scope": "complete-profile-instance", "ordering": "record-array-position-nonauthoritative-identity-keyed",
            "normalization": "none-exact-ASCII-case-sensitive", "missing": "reject-missing-core-object",
            "duplicate": "reject-duplicate-core-identity", "ambiguous": "reject-ambiguous-core-locator",
            "unknown": "reject-unknown-core-object-kind", "misplaced": "reject-misplaced-core-object",
        })
    counterpart = {"Section", "PresentationStatement", "Exhibit", "CaseBinding", "MaterializedValue", "TypedRelation", "MaterialProvenance", "Obligation"}
    planner = {"RendererRequirement"}
    for kind, owners, locs, ident, core_anchor, ordering in nested:
        entries.append({
            "kind": kind, "owning_profile": ["briefforge-core-representation-profile", "1.0.0"],
            "owning_record_kinds": owners, "canonical_locations": locs, "identity_field": ident,
            "locator_syntax": "RFC6901-JSON-Pointer-with-decimal-array-index",
            "traversable": True, "counterpart_target": kind in counterpart,
            "paired_cross_domain_anchor": core_anchor, "planner_coverage_obligation": kind in planner,
            "uniqueness_scope": "complete-profile-instance", "ordering": ordering,
            "normalization": "none-exact-ASCII-case-sensitive", "missing": "reject-missing-core-object",
            "duplicate": "reject-duplicate-core-identity", "ambiguous": "reject-ambiguous-core-locator",
            "unknown": "reject-unknown-core-object-kind", "misplaced": "reject-misplaced-core-object",
        })
    return {
        "contract": "briefforge:core-object-kind-location-registry:1.0.0",
        "registry_identity": "registry:briefforge-bcrp-core-object-locations-v1",
        "profile_dispatch": [["briefforge-core-representation-profile", "1.0.0"]],
        "unsupported_version": "reject-unsupported-core-profile-version",
        "namespace_collision": "reject-duplicate-local-identity-within-core-domain;same-local-identity-across-core-and-paired-is-not-collision-or-equality",
        "source_locator_construction": "candidate-identity+profile-byte-digest+record-identity+RFC6901-pointer;locator-is-diagnostic-only",
        "identity_resolution": "record-identity-and-nested-id-only-at-enumerated-locations;never-arbitrary-string-scan-or-structural-resemblance",
        "document_order": "meaning-only-where-entry-ordering-explicitly-says-authoritative",
        "reorder_identity_rule": "reordered-identity-keyed-objects-remain-the-same-authoritative-object-but-change-bytes-and-require-reauthentication;authoritative-order-reordering-rejects",
        "unknown_extensions": "no-semantic-meaning;exact-dispatch-and-preservation-policy-required",
        "counterpart_exclusions": [{"paired_kind": "Section", "paired_field": "order", "reason": "paired-owned-composition-order;core-section-array-position-is-nonauthoritative"}],
        "other_counterpart_exclusions": [],
        "entries": entries,
    }


def locate_core(profile: dict[str, Any], reg: dict[str, Any]) -> tuple[list[list[Any]], dict[str, tuple[list[Any], str, Any]], list[list[Any]]]:
    """Execute the registry, then reproduce frozen bcrp-graph reference discovery.

    Object discovery is deliberately not a recursive resemblance/prefix scan.  A
    value is a core object only when one of the 37 entries selects its exact
    owning record kind, canonical location and identity field.
    """
    domain = ["briefforge:bcrp-core", "1.0.0"]
    nodes: list[list[Any]] = []
    index: dict[str, tuple[list[Any], str, Any]] = {}
    def add(identity: str, kind: str, pointer: str, fragment: Any, record_identity: str) -> None:
        if identity in index: raise ValueError(f"duplicate core identity {identity}")
        dqi = domain + [kind, identity]
        node = [dqi, record_identity, pointer, h("briefforge.task075.source-fragment.v1", fragment)]
        nodes.append(node); index[identity] = (dqi, pointer, fragment)
    def select(value: Any, parts: list[str], pointer: str) -> list[tuple[Any,str]]:
        if not parts: return [(value,pointer)]
        part=parts[0]; rest=parts[1:]; selected=[]
        if part in {"{record_index}","{index}","{set_index}","{exhibit_index}"}:
            if not isinstance(value,list): return []
            for i,child in enumerate(value): selected.extend(select(child,rest,pointer+f"/{i}"))
        elif isinstance(value,dict) and part in value:
            selected.extend(select(value[part],rest,pointer+"/"+ptr_escape(part)))
        return selected
    record_by_pointer={f"/records/{i}":r for i,r in enumerate(profile["records"])}
    executed=[]
    for entry in reg["entries"]:
        matched=0
        for template in entry["canonical_locations"]:
            parts=[x for x in template.split("/") if x]
            # Registry nested locations are owner-record-relative; record-kind
            # entries alone use the absolute /records/{record_index} template.
            if not parts or parts[0] != "records": parts=["records","{record_index}"]+parts
            for fragment,pointer in select(profile,parts,""):
                record_pointer="/".join(pointer.split("/")[:3])
                owner=record_by_pointer.get(record_pointer)
                if not owner or owner["record_kind"] not in entry["owning_record_kinds"]: continue
                identity=fragment.get(entry["identity_field"]) if isinstance(fragment,dict) else None
                if not isinstance(identity,str): raise ValueError(f"missing exact {entry['identity_field']} for {entry['kind']} at {pointer}")
                if entry["kind"] in {x["record_kind"] for x in profile["records"]} and fragment.get("record_kind") != entry["kind"]: continue
                add(identity,entry["kind"],pointer,fragment,owner["identity"]); matched+=1
        executed.append([entry["kind"],matched])
    if len(executed)!=37 or {x[0] for x in executed}!={x["kind"] for x in reg["entries"]}:
        raise ValueError("registry execution did not execute every exact entry")
    reference_list_keys = {"artifact_audit_refs","authority_refs","caveat_ids","children","conformance_refs","evidence_refs","evidence_snapshot_refs","exhibit_ids","expressed_statement_ids","fallback_refs","material_refs","obligation_ids","renderer_requirement_ids","required_value_ids","source_value_refs","state_ids","statement_ids","static_expression","print_expression","target_refs","uncertainty_ids","upstream_refs","value_ids"}
    edges: list[list[Any]] = []
    def collect(value: Any, owner: str, pointer: str) -> None:
        if isinstance(value, dict):
            current = value.get("id") if isinstance(value.get("id"), str) else owner
            for key, child in value.items():
                p = pointer + "/" + ptr_escape(key)
                targets: list[tuple[int,str]] = []
                if key.endswith("_ref") and isinstance(child, str): targets=[(0,child)]
                elif (key.endswith("_refs") or key in reference_list_keys) and isinstance(child,list): targets=[(i,x) for i,x in enumerate(child) if isinstance(x,str)]
                for ordinal,target in targets:
                    if target not in index: raise ValueError(f"dangling core target {target} at {p}")
                    sdqi=index[current][0] if current in index else index[owner][0]; tdqi=index[target][0]
                    attrs={"source_pointer":pointer,"source_field":key,"target_kind":tdqi[2]}
                    edges.append([sdqi,key,ordinal,tdqi,h("briefforge.task075.edge-attributes.v1",attrs)])
                collect(child,current,p)
        elif isinstance(value,list):
            for i,child in enumerate(value): collect(child,owner,pointer+f"/{i}")
    # Frozen bcrp-graph:1.0.0 scans both semantic and extensions.  TASK-071's
    # paired envelope contributes exactly authority_ref and target_refs edges.
    for i,record in enumerate(profile["records"]):
        collect(record["semantic"],record["identity"],f"/records/{i}/semantic")
        collect(record["extensions"],record["identity"],f"/records/{i}/extensions")
    nodes.sort(key=lambda x:cbytes(x[0])); edges.sort(key=lambda x:(cbytes(x[0]),x[1].encode(),x[2],cbytes(x[3]),x[4]))
    return nodes,index,edges


def paired_population(profile: dict[str, Any], core_index: dict[str, tuple[list[Any],str,Any]]) -> tuple[dict[str,Any],list[list[Any]],dict[str,tuple[list[Any],str,Any]],list[list[Any]]]:
    cand = next(x for x in profile["records"] if x["record_kind"] == "CandidatePresentationPackageRecord")
    ext = cand["extensions"][0]; sem = json.loads(ext["payload"]["canonical_semantics"])
    domain=["briefforge:paired-terminal","3.0.0"]
    specs=[("Section",sem["sections"],"/sections"),("Statement",sem["statements"],"/statements"),("Table",[sem["table"]],"/table"),("Row",sem["table"]["rows"],"/table/rows"),("Value",sem["values"],"/values"),("Qualification",sem["qualifications"],"/qualifications"),("Provenance",sem["provenance"],"/provenance"),("Obligation",sem["obligations"],"/obligations")]
    nodes=[]; index={}
    for kind,items,base in specs:
        for i,item in enumerate(items):
            pointer=base if kind=="Table" else f"{base}/{i}"; ident=item["identity"]
            if ident in index: raise ValueError(f"duplicate paired identity {ident}")
            dqi=domain+[kind,ident]; node=[dqi,pointer,h("briefforge.task075.source-fragment.v1",item)]
            nodes.append(node); index[ident]=(dqi,pointer,item)
    edge_specs=[]
    def edge(src:str, field:str, relation:str, target:str, ordinal:int=0):
        if target in index: target_data=index[target]
        elif target in core_index: target_data=core_index[target]
        else: raise ValueError(f"dangling paired target {target}")
        sdqi,sptr,_=index[src]; tdqi=target_data[0]
        attrs={"source_pointer":sptr,"source_field":field,"target_kind":tdqi[2]}
        edge_specs.append([sdqi,relation,ordinal,tdqi,h("briefforge.task075.edge-attributes.v1",attrs)])
    for sec in sem["sections"]:
        for i,ch in enumerate(sec["children"]): edge(sec["identity"],"children","ordered-child",ch["target_ref"],i)
    table=sem["table"]; edge(table["identity"],"purpose_ref","purpose",table["purpose_ref"]); edge(table["identity"],"authority_ref","authority",table["authority_ref"])
    for i,row in enumerate(table["rows"]): edge(table["identity"],"rows","ordered-row",row["identity"],i)
    for st in sem["statements"]: edge(st["identity"],"authority_ref","authority",st["authority_ref"])
    for row in table["rows"]:
        for f,r in [("row_statement_ref","row-statement"),("raw_value_ref","raw-value"),("first_difference_value_ref","first-difference-value")]: edge(row["identity"],f,r,row[f])
        for f,r in [("qualification_refs","qualification"),("provenance_refs","provenance")]:
            for i,t in enumerate(row[f]): edge(row["identity"],f,r,t,i)
    for val in sem["values"]:
        for f,r in [("unit_ref","unit"),("semantic_type_ref","semantic-type"),("source_ref","source"),("authority_ref","authority")]: edge(val["identity"],f,r,val[f])
    for q in sem["qualifications"]:
        for f,r in [("source_ref","qualification-source"),("target_ref","qualification-target"),("authority_ref","authority")]: edge(q["identity"],f,r,q[f])
    for p in sem["provenance"]:
        for i,t in enumerate(p["target_refs"]): edge(p["identity"],"target_refs","provenance-target",t,i)
        edge(p["identity"],"placement_ref","placement",p["placement_ref"])
        # Paired-v3 source_snapshot_identity is an owner-typed source token.  The
        # exact TASK-071 token is not a BCRP EvidenceSnapshot identity, so it is
        # committed as a node attribute and never promoted by resemblance.
        edge(p["identity"],"authority_ref","authority",p["authority_ref"])
    for o in sem["obligations"]:
        for i,t in enumerate(o["target_refs"]): edge(o["identity"],"target_refs","obligation-target",t,i)
        edge(o["identity"],"placement_ref","placement",o["placement_ref"]); edge(o["identity"],"authority_ref","authority",o["authority_ref"])
    nodes.sort(key=lambda x:cbytes(x[0])); edge_specs.sort(key=lambda x:(cbytes(x[0]),x[1].encode(),x[2],cbytes(x[3]),x[4]))
    return sem,nodes,index,edge_specs


def counterpart_records(sem:dict[str,Any], pindex:dict[str,tuple[list[Any],str,Any]], cindex:dict[str,tuple[list[Any],str,Any]]) -> list[list[Any]]:
    items=[("Section",sem["sections"]),("Statement",sem["statements"]),("Table",[sem["table"]]),("Row",sem["table"]["rows"]),("Value",sem["values"]),("Qualification",sem["qualifications"]),("Provenance",sem["provenance"]),("Obligation",sem["obligations"])]
    rules={
      "Section":[(0,"identity","id","EXACT_JSON_V1"),(1,"title","title","EXACT_JSON_V1"),(2,"children","children","ORDERED_REF_ARRAY_V1")],
      "Statement":[(3,"identity","id","EXACT_JSON_V1"),(4,"text","text","EXACT_JSON_V1"),(5,"role","posture","EXACT_JSON_V1"),(6,"authority_ref","authority_ref","EXACT_JSON_V1")],
      "Table":[(7,"identity","id","EXACT_JSON_V1"),(8,"column_identities","column_ids","TABLE_COLUMN_ID_PERMUTE_4_2_3_0_1_V1"),(9,"column_headings","headings","TABLE_HEADING_PERMUTE_4_2_3_0_1_V1")],
      "Row":[(10,"identity","id","EXACT_JSON_V1"),(11,"order","order","EXACT_JSON_V1"),(12,"relationship_identity","relationship_identity","EXACT_JSON_V1"),(13,"relationship_label","relationship_label","EXACT_JSON_V1"),(14,"raw_value_ref","primary_ref","EXACT_JSON_V1"),(15,"first_difference_value_ref","comparison_ref","EXACT_JSON_V1")],
      "Value":[(16,"identity","id","EXACT_JSON_V1"),(17,"value_state","value_state","EXACT_JSON_V1"),(18,"@decimal","payload","SCALED_INTEGER_DECIMAL_V1"),(19,"scale","payload/scale","EXACT_JSON_V1"),(20,"lexical_representation","lexical_representation","EXACT_JSON_V1"),(21,"unit_ref","unit_ref","EXACT_JSON_V1"),(22,"semantic_type_ref","semantic_type_ref","EXACT_JSON_V1"),(23,"source_ref","source_ref","EXACT_JSON_V1"),(24,"authority_ref","authority_ref","EXACT_JSON_V1"),(25,"method_ref","method","EXACT_JSON_V1"),(26,"transformation_identity","transformation","EXACT_JSON_V1"),(27,"transformation_state","transformation_state","EXACT_JSON_V1"),(28,"aligned_period","aligned_period","EXACT_JSON_V1"),(29,"aligned_count","aligned_count","EXACT_JSON_V1"),(30,"package_identity","package_id","EXACT_JSON_V1")],
      "Qualification":[(31,"identity","id","EXACT_JSON_V1"),(32,"kind","kind","EXACT_JSON_V1"),(33,"source_ref","source_ref","EXACT_JSON_V1"),(34,"target_ref","target_ref","EXACT_JSON_V1"),(35,"authority_ref","authority_ref","EXACT_JSON_V1"),(36,"target_order","declared_target_order","EXACT_JSON_V1")],
      "Provenance":[(37,"identity","id","EXACT_JSON_V1"),(38,"citation","citation","EXACT_JSON_V1"),(39,"authority_ref","authority_ref","EXACT_JSON_V1"),(40,"target_refs","target_refs","SORTED_UTF8_SET_V1")],
      "Obligation":[(41,"identity","id","EXACT_JSON_V1"),(42,"kind","kind","EXACT_JSON_V1"),(43,"target_refs","target_refs","SORTED_UTF8_SET_V1"),(44,"authority_ref","authority_ref","EXACT_JSON_V1")],
    }
    def get(v:Any,path:str):
        for part in path.split("/"): v=v[part]
        return v
    records=[]
    for kind,objs in items:
      for po in objs:
        ident=po["identity"]
        if ident not in cindex: raise ValueError(f"missing counterpart {ident}")
        co=cindex[ident][2]; results=[]
        for ordinal,pp,cp,norm in rules[kind]:
            if pp=="@decimal": pv={"coefficient":str(po["coefficient"]),"scale":po["scale"]}; cv={"coefficient":str(co["payload"]["coefficient"]),"scale":co["payload"]["scale"]}; pptr=pindex[ident][1]; cptr=cindex[ident][1]
            else:
                pv=get(po,pp); cv=get(co,cp); pptr=pindex[ident][1]+"/"+pp.replace("/","/"); cptr=cindex[ident][1]+"/"+cp
                if norm.startswith("TABLE_"): cv=[cv[i] for i in (4,2,3,0,1)]
                if norm=="ORDERED_REF_ARRAY_V1": pv=[x["target_ref"] for x in pv]
                if norm=="SORTED_UTF8_SET_V1": pv=sorted(pv,key=lambda x:x.encode()); cv=sorted(cv,key=lambda x:x.encode())
            if pv!=cv: raise ValueError(f"counterpart mismatch {kind} {ident} rule {ordinal}: {pv!r} != {cv!r}")
            results.append([ordinal,pptr,cptr,norm,pv,cv,True])
        pfrag=pindex[ident][2]; cfrag=cindex[ident][2]
        records.append([pindex[ident][0],cindex[ident][0],kind,"briefforge:paired-core-counterpart-proof:1.0.0",h("briefforge.task075.source-fragment.v1",pfrag),h("briefforge.task075.source-fragment.v1",cfrag),results])
    records.sort(key=lambda x:cbytes(x[0]))
    if len(records)!=144 or len({cbytes(x[1]) for x in records})!=144: raise ValueError("counterpart bijection is not 144")
    return records


def schemas(registry_artifact:dict[str,Any], envelope_artifact:dict[str,Any], capability_artifact:dict[str,Any], plan_artifact:dict[str,Any]) -> dict[str,dict[str,Any]]:
    """Closed production-shape schemas; each exact generated artifact validates."""
    digest={"type":"string","pattern":"^[0-9a-f]{64}$"}; ident={"type":"string","pattern":"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*$"}
    text={"type":"string","minLength":1}; integer={"type":"integer","minimum":0}
    def obj(required:list[str], properties:dict[str,Any])->dict[str,Any]:
        return {"type":"object","additionalProperties":False,"required":required,"properties":properties}
    counts_keys=["core_nodes","core_edges","paired_nodes","paired_edges","counterparts","sections","statements","tables","rows","values","qualifications","provenance","obligations"]
    env_fields=["contract","evidence_identity","issuer_identity","verifier_identity","implementation_contract","implementation_digest","registry_identity","registry_digest","bcrp_profile","paired_profile","candidate_identity","candidate_profile_instance_fingerprint","candidate_profile_byte_digest","source_locator_identity","extension_tuple","extension_envelope_digest","paired_payload_digest","paired_closure_digest","decoded_paired_population_digest","decoded_paired_object_count","core_graph_digest","paired_graph_digest","counterpart_proof_digest","effective_graph_digest","requirement_inventory_digest","mapping_inventory_digest","mapping_count","decoded_row_count","counts","counterpart_exclusions","graph_emission_classifications","invariant_results","findings","rejection_state","operation_identity","authorization_fingerprint","issued_at_utc","fingerprint"]
    ep={k:copy.deepcopy(digest) for k in env_fields if k.endswith("digest") or k.endswith("fingerprint")}
    ep.update({"contract":{"const":"briefforge:paired-semantic-derivation-evidence:2.0.0"},"evidence_identity":ident,"issuer_identity":{"const":"briefforge:paired-semantic-derivation-issuer:2.0.0"},"verifier_identity":{"const":"briefforge:paired-semantic-derivation-verifier:2.0.0"},"implementation_contract":{"const":"briefforge:effective-semantic-graph-derivation:1.0.0"},"registry_identity":ident,"bcrp_profile":{"const":["briefforge-core-representation-profile","1.0.0"]},"paired_profile":{"const":["briefforge:representative-paired-terminal-static-html-profile","3.0.0"]},"candidate_identity":ident,"source_locator_identity":ident,
      "extension_tuple":{"type":"array","prefixItems":[{"const":"briefforge-paired-terminal-profile"},{"const":"paired-semantic-input"},{"const":"3.0.0"},ident,{"const":"candidate-paired-semantic-input"},{"type":"array","items":ident,"minItems":1,"uniqueItems":True},{"const":"required"},{"const":"semantic"},{"const":"bcrp:core-extension-envelope:1.0.0"},{"const":"must-preserve"},{"const":"briefforge:representative-paired-terminal-semantic-input:3.0.0"},{"const":"3.0.0"}],"minItems":12,"maxItems":12},
      "decoded_paired_object_count":integer,"mapping_count":integer,"decoded_row_count":integer,"counts":obj(counts_keys,{k:integer for k in counts_keys}),
      "counterpart_exclusions":{"const":[["Section","order","paired-owned;core-array-position-nonauthoritative"]]},
      "graph_emission_classifications":{"const":[["Provenance","source_snapshot_identity","owner-typed-token-not-core-reference-for-task071;emit-snapshot-edge-only-when-exact-EvidenceSnapshot-resolves"]]},
      "invariant_results":{"const":envelope_artifact["invariant_results"]},"findings":{"const":[]},"rejection_state":{"const":"none"},"operation_identity":ident,"issued_at_utc":{"type":"string","format":"date-time","pattern":"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"}})
    env={"$schema":"https://json-schema.org/draft/2020-12/schema","$id":"briefforge:paired-semantic-derivation-evidence:2.0.0",**obj(env_fields,ep)}

    tuple3={"type":"array","prefixItems":[text,text,digest],"minItems":3,"maxItems":3}
    mapping_claim=obj(["contract","profiles","mode"],{"contract":{"const":"briefforge:paired-row-relationship-static-table:1.0.0"},"profiles":{"type":"array","minItems":1,"items":{"type":"array","prefixItems":[text,text],"minItems":2,"maxItems":2}},"mode":{"const":"static"}})
    cap_keys=["contract","declaration_identity","renderer_identity","implementation_identity","implementation_digest","owner_identity","owner_role","profile","media_types","output_count","asset_count","table_count","column_count","mapping_capability","semantic_digest","operation_identity","authorization_fingerprint","storage_identity","issued_at_utc","fingerprint"]
    cap_props={"contract":{"const":"briefforge:renderer-capability-declaration:2.0.0"},"declaration_identity":ident,"renderer_identity":ident,"implementation_identity":ident,"implementation_digest":digest,"semantic_digest":digest,"owner_identity":ident,"owner_role":text,"profile":{"const":["briefforge:representative-paired-terminal-static-html-profile","3.0.0"]},"media_types":{"type":"array","minItems":1,"uniqueItems":True,"items":text},"mapping_capability":mapping_claim,"operation_identity":ident,"authorization_fingerprint":digest,"storage_identity":ident,"issued_at_utc":{"type":"string","format":"date-time","pattern":"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"},"fingerprint":digest,**{k:integer for k in ["output_count","asset_count","table_count","column_count"]}}
    cap_sem_keys=list(capability_artifact["semantic"])
    cap_sem=obj(cap_sem_keys,{"renderer_id":ident,"renderer_version":text,"capabilities":{"const":["renderer","media-type","output-count","asset-count","table-count","column-count","paired-row-mapping"]},"declaration_identity":ident,"capability_profile_identity":{"const":"briefforge-renderer-capability-profile"},"capability_profile_version":{"const":"2.0.0"},"declaration_time":{"type":"string","format":"date-time","pattern":"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"},"inventory_complete":{"const":True},"unsupported_capabilities":{"type":"array","items":text,"uniqueItems":True},"declared_constraints":{"type":"array","items":text,"uniqueItems":True},"claim_character":{"const":"renderer-owned-claim-not-conformance-proof"}})

    req_item={"type":"array","prefixItems":[integer,text,text,{"const":"briefforge:renderer-capability-declaration:2.0.0"},digest,text,{},text,{"enum":["supported","unsupported"]},{"type":["string","null"]}],"minItems":10,"maxItems":10}
    graph_ref={"type":"array","prefixItems":[digest,digest,{"type":"array","prefixItems":[{"const":"briefforge:paired-terminal"},{"const":"3.0.0"},{"const":"Row"},ident],"minItems":4,"maxItems":4}],"minItems":3,"maxItems":3}
    map_item={"type":"array","prefixItems":[integer,graph_ref,text,{"const":"briefforge:paired-row-relationship-static-table:1.0.0"},{"const":"briefforge:renderer-capability-declaration:2.0.0"},digest,mapping_claim,{"const":"mapping-expression-exact-v1"},{"enum":["supported","unsupported"]},{"type":["string","null"]}],"minItems":10,"maxItems":10}
    plan_keys=["contract","plan_identity","candidate_profile_instance_fingerprint","judgment_fingerprint","ready_fingerprint","release_identity","release_fingerprint","release_closure_digest","capability_identity","capability_fingerprint","capability_contract","resolver","derivation","derivation_evidence_fingerprint","core_graph_digest","paired_graph_digest","counterpart_proof_digest","effective_graph_digest","paired_closure_digest","requirement_inventory_digest","mapping_inventory_digest","requirement_outcomes_digest","mapping_outcomes_digest","requirement_outcomes","mapping_outcomes","planning_completeness_digest","semantic_digest","mode","supported","findings","operation_identity","authorization_fingerprint","fingerprint"]
    plan_props={k:copy.deepcopy(digest) for k in plan_keys if k.endswith("digest") or k.endswith("fingerprint")}
    plan_props.update({"contract":{"const":"briefforge:renderer-compatibility-plan:2.0.0"},"plan_identity":ident,"release_identity":ident,"capability_identity":ident,"capability_contract":{"const":"briefforge:renderer-capability-declaration:2.0.0"},"resolver":tuple3,"derivation":tuple3,"requirement_outcomes":{"type":"array","minItems":6,"maxItems":6,"items":req_item},"mapping_outcomes":{"type":"array","minItems":0,"maxItems":16,"items":map_item},"mode":{"const":"paired-v3-static"},"supported":{"type":"boolean"},"findings":{"type":"array"},"operation_identity":ident})
    plan_sem_keys=list(plan_artifact["semantic"]); plan_sem=obj(plan_sem_keys,{"ready_ref":ident,"renderer_capability_ref":ident,"declared_transformations":{"type":"array","items":text},"fallbacks":{"type":"array","items":text},"supported":{"type":"boolean"},"mode":{"const":"paired-v3-static"}})
    extension_keys=["owner_namespace","name","version","authority_ref","scope","target_refs","criticality","character","validation_contract","preservation","payload"]
    def record_schema(kind:str, owner:str, name:str, authority:str, scope:str, contract:str, payload:dict[str,Any], semantic:dict[str,Any], targets:int)->dict[str,Any]:
        ext_props={"owner_namespace":{"const":owner},"name":{"const":name},"version":{"const":"2.0.0"},"authority_ref":{"const":authority},"scope":{"const":scope},"target_refs":{"type":"array","minItems":targets,"maxItems":targets,"items":ident,"uniqueItems":True},"criticality":{"const":"required"},"character":{"const":"semantic"},"validation_contract":{"const":contract},"preservation":{"const":"must-preserve"},"payload":payload}
        ext=obj(extension_keys,ext_props)
        top=obj(["record_kind","identity","profile","semantic","extensions"],{"record_kind":{"const":kind},"identity":ident,"profile":{"const":{"identity":"briefforge-core-representation-profile","version":"1.0.0"}},"semantic":semantic,"extensions":{"type":"array","prefixItems":[ext],"minItems":1,"maxItems":1}})
        return {"$schema":"https://json-schema.org/draft/2020-12/schema","$id":contract+":record-schema",**top}
    entry_common=["kind","owning_profile","owning_record_kinds","canonical_locations","identity_field","locator_syntax","traversable","counterpart_target","planner_coverage_obligation","uniqueness_scope","ordering","normalization","missing","duplicate","ambiguous","unknown","misplaced"]
    entry_props={"kind":text,"owning_profile":{"const":["briefforge-core-representation-profile","1.0.0"]},"owning_record_kinds":{"type":"array","minItems":1,"uniqueItems":True,"items":text},"canonical_locations":{"type":"array","minItems":1,"uniqueItems":True,"items":{"type":"string","pattern":"^/"}},"identity_field":{"enum":["identity","id"]},"locator_syntax":text,"traversable":{"const":True},"counterpart_target":{"type":"boolean"},"planner_coverage_obligation":{"type":"boolean"},"uniqueness_scope":text,"ordering":text,"normalization":text,"missing":text,"duplicate":text,"ambiguous":text,"unknown":text,"misplaced":text,"paired_cross_domain_anchor":{"type":"boolean"}}
    reg_keys=["contract","registry_identity","profile_dispatch","unsupported_version","namespace_collision","source_locator_construction","identity_resolution","document_order","reorder_identity_rule","unknown_extensions","counterpart_exclusions","other_counterpart_exclusions","entries","registry_digest"]
    reg_props={k:text for k in reg_keys if k not in {"contract","profile_dispatch","counterpart_exclusions","other_counterpart_exclusions","entries","registry_digest"}}
    reg_props.update({"contract":{"const":"briefforge:core-object-kind-location-registry:1.0.0"},"profile_dispatch":{"const":[["briefforge-core-representation-profile","1.0.0"]]},"counterpart_exclusions":{"const":registry_artifact["counterpart_exclusions"]},"other_counterpart_exclusions":{"const":[]},"entries":{"type":"array","minItems":37,"maxItems":37,"uniqueItems":True,"items":{"oneOf":[obj(entry_common,{k:v for k,v in entry_props.items() if k!="paired_cross_domain_anchor"}),obj(entry_common+["paired_cross_domain_anchor"],entry_props)]}},"registry_digest":digest})
    registry_schema={"$schema":"https://json-schema.org/draft/2020-12/schema","$id":"briefforge:core-object-kind-location-registry:1.0.0:schema",**obj(reg_keys,reg_props)}
    return {
        "core-object-kind-location-registry.schema.json":registry_schema,
        "derivation-evidence-envelope.schema.json":env,
        "capability-v2-record.schema.json":record_schema("RendererCapabilityDeclarationRecord","briefforge-renderer-capability","renderer-capability-declaration","authority:briefforge-renderer-capability-declaration","renderer-capability-declaration","briefforge:renderer-capability-declaration:2.0.0",obj(cap_keys,cap_props),cap_sem,1),
        "plan-v2-record.schema.json":record_schema("RendererCompatibilityPlanRecord","briefforge-renderer-compatibility-planning","renderer-compatibility-plan","authority:briefforge-renderer-compatibility-planning","renderer-compatibility-plan","briefforge:renderer-compatibility-plan:2.0.0",obj(plan_keys,plan_props),plan_sem,4),
    }


def build() -> None:
    raw=PROFILE.read_bytes()
    if sha(raw)!=PROFILE_SHA: raise ValueError("TASK-071 profile bytes changed")
    profile=json.loads(raw)
    reg=registry(); reg_digest=h("briefforge.task076.core-registry.v1",reg)
    reg["registry_digest"]=reg_digest
    core_nodes,cindex,core_edges=locate_core(profile,reg)
    sem,pnodes,pindex,pedges=paired_population(profile,cindex)
    counterparts=counterpart_records(sem,pindex,cindex)
    ext=next(x for x in profile["records"] if x["record_kind"]=="CandidatePresentationPackageRecord")["extensions"][0]
    paired_raw=ext["payload"]["canonical_semantics"].encode()
    core_graph={"contract":"briefforge:verified-core-semantic-graph:1.0.0","candidate_profile_instance_fingerprint":CANDIDATE_FP,"domain":["briefforge:bcrp-core","1.0.0"],"nodes":core_nodes,"edges":core_edges,"source_digest":h("briefforge.task075.source-fragment.v1",profile)}
    paired_graph={"contract":"briefforge:verified-paired-semantic-graph:1.0.0","candidate_profile_instance_fingerprint":CANDIDATE_FP,"domain":["briefforge:paired-terminal","3.0.0"],"nodes":pnodes,"edges":pedges,"source_digest":h("briefforge.task075.paired-payload.v1",paired_raw,True)}
    core_digest=h("briefforge.task075.core-graph.v1",core_graph); paired_digest=h("briefforge.task075.paired-graph.v1",paired_graph); counterpart_digest=h("briefforge.task075.counterpart-proof.v1",counterparts)
    effective={"contract":"briefforge:verified-effective-semantic-graph:1.0.0","candidate_profile_instance_fingerprint":CANDIDATE_FP,"core_graph_digest":core_digest,"paired_graph_digest":paired_digest,"counterpart_proof_digest":counterpart_digest,"nodes":core_nodes+pnodes,"edges":core_edges+pedges}
    effective_digest=h("briefforge.task075.effective-graph.v1",effective)
    requirements=[[i,x[0],x[1]] for i,x in enumerate(sem["renderer_requirements"])]
    mappings=[[i,[CANDIDATE_FP,effective_digest,pindex[row][0]],rel] for i,(row,rel) in enumerate(sem["renderer_mappings"])]
    req_digest=h("briefforge.task075.requirement-inventory.v1",requirements); map_digest=h("briefforge.task075.mapping-inventory.v1",mappings)
    populations={"contract":"briefforge:task076-derived-populations-fixture:1.0.0","fixture_character":"non-authority-contract-test-vector","candidate_profile_byte_digest":PROFILE_SHA,"candidate_profile_instance_fingerprint":CANDIDATE_FP,"core_graph":core_graph,"paired_graph":paired_graph,"counterpart_records":counterparts,"effective_graph":effective,"requirement_inventory":requirements,"mapping_inventory":mappings}
    implementation_digest=sha(Path(__file__).read_bytes())
    env={"contract":"briefforge:paired-semantic-derivation-evidence:2.0.0","evidence_identity":"evidence:task076-task071-representability","issuer_identity":"briefforge:paired-semantic-derivation-issuer:2.0.0","verifier_identity":"briefforge:paired-semantic-derivation-verifier:2.0.0","implementation_contract":"briefforge:effective-semantic-graph-derivation:1.0.0","implementation_digest":implementation_digest,"registry_identity":reg["registry_identity"],"registry_digest":reg_digest,"bcrp_profile":["briefforge-core-representation-profile","1.0.0"],"paired_profile":["briefforge:representative-paired-terminal-static-html-profile","3.0.0"],"candidate_identity":"candidate:task071-cross-inquiry","candidate_profile_instance_fingerprint":CANDIDATE_FP,"candidate_profile_byte_digest":PROFILE_SHA,"source_locator_identity":"storage:task071-canonical-profile","extension_tuple":[ext["owner_namespace"],ext["name"],ext["version"],ext["authority_ref"],ext["scope"],ext["target_refs"],ext["criticality"],ext["character"],ext["validation_contract"],ext["preservation"],ext["payload"]["contract_identity"],ext["payload"]["contract_version"]],"extension_envelope_digest":h("briefforge.task075.extension-envelope.v1",ext),"paired_payload_digest":h("briefforge.task075.paired-payload.v1",paired_raw,True),"paired_closure_digest":h("briefforge.task075.paired-closure.v1",sem),"decoded_paired_population_digest":h("briefforge.task076.decoded-paired-population.v1",pnodes),"decoded_paired_object_count":len(pnodes),"core_graph_digest":core_digest,"paired_graph_digest":paired_digest,"counterpart_proof_digest":counterpart_digest,"effective_graph_digest":effective_digest,"requirement_inventory_digest":req_digest,"mapping_inventory_digest":map_digest,"mapping_count":len(mappings),"decoded_row_count":len(sem["table"]["rows"]),"counts":{"core_nodes":len(core_nodes),"core_edges":len(core_edges),"paired_nodes":len(pnodes),"paired_edges":len(pedges),"counterparts":len(counterparts),"sections":len(sem["sections"]),"statements":len(sem["statements"]),"tables":1,"rows":len(sem["table"]["rows"]),"values":len(sem["values"]),"qualifications":len(sem["qualifications"]),"provenance":len(sem["provenance"]),"obligations":len(sem["obligations"])},"counterpart_exclusions":[["Section","order","paired-owned;core-array-position-nonauthoritative"]],"graph_emission_classifications":[["Provenance","source_snapshot_identity","owner-typed-token-not-core-reference-for-task071;emit-snapshot-edge-only-when-exact-EvidenceSnapshot-resolves"]],"invariant_results":[[x,"pass"] for x in ["exact-profile-dispatch","complete-decode","canonical-reencode-equality","unique-paired-identities","closed-edge-emission","core-registry-resolution","counterpart-bijection","counterpart-nontraversability","six-requirements","all-owner-mappings","mapping-count-equals-decoded-row-count","effective-graph-derived-only"]],"findings":[],"rejection_state":"none","operation_identity":"operation:task076-contract-fixture","authorization_fingerprint":h("briefforge.task076.fixture-authorization.v1",["TASK-076","non-authority"]),"issued_at_utc":"2026-08-11T00:00:00Z"}
    env["fingerprint"]=h("briefforge.task076.derivation-evidence.v2",env)
    # Capability-v2 exact normative non-authority fixture.
    mapping_claim={"contract":"briefforge:paired-row-relationship-static-table:1.0.0","profiles":[["briefforge:representative-paired-terminal-static-html-profile","3.0.0"]],"mode":"static"}
    cap_semantic={"renderer_id":"briefforge:representative-paired-static-html-renderer:1.0.0","renderer_version":"1.0.0","capabilities":["renderer","media-type","output-count","asset-count","table-count","column-count","paired-row-mapping"],"declaration_identity":"capability:task076-normative-v2","capability_profile_identity":"briefforge-renderer-capability-profile","capability_profile_version":"2.0.0","declaration_time":"2026-08-11T00:00:00Z","inventory_complete":True,"unsupported_capabilities":[],"declared_constraints":["deterministic","bounded","offline"],"claim_character":"renderer-owned-claim-not-conformance-proof"}
    cap_payload={"contract":"briefforge:renderer-capability-declaration:2.0.0","declaration_identity":"capability:task076-normative-v2","renderer_identity":"briefforge:representative-paired-static-html-renderer:1.0.0","implementation_identity":"briefforge:paired-static-html-renderer:1.0.0","implementation_digest":h("briefforge.task076.fixture-implementation.v1",["renderer","1.0.0"]),"owner_identity":"project:BriefForge","owner_role":"bounded-publication-renderer","profile":["briefforge:representative-paired-terminal-static-html-profile","3.0.0"],"media_types":["text/html;charset=utf-8"],"output_count":1,"asset_count":0,"table_count":1,"column_count":5,"mapping_capability":mapping_claim,"semantic_digest":h("briefforge.task076.capability-core-semantic.v1",cap_semantic),"operation_identity":"operation:task076-capability-fixture","authorization_fingerprint":h("briefforge.task076.fixture-authorization.v1",["capability","non-authority"]),"storage_identity":"storage:task076-capability-normative-bytes","issued_at_utc":"2026-08-11T00:00:00Z"}
    cap_payload["fingerprint"]=h("briefforge.task075.capability-declaration.v2",cap_payload)
    cap_ext={"owner_namespace":"briefforge-renderer-capability","name":"renderer-capability-declaration","version":"2.0.0","authority_ref":"authority:briefforge-renderer-capability-declaration","scope":"renderer-capability-declaration","target_refs":[cap_payload["declaration_identity"]],"criticality":"required","character":"semantic","validation_contract":"briefforge:renderer-capability-declaration:2.0.0","preservation":"must-preserve","payload":cap_payload}
    cap_record={"record_kind":"RendererCapabilityDeclarationRecord","identity":cap_payload["declaration_identity"],"profile":{"identity":"briefforge-core-representation-profile","version":"1.0.0"},"semantic":cap_semantic,"extensions":[cap_ext]}
    # Plan-v2 exact normative non-authority fixture.
    capability_contract=cap_payload["contract"]; capfp=cap_payload["fingerprint"]
    expected=[("renderer","renderer_identity","renderer-exact-v1","briefforge:representative-paired-static-html-renderer:1.0.0",cap_payload["renderer_identity"]),("media-type","media_types","media-type-member-v1","text/html;charset=utf-8",cap_payload["media_types"]),("output-count","output_count","integer-text-equality-v1","1",1),("asset-count","asset_count","integer-text-equality-v1","0",0),("table-count","table_count","integer-text-equality-v1","1",1),("column-count","column_count","integer-text-equality-v1","5",5)]
    req_out=[[i,key,owner,capability_contract,capfp,claim,actual,policy,"supported",None] for i,(key,claim,policy,owner,actual) in enumerate(expected)]
    map_out=[[i,rowref,rel,"briefforge:paired-row-relationship-static-table:1.0.0",capability_contract,capfp,mapping_claim,"mapping-expression-exact-v1","supported",None] for i,(_,rowref,rel) in enumerate(mappings)]
    req_out_digest=h("briefforge.task075.requirement-outcomes.v1",req_out); map_out_digest=h("briefforge.task075.mapping-outcomes.v1",map_out)
    release_fp=h("briefforge.task076.fixture-binding.v1",["release"]); judgment_fp=h("briefforge.task076.fixture-binding.v1",["judgment"]); ready_fp=h("briefforge.task076.fixture-binding.v1",["ready"]); release_closure=h("briefforge.task076.fixture-binding.v1",["release-closure"])
    completeness={"contract":"briefforge:planning-completeness-evidence:1.0.0","candidate_profile_instance_fingerprint":CANDIDATE_FP,"release_fingerprint":release_fp,"capability_fingerprint":capfp,"derivation_evidence_fingerprint":env["fingerprint"],"effective_graph_digest":effective_digest,"paired_closure_digest":env["paired_closure_digest"],"requirement_inventory_digest":req_digest,"mapping_inventory_digest":map_digest,"requirement_outcomes_digest":req_out_digest,"mapping_outcomes_digest":map_out_digest,"requirement_outcomes":req_out,"mapping_outcomes":map_out,"mapping_count":len(map_out),"findings":[],"supported":True}
    plan_semantic={"ready_ref":"ready:task076-normative-v2","renderer_capability_ref":cap_payload["declaration_identity"],"declared_transformations":[],"fallbacks":[],"supported":True,"mode":"paired-v3-static"}
    plan_payload={"contract":"briefforge:renderer-compatibility-plan:2.0.0","plan_identity":"plan:task076-normative-v2","candidate_profile_instance_fingerprint":CANDIDATE_FP,"judgment_fingerprint":judgment_fp,"ready_fingerprint":ready_fp,"release_identity":"release:task076-normative-v2","release_fingerprint":release_fp,"release_closure_digest":release_closure,"capability_identity":cap_payload["declaration_identity"],"capability_fingerprint":capfp,"capability_contract":capability_contract,"resolver":["briefforge:paired-semantic-resolver","1.0.0",implementation_digest],"derivation":["briefforge:effective-semantic-graph-derivation","1.0.0",implementation_digest],"derivation_evidence_fingerprint":env["fingerprint"],"core_graph_digest":core_digest,"paired_graph_digest":paired_digest,"counterpart_proof_digest":counterpart_digest,"effective_graph_digest":effective_digest,"paired_closure_digest":env["paired_closure_digest"],"requirement_inventory_digest":req_digest,"mapping_inventory_digest":map_digest,"requirement_outcomes_digest":req_out_digest,"mapping_outcomes_digest":map_out_digest,"requirement_outcomes":req_out,"mapping_outcomes":map_out,"planning_completeness_digest":h("briefforge.task075.planning-completeness.v1",completeness),"semantic_digest":h("briefforge.task076.plan-core-semantic.v1",plan_semantic),"mode":"paired-v3-static","supported":True,"findings":[],"operation_identity":"operation:task076-plan-fixture","authorization_fingerprint":h("briefforge.task076.fixture-authorization.v1",["plan","non-authority"])}
    plan_payload["fingerprint"]=h("briefforge.task075.plan-extension.v2",plan_payload)
    plan_ext={"owner_namespace":"briefforge-renderer-compatibility-planning","name":"renderer-compatibility-plan","version":"2.0.0","authority_ref":"authority:briefforge-renderer-compatibility-planning","scope":"renderer-compatibility-plan","target_refs":[plan_payload["plan_identity"],"candidate:task071-cross-inquiry",plan_payload["release_identity"],plan_payload["capability_identity"]],"criticality":"required","character":"semantic","validation_contract":"briefforge:renderer-compatibility-plan:2.0.0","preservation":"must-preserve","payload":plan_payload}
    plan_record={"record_kind":"RendererCompatibilityPlanRecord","identity":plan_payload["plan_identity"],"profile":{"identity":"briefforge-core-representation-profile","version":"1.0.0"},"semantic":plan_semantic,"extensions":[plan_ext]}
    invalid_ids=[
      ("candidate-a-evidence-b","foreign-candidate-evidence"),("registry-a-declares-b","foreign-registry-identity"),("same-registry-identity-different-bytes","registry-digest-mismatch"),("capability-a-plan-b","foreign-capability-plan"),("release-a-plan-b","foreign-release-plan"),("core-only-capability-paired-coverage","core-only-capability-claims-paired"),("paired-capability-no-decoder","missing-paired-decoder"),("unknown-extension-profile","unknown-renderer-semantic-family"),("partial-extension-profile","partially-supported-extension-family"),("omitted-paired-object","incomplete-paired-decoding"),("duplicated-paired-object","duplicate-paired-identity"),("omitted-mandatory-requirement","missing-requirement-outcome"),("omitted-owner-mapping","missing-owner-mapping"),("invented-mapping","surplus-owner-mapping"),("zero-mappings-nonempty-obligations","empty-mapping-coverage"),("row-count-mismatch","mapping-count-row-count-mismatch"),("foreign-structural-identity","foreign-authority-bytes"),("substituted-effective-graph","effective-graph-digest-mismatch"),("traversable-counterpart-proof","counterpart-proof-nontraversable"),("altered-candidate-after-derivation","candidate-byte-digest-mismatch"),("reordered-authoritative-records","authoritative-order-mismatch"),("ambiguous-core-locator","ambiguous-core-locator"),("namespace-collision","duplicate-core-identity"),("task067-authority-as-native-v2","historical-authority-family-rejected"),("foreign-rendering-conformance-chain","foreign-plan-rendering-chain"),("duplicated-extension","duplicate-extension-family"),("missing-extension","missing-required-extension"),("mapping-reordered","mapping-order-mismatch"),("unknown-extension-data-semantic","unknown-extension-semantic-meaning"),
    ]
    mutation_specs={
      "candidate-a-evidence-b":("set","candidate_binding","candidate:B"),"registry-a-declares-b":("set","registry_identity","registry:B"),"same-registry-identity-different-bytes":("set","registry_digest","f"*64),"capability-a-plan-b":("set","plan_capability","capability:B"),"release-a-plan-b":("set","plan_release","release:B"),"core-only-capability-paired-coverage":("set","dispatch","core-only"),"paired-capability-no-decoder":("set","decoder",False),"unknown-extension-profile":("set","extension_family","unknown"),"partial-extension-profile":("set","extension_family","partial"),"omitted-paired-object":("remove","decoded_objects",0),"duplicated-paired-object":("append","decoded_objects","paired:a"),"omitted-mandatory-requirement":("remove","requirement_outcomes",0),"omitted-owner-mapping":("remove","mapping_outcomes",0),"invented-mapping":("append","mapping_outcomes","row:invented"),"zero-mappings-nonempty-obligations":("set","mapping_outcomes",[]),"row-count-mismatch":("append","rows","row:extra"),"foreign-structural-identity":("set","authority_digest","e"*64),"substituted-effective-graph":("set","effective_graph_digest","d"*64),"traversable-counterpart-proof":("set","counterpart_traversable",True),"altered-candidate-after-derivation":("set","candidate_byte_digest","c"*64),"reordered-authoritative-records":("reorder","authoritative_order",[1,0]),"ambiguous-core-locator":("append","core_locations","/records/0/semantic/a"),"namespace-collision":("append","core_identities","core:a"),"task067-authority-as-native-v2":("set","capability_version","1.0.0"),"foreign-rendering-conformance-chain":("set","rendering_plan","plan:B"),"duplicated-extension":("append","extensions","paired-v3"),"missing-extension":("set","extensions",[]),"mapping-reordered":("reorder","mapping_outcomes",[1,0]),"unknown-extension-data-semantic":("set","unknown_extension_semantic",True),
    }
    invalid_base={"candidate_identity":"candidate:A","candidate_binding":"candidate:A","registry_identity":"registry:A","expected_registry_identity":"registry:A","registry_digest":"a"*64,"expected_registry_digest":"a"*64,"capability_identity":"capability:A","plan_capability":"capability:A","release_identity":"release:A","plan_release":"release:A","dispatch":"paired-v3","decoder":True,"extension_family":"paired-v3","decoded_objects":["paired:a","paired:b"],"expected_decoded_objects":["paired:a","paired:b"],"requirement_inventory":["renderer"],"requirement_outcomes":["renderer"],"rows":["row:0","row:1"],"mapping_inventory":["row:0","row:1"],"mapping_outcomes":["row:0","row:1"],"obligations":["obligation:0"],"authority_digest":"b"*64,"expected_authority_digest":"b"*64,"effective_graph_digest":"a"*64,"expected_effective_graph_digest":"a"*64,"counterpart_traversable":False,"candidate_byte_digest":PROFILE_SHA,"expected_candidate_byte_digest":PROFILE_SHA,"authoritative_order":["record:a","record:b"],"expected_authoritative_order":["record:a","record:b"],"core_locations":["/records/0/semantic/a"],"core_identities":["core:a"],"capability_version":"2.0.0","rendering_plan":"plan:A","plan_identity":"plan:A","extensions":["paired-v3"],"unknown_extension_semantic":False}
    invalid={"contract":"briefforge:task076-executable-invalid-fixtures:2.0.0","base_input":invalid_base,"fixtures":[{"id":i,"mutation":{"operation":mutation_specs[i][0],"path":mutation_specs[i][1],"value":mutation_specs[i][2]},"expected_findings":[code]} for i,code in invalid_ids]}
    findings={code:{"severity":"blocking","consequence":"contract-byte-admission","message":code.replace("-"," ")} for _,code in invalid_ids}
    findings.update({code:{"severity":"blocking","consequence":"contract-byte-admission","message":code.replace("-"," ")} for code in ["duplicate-generic-row-identity","incomplete-predecessor-closure","substituted-paired-decoding","requirement-inventory-mismatch","mapping-inventory-mismatch","source-row-population-mismatch","semantic-commitment-mismatch","plan-evidence-binding-mismatch"]})
    rules={"contract":"briefforge:task076-contract-validation-rules:2.0.0","canonical_json":"UTF-8;sort_keys=true;separators=(',',':');ensure_ascii=false;allow_nan=false;no-trailing-newline-for-governed-bytes","digest_rule":"ASCII-domain-tag || 0x00 || canonical-bytes; SHA-256 lowercase hex","authority_boundary":"fixtures are non-authority; production verifiers must reload authenticated canonical bytes and reproduce all commitments","coverage":"six requirement outcomes plus every owner mapping; mapping_count == decoded row count; obligations-empty permits N=0; nonempty rows or obligations prohibit empty mappings","counterparts":"exact 144 TASK-071 bijection; counterpart exclusion is only Section.order; graph-emission classification separately governs Provenance.source_snapshot_identity; proof records never nodes, edges, references, or coverage","invalid_fixture_execution":"deep-copy base_input; apply declared operation; run independent invariant detector; compare blocking findings"}
    def card(n:int, obligations:bool=True)->dict[str,Any]:
        rows=[f"row:generic-{n}-{i}" for i in range(n)]
        return {"id":f"generic-cardinality-n{n}","kind":"planner-cardinality","input":{"rows":rows,"mapping_inventory":rows,"mapping_outcomes":rows,"obligations":(["obligation:generic"] if obligations else [])},"expected":"PASS","N":n}
    source_records={record["record_kind"]:record for record in profile["records"]}
    def closure(size:int)->dict[str,Any]:
        brief_id=source_records["PresentationBriefRecord"]["identity"]; material_id=source_records["PortablePresentationMaterialRecord"]["identity"]; candidate_id=source_records["CandidatePresentationPackageRecord"]["identity"]
        judgment_id="judgment:task076-normative-v2"; ready_id=plan_semantic["ready_ref"]; release_id=plan_payload["release_identity"]; capability_id=cap_record["identity"]; plan_id=plan_record["identity"]
        def complete(kind:str,identity:str,refs:list[str],exact:dict[str,Any]|None=None)->dict[str,Any]:
            record=copy.deepcopy(exact) if exact is not None else {"record_kind":kind,"identity":identity,"profile":{"identity":"briefforge-core-representation-profile","version":"1.0.0"},"semantic":{"fixture_character":"non-authority-predecessor-byte-stand-in","predecessor_refs":refs},"extensions":[]}
            return {"kind":kind,"identity":identity,"refs":refs,"record":record,"fingerprint":h("briefforge.task076.predecessor-closure-record-bytes.v2",record)}
        records=[complete("PresentationBriefRecord",brief_id,[],source_records["PresentationBriefRecord"]),complete("PortablePresentationMaterialRecord",material_id,[],source_records["PortablePresentationMaterialRecord"]),complete("CandidatePresentationPackageRecord",candidate_id,[brief_id,material_id],source_records["CandidatePresentationPackageRecord"]),complete("ValidationJudgmentRecord",judgment_id,[candidate_id]),complete("ReadyPresentationPackageRecord",ready_id,[judgment_id]),complete("PublicationReleaseRecord",release_id,[ready_id]),complete("RendererCapabilityDeclarationRecord",capability_id,[],cap_record),complete("RendererCompatibilityPlanRecord",plan_id,[candidate_id,ready_id,release_id,capability_id],plan_record)]
        if size==10:
            records+=[complete("GeneratedArtifactAuditRecord","audit:task076-normative-v2",[release_id,ready_id,plan_id,capability_id]),complete("SemanticArtifactConformanceRecord","conformance:task076-normative-v2",["audit:task076-normative-v2",ready_id])]
        root=plan_id if size==8 else "conformance:task076-normative-v2"
        return {"id":f"plan-v2-predecessor-closure-{size}-record","kind":"predecessor-closure","record_order":[x["identity"] for x in records],"records":records,"root":root,"expected_reachable":[x["identity"] for x in records],"expected":"PASS"}
    valid={"contract":"briefforge:task076-valid-fixture-index:2.0.0","binding_authority":{"contract":"briefforge:task076-authenticated-binding-authority-fixture:1.0.0","character":"non-authority-stand-in-for-authenticated-issuer-and-predecessor-bytes","capability":{"record_identity":cap_record["identity"],"semantic":cap_record["semantic"],"extension_metadata":{k:v for k,v in cap_ext.items() if k!="payload"},"payload":cap_payload},"plan":{"record_identity":plan_record["identity"],"semantic":plan_record["semantic"],"extension_metadata":{k:v for k,v in plan_ext.items() if k!="payload"},"payload":plan_payload}},"fixtures":[{"id":"task071-derived-model","artifact":"task071-derived-populations.json","expected":"PASS","counts":env["counts"]},{"id":"task071-derivation-envelope","artifact":"task071-derivation-evidence-envelope.json","expected":"PASS"},{"id":"capability-v2","artifact":"capability-v2-record.json","expected":"PASS"},{"id":"plan-v2","artifact":"plan-v2-record.json","expected":"PASS","requirement_outcomes":6,"mapping_outcomes":7,"mapping_count":7,"decoded_row_count":7},card(0,False),card(1),card(7),card(16),closure(8),closure(10)]}
    duplicate_card=card(7); duplicate_card["id"]="generic-cardinality-duplicate-row"; duplicate_card["input"]["rows"][1]=duplicate_card["input"]["rows"][0]; duplicate_card["input"]["mapping_inventory"][1]=duplicate_card["input"]["mapping_inventory"][0]; duplicate_card["input"]["mapping_outcomes"][1]=duplicate_card["input"]["mapping_outcomes"][0]; duplicate_card["expected"]="FAIL"; duplicate_card["expected_findings"]=["duplicate-generic-row-identity"]
    incomplete_closure=closure(8); incomplete_closure["id"]="plan-v2-predecessor-closure-unreachable-extra"; incomplete_closure["records"][-1]["refs"].remove(cap_record["identity"]); incomplete_closure["expected"]="FAIL"; incomplete_closure["expected_findings"]=["incomplete-predecessor-closure"]
    substituted_kind=closure(8); substituted_kind["id"]="plan-v2-predecessor-closure-substituted-kind"; substituted_kind["records"][0]["kind"]="ForeignBriefRecord"; substituted_kind["records"][0]["record"]["record_kind"]="ForeignBriefRecord"; substituted_kind["records"][0]["fingerprint"]=h("briefforge.task076.predecessor-closure-record-bytes.v2",substituted_kind["records"][0]["record"]); substituted_kind["expected"]="FAIL"; substituted_kind["expected_findings"]=["incomplete-predecessor-closure"]
    nonplan_root=closure(8); nonplan_root["id"]="plan-v2-predecessor-closure-nonplan-root"; nonplan_root["root"]=source_records["CandidatePresentationPackageRecord"]["identity"]; nonplan_root["expected"]="FAIL"; nonplan_root["expected_findings"]=["incomplete-predecessor-closure"]
    altered_fingerprint=closure(8); altered_fingerprint["id"]="plan-v2-predecessor-closure-altered-fingerprint"; altered_fingerprint["records"][0]["fingerprint"]="f"*64; altered_fingerprint["expected"]="FAIL"; altered_fingerprint["expected_findings"]=["incomplete-predecessor-closure"]
    altered_topology=closure(10); altered_topology["id"]="plan-v2-predecessor-closure-altered-topology"; altered_topology["records"][-1]["refs"][-1]="judgment:task076-normative-v2"; altered_topology["records"][-1]["record"]["semantic"]["predecessor_refs"][-1]="judgment:task076-normative-v2"; altered_topology["records"][-1]["fingerprint"]=h("briefforge.task076.predecessor-closure-record-bytes.v2",altered_topology["records"][-1]["record"]); altered_topology["expected"]="FAIL"; altered_topology["expected_findings"]=["incomplete-predecessor-closure"]
    altered_order=closure(10); altered_order["id"]="plan-v2-predecessor-closure-altered-order"; altered_order["records"].reverse(); altered_order["expected"]="FAIL"; altered_order["expected_findings"]=["incomplete-predecessor-closure"]
    abstract_reclosures=[]
    for closure_size in (8,10):
        minimal=closure(closure_size); minimal["id"]=f"plan-v2-predecessor-closure-{closure_size}-minimal-record-reclosure"; minimal_record={"record_kind":"PresentationBriefRecord","identity":source_records["PresentationBriefRecord"]["identity"]}; minimal["records"][0]["record"]=minimal_record; minimal["records"][0]["fingerprint"]=h("briefforge.task076.predecessor-closure-record-bytes.v2",minimal_record); minimal["expected"]="FAIL"; minimal["expected_findings"]=["incomplete-predecessor-closure"]; abstract_reclosures.append(minimal)
        foreign=closure(closure_size); foreign["id"]=f"plan-v2-predecessor-closure-{closure_size}-foreign-record-reclosure"; foreign_record={"record_kind":"PresentationBriefRecord","identity":source_records["PresentationBriefRecord"]["identity"],"profile":{"identity":"foreign-profile","version":"9.9.9"},"semantic":{"attacker_controlled":True},"extensions":[{"foreign":True}]}; foreign["records"][0]["record"]=foreign_record; foreign["records"][0]["fingerprint"]=h("briefforge.task076.predecessor-closure-record-bytes.v2",foreign_record); foreign["expected"]="FAIL"; foreign["expected_findings"]=["incomplete-predecessor-closure"]; abstract_reclosures.append(foreign)
    invalid["structural_fixtures"]=[duplicate_card,incomplete_closure,substituted_kind,nonplan_root,altered_fingerprint,altered_topology,altered_order]+abstract_reclosures
    invalid["correlated_fixtures"]=[
      {"id":"correlated-candidate-substitution","sets":{"candidate_identity":"candidate:B","candidate_binding":"candidate:B"},"expected_findings":["foreign-candidate-evidence"]},
      {"id":"correlated-candidate-digest-oracle-substitution","sets":{"candidate_byte_digest":"c"*64,"expected_candidate_byte_digest":"c"*64},"expected_findings":["candidate-byte-digest-mismatch"]},
      {"id":"correlated-registry-digest-oracle-substitution","sets":{"registry_digest":"c"*64,"expected_registry_digest":"c"*64},"expected_findings":["registry-digest-mismatch"]},
      {"id":"correlated-authority-digest-oracle-substitution","sets":{"authority_digest":"c"*64,"expected_authority_digest":"c"*64},"expected_findings":["foreign-authority-bytes"]},
      {"id":"correlated-effective-graph-oracle-substitution","sets":{"effective_graph_digest":"c"*64,"expected_effective_graph_digest":"c"*64},"expected_findings":["effective-graph-digest-mismatch"]},
      {"id":"correlated-order-oracle-substitution","sets":{"authoritative_order":["record:x","record:y"],"expected_authoritative_order":["record:x","record:y"]},"expected_findings":["authoritative-order-mismatch"]},
      {"id":"equal-length-decoded-substitution","sets":{"decoded_objects":["paired:x","paired:y"]},"expected_findings":["substituted-paired-decoding"]},
      {"id":"correlated-requirement-substitution","sets":{"requirement_inventory":["foreign"],"requirement_outcomes":["foreign"]},"expected_findings":["requirement-inventory-mismatch"]},
      {"id":"correlated-mapping-inventory-substitution","sets":{"mapping_inventory":["row:x","row:y"],"mapping_outcomes":["row:x","row:y"]},"expected_findings":["mapping-inventory-mismatch"]},
      {"id":"same-length-source-row-substitution","sets":{"rows":["row:x","row:y"]},"expected_findings":["source-row-population-mismatch"]},
    ]
    plan_predecessor_fields=["candidate_profile_instance_fingerprint","judgment_fingerprint","ready_fingerprint","release_identity","release_fingerprint","release_closure_digest","capability_identity","capability_fingerprint"]
    plan_predecessor_fixtures=[]
    for key in plan_predecessor_fields:
        value=("foreign:"+key) if key.endswith("identity") else "f"*64
        expected_findings=["plan-evidence-binding-mismatch"]+(["semantic-commitment-mismatch"] if key=="capability_identity" else [])
        plan_predecessor_fixtures.append({"id":f"plan-recomputed-fingerprint-foreign-{key.replace('_','-')}","artifact":"plan-v2-record.json","mutations":[{"path":["extensions",0,"payload",key],"value":value}],"recompute_fingerprint":True,"expected_findings":expected_findings})
    invalid["record_fixtures"]=[
      {"id":"capability-core-semantic-shadow","artifact":"capability-v2-record.json","mutation":{"path":["semantic","renderer_id"],"value":"renderer:foreign"},"expected_findings":["semantic-commitment-mismatch"]},
      {"id":"capability-correlated-renderer-reclosure","artifact":"capability-v2-record.json","mutations":[{"path":["semantic","renderer_id"],"value":"renderer:foreign"},{"path":["extensions",0,"payload","renderer_identity"],"value":"renderer:foreign"}],"recompute_semantic_digest":True,"recompute_fingerprint":True,"expected_findings":["semantic-commitment-mismatch"]},
      {"id":"plan-core-semantic-shadow","artifact":"plan-v2-record.json","mutation":{"path":["semantic","ready_ref"],"value":"ready:foreign"},"expected_findings":["semantic-commitment-mismatch"]},
      {"id":"plan-correlated-predecessor-family-reclosure","artifact":"plan-v2-record.json","mutations":[{"path":["semantic","ready_ref"],"value":"ready:foreign"},{"path":["semantic","renderer_capability_ref"],"value":"capability:foreign"},{"path":["extensions",0,"payload","candidate_profile_instance_fingerprint"],"value":"f"*64},{"path":["extensions",0,"payload","judgment_fingerprint"],"value":"e"*64},{"path":["extensions",0,"payload","ready_fingerprint"],"value":"d"*64},{"path":["extensions",0,"payload","release_identity"],"value":"release:foreign"},{"path":["extensions",0,"payload","release_fingerprint"],"value":"c"*64},{"path":["extensions",0,"payload","release_closure_digest"],"value":"b"*64},{"path":["extensions",0,"payload","capability_identity"],"value":"capability:foreign"},{"path":["extensions",0,"payload","capability_fingerprint"],"value":"a"*64},{"path":["extensions",0,"target_refs",2],"value":"release:foreign"},{"path":["extensions",0,"target_refs",3],"value":"capability:foreign"}],"recompute_semantic_digest":True,"recompute_fingerprint":True,"expected_findings":["semantic-commitment-mismatch","plan-evidence-binding-mismatch"]},
      {"id":"plan-recomputed-fingerprint-foreign-core-graph","artifact":"plan-v2-record.json","mutation":{"path":["extensions",0,"payload","core_graph_digest"],"value":"f"*64},"recompute_fingerprint":True,"expected_findings":["plan-evidence-binding-mismatch"]},
    ]+plan_predecessor_fixtures
    # Write governed contract byte sequences.
    write_json("core-object-kind-location-registry.json",reg,True)
    write_json("task071-derived-populations.json",populations,True)
    write_json("task071-derivation-evidence-envelope.json",env,True)
    for name,schema in schemas(reg,env,cap_record,plan_record).items(): write_json(name,schema,True)
    write_json("capability-v2-extension.json",cap_ext,True); write_json("capability-v2-record.json",cap_record,True)
    write_json("plan-v2-extension.json",plan_ext,True); write_json("plan-v2-record.json",plan_record,True)
    write_json("planning-completeness-evidence.json",completeness,True)
    write_json("valid-fixtures.json",valid,True); write_json("invalid-fixtures.json",invalid,True)
    write_json("expected-findings.json",findings,True); write_json("validation-rules.json",rules,True)
    print(json.dumps({"status":"PASS","core_nodes":len(core_nodes),"core_edges":len(core_edges),"paired_nodes":len(pnodes),"paired_edges":len(pedges),"counterparts":len(counterparts),"requirements":len(requirements),"mappings":len(mappings),"registry_entries":len(reg["entries"]),"registry_digest":reg_digest,"envelope_fingerprint":env["fingerprint"],"capability_fingerprint":capfp,"plan_fingerprint":plan_payload["fingerprint"]},sort_keys=True))

if __name__ == "__main__": build()
