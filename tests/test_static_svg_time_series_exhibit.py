"""TASK-033 renderer-side static SVG time-series exhibit tests.

These tests prove one bounded visualization class: a static SVG line chart for
existing source-supported time-series evidence. They deliberately keep the
exhibit downstream and non-canonical.
"""

from dataclasses import fields
from pathlib import Path
import json
import re
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
TESTS = PROJECT_ROOT / "tests"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(TESTS))

from test_communication_intent_experiment import candidate_from_json  # noqa: E402
from tests.test_large_report_stress_validation import large_report_candidate_package  # noqa: E402

from briefforge.runtime import (  # noqa: E402
    CandidatePresentationPackage,
    EncounterSemantics,
    OrganizingPurpose,
    PackageIdentity,
    PresentationObligation,
    PresentationStatement,
    UpstreamReference,
)

TASK_032_HTML = (
    PROJECT_ROOT
    / "artifacts"
    / "presentations"
    / "TASK-032-static-exhibit-renderer-proof"
    / "briefforge_v0_5_static_exhibit_renderer_proof.html"
)
TASK_026_GDP_PACKAGE = (
    PROJECT_ROOT
    / "artifacts"
    / "presentations"
    / "TASK-026-operational-publication-trial"
    / "pub-02-macroforge-canonical-gdp-snapshot"
    / "candidate_presentation_package.json"
)
MACROFORGE_BLS_NORMALIZED = (
    PROJECT_ROOT.parents[0]
    / "MacroForge"
    / "data"
    / "processed"
    / "bls_labor_core_operational"
    / "bls-labor-core-operational-normalized.json"
)


def _bls_time_series_candidate() -> CandidatePresentationPackage:
    """Build a package from existing MacroForge BLS time-series evidence."""

    source = json.loads(MACROFORGE_BLS_NORMALIZED.read_text())
    rows = [
        row
        for row in source["rows"]
        if row["series_id"] == "LNS14000000" and row["period_year"] == 2024
    ][:12]
    table_rows = ["| Period | Value | Unit |", "| --- | --- | --- |"]
    table_rows.extend(
        f"| {row['provider_period_code']} | {row['value']} | {row['unit_label']} |"
        for row in rows
    )
    source_table = "\n".join(table_rows)
    statement_id = "stmt-task-033-bls-unemployment-rate-2024"
    reference_id = "ref-macroforge-bls-labor-core-operational"
    obligation_id = "obligation-task-033-source-owned-evidence"
    return CandidatePresentationPackage(
        identity=PackageIdentity(
            package_id="briefforge-task-033-bls-unemployment-static-svg-proof",
            title="TASK-033 BLS Unemployment Time-Series Exhibit Proof",
            purpose_summary="Renderer-side proof using existing MacroForge BLS monthly unemployment evidence.",
            scope="Static HTML rendering proof for one time-series exhibit class.",
            non_scope="No runtime exhibit object, chart framework, JavaScript, dashboard, portal, map, or visualization engine.",
        ),
        organizing_purpose=OrganizingPurpose(
            statement="Show whether existing monthly unemployment-rate evidence benefits from one static SVG time-series exhibit.",
            scope="Uses only existing MacroForge normalized BLS evidence already present on disk.",
            non_scope="Does not create new analysis, forecast, runtime concept, package field, or grammar rule.",
        ),
        statements=(
            PresentationStatement(
                statement_id=statement_id,
                encounter_meaning=(
                    "BLS unemployment rate, United States, 2024\n\n"
                    "Source: MacroForge BLS labor core operational normalized dataset\n"
                    "Series: LNS14000000\n"
                    "Metric: Unemployment rate, civilian labor force, seasonally adjusted\n"
                    "Territory: United States\n"
                    "Frequency: monthly\n\n"
                    f"{source_table}"
                ),
                belongs_to_purpose="Show whether existing monthly unemployment-rate evidence benefits from one static SVG time-series exhibit.",
                encounter_semantics=EncounterSemantics(
                    mode="evidence",
                    description="Existing source-owned temporal evidence suitable for a renderer-side static time-series exhibit.",
                ),
                upstream_reference_ids=(reference_id,),
                obligation_ids=(obligation_id,),
            ),
        ),
        upstream_references=(
            UpstreamReference(
                reference_id=reference_id,
                owning_project="MacroForge",
                reference_kind="normalized-operational-dataset",
                locator=str(MACROFORGE_BLS_NORMALIZED),
                owned_meaning="Monthly U.S. labor-market observations from the normalized MacroForge BLS labor core operational dataset.",
            ),
        ),
        obligations=(
            PresentationObligation(
                obligation_id=obligation_id,
                category="source ownership",
                requirement="Rendered output must preserve that values are source-owned MacroForge/BLS evidence and not BriefForge analysis.",
                applies_to=(statement_id, reference_id),
            ),
        ),
    )


class StaticSvgTimeSeriesExhibitTests(unittest.TestCase):
    def _render_candidate(self, candidate):
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.renderer_adapter import (
            check_rendered_artifact_conformance,
            html_renderer_contract,
            render_minimal_html,
        )
        from briefforge.validation import validate_candidate_presentation_package

        judgment = validate_candidate_presentation_package(candidate)
        self.assertTrue(judgment.valid, judgment.findings)
        ready = promote_candidate_presentation_package(candidate, judgment)
        artifact = render_minimal_html(ready, html_renderer_contract())
        conformance = check_rendered_artifact_conformance(ready, artifact)
        return ready, artifact, conformance

    def test_task_032_baseline_contains_no_static_svg_time_series_exhibit_but_task_033_render_inserts_one(self):
        baseline_html = TASK_032_HTML.read_text()
        self.assertNotIn('data-exhibit-type="time-series-svg"', baseline_html)
        self.assertNotIn('<svg', baseline_html.lower())

        _ready, artifact, _conformance = self._render_candidate(_bls_time_series_candidate())
        html = artifact.html

        self.assertEqual(1, html.count('data-exhibit-type="time-series-svg"'))
        self.assertEqual(1, html.lower().count('<svg'))
        self.assertIn('data-visualization-class="time-series"', html)
        self.assertIn('data-exhibit-policy="no-runtime-object"', html)
        self.assertIn('data-svg-policy="static-only"', html)
        self.assertIn('<polyline', html)

    def test_non_time_series_reports_do_not_receive_fabricated_svg_charts(self):
        _ready, large_artifact, large_conformance = self._render_candidate(large_report_candidate_package())
        _ready, gdp_artifact, gdp_conformance = self._render_candidate(candidate_from_json(TASK_026_GDP_PACKAGE))

        self.assertTrue(large_conformance.conforms, large_conformance.findings)
        self.assertTrue(gdp_conformance.conforms, gdp_conformance.findings)
        self.assertNotIn('data-exhibit-type="time-series-svg"', large_artifact.html)
        self.assertNotIn('<svg', large_artifact.html.lower())
        self.assertNotIn('data-exhibit-type="time-series-svg"', gdp_artifact.html)
        self.assertNotIn('<svg', gdp_artifact.html.lower())

    def test_static_svg_preserves_semantic_ordering_and_conformance(self):
        candidate = _bls_time_series_candidate()
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
            html.index('data-statement-id="stmt-task-033-bls-unemployment-rate-2024"'),
            html.index('data-exhibit-type="time-series-svg"'),
        )

    def test_static_svg_does_not_expand_runtime_or_models_and_introduces_no_javascript(self):
        import briefforge.runtime as runtime
        from briefforge.runtime import CandidatePresentationPackage, PresentationStatement
        from briefforge.presentation_models import (
            CountryComparisonPresentation,
            CountryProfilePresentation,
            InvestmentThesisPresentation,
        )

        _ready, artifact, _conformance = self._render_candidate(_bls_time_series_candidate())
        html = artifact.html.lower()

        self.assertFalse(hasattr(runtime, "TimeSeriesExhibit"))
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
        self.assertNotIn("<script", html)
        self.assertIsNone(re.search(r"\son[a-z]+=", html))
        self.assertNotIn("chart.js", html)
        self.assertNotIn("d3.", html)
        self.assertNotIn("canvas", html)
        self.assertNotIn("dashboard", html)
        self.assertNotIn("portal", html)


if __name__ == "__main__":
    unittest.main()
