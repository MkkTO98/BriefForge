"""Tests for renderer-output conformance boundary.

These tests cover only downstream conformance checking of rendered artifacts
against Ready Presentation Package audit metadata. They must not require HTML,
PDF, browser output, templates, charts, maps, visualization, exports,
persistence, APIs, networking, portal behavior, dashboard behavior, search, UI
components, renderer registries, or plugin architecture.
"""

from copy import deepcopy
from dataclasses import fields, is_dataclass, replace
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
TESTS = PROJECT_ROOT / "tests"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(TESTS))

from test_renderer_adapter_boundary import ready_package  # noqa: E402


class RenderedArtifactConformanceTests(unittest.TestCase):
    def test_toy_rendered_artifact_conforming_to_ready_package_passes(self):
        from briefforge.renderer_adapter import (
            RenderedArtifactConformance,
            check_rendered_artifact_conformance,
            render_toy_plain_text,
        )

        ready = ready_package()
        artifact = render_toy_plain_text(ready)

        conformance = check_rendered_artifact_conformance(ready, artifact)

        self.assertIsInstance(conformance, RenderedArtifactConformance)
        self.assertTrue(conformance.conforms)
        self.assertEqual(conformance.findings, ())
        self.assertEqual(conformance.adapter_identity, artifact.adapter_identity)
        self.assertEqual(conformance.package_identity, ready.candidate.identity)
        self.assertEqual(conformance.semantic_fingerprint, ready.semantic_fingerprint)
        self.assertEqual(conformance.validation_policy_id, ready.validation_policy_id)

    def test_artifact_with_wrong_package_identity_fails(self):
        from briefforge.renderer_adapter import check_rendered_artifact_conformance, render_toy_plain_text
        from briefforge.runtime import PackageIdentity

        ready = ready_package()
        artifact = render_toy_plain_text(ready)
        wrong_identity_artifact = replace(
            artifact,
            package_identity=PackageIdentity(
                package_id="wrong-package",
                title="Wrong Package",
                purpose_summary="Wrong package identity for conformance test.",
                scope="Mismatch proof.",
                non_scope="No rendering architecture.",
            ),
        )

        conformance = check_rendered_artifact_conformance(ready, wrong_identity_artifact)

        self.assertFalse(conformance.conforms)
        self.assertIn("package_identity", conformance.findings)

    def test_artifact_with_wrong_semantic_fingerprint_fails(self):
        from briefforge.renderer_adapter import check_rendered_artifact_conformance, render_toy_plain_text

        ready = ready_package()
        artifact = render_toy_plain_text(ready)
        wrong_fingerprint_artifact = replace(artifact, semantic_fingerprint="wrong-fingerprint")

        conformance = check_rendered_artifact_conformance(ready, wrong_fingerprint_artifact)

        self.assertFalse(conformance.conforms)
        self.assertIn("semantic_fingerprint", conformance.findings)

    def test_artifact_with_wrong_validation_policy_identity_fails(self):
        from briefforge.renderer_adapter import check_rendered_artifact_conformance, render_toy_plain_text

        ready = ready_package()
        artifact = render_toy_plain_text(ready)
        wrong_policy_artifact = replace(artifact, validation_policy_id="wrong-validation-policy")

        conformance = check_rendered_artifact_conformance(ready, wrong_policy_artifact)

        self.assertFalse(conformance.conforms)
        self.assertIn("validation_policy_id", conformance.findings)

    def test_malformed_artifact_fails(self):
        from briefforge.renderer_adapter import (
            RenderedArtifactConformanceRejected,
            check_rendered_artifact_conformance,
        )

        with self.assertRaises(RenderedArtifactConformanceRejected):
            check_rendered_artifact_conformance(ready_package(), object())

    def test_conformance_checking_does_not_mutate_ready_package_or_artifact(self):
        from briefforge.renderer_adapter import check_rendered_artifact_conformance, render_toy_plain_text

        ready = ready_package()
        artifact = render_toy_plain_text(ready)
        ready_before = deepcopy(ready)
        artifact_before = deepcopy(artifact)

        check_rendered_artifact_conformance(ready, artifact)

        self.assertEqual(ready, ready_before)
        self.assertEqual(artifact, artifact_before)

    def test_conformance_result_does_not_become_semantic_authority(self):
        from briefforge.promotion import ReadyPresentationPackage
        from briefforge.renderer_adapter import RenderedArtifactConformance, check_rendered_artifact_conformance, render_toy_plain_text
        from briefforge.runtime import CandidatePresentationPackage
        from briefforge.validation import ValidationJudgment

        result = check_rendered_artifact_conformance(ready_package(), render_toy_plain_text(ready_package()))

        self.assertTrue(is_dataclass(RenderedArtifactConformance))
        self.assertNotIsInstance(result, ReadyPresentationPackage)
        self.assertNotIsInstance(result, CandidatePresentationPackage)
        self.assertNotIsInstance(result, ValidationJudgment)
        self.assertFalse(hasattr(result, "candidate"))
        self.assertFalse(hasattr(result, "ready_package"))
        self.assertFalse(hasattr(result, "artifact"))
        self.assertFalse(hasattr(result, "statements"))
        self.assertFalse(hasattr(result, "organizing_purpose"))
        self.assertFalse(hasattr(result, "upstream_references"))
        self.assertFalse(hasattr(result, "obligations"))
        self.assertFalse(hasattr(result, "validation_judgment"))
        self.assertFalse(hasattr(result, "valid"))
        self.assertFalse(hasattr(result, "promote"))
        self.assertFalse(hasattr(result, "semantic_authority"))
        self.assertEqual(
            {field.name for field in fields(RenderedArtifactConformance)},
            {
                "conforms",
                "findings",
                "adapter_identity",
                "package_identity",
                "semantic_fingerprint",
                "validation_policy_id",
            },
        )


if __name__ == "__main__":
    unittest.main()
