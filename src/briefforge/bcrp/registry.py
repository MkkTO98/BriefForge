"""Closed generation-8 core object registry and registry-driven graph."""
from __future__ import annotations

from dataclasses import dataclass
import re
from types import MappingProxyType
from typing import Any, Mapping

from briefforge.task076_contracts import (
    AuthenticatedGeneration8Candidate, authenticate_generation8_candidate, canonical_json,
    domain_digest, load_generation8_candidate, load_task076_contracts,
)

CORE_DOMAIN = ("briefforge:bcrp-core", "1.0.0")
_PROFILE = ("briefforge-core-representation-profile", "1.0.0")
_PLACEHOLDERS = {"{record_index}", "{index}", "{set_index}", "{exhibit_index}"}
_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*$")
_REFERENCE_LIST_KEYS = {
    "artifact_audit_refs", "authority_refs", "caveat_ids", "children", "conformance_refs",
    "evidence_refs", "evidence_snapshot_refs", "exhibit_ids", "expressed_statement_ids",
    "fallback_refs", "material_refs", "obligation_ids", "renderer_requirement_ids",
    "required_value_ids", "source_value_refs", "state_ids", "statement_ids",
    "static_expression", "print_expression", "target_refs", "uncertainty_ids",
    "upstream_refs", "value_ids",
}

class CoreRegistryError(ValueError):
    pass


def _escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


@dataclass(frozen=True)
class CoreObject:
    dqi: tuple[str, str, str, str]
    record_identity: str
    pointer: str
    fragment_digest: str
    fragment: Mapping[str, Any]

    def wire(self) -> list[Any]:
        return [list(self.dqi), self.record_identity, self.pointer, self.fragment_digest]


@dataclass(frozen=True)
class VerifiedCoreGraph:
    candidate_profile_instance_fingerprint: str
    nodes: tuple[CoreObject, ...]
    edges: tuple[tuple[Any, ...], ...]
    source_digest: str
    digest: str

    @property
    def identities(self) -> tuple[str, ...]:
        return tuple(node.dqi[3] for node in self.nodes)

    def document(self) -> dict[str, Any]:
        return {"contract": "briefforge:verified-core-semantic-graph:1.0.0",
                "candidate_profile_instance_fingerprint": self.candidate_profile_instance_fingerprint,
                "domain": list(CORE_DOMAIN), "nodes": [n.wire() for n in self.nodes],
                "edges": [_wire(e) for e in self.edges], "source_digest": self.source_digest}


def _wire(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_wire(x) for x in value]
    return value


def core_registry() -> Mapping[str, Any]:
    registry = load_task076_contracts().document("core-object-kind-location-registry.json")
    if (registry.get("contract") != "briefforge:core-object-kind-location-registry:1.0.0" or
            tuple(tuple(x) for x in registry.get("profile_dispatch", ())) != (_PROFILE,) or
            len(registry.get("entries", ())) != 37 or
            len({e.get("kind") for e in registry["entries"]}) != 37):
        raise CoreRegistryError("authenticated core registry has unsupported closure")
    provisional = {k: _thaw(v) for k, v in registry.items() if k != "registry_digest"}
    if domain_digest("briefforge.task076.core-registry.v1", provisional) != registry.get("registry_digest"):
        raise CoreRegistryError("authenticated core registry domain digest differs")
    return registry


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping): return {k: _thaw(v) for k, v in value.items()}
    if isinstance(value, tuple): return [_thaw(x) for x in value]
    return value


def _freeze(value: Any) -> Any:
    if type(value) is dict:
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if type(value) is list:
        return tuple(_freeze(item) for item in value)
    return value


def _candidate_parts(candidate: AuthenticatedGeneration8Candidate | None) -> tuple[dict[str, Any], str]:
    candidate = candidate or load_generation8_candidate()
    try:
        candidate = authenticate_generation8_candidate(candidate)
    except Exception as exc:
        raise CoreRegistryError("authenticated generation-8 Candidate required") from exc
    profile = _thaw(candidate.profile_document)
    declared = profile.get("profile", {})
    if (declared.get("identity"), declared.get("version")) != _PROFILE:
        raise CoreRegistryError("unsupported core profile/version")
    return profile, candidate.candidate_profile_instance_fingerprint


def _select(value: Any, parts: list[str], pointer: str) -> list[tuple[Any, str]]:
    if not parts: return [(value, pointer)]
    part, rest = parts[0], parts[1:]
    selected: list[tuple[Any, str]] = []
    if part in _PLACEHOLDERS:
        if type(value) is not list: return []
        for i, child in enumerate(value): selected.extend(_select(child, rest, f"{pointer}/{i}"))
    elif type(value) is dict and part in value:
        selected.extend(_select(value[part], rest, pointer + "/" + _escape(part)))
    return selected


def execute_core_registry(candidate: AuthenticatedGeneration8Candidate | None = None) -> tuple[tuple[CoreObject, ...], Mapping[str, CoreObject]]:
    profile, _ = _candidate_parts(candidate)
    registry = core_registry()
    records = profile.get("records")
    if type(records) is not list:
        raise CoreRegistryError("profile records are not an exact array")
    known_record_kinds = {e["kind"] for e in registry["entries"] if e["canonical_locations"] == ("/records/{record_index}",)}
    unknown = [r.get("record_kind") for r in records if type(r) is not dict or r.get("record_kind") not in known_record_kinds]
    if unknown: raise CoreRegistryError(f"unknown core record kind: {unknown[0]!r}")
    record_by_pointer = {f"/records/{i}": r for i, r in enumerate(records)}
    objects: list[CoreObject] = []
    index: dict[str, CoreObject] = {}
    selected_pointers: set[str] = set()
    for entry in registry["entries"]:
        for template in entry["canonical_locations"]:
            parts = [x for x in template.split("/") if x]
            if not parts or parts[0] != "records": parts = ["records", "{record_index}"] + parts
            for fragment, pointer in _select(profile, parts, ""):
                owner_pointer = "/".join(pointer.split("/")[:3])
                owner = record_by_pointer.get(owner_pointer)
                if not owner or owner.get("record_kind") not in entry["owning_record_kinds"]: continue
                if template == "/records/{record_index}" and fragment.get("record_kind") != entry["kind"]: continue
                identity = fragment.get(entry["identity_field"]) if type(fragment) is dict else None
                if type(identity) is not str or not _ID.fullmatch(identity):
                    raise CoreRegistryError(f"missing/invalid {entry['kind']} identity at {pointer}")
                if identity in index:
                    raise CoreRegistryError(f"duplicate core identity {identity!r}")
                dqi = CORE_DOMAIN + (entry["kind"], identity)
                obj = CoreObject(dqi, owner["identity"], pointer,
                    domain_digest("briefforge.task075.source-fragment.v1", fragment),
                    _freeze(fragment))
                objects.append(obj); index[identity] = obj; selected_pointers.add(pointer)
    # Reject identity-bearing semantic objects outside the 37 exact locators.
    def inspect(value: Any, pointer: str) -> None:
        if type(value) is dict:
            if "id" in value and pointer not in selected_pointers:
                raise CoreRegistryError(f"unknown or misplaced core object at {pointer}")
            for k, v in value.items(): inspect(v, pointer + "/" + _escape(k))
        elif type(value) is list:
            for i, v in enumerate(value): inspect(v, f"{pointer}/{i}")
    for i, record in enumerate(records): inspect(record.get("semantic"), f"/records/{i}/semantic")
    objects.sort(key=lambda x: canonical_json(list(x.dqi)))
    return tuple(objects), MappingProxyType(index)


def reconstruct_core_graph(candidate: AuthenticatedGeneration8Candidate | None = None) -> VerifiedCoreGraph:
    candidate = candidate or load_generation8_candidate()
    profile, fingerprint = _candidate_parts(candidate)
    nodes, index = execute_core_registry(candidate)
    edges: list[tuple[Any, ...]] = []
    def collect(value: Any, owner: str, pointer: str) -> None:
        if type(value) is dict:
            current = value.get("id") if type(value.get("id")) is str else owner
            for key, child in value.items():
                p = pointer + "/" + _escape(key)
                targets: list[tuple[int, str]] = []
                if key.endswith("_ref") and type(child) is str: targets = [(0, child)]
                elif (key.endswith("_refs") or key in _REFERENCE_LIST_KEYS) and type(child) is list:
                    targets = [(i, x) for i, x in enumerate(child) if type(x) is str]
                for ordinal, target in targets:
                    if target not in index: raise CoreRegistryError(f"dangling core target {target!r} at {p}")
                    source = index.get(current) or index.get(owner)
                    if source is None: raise CoreRegistryError(f"unknown edge source {current!r}")
                    target_obj = index[target]
                    attrs = {"source_pointer": pointer, "source_field": key,
                             "target_kind": target_obj.dqi[2]}
                    edges.append((source.dqi, key, ordinal, target_obj.dqi,
                        domain_digest("briefforge.task075.edge-attributes.v1", attrs)))
                collect(child, current, p)
        elif type(value) is list:
            for i, child in enumerate(value): collect(child, owner, f"{pointer}/{i}")
    for i, record in enumerate(profile["records"]):
        collect(record["semantic"], record["identity"], f"/records/{i}/semantic")
        collect(record["extensions"], record["identity"], f"/records/{i}/extensions")
    if len(edges) != len(set(edges)): raise CoreRegistryError("duplicate core graph edge")
    edges.sort(key=lambda e: (canonical_json(list(e[0])), e[1].encode(), e[2], canonical_json(list(e[3])), e[4]))
    source_digest = domain_digest("briefforge.task075.source-fragment.v1", profile)
    provisional = VerifiedCoreGraph(fingerprint, nodes, tuple(edges), source_digest, "")
    digest = domain_digest("briefforge.task075.core-graph.v1", provisional.document())
    return VerifiedCoreGraph(fingerprint, nodes, tuple(edges), source_digest, digest)


def resolve_core_locator(pointer: str, *, expected_kind: str,
                         candidate: AuthenticatedGeneration8Candidate | None = None) -> CoreObject:
    if type(pointer) is not str or type(expected_kind) is not str:
        raise CoreRegistryError("exact locator and kind required")
    nodes, _ = execute_core_registry(candidate)
    matches = [n for n in nodes if n.pointer == pointer]
    if len(matches) != 1 or matches[0].dqi[2] != expected_kind:
        raise CoreRegistryError("unknown, ambiguous, or kind-mismatched core locator")
    return matches[0]
