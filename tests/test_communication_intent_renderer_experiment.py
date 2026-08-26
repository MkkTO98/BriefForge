"""TASK-028 tests for the Communication Intent renderer experiment.

The experiment compares the existing static HTML renderer with one isolated
renderer variant that consumes the non-canonical Communication Intent layer. It
must not replace renderer_adapter behavior or change runtime, validation,
promotion, Presentation Package, Presentation Grammar, or constitutional files.
"""

import ast
import inspect
import json
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
TESTS = PROJECT_ROOT / "tests"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(TESTS))

from test_communication_intent_experiment import candidate_from_json  # noqa: E402

TASK_023_READY = (
    PROJECT_ROOT
    / "artifacts"
    / "presentations"
    / "TASK-023-large-report-stress-validation"
    / "ready_presentation_package.json"
)
TASK_028_DIR = PROJECT_ROOT / "artifacts" / "presentations" / "TASK-028-communication-intent-renderer-experiment"


def task_023_ready_package():
    from briefforge.promotion import promote_candidate_presentation_package
    from briefforge.validation import validate_candidate_presentation_package

    candidate = candidate_from_json(TASK_023_READY)
    judgment = validate_candidate_presentation_package(candidate)
    return promote_candidate_presentation_package(candidate, judgment)


class CommunicationIntentRendererExperimentTests(unittest.TestCase):
    def test_experimental_renderer_produces_static_html_from_task_023_without_replacing_current_renderer(self):
        from briefforge.communication_intent_renderer_experiment import render_communication_intent_html
        from briefforge.renderer_adapter import HtmlRenderedArtifact, render_minimal_html

        ready = task_023_ready_package()
        renderer_a = render_minimal_html(ready)
        renderer_b = render_communication_intent_html(ready)

        self.assertIsInstance(renderer_b, HtmlRenderedArtifact)
        self.assertNotEqual(renderer_a.adapter_identity.adapter_id, renderer_b.adapter_identity.adapter_id)
        self.assertEqual(renderer_b.adapter_identity.adapter_id, "communication-intent-html-experiment")
        self.assertEqual(renderer_b.package_identity, ready.candidate.identity)
        self.assertEqual(renderer_b.semantic_fingerprint, ready.semantic_fingerprint)
        self.assertEqual(renderer_b.validation_policy_id, ready.validation_policy_id)
        lowered = renderer_b.html.lower()
        self.assertIn("<!doctype html>", lowered)
        self.assertIn('data-experiment="communication-intent-renderer-v0.1"', lowered)
        self.assertIn('data-intent="orient"', lowered)
        self.assertIn('data-intent="explain"', lowered)
        self.assertIn('data-intent="qualify"', lowered)
        self.assertIn('data-intent="trace"', lowered)
        self.assertIn('data-intent="conclude"', lowered)
        self.assertNotIn("<script", lowered)
        self.assertNotIn("<style", lowered)
        self.assertNotIn('data-dashboard=', lowered)
        self.assertNotIn('data-portal=', lowered)
        self.assertNotIn("<canvas", lowered)
        self.assertNotIn("<svg", lowered)

    def test_intent_renderer_aligns_sections_to_presentation_architecture_patterns(self):
        from briefforge.communication_intent_renderer_experiment import render_communication_intent_html

        html = render_communication_intent_html(task_023_ready_package()).html

        expected_sequence = (
            "Executive capsule",
            "Claim-evidence-implication flow",
            "Uncertainty and risk",
            "Evidence register",
            "Methodology and obligations",
            "Bounded synthesis",
        )
        positions = [html.index(label) for label in expected_sequence]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("Communication Pattern Library", html)
        self.assertIn("Visualization Decision Framework", html)
        self.assertIn("Reader question", html)
        self.assertIn("no new visualization capability", html.lower())

    def test_complexity_metrics_show_intent_renderer_reduces_branching_against_current_renderer_path(self):
        from briefforge import communication_intent_renderer_experiment as intent_renderer
        from briefforge import renderer_adapter

        metrics = intent_renderer.compare_renderer_complexity(renderer_adapter, intent_renderer)

        self.assertGreater(metrics["renderer_a_branching_points"], metrics["renderer_b_branching_points"])
        self.assertLess(metrics["renderer_b_renderer_heuristic_functions"], metrics["renderer_a_renderer_heuristic_functions"])
        self.assertIn("branching_reduced", metrics)
        self.assertTrue(metrics["branching_reduced"])

    def test_side_by_side_comparison_recommends_keep_experimental_not_adoption(self):
        from briefforge.communication_intent_renderer_experiment import build_task_028_comparison

        comparison = build_task_028_comparison(task_023_ready_package())

        self.assertEqual(comparison["recommendation"], "Keep Experimental")
        self.assertEqual(comparison["selected_publication"], "TASK-023 large InsightForge report")
        self.assertGreater(comparison["complexity"]["renderer_a_branching_points"], comparison["complexity"]["renderer_b_branching_points"])
        self.assertIn("improves section organization", comparison["evidence"])
        self.assertIn("does not prove adoption", comparison["evidence"])
        self.assertIn("Presentation Architecture", comparison["metaharvest_consultation"])

    def test_experiment_does_not_expand_frozen_runtime_or_current_renderer_objects(self):
        from dataclasses import fields
        from briefforge.promotion import ReadyPresentationPackage
        from briefforge.renderer_adapter import HtmlRenderedArtifact, RendererAdapterRequest, render_minimal_html
        from briefforge.runtime import CandidatePresentationPackage, PresentationStatement
        from briefforge.validation import ValidationJudgment

        self.assertEqual(tuple(field.name for field in fields(CandidatePresentationPackage)), ("identity", "organizing_purpose", "statements", "upstream_references", "obligations"))
        self.assertEqual(tuple(field.name for field in fields(PresentationStatement)), ("statement_id", "encounter_meaning", "belongs_to_purpose", "encounter_semantics", "upstream_reference_ids", "obligation_ids"))
        self.assertNotIn("communication_intent", {field.name for field in fields(ValidationJudgment)})
        self.assertNotIn("communication_intent", {field.name for field in fields(ReadyPresentationPackage)})
        self.assertNotIn("communication_intent", {field.name for field in fields(RendererAdapterRequest)})
        self.assertNotIn("communication_intent", {field.name for field in fields(HtmlRenderedArtifact)})
        self.assertEqual(render_minimal_html.__module__, "briefforge.renderer_adapter")


if __name__ == "__main__":
    unittest.main()
