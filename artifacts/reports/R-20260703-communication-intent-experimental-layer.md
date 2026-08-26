# TASK-027 Communication Intent Experimental Report

Date: 2026-07-03
Status: Complete — recommendation: KEEP EXPERIMENTAL

## Objective

Investigate whether an explicit Communication Intent layer provides a better foundation for future renderer behavior than direct renderer heuristics.

This task implemented the layer as an isolated experiment only. It does not change the frozen constitution, runtime model, validation, promotion, Ready Presentation Package, Presentation Grammar, or existing renderer.

## Scope boundary

Modified:

- `src/briefforge/communication_intent_experiment.py`
- `tests/test_communication_intent_experiment.py`
- `docs/communication-intent-experimental-layer.md`
- this report and task closeout artifacts

Not modified:

- `CONSTITUTION.md`
- `src/briefforge/runtime.py`
- `src/briefforge/validation.py`
- `src/briefforge/promotion.py`
- `src/briefforge/renderer_adapter.py`
- `docs/presentation-grammar-specification.md`
- existing renderer implementation
- BriefForge Presentation Package / Ready Presentation Package semantics

Not implemented:

- charts
- browser applications
- templates
- CSS
- JavaScript
- dashboards
- portals
- renderer replacement

## Evidence consulted

BriefForge evidence:

- Country Profile Presentation Model, TASK-017.
- Country Comparison Presentation Model, TASK-018.
- Investment Thesis Presentation Model, TASK-019.
- TASK-021 Presentation Grammar.
- TASK-023 Large Report Stress Validation.
- TASK-026 Operational Publication Trial.

MetaHarvest consultation was intentionally limited to the new Presentation Architecture domain:

- `presentation_architecture/communication_pattern_library.md`
- `presentation_architecture/visualization_decision_framework.md`
- `presentation_architecture/candidate_prioritization.md`
- `reports/R-20260703-presentation-architecture-expansion.md`

No unrelated MetaHarvest domains were consulted for this task.

## Experimental implementation

Created `src/briefforge/communication_intent_experiment.py` as a separate non-canonical layer.

The layer reads an existing `CandidatePresentationPackage` or an object with a `candidate` attribute, such as `ReadyPresentationPackage`, and derives a `PackageCommunicationIntentProfile`.

The profile contains:

- package id;
- vocabulary version;
- experimental layer status;
- package-level intents;
- statement-level intent annotations;
- evidence basis explaining why an intent was derived;
- communication strategy for the primary intent.

The layer does not write back into the package. It does not affect validation, promotion, rendering, conformance, or semantic fingerprinting.

## Candidate intent vocabulary

Final experimental vocabulary:

| Intent | Meaning | Source basis |
|---|---|---|
| `orient` | Establish reader question, subject, scope, non-scope, and source owner. | Presentation Grammar orientation; Wikipedia lead; GOV.UK user-need framing. |
| `summarize` | Give the main point or executive capsule before detail. | Presentation Grammar primary semantic point; MetaHarvest Executive Capsule Pattern. |
| `explain` | Connect claim, evidence, reasoning, and implication. | TASK-021 elaboration; MetaHarvest Claim-Evidence-Implication Pattern. |
| `compare` | Communicate similarities, differences, tradeoffs, and comparison basis. | Country Comparison model; MetaHarvest Comparison Matrix Pattern. |
| `quantify` | Preserve metric meaning, unit, time period, source, definition, and numeric status. | Country Profile/Comparison; TASK-026 table-heavy publication; MetaHarvest evidence register and decision framework. |
| `warn` | Prevent misuse or over-interpretation. | Obligations, non-advice constraints, no-ranking constraints, GOV.UK/Carbon warning/status patterns. |
| `qualify` | Attach caveats, uncertainty, risks, counterarguments, assumptions, confidence, and boundaries. | TASK-021 uncertainty grammar; TASK-023 caveat/failure-mode pressure; MetaHarvest Uncertainty and Risk Pattern. |
| `trace` | Keep evidence, references, obligations, ownership, and audit identity inspectable. | BriefForge constitutional traceability; MetaHarvest Evidence Register Pattern. |
| `conclude` | Close with bounded synthesis or decision-relevant takeaway without increasing claim strength. | Presentation Grammar close; consulting and institutional executive synthesis patterns. |

Rejected as separate first-class intents for now:

- `navigate`: valuable, but currently better treated as a strategy supporting `orient`, `trace`, and long-document reading flow.
- `visualize`: not an intent; it is a possible downstream form-selection result.
- `rank`: too specific; currently fits under `compare` plus `quantify` and should only split out after more ranking-heavy evidence.
- `methodologize`: useful but too awkward as vocabulary; currently covered by `trace`, `qualify`, and `explain`.

## Mapping from Presentation Grammar to Communication Intent

| Presentation Grammar concept | Communication Intent mapping | Notes |
|---|---|---|
| Orientation | `orient` | Direct mapping. |
| Primary semantic claim or summary | `summarize`, sometimes `conclude` | Grammar says where/priority; intent says what the statement is trying to do. |
| Structured elaboration | `explain`, `compare`, `quantify` | Intent separates different kinds of elaboration that current renderer heuristics often collapse. |
| Evidence and traceability | `trace` | Direct mapping, strengthened by MetaHarvest Evidence Register Pattern. |
| Caveats, uncertainty, obligations | `qualify`, `warn` | Intent separates normal uncertainty qualification from misuse-prevention warnings. |
| Closing synthesis | `conclude` | Direct mapping. |
| Reader attention: primary | Usually `orient`, `summarize`, or `conclude` | Attention is priority; intent is communicative function. |
| Reader attention: secondary | Often `explain`, `compare`, or `quantify` | Secondary material can have different intents. |
| Reader attention: supporting | Often `trace`, `qualify`, or `warn` | Supporting is not equivalent to low importance. |
| Discoverable on demand | Usually `trace` | Trace should be available without dominating the first reading path. |
| Narrative: Orient -> State -> Elaborate -> Qualify -> Trace -> Close | `orient` -> `summarize` -> `explain`/`compare`/`quantify` -> `qualify`/`warn` -> `trace` -> `conclude` | Intent vocabulary is a more granular explanation of why a grammar stage exists. |

Conclusion: Communication Intent partially duplicates the Presentation Grammar but adds useful granularity where Grammar stages are too broad for renderer guidance.

## Mapping from Communication Intent to communication strategies

These are communication strategies, not renderer implementations.

| Intent | Communication strategy |
|---|---|
| `orient` | Establish the reader question, subject, scope, non-scope, source owner, and why the presentation exists before details. |
| `summarize` | Provide an executive capsule: main point, bounded implication, and confidence/uncertainty marker before supporting material. |
| `explain` | Use claim-evidence-implication sequencing so the reader can connect a statement to its reason and consequence. |
| `compare` | Keep comparison basis, comparable entities, dimensions, units, and non-comparability caveats visible. |
| `quantify` | Preserve exact metric meaning: unit, geography, time period, source, definition, and whether numbers are observed, approximate, forecast, or scenario. |
| `warn` | Surface interpretation hazards early enough to prevent misuse: non-advice, non-ranking, source limits, stale data, or missing evidence. |
| `qualify` | Attach uncertainty, risk, caveat, counterargument, assumption, confidence, or status context to the affected claim rather than burying it later. |
| `trace` | Maintain an evidence register: source ownership, references, obligations, and audit identity remain inspectable without overwhelming first reading. |
| `conclude` | Close with bounded synthesis that states what the reader should take away without increasing claim strength beyond package evidence. |

## Comparative evaluation against current renderer heuristics

Current renderer behavior uses direct mode-to-stage and mode-to-attention heuristics:

- `orientation` -> state-main-point / primary.
- `synthesis` or `conclusion` -> close / primary.
- modes containing `risk`, `caveat`, or `counter` -> qualify / supporting.
- otherwise -> elaborate / secondary.

This is simple and constitutionally safe, but it loses communication distinctions.

### Evaluation sample results

| Sample | Statements | Communication Intent result | Current renderer heuristic result | Finding |
|---|---:|---|---|---|
| Country Profile | 6 | Detected `orient`, `quantify`, `qualify`, `trace`, `explain`, `compare`, `warn`, `conclude`. Primary intents distribute across orientation, metrics, warning, explanation, and conclusion. | 1 state-main-point, 3 elaborate, 1 qualify, 1 close; attention: 2 primary, 3 secondary, 1 supporting. | Current heuristic is adequate but cannot explain why numeric/profile/source-limited statements need different strategies. |
| Country Comparison | 6 | Detected `compare` across all statements, with `quantify`, `trace`, `explain`, and non-ranking warning support. | All 6 statements become elaborate/secondary. | Strongest evidence for Intent: current renderer collapses comparison into generic elaboration. |
| Investment Thesis | 5 | Detected `warn`, `qualify`, `trace`, `explain`, `conclude`, and non-advice pressure. | 2 elaborate, 2 qualify, 1 close; attention: 3 secondary, 2 supporting. | Intent gives better guidance for non-advice warnings and bounded thesis conclusion, but overlaps heavily with Grammar. |
| Large InsightForge report | 32 | Detected broad intent mix: `orient`, `compare`, `quantify`, `qualify`, `trace`, `explain`, `warn`, `conclude`, `summarize`. | 1 state-main-point, 23 elaborate, 7 qualify, 1 close; attention: 2 primary, 23 secondary, 7 supporting. | Intent exposes why long-report reading flow degrades: too many different communication jobs are hidden under generic elaboration. |

### Does Communication Intent reduce renderer complexity?

Potentially yes, but not proven enough for adoption.

The current renderer embeds communication judgments directly in helper functions such as statement attention, statement stage, uncertainty grouping, and long-document outline. A future renderer could be simpler if it consumed pre-derived intent guidance instead of re-inferring the same distinctions from encounter modes, text, references, and obligations.

However, the current experimental derivation is heuristic and sometimes over-detects. Example: Country Profile picks up comparison/warning signals from language and obligations even though the profile is not fundamentally a comparison presentation. That is acceptable for an experiment but not safe enough as canonical architecture.

### Does it improve visualization decisions?

Yes as a decision layer, not as implementation.

MetaHarvest Presentation Architecture says form should follow reader question. Communication Intent expresses the reader question before any renderer chooses a form:

- `compare` asks for comparison basis and comparable dimensions.
- `quantify` asks for precise metric semantics.
- `qualify` asks for uncertainty and caveat proximity.
- `trace` asks for evidence/audit accessibility.

This improves future form-selection reasoning without adding chart, map, table, template, or browser infrastructure now.

### Does it improve reading flow?

Likely yes.

TASK-023 and TASK-026 show that the current renderer's recurring weaknesses are generic display headings, source-structure flattening, repeated traceability noise, caveat density, and long-document fatigue. Intent separates the communication jobs behind those weaknesses. In particular, the large report had 23 statements treated as generic renderer elaboration, while Intent identified explain, qualify, warn, quantify, summarize, and conclude pressure inside that mass.

### Does it improve future renderer independence?

Yes.

Communication Intent is renderer-independent and does not choose HTML, CSS, components, templates, charts, maps, dashboards, or portals. It can guide a static HTML renderer, terminal renderer, slide renderer, document renderer, or future browser report renderer without becoming the renderer.

### Does it merely duplicate Presentation Grammar?

No, but it overlaps substantially.

Presentation Grammar already defines the narrative skeleton and attention hierarchy. Communication Intent adds a thinner layer that says why a statement needs a communication treatment. The useful distinction is:

```text
Presentation Grammar = communication order and priority
Communication Intent = communication job of each semantic unit
Renderer = target-specific expression
```

The overlap is high enough that adoption would be premature. The differentiation is strong enough that outright rejection would also be premature.

## Architectural recommendation

Recommendation: KEEP EXPERIMENTAL.

Do not adopt Communication Intent as canonical architecture yet.

Rationale:

1. It demonstrably unifies existing Presentation Grammar with MetaHarvest Presentation Architecture evidence at the vocabulary level.
2. It exposes communication distinctions hidden by current direct renderer heuristics, especially for Country Comparison and large reports.
3. It gives a plausible future way to simplify renderer decisions by moving intent derivation out of renderer implementation.
4. It remains renderer-independent and does not modify the frozen constitution/runtime boundary.
5. But the implementation evidence is still only a separate heuristic derivation plus tests. It has not yet proven that an actual renderer becomes simpler or better when consuming intent.
6. Some over-detection remains, so canonical adoption would risk adding a noisy abstraction.

Reject only if future renderer trials show that Presentation Grammar plus encounter semantics are sufficient and Communication Intent adds no measurable simplification.

Adopt only if a future bounded renderer experiment proves:

- less renderer-specific branching;
- better section labels and reading flow;
- cleaner traceability/obligation compression decisions;
- no semantic reinterpretation;
- no runtime/constitution changes;
- less complexity than direct renderer heuristics.

## Success criterion assessment

The success criterion is partially satisfied but not enough for adoption.

Communication Intent does unify existing Presentation Grammar and MetaHarvest communication evidence, and it appears to simplify future renderer decision reasoning. But it has not yet demonstrated simplification inside a real renderer implementation. Therefore the correct architectural decision is `KEEP EXPERIMENTAL`, not `ADOPT`.

## Verification

Targeted test:

```text
python3 -m unittest tests.test_communication_intent_experiment -v
Ran 5 tests in 0.023s
OK
```

Full verification:

```text
python3 -m unittest discover -s tests -v
Ran 131 tests in 0.052s
OK

python3 -m compileall -q src tests tools
OK

python3 tools/check_coherence.py
coherence: 0 block(s), 0 warning(s)

python3 tools/context_health.py
context health: 0 block(s), 0 warning(s)
```

Generated cache cleanup:

```text
removed __pycache__ directories: 3
remaining *.pyc files: 0
```
