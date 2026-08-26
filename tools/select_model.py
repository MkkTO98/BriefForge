#!/usr/bin/env python3
"""Select a model from project-local routing policy.

The selector is advisory for Hermes/external agents. It enforces this project's
rule that cloud/Codex choices need an explicit escalation reason and a recent
context audit that fits the configured cloud budget.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

LOCAL_PROVIDERS = {"local", "ollama", "hermes"}
CLOUD_PROVIDERS = {"openai", "anthropic", "google", "openrouter", "external"}
ROUTINE_LOCAL_TASKS = {
    "summarization",
    "folder_summary_update",
    "log_compression",
    "code_search",
    "simple_code_edit",
    "routine_implementation",
    "scaffold_rendering",
    "tests",
}
CLOUD_ESCALATION_REASONS = {
    "architecture_decision",
    "project_audit",
    "strategic_planning",
    "gap_analysis",
    "redesign",
    "consistency_review",
    "local_failed_twice",
    "high_ambiguity",
    "explicit_user_request",
    "safety_critical_destructive_operation",
    "repeated_failure_debugging",
    "security_or_secret_handling",
}


def load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML required. Use `uvx --with pyyaml python tools/select_model.py ...` for one-shot execution, or run `uv venv && uv pip install pyyaml`.")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def model_dirs(project: Path) -> Path:
    if (project / "models").exists():
        return project / "models"
    return Path(__file__).resolve().parents[1] / "models"


def provider_of(registry: dict[str, Any], model: str) -> str:
    return str(registry.get(model, {}).get("provider", "")).lower()


def is_cloud(registry: dict[str, Any], model: str) -> bool:
    provider = provider_of(registry, model)
    return provider in CLOUD_PROVIDERS or model.startswith(("codex", "gpt", "claude"))


def is_local(registry: dict[str, Any], model: str) -> bool:
    return not is_cloud(registry, model) and (provider_of(registry, model) in LOCAL_PROVIDERS or bool(registry.get(model)))


def context_policy(project: Path) -> dict[str, int]:
    data = load_yaml(project / "context" / "context_policy.yaml").get("context_policy", {}) if (project / "context" / "context_policy.yaml").exists() else {}
    budgets = data.get("budgets", {})
    return {
        "cloud_budget": int(budgets.get("cloud_governance_tokens", budgets.get("cloud_model_tokens", min(int(data.get("default_budget_tokens", 24000)), 10000)))),
        "project_wide_budget": int(budgets.get("project_wide_review_tokens", 64000)),
        "local_budget": int(budgets.get("local_model_tokens", int(data.get("default_budget_tokens", 24000)))),
    }


def validate_cloud_audit(project: Path, audit_arg: str, cloud_budget: int, project_wide_budget: int) -> tuple[bool, str]:
    if not audit_arg:
        return False, "cloud model requires context audit report via --context-audit pointing to context/context_audit.json"
    path = Path(audit_arg)
    if not path.is_absolute():
        path = project / audit_arg
    if not path.exists():
        return False, f"context audit not found: {path}"
    audit = json.loads(path.read_text(encoding="utf-8"))
    if not audit.get("raw_logs_excluded", False):
        return False, "context audit does not confirm raw logs were excluded"
    if not audit.get("summaries_used", False):
        return False, "context audit does not confirm summaries were used"
    tokens = int(audit.get("estimated_tokens", 0))
    budget = int(audit.get("budget_tokens", cloud_budget))
    context_mode = str(audit.get("context_mode", "normal"))
    review_justification = str(audit.get("review_justification", "")).strip()
    if context_mode == "project_wide_review":
        if not review_justification:
            return False, "project-wide cloud review requires an audit review_justification"
        effective_budget = min(budget, project_wide_budget)
    else:
        effective_budget = min(budget, cloud_budget)
    if tokens > effective_budget:
        return False, f"audited context has {tokens} tokens, above {context_mode} budget {effective_budget}"
    return True, f"context audit passed ({tokens}/{effective_budget} tokens, mode={context_mode})"


def main() -> int:
    p = argparse.ArgumentParser(description="Select a model from project-local routing policy.")
    p.add_argument("--project", default=".")
    p.add_argument("--agent", required=True)
    p.add_argument("--task", default="")
    p.add_argument("--failure-count", type=int, default=0)
    p.add_argument("--ambiguity", choices=["low", "medium", "high"], default="low")
    p.add_argument("--escalation-reason", default="", help="Required for cloud/Codex selection")
    p.add_argument("--explicit-cloud", action="store_true")
    p.add_argument("--architecture-decision", action="store_true")
    p.add_argument("--governance", action="store_true", help="Cloud governance task: audit, strategy, gap analysis, consistency review, redesign")
    p.add_argument("--destructive-safety", action="store_true")
    p.add_argument("--context-audit", default="")
    p.add_argument("--json", action="store_true")
    ns = p.parse_args()

    project = Path(ns.project).resolve()
    models_dir = model_dirs(project)
    registry = load_yaml(models_dir / "registry.yaml").get("models", {})
    routing = load_yaml(models_dir / "routing.yaml").get("routing", {})
    budgets = context_policy(project)

    task_route = routing.get("by_task", {}).get(ns.task, {}) if ns.task else {}
    agent_route = routing.get("by_agent", {}).get(ns.agent, {})
    candidates = list(task_route.get("preferred") or agent_route.get("preferred") or registry.keys())

    reasons: list[str] = []
    if ns.architecture_decision or ns.task == "architecture_decision":
        reasons.append("architecture_decision")
    if ns.governance or ns.task in {"project_audit", "strategic_planning", "gap_analysis", "redesign", "consistency_review"}:
        reasons.append(ns.task if ns.task else "project_audit")
    if ns.failure_count >= 2:
        reasons.append("local_failed_twice")
    if ns.ambiguity == "high":
        reasons.append("high_ambiguity")
    if ns.explicit_cloud:
        reasons.append("explicit_user_request")
    if ns.destructive_safety:
        reasons.append("safety_critical_destructive_operation")
    if ns.escalation_reason:
        reasons.append(ns.escalation_reason)
    if ns.task in {"repeated_failure_debugging", "security_or_secret_handling"}:
        reasons.append(ns.task)

    cloud_allowed = any(reason in CLOUD_ESCALATION_REASONS for reason in reasons)

    if ns.task in ROUTINE_LOCAL_TASKS:
        local_candidates = [c for c in candidates if c in registry and is_local(registry, c)]
        choice = local_candidates[0] if local_candidates else next((c for c in candidates if c in registry), candidates[0] if candidates else "unknown")
        why = f"routine task `{ns.task}` uses local-first policy"
    elif cloud_allowed:
        threshold = agent_route.get("escalation_after_failures")
        if threshold is not None and ns.failure_count < int(threshold) and not (ns.explicit_cloud or ns.architecture_decision or ns.governance or ns.ambiguity == "high" or ns.destructive_safety):
            local_candidates = [c for c in candidates if c in registry and is_local(registry, c)]
            choice = local_candidates[0] if local_candidates else next((c for c in candidates if c in registry), candidates[0] if candidates else "unknown")
            why = f"below failure threshold {threshold}; stayed local"
        else:
            cloud_candidates = [c for c in candidates if c in registry and is_cloud(registry, c)]
            choice = cloud_candidates[0] if cloud_candidates else ("codex_supervisor" if "codex_supervisor" in registry else next((c for c in candidates if c in registry), candidates[0] if candidates else "unknown"))
            why = "cloud escalation permitted: " + ", ".join(sorted(set(reasons)))
    else:
        local_candidates = [c for c in candidates if c in registry and is_local(registry, c)]
        choice = local_candidates[0] if local_candidates else next((c for c in candidates if c in registry), candidates[0] if candidates else "unknown")
        why = "no cloud escalation condition met; selected local/smallest sufficient candidate"

    audit_status = "not_required"
    audit_ok = True
    if choice in registry and is_cloud(registry, choice):
        audit_ok, audit_status = validate_cloud_audit(project, ns.context_audit, budgets["cloud_budget"], budgets["project_wide_budget"])
        if not audit_ok:
            result = {"model": choice, "allowed": False, "reason": why, "audit_status": audit_status, "cloud_budget_tokens": budgets["cloud_budget"], "project_wide_budget_tokens": budgets["project_wide_budget"]}
            if ns.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"ERROR: {audit_status}")
            return 2

    result = {"model": choice, "allowed": True, "reason": why, "audit_status": audit_status, "cloud_budget_tokens": budgets["cloud_budget"], "project_wide_budget_tokens": budgets["project_wide_budget"]}
    if ns.json:
        print(json.dumps(result, indent=2))
    else:
        print(choice)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
