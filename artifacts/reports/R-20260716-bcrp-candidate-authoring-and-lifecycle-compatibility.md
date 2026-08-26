# TASK-046 BCRP Candidate Authoring and Lifecycle Compatibility Report

Date: 2026-07-16
Status: accepted implementation evidence
Task: `TASK-046 — BCRP Candidate Authoring and Existing-Lifecycle Compatibility Proof`

## 1. Executive verdict

**CLEAR TO PROCEED**, but only to a renderer-independent compatibility-plan producer—not renderer invocation.

TASK-046 proves that BCRP Candidate-stage records can be authored without semantic inference, validated under explicit L0-L2 authority, bound to an inspectable Validation Judgment, and promoted to Ready only when the exact Candidate remains unchanged. The reduced TASK-039-derived proof is semantically and fingerprint-equivalent to accepted golden case 1. A structurally different second case proves the implementation is not a fixture-specific adapter.

## 2. Context used

- `CONSTITUTION.md`, `AGENTS.md`, all project instructions;
- current active goal, project state, architecture, and latest handoff;
- TASK-039 task and historical Candidate/Judgment/Ready evidence;
- TASK-041 through TASK-045 specifications, tasks, reports, and accepted BCRP record/lifecycle authority;
- current BCRP model, canonicalization, structure, validation, corpus, fixtures, and tests;
- existing legacy runtime, validation, promotion, builder, and renderer-independence evidence.

## 3. Baseline and safety

- BriefForge remains an intentional non-Git filesystem tree.
- Fresh non-Git baseline: `/tmp/briefforge-before-task046-20260716.json`.
- Baseline inventory: 638 included paths.
- Pre-implementation suite: 183 tests, all passing.
- Existing unrelated files were preserved.
- No fetch, network, database, package install, upstream mutation, Git initialization, commit, or push occurred.
- No `compileall` was run.

## 4. Producer boundary

### Explicit drafts, not semantic automation

`RecordDraft` carries only explicit identity, semantic content, and extensions. Named function parameters assign exactly these roles:

1. `PresentationBriefRecord`;
2. `PortablePresentationMaterialRecord`;
3. `CandidatePresentationPackageRecord`.

The caller cannot use a `record_kind` draft field to create Judgment, Ready, release, renderer, artifact, conformance, or manifest authority. The producer deep-copies all input and introduces no semantic defaults, IDs, values, postures, purposes, audiences, sections, obligations, fallbacks, or upstream meaning.

### Candidate admission

`author_candidate_bundle(...)` creates one bounded in-memory BCRP 1.0 closure and executes L0-L2. Blocking findings reject the closure with the original layer/family/message. The producer does not repair, infer, dereference external references, query upstream systems, load fixtures, or serialize a second representation.

## 5. TASK-039 compatibility proof

The compatibility test authors Brief + Portable Material + Candidate from the accepted reduced TASK-039-derived golden case through the production API, not by returning the fixture bundle.

Actual assertions:

- exact authored inventory: Brief, Material, Candidate only;
- L0-L2 result: non-blocking;
- `semantic_equal(golden, authored)`: true;
- candidate-semantic fingerprint equality: true;
- resulting digest: `92df4a43e8be50b26d2bdd7bde5f3cea8b90222b44f9241285b9dfbeb9896532`.

The proof does not claim that the reduced BCRP fixture is byte-identical to the larger historical runtime artifact. It proves compatibility with the accepted TASK-039-derived BCRP semantics selected in TASK-044/045. Historical TASK-039 files, HTML/SVG, renderer audit metadata, and known table-metadata inconsistency remain unchanged.

## 6. Anti-overfitting proof

Golden case 2 is authored through the same API and remains semantically equal to its accepted source. Its fictional-company comparison, explicit missing/zero states, and recommendation posture differ materially from case 1.

The production module contains:

- no fixture paths;
- no case IDs;
- no TASK-039 identifiers;
- no demographic, correlation, company, or financial vocabulary;
- no `corpus.py` import;
- no renderer/runtime import.

Therefore the TASK-039 result is an instance-level compatibility proof, not hard-coded implementation behavior.

## 7. Lifecycle-authority proof

### Judgment

`record_candidate_validation(...)`:

- requires exactly one Candidate-stage closure and no existing lifecycle records;
- executes exactly L0-L2;
- records `executed_layers: [L0, L1, L2]`;
- binds the exact Candidate identity and candidate-semantic fingerprint;
- retains every complete deterministic finding;
- emits `valid: false` for blocking candidates rather than suppressing the Judgment;
- creates no Ready implicitly.

This avoids the false authority claim that L3-L6 ran before the required release, renderer, and artifact records existed.

### Ready

`promote_validated_candidate(...)`:

- requires exactly one successful L0-L2 Judgment;
- rejects finding-bearing or invalid Judgments;
- reruns Candidate validation;
- rejects Candidate identity/fingerprint drift after Judgment;
- creates one Ready binding to the Candidate and exact Judgment;
- refuses bundles already containing Ready or Publication Release authority.

Ready fingerprint follows the existing BCRP 1.0 corpus convention:

```text
sha256(ready_identity + "|" + candidate_semantic_fingerprint)
```

Ready does not establish Publication Release, renderer compatibility, artifact acceptance, or manifest/catalogue authority.

## 8. Existing-lifecycle compatibility

The legacy `runtime.py`, `validation.py`, `promotion.py`, `builder.py`, renderer modules, and their tests were not modified. All 183 pre-existing tests still pass. The BCRP path is parallel and independently authoritative only for BCRP records; legacy dataclasses remain bounded historical/implementation evidence.

A fresh import returned no loaded legacy runtime/renderer modules:

```text
[]
```

## 9. Failure behavior verified

- Invalid Candidate closures are rejected during authoring without repair.
- Invalid post-authoring Candidates receive inspectable negative Judgments.
- Negative Judgments cannot promote.
- Candidate semantic mutation after Judgment invalidates promotion.
- Competing/additional Judgment creation against an already judged closure is rejected.
- Existing Ready/release authority cannot be overwritten by this API.
- Input mutation after authoring does not mutate the authored bundle.

## 10. Scope boundaries preserved

No change was made to:

- BCRP profile semantics, structure authority, canonicalization rules, or existing validator behavior;
- corpus fixtures or thirty invalid variants;
- existing runtime, builder, validation, promotion, renderer adapter, renderer, HTML/SVG, publication, or TASK-039 evidence;
- AtlasForge or any upstream project;
- selector/fallback runtime, Publication Release, renderer plan, artifact conformance, or manifest emission;
- financial-domain semantics deferred by DSB-007;
- Constitution or accepted decisions.

No new decision artifact was needed because the implementation materializes already accepted TASK-041/044/045 responsibilities and the existing corpus Ready-fingerprint convention.

## 11. Verification results

```text
Recovery
PYTHONDONTWRITEBYTECODE=1 python3 -B tools/recover_session.py --project . --json
exit 0

Fresh before-manifest
python3 -B /tmp/briefforge_manifest.py . /tmp/briefforge-before-task046-20260716.json
638 included paths; exit 0

Pre-implementation baseline
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -v
Ran 183 tests — OK

Targeted RED
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_bcrp_authoring_lifecycle -v
expected ImportError: BCRPAuthoringRejected absent

Targeted GREEN
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_bcrp_authoring_lifecycle -v
Ran 7 tests — OK

Complete suite
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -v
Ran 190 tests — OK

Fresh import independence
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -c '<module inspection>'
[]

Static scan of changed Python source
0 dangerous-pattern matches

Python syntax check
exit 0
```

Final coherence, context health, architecture-to-reality audit, and exact post-manifest comparison are recorded below after final closeout.

## 12. Gate

**CLEAR TO PROCEED**.

BCRP now has a controlled, renderer-independent Candidate -> Judgment -> Ready path. There is no unresolved duplication or authority conflict blocking the next narrow stage. Renderer invocation remains premature because no production boundary yet derives an explicit compatibility/fallback plan from Ready requirements and renderer-owned capability evidence.

## 13. Exactly one recommended next task

`TASK-047 — BCRP Renderer Compatibility-Plan Production and Fail-Closed Proof`

Objective:

- accept one exact BCRP Ready closure and one explicit renderer-owned `RendererCapabilityDeclarationRecord`;
- deterministically produce one `RendererCompatibilityPlanRecord` without rendering;
- prove native support, complete static fallback, and explicit unsupported/fail-closed outcomes using accepted golden semantics;
- preserve renderer transformation sovereignty and package-owned requirements;
- stop before renderer invocation, HTML/SVG mutation, selector runtime, Publication Release/manifest emission, AtlasForge integration, runtime migration, or second formats.

This task is correctly bounded because it establishes the remaining authority handoff immediately before rendering without conflating plan production with renderer execution or publication.

## 14. Final closeout results

Governance checks after task/state/handoff/summary edits:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -B tools/context_health.py --project . --json
0 blocks; 0 warnings

PYTHONDONTWRITEBYTECODE=1 python3 -B tools/check_coherence.py --project .
0 blocks; 1 Historical Compatibility warning
The retained `metaharvest`/`eip` references are historical/compatibility vocabulary, not a TASK-046 defect.

PYTHONDONTWRITEBYTECODE=1 python3 -B tools/architecture_reality_audit.py --project . --write-report
0 blocks; 0 warnings
```

Fresh non-Git before/after comparison (cache directories and bytecode excluded by the established helper):

- before: 638 included paths;
- after: 642 included paths;
- added: 4;
- modified: 10;
- deleted: 0.

Added:

- `artifacts/reports/R-20260716-bcrp-candidate-authoring-and-lifecycle-compatibility.md`;
- `artifacts/tasks/TASK-046-bcrp-candidate-authoring-and-existing-lifecycle-compatibility-proof.md`;
- `src/briefforge/bcrp/authoring.py`;
- `tests/test_bcrp_authoring_lifecycle.py`.

Modified:

- `artifacts/reports/R-20260716-architecture-reality-audit.md`;
- `artifacts/reports/_SUMMARY.md`;
- `artifacts/tasks/_SUMMARY.md`;
- `context/latest_handoff.md`;
- `src/briefforge/bcrp/_SUMMARY.md`;
- `src/briefforge/bcrp/__init__.py`;
- `state/active_goal.md`;
- `state/architecture.md`;
- `state/project_state.md`;
- `tests/_SUMMARY.md`.

No other included path changed and no included path was deleted. Final manifest: `/tmp/briefforge-after-task046-20260716.json`.

## Erratum — superseded by TASK-047

Status: historical correction accepted 2026-07-16.

The 190-test TASK-046 execution evidence and Candidate-authoring/golden-parity results remain valid. The report's claims that L0-L2 technical validation itself created a governed `ValidationJudgmentRecord`, that native BCRP could independently promote Ready, and that renderer compatibility planning was immediately next are superseded.

TASK-047 establishes instead:

- BCRP L0-L2 success is `TechnicalValidationResult` evidence only;
- native BCRP promotion fails closed absent an accepted governance authority;
- the governed legacy Candidate/Judgment/Ready path remains the sole current operational approval/promotion authority;
- compatibility represents an already-governed legacy result through a required, generically unsupported extension with exact policy, authority, inventory, identity, timestamp, and separate-domain lineage checks;
- compatibility grants no Publication Release, renderer, artifact, manifest, distribution, or legacy-downstream authority;
- actual TASK-039 history fails closed for compatibility because its archived lifecycle evidence lacks required Judgment/Ready identities and validation/readiness timestamps; those values were not inferred.

A compatibility plan directly references Ready and renderer capability, not Release. Nevertheless, accepted BCRP processing expectations and validation-layer order place explicit Publication Release/governance authority at L4 before L5 compatibility planning, while accepted artifact evidence later requires both Release and plan. The corrected recommendation is therefore one bounded Publication Release production/lifecycle proof before renderer compatibility-plan production is reconsidered.

Canonical correction evidence is TASK-047's accepted decision, authority/compatibility specification, implementation report, corrected authoring API, compatibility adapter, and focused tests.
