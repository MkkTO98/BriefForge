#!/usr/bin/env python3
"""Generate the two bounded reusable-foundation report outputs."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from briefforge.interactive_report_configs import macro_config, norway_config
from briefforge.interactive_report_foundation import write_report

DEFAULT_INPUT = Path("/home/mkkto/srv/EIP/projects/InsightForge/artifacts/fixtures/T-035-demographic-growth-correlation-report-input.json")
DEFAULT_OUTPUT = Path("/home/mkkto/.local/state/eip-results/briefforge/reusable-interactive-foundation-v1-20260824")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    paths = [write_report(macro_config(), args.output / "macro-model/index.html"), write_report(norway_config(data, args.input), args.output / "norway/index.html")]
    for path in paths:
        print(path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
