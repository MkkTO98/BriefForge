# Report: BriefForge Architectural Validation Plan

Date: 2026-07-02
Type: architectural validation planning
Status: Final
Owner: BriefForge
Scope: smallest validation-only implementation experiment capable of testing the frozen constitutional and runtime architecture

## 1. Executive conclusion

The smallest implementation capable of validating the frozen architecture is not a product slice.

It is a validation-only architectural experiment whose sole purpose is to prove that a Ready Presentation Package can exist without any rendering technology.

The minimal experimental loop is:

```text
Candidate Presentation Package
-> Presentation Validation
-> Ready Presentation Package or Rejected Package
-> Downstream Consumption Boundary assertion
```

The experiment should not produce a useful presentation.

The experiment should prove only that:

1. a candidate package can carry the frozen constitutional concepts;
2. presentation-local validation can accept or reject that package;
3. a ready package can exist as semantic authority without rendering;
4. a downstream consumer boundary can be represented without giving the consumer semantic authority.

This is enough to test the architecture before any renderer, browser, template, API, serialization, or persistence decision is allowed.

## 2. Governing architectural baseline

This plan treats the following artifacts as fixed:

- Frozen constitution: `CONSTITUTION.md`
- Implementation Constitution: `artifacts/reports/R-20260701-implementation-constitution.md`
- Implementation Architecture Extraction: `artifacts/reports/R-20260702-implementation-architecture-extraction.md`
- Runtime Representation Architecture: `artifacts/reports/R-20260702-runtime-representation-architecture.md`

BriefForge owns exactly:

1. Presentation Contract.
2. Composition Semantics.
3. Presentation Validation Obligations.

The canonical object is the structured semantic Presentation Package.

The runtime lifecycle is:

```text
Candidate Presentation Package
-> Validation Judgment
-> Ready Presentation Package or Rejected Package
-> Downstream Consumption Boundary
```

This plan does not reopen those decisions.

## 3. Central validation question

Can BriefForge demonstrate that a Ready Presentation Package exists independently of every rendering technology?

A successful validation experiment answers yes by showing that readiness depends only on presentation-local semantic validity, not on HTML, PDF, browser state, renderer output, visualization grammar, template expansion, API transport, storage, or UI behavior.

## 4. Minimal implementation scope

The first implementation experiment should contain only four conceptual capabilities.

### 4.1 Candidate package construction for test purposes

Purpose:

Create the smallest candidate package-shaped object needed to exercise the frozen concepts.

Minimum content:

- package identity;
- organizing purpose;
- at least one organized presentation statement;
- target-independent encounter semantics sufficient to prove composition is not rendering;
- upstream reference for any statement that depends on upstream-owned meaning;
- required presentation obligations attached to the relevant statement or reference.

Not included:

- file loading;
- serialization;
- persistence;
- authoring UI;
- package editor;
- import pipeline;
- canonical data lookup;
- real upstream data retrieval.

Validation role:

This candidate exists only as controlled experimental input.

### 4.2 Presentation validation

Purpose:

Evaluate whether the candidate satisfies the frozen presentation-local contract.

Minimum validation checks:

1. Package has bounded identity.
2. Package has Organizing Purpose.
3. Every presentation statement belongs to the Organizing Purpose.
4. Encounter semantics are target-independent and internally coherent.
5. Statements with upstream dependency have upstream references.
6. Required presentation obligations are present and attached.
7. No forbidden ownership concepts appear in the package boundary.
8. Candidate is accepted as Ready only if all required checks pass.

Not included:

- economic truth validation;
- analytical correctness validation;
- confidence judgment calculation;
- caveat correctness judgment;
- freshness checking against external systems;
- renderer behavior validation;
- browser behavior validation;
- UI quality validation.

### 4.3 Ready or rejected package transition

Purpose:

Prove that package readiness is a validation state, not a rendered artifact.

Minimum behavior:

- accepted candidate becomes Ready for downstream consumption;
- rejected candidate remains non-ready;
- validation judgment explains acceptance or rejection at the architectural-category level;
- semantic mutation after readiness requires revalidation.

Not included:

- version store;
- history log;
- database status field;
- workflow engine;
- event sourcing;
- lifecycle orchestration.

### 4.4 Downstream consumption boundary assertion

Purpose:

Prove that a downstream consumer can receive or observe a Ready Package without becoming semantic authority.

Minimum behavior:

- downstream boundary accepts only Ready packages;
- downstream boundary rejects Candidate or Rejected packages;
- downstream boundary cannot add, remove, reinterpret, or detach identity, purpose, statements, references, or obligations;
- downstream boundary does not render, export, serialize, display, route, search, persist, or network the package.

Not included:

- renderer adapter;
- HTML exporter;
- PDF exporter;
- browser view;
- visualization adapter;
- template engine;
- API endpoint;
- portal integration;
- search or catalog integration.

## 5. Explicit exclusions from the validation implementation

The first validation experiment must exclude:

- HTML;
- PDF;
- browser;
- renderer;
- visualization;
- charts;
- maps;
- dashboards;
- templates;
- APIs;
- serialization;
- persistence;
- UI;
- search;
- portal;
- networking;
- real data ingestion;
- canonicalization;
- analysis;
- generic plugin framework;
- schema language adoption;
- dataclass/model framework adoption.

If any of these are required for the experiment to pass, that is evidence against the current architectural assumptions.

## 6. Smallest validation examples

The first implementation experiment needs only a tiny evidence set.

### 6.1 One valid candidate

A minimal valid candidate should prove:

- identity exists;
- organizing purpose exists;
- one or more presentation statements belong to that purpose;
- encounter semantics organize statements without layout or rendering;
- upstream dependency is represented as reference, not absorbed truth;
- obligations are attached;
- validation accepts the candidate;
- downstream boundary recognizes only the Ready package.

### 6.2 One missing-obligation invalid candidate

Purpose:

Prove obligations are required correctness constraints, not optional display hints.

Expected outcome:

Validation rejects the candidate.

### 6.3 One missing-reference invalid candidate

Purpose:

Prove upstream-dependent statements cannot become BriefForge-owned meaning.

Expected outcome:

Validation rejects the candidate.

### 6.4 One boundary-violation invalid candidate

Purpose:

Prove renderer/browser/template/portal concepts are not accepted into canonical package meaning.

Expected outcome:

Validation rejects the candidate.

### 6.5 One downstream-authority invalid interaction

Purpose:

Prove downstream consumption cannot reinterpret the Ready Package as semantic authority.

Expected outcome:

Boundary assertion rejects or flags the interaction.

This five-example set is the smallest useful architectural evidence set. Fewer examples would test the happy path only and fail to falsify the boundaries that matter.

## 7. Architectural assumptions under test

### Assumption A1: Presentation Package independence

Claim:

A Presentation Package can exist as a semantic object without rendering, serialization, storage, UI, or networking.

Test:

Create and validate a candidate package without any excluded technology.

Success criterion:

A Ready Package exists after validation and no renderer/browser/template/API/persistence mechanism is involved.

Failure interpretation:

- Implementation defect if the experiment accidentally couples package creation to a chosen technology.
- Runtime architecture defect if the candidate cannot exist without a lifecycle stage that the runtime architecture omitted.
- Implementation architecture defect if the package contract requires technology-specific mechanisms not identified by the extraction report.
- Constitutional defect only if presentation meaning itself cannot be represented without delivery meaning.

### Assumption A2: Validation is presentation-local

Claim:

BriefForge can validate package readiness without validating economic truth, analytical correctness, or renderer quality.

Test:

Validation accepts/rejects candidates based only on identity, purpose, statements, encounter semantics, references, obligations, and boundary compliance.

Success criterion:

Validation produces acceptance/rejection without fetching upstream data or judging analytical truth.

Failure interpretation:

- Implementation defect if validation accidentally performs external lookup, data truth checks, or analysis.
- Runtime architecture defect if validation result cannot be separated from upstream truth or downstream rendering.
- Implementation architecture defect if the validation boundary is too underspecified to implement presentation-local checks.
- Constitutional defect if the constitution's obligations require truth/analysis judgment by BriefForge.

### Assumption A3: Obligations can be validated without rendering

Claim:

Presentation obligations are semantic attachment constraints, not display/layout rules.

Test:

A missing-obligation candidate is rejected before any renderer exists; a valid candidate is accepted because obligations are present and attached.

Success criterion:

Obligation satisfaction is decidable without knowing how anything will be displayed.

Failure interpretation:

- Implementation defect if obligations are modeled as display hints or layout instructions.
- Runtime architecture defect if obligation attachment cannot be represented independently of a downstream consumer.
- Implementation architecture defect if obligation categories need a stronger attachment model than currently planned.
- Constitutional defect if obligations are only meaningful as rendered visibility rules rather than semantic constraints.

### Assumption A4: Upstream references preserve ownership without ingestion

Claim:

BriefForge can preserve upstream ownership through references without ingesting, canonicalizing, or validating upstream material.

Test:

A statement with upstream dependency is valid only when an upstream reference and required obligations remain attached.

Success criterion:

Validation can distinguish referenced upstream meaning from BriefForge-owned presentation meaning without retrieving upstream content.

Failure interpretation:

- Implementation defect if validation dereferences or imports upstream data unnecessarily.
- Runtime architecture defect if references cannot be attached and preserved through readiness.
- Implementation architecture defect if the reference model is too weak to distinguish ownership from content copying.
- Constitutional defect if BriefForge cannot preserve presentation meaning without owning upstream content.

### Assumption A5: Composition semantics are target-independent

Claim:

Organized presentation statements can have encounter semantics without becoming layout, visual encoding, template hierarchy, portal route graph, or browser navigation.

Test:

The valid candidate uses minimal encounter semantics and passes; a boundary-violation candidate using delivery-specific concepts fails.

Success criterion:

Validation accepts target-independent organization and rejects delivery-specific organization.

Failure interpretation:

- Implementation defect if the implementation names or treats encounter semantics as UI/layout concepts.
- Runtime architecture defect if composition cannot be evaluated as package substance rather than a separate runtime stage.
- Implementation architecture defect if the minimal composition representation is underspecified.
- Constitutional defect if target-independent encounter semantics cannot be distinguished from delivery mechanics.

### Assumption A6: Ready status is validation-derived

Claim:

Readiness is produced by presentation validation and is not equivalent to successful rendering, persistence, export, or transport.

Test:

Only accepted candidates become Ready; invalid candidates remain non-ready; no rendered artifact exists.

Success criterion:

Ready status is determined entirely by validation judgment.

Failure interpretation:

- Implementation defect if readiness is tied to generated output or external side effect.
- Runtime architecture defect if Ready Package state cannot be represented separately from validation result.
- Implementation architecture defect if transition rules are incomplete.
- Constitutional defect if readiness cannot be meaningful without a delivery artifact.

### Assumption A7: Downstream consumers are non-authoritative

Claim:

A downstream consumption boundary can exist without implementing a downstream technology and without transferring semantic authority.

Test:

Boundary accepts only Ready packages and rejects attempts to consume candidates/rejected packages or detach obligations/references.

Success criterion:

The boundary proves consumer eligibility and preservation requirements without rendering, exporting, routing, or displaying.

Failure interpretation:

- Implementation defect if the boundary performs rendering/exporting or mutates package semantics.
- Runtime architecture defect if downstream consumption cannot be represented without a concrete consumer technology.
- Implementation architecture defect if consumer boundary rules are too weak to prevent semantic authority leakage.
- Constitutional defect if BriefForge's package semantics require the consumer to define meaning.

## 8. Success criteria for the first validation implementation

The first implementation experiment succeeds only if all of the following are true:

1. A valid Candidate Presentation Package is accepted as Ready.
2. At least one invalid candidate is rejected for missing obligations.
3. At least one invalid candidate is rejected for missing upstream references.
4. At least one invalid candidate is rejected for boundary violation.
5. A downstream boundary accepts only Ready packages.
6. A downstream boundary cannot become semantic authority.
7. No renderer, browser, template, visualization, API, persistence, serialization, networking, search, portal, map, chart, dashboard, or UI system is used.
8. Validation remains presentation-local.
9. The implementation does not introduce dataclasses, schemas, framework models, or production package formats as architectural authority.
10. The resulting evidence can be summarized as architecture validation, not product functionality.

## 9. Failure interpretation guide

| Failure observed | Primary interpretation | Escalation condition |
|---|---|---|
| Valid candidate cannot be represented without choosing a renderer/browser/template | Possible constitutional defect | Escalate if no simpler implementation representation can remove the coupling |
| Valid candidate cannot be represented without serialization/persistence | Runtime or implementation architecture defect | Escalate if package identity/readiness requires durable storage rather than runtime semantics |
| Validation requires economic truth or analytical correctness | Constitutional or implementation architecture defect | Escalate if obligations cannot be checked without truth ownership |
| Obligations cannot be attached without display/layout concepts | Runtime architecture or constitutional defect | Escalate if semantic attachment cannot be separated from rendered visibility |
| References require data ingestion or canonicalization | Implementation defect first; constitutional defect only if unavoidable | Escalate if ownership preservation cannot work without content ownership |
| Encounter semantics collapse into layout/template concepts | Implementation defect first; runtime architecture defect if unavoidable | Escalate if target-independent organization cannot be made concrete |
| Ready status depends on rendered output | Implementation defect | Escalate only if no validation-derived readiness model is possible |
| Downstream boundary must render/export/display to be meaningful | Runtime architecture defect | Escalate if boundary cannot be expressed as eligibility/preservation rules |
| Invalid package passes validation | Implementation defect or incomplete implementation architecture | Escalate if the failure reveals missing constitutional validation obligation |
| Valid package fails because validation is over-broad | Implementation defect | Escalate if the frozen constitution itself is overconstraining minimal validity |

Failure classification order should be conservative:

1. Implementation defect.
2. Runtime architecture defect.
3. Implementation architecture defect.
4. Constitutional defect.

Do not declare a constitutional defect from the first failed experiment unless the failure remains after removing implementation choices and confirming that the frozen concepts themselves are contradictory.

## 10. Minimal implementation shape

The first implementation should be a test harness plus the smallest validation core needed to exercise the architecture.

It should not be a package authoring system, rendering system, storage system, API, or product feature.

Conceptual pieces:

1. Test-owned candidate package examples.
2. Validation operation.
3. Validation judgment.
4. Ready/rejected transition marker.
5. Downstream boundary assertion.

All pieces should be disposable if later architecture changes.

The implementation should be intentionally boring. Its job is not to be elegant; its job is to falsify or strengthen the architecture at minimum cost.

## 11. Recommended first implementation task

Recommended task title:

`TASK-001: Validation-only Presentation Package readiness experiment`

Purpose:

Implement the smallest local validation experiment proving that a Candidate Presentation Package can become Ready through presentation-local validation and cross a downstream consumption boundary without any renderer, browser, template, API, serialization, persistence, UI, or networking.

Non-goals:

- no HTML;
- no PDF;
- no browser;
- no renderer;
- no visualization;
- no charts;
- no maps;
- no dashboards;
- no templates;
- no APIs;
- no serialization;
- no persistence;
- no UI;
- no search;
- no portal;
- no networking;
- no production presentation output;
- no dataclasses or schemas as architectural authority;
- no general implementation beyond the validation experiment.

Required evidence:

1. One valid candidate becomes Ready.
2. Missing-obligation candidate is rejected.
3. Missing-reference candidate is rejected.
4. Boundary-violation candidate is rejected.
5. Downstream boundary accepts Ready and rejects non-ready.
6. Verification output proves the experiment runs locally.
7. Closeout report classifies any failures using this plan's failure interpretation guide.

Implementation discipline:

- Write tests first.
- Keep all examples artificial and minimal.
- Avoid introducing production file formats.
- Avoid naming anything after UI/layout/rendering concepts.
- Stop after architecture validation evidence is produced.

This recommended task is not created by this report. It should be created only if explicitly approved as the first implementation experiment.

## 12. Architectural phase conclusion

This report concludes the architecture-planning sequence before the first implementation experiment.

The frozen constitution says what BriefForge is.

The implementation architecture extraction says what BriefForge-specific implementation responsibilities exist.

The runtime representation architecture says how those concepts exist during execution.

This architectural validation plan says what the first implementation must test before general implementation expands.

If the recommended validation-only task succeeds, BriefForge will have evidence that its canonical Presentation Package can become Ready independently of rendering technologies.

If it fails, the failure should be interpreted using this report before any workaround, framework adoption, renderer introduction, or constitutional revision is proposed.
