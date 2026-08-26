# Country Comparison Presentation Model

Date: 2026-07-02
Status: Implemented as TASK-018 semantic authoring abstraction

## Purpose

`CountryComparisonPresentation` is the second BriefForge Presentation Model.

It exists to validate that a substantially different presentation type can still compile into the existing `CandidatePresentationPackage` without adding runtime, rendering, template, browser, visualization, persistence, API, or constitutional concepts.

## What was implemented

- `CountryComparisonPresentation`
- `CountryComparisonBuilder`
- conversion to the existing `CandidatePresentationPackage` through `to_candidate_presentation_package()`
- small authoring surface for:
  - compared countries;
  - identity;
  - organizing purpose;
  - references;
  - obligations;
  - overview statements;
  - selected indicators;
  - similarities;
  - differences;
  - generic comparison sections.

The model uses `PresentationPackageBuilder` internally.

## Why Presentation Models remain authoring abstractions

A Presentation Model is upstream authoring vocabulary. It helps an author express recurring presentation intent, but it does not become canonical.

The canonical BriefForge object remains the `CandidatePresentationPackage`.

The boundary remains:

```text
Country Comparison Presentation Model
-> PresentationPackageBuilder
-> CandidatePresentationPackage
```

After conversion, validation, promotion, renderer-adapter checks, rendering, and conformance operate on the existing runtime objects only.

## Why this is not a template

The model does not prescribe visual layout, page structure, components, style, HTML, charts, maps, or browser behavior.

`indicator`, `similarity`, and `difference` are authoring conveniences that map to ordinary presentation statements with encounter semantics. They do not create runtime sections, layout slots, visualization marks, or template regions.

## End-to-end proof

A realistic Denmark vs Germany comparison was authored through the model.

It crossed the existing lifecycle unchanged:

```text
CountryComparisonPresentation
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

The deterministic semantic fingerprint for this comparison is:

```text
e5e6a30c6c04c1132391d77df9c4ec8341117068a5cc3fc708402d04d1c7fb11
```

## Architectural evaluation

### Organizing purpose

Comparison fit the existing Organizing Purpose model naturally. The purpose describes the reader-facing comparative frame without requiring a new comparison-specific runtime object.

Classification: implementation friction only if authoring text is verbose; no runtime friction or constitutional contradiction.

### Presentation statements

Overview, selected indicators, similarities, differences, and synthesis all mapped naturally to existing `PresentationStatement` records.

Classification: authoring friction around naming and statement granularity; no runtime friction.

### Encounter semantics

Comparison-specific reading intent fit in `EncounterSemantics.mode` and `description` using modes such as `comparative-indicator`, `comparative-similarity`, and `comparative-difference`.

Classification: authoring friction if mode vocabulary grows; no constitutional contradiction.

### References

Shared comparison references mapped to existing upstream references. BriefForge still does not own data or analysis meaning.

Classification: no architecture pressure.

### Obligations

Comparison-specific obligations such as no ranking/recommendation and approximate manual data mapped to existing obligations.

Classification: no architecture pressure, though downstream reader visibility remains a previously observed possible next slice.

### Deterministic identifiers

Explicit ids worked unchanged. Existing deterministic builder-side ids remain available if ids are omitted.

Classification: no new identifier architecture required.

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

Country Comparison introduced pressure around comparison vocabulary, not architecture:

- authors need to decide whether a statement is an indicator, similarity, difference, or generic section;
- compared countries are authoring context and do not appear as runtime fields;
- relation/obligation authoring still requires human judgment;
- a future vocabulary expansion should be evidence-driven by more real comparison examples, not added preemptively.

## Implementation Readiness Assessment

GREEN.

1. Validated architectural assumptions:
   - Presentation Models can remain upstream authoring abstractions.
   - The existing Candidate Presentation Package can represent both profile and comparison presentations.
   - Existing statements, encounter semantics, references, obligations, deterministic ids, validation, promotion, rendering, and conformance are sufficient for a small country comparison.

2. Evidence against the frozen constitution:
   - None found.

3. Smallest next capability:
   - Author one more comparison or a non-country presentation model before adding more model vocabulary; alternatively address downstream obligation/reference visibility if reader-facing audit visibility becomes the bottleneck.

4. Presentation-driven development status:
   - Still presentation-driven. The implementation added only the model needed for the Denmark vs Germany proof and did not expand infrastructure.
