# TASK-045 BCRP 1.0 Vertical-Slice Implementation Report

Date: 2026-07-16
Status: accepted implementation evidence
Task: `TASK-045 — Initial Representation Profile, Layered Validator, and Golden Corpus Vertical Slice`

## 1. Executive verdict

**CLEAR TO PROCEED** to one bounded BCRP authoring/lifecycle compatibility proof.

TASK-045 materially implements the accepted TASK-044 representation contract without connecting BCRP to the existing runtime or renderer. The implementation has one standard-library structural authority, one deterministic canonical JSON direction, explicit L0-L6 findings, three valid cases, and exactly thirty accepted invalid mutations. The full legacy-plus-new suite passes.

This is not authorization for renderer integration, a second format, runtime replacement, AtlasForge integration, live interaction, financial-domain fields, or broad migration.

## 2. Baseline and constraints

- Repository remains an intentional non-Git filesystem tree.
- Fresh authorized baseline: `/tmp/briefforge-before-task045-20260716.json`.
- Pre-implementation test baseline: 154 tests, all passing.
- No package was installed; BCRP uses the Python standard library only.
- Earlier task manifests were not consulted.
- Existing runtime, promotion, legacy validation, presentation-model and renderer source files were not modified.
- `src/briefforge/__init__.py` changed only from eager to lazy compatibility exports because a fresh import of `briefforge.bcrp` otherwise imported runtime and renderer modules, violating the required independence proof.
- No schema library, serializer package, network, database, upstream package or renderer dependency is used.
- `compileall` was not run.

## 3. Contract materialization

### 3.1 Concrete topology

The profile identity is `briefforge-core-representation-profile`, version `1.0.0`.

A bundle consists of a non-semantic `bundle.json` inventory and independently addressable JSON documents for:

1. Presentation Brief;
2. Portable Presentation Material;
3. Candidate Presentation Package;
4. Validation Judgment;
5. Ready Presentation Package;
6. Publication Release;
7. Renderer Capability Declaration;
8. Renderer Compatibility Plan;
9. Generated-Artifact Audit;
10. Semantic Artifact Conformance;
11. derivative Publication Manifest.

The index uses relative local locations and optional transport SHA-256 digests. Locations, index ordering and transport hashes are not semantic identity.

### 3.2 Representation

`model.py` supplies mutable in-memory record/bundle values for validation and corpus mutation, immutable findings/fingerprints, and a derived graph value. Runtime behavior does not depend on the existing `runtime.py` dataclasses.

Record documents retain:

- record kind and stable identity;
- explicit profile identity/version;
- semantic content;
- fail-closed extension envelopes;
- optional non-semantic metadata.

### 3.3 Loader safety

`loader.py`:

- permits local filesystem paths only;
- rejects absolute locations, parent traversal and resolved symlink escape;
- rejects duplicate transport locations, root identities and nested semantic identities;
- rejects duplicate JSON object keys;
- rejects binary floats, `NaN`, `Infinity`, `null`, malformed Unicode and unsupported profile majors;
- enforces file-size, record-count, nesting-depth and container-item bounds;
- verifies declared kind/identity/profile against each document;
- optionally verifies transport SHA-256;
- never follows or resolves semantic external references.

### 3.4 Structural authority

`structure.py` is the sole executable BCRP 1.0 structural authority. It identifies itself as `bcrp-stdlib-native-structure-v1`, has no optional schema-engine dependency, and checks record inventory, required semantic keys, profile declarations, identity/reference graph integrity, state/payload forms, finite-selection structure, extension envelopes and DSB-007 prohibited fields.

No JSON Schema or parallel structural definition was introduced.

### 3.5 Graph

`graph.py` reconstructs canonical one-way edges from source-owned references. It rejects duplicate nodes/edges and dangling local references and derives reverse traversal in memory. The reverse index is disposable and excluded from serialization and fingerprints.

### 3.6 Canonicalization and equality

`canonical.py` provides:

- NFC text normalization and LF line endings;
- UTC timestamp normalization with explicit offset required;
- arbitrary-size exact integer/decimal support without binary floats;
- normalized negative zero and equivalent coefficient/scale forms;
- semantic order preservation for declared ordered fields;
- stable identity ordering for unordered records/sets;
- deterministic canonical JSON bytes;
- canonical reload/round trip;
- candidate-semantic, release-semantic, profile-instance, manifest-instance and artifact-byte domains;
- explicit domain/root/profile/canonicalization/algorithm metadata with SHA-256 fingerprints;
- distinct semantic equality, profile-instance equality, artifact byte equality and validated presentation equivalence.

Candidate-semantic scope includes the Candidate, Brief and referenced Portable Material. It excludes transport metadata, reverse indexes, comments, display-only extensions, release/renderer/artifact/manifest mechanics and renderer-only changes.

No fingerprint is treated as evidence of truth, analytical authority, governance approval or presentation equivalence. Candidate fingerprint issuance fails when L0-L2 prerequisites have blocking findings.

### 3.7 Layered validation

`validation.py` executes explicit, separately inspectable layers:

- L0 intake completeness/scope;
- L1 profile structure, reference integrity, extension and DSB-007 boundary;
- L2 semantic authority, state, qualifier, composition, selection, narrative and fallback obligations;
- L3 Candidate/Judgment/Ready/Release fingerprint and evidence-snapshot lifecycle;
- L4 release/distribution/recommendation governance;
- L5 renderer capability, declared transformation and fallback compatibility;
- L6 audit-link, lifecycle and semantic-artifact conformance.

Every finding has:

- layer;
- family/code;
- severity;
- semantic identity;
- location;
- message;
- blocked transition/consequence;
- referenced identities.

Findings are deterministic. Validation does not repair, infer approval, manufacture defaults, resolve evidence conflict, calculate selection values or rewrite content.

## 4. Golden corpus

### Case 1 — demographic/correlation publication

A reduced, public TASK-039-derived fixed-evidence publication with a bounded comparison universe, exact retained coefficients, explicit method/provenance, qualifier relations, static/print fallback and no new analysis.

Valid result: 0 findings.
Candidate fingerprint: `92df4a43e8be50b26d2bdd7bde5f3cea8b90222b44f9241285b9dfbeb9896532`.

### Case 2 — synthetic company comparison

A conspicuously fictional Aster Vale Tools / Boreal Kite Systems comparison. It uses generic typed external references and explicit zero, small-nonzero, missing, unavailable, not-applicable, suppressed and conflicting states. It defines no financial ontology.

Valid result: 0 findings.
Candidate fingerprint: `62f79aab2234c99025612fd77618e5f8df9b5fc608e7ca24a41ff3bf93967108`.

### Case 3 — synthetic company–macro selection

A conspicuously fictional Cinder Atlas Components publication with exactly three enumerated states, one authority-declared default, complete independently validated projections, state-compatible narratives/caveats, and complete static/print expression.

Valid result: 0 findings.
Candidate fingerprint: `3d19ab155f86d6bf0ba04b34247f3c7159087acc608748668883b5beb7080faf`.

## 5. Exact invalid-variant results

Every row below passed its declared primary finding assertions. Additional findings are deliberate cascades, chiefly stale Candidate/Judgment/Ready fingerprints after a semantic mutation; they are not substitutes for the primary finding.

| Variant | Actual findings | Actual layers | Required primary finding result |
|---|---:|---|---|
| C1-I01 | 21 | L0,L1,L2,L3 | PASS |
| C1-I02 | 4 | L1,L2,L3 | PASS |
| C1-I03 | 3 | L2,L3 | PASS |
| C1-I04 | 3 | L2,L3 | PASS |
| C1-I05 | 3 | L2,L3 | PASS |
| C1-I06 | 1 | L5 | PASS |
| C1-I07 | 2 | L3,L6 | PASS |
| C1-I08 | 2 | L1,L6 | PASS |
| C1-I09 | 1 | L6 | PASS |
| C2-I01 | 4 | L2,L3 | PASS |
| C2-I02 | 4 | L1,L2,L3 | PASS |
| C2-I03 | 7 | L1,L2,L3 | PASS |
| C2-I04 | 3 | L2,L3 | PASS |
| C2-I05 | 4 | L1,L2,L3 | PASS |
| C2-I06 | 3 | L2,L3 | PASS |
| C2-I07 | 4 | L2,L3,L4 | PASS |
| C2-I08 | 1 | L4 | PASS |
| C2-I09 | 3 | L3,L5 | PASS |
| C2-I10 | 3 | L1,L3 | PASS |
| C2-I11 | 4 | L1,L2,L3 | PASS |
| C3-I01 | 4 | L1,L2,L3 | PASS |
| C3-I02 | 6 | L1,L2,L3 | PASS |
| C3-I03 | 3 | L2,L3 | PASS |
| C3-I04 | 3 | L2,L3 | PASS |
| C3-I05 | 1 | L6 | PASS |
| C3-I06 | 5 | L2,L3,L5,L6 | PASS |
| C3-I07 | 1 | L5 | PASS |
| C3-I08 | 4 | L2,L3,L5 | PASS |
| C3-I09 | 6 | L2,L3 | PASS |
| C3-I10 | 5 | L2,L3 | PASS |

The accepted primary layer/family/severity/consequence tuples are inspectable in `tests/fixtures/bcrp/expectations.json`; the corresponding explicit mutations are in `src/briefforge/bcrp/corpus.py`.

## 6. Adversarial conclusions

### Golden-only acceptance

Rejected. Tests assert thirty invalid variants, required findings, exact case inventory, loading failures, deterministic order, non-repair, and legacy compatibility.

### Input-order dependence

Rejected. Tests reverse record order, object-key order and semantically unordered data while preserving canonical bytes/fingerprints. Ordered composition children remain meaning-bearing and do change equality/fingerprints.

### Undeclared fingerprint scope

Rejected. Fingerprint results name domain, root, profile, canonicalization version and algorithm. Candidate scope is separately tested against transport/index/display/renderer/artifact/manifest changes.

### Fixture shortcuts

Rejected. The valid corpus is materialized as 33 independently readable record files plus three indexes. The thirty mutations are named, narrow functions—not a generic patch interpreter—and expectations are explicit JSON evidence.

### Runtime/renderer contamination

Rejected. A fresh-process test proves importing `briefforge.bcrp` does not import `briefforge.runtime`, `briefforge.presentation_models` or `briefforge.renderer_adapter`. Corpus execution imports no upstream package, network or database module.

### Financial-domain leakage

Rejected. Case 2 is generic and conspicuously synthetic. The structural and semantic layers reject DSB-007 field names such as `fiscal_period`. BCRP retains publication-owned lifecycle semantics only.

## 7. Deviations and corrections during implementation

- An initial explicit-zero fixture used noncanonical `-0 × 10^-3`; semantic canonicalization handled it correctly, but the inspectable valid fixture was corrected to canonical `0 × 10^0`.
- External-reference `locator` was initially included in candidate canonical scope; it was correctly classified as a transport locator and excluded.
- An optional semantic-extension test initially ran through lifecycle validation without regenerating the Candidate fingerprint. The test was constrained to L2 admission because the later L3 stale-fingerprint block is correct.
- Parent package eager exports initially violated fresh BCRP import independence. Lazy compatibility exports resolved this without changing public export names; the full legacy suite proves compatibility.
- Explicit approximation qualification was added to L2 after a RED test proved that `approximate: true` without method/bound was otherwise admitted.

No accepted BCRP semantic decision was weakened for implementation convenience.

## 8. Known bounded limitations

- This is not a general-purpose schema ecosystem or arbitrary profile engine.
- The current profile reader accepts profile major 1 and rejects other majors; future minor-version behavior remains governed by accepted compatibility decisions and will require concrete evidence.
- No production authoring API creates BCRP records yet.
- No existing runtime object is migrated or treated as BCRP authority.
- No renderer consumes BCRP.
- Golden artifacts use declared audit/conformance records; TASK-045 does not generate real HTML/SVG output or inspect historical TASK-039 output.
- The validator implements the accepted initial vertical slice, not every future presentation-domain policy.
- The historical TASK-039 table-metadata inconsistency and missing `templates/` warning remain separate and unchanged.

## 9. Gate and successor

### Gate

**CLEAR TO PROCEED**.

The representation, loader, canonicalizer, validator and corpus are executable and independently verified. There is no blocker to a bounded adoption proof. Direct renderer integration would still be premature because no controlled producer path currently creates BCRP Candidate/Judgment/Ready records.

### Exactly one recommended next task

`TASK-046 — BCRP Candidate Authoring and Existing-Lifecycle Compatibility Proof`

Objective:

- implement one small renderer-independent authoring boundary for Brief, Portable Material and Candidate records;
- produce explicit Validation Judgment and Ready records through the BCRP validator without granting the builder semantic authority;
- adapt only the existing TASK-039-derived case as the proof;
- compare canonical semantic fingerprint/equality with the accepted golden case;
- preserve existing legacy runtime behavior and keep legacy dataclasses non-authoritative.

Non-goals:

- renderer or selector invocation;
- runtime replacement or broad migration;
- Publication Manifest emission or AtlasForge integration;
- second formats/converters;
- live data/network/database access;
- financial-domain fields.

This is the smallest slice that proves BCRP can be produced under controlled authority before any renderer is allowed to consume it.

## 10. Verification record

Pre-implementation:

- recovery: exit 0;
- fresh before-manifest creation: exit 0;
- `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -v`: 154 tests, OK.

Implementation:

- initial targeted RED: expected import failure;
- intermediate BCRP run: 27 tests, 3 failures, then corrected;
- fresh-import independence RED: 1 expected failure, then corrected;
- approximation qualification RED: 1 expected failure, then corrected;
- targeted BCRP final run: 29 tests, OK;
- complete final suite: 183 tests, OK;
- context health: 0 blocks, 0 warnings;
- architecture-to-reality audit: 0 blocks, 0 warnings; report refreshed at `artifacts/reports/R-20260716-architecture-reality-audit.md`;
- final coherence and exact post-manifest comparison run after this report becomes immutable.

## 11. No external side effects

- No package installation.
- No network, database, renderer, AtlasForge or upstream runtime access.
- No Git initialization.
- No commit.
- No push.
- No `compileall`.
- No credentials or credential-bearing fixture values.
