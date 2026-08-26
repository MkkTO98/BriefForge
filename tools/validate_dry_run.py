#!/usr/bin/env python3
"""Validate project-local dry-run reports.

This is intentionally lightweight. It ensures dry-run reports contain the
fields agents need before execution proceeds.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

REQUIRED = [
    'timestamp','proposal','risk','mode','dry_run_depth','files','commands',
    'validation_plan','rollback_plan','approval_required','context_used',
    'decision_artifacts_checked'
]
ALLOWED_RISK={'low','medium','high'}


def extract_json(text: str) -> dict:
    m = re.search(r"```json\s*(.*?)\s*```", text, re.S)
    raw = m.group(1) if m else text
    return json.loads(raw)


def validate(path: Path) -> list[str]:
    try:
        data = extract_json(path.read_text(encoding='utf-8'))
    except Exception as e:
        return [f'cannot parse dry-run report as JSON: {e}']
    errors=[]
    for k in REQUIRED:
        if k not in data:
            errors.append(f'missing required field: {k}')
    if data.get('risk') not in ALLOWED_RISK:
        errors.append(f"invalid risk: {data.get('risk')}")
    if not str(data.get('proposal','')).strip():
        errors.append('proposal is empty')
    if data.get('risk') in {'medium','high'} and not data.get('validation_plan'):
        errors.append('medium/high risk requires validation_plan')
    if data.get('risk') == 'high' and not data.get('approval_required'):
        errors.append('high risk must require approval')
    return errors


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('report')
    ns=ap.parse_args(); path=Path(ns.report)
    errs=validate(path)
    if errs:
        for e in errs: print(f'BLOCK: {e}', file=sys.stderr)
        return 2
    print(f'valid: {path}')
    return 0
if __name__ == '__main__': raise SystemExit(main())
