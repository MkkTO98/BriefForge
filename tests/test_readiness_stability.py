"""Tests for readiness stability via semantic fingerprints.

These tests cover only semantic package substance linkage across validation,
promotion, readiness, and downstream access. They must not require rendering,
HTML, browser behavior, templates, serialization, APIs, persistence, networking,
visualization, exports, portal logic, dashboards, or renderer ownership.
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


class ReadinessStabilityTests(unittest.TestCase):
    def test_validation_judgment_links_candidate_identity_and_semantic_fingerprint(self):
        from briefforge.runtime import semantic_fingerprint
        from briefforge.validation import validate_candidate_presentation_package

        candidate = valid_candidate_package()

        judgment = validate_candidate_presentation_package(candidate)

        self.assertTrue(judgment.valid)
        self.assertEqual(judgment.candidate_package_id, candidate.identity.package_id)
        self.assertEqual(judgment.candidate_semantic_fingerprint, semantic_fingerprint(candidate))
        self.assertIsInstance(judgment.candidate_semantic_fingerprint, str)
        self.assertGreater(len(judgment.candidate_semantic_fingerprint), 20)

    def test_promotion_succeeds_when_candidate_identity_and_fingerprint_match_judgment(self):
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.runtime import semantic_fingerprint
        from briefforge.validation import validate_candidate_presentation_package

        candidate = valid_candidate_package()
        judgment = validate_candidate_presentation_package(candidate)

        ready = promote_candidate_presentation_package(candidate, judgment)

        self.assertEqual(ready.candidate.identity.package_id, judgment.candidate_package_id)
        self.assertEqual(ready.semantic_fingerprint, judgment.candidate_semantic_fingerprint)
        self.assertEqual(ready.semantic_fingerprint, semantic_fingerprint(candidate))

    def test_promotion_fails_if_candidate_substance_changes_after_validation(self):
        from briefforge.promotion import PromotionRejected, promote_candidate_presentation_package
        from briefforge.validation import validate_candidate_presentation_package

        candidate = valid_candidate_package()
        judgment = validate_candidate_presentation_package(candidate)
        changed_statement = replace(
            candidate.statements[0],
            encounter_meaning="Changed semantic encounter meaning after validation.",
        )
        changed_candidate = replace(candidate, statements=(changed_statement,))

        self.assertEqual(changed_candidate.identity.package_id, candidate.identity.package_id)
        with self.assertRaises(PromotionRejected):
            promote_candidate_presentation_package(changed_candidate, judgment)

    def test_ready_package_preserves_the_accepted_fingerprint(self):
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.validation import validate_candidate_presentation_package

        candidate = valid_candidate_package()
        judgment = validate_candidate_presentation_package(candidate)

        ready = promote_candidate_presentation_package(candidate, judgment)

        self.assertEqual(ready.semantic_fingerprint, judgment.candidate_semantic_fingerprint)
        self.assertEqual(ready.validation_judgment.candidate_semantic_fingerprint, ready.semantic_fingerprint)

    def test_downstream_access_exposes_fingerprint_but_cannot_mutate_it(self):
        from briefforge.downstream import prepare_downstream_semantic_package
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.validation import validate_candidate_presentation_package

        candidate = valid_candidate_package()
        judgment = validate_candidate_presentation_package(candidate)
        ready = promote_candidate_presentation_package(candidate, judgment)

        downstream_package = prepare_downstream_semantic_package(ready)

        self.assertEqual(downstream_package.semantic_fingerprint, ready.semantic_fingerprint)
        with self.assertRaises(FrozenInstanceError):
            downstream_package.ready_package = None
        with self.assertRaises(FrozenInstanceError):
            downstream_package.ready_package.semantic_fingerprint = "changed"

    def test_semantic_fingerprint_surface_has_no_delivery_or_persistence_inputs(self):
        from briefforge.runtime import CandidatePresentationPackage

        forbidden_terms = {
            "renderer",
            "render",
            "browser",
            "template",
            "html",
            "dom",
            "css",
            "visualization",
            "visualisation",
            "chart",
            "map",
            "dashboard",
            "export",
            "api",
            "network",
            "persistence",
            "database",
            "path",
            "file",
            "storage",
            "serialization",
            "serialized",
            "ui",
        }
        field_names = {field_name.lower() for field_name in CandidatePresentationPackage.__dataclass_fields__}
        for forbidden in forbidden_terms:
            self.assertFalse(
                any(forbidden in field_name for field_name in field_names),
                f"CandidatePresentationPackage fingerprint input leaks excluded assumption {forbidden!r}",
            )


if __name__ == "__main__":
    unittest.main()
