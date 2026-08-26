"""Experimental tests for TASK-027 Communication Intent.

These tests exercise a non-canonical layer that derives communication intent
from existing semantic content. They must not modify or replace runtime,
validation, promotion, Presentation Grammar, or renderer behavior.
"""

import json
from dataclasses import fields
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
TESTS = PROJECT_ROOT / "tests"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(TESTS))

from test_country_profile_presentation_model import denmark_country_profile_model_candidate
from test_country_comparison_presentation_model import denmark_germany_comparison_candidate
from test_investment_thesis_presentation_model import renewable_grid_investment_thesis_candidate


def candidate_from_json(path: Path):
    from briefforge.runtime import (
        CandidatePresentationPackage,
        EncounterSemantics,
        OrganizingPurpose,
        PackageIdentity,
        PresentationObligation,
        PresentationStatement,
        UpstreamReference,
    )

    raw = json.loads(path.read_text())
    candidate_raw = raw["candidate"] if "candidate" in raw else raw
    return CandidatePresentationPackage(
        identity=PackageIdentity(**candidate_raw["identity"]),
        organizing_purpose=OrganizingPurpose(**candidate_raw["organizing_purpose"]),
        upstream_references=tuple(UpstreamReference(**item) for item in candidate_raw["upstream_references"]),
        obligations=tuple(
            PresentationObligation(
                obligation_id=item["obligation_id"],
                category=item["category"],
                requirement=item["requirement"],
                applies_to=tuple(item["applies_to"]),
            )
            for item in candidate_raw["obligations"]
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
            for item in candidate_raw["statements"]
        ),
    )


class CommunicationIntentExperimentTests(unittest.TestCase):
    def test_intent_profile_derives_from_existing_country_profile_semantics(self):
        from briefforge.communication_intent_experiment import derive_communication_intent_profile

        profile = derive_communication_intent_profile(denmark_country_profile_model_candidate())

        self.assertEqual(profile.layer_status, "experimental-noncanonical")
        self.assertIn("orient", profile.package_intents)
        self.assertIn("quantify", profile.package_intents)
        self.assertIn("trace", profile.package_intents)
        self.assertEqual(len(profile.statement_intents), 6)

    def test_intent_profile_distinguishes_comparison_and_thesis_pressure(self):
        from briefforge.communication_intent_experiment import derive_communication_intent_profile

        comparison = derive_communication_intent_profile(denmark_germany_comparison_candidate())
        thesis = derive_communication_intent_profile(renewable_grid_investment_thesis_candidate())

        self.assertIn("compare", comparison.package_intents)
        self.assertIn("quantify", comparison.package_intents)
        self.assertIn("warn", thesis.package_intents)
        self.assertIn("qualify", thesis.package_intents)
        self.assertIn("conclude", thesis.package_intents)

    def test_large_report_derivation_exposes_reading_flow_intents_without_renderer_change(self):
        from briefforge.communication_intent_experiment import derive_communication_intent_profile

        candidate = candidate_from_json(
            PROJECT_ROOT
            / "artifacts"
            / "presentations"
            / "TASK-023-large-report-stress-validation"
            / "ready_presentation_package.json"
        )
        profile = derive_communication_intent_profile(candidate)

        self.assertGreaterEqual(len(profile.statement_intents), 30)
        self.assertIn("orient", profile.package_intents)
        self.assertIn("explain", profile.package_intents)
        self.assertIn("qualify", profile.package_intents)
        self.assertIn("conclude", profile.package_intents)
        self.assertTrue(all(intent.communication_strategy for intent in profile.statement_intents))

    def test_intent_layer_does_not_expand_frozen_runtime_validation_promotion_or_renderer_objects(self):
        from briefforge.runtime import CandidatePresentationPackage, PresentationStatement
        from briefforge.validation import ValidationJudgment
        from briefforge.promotion import ReadyPresentationPackage
        from briefforge.renderer_adapter import HtmlRenderedArtifact, RendererAdapterRequest

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
        self.assertNotIn("communication_intent", {field.name for field in fields(ValidationJudgment)})
        self.assertNotIn("communication_intent", {field.name for field in fields(ReadyPresentationPackage)})
        self.assertNotIn("communication_intent", {field.name for field in fields(RendererAdapterRequest)})
        self.assertNotIn("communication_intent", {field.name for field in fields(HtmlRenderedArtifact)})

    def test_intent_strategy_mapping_is_communication_strategy_not_renderer_implementation(self):
        from briefforge.communication_intent_experiment import CANONICAL_INTENTS, intent_strategy_mapping

        mapping = intent_strategy_mapping()
        forbidden_implementation_terms = (
            "html",
            "css",
            "javascript",
            "template",
            "dashboard",
            "portal",
            "browser app",
            "chart engine",
        )
        self.assertEqual(tuple(mapping), CANONICAL_INTENTS)
        for strategy in mapping.values():
            lowered = strategy.lower()
            self.assertFalse(
                any(term in lowered for term in forbidden_implementation_terms),
                strategy,
            )


if __name__ == "__main__":
    unittest.main()
