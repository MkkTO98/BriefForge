"""TASK-046 BCRP candidate authoring and lifecycle-compatibility proof.

The authoring boundary is intentionally renderer-independent and does not replace
or adapt the historical runtime.  The TASK-039 proof targets the accepted BCRP
golden Candidate semantics; it does not rewrite historical publication evidence.
"""

from __future__ import annotations

from copy import deepcopy
import sys
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

from briefforge.bcrp import (  # noqa: E402
    BCRPAuthoringRejected,
    BCRPPromotionRejected,
    RecordDraft,
    author_candidate_bundle,
    fingerprint_bundle,
    promote_validated_candidate,
    record_candidate_validation,
    semantic_equal,
    validate_bundle,
)
from briefforge.bcrp.corpus import CASE_IDS, load_case  # noqa: E402


class BCRPCandidateAuthoringTests(unittest.TestCase):
    def _draft(self, bundle, kind: str) -> RecordDraft:
        record = bundle.one(kind)
        return RecordDraft(
            identity=record.identity,
            semantic=deepcopy(record.semantic),
            extensions=deepcopy(record.extensions),
        )

    def _author_case(self, case_id: str):
        expected = load_case(case_id)
        authored = author_candidate_bundle(
            brief=self._draft(expected, "PresentationBriefRecord"),
            material=self._draft(expected, "PortablePresentationMaterialRecord"),
            candidate=self._draft(expected, "CandidatePresentationPackageRecord"),
        )
        return expected, authored

    def test_task039_derived_authoring_matches_accepted_golden_candidate(self):
        expected, authored = self._author_case(CASE_IDS[0])
        self.assertEqual(
            tuple(record.kind for record in authored.records),
            (
                "PresentationBriefRecord",
                "PortablePresentationMaterialRecord",
                "CandidatePresentationPackageRecord",
            ),
        )
        self.assertFalse(validate_bundle(authored, through_layer="L2").blocking)
        self.assertTrue(semantic_equal(expected, authored))
        self.assertEqual(
            fingerprint_bundle(expected, domain="candidate-semantic"),
            fingerprint_bundle(authored, domain="candidate-semantic"),
        )

    def test_authoring_is_generic_not_a_task039_fixture_special_case(self):
        expected, authored = self._author_case(CASE_IDS[1])
        self.assertTrue(semantic_equal(expected, authored))
        candidate = authored.one("CandidatePresentationPackageRecord")
        self.assertEqual(candidate.identity, "candidate:case-2")
        self.assertTrue(any(statement["posture"] == "recommendation" for statement in candidate.semantic["statements"]))

    def test_authoring_copies_input_and_rejects_invalid_candidate_closure(self):
        expected = load_case(CASE_IDS[0])
        brief = self._draft(expected, "PresentationBriefRecord")
        material = self._draft(expected, "PortablePresentationMaterialRecord")
        candidate = self._draft(expected, "CandidatePresentationPackageRecord")
        authored = author_candidate_bundle(brief=brief, material=material, candidate=candidate)
        candidate.semantic["statements"][0]["text"] = "mutated after authoring"
        self.assertNotEqual(
            candidate.semantic["statements"][0]["text"],
            authored.one("CandidatePresentationPackageRecord").semantic["statements"][0]["text"],
        )

        invalid = self._draft(expected, "CandidatePresentationPackageRecord")
        invalid.semantic["brief_ref"] = "brief:absent"
        with self.assertRaisesRegex(BCRPAuthoringRejected, "L1|identity-or-reference-integrity"):
            author_candidate_bundle(brief=brief, material=material, candidate=invalid)


class BCRPLifecycleAuthorityTests(unittest.TestCase):
    def _authored(self):
        expected = load_case(CASE_IDS[0])
        draft = lambda kind: RecordDraft(  # noqa: E731
            identity=expected.one(kind).identity,
            semantic=deepcopy(expected.one(kind).semantic),
            extensions=deepcopy(expected.one(kind).extensions),
        )
        return author_candidate_bundle(
            brief=draft("PresentationBriefRecord"),
            material=draft("PortablePresentationMaterialRecord"),
            candidate=draft("CandidatePresentationPackageRecord"),
        )

    def test_technical_validation_records_layers_without_manufacturing_judgment(self):
        authored = self._authored()
        result = record_candidate_validation(authored)
        candidate_digest = fingerprint_bundle(authored, domain="candidate-semantic").digest
        self.assertEqual(result.candidate_fingerprint, candidate_digest)
        self.assertEqual(result.executed_layers, ("L0", "L1", "L2"))
        self.assertTrue(result.passed)
        self.assertEqual(result.findings, ())
        self.assertFalse(authored.records_of_kind("ValidationJudgmentRecord"))

    def test_native_bcrp_promotion_is_authority_gated(self):
        with self.assertRaisesRegex(BCRPPromotionRejected, "sole operational|compatibility"):
            promote_validated_candidate(
                self._authored(),
                ready_identity="ready:authority-free",
                readiness_time="2026-07-16T14:01:00Z",
            )

    def test_invalid_technical_findings_are_retained_without_judgment(self):
        authored = self._authored()
        authored.one("CandidatePresentationPackageRecord").semantic["statements"][0].pop("authority_ref")
        result = record_candidate_validation(authored)
        self.assertFalse(result.passed)
        self.assertTrue(result.findings)
        self.assertFalse(authored.records_of_kind("ValidationJudgmentRecord"))


if __name__ == "__main__":
    unittest.main()
