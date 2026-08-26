"""Tests for the first semantic Presentation Model: Country Profile.

Country Profile is an authoring abstraction only. It must produce the existing
Candidate Presentation Package through the existing builder and runtime. It is
not a template, renderer, browser page, visualization, API, persistence layer,
or new runtime concept.
"""

import json
from dataclasses import fields
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

ARTIFACT_DIR = PROJECT_ROOT / "artifacts" / "presentations" / "TASK-014-denmark-country-profile"
EXPECTED_TASK_014_FINGERPRINT = "90d4651099df06afcaf1f531c887b03ae551475096dfa3ad163c44db04c089ff"


def candidate_from_task_014_artifact():
    from briefforge.runtime import (
        CandidatePresentationPackage,
        EncounterSemantics,
        OrganizingPurpose,
        PackageIdentity,
        PresentationObligation,
        PresentationStatement,
        UpstreamReference,
    )

    raw = json.loads((ARTIFACT_DIR / "candidate_presentation_package.json").read_text())
    return CandidatePresentationPackage(
        identity=PackageIdentity(**raw["identity"]),
        organizing_purpose=OrganizingPurpose(**raw["organizing_purpose"]),
        upstream_references=tuple(UpstreamReference(**item) for item in raw["upstream_references"]),
        obligations=tuple(
            PresentationObligation(
                obligation_id=item["obligation_id"],
                category=item["category"],
                requirement=item["requirement"],
                applies_to=tuple(item["applies_to"]),
            )
            for item in raw["obligations"]
        ),
        statements=tuple(
            PresentationStatement(
                statement_id=item["statement_id"],
                encounter_meaning=item["encounter_meaning"],
                belongs_to_purpose=item["belongs_to_purpose"],
                encounter_semantics=EncounterSemantics(
                    mode=item["encounter_semantics"]["mode"],
                    description=item["encounter_semantics"]["description"],
                    related_statement_ids=tuple(item["encounter_semantics"]["related_statement_ids"]),
                ),
                upstream_reference_ids=tuple(item["upstream_reference_ids"]),
                obligation_ids=tuple(item["obligation_ids"]),
            )
            for item in raw["statements"]
        ),
    )


def denmark_country_profile_model_candidate():
    from briefforge.presentation_models import CountryProfileBuilder

    return (
        CountryProfileBuilder(country_name="Denmark")
        .identity(
            package_id="briefforge-task-014-denmark-country-profile",
            title="Denmark Country Profile: small open economy with ageing pressure",
            purpose_summary=(
                "A compact economic presentation that helps a reader understand Denmark's current macro profile, "
                "labor-market strength, demographic pressure, and energy transition context."
            ),
            scope=(
                "Presentation-level organization of selected macroeconomic, demographic, fiscal, and energy facts "
                "for a small country profile proof."
            ),
            non_scope=(
                "No live data ingestion, forecasting, econometric modeling, investment recommendation, dashboard, "
                "interactive visualization, or portal navigation."
            ),
        )
        .organizing_purpose(
            statement=(
                "Show how Denmark combines high-income macro stability and strong employment with medium-term "
                "demographic ageing and transition-policy obligations."
            ),
            scope=(
                "Bind a small set of manually authored, source-attributed presentation statements into one coherent "
                "country-profile narrative."
            ),
            non_scope=(
                "Do not canonicalize source data, adjudicate conflicting economic meaning, forecast outcomes, or own "
                "the upstream statistical interpretation."
            ),
        )
        .reference(
            reference_id="ref-world-bank-denmark-gdp-2024",
            owning_project="Manual TASK-014 source note",
            reference_kind="source-statistic",
            locator="World Bank national accounts, Denmark GDP current US dollars, 2024 approximate public series",
            owned_meaning="Upstream source owns the GDP measurement and national-accounts definition.",
        )
        .reference(
            reference_id="ref-statbank-denmark-population-ageing-2024",
            owning_project="Manual TASK-014 source note",
            reference_kind="source-statistic",
            locator="Statistics Denmark / StatBank demographic age-structure context, 2024 public tables",
            owned_meaning="Upstream demographic source owns population counts and age-group definitions.",
        )
        .reference(
            reference_id="ref-eurostat-denmark-unemployment-2024",
            owning_project="Manual TASK-014 source note",
            reference_kind="source-statistic",
            locator="Eurostat unemployment-rate context for Denmark, 2024 public labor-market series",
            owned_meaning="Upstream labor statistics source owns unemployment-rate measurement.",
        )
        .reference(
            reference_id="ref-iea-denmark-energy-transition",
            owning_project="Manual TASK-014 source note",
            reference_kind="source-context",
            locator="IEA Denmark energy-policy and renewables context, recent public country material",
            owned_meaning="Upstream energy source owns policy and energy-system factual context.",
        )
        .obligation(
            obligation_id="obl-source-attribution",
            category="attribution",
            requirement="Keep source ownership visible for every quantitative or source-dependent statement.",
            applies_to=(
                "ref-world-bank-denmark-gdp-2024",
                "ref-statbank-denmark-population-ageing-2024",
                "ref-eurostat-denmark-unemployment-2024",
                "ref-iea-denmark-energy-transition",
            ),
        )
        .obligation(
            obligation_id="obl-no-forecast-claim",
            category="scope-control",
            requirement="Do not present the country profile as a forecast, recommendation, or live MacroForge output.",
            applies_to=("stmt-positioning", "stmt-demographic-pressure", "stmt-investment-relevance"),
        )
        .obligation(
            obligation_id="obl-approximate-manual-data",
            category="data-quality",
            requirement=(
                "State that figures are manually authored approximate public-context facts and not canonicalized "
                "BriefForge-owned data."
            ),
            applies_to=("stmt-macro-scale", "stmt-labor-market", "stmt-demographic-pressure"),
        )
        .overview(
            statement_id="stmt-positioning",
            encounter_meaning=(
                "Denmark should be encountered first as a small, high-income, highly open European economy whose "
                "presentation relevance comes from stability, external exposure, and institutional capacity."
            ),
            encounter_description="Introduce the country lens before quantitative detail.",
            related_statement_ids=("stmt-macro-scale", "stmt-investment-relevance"),
            obligation_ids=("obl-no-forecast-claim",),
        )
        .economy(
            statement_id="stmt-macro-scale",
            encounter_meaning=(
                "A rough 2024 public-context view places Denmark near USD 400 billion in nominal GDP with a "
                "population around 6 million, making per-capita income high but aggregate scale modest."
            ),
            encounter_mode="quantitative-context",
            encounter_description="Give the reader scale without turning BriefForge into the data owner.",
            related_statement_ids=("stmt-positioning", "stmt-labor-market"),
            upstream_reference_ids=("ref-world-bank-denmark-gdp-2024",),
            obligation_ids=("obl-source-attribution", "obl-approximate-manual-data"),
        )
        .economy(
            statement_id="stmt-labor-market",
            encounter_meaning=(
                "Denmark's labor-market story is one of relatively strong employment institutions and low-to-moderate "
                "unemployment by European comparison, relevant to wage pressure and household resilience."
            ),
            encounter_mode="supporting-context",
            encounter_description="Connect labor-market facts to macro resilience while preserving source ownership.",
            related_statement_ids=("stmt-macro-scale", "stmt-demographic-pressure"),
            upstream_reference_ids=("ref-eurostat-denmark-unemployment-2024",),
            obligation_ids=("obl-source-attribution", "obl-approximate-manual-data"),
        )
        .demographics(
            statement_id="stmt-demographic-pressure",
            encounter_meaning=(
                "Population ageing is a medium-term pressure: the presentation should make ageing visible without "
                "claiming that BriefForge has modeled fiscal, labor-supply, or healthcare outcomes."
            ),
            encounter_mode="risk-context",
            encounter_description="Surface a structural pressure after baseline macro and labor context.",
            related_statement_ids=("stmt-labor-market", "stmt-investment-relevance"),
            upstream_reference_ids=("ref-statbank-denmark-population-ageing-2024",),
            obligation_ids=("obl-source-attribution", "obl-approximate-manual-data", "obl-no-forecast-claim"),
        )
        .section(
            statement_id="stmt-energy-transition",
            section_kind="energy-transition",
            encounter_meaning=(
                "Energy transition context matters because Denmark has substantial wind-power and climate-policy "
                "salience, but this package only presents that relevance; it does not render charts or model energy markets."
            ),
            encounter_mode="thematic-context",
            encounter_description="Add a policy/sector theme without creating a visualization obligation.",
            related_statement_ids=("stmt-investment-relevance",),
            upstream_reference_ids=("ref-iea-denmark-energy-transition",),
            obligation_ids=("obl-source-attribution",),
        )
        .section(
            statement_id="stmt-investment-relevance",
            section_kind="synthesis",
            encounter_meaning=(
                "For an EIP reader, the profile's value is not a recommendation but a reusable presentation frame: "
                "macro stability, open-economy exposure, ageing pressure, and transition-policy context can be compared later."
            ),
            encounter_mode="synthesis",
            encounter_description="Close by connecting the selected facts into the intended decision-relevant frame.",
            related_statement_ids=("stmt-positioning", "stmt-demographic-pressure", "stmt-energy-transition"),
            obligation_ids=("obl-no-forecast-claim",),
        )
        .build()
        .to_candidate_presentation_package()
    )


class CountryProfilePresentationModelTests(unittest.TestCase):
    def test_country_profile_presentation_produces_valid_candidate_package(self):
        from briefforge.runtime import CandidatePresentationPackage
        from briefforge.validation import validate_candidate_presentation_package

        candidate = denmark_country_profile_model_candidate()
        judgment = validate_candidate_presentation_package(candidate)

        self.assertIsInstance(candidate, CandidatePresentationPackage)
        self.assertTrue(judgment.valid, judgment.findings)
        self.assertEqual(candidate.identity.title, "Denmark Country Profile: small open economy with ageing pressure")

    def test_denmark_country_profile_migrates_with_semantic_equivalence(self):
        self.assertEqual(denmark_country_profile_model_candidate(), candidate_from_task_014_artifact())

    def test_existing_semantic_fingerprint_remains_stable_for_denmark_migration(self):
        from briefforge.runtime import semantic_fingerprint

        candidate = denmark_country_profile_model_candidate()

        self.assertEqual(semantic_fingerprint(candidate), EXPECTED_TASK_014_FINGERPRINT)
        self.assertEqual(semantic_fingerprint(candidate), semantic_fingerprint(candidate_from_task_014_artifact()))

    def test_existing_pipeline_passes_unchanged(self):
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.renderer_adapter import (
            check_rendered_artifact_conformance,
            check_renderer_adapter_compatibility,
            html_renderer_contract,
            invoke_renderer_adapter,
            render_minimal_html,
        )
        from briefforge.validation import validate_candidate_presentation_package

        candidate = denmark_country_profile_model_candidate()
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

    def test_country_profile_introduces_no_new_runtime_abstractions(self):
        import briefforge.runtime as runtime
        from briefforge.runtime import CandidatePresentationPackage

        candidate = denmark_country_profile_model_candidate()
        candidate_fields = {field.name for field in fields(CandidatePresentationPackage)}

        self.assertIs(type(candidate), CandidatePresentationPackage)
        self.assertFalse(
            candidate_fields
            & {
                "country_profile",
                "template",
                "layout",
                "html",
                "css",
                "javascript",
                "browser",
                "dashboard",
                "portal",
                "api",
                "persistence",
            }
        )
        self.assertFalse(hasattr(runtime, "CountryProfilePresentation"))
        self.assertFalse(hasattr(runtime, "CountryProfileBuilder"))


if __name__ == "__main__":
    unittest.main()
