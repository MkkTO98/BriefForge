# TASK-041 — Publication Boundary, Intake, Portability, and Lifecycle Foundations

Status: Completed
Owner: project-owned
Created: 2026-07-16

## Request

Specify and decide BriefForge's publication boundary, pre-candidate presentation intake, portable materialized presentation input, relationship to Candidate Presentation Package -> Validation Judgment -> Ready Presentation Package, publication identity/lifecycle, minimal publication-manifest semantics, optional AtlasForge consumption, and bounded derivative-publication responsibility.

## Identifier check

TASK-041 was available before activation: no repository path or content occurrence used `TASK-041`, TASK-040 was complete, and current state recommended this workstream without reserving an identifier. TASK-041 is therefore the next repository-consistent identifier.

## Methodology slice

- Objective: establish the smallest coherent semantic model needed before the later semantic-authority/failure-behaviour task.
- Architectural uncertainty: whether publication is merely Ready status, a release event, or a distinct record; whether intake and portable material can share authority; and whether bounded derivative renderers conflict with constitutional exclusions.
- Explicit non-goals: no representation profile, field schema, serialization, validator, source/runtime/test/renderer change, HTML/SVG/publication regeneration, AtlasForge implementation, browser application, portal, financial-domain semantics, or constitutional amendment.
- Implementation boundary: one semantic specification, three bounded decisions, one evidence report, backlog/state/continuity updates, affected summaries, and generated closeout context.
- Readiness prerequisites: successful recovery; all instructions inspected; TASK-041 availability confirmed; non-Git baseline manifest recorded; TASK-040 accepted as starting evidence; TASK-039 evidence inspected without mutation.
- Success criteria: terminology, layers, intake, portable input, lifecycle/version axes, manifest boundary, AtlasForge independence, renderer/application distinction, 14 adversarial scenarios, explicit deferrals, and gate verdict are durable and mutually coherent.
- Verification expectations: artifact consistency, coherence, context health, architecture-to-reality audit, context regeneration, and exact deterministic before/after manifest comparison.
- Post-slice decision: preserve the specification; authorize only the next specification-and-decision task, not implementation.

## Scope

1. Reconcile and reuse existing Presentation Package and ADPM concepts.
2. Define `Presentation Intake` as a governed pre-candidate boundary.
3. Define `Portable Presentation Material` as upstream-authority-preserving, offline-usable material associated with candidate construction.
4. Add no second readiness lifecycle.
5. Define a `Publication Release Record` only for responsibilities not carried by Ready packages.
6. Define fixed-evidence standalone publication terminology and the deferred boundary of bounded parameterized publication.
7. Define generic publication lifecycle and independent version axes.
8. Define a derivative publication manifest and AtlasForge-facing independence boundary.
9. Clarify bounded derivative publication behaviour versus prohibited application/platform behaviour.
10. Pressure-test the model against concrete failure and lifecycle scenarios.

## Explicit non-scope

- ADPM representation profiles or transport formats.
- JSON/YAML/XML, schemas, serialization, builders, validators, or runtime implementation.
- Renderer code, styles, capabilities, HTML/SVG artifacts, or TASK-039 evidence changes.
- Statement-role taxonomy, declared/prevalidated selection admission, evidence-state vocabulary, transformation sovereignty details, or renderer fallback semantics.
- AtlasForge, portal, search, discovery, global navigation, sessions, or embedding implementation.
- Company or financial-domain semantics deferred under DSB-007.
- Constitutional amendment.
- Separate known follow-ups: TASK-039 table metadata inconsistency, missing `templates/` reference, and stale general implementation wording.

## Governance links

- Specification: `artifacts/specifications/publication-boundary-intake-portability-lifecycle.md`
- Decisions:
  - `artifacts/decisions/D-20260716-publication-layer-intake-and-portability.md`
  - `artifacts/decisions/D-20260716-publication-lifecycle-and-manifest.md`
  - `artifacts/decisions/D-20260716-derivative-publication-responsibility.md`
- Report: `artifacts/reports/R-20260716-publication-boundary-intake-portability-lifecycle-foundations.md`
- Predecessor: `artifacts/tasks/TASK-040-current-state-capability-reconciliation.md`
- Deferred financial semantics: `artifacts/decision_support_backlog.md`, DSB-007

## Outcome

Completed as specification-and-decision work only.

- `Fixed-evidence standalone publication` is accepted terminology.
- `Presentation Intake` and `Portable Presentation Material` are accepted as distinct pre-candidate responsibilities.
- Candidate -> Judgment -> Ready remains the only presentation-readiness lifecycle.
- `Publication Release Record` is accepted as the minimal immutable record of a publication act; it does not duplicate readiness or package meaning.
- Semantic publication, evidence snapshot, Ready package, renderer, generated artifact, and manifest identities/versions remain distinct.
- A publication manifest is derivative catalogue/embedding metadata, never semantic authority.
- AtlasForge consumption is optional and cannot become a BriefForge runtime dependency.
- Bounded derivative publications are compatible with existing doctrine; application/platform behaviour remains prohibited.
- Bounded parameterized publication is recognized only as a deferred category whose admission depends on the next semantic-authority task.
- Gate: **CLEAR TO PROCEED** to one later specification-and-decision task, with implementation still prohibited.

## Notes

BriefForge remains an intentional non-Git project tree. Deterministic `/tmp` manifests prove this task's path/content delta only; they do not establish historical authorship or cleanliness.
