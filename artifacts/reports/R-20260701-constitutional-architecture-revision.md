# Report: BriefForge Constitutional Architecture Revision

Date: 2026-07-01
Type: architectural-revision
Status: Final
Owner: BriefForge
Revision basis:

- `artifacts/reports/R-20260701-constitutional-architecture.md`
- `artifacts/reports/R-20260701-constitutional-architecture-falsification-review.md`

## 1. Scope and gate position

This report revises BriefForge's constitutional architecture in accordance with the falsification review.

This task performs only this gate stage:

```text
Architecture Proposal
-> Architectural Review
-> Architectural Revision   <-- this report
-> Constitution Freeze
-> Implementation
```

This report does not freeze the constitution. Material constitutional questions remain, especially the exact minimal presentation contract shape, validation obligations, first archetype pressure-test, reference-versus-snapshot reproducibility, and renderer boundary.

This report does not authorize implementation.

Explicitly not authorized:

- production code;
- renderer code;
- browser applications;
- dashboard systems;
- visualization code;
- map systems;
- search systems;
- portal/navigation functionality;
- template engines;
- APIs;
- generic UI component libraries;
- implementation tasks.

## 2. Executive revision

The falsification review upheld BriefForge's external responsibility boundary but rejected premature freezing of the internal hierarchy.

Revised constitutional conclusion:

> BriefForge is EIP's presentation contract system. It owns the minimal structured contract and validation layer required to compose upstream-owned information into target-independent presentation packages. It does not own upstream truth, analysis, ingestion, rendering, browsers, dashboards, maps, search, portal behavior, templates, or a generic UI component library.

The revised constitutional core is exactly:

1. Presentation Contract.
2. Composition Semantics.
3. Presentation Validation Obligations.

Everything else is either excluded, deferred, or candidate vocabulary.

## 3. Revised mission

BriefForge exists to define and validate structured presentation packages for the Economic Intelligence Platform.

Its mission is to let upstream-owned structured information be composed into coherent, inspectable, reusable, target-independent presentation packages without transferring ownership of data, analysis, rendering, portal navigation, or user-facing intelligence prioritization.

BriefForge's mission is not to produce a running presentation product now. Its current mission is constitutional: define the smallest safe architecture that can later support rendering by downstream or adjacent systems.

## 4. Revised owned responsibilities

BriefForge owns only the following constitutional responsibilities.

### 4.1 Presentation Contract

The Presentation Contract defines:

- what kinds of structured information BriefForge can receive;
- how upstream-owned artifacts are referenced;
- what self-description a presentation package must carry;
- what obligations must remain attached to referenced material;
- what target-independent presentation intent may be represented;
- what a downstream renderer, adapter, or portal may consume without becoming BriefForge's responsibility.

The contract must remain independent of:

- data ownership;
- analysis ownership;
- ingestion;
- canonicalization;
- rendering engines;
- browser applications;
- dashboards;
- maps;
- search;
- portal/navigation behavior;
- generic UI component libraries.

### 4.2 Composition Semantics

Composition Semantics define how presentation units may be:

- ordered;
- nested only when necessary;
- related;
- referenced;
- described;
- connected to upstream-owned material;
- constrained by required presentation obligations.

Composition Semantics must not freeze a premature hierarchy such as primitives/components/blocks/sections/templates/archetypes.

The correct constitutional question is not:

> Which elegant hierarchy should BriefForge use?

The correct constitutional question is:

> What is the minimum structure required to preserve upstream meaning, obligations, order, and target-independent presentation intent?

### 4.3 Presentation Validation Obligations

Presentation Validation Obligations define what BriefForge must validate before a presentation package can be accepted as structurally valid.

Validation is presentation-local. It may check that:

- source references are present and structurally valid;
- required self-description metadata exists;
- required fields are present;
- referenced units are internally consistent;
- evidence/provenance/caveat/confidence/freshness obligations are not suppressed;
- target-independent interaction intent, if present, is declared rather than implemented;
- presentation units do not detach claims from their required evidence/caveats;
- renderer-specific or portal-specific requirements are not incorrectly embedded as constitutional semantics.

Validation must not check or assert:

- whether economic data is true;
- whether canonicalization is correct;
- whether source-specific interpretation is valid;
- whether an analytical conclusion is justified;
- whether a visualization rendering is correct;
- whether portal routing/search/personalization is correct.

Those responsibilities belong elsewhere.

## 5. Revised excluded responsibilities

BriefForge does not own:

1. Data ingestion.
2. Canonicalization.
3. Canonical economic data storage.
4. Source-specific economic semantics.
5. Analytical conclusions.
6. Confidence judgments for analysis.
7. Domain or investment judgment.
8. Rendering engines.
9. Browser applications.
10. Dashboards.
11. Visualization engines.
12. Map systems or GIS rendering.
13. Search/indexing/ranking systems.
14. Portal navigation, routing, sessions, personalization, or reading queues.
15. APIs in the current architecture phase.
16. Template engines.
17. Generic UI component libraries.
18. ProjectForge scaffolding methodology.
19. MetaHarvest architecture harvesting or advisory knowledge storage.
20. Ecosystem coordination or prioritization.

If a future capability mixes presentation contract, rendering, portal navigation, data interpretation, and user prioritization, it must be split by ownership boundary before implementation.

## 6. Revised minimal constitutional core

The minimal core can be expressed as:

```text
Upstream-owned artifacts
  -> BriefForge Presentation Contract
  -> BriefForge Composition Semantics
  -> BriefForge Presentation Validation Obligations
  -> future renderer/adapter/portal owned elsewhere or separately justified
```

Irreducible concepts:

### Upstream-owned reference

A presentation package must be able to refer to upstream-owned material without owning it.

Conceptual fields may include:

- owner project;
- artifact identity;
- artifact type;
- version or review state;
- referenced part;
- required caveat visibility;
- required provenance visibility;
- required confidence/freshness visibility where supplied by the owner.

This is constitutional vocabulary, not an implementation schema.

### Presentation obligation

A presentation package must preserve obligations attached to upstream material.

Examples:

- show caveat;
- show provenance;
- show confidence if supplied;
- show freshness/staleness if supplied;
- preserve scope limit;
- do not present unsupported text as an upstream finding;
- do not detach a claim from its required evidence.

This obligation model is more constitutionally important than any primitive/component hierarchy.

### Presentation self-description metadata

A presentation package must describe itself sufficiently for future systems to interpret or discover it without implying BriefForge owns portal behavior.

Presentation self-description metadata may describe:

- what the presentation package is;
- what it contains;
- what upstream artifacts it depends on;
- what audience or use context it is suitable for;
- what freshness/staleness state is known;
- what caveat/confidence summary must remain visible;
- how future systems may interpret the package at a descriptive level.

It must not define portal search ranking, routing, personalization, navigation taxonomy, user sessions, or reading queues.

## 7. Revised relationship to EIP systems

### MacroForge

MacroForge owns trusted canonical economic observations and ingestion capability.

BriefForge may reference MacroForge-owned outputs through explicit upstream references. BriefForge must not acquire, canonicalize, reinterpret, aggregate, revise, transform, or validate economic data to fit a presentation.

Boundary rule:

> If a change affects what the data means, it belongs to MacroForge or another upstream data owner, not BriefForge.

### InsightForge

InsightForge owns justified conclusions derived from trusted evidence.

BriefForge may reference and present InsightForge findings, caveats, confidence, evidence links, and scope limits. BriefForge must not rewrite findings into new conclusions or synthesize unsupported analytical meaning.

Boundary rule:

> If a change affects what is concluded, it belongs to InsightForge or another analytical owner, not BriefForge.

### MetaHarvest

MetaHarvest owns reusable non-domain architecture evidence and advisory knowledge.

BriefForge may consult MetaHarvest when architectural uncertainty exists. MetaHarvest evidence may inform BriefForge's local architecture, but MetaHarvest does not decide adoption, create BriefForge tasks, or modify BriefForge.

The revision incorporates the falsification review's MetaHarvest conclusion:

- Mature systems support explicit contracts.
- Mature systems support staged delivery boundaries.
- Mature systems support specification/rendering separation.
- Mature systems support governed substitution boundaries.
- Mature systems do not justify freezing BriefForge's earlier custom hierarchy of primitives/components/blocks/sections/templates/archetypes/render plans.

### ProjectForge

ProjectForge supplied the generated project operating system and governance methodology.

BriefForge is autonomous after creation. ProjectForge does not own BriefForge's architecture, tasks, decisions, implementation, or future evolution.

Boundary rule:

> ProjectForge is scaffold provenance and reusable methodology reference, not BriefForge's project manager.

### Future portal/navigation systems

Future portal/navigation systems may later own discovery, routing, navigation, user sessions, search, ranking, personalization, reading queues, and ecosystem entry points.

BriefForge owns only presentation self-description metadata inside presentation packages. That metadata may help future systems interpret or discover packages, but it does not transfer portal responsibility to BriefForge.

Boundary rule:

> BriefForge describes presentation packages; a portal decides how users discover, navigate, search, rank, personalize, or interact with them.

## 8. Revised canonical representation decision

The canonical object is the structured semantic presentation package.

HTML is not constitutionally canonical.

HTML may remain the likely first rendered target because it is inspectable, browser-compatible, interactive, and portable. But HTML is a rendered representation, not the semantic authority.

Revised lifecycle distinction:

```text
Semantic canonical artifact: BriefForge presentation package
Rendered artifact: HTML or another future target produced by a renderer/adapter
Portal artifact: portal-owned route/index/view/session state referencing the package or rendered artifact
```

Consequences:

- BriefForge must not bury provenance, caveat, confidence, freshness, or ownership semantics inside HTML markup as the only source of truth.
- A renderer may later emit HTML, documents, or other targets, but that decision remains outside this constitutional revision.
- If future evidence proves rendering and presentation cannot remain separate, that must be recorded as a later architectural finding, not assumed now.

## 9. Revised terminology

Accepted constitutional terminology:

- Presentation Contract.
- Composition Semantics.
- Presentation Validation Obligations.
- Structured semantic presentation package.
- Upstream-owned reference.
- Presentation obligation.
- Presentation self-description metadata.
- Target-independent presentation intent.
- Renderer/adapter as future unresolved boundary.

Terminology narrowed:

- "Portal metadata" is replaced by "presentation self-description metadata."
- "Presentation package" means semantic package, not rendered HTML.
- "Validation" means presentation-local structural/obligation validation, not data/analysis truth validation.

## 10. Deferred vocabulary

The following terms are demoted from constitutional subsystems to candidate future vocabulary:

- primitives;
- components;
- blocks;
- sections;
- templates;
- archetypes;
- render plans;
- exports;
- broad lifecycle metadata;
- portal metadata.

These terms may appear in future investigations only as possible implementation or specification vocabulary. They must not be treated as frozen architecture unless later evidence proves they are necessary.

Deferred vocabulary may be promoted only when:

1. a concrete architecture investigation demonstrates that the concept is necessary;
2. the concept reduces confusion or maintenance rather than adding elegance;
3. the concept preserves ownership boundaries;
4. the concept does not smuggle in rendering, portal, dashboard, visualization, template, or UI-component ownership;
5. the concept is recorded in a later decision or constitutional revision.

## 11. Validation obligations

Before a future presentation package can be accepted, BriefForge must eventually be able to validate these categories. This is an architectural obligation, not an implemented validator.

### 11.1 Reference validity

- Every upstream-owned reference identifies an owner.
- Every referenced artifact or artifact part is structurally identified.
- The package distinguishes reference from ownership.

### 11.2 Required self-description

- The package describes what it is.
- The package describes what it contains.
- The package describes what it depends on.
- The package describes its intended audience/use context if supplied.

### 11.3 Obligation preservation

- Required caveats are not hidden.
- Provenance is not suppressed.
- Confidence and freshness indicators supplied by upstream owners remain visible obligations.
- Scope limits remain attached to referenced material.

### 11.4 Internal consistency

- Presentation units do not reference missing material.
- Ordering and relationships are structurally valid.
- A package does not declare unsupported target-independent intent.
- Claims, findings, evidence, caveats, and self-description do not contradict at the presentation-structure level.

### 11.5 Boundary compliance

- The package does not contain data-ingestion logic.
- The package does not contain analytical inference logic.
- The package does not contain renderer/browser/dashboard/map/search/portal implementation behavior.
- The package does not depend on a generic UI component library.

## 12. MetaHarvest alignment

The revised architecture aligns with MetaHarvest evidence by adopting the transferable pattern, not the source-project internals.

Adopted alignment:

- Portable contracts: BriefForge's semantic package is a portable record/contract.
- Specification/rendering separation: the semantic package is not HTML, a browser UI, or a renderer runtime.
- Staged delivery boundaries: upstream owners produce reviewed material; BriefForge packages presentation semantics; renderers/adapters/portals remain later stages.
- Governed substitution boundaries: future renderers or portals should be replaceable as long as they satisfy the presentation contract and obligations.

Rejected over-application:

- Do not copy Vega-Lite's visual grammar.
- Do not copy ECharts' option/component model.
- Do not copy Grafana's panel/dashboard architecture.
- Do not copy Perspective's client/server rendering model.
- Do not copy MapLibre/OpenLayers/Leaflet GIS source/layer/view architectures.
- Do not copy search or graph system architectures into BriefForge.

The mature-system lesson is boundary discipline, not a custom BriefForge ontology.

## 13. Remaining open questions

Material constitutional questions remain:

1. What is the smallest valid presentation contract for the first pressure-test?
2. Which single archetype should be used only as an architecture pressure-test: economic release brief or InsightForge finding memo?
3. Can the contract remain reference-only, or is a bounded display snapshot required for reproducibility?
4. What exact presentation obligations must always travel with evidence, findings, caveats, confidence, and freshness?
5. How much target-independent interaction intent is safe before it becomes renderer or portal state?
6. Where is the boundary between a visual slot, visualization specification, and visualization rendering?
7. When should renderer ownership be decided, and by what evidence?
8. What minimal self-description metadata is enough for future portal compatibility without owning portal behavior?
9. What evidence would justify promoting any deferred vocabulary into constitutional architecture?
10. What must be true before Constitution Freeze is justified?

## 14. Constitution freeze gate

This report does not freeze the constitution.

A future Constitution Freeze may be considered only after a later architecture-only investigation demonstrates that:

1. the minimal presentation contract is defined well enough to be reviewed;
2. the contract has been pressure-tested against exactly one first archetype;
3. ownership boundaries remain intact;
4. no renderer/browser/dashboard/portal assumptions are hidden inside the semantic package;
5. validation obligations are specific enough to guide later implementation;
6. remaining open questions are either resolved or intentionally deferred until implementation evidence;
7. implementation can begin without reopening the mission, ownership boundary, canonical representation, or minimal constitutional core.

Until then, the next allowed work is architecture-only investigation, not implementation.

## 15. Final revised constitutional position

BriefForge's constitutional architecture is revised as follows:

```text
BriefForge owns the structured semantic presentation package contract, the composition semantics for arranging upstream-owned material without changing its meaning, and presentation-local validation obligations that prevent presentation from obscuring provenance, caveats, confidence, freshness, ownership, or structural integrity.
```

BriefForge does not own the systems that create, analyze, render, navigate, search, personalize, or operationalize those packages.

The architecture is now intentionally smaller than the original proposal. That reduction is the point of this revision.
