# TASK-017: First Presentation Model — Country Profile

Date: 2026-07-02
Status: Complete

## Objective

Implement the first semantic Presentation Model: Country Profile.

The model is an authoring abstraction that produces the existing `CandidatePresentationPackage`. It is not a template, renderer, browser page, HTML artifact, layout, visualization, export, API, persistence layer, or new runtime concept.

## Scope implemented

Implemented:

- `CountryProfilePresentation`
- `CountryProfileBuilder`
- conversion to existing `CandidatePresentationPackage`
- small country-profile authoring surface:
  - identity;
  - organizing purpose;
  - overview;
  - economy;
  - demographics;
  - references;
  - obligations;
  - generic section for deliberately small additional country-profile themes.

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
- layout;
- browser application;
- CSS;
- JavaScript;
- visualization;
- charts;
- maps;
- PDF;
- exports;
- persistence;
- APIs;
- networking;
- InsightForge integration;
- runtime relationship abstractions;
- constitutional changes.

## Files changed

Source:

- `src/briefforge/presentation_models.py`
- `src/briefforge/__init__.py`

Tests:

- `tests/test_country_profile_presentation_model.py`
- `tests/test_real_presentation_end_to_end.py`

Docs/state:

- `docs/country-profile-presentation-model.md`
- `artifacts/tasks/TASK-017-country-profile-presentation-model.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `state/recent_changes.md`
- `context/latest_handoff.md`

## RED evidence

Targeted RED command:

```bash
python3 -m unittest tests.test_country_profile_presentation_model -v
```

Result before implementation:

```text
Ran 5 tests
FAILED (errors=5)
ModuleNotFoundError: No module named 'briefforge.presentation_models'
```

This proved the Country Profile Presentation Model did not exist.

## GREEN evidence

Targeted GREEN command:

```bash
python3 -m unittest tests.test_country_profile_presentation_model -v
```

Result after implementation:

```text
Ran 5 tests in 0.020s
OK
```

Regression commands:

```bash
python3 -m unittest tests.test_real_presentation_end_to_end -v
python3 -m unittest tests.test_presentation_package_builder -v
python3 -m unittest tests.test_deterministic_authoring_identifiers -v
```

Results:

```text
TASK-014: Ran 2 tests, OK
TASK-015: Ran 6 tests, OK
TASK-016: Ran 7 tests, OK
```

Full discovery:

```bash
python3 -m unittest discover -s tests -v
```

Result:

```text
Ran 90 tests
OK
```

## Required proof coverage

1. Country Profile Presentation produces a valid Candidate Presentation Package.
   - Covered by `test_country_profile_presentation_produces_valid_candidate_package`.

2. Denmark Country Profile migrates successfully.
   - Covered by `test_denmark_country_profile_migrates_with_semantic_equivalence`.

3. Existing semantic fingerprints remain stable where semantics are unchanged.
   - Covered by `test_existing_semantic_fingerprint_remains_stable_for_denmark_migration`.

4. Existing pipeline passes unchanged.
   - Covered by `test_existing_pipeline_passes_unchanged` and TASK-014 regression.

5. Country Profile introduces no new runtime abstractions.
   - Covered by `test_country_profile_introduces_no_new_runtime_abstractions`.

## TASK-014 migration

The TASK-014 Denmark helper now returns the Country Profile model output rather than manually constructing runtime dataclasses.

The output remains equal to the original TASK-014 candidate artifact and preserves the known semantic fingerprint:

```text
90d4651099df06afcaf1f531c887b03ae551475096dfa3ad163c44db04c089ff
```

The validation, promotion, renderer-adapter compatibility, invocation, minimal HTML rendering, and rendered-artifact conformance pipeline passes unchanged.

## Architectural observations

Presentation Models naturally fit the existing architecture if they remain authoring-only.

The key boundary is simple:

```text
Presentation Model -> existing PresentationPackageBuilder -> existing CandidatePresentationPackage
```

The model does not become canonical. The Candidate Presentation Package remains canonical for BriefForge.

The frozen constitution remains sufficient.

## Implementation pressure observed

Pressure emerged around vocabulary sizing:

- `overview`, `economy`, and `demographics` are useful for the first country profile;
- a generic `section()` remains necessary to avoid prematurely encoding every country-profile theme;
- relationships, references, and obligations still require author judgment;
- expanding section types should require more real profile evidence.

This is acceptable and does not justify architectural change.

## Implementation Readiness Assessment

GREEN.

Country Profile is safe to keep as the first Presentation Model because it maps naturally to the existing Presentation Package, preserves TASK-014 semantics, and does not alter runtime, validation, promotion, rendering, conformance, or constitution.

Recommended next capability if approved:

- author a second small country profile through the model to test vocabulary pressure before adding more section-specific helpers; or
- address downstream obligation/reference visibility if reader-facing audit visibility becomes higher priority.
