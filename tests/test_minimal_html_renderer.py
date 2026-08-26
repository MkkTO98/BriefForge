"""Tests for the deliberately tiny HTML renderer proof.

These tests cover only one bounded HTML renderer adapter that consumes a Ready
Presentation Package downstream and returns static browser-readable HTML plus
audit metadata. They must not require templates, CSS frameworks, JavaScript,
charts, maps, visualization, PDF, exports, persistence, APIs, networking,
portal behavior, dashboard behavior, UI component libraries, renderer
registries, or plugin architecture.
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
from test_renderer_adapter_boundary import ready_package  # noqa: E402


class MinimalHtmlRendererTests(unittest.TestCase):
    def test_ready_package_can_produce_bounded_html_artifact(self):
        from briefforge.renderer_adapter import (
            HtmlRenderedArtifact,
            html_renderer_contract,
            render_minimal_html,
        )

        ready = ready_package()
        contract = html_renderer_contract()

        artifact = render_minimal_html(ready, contract)

        self.assertIsInstance(artifact, HtmlRenderedArtifact)
        self.assertEqual(artifact.adapter_identity, contract.identity)
        self.assertEqual(artifact.package_identity, ready.candidate.identity)
        self.assertIsInstance(artifact.html, str)
        self.assertIn("<!doctype html>", artifact.html.lower())
        self.assertIn("<html", artifact.html.lower())
        self.assertIn("</html>", artifact.html.lower())
        self.assertIn(ready.candidate.identity.title, artifact.html)
        self.assertIn(ready.candidate.organizing_purpose.statement, artifact.html)
        self.assertIn(ready.candidate.statements[0].encounter_meaning, artifact.html)
        self.assertNotIn("<script", artifact.html.lower())
        self.assertIn("<style", artifact.html.lower())
        self.assertIn("data-reader-experience=\"static-v0.3\"", artifact.html.lower())

    def test_candidate_package_cannot_produce_html(self):
        from briefforge.renderer_adapter import RendererAdapterRejected, render_minimal_html

        with self.assertRaises(RendererAdapterRejected):
            render_minimal_html(valid_candidate_package())

    def test_incompatible_adapter_contract_cannot_produce_html(self):
        from briefforge.renderer_adapter import (
            RendererAdapterInvocationRejected,
            render_minimal_html,
            toy_plain_text_renderer_contract,
        )

        with self.assertRaises(RendererAdapterInvocationRejected):
            render_minimal_html(ready_package(), toy_plain_text_renderer_contract())

    def test_html_artifact_includes_audit_metadata(self):
        from briefforge.renderer_adapter import HtmlRenderedArtifact, html_renderer_contract, render_minimal_html

        ready = ready_package()
        contract = html_renderer_contract()
        artifact = render_minimal_html(ready, contract)

        self.assertTrue(is_dataclass(HtmlRenderedArtifact))
        self.assertEqual(
            {field.name for field in fields(HtmlRenderedArtifact)},
            {
                "html",
                "adapter_identity",
                "package_identity",
                "semantic_fingerprint",
                "validation_policy_id",
            },
        )
        self.assertEqual(artifact.adapter_identity, contract.identity)
        self.assertEqual(artifact.package_identity, ready.candidate.identity)
        self.assertEqual(artifact.semantic_fingerprint, ready.semantic_fingerprint)
        self.assertEqual(artifact.validation_policy_id, ready.validation_policy_id)
        self.assertIn(contract.identity.adapter_id, artifact.html)
        self.assertIn(ready.candidate.identity.package_id, artifact.html)
        self.assertIn(ready.semantic_fingerprint, artifact.html)
        self.assertIn(ready.validation_policy_id, artifact.html)

    def test_html_artifact_passes_rendered_artifact_conformance(self):
        from briefforge.renderer_adapter import check_rendered_artifact_conformance, render_minimal_html

        ready = ready_package()
        artifact = render_minimal_html(ready)

        conformance = check_rendered_artifact_conformance(ready, artifact)

        self.assertTrue(conformance.conforms)
        self.assertEqual(conformance.findings, ())
        self.assertEqual(conformance.adapter_identity, artifact.adapter_identity)
        self.assertEqual(conformance.package_identity, ready.candidate.identity)
        self.assertEqual(conformance.semantic_fingerprint, ready.semantic_fingerprint)
        self.assertEqual(conformance.validation_policy_id, ready.validation_policy_id)

    def test_html_rendering_does_not_mutate_ready_package(self):
        from briefforge.renderer_adapter import render_minimal_html

        ready = ready_package()
        before = deepcopy(ready)

        render_minimal_html(ready)

        self.assertEqual(ready, before)

    def test_html_output_does_not_become_semantic_authority(self):
        from briefforge.promotion import ReadyPresentationPackage
        from briefforge.renderer_adapter import HtmlRenderedArtifact, render_minimal_html
        from briefforge.runtime import CandidatePresentationPackage
        from briefforge.validation import ValidationJudgment

        artifact = render_minimal_html(ready_package())

        self.assertNotIsInstance(artifact, ReadyPresentationPackage)
        self.assertNotIsInstance(artifact, CandidatePresentationPackage)
        self.assertNotIsInstance(artifact, ValidationJudgment)
        self.assertFalse(hasattr(artifact, "candidate"))
        self.assertFalse(hasattr(artifact, "statements"))
        self.assertFalse(hasattr(artifact, "organizing_purpose"))
        self.assertFalse(hasattr(artifact, "upstream_references"))
        self.assertFalse(hasattr(artifact, "obligations"))
        self.assertFalse(hasattr(artifact, "validation_judgment"))
        self.assertFalse(hasattr(artifact, "valid"))
        self.assertFalse(hasattr(artifact, "promote"))
        self.assertFalse(hasattr(artifact, "semantic_authority"))
        self.assertEqual(
            {field.name for field in fields(HtmlRenderedArtifact)},
            {
                "html",
                "adapter_identity",
                "package_identity",
                "semantic_fingerprint",
                "validation_policy_id",
            },
        )


if __name__ == "__main__":
    unittest.main()
