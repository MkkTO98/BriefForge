"""Tests for the second semantic Presentation Model: Country Comparison.

Country Comparison is an authoring abstraction only. It must produce the
existing Candidate Presentation Package through the existing builder and runtime.
It is not a template, layout, renderer, browser page, visualization, API,
persistence layer, or new runtime concept.
"""

from dataclasses import fields
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))


def denmark_germany_comparison_candidate():
    from briefforge.presentation_models import CountryComparisonBuilder

    return (
        CountryComparisonBuilder(compared_countries=("Denmark", "Germany"))
        .identity(
            package_id="briefforge-task-018-denmark-germany-comparison",
            title="Denmark vs Germany: small-open-economy comparison frame",
            purpose_summary=(
                "A compact comparison presentation that helps a reader encounter Denmark and Germany through "
                "scale, openness, labor-market resilience, demographics, and energy-transition context."
            ),
            scope=(
                "Presentation-level organization of selected public-context facts into a small comparative frame."
            ),
            non_scope=(
                "No live data ingestion, canonicalization, forecasting, investment recommendation, dashboard, chart, "
                "map, browser application, or visualization."
            ),
        )
        .organizing_purpose(
            statement=(
                "Compare Denmark and Germany as European economies with shared institutional context but different "
                "scale, industrial structure, and transition exposure."
            ),
            scope=(
                "Bind manually authored comparison statements into one coherent presentation package while preserving "
                "upstream source ownership."
            ),
            non_scope=(
                "Do not adjudicate canonical economic truth, model macro outcomes, forecast relative performance, or "
                "own upstream statistical interpretation."
            ),
        )
        .reference(
            reference_id="ref-world-bank-denmark-germany-gdp-2024",
            owning_project="Manual TASK-018 source note",
            reference_kind="source-statistic",
            locator="World Bank national accounts public GDP context for Denmark and Germany, 2024 approximate series",
            owned_meaning="Upstream source owns GDP measurement and national-accounts definitions.",
        )
        .reference(
            reference_id="ref-eurostat-denmark-germany-labor-2024",
            owning_project="Manual TASK-018 source note",
            reference_kind="source-statistic",
            locator="Eurostat public unemployment and labor-market context for Denmark and Germany, 2024 series",
            owned_meaning="Upstream labor statistics source owns unemployment-rate measurement and definitions.",
        )
        .reference(
            reference_id="ref-eurostat-denmark-germany-demographics-2024",
            owning_project="Manual TASK-018 source note",
            reference_kind="source-statistic",
            locator="Eurostat demographic and ageing context for Denmark and Germany, 2024 public tables",
            owned_meaning="Upstream demographic source owns population counts and age-structure definitions.",
        )
        .reference(
            reference_id="ref-iea-denmark-germany-energy-transition",
            owning_project="Manual TASK-018 source note",
            reference_kind="source-context",
            locator="IEA public country energy-transition context for Denmark and Germany",
            owned_meaning="Upstream energy source owns policy and energy-system factual context.",
        )
        .obligation(
            obligation_id="obl-comparison-source-attribution",
            category="attribution",
            requirement="Keep source ownership visible for each quantitative or source-dependent comparison statement.",
            applies_to=(
                "ref-world-bank-denmark-germany-gdp-2024",
                "ref-eurostat-denmark-germany-labor-2024",
                "ref-eurostat-denmark-germany-demographics-2024",
                "ref-iea-denmark-germany-energy-transition",
            ),
        )
        .obligation(
            obligation_id="obl-no-ranking-or-recommendation",
            category="scope-control",
            requirement="Do not present the comparison as a country ranking, forecast, investment recommendation, or live MacroForge output.",
            applies_to=("stmt-comparison-overview", "stmt-scale-difference", "stmt-investment-frame"),
        )
        .obligation(
            obligation_id="obl-approximate-comparison-data",
            category="data-quality",
            requirement=(
                "State that figures are manually authored approximate public-context facts and not canonicalized "
                "BriefForge-owned data."
            ),
            applies_to=("stmt-scale-difference", "stmt-labor-similarity", "stmt-demographic-pressure"),
        )
        .overview(
            statement_id="stmt-comparison-overview",
            encounter_meaning=(
                "The reader should first encounter Denmark and Germany as comparable European economies only in a "
                "bounded presentation sense: shared institutional context, sharply different scale, and different exposure channels."
            ),
            encounter_description="Introduce the comparison lens before individual indicators.",
            related_statement_ids=("stmt-scale-difference", "stmt-investment-frame"),
            obligation_ids=("obl-no-ranking-or-recommendation",),
        )
        .indicator(
            statement_id="stmt-scale-difference",
            indicator_name="nominal GDP and population scale",
            encounter_meaning=(
                "Germany's aggregate economic scale is much larger than Denmark's, while Denmark remains a high-income "
                "small open economy; this difference changes how readers should interpret macro signals."
            ),
            encounter_description="Compare scale without converting the package into a data owner or chart specification.",
            related_statement_ids=("stmt-comparison-overview", "stmt-labor-similarity"),
            upstream_reference_ids=("ref-world-bank-denmark-germany-gdp-2024",),
            obligation_ids=("obl-comparison-source-attribution", "obl-approximate-comparison-data", "obl-no-ranking-or-recommendation"),
        )
        .similarity(
            statement_id="stmt-labor-similarity",
            encounter_meaning=(
                "Both countries can be presented as institutionally strong labor markets in a European context, but the "
                "comparison should preserve source ownership rather than assert canonical labor-market diagnosis."
            ),
            encounter_description="Surface a shared labor-market resilience theme after the scale contrast.",
            related_statement_ids=("stmt-scale-difference", "stmt-demographic-pressure"),
            upstream_reference_ids=("ref-eurostat-denmark-germany-labor-2024",),
            obligation_ids=("obl-comparison-source-attribution", "obl-approximate-comparison-data"),
        )
        .difference(
            statement_id="stmt-demographic-pressure",
            encounter_meaning=(
                "Both economies face ageing pressure, but Germany's larger population base and industrial structure make "
                "the presentation relevance different from Denmark's smaller welfare-state and open-economy framing."
            ),
            encounter_description="Use demographics as a comparative pressure rather than a modeled forecast.",
            related_statement_ids=("stmt-labor-similarity", "stmt-investment-frame"),
            upstream_reference_ids=("ref-eurostat-denmark-germany-demographics-2024",),
            obligation_ids=("obl-comparison-source-attribution", "obl-approximate-comparison-data"),
        )
        .section(
            statement_id="stmt-energy-transition-context",
            section_kind="energy-transition",
            encounter_meaning=(
                "Energy transition is comparison-relevant because Denmark and Germany both have major transition-policy "
                "salience, but this package only presents the comparison context and does not model power markets."
            ),
            encounter_mode="thematic-comparison",
            encounter_description="Add a shared policy theme without creating chart, map, or visualization obligations.",
            related_statement_ids=("stmt-investment-frame",),
            upstream_reference_ids=("ref-iea-denmark-germany-energy-transition",),
            obligation_ids=("obl-comparison-source-attribution",),
        )
        .section(
            statement_id="stmt-investment-frame",
            section_kind="synthesis",
            encounter_meaning=(
                "For an EIP reader, the comparison's value is a reusable frame: scale, openness, labor resilience, ageing, "
                "and transition context can be compared without BriefForge owning analysis or recommendation."
            ),
            encounter_mode="comparison-synthesis",
            encounter_description="Close by connecting comparison dimensions into a reusable decision-relevant frame.",
            related_statement_ids=("stmt-comparison-overview", "stmt-scale-difference", "stmt-energy-transition-context"),
            obligation_ids=("obl-no-ranking-or-recommendation",),
        )
        .build()
        .to_candidate_presentation_package()
    )


class CountryComparisonPresentationModelTests(unittest.TestCase):
    def test_country_comparison_presentation_produces_valid_candidate_package(self):
        from briefforge.runtime import CandidatePresentationPackage
        from briefforge.validation import validate_candidate_presentation_package

        candidate = denmark_germany_comparison_candidate()
        judgment = validate_candidate_presentation_package(candidate)

        self.assertIsInstance(candidate, CandidatePresentationPackage)
        self.assertTrue(judgment.valid, judgment.findings)
        self.assertEqual(candidate.identity.package_id, "briefforge-task-018-denmark-germany-comparison")
        self.assertIn("Denmark vs Germany", candidate.identity.title)

    def test_existing_pipeline_passes_unchanged_for_country_comparison(self):
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.renderer_adapter import (
            check_rendered_artifact_conformance,
            check_renderer_adapter_compatibility,
            html_renderer_contract,
            invoke_renderer_adapter,
            render_minimal_html,
        )
        from briefforge.validation import validate_candidate_presentation_package

        candidate = denmark_germany_comparison_candidate()
        judgment = validate_candidate_presentation_package(candidate)
        ready = promote_candidate_presentation_package(candidate, judgment)
        contract = html_renderer_contract()
        compatibility = check_renderer_adapter_compatibility(ready, contract)
        invocation = invoke_renderer_adapter(ready, contract)
        artifact = render_minimal_html(ready, contract)
        conformance = check_rendered_artifact_conformance(ready, artifact)

        self.assertTrue(judgment.valid, judgment.findings)
        self.assertTrue(compatibility.compatible)
        self.assertTrue(invocation.accepted)
        self.assertTrue(conformance.conforms, conformance.findings)
        self.assertIn("Denmark", artifact.html)
        self.assertIn("Germany", artifact.html)
        self.assertNotIn("<script", artifact.html.lower())
        self.assertIn("<style", artifact.html.lower())
        self.assertIn("data-reader-experience=\"static-v0.3\"", artifact.html.lower())

    def test_existing_runtime_abstractions_require_no_modification(self):
        import briefforge.runtime as runtime
        from briefforge.runtime import CandidatePresentationPackage

        candidate = denmark_germany_comparison_candidate()
        candidate_fields = {field.name for field in fields(CandidatePresentationPackage)}

        self.assertIs(type(candidate), CandidatePresentationPackage)
        self.assertFalse(hasattr(runtime, "CountryComparisonPresentation"))
        self.assertFalse(hasattr(runtime, "CountryComparisonBuilder"))
        self.assertFalse(
            candidate_fields
            & {
                "country_comparison",
                "compared_countries",
                "indicator",
                "similarity",
                "difference",
                "template",
                "layout",
                "html",
                "css",
                "javascript",
                "browser",
                "dashboard",
                "portal",
                "visualization",
                "chart",
                "map",
                "api",
                "persistence",
            }
        )

    def test_existing_semantic_fingerprints_remain_deterministic(self):
        from briefforge.runtime import semantic_fingerprint

        first = denmark_germany_comparison_candidate()
        second = denmark_germany_comparison_candidate()

        self.assertEqual(first, second)
        self.assertEqual(semantic_fingerprint(first), semantic_fingerprint(second))

    def test_existing_validation_promotion_rendering_and_conformance_continue_unchanged(self):
        from briefforge.promotion import ReadyPresentationPackage, promote_candidate_presentation_package
        from briefforge.renderer_adapter import HtmlRenderedArtifact, RenderedArtifactConformance, html_renderer_contract
        from briefforge.renderer_adapter import check_rendered_artifact_conformance, render_minimal_html
        from briefforge.validation import ValidationJudgment, validate_candidate_presentation_package

        candidate = denmark_germany_comparison_candidate()
        judgment = validate_candidate_presentation_package(candidate)
        ready = promote_candidate_presentation_package(candidate, judgment)
        artifact = render_minimal_html(ready, html_renderer_contract())
        conformance = check_rendered_artifact_conformance(ready, artifact)

        self.assertIsInstance(judgment, ValidationJudgment)
        self.assertIsInstance(ready, ReadyPresentationPackage)
        self.assertIsInstance(artifact, HtmlRenderedArtifact)
        self.assertIsInstance(conformance, RenderedArtifactConformance)
        self.assertTrue(conformance.conforms, conformance.findings)


if __name__ == "__main__":
    unittest.main()
