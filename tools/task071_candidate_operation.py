#!/usr/bin/env python3
"""Bounded TASK-071 successor Candidate preparation, authoring, and recovery.

`run_preflight` is read-only. `prepare_governed_attempt` creates only the accepted
TASK-070 authority and PREPARED_NOT_CONSUMED commitment. `author_governed_once`
is the sole real construction operation and calls only the public governed
coordinator boundary. Recovery never constructs.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from briefforge.bcrp.authoring import RecordDraft
from briefforge.candidate_authoring import (
    AuthorityBinding,
    GOVERNED_AUTHORITY_ROOT,
    GOVERNED_LEDGER_ROOT,
    GOVERNED_OUTPUT_ROOT,
    PAIRED_CANDIDATE_VALIDATOR_IDENTITY,
    PAIRED_SEMANTIC_VALIDATION_PROFILE,
    _authenticate_authority_evidence,
    _binding_document,
    _canonical,
    _exclusive_commit,
    _validate_binding,
    fingerprint_authoring_input,
    governed_author_candidate,
    governed_recover_candidate,
)
from briefforge.bcrp.canonical import ORDERED_LIST_KEYS
from briefforge_paired_terminal_profile.profile import (
    build_paired_semantic_extension,
    paired_semantic_closure_fingerprint,
)
from tools import author_task069_candidate as frozen_projection

ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "TASK-071"
BRIEF_ID = "brief:task071-cross-inquiry"
MATERIAL_ID = "material:task071-t039"
CANDIDATE_ID = "candidate:task071-cross-inquiry"
BLUEPRINT_SHA256 = "424fd07da96e1e0914385997dcdb9f4f645f1d6228b4d9f9bb93cfdfbe4689ae"
CAMPAIGN_ID = f"blueprint:{BLUEPRINT_SHA256}"
ATTEMPT_ID = "attempt:task071-representative-campaign-002"
SOURCE_SNAPSHOT = frozen_projection.SOURCE_SNAPSHOT
EXPECTED_SEMANTIC_CLOSURE_SHA256 = "ed0d50ca4633db9d55846af949cfe1f1dc147412aefe0f418710738f69f81df0"
PREDECESSOR_PATH = ROOT / "artifacts/pilots/task069/.candidate-authoring-single-use"
PREDECESSOR_SHA256 = "05d7d994a64b798417e21b26ba5782cbc31d87a68af39e0a13f282a073e8a70f"
DECISION_PATH = ROOT / "artifacts/decisions/D-20260808-task-071-successor-candidate-attempt-authority-and-identity-lineage.md"
AUTHORITY_PATH = GOVERNED_AUTHORITY_ROOT / f"{ATTEMPT_ID}.authority.json"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_closure_fingerprint(semantics) -> str:
    return paired_semantic_closure_fingerprint(semantics)


def _contracts():
    ledger, table, blueprint, gate, admission = frozen_projection.load_contracts()
    if _sha256(frozen_projection.BLUEPRINT_PATH) != BLUEPRINT_SHA256:
        raise ValueError("TASK-064 blueprint byte fingerprint differs")
    if ledger.get("source_snapshot_identity") != SOURCE_SNAPSHOT:
        raise ValueError("TASK-064 source snapshot identity differs")
    return ledger, table, blueprint, gate, admission


def build_successor_inputs():
    """Build exact TASK-064 semantics with a new outer lifecycle envelope only."""
    ledger, table, blueprint, _, _ = _contracts()
    semantics = frozen_projection.build_paired_semantics(ledger, table, blueprint)
    frozen_brief, frozen_material, frozen_candidate = frozen_projection.build_record_drafts(semantics)

    brief = RecordDraft(BRIEF_ID, deepcopy(frozen_brief.semantic),
                        deepcopy(frozen_brief.extensions))
    material = RecordDraft(MATERIAL_ID, deepcopy(frozen_material.semantic),
                           deepcopy(frozen_material.extensions))
    candidate_semantic = deepcopy(frozen_candidate.semantic)
    candidate_semantic["brief_ref"] = BRIEF_ID
    candidate_semantic["material_refs"] = [MATERIAL_ID]
    extension = build_paired_semantic_extension(semantics, candidate_identity=CANDIDATE_ID)
    candidate = RecordDraft(CANDIDATE_ID, candidate_semantic, [extension])

    if semantic_closure_fingerprint(semantics) != EXPECTED_SEMANTIC_CLOSURE_SHA256:
        raise ValueError("TASK-064 semantic closure fingerprint differs")
    return semantics, brief, material, candidate


def build_authority_binding(semantics, brief, material, candidate) -> AuthorityBinding:
    if semantic_closure_fingerprint(semantics) != EXPECTED_SEMANTIC_CLOSURE_SHA256:
        raise ValueError("prepared semantics differ from accepted closure")
    if _sha256(PREDECESSOR_PATH) != PREDECESSOR_SHA256:
        raise ValueError("TASK-069 predecessor marker differs")
    decision_sha = _sha256(DECISION_PATH)
    return AuthorityBinding(
        task_id=TASK_ID,
        campaign_id=CAMPAIGN_ID,
        candidate_id=CANDIDATE_ID,
        brief_id=BRIEF_ID,
        material_ids=(MATERIAL_ID,),
        source_snapshot=SOURCE_SNAPSHOT,
        blueprint_fingerprint=BLUEPRINT_SHA256,
        attempt_id=ATTEMPT_ID,
        cumulative_attempt_number=2,
        predecessor_attempt_digests=(PREDECESSOR_SHA256,),
        predecessor_evidence_paths=(str(PREDECESSOR_PATH.resolve()),),
        authoring_input_sha256=fingerprint_authoring_input(brief, material, candidate),
        semantic_validation_profile=PAIRED_SEMANTIC_VALIDATION_PROFILE,
        expected_semantic_closure_sha256=EXPECTED_SEMANTIC_CLOSURE_SHA256,
        validator_identity=PAIRED_CANDIDATE_VALIDATOR_IDENTITY,
        authority_decision_path=str(DECISION_PATH.resolve()),
        authority_decision_sha256=decision_sha,
        ledger_root=str(GOVERNED_LEDGER_ROOT.resolve()),
        output_root=str(GOVERNED_OUTPUT_ROOT.resolve()),
        scope="governed",
    )


def _topology(semantics) -> dict[str, int]:
    return {
        "sections": len(semantics.sections),
        "statements": len(semantics.statements),
        "qualifications": len(semantics.qualifications),
        "obligations": len(semantics.obligations),
        "provenance": len(semantics.provenance),
        "paired_rows": len(semantics.table.rows),
        "paired_values": len(semantics.values),
        "governed_columns": len(semantics.table.column_identities),
    }


def run_preflight() -> dict[str, Any]:
    """Authenticate all permitted prerequisites without governed filesystem writes."""
    ledger, table, blueprint, gate, admission = _contracts()
    frozen = frozen_projection.preflight(
        ledger, table, blueprint, gate, admission, authenticate_source=True,
    )
    semantics, brief, material, candidate = build_successor_inputs()
    trace = frozen_projection.semantic_traceability_report(
        semantics, ledger, table, blueprint,
    )
    binding = build_authority_binding(semantics, brief, material, candidate)
    _validate_binding(binding)
    _authenticate_authority_evidence(binding, GOVERNED_AUTHORITY_ROOT, "governed")

    topology = _topology(semantics)
    expected = {"sections": 6, "statements": 76, "qualifications": 27,
                "obligations": 5, "provenance": 8, "paired_rows": 7,
                "paired_values": 14, "governed_columns": 5}
    if topology != expected or not trace["passed"] or not frozen["traceability"]["passed"]:
        raise ValueError("TASK-064 semantic topology or traceability differs")
    if "records" in ORDERED_LIST_KEYS:
        raise ValueError("canonical record array unexpectedly preserves authoring role order")

    statement_order = [item.identity for item in semantics.statements]
    attachment_counts = {
        "qualification_edges": len(semantics.qualifications),
        "obligation_targets": sum(len(item.target_refs) for item in semantics.obligations),
        "provenance_targets": sum(len(item.target_refs) for item in semantics.provenance),
        "row_qualification_refs": sum(len(item.qualification_refs) for item in semantics.table.rows),
        "row_provenance_refs": sum(len(item.provenance_refs) for item in semantics.table.rows),
    }
    artifacts = []
    for path in (frozen_projection.LEDGER_PATH, frozen_projection.TABLE_PATH,
                 frozen_projection.BLUEPRINT_PATH, frozen_projection.GATE_PATH,
                 frozen_projection.ADMISSION_PATH):
        artifacts.append({"path": path.relative_to(ROOT).as_posix(),
                          "bytes": len(path.read_bytes()), "sha256": _sha256(path)})
    return {
        "format": "briefforge-task071-pre-attempt-readiness-v1",
        "result": "PASS",
        "task_id": TASK_ID,
        "campaign_id": CAMPAIGN_ID,
        "attempt_id": ATTEMPT_ID,
        "cumulative_attempt_number": 2,
        "source_snapshot": SOURCE_SNAPSHOT,
        "source_authentication": {
            key: value for key, value in frozen["source_authentication"].items()
            if key != "source"
        },
        "contract_artifacts": artifacts,
        "blueprint_fingerprint_sha256": BLUEPRINT_SHA256,
        "semantic_closure_sha256": EXPECTED_SEMANTIC_CLOSURE_SHA256,
        "authoring_input_sha256": binding.authoring_input_sha256,
        "topology": topology,
        "statement_order_sha256": hashlib.sha256(canonical_bytes(statement_order)).hexdigest(),
        "exact_statement_order": trace["exact_authoritative_semantics"],
        "exact_statement_ledger_composition": trace["exact_statement_ledger_composition"],
        "all_109_treatments_passed": len(trace["ledger_treatments"]) == 109 and
                                     all(item["passed"] for item in trace["ledger_treatments"]),
        "all_7_rows_passed": len(trace["row_results"]) == 7 and
                              all(item["passed"] for item in trace["row_results"]),
        "attachment_counts": attachment_counts,
        "canonical_serialization": {
            "record_array_key_is_unordered": True,
            "physical_kind_order": ["CandidatePresentationPackageRecord",
                                    "PortablePresentationMaterialRecord",
                                    "PresentationBriefRecord"],
            "physical_kind_order_authenticated": True,
            "role_order_is_not_required": True,
            "authored_statement_order_key_is_ordered": "children" in ORDERED_LIST_KEYS,
        },
        "authority_binding": json.loads(canonical_bytes(asdict(binding))),
        "coordinator_route": {
            "author": "briefforge.candidate_authoring.governed_author_candidate",
            "recover": "briefforge.candidate_authoring.governed_recover_candidate",
            "caller_supplied_builder": False,
            "caller_supplied_validator": False,
            "caller_supplied_fault": False,
        },
    }


def prepare_governed_attempt():
    """Create exactly one governed authority and PREPARED_NOT_CONSUMED commitment."""
    semantics, brief, material, candidate = build_successor_inputs()
    binding = build_authority_binding(semantics, brief, material, candidate)
    _validate_binding(binding)
    _authenticate_authority_evidence(binding, GOVERNED_AUTHORITY_ROOT, "governed")
    data = _canonical(_binding_document(binding, AUTHORITY_PATH.absolute()))
    _exclusive_commit(AUTHORITY_PATH, data)
    authority_digest = hashlib.sha256(data).hexdigest()
    state = {
        "format": "briefforge-candidate-attempt-state-v1",
        "sequence": 0,
        "state": "PREPARED_NOT_CONSUMED",
        "authority_digest": authority_digest,
        "prior_state_digest": None,
        "detail": {},
    }
    ledger = GOVERNED_LEDGER_ROOT / ATTEMPT_ID
    _exclusive_commit(ledger / "00-PREPARED_NOT_CONSUMED.json", _canonical(state))
    return {"authority_path": str(AUTHORITY_PATH.resolve()),
            "authority_sha256": authority_digest,
            "prepared_state_path": str((ledger / "00-PREPARED_NOT_CONSUMED.json").resolve()),
            "authoring_input_sha256": binding.authoring_input_sha256,
            "expected_semantic_closure_sha256": binding.expected_semantic_closure_sha256,
            "state": "PREPARED_NOT_CONSUMED"}


def _authority_digest() -> str:
    if not AUTHORITY_PATH.is_file():
        raise FileNotFoundError("governed TASK-071 authority is absent")
    return _sha256(AUTHORITY_PATH)


def author_governed_once():
    """Invoke the accepted public governed authoring boundary exactly once."""
    _, brief, material, candidate = build_successor_inputs()
    return governed_author_candidate(
        AUTHORITY_PATH, _authority_digest(), brief, material, candidate,
    )


def recover_governed_attempt():
    """Authenticate/recover without reconstructing Candidate bytes."""
    return governed_recover_candidate(AUTHORITY_PATH, _authority_digest())


def _receipt_dict(receipt) -> dict[str, Any]:
    return asdict(receipt)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("preflight", "prepare", "author", "recover"))
    args = parser.parse_args(argv)
    if args.action == "preflight":
        result = run_preflight()
    elif args.action == "prepare":
        result = prepare_governed_attempt()
    elif args.action == "author":
        result = _receipt_dict(author_governed_once())
    else:
        result = _receipt_dict(recover_governed_attempt())
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
