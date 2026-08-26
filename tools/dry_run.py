#!/usr/bin/env python3
"""Risk-scaled dry-run helper.

This tool does not execute changes. It creates a dry-run report under
`simulation/dry_runs/` describing proposed changes, risk, dry-run depth,
context used, decisions checked, validation, rollback, and approval needs.
"""
from __future__ import annotations
import argparse, datetime as dt, json, subprocess, sys
from pathlib import Path

LOW_HINTS = {'doc','docs','readme','comment','format','typing','test','summary'}
MEDIUM_HINTS = {'config','refactor','api','pipeline','model','agent','skill','folder','routing','template','workspace'}
HIGH_HINTS = {'delete','remove','schema','permission','credential','secret','deploy','push','install','migration','production','database','rm -rf','sudo'}

def classify(text: str) -> str:
    s = text.lower()
    if any(h in s for h in HIGH_HINTS): return 'high'
    if any(h in s for h in MEDIUM_HINTS): return 'medium'
    if any(h in s for h in LOW_HINTS): return 'low'
    return 'medium'

def depth(risk: str, mode: str) -> str:
    table = {
        'balanced': {'low':'micro_preflight','medium':'standard_dry_run','high':'full_dry_run'},
        'aggressive_safe': {'low':'standard_dry_run','medium':'full_dry_run','high':'full_dry_run_human_review'},
        'speed': {'low':'none','medium':'micro_preflight','high':'full_dry_run'},
    }
    return table.get(mode, table['balanced']).get(risk, 'standard_dry_run')

def split_csv(s: str): return [x.strip() for x in s.split(',') if x.strip()]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', default='.')
    ap.add_argument('--proposal', required=True, help='Short description of proposed change')
    ap.add_argument('--files', default='', help='Comma-separated planned files')
    ap.add_argument('--commands', default='', help='Comma-separated planned commands')
    ap.add_argument('--mode', default='balanced', choices=['balanced','aggressive_safe','speed'])
    ap.add_argument('--risk', choices=['low','medium','high'])
    ap.add_argument('--context-used', default='', help='Comma-separated context files consulted')
    ap.add_argument('--decisions-checked', default='', help='Comma-separated decision artifacts checked')
    ap.add_argument('--validation-plan', default='Run relevant tests and inspect git diff before commit.')
    ap.add_argument('--rollback-plan', default='Use git diff before commit; revert local changes if validation fails.')
    ap.add_argument('--no-validate', action='store_true')
    ns = ap.parse_args()
    project = Path(ns.project).resolve()
    risk = ns.risk or classify(' '.join([ns.proposal, ns.files, ns.commands]))
    d = depth(risk, ns.mode)
    stamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    outdir = project/'simulation'/'dry_runs'; outdir.mkdir(parents=True, exist_ok=True)
    report = {
        'timestamp': stamp,
        'proposal': ns.proposal,
        'risk': risk,
        'mode': ns.mode,
        'dry_run_depth': d,
        'files': split_csv(ns.files),
        'commands': split_csv(ns.commands),
        'validation_plan': ns.validation_plan,
        'rollback_plan': ns.rollback_plan,
        'approval_required': risk == 'high' or 'human_review' in d,
        'context_used': split_csv(ns.context_used),
        'decision_artifacts_checked': split_csv(ns.decisions_checked),
    }
    md = outdir/f'{stamp}-dry-run.md'
    md.write_text('# Dry Run Report\n\n```json\n'+json.dumps(report, indent=2)+'\n```\n', encoding='utf-8')
    if not ns.no_validate:
        validator = Path(__file__).with_name('validate_dry_run.py')
        if validator.exists():
            res=subprocess.run([sys.executable, str(validator), str(md)], text=True, capture_output=True)
            if res.returncode != 0:
                print(res.stderr, file=sys.stderr)
                return res.returncode
    print(md)
    return 0
if __name__ == '__main__': raise SystemExit(main())
