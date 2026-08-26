# TASK-032 — Static Exhibit Recommendation and Rendering Proof

Status: complete
Date: 2026-07-03
Scope: renderer-only static exhibit proof

## Objective

Determine whether renderer-side Exhibits provide a better abstraction than renderer-side charts for improving visual evidence presentation while preserving BriefForge's frozen architecture.

## Result

Renderer-side Exhibits are validated as the better current abstraction.

The implementation adds bounded static exhibit rendering for existing source-supported evidence only:

- key-number exhibits from existing key-value lines;
- small statistical table exhibits from existing Markdown tables;
- comparison table exhibits from existing territory/period/value tables.

This is not a generic chart system and not a runtime concept.

## RED / GREEN evidence

RED:

- `python3 -m unittest tests.test_static_exhibit_renderer -v`
- Failed before implementation because no renderer exhibit markers, no static exhibit region, and no exhibit inference policy existed.

GREEN:

- `python3 -m unittest tests.test_static_exhibit_renderer -v`
- 5 tests passed after renderer-only implementation.

## Evaluation datasets

Used:

- TASK-023 large InsightForge report as no-exhibit control.
- TASK-026 GDP operational publication as structured evidence exhibit case.

Not used:

- synthetic reports;
- new analytical content.

## Implementation boundary

Modified renderer behavior only:

- no Constitution changes;
- no runtime changes;
- no validation/promotion changes;
- no Presentation Package changes;
- no Presentation Grammar changes;
- no Presentation Model changes;
- no runtime exhibit objects;
- no chart libraries;
- no dashboards;
- no browser applications;
- no JavaScript;
- no templates;
- no CSS frameworks;
- no maps;
- no visualization engine.

## Measured proof output

TASK-026 GDP static exhibit output:

- static exhibits: 5
- key-number exhibits: 3
- small statistical table exhibits: 1
- comparison table exhibits: 1
- conformance: true
- JavaScript: absent
- event handlers: absent
- SVG/canvas: absent

TASK-023 control:

- static exhibits: 0
- marked `data-exhibit-region="none-detected"`
- conformance: true

## MetaHarvest consultation

Consulted the Presentation Architecture domain:

- Visualization Decision Framework: tables are preferred when exact values, row-level audit, and multi-entity comparison matter.
- Communication Pattern Library P-02: evidence should sit near the claim it supports.
- P-04: evidence remains traceable.
- P-07: comparison matrices support entity comparison across common dimensions.
- P-13: visual grouping helps focus attention without becoming a dashboard.

The exhibit choices align with harvested evidence.

## Recommendation

Adopt renderer-side Exhibit concept.

Meaning of adoption:

- renderer-side only;
- non-canonical;
- inferred only from existing evidence already present in the package;
- no runtime/package/grammar adoption;
- no generic chart system.

## Next renderer milestone

Static evidence-display refinement:

1. improve large table scannability;
2. compact source notes near exhibits;
3. consider static trend micro-exhibits only when real source data already contains enough time-series structure;
4. do not implement generic charts yet.
