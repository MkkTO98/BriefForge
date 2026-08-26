"""TASK-014 end-to-end proof using one realistic economic presentation.

This test exercises the already implemented BriefForge workflow without adding
new runtime concepts, renderer behavior, templates, browser code, dashboards,
visualizations, APIs, or persistence.
"""

from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
TESTS = PROJECT_ROOT / "tests"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(TESTS))

ARTIFACT_DIR = PROJECT_ROOT / "artifacts" / "presentations" / "TASK-014-denmark-country-profile"


def denmark_country_profile_candidate():
    """Return the TASK-014 Denmark profile through the Country Profile Presentation Model.

    TASK-017 migrated the helper away from manual runtime dataclass construction.
    The resulting Candidate Presentation Package remains semantically equivalent
    to the original TASK-014 artifact.
    """

    from test_country_profile_presentation_model import denmark_country_profile_model_candidate

    return denmark_country_profile_model_candidate()


class FirstRealPresentationEndToEndProofTests(unittest.TestCase):
    def test_realistic_denmark_profile_crosses_existing_pipeline(self):
        from briefforge.promotion import ReadyPresentationPackage, promote_candidate_presentation_package
        from briefforge.renderer_adapter import (
            HtmlRenderedArtifact,
            RenderedArtifactConformance,
            check_rendered_artifact_conformance,
            check_renderer_adapter_compatibility,
            html_renderer_contract,
            invoke_renderer_adapter,
            render_minimal_html,
        )
        from briefforge.validation import ValidationJudgment, validate_candidate_presentation_package

        candidate = denmark_country_profile_candidate()
        judgment = validate_candidate_presentation_package(candidate)
        ready = promote_candidate_presentation_package(candidate, judgment)
        contract = html_renderer_contract()
        compatibility = check_renderer_adapter_compatibility(ready, contract)
        invocation_result = invoke_renderer_adapter(ready, contract)
        artifact = render_minimal_html(ready, contract)
        conformance = check_rendered_artifact_conformance(ready, artifact)

        self.assertTrue(judgment.valid, judgment.findings)
        self.assertIsInstance(judgment, ValidationJudgment)
        self.assertIsInstance(ready, ReadyPresentationPackage)
        self.assertTrue(compatibility.compatible)
        self.assertTrue(invocation_result.accepted)
        self.assertIsInstance(artifact, HtmlRenderedArtifact)
        self.assertIsInstance(conformance, RenderedArtifactConformance)
        self.assertTrue(conformance.conforms, conformance.findings)
        self.assertIn("Denmark", artifact.html)
        self.assertIn("ageing", artifact.html)
        self.assertIn("Energy transition", artifact.html)
        self.assertNotIn("<script", artifact.html.lower())
        self.assertIn("<style", artifact.html.lower())
        self.assertIn("data-reader-experience=\"static-v0.3\"", artifact.html.lower())

    def test_task_014_deliverable_files_exist_after_artifact_generation(self):
        expected_files = (
            "candidate_presentation_package.json",
            "validation_judgment.json",
            "ready_presentation_package.json",
            "minimal_html_artifact.html",
            "rendered_artifact_conformance.json",
            "workflow_observations.md",
        )

        missing = tuple(name for name in expected_files if not (ARTIFACT_DIR / name).is_file())

        self.assertEqual(missing, ())


if __name__ == "__main__":
    unittest.main()
