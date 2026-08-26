#!/usr/bin/env python3
"""Architecture-to-Reality Audit for ProjectForge projects.

This is a lightweight automated drift detector. It does not replace human or
cloud-governance review; it creates an evidence-backed checklist and catches the
mechanical cases that routinely cause architecture/governance drift.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

AUDIT_CATEGORIES = [
    "architecture_vs_implementation",
    "state_files_vs_reality",
    "agent_instructions_vs_behavior",
    "logging_systems",
    "context_management_systems",
    "governance_processes",
    "automation_workflows",
    "templates_vs_generated_projects",
    "subsystem_responsibility_boundaries",
    "validator_ownership_boundaries",
]

DRIFT_TYPES = [
    "drift",
    "obsolete_documentation",
    "duplicated_systems",
    "unused_systems",
    "missing_implementation",
    "implementation_without_documentation",
    "documentation_without_implementation",
]

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

REQUIRED_PROCESS_PHRASES = [
    "Architecture-to-Reality Audit",
    "every 5-10 completed tasks",
    "before major architecture changes",
    "before major governance reviews",
]

ROOT_TOOL_REQUIRED = [
    "tools/check_coherence.py",
    "tools/context_health.py",
    "tools/build_context.py",
    "tools/architecture_reality_audit.py",
]

GENERATED_TOOL_REQUIRED = [
    "tools/check_coherence.py",
    "tools/context_health.py",
    "tools/build_context.py",
    "tools/architecture_reality_audit.py",
]

POLICY_FILES = [
    "CONSTITUTION.md",
    "AGENTS.md",
    "context/context_policy.yaml",
    "docs/OPERATOR_MANUAL.md",
    "automation/orchestration_schedule.yaml",
]

TEMPLATE_POLICY_FILES = [
    "templates/_shared_project/AGENTS.md",
    "templates/_shared_project/context/context_policy.yaml",
    "templates/_shared_project/instructions/GENERAL_INSTRUCTIONS.md",
]

SYSTEM_BOUNDARY_FILES = {
    "identity": "CONSTITUTION.md",
    "context": "context/context_policy.yaml",
    "governance": "AGENTS.md",
    "methodology": "instructions/WORK_EXECUTION_METHODOLOGY.md",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def has(path: Path, text: str) -> bool:
    return text.lower() in read(path).lower()


def estimate_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4) if text else 0


def validation_category_for(severity: str, category: str, drift_type: str, message: str) -> tuple[str, str]:
    lower = message.lower()
    if "authority" in lower or "ownership" in lower:
        return "Constitutional Violation", "Required constitutional fix"
    if category in {"architecture_vs_implementation", "state_files_vs_reality", "context_management_systems", "governance_processes", "subsystem_responsibility_boundaries", "validator_ownership_boundaries"} and severity == "block":
        return "Architectural Inconsistency", "Required safety fix"
    if category == "templates_vs_generated_projects" and severity == "warn":
        return "Implementation Inconsistency", "Architectural recommendation"
    return ("Architectural Inconsistency" if severity == "block" else "Implementation Inconsistency", "Architectural recommendation" if severity == "warn" else "Required safety fix")


def add(items: list[dict[str, str]], severity: str, category: str, drift_type: str, message: str, remediation: str) -> None:
    validation_category, migration_class = validation_category_for(severity, category, drift_type, message)
    items.append({
        "severity": severity,
        "category": category,
        "validation_category": validation_category,
        "migration_class": migration_class,
        "drift_type": drift_type,
        "message": message,
        "remediation": remediation,
    })


def latest_architecture_audit(project: Path) -> Path | None:
    reports = sorted((project / "artifacts" / "reports").glob("R-*-architecture-reality-audit.md"))
    return reports[-1] if reports else None


def completed_tasks_since(project: Path, since: Path | None) -> int:
    since_time = since.stat().st_mtime if since and since.exists() else 0.0
    count = 0
    for task in (project / "artifacts" / "tasks").glob("*.md"):
        if task.name == "_SUMMARY.md":
            continue
        text = read(task).lower()
        if ("status: completed" in text or "status: done" in text or "completed:" in text) and task.stat().st_mtime >= since_time:
            count += 1
    return count


def detect_mode(project: Path) -> str:
    return "root" if (project / "projectforge.yaml").exists() else "generated"


def check_process_documented(project: Path, mode: str, findings: list[dict[str, str]]) -> None:
    files = POLICY_FILES if mode == "root" else ["AGENTS.md", "context/context_policy.yaml", "instructions/GENERAL_INSTRUCTIONS.md"]
    combined = "\n".join(read(project / rel) for rel in files)
    for phrase in REQUIRED_PROCESS_PHRASES:
        if phrase.lower() not in combined.lower():
            add(
                findings,
                "block" if phrase == "Architecture-to-Reality Audit" else "warn",
                "governance_processes",
                "documentation_without_implementation",
                f"Architecture audit process phrase missing from policy/instructions: {phrase}",
                "Document the Architecture-to-Reality Audit cadence, triggers, recording location, and remediation workflow in AGENTS/context policy/operator instructions.",
            )


def check_tools_and_automation(project: Path, mode: str, findings: list[dict[str, str]]) -> None:
    required = ROOT_TOOL_REQUIRED if mode == "root" else GENERATED_TOOL_REQUIRED
    for rel in required:
        if not (project / rel).exists():
            add(findings, "block", "automation_workflows", "missing_implementation", f"Required audit/coherence tool missing: {rel}", "Copy the current ProjectForge tool from templates or restore it before relying on automated governance checks.")

    if mode == "root":
        schedule = project / "automation" / "orchestration_schedule.yaml"
        if not has(schedule, "architecture_reality_audit"):
            add(findings, "block", "automation_workflows", "missing_implementation", "orchestration schedule does not run architecture_reality_audit", "Add Architecture-to-Reality Audit to periodic and pre-major-governance automation.")
        hygiene = project / "tools" / "orchestrator_hygiene.py"
        if not has(hygiene, "architecture_reality_audit.py"):
            add(findings, "warn", "automation_workflows", "implementation_without_documentation", "orchestrator_hygiene.py does not invoke architecture_reality_audit.py", "Add the audit command to periodic/all hygiene phases so routine automation can execute it.")


def check_context_and_state(project: Path, findings: list[dict[str, str]]) -> None:
    state_files = ["state/active_goal.md", "state/project_state.md", "state/architecture.md"]
    for rel in state_files:
        p = project / rel
        if not p.exists():
            add(findings, "block", "state_files_vs_reality", "missing_implementation", f"Missing primary state file: {rel}", "Restore the primary state artifact or regenerate the project scaffold.")
            continue
        text = read(p)
        if estimate_tokens(text) > 3500:
            add(findings, "warn", "state_files_vs_reality", "drift", f"{rel} is large for a current-state artifact (~{estimate_tokens(text)} tokens)", "Summarize current truth in state and move history/evidence to task artifacts, reports, handoffs, or derived logs.")
        historical_markers = len(re.findall(r"\b(completed|implemented|verification|changed files|diff|commit|log)\b", text, flags=re.I))
        if historical_markers > 20:
            add(findings, "warn", "state_files_vs_reality", "obsolete_documentation", f"{rel} appears to accumulate implementation history", "Keep only active/current pointers in state; move historical details to reports or task artifacts.")

    if not has(project / "context" / "context_policy.yaml", "context_loading_hierarchy"):
        add(findings, "block", "context_management_systems", "documentation_without_implementation", "context policy lacks explicit context_loading_hierarchy", "Upgrade context/context_policy.yaml from current ProjectForge templates.")
    if not has(project / "context" / "context_policy.yaml", "architecture_reality_audit"):
        add(findings, "warn", "governance_processes", "documentation_without_implementation", "context policy lacks Architecture-to-Reality Audit governance settings", "Add architecture_reality_audit policy with cadence, categories, and report location.")


def check_agent_instruction_alignment(project: Path, mode: str, findings: list[dict[str, str]]) -> None:
    agent_files = list((project / "agents").glob("*.md")) if (project / "agents").exists() else []
    if not agent_files:
        add(findings, "warn", "agent_instructions_vs_behavior", "missing_implementation", "No role agent instruction files found under agents/", "Generated projects should inherit role prompts or document why this project uses only AGENTS.md.")
        return
    for p in agent_files:
        if p.name.startswith("_"):
            continue
        txt = read(p).lower()
        if "context used" not in txt:
            add(findings, "warn", "agent_instructions_vs_behavior", "drift", f"{p.relative_to(project)} does not require Context used reporting", "Update role prompt from ProjectForge templates or add explicit Context used reporting.")
        if "architecture-to-reality" not in txt and p.name in {"auditor.md", "reviewer.md", "planner.md"}:
            add(findings, "warn", "agent_instructions_vs_behavior", "documentation_without_implementation", f"{p.relative_to(project)} does not mention Architecture-to-Reality Audit triggers", "Add audit-trigger guidance to governance/review/planning roles.")


def check_logging_and_metrics(project: Path, findings: list[dict[str, str]]) -> None:
    if not has(project / "logs" / "logging_policy.yaml", "raw"):
        add(findings, "warn", "logging_systems", "obsolete_documentation", "logging policy does not clearly define raw operational logs", "Clarify logs/raw vs logs/derived separation in logs/logging_policy.yaml.")
    if not has(project / "metrics" / "metrics_policy.yaml", "derived"):
        add(findings, "warn", "logging_systems", "obsolete_documentation", "metrics policy does not clearly define metrics as derived evidence", "Clarify metrics as derived evidence, not raw logs.")


def check_templates(project: Path, mode: str, findings: list[dict[str, str]]) -> None:
    if mode != "root":
        return
    for rel in TEMPLATE_POLICY_FILES:
        if not (project / rel).exists():
            add(findings, "block", "templates_vs_generated_projects", "missing_implementation", f"Template policy file missing: {rel}", "Restore shared generated-project template file.")
            continue
        if not has(project / rel, "Architecture-to-Reality Audit"):
            add(findings, "block", "templates_vs_generated_projects", "documentation_without_implementation", f"Template does not inherit Architecture-to-Reality Audit guidance: {rel}", "Patch shared template so future generated projects inherit the audit process.")
    for rel in ["templates/_shared_project/tools/architecture_reality_audit.py", "templates/_shared_project/tools/check_coherence.py"]:
        if not (project / rel).exists():
            add(findings, "block", "templates_vs_generated_projects", "missing_implementation", f"Generated-project template missing tool: {rel}", "Copy root tool into templates/_shared_project/tools/.")



def check_subsystem_responsibility_drift(project: Path, mode: str, findings: list[dict[str, str]]) -> None:
    """Advisory checks for System 1-5 boundary drift.

    Coherence owns hard structural validation. This audit only reports likely
    architectural drift: duplicated doctrine, validation platform creep, or
    documentation/tool mismatch.
    """
    if (project / "instructions" / "VALIDATION_AND_EVIDENCE.md").exists():
        add(
            findings,
            "warn",
            "validator_ownership_boundaries",
            "duplicated_systems",
            "Standalone VALIDATION_AND_EVIDENCE.md exists even though validation policy should remain distributed across existing architecture",
            "Remove or merge standalone validation doctrine into existing tool/policy locations unless a later accepted decision changes System 5 boundaries.",
        )

    methodology = project / "instructions" / "WORK_EXECUTION_METHODOLOGY.md"
    if methodology.exists():
        text = read(methodology).lower()
        platform_terms = ["ci/cd", "workflow engine", "quality management system", "static analysis framework"]
        for term in platform_terms:
            if term in text and f"not {term}" not in text and f"not a {term}" not in text:
                add(
                    findings,
                    "warn",
                    "subsystem_responsibility_boundaries",
                    "drift",
                    f"Methodology file appears to contain validation/platform responsibility: {term}",
                    "Keep validation/tool ownership in existing validation tools and keep methodology limited to how bounded work is performed.",
                )

    agents = read(project / "AGENTS.md")
    if agents.lower().count("bounded implementation slice") > 3:
        add(
            findings,
            "warn",
            "subsystem_responsibility_boundaries",
            "duplicated_systems",
            "AGENTS.md appears to duplicate methodology doctrine instead of pointing to WORK_EXECUTION_METHODOLOGY.md",
            "Keep AGENTS.md concise and delegate detailed methodology to instructions/WORK_EXECUTION_METHODOLOGY.md.",
        )

    if mode == "root":
        for rel in [
            "templates/_shared_project/tools/check_coherence.py",
            "templates/_shared_project/tools/context_health.py",
            "templates/_shared_project/tools/architecture_reality_audit.py",
            "templates/_shared_project/tools/recover_session.py",
        ]:
            if not (project / rel).exists():
                add(findings, "block", "templates_vs_generated_projects", "missing_implementation", f"Generated-project template missing validation/recovery tool: {rel}", "Copy the project-owned tool into templates/_shared_project/tools/ so generated projects remain independent.")
        root_coherence = read(project / "tools" / "check_coherence.py")
        template_coherence = read(project / "templates" / "_shared_project" / "tools" / "check_coherence.py")
        if root_coherence and template_coherence and "generated-project independence scan" not in template_coherence:
            add(
                findings,
                "warn",
                "templates_vs_generated_projects",
                "templates_vs_generated_projects",
                "Template check_coherence.py does not include current generated-project independence evidence checks",
                "Copy the current root check_coherence.py into templates/_shared_project/tools/check_coherence.py after validator changes are complete.",
            )

    # Duplicated identity doctrine outside CONSTITUTION should stay rare and referential.
    identity_phrase = "generated-project independence"
    duplicate_paths = []
    for rel in ["AGENTS.md", "state/project_state.md", "state/architecture.md", "instructions/GENERAL_INSTRUCTIONS.md"]:
        if identity_phrase in read(project / rel).lower():
            duplicate_paths.append(rel)
    if len(duplicate_paths) > 2:
        add(
            findings,
            "warn",
            "subsystem_responsibility_boundaries",
            "duplicated_systems",
            f"Identity doctrine appears duplicated outside CONSTITUTION.md: {', '.join(duplicate_paths)}",
            "Prefer concise pointers to CONSTITUTION.md instead of repeating identity doctrine in operational files.",
        )

def check_architecture_docs(project: Path, findings: list[dict[str, str]]) -> None:
    arch = project / "state" / "architecture.md"
    if not arch.exists():
        return
    arch_text = read(arch).lower()
    implementation_markers = ["tools/", "context/", "agents/", "templates/", "logs/", "metrics/"]
    missing = [m for m in implementation_markers if m.rstrip("/") in arch_text and not (project / m).exists()]
    for marker in missing:
        add(findings, "warn", "architecture_vs_implementation", "documentation_without_implementation", f"architecture.md references {marker} but path is missing", "Either restore the implementation path or update architecture.md to reflect current reality.")
    if "architecture-to-reality" in "\n".join(read(project / rel) for rel in POLICY_FILES if (project / rel).exists()).lower() and not (project / "tools" / "architecture_reality_audit.py").exists():
        add(findings, "block", "architecture_vs_implementation", "documentation_without_implementation", "Architecture-to-Reality Audit is documented but the tool is missing", "Restore tools/architecture_reality_audit.py.")


def check(project: Path) -> dict[str, Any]:
    project = project.resolve()
    mode = detect_mode(project)
    findings: list[dict[str, str]] = []
    latest = latest_architecture_audit(project)
    completed = completed_tasks_since(project, latest)

    check_process_documented(project, mode, findings)
    check_tools_and_automation(project, mode, findings)
    check_context_and_state(project, findings)
    check_agent_instruction_alignment(project, mode, findings)
    check_logging_and_metrics(project, findings)
    check_templates(project, mode, findings)
    check_subsystem_responsibility_drift(project, mode, findings)
    check_architecture_docs(project, findings)

    if completed >= 10:
        add(findings, "block", "governance_processes", "drift", f"{completed} completed task(s) since last Architecture-to-Reality Audit", "Run and record an Architecture-to-Reality Audit before continuing major work.")
    elif completed >= 5:
        add(findings, "warn", "governance_processes", "drift", f"{completed} completed task(s) since last Architecture-to-Reality Audit", "Schedule an Architecture-to-Reality Audit soon; cadence is every 5-10 completed tasks.")

    blocks = [f for f in findings if f["severity"] == "block"]
    warnings = [f for f in findings if f["severity"] == "warn"]
    return {
        "project": str(project),
        "mode": mode,
        "timestamp": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "audit_categories": AUDIT_CATEGORIES,
        "drift_types": DRIFT_TYPES,
        "validation_taxonomy": VALIDATION_CATEGORIES,
        "migration_classes": MIGRATION_CLASSES,
        "latest_architecture_reality_audit": str(latest.relative_to(project)) if latest else None,
        "completed_tasks_since_latest_audit": completed,
        "command": "python3 tools/architecture_reality_audit.py --project <project> --json",
        "files_checked": sorted({rel for rel in POLICY_FILES if (project / rel).exists()} | {rel for rel in TEMPLATE_POLICY_FILES if (project / rel).exists()} | {"state/active_goal.md", "state/project_state.md", "state/architecture.md"}),
        "checks_performed": [
            "architecture_audit_process_documentation",
            "tool_and_automation_alignment",
            "context_and_state_drift",
            "agent_instruction_alignment",
            "logging_and_metrics_drift",
            "template_inheritance",
            "subsystem_responsibility_drift",
            "architecture_documentation_reality",
            "audit_cadence",
        ],
        "blocks": blocks,
        "warnings": warnings,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Architecture-to-Reality Audit",
        "",
        f"Date: {report['timestamp']}",
        f"Project: {report['project']}",
        f"Mode: {report['mode']}",
        f"Latest previous audit: {report['latest_architecture_reality_audit'] or 'none'}",
        f"Completed tasks since latest audit: {report['completed_tasks_since_latest_audit']}",
        "",
        "## Scope",
        "",
        "This audit checks documented architecture, governance rules, operating procedures, state artifacts, templates, automation, logging/context systems, and available implementation for drift.",
        "",
        "## Categories",
        "",
    ]
    lines.extend(f"- {cat}" for cat in report["audit_categories"])
    lines.extend(["", "## Drift types", ""])
    lines.extend(f"- {kind}" for kind in report["drift_types"])
    for title, key in [("Blocks", "blocks"), ("Warnings", "warnings")]:
        lines.extend(["", f"## {title}", ""])
        if not report[key]:
            lines.append("None.")
        for item in report[key]:
            lines.extend([
                f"- Category: {item['category']}",
                f"  Drift type: {item['drift_type']}",
                f"  Finding: {item['message']}",
                f"  Remediation: {item['remediation']}",
            ])
    lines.extend([
        "",
        "## Remediation workflow",
        "",
        "1. Fix blocks before major architecture/governance work continues.",
        "2. Convert durable policy or architecture changes into decision artifacts.",
        "3. Update implementation, templates, docs, and state together so future projects inherit the correction.",
        "4. Refresh affected folder summaries and latest handoff.",
        "5. Rerun `tools/architecture_reality_audit.py`, `tools/check_coherence.py`, and relevant tests.",
    ])
    return "\n".join(lines) + "\n"


def write_report(project: Path, report: dict[str, Any]) -> Path:
    today = dt.date.today().isoformat().replace("-", "")
    out = project / "artifacts" / "reports" / f"R-{today}-architecture-reality-audit.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_markdown(report), encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Run ProjectForge Architecture-to-Reality Audit.")
    ap.add_argument("--project", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-report", action="store_true", help="Write artifacts/reports/R-YYYYMMDD-architecture-reality-audit.md")
    ns = ap.parse_args()

    project = Path(ns.project).resolve()
    report = check(project)
    report_path = None
    if ns.write_report:
        report_path = write_report(project, report)
        report["report_path"] = str(report_path)

    if ns.json:
        print(json.dumps(report, indent=2))
    else:
        if report_path:
            print(f"Report: {report_path}")
        for item in report["blocks"]:
            print(f"BLOCK: {item['message']}", file=sys.stderr)
        for item in report["warnings"]:
            print(f"WARN: {item['message']}")
        print(f"architecture-reality-audit: {len(report['blocks'])} block(s), {len(report['warnings'])} warning(s)")
    return 2 if report["blocks"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
