"""Semantic graph reconstruction from canonical BCRP relationship directions."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .model import BCRPBundle, SemanticGraph

REFERENCE_LIST_KEYS = {
    "artifact_audit_refs",
    "authority_refs",
    "caveat_ids",
    "children",
    "conformance_refs",
    "evidence_refs",
    "evidence_snapshot_refs",
    "exhibit_ids",
    "expressed_statement_ids",
    "fallback_refs",
    "material_refs",
    "obligation_ids",
    "renderer_requirement_ids",
    "required_value_ids",
    "source_value_refs",
    "state_ids",
    "statement_ids",
    "static_expression",
    "print_expression",
    "target_refs",
    "uncertainty_ids",
    "upstream_refs",
    "value_ids",
}


class GraphReconstructionError(ValueError):
    """Raised when the profile cannot reconstruct one unambiguous graph."""

    def __init__(self, problems: tuple[tuple[str, str, str], ...]):
        self.problems = problems
        super().__init__("; ".join(f"{kind} at {location}: {value}" for kind, location, value in problems))


def inspect_graph(bundle: BCRPBundle) -> tuple[SemanticGraph, tuple[tuple[str, str, str], ...]]:
    identities: dict[str, str] = {}
    edges: list[tuple[str, str, str]] = []
    problems: list[tuple[str, str, str]] = []

    def register(identity: str, location: str) -> None:
        if identity in identities:
            problems.append(("duplicate-identity", location, identity))
        else:
            identities[identity] = location

    def register_objects(value: Any, location: str) -> None:
        if isinstance(value, dict):
            if isinstance(value.get("id"), str):
                register(value["id"], location)
            for key, child in value.items():
                register_objects(child, f"{location}/{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                register_objects(child, f"{location}/{index}")

    for record in bundle.records:
        register(record.identity, record.identity)
        register_objects(record.semantic, f"{record.identity}/semantic")
        register_objects(record.extensions, f"{record.identity}/extensions")

    def collect(value: Any, owner: str, location: str) -> None:
        if isinstance(value, dict):
            current_owner = value.get("id") if isinstance(value.get("id"), str) else owner
            for key, child in value.items():
                child_location = f"{location}/{key}"
                if key.endswith("_ref") and isinstance(child, str):
                    edges.append((current_owner, key, child))
                elif (key.endswith("_refs") or key in REFERENCE_LIST_KEYS) and isinstance(child, list):
                    for target in child:
                        if isinstance(target, str):
                            edges.append((current_owner, key, target))
                collect(child, current_owner, child_location)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                collect(child, owner, f"{location}/{index}")

    for record in bundle.records:
        collect(record.semantic, record.identity, f"{record.identity}/semantic")
        collect(record.extensions, record.identity, f"{record.identity}/extensions")

    seen_edges: set[tuple[str, str, str]] = set()
    for edge in edges:
        if edge in seen_edges:
            problems.append(("duplicate-edge", edge[0], f"{edge[1]}->{edge[2]}"))
        seen_edges.add(edge)
        if edge[2] not in identities:
            problems.append(("dangling-reference", edge[0], edge[2]))

    canonical_edges = tuple(sorted(seen_edges))
    reverse: dict[str, list[str]] = defaultdict(list)
    for source, relation, target in canonical_edges:
        reverse[target].append(f"{source}|{relation}")
    reverse_index = {target: sorted(sources) for target, sources in sorted(reverse.items())}
    graph = SemanticGraph(tuple(sorted(identities)), canonical_edges, reverse_index)
    return graph, tuple(sorted(set(problems)))


def reconstruct_graph(bundle: BCRPBundle) -> SemanticGraph:
    """Reconstruct canonical edges and reject ambiguity or dangling internal references."""

    graph, problems = inspect_graph(bundle)
    if problems:
        raise GraphReconstructionError(problems)
    return graph
