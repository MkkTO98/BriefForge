#!/usr/bin/env python3
"""Create simple rollup reports from JSONL metric events."""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--project', default='.')
    ns=ap.parse_args(); root=Path(ns.project).resolve(); f=root/'metrics'/'events.jsonl'
    counts=collections.Counter(); failures=collections.Counter()
    if f.exists():
        for line in f.read_text(encoding='utf-8').splitlines():
            if not line.strip(): continue
            rec=json.loads(line); key=(rec.get('entity_type'),rec.get('entity'),rec.get('event')); counts[key]+=1
            if rec.get('status') in {'failed','failure','blocked'}: failures[key]+=1
    out=root/'metrics'/'reports'/'metrics_rollup.md'; out.parent.mkdir(parents=True, exist_ok=True)
    lines=['# Metrics Rollup\n']
    lines.append('## Event Counts\n')
    for (typ, ent, ev), n in counts.most_common(): lines.append(f'- `{typ}:{ent}:{ev}` = {n}')
    lines.append('\n## Failures / Blocks\n')
    for (typ, ent, ev), n in failures.most_common(): lines.append(f'- `{typ}:{ent}:{ev}` = {n}')
    out.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(out)
    return 0
if __name__ == '__main__': raise SystemExit(main())
