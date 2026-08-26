"""Tests for constitutional validation of Candidate Presentation Packages.

These tests cover validation only. They must not require promotion, Ready
Presentation Packages, rendering, serialization, HTML, browser behavior,
templates, APIs, persistence, networking, visualization, exports, or downstream
consumers.
"""

from copy import deepcopy
from dataclasses import fields, is_dataclass
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

from briefforge.runtime import (  # noqa: E402
    CandidatePresentationPackage,
    EncounterSemantics,
    OrganizingPurpose,
    PackageIdentity,
    PresentationObligation,
    PresentationStatement,
    UpstreamReference,
)


def valid_candidate_package() -> CandidatePresentationPackage:
    reference = UpstreamReference(
        reference_id="macroforge:gdp:2026-06",
        owning_project="MacroForge",
        reference_kind="reviewed macroeconomic observation",
        locator="macroforge://reports/gdp/2026-06",
        owned_meaning="GDP observation, caveats, provenance, confidence, and freshness remain upstream-owned.",
    )
    obligation = PresentationObligation(
        obligation_id="obligation:ownership-visible",
        category="ownership visibility",
        requirement="Keep MacroForge ownership visible wherever the referenced GDP observation is encountered.",
        applies_to=(reference.reference_id,),
    )
    statement = PresentationStatement(
        statement_id="statement:gdp-context",
        encounter_meaning="Encounter reviewed GDP context before dependent presentation commentary.",
        belongs_to_purpose="GDP context is required for the package's bounded presentation purpose.",
        encounter_semantics=EncounterSemantics(
            mode="ordered-before",
            description="Encounter before dependent commentary, independent of target medium.",
            related_statement_ids=(),
        ),
        upstream_reference_ids=(reference.reference_id,),
        obligation_ids=(obligation.obligation_id,),
    )
    return CandidatePresentationPackage(
        identity=PackageIdentity(
            package_id="bf-candidate-001",
            title="Monthly GDP presentation package",
            purpose_summary="Present reviewed GDP movement context without owning analysis.",
            scope="Presentation-local organization of reviewed macroeconomic statements.",
            non_scope="No data ingestion, analysis, rendering, portal routing, or visualization.",
        ),
        organizing_purpose=OrganizingPurpose(
            statement="Help a reader encounter reviewed GDP context coherently.",
            scope="Package-level presentation organization.",
            non_scope="Investment recommendation or analytical conclusion.",
        ),
        statements=(statement,),
        upstream_references=(reference,),
        obligations=(obligation,),
    )


class ConstitutionalValidationTests(unittest.TestCase):
    def test_valid_candidate_produces_successful_validation_judgment_without_mutation(self):
        from briefforge.validation import validate_candidate_presentation_package

        package = valid_candidate_package()
        before = deepcopy(package)

        judgment = validate_candidate_presentation_package(package)

        self.assertTrue(judgment.valid)
        self.assertEqual(judgment.findings, ())
        self.assertEqual(package, before)
        self.assertIsNot(judgment, package)

    def test_missing_identity_fails_validation(self):
        from briefforge.validation import validate_candidate_presentation_package

        package = valid_candidate_package()
        package_without_identity = CandidatePresentationPackage(
            identity=None,
            organizing_purpose=package.organizing_purpose,
            statements=package.statements,
            upstream_references=package.upstream_references,
            obligations=package.obligations,
        )

        judgment = validate_candidate_presentation_package(package_without_identity)

        self.assertFalse(judgment.valid)
        self.assert_finding(judgment, "package identity")

    def test_missing_organizing_purpose_fails_validation(self):
        from briefforge.validation import validate_candidate_presentation_package

        package = valid_candidate_package()
        package_without_purpose = CandidatePresentationPackage(
            identity=package.identity,
            organizing_purpose=None,
            statements=package.statements,
            upstream_references=package.upstream_references,
            obligations=package.obligations,
        )

        judgment = validate_candidate_presentation_package(package_without_purpose)

        self.assertFalse(judgment.valid)
        self.assert_finding(judgment, "organizing purpose")

    def test_missing_required_obligations_fails_validation(self):
        from briefforge.validation import validate_candidate_presentation_package

        package = valid_candidate_package()
        package_without_obligations = CandidatePresentationPackage(
            identity=package.identity,
            organizing_purpose=package.organizing_purpose,
            statements=package.statements,
            upstream_references=package.upstream_references,
            obligations=(),
        )

        judgment = validate_candidate_presentation_package(package_without_obligations)

        self.assertFalse(judgment.valid)
        self.assert_finding(judgment, "presentation obligations")

    def test_invalid_reference_relationships_fail_validation(self):
        from briefforge.validation import validate_candidate_presentation_package

        package = valid_candidate_package()
        statement = package.statements[0]
        statement_with_missing_reference = PresentationStatement(
            statement_id=statement.statement_id,
            encounter_meaning=statement.encounter_meaning,
            belongs_to_purpose=statement.belongs_to_purpose,
            encounter_semantics=statement.encounter_semantics,
            upstream_reference_ids=("macroforge:missing-reference",),
            obligation_ids=statement.obligation_ids,
        )
        package_with_missing_reference = CandidatePresentationPackage(
            identity=package.identity,
            organizing_purpose=package.organizing_purpose,
            statements=(statement_with_missing_reference,),
            upstream_references=package.upstream_references,
            obligations=package.obligations,
        )

        judgment = validate_candidate_presentation_package(package_with_missing_reference)

        self.assertFalse(judgment.valid)
        self.assert_finding(judgment, "upstream references")

    def test_validation_judgment_has_no_promotion_or_delivery_assumptions(self):
        from briefforge.validation import ValidationFinding, ValidationJudgment

        self.assertTrue(is_dataclass(ValidationFinding))
        self.assertTrue(is_dataclass(ValidationJudgment))

        forbidden_terms = {
            "ready",
            "promotion",
            "promote",
            "renderer",
            "render",
            "browser",
            "template",
            "html",
            "visualization",
            "chart",
            "map",
            "dashboard",
            "export",
            "api",
            "network",
            "persistence",
            "database",
            "route",
            "portal",
        }
        for runtime_type in (ValidationFinding, ValidationJudgment):
            field_names = {field.name.lower() for field in fields(runtime_type)}
            for forbidden in forbidden_terms:
                self.assertFalse(
                    any(forbidden in field_name for field_name in field_names),
                    f"{runtime_type.__name__} leaks excluded assumption {forbidden!r}",
                )

    def assert_finding(self, judgment, concept_fragment: str):
        concepts = "\n".join(finding.constitutional_concept.lower() for finding in judgment.findings)
        reasons = "\n".join(finding.reason.lower() for finding in judgment.findings)
        self.assertIn(concept_fragment, concepts + "\n" + reasons)


if __name__ == "__main__":
    unittest.main()
