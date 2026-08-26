# TASK-043 — Semantic Representation Contract and Layered Validation Specification Planning

Status: complete
Date: 2026-07-16

## Request

Allocate the accepted TASK-041 publication semantics and TASK-042 semantic-authority/failure semantics to a renderer-independent representation contract, define validation authority by layer, decide the representation-profile boundary, and determine whether a golden corpus may begin. Remain specification-only.

## Methodology slice

- Objective: define a transport-neutral semantic object graph, identity/reference rules, scoped states, finite selection semantics, renderer requirements/fallbacks, validation layers, cross-layer invariants, worked traces, and the next implementation gate.
- Explicit non-goals: no runtime records, schema, serialization, validator, builder, renderer, API, fixture, golden corpus, browser runtime, AtlasForge change, financial-domain semantics, or amendment of TASK-041/TASK-042 terminology.
- Implementation boundary: one specification, three architecture decisions, one evidence report, bounded backlog/state/handoff/summary/context updates, and deterministic non-Git manifest closeout.
- Readiness prerequisites: successful recovery; all applicable instructions inspected; TASK-043 identifier confirmed unused; fresh deterministic baseline manifest recorded at `/tmp/briefforge-before-task043-20260716.json`; TASK-041 and TASK-042 closeout accepted without reopening their manifests.
- Success criteria: every accepted semantic responsibility has one representation owner; every validation concern has an authority owner; traceability and semantic conformance remain distinct; worked traces expose cross-layer behavior; serialization convenience introduces no semantic requirement; golden-corpus gate and one successor task are explicit.
- Verification expectations: artifact consistency, Python compilation and unit tests, coherence, context health, architecture-to-reality audit, generated context refresh, recovery, and exact pre/post manifest comparison.

## Evidence used

Primary:
- `CONSTITUTION.md`
- `artifacts/specifications/architectural-decision-package-model.md`
- `artifacts/decisions/D-20260708-adpm-representation-architecture.md`
- `artifacts/reports/R-20260708-adpm-representation-architecture-evaluation.md`
- `artifacts/reports/R-20260708-adpm-representation-recommendations.md`
- `artifacts/specifications/publication-boundary-intake-portability-lifecycle.md`
- `artifacts/specifications/semantic-authority-evidence-states-interaction-renderer-fallback.md`
- TASK-040 through TASK-042 task/report/decision artifacts

Implementation evidence:
- `src/briefforge/runtime.py`
- `src/briefforge/validation.py`
- `src/briefforge/promotion.py`
- `src/briefforge/downstream.py`
- `src/briefforge/renderer_adapter.py`
- corresponding lifecycle, adapter, conformance, and downstream tests
- TASK-039 candidate/judgment/ready/renderer/conformance artifacts and InsightForge source fixture
- Presentation Grammar, Communication Intent experimental status, renderer backlog, and renderer policy

## Outputs

- `artifacts/specifications/semantic-representation-contract-and-layered-validation.md`
- `artifacts/reports/R-20260716-semantic-representation-contract-and-layered-validation-planning.md`
- `artifacts/decisions/D-20260716-semantic-object-graph-and-reference-authority.md`
- `artifacts/decisions/D-20260716-layered-validation-authority-and-cross-layer-invariants.md`
- `artifacts/decisions/D-20260716-representation-profile-boundary-and-golden-corpus-gate.md`

## Outcome

Accepted a renderer-independent semantic representation contract and validation responsibility model. Existing runtime dataclasses remain implementation evidence, not the future contract. No accepted TASK-041 or TASK-042 concept was reopened merely for naming.

Key results:
- one abstract graph joins Presentation Intake, Portable Presentation Material, Candidate -> Judgment -> Ready, release/lifecycle, renderer requirements, derivative artifacts, and manifest projection without collapsing their authorities;
- statement semantics are represented as independent dimensions rather than one universal type/mode/status;
- references are stable identity edges, not serialization paths;
- state and selection are explicitly scoped; finite selection remains prevalidated presentation-state choice rather than analysis;
- renderer requirements are package obligations while renderer capabilities are downstream declarations;
- traceability is necessary but insufficient for semantic conformance;
- validation remains layered and every layer has a named authority owner;
- one initial representation profile is required before any transport schema or golden corpus is materialized.

Gate verdict: CLEAR TO PROCEED to one specification-only successor task defining the initial representation profile and golden-corpus acceptance plan. Golden-corpus materialization remains blocked until that profile is accepted.

## Non-mutation confirmation

No source, test, runtime, validator, renderer, publication, fixture, schema, serialization, AtlasForge, upstream-project, or financial-domain file was modified by TASK-043. BriefForge remained a non-Git filesystem tree; no Git repository was initialized, and no commit or push occurred.
