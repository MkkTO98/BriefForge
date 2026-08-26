# TASK-077 Pre-Freeze Audit 1 — Authority, Closure, and Native Integration

Status: **FAIL — REMEDIATION BASELINE**
Date: 2026-08-11
Subject: pre-remediation TASK-077 production/test bytes recorded in `R-20260811-task-077-pre-remediation-path-manifest.json`

## Exact blockers

1. `verify_plan_v2_predecessor_closure` authenticated kind/order/topology but not complete independently bound record bytes. Direct probes admitted 36/36 complete-record substitutions: 8/8 minimal and 8/8 fully shaped substitutions in the eight-record closure; 10/10 minimal and 10/10 fully shaped substitutions in the ten-record closure.
2. Capability-v2 serialized bytes were transferable across independently valid Candidate chains when issuer inputs were unchanged. A direct cross-chain probe admitted unchanged Capability bytes against a different valid generation-8 Candidate and independently reconstructed foreign envelope.
3. TASK-077 created `NativeVerifiedPlanV2Handle` and a second process-local registry instead of integrating the existing `NativeBCRPPairedTerminalAdmissionHandle` owner. The duplicate lacked the existing owner’s TTL, reservation/commit/rollback lifecycle, issuer-family dispatch, and downstream integration.
4. The required 36 complete-record attack matrix was absent from committed TASK-077 tests.
5. The 63 frozen invalid fixtures were not directly ported through production entry points.
6. Native integration tests covered only the parallel TASK-077 handle, not the accepted native owner.
7. Valid cross-Candidate Capability transfer was untested.
8. Plan persistence attack coverage lacked second-write, residue, symlink, tampering, extra-inventory, stale same-shaped authority, and byte-transfer probes.

## Verified strengths

- Exact manifest loading, Candidate/envelope reconstruction, and full Plan reconstruction were materially stronger than the standalone closure verifier.
- Focused TASK-077 tests passed before this audit, but did not cover the attacks above.

## Ruling

Freeze blocked. Preserve every finding until production remediation and direct attack evidence close it.