"""Tests for the minimal Candidate Presentation Package runtime representation.

These tests intentionally cover representation only. They must not require
validation, rendering, serialization, HTML, browser behavior, templates, APIs,
persistence, networking, visualization, exports, or downstream consumers.
"""

from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))


class CandidatePresentationPackageTests(unittest.TestCase):
    def test_candidate_package_represents_only_frozen_constitutional_concepts(self):
        from briefforge.runtime import (
            CandidatePresentationPackage,
            EncounterSemantics,
            OrganizingPurpose,
            PackageIdentity,
            PresentationObligation,
            PresentationStatement,
            UpstreamReference,
        )

        identity = PackageIdentity(
            package_id="bf-candidate-001",
            title="Monthly GDP presentation package",
            purpose_summary="Present reviewed GDP movement context without owning analysis.",
            scope="Presentation-local organization of reviewed macroeconomic statements.",
            non_scope="No data ingestion, analysis, rendering, portal routing, or visualization.",
        )
        purpose = OrganizingPurpose(
            statement="Help a reader encounter reviewed GDP context coherently.",
            scope="Package-level presentation organization.",
            non_scope="Investment recommendation or analytical conclusion.",
        )
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
                description="This statement should be encountered before dependent commentary, independent of target medium.",
                related_statement_ids=("statement:dependent-commentary",),
            ),
            upstream_reference_ids=(reference.reference_id,),
            obligation_ids=(obligation.obligation_id,),
        )

        package = CandidatePresentationPackage(
            identity=identity,
            organizing_purpose=purpose,
            statements=(statement,),
            upstream_references=(reference,),
            obligations=(obligation,),
        )

        self.assertEqual(package.identity, identity)
        self.assertEqual(package.organizing_purpose, purpose)
        self.assertEqual(package.statements, (statement,))
        self.assertEqual(package.upstream_references, (reference,))
        self.assertEqual(package.obligations, (obligation,))

    def test_candidate_package_has_no_rendering_or_delivery_assumptions(self):
        from dataclasses import fields, is_dataclass

        from briefforge.runtime import (
            CandidatePresentationPackage,
            EncounterSemantics,
            OrganizingPurpose,
            PackageIdentity,
            PresentationObligation,
            PresentationStatement,
            UpstreamReference,
        )

        runtime_types = (
            CandidatePresentationPackage,
            PackageIdentity,
            OrganizingPurpose,
            PresentationStatement,
            EncounterSemantics,
            UpstreamReference,
            PresentationObligation,
        )
        forbidden_terms = {
            "renderer",
            "render",
            "browser",
            "template",
            "html",
            "dom",
            "css",
            "visualization",
            "visualisation",
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

        for runtime_type in runtime_types:
            self.assertTrue(is_dataclass(runtime_type), runtime_type)
            field_names = {field.name.lower() for field in fields(runtime_type)}
            for forbidden in forbidden_terms:
                self.assertFalse(
                    any(forbidden in field_name for field_name in field_names),
                    f"{runtime_type.__name__} leaks delivery/rendering assumption {forbidden!r}",
                )


if __name__ == "__main__":
    unittest.main()
