# TASK-046 — BCRP Candidate Authoring and Existing-Lifecycle Compatibility Proof

Status: complete
Type: bounded implementation slice
Date: 2026-07-16

## Objective

Add one renderer-independent producer boundary for BCRP Presentation Brief, Portable Presentation Material, and Candidate records; create explicit Validation Judgment and Ready records without collapsing lifecycle authorities; and prove that the reduced TASK-039-derived authored Candidate is semantically and fingerprint-equivalent to the accepted BCRP golden case.

## Authorization basis

- TASK-038 specification-first representation architecture;
- TASK-041 Candidate -> Judgment -> Ready lifecycle separation;
- TASK-042 semantic authority and fail-closed behavior;
- TASK-043 layered validation and authority separation;
- TASK-044 BCRP 1.0 profile/corpus contract;
- TASK-045 verified BCRP vertical slice and explicit successor recommendation;
- direct human authorization for TASK-046.

## Bounded slice

### Objective

Prove that BCRP can be authored and promoted under controlled authority before any renderer is permitted to consume it.

### Non-goals

- no migration, replacement, or adaptation of legacy runtime dataclasses;
- no renderer/selector/fallback invocation or HTML/SVG change;
- no Publication Release, renderer plan, artifact, conformance, or manifest production;
- no AtlasForge integration, second format, converter, network, database, live data, or upstream mutation;
- no company/financial-domain semantics deferred by DSB-007;
- no repair or rewrite of historical TASK-039 publication evidence;
- no Git initialization, commit, or push.

### Implementation boundary

- one new renderer-independent authoring/lifecycle module;
- one bounded public API export update;
- one test module covering TASK-039 compatibility, non-fixture-specific authoring, lifecycle authority, invalidity, mutation, and rewrite rejection;
- task/report/state/handoff/summary closeout only.

### Success criteria

1. Brief + Material + Candidate are authored from explicit transport-neutral drafts with no semantic defaults or inferred authority.
2. Authored input is copied, validated through L0-L2, and rejected rather than repaired when invalid.
3. The TASK-039-derived authored Candidate is semantically equal to, and has the same candidate-semantic fingerprint as, golden case 1.
4. A second synthetic case proves the producer is not hard-coded to TASK-039 content.
5. Validation Judgment records only L0-L2 as executed and retains explicit negative findings when invalid.
6. Ready creation requires one successful exact-fingerprint Judgment and rejects post-judgment Candidate mutation.
7. Existing runtime/renderer imports and all legacy behavior remain independent.

## Implementation

### `src/briefforge/bcrp/authoring.py`

Introduced:

- `RecordDraft` — explicit identity, semantic body, and extensions; no record-kind field, so convenience authoring cannot fabricate lifecycle/renderer/artifact authority records;
- `author_candidate_bundle(...)` — creates exactly one Brief, Material, and Candidate under BCRP 1.0, deep-copies inputs, executes L0-L2, and rejects blocking findings without defaults, repair, upstream dereference, or fixture lookup;
- `record_candidate_validation(...)` — executes exactly L0-L2 and appends one explicit Judgment, including deterministic complete findings and exact Candidate fingerprint; invalid Candidates produce inspectable negative Judgments;
- `promote_validated_candidate(...)` — creates Ready only when one successful L0-L2 Judgment binds the unchanged Candidate identity/fingerprint;
- `BCRPAuthoringRejected` and `BCRPPromotionRejected` — fail-closed stage-specific errors.

Ready fingerprint generation reuses the already-materialized BCRP 1.0 golden-corpus convention:

```text
sha256(ready_identity + "|" + candidate_semantic_fingerprint)
```

The Judgment identity remains an explicit checked Ready semantic binding. Ready grants no Publication Release or renderer authority.

### `src/briefforge/bcrp/__init__.py`

Exports only the bounded authoring/lifecycle API. Fresh BCRP import remains independent of legacy runtime, presentation models, and renderer modules.

### `tests/test_bcrp_authoring_lifecycle.py`

Seven tests prove:

- TASK-039-derived Candidate semantic equality and exact fingerprint compatibility with golden case 1;
- generic behavior on synthetic golden case 2, including a recommendation posture absent from TASK-039;
- deep-copy isolation and invalid closure rejection;
- exact L0-L2 Judgment scope;
- Ready binding and deterministic Ready fingerprint;
- post-Judgment mutation rejection;
- retained negative Judgment plus promotion rejection;
- refusal to overwrite or append competing lifecycle authority records.

## Anti-overfitting result

The implementation does not import `corpus.py`, inspect case IDs, copy fixture files, infer TASK-039-specific fields, or contain demographic/correlation logic. Tests create the same API input from both case 1 and structurally different synthetic case 2. The second case preserves its recommendation posture and passes semantic equality. TASK-039 is therefore compatibility evidence, not executable special-case logic.

## Lifecycle-authority result

- Candidate authoring creates no Judgment or Ready implicitly.
- Judgment creation records only layers actually executed (`L0`, `L1`, `L2`), not the later L3-L6 layers that require lifecycle/release/renderer/artifact records.
- An invalid Candidate can receive an explicit negative Judgment but cannot become Ready.
- Ready requires exact Candidate identity/fingerprint continuity and one successful Judgment.
- Candidate -> Judgment -> Ready remains separate from Publication Release and all derivative publication/runtime authority.
- Existing legacy lifecycle remains unchanged and non-authoritative for BCRP.

## TDD evidence

1. The targeted test module was written first.
2. RED run failed with the expected import error because the TASK-046 API did not exist.
3. The smallest authoring/lifecycle module and exports were added.
4. Targeted run passed all 7 tests.
5. Complete suite passed all 190 tests (183 baseline + 7 TASK-046).

## Outcome

TASK-046 is complete. A controlled producer now creates and validates Candidate-stage BCRP records, records an explicit layer-honest Judgment, and creates Ready only under exact unchanged-fingerprint authority. The TASK-039-derived compatibility proof matches the accepted golden Candidate semantically and by fingerprint. No legacy runtime migration or renderer integration occurred.

## Verification

Pre-implementation:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -B tools/recover_session.py --project . --json
exit 0

python3 -B /tmp/briefforge_manifest.py . /tmp/briefforge-before-task046-20260716.json
638 included paths; exit 0

PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -v
Ran 183 tests — OK
```

Implementation:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_bcrp_authoring_lifecycle -v
initial RED: expected ImportError for missing TASK-046 API
final: Ran 7 tests — OK

PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -v
Ran 190 tests — OK

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -c '<fresh BCRP import inspection>'
[]
```

Final governance and exact mutation-boundary results are recorded in `artifacts/reports/R-20260716-bcrp-candidate-authoring-and-lifecycle-compatibility.md` after closeout.

## Gate

**CLEAR TO PROCEED**, but not to renderer invocation.

## Exactly one recommended successor

`TASK-047 — BCRP Renderer Compatibility-Plan Production and Fail-Closed Proof`

Bounded objective: create one renderer-independent producer for `RendererCompatibilityPlanRecord` from an exact BCRP Ready package plus an explicit `RendererCapabilityDeclarationRecord`; prove deterministic native/fallback/unsupported outcomes against accepted golden cases; and stop before renderer invocation, HTML/SVG mutation, manifest emission, AtlasForge integration, or runtime migration.

This is the narrow next authority boundary: BCRP can now reach Ready, but no controlled producer yet turns Ready requirements and renderer-owned capability evidence into the deterministic, fail-closed compatibility plan required before rendering.

## Erratum — superseded by TASK-047

Status: historical correction accepted 2026-07-16.

TASK-046 correctly proved explicit renderer-independent BCRP Candidate authoring, L0-L2 technical validation behavior, golden-case semantic/fingerprint parity, and generalized construction. It incorrectly characterized its L0-L2 output as a governed `ValidationJudgmentRecord`, its native promotion helper as authorized Ready production, and the resulting BCRP path as independently authoritative. No accepted decision authorized that second lifecycle authority.

TASK-047 supersedes only those lifecycle-authority claims:

- `record_candidate_validation(...)` now returns technical evidence and cannot manufacture governance Judgment;
- `promote_validated_candidate(...)` now fails closed because native BCRP promotion has no accepted authority;
- the governed legacy Candidate/Judgment/Ready runtime remains the sole current operational approval/promotion authority;
- an already-governed legacy result may be represented in BCRP only through the required, generically unsupported, fail-closed compatibility contract;
- mapped records grant no Publication Release, renderer, artifact, conformance, manifest, distribution, or legacy-downstream authority;
- TASK-039 golden parity proves BCRP Candidate semantics only and cannot supply missing historical lifecycle identities or timestamps.

The TASK-046 recommendation to proceed directly to renderer compatibility planning is withdrawn. A compatibility-plan record depends directly on Ready plus renderer capability, not on a release reference; however, the accepted processing sequence and validation-layer order place explicit Publication Release/governance authority at L4 before L5 compatibility planning, and artifact acceptance later requires both Release and plan. The next bounded task must therefore establish Publication Release production and lifecycle proof before renderer compatibility-plan production is reconsidered.

Canonical correction evidence:

- `artifacts/decisions/D-20260716-bcrp-lifecycle-authority-and-legacy-compatibility.md`;
- `artifacts/specifications/bcrp-lifecycle-authority-and-legacy-compatibility.md`;
- `artifacts/reports/R-20260716-bcrp-lifecycle-authority-and-legacy-compatibility.md`;
- `src/briefforge/bcrp/authoring.py`;
- `src/briefforge/bcrp_legacy_compatibility.py`.
