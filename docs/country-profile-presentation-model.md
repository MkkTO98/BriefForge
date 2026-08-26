# Country Profile Presentation Model

Date: 2026-07-02
Status: Implemented as TASK-017 semantic authoring abstraction

## Purpose

`CountryProfilePresentation` is the first BriefForge Presentation Model.

It exists to make a small country-profile presentation easier to author while still producing the existing `CandidatePresentationPackage` runtime object.

It is not a template, renderer, browser page, layout system, visualization system, API, persistence layer, export mechanism, or new runtime concept.

## What was implemented

- `CountryProfilePresentation`
- `CountryProfileBuilder`
- conversion to existing `CandidatePresentationPackage` through `to_candidate_presentation_package()`
- small authoring surface for:
  - identity;
  - organizing purpose;
  - references;
  - obligations;
  - overview statements;
  - economy statements;
  - demographics statements;
  - generic country-profile sections.

## Relationship to the existing builder

The Country Profile model uses `PresentationPackageBuilder` internally.

That means it inherits the existing builder behavior:

- production of existing runtime dataclasses;
- required-field rejection;
- deterministic id generation when ids are omitted;
- explicit id preservation when ids are supplied.

## Why this is not a template

A template prescribes rendering structure, visual layout, reusable page components, or output formatting.

The Country Profile model does none of those things.

It only helps authors express country-profile semantic material and then maps that material into the existing Presentation Package representation.

It has no HTML, CSS, JavaScript, layout, chart, map, export, browser, dashboard, or portal behavior.

## Why this introduces no new constitutional concept

The frozen BriefForge constitution already permits authoring of Presentation Packages.

The Country Profile model does not change the canonical object. It does not add fields to `CandidatePresentationPackage`. It does not affect validation, promotion, readiness, renderer adapters, rendered artifacts, or conformance.

The runtime lifecycle remains:

```text
Candidate Presentation Package
-> Validation Judgment
-> Ready Presentation Package
-> Renderer Adapter Boundary
-> Renderer Invocation
-> Minimal HTML Renderer
-> Rendered Artifact Conformance
```

The model is upstream of that lifecycle and emits the same candidate package.

## TASK-014 migration

The Denmark Country Profile was migrated from manual runtime dataclass construction to the Country Profile model.

Result:

- the generated Candidate Presentation Package is semantically equivalent to the original TASK-014 artifact;
- the existing TASK-014 semantic fingerprint remains unchanged:

```text
90d4651099df06afcaf1f531c887b03ae551475096dfa3ad163c44db04c089ff
```

- validation, promotion, renderer-adapter compatibility, renderer invocation, minimal HTML rendering, and conformance all pass unchanged.

## Implementation pressure observed

Presentation Models fit naturally as authoring abstractions, but some pressure remains:

- model vocabulary can become too domain-specific if expanded prematurely;
- authors still need to decide relationships, references, and obligations;
- generic `section()` is necessary to avoid forcing every country-profile theme into a fixed enum too early;
- future models may need evidence before adding richer typed sections.

The correct response is not to add templates or rendering infrastructure. The next pressure is authoring evidence: how many real country profiles can the small model represent before its vocabulary becomes awkward?

## Implementation Readiness Assessment

GREEN.

The Country Profile Presentation Model is safe to keep because it is confined to authoring, uses the existing builder/runtime, preserves the TASK-014 fingerprint, and leaves the frozen constitution and runtime boundaries unchanged.
