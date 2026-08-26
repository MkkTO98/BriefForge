# Report: BriefForge Constitutional Architecture Falsification Review

Date: 2026-07-01
Type: architecture-review
Status: Final
Owner: BriefForge
Reviewed artifact: `artifacts/reports/R-20260701-constitutional-architecture.md`

## Question or scope

This report formally reviews the completed BriefForge constitutional architecture as a hypothesis to be falsified, not as a design to defend.

The review asks:

> Is the proposed BriefForge constitution the simplest architecture capable of satisfying BriefForge's intended EIP role while minimizing responsibility, maintenance, coupling, and premature abstraction?

This review does not authorize implementation, production code, renderer work, browser work, visualization work, template work, API work, or implementation task creation.

## Evidence consulted

BriefForge local artifacts:

- `CONSTITUTION.md`
- `state/architecture.md`
- `context/latest_handoff.md`
- `artifacts/reports/R-20260701-constitutional-architecture.md`

EIP and sibling-project boundary artifacts:

- `/home/mkkto/srv/EIP/governance/CAPABILITY_OWNERSHIP.md`
- `/home/mkkto/srv/EIP/projects/MacroForge/CONSTITUTION.md`
- `/home/mkkto/srv/EIP/projects/InsightForge/docs/INSIGHTFORGE_DOCTRINE.md`

MetaHarvest evidence reviewed again:

- `/home/mkkto/srv/EIP/projects/MetaHarvest/reports/R-20260701-gen2-visualization_architecture-coverage-report.md`
- `/home/mkkto/srv/EIP/projects/MetaHarvest/reports/R-20260701-gen2-interactive_analytics-coverage-report.md`
- selected component cards for Vega-Lite, Observable Plot, Apache ECharts, Grafana, Perspective, MapLibre GL JS, Leaflet, Meilisearch, and Neo4j.

## Executive verdict

The constitutional architecture mostly survives falsification at the boundary level, but not at the internal-abstraction level.

The strongest part of the constitution is the negative boundary:

- BriefForge should not own data ingestion.
- BriefForge should not own canonical economic data.
- BriefForge should not own analytical conclusions.
- BriefForge should not own MetaHarvest-style architectural evidence.
- BriefForge should not own ProjectForge scaffolding doctrine.
- BriefForge should not own future portal navigation, search, routing, sessions, or ecosystem entry points.
- BriefForge should not begin as a renderer, browser app, dashboard platform, PDF/report generator, template engine, or visualization system.

The weakest part is the tendency to name too many internal concepts before any presentation archetype has been pressure-tested. The current report correctly marks many concepts as conceptual, but the vocabulary itself risks hardening into architecture:

- primitives;
- components;
- blocks;
- sections;
- templates;
- archetypes;
- render plans;
- exports;
- lifecycle metadata;
- portal metadata;
- validation reports.

The review conclusion is:

> Keep BriefForge's constitutional boundary, but simplify its internal constitutional core to three irreducible responsibilities: presentation contract, composition semantics, and presentation validation obligations. Treat primitives, components, templates, archetypes, render plans, exports, and lifecycle metadata as evidence-seeking vocabulary, not constitutional subsystems.

## Falsification standard used

A proposed responsibility or subsystem is retained only if deleting it would prevent BriefForge from fulfilling its mission as a presentation engine independent of upstream data/analysis and downstream portal/rendering systems.

For each subsystem the review asks:

```text
Can this be deleted while preserving the mission?
```

If yes, it is recommended for deletion, demotion, or deferral.

If no, the report explains why it is irreducible.

## 1. Constitutional strengths

### Strength 1: Responsibility boundaries are mostly correct

The report's central boundary is evidence-supported:

```text
MacroForge -> trusted canonical economic observations
InsightForge -> justified analytical conclusions
MetaHarvest -> reusable non-domain architecture evidence
ProjectForge -> reusable scaffold/governance methodology
Future portal/navigation -> discovery, routing, navigation, sessions, entry points
BriefForge -> presentation composition
```

This matches the EIP capability ownership doctrine: observing, storing, evaluating, routing, prioritizing, publishing, and presenting are separate responsibilities. It also matches InsightForge's explicit doctrine that InsightForge does not own dashboards, report formatting, PDF generation, presentation, or briefing.

Verdict: Required to retain.

### Strength 2: Presentation-package-first is the right anti-coupling posture

The report's preference for a structured presentation package over browser-first or document-first architecture is the simplest currently defensible posture. It avoids premature commitment to either:

- a browser application; or
- a document/PDF generator.

It also preserves compatibility with a future portal without making BriefForge the portal.

Verdict: Required to retain, but the phrase should be narrowed. See Recommendation R1.

### Strength 3: HTML is correctly treated as likely rendering target, not semantic authority

The report correctly rejects premature HTML canonicality. HTML is likely the first useful rendered target, but it is not the same as the semantic presentation artifact.

MetaHarvest visualization evidence supports this distinction. Vega-Lite, Observable Plot, ECharts, MapLibre, Grafana, and Perspective repeatedly separate some form of specification/record/contract from rendering/runtime behavior.

Verdict: Required to retain.

### Strength 4: The report correctly rejects template theater

The current report correctly identifies templates as dangerous if they become content generators or hidden analysis mechanisms. This is important because a template that fills missing narrative can silently create unsupported conclusions.

Verdict: Required to retain.

### Strength 5: The report explicitly leaves rendering ownership unresolved

This is a strength. The architecture should not decide renderer ownership before a semantic package and one archetype have been tested.

Verdict: Required to retain.

## 2. Constitutional weaknesses

### Weakness 1: Too many internal layers are named before evidence exists

The current report names many candidate concepts. Even with caveats, naming them creates gravitational pull toward implementing a framework.

Potential over-named layers:

- presentation primitives;
- semantic presentation components;
- content/evidence/visual/interaction/navigation component families;
- blocks;
- sections;
- archetypes;
- templates;
- render plans;
- output target profiles;
- presentation lifecycle metadata;
- validation reports.

Problem:

MetaHarvest evidence supports explicit contracts and staged boundaries. It does not support creating a bespoke multi-layer presentation ontology before BriefForge has one pressure-tested presentation.

Falsification result:

- BriefForge needs a contract.
- BriefForge needs composition semantics.
- BriefForge needs validation obligations.
- BriefForge does not yet need a constitutional primitive/component/block/template hierarchy.

Classification: Required simplification.

### Weakness 2: "Presentation artifact model" is too broad

The report says BriefForge should own a presentation artifact model representing sections, blocks, cards, evidence references, caveats, visual slots, narrative ordering, interaction affordances, and output target requirements.

This is directionally right but too expansive as a constitutional responsibility. It risks preloading the artifact with every possible future need.

Better formulation:

> BriefForge owns the minimal presentation contract required to preserve narrative order, upstream references, caveat/provenance visibility obligations, and target-independent presentation intent.

Everything else should be admitted only when the first archetype proves it necessary.

Classification: Required refinement.

### Weakness 3: "Presentation primitives" risks becoming a custom ontology

The primitives list is useful as brainstorming, but constitutionally dangerous. It includes many candidates that may not be primitive:

- transition;
- thesis placeholder;
- glossary tooltip;
- filter/slice affordance;
- linked evidence highlight;
- render status;
- validation status;
- output target profile.

Some of these likely belong elsewhere:

- filter/slice semantics may belong to upstream data/analysis systems or renderer/portal interaction state;
- glossary/tooltips may belong to KnowledgeForge or renderer/portal presentation layer;
- render status may belong to a renderer or artifact registry, not the semantic package;
- validation status may belong to governance/validation reports, not a presentation primitive.

Classification: Required demotion from constitutional architecture to candidate vocabulary.

### Weakness 4: Portal metadata is correctly mentioned but may be over-owned

The report says BriefForge may expose metadata useful for navigation: title, summary, tags, source projects, date, freshness, artifact type, intended audience, confidence/caveat summary.

This is mostly correct, but the boundary should be stricter:

- BriefForge may include self-description metadata on presentation artifacts.
- A future portal owns indexing, ranking, search facets, navigation taxonomy, routing, reading queues, and personalization.

BriefForge should not design metadata around future portal needs beyond stable self-description.

Classification: Recommended refinement.

### Weakness 5: "Presentation quality criteria" may overlap with upstream truth quality

Presentation quality criteria include coherence, provenance visibility, caveat visibility, internal consistency, reusable structure, and user comprehension.

This is useful, but internal consistency is ambiguous. It could mean:

- presentation-internal consistency: no claim card references missing evidence; no hidden caveat; no contradictory labels; or
- analytical consistency: conclusions agree with data and methodology.

Only the first belongs to BriefForge.

Classification: Required clarification.

### Weakness 6: The report may understate the ownership of "briefing"

The EIP capability doctrine says future EII may own user-facing synthesis, attention allocation, briefing generation, and personalization if created. BriefForge is envisioned as a presentation engine, not as the user-facing intelligence product.

Therefore BriefForge should avoid owning "briefing generation" in the EII sense. It may own presentation composition for a brief artifact, but not deciding what Mikkel should read or which issue deserves attention.

Classification: Required clarification.

## 3. Responsibility boundary review

### MacroForge boundary

Current architecture says MacroForge owns data ingestion, canonicalization, economic semantics, source metadata, quality flags, and canonical observations.

Falsification attempt:

Could BriefForge own data shaping for charts/tables?

Answer: only presentation-local display shaping, and only after upstream meaning is fixed. Any transformation that changes economic meaning, units, frequency, geography, seasonal adjustment, source interpretation, or canonical mapping belongs to MacroForge.

Recommendation:

- Required: keep MacroForge boundary.
- Required: state explicitly that BriefForge may not compute economic aggregates, revisions, rates, transformations, or indicator interpretations merely to fit a visual.
- Optional: later define a "display excerpt" concept for immutable, bounded display snapshots, but only after reproducibility requirements are proven.

### InsightForge boundary

Current architecture says InsightForge owns justified conclusions.

Falsification attempt:

Could BriefForge summarize or rewrite findings into better presentation language?

Answer: dangerous. Rewriting can become new analysis. BriefForge may arrange, quote, excerpt, or preserve upstream-authored text and may flag missing presentation context. It should not synthesize a new conclusion unless the upstream analytical owner supplies or approves that wording.

Recommendation:

- Required: keep InsightForge boundary.
- Required: classify narrative synthesis as unresolved and high-risk.
- Recommended: first architecture investigation should test whether BriefForge can compose presentations using upstream-authored finding blocks only.

### MetaHarvest boundary

Current architecture says MetaHarvest is advisory evidence only.

Falsification attempt:

Could MetaHarvest provide presentation architecture directly?

Answer: no. MetaHarvest can provide reusable patterns but cannot adopt them for BriefForge, create BriefForge tasks, or decide local relevance.

Recommendation:

- Required: keep MetaHarvest advisory boundary.
- Recommended: future BriefForge architecture reports should cite MetaHarvest component cards by exact ID when evidence is materially used, not just domain families.

### ProjectForge boundary

Current architecture says ProjectForge owns scaffolding/governance methodology and BriefForge is autonomous after creation.

Falsification attempt:

Could BriefForge rely on ProjectForge validation/governance as part of its architecture?

Answer: no. ProjectForge can provide operating scaffolding, but BriefForge's presentation architecture must survive without ProjectForge.

Recommendation:

- Required: keep autonomy boundary.
- Recommended: avoid treating ProjectForge artifact categories as BriefForge product architecture.

### Future portal/navigation boundary

Current architecture says future portal owns discovery, routing, navigation, search, sessions, and entry points.

Falsification attempt:

Could BriefForge own presentation discovery because presentations need to be found?

Answer: no. BriefForge can emit artifact self-description. Discovery, ranking, search, routing, personalization, and navigation belong to a future portal/navigation system or no project yet.

Recommendation:

- Required: keep portal boundary.
- Required: replace "portal metadata" with "presentation self-description metadata" in future constitutional refinement.

### No project at all

Some named responsibilities should currently belong to no project:

- global ecosystem coordination;
- ecosystem-wide prioritization;
- user-personalized reading queues;
- presentation search/ranking;
- generic dashboard platform;
- generic component library;
- generic renderer framework;
- generic export pipeline;
- generic map/report system.

Recommendation:

- Required: do not assign these to BriefForge by default.

## 4. Internal architecture simplification audit

| Proposed subsystem/concept | Can it be deleted now? | Verdict | Classification | Justification |
|---|---:|---|---|---|
| Mission: presentation composition | No | Keep | Required | Without this there is no project identity. |
| Presentation package / contract | No | Keep, narrow | Required | The project needs a portable semantic record independent of renderers and portal. |
| Presentation composition semantics | No | Keep | Required | BriefForge's distinct value is ordering and structuring upstream material. |
| Input contracts | No | Keep at interface level | Required | It must know what upstream owners supply, without owning their data/analysis. |
| Output contracts | No | Keep at interface level | Required | Renderers/portal need a stable artifact to consume. |
| Presentation validation obligations | No | Keep, narrow | Required | Caveat/provenance suppression is a core presentation failure mode. |
| Presentation quality criteria | Partly | Keep only presentation-local criteria | Required | Must not become analytical correctness or domain truth validation. |
| Presentation primitives | Yes | Demote | Required | Candidate vocabulary, not constitutional subsystem. |
| Components | Yes | Demote | Required | No evidence yet that BriefForge needs component architecture rather than a simple semantic contract. |
| Blocks | Yes | Avoid as constitutional layer | Recommended | May emerge inside one archetype; not needed constitutionally. |
| Sections | Partly | Keep as ordinary presentation structure, not subsystem | Recommended | Necessary as plain structure, but not an architecture layer. |
| Templates | Yes | Defer | Required | Dangerous before validated archetype; treat as future contract candidate. |
| Archetypes | No, but limited | Keep as evidence probes | Recommended | Useful to test architecture, but not product taxonomy yet. |
| Render plans | Yes | Defer | Recommended | Renderer boundary unresolved; render plan may be renderer-owned. |
| HTML rendered artifact | Yes as constitutional fact; no as likely investigation | Keep as candidate | Required | HTML likely first target, not semantic authority. |
| Document/export artifact | Yes | Defer | Recommended | No evidence PDF/export is first-class. |
| Portal metadata | Partly | Rename/narrow | Required | Self-description belongs to BriefForge; indexing/navigation does not. |
| Lifecycle metadata | Partly | Keep minimal version/source/staleness metadata only | Recommended | Some reproducibility metadata is necessary; render state and registry status may belong elsewhere. |
| Artifact registry | Yes | Reject for now | Required | Discovery/registry can become portal infrastructure; no current need. |
| Local renderer ownership | Yes | Defer | Required | Premature scope expansion. |
| Browser UI | Yes | Reject now | Required | Explicit non-scope. |
| Dashboard platform | Yes | Reject now | Required | Belongs to future portal/analytics or no project. |
| Map view system | Yes | Reject now | Required | GIS rendering/layer/source concerns are not BriefForge core. |

## 5. MetaHarvest evidence review

### Where mature systems converge

Across the consulted mature systems, MetaHarvest evidence shows convergence around:

1. Explicit record/contract boundaries.
   - Vega-Lite: visual encoding specification.
   - ECharts: option component model.
   - MapLibre: style spec/layer contract.
   - Grafana: panel/dashboard composition model.
   - Perspective: table/view update contract.

2. Separation between specification and rendering/runtime.
   - Vega-Lite has a compiler/runtime boundary.
   - Perspective distinguishes client/server rendering responsibilities.
   - MapLibre distinguishes style/source/layer contract from render loop.

3. Stage boundaries enabling substitution.
   - MetaHarvest links these projects to `portable-record-contract`, `decoupled-staged-delivery-pipeline`, and `governed-substitution-boundary`.

4. Routing/discovery is not payload semantics.
   - Search/retrieval systems provide indexing/query/ranking contracts, but these are not the semantic payload being searched.

### Where mature systems diverge

Mature systems diverge on domain-specific internal models:

- Vega-Lite emphasizes declarative visual grammar and compilation.
- Observable Plot emphasizes marks/transforms/layered composition.
- ECharts emphasizes option trees and component/series models.
- Grafana emphasizes dashboard/panel composition with data-source plugin contracts.
- Perspective emphasizes table/view update contracts and client/server boundaries.
- MapLibre/Leaflet/OpenLayers emphasize map source/layer/view/camera/interaction boundaries.
- Search systems emphasize schema/index/facet/ranking/query boundaries.
- Graph systems emphasize graph record/query/traversal/inference boundaries.

Implication:

> MetaHarvest supports BriefForge having a portable presentation contract. It does not support copying any one mature system's internal hierarchy into BriefForge.

### Where BriefForge may be introducing unnecessary custom architecture

The constitutional report may be inventing a custom hierarchy too early:

```text
presentation package -> primitives -> components -> blocks -> sections -> templates -> archetypes -> render plans -> renderers/exports
```

Mature systems do not converge on this exact stack. They converge on explicit contracts and staged boundaries, not on a universal presentation ontology.

Recommendation:

- Required: define one minimal portable presentation contract before defining a library of primitives/components.
- Recommended: use one archetype to discover necessary fields and sections.
- Rejected: adopting a full component hierarchy from visualization/dashboard systems.

### Existing patterns that should replace proposed internal designs

Evidence-supported replacement pattern:

```text
Upstream owned package references
-> BriefForge minimal presentation contract
-> target-specific renderer/adapter later
-> future portal/navigation consumes self-description metadata only
```

This is simpler than:

```text
Upstream data/finding packages
-> primitives
-> components
-> blocks
-> sections
-> templates
-> archetypes
-> render plans
-> multi-target output system
-> registry/portal metadata system
```

Classification: Required simplification.

## 6. Future portal compatibility review

The current constitution is mostly portal-compatible because it refuses to own navigation. However, portal compatibility should be achieved through a narrow artifact boundary, not through early portal-oriented architecture.

### Browser reports

A browser report can emerge from a presentation package if the package preserves:

- ordered structure;
- stable artifact identity;
- title/summary/audience/purpose;
- upstream references;
- caveat/provenance obligations;
- optional target-independent interaction intent.

It does not require BriefForge to own a browser app.

Classification: Current architecture sufficient if simplified.

### Dashboards

Dashboards are high-risk. Grafana evidence shows dashboards are composition systems with data-source contracts, panels, transformation/alerting pipelines, and operational concerns. That is not BriefForge's initial mission.

A dashboard-brief hybrid may later be an archetype, but BriefForge should not become a dashboard platform.

Classification: Required rejection of dashboard-platform ownership.

### Interactive pages

Interactive pages can emerge if BriefForge eventually distinguishes semantic interaction intent from renderer/portal state. But no generic interaction model should be adopted before one archetype proves it necessary.

Classification: Recommended deferral.

### Map views

Map views require GIS-specific source/layer/style/camera/projection boundaries. MapLibre, OpenLayers, and Leaflet evidence shows this is a distinct architecture domain. BriefForge may reserve a map slot in a presentation, but GIS rendering and map data semantics should not be owned by BriefForge by default.

Classification: Required boundary clarification.

### Future navigation

Navigation should emerge from future portal ownership over artifact discovery, routing, search, sessions, and reading flows. BriefForge should expose only artifact self-description.

Classification: Required boundary clarification.

## 7. Browser-first versus document-first review

The report's three-way comparison is sound, but the recommended conclusion can be made simpler:

- Browser-first is too implementation-shaped.
- Document-first is too export-shaped.
- Presentation-contract-first is the only constitutionally safe posture.

Recommended wording:

> BriefForge's constitutional artifact is a presentation contract, not a browser artifact or document artifact. HTML is a likely first rendering target. Documents/PDFs are possible downstream exports. Neither should define the project identity.

Classification: Required refinement.

## 8. HTML canonicality review

HTML should not be canonical at the semantic level. The constitutional report already says this, and the review strengthens it.

Recommended lifecycle distinction:

1. Semantic canonical artifact: presentation contract/package.
2. Rendered artifact: HTML or other target output produced later by a renderer/adapter.
3. Portal artifact: portal-owned index/route/view state referencing the presentation or rendered output.

This avoids confusing semantic authority with rendered representation.

Classification: Required.

## 9. Data ownership and reproducibility review

The report correctly defers reference-only versus snapshot versus hybrid. However, the review identifies a likely irreducible need:

- BriefForge must preserve stable upstream references and source ownership.
- BriefForge probably needs enough immutable display evidence for reproducible review, but the minimum is not yet known.

Do not decide snapshot policy now.

Recommended next investigation should compare two minimal models:

A. Reference-only presentation contract.
B. Reference-plus-display-snapshot contract.

Reject a broad local data cache.

Classification:

- Required: no canonical data ownership.
- Recommended: explicitly investigate reference-plus-display-snapshot as a reproducibility pressure point.
- Rejected: local canonical data cache or presentation-owned data warehouse.

## 10. Rendering ownership review

The report correctly defers rendering ownership. The review adds a stronger warning:

A renderer is not just an output function. It tends to bring:

- layout rules;
- style system;
- interaction runtime;
- accessibility concerns;
- asset handling;
- export behavior;
- browser/document quirks;
- testing strategy.

Therefore renderer ownership should be separately justified after the semantic presentation contract and one archetype are validated.

Classification: Required deferral.

## 11. Template philosophy review

Current template doctrine is sound but still too generous. The safest constitutional rule is:

> No template system exists constitutionally. Only archetype pressure tests exist. A template becomes eligible only after a repeated archetype shows stable required/optional structure and evidence obligations.

Classification: Required.

## 12. Candidate archetype review

The proposed candidate archetypes are useful, but some are too speculative for near-term architecture:

High-value near-term probes:

1. Economic release brief.
2. Insight/finding memo.
3. Indicator deep dive.

Defer:

- comparative dashboard-brief;
- market/investment context brief;
- scenario explainer;
- map-based economic/geographic brief;
- country/region profile if it requires broad data/finding aggregation.

Reason:

The first probe should test BriefForge's core boundary with minimal ownership ambiguity. Economic release brief is likely best if it uses MacroForge outputs only. Insight/finding memo is best if testing InsightForge boundary. Indicator deep dive may be slightly broader because it mixes data, context, explanation, and caveats.

Classification: Recommended.

## 13. Missing abstractions

The review identifies two missing or under-specified abstractions that are more important than many named primitives.

### Missing abstraction 1: Upstream-owned claim/evidence reference

BriefForge needs a way to refer to upstream-owned material without owning it. This should be the central building block, not a large primitive library.

Minimal concept:

```text
upstream_reference:
  owner_project
  artifact_id_or_path
  artifact_type
  version_or_review_state
  referenced_part
  caveat_visibility_obligation
  provenance_visibility_obligation
```

This is not an implementation schema. It is a constitutional concept.

Classification: Required.

### Missing abstraction 2: Presentation obligation

BriefForge's unique responsibility is not merely arrangement. It must preserve obligations attached to upstream material:

- show caveat;
- show provenance;
- show confidence;
- show freshness/staleness;
- do not detach evidence from claim;
- do not hide scope limit;
- do not render unsupported assertion as finding.

This is more important than deciding whether something is a block, card, section, or component.

Classification: Required.

### Candidate abstraction: Presentation self-description

BriefForge likely needs minimal self-description metadata:

- title;
- purpose;
- audience;
- source projects;
- creation/update time;
- freshness/staleness state;
- artifact type;
- caveat summary.

This should not become portal search taxonomy.

Classification: Recommended.

## 14. Recommendation register

### R1. Narrow the constitutional core to three responsibilities

Classification: Required

Recommendation:

Define BriefForge's irreducible constitutional responsibilities as:

1. Presentation contract.
2. Composition semantics.
3. Presentation validation obligations.

Justification:

These three are necessary and sufficient for BriefForge to exist independently of data ingestion, analysis, rendering, and portal navigation. Other concepts can be discovered later.

### R2. Demote primitives/components/blocks/templates from constitutional subsystems

Classification: Required

Recommendation:

Treat these as candidate vocabulary for future archetype investigations, not as accepted internal architecture.

Justification:

No implementation or archetype evidence currently proves that BriefForge needs this hierarchy. MetaHarvest evidence supports explicit contracts, not this particular hierarchy.

### R3. Replace "portal metadata" with "presentation self-description metadata"

Classification: Required

Recommendation:

BriefForge may include stable self-description metadata on presentation artifacts. It must not own portal indexing, routing, ranking, personalization, sessions, or navigation taxonomy.

Justification:

EIP capability doctrine separates routing/discovery from payload semantics.

### R4. Clarify that BriefForge validation is presentation-local

Classification: Required

Recommendation:

Presentation validation may check missing provenance, missing caveats, unsupported local references, hidden uncertainty, detached evidence, broken upstream references, and target incompatibility. It must not validate economic truth or analytical correctness.

Justification:

Truth belongs upstream to MacroForge/InsightForge. BriefForge only preserves presentation integrity.

### R5. Make upstream-owned references and presentation obligations first-class constitutional concepts

Classification: Required

Recommendation:

Future architecture should center on upstream references and display obligations rather than on a broad primitive/component taxonomy.

Justification:

This directly protects EIP boundaries and addresses the core failure mode: presentation changing or obscuring upstream meaning.

### R6. Keep semantic package canonical; keep HTML as likely first rendered target only

Classification: Required

Recommendation:

Canonicality should attach to the semantic presentation contract. HTML can become the first rendered target after a separate architecture decision.

Justification:

Avoids semantic loss in markup and preserves future document/portal compatibility.

### R7. Defer renderer ownership decision

Classification: Required

Recommendation:

Do not decide whether BriefForge owns renderers until after the semantic contract and one archetype are specified.

Justification:

Renderer ownership brings browser/document/runtime complexity and may deserve separate ownership.

### R8. Defer all template systems

Classification: Required

Recommendation:

No concrete template system should be part of the constitution. Archetypes may be used as pressure tests. Templates become eligible only after repeated structure stabilizes.

Justification:

Prevents template theater and unsupported content generation.

### R9. Select exactly one first archetype for the next architecture investigation

Classification: Recommended

Recommendation:

Use `economic release brief` if the next goal is to test MacroForge data-output presentation, or `InsightForge finding memo` if the next goal is to test conclusion/caveat preservation. Do not investigate many archetypes at once.

Justification:

One archetype reduces abstraction pressure and reveals actual minimum fields.

### R10. Investigate reference-only versus reference-plus-display-snapshot explicitly

Classification: Recommended

Recommendation:

The next architecture report should compare the smallest reproducible presentation contract variants.

Justification:

Reproducibility is likely a real pressure point, but a full data cache would violate ownership boundaries.

### R11. Treat interaction as target-independent intent only until proven otherwise

Classification: Recommended

Recommendation:

Do not define generic interaction primitives. If interaction is needed, record only high-level intent such as "allow evidence expansion" or "allow source detail reveal" until renderer evidence exists.

Justification:

Interaction models are renderer-, portal-, and domain-specific. Premature interaction architecture creates coupling.

### R12. Defer dashboard, map, search, and graph architecture to owning systems

Classification: Required

Recommendation:

BriefForge may reference chart/map/search/graph presentation slots later, but should not own GIS source/layer/camera contracts, dashboard panels/data sources, search/facet/ranking systems, or graph traversal models.

Justification:

MetaHarvest evidence shows these are mature domains with separate architectural responsibilities.

### R13. Reject generic component library as an initial goal

Classification: Rejected

Rejected proposal:

Build or constitutionally define a reusable component library before one archetype is validated.

Justification:

Premature abstraction. Reuse should emerge from repeated archetype pressure, not elegance.

### R14. Reject BriefForge as dashboard platform

Classification: Rejected

Rejected proposal:

Make BriefForge own dashboard composition, panels, data-source plugin contracts, live updates, or user dashboard state.

Justification:

Grafana/Perspective evidence shows dashboard architecture is materially larger than presentation composition and would collapse portal/analytics/rendering boundaries.

### R15. Reject BriefForge as user-facing briefing/intelligence prioritization system

Classification: Rejected

Rejected proposal:

Make BriefForge decide what intelligence Mikkel should read, prioritize, or act on.

Justification:

Future EII or portal systems may own user-facing attention allocation if explicitly created. BriefForge is a presentation engine, not an intelligence coordinator.

## 15. Simplified constitutional model proposed by this review

This review does not modify the constitutional report directly, but it recommends that a future refinement use this smaller model:

```text
Upstream owner artifacts
  MacroForge: canonical observations/evidence packages
  InsightForge: justified findings/conclusions
  Knowledge/context owner if later approved: definitions/background

        |
        v

BriefForge semantic presentation contract
  - artifact identity and self-description
  - ordered presentation structure
  - upstream-owned references
  - presentation obligations: caveat/provenance/confidence/freshness visibility
  - target-independent presentation intent
  - validation obligations

        |
        v

Future renderer/adapter decision
  - HTML likely first rendered target
  - document/export optional later
  - browser/dashboard/map runtime not owned by default

        |
        v

Future portal/navigation system
  - discovery
  - routing
  - search
  - user sessions
  - personalization
  - navigation
```

Everything outside this path should remain deferred until evidence forces it.

## 16. Remaining open questions

1. What is the smallest semantic presentation contract that can preserve upstream meaning without becoming a renderer schema?
2. Can an economic release brief be represented using only upstream references, obligations, ordering, and self-description?
3. Can an InsightForge finding memo be represented without BriefForge rewriting or synthesizing conclusions?
4. What exact obligations must always travel with an upstream claim, finding, metric, caveat, and evidence reference?
5. Is reproducibility possible with references only, or is a bounded display snapshot required?
6. What does "presentation validation" mean without validating upstream truth?
7. When does a visual slot become a visualization specification, and which project owns that boundary?
8. What is the minimum interaction vocabulary, if any, that remains target-independent?
9. What metadata is genuinely self-description versus portal-owned indexing/search/navigation taxonomy?
10. Does the first archetype require renderer assumptions? If yes, presentation/rendering may be less separable than the current constitution assumes.

## 17. Recommended next architectural investigation

Do not implement.

Do not create implementation tasks.

Recommended next architecture-only investigation:

> Define the minimal semantic presentation contract for exactly one archetype, with explicit upstream references, presentation obligations, self-description metadata, and validation rules. Use the investigation to test whether primitives/components/templates are actually necessary.

Preferred archetype options:

1. Economic release brief — best for testing MacroForge data/evidence boundary.
2. InsightForge finding memo — best for testing analytical conclusion/caveat boundary.

The investigation should explicitly attempt to avoid:

- component hierarchy;
- template system;
- renderer assumptions;
- browser assumptions;
- dashboard assumptions;
- portal taxonomy;
- local data cache.

Stop condition:

If the archetype cannot be represented without selecting renderer behavior, record this as falsifying evidence against strict presentation/rendering separation. Do not solve the problem by silently adding renderer architecture.

## Final review conclusion

The BriefForge constitutional architecture is directionally correct and boundary-safe, but internally too vocabulary-rich for an architecture-first project with no archetype evidence.

Freeze the boundary, not the hierarchy.

The simplest surviving architecture is:

```text
BriefForge owns the minimal presentation contract, the semantics of composing upstream-owned material into ordered presentation artifacts, and the validation obligations that prevent presentation from obscuring provenance, caveats, confidence, freshness, or ownership.
```

Everything else should remain unowned, deferred, or treated as candidate vocabulary until evidence from one architectural archetype investigation proves it necessary.
