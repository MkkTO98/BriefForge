# TASK-045 — Initial Representation Profile, Layered Validator, and Golden Corpus Vertical Slice

Status: complete
Type: bounded implementation vertical slice
Date: 2026-07-16

## Objective

Materialize the accepted TASK-044 BriefForge Core Representation Profile 1.0.0 (BCRP 1.0) contract as one renderer-independent standard-library implementation, with deterministic canonical JSON, safe local bundle loading, explicit equality/fingerprint domains, layer-separated L0-L6 validation, and the accepted three-case golden corpus plus all thirty adversarial variants.

## Authorization basis

- TASK-038 specification-first representation architecture;
- TASK-041 publication/lifecycle foundations;
- TASK-042 semantic authority, state, selection and fallback foundations;
- TASK-043 graph and layered-validation specification;
- TASK-044 accepted BCRP 1.0 representation and golden-corpus contract;
- explicit human authorization for this bounded TASK-045 slice.

## Scope

- concrete BCRP 1.0 in-memory records and deterministic JSON bundle topology;
- bounded local-only loader with duplicate-key, path, size/depth/item, Unicode, number, null, identity and profile checks;
- one machine structural authority;
- one-way graph reconstruction with derived reverse indexes;
- graph-/domain-scoped canonicalization, equality and SHA-256 fingerprints;
- L0-L6 validator retaining explicit layer, family, severity, location, identity, blocked transition and references;
- three valid multi-record bundles and thirty narrow deterministic invalid mutations;
- round-trip, determinism, safety, equality, validation, corpus and independence tests;
- lazy package exports strictly to prove that `briefforge.bcrp` does not import the existing runtime or renderer.

## Non-goals

- no existing runtime-package migration;
- no BCRP-to-runtime or runtime-to-BCRP adapter;
- no renderer, selector, HTML/SVG, manifest-emission or fallback runtime integration;
- no schema language, second serialization, converter or network loader;
- no AtlasForge integration;
- no company/financial-domain semantics prohibited by DSB-007;
- no repair of historical TASK-039 publication evidence;
- no Git initialization, commit or push.

## Implementation

### Source

- `src/briefforge/bcrp/model.py` — record, bundle, finding, graph and fingerprint result models;
- `src/briefforge/bcrp/loader.py` — bounded deterministic JSON loader;
- `src/briefforge/bcrp/graph.py` — canonical one-way relation inspection and derived reverse traversal;
- `src/briefforge/bcrp/structure.py` — sole executable BCRP 1.0 structural authority;
- `src/briefforge/bcrp/canonical.py` — domain canonicalization, serialization, reload, equality and fingerprints;
- `src/briefforge/bcrp/validation.py` — explicit L0-L6 validation without repair;
- `src/briefforge/bcrp/corpus.py` — fixture access and thirty reviewable accepted mutations;
- `src/briefforge/bcrp/__init__.py` — renderer-independent public API;
- `src/briefforge/__init__.py` — lazy compatibility exports needed to prevent BCRP import from eagerly loading runtime/renderer modules.

Existing runtime, validator, promotion, presentation-model and renderer modules remain semantically and textually unchanged.

### Corpus

Materialized under `tests/fixtures/bcrp/`:

1. `case-1-demographic-correlation-publication` — reduced public TASK-039-derived fixed-evidence case;
2. `case-2-synthetic-company-comparison` — conspicuously fictional generic comparison with explicit value states and no financial ontology;
3. `case-3-synthetic-company-macro-selection` — conspicuously fictional three-state finite/prevalidated selection case.

Each valid case has eleven independently addressable root records plus a non-semantic relative-location index. `expectations.json` declares all accepted invalid findings. Invalid variants are narrow named mutations in `corpus.py`, not a generic patch language.

### Tests

`tests/test_bcrp_vertical_slice.py` covers:

- all three valid cases through L0-L6;
- all thirty invalid variants and every declared primary finding;
- round-trip equality and fingerprint stability;
- record/object order, NFC/LF and timestamp normalization;
- exact decimal, zero/missing/rounded-display distinction and approximation qualification;
- semantic/profile/artifact/presentation-equivalence separation;
- transport, reverse-index, display-extension and renderer-artifact fingerprint scope;
- duplicate keys/locations/identities, traversal/absolute paths, malformed constants/floats/nulls/Unicode, bounds and unsupported majors;
- optional/required extension behavior;
- validator non-repair and deterministic findings;
- fresh-process independence from runtime, renderer, upstream package, network and database imports.

## TDD evidence

1. Initial targeted run failed because `briefforge.bcrp` did not exist.
2. First implementation run: 27 tests, 3 failures (noncanonical fixture zero, locator canonical scope, optional-extension test incorrectly crossing stale lifecycle records).
3. Corrections were bounded to canonical semantic scope, fixture canonical zero, and layer-correct test expectation.
4. Fresh-import independence test then failed because parent package exports eagerly imported runtime/renderer modules.
5. Parent package exports were made lazy while preserving the prior public names; targeted and complete legacy suites passed.
6. Approximation-qualifier test failed first and passed after the L2 rule was implemented.

## Outcome

- BCRP 1.0 is now materialized as a renderer-independent vertical slice.
- All three accepted valid cases pass with zero findings.
- All thirty accepted invalid variants produce all declared primary layer/family/severity/blocked-transition findings.
- Canonical fingerprints are input-order independent and have explicit domain/root/profile/canonicalization/algorithm metadata.
- Candidate fingerprints exclude transport locations/order, reverse indexes, comments, display-only extensions, lifecycle/artifact/manifest mechanics and renderer-only changes.
- The loader never follows external references and rejects unsafe local transport constructs.
- The validator reports but never repairs semantic content.
- Existing runtime and renderer behavior remains compatible; no integration was introduced.

## Verification

Pre-implementation baseline:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -v
Ran 154 tests — OK
```

Implementation verification:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_bcrp_vertical_slice -v
Ran 29 tests — OK

PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -v
Ran 183 tests — OK

PYTHONDONTWRITEBYTECODE=1 python3 -B tools/check_coherence.py --project .
0 blocks; final rerun required after closeout text edits

PYTHONDONTWRITEBYTECODE=1 python3 -B tools/context_health.py --project . --json
0 blocks; 0 warnings

PYTHONDONTWRITEBYTECODE=1 python3 -B tools/architecture_reality_audit.py --project . --write-report
0 blocks; 0 warnings
```

## Gate

**CLEAR TO PROCEED**, but not directly to renderer integration.

The next bounded task should establish one producer/adoption boundary before BCRP becomes an input to any renderer.

## Recommended successor

`TASK-046 — BCRP Candidate Authoring and Existing-Lifecycle Compatibility Proof`

Bounded objective: implement one renderer-independent authoring path for Brief + Portable Material + Candidate records; produce a Validation Judgment and Ready record through the BCRP validator; map one existing TASK-039-derived case without making legacy runtime dataclasses authoritative; and prove semantic/fingerprint compatibility. Exclude renderer invocation, selector runtime, AtlasForge, manifest emission, second formats and financial-domain fields.
