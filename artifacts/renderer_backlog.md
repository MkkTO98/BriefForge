# Renderer Backlog

Date initialized: 2026-07-03
Status: Active evidence ledger
Owner: BriefForge
Specification: `docs/renderer-backlog-specification.md`

## Governance rule

This backlog records reader friction. It does not authorize implementation by itself.

Renderer improvements require repeated operational evidence, renderer-only scope, and a separate approved implementation task.

## Relationship to decision-support backlog

The latest MetaHarvest usability review identified a higher-level decision-support backlog outside the renderer backlog.

- Decision-support backlog: `artifacts/decision_support_backlog.md`
- Governance rule: do not implement renderer or UI work to solve MetaHarvest usability until the decision-support package model is defined and validated.
- Current next recommended workstream: `TASK-035 MetaHarvest Architectural Decision Package Model`.

## Entries

### RB-001 — Browser-default visual presentation

Identifier: RB-001

First observed publication:
- `TASK-026-operational-publication-trial/pub-01-insightforge-eurostat-finding`

Subsequent occurrences:
- `TASK-026-operational-publication-trial/pub-02-macroforge-canonical-gdp-snapshot`
- `TASK-026-operational-publication-trial/pub-03-insightforge-knowledge-accumulation-report`
- `TASK-030-briefforge-v0.3-reader-experience-showcase` confirmed that static typography, spacing, constrained line width, and section separation materially improve reader experience without runtime expansion.

Category:
- Renderer readability

Severity:
- High

Evidence:
- `artifacts/tasks/TASK-026-operational-publication-trial.md`, recurring patterns lines describing browser-default visual presentation across all three publications.
- `artifacts/presentations/TASK-026-operational-publication-trial/cross_publication_comparison.md`, repeated issue 1.
- `artifacts/presentations/TASK-030-briefforge-v0.3-reader-experience-showcase/reader_evaluation.md`, first-impression, readability, typography, and long-document comfort evaluation.

Proposed renderer improvement:
- Professional static report readability layer: better typography, spacing, constrained line width, section separation, and callout treatment while remaining static and audit-preserving.

Implementation status:
- Implemented as bounded renderer-level static CSS in TASK-030

Boundary assessment:
- Appears renderer-only if limited to static HTML readability. Must not introduce templates, CSS framework architecture, JavaScript, runtime concepts, dashboard/portal behavior, or semantic changes.

Threshold status:
- Meets recurrence threshold. Implemented only as static renderer-level readability polish in TASK-030; no templates, JavaScript, browser application, dashboard, runtime concept, Presentation Grammar change, or Presentation Model change introduced.

---

### RB-002 — Primary-message duplication

Identifier: RB-002

First observed publication:
- `TASK-026-operational-publication-trial/pub-01-insightforge-eurostat-finding`

Subsequent occurrences:
- `TASK-026-operational-publication-trial/pub-02-macroforge-canonical-gdp-snapshot`
- `TASK-026-operational-publication-trial/pub-03-insightforge-knowledge-accumulation-report`
- `TASK-030-briefforge-v0.3-reader-experience-showcase` repeated the issue: the selected report's scope appears both as the Primary message and as the first core-narrative article.

Category:
- Renderer readability / narrative flow

Severity:
- Medium

Evidence:
- `artifacts/tasks/TASK-026-operational-publication-trial.md`, recurring renderer deficiencies.
- `artifacts/presentations/TASK-026-operational-publication-trial/cross_publication_comparison.md`, repeated issue 2.

Proposed renderer improvement:
- Avoid rendering the same leading statement twice when it already appears as the primary message; preserve statement identity and traceability without visible repetition.

Implementation status:
- Candidate

Boundary assessment:
- Likely renderer-only. Must not alter package contents, statement IDs, validation, promotion, or semantic fingerprints.

Threshold status:
- Meets recurrence threshold. Not approved for implementation by this task.

---

### RB-003 — Repeated traceability links create reading noise

Identifier: RB-003

First observed publication:
- `TASK-026-operational-publication-trial/pub-01-insightforge-eurostat-finding`

Subsequent occurrences:
- `TASK-026-operational-publication-trial/pub-02-macroforge-canonical-gdp-snapshot`
- `TASK-026-operational-publication-trial/pub-03-insightforge-knowledge-accumulation-report`
- `TASK-028-communication-intent-renderer-experiment` comparison evidence also identified evidence-register/obligation placement as a communication issue.
- `TASK-030-briefforge-v0.3-reader-experience-showcase` repeated the issue: per-statement evidence and obligation links remain audit-useful but visually interrupt long-form reading.

Category:
- Traceability / evidence placement

Severity:
- High

Evidence:
- `artifacts/tasks/TASK-026-operational-publication-trial.md`, recurring renderer deficiencies.
- `artifacts/presentations/TASK-026-operational-publication-trial/cross_publication_comparison.md`, repeated issue 3.
- `artifacts/reports/R-20260703-communication-intent-renderer-experiment.md`, communication result on evidence and obligation placement.

Proposed renderer improvement:
- Traceability compression: keep references, obligations, statement IDs, and audit metadata inspectable while reducing repeated per-statement visual interruption.

Implementation status:
- Candidate

Boundary assessment:
- Renderer-only if it changes only display placement. Must preserve audit links and rendered artifact conformance.

Threshold status:
- Meets recurrence threshold. Not approved for implementation by this task.

---

### RB-004 — Source structure flattening

Identifier: RB-004

First observed publication:
- `TASK-026-operational-publication-trial/pub-02-macroforge-canonical-gdp-snapshot`

Subsequent occurrences:
- `TASK-026-operational-publication-trial/pub-03-insightforge-knowledge-accumulation-report`
- Partial occurrence in `TASK-026-operational-publication-trial/pub-01-insightforge-eurostat-finding` caveat presentation.
- `TASK-030-briefforge-v0.3-reader-experience-showcase` made this the largest professional-publication gap: upstream bullets/lists and nested structure remained visible only as flattened paragraph text.
- `TASK-031-renderer-source-structure-preservation` proved the boundary and implemented a bounded renderer-only fix on the TASK-023 large InsightForge report.

Category:
- Source structure preservation

Severity:
- High before TASK-031; resolved as a foundational renderer issue for Markdown-like upstream structure already present in statement text.

Evidence:
- `artifacts/tasks/TASK-026-operational-publication-trial.md`, publication 02 and 03 weaknesses.
- `artifacts/presentations/TASK-026-operational-publication-trial/cross_publication_comparison.md`, repeated issue 4.
- `artifacts/presentations/TASK-030-briefforge-v0.3-reader-experience-showcase/reader_evaluation.md`, source-structure flattening identified as the largest remaining professional gap.
- `artifacts/presentations/TASK-031-renderer-source-structure-preservation/source_structure_preservation_report.md`, renderer-only implementation evidence.
- `tests/test_source_structure_preservation.py`, RED/GREEN tests for headings, nested lists, tables-where-present behavior, caveat/methodology/recommendation blocks, semantic ordering, conformance, and runtime immutability.

Implemented renderer improvement:
- Preserve existing upstream headings, short source section labels, ordered lists, unordered lists, nested unordered lists, blockquotes, Markdown tables where present, and conservative inline code spans as readable report structure.
- Use renderer-local `data-source-structure`, `data-source-list`, `data-source-tables`, and `data-source-block` attributes only in final HTML.

Implementation status:
- Implemented for existing renderer-visible Markdown-like source structure.

Boundary assessment:
- Proven renderer-only for TASK-023/TASK-031. No constitution, runtime, Presentation Package, validation, promotion, Presentation Grammar, or Presentation Models were modified.

Threshold status:
- Meets recurrence threshold and now has implementation evidence. Foundational source-structure work is complete enough that visualization/exhibit-oriented renderer work becomes the next highest-value milestone, constrained to real source-supported exhibits.

---

### RB-005 — Generic display headings weaken reader orientation

Identifier: RB-005

First observed publication:
- `TASK-026-operational-publication-trial/pub-02-macroforge-canonical-gdp-snapshot`

Subsequent occurrences:
- `TASK-026-operational-publication-trial/pub-03-insightforge-knowledge-accumulation-report`
- `TASK-030-briefforge-v0.3-reader-experience-showcase` repeated the issue: generic labels such as `Hypothesis Review` and `Analytical Section` are semantically safe but weaker than source-specific publication headings.

Category:
- Navigation / hierarchy / section labeling

Severity:
- Medium

Evidence:
- `artifacts/tasks/TASK-026-operational-publication-trial.md`, recurring renderer deficiencies.
- `artifacts/presentations/TASK-026-operational-publication-trial/cross_publication_comparison.md`, repeated issue 5.
- `artifacts/reports/R-20260703-communication-intent-renderer-experiment.md`, reader-task labeling improvement in experimental renderer.

Proposed renderer improvement:
- Prefer reader-meaningful section labels derived from existing semantic/presentation evidence over generic encounter-mode labels, without adding new semantic authority.

Implementation status:
- Candidate

Boundary assessment:
- Potentially renderer-only if labels derive from existing package fields or source evidence. Must not modify Presentation Grammar unless future evidence directly contradicts it.

Threshold status:
- Meets recurrence threshold. Not approved for implementation by this task.

---

### RB-006 — Obligations are visible but too mechanical for readers

Identifier: RB-006

First observed publication:
- `TASK-026-operational-publication-trial/pub-01-insightforge-eurostat-finding`

Subsequent occurrences:
- `TASK-026-operational-publication-trial/pub-02-macroforge-canonical-gdp-snapshot`
- `TASK-026-operational-publication-trial/pub-03-insightforge-knowledge-accumulation-report`

Category:
- Obligation disclosure / reader trust

Severity:
- Medium

Evidence:
- `artifacts/tasks/TASK-026-operational-publication-trial.md`, recurring renderer deficiencies.
- `artifacts/presentations/TASK-026-operational-publication-trial/cross_publication_comparison.md`, repeated issue 6.

Proposed renderer improvement:
- Present obligations as reader-facing disclosure or methodology blocks while retaining exact obligation IDs and conformance traceability.

Implementation status:
- Candidate

Boundary assessment:
- Renderer-only if display changes preserve obligation content and identifiers. No validation or promotion changes justified.

Threshold status:
- Meets recurrence threshold. Not approved for implementation by this task.

---

### RB-007 — Table-heavy reports are hard to scan

Identifier: RB-007

First observed publication:
- `TASK-026-operational-publication-trial/pub-02-macroforge-canonical-gdp-snapshot`

Subsequent occurrences:
- TASK-032 static exhibit proof confirmed the same GDP publication benefits from renderer-side key-number, small statistical table, and comparison table exhibits.

Category:
- Quantitative/table display / static evidence exhibits

Severity:
- High for table-heavy evidence publications; conditional for narrative-only reports.

Evidence:
- `artifacts/tasks/TASK-026-operational-publication-trial.md`, Publication 02 weaknesses.
- `artifacts/presentations/TASK-026-operational-publication-trial/cross_publication_comparison.md`, one-off observations.
- `artifacts/presentations/TASK-032-static-exhibit-renderer-proof/static_exhibit_renderer_proof.md`.
- `tests/test_static_exhibit_renderer.py`.

Proposed renderer improvement:
- Use bounded renderer-side static Exhibits for existing source-supported key-value and table evidence. Exhibits are display decisions, not runtime objects or chart specifications.

Implementation status:
- Partially Implemented

Boundary assessment:
- Renderer-only implementation validated in TASK-032. No runtime exhibit object, Presentation Package field, Presentation Grammar change, chart library, JavaScript, browser application, dashboard, template, CSS framework, map, or visualization engine was introduced.

Threshold status:
- Approved and implemented as a bounded proof by TASK-032. Keep scope conservative until more operational publications repeat the need.

---

### RB-008 — Long reports may need stronger navigation affordances

Identifier: RB-008

First observed publication:
- `TASK-026-operational-publication-trial/pub-03-insightforge-knowledge-accumulation-report`

Subsequent occurrences:
- TASK-023 large-report stress validation exposed long-document pressure, but it was a stress validation rather than operational multi-report recurrence.
- TASK-030 reader-experience showcase showed that static long-document regions are useful, but professional-comparison evidence still favors stronger static outline/pacing; interactive navigation remains out of scope.

Category:
- Long-document navigation

Severity:
- Medium

Evidence:
- `artifacts/tasks/TASK-026-operational-publication-trial.md`, Publication 03 weaknesses.
- `artifacts/presentations/TASK-026-operational-publication-trial/cross_publication_comparison.md`, one-off observations.
- `artifacts/tasks/TASK-023-large-report-stress-validation.md` and TASK-024 long-document strategy provide prior stress evidence.

Proposed renderer improvement:
- Strengthen static long-document outline if more operational long reports repeat the problem. Interactive search/collapse/sticky navigation remains out of scope unless separately justified.

Implementation status:
- Observation

Boundary assessment:
- Static outline may be renderer-only; interactive navigation would violate current no-JavaScript/browser-app boundary.

Threshold status:
- Below operational recurrence threshold. Do not implement.

---

### RB-009 — Time-series evidence lacks trend shape

Identifier: RB-009

First observed publication:
- `TASK-033-static-svg-time-series-exhibit-proof`

Subsequent occurrences:
- None yet.

Category:
- Static evidence visualization / time-series exhibit

Severity:
- High when a report contains a clean single-series temporal table; not applicable to narrative-only or mixed-series reports.

Evidence:
- `artifacts/presentations/TASK-033-static-svg-time-series-exhibit-proof/static_svg_time_series_renderer_proof.md`.
- `artifacts/presentations/TASK-033-static-svg-time-series-exhibit-proof/reader_evaluation.md`.
- `tests/test_static_svg_time_series_exhibit.py`.

Proposed renderer improvement:
- Use one bounded renderer-side static SVG line exhibit only when existing source evidence already provides a single-series table with Period, numeric Value, at least three periods, and stable non-temporal dimensions.

Implementation status:
- Experimental

Boundary assessment:
- Renderer-only proof validated in TASK-033. No runtime visualization object, Presentation Package field, Presentation Grammar change, validation/promotion change, renderer registry, JavaScript, chart library, dashboard, browser app, portal, map, or visualization engine was introduced.

Threshold status:
- Keep Experimental. One real dataset demonstrated reader value, but recurrence is insufficient for broad adoption.
