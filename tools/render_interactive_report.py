#!/usr/bin/env python3
"""Render a self-contained interactive browser report from explicit JSON config."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from briefforge.interactive_report_foundation import write_report


def load_config(path: Path, parser: argparse.ArgumentParser) -> dict[str, Any]:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        parser.error(f"unable to read configuration {path}: {exc}")
    try:
        config = json.loads(source)
    except json.JSONDecodeError as exc:
        parser.error(f"invalid JSON configuration {path}: {exc.msg} at line {exc.lineno} column {exc.colno}")
    if not isinstance(config, dict):
        parser.error(f"configuration must be a JSON object: {path}")
    return config


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Supported route for structured interactive browser reports. "
            "Minimal/static Ready-Package rendering remains a separate legacy route."
        )
    )
    parser.add_argument("--config", required=True, type=Path, help="explicit interactive-report JSON configuration")
    parser.add_argument("--output", required=True, type=Path, help="explicit destination HTML path")
    args = parser.parse_args()
    config = load_config(args.config, parser)
    try:
        destination = write_report(config, args.output)
    except (KeyError, TypeError, ValueError) as exc:
        parser.error(f"invalid interactive-report configuration {args.config}: {exc}")
    except OSError as exc:
        parser.error(f"unable to write output {args.output}: {exc}")
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
