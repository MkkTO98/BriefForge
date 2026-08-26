# Operational Publication Workflow

Date: 2026-07-03
Status: Active workflow baseline
Owner: BriefForge

## Purpose

This document defines the standard long-term operating loop for BriefForge after completion of its first architectural validation cycle.

BriefForge now evolves through operational publication evidence, not speculative architecture.

## Standard workflow

```text
MacroForge
↓
InsightForge
↓
BriefForge Publication
↓
Human Review
↓
Renderer Backlog
↓
Evidence Threshold
↓
Renderer Improvement
```

## Stage responsibilities

### 1. MacroForge

MacroForge owns economic data construction, source evaluation, and economic analysis inputs.

BriefForge must not reinterpret MacroForge data or analysis.

### 2. InsightForge

InsightForge owns analytical synthesis, reviewed findings, research reports, and cross-source interpretation.

BriefForge must preserve source ownership and analytical boundaries.

### 3. BriefForge Publication

BriefForge converts an existing analytical artifact into:

```text
Candidate Presentation Package
-> Validation Judgment
-> Ready Presentation Package
-> Renderer output
-> Rendered Artifact Conformance
```

BriefForge owns presentation meaning and publication structure. It does not own upstream facts or analysis.

### 4. Human Review

A human reader reviews the rendered publication for communication friction:

- What is hard to understand?
- What is repeated unnecessarily?
- What evidence is too visible, too hidden, or poorly placed?
- What uncertainty is hard to find?
- What source structure was lost?
- What navigation/hierarchy problem appears?

Review should be attached to the publication evidence, usually as `reader_evaluation.md`.

### 5. Renderer Backlog

Reader friction is recorded in `artifacts/renderer_backlog.md`.

The backlog records evidence. It does not approve implementation.

### 6. Evidence Threshold

A renderer issue becomes a candidate only after repeated evidence across different real reports.

Single observations remain observations.

### 7. Renderer Improvement

Only after threshold and approval may renderer work begin.

Renderer improvements must preserve:

- constitution;
- runtime;
- validation;
- promotion;
- Ready Presentation Package;
- Presentation Grammar;
- renderer-adapter/conformance boundary.

## Operational publication artifact checklist

Each real publication should preserve:

- selected upstream artifact path or copy;
- candidate package;
- validation judgment;
- ready package;
- renderer output;
- rendered artifact conformance;
- renderer audit metadata if applicable;
- human reader evaluation;
- backlog updates if friction appears.

## Future development priority order

Future BriefForge development should prioritize:

1. Publishing real analytical work.
2. Recording reader friction.
3. Improving renderer quality.
4. Avoiding speculative infrastructure.
5. Preserving the frozen constitutional architecture unless contradicted by strong implementation evidence.

## Stop conditions

Stop and do not implement if the proposed change:

- depends on only one observation;
- requires runtime or constitutional changes;
- requires Presentation Grammar changes without strong contradictory evidence;
- adds browser application scope;
- adds dashboard/portal scope;
- adds visualization or template infrastructure;
- is motivated mainly by external design inspiration rather than BriefForge publication evidence.
