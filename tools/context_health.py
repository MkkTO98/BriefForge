#!/usr/bin/env python3
"""Check ProjectForge context artifacts for token/size hygiene.

This checker keeps primary state files concise and treats generated context bundles
as outputs, not mandatory startup inputs. It is intentionally dependency-light so
it can run inside generated projects.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None

VALIDATION_CATEGORIES = [
    "Constitutional Violation",
    "Architectural Inconsistency",
    "Implementation Inconsistency",
    "Historical Compatibility",
    "Sovereign Divergence",
    "Informational",
]

MIGRATION_CLASSES = [
    "Required constitutional fix",
    "Required safety fix",
    "Architectural recommendation",
    "Optional capability promotion",
    "Historical compatibility notice",
    "Informational improvement",
]

DEFAULT_LIMITS = {
    "active_goal_chars": 6000,
    "project_state_chars": 12000,
    "architecture_chars": 12000,
    "recent_changes_chars": 6000,
    "handoff_warn_chars": 3000,
    "handoff_block_chars": 9000,
    "active_context_warn_chars": 40000,
    "active_context_block_chars": 256000,
    "generated_context_stale_hours": 168,
}

HISTORICAL_LEDGER_MARKERS = (
    "## verification completed",
    "## files changed in the completed implementation sequence",
    "```text\npython3 tools/",
    "passed in ",
    "failed tests/",
    "files changed",
    "commit ",
    "diff --git",
)

HANDOFF_EXPECTED_MARKERS = (
    "context used",
    "files changed",
    "tests/checks",
    "checks run",
    "decisions/tasks",
    "remaining risks",
    "blockers",
    "next",
    "resume",
)

PRIMARY_STATE = {
    "state/active_goal.md": "active_goal_chars",
    "state/project_state.md": "project_state_chars",
    "state/architecture.md": "architecture_chars",
    "state/recent_changes.md": "recent_changes_chars",
}


def estimate_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4)


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def policy_limits(project: Path) -> dict[str, int]:
    data = load_yaml(project / "context" / "context_policy.yaml").get("context_policy", {})
    limits = DEFAULT_LIMITS.copy()
    configured = data.get("context_health", {})
    for key, value in configured.items():
        if key in limits:
            limits[key] = int(value)

    base_limits = data.get("limits", {})
    handoff_chars = int(base_limits.get("handoff_chars", limits["handoff_warn_chars"]))
    limits["handoff_warn_chars"] = int(configured.get("handoff_warn_chars", handoff_chars))
    limits["handoff_block_chars"] = int(configured.get("handoff_block_chars", max(handoff_chars * 3, limits["handoff_block_chars"])))

    budgets = data.get("budgets", {})
    cloud_budget = int(budgets.get("cloud_governance_tokens", 10000))
    project_wide_budget = int(budgets.get("project_wide_review_tokens", 64000))
    limits["active_context_warn_chars"] = int(configured.get("active_context_warn_chars", cloud_budget * 4))
    limits["active_context_block_chars"] = int(configured.get("active_context_block_chars", project_wide_budget * 4))
    limits["generated_context_stale_hours"] = int(configured.get("generated_context_stale_hours", limits["generated_context_stale_hours"]))
    return limits


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def check(project: Path) -> dict[str, Any]:
    project = project.resolve()
    limits = policy_limits(project)
    blocks: list[str] = []
    warnings: list[str] = []
    measured: list[dict[str, Any]] = []
    files_checked: list[str] = []
    checks_performed: list[str] = [
        "primary_state_size_and_ledger_hygiene",
        "handoff_size_and_completeness",
        "generated_context_bundle_integrity",
        "context_budget_bounds",
    ]

    for rel, limit_key in PRIMARY_STATE.items():
        path = project / rel
        if not path.exists():
            continue
        files_checked.append(rel)
        text = read_text(path)
        chars = len(text)
        limit = limits[limit_key]
        measured.append({"path": rel, "chars": chars, "estimated_tokens": estimate_tokens(text), "limit_chars": limit})
        if chars > limit:
            blocks.append(f"{rel} is {chars} chars; primary state files must stay concise (limit {limit})")
        elif chars > int(limit * 0.75):
            warnings.append(f"{rel} is approaching context-health limit ({chars}/{limit} chars)")
        lowered = text.lower()
        marker_hits = [m for m in HISTORICAL_LEDGER_MARKERS if m in lowered]
        if marker_hits and chars > int(limit * 0.6):
            warnings.append(
                f"{rel} looks like a historical ledger; move long logs/file histories to handoffs, reports, or logs/derived"
            )

    for rel in ("context/latest_handoff.md", "context/handoff.md"):
        path = project / rel
        if not path.exists():
            continue
        files_checked.append(rel)
        text = read_text(path)
        chars = len(text)
        measured.append({
            "path": rel,
            "chars": chars,
            "estimated_tokens": estimate_tokens(text),
            "warn_chars": limits["handoff_warn_chars"],
            "block_chars": limits["handoff_block_chars"],
        })
        if chars > limits["handoff_block_chars"]:
            blocks.append(f"{rel} is {chars} chars; handoff must be a short recent pointer (block limit {limits['handoff_block_chars']})")
        elif chars > limits["handoff_warn_chars"]:
            warnings.append(f"{rel} is {chars} chars; prefer a concise handoff and move detail to artifacts/handoffs or reports")
        lowered = text.lower()
        marker_hits = sum(1 for marker in HANDOFF_EXPECTED_MARKERS if marker in lowered)
        # Empty/new-project handoffs are allowed, but substantive handoffs should preserve recovery evidence.
        if chars > 500 and marker_hits < 3:
            warnings.append(f"{rel} appears incomplete for recovery evidence ({marker_hits} expected handoff markers found)")
        if sum(1 for marker in HISTORICAL_LEDGER_MARKERS if marker in lowered) >= 3 and chars > limits["handoff_warn_chars"]:
            warnings.append(f"{rel} looks like a historical ledger; move long history to artifacts/handoffs or reports and keep latest handoff concise")

    active_context = project / "context" / "active_context.md"
    if active_context.exists():
        files_checked.append("context/active_context.md")
        text = read_text(active_context)
        chars = len(text)
        measured.append({
            "path": "context/active_context.md",
            "chars": chars,
            "estimated_tokens": estimate_tokens(text),
            "warn_chars": limits["active_context_warn_chars"],
            "block_chars": limits["active_context_block_chars"],
            "generated_artifact": True,
        })
        audit_path = project / "context" / "context_audit.json"
        audit_mode = None
        audit: dict[str, Any] = {}
        if audit_path.exists():
            files_checked.append("context/context_audit.json")
            try:
                audit = json.loads(read_text(audit_path))
                audit_mode = audit.get("context_mode")
                if not audit.get("estimated_tokens") and not audit.get("budget_tokens") and chars > 2000:
                    warnings.append("context/context_audit.json lacks token/budget evidence for a non-placeholder generated bundle")
            except json.JSONDecodeError:
                warnings.append("context/context_audit.json is not valid JSON; regenerate context with tools/build_context.py")
        else:
            placeholder = "not mandatory startup context" in text.lower() and chars < 2000
            if not placeholder:
                warnings.append("context/active_context.md exists without context/context_audit.json; regenerate with tools/build_context.py before trusting it")

        stale_hours = limits["generated_context_stale_hours"]
        age_hours = (time.time() - active_context.stat().st_mtime) / 3600
        if stale_hours > 0 and age_hours > stale_hours:
            warnings.append(
                f"context/active_context.md is {age_hours:.1f} hours old; generated bundles are task-specific and should be regenerated when needed"
            )

        if audit_mode == "project_wide_review" and not audit.get("review_justification"):
            blocks.append(
                "context/context_audit.json records project_wide_review without review_justification; broad context loading must be explicitly justified"
            )
        if audit_mode == "project_wide_review" and audit.get("raw_logs_excluded") is False:
            blocks.append(
                "context/context_audit.json records project_wide_review with raw_logs_excluded=false; project-wide reviews must remain summary-first unless doing forensic/incident work"
            )

        if chars > limits["active_context_block_chars"]:
            blocks.append(
                f"context/active_context.md is {chars} chars; generated context exceeds project-wide budget-derived block limit {limits['active_context_block_chars']}"
            )
        elif chars > limits["active_context_warn_chars"] and audit_mode != "project_wide_review":
            warnings.append(
                "context/active_context.md is a large generated bundle; do not load it as startup context, and regenerate a task-specific compact bundle when needed"
            )

    findings = [
        {"severity": "block", "category": "Architectural Inconsistency", "message": item, "migration_class": "Required safety fix", "responsibility": "Generated Project"}
        for item in blocks
    ] + [
        {"severity": "warn", "category": "Implementation Inconsistency", "message": item, "migration_class": "Informational improvement", "responsibility": "Generated Project"}
        for item in warnings
    ]
    return {
        "project": str(project),
        "validation_taxonomy": VALIDATION_CATEGORIES,
        "migration_classes": MIGRATION_CLASSES,
        "blocks": blocks,
        "warnings": warnings,
        "findings": findings,
        "measured": measured,
        "policy": limits,
        "files_checked": files_checked,
        "checks_performed": checks_performed,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Check context artifact size and startup-context hygiene")
    ap.add_argument("--project", default=".")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args()
    report = check(Path(ns.project))
    if ns.json:
        print(json.dumps(report, indent=2))
    else:
        for b in report["blocks"]:
            print(f"BLOCK: {b}", file=sys.stderr)
        for w in report["warnings"]:
            print(f"WARN: {w}")
        print(f"context health: {len(report['blocks'])} block(s), {len(report['warnings'])} warning(s)")
    return 2 if report["blocks"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
