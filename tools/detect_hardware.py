#!/usr/bin/env python3
from __future__ import annotations
import os, platform, subprocess
from pathlib import Path

def main() -> int:
    ram_gb = 'unknown'
    try:
        pages = os.sysconf('SC_PHYS_PAGES'); page_size = os.sysconf('SC_PAGE_SIZE')
        ram_gb = round(pages * page_size / (1024**3), 2)
    except Exception: pass
    gpu = 'unknown'
    try:
        r = subprocess.run(['bash','-lc','command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -1 || true'], capture_output=True, text=True)
        gpu = r.stdout.strip() or 'unknown_or_no_nvidia_gpu'
    except Exception: pass
    print(f"cpu: {platform.processor() or platform.machine()}")
    print(f"ram_gb: {ram_gb}")
    print(f"gpu: {gpu}")
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
