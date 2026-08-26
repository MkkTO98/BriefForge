#!/usr/bin/env python3
"""REJECTED, UNEXECUTED investigative draft for TASK-065.

Do not run this file. Independent review proved that it cannot preserve the
TASK-064 contract through the accepted TASK-062 profile. It would also consume
its single-use marker before using the wrong non-Git cwd for ``git show``.
It is retained only as truthful evidence of the discovered pre-authoring gap.

This task-local program intentionally stops at Candidate evidence.  It contains no
promotion, Judgment, Ready, Release, projection, renderer, manifest, delivery, or
deployment operation.  The caller supplies PYTHONDONTWRITEBYTECODE=1.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable

from briefforge.bcrp import RecordDraft, author_candidate_bundle
from briefforge.bcrp.canonical import canonical_json_bytes, fingerprint_bundle
from briefforge.bcrp.validation import validate_bundle
from briefforge_terminal_profile.profile import (
    TERMINAL_OPERATIONAL_IDENTITIES,
    TERMINAL_OPERATIONAL_ROLES,
)

ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / "artifacts/pilots/task065"
CANDIDATE_DIR = PILOT / "candidate"
REPORT = ROOT / "artifacts/reports/R-20260801-task-065-candidate-pre-promotion-gate.json"
MARKER = PILOT / ".candidate-authoring-single-use"
SOURCE_COMMIT = "db97c30f2a79f3f1526c5c3347238f7d58be9d12"
SOURCE_PATH = "artifacts/fixtures/T-039-cross-inquiry-synthesis.json"
SOURCE_SHA256 = "b2e6dce194e6e489c3b5f20ad0896affb2e1175e1fecf15018a7a4e37da5501b"
SOURCE_LENGTH = 36866
SNAPSHOT_ID = "source-snapshot:insightforge-t039:ab61ed6d7cde638ca8433e71a13480981a5a45364523d16cc9ee77b6d73da689"

LEDGER_PATH = ROOT / "artifacts/reports/R-20260801-task-064-editorial-closure-ledger.json"
TABLE_PATH = ROOT / "artifacts/reports/R-20260801-task-064-seven-row-paired-table-contract.json"
BLUEPRINT_PATH = ROOT / "artifacts/reports/R-20260801-task-064-source-to-candidate-authoring-blueprint.json"
GATE_PATH = ROOT / "artifacts/reports/R-20260801-task-064-pre-release-editorial-gate.json"
ADMISSION_PATH = ROOT / "artifacts/reports/R-20260801-task-065-source-and-contract-admission.json"

ANALYTICAL_AUTHORITY_ID = "authority:insightforge-t039-task065-analytical"
STRUCTURAL_AUTHORITY_ID = "authority:briefforge-task065-structural-presentation"
BRIEF_ID = "brief:task065-cross-inquiry"
MATERIAL_ID = "material:task065-t039"
CANDIDATE_ID = "candidate:task065-cross-inquiry"
PURPOSE_BRIEF_ID = "purpose:task065-brief"
PURPOSE_CANDIDATE_ID = "purpose:task065-candidate"
AUDIENCE_BRIEF_ID = "audience:task065-brief"
AUDIENCE_CANDIDATE_ID = "audience:task065-candidate"
EXTERNAL_SOURCE_ID = "external:insightforge-t039-task065"
UNIT_ID = "unit:task065-unitless"
SEMANTIC_TYPE_ID = "semantic-type:task065-pearson-coefficient"

# TASK-062's closed order and roles.  The final three scopes are deliberately
# bounded to this task's not-yet-authorized future terminal locations.  They are
# authority inventory only and are excluded from every displayed field.
_OPERATIONAL_SCOPES = (
    "BCRP-L0-L6",
    "fixed-evidence-publication-release",
    "one-controlled-renderer-invocation-act",
    "one-semantic-artifact-conformance-assessment",
    "one-publication-manifest-production",
    "task065-controlled-local-delivery-not-authorized",
    "task065-bounded-loopback-deployment-not-authorized",
    "task065-technical-publication-verification-not-authorized",
)


def canonical_object(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def meaning_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    return canonical_object(value).decode("utf-8")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if type(value) is not dict:
        raise ValueError(f"authoritative input is not an object: {path}")
    return value


def exclusive_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise


def persist_report(report: dict[str, Any]) -> None:
    data = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False).encode("utf-8") + b"\n"
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    temporary = REPORT.with_name(f".{REPORT.name}.{os.getpid()}.tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, REPORT)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def initial_report() -> dict[str, Any]:
    return {
        "schema": "briefforge-task065-candidate-pre-promotion-gate:1.0.0",
        "task_id": "TASK-065",
        "gate_position": "after-Candidate-before-any-promotion",
        "candidate_created": False,
        "candidate_persisted": False,
        "promotion_attempted": False,
        "release_or_renderer_code_present": False,
        "status": "BLOCKED",
        "blocking_findings": [],
        "checks": [],
        "ledger_treatments": [],
        "table_invariants": [],
    }


def check(report: dict[str, Any], identity: str, passed: bool, expected: Any, actual: Any) -> None:
    item = {"check": identity, "passed": bool(passed), "expected": expected, "actual": actual}
    report["checks"].append(item)
    if not passed:
        report["blocking_findings"].append(item)


def create_single_use_marker() -> None:
    payload = canonical_object({
        "schema": "briefforge-task065-candidate-authoring-single-use:1.0.0",
        "task_id": "TASK-065",
        "candidate_identity": CANDIDATE_ID,
        "rule": "Presence permanently consumes the sole TASK-065 Candidate authoring attempt.",
    }) + b"\n"
    exclusive_bytes(MARKER, payload)


def load_source_at_commit() -> tuple[dict[str, Any], bytes]:
    completed = subprocess.run(
        ["git", "show", f"{SOURCE_COMMIT}:{SOURCE_PATH}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    raw = completed.stdout
    if len(raw) != SOURCE_LENGTH or hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("immutable T-039 git object does not match admitted byte identity")
    source = json.loads(raw)
    if type(source) is not dict:
        raise ValueError("immutable T-039 JSON root is not an object")
    return source, raw


def scalar_inventory(value: Any) -> list[Any]:
    result: list[Any] = []
    if isinstance(value, dict):
        for child in value.values():
            result.extend(scalar_inventory(child))
    elif isinstance(value, list):
        for child in value:
            result.extend(scalar_inventory(child))
    elif value is not None and not isinstance(value, float):
        result.append(value)
    return result


def verify_authoritative_inputs(
    report: dict[str, Any], ledger: dict[str, Any], table: dict[str, Any],
    blueprint: dict[str, Any], gate: dict[str, Any], admission: dict[str, Any], source: dict[str, Any],
) -> None:
    check(report, "source-commit", ledger.get("source_commit") == SOURCE_COMMIT, SOURCE_COMMIT, ledger.get("source_commit"))
    check(report, "source-snapshot", ledger.get("source_snapshot_identity") == SNAPSHOT_ID, SNAPSHOT_ID, ledger.get("source_snapshot_identity"))
    check(report, "admission-pass", admission.get("status") == "PASS" and admission.get("candidate_authoring_permitted") is True, "PASS/permitted", [admission.get("status"), admission.get("candidate_authoring_permitted")])
    check(report, "ledger-cardinality", (ledger.get("item_count"), ledger.get("mandatory_item_count"), ledger.get("conditional_item_count"), ledger.get("excluded_item_count")) == (109, 104, 2, 3), [109, 104, 2, 3], [ledger.get("item_count"), ledger.get("mandatory_item_count"), ledger.get("conditional_item_count"), ledger.get("excluded_item_count")])
    check(report, "table-shape-contract", (table.get("table_count"), table.get("column_count"), table.get("row_count"), table.get("coefficient_count")) == (1, 5, 7, 14), [1, 5, 7, 14], [table.get("table_count"), table.get("column_count"), table.get("row_count"), table.get("coefficient_count")])
    check(report, "blueprint-not-candidate", blueprint.get("candidate_creation_authorized") is False, False, blueprint.get("candidate_creation_authorized"))
    check(report, "gate-fail-closed", gate.get("fail_closed") is True, True, gate.get("fail_closed"))
    expected_resolutions = [(x["ledger_item_id"], x["statement_id"]) for x in blueprint["conditional_composition"]]
    actual_resolutions = [(x["ledger_item_id"], x["statement_id"]) for x in admission["conditional_resolutions"] if x.get("resolution") == "included-by-exact-composition-rule"]
    check(report, "conditional-composition-resolution", actual_resolutions == expected_resolutions, expected_resolutions, actual_resolutions)
    source_cases = source.get("cases", [])
    check(report, "immutable-source-seven-cases", type(source_cases) is list and len(source_cases) == 7, 7, len(source_cases) if isinstance(source_cases, list) else type(source_cases).__name__)
    if isinstance(source_cases, list) and len(source_cases) == 7:
        source_rows = []
        for position, (case, row) in enumerate(zip(source_cases, table["rows"], strict=True), 1):
            inventory = scalar_inventory(case)
            required = [
                row["relationship_identity"], row["relationship_label"], row["classification"],
                row["source_inclusion_role"], row["raw"]["lexical_representation"],
                row["first_difference"]["lexical_representation"], row["raw"]["package_id"],
                row["first_difference"]["package_id"], row["raw"]["aligned_period"],
                row["first_difference"]["aligned_period"], row["raw"]["aligned_count"],
                row["first_difference"]["aligned_count"],
            ]
            missing = [item for item in required if item not in inventory]
            source_rows.append({"position": position, "relationship": row["relationship_identity"], "missing_exact_source_scalars": missing, "passed": not missing})
        check(report, "table-contract-values-occur-in-immutable-source", all(x["passed"] for x in source_rows), "all exact row scalars present in same immutable case", source_rows)


def operational_authorities() -> list[dict[str, str]]:
    return [
        {"id": identity, "owner_identity": "project:BriefForge", "role": role, "scope": scope}
        for identity, role, scope in zip(
            TERMINAL_OPERATIONAL_IDENTITIES, TERMINAL_OPERATIONAL_ROLES, _OPERATIONAL_SCOPES, strict=True
        )
    ]


def content_authorities() -> list[dict[str, str]]:
    return [
        {"id": ANALYTICAL_AUTHORITY_ID, "owner_identity": f"project:InsightForge@{SOURCE_COMMIT}", "role": "presentation-content-authority", "scope": "T-039 admitted analytical meaning for TASK-065 only"},
        {"id": STRUCTURAL_AUTHORITY_ID, "owner_identity": "project:BriefForge", "role": "presentation-content-authority", "scope": "TASK-065 presentation structure, identities, ordering, and attachments only"},
    ]


def ledger_by_destination(ledger: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for item in ledger["items"]:
        result.setdefault(item["intended_candidate_destination"], []).append(item)
    return result


def composed_text(items: Iterable[dict[str, Any]]) -> str:
    # Multiple links share a destination only where TASK-064's exact statement
    # index says that identity consumes them together.  Every complete meaning is
    # retained in ledger encounter order; no free editorial compression occurs.
    return "\n\n".join(meaning_text(item["source_authored_meaning"]) for item in items)


def statement_posture(item_ids: set[str]) -> str:
    if any("qualification:" in item or "no-" in item or "exclude-" in item or "boundary" in item or "limited" in item for item in item_ids):
        return "caveat"
    return "observation"


def build_statements(ledger: dict[str, Any], blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    by_destination = ledger_by_destination(ledger)
    statements: list[dict[str, Any]] = []
    for declaration in blueprint["statement_contract"]["ledger_statement_index"]:
        identity = declaration["statement_id"]
        items = by_destination.get(identity, [])
        declared_ids = declaration["ledger_item_ids"]
        if [x["item_id"] for x in items] != declared_ids:
            raise ValueError(f"ledger encounter order/content differs from statement contract for {identity}")
        item_ids = set(declared_ids)
        statement = {
            "id": identity,
            "text": composed_text(items),
            "posture": statement_posture(item_ids),
            "communication_functions": ["qualify"] if statement_posture(item_ids) == "caveat" else ["inform"],
            "attention": "supporting" if statement_posture(item_ids) == "caveat" else "primary",
            "purpose_ref": PURPOSE_CANDIDATE_ID,
            "authority_ref": ANALYTICAL_AUTHORITY_ID,
            "upstream_refs": [EXTERNAL_SOURCE_ID],
            "requires_comparison_universe": False,
            "ledger_item_ids": declared_ids,
        }
        if identity.startswith("statement:task065-row-"):
            row = next(x for x in blueprint["statement_contract"]["row_statements"] if x["statement_id"] == identity)
            statement["value_ids"] = list(row["value_refs"])
            statement["table_row_ref"] = row["table_row_ref"]
            statement["qualification_ref"] = row["qualification_ref"]
            statement["provenance_ref"] = row["provenance_ref"]
        statements.append(statement)
    return statements


def build_sections(blueprint: dict[str, Any], conditional_ids: set[str]) -> list[dict[str, Any]]:
    result = []
    for declaration in sorted(blueprint["deterministic_section_hierarchy"], key=lambda x: x["order"]):
        children = list(declaration["children"])
        if declaration["section_id"] == "section:task065-interpretation":
            for conditional in blueprint["conditional_composition"]:
                if conditional["statement_id"] in conditional_ids:
                    children.append(conditional["statement_id"])
        title = ""
        if declaration["section_id"] == "section:task065-root":
            title = next(x for x in blueprint["ledger_destination_index"] if x["ledger_item_id"] == "closure:title")["ledger_item_id"]
        else:
            title = declaration["section_id"].split("task065-", 1)[-1].replace("-", " ").title()
        result.append({"id": declaration["section_id"], "title": title, "children": children})
    return result


def build_values(table: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for row in table["rows"]:
        for key in ("raw", "first_difference"):
            source_value = row[key]
            result.append({
                "id": source_value["value_id"],
                "value_state": source_value["value_state"],
                "payload": deepcopy(source_value["exact_decimal_payload"]),
                "lexical_representation": source_value["lexical_representation"],
                "unit_ref": UNIT_ID,
                "semantic_type_ref": SEMANTIC_TYPE_ID,
                "source_ref": EXTERNAL_SOURCE_ID,
                "authority_ref": ANALYTICAL_AUTHORITY_ID,
                "method": source_value["method_ref"],
                "transformation": source_value.get("transformation_ref", "none"),
                "transformation_state": source_value["transformation_state"],
                "aligned_period": source_value["aligned_period"],
                "aligned_count": source_value["aligned_count"],
                "package_id": source_value["package_id"],
            })
    return result


def build_provenance(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for declaration in blueprint["provenance_attachments"]:
        item = {
            "id": declaration["provenance_id"],
            "citation": declaration.get("source_locator", f"InsightForge immutable T-039 snapshot at {SOURCE_COMMIT}"),
            "authority_ref": ANALYTICAL_AUTHORITY_ID,
            "target_refs": list(declaration["targets"]),
        }
        if "source_commit" in declaration:
            item["source_commit"] = declaration["source_commit"]
            item["source_snapshot"] = declaration["source_snapshot"]
        if "package_ids" in declaration:
            item["package_ids"] = list(declaration["package_ids"])
        result.append(item)
    return result


def build_relations(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for source, targets in blueprint["qualification_targets"].items():
        for index, target in enumerate(targets, 1):
            result.append({
                "id": f"relation:task065-qualification-{len(result)+1:02d}",
                "kind": "limits-target",
                "source_ref": source,
                "target_ref": target,
                "authority_ref": ANALYTICAL_AUTHORITY_ID,
                "declared_target_order": index,
            })
    return result


def build_obligations(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    kinds = {
        "obligation:preserve-source-meaning-task065": "preserve-source-meaning",
        "obligation:display-source-task065": "source-display",
        "obligation:qualification-attachment-task065": "qualification-display",
        "obligation:display-exclusions-task065": "exclusion-display",
        "obligation:future-work-language-task065": "future-work-language",
    }
    return [
        {"id": x["obligation_id"], "kind": kinds[x["obligation_id"]], "authority_ref": ANALYTICAL_AUTHORITY_ID, "target_refs": list(x["targets"])}
        for x in blueprint["obligation_attachments"]
    ]


def build_exhibit(table: dict[str, Any]) -> dict[str, Any]:
    bindings = []
    for row in table["rows"]:
        bindings.append({
            "id": row["row_id"],
            "order": row["row_order"],
            "relationship_identity": row["relationship_identity"],
            "relationship_label": row["relationship_label"],
            "primary_ref": row["raw"]["value_id"],
            "comparison_ref": row["first_difference"]["value_id"],
            "raw_state": {"transformation_state": row["raw"]["transformation_state"], "period": row["raw"]["aligned_period"], "aligned_count": row["raw"]["aligned_count"]},
            "first_difference_state": {"transformation_state": row["first_difference"]["transformation_state"], "period": row["first_difference"]["aligned_period"], "aligned_count": row["first_difference"]["aligned_count"]},
        })
    return {
        "id": table["table_identity"],
        "kind": table["table_kind"],
        "purpose_ref": PURPOSE_CANDIDATE_ID,
        "column_ids": [x["column_id"] for x in table["governed_columns"]],
        "headings": [x["heading"] for x in table["governed_columns"]],
        "case_bindings": bindings,
        "value_ids": [value for row in table["rows"] for value in (row["raw"]["value_id"], row["first_difference"]["value_id"])],
    }


def author(ledger: dict[str, Any], table: dict[str, Any], blueprint: dict[str, Any]) -> Any:
    purpose = "Present the admitted T-039 raw-level and first-difference comparison without changing analytical meaning."
    brief = RecordDraft(BRIEF_ID, {
        "organizing_purpose": {"id": PURPOSE_BRIEF_ID, "statement": purpose},
        "audiences": [{"id": AUDIENCE_BRIEF_ID, "description": "Readers assessing transformation-aware cross-inquiry evidence."}],
        "scope": "Exactly the admitted seven T-039 relationships and TASK-064 closure contract.",
        "non_scope": "No new result, relationship, method, inference, recommendation, promotion, or publication.",
    })
    material = RecordDraft(MATERIAL_ID, {
        "authorities": operational_authorities() + content_authorities(),
        "provenance": build_provenance(blueprint),
        "evidence_snapshots": [{"id": "snapshot:task065-t039", "version": SOURCE_COMMIT, "content_fingerprint": f"sha256:{SOURCE_SHA256}", "provenance_ref": "provenance:t039-source-snapshot-task065"}],
        "external_references": [{"id": EXTERNAL_SOURCE_ID, "reference_kind": "immutable-git-json", "upstream_object_identity": SOURCE_PATH, "snapshot_ref": "snapshot:task065-t039", "provenance_ref": "provenance:t039-source-snapshot-task065", "authority_ref": ANALYTICAL_AUTHORITY_ID}],
        "units": [{"id": UNIT_ID, "description": "unitless"}],
        "semantic_types": [{"id": SEMANTIC_TYPE_ID, "description": "Pearson coefficient"}],
        "values": build_values(table),
        "required_value_ids": [value for row in table["rows"] for value in (row["raw"]["value_id"], row["first_difference"]["value_id"])],
        "consistency_assertions": [],
        "state_validations": [],
    })
    conditional_ids = {x["statement_id"] for x in blueprint["conditional_composition"]}
    statements = build_statements(ledger, blueprint)
    root_title = next(x["source_authored_meaning"] for x in ledger["items"] if x["item_id"] == "closure:title")
    sections = build_sections(blueprint, conditional_ids)
    next(x for x in sections if x["id"] == "section:task065-root")["title"] = root_title
    candidate = RecordDraft(CANDIDATE_ID, {
        "brief_ref": BRIEF_ID,
        "material_refs": [MATERIAL_ID],
        "organizing_purpose": {"id": PURPOSE_CANDIDATE_ID, "statement": purpose, "brief_purpose_ref": PURPOSE_BRIEF_ID},
        "audiences": [{"id": AUDIENCE_CANDIDATE_ID, "description": "Readers assessing transformation-aware cross-inquiry evidence."}],
        "scope": "Exactly the admitted seven T-039 relationships and TASK-064 closure contract.",
        "non_scope": "No new result, relationship, method, inference, recommendation, promotion, or publication.",
        "structural_authority_ref": STRUCTURAL_AUTHORITY_ID,
        "statements": statements,
        "sections": sections,
        "obligations": build_obligations(blueprint),
        "renderer_requirements": [],
        "fallbacks": [],
        "exhibits": [build_exhibit(table)],
        "relations": build_relations(blueprint),
        "comparison_universes": [],
        "selection_sets": [],
    })
    return author_candidate_bundle(brief=brief, material=material, candidate=candidate)


def nested_id_map(value: Any) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    def visit(child: Any) -> None:
        if isinstance(child, dict):
            if isinstance(child.get("id"), str):
                result[child["id"]] = child
            for grandchild in child.values():
                visit(grandchild)
        elif isinstance(child, list):
            for grandchild in child:
                visit(grandchild)
    visit(value)
    return result


def exact_meaning_present(actual: dict[str, Any] | None, expected: Any) -> bool:
    if actual is None:
        return False
    text = actual.get("text", actual.get("title", ""))
    return isinstance(text, str) and meaning_text(expected) in text


def gate_ledger(report: dict[str, Any], bundle: Any, ledger: dict[str, Any]) -> None:
    objects: dict[str, dict[str, Any]] = {}
    for record in bundle.records:
        objects[record.identity] = {"id": record.identity, **record.semantic}
        objects.update(nested_id_map(record.semantic))
    candidate = bundle.one("CandidatePresentationPackageRecord")
    material = bundle.one("PortablePresentationMaterialRecord")
    obligation_targets = {x["id"]: x["target_refs"] for x in candidate.semantic["obligations"]}
    provenance_targets = {x["id"]: x["target_refs"] for x in material.semantic["provenance"]}
    for item in ledger["items"]:
        destination = item["intended_candidate_destination"]
        actual = objects.get(destination)
        if item["item_category"] in {"raw-result", "first-difference-result"}:
            present = actual is not None
            meaning_ok = present
        elif item["item_id"] == "closure:source-provenance":
            present = actual is not None
            meaning_ok = present and actual.get("source_commit") == SOURCE_COMMIT
        else:
            present = actual is not None
            meaning_ok = exact_meaning_present(actual, item["source_authored_meaning"])
        obligations_ok = all(destination in obligation_targets.get(x, []) for x in item["obligation_attachments"])
        provenance_ok = all(destination in provenance_targets.get(x, []) for x in item["provenance_attachments"])
        treatment = {
            "ledger_item_id": item["item_id"],
            "inclusion_status": item["inclusion_status"],
            "expected_destination": destination,
            "actual_identity_present": present,
            "complete_source_meaning_present": meaning_ok,
            "expected_obligation_attachments": item["obligation_attachments"],
            "obligation_attachments_exactly_reach_destination": obligations_ok,
            "expected_provenance_attachments": item["provenance_attachments"],
            "provenance_attachments_exactly_reach_destination": provenance_ok,
            "treatment": "represented" if all((present, meaning_ok, obligations_ok, provenance_ok)) else "blocking-mismatch",
        }
        report["ledger_treatments"].append(treatment)
        if treatment["treatment"] != "represented":
            report["blocking_findings"].append({"check": "ledger-item-treatment", **treatment})


def invariant(report: dict[str, Any], name: str, passed: bool, expected: Any, actual: Any) -> None:
    item = {"invariant": name, "passed": bool(passed), "expected": expected, "actual": actual}
    report["table_invariants"].append(item)
    if not passed:
        report["blocking_findings"].append({"check": "table-invariant", **item})


def gate_table(report: dict[str, Any], bundle: Any, table: dict[str, Any]) -> None:
    candidate = bundle.one("CandidatePresentationPackageRecord")
    material = bundle.one("PortablePresentationMaterialRecord")
    exhibits = candidate.semantic.get("exhibits", [])
    matching = [x for x in exhibits if x.get("id") == table["table_identity"]]
    invariant(report, "exactly-one-table", len(exhibits) == 1 and len(matching) == 1, 1, len(exhibits))
    exhibit = matching[0] if len(matching) == 1 else {}
    expected_columns = [x["column_id"] for x in table["governed_columns"]]
    expected_headings = [x["heading"] for x in table["governed_columns"]]
    invariant(report, "exactly-five-governed-columns-in-listed-order", exhibit.get("column_ids") == expected_columns and exhibit.get("headings") == expected_headings, {"column_ids": expected_columns, "headings": expected_headings}, {"column_ids": exhibit.get("column_ids"), "headings": exhibit.get("headings")})
    bindings = exhibit.get("case_bindings", [])
    invariant(report, "exactly-seven-body-rows", len(bindings) == 7, 7, len(bindings))
    expected_rows = table["rows"]
    values = {x["id"]: x for x in material.semantic.get("values", [])}
    relations = candidate.semantic.get("relations", [])
    provenance = {x["id"]: x for x in material.semantic.get("provenance", [])}
    statement_map = {x["id"]: x for x in candidate.semantic.get("statements", [])}
    actual_order = [x.get("relationship_identity") for x in bindings]
    invariant(report, "canonical-relationship-order", actual_order == table["canonical_relationship_order"], table["canonical_relationship_order"], actual_order)
    invariant(report, "exactly-one-stable-relationship-identity-per-row", all(x.get("id", "").startswith("row:") and x.get("relationship_identity") for x in bindings), "relationship-owned row identities", [x.get("id") for x in bindings])
    invariant(report, "no-coefficient-as-relationship-row", all(not x.get("id", "").startswith("value:") for x in bindings), True, [x.get("id") for x in bindings])
    invariant(report, "no-generic-value-slot-row-identity", all(x.get("id") == f"row:{x.get('relationship_identity')}" for x in bindings), True, [x.get("id") for x in bindings])
    invariant(report, "no-six-or-eight-row-contract", len(bindings) not in {6, 8}, True, len(bindings))
    invariant(report, "no-duplicated-relationship", len(actual_order) == len(set(actual_order)), True, actual_order)
    pair_details = []
    lexical_details = []
    state_details = []
    support_details = []
    for binding, row in zip(bindings, expected_rows):
        expected_pair = [row["raw"]["value_id"], row["first_difference"]["value_id"]]
        actual_pair = [binding.get("primary_ref"), binding.get("comparison_ref")]
        pair_details.append({"row": row["row_id"], "expected": expected_pair, "actual": actual_pair, "passed": expected_pair == actual_pair})
        for key, actual_ref in (("raw", binding.get("primary_ref")), ("first_difference", binding.get("comparison_ref"))):
            actual = values.get(actual_ref, {})
            expected = row[key]
            expected_value = {"payload": expected["exact_decimal_payload"], "lexical_representation": expected["lexical_representation"], "value_state": expected["value_state"], "method": expected["method_ref"], "transformation": expected.get("transformation_ref", "none"), "transformation_state": expected["transformation_state"], "aligned_period": expected["aligned_period"], "aligned_count": expected["aligned_count"], "package_id": expected["package_id"]}
            actual_value = {name: actual.get(name) for name in expected_value}
            lexical_details.append({"value_id": actual_ref, "expected": expected_value, "actual": actual_value, "passed": actual_value == expected_value})
        expected_states = {
            "raw_state": {"transformation_state": row["raw"]["transformation_state"], "period": row["raw"]["aligned_period"], "aligned_count": row["raw"]["aligned_count"]},
            "first_difference_state": {"transformation_state": row["first_difference"]["transformation_state"], "period": row["first_difference"]["aligned_period"], "aligned_count": row["first_difference"]["aligned_count"]},
        }
        actual_states = {key: binding.get(key) for key in expected_states}
        state_details.append({"row": row["row_id"], "expected": expected_states, "actual": actual_states, "passed": actual_states == expected_states})
        row_number = row["row_order"]
        row_statement = statement_map.get(f"statement:task065-row-{row_number:02d}", {})
        qid = row["qualification_statement_ref"]
        expected_q_targets = row["qualification_targets"]
        actual_q_targets = [x.get("target_ref") for x in relations if x.get("source_ref") == qid and x.get("kind") == "limits-target"]
        pid = f"provenance:t039-row-{row_number:02d}"
        support_details.append({
            "row": row["row_id"],
            "classification_present": row["classification"] in row_statement.get("text", ""),
            "evidence_role_present": row["source_inclusion_role"] in row_statement.get("text", ""),
            "qualification_expected": expected_q_targets,
            "qualification_actual": actual_q_targets,
            "qualification_passed": actual_q_targets == expected_q_targets,
            "provenance_expected": [row_statement.get("id"), *expected_pair],
            "provenance_actual": provenance.get(pid, {}).get("target_refs"),
            "provenance_passed": provenance.get(pid, {}).get("target_refs") == [row_statement.get("id"), *expected_pair],
        })
    invariant(report, "exactly-one-raw-and-one-first-difference-value-per-row", all(x["passed"] for x in pair_details), "exact table-contract pair per row", pair_details)
    invariant(report, "no-cross-paired-coefficients", all(x["passed"] for x in pair_details), "no cross pairing", pair_details)
    invariant(report, "exactly-fourteen-coefficients-total", len(values) == 14 and len(exhibit.get("value_ids", [])) == 14 and len(set(exhibit.get("value_ids", []))) == 14, 14, {"material_values": len(values), "table_value_refs": len(exhibit.get("value_ids", [])), "unique_table_value_refs": len(set(exhibit.get("value_ids", [])))})
    invariant(report, "exact-lexical-sign-and-precision", all(x["passed"] for x in lexical_details), "all exact payload/lexical/method/package fields", lexical_details)
    invariant(report, "matching-period-and-aligned-count", all(x["passed"] for x in state_details), "all exact states", state_details)
    invariant(report, "preserved-evidence-role", all(x["evidence_role_present"] and x["classification_present"] for x in support_details), True, support_details)
    invariant(report, "attached-qualification", all(x["qualification_passed"] for x in support_details), True, support_details)
    invariant(report, "attached-provenance", all(x["provenance_passed"] for x in support_details), True, support_details)


def gate_other_contracts(report: dict[str, Any], bundle: Any, blueprint: dict[str, Any]) -> None:
    candidate = bundle.one("CandidatePresentationPackageRecord")
    material = bundle.one("PortablePresentationMaterialRecord")
    statement_ids = [x["id"] for x in candidate.semantic["statements"]]
    section_actual = [{"section_id": x["id"], "children": x["children"]} for x in candidate.semantic["sections"]]
    expected_section = []
    conditional_ids = {x["statement_id"] for x in blueprint["conditional_composition"]}
    for item in sorted(blueprint["deterministic_section_hierarchy"], key=lambda x: x["order"]):
        children = list(item["children"])
        if item["section_id"] == "section:task065-interpretation":
            children += [x["statement_id"] for x in blueprint["conditional_composition"] if x["statement_id"] in conditional_ids]
        expected_section.append({"section_id": item["section_id"], "children": children})
    check(report, "exact-deterministic-hierarchy", section_actual == expected_section, expected_section, section_actual)
    expected_statements = [x["statement_id"] for x in blueprint["statement_contract"]["ledger_statement_index"]]
    check(report, "exact-statement-identities", statement_ids == expected_statements, expected_statements, statement_ids)
    check(report, "no-task063-identity", "task063" not in canonical_object([r.to_document() for r in bundle.records]).decode("utf-8").lower(), "no TASK-063 identity", "present" if "task063" in canonical_object([r.to_document() for r in bundle.records]).decode("utf-8").lower() else "absent")
    authority_ids = [x["id"] for x in material.semantic["authorities"]]
    expected_authorities = list(TERMINAL_OPERATIONAL_IDENTITIES) + [ANALYTICAL_AUTHORITY_ID, STRUCTURAL_AUTHORITY_ID]
    check(report, "task062-eight-operational-plus-two-content-authorities", authority_ids == expected_authorities, expected_authorities, authority_ids)
    displayed = canonical_object({"statements": candidate.semantic["statements"], "sections": candidate.semantic["sections"], "exhibits": candidate.semantic["exhibits"]}).decode("utf-8")
    leaked = [identity for identity in TERMINAL_OPERATIONAL_IDENTITIES if identity in displayed]
    check(report, "no-operational-authority-in-displayed-semantics", not leaked, [], leaked)
    # The accepted TASK-062 representative projection is bounded to <=32.  This
    # gate reports the actual result rather than pretending the much larger
    # TASK-064 identity contract fits.  A failure blocks promotion truthfully.
    check(report, "task062-representative-profile-statement-bound", len(statement_ids) <= 32, "<=32", len(statement_ids))
    validation = validate_bundle(bundle, through_layer="L2")
    report["technical_validation"] = {
        "executed_layers": list(validation.executed_layers),
        "passed": not validation.blocking,
        "findings": [finding.__dict__ for finding in validation.findings],
    }
    if validation.blocking:
        report["blocking_findings"].append({"check": "BCRP-L0-L2", "findings": report["technical_validation"]["findings"]})


def persist_candidate(bundle: Any, report: dict[str, Any]) -> tuple[bytes, bytes, str]:
    profile_bytes = canonical_json_bytes(bundle, domain="profile-instance", require_valid=True)
    candidate_bytes = canonical_json_bytes(bundle, domain="candidate-semantic", require_valid=True)
    fingerprint = fingerprint_bundle(bundle, domain="candidate-semantic", require_valid=True)
    fingerprint_document = {
        "algorithm": fingerprint.algorithm,
        "canonicalization": fingerprint.canonicalization,
        "digest": fingerprint.digest,
        "domain": fingerprint.domain,
        "profile_identity": fingerprint.profile_identity,
        "profile_version": fingerprint.profile_version,
        "root_identity": fingerprint.root_identity,
        "scope": fingerprint.scope,
    }
    exclusive_bytes(CANDIDATE_DIR / "candidate.profile-instance.canonical.json", profile_bytes + b"\n")
    exclusive_bytes(CANDIDATE_DIR / "candidate.semantic.canonical.json", candidate_bytes + b"\n")
    exclusive_bytes(CANDIDATE_DIR / "candidate.fingerprint.json", json.dumps(fingerprint_document, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n")
    report["candidate_persisted"] = True
    report["candidate_evidence"] = {
        "profile_instance_path": str(CANDIDATE_DIR / "candidate.profile-instance.canonical.json"),
        "profile_instance_sha256": hashlib.sha256(profile_bytes).hexdigest(),
        "candidate_semantic_path": str(CANDIDATE_DIR / "candidate.semantic.canonical.json"),
        "candidate_semantic_sha256": hashlib.sha256(candidate_bytes).hexdigest(),
        "fingerprint_path": str(CANDIDATE_DIR / "candidate.fingerprint.json"),
        "candidate_fingerprint": fingerprint_document,
    }
    return profile_bytes, candidate_bytes, fingerprint.digest


def main() -> int:
    report = initial_report()
    try:
        create_single_use_marker()  # irrevocably before author_candidate_bundle
    except FileExistsError:
        print("TASK-065 Candidate gate: BLOCKED (single-use authoring marker already exists)")
        return 2
    try:
        ledger = load_json(LEDGER_PATH)
        table = load_json(TABLE_PATH)
        blueprint = load_json(BLUEPRINT_PATH)
        gate = load_json(GATE_PATH)
        admission = load_json(ADMISSION_PATH)
        source, source_bytes = load_source_at_commit()
        report["immutable_source"] = {
            "commit": SOURCE_COMMIT, "path": SOURCE_PATH,
            "byte_length": len(source_bytes), "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "loaded_via": "git show",
        }
        verify_authoritative_inputs(report, ledger, table, blueprint, gate, admission, source)
        if report["blocking_findings"]:
            raise ValueError("authoritative prerequisite checks blocked Candidate authoring")

        bundle = author(ledger, table, blueprint)  # the sole Candidate creation call
        report["candidate_created"] = True
        report["candidate_identity"] = bundle.one("CandidatePresentationPackageRecord").identity
        profile_before, semantic_before, digest_before = persist_candidate(bundle, report)
        frozen_documents = deepcopy([record.to_document() for record in bundle.records])

        gate_ledger(report, bundle, ledger)
        gate_table(report, bundle, table)
        gate_other_contracts(report, bundle, blueprint)

        profile_after = canonical_json_bytes(bundle, domain="profile-instance", require_valid=True)
        semantic_after = canonical_json_bytes(bundle, domain="candidate-semantic", require_valid=True)
        digest_after = fingerprint_bundle(bundle, domain="candidate-semantic", require_valid=True).digest
        mutation_free = (
            profile_before == profile_after and semantic_before == semantic_after
            and digest_before == digest_after
            and frozen_documents == [record.to_document() for record in bundle.records]
        )
        check(report, "no-post-authoring-mutation", mutation_free, True, mutation_free)
        report["status"] = "PASS" if not report["blocking_findings"] else "BLOCKED"
    except BaseException as exc:
        report["status"] = "BLOCKED"
        report["exception"] = {"type": type(exc).__name__, "message": str(exc)}
        report["blocking_findings"].append({"check": "single-run-exception", "type": type(exc).__name__, "message": str(exc)})
    persist_report(report)
    print(f"TASK-065 Candidate gate: {report['status']} ({len(report['blocking_findings'])} blocking findings)")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
