"""Tests for the deliberately bounded toy plain-text renderer proof.

These tests cover only one non-general renderer adapter that consumes a Ready
Presentation Package through the renderer-adapter boundary and returns bounded
plain text plus audit metadata. They must not require HTML, PDF, browser output,
templates, charts, maps, visualization, exports, persistence, APIs, networking,
portal behavior, dashboard behavior, search, or UI components.
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


class ToyPlainTextRendererTests(unittest.TestCase):
    def test_ready_package_can_be_rendered_by_toy_plain_text_renderer(self):
        from briefforge.renderer_adapter import (
            ToyPlainTextRenderedArtifact,
            render_toy_plain_text,
            toy_plain_text_renderer_contract,
        )

        ready = ready_package()
        contract = toy_plain_text_renderer_contract()

        artifact = render_toy_plain_text(ready, contract)

        self.assertIsInstance(artifact, ToyPlainTextRenderedArtifact)
        self.assertEqual(artifact.adapter_identity, contract.identity)
        self.assertEqual(artifact.package_identity, ready.candidate.identity)
        self.assertIn(ready.candidate.identity.title, artifact.plain_text)
        self.assertIn(ready.candidate.organizing_purpose.statement, artifact.plain_text)
        self.assertIn(ready.candidate.statements[0].encounter_meaning, artifact.plain_text)

    def test_candidate_package_cannot_be_rendered(self):
        from briefforge.renderer_adapter import RendererAdapterRejected, render_toy_plain_text

        with self.assertRaises(RendererAdapterRejected):
            render_toy_plain_text(valid_candidate_package())

    def test_incompatible_adapter_contract_cannot_render(self):
        from briefforge.renderer_adapter import (
            RendererAdapterCapability,
            RendererAdapterContract,
            RendererAdapterIdentity,
            RendererAdapterInvocationRejected,
            render_toy_plain_text,
        )

        incompatible_contract = RendererAdapterContract(
            identity=RendererAdapterIdentity(
                adapter_id="not-the-toy-renderer",
                name="Not The Toy Renderer",
                version="0.1.0",
                owner="BriefForge renderer tests",
            ),
            capabilities=(
                RendererAdapterCapability(
                    capability_id="unsupported-renderer-need",
                    description="Requires an unsupported package feature.",
                    package_features=("unsupported_feature",),
                ),
            ),
        )

        with self.assertRaises(RendererAdapterInvocationRejected):
            render_toy_plain_text(ready_package(), incompatible_contract)

    def test_rendered_output_contains_only_bounded_plain_output_and_audit_metadata(self):
        from briefforge.renderer_adapter import ToyPlainTextRenderedArtifact, render_toy_plain_text

        ready = ready_package()
        artifact = render_toy_plain_text(ready)

        self.assertTrue(is_dataclass(ToyPlainTextRenderedArtifact))
        self.assertEqual(
            {field.name for field in fields(ToyPlainTextRenderedArtifact)},
            {
                "plain_text",
                "adapter_identity",
                "package_identity",
                "semantic_fingerprint",
                "validation_policy_id",
            },
        )
        self.assertIsInstance(artifact.plain_text, str)
        self.assertNotIn("<html", artifact.plain_text.lower())
        self.assertNotIn("<body", artifact.plain_text.lower())
        self.assertNotIn("```", artifact.plain_text)
        self.assertEqual(artifact.semantic_fingerprint, ready.semantic_fingerprint)
        self.assertEqual(artifact.validation_policy_id, ready.validation_policy_id)

    def test_rendering_does_not_mutate_ready_package(self):
        from briefforge.renderer_adapter import render_toy_plain_text

        ready = ready_package()
        before = deepcopy(ready)

        render_toy_plain_text(ready)

        self.assertEqual(ready, before)

    def test_renderer_output_does_not_become_semantic_authority(self):
        from briefforge.promotion import ReadyPresentationPackage
        from briefforge.renderer_adapter import render_toy_plain_text
        from briefforge.runtime import CandidatePresentationPackage
        from briefforge.validation import ValidationJudgment

        artifact = render_toy_plain_text(ready_package())

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


if __name__ == "__main__":
    unittest.main()
