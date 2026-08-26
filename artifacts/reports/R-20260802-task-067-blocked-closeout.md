# TASK-067 Blocked Closeout Review

Date: 2026-08-02
Disposition: `BLOCKED / NOT RECONCILED`
Task: `TASK-067-versioned-terminal-profile-and-paired-table-capability-implementation.md`

## Scope

This report preserves the final adversarial review findings reached after implementation and test expansion. It is not completion authority, representative Candidate authority, Publication Release authority, delivery authority, or permission to activate a successor.

## Verified evidence before the final review

- Complete suite: 604 tests passed in 263.658 seconds with bytecode disabled.
- Focused TASK-067 suite: 64 tests passed.
- Historical TASK-062 suite: 17 tests passed.
- Dangerous-call scan: no prohibited dynamic execution, subprocess, network, or database calls found in the paired package.
- Cache/bytecode scan: clean.
- BCRP import boundary: clean.

After the incomplete canonical-extension correction, the focused TASK-067 suite passed 64 tests in 1.457 seconds and the complete suite passed 604 tests in 255.434 seconds. These tests do not resolve the independent review blockers and are not completion authority.

## Blocking findings

### 1. Canonical BCRP extension representation

The paired DTO legitimately contains optional values represented internally as `None`. Directly embedding the DTO as an extension payload object makes BCRP canonicalization reject JSON nulls. Encoding the DTO as one canonical JSON string is a promising bounded boundary because it keeps extension-owned identities and nulls opaque to the unchanged core graph while retaining deterministic reconstructability.

The started implementation is incomplete: the produced extension lacks the full exact BCRP extension envelope and has not passed a genuine unpatched Publication Release verification path. Required reconciliation includes `authority_ref`, `scope`, `target_refs`, `character`, and accepted required-extension validation-contract semantics. Historical BCRP core behavior and the eleven-kind invariant must not be changed merely to admit the profile.

### 2. Controlled invocation directory continuity

The output and evidence directory paths can be replaced after path validation but before descriptor opening. The opened descriptor must be proven to have the same device/inode as the object admitted by path validation. A deterministic directory-swap regression test is required for both boundaries.

### 3. Independent N+1 evidence

The obligation-target and provenance-target overflow tests currently append a duplicate identity. They therefore mutate cardinality and uniqueness simultaneously. Replace each appended value with a valid resolving identity that is absent from the original frontier, proving cardinality alone causes rejection.

## Preserved boundaries

- TASK-067 remains active; it is not completed.
- TASK-068 remains unused and unactivated.
- No representative Candidate, Release, delivery, deployment, browser proof, or TASK-056 evidence was created.
- Repository remains intentionally non-Git.
- No network, database, dependency installation, remote mutation, or upstream-project mutation was performed.

## Resume order

1. Complete and independently prove the BCRP extension representation through an unpatched verified Release path.
2. Close controlled-invocation descriptor identity continuity and add swap tests.
3. Repair the two independent N+1 tests.
4. Run focused, historical, and full suites.
5. Obtain fresh independent architecture, security/filesystem, and test-adequacy PASS reviews.
6. Only then complete final accounting and consider TASK-067 completion.
