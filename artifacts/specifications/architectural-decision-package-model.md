# Architectural Decision Package Model Specification

Date: 2026-07-08
Status: canonical semantic specification after TASK-036 adversarial refinement and TASK-037 lifecycle integration
Owner: BriefForge
Scope: renderer-independent architectural decision-support packages

## 1. Purpose

The Architectural Decision Package Model (ADPM) defines the canonical semantic structure BriefForge uses to package architectural investigations into decision-ready objects.

ADPM exists to answer one question:

> What is the smallest complete package of information required for an architect to make a high-confidence architectural adoption decision without reading an entire investigation?

ADPM is not a renderer model, UI model, dashboard model, template model, graph model, or runtime model.

## 2. Boundary

### 2.1 In scope

ADPM defines:

- semantic objects;
- required relationships;
- required fields;
- completeness invariants;
- extension rules;
- validation requirements;
- compatibility expectations.

### 2.2 Out of scope

ADPM does not define:

- HTML;
- CSS;
- JavaScript;
- dashboards;
- charts;
- maps;
- visualizations;
- graph layouts;
- templates;
- browser behavior;
- interactive navigation;
- runtime execution;
- storage;
- APIs;
- source ingestion;
- consumer-project implementation.

## 3. Design principles

1. Decision quality over presentation polish.
2. Semantic completeness over prose fluency.
3. Auditability over compression alone.
4. Evidence ownership preservation.
5. Renderer independence.
6. Project independence.
7. Minimality: no object or field is canonical unless it improves architectural decision-making.
8. Consumer sovereignty: package recommendations do not execute work or override project owners.

## 3A. Lifecycle and ownership semantics

ADPM has a governed architectural lifecycle:

```text
Investigation Evidence
-> Decision Need Identification
-> Package Construction
-> Semantic Review
-> Architectural Approval
-> Constitutional Freeze
-> Consumption Boundary
-> Publication Expression
-> Operational Reference
-> Archival / Supersession
```

Lifecycle states are represented by `package_status` and are distinct from recommendation `disposition`.

Canonical lifecycle states:
- `draft`
- `under_review`
- `approved`
- `frozen`
- `deprecated`
- `superseded`
- `archived`
- `rejected`

Allowed normal transitions:
- `draft -> under_review`
- `under_review -> draft`
- `under_review -> approved`
- `under_review -> rejected`
- `approved -> frozen`
- `frozen -> deprecated`
- `frozen -> superseded`
- `frozen -> archived`
- `deprecated -> archived`
- `superseded -> archived`
- `rejected -> archived`

Prohibited transitions:
- `frozen -> draft`
- `frozen -> under_review`
- `frozen -> approved`
- `superseded -> draft`
- `archived -> draft`
- `archived -> frozen`
- `rejected -> frozen`

Ownership rules:
- source evidence owners own evidence correctness;
- package authors/builders may construct draft packages but may not approve or freeze them;
- semantic reviewers/validators may emit findings but may not infer recommendations or approve packages;
- BriefForge constitutional governance owns approval, freeze, rejection, deprecation, supersession, and archival transitions;
- serializers transport ADPM semantics but do not define them;
- renderers consume frozen ADPM packages read-only and do not modify semantics;
- search, indexing, comparison, and aggregation produce derived views and do not modify canonical packages;
- consumer projects own local adoption decisions and implementation, not canonical BriefForge package mutation.

Package relationship values are limited to:
- `supersedes`
- `superseded_by`
- `references`
- `derives_from`
- `amends`
- `amended_by`
- `related_to`

Lifecycle invariants:
- frozen packages are immutable;
- post-freeze corrections require a separate amendment or supersession relationship;
- package lineage must remain traceable;
- published outputs are expressions, not semantic authority;
- no component gains governance authority merely by consuming a package.

## 4. Core semantic objects

### 4.1 ArchitecturalDecisionPackage

Definition:
- the bounded semantic container for one decision-support package.

Required fields:
- `package_id`
- `adpm_version`
- `title`
- `primary_decision_question_id`
- `decision_question_ids`
- `purpose`
- `scope`
- `non_scope`
- `recommendation_ids`
- `decision_authority_ids`
- `boundary_constraint_ids`
- `evidence_reference_ids`
- `source_provenance_ids`
- `created_at`
- `package_status`
- `traceability_links`

Allowed `package_status` values:
- `draft`
- `under_review`
- `approved`
- `frozen`
- `deprecated`
- `superseded`
- `archived`
- `rejected`

Invariants:
- must contain at least one DecisionQuestion;
- must identify exactly one primary DecisionQuestion for package entry;
- may contain multiple DecisionQuestions when a corpus naturally contains coupled sub-decisions;
- must contain at least one Recommendation unless `package_status` is `rejected` with rationale;
- must preserve source provenance for all evidence references;
- must declare decision authority and boundary constraints for recommendations that could be mistaken for implementation authorization;
- must not contain renderer instructions.

### 4.2 DecisionQuestion

Definition:
- the architectural question the package helps answer.

Required fields:
- `decision_question_id`
- `question`
- `decision_type`
- `affected_scope`
- `why_now`

Allowed `decision_type` values:
- `adoption`
- `adaptation`
- `rejection`
- `deferral`
- `investigation`
- `supersession`
- `monitoring`

Invariants:
- must be answerable by the package's recommendations;
- must not be a broad research topic without a decision boundary.

### 4.3 Recommendation

Definition:
- an actionable architectural proposal or non-action proposal inside a package.

Required fields:
- `recommendation_id`
- `title`
- `decision_question_ids`
- `disposition`
- `planning_horizon`
- `priority_assessment_id`
- `recommended_action`
- `rationale`
- `why_now`
- `owner_scope`
- `decision_authority_id`
- `affected_projects_or_domains`
- `boundary_constraint_ids`
- `evidence_for_ids`
- `evidence_against_or_limiting_ids`
- `confidence_assessment_id`
- `uncertainty_ids`
- `assumption_ids`
- `risk_ids`
- `alternative_ids`
- `consequence_ids`
- `dependency_ids`
- `impact_ids`
- `follow_up_action_ids`
- `open_question_ids`
- `traceability_links`

Allowed `disposition` values:
- `adopt`
- `adapt`
- `investigate`
- `defer`
- `reject`
- `monitor`
- `supersede`

Allowed `planning_horizon` values:
- `immediate_architectural_blocker`
- `immediate_high_value_capability`
- `near_term_improvement`
- `medium_term_capability`
- `long_term_research`
- `deferred_investigation`
- `rejected`
- `superseded`

Invariants:
- must answer at least one associated DecisionQuestion;
- may answer multiple DecisionQuestions only when the coupling is explicit and traceable;
- must include supporting evidence or explicitly state that supporting evidence is absent;
- must include limiting/opposing evidence or explicitly state that none is known;
- must include no-action consequence;
- must include confidence rationale;
- must include priority rationale;
- must include decision authority and authorization boundary;
- must include traceability;
- must not create an implementation task by itself.

### 4.4 DecisionAuthority

Definition:
- the governance/ownership authority that may accept, reject, defer, or execute a recommendation.

Required fields:
- `decision_authority_id`
- `authority_owner`
- `authority_scope`
- `permission_level`
- `approval_required`
- `authority_notes`

Allowed `permission_level` values:
- `routine`
- `architectural`
- `strategic`
- `foundational`
- `external_or_unknown`

Invariants:
- decision authority must not be inferred from confidence or priority;
- a recommendation may advise a project but cannot claim adoption authority over that project;
- unknown authority must be explicit.

### 4.5 BoundaryConstraint

Definition:
- an explicit statement of what a package or recommendation authorizes, does not authorize, or must preserve.

Required fields:
- `boundary_constraint_id`
- `constraint_type`
- `description`
- `affected_scope`
- `rationale`

Allowed `constraint_type` values:
- `in_scope`
- `out_of_scope`
- `non_authorization`
- `must_preserve`
- `stop_condition`

Invariants:
- implementation, renderer, ingestion, generated-project, or consumer-project boundaries must be stated as BoundaryConstraints when relevant;
- BoundaryConstraints are semantic governance constraints, not UI warnings.

### 4.6 PriorityAssessment

Definition:
- the decision-weighting basis that explains recommendation ordering or non-ordering.

Required fields:
- `priority_assessment_id`
- `priority_level`
- `priority_rationale`
- `expected_benefit`
- `complexity_or_cost`
- `risk_of_inaction`
- `dependency_readiness`

Allowed `priority_level` values:
- `critical`
- `high`
- `medium`
- `low`
- `none`
- `unknown`

Invariants:
- priority is not authority;
- priority must not be derived from planning horizon alone;
- `unknown` priority must explain what evidence is missing.

### 4.7 EvidenceReference

Definition:
- a reference to upstream-owned evidence used by a package or recommendation.

Required fields:
- `evidence_reference_id`
- `source_provenance_id`
- `evidence_role`
- `summary`
- `locator`
- `evidence_mode`
- `strength`
- `limitations`

Allowed `evidence_role` values:
- `supports`
- `opposes`
- `qualifies`
- `background`
- `missing`

Allowed `evidence_mode` values:
- `source_code`
- `documentation`
- `specification`
- `example_or_specimen`
- `test_or_execution`
- `report`
- `decision_record`
- `human_review`
- `mixed`
- `unknown`

Allowed `strength` values:
- `strong`
- `medium`
- `weak`
- `missing`

Invariants:
- must preserve upstream ownership;
- must not convert evidence into BriefForge-owned analytical truth;
- must identify limitations when evidence is not source-code/execution-backed.

### 4.8 SourceProvenance

Definition:
- origin metadata for evidence.

Required fields:
- `source_provenance_id`
- `source_name`
- `source_type`
- `source_locator`
- `review_state`
- `freshness_or_date`
- `owner_or_origin`

Allowed `source_type` values:
- `repository`
- `project_artifact`
- `report`
- `specification`
- `documentation`
- `dataset`
- `human_review`
- `generated_artifact`
- `other`

Invariants:
- must be sufficient for audit follow-up;
- must not imply BriefForge ownership of the source.

### 4.9 ConfidenceAssessment

Definition:
- assessment of recommendation confidence and its rationale.

Required fields:
- `confidence_assessment_id`
- `level`
- `rationale`
- `evidence_mode_summary`
- `evidence_diversity`
- `confidence_reducers`
- `confidence_improvers`

Allowed `level` values:
- `high`
- `medium_high`
- `medium`
- `medium_low`
- `low`
- `unknown`

Invariants:
- must distinguish evidence strength from decision urgency;
- must not omit confidence reducers;
- must identify what would increase confidence.

### 4.10 Uncertainty

Definition:
- unresolved unknown that affects interpretation or action.

Required fields:
- `uncertainty_id`
- `description`
- `classification`
- `affected_recommendation_ids`
- `resolution_path`

Allowed `classification` values:
- `blocker`
- `material_non_blocking`
- `monitoring_required`
- `acceptable_residual`
- `missing_evidence`

Invariants:
- blocker uncertainty must prevent `adopt` disposition unless explicitly justified;
- every material uncertainty must have a resolution or monitoring path.

### 4.11 Assumption

Definition:
- a proposition the recommendation depends on but has not fully proven.

Required fields:
- `assumption_id`
- `statement`
- `basis`
- `risk_if_false`
- `validation_path`

Invariants:
- assumptions must not be hidden inside confidence rationale only.

### 4.12 Risk

Definition:
- possible negative outcome related to accepting, rejecting, or delaying a recommendation.

Required fields:
- `risk_id`
- `description`
- `risk_type`
- `likelihood`
- `impact`
- `mitigation_or_monitoring`

Allowed `risk_type` values:
- `acceptance_risk`
- `delay_risk`
- `rejection_risk`
- `implementation_risk`
- `governance_risk`
- `evidence_risk`

Allowed likelihood/impact values:
- `high`
- `medium`
- `low`
- `unknown`

Invariants:
- at least one risk or an explicit `none identified` entry must exist per recommendation.

### 4.13 Alternative

Definition:
- plausible competing choice considered by the recommendation.

Required fields:
- `alternative_id`
- `description`
- `reason_not_selected`
- `conditions_for_reconsideration`

Invariants:
- rejected alternatives must be traceable enough to prevent repeated reconsideration without new evidence.

### 4.14 Consequence

Definition:
- expected result of accepting, rejecting, delaying, or doing nothing.

Required fields:
- `consequence_id`
- `consequence_type`
- `description`
- `affected_scope`

Allowed `consequence_type` values:
- `if_accepted`
- `if_rejected`
- `if_deferred`
- `if_no_action`

Invariants:
- every recommendation must include an `if_no_action` consequence.

### 4.15 Dependency

Definition:
- prerequisite or coupled condition for a recommendation.

Required fields:
- `dependency_id`
- `description`
- `dependency_type`
- `status`
- `owner_scope`

Allowed `dependency_type` values:
- `evidence`
- `architecture`
- `implementation`
- `governance`
- `project_boundary`
- `operational`

Allowed `status` values:
- `satisfied`
- `unsatisfied`
- `unknown`
- `not_required`

Invariants:
- unsatisfied dependencies must influence horizon or confidence.

### 4.16 Impact

Definition:
- downstream effect of a recommendation.

Required fields:
- `impact_id`
- `impact_type`
- `affected_scope`
- `description`
- `severity`

Allowed `impact_type` values:
- `architectural`
- `implementation`
- `operational`
- `validation`
- `governance`
- `downstream_project`

Allowed `severity` values:
- `high`
- `medium`
- `low`
- `informational`

Invariants:
- implementation impact does not authorize implementation.

### 4.17 FollowUpAction

Definition:
- bounded next action that increases confidence, resolves uncertainty, or moves an accepted recommendation toward adoption.

Required fields:
- `follow_up_action_id`
- `description`
- `purpose`
- `owner_scope`
- `trigger`
- `non_goals`

Invariants:
- follow-up actions are not tasks unless separately adopted by the owner.

### 4.18 OpenQuestion

Definition:
- unresolved question remaining after package creation.

Required fields:
- `open_question_id`
- `question`
- `why_it_matters`
- `blocking_status`
- `resolution_path`

Allowed `blocking_status` values:
- `blocking`
- `non_blocking`
- `monitor`

### 4.19 TraceabilityLink

Definition:
- explicit link connecting ADPM objects to evidence, decisions, reports, source artifacts, or follow-up records.

Required fields:
- `traceability_link_id`
- `from_object_id`
- `to_target`
- `relationship`

Allowed `relationship` values:
- `supported_by`
- `limited_by`
- `derived_from`
- `supersedes`
- `superseded_by`
- `depends_on`
- `affects`
- `audits_to`

Invariants:
- every Recommendation must have at least one traceability link;
- every EvidenceReference must trace to SourceProvenance.

## 5. Mandatory relationships

1. ArchitecturalDecisionPackage -> one or more DecisionQuestions.
2. ArchitecturalDecisionPackage -> exactly one primary DecisionQuestion for package entry.
3. ArchitecturalDecisionPackage -> one or more Recommendations unless explicitly rejected.
4. Recommendation -> one or more DecisionQuestions.
5. Recommendation -> one ConfidenceAssessment.
6. Recommendation -> one PriorityAssessment.
7. Recommendation -> one DecisionAuthority.
8. Recommendation -> zero or more BoundaryConstraints, with explicit constraints required when the recommendation could imply implementation, renderer, ingestion, generated-project, or consumer-project authority.
9. Recommendation -> zero or more EvidenceReferences, but absence of evidence must be explicit.
10. EvidenceReference -> one SourceProvenance.
11. Recommendation -> zero or more Uncertainties, Assumptions, Risks, Alternatives, Consequences, Dependencies, Impacts, FollowUpActions, and OpenQuestions.
12. Recommendation -> at least one Consequence with `if_no_action` type.
13. Recommendation -> at least one TraceabilityLink.
14. All source-derived claims -> SourceProvenance through EvidenceReference.

## 6. Completeness rules

A Recommendation is complete only if:

1. it states what decision is being proposed;
2. it states why now;
3. it identifies affected owner/scope;
4. it declares decision authority and approval boundary;
5. it declares disposition;
6. it declares planning horizon;
7. it declares priority basis, expected benefit, complexity/cost, and risk of inaction;
8. it states the recommended action and rationale;
9. it links supporting evidence or explicitly records missing evidence;
10. it links opposing/limiting evidence or explicitly records none known;
11. it includes confidence level and rationale;
12. it records uncertainty and blocking status;
13. it records assumptions or `none identified`;
14. it records risks or `none identified`;
15. it records alternatives or `none identified`;
16. it records consequences including no-action consequence;
17. it records dependencies or `none identified`;
18. it records impacts;
19. it records boundary constraints/non-authorizations when relevant;
20. it records follow-up/confidence-improvement path;
21. it traces to source provenance.

A Package is complete only if:

1. every Recommendation is complete;
2. package scope and non-scope are explicit;
3. package ADPM version is explicit;
4. source provenance is preserved;
5. decision authority and boundary constraints are recorded where relevant;
6. no renderer assumptions appear;
7. no follow-up action is represented as already approved implementation.

## 7. Extension rules

Extensions may add optional fields or derived objects only if they satisfy all rules below:

1. They improve architectural decision-making.
2. They do not encode renderer, UI, dashboard, chart, or template assumptions.
3. They preserve upstream evidence ownership.
4. They do not make BriefForge the owner of consumer-project adoption decisions.
5. They can be ignored by a consumer without invalidating the core package.
6. They do not weaken mandatory completeness rules.
7. They must be documented with purpose, scope, and compatibility expectations.

Forbidden extensions:

- visual layout hints;
- CSS or HTML classes;
- interactive behavior flags;
- dashboard widget definitions;
- graph layout instructions;
- template slots;
- consumer-project task execution state.

## 8. Validation requirements

A future ADPM validator must check at minimum:

1. required object presence;
2. required field presence;
3. allowed enum values;
4. relationship integrity;
5. recommendation completeness;
6. package completeness;
7. source provenance linkage;
8. ADPM version declaration;
9. decision authority declaration;
10. boundary/non-authorization declaration;
11. priority basis completeness;
12. no renderer assumptions;
13. no implementation authorization leakage;
14. no upstream evidence ownership violation;
15. no consumer-project adoption authority leakage.

Planning-horizon validation:
- `rejected` disposition should normally use `rejected` horizon;
- `supersede` disposition should normally use `superseded` horizon;
- blocker uncertainty should prevent immediate adopt/adapt disposition unless explicitly justified;
- unsatisfied dependencies should reduce horizon readiness or confidence.

## 9. Future compatibility expectations

ADPM must remain stable across:

- different upstream evidence producers;
- different consuming projects;
- different renderer technologies;
- different output media;
- different architectural domains;
- future aggregation/indexing systems.

Future renderers may consume ADPM but must not redefine ADPM semantics.

Future schemas may serialize ADPM in YAML, JSON, Markdown frontmatter, database records, or other formats. Serialization is not canonical; semantics are canonical.

Future aggregate views may derive:

- recommendation indexes;
- owner-specific decision queues;
- capability maps;
- pattern recurrence maps;
- uncertainty registers;
- dependency maps.

These are derived views, not replacements for the package model.

## 10. Minimal valid package checklist

A minimal valid ADPM package contains:

- one ArchitecturalDecisionPackage with explicit `adpm_version`;
- at least one DecisionQuestion and exactly one primary DecisionQuestion;
- at least one Recommendation;
- one DecisionAuthority where adoption/execution authority matters;
- BoundaryConstraints for relevant scope, non-authorization, preservation, and stop-condition limits;
- one PriorityAssessment per recommendation;
- at least one EvidenceReference or explicit missing-evidence record;
- SourceProvenance for every evidence reference;
- one ConfidenceAssessment per recommendation;
- uncertainty, assumption, risk, alternative, consequence, dependency, impact, follow-up, and open-question records where applicable, with explicit `none identified` records where required;
- traceability links sufficient for audit.

## 11. Governance note

ADPM acceptance does not authorize runtime implementation, renderer integration, schema implementation, or generated-project modification.

Any future implementation requires a separate approved task.
