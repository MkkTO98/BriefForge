#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt
from pathlib import Path


def append(path: Path, line: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(line.rstrip()+"\n")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--project", default=".")
    p.add_argument("--recent")
    p.add_argument("--issue")
    p.add_argument("--lesson")
    ns = p.parse_args()
    project = Path(ns.project).resolve()
    today = dt.date.today().isoformat()
    if ns.recent:
        append(project/"state"/"recent_changes.md", f"- {today}: {ns.recent}")
    if ns.issue:
        append(project/"state"/"known_issues.md", f"- {today}: {ns.issue}")
    if ns.lesson:
        append(project/"state"/"lessons.md", f"- {today}: {ns.lesson}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
