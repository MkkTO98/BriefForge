# Versioned Representative Paired Terminal Capability

Version: 1.0.0
Date: 2026-08-01
Status: accepted design specification by TASK-066; not implemented
Decision: `CREATE VERSIONED TERMINAL CAPABILITY`

## 1. Layered evidence model

The following must never be conflated:

1. **Abstract BCRP representability**: eleven core kinds can encode the semantic graph under generic BCRP validation.
2. **Profile admission**: a named strict profile admits one exact Release shape and bounded cardinalities.
3. **Projection preservation**: a named schema and projector losslessly preserve every admitted identity, field, edge and order.
4. **Renderer compatibility**: a named renderer consumes only that projection and realizes the fixed output model.
5. **Complete terminal-route compatibility**: independent conformance and the existing lifecycle/Manifest/distribution chain accept exact bound evidence.

Each layer requires its own independently persisted evidence. Success at a later layer cannot repair failure at an earlier layer.

## 2. Capability identities

- Profile: `briefforge:representative-paired-terminal-static-html-profile:3.0.0`
- Projection schema: `briefforge:representative-paired-static-html-projection-schema:1.0.0`
- Projection implementation: `briefforge_paired_terminal_profile.projection:1.0.0`
- Renderer: `briefforge:representative-paired-static-html-renderer:1.0.0`
- Invocation policy: `briefforge-paired-terminal-controlled-renderer-invocation-policy:1.0.0`
- Invocation evidence: `briefforge:paired-terminal-controlled-renderer-invocation-evidence:1.0.0`
- Invocation authorization class: `briefforge_paired_terminal_profile.controlled_invocation.PairedTerminalRendererInvocationAuthorization`
- Conformance profile: `briefforge:representative-paired-static-html-conformance-profile:1.0.0`
- Assessor implementation: `briefforge_paired_terminal_profile.semantic_conformance:1.0.0`
- Conformance policy: `briefforge-paired-terminal-semantic-conformance-assessment-policy:1.0.0`
- Conformance evidence: `briefforge:paired-terminal-semantic-artifact-conformance-evidence:1.0.0`
- Conformance authorization class: `briefforge_paired_terminal_profile.semantic_conformance.PairedTerminalSemanticArtifactConformanceAuthorization`
- Manifest policy: `briefforge-paired-terminal-publication-manifest-admission-policy:3.0.0`
- Manifest profile: `briefforge:paired-terminal-publication-manifest-admission-profile:3.0.0`
- Manifest validation contract: `briefforge:paired-terminal-publication-manifest-admission-authority:3.0.0`
- Manifest implementation: `briefforge_paired_terminal_profile.manifest_admission:1.0.0`
- Manifest authorization class: existing exact `briefforge.publication_manifest_admission.PublicationManifestAuthorization`

All identities and versions are exact literals. There is no range, compatible-major selection, alias, `latest`, fallback, registry or caller-selected implementation.

The capability uses the existing BCRP profile family and all eleven current record kinds. It adds no core kind and changes no core canonicalization rule.

## 3. Accepted inputs and output

Inputs:

- one independently verified immutable active Publication Release;
- complete lifecycle scope;
- one fresh Candidate/Judgment/Ready chain from which the immutable Release was constructed and which that Release transitively binds;
- content authorities and unchanged TASK-062 operational-authority inventory;
- exact capability declaration and compatibility Plan for the v3 tuple;
- one exact invocation authorization;
- semantic objects admitted by the strict schema below.

Output:

- exactly one standalone UTF-8 static HTML file;
- exactly one fixed five-column paired-comparison table;
- no script, network resource, external asset or auxiliary file;
- deterministic authored hierarchy and encounter order.

The generic profile admits 1..16 paired rows. An instance-specific editorial gate may narrow a publication to an exact row count; TASK-064 requires exactly seven.

## 4. Strict versioned schemas

Schemas are exact-field, reject-unknown, immutable DTO definitions. They import neither renderer nor BCRP verifiers.

### 4.1 Root projection

`PairedEditorialProjection` contains:

- schema identity/version;
- profile identity/version;
- Release identity/fingerprint;
- lifecycle-scope fingerprint;
- Plan identity/fingerprint;
- capability-declaration identity/fingerprint;
- ordered sections;
- statements;
- one `PairedTable`;
- qualifications;
- provenance attachments;
- obligations;
- evidence snapshots;
- external references;
- content authorities;
- renderer requirements/mappings;
- content-closure fingerprint;
- projection fingerprint.

### 4.2 Sections and statements

`Section`: identity, title, order, ordered `children` whose closed tagged union is section, statement, table, provenance or obligation reference.

`Statement`: identity, role, exact authored text, authority reference and optional structured display classification. Each statement occurs exactly once in composition.

Bounds:

- sections: 2..8;
- total statements: 2..76;
- children per section: 1..32;
- hierarchy: exact depth two for this profile; one root and ordered leaves;
- text field: existing accepted UTF-8 byte bound, maximum 4096 bytes.

### 4.3 Qualification relations

`QualificationEdge`: identity, kind fixed to `limits-target`, source statement reference, target reference from closed union {statement, paired value, paired table}, declared target order, authority reference.

Rules:

- 1..27 edges;
- at most 3 targets per source;
- source may repeat;
- uniqueness is exact `(kind, source_ref, target_ref)`;
- target order is contiguous and deterministic per source;
- no transitive substitution and no parent/root substitute;
- every caveat/uncertainty source has at least one edge;
- all references resolve within the same projection.

### 4.4 Obligations

`Obligation`: identity, closed kind, exact ordered target references, authority reference and authored placement reference.

Closed kinds:

- `preserve-source-meaning`;
- `source-display`;
- `qualification-display`;
- `exclusion-display`;
- `future-work-language`.

Bounds: 1..16 obligations; 1..82 targets each. Target identity and order are exact and non-transitive.

### 4.5 Provenance

`Provenance`: identity, citation, authority reference, optional source commit, optional source-snapshot identity, optional source locator, ordered package identities, exact ordered target references, target rule and authored placement reference.

Bounds:

- 1..16 provenance objects;
- 1..92 targets each;
- 0..2 package identities;
- commit/snapshot/locator combinations follow a closed profile validation table, not free-form inference.

Source-level and row-level provenance remain distinct identities. Citation prose is not a substitute for target topology.

### 4.6 Paired values

`PairedValue` contains:

- identity;
- exact integer coefficient and scale;
- `value_state`, fixed to `present` for this capability;
- exact lexical representation;
- transformation identity;
- transformation state, exactly `raw` or `first_difference`;
- aligned period;
- aligned count;
- unit reference;
- semantic-type reference;
- source reference;
- authority reference;
- method reference;
- package identity.

Rules:

- exactly two values per paired row, maximum 32 total;
- scale remains 0..18;
- value state is exactly `present`; absent, withheld, null and approximate states are rejected;
- lexical representation parses exactly to coefficient/scale without binary floating point, rounding or normalization;
- leading zeroes are valid when required by the source lexical contract;
- no NaN, infinity, approximation substitution or sign/precision drift;
- metadata is displayed state, not permission to recompute analysis.

### 4.7 Paired table and rows

`PairedTable`: identity, purpose reference, exact ordered column identities/headings, ordered rows and authority reference.

The only column contract is:

1. `column:relationship-case` — `Relationship case`
2. `column:raw-pearson-coefficient` — `Raw Pearson coefficient`
3. `column:raw-state` — `Raw state`
4. `column:first-difference-pearson-coefficient` — `First-difference Pearson coefficient`
5. `column:first-difference-state` — `First-difference state`

`PairedRow`: identity, contiguous order, relationship identity, source-authored relationship label, row statement reference, raw value reference, first-difference value reference, classification reference, evidence-role reference, qualification references and provenance references.

Rules:

- one table exactly;
- 1..16 rows generically;
- unique relationship and row identities;
- exact all-value consumption once each;
- each row has one raw and one first-difference value for the same relationship;
- stable order is authored order, never value/sign/magnitude sort;
- no value-slot identity may substitute for row identity;
- row support must resolve to the same row/value closure.

## 5. Capacity derivation and overfitting boundary

Frozen maxima are:

- sections 8, rows 16, values 32, obligation/provenance object counts 16 and decimal scale 18: retained accepted TASK-062 envelopes already sufficient for the new contract;
- statements 76, children per section 32, qualification edges 27, targets per qualification source 3, obligation targets 82, provenance targets 92 and package refs 2: exact demonstrated TASK-064 minima, with zero operational headroom because no broader accepted evidence or policy justifies more.

The exact-frontier limits risk requiring a later version for a larger document. That cost is preferred to inventing reusable capacity policy from one pilot. Source neutrality comes from generic identity, field and topology rules—not from unsupported numerical headroom. Production code may encode these bounds but never T-039/TASK-064/TASK-065 identities, coefficients, periods, counts, wording or domain categories. Any raised frontier requires a later decision with independent evidence.

## 6. Profile admission

Admission order:

1. verify persisted Release bytes/fingerprint and complete lifecycle scope;
2. prove current active Release without ambiguity;
3. verify Candidate/Judgment/Ready/Release fingerprint chain;
4. verify exact v3 profile and authority inventories;
5. enforce identity uniqueness and reference closure;
6. enforce section/statement composition and bounds;
7. enforce paired-table/value closure;
8. enforce qualification topology;
9. enforce provenance and obligation attachments;
10. enforce no operational-authority display;
11. verify renderer requirements and exact capability tuple;
12. emit structured findings and immutable admission fingerprint.

No repair, compression, inference, fallback or renderer call occurs during admission.

## 7. Projection behavior

The projector consumes only independently admitted immutable Release semantics and exact v3 Plan/capability bindings. It:

- performs no editorial summarization or analytical interpretation;
- consumes every admitted semantic identity and mapping exactly once;
- preserves authored text, hierarchy, order, lexical decimals, row pairs, metadata and all directed edges;
- rejects missing, duplicate, contradictory, stale or unconsumed mappings;
- computes `content_closure_fingerprint` over canonical semantic input and mapping trace;
- computes `projection_fingerprint` over every schema field in deterministic key/list order;
- imports no renderer and performs no network/database/environment lookup.

Evidence requirement: persisted projection, mapping trace, source closure, all exact upstream fingerprints and an independent reload verification.

## 8. Renderer behavior

The renderer imports only immutable v1 paired projection DTOs. It:

- supports only standalone UTF-8 static HTML;
- emits fixed title/content hierarchy in authored order;
- emits exactly one table with the five fixed headings;
- emits exactly one `<tr>` for each `PairedRow`;
- places relationship label/identity, exact raw lexical coefficient, verified `present` value state plus raw transformation state, exact first-difference lexical coefficient and verified `present` value state plus first-difference transformation state in that row;
- includes period and aligned count in each state cell;
- realizes classification, evidence role, qualifications and provenance as deterministic row-adjacent support keyed by stable identities;
- realizes obligations/provenance at their exact authored section destination;
- HTML-escapes all semantic text and identifiers;
- never parses decimals through float, rounds, computes, follows sources, sorts by values or infers semantics.

It accepts no template, callable, module path, executable path, environment-selected option or fallback. It writes one declared regular file inside a bounded output directory.

Evidence requirement: exact renderer source identity/digest, two independent byte-identical invocations, bounded inventory and invocation evidence. Renderer completion does not establish semantic conformance.

## 9. Independent conformance

The assessor has a distinct identity/source closure and must not call the renderer, reuse HTML fragments or derive expectations from renderer output.

It independently reconstructs expected semantics from verified Release and v3 profile, parses persisted HTML, and verifies:

- one table, exact five headings and exact row count/order;
- one row per relationship with exact lexical values, `present` value states, transformation states, periods, counts and identities;
- all required statements, qualifications, provenance, exclusions and obligations at governed destinations;
- no extra rows, tables, coefficients, claims, hidden semantic text or displayed operational authority;
- safe HTML and no executable/external content;
- exact artifact/projection/renderer/invocation bindings.

Evidence requirement: independent findings, source digest, authorization and cross-bound fingerprints. Conformance still does not create Manifest or distribution authority.

## 10. Determinism and immutable identity

Canonical serialization is UTF-8 JSON, sorted object keys, preserved array order, LF line endings, no insignificant whitespace, normalized decimal components without changing source lexical fields, and SHA-256 over exact bytes under the existing accepted digest policy.

Every persisted layer binds its exact identity, version, implementation digest, input fingerprints and payload digest. Any field, order, byte, identity or version change creates a different fingerprint and invalidates downstream bindings.

## 11. Version dispatch

### Exact selector architecture

The only existing production file TASK-067 may edit is:

`src/briefforge_terminal_profile/manifest_admission.py`

Its public selector already receives all three concrete authorizations and reads the persisted Manifest validation contract before entering a verifier. TASK-067 adds one deferred import and one exact branch there; it does not edit `src/briefforge/publication_distribution_delivery.py`, any TASK-062 profile/schema/projector/renderer, or any historical verifier.

The new accepted tuple is exactly:

- `type(invocation_authorization) is briefforge_paired_terminal_profile.controlled_invocation.PairedTerminalRendererInvocationAuthorization`;
- `type(conformance_authorization) is briefforge_paired_terminal_profile.semantic_conformance.PairedTerminalSemanticArtifactConformanceAuthorization`;
- `type(authorization) is briefforge.publication_manifest_admission.PublicationManifestAuthorization`;
- persisted validation contract equals `briefforge:paired-terminal-publication-manifest-admission-authority:3.0.0`.

That branch alone calls `briefforge_paired_terminal_profile.manifest_admission.verify_persisted_paired_terminal_publication_manifest`. The eligibility selector similarly delegates only when the verified Manifest carries that exact validation contract. Historical v1, representative-v2 and TASK-062 terminal-v2 branches remain textually and behaviorally unchanged.

The paired Manifest's atomic tuple additionally binds exact profile/schema/projection/renderer/assessor identities, versions and implementation digests plus invocation/conformance authorization and evidence fingerprints named in §2.

### Source-closure truth

Before the one existing selector file is edited, TASK-067 must archive its exact pre-change bytes, byte length and SHA-256 in a new immutable successor source-closure artifact. After the edit it records a fresh active byte length and digest. The pre-change digest remains labeled historical; the active digest is never substituted into TASK-062 evidence, and no old digest is attributed to changed bytes.

`src/briefforge/publication_distribution_delivery.py` remains byte-identical, so TASK-062's `_ACTIVE_DELIVERY_DIGEST` continues to verify truthfully. Existing archived `src/briefforge/**` closure paths and all old Manifest validation contracts remain unchanged.

Reject unknown, partial, mixed, subclassed, duck-typed or cross-version tuples before any verifier is entered. Exhaustively test the cross-product. No dynamic registry, import string, plugin, semantic-version range, compatibility guessing, `latest`, fallback or environment switch.

## 12. Backward compatibility and migration

- TASK-060, TASK-062, TASK-063 and TASK-056 evidence retains original meaning and verification behavior.
- Historical projections and HTML golden artifacts remain byte-identical.
- Persisted historical evidence reloads only under its original tuple.
- There is no migration or reinterpretation of old records.
- Capabilities coexist; no deprecation is scheduled.
- Future retirement requires a separate decision and cannot make historical evidence unverifiable.

## 13. Failure classifications

Failures are classified separately as:

- Release/lifecycle authority;
- profile identity/version;
- schema/field/cardinality;
- identity/reference closure;
- relation topology;
- provenance/obligation attachment;
- value lexical/metadata;
- paired-table closure;
- projection consumption/drift;
- renderer identity/invocation;
- deterministic output;
- semantic conformance;
- cross-version dispatch;
- filesystem/security;
- environment/tooling;
- governance/authorization.

A denial or absent authority is not a renderer or technical failure. No failed layer emits usable downstream evidence.

## 14. Adversarial acceptance criteria

At minimum prove rejection of:

- 77 statements, 33 children, 17 rows, 33 values, 28 relations, 4 targets from one qualifier, 83 obligation targets, 93 provenance targets or 3 package refs;
- duplicate/gapped row order, duplicate relationships, missing/orphaned/reused/cross-paired values, raw/raw or difference/difference pairs;
- wrong or missing `value_state`, lexical coefficient, sign, scale, precision, period, count, method, package, source or authority;
- missing/misattached qualification, provenance, obligation, exclusion or conditional treatment;
- parent/root substitution for exact targets;
- extra/reordered rows, columns, table, values, hidden claims or operational-authority display;
- HTML injection, executable URLs, external resources and unescaped markup;
- mixed historical/v3 tuple cross-products, subclasses, duck types and unknown future versions before verifier entry;
- projection/renderer/artifact/evidence tampering;
- nondeterministic replay;
- assessor dependence on renderer implementation.

Mutation tests must independently defect the renderer and assessor and prove cross-detection/independence.

## 15. Historical fixture expectations

Existing fixtures and persisted evidence are immutable. TASK-067 may add new synthetic focused fixtures but must not edit historical ones. Tests must verify historical source lengths/digests, exact old dispatch selection and byte-identical old outputs. New fixtures must contain no production special-casing authority.

## 16. Implementation boundaries

Authorized only in separately activated TASK-067:

- additive v3 profile/schema/projector/renderer/assessor modules;
- minimal exact selector additions;
- focused/adversarial/compatibility tests;
- source-closure and architecture evidence.

Unauthorized:

- Candidate or pilot execution;
- Publication Release or downstream chain;
- changes to old profiles/renderers/schemas/fixtures/evidence beyond unavoidable additive selector seams;
- generic framework expansion;
- new BCRP kind or core profile major;
- network, browser, database, external dependency, sibling mutation or analytical recomputation.

TASK-067 stops after implementation and independent reconciliation. A representative Candidate retry is a later task.
