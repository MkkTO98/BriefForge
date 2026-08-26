# Context Policy

Project context is summary-first, incremental, and optimized for leverage per cloud token. `_SUMMARY.md` files are folder-local maps. `context/active_context.md` is the selected task bundle. `context/context_audit.md` explains what was included/excluded and why. `state/` contains current project truth. `artifacts/decisions/` contains durable choices and deferred specifications.

Rules:
- Context building should use `tools/build_context.py` for explicit bundles.
- Summary maintenance should use `tools/update_context_summaries.py`.
- Agents must report `Context used:` in every run report.
- Local execution tasks should use local tools/models for implementation, refactoring, tests, debugging, summarization, retrieval/indexing, log compression, and routine documentation.
- Cloud governance tasks are architecture review, strategic planning, project audit, gap analysis, redesign, consistency review, high ambiguity, repeated local failure, explicit user request, or safety-critical reasoning.
- Normal task context may include only project summary/current state, active task file, relevant folder summaries, relevant decision records, explicitly retrieved source files, and a short recent handoff.
- Normal task context must not include raw logs, previous full conversations, full session JSONL files, whole-project file dumps, unrelated folders, large tool outputs, or generated artifacts unless explicitly relevant.
- Raw logs may be read only for failure investigation, forensic, or incident work when summaries are insufficient.
- Cloud/Codex escalation requires `context/context_audit.json` / `.md`, estimated token counts, context mode, included/excluded file reasons, confirmation that raw logs were excluded, and confirmation that summaries were used.
- Compact cloud governance uses the normal governance budget. Legitimate project-wide audits, redesigns, strategic reviews, gap analyses, and consistency reviews may use `--context-mode project_wide_review` with `--review-justification` and the larger configured project-wide review budget.
- Agents must not treat summaries as authoritative when they conflict with decisions or state.
- Cross-module changes must consult `knowledge/dependencies.yaml`.
