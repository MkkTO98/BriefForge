# ADPM Stability Assessment

Date: 2026-07-08
Status: decision gate assessment
Scope: TASK-036 — determine whether ADPM is ready for constitutional semantic freeze

## Decision-gate answer

ADPM was not ready to freeze in its original TASK-035 form.

The adversarial validation found material semantic gaps: authority, boundary constraints/non-authorizations, priority basis, model versioning, and support for multiple coupled decision questions.

After applying the minimum architectural refinements to the canonical specification, ADPM is ready for constitutional semantic freeze.

This freeze should be understood narrowly:

- freeze the semantic ontology and core completeness rules;
- do not freeze any schema, serialization, builder, validator, renderer, template, dashboard, or runtime implementation;
- require separate approval for implementation.

## Which semantic objects remained invariant across every validation?

The following TASK-035 objects remained valid and necessary across the corpus:

### ArchitecturalDecisionPackage

Invariant role:
- bounded semantic container.

Validation evidence:
- every corpus artifact needed a package boundary: MetaHarvest campaign, ProjectForge methodology freeze, MacroForge capability planning, BriefForge usability review, InsightForge hypothesis pressure test, and KnowledgeForge validator hardening.

Refinement:
- package now supports one primary decision question plus multiple coupled decision questions;
- package now requires `adpm_version` and `package_status`.

### DecisionQuestion

Invariant role:
- defines what the package helps decide.

Validation evidence:
- artifacts without explicit decision questions required manual interpretation;
- ProjectForge and MacroForge artifacts were easiest to map when their review/decision question was explicit.

Refinement:
- no longer limited to exactly one per package.

### Recommendation

Invariant role:
- central operational decision proposal.

Validation evidence:
- all meaningful corpus artifacts contained either positive recommendations, negative recommendations, deferrals, monitoring recommendations, or rejection recommendations.

Refinement:
- recommendations now include rationale, priority assessment, authority, and boundary constraints.

### EvidenceReference

Invariant role:
- connects recommendations to supporting, opposing, qualifying, background, or missing evidence.

Validation evidence:
- documentation-first MetaHarvest evidence, ProjectForge reports, MacroForge task evidence, and InsightForge findings all required role-specific evidence linkage.

### SourceProvenance

Invariant role:
- preserves source origin and auditability.

Validation evidence:
- upstream ownership was central in every project family.

### ConfidenceAssessment

Invariant role:
- expresses confidence without hiding evidence limitations.

Validation evidence:
- MetaHarvest documentation-first evidence, InsightForge rejected hypotheses, and MacroForge bounded planning all required explicit confidence framing.

### Uncertainty

Invariant role:
- records unknowns and blocking status.

Validation evidence:
- MetaHarvest blind spots, InsightForge missing evidence, and MacroForge preflight stop conditions all needed uncertainty semantics.

### Assumption

Invariant role:
- records conditionally accepted premises.

Validation evidence:
- InsightForge hypotheses and MacroForge planning depended on explicit assumptions.

### Risk

Invariant role:
- records possible negative outcomes.

Validation evidence:
- ProjectForge sovereignty leakage, MacroForge mirror asymmetry, and BriefForge renderer drift risks needed risk semantics.

### Alternative

Invariant role:
- records considered/rejected options.

Validation evidence:
- MacroForge ACPF and ProjectForge methodology freeze contained many alternatives that must remain discoverable.

### Consequence

Invariant role:
- records expected outcomes, including no action.

Validation evidence:
- ProjectForge governance, MacroForge bounded planning, and BriefForge next-evolution choices all required action/no-action consequences.

### Dependency

Invariant role:
- records prerequisites and sequencing constraints.

Validation evidence:
- MacroForge capability planning depended heavily on prerequisite source evidence and boundary readiness.

### Impact

Invariant role:
- records affected architectural, implementation, operational, validation, governance, or downstream project surfaces.

Validation evidence:
- every cross-project case required impact classification.

### Follow-up Action

Invariant role:
- records bounded next action or confidence-improvement path.

Validation evidence:
- MetaHarvest blind spots, MacroForge next slice recommendations, and BriefForge next workstreams all required follow-up semantics.

### OpenQuestion

Invariant role:
- records unresolved questions.

Validation evidence:
- InsightForge hypotheses, MetaHarvest blind spots, and MacroForge preflight questions required unresolved-question semantics.

### TraceabilityLink

Invariant role:
- preserves audit connections.

Validation evidence:
- essential across all project families.

### PlanningHorizon

Invariant role:
- separates timing from importance.

Validation evidence:
- ProjectForge deferrals, MacroForge immediate next tasks, BriefForge later renderer work, and InsightForge rejected hypotheses all needed horizon classification.

## Which objects were ambiguous?

### Assumption vs Uncertainty

Ambiguity:
- an unproven premise can look like both.

Resolution:
- assumption = conditionally accepted proposition;
- uncertainty = unknown with blocking/monitoring status.

Status:
- clarified, not merged.

### Risk vs Consequence

Ambiguity:
- both describe future negative outcomes.

Resolution:
- risk = possible outcome with likelihood/impact/mitigation;
- consequence = expected result under action path.

Status:
- clarified, not merged.

### Impact vs Consequence

Ambiguity:
- both describe effects.

Resolution:
- impact = affected surface;
- consequence = decision outcome.

Status:
- clarified, not merged.

### Follow-up Action vs Open Question

Ambiguity:
- every open question may imply a follow-up action.

Resolution:
- open question states the unresolved issue;
- follow-up action states the bounded action that may resolve it.

Status:
- clarified, not merged.

### Package status vs recommendation disposition

Ambiguity:
- original `accepted` package status could be confused with accepted recommendation disposition.

Resolution:
- field renamed to `package_status`;
- package states now include `validated` and `frozen` rather than ambiguous `accepted`.

Status:
- refined.

## Which objects required refinement?

### ArchitecturalDecisionPackage

Refinements:
- added `adpm_version`;
- changed `decision_question_id` to `primary_decision_question_id` plus `decision_question_ids`;
- changed `status` to `package_status`;
- added decision authority and boundary constraint relationships.

Reason:
- real packages may contain coupled sub-decisions;
- versioning is needed after ontology changes;
- package status must not be confused with recommendation disposition.

### Recommendation

Refinements:
- `decision_question_id` became `decision_question_ids`;
- added `rationale`;
- added `priority_assessment_id`;
- added `decision_authority_id`;
- added `boundary_constraint_ids`.

Reason:
- significant recommendations require authority, boundary, rationale, and priority basis.

### Mandatory relationships and completeness rules

Refinements:
- added DecisionAuthority, BoundaryConstraint, PriorityAssessment relationships;
- added authority, non-authorization, priority basis, version, and multi-question completeness requirements.

Reason:
- future validators/builders need these semantics if implemented later.

## Which objects were removed or merged?

No TASK-035 object was removed or merged.

The adversarial review found adjacent concepts, but none were redundant enough to remove without losing decision quality.

Objects not promoted to first-class status:

- Observation;
- Finding;
- Hypothesis;
- Executive Summary;
- Capability Map;
- Knowledge Graph;
- Visualization;
- Navigation Path.

These remain evidence content, recommendation forms, presentation expressions, or derived views.

## Which architectural assumptions survived?

### ADPM should be renderer-independent

Survived.

No corpus case required HTML, dashboards, UI, charts, templates, graph layouts, or interaction semantics.

### ADPM should be implementation-independent

Survived after BoundaryConstraint refinement.

Implementation non-authorizations are now semantic boundary constraints, not implementation behavior.

### Evidence and source provenance must be separate

Survived.

Every corpus family required both origin metadata and role-specific evidence use.

### Recommendations require evidence for and limiting evidence

Survived.

The strongest adversarial cases were rejected hypotheses and non-materialized documentation-first investigations.

### Confidence must remain separate from uncertainty

Survived.

Several recommendations had useful confidence in one dimension while retaining material uncertainty in another.

### Planning horizon belongs in the canonical model

Survived.

Rejected, deferred, immediate, and long-term recommendations all appeared in the corpus.

### BriefForge should not own consumer-project adoption

Survived.

DecisionAuthority strengthens this assumption.

## Which assumptions failed?

### Failed assumption 1: one package can be constrained to exactly one decision question

Failed.

Real architectural investigations often contain one primary decision plus sub-decisions.

Correction:
- one primary question plus multiple decision questions.

### Failed assumption 2: owner/scope is enough for adoption authority

Failed.

Authority must be explicit.

Correction:
- DecisionAuthority.

### Failed assumption 3: package/recommendation scope is enough to represent non-authorizations

Failed.

Non-authorizations and stop conditions are central decision semantics.

Correction:
- BoundaryConstraint.

### Failed assumption 4: planning horizon is enough for prioritization

Failed.

Priority requires expected benefit, cost/complexity, risk of inaction, and dependency readiness.

Correction:
- PriorityAssessment.

### Failed assumption 5: package status does not need versioned semantics

Failed.

TASK-036 changed ADPM itself.

Correction:
- `adpm_version` and refined `package_status`.

## Is ADPM ready to become a frozen constitutional model?

Yes, after TASK-036 refinements.

The original TASK-035 model should not be frozen as-is.

The refined model is ready for constitutional semantic freeze because:

- all selected corpus decisions can be represented;
- no project-specific semantic object is required;
- no renderer/UI/runtime/schema assumption is introduced;
- no existing object was proven removable;
- newly added objects directly correspond to repeated real decision pressure;
- object boundaries are sufficiently clear for future validation design.

## What evidence prevents freezing?

No evidence prevents freezing the refined semantic model.

Evidence does prevent the following:

- freezing a serialization format;
- implementing schema/validation directly without planning;
- building package builders;
- integrating renderers;
- creating dashboards/templates/UI;
- treating ADPM recommendations as implementation authority.

## Freeze recommendation

Freeze ADPM as a constitutional semantic model at the refined TASK-036 level.

Freeze scope:
- semantic objects;
- mandatory relationships;
- completeness requirements;
- extension rules;
- boundary/non-authority doctrine.

Do not freeze:
- storage format;
- schemas;
- CLI tools;
- builders;
- validators;
- renderers;
- presentation templates;
- examples as canonical implementation.

## Next recommended workstream

`TASK-037 ADPM Serialization and Validation Planning`

Purpose:
- determine the smallest non-runtime representation and validation plan for ADPM without implementing it.

Alternative valid next step:
- hand-author two or three example ADPM packages from existing investigations as a no-schema exercise.

Recommendation:
- choose planning before implementation; avoid schema-first lock-in.
