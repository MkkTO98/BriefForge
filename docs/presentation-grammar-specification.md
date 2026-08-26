# Presentation Grammar Specification

Date: 2026-07-02
Status: TASK-021 renderer-independent communication specification

## 1. Purpose

The BriefForge Presentation Grammar defines how validated semantic Presentation Packages should be communicated to human readers.

It is not a renderer, template system, browser architecture, HTML schema, CSS system, JavaScript interaction model, dashboard framework, portal, visualization grammar, charting system, map layer model, PDF generator, component library, or runtime extension.

The grammar is renderer-independent. A minimal HTML renderer, a future static document renderer, a terminal renderer, a slide renderer, or a future browser report renderer should all be able to implement the same communication principles while preserving the existing BriefForge architecture.

## 2. Evidence basis

This specification is derived from implemented BriefForge evidence only:

- Country Profile Presentation Model, TASK-017.
- Country Comparison Presentation Model, TASK-018.
- Investment Thesis Presentation Model, TASK-019.
- InsightForge -> BriefForge Integration Proof, TASK-020.

It also consults existing MetaHarvest evidence as pattern evidence, not adoption authority.

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
- prior BriefForge MetaHarvest synthesis in `artifacts/reports/R-20260702-implementation-architecture-extraction.md` and `artifacts/reports/R-20260701-constitutional-architecture-falsification-review.md`.

MetaHarvest search note:

The local MetaHarvest corpus contains analyzed evidence for visualization architecture, dashboard/interactive analytics, validation/documentation surfaces, metadata/lineage, and application record systems. It did not expose first-class analyzed local project cards for Our World in Data, OEC, or Evidence.dev under those names. Therefore this specification does not claim direct MetaHarvest support from those three systems. It uses only the mature systems actually represented in local MetaHarvest and records OWID/OEC/Evidence-style narrative/report systems as a future evidence gap.

## 3. Grammar boundary

Presentation Grammar sits after semantic package construction and before target-specific rendering decisions.

```text
Candidate/Ready Presentation Package semantics
-> Presentation Grammar interpretation
-> target-specific renderer implementation later
```

The grammar may say:

- communicate purpose before details;
- keep evidence near claims;
- reveal caveats before conclusions are overinterpreted;
- preserve source ownership;
- expose obligations where they constrain interpretation.

The grammar may not say:

- use a sidebar;
- use cards;
- use CSS classes;
- use tabs;
- use charts;
- use maps;
- generate JavaScript;
- create dashboards;
- implement templates;
- add runtime fields.

## 4. Common information hierarchy

All validated models share a common communication hierarchy:

1. Orientation.
   - What is this presentation about?
   - Why should the reader read it?
   - What question, subject, or comparison is being addressed?

2. Primary semantic claim or summary.
   - Country Profile: the profile's high-level characterization.
   - Country Comparison: the core comparison summary.
   - Investment Thesis: the thesis statement.
   - InsightForge integration: the upstream finding/conclusion.

3. Structured elaboration.
   - Country Profile: thematic profile dimensions such as economy and demographics.
   - Country Comparison: indicators, similarities, and differences.
   - Investment Thesis: supporting evidence, risks, counterarguments, and conclusion.
   - InsightForge integration: question, conclusion, confidence, caveats, reproducibility, and evidence boundary.

4. Evidence and traceability.
   - References should be visible enough that readers can tell what supports which material.
   - References should not be transformed into BriefForge-owned facts.

5. Caveats, uncertainty, and obligations.
   - Material constraints on interpretation must be communicated before the reader can mistake the package for stronger authority than it has.

6. Closing synthesis.
   - The reader should leave with the intended conclusion, comparison takeaway, or bounded thesis without losing track of uncertainty and evidence boundaries.

This hierarchy is conceptual, not visual.

## 5. Reader attention grammar

BriefForge renderers should communicate semantic material through four attention levels.

### 5.1 Primary

Primary material is necessary to understand the presentation's main purpose.

Examples:

- organizing purpose;
- main profile overview;
- comparison thesis;
- investment thesis statement;
- InsightForge finding conclusion.

Primary material should appear early and should not depend on the reader first traversing supporting evidence.

### 5.2 Secondary

Secondary material elaborates or qualifies the primary material.

Examples:

- economy and demographics in a country profile;
- selected indicators in a comparison;
- supporting evidence in a thesis;
- confidence justification in an InsightForge-derived presentation.

Secondary material should remain close enough to the primary material that readers understand why it matters.

### 5.3 Supporting

Supporting material enables audit and interpretation but is not the main narrative.

Examples:

- upstream references;
- reproducibility notes;
- detailed caveats;
- evidence boundary explanations;
- statement-level relationship context.

Supporting material should be discoverable without interrupting comprehension.

### 5.4 Discoverable on demand

Discoverable material is necessary for auditability or deeper review but should not dominate the first reading path.

Examples:

- full source paths;
- validation metadata;
- semantic fingerprints;
- complete reference lists;
- detailed obligation text when not directly attached to a claim.

Discoverable does not mean hidden. It means lower attention priority than the core communication path.

## 6. Narrative structure

Descriptive, comparative, and argumentative presentations share a common grammar:

```text
Orient -> State main semantic point -> Elaborate -> Qualify -> Trace -> Close
```

They diverge in the middle.

### 6.1 Descriptive grammar: Country Profile

A descriptive presentation should communicate:

1. subject and purpose;
2. profile overview;
3. stable thematic dimensions;
4. caveats and evidence boundaries;
5. references and obligations.

Descriptive grammar should avoid pretending that ordering implies analytical importance unless the package explicitly says so.

### 6.2 Comparative grammar: Country Comparison

A comparative presentation should communicate:

1. compared entities and comparison purpose;
2. comparison summary;
3. basis of comparison;
4. similarities;
5. differences;
6. caveats about comparability;
7. references and obligations.

Comparative grammar should keep comparison basis visible. A reader should not have to infer whether the comparison is based on GDP, population, direction of change, qualitative structure, or another basis.

### 6.3 Argumentative grammar: Investment Thesis

An argumentative presentation should communicate:

1. subject and thesis statement;
2. evidence supporting the thesis;
3. material risks;
4. counterarguments;
5. conclusion;
6. uncertainty, caveats, and non-advice obligations;
7. references.

Argumentative grammar must not collapse risks and counterarguments into footnotes. They are part of the argument, not optional legal boilerplate.

### 6.4 Upstream analytical finding grammar: InsightForge integration

An upstream finding presentation should communicate:

1. source project and artifact identity;
2. analytical question;
3. upstream conclusion;
4. evidence boundary;
5. confidence and caveats;
6. reproducibility method;
7. references and obligations.

This grammar preserves responsibility boundaries: the upstream project owns the conclusion; BriefForge owns how that conclusion is presented.

## 7. Reference presentation guidance

References should be communicated conceptually in four ways.

### 7.1 Evidence-linked references

When a statement depends on a source, the reader should be able to identify the relevant source near that statement.

Justification:

TASK-020 showed that source-dependent statements need obligations and references to preserve ownership. MetaHarvest lineage evidence from dbt, OpenMetadata, and provider-evidence-not-canonical-truth supports keeping evidence relationships inspectable.

### 7.2 Grouped reference inventory

A presentation should also provide a grouped reference inventory so readers can audit all upstream sources without scanning every statement.

Justification:

Great Expectations Data Docs, dbt manifest lineage, and dashboard/report systems converge on human-readable documentation of record-backed artifacts. The grouped inventory is a communication pattern, not a UI component.

### 7.3 Source ownership labels

References should communicate who owns the referenced meaning.

Examples:

- MacroForge-owned canonical data evidence.
- InsightForge-owned analytical finding.
- Manual authoring source.

Justification:

BriefForge's constitution requires upstream-owned references. TASK-020 specifically proved this boundary across InsightForge, MacroForge, and BriefForge.

### 7.4 Avoid reference inflation

Do not repeat the full reference text after every statement unless repetition is needed to prevent misinterpretation. Prefer proximity plus grouped inventory.

Justification:

The three Presentation Models showed that repeated references can overwhelm primary communication. Traceability must remain visible without turning the presentation into a citation dump.

## 8. Obligation presentation guidance

Obligations are reader-facing constraints on interpretation.

They should be communicated according to their force.

### 8.1 Global obligations

Global obligations apply to the whole package.

Examples:

- source attribution must be preserved;
- presentation is descriptive, not investment advice;
- upstream conclusion ownership must remain visible.

Global obligations should be visible in the presentation's framing and available in the grouped obligation inventory.

### 8.2 Contextual obligations

Contextual obligations apply to specific statements or sections.

Examples:

- a claim must retain a caveat;
- a comparison must not be interpreted as ranking;
- an evidence statement must preserve source limitations.

Contextual obligations should appear close to the constrained statement.

### 8.3 Conditional obligations

Conditional obligations matter only under certain reader interpretations.

Examples:

- if a thesis is used for decision support, show non-advice and uncertainty obligations;
- if a chart/map renderer later visualizes data, preserve source and caveat obligations.

Conditional obligations should be exposed when the relevant interpretation path is likely.

### 8.4 Obligation grouping

All obligations should be auditable as a group, but grouping alone is insufficient when the obligation materially changes how a statement should be read.

## 9. Uncertainty grammar

BriefForge should communicate uncertainty using existing concepts only:

- statements;
- encounter semantics;
- references;
- obligations;
- caveats authored upstream or in the Presentation Model.

It should not introduce probability models, confidence runtime objects, risk score fields, or uncertainty engines.

Uncertainty should be communicated through:

1. explicit caveat statements;
2. risk statements;
3. counterarguments;
4. confidence-justification statements when upstream artifacts provide them;
5. obligations that prevent overclaiming;
6. reference proximity showing source limitations.

Model-specific uncertainty:

- Country Profile: communicate data coverage, source freshness, and descriptive scope.
- Country Comparison: communicate comparability limits, denominator/unit differences, period differences, and non-ranking obligations.
- Investment Thesis: communicate risks, counterarguments, non-advice scope, and evidence limitations.
- InsightForge finding: communicate confidence, caveats, and reproducibility exactly as upstream-owned material.

## 10. Common communication rules

These rules are derived from implemented evidence and MetaHarvest convergence around explicit contracts, durable records, staged boundaries, and source/lineage visibility.

1. Purpose before detail.
   - A reader must know why the package exists before reading statements.

2. Summary before elaboration.
   - Present the main semantic point before thematic details, comparison dimensions, or evidence lists.

3. Evidence proximity.
   - Keep source ownership and evidence relationships near dependent material.

4. Caveats before overinterpretation.
   - Caveats must appear early enough to prevent false certainty.

5. Counterarguments are first-class in argumentative presentations.
   - Do not bury counterarguments below generic notes.

6. Obligations constrain reading, not rendering.
   - A renderer may choose target-specific expression, but it must preserve the interpretive force.

7. Preserve semantic authority separation.
   - Rendered appearance never becomes semantic authority.

8. Avoid repeated support unless it prevents misreading.
   - Group common references/obligations, but attach material constraints near relevant statements.

9. Preserve upstream ownership.
   - BriefForge communicates source relationships; it does not re-own data or analysis.

10. Do not infer absent structure.
   - If the package does not express ranking, priority, probability, or causality, the renderer must not imply it.

11. Respect encounter order without treating it as layout.
   - Encounter order is communication sequence, not a visual template.

12. Make audit paths available.
   - Readers should be able to find references, obligations, validation identity, and package identity when needed.

## 11. Model-specific communication guidance

### 11.1 Country Profile

Communication goal:

Help the reader understand a country through a small set of organized descriptive dimensions.

Recommended grammar:

1. subject and purpose;
2. concise overview;
3. main thematic dimensions;
4. caveats or source limitations;
5. references and obligations.

Avoid:

- implying causal analysis;
- implying ranking;
- overloading profile sections with thesis-style argument;
- hiding source freshness or scope limitations.

### 11.2 Country Comparison

Communication goal:

Help the reader understand similarities and differences between two countries under a defined comparison basis.

Recommended grammar:

1. compared countries and comparison purpose;
2. basis of comparison;
3. comparison overview;
4. selected indicators;
5. similarities;
6. differences;
7. comparability caveats;
8. references and obligations.

Avoid:

- implying a winner/loser ranking unless explicitly authored;
- mixing incomparable indicators without caveats;
- burying comparison basis after conclusions.

### 11.3 Investment Thesis

Communication goal:

Help the reader understand a bounded, evidence-linked argument while preserving uncertainty and non-advice scope.

Recommended grammar:

1. subject and thesis statement;
2. supporting evidence;
3. key risks;
4. counterarguments;
5. conclusion;
6. uncertainty and non-advice obligations;
7. references.

Avoid:

- turning thesis into recommendation/advice;
- suppressing counterarguments;
- presenting evidence without limitations;
- treating conclusion as stronger than supporting statements justify.

### 11.4 InsightForge-derived finding presentation

Communication goal:

Help the reader understand an upstream analytical finding without transferring analytical ownership to BriefForge.

Recommended grammar:

1. source artifact and owner;
2. analytical question;
3. upstream conclusion;
4. evidence boundary;
5. confidence/caveats;
6. reproducibility;
7. references and obligations.

Avoid:

- changing the upstream conclusion;
- treating BriefForge validation as analytical validation;
- hiding MacroForge/InsightForge ownership boundaries.

## 12. MetaHarvest comparison

| Evidence source | Communication pattern extracted | Adopted grammar principle | Rejected implementation implication |
|---|---|---|---|
| Grafana panel/dashboard composition | Durable composition records and panel/dashboard boundaries | Preserve presentation organization as inspectable record | Do not adopt dashboards, panels, plugins, or platform behavior |
| Superset dashboard/chart record model | User-facing analytical artifacts as durable records separate from query execution | Communicate presentation artifact identity and traceability | Do not adopt chart/dashboard/runtime analytics concepts |
| Metabase application model records | Questions/dashboards/collections as durable application records | Preserve question/purpose as reader orientation | Do not adopt BI product/application state |
| Observable Plot layered composition | Layered composition and mark/transform separation | Treat composition as ordered communication, separate from rendering | Do not adopt visualization marks/transforms into BriefForge grammar |
| Vega-Lite visual encoding specification | Specification/render separation | Keep grammar renderer-independent | Do not create visual encoding or compiler architecture |
| dbt manifest lineage | Static inspectability of semantic definitions and lineage | Make references and source ownership auditable | Do not adopt transformation framework or manifest compiler |
| OpenMetadata lineage resource | Lineage edges with details and source ownership | Preserve evidence-linked references conceptually | Do not adopt graph/search/catalog platform |
| Great Expectations Data Docs | Human-readable evidence surfaces from validation records | Renderers should expose validation/reference/obligation audit paths | Do not adopt data-quality framework |
| provider_evidence_not_canonical_truth | Provider/source evidence is not accepted truth | Preserve upstream-owned evidence and avoid BriefForge re-ownership | Do not make BriefForge a canonicalization or analysis authority |

Cross-system convergence:

- explicit record contracts;
- separation between semantic specification and rendering/runtime;
- inspectable evidence/lineage/ownership;
- durable human-readable documentation surfaces;
- caution against product/platform adoption without matching pressure.

Non-convergence:

- no universal UI hierarchy;
- no universal dashboard/report component stack;
- no universal visualization grammar for non-visual presentations;
- no evidence that BriefForge should create templates or components now.

## 13. Recommendations for future renderers

Future renderers should implement the grammar, not replace it.

Minimum justified renderer capabilities:

1. Purpose-first presentation.
   - Render organizing purpose and package identity clearly.

2. Ordered statement communication.
   - Preserve authored encounter sequence without implying unexpressed layout semantics.

3. Attention differentiation.
   - Distinguish primary, secondary, supporting, and discoverable information in the target medium.

4. Evidence proximity.
   - Communicate references near dependent statements when material.

5. Grouped audit surfaces.
   - Provide a complete reference inventory and obligation inventory.

6. Obligation proximity.
   - Show obligations near constrained claims when the obligation affects interpretation.

7. Uncertainty preservation.
   - Preserve caveats, risks, counterarguments, confidence notes, and non-advice constraints.

8. Source ownership communication.
   - Identify upstream owner/project when available in references.

9. Validation/audit metadata availability.
   - Make package identity, validation policy identity, and semantic fingerprint discoverable.

10. No semantic reinterpretation.
   - Renderers must not infer rankings, probabilities, causality, recommendations, or source truth not present in the package.

These are renderer capabilities, not runtime changes.

## 14. Final assessment

### 1. Does the current BriefForge architecture naturally support the proposed Presentation Grammar?

Yes.

The grammar is an interpretation guide over existing Presentation Package concepts: organizing purpose, ordered statements, encounter semantics, references, obligations, validation identity, and downstream renderer boundary. TASK-017 through TASK-020 provide enough evidence to define this grammar without adding runtime fields.

### 2. Does the grammar require constitutional changes?

No.

The grammar strengthens the existing constitutional distinction between presentation meaning and rendered appearance. It does not add responsibility for rendering, dashboards, portals, analysis, canonical data, or upstream conclusions.

### 3. Does it require runtime changes?

No.

The grammar can be implemented by future renderers using existing runtime objects. Any future pressure for additional package fields must come from renderer implementation evidence, not from this specification alone.

### 4. Does it require only renderer-level implementation?

Yes.

Future work belongs at renderer/adapter behavior level: how a renderer communicates existing purpose, statements, references, obligations, uncertainty, and audit metadata. That work must not grant rendered artifacts semantic authority.

### 5. Which future renderer capabilities become justified by this specification?

Justified as future renderer-level capabilities:

- purpose-first rendering;
- statement ordering preservation;
- primary/secondary/supporting/discoverable communication treatment;
- evidence-linked reference presentation;
- grouped reference inventory;
- contextual and grouped obligation presentation;
- uncertainty/caveat/risk/counterargument visibility;
- source ownership labels;
- validation/audit metadata discoverability.

Not justified:

- templates;
- CSS systems;
- JavaScript applications;
- browser apps;
- dashboards;
- portals;
- visualization engines;
- charts;
- maps;
- PDF generation;
- runtime schema changes;
- constitutional revision.
