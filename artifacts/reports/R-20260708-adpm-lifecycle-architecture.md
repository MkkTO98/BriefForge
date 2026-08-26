# ADPM Lifecycle Architecture

Date: 2026-07-08
Status: architecture-only lifecycle definition
Scope: TASK-037 — Architectural Decision Package Model lifecycle, ownership, and integration

## Executive conclusion

ADPM should not be treated as a file format, renderer input, schema artifact, or runtime object first.

ADPM is a constitutional semantic object that moves through a governed lifecycle:

```text
Investigation Evidence
-> Decision Need Identification
-> Package Construction
-> Semantic Review
-> Architectural Approval
-> Constitutional Freeze
-> Consumption Boundary
-> Publication Expression
-> Operational Reference
-> Archival / Supersession
```

The key architectural rule is that ADPM semantics become authoritative before any renderer, serializer, validator, builder, indexer, or publication system consumes them. Later components may transport, check, display, index, or reference ADPM, but they may not redefine its semantics.

TASK-037 therefore establishes:

1. the complete lifecycle of an Architectural Decision Package;
2. ownership and transition boundaries;
3. lifecycle states distinct from recommendation disposition;
4. lineage relationships;
5. permanent invariants;
6. future capability placement;
7. readiness for serialization/schema/validator/builder planning.

No implementation is authorized or produced by this report.

## Problem statement

TASK-035 defined ADPM semantics. TASK-036 adversarially validated and refined them. The remaining architectural risk was surrounding lifecycle ambiguity.

Without a lifecycle model, downstream implementation could create several failure modes:

- package builders start making governance decisions;
- validators infer recommendations rather than checking completeness;
- renderers shape semantic fields by display convenience;
- schemas freeze transport choices instead of semantic invariants;
- packages mutate after publication without traceable lineage;
- archival, supersession, and deprecation become ad hoc;
- consumer projects confuse BriefForge recommendation packaging with adoption authority.

This task resolves those risks before serialization or implementation planning begins.

## Design goals

The lifecycle must be:

1. Semantic-first — the package is defined by meaning, not format.
2. Renderer-independent — renderers consume but never shape ADPM.
3. Implementation-independent — lifecycle stages do not assume code, storage, APIs, JSON, YAML, schemas, or databases.
4. Authority-preserving — upstream evidence ownership and downstream adoption sovereignty remain intact.
5. Immutable at freeze — frozen packages do not mutate; later changes create lineage.
6. Auditable — every transition has owner, reason, and evidence.
7. Minimal — only lifecycle stages needed for decision support are canonical.
8. Future-compatible — later serializers, validators, builders, renderers, search, and indexing can attach without redesigning lifecycle.

## Rejected lifecycle designs

### Rejected: renderer-led lifecycle

```text
Investigation -> renderer template -> published report -> extracted decisions
```

Rejected because it makes display shape determine semantics. This recreates the bottleneck ADPM exists to remove.

### Rejected: validator-led lifecycle

```text
Raw package -> validator accepts/rejects -> canonical package
```

Rejected because validators should check completeness and invariants, not create authority. Architectural approval must remain a governance action.

### Rejected: schema-led lifecycle

```text
Schema definition -> serialized package -> downstream use
```

Rejected for this task because serialization format is not yet authorized and should not become the architectural source of truth.

### Rejected: report-as-package lifecycle

```text
Investigation report -> ADPM summary section -> publication
```

Rejected because a prose report can contain an ADPM expression, but the canonical package is semantic. Reports are evidence/provenance sources or publication expressions, not the lifecycle authority.

### Rejected: no formal lifecycle

Rejected because TASK-036 showed that authority, boundary constraints, versioning, status, and priority are essential. Those semantics require lifecycle governance to prevent drift.

## Accepted lifecycle overview

The accepted lifecycle has ten stages:

1. Investigation Evidence
2. Decision Need Identification
3. Package Construction
4. Semantic Review
5. Architectural Approval
6. Constitutional Freeze
7. Consumption Boundary
8. Publication Expression
9. Operational Reference
10. Archival / Supersession

These are architectural stages, not necessarily software modules.

## Stage 1 — Investigation Evidence

Purpose:
- collect or identify source material that may support architectural decisions.

Inputs:
- reports;
- decisions;
- implementation lessons;
- architecture reviews;
- operational readiness evidence;
- validation output;
- comparative investigations;
- source provenance.

Outputs:
- evidence corpus;
- candidate decision pressure;
- provenance references.

Invariants:
- evidence ownership remains with source-producing projects or artifacts;
- BriefForge does not rewrite source truth;
- absence or weakness of evidence must remain representable.

Ownership:
- source-producing project owns evidence correctness;
- BriefForge owns later packaging semantics only.

Transition condition:
- decision pressure is identifiable: a reader would benefit from decision-ready packaging rather than reading the whole corpus first.

## Stage 2 — Decision Need Identification

Purpose:
- determine whether the evidence corpus implies one or more bounded architectural decision questions.

Inputs:
- evidence corpus;
- known reader/adopter decision problem;
- architecture/governance boundaries.

Outputs:
- candidate primary DecisionQuestion;
- candidate coupled DecisionQuestions;
- preliminary scope and non-scope;
- preliminary authority/boundary questions.

Invariants:
- broad research topics are not sufficient;
- every package must be decision-oriented;
- if no decision question exists, no ADPM package should be constructed.

Ownership:
- BriefForge decision-support architecture owns identification of package-worthiness;
- downstream projects retain adoption authority.

Transition condition:
- at least one bounded DecisionQuestion can be stated with affected scope and why-now.

## Stage 3 — Package Construction

Purpose:
- assemble ADPM semantic objects from evidence into a candidate package.

Inputs:
- DecisionQuestion(s);
- source provenance;
- evidence references;
- candidate recommendations;
- confidence/uncertainty/assumption/risk/alternative/consequence/dependency/impact/follow-up/open-question information;
- authority and boundary constraints.

Outputs:
- Draft ADPM package.

Invariants:
- construction creates candidate semantics, not approval;
- recommendations do not become tasks;
- missing evidence must be explicit rather than silently omitted;
- renderer considerations must not influence object structure.

Ownership:
- future ADPM Package Builder or human package author may construct;
- BriefForge owns construction rules;
- builder/author does not own approval.

Transition condition:
- package contains required objects and can be reviewed for semantic completeness.

## Stage 4 — Semantic Review

Purpose:
- evaluate whether the package is complete, coherent, traceable, and internally non-contradictory.

Inputs:
- Draft package;
- canonical ADPM specification;
- source provenance.

Outputs:
- Reviewed package;
- review findings;
- required corrections or rejection rationale.

Invariants:
- review checks semantics, not presentation quality;
- review may identify incompleteness but must not invent evidence;
- validators, if later implemented, support review but do not replace architectural judgment.

Ownership:
- BriefForge semantic validation/review function owns semantic review;
- source owners own corrections to source evidence;
- package author owns candidate correction.

Transition condition:
- package is semantically complete enough for architectural approval, or explicitly rejected/deferred.

## Stage 5 — Architectural Approval

Purpose:
- decide whether the reviewed package is accepted as a valid architectural decision-support package.

Inputs:
- Reviewed package;
- semantic review findings;
- decision authority records;
- boundary constraints.

Outputs:
- Approved package, rejected package, or returned-for-revision package;
- approval rationale.

Invariants:
- approval validates package fitness, not downstream implementation adoption;
- BriefForge approval does not override consumer-project authority;
- approval must preserve non-authorizations and boundary constraints.

Ownership:
- BriefForge constitutional/governance owner approves the package as ADPM-valid;
- external project owners approve their own adoption decisions separately.

Transition condition:
- approval status is explicit and traceable.

## Stage 6 — Constitutional Freeze

Purpose:
- make an approved package immutable as a canonical decision-support artifact.

Inputs:
- Approved package;
- approval record;
- package identity/version.

Outputs:
- Frozen ADPM package.

Invariants:
- frozen packages are immutable;
- corrections after freeze require supersession, amendment package, or erratum lineage rather than in-place semantic mutation;
- package lineage must remain traceable;
- package status is distinct from recommendation disposition.

Ownership:
- BriefForge constitutional governance owns freeze decision;
- archival system may preserve frozen package but does not modify it.

Transition condition:
- package is approved and freeze rationale is recorded.

## Stage 7 — Consumption Boundary

Purpose:
- allow downstream capabilities to consume the frozen package without semantic authority leakage.

Inputs:
- Frozen package;
- canonical ADPM specification;
- package status and version.

Outputs:
- read-only consumption by serializers, validators, renderers, comparison engines, search/indexing, or consumers.

Invariants:
- consuming components receive read authority only unless explicitly assigned construction/review roles before freeze;
- renderers never modify semantics;
- serializers transport semantics and do not define them;
- comparison/search/indexing derive views and do not alter canonical packages.

Ownership:
- consuming component owns its own output;
- BriefForge ADPM governance retains semantic authority.

Transition condition:
- package is frozen or explicitly marked as non-frozen for internal review consumption.

## Stage 8 — Publication Expression

Purpose:
- express package meaning through one or more publication outputs.

Inputs:
- Frozen package;
- renderer or publication capability;
- target output constraints.

Outputs:
- published report, HTML, PDF, markdown, index entry, comparison view, or other future expression.

Invariants:
- published outputs are non-canonical expressions;
- publication may omit or summarize for audience but must not contradict canonical semantics;
- conformance can check linkage back to frozen package.

Ownership:
- renderer/publication layer owns output expression;
- ADPM governance owns semantic source;
- readers/consumer projects own adoption decisions.

Transition condition:
- publication output references package identity and version/lineage.

## Stage 9 — Operational Reference

Purpose:
- allow packages to be used for planning, comparison, search, indexing, backlog discussion, and adoption review.

Inputs:
- Frozen package;
- publication outputs;
- package metadata and relationships.

Outputs:
- references in backlog, decisions, adoption reviews, search indexes, comparison matrices, or future aggregate views.

Invariants:
- operational reference does not mutate package content;
- derived views must identify the package(s) they derive from;
- adoption by a consumer project creates separate consumer-owned decisions/tasks.

Ownership:
- each referencing component owns its reference or derived view;
- package lineage remains under ADPM governance.

Transition condition:
- package remains current, is superseded, deprecated, rejected, or archived.

## Stage 10 — Archival / Supersession

Purpose:
- preserve long-term traceability and manage package lifecycle after newer evidence, better packages, or changed architecture.

Inputs:
- Frozen package;
- superseding package or archival reason;
- lineage relationship.

Outputs:
- archived package;
- supersession/deprecation record;
- lineage links.

Invariants:
- archives are immutable;
- supersession does not delete historical packages;
- consumers can reconstruct what recommendation was available at the time;
- supersession changes package status, not historical content.

Ownership:
- BriefForge archival/governance owner records archival/supersession;
- storage mechanism is implementation detail.

Transition condition:
- package is no longer current, has been superseded, or is retained for long-term record.

## Lifecycle states

ADPM requires formal lifecycle states because package status drives permission, immutability, consumption, and archival treatment.

Accepted states:

1. `draft`
2. `under_review`
3. `approved`
4. `frozen`
5. `deprecated`
6. `superseded`
7. `archived`
8. `rejected`

These states refine but do not replace the TASK-036 `package_status` values. The specification should clarify them.

### State meanings

`draft`:
- package is being constructed;
- semantics may change;
- not authoritative.

`under_review`:
- package is undergoing semantic completeness/coherence review;
- semantics may change only through review correction.

`approved`:
- package is accepted as ADPM-valid but not yet immutable;
- brief holding state before freeze.

`frozen`:
- canonical immutable package;
- safe for downstream consumption.

`deprecated`:
- still historically valid but no longer recommended as current guidance;
- may or may not be superseded by a replacement.

`superseded`:
- replaced by one or more later packages;
- historical package remains traceable.

`archived`:
- retained for long-term record;
- no longer active guidance.

`rejected`:
- package candidate failed approval or was determined not to be package-worthy;
- retained only if rejection rationale has governance value.

### Required transitions

Allowed normal transitions:

```text
draft -> under_review
under_review -> draft
under_review -> approved
under_review -> rejected
approved -> frozen
frozen -> deprecated
frozen -> superseded
frozen -> archived
deprecated -> archived
superseded -> archived
rejected -> archived
```

Allowed exceptional transition:

```text
frozen -> frozen_erratum_package
```

This is not in-place mutation. It means a separate erratum/amendment package records correction while the original remains traceable.

### Prohibited transitions

Prohibited:

```text
frozen -> draft
frozen -> under_review
frozen -> approved
superseded -> draft
archived -> draft
archived -> frozen
rejected -> frozen
```

Rationale:
- immutable packages must not be silently reopened;
- rejected packages must not become canonical without reconstruction and review;
- archives are historical records.

## Lifecycle state versus recommendation disposition

Lifecycle state describes the package's governance status.

Recommendation disposition describes the recommendation's architectural advice.

Examples:
- a `frozen` package may contain a `reject` recommendation;
- a `draft` package may contain an `adopt` recommendation, but it is not authoritative;
- a `superseded` package may contain historically important recommendations that are no longer current;
- an `archived` package does not imply all contained recommendations were rejected.

This distinction is mandatory.

## Package relationships

ADPM should support a small set of package relationships. These are needed for lineage, traceability, and derived views.

Accepted relationships:

- `supersedes`
- `superseded_by`
- `references`
- `derives_from`
- `amends`
- `amended_by`
- `related_to`

Deferred relationships:

- `merged_from`
- `split_into`
- `extends`

Rationale:
- `merged_from` and `split_into` may be useful later but add complexity before real multi-package operations exist;
- `extends` is ambiguous between lineage, scope expansion, and derived view.

### Relationship semantics

`supersedes` / `superseded_by`:
- replacement relationship between packages.

`references`:
- package cites another package without replacing it.

`derives_from`:
- package was built from earlier package evidence/structure but is not a replacement.

`amends` / `amended_by`:
- separate correction or clarification package.

`related_to`:
- weak association used sparingly when no stronger relationship applies.

## Architectural invariants

Permanent lifecycle invariants:

1. ADPM is semantic authority; renderers are expression mechanisms.
2. Renderers never modify ADPM semantics.
3. Serializers transport semantics but do not define them.
4. Validators check conformance/completeness but do not infer recommendations.
5. Builders may construct candidate packages but do not approve or freeze them.
6. Frozen packages are immutable.
7. Post-freeze corrections require lineage, not in-place mutation.
8. Package lifecycle state is distinct from recommendation disposition.
9. Source provenance remains traceable.
10. Upstream evidence ownership remains with source-producing projects/artifacts.
11. Downstream adoption authority remains with consumer projects/owners.
12. Derived views must identify source package identity and version.
13. Package relationships are explicit, not inferred from naming or publication order.
14. ADPM version changes must preserve compatibility expectations or record migration rationale.
15. No component gains authority by consuming a package.

## Future capability mapping

### Serializers

Belongs in BriefForge:
- yes, if needed for durable package representation.

Layer:
- representation/transport layer.

Consumes:
- frozen or draft ADPM semantics.

May modify ADPM:
- no.

### Schema definitions

Belongs in BriefForge:
- yes, if separately approved.

Layer:
- validation/representation contract.

Consumes:
- ADPM specification and lifecycle rules.

May modify ADPM:
- no; schema changes follow semantic spec changes, not vice versa.

### Semantic validators

Belongs in BriefForge:
- yes.

Layer:
- semantic validation support.

Consumes:
- candidate ADPM packages and canonical spec.

May modify ADPM:
- no; validators emit findings only.

### Package builders

Belongs in BriefForge:
- yes, if separately approved.

Layer:
- construction support.

Consumes:
- source evidence and ADPM spec.

May modify ADPM:
- yes only before approval/freeze and only as candidate construction.

### Renderer pipelines

Belongs in BriefForge:
- yes, if separately approved.

Layer:
- publication/expression.

Consumes:
- frozen ADPM packages.

May modify ADPM:
- no.

### HTML/PDF/Markdown renderers

Belongs in BriefForge:
- yes as renderer capabilities only after separate approval.

Layer:
- publication expression.

Consumes:
- frozen ADPM plus presentation rules.

May modify ADPM:
- no.

### Comparison engines

Belongs in BriefForge:
- yes as derived-view capability after packages exist.

Layer:
- analysis/indexing/derived view.

Consumes:
- multiple frozen packages.

May modify ADPM:
- no.

### Search and indexing

Belongs in BriefForge:
- yes for package discovery.

Layer:
- indexing/discovery.

Consumes:
- package metadata and text/semantic fields.

May modify ADPM:
- no.

### Recommendation aggregation

Belongs in BriefForge:
- yes as derived synthesis if enough packages exist.

Layer:
- derived decision-support view.

Consumes:
- frozen packages and package relationships.

May modify ADPM:
- no.

### Archival system

Belongs in BriefForge:
- yes as governance preservation capability.

Layer:
- archival/governance.

Consumes:
- frozen/deprecated/superseded packages.

May modify ADPM:
- only package lifecycle metadata/relationship records through governed transition; not package semantic content.

## Readiness assessment

The architecture is now mature enough to begin planning for:

- serialization strategy;
- schema definition strategy;
- validator architecture;
- package-builder architecture.

It is not yet mature enough to implement any of those.

Before implementation, the next planning task should decide:

1. whether ADPM has one canonical representation or multiple transport forms;
2. how lifecycle states and package relationships are represented without making format the authority;
3. how semantic validation is layered from structural checks to governance approval;
4. how package identity/version/lineage are preserved;
5. which lifecycle stages need tool support first.

## Minimum next task

Recommended next workstream:

`TASK-038 ADPM Serialization and Validation Architecture Planning`

Purpose:
- design the representation and validation architecture after lifecycle/ownership freeze, without implementing schemas, builders, validators, renderers, or runtime behavior.

## Conclusion

ADPM now has a defined architectural role:

- it originates from evidence-backed decision need;
- it is constructed as candidate semantics;
- it is semantically reviewed;
- it is architecturally approved;
- it is frozen before downstream consumption;
- renderers and derived systems consume it read-only;
- publications are expressions, not authority;
- archival/supersession preserve lineage without mutating history.

This closes the major architectural gap between semantic model definition and future implementation planning.
