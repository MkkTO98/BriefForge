from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for value in (str(ROOT), str(SRC)):
    if value not in sys.path:
        sys.path.insert(0, value)

from briefforge.candidate_authoring import (  # noqa: E402
    GOVERNED_AUTHORITY_ROOT,
    GOVERNED_LEDGER_ROOT,
    GOVERNED_OUTPUT_ROOT,
    fingerprint_authoring_input,
)


class Task071SuccessorCandidateOperationTests(unittest.TestCase):
    def _governed_inventory(self):
        result = {}
        for root in (GOVERNED_AUTHORITY_ROOT, GOVERNED_LEDGER_ROOT, GOVERNED_OUTPUT_ROOT):
            if root.exists():
                result[str(root)] = tuple(
                    (path.relative_to(root).as_posix(),
                     hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "directory")
                    for path in sorted(root.rglob("*"))
                )
            else:
                result[str(root)] = None
        return result

    def test_exact_successor_identity_and_drafts_preserve_frozen_internal_semantics(self):
        from tools import task071_candidate_operation as operation

        before = self._governed_inventory()
        semantics, brief, material, candidate = operation.build_successor_inputs()
        self.assertEqual("brief:task071-cross-inquiry", brief.identity)
        self.assertEqual("material:task071-t039", material.identity)
        self.assertEqual("candidate:task071-cross-inquiry", candidate.identity)
        self.assertEqual(brief.identity, candidate.semantic["brief_ref"])
        self.assertEqual([material.identity], candidate.semantic["material_refs"])
        extension = candidate.extensions[0]
        self.assertEqual([candidate.identity], extension["target_refs"])
        self.assertEqual(
            "ed0d50ca4633db9d55846af949cfe1f1dc147412aefe0f418710738f69f81df0",
            operation.semantic_closure_fingerprint(semantics),
        )
        self.assertEqual(before, self._governed_inventory())

    def test_binding_is_exact_cumulative_attempt_two_and_uses_fixed_roots(self):
        from tools import task071_candidate_operation as operation

        semantics, brief, material, candidate = operation.build_successor_inputs()
        binding = operation.build_authority_binding(semantics, brief, material, candidate)
        self.assertEqual("TASK-071", binding.task_id)
        self.assertEqual(
            "blueprint:424fd07da96e1e0914385997dcdb9f4f645f1d6228b4d9f9bb93cfdfbe4689ae",
            binding.campaign_id,
        )
        self.assertEqual("attempt:task071-representative-campaign-002", binding.attempt_id)
        self.assertEqual(2, binding.cumulative_attempt_number)
        self.assertEqual(
            ("05d7d994a64b798417e21b26ba5782cbc31d87a68af39e0a13f282a073e8a70f",),
            binding.predecessor_attempt_digests,
        )
        self.assertEqual(fingerprint_authoring_input(brief, material, candidate),
                         binding.authoring_input_sha256)
        self.assertEqual(str(GOVERNED_LEDGER_ROOT.resolve()), binding.ledger_root)
        self.assertEqual(str(GOVERNED_OUTPUT_ROOT.resolve()), binding.output_root)
        self.assertEqual("governed", binding.scope)

    def test_preflight_authenticates_complete_frozen_contract_without_authoring(self):
        from tools import task071_candidate_operation as operation

        before = self._governed_inventory()
        report = operation.run_preflight()
        self.assertEqual("PASS", report["result"])
        self.assertEqual(13, report["source_authentication"]["artifact_count"])
        self.assertEqual(130, report["source_authentication"]["locator_count"])
        self.assertEqual(
            {"sections": 6, "statements": 76, "qualifications": 27,
             "obligations": 5, "provenance": 8, "paired_rows": 7,
             "paired_values": 14, "governed_columns": 5},
            report["topology"],
        )
        self.assertTrue(report["canonical_serialization"]["role_order_is_not_required"])
        self.assertTrue(report["canonical_serialization"]["physical_kind_order_authenticated"])
        self.assertEqual(before, self._governed_inventory())

    def test_operation_boundaries_expose_no_builder_validator_or_fault_callbacks(self):
        from tools import task071_candidate_operation as operation

        self.assertEqual((), tuple(inspect.signature(operation.prepare_governed_attempt).parameters))
        self.assertEqual((), tuple(inspect.signature(operation.author_governed_once).parameters))
        self.assertEqual((), tuple(inspect.signature(operation.recover_governed_attempt).parameters))
        source = inspect.getsource(operation.author_governed_once)
        self.assertIn("governed_author_candidate", source)
        self.assertNotIn("author_candidate_bundle", source)
        self.assertNotIn("fault", source)

    def test_preflight_report_is_canonical_and_replay_stable(self):
        from tools import task071_candidate_operation as operation

        first = operation.run_preflight()
        second = operation.run_preflight()
        self.assertEqual(first, second)
        encoded = operation.canonical_bytes(first)
        self.assertEqual(first, json.loads(encoded))
        self.assertEqual(encoded, operation.canonical_bytes(json.loads(encoded)))


if __name__ == "__main__":
    unittest.main()
