"""TASK-020 first InsightForge -> BriefForge integration proof.

This test proves one-way integration only. InsightForge remains the analytical
owner. BriefForge receives an upstream-authored finding and composes it into the
existing Candidate Presentation Package, then uses the existing validation,
promotion, renderer-adapter, minimal HTML, and conformance pipeline unchanged.
"""

from dataclasses import asdict, fields, is_dataclass
import json
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EIP_PROJECTS_ROOT = PROJECT_ROOT.parent
INSIGHTFORGE_ROOT = EIP_PROJECTS_ROOT / "InsightForge"
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

SOURCE_FINDING = (
    INSIGHTFORGE_ROOT
    / "artifacts"
    / "analytical"
    / "IF-A-20260619-002-eurostat-deu-fra-quarterly-direction.md"
)
ARTIFACT_DIR = PROJECT_ROOT / "artifacts" / "integrations" / "TASK-020-insightforge-briefing-proof"


EXPECTED_FILES = (
    "insightforge_analytical_artifact.md",
    "candidate_presentation_package.json",
    "validation_judgment.json",
    "ready_presentation_package.json",
    "minimal_html_artifact.html",
    "rendered_artifact_conformance.json",
    "integration_observations.md",
)


def _frontmatter_lines(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise AssertionError(f"{path} does not start with YAML-like frontmatter")
    end = lines.index("---", 1)
    return lines[1:end]


def _scalar(lines: list[str], key: str) -> str:
    prefix = f"{key}:"
    for line in lines:
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    raise AssertionError(f"missing frontmatter scalar: {key}")


def _list_after(lines: list[str], key: str) -> tuple[str, ...]:
    prefix = f"{key}:"
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            values: list[str] = []
            for follow in lines[index + 1 :]:
                if follow and not follow.startswith(" "):
                    break
                stripped = follow.strip()
                if stripped.startswith("- "):
                    values.append(stripped.removeprefix("- ").strip())
            return tuple(values)
    raise AssertionError(f"missing frontmatter list: {key}")


def _nested_scalar(lines: list[str], parent: str, key: str) -> str:
    parent_prefix = f"{parent}:"
    key_prefix = f"{key}:"
    in_parent = False
    for line in lines:
        if line.startswith(parent_prefix):
            in_parent = True
            continue
        if in_parent and line and not line.startswith(" "):
            break
        if in_parent and line.strip().startswith(key_prefix):
            return line.strip().removeprefix(key_prefix).strip()
    raise AssertionError(f"missing nested scalar: {parent}.{key}")


def _evidence_source_projects(lines: list[str]) -> tuple[str, ...]:
    projects: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("source_project:"):
            projects.append(stripped.removeprefix("source_project:").strip())
    return tuple(projects)


def _source_artifact_paths(lines: list[str]) -> tuple[str, ...]:
    paths: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("source_artifact:"):
            paths.append(stripped.removeprefix("source_artifact:").strip())
    return tuple(paths)


def selected_insightforge_finding() -> dict[str, object]:
    lines = _frontmatter_lines(SOURCE_FINDING)
    return {
        "id": _scalar(lines, "id"),
        "subtype": _scalar(lines, "subtype"),
        "status": _scalar(lines, "status"),
        "title": _scalar(lines, "title"),
        "question": _scalar(lines, "question"),
        "conclusion": _scalar(lines, "conclusion"),
        "caveats": _list_after(lines, "caveats"),
        "confidence_level": _nested_scalar(lines, "confidence", "level"),
        "confidence_justification": _nested_scalar(lines, "confidence", "justification"),
        "reproducibility_method": _nested_scalar(lines, "reproducibility", "method"),
        "evidence_source_projects": _evidence_source_projects(lines),
        "source_artifacts": _source_artifact_paths(lines),
        "source_path": str(SOURCE_FINDING),
    }


def insightforge_finding_candidate_package():
    from briefforge.builder import PresentationPackageBuilder

    finding = selected_insightforge_finding()
    finding_id = str(finding["id"])
    source_artifacts = tuple(str(path) for path in finding["source_artifacts"])
    caveats = tuple(str(caveat) for caveat in finding["caveats"])

    return (
        PresentationPackageBuilder()
        .identity(
            package_id="briefforge-task-020-insightforge-finding-proof",
            title=f"InsightForge finding memo: {finding['title']}",
            purpose_summary=(
                "A minimal one-way integration proof presenting an existing reviewed InsightForge finding "
                "without BriefForge changing the analytical conclusion."
            ),
            scope=(
                "Presentation-level organization of one existing InsightForge finding, its confidence, caveats, "
                "evidence ownership, and reproducibility method."
            ),
            non_scope=(
                "No automatic report generation, AI generation, analysis, data ownership, renderer-internal dependency, "
                "template, dashboard, portal, browser application, CSS, JavaScript, visualization, API, networking, "
                "or bidirectional coupling."
            ),
        )
        .organizing_purpose(
            statement=(
                "Allow a reader to encounter the upstream InsightForge finding as reviewed analytical content while "
                "BriefForge owns only presentation organization and obligation preservation."
            ),
            scope="Compose the finding question, conclusion, confidence, caveats, and reproducibility into one package.",
            non_scope="Do not create, revise, summarize into a new conclusion, or validate the analytical truth of the finding.",
        )
        .add_upstream_reference(
            reference_id="ref-insightforge-finding-if-a-20260619-002",
            owning_project="InsightForge",
            reference_kind="reviewed-analytical-finding",
            locator=str(finding["source_path"]),
            owned_meaning=(
                "InsightForge owns the reviewed question, conclusion, confidence, caveats, and reproducibility method "
                "for this finding."
            ),
        )
        .add_upstream_reference(
            reference_id="ref-macroforge-canonical-gdp-snapshot",
            owning_project="MacroForge",
            reference_kind="upstream-evidence-artifact",
            locator=source_artifacts[0],
            owned_meaning="MacroForge owns the canonical GDP observations and source lineage cited by InsightForge.",
        )
        .add_obligation(
            obligation_id="obl-preserve-insightforge-conclusion",
            category="analytical-boundary",
            requirement="Preserve the InsightForge-authored conclusion without rewriting it into a new analytical claim.",
            applies_to=("stmt-insightforge-conclusion",),
        )
        .add_obligation(
            obligation_id="obl-preserve-caveats",
            category="caveat-preservation",
            requirement="Present caveats and confidence with the finding; do not strip uncertainty for readability.",
            applies_to=("stmt-insightforge-confidence", "stmt-insightforge-caveats"),
        )
        .add_obligation(
            obligation_id="obl-keep-source-ownership-visible",
            category="source-ownership",
            requirement="Keep InsightForge as conclusion owner and MacroForge as evidence owner.",
            applies_to=(
                "ref-insightforge-finding-if-a-20260619-002",
                "ref-macroforge-canonical-gdp-snapshot",
                "stmt-insightforge-evidence-boundary",
            ),
        )
        .add_statement(
            statement_id="stmt-insightforge-question",
            encounter_meaning=f"InsightForge question: {finding['question']}",
            belongs_to_purpose=finding_id,
            encounter_mode="finding-question",
            encounter_description="Establish the upstream analytical question before presenting the conclusion.",
            related_statement_ids=("stmt-insightforge-conclusion",),
            upstream_reference_ids=("ref-insightforge-finding-if-a-20260619-002",),
            obligation_ids=("obl-keep-source-ownership-visible",),
        )
        .add_statement(
            statement_id="stmt-insightforge-conclusion",
            encounter_meaning=f"InsightForge conclusion: {finding['conclusion']}",
            belongs_to_purpose=finding_id,
            encounter_mode="finding-conclusion",
            encounter_description="Present the upstream-authored conclusion without BriefForge alteration.",
            related_statement_ids=("stmt-insightforge-question", "stmt-insightforge-confidence", "stmt-insightforge-caveats"),
            upstream_reference_ids=("ref-insightforge-finding-if-a-20260619-002",),
            obligation_ids=("obl-preserve-insightforge-conclusion",),
        )
        .add_statement(
            statement_id="stmt-insightforge-confidence",
            encounter_meaning=(
                f"InsightForge confidence: {finding['confidence_level']}. "
                f"Justification: {finding['confidence_justification']}"
            ),
            belongs_to_purpose=finding_id,
            encounter_mode="finding-confidence",
            encounter_description="Carry upstream confidence as routing metadata, not as BriefForge truth certification.",
            related_statement_ids=("stmt-insightforge-conclusion", "stmt-insightforge-caveats"),
            upstream_reference_ids=("ref-insightforge-finding-if-a-20260619-002",),
            obligation_ids=("obl-preserve-caveats",),
        )
        .add_statement(
            statement_id="stmt-insightforge-caveats",
            encounter_meaning="InsightForge caveats: " + " ".join(caveats),
            belongs_to_purpose=finding_id,
            encounter_mode="finding-caveats",
            encounter_description="Preserve scope limits before any reader treats the finding as broadly comparable or causal.",
            related_statement_ids=("stmt-insightforge-conclusion", "stmt-insightforge-evidence-boundary"),
            upstream_reference_ids=("ref-insightforge-finding-if-a-20260619-002",),
            obligation_ids=("obl-preserve-caveats",),
        )
        .add_statement(
            statement_id="stmt-insightforge-evidence-boundary",
            encounter_meaning=(
                "Evidence boundary: InsightForge cites MacroForge-owned canonical GDP evidence; BriefForge presents "
                "the reference relationship but does not verify, canonicalize, or reinterpret the GDP data."
            ),
            belongs_to_purpose=finding_id,
            encounter_mode="source-ownership-boundary",
            encounter_description="Make one-way ownership visible: InsightForge conclusion, MacroForge evidence, BriefForge presentation.",
            related_statement_ids=("stmt-insightforge-conclusion", "stmt-insightforge-reproducibility"),
            upstream_reference_ids=(
                "ref-insightforge-finding-if-a-20260619-002",
                "ref-macroforge-canonical-gdp-snapshot",
            ),
            obligation_ids=("obl-keep-source-ownership-visible",),
        )
        .add_statement(
            statement_id="stmt-insightforge-reproducibility",
            encounter_meaning=f"InsightForge reproducibility method: {finding['reproducibility_method']}",
            belongs_to_purpose=finding_id,
            encounter_mode="finding-reproducibility",
            encounter_description="Expose the upstream reproducibility method without creating a BriefForge analysis step.",
            related_statement_ids=("stmt-insightforge-evidence-boundary",),
            upstream_reference_ids=("ref-insightforge-finding-if-a-20260619-002",),
            obligation_ids=("obl-keep-source-ownership-visible",),
        )
        .build()
    )


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


class InsightForgeBriefForgeIntegrationProofTests(unittest.TestCase):
    def test_insightforge_finding_naturally_produces_valid_candidate_package(self):
        from briefforge.runtime import CandidatePresentationPackage
        from briefforge.validation import validate_candidate_presentation_package

        finding = selected_insightforge_finding()
        candidate = insightforge_finding_candidate_package()
        judgment = validate_candidate_presentation_package(candidate)

        self.assertEqual(finding["subtype"], "finding")
        self.assertEqual(finding["status"], "reviewed")
        self.assertIn("MacroForge", finding["evidence_source_projects"])
        self.assertIsInstance(candidate, CandidatePresentationPackage)
        self.assertTrue(judgment.valid, judgment.findings)
        self.assertEqual(candidate.identity.package_id, "briefforge-task-020-insightforge-finding-proof")
        self.assertIn("InsightForge finding memo", candidate.identity.title)

    def test_complete_existing_pipeline_passes_unchanged_for_insightforge_finding(self):
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.renderer_adapter import (
            check_rendered_artifact_conformance,
            check_renderer_adapter_compatibility,
            html_renderer_contract,
            invoke_renderer_adapter,
            render_minimal_html,
        )
        from briefforge.validation import validate_candidate_presentation_package

        candidate = insightforge_finding_candidate_package()
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
        self.assertIn("Germany", artifact.html)
        self.assertIn("France", artifact.html)
        self.assertIn("InsightForge conclusion", artifact.html)
        self.assertNotIn("<script", artifact.html.lower())
        self.assertIn("<style", artifact.html.lower())
        self.assertIn("data-reader-experience=\"static-v0.3\"", artifact.html.lower())

    def test_existing_runtime_abstractions_require_no_insightforge_special_case(self):
        import briefforge.runtime as runtime
        from briefforge.runtime import CandidatePresentationPackage

        candidate = insightforge_finding_candidate_package()
        candidate_fields = {field.name for field in fields(CandidatePresentationPackage)}

        self.assertIs(type(candidate), CandidatePresentationPackage)
        self.assertFalse(hasattr(runtime, "InsightForgeFinding"))
        self.assertFalse(hasattr(runtime, "IntegrationPackage"))
        self.assertFalse(
            candidate_fields
            & {
                "insightforge",
                "finding",
                "confidence",
                "caveats",
                "integration",
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

    def test_insightforge_does_not_need_renderer_internals_or_BriefForge_analysis(self):
        source_text = SOURCE_FINDING.read_text(encoding="utf-8").lower()
        candidate = insightforge_finding_candidate_package()

        self.assertNotIn("html", source_text)
        self.assertNotIn("renderer", source_text)
        self.assertNotIn("css", source_text)
        self.assertNotIn("javascript", source_text)
        self.assertEqual(candidate.upstream_references[0].owning_project, "InsightForge")
        self.assertEqual(candidate.upstream_references[1].owning_project, "MacroForge")
        self.assertIn("does not verify", candidate.statements[4].encounter_meaning)

    def test_semantic_fingerprint_is_deterministic(self):
        from briefforge.runtime import semantic_fingerprint

        first = insightforge_finding_candidate_package()
        second = insightforge_finding_candidate_package()

        self.assertEqual(first, second)
        self.assertEqual(semantic_fingerprint(first), semantic_fingerprint(second))

    def test_task_020_deliverable_files_exist_after_artifact_generation(self):
        missing = tuple(name for name in EXPECTED_FILES if not (ARTIFACT_DIR / name).is_file())
        self.assertEqual(missing, ())


if __name__ == "__main__":
    unittest.main()
