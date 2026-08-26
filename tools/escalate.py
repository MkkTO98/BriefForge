#!/usr/bin/env python3
"""Create escalation records for capability, permission, or specification failures."""
from __future__ import annotations
import argparse, datetime as dt, json
from pathlib import Path

CHAINS = {
  'capability': ['local_worker','local_reviewer','stronger_local_model','codex_or_premium_model','human_if_still_blocked'],
  'permission': ['question_queue','human_approval'],
  'specification': ['decision_lookup','question_queue','human_answer','decision_artifact'],
  'safety': ['stop','human_review'],
}

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--project', default='.')
    ap.add_argument('--kind', choices=sorted(CHAINS), required=True)
    ap.add_argument('--reason', required=True)
    ap.add_argument('--task', default='unspecified')
    ap.add_argument('--confidence', default='unknown')
    ns=ap.parse_args(); root=Path(ns.project).resolve()
    stamp=dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    rec={'timestamp':stamp,'kind':ns.kind,'task':ns.task,'reason':ns.reason,'confidence':ns.confidence,'chain':CHAINS[ns.kind]}
    out=root/'recovery'/'escalations'; out.mkdir(parents=True, exist_ok=True)
    p=out/f'{stamp}-{ns.kind}.json'; p.write_text(json.dumps(rec, indent=2), encoding='utf-8')
    if ns.kind in {'permission','specification','safety'}:
        qdir=root/'question_queue'/'pending'; qdir.mkdir(parents=True, exist_ok=True)
        q=(qdir/f'{stamp}-{ns.kind}.md')
        q.write_text(f"# Escalation Question\n\nKind: {ns.kind}\nTask: {ns.task}\nConfidence: {ns.confidence}\n\n## Reason\n{ns.reason}\n\n## Required response\nProvide approval, denial, or specification. Store the final answer as a decision artifact if it changes project policy.\n", encoding='utf-8')
    print(p)
    return 0
if __name__ == '__main__': raise SystemExit(main())
