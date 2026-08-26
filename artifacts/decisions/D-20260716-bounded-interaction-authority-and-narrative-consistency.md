# D-20260716 — Bounded Interaction Authority and Narrative Consistency

Date: 2026-07-16
Status: Accepted
Task: TASK-042

## Decision

BriefForge distinguishes four interaction classes:

1. in-publication navigation — admitted;
2. inspection/disclosure of already-present material — admitted;
3. declared/prevalidated selection among finite complete presentation states — conditionally admissible;
4. analytical recalculation and open-ended exploration — prohibited.

A declared selector is admissible only when all prerequisites in the TASK-042 semantic specification are satisfied, including:

- upstream authority for every selectable dimension/value/state;
- finite enumerated valid states rather than an open domain or implied Cartesian product;
- stable state identities and exact retained evidence bindings;
- no lookup, refresh, filtering, calculation, ranking, interpolation, or new interpretation;
- authored state projections for statements, exhibits, references, and obligations;
- independent narrative validation for every state;
- cross-state checks against stale titles, summaries, methods, values, periods, sample sizes, rankings, caveats, or provenance;
- an authority-declared default state;
- deterministic semantically complete static fallback;
- renderer preflight for all required capabilities;
- visible/auditable selected-state identity;
- offline reproducibility;
- a new semantic publication version/release when state space, default, evidence binding, narrative, or obligations change.

Failure of any prerequisite blocks selector publication. It does not block a separately valid fixed-state standalone publication.

Narrative consistency is a semantic validity concern. A renderer cannot repair an inconsistent state by inferring prominence, hiding incompatible statements, or generating a new summary.

## Rationale

TASK-041 already admits only a narrow possibility of finite authoritative prevalidated selection and rejects discovery, querying, arbitrary filtering, recomputation, and open-ended exploration. This decision converts that possibility into a fail-closed authority gate without implementing interaction.

The distinction preserves the constitutional boundary between a bounded self-contained publication and a dashboard/browser application. Navigation changes location; inspection reveals retained meaning; declared selection chooses an already-valid presentation state. None creates analytical meaning.

TASK-039 adversarial cases show why state-complete narrative validation is mandatory: changing country, date window, raw/first-difference basis, or selected relationship while retaining the same executive finding would produce false or unsupported narrative.

## Rejected alternatives

1. Treat any finite UI control as bounded.
   - Rejected: finite controls can still recompute, filter evidence, or create invalid combinations.
2. Validate only the default state.
   - Rejected: every selectable state is reader-visible publication meaning.
3. Let the renderer derive valid combinations or choose the first state.
   - Rejected: those are semantic/default authorities.
4. Treat static fallback as a screenshot or partial dump.
   - Rejected unless it is a complete prevalidated expression.
5. Allow arbitrary search/filter because data are already fixed.
   - Rejected: fixed evidence does not make unvalidated analytical selection presentation-only.

## Consequences

- No selector implementation is authorized.
- A future parameterized publication requires a semantic representation and validation specification first.
- AtlasForge embedding cannot expand available states or change defaults.
- Selection-state changes that alter meaning are semantic publication changes, not renderer-only rerenders.
- Navigation and inspection remain compatible with standalone static publication only when complete static access is preserved.

## Evidence anchors

- `CONSTITUTION.md`, Non-Goals, Ownership Boundaries, and Constitutional Exclusions.
- `artifacts/specifications/publication-boundary-intake-portability-lifecycle.md`, bounded selection and derivative-publication sections.
- `artifacts/decisions/D-20260716-derivative-publication-responsibility.md`.
- `artifacts/presentations/TASK-039-demographic-correlation-browser-report/candidate_presentation_package.json`.
- `artifacts/specifications/semantic-authority-evidence-states-interaction-renderer-fallback.md`.
