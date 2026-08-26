# ADPM Component Responsibility Model

Date: 2026-07-08
Status: architecture-only responsibility model
Scope: TASK-037 — ADPM ownership, component boundaries, and authority model

## Executive conclusion

ADPM requires a strict authority model:

- evidence producers own evidence correctness;
- BriefForge owns package semantics and lifecycle governance;
- package builders construct candidates but do not approve;
- semantic validators/reviewers check completeness but do not infer recommendations;
- constitutional governance approves and freezes;
- serializers transport;
- renderers express;
- search/index/comparison engines derive read-only views;
- archives preserve lineage;
- consumer projects decide adoption.

No component may gain governance authority merely because it can read, serialize, validate, render, index, or reference an ADPM package.

## Authority categories

Four authority categories govern component interaction.

### Read authority

Permission to inspect package semantics or metadata.

Read authority does not include permission to alter semantics, lifecycle state, lineage, or recommendation meaning.

### Write authority

Permission to create or modify candidate package content before freeze.

Write authority is limited to draft or under-review states unless explicitly defined as lifecycle metadata update authority.

### Governance authority

Permission to approve, freeze, deprecate, supersede, archive, or reject a package.

Governance authority cannot be delegated to renderers, serializers, validators, or search/index components.

### Rendering authority

Permission to produce non-canonical outputs from package semantics.

Rendering authority does not include semantic authority.

## Responsibility matrix

| Component | Read | Write | Governance | Render | Primary responsibility |
|---|---:|---:|---:|---:|---|
| Source Evidence Owner | yes | source only | source only | no | Own source evidence correctness |
| Decision Need Identifier | yes | candidate questions | no | no | Identify package-worthy decision pressure |
| ADPM Package Author / Builder | yes | draft package | no | no | Construct candidate package semantics |
| Semantic Reviewer / Validator | yes | findings only | no | no | Check completeness, coherence, traceability |
| BriefForge Constitutional Governance | yes | lifecycle metadata | yes | no | Approve, freeze, reject, supersede, archive |
| ADPM Registry / Catalog | yes | metadata only | no | no | Track package identity, status, lineage |
| Serializer / Deserializer | yes | representation only | no | no | Transport package semantics |
| Schema / Structural Contract | yes | contract expression | no | no | Encode structural constraints derived from spec |
| Renderer Pipeline | yes | output only | no | yes | Produce non-canonical publication expressions |
| Published Artifact | read expression | no | no | no | Communicate package meaning to readers |
| Search / Index | yes | index only | no | no | Enable discovery |
| Comparison / Aggregation Engine | yes | derived view only | no | optional expression | Compare recommendations/packages |
| Archival Store | yes | archival metadata | governed only | no | Preserve immutable package records |
| Consumer Project / Adoption Owner | yes | local adoption artifacts | local only | optional local | Decide whether to adopt recommendations |

## Component definitions

### 1. Source Evidence Owner

Definition:
- the project, artifact, or investigation responsible for evidence content.

Responsibilities:
- preserve source evidence;
- correct source evidence if needed;
- expose provenance enough for ADPM traceability.

Permitted interactions:
- provide evidence references;
- clarify source meaning;
- issue source corrections.

Prohibited interactions:
- cannot force BriefForge to recommend adoption;
- cannot mutate frozen ADPM packages directly;
- cannot bypass package review/freeze.

Authority model:
- owns evidence correctness, not ADPM package approval.

### 2. Decision Need Identifier

Definition:
- human or future support tool that recognizes decision-support need from evidence.

Responsibilities:
- identify bounded architectural decision questions;
- distinguish decision pressure from general interest;
- define candidate scope/non-scope.

Permitted interactions:
- propose package creation;
- propose primary and coupled decision questions.

Prohibited interactions:
- cannot approve package;
- cannot render package as canonical;
- cannot turn broad research topics into packages without decision boundary.

Authority model:
- has proposal authority only.

### 3. ADPM Package Author / Builder

Definition:
- human author or future builder capability that constructs candidate ADPM semantics.

Responsibilities:
- assemble semantic objects;
- link evidence/provenance;
- make uncertainty, risks, alternatives, consequences, boundaries, authority, priority, and follow-up explicit;
- preserve missing-evidence declarations.

Permitted interactions:
- create draft packages;
- revise draft/under-review packages based on findings.

Prohibited interactions:
- cannot approve, freeze, supersede, archive, or publish as authoritative;
- cannot infer adoption authority from recommendation confidence;
- cannot add renderer-driven fields as canonical semantics.

Authority model:
- write authority over candidate package content only.

### 4. Semantic Reviewer / Validator

Definition:
- human reviewer or future validator support that checks ADPM completeness and invariants.

Responsibilities:
- check object presence;
- check relationship integrity;
- check recommendation completeness;
- check provenance and traceability;
- detect authority/boundary ambiguity;
- report failures.

Permitted interactions:
- read candidate packages;
- emit findings;
- mark review result when governed.

Prohibited interactions:
- cannot invent missing recommendations;
- cannot infer evidence;
- cannot approve/freeze packages merely by passing checks;
- cannot optimize package fields for renderer convenience.

Authority model:
- validation/findings authority only.

### 5. BriefForge Constitutional Governance

Definition:
- the project-level governance function that owns ADPM lifecycle authority.

Responsibilities:
- approve or reject ADPM packages;
- freeze canonical packages;
- control lifecycle-state transitions;
- maintain lineage/supersession/archive decisions;
- maintain ADPM specification compatibility.

Permitted interactions:
- approve/freeze/reject/deprecate/supersede/archive;
- authorize future implementation tasks;
- update constitutional specification when evidence supports it.

Prohibited interactions:
- cannot claim upstream evidence correctness;
- cannot override consumer-project adoption authority;
- should not mutate frozen package semantics in-place.

Authority model:
- governance authority over ADPM packages and lifecycle.

### 6. ADPM Registry / Catalog

Definition:
- future logical index of package identity, state, version, and lineage.

Responsibilities:
- record package identifiers;
- track lifecycle state;
- record package relationships;
- provide discoverability.

Permitted interactions:
- read package metadata;
- update registry metadata through governed transitions.

Prohibited interactions:
- cannot alter package semantics;
- cannot create recommendations;
- cannot replace governance approval.

Authority model:
- metadata stewardship only.

### 7. Serializer / Deserializer

Definition:
- future capability that converts ADPM semantics into or out of transport representation.

Responsibilities:
- preserve semantics across representation boundaries;
- detect representational loss;
- preserve version/identity/lineage fields.

Permitted interactions:
- read packages;
- emit representation forms;
- reconstruct candidate package objects from representation if separately authorized.

Prohibited interactions:
- cannot define semantic meaning;
- cannot drop required objects for convenience;
- cannot make JSON/YAML/Markdown shape the constitutional source of truth.

Authority model:
- transport authority only.

### 8. Schema / Structural Contract

Definition:
- future formal expression of ADPM structural requirements.

Responsibilities:
- encode required fields, allowed values, relationships, and lifecycle-state constraints;
- support deterministic validation.

Permitted interactions:
- consume ADPM specification;
- support validators/builders.

Prohibited interactions:
- cannot add canonical concepts not present in ADPM specification;
- cannot remove semantic requirements because they are inconvenient to encode;
- cannot become governance authority.

Authority model:
- structural expression authority only.

### 9. Renderer Pipeline

Definition:
- future publication/expression component consuming ADPM packages.

Responsibilities:
- express package semantics for readers;
- preserve traceability to package identity/version;
- avoid contradiction of canonical semantics.

Permitted interactions:
- read frozen packages;
- generate non-canonical outputs;
- report rendering limitations.

Prohibited interactions:
- cannot modify semantics;
- cannot determine package lifecycle state;
- cannot hide boundary constraints in ways that change meaning;
- cannot make presentation fields canonical.

Authority model:
- rendering authority only.

### 10. Published Artifact

Definition:
- output produced from an ADPM package or package-derived view.

Responsibilities:
- communicate package meaning;
- link back to canonical package identity/lineage.

Permitted interactions:
- be read, cited, distributed, or archived as output.

Prohibited interactions:
- cannot become semantic authority over the package;
- cannot supersede package content by being edited.

Authority model:
- communication artifact only.

### 11. Search / Index

Definition:
- future discoverability capability over packages and metadata.

Responsibilities:
- provide lookup;
- support retrieval;
- preserve links to canonical package IDs.

Permitted interactions:
- read package fields;
- write indexes.

Prohibited interactions:
- cannot rank packages in a way that changes recommendation priority unless clearly marked as derived view;
- cannot mutate package lifecycle state.

Authority model:
- discovery authority only.

### 12. Comparison / Aggregation Engine

Definition:
- future derived-view capability comparing packages or recommendations.

Responsibilities:
- compare horizons, confidence, authority, impacts, priority, risks, or open questions;
- produce aggregate views.

Permitted interactions:
- read frozen packages;
- generate derived comparison outputs.

Prohibited interactions:
- cannot merge packages by itself;
- cannot create canonical recommendations;
- cannot supersede packages.

Authority model:
- derived-view authority only.

### 13. Archival Store

Definition:
- durable preservation location/system for packages and lineage records.

Responsibilities:
- preserve immutable frozen, superseded, deprecated, archived, or rejected packages;
- retain lineage and audit information.

Permitted interactions:
- store packages;
- expose packages for retrieval;
- update archival metadata only through governed transition.

Prohibited interactions:
- cannot edit frozen package semantics;
- cannot delete lineage needed for auditability.

Authority model:
- preservation authority only.

### 14. Consumer Project / Adoption Owner

Definition:
- downstream project or owner that may act on a recommendation.

Responsibilities:
- decide whether to adopt, reject, defer, or adapt recommendations locally;
- create local tasks/decisions if adopted;
- own implementation consequences.

Permitted interactions:
- read ADPM packages;
- reference ADPM in local decisions;
- create local adoption artifacts.

Prohibited interactions:
- cannot modify canonical BriefForge package semantics;
- cannot treat ADPM recommendation as automatic implementation approval;
- cannot require BriefForge to change ADPM to match local implementation preference.

Authority model:
- local adoption authority only.

## Permitted interaction map

```text
Source Evidence Owner
  -> provides provenance/evidence to
Decision Need Identifier
  -> proposes questions to
ADPM Package Author / Builder
  -> constructs draft for
Semantic Reviewer / Validator
  -> emits findings to
Package Author / Builder
  -> revises draft until
BriefForge Constitutional Governance
  -> approves/freezes/rejects and records state in
ADPM Registry / Catalog / Archive
  -> exposes read-only package to
Serializers / Renderers / Search / Comparison / Consumer Projects
```

## Prohibited authority leakage

The following are explicitly prohibited:

1. Renderer changes ADPM semantics.
2. Serializer defines canonical object meaning.
3. Validator infers missing recommendations.
4. Builder approves its own package.
5. Search/index changes recommendation priority.
6. Comparison engine supersedes packages automatically.
7. Published artifact becomes canonical package authority.
8. Consumer project treats recommendation as automatic local task.
9. Source evidence owner bypasses package review.
10. Archive mutates frozen package content.

## Interface expectations

Interfaces are architectural, not serialized formats.

### Evidence-to-package interface

Must preserve:
- evidence reference;
- source provenance;
- known limitations;
- evidence role.

May not require:
- a particular file format;
- a particular upstream project structure.

### Package-to-review interface

Must expose:
- all required objects;
- relationships;
- lifecycle state;
- version;
- traceability;
- boundary constraints;
- authority records.

May not expose:
- renderer instructions as semantic requirements.

### Package-to-renderer interface

Must expose:
- frozen package semantics;
- package identity/version;
- traceability links;
- explicit boundary constraints.

May not allow:
- renderer writes to package semantics.

### Package-to-index/comparison interface

Must expose:
- package metadata;
- recommendation dispositions/horizons/priorities;
- confidence and uncertainty;
- relationships;
- lifecycle state.

May not allow:
- derived view mutation of canonical package.

## Boundary decisions

Accepted:
- BriefForge owns ADPM semantics and lifecycle governance.
- Future package builders belong in BriefForge as candidate construction support.
- Future validators belong in BriefForge as semantic-check support.
- Future serializers/schemas belong in BriefForge as representation/contract support, not authority.
- Future renderers consume frozen ADPM read-only.
- Future search/comparison/indexing consume packages read-only and produce derived views.
- Consumer projects retain adoption sovereignty.

Rejected:
- source projects owning BriefForge package semantics;
- renderers owning package structure;
- schemas owning ontology;
- validators owning approval;
- builders owning freeze;
- published outputs owning canonical semantics;
- consumer projects mutating canonical BriefForge packages.

## Readiness for future planning

This responsibility model is sufficient to begin serialization and validation architecture planning because it clarifies:

- who creates candidate packages;
- who validates semantics;
- who approves/freezes;
- who may consume read-only;
- which future capabilities are transport/check/expression rather than semantic authority.

Next planning should preserve this responsibility model and avoid implementing any component until its interface and authority boundary are explicitly designed.
