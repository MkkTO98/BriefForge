#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, json, uuid
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--project", default=".")
    p.add_argument("--severity", required=True, choices=["L1","L2","L3","L4"])
    p.add_argument("--question", required=True)
    p.add_argument("--options", default="")
    p.add_argument("--recommended-default", default="")
    p.add_argument("--consequence", default="")
    ns = p.parse_args()
    project = Path(ns.project).resolve()
    qid = str(uuid.uuid4())
    rec = {
        "id": qid,
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "severity": ns.severity,
        "question": ns.question,
        "options": [x.strip() for x in ns.options.split("|") if x.strip()],
        "recommended_default": ns.recommended_default,
        "consequence_if_unanswered": ns.consequence,
        "status": "pending",
    }
    out = project/"question_queue"/"pending"/f"{qid}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
    print(out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
