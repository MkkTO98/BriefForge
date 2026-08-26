# D-20260716 — Multidimensional Statement Authority and Explicit State Semantics

Date: 2026-07-16
Status: Accepted
Task: TASK-042

## Decision

BriefForge accepts a multidimensional semantic model for presentation statements. Statement role, scoped authority/provenance, communication function, encounter/composition relations, attention, evidence state, value state, consistency state, lifecycle references, and presentation obligations are independent dimensions.

BriefForge rejects a universal statement `type`, encounter `mode`, or general `status` that collapses these responsibilities.

The semantic postures that must remain distinguishable are observation, reusable evidence, accepted finding, interpretation, hypothesis, scenario, recommendation, uncertainty, caveat, and personal annotation. These postures may coexist; they are not forced into one mutually exclusive representation vocabulary.

Evidence state, value state, consistency state, and lifecycle state are separately scoped:

- evidence distinguishes availability, integrity, upstream acceptance, review, freshness, and active-use declarations;
- value distinguishes present, explicit zero, missing, unavailable, not applicable, suppressed, unresolved, and invalid;
- consistency distinguishes consistent, conflicting, unresolved/indeterminate, invalid under a named contract, and not checked;
- upstream evidence, Candidate/Judgment/Ready, publication release, generated artifact, and manifest lifecycles remain independent.

BriefForge may author framing and faithful presentation synthesis but cannot increase upstream claim strength, resolve disagreement, create ranking, infer causation, or grant evidence/finding status.

Communication Intent's orient/summarize/explain/compare/quantify/warn/qualify/trace/conclude distinction is accepted as semantic evidence, but its heuristic derivation remains non-canonical and receives no validation or authority role.

Encounter semantics are confined to target-independent ordering, grouping, hierarchy, co-encounter/proximity, and bounded path relations. They do not encode content role, evidential support, causality, confidence, or authority.

## Rationale

- `CONSTITUTION.md`, Core Conceptual Model, separates Presentation Statements, Composition Semantics, Encounter Semantics, and Validation Obligations.
- `src/briefforge/runtime.py` exposes the existing bounded statement/reference/obligation evidence but its single `EncounterSemantics.mode` cannot carry the complete accepted distinction.
- TASK-039 uses `orientation`, `conclusion`, `methodology`, `finding`, `evidence`, `caveat`, and `provenance` as encounter modes, demonstrating semantic overloading.
- ADPM requires findings, recommendations, confidence, uncertainty, risks, counterarguments, and evidence without transferring analytical authority to BriefForge.
- TASK-041 separates requestor, exporter, upstream authority, BriefForge readiness, release, renderer, artifact, and manifest responsibilities.
- A single status would conflate zero/missing, conflict/invalidity, stale/withdrawn, and Ready/publication status.

## Rejected alternatives

1. One enum for all statement roles.
   - Rejected because a recommendation may also carry uncertainty and caveats, and role does not determine authority or communication function.
2. Reuse `EncounterSemantics.mode` as the canonical taxonomy.
   - Rejected because encounter is relational while current values mix role and communication purpose.
3. Promote heuristic Communication Intent derivation into readiness authority.
   - Rejected because keyword inference can misclassify role, authority, and narrative importance.
4. One missing/error/status vocabulary.
   - Rejected because absence, zero, suppression, invalidity, conflict, staleness, and withdrawal have different owners and consequences.
5. Let BriefForge resolve conflicting upstream evidence.
   - Rejected as analytical authority expansion.

## Consequences

- Future representation planning must encode independent dimensions without choosing a transport format first.
- Composite statements with materially different authority, state, or obligations must be split.
- Superlatives/rankings require upstream comparison-universe and selection provenance.
- Personal annotations must remain attributed and non-authoritative.
- Structured disagreement can be valid; undeclared contradiction cannot.
- No runtime, schema, validator, renderer, or fixture change is authorized by this decision.

## Evidence anchors

- `CONSTITUTION.md`, Core Conceptual Model and Ownership Boundaries.
- `artifacts/specifications/architectural-decision-package-model.md`.
- `artifacts/specifications/publication-boundary-intake-portability-lifecycle.md`.
- `docs/presentation-grammar-specification.md`.
- `docs/communication-intent-experimental-layer.md`.
- `src/briefforge/runtime.py` (`PresentationStatement`, `EncounterSemantics`, `UpstreamReference`, `PresentationObligation`).
- `artifacts/presentations/TASK-039-demographic-correlation-browser-report/candidate_presentation_package.json`.
- `artifacts/specifications/semantic-authority-evidence-states-interaction-renderer-fallback.md`.
