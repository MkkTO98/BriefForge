"""TASK-031 renderer-side source-structure preservation tests.

These tests use the existing TASK-023 large InsightForge report only. They prove
that the renderer preserves author-provided document structure without changing
runtime, Presentation Package, Presentation Grammar, validation, promotion, or
Presentation Models.
"""

from dataclasses import fields
import sys
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

from tests.test_large_report_stress_validation import large_report_candidate_package


class SourceStructurePreservationTests(unittest.TestCase):
    def _render_large_report(self):
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.renderer_adapter import (
            check_rendered_artifact_conformance,
            html_renderer_contract,
            render_minimal_html,
        )
        from briefforge.validation import validate_candidate_presentation_package

        candidate = large_report_candidate_package()
        judgment = validate_candidate_presentation_package(candidate)
        ready = promote_candidate_presentation_package(candidate, judgment)
        artifact = render_minimal_html(ready, html_renderer_contract())
        conformance = check_rendered_artifact_conformance(ready, artifact)
        return candidate, ready, artifact, conformance

    def test_existing_renderer_preserves_author_headings_from_task_023(self):
        candidate, _ready, artifact, _conformance = self._render_large_report()
        html = artifact.html

        self.assertIn("data-source-structure=\"preserved-v0.1\"", html)
        self.assertIn(">Restated hypothesis</h4>", html)
        self.assertIn(">Supporting findings</h4>", html)
        self.assertIn(">Missing evidence</h4>", html)
        self.assertIn(">Why not accepted</h4>", html)
        self.assertLess(
            html.index("Restated hypothesis"),
            html.index("Supporting findings"),
        )
        self.assertEqual(
            tuple(statement.statement_id for statement in candidate.statements),
            tuple(
                statement_id.split('"')[0]
                for statement_id in html.split('data-statement-id="')[1:]
            ),
        )

    def test_existing_renderer_preserves_nested_lists_from_task_023_scope(self):
        _candidate, _ready, artifact, _conformance = self._render_large_report()
        html = artifact.html

        self.assertIn("<ul data-source-list=\"unordered\">", html)
        self.assertIn("<ul data-source-list=\"unordered-nested\">", html)
        self.assertIn("Existing reviewed finding artifacts", html)
        self.assertIn("IF-A-20260619-001-wdi-usa-dnk-gdp-direction.md", html)
        self.assertLess(
            html.index("Existing reviewed finding artifacts"),
            html.index("IF-A-20260619-001-wdi-usa-dnk-gdp-direction.md"),
        )

    def test_existing_renderer_preserves_table_markup_where_task_023_contains_tables(self):
        _candidate, _ready, artifact, _conformance = self._render_large_report()
        html = artifact.html

        self.assertIn("data-source-tables=\"absent\"", html)
        self.assertNotIn("<table", html.lower())
        self.assertNotIn("|---", html)

    def test_existing_renderer_preserves_warning_caveat_methodology_and_recommendation_blocks(self):
        _candidate, _ready, artifact, _conformance = self._render_large_report()
        html = artifact.html

        self.assertIn('data-source-block="caveat"', html)
        self.assertIn('data-source-block="methodology"', html)
        self.assertIn('data-source-block="recommendation"', html)
        self.assertIn("Why not accepted", html)
        self.assertIn("Controlled hypothesis pressure test", html)
        self.assertIn("Recommendation", html)

    def test_source_structure_preservation_keeps_conformance_and_runtime_unchanged(self):
        from briefforge.runtime import CandidatePresentationPackage, PresentationStatement
        import briefforge.runtime as runtime
        from briefforge.presentation_models import (
            CountryComparisonPresentation,
            CountryProfilePresentation,
            InvestmentThesisPresentation,
        )

        candidate, ready, artifact, conformance = self._render_large_report()

        self.assertTrue(conformance.conforms, conformance.findings)
        self.assertEqual(ready.semantic_fingerprint, artifact.semantic_fingerprint)
        self.assertFalse(hasattr(runtime, "SourceStructureBlock"))
        self.assertFalse(hasattr(runtime, "RenderedStructureNode"))
        self.assertFalse(hasattr(runtime, "MarkdownDocument"))
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
