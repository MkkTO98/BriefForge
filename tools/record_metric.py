#!/usr/bin/env python3
"""Append a JSONL metric event."""
from __future__ import annotations
import argparse, datetime as dt, json
from pathlib import Path

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--project', default='.')
    ap.add_argument('--entity-type', required=True, choices=['agent','model','tool','skill','task','template','permission','project'])
    ap.add_argument('--entity', required=True)
    ap.add_argument('--event', required=True)
    ap.add_argument('--status', default='observed')
    ap.add_argument('--details', default='')
    ns=ap.parse_args()
    out=Path(ns.project).resolve()/'metrics'/'events.jsonl'; out.parent.mkdir(parents=True, exist_ok=True)
    rec={'timestamp':dt.datetime.now().isoformat(timespec='seconds'), 'entity_type':ns.entity_type, 'entity':ns.entity, 'event':ns.event, 'status':ns.status, 'details':ns.details}
    with out.open('a', encoding='utf-8') as f: f.write(json.dumps(rec, ensure_ascii=False)+'\n')
    print(out)
    return 0
if __name__ == '__main__': raise SystemExit(main())
