"""Tests for the renderer-adapter boundary proof.

These tests cover only the boundary by which renderer adapters may receive a
Ready Presentation Package. They must not require actual rendering, HTML, PDF,
browser behavior, templates, visualization, charts, maps, exports, persistence,
APIs, networking, portal behavior, dashboard behavior, search, or UI components.
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


class RendererAdapterBoundaryTests(unittest.TestCase):
    def test_ready_package_can_cross_renderer_adapter_boundary(self):
        from briefforge.renderer_adapter import (
            RendererAdapterRequest,
            prepare_renderer_adapter_request,
        )

        ready = ready_package()

        request = prepare_renderer_adapter_request(ready)

        self.assertIsInstance(request, RendererAdapterRequest)
        self.assertEqual(request.ready_package, ready)

    def test_candidate_package_cannot_cross_renderer_adapter_boundary(self):
        from briefforge.renderer_adapter import RendererAdapterRejected, prepare_renderer_adapter_request

        with self.assertRaises(RendererAdapterRejected):
            prepare_renderer_adapter_request(valid_candidate_package())

    def test_invalid_promotion_objects_or_judgments_cannot_cross_renderer_adapter_boundary(self):
        from briefforge.renderer_adapter import RendererAdapterRejected, prepare_renderer_adapter_request
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

        with self.assertRaises(RendererAdapterRejected):
            prepare_renderer_adapter_request(invalid_judgment)
        with self.assertRaises(RendererAdapterRejected):
            prepare_renderer_adapter_request(failed_promotion.exception)

    def test_renderer_adapter_exposes_semantic_package_metadata_read_only(self):
        from briefforge.renderer_adapter import prepare_renderer_adapter_request

        ready = ready_package()
        request = prepare_renderer_adapter_request(ready)

        self.assertEqual(request.identity, ready.candidate.identity)
        self.assertEqual(request.organizing_purpose, ready.candidate.organizing_purpose)
        self.assertEqual(request.statements, ready.candidate.statements)
        self.assertEqual(request.upstream_references, ready.candidate.upstream_references)
        self.assertEqual(request.obligations, ready.candidate.obligations)
        self.assertEqual(request.semantic_fingerprint, ready.semantic_fingerprint)
        self.assertEqual(request.validation_policy_id, ready.validation_policy_id)
        self.assertEqual(request.validation_judgment, ready.validation_judgment)

        with self.assertRaises(FrozenInstanceError):
            request.ready_package = None
        with self.assertRaises(FrozenInstanceError):
            request.identity.title = "Renderer rewrite"
        with self.assertRaises(FrozenInstanceError):
            request.ready_package.semantic_fingerprint = "changed"
        with self.assertRaises(FrozenInstanceError):
            request.ready_package.validation_policy_id = "changed-policy"

    def test_renderer_adapter_boundary_does_not_mutate_ready_package(self):
        from briefforge.renderer_adapter import prepare_renderer_adapter_request

        ready = ready_package()
        before = deepcopy(ready)

        prepare_renderer_adapter_request(ready)

        self.assertEqual(ready, before)

    def test_renderer_adapter_boundary_does_not_create_rendered_output(self):
        from briefforge.renderer_adapter import RendererAdapterRequest, prepare_renderer_adapter_request

        request = prepare_renderer_adapter_request(ready_package())

        self.assertTrue(is_dataclass(RendererAdapterRequest))
        forbidden_output_terms = {
            "html",
            "pdf",
            "browser",
            "template",
            "visualization",
            "visualisation",
            "chart",
            "map",
            "export",
            "persistence",
            "database",
            "api",
            "network",
            "portal",
            "dashboard",
            "search",
            "ui",
            "component",
            "output",
            "artifact",
            "document",
            "rendered",
            "content",
        }
        field_names = {field.name.lower() for field in fields(RendererAdapterRequest)}
        property_names = {
            name.lower()
            for name, value in vars(RendererAdapterRequest).items()
            if isinstance(value, property)
        }
        exposed_names = field_names | property_names
        for forbidden in forbidden_output_terms:
            self.assertFalse(
                any(forbidden in exposed_name for exposed_name in exposed_names),
                f"RendererAdapterRequest leaks excluded output assumption {forbidden!r}",
            )
        for forbidden_attribute in ("rendered_output", "html", "pdf", "template", "export"):
            self.assertFalse(hasattr(request, forbidden_attribute))


if __name__ == "__main__":
    unittest.main()
