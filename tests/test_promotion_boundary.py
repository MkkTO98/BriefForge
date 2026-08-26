"""Tests for promotion from Candidate to Ready Presentation Package.

These tests cover the promotion boundary only. They must not require validation to
run inside promotion, rendering, serialization, HTML, browser behavior,
templates, APIs, persistence, networking, visualization, exports, portal logic,
or downstream consumers.
"""

from copy import deepcopy
from dataclasses import fields, is_dataclass
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
TESTS = PROJECT_ROOT / "tests"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(TESTS))

from test_constitutional_validation import valid_candidate_package  # noqa: E402


class PromotionBoundaryTests(unittest.TestCase):
    def test_valid_candidate_plus_successful_judgment_becomes_ready_package(self):
        from briefforge.promotion import ReadyPresentationPackage, promote_candidate_presentation_package
        from briefforge.validation import validate_candidate_presentation_package

        candidate = valid_candidate_package()
        judgment = validate_candidate_presentation_package(candidate)

        ready_package = promote_candidate_presentation_package(candidate, judgment)

        self.assertIsInstance(ready_package, ReadyPresentationPackage)
        self.assertEqual(ready_package.candidate, candidate)
        self.assertEqual(ready_package.validation_judgment, judgment)
        self.assertIsNot(ready_package, candidate)
        self.assertIsNot(ready_package, judgment)

    def test_invalid_judgment_cannot_promote_candidate(self):
        from briefforge.promotion import PromotionRejected, promote_candidate_presentation_package
        from briefforge.validation import validate_candidate_presentation_package
        from briefforge.runtime import CandidatePresentationPackage

        candidate = valid_candidate_package()
        invalid_candidate = CandidatePresentationPackage(
            identity=None,
            organizing_purpose=candidate.organizing_purpose,
            statements=candidate.statements,
            upstream_references=candidate.upstream_references,
            obligations=candidate.obligations,
        )
        invalid_judgment = validate_candidate_presentation_package(invalid_candidate)

        with self.assertRaises(PromotionRejected):
            promote_candidate_presentation_package(candidate, invalid_judgment)

    def test_judgment_for_different_candidate_cannot_promote_this_candidate(self):
        from briefforge.promotion import PromotionRejected, promote_candidate_presentation_package
        from briefforge.validation import validate_candidate_presentation_package
        from briefforge.runtime import CandidatePresentationPackage, PackageIdentity

        candidate = valid_candidate_package()
        other_candidate = CandidatePresentationPackage(
            identity=PackageIdentity(
                package_id="bf-candidate-other",
                title=candidate.identity.title,
                purpose_summary=candidate.identity.purpose_summary,
                scope=candidate.identity.scope,
                non_scope=candidate.identity.non_scope,
            ),
            organizing_purpose=candidate.organizing_purpose,
            statements=candidate.statements,
            upstream_references=candidate.upstream_references,
            obligations=candidate.obligations,
        )
        other_judgment = validate_candidate_presentation_package(other_candidate)

        self.assertTrue(other_judgment.valid)
        with self.assertRaises(PromotionRejected):
            promote_candidate_presentation_package(candidate, other_judgment)

    def test_promotion_does_not_mutate_candidate(self):
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.validation import validate_candidate_presentation_package

        candidate = valid_candidate_package()
        before = deepcopy(candidate)
        judgment = validate_candidate_presentation_package(candidate)

        promote_candidate_presentation_package(candidate, judgment)

        self.assertEqual(candidate, before)

    def test_ready_package_has_no_rendering_or_delivery_fields(self):
        from briefforge.promotion import ReadyPresentationPackage

        self.assertTrue(is_dataclass(ReadyPresentationPackage))
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
            "route",
            "portal",
            "delivery",
            "consumer",
        }
        field_names = {field.name.lower() for field in fields(ReadyPresentationPackage)}
        for forbidden in forbidden_terms:
            self.assertFalse(
                any(forbidden in field_name for field_name in field_names),
                f"ReadyPresentationPackage leaks excluded assumption {forbidden!r}",
            )


if __name__ == "__main__":
    unittest.main()
