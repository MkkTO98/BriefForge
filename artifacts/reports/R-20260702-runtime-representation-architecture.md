# Report: BriefForge Runtime Representation Architecture

Date: 2026-07-02
Type: implementation-phase architectural investigation
Status: Final
Owner: BriefForge
Scope: runtime representation architecture, independent of language, serialization, storage, renderer, browser, API, database, or framework

## 1. Executive conclusion

The canonical Presentation Package should exist during execution as a bounded semantic runtime object that is inspectable, validated, and then made available to downstream consumers without becoming a rendered artifact, browser state, template instance, visualization specification, database record, API resource, or programming-language object model.

The minimal runtime representation is:

```text
Candidate Presentation Package
-> Validation Judgment
-> Ready Presentation Package
-> Downstream Consumption Boundary
```

No separate composition stage is required in the minimal runtime lifecycle.

Composition is not a later transformation step. Composition is part of the package's semantic substance and is validated as part of package readiness.

The runtime should distinguish three states only:

1. Candidate package: a package-shaped semantic object not yet accepted.
2. Rejected package: a candidate with a validation result that prevents acceptance.
3. Ready package: a validated semantic object safe for downstream consumption.

This keeps BriefForge independent of programming language, serialization format, database, renderer, browser, API, and framework choices while preserving the frozen constitution.

## 2. Governing baseline

This investigation does not reopen the frozen constitution.

BriefForge owns exactly:

1. Presentation Contract.
2. Composition Semantics.
3. Presentation Validation Obligations.

The canonical object is the structured semantic Presentation Package.

A Presentation Package requires:

1. Package identity.
2. Organizing Purpose.
3. Organized presentation statements with target-independent encounter semantics.
4. Upstream-owned references where dependency exists.
5. Presentation obligations.

BriefForge owns presentation meaning only.

It references economic and analytical meaning owned elsewhere.

It excludes delivery meaning.

The previous implementation architecture extraction concluded that BriefForge's minimal architecture is contract-first, validation-first, and downstream-boundary-aware. This report narrows that conclusion to runtime meaning only.

## 3. Runtime representation principle

Runtime representation means: how a constitutional concept exists while BriefForge is executing.

It does not mean:

- a programming-language class;
- a schema;
- a serialization format;
- a file format;
- a database row;
- an API resource;
- a browser model;
- a rendered document;
- a template instance;
- a visualization specification.

Runtime concepts must be:

1. Semantically inspectable.
2. Validation-addressable.
3. Boundary-preserving.
4. Target-independent.
5. Downstream-consumable without downstream authority.

## 4. MetaHarvest runtime consultation

Existing MetaHarvest evidence was consulted for immutable runtime contracts, validation models, contract-driven architectures, runtime record models, and specification/runtime separation.

Relevant evidence:

| Evidence source | Runtime pattern observed | BriefForge use | Boundary caution |
|---|---|---|---|
| `explicit-architectural-contract` primitive | Producers and consumers communicate through named contracts rather than implicit conventions | Adopt as runtime boundary discipline | Contract must not become framework/API ownership |
| `portable-record-contract` pattern | Meaningful state or observation survives beyond hidden control flow as inspectable record | Adopt for Presentation Package runtime identity | Do not over-formalize into platform/storage machinery |
| `durable-event-or-record-history` primitive | Runtime progress or observation can be retained as records where audit/recovery matters | Adapt only for validation result and package readiness | Do not create event sourcing or workflow history |
| `staged-execution-pipeline` primitive | Complex execution benefits from explicit stages | Adapt minimally as Candidate -> Validation -> Ready -> Consumer | Avoid unnecessary orchestration stages |
| `stage-boundaries-enable-substitution` invariant | Boundaries make substitution and validation easier | Adopt for downstream consumer boundary | Do not create plugin/runtime framework prematurely |
| Great Expectations validation definition | Validation binds subject and expectation contract | Adapt conceptually for package validation | Do not adopt data-quality framework or validate data truth |
| Great Expectations expectation suite | Grouped expectations are reusable validation contracts | Adapt as obligation-checking concept | Do not import dataset/domain validation semantics |
| dbt manifest lineage | Definitions, lineage, metadata, and validation are statically inspectable before runtime orchestration | Adapt inspectability principle | Do not adopt transformation compiler/template system |
| Kubernetes versioned API object contract | Stable portable records separate identity, desired state, observed status, and version/generation metadata | Adapt identity/status separation conceptually | Do not adopt control-plane/reconciliation model |
| OpenLineage run/job/dataset model | Stable identities represent lineage independently of tool-specific execution records | Adapt reference-stability concept | Do not adopt lineage backend/event standard as core |
| Terraform state snapshot | Runtime state can be snapshotted with lineage/serial metadata when state management matters | Adapt only if later package state history is needed | Do not create state manager/storage backend now |
| Polars portable plan serialization | Runtime plans may require version/hash gates before reuse | Adapt compatibility-gate idea only | Do not adopt plan serialization or query runtime |
| Vega-Lite compiler/runtime boundary | Declarative specification is separate from rendering runtime | Adopt spec/runtime separation as downstream boundary | Do not make visual encoding canonical |

MetaHarvest convergence:

Mature systems converge on five runtime lessons:

1. Runtime meaning should cross boundaries through explicit contracts.
2. Accepted runtime records should be inspectable and not hidden in process control flow.
3. Validation should produce an explicit judgment separate from the subject being validated.
4. Specification/runtime/rendering boundaries prevent downstream systems from becoming semantic authority.
5. Over-staging and wholesale platform adoption are recurring risks when a simple local contract is enough.

BriefForge should adopt these lessons as architectural discipline, not as product dependencies.

## 5. Runtime concept model

### 5.1 Presentation Package

Runtime purpose:

The Presentation Package is the bounded semantic object under evaluation or consumption. It carries the package's identity, organizing purpose, organized presentation statements, upstream references, and presentation obligations as one coherent presentation object.

Runtime lifetime:

- Begins when package-shaped semantic content is introduced into BriefForge execution.
- Exists first as a Candidate Presentation Package.
- Becomes a Ready Presentation Package only after validation accepts it.
- May be handed to downstream consumers only in Ready form.
- Does not become obsolete merely because a downstream representation is produced.

Ownership:

BriefForge owns the package's presentation meaning and validation state.

BriefForge does not own upstream economic/analytical meaning referenced by the package.

BriefForge does not own downstream rendered or delivered representations.

Mutability:

- Candidate packages may be corrected before acceptance.
- Ready packages are semantically stable for the validation judgment that accepted them.
- Any semantic change after readiness creates a new candidate validation event, not an in-place mutation of the accepted ready package.

Interaction with other runtime concepts:

- Contains Package Identity and Organizing Purpose.
- Contains or binds organized presentation statements.
- References upstream-owned material where dependency exists.
- Carries or attaches presentation obligations.
- Is evaluated by validation.
- Is exposed to downstream consumers only through the downstream consumption boundary.

Validation boundary:

Validation determines whether the package satisfies BriefForge's presentation-local contract. It does not determine whether upstream facts or analysis are true.

### 5.2 Package Identity

Runtime purpose:

Package Identity distinguishes this package from other packages and defines its bounded self-description: what it is, why it exists as a presentation object, what scope it claims, and what it explicitly does not claim.

Runtime lifetime:

- Present from candidate creation.
- Must remain stable across validation.
- Must remain visible to downstream consumers as presentation self-description.

Ownership:

BriefForge owns the package-level self-identification as presentation meaning.

It does not own portal identity, route identity, search identity, user-session identity, or registry identity.

Mutability:

- Candidate identity may be revised before readiness.
- Ready identity must not change without revalidation.

Interaction with other runtime concepts:

- Binds Organizing Purpose and statements into one package object.
- Gives validation an identity target for diagnostics.
- Gives downstream consumers a self-description without giving them routing authority.

Validation boundary:

Validation checks that identity is present, bounded, internally consistent, and not pretending to be portal/search/routing/session metadata.

### 5.3 Organizing Purpose

Runtime purpose:

Organizing Purpose is the runtime reason that binds statements into one package. It explains why the package exists as a bounded presentation object without making upstream analytical claims.

Runtime lifetime:

- Present from candidate creation.
- Used during validation to evaluate statement membership and package coherence.
- Preserved in Ready Package form for downstream interpretation.

Ownership:

BriefForge owns the presentation-local organizing purpose.

It does not own economic thesis, analytical conclusion, investment recommendation, audience personalization goal, delivery strategy, or portal intent.

Mutability:

- Candidate purpose may be revised before readiness.
- Ready purpose must not change without revalidation because it changes statement membership meaning.

Interaction with other runtime concepts:

- Interprets why each presentation statement belongs.
- Constrains composition validity.
- Helps detect scope creep or analytical overreach.

Validation boundary:

Validation checks that Organizing Purpose is presentation-local, bounded, and compatible with the package's statements and non-scope. It must not validate whether the purpose is analytically wise or persuasive.

### 5.4 Organized Presentation Statements

Runtime purpose:

Organized Presentation Statements are the runtime units of BriefForge-owned presentation meaning. Each statement says what should be encountered, why it belongs to the Organizing Purpose, how it relates to other statements when relevant, and which references/obligations remain attached.

Runtime lifetime:

- Present in candidate form before validation.
- Become ready only as part of an accepted package.
- Cannot be validly consumed apart from required references and obligations.

Ownership:

BriefForge owns presentation meaning and target-independent encounter organization.

BriefForge does not own economic meaning, analytical truth, renderer layout, visual encoding, user interaction, or portal navigation.

Mutability:

- Candidate statements may be revised before readiness.
- Ready statements are stable for the accepted package.
- Reordering, regrouping, relation changes, or statement edits after readiness require revalidation when they affect encounter semantics.

Interaction with other runtime concepts:

- Belong to the Organizing Purpose.
- May be ordered, partially ordered, related, grouped, hierarchical, or navigably connected where constitutionally needed.
- May depend on upstream references.
- Must carry relevant obligations.

Validation boundary:

Validation checks membership, internal consistency, encounter-semantics validity, reference attachment, obligation attachment, and boundary compliance.

Validation must not treat statements as UI components, template blocks, visual marks, dashboard panels, graph database nodes, map layers, or HTML sections.

### 5.5 Upstream References

Runtime purpose:

Upstream References preserve the connection between presentation statements and material owned elsewhere. They prevent BriefForge from silently absorbing economic, analytical, evidential, definitional, caveat, confidence, freshness, or provenance meaning.

Runtime lifetime:

- Exist wherever a statement depends on upstream-owned material.
- Must exist before a dependent statement can be accepted as ready.
- Must remain attached for downstream consumption.

Ownership:

The upstream owner owns the referenced meaning.

BriefForge owns only the fact that the package depends on that upstream-owned material and the obligation to preserve that ownership visibly.

Mutability:

- Candidate references may be corrected before readiness.
- Ready references cannot be removed, weakened, or redirected without revalidation.
- If upstream ownership or referenced material changes materially, affected package readiness must be reconsidered.

Interaction with other runtime concepts:

- Attach to statements or package-level dependencies where needed.
- Trigger presentation obligations.
- Inform validation diagnostics.
- Constrain downstream consumers through non-detachment obligations.

Validation boundary:

Validation checks that references exist where dependency exists, are internally consistent, preserve ownership, and carry required obligations.

Validation does not dereference, fetch, ingest, canonicalize, verify, transform, or judge upstream content unless a later architecture explicitly and narrowly authorizes reference existence checks without semantic ownership.

### 5.6 Presentation Obligations

Runtime purpose:

Presentation Obligations are runtime constraints that prevent presentation from hiding, weakening, detaching, overstating, or transforming upstream-owned meaning.

Obligation categories are:

1. Ownership visibility.
2. Evidence/provenance visibility.
3. Caveat/scope visibility.
4. Confidence/uncertainty visibility.
5. Freshness/review-state visibility.
6. Non-transformation.
7. Non-detachment.

Runtime lifetime:

- Exist whenever package content creates a risk of hiding, weakening, detaching, overstating, or transforming upstream-owned meaning.
- Must be present before package readiness.
- Must remain active through downstream consumption.

Ownership:

BriefForge owns the presentation obligation as a contract requirement.

Upstream systems own the underlying evidence, caveat, confidence, freshness, and provenance meaning.

Downstream consumers must preserve the obligation but do not own it.

Mutability:

- Candidate obligations may be corrected before readiness.
- Ready obligations are not optional display hints and cannot be removed without revalidation.
- Obligations may be strengthened without constitutional conflict, but weakening or detachment requires rejection or revalidation.

Interaction with other runtime concepts:

- Bind to upstream references, statements, or package-level dependencies.
- Form the core of validation judgment.
- Constrain downstream consumers.

Validation boundary:

Validation checks obligation presence, attachment, internal consistency, and preservation requirements.

It does not decide upstream confidence, caveat correctness, evidence quality, analytical quality, or freshness truth.

### 5.7 Validation Result

Runtime purpose:

Validation Result is the explicit runtime judgment about whether a Candidate Presentation Package satisfies BriefForge's presentation-local contract.

It separates validation outcome from the package itself.

Runtime lifetime:

- Created by validation.
- Exists at least long enough to justify acceptance or rejection.
- For a Ready Package, the acceptance result should remain associated with the package's readiness claim.

Ownership:

BriefForge owns the validation judgment.

It does not own upstream truth or downstream rendering quality.

Mutability:

- A validation result is stable as a record of a specific validation judgment.
- New package content or changed validation rules create a new validation judgment rather than mutating the meaning of the prior one.

Interaction with other runtime concepts:

- References the candidate package evaluated.
- Identifies accepted/rejected status.
- Explains validation failures or warnings.
- Authorizes transition from Candidate Package to Ready Package only when accepted.

Validation boundary:

Validation Result must be limited to presentation-local validation: structure, references, obligations, composition, internal consistency, and boundary compliance.

It must not contain economic truth judgments, analytical correctness judgments, renderer-quality judgments, browser-quality judgments, or portal-quality judgments.

## 6. Minimal runtime lifecycle

### 6.1 Candidate lifecycle considered

A tempting lifecycle is:

```text
Input
-> Validation
-> Composition
-> Ready Presentation Package
-> Downstream Consumer
```

This is too complex.

It incorrectly implies that composition happens after validation or as a separate assembly phase. In the frozen constitution, Composition Semantics are part of the package's semantic substance. A package is not ready until its organization is already present and validated.

### 6.2 Minimal lifecycle selected

The minimal lifecycle is:

```text
Candidate Presentation Package
-> Validation Judgment
-> Ready Presentation Package or Rejected Package
-> Downstream Consumption Boundary
```

Expanded conceptually:

1. Candidate Presentation Package exists.
   - It contains identity, purpose, statements, encounter semantics, references, and obligations.
   - It is not yet acceptable for downstream consumption.

2. Validation Judgment evaluates the candidate.
   - It checks presentation-local contract satisfaction.
   - It produces an acceptance or rejection result.

3. Ready Presentation Package exists only if validation accepts the candidate.
   - It is semantically stable relative to that validation judgment.
   - It may be consumed downstream.

4. Downstream Consumption Boundary receives the Ready Package.
   - It may produce rendered/exported/displayed representations elsewhere.
   - It must not become semantic authority.

### 6.3 Stages deliberately removed

Removed: separate Input stage.

Reason:

Input mechanism is technology-specific. Runtime architecture only needs the concept of a Candidate Presentation Package.

Removed: separate Composition stage.

Reason:

Composition is part of candidate package substance and validation, not a later runtime phase.

Removed: separate Serialization/Persistence stage.

Reason:

Serialization and persistence are implementation choices, not runtime constitutional concepts.

Removed: separate Rendering/Export stage.

Reason:

Rendering/export is downstream and excluded from BriefForge ownership.

Removed: separate Portal/Discovery stage.

Reason:

Portal/search/navigation is excluded from BriefForge ownership.

## 7. Runtime invariants

Only invariants justified by the frozen constitution are retained.

### 7.1 Package boundedness invariant

A runtime package must remain one bounded presentation object with declared scope and non-scope.

Violation examples:

- Package expands into ecosystem registry.
- Package becomes a portal route collection.
- Package accumulates unrelated statements without organizing purpose.

### 7.2 Identity stability invariant

A Ready Presentation Package's identity must remain stable for the validation judgment that accepted it.

Changing identity changes what was validated.

### 7.3 Organizing Purpose coherence invariant

Every ready statement must belong to the package's Organizing Purpose.

The purpose may not be replaced by analytical thesis, investment recommendation, audience personalization, or delivery strategy.

### 7.4 Statement attachment invariant

A presentation statement that depends on upstream material must remain attached to required upstream references and obligations.

A statement separated from required references or obligations is not valid for downstream consumption.

### 7.5 Reference consistency invariant

A runtime upstream reference must preserve upstream ownership of the referenced meaning.

It must not silently convert referenced meaning into BriefForge-owned meaning.

### 7.6 Obligation satisfaction invariant

Required presentation obligations must be present, attached, and non-detached for a Ready Package.

Obligations are correctness constraints, not display suggestions.

### 7.7 Composition validity invariant

Target-independent encounter semantics must remain valid and internally consistent.

Composition must not become layout, template hierarchy, dashboard panel structure, visual grammar, map layer stack, browser navigation, or portal route graph.

### 7.8 Validation-before-consumption invariant

Only Ready Presentation Packages may cross the downstream consumption boundary.

Candidates and rejected packages may be inspected or corrected but not treated as consumable presentation packages.

### 7.9 Downstream non-authority invariant

A downstream consumer may transform a Ready Package into another representation only if the Ready Package remains the semantic authority.

Rendered/exported/browser/portal artifacts are not canonical.

### 7.10 Boundary-negative invariant

Runtime representation must not create ownership of:

- data ingestion;
- canonicalization;
- upstream truth;
- analytical conclusions;
- rendering;
- browser behavior;
- visualization grammar;
- map rendering;
- templates;
- API resources;
- search/ranking;
- portal navigation;
- workflow orchestration.

## 8. Runtime interaction model

The runtime interaction model is minimal and directional.

```text
Package Identity
  constrains and identifies
    Presentation Package

Organizing Purpose
  binds
    Presentation Statements

Presentation Statements
  are organized by
    Target-Independent Encounter Semantics

Presentation Statements
  depend on, where needed
    Upstream References

Upstream References
  trigger and carry
    Presentation Obligations

Presentation Obligations
  constrain
    Statements, References, Package, and Downstream Consumers

Validation Judgment
  evaluates
    Candidate Presentation Package

Accepted Validation Judgment
  authorizes
    Ready Presentation Package

Ready Presentation Package
  crosses
    Downstream Consumption Boundary
```

Key interaction rules:

1. Identity does not route.
2. Purpose does not analyze.
3. Statements do not own upstream truth.
4. References do not ingest.
5. Obligations do not specify layout.
6. Validation does not judge truth.
7. Downstream consumption does not create canonical meaning.

## 9. Runtime mutability model

### 9.1 Candidate Package mutability

Candidate packages are mutable in the sense that they may be corrected before acceptance.

Permitted candidate changes:

- clarify identity;
- narrow scope/non-scope;
- revise organizing purpose;
- revise statement membership;
- correct encounter semantics;
- add missing references;
- attach missing obligations;
- remove boundary-violating delivery concepts.

### 9.2 Ready Package mutability

Ready packages are semantically immutable relative to the validation judgment that accepted them.

A change to identity, purpose, statements, references, obligations, or encounter semantics produces a new candidate requiring validation.

This does not require any particular storage or copy mechanism. It is a runtime meaning rule, not a data-structure rule.

### 9.3 Validation Result mutability

A validation result records a judgment.

It is not edited to make an invalid package valid. A revised package receives a new judgment.

### 9.4 Downstream consumer mutability

Downstream consumers may derive target-specific representations, but those derived representations do not mutate the Ready Package's semantic authority.

## 10. Boundary verification

### 10.1 Rendering ownership

The runtime model does not include a renderer concept.

Downstream consumers may later render, but rendering is outside BriefForge runtime ownership. The Ready Package remains semantic authority.

### 10.2 Browser ownership

The runtime model has no browser state, session, route, interaction state, DOM model, client/server state, or user-state concept.

Any browser consumer is downstream.

### 10.3 Visualization ownership

The runtime model has no visual marks, encodings, scales, facets, chart series, dashboard panels, or interaction dispatch.

Visualization systems may consume Ready Packages later, but their visual specifications are not canonical Presentation Packages.

### 10.4 Template ownership

The runtime model has no templates, slots, components, blocks, sections, or reusable UI primitives.

Composition semantics are target-independent encounter semantics, not template structure.

### 10.5 Portal ownership

Package Identity supports self-description only.

It does not become routing, navigation, ranking, personalization, registry entry, reading queue, or portal metadata.

### 10.6 Analysis ownership

Organizing Purpose and statements do not create economic claims, analytical conclusions, confidence judgments, or investment recommendations.

Upstream references preserve ownership elsewhere.

Validation checks presentation-local integrity, not truth.

### 10.7 Data ownership

The runtime model does not fetch, ingest, canonicalize, store, transform, or refresh upstream data.

References point to upstream-owned material; obligations preserve visibility of upstream ownership and caveats.

## 11. Runtime comparison against mature systems

| Mature-system pattern | Runtime lesson | BriefForge adoption | Rejected implication |
|---|---|---|---|
| Kubernetes versioned API object | Runtime objects benefit from stable identity/status distinction | Ready vs Candidate/Rejected distinction | No control plane, resource reconciliation, API server, or database |
| Great Expectations validation definition | Validation binds a subject to reusable checks and produces explicit outcome | Validation Judgment separate from Candidate Package | No data-quality framework or data truth validation |
| dbt manifest lineage | Runtime execution benefits when semantic definitions are inspectable before orchestration | Package semantics must be inspectable before downstream consumption | No transformation compiler or template engine |
| OpenLineage identity model | Stable identities preserve meaning across tool boundaries | Upstream references must preserve ownership across boundaries | No lineage backend/event transport adoption |
| Terraform state snapshot | Accepted runtime state should not be confused with desired changes | Ready Package stability relative to validation judgment | No state manager, lock manager, remote backend, or apply engine |
| Polars portable plan | Runtime plans need compatibility gates when moved across contexts | Future compatibility checks may protect package readiness | No query plan/runtime or serialization format chosen |
| Vega-Lite compiler/runtime boundary | Specification and rendering runtime must be separated | Ready Package is not rendered output | No visual encoding grammar as package core |
| Grafana dashboard composition | Dashboard composition is powerful but delivery-specific | Use as caution against UI composition leakage | No dashboard panel runtime |
| OpenMetadata/Backstage catalog models | Entity self-description and ownership matter | Package identity may self-describe | No catalog, portal, search, routing, or scaffolder ownership |

## 12. Runtime architecture decision

The canonical Presentation Package should exist during execution as a semantically stable, validation-addressable package object whose readiness is determined by a separate validation judgment.

The runtime architecture is:

```text
Candidate Package
  contains constitutional substance
  may be corrected
  cannot be consumed downstream as ready

Validation Judgment
  evaluates presentation-local correctness
  accepts or rejects
  does not judge upstream truth or downstream quality

Ready Package
  accepted semantic authority
  stable relative to its validation judgment
  available to downstream consumers

Downstream Consumption Boundary
  allows later rendering/export/display elsewhere
  preserves obligations
  cannot redefine package meaning
```

This architecture is independent of programming language, serialization, database, API, renderer, browser, and framework choices.

## 13. Open questions deferred

These questions are intentionally not answered here because they belong to later representation-selection or implementation investigations:

1. Which concrete serialization format, if any, should persist package records?
2. Which programming language should represent packages internally?
3. Whether validation should be schema-based, rule-based, or hybrid.
4. How compatibility/versioning should be encoded concretely.
5. Whether validation results should be persisted as files, logs, records, or only emitted locally.
6. Whether downstream consumers need a formal adapter protocol.
7. Which renderer, if any, should be selected later.
8. Whether example packages should be authored before or during implementation.

## 14. Recommendation for next architecture-only investigation

If another architecture-only step is desired before implementation, investigate runtime acceptance semantics:

Question:

What exact conditions distinguish a Candidate Presentation Package, a Rejected Package, and a Ready Presentation Package, without choosing schemas, programming languages, or serialization formats?

That investigation should define acceptance/rejection criteria and diagnostic categories only.

It should still avoid implementation tasks, code, schemas, APIs, renderers, browsers, templates, and serialization choices.

## 15. Final decision

BriefForge's minimal runtime representation is:

1. Candidate Presentation Package.
2. Validation Judgment.
3. Ready Presentation Package or Rejected Package.
4. Downstream Consumption Boundary.

The runtime substance of the Presentation Package consists of:

1. Package Identity.
2. Organizing Purpose.
3. Organized Presentation Statements.
4. Upstream References.
5. Presentation Obligations.

The runtime architecture preserves the frozen constitution by keeping presentation meaning canonical, validation presentation-local, and all rendering/browser/visualization/template/portal/analysis responsibilities outside BriefForge runtime ownership.
