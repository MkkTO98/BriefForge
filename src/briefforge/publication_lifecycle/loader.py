"""Bounded local JSON loading for the separately negotiated lifecycle profile."""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Any

from briefforge.bcrp.loader import loads_json_bytes

from .model import BUNDLE_FORMAT, PROFILE_ID, PROFILE_VERSION, LifecycleBundle, event_from_document

MAX_EVENTS = 256


class LifecycleLoadError(ValueError):
    pass


def _safe_path(root: Path, location: Any) -> Path:
    if not isinstance(location, str) or not location:
        raise LifecycleLoadError("event location must be a non-empty relative path")
    posix = PurePosixPath(location)
    if posix.is_absolute() or ".." in posix.parts or "." in posix.parts or "\\" in location:
        raise LifecycleLoadError("event location must remain inside the lifecycle bundle")
    resolved_root = root.resolve()
    path = (resolved_root / Path(*posix.parts)).resolve()
    if not path.is_relative_to(resolved_root):
        raise LifecycleLoadError("event location escapes the lifecycle bundle")
    return path


def load_bundle(root: str | Path) -> LifecycleBundle:
    bundle_root = Path(root)
    try:
        index = loads_json_bytes((bundle_root / "bundle.json").read_bytes(), source="lifecycle bundle index")
    except (OSError, ValueError) as exc:
        raise LifecycleLoadError(f"cannot load lifecycle bundle index: {exc}") from exc
    if not isinstance(index, dict) or index.get("format") != BUNDLE_FORMAT:
        raise LifecycleLoadError("unsupported lifecycle bundle format")
    profile = index.get("profile")
    if not isinstance(profile, dict) or profile.get("identity") != PROFILE_ID or profile.get("version") != PROFILE_VERSION:
        raise LifecycleLoadError("unsupported lifecycle profile identity or version")
    entries = index.get("events")
    if not isinstance(entries, list) or len(entries) > MAX_EVENTS:
        raise LifecycleLoadError("lifecycle bundle events inventory is invalid or excessive")
    locations: set[str] = set()
    identities: set[str] = set()
    events = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise LifecycleLoadError("lifecycle event inventory entries must be objects")
        location = entry.get("location")
        declared_identity = entry.get("identity")
        if location in locations or declared_identity in identities:
            raise LifecycleLoadError("duplicate lifecycle event identity or location")
        locations.add(location)
        identities.add(declared_identity)
        path = _safe_path(bundle_root, location)
        try:
            document = loads_json_bytes(path.read_bytes(), source=f"lifecycle event {location}")
            event = event_from_document(document)
        except (OSError, ValueError) as exc:
            raise LifecycleLoadError(f"cannot load lifecycle event {location!r}: {exc}") from exc
        if event.identity != declared_identity:
            raise LifecycleLoadError("lifecycle event inventory identity mismatch")
        events.append(event)
    events.sort(key=lambda item: item.identity)
    return LifecycleBundle(PROFILE_ID, PROFILE_VERSION, tuple(events))
