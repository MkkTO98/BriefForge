"""Tests for validation policy identity metadata.

These tests cover only audit metadata linking a Validation Judgment, Ready
Presentation Package, and downstream semantic access to the validation policy
that accepted the candidate. They must not require configurable policies,
multiple validators, rule engines, rendering, browser behavior, templates,
serialization, persistence, APIs, visualization, exports, portal behavior,
dashboards, search, or maps.
"""

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
TESTS = PROJECT_ROOT / "tests"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(TESTS))

from test_constitutional_validation import valid_candidate_package  # noqa: E402


class ValidationPolicyIdentityTests(unittest.TestCase):
    def test_validation_judgment_includes_validation_policy_identity(self):
        from briefforge.validation import CURRENT_VALIDATION_POLICY_ID, validate_candidate_presentation_package

        judgment = validate_candidate_presentation_package(valid_candidate_package())

        self.assertEqual(judgment.validation_policy_id, CURRENT_VALIDATION_POLICY_ID)
        self.assertIsInstance(judgment.validation_policy_id, str)
        self.assertTrue(judgment.validation_policy_id.strip())

    def test_ready_package_preserves_validation_policy_identity(self):
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.validation import validate_candidate_presentation_package

        candidate = valid_candidate_package()
        judgment = validate_candidate_presentation_package(candidate)

        ready = promote_candidate_presentation_package(candidate, judgment)

        self.assertEqual(ready.validation_policy_id, judgment.validation_policy_id)
        self.assertEqual(ready.validation_judgment.validation_policy_id, ready.validation_policy_id)

    def test_downstream_access_exposes_policy_identity_but_cannot_mutate_it(self):
        from briefforge.downstream import prepare_downstream_semantic_package
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.validation import validate_candidate_presentation_package

        candidate = valid_candidate_package()
        judgment = validate_candidate_presentation_package(candidate)
        ready = promote_candidate_presentation_package(candidate, judgment)

        downstream_package = prepare_downstream_semantic_package(ready)

        self.assertEqual(downstream_package.validation_policy_id, ready.validation_policy_id)
        with self.assertRaises(FrozenInstanceError):
            downstream_package.ready_package = None
        with self.assertRaises(FrozenInstanceError):
            downstream_package.ready_package.validation_policy_id = "changed-policy"
        with self.assertRaises(FrozenInstanceError):
            downstream_package.validation_judgment.validation_policy_id = "changed-policy"

    def test_promotion_rejects_judgment_with_absent_policy_identity(self):
        from briefforge.promotion import PromotionRejected, promote_candidate_presentation_package
        from briefforge.validation import validate_candidate_presentation_package

        candidate = valid_candidate_package()
        judgment = validate_candidate_presentation_package(candidate)
        malformed_judgment = replace(judgment, validation_policy_id=None)

        with self.assertRaises(PromotionRejected):
            promote_candidate_presentation_package(candidate, malformed_judgment)

    def test_promotion_rejects_judgment_with_malformed_policy_identity(self):
        from briefforge.promotion import PromotionRejected, promote_candidate_presentation_package
        from briefforge.validation import validate_candidate_presentation_package

        candidate = valid_candidate_package()
        judgment = validate_candidate_presentation_package(candidate)
        malformed_judgment = replace(judgment, validation_policy_id="   ")

        with self.assertRaises(PromotionRejected):
            promote_candidate_presentation_package(candidate, malformed_judgment)

    def test_existing_validation_behavior_remains_unchanged(self):
        from briefforge.runtime import CandidatePresentationPackage
        from briefforge.validation import validate_candidate_presentation_package

        candidate = valid_candidate_package()
        valid_judgment = validate_candidate_presentation_package(candidate)
        invalid_judgment = validate_candidate_presentation_package(
            CandidatePresentationPackage(
                identity=None,
                organizing_purpose=candidate.organizing_purpose,
                statements=candidate.statements,
                upstream_references=candidate.upstream_references,
                obligations=candidate.obligations,
            )
        )

        self.assertTrue(valid_judgment.valid)
        self.assertEqual(valid_judgment.findings, ())
        self.assertFalse(invalid_judgment.valid)
        self.assertTrue(invalid_judgment.findings)
        self.assertEqual(valid_judgment.candidate_package_id, candidate.identity.package_id)
        self.assertIsInstance(valid_judgment.candidate_semantic_fingerprint, str)


if __name__ == "__main__":
    unittest.main()
