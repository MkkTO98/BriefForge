#!/usr/bin/env python3
"""TASK-069 governed, single-attempt Candidate authoring program.

Importing this module and exercising its construction/preflight validators does not
consume the attempt.  Only ``main`` reaches ``_consume_attempt_and_author``.  This
program intentionally contains no lifecycle, Release, token, projection, renderer,
publication, delivery, or deployment operation.
"""
from __future__ import annotations

from contextlib import suppress
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable

from briefforge.bcrp.authoring import RecordDraft
from briefforge.bcrp.authoring import author_candidate_bundle as _task069_author_once
from briefforge.bcrp.canonical import (
    bundle_from_canonical_json,
    canonical_json_bytes,
    fingerprint_bundle,
)
from briefforge.bcrp.model import BCRPBundle
from briefforge.bcrp.validation import validate_bundle
from briefforge.bounded_loopback_deployment import DeploymentRouteItem, DeploymentTarget
from briefforge_paired_terminal_profile.profile import build_paired_semantic_extension
from briefforge_paired_terminal_profile.schema import (
    Obligation, PairedRow, PairedSemanticInput, PairedTable, PairedValue,
    Provenance, QualificationEdge, RENDERER_REQUIREMENTS, Section, SectionChild,
    Statement, validate_paired_semantics,
)
from briefforge_terminal_profile.profile import (
    build_terminal_authority_profile, verify_terminal_authority_profile,
)

ROOT = Path(__file__).resolve().parents[1]
INSIGHTFORGE = Path("/home/mkkto/srv/EIP/projects/InsightForge")
SOURCE_COMMIT = "db97c30f2a79f3f1526c5c3347238f7d58be9d12"
SOURCE_SNAPSHOT = "source-snapshot:insightforge-t039:ab61ed6d7cde638ca8433e71a13480981a5a45364523d16cc9ee77b6d73da689"
SOURCE_PATH = "artifacts/fixtures/T-039-cross-inquiry-synthesis.json"
SOURCE_SHA256 = "b2e6dce194e6e489c3b5f20ad0896affb2e1175e1fecf15018a7a4e37da5501b"
SOURCE_LENGTH = 36866

BRIEF_ID = "brief:task065-cross-inquiry"
MATERIAL_ID = "material:task065-t039"
CANDIDATE_ID = "candidate:task065-cross-inquiry"
ANALYTICAL_AUTHORITY_ID = "authority:insightforge-t039-task065-analytical"
STRUCTURAL_AUTHORITY_ID = "authority:briefforge-task065-structural-presentation"
PURPOSE_BRIEF_ID = "purpose:task065-brief"
PURPOSE_CANDIDATE_ID = "purpose:task065-candidate"
AUDIENCE_BRIEF_ID = "audience:task065-brief"
AUDIENCE_CANDIDATE_ID = "audience:task065-candidate"
SNAPSHOT_ID = "snapshot:task065-t039"
EXTERNAL_SOURCE_ID = "external:insightforge-t039-task065"
UNIT_ID = "unit:task065-unitless"
SEMANTIC_TYPE_ID = "semantic-type:task065-pearson-coefficient"

LEDGER_PATH = ROOT / "artifacts/reports/R-20260801-task-064-editorial-closure-ledger.json"
TABLE_PATH = ROOT / "artifacts/reports/R-20260801-task-064-seven-row-paired-table-contract.json"
BLUEPRINT_PATH = ROOT / "artifacts/reports/R-20260801-task-064-source-to-candidate-authoring-blueprint.json"
GATE_PATH = ROOT / "artifacts/reports/R-20260801-task-064-pre-release-editorial-gate.json"
ADMISSION_PATH = ROOT / "artifacts/reports/R-20260801-task-065-source-and-contract-admission.json"
CANDIDATE_DIR = ROOT / "artifacts/pilots/task069/candidate"
STAGING_DIR = ROOT / "artifacts/pilots/task069/.candidate-staging"
MARKER = ROOT / "artifacts/pilots/task069/.candidate-authoring-single-use"
REPORT = ROOT / "artifacts/reports/R-20260808-task-069-candidate-semantic-acceptance.json"
PROFILE_OUTPUT = CANDIDATE_DIR / "candidate.profile-instance.canonical.json"
SEMANTIC_OUTPUT = CANDIDATE_DIR / "candidate.semantic.canonical.json"
FINGERPRINT_OUTPUT = CANDIDATE_DIR / "candidate.fingerprint.json"

_OUTPUTS = (PROFILE_OUTPUT, SEMANTIC_OUTPUT, FINGERPRINT_OUTPUT, REPORT)
BOUNDARY_ROOT = ROOT / "artifacts/pilots/task069/terminal-boundaries"
_OBLIGATION_KINDS = {
    "obligation:preserve-source-meaning-task065": "preserve-source-meaning",
    "obligation:display-source-task065": "source-display",
    "obligation:qualification-attachment-task065": "qualification-display",
    "obligation:display-exclusions-task065": "exclusion-display",
    "obligation:future-work-language-task065": "future-work-language",
}


def _json_bytes(value: Any, *, pretty: bool = False) -> bytes:
    options = {"ensure_ascii": False, "sort_keys": True, "allow_nan": False}
    if pretty:
        options["indent"] = 2
    else:
        options["separators"] = (",", ":")
    return json.dumps(value, **options).encode("utf-8")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if type(value) is not dict:
        raise ValueError(f"authoritative JSON root is not an object: {path}")
    return value


def load_contracts() -> tuple[dict[str, Any], ...]:
    return tuple(load_json(path) for path in (
        LEDGER_PATH, TABLE_PATH, BLUEPRINT_PATH, GATE_PATH, ADMISSION_PATH,
    ))


def _git_object(path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{SOURCE_COMMIT}:{path}"], cwd=INSIGHTFORGE,
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return completed.stdout


def _pointer(value: Any, pointer: str) -> Any:
    if pointer == "":
        return value
    if not pointer.startswith("/"):
        raise ValueError(f"not a JSON pointer: {pointer}")
    current = value
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if type(current) is dict:
            if token not in current:
                raise ValueError(f"JSON pointer does not resolve: {pointer}")
            current = current[token]
        elif type(current) is list and token.isdigit() and int(token) < len(current):
            current = current[int(token)]
        else:
            raise ValueError(f"JSON pointer does not resolve: {pointer}")
    return current


def authenticate_sources_and_locators(
    ledger: dict[str, Any], admission: dict[str, Any],
) -> dict[str, Any]:
    """Authenticate all 13 admitted Git objects and resolve all 130 locators."""
    if not INSIGHTFORGE.is_dir():
        raise ValueError("immutable InsightForge source repository is absent")
    authenticated: dict[str, bytes] = {}
    artifact_results = []
    for item in admission.get("artifacts", []):
        path = item["path"]
        raw = _git_object(path)
        digest = hashlib.sha256(raw).hexdigest()
        passed = (len(raw) == item["expected_byte_length"] and
                  digest == item["expected_sha256"])
        artifact_results.append({"path": path, "byte_length": len(raw),
                                 "sha256": digest, "passed": passed})
        if not passed:
            raise ValueError(f"admitted immutable Git object differs: {path}")
        authenticated[path] = raw
    if len(artifact_results) != 13:
        raise ValueError("source admission does not contain exactly 13 objects")
    if len(authenticated[SOURCE_PATH]) != SOURCE_LENGTH or hashlib.sha256(
            authenticated[SOURCE_PATH]).hexdigest() != SOURCE_SHA256:
        raise ValueError("T-039 source byte identity differs")

    parsed_json: dict[str, Any] = {SOURCE_PATH: json.loads(authenticated[SOURCE_PATH])}
    locator_results = []
    for ledger_item in ledger.get("items", []):
        locators = ledger_item["exact_source_locator"]
        if type(locators) is str:
            locators = [locators]
        authority = ledger_item["authoritative_source_artifact"]
        for locator in locators:
            if authority.startswith(f"InsightForge@{SOURCE_COMMIT}:"):
                path = authority.split(":", 1)[1]
                raw = authenticated.get(path)
                if raw is None:
                    raw = _git_object(path)
                    authenticated[path] = raw
                if locator.startswith("/"):
                    document = parsed_json.setdefault(path, json.loads(raw))
                    _pointer(document, locator)
                else:
                    match = re.search(r"line\s+(\d+)$", locator)
                    if match is None or not 1 <= int(match.group(1)) <= len(raw.decode("utf-8").splitlines()):
                        raise ValueError(f"source line locator does not resolve: {locator}")
            elif authority.startswith("BriefForge:"):
                path = ROOT / authority.split(":", 1)[1]
                document = load_json(path)
                _pointer(document, locator)
            else:
                raise ValueError(f"unknown ledger authority: {authority}")
            locator_results.append({"item_id": ledger_item["item_id"],
                                    "authority": authority, "locator": locator,
                                    "resolved": True})
    if len(locator_results) != 130:
        raise ValueError(f"expected 130 authoritative locators, found {len(locator_results)}")
    return {"commit": SOURCE_COMMIT, "artifact_count": 13,
            "artifacts": artifact_results, "locator_count": 130,
            "locators_resolved": True,
            "source": parsed_json[SOURCE_PATH]}


def _meaning(item: dict[str, Any]) -> str:
    """Render every ledger meaning as unambiguous, exact usable text."""
    value = item["source_authored_meaning"]
    if type(value) is str:
        return value
    label = f"[{item['item_id']}]"
    if type(value) is list:
        if not value or any(type(part) is not str for part in value):
            raise ValueError(f"non-string list meaning is not exact text: {item['item_id']}")
        return label + "\n" + "\n".join(f"- {part}" for part in value)
    if type(value) in (dict, bool):
        return f"{label} {_json_bytes(value).decode('utf-8')}"
    raise ValueError(f"unsupported ledger meaning type: {item['item_id']}")


def _ledger_by_destination(ledger: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for item in ledger["items"]:
        result.setdefault(item["intended_candidate_destination"], []).append(item)
    return result


def _composed_text(items: Iterable[dict[str, Any]]) -> str:
    return "\n\n".join(_meaning(item) for item in items)


def _ordered_statements(
    ledger: dict[str, Any], blueprint: dict[str, Any], sections: tuple[Section, ...],
) -> tuple[Statement, ...]:
    by_destination = _ledger_by_destination(ledger)
    declarations = {item["statement_id"]: item for item in
                    blueprint["statement_contract"]["ledger_statement_index"]}
    ordered_ids = tuple(child.target_ref for section in sections for child in section.children
                        if child.kind == "statement")
    if len(ordered_ids) != 76 or set(ordered_ids) != set(declarations):
        raise ValueError("TASK-064 statement composition is not exact 76-item closure")
    result = []
    for identity in ordered_ids:
        declaration = declarations[identity]
        items = by_destination.get(identity, [])
        if [item["item_id"] for item in items] != declaration["ledger_item_ids"]:
            raise ValueError(f"ledger statement consumption differs: {identity}")
        role = "caveat" if identity in blueprint["qualification_targets"] else "observation"
        classification = None
        if identity.startswith("statement:task065-row-"):
            position = int(identity.rsplit("-", 1)[1]) - 1
            relationship = blueprint["table_contract"]["cell_contract"][
                blueprint["table_contract"]["row_ids"][position]]["relationship_case"]
            classification = f"classification:{relationship}"
        result.append(Statement(identity, role, _composed_text(items),
                                ANALYTICAL_AUTHORITY_ID, classification))
    return tuple(result)


def _sections(ledger: dict[str, Any], blueprint: dict[str, Any]) -> tuple[Section, ...]:
    conditional = tuple(item["statement_id"] for item in blueprint["conditional_composition"])
    title_by_item = {item["item_id"]: _meaning(item)
                     for item in ledger["items"]}
    result = []
    for declaration in sorted(blueprint["deterministic_section_hierarchy"],
                              key=lambda item: item["order"]):
        child_ids = list(declaration["children"])
        if declaration["section_id"] == "section:task065-interpretation":
            child_ids.extend(item for item in conditional if item not in child_ids)
        if declaration["section_id"] == "section:task065-provenance-and-obligations":
            child_ids.append("obligation:future-work-language-task065")
        children = tuple(SectionChild(
            "section" if target.startswith("section:") else
            "statement" if target.startswith("statement:") else
            "table" if target.startswith("table:") else
            "provenance" if target.startswith("provenance:") else "obligation", target)
            for target in child_ids)
        title_source = declaration.get("title_source")
        title = (title_by_item[title_source] if title_source in title_by_item else
                 declaration["section_id"].split("task065-", 1)[-1].replace("-", " ").title())
        result.append(Section(declaration["section_id"], title,
                              declaration["order"], children))
    return tuple(result)


def _qualifications(blueprint: dict[str, Any]) -> tuple[QualificationEdge, ...]:
    result = []
    for source, targets in blueprint["qualification_targets"].items():
        for order, target in enumerate(targets):
            result.append(QualificationEdge(
                f"qualification:{source.split(':', 1)[1]}-{order}", "limits-target",
                source, target, order, ANALYTICAL_AUTHORITY_ID))
    return tuple(result)


def _values_and_rows(
    table_contract: dict[str, Any], blueprint: dict[str, Any],
    qualifications: tuple[QualificationEdge, ...],
) -> tuple[tuple[PairedValue, ...], tuple[PairedRow, ...]]:
    q_by_source: dict[str, list[str]] = {}
    for edge in qualifications:
        q_by_source.setdefault(edge.source_ref, []).append(edge.identity)
    provenance_by_targets = {tuple(item["targets"]): item
                             for item in blueprint["provenance_attachments"][1:]}
    values = []
    rows = []
    for order, row in enumerate(table_contract["rows"], 1):
        relationship = row["relationship_identity"]
        row_statement = f"statement:task065-row-{order:02d}"
        q_source = row["qualification_statement_ref"]
        for state_key in ("raw", "first_difference"):
            value = row[state_key]
            coefficient = int(value["exact_decimal_payload"]["coefficient"])
            values.append(PairedValue(
                value["value_id"], relationship, coefficient,
                value["exact_decimal_payload"]["scale"], value["value_state"],
                value["lexical_representation"],
                value.get("transformation_ref", value["transformation_state"]),
                value["transformation_state"], value["aligned_period"],
                value["aligned_count"], UNIT_ID, SEMANTIC_TYPE_ID,
                EXTERNAL_SOURCE_ID, ANALYTICAL_AUTHORITY_ID, value["method_ref"],
                value["package_id"],
            ))
        targets = (row_statement, row["raw"]["value_id"],
                   row["first_difference"]["value_id"])
        provenance = provenance_by_targets[targets]
        rows.append(PairedRow(
            row["row_id"], order, relationship, row["relationship_label"],
            row_statement, row["raw"]["value_id"],
            row["first_difference"]["value_id"],
            f"classification:{relationship}", f"evidence-role:{relationship}",
            tuple(q_by_source[q_source]), (provenance["provenance_id"],),
        ))
    return tuple(values), tuple(rows)


def _provenance(blueprint: dict[str, Any], rows: tuple[PairedRow, ...]) -> tuple[Provenance, ...]:
    result = []
    for position, item in enumerate(blueprint["provenance_attachments"]):
        if position == 0:
            result.append(Provenance(
                item["provenance_id"],
                f"Immutable InsightForge T-039 source snapshot at {SOURCE_COMMIT}",
                ANALYTICAL_AUTHORITY_ID, item["source_commit"], item["source_snapshot"],
                None, (), tuple(item["targets"]), "exact-targets",
                "section:task065-provenance-and-obligations"))
        else:
            row = next(row for row in rows if row.row_statement_ref == item["targets"][0])
            result.append(Provenance(
                item["provenance_id"], item["source_locator"], ANALYTICAL_AUTHORITY_ID,
                None, None, item["source_locator"], tuple(item["package_ids"]),
                tuple(item["targets"]), "exact-targets", row.identity))
    return tuple(result)


def _obligations(blueprint: dict[str, Any]) -> tuple[Obligation, ...]:
    return tuple(Obligation(
        item["obligation_id"], _OBLIGATION_KINDS[item["obligation_id"]],
        tuple(item["targets"]), ANALYTICAL_AUTHORITY_ID,
        "section:task065-provenance-and-obligations")
        for item in blueprint["obligation_attachments"])


def build_paired_semantics(
    ledger: dict[str, Any], table_contract: dict[str, Any], blueprint: dict[str, Any],
) -> PairedSemanticInput:
    """Build the exact real TASK-064 6/76/27/5/8/7/14 semantic closure."""
    sections = _sections(ledger, blueprint)
    statements = _ordered_statements(ledger, blueprint, sections)
    qualifications = _qualifications(blueprint)
    values, rows = _values_and_rows(table_contract, blueprint, qualifications)
    provenance = _provenance(blueprint, rows)
    obligations = _obligations(blueprint)
    table = PairedTable(
        table_contract["table_identity"], "statement:task065-introduction",
        tuple(item["column_id"] for item in table_contract["governed_columns"]),
        tuple(item["heading"] for item in table_contract["governed_columns"]),
        rows, ANALYTICAL_AUTHORITY_ID)
    semantics = PairedSemanticInput(
        sections, statements, table, values, qualifications, provenance, obligations,
        (SOURCE_SNAPSHOT,), (EXTERNAL_SOURCE_ID,),
        (ANALYTICAL_AUTHORITY_ID, STRUCTURAL_AUTHORITY_ID), RENDERER_REQUIREMENTS,
        tuple((row.identity, row.relationship_identity) for row in rows))
    validate_paired_semantics(semantics)
    return semantics


def content_authorities() -> list[dict[str, str]]:
    return sorted([
        {"id": ANALYTICAL_AUTHORITY_ID,
         "owner_identity": f"project:InsightForge@{SOURCE_COMMIT}",
         "role": "presentation-content-authority",
         "scope": "Admitted T-039 analytical meaning for the reserved TASK-065 identities"},
        {"id": STRUCTURAL_AUTHORITY_ID, "owner_identity": "project:BriefForge",
         "role": "presentation-content-authority",
         "scope": "TASK-064-prescribed structure, identities, ordering, and attachments only"},
    ], key=lambda item: item["id"])


def authority_inventory() -> list[dict[str, str]]:
    """Derive exact future terminal scopes through the public profile API only."""
    profile = build_terminal_authority_profile(
        destination_parent=BOUNDARY_ROOT / "delivery",
        destination_basename="task069-paired-terminal.html",
        delivery_ledger=BOUNDARY_ROOT / "delivery-ledger",
        target=DeploymentTarget("127.0.0.1", 47609, "http://127.0.0.1:47609"),
        routes=(DeploymentRouteItem("/task069-paired-terminal.html",
                                    "task069-paired-terminal.html",
                                    "text/html"),),
        deployment_ledger=BOUNDARY_ROOT / "deployment-ledger",
        verification_ledger=BOUNDARY_ROOT / "verification-ledger",
        content_authorities=tuple(content_authorities()),
    )
    verify_terminal_authority_profile(profile)
    return [dict(item) for item in profile.authorities]


def _core_values(semantics: PairedSemanticInput) -> list[dict[str, Any]]:
    result = []
    for value in semantics.values:
        result.append({
            "id": value.identity, "value_state": value.value_state,
            "payload": {"coefficient": str(value.coefficient), "scale": value.scale},
            "lexical_representation": value.lexical_representation,
            "unit_ref": value.unit_ref, "semantic_type_ref": value.semantic_type_ref,
            "source_ref": value.source_ref, "authority_ref": value.authority_ref,
            "method": value.method_ref, "transformation": value.transformation_identity,
            "transformation_state": value.transformation_state,
            "aligned_period": value.aligned_period, "aligned_count": value.aligned_count,
            "package_id": value.package_identity,
        })
    return result


def build_record_drafts(semantics: PairedSemanticInput) -> tuple[RecordDraft, RecordDraft, RecordDraft]:
    """Create narrow truthful Brief, Material, and Candidate RecordDrafts."""
    validate_paired_semantics(semantics)
    purpose = "Present admitted T-039 raw and first-difference evidence without changing its analytical meaning."
    brief = RecordDraft(BRIEF_ID, {
        "organizing_purpose": {"id": PURPOSE_BRIEF_ID, "statement": purpose},
        "audiences": [{"id": AUDIENCE_BRIEF_ID,
                       "description": "Readers assessing transformation-aware cross-inquiry evidence."}],
        "scope": "The seven admitted T-039 relationships and exact TASK-064 closure.",
        "non_scope": "No new analysis, lifecycle authority, release, projection, rendering, or publication.",
    })
    material = RecordDraft(MATERIAL_ID, {
        "authorities": authority_inventory(),
        "provenance": [{"id": item.identity, "citation": item.citation,
                        "authority_ref": item.authority_ref,
                        "target_refs": list(item.target_refs)} for item in semantics.provenance],
        "evidence_snapshots": [{"id": SNAPSHOT_ID, "version": SOURCE_COMMIT,
                                "content_fingerprint": f"sha256:{SOURCE_SHA256}"}],
        "external_references": [{"id": EXTERNAL_SOURCE_ID,
                                 "reference_kind": "immutable-git-json",
                                 "upstream_object_identity": SOURCE_PATH,
                                 "snapshot_ref": SNAPSHOT_ID,
                                 "authority_ref": ANALYTICAL_AUTHORITY_ID}],
        "units": [{"id": UNIT_ID, "description": "unitless"}],
        "semantic_types": [{"id": SEMANTIC_TYPE_ID, "description": "Pearson coefficient"}],
        "values": _core_values(semantics),
        "required_value_ids": [item.identity for item in semantics.values],
        "consistency_assertions": [], "state_validations": [],
    })
    statements = [{
        "id": item.identity, "text": item.text, "posture": item.role,
        "communication_functions": ["qualify"] if item.role == "caveat" else ["inform"],
        "attention": "supporting" if item.role == "caveat" else "primary",
        "purpose_ref": PURPOSE_CANDIDATE_ID, "authority_ref": item.authority_ref,
        "upstream_refs": [EXTERNAL_SOURCE_ID], "requires_comparison_universe": False,
    } for item in semantics.statements]
    sections = [{"id": item.identity, "title": item.title,
                 "children": [child.target_ref for child in item.children]}
                for item in semantics.sections]
    relations = [{"id": item.identity, "kind": item.kind,
                  "source_ref": item.source_ref, "target_ref": item.target_ref,
                  "authority_ref": item.authority_ref,
                  "declared_target_order": item.target_order}
                 for item in semantics.qualifications]
    obligations = [{"id": item.identity, "kind": item.kind,
                    "target_refs": list(item.target_refs),
                    "authority_ref": item.authority_ref}
                   for item in semantics.obligations]
    exhibit = {
        "id": semantics.table.identity, "kind": "fixed-static-table",
        "purpose_ref": PURPOSE_CANDIDATE_ID,
        "column_ids": list(semantics.table.column_identities),
        "headings": list(semantics.table.column_headings),
        "case_bindings": [{
            "id": row.identity, "order": row.order,
            "relationship_identity": row.relationship_identity,
            "relationship_label": row.relationship_label,
            "primary_ref": row.raw_value_ref,
            "comparison_ref": row.first_difference_value_ref,
        } for row in semantics.table.rows],
        "value_ids": [item.identity for item in semantics.values],
    }
    candidate_semantic = {
        "brief_ref": BRIEF_ID, "material_refs": [MATERIAL_ID],
        "organizing_purpose": {"id": PURPOSE_CANDIDATE_ID, "statement": purpose,
                               "brief_purpose_ref": PURPOSE_BRIEF_ID},
        "audiences": [{"id": AUDIENCE_CANDIDATE_ID,
                       "description": "Readers assessing transformation-aware cross-inquiry evidence."}],
        "scope": "The seven admitted T-039 relationships and exact TASK-064 closure.",
        "non_scope": "No new analysis, lifecycle authority, release, projection, rendering, or publication.",
        "structural_authority_ref": STRUCTURAL_AUTHORITY_ID,
        "statements": statements, "sections": sections, "obligations": obligations,
        "renderer_requirements": [], "fallbacks": [], "exhibits": [exhibit],
        "relations": relations, "comparison_universes": [], "selection_sets": [],
    }
    extension = build_paired_semantic_extension(semantics, candidate_identity=CANDIDATE_ID)
    candidate = RecordDraft(CANDIDATE_ID, candidate_semantic, [extension])
    return brief, material, candidate


def _exact_object(value: Any, fields: tuple[str, ...], label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != set(fields):
        raise ValueError(f"{label} fields differ")
    return dict(value)


def reconstruct_canonical_semantics(payload: Any) -> PairedSemanticInput:
    """Independent public-DTO decoder for the canonical extension payload."""
    if type(payload) is not str or len(payload.encode("utf-8")) > 4 * 1024 * 1024:
        raise ValueError("canonical semantics requires bounded text")
    parsed = json.loads(payload)
    if _json_bytes(parsed).decode("utf-8") != payload:
        raise ValueError("semantic payload is not canonical JSON")
    root_fields = tuple(PairedSemanticInput.__dataclass_fields__)
    root = _exact_object(parsed, root_fields, "semantic root")
    def objects(name: str, cls: type) -> tuple:
        values = root[name]
        if type(values) is not list:
            raise ValueError(f"{name} is not an array")
        return tuple(cls(**_exact_object(item, tuple(cls.__dataclass_fields__), name))
                     for item in values)
    sections = []
    if type(root["sections"]) is not list:
        raise ValueError("sections is not an array")
    for item in root["sections"]:
        data = _exact_object(item, tuple(Section.__dataclass_fields__), "section")
        if type(data["children"]) is not list:
            raise ValueError("section children is not an array")
        data["children"] = tuple(SectionChild(**_exact_object(
            child, tuple(SectionChild.__dataclass_fields__), "section child"))
            for child in data["children"])
        sections.append(Section(**data))
    table_data = _exact_object(root["table"], tuple(PairedTable.__dataclass_fields__), "table")
    rows = []
    if type(table_data["rows"]) is not list:
        raise ValueError("table rows is not an array")
    for item in table_data["rows"]:
        data = _exact_object(item, tuple(PairedRow.__dataclass_fields__), "row")
        data["qualification_refs"] = tuple(data["qualification_refs"])
        data["provenance_refs"] = tuple(data["provenance_refs"])
        rows.append(PairedRow(**data))
    table_data["rows"] = tuple(rows)
    table_data["column_identities"] = tuple(table_data["column_identities"])
    table_data["column_headings"] = tuple(table_data["column_headings"])
    provenance = []
    for item in root["provenance"]:
        data = _exact_object(item, tuple(Provenance.__dataclass_fields__), "provenance")
        data["package_identities"] = tuple(data["package_identities"])
        data["target_refs"] = tuple(data["target_refs"])
        provenance.append(Provenance(**data))
    obligations = []
    for item in root["obligations"]:
        data = _exact_object(item, tuple(Obligation.__dataclass_fields__), "obligation")
        data["target_refs"] = tuple(data["target_refs"])
        obligations.append(Obligation(**data))
    semantics = PairedSemanticInput(
        tuple(sections), objects("statements", Statement), PairedTable(**table_data),
        objects("values", PairedValue), objects("qualifications", QualificationEdge),
        tuple(provenance), tuple(obligations), tuple(root["evidence_snapshots"]),
        tuple(root["external_references"]), tuple(root["content_authorities"]),
        tuple(tuple(item) for item in root["renderer_requirements"]),
        tuple(tuple(item) for item in root["renderer_mappings"]),
    )
    return validate_paired_semantics(semantics)


def reconstruct_exact_extension(candidate: Any) -> PairedSemanticInput:
    extensions = candidate.extensions
    matches = [item for item in extensions if type(item) is dict and
               item.get("name") == "paired-semantic-input"]
    if len(matches) != 1:
        raise ValueError("exactly one paired semantic extension is required")
    extension = matches[0]
    if extension.get("target_refs") != [CANDIDATE_ID]:
        raise ValueError("paired extension is not bound to the exact Candidate")
    semantics = reconstruct_canonical_semantics(extension["payload"]["canonical_semantics"])
    rebuilt = build_paired_semantic_extension(semantics, candidate_identity=CANDIDATE_ID)
    if rebuilt != extension:
        raise ValueError("paired extension does not reconstruct exactly")
    return semantics


def semantic_traceability_report(
    semantics: PairedSemanticInput, ledger: dict[str, Any],
    table_contract: dict[str, Any], blueprint: dict[str, Any],
) -> dict[str, Any]:
    """Direct authoritative TASK-064 acceptance oracle."""
    validate_paired_semantics(semantics)
    authoritative = build_paired_semantics(ledger, table_contract, blueprint)
    statement_by = {item.identity: item for item in semantics.statements}
    values_by = {item.identity: item for item in semantics.values}
    provenance_by = {item.identity: item for item in semantics.provenance}
    obligations_by = {item.identity: item for item in semantics.obligations}
    objects = {**statement_by, **values_by}
    objects.update({item.identity: item for item in semantics.sections})
    objects.update(provenance_by)
    treatments = []
    for item in ledger["items"]:
        destination = item["intended_candidate_destination"]
        actual = objects.get(destination)
        if item["item_category"] in {"raw-result", "first-difference-result"}:
            meaning_present = actual is not None
        elif destination == "provenance:t039-source-snapshot-task065":
            meaning_present = actual is not None and actual.source_commit == SOURCE_COMMIT
        else:
            text = getattr(actual, "text", getattr(actual, "title", ""))
            meaning_present = actual is not None and _meaning(item) in text
        obligation_ok = all(destination in obligations_by[ref].target_refs
                            for ref in item["obligation_attachments"])
        provenance_ok = all(destination in provenance_by[ref].target_refs
                            for ref in item["provenance_attachments"])
        treatments.append({"item_id": item["item_id"], "destination": destination,
                           "meaning_present": meaning_present,
                           "obligations_attached": obligation_ok,
                           "provenance_attached": provenance_ok,
                           "passed": meaning_present and obligation_ok and provenance_ok})
    rows = semantics.table.rows
    row_results = []
    for actual, expected in zip(rows, table_contract["rows"], strict=True):
        raw = values_by[actual.raw_value_ref]
        diff = values_by[actual.first_difference_value_ref]
        expected_values = (expected["raw"], expected["first_difference"])
        actual_values = (raw, diff)
        values_exact = all(
            value.identity == contract["value_id"] and
            value.lexical_representation == contract["lexical_representation"] and
            value.coefficient == int(contract["exact_decimal_payload"]["coefficient"]) and
            value.scale == contract["exact_decimal_payload"]["scale"] and
            value.aligned_period == contract["aligned_period"] and
            value.aligned_count == contract["aligned_count"] and
            value.value_state == contract["value_state"] and
            value.package_identity == contract["package_id"] and
            value.relationship_identity == expected["relationship_identity"] and
            value.transformation_identity == contract.get(
                "transformation_ref", contract["transformation_state"]) and
            value.transformation_state == contract["transformation_state"] and
            value.unit_ref == UNIT_ID and value.semantic_type_ref == SEMANTIC_TYPE_ID and
            value.source_ref == EXTERNAL_SOURCE_ID and
            value.authority_ref == ANALYTICAL_AUTHORITY_ID and
            value.method_ref == contract["method_ref"]
            for value, contract in zip(actual_values, expected_values, strict=True))
        row_results.append({"row": actual.identity, "passed":
            actual.identity == expected["row_id"] and
            actual.order == len(row_results) + 1 and
            actual.relationship_identity == expected["relationship_identity"] and
            actual.relationship_label == expected["relationship_label"] and
            actual.row_statement_ref == f"statement:task065-row-{len(row_results)+1:02d}" and
            actual.classification_ref == f"classification:{expected['relationship_identity']}" and
            actual.evidence_role_ref == f"evidence-role:{expected['relationship_identity']}" and
            values_exact})
    topology = {
        "sections": len(semantics.sections), "statements": len(semantics.statements),
        "qualifications": len(semantics.qualifications),
        "obligations": len(semantics.obligations), "provenance": len(semantics.provenance),
        "rows": len(rows), "values": len(semantics.values),
        "columns": len(semantics.table.column_identities),
    }
    expected_topology = {"sections": 6, "statements": 76, "qualifications": 27,
                         "obligations": 5, "provenance": 8, "rows": 7,
                         "values": 14, "columns": 5}
    statement_order = tuple(item.identity for item in semantics.statements)
    ledger_by_destination = _ledger_by_destination(ledger)
    declaration_by_id = {item["statement_id"]: item for item in
                         blueprint["statement_contract"]["ledger_statement_index"]}
    exact_statement_contract = all(
        item.identity in declaration_by_id and
        [entry["item_id"] for entry in ledger_by_destination[item.identity]] ==
            declaration_by_id[item.identity]["ledger_item_ids"] and
        item.text == _composed_text(ledger_by_destination[item.identity])
        for item in semantics.statements)
    authoritative_hierarchy = tuple(
        (section.identity, section.order, tuple((child.kind, child.target_ref)
                                                for child in section.children))
        for section in authoritative.sections)
    actual_hierarchy = tuple(
        (section.identity, section.order, tuple((child.kind, child.target_ref)
                                                for child in section.children))
        for section in semantics.sections)
    expected_order = tuple(item.identity for item in authoritative.statements)
    exact_authoritative_semantics = semantics == authoritative
    passed = (topology == expected_topology and statement_order == expected_order and
              actual_hierarchy == authoritative_hierarchy and exact_authoritative_semantics and
              exact_statement_contract and
              len(treatments) == 109 and all(item["passed"] for item in treatments) and
              len(row_results) == 7 and all(item["passed"] for item in row_results))
    return {"passed": passed, "topology": topology,
            "expected_topology": expected_topology,
            "ledger_treatments": treatments, "row_results": row_results,
            "exact_statement_ledger_composition": exact_statement_contract,
            "exact_authoritative_semantics": exact_authoritative_semantics}


def draft_stage_report(drafts: tuple[RecordDraft, ...]) -> dict[str, Any]:
    """Inspect actual drafts for closed Candidate-stage negative assertions."""
    expected_ids = (BRIEF_ID, MATERIAL_ID, CANDIDATE_ID)
    exact_records = len(drafts) == 3 and tuple(item.identity for item in drafts) == expected_ids
    extensions = [item for draft in drafts for item in draft.extensions]
    lifecycle_extension_names = [item.get("name") for item in extensions
                                 if item.get("name") != "paired-semantic-input"]
    forbidden_keys = {"lifecycle_state", "release_ref", "plan_ref", "publication_state",
                      "renderer_invocation", "projector_invocation"}
    def present_keys(value: Any) -> set[str]:
        if type(value) is dict:
            return (set(value) & forbidden_keys) | set().union(
                *(present_keys(item) for item in value.values()), set())
        if type(value) is list:
            return set().union(*(present_keys(item) for item in value), set())
        return set()
    indicators = sorted(set().union(*(present_keys(draft.semantic) for draft in drafts)))
    return {"passed": exact_records and len(extensions) == 1
            and not lifecycle_extension_names and not indicators,
            "record_count": len(drafts), "record_identities": [item.identity for item in drafts],
            "extension_count": len(extensions),
            "lifecycle_extension_names": lifecycle_extension_names,
            "forbidden_state_or_invocation_keys": indicators}


def validate_persisted_canonical_bytes(
    profile_bytes: bytes, semantic_bytes: bytes, ledger: dict[str, Any],
    table_contract: dict[str, Any], blueprint: dict[str, Any],
) -> dict[str, Any]:
    """Independently validate persisted canonical bytes and embedded traceability."""
    profile = profile_bytes.rstrip(b"\n")
    semantic = semantic_bytes.rstrip(b"\n")
    bundle = bundle_from_canonical_json(profile)
    record_kinds = tuple(item.kind for item in bundle.records)
    expected_kinds = ("PresentationBriefRecord", "PortablePresentationMaterialRecord",
                      "CandidatePresentationPackageRecord")
    if (len(record_kinds) != 3 or
            {kind: record_kinds.count(kind) for kind in expected_kinds} !=
            {kind: 1 for kind in expected_kinds}):
        raise ValueError("returned bundle is not exactly the three Candidate-stage records")
    candidate = bundle.one("CandidatePresentationPackageRecord")
    non_candidates = tuple(item for item in bundle.records
                           if item.kind != "CandidatePresentationPackageRecord")
    if any(item.extensions for item in non_candidates) or len(candidate.extensions) != 1:
        raise ValueError("returned bundle contains unexpected or lifecycle extensions")
    if canonical_json_bytes(bundle, domain="profile-instance", require_valid=True) != profile:
        raise ValueError("profile-instance canonical bytes do not round trip")
    if canonical_json_bytes(bundle, domain="candidate-semantic", require_valid=True) != semantic:
        raise ValueError("candidate-semantic canonical bytes do not bind profile bytes")
    semantics = reconstruct_exact_extension(candidate)
    report = semantic_traceability_report(semantics, ledger, table_contract, blueprint)
    report["profile_sha256"] = hashlib.sha256(profile).hexdigest()
    report["candidate_semantic_sha256"] = hashlib.sha256(semantic).hexdigest()
    report["technical_validation_passed"] = not validate_bundle(
        bundle, through_layer="L2").blocking
    report["candidate_stage_record_kinds"] = list(record_kinds)
    report["lifecycle_records_or_extensions_present"] = False
    report["passed"] = report["passed"] and report["technical_validation_passed"]
    return report


def preflight(
    ledger: dict[str, Any], table_contract: dict[str, Any], blueprint: dict[str, Any],
    gate: dict[str, Any], admission: dict[str, Any], *, authenticate_source: bool = True,
) -> dict[str, Any]:
    """Complete every fallible construction/validation check before the attempt."""
    if (ledger.get("item_count"), ledger.get("mandatory_item_count"),
            ledger.get("conditional_item_count"), ledger.get("excluded_item_count")) != (109, 104, 2, 3):
        raise ValueError("TASK-064 ledger cardinality differs")
    if (table_contract.get("table_count"), table_contract.get("column_count"),
            table_contract.get("row_count"), table_contract.get("coefficient_count")) != (1, 5, 7, 14):
        raise ValueError("TASK-064 paired table cardinality differs")
    if gate.get("fail_closed") is not True or blueprint.get("candidate_creation_authorized") is not False:
        raise ValueError("TASK-064 authority/gate contract differs")
    source_report = authenticate_sources_and_locators(ledger, admission) if authenticate_source else {
        "not_executed": True}
    semantics = build_paired_semantics(ledger, table_contract, blueprint)
    drafts = build_record_drafts(semantics)
    reconstructed = reconstruct_exact_extension(drafts[2])
    if reconstructed != semantics:
        raise ValueError("paired semantic extension reconstruction differs")
    traceability = semantic_traceability_report(
        reconstructed, ledger, table_contract, blueprint)
    if not traceability["passed"]:
        raise ValueError("independent semantic/traceability preflight blocked")
    stage = draft_stage_report(drafts)
    if not stage["passed"]:
        raise ValueError("Candidate-stage negative preflight blocked")
    return {"source_authentication": source_report, "semantics": semantics,
            "drafts": drafts, "traceability": traceability, "stage": stage}


def create_staging_directory() -> None:
    """Exclusively stage a whole Candidate directory; never create final outputs."""
    if CANDIDATE_DIR.exists() or REPORT.exists():
        raise FileExistsError("final TASK-069 evidence already exists")
    CANDIDATE_DIR.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    STAGING_DIR.mkdir(mode=0o700, exist_ok=False)


def _atomic_write(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


def persist_candidate_directory(profile: bytes, semantic: bytes, fingerprint: bytes) -> None:
    """Fsync staged evidence, then publish the complete directory in one rename."""
    for name, data in ((PROFILE_OUTPUT.name, profile), (SEMANTIC_OUTPUT.name, semantic),
                       (FINGERPRINT_OUTPUT.name, fingerprint)):
        path = STAGING_DIR / name
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        try:
            view = memoryview(data)
            while view:
                written = os.write(fd, view)
                if written <= 0:
                    raise OSError("staged evidence write made no progress")
                view = view[written:]
            os.fsync(fd)
        finally:
            os.close(fd)
    staging_fd = os.open(STAGING_DIR, os.O_RDONLY | os.O_DIRECTORY)
    parent_fd = os.open(CANDIDATE_DIR.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(staging_fd)
        os.rename(STAGING_DIR, CANDIDATE_DIR)
        os.fsync(parent_fd)
    finally:
        os.close(staging_fd)
        os.close(parent_fd)


def _marker_payload() -> bytes:
    return _json_bytes({
        "schema": "briefforge-task069-candidate-authoring-single-use:1.0.0",
        "task_id": "TASK-069", "candidate_identity": CANDIDATE_ID,
        "rule": "Presence permanently consumes the sole TASK-069 Candidate authoring attempt.",
    }) + b"\n"


def _consume_attempt_and_author(
    brief: RecordDraft, material: RecordDraft, candidate: RecordDraft,
    marker_payload: bytes,
) -> BCRPBundle:
    """Durably account the attempt, then cross exactly one production call boundary."""
    parent_fd = os.open(MARKER.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        fd = os.open(MARKER, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    except BaseException:
        with suppress(OSError):
            os.close(parent_fd)
        raise
    try:
        view = memoryview(marker_payload)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise OSError("attempt marker write made no progress")
            view = view[written:]
        os.fsync(fd)
        os.fsync(parent_fd)
    except BaseException:
        with suppress(OSError):
            os.close(fd)
        with suppress(OSError):
            MARKER.unlink()
        with suppress(OSError):
            os.close(parent_fd)
        raise
    try:
        return _task069_author_once(brief=brief, material=material, candidate=candidate)
    finally:
        with suppress(OSError):
            os.close(fd)
        with suppress(OSError):
            os.close(parent_fd)


def _fingerprint_document(bundle: BCRPBundle) -> dict[str, Any]:
    fingerprint = fingerprint_bundle(bundle, domain="candidate-semantic", require_valid=True)
    return {name: getattr(fingerprint, name) for name in (
        "algorithm", "canonicalization", "digest", "domain", "profile_identity",
        "profile_version", "root_identity", "scope")}


def _report_base() -> dict[str, Any]:
    return {"schema": "briefforge-task069-candidate-semantic-acceptance:1.0.0",
            "task_id": "TASK-069", "candidate_identity": CANDIDATE_ID,
            "attempt_consumed": MARKER.exists(), "authoring_call_count": 0,
            "candidate_created": False, "candidate_persisted": False,
            "status": "BLOCKED", "blocking_findings": []}


def main() -> int:
    """Execute the separately governed one-shot operation.  Do not use for tests."""
    if MARKER.exists():
        raise SystemExit("TASK-069 attempt is already permanently consumed")
    ledger, table_contract, blueprint, gate, admission = load_contracts()
    prepared = preflight(ledger, table_contract, blueprint, gate, admission)
    create_staging_directory()
    report = _report_base()
    source = prepared["source_authentication"]
    report["preflight"] = {
        "status": "PASS",
        "source_commit": source["commit"],
        "authenticated_source_objects": source["artifact_count"],
        "resolved_task064_locators": source["locator_count"],
        "topology": prepared["traceability"]["topology"],
        "draft_stage_inspection": prepared["stage"],
        "extension_reconstructed_exactly": True,
        "canonical_bytes_independently_validated": False,
    }
    marker_payload = _marker_payload()
    brief, material, candidate = prepared["drafts"]
    try:
        bundle = _consume_attempt_and_author(brief, material, candidate, marker_payload)
        report["attempt_consumed"] = True
        report["authoring_call_count"] = 1
        report["candidate_created"] = True
        profile = canonical_json_bytes(bundle, domain="profile-instance", require_valid=True)
        semantic = canonical_json_bytes(bundle, domain="candidate-semantic", require_valid=True)
        fingerprint = _fingerprint_document(bundle)
        acceptance = validate_persisted_canonical_bytes(
            profile, semantic, ledger, table_contract, blueprint)
        report["acceptance"] = acceptance
        report["fingerprint"] = fingerprint
        report["candidate_evidence"] = {
            "profile_instance_path": str(PROFILE_OUTPUT),
            "profile_instance_sha256": hashlib.sha256(profile).hexdigest(),
            "candidate_semantic_path": str(SEMANTIC_OUTPUT),
            "candidate_semantic_sha256": hashlib.sha256(semantic).hexdigest(),
            "fingerprint_path": str(FINGERPRINT_OUTPUT),
        }
        persist_candidate_directory(
            profile, semantic, _json_bytes(fingerprint, pretty=True) + b"\n")
        report["candidate_persisted"] = True
        report["status"] = "PASS" if acceptance["passed"] else "BLOCKED"
    except BaseException as exc:
        report["attempt_consumed"] = MARKER.exists()
        # Marker durability is immediately adjacent to the call expression, so
        # its presence accounts the one call boundary even when that call raises.
        report["authoring_call_count"] = 1 if MARKER.exists() else 0
        report["authoring_call_attempted"] = MARKER.exists()
        report["blocking_findings"].append({"type": type(exc).__name__, "message": str(exc)})
    _atomic_write(REPORT, _json_bytes(report, pretty=True) + b"\n")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
