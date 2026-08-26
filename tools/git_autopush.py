#!/usr/bin/env python3
"""Conservative milestone commit-and-push helper."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


def run(args: list[str], cwd: Path) -> int:
    print("+", " ".join(args))
    return subprocess.call(args, cwd=cwd)


def staged_paths(cwd: Path) -> set[str]:
    output = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only", "-z"],
        cwd=cwd,
    )
    return {
        item.decode("utf-8", "surrogateescape")
        for item in output.split(b"\0")
        if item
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    parser.add_argument("--message")
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--yes-push", action="store_true")
    parser.add_argument("--paths", nargs="+")
    args = parser.parse_args()
    cwd = Path(args.project).resolve()

    run(["git", "status"], cwd)
    run(["git", "diff", "--stat"], cwd)

    if args.commit:
        if not args.message:
            print("--message required for commit", file=sys.stderr)
            return 2
        if not args.paths:
            print("--paths required for commit", file=sys.stderr)
            return 3
        authorized = set(args.paths)
        unexpected = staged_paths(cwd) - authorized
        if unexpected:
            print("Refusing unrelated staged paths: " + ", ".join(sorted(unexpected)), file=sys.stderr)
            return 3
        if run(["git", "add", "--", *args.paths], cwd) != 0:
            return 3
        staged = staged_paths(cwd)
        if staged - authorized:
            print("Refusing unrelated staged paths", file=sys.stderr)
            return 3
        if staged:
            if run(["git", "commit", "-m", args.message], cwd) != 0:
                return 4
        else:
            print("No authorized milestone changes to commit.")

    if args.push:
        if not args.yes_push:
            print("Push requires --yes-push", file=sys.stderr)
            return 5
        return run(["git", "push", "origin", "HEAD:main"], cwd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
