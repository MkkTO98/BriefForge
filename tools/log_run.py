#!/usr/bin/env python3
"""Record raw run metadata and maintain compact task/session summaries."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import time
import uuid
from pathlib import Path


def split_csv(value: str) -> list[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def compact_markdown(rec: dict) -> str:
    files = rec.get("files") or []
    files_text = "\n".join(f"- `{f}`" for f in files) if files else "- None recorded."
    notes = rec.get("notes") or "No additional notes recorded."
    return f"""# Latest Handoff

Updated: {rec['iso_time']}
Agent: {rec['agent']}
Status: {rec['status']}
Run ID: {rec['id']}

## Goal
{rec['goal']}

## Files changed or touched
{files_text}

## Compact notes
{notes}

## Context rule
Future agents should read this handoff, project/folder summaries, active task files, and relevant decisions first. Raw logs remain available for audit/debugging but must not be loaded into normal task context.
"""


def update_project_state_summary(project: Path, rec: dict) -> None:
    path = project / "context" / "project_summary.md"
    existing = path.read_text(encoding="utf-8", errors="replace") if path.exists() else "# Project Summary\n"
    marker = "## Latest recorded run"
    latest = f"""## Latest recorded run
- Time: {rec['iso_time']}
- Agent: {rec['agent']}
- Status: {rec['status']}
- Goal: {rec['goal']}
- Run ID: {rec['id']}
"""
    if marker in existing:
        before = existing.split(marker, 1)[0].rstrip()
        path.write_text(before + "\n\n" + latest, encoding="utf-8")
    else:
        path.write_text(existing.rstrip() + "\n\n" + latest, encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--project", default=".")
    p.add_argument("--agent", required=True)
    p.add_argument("--goal", required=True)
    p.add_argument("--status", required=True)
    p.add_argument("--files", default="")
    p.add_argument("--notes", default="")
    p.add_argument("--tests", default="", help="Short test/validation evidence")
    ns = p.parse_args()

    project = Path(ns.project).resolve()
    now = dt.datetime.now(dt.timezone.utc)
    rec = {
        "id": str(uuid.uuid4()),
        "ts": time.time(),
        "iso_time": now.isoformat(),
        "agent": ns.agent,
        "goal": ns.goal,
        "status": ns.status,
        "files": split_csv(ns.files),
        "notes": ns.notes,
        "tests": ns.tests,
    }

    # Raw operational record remains available for audit/debugging.
    append_jsonl(project / "logs" / "agents" / "runs.jsonl", rec)
    # Compact derived summaries are the normal future context source.
    append_jsonl(project / "logs" / "derived" / "session_summaries.jsonl", {
        "id": rec["id"],
        "iso_time": rec["iso_time"],
        "agent": rec["agent"],
        "goal": rec["goal"],
        "status": rec["status"],
        "files": rec["files"],
        "notes": rec["notes"][:2000],
        "tests": rec["tests"][:2000],
    })
    (project / "context").mkdir(parents=True, exist_ok=True)
    (project / "context" / "latest_handoff.md").write_text(compact_markdown(rec), encoding="utf-8")
    update_project_state_summary(project, rec)
    print(rec["id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
