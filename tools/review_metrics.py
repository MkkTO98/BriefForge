#!/usr/bin/env python3
"""Review metrics and propose operational improvements without auto-applying them."""
from __future__ import annotations
import argparse, collections, datetime as dt, json
from pathlib import Path

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--project', default='.'); ap.add_argument('--failure-threshold', type=int, default=3)
    ns=ap.parse_args(); root=Path(ns.project).resolve(); events=root/'metrics'/'events.jsonl'
    failures=collections.Counter(); totals=collections.Counter()
    if events.exists():
        for line in events.read_text(encoding='utf-8').splitlines():
            if not line.strip(): continue
            try: rec=json.loads(line)
            except Exception: continue
            key=f"{rec.get('entity_type','unknown')}:{rec.get('entity','unknown')}:{rec.get('event','unknown')}"
            totals[key]+=1
            if rec.get('status') in {'failed','failure','blocked'}: failures[key]+=1
    lines=['# Metrics Review', f'Date: {dt.date.today().isoformat()}', '']
    lines.append('## Findings')
    if not totals: lines.append('- No metrics recorded yet.')
    for k,n in failures.most_common():
        lines.append(f'- `{k}` has {n} failure/block event(s).')
    lines.append('\n## Recommendations')
    any_rec=False
    for k,n in failures.most_common():
        if n >= ns.failure_threshold:
            any_rec=True
            lines.append(f'- Consider a specialized agent/skill or routing change for `{k}`. Request user approval before generating anything.')
    if not any_rec: lines.append('- No specialized-agent or routing change recommended yet.')
    lines.append('\n## Policy')
    lines.append('- This report may propose local scaffold improvements but must not apply them automatically.')
    out=root/'metrics'/'reports'/f"metrics_review_{dt.date.today().strftime('%Y%m%d')}.md"; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(out)
    return 0
if __name__=='__main__': raise SystemExit(main())
