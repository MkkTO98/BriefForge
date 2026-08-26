"""Exact paired-v3 decoding, graph emission and core-counterpart proof."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from types import MappingProxyType
from typing import Any, Mapping

from briefforge.bcrp.registry import CoreObject, VerifiedCoreGraph, reconstruct_core_graph
from briefforge.task076_contracts import (
    AuthenticatedGeneration8Candidate, authenticate_generation8_candidate, canonical_json,
    domain_digest, load_generation8_candidate,
)
from briefforge_paired_terminal_profile.profile import validate_candidate_paired_semantics

PAIRED_DOMAIN = ("briefforge:paired-terminal", "3.0.0")
PAIRED_PROFILE = ("briefforge:representative-paired-terminal-static-html-profile", "3.0.0")
_KINDS = ("Section", "Statement", "Table", "Row", "Value", "Qualification", "Provenance", "Obligation")

class PairedInterpretationError(ValueError):
    pass


@dataclass(frozen=True)
class PairedObject:
    dqi: tuple[str, str, str, str]
    pointer: str
    fragment_digest: str
    fragment: Mapping[str, Any]
    def wire(self) -> list[Any]: return [list(self.dqi), self.pointer, self.fragment_digest]


@dataclass(frozen=True)
class VerifiedPairedGraph:
    candidate_profile_instance_fingerprint: str
    nodes: tuple[PairedObject, ...]
    edges: tuple[tuple[Any, ...], ...]
    source_digest: str
    digest: str
    def document(self) -> dict[str, Any]:
        return {"contract": "briefforge:verified-paired-semantic-graph:1.0.0",
            "candidate_profile_instance_fingerprint": self.candidate_profile_instance_fingerprint,
            "domain": list(PAIRED_DOMAIN), "nodes": [n.wire() for n in self.nodes],
            "edges": [_wire(e) for e in self.edges], "source_digest": self.source_digest}


@dataclass(frozen=True)
class CounterpartProof:
    paired_dqi: tuple[str, str, str, str]
    core_dqi: tuple[str, str, str, str]
    paired_kind: str
    contract: str
    paired_fragment_digest: str
    core_fragment_digest: str
    comparisons: tuple[tuple[Any, ...], ...]
    traversable: bool = False
    def wire(self) -> list[Any]:
        return [list(self.paired_dqi), list(self.core_dqi), self.paired_kind, self.contract,
                self.paired_fragment_digest, self.core_fragment_digest,
                [_wire(x) for x in self.comparisons]]


@dataclass(frozen=True)
class VerifiedEffectiveGraph:
    candidate_profile_instance_fingerprint: str
    core_graph_digest: str
    paired_graph_digest: str
    counterpart_proof_digest: str
    nodes: tuple[Any, ...]
    edges: tuple[tuple[Any, ...], ...]
    digest: str
    def document(self) -> dict[str, Any]:
        return {"contract": "briefforge:verified-effective-semantic-graph:1.0.0",
            "candidate_profile_instance_fingerprint": self.candidate_profile_instance_fingerprint,
            "core_graph_digest": self.core_graph_digest, "paired_graph_digest": self.paired_graph_digest,
            "counterpart_proof_digest": self.counterpart_proof_digest,
            "nodes": [x.wire() for x in self.nodes], "edges": [_wire(e) for e in self.edges]}


@dataclass(frozen=True)
class PairedInterpretation:
    semantics: Any
    semantic_document: Mapping[str, Any]
    inventory: tuple[PairedObject, ...]
    index: Mapping[str, PairedObject]
    core_graph: VerifiedCoreGraph
    paired_graph: VerifiedPairedGraph
    counterparts: tuple[CounterpartProof, ...]
    counterpart_proof_digest: str
    effective_graph: VerifiedEffectiveGraph
    requirement_inventory: tuple[tuple[Any, ...], ...]
    requirement_inventory_digest: str
    mapping_inventory: tuple[tuple[Any, ...], ...]
    mapping_inventory_digest: str


def _wire(value: Any) -> Any:
    if isinstance(value, tuple): return [_wire(x) for x in value]
    return value


def _freeze(value: Any) -> Any:
    if type(value) is dict:
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if type(value) is list:
        return tuple(_freeze(item) for item in value)
    return value


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return value


def _candidate(candidate: AuthenticatedGeneration8Candidate | None) -> AuthenticatedGeneration8Candidate:
    candidate = candidate or load_generation8_candidate()
    try:
        candidate = authenticate_generation8_candidate(candidate)
    except Exception as exc:
        raise PairedInterpretationError("authenticated generation-8 Candidate required") from exc
    if (candidate.bundle.profile_identity, candidate.bundle.profile_version) != (
            "briefforge-core-representation-profile", "1.0.0"):
        raise PairedInterpretationError("unsupported BCRP profile/version")
    return candidate


def decode_paired_inventory(candidate: AuthenticatedGeneration8Candidate | None = None
                            ) -> tuple[Any, Mapping[str, Any], tuple[PairedObject, ...], Mapping[str, PairedObject]]:
    candidate = _candidate(candidate)
    try:
        semantics = validate_candidate_paired_semantics(candidate.bundle)
        # Convert immutable DTO tuples into their exact JSON array wire types.
        document = json.loads(canonical_json(asdict(semantics)))
        # Independent canonical re-encode against the authenticated extension bytes.
        extension = candidate.bundle.one("CandidatePresentationPackageRecord").extensions[0]
        raw = extension["payload"]["canonical_semantics"]
        if canonical_json(document) != raw.encode("utf-8"):
            raise PairedInterpretationError("paired decoder did not exactly re-encode its authority bytes")
    except PairedInterpretationError:
        raise
    except Exception as exc:
        raise PairedInterpretationError(str(exc)) from exc
    specs = (("Section", document["sections"], "/sections"),
             ("Statement", document["statements"], "/statements"),
             ("Table", (document["table"],), "/table"),
             ("Row", document["table"]["rows"], "/table/rows"),
             ("Value", document["values"], "/values"),
             ("Qualification", document["qualifications"], "/qualifications"),
             ("Provenance", document["provenance"], "/provenance"),
             ("Obligation", document["obligations"], "/obligations"))
    inventory: list[PairedObject] = []; index: dict[str, PairedObject] = {}
    for kind, items, base in specs:
        for i, fragment in enumerate(items):
            identity = fragment.get("identity") if type(fragment) is dict else None
            if type(identity) is not str or identity in index:
                raise PairedInterpretationError("missing or duplicate paired identity")
            pointer = base if kind == "Table" else f"{base}/{i}"
            obj = PairedObject(PAIRED_DOMAIN + (kind, identity), pointer,
                domain_digest("briefforge.task075.source-fragment.v1", fragment),
                _freeze(fragment))
            inventory.append(obj); index[identity] = obj
    inventory.sort(key=lambda x: canonical_json(list(x.dqi)))
    return semantics, _freeze(document), tuple(inventory), MappingProxyType(index)


def interpret_paired_candidate(candidate: AuthenticatedGeneration8Candidate | None = None) -> PairedInterpretation:
    candidate = _candidate(candidate)
    semantics, sem, nodes, pindex = decode_paired_inventory(candidate)
    core = reconstruct_core_graph(candidate)
    cindex = {n.dqi[3]: n for n in core.nodes}
    edges: list[tuple[Any, ...]] = []
    def edge(source: str, field: str, relation: str, target: str, ordinal: int = 0) -> None:
        target_obj = pindex.get(target) or cindex.get(target)
        if target_obj is None: raise PairedInterpretationError(f"dangling paired target {target!r}")
        source_obj = pindex.get(source)
        if source_obj is None: raise PairedInterpretationError(f"unknown paired source {source!r}")
        attrs = {"source_pointer": source_obj.pointer, "source_field": field,
                 "target_kind": target_obj.dqi[2]}
        edges.append((source_obj.dqi, relation, ordinal, target_obj.dqi,
                      domain_digest("briefforge.task075.edge-attributes.v1", attrs)))
    for section in sem["sections"]:
        for i, child in enumerate(section["children"]): edge(section["identity"], "children", "ordered-child", child["target_ref"], i)
    table = sem["table"]
    edge(table["identity"], "purpose_ref", "purpose", table["purpose_ref"])
    edge(table["identity"], "authority_ref", "authority", table["authority_ref"])
    for i, row in enumerate(table["rows"]): edge(table["identity"], "rows", "ordered-row", row["identity"], i)
    for statement in sem["statements"]: edge(statement["identity"], "authority_ref", "authority", statement["authority_ref"])
    for row in table["rows"]:
        for field, relation in (("row_statement_ref", "row-statement"), ("raw_value_ref", "raw-value"),
                                ("first_difference_value_ref", "first-difference-value")):
            edge(row["identity"], field, relation, row[field])
        for field, relation in (("qualification_refs", "qualification"), ("provenance_refs", "provenance")):
            for i, target in enumerate(row[field]): edge(row["identity"], field, relation, target, i)
    for value in sem["values"]:
        for field, relation in (("unit_ref", "unit"), ("semantic_type_ref", "semantic-type"),
                                ("source_ref", "source"), ("authority_ref", "authority")):
            edge(value["identity"], field, relation, value[field])
    for qualification in sem["qualifications"]:
        for field, relation in (("source_ref", "qualification-source"), ("target_ref", "qualification-target"),
                                ("authority_ref", "authority")):
            edge(qualification["identity"], field, relation, qualification[field])
    for provenance in sem["provenance"]:
        for i, target in enumerate(provenance["target_refs"]): edge(provenance["identity"], "target_refs", "provenance-target", target, i)
        edge(provenance["identity"], "placement_ref", "placement", provenance["placement_ref"])
        edge(provenance["identity"], "authority_ref", "authority", provenance["authority_ref"])
        snapshot = provenance.get("source_snapshot_identity")
        if snapshot in cindex and cindex[snapshot].dqi[2] == "EvidenceSnapshot":
            edge(provenance["identity"], "source_snapshot_identity", "source-snapshot", snapshot)
    for obligation in sem["obligations"]:
        for i, target in enumerate(obligation["target_refs"]): edge(obligation["identity"], "target_refs", "obligation-target", target, i)
        edge(obligation["identity"], "placement_ref", "placement", obligation["placement_ref"])
        edge(obligation["identity"], "authority_ref", "authority", obligation["authority_ref"])
    if len(edges) != len(set(edges)): raise PairedInterpretationError("duplicate paired graph edge")
    edges.sort(key=lambda e: (canonical_json(list(e[0])), e[1].encode(), e[2], canonical_json(list(e[3])), e[4]))
    candidate_record = candidate.bundle.one("CandidatePresentationPackageRecord")
    raw = candidate_record.extensions[0]["payload"]["canonical_semantics"].encode("utf-8")
    paired0 = VerifiedPairedGraph(candidate.candidate_profile_instance_fingerprint, nodes, tuple(edges),
        domain_digest("briefforge.task075.paired-payload.v1", raw, raw=True), "")
    pdigest = domain_digest("briefforge.task075.paired-graph.v1", paired0.document())
    paired = VerifiedPairedGraph(paired0.candidate_profile_instance_fingerprint, nodes, tuple(edges), paired0.source_digest, pdigest)
    proofs = _counterparts(sem, pindex, cindex)
    proof_digest = domain_digest("briefforge.task075.counterpart-proof.v1", [p.wire() for p in proofs])
    all_nodes: tuple[Any, ...] = core.nodes + paired.nodes
    all_edges = core.edges + paired.edges
    effective0 = VerifiedEffectiveGraph(candidate.candidate_profile_instance_fingerprint, core.digest,
        paired.digest, proof_digest, all_nodes, all_edges, "")
    edigest = domain_digest("briefforge.task075.effective-graph.v1", effective0.document())
    effective = VerifiedEffectiveGraph(effective0.candidate_profile_instance_fingerprint, core.digest,
        paired.digest, proof_digest, all_nodes, all_edges, edigest)
    requirements = tuple((i, x[0], x[1]) for i, x in enumerate(sem["renderer_requirements"]))
    mappings = tuple((i, (candidate.candidate_profile_instance_fingerprint, edigest, pindex[row].dqi), rel)
                     for i, (row, rel) in enumerate(sem["renderer_mappings"]))
    if len(mappings) != len(sem["table"]["rows"]):
        raise PairedInterpretationError("mapping count differs from decoded row count")
    return PairedInterpretation(semantics, sem, nodes, pindex, core, paired, proofs, proof_digest,
        effective, requirements, domain_digest("briefforge.task075.requirement-inventory.v1", requirements),
        mappings, domain_digest("briefforge.task075.mapping-inventory.v1", mappings))


_RULES = {
 "Section": ((0,"identity","id","EXACT_JSON_V1"),(1,"title","title","EXACT_JSON_V1"),(2,"children","children","ORDERED_REF_ARRAY_V1")),
 "Statement": ((3,"identity","id","EXACT_JSON_V1"),(4,"text","text","EXACT_JSON_V1"),(5,"role","posture","EXACT_JSON_V1"),(6,"authority_ref","authority_ref","EXACT_JSON_V1")),
 "Table": ((7,"identity","id","EXACT_JSON_V1"),(8,"column_identities","column_ids","TABLE_COLUMN_ID_PERMUTE_4_2_3_0_1_V1"),(9,"column_headings","headings","TABLE_HEADING_PERMUTE_4_2_3_0_1_V1")),
 "Row": ((10,"identity","id","EXACT_JSON_V1"),(11,"order","order","EXACT_JSON_V1"),(12,"relationship_identity","relationship_identity","EXACT_JSON_V1"),(13,"relationship_label","relationship_label","EXACT_JSON_V1"),(14,"raw_value_ref","primary_ref","EXACT_JSON_V1"),(15,"first_difference_value_ref","comparison_ref","EXACT_JSON_V1")),
 "Value": ((16,"identity","id","EXACT_JSON_V1"),(17,"value_state","value_state","EXACT_JSON_V1"),(18,"@decimal","payload","SCALED_INTEGER_DECIMAL_V1"),(19,"scale","payload/scale","EXACT_JSON_V1"),(20,"lexical_representation","lexical_representation","EXACT_JSON_V1"),(21,"unit_ref","unit_ref","EXACT_JSON_V1"),(22,"semantic_type_ref","semantic_type_ref","EXACT_JSON_V1"),(23,"source_ref","source_ref","EXACT_JSON_V1"),(24,"authority_ref","authority_ref","EXACT_JSON_V1"),(25,"method_ref","method","EXACT_JSON_V1"),(26,"transformation_identity","transformation","EXACT_JSON_V1"),(27,"transformation_state","transformation_state","EXACT_JSON_V1"),(28,"aligned_period","aligned_period","EXACT_JSON_V1"),(29,"aligned_count","aligned_count","EXACT_JSON_V1"),(30,"package_identity","package_id","EXACT_JSON_V1")),
 "Qualification": ((31,"identity","id","EXACT_JSON_V1"),(32,"kind","kind","EXACT_JSON_V1"),(33,"source_ref","source_ref","EXACT_JSON_V1"),(34,"target_ref","target_ref","EXACT_JSON_V1"),(35,"authority_ref","authority_ref","EXACT_JSON_V1"),(36,"target_order","declared_target_order","EXACT_JSON_V1")),
 "Provenance": ((37,"identity","id","EXACT_JSON_V1"),(38,"citation","citation","EXACT_JSON_V1"),(39,"authority_ref","authority_ref","EXACT_JSON_V1"),(40,"target_refs","target_refs","SORTED_UTF8_SET_V1")),
 "Obligation": ((41,"identity","id","EXACT_JSON_V1"),(42,"kind","kind","EXACT_JSON_V1"),(43,"target_refs","target_refs","SORTED_UTF8_SET_V1"),(44,"authority_ref","authority_ref","EXACT_JSON_V1")),
}
_EXPECTED_CORE_KIND = {"Section":"Section", "Statement":"PresentationStatement", "Table":"Exhibit",
 "Row":"CaseBinding", "Value":"MaterializedValue", "Qualification":"TypedRelation",
 "Provenance":"MaterialProvenance", "Obligation":"Obligation"}


def _get(value: Any, path: str) -> Any:
    for part in path.split("/"): value = value[part]
    return value


def _counterparts(sem: Mapping[str, Any], pindex: Mapping[str, PairedObject],
                  cindex: Mapping[str, CoreObject]) -> tuple[CounterpartProof, ...]:
    groups = (("Section", sem["sections"]), ("Statement", sem["statements"]),
              ("Table", (sem["table"],)), ("Row", sem["table"]["rows"]),
              ("Value", sem["values"]), ("Qualification", sem["qualifications"]),
              ("Provenance", sem["provenance"]), ("Obligation", sem["obligations"]))
    proofs: list[CounterpartProof] = []; used: set[tuple[str, str, str, str]] = set()
    for kind, objects in groups:
        for paired_fragment in objects:
            identity = paired_fragment["identity"]
            core = cindex.get(identity)
            if core is None or core.dqi[2] != _EXPECTED_CORE_KIND[kind]:
                raise PairedInterpretationError(f"missing or wrong-kind counterpart {identity!r}")
            if core.dqi in used: raise PairedInterpretationError("counterpart target collision")
            used.add(core.dqi); comparisons = []
            for ordinal, pp, cp, normalization in _RULES[kind]:
                if pp == "@decimal":
                    pv = {"coefficient": str(paired_fragment["coefficient"]), "scale": paired_fragment["scale"]}
                    cv = {"coefficient": str(core.fragment["payload"]["coefficient"]), "scale": core.fragment["payload"]["scale"]}
                    pptr, cptr = pindex[identity].pointer, core.pointer
                else:
                    pv, cv = _get(paired_fragment, pp), _get(core.fragment, cp)
                    pptr, cptr = pindex[identity].pointer + "/" + pp, core.pointer + "/" + cp
                    if normalization.startswith("TABLE_"): cv = [cv[i] for i in (4,2,3,0,1)]
                    if normalization == "ORDERED_REF_ARRAY_V1": pv = [x["target_ref"] for x in pv]
                    if normalization == "SORTED_UTF8_SET_V1":
                        pv, cv = sorted(pv, key=lambda x:x.encode()), sorted(cv, key=lambda x:x.encode())
                pv, cv = _plain(pv), _plain(cv)
                if pv != cv: raise PairedInterpretationError(f"counterpart mismatch {kind} {identity} field {pp}")
                comparisons.append((ordinal, pptr, cptr, normalization, pv, cv, True))
            po = pindex[identity]
            proofs.append(CounterpartProof(po.dqi, core.dqi, kind,
                "briefforge:paired-core-counterpart-proof:1.0.0", po.fragment_digest,
                core.fragment_digest, tuple(comparisons), False))
    proofs.sort(key=lambda x: canonical_json(list(x.paired_dqi)))
    if len(proofs) != len(pindex) or any(p.traversable for p in proofs):
        raise PairedInterpretationError("counterpart proof is incomplete or traversable")
    return tuple(proofs)
