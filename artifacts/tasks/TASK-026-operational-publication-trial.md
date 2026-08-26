# TASK-026: Operational Publication Trial

Date: 2026-07-03

## Status

Complete.

BriefForge v0.2 was used as an operational publication system without implementing new runtime concepts, renderer capabilities, Presentation Grammar changes, constitutional changes, templates, CSS frameworks, JavaScript, dashboards, portals, search, visualization engines, APIs, or persistence.

## Objective

Publish three substantially different existing EIP analytical artifacts through the existing BriefForge pipeline and evaluate recurring user-facing limitations through operational use.

## Pipeline used

For each publication:

```text
Upstream Artifact
-> Presentation Model if applicable / PresentationPackageBuilder
-> Candidate Presentation Package
-> Validation
-> Ready Presentation Package
-> Human-Centered HTML Renderer
-> Rendered Artifact Conformance
```

The pipeline was not modified.

## Selected artifacts

### 1. InsightForge reviewed finding

Publication id: `pub-01-insightforge-eurostat-finding`

Source:
`/home/mkkto/srv/EIP/projects/InsightForge/artifacts/analytical/IF-A-20260619-002-eurostat-deu-fra-quarterly-direction.md`

Category: macroeconomic finding.

Selection reason:
Reviewed InsightForge analytical finding with YAML frontmatter, evidence/caveats/confidence metadata, and compact table-like body. It tests compact finding publication with explicit analytical boundaries.

### 2. MacroForge canonical GDP snapshot

Publication id: `pub-02-macroforge-canonical-gdp-snapshot`

Source:
`/home/mkkto/srv/EIP/projects/MacroForge/artifacts/reports/canonical-gdp-snapshot-20260604.md`

Category: macroeconomic data snapshot / comparative source report.

Selection reason:
Existing MacroForge succeeded report dominated by tables, source coverage, missingness, data quality, source lineage, and observations. It tests table-heavy publication behavior.

### 3. InsightForge knowledge-accumulation pressure-test report

Publication id: `pub-03-insightforge-knowledge-accumulation-report`

Source:
`/home/mkkto/srv/EIP/projects/InsightForge/artifacts/reports/R-20260619-knowledge-accumulation-pressure-test.md`

Category: methodology / research report.

Selection reason:
Existing long InsightForge methodology report with nested headings, governance analysis, growth-pressure scenarios, risks, and boundary review. It tests long-document narrative publication beyond a compact finding or data snapshot.

## Deliverables

Publication root:
`/home/mkkto/srv/EIP/projects/BriefForge/artifacts/presentations/TASK-026-operational-publication-trial/`

Per publication deliverables:

- published HTML report;
- `candidate_presentation_package.json`;
- `validation_judgment.json`;
- `ready_presentation_package.json`;
- `renderer_audit_metadata.json`;
- `rendered_artifact_conformance.json`;
- `selected_upstream_artifact.md`;
- `reader_evaluation.md`.

Cross-publication deliverables:

- `publication_audit_index.json`;
- `cross_publication_comparison.md`.

## Publication metrics

| Publication | Statements | References | Obligations | HTML bytes | Conformance |
| --- | ---: | ---: | ---: | ---: | --- |
| pub-01-insightforge-eurostat-finding | 6 | 2 | 3 | 12,585 | true |
| pub-02-macroforge-canonical-gdp-snapshot | 5 | 1 | 3 | 11,754 | true |
| pub-03-insightforge-knowledge-accumulation-report | 29 | 1 | 3 | 58,614 | true |

Semantic fingerprints:

- pub-01: `19e3cf57c9f3dd252f7612043b2f65ec8f0ebce15461e140f8354700cbb8929a`
- pub-02: `888d0132c9b480d38ba2d336cced5a6a24ef73330dea0c28b3f4947261ab815a`
- pub-03: `72054044ae4c7630f336d5e994c57c929aead3e6f441d3cd6513cb794a1aaea3`

## Evaluation summary

### Publication 01 — InsightForge finding

Overall usefulness: high.

The compact finding is a good fit for current BriefForge. Question, conclusion, confidence, caveats, source ownership, and reproducibility remain visible.

Main weaknesses:
- browser-default visual appearance — renderer issue;
- repeated primary message — renderer issue;
- caveats flattened into dense prose — renderer issue / authoring issue;
- obligations visible but mechanical — renderer issue.

### Publication 02 — MacroForge GDP snapshot

Overall usefulness: moderate.

The pipeline succeeds, but table-heavy source content exposes a major limitation: Markdown tables are flattened into paragraph text.

Main weaknesses:
- table flattening — renderer issue;
- numeric rows hard to scan — renderer issue;
- generic section labels — renderer issue / presentation grammar issue;
- source data report is compact rather than narrative — upstream content issue.

### Publication 03 — InsightForge methodology report

Overall usefulness: high as audit-grade publication, moderate as reading experience.

The long-document regions help. The report demonstrates repeatable large-report publication beyond TASK-023, but dense paragraphs and generic section labels remain significant.

Main weaknesses:
- dense long paragraphs — renderer issue / upstream content issue;
- source H2/H3 hierarchy flattened — presentation grammar issue / renderer issue;
- repeated reference and obligation links — renderer issue;
- no sticky navigation/search/collapse/reading progress — renderer issue / runtime issue.

## Recurring patterns

Recurring implementation candidates must appear repeatedly. TASK-026 identified these recurring deficiencies:

1. Browser-default visual presentation.
2. Primary-message duplication.
3. Repeated traceability links creating noise.
4. Source structure flattening for lists/tables/nested headings.
5. Generic display headings.
6. Obligations are audit-visible but not reader-friendly.

One-off observations:

- Table flattening is severe in the MacroForge snapshot, but only one table-heavy publication was tested.
- Sticky navigation/search/collapse is important for the long methodology report, but only one long report was tested in this trial.

## Ranked recurring renderer deficiencies

1. Professional static report readability layer: typography, spacing, constrained line width, section separation, and callout styling.
2. Traceability compression: reduce repeated references/obligations while preserving audit links.
3. Primary-message de-duplication.
4. Source-structure preservation for existing Markdown lists/tables/nested headings.
5. Meaningful section display labels instead of generic encounter-mode headings.
6. Reader-friendly obligation presentation.
7. Better uncertainty/caveat display.
8. Long-document section outline beyond broad regions.
9. One-source report simplification.
10. Data/table affordances after more table-heavy evidence.

## Single highest-impact future renderer improvement

Recommendation: professional static report readability layer.

Justification:

- It appeared as a weakness in all three publications.
- It improves compact findings, data reports, and long methodology reports.
- It is user-visible immediately.
- It does not require runtime, Presentation Grammar, constitutional, browser-app, JavaScript, dashboard, portal, search, or visualization changes.
- It preserves the existing static HTML and conformance model.

This is a recommendation only, not implementation approval.

## Success criterion assessment

Success criterion met.

BriefForge repeatedly published real EIP analytical work through the existing pipeline. The trial generated three HTML reports and associated audit/conformance/evaluation artifacts. The recurring limitations were identified through operational use rather than speculative design.
