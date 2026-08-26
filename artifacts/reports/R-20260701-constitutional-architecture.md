# Report: BriefForge Constitutional Architecture

Date: 2026-07-01
Type: synthesis
Status: Final
Owner: BriefForge

## Question or scope

This report establishes the initial constitutional architecture of BriefForge before implementation begins.

The central question is:

> What should BriefForge constitutionally own, not own, consume, produce, and defer as the EIP presentation engine?

This is architecture-first work. It does not authorize renderer implementation, browser interfaces, APIs, templates, visualization code, dashboards, document generation, runtime storage, or production deployment.

## Evidence consulted

ProjectForge / EIP governance:

- `/home/mkkto/srv/ProjectForge/CONSTITUTION.md`
- `/home/mkkto/srv/ProjectForge/state/project_state.md`
- `/home/mkkto/srv/ProjectForge/state/architecture.md`
- `/home/mkkto/srv/ProjectForge/context/latest_handoff.md`
- `/home/mkkto/srv/EIP/governance/CAPABILITY_OWNERSHIP.md`

Sibling project boundaries:

- `/home/mkkto/srv/EIP/projects/MacroForge/CONSTITUTION.md`
- `/home/mkkto/srv/EIP/projects/InsightForge/docs/INSIGHTFORGE_DOCTRINE.md`
- `/home/mkkto/srv/EIP/projects/InsightForge/CONSTITUTION.md`

MetaHarvest consultation evidence:

- `/home/mkkto/srv/EIP/projects/MetaHarvest/CONSTITUTION.md`
- `/home/mkkto/srv/EIP/projects/MetaHarvest/latest_handoff.md`
- `/home/mkkto/srv/EIP/projects/MetaHarvest/retrieval/problem_catalog.yaml`
- `/home/mkkto/srv/EIP/projects/MetaHarvest/retrieval/retrieval_index.yaml`
- `/home/mkkto/srv/EIP/projects/MetaHarvest/coverage/architectural_coverage_assessment.md`
- `/home/mkkto/srv/EIP/projects/MetaHarvest/reports/R-20260701-gen2-visualization_architecture-coverage-report.md`
- `/home/mkkto/srv/EIP/projects/MetaHarvest/reports/R-20260701-gen2-interactive_analytics-coverage-report.md`
- `/home/mkkto/srv/EIP/projects/MetaHarvest/reports/R-20260701-second-generation-knowledge-evolution.md`

Generated BriefForge setup artifacts:

- `/home/mkkto/srv/EIP/projects/BriefForge/CONSTITUTION.md`
- `/home/mkkto/srv/EIP/projects/BriefForge/state/project_state.md`
- setup decision artifacts under `/home/mkkto/srv/EIP/projects/BriefForge/artifacts/decisions/`

## Executive finding

BriefForge should be constitutionally defined as the EIP presentation composition project, not as a data, analysis, visualization, dashboard, portal, or document-production project.

The cleanest current boundary is:

```text
MacroForge owns trusted canonical economic observations.
InsightForge owns justified analytical conclusions derived from trusted evidence.
MetaHarvest owns reusable non-domain architecture/pattern evidence and advisory knowledge.
ProjectForge owns reusable project scaffolding and governance methodology.
Future portal/navigation systems own discovery, routing, navigation, user session surfaces, and ecosystem entry points.
BriefForge owns presentation composition: the structured transformation from upstream reviewed information packages into coherent presentation artifacts.
```

The highest-confidence constitutional rule is therefore:

> BriefForge owns presentation structure and presentation semantics, but not upstream truth, upstream analysis, downstream navigation, or low-level rendering technology until rendering ownership is separately justified.

## 1. Mission and purpose

### Recommended constitutional mission

BriefForge exists to transform structured, reviewed, provenance-bearing information packages into coherent, reusable, interactive presentation artifacts for the EIP.

Its purpose is not to discover facts, validate facts, create analytical conclusions, govern projects, or serve as the user-facing portal. Its purpose is to preserve and compose presentation intent: narrative flow, evidence placement, visual slots, interactive affordances, provenance visibility, caveats, reuse boundaries, and output-target independence.

### Why this mission is distinct

BriefForge is extractable because presentation composition has its own purpose, lifecycle, artifact model, and failure modes:

- A good presentation can be wrong if upstream evidence is wrong; BriefForge must not own upstream truth.
- A correct finding can be poorly presented; BriefForge can improve this without changing the finding.
- A portal can navigate to presentations; navigation does not define presentation semantics.
- A renderer can render a presentation; rendering code does not decide what belongs in the presentation.

### Initial phase mission

The current phase is not to build that engine. The current phase is to establish the constitutional architecture needed before any engine exists.

## 2. Responsibilities owned by BriefForge

BriefForge should eventually own these responsibilities, subject to later evidence and implementation decisions:

1. Presentation artifact model
   - Define what a presentation package is.
   - Represent sections, blocks, cards, evidence references, caveats, visual slots, narrative ordering, interaction affordances, and output target requirements.

2. Presentation composition semantics
   - Decide how reviewed inputs become a coherent presentation structure.
   - Preserve sequence, hierarchy, emphasis, comparison, drilldown, appendix, source visibility, and reuse intent.

3. Presentation-specific contracts
   - Specify the minimum structured input contract BriefForge needs from upstream projects.
   - Specify output contracts consumed by renderers, portals, document exporters, or future interfaces.

4. Presentation quality criteria
   - Coherence, provenance visibility, caveat visibility, internal consistency, reusable structure, and user comprehension.
   - These are presentation-quality properties, not truth-quality or analytical-quality properties.

5. Presentation primitives
   - Define conceptual primitives such as title, summary, claim block, finding block, evidence panel, metric card, comparison table, chart slot, map slot, timeline slot, caveat block, methodology note, appendix, callout, and navigation anchor.

6. Presentation archetypes
   - Define candidate report/presentation families such as economic release brief, country profile, indicator deep dive, comparative dashboard-brief, analytical finding memo, risk monitor, scenario explainer, and research appendix.

7. Presentation lifecycle metadata
   - Version, source package references, upstream review state, generated/rendered state, target profile, staleness, and supersession.

8. Output-target governance
   - Preserve which aspects of a presentation are target-independent and which are target-specific.
   - Do not prematurely hardwire the project to browser-only or document-only output.

## 3. Responsibilities explicitly excluded

BriefForge must not own:

1. Data ingestion
   - MacroForge owns acquisition of economic evidence and ingestion capability.

2. Canonical data storage or canonicalization
   - MacroForge owns canonical, deterministic, auditable observations.

3. Analytical conclusions
   - InsightForge owns transformation of trusted evidence into justified conclusions.

4. Domain/investment judgment
   - Domain/investment intelligence remains with domain projects today and possible future EII where explicitly approved.

5. Upstream trust assignment
   - BriefForge may display trust/caveat metadata supplied by owners; it must not assign truth by presentation.

6. Meta-architecture harvesting
   - MetaHarvest owns reusable non-domain architectural evidence and advisory patterns.

7. Project scaffolding/governance methodology
   - ProjectForge owns project creation methodology and reusable framework doctrine.

8. Ecosystem navigation and routing
   - Future portal/navigation systems should own discovery, browsing, routing, user session context, permissioned navigation, and cross-project entry points.

9. Visualization computation by default
   - BriefForge may own visual slots and presentation-level visual intent, but not necessarily chart engines, geospatial engines, query engines, or analytical transformations.

10. Renderer implementation by default
   - Rendering may become a separate layer, submodule, dependency, or sibling concern. BriefForge must not assume it owns low-level rendering until evidence justifies that boundary.

11. Template factory by default
   - Templates are dangerous if they become unreviewed presentation logic. BriefForge may define template philosophy and conceptual archetypes, but concrete template systems require later evidence.

12. APIs, browser interface, dashboard app, PDF generator, or public UI in this phase.

## 4. Relationship with other systems

### MacroForge

MacroForge mission evidence: it transforms heterogeneous public economic evidence into deterministic, canonical, auditable observations suitable for long-term analytical use.

Relationship:

- MacroForge is an upstream data/evidence owner.
- BriefForge may consume MacroForge-owned data products only through reviewed, provenance-bearing contracts.
- BriefForge must not query raw data opportunistically and infer meaning.
- BriefForge must not alter canonical mappings, quality checks, source-specific metadata, units, frequencies, or economic semantics.

Possible future contract:

```text
MacroForge canonical observation package
-> indicator metadata, series values, provenance, quality flags, caveats, review status, source links
-> BriefForge presentation package references these as evidence/metric blocks
```

Boundary rule:

> If a change affects what the data means, it belongs upstream of BriefForge.

### InsightForge

InsightForge doctrine states: InsightForge exists to transform trusted evidence into justified conclusions. It explicitly does not own dashboards, report formatting, PDF generation, presentation, briefing, or external architecture harvesting.

Relationship:

- InsightForge is an upstream analytical-conclusion owner.
- BriefForge may present InsightForge findings, conclusions, caveats, confidence, and evidence references.
- BriefForge must not create or modify conclusions to fit a presentation.
- BriefForge may flag presentation-level incoherence or missing context back to InsightForge, but such feedback is advisory.

Possible future contract:

```text
InsightForge finding package
-> claim/finding, confidence, caveats, evidence links, reproducibility method, scope limits
-> BriefForge presentation package composes finding into narrative/brief structure
```

Boundary rule:

> If a change affects what is concluded, it belongs to InsightForge, not BriefForge.

### MetaHarvest

MetaHarvest is an advisory non-domain architectural knowledge repository. It may recommend patterns but may not decide adoption, create tasks in target projects, or modify projects.

Relationship:

- BriefForge should consult MetaHarvest at architectural decision points, especially presentation, visualization, dashboard, component, interactive analytics, browser/report, and rendering-boundary questions.
- BriefForge owns local relevance evaluation and adoption decisions.
- MetaHarvest evidence should inform but not determine BriefForge architecture.

Current consultation status:

- Consultation is triggered for this phase because ProjectForge and MetaHarvest policy require consultation during architecture definition when uncertainty and relevant pattern evidence exist.
- MetaHarvest Gen2 evidence includes visualization architecture, GIS, search/retrieval, knowledge graphs, and interactive analytics.
- Relevant analyzed sources include Vega-Lite, Apache ECharts, Observable Plot, Apache Arrow, Perspective, Grafana, MapLibre GL JS, OpenLayers, Leaflet, Meilisearch, Typesense, OpenSearch, Neo4j, Apache Jena, and Memgraph.
- This report uses that evidence only at architectural-pattern level. It emits no adoption recommendation.

### ProjectForge

ProjectForge created the BriefForge scaffold and governance operating system. After creation, BriefForge is autonomous.

Relationship:

- ProjectForge owns reusable scaffold methodology.
- BriefForge owns its local identity, architecture, tasks, decisions, reports, and future implementation.
- ProjectForge future improvements do not automatically mutate BriefForge.

Boundary rule:

> ProjectForge is historical scaffold source and future framework reference, not BriefForge's project manager.

### Future portal/navigation systems

Future portal/navigation systems are not yet approved implementation targets, but the boundary must be preserved now.

Likely portal responsibilities:

- User entry point.
- Navigation between projects, presentations, data pages, and findings.
- Search/discovery/routing.
- User session and personalization surface.
- Possibly permissioned access and reading queues.

BriefForge responsibilities relative to portal:

- Produce presentation artifacts that a portal can list, embed, route to, or render through adapters.
- Expose metadata useful for navigation: title, summary, tags, source projects, date, freshness, artifact type, intended audience, confidence/caveat summary.
- Avoid owning portal navigation, user accounts, reading queues, global search, or ecosystem-level prioritization.

Boundary rule:

> BriefForge produces presentation objects; a portal decides how users discover and navigate them.

## 5. Inputs and outputs

### Inputs

Candidate future inputs, not yet implementation contracts:

1. Evidence packages
   - Source: MacroForge or other domain data projects.
   - Contents: values, metadata, provenance, quality flags, caveats, review state.

2. Finding/conclusion packages
   - Source: InsightForge or future analytical projects.
   - Contents: claim, justification, caveats, confidence, evidence references, scope limits.

3. Reusable knowledge/context packages
   - Source: KnowledgeForge or future knowledge substrate if/when accepted.
   - Contents: definitions, concepts, background, glossary, relationship context.

4. Visualization intent or visual-ready data packages
   - Source: upstream analytical/visual systems or BriefForge composition layer.
   - Contents: desired visual role, data reference, encoding intent, interaction needs.

5. Presentation request/context
   - Source: user, future portal, EII, or project-local task.
   - Contents: intended audience, purpose, output target, level of detail, archetype, constraints.

### Outputs

Candidate future outputs:

1. Presentation package
   - Canonical structured representation of the presentation.
   - Target-independent as far as possible.

2. Render plan
   - Optional intermediate describing output target requirements.
   - Could be owned by BriefForge or renderer layer; unresolved.

3. HTML artifact or HTML-ready representation
   - Candidate canonical rendering target; not implemented now.

4. Document/export artifact
   - Possible downstream output if document-first or export layer is later adopted.

5. Portal metadata
   - Title, summary, tags, source projects, freshness, type, audience, caveats.

6. Presentation validation report
   - Checks for missing provenance, unsupported claims, broken references, caveat suppression, and target incompatibilities.

## 6. Data ownership

BriefForge should not own source data.

Recommended data doctrine:

- Upstream projects own data, evidence, findings, and domain semantics.
- BriefForge may own references to upstream artifacts, not copies as canonical truth.
- BriefForge may cache derived presentation artifacts later, but caches are not authority.
- BriefForge must preserve lineage to upstream owners.
- Presentation-level transformation must not erase provenance, caveats, confidence, units, review state, or scope limits.

Competing alternatives:

A. Reference-only model
   - BriefForge stores only references and presentation structure.
   - Pros: clean ownership, low duplication, low staleness risk.
   - Cons: rendering may depend on upstream availability/versioning.

B. Snapshot package model
   - BriefForge stores a bounded immutable input snapshot inside presentation artifacts.
   - Pros: reproducible presentations, easier archival/export.
   - Cons: duplication, staleness, ownership ambiguity, possible data-volume creep.

C. Hybrid model
   - BriefForge stores references plus selected immutable display snapshots with explicit source ownership and checksum/version metadata.
   - Pros: likely best long-term balance.
   - Cons: requires careful constitutional rules.

Initial recommendation: defer selection. Use reference-first doctrine in architecture until reproducibility/export requirements justify snapshots.

## 7. Rendering ownership

Rendering ownership is unresolved and should not be prematurely collapsed into BriefForge.

Three alternatives:

A. BriefForge owns rendering
   - BriefForge defines presentation package and implements renderers.
   - Pros: integrated responsibility, easier correctness checks across composition/rendering.
   - Cons: high scope creep; risks becoming browser/PDF/dashboard framework; violates current no-production constraint.

B. BriefForge owns presentation packages; separate renderers consume them
   - BriefForge defines semantic structure and output contracts.
   - Renderers are adapters or future sibling systems.
   - Pros: strongest constitutional separation; supports browser, document, portal, and future targets.
   - Cons: requires careful contract design; may slow first implementation.

C. BriefForge owns a canonical HTML renderer only
   - BriefForge treats HTML as canonical rendering output and everything else derives from HTML.
   - Pros: pragmatic, inspectable, interactive, browser-compatible.
   - Cons: risks making HTML implementation choices constitutional too early.

Initial recommendation: choose B constitutionally for now, while treating HTML as the leading candidate for first canonical rendering target pending further evidence.

## 8. Presentation ownership

BriefForge should own presentation semantics.

Presentation ownership includes:

- What sections exist.
- What order they appear in.
- Which evidence appears near which claim.
- Which caveats must be visible.
- Which visual slots are needed.
- Which interactions are presentation-level rather than data-analysis-level.
- Which appendix/detail/drilldown structures are included.
- Which output profiles are acceptable.

Presentation ownership excludes:

- Whether a claim is true.
- Whether data is canonical.
- Whether an indicator mapping is valid.
- Whether a model/analysis is methodologically correct.
- How a charting engine draws pixels.
- How a portal routes users.

Constitutional rule:

> BriefForge may restructure presentation of upstream meaning; it may not change upstream meaning.

## 9. Browser-first versus document-first architecture

This is a central unresolved tradeoff.

### Browser-first

Interpretation: canonical presentations are interactive web-native artifacts.

Pros:

- Best supports interactivity, drilldown, dynamic filtering, expandable evidence, hover/context panels, and future portal embedding.
- Aligns with HTML as likely canonical rendering target.
- Better for reusable components and future EIP navigation.

Cons:

- Can easily become a web app/dashboard project.
- Requires stronger boundaries between presentation and portal.
- Risks optimizing for UI before presentation semantics.

### Document-first

Interpretation: canonical presentations are structured documents, with browser rendering as one export target.

Pros:

- Stronger narrative discipline.
- Easier archiving, review, citation, and reproducibility.
- Lower implementation complexity early.

Cons:

- Can underfit interactive economics presentations.
- May lead to PDF/report-generator thinking and weak component reuse.
- Portal integration may become an afterthought.

### Presentation-package-first

Interpretation: canonical artifact is neither browser nor document; it is a structured presentation package that can render to browser/document targets.

Pros:

- Preserves constitutional separation.
- Delays target-specific commitment while allowing HTML-first implementation later.
- Best match for current uncertainty.

Cons:

- Requires more careful architecture before first renderer.
- Risk of overabstracting if not constrained by real archetypes.

Initial recommendation: adopt presentation-package-first as constitutional posture; investigate HTML-first as likely first renderer target, not as the whole architecture.

## 10. HTML as canonical rendering target

HTML is currently the strongest candidate for first canonical rendering target, but not yet a constitutional fact.

Arguments for HTML:

- Human inspectable.
- Browser-native interactivity.
- Portable across local files, servers, and portals.
- Can embed text, tables, charts, maps, references, and disclosure controls.
- Compatible with future export paths.
- Aligns with MetaHarvest evidence around specification-driven rendering and interactive analytics.

Arguments against premature HTML canonicality:

- HTML is a rendering representation, not necessarily the presentation semantic model.
- Treating HTML as canonical too early may bury provenance/caveat semantics in markup.
- Document/export needs may require a cleaner intermediate structure.
- Portal integration may need metadata outside HTML.

Recommended constitutional position:

> BriefForge should treat HTML as the leading candidate canonical rendered artifact, while treating the structured presentation package as the canonical semantic artifact.

Unresolved question:

- Should canonicality attach to semantic package, rendered HTML, or both at different lifecycle stages?

## 11. Component composition philosophy

MetaHarvest visualization and interactive analytics evidence reinforces separation between specification, composition, rendering, interaction, and data responsibilities.

Recommended philosophy:

1. Components are semantic presentation components first, not UI widgets.
2. Components should declare required input shape, provenance display obligations, caveat display obligations, and target compatibility.
3. Components should compose into sections and archetypes without owning upstream data truth.
4. Components should distinguish:
   - content components: title, summary, finding, caveat, methodology note;
   - evidence components: source reference, metric card, table, observation excerpt;
   - visual-intent components: chart slot, map slot, timeline slot, comparison slot;
   - interaction components: drilldown, expand/collapse, filter affordance, linked highlight;
   - navigation metadata: anchors, related sections, appendix links.
5. Component reuse should emerge from archetype pressure, not speculative library design.

Anti-patterns:

- Building a component library before real presentation archetypes are tested.
- Letting component aesthetics drive architecture.
- Treating chart components as analysis engines.
- Hiding caveats or provenance in optional footnotes.

## 12. Template philosophy

Templates are useful but dangerous.

A template can mean:

1. A conceptual archetype: e.g. economic release brief.
2. A semantic schema: required/optional sections and evidence obligations.
3. A layout recipe: visual arrangement and responsive behavior.
4. A rendering implementation: code/styles/components.
5. A content generator: automatically fills narrative.

Only (1) and possibly early (2) are appropriate in the constitutional phase.

Recommended doctrine:

- Templates should be treated as presentation contracts, not content generators.
- Templates must preserve upstream evidence/caveat obligations.
- Templates should be archetype-specific before becoming generic.
- Concrete templates should not be implemented until at least one report archetype has a validated semantic package.
- A template must not invent analysis to fill empty slots.

## 13. Presentation primitives

Candidate primitive families:

### Identity and framing

- presentation title
- subtitle/context line
- audience profile
- purpose statement
- generated/updated timestamp
- source project references
- freshness/staleness marker

### Narrative structure

- executive summary
- key takeaways
- section
- subsection
- transition
- conclusion/implication block

### Analytical content references

- finding block
- claim block
- thesis placeholder, if future project owns theses
- confidence statement
- uncertainty statement
- caveat block
- methodology note

### Evidence display

- source reference
- provenance trail
- metric card
- observation table
- comparison table
- chart slot
- map slot
- timeline slot
- appendix evidence bundle

### Interaction

- expand/collapse detail
- drilldown link
- filter/slice affordance
- linked evidence highlight
- glossary tooltip
- provenance reveal

### Governance/lifecycle

- review status
- upstream owner
- version/snapshot reference
- supersession marker
- output target profile
- render status
- validation status

These are conceptual primitives only; no schema or code is implemented here.

## 14. Candidate report archetypes

Candidate archetypes for future evidence investigation:

1. Economic release brief
   - Presents a new data release, key movements, caveats, and links to source/canonical observations.
   - Upstream owners: MacroForge for data; InsightForge only if conclusions are included.

2. Indicator deep dive
   - Explains one economic indicator over time, its source, construction, caveats, and interpretation limits.

3. Country or region profile
   - Combines multiple indicators and context into a structured profile.

4. Comparative macro brief
   - Compares countries, regions, periods, or indicators.

5. Insight/finding memo
   - Presents one or more InsightForge findings with evidence panels and caveats.

6. Market/investment context brief
   - Presents investment-relevant macro context without making portfolio decisions.

7. Scenario explainer
   - Presents assumptions, pathways, evidence, and uncertainty; may depend on future scenario/forecast ownership.

8. Research appendix
   - Evidence-heavy artifact for review, reproducibility, and audit.

9. Dashboard-brief hybrid
   - Combines narrative with interactive elements, but must not become a dashboard platform by default.

10. Map-based economic/geographic brief
   - Requires AtlasForge/GIS boundary clarity before implementation.

Highest-priority archetypes for next investigation:

- Economic release brief.
- Insight/finding memo.
- Indicator deep dive.

These are closest to current MacroForge/InsightForge boundaries and require the least speculative future ecosystem.

## 15. Long-term evolution strategy

BriefForge should evolve in layers, but only after architecture evidence supports each layer.

### Layer 0: Constitutional architecture

Current phase. Define ownership, exclusions, inputs/outputs, alternatives, risks, and evidence gaps.

### Layer 1: Semantic presentation package specification

Future architecture investigation. Define target-independent presentation package structure with provenance/caveat obligations.

### Layer 2: One archetype contract

Future architecture investigation. Select one report archetype and define required upstream inputs and presentation outputs.

### Layer 3: Validation rules

Future architecture/design work. Define how to detect unsupported claims, missing evidence, caveat suppression, broken references, and target incompatibilities.

### Layer 4: First rendering target decision

Future architecture decision. Decide whether HTML is canonical rendered output, first renderer only, or one of multiple targets.

### Layer 5: Minimal implementation slice

Not authorized by this report. Would require separate accepted task.

### Layer 6: Additional archetypes and target adapters

Future expansion only after one archetype proves the architecture.

Strategic rule:

> Do not build a generic presentation framework before one presentation archetype proves the semantic package and validation obligations.

## 16. Risks and architectural trade-offs

### Risk: Scope creep into dashboard platform

BriefForge could become a dashboard builder if interactive elements are treated as the core mission.

Mitigation: Presentation-package-first doctrine; dashboards are archetypes or downstream render targets, not project identity.

### Risk: Scope creep into portal/navigation

BriefForge could absorb user navigation because presentations need discovery.

Mitigation: BriefForge emits metadata; portal owns navigation.

### Risk: Scope creep into analysis

BriefForge could rewrite or summarize findings in ways that create new conclusions.

Mitigation: Preserve upstream owners and require explicit conclusion provenance.

### Risk: HTML overcommitment

HTML may be correct for first rendering but wrong as semantic canonical form.

Mitigation: Separate semantic package from rendered artifact until evidence proves otherwise.

### Risk: Template theater

Templates may create the illusion of correctness while suppressing caveats.

Mitigation: Treat templates as contracts with evidence/caveat obligations, not content generators.

### Risk: Premature component library

A component system may be built before archetypes reveal real reuse.

Mitigation: Derive reusable components from repeated archetype evidence.

### Risk: Unclear rendering ownership

If BriefForge owns neither rendering nor renderer contracts, outputs may be abstract and unusable. If it owns too much rendering, it becomes a UI framework.

Mitigation: Design output contracts before implementation and select one minimal renderer only after architectural investigation.

### Risk: Staleness/reproducibility tension

Reference-only presentations remain live but may become unreproducible; snapshots are reproducible but duplicate upstream data.

Mitigation: Investigate hybrid reference-plus-snapshot model.

### Risk: MetaHarvest overuse

Consultation can become ceremony.

Mitigation: Use MetaHarvest problem-first and evidence-only; BriefForge owns local relevance decisions.

## 17. Open questions requiring further evidence

1. What is the canonical semantic artifact?
   - Presentation package, HTML, both, or a layered lifecycle?

2. What minimum upstream input contract should MacroForge expose for presentation?
   - Series packages, release packages, indicator profiles, or curated data views?

3. What minimum upstream input contract should InsightForge expose?
   - Finding packages, conclusion packages, evidence bundles, or reviewed analytical memos?

4. Should BriefForge allow narrative synthesis, or only compose upstream-authored text blocks?
   - This determines whether it risks becoming an analysis/summarization project.

5. What is the constitutional boundary between chart slot, visualization specification, and chart rendering?
   - MetaHarvest evidence suggests specification/rendering separation, but local ownership is unresolved.

6. What is the canonical representation of interactivity?
   - Semantic affordances, declarative interaction specs, renderer-specific events, or portal-owned state?

7. What evidence must be visible in every presentation?
   - Source, owner, caveat, confidence, review state, freshness, reproducibility?

8. Should presentations be immutable, versioned, regeneratable, or live views?
   - This affects storage, reproducibility, and portal integration.

9. How should BriefForge handle stale upstream inputs?
   - Warning, invalidation, automatic re-render proposal, or portal-level notification?

10. Does BriefForge need a local artifact registry, or should portal/navigation own discovery?

11. Are documents/PDF exports a first-class concern or downstream export concern?

12. Which first archetype best tests the architecture with minimal scope creep?

13. What should future KnowledgeForge or EII own relative to BriefForge?
   - Knowledge/background and user-facing synthesis boundaries remain future-context only.

## MetaHarvest consultation determination

Consultation is triggered.

Reason:

- ProjectForge doctrine says MetaHarvest consultation is required for architecture definition when architectural uncertainty or relevant pattern evidence exists.
- MetaHarvest constitution says new project creation should consult MetaHarvest when architectural uncertainty or relevant pattern evidence exists.
- BriefForge directly raises unresolved questions about presentation, visualization, dashboard/report, component composition, rendering boundaries, browser/document architecture, and interactive analytics.
- MetaHarvest has fresh Gen2 evidence specifically relevant to these domains.

Relevant MetaHarvest evidence domains:

1. Visualization architecture
   - Sources: Vega-Lite, Apache ECharts, Observable Plot.
   - Relevant concepts: declarative visualization grammars, specification-driven rendering, visual composition, interaction dispatch, marks/layers/series, separation of data/spec/render/interaction/presentation.

2. Interactive analytics
   - Sources: Apache Arrow, Perspective, Grafana.
   - Relevant concepts: columnar representation, streaming updates, dashboard composition, client/server data responsibility boundaries, panel/dashboard composition, table/view update contracts.

3. GIS architecture
   - Sources: MapLibre GL JS, OpenLayers, Leaflet.
   - Relevant if map-based economic presentations become a priority.
   - Concepts: style/layer contracts, tile pipelines, source/layer/view separation, camera/interaction loops, projection boundaries.

4. Search/retrieval
   - Sources: Meilisearch, Typesense, OpenSearch.
   - Relevant if presentation discovery, faceting, or portal search boundaries are investigated.
   - Likely portal-owned, but BriefForge metadata must be compatible.

5. Knowledge graphs
   - Sources: Neo4j, Apache Jena, Memgraph.
   - Relevant if presentations need relationship navigation or knowledge-context graph embedding.
   - More likely KnowledgeForge/portal-related than BriefForge-owned.

6. Cross-cutting MetaHarvest patterns
   - Portable record contract.
   - Decoupled staged delivery pipeline.
   - Governed substitution boundary.
   - Explicit architectural contract.
   - Stage boundaries enable substitution.
   - Routing is not payload semantics.

Consultation conclusion:

MetaHarvest evidence materially improves the design by warning against collapsing specification, rendering, interaction, data, and dashboard ownership. It supports a staged architecture where BriefForge first owns a portable presentation record/contract and defers renderer/dashboard/portal implementation.

## Architectural assumptions

Accepted assumptions for the current report:

1. EIP remains an ecosystem of autonomous projects, not a monolith.
2. BriefForge is approved for creation by this task, but not approved for production implementation.
3. MacroForge and InsightForge remain upstream owners of data and conclusions respectively.
4. Future portal/navigation systems are likely but not approved implementation targets.
5. HTML is likely important but not yet proven as semantic canonical form.
6. Presentation correctness requires preserving provenance, caveats, confidence, and upstream ownership.
7. Rendering and presentation are separable until evidence proves they must be unified.
8. Templates should begin as conceptual archetypes/contracts, not code.
9. MetaHarvest evidence is advisory and does not grant implementation authority.

## Architecture changes observed or proposed

This report proposes an initial constitutional architecture for BriefForge only. It does not change ProjectForge, MacroForge, InsightForge, MetaHarvest, EIP root governance, or any future portal system.

Constitutional owner: BriefForge owns the local presentation-composition architecture proposed here.

Maintenance owner after adoption: BriefForge.

Would BriefForge keep this if ProjectForge disappeared? Yes. The presentation-engine boundary is project-specific and remains meaningful independent of ProjectForge.

Has this emerged in multiple projects? The exact BriefForge boundary is local to EIP, but MetaHarvest evidence shows repeated external separation of specification, rendering, composition, interaction, and data responsibilities.

Does it reduce or increase architectural attention? It reduces future attention by preventing premature scope collapse into analysis, dashboard, portal, or renderer ownership.

Minimum autonomy or optional convenience? Minimum autonomy. BriefForge needs a boundary to exist safely.

Level: Constitutional/project-architecture level.

## Recommendations for the next architectural investigation

Do not create implementation tasks yet.

Recommended next investigation:

1. Define the semantic presentation package candidate.
   - Required fields.
   - Provenance/caveat obligations.
   - Upstream reference model.
   - Target-independent versus target-specific sections.

2. Select one first archetype for architectural pressure-testing.
   - Recommended candidates: economic release brief, InsightForge finding memo, or indicator deep dive.

3. Investigate canonicality alternatives.
   - Semantic package canonical.
   - HTML canonical.
   - Dual canonical lifecycle.

4. Investigate renderer boundary alternatives.
   - BriefForge-owned renderer.
   - Separate renderer adapter.
   - HTML-only initial renderer.

5. Consult MetaHarvest's visualization and interactive analytics component cards in detail only for the unresolved renderer/specification/interaction questions.

6. Produce a decision artifact only after the above investigation narrows alternatives.

Stop condition:

- If the next investigation cannot define a minimal semantic package without choosing a renderer, record that as evidence that rendering and presentation ownership may be less separable than assumed.
- If it can define the package cleanly, implementation still remains unauthorized until a separate implementation task is approved.

## Final constitutional recommendation

BriefForge should begin as a presentation-package and presentation-composition project.

It should not begin as:

- a renderer;
- a browser app;
- a dashboard system;
- a template engine;
- a PDF/report generator;
- an analysis/summarization system;
- a portal/navigation layer;
- a data warehouse or canonical data owner.

The next architectural move is not to build HTML. It is to define the semantic presentation package strongly enough that HTML can later be selected, rejected, or scoped as a renderer target without changing the project's constitutional identity.
