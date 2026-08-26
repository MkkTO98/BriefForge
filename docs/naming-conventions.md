# BriefForge Naming Conventions

Date: 2026-07-08

## Canonical public name

The canonical public project name is **BriefForge**.

Use **BriefForge** for prose references to the project in documentation, reports, state files, task artifacts, handoffs, summaries, and other user-visible governance material.

## Repository directory

The repository directory is named `BriefForge`.

Historical absolute paths using `the former lowercase repository path` were updated to `/home/mkkto/srv/EIP/projects/BriefForge` during the repository-wide naming-normalization task.

## Python package

The Python package/module namespace remains `briefforge`.

Rationale:

- Python package and module names are conventionally lowercase.
- Existing source, tests, generated artifacts, and downstream examples import `briefforge`.
- Renaming the package to `BriefForge` would create import instability and violate normal Python style without improving project identity consistency.
- Lowercase package references are technical identifiers, not public-project-name prose.

## Intentionally preserved lowercase identifiers

Do not rewrite the following merely to match public-project-name capitalization:

- `src/briefforge/` package path;
- `import briefforge` and `from briefforge...` imports;
- validation policy IDs such as `briefforge-constitutional-validation-policy:v1`;
- package IDs such as `briefforge-task-...`;
- HTML metadata keys such as `briefforge-package-id`;
- historical artifact filenames and directory names such as `TASK-025-showcase-briefforge-v0.2/` and `briefforge_v0_2_showcase.html`.

These are stable technical or historical identifiers. Preserving them avoids unnecessary churn and does not create ambiguity because this convention explicitly distinguishes:

- Project name = BriefForge
- Python package = `briefforge`
