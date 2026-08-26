# Decision: Bounded Derivative Publication Responsibility

Date: 2026-07-16
Status: accepted architectural clarification; no constitutional amendment or implementation authorized
Scope: TASK-041

## Decision

Existing doctrine is sufficient when read by responsibility and authority:

- BriefForge does not own a rendering engine, browser application, visualization grammar, dashboard, portal, or generic UI/template platform as constitutional architecture.
- BriefForge may contain or invoke separately approved bounded renderer adapters that generate deterministic, standalone, non-canonical publication artifacts from exact Ready Presentation Packages.
- Those derivative capabilities gain no evidentiary, analytical, presentation-validation, promotion, or publication authority.

Permitted derivative publication behaviour is limited to:

- standalone generated documents;
- deterministic layout and formatting;
- stable internal navigation and anchors;
- native disclosure/inspection;
- bounded static exhibits;
- scoped styles;
- print-safe or accessible derivative forms;
- renderer-local mechanics that preserve meaning and obligations.

Prohibited application/platform behaviour includes:

- persistent application state;
- analytical recomputation;
- arbitrary filtering, querying, comparison, or exploration;
- dashboards;
- routing systems and cross-report portal navigation;
- global search/discovery/ranking;
- visualization engines or grammars;
- component/template platforms;
- live entity and continuously updated company pages.

Declared/prevalidated selection is neither permitted nor prohibited by this decision; it remains deferred until the later semantic-authority task proves its finite state space, narrative validity, evidence preservation, and deterministic fallback.

## Evidence

- `CONSTITUTION.md`, Project identity, Frozen constitutional architecture, Explicit non-scope, Operating principles, and Implementation bridge.
- `docs/renderer-adapter-boundary.md` keeps renderers read-only and post-Ready.
- `docs/rendered-artifact-conformance.md` keeps outputs non-canonical and audit-linked.
- `docs/renderer-improvement-policy.md` and `docs/renderer-backlog-specification.md` prohibit speculative browser/application/platform evolution.
- TASK-039 proves a standalone HTML publication without browser-app state, recomputation, or renderer redesign.

## Constitutional verdict

No amendment is necessary. The literal phrase `rendering engines` remains awkward against local renderer implementation names, but the constitution consistently speaks in terms of owned constitutional responsibilities and explicitly permits concrete downstream representations through the implementation bridge. This decision supplies the narrow responsibility clarification without changing the frozen core or weakening any exclusion.

A constitutional amendment should be reconsidered only if later evidence shows that this responsibility interpretation cannot prevent scope leakage or cannot explain an approved bounded publication capability. Renderer attractiveness or convenience is insufficient.

## Non-authorization

This decision does not authorize JavaScript interaction, selectors, renderer changes, new artifact formats, template/component systems, browser applications, AtlasForge work, or any implementation.
