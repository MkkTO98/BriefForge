# Communication Intent Experimental Layer

Date: 2026-07-03
Status: Experimental, non-canonical

## Purpose

The Communication Intent layer investigates whether BriefForge can express communication decisions independently of semantic meaning and rendering technology.

It sits conceptually after existing semantic content and before any target-specific renderer decision:

```text
Candidate or Ready Presentation Package semantics
-> experimental Communication Intent derivation
-> future renderer-specific expression, if later justified
```

This is not a new runtime concept. It is not part of validation, promotion, readiness, Presentation Grammar, or renderer conformance.

## Boundary

The layer may:

- read existing package identity, organizing purpose, statements, encounter semantics, references, and obligations;
- derive non-canonical intent annotations;
- explain communication strategy in renderer-independent language;
- support experimental comparison against current renderer heuristics.

The layer may not:

- mutate Presentation Packages;
- add fields to runtime dataclasses;
- affect validation or promotion;
- affect semantic fingerprints;
- render HTML or any other target;
- choose charts, maps, CSS, JavaScript, templates, dashboards, portals, or browser applications;
- become constitutional authority.

## Vocabulary

Experimental v0.1 vocabulary:

1. `orient`
2. `summarize`
3. `explain`
4. `compare`
5. `quantify`
6. `warn`
7. `qualify`
8. `trace`
9. `conclude`

## Strategy mapping

| Intent | Strategy |
|---|---|
| `orient` | Establish reader question, subject, scope, non-scope, source owner, and why the presentation exists. |
| `summarize` | Provide an executive capsule before supporting material. |
| `explain` | Connect claim, evidence, reasoning, and implication. |
| `compare` | Keep comparison basis, comparable entities, dimensions, units, and caveats visible. |
| `quantify` | Preserve metric meaning: unit, geography, time period, source, definition, and numeric status. |
| `warn` | Surface interpretation hazards early enough to prevent misuse. |
| `qualify` | Attach caveats, uncertainty, risk, counterargument, assumptions, confidence, and boundaries to affected claims. |
| `trace` | Keep source ownership, references, obligations, and audit identity inspectable without overwhelming first reading. |
| `conclude` | Close with bounded synthesis without increasing claim strength. |

## Experimental API

Implemented in:

- `src/briefforge/communication_intent_experiment.py`

Primary functions:

- `derive_communication_intent_profile(package)`
- `intent_strategy_mapping()`
- `strategy_for_intent(intent)`

Primary dataclasses:

- `StatementCommunicationIntent`
- `PackageCommunicationIntentProfile`

The API accepts either a `CandidatePresentationPackage` or an object with a `candidate` attribute, such as `ReadyPresentationPackage`.

## Current verdict

Keep experimental.

The layer is useful enough not to reject: it distinguishes communication jobs that the current renderer collapses into broad grammar stages. It is not proven enough to adopt: no renderer has yet been simplified by consuming it, and the derivation remains heuristic.
