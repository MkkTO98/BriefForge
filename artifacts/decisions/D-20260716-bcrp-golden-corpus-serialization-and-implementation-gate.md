# D-20260716 BCRP Golden Corpus, Serialization, and Implementation Gate

Date: 2026-07-16
Status: accepted
Task: TASK-044

## Decision

BriefForge accepts the BCRP 1.0 golden-corpus plan with exactly three primary cases:

1. a reduced TASK-039-derived demographic/correlation fixed-evidence publication;
2. a synthetic fictional-company comparison/decision publication using only generic external references;
3. a synthetic company–macro relationship publication with finite, fully materialized prevalidated selection.

Each case has one expected-valid instance and minimal invalid mutations with expected validation layer, finding family, severity, continuation behavior, and blocked lifecycle consequence. Together they cover every mandatory BCRP responsibility, all TASK-043 validation layers and cross-layer invariants, release/artifact/manifest boundaries, fail-closed fallback, audit-link versus semantic conformance, fixture safety, DSB-007, and optional AtlasForge catalogue consumption.

No corpus file is created by TASK-044. TASK-039 JSON is evidence only; its table-metadata mismatch is a historical invalid-input condition, not a valid expected outcome.

For the bounded implementation successor, the single initial serialization direction is deterministic canonical JSON documents in a multi-record bundle. Exact decimals must avoid ambiguous JSON numbers. Markdown is not canonical and no parallel format/converter work is admitted.

Implementation gate: **CLEAR TO IMPLEMENT** exactly one next task:

`TASK-045 — Initial Representation Profile, Layered Validator, and Golden Corpus Vertical Slice`

Its scope is one selected serialization, BCRP 1.0, deterministic loader/canonicalizer, structural and core semantic validation, materialization of the three cases and invalid variants, and round-trip/expected-finding tests. It excludes runtime package migration, renderer integration, selectors, and AtlasForge integration.

## Rationale

The profile now maps all accepted semantics without gaps, settles canonical direction and equality, and fails closed on unknown meaning. Three deliberately heterogeneous cases expose happy-path and adversarial pressure without company-specific fields or a fourth case. JSON has the strongest minimum fit for the existing Python/offline/test environment while remaining subordinate to BCRP.

## Alternatives considered

- materialize fixtures in TASK-044 — rejected; this task is the final architecture-only gate;
- several initial formats — rejected; creates uncontrolled divergence;
- reuse TASK-039 JSON unchanged — rejected; incomplete runtime shape and known metadata inconsistency;
- YAML or Markdown canonical form — rejected; ambiguity or prose authority risk;
- another planning task — rejected; no concrete architecture blocker remains.

## Consequences

- TASK-045 may be proposed but is not activated here.
- Golden fixtures must be deterministic, redacted, offline, small, and mutation-derived.
- Runtime tests are not run for TASK-044 because executable source/tests/validators are unchanged.
- Any implementation divergence from BCRP or corpus expectations returns to decision authority rather than silently changing the profile.
