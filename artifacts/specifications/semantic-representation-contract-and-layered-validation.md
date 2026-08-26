# Semantic Representation Contract and Layered Validation Specification

Date: 2026-07-16
Status: accepted specification
Task: TASK-043
Authority: renderer-independent representation and validation planning subordinate to `CONSTITUTION.md`, accepted ADPM doctrine, TASK-041, and TASK-042

## 1. Purpose

This specification allocates already-accepted BriefForge semantics to an abstract, renderer-independent representation and assigns validation responsibility to explicit authority layers.

It does not select a programming language, record library, schema language, transport format, storage model, API, renderer, interaction runtime, or UI. A future representation profile must derive from this contract. A schema or serialized document may express a profile but may not define the semantics.

The contract preserves:

- Presentation Package as BriefForge's canonical semantic object;
- ADPM as a specialized decision-support Presentation Package lifecycle;
- TASK-041 Presentation Intake, Portable Presentation Material, publication taxonomy, release lifecycle, version axes, and manifest boundary;
- TASK-042 multidimensional statement authority, scoped states, finite prevalidated selection, narrative consistency, transformation sovereignty, and fail-closed fallback;
- Candidate -> Validation Judgment -> Ready;
- rendered artifacts as non-canonical derivatives;
- complete standalone publications and optional consumer embedding;
- upstream sovereignty and the MacroForge financial-semantic deferral.

## 2. Non-duplication and authority rules

1. Existing concepts keep their accepted meanings. This specification allocates them; it does not rename them for novelty.
2. Presentation Brief is the minimum semantic intake contract. `PresentationRequest` may be used as an implementation-facing label only if a future profile maps it explicitly to Presentation Brief rather than creating a second intake concept.
3. Portable Presentation Material is the accepted resolved, portable input boundary. `ResolvedPresentationInput` may be an implementation label only as an explicit profile mapping to that concept.
4. Candidate Presentation Package, Validation Judgment, and Ready Presentation Package remain separate lifecycle objects.
5. Publication Release Record owns BriefForge publication identity and lifecycle. A publication manifest is a derivative projection, not the release authority.
6. Upstream evidence objects remain external semantic authorities. BriefForge records references, bindings, presentation obligations, and compatibility findings; it does not duplicate their domain ontology.
7. Existing Python dataclasses, JSON artifacts, and renderer records are evidence. They are not the semantic contract.
8. Communication Intent remains experimental. Its vocabulary may populate an explicitly authored communication-function dimension, but heuristic derivation is not canonical.
9. Presentation Models remain authoring conveniences that produce a Candidate. They are not archetypes, templates, canonical package subtypes, or representation profiles.

## 3. Abstract semantic object graph

The graph is expressed through identities and typed relationships, not through required nesting.

```text
Presentation Brief
  -> intake disposition
  -> Portable Presentation Material
       -> upstream semantic references and evidence-snapshot bindings
       -> authority declarations and presentation obligations
  -> Candidate Presentation Package
       -> Package Identity
       -> Organizing Purpose
       -> Audience Orientation
       -> Presentation Statements
       -> Encounter/Composition Relations
       -> Scoped Semantic State Assertions
       -> finite Selection Sets, if any
       -> Renderer Requirements and Fallback Obligations
       -> upstream references and traceability bindings
  -> Validation Judgment bundle
  -> Ready Presentation Package
  -> Publication Release Record
       -> generated artifact records
       -> publication lifecycle events
       -> derivative publication manifest projection
  -> renderer compatibility finding
  -> rendered artifact
  -> audit-link conformance finding
  -> semantic artifact conformance finding
```

Arrows denote authority-preserving relationships, not mandatory serialized containment.

### 3.1 Presentation Brief

Represents the TASK-041 minimum intake semantics: audience/use, organizing purpose, scope/non-scope, requested communication outcome, source ownership, evidence snapshot expectations, caveats/obligations, publication mode, and authority to request presentation work.

It is not a query. It cannot authorize BriefForge to acquire data, select an analytical question, create a finding, or infer missing upstream meaning.

Disposition is one of admitted, incomplete, or rejected under TASK-041. Incomplete and rejected outcomes identify missing or violated responsibilities; neither silently manufactures defaults.

### 3.2 Portable Presentation Material

Represents resolved, bounded material suitable for Candidate construction. Its responsibilities are:

- identify material and originating/exporting authority;
- retain the exact upstream semantic and evidence-snapshot bindings needed for reproducibility;
- carry generic typed external references without importing upstream domain ontology;
- declare supplied roles, states, selections, obligations, and authority scopes;
- distinguish source material from BriefForge-authored framing or synthesis;
- record transformations already authorized upstream;
- identify unresolved or incompatible material rather than coercing it.

It is not a second canonical package and not a lossy renderer input.

### 3.3 Candidate Presentation Package

The Candidate is the revisable semantic proposal for one package. A fingerprinted instance may be immutable; conceptual revision creates a replacement Candidate.

The Candidate owns or aggregates the following semantic responsibilities:

- Package Identity;
- Organizing Purpose;
- Audience Orientation;
- Presentation Statements;
- typed Encounter/Composition Relations;
- upstream semantic references and evidence bindings;
- Presentation Obligations;
- Scoped Semantic State Assertions;
- finite Selection Sets where admitted;
- Renderer Requirements and declared fallback obligations;
- traceability relationships to Portable Presentation Material.

This does not imply one monolithic serialized record.

### 3.4 Validation Judgment and Ready Presentation Package

A Validation Judgment identifies:

- the exact Candidate semantic identity/fingerprint assessed;
- validation policy and contract versions;
- each layer actually executed;
- findings with layer, authority, scope, affected identities, severity/blocking consequence, and rationale;
- validity/readiness consequence without governance-approval inference.

A Ready Presentation Package binds one exact Candidate to a successful matching judgment. It does not absorb publication release identity, renderer identity, or generated artifact version.

### 3.5 Publication Release Record and derivatives

The Publication Release Record owns:

- stable publication identity;
- semantic publication version;
- evidence-snapshot reference set;
- Ready package identity/fingerprint;
- release status and lifecycle events;
- release/correction/supersession/withdrawal/staleness declarations;
- renderer and generated-artifact records where artifacts exist.

Renderer version, generated-artifact version, and manifest-projection version remain independent from semantic publication version. A rerender without semantic change does not create a new semantic version. A correction that changes meaning does.

The publication manifest is a minimal derivative discovery/integration projection. AtlasForge or another consumer may catalog or embed it without becoming BriefForge authority and without BriefForge depending on that consumer.

## 4. Core semantic responsibilities

### 4.1 Package Identity

Package identity is stable for one semantic package lineage. It must not be inferred from file path, title, renderer route, or content position. A future profile must express stable identity and the semantic version or lineage relation needed to disambiguate revisions.

### 4.2 Organizing Purpose

Organizing Purpose binds the package's material and defines why it exists, its scope, and its non-scope. Every statement and selectable state must remain compatible with it. It is not a visual heading, template name, or audience segment.

### 4.3 Audience Orientation

Audience semantics answer who must understand or use the package and what relevant literacy, decision context, access, or distribution constraints apply. Audience orientation may affect communication obligations but cannot weaken evidence, caveats, provenance, uncertainty, or authority boundaries.

No global user model, personalization engine, or portal profile is implied.

### 4.4 Presentation Statement

Presentation Statement remains the smallest BriefForge-owned unit of presentation meaning. Its representation must permit these independent dimensions without coercing them into one universal enum:

1. stable statement identity;
2. content or faithful content binding;
3. primary semantic posture plus any attached distinctions: observation, reusable evidence, accepted finding, interpretation, hypothesis, scenario, recommendation, uncertainty, caveat, or personal annotation;
4. scoped authorities: originator, semantic/acceptance authority, evidence authority, exporter/materializer, requestor/transporter, presentation author, presentation validation authority, and publication authority as applicable;
5. communication function: explicitly authored/reviewed orient, summarize, explain, compare, quantify, warn, qualify, trace, conclude, or a future compatible value;
6. attention obligation: primary, secondary, supporting, or discoverable;
7. evidence, value, consistency, upstream-lifecycle, and publication-use state bindings where applicable;
8. encounter/composition relationships;
9. source/evidence/traceability references;
10. attached presentation obligations.

A composite statement must split when constituents differ materially in role, authority, state, or obligation. A statement may carry several attached distinctions, but one label must not imply another dimension.

BriefForge-authored synthesis must trace to source assertions and qualifications and must not increase claim strength, settle conflict, invent ranking, infer causation, create recommendation, or replace exact wording obligations.

### 4.5 Encounter and composition relationships

Relations are typed identity edges. Admitted semantic relationship families are:

- required precedence/order;
- grouping/membership;
- hierarchy/containment for communication organization;
- required co-encounter/proximity;
- bounded alternate path;
- entry/continuation.

They do not imply evidence support, derivation, contradiction, causality, confidence, analytical importance, or authority.

Strict order and hierarchy must be acyclic. Multiple valid paths are permitted. A future profile must not require a total list order where the semantic graph declares only partial order.

Existing `EncounterSemantics.mode` values mix concerns and are not sufficient future representation; no runtime repair is authorized by this specification.

### 4.6 Upstream semantic reference and evidence-snapshot binding

An external reference must support:

- stable reference identity within the package;
- owner and authority scope;
- reference kind without speculative domain fields;
- locator or resolvable retrieval handle where available;
- upstream object identity/version/fingerprint where supplied;
- exact evidence-snapshot binding when material depends on a fixed snapshot;
- owned meaning and limitations;
- relationship to statements, states, selections, and obligations.

A locator is not identity. A fingerprint proves integrity/equality under a defined canonicalization, not truth, authority, or semantic equivalence. Upstream authority must establish equivalence after locator or object change.

### 4.7 Presentation Obligation

An obligation has stable identity, category, normative requirement, owner/authority, scope, and explicit targets. Targets may include package, statement, relation, evidence binding, selection state, renderer requirement, release, or artifact expression where applicable.

One direction of attachment may be canonical in a profile, but validation must prove the complete bidirectional semantic relation. Serializing duplicate links does not create two authorities.

## 5. Identity and reference rules

1. Every referenceable semantic object has stable identity in its declared scope.
2. Identity scope is explicit: package-local, release-lineage, project-global, or external-authority scope.
3. References target identities plus an explicit relationship kind; they do not target array indexes, object positions, CSS selectors, DOM paths, or file offsets.
4. All internal references must resolve within the represented graph or an explicitly declared external boundary.
5. Duplicate identities in one scope block structural/semantic admission.
6. A target kind mismatch blocks semantic validation even when an identifier string exists.
7. Strict relation cycles block readiness; non-ordering relatedness does not.
8. Versioned replacement uses explicit lineage, supersession, or correction relationships; identity reuse must not conceal changed meaning.
9. Deep links derive from stable semantic identities. They are renderer expressions, not semantic identities themselves.
10. Integrity hashes, semantic fingerprints, release identities, renderer identities, and artifact identities are separate identifiers with separate owners.

## 6. Scoped semantic states

No universal `status` field is permitted. A state assertion must identify:

- state assertion identity;
- state family;
- exact subject identity and subject kind;
- value from the applicable vocabulary;
- declaring/detecting authority;
- effective evidence snapshot or lifecycle time where relevant;
- rationale or reason when required;
- affected obligations and blocking consequence;
- resolution authority/path where unresolved or conflicting.

### 6.1 Evidence state

Evidence state is scoped to an evidence reference or snapshot and separates:

- availability: available, partial, missing, unavailable;
- integrity: verified, unverified, mismatch;
- authority acceptance: accepted by declared authority, not accepted, ambiguous, unauthorized;
- exact upstream review state;
- freshness: current, stale, unknown, not applicable;
- active use: active or withdrawn.

### 6.2 Value state

Value state is scoped to one materialized value and distinguishes:

- present;
- explicit zero;
- missing/not provided;
- unavailable;
- not applicable;
- suppressed/withheld;
- unresolved;
- invalid.

A value-bearing representation must preserve the state independently from the lexical payload. Zero, false, empty collection, and empty string are not automatically missing. Suppressed values preserve suppression authority/reason when distribution permits. Renderers cannot impute or substitute.

### 6.3 Consistency state

Consistency is a finding over identified material: consistent, conflicting, unresolved/indeterminate, invalid under a named contract, or not checked. Conflict declarations identify kind, affected material, detection authority, resolution authority, and blocking consequence.

Explicit disagreement may be valid. Accidental contradiction, broken reference consistency, undeclared incompatibility, or authority ambiguity blocks readiness. BriefForge may present a conflict but may not choose a winner.

### 6.4 Lifecycle state

Upstream lifecycle, Candidate/Judgment/Ready, Publication Release Record lifecycle, generated-artifact state, and manifest generation state remain separate. A state event never mutates historical identity into a different fact. Stale or withdrawn current-use state does not erase a historical release; artifact corruption does not invalidate semantic readiness.

## 7. Finite selection representation

A Selection Set represents conditionally admitted declared/prevalidated presentation-state choice. It is not a query, filter, parameterized computation, interval, wildcard, or implied Cartesian product.

A Selection Set must express:

- stable selection-set identity;
- upstream/semantic publication authority;
- closed enumerated option identities;
- one authority-declared default option;
- for every option, an exact complete Presentation State Projection;
- exact evidence-snapshot bindings;
- explicit included/active statement, relation, exhibit/material, reference, obligation, title, purpose, scope, caveat, uncertainty, provenance, and narrative bindings;
- independent validation identity for every state;
- deterministic static fallback identity and semantics;
- deep-link/copy identity requirements;
- version-change rule when options, default, evidence, narratives, or obligations change.

A Presentation State Projection references existing semantic units and state-specific authored variants; it does not run transformations. Every valid option must form a coherent publication. Unknown option, undeclared combination, missing evidence binding, stale narrative, detached obligation, or required recalculation blocks selector publication. A separately valid fixed-state publication may remain possible.

Selection-state identity is semantic and must be visible/auditable in any native or deep-linked view. A renderer may express a selected state; it may not choose the substantive default or invent combinations.

## 8. Renderer requirements, capabilities, and fallback

### 8.1 Renderer Requirement

A Renderer Requirement is a package-owned semantic obligation. It must express:

- requirement identity;
- semantic subject identities;
- required semantic input/relationship/state to preserve;
- required expression or transformation class, if any;
- admitted interaction class, if any;
- narrative/obligation-preservation constraints;
- accessibility, standalone, deep-link, or scoped-style obligations where semantically required;
- whether the requirement is mandatory or an explicitly optional enhancement;
- accepted fallback strategy identity/semantics;
- failure consequence.

A requirement must not prescribe HTML elements, CSS classes, coordinates, component libraries, templates, or a serialization layout.

### 8.2 Renderer Capability Declaration

A renderer capability is a downstream declaration tied to stable renderer identity and version. It declares verified support for named semantic requirements, expression/transformation classes, admitted interactions, state/narrative behavior, obligation preservation, fallback, accessibility, standalone operation, and evidence of verification.

The current `package_features` declarations are narrow implementation evidence and insufficient for this future contract. Capability declaration does not prove successful output.

### 8.3 Compatibility and fallback plan

Compatibility compares one exact Ready package's requirements against one exact renderer identity/version and produces findings plus a deterministic expression/fallback plan. It does not alter semantics.

Fallback order remains:

1. verified native expression;
2. prevalidated semantically equivalent expression;
3. deterministic complete static representation;
4. explicit unsupported/unavailable expression only when authorized and non-misleading;
5. fail closed.

Silent best effort is prohibited. Required content or obligations cannot be dropped. Zero cannot become missing; conflicts cannot be flattened; selection defaults cannot be guessed; evidence cannot be refreshed; analytical values cannot be recalculated; stale or withdrawn material cannot be presented as current.

## 9. Traceability versus semantic conformance

Traceability answers whether identities and relationships permit an auditor to follow:

```text
source/evidence snapshot
-> Portable Presentation Material
-> statement/state/obligation
-> Candidate and Judgment
-> Ready package
-> Publication Release Record
-> renderer identity/version
-> artifact identity/version
-> manifest projection
```

Traceability proves link continuity, declared ownership, and retrievability where supported. Integrity metadata can prove byte-level equality under a rule. Neither proves truth, authority, narrative faithfulness, or semantic preservation.

Semantic conformance answers whether represented or rendered meaning preserves the authorized roles, values, states, relationships, authority, scope, claim strength, encounter obligations, selection state, caveats, uncertainty, provenance, and fallback semantics.

Therefore:

- traceability is necessary for substantive material;
- traceability can pass while semantic conformance fails;
- semantic conformance requires traceability where the obligation demands it;
- current rendered-artifact conformance is audit-link conformance only;
- future semantic artifact conformance must inspect or compare semantic expression against an authorized transformation/fallback plan and exact renderer identity/version;
- no single boolean may collapse audit linkage and semantic conformance findings.

## 10. Representation-profile boundary

The semantic representation contract defines conceptual responsibilities, relationships, invariants, authority, and allowed state vocabularies. It does not define physical field order, nesting, null syntax, reference encoding, scalar syntax, extension container syntax, or canonical byte generation.

A Representation Profile is a named, versioned mapping from every required semantic responsibility to one concrete abstract record/graph shape. It may decide:

- which relations are represented by containment versus identity reference;
- canonical direction for bidirectional semantic relationships;
- required/optional profile properties;
- explicit absence/state encoding;
- extension namespaces;
- ordering and canonicalization needed for deterministic fingerprints;
- profile-level structural constraints;
- transport mappings that may be derived later.

A profile may not:

- redefine semantic roles or authority;
- merge independent state dimensions;
- convert absence into transport null without semantic state;
- introduce requirements solely because JSON, YAML, XML, Python, a database, or a renderer makes them convenient;
- use renderer input shape as the package ontology;
- make Markdown canonical;
- import speculative financial-domain fields.

ADPM semantic version and representation-profile version remain independent. Transport serialization version, if needed, is also separate. A semantic change may require a new semantic version even if profile syntax is stable; a lossless profile revision may leave semantic version unchanged.

## 11. Layered validation architecture

Validation findings are records with: finding identity, layer, policy/contract identity, executing authority, subject identities, code/category, rationale, evidence, blocking consequence, and remediation/resolution authority. Tools may consolidate execution, but not authority.

### 11.1 Layer 0 — intake admission

- Subject: Presentation Brief.
- Authority owner: BriefForge presentation-intake authority, with upstream/requestor authority for supplied meaning.
- Checks: completeness, source/authority declarations, scope, non-scope, evidence expectation, publication mode, and prohibited analytical requests.
- Result: admitted, incomplete, or rejected; not Candidate validity.

### 11.2 Layer 1 — profile structural validation

- Subject: one representation-profile instance.
- Authority owner: the named Representation Profile contract.
- Checks: record shape, required properties, scalar/container forms, identity syntax, extension placement, canonicalization prerequisites, and basic reference shape.
- Result: structurally valid/invalid under that profile.
- Prohibition: structural success does not establish semantic validity, readiness, upstream truth, or governance approval.

### 11.3 Layer 2 — semantic contract validation

- Subject: reconstructed semantic object graph.
- Authority owner: BriefForge semantic contract, plus declared upstream authorities for upstream-owned assertions.
- Checks: semantic completeness, independent dimensions, authority scopes, referential integrity and target kinds, obligation attachment, state distinctions, evidence bindings, role/claim-strength consistency, composition acyclicity, selection closure, narrative consistency, superlative universe, renderer requirements, and fallback semantics.
- Result: semantic findings over the Candidate; no publication approval.

### 11.4 Layer 3 — lifecycle/readiness validation

- Subject: Candidate, Judgment, Ready transition, and later release events.
- Authority owner: BriefForge lifecycle policy.
- Checks: judgment belongs to exact Candidate identity/fingerprint and policy; all blocking required layers passed; promotion is immutable; release event/version rules hold; corrected/superseded/withdrawn/stale states do not rewrite history.
- Result: readiness or lifecycle-event admissibility.

### 11.5 Layer 4 — governance approval

- Subject: disposition or authorization requiring human/project authority.
- Authority owner: declared decision/publication/governance authority, not validator code.
- Checks: approval boundaries, decision authority, release authority, distribution authorization, unresolved blockers, and explicit non-authorization.
- Result: governance decision record. It must not be inferred from semantic validity, confidence, priority, or readiness.

### 11.6 Layer 5 — renderer compatibility and plan validation

- Subject: exact Ready package requirements versus exact renderer identity/version/capability evidence.
- Authority owner: BriefForge renderer-adapter contract for compatibility; renderer owner for truthful capability declaration.
- Checks: all required semantics, interactions, narrative states, obligation preservation, standalone/accessibility requirements, and fallback strategies are declared and verified; expression plan is deterministic.
- Result: compatible with a named plan, or incompatible. No rendering success is implied.

### 11.7 Layer 6 — output conformance

Two finding families remain explicit:

1. audit-link conformance: package/release identity, semantic fingerprint, validation policy, renderer identity/version, artifact identity/version, and manifest linkage;
2. semantic artifact conformance: actual output preserves authorized values, roles, states, order/proximity, selection identity, narrative, caveats, uncertainty, provenance, obligations, and approved fallback plan.

Authority owner: BriefForge publication/output conformance specification, using renderer-generated evidence without granting renderer semantic authority.

A pass in audit linkage cannot mask a semantic artifact failure.

## 12. Cross-layer invariants

1. Semantic reconstruction invariant: every conforming profile instance reconstructs one unambiguous semantic graph.
2. Round-trip invariant: profile -> semantic graph -> same profile preserves semantic equality and identity, excluding explicitly non-semantic transport metadata.
3. Authority invariant: no lower layer manufactures authority owned by another layer.
4. Identity invariant: Candidate, Judgment, Ready, release, renderer, artifact, and manifest identities remain distinguishable and correctly linked.
5. Fingerprint invariant: the semantic fingerprint covers declared semantic substance only under a named canonicalization and excludes renderer/artifact mechanics.
6. Reference invariant: every internal edge resolves to the correct target kind; external edges preserve owner and snapshot semantics.
7. Obligation invariant: every applicable obligation is reachable from and validated against every affected subject/state/expression.
8. State invariant: explicit zero, missing, unavailable, not applicable, suppressed, unresolved, invalid, conflicting, stale, and withdrawn remain distinguishable end-to-end.
9. Composition invariant: strict order/hierarchy is acyclic; renderers preserve semantic partial order and proximity constraints.
10. Selection closure invariant: every admitted option has a complete, independently valid narrative and evidence binding; no implied combination exists.
11. Narrative invariant: claim strength, title, scope, values, periods, sample sizes, rankings, caveats, uncertainty, and provenance match each fixed/selectable state.
12. Transformation invariant: every non-mechanical transformation is preauthorized and included in compatibility/output conformance; geometry and encoding do not create semantic authority.
13. Fallback invariant: a fallback is predeclared and semantically complete for required obligations or publication fails closed.
14. Traceability invariant: substantive material traces to authority and evidence, but traceability success is never substituted for semantic conformance.
15. Version invariant: semantic, profile, transport, renderer, artifact, and manifest versions change only under their owning rules.
16. Standalone invariant: optional embedding cannot be necessary to understand, navigate within, inspect, or audit the complete publication.
17. Scope invariant: AtlasForge catalog/discovery state, live upstream state, and financial-domain ontology remain outside the package contract.

## 13. Worked semantic traces

### 13.1 Accepted finding with caveat and evidence

1. Upstream exports an accepted finding and reusable evidence with owner, acceptance scope, snapshot fingerprint, and caveat.
2. Portable Presentation Material retains both roles, authorities, evidence binding, and caveat attachment.
3. Candidate creates a finding statement, evidence reference, caveat statement/obligation, and required co-encounter relation.
4. Semantic validation verifies authority, reference targets, claim strength, and attachment.
5. Readiness binds the exact Candidate fingerprint.
6. Renderer compatibility requires finding expression, evidence inspection, caveat proximity, and static fallback.
7. Artifact audit links pass only if identities match. Semantic conformance separately fails if prose strengthens the finding or the caveat is detached.

### 13.2 Explicit zero versus missing value

1. Upstream supplies one value with state `present/explicit zero` and another with `missing/not provided`.
2. Portable material retains both state assertions and authorities.
3. Candidate references the zero as data and the missing state as absence; no placeholder value is invented.
4. Structural validation confirms both encodings exist under the profile; semantic validation confirms they remain distinct.
5. A renderer that blanks both may retain correct audit identifiers yet fails semantic artifact conformance.
6. An approved fallback must render zero and the authorized missing expression distinctly.

### 13.3 Finite prevalidated selection

1. Upstream declares three exact accepted scenario states with distinct identities and evidence snapshots; publication authority declares one default.
2. Candidate contains one Selection Set with three complete projections. Each projection binds title, purpose, statements, assumptions, values, caveats, provenance, and obligations.
3. Semantic validation checks each state independently and cross-state consistency; no fourth combination is inferred.
4. Renderer compatibility checks state identity visibility, deep links, native selection, and complete static fallback.
5. If native selection is unsupported, the approved fallback enumerates three coherent fixed states. Choosing the first option silently is prohibited.
6. Changing one option or the default requires a new judgment, Ready fingerprint, semantic publication version, and release.

### 13.4 TASK-039-style analytical publication

1. InsightForge owns question selection and interpretation; KnowledgeForge owns accepted coefficients, methods, provenance, and validation state.
2. Portable material preserves those separate authorities and the fixed source fixture fingerprint.
3. Statements represent question/orientation, accepted findings, evidence, methodology, caveats, and provenance as independent dimensions rather than overloaded encounter modes.
4. The term `strongest` is valid only with explicit upstream comparison universe, exclusions, method, and evidence snapshot.
5. A proposed country selector or date slider fails admission because it requires new evidence or recalculation.
6. Static HTML/SVG may remain derivative expressions. Correct fingerprint metadata does not prove that coefficients, caveats, or thesis were rendered faithfully.

### 13.5 Rerender, correction, and withdrawal

1. Release 1.0.0 binds Ready fingerprint A and artifact version H1 from renderer R1.
2. A style-only rerender using renderer R2 produces H2; semantic version remains 1.0.0, artifact and renderer versions change, and both remain traceable.
3. A corrected coefficient changes semantic substance, producing Candidate/Ready fingerprint B and semantic release 1.0.1 with correction and supersession links.
4. Later withdrawal creates a lifecycle event; it does not erase 1.0.0 or 1.0.1.
5. Regenerating a manifest cannot make a withdrawn release active.

## 14. Adversarial proposal dispositions

| Proposal | Disposition | Reason |
| --- | --- | --- |
| Use current Python dataclasses as the future semantic contract. | Rejected | They omit accepted TASK-041/TASK-042 semantics and are implementation evidence only. |
| Add one `type` field covering role, function, order, and state. | Rejected | It collapses independent authorities and cannot represent composite obligations safely. |
| Introduce `PresentationRequest` beside Presentation Brief. | Rejected as a new concept; accepted only as a profile alias | Duplicate intake semantics would create drift. |
| Introduce `ResolvedPresentationInput` beside Portable Presentation Material. | Rejected as a new concept; accepted only as a profile alias | TASK-041 already owns the responsibility. |
| Store references as JSON Pointer/array indexes. | Rejected | Transport paths are unstable and cannot define semantic identity. |
| Make every semantic edge bidirectionally serialized. | Deferred to profile | Semantic bidirectional consistency is required, but duplicating storage may create two authorities. |
| Treat integrity fingerprints as evidence acceptance. | Rejected | Integrity is not truth or authority. |
| Treat current rendered-artifact conformance as semantic conformance. | Rejected | It checks audit linkage only. |
| Let a renderer infer communication function from keywords. | Rejected as canonical; existing experiment remains evidence | TASK-042 requires authored/reviewed function before authority-sensitive use. |
| Let a renderer select extrema and write a caption. | Rejected unless exact transformation and claim are upstream-authorized and prevalidated | Otherwise the renderer creates analysis/interpretation. |
| Define a generic `null` for all absent states. | Rejected | Missing, unavailable, not applicable, suppressed, unresolved, and invalid differ semantically. |
| Infer all combinations from independent selector dimensions. | Rejected | Selection requires a closed enumerated set of complete states. |
| Embed renderer capability flags in each statement. | Rejected | Package requirements and renderer capabilities have different owners. |
| Use one validator that returns one pass/fail. | Rejected as authority model | One tool may orchestrate, but layer findings and authorities remain explicit. |
| Materialize multiple JSON/YAML/XML profiles immediately. | Rejected | No measured need; it creates uncontrolled multi-format drift. |
| Add fiscal-period/company/security fields for future reports. | Deferred/prohibited now | MacroForge must stabilize those semantics first; generic typed external references suffice. |
| Promote Communication Intent as canonical while defining the profile. | Deferred | Its status remains experimental and no profile convenience overrides that gate. |
| Build the golden corpus before choosing a profile. | Rejected | Examples would accidentally define syntax and semantics without an accepted mapping contract. |
| Use TASK-039 JSON artifacts unchanged as golden examples. | Rejected for automatic adoption | They are valuable source cases but reflect the current incomplete runtime and a known renderer-audit table inconsistency. |
| Make AtlasForge manifest fields canonical package fields. | Rejected | Manifest projection and consumer catalog state are downstream derivatives. |

## 15. Golden-corpus gate

Verdict: semantic cases are sufficiently defined to design a corpus, but corpus materialization is NOT YET AUTHORIZED.

Preconditions before creating corpus files:

1. accept one initial Representation Profile mapping every mandatory semantic responsibility;
2. define profile identity/version and deterministic canonicalization/fingerprint rules;
3. define expected structural and semantic findings separately;
4. define extension and unknown-field behavior;
5. define semantic equality/round-trip expectations;
6. define credential redaction and external-reference fixture rules;
7. select positive and adversarial cases from TASK-039, ADPM, publication lifecycle, explicit states, conflict, selection, renderer fallback, and AtlasForge manifest boundaries;
8. prove that corpus examples do not make one renderer or transport canonical.

Minimum future corpus classes:

- minimal fixed-evidence publication;
- ADPM package preserving all mandatory decision relationships;
- explicit zero/missing/unavailable/not-applicable/suppressed/unresolved/invalid cases;
- accepted conflict versus invalid inconsistency;
- finite selection with complete state narratives and static fallback;
- renderer incompatibility and approved fallback;
- audit-link pass plus semantic-conformance fail;
- correction/rerender/supersession/withdrawal/staleness lifecycle;
- generic external reference demonstrating financial-semantic deferral;
- malformed authority, dangling reference, cycle, detached caveat, unknown selector state, and speculative domain-field rejections.

## 16. Exact next task

Recommended successor:

`TASK-044 — Initial Representation Profile and Golden Corpus Acceptance Specification`

Scope:

- define exactly one renderer-independent initial Representation Profile from this semantic contract;
- map every mandatory object, relationship, state, identity, extension, and finding without choosing renderer inputs;
- specify deterministic canonicalization and semantic equality;
- specify, but do not yet implement, the golden corpus case inventory and expected layer findings;
- issue the implementation gate for profile schema/serializer/validator/corpus work.

Non-goals:

- no schema or transport implementation;
- no validator, serializer, builder, runtime, renderer, fixture, or golden-corpus file creation;
- no second profile or multi-format plan;
- no financial-domain semantics;
- no reopening TASK-041/TASK-042 absent demonstrated incoherence.

This is correctly bounded because representation allocation and validation authority are now decided, while syntax, canonicalization, and test vectors still require one coherent profile before implementation can be safe.

## 17. Final gate

CLEAR TO PROCEED to TASK-044 as specified above.

This verdict authorizes specification of one representation profile and corpus acceptance plan only. It does not authorize implementation.
