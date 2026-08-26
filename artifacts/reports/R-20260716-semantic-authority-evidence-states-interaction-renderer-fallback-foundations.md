# R-20260716 — Semantic Authority, Evidence States, Interaction, and Renderer Fallback Foundations

Date: 2026-07-16
Status: Accepted final report
Task: TASK-042

## 1. Executive verdict

TASK-042 is complete as semantic specification-and-decision work.

Gate verdict: **CLEAR TO PROCEED**.

The repository supports a coherent next specification step without constitutional change or ownership expansion. It does not support immediate schemas, validators, renderer changes, selectors, or fallback implementation.

Exactly one next task is recommended:

> Plan the semantic representation contract and layered validation specifications that cover accepted TASK-041 publication/intake/lifecycle responsibilities and TASK-042 authority/state/interaction/transformation/fallback responsibilities, without choosing transport syntax or implementing runtime behavior.

This is correctly bounded because TASK-038 requires semantic contract architecture before schema/transport implementation, while TASK-041 and TASK-042 now supply the missing semantic responsibilities. Splitting representation planning from validation planning would force each to invent the other's semantic boundaries; combining them as planning specifications is coherent, while combining them with implementation is not.

## 2. Recovery and preflight result

- Normal recovery ran successfully before mutation: `PYTHONDONTWRITEBYTECODE=1 python3 tools/recover_session.py --project . --json` (exit 0).
- TASK-041 closeout was accepted as conclusively closed by explicit user direction without redundant reverification.
- `/tmp/briefforge-after-task041-20260716.json` was not accessed, hashed, parsed, verified, compared, copied, or otherwise operated on.
- The previously denied TASK-041-manifest operation was not retried, reproduced, rephrased, or bypassed.
- Applicable `AGENTS.md` and all eight Markdown files under `instructions/` were inspected before mutation.
- No TASK-042 artifact existed before the fresh baseline.
- Fresh pre-task manifest was established before mutation at `/tmp/briefforge-before-task042-20260716.json`.
- Format: `briefforge-filesystem-manifest-v1`.
- Root: `/home/mkkto/srv/EIP/projects/BriefForge`.
- Included paths: 559.
- Exclusions: `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `__pycache__`, and `.pyc`/`.pyo` suffixes.
- No external manifest-file SHA-256 was required or used as mutation proof.

## 3. Repository baseline

BriefForge is an ordinary filesystem tree and not a Git worktree. Historical branch, HEAD, origin/main, ahead/behind, staged paths, and tracked/untracked classification are unavailable. The exact Git probe from predecessor work returned:

`fatal: not a git repository (or any of the parent directories): .git`

TASK-042 therefore used deterministic filesystem manifests as its bounded mutation proof. It did not initialize Git, fetch, stage, commit, push, reset, restore, clean, or delete files.

## 4. Evidence inspected

### Doctrine, operating instructions, and lifecycle

- `AGENTS.md` and all files under `instructions/`;
- `CONSTITUTION.md`;
- `state/active_goal.md`;
- `state/project_state.md`;
- `state/architecture.md`;
- `context/latest_handoff.md`;
- `artifacts/decision_support_backlog.md`.

### Accepted predecessors

- TASK-040 task and current-state capability reconciliation report;
- TASK-041 task, specification, final report, and three accepted decisions;
- TASK-038 ADPM representation direction and integration decisions;
- canonical ADPM specification.

### Presentation semantics and implementation evidence

- Presentation Grammar;
- Candidate Presentation Package runtime documentation;
- `src/briefforge/runtime.py`;
- Communication Intent experiment/status documentation, source, and tests;
- renderer adapter contract/boundary and source;
- rendered-artifact conformance specification/source/tests;
- renderer improvement policy and backlog specification;
- relevant presentation model, adapter, invocation, conformance, static exhibit, and integration tests.

### Operational publication evidence

- TASK-039 task and boundary decision;
- TASK-039 candidate Presentation Package;
- renderer audit metadata and conformance evidence;
- demographic/correlation publication report evidence.

## 5. Reused concepts and avoided duplication

Reused:

- Presentation Statement as the smallest BriefForge-owned unit of presentation meaning;
- Organizing Purpose, Presentation Grammar, attention, Composition Semantics, and Presentation Validation Obligations;
- UpstreamReference and presentation-local obligations;
- Candidate -> Judgment -> Ready, without a second readiness lifecycle;
- TASK-041 intake, retained portable material, release, version, lifecycle, manifest, and AtlasForge boundaries;
- ADPM authority, evidence, recommendation, uncertainty, and immutability semantics;
- renderer adapter and conformance boundaries as bounded implementation evidence;
- Communication Intent only as experimental semantic evidence;
- renderer backlog governance for later implementation pressure.

Avoided:

- no universal statement type or status;
- no new publication lifecycle;
- no new analytical acceptance authority;
- no renderer-input-first representation;
- no selector schema or browser state model;
- no generic capability registry, visualization grammar, template system, UI framework, or plugin architecture;
- no semantic duplication of TASK-041 publication identity/versioning;
- no speculative financial/company fields;
- no retroactive TASK-039 rewrite.

## 6. Semantic decisions

### 6.1 Multidimensional statement authority

A statement must be understood across independent dimensions:

- semantic posture: observation, reusable evidence, accepted finding, interpretation, hypothesis, scenario, recommendation, uncertainty, caveat, personal annotation;
- scoped authority/provenance;
- communication function;
- encounter/composition relations;
- attention/prominence;
- evidence, value, consistency, and lifecycle references;
- obligations.

A recommendation can carry uncertainty and caveats. A conclusion function does not make BriefForge the finding owner. A primary statement is not necessarily more certain. These distinctions make a single enum structurally misleading.

### 6.2 Authority separation

Originator, semantic authority, evidence authority, exporter, requestor, presentation author, presentation validator, and publication authority remain distinct. TASK-039's split between InsightForge interpretation authority and KnowledgeForge evidence authority is the operational model.

Unknown/ambiguous authority blocks substantive admission. Fingerprints prove identity, not truth or authority.

### 6.3 Communication and encounter

The Communication Intent vocabulary is useful, but keyword derivation remains non-canonical. Communication function cannot decide role, truth, prominence, or renderer feature.

Encounter semantics are limited to order, grouping, hierarchy, required proximity/co-encounter, and bounded paths. TASK-039 demonstrates that current `mode` values overload role and communication function; no runtime change was made.

### 6.4 Explicit state

The specification rejects a universal state:

- evidence: availability, integrity, acceptance/authority, review, freshness, active use;
- value: present, explicit zero, missing, unavailable, not applicable, suppressed, unresolved, invalid;
- consistency: consistent, conflicting, unresolved/indeterminate, invalid under contract, not checked;
- lifecycle: upstream, readiness, release, artifact, and manifest lifecycles remain independent.

Structured disagreement and counterevidence may be valid. Undeclared contradiction, authority ambiguity, or broken references block progression.

### 6.5 Interaction

Admitted:

- in-publication navigation;
- inspection of already-present material.

Conditionally admissible:

- finite, closed, authority-declared selection among complete prevalidated states, only when every authority, evidence, narrative, default, fallback, capability, audit, version, and offline-reproduction prerequisite passes.

Prohibited:

- analytical recalculation;
- arbitrary filtering/querying;
- open-ended exploration.

### 6.6 Narrative consistency

Every selectable state must independently keep title, purpose, scope, primary message, methods, values, periods, sample sizes, rankings, caveats, uncertainty, provenance, and non-scope coherent. A renderer cannot infer or repair narrative state.

### 6.7 Renderer sovereignty and fallback

Renderer-owned mechanics include target encoding, deterministic layout/geometry, scoped styles, anchors, native disclosure, accessibility, and predeclared lossless expression.

Renderer-prohibited authority includes role inference, prominence selection, ranking, derived summaries, evidence repair, silent omission, live lookup, or obligation detachment.

Fallback order is verified native expression -> prevalidated equivalent -> complete static representation -> authorized explicit unsupported/unavailable expression -> fail closed. Silent best effort is prohibited.

Existing capability checks prove package-field compatibility only. Existing artifact conformance proves audit linkage only. Neither proves semantic output fidelity.

## 7. Adversarial findings

| Evidence pressure | Finding | Consequence |
| --- | --- | --- |
| TASK-039 `EncounterSemantics.mode` values include orientation, finding, evidence, caveat, provenance, methodology, conclusion. | Role/function/encounter concerns are overloaded. | Separate semantics in future representation planning; no runtime repair now. |
| TASK-039 first statement is orientation while renderer evidence can promote first position as primary. | Position-based prominence can misstate narrative authority. | Primary role must be authored/validated. |
| TASK-039 uses `strongest` claims. | Comparison universe and selection authority must be explicit. | Future admission/validation requirement. |
| TASK-039 statement obligation IDs and obligation `applies_to` are not fully reciprocal. | Non-detachment cannot rely on ambiguous direction. | Next representation/validation planning must decide authoritative direction and consistency checks. |
| TASK-039 absolute locators predate TASK-041 portability. | Historical fixture is not proof of TASK-041 offline portability. | Preserve history; do not retrofit silently. |
| ADPM requires counterarguments/opposing evidence while intake rejects unresolved conflicts. | Conflict cannot mean all disagreement. | Distinguish structured disagreement from accidental contradiction. |
| Runtime fingerprints all dataclass content, including locators. | Semantic identity may be location-sensitive. | Next planning task must separate semantic and transport/location identity; no code change now. |
| Renderer capabilities list package features. | Capability declaration does not prove output, interaction, fallback, accessibility, or obligation behavior. | Future positive capability/preflight semantics required. |
| Conformance checks identifiers, not rendered content. | Fabricated prose could retain valid audit metadata. | Audit-link conformance is necessary but insufficient. |
| Renderer parses/sorts values and can derive extrema/summary captions. | Deterministic computation can still create semantic claims. | Exact authorization/validation required; source order default. |
| Unsupported exhibit paths may silently omit output. | Silent degradation is not semantic fallback. | Fail closed unless a declared equivalent exists. |
| Financial selectors would require unstable fiscal/company semantics. | Generic extensibility cannot supply domain meaning. | DSB-007 deferral remains binding. |

## 8. Cross-domain scenario verdicts

The accepted specification tests at least these cases:

1. zero versus missing;
2. unavailable versus suppressed;
3. conflicting accepted sources;
4. structured ADPM counterargument;
5. hypothesis styled as finding;
6. scenario interpolation;
7. unattributed personal annotation;
8. recommendation fallback losing qualifiers;
9. TASK-039 country selector;
10. TASK-039 date-window recomputation;
11. raw/first-difference toggle with stale thesis;
12. superlative without comparison universe;
13. inferred first-statement prominence;
14. renderer-derived extrema;
15. detached caveat fallback;
16. lossless source-table fallback;
17. fabricated prose with correct audit identifiers;
18. stale selector state;
19. AtlasForge embed failure;
20. premature company/fiscal selector;
21. changed locator with claimed semantic equivalence;
22. cyclic encounter relations;
23. nonreciprocal obligation references.

The design rejects semantic leakage rather than broadening BriefForge to absorb each case.

## 9. Constitutional verdict

No constitutional change is required for TASK-042.

Existing doctrine already distinguishes bounded derivative publication from application/platform ownership:

- navigation and native inspection can be derivative publication mechanics;
- finite selection is only conditionally admissible when it chooses prevalidated presentation states;
- recalculation, querying, discovery, cross-report navigation, dashboards, portals, and open-ended exploration remain outside BriefForge;
- standalone operation remains mandatory;
- AtlasForge consumption remains optional and downstream.

The tension is resolved by authority and completeness, not by whether an artifact uses a browser. A self-contained publication may have bounded interaction; BriefForge may not become an exploratory application.

## 10. Financial-domain semantic deferral

Location: `artifacts/decision_support_backlog.md`, DSB-007 — Defer company and financial-domain semantics to upstream operational evidence.

Final accepted wording remains:

> BriefForge defers canonical semantics for fiscal periods; financial-reporting dates; restatements; corporate actions; currency conversion; company consolidation; security identity; reporting segments; reported-versus-adjusted values; and related company and financial-domain concepts. MacroForge should first encounter and define these concepts through operational company and financial-data work. After those concepts stabilize upstream, BriefForge should conduct a bounded compatibility review, consume upstream definitions where appropriate, and add only presentation-specific obligations that MacroForge does not own. Until then, ADPM may support generic typed external references and bounded extensibility, but it must not contain speculative financial-domain fields.
>
> This is a semantic deferral; no BriefForge runtime dependency on MacroForge and no blocker for generic BriefForge development. It does not cover BriefForge-owned publication semantics: publication identity; semantic publication version; evidence-snapshot reference; renderer version; generated-artifact version; publication time; correction; rerender; supersession; withdrawal; and staleness.

TASK-042 preserved this note and did not reopen its scope.

## 11. Artifacts

Created:

- `artifacts/tasks/TASK-042-semantic-authority-evidence-states-interaction-renderer-fallback-foundations.md`;
- `artifacts/specifications/semantic-authority-evidence-states-interaction-renderer-fallback.md`;
- `artifacts/decisions/D-20260716-multidimensional-statement-authority-and-state-semantics.md`;
- `artifacts/decisions/D-20260716-bounded-interaction-authority-and-narrative-consistency.md`;
- `artifacts/decisions/D-20260716-renderer-transformation-sovereignty-and-fail-closed-fallback.md`;
- this report.

Updated during closeout:

- `artifacts/decision_support_backlog.md`;
- affected `_SUMMARY.md` files;
- `state/active_goal.md`;
- `state/project_state.md`;
- `state/architecture.md`;
- `context/latest_handoff.md`;
- established generated context/audit artifacts as required by project procedure.

No source, tests, fixtures, publication outputs, renderer, constitution, or external project changed.

## 12. Gate and exact next task

**CLEAR TO PROCEED**

Exact next task:

**TASK-043 — Semantic Representation Contract and Layered Validation Specification Planning**

Objective:

- map accepted TASK-041 and TASK-042 semantic responsibilities into a renderer-independent semantic representation contract;
- define validation layers, ownership, inputs, findings, blocking consequences, and cross-layer invariants;
- resolve semantic-versus-location identity, obligation-reference direction, scoped state declarations, finite selection state representation, capability requirement declarations, and audit-link-versus-semantic artifact conformance;
- keep Candidate -> Judgment -> Ready and ADPM semantic-version independence;
- remain transport-neutral and implementation-free.

Non-goals:

- no JSON/YAML/XML, schema, examples/golden corpus, builder, validator, serializer, renderer, selector, fallback implementation, manifest emitter, API, UI, or runtime change.

Why exactly one combined planning task: representation responsibilities and validation layers are mutually constraining semantic specifications. Separating them now would duplicate unresolved invariants; implementing either now would violate TASK-038's specification-first gate.

## 13. Verification and mutation proof

Commands run successfully:

- `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests` — 154 tests passed;
- focused TASK-042 artifact consistency script — 42 checks passed, 0 failed;
- `PYTHONDONTWRITEBYTECODE=1 python3 -B tools/update_context_summaries.py --project . --max-depth 3` — exit 0;
- `PYTHONDONTWRITEBYTECODE=1 python3 -B tools/build_context.py ... --context-mode normal ...` — exit 0, within the 24,000-token budget;
- `PYTHONDONTWRITEBYTECODE=1 python3 -B tools/check_coherence.py --project . --json` — exit 0, 0 blocks, 2 context-size warnings;
- `PYTHONDONTWRITEBYTECODE=1 python3 -B tools/context_health.py --project . --json` — exit 0, 0 blocks, 2 context-size warnings;
- `PYTHONDONTWRITEBYTECODE=1 python3 -B tools/architecture_reality_audit.py --project . --write-report` — exit 0, 0 blocks, 1 warning for the known missing `templates/` reference.

A first governance-mode context build exceeded its 10,000-token budget at 13,784 estimated tokens and exited 2 after writing generated audit outputs. It was not treated as a pass. The bundle was narrowed to the established normal mode and rebuilt successfully within budget.

The final TASK-042 manifest comparison uses:

- before: `/tmp/briefforge-before-task042-20260716.json`;
- after: `/tmp/briefforge-after-task042-20260716.json`;
- format/root/exclusions match exactly;
- before included paths: 559;
- after included paths: 565;
- additions: 6 intended TASK-042 artifacts;
- content changes: 15 intended backlog, state, handoff, summary, generated-context, and audit-report paths;
- deletions: 0;
- path-type changes: 0;
- symlink-target changes: 0;
- unexpected differences: 0;
- unchanged baseline paths: 544.

No external manifest-file digest was used. Mutation proof is the manifest's internal path/type/content-hash comparison.

No Git repository was initialized. No commit or push occurred.
