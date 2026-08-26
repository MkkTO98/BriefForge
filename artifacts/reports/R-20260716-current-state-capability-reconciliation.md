# Current-State Capability Reconciliation

Date: 2026-07-16
Task: TASK-040
Status: Complete
Gate: **PROCEED WITH PRECONDITIONS**

## 1. Purpose and evidence standard

This report reconciles proposed BriefForge publication/interface responsibilities with repository reality before any foundational contract specification or implementation begins. It converts the preceding read-only audit into durable project evidence; direct reinspection corrected path anchors and active-state drift but did not overturn the material findings.

Evidence levels are kept separate:

1. **Mentioned** — prose names a concept.
2. **Specified** — semantics or responsibility are decided in doctrine/specification.
3. **Represented** — a concrete model or artifact shape exists.
4. **Validated** — implemented checks enforce at least part of it.
5. **Implemented** — runtime or renderer behaviour exists.
6. **Proven** — tests or completed operational artifacts exercise it.

A row is not classified as implemented merely because prose mentions it. Each row has exactly one primary state from the task vocabulary; qualifications describe evidence maturity without changing that primary classification.

## 2. Recovery and baseline

`PYTHONDONTWRITEBYTECODE=1 python3 tools/recover_session.py --project . --json` exited 0. Recovery confirmed:

- TASK-039 Demographic Correlation Browser Report is complete;
- no implementation task is active;
- TASK-038 authorized architecture/specification direction but no implementation;
- the directory is known to be non-Git.

Direct `git rev-parse --is-inside-work-tree` verification returned `fatal: not a git repository (or any of the parent directories): .git`.

TASK-040 was available: no `TASK-040` task artifact existed at baseline, while TASK-039 is the completed demographic/correlation publication (`state/active_goal.md`, “Latest completed task”; `artifacts/tasks/TASK-039-demographic-correlation-browser-report.md`, status and objective). TASK-040 is therefore used for this reconciliation. Historical prospective references assigning TASK-039 to ADPM planning are not treated as activated tasks.

The deterministic pre-mutation manifest is `/tmp/briefforge-before-20260716.json`. It includes regular-file SHA-256 and size, directory path/type, and symlink target; it excludes only directory components `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `__pycache__` and file suffixes `.pyc`, `.pyo`. It cannot establish historical authorship or cleanliness; every included baseline path is treated as pre-existing state.

## 3. Capability reconciliation matrix

| # | Capability | Primary state | Evidence and qualification |
|---|---|---|---|
| 1 | Presentation Package | **already implemented** | `src/briefforge/models.py` defines package structures; `src/briefforge/builder.py` builds candidates; `src/briefforge/runtime.py` validates/promotes; `tests/test_candidate_runtime.py`, `tests/test_builder.py`, and TASK-039 candidate/ready artifacts prove execution. The frozen core is named in `CONSTITUTION.md`, “Core Conceptual Model”. |
| 2 | ADPM | **already specified** | `artifacts/specifications/architectural-decision-package-model.md` defines semantic architecture; `D-20260708-architectural-decision-package-adoption.md` adopts it; `D-20260708-adpm-representation-architecture.md` explicitly says architecture-only/no implementation. No ADPM runtime representation exists. |
| 3 | Typed presentation statements and existing roles | **partially implemented** | `src/briefforge/presentation_models.py` represents typed presentational items; `docs/presentation-grammar-specification.md` specifies statement/presentation grammar; existing models/tests prove selected roles. The broader proposed epistemic role set is neither fully accepted nor represented. |
| 4 | Organizing purpose | **already implemented** | `src/briefforge/models.py` and builder/runtime paths carry purpose; `docs/presentation-grammar-specification.md` defines organizing purpose; candidate/ready fixtures and validation tests exercise it. |
| 5 | Composition and encounter order | **partially implemented** | `CONSTITUTION.md`, “Core Conceptual Model”, freezes Composition Semantics; `docs/presentation-grammar-specification.md` and `src/briefforge/presentation_models.py` provide ordered sections/items. `tests/test_large_report_stress.py` and TASK-039 prove ordered rendering. EncounterSemantics/Communication Intent remain experimental rather than one complete accepted authority model (`R-20260703-communication-intent-experimental-layer.md`). |
| 6 | Candidate → Judgment → Ready lifecycle | **already implemented** | `src/briefforge/runtime.py`, `validation.py`, and `promotion.py` implement Candidate Presentation Package → Validation Judgment → Ready Presentation Package; `tests/test_candidate_runtime.py`, `test_promotion.py`, and TASK-039 validation/ready artifacts prove it. This must not be duplicated by a publication-readiness lifecycle. |
| 7 | Renderer adapter boundary | **already implemented** | `docs/renderer-adapter-boundary.md` specifies it; `src/briefforge/renderer_adapter.py` implements `RendererAdapterRequest` and invocation; `tests/test_renderer_adapter_contract.py` and `test_renderer_adapter_invocation.py` prove it. A pre-candidate intake must not reuse this name or responsibility. |
| 8 | Rendered-artifact conformance | **already implemented** | `docs/rendered-artifact-conformance.md` specifies a narrow derivative-output obligation; `src/briefforge/rendered_artifact.py` implements checks; `tests/test_rendered_artifact_conformance.py` and TASK-039 conformance evidence prove it. This is not semantic-package validity. |
| 9 | Static HTML/SVG renderer | **already implemented** | `src/briefforge/minimal_html_renderer.py` and `static_svg.py` implement bounded derivative rendering; `tests/test_minimal_html_renderer.py`, `test_static_svg_time_series_exhibit.py`, and TASK-033 prove it. It is not a general visualization engine. |
| 10 | Existing demographic/correlation report | **already implemented** | `artifacts/tasks/TASK-039-demographic-correlation-browser-report.md`, `artifacts/reports/R-20260713-demographic-correlation-browser-report.md`, candidate/ready packages, HTML, conformance, metadata, and browser inspection under `artifacts/presentations/TASK-039-demographic-correlation-browser-report/` form the operational proof. |
| 11 | Template, archetype, profile, or equivalent concepts | **deferred** | `CONSTITUTION.md`, “Ownership Boundaries” and “Constitutional Exclusions”, rejects templates/UI libraries as constitutional architecture; existing country-profile/comparison/investment-thesis presentation models are bounded authored models (`src/briefforge/presentation_models.py`, related tests), not a canonical template/archetype/profile subsystem. `state/architecture.md` mentions a missing `templates/` path, but absence does not authorize one. |
| 12 | Audience models | **missing** | Audience-appropriate communication is an owned responsibility in `CONSTITUTION.md`, but no accepted audience contract/model with representation, validation, or proof was found. Communication Intent evidence is experimental (`R-20260703-communication-intent-experimental-layer.md`), not an audience authority contract. |
| 13 | Evidence, provenance, and caveat obligations | **already implemented** | `CONSTITUTION.md`, “Validation Philosophy”; `docs/presentation-grammar-specification.md`; package models/validation; and `tests/test_constitutional_validation.py` establish obligations. TASK-039 carries upstream source references, caveats, and rejected raw-level relationships into rendered output. Scope is presentation traceability, not upstream truth adjudication. |
| 14 | Sensitivity and distribution obligations | **partially implemented** | ADPM specifies sensitivity/uncertainty/comparison obligations (`architectural-decision-package-model.md`); existing presentation grammar and reports can communicate them, but no general accepted runtime contract/validator proves the full proposed obligation set. Distribution is represented only where source evidence supplies it. |
| 15 | Renderer backlog and improvement policy | **already specified** | `artifacts/renderer_backlog.md`, `docs/renderer-backlog-specification.md`, and `docs/renderer-improvement-policy.md` govern evidence-gated renderer evolution. Bounded proofs exist, but backlog entries are evidence/candidates, not automatic implementation authority. |
| 16 | Publication and static-publication concepts | **partially implemented** | `docs/operational-publication-workflow.md`, TASK-026, TASK-030, TASK-033, and TASK-039 prove standalone static outputs. A complete publication identity/taxonomy/lifecycle contract is absent. |
| 17 | Integration and project-independence proofs | **already implemented** | `src/briefforge/downstream.py`, `tests/test_downstream_integration_proof.py`, `tests/test_insightforge_integration_proof.py`, and TASK-039 prove file/package-based downstream and upstream-owner separation without runtime coupling. These proofs are bounded, not universal interoperability. |
| 18 | AtlasForge boundary | **already specified** | `CONSTITUTION.md`, “Non-Goals” and ownership limits; `R-20260701-constitutional-architecture.md` boundary findings; and `D-20260708-briefforge-next-evolution.md` assign navigation/discovery/exploration elsewhere. An AtlasForge-consumable manifest may later be specified as a publication boundary, but it is not a portal implementation or runtime dependency. |
| 19 | MetaHarvest Presentation Architecture references | **already specified** | `docs/renderer-improvement-policy.md`, “Relationship to ArchitectureHarvest/MetaHarvest evidence”, and `docs/renderer-backlog-specification.md` make external presentation architecture advisory. It cannot authorize BriefForge architecture or implementation. |
| 20a | Immutable released/publication snapshot responsibility (proposed “frozen publication”) | **missing** | ADPM and Ready package immutability provide related semantics (`D-20260708-adpm-architecture-integration.md`; `state/project_state.md`, accepted principles), but no publication taxonomy term is accepted. “Freeze” already has constitutional/ADPM meanings; the responsibility needs later terminology reconciliation, not automatic adoption of “frozen publication”. |
| 20b | Parameterized publication | **missing** | Bounded authored variants exist, but no accepted semantics distinguish declared/prevalidated parameters from recalculation or exploration. |
| 20c | Publication manifest | **missing** | No canonical publication manifest contract exists. Renderer metadata and conformance records are evidence, not a manifest contract. |
| 20d | Live entity page | **intentionally prohibited** | `CONSTITUTION.md`, “Non-Goals”, excludes browser/dashboard/application ownership; current doctrine supports standalone artifacts, not continuously updated entity pages. |
| 20e | Open-ended exploratory workspace | **intentionally prohibited** | `CONSTITUTION.md`, “Non-Goals” and “Constitutional Exclusions”, excludes dashboards, browser apps, visualization engines/grammars, arbitrary exploration, and portal/navigation responsibilities. |
| 21 | Pre-candidate presentation-request contract | **missing** | Existing intake is via builder inputs and upstream references; no owned, named pre-candidate request contract exists. `RendererAdapterRequest` is post-ready renderer invocation (`renderer_adapter.py`) and must not be overloaded. |
| 22 | Portable materialized presentation-input boundary | **missing** | TASK-039 proves file-backed consumption of an upstream-owned analytical package, and `UpstreamReference`/downstream integration provide related concepts. No generic portable, materialized pre-candidate contract exists. It must not import acquisition, normalization, ingestion, analysis, or acceptance authority into BriefForge. |
| 23a | Observation | **partially implemented** | Presentation grammar/models can carry factual/evidence statements, but no complete accepted epistemic role taxonomy distinguishes observation from all adjacent roles. |
| 23b | Reusable evidence | **partially implemented** | Evidence references and provenance are implemented; role semantics as a first-class statement category are incomplete. |
| 23c | Accepted finding | **partially implemented** | Upstream accepted findings can be referenced/presented (TASK-039), but BriefForge does not own analytical acceptance and lacks a full role contract. |
| 23d | Interpretation | **partially implemented** | Existing narrative/communication items can express interpretation, but role authority and validation are incomplete. |
| 23e | Hypothesis | **already specified** | ADPM distinguishes hypotheses/uncertainty and ownership boundaries; no general runtime statement-role representation is implemented. |
| 23f | Scenario | **already specified** | ADPM includes planning/scenario semantics; runtime role representation remains absent. |
| 23g | Recommendation | **already specified** | ADPM recommendation completeness is adopted; current presentation models can render recommendation-like text, but ADPM representation is not implemented. |
| 23h | Uncertainty | **partially implemented** | Caveat/uncertainty communication exists and ADPM specifies richer semantics; complete typed role representation/validation does not. |
| 23i | Caveat | **already implemented** | Package validation, grammar, renderer, and TASK-039 prove caveat preservation. |
| 23j | Personal annotation | **missing** | No accepted personal-annotation role, authority, lifecycle, or renderer obligation exists. |
| 24a | Navigation | **already implemented** | Bounded in-document ordering, headings, anchors, and contents navigation exist in the minimal HTML renderer and tests; global/cross-report navigation remains outside BriefForge. |
| 24b | Presentation inspection | **already implemented** | Native disclosure, evidence/caveat inspection, and rendered conformance are proven in HTML outputs and TASK-039 browser inspection. |
| 24c | Declared/prevalidated selection | **missing** | Doctrine does not yet define which parameterized selections preserve semantic validity without recalculation. This is the narrow interactive authority gap. |
| 24d | Analytical recalculation | **intentionally prohibited** | Analysis and statistical computation are upstream responsibilities; BriefForge renders accepted/materialized inputs. |
| 24e | Open-ended exploration | **intentionally prohibited** | Explicitly outside the presentation-only boundary and constitutional exclusions. |
| 25 | Renderer transformation sovereignty | **already specified** | `docs/renderer-adapter-boundary.md`, `docs/rendered-artifact-conformance.md`, and `D-20260708-adpm-architecture-integration.md` keep renderer transformations derivative, read-only, and non-canonical. Renderers cannot create semantic authority. |
| 26 | Publication identity, versioning, correction, rerender, supersession, withdrawal, and staleness | **partially implemented** | Package IDs, fingerprints, validation-policy IDs, renderer IDs/versions, generated artifacts, and ADPM semantic/profile version distinctions exist. A unified publication-semantic lifecycle distinguishing semantic correction from renderer-only rerender, supersession, withdrawal, and staleness is not specified or implemented. |
| 27 | Explicit missing, zero, not-applicable, suppressed, unresolved, unavailable, invalid, conflicting, stale, and withdrawn states | **missing** | Individual validation failures/caveats exist, but no accepted complete typed state vocabulary distinguishes these semantically across presentation input/package/publication. Do not infer absence from zero or invalidity from unavailability. |
| 28 | Renderer capability declarations and explicit fallback behaviour | **partially implemented** | Adapter contracts and bounded renderer/conformance checks declare supported behaviour; tests exercise specific capability paths. Semantic fallback requirements for unsupported statements/exhibits/interactions are incomplete and must fail visibly rather than silently transform meaning. |
| 29 | Stable identifiers, deep links, scoped styles, standalone operation, optional embedding, and manifest support | **partially implemented** | Deterministic/stable authored identifiers (`TASK-016`, builder tests), HTML anchors/deep links, scoped renderer styles, and standalone artifacts are implemented/proven. Optional embedding responsibility and a publication manifest boundary are not fully specified; neither should create AtlasForge ownership or portal coupling. |

## 4. Concepts to reuse; duplications avoided

Reuse:

- Presentation Contract, Composition Semantics, and Presentation Validation Obligations.
- Candidate Presentation Package → Validation Judgment → Ready Presentation Package.
- Presentation Grammar, Organizing Purpose, ordered sections/items, and experimental EncounterSemantics/Communication Intent evidence.
- UpstreamReference and existing file-backed integration proofs.
- RendererAdapterRequest only for ready-package renderer invocation.
- Renderer adapter boundary and rendered-artifact conformance.
- semantic fingerprints, deterministic authoring IDs, package/renderer/policy identifiers, and separate ADPM semantic/profile versions.
- renderer backlog/improvement policy and MetaHarvest’s advisory status.

Avoided duplications:

- no second publication-readiness lifecycle beside Candidate → Judgment → Ready;
- no generic “request” conflating pre-candidate intent/intake with RendererAdapterRequest;
- no “ResolvedInput” that imports ingestion, normalization, analytical acceptance, or live upstream runtime dependencies;
- no template/archetype/profile platform inferred from bounded presentation models;
- no publication manifest treated as an AtlasForge portal, registry, or discovery implementation;
- no new statement taxonomy declared before reconciling Presentation Grammar, ADPM, EncounterSemantics, and upstream analytical ownership;
- no renderer capability expansion used to compensate for missing semantic contracts.

## 5. TASK-039 planning collision

TASK-039 remains exclusively the completed demographic/correlation browser report. No completed artifact was renamed, modified, or reinterpreted.

Active correction:

- `artifacts/decision_support_backlog.md`, “Recommended future workstream (identifier unreserved)”, removes the stale prospective TASK-039 reservation.
- `state/project_state.md` points to the unreserved later semantic task rather than a colliding ID.
- generated context is rebuilt from corrected current state.

Unmodified historical occurrences remain in:

- `artifacts/decisions/D-20260708-adpm-representation-architecture.md`;
- `artifacts/reports/R-20260708-adpm-representation-architecture-evaluation.md`;
- `artifacts/reports/R-20260708-adpm-representation-recommendations.md`;
- `state/recent_changes.md` historical TASK-038 entry;
- `artifacts/renderer_backlog.md` historical sequencing text.

Those are preserved as historical evidence or are outside this task’s authorized correction surface. This report supplies the current correction rather than rewriting history.

## 6. MacroForge financial-semantic deferral

Exact location: `artifacts/decision_support_backlog.md`, `DSB-007 — Defer company and financial-domain semantics to upstream operational evidence`.

Exact wording:

> Category:
> - Cross-project semantic ownership / deferred compatibility
>
> Severity:
> - Deferred; non-blocking for generic BriefForge development
>
> Evidence:
> - BriefForge is presentation-only and does not own source-data acquisition, canonicalization, company-data ingestion, or financial-domain analytical meaning.
> - No current BriefForge operational evidence justifies canonical company or financial-domain fields in ADPM.
>
> Recommended improvement:
> - BriefForge defers canonical semantics for fiscal periods; financial-reporting dates; restatements; corporate actions; currency conversion; company consolidation; security identity; reporting segments; reported-versus-adjusted values; and related company and financial-domain concepts.
> - MacroForge should first encounter and define these concepts through operational company and financial-data work.
> - After those concepts stabilize upstream, BriefForge should conduct a bounded compatibility review, consume upstream definitions where appropriate, and add only presentation-specific obligations that MacroForge does not own.
> - Until then, ADPM may support generic typed external references and bounded extensibility, but it must not contain speculative financial-domain fields.
>
> Implementation status:
> - Semantic deferral; no BriefForge runtime dependency on MacroForge and no blocker for generic BriefForge development.
>
> Boundary assessment:
> - This deferral does not cover BriefForge-owned publication semantics: publication identity; semantic publication version; evidence-snapshot reference; renderer version; generated-artifact version; publication time; correction; rerender; supersession; withdrawal; and staleness.
> - MacroForge remains the prospective upstream semantic owner only after operational evidence stabilizes those concepts; BriefForge remains independently operable.
>
> Threshold status:
> - Revisit only after upstream operational company/financial semantics stabilize; do not speculate now.

This is a deferred backlog entry, not an activated task or runtime dependency.

## 7. Constitutional interactive-publication verdict

Existing doctrine supports part of the intended distinction but remains narrow and partially ambiguous.

Supported now:

- complete standalone static publications;
- stable in-document anchors/navigation;
- native disclosure/inspection;
- bounded, non-canonical HTML/SVG exhibits;
- derivative renderer transformation that cannot alter semantic authority.

Not authorized now:

- JavaScript application state;
- analytical recomputation;
- arbitrary filtering/querying;
- dashboards;
- persistent browser applications;
- global routing/search/discovery;
- visualization engines or grammars.

Evidence: `CONSTITUTION.md`, “Non-Goals”, “Ownership Boundaries”, and “Constitutional Exclusions”; `docs/renderer-adapter-boundary.md`; `docs/rendered-artifact-conformance.md`; `docs/renderer-improvement-policy.md`; implemented minimal HTML/SVG proofs.

Verdict: doctrine already distinguishes presentation ownership from exploration/application ownership in responsibility terms, and existing bounded renderers prove that derivative artifact generation is allowed. However, literal “no rendering engines” language is ambiguous against implemented renderer terminology, and declared/prevalidated selection has no authority contract. No constitutional change is justified now. The narrow later specification should clarify that a bounded self-contained derivative publication is not a persistent analytical/browser application, while preserving all current prohibitions. Any broader capability still requires independent evidence and approval.

## 8. Recorded contradictions and follow-up destinations

| Finding | Disposition |
|---|---|
| `CONSTITUTION.md` contains stale historical language saying implementation has not begun. | **State/architecture reconciliation task.** Correct current-vs-historical wording only after a bounded constitutional consistency review; no change here. |
| Literal “no rendering engines” wording is ambiguous against existing bounded renderer implementation. | **Next publication-boundary specification task** for a narrow responsibility clarification; constitutional amendment only if that specification proves unavoidable. |
| Doctrine supports static standalone publications, anchors, disclosure, and bounded non-canonical exhibits, but not JS app state, recomputation, arbitrary filtering, dashboards, routing, search, or visualization grammars. | **Next publication-boundary specification task** should preserve this line while defining derivative publication scope. |
| TASK-039 renderer audit metadata says no table exhibit is present although HTML/inspection evidence contain a small statistical table. | **Bounded metadata-correction task.** Historical renderer output/evidence must not be silently rewritten here. |
| `state/architecture.md` references missing `templates/`. | **State/architecture reconciliation task.** Determine whether the reference is obsolete or an expected path; do not create templates merely to silence the audit. |
| Architecture-to-reality audit reports nine completed tasks since the latest formal audit. | **No separate product/semantic action.** Run and record the established formal audit during this governance closeout; address only substantive findings it produces. |

## 9. Gate verdict

**PROCEED WITH PRECONDITIONS**

Repository reality does not reveal a contradiction that requires pausing generic semantic work, but foundational work must resolve bounded publication/intake/lifecycle questions before representation, schema, validation, or renderer implementation.

Preconditions for the next task:

1. Reuse Candidate → Judgment → Ready rather than creating publication readiness.
2. Distinguish pre-candidate intake from RendererAdapterRequest.
3. Keep portable input materialized and upstream-independent without importing acquisition/analysis authority.
4. Reconcile publication terminology with existing constitutional/ADPM “freeze” meanings.
5. Preserve the strict derivative-publication versus browser/exploration boundary.
6. Define manifest consumption as optional downstream interoperability, not AtlasForge implementation or dependency.
7. Keep financial-domain concepts deferred as DSB-007.

## 10. Exact recommended workstream decomposition

### Next task — one task only, not activated

**Publication Boundary, Intake, Portability, and Lifecycle Foundations**

It should specify, using existing concepts where possible:

- publication artifact taxonomy and terminology, including a non-colliding term for an immutable released snapshot;
- a distinctly named pre-candidate presentation-request/intake boundary;
- a portable materialized presentation-input boundary without upstream runtime dependency or imported acquisition/analysis authority;
- relationship to CandidatePresentationPackage and the existing Candidate → Judgment → Ready lifecycle;
- publication identity and semantic publication version;
- evidence-snapshot identity;
- renderer version and generated-artifact version;
- publication time;
- correction versus renderer-only rerender;
- supersession, withdrawal, and staleness;
- a minimal publication-manifest boundary and optional AtlasForge consumption without portal coupling;
- narrow clarification of bounded derivative publications versus prohibited browser applications/rendering platforms.

Non-goals: no representation profile, schema, serializer, validator, renderer, JavaScript interaction, portal, AtlasForge implementation, or financial-domain semantics.

### Later separate task

Only after the first task stabilizes publication/intake/lifecycle boundaries, address:

- accepted statement-role taxonomy and its relationship to Presentation Grammar, EncounterSemantics, and Communication Intent;
- interaction authority, including declared/prevalidated selection;
- renderer transformation sovereignty;
- explicit missing/conflicting/invalid/stale/withdrawn evidence states;
- renderer capability failures and semantic fallback behaviour.

Combining both would couple publication identity/lifecycle to unresolved epistemic-role and renderer-failure semantics, creating an oversized contract and increasing duplication risk. The repository supports the two-stage decomposition.

## 11. Scope confirmation

This task changed no constitution, ADPM specification/decision, source code, tests, renderer, styles, publications, TASK-039 presentation artifacts, schema, serialization, fixtures, AtlasForge, or other EIP project. It initialized no Git repository and made no commit or push.
