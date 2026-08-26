"""TASK-022 tests for grammar-centered static HTML rendering.

The renderer remains a bounded downstream proof. These tests require only
renderer-level communication improvements already justified by TASK-021. They
must not introduce runtime concepts, templates, CSS frameworks, JavaScript,
dashboards, portals, visualizations, charts, maps, PDFs, exports, persistence,
APIs, networking, renderer registries, or browser applications.
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

from test_real_presentation_end_to_end import denmark_country_profile_candidate  # noqa: E402


def denmark_ready_package():
    from briefforge.promotion import promote_candidate_presentation_package
    from briefforge.validation import validate_candidate_presentation_package

    candidate = denmark_country_profile_candidate()
    judgment = validate_candidate_presentation_package(candidate)
    return promote_candidate_presentation_package(candidate, judgment)


def denmark_html():
    from briefforge.renderer_adapter import render_minimal_html

    return render_minimal_html(denmark_ready_package()).html


class HumanCenteredHtmlRendererTests(unittest.TestCase):
    def test_existing_minimal_html_output_now_must_implement_presentation_grammar(self):
        html = denmark_html()
        lowered = html.lower()

        self.assertIn('data-grammar="presentation-grammar-v1"', lowered)
        self.assertIn('data-grammar-stage="orient"', lowered)
        self.assertIn('data-grammar-stage="state-main-point"', lowered)
        self.assertIn('data-grammar-stage="elaborate"', lowered)
        self.assertIn('data-grammar-stage="qualify"', lowered)
        self.assertIn('data-grammar-stage="trace"', lowered)
        self.assertIn('data-grammar-stage="close"', lowered)

        title_position = html.index("Denmark Country Profile")
        purpose_position = html.index("Show how Denmark combines")
        first_statement_position = html.index("Denmark should be encountered first")
        self.assertLess(title_position, purpose_position)
        self.assertLess(purpose_position, first_statement_position)

    def test_updated_renderer_exposes_human_attention_hierarchy(self):
        html = denmark_html()
        lowered = html.lower()

        self.assertIn('data-attention="primary"', lowered)
        self.assertIn('data-attention="secondary"', lowered)
        self.assertIn('data-attention="supporting"', lowered)
        self.assertIn('data-attention="discoverable"', lowered)
        self.assertIn("primary message", lowered)
        self.assertIn("supporting details", lowered)

        primary_position = lowered.index('data-attention="primary"')
        secondary_position = lowered.index('data-attention="secondary"')
        discoverable_position = lowered.index('data-attention="discoverable"')
        self.assertLess(primary_position, secondary_position)
        self.assertLess(secondary_position, discoverable_position)

    def test_references_are_linked_near_claims_and_grouped_for_audit(self):
        html = denmark_html()

        self.assertIn('href="#reference-ref-world-bank-denmark-gdp-2024"', html)
        self.assertIn('id="reference-ref-world-bank-denmark-gdp-2024"', html)
        self.assertIn("World Bank national accounts", html)
        self.assertIn("Source owner", html)
        self.assertIn("Manual TASK-014 source note", html)
        self.assertIn("Reference inventory", html)

        claim_position = html.index("rough 2024 public-context view")
        nearby_reference_position = html.index('href="#reference-ref-world-bank-denmark-gdp-2024"')
        inventory_position = html.index("Reference inventory")
        self.assertLess(claim_position, nearby_reference_position)
        self.assertLess(nearby_reference_position, inventory_position)

    def test_obligations_are_contextual_and_grouped_without_dominating(self):
        html = denmark_html()

        self.assertIn('href="#obligation-obl-no-forecast-claim"', html)
        self.assertIn('id="obligation-obl-no-forecast-claim"', html)
        self.assertIn("Do not present the country profile as a forecast", html)
        self.assertIn("Obligation inventory", html)
        self.assertIn("Contextual obligations", html)

        first_statement_position = html.index("Denmark should be encountered first")
        contextual_obligation_position = html.index('href="#obligation-obl-no-forecast-claim"')
        obligation_inventory_position = html.index("Obligation inventory")
        self.assertLess(first_statement_position, contextual_obligation_position)
        self.assertLess(contextual_obligation_position, obligation_inventory_position)

    def test_uncertainty_and_caveats_are_positioned_before_audit_metadata(self):
        html = denmark_html()

        self.assertIn("Uncertainty and caveats", html)
        self.assertIn("Population ageing is a medium-term pressure", html)
        self.assertIn("not present the country profile as a forecast", html)
        self.assertIn("not canonicalized BriefForge-owned data", html)
        self.assertIn("Validation and audit metadata", html)

        caveat_position = html.index("Uncertainty and caveats")
        audit_position = html.index("Validation and audit metadata")
        self.assertLess(caveat_position, audit_position)

    def test_audit_metadata_and_conformance_remain_intact(self):
        from briefforge.renderer_adapter import check_rendered_artifact_conformance, render_minimal_html

        ready = denmark_ready_package()
        artifact = render_minimal_html(ready)
        conformance = check_rendered_artifact_conformance(ready, artifact)

        self.assertTrue(conformance.conforms, conformance.findings)
        self.assertEqual(artifact.package_identity, ready.candidate.identity)
        self.assertEqual(artifact.semantic_fingerprint, ready.semantic_fingerprint)
        self.assertEqual(artifact.validation_policy_id, ready.validation_policy_id)
        self.assertIn(ready.semantic_fingerprint, artifact.html)
        self.assertIn(ready.validation_policy_id, artifact.html)
        self.assertIn("Validation and audit metadata", artifact.html)

    def test_runtime_objects_and_presentation_models_remain_unchanged(self):
        from briefforge.presentation_models import (
            CountryComparisonPresentation,
            CountryProfilePresentation,
            InvestmentThesisPresentation,
        )
        from briefforge.renderer_adapter import HtmlRenderedArtifact, render_minimal_html
        from briefforge.runtime import CandidatePresentationPackage, PresentationStatement, UpstreamReference

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
        self.assertEqual(
            tuple(field.name for field in fields(UpstreamReference)),
            ("reference_id", "owning_project", "reference_kind", "locator", "owned_meaning"),
        )
        self.assertEqual(tuple(field.name for field in fields(HtmlRenderedArtifact)), ("html", "adapter_identity", "package_identity", "semantic_fingerprint", "validation_policy_id"))
        self.assertEqual(tuple(field.name for field in fields(CountryProfilePresentation)), ("country_name", "candidate"))
        self.assertEqual(tuple(field.name for field in fields(CountryComparisonPresentation)), ("compared_countries", "candidate"))
        self.assertEqual(tuple(field.name for field in fields(InvestmentThesisPresentation)), ("subject", "candidate"))

        artifact = render_minimal_html(denmark_ready_package())
        self.assertIsInstance(artifact, HtmlRenderedArtifact)

    def test_renderer_remains_static_html_not_a_browser_application_or_template_system(self):
        html = denmark_html()
        lowered = html.lower()

        self.assertNotIn("<script", lowered)
        self.assertIn("<style", lowered)
        self.assertIn("data-reader-experience=\"static-v0.3\"", lowered)
        self.assertNotIn("bootstrap", lowered)
        self.assertNotIn("tailwind", lowered)
        self.assertNotIn("react", lowered)
        self.assertNotIn("data-template", lowered)
        self.assertNotIn("dashboard", lowered)
        self.assertNotIn("portal", lowered)
        self.assertNotIn("<canvas", lowered)
        self.assertNotIn("<svg", lowered)
        self.assertNotIn("fetch(", lowered)


if __name__ == "__main__":
    unittest.main()
