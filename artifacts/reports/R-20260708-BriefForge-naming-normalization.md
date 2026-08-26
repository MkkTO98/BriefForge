# BriefForge Naming Normalization Report

Date: 2026-07-08
Task: `artifacts/tasks/TASK-034-repository-wide-BriefForge-naming-normalization.md`

## Scope

Repository-wide naming cleanup only. No functionality, architecture, runtime behavior, or constitution semantics were changed.

## Canonical names

- Public project name: **BriefForge**
- Repository directory: `BriefForge`
- Python package/module namespace: `briefforge`

## Occurrence investigation

Search terms used:

- `briefforge`
- capitalized-only-invalid variant
- mixed-case invalid variant
- all-caps invalid variant
- spaced capitalized invalid variant
- spaced lowercase invalid variant

Results:

- One inconsistent mixed-case occurrence was found in a test method name and corrected to `BriefForge`.
- No invalid capitalization or spacing variants remain.
- Lowercase `briefforge` remains intentionally where it is a Python/package/module identifier, policy/package ID, metadata key, path component, or historical artifact identifier.

## Classification

| Class | Treatment |
| --- | --- |
| Project name | Public prose normalized to `BriefForge`. |
| Repository path | Directory renamed to `/home/mkkto/srv/EIP/projects/BriefForge`; absolute path references updated. |
| Python package/module | Kept lowercase as `briefforge`. |
| Documentation | README naming convention added; dedicated naming-conventions doc added. |
| Reports | Absolute paths updated where found; historical report filenames preserved. |
| Tasks | Absolute paths updated where found; task artifact created for this normalization. |
| State files | Updated during closeout to reflect TASK-034 and repository path. |
| Tests | Mixed-case test method corrected; imports preserved as `briefforge`. |
| Examples | No separate example-only inconsistent names found. |
| Generated artifacts | Historical IDs, filenames, HTML metadata keys, validation policy IDs, package IDs, and fingerprints preserved. |

## Modified existing content categories

- Path references changed from `the former lowercase repository path` to `/home/mkkto/srv/EIP/projects/BriefForge`.
- ProjectForge workspace metadata path changed to the new repository directory.
- One test method name normalized to `BriefForge`.
- README and docs now explicitly document the project/package naming split.

## Intentionally preserved lowercase names

The following lowercase forms are intentional and should not be treated as ambiguous public naming:

- `src/briefforge/`
- `import briefforge` and `from briefforge...`
- `briefforge-constitutional-validation-policy:v1`
- `briefforge-task-...` package IDs
- `briefforge-*` HTML metadata keys
- historical artifact filenames/directories such as `TASK-025-showcase-briefforge-v0.2/`, `TASK-030-briefforge-v0.3-reader-experience-showcase/`, and `briefforge_v0_*.html`

Rationale: these are technical identifiers or historical generated artifact names. Changing them would create unnecessary churn and could invalidate tests, fingerprints, or artifact traceability.

## Package-name decision

The package remains `briefforge` because Python package and module names are normally lowercase. Keeping it lowercase preserves import compatibility and avoids a style regression. The public project name is now explicitly documented as **BriefForge**.
