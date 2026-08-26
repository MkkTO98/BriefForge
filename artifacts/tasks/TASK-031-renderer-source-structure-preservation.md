# TASK-031 — Renderer Source-Structure Preservation

Status: complete
Date: 2026-07-03
Scope: renderer-only
Evaluation dataset: TASK-023 large InsightForge report

## Objective

Determine whether BriefForge can preserve upstream document structure without modifying frozen architecture or runtime concepts.

## Constraints honored

No changes were made to:

- constitution;
- Presentation Package;
- runtime;
- validation;
- promotion;
- Presentation Grammar;
- Presentation Models.

Not implemented:

- browser application;
- templates;
- CSS framework;
- JavaScript;
- charts;
- maps;
- dashboards;
- portals;
- search;
- visualization engine.

## MetaHarvest Presentation Architecture consultation

Consulted Presentation Architecture artifacts:

- Communication Pattern Library;
- Visualization Decision Framework;
- BriefForge renderer evolution recommendations.

Finding: mature communication systems preserve hierarchy, methodology, caveat, evidence, and recommendation structure before introducing visualization. TASK-031 aligns because it preserves author-provided structure without interpretation.

## RED/GREEN evidence

RED tests were added in:

- `tests/test_source_structure_preservation.py`

Initial RED result:

- renderer lacked `data-source-structure="preserved-v0.1"`;
- headings such as `Restated hypothesis`, `Supporting findings`, `Missing evidence`, and `Why not accepted` remained embedded in paragraph text;
- nested source lists remained flattened;
- caveat/methodology/recommendation blocks were not structurally exposed;
- runtime/conformance immutability test already passed.

GREEN result:

- `python3 -m unittest tests.test_source_structure_preservation -v` passed 5 tests.
- `python3 -m unittest tests.test_v03_reader_experience_showcase tests.test_large_report_stress_validation -v` passed 9 regression tests.

## Implementation summary

Implemented bounded renderer-side source-structure preservation in:

- `src/briefforge/renderer_adapter.py`

Preserves structures already present in statement text:

- source headings / short section labels;
- unordered lists;
- nested unordered lists;
- ordered lists;
- blockquotes;
- Markdown tables where present;
- conservative inline code spans;
- renderer-local caveat/methodology/recommendation display roles.

TASK-023 contains no Markdown tables; renderer correctly reports source tables absent and does not create synthetic tables.

## Generated artifacts

Directory:

- `artifacts/presentations/TASK-031-renderer-source-structure-preservation/`

Files:

- `selected_upstream_artifact.md`
- `briefforge_v0_4_source_structure_preservation.html`
- `renderer_audit_metadata.json`
- `rendered_artifact_conformance.json`
- `source_structure_preservation_report.md`
- `before_after_renderer_comparison.md`
- `reader_evaluation.md`
- `remaining_renderer_deficiencies.md`
- `next_renderer_milestone_recommendation.md`

## Renderer Backlog update

RB-004 was updated from Candidate to Implemented for existing renderer-visible Markdown-like source structure.

## Architectural observation

RB-004 was a renderer fidelity problem, not a frozen-architecture gap. BriefForge can preserve author information architecture using final-renderer behavior only.

## Next milestone recommendation

Yes: BriefForge is now structurally faithful enough that visualization/exhibit-oriented renderer work becomes the next highest-value improvement.

Constraint: future visualization work should remain bounded to real source-supported exhibits and should not introduce dashboards, browser apps, JavaScript, portals, or runtime concepts.
