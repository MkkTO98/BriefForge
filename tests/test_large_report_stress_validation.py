"""TASK-023 large-report stress validation.

This module transforms one existing large InsightForge analytical report into the
existing BriefForge pipeline. It intentionally adds no runtime concepts, no
workflow stage, no templates, no browser app, no CSS/JavaScript framework, no
visualization system, and no renderer optimization.
"""

from dataclasses import asdict, fields, is_dataclass
import json
from pathlib import Path
import re
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EIP_PROJECTS_ROOT = PROJECT_ROOT.parent
INSIGHTFORGE_ROOT = EIP_PROJECTS_ROOT / "InsightForge"
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

SOURCE_REPORT = (
    INSIGHTFORGE_ROOT
    / "artifacts"
    / "reports"
    / "R-20260619-hypothesis-validation-pressure-test.md"
)
ARTIFACT_DIR = PROJECT_ROOT / "artifacts" / "presentations" / "TASK-023-large-report-stress-validation"

EXPECTED_FILES = (
    "selected_upstream_artifact.md",
    "candidate_presentation_package.json",
    "validation_judgment.json",
    "ready_presentation_package.json",
    "human_centered_html_artifact.html",
    "rendered_artifact_conformance.json",
    "stress_evaluation.md",
    "stress_findings.json",
    "renderer_recommendations.md",
)


_HEADING_PATTERN = re.compile(r"^(#{2,3})\s+(.+)$")


def _slug(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return normalized[:72] or "section"


def _source_text() -> str:
    return SOURCE_REPORT.read_text(encoding="utf-8")


def _source_sections() -> tuple[dict[str, object], ...]:
    lines = _source_text().splitlines()
    headings: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        match = _HEADING_PATTERN.match(line)
        if match:
            headings.append((index, len(match.group(1)), match.group(2).strip()))

    sections: list[dict[str, object]] = []
    for ordinal, (start, level, heading) in enumerate(headings):
        end = headings[ordinal + 1][0] if ordinal + 1 < len(headings) else len(lines)
        body = "\n".join(line for line in lines[start + 1 : end]).strip()
        if not body:
            continue
        sections.append(
            {
                "ordinal": len(sections) + 1,
                "level": level,
                "heading": heading,
                "body": body,
                "line_start": start + 1,
                "line_end": end,
            }
        )
    return tuple(sections)


def _section_mode(heading: str) -> str:
    lower = heading.lower()
    if heading == "Scope":
        return "orientation"
    if "failure mode" in lower or "why not accepted" in lower:
        return "risk-caveat"
    if "evidence" in lower or "requirements" in lower or "readiness" in lower:
        return "evidence-requirement"
    if "recommendation" in lower:
        return "conclusion"
    if lower.startswith("h") and "—" in heading:
        return "hypothesis-review"
    return "analytical-section"


def _section_reference_ids(heading: str) -> tuple[str, ...]:
    refs = ["ref-insightforge-hypothesis-validation-report"]
    if heading.startswith("H1"):
        refs.extend(["ref-insightforge-finding-if-a-001", "ref-insightforge-finding-if-a-003"])
    if heading.startswith("H2"):
        refs.extend(["ref-insightforge-finding-if-a-003", "ref-insightforge-finding-if-a-004"])
    if heading.startswith("H3"):
        refs.extend(
            [
                "ref-insightforge-finding-if-a-001",
                "ref-insightforge-finding-if-a-002",
                "ref-insightforge-finding-if-a-003",
                "ref-insightforge-finding-if-a-004",
            ]
        )
    if heading.startswith("H4"):
        refs.append("ref-insightforge-finding-if-a-003")
    return tuple(dict.fromkeys(refs))


def _json_ready(value: object) -> object:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    return value


def large_report_candidate_package():
    from briefforge.builder import PresentationPackageBuilder

    sections = _source_sections()
    builder = (
        PresentationPackageBuilder()
        .identity(
            package_id="briefforge-task-023-large-report-stress-validation",
            title="InsightForge hypothesis validation pressure test presentation",
            purpose_summary=(
                "A large-report stress validation presenting an existing InsightForge analytical report "
                "through the existing BriefForge pipeline."
            ),
            scope=(
                "Renderer-independent organization of the selected InsightForge report's scope, hypothesis reviews, "
                "evidence requirements, failure modes, controlled pressure test, readiness assessment, and recommendation."
            ),
            non_scope=(
                "No new analysis, synthesis beyond the upstream report, browser application, template, dashboard, portal, "
                "CSS framework, JavaScript, visualization, search, persistence, API, or renderer infrastructure expansion."
            ),
        )
        .organizing_purpose(
            statement=(
                "Allow a reader to encounter the existing InsightForge hypothesis validation pressure test as a large "
                "analytical report while BriefForge owns only presentation organization and obligation preservation."
            ),
            scope="Transform an existing upstream analytical report into the existing Candidate Presentation Package shape.",
            non_scope="Do not author synthetic analytical content, optimize the renderer, or add workflow stages.",
        )
        .add_upstream_reference(
            reference_id="ref-insightforge-hypothesis-validation-report",
            owning_project="InsightForge",
            reference_kind="large-analytical-report",
            locator=str(SOURCE_REPORT),
            owned_meaning=(
                "InsightForge owns the report's analytical scope, hypothesis review, evidence requirements, "
                "failure-mode analysis, readiness assessment, and recommendation."
            ),
        )
        .add_upstream_reference(
            reference_id="ref-insightforge-finding-if-a-001",
            owning_project="InsightForge",
            reference_kind="supporting-reviewed-finding",
            locator="artifacts/analytical/IF-A-20260619-001-wdi-usa-dnk-gdp-direction.md",
            owned_meaning="InsightForge owns the WDI USA/DNK GDP direction finding cited by the report.",
        )
        .add_upstream_reference(
            reference_id="ref-insightforge-finding-if-a-002",
            owning_project="InsightForge",
            reference_kind="supporting-reviewed-finding",
            locator="artifacts/analytical/IF-A-20260619-002-eurostat-deu-fra-quarterly-direction.md",
            owned_meaning="InsightForge owns the Eurostat DEU/FRA quarterly direction finding cited by the report.",
        )
        .add_upstream_reference(
            reference_id="ref-insightforge-finding-if-a-003",
            owning_project="InsightForge",
            reference_kind="supporting-reviewed-finding",
            locator="artifacts/analytical/IF-A-20260619-003-oecd-unit-profile-comparison.md",
            owned_meaning="InsightForge owns the OECD unit-profile comparison finding cited by the report.",
        )
        .add_upstream_reference(
            reference_id="ref-insightforge-finding-if-a-004",
            owning_project="InsightForge",
            reference_kind="supporting-reviewed-finding",
            locator="artifacts/analytical/IF-A-20260619-004-cross-source-usa-comparability-boundary.md",
            owned_meaning="InsightForge owns the cross-source comparability boundary finding cited by the report.",
        )
        .add_obligation(
            obligation_id="obl-preserve-upstream-report-wording",
            category="source-fidelity",
            requirement="Preserve the upstream report's analytical wording; do not rewrite sections into new BriefForge conclusions.",
            applies_to=("ref-insightforge-hypothesis-validation-report",),
        )
        .add_obligation(
            obligation_id="obl-keep-hypotheses-non-accepted",
            category="analytical-boundary",
            requirement="Do not present reviewed hypotheses or controlled pressure tests as accepted analytical conclusions.",
            applies_to=("ref-insightforge-hypothesis-validation-report",),
        )
        .add_obligation(
            obligation_id="obl-maintain-source-ownership",
            category="source-ownership",
            requirement="Keep InsightForge as analytical owner and BriefForge as presentation organizer only.",
            applies_to=("ref-insightforge-hypothesis-validation-report",),
        )
        .add_obligation(
            obligation_id="obl-surface-caveats-and-failure-modes",
            category="uncertainty-visibility",
            requirement="Keep caveats, missing evidence, assumptions, and failure modes visible to the reader.",
            applies_to=("ref-insightforge-hypothesis-validation-report",),
        )
    )

    statement_ids = [f"stmt-large-report-{section['ordinal']:02d}-{_slug(str(section['heading']))}" for section in sections]
    for index, section in enumerate(sections):
        statement_id = statement_ids[index]
        related = []
        if index > 0:
            related.append(statement_ids[index - 1])
        if index + 1 < len(statement_ids):
            related.append(statement_ids[index + 1])
        heading = str(section["heading"])
        body = str(section["body"])
        line_start = int(section["line_start"])
        line_end = int(section["line_end"])
        obligations = ["obl-preserve-upstream-report-wording", "obl-maintain-source-ownership"]
        if any(term in heading.lower() or term in body.lower() for term in ("missing evidence", "assumptions", "failure mode", "why not accepted", "caveat")):
            obligations.append("obl-surface-caveats-and-failure-modes")
        if "hypothesis" in heading.lower() or heading.startswith("H"):
            obligations.append("obl-keep-hypotheses-non-accepted")
        builder.add_statement(
            statement_id=statement_id,
            encounter_meaning=f"{heading}\n\n{body}",
            belongs_to_purpose="InsightForge hypothesis validation pressure test",
            encounter_mode=_section_mode(heading),
            encounter_description=(
                f"Present upstream section lines {line_start}-{line_end} without analytical rewriting."
            ),
            related_statement_ids=tuple(related),
            upstream_reference_ids=_section_reference_ids(heading),
            obligation_ids=tuple(dict.fromkeys(obligations)),
        )
    return builder.build()


class LargeReportStressValidationTests(unittest.TestCase):
    def test_selected_report_is_significantly_larger_than_previous_insightforge_finding(self):
        previous = (
            INSIGHTFORGE_ROOT
            / "artifacts"
            / "analytical"
            / "IF-A-20260619-002-eurostat-deu-fra-quarterly-direction.md"
        )
        selected_text = _source_text()
        previous_text = previous.read_text(encoding="utf-8")
        sections = _source_sections()

        self.assertGreater(len(selected_text), 20000)
        self.assertGreater(len(selected_text), len(previous_text) * 4)
        self.assertGreaterEqual(len(sections), 25)
        self.assertIn("## 4. Failure-mode analysis", selected_text)
        self.assertIn("## 7. Recommendation", selected_text)

    def test_large_report_candidate_uses_existing_package_builder_and_runtime(self):
        from briefforge.runtime import CandidatePresentationPackage
        from briefforge.validation import validate_candidate_presentation_package

        candidate = large_report_candidate_package()
        judgment = validate_candidate_presentation_package(candidate)

        self.assertIs(type(candidate), CandidatePresentationPackage)
        self.assertTrue(judgment.valid, judgment.findings)
        self.assertEqual(candidate.identity.package_id, "briefforge-task-023-large-report-stress-validation")
        self.assertGreaterEqual(len(candidate.statements), 25)
        self.assertGreaterEqual(len(candidate.upstream_references), 5)
        self.assertGreaterEqual(len(candidate.obligations), 4)
        self.assertIn("H1 — Selected annual GDP rows", candidate.statements[1].encounter_meaning)
        self.assertIn("## 7. Recommendation", _source_text())

    def test_complete_existing_pipeline_handles_large_report_unchanged(self):
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.renderer_adapter import (
            check_rendered_artifact_conformance,
            check_renderer_adapter_compatibility,
            html_renderer_contract,
            invoke_renderer_adapter,
            render_minimal_html,
        )
        from briefforge.validation import validate_candidate_presentation_package

        candidate = large_report_candidate_package()
        judgment = validate_candidate_presentation_package(candidate)
        ready = promote_candidate_presentation_package(candidate, judgment)
        contract = html_renderer_contract()
        compatibility = check_renderer_adapter_compatibility(ready, contract)
        invocation = invoke_renderer_adapter(ready, contract)
        artifact = render_minimal_html(ready, contract)
        conformance = check_rendered_artifact_conformance(ready, artifact)

        self.assertTrue(compatibility.compatible)
        self.assertTrue(invocation.accepted)
        self.assertTrue(conformance.conforms, conformance.findings)
        self.assertIn("Hypothesis Review", artifact.html)
        self.assertIn("Failure mode 1", artifact.html)
        self.assertIn("Reference inventory", artifact.html)
        self.assertIn("Obligation inventory", artifact.html)
        self.assertIn("Validation and audit metadata", artifact.html)
        self.assertNotIn("<script", artifact.html.lower())
        self.assertIn("<style", artifact.html.lower())
        self.assertIn("data-reader-experience=\"static-v0.3\"", artifact.html.lower())

    def test_runtime_objects_and_existing_models_remain_unchanged(self):
        import briefforge.runtime as runtime
        from briefforge.presentation_models import (
            CountryComparisonPresentation,
            CountryProfilePresentation,
            InvestmentThesisPresentation,
        )
        from briefforge.runtime import CandidatePresentationPackage, PresentationStatement

        self.assertFalse(hasattr(runtime, "LargeReportPresentationPackage"))
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
        self.assertEqual(tuple(field.name for field in fields(CountryProfilePresentation)), ("country_name", "candidate"))
        self.assertEqual(tuple(field.name for field in fields(CountryComparisonPresentation)), ("compared_countries", "candidate"))
        self.assertEqual(tuple(field.name for field in fields(InvestmentThesisPresentation)), ("subject", "candidate"))

    def test_task_023_deliverable_files_exist_after_artifact_generation(self):
        missing = tuple(name for name in EXPECTED_FILES if not (ARTIFACT_DIR / name).is_file())
        self.assertEqual(missing, ())


if __name__ == "__main__":
    unittest.main()
