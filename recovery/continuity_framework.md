# Continuity and Recovery Framework

Purpose: preserve work continuity across Hermes sessions while spending the fewest possible tokens needed to recover useful state.

This framework extends existing project-local state, task, decision, context-health, and handoff mechanisms. It is not a new governance layer, database, vector store, index, or parallel source of truth.

## Recovery contract

A fresh agent session should recover by reading, in order:

1. `CONSTITUTION.md`
2. `state/active_goal.md`
3. `state/project_state.md`
4. `state/architecture.md`
5. `context/latest_handoff.md` when present
6. the active task artifact only when named by the startup files or recovery report
7. only relevant decisions and folder summaries

Repository-wide scanning is not a startup step. Raw logs, session JSONL, previous full conversations, generated context bundles, unrelated folders, and large artifacts are excluded from normal recovery.

Use the deterministic helper when a compact recovery snapshot is useful:

```bash
python3 tools/recover_session.py --project .
python3 tools/recover_session.py --project . --json
```

The helper reads a bounded set of fixed files plus only recent direct children of `artifacts/tasks/`, `artifacts/decisions/`, and `question_queue/pending/`. It does not inspect raw logs or walk the repository.

## What the recovery snapshot must answer

The recovery snapshot must expose:

- current project state;
- active goal or active/recent task;
- recent decisions;
- current blockers and pending questions;
- next recommended actions;
- recommended resume procedure;
- files consulted.

If these answers are missing or stale, update the existing state/task/handoff artifacts. Do not create a new state artifact just because a current one was poorly maintained.

## Standard project closeout contract

The following user command is sufficient to end a normal session safely:

```text
Perform standard project closeout. Follow the continuity framework. Run required verification if project files changed. Then stop.
```

When receiving that command, the agent must not ask the user for a custom closeout checklist. It must execute the standard file-backed closeout sequence below, using the current project root:

1. Identify the active task from `state/active_goal.md`, `state/project_state.md`, `context/latest_handoff.md`, or `python3 tools/recover_session.py --project . --json`.
2. Update the active task artifact with current status, outcome/evidence, blockers or open questions, incomplete acceptance criteria, and next recommended action. If no active task exists, record the reason in `context/latest_handoff.md` instead of inventing one.
3. Update `context/latest_handoff.md` with context used, files changed, decisions/tasks updated, tests/checks actually run with real output, blockers, next recommended actions, and the exact resume command.
4. Update `state/active_goal.md` and `state/project_state.md` when their current-state pointers changed. Keep them concise; move history to task, decision, report, or handoff artifacts.
5. Refresh affected `_SUMMARY.md` files when summaries are affected; inspect curated `Active Work`, `Needs Attention`, and task-status sections; patch stale curated notes manually.
6. Run the narrowest meaningful verification after the task/state/handoff/summary edits. For structural scaffold changes this normally includes tests, local coherence, recovery smoke checks, and Architecture-to-Reality Audit for governance/template changes.
7. Replace any `pending verification` placeholders with real verification output, or explicitly record remaining verification as a blocker before stopping.

This standard closeout replaces ad hoc user-provided closeout procedures. User instructions may narrow scope or add checks, but they should not be required to restate the standard task/state/handoff/summary/verification sequence.

## Near-quota shutdown priority

When a session is near token, tool, time, or quota exhaustion, continuity beats optional cleanup. Perform these in order:

1. Update the active task artifact with status, outcome so far, and incomplete acceptance criteria.
2. Record blockers, open questions, or approval needs in the active task or `question_queue/pending/` as appropriate.
3. Update `context/latest_handoff.md` with context used, files changed, tests/checks actually run, current blockers, next recommended actions, and exact resume command.
4. Update `state/active_goal.md` and `state/project_state.md` only if their current-state pointers changed.
5. If time remains, refresh affected summaries and run final verification.

Do not spend the last usable budget on broad scans, cosmetic summary rewrites, raw-log reading, optional narrative, or new design work.

## Resume procedure for the next agent

The following user command is sufficient to resume safely:

```text
Recover project state and continue work.
```

When receiving that command, the agent must run or emulate the bounded recovery workflow below before editing files. It should not ask the user to restate project status unless the recovered artifacts reveal a blocking ambiguity.

1. Run `python3 tools/recover_session.py --project . --json` or read the Markdown output.
2. Read the named active/recent task artifact, if any.
3. Read only the decisions and folder summaries relevant to that task.
4. Run `python3 tools/context_health.py --project . --json` or `python3 tools/check_coherence.py --project . --json` when state/handoff freshness is uncertain.
5. Continue from the next recommended action, preserving any recorded blockers or safety boundaries.

## Adoption by existing projects

Existing generated projects are autonomous. They adopt this framework through a project-local governance task or explicit user-approved migration:

- copy or recreate `tools/recover_session.py`;
- add this document under `recovery/continuity_framework.md`;
- update local `AGENTS.md` and `context/context_policy.yaml` with the recovery contract;
- run the project-local recovery smoke check and coherence check;
- record the adoption in local task/state/handoff artifacts.

Generator/template changes must not silently mutate this existing project.
