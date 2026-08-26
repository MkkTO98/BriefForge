#!/usr/bin/env python3
"""Generate the bounded T-035 Norway interactive report."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from briefforge.norway_interactive_report import render_t035_file  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()
    report = render_t035_file(args.input, args.output_directory)
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
