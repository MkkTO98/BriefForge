# R-20260717 — TASK-051 BCRP Renderer Compatibility-Plan Production and Fail-Closed Proof

Date: 2026-07-17
Status: Complete
Task: TASK-051
Gate: **CLEAR TO PROCEED**

## Executive result

BriefForge now has a renderer-independent compatibility-planning boundary:

```text
independently reverified immutable Publication Release
+ explicitly complete graph-validated lifecycle scope
+ exact immutable renderer-owned capability declaration
+ exact BriefForge planning authorization
-> one deterministic RendererCompatibilityPlanRecord OR complete blocking findings and no Plan
```

TASK-051 reused the existing BCRP `RendererCapabilityDeclarationRecord` and `RendererCompatibilityPlanRecord`; it did not add a record kind or infer capability from renderer code. Generic BCRP remains fail closed and retains exactly eleven record kinds.

The implementation stops before renderer selection/invocation, output generation, artifact/audit evidence, semantic conformance, `PublicationManifestRecord`, distribution, network or external I/O.

## Phase 1 representation and authority gate

| Required topology | Existing carrier | Reconciliation | Verdict |
|---|---|---|---|
| Immutable Release | `PublicationReleaseRecord` plus TASK-050 required extension | Reverify exact six-record Release closure and evidence snapshot | sufficient |
| Current lifecycle state | TASK-049 companion profile | Require explicit complete Release/event/policy catalog, digest it, validate graph, derive exact sole current Release | sufficient |
| Renderer capability evidence | `RendererCapabilityDeclarationRecord` | Add exact renderer-owned versioned declaration contract and complete immutable fingerprint-bound inventory | sufficient through specialized contract |
| Requirement inventory | Candidate `renderer_requirements` | Require exact target identities, criticality, constraints, transformations, fallbacks and optional unsupported authority | sufficient through TASK-051 contract |
| Fallback authority | Candidate `fallbacks` | Require closed kind/mode vocabulary, complete coverage and preservation of authority/caveat identities | sufficient |
| Plan topology | `RendererCompatibilityPlanRecord` | Bind Release/Ready/Candidate/evidence/lifecycle/declaration/authorization and exact per-requirement outcomes in one required extension | sufficient through specialized contract |
| Blocking outcome | no core blocking record exists or is needed | Return deterministic findings outside the BCRP usable-Plan closure; produce zero Plan records | sufficient |
| Persisted verification | no pre-existing specialized verifier | Independently reproduce and byte-compare exact eight-record closure | implemented |

Gate result: representation was sufficient without changing the eleven-kind profile, mutating the Release, inventing a blocking Plan, or importing renderer authority.

## Implemented contracts

Accepted identities:

- policy: `briefforge-renderer-compatibility-planning-policy:1.0.0`;
- capability declaration: `briefforge:renderer-capability-declaration:1.0.0`;
- Plan: `briefforge:renderer-compatibility-plan:1.0.0`;
- authorization: `briefforge:renderer-compatibility-planning-authorization:1.0.0`;
- capability profile: `briefforge-renderer-capability-profile:1.0.0`.

The declaration binds renderer identity/version, owner/role, declaration time, exact supported claims, explicit unsupported identities, constraints, extensions, complete-inventory assertion and SHA-256 fingerprint. It is a renderer-owned claim, not output/conformance proof.

The Plan binds:

- exact TASK-050 Release identity and `release-semantic` fingerprint;
- Ready and Candidate fingerprints;
- fixed evidence snapshot;
- exact complete TASK-049 lifecycle catalog, digest and graph-derived current state;
- exact capability declaration identity/fingerprint/profile/renderer version and full inventory;
- exact planning authorization/policy/authority/times;
- one outcome for every renderer requirement;
- affected semantic identities, criticality, mode, capability, fallback, transformation and deterministic reason;
- explicit exclusions for renderer selection/invocation/output, artifacts, conformance, Manifest and distribution.

## Deterministic outcome policy

For each requirement, in order:

1. exact native claim satisfying constraints;
2. exact predeclared complete equivalent expression;
3. exact predeclared complete static expression;
4. explicit unsupported only when the requirement is governed optional and the declaration explicitly marks the capability unavailable;
5. otherwise blocking.

Same-rank ambiguity blocks. A fallback must have one accepted kind consistent with its mode and preserve all target meaning, authority labels, caveats and authorized transformations. Required meaning cannot become unsupported.

If any requirement or global prerequisite blocks, all determinable findings are returned and no usable Plan exists. A blocking result is not serialized as `supported=false` Plan evidence.

## Lifecycle proof

Planning requires an explicit `LifecyclePlanningScope` containing immutable tuples of exact lifecycle events, Release bindings and policies. Omission is not interpreted as an empty catalog. The planner:

1. recomputes the complete inventory digest;
2. runs TASK-049 lifecycle validation;
3. derives state from the graph;
4. requires the exact planned Release to be the sole current Release;
5. rejects withdrawn, superseded, orphaned, stale/incomplete, conflicting, malformed or ambiguous evidence.

The valid zero-event case is explicit and fingerprint-bound.

## Persisted verification proof

`verify_renderer_compatibility_plan()` accepts only an exact immutable `BCRPBundle` containing exactly one each of:

- Brief;
- Portable Material;
- Candidate;
- Judgment;
- Ready;
- Release;
- renderer capability declaration;
- renderer compatibility Plan.

It reconstructs the six-record Release closure, independently re-runs TASK-050 verification, reproduces TASK-051 planning from the supplied exact lifecycle/declaration/authorization material, byte-compares the closure and recomputes the `profile-instance` fingerprint. Tamper, stale lifecycle/declaration/Release evidence, duplicate or missing mappings, mutable/malformed envelopes and downstream records fail closed.

## Adversarial review corrections

Three independent review rounds found and drove correction of:

- mutable nested capability inventories accepted as immutable;
- fallback `kind` not governed against expression mode;
- malformed lifecycle members escaping as exceptions;
- unhashable malformed capability identity and fallback mode values escaping as exceptions;
- mutable nested lifecycle policy inventories;
- malformed or mutable persisted BCRP bundle envelopes.

All received regression tests. The final remaining high finding was corrected by exact `BCRPBundle`/tuple/record checks and its focused regression test passed. No uncorrected blocker or high-severity finding remains.

## Evidence

Implementation:

- `src/briefforge/renderer_compatibility_planning.py`

Tests:

- `tests/test_renderer_compatibility_planning.py`

Governance:

- `artifacts/tasks/TASK-051-bcrp-renderer-compatibility-plan-production-and-fail-closed-proof.md`
- `artifacts/decisions/D-20260717-renderer-compatibility-planning-authority-and-fail-closed-result.md`
- `artifacts/specifications/renderer-compatibility-planning.md`

## Verification and formal closeout

- TASK-051 focused: 19 tests, OK.
- TASK-047/TASK-049/TASK-050/TASK-051 focused: 85 tests, OK.
- Full implementation suite after final continuity edits: 274 tests, OK.
- Architecture-to-reality audit: 0 blocks, 0 warnings.
- Context health: 0 blocks, 0 warnings.
- Coherence: 0 blocks; one intentional Historical Compatibility warning for retained ecosystem references.
- Recovery: TASK-051 completed, `CLEAR TO PROCEED`, no active task, TASK-052 recommended but unactivated.
- Static import/invocation boundary scan: no renderer/HTML/SVG/Manifest import or call evidence.
- Security-pattern scan: no findings.
- BCRP core record kinds: exactly 11.
- Python bytecode/cache scan after removal of reviewer-created cache residue: zero paths.

## Preliminary exact filesystem accounting

The established deterministic manifest changed from 670 to 678 included paths: 8 additions, 15 changed files, no deletions, no type changes and no symlink-target changes. The eight additions are:

- `artifacts/decisions/D-20260717-renderer-compatibility-planning-authority-and-fail-closed-result.md`
- `artifacts/reports/R-20260717-task-051-bcrp-renderer-compatibility-plan-production-and-fail-closed-proof.md`
- `artifacts/specifications/renderer-compatibility-planning.md`
- `artifacts/tasks/TASK-051-bcrp-renderer-compatibility-plan-production-and-fail-closed-proof.md`
- `src/briefforge/publication_lifecycle/_SUMMARY.md`
- `src/briefforge/renderer_compatibility_planning.py`
- `tests/fixtures/publication_lifecycle/_SUMMARY.md`
- `tests/test_renderer_compatibility_planning.py`

The fifteen changed files are:

- `artifacts/decisions/_SUMMARY.md`
- `artifacts/reports/R-20260717-architecture-reality-audit.md`
- `artifacts/reports/_SUMMARY.md`
- `artifacts/specifications/_SUMMARY.md`
- `artifacts/tasks/_SUMMARY.md`
- `context/latest_handoff.md`
- `src/briefforge/_SUMMARY.md`
- `src/briefforge/bcrp/_SUMMARY.md`
- `state/active_goal.md`
- `state/architecture.md`
- `state/project_state.md`
- `state/recent_changes.md`
- `tests/_SUMMARY.md`
- `tests/fixtures/_SUMMARY.md`
- `tests/fixtures/bcrp/_SUMMARY.md`

All are implementation, test, TASK-051 governance, architecture audit, continuity or generated-summary paths authorized by the bounded task. The authoritative final post-manifest must be created after this evidence write and must reproduce this exact classification before repository-level closeout is claimed.

## Boundary confirmation

No renderer was selected, probed or invoked. No HTML/SVG, artifact, audit-link evidence, semantic conformance, `PublicationManifestRecord` or distribution output was created. No network, database, dependency install, AtlasForge/upstream mutation or external authentication was used.

## Gate

**CLEAR TO PROCEED**

The accepted BCRP representation can carry one deterministic compatibility Plan while preserving Release immutability, lifecycle closure, semantic completeness, generic fail-closed behavior and downstream authority separation.

## Exactly one next task

Recommend but do not activate:

`TASK-052 — Controlled Renderer Invocation and Publication Artifact-Evidence Boundary Proof`

It is correctly bounded because TASK-051 has established planning eligibility but explicitly grants no execution or output authority. TASK-052 should consume only an independently verified eligible TASK-051 Plan plus exact renderer identity/version, invoke only the planned renderer under a controlled boundary, and produce generated artifact/audit-link evidence without yet claiming semantic artifact conformance, producing a Publication Manifest or distributing anything.
