# Communication Intent Renderer Experiment

Date: 2026-07-03
Status: Experimental comparison complete
Recommendation: KEEP EXPERIMENTAL

## Summary

TASK-028 implemented one isolated static HTML renderer variant that consumes the TASK-027 Communication Intent profile instead of the current renderer's direct heuristics.

This is not an adoption. It is a comparison artifact.

## Files

- Renderer experiment: `src/briefforge/communication_intent_renderer_experiment.py`
- Tests: `tests/test_communication_intent_renderer_experiment.py`
- HTML output: `artifacts/presentations/TASK-028-communication-intent-renderer-experiment/communication_intent_html_artifact.html`
- Side-by-side JSON: `artifacts/presentations/TASK-028-communication-intent-renderer-experiment/side_by_side_comparison.json`
- Side-by-side report: `artifacts/presentations/TASK-028-communication-intent-renderer-experiment/side_by_side_comparison.md`

## Experimental renderer behavior

The renderer derives Communication Intent from the Ready Presentation Package and organizes the static HTML into reader-task sections:

1. Executive capsule.
2. Claim-evidence-implication flow.
3. Uncertainty and risk.
4. Evidence register.
5. Methodology and obligations.
6. Bounded synthesis.

It preserves:

- package identity;
- semantic fingerprint;
- validation policy;
- statement IDs;
- reference IDs;
- obligation IDs.

It does not validate, promote, canonicalize, reinterpret, persist, serve, script, style, template, chart, map, dashboard, portal, or replace the current renderer.

## Complexity result

| Metric | Current renderer | Communication Intent renderer |
| --- | ---: | ---: |
| Branching points | 40 | 17 |
| Source lines in compared path | 233 | 200 |
| Renderer heuristic functions | 4 | 1 |

Communication Intent reduces measured renderer branching for the TASK-023 large-report path.

## Communication result

Communication Intent improves:

- section organization;
- evidence placement;
- obligation placement;
- uncertainty placement;
- reader-task labeling;
- alignment with MetaHarvest Presentation Architecture evidence.

It does not improve visual polish and does not add visualization capability.

## MetaHarvest evidence alignment

Consulted only:

- Communication Pattern Library.
- Visualization Decision Framework.

Renderer B aligns with:

- Executive Capsule Pattern;
- Claim-Evidence-Implication Pattern;
- Evidence Register Pattern;
- Methodology Disclosure Pattern;
- Uncertainty and Risk Pattern;
- Progressive Disclosure Pattern.

The Visualization Decision Framework does not justify new charts/maps/tables here. The relevant reader questions are conclusion, support, uncertainty, and traceability questions, so static text and evidence/register blocks are sufficient for this experiment.

## Recommendation

KEEP EXPERIMENTAL.

Reason:

- The experiment shows real simplification and communication improvement for one large report.
- But the renderer still duplicates HTML assembly logic and depends on heuristic intent derivation.
- One publication is not enough to adopt into the production renderer.

Adoption would require a later refactor proving Communication Intent can simplify the existing renderer without creating a parallel renderer path.

Rejection should occur if a second publication experiment fails to preserve branching reduction and communication improvement without duplicated output assembly.
