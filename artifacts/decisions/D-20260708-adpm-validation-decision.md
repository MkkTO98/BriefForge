# Decision: ADPM Validation and Constitutional Freeze

Date: 2026-07-08
Status: accepted architectural decision; semantic freeze recommended after refinement
Scope: TASK-036 adversarial validation of ADPM

## Decision

BriefForge accepts the TASK-036 adversarial validation result:

1. The original TASK-035 ADPM was not mature enough to freeze unchanged.
2. The adversarial campaign found material semantic gaps.
3. The canonical ADPM specification has been refined at the architectural level.
4. The refined ADPM is now ready for constitutional semantic freeze.
5. No runtime, schema, builder, validator, renderer, template, dashboard, visualization, Presentation Grammar, or generated-project implementation is authorized by this decision.

Canonical refined specification:
- `artifacts/specifications/architectural-decision-package-model.md`

Validation reports:
- `artifacts/reports/R-20260708-adpm-adversarial-validation.md`
- `artifacts/reports/R-20260708-adpm-stability-assessment.md`

## Accepted refinements

### 1. Multi-question package support

Accepted.

Change:
- ArchitecturalDecisionPackage now contains `primary_decision_question_id` and `decision_question_ids`.

Rationale:
- real architectural investigations often contain one primary decision plus coupled sub-decisions;
- forcing a single decision question creates artificial package splits or prose workarounds.

### 2. ADPM versioning

Accepted.

Change:
- ArchitecturalDecisionPackage now requires `adpm_version`.

Rationale:
- TASK-036 changed the semantic contract;
- future packages must declare which ADPM contract they follow.

### 3. Package status refinement

Accepted.

Change:
- `status` becomes `package_status`;
- package states include `draft`, `reviewed`, `validated`, `frozen`, `superseded`, and `rejected`.

Rationale:
- original `accepted` package status risked confusion with recommendation disposition.

### 4. DecisionAuthority

Accepted as first-class ADPM object.

Rationale:
- ProjectForge governance artifacts prove that authority cannot be inferred from confidence, priority, owner, or recommendation wording;
- BriefForge recommendations must not silently claim downstream adoption authority.

### 5. BoundaryConstraint

Accepted as first-class ADPM object.

Rationale:
- real decisions repeatedly depend on explicit non-authorizations, stop conditions, must-preserve boundaries, and out-of-scope declarations;
- these are semantic governance constraints, not presentation warnings.

### 6. PriorityAssessment

Accepted as first-class ADPM object.

Rationale:
- planning horizon separates timing from importance but does not explain priority;
- adoption decisions require expected benefit, cost/complexity, risk of inaction, and dependency readiness.

### 7. Recommendation rationale and expanded completeness

Accepted.

Change:
- Recommendation now includes rationale, authority, boundary constraints, and priority basis in addition to action, evidence, confidence, uncertainty, and traceability.

Rationale:
- without these fields, independent architects would produce inconsistent packages.

## Rejected refinements

### Observation as first-class object

Rejected.

Reason:
- observations remain evidence content unless they affect recommendations;
- promoting observations would increase volume without improving decision completeness.

### Finding as first-class object

Rejected.

Reason:
- findings can be represented as evidence-backed claims or recommendation support;
- a separate Finding object would duplicate EvidenceReference and Recommendation semantics.

### Hypothesis as first-class object

Rejected.

Reason:
- hypotheses can be represented as `investigate`, `defer`, or `reject` recommendations with assumptions, uncertainty, evidence, and open questions;
- InsightForge-specific hypothesis governance should not become ADPM's canonical model.

### Executive summary as semantic object

Rejected.

Reason:
- summaries are presentation expressions of ADPM objects, not canonical semantics.

### Capability map / knowledge graph as canonical ADPM object

Rejected.

Reason:
- maps and graphs are derived aggregate views;
- canonicalizing them now would introduce unnecessary abstraction before package-level semantics are implemented.

### Renderer/navigation fields

Rejected.

Reason:
- ADPM must remain renderer-independent.

## Deferred issues

### Serialization format

Deferred.

Reason:
- this task validates architecture only;
- YAML, JSON, Markdown frontmatter, database records, or other formats require separate planning.

### Validation-rule implementation

Deferred.

Reason:
- validation requirements are specified semantically, but no validator implementation is authorized.

### Package builder design

Deferred.

Reason:
- package builders should follow semantic freeze and serialization planning.

### Renderer consumption

Deferred.

Reason:
- renderers should consume ADPM only after representation/validation strategy is approved.

### Hand-authored example packages

Deferred but recommended.

Reason:
- example packages may help implementation planning, but this task focused on adversarial validation and architecture refinement.

## Constitutional implications

ADPM is now BriefForge's constitutional semantic decision-support layer.

This means BriefForge may define:

- decision package semantics;
- recommendation completeness;
- evidence/provenance linkage requirements;
- confidence and uncertainty structure;
- authority and boundary constraints;
- prioritization basis;
- traceability and compatibility rules.

BriefForge still does not own:

- upstream analytical truth;
- source ingestion;
- downstream adoption decisions;
- implementation authority in consumer projects;
- runtime behavior;
- renderer behavior;
- schemas/builders/validators until separately approved;
- dashboards/UI/templates/visualization engines.

## Freeze recommendation

Recommendation: freeze the refined ADPM semantic ontology.

Freeze applies to:

- object set;
- required relationships;
- completeness invariants;
- authority/boundary doctrine;
- extension rules.

Freeze does not apply to:

- serialization;
- validation implementation;
- package-builder behavior;
- renderer integration;
- output templates;
- examples;
- dashboards/UI.

## Expected downstream impact

### BriefForge

BriefForge gains a stable semantic target for future decision-support capabilities.

Next work should be planning-only:
- `TASK-037 ADPM Serialization and Validation Planning`, or
- hand-authored ADPM examples as a no-schema validation aid.

### Evidence-producing projects

Evidence producers remain responsible for evidence correctness and domain interpretation.

ADPM only packages evidence references and decision semantics.

### Consumer projects

Consumer projects gain better inputs:

- what is recommended;
- who has authority;
- what is not authorized;
- how important it is;
- what evidence supports or limits it;
- what uncertainty remains;
- what happens if no action is taken.

They retain adoption sovereignty.

## Non-authorizations

This decision does not authorize:

- schema implementation;
- package-builder implementation;
- validator implementation;
- renderer implementation;
- HTML, dashboards, charts, templates, UI, visualization engines;
- Presentation Grammar changes;
- runtime behavior changes;
- generated-project modifications;
- upstream project modifications.

## Next recommended workstream

`TASK-037 ADPM Serialization and Validation Planning`

Purpose:
- decide the smallest implementation-adjacent representation and validation plan for ADPM while preserving renderer/runtime independence.

Non-goals:
- no implementation;
- no schema files unless explicitly approved in that task;
- no renderer integration;
- no generated-project changes.
