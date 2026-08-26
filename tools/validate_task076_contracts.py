#!/usr/bin/env python3
"""Read-only, executable validator for TASK-076 contract bytes and fixtures."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import tempfile
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/contracts/task076"
GEN = ROOT / "tools/build_task076_contracts.py"
PROFILE = ROOT / "artifacts/pilots/candidate-authoring-output/attempt:task071-representative-campaign-002/profile.json"
PROFILE_SHA = "62cbe5294b123c9b4043e9f721a1b2585c70a5380e2121a39e8558b5c73b1898"
FIXTURE_AUTHORITY = {
    "candidate_identity":"candidate:A","registry_identity":"registry:A","registry_digest":"a"*64,
    "capability_identity":"capability:A","release_identity":"release:A","decoded_objects":["paired:a","paired:b"],
    "requirement_inventory":["renderer"],"rows":["row:0","row:1"],"mapping_inventory":["row:0","row:1"],
    "authority_digest":"b"*64,"effective_graph_digest":"a"*64,"candidate_byte_digest":PROFILE_SHA,
    "authoritative_order":["record:a","record:b"],"plan_identity":"plan:A",
}


def load(path: Path) -> Any:
    return json.loads(path.read_bytes())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()


def domain_hash(tag: str, value: Any) -> str:
    return hashlib.sha256(tag.encode()+b"\0"+canonical(value)).hexdigest()


def schema_errors(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Validate the closed JSON-Schema subset used by the governed schemas."""
    errors: list[str] = []
    if "oneOf" in schema:
        matches = [s for s in schema["oneOf"] if not schema_errors(value, s, path)]
        if len(matches) != 1:
            errors.append(f"{path}: oneOf matched {len(matches)} branches")
        return errors
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: const mismatch")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: enum mismatch")
    allowed = schema.get("type")
    if allowed is not None:
        allowed_types = [allowed] if isinstance(allowed, str) else allowed
        def is_type(name: str) -> bool:
            return {
                "object": isinstance(value, dict), "array": isinstance(value, list),
                "string": isinstance(value, str), "integer": isinstance(value, int) and not isinstance(value, bool),
                "boolean": isinstance(value, bool), "null": value is None,
            }.get(name, True)
        if not any(is_type(x) for x in allowed_types):
            errors.append(f"{path}: expected type {allowed_types}, got {type(value).__name__}")
            return errors
    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing {key}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    errors.append(f"{path}: additional property {key}")
        for key, child in value.items():
            if key in props:
                errors.extend(schema_errors(child, props[key], f"{path}.{key}"))
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0): errors.append(f"{path}: too few items")
        if "maxItems" in schema and len(value) > schema["maxItems"]: errors.append(f"{path}: too many items")
        if schema.get("uniqueItems") and len({canonical(x) for x in value}) != len(value): errors.append(f"{path}: duplicate items")
        prefix = schema.get("prefixItems", [])
        for i, child_schema in enumerate(prefix):
            if i < len(value): errors.extend(schema_errors(value[i], child_schema, f"{path}[{i}]"))
        if "items" in schema:
            start = len(prefix) if prefix else 0
            for i in range(start, len(value)): errors.extend(schema_errors(value[i], schema["items"], f"{path}[{i}]"))
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0): errors.append(f"{path}: too short")
        if "pattern" in schema and re.search(schema["pattern"], value) is None: errors.append(f"{path}: pattern mismatch")
        if schema.get("format")=="date-time":
            try: datetime.strptime(value,"%Y-%m-%dT%H:%M:%SZ")
            except ValueError: errors.append(f"{path}: invalid canonical UTC date-time")
    if isinstance(value, int) and not isinstance(value, bool) and value < schema.get("minimum", value): errors.append(f"{path}: below minimum")
    return errors


def apply_mutation(base: dict[str, Any], mutation: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(base)
    key = mutation["path"]
    op = mutation["operation"]
    arg = copy.deepcopy(mutation["value"])
    if op == "set": value[key] = arg
    elif op == "remove": value[key].pop(arg)
    elif op == "append": value[key].append(arg)
    elif op == "reorder":
        sequence = value[key]
        order = arg + list(range(len(arg), len(sequence)))
        value[key] = [sequence[i] for i in order]
    else: raise AssertionError(f"unknown mutation operation {op}")
    return value


def detect_findings(x: dict[str, Any]) -> list[str]:
    """Independent detector against immutable fixture authority, never mutable expected_* fields."""
    a=FIXTURE_AUTHORITY; findings: list[str] = []
    if x["candidate_binding"] != a["candidate_identity"] or x["candidate_identity"] != a["candidate_identity"]: findings.append("foreign-candidate-evidence")
    if x["registry_identity"] != a["registry_identity"]: findings.append("foreign-registry-identity")
    if x["registry_digest"] != a["registry_digest"]: findings.append("registry-digest-mismatch")
    if x["plan_capability"] != a["capability_identity"] or x["capability_identity"] != a["capability_identity"]: findings.append("foreign-capability-plan")
    if x["plan_release"] != a["release_identity"] or x["release_identity"] != a["release_identity"]: findings.append("foreign-release-plan")
    if x["dispatch"] == "core-only": findings.append("core-only-capability-claims-paired")
    if not x["decoder"]: findings.append("missing-paired-decoder")
    if x["extension_family"] == "unknown": findings.append("unknown-renderer-semantic-family")
    if x["extension_family"] == "partial": findings.append("partially-supported-extension-family")
    if x["decoded_objects"] != a["decoded_objects"]:
        if len(x["decoded_objects"]) < len(a["decoded_objects"]): findings.append("incomplete-paired-decoding")
        elif len(set(x["decoded_objects"])) != len(x["decoded_objects"]): findings.append("duplicate-paired-identity")
        else: findings.append("substituted-paired-decoding")
    if x["requirement_inventory"] != a["requirement_inventory"]: findings.append("requirement-inventory-mismatch")
    elif x["requirement_outcomes"] != a["requirement_inventory"]: findings.append("missing-requirement-outcome")
    rows, inventory, outcomes = x["rows"], x["mapping_inventory"], x["mapping_outcomes"]
    if len(set(rows)) != len(rows): findings.append("duplicate-generic-row-identity")
    elif len(rows)==len(a["rows"]) and rows != a["rows"]: findings.append("source-row-population-mismatch")
    if len(inventory) != len(rows): findings.append("mapping-count-row-count-mismatch")
    elif inventory != a["mapping_inventory"]: findings.append("mapping-inventory-mismatch")
    elif not outcomes and (rows or x["obligations"]): findings.append("empty-mapping-coverage")
    elif len(outcomes) < len(inventory): findings.append("missing-owner-mapping")
    elif any(y not in inventory for y in outcomes): findings.append("surplus-owner-mapping")
    elif outcomes != inventory: findings.append("mapping-order-mismatch")
    if x["authority_digest"] != a["authority_digest"]: findings.append("foreign-authority-bytes")
    if x["effective_graph_digest"] != a["effective_graph_digest"]: findings.append("effective-graph-digest-mismatch")
    if x["counterpart_traversable"]: findings.append("counterpart-proof-nontraversable")
    if x["candidate_byte_digest"] != a["candidate_byte_digest"]: findings.append("candidate-byte-digest-mismatch")
    if x["authoritative_order"] != a["authoritative_order"]: findings.append("authoritative-order-mismatch")
    if len(x["core_locations"]) != len(set(x["core_locations"])): findings.append("ambiguous-core-locator")
    if len(x["core_identities"]) != len(set(x["core_identities"])): findings.append("duplicate-core-identity")
    if x["capability_version"] != "2.0.0": findings.append("historical-authority-family-rejected")
    if x["rendering_plan"] != a["plan_identity"] or x["plan_identity"] != a["plan_identity"]: findings.append("foreign-plan-rendering-chain")
    if len(x["extensions"]) > 1: findings.append("duplicate-extension-family")
    elif not x["extensions"]: findings.append("missing-required-extension")
    if x["unknown_extension_semantic"]: findings.append("unknown-extension-semantic-meaning")
    return findings


def validate_closure(fixture: dict[str, Any], profile: dict[str,Any], capability_record: dict[str,Any], plan_record: dict[str,Any]) -> None:
    records = fixture["records"]; size=len(records)
    require(size in (8,10),f"{fixture['id']}: wrong closure size")
    brief="brief:task071-cross-inquiry"; material="material:task071-t039"; candidate="candidate:task071-cross-inquiry"; judgment="judgment:task076-normative-v2"; ready="ready:task076-normative-v2"; release="release:task076-normative-v2"; capability="capability:task076-normative-v2"; plan="plan:task076-normative-v2"
    expected=[("PresentationBriefRecord",brief,[]),("PortablePresentationMaterialRecord",material,[]),("CandidatePresentationPackageRecord",candidate,[brief,material]),("ValidationJudgmentRecord",judgment,[candidate]),("ReadyPresentationPackageRecord",ready,[judgment]),("PublicationReleaseRecord",release,[ready]),("RendererCapabilityDeclarationRecord",capability,[]),("RendererCompatibilityPlanRecord",plan,[candidate,ready,release,capability])]
    if size==10: expected += [("GeneratedArtifactAuditRecord","audit:task076-normative-v2",[release,ready,plan,capability]),("SemanticArtifactConformanceRecord","conformance:task076-normative-v2",["audit:task076-normative-v2",ready])]
    source_by_identity={record["identity"]:record for record in profile["records"]}
    def standin(kind:str,identity:str,refs:list[str])->dict[str,Any]:
        return {"record_kind":kind,"identity":identity,"profile":{"identity":"briefforge-core-representation-profile","version":"1.0.0"},"semantic":{"fixture_character":"non-authority-predecessor-byte-stand-in","predecessor_refs":refs},"extensions":[]}
    expected_complete={brief:source_by_identity[brief],material:source_by_identity[material],candidate:source_by_identity[candidate],judgment:standin("ValidationJudgmentRecord",judgment,[candidate]),ready:standin("ReadyPresentationPackageRecord",ready,[judgment]),release:standin("PublicationReleaseRecord",release,[ready]),capability:capability_record,plan:plan_record}
    if size==10:
        expected_complete["audit:task076-normative-v2"]=standin("GeneratedArtifactAuditRecord","audit:task076-normative-v2",[release,ready,plan,capability])
        expected_complete["conformance:task076-normative-v2"]=standin("SemanticArtifactConformanceRecord","conformance:task076-normative-v2",["audit:task076-normative-v2",ready])
    expected_by_id={identity:(kind,refs) for kind,identity,refs in expected}; expected_order=[identity for _,identity,_ in expected]
    expected_root=plan if size==8 else "conformance:task076-normative-v2"
    require(fixture["root"]==expected_root,f"{fixture['id']}: root differs from exact closure terminal")
    require(fixture.get("record_order")==expected_order,f"{fixture['id']}: declared record order differs")
    require([r["identity"] for r in records]==expected_order,f"{fixture['id']}: record array order differs")
    by_id={r["identity"]:r for r in records}; require(len(by_id)==len(records),f"{fixture['id']}: duplicate identities")
    require(set(by_id)==set(expected_by_id),f"{fixture['id']}: predecessor identity population differs")
    for identity,record in by_id.items():
        kind,refs=expected_by_id[identity]
        require(record["kind"]==kind,f"{fixture['id']}: substituted record kind {identity}")
        require(record["refs"]==refs,f"{fixture['id']}: altered predecessor topology {identity}")
        complete=record["record"]
        require(complete["record_kind"]==kind and complete["identity"]==identity,f"{fixture['id']}: complete record identity/kind differs {identity}")
        require(complete==expected_complete[identity],f"{fixture['id']}: complete canonical record bytes differ {identity}")
        require(record["fingerprint"]==domain_hash("briefforge.task076.predecessor-closure-record-bytes.v2",complete),f"{fixture['id']}: record fingerprint mismatch {identity}")
        for ref in refs: require(ref in by_id,f"{fixture['id']}: dangling predecessor {ref}")
    reachable:set[str]=set(); stack=[fixture["root"]]
    while stack:
        current=stack.pop()
        if current in reachable: continue
        reachable.add(current); stack.extend(by_id[current]["refs"])
    require(reachable==set(by_id),f"{fixture['id']}: closure is not complete")
    require(fixture["expected_reachable"]==expected_order,f"{fixture['id']}: declared reachability order differs")

def validate_cardinality(fixture: dict[str, Any]) -> None:
    x=fixture["input"]; rows=x["rows"]; inventory=x["mapping_inventory"]; outcomes=x["mapping_outcomes"]
    require(len(rows)==len(inventory)==len(outcomes)==fixture["N"],f"{fixture['id']}: cardinality mismatch")
    require(len(set(rows))==len(rows),f"{fixture['id']}: duplicate row identity")
    require(inventory==rows and outcomes==rows,f"{fixture['id']}: mappings are not exact once-only authored-row coverage")
    require(fixture["N"]>0 or not x["obligations"],f"{fixture['id']}: invalid zero case")


def record_binding_findings(record: dict[str,Any], authority: dict[str,Any]) -> list[str]:
    ext=record["extensions"][0]; payload=ext["payload"]; semantic=record["semantic"]; findings=[]
    if record["record_kind"]=="RendererCapabilityDeclarationRecord":
        expected=authority["capability"]; extension_metadata={k:v for k,v in ext.items() if k!="payload"}
        unsigned=copy.deepcopy(payload); fingerprint=unsigned.pop("fingerprint",None)
        if record["identity"]!=expected["record_identity"] or semantic!=expected["semantic"] or extension_metadata!=expected["extension_metadata"] or payload!=expected["payload"]: findings.append("semantic-commitment-mismatch")
        if payload.get("semantic_digest")!=domain_hash("briefforge.task076.capability-core-semantic.v1",semantic) or fingerprint!=domain_hash("briefforge.task075.capability-declaration.v2",unsigned): findings.append("semantic-commitment-mismatch")
        if not (record["identity"]==payload["declaration_identity"]==semantic["declaration_identity"]==ext["target_refs"][0] and semantic["renderer_id"]==payload["renderer_identity"] and semantic["declaration_time"]==payload["issued_at_utc"]): findings.append("semantic-commitment-mismatch")
    elif record["record_kind"]=="RendererCompatibilityPlanRecord":
        expected=authority["plan"]; expected_payload=expected["payload"]; extension_metadata={k:v for k,v in ext.items() if k!="payload"}
        unsigned=copy.deepcopy(payload); fingerprint=unsigned.pop("fingerprint",None)
        if record["identity"]!=expected["record_identity"] or semantic!=expected["semantic"]: findings.append("semantic-commitment-mismatch")
        if payload.get("semantic_digest")!=domain_hash("briefforge.task076.plan-core-semantic.v1",semantic): findings.append("semantic-commitment-mismatch")
        critical={k:v for k,v in payload.items() if k not in {"semantic_digest","fingerprint"}}
        expected_critical={k:v for k,v in expected_payload.items() if k not in {"semantic_digest","fingerprint"}}
        if extension_metadata!=expected["extension_metadata"] or critical!=expected_critical or fingerprint!=domain_hash("briefforge.task075.plan-extension.v2",unsigned): findings.append("plan-evidence-binding-mismatch")
        if not (record["identity"]==payload["plan_identity"]==ext["target_refs"][0] and semantic["renderer_capability_ref"]==payload["capability_identity"] and semantic["supported"]==payload["supported"] and semantic["mode"]==payload["mode"]): findings.append("semantic-commitment-mismatch")
    else: raise AssertionError(f"unsupported governed record {record['record_kind']}")
    return list(dict.fromkeys(findings))


def independently_reconstruct_paired(profile: dict[str,Any], core_index: dict[str,tuple[list[Any],str,Any]], candidate_fingerprint: str, effective_graph_digest: str) -> tuple[list[list[Any]],list[list[Any]],list[list[Any]],list[list[Any]],list[list[Any]]]:
    """Independent TASK-071 paired decoder/counterpart oracle; never calls builder paired helpers."""
    candidate=next(r for r in profile["records"] if r["record_kind"]=="CandidatePresentationPackageRecord")
    source=json.loads(candidate["extensions"][0]["payload"]["canonical_semantics"])
    groups=[("Section",source["sections"],"/sections"),("Statement",source["statements"],"/statements"),("Table",[source["table"]],"/table"),("Row",source["table"]["rows"],"/table/rows"),("Value",source["values"],"/values"),("Qualification",source["qualifications"],"/qualifications"),("Provenance",source["provenance"],"/provenance"),("Obligation",source["obligations"],"/obligations")]
    paired_index:dict[str,tuple[list[Any],str,Any]]={}; nodes=[]
    for kind,items,base in groups:
        for ordinal,item in enumerate(items):
            identity=item["identity"]; require(identity not in paired_index,f"independent paired duplicate {identity}")
            pointer=base if kind=="Table" else f"{base}/{ordinal}"; dqi=["briefforge:paired-terminal","3.0.0",kind,identity]
            paired_index[identity]=(dqi,pointer,item); nodes.append([dqi,pointer,domain_hash("briefforge.task075.source-fragment.v1",item)])
    edges=[]
    def add_edge(source_identity:str,field:str,relation:str,target_identity:str,ordinal:int=0)->None:
        require(target_identity in paired_index or target_identity in core_index,f"independent paired dangling {target_identity}")
        source_dqi,source_pointer,_=paired_index[source_identity]
        target_dqi=(paired_index.get(target_identity) or core_index[target_identity])[0]
        attrs={"source_pointer":source_pointer,"source_field":field,"target_kind":target_dqi[2]}
        edges.append([source_dqi,relation,ordinal,target_dqi,domain_hash("briefforge.task075.edge-attributes.v1",attrs)])
    for section in source["sections"]:
        for ordinal,child in enumerate(section["children"]): add_edge(section["identity"],"children","ordered-child",child["target_ref"],ordinal)
    table=source["table"]
    add_edge(table["identity"],"purpose_ref","purpose",table["purpose_ref"]); add_edge(table["identity"],"authority_ref","authority",table["authority_ref"])
    for ordinal,row in enumerate(table["rows"]): add_edge(table["identity"],"rows","ordered-row",row["identity"],ordinal)
    for statement in source["statements"]: add_edge(statement["identity"],"authority_ref","authority",statement["authority_ref"])
    for row in table["rows"]:
        for field,relation in (("row_statement_ref","row-statement"),("raw_value_ref","raw-value"),("first_difference_value_ref","first-difference-value")): add_edge(row["identity"],field,relation,row[field])
        for field,relation in (("qualification_refs","qualification"),("provenance_refs","provenance")):
            for ordinal,target in enumerate(row[field]): add_edge(row["identity"],field,relation,target,ordinal)
    for value in source["values"]:
        for field,relation in (("unit_ref","unit"),("semantic_type_ref","semantic-type"),("source_ref","source"),("authority_ref","authority")): add_edge(value["identity"],field,relation,value[field])
    for qualification in source["qualifications"]:
        for field,relation in (("source_ref","qualification-source"),("target_ref","qualification-target"),("authority_ref","authority")): add_edge(qualification["identity"],field,relation,qualification[field])
    for provenance in source["provenance"]:
        for ordinal,target in enumerate(provenance["target_refs"]): add_edge(provenance["identity"],"target_refs","provenance-target",target,ordinal)
        add_edge(provenance["identity"],"placement_ref","placement",provenance["placement_ref"]); add_edge(provenance["identity"],"authority_ref","authority",provenance["authority_ref"])
    for obligation in source["obligations"]:
        for ordinal,target in enumerate(obligation["target_refs"]): add_edge(obligation["identity"],"target_refs","obligation-target",target,ordinal)
        add_edge(obligation["identity"],"placement_ref","placement",obligation["placement_ref"]); add_edge(obligation["identity"],"authority_ref","authority",obligation["authority_ref"])
    nodes.sort(key=lambda x:canonical(x[0])); edges.sort(key=lambda x:(canonical(x[0]),x[1].encode(),x[2],canonical(x[3]),x[4]))

    core_fragments:dict[str,Any]={}
    def index_core(value:Any)->None:
        if isinstance(value,dict):
            identity=value.get("id")
            if isinstance(identity,str):
                require(identity not in core_fragments,f"independent core semantic duplicate {identity}"); core_fragments[identity]=value
            for child in value.values(): index_core(child)
        elif isinstance(value,list):
            for child in value: index_core(child)
    for record in profile["records"]: index_core(record["semantic"])
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
    def get_path(value:Any,path:str)->Any:
        for part in path.split("/"): value=value[part]
        return value
    counterparts=[]
    for kind,items,_ in groups:
        for paired in items:
            identity=paired["identity"]; require(identity in core_fragments and identity in core_index,f"independent counterpart missing {identity}")
            core=core_fragments[identity]; comparisons=[]
            for rule_ordinal,paired_path,core_path,normalization in rules[kind]:
                if paired_path=="@decimal":
                    paired_value={"coefficient":str(paired["coefficient"]),"scale":paired["scale"]}; core_value={"coefficient":str(core["payload"]["coefficient"]),"scale":core["payload"]["scale"]}
                    paired_pointer=paired_index[identity][1]; core_pointer=core_index[identity][1]
                else:
                    paired_value=get_path(paired,paired_path); core_value=get_path(core,core_path)
                    if normalization.startswith("TABLE_"): core_value=[core_value[i] for i in (4,2,3,0,1)]
                    if normalization=="ORDERED_REF_ARRAY_V1": paired_value=[x["target_ref"] for x in paired_value]
                    if normalization=="SORTED_UTF8_SET_V1": paired_value=sorted(paired_value,key=lambda x:x.encode()); core_value=sorted(core_value,key=lambda x:x.encode())
                    paired_pointer=paired_index[identity][1]+"/"+paired_path; core_pointer=core_index[identity][1]+"/"+core_path
                require(paired_value==core_value,f"independent counterpart mismatch {kind} {identity} rule {rule_ordinal}")
                comparisons.append([rule_ordinal,paired_pointer,core_pointer,normalization,paired_value,core_value,True])
            counterparts.append([paired_index[identity][0],core_index[identity][0],kind,"briefforge:paired-core-counterpart-proof:1.0.0",domain_hash("briefforge.task075.source-fragment.v1",paired),domain_hash("briefforge.task075.source-fragment.v1",core),comparisons])
    counterparts.sort(key=lambda x:canonical(x[0]))
    requirements=[[ordinal,item[0],item[1]] for ordinal,item in enumerate(source["renderer_requirements"])]
    mappings=[[ordinal,[candidate_fingerprint,effective_graph_digest,paired_index[row][0]],relation] for ordinal,(row,relation) in enumerate(source["renderer_mappings"])]
    return nodes,edges,counterparts,requirements,mappings


def main() -> None:
    if "--skip-manifest" not in sys.argv:
        manifest_path=OUT/"final-contract-byte-manifest.json"; require(manifest_path.is_file(),"frozen manifest missing")
        manifest=load(manifest_path); require(manifest["freeze_generation"]>=8,"obsolete frozen generation")
        paths=[e["path"] for e in manifest["entries"]]; require(paths==sorted(set(paths)),"manifest paths not unique/sorted")
        for entry in manifest["entries"]:
            data=(ROOT/entry["path"]).read_bytes(); require(len(data)==entry["length"] and hashlib.sha256(data).hexdigest()==entry["sha256"],f"manifest byte mismatch: {entry['path']}")
        require(hashlib.sha256(canonical(manifest["entries"])).hexdigest()==manifest["entries_digest_sha256"],"manifest entries digest mismatch")
    spec = importlib.util.spec_from_file_location("task076_builder", GEN)
    module = importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="task076-contract-verify-") as td:
        module.OUT = Path(td); module.build()
        expected = sorted(p.name for p in OUT.iterdir() if p.is_file() and p.name != "final-contract-byte-manifest.json")
        reproduced = sorted(p.name for p in Path(td).iterdir() if p.is_file())
        require(expected == reproduced, f"artifact inventory mismatch: {expected} != {reproduced}")
        for name in expected: require((OUT/name).read_bytes() == (Path(td)/name).read_bytes(), f"nondeterministic bytes: {name}")

    registry=load(OUT/"core-object-kind-location-registry.json"); envelope=load(OUT/"task071-derivation-evidence-envelope.json")
    populations=load(OUT/"task071-derived-populations.json"); capability=load(OUT/"capability-v2-record.json"); capext=load(OUT/"capability-v2-extension.json")
    plan=load(OUT/"plan-v2-record.json"); planext=load(OUT/"plan-v2-extension.json"); completeness=load(OUT/"planning-completeness-evidence.json")
    invalid=load(OUT/"invalid-fixtures.json"); expected_findings=load(OUT/"expected-findings.json"); valid=load(OUT/"valid-fixtures.json")

    schema_pairs=[("core-object-kind-location-registry.schema.json",registry),("derivation-evidence-envelope.schema.json",envelope),("capability-v2-record.schema.json",capability),("plan-v2-record.schema.json",plan)]
    for schema_name, artifact in schema_pairs:
        errors=schema_errors(artifact,load(OUT/schema_name)); require(not errors,f"{schema_name} rejects normative bytes: {errors[:5]}")
    invalid_time=copy.deepcopy(capability); invalid_time["semantic"]["declaration_time"]="2026-99-99T99:99:99Z"; invalid_time["extensions"][0]["payload"]["issued_at_utc"]="not-a-timeZ"
    require(schema_errors(invalid_time,load(OUT/"capability-v2-record.schema.json")),"Capability schema accepted malformed canonical UTC times")
    invalid_envelope_time=copy.deepcopy(envelope); invalid_envelope_time["issued_at_utc"]="2026-02-30T00:00:00Z"
    require(schema_errors(invalid_envelope_time,load(OUT/"derivation-evidence-envelope.schema.json")),"derivation envelope schema accepted malformed canonical UTC time")
    require(not record_binding_findings(capability,valid["binding_authority"]),"Capability semantic binding differs")
    require(not record_binding_findings(plan,valid["binding_authority"]),"Plan semantic/evidence binding differs")

    reg_unsigned=copy.deepcopy(registry); reg_digest=reg_unsigned.pop("registry_digest")
    require(module.h("briefforge.task076.core-registry.v1",reg_unsigned)==reg_digest,"registry digest mismatch")
    require(len(registry["entries"])==37 and len({x["kind"] for x in registry["entries"]})==37,"registry not exactly 37 unique kinds")
    require(registry["other_counterpart_exclusions"]==[] and len(registry["counterpart_exclusions"])==1,"counterpart exclusion set not closed")

    profile_raw=PROFILE.read_bytes(); require(hashlib.sha256(profile_raw).hexdigest()==PROFILE_SHA,"TASK-071 bytes changed")
    profile=json.loads(profile_raw); core_nodes,core_index,core_edges=module.locate_core(profile,registry)
    require(len(core_nodes)==165 and len(core_edges)==722,"registry graph must reproduce 165 nodes / 722 frozen edges")
    sys.path.insert(0, str(ROOT / "src"))
    from briefforge.bcrp.model import BCRPBundle,BCRPRecord
    from briefforge.bcrp.graph import inspect_graph
    bundle=BCRPBundle("briefforge-core-representation-profile","1.0.0",tuple(BCRPRecord.from_document(r) for r in profile["records"]))
    native,native_problems=inspect_graph(bundle)
    require(not native_problems and len(native.identities)==165 and len(native.edges)==722,"frozen bcrp graph differs")
    derived_triples={(edge[0][3],edge[1],edge[3][3]) for edge in core_edges}
    require(derived_triples==set(native.edges),"registry graph edges differ from frozen bcrp graph")
    independent_nodes,independent_edges,independent_counterparts,independent_requirements,independent_mappings=independently_reconstruct_paired(profile,core_index,envelope["candidate_profile_instance_fingerprint"],envelope["effective_graph_digest"])
    require(independent_nodes==populations["paired_graph"]["nodes"],"independent paired-node reconstruction differs")
    require(independent_edges==populations["paired_graph"]["edges"],"independent paired-edge reconstruction differs")
    require(independent_counterparts==populations["counterpart_records"],"independent counterpart reconstruction differs")
    require(independent_requirements==populations["requirement_inventory"],"independent requirement reconstruction differs")
    require(independent_mappings==populations["mapping_inventory"],"independent mapping reconstruction differs")

    counts=envelope["counts"]
    require([counts[k] for k in ("sections","statements","tables","rows","values","qualifications","provenance","obligations")]==[6,76,1,7,14,27,8,5],"TASK-071 class counts differ")
    require(counts["core_edges"]==722 and counts["paired_nodes"]==counts["counterparts"]==144,"graph counts differ")
    require(len({canonical(x[1]) for x in populations["counterpart_records"]})==144,"counterparts not bijective")
    require("counterpart" not in json.dumps(populations["effective_graph"]["edges"]).lower(),"counterpart proof traversable")
    require(len(populations["requirement_inventory"])==6 and len(populations["mapping_inventory"])==7,"coverage inventories incomplete")
    require(envelope["mapping_count"]==envelope["decoded_row_count"]==7,"N != decoded rows")
    require(envelope["counterpart_exclusions"]==[["Section","order","paired-owned;core-array-position-nonauthoritative"]],"counterpart exclusions differ")
    require(envelope["graph_emission_classifications"]==[["Provenance","source_snapshot_identity","owner-typed-token-not-core-reference-for-task071;emit-snapshot-edge-only-when-exact-EvidenceSnapshot-resolves"]],"graph classification differs")
    env_unsigned=copy.deepcopy(envelope); env_fp=env_unsigned.pop("fingerprint"); require(module.h("briefforge.task076.derivation-evidence.v2",env_unsigned)==env_fp,"envelope fingerprint mismatch")
    source_ext=next(r for r in profile["records"] if r["record_kind"]=="CandidatePresentationPackageRecord")["extensions"][0]
    exact_tuple=[source_ext["owner_namespace"],source_ext["name"],source_ext["version"],source_ext["authority_ref"],source_ext["scope"],source_ext["target_refs"],source_ext["criticality"],source_ext["character"],source_ext["validation_contract"],source_ext["preservation"],source_ext["payload"]["contract_identity"],source_ext["payload"]["contract_version"]]
    require(envelope["extension_tuple"]==exact_tuple,"extension tuple is not the full exact decomposition")
    paired_raw=source_ext["payload"]["canonical_semantics"].encode(); paired_sem=json.loads(paired_raw)
    require(module.h("briefforge.task075.extension-envelope.v1",source_ext)==envelope["extension_envelope_digest"],"extension envelope digest mismatch")
    require(module.h("briefforge.task075.paired-payload.v1",paired_raw,True)==envelope["paired_payload_digest"],"paired payload digest mismatch")
    require(module.h("briefforge.task075.paired-closure.v1",paired_sem)==envelope["paired_closure_digest"],"paired closure digest mismatch")
    require(module.h("briefforge.task076.decoded-paired-population.v1",populations["paired_graph"]["nodes"])==envelope["decoded_paired_population_digest"],"decoded population digest mismatch")
    require(module.h("briefforge.task075.core-graph.v1",populations["core_graph"])==envelope["core_graph_digest"],"core graph digest mismatch")
    require(module.h("briefforge.task075.paired-graph.v1",populations["paired_graph"])==envelope["paired_graph_digest"],"paired graph digest mismatch")
    require(module.h("briefforge.task075.counterpart-proof.v1",populations["counterpart_records"])==envelope["counterpart_proof_digest"],"counterpart proof digest mismatch")
    require(module.h("briefforge.task075.effective-graph.v1",populations["effective_graph"])==envelope["effective_graph_digest"],"effective graph digest mismatch")
    require(module.h("briefforge.task075.requirement-inventory.v1",populations["requirement_inventory"])==envelope["requirement_inventory_digest"],"requirement inventory digest mismatch")
    require(module.h("briefforge.task075.mapping-inventory.v1",populations["mapping_inventory"])==envelope["mapping_inventory_digest"],"mapping inventory digest mismatch")

    extkeys={"owner_namespace","name","version","authority_ref","scope","target_refs","criticality","character","validation_contract","preservation","payload"}
    require(set(capext)==extkeys and capability["extensions"]==[capext],"Capability exact bytes differ")
    require(capext["target_refs"]==[capability["identity"]] and capext["version"]=="2.0.0","Capability binding differs")
    cap_unsigned=copy.deepcopy(capext["payload"]); cap_fp=cap_unsigned.pop("fingerprint"); require(module.h("briefforge.task075.capability-declaration.v2",cap_unsigned)==cap_fp,"Capability fingerprint mismatch")
    require(set(planext)==extkeys and plan["extensions"]==[planext],"Plan exact bytes differ")
    pp=planext["payload"]
    require(planext["target_refs"]==[plan["identity"],"candidate:task071-cross-inquiry",pp["release_identity"],pp["capability_identity"]],"Plan targets differ")
    require(len(pp["requirement_outcomes"])==6 and len(pp["mapping_outcomes"])==7 and pp["supported"] and not pp["findings"],"Plan coverage differs")
    plan_unsigned=copy.deepcopy(pp); plan_fp=plan_unsigned.pop("fingerprint"); require(module.h("briefforge.task075.plan-extension.v2",plan_unsigned)==plan_fp,"Plan fingerprint mismatch")
    require(module.h("briefforge.task075.requirement-outcomes.v1",pp["requirement_outcomes"])==pp["requirement_outcomes_digest"],"requirement digest mismatch")
    require(module.h("briefforge.task075.mapping-outcomes.v1",pp["mapping_outcomes"])==pp["mapping_outcomes_digest"],"mapping digest mismatch")
    require(module.h("briefforge.task075.planning-completeness.v1",completeness)==pp["planning_completeness_digest"],"completeness digest mismatch")
    require(completeness["mapping_count"]==7 and completeness["mapping_outcomes"]==pp["mapping_outcomes"],"completeness mappings differ")
    for i,row in enumerate(pp["mapping_outcomes"]):
        require(row[0]==i and row[1][0]==envelope["candidate_profile_instance_fingerprint"] and row[1][1]==envelope["effective_graph_digest"],"graph-scoped mapping differs")

    observed={}
    for case in invalid["fixtures"]:
        mutated=apply_mutation(invalid["base_input"],case["mutation"]); found=detect_findings(mutated)
        require(found==case["expected_findings"],f"{case['id']}: observed {found}, expected {case['expected_findings']}")
        require(all(code in expected_findings and expected_findings[code]["severity"]=="blocking" for code in found),f"{case['id']}: unregistered finding")
        observed[case["id"]]=found
    for fixture in invalid["structural_fixtures"]:
        if fixture["kind"]=="planner-cardinality":
            try: validate_cardinality(fixture); found=[]
            except AssertionError: found=["duplicate-generic-row-identity"]
        elif fixture["kind"]=="predecessor-closure":
            try: validate_closure(fixture,profile,capability,plan); found=[]
            except AssertionError: found=["incomplete-predecessor-closure"]
        else: raise AssertionError(f"unknown structural fixture {fixture['kind']}")
        require(found==fixture["expected_findings"],f"{fixture['id']}: observed {found}")
        require(all(code in expected_findings and expected_findings[code]["severity"]=="blocking" for code in found),f"{fixture['id']}: unregistered finding")
        observed[fixture["id"]]=found
    for fixture in invalid["correlated_fixtures"]:
        mutated=copy.deepcopy(invalid["base_input"]); mutated.update(copy.deepcopy(fixture["sets"])); found=detect_findings(mutated)
        require(found==fixture["expected_findings"],f"{fixture['id']}: observed {found}")
        observed[fixture["id"]]=found
    artifacts={"capability-v2-record.json":capability,"plan-v2-record.json":plan}
    for fixture in invalid["record_fixtures"]:
        mutated=copy.deepcopy(artifacts[fixture["artifact"]])
        mutations=fixture.get("mutations",[fixture.get("mutation")])
        for mutation in mutations:
            require(mutation is not None,f"{fixture['id']}: missing mutation")
            cursor=mutated; path=mutation["path"]
            for key in path[:-1]: cursor=cursor[key]
            cursor[path[-1]]=mutation["value"]
        payload=mutated["extensions"][0]["payload"]
        if fixture.get("recompute_semantic_digest"):
            semantic_domain="briefforge.task076.capability-core-semantic.v1" if mutated["record_kind"]=="RendererCapabilityDeclarationRecord" else "briefforge.task076.plan-core-semantic.v1"
            payload["semantic_digest"]=domain_hash(semantic_domain,mutated["semantic"])
        if fixture.get("recompute_fingerprint"):
            fingerprint_domain="briefforge.task075.capability-declaration.v2" if mutated["record_kind"]=="RendererCapabilityDeclarationRecord" else "briefforge.task075.plan-extension.v2"
            payload.pop("fingerprint",None); payload["fingerprint"]=domain_hash(fingerprint_domain,payload)
        schema_name="capability-v2-record.schema.json" if fixture["artifact"].startswith("capability") else "plan-v2-record.schema.json"
        require(not schema_errors(mutated,load(OUT/schema_name)),f"{fixture['id']}: mutation must remain schema-shaped")
        found=record_binding_findings(mutated,valid["binding_authority"])
        require(found==fixture["expected_findings"],f"{fixture['id']}: observed {found}")
        observed[fixture["id"]]=found
    require(observed["zero-mappings-nonempty-obligations"]==["empty-mapping-coverage"],"zero coverage passed")

    exercised_findings={code for codes in observed.values() for code in codes}
    require(exercised_findings==set(expected_findings),f"negative finding coverage differs: missing={sorted(set(expected_findings)-exercised_findings)} surplus={sorted(exercised_findings-set(expected_findings))}")
    cardinalities=[]; closures=[]
    for fixture in valid["fixtures"]:
        if fixture.get("kind")=="planner-cardinality":
            validate_cardinality(fixture); cardinalities.append(fixture["N"])
        elif fixture.get("kind")=="predecessor-closure": validate_closure(fixture,profile,capability,plan); closures.append(len(fixture["records"]))
    require(cardinalities==[0,1,7,16] and closures==[8,10],"generic cardinality/closure fixtures incomplete")

    result={"status":"PASS","deterministic_artifacts":len(expected),"schemas_valid":len(schema_pairs),"registry_entries":37,"core_nodes":165,"core_edges":722,"valid_fixtures":len(valid["fixtures"]),"invalid_fixtures":len(invalid["fixtures"])+len(invalid["structural_fixtures"])+len(invalid["correlated_fixtures"])+len(invalid["record_fixtures"]),"invalid_fixture_passes":len(observed),"generic_cardinalities":cardinalities,"predecessor_closures":closures,"task071":{"paired_objects":144,"unique_core_counterparts":144,"counterpart_mismatches":0,"renderer_requirements":6,"owner_mappings":7,"plan_rows":7,"section_order":"counterpart-excluded"},"authority":"exact Candidate/profile bytes only; generated evidence is non-authority fixture material","counterpart_traversable":False,"zero_coverage_allowed":False}
    print(json.dumps(result,sort_keys=True))

if __name__ == "__main__": main()
