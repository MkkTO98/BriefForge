# Skill: Context Budgeting

Build the smallest sufficient context bundle for the task.

Use, in order:
- Priority 1: `state/active_goal.md`, `state/project_state.md`, `state/architecture.md`, and `context/latest_handoff.md` (plus `CONSTITUTION.md` when changing files)
- Priority 2: active task files, relevant decision records, and relevant folder summaries
- Priority 3: broader documentation, reports, design notes, roadmap files, and historical artifacts only after justified expansion
- directly relevant source files only after summaries/current state are insufficient

Rules:
- Keep primary state files current, not historical ledgers.
- Treat `context/active_context.md` as a generated output for a specific context-build run, not startup context.
- Regenerate task-specific bundles with `tools/build_context.py` instead of loading stale bundles.
- Run `tools/context_health.py --project . --json` or coherence when state/handoff/context size may have drifted.
- Avoid loading the whole project unless the task explicitly requires a justified project-wide review.
