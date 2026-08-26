# Project Identity

This file is the project-owned constitutional identity artifact. It defines what BriefForge is, what it is for, what it must not become, and which authority boundaries agents must respect.

## Project identity

- Name: BriefForge
- Primary purpose: BriefForge is the local presentation contract system for the economic-intelligence ecosystem. Its constitutional role is to define and validate structured semantic Presentation Packages that compose upstream-owned information without owning data, analysis, ingestion, canonicalization, rendering, browser applications, dashboards, maps, search, portal navigation, templates, APIs, or generic UI component libraries.
- Frozen constitutional core: Presentation Contract, Composition Semantics, and Presentation Validation Obligations.
- Current gate: Constitution Freeze complete. Implementation has not begun and still requires a separate approved implementation task.
- Constitutional status: Stable and frozen as of `artifacts/reports/R-20260701-constitution-freeze.md`.
- Primary users or consumers: Primary users are Mikkel and Hermes agents operating the economic-intelligence ecosystem. Future downstream consumers may include approved renderers, adapters, portal/navigation systems, and user-facing intelligence surfaces, but those systems do not become BriefForge constitutional responsibilities by consuming BriefForge packages.

## Frozen constitutional architecture

BriefForge owns exactly these constitutional responsibilities:

1. Presentation Contract.
2. Composition Semantics.
3. Presentation Validation Obligations.

The canonical object is the structured semantic Presentation Package.

A canonical Presentation Package consists of exactly these required category types:

1. Package identity.
2. Organizing Purpose.
3. Organized presentation statements with target-independent encounter semantics.
4. Upstream-owned references where dependency exists.
5. Presentation obligations.

BriefForge owns presentation meaning only.

BriefForge references economic and analytical meaning owned elsewhere.

BriefForge excludes delivery meaning.

## Frozen semantic definitions

### Package identity

Package identity is the bounded self-identification of the Presentation Package: what it is, what presentation purpose it serves, what scope it claims, and what scope it explicitly does not claim.

### Organizing Purpose

Organizing Purpose is the target-independent reason that binds the package's presentation statements into one bounded presentation object, including scope and non-scope, without creating upstream economic or analytical meaning.

### Presentation statement

A presentation statement is the smallest BriefForge-owned unit of presentation meaning. It says what should be encountered, why it belongs to the package's Organizing Purpose, how it relates to other presentation statements when relevant, and which upstream-owned references and presentation obligations must remain attached.

A presentation statement does not create upstream economic or analytical meaning.

### Target-independent encounter semantics

Target-independent encounter semantics define presentation-local organization independent of runtime, medium, surface, or delivery target.

They may include order, partial order, relation, grouping, hierarchy, or navigable encounter paths where constitutionally needed.

They must not define renderer behavior, browser mechanics, user state, portal routing, personalization, search, ranking, dashboard behavior, visualization systems, templates, or delivery implementation.

### Upstream-owned references

Upstream-owned references identify material on which a presentation statement depends while preserving upstream ownership of economic, analytical, evidential, definitional, caveat, confidence, freshness, and provenance meaning.

### Presentation obligations

Presentation obligations are required constraints that prevent presentation from hiding, weakening, detaching, overstating, or transforming upstream-owned meaning.

The irreducible obligation categories are ownership visibility, evidence/provenance visibility, caveat/scope visibility, confidence/uncertainty visibility, freshness/review-state visibility, non-transformation, and non-detachment.

## Scope

### In scope

BriefForge may define, validate, and preserve:

- the Presentation Contract;
- Composition Semantics for organized presentation statements with target-independent encounter semantics;
- Presentation Validation Obligations;
- upstream-owned references;
- package identity and Organizing Purpose;
- presentation self-description needed to understand the package without making BriefForge a portal, registry, search system, or prioritization system;
- constitutional and architectural governance artifacts needed to preserve the frozen architecture.

### Explicit non-scope

BriefForge must not own:

- production functionality not separately approved after freeze;
- data ingestion;
- canonicalization;
- canonical economic data storage;
- source-specific economic semantics;
- analytical conclusions;
- confidence judgments for analysis;
- domain or investment judgment;
- rendering engines;
- browser applications;
- dashboards;
- visualization engines or grammars;
- map systems or GIS rendering;
- search/indexing/ranking systems;
- portal navigation, routing, sessions, personalization, or reading queues;
- APIs as constitutional architecture;
- template engines;
- generic UI component libraries;
- external scaffolding methodology;
- external architecture harvesting or advisory knowledge storage;
- ecosystem coordination or prioritization.

## Responsibility boundaries

BriefForge owns only the structured semantic presentation contract and validation layer that allows upstream-owned structured information to later be consumed by downstream or adjacent systems.

It may consume structured, reviewed outputs from owning projects through explicit contracts once those contracts are designed and approved.

Default boundaries when a more specific decision is absent:

- This repository owns only its local files, policies, decisions, source code if later approved, tests if later approved, documentation, and generated artifacts.
- This repository does not govern other projects, external ecosystems, advisory providers, or infrastructure outside this checkout.
- External services, paid resources, credentials, production data, destructive actions, publishing, and remote pushes require explicit human approval or an accepted local decision artifact.
- Missing or ambiguous project-wide policy must not be invented silently. Record a deferred decision or ask a blocking question when the ambiguity changes scope, safety, cost, or long-term responsibility.

## Constitutional change control

The constitutional architecture is considered stable and frozen.

Future constitutional modifications require architectural evidence.

The following are insufficient justification for constitutional change:

- implementation convenience;
- aesthetic preference;
- theoretical elegance;
- symmetry with another project;
- framework or library pressure;
- desire for faster implementation;
- accidental coupling discovered during coding without architectural analysis.

Future implementation discoveries may improve implementation. They do not automatically justify constitutional evolution.

A future constitutional change is justified only when evidence shows that the frozen constitution prevents BriefForge from satisfying its mission or creates materially worse boundary, validation, or ownership outcomes than an alternative.

## Operating principles

1. Keep the project understandable from ordinary files: Markdown, YAML, JSON, source code if later approved, tests if later approved, and deterministic local outputs.
2. Prefer simple, reversible, project-owned changes over hidden automation or broad abstractions.
3. Preserve durable choices as local decision artifacts when they affect identity, scope, responsibility, policy, or architecture.
4. Treat generated scaffolding as a starting point, not an external authority.
5. Do not broaden project purpose or responsibility by convenience.
6. Do not freeze primitives, components, blocks, sections, templates, archetypes, render plans, exports, broad lifecycle metadata, or portal metadata as constitutional architecture unless later evidence justifies constitutional revision.
7. Treat any specific rendered target as a possible future rendered representation, not the canonical semantic representation.
8. Preserve renderer, portal, dashboard, visualization, map, search, API, template, and generic UI-component boundaries unless later constitutional evidence justifies revision.

## Architecture gate

BriefForge follows this architecture gate sequence:

```text
Architecture Proposal
-> Architectural Review
-> Architectural Revision
-> Adversarial Review
-> Canonical Object Discovery
-> Expressiveness Proof
-> Final Semantic Investigation
-> Constitution Freeze
-> Implementation Constitution
-> Implementation
```

Current stage: Constitution Freeze complete; Implementation Constitution produced; Implementation not started.

Implementation requires a separate approved implementation task after Constitution Freeze or an explicit human decision overriding the gate.

## Implementation bridge

Future implementation must preserve `artifacts/reports/R-20260701-implementation-constitution.md` as the bridge from frozen constitutional concepts to implementation concepts.

Implementation may choose concrete representations, validation mechanics, storage, runtime, adapters, or downstream consumption mechanisms only when those choices preserve the frozen constitutional architecture.

Implementation must not reinterpret constitutional concepts to fit a convenient technology.

## Instruction hierarchy

When project instructions conflict, use this order:

1. Direct human instruction for the current task.
2. This Project Identity artifact for purpose, scope, responsibility boundaries, operating principles, authority boundaries, architecture gate, and constitutional freeze status.
3. Accepted local decision artifacts that refine or amend identity/scope.
4. Project-local agent and instruction files for execution behavior.
5. Current-state files and summaries for orientation.
6. Historical reports, handoffs, logs, and generated artifacts as evidence only.

If a lower-priority artifact conflicts with a higher-priority artifact, follow the higher-priority artifact and record the conflict if it affects future work.

## Generated-project independence

This project is autonomous after creation. Its copied scaffold is project-owned.

- No external generator is required to run, modify, govern, validate, or understand this project.
- Template provenance is historical context only, not authority.
- Future template/framework changes elsewhere do not silently mutate this project.
- This project must not assume any consumer ecosystem, advisory provider, or parent workspace unless a local decision explicitly adopts one.
