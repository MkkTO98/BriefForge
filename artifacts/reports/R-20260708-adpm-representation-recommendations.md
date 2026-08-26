# ADPM Representation and Validation Recommendations

Date: 2026-07-08
Status: architecture-only recommendations
Scope: TASK-038 — representation, serialization, validation, and versioning architecture

## Executive recommendation

Adopt a specification-first semantic contract architecture for ADPM representation and validation.

Do not choose or implement a concrete serialization format yet. Do not write schemas yet. Do not build validators, builders, serializers, renderers, APIs, or runtime behavior.

The strongest architecture is:

```text
ADPM semantic specification
-> semantic representation contract
-> representation profile(s)
-> layered validation specifications
-> future implementation only after separate approval
```

This preserves the governing principle:

> Representation must serve the semantic model; representation must not become the model.

## Recommendation 1 — Keep ADPM specification-first

Problem addressed:
- Schema-first or format-first work could accidentally make a JSON/YAML/schema shape the constitutional authority.

Architectural rationale:
- ADPM contains governance, authority, lifecycle, provenance, confidence, recommendation, and boundary semantics that cannot be fully represented by structural fields alone.
- TASK-037 established that serializers transport semantics but do not define them.

Expected benefits:
- preserves semantic independence;
- prevents renderer/schema influence over ontology;
- supports future representation changes without constitutional redesign;
- aligns with ProjectForge capability-first governance.

Potential drawbacks:
- requires discipline to keep implementation artifacts subordinate;
- implementers may want a machine-readable artifact sooner.

Implementation implications:
- future schema/serialization work must cite the semantic specification as authority;
- generated validators should classify checks by semantic layer;
- no first implementation should claim to be the model.

Confidence assessment:
- High.

## Recommendation 2 — Introduce a semantic representation contract before transport profiles

Problem addressed:
- Directly jumping from prose specification to a concrete serialization format risks encoding accidental choices.

Architectural rationale:
- A semantic representation contract can define objects, relationships, identity, versioning, lifecycle obligations, and invariant categories without selecting JSON/YAML/XML/etc.
- This creates a bridge from constitutional semantics to future schemas.

Expected benefits:
- gives implementation planning enough precision;
- avoids premature format selection;
- supports multiple profiles later;
- clarifies what schemas must preserve.

Potential drawbacks:
- introduces an additional planning artifact;
- could become redundant if over-specified.

Implementation implications:
- future TASK-039 should define contract scope and obligations, not implementation files;
- contract should remain minimal and derived from ADPM, not a second ontology.

Confidence assessment:
- High.

## Recommendation 3 — Treat serialization as transport only

Problem addressed:
- Serialized files often become de facto authority because tools consume them.

Architectural rationale:
- ADPM constitutional semantics exist independently of serialization.
- A serialized form should be a lossless expression of a package under a known ADPM semantic version and representation profile version.

Expected benefits:
- avoids format lock-in;
- permits future multiple profiles;
- protects frozen packages from parser/schema convenience changes;
- supports archival and compatibility.

Potential drawbacks:
- tooling may require explicit mapping rules;
- a single first profile may feel non-canonical despite being operationally preferred.

Implementation implications:
- serialized packages must carry semantic-version/profile-version identity later;
- serializers must detect loss/incompatibility rather than reinterpret content;
- no renderer should consume a private shape that bypasses semantic contracts.

Confidence assessment:
- High.

## Recommendation 4 — Separate semantic schemas from transport schemas

Problem addressed:
- A single schema cannot safely represent structural shape, semantic invariants, lifecycle transitions, governance authority, and compatibility policy without conflating responsibilities.

Architectural rationale:
- Field presence differs from recommendation completeness.
- Enum validity differs from lifecycle authority.
- Lifecycle state differs from recommendation disposition.
- Governance approval differs from validator success.

Expected benefits:
- clearer validation outputs;
- less authority leakage;
- easier future migration;
- better fit for review-assisted semantic validation.

Potential drawbacks:
- more conceptual categories to explain;
- future tooling must avoid unnecessary component proliferation.

Implementation implications:
- one future tool may run multiple validation layers, but results must remain classified;
- schema files, if later created, should not claim full governance validation.

Confidence assessment:
- High.

## Recommendation 5 — Define layered validation architecture

Problem addressed:
- A monolithic validator would blur malformed representation, incomplete semantics, invalid lifecycle transition, missing governance authority, and renderer conformance.

Architectural rationale:
- TASK-037 says validators check but do not approve/freeze.
- Different validation failures require different owners and remedies.

Recommended validation layers:

1. Structural validation
2. Semantic validation
3. Lifecycle validation
4. Governance validation
5. Compatibility validation
6. Renderer/output conformance validation

Expected benefits:
- precise diagnostics;
- clear owner responsibility;
- prevents validator-led approval;
- supports future automation without replacing human governance.

Potential drawbacks:
- could be over-implemented as many tools;
- may require careful reporting taxonomy.

Implementation implications:
- a single future command may produce layered findings;
- passing structural validation must not imply package approval;
- governance validation may require human approval records.

Confidence assessment:
- High.

## Recommendation 6 — Version semantics independently from representation profiles

Problem addressed:
- Without separate versions, a format change could be mistaken for semantic change, or a semantic change could be hidden inside a schema revision.

Architectural rationale:
- Frozen packages must remain interpretable under the ADPM version used at freeze.
- Representation profiles should evolve without rewriting semantic meaning.

Expected benefits:
- clearer migration path;
- safer archival;
- supports compatibility adapters;
- reduces pressure to mutate frozen packages.

Potential drawbacks:
- version bookkeeping increases complexity;
- early implementation may seem heavier.

Implementation implications:
- future package representations should identify both ADPM semantic version and representation profile version;
- compatibility reports should distinguish semantic vs profile incompatibility.

Confidence assessment:
- High.

## Recommendation 7 — Defer multi-format support until evidence requires it

Problem addressed:
- Multiple formats too early would create complexity without demonstrated value.

Architectural rationale:
- The architecture should permit multiple profiles but not implement them prematurely.
- Current evidence supports representation independence, not multi-format implementation.

Expected benefits:
- preserves flexibility without immediate complexity;
- avoids overengineering;
- reduces first implementation burden.

Potential drawbacks:
- future second format may require profile abstraction discipline from the start.

Implementation implications:
- future first profile should be designed as one profile among possible profiles, even if only one exists;
- do not build conversion matrices until needed.

Confidence assessment:
- Medium-high.

## Recommendation 8 — Defer registry/database architecture

Problem addressed:
- A registry or database-first approach could overbuild before multiple frozen ADPM packages exist.

Architectural rationale:
- TASK-037 established registry/catalog as a logical component, not an immediate system.
- Current needs are semantic representation and validation planning, not persistence.

Expected benefits:
- avoids premature storage design;
- keeps ADPM implementation-independent;
- reduces authority leakage from database schema.

Potential drawbacks:
- later search/index work may need backfilled metadata.

Implementation implications:
- future representation contract should preserve identity, lifecycle state, version, and relationships so registry can be added later;
- no database/API should be designed now.

Confidence assessment:
- High.

## Recommendation 9 — Treat Markdown/prose as expression, not canonical representation

Problem addressed:
- Existing BriefForge reports are Markdown-heavy; there is a temptation to make Markdown sections the package representation.

Architectural rationale:
- Markdown is excellent for human review and publication but weak for relationship integrity and machine validation.
- Reports are evidence or expression, not semantic package authority.

Expected benefits:
- preserves human-readable review;
- prevents heading structure from becoming ontology;
- supports future rendered outputs without semantic drift.

Potential drawbacks:
- early hand-authored examples may need another structured representation later.

Implementation implications:
- Markdown examples may be useful, but should be labeled non-canonical expressions unless they are paired with a semantic representation profile later.

Confidence assessment:
- High.

## Recommendation 10 — Make extension mechanisms conservative and evidence-gated

Problem addressed:
- Too much extensibility can undermine a frozen semantic model; too little can block future project-independent evolution.

Architectural rationale:
- ADPM must remain stable but future package families may reveal repeated needs.
- Extensions should not redefine canonical semantics or bypass validation.

Expected benefits:
- supports long-term evolution;
- prevents project-specific drift;
- allows evidence accumulation before promotion.

Potential drawbacks:
- extension rules may be unnecessary for first examples;
- poorly governed extensions could fragment ADPM.

Implementation implications:
- future planning may define extension principles, but actual extension implementation should wait for evidence;
- extension promotion should require adversarial review.

Confidence assessment:
- Medium.

## Recommendation 11 — Use immutable package instances with amendment/supersession lineage

Problem addressed:
- Representation planning must preserve TASK-037 immutability.

Architectural rationale:
- Frozen package semantics cannot mutate without losing auditability.
- Amendments and supersession preserve original decision context.

Expected benefits:
- reliable audit trail;
- safer long-term archival;
- compatibility with frozen package versioning;
- clear distinction between correction and replacement.

Potential drawbacks:
- more lineage metadata;
- consumers must understand active vs superseded packages.

Implementation implications:
- future representation contract must include identity/version/relationship obligations;
- migration should produce views or related records, not silent rewrites.

Confidence assessment:
- High.

## Recommendation 12 — Keep builder, validator, serializer, renderer, and derived-view authority separate even if implemented together later

Problem addressed:
- Future codebases may combine multiple capabilities, creating implicit authority leakage.

Architectural rationale:
- Authority separation is conceptual first, implementation second.
- A single CLI could eventually run builder assistance and validation, but it must not approve/freeze.

Expected benefits:
- avoids unnecessary tool proliferation;
- preserves governance boundaries;
- supports pragmatic implementation later.

Potential drawbacks:
- requires explicit output labeling and role separation.

Implementation implications:
- future tools should classify mode and authority in outputs;
- no tool output should imply governance approval unless governance action is explicitly recorded.

Confidence assessment:
- High.

## Recommendation 13 — Require hand-authored example pressure after representation contract planning

Problem addressed:
- The architecture has not yet been tested through concrete ADPM package instances.

Architectural rationale:
- Examples reveal friction without implementing runtime systems.
- Examples should test the semantic contract before schemas/builders/validators are implemented.

Expected benefits:
- reduces risk of overabstract contract design;
- reveals missing representation obligations;
- informs first profile/schema planning.

Potential drawbacks:
- examples may be mistaken for implementation artifacts;
- examples may bias the first profile if too few are used.

Implementation implications:
- examples should be explicitly non-runtime and hand-authored;
- select diverse prior investigations, including no-action, high-uncertainty, and competing-alternative decisions.

Confidence assessment:
- Medium-high.

## Recommendation 14 — Allow one future validator implementation to run multiple checks, but require layered findings

Problem addressed:
- Layered architecture could be mistaken as a demand for many separate tools.

Architectural rationale:
- Architectural separation does not require implementation proliferation.
- What matters is the authority boundary and failure classification.

Expected benefits:
- simpler future implementation;
- preserves diagnostic precision;
- avoids unnecessary abstraction.

Potential drawbacks:
- a combined tool may encourage users to treat one pass as approval.

Implementation implications:
- validator reports must distinguish structural, semantic, lifecycle, governance, compatibility, and renderer findings;
- validator success must not equal freeze/approval.

Confidence assessment:
- High.

## Recommendation 15 — Do not begin implementation after TASK-038; begin specification planning

Problem addressed:
- TASK-038 answers direction, not detailed contract contents.

Architectural rationale:
- Representation and validation principles are now clear, but concrete contract/specification boundaries still need planning before implementation.

Expected benefits:
- prevents premature JSON/schema work;
- creates a precise next gate;
- reduces risk of rework.

Potential drawbacks:
- delays implementation.

Implementation implications:
- next task should be `TASK-039 ADPM Representation Contract and Validation Specification Planning`.

Confidence assessment:
- High.

## Consolidated accepted principles

1. ADPM semantics are canonical; representations are subordinate.
2. Serialization is transport, not authority.
3. Semantic contracts precede transport profiles.
4. Schemas express structure and some constraints, but not governance legitimacy.
5. Validation is layered and findings must remain classified.
6. Semantic version and representation profile version are distinct.
7. Frozen package instances are immutable.
8. Migration must preserve lineage.
9. Renderers, search, index, comparison, and publication consume read-only.
10. Builders assist construction but do not approve/freeze.
11. Validators check but do not infer recommendations or approve/freeze.
12. Multi-format support is permitted architecturally but deferred operationally.
13. Registry/database architecture is deferred.
14. Markdown/prose remains expression/review, not canonical representation.
15. Hand-authored examples should follow contract planning and precede implementation.

## Rejected approaches

Rejected as canonical:
- schema-first architecture;
- JSON/YAML/XML-first architecture;
- database/registry-first architecture;
- renderer-input-first architecture;
- Markdown/prose-as-canonical package architecture;
- validator-pass-as-approval architecture;
- one serialization format as constitutional authority.

Deferred:
- multi-format implementation;
- registry/database design;
- extension mechanism implementation;
- compatibility adapters;
- migration tooling;
- package examples until representation contract planning is complete.

## Readiness recommendation

BriefForge is ready for architecture-only specification planning:

- representation contract specification planning;
- validation specification planning;
- schema architecture planning;
- builder specification planning.

BriefForge is not ready for implementation of:

- serialization formats;
- schemas;
- validators;
- builders;
- serializers;
- renderers;
- APIs;
- runtime behavior;
- generated-project changes.
