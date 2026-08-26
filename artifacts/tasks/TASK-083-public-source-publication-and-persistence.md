# TASK-083 — Public-source publication and governed persistence

Status: COMPLETED
Date: 2026-08-26

## Objective

Establish BriefForge as a rights-aware public source repository and activate exact-path automatic Git persistence for governed completed tasks and explicitly eligible milestones.

## Public-source result

- Public repository: `https://github.com/MkkTO98/BriefForge`
- Baseline commit: `a2f7fb0047be41495117f5ad6c121fadc7ec9568`
- Baseline tree: exactly 904 audited paths from `publication/initial-candidate-manifest.json`.
- Restricted upstream inputs, derived publications, replay/verification payloads, machine configuration, and campaign source that embeds restricted derived content remain local only.
- The public Git repository is authoritative for distributable source, not a complete archive of restricted runtime material.

## Persistence result

- Exact-path helper: `tools/public_persistence.py`
- Mandatory policy gate: `publication/public-source-policy.json`
- Trigger: authoritative task `COMPLETED`, `ACCEPTED`, or fully reconciled `CLOSED`; or an explicitly persistence-eligible milestone.
- Non-triggers: `BLOCKED`, `PARTIAL`, `FAILED`, `INCOMPLETE`, and `WAITING_DECISION`.
- The standard Hermes closeout contract now requires the helper as its final eligible closeout act.

## Verification

- Publication-policy and persistence suite: 14 tests passed.
- TASK-081 restricted-fixture integration suite: 9 tests passed when supplied through explicit `BRIEFFORGE_LOCAL_*` paths.
- Coherence: 0 blockers; 2 pre-existing informational context warnings.
- Disposable negative paths prove sensitive candidate rejection, unrelated dirt rejection, invalid terminal-state rejection, push-failure preservation, exact staging, local-only outcomes, parity, and idempotence.

## Outcome

COMPLETED. This task's final six-path activation change set is the genuine production closeout used to prove automatic commit, push, and remote parity.
