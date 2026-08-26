# Report: BriefForge Implementation Constitution

Date: 2026-07-01
Type: implementation-constitution
Status: Final
Owner: BriefForge
Scope: bridge from frozen constitutional architecture to future implementation

## 1. Purpose

This report defines how future BriefForge implementation should preserve the frozen constitutional architecture.

It defines mappings only.

It does not select technologies, programming languages, frameworks, runtimes, storage systems, renderers, browser interfaces, APIs, templates, visualization systems, or production tasks.

## 2. Governing principle

Implementation is free only where the constitution is silent.

Implementation must preserve constitutional invariants even when a convenient technical design would be faster.

The implementation goal is not to make the constitution fit a tool. The goal is to make tools preserve the constitution.

## 3. Required invariant chain

Future implementation must preserve this chain:

```text
Constitutional Concept
-> Implementation Concept
-> Runtime Representation
-> Rendered or Consumed Representation
```

The lower layers may change. The constitutional concept must not.

## 4. Constitutional-to-implementation mappings

### 4.1 BriefForge project mission

Constitutional concept:

- Presentation contract system.

Implementation concept:

- A system that defines, accepts, validates, and exposes semantic presentation packages.

Runtime representation:

- Any inspectable internal representation capable of preserving package identity, Organizing Purpose, organized presentation statements, upstream-owned references, and presentation obligations.

Rendered or consumed representation:

- Any downstream artifact or consumer view that preserves the package's semantic obligations without becoming the source of constitutional truth.

Invariant:

- The implementation must not become data ingestion, analysis, rendering ownership, portal ownership, dashboard ownership, or template ownership by convenience.

### 4.2 Canonical Presentation Package

Constitutional concept:

- Structured semantic Presentation Package.

Implementation concept:

- Package representation.

Runtime representation:

- A concrete internal or persisted representation chosen later.

Rendered or consumed representation:

- A downstream presentation, export, adapter output, or portal-consumed artifact.

Invariant:

- The package is canonical at the semantic level. A rendered artifact is never the constitutional source of truth.

### 4.3 Package identity

Constitutional concept:

- Bounded presentation object identity: what the package is, its purpose, scope, and non-scope.

Implementation concept:

- Package identity metadata.

Runtime representation:

- Any representation that can distinguish one package from another and support validation of scope/non-scope.

Rendered or consumed representation:

- Optional display or discovery information derived from the package identity.

Invariant:

- Identity metadata must not become portal routing, search ranking, personalization, session state, or registry ownership.

### 4.4 Organizing Purpose

Constitutional concept:

- Target-independent reason binding package statements into one bounded presentation object.

Implementation concept:

- Purpose field or purpose structure.

Runtime representation:

- Any inspectable representation that can support validation of whether statements belong to the package.

Rendered or consumed representation:

- Any downstream expression of the package purpose.

Invariant:

- Organizing Purpose must not create analytical conclusions, investment recommendations, audience personalization, portal intent, or delivery strategy.

### 4.5 Organized presentation statements with target-independent encounter semantics

Constitutional concept:

- Smallest BriefForge-owned units of presentation meaning, organized by target-independent encounter semantics.

Implementation concept:

- Statement representation plus composition representation.

Runtime representation:

- Any structure capable of representing statements and their target-independent order, partial order, relations, grouping, hierarchy, or navigable encounter paths where needed.

Rendered or consumed representation:

- Any downstream arrangement that preserves statement meaning and obligations.

Invariant:

- Implementation must not collapse this concept into a mandatory linear document, a UI component tree, a template hierarchy, a visual grammar, or a portal navigation model.

### 4.6 Upstream-owned references

Constitutional concept:

- References to material owned by upstream projects or external owning artifacts.

Implementation concept:

- Reference model.

Runtime representation:

- Any representation that identifies ownership, referenced material, relevant part, and attached obligations.

Rendered or consumed representation:

- Any visible or consumable attribution/provenance/caveat connection required by the package.

Invariant:

- Implementation must not copy upstream meaning into BriefForge ownership, silently transform it, or detach it from required obligations.

### 4.7 Presentation obligations

Constitutional concept:

- Required constraints preserving ownership, evidence, caveats, confidence, freshness, non-transformation, and non-detachment.

Implementation concept:

- Obligation model and validation rules.

Runtime representation:

- Any representation that can be checked before a package is accepted or consumed.

Rendered or consumed representation:

- Any downstream representation that does not hide, weaken, or detach required obligations.

Invariant:

- Obligation preservation is not optional polish. It is a constitutional correctness condition.

### 4.8 Presentation validation

Constitutional concept:

- Presentation-local validation.

Implementation concept:

- Validator or validation process.

Runtime representation:

- Any deterministic or reviewable process capable of checking structure, references, obligations, internal consistency, and boundary compliance.

Rendered or consumed representation:

- Validation outcome, acceptance state, or rejection reason.

Invariant:

- Validation must not validate economic truth, canonicalization correctness, analytical correctness, renderer behavior, portal behavior, or user-facing quality.

### 4.9 Composition

Constitutional concept:

- Composition Semantics.

Implementation concept:

- Composition representation or composition validation.

Runtime representation:

- Any mechanism that preserves organization among statements without changing upstream meaning.

Rendered or consumed representation:

- Any downstream encounter structure that preserves the package's target-independent semantics.

Invariant:

- Composition must not become templates, layout, visual design, interface behavior, search/ranking, or personalization.

### 4.10 Rendering pipeline

Constitutional concept:

- Downstream consumption boundary, not BriefForge constitutional ownership.

Implementation concept:

- Renderer, adapter, exporter, or consumer boundary if later approved.

Runtime representation:

- Any future process that consumes a validated package and produces another representation.

Rendered or consumed representation:

- Any future output target.

Invariant:

- A rendering pipeline must consume the package; it must not become the semantic authority. Renderer substitution must remain possible when obligations are preserved.

### 4.11 Future export targets

Constitutional concept:

- Future downstream representations.

Implementation concept:

- Export adapter or export process if later approved.

Runtime representation:

- Any target-specific conversion process chosen later.

Rendered or consumed representation:

- Any target-specific output.

Invariant:

- Export targets must preserve package meaning and obligations. Export constraints must not rewrite the constitution.

## 5. Implementation decisions intentionally free to evolve

Future implementation may decide, with appropriate task approval:

- internal data structures;
- serialization or persistence format;
- validation mechanics;
- packaging workflow;
- adapter boundaries;
- renderer substitution mechanisms;
- export mechanisms;
- local tooling;
- test strategy;
- runtime language or environment;
- storage approach, if any.

These choices are implementation decisions, not constitutional decisions, unless they change ownership, canonical meaning, validation scope, or excluded responsibilities.

## 6. Implementation decisions not free to evolve without constitutional evidence

Future implementation must not change these without constitutional evidence and accepted constitutional revision:

- BriefForge's mission as a presentation contract system;
- canonical object as semantic Presentation Package;
- five required package category types;
- upstream ownership boundary;
- exclusion of data ingestion and analysis;
- exclusion of rendering, portal, dashboard, visualization, template, and generic UI-component ownership;
- presentation-local validation boundary;
- obligation preservation as a correctness requirement;
- target independence of encounter semantics.

## 7. Boundary-violation tests for future implementation

A future implementation proposal should be rejected or revised if it answers yes to any of these:

1. Does it make BriefForge the owner of economic or analytical meaning?
2. Does it make a rendered artifact the canonical source of truth?
3. Does it require one delivery target to define package semantics?
4. Does it hide or weaken upstream caveats, confidence, freshness, provenance, or ownership?
5. Does it turn composition into templates, layout, UI components, dashboards, maps, or portal navigation?
6. Does validation judge upstream truth or analytical correctness?
7. Does implementation convenience require constitutional language to be reinterpreted without evidence?

## 8. Implementation readiness rule

This Implementation Constitution bridges the frozen constitution to future implementation.

It does not itself authorize implementation.

Future implementation requires a separate approved implementation task that explicitly states how it preserves these mappings and invariants.
