# ADPM Representation Architecture Evaluation

Date: 2026-07-08
Status: architecture-only evaluation and recommendation campaign
Scope: TASK-038 — ADPM representation, serialization, validation, and versioning architecture

## Executive conclusion

The best long-term direction is a specification-first, semantic-canonical architecture with derived representation contracts.

ADPM should not become a JSON model, YAML model, schema-first model, renderer input model, database model, or runtime object model. Its constitutional authority should remain the semantic specification and lifecycle governance established by TASK-035 through TASK-037.

Recommended direction:

```text
Constitutional ADPM semantic specification
-> semantic object model / conceptual contract
-> representation profile contracts
-> transport serialization forms
-> layered validation architecture
-> read-only renderer/search/index/comparison consumption
```

This direction preserves the key principle:

> Representation serves ADPM semantics; ADPM semantics do not evolve for representation convenience.

The evaluation did not find evidence that BriefForge needs a heavy intermediate-platform architecture before implementation planning. The opposite risk is larger: over-abstracting before even one real ADPM package has been represented. The recommended approach is therefore conservative:

1. keep ADPM semantics specification-first;
2. distinguish semantic contracts from transport schemas;
3. make serialization a lossless transport expression, not authority;
4. use layered validators with separate responsibilities;
5. version ADPM semantics independently from representation profiles;
6. require example-driven pressure before adding complex extension machinery.

## Scope and non-scope

In scope:
- representation alternatives;
- serialization philosophy;
- schema architecture;
- validation architecture;
- versioning and compatibility principles;
- future component boundaries;
- adversarial review of overengineering risk;
- readiness for future planning.

Out of scope:
- JSON design;
- YAML design;
- XML design;
- schema files;
- builders;
- validators;
- serializers;
- renderers;
- APIs;
- templates;
- runtime behavior;
- generated-project changes.

## Evidence base

This evaluation relies on:

- `artifacts/specifications/architectural-decision-package-model.md`
- `artifacts/reports/R-20260708-architectural-decision-package-model.md`
- `artifacts/reports/R-20260708-adpm-adversarial-validation.md`
- `artifacts/reports/R-20260708-adpm-stability-assessment.md`
- `artifacts/decisions/D-20260708-adpm-validation-decision.md`
- `artifacts/reports/R-20260708-adpm-lifecycle-architecture.md`
- `artifacts/reports/R-20260708-adpm-component-responsibilities.md`
- `artifacts/decisions/D-20260708-adpm-architecture-integration.md`
- current BriefForge architecture/state/backlog continuity files.

Key prior findings used here:

- ADPM is semantic authority, not renderer/presentation authority.
- Lifecycle state is distinct from recommendation disposition.
- Frozen packages are immutable.
- Serializers transport semantics but do not define them.
- Validators check semantics but do not infer recommendations.
- Builders construct candidate packages but do not approve/freeze them.
- Renderers consume frozen packages read-only.
- Package lineage and ADPM versioning are necessary before serialized packages exist.

## Evaluation criteria

Alternatives were evaluated against:

1. semantic stability;
2. implementation independence;
3. renderer independence;
4. long-term maintainability;
5. auditability;
6. lifecycle compatibility;
7. ProjectForge governance compatibility;
8. ability to support future builders, validators, renderers, search, indexing, and comparison;
9. resistance to authority leakage;
10. simplicity proportional to current evidence.

## Alternative A — Canonical internal semantic model with derived serialized forms

Summary:
- ADPM semantics remain canonical.
- Serialized forms are generated or authored expressions of those semantics.
- Future schemas validate representation conformance to semantic contracts rather than becoming the ontology.

Strengths:
- best preserves semantic authority;
- aligns with TASK-037 lifecycle and authority boundaries;
- supports multiple serialization profiles without making any one format canonical;
- keeps renderers/search/index/comparison read-only;
- allows future implementation language choice without constitutional impact;
- supports versioning of semantics separately from representation profiles.

Weaknesses:
- requires careful documentation so future implementers do not treat the first format as canonical by accident;
- needs explicit mapping rules between semantic objects and representation profiles;
- may feel slower than immediately writing a JSON schema.

Maintainability:
- high, if contracts are small and versioned.

Semantic stability:
- high.

Implementation independence:
- high.

ProjectForge compatibility:
- strong; ProjectForge favors capability/constitution first and implementation as supporting expression.

Assessment:
- Recommended, but with a simplification: call this a semantic-contract architecture, not an elaborate internal object platform until implementation evidence justifies one.

## Alternative B — Schema-first architecture

Summary:
- A schema language becomes the primary artifact from which objects, validators, builders, and serializers are derived.

Strengths:
- easier deterministic validation;
- familiar implementation path;
- clear field requirements;
- fast tooling ecosystem once a schema language is selected.

Weaknesses:
- risks making encoding choices canonical;
- schema language expressiveness could distort ontology;
- hard-to-express invariants may be downgraded or omitted;
- lifecycle and governance rules may get flattened into structural fields;
- future non-schema-friendly semantics could be resisted because they are inconvenient.

Maintainability:
- medium; strong for structural checks, weaker for constitutional evolution.

Semantic stability:
- medium-low if schema becomes authority.

Implementation independence:
- medium-low.

ProjectForge compatibility:
- weak as a constitutional source of truth; acceptable only as a derived structural contract.

Assessment:
- Rejected as canonical architecture.
- Accepted only as a future derived layer.

## Alternative C — Specification-first architecture

Summary:
- The prose/constitutional ADPM specification remains the canonical authority.
- Future representation, schema, and validation artifacts are subordinate expressions.

Strengths:
- strongest constitutional clarity;
- matches current BriefForge architecture style;
- prevents schema/format from redefining semantics;
- accommodates governance, authority, and lifecycle rules that are not purely structural.

Weaknesses:
- pure prose can be too ambiguous for implementation unless paired with machine-checkable contracts;
- implementers need translation from specification to representation rules;
- risk of divergence between prose and schemas unless governance is explicit.

Maintainability:
- high if paired with contract derivation discipline.

Semantic stability:
- high.

Implementation independence:
- high.

ProjectForge compatibility:
- strong.

Assessment:
- Recommended as the constitutional layer, but insufficient alone. It should be paired with semantic contracts and layered validation specifications.

## Alternative D — Contract-first architecture

Summary:
- A stable semantic contract defines objects, relationships, lifecycle states, invariants, and compatibility expectations before choosing serialization formats.

Strengths:
- bridges prose and eventual implementation;
- keeps semantics independent of JSON/YAML/XML/etc.;
- supports future schemas as contract expressions;
- allows multiple representation profiles;
- separates structural, semantic, lifecycle, compatibility, and governance validation.

Weaknesses:
- contract terminology can become abstract if not grounded by examples;
- contract/version boundaries must be clear to avoid becoming another ontology layer.

Maintainability:
- high.

Semantic stability:
- high.

Implementation independence:
- high.

ProjectForge compatibility:
- strong.

Assessment:
- Recommended as the next architectural planning layer: specification-first plus contract-first representation planning.

## Alternative E — Intermediate representation layer

Summary:
- Define an intermediate ADPM representation independent of serialization and implementation languages; serializers/renderers consume this representation.

Strengths:
- clean separation from transport formats;
- can support multiple serialized forms;
- can centralize semantic mapping;
- useful if multiple implementations or renderers emerge.

Weaknesses:
- likely premature before one real representation exists;
- creates a second model that could drift from the semantic specification;
- may introduce unnecessary abstraction and implementation burden;
- risks treating implementation object shape as canonical.

Maintainability:
- medium-high only after enough implementation evidence exists.

Semantic stability:
- high if disciplined, medium if it drifts.

Implementation independence:
- high conceptually, lower if prematurely tied to a language/runtime.

ProjectForge compatibility:
- acceptable later; premature now.

Assessment:
- Defer. Plan the boundary, but do not constitutionalize a separate intermediate representation before concrete examples exist.

## Alternative F — Immutable document model

Summary:
- Treat each ADPM package as an immutable document once frozen; amendments and supersession create new documents/records.

Strengths:
- aligns with frozen-package immutability;
- supports auditability, archival, and lineage;
- easy for readers to understand;
- compatible with multiple serialized forms.

Weaknesses:
- document thinking can collapse semantics into prose/file representation;
- partial updates and derived views require disciplined lineage rules;
- may underspecify semantic object identity if treated too loosely.

Maintainability:
- high for archival and governance.

Semantic stability:
- high if document is an expression of a semantic package, not the authority itself.

Implementation independence:
- high.

ProjectForge compatibility:
- strong.

Assessment:
- Accept as lifecycle/archival doctrine: frozen ADPM package instances are immutable semantic documents. Do not treat document format as canonical.

## Alternative G — Database/registry-first architecture

Summary:
- ADPM exists primarily as records in a registry/database; packages are queried, rendered, and versioned through persistent storage.

Strengths:
- strong indexing/search possibilities;
- supports package relationships and lifecycle metadata;
- useful at scale.

Weaknesses:
- heavy and premature;
- makes persistence design seem authoritative;
- conflicts with current no-runtime/no-storage boundary;
- unnecessary before multiple frozen packages exist.

Maintainability:
- unknown; too early.

Semantic stability:
- medium if database schema becomes authority.

Implementation independence:
- low at this phase.

ProjectForge compatibility:
- weak now; may become a later derived capability.

Assessment:
- Rejected for current phase. Registry/catalog remains a logical component only.

## Alternative H — Markdown/prose package as canonical representation

Summary:
- ADPM packages are authored as Markdown documents with headings/sections corresponding to objects.

Strengths:
- human-friendly;
- low tooling burden;
- easy to review early examples;
- matches existing artifact culture.

Weaknesses:
- headings are brittle as structural authority;
- relationship integrity and lifecycle transitions are hard to validate;
- can blur semantic object boundaries;
- renderer/publication expression may be mistaken for canonical semantics.

Maintainability:
- medium for human review; weak for reliable validation.

Semantic stability:
- medium-low if canonical.

Implementation independence:
- high superficially, but low for machine validation.

ProjectForge compatibility:
- acceptable as reports/examples, not as canonical package authority.

Assessment:
- Reject as canonical representation. Accept as a review/publication expression or hand-authored example aid.

## Alternative I — One canonical serialization format

Summary:
- Select one future transport format and make it the only canonical package representation.

Strengths:
- simpler tooling;
- fewer conversion concerns;
- easier for initial implementation.

Weaknesses:
- format becomes authority by default;
- future migration becomes costly;
- semantic evolution becomes coupled to parser/schema limitations;
- conflicts with representation-independence principle.

Maintainability:
- high initially, lower over time.

Semantic stability:
- medium-low.

Implementation independence:
- low.

ProjectForge compatibility:
- weak as constitutional architecture.

Assessment:
- Rejected as constitutional philosophy. A first implementation may choose one format later, but it must remain a profile, not the ontology.

## Comparative summary

| Alternative | Semantic stability | Simplicity now | Long-term flexibility | Authority leakage risk | Recommendation |
|---|---:|---:|---:|---:|---|
| Semantic canonical + derived serialized forms | high | medium | high | low | accept |
| Schema-first | medium-low | high | medium | high | reject as canonical |
| Specification-first | high | high | medium-high | low | accept as constitutional layer |
| Contract-first | high | medium | high | low | accept as next planning layer |
| Intermediate representation | medium-high | low | high | medium | defer |
| Immutable document model | high | high | medium-high | low-medium | accept as lifecycle doctrine |
| Database/registry-first | medium | low | medium | high | reject now |
| Markdown/prose canonical | medium-low | high | medium | high | reject as canonical |
| One canonical serialization format | medium-low | high | low-medium | high | reject as constitutional direction |

## Serialization philosophy

Serialization should be a transport and interchange mechanism only.

Accepted principles:

1. Canonical ADPM semantics exist independently of any serialized form.
2. No serialization format is semantic authority.
3. Multiple serialization profiles may eventually exist if they preserve the same semantic contract.
4. A profile may be preferred operationally without becoming constitutional authority.
5. Lossy serialization cannot represent a canonical package.
6. Every serialized package must identify ADPM semantic version and representation profile version.
7. Serializers/deserializers may detect representational loss but may not reinterpret recommendations.
8. Human-readable rendered outputs are not serialization authority.

Rejected serialization philosophies:

- “JSON is the model.”
- “Markdown headings are the model.”
- “The renderer input shape is the model.”
- “The validator schema is the model.”
- “The database tables are the model.”

## Schema architecture evaluation

Schemas should eventually be derived expressions of semantic contracts.

Recommended separation:

1. Semantic contract specification
   - object types, relationships, invariants, authority rules, lifecycle semantics, compatibility expectations.

2. Transport schema/profile
   - concrete representation of the semantic contract in a selected interchange format.

3. Lifecycle rule specification
   - allowed/prohibited transitions, governance authority, immutability, archival and supersession rules.

4. Validation policy specification
   - which checks are structural, semantic, lifecycle, governance, compatibility, or renderer-facing.

Why separate them:
- structural field presence is not the same as recommendation completeness;
- lifecycle transitions are not mere enum validation;
- governance authority cannot be proven by schema alone;
- renderer conformance is downstream and should not constrain canonical semantics;
- compatibility rules must survive representation-profile changes.

Extensibility:
- extension points should exist eventually, but should be conservative;
- extensions must be namespaced/profiled;
- extensions must not redefine canonical objects;
- extension use in frozen packages must remain traceable;
- repeated evidence should precede canonical promotion.

What schemas must never express alone:
- architectural approval;
- downstream adoption authority;
- evidence truth;
- recommendation correctness;
- confidence truth;
- governance legitimacy;
- renderer adequacy;
- package freeze by mere structural validity.

## Validation architecture evaluation

Validation must be layered. Collapsing all validation into one validator would create authority leakage.

### Structural validation

Purpose:
- required fields;
- allowed enum values;
- object identity uniqueness;
- relationship references exist;
- profile-level representation well-formedness.

Owner:
- structural contract/schema layer.

Authority:
- can fail malformed packages;
- cannot approve packages.

### Semantic validation

Purpose:
- recommendations answer decision questions;
- evidence roles are coherent;
- boundary constraints exist where needed;
- confidence has rationale/reducers/improvers;
- no-action consequence exists;
- missing evidence is explicit.

Owner:
- semantic validation/review function.

Authority:
- can produce findings;
- cannot invent missing content;
- cannot approve/freeze.

### Lifecycle validation

Purpose:
- package status is allowed;
- transitions are allowed;
- frozen package immutability is preserved;
- supersession/amendment lineage is explicit;
- archived packages are not silently mutated.

Owner:
- ADPM lifecycle governance/checking function.

Authority:
- can reject invalid transition records;
- cannot replace constitutional governance.

### Governance validation

Purpose:
- approval/freeze/rejection/supersession/archive actions have proper authority;
- non-authorizations are preserved;
- consumer-project adoption authority is not claimed by BriefForge.

Owner:
- BriefForge constitutional governance.

Authority:
- governance approval only; not automated validity alone.

### Compatibility validation

Purpose:
- ADPM semantic version compatibility;
- representation profile version compatibility;
- migration/supersession expectations;
- forward/backward compatibility declarations.

Owner:
- ADPM compatibility governance.

Authority:
- can identify migration requirement or incompatibility;
- cannot silently migrate frozen semantics.

### Renderer validation

Purpose:
- rendered output traces to package identity/version;
- rendered output does not contradict package semantics;
- publication expression preserves boundary constraints and authority caveats.

Owner:
- renderer/conformance layer.

Authority:
- output conformance only;
- no semantic authority.

## Versioning and compatibility

ADPM requires at least two conceptual version axes:

1. ADPM semantic version
   - version of the canonical semantic model and lifecycle rules.

2. Representation profile version
   - version of a particular serialized/transport expression.

Additional future version axes may include:
- validator policy version;
- renderer profile version;
- migration rule version.

Versioning principles:

- semantic version changes require constitutional rationale;
- representation profile changes must not imply semantic changes;
- frozen packages retain the ADPM semantic version under which they were frozen;
- backward-compatible semantic additions may be allowed only if existing packages remain interpretable;
- breaking semantic changes require explicit migration, amendment, or supersession strategy;
- no frozen package should be silently rewritten to a new semantic version;
- compatibility declarations should be explicit, not inferred from dates or filenames.

Migration philosophy:

- prefer non-destructive migration views over in-place mutation;
- preserve original package identity/version;
- record derived migrated expression separately when needed;
- use supersession for changed meaning;
- use amendment for correction/clarification that preserves original decision lineage.

Forward compatibility:
- future consumers should fail safely on unknown required semantics;
- optional extensions should be ignorable only when they do not affect decision meaning;
- unknown lifecycle states or dispositions must not be guessed.

Backward compatibility:
- future tooling should preserve access to older frozen packages;
- older packages may be rendered/indexed through compatibility adapters, but adapters must identify source semantic version.

## Builder, serializer, validator, renderer, and derived-system boundaries

### Package builders

May:
- construct candidate packages;
- assist with completeness;
- expose missing fields;
- propose evidence links.

May not:
- approve/freeze;
- invent evidence;
- claim adoption authority;
- optimize object structure for renderer convenience.

### Serializers/deserializers

May:
- transport packages;
- preserve identity/version/relationships;
- report loss or incompatibility.

May not:
- define semantic meaning;
- reinterpret missing evidence;
- alter recommendation disposition;
- mutate frozen packages.

### Validators

May:
- classify failures;
- emit findings;
- check structural/semantic/lifecycle/governance/compatibility constraints according to layer.

May not:
- approve/freeze;
- infer recommendations;
- turn passing validation into constitutional acceptance.

### Renderers/publication pipelines

May:
- consume frozen/read-only packages;
- create published outputs;
- link to package identity/version;
- surface boundary/authority caveats.

May not:
- alter canonical semantics;
- hide constraints in ways that change meaning;
- make presentation fields canonical.

### Search/index/comparison systems

May:
- build derived views;
- rank or group packages as an explicit derived operation;
- link back to source package identity/version.

May not:
- mutate source packages;
- infer supersession unless governed relationship exists;
- make derived priority canonical.

## Adversarial review

### Challenge: Are we overengineering?

Partially yes, if the architecture jumps directly to multiple formats, registry, migrations, and extensibility mechanisms before one package is represented.

Correction:
- Keep the next step to architecture/planning, then hand-authored examples, then smallest representation profile.
- Do not implement multi-format support until a second format has a real need.

### Challenge: Is one simple canonical file enough?

It may be enough operationally for the first implementation, but not constitutionally. The first file format can be a profile. It should not become semantic authority.

Correction:
- Permit one initial profile later, but define it as derived from semantic contracts.

### Challenge: Have concerns been separated too aggressively?

Some separation is necessary because TASK-037 already proved authority leakage risks. However, implementation should not create many separate tools immediately.

Correction:
- Distinguish architectural responsibilities now; consolidate implementation later where safe.
- A single future validator executable could run multiple validation layers, provided findings remain classified by layer.

### Challenge: Could implementation become unnecessarily difficult?

Yes, if every conceptual layer becomes a separate implementation component.

Correction:
- The architecture should require boundary separation, not component proliferation.
- Future implementation may use one codebase/tool for multiple roles if authority boundaries and output classifications remain explicit.

### Challenge: Are assumptions untested?

Yes:
- no concrete ADPM package has been serialized;
- no hand-authored examples exist;
- no compatibility/migration case has occurred;
- no renderer has consumed ADPM;
- no search/index/comparison system has consumed ADPM.

Correction:
- Before implementation, create hand-authored examples and representation specifications; keep implementation deferred until those examples pressure-test the contract.

## Remaining uncertainties

1. Whether one representation profile will suffice for the first several ADPM packages.
2. Whether lifecycle transitions should be represented inside packages, alongside packages, or both.
3. Whether amendments should be separate packages or package relationship records.
4. How much validation can be deterministic versus reviewer-assisted.
5. Whether a future registry/catalog is needed before multiple frozen packages exist.
6. Whether extension points are needed in v1 or should be explicitly deferred.

These uncertainties do not block architecture-only representation/specification planning. They do block implementation if unresolved.

## Recommended direction

Adopt a specification-first semantic contract architecture:

```text
ADPM constitutional specification
  owns semantic meaning, lifecycle, authority, invariants

Semantic representation contract
  defines object/relationship/identity/version/profile obligations without choosing JSON/YAML/etc.

Representation profiles
  define concrete transport forms derived from the contract

Layered validation specifications
  define structural, semantic, lifecycle, governance, compatibility, and renderer-facing checks

Future implementations
  may consolidate tooling but must preserve authority boundaries
```

## Readiness assessment

After this evaluation, BriefForge is ready to begin architecture-only design of:

- representation specifications;
- semantic contract specifications;
- schema architecture;
- validator specifications;
- builder specifications.

BriefForge is not ready to implement:

- serialization formats;
- JSON/YAML/XML files;
- schemas;
- validators;
- builders;
- serializers;
- renderers;
- APIs;
- runtime behavior;
- generated-project changes.

## Next recommended workstream

`TASK-039 ADPM Representation Contract and Validation Specification Planning`

Scope:
- define the architecture of the semantic representation contract and layered validation specifications;
- decide what must be specified before hand-authored examples and implementation planning;
- avoid concrete JSON/YAML/schema implementation.

A smaller alternative is possible:

`TASK-039 ADPM Hand-Authored Package Examples Planning`

But the better next step is the contract/validation specification plan, because examples should be evaluated against a clear representation contract rather than unconstrained prose.
