# TASK-034 Repository-Wide BriefForge Naming Normalization

Status: completed
Date: 2026-07-08

## Objective

Normalize repository naming so the public project name is consistently **BriefForge** while preserving normal Python package conventions and stable historical identifiers.

## Non-goals

- No new functionality.
- No architecture changes.
- No runtime behavior changes.
- No constitution changes.
- No Python package rename.

## Investigation summary

Searched for inconsistent variants and related lowercase occurrences:

- `briefforge`
- capitalized-only-invalid variant
- mixed-case invalid variant
- all-caps invalid variant
- spaced variants such as spaced capitalized invalid variant / spaced lowercase invalid variant

Findings:

- One inconsistent mixed-case test method name was found in `tests/test_insightforge_integration_proof.py`.
- capitalized-only-invalid variant, all-caps invalid variant, spaced capitalized invalid variant, spaced lowercase invalid variant: no remaining occurrences after normalization scan.
- `briefforge`: many intentional technical/historical occurrences, classified below.

## Classification

### Project name

Public prose project-name references are normalized to **BriefForge**.

### Repository path

The project checkout was renamed from:

- `the former lowercase repository path`

To:

- `/home/mkkto/srv/EIP/projects/BriefForge`

Absolute repository path references inside project artifacts were updated to the new directory name. ProjectForge workspace metadata was also updated.

### Python package/module

The Python package remains:

- `briefforge`

Justification: Python package/module names are conventionally lowercase; existing source/tests import `briefforge`; renaming the package would create unnecessary import churn and risk runtime breakage without improving public naming clarity.

### Documentation

Normalized by adding explicit naming documentation in:

- `README.md`
- `docs/naming-conventions.md`

### Reports

Absolute repository path references were updated where present. Historical report filenames such as `R-20260703-briefforge-v0.2-operational-milestone.md` were intentionally preserved as historical artifact identifiers.

### Tasks

Absolute repository path references were updated where present. Historical task filenames/directories such as `TASK-025-showcase-briefforge-v0.2.md` were intentionally preserved.

### State files / handoff / summaries

State and handoff were updated during closeout to record the new repository path and naming convention. Context summaries were regenerated after changes.

### Tests

The only inconsistent mixed-case test method name was normalized to `BriefForge`. Test imports remain `briefforge` intentionally.

### Examples

No separate example-only naming inconsistencies were found.

### Generated artifacts

Generated artifact IDs, package IDs, validation policy IDs, HTML metadata keys, and historical filenames containing lowercase `briefforge` were intentionally preserved to avoid unnecessary churn and keep existing semantic fingerprints/artifact identity stable.

## Intentionally unchanged names

- Python package path: `src/briefforge/`
- Python imports: `import briefforge`, `from briefforge...`
- Validation policy ID: `briefforge-constitutional-validation-policy:v1`
- Historical package IDs: `briefforge-task-...`
- HTML metadata keys: `briefforge-adapter-id`, `briefforge-package-id`, `briefforge-semantic-fingerprint`, `briefforge-validation-policy-id`
- Historical artifact filenames/directories containing `briefforge`, including v0.2/v0.3/v0.4/v0.5 showcase/proof artifacts.

## Verification

Final verification was run after edits, directory rename, summary regeneration, and closeout updates:

- context summaries updated;
- coherence check run;
- context health run;
- full test suite run;
- compileall run;
- direct import verification run;
- repository path/reference scan run.

See `context/latest_handoff.md` for final command output summary.
