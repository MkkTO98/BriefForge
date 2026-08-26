# Communication Intent Status

Date: 2026-07-03
Status: KEEP EXPERIMENTAL
Owner: BriefForge

## Decision

Communication Intent remains experimental.

Do not adopt.
Do not reject.

## Evidence base

TASK-027 implemented an isolated experimental Communication Intent derivation layer.

TASK-028 implemented one isolated renderer experiment using Communication Intent and compared it against the current renderer on the TASK-023 large InsightForge report.

## Positive evidence

TASK-027 showed that Communication Intent exposes communication jobs hidden by current renderer heuristics, especially:

- comparison pressure;
- quantitative meaning;
- warning/qualification pressure;
- traceability pressure;
- long-report communication variety.

TASK-028 showed that, on one large report, a Communication Intent renderer path reduced measured branching:

| Metric | Current renderer | Communication Intent renderer |
| --- | ---: | ---: |
| Branching points | 40 | 17 |
| Source lines in compared path | 233 | 200 |
| Renderer heuristic functions | 4 | 1 |

It also improved reader-task organization through sections such as executive capsule, claim-evidence-implication flow, uncertainty/risk, evidence register, methodology/obligations, and bounded synthesis.

## Why adoption is not justified

Adoption is not justified because:

- evidence comes from one renderer experiment rather than repeated operational publications;
- the experiment still duplicates HTML assembly logic;
- intent derivation remains heuristic;
- Presentation Grammar already covers part of the same territory;
- adopting now would add architecture before operational evidence requires it.

## Why rejection is not justified

Rejection is not justified because:

- measured branching was lower in the experimental comparison;
- communication organization improved for the large report;
- the idea remains renderer-independent;
- it may later help simplify repeated renderer decisions if evidence accumulates.

## Future adoption gate

Communication Intent may be reconsidered only if repeated operational evidence shows that it:

1. reduces renderer branching or duplicated heuristics across multiple report shapes;
2. improves reader communication in human review;
3. avoids duplicated renderer assembly;
4. does not reinterpret semantic content;
5. requires no constitution, runtime, validation, promotion, Ready Package, or Presentation Grammar changes.

Until then it remains outside the canonical lifecycle.

## Lifecycle boundary

Current canonical lifecycle remains:

```text
Candidate Presentation Package
-> Validation Judgment
-> Ready Presentation Package
-> Renderer Adapter Boundary
-> Renderer output
-> Rendered Artifact Conformance
```

Communication Intent remains outside this lifecycle as experimental evidence only.
