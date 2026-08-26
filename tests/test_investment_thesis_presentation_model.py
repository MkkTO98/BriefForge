"""Tests for the third semantic Presentation Model: Investment Thesis.

Investment Thesis is an authoring abstraction only. It must produce the
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


def renewable_grid_investment_thesis_candidate():
    from briefforge.presentation_models import InvestmentThesisBuilder

    return (
        InvestmentThesisBuilder(subject="European grid investment theme")
        .identity(
            package_id="briefforge-task-019-european-grid-investment-thesis",
            title="European grid investment thesis: bottleneck infrastructure as a transition enabler",
            purpose_summary=(
                "A compact investment-thesis presentation that helps a reader encounter the claim that European "
                "power-grid investment may be a durable transition bottleneck theme while preserving uncertainty, "
                "risk, counterargument, and source-ownership boundaries."
            ),
            scope=(
                "Presentation-level organization of manually authored thesis, evidence, risks, counterarguments, "
                "and conclusion for architectural validation."
            ),
            non_scope=(
                "No live MacroForge integration, investment advice, valuation model, forecast, recommendation, "
                "portfolio construction, chart, map, dashboard, browser application, or visualization."
            ),
        )
        .organizing_purpose(
            statement=(
                "Present a bounded investment thesis about European grid infrastructure as a transition bottleneck "
                "without converting BriefForge into an analyst, model owner, data owner, or recommendation engine."
            ),
            scope=(
                "Bind claim, evidence, risks, counterarguments, and conclusion into one coherent presentation package."
            ),
            non_scope=(
                "Do not provide investment advice, own upstream facts, calculate valuation, forecast returns, or decide "
                "portfolio action."
            ),
        )
        .reference(
            reference_id="ref-iea-grid-investment-context",
            owning_project="Manual TASK-019 source note",
            reference_kind="source-context",
            locator="IEA public grid investment and clean-energy transition context, manually summarized",
            owned_meaning="Upstream source owns grid-investment factual context and energy-system definitions.",
        )
        .reference(
            reference_id="ref-eu-grid-policy-context",
            owning_project="Manual TASK-019 source note",
            reference_kind="policy-context",
            locator="European public policy context on grid expansion, permitting, and renewable integration",
            owned_meaning="Upstream policy sources own policy text, institutional context, and official targets.",
        )
        .reference(
            reference_id="ref-market-risk-context",
            owning_project="Manual TASK-019 source note",
            reference_kind="risk-context",
            locator="Manually authored public-market risk context for regulated utilities and grid equipment exposure",
            owned_meaning="Upstream market sources and future research systems own factual and analytical market context.",
        )
        .obligation(
            obligation_id="obl-not-investment-advice",
            category="scope-control",
            requirement="Do not present the thesis as investment advice, a recommendation, a forecast, or portfolio instruction.",
            applies_to=("stmt-thesis-claim", "stmt-thesis-conclusion"),
        )
        .obligation(
            obligation_id="obl-thesis-source-attribution",
            category="attribution",
            requirement="Keep upstream source ownership visible for source-dependent evidence, policy context, and risk framing.",
            applies_to=("ref-iea-grid-investment-context", "ref-eu-grid-policy-context", "ref-market-risk-context"),
        )
        .obligation(
            obligation_id="obl-preserve-uncertainty",
            category="uncertainty",
            requirement="Preserve uncertainty, risks, and counterarguments rather than collapsing the presentation into a one-sided claim.",
            applies_to=("stmt-supporting-evidence", "stmt-key-risks", "stmt-counterargument", "stmt-thesis-conclusion"),
        )
        .thesis_statement(
            statement_id="stmt-thesis-claim",
            encounter_meaning=(
                "The reader should encounter the thesis as a bounded claim: European grid infrastructure may be a "
                "durable enabling bottleneck for electrification and renewable integration."
            ),
            encounter_description="State the core claim before evidence, risk, and counterargument are introduced.",
            related_statement_ids=("stmt-supporting-evidence", "stmt-key-risks", "stmt-counterargument"),
            obligation_ids=("obl-not-investment-advice",),
        )
        .supporting_evidence(
            statement_id="stmt-supporting-evidence",
            encounter_meaning=(
                "Supporting evidence is presentation-level: electrification, renewable interconnection queues, and grid "
                "reinforcement needs make infrastructure investment relevant, but BriefForge does not own the upstream facts."
            ),
            encounter_description="Show why the claim is plausible while preserving upstream factual ownership.",
            related_statement_ids=("stmt-thesis-claim", "stmt-key-risks"),
            upstream_reference_ids=("ref-iea-grid-investment-context", "ref-eu-grid-policy-context"),
            obligation_ids=("obl-thesis-source-attribution", "obl-preserve-uncertainty"),
        )
        .risk(
            statement_id="stmt-key-risks",
            encounter_meaning=(
                "Key risks include regulation, permitting delays, rate-base politics, execution bottlenecks, interest-rate "
                "sensitivity, and valuation compression."
            ),
            encounter_description="Force the reader to encounter uncertainty before any conclusion.",
            related_statement_ids=("stmt-supporting-evidence", "stmt-counterargument", "stmt-thesis-conclusion"),
            upstream_reference_ids=("ref-market-risk-context",),
            obligation_ids=("obl-thesis-source-attribution", "obl-preserve-uncertainty"),
        )
        .counterargument(
            statement_id="stmt-counterargument",
            encounter_meaning=(
                "A serious counterargument is that the theme may already be capitalized into exposed assets, while political "
                "and regulatory frictions can prevent grid need from becoming attractive investor returns."
            ),
            encounter_description="Preserve the strongest opposing interpretation inside the same package.",
            related_statement_ids=("stmt-thesis-claim", "stmt-key-risks", "stmt-thesis-conclusion"),
            upstream_reference_ids=("ref-market-risk-context",),
            obligation_ids=("obl-preserve-uncertainty",),
        )
        .conclusion(
            statement_id="stmt-thesis-conclusion",
            encounter_meaning=(
                "The appropriate presentation conclusion is watchlist framing, not a recommendation: the theme is coherent "
                "enough for further research, but the package does not assert valuation, timing, or action."
            ),
            encounter_description="Close with a bounded research-next-step conclusion rather than investment advice.",
            related_statement_ids=("stmt-thesis-claim", "stmt-supporting-evidence", "stmt-counterargument"),
            obligation_ids=("obl-not-investment-advice", "obl-preserve-uncertainty"),
        )
        .build()
        .to_candidate_presentation_package()
    )


class InvestmentThesisPresentationModelTests(unittest.TestCase):
    def test_investment_thesis_presentation_produces_valid_candidate_package(self):
        from briefforge.runtime import CandidatePresentationPackage
        from briefforge.validation import validate_candidate_presentation_package

        candidate = renewable_grid_investment_thesis_candidate()
        judgment = validate_candidate_presentation_package(candidate)

        self.assertIsInstance(candidate, CandidatePresentationPackage)
        self.assertTrue(judgment.valid, judgment.findings)
        self.assertEqual(candidate.identity.package_id, "briefforge-task-019-european-grid-investment-thesis")
        self.assertIn("investment thesis", candidate.identity.title.lower())

    def test_existing_pipeline_passes_unchanged_for_investment_thesis(self):
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.renderer_adapter import (
            check_rendered_artifact_conformance,
            check_renderer_adapter_compatibility,
            html_renderer_contract,
            invoke_renderer_adapter,
            render_minimal_html,
        )
        from briefforge.validation import validate_candidate_presentation_package

        candidate = renewable_grid_investment_thesis_candidate()
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
        self.assertIn("grid", artifact.html.lower())
        self.assertIn("counterargument", artifact.html.lower())
        self.assertNotIn("<script", artifact.html.lower())
        self.assertIn("<style", artifact.html.lower())
        self.assertIn("data-reader-experience=\"static-v0.3\"", artifact.html.lower())

    def test_existing_runtime_abstractions_require_no_modification(self):
        import briefforge.runtime as runtime
        from briefforge.runtime import CandidatePresentationPackage

        candidate = renewable_grid_investment_thesis_candidate()
        candidate_fields = {field.name for field in fields(CandidatePresentationPackage)}

        self.assertIs(type(candidate), CandidatePresentationPackage)
        self.assertFalse(hasattr(runtime, "InvestmentThesisPresentation"))
        self.assertFalse(hasattr(runtime, "InvestmentThesisBuilder"))
        self.assertFalse(
            candidate_fields
            & {
                "investment_thesis",
                "thesis_statement",
                "supporting_evidence",
                "risk",
                "counterargument",
                "conclusion",
                "claim",
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

        first = renewable_grid_investment_thesis_candidate()
        second = renewable_grid_investment_thesis_candidate()

        self.assertEqual(first, second)
        self.assertEqual(semantic_fingerprint(first), semantic_fingerprint(second))

    def test_existing_validation_promotion_rendering_and_conformance_continue_unchanged(self):
        from briefforge.promotion import ReadyPresentationPackage, promote_candidate_presentation_package
        from briefforge.renderer_adapter import HtmlRenderedArtifact, RenderedArtifactConformance, html_renderer_contract
        from briefforge.renderer_adapter import check_rendered_artifact_conformance, render_minimal_html
        from briefforge.validation import ValidationJudgment, validate_candidate_presentation_package

        candidate = renewable_grid_investment_thesis_candidate()
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
