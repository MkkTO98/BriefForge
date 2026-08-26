#!/usr/bin/env python3
"""Layered command runner for generated projects.

This is intentionally conservative. It is not a sandbox. It is a policy gate.
Use OS-level sandboxing for stronger isolation.
"""
from __future__ import annotations
import argparse, json, os, shlex, shutil, subprocess, sys, time
from pathlib import Path

try:
    import yaml
except Exception:
    yaml = None


def load_yaml(path: Path):
    text = path.read_text(encoding="utf-8")
    if yaml:
        return yaml.safe_load(text) or {}
    raise RuntimeError("PyYAML is required for tools/run.py. Use `uvx --with pyyaml python tools/run.py ...` for one-shot execution, or run `uv venv && uv pip install pyyaml`.")


def command_string(args: list[str]) -> str:
    return " ".join(shlex.quote(a) for a in args)


def denied(cmd: str, deny_cfg: dict) -> str | None:
    for pattern in deny_cfg.get("forbidden_patterns", []):
        crude = pattern.replace("*", "")
        if crude and crude in cmd:
            return pattern
    return None


def allowed(cmd_args: list[str], level: str, allow_cfg: dict) -> bool:
    cmd = command_string(cmd_args)
    levels = allow_cfg.get("levels", {})
    allowed_cmds = levels.get(level, {}).get("commands", [])
    return any(cmd.startswith(allowed_prefix) for allowed_prefix in allowed_cmds)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    parser.add_argument("--level", default="safe", choices=["safe", "review", "dangerous"])
    parser.add_argument("--yes-dangerous", action="store_true", help="Allow dangerous command after explicit operator choice.")
    parser.add_argument("cmd", nargs=argparse.REMAINDER)
    ns = parser.parse_args()

    if ns.cmd and ns.cmd[0] == "--":
        ns.cmd = ns.cmd[1:]
    if not ns.cmd:
        print("No command provided", file=sys.stderr)
        return 2

    project = Path(ns.project).resolve()
    perms = project / "permissions"
    if not perms.exists():
        perms = Path(__file__).resolve().parents[1] / "permissions"

    allow_cfg = load_yaml(perms / "allowlist.yaml")
    deny_cfg = load_yaml(perms / "denylist.yaml")
    cmd = command_string(ns.cmd)

    bad = denied(cmd, deny_cfg)
    if bad:
        print(f"DENIED: command matches forbidden pattern: {bad}", file=sys.stderr)
        return 10

    if ns.level == "dangerous" and not ns.yes_dangerous:
        print("DENIED: dangerous command requires --yes-dangerous", file=sys.stderr)
        return 11

    if not allowed(ns.cmd, ns.level, allow_cfg):
        print(f"DENIED: command not allowlisted for level {ns.level}: {cmd}", file=sys.stderr)
        return 12

    if shutil.which(ns.cmd[0]) is None:
        print(f"DENIED: executable not found: {ns.cmd[0]}", file=sys.stderr)
        return 13

    log_dir = project / "logs" / "agents"
    log_dir.mkdir(parents=True, exist_ok=True)
    record = {"ts": time.time(), "level": ns.level, "cmd": ns.cmd, "cwd": str(project)}
    with (log_dir / "commands.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    try:
        return subprocess.call(ns.cmd, cwd=project)
    except FileNotFoundError as exc:
        print(f"DENIED: executable not found: {exc.filename or ns.cmd[0]}", file=sys.stderr)
        return 13

if __name__ == "__main__":
    raise SystemExit(main())
