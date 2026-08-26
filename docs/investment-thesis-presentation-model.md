# Investment Thesis Presentation Model

Date: 2026-07-02
Status: Implemented as TASK-019 semantic authoring abstraction

## Purpose

`InvestmentThesisPresentation` is the third BriefForge Presentation Model.

It validates that a fundamentally different semantic presentation — claim-bearing, uncertainty-preserving, and decision-relevant — can still compile into the existing `CandidatePresentationPackage` without adding runtime, rendering, template, browser, visualization, persistence, API, networking, InsightForge, or constitutional concepts.

## What was implemented

- `InvestmentThesisPresentation`
- `InvestmentThesisBuilder`
- conversion to the existing `CandidatePresentationPackage` through `to_candidate_presentation_package()`
- small authoring surface for:
  - subject;
  - identity;
  - organizing purpose;
  - references;
  - obligations;
  - thesis statement;
  - supporting evidence;
  - risks;
  - counterarguments;
  - conclusion;
  - generic thesis sections.

The model uses `PresentationPackageBuilder` internally.

## Why this remains a semantic Presentation Model

An Investment Thesis model is upstream authoring vocabulary. It helps an author express recurring investment-thesis intent, but it does not become canonical runtime substance.

The canonical BriefForge object remains the `CandidatePresentationPackage`.

The boundary remains:

```text
Investment Thesis Presentation Model
-> PresentationPackageBuilder
-> CandidatePresentationPackage
```

After conversion, validation, promotion, renderer-adapter checks, rendering, and conformance operate on the existing runtime objects only.

## Why this is not a report template

The model does not prescribe visual layout, page order, component slots, style, HTML, charts, maps, dashboard behavior, browser interaction, or export behavior.

`thesis_statement`, `supporting_evidence`, `risk`, `counterargument`, and `conclusion` are authoring conveniences. They map to ordinary presentation statements with encounter semantics and do not create runtime sections, claim objects, evidence objects, risk tables, or recommendation records.

## End-to-end proof

A realistic manually authored thesis was created: European grid investment as a transition-bottleneck theme.

It crossed the existing lifecycle unchanged:

```text
InvestmentThesisPresentation
-> PresentationPackageBuilder
-> Candidate Presentation Package
-> Validation
-> Validation Judgment
-> Ready Presentation Package
-> Renderer Adapter Boundary
-> Renderer Invocation
-> Minimal HTML Renderer
-> Rendered Artifact Conformance
```

No new workflow stage was introduced.

The deterministic semantic fingerprint for this thesis is:

```text
f237c2b7dc0e580c518671c274868158c3078eb998e4cc08670c1c04b100116d
```

## Architectural evaluation

### Claims

The thesis claim mapped naturally to a `PresentationStatement` with `investment-thesis-claim` encounter mode.

Classification: authoring friction only. No runtime friction and no constitutional contradiction.

### Supporting evidence

Supporting evidence mapped to normal statements linked to upstream references. BriefForge still does not own factual, analytical, or source meaning.

Classification: no runtime friction. Authoring judgment is required to keep evidence source-owned.

### Uncertainty

Uncertainty mapped through explicit obligations and risk/counterargument statements. The model did not require a probability, confidence, or uncertainty runtime object.

Classification: authoring friction only.

### Risks

Risks mapped to presentation statements plus obligations. They can be encountered in sequence without a risk-table runtime construct.

Classification: authoring friction only.

### Counterarguments

Counterarguments mapped naturally to statements with a counterargument encounter mode and relationships to claim/risk/conclusion statements.

Classification: no architecture pressure.

### Conclusions

The conclusion mapped naturally to a bounded presentation statement. The key architectural constraint was to keep it from becoming recommendation or advice, handled by obligations and scope text.

Classification: authoring friction and scope-control judgment only.

## Infrastructure expansion assessment

No infrastructure expansion was genuinely required.

Not changed:
- runtime dataclasses;
- validation;
- promotion;
- renderer boundaries;
- HTML renderer;
- conformance;
- serialization;
- persistence;
- APIs;
- templates;
- layout;
- browser code;
- visualization systems.

## Implementation pressure discovered

Investment Thesis introduced pressure around authoring discipline, not architecture:

- preventing thesis language from becoming investment advice;
- deciding the right granularity for evidence/risk/counterargument statements;
- preserving uncertainty inside the presentation rather than collapsing it into a one-sided claim;
- keeping upstream evidence ownership explicit;
- deciding whether future thesis vocabulary should distinguish base case, upside, downside, catalysts, or monitoring signals.

That pressure does not justify runtime expansion from one proof.

## Implementation Readiness Assessment

GREEN.

1. Validated architectural assumptions:
   - Presentation Models can remain upstream authoring abstractions even for claim-bearing presentations.
   - The existing Candidate Presentation Package can represent descriptive, comparative, and investment-thesis presentations.
   - Existing statements, encounter semantics, references, obligations, deterministic fingerprints, validation, promotion, rendering, and conformance are sufficient for a small thesis.

2. Evidence against the frozen constitution:
   - None found.

3. Smallest next capability:
   - Do not expand infrastructure yet. The smallest useful next capability is either another fundamentally different presentation model proof or a bounded downstream obligation/reference visibility slice if reader-facing audit clarity is now the bottleneck.

4. Presentation-driven development status:
   - Still presentation-driven. TASK-019 added only the model needed for the thesis proof and did not broaden infrastructure.
