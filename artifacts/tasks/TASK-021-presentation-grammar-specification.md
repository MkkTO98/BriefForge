# TASK-021: Presentation Grammar Specification (Renderer-Independent)

Date: 2026-07-02
Status: Complete

## Objective

Produce the first BriefForge Presentation Grammar Specification.

The grammar defines how semantic Presentation Packages should be communicated to human readers while remaining independent of HTML, PDF, browser rendering, templates, CSS, JavaScript, component libraries, visualization frameworks, dashboards, portals, charts, maps, or richer renderers.

## Scope implemented

Created:

- `docs/presentation-grammar-specification.md`
- this task closeout record
- continuity updates

No production code was written.
No tests were added.
No runtime objects were changed.
No renderer behavior was changed.
No constitution text was changed.

## Evidence used

Implemented BriefForge evidence:

- TASK-017 Country Profile Presentation Model.
- TASK-018 Country Comparison Presentation Model.
- TASK-019 Investment Thesis Presentation Model.
- TASK-020 InsightForge -> BriefForge Integration Proof.

MetaHarvest evidence consulted:

- `component_cards/grafana-panel-dashboard-composition-model.yaml`
- `component_cards/superset-dashboard-chart-record-model.yaml`
- `component_cards/metabase-application-model-records.yaml`
- `component_cards/observable-plot-layered-composition-model.yaml`
- `component_cards/vega-lite-visual-encoding-specification.yaml`
- `component_cards/dbt-manifest-lineage.yaml`
- `component_cards/openmetadata-lineage-resource.yaml`
- `synthesis/provider_evidence_not_canonical_truth.yaml`
- `projects/great-expectations.md`
- `reports/R-20260701-gen2-visualization_architecture-coverage-report.md`
- `reports/R-20260701-gen2-interactive_analytics-coverage-report.md`
- prior BriefForge MetaHarvest synthesis reports.

MetaHarvest note:

Local MetaHarvest does not currently expose first-class analyzed artifacts named Our World in Data, OEC, or Evidence.dev. The specification therefore records these as future evidence gaps and does not claim direct support from them. It uses the analyzed local evidence actually present in MetaHarvest.

## Specification summary

The Presentation Grammar is:

```text
semantic package concepts
-> renderer-independent communication grammar
-> future target-specific renderer expression
```

It defines:

- common information hierarchy;
- reader attention levels;
- narrative structure shared and divergent across implemented models;
- reference communication guidance;
- obligation communication guidance;
- uncertainty communication guidance;
- common communication rules;
- model-specific guidance;
- MetaHarvest comparison;
- recommendations for future renderers.

## Core grammar

All validated models share this communication shape:

```text
Orient -> State main semantic point -> Elaborate -> Qualify -> Trace -> Close
```

Shared hierarchy:

1. Orientation.
2. Primary semantic claim or summary.
3. Structured elaboration.
4. Evidence and traceability.
5. Caveats, uncertainty, and obligations.
6. Closing synthesis.

Attention levels:

- primary;
- secondary;
- supporting;
- discoverable on demand.

## Model-specific conclusions

### Country Profile

Natural communication shape:

1. subject and purpose;
2. concise overview;
3. thematic dimensions;
4. caveats/source limits;
5. references/obligations.

### Country Comparison

Natural communication shape:

1. compared countries and comparison purpose;
2. basis of comparison;
3. comparison overview;
4. indicators;
5. similarities;
6. differences;
7. comparability caveats;
8. references/obligations.

### Investment Thesis

Natural communication shape:

1. subject and thesis statement;
2. supporting evidence;
3. key risks;
4. counterarguments;
5. conclusion;
6. uncertainty and non-advice obligations;
7. references.

### InsightForge-derived finding

Natural communication shape:

1. source artifact and owner;
2. analytical question;
3. upstream conclusion;
4. evidence boundary;
5. confidence/caveats;
6. reproducibility;
7. references/obligations.

## References guidance

References should be communicated as:

- evidence-linked near dependent statements when material;
- grouped in a complete reference inventory;
- labeled by source ownership where possible;
- not repeated excessively when one grouped reference plus proximity is sufficient.

## Obligations guidance

Obligations should be communicated as:

- global obligations when they constrain the whole package;
- contextual obligations near constrained claims/statements;
- conditional obligations where interpretation paths create risk;
- grouped obligation inventory for auditability.

## Uncertainty guidance

Uncertainty should be communicated with existing concepts only:

- statements;
- encounter semantics;
- caveats;
- risks;
- counterarguments;
- confidence notes when upstream-authored;
- obligations;
- reference proximity.

No probability model, confidence runtime object, risk score, or uncertainty engine is justified.

## MetaHarvest comparison result

MetaHarvest supports:

- explicit record contracts;
- separation between specification and rendering/runtime;
- inspectable evidence, lineage, and ownership;
- durable human-readable documentation surfaces;
- cautious renderer substitution boundaries.

MetaHarvest does not support:

- adopting dashboard platforms;
- adopting visualization grammars as BriefForge core;
- adopting browser-report architecture now;
- adopting templates/components now;
- copying one mature system's internal hierarchy.

## Future renderer capabilities justified

The specification justifies future renderer-level capabilities only:

- purpose-first rendering;
- statement order preservation;
- attention differentiation;
- evidence-linked reference display;
- grouped reference inventory;
- contextual and grouped obligation display;
- uncertainty/caveat/risk/counterargument visibility;
- source ownership labels;
- validation/audit metadata discoverability;
- no semantic reinterpretation by renderers.

## Explicit non-goals preserved

Not implemented or authorized:

- runtime changes;
- constitution changes;
- renderer changes;
- templates;
- HTML changes;
- browser applications;
- CSS;
- JavaScript;
- dashboards;
- portals;
- visualization;
- charts;
- maps;
- PDF generation;
- component libraries;
- APIs;
- persistence;
- networking.

## Final assessment

1. Does the current BriefForge architecture naturally support the proposed Presentation Grammar?

Yes. The grammar is an interpretation guide over existing package concepts: organizing purpose, ordered statements, encounter semantics, references, obligations, validation identity, and renderer boundary.

2. Does the grammar require constitutional changes?

No. It reinforces the frozen separation between presentation meaning and rendered appearance.

3. Does it require runtime changes?

No. Existing runtime concepts are sufficient.

4. Does it require only renderer-level implementation?

Yes. Future implementation belongs in renderer/adapter behavior and must preserve semantic authority separation.

5. Which future renderer capabilities become justified?

Purpose-first output, attention differentiation, evidence/reference proximity, obligation visibility, uncertainty visibility, source ownership labeling, and audit metadata discoverability.

## Verification

Because this was specification-only, verification focused on no-implementation boundary and ProjectForge health:

- no source/runtime files intentionally modified;
- no tests intentionally added;
- no renderer files intentionally modified;
- context summaries regenerated;
- coherence and context-health checks run after closeout.
