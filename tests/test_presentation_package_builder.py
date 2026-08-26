"""Tests for the Presentation Package Builder authoring convenience.

The builder must produce existing Candidate Presentation Package runtime objects
only. It must not alter validation, promotion, rendering, conformance, templates,
components, persistence, APIs, browser behavior, or semantic concepts.
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


EXPECTED_TASK_014_FINGERPRINT = "90d4651099df06afcaf1f531c887b03ae551475096dfa3ad163c44db04c089ff"


def manual_small_candidate():
    from briefforge.runtime import (
        CandidatePresentationPackage,
        EncounterSemantics,
        OrganizingPurpose,
        PackageIdentity,
        PresentationObligation,
        PresentationStatement,
        UpstreamReference,
    )

    return CandidatePresentationPackage(
        identity=PackageIdentity(
            package_id="builder-proof-package",
            title="Builder Proof Package",
            purpose_summary="Prove builder output equivalence.",
            scope="One small package.",
            non_scope="No rendering or delivery ownership.",
        ),
        organizing_purpose=OrganizingPurpose(
            statement="Bind a statement to one package purpose.",
            scope="Authoring convenience proof.",
            non_scope="No runtime-model change.",
        ),
        statements=(
            PresentationStatement(
                statement_id="stmt-one",
                encounter_meaning="The builder should produce this exact statement.",
                belongs_to_purpose="Builder proof purpose",
                encounter_semantics=EncounterSemantics(
                    mode="orientation",
                    description="Introduce the proof statement.",
                    related_statement_ids=("stmt-two",),
                ),
                upstream_reference_ids=("ref-one",),
                obligation_ids=("obl-one",),
            ),
            PresentationStatement(
                statement_id="stmt-two",
                encounter_meaning="A second statement exercises tuple ordering.",
                belongs_to_purpose="Builder proof purpose",
                encounter_semantics=EncounterSemantics(
                    mode="supporting-context",
                    description="Support the first proof statement.",
                ),
            ),
        ),
        upstream_references=(
            UpstreamReference(
                reference_id="ref-one",
                owning_project="Manual proof source",
                reference_kind="source-note",
                locator="manual://builder-proof",
                owned_meaning="The upstream source owns the proof fact.",
            ),
        ),
        obligations=(
            PresentationObligation(
                obligation_id="obl-one",
                category="scope-control",
                requirement="Do not treat builder output as a new semantic concept.",
                applies_to=("stmt-one", "ref-one"),
            ),
        ),
    )


def builder_small_candidate():
    from briefforge.builder import PresentationPackageBuilder

    return (
        PresentationPackageBuilder()
        .identity(
            package_id="builder-proof-package",
            title="Builder Proof Package",
            purpose_summary="Prove builder output equivalence.",
            scope="One small package.",
            non_scope="No rendering or delivery ownership.",
        )
        .organizing_purpose(
            statement="Bind a statement to one package purpose.",
            scope="Authoring convenience proof.",
            non_scope="No runtime-model change.",
        )
        .add_upstream_reference(
            reference_id="ref-one",
            owning_project="Manual proof source",
            reference_kind="source-note",
            locator="manual://builder-proof",
            owned_meaning="The upstream source owns the proof fact.",
        )
        .add_obligation(
            obligation_id="obl-one",
            category="scope-control",
            requirement="Do not treat builder output as a new semantic concept.",
            applies_to=("stmt-one", "ref-one"),
        )
        .add_statement(
            statement_id="stmt-one",
            encounter_meaning="The builder should produce this exact statement.",
            belongs_to_purpose="Builder proof purpose",
            encounter_mode="orientation",
            encounter_description="Introduce the proof statement.",
            related_statement_ids=("stmt-two",),
            upstream_reference_ids=("ref-one",),
            obligation_ids=("obl-one",),
        )
        .add_statement(
            statement_id="stmt-two",
            encounter_meaning="A second statement exercises tuple ordering.",
            belongs_to_purpose="Builder proof purpose",
            encounter_mode="supporting-context",
            encounter_description="Support the first proof statement.",
        )
        .build()
    )


def denmark_country_profile_candidate_built_with_builder():
    from briefforge.builder import PresentationPackageBuilder

    return (
        PresentationPackageBuilder()
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
        .add_upstream_reference(
            reference_id="ref-world-bank-denmark-gdp-2024",
            owning_project="Manual TASK-014 source note",
            reference_kind="source-statistic",
            locator="World Bank national accounts, Denmark GDP current US dollars, 2024 approximate public series",
            owned_meaning="Upstream source owns the GDP measurement and national-accounts definition.",
        )
        .add_upstream_reference(
            reference_id="ref-statbank-denmark-population-ageing-2024",
            owning_project="Manual TASK-014 source note",
            reference_kind="source-statistic",
            locator="Statistics Denmark / StatBank demographic age-structure context, 2024 public tables",
            owned_meaning="Upstream demographic source owns population counts and age-group definitions.",
        )
        .add_upstream_reference(
            reference_id="ref-eurostat-denmark-unemployment-2024",
            owning_project="Manual TASK-014 source note",
            reference_kind="source-statistic",
            locator="Eurostat unemployment-rate context for Denmark, 2024 public labor-market series",
            owned_meaning="Upstream labor statistics source owns unemployment-rate measurement.",
        )
        .add_upstream_reference(
            reference_id="ref-iea-denmark-energy-transition",
            owning_project="Manual TASK-014 source note",
            reference_kind="source-context",
            locator="IEA Denmark energy-policy and renewables context, recent public country material",
            owned_meaning="Upstream energy source owns policy and energy-system factual context.",
        )
        .add_obligation(
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
        .add_obligation(
            obligation_id="obl-no-forecast-claim",
            category="scope-control",
            requirement="Do not present the country profile as a forecast, recommendation, or live MacroForge output.",
            applies_to=("stmt-positioning", "stmt-demographic-pressure", "stmt-investment-relevance"),
        )
        .add_obligation(
            obligation_id="obl-approximate-manual-data",
            category="data-quality",
            requirement=(
                "State that figures are manually authored approximate public-context facts and not canonicalized "
                "BriefForge-owned data."
            ),
            applies_to=("stmt-macro-scale", "stmt-labor-market", "stmt-demographic-pressure"),
        )
        .add_statement(
            statement_id="stmt-positioning",
            encounter_meaning=(
                "Denmark should be encountered first as a small, high-income, highly open European economy whose "
                "presentation relevance comes from stability, external exposure, and institutional capacity."
            ),
            belongs_to_purpose="Denmark country-profile organizing purpose",
            encounter_mode="orientation",
            encounter_description="Introduce the country lens before quantitative detail.",
            related_statement_ids=("stmt-macro-scale", "stmt-investment-relevance"),
            obligation_ids=("obl-no-forecast-claim",),
        )
        .add_statement(
            statement_id="stmt-macro-scale",
            encounter_meaning=(
                "A rough 2024 public-context view places Denmark near USD 400 billion in nominal GDP with a "
                "population around 6 million, making per-capita income high but aggregate scale modest."
            ),
            belongs_to_purpose="Denmark country-profile organizing purpose",
            encounter_mode="quantitative-context",
            encounter_description="Give the reader scale without turning BriefForge into the data owner.",
            related_statement_ids=("stmt-positioning", "stmt-labor-market"),
            upstream_reference_ids=("ref-world-bank-denmark-gdp-2024",),
            obligation_ids=("obl-source-attribution", "obl-approximate-manual-data"),
        )
        .add_statement(
            statement_id="stmt-labor-market",
            encounter_meaning=(
                "Denmark's labor-market story is one of relatively strong employment institutions and low-to-moderate "
                "unemployment by European comparison, relevant to wage pressure and household resilience."
            ),
            belongs_to_purpose="Denmark country-profile organizing purpose",
            encounter_mode="supporting-context",
            encounter_description="Connect labor-market facts to macro resilience while preserving source ownership.",
            related_statement_ids=("stmt-macro-scale", "stmt-demographic-pressure"),
            upstream_reference_ids=("ref-eurostat-denmark-unemployment-2024",),
            obligation_ids=("obl-source-attribution", "obl-approximate-manual-data"),
        )
        .add_statement(
            statement_id="stmt-demographic-pressure",
            encounter_meaning=(
                "Population ageing is a medium-term pressure: the presentation should make ageing visible without "
                "claiming that BriefForge has modeled fiscal, labor-supply, or healthcare outcomes."
            ),
            belongs_to_purpose="Denmark country-profile organizing purpose",
            encounter_mode="risk-context",
            encounter_description="Surface a structural pressure after baseline macro and labor context.",
            related_statement_ids=("stmt-labor-market", "stmt-investment-relevance"),
            upstream_reference_ids=("ref-statbank-denmark-population-ageing-2024",),
            obligation_ids=("obl-source-attribution", "obl-approximate-manual-data", "obl-no-forecast-claim"),
        )
        .add_statement(
            statement_id="stmt-energy-transition",
            encounter_meaning=(
                "Energy transition context matters because Denmark has substantial wind-power and climate-policy "
                "salience, but this package only presents that relevance; it does not render charts or model energy markets."
            ),
            belongs_to_purpose="Denmark country-profile organizing purpose",
            encounter_mode="thematic-context",
            encounter_description="Add a policy/sector theme without creating a visualization obligation.",
            related_statement_ids=("stmt-investment-relevance",),
            upstream_reference_ids=("ref-iea-denmark-energy-transition",),
            obligation_ids=("obl-source-attribution",),
        )
        .add_statement(
            statement_id="stmt-investment-relevance",
            encounter_meaning=(
                "For an EIP reader, the profile's value is not a recommendation but a reusable presentation frame: "
                "macro stability, open-economy exposure, ageing pressure, and transition-policy context can be compared later."
            ),
            belongs_to_purpose="Denmark country-profile organizing purpose",
            encounter_mode="synthesis",
            encounter_description="Close by connecting the selected facts into the intended decision-relevant frame.",
            related_statement_ids=("stmt-positioning", "stmt-demographic-pressure", "stmt-energy-transition"),
            obligation_ids=("obl-no-forecast-claim",),
        )
        .build()
    )


class PresentationPackageBuilderTests(unittest.TestCase):
    def test_builder_produces_same_candidate_package_as_manual_construction(self):
        self.assertEqual(builder_small_candidate(), manual_small_candidate())

    def test_missing_required_fields_are_rejected_before_build(self):
        from briefforge.builder import PresentationPackageBuildRejected, PresentationPackageBuilder

        with self.assertRaisesRegex(PresentationPackageBuildRejected, "identity"):
            PresentationPackageBuilder().build()

        with self.assertRaisesRegex(PresentationPackageBuildRejected, "organizing_purpose"):
            PresentationPackageBuilder().identity(
                package_id="pkg",
                title="Title",
                purpose_summary="Purpose",
                scope="Scope",
                non_scope="Non-scope",
            ).build()

        with self.assertRaisesRegex(PresentationPackageBuildRejected, "statements"):
            (
                PresentationPackageBuilder()
                .identity(
                    package_id="pkg",
                    title="Title",
                    purpose_summary="Purpose",
                    scope="Scope",
                    non_scope="Non-scope",
                )
                .organizing_purpose(
                    statement="Purpose",
                    scope="Scope",
                    non_scope="Non-scope",
                )
                .build()
            )

        with self.assertRaisesRegex(PresentationPackageBuildRejected, "package_id"):
            PresentationPackageBuilder().identity(
                package_id="",
                title="Title",
                purpose_summary="Purpose",
                scope="Scope",
                non_scope="Non-scope",
            )

    def test_builder_does_not_invent_defaults_beyond_empty_optional_collections(self):
        from briefforge.builder import PresentationPackageBuilder
        from briefforge.runtime import CandidatePresentationPackage

        candidate = (
            PresentationPackageBuilder()
            .identity(
                package_id="minimal-builder-package",
                title="Minimal Builder Package",
                purpose_summary="Minimal proof.",
                scope="Only required semantic fields.",
                non_scope="No invented delivery behavior.",
            )
            .organizing_purpose(
                statement="Minimal package purpose.",
                scope="Required purpose fields.",
                non_scope="No invented semantics.",
            )
            .add_statement(
                statement_id="stmt-minimal",
                encounter_meaning="A minimal statement.",
                belongs_to_purpose="Minimal purpose.",
                encounter_mode="orientation",
                encounter_description="Required encounter description.",
            )
            .build()
        )

        self.assertIsInstance(candidate, CandidatePresentationPackage)
        self.assertEqual(candidate.upstream_references, ())
        self.assertEqual(candidate.obligations, ())
        self.assertEqual(candidate.statements[0].encounter_semantics.related_statement_ids, ())
        self.assertEqual(candidate.statements[0].upstream_reference_ids, ())
        self.assertEqual(candidate.statements[0].obligation_ids, ())
        forbidden_fields = {
            "template",
            "component",
            "layout",
            "html",
            "css",
            "javascript",
            "api",
            "persistence",
            "renderer",
            "browser",
            "dashboard",
            "portal",
        }
        candidate_fields = {field.name for field in fields(CandidatePresentationPackage)}
        self.assertFalse(candidate_fields & forbidden_fields)

    def test_builder_preserves_semantic_fingerprint(self):
        from briefforge.runtime import semantic_fingerprint

        self.assertEqual(semantic_fingerprint(builder_small_candidate()), semantic_fingerprint(manual_small_candidate()))

    def test_builder_recreates_task_014_denmark_profile_with_unchanged_fingerprint(self):
        from briefforge.runtime import semantic_fingerprint

        manual_candidate = denmark_country_profile_candidate()
        builder_candidate = denmark_country_profile_candidate_built_with_builder()

        self.assertEqual(builder_candidate, manual_candidate)
        self.assertEqual(semantic_fingerprint(builder_candidate), EXPECTED_TASK_014_FINGERPRINT)
        self.assertEqual(semantic_fingerprint(builder_candidate), semantic_fingerprint(manual_candidate))

    def test_builder_built_denmark_profile_crosses_existing_workflow_unchanged(self):
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.renderer_adapter import (
            check_rendered_artifact_conformance,
            check_renderer_adapter_compatibility,
            html_renderer_contract,
            invoke_renderer_adapter,
            render_minimal_html,
        )
        from briefforge.validation import validate_candidate_presentation_package

        candidate = denmark_country_profile_candidate_built_with_builder()
        judgment = validate_candidate_presentation_package(candidate)
        ready = promote_candidate_presentation_package(candidate, judgment)
        contract = html_renderer_contract()
        compatibility = check_renderer_adapter_compatibility(ready, contract)
        invocation_result = invoke_renderer_adapter(ready, contract)
        artifact = render_minimal_html(ready, contract)
        conformance = check_rendered_artifact_conformance(ready, artifact)

        self.assertTrue(judgment.valid, judgment.findings)
        self.assertTrue(compatibility.compatible)
        self.assertTrue(invocation_result.accepted)
        self.assertTrue(conformance.conforms, conformance.findings)
        self.assertIn("Denmark", artifact.html)


if __name__ == "__main__":
    unittest.main()
