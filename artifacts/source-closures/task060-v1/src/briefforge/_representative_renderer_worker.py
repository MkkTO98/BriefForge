"""Isolated stdin/stdout worker for the fixed representative renderer."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

# The fixed flags omit ambient source paths. Restore only this measured package root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from briefforge.representative_controlled_invocation import (  # noqa: E402
    _projection_from_document,
    representative_renderer_implementation_digest,
)
from briefforge.representative_renderer import render_representative_html  # noqa: E402


def main() -> int:
    try:
        document = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        if type(document) is not dict or set(document) != {"projection", "renderer_digest"}:
            raise ValueError("worker request schema is invalid")
        if type(document["renderer_digest"]) is not str or document["renderer_digest"] != representative_renderer_implementation_digest():
            raise ValueError("renderer implementation digest mismatch")
        artifact = render_representative_html(_projection_from_document(document["projection"]))
        if tuple(Path.cwd().iterdir()):
            raise ValueError("renderer produced undeclared auxiliary files")
        effective = {
            "dont_write_bytecode": bool(sys.flags.dont_write_bytecode),
            "environment": {name: os.environ[name] for name in sorted(os.environ)},
            "hash_randomization": bool(sys.flags.hash_randomization),
            "ignore_environment": bool(sys.flags.ignore_environment),
            "interpreter_flags": sys.orig_argv[1:-1],
            "utf8_mode": sys.flags.utf8_mode,
        }
        sys.stderr.buffer.write(json.dumps(effective, ensure_ascii=True, sort_keys=True,
                                           separators=(",", ":")).encode("utf-8"))
        sys.stdout.buffer.write(artifact)
        return 0
    except Exception as exc:
        sys.stderr.write(str(exc)[:1000])
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
