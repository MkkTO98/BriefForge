# R-20260716 Semantic Representation Contract and Layered Validation Planning

Date: 2026-07-16
Status: complete
Task: TASK-043

## 1. Recovery and mutation baseline

The required recovery command ran before repository mutation:

```text
PYTHONDONTWRITEBYTECODE=1 python3 tools/recover_session.py --project . --json
exit 0
```

Recovery identified TASK-042 as complete, no implementation task active, and the exact next pressure as renderer-independent semantic representation and layered validation planning. It also preserved the known separate issues: TASK-039 renderer metadata mismatch, missing `templates/`, stale implementation wording, and non-Git provenance limitations.

All applicable instructions were inspected before mutation: root `AGENTS.md`, `CONSTITUTION.md`, all eight Markdown files under `instructions/`, startup state pointers, and latest handoff.

TASK-043 availability was checked by filename and content search. No existing TASK-043 artifact existed; the identifier was available and was used without inventing a parallel numbering scheme.

Fresh baseline:

- path: `/tmp/briefforge-before-task043-20260716.json`
- format: `briefforge-filesystem-manifest-v1`
- root: `/home/mkkto/srv/EIP/projects/BriefForge`
- included paths: 565
- excluded directory names: `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `__pycache__`
- excluded suffixes: `.pyc`, `.pyo`

The baseline was created with the authorized `/tmp/briefforge_manifest.py`. No prior TASK-041 or TASK-042 manifest was read or reverified.

## 2. Repository/Git state

BriefForge remains an ordinary filesystem tree, not a Git worktree.

Actual probes:

```text
git rev-parse --is-inside-work-tree
fatal: not a git repository (or any of the parent directories): .git

git status --porcelain=v2 --branch
fatal: not a git repository (or any of the parent directories): .git

git remote get-url origin
fatal: not a git repository (or any of the parent directories): .git
```

Therefore branch, HEAD, origin/main, ahead/behind, staged paths, tracked modifications, and Git status fingerprint do not exist. The deterministic filesystem manifest is the accepted task-local mutation boundary. It proves exact pre/post path content for included files, not historical authorship.

## 3. Evidence inspected

### Governing doctrine and state

- `CONSTITUTION.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `context/latest_handoff.md`
- `artifacts/decision_support_backlog.md`
- `artifacts/renderer_backlog.md`

### ADPM and representation doctrine

- `artifacts/specifications/architectural-decision-package-model.md`, especially core objects, relationships, completeness, extension, validation, and compatibility
- `artifacts/decisions/D-20260708-adpm-representation-architecture.md`
- `artifacts/decisions/D-20260708-adpm-architecture-integration.md`
- `artifacts/decisions/D-20260708-adpm-validation-decision.md`
- `artifacts/reports/R-20260708-adpm-representation-architecture-evaluation.md`
- `artifacts/reports/R-20260708-adpm-representation-recommendations.md`

### Accepted predecessor work

- TASK-040 task/report capability reconciliation
- TASK-041 task, publication specification, report, and three accepted decisions
- TASK-042 task, semantic-authority specification, report, and three accepted decisions

The accepted predecessors were used as fixed semantics. They were not reopened for terminology-only changes.

### Runtime and lifecycle evidence

- `src/briefforge/runtime.py`: `PackageIdentity`, `OrganizingPurpose`, `EncounterSemantics`, `UpstreamReference`, `PresentationObligation`, `PresentationStatement`, `CandidatePresentationPackage`, `semantic_fingerprint`
- `src/briefforge/validation.py`: `ValidationFinding`, `ValidationJudgment`, constitutional checks
- `src/briefforge/promotion.py`: `ReadyPresentationPackage` and exact Candidate/Judgment/fingerprint matching
- `src/briefforge/downstream.py`: Ready-only immutable semantic access
- `src/briefforge/renderer_adapter.py`: adapter request, identity, narrow `package_features` capability, compatibility, invocation, static HTML/SVG evidence, and audit-link conformance
- lifecycle, adapter, invocation, downstream, and conformance tests

### Communication and renderer evidence

- `docs/presentation-grammar-specification.md`
- `docs/communication-intent-experimental-layer.md`
- `docs/communication-intent-status.md`
- `docs/renderer-adapter-boundary.md`
- `docs/renderer-adapter-contract.md`
- `docs/rendered-artifact-conformance.md`
- `docs/renderer-backlog-specification.md`
- `docs/renderer-improvement-policy.md`
- `src/briefforge/presentation_models.py`

### TASK-039 source and publication evidence

- InsightForge source fixture: `/home/mkkto/srv/EIP/projects/InsightForge/artifacts/fixtures/T-035-demographic-growth-correlation-report-input.json`
- TASK-039 task, report, boundary decision
- Candidate, Judgment, Ready, rendered HTML, conformance, audit metadata, and inspection artifacts

Observed facts:

- InsightForge owns question selection/interpretation; KnowledgeForge owns accepted coefficients/method/provenance; BriefForge owns presentation.
- The candidate has 11 statements, three upstream references, and three obligations.
- Existing encounter `mode` values mix orientation/conclusion/methodology with finding/evidence/caveat/provenance, confirming TASK-042's representational pressure.
- audit-link conformance passes for package identity, semantic fingerprint, validation policy, and renderer identity.
- renderer audit says `table_exhibit_present: false` while the publication and inspection include a comparison table; this remains a separate known inconsistency and was not repaired.

### MetaHarvest relationship

BriefForge evidence consistently treats MetaHarvest Presentation Architecture as advisory pattern evidence, not implementation or semantic authority. External dashboard, application-record, lineage, and visualization systems support separation of durable semantics, composition, lineage, and rendering, but do not justify importing dashboard, BI, template, visualization-grammar, or application architecture.

## 4. Evidence-to-representation allocation

| Accepted responsibility | Representation owner | Key evidence | Allocation result |
| --- | --- | --- | --- |
| Intake | Presentation Brief | TASK-041 §§3.1, 5 | Reused; no parallel Presentation Request concept. |
| Resolved portable input | Portable Presentation Material | TASK-041 §§3.2, 6 | Reused; no parallel Resolved Presentation Input concept. |
| Canonical package | Candidate/Ready Presentation Package | Constitution; runtime; TASK-041 §7 | Preserved as semantic authority, not transport shape. |
| ADPM | ADPM specialized semantic graph | ADPM spec §§4-8 | Retained as decision-support specialization, not renderer input. |
| Statement semantics | multidimensional Presentation Statement | TASK-042 §§3-6 | Allocated to independent role, authority, function, attention, relation, state, and obligation dimensions. |
| Composition | typed identity relations | TASK-042 §5.3; Presentation Grammar | Partial order/group/hierarchy/proximity/alternate path; no layout. |
| Evidence/provenance | external semantic reference + snapshot binding | ADPM EvidenceReference/SourceProvenance; TASK-041 §6; TASK-042 §4.3 | Generic and authority-preserving; no upstream ontology copy. |
| Explicit states | scoped state assertion | TASK-042 §6 | State family, subject, authority, rationale, consequence; no universal status. |
| Finite selection | Selection Set + complete state projections | TASK-042 §7.3 | Closed enumerated valid states only; no query or implied combinations. |
| Renderer need | package-owned Renderer Requirement | TASK-042 §10 | Separated from renderer-owned capabilities. |
| Capability | renderer identity/version declaration with verification evidence | existing adapter proof; TASK-042 §10 | Current package-feature flags are evidence but insufficient future semantics. |
| Fallback | declared fallback obligation and compatibility expression plan | TASK-042 §11 | Deterministic hierarchy; no best effort. |
| Lifecycle | Candidate/Judgment/Ready plus Publication Release Record | TASK-041 §§7-9 | Preserves independent semantic/release/renderer/artifact/manifest versions. |
| Manifest | derivative projection | TASK-041 §§10-11 | Consumer-facing discovery boundary, not canonical package. |
| Artifact conformance | separate audit-link and semantic findings | current tests; TASK-042 §10 | Current check retained as audit-link evidence, not mislabelled semantic proof. |

## 5. Existing concepts reused and duplications avoided

Reused:

- Presentation Brief rather than introducing a second request contract;
- Portable Presentation Material rather than a second resolved-input contract;
- Package Identity and Organizing Purpose;
- Presentation Statement, Upstream Reference, Presentation Obligation, and Encounter/Composition Semantics;
- Candidate -> Judgment -> Ready;
- Publication Release Record and publication manifest projection;
- ADPM objects and authority/completeness rules;
- Presentation Grammar's attention and communication principles;
- renderer adapter identity/capability/compatibility boundary as implementation evidence;
- renderer backlog and frozen-surface policy;
- standalone operation and optional embedding boundaries.

Avoided:

- no universal statement `type`, `mode`, or `status`;
- no new statement lifecycle;
- no canonical section/template/archetype/profile based on current Presentation Models;
- no renderer capability flags embedded into semantic statements;
- no serialization-path references;
- no schema-first representation;
- no multi-format architecture;
- no Markdown canonical form;
- no Communication Intent promotion;
- no AtlasForge catalog fields in the canonical package;
- no financial-domain fields.

## 6. Abstract graph and validation result

The accepted graph is:

```text
Presentation Brief
-> Portable Presentation Material
-> Candidate Presentation Package
-> layered Validation Judgment
-> Ready Presentation Package
-> Publication Release Record
-> named renderer compatibility/expression plan
-> derivative artifact
-> audit-link conformance + semantic artifact conformance
-> derivative manifest projection
```

Identity edges connect package, statement, relation, evidence snapshot, obligation, state assertion, selection state, requirement, release, renderer, artifact, and manifest records without prescribing nested syntax.

Validation authority is allocated to intake admission, profile structure, semantic contract, lifecycle/readiness, governance approval, renderer compatibility/planning, and output conformance. A consolidated future tool is permitted only if it preserves those authority boundaries and findings.

## 7. Traceability and conformance verdict

Current runtime and tests prove:

- immutable Candidate/Ready relationships;
- deterministic semantic fingerprinting of current runtime substance;
- matching Candidate/Judgment promotion;
- Ready-only renderer access;
- adapter identity and narrow package-input declaration;
- audit-link checks for package identity, semantic fingerprint, validation policy, and adapter identity.

They do not prove semantic artifact conformance. Fabricated prose could carry correct audit identifiers. TASK-043 therefore accepts traceability as necessary but insufficient and makes semantic output conformance a separate future finding family.

## 8. Worked and adversarial evidence result

The specification includes five worked traces:

1. accepted finding + reusable evidence + caveat;
2. explicit zero versus missing;
3. finite prevalidated selection with static fallback;
4. TASK-039-style cross-project analytical publication;
5. rerender, correction, supersession, withdrawal, and staleness.

Twenty adversarial proposals are explicitly accepted, rejected, or deferred. The highest-risk rejected shortcuts are current dataclasses as contract, one universal type, duplicate intake/resolved-input concepts, serialization-path references, fingerprint-as-authority, audit-link-as-semantic-conformance, generic null, inferred selector combinations, renderer-owned semantic requirements, monolithic pass/fail authority, immediate multi-format work, speculative financial fields, and a pre-profile golden corpus.

## 9. Representation-profile and golden-corpus gate

A Representation Profile is now narrowly defined as a named/versioned mapping from accepted semantics to one concrete abstract record/graph shape. It may choose containment/reference direction, explicit state encoding, extensions, ordering, and canonicalization. It may not redefine semantics or serve renderer/transport convenience.

Golden-corpus verdict:

- semantic case design is justified;
- corpus materialization is blocked;
- one initial profile, deterministic canonicalization, semantic equality, layer-specific expected findings, extension policy, and redaction/external-reference rules must be accepted first.

Existing TASK-039 JSON is a valuable source case but cannot be copied unchanged into a golden corpus because it reflects the current incomplete runtime and known metadata inconsistency.

## 10. Decisions recorded

- `D-20260716-semantic-object-graph-and-reference-authority.md`
- `D-20260716-layered-validation-authority-and-cross-layer-invariants.md`
- `D-20260716-representation-profile-boundary-and-golden-corpus-gate.md`

All three are accepted. None authorizes implementation.

## 11. Gate verdict and exact next task

CLEAR TO PROCEED.

Exact successor:

`TASK-044 — Initial Representation Profile and Golden Corpus Acceptance Specification`

It should define exactly one renderer-independent profile, deterministic canonicalization/semantic equality, extension behavior, and the planned corpus inventory with expected findings by validation layer. It must remain specification-only and issue the later implementation gate.

This is correctly bounded because TASK-043 has decided responsibility allocation and validation authority, but syntax/canonicalization/test-vector design still needs one coherent profile. Implementing schemas, serializers, validators, or corpus files now would be premature. Defining all contracts at once or adding a second profile would create uncontrolled breadth.

## 12. MacroForge semantic deferral

TASK-043 preserves, but does not duplicate or weaken, the accepted deferral in `artifacts/decision_support_backlog.md` under `DSB-007 — Defer company and financial-domain semantics to upstream operational work` and TASK-041/TASK-042 specifications.

Representation consequence recorded here:

> Generic typed external references and extensions may identify upstream-owned material, but the semantic graph and future profile must not define speculative canonical fields for fiscal periods, financial-reporting dates, restatements, corporate actions, currency conversion, company consolidation, security identity, reporting segments, reported-versus-adjusted values, or related company/financial concepts. MacroForge must stabilize those concepts operationally first. BriefForge may later perform a bounded compatibility review and add only presentation-specific obligations. This is semantic deferral, not a runtime dependency and not a blocker for generic development. BriefForge-owned publication identity, semantic publication version, evidence-snapshot reference, renderer version, artifact version, publication time, correction, rerender, supersession, withdrawal, and staleness remain in scope.

## 13. Verification

Commands and actual results:

- `PYTHONDONTWRITEBYTECODE=1 python3 -B tools/recover_session.py --project . --json` — exit 0 at startup and closeout;
- fresh `/tmp/briefforge-before-task043-20260716.json` — 565 included paths;
- `PYTHONDONTWRITEBYTECODE=1 python3 -B -m compileall -q src tests tools` — exit 0;
- `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests` — 154 tests passed;
- focused TASK-043 artifact consistency script — 63/63 checks passed;
- `PYTHONDONTWRITEBYTECODE=1 python3 -B tools/update_context_summaries.py --project . --max-depth 3` — exit 0; affected listings inspected;
- initial overbroad normal context build — correctly failed at 18,722 estimated tokens against 10,000 budget and was not treated as passing;
- narrowed normal context build — exit 0 within the 10,000-token budget;
- `PYTHONDONTWRITEBYTECODE=1 python3 -B tools/context_health.py --project . --json` — exit 0, 0 blocks, 0 warnings after state compaction;
- `PYTHONDONTWRITEBYTECODE=1 python3 -B tools/check_coherence.py --project . --json` — exit 0, 0 blocks, one intentional Historical Compatibility notice for retained MetaHarvest/MacroForge references;
- `PYTHONDONTWRITEBYTECODE=1 python3 -B tools/architecture_reality_audit.py --project . --write-report --json` — exit 0, 0 blocks, one known missing-`templates/` documentation-without-implementation warning;
- final `/tmp/briefforge-after-task043-20260716.json` — 571 included paths;
- exact manifest comparison — 6 additions, 15 content changes, 0 deletions, 0 type/symlink changes, 550 unchanged baseline paths, and no unauthorized difference.

The report does not hide the failed first context build; narrowing retrieval was the prescribed correction.

## 14. Scope discipline

No source code, test, runtime record, schema, serialization, validator, builder, renderer, HTML/SVG publication, TASK-039 fixture, golden corpus, AtlasForge artifact, upstream project, financial-domain architecture, Git repository, commit, or push was created or modified by this task.
