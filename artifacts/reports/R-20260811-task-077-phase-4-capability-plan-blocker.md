# TASK-077 Phase 4 — Capability-v2, Plan-v2, and Acceptance Blocker

Status: **PARTIAL PASS — PHASE 4 REMAINS IN PROGRESS / POSITIVE PLAN AUTHORITY PATH BLOCKED**
Date: 2026-08-11

## Scope completed

Production work retained in the existing planner owner:

- Capability-v2 construction, exact serialization, admission, deterministic persistence/reload, collision/stale/correlated-substitution rejection;
- Plan-v2 deterministic requirement/mapping planning core;
- generic nonempty cardinalities tested at `N=1/7/16`, with `N=0` fail-closed;
- exact frozen 8/10-record predecessor closure verification;
- reordered, duplicate, and altered-topology closure rejection;
- generalized process-issued paired-v3 Candidate authentication from independent predecessor digest/fingerprint/identity facts;
- historical v1 planner paths preserved.

No frozen contract byte changed.

## Exact acceptance blocker

TASK-077 requires a positive test through the real Plan-v2 production constructor/admission/native-handle path. That path correctly requires an actual `VerifiedPublicationRelease` bound to the exact authenticated paired-v3 Candidate.

No accepted `VerifiedPublicationRelease` exists for TASK-071. The frozen TASK-076 8/10 closure records explicitly identify themselves as `non-authority-predecessor-byte-stand-in` fixtures. Treating them as release authority would violate the contract authority boundary. Producing a real TASK-071 Judgment/Ready/Release would execute the lifecycle act that TASK-077 explicitly prohibits.

A synthetic historical `NativeFixture` release was tested only as a temporary test subject. Its Candidate is not generation-8 contract-conforming: production interpretation rejected dangling paired target `unit:dimensionless`. It therefore cannot authenticate the Plan-v2 path, and weakening the production graph to admit it would reinterpret the frozen generation-8 contract.

Accordingly, Plan-v2 deterministic construction logic exists, but Plan-v2 production admission, persistence/reload, opaque handle consumption, and native integration are **not accepted or complete**. Advancing to Phase 5/6 would be false.

## Current byte classifications

- `src/briefforge/task076_contracts.py` — correct and retainable after remediation; process-issued generic paired-v3 Candidate authority added. SHA-256 `8bf9ab2ddee29a210747677029e4cf70faf80f5a385a5f08b306c4db078191b0`.
- `src/briefforge/bcrp/registry.py` — correct and retainable for Phase-3 scope. SHA-256 `651f5465c49da789d952a835e74aa4490ae4b94e8aeb57a280eca5a42acb4074`.
- `src/briefforge/bcrp_paired_semantic_interpretation_v2.py` — correct and retainable for authenticated generation-8 interpretation; historical synthetic fixture rejection is correct. SHA-256 `4f1c5866d4d9efb9ac2d28fa14f4341f31b36bd0ff2f1b9fb1f60f85bf9dbd75`.
- `src/briefforge/bcrp_paired_derivation_evidence_v2.py` — correct and retainable for Phase-3 scope. SHA-256 `7d51ee3c98b3ad760b509baeb324727c4bc525de401cdd3fa6cc33b8532c5e0f`.
- `src/briefforge/bcrp_renderer_compatibility_planning_v2.py` — Capability-v2 and generic/closure portions retainable; Plan-v2 end-to-end authority path incomplete and unaccepted. SHA-256 `132a54a60dd4d5c21386c8057c19ef516a1fc38f3ae2e39f8a777aa039c1dba3`.

The four paused modules changed during explicitly authorized resumption. Exact paused hashes were not recorded before the denial, so no unsupported byte-for-byte paused comparison is claimed. Their current hashes are recorded above.

## Tests

Focused TASK-077 suite:

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_task077_interpretation_envelope tests.test_task077_capability_v2 tests.test_task077_plan_v2`
- PASS: 23 tests in 14.726s.

Relevant prior-owner regressions:

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_bcrp_vertical_slice tests.test_task067_schema_projection`
- PASS: 48 tests in 0.972s.

Frozen validator:

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/validate_task076_contracts.py`
- PASS: 16 deterministic artifacts, four schemas, 37 registry entries, exact 165/722/144/590 graph counts, 10 valid fixtures, 63/63 invalid fixtures rejected.

Protected hashes remain:

- manifest `b393b7fbdddbcb03792a01ba7ee25056e86a0f70a316b41c036de5314458d0a6`;
- TASK-071 profile `62cbe5294b123c9b4043e9f721a1b2585c70a5380e2121a39e8558b5c73b1898`;
- paired initializer `b2bd66bf3b9deb346b708348fcd7220d159bcc6df4d44e43e7d0adb5a3ee842e`.

## Commands and notable results

Phase-3 recovery/inspection commands and results are recorded exhaustively in `R-20260811-task-077-phase-3-inspection-and-implementation.md`.

Phase-4 commands:

1. Capability focused test: PASS, 5 tests.
2. Plan-v2 import smoke: PASS.
3. TASK-077 Phase-3 + Capability regression after generic Candidate-auth refactor: initial FAIL because the extension family was specified incorrectly; corrected to exact `paired-semantic-input` / `bcrp:core-extension-envelope:1.0.0`; rerun PASS, 18 tests.
4. Synthetic NativeFixture generation-8 smoke: FAIL as evidence, with exact rejection `dangling paired target 'unit:dimensionless'`; no production weakening performed.
5. Generic/closure Plan-v2 focused test: initial test-harness TypeErrors; harness corrected; rerun PASS, 5 tests.
6. Final focused TASK-077 suite: PASS, 23 tests.
7. Relevant owner regressions: PASS, 48 tests.
8. Frozen TASK-076 validator: PASS.
9. Protected hash check: PASS.
10. Current implementation/test hash inventory: recorded above.

No command was denied after authorized resumption. No cache deletion or cleanup command was run.

## Residue

Previously observed `.pyc` files remain unmodified and undeleted. TASK-077 commands used `PYTHONDONTWRITEBYTECODE=1`. No claim is made that all residue predates TASK-077; no cleanup is necessary for the current blocker.

## Required decision

Keep TASK-077 active and Phase 4 in progress. Do not create a successor and do not advance to adversarial freeze/review.

Resolution requires one of:

1. explicit authorization for an isolated, temporary, non-publication synthetic lifecycle that produces a real `VerifiedPublicationRelease` for an exact generation-8-conforming Candidate solely to test Plan-v2 production admission; or
2. an already accepted generation-8 `VerifiedPublicationRelease` supplied from predecessor authority.

This does not authorize a real TASK-071 lifecycle, projection, rendering, Audit, conformance, Manifest, publication, or external action.
