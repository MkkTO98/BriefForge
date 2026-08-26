"""Truthful fixed adapter from the terminal-profile DTO to the renderer DTO."""
from __future__ import annotations

from dataclasses import fields
import hashlib
from pathlib import Path

from briefforge import representative_projection as legacy

ADAPTER_IDENTITY = "adapter:briefforge-terminal-to-representative-static-html"
ADAPTER_VERSION = "1.0.0"
ADAPTER_IMPLEMENTATION_IDENTITY = "briefforge_terminal_profile.renderer_adapter"


class TerminalRendererAdapterRejected(ValueError):
    pass


def adapter_source_digest() -> str:
    """Return the SHA-256 of the exact active adapter source bytes."""
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def adapt_terminal_projection(projection):
    """Translate only fixed routing metadata; preserve every semantic field.

    The result is the exact historical DTO type required by the real renderer.
    Its planned-zero inventory deliberately remains eight objects: the renderer
    never realizes that inventory, and no exclusion is hidden by translation.
    """
    from .projection import (
        TerminalRepresentativeProjection,
        verify_terminal_projection,
    )
    if type(projection) is not TerminalRepresentativeProjection:
        raise TerminalRendererAdapterRejected("exact terminal successor DTO required")
    verify_terminal_projection(projection)
    values={f.name:getattr(projection,f.name) for f in fields(legacy.RepresentativeProjection)}
    values.update(
        profile_identity=legacy.PROJECTION_PROFILE_ID,
        profile_version=legacy.PROJECTION_PROFILE_VERSION,
        renderer_adapter_id=legacy.RENDERER_ADAPTER_ID,
        fingerprint="",
    )
    provisional=legacy.RepresentativeProjection(**values)
    result=legacy.RepresentativeProjection(
        **(values | {"fingerprint":legacy.compute_representative_projection_fingerprint(provisional)})
    )
    legacy.verify_representative_projection(result)
    if result.operational_authority_exclusions != projection.operational_authority_exclusions:
        raise TerminalRendererAdapterRejected("adapter lost an operational exclusion")
    return result
