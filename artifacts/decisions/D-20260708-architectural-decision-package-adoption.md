# Decision: Architectural Decision Package Adoption

Date: 2026-07-08
Status: Accepted architectural decision; no runtime implementation authorized
Scope: BriefForge semantic decision-support architecture

## Decision

BriefForge accepts the Architectural Decision Package Model (ADPM) as the canonical renderer-independent semantic model for architectural decision-support packages.

ADPM defines the minimum complete package of information required for an architect to make a high-confidence architectural adoption decision without reading an entire investigation first.

The accepted model is documented in:

- `artifacts/specifications/architectural-decision-package-model.md`
- `artifacts/reports/R-20260708-architectural-decision-package-model.md`

## Accepted concepts

### 1. Architectural Decision Package

Accepted as the bounded semantic container for decision-support material.

Rationale:
- current reports are coherent but require manual decision extraction;
- a package-level semantic object makes the decision question, recommendations, confidence, uncertainty, and traceability explicit.

### 2. Decision Question

Accepted as mandatory.

Rationale:
- without an explicit decision question, a package can only be a report;
- decision-support must clarify what the reader is deciding.

### 3. Recommendation as central operational object

Accepted as mandatory.

Rationale:
- recommendations are where evidence becomes architectural action guidance;
- prose recommendations are not complete enough for governance use.

### 4. Decision Disposition

Accepted.

Canonical dispositions:
- adopt;
- adapt;
- investigate;
- defer;
- reject;
- monitor;
- supersede.

Rationale:
- architectural decisions need more than positive recommendations;
- rejection, deferral, monitoring, and supersession are first-class governance outcomes.

### 5. Planning Horizon

Accepted.

Canonical horizons:
- immediate architectural blocker;
- immediate high-value capability;
- near-term improvement;
- medium-term capability;
- long-term research;
- deferred investigation;
- rejected;
- superseded.

Rationale:
- horizon separates importance from timing;
- backlog priority needs a semantic input but remains owned by the consuming project.

### 6. Evidence roles

Accepted.

Evidence may support, oppose, qualify, provide background, or be missing.

Rationale:
- decision confidence depends on counterevidence and missing evidence as much as positive support.

### 7. Confidence and uncertainty separation

Accepted.

Rationale:
- a recommendation can have meaningful confidence while still carrying blockers;
- uncertainty must be visible as blocker, material non-blocker, monitoring requirement, acceptable residual uncertainty, or missing evidence.

### 8. Assumptions, risks, alternatives, consequences, and dependencies

Accepted as required recommendation completeness fields.

Rationale:
- these concepts are required to evaluate tradeoffs, no-action cost, and implementation readiness.

### 9. Impact and ownership mapping

Accepted.

Rationale:
- downstream projects must know whether a recommendation affects architecture, implementation, operations, validation, governance, or another project boundary.

### 10. Follow-up actions and open questions

Accepted.

Rationale:
- decision packages must indicate what would increase confidence or move the recommendation forward;
- follow-up actions are not implementation tasks unless separately accepted.

### 11. Traceability and source provenance

Accepted as mandatory.

Rationale:
- ADPM reduces first-pass reading, but auditability must remain intact;
- BriefForge preserves upstream evidence ownership rather than claiming analytical truth.

## Rejected concepts

### Renderer assumptions

Rejected from ADPM.

Examples:
- HTML layout;
- expandable sections;
- dashboards;
- charts;
- graph visualization;
- CSS classes;
- interactive navigation;
- templates.

Rationale:
- ADPM is a semantic model;
- renderers must consume ADPM, not shape it.

### Executive summary as first-class semantic object

Rejected.

Rationale:
- executive summaries are presentation expressions of decision objects;
- the semantic objects are decision question, recommendation, evidence, confidence, uncertainty, impacts, and traceability.

### Observation and finding as first-class ADPM objects

Rejected as mandatory first-class objects.

Rationale:
- observations belong as evidence unless they drive a recommendation;
- findings can be represented as evidence-backed claims inside packages or recommendations;
- adding more top-level objects would increase complexity without improving decision completeness.

### Capability graph / knowledge graph as canonical model

Rejected for this phase.

Rationale:
- current evidence requires decision completeness before graph abstraction;
- graph or map forms can be derived later from ADPM objects.

### Project-specific package variants

Rejected.

Rationale:
- the model must apply across current and future EIP projects;
- source-specific variants belong in adapters or upstream evidence contracts, not the canonical BriefForge model.

## Deferred concepts

### Aggregated capability maps

Deferred.

Reason:
- likely useful across many packages, but should derive from stable ADPM fields after package-level validation.

### Cross-package recommendation indexes

Deferred.

Reason:
- useful after multiple ADPM packages exist;
- not necessary to define the minimal complete package.

### Interactive filtering and navigation

Deferred.

Reason:
- may improve future use, but only after semantic fields prove stable.

### Machine-readable schema implementation

Deferred.

Reason:
- this task defines architecture only;
- schema/validation implementation requires separate approval.

### Renderer integration

Deferred.

Reason:
- rendering must wait until ADPM semantics are manually validated.

## Constitutional implications

ADPM establishes BriefForge's next constitutional semantic direction: decision-support packaging.

This is an extension of BriefForge's existing responsibility for structured semantic presentation, not a transfer of upstream analytical authority.

BriefForge may define and validate decision-support package semantics.

BriefForge still does not own:

- upstream evidence extraction;
- economic or analytical truth;
- source-specific interpretation;
- consumer-project adoption decisions;
- implementation planning authority for other projects;
- rendering behavior;
- dashboards;
- UI interaction;
- templates;
- runtime execution.

## Expected downstream impact

### BriefForge

BriefForge gains a stable semantic target for future decision-support outputs.

Likely future work:
- manual ADPM validation against representative investigation corpora;
- ADPM validation rules;
- package-builder design;
- renderer consumption only after semantic validation.

### Evidence-producing projects

Evidence-producing projects may later expose fields that map cleanly into ADPM, but they remain owners of evidence correctness and domain interpretation.

### Consumer projects

Consumer projects receive clearer adoption inputs:
- recommendation;
- horizon;
- confidence;
- uncertainty;
- impact;
- dependencies;
- follow-up.

They retain authority to accept, modify, reject, or ignore recommendations.

## Decision consequences

Accepted consequences:
- BriefForge should treat ADPM as the canonical next semantic foundation.
- Future decision-support work should validate against ADPM before UI/rendering work.
- Backlog language should move from source-specific decision-package terminology to general ADPM terminology.

Rejected consequences:
- no runtime behavior is implemented by this decision;
- no renderer behavior changes;
- no Presentation Package or Presentation Grammar implementation changes;
- no templates or dashboards;
- no generated-project modifications.

## Follow-up recommendation

Open a later bounded validation task only after this architecture task is closed:

`TASK-036 Manual ADPM Validation Against Existing Investigation Corpora`

Purpose:
- test whether the ADPM objects are sufficient and minimal across representative architectural decision scenarios before implementing schema or renderer behavior.

Non-goals:
- no runtime implementation;
- no renderer integration;
- no dashboards;
- no generated project changes.
