# TASK-027: Communication Intent Experimental Layer

Date: 2026-07-03
Status: Complete — KEEP EXPERIMENTAL

## Objective

Investigate whether an explicit Communication Intent layer provides a better foundation for renderer behavior than current direct renderer heuristics.

## Scope implemented

Created an isolated experimental layer:

- `src/briefforge/communication_intent_experiment.py`
- `tests/test_communication_intent_experiment.py`
- `docs/communication-intent-experimental-layer.md`
- `artifacts/reports/R-20260703-communication-intent-experimental-layer.md`

The layer derives non-canonical communication intent profiles from existing semantic packages.

## Scope preserved

Not modified:

- constitution;
- runtime;
- validation;
- promotion;
- Ready Presentation Package;
- Presentation Grammar;
- existing renderer implementation.

Not implemented:

- charts;
- browser applications;
- templates;
- CSS;
- JavaScript;
- dashboards;
- portals.

## Evidence used

BriefForge:

- TASK-017 Country Profile Presentation Model.
- TASK-018 Country Comparison Presentation Model.
- TASK-019 Investment Thesis Presentation Model.
- TASK-021 Presentation Grammar.
- TASK-023 Large Report Stress Validation.
- TASK-026 Operational Publication Trial.

MetaHarvest:

- only the Presentation Architecture domain, specifically the communication pattern library, visualization decision framework, candidate prioritization, and expansion report.

## Candidate vocabulary

Final experimental vocabulary:

- `orient`
- `summarize`
- `explain`
- `compare`
- `quantify`
- `warn`
- `qualify`
- `trace`
- `conclude`

## Evaluation result

Communication Intent adds value over direct renderer heuristics in two cases:

1. Country Comparison: current renderer treats all six statements as generic elaborate/secondary, while Intent identifies comparison, quantification, traceability, and non-ranking warning pressure.
2. Large InsightForge report: current renderer treats 23 of 32 statements as generic elaboration, while Intent exposes mixed explain, qualify, warn, quantify, summarize, trace, and conclude jobs.

It overlaps heavily with Presentation Grammar for orientation, qualification, traceability, and closing synthesis.

## Recommendation

KEEP EXPERIMENTAL.

Do not adopt as canonical architecture yet.

Do not reject yet.

Adoption requires a later bounded renderer experiment proving that consuming Communication Intent reduces renderer branching, improves labels/reading flow/traceability compression, and preserves all semantic and constitutional boundaries.

## Verification

Targeted test:

```bash
python3 -m unittest tests.test_communication_intent_experiment -v
```

Result:

```text
Ran 5 tests in 0.023s
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
Ran 131 tests in 0.052s
OK
compileall: passed
coherence: 0 block(s), 0 warning(s)
context health: 0 block(s), 0 warning(s)
```

Cleanup:

```text
removed __pycache__ directories: 3
remaining *.pyc files: 0
```

## Closeout

Standard project closeout completed under the continuity framework.

Final status:
- Complete — KEEP EXPERIMENTAL.
- No blockers.
- No pending questions.
- No incomplete acceptance criteria recorded.

Next recommended action:
- Do not adopt Communication Intent canonically without a later bounded renderer experiment proving simpler renderer branching, better labels/reading flow/traceability compression, and preserved semantic boundaries.
