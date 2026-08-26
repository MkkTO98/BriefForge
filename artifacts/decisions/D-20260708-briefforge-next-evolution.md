# Decision: BriefForge Next Evolution After MetaHarvest Third-Generation Expansion

Date: 2026-07-08
Status: Accepted recommendation, not implementation authorization
Scope: BriefForge architectural evolution for MetaHarvest investigations

## Decision

BriefForge's next recommended evolution is to define and validate a MetaHarvest Architectural Decision Package model.

BriefForge should not next prioritize dashboards, browser applications, templates, JavaScript navigation, visualization engines, or additional renderer features.

The immediate need is a stronger decision-support information architecture that turns MetaHarvest investigations into layered, prioritized, evidence-weighted, downstream-actionable architectural packages.

## Context

MetaHarvest's third-generation campaign investigated 39 sources across 8 domains and produced:

- individual source investigations;
- project cards;
- component cards;
- domain comparisons;
- cross-domain synthesis;
- knowledge evolution report;
- final report.

The material is more coherent and evidence-rich than earlier outputs. However, it still places too much burden on human readers to identify:

- what matters most;
- what changed;
- what to do next;
- which evidence is strong enough;
- which EIP project should act;
- which findings are repeated versus one-off;
- which uncertainties block adoption.

## Immediate improvements recommended

### 1. MetaHarvest Architectural Decision Package model

Rationale:
- The primary failure mode is not rendering quality but absence of a decision-ready package structure.

Required sections:
- decision brief;
- ranked recommendations;
- evidence-confidence summary;
- cross-source comparison;
- pattern recurrence map;
- downstream implication map;
- uncertainty/blocker register;
- audit trail.

### 2. Structured recommendation objects

Rationale:
- Prose recommendations are not sufficiently actionable.

Each recommendation should include:
- problem;
- recommended action;
- owner project;
- evidence;
- confidence;
- expected benefit;
- implementation complexity;
- architectural priority;
- dependencies;
- adoption risk;
- non-goals;
- audit links.

### 3. Evidence-confidence framing

Rationale:
- MetaHarvest third-generation evidence is documentation/specimen-first and intentionally did not materialize repositories. This is valid, but recommendations must carry evidence-mode limits.

The package should distinguish:
- high-confidence public architectural contracts;
- medium-confidence documentation/specimen conclusions;
- implementation-uncertain findings;
- adoption blockers;
- materialization-required questions.

### 4. Downstream implication mapping

Rationale:
- MetaHarvest findings are not automatically BriefForge work. They may belong to MacroForge, KnowledgeForge, MetaHarvest, BriefForge, ProjectForge, or future AtlasForge.

Each major conclusion should identify its most likely EIP owner and action type.

## Improvements recommended later

### Cross-source comparison matrix

Recommended after the decision package model is specified.

Purpose:
- compare capability overlap, uniqueness, evidence mode, maturity, integration cost, adoption risk, and recommended action.

### Pattern recurrence and adoption-cluster maps

Recommended after comparison dimensions are stable.

Purpose:
- separate repeated architectural evidence from vocabulary accumulation;
- identify implementation opportunities without premature canonization.

### Static progressive disclosure

Recommended after the semantic hierarchy is validated.

Purpose:
- support executive, architect, and auditor reading paths without browser-app behavior.

### Renderer/navigation improvements

Recommended only after the decision package model proves which navigation needs remain.

Purpose:
- avoid optimizing visuals before clarifying decisions.

## Ideas rejected for this phase

### Dashboard or portal architecture

Rejected because:
- current evidence points to decision semantics, not an application shell;
- BriefForge governance forbids dashboard/portal drift absent strong evidence;
- dashboards would add complexity before proving the decision model.

### JavaScript interaction, expandable sections, sticky navigation, or search UI

Rejected because:
- progressive disclosure can first be achieved through static report hierarchy and indexes;
- interactive behavior would create runtime/browser-app pressure;
- current evidence does not prove it is the highest-priority next step.

### Visualization or graph engines

Rejected/deferred because:
- no evidence shows graph visualization is required before matrix-style comparison and recommendation indexes;
- visualization risks substituting appearance for decision quality.

### Template system

Rejected/deferred because:
- MetaHarvest needs a semantic package model before a template model;
- templates could freeze premature assumptions about report shape.

### Immediate renderer feature implementation

Rejected because:
- the user explicitly scoped this campaign as assessment only;
- existing renderer backlog already covers lower-level visual friction;
- the new evidence identifies a higher-level decision-support gap.

## Rationale

The latest MetaHarvest expansion changes the BriefForge problem from "can we render coherent reports?" to "can we make large architectural investigations actionable?"

BriefForge should evolve at the semantic/report-architecture layer first because:

- the evidence already exists but is not decision-compressed;
- current reports are coherent but require too much synthesis work;
- recommendations lack owner/priority/confidence structure;
- comparison reports are stable but not sufficiently comparative;
- renderer changes alone would not answer what to adopt, defer, or reject.

## Consequences

Accepted consequences:
- BriefForge's next workstream becomes decision-support architecture, not visual polish.
- Some future work may require package-builder or report-model changes, but none are authorized by this decision alone.
- MetaHarvest remains the evidence producer; BriefForge becomes the decision-support publisher.
- Consumer projects retain sovereignty over adoption.

Rejected consequences:
- No new runtime behavior now.
- No renderer changes now.
- No generated templates now.
- No MetaHarvest ingestion change now.
- No generated project modifications.

## Follow-up recommendation

Open a bounded next task:

`TASK-035 MetaHarvest Architectural Decision Package Model`

Purpose:
- define the model;
- validate it manually against the third-generation MetaHarvest campaign;
- prove that it reduces decision-making effort before implementing any renderer behavior.

Success test:
- a reader can identify top conclusions, owner, evidence, confidence, blockers, and next action without reading the full source corpus first.
