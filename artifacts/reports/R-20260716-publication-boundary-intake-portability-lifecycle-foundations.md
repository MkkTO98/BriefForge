# Publication Boundary, Intake, Portability, and Lifecycle Foundations

Date: 2026-07-16
Task: TASK-041
Status: Complete
Gate: **CLEAR TO PROCEED**

## 1. Purpose and method

This report records the focused evidence, adversarial reasoning, accepted decisions, and gate for the first BriefForge semantic-foundation task after TASK-040. It does not repeat the whole-repository capability audit.

Method:

1. recover and inspect project instructions;
2. confirm TASK-041 availability;
3. record the deterministic non-Git baseline;
4. treat TASK-040 as accepted starting evidence;
5. inspect authoritative ADPM, publication, renderer, state, and complete TASK-039 evidence;
6. distinguish semantic responsibilities before considering representation;
7. reject models that require BriefForge to gain analytical, ingestion, portal, application, or financial-domain authority;
8. pressure-test the accepted model;
9. record bounded decisions and specification only.

## 2. Recovery, identifier, and non-Git baseline

`PYTHONDONTWRITEBYTECODE=1 python3 tools/recover_session.py --project . --json` exited 0. Recovery identified TASK-040 as complete, no semantic-specification or implementation task active, and the recommended next workstream as Publication Boundary, Intake, Portability, and Lifecycle Foundations.

Only one `AGENTS.md` applies. It and all eight files under `instructions/` were inspected before mutation.

TASK-041 availability was directly checked by filename and content search. No `TASK-041` occurrence existed at baseline; TASK-040 was complete and current state named this workstream without reserving an identifier. TASK-041 is therefore the next valid identifier.

BriefForge remains intentionally non-Git. No repository was initialized or sought elsewhere.

Baseline manifest:

- path: `/tmp/briefforge-before-task041-20260716.json`;
- SHA-256: `898aaf2d9a20fd9f5c05825e098d87bf94d266988c627998a6cf93494436d066`;
- included paths: 550;
- entries: regular-file SHA-256 and size, directory path/type, and symlink target;
- excluded directory components: `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `__pycache__`;
- excluded file suffixes: `.pyc`, `.pyo`;
- all baseline files are treated as pre-existing state; the manifest proves task-local mutation only, not historical authorship or cleanliness.

## 3. Focused evidence inspected

Primary evidence:

- `artifacts/tasks/TASK-040-current-state-capability-reconciliation.md`, Outcome;
- `artifacts/reports/R-20260716-current-state-capability-reconciliation.md`, capability matrix, duplication analysis, constitutional verdict, and exact next-task decomposition;
- `artifacts/decision_support_backlog.md`, future workstream and DSB-007;
- `artifacts/specifications/architectural-decision-package-model.md`, lifecycle/ownership, immutability, publication expression, and extension rules;
- `artifacts/decisions/D-20260708-adpm-representation-architecture.md`, specification-first architecture and separate semantic/profile versions;
- `artifacts/decisions/D-20260708-adpm-architecture-integration.md`, lifecycle, authority, read-only publication/derived views, and immutable lineage;
- `artifacts/decisions/D-20260708-adpm-validation-decision.md`, rejected duplicate objects and renderer independence;
- `artifacts/reports/R-20260708-adpm-representation-architecture-evaluation.md`, semantic-canonical alternatives and immutable-document analysis;
- `artifacts/reports/R-20260708-adpm-representation-recommendations.md`, especially Recommendations 2, 6, 11, 12, and 15;
- `docs/operational-publication-workflow.md`, Candidate -> Ready -> renderer -> conformance evidence chain;
- `docs/renderer-adapter-boundary.md`, post-Ready read-only `RendererAdapterRequest`;
- `docs/rendered-artifact-conformance.md`, derivative audit-link obligations;
- `docs/renderer-improvement-policy.md` and `docs/renderer-backlog-specification.md`, evidence gate and application/platform exclusions;
- `CONSTITUTION.md`, constitutional core, ownership exclusions, operating principles, and implementation bridge;
- `state/architecture.md`, frozen runtime/renderer boundaries and operational evolution;
- `state/project_state.md` and `context/latest_handoff.md`, TASK-040 gate and assigned follow-ups.

Complete TASK-039 evidence inspected:

- task, boundary decision, and outcome report;
- InsightForge source fixture `T-035-demographic-growth-correlation-report-input.json`;
- candidate package, validation judgment, Ready package;
- generated HTML, conformance record, renderer audit metadata, inspection report, and presentation summary.

TASK-039 proves a useful separation: InsightForge selected the analytical question and materialized accepted KnowledgeForge values; BriefForge constructed presentation statements/obligations, validated/promoted the package, and generated a derivative artifact without recomputation (`D-20260713-demographic-correlation-browser-report-boundary.md`, Boundary; candidate package `ref-insightforge-t035-input`; source fixture `presentation_obligations_for_briefforge`). It does not prove generic intake, portable-material, publication identity, or lifecycle contracts.

The known TASK-039 renderer metadata/table inconsistency was observed but not modified.

## 4. Existing concepts reused and duplications avoided

Reused:

- the frozen Presentation Contract, Organizing Purpose, Composition Semantics, Presentation Grammar, and Presentation Validation Obligations;
- PresentationStatement, EncounterSemantics, PresentationObligation, and UpstreamReference;
- CandidatePresentationPackage -> ValidationJudgment -> ReadyPresentationPackage;
- semantic fingerprint and deterministic authored identifiers;
- renderer identity/capability declaration and `RendererAdapterRequest` only after Ready;
- rendered-artifact conformance and non-canonical output;
- ADPM authority-separation, immutability/lineage, semantic/profile-version separation, source evidence owner, publication expression, derived view, and local adoption authority.

Duplications rejected:

- no second readiness or promotion lifecycle;
- no intake overload of `RendererAdapterRequest`;
- no `ResolvedInput` that suggests BriefForge resolves analytical meaning;
- no publication manifest as package, registry, portal, or semantic authority;
- no publication artifact as canonical meaning;
- no template/archetype/profile or browser-application subsystem;
- no speculative financial-domain additions to ADPM or Presentation Package;
- no new audience/persona platform.

## 5. Accepted publication-layer model

The accepted layers are:

1. upstream evidence and accepted upstream statements;
2. Presentation Intake, comprising Presentation Brief and Portable Presentation Material;
3. Candidate Presentation Package;
4. Validation Judgment;
5. Ready Presentation Package;
6. immutable Publication Release Record;
7. renderer invocation through the established adapter boundary;
8. generated publication artifact;
9. derivative publication manifest;
10. optional downstream catalogue/embedding surface.

The full owner, authority, mutability, identity, input/output, failure, canonical/derivative, and offline-existence matrix is canonical in `artifacts/specifications/publication-boundary-intake-portability-lifecycle.md`, section 4.

The key adversarial finding is that publication cannot be only a mutable Ready status. Ready proves valid presentation meaning but does not establish that publication happened, release time, semantic publication lineage/version, exact evidence binding, or later withdrawal/staleness/supersession. A small immutable Publication Release Record is therefore justified. It references rather than copies the Ready package and creates no second validity gate.

## 6. Publication taxonomy and terminology

Accepted:

### Fixed-evidence standalone publication

Bound to an exact evidence snapshot and Ready fingerprint; semantically deterministic; reproducible from retained portable material; complete without AtlasForge or live upstream systems; BriefForge-owned only at presentation/publication level.

`Frozen publication` is rejected because constitutional freeze and ADPM frozen package state already carry governance meaning.

### Bounded parameterized publication

Recognized only as a deferred category boundary. No selector or parameterized instance is admitted. Later work must prove finite predeclared states, prevalidation, known affected components, valid narrative in every state, evidence preservation, static fallback, and no recomputation.

### Publication manifest

Accepted as derivative machine-readable catalogue/embedding metadata emitted by BriefForge. It is not authority, a portal database, AtlasForge implementation, discovery service, or global-navigation model.

Explicitly excluded:

- live entity and continuously updated company pages;
- exploratory workspaces and arbitrary querying/comparison;
- dashboards, portals, global search/discovery, persistent analytical applications;
- AtlasForge application responsibilities.

## 7. Intake-boundary decision

Accepted name: `Presentation Intake`.

It is a governed authoring boundary with two authority-separated sub-responsibilities:

- `Presentation Brief`: requestor communication need and constraints;
- `Portable Presentation Material`: upstream-authority-asserted material needed for presentation.

This split is necessary rather than speculative: a requestor can own communication need without owning evidence, and an upstream owner can assert material without owning BriefForge presentation approval.

Minimum Brief semantics:

- organizing purpose;
- intended audience description;
- decision/communication context;
- subjects and non-scope;
- governed upstream references;
- supplied/requested statements;
- requested publication category/output/interactions;
- requestor and authority declarations;
- sensitivity/distribution constraints;
- forbidden inferences/transformations.

Minimum audience semantics are only audience identity/use context, material knowledge/terminology assumptions, and accessibility/sensitivity/distribution needs. Personas, segmentation, personalization, sessions, and user profiles are rejected.

Outcomes are exactly conceptual admission states, not runtime enums: admitted for candidate construction, incomplete, or rejected. Intake admission never creates or validates a Candidate.

## 8. Portable materialized-input decision

Accepted name: `Portable Presentation Material`.

The upstream owner or its authorized exporter materializes and asserts meaning. BriefForge may validate integrity, declared authority, presentation completeness/compatibility, internal reference consistency, preservation obligations, and offline reproducibility. BriefForge must reject rather than acquire, repair, canonicalize, normalize, recompute, infer, rank, re-accept findings, or silently fill gaps.

Portable material may carry upstream identities, materialized exhibit values, semantic types/units/subjects, accepted statements, evidence scope/snapshot, caveats, provenance, sensitivity/distribution constraints, permitted transformations/interactions, and generic typed external references.

It is associated with Candidate construction. Whether future representation embeds or immutably references it is deferred. Semantically, exact retained material and fingerprints must remain sufficient to validate/regenerate fixed-evidence releases with every upstream runtime offline.

## 9. Relationship to Candidate -> Judgment -> Ready

Accepted sequence:

```text
Presentation Intake
-> candidate construction
-> Candidate Presentation Package
-> Validation Judgment
-> Ready Presentation Package
-> Publication Release Record
-> renderer invocation
-> generated artifact
-> output conformance
-> derivative manifest
-> optional downstream catalogue/embed
```

No earlier state implies a later state. Publication approval checks exact Ready/evidence binding, category, authority, and release obligations; it does not rerun or replace semantic validation. Artifact conformance never becomes semantic authority.

## 10. Lifecycle and version model

Distinct identities/axes are accepted for:

- semantic publication identity;
- semantic publication version;
- evidence-snapshot identity;
- Ready package identity/fingerprint;
- renderer identity/version;
- generated-artifact identity/version;
- manifest artifact identity/version;
- publication/release time;
- lifecycle-event time.

Rules:

- semantic correction or evidence replacement -> new semantic version, Ready fingerprint, judgment, release, artifacts, and manifest;
- renderer-only correction/rerender/regeneration -> same semantic version and evidence/Ready binding, new artifact version, conformance, and updated manifest if needed;
- supersession -> explicit lineage; prior release remains addressable;
- withdrawal -> historical identity/evidence preserved; active-use authority removed;
- staleness -> authority-declared/propagated status, not a polling service;
- manifest regeneration -> manifest artifact change only when authorities are unchanged.

No financial-time semantics are imported.

## 11. Manifest-property classification

| Property | Primary classification |
|---|---|
| Manifest artifact identity/version | required |
| Publication identifier | required |
| Semantic publication version | required |
| Title | required |
| Organizing Purpose | required |
| Publication category | required |
| Evidence-snapshot identifier | required |
| Ready package identity/fingerprint | required |
| Renderer identity/version per artifact | required |
| Generated-artifact identity/version | required |
| Publication/release time | required |
| Lifecycle status | required |
| Supersedes/superseded-by | optional; conditionally required when applicable |
| Withdrawal details | optional; conditionally required when withdrawn |
| Staleness details | optional; conditionally required when stale |
| Stable section/statement IDs and deep links | derived |
| Available artifact formats | required |
| Standalone entry point | required |
| Sensitivity/distribution designation | required |
| Reproducibility fingerprints | required |
| Embedding information | optional |
| Audience description | derived |
| Requestor identity | prohibited by default |
| AtlasForge routes/search/rank/portal/user/session/global navigation | prohibited |
| Canonical schema/serialization hints | prohibited |
| Parameter state/selector definition | deferred |
| Detailed evidence-state/fallback vocabulary | deferred |

Properties classified required may be copied from an authority but remain derivative in the manifest. Conditional requirements do not make absent, inapplicable lifecycle relationships mandatory noise.

## 12. AtlasForge boundary

AtlasForge may consume manifest metadata, catalogue semantic versions, link to standalone artifacts, or embed them when policy permits. AtlasForge owns its catalogue/view state.

BriefForge knows no AtlasForge routes, indices, portal structure, ranking, users, sessions, permissions implementation, or navigation. AtlasForge failure cannot invalidate a publication, artifact, Ready package, or manifest. AtlasForge cannot mutate BriefForge authority.

## 13. Constitutional and renderer-boundary verdict

**Existing doctrine is sufficient when read coherently; the new bounded decision is sufficient; no constitutional wording change is presently necessary.**

Evidence:

- `CONSTITUTION.md` defines exclusions as responsibilities BriefForge must not own, keeps rendered targets non-canonical, and permits later concrete representations through its implementation bridge when the frozen core is preserved.
- `docs/renderer-adapter-boundary.md` makes renderer invocation post-Ready and read-only.
- `docs/rendered-artifact-conformance.md` makes artifacts derivative and audit-linked.
- renderer policy/backlog prohibit browser/application/platform evolution.
- TASK-039 proves a bounded standalone HTML artifact without application state or recomputation.

Accepted clarification: a separately approved bounded renderer adapter may generate standalone deterministic artifacts without becoming a constitutional rendering-engine responsibility. Permitted mechanics are layout/formatting, internal anchors/navigation, disclosure, bounded static exhibits, scoped styles, and accessible/print derivatives that preserve meaning.

Still prohibited: persistent app state, recomputation, arbitrary filtering/querying/comparison, dashboards, routing/global navigation, search/discovery/ranking, visualization grammars, template/component platforms, and live entity pages.

The literal `rendering engines` wording is awkward but not an irreconcilable contradiction. Amendment would be justified only if later evidence proves responsibility interpretation cannot preserve mission/boundaries—not because a renderer feature is attractive. Declared/prevalidated selection remains deferred.

## 14. Adversarial scenario results

| # | Scenario and verdict | Responsible owner | Identity/version consequence | Lifecycle consequence and failure behaviour | Later work? |
|---|---|---|---|---|---|
| 1 | TASK-039 identical semantics, corrected CSS: **admitted as renderer-only correction** | Renderer/publication pipeline; BriefForge publication records artifact lineage | Publication/evidence/Ready stable; renderer version changes if code changed; new artifact version; manifest version if changed | No new judgment; output conformance required; prior artifact remains addressable/marked replaced or defective | No semantic work |
| 2 | Corrected statistical value from upstream: **admitted only as semantic correction** | Upstream owner corrects evidence; BriefForge rebuilds/revalidates presentation | New evidence snapshot, Ready fingerprint, semantic publication version, artifacts, manifest | New judgment and release; old release retained with supersession/amendment relationship | Evidence-state detail may refine later |
| 3 | Renderer version changes, Ready unchanged: **admitted as rerender** | Renderer layer | Semantic version stable; new renderer and artifact versions | No new semantic judgment; conformance required | No |
| 4 | Artifact corrupt, semantic release valid: **artifact rejected/replaced; release remains valid** | Artifact storage/publication pipeline | New artifact identity/version on regeneration; semantic identities stable | Mark corrupt artifact unusable; regenerate from retained inputs; conformance required | Detailed fallback later |
| 5 | Evidence snapshot becomes stale: **admitted as staleness declaration, not silent refresh** | Upstream freshness authority declares; BriefForge publication authority propagates | Identities/semantic version stable until replacement | Add staleness lifecycle event/status and manifest exposure; no polling; replacement creates new semantic release | Evidence-state semantics later |
| 6 | Upstream artifact withdrawn: **active use rejected pending authority disposition** | Upstream owner declares withdrawal; BriefForge publication authority marks dependent release stale/withdrawn as declaration requires | Existing identities retained; replacement requires new evidence/version | Never delete history; expose withdrawal/staleness and block misleading active use; no live reacquisition | Evidence-state semantics later |
| 7 | AtlasForge unavailable: **publication remains admitted/valid** | AtlasForge owns its outage | No BriefForge identity/version change | Standalone artifact and manifest continue; catalogue/embed fails locally only | No |
| 8 | AtlasForge catalogues two semantic versions: **admitted** | AtlasForge catalogue, using BriefForge lineage metadata | One publication identity, two semantic versions, distinct Ready/evidence/artifacts | Both addressable; current/superseded status follows BriefForge records | No implementation here |
| 9 | Regenerate with all upstream projects offline: **admitted only if portable retention is complete** | BriefForge publication pipeline | Semantic identities stable; new artifact version | Regenerate and conform from retained material; if material absent/inconsistent, fail closed and do not reacquire/substitute | Implementation later |
| 10 | Intake asks BriefForge to calculate a new correlation: **rejected** | Requestor returns task to InsightForge/KnowledgeForge or proper analytical owner | No Candidate/publication identity | Intake rejection names analytical-authority violation | No; ownership already clear |
| 11 | Intake lacks Organizing Purpose: **incomplete/rejected before Candidate** | Requestor supplies communication need; BriefForge may restate but not invent analysis | Intake audit identity only | Candidate construction blocked; missing-input outcome identifies owner | No |
| 12 | Company comparison needs unstabilized fiscal periods: **rejected/deferred under DSB-007** | MacroForge first encounters/defines semantics | No BriefForge semantic publication | Intake rejection/defer; generic external references do not cure missing domain meaning | Bounded compatibility review after upstream stabilization |
| 13 | Finite selector lacks proof of narrative validity for every state: **rejected as parameterized publication** | Requestor/upstream owner must supply proof; later BriefForge semantic review | No parameterized release | Static fixed-evidence publication may proceed only without selector; no hidden recomputation | Yes: next semantic-authority task |
| 14 | Manifest conflicts with Ready/lifecycle authority: **manifest rejected** | Manifest emitter/publisher | Semantic identities unchanged; corrected manifest gets new manifest version | Fail closed, regenerate from authorities; manifest never corrects Ready/release | Implementation later |

No scenario requires BriefForge to acquire analysis, ingestion, portal, financial-semantic, or open-ended exploration authority.

## 15. Accepted, rejected, and deferred proposals

Accepted:

- Presentation Intake, Presentation Brief, Portable Presentation Material;
- fixed-evidence standalone publication;
- immutable Publication Release Record after Ready;
- independent identity/version axes;
- generic correction/rerender/supersession/withdrawal/staleness/regeneration semantics;
- derivative manifest and optional AtlasForge consumption;
- bounded derivative-publication responsibility clarification.

Rejected:

- frozen-publication terminology;
- status-only mutable publication on Ready;
- second readiness lifecycle;
- RendererAdapterRequest as intake;
- ResolvedInput and live upstream dependencies;
- manifest/artifact canonical authority;
- AtlasForge coupling;
- browser/application/platform capabilities;
- speculative financial-domain semantics;
- implementation during this task.

Deferred:

- bounded parameterized publication admission;
- statement roles and semantic authority;
- declared selection and broader interaction authority;
- missing/conflicting/invalid/stale/withdrawn evidence-state taxonomy;
- renderer capability failure and semantic fallback;
- representation profiles, schema, serialization, validators, runtime, renderers, manifest emitters, and AtlasForge integration.

Separate findings deliberately not fixed: TASK-039 table metadata inconsistency, missing `templates/` reference, and stale general `implementation has not begun` wording.

## 16. Gate verdict and exact next task

**CLEAR TO PROCEED**

The second foundational semantic task may begin. TASK-041 resolved the publication/intake/portability/lifecycle distinctions without duplicating readiness or violating ownership. No unresolved contradiction blocks the next semantic layer.

Exactly one next task is recommended, not activated:

**TASK-042 — Semantic Authority, Evidence States, Interaction, and Renderer Fallback Foundations**

Why this is correctly bounded:

- it consumes the publication categories, intake authorities, release lifecycle, and manifest boundary established here;
- it can decide statement roles, EncounterSemantics/Communication Intent relationships, navigation/inspection/declared-selection authority, transformation sovereignty, evidence failure states, and renderer fallbacks as one coupled semantic-failure layer;
- it must not reopen publication identity/lifecycle or begin representation/implementation;
- separating it prevents publication release semantics from being entangled with unresolved epistemic roles and renderer failure behaviour.

No representation or renderer implementation should be recommended until both semantic layers are coherent and a later gate explicitly authorizes implementation planning.

## 17. Decision artifacts

Accepted decisions:

- `artifacts/decisions/D-20260716-publication-layer-intake-and-portability.md`;
- `artifacts/decisions/D-20260716-publication-lifecycle-and-manifest.md`;
- `artifacts/decisions/D-20260716-derivative-publication-responsibility.md`.

Canonical specification:

- `artifacts/specifications/publication-boundary-intake-portability-lifecycle.md`.

These decisions refine responsibilities but do not amend `CONSTITUTION.md`, ADPM ontology/representation architecture, Presentation Package runtime, or renderer implementation.
