"""Generate TASK-030 BriefForge v0.3 reader-experience showcase artifacts.

This script intentionally uses existing BriefForge runtime/promotion/validation and
the existing TASK-023 large-report candidate helper. It does not implement
BriefForge features or author new analytical source content.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "tests"))

from test_large_report_stress_validation import SOURCE_REPORT, large_report_candidate_package  # noqa: E402
from briefforge.promotion import promote_candidate_presentation_package  # noqa: E402
from briefforge.renderer_adapter import check_rendered_artifact_conformance, render_minimal_html  # noqa: E402
from briefforge.validation import validate_candidate_presentation_package  # noqa: E402

ARTIFACT_DIR = PROJECT_ROOT / "artifacts" / "presentations" / "TASK-030-briefforge-v0.3-reader-experience-showcase"


def json_ready(value: object) -> object:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, tuple):
        return [json_ready(item) for item in value]
    if isinstance(value, list):
        return [json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    return value


def write_text(name: str, content: str) -> None:
    (ARTIFACT_DIR / name).write_text(content, encoding="utf-8")


def write_json(name: str, value: object) -> None:
    write_text(name, json.dumps(json_ready(value), indent=2, sort_keys=True))


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    source_text = SOURCE_REPORT.read_text(encoding="utf-8")
    candidate = large_report_candidate_package()
    judgment = validate_candidate_presentation_package(candidate)
    ready = promote_candidate_presentation_package(candidate, judgment)
    artifact = render_minimal_html(ready)
    conformance = check_rendered_artifact_conformance(ready, artifact)
    html = artifact.html
    lowered_html = html.lower()

    write_text("selected_upstream_artifact.md", source_text)
    write_json("validation_judgment.json", judgment)
    write_json("ready_presentation_package.json", ready)
    write_text("briefforge_v0_3_reader_experience_showcase.html", html)
    write_json("rendered_artifact_conformance.json", conformance)

    metrics = {
        "task": "TASK-030",
        "renderer": artifact.adapter_identity.adapter_id,
        "reader_experience": "static-v0.3",
        "selected_source": str(SOURCE_REPORT),
        "html_bytes": len(html.encode("utf-8")),
        "source_characters": len(source_text),
        "statement_count": len(candidate.statements),
        "upstream_reference_count": len(candidate.upstream_references),
        "obligation_count": len(candidate.obligations),
        "semantic_fingerprint": artifact.semantic_fingerprint,
        "validation_policy_id": artifact.validation_policy_id,
        "conformance": conformance.conforms,
        "conformance_findings": list(conformance.findings),
        "contains_script": "<script" in lowered_html,
        "contains_style": "<style" in lowered_html,
        "contains_css_framework_terms": any(term in lowered_html for term in ("bootstrap", "tailwind", "react")),
        "contains_dashboard_or_portal_terms": any(term in lowered_html for term in ("data-dashboard", "data-portal")),
    }
    write_json("renderer_audit_metadata.json", metrics)

    write_text(
        "reader_evaluation.md",
        f"""# TASK-030 Reader Evaluation — BriefForge v0.3 Reader Experience Showcase

Status: complete
Selected artifact: `{SOURCE_REPORT}`
Rendered artifact: `briefforge_v0_3_reader_experience_showcase.html`

## Selection rationale

The selected InsightForge hypothesis validation pressure-test report remains the strongest current EIP analytical artifact for this showcase because it exercises the most BriefForge capabilities at once:

- substantial real analytical material ({len(source_text)} source characters);
- long-form analytical structure;
- explicit hypotheses, caveats, missing evidence, failure modes, readiness judgment, and recommendation;
- upstream ownership preservation;
- multiple references and obligations;
- existing BriefForge transformation, validation, promotion, and rendering path from TASK-023/TASK-025.

No new analytical content was authored. BriefForge presents existing InsightForge material.

## First impression

The v0.3 output now feels like a serious static report rather than raw browser-default HTML. The constrained page width, warm background, card-like sections, clearer heading scale, and evidence/audit regions make the artifact immediately more credible to a technically literate reader.

The first impression is still not professional-publication grade. The content begins with a long upstream scope statement and then repeats it as the first core narrative article. The report looks governed and readable, but not editorially designed.

## Readability

Improved materially versus v0.2:

- line length is constrained;
- line height is comfortable;
- sections have visible separation;
- paragraphs no longer run full-width across the browser;
- long-document regions are easier to scan.

Remaining weakness:

- upstream markdown bullet/list structure is still flattened into paragraph text inside statements;
- the first statement is duplicated as primary message and core narrative;
- repeated evidence/obligation links still interrupt the reader.

## Visual hierarchy

Strengths:

- title, purpose, primary message, core narrative, supporting evidence, references, obligations, and audit metadata are visually distinguishable;
- primary and supporting attention levels now have subtle visual treatment;
- long-document navigation appears as a report affordance rather than raw scaffolding.

Weaknesses:

- headings such as `Hypothesis Review` and `Analytical Section` are semantically correct but too generic for publication-grade orientation;
- the renderer cannot yet recover source subheadings as display headings without source-structure preservation work;
- no charts or data exhibits exist because the selected upstream artifact is text-heavy and BriefForge has no approved chart renderer.

## Typography and spacing

Strengths:

- static CSS provides professional-enough default typography;
- card spacing and max-width reduce fatigue;
- mobile sizing is bounded without a framework.

Weaknesses:

- typography is still generic system-font styling, not a fully designed publication identity;
- source text blocks remain dense because BriefForge preserves upstream wording.

## Evidence visibility

Strengths:

- evidence links remain near claims;
- reference inventory is recoverable;
- obligations are visible and grouped;
- audit metadata is present but tucked into a details block.

Weaknesses:

- repeated links still feel mechanical;
- reader-facing evidence-state prose is not yet as elegant as institutional methodology/source notes.

## Charts or lack thereof

The absence of charts is honest. The selected report is primarily a governance/analytical-methodology artifact, not a quantitative exhibit. BriefForge should not invent charts.

Professional readers will still notice the gap: IMF, OWID, McKinsey, and FT all use visuals when they materially reduce cognitive load. BriefForge currently cannot express chart/table/map decisions at renderer level without future approved work.

## Reference usability

References are usable and auditable. Anchor links work in a static browser. The grouped reference region is one of BriefForge's strongest publication qualities.

Reference usability remains below professional level because repeated local links are visually noisy and source notes are not yet compressed into reader-friendly disclosures.

## Long-document comfort

Long-document comfort improved from v0.2 because static styling makes the existing long-document regions useful in practice. It is now possible to read the report without immediate fatigue.

The biggest remaining comfort issue is source-structure flattening: bullets, numbered lists, and nested sections are represented as text inside statement paragraphs rather than as semantic HTML lists/headings.

## Professional appearance

The report now clears the threshold for a credible internal/publication-preview artifact. It does not yet match professional publication quality.

Best current strengths:

1. Strong auditability.
2. Clear ownership boundary.
3. Traceable references and obligations.
4. Static, portable HTML.
5. Better visual comfort after RB-001 renderer-level polish.

Largest remaining professional gap:

Source-structure preservation. The report has professional framing, but the core analytical content still loses upstream list/table/heading structure. This produces dense paragraphs where professional exemplars would use bullets, exhibits, callouts, or structured methodology notes.
""",
    )

    write_text(
        "professional_comparison.md",
        """# TASK-030 Professional Exemplar Comparison

## IMF

IMF reports combine executive framing, careful uncertainty language, charts/tables, and methodology/source notes. BriefForge currently matches the audit/governance instinct but lacks publication-grade exhibit design and source-note elegance.

Single relevant gap: source/evidence disclosures are mechanically traceable but not yet institutionally polished.

## Our World in Data

OWID excels at chart-first explanatory clarity, visible source/method notes, and narrative around data. BriefForge should not imitate OWID by adding charts prematurely. The relevant lesson is that evidence context should travel with the claim in a reader-friendly way.

Single relevant gap: BriefForge has traceability, but not yet reader-friendly evidence-state presentation.

## McKinsey

McKinsey reports emphasize executive takeaway, exhibit hierarchy, and controlled visual density. BriefForge's static report is now more readable, but the lead and section hierarchy remain generated from semantic scaffolding rather than editorial exhibit design.

Single relevant gap: the primary message is still structurally duplicated and not packaged as a concise executive exhibit.

## Financial Times Visual Journalism

FT visual journalism uses narrative pacing, annotations, spatial hierarchy, and visual evidence. BriefForge currently has no approved visualization layer and should not add one here. The relevant comparison is pacing: FT reduces reader inference burden; BriefForge preserves evidence but asks the reader to work through dense source text.

Single relevant gap: BriefForge lacks source-structure preservation and editorial pacing inside the core narrative.

## Largest remaining gap

The single largest remaining gap is source-structure preservation in rendered core narrative.

Why this is larger than charts:

- charts would be inappropriate for many existing reports;
- source-structure flattening affects every long analytical artifact with bullets, headings, lists, or tables;
- fixing it can remain renderer-level only if existing statement text/source material contains recoverable Markdown structure;
- it directly improves readability without introducing dashboards, JavaScript, templates, or runtime concepts.
""",
    )

    write_text(
        "remaining_user_visible_shortcomings.md",
        """# TASK-030 Ranked User-Visible Shortcomings

## 1. Source-structure flattening in core narrative

Classification: Renderer issue, with boundary investigation required.

Evidence:
- TASK-026 RB-004 repeated source-structure flattening.
- TASK-030 professional comparison shows the same issue in the showcase: upstream bullets/lists are present in source material but appear as dense paragraph text.

Recommendation:
- Promote RB-004 from Candidate with boundary uncertainty to Candidate requiring a focused renderer-only feasibility investigation.
- Do not modify Presentation Grammar unless renderer-only recovery proves impossible.

## 2. Primary-message duplication

Classification: Renderer issue.

Evidence:
- Existing RB-002 recurrence.
- TASK-030 repeats the selected report's scope both as Primary message and first core narrative article.

Recommendation:
- Keep RB-002 Candidate. This remains a small renderer display problem, not runtime or grammar pressure.

## 3. Repeated traceability links interrupt reading

Classification: Renderer issue.

Evidence:
- Existing RB-003 recurrence.
- TASK-030 still shows repeated per-statement evidence and obligation links.

Recommendation:
- Keep RB-003 Candidate. Future work should preserve auditability while improving evidence-state disclosure.

## 4. Generic section labels weaken publication orientation

Classification: Renderer issue, possible authoring/source-structure issue.

Evidence:
- Existing RB-005 recurrence.
- TASK-030 still shows repeated `Hypothesis Review` / `Analytical Section` labels instead of source-specific section titles.

Recommendation:
- Keep RB-005 Candidate and evaluate alongside source-structure preservation.

## 5. No approved chart/table exhibit rendering

Classification: Observation only.

Evidence:
- Professional exemplars use exhibits, but TASK-030's selected artifact is text-heavy.
- RB-007 remains below threshold.

Recommendation:
- Do not implement charts or visualization. Gather more table-heavy operational publications first.

## 6. Long-document navigation remains static and coarse

Classification: Observation only.

Evidence:
- TASK-030 benefits from static long-document structure but remains less comfortable than professional long-form reports.
- RB-008 remains below operational recurrence threshold.

Recommendation:
- Keep static only. Do not add JavaScript, search, sticky navigation, portal, or browser app behavior.
""",
    )

    write_text(
        "browser_screenshot_record.md",
        """# TASK-030 Browser Screenshot Record

Status: pending browser capture at generation time.

Primary HTML artifact:
- `briefforge_v0_3_reader_experience_showcase.html`

Planned screenshots, if browser tooling is available:
- opening viewport;
- mid-report core narrative;
- references/audit region.

If no screenshot files are present beside this record, use the HTML artifact directly in a browser. The showcase is static HTML and requires no server, JavaScript, dashboard, portal, API, or external asset.
""",
    )

    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0 if conformance.conforms else 1


if __name__ == "__main__":
    raise SystemExit(main())
