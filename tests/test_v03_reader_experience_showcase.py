"""TASK-030 BriefForge v0.3 reader-experience showcase tests.

This task is a bounded reader-experience showcase. It may use renderer-level
readability improvements justified by RB-001, but must not modify runtime,
constitution, Presentation Grammar, Presentation Models, templates, browser
applications, dashboards, JavaScript, visualization systems, or CSS frameworks.
"""

from dataclasses import fields
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
TESTS = PROJECT_ROOT / "tests"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(TESTS))

from test_large_report_stress_validation import large_report_candidate_package  # noqa: E402

ARTIFACT_DIR = PROJECT_ROOT / "artifacts" / "presentations" / "TASK-030-briefforge-v0.3-reader-experience-showcase"
EXPECTED_FILES = (
    "selected_upstream_artifact.md",
    "ready_presentation_package.json",
    "validation_judgment.json",
    "briefforge_v0_3_reader_experience_showcase.html",
    "rendered_artifact_conformance.json",
    "renderer_audit_metadata.json",
    "browser_screenshot_record.md",
    "reader_evaluation.md",
    "professional_comparison.md",
    "remaining_user_visible_shortcomings.md",
)


def v03_ready_package():
    from briefforge.promotion import promote_candidate_presentation_package
    from briefforge.validation import validate_candidate_presentation_package

    candidate = large_report_candidate_package()
    judgment = validate_candidate_presentation_package(candidate)
    return promote_candidate_presentation_package(candidate, judgment)


class V03ReaderExperienceShowcaseTests(unittest.TestCase):
    def test_selected_showcase_uses_existing_large_analytical_artifact_without_new_analysis(self):
        ready = v03_ready_package()

        self.assertEqual(ready.candidate.identity.package_id, "briefforge-task-023-large-report-stress-validation")
        self.assertIn("InsightForge hypothesis validation pressure test", ready.candidate.identity.title)
        self.assertGreaterEqual(len(ready.candidate.statements), 25)
        self.assertGreaterEqual(len(ready.candidate.upstream_references), 5)
        self.assertIn("No new analysis", ready.candidate.identity.non_scope)

    def test_renderer_includes_static_reader_experience_styles_without_becoming_browser_app(self):
        from briefforge.renderer_adapter import render_minimal_html

        html = render_minimal_html(v03_ready_package()).html
        lowered = html.lower()

        self.assertIn("<style>", lowered)
        self.assertIn("max-width:", lowered)
        self.assertIn("line-height:", lowered)
        self.assertIn("font-family:", lowered)
        self.assertIn("data-reader-experience=\"static-v0.3\"", lowered)
        self.assertIn("data-grammar=\"presentation-grammar-v1\"", lowered)
        self.assertNotIn("<script", lowered)
        self.assertNotIn("bootstrap", lowered)
        self.assertNotIn("tailwind", lowered)
        self.assertNotIn("react", lowered)
        self.assertNotIn("data-template", lowered)
        self.assertNotIn("data-dashboard", lowered)
        self.assertNotIn("data-portal", lowered)
        self.assertNotIn("<canvas", lowered)
        self.assertNotIn("<svg", lowered)
        self.assertNotIn("fetch(", lowered)

    def test_renderer_level_polish_preserves_existing_semantics_and_conformance(self):
        from briefforge.renderer_adapter import check_rendered_artifact_conformance, render_minimal_html
        from briefforge.runtime import CandidatePresentationPackage, PresentationStatement, UpstreamReference
        from briefforge.presentation_models import CountryComparisonPresentation, CountryProfilePresentation, InvestmentThesisPresentation

        ready = v03_ready_package()
        artifact = render_minimal_html(ready)
        conformance = check_rendered_artifact_conformance(ready, artifact)

        self.assertTrue(conformance.conforms, conformance.findings)
        self.assertEqual(artifact.package_identity, ready.candidate.identity)
        self.assertEqual(artifact.semantic_fingerprint, ready.semantic_fingerprint)
        self.assertEqual(artifact.validation_policy_id, ready.validation_policy_id)
        self.assertEqual(tuple(field.name for field in fields(CandidatePresentationPackage)), ("identity", "organizing_purpose", "statements", "upstream_references", "obligations"))
        self.assertEqual(tuple(field.name for field in fields(PresentationStatement)), ("statement_id", "encounter_meaning", "belongs_to_purpose", "encounter_semantics", "upstream_reference_ids", "obligation_ids"))
        self.assertEqual(tuple(field.name for field in fields(UpstreamReference)), ("reference_id", "owning_project", "reference_kind", "locator", "owned_meaning"))
        self.assertEqual(tuple(field.name for field in fields(CountryProfilePresentation)), ("country_name", "candidate"))
        self.assertEqual(tuple(field.name for field in fields(CountryComparisonPresentation)), ("compared_countries", "candidate"))
        self.assertEqual(tuple(field.name for field in fields(InvestmentThesisPresentation)), ("subject", "candidate"))

    def test_task_030_showcase_deliverables_exist(self):
        missing = tuple(name for name in EXPECTED_FILES if not (ARTIFACT_DIR / name).is_file())
        self.assertEqual(missing, ())


if __name__ == "__main__":
    unittest.main()
