"""Fixed TASK-052 renderer worker launched with an explicit isolated environment."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

# Isolated mode intentionally omits the source root; this fixed worker restores
# only its own package root before importing the measured implementation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from briefforge.controlled_renderer_invocation import (  # noqa: E402
    _projection_from_document,
    renderer_implementation_digest,
)
from briefforge.renderer_adapter import render_minimal_html_projection  # noqa: E402


def main() -> int:
    request = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    if type(request) is not dict or set(request) != {"projection", "renderer_implementation_digest"}:
        raise ValueError("Renderer worker request envelope is malformed.")
    expected = request["renderer_implementation_digest"]
    observed = renderer_implementation_digest()
    if type(expected) is not str or observed != expected:
        raise ValueError(
            f"Renderer implementation changed before isolated execution: expected {expected!r}, observed {observed!r}."
        )
    projection = _projection_from_document(request["projection"])
    artifact = render_minimal_html_projection(projection)
    if type(artifact.html) is not str:
        raise ValueError("Fixed renderer did not return text HTML.")
    if tuple(Path.cwd().iterdir()):
        raise ValueError("Fixed renderer produced undeclared auxiliary files.")
    effective = {
        "dont_write_bytecode": bool(sys.flags.dont_write_bytecode),
        "environment": {name: os.environ[name] for name in sorted(os.environ)},
        "hash_randomization": bool(sys.flags.hash_randomization),
        "ignore_environment": bool(sys.flags.ignore_environment),
        "interpreter_flags": sys.orig_argv[1:-1],
        "utf8_mode": sys.flags.utf8_mode,
    }
    sys.stderr.buffer.write(
        json.dumps(effective, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    sys.stdout.buffer.write(artifact.html.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
