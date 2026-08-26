# TASK-028: Communication Intent Renderer Experiment

Date: 2026-07-03
Status: Complete — KEEP EXPERIMENTAL

## Objective

Determine whether the experimental Communication Intent layer measurably simplifies renderer behavior compared with the current static HTML renderer heuristics.

## Selected publication

Selected publication:

- TASK-023 large InsightForge report.

Rationale:

- It is the strongest existing stress case for renderer organization.
- It contains 32 statements, 5 references, and 4 obligations.
- TASK-027 found the clearest large-report signal that current renderer heuristics collapse too much content into generic elaboration.

## Scope implemented

Created one isolated renderer variant:

- `src/briefforge/communication_intent_renderer_experiment.py`

Created tests:

- `tests/test_communication_intent_renderer_experiment.py`

Generated comparison artifacts:

- `artifacts/presentations/TASK-028-communication-intent-renderer-experiment/communication_intent_html_artifact.html`
- `artifacts/presentations/TASK-028-communication-intent-renderer-experiment/side_by_side_comparison.json`
- `artifacts/presentations/TASK-028-communication-intent-renderer-experiment/side_by_side_comparison.md`

Produced report:

- `artifacts/reports/R-20260703-communication-intent-renderer-experiment.md`

## Scope preserved

Not modified:

- constitution;
- runtime;
- validation;
- promotion;
- Presentation Package;
- Presentation Grammar;
- existing renderer behavior.

Not implemented:

- browser application;
- templates;
- CSS framework;
- JavaScript;
- dashboard;
- portal;
- visualization engine;
- charts/maps/timelines as new capabilities.

## Renderer A vs Renderer B

Renderer A:

- existing `render_minimal_html`;
- bases presentation decisions on encounter mode, risk/caveat string checks, obligation IDs, and long-document threshold.

Renderer B:

- new `render_communication_intent_html`;
- derives a Communication Intent profile and groups content into reader-task sections:
  1. Executive capsule.
  2. Claim-evidence-implication flow.
  3. Uncertainty and risk.
  4. Evidence register.
  5. Methodology and obligations.
  6. Bounded synthesis.

## Complexity comparison

Measured compared renderer path:

| Metric | Renderer A current | Renderer B intent experiment |
| --- | ---: | ---: |
| Branching points | 40 | 17 |
| Source lines in compared path | 233 | 200 |
| Renderer heuristic functions | 4 | 1 |

Interpretation:

- Communication Intent reduces measured branching in the compared renderer decision path.
- It makes section organization more declarative.
- It does not eliminate HTML assembly complexity and still duplicates enough rendering structure to prevent immediate adoption.

## Communication comparison

Renderer B improves:

- readability through reader-task section labels;
- section organization via harvested Presentation Architecture patterns;
- evidence placement by keeping links near claims and preserving an evidence register;
- obligation placement by grouping obligations by reader task and preserving the obligation register;
- uncertainty placement by explicitly elevating qualify/warn content;
- traceability by preserving package identity, semantic fingerprint, validation policy, statement IDs, references, and obligations.

Renderer B does not improve:

- visual polish;
- chart/table/map/timeline capability;
- audit identity beyond existing renderer conformance;
- generality beyond this one large-report experiment.

## MetaHarvest consultation

Consulted only the specialized Presentation Architecture domain:

- Communication Pattern Library.
- Visualization Decision Framework.

Alignment result:

- Renderer B aligns better with P-01 Executive Capsule, P-02 Claim-Evidence-Implication, P-04 Evidence Register, P-05 Methodology Disclosure, P-06 Uncertainty and Risk, and P-03 Progressive Disclosure.
- The Visualization Decision Framework did not justify new visuals for this experiment. The task questions are mostly answer/evidence/uncertainty/traceability questions, so static text plus evidence/register blocks are appropriate.

## Recommendation

KEEP EXPERIMENTAL.

Do not adopt yet.
Do not reject yet.

Evidence for keeping:

- measured branching reduction from 40 to 17 in the compared path;
- clearer reader-task organization;
- stronger alignment with MetaHarvest Presentation Architecture evidence.

Evidence against adoption now:

- still duplicates HTML assembly logic;
- intent derivation remains heuristic;
- evidence comes from one large-report publication only;
- adoption would require a later extraction/refactor decision, not a second production renderer.

Future rejection gate:

- If a second publication experiment cannot preserve branching reduction and communication improvement without duplicated renderer assembly, reject Communication Intent from future renderer architecture consideration.

## Verification

RED:

```bash
python3 -m unittest tests.test_communication_intent_renderer_experiment -v
```

Initial result before implementation:

```text
FAILED (errors=4)
```

Expected reason:

- `briefforge.communication_intent_renderer_experiment` did not exist.

GREEN targeted result:

```text
Ran 5 tests in 0.061s
OK
```

Full verification:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests tools
python3 tools/check_coherence.py
python3 tools/context_health.py
```

Result:

```text
Ran 136 tests in 0.093s
OK
compileall: passed
coherence: 0 block(s), 0 warning(s)
context health: 0 block(s), 0 warning(s)
```
