# TASK-050 — BCRP Publication Release Authority, Production, and Lifecycle Proof

Status: completed — CLEAR TO PROCEED
Type: bounded Release-authority contract and implementation proof
Date: 2026-07-16

## Objective

Implement and prove the governed boundary:

```text
exact TASK-047-verified governed BCRP Ready
-> explicit immutable Publication Release authorization
-> exactly one immutable PublicationReleaseRecord
```

The Release binds publication identity/version, exact Candidate/Judgment/Ready and legacy/BCRP lineage, one fixed evidence-snapshot closure, Release policy and authority, authorization/Release identities and times, initial active state, and explicit distribution constraints.

## Readiness and Phase-1 result

- Normal bounded recovery passed.
- TASK-050 had no task artifact before human activation; prior mentions were recommendations only.
- The intentionally non-Git baseline contained 663 included paths and 239 passing tests.
- L4 admits a Release-stage bundle without a Manifest.
- TASK-047's exact five-record verifier can be composed with six-record L0–L4 validation while generic BCRP remains fail closed on required compatibility extensions.
- Existing core Release lineage plus the Candidate fingerprint can bind the fixed evidence closure without a new record kind. Explicit authorization material requires one Release-owned required semantic extension because core BCRP has no authorization/policy carrier.
- Exactly one Release root is representable.
- TASK-049 admits that Release as a zero-event initial anchor without changing its fingerprint.

Phase-1 gate: **PASS — proceed with bounded implementation**.

## Implementation boundary

Add one renderer-independent module outside `briefforge.bcrp` that owns:

- immutable evidence-snapshot input and deterministic inventory digest;
- immutable Release authorization under one accepted policy translation;
- one producer accepting only exact TASK-047 governed Ready;
- one independent persisted-record verifier;
- narrow reconciliation of only the exact verified TASK-047 and TASK-050 required-extension findings;
- exact TASK-049 Release-binding compatibility.

## Non-goals

No native Ready promotion; lifecycle-event production; renderer capability or plan; rendering; HTML/SVG; artifacts; conformance; Publication Manifest; distribution execution; AtlasForge; database/network; financial semantics; broad migration; second representation.

## Success criteria

1. Only an exact TASK-047-verifiable mapped Ready can produce Release.
2. Release authority is separate from Candidate authoring, validation, Judgment, Ready, mapping, lifecycle events, renderer, artifact, manifest and distribution.
3. Explicit identity/version/lineage/snapshot/authority/time/constraints are deterministic and immutable.
4. Exactly one Release is produced; no event or Manifest is created.
5. Persisted verification recomputes all closures and fingerprint and fails closed on drift, unknown fields or competing authority.
6. Generic BCRP still rejects all required authority-critical extensions.
7. TASK-049 projection leaves Release identity/fingerprint unchanged.
8. Generalized tests and full governance checks pass with no unauthorized path changes.

## Mandatory stop

Stop before renderer compatibility planning, rendering, artifact production, manifest production or distribution. Do not activate another task.

## Outcome

Completed the exact six-record production and persisted-verification boundary in `src/briefforge/publication_release.py` under `briefforge-publication-release-policy:1.0.0`.

- One authority-issued authorization targets exactly one semantic Release act: publication/version, complete governed-Ready closure, fixed evidence snapshot, Release identity/time, recommendation state and exact constraints.
- The Release extension binds the exact five-record `profile-instance` fingerprint, so its `release-semantic` fingerprint commits to Candidate/Judgment/Ready and compatibility lineage without adding a core kind.
- Verified state is immutable serialized text; exposed bundle/record values are detached copies and TASK-049 projection re-verifies before binding.
- Generic BCRP remains fail closed on exactly three unsupported required extensions while the specialized verifier preserves every unrelated finding.
- TASK-049 zero-event and later-event processing preserve Release identity and fingerprint.
- No downstream renderer, artifact, Manifest, distribution or lifecycle-event production authority was added.

Verification: 16 focused TASK-050 tests, 66 focused TASK-047/TASK-049/TASK-050 tests and 255 full-suite tests passed. Independent adversarial review passed after correcting three initial blockers: exact Release-act targeting, immutable verified output and full governed-Ready closure binding.

Gate: **CLEAR TO PROCEED**.

Recommended but unactivated: `TASK-051 — BCRP Renderer Compatibility-Plan Production and Fail-Closed Proof`.
