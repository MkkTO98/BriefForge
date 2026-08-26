# TASK-047 — BCRP Lifecycle Authority and Legacy Compatibility Implementation Report

Date: 2026-07-16
Status: complete
Task: `artifacts/tasks/TASK-047-bcrp-lifecycle-authority-decision-and-legacy-compatibility-contract.md`
Decision: `artifacts/decisions/D-20260716-bcrp-lifecycle-authority-and-legacy-compatibility.md`
Specification: `artifacts/specifications/bcrp-lifecycle-authority-and-legacy-compatibility.md`

## 1. Objective

Reconcile the duplicate lifecycle authority introduced by TASK-046. Preserve the governed legacy Candidate -> Validation Judgment -> Ready runtime as the sole current operational approval/promotion authority; reduce BCRP L0-L2 execution to technical evidence; and add one explicit fail-closed compatibility boundary that can represent an already-governed legacy result without treating legacy and BCRP fingerprints as equal or granting downstream publication authority.

## 2. Context used

- `CONSTITUTION.md`, `AGENTS.md`, all project instructions, active state, architecture and latest handoff;
- TASK-039 Candidate/Judgment/Ready artifacts and demographic/correlation source evidence;
- TASK-041 through TASK-046 task/report/specification evidence;
- accepted BCRP topology, canonicalization/equality/versioning, object-graph/reference-authority and golden-corpus decisions;
- `src/briefforge/runtime.py`, `validation.py`, `promotion.py` as the governed operational lifecycle;
- `src/briefforge/bcrp/` structure, model, graph, canonicalization, validation, authoring and tests;
- accepted corpus cases and invalid mutations;
- project lifecycle-governance and implementation-slice procedures.

No network, database, dependency installation, AtlasForge/upstream access, renderer mutation, Git initialization, commit or push was used.

## 3. Authority finding

TASK-046 implemented a technically executable BCRP Candidate -> Judgment -> Ready path, but no accepted decision transferred governance approval/promotion authority from the existing runtime or created a second authority. That path was therefore an authority defect even though its tests passed.

Accepted correction:

1. the governed legacy Candidate/Judgment/Ready runtime remains the sole current operational approval/promotion authority;
2. BCRP L0-L2 success is technical evidence only;
3. native BCRP cannot manufacture a governance Judgment or Ready record;
4. an already-governed legacy result may be represented in BCRP only through the explicit compatibility contract;
5. native BCRP lifecycle authority requires a future accepted governance decision;
6. compatibility is representation, not approval, promotion, release, rendering, artifact acceptance or distribution authority.

## 4. Implementation

### 4.1 Technical-validation correction

`src/briefforge/bcrp/authoring.py` now:

- keeps Candidate authoring renderer-independent and limited to Brief, Portable Material and Candidate records;
- returns `TechnicalValidationResult` from `record_candidate_validation(...)`;
- preserves exact Candidate identity/fingerprint, executed L0-L2 layers, complete findings and pass/fail status;
- creates no `ValidationJudgmentRecord`;
- makes `promote_validated_candidate(...)` fail closed with `BCRPPromotionRejected`;
- retains the old promotion signature only so existing callers receive an explicit authority-boundary failure.

`src/briefforge/bcrp/__init__.py` exports the corrected technical result type.

### 4.2 Compatibility boundary

`src/briefforge/bcrp_legacy_compatibility.py` is outside `briefforge.bcrp` because it intentionally imports the governed legacy runtime/validation types. This preserves fresh BCRP package independence.

The adapter verifies:

- exact legacy Candidate/Judgment/Ready types;
- successful, finding-free Judgment;
- exact Candidate/Judgment/Ready closure;
- identity, policy and recomputed legacy fingerprint continuity;
- one exact accepted policy translation;
- BriefForge-owned `validation-authority` role;
- complete-scope evidence inventory, explicit empty competitor inventory and deterministic inventory binding;
- explicit evidence, mapping-attestation and lifecycle identities/times;
- exact BCRP Candidate identity/fingerprint and explicit cross-domain lineage;
- no pre-existing lifecycle/release/renderer/artifact/manifest records;
- no post-mapping Candidate mutation;
- exact persisted payload shape and Judgment/Ready cross-record consistency.

The compatibility extension is semantic, must-preserve, `criticality: required`, and names `briefforge:legacy-lifecycle-compatibility:1.0.0`. Generic BCRP validation intentionally blocks this unsupported required meaning. Only the dedicated verifier may admit the expected extension findings and then validate the exact payload.

### 4.3 Trust boundary

BriefForge accepts a trusted in-process/accepted-artifact boundary for this adapter. Governance provenance is an input precondition. The deterministic inventory digest detects mutation and inconsistency but is not a signature and does not authenticate an untrusted issuer. The adapter verifies structural/semantic closure, policy, authority representation and binding; it does not invent authenticated issuance. A future authenticated boundary would require a separately governed attestation artifact or trusted issuer decision.

This limitation is explicit in the accepted decision/specification and is not hidden behind a stronger “verified” claim.

## 5. TDD and failure behavior

Initial focused authority/compatibility tests failed before implementation, establishing RED for missing authority separation and compatibility behavior. The resulting focused suite proves:

- technically valid native Candidate cannot self-approve or self-promote;
- negative technical findings remain complete without becoming Judgment;
- one complete synthetic governed closure maps successfully;
- stale, unsuccessful, competing, mismatched or incomplete closure fails;
- missing semantic material is never inferred;
- unknown policy translation or wrong authority role fails;
- generic BCRP processing blocks mapped authority-critical extensions;
- payload additions, contradictions, persisted policy mutation and Candidate drift fail;
- legacy/BCRP fingerprint domains remain distinct with explicit lineage;
- mapped Ready grants no release, renderer, artifact, manifest or distribution authority;
- generalized synthetic case behavior avoids TASK-039 fixture specialization.

## 6. TASK-039 three-way proof

### 6.1 Actual legacy evidence

The archived TASK-039 Candidate, Judgment and Ready JSON were loaded through their real legacy runtime types. Candidate identity, successful Judgment, Ready closure and the legacy semantic digest remain inspectable.

### 6.2 Explicit BCRP semantic representation

The reduced TASK-039 Candidate semantics remain reproducible in BCRP with Candidate-semantic fingerprint:

`92df4a43e8be50b26d2bdd7bde5f3cea8b90222b44f9241285b9dfbeb9896532`

That value is a BCRP-domain fingerprint and is not equalized with the legacy digest.

### 6.3 Fail-closed compatibility outcome

The historical Judgment artifact has no Judgment evidence identity or validation time. The historical Ready artifact has no Ready evidence identity or readiness time. Those fields cannot be inferred from filesystem metadata, report prose, generation time, current time or golden-corpus fixtures. Therefore actual TASK-039 compatibility mapping correctly fails closed.

This does not invalidate TASK-039's historical governed legacy result. It proves that the archived evidence is insufficient for the stricter cross-representation compatibility contract.

## 7. TASK-046 historical correction

Explicit errata were appended without rewriting historical execution evidence:

- `artifacts/tasks/TASK-046-bcrp-candidate-authoring-and-existing-lifecycle-compatibility-proof.md`;
- `artifacts/reports/R-20260716-bcrp-candidate-authoring-and-lifecycle-compatibility.md`.

The errata preserve valid Candidate-authoring, golden-parity and 190-test evidence while superseding the unaccepted native BCRP Judgment/Ready authority and direct renderer-plan recommendation.

## 8. Independence and anti-overfitting

Production compatibility code contains no fixture paths, case IDs, task IDs or demographic/company special cases. The BCRP core package does not import legacy runtime, promotion, compatibility, renderer or downstream modules. Compatibility code remains outside the BCRP core package and follows no external references.

Static source scans parse the changed Python files and check dangerous dynamic-execution/deserialization patterns plus fixture/domain specialization. Final results are recorded in section 11.

## 9. Topology review

The accepted profile gives `RendererCompatibilityPlanRecord` direct dependencies on Ready and renderer capability; it does not contain a `release_ref`. Therefore Release is not a structural field-level prerequisite of the plan record.

However:

- accepted processing expectations order explicit governance/Release before compatibility planning;
- L4 is governance approval/Release and L5 is compatibility/plan;
- Publication Release owns stable publication identity, semantic publication version, evidence snapshots, lifecycle status, distribution scope and release authority;
- accepted artifact evidence later requires both Release and compatibility plan;
- mapped Ready explicitly grants no Release authority.

The correct workstream order is therefore to establish the Release authority/production boundary before implementing the L5 plan producer. This is an authority and lifecycle ordering decision, not a false claim that the plan schema directly references Release.

## 10. Gate verdict

**RECONCILED**, contingent only on the final mechanical results in sections 11-12 remaining successful.

The duplicate operational approval/promotion path has been removed. Technical validation, governed lifecycle authority and compatibility representation are now separate. The trusted-input limitation is explicit. No unresolved ownership or semantic contradiction blocks the next bounded task.

## 11. Verification results

Completed before final context closeout:

```text
Recovery
python3 tools/recover_session.py --project . --json
exit 0

Pre-mutation full suite
190 tests — OK

Focused authority/compatibility suite
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest tests.test_bcrp_authoring_lifecycle tests.test_bcrp_lifecycle_authority_compatibility -v
23 tests — OK

TASK-039 exact fail-closed proof
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest tests.test_bcrp_lifecycle_authority_compatibility.LegacyCompatibilityContractTests.test_actual_task039_evidence_fails_closed_without_historical_lifecycle_times -v
1 test — OK

Complete suite
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
206 tests — OK

Fresh BCRP import forbidden-module inventory
[]
```

One mistyped targeted command named a nonexistent test class and exited 1; it was a tooling invocation error, not a product/test failure. The corrected exact command above passed.

Additional final checks:

- changed-production AST parse and fixture/task/domain/dangerous-pattern scan: 3 paths parsed, 0 hits;
- fresh `briefforge.bcrp` forbidden-module inventory: `[]`;
- `python3 -B tools/architecture_reality_audit.py --project . --write-report`: exit 0, 0 blocks, 0 warnings;
- `python3 -B tools/context_health.py --project . --json`: exit 0, 0 blocks, 0 warnings after state/handoff hygiene;
- `python3 -B tools/check_coherence.py --project .`: exit 0, 0 blocks; one expected Historical Compatibility warning remains for retained EIP/MetaHarvest boundary references.

No repository inconsistency or governance inconsistency remained. The one retained coherence warning is a classified historical-compatibility notice, not a tooling/environment failure or execution blocker.

## 12. Filesystem accounting

Authoritative before-manifest:

`/tmp/briefforge-before-task047-authority-20260716.json`

Authoritative final after-manifest:

`/tmp/briefforge-after-task047-authority-20260716.json`

Before: 642 included paths. After: 648 included paths.

Added (6):

- `artifacts/decisions/D-20260716-bcrp-lifecycle-authority-and-legacy-compatibility.md`;
- `artifacts/reports/R-20260716-bcrp-lifecycle-authority-and-legacy-compatibility.md`;
- `artifacts/specifications/bcrp-lifecycle-authority-and-legacy-compatibility.md`;
- `artifacts/tasks/TASK-047-bcrp-lifecycle-authority-decision-and-legacy-compatibility-contract.md`;
- `src/briefforge/bcrp_legacy_compatibility.py`;
- `tests/test_bcrp_lifecycle_authority_compatibility.py`.

Modified (18):

- `artifacts/decisions/_SUMMARY.md`;
- `artifacts/reports/R-20260716-architecture-reality-audit.md`;
- `artifacts/reports/R-20260716-bcrp-candidate-authoring-and-lifecycle-compatibility.md`;
- `artifacts/reports/_SUMMARY.md`;
- `artifacts/specifications/_SUMMARY.md`;
- `artifacts/tasks/TASK-046-bcrp-candidate-authoring-and-existing-lifecycle-compatibility-proof.md`;
- `artifacts/tasks/_SUMMARY.md`;
- `context/latest_handoff.md`;
- `src/briefforge/_SUMMARY.md`;
- `src/briefforge/bcrp/_SUMMARY.md`;
- `src/briefforge/bcrp/__init__.py`;
- `src/briefforge/bcrp/authoring.py`;
- `state/active_goal.md`;
- `state/architecture.md`;
- `state/project_state.md`;
- `state/recent_changes.md`;
- `tests/_SUMMARY.md`;
- `tests/test_bcrp_authoring_lifecycle.py`.

Deleted: none.

Every delta belongs to TASK-047 implementation/tests, its governance/reporting, explicit TASK-046 errata, current-state continuity, affected summaries, or required audit evidence. No unrelated included path changed. Cache directories and bytecode are excluded by the authorized manifest helper; they were not deleted or treated as task-owned evidence.

## 13. Exactly one recommended next task

`TASK-048 — BCRP Publication Release Authority, Production, and Lifecycle Proof`

Bounded objective:

- accept one exact governed BCRP Ready representation through an admitted authority boundary;
- require explicit Publication Release authority, stable publication lineage, semantic publication version, exact evidence-snapshot closure, release time/status and distribution constraints;
- produce and validate one `PublicationReleaseRecord` without renderer-plan, rendering, artifact, conformance or manifest production;
- prove correction, rerender/non-semantic change, supersession, withdrawal and staleness distinctions fail closed where not explicitly authorized;
- preserve DSB-007 and AtlasForge independence.

Why this is correctly bounded: it establishes L4 publication identity/lifecycle authority after Ready and before L5 compatibility planning, without combining Release with renderer capability reconciliation or artifact production. The task is recommended only and is not activated.
