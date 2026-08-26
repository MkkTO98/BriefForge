# TASK-022: First Human-Centered HTML Presentation

Date: 2026-07-02
Status: Complete

## Objective

Improve the existing minimal HTML renderer so it implements the TASK-021 Presentation Grammar rather than merely emitting semantic content.

The objective was to determine whether the existing BriefForge architecture can communicate information effectively through simple static HTML without introducing new infrastructure.

## Scope implemented

Implemented renderer-level improvements in the existing minimal HTML renderer:

- purpose-first presentation;
- semantic hierarchy;
- attention differentiation;
- evidence-linked references;
- grouped reference inventory;
- contextual obligations;
- grouped obligation inventory;
- uncertainty/caveat visibility;
- source ownership labels;
- discoverable validation/audit metadata.

Primary target:

- TASK-014 Denmark Country Profile.

Generated artifacts:

- `artifacts/presentations/TASK-022-human-centered-denmark-html/human_centered_html_artifact.html`
- `artifacts/presentations/TASK-022-human-centered-denmark-html/rendered_artifact_conformance.json`
- `artifacts/presentations/TASK-022-human-centered-denmark-html/renderer_audit_metadata.json`
- `artifacts/presentations/TASK-022-human-centered-denmark-html/reader_evaluation.md`

Documentation:

- `docs/human-centered-html-renderer.md`

Tests:

- `tests/test_human_centered_html_renderer.py`

## Scope explicitly excluded

Not implemented:

- new runtime concepts;
- Presentation Plans;
- new Presentation Models;
- templates;
- CSS frameworks;
- JavaScript;
- browser application behavior;
- dashboards;
- portals;
- component libraries;
- visualization engines;
- charts;
- maps;
- PDF generation;
- exports;
- persistence;
- APIs;
- networking;
- renderer registry;
- constitutional revision.

The only source behavior changed was the existing bounded static HTML renderer.

## RED evidence

Command:

```bash
python3 -m unittest tests.test_human_centered_html_renderer -v
```

Initial result before renderer implementation:

```text
Ran 8 tests in 0.025s
FAILED (failures=6)
```

Expected failures proved the existing minimal HTML output did not satisfy the Presentation Grammar:

- missing `data-grammar="presentation-grammar-v1"`;
- missing grammar stages;
- missing attention hierarchy;
- missing evidence-linked references;
- missing grouped reference inventory;
- missing contextual obligations;
- missing grouped obligation inventory;
- missing uncertainty/caveat section;
- missing discoverable validation/audit metadata.

Two tests already passed during RED:

- static HTML remained non-browser-app output;
- runtime objects and Presentation Models were unchanged.

## GREEN evidence

Targeted command:

```bash
python3 -m unittest tests.test_human_centered_html_renderer -v
```

Result:

```text
Ran 8 tests in 0.029s
OK
```

## Regression evidence

Commands:

```bash
python3 -m unittest tests.test_real_presentation_end_to_end -v
python3 -m unittest tests.test_country_profile_presentation_model -v
python3 -m unittest tests.test_country_comparison_presentation_model -v
python3 -m unittest tests.test_investment_thesis_presentation_model -v
python3 -m unittest tests.test_insightforge_integration_proof -v
python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests
```

Results:

- TASK-014 regression: 2 tests passed.
- TASK-017 regression: 5 tests passed.
- TASK-018 regression: 5 tests passed.
- TASK-019 regression: 5 tests passed.
- TASK-020 integration regression: 6 tests passed.
- Full unit discovery: 114 tests passed.
- compileall: passed.

## Reader evaluation

See:

- `artifacts/presentations/TASK-022-human-centered-denmark-html/reader_evaluation.md`

Summary:

- Primary message is immediately visible.
- Supporting details are naturally discoverable.
- References are inspectable through nearby links and grouped inventory.
- Obligations are visible near constrained statements and grouped for audit.
- Uncertainty/caveats are placed before audit metadata.
- Reading order follows the Presentation Grammar.

## Friction classification

| Observation | Classification | Architectural consequence |
| --- | --- | --- |
| Encounter labels are mechanically derived from encounter modes. | renderer issue | Future renderer polish only. |
| Obligation inventory can be text-heavy. | renderer issue | Future compression/display refinement only. |
| Synthesis remains in authored statement order rather than a final visual block. | renderer issue | No runtime change required. |
| Static HTML lacks richer long-report navigation. | renderer issue | Future browser-report investigation only. |
| No issue requiring grammar change. | grammar issue: none | No grammar revision required. |
| No issue requiring runtime change. | runtime issue: none | Runtime remains unchanged. |
| No issue contradicting constitution. | constitutional issue: none | Constitution remains frozen. |

## Architectural observations

1. The Ready Presentation Package already contains sufficient semantic material for readable static HTML.
2. References and obligations can be communicated with existing runtime fields.
3. Uncertainty can be communicated conservatively through encounter modes, authored caveat/risk statements, and obligations.
4. Renderer-adapter audit metadata remains intact.
5. Rendered HTML still does not become semantic authority.
6. The HTML renderer contract now reads `upstream_references` and `obligations`, which are already approved Ready package features.
7. No Presentation Model required modification.

## Implementation Readiness Assessment

Status: GREEN for bounded human-centered static HTML renderer proof.

Evidence supports:

- continuing to treat BriefForge as a semantic presentation package system with downstream renderers;
- future renderer-level work on reference/obligation/uncertainty affordances;
- cautious browser-report investigation later.

Evidence does not support:

- runtime expansion;
- constitution revision;
- templates;
- browser applications;
- dashboards/portals;
- visualization/chart/map systems;
- renderer registry;
- persistence/API/export infrastructure.

## Final assessment

1. Would this HTML be something a knowledgeable analyst would willingly read?

Yes, for a compact country-profile proof. It is not visually polished, but it is coherent, auditable, and meaningfully reader-centered compared with the previous flat semantic dump.

2. What remains missing before BriefForge produces genuinely useful browser reports?

- better typography and spacing;
- long-report navigation;
- refined synthesis placement;
- richer source/obligation affordances;
- larger cross-project examples;
- explicit browser-report architecture investigation.

These are renderer/browser-report questions, not runtime or constitutional blockers.

3. Did implementation expose evidence requiring runtime or constitutional change?

No.
