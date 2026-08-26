# TASK-051 — BCRP Renderer Compatibility-Plan Production and Fail-Closed Proof

Status: completed — CLEAR TO PROCEED
Type: bounded renderer-independent compatibility-planning contract and implementation proof
Date: 2026-07-17

## Objective

Implement and prove:

```text
independently verified immutable TASK-050 Release
+ explicit complete-scope TASK-049 lifecycle evidence yielding that exact Release as active
+ immutable renderer-owned capability declaration
+ explicit BriefForge planning authorization
-> deterministic compatibility result
```

Exactly one `RendererCompatibilityPlanRecord` may be produced only when every Candidate renderer requirement has exactly one policy-authorized outcome. Blocking compatibility returns complete findings and no Plan record.

## Phase-1 representation gate

**PASS — bounded required semantic extensions are necessary and sufficient.**

Existing BCRP topology already requires one core `RendererCapabilityDeclarationRecord` and one core `RendererCompatibilityPlanRecord`; no record kind is added and the eleven-kind core remains unchanged. Core Plan fields bind Ready and capability-record identity, but do not directly bind Release, publication, evidence snapshot, lifecycle scope, declaration fingerprint, per-requirement outcomes, or planning authority. Core capability fields do not bind owner/role, declaration/profile identity and time, complete inventory, constraints, or declaration fingerprint.

The admitted refinement is therefore:

- strict renderer-declaration semantics plus one required declaration extension;
- strict Plan core semantics plus one required Plan extension;
- direct Release/Ready/Candidate/snapshot/publication, lifecycle-catalog, declaration, policy, authorization, and mapping bindings in that Plan extension;
- independent specialized verification while generic BCRP continues to fail closed on unnegotiated required extensions.

A blocked attempt is a technical `CompatibilityPlanningResult` with complete findings and no BCRP Plan record. It is not an executable or usable Plan. This avoids falsely representing unexpressible required meaning as a Plan.

An omitted lifecycle catalog is not accepted. An explicitly complete empty event inventory is accepted only when its digest and exact Release catalog are supplied and graph derivation yields the planned Release as the sole current active Release. No archival planning policy is introduced.

## Implementation boundary

Add one renderer-independent module outside `briefforge.bcrp` that owns:

- immutable renderer capability declarations and deterministic declaration fingerprints;
- complete lifecycle-scope bindings and deterministic inventory fingerprints;
- exact BriefForge planning authorization/policy checks;
- deterministic ordered native/equivalent/static/unsupported/blocking resolution;
- one producer and one persisted-content verifier;
- immutable verified Plan closure and stale-binding eligibility checks.

## Non-goals

No renderer selection, import, invocation, probing, runtime detection, HTML/SVG, interaction runtime, artifact, conformance, Publication Manifest, distribution, AtlasForge, network/database, upstream mutation, financial semantics, or second representation.

## Success criteria

1. Exact TASK-050 Release re-verification and exact TASK-049 lifecycle closure are prerequisites.
2. Only the sole active current Release is eligible; stale, superseded, withdrawn, incomplete or ambiguous evidence blocks.
3. Renderer declaration identity/version/owner/role/profile/time/inventory/constraints and fingerprint are explicit and immutable.
4. Every requirement receives exactly one outcome under the accepted ordering.
5. Fallbacks are exact Candidate-declared expressions; completeness and semantic/authority/caveat coverage are verified.
6. Optional explicit unsupported remains distinct and cannot erase required meaning.
7. Blocking returns complete findings and no Plan.
8. Persisted Plan verification detects content drift and every stale binding.
9. Generic BCRP remains fail closed and retains eleven core kinds.
10. Generalized tests and full governance checks pass with exact filesystem accounting.

## Mandatory stop

Stop before renderer selection/invocation, artifact output/evidence/conformance, Manifest, or distribution. Do not activate another task.

## Outcome

Completed on 2026-07-17 with **CLEAR TO PROCEED**.

- Implemented `src/briefforge/renderer_compatibility_planning.py` with exact immutable capability declarations, complete lifecycle closure, planning authorization, deterministic outcome resolution, blocked findings/no-Plan semantics, immutable verified output and persisted reproduction/verification.
- Added `tests/test_renderer_compatibility_planning.py` with 19 focused tests covering two materially different valid cases and adversarial Release/snapshot/lifecycle/declaration/requirement/fallback/mapping/persisted-bundle failures.
- Corrected all blocker/high-severity findings from three independent adversarial review rounds.
- Verified 19 TASK-051 tests, 85 focused TASK-047/049/050/051 tests and 274 full-suite tests.
- Preserved generic BCRP fail-closed behavior, exactly eleven core record kinds and renderer/import independence.
- Stopped before renderer selection/invocation, artifact output/evidence/conformance, Manifest or distribution.

Canonical report: `artifacts/reports/R-20260717-task-051-bcrp-renderer-compatibility-plan-production-and-fail-closed-proof.md`.

Exact closeout accounting: 670 -> 678 included paths; 8 additions and 15 content changes; no deletion, type change or symlink-target change. The canonical report contains the complete path lists.

Exactly one next task is recommended but unactivated: `TASK-052 — Controlled Renderer Invocation and Publication Artifact-Evidence Boundary Proof`.
