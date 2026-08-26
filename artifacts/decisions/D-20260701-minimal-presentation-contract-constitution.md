# Decision: Minimal Presentation Contract Constitution

Date: 2026-07-01
Status: Accepted for Architectural Revision; not frozen for implementation
Owner: BriefForge
Related reports:

- `artifacts/reports/R-20260701-constitutional-architecture.md`
- `artifacts/reports/R-20260701-constitutional-architecture-falsification-review.md`
- `artifacts/reports/R-20260701-constitutional-architecture-revision.md`

## Decision

BriefForge's revised constitutional architecture is centered on exactly three core concepts:

1. Presentation Contract.
2. Composition Semantics.
3. Presentation Validation Obligations.

BriefForge is EIP's presentation contract system, not a renderer, browser app, dashboard platform, visualization system, map system, search system, portal, template engine, API service, data owner, analysis owner, ingestion system, canonicalization system, or generic UI component library.

The canonical representation is the structured semantic presentation package. HTML may be a likely future rendered target, but HTML is not constitutionally canonical.

## Rationale

The falsification review found that BriefForge's external boundary mostly survived review, but its proposed internal vocabulary risked prematurely freezing an elegant but unevidenced hierarchy.

The revised constitution therefore keeps the boundary and shrinks the internal architecture.

## Accepted concepts

- Presentation Contract.
- Composition Semantics.
- Presentation Validation Obligations.
- Structured semantic presentation package.
- Upstream-owned reference.
- Presentation obligation.
- Presentation self-description metadata.
- Target-independent presentation intent.

## Demoted candidate vocabulary

The following are not constitutional subsystems:

- primitives;
- components;
- blocks;
- sections;
- templates;
- archetypes;
- render plans;
- exports;
- broad lifecycle metadata;
- portal metadata.

They may be used only as candidate vocabulary in future architecture investigations unless later evidence justifies promotion.

## Non-authorizations

This decision does not authorize:

- production code;
- renderer implementation;
- browser implementation;
- dashboard implementation;
- visualization implementation;
- map implementation;
- search implementation;
- portal/navigation implementation;
- API implementation;
- template implementation;
- generic UI component library work;
- implementation tasks.

## Architecture gate

BriefForge is currently at:

```text
Architecture Proposal
-> Architectural Review
-> Architectural Revision
-> Constitution Freeze
-> Implementation
```

This decision records Architectural Revision only. Constitution Freeze has not occurred.
