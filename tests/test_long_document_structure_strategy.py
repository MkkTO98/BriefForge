"""TASK-024 Long-Document Structure Strategy tests.

These tests require renderer-level organization for large analytical reports.
They must not change runtime objects, Presentation Package shape, Presentation
Grammar, templates, browser applications, JavaScript, CSS frameworks, dashboards,
portals, search, visualization systems, or APIs.
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

from test_large_report_stress_validation import large_report_candidate_package  # noqa: E402


def large_report_ready_package():
    from briefforge.promotion import promote_candidate_presentation_package
    from briefforge.validation import validate_candidate_presentation_package

    candidate = large_report_candidate_package()
    judgment = validate_candidate_presentation_package(candidate)
    return promote_candidate_presentation_package(candidate, judgment)


def large_report_html():
    from briefforge.renderer_adapter import render_minimal_html

    return render_minimal_html(large_report_ready_package()).html


class LongDocumentStructureStrategyTests(unittest.TestCase):
    def test_large_reports_are_organized_into_evidence_derived_document_regions(self):
        html = large_report_html()

        expected_regions = (
            "front-matter",
            "core-narrative",
            "supporting-evidence",
            "references",
            "obligations",
            "audit-metadata",
        )
        for region in expected_regions:
            self.assertIn(f'data-long-document-region="{region}"', html)

        self.assertIn("Long-document structure", html)
        self.assertIn('href="#long-document-region-core-narrative"', html)
        self.assertIn('href="#long-document-region-supporting-evidence"', html)
        self.assertIn('href="#long-document-region-references"', html)
        self.assertIn('href="#long-document-region-obligations"', html)

        positions = [html.index(f'data-long-document-region="{region}"') for region in expected_regions]
        self.assertEqual(positions, sorted(positions))

    def test_existing_semantic_statement_order_is_preserved_inside_core_narrative(self):
        ready = large_report_ready_package()
        html = large_report_html()

        core_start = html.index('data-long-document-region="core-narrative"')
        evidence_start = html.index('data-long-document-region="supporting-evidence"')
        core_html = html[core_start:evidence_start]

        ordered_positions = []
        for statement in ready.candidate.statements:
            marker = f'data-statement-id="{statement.statement_id}"'
            self.assertIn(marker, core_html)
            ordered_positions.append(core_html.index(marker))
        self.assertEqual(ordered_positions, sorted(ordered_positions))

    def test_references_are_in_designated_region_while_statement_evidence_links_remain(self):
        html = large_report_html()

        core_start = html.index('data-long-document-region="core-narrative"')
        references_start = html.index('data-long-document-region="references"')
        obligations_start = html.index('data-long-document-region="obligations"')
        core_html = html[core_start:references_start]
        references_html = html[references_start:obligations_start]

        self.assertIn("Reference inventory", references_html)
        self.assertIn('id="reference-ref-insightforge-hypothesis-validation-report"', references_html)
        self.assertIn('href="#reference-ref-insightforge-hypothesis-validation-report"', core_html)
        self.assertIn("Evidence links", core_html)

        # TASK-023 evidence showed repeated local source-owner scaffolding was noisy.
        self.assertNotIn("Source owner:", core_html)
        self.assertIn("Source owner:", references_html)

    def test_obligations_are_contextual_links_and_grouped_without_repeated_local_scaffolding(self):
        html = large_report_html()

        core_start = html.index('data-long-document-region="core-narrative"')
        obligations_start = html.index('data-long-document-region="obligations"')
        audit_start = html.index('data-long-document-region="audit-metadata"')
        core_html = html[core_start:obligations_start]
        obligations_html = html[obligations_start:audit_start]

        self.assertIn("Obligation inventory", obligations_html)
        self.assertIn('id="obligation-obl-preserve-upstream-report-wording"', obligations_html)
        self.assertIn('href="#obligation-obl-preserve-upstream-report-wording"', core_html)
        self.assertIn("Obligation links", core_html)
        self.assertIn("Grouped obligations", obligations_html)

        # Local obligation links remain contextual, but repeated category scaffolding is removed.
        self.assertNotIn("Contextual obligations", core_html)
        self.assertIn("source-fidelity", obligations_html)

    def test_existing_conformance_continues_unchanged(self):
        from briefforge.renderer_adapter import check_rendered_artifact_conformance, render_minimal_html

        ready = large_report_ready_package()
        artifact = render_minimal_html(ready)
        conformance = check_rendered_artifact_conformance(ready, artifact)

        self.assertTrue(conformance.conforms, conformance.findings)
        self.assertEqual(artifact.package_identity, ready.candidate.identity)
        self.assertEqual(artifact.semantic_fingerprint, ready.semantic_fingerprint)
        self.assertEqual(artifact.validation_policy_id, ready.validation_policy_id)
        self.assertIn(ready.semantic_fingerprint, artifact.html)
        self.assertIn(ready.validation_policy_id, artifact.html)

    def test_existing_runtime_objects_remain_unchanged(self):
        import briefforge.runtime as runtime
        from briefforge.renderer_adapter import HtmlRenderedArtifact
        from briefforge.runtime import CandidatePresentationPackage, PresentationStatement, UpstreamReference

        self.assertFalse(hasattr(runtime, "LongDocumentStructureStrategy"))
        self.assertFalse(hasattr(runtime, "DocumentRegion"))
        self.assertFalse(hasattr(runtime, "ReportSection"))
        self.assertFalse(hasattr(runtime, "NavigationPlan"))
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
        self.assertEqual(
            tuple(field.name for field in fields(HtmlRenderedArtifact)),
            ("html", "adapter_identity", "package_identity", "semantic_fingerprint", "validation_policy_id"),
        )

    def test_renderer_remains_static_html_only(self):
        html = large_report_html().lower()

        forbidden_terms = (
            "<script",
            "bootstrap",
            "tailwind",
            "react",
            "data-template",
            "data-dashboard",
            "data-portal",
            "<canvas",
            "<svg",
            "fetch(",
        )
        for term in forbidden_terms:
            self.assertNotIn(term, html)


if __name__ == "__main__":
    unittest.main()
