# TASK-047 — BCRP Lifecycle Authority Decision and Legacy Compatibility Contract

Status: complete
Type: corrective architecture and compatibility implementation slice
Date: 2026-07-16

## Objective

Eliminate the parallel lifecycle-authority defect left by TASK-046. Preserve the existing governed BriefForge Candidate -> Validation Judgment -> Ready lifecycle as the sole current operational approval/promotion authority, separate BCRP technical validation from governance judgment, and add the smallest fail-closed boundary capable of representing an already-governed legacy lifecycle result in BCRP.

## Defect being corrected

TASK-046 implemented an independently executable native BCRP Candidate -> Judgment -> Ready path. L0-L2 technical success could manufacture a successful `ValidationJudgmentRecord`, and that record could independently produce BCRP Ready. Existing downstream code instead recognizes the governed legacy `ReadyPresentationPackage`. No accepted decision authorized a second operational authority or mapped the two lifecycles.

## Authorization basis

- direct human authorization and authority model for TASK-047;
- TASK-041's one Candidate -> Judgment -> Ready readiness lifecycle;
- TASK-042 authority separation and fail-closed behavior;
- TASK-043 layered validation and non-manufacture of governance approval;
- BCRP 1.0 extension and domain-scoped fingerprint rules accepted by TASK-044;
- TASK-045/046 implementation evidence and the corrective audit preceding this task.

## Bounded implementation slice

### In scope

1. Accept one lifecycle authority and legacy-compatibility contract.
2. Make BCRP L0-L2 execution return technical evidence, never governance Judgment.
3. Prevent native BCRP promotion without adapter-verified legacy authority.
4. Implement one compatibility module outside `briefforge.bcrp`.
5. Verify exact legacy Candidate/Judgment/Ready closure, policy translation, identity mapping, separate fingerprint domains, explicit lineage, staleness, competing evidence, and explicit BCRP semantic material.
6. Exercise actual TASK-039 evidence honestly, accepted golden case 1, TASK-046 native authoring, and a complete materially different synthetic closure.
7. Correct TASK-046's compatibility overclaim without rewriting history.

### Non-goals

- no renderer compatibility planning or invocation;
- no HTML/SVG, Publication Release, artifact, conformance, or manifest production;
- no AtlasForge integration or broad legacy migration;
- no new record kind, breaking BCRP change, second representation format, or financial-domain semantics;
- no network, database, package installation, external-project mutation, Git initialization, commit, or push.

### Success criteria

1. Existing governed runtime remains the sole current operational approval/promotion producer.
2. Technical validation cannot produce a successful lifecycle Judgment.
3. Native BCRP cannot self-promote.
4. A mapped BCRP Judgment/Ready pair can arise only from exact verified legacy lifecycle evidence plus explicit governed mapping material.
5. Legacy and BCRP fingerprints are preserved in named separate domains with explicit lineage and no equality claim.
6. Missing, stale, incomplete, ambiguous, unsuccessful, or competing evidence fails closed.
7. TASK-039 is reported as compatible or incompatible only to the extent its actual evidence proves.
8. A generic synthetic closure proves successful mapping without fixture/domain overfitting.
9. BCRP imports remain independent of legacy/runtime/renderer modules.
10. Full suite and project governance checks pass, with no unauthorized path changes.

## Contract and decision links

- Specification: `artifacts/specifications/bcrp-lifecycle-authority-and-legacy-compatibility.md`
- Decision: `artifacts/decisions/D-20260716-bcrp-lifecycle-authority-and-legacy-compatibility.md`
- Report: `artifacts/reports/R-20260716-bcrp-lifecycle-authority-and-legacy-compatibility.md`

## Preflight evidence

- Recovery: exit 0.
- TASK-047 availability: no task artifact existed before activation; earlier references were recommendations/audit discussion only.
- Repository: intentional non-Git filesystem tree.
- Fresh baseline manifest: `/tmp/briefforge-before-task047-authority-20260716.json`.
- Baseline included paths: 642.
- Baseline manifest digest reported by helper: `ccee49f21e878111ff2f96785379e262ffa7475c480fe4ecbbea24b018f51e69`.
- Pre-mutation complete suite: 190 tests passed.

## Post-slice gate

Report `RECONCILED` only if one authority, technical/governance separation, adapter fail-closure, explicit cross-domain lineage, truthful historical evidence, generalized proof, complete passing suite, and exact authorized mutation boundary are all proven. Otherwise report `NOT RECONCILED` and stop before renderer/publication work.

## Outcome

**RECONCILED.**

- BCRP L0-L2 now yields `TechnicalValidationResult`; it cannot create governed Judgment or Ready authority.
- Native BCRP promotion fails closed.
- The governed legacy lifecycle remains the sole current operational approval/promotion authority.
- A generalized compatibility adapter represents already-governed legacy evidence through one required, generically unsupported contract with exact closure, accepted policy/authority, complete inventory, lifecycle time/identity, separate-domain lineage and payload-consistency checks.
- The accepted trusted in-process/accepted-artifact input boundary is explicit: deterministic binding is not external authentication and no signature/token was invented.
- Actual TASK-039 history fails closed because required historical Judgment/Ready identities and validation/readiness times are absent; no values were inferred.
- TASK-046 task/report errata preserve valid historical test evidence while superseding the native BCRP lifecycle-authority claim.
- Focused suite: 23 tests, OK. Complete suite: 206 tests, OK. Fresh BCRP forbidden-module import inventory: `[]`.
- Accepted topology places L4 Publication Release governance before L5 compatibility planning even though the plan record directly references Ready plus renderer capability rather than Release.

Exactly one successor is recommended but not activated: `TASK-048 — BCRP Publication Release Authority, Production, and Lifecycle Proof`.

Canonical report: `artifacts/reports/R-20260716-bcrp-lifecycle-authority-and-legacy-compatibility.md`.
