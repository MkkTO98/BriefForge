#!/usr/bin/env python3
"""Conservative git helper.

Default behavior prepares status/diff and optionally commits. Push is disabled unless
--push and --yes-push are both supplied.
"""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path


def run(args, cwd):
    print("+", " ".join(args))
    return subprocess.call(args, cwd=cwd)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--project", default=".")
    p.add_argument("--message")
    p.add_argument("--commit", action="store_true")
    p.add_argument("--push", action="store_true")
    p.add_argument("--yes-push", action="store_true")
    ns = p.parse_args()
    cwd = Path(ns.project).resolve()
    run(["git","status"], cwd)
    run(["git","diff","--stat"], cwd)
    if ns.commit:
        if not ns.message:
            print("--message required for commit", file=sys.stderr)
            return 2
        if run(["git","add","-A"], cwd) != 0: return 3
        if run(["git","commit","-m",ns.message], cwd) != 0: return 4
    if ns.push:
        if not ns.yes_push:
            print("Push requires --yes-push", file=sys.stderr)
            return 5
        return run(["git","push"], cwd)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
