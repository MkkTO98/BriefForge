#!/usr/bin/env python3
"""Build a strict, summary-first task context bundle.

Normal context is intentionally compact. Raw logs, full conversations, generated
artifacts, unrelated folders, and whole-project dumps are excluded unless the
caller explicitly requests a forensic/failure-investigation context.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None

RAW_LOG_PATTERNS = (
    "logs/raw/",
    "logs/agents/",
    "logs/sessions/",
    "logs/runs/",
    "session.jsonl",
    "sessions.jsonl",
    "conversation",
    "transcript",
)
GENERATED_OR_BULK_DIRS = {
    ".git",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "htmlcov",
    "generated",
}
PRIORITY1_STATE_CANDIDATES = [
    "CONSTITUTION.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
]
PRIORITY1_HANDOFF_CANDIDATES = [
    "context/latest_handoff.md",
    "context/handoff.md",
]
PRIORITY3_PROJECT_SUMMARY_CANDIDATES = [
    "context/PROJECT_CONTEXT.md",
    "context/project_summary.md",
    "state/recent_changes.md",
]
DECISION_DIRS = ["artifacts/decisions"]
TASK_DIRS = ["artifacts/tasks"]


@dataclass
class ContextItem:
    rel: str
    path: Path
    reason: str
    category: str
    max_chars: int


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def policy_for(project: Path) -> dict[str, Any]:
    data = load_yaml(project / "context" / "context_policy.yaml").get("context_policy", {})
    budgets = data.get("budgets", {})
    # Backward compatibility with older flat policy.
    if "default_budget_tokens" in data and not budgets:
        budgets = {
            "local_model_tokens": int(data.get("default_budget_tokens", 24000)),
            "cloud_governance_tokens": min(int(data.get("default_budget_tokens", 24000)), 10000),
        }
    return {
        "local_budget": int(budgets.get("local_model_tokens", 24000)),
        "cloud_budget": int(budgets.get("cloud_governance_tokens", budgets.get("cloud_model_tokens", 10000))),
        "cloud_target": int(budgets.get("cloud_governance_target_tokens", budgets.get("cloud_target_tokens", 8000))),
        "project_wide_budget": int(budgets.get("project_wide_review_tokens", 64000)),
        "project_wide_target": int(budgets.get("project_wide_review_target_tokens", 32000)),
        "per_file_chars": int(data.get("limits", {}).get("explicit_source_file_chars", 20000)),
        "project_wide_per_file_chars": int(data.get("limits", {}).get("project_wide_source_file_chars", data.get("limits", {}).get("explicit_source_file_chars", 20000))),
        "summary_chars": int(data.get("limits", {}).get("summary_file_chars", 4000)),
        "handoff_chars": int(data.get("limits", {}).get("handoff_chars", 3000)),
        "decision_chars": int(data.get("limits", {}).get("decision_record_chars", 6000)),
        "task_chars": int(data.get("limits", {}).get("active_task_chars", 8000)),
        "project_wide_summary_limit": int(data.get("limits", {}).get("project_wide_folder_summary_count", 200)),
    }


def estimate_tokens(text: str) -> int:
    # Conservative enough for budget gates without tokenizer dependencies.
    return max(1, (len(text) + 3) // 4)


def rel_for(project: Path, path: Path) -> str:
    return str(path.resolve().relative_to(project.resolve())).replace("\\", "/")


def is_under(path: Path, project: Path) -> bool:
    try:
        path.resolve().relative_to(project.resolve())
        return True
    except ValueError:
        return False


def is_raw_log_rel(rel: str) -> bool:
    rel_l = rel.lower()
    return any(pattern in rel_l for pattern in RAW_LOG_PATTERNS) or rel_l.startswith("logs/raw")


def excluded_reason(project: Path, path: Path, allow_raw_logs: bool, task_type: str) -> str | None:
    if not is_under(path, project):
        return "outside project root"
    rel = rel_for(project, path)
    parts = set(Path(rel).parts)
    if parts & GENERATED_OR_BULK_DIRS:
        return "generated/cache/bulk directory excluded"
    if path.name.endswith((".pyc", ".pyo", ".pyd")):
        return "compiled artifact excluded"
    raw_allowed = allow_raw_logs or task_type in {"failure_investigation", "forensic", "incident"}
    if is_raw_log_rel(rel) and not raw_allowed:
        return "raw logs/session transcripts excluded from normal context"
    if rel.startswith("logs/") and path.name != "_SUMMARY.md" and not raw_allowed:
        return "log files excluded from normal context; use summaries or failure_investigation"
    if rel.startswith("data/raw/") and not raw_allowed:
        return "raw data excluded unless explicitly relevant"
    return None


def read_limited(path: Path, max_chars: int) -> tuple[str, bool]:
    txt = path.read_text(encoding="utf-8", errors="replace")
    truncated = len(txt) > max_chars
    if truncated:
        txt = txt[:max_chars] + "\n\n[TRUNCATED BY CONTEXT POLICY]\n"
    return txt, truncated


def add_if_exists(items: list[ContextItem], project: Path, rel: str, reason: str, category: str, max_chars: int) -> None:
    path = project / rel
    if path.exists() and path.is_file():
        items.append(ContextItem(rel.replace("\\", "/"), path, reason, category, max_chars))


def split_csv(value: str) -> list[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


def relevant_folder_summaries(project: Path, folders: list[str], files: list[str], task: str, context_mode: str = "normal", max_project_wide: int = 200) -> list[tuple[str, str]]:
    candidates: dict[str, str] = {}
    if context_mode == "project_wide_review":
        for summary in sorted(project.glob("**/_SUMMARY.md"))[:max_project_wide]:
            candidates[rel_for(project, summary)] = "project-wide governance review folder map"
    for folder in folders:
        rel = folder.strip("/")
        if rel:
            candidates[f"{rel}/_SUMMARY.md"] = "explicitly requested relevant folder summary"
    for file_rel in files:
        parent = str(Path(file_rel).parent).replace("\\", "/")
        while parent and parent != ".":
            candidates[f"{parent}/_SUMMARY.md"] = "summary for explicitly retrieved source file parent"
            parent = str(Path(parent).parent).replace("\\", "/")
            if parent == ".":
                break
    lowered = task.lower()
    for d in sorted(project.glob("*/_SUMMARY.md")):
        folder = d.parent.name.lower()
        if folder in lowered:
            candidates[rel_for(project, d)] = "folder summary matched task keywords"
    return sorted(candidates.items())


def relevant_decisions(project: Path, decisions: list[str], task: str, max_auto: int = 6) -> list[tuple[str, str]]:
    found: dict[str, str] = {}
    for rel in decisions:
        found[rel] = "explicitly requested decision record"
    terms = {t.strip(".,:;()[]{}!?`").lower() for t in task.split() if len(t.strip(".,:;()[]{}!?`")) >= 5}
    for ddir in DECISION_DIRS:
        base = project / ddir
        if not base.exists():
            continue
        scored: list[tuple[int, Path]] = []
        for path in base.glob("*.md"):
            name = path.name.lower()
            score = sum(1 for term in terms if term in name)
            if score:
                scored.append((score, path))
        for _, path in sorted(scored, reverse=True)[:max_auto]:
            found[rel_for(project, path)] = "decision record matched task keywords"
    return sorted(found.items())


def write_markdown_audit(audit_path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# Context Audit Report",
        "",
        f"Task: {audit['task']}",
        f"Task type: {audit['task_type']}",
        f"Context mode: {audit['context_mode']}",
        f"Review justification: {audit['review_justification'] or 'not required'}",
        f"Model target: {audit['model_target']}",
        f"Model selected: {audit['model_selected']}",
        f"Model reason: {audit['model_reason']}",
        f"Estimated tokens: {audit['estimated_tokens']}",
        f"Budget tokens: {audit['budget_tokens']}",
        f"Within budget: {audit['within_budget']}",
        f"Raw logs excluded: {audit['raw_logs_excluded']}",
        f"Summaries used: {audit['summaries_used']}",
        "",
        "## Included files",
    ]
    for item in audit["included_files"]:
        lines.append(f"- `{item['path']}` ({item['tokens']} tokens): {item['reason']}")
    lines.extend(["", "## Excluded files"])
    for item in audit["excluded_files"]:
        lines.append(f"- `{item['path']}`: {item['reason']}")
    audit_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build ProjectForge strict summary-first context")
    ap.add_argument("--project", default=".")
    ap.add_argument("--task", default="general")
    ap.add_argument("--task-type", default="normal", choices=["normal", "implementation", "architecture_decision", "project_audit", "strategic_planning", "gap_analysis", "redesign", "failure_investigation", "forensic", "incident"])
    ap.add_argument("--context-mode", default="normal", choices=["normal", "governance", "project_wide_review"], help="normal is compact; governance is cloud reasoning over selected context; project_wide_review allows larger justified audit context")
    ap.add_argument("--review-justification", default="", help="Required for project_wide_review; explains why broader cloud context is worth the tokens")
    ap.add_argument("--task-file", default="", help="Active task artifact to include")
    ap.add_argument("--files", default="", help="Comma-separated explicit source files to include")
    ap.add_argument("--folders", default="", help="Comma-separated relevant folders whose _SUMMARY.md files should be included")
    ap.add_argument("--decisions", default="", help="Comma-separated decision records to include")
    ap.add_argument("--model-target", choices=["local", "cloud"], default="local")
    ap.add_argument("--model-selected", default="local_first")
    ap.add_argument("--model-reason", default="summary-first local context build")
    ap.add_argument("--allow-raw-logs", action="store_true", help="Only for failure/forensic investigations")
    ap.add_argument("--refresh-summaries", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ns = ap.parse_args()

    project = Path(ns.project).resolve()
    if ns.refresh_summaries:
        updater = Path(__file__).with_name("update_context_summaries.py")
        if updater.exists():
            subprocess.run([sys.executable, str(updater), "--project", str(project), "--core-only"], check=False)

    policy = policy_for(project)
    if ns.context_mode == "project_wide_review":
        budget = policy["project_wide_budget"]
    else:
        budget = policy["cloud_budget"] if ns.model_target == "cloud" else policy["local_budget"]
    explicit_files = split_csv(ns.files)
    folders = split_csv(ns.folders)
    explicit_decisions = split_csv(ns.decisions)

    items: list[ContextItem] = []
    excluded: list[dict[str, str]] = []

    for rel in PRIORITY1_STATE_CANDIDATES:
        add_if_exists(items, project, rel, "priority 1 current state artifact", "priority_1_state", policy["summary_chars"])
    for rel in PRIORITY1_HANDOFF_CANDIDATES:
        add_if_exists(items, project, rel, "priority 1 recent handoff pointer", "priority_1_handoff", policy["handoff_chars"])
    if ns.task_file:
        add_if_exists(items, project, ns.task_file, "priority 2 active task file", "priority_2_active_task", policy["task_chars"])
    for rel, reason in relevant_folder_summaries(project, folders, explicit_files, ns.task, ns.context_mode, policy["project_wide_summary_limit"]):
        add_if_exists(items, project, rel, f"priority 2 {reason}", "priority_2_folder_summary", policy["summary_chars"])
    for rel, reason in relevant_decisions(project, explicit_decisions, ns.task):
        add_if_exists(items, project, rel, f"priority 2 {reason}", "priority_2_decision_record", policy["decision_chars"])
    if ns.context_mode != "normal":
        for rel in PRIORITY3_PROJECT_SUMMARY_CANDIDATES:
            add_if_exists(items, project, rel, "priority 3 broader project summary for governance/review context", "priority_3_broader_context", policy["summary_chars"])
    source_file_chars = policy["project_wide_per_file_chars"] if ns.context_mode == "project_wide_review" else policy["per_file_chars"]
    for rel in explicit_files:
        add_if_exists(items, project, rel, "explicitly retrieved source file after priority context is insufficient", "source_file", source_file_chars)

    seen: set[str] = set()
    sections = [
        "# Active Context Bundle",
        "",
        f"Task: {ns.task}",
        f"Task type: {ns.task_type}",
        f"Context mode: {ns.context_mode}",
        "",
        "Context loading hierarchy:",
        "- Priority 1: CONSTITUTION.md plus active goal, project state, architecture, latest handoff.",
        "- Priority 2: active task, relevant decisions, relevant folder summaries.",
        "- Priority 3: broader summaries/docs/reports/design notes only for justified expansion.",
        "",
    ]
    if ns.review_justification:
        sections.extend(["Review justification:", ns.review_justification, ""])
    included: list[dict[str, Any]] = []
    raw_logs_excluded = True
    summaries_used = False
    for item in items:
        if item.rel in seen:
            continue
        seen.add(item.rel)
        reason = excluded_reason(project, item.path, ns.allow_raw_logs, ns.task_type)
        if reason:
            excluded.append({"path": item.rel, "reason": reason})
            if is_raw_log_rel(item.rel):
                raw_logs_excluded = True
            continue
        text, truncated = read_limited(item.path, item.max_chars)
        tokens = estimate_tokens(text)
        sections.append(f"## {item.rel}\n")
        sections.append(f"Reason included: {item.reason}\n")
        sections.append(text)
        sections.append("")
        included.append({"path": item.rel, "reason": item.reason, "category": item.category, "tokens": tokens, "truncated": truncated})
        if item.category == "folder_summary" or item.rel.endswith("_SUMMARY.md"):
            summaries_used = True

    # Record attempts to include unsafe explicit paths even when missing.
    for rel in explicit_files + split_csv(ns.task_file):
        path = project / rel
        if not path.exists():
            excluded.append({"path": rel, "reason": "requested file does not exist"})

    context_text = "\n".join(sections)
    total_tokens = estimate_tokens(context_text)
    within_budget = total_tokens <= budget
    audit = {
        "task": ns.task,
        "task_type": ns.task_type,
        "context_mode": ns.context_mode,
        "validation_category": "Informational",
        "responsibility": "Context and Continuity",
        "review_justification": ns.review_justification,
        "model_target": ns.model_target,
        "model_selected": ns.model_selected,
        "model_reason": ns.model_reason,
        "estimated_tokens": total_tokens,
        "budget_tokens": budget,
        "within_budget": within_budget,
        "raw_logs_excluded": raw_logs_excluded and not ns.allow_raw_logs,
        "summaries_used": summaries_used,
        "context_hierarchy": {
            "priority_1": ["CONSTITUTION.md", "state/active_goal.md", "state/project_state.md", "state/architecture.md", "context/latest_handoff.md"],
            "priority_2": ["active task file", "relevant decision records", "relevant folder summaries"],
            "priority_3": ["broader documentation", "reports", "design notes", "roadmaps", "historical artifacts"],
        },
        "included_files": included,
        "excluded_files": excluded,
    }

    out_dir = project / "context"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "active_context.md"
    manifest = out_dir / "context_manifest.json"
    audit_json = out_dir / "context_audit.json"
    audit_md = out_dir / "context_audit.md"

    if not ns.dry_run:
        out.write_text(context_text, encoding="utf-8")
        manifest.write_text(json.dumps({"task": ns.task, "context_used": [i["path"] for i in included], "estimated_tokens": total_tokens}, indent=2), encoding="utf-8")
        audit_json.write_text(json.dumps(audit, indent=2), encoding="utf-8")
        write_markdown_audit(audit_md, audit)

    print(json.dumps({"context": str(out), "audit": str(audit_json), "estimated_tokens": total_tokens, "budget_tokens": budget, "within_budget": within_budget, "context_mode": ns.context_mode}, indent=2))
    if ns.context_mode == "project_wide_review" and not ns.review_justification:
        print("ERROR: project_wide_review requires --review-justification so broad cloud context is intentional and auditable", file=sys.stderr)
        return 2
    if ns.model_target == "cloud" and not within_budget:
        print("ERROR: context exceeds configured budget for this mode; narrow retrieval, summarize locally, or use justified project_wide_review", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
