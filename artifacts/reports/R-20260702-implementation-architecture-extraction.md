# Report: BriefForge Implementation Architecture Extraction

Date: 2026-07-02
Type: implementation-phase architectural investigation
Status: Final
Owner: BriefForge
Scope: minimal implementation architecture extraction from frozen constitution and MetaHarvest evidence

## 1. Executive conclusion

BriefForge does not need a dashboard platform, browser application, visualization engine, map framework, template engine, API platform, search system, portal, or static-site generator to realize its frozen constitution.

The smallest implementation architecture capable of realizing the constitution is:

1. A portable semantic Presentation Package record contract.
2. A deterministic package validation boundary.
3. A minimal composition-semantics representation inside the package contract.
4. A governed downstream-consumer boundary that preserves renderer/export/portal substitution without making BriefForge own rendering, exports, browser delivery, templates, dashboards, maps, visualization, search, or portal navigation.
5. Optional local inspection/serialization tooling only insofar as it serves contract authoring, validation, and handoff.

The strongest MetaHarvest evidence supports reusing mature architectural patterns, not adopting mature products.

Implementation should therefore maximize reuse at the level of:

- explicit architectural contracts;
- portable record contracts;
- governed substitution boundaries;
- contracted extension surfaces;
- stage-boundary discipline;
- validation-result records;
- schema/version discipline.

Implementation should minimize custom architecture by not building systems whose mature versions already exist elsewhere and whose responsibilities are constitutionally excluded from BriefForge.

## 2. Governing frozen constitution

This investigation treats the frozen BriefForge constitution as fixed.

BriefForge owns exactly:

1. Presentation Contract.
2. Composition Semantics.
3. Presentation Validation Obligations.

The canonical object is the structured semantic Presentation Package.

Required package category types:

1. Package identity.
2. Organizing Purpose.
3. Organized presentation statements with target-independent encounter semantics.
4. Upstream-owned references where dependency exists.
5. Presentation obligations.

BriefForge owns presentation meaning only.

BriefForge references economic and analytical meaning owned elsewhere.

BriefForge excludes delivery meaning.

Explicit non-scope includes rendering engines, browser applications, dashboards, visualization engines, maps/GIS rendering, search/indexing/ranking, portal navigation/routing/sessions/personalization, APIs as constitutional architecture, template engines, and generic UI component libraries.

## 3. MetaHarvest consultation scope

The existing MetaHarvest knowledge base was consulted from:

- `source_registry.yaml`
- `project_cards/*.yaml`
- `component_cards/*.yaml`
- `architecture_patterns/*.yaml`
- `architecture_primitives/*.yaml`
- `architecture_invariants/*.yaml`
- relevant human summaries and reports where needed

The consultation focused on existing analyzed projects in the following categories:

- browser report generation;
- structured document generation;
- specification/render separation;
- interactive reporting;
- dashboard architecture;
- visualization engines;
- rendering pipelines;
- component systems;
- map frameworks;
- report generation;
- static site generation;
- documentation generators;
- presentation engines;
- knowledge exploration interfaces.

MetaHarvest contains no direct mature “BriefForge-like” presentation-contract system. It does contain strong evidence for adjacent reusable architecture.

## 4. MetaHarvest architectural patterns most relevant to BriefForge

### 4.1 Portable record contract

MetaHarvest pattern: `architecture_patterns/portable-record-contract.yaml`

Problem solved:

Progress, observations, or analytical execution become hard to recover, audit, or interpret when represented only as hidden control flow or in-memory structures.

BriefForge relevance:

Very high. The Presentation Package is precisely a portable semantic record contract: it must preserve package identity, organizing purpose, presentation statements, upstream-owned references, and obligations across future consumers without making the consumer the source of truth.

Adoption decision:

Adopt the pattern.

BriefForge-specific implementation need:

Implement a project-local Presentation Package schema/record shape. Do not adopt a third-party product for this core semantic contract.

### 4.2 Explicit architectural contract

MetaHarvest primitive: `architecture_primitives/explicit-architectural-contract.yaml`

BriefForge relevance:

Very high. The frozen constitution is itself a contract boundary. Implementation must make the package contract explicit enough to validate and consume.

Adoption decision:

Adopt the pattern.

BriefForge-specific implementation need:

Implement the minimal explicit contract required by the five required package categories and obligation rules.

### 4.3 Governed substitution boundary

MetaHarvest pattern: `architecture_patterns/governed-substitution-boundary.yaml`

Problem solved:

A system needs components or stages to be swappable without eroding correctness, maturity, or architectural clarity.

BriefForge relevance:

High for downstream consumption. Future renderers, exporters, document generators, browser viewers, portals, or inspection tools must be substitutable consumers of the package, not semantic authorities.

Adoption decision:

Adapt the pattern.

BriefForge-specific implementation need:

Define a lightweight downstream-consumer boundary and acceptance criteria. Do not implement renderer plugins yet. Do not implement an extension marketplace or runtime plugin framework unless repeated evidence later justifies it.

### 4.4 Contracted extension surface

MetaHarvest pattern: `architecture_patterns/contracted-extension-surface.yaml`

Problem solved:

A system needs to admit new behavior without destabilizing its core or allowing arbitrary incompatible extensions.

BriefForge relevance:

Medium. BriefForge will likely need a stable boundary for future renderers/exporters/import adapters, but the constitution does not require a plugin architecture now.

Adoption decision:

Adapt narrowly.

BriefForge-specific implementation need:

Represent future extension points as architectural boundaries and tests, not as production plugin machinery.

### 4.5 Decoupled staged delivery pipeline

MetaHarvest pattern: `architecture_patterns/decoupled-staged-delivery-pipeline.yaml`

Problem solved:

Direct producer-consumer coupling makes execution, transformation, routing, retry, and delivery failure modes hard to isolate.

BriefForge relevance:

Medium-low for initial implementation. BriefForge has a meaningful conceptual flow — create/load package -> validate package -> hand package to consumer — but does not yet need queues, routing, distributed stages, delivery infrastructure, or browser serving.

Adoption decision:

Adapt conceptually; reject operational pipeline implementation for the minimal architecture.

BriefForge-specific implementation need:

Keep stages conceptually separate in code/tests when implementation begins, but avoid queue/process/pipeline infrastructure.

### 4.6 Routing is not payload semantics

MetaHarvest invariant: `architecture_invariants/routing-is-not-payload-semantics.yaml`

BriefForge relevance:

Very high. It directly protects the frozen boundary: portal routing, browser navigation, search ranking, export target, or renderer layout must not define package semantics.

Adoption decision:

Adopt as a boundary verification rule.

BriefForge-specific implementation need:

Any future consumer boundary must prove it cannot reinterpret target-independent encounter semantics as delivery-specific routing.

## 5. Project-by-project MetaHarvest comparison matrix

Legend:

- Alignment: High means the project’s architecture teaches a directly reusable pattern without violating the constitution. Medium means useful evidence with significant boundary caution. Low means mostly excluded responsibility evidence.
- Adoption potential: Pattern means architectural pattern only; dependency means possible future library dependency; reject means do not adopt for BriefForge core.

| Project | MetaHarvest category | Constitutional alignment | Implementation architecture observed | Reusable subsystems/interfaces/concepts | Adoption potential | BriefForge decision |
|---|---|---:|---|---|---|---|
| Grafana | interactive analytics / dashboards | Medium | Data-source plugin query contracts, panel/dashboard composition, transformations, alerting | explicit contracts; dashboard composition as cautionary evidence; datasource boundaries | Pattern only | Adapt boundary concepts; reject dashboard/platform adoption |
| Metabase | BI query product / semantic layer | Medium-low | Query processor, driver extension contract, durable application model records, API/channel boundary | durable product records; driver boundary; API/channel separation | Pattern only | Adapt record-boundary lessons; reject BI/query/API/product adoption |
| Apache Superset | BI dashboard semantic query surface | Medium-low | Dataset semantic contracts, chart/dashboard record model, visualization plugin boundary, security/database governance | chart/dashboard records; visualization plugin boundary; semantic-dataset caution | Pattern only | Adapt substitution-boundary evidence; reject dashboard/semantic-query ownership |
| Perspective | interactive analytics | Medium | Table/view/update contract, pivot/expression aggregation pipeline, client/server rendering boundary | client/server rendering boundary; table/view contract | Pattern only | Adapt rendering-boundary caution; reject runtime analytics/aggregation ownership |
| Vega-Lite | visualization architecture | Medium-high for spec/render separation; low for core adoption | Declarative visual encoding spec, transform/composition pipeline, compiler/runtime boundary | specification/render separation; compiler boundary | Possible downstream dependency later, not core | Adopt as external-renderer evidence; do not make visual spec canonical |
| Apache ECharts | visualization architecture | Medium | Option-driven chart model, series renderer pipeline, interaction dispatch/action model | option/component model; renderer pipeline; interaction boundary | Possible downstream dependency later, not core | Adapt renderer-boundary concepts; reject interaction/render ownership |
| Observable Plot | visualization architecture | Medium | Mark-transform contract, layered composition, scale/facet abstraction | declarative marks/transforms; layered composition | Possible downstream dependency later, not core | Adapt only as evidence; reject visualization grammar in package core |
| Leaflet | GIS architecture | Low-medium | Map/layer/control contract, tile loading pipeline, evented interaction model | layer/control separation; event model caution | Downstream only | Reject core adoption; possible future map renderer consumer only |
| OpenLayers | GIS architecture | Low-medium | Source/layer/view separation, projection boundary, interaction/control pipeline | strict map source/layer/view separation | Downstream only | Reject core adoption; preserve map as external consumer |
| MapLibre GL JS | GIS architecture | Low-medium | Style-spec layer contract, tile-source/cache pipeline, camera interaction/render loop | style-spec/render separation; source/layer contract | Downstream only | Reject core adoption; possible external map-render target only |
| Backstage | developer portal/catalog | Medium for portal boundary; low for adoption | Catalog entity descriptors, provider-owned ingestion, backend plugin modules, scaffolder task engine | entity descriptor contract; provider-owned ingestion; plugin boundaries | Pattern only | Adapt catalog/portal boundary lessons; reject portal/catalog/scaffolder ownership |
| dbt | transformation/documentation/manifest | High for manifest/contract discipline; low for transformation adoption | File-first SQL/YAML/Jinja compiler to manifest, lineage, tests, metadata | manifest records; contract tests; schema evolution discipline | Pattern only | Adapt manifest/validation lessons; reject transformation/Jinja/template ownership |
| Great Expectations | validation/docs | High for validation architecture; low for data validation domain | Expectation suites, validation definitions, checkpoints, stores, Data Docs | validation suite concept; validation-result records; Data Docs as downstream docs | Pattern only | Adapt deterministic validation-result pattern; reject data-quality/domain validation |
| OpenMetadata | metadata catalog/knowledge exploration | Medium | Schema-first entity model, lineage resources, governance taxonomy, context interface | schema-first entity contract; ownership/lineage visibility | Pattern only | Adapt ownership visibility concepts; reject catalog/search/governance platform adoption |
| OpenLineage | lineage metadata standard | Medium-high for references/ownership | Run/job/dataset/facet event model and extension facets | reference/facet extension model; transport boundary | Pattern only | Adapt upstream-reference/facet idea; do not adopt lineage event standard as core |
| Apache Arrow | portable data format | Medium | Columnar memory format, IPC/Flight boundary, language-binding boundary | portable representation contract; engine independence | Possible dependency only if later data payloads require it | Adapt portability principle; reject data format ownership |
| FastAPI | typed API framework | Low-medium | Routing contract, dependency graph, validation error response, OpenAPI generation | validation error shape; schema generation boundary | Reject for minimal core | Reject API framework adoption; APIs are non-constitutional |
| Typesense | search/retrieval | Low | Collection schema, facet/filter query pipeline, cluster boundary | schema/filter boundary as cautionary evidence | Reject core | Reject search/ranking ownership |
| Meilisearch | search/retrieval | Low | Index task queue, filter/facet/ranking contract, document API boundary | indexing task caution; ranking boundary | Reject core | Reject search/ranking/indexing ownership |
| OpenSearch | search/retrieval | Low | Index/shard/segment model, query DSL/aggregation pipeline, plugin boundary | plugin boundary; aggregation pipeline caution | Reject core | Reject search/analytics engine ownership |
| Apache Jena | knowledge graph | Medium-low | RDF dataset graph model, SPARQL query/inference pipeline, ontology/vocabulary boundary | graph relation model; ontology boundary | Pattern only | Adapt relation/reference vocabulary caution; reject KG/query/inference adoption |
| Neo4j | knowledge graph | Medium-low | Property graph record model, Cypher traversal query boundary, transaction/index/storage | nodes/relationships as graph-model evidence | Pattern only | Adapt relation semantics cautiously; reject graph DB adoption |
| Memgraph | knowledge graph | Medium-low | Property graph streaming runtime, Cypher module extensions, trigger/query/update pipeline | graph extension and trigger pipeline caution | Pattern only | Reject runtime adoption; no streaming graph system needed |
| n8n | workflow automation | Low-medium | Workflow graph, webhook triggers, execution persistence, credential-node interface | workflow graph as caution; execution records | Pattern only | Reject workflow automation; no browser workflow builder |
| Airflow | workflow orchestration | Low-medium | DAG definitions, scheduler loop, timetable contract, asset scheduling | static DAG boundary; scheduling discipline | Pattern only | Reject orchestration; no scheduler needed |
| Dagster | asset orchestration | Medium | Asset graph, checks, metadata schema versioning, source/external assets | external asset boundary; validation checks | Pattern only | Adapt upstream-owned reference/source-boundary concept; reject orchestration |
| DVC | artifact/versioning | Medium | Declaration/lockfile split, content-addressed outputs, graph reproduction planner | declaration/lockfile split; reproducible artifact records | Pattern only | Adapt only if package/version provenance later needs it; reject data-artifact system |
| Terraform | declarative state/diff | Medium | Configuration modules, state snapshots, provider protocol, plan/apply graph | plan/desired-state separation; provider boundary | Pattern only | Adapt plan-vs-output boundary; reject infra-style apply engine |
| Kubernetes | declarative control plane | Medium | Versioned API object contract, resourceVersion/watch, controller pipeline, CRDs | versioned object contracts; CRD extension caution | Pattern only | Adapt versioned object discipline; reject control-plane machinery |
| OpenTelemetry Collector | telemetry pipeline | Medium | Telemetry pipeline contract, component factories, connector routing, stability governance | stable component contracts; maturity governance | Pattern only | Adapt maturity/status labels; reject telemetry pipeline |
| Temporal | durable workflow | Low-medium | Durable workflow history, task queues, timers/retries, update protocol | durable history where process recovery matters | Pattern only | Reject workflow engine; no long-running process required |
| Prefect | workflow state | Low-medium | Flow/task declarations, durable run state, deployments/work pools, integration blocks | durable run state/artifacts | Pattern only | Reject orchestration; maybe adapt result artifact discipline |
| Polars | lazy dataframe/query engine | Low-medium | Lazy DSL, plan serialization, optimization/execution pipeline, IO plugins | plan/runtime separation | Pattern only | Reject data/query engine ownership |
| DuckDB | embedded analytics | Low-medium | Embedded analytics boundary, vectorized execution, extension loading | embedded local runtime boundary | Pattern only | Reject analytics engine; possible external consumer input only |
| Airbyte/Meltano | data integration | Low | Connector protocols, catalogs, manifests, state checkpoints | connector boundary evidence | Pattern only | Reject ingestion/connectors |
| Marquez | lineage backend | Medium | Lineage API boundary, metadata DB record model, service coordination | lineage/ownership visibility | Pattern only | Adapt reference visibility concept; reject lineage backend ownership |

Non-selected MetaHarvest projects were also scanned through project-card inventory. Agent systems, ML lifecycle platforms, distributed runtimes, infrastructure tools, and source-ingestion/orchestration systems are useful only as broad evidence for contracts, records, boundaries, and validation; they do not materially change BriefForge's minimal architecture.

## 6. What already exists in mature systems

Mature systems already provide:

1. Dashboard composition and browser delivery
   - Grafana, Metabase, Superset.
   - BriefForge should not implement these responsibilities.

2. Visualization grammars and renderers
   - Vega-Lite, Observable Plot, Apache ECharts.
   - BriefForge should not implement visualization grammars or rendering engines.

3. Map rendering frameworks
   - Leaflet, OpenLayers, MapLibre GL JS.
   - BriefForge should not implement maps or GIS rendering.

4. Search and knowledge exploration platforms
   - OpenSearch, Typesense, Meilisearch, OpenMetadata, graph systems.
   - BriefForge should not implement search, ranking, catalog, or knowledge graph exploration.

5. API frameworks
   - FastAPI and many product APIs in BI systems.
   - BriefForge should not make APIs a constitutional or initial implementation responsibility.

6. Workflow/orchestration systems
   - Airflow, Dagster, Temporal, Prefect, n8n.
   - BriefForge should not implement orchestration beyond local deterministic validation flow.

7. Validation frameworks and documentation/result surfaces
   - Great Expectations, dbt, FastAPI validation, schema-first metadata systems.
   - BriefForge should reuse the pattern of explicit validation definitions and validation-result records, not the data-quality frameworks themselves.

8. Portable record contracts and manifest patterns
   - OpenLineage, dbt, Terraform, Kubernetes, Arrow, Great Expectations, DVC.
   - BriefForge should implement its own minimal semantic Presentation Package record, because this is the project-specific core.

## 7. What genuinely needs to be BriefForge-specific

BriefForge-specific implementation is necessary only where the frozen constitution defines semantics no mature external product owns for us:

1. Presentation Package contract
   - Must encode the five required category types.
   - Must preserve target-independent encounter semantics.
   - Must preserve upstream-owned references and obligations.
   - No mature external system in MetaHarvest directly represents this constitutional object.

2. Presentation-local validator
   - Must check package structure, references, obligations, internal consistency, and boundary compliance.
   - Must not validate economic truth, analytical correctness, renderer quality, portal behavior, or UI quality.
   - Existing systems provide validation patterns, not this domain-specific validation rule set.

3. Boundary-preservation checks
   - Must detect when implementation proposals or package records drift into excluded responsibilities.
   - This is specific to BriefForge's constitution.

4. Minimal downstream-consumer contract
   - Must define what a future renderer/exporter/browser/portal may consume and what it must preserve.
   - Must not implement those consumers.
   - This boundary is specific because it translates BriefForge obligations into downstream acceptance criteria.

Everything else should remain external, deferred, or pattern-only until repeated evidence justifies more.

## 8. Derived capability decomposition

The following capabilities are derived from the constitution and MetaHarvest evidence. They are not implementation tasks.

### Capability A: Presentation Package record contract

Constitutional source:

- Presentation Contract.
- Canonical Presentation Package.

MetaHarvest evidence:

- Portable record contract.
- Explicit architectural contract.
- dbt manifest discipline.
- Kubernetes versioned API object discipline.
- OpenLineage run/job/dataset/facet model.

Capability definition:

A project-local structured representation for package identity, Organizing Purpose, organized presentation statements, upstream-owned references, and presentation obligations.

Classification:

Implement.

Justification:

This is the irreducible BriefForge-specific object. Mature systems provide record-contract patterns, not the BriefForge semantic contract.

Minimality guard:

Do not include renderer instructions, UI components, templates, dashboards, maps, search metadata, portal routing, or analytical conclusions.

### Capability B: Schema/version discipline

Constitutional source:

- Presentation Contract stability.
- Implementation Constitution invariant chain.

MetaHarvest evidence:

- Kubernetes versioned API objects.
- dbt metadata schema evolution.
- OpenMetadata schema-first entity model.
- FastAPI OpenAPI generation boundary.

Capability definition:

A minimal versioned schema discipline for the Presentation Package contract and validation results.

Classification:

Adapt.

Justification:

Version discipline is mature and reusable as a pattern. BriefForge needs it, but not a large schema registry or API framework.

Minimality guard:

Prefer file-backed versioning and simple compatibility rules before introducing schema registries or services.

### Capability C: Presentation-local validation engine

Constitutional source:

- Presentation Validation Obligations.

MetaHarvest evidence:

- Great Expectations expectation suites and validation definitions.
- dbt contracts/tests.
- FastAPI validation error response contracts.
- Dagster checks.

Capability definition:

A deterministic validation process that checks structural completeness, obligation attachment, reference shape, internal consistency, and boundary compliance.

Classification:

Implement, using adapted validation-result patterns.

Justification:

No external validation framework understands BriefForge's presentation obligations. Existing systems validate data/API/assets, not target-independent presentation meaning.

Minimality guard:

Do not validate upstream truth, analysis quality, canonicalization correctness, renderer behavior, or user-facing quality.

### Capability D: Validation result / acceptance record

Constitutional source:

- Validation obligations as correctness condition.

MetaHarvest evidence:

- Great Expectations validation results.
- dbt test/manifest outputs.
- DVC declaration/lockfile split.
- Terraform plan/result separation.

Capability definition:

A small inspectable record of validation status, errors, warnings, package identity, schema version, and boundary status.

Classification:

Adapt.

Justification:

The pattern is mature. BriefForge needs only a minimal local record, not a validation platform.

Minimality guard:

Do not create dashboards, docs sites, databases, or UI reports for validation results in the minimal implementation.

### Capability E: Composition semantics representation

Constitutional source:

- Composition Semantics.
- Organized presentation statements with target-independent encounter semantics.

MetaHarvest evidence:

- Grafana dashboard composition as cautionary evidence.
- Vega-Lite composition as spec/render separation evidence.
- Observable Plot layered composition as visualization-specific caution.
- Neo4j/Jena graph relation models as relation vocabulary evidence.
- Airflow/Dagster DAGs as caution against over-orchestration.

Capability definition:

A minimal way to represent order, partial order, grouping, hierarchy, relation, or navigable encounter paths where constitutionally needed.

Classification:

Implement minimally.

Justification:

This is BriefForge-specific because the semantics are target-independent presentation encounter semantics, not UI layout, visualization layers, dashboard panels, graph queries, workflow DAGs, or portal navigation.

Minimality guard:

Start with the smallest representation that can express required relationships among presentation statements. Do not freeze a broad primitives/components/blocks/sections hierarchy.

### Capability F: Upstream reference model

Constitutional source:

- Upstream-owned references where dependency exists.

MetaHarvest evidence:

- OpenLineage facets and run/job/dataset model.
- OpenMetadata ownership/lineage resources.
- Dagster source/external assets.
- Marquez lineage backend.

Capability definition:

A reference shape that identifies upstream owner, referenced artifact/object, relevant part, dependency kind, and attached obligations without copying upstream meaning into BriefForge.

Classification:

Implement minimally; adapt lineage/reference concepts.

Justification:

The concept is BriefForge-specific but should borrow the mature idea that references/facets preserve ownership across boundaries.

Minimality guard:

Do not implement lineage storage, metadata catalog, search, freshness polling, data ownership, or canonical data access.

### Capability G: Presentation obligation model

Constitutional source:

- Presentation obligations.

MetaHarvest evidence:

- Great Expectations validation definitions.
- OpenMetadata governance taxonomy.
- OpenLineage facets.
- dbt contracts.

Capability definition:

Represent obligations for ownership visibility, evidence/provenance visibility, caveat/scope visibility, confidence/uncertainty visibility, freshness/review-state visibility, non-transformation, and non-detachment.

Classification:

Implement.

Justification:

This is core to BriefForge. External systems provide governance and validation analogies but not the exact obligation categories.

Minimality guard:

Obligations should be semantic constraints and validation checks, not renderer layout rules.

### Capability H: Downstream consumer boundary

Constitutional source:

- Rendering pipeline as downstream consumption boundary, not BriefForge constitutional ownership.

MetaHarvest evidence:

- Vega-Lite compiler/runtime boundary.
- Apache ECharts renderer pipeline.
- Perspective client/server rendering boundary.
- MapLibre style-spec renderer boundary.
- Metabase API/channel boundary.
- Superset visualization plugin boundary.

Capability definition:

A future-facing boundary saying how a validated package may be consumed by renderers/exporters/portals without becoming canonical truth.

Classification:

Adapt.

Justification:

BriefForge needs a boundary, not a renderer. Mature systems strongly support spec/render separation and plugin boundaries, but implementation should stop at a consumer contract.

Minimality guard:

No renderer plugins, no browser delivery, no export engines, no templates, no APIs in the minimal implementation.

### Capability I: Renderer/export/browser delivery

Constitutional source:

- Explicit non-scope.

MetaHarvest evidence:

- Grafana, Metabase, Superset, Vega-Lite, ECharts, Observable Plot, Leaflet, OpenLayers, MapLibre all provide mature external implementations.

Capability definition:

Actual production rendering, export generation, browser delivery, document output, dashboard display, map display, visualization grammar, or portal UI.

Classification:

Reject for BriefForge minimal implementation.

Justification:

These systems already exist and the constitution excludes ownership. Future use should be downstream, not BriefForge core.

Minimality guard:

Any future renderer must consume validated packages and preserve obligations. It must not redefine package semantics.

### Capability J: Template engine / component library

Constitutional source:

- Explicit non-scope; deferred vocabulary.

MetaHarvest evidence:

- Backstage scaffolder templates, BI dashboard component models, chart component models, map layer controls.

Capability definition:

Reusable template/component system for presentation creation or rendering.

Classification:

Reject for minimal implementation.

Justification:

Templates/components are implementation/delivery vocabulary and were explicitly deferred from constitutional architecture.

Minimality guard:

Conceptual examples may appear in documentation, but no template files, template engine, or component library should be created in the minimal implementation.

### Capability K: API/service boundary

Constitutional source:

- APIs are not constitutional architecture.

MetaHarvest evidence:

- FastAPI routing/OpenAPI boundary; Metabase/Superset product APIs.

Capability definition:

HTTP/RPC API for BriefForge package operations.

Classification:

Reject for minimal implementation.

Justification:

Local file/tool execution is enough for the first implementation. API adoption would add surface area before there is evidence of a consuming service need.

Minimality guard:

If an API becomes necessary later, it must be downstream/access infrastructure, not constitutional authority.

### Capability L: Search/catalog/portal discovery

Constitutional source:

- Portal navigation, search, indexing, ranking, sessions, personalization are excluded.

MetaHarvest evidence:

- OpenMetadata, Backstage, OpenSearch, Typesense, Meilisearch.

Capability definition:

Discovery, registry, navigation, ranking, catalog, or reading queue functionality.

Classification:

Reject for BriefForge minimal implementation.

Justification:

Mature systems already exist and the constitution explicitly excludes this responsibility.

Minimality guard:

Package identity may support self-description, but not portal ownership.

## 9. Adopt / Adapt / Implement / Reject recommendations

| Capability | Decision | Reason |
|---|---|---|
| Presentation Package record contract | Implement | Constitution-specific canonical object; no mature external system owns these semantics |
| Schema/version discipline | Adapt | Mature pattern; keep local and simple |
| Presentation-local validation engine | Implement | Constitution-specific obligation checks |
| Validation result / acceptance record | Adapt | Mature validation-result pattern; minimal local record sufficient |
| Composition semantics representation | Implement minimally | Core BriefForge meaning; must not borrow UI/dashboard/visualization semantics wholesale |
| Upstream reference model | Implement minimally / Adapt concepts | Specific reference obligations; borrow lineage/facet ownership idea |
| Presentation obligation model | Implement | Core constitutional correctness condition |
| Downstream consumer boundary | Adapt | Needed to preserve renderer/export substitution without implementation |
| Renderer plugins | Reject now | Rendering excluded; mature renderers exist downstream |
| Browser delivery | Reject now | Browser apps excluded; mature browser/report systems exist |
| Static artifact generation/export engines | Reject now | Exports are downstream representations; not minimal core |
| Template engine | Reject now | Templates explicitly deferred/excluded |
| Generic UI components | Reject now | Explicitly excluded |
| Dashboard architecture | Reject now | Mature systems exist and dashboard ownership is excluded |
| Visualization grammar/engine | Reject now | Mature systems exist; package must remain target-independent |
| Map/GIS rendering | Reject now | Mature systems exist; map rendering excluded |
| Search/catalog/portal | Reject now | Explicit non-scope |
| API/service layer | Reject now | Not needed for local minimal implementation; APIs not constitutional |
| Workflow/orchestration | Reject now | No evidence of long-running/delivery orchestration need |

## 10. Minimal implementation architecture

The minimal implementation architecture should be a small local contract-and-validation system.

Conceptual architecture:

```text
BriefForge-owned semantic layer

Presentation Package record
  - package identity
  - organizing purpose
  - presentation statements
  - target-independent encounter semantics
  - upstream-owned references
  - presentation obligations

Validation boundary
  - schema/category completeness
  - statement/reference/obligation consistency
  - boundary checks
  - validation result record

Downstream consumer boundary
  - consumes validated package
  - must preserve obligations
  - may render/export/display elsewhere
  - never becomes semantic authority
```

Not included:

```text
No renderer engine
No browser app
No dashboard
No visualization grammar
No map framework
No API service
No template engine
No portal/search/catalog
No workflow runtime
No data ingestion
No analysis
No canonical data store
```

## 11. Boundary verification

Every proposed capability preserves the frozen constitutional boundaries as follows.

### 11.1 Data and analysis boundary

Proposed capabilities never fetch, canonicalize, transform, analyze, or judge upstream data.

The upstream reference model records external ownership and required obligations only.

Validator checks reference shape and obligation preservation, not upstream truth.

### 11.2 Rendering boundary

Renderer/export/browser delivery is rejected from the minimal architecture.

The downstream consumer boundary exists only to prevent future consumers from becoming semantic authorities.

### 11.3 Template/component boundary

Template and component systems are rejected.

Composition semantics remain target-independent statement organization, not UI components, layout blocks, sections, templates, chart layers, map layers, or dashboard panels.

### 11.4 Portal/search boundary

Package identity may contain self-description required to understand the package.

It must not become routing, search ranking, reading queues, personalization, session state, registry ownership, or portal navigation.

### 11.5 Validation boundary

Validation is presentation-local.

It may check:

- required category presence;
- internal structural consistency;
- statement membership in Organizing Purpose;
- upstream-reference presence where dependency exists;
- obligation attachment and non-detachment;
- boundary violations.

It must not check:

- economic truth;
- analysis correctness;
- canonicalization correctness;
- visual quality;
- renderer behavior;
- portal behavior;
- user engagement or communication effectiveness beyond contract obligations.

## 12. Candidate architecture eliminated by evidence

### 12.1 Adopt Grafana/Metabase/Superset-style dashboard architecture

Decision: Reject.

Reason:

These architectures solve dashboard/product analytics problems. BriefForge's constitution excludes dashboards, query products, UI, rendering, and data-source ownership. Their reusable value is boundary evidence only.

### 12.2 Adopt Vega-Lite as canonical package model

Decision: Reject.

Reason:

Vega-Lite is strong evidence for declarative spec/render separation, but its semantics are visual-encoding semantics. BriefForge's canonical object is target-independent presentation meaning, not visual encoding.

### 12.3 Adopt a graph database or RDF model for presentation relationships

Decision: Reject for minimal implementation.

Reason:

Graph systems demonstrate relation modeling, but adopting graph databases/RDF/SPARQL would import query/inference/storage responsibilities. BriefForge needs only minimal encounter-semantics relationships.

### 12.4 Adopt a portal/catalog system

Decision: Reject.

Reason:

Backstage/OpenMetadata demonstrate mature catalog/entity patterns, but BriefForge excludes portal navigation, catalog/search, and ecosystem coordination. Self-description is enough.

### 12.5 Adopt a workflow engine

Decision: Reject.

Reason:

Validation flow can remain local and deterministic. Workflow engines solve scheduling, durable process, retries, orchestration, and external execution boundaries not required by the constitution.

### 12.6 Build a plugin architecture immediately

Decision: Reject for minimal implementation; adapt boundary concept only.

Reason:

MetaHarvest strongly supports contracted extension surfaces when a stable extension ecosystem exists. BriefForge does not yet have multiple real consumers. Premature plugin machinery would be framework accumulation.

## 13. Minimal implementation roadmap

This is a roadmap, not a set of implementation tasks.

### Phase 1: Contract-only vertical slice

Goal:

Create the smallest project-local representation of a Presentation Package and validation result that can express the frozen five-category contract.

Architecture outcome:

- A package record exists.
- A validation boundary exists.
- No renderer, browser, template, API, dashboard, map, or portal exists.

Evidence required before moving on:

- At least one example package can be validated as structurally complete.
- At least one invalid package demonstrates boundary/obligation failure.
- Validation output is inspectable.

### Phase 2: Composition-semantics pressure test

Goal:

Test whether the minimal representation can express order, partial order, grouping, hierarchy, relation, and navigable encounter path without collapsing into UI/layout/template semantics.

Architecture outcome:

- Composition representation remains target-independent.
- No primitives/components/blocks/sections hierarchy is frozen unless evidence forces it.

Evidence required before moving on:

- Multiple package shapes exercise different encounter semantics.
- Validator catches at least one composition/boundary violation.

### Phase 3: Upstream-reference and obligation preservation pressure test

Goal:

Test whether upstream references and presentation obligations can remain attached across package composition and downstream-consumer handoff.

Architecture outcome:

- References preserve upstream ownership.
- Obligations cannot be detached from dependent statements.

Evidence required before moving on:

- A package with multiple upstream owners remains valid only when ownership/provenance/caveat/confidence/freshness obligations remain attached.

### Phase 4: Downstream-consumer boundary specification

Goal:

Specify what future renderers/exporters/browser/portal consumers must preserve before any consumer implementation is approved.

Architecture outcome:

- A renderer/export/browser implementation can later be evaluated without becoming constitutional authority.

Evidence required before moving on:

- Boundary tests can distinguish valid consumption from semantic reinterpretation.

### Phase 5: Renderer selection investigation, only if needed

Goal:

If and when a validated package needs actual presentation output, choose an external rendering path by obligation preservation and minimal custom code.

Likely candidates to compare later:

- HTML document/static artifact path.
- Vega-Lite/Observable Plot/ECharts for chart-specific downstream rendering.
- Leaflet/OpenLayers/MapLibre for map-specific downstream rendering.
- Existing document/static-site tooling if document-first evidence becomes stronger.

Explicitly not authorized by this report:

- renderer implementation;
- browser implementation;
- export implementation;
- template creation;
- API creation.

## 14. Open questions requiring further evidence

1. What is the smallest concrete serialization that preserves package semantics without creating a template language?

2. Should the first package representation be YAML, JSON, typed Python objects, or another local format?

3. How much schema formalism is needed before examples become misleading or validation becomes brittle?

4. What reference identifiers will MacroForge, InsightForge, MetaHarvest, and future EIP systems expose for upstream-owned artifacts?

5. How should obligations attach when one presentation statement depends on multiple upstream artifacts with conflicting caveats or freshness states?

6. What downstream consumer boundary is sufficient before a renderer/exporter can be safely implemented?

7. Should HTML become a preferred downstream target later, or remain one renderer choice among several until actual use cases prove otherwise?

8. What is the minimum example corpus needed to falsify the package contract before production implementation expands?

## 15. Recommendation for the next architectural investigation

Before production implementation expands beyond a contract-only slice, perform a narrow representation-selection investigation:

Question:

Which local representation strategy best preserves the frozen Presentation Package semantics with the least custom architecture and the strongest validation leverage?

Compare only:

- YAML/JSON file-backed package records;
- JSON Schema or equivalent schema validation;
- typed internal representation;
- validation result record format.

Do not compare renderers, browsers, dashboards, templates, visualization libraries, map frameworks, APIs, or portals in that investigation unless the representation decision directly depends on them.

## 16. Final decision

The minimal BriefForge implementation architecture should be contract-first, validation-first, file/local-first, and downstream-boundary-aware.

BriefForge-specific implementation should be limited to:

1. Presentation Package record contract.
2. Presentation obligation model.
3. Upstream reference model.
4. Minimal composition semantics representation.
5. Presentation-local validator.
6. Validation result record.
7. Downstream consumer boundary rules.

Everything else should be adopted only as external mature downstream capability later, or rejected from BriefForge core.

This preserves the frozen constitution while minimizing custom infrastructure.
