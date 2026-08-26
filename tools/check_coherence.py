#!/usr/bin/env python3
"""ProjectForge coherence checker.

Supports root factory projects and generated projects. Root mode validates the
ProjectForge factory contract; generated mode validates the lighter project-local
contract produced by `tools/new_project.py`.

System 5 responsibility: deterministic structural and project-local invariant
checks only. This tool does not judge project quality, run CI, manage workflow,
or replace human architectural judgment.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover - optional dependency
    yaml = None

ROOT_REQUIRED = [
    'CONSTITUTION.md','projectforge.yaml','state/active_goal.md','state/project_state.md',
    'state/architecture.md','permissions/allowlist.yaml','permissions/denylist.yaml',
    'permissions/escalation_rules.yaml','context/context_policy.yaml','simulation/dry_run_policy.yaml',
    'metrics/metrics_policy.yaml','recovery/escalation_policy.yaml','recovery/continuity_framework.md','hardware/profile.yaml',
    'automation/orchestration_schedule.yaml','docs/OPERATOR_MANUAL.md','tools/architecture_reality_audit.py','tools/recover_session.py'
]

GENERATED_REQUIRED = [
    'CONSTITUTION.md','AGENTS.md','project.yaml','state/active_goal.md','state/project_state.md',
    'state/architecture.md','permissions/allowlist.yaml','permissions/denylist.yaml',
    'permissions/escalation_rules.yaml','context/context_policy.yaml','simulation/dry_run_policy.yaml',
    'metrics/metrics_policy.yaml','recovery/escalation_policy.yaml','recovery/continuity_framework.md','hardware/profile.yaml',
    'tools/check_coherence.py','tools/run.py','tools/architecture_reality_audit.py','tools/recover_session.py',
    'tools/context_health.py','tools/build_context.py','architecture/architecture_state.md'
]

IDENTITY_SECTIONS = [
    'Project identity','Scope','Explicit non-scope','Responsibility boundaries',
    'Operating principles','Instruction hierarchy','Generated-project independence'
]

PRIORITY_1_FILES = [
    'CONSTITUTION.md','state/active_goal.md','state/project_state.md',
    'state/architecture.md','context/latest_handoff.md'
]

GOVERNANCE_DIRS = [
    'artifacts/tasks','artifacts/decisions','artifacts/reports','artifacts/handoffs'
]
GOVERNANCE_TEMPLATES = {
    'artifacts/tasks/TEMPLATE.md': ['Status:', '## Request', '## Scope', '## Explicit non-scope', '## Methodology slice', '## Governance links', '## Outcome'],
    'artifacts/decisions/TEMPLATE.md': ['Status:', '## Decision', '## Rationale', '## Alternatives considered', '## Consequences', '## Approval boundary'],
    'artifacts/reports/TEMPLATE.md': ['Date:', 'Type:', 'Status:', '## Evidence consulted', '## Findings', '## Methodology observations', '## Follow-up governance'],
}
APPROVAL_TERMS = ['destructive', 'external publication', 'remote push', 'paid resources', 'credential', 'production data', 'major scope', 'architecture changes']
FORBIDDEN_GENERATED_TERMS = ['ProjectForge', 'EIP', 'MacroForge', 'KnowledgeForge', 'Meta' + 'Harvest', 'Architecture' + 'Harvest', 'architecture' + 'harvest']
UNRESOLVED_PLACEHOLDERS = ['{' + 'project_name}', '{' + 'identity_']
METHODOLOGY_TERMS = ['bounded implementation slice', 'explicit non-goals', 'implementation boundary', 'readiness', 'success criteria', 'verification expectations', 'expected evidence', 'post-slice decision', 'Evidence-gated architectural evolution']
METHODOLOGY_FORBIDDEN = ['scrum', 'kanban', 'sprint', 'issue tracker', 'workflow engine', 'quality management system', 'ci/cd']

VALIDATION_CATEGORIES = {
    'constitutional_violation': 'Constitutional Violation',
    'architectural_inconsistency': 'Architectural Inconsistency',
    'implementation_inconsistency': 'Implementation Inconsistency',
    'historical_compatibility': 'Historical Compatibility',
    'sovereign_divergence': 'Sovereign Divergence',
    'informational': 'Informational',
}

MIGRATION_CLASSES = {
    'required_constitutional_fix': 'Required constitutional fix',
    'required_safety_fix': 'Required safety fix',
    'architectural_recommendation': 'Architectural recommendation',
    'optional_capability_promotion': 'Optional capability promotion',
    'historical_compatibility_notice': 'Historical compatibility notice',
    'informational_improvement': 'Informational improvement',
}

PROJECTFORGE_AUTHORITY_PATTERNS = [
    r'governed by ProjectForge',
    r'ProjectForge governs',
    r'ProjectForge owns',
    r'ProjectForge authority',
    r'controlled by ProjectForge',
    r'managed by ProjectForge',
    r'must adopt ProjectForge',
    r'ProjectForge approval required',
]

def read(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace') if path.exists() else ''


def has_text(path: Path, needle: str) -> bool:
    return needle.lower() in read(path).lower()


def load_yaml_file(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    return data or {}


def add_evidence(evidence: list[dict[str, Any]], check: str, files: list[str], detail: str) -> None:
    evidence.append({'check': check, 'files_checked': files, 'detail': detail})


def add_finding(findings: list[dict[str, Any]], severity: str, category: str, message: str, *,
                rule: str = '', migration_class: str = '', responsibility: str = '', evidence: str = '') -> None:
    findings.append({
        'severity': severity,
        'category': VALIDATION_CATEGORIES.get(category, category),
        'rule': rule,
        'message': message,
        'migration_class': MIGRATION_CLASSES.get(migration_class, migration_class) if migration_class else '',
        'responsibility': responsibility,
        'evidence': evidence,
    })


def split_findings(findings: list[dict[str, Any]]) -> tuple[list[str], list[str], list[dict[str, Any]]]:
    blocks = [f['message'] for f in findings if f.get('severity') == 'block']
    warnings = [f['message'] for f in findings if f.get('severity') == 'warn']
    observations = [f for f in findings if f.get('severity') in {'info', 'observe'}]
    return blocks, warnings, observations


def is_mature_sovereign_project(root: Path) -> bool:
    if (root / 'projectforge.yaml').exists():
        return False
    task_files = len([p for p in (root / 'artifacts' / 'tasks').glob('*.md') if p.name not in {'_SUMMARY.md', 'TEMPLATE.md'}]) if (root / 'artifacts' / 'tasks').exists() else 0
    report_files = len([p for p in (root / 'artifacts' / 'reports').glob('*.md') if p.name not in {'_SUMMARY.md', 'TEMPLATE.md'}]) if (root / 'artifacts' / 'reports').exists() else 0
    current_text = '\n'.join(read(root / rel) for rel in ['README.md', '_SUMMARY.md', 'state/project_state.md', 'state/architecture.md'])
    markers = ['compatibility/history', 'sovereign', 'domain expansion', 'architecturally stable', 'generated-project', 'project-specific']
    marker_hits = sum(1 for marker in markers if marker in current_text.lower())
    return (task_files + report_files) >= 10 or (task_files >= 3 and marker_hits >= 2)


def classify_template_severity(root: Path) -> tuple[str, str, str]:
    if is_mature_sovereign_project(root):
        return 'warn', 'sovereign_divergence', 'architectural_recommendation'
    return 'block', 'architectural_inconsistency', 'required_constitutional_fix'


def classify_issue(message: str, severity: str) -> dict[str, Any]:
    lower = message.lower()
    category = 'Implementation Inconsistency'
    migration = 'Architectural recommendation'
    responsibility = 'Generated Project'
    if 'external-authority leakage' in lower or 'unresolved template placeholders' in lower or 'push rule missing' in lower or 'capability escalation missing' in lower:
        category = 'Constitutional Violation'
        migration = 'Required constitutional fix'
        responsibility = 'ProjectForge Factory' if 'template' in lower else 'Generated Project'
    elif 'context health:' in lower:
        category = 'Architectural Inconsistency' if severity == 'block' else 'Implementation Inconsistency'
        migration = 'Required safety fix' if severity == 'block' else 'Informational improvement'
    elif 'missing required file' in lower or 'missing required startup file' in lower or 'missing required context/recovery tool' in lower or 'missing governance directory' in lower:
        category = 'Architectural Inconsistency'
        migration = 'Required constitutional fix'
    elif lower.startswith('historical compatibility:') or 'compatibility' in lower:
        category = 'Historical Compatibility'
        migration = 'Historical compatibility notice'
        responsibility = 'Historical Compatibility'
    elif lower.startswith('sovereign divergence:') or 'template drift' in lower or 'does not reference work_execution_methodology' in lower or 'missing methodology file' in lower or 'missing governance template' in lower or 'missing required text' in lower:
        category = 'Sovereign Divergence' if severity == 'warn' else 'Architectural Inconsistency'
        migration = 'Architectural recommendation' if severity == 'warn' else 'Required constitutional fix'
    elif 'warn' == severity:
        migration = 'Informational improvement'
    return {
        'severity': severity,
        'category': category,
        'message': message,
        'migration_class': migration,
        'responsibility': responsibility,
    }


def classified_issues(blocks: list[str], warnings: list[str]) -> list[dict[str, Any]]:
    return [classify_issue(item, 'block') for item in blocks] + [classify_issue(item, 'warn') for item in warnings]


def require_text(path: Path, needles: list[str], issues: list[str], label: str, *,
                 severity: str = 'block', category: str = 'architectural_inconsistency',
                 migration_class: str = 'required_constitutional_fix', rule: str = 'required_text') -> None:
    text = read(path).lower()
    for needle in needles:
        if needle.lower() not in text:
            prefix = '' if severity == 'block' else f'{VALIDATION_CATEGORIES.get(category, category)}: '
            issues.append(f'{prefix}{label} missing required text: {needle}')


GENERATED_INDEPENDENCE_SCAN_FILES = [
    'CONSTITUTION.md', 'AGENTS.md', 'project.yaml',
    'state/active_goal.md', 'state/project_state.md', 'state/architecture.md',
    'context/context_policy.yaml', 'context/latest_handoff.md',
    'instructions/GENERAL_INSTRUCTIONS.md', 'instructions/WORK_EXECUTION_METHODOLOGY.md',
    'artifacts/tasks/TEMPLATE.md', 'artifacts/decisions/TEMPLATE.md', 'artifacts/reports/TEMPLATE.md',
]


def iter_project_text_files(root: Path):
    # Generated-project independence is an authority/context invariant, not a
    # ban on historical tool names in copied local helper scripts or summaries.
    for rel in GENERATED_INDEPENDENCE_SCAN_FILES:
        path = root / rel
        if path.exists() and path.is_file():
            yield path


def check_identity_contract(root: Path, blocks: list[str], warns: list[str], evidence: list[dict[str, Any]], *, base: str = '') -> None:
    constitution = root / base / 'CONSTITUTION.md'
    agents = root / base / 'AGENTS.md'
    mature = not base and is_mature_sovereign_project(root)
    target = warns if mature else blocks
    require_text(
        constitution,
        IDENTITY_SECTIONS,
        target,
        f'{base}CONSTITUTION.md' if base else 'CONSTITUTION.md',
        severity='warn' if mature else 'block',
        category='sovereign_divergence' if mature else 'architectural_inconsistency',
        migration_class='architectural_recommendation' if mature else 'required_constitutional_fix',
    )
    if agents.exists() and 'constitution.md' not in read(agents).lower():
        target.append(f'{base}AGENTS.md does not point to CONSTITUTION.md as identity authority')
    detail = 'checked identity sections, instruction hierarchy, independence doctrine, and AGENTS pointer'
    if mature:
        detail += '; mature sovereign project template drift is reported as warning, not constitutional failure'
    add_evidence(evidence, 'identity structural contract', [str(Path(base) / 'CONSTITUTION.md'), str(Path(base) / 'AGENTS.md')], detail)


def check_generated_independence(root: Path, blocks: list[str], evidence: list[dict[str, Any]], warns: list[str] | None = None) -> None:
    authority_hits: list[str] = []
    identity_mentions: list[str] = []
    historical_mentions: list[str] = []
    placeholder_hits: list[str] = []
    mature = is_mature_sovereign_project(root)
    project_name = load_yaml_file(root / 'project.yaml').get('project', {}).get('name') or root.name
    allowed_identity_terms = {str(project_name).lower(), root.name.lower()}
    historical_terms = {'architecture' + 'harvest', ('Architecture' + 'Harvest').lower()}
    external_terms = {'projectforge', 'eip', 'macroforge', 'knowledgeforge', 'meta' + 'harvest', 'architecture' + 'harvest'}
    for path in iter_project_text_files(root):
        rel = str(path.relative_to(root)).replace('\\', '/')
        text = read(path)
        lower = text.lower()
        for pattern in PROJECTFORGE_AUTHORITY_PATTERNS:
            if re.search(pattern, text, flags=re.I):
                authority_hits.append(f'{rel}: {pattern}')
        for term in external_terms:
            if term in lower:
                if term in allowed_identity_terms:
                    continue
                if term in historical_terms or 'compatibility' in lower or 'history' in lower:
                    historical_mentions.append(f'{rel}: {term}')
                else:
                    identity_mentions.append(f'{rel}: {term}')
        for marker in UNRESOLVED_PLACEHOLDERS:
            if marker in text:
                placeholder_hits.append(f'{rel}: {marker}')
    if authority_hits:
        blocks.append('generated project contains forbidden external-authority references / external-authority leakage: ' + '; '.join(authority_hits[:20]))
    if identity_mentions and not mature:
        blocks.append('generated project contains forbidden external-authority references: ' + '; '.join(identity_mentions[:20]))
    elif identity_mentions and warns is not None:
        warns.append('Sovereign Divergence: generated project contains project/ecosystem references requiring local ownership interpretation: ' + '; '.join(identity_mentions[:20]))
    if historical_mentions and warns is not None:
        warns.append('Historical Compatibility: retained compatibility or historical references detected: ' + '; '.join(historical_mentions[:20]))
    if placeholder_hits:
        blocks.append('generated project contains unresolved template placeholders: ' + '; '.join(placeholder_hits[:20]))
    add_evidence(evidence, 'generated-project independence scan', ['priority identity/context/governance files'], f'authority_hits={len(authority_hits)}, identity_reference_hits={len(identity_mentions)}, historical_compatibility_hits={len(historical_mentions)}, unresolved_placeholder_hits={len(placeholder_hits)}, mature_sovereign_project={mature}')


def context_priority_files_from_policy(root: Path) -> list[str]:
    policy = load_yaml_file(root / 'context' / 'context_policy.yaml').get('context_policy', {})
    priority = policy.get('context_loading_hierarchy', {}).get('priority_1', {})
    return list(priority.get('files') or [])


def check_context_contract(root: Path, blocks: list[str], evidence: list[dict[str, Any]], *, base: str = '', warns: list[str] | None = None) -> None:
    prefix = Path(base)
    mature = not base and is_mature_sovereign_project(root)
    target = warns if mature and warns is not None else blocks
    if not base:
        for rel in PRIORITY_1_FILES:
            if not (root / prefix / rel).exists():
                blocks.append(f'missing required startup file: {prefix / rel}')
    policy_files = context_priority_files_from_policy(root / prefix)
    if policy_files and policy_files != PRIORITY_1_FILES:
        target.append(f'context policy priority_1 files do not match canonical startup files: {policy_files}')
    for rel in ['tools/build_context.py', 'tools/recover_session.py', 'tools/context_health.py']:
        if not (root / prefix / rel).exists():
            blocks.append(f'missing required context/recovery tool: {prefix / rel}')
    agents = root / prefix / 'AGENTS.md'
    if agents.exists():
        require_text(agents, ['not mandatory startup context', 'Repository-wide exploration is not default startup behavior'], target, f'{prefix / "AGENTS.md"}', severity='warn' if mature else 'block', category='sovereign_divergence' if mature else 'architectural_inconsistency')
    add_evidence(evidence, 'context and recovery structural contract', [str(prefix / rel) for rel in PRIORITY_1_FILES] + [str(prefix / 'context/context_policy.yaml')], 'checked startup files, policy priority_1 consistency, active_context boundary, and required recovery/context tools')


def check_governance_contract(root: Path, blocks: list[str], evidence: list[dict[str, Any]], *, base: str = '', warns: list[str] | None = None) -> None:
    prefix = Path(base)
    mature = not base and is_mature_sovereign_project(root)
    template_target = warns if mature and warns is not None else blocks
    for rel in GOVERNANCE_DIRS:
        if not (root / prefix / rel).is_dir():
            blocks.append(f'missing governance directory: {prefix / rel}')
    for rel, headings in GOVERNANCE_TEMPLATES.items():
        p = root / prefix / rel
        if not p.exists():
            template_target.append(f'missing governance template: {prefix / rel}')
            continue
        require_text(p, headings, template_target, str(prefix / rel), severity='warn' if mature else 'block', category='sovereign_divergence' if mature else 'architectural_inconsistency')
    agents = root / prefix / 'AGENTS.md'
    if agents.exists():
        require_text(agents, APPROVAL_TERMS, template_target, str(prefix / 'AGENTS.md'), severity='warn' if mature else 'block', category='sovereign_divergence' if mature else 'architectural_inconsistency')
    detail = 'checked governance directories, template headings, and approval boundary terms'
    if mature:
        detail += '; template drift is treated as sovereign divergence unless core governance directories are missing'
    add_evidence(evidence, 'governance structural contract', [str(prefix / rel) for rel in GOVERNANCE_DIRS] + [str(prefix / rel) for rel in GOVERNANCE_TEMPLATES], detail)


def check_methodology_contract(root: Path, blocks: list[str], evidence: list[dict[str, Any]], *, base: str = '', warns: list[str] | None = None) -> None:
    prefix = Path(base)
    mature = not base and is_mature_sovereign_project(root)
    template_target = warns if mature and warns is not None else blocks
    methodology = root / prefix / 'instructions' / 'WORK_EXECUTION_METHODOLOGY.md'
    if not methodology.exists():
        template_target.append(f'missing methodology file: {prefix / "instructions/WORK_EXECUTION_METHODOLOGY.md"}')
    else:
        require_text(methodology, METHODOLOGY_TERMS, template_target, str(prefix / 'instructions/WORK_EXECUTION_METHODOLOGY.md'), severity='warn' if mature else 'block', category='sovereign_divergence' if mature else 'architectural_inconsistency')
        require_text(methodology, ['does not define project identity', 'context loading', 'governance record lifecycles', 'validation policy', 'deterministic validators'], template_target, str(prefix / 'instructions/WORK_EXECUTION_METHODOLOGY.md'), severity='warn' if mature else 'block', category='sovereign_divergence' if mature else 'architectural_inconsistency')
        text = read(methodology).lower()
        for term in METHODOLOGY_FORBIDDEN:
            if term in text and f'not {term}' not in text and f'not a {term}' not in text:
                blocks.append(f'methodology file contains prohibited workflow/platform concept outside a clear anti-goal: {term}')
    for rel in ['AGENTS.md', 'instructions/GENERAL_INSTRUCTIONS.md']:
        p = root / prefix / rel
        if p.exists() and 'work_execution_methodology.md' not in read(p).lower():
            template_target.append(f'{prefix / rel} does not reference WORK_EXECUTION_METHODOLOGY.md')
    for rel, needle in [('artifacts/tasks/TEMPLATE.md', '## Methodology slice'), ('artifacts/reports/TEMPLATE.md', '## Methodology observations')]:
        if not has_text(root / prefix / rel, needle):
            template_target.append(f'{prefix / rel} missing methodology section: {needle}')
    detail = 'checked methodology file, references, template sections, separation wording, and prohibited workflow concepts'
    if mature:
        detail += '; missing current methodology template is reported as sovereign divergence unless it creates a constitutional/safety failure'
    add_evidence(evidence, 'work execution methodology structural contract', [str(prefix / 'instructions/WORK_EXECUTION_METHODOLOGY.md'), str(prefix / 'AGENTS.md'), str(prefix / 'artifacts/tasks/TEMPLATE.md'), str(prefix / 'artifacts/reports/TEMPLATE.md')], detail)



def detect_mode(root: Path) -> str:
    return 'root' if (root / 'projectforge.yaml').exists() else 'generated'


def check_common(root: Path, blocks: list[str], warns: list[str], evidence: list[dict[str, Any]]) -> None:
    if (root/'logs'/'index').exists(): warns.append('logs/index exists; SQLite indexing should be opt-in, not default')
    if (root/'models'/'hardware_profile.yaml').exists(): warns.append('models/hardware_profile.yaml is redundant; use hardware/profile.yaml')
    if (root/'tools'/'update_folder_summaries.py').exists(): warns.append('legacy update_folder_summaries.py present; use update_context_summaries.py')
    if not has_text(root/'permissions'/'escalation_rules.yaml','push_requires_human_approval'):
        blocks.append('manual GitHub push rule missing from permissions/escalation_rules.yaml')
    if not has_text(root/'confidence'/'confidence_policy.yaml','codex_or_premium_model'):
        blocks.append('Codex-before-human capability escalation missing from confidence policy')
    if (root/'workspace').exists() and (root/'project.yaml').exists():
        py=read(root/'project.yaml').lower()
        if 'meta_project: true' not in py:
            warns.append('project contains workspace/; generated projects should usually avoid embedded parent workspaces')
    v=root/'tools'/'validate_dry_run.py'
    if v.exists():
        spec=importlib.util.spec_from_file_location('projectforge_validate_dry_run', v)
        mod=importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
        checked = 0
        for report in (root/'simulation'/'dry_runs').glob('*.md') if (root/'simulation'/'dry_runs').exists() else []:
            if report.name in {'README.md','_SUMMARY.md'}:
                continue
            checked += 1
            errs=mod.validate(report)
            if errs: blocks.append(f'invalid dry-run report: {report}: {errs[0]}')
        add_evidence(evidence, 'dry-run report structural validation', ['simulation/dry_runs/*.md'], f'checked_reports={checked}')
    for rel in ['agents/planner.md','agents/coder.md','agents/reviewer.md','agents/auditor.md']:
        p=root/rel
        if p.exists() and 'context used' not in read(p).lower():
            warns.append(f'{rel} does not explicitly require Context used reporting')
    for rel in ['agents/coder.md','agents/reviewer.md']:
        p=root/rel
        txt=read(p).lower()
        if p.exists() and ('knowledge/components.yaml' not in txt or 'knowledge/dependencies.yaml' not in txt):
            blocks.append(f'{rel} does not enforce knowledge-map checks before structural changes')
    if not has_text(root/'logs'/'logging_policy.yaml', 'raw events') and not has_text(root/'logs'/'logging_policy.yaml', 'raw_operational_record'):
        warns.append('logging policy does not clearly define logs as raw operational records')
    if not has_text(root/'metrics'/'metrics_policy.yaml', 'derived'):
        warns.append('metrics policy does not clearly define metrics as derived evidence')
    mature = is_mature_sovereign_project(root) if detect_mode(root) == 'generated' else False
    continuity_target = warns if mature else blocks
    continuity_prefix = 'Sovereign Divergence: ' if mature else ''
    if not has_text(root/'recovery'/'continuity_framework.md', 'Standard project closeout contract'):
        continuity_target.append(f'{continuity_prefix}continuity framework missing standard closeout contract')
    if not has_text(root/'recovery'/'continuity_framework.md', 'Recover project state and continue work'):
        continuity_target.append(f'{continuity_prefix}continuity framework missing fresh-session recovery command contract')
    if not has_text(root/'context'/'context_policy.yaml', 'standard_closeout_order'):
        continuity_target.append(f'{continuity_prefix}context policy missing standard continuity closeout order')
    if not has_text(root/'context'/'context_policy.yaml', 'standard_closeout_command'):
        continuity_target.append(f'{continuity_prefix}context policy missing standard closeout command')
    run_context_health(root, blocks, warns, evidence)


def run_context_health(root: Path, blocks: list[str], warns: list[str], evidence: list[dict[str, Any]]) -> None:
    checker = root / 'tools' / 'context_health.py'
    if not checker.exists():
        warns.append('tools/context_health.py missing; context-size hygiene is not automated')
        return
    spec = importlib.util.spec_from_file_location('projectforge_context_health', checker)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    report = mod.check(root)
    blocks.extend(f'context health: {item}' for item in report.get('blocks', []))
    warns.extend(f'context health: {item}' for item in report.get('warnings', []))
    add_evidence(evidence, 'context health validation', report.get('files_checked', []), f"blocks={len(report.get('blocks', []))}, warnings={len(report.get('warnings', []))}, measured={len(report.get('measured', []))}")


def check_root(root: Path):
    blocks: list[str] = []
    warns: list[str] = []
    evidence: list[dict[str, Any]] = []
    for rel in ROOT_REQUIRED:
        if not (root/rel).exists(): blocks.append(f'missing required file: {rel}')
    check_common(root, blocks, warns, evidence)
    if not has_text(root/'automation'/'orchestration_schedule.yaml', 'check_coherence'):
        blocks.append('automation schedule does not run check_coherence')
    if not has_text(root/'automation'/'orchestration_schedule.yaml', 'validate_dry_run'):
        blocks.append('automation schedule does not run validate_dry_run')
    if not has_text(root/'automation'/'orchestration_schedule.yaml', 'review_metrics'):
        blocks.append('automation schedule does not run review_metrics')
    if not has_text(root/'automation'/'orchestration_schedule.yaml', 'architecture_reality_audit'):
        blocks.append('automation schedule does not run architecture_reality_audit')
    workspace_policy = load_yaml_file(root/'workspace'/'workspace_policy.yaml').get('workspace_policy', {})
    canonical_paths = workspace_policy.get('canonical_paths') or {}
    expected_projects_root = load_yaml_file(root/'projectforge.yaml').get('projectforge', {}).get('defaults', {}).get('workspace_projects_root')
    configured_projects_root = canonical_paths.get('generated_projects_root')
    if not configured_projects_root:
        blocks.append('workspace policy missing canonical generated projects path')
    elif expected_projects_root and configured_projects_root != expected_projects_root:
        blocks.append('workspace policy generated projects path does not match projectforge.yaml defaults.workspace_projects_root')
    # Root factory validation checks the generated-project template contract without treating templates as active project state.
    base = 'templates/_shared_project'
    check_identity_contract(root, blocks, warns, evidence, base=base)
    check_context_contract(root, blocks, evidence, base=base, warns=warns)
    check_governance_contract(root, blocks, evidence, base=base, warns=warns)
    check_methodology_contract(root, blocks, evidence, base=base, warns=warns)
    return blocks, warns, evidence


def check_generated(root: Path):
    blocks: list[str] = []
    warns: list[str] = []
    evidence: list[dict[str, Any]] = []
    for rel in GENERATED_REQUIRED:
        if not (root/rel).exists(): blocks.append(f'missing required file: {rel}')
    check_common(root, blocks, warns, evidence)
    if (root/'tools'/'new_project.py').exists():
        warns.append('generated project contains factory-only tools/new_project.py')
    if has_text(root/'state'/'active_goal.md', 'Project:') and not has_text(root/'state'/'active_goal.md', 'Purpose'):
        warns.append('state/active_goal.md appears underpopulated')
    check_identity_contract(root, blocks, warns, evidence)
    check_context_contract(root, blocks, evidence, warns=warns)
    check_governance_contract(root, blocks, evidence, warns=warns)
    check_methodology_contract(root, blocks, evidence, warns=warns)
    check_generated_independence(root, blocks, evidence, warns=warns)
    return blocks, warns, evidence


def check(root: Path, mode: str = 'auto'):
    if mode == 'auto':
        mode = detect_mode(root)
    if mode == 'root':
        blocks, warns, _ = check_root(root)
        return blocks, warns
    if mode == 'generated':
        blocks, warns, _ = check_generated(root)
        return blocks, warns
    raise ValueError(f'unknown mode: {mode}')


def check_with_evidence(root: Path, mode: str = 'auto') -> dict[str, Any]:
    if mode == 'auto':
        mode = detect_mode(root)
    if mode == 'root':
        blocks, warns, evidence = check_root(root)
    elif mode == 'generated':
        blocks, warns, evidence = check_generated(root)
    else:
        raise ValueError(f'unknown mode: {mode}')
    return {
        'mode': mode,
        'command': 'python3 tools/check_coherence.py --project <project> --json',
        'project': str(root.resolve()),
        'validation_taxonomy': list(VALIDATION_CATEGORIES.values()),
        'migration_classes': list(MIGRATION_CLASSES.values()),
        'mature_sovereign_project': mode == 'generated' and is_mature_sovereign_project(root),
        'blocks': blocks,
        'warnings': warns,
        'findings': classified_issues(blocks, warns),
        'evidence': evidence,
    }


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--project', default='.'); ap.add_argument('--mode', choices=['auto','root','generated'], default='auto'); ap.add_argument('--json', action='store_true')
    ns=ap.parse_args(); root=Path(ns.project).resolve(); report=check_with_evidence(root, ns.mode)
    if ns.json:
        print(json.dumps(report, indent=2))
    else:
        for b in report['blocks']: print(f'BLOCK: {b}', file=sys.stderr)
        for w in report['warnings']: print(f'WARN: {w}')
        print(f"coherence: {len(report['blocks'])} block(s), {len(report['warnings'])} warning(s)")
    return 2 if report['blocks'] else 0
if __name__=='__main__': raise SystemExit(main())
