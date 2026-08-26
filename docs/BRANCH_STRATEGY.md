# Branch Strategy

A git branch is a separate line of development.

project-local default:

- Start with one main branch.
- Use feature branches when work becomes risky, parallel, or long-running.
- Use agent branches when multiple agents may touch overlapping files.

Recommended progression:

1. Single branch while project is small.
2. Feature branches once changes become nontrivial.
3. Agent-specific branches only when simultaneous autonomous work is reliable.

This avoids premature complexity.
