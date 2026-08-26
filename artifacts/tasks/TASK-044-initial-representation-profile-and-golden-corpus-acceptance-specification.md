# TASK-044 — Initial Representation Profile and Golden Corpus Acceptance Specification

Status: complete
Date: 2026-07-16

## Request

Accept exactly one renderer-independent initial Representation Profile, settle its topology, canonical relationships, explicit states, finite selection, deterministic semantic canonicalization, equality, fingerprints, extensions and versioning, and specify exactly three primary golden-corpus cases with valid/adversarial expectations. Issue the final architecture-only gate before bounded implementation.

## Methodology slice

- Objective: convert TASK-043's accepted abstract graph and layered validation contract into one binding profile and one complete corpus acceptance plan.
- Explicit non-goals: no profile instance, schema, serialization, loader, canonicalizer, validator, builder, runtime, renderer, selector, fallback, manifest emission, fixture materialization, AtlasForge change, financial-domain semantics, TASK-039 repair, constitutional amendment, Git initialization, commit, or push.
- Implementation boundary: one task, two specifications, three bounded decisions, one architectural report, bounded backlog/state/handoff/summary/context updates, and deterministic non-Git manifest closeout.
- Readiness prerequisites: successful recovery; applicable instructions inspected; TASK-043 reconciled complete; no implementation task active; TASK-044 identifier unused; non-Git state confirmed; fresh baseline at `/tmp/briefforge-before-task044-20260716.json`.
- Success criteria: one profile maps all accepted semantics without duplication; canonical direction and state encoding are settled; canonicalization/equality are deterministic enough to implement; extensions fail safely; exactly three cases cover every layer/invariant/lifecycle/fallback responsibility; one serialization direction and one next task are selected.
- Verification expectations: focused artifact consistency, summary refresh, context regeneration, coherence, context health, architecture-to-reality audit, recovery, and exact pre/post manifest comparison. Runtime tests and compileall are excluded because no executable source/test/validator changes are authorized.

## Evidence used

- TASK-038 representation decisions/reports and canonical ADPM specification/versioning decisions;
- TASK-040 capability reconciliation;
- TASK-041 publication specification/report and three accepted decisions;
- TASK-042 semantic-authority specification/report and three accepted decisions;
- TASK-043 task/specification/report and three accepted decisions;
- current Candidate/Judgment/Ready runtime, renderer adapter/conformance evidence, TASK-039 source/publication chain, tests as read-only evidence, renderer policy, decision-support backlog, state, and latest handoff.

## Outputs

- `artifacts/specifications/briefforge-core-representation-profile.md`
- `artifacts/specifications/bcrp-golden-corpus-acceptance.md`
- `artifacts/reports/R-20260716-initial-representation-profile-and-golden-corpus-acceptance.md`
- `artifacts/decisions/D-20260716-bcrp-topology-relationship-and-state-profile.md`
- `artifacts/decisions/D-20260716-bcrp-canonicalization-equality-extension-and-versioning.md`
- `artifacts/decisions/D-20260716-bcrp-golden-corpus-serialization-and-implementation-gate.md`

## Outcome

Accepted **BriefForge Core Representation Profile 1.0.0 (BCRP 1.0)** as the single initial renderer-independent profile. It uses independently addressable typed records and stable identity edges, explicit scoped state assertions, complete finite selection projections, deterministic semantic canonicalization, independent equality/fingerprint domains, and fail-closed extensions.

Accepted exactly three future corpus cases: TASK-039-derived demographic/correlation publication, synthetic fictional-company comparison, and synthetic company–macro finite-selection publication. Their valid and invalid variants cover all validation layers and core invariants without materializing files.

Gate verdict: **CLEAR TO IMPLEMENT** one bounded successor only:

`TASK-045 — Initial Representation Profile, Layered Validator, and Golden Corpus Vertical Slice`

No implementation is activated by TASK-044.

## Non-mutation confirmation

TASK-044 modifies no executable source, test, validator, runtime model, renderer, publication, TASK-039 artifact, fixture, schema, serialization, AtlasForge project, upstream project, financial-domain architecture, or Constitution. BriefForge remains non-Git; no commit or push occurred.
