"""Tests for the downstream consumption boundary proof.

These tests cover semantic boundary access only. They must not require rendering,
serialization, HTML, browser behavior, templates, APIs, persistence, networking,
visualization, exports, portal logic, dashboards, search, maps, or renderer
ownership.
"""

from copy import deepcopy
from dataclasses import FrozenInstanceError, fields, is_dataclass
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
TESTS = PROJECT_ROOT / "tests"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(TESTS))

from test_constitutional_validation import valid_candidate_package  # noqa: E402


def ready_package():
    from briefforge.promotion import promote_candidate_presentation_package
    from briefforge.validation import validate_candidate_presentation_package

    candidate = valid_candidate_package()
    judgment = validate_candidate_presentation_package(candidate)
    return promote_candidate_presentation_package(candidate, judgment)


class DownstreamBoundaryTests(unittest.TestCase):
    def test_ready_package_can_cross_downstream_boundary(self):
        from briefforge.downstream import (
            DownstreamSemanticPackage,
            prepare_downstream_semantic_package,
        )

        ready = ready_package()

        downstream_package = prepare_downstream_semantic_package(ready)

        self.assertIsInstance(downstream_package, DownstreamSemanticPackage)
        self.assertEqual(downstream_package.ready_package, ready)
        self.assertEqual(downstream_package.identity, ready.candidate.identity)
        self.assertEqual(downstream_package.organizing_purpose, ready.candidate.organizing_purpose)
        self.assertEqual(downstream_package.statements, ready.candidate.statements)
        self.assertEqual(downstream_package.upstream_references, ready.candidate.upstream_references)
        self.assertEqual(downstream_package.obligations, ready.candidate.obligations)
        self.assertEqual(downstream_package.validation_judgment, ready.validation_judgment)

    def test_candidate_package_cannot_cross_downstream_boundary(self):
        from briefforge.downstream import DownstreamBoundaryRejected, prepare_downstream_semantic_package

        candidate = valid_candidate_package()

        with self.assertRaises(DownstreamBoundaryRejected):
            prepare_downstream_semantic_package(candidate)

    def test_invalid_or_failed_promotion_cannot_cross_downstream_boundary(self):
        from briefforge.downstream import DownstreamBoundaryRejected, prepare_downstream_semantic_package
        from briefforge.promotion import PromotionRejected, promote_candidate_presentation_package
        from briefforge.runtime import CandidatePresentationPackage
        from briefforge.validation import validate_candidate_presentation_package

        candidate = valid_candidate_package()
        invalid_candidate = CandidatePresentationPackage(
            identity=None,
            organizing_purpose=candidate.organizing_purpose,
            statements=candidate.statements,
            upstream_references=candidate.upstream_references,
            obligations=candidate.obligations,
        )
        invalid_judgment = validate_candidate_presentation_package(invalid_candidate)

        with self.assertRaises(PromotionRejected) as failed_promotion:
            promote_candidate_presentation_package(candidate, invalid_judgment)

        with self.assertRaises(DownstreamBoundaryRejected):
            prepare_downstream_semantic_package(invalid_judgment)
        with self.assertRaises(DownstreamBoundaryRejected):
            prepare_downstream_semantic_package(failed_promotion.exception)

    def test_downstream_consumption_does_not_mutate_ready_package(self):
        from briefforge.downstream import prepare_downstream_semantic_package

        ready = ready_package()
        before = deepcopy(ready)

        prepare_downstream_semantic_package(ready)

        self.assertEqual(ready, before)

    def test_downstream_consumption_cannot_alter_semantic_package_or_judgment(self):
        from briefforge.downstream import prepare_downstream_semantic_package

        downstream_package = prepare_downstream_semantic_package(ready_package())

        with self.assertRaises(FrozenInstanceError):
            downstream_package.ready_package = None
        with self.assertRaises(FrozenInstanceError):
            downstream_package.identity.title = "Downstream rewrite"
        with self.assertRaises(FrozenInstanceError):
            downstream_package.validation_judgment.valid = False

    def test_downstream_package_has_no_rendering_delivery_or_authority_fields(self):
        from briefforge.downstream import DownstreamSemanticPackage

        self.assertTrue(is_dataclass(DownstreamSemanticPackage))
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
            "search",
            "authority",
            "authoritative",
            "mutate",
            "write",
            "promote",
            "validate",
        }
        field_names = {field.name.lower() for field in fields(DownstreamSemanticPackage)}
        for forbidden in forbidden_terms:
            self.assertFalse(
                any(forbidden in field_name for field_name in field_names),
                f"DownstreamSemanticPackage leaks excluded assumption {forbidden!r}",
            )


if __name__ == "__main__":
    unittest.main()
