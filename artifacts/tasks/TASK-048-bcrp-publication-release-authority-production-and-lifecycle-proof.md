# TASK-048 — BCRP Publication Release Authority, Production, and Lifecycle Proof

Status: blocked at Phase 1; source implementation not started
Type: architecture-reconciliation gate before implementation
Date: 2026-07-16

## Objective

Establish the governed boundary from one exact adapter-verified BCRP Ready representation to one immutable `PublicationReleaseRecord`, with explicit publication identity/version, evidence-snapshot closure, release authority/policy/time, lineage and distribution constraints, while granting no renderer, artifact, conformance, manifest or distribution-execution authority.

## Authorization basis

- direct human authorization for TASK-048;
- accepted TASK-041 through TASK-047 semantics and authority boundaries;
- TASK-047's governed legacy lifecycle compatibility contract;
- BCRP 1.0 topology, canonicalization, validation layers and corpus evidence.

## Bounded phases

1. Reconcile accepted Publication Release semantics against executable BCRP 1.0.
2. Only if representable, establish the Release authority contract.
3. Only after accepted contract and RED evidence, implement deterministic Release production.
4. Verify authority separation, lifecycle distinctions, independence and bounded filesystem mutation.

## Non-goals

- no renderer compatibility-plan or capability production;
- no renderer selection/invocation, HTML/SVG, interaction or artifact production;
- no artifact conformance, `PublicationManifestRecord`, distribution execution or AtlasForge integration;
- no broad migration, second representation format or financial-domain semantics;
- no Git initialization, network, database, dependency installation, commit or push.

## Preflight evidence

- Recovery command exited 0.
- `TASK-048` had no pre-existing task artifact; prior mentions were recommendations only.
- Repository remains intentionally non-Git.
- Fresh baseline manifest: `/tmp/briefforge-before-task048-20260716.json`.
- Baseline included paths: 648.
- Baseline manifest digest reported by the established helper: `89d16086a604434c316ae68052dfa98d282f4f9360fa98949671c93c98e5ef19`.
- Pre-mutation complete suite: 206 tests passed.

## Phase 1 result

**BLOCKED.** BCRP 1.0 cannot represent the accepted immutable publication lifecycle honestly.

The profile provides one `PublicationReleaseRecord` with mutable-looking `lifecycle_status`, but no independently addressable publication lifecycle-event record. Accepted doctrine requires withdrawal, staleness and supersession to point to later authoritative events without rewriting the prior Release. Appending an embedded event changes the Release's `release-semantic` digest; creating a second Release falsely asserts a second publication act and conflicts with the executable exactly-one-Release assumptions.

The gap is architecture-caused, not a local validator defect. Per the task's stop rule, no Release authority specification/decision, RED tests, producer, validator extension or source implementation was created. No ambiguous field, optional prose, or required extension was used to simulate immutable lifecycle history.

## Evidence and report

Canonical reconciliation report:

`artifacts/reports/R-20260716-task-048-publication-release-representation-gap.md`

The report contains the field-and-authority matrix, adversarial runtime probes, exact representation gap, gate verdict and the one unactivated profile-evolution recommendation.

## Outcome

**BLOCKED / NOT RECONCILED.** Phase 1 is complete. TASK-048 remains blocked rather than being misreported as an implementation success.

Required intervening work, not activated: **BCRP append-only publication lifecycle-event profile evolution and corpus proof**. It must decide an independently identifiable event topology and version impact, then specify canonicalization, fingerprinting, L3/L4 authority, immutable correction/supersession/withdrawal/staleness lineage, and generalized positive/adversarial corpus cases.

Historical identifier note: the unactivated renderer-compatibility placeholder formerly labelled `TASK-049` was never activated and is superseded by the human-authorized allocation of `TASK-049` to the required append-only lifecycle-event work. Renderer compatibility planning remains deferred to a later identifier and is not recommended while Release production remains incomplete.
