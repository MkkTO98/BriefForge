# TASK-033 — Static SVG Time-Series Exhibit Proof

Status: complete
Date: 2026-07-03
Scope: renderer-only static SVG time-series proof

## Objective

Determine whether one bounded renderer-side static SVG time-series exhibit materially improves communication while preserving BriefForge's frozen architecture and evidence-driven development method.

## Result

Decision: Keep Experimental.

The proof demonstrates material communication value for one real time-series dataset, but recurrence is not yet strong enough for broad adoption.

## Implemented scope

Exactly one visualization class was implemented:

- static SVG time-series line exhibit.

The renderer emits this exhibit only when existing source evidence already provides:

- a Markdown-like source table;
- a `Period` column;
- a numeric `Value` column;
- at least three periods;
- stable non-temporal dimensions, so the table represents one series.

If those conditions are not met, no SVG chart is generated.

## Excluded scope

No changes to:

- constitution;
- runtime;
- Presentation Package;
- validation;
- promotion;
- Presentation Grammar;
- Presentation Models;
- adapter contract.

No implementation of:

- generic chart library;
- multiple chart types;
- interactive graphics;
- JavaScript;
- browser application;
- dashboard;
- portal;
- visualization engine;
- runtime visualization object;
- renderer registry;
- map.

## Evaluation dataset

Selected real source evidence:

- `/home/mkkto/srv/EIP/projects/MacroForge/data/processed/bls_labor_core_operational/bls-labor-core-operational-normalized.json`

Selected series:

- BLS `LNS14000000`
- unemployment rate, civilian labor force, seasonally adjusted
- United States
- 2024 monthly observations

Why not TASK-026 GDP for SVG:

- TASK-026 GDP is useful table/comparison evidence.
- It does not contain a clean single-series table with at least three periods.
- Presentation Architecture evidence warns against line charts when only two periods or categorical comparison matter.

## RED / GREEN evidence

RED:

- `python3 -m unittest tests.test_static_svg_time_series_exhibit -v`
- Failed because the renderer produced no `data-exhibit-type="time-series-svg"` and no static SVG line chart.

GREEN:

- `python3 -m unittest tests.test_static_svg_time_series_exhibit -v`
- Passed after adding renderer-only static SVG time-series rendering.

## Measured proof output

TASK-033 after publication:

- static SVG time-series exhibits: 1
- SVG elements: 1
- polyline elements: 1
- conformance: true
- JavaScript: absent
- event handlers: absent
- canvas: absent
- chart-library terms: absent

Controls:

- TASK-023 large narrative report receives no SVG chart.
- TASK-026 GDP operational publication receives no SVG chart because the source table is mixed-source/mixed-series and insufficient for a single-series time-series line.

## MetaHarvest consultation

Used only Presentation Architecture evidence:

- Visualization Decision Framework: line charts are appropriate when time continuity, trends, inflection points, cycles, or paths are central.
- Communication Pattern Library P-08 Trend Pattern: requires time range, movement, source, and unit.
- Presentation Architecture caution: a trend can be communicated in many forms; chart type must follow reader task and evidence structure.

TASK-033 aligns because it uses SVG only for a genuine 12-period monthly source table and refuses unsuitable controls.

## Reader evaluation

The static SVG improves:

- comprehension of movement over time;
- first-pass reading speed;
- information density;
- evidence clarity;
- publication quality for temporal evidence.

It is not decorative because the reader task is temporal.

## Renderer complexity assessment

Complexity increase is moderate but bounded:

- source table parsing reuse;
- period parsing for year/month/quarter/year forms;
- single-series eligibility checks;
- one static SVG renderer.

This remains simpler than a visualization framework because there is no chart specification language, registry, dependency, interactive lifecycle, or runtime model.

## Backlog update

Added RB-009 as Experimental:

- `artifacts/renderer_backlog.md`

## Recommendation

Keep Experimental.

Use the implementation as the reference proof for future renderer-side exhibit experiments, but do not treat it as the start of generalized charting.

Next milestone:

- run one more operational publication trial with naturally time-series economic evidence;
- if repeated evidence confirms value, consider promoting static SVG time-series exhibits from Experimental to Partially Implemented.
