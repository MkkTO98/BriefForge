# Decision: ADPM Representation and Validation Architecture

Date: 2026-07-08
Status: accepted architecture-only decision; no implementation authorized
Scope: TASK-038 — ADPM representation, serialization, validation, and versioning architecture

## Decision

Accept a specification-first semantic contract architecture for future ADPM representation and validation.

Canonical direction:

```text
ADPM constitutional semantic specification
-> semantic representation contract
-> representation profile contracts
-> transport serialization forms
-> layered validation specifications
-> future implementation only after separate approval
```

This decision does not select JSON, YAML, XML, Markdown, a database schema, an API, or any concrete representation format.

## Accepted architectural principles

1. ADPM semantics remain canonical.
2. Representation serves semantics.
3. Serialization is transport, not authority.
4. No serialization format becomes constitutional authority.
5. Semantic contracts must precede transport profiles.
6. Schemas are derived structural/constraint expressions, not ontology authority.
7. Structural validation is distinct from semantic validation.
8. Semantic validation is distinct from lifecycle validation.
9. Lifecycle validation is distinct from governance approval.
10. Governance approval/freeze cannot be produced by validator success alone.
11. Renderer validation is downstream output conformance only.
12. Frozen package instances are immutable.
13. Post-freeze correction requires amendment/supersession lineage.
14. ADPM semantic version and representation profile version must remain distinct.
15. Future tools may consolidate implementation but must preserve authority boundaries and findings classification.

## Accepted representation architecture

Accepted:
- specification-first constitutional authority;
- semantic representation contract as next planning layer;
- representation profiles as derived transport contracts;
- transport serialization as subordinate expression;
- immutable package instances after freeze;
- layered validation specifications;
- versioned semantic/profile compatibility model;
- read-only consumption by renderers, search, indexing, comparison, and publication pipelines.

Not accepted:
- schema as ontology;
- serializer as authority;
- renderer input shape as package model;
- Markdown/prose report as canonical package;
- database/registry schema as package authority;
- validator success as approval/freeze.

## Serialization philosophy

Serialization is a lossless transport expression of ADPM semantics under a known semantic version and representation profile version.

Serialization may eventually support more than one profile, but no multi-format implementation is authorized now.

A first future format may be operationally preferred, but it must remain a representation profile, not the constitutional source of truth.

## Schema architecture decision

Future schema architecture should separate:

1. semantic representation contract;
2. transport profile schema;
3. lifecycle transition rules;
4. validation policy/check taxonomy;
5. compatibility/versioning rules;
6. renderer/output conformance rules if needed.

Schemas must never be treated as sufficient to establish:
- recommendation correctness;
- evidence truth;
- confidence truth;
- governance legitimacy;
- downstream adoption authority;
- package freeze.

## Validation architecture decision

Future validation should be layered:

| Layer | Purpose | Authority |
|---|---|---|
| Structural | required fields, enum values, identity/reference integrity | malformed/not malformed |
| Semantic | recommendation completeness, evidence/provenance coherence, boundary/confidence/risk completeness | findings only |
| Lifecycle | allowed transitions, immutability, lineage | transition validity findings |
| Governance | approval/freeze authority, non-authorizations, adoption boundary | governance action support |
| Compatibility | semantic/profile version compatibility and migration need | compatibility findings |
| Renderer/output | output traceability and non-contradiction | output conformance only |

A single future executable may run multiple layers, but outputs must remain classified by layer. Passing validation must not imply governance approval.

## Versioning and compatibility decision

Accepted version axes:

1. ADPM semantic version.
2. Representation profile version.

Future optional axes:
- validator policy version;
- renderer profile version;
- migration rule version.

Principles:
- frozen packages retain the semantic version under which they were frozen;
- semantic breaking changes require constitutional rationale and migration/amendment/supersession strategy;
- representation profile changes do not imply semantic changes;
- no frozen package should be silently rewritten to a new semantic version;
- unknown required semantics must fail safely.

## Builder/serializer/validator/renderer boundary decision

Accepted:
- builders construct candidates only;
- serializers transport semantics only;
- validators check and classify findings only;
- renderers express read-only frozen packages only;
- search/index/comparison produce derived views only;
- publication pipelines produce non-canonical outputs only.

No component gains governance authority from implementation capability.

## Rejected alternatives

Rejected: schema-first architecture.
- Reason: risks making schema language the ontology and flattening governance/lifecycle semantics.

Rejected: format-first architecture.
- Reason: JSON/YAML/XML/Markdown choices must not shape constitutional semantics.

Rejected: renderer-input-first architecture.
- Reason: repeats the presentation-led failure mode ADPM exists to avoid.

Rejected: database/registry-first architecture.
- Reason: premature, persistence-shaped, and unnecessary before multiple frozen packages exist.

Rejected: Markdown/prose as canonical package representation.
- Reason: useful for review/publication but weak for object identity, relationship integrity, and deterministic validation.

Rejected: monolithic validator authority.
- Reason: malformed representation, incomplete semantics, invalid lifecycle transition, missing governance authority, and renderer conformance require different owners and remedies.

Rejected: immediate multi-format implementation.
- Reason: architecture should permit multiple profiles but implementation should wait for evidence.

## Deferred decisions

Deferred until future architecture or implementation-planning tasks:

- concrete representation syntax;
- JSON/YAML/XML/Markdown profile choice;
- schema language choice;
- file organization;
- package identifier syntax;
- exact compatibility policy mechanics;
- migration record format;
- extension syntax;
- registry/catalog design;
- builder specification details;
- validator output format;
- renderer consumption contract;
- concrete hand-authored package examples.

## Readiness assessment

BriefForge is ready for the next architecture-only planning task:

`TASK-039 ADPM Representation Contract and Validation Specification Planning`

This next task may define:
- the scope and contents of a semantic representation contract;
- validation specification layers and findings taxonomy;
- representation profile requirements;
- compatibility/versioning planning;
- prerequisites for hand-authored examples.

BriefForge is not ready for implementation.

Implementation remains unauthorized for:
- JSON;
- YAML;
- XML;
- schemas;
- builders;
- validators;
- serializers;
- renderers;
- APIs;
- HTML;
- dashboards;
- templates;
- Presentation Grammar changes;
- runtime behavior;
- generated-project modifications.

## Constitutional implications

This decision strengthens the TASK-037 lifecycle by defining how representation and validation remain subordinate to ADPM semantics.

It does not alter ADPM ontology.
It does not alter ADPM lifecycle states.
It does not alter Presentation Package architecture.
It does not alter renderer boundaries.
It does not alter runtime behavior.

## Success criterion assessment

TASK-038 succeeds because it determines the long-term direction before implementation:

- semantics remain independent of representation;
- serialization is transport;
- schemas are derived contracts;
- validation is layered;
- versioning distinguishes semantic and profile versions;
- authority does not leak into builders, serializers, validators, renderers, indexes, or publication pipelines;
- next work is architecture-only specification planning, not implementation.
