"""TASK-032 renderer-side static Exhibit tests.

These tests prove that BriefForge can add bounded static evidence exhibits from
existing Presentation Package semantics without changing the frozen runtime,
Presentation Grammar, validation, promotion, or conformance architecture.
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

from test_communication_intent_experiment import candidate_from_json  # noqa: E402
from tests.test_large_report_stress_validation import large_report_candidate_package  # noqa: E402

TASK_031_HTML = (
    PROJECT_ROOT
    / "artifacts"
    / "presentations"
    / "TASK-031-renderer-source-structure-preservation"
    / "briefforge_v0_4_source_structure_preservation.html"
)
TASK_026_GDP_PACKAGE = (
    PROJECT_ROOT
    / "artifacts"
    / "presentations"
    / "TASK-026-operational-publication-trial"
    / "pub-02-macroforge-canonical-gdp-snapshot"
    / "candidate_presentation_package.json"
)


class StaticExhibitRendererTests(unittest.TestCase):
    def _render_candidate(self, candidate):
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.renderer_adapter import (
            check_rendered_artifact_conformance,
            html_renderer_contract,
            render_minimal_html,
        )
        from briefforge.validation import validate_candidate_presentation_package

        judgment = validate_candidate_presentation_package(candidate)
        ready = promote_candidate_presentation_package(candidate, judgment)
        artifact = render_minimal_html(ready, html_renderer_contract())
        conformance = check_rendered_artifact_conformance(ready, artifact)
        return ready, artifact, conformance

    def test_task_031_baseline_contains_no_renderer_exhibits_but_task_032_render_inserts_them(self):
        baseline_html = TASK_031_HTML.read_text()
        self.assertNotIn('data-renderer-exhibit="static-v0.1"', baseline_html)

        _ready, artifact, _conformance = self._render_candidate(candidate_from_json(TASK_026_GDP_PACKAGE))
        html = artifact.html

        self.assertIn('data-renderer-exhibit="static-v0.1"', html)
        self.assertIn('data-exhibit-type="key-number"', html)
        self.assertIn('data-exhibit-type="small-statistical-table"', html)
        self.assertIn('data-exhibit-type="comparison-table"', html)
        self.assertIn('data-exhibit-source-statement="stmt-macroforge-gdp-snapshot-01-coverage"', html)
        self.assertIn('data-exhibit-source-statement="stmt-macroforge-gdp-snapshot-05-gdp-observations"', html)

    def test_static_exhibits_preserve_semantic_ordering_and_conformance(self):
        candidate = candidate_from_json(TASK_026_GDP_PACKAGE)
        ready, artifact, conformance = self._render_candidate(candidate)
        html = artifact.html

        self.assertTrue(conformance.conforms, conformance.findings)
        self.assertEqual(ready.semantic_fingerprint, artifact.semantic_fingerprint)
        rendered_order = tuple(
            statement_id.split('"')[0]
            for statement_id in html.split('data-statement-id="')[1:]
        )
        self.assertEqual(tuple(statement.statement_id for statement in candidate.statements), rendered_order)
        self.assertLess(
            html.index('data-statement-id="stmt-macroforge-gdp-snapshot-01-coverage"'),
            html.index('data-statement-id="stmt-macroforge-gdp-snapshot-05-gdp-observations"'),
        )

    def test_exhibit_inference_is_bounded_to_existing_evidence_and_avoids_scripts_or_browser_app_behavior(self):
        _ready, artifact, _conformance = self._render_candidate(candidate_from_json(TASK_026_GDP_PACKAGE))
        html = artifact.html.lower()

        self.assertIn('data-exhibit-inference="renderer-side-existing-evidence"', html)
        self.assertIn('data-exhibit-policy="no-runtime-object"', html)
        self.assertNotIn('<script', html)
        self.assertNotIn('onclick=', html)
        self.assertNotIn('onchange=', html)
        self.assertNotIn('dashboard', html)
        self.assertNotIn('portal', html)
        self.assertNotIn('chart.js', html)
        self.assertNotIn('d3.', html)
        self.assertNotIn('canvas', html)
        self.assertNotIn('svg', html)

    def test_large_task_023_report_does_not_fabricate_exhibits_when_evidence_is_not_structured_for_them(self):
        _ready, artifact, conformance = self._render_candidate(large_report_candidate_package())
        html = artifact.html

        self.assertTrue(conformance.conforms, conformance.findings)
        self.assertIn('data-exhibit-region="none-detected"', html)
        self.assertNotIn('<aside data-renderer-exhibit="static-v0.1"', html)

    def test_static_exhibits_do_not_expand_runtime_or_presentation_models(self):
        import briefforge.runtime as runtime
        from briefforge.runtime import CandidatePresentationPackage, PresentationStatement
        from briefforge.presentation_models import (
            CountryComparisonPresentation,
            CountryProfilePresentation,
            InvestmentThesisPresentation,
        )

        self.assertFalse(hasattr(runtime, "Exhibit"))
        self.assertFalse(hasattr(runtime, "RendererExhibit"))
        self.assertFalse(hasattr(runtime, "ChartSpec"))
        self.assertFalse(hasattr(runtime, "VisualizationSpec"))
        self.assertEqual(
            tuple(field.name for field in fields(CandidatePresentationPackage)),
            ("identity", "organizing_purpose", "statements", "upstream_references", "obligations"),
        )
        self.assertEqual(
            tuple(field.name for field in fields(PresentationStatement)),
            (
                "statement_id",
                "encounter_meaning",
                "belongs_to_purpose",
                "encounter_semantics",
                "upstream_reference_ids",
                "obligation_ids",
            ),
        )
        self.assertEqual(tuple(field.name for field in fields(CountryProfilePresentation)), ("country_name", "candidate"))
        self.assertEqual(tuple(field.name for field in fields(CountryComparisonPresentation)), ("compared_countries", "candidate"))
        self.assertEqual(tuple(field.name for field in fields(InvestmentThesisPresentation)), ("subject", "candidate"))


if __name__ == "__main__":
    unittest.main()
