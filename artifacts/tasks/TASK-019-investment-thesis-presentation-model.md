# TASK-019: Third Presentation Model — Investment Thesis

Date: 2026-07-02
Status: Complete

## Objective

Implement the third semantic Presentation Model: Investment Thesis.

The model is an authoring abstraction that produces the existing `CandidatePresentationPackage`. It is not a template, layout, HTML artifact, browser page, visualization, renderer, API, persistence layer, InsightForge integration, or new runtime concept.

## Scope implemented

Implemented:

- `InvestmentThesisPresentation`
- `InvestmentThesisBuilder`
- conversion to existing `CandidatePresentationPackage`
- small thesis authoring surface:
  - subject;
  - identity;
  - organizing purpose;
  - thesis statement;
  - supporting evidence;
  - risks;
  - counterarguments;
  - conclusion;
  - references;
  - obligations;
  - generic sections.

The implementation uses `PresentationPackageBuilder` internally.

## Scope excluded

No changes were made to:

- `CandidatePresentationPackage`;
- validation;
- promotion;
- `ReadyPresentationPackage`;
- renderer boundaries;
- HTML renderer;
- conformance;
- serialization.

Not introduced:

- templates;
- layout systems;
- CSS;
- JavaScript;
- browser applications;
- dashboards;
- portals;
- visualization engines;
- charts;
- maps;
- persistence;
- APIs;
- networking;
- InsightForge integration;
- MacroForge integration;
- runtime claim/evidence/risk objects;
- recommendation/advice concepts;
- constitutional changes.

## Files changed

Source:

- `src/briefforge/presentation_models.py`
- `src/briefforge/__init__.py`

Tests:

- `tests/test_investment_thesis_presentation_model.py`

Docs/state:

- `docs/investment-thesis-presentation-model.md`
- `artifacts/tasks/TASK-019-investment-thesis-presentation-model.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `state/recent_changes.md`
- `context/latest_handoff.md`

## RED evidence

Targeted RED command:

```bash
python3 -m unittest tests.test_investment_thesis_presentation_model -v
```

Result before implementation:

```text
Ran 5 tests
FAILED (errors=5)
ImportError: cannot import name 'InvestmentThesisBuilder' from 'briefforge.presentation_models'
```

This proved the Investment Thesis Presentation Model did not exist.

## GREEN evidence

Targeted GREEN command:

```bash
python3 -m unittest tests.test_investment_thesis_presentation_model -v
```

Result after implementation:

```text
Ran 5 tests in 0.025s
OK
```

Regression commands:

```bash
python3 -m unittest tests.test_real_presentation_end_to_end -v
python3 -m unittest tests.test_country_profile_presentation_model -v
python3 -m unittest tests.test_country_comparison_presentation_model -v
```

Results:

```text
TASK-014: Ran 2 tests, OK
TASK-017: Ran 5 tests, OK
TASK-018: Ran 5 tests, OK
```

Full discovery:

```bash
python3 -m unittest discover -s tests -v
```

Result:

```text
Ran 100 tests
OK
```

## Required proof coverage

1. InvestmentThesisPresentation produces a valid Candidate Presentation Package.
   - Covered by `test_investment_thesis_presentation_produces_valid_candidate_package`.

2. Complete existing pipeline passes unchanged.
   - Covered by `test_existing_pipeline_passes_unchanged_for_investment_thesis`.

3. Existing runtime abstractions require no modification.
   - Covered by `test_existing_runtime_abstractions_require_no_modification`.

4. Existing semantic fingerprints remain deterministic.
   - Covered by `test_existing_semantic_fingerprints_remain_deterministic`.

5. Existing validation, promotion, rendering, and conformance continue unchanged.
   - Covered by `test_existing_validation_promotion_rendering_and_conformance_continue_unchanged`.

## End-to-end proof

The realistic thesis was: European grid investment as a transition-bottleneck theme.

The package crossed the existing workflow:

```text
InvestmentThesisPresentation
-> PresentationPackageBuilder
-> Candidate Presentation Package
-> Validation
-> Validation Judgment
-> Ready Presentation Package
-> Renderer Adapter Boundary
-> Renderer Invocation
-> Minimal HTML Renderer
-> Rendered Artifact Conformance
```

No new workflow stages were introduced.

Deterministic semantic fingerprint:

```text
f237c2b7dc0e580c518671c274868158c3078eb998e4cc08670c1c04b100116d
```

## Architectural evaluation

### Claims

Claims mapped to existing `PresentationStatement` records with thesis-specific encounter modes.

Classification: authoring friction only.

### Supporting evidence

Supporting evidence mapped to statements plus upstream references.

Classification: authoring friction around source ownership and evidence granularity only.

### Uncertainty

Uncertainty mapped through obligations and explicit risk/counterargument statements.

Classification: authoring friction only; no runtime probability/confidence object required.

### Risks

Risks mapped to presentation statements plus obligations.

Classification: authoring friction only.

### Counterarguments

Counterarguments mapped naturally to statements related to claim, risk, and conclusion.

Classification: no architecture pressure.

### Conclusions

Conclusions mapped to bounded presentation statements. Recommendation/advice avoidance is handled by scope and obligations.

Classification: authoring friction and scope-control judgment only.

## Implementation pressure discovered

The pressure is authoring discipline, not runtime architecture:

- preventing thesis wording from becoming investment advice;
- deciding evidence/risk/counterargument granularity;
- preserving uncertainty and opposing interpretations;
- keeping source ownership explicit;
- deciding whether future thesis vocabulary should include base case, upside, downside, catalysts, or monitoring signals.

No infrastructure expansion was genuinely required.

## Implementation Readiness Assessment

GREEN.

1. Further validated assumptions:
   - Presentation Models can remain authoring-only even for claim-bearing investment presentations.
   - The existing Presentation Package represents descriptive, comparative, and investment-thesis presentations.
   - Existing validation, promotion, renderer-adapter, minimal HTML, conformance, and semantic fingerprints remain sufficient.

2. Evidence against frozen constitution:
   - None.

3. Smallest next capability:
   - Do not expand infrastructure yet. Either prove one more fundamentally different presentation model or implement bounded downstream obligation/reference visibility if reader-facing audit clarity becomes the bottleneck.

4. Presentation-driven vs infrastructure-driven development:
   - Still presentation-driven. TASK-019 added only the smallest model required by the thesis proof and did not broaden infrastructure.

## Constitutional revision decision

No constitutional revision is required.
