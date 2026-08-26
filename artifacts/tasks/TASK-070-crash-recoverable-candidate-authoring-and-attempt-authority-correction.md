# TASK-070 — Crash-Recoverable Candidate Authoring and Attempt-Authority Correction

Date: 2026-08-08
Status: **COMPLETED — ACCEPTED / NO CANDIDATE AUTHORED / RECONCILED**
Task type: bounded lifecycle correction, durable authoring coordination, adversarial verification, and governance reconciliation

## Objective

Correct Candidate authoring so one governed operation owns authorization, durable attempt consumption, exactly one semantic construction, canonical serialization, durable attempt-specific staging, fingerprint receipt, post-staging validation, explicit acceptance, and deterministic recovery.

## Authenticated baseline

- Canonical recovery reported no active task before activation.
- No overlapping BriefForge authoring, test, or project-tool process existed.
- TASK-069 remains immutable `COMPLETED — BLOCKED / NOT ACCEPTED / RECONCILED`.
- TASK-069 marker SHA-256: `05d7d994a64b798417e21b26ba5782cbc31d87a68af39e0a13f282a073e8a70f`.
- TASK-069 final reconciliation SHA-256: `a9d29c7235d5a1f21ea12f49dc1b13a1921c593f8263d090bf5a8f845bedfb12`.
- Pre-task manifest: `artifacts/reports/R-20260808-task-070-pre-task-filesystem-manifest.json`.
- Baseline paths excluding manifest self: 959.
- Baseline entries digest: `f5429d9678ec797e5c1ce79e222eb54a869a30fb92e9a30d90c68e3513fbc50c`.
- Baseline report SHA-256: `b8cf740022afc9cb0d71a109c853ee73ae9e1dc0a19ba39c1fc533520fc0b919`.
- Cache/bytecode paths: 0.

## Causal authentication

The generic `briefforge.bcrp.authoring.author_candidate_bundle` function is a public pure semantic/technical constructor. It accepts three drafts, creates the fixed three-record closure, runs L0–L2, and returns an in-memory bundle. It has no task, attempt, authorization, path, persistence, or lifecycle authority.

TASK-069's governed boundary was its task-local wrapper. That wrapper durably consumed the attempt, called the pure constructor, canonicalized in memory, ran fallible post-author validation, and only then attempted persistence. The canonical-order validator defect therefore destroyed recoverability after a successful constructor return.

The delegated reviewer crossed the public pure-constructor boundary, not the TASK-069 governed attempt boundary. The act remains an unauthorized review-process invocation, but it was not a production authority bypass and created no governed identity or evidence.

## Accepted contract

`artifacts/decisions/D-20260808-task-070-crash-recoverable-candidate-authoring-and-attempt-authority.md` is accepted before production implementation.

## Bounded implementation slice

### Objective

Add the smallest source-neutral file-backed coordinator and recovery model that makes durable staging precede semantic acceptance.

### Non-goals

No real Candidate attempt; no TASK-069 retry, reconstruction, marker mutation, or acceptance; no generic registry, service, database, plugin framework, distributed transaction claim, publication-stage authority, or successor activation.

### Implementation boundary

- one bounded production coordinator module under `src/briefforge/`;
- explicit pure-builder naming while preserving compatibility;
- focused synthetic tests under isolated temporary roots;
- TASK-070 governance, reports, state, handoff, and affected summaries.

### Success criteria

- monotonic durable states and fail-closed recovery;
- no governed return before staged bytes and receipt are recoverable;
- validation failure preserves exact bytes, fingerprint, and receipt without acceptance;
- no replay after consumption;
- exact binding and path enforcement;
- concurrent duplicate refusal;
- accepted semantic ordering and topology validation remain intact;
- TASK-069 marker and endpoint remain exact.

## Prohibited effects

No real Candidate, Judgment, Ready package, Release, Plan, token, projection, rendering, conformance, Manifest, delivery, deployment, HTTP evidence, TASK-056 evidence, TASK-051 work, AtlasForge work, Git action, network/database/dependency action, or successor activation.

## Outcome

Implemented the bounded source-neutral coordinator in `src/briefforge/candidate_authoring.py` and its adversarial proof in `tests/test_task070_candidate_authoring_recovery.py`.

The accepted endpoint provides:

- monotonic prepared, consumed, staged, validation-pending, accepted, rejected, and indeterminate terminal commitments;
- durable attempt consumption before semantic construction;
- exactly one fixed production constructor invocation with immutable attempt-specific staging before acceptance validation;
- exact canonical-byte, Candidate-fingerprint, input-digest, authority-decision, predecessor-evidence, campaign, attempt, and semantic-profile binding;
- fixed governed paired-semantic validation and callback-free governed authoring/recovery;
- deterministic recovery that never repeats authoring;
- conservative fail-closed handling of interrupted, tampered, ambiguous, and concurrent states;
- non-overlapping governed and synthetic roots;
- historical TASK-060 closure preservation and unchanged TASK-069 attempt evidence.

No governed TASK-070 attempt was authorized or executed. The canonical authority, ledger, and output roots remain absent.

## Independent review

Four independent read-only review dimensions covered durability/recovery, attempt accounting/invocation authority, semantic preservation, and immutable-history/scope boundaries. Evidence-backed blockers were corrected. Review artifacts are preserved under `artifacts/reports/R-20260808-task-070-independent-review-*.md`; final reconciliation review passed after closeout accounting.

## Verification

- TASK-070 focused: `Ran 36 tests in 2.338s — OK`.
- TASK-069 historical: `Ran 11 tests in 0.093s — OK`.
- TASK-067 historical: `Ran 76 tests in 2.411s — OK`.
- TASK-062 historical: `Ran 17 tests in 37.686s — OK`.
- historical publication/delivery regression: `Ran 128 tests in 128.877s — OK`.
- full repository after correction: `Ran 663 tests in 258.263s — OK`.
- architecture-to-reality audit: no blocks or warnings.
- context health: no blocks or warnings.
- generated-project coherence: no blocks; the temporary absolute-path sovereignty warning was removed in closeout.
- static source/security inspection: Python AST PASS; no dangerous process/evaluation constructs; no source-specific TASK-064/TASK-069 fixture identity in production.
- historical TASK-060 source-closure mismatches: 0.
- final cache/bytecode residue: 0.
- final post-closeout focused rerun: `Ran 36 tests in 2.264s — OK`.
- final post-closeout full rerun: `Ran 663 tests in 260.345s — OK`.

## Post-slice decision

Accept the bounded correction and stop. Do not generalize it into a registry, service, or publication workflow. No successor is active. Any future Candidate attempt requires a separate explicit human decision, new governed identity and lineage, and cumulative representative-campaign attempt number 2.

## Evidence

- Decision: `artifacts/decisions/D-20260808-task-070-crash-recoverable-candidate-authoring-and-attempt-authority.md`
- Causal report: `artifacts/reports/R-20260808-task-070-causal-authentication.md`
- Independent reviews: `artifacts/reports/R-20260808-task-070-independent-review-1-durability-recovery.md` through `R-20260808-task-070-independent-review-4-history-scope.md`
- Completion: `artifacts/reports/R-20260808-task-070-completion.md`
- Final reconciliation: `artifacts/reports/R-20260808-task-070-final-filesystem-reconciliation.json`
