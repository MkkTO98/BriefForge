#!/usr/bin/env python3
"""Produce a compact ProjectForge session recovery report.

The tool intentionally reads a bounded, fixed set of file-backed governance
artifacts. It is a continuity helper, not a repository scanner, indexer, database,
or replacement for task/decision/state artifacts.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

STARTUP_FILES = [
    "CONSTITUTION.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
]
OPTIONAL_CONTEXT_FILES = [
    "context/context_policy.yaml",
    "state/recent_changes.md",
]
RAW_LOG_PARTS = {"logs/raw", "logs/sessions", "logs/runs", "logs/agents"}
MAX_TEXT_CHARS = 2800
MAX_TASKS = 3
MAX_DECISIONS = 5
MAX_QUESTIONS = 5


@dataclass(frozen=True)
class ReadItem:
    rel: str
    status: str
    chars: int = 0


def rel_for(project: Path, path: Path) -> str:
    return str(path.resolve().relative_to(project.resolve())).replace("\\", "/")


def read_limited(path: Path, max_chars: int = MAX_TEXT_CHARS) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) > max_chars:
        return text[:max_chars].rstrip() + "\n[TRUNCATED FOR RECOVERY REPORT]"
    return text


def heading_section(text: str, names: tuple[str, ...], max_chars: int = 900) -> str:
    lines = text.splitlines()
    wanted = {name.lower() for name in names}
    start = None
    for i, line in enumerate(lines):
        stripped = line.strip().lower().lstrip("#").strip()
        if stripped in wanted:
            start = i + 1
            break
    if start is None:
        return ""
    out: list[str] = []
    for line in lines[start:]:
        if line.startswith("#") and out:
            break
        out.append(line)
    value = "\n".join(out).strip()
    return value[:max_chars].rstrip()


def first_nonempty_under_title(text: str, max_chars: int = 700) -> str:
    lines = [line.strip() for line in text.splitlines()]
    body = [line for line in lines if line and not line.startswith("#")]
    return "\n".join(body[:8])[:max_chars].rstrip()


def newest_files(base: Path, pattern: str, limit: int) -> list[Path]:
    if not base.exists():
        return []
    paths = [
        p for p in base.glob(pattern)
        if p.is_file() and not p.name.startswith(".") and p.name != "_SUMMARY.md"
    ]
    return sorted(paths, key=lambda p: (p.stat().st_mtime, p.name), reverse=True)[:limit]


def discover_active_task(project: Path, texts: dict[str, str]) -> list[dict[str, Any]]:
    referenced: list[Path] = []
    combined = "\n".join(texts.get(rel, "") for rel in ("state/active_goal.md", "state/project_state.md", "context/latest_handoff.md"))
    for match in re.finditer(r"artifacts/tasks/[A-Za-z0-9_.\-/]+\.md", combined):
        p = project / match.group(0)
        if p.name == "_SUMMARY.md":
            continue
        if p.exists() and p not in referenced:
            referenced.append(p)
    if not referenced:
        referenced = newest_files(project / "artifacts" / "tasks", "*.md", MAX_TASKS)
    tasks: list[dict[str, Any]] = []
    for path in referenced[:MAX_TASKS]:
        text = read_limited(path, 1600)
        status_match = re.search(r"^Status:\s*(.+)$", text, re.MULTILINE)
        tasks.append({
            "path": rel_for(project, path),
            "status": status_match.group(1).strip() if status_match else "unknown",
            "summary": first_nonempty_under_title(text, 700),
        })
    return tasks


def recent_decisions(project: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in newest_files(project / "artifacts" / "decisions", "*.md", MAX_DECISIONS):
        text = read_limited(path, 1000)
        status_match = re.search(r"^Status:\s*(.+)$", text, re.MULTILINE)
        records.append({
            "path": rel_for(project, path),
            "status": status_match.group(1).strip() if status_match else "unknown",
            "summary": first_nonempty_under_title(text, 450),
        })
    return records


def pending_questions(project: Path) -> list[dict[str, str]]:
    questions: list[dict[str, str]] = []
    for path in newest_files(project / "question_queue" / "pending", "*", MAX_QUESTIONS):
        if not path.is_file():
            continue
        text = read_limited(path, 700)
        questions.append({"path": rel_for(project, path), "summary": first_nonempty_under_title(text, 350) or text[:350]})
    return questions


def collect(project: Path) -> dict[str, Any]:
    project = project.resolve()
    if not project.exists():
        raise FileNotFoundError(project)

    texts: dict[str, str] = {}
    read_items: list[ReadItem] = []
    for rel in STARTUP_FILES + OPTIONAL_CONTEXT_FILES:
        path = project / rel
        if path.exists() and path.is_file():
            text = read_limited(path)
            texts[rel] = text
            read_items.append(ReadItem(rel, "read", len(text)))
        else:
            read_items.append(ReadItem(rel, "missing", 0))

    active_goal = texts.get("state/active_goal.md", "")
    project_state = texts.get("state/project_state.md", "")
    architecture = texts.get("state/architecture.md", "")
    handoff = texts.get("context/latest_handoff.md", "")

    blockers = [
        s for s in [
            heading_section(active_goal, ("blockers", "current blockers", "remaining risks", "risks")),
            heading_section(project_state, ("blockers", "current blockers", "remaining risks", "risks", "deferred or watchlist items")),
            heading_section(handoff, ("blockers", "current blockers", "remaining risks", "remaining risks / boundaries", "risks / boundaries")),
        ]
        if s
    ]
    next_actions = [
        s for s in [
            heading_section(active_goal, ("next recommended task", "next recommended actions", "next actions")),
            heading_section(handoff, ("next recommended task", "next recommended actions", "next actions")),
            heading_section(project_state, ("next recommended task", "next recommended actions", "next actions")),
        ]
        if s
    ]

    report = {
        "project": str(project),
        "recovery_contract": {
            "mode": "bounded_file_backed_recovery",
            "responsibility": "Context and Continuity",
            "validation_category": "Informational",
            "raw_logs_read": False,
            "repository_wide_scan": False,
            "startup_files": STARTUP_FILES,
            "bounded_directories": ["artifacts/tasks/*.md", "artifacts/decisions/*.md", "question_queue/pending/*"],
        },
        "current_project_state": first_nonempty_under_title(project_state, 1400),
        "active_goal": first_nonempty_under_title(active_goal, 1200),
        "architecture_posture": first_nonempty_under_title(architecture, 900),
        "latest_handoff": first_nonempty_under_title(handoff, 1200),
        "active_or_recent_tasks": discover_active_task(project, texts),
        "recent_decisions": recent_decisions(project),
        "current_blockers": blockers,
        "pending_questions": pending_questions(project),
        "next_recommended_actions": next_actions or ["Read the active/recent task listed above, then run the narrowest relevant verification before editing."],
        "recommended_resume_procedure": [
            "Read only the startup files listed in recovery_contract.startup_files.",
            "Read the active/recent task artifact named by this report, if one exists.",
            "Read only decisions and folder summaries directly relevant to that task.",
            "Run `python3 tools/context_health.py --project . --json` or coherence if context size/staleness is uncertain.",
            "Before cloud/Codex escalation, rebuild a compact context with `tools/build_context.py` and inspect the context audit.",
            "If stopping near quota exhaustion, update task status, blockers, next actions, and `context/latest_handoff.md` before any optional cleanup.",
        ],
        "files_consulted": [item.__dict__ for item in read_items],
    }
    return report


def to_markdown(report: dict[str, Any]) -> str:
    def block(value: Any) -> str:
        if not value:
            return "- None recorded."
        if isinstance(value, list):
            lines: list[str] = []
            for item in value:
                if isinstance(item, dict):
                    head = item.get("path", "item")
                    status = f" ({item.get('status')})" if item.get("status") else ""
                    summary = item.get("summary", "")
                    lines.append(f"- `{head}`{status}: {summary}".rstrip())
                else:
                    lines.append(f"- {str(item).strip()}")
            return "\n".join(lines)
        return str(value).strip() or "- None recorded."

    return "\n".join([
        "# Session Recovery Report",
        "",
        f"Project: `{report['project']}`",
        "",
        "## Recovery contract",
        f"- Mode: {report['recovery_contract']['mode']}",
        f"- Raw logs read: {report['recovery_contract']['raw_logs_read']}",
        f"- Repository-wide scan: {report['recovery_contract']['repository_wide_scan']}",
        "",
        "## Current project state",
        block(report["current_project_state"]),
        "",
        "## Active goal",
        block(report["active_goal"]),
        "",
        "## Active or recent tasks",
        block(report["active_or_recent_tasks"]),
        "",
        "## Recent decisions",
        block(report["recent_decisions"]),
        "",
        "## Current blockers",
        block(report["current_blockers"]),
        "",
        "## Pending questions",
        block(report["pending_questions"]),
        "",
        "## Next recommended actions",
        block(report["next_recommended_actions"]),
        "",
        "## Recommended resume procedure",
        block(report["recommended_resume_procedure"]),
        "",
        "## Files consulted",
        block([f"`{item['rel']}` — {item['status']} ({item['chars']} chars)" for item in report["files_consulted"]]),
        "",
    ])


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a compact ProjectForge recovery report without broad repository scanning")
    ap.add_argument("--project", default=".", help="Project root to recover")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    ns = ap.parse_args()
    try:
        report = collect(Path(ns.project))
    except Exception as exc:  # pragma: no cover - CLI guard
        print(f"recover_session failed: {exc}", file=sys.stderr)
        return 2
    if ns.json:
        print(json.dumps(report, indent=2))
    else:
        print(to_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
