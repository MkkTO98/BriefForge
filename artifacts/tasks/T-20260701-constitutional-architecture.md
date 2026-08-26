# Task: Constitutional Architecture Design

Status: Completed
Owner: project-owned
Created: 2026-07-01
Completed: 2026-07-01

## Request

Establish the constitutional architecture of BriefForge before implementation begins.

BriefForge is envisioned as the EIP presentation engine: a future project that may transform structured information into coherent, reusable, interactive presentations while remaining independent of data ingestion, canonicalization, analysis, and research.

## Methodology slice

- Objective: Produce a comprehensive architecture-first design report and local governance record for BriefForge.
- Expected architectural uncertainty: High. Responsibility boundaries, presentation ownership, rendering ownership, browser-first/document-first posture, HTML canonicality, template philosophy, and relationships to sibling EIP projects require explicit analysis before implementation.
- Explicit non-goals: No renderer code, browser code, visualization code, APIs, templates, dashboard implementation, production functionality, or implementation task generation.
- Implementation boundary: ProjectForge scaffold plus governance/report artifacts only.
- Readiness prerequisites: ProjectForge scaffold created; ProjectForge/EIP/MetaHarvest/InsightForge/MacroForge context consulted; MetaHarvest consultation trigger evaluated.
- Success criteria: Constitutional architecture report exists; assumptions, boundaries, evidence gaps, tradeoffs, and next architectural investigation recommendations are documented; no production implementation is added.
- Verification expectations: Scaffold coherence/context checks pass; repository contains no production implementation beyond scaffold.
- Expected evidence: Report, state/handoff updates, verification command output.
- Post-slice decision: propose decision/report.

## Scope

In scope:

- Mission and purpose.
- Owned and excluded responsibilities.
- Relationships with MacroForge, InsightForge, MetaHarvest, ProjectForge, and future portal/navigation systems.
- Inputs/outputs and ownership boundaries.
- Data/rendering/presentation ownership.
- Browser-first vs document-first alternatives.
- HTML as canonical rendering target.
- Component composition, template philosophy, presentation primitives, candidate report archetypes.
- Long-term evolution strategy.
- Risks, tradeoffs, assumptions, and open evidence questions.
- MetaHarvest consultation-policy evaluation and evidence summary.

## Explicit non-scope

Out of scope:

- Production rendering engines.
- Browser interfaces.
- APIs.
- Visualization code.
- Templates beyond conceptual examples.
- Dashboards.
- Document/PDF generation.
- Implementation tasks or implementation roadmap.
- Runtime/storage/deployment selection.
- Cross-project authority changes.

## Governance links

- Related decision(s): setup decision artifacts under `artifacts/decisions/D-20260701-setup-*.md`.
- Related report(s): `artifacts/reports/R-20260701-constitutional-architecture.md`.
- Related handoff(s): `context/latest_handoff.md`.

## Outcome

Completed. BriefForge was instantiated as a ProjectForge project at `/home/mkkto/srv/EIP/projects/BriefForge`. The constitutional architecture report was produced without adding production implementation. MetaHarvest consultation was triggered by the existing policy because this is architecture definition for a new project with relevant available external architectural evidence; relevant evidence domains were identified but no adoption recommendation or implementation action was taken.

## Notes

The report is constitutional design material, not an implementation authorization. Future implementation requires a separate accepted task after the unresolved architecture questions are narrowed.
