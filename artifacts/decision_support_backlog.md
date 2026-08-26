# Decision-Support Backlog

Date initialized: 2026-07-08
Status: Active architectural backlog
Owner: BriefForge
Scope: architectural investigation decision support

## Governance rule

This backlog records decision-support pressure. It does not authorize implementation.

A decision-support improvement requires:

1. evidence from real investigation artifacts;
2. a clear reader decision problem;
3. an owner boundary showing whether the work belongs in BriefForge, a source evidence-producing project, or a downstream consumer project;
4. a separate approved implementation, modeling, or validation task.

Renderer changes remain governed by `artifacts/renderer_backlog.md` and `docs/renderer-improvement-policy.md`.

## Established model

`TASK-038 Evaluation of ADPM Representation, Serialization, and Validation Architecture` is complete as architecture-only work.

Canonical refined specification:
- `artifacts/specifications/architectural-decision-package-model.md`

Representation architecture artifacts:
- `artifacts/reports/R-20260708-adpm-representation-architecture-evaluation.md`
- `artifacts/reports/R-20260708-adpm-representation-recommendations.md`
- `artifacts/decisions/D-20260708-adpm-representation-architecture.md`

Lifecycle/integration artifacts:
- `artifacts/decisions/D-20260708-adpm-architecture-integration.md`
- `artifacts/reports/R-20260708-adpm-lifecycle-architecture.md`
- `artifacts/reports/R-20260708-adpm-component-responsibilities.md`

Prior model/validation artifacts:
- `artifacts/decisions/D-20260708-architectural-decision-package-adoption.md`
- `artifacts/reports/R-20260708-architectural-decision-package-model.md`
- `artifacts/decisions/D-20260708-adpm-validation-decision.md`
- `artifacts/reports/R-20260708-adpm-adversarial-validation.md`
- `artifacts/reports/R-20260708-adpm-stability-assessment.md`

ADPM is now the canonical renderer-independent semantic lifecycle for decision-support packages, with accepted representation/validation architecture direction.

Freeze posture:
- semantic ontology, lifecycle, ownership, authority boundaries, immutability rules, and representation/validation principles are ready for constitutional freeze;
- serialization formats, schemas, builders, validators, serializers, renderers, examples, APIs, and runtime behavior are not authorized.

## TASK-041 publication-foundation result

`TASK-041 Publication Boundary, Intake, Portability, and Lifecycle Foundations` is complete as specification-and-decision work.

Accepted:
- `Presentation Intake`, with authority-separated Presentation Brief and Portable Presentation Material responsibilities;
- fixed-evidence standalone publication terminology;
- Candidate Presentation Package -> Validation Judgment -> Ready Presentation Package as the only readiness lifecycle;
- immutable Publication Release Record for exact Ready/evidence binding, publication identity/version/time, status, and lineage;
- separate semantic publication, evidence snapshot, Ready package, renderer, generated-artifact, and manifest versions;
- derivative publication manifest and optional AtlasForge consumption without runtime coupling;
- bounded derivative-publication responsibility without application/platform ownership.

Canonical artifacts:
- `artifacts/specifications/publication-boundary-intake-portability-lifecycle.md`;
- `artifacts/reports/R-20260716-publication-boundary-intake-portability-lifecycle-foundations.md`;
- `artifacts/decisions/D-20260716-publication-layer-intake-and-portability.md`;
- `artifacts/decisions/D-20260716-publication-lifecycle-and-manifest.md`;
- `artifacts/decisions/D-20260716-derivative-publication-responsibility.md`.

## TASK-042 semantic-authority/state/interaction/fallback result

`TASK-042 — Semantic Authority, Evidence States, Interaction, and Renderer Fallback Foundations` is complete as specification-and-decision work.

Accepted:
- multidimensional statement semantics separating posture, scoped authority, communication function, encounter/composition, attention, states, and obligations;
- explicit evidence, value, consistency, and lifecycle scopes without one universal status;
- admitted navigation/inspection, conditional finite declared/prevalidated selection, and prohibited recalculation/open-ended exploration;
- complete state-specific narrative validation and static-fallback requirements;
- renderer transformation sovereignty, positive capability obligations, and fail-closed fallback;
- audit-link conformance as necessary but insufficient semantic-output proof;
- Communication Intent remains experimental and DSB-007 remains binding.

Canonical artifacts:
- `artifacts/specifications/semantic-authority-evidence-states-interaction-renderer-fallback.md`;
- `artifacts/reports/R-20260716-semantic-authority-evidence-states-interaction-renderer-fallback-foundations.md`;
- `artifacts/decisions/D-20260716-multidimensional-statement-authority-and-state-semantics.md`;
- `artifacts/decisions/D-20260716-bounded-interaction-authority-and-narrative-consistency.md`;
- `artifacts/decisions/D-20260716-renderer-transformation-sovereignty-and-fail-closed-fallback.md`.

## TASK-043 representation/validation result

`TASK-043 — Semantic Representation Contract and Layered Validation Specification Planning` is complete as specification-and-decision work.

Accepted:
- one renderer-independent semantic graph joining Presentation Brief, Portable Presentation Material, Candidate -> Judgment -> Ready, Publication Release Record, renderer requirements, artifacts, conformance, and derivative manifest;
- stable identity/reference authority, explicit scoped states, complete finite selection, and package-owned renderer requirements;
- seven validation layers and 17 cross-layer invariants;
- a Representation Profile boundary subordinate to semantics.

Canonical artifacts:
- `artifacts/specifications/semantic-representation-contract-and-layered-validation.md`;
- its TASK-043 report and three accepted decisions.

## TASK-044 profile/corpus result

`TASK-044 — Initial Representation Profile and Golden Corpus Acceptance Specification` is complete as the final architecture-only gate.

Accepted:
- `briefforge-core-representation-profile` `1.0.0` (BCRP 1.0) as the single initial renderer-independent profile;
- independently addressable typed records, one-way canonical relations, explicit scoped states, complete finite selection projections, deterministic semantic canonicalization, equality/fingerprint domains, fail-closed extensions, and independent profile versioning;
- exactly three planned golden-corpus cases with valid/adversarial layered expectations and complete responsibility/invariant/lifecycle/fallback coverage;
- deterministic canonical JSON documents as the sole initial serialization direction;
- **CLEAR TO IMPLEMENT** one bounded vertical slice, not automatic activation.

Canonical artifacts:
- `artifacts/specifications/briefforge-core-representation-profile.md`;
- `artifacts/specifications/bcrp-golden-corpus-acceptance.md`;
- `artifacts/reports/R-20260716-initial-representation-profile-and-golden-corpus-acceptance.md`;
- the three accepted TASK-044 decisions.

## Recommended future workstream (not activated)

`TASK-045 — Initial Representation Profile, Layered Validator, and Golden Corpus Vertical Slice`

Scope:
- one deterministic JSON serialization of BCRP 1.0;
- loader/canonicalizer plus structural and core semantic validation;
- materialize the three accepted valid cases and invalid mutations;
- round-trip and expected-finding tests.

Non-goals:
- no current runtime-package migration;
- no renderer, selector, fallback runtime, or AtlasForge integration;
- no second format, converter, company-specific fields, or DSB-007 financial semantics.

## Entries

### DSB-001 — Decision-ready package model and semantic representation architecture established

Category:
- Information architecture / decision support

Severity:
- Resolved as semantic architecture and initial profile; cleared for one bounded implementation slice

Evidence:
- Large investigation corpora showed coherent reports still required readers to manually assemble top conclusions, priority, owner, confidence, uncertainty, and next action.
- TASK-035 produced the initial renderer-independent ADPM specification, adoption decision, and architecture report.
- TASK-036 adversarial validation refined ADPM with authority, boundary, priority, versioning, status, and multi-question support.
- TASK-037 defined lifecycle, ownership, component responsibilities, lifecycle states, package relationships, and authority boundaries.
- TASK-038 evaluated representation alternatives and accepted specification-first semantic contract architecture.
- TASK-043 accepted the renderer-independent semantic object graph, scoped identity/reference/state/selection representation, layered validation authorities, cross-layer invariants, and representation-profile boundary.
- TASK-044 accepted BCRP 1.0, deterministic canonicalization/equality, fail-closed extensions/versioning, and the three-case adversarial corpus plan.

Accepted representation direction:
- ADPM constitutional semantic specification;
- semantic representation contract;
- representation profile contracts;
- transport serialization forms;
- layered validation specifications;
- future implementation only after separate approval.

Implementation status:
- Semantic architecture and BCRP 1.0 profile/corpus acceptance are complete.
- One bounded JSON/profile/validator/corpus vertical slice is cleared for separate activation; renderer/API/runtime-migration work is not authorized.

Boundary assessment:
- Belongs in BriefForge as semantic decision-support architecture.
- Source evidence producers remain evidence owners.
- Consumer projects retain adoption authority.

Threshold status:
- Profile/corpus gate satisfied by TASK-044; ready for one separately activated TASK-045 vertical slice.

---

### DSB-002 — ADPM representation contract and validation specification planning completed

Category:
- Representation / validation planning

Severity:
- Resolved by TASK-043

Evidence:
- TASK-038 concluded that direct JSON/YAML/schema work would risk making representation authority.
- TASK-038 recommended a semantic representation contract before transport profiles.
- TASK-038 established layered validation responsibilities but did not define concrete validation specifications.
- TASK-043 accepted the abstract semantic object graph, representation allocation, validation authority layers, cross-layer invariants, representation-profile boundary, and golden-corpus gate.

Recommended improvement:
- Preserve the accepted TASK-043 semantic representation and layered-validation specifications and TASK-044 BCRP/corpus decisions during the bounded TASK-045 vertical slice.

Implementation status:
- Planning and profile/corpus acceptance completed by TASK-043 and TASK-044.
- One separately activated JSON/profile/validator/corpus vertical slice is permitted; no renderer, selector, AtlasForge, or runtime migration is authorized.

Boundary assessment:
- BriefForge owns semantic representation and validation architecture planning.
- Implementation requires separate approval.

Threshold status:
- Planning and profile/corpus thresholds satisfied; bounded implementation awaits explicit TASK-045 activation.

---

### DSB-003 — Hand-authored ADPM examples should follow representation-contract planning

Category:
- Example-driven validation

Severity:
- Medium-high

Evidence:
- TASK-036 validated ADPM conceptually against corpora but did not produce serialized packages.
- TASK-037 established lifecycle and ownership.
- TASK-038 found examples are useful, but should be evaluated against a semantic representation contract rather than unconstrained prose.

Recommended improvement:
- Materialize the bounded BCRP 1.0 examples only inside the accepted TASK-045 vertical slice and test them against profile and semantic conformance.

Implementation status:
- Corpus plan accepted by TASK-044; fixture materialization remains unstarted and requires TASK-045 activation.

Boundary assessment:
- Examples must not become canonical runtime format unless separately approved.

Threshold status:
- Design threshold satisfied; materialization is bounded to the future TASK-045 slice.

---

### DSB-004 — Cross-source comparisons should derive from frozen ADPM packages

Category:
- Comparative analysis

Severity:
- Medium-high

Evidence:
- TASK-037 places comparison/aggregation in a read-only derived-view layer.
- TASK-038 confirmed search/index/comparison systems are derived views and must identify source package identity/version.

Recommended improvement:
- Revisit after multiple frozen ADPM packages exist.

Implementation status:
- Deferred.

Boundary assessment:
- BriefForge derived view; source projects remain evidence owners.

Threshold status:
- Evidence supports later work after ADPM representation planning/examples.

---

### DSB-005 — Pattern recurrence and adoption clusters should remain derived views

Category:
- Cross-project synthesis

Severity:
- Medium

Evidence:
- TASK-035 rejected capability/knowledge graphs as canonical semantic objects.
- TASK-036 upheld that rejection.
- TASK-037 places recurrence/adoption maps in future read-only derived-view components.
- TASK-038 confirmed derived views must not become canonical priority or supersession authority.

Recommended improvement:
- Revisit after multiple frozen ADPM packages exist.

Implementation status:
- Deferred.

Boundary assessment:
- BriefForge may present derived maps later; source projects remain evidence owners.

Threshold status:
- Evidence supports later work, not next implementation.

---

### DSB-006 — Long-investigation navigation remains semantic before interactive

Category:
- Navigation / progressive disclosure

Severity:
- Medium

Evidence:
- TASK-037 confirms published artifacts and renderers are expressions, not semantic authority.
- TASK-038 rejected renderer-input-first and Markdown/prose-as-canonical approaches.
- Decision lifecycle, package status, authority, boundary, confidence, priority, horizon, and traceability should reduce reading burden before interactive navigation is considered.

Recommended improvement:
- Test whether lifecycle-aware ADPM packages reduce reading burden before authorizing interactive navigation or renderer features.

Implementation status:
- Deferred.

Boundary assessment:
- BriefForge semantic model first; renderer/UI implementation requires later approval.

Threshold status:
- Evidence supports semantic representation planning, not renderer implementation.

---

### DSB-007 — Defer company and financial-domain semantics to upstream operational evidence

Category:
- Cross-project semantic ownership / deferred compatibility

Severity:
- Deferred; non-blocking for generic BriefForge development

Evidence:
- BriefForge is presentation-only and does not own source-data acquisition, canonicalization, company-data ingestion, or financial-domain analytical meaning.
- No current BriefForge operational evidence justifies canonical company or financial-domain fields in ADPM.

Recommended improvement:
- BriefForge defers canonical semantics for fiscal periods; financial-reporting dates; restatements; corporate actions; currency conversion; company consolidation; security identity; reporting segments; reported-versus-adjusted values; and related company and financial-domain concepts.
- MacroForge should first encounter and define these concepts through operational company and financial-data work.
- After those concepts stabilize upstream, BriefForge should conduct a bounded compatibility review, consume upstream definitions where appropriate, and add only presentation-specific obligations that MacroForge does not own.
- Until then, ADPM may support generic typed external references and bounded extensibility, but it must not contain speculative financial-domain fields.

Implementation status:
- Semantic deferral; no BriefForge runtime dependency on MacroForge and no blocker for generic BriefForge development.

Boundary assessment:
- This deferral does not cover BriefForge-owned publication semantics: publication identity; semantic publication version; evidence-snapshot reference; renderer version; generated-artifact version; publication time; correction; rerender; supersession; withdrawal; and staleness.
- MacroForge remains the prospective upstream semantic owner only after operational evidence stabilizes those concepts; BriefForge remains independently operable.

Threshold status:
- Revisit only after upstream operational company/financial semantics stabilize; do not speculate now.
