# Project Agent Instructions

Follow `CONSTITUTION.md` for project identity, purpose, scope, operating principles, responsibility boundaries, instruction hierarchy, and independence doctrine. Use this file for agent operating behavior.

## Context and Continuity

Use this startup hierarchy before changing files:

1. Priority 1 startup context:
   - `CONSTITUTION.md` — Project Identity: purpose, scope, operating principles, responsibility boundaries, instruction hierarchy, and independence doctrine.
   - `state/active_goal.md` — concise current goal pointer.
   - `state/project_state.md` — concise current operating-state pointer.
   - `state/architecture.md` — concise current architecture pointer.
   - `context/latest_handoff.md` — latest recovery handoff.
2. Priority 2 task-specific context, only when relevant:
   - active task files;
   - relevant decision records;
   - relevant folder `_SUMMARY.md` files;
   - explicitly retrieved source files.
3. Priority 3 historical/deep context, only after justified expansion:
   - broader documentation;
   - reports;
   - design notes;
   - roadmaps;
   - historical artifacts.
4. Generated context bundles:
   - `context/active_context.md` is generated for a specific task/model target and is not mandatory startup context.
   - Rebuild stale generated bundles instead of treating them as authoritative.

Repository-wide exploration is not default startup behavior. Expand context incrementally and state why broader context is needed.

State files are current-state pointers, not append-only ledgers. Historical evidence belongs in `artifacts/tasks/`, `artifacts/decisions/`, `artifacts/reports/`, `artifacts/handoffs/`, or derived logs. Folder `_SUMMARY.md` files are navigation aids, not authoritative doctrine.

Raw logs, full session JSONL files, previous full conversations, whole-project dumps, unrelated folders, large tool outputs, and generated artifacts are excluded from normal startup context unless explicitly relevant.

For fast recovery or uncertain state, run `python3 tools/recover_session.py --project . --json`; use its bounded output to identify current state, relevant recent decisions, blockers, next actions, and resume procedure before expanding context.

Use `tools/build_context.py` only when an explicit task-specific bundle is useful. Inspect `context/context_audit.md` before using a generated bundle for broad reasoning. Run `tools/context_health.py --project . --json` or coherence when state/handoff/context size or freshness is uncertain.

## Governance and Decision

Use lightweight project-owned governance artifacts when work must survive the current session:

- `artifacts/tasks/` records substantive work, status, outcome, and links to relevant decisions/reports/handoffs.
- `artifacts/decisions/` records rationale, alternatives, consequences, and status for durable project choices.
- `artifacts/reports/` records review, audit, investigation, architecture-to-reality, implementation, or synthesis findings.
- `artifacts/handoffs/` stores durable handoff snapshots when `context/latest_handoff.md` would become too large.

State files remain current pointers, not historical ledgers. Handoffs preserve continuity, not full history. Historical governance artifacts should not be rewritten merely to make history look clean; amend, supersede, or create a new artifact instead.

Approval is required before destructive actions, external publication, remote pushes, paid resources, credential/production-data handling, major scope changes, or architecture changes that exceed existing identity, decision, or architecture doctrine.

Advisory recommendations, review notes, and ideas do not automatically become tasks. Record them as reports, deferred decisions, or questions unless a human or accepted local decision authorizes task creation.

Run a formal Architecture-to-Reality Audit every 5-10 completed tasks, before major architecture changes, and before major governance reviews:

```bash
python3 tools/architecture_reality_audit.py --project . --write-report
```

Record audit results under `artifacts/reports/`. Convert durable corrections into decision artifacts when policy, architecture, scope, or responsibility boundaries change.

## Work Execution Methodology

Use `instructions/WORK_EXECUTION_METHODOLOGY.md` for implementation approach. Work in bounded implementation slices with explicit objectives, non-goals, implementation boundaries, readiness, success criteria, expected evidence, and a post-slice decision when the work is non-trivial.

Prefer the smallest useful implementation. Let architecture evolve through repeated implementation evidence, recurring implementation pain, or measurable future maintenance reduction; do not generalize speculatively, start framework-first, or redesign broadly during local implementation tasks.

## Hermes operating model

Use Hermes tools directly for normal agent work: reading files, searching, patching, running tests, checking git state, and delegating bounded subtasks.

Project-local tools are helpers, not a replacement for Hermes:

- `tools/build_context.py` creates explicit context bundles.
- `tools/architecture_reality_audit.py` checks architecture/governance/state/template drift.
- `tools/dry_run.py` and `tools/validate_dry_run.py` document and validate risky changes.
- `tools/check_coherence.py` checks scaffold conventions.
- `tools/update_context_summaries.py` refreshes folder summaries.
- `tools/run.py` is an audit/policy wrapper for manual or non-Hermes command execution.

## Safety rules

- Do not push to a remote without human approval.
- Do not handle secrets, credentials, production data, destructive operations, or billing-sensitive actions without explicit approval.
- Do not invent project-wide policy. If policy is absent or conflicting, create a deferred decision or blocking question.
- Record durable architectural/product choices as decision artifacts.
- Record concrete work as task artifacts when it needs to survive the current session.

## Completion discipline

The command `Perform standard project closeout. Follow the continuity framework. Then stop.` is sufficient for a normal safe closeout. Follow `recovery/continuity_framework.md`; do not require the user to restate task/state/handoff/summary/verification steps.

Before summarizing changes, run relevant verification. For code changes, run the applicable tests. For structural project changes, run coherence checks when available.

Near token, tool, time, or quota exhaustion, continuity comes first: update the active task status, blockers/open questions, next actions, and `context/latest_handoff.md` with an exact resume command before optional cleanup or narrative polish.

When completing a task, follow the project `context/context_policy.yaml` task-completion policy:

- Update the task artifact outcome/status, state files, and latest handoff when the change affects future agents.
- Refresh only affected folder `_SUMMARY.md` files when possible, not the whole project by default.
- Inspect refreshed summaries for stale curated sections such as `Active Work`, `Needs Attention`, and task status notes; patch them manually if needed.
- Run final verification after task/state/handoff/summary edits.

Every substantive handoff should include:

- Context used
- Files changed
- Tests/checks run with real output
- Decisions/tasks created or updated
- Remaining risks or next steps

