#!/usr/bin/env python3
"""Maintain lightweight `_SUMMARY.md` files used by the context system.

Refresh policy: triggered by folder changes, completed tasks, or context build.
This tool is the canonical summary maintainer; do not maintain a second summary tool.
Tracked summaries are deterministic: volatile refresh timestamps belong in logs, not
in `_SUMMARY.md` files.

Only the `## Contains` inventory is generated. Curated `## Purpose`,
`## Active Work`, and `## Needs Attention` sections are preserved so routine
hygiene does not erase useful agent context.
"""
from __future__ import annotations
import argparse, os, re
from pathlib import Path

IGNORE = {'.git','__pycache__','.venv','node_modules','.pytest_cache','generated','.mypy_cache','.ruff_cache','htmlcov','dist','build'}
DYNAMIC_SUFFIXES = ('-dry-run.md',)
CORE_DIRS = {
    Path('.'), Path('state'), Path('artifacts'), Path('artifacts/decisions'), Path('artifacts/tasks'),
    Path('docs'), Path('instructions'), Path('context'), Path('tools'), Path('permissions'),
    Path('logs'), Path('metrics'), Path('simulation'), Path('question_queue'), Path('knowledge'), Path('recovery')
}
GENERATED_BEGIN = '<!-- PROJECTFORGE:BEGIN-CONTAINS -->'
GENERATED_END = '<!-- PROJECTFORGE:END-CONTAINS -->'

GOVERNANCE_PURPOSE_DEFAULTS = {
    'artifacts': 'Durable governance history root for project-owned task, decision, report, and handoff accountability records. Current state belongs in state/ and context/latest_handoff.md; historical artifacts should be amended or superseded rather than rewritten merely to look clean.',
    'artifacts/tasks': 'Durable governance records for substantive work that must survive the current session. Tasks record request, status, scope/non-scope, outcome, and related decisions/reports/handoffs; they are not hidden chat plans or a project-management product.',
    'artifacts/decisions': 'Durable governance records for choices affecting scope, responsibility, architecture, policy, external dependencies, approval boundaries, or future agent behavior. Decisions record rationale, alternatives, consequences, and status.',
    'artifacts/reports': 'Durable governance records for review, audit, investigation, architecture-to-reality, implementation, or synthesis findings. Reports preserve evidence and findings; recommendations do not automatically become tasks.',
    'artifacts/handoffs': 'Durable governance history for handoff snapshots when context/latest_handoff.md should remain concise. Handoffs preserve continuity, not complete project history.',
}


def entries_for(d: Path) -> list[str]:
    return [
        p.name + ('/' if p.is_dir() else '')
        for p in sorted(d.iterdir())
        if p.name not in IGNORE
        and p.name != '_SUMMARY.md'
        and not any(p.name.endswith(suffix) for suffix in DYNAMIC_SUFFIXES)
    ]


def section(text: str, heading: str, default: str) -> str:
    pattern = rf'(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)'
    match = re.search(pattern, text)
    if not match:
        return default.strip()
    content = match.group(1).strip()
    # Old generated summaries used generic boilerplate. Replace that with durable defaults.
    generic = {
        'Purpose': ['Auto-maintained context-map summary', 'TODO: Maintain a concise description'],
        'Active Work': ['Not specified.'],
        'Needs Attention': ['Keep this summary current when changing this folder.'],
    }
    if any(token in content for token in generic.get(heading, [])):
        return default.strip()
    return content or default.strip()


def legacy_purpose(text: str) -> str | None:
    match = re.search(r'(?m)^Purpose:\s*(.*)$', text)
    if not match:
        return None
    value = match.group(1).strip()
    if 'Auto-maintained context-map summary' in value:
        return None
    return value or None


def summarize_content(d: Path, root: Path) -> str:
    rel = '.' if d == root else str(d.relative_to(root))
    existing = (d / '_SUMMARY.md').read_text(encoding='utf-8') if (d / '_SUMMARY.md').exists() else ''
    purpose_default = GOVERNANCE_PURPOSE_DEFAULTS.get(rel, f'This folder is part of the project-local file-backed operating system for `{rel}`.')
    purpose = section(existing, 'Purpose', legacy_purpose(existing) or purpose_default)
    active = section(existing, 'Active Work', '- No folder-specific active work recorded.')
    needs = section(existing, 'Needs Attention', '- No folder-specific issues recorded.')
    contains = ''.join(f'- `{e}`\n' for e in entries_for(d)[:120]) or '- Empty or placeholder-only folder.\n'
    return (
        f'# Folder Summary: {rel}\n\n'
        f'## Purpose\n{purpose}\n\n'
        f'## Contains\n{GENERATED_BEGIN}\n{contains}{GENERATED_END}\n\n'
        f'## Active Work\n{active}\n\n'
        f'## Needs Attention\n{needs}\n'
    )


def should_include(p: Path, root: Path, max_depth: int, core_only: bool) -> bool:
    rel = Path('.') if p == root else p.relative_to(root)
    if core_only:
        return rel in CORE_DIRS
    depth = len(rel.parts) if rel != Path('.') else 0
    return depth <= max_depth


def summarize_dir(d: Path, root: Path) -> bool:
    content = summarize_content(d, root)
    target = d / '_SUMMARY.md'
    if target.exists() and target.read_text(encoding='utf-8') == content:
        return False
    target.write_text(content, encoding='utf-8')
    return True


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--project', default='.'); ap.add_argument('--max-depth', type=int, default=2); ap.add_argument('--core-only', action='store_true')
    ns=ap.parse_args(); root=Path(ns.project).resolve(); changed=0
    for d, subdirs, files in os.walk(root):
        p=Path(d); subdirs[:] = [s for s in subdirs if s not in IGNORE]
        if should_include(p, root, ns.max_depth, ns.core_only):
            changed += int(summarize_dir(p, root))
    print(root); return 0
if __name__ == '__main__': raise SystemExit(main())
