# Decision: ADPM Architecture Integration

Date: 2026-07-08
Status: accepted architectural decision; no implementation authorized
Scope: TASK-037 — ADPM lifecycle, ownership, and BriefForge architectural integration

## Decision

Accept the ADPM lifecycle and ownership architecture defined by:

- `artifacts/reports/R-20260708-adpm-lifecycle-architecture.md`
- `artifacts/reports/R-20260708-adpm-component-responsibilities.md`

ADPM is now constitutionally integrated into BriefForge as a semantic decision-support lifecycle, not merely an ontology.

## Accepted lifecycle

The accepted lifecycle is:

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

This lifecycle is architectural, renderer-independent, and implementation-independent.

## Accepted lifecycle states

Accepted package lifecycle states:

- `draft`
- `under_review`
- `approved`
- `frozen`
- `deprecated`
- `superseded`
- `archived`
- `rejected`

Lifecycle state is distinct from recommendation disposition.

Examples:
- a frozen package may recommend rejection;
- a draft package may contain an adopt recommendation but is not authoritative;
- a superseded package remains historically valid;
- an archived package does not imply rejected recommendations.

## Accepted ownership model

Accepted authoritative owners:

| Responsibility | Owner |
|---|---|
| Evidence correctness | source evidence owner |
| Decision-need identification | BriefForge decision-support architecture |
| Candidate package construction | ADPM package author/builder |
| Semantic completeness review | semantic reviewer/validator function |
| Package approval/freeze/rejection/supersession/archive | BriefForge constitutional governance |
| Package identity/state/lineage catalog | ADPM registry/catalog stewardship |
| Serialization/transport | serializer/deserializer layer |
| Structural contract expression | schema/contract layer |
| Publication expression | renderer/publication layer |
| Search/index/comparison | derived-view layers |
| Adoption/implementation | consumer project or responsible owner |

## Accepted invariants

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

## Accepted package relationships

Accepted now:

- `supersedes`
- `superseded_by`
- `references`
- `derives_from`
- `amends`
- `amended_by`
- `related_to`

Deferred:

- `merged_from`
- `split_into`
- `extends`

Rationale:
- supersession, reference, derivation, and amendment are needed for lineage and auditability;
- merge/split/extend semantics add complexity before real multi-package operations exist.

## Accepted capability placement

Future capability placement is accepted as follows:

- serializers: BriefForge representation/transport layer; no semantic authority;
- schemas: structural contract expression derived from ADPM; no ontology authority;
- validators: semantic-check support; no approval authority;
- package builders: candidate construction support; no approval/freeze authority;
- renderers: publication expression; read-only consumption of frozen ADPM;
- search/index: discovery layer; read-only;
- comparison/aggregation: derived-view layer; read-only;
- archive: preservation layer; lifecycle metadata only through governed transitions;
- consumer projects: local adoption authority only.

## Rejected alternatives

Rejected: renderer-led lifecycle.
- Reason: presentation convenience must not define semantics.

Rejected: schema-led lifecycle.
- Reason: format/transport should not become ontology authority.

Rejected: validator-led approval.
- Reason: validators can support review but cannot replace governance.

Rejected: builder-owned freeze.
- Reason: construction and approval must remain separate.

Rejected: mutable frozen packages.
- Reason: destroys auditability and makes historical adoption decisions unrecoverable.

Rejected: publication artifact as canonical package.
- Reason: outputs are expressions and may be incomplete/audience-shaped.

Rejected: consumer-project mutation of canonical BriefForge package.
- Reason: consumer projects own local adoption, not BriefForge package history.

## Constitutional implications

This decision upgrades ADPM from semantic ontology to governed architectural lifecycle.

BriefForge now has two distinct but compatible semantic domains:

1. Presentation Package domain:
   - governs presentation meaning, readiness, renderer adapter boundaries, and rendered artifact conformance.

2. Architectural Decision Package domain:
   - governs architectural decision-support semantics, lifecycle state, authority, freeze, consumption, and archival.

The two domains may later interact, but neither collapses into the other.

ADPM does not modify the Presentation Package, Presentation Grammar, renderer contract, runtime behavior, validation implementation, promotion implementation, or generated projects.

## Readiness recommendation

Ready for architecture-only serialization and validation planning.

Not ready for implementation.

The next safe task is:

`TASK-038 ADPM Serialization and Validation Architecture Planning`

Scope:
- plan representation, schema, validation layers, and builder/validator architecture from the lifecycle model;
- do not implement JSON, YAML, schemas, builders, validators, renderers, runtime behavior, or generated-project changes.

## Non-authorizations

This decision does not authorize:

- serialization format implementation;
- JSON/YAML design as a committed format;
- schema implementation;
- builders;
- validators;
- renderers;
- HTML;
- dashboards;
- templates;
- visualization engines;
- Presentation Grammar changes;
- runtime behavior;
- generated-project modifications;
- source-ingestion changes;
- consumer-project task creation.

## Verification expectation

After this decision, continuity files should identify TASK-037 as complete, point to the lifecycle and responsibility reports, and recommend TASK-038 as the next architecture-only planning task.

Project verification should run:

- context build;
- context summaries;
- coherence;
- context health;
- unit test discovery.
