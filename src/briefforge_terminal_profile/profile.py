"""Closed terminal authority profile.

This module is deliberately a sibling of :mod:`briefforge`; the historical
The historical representative implementation closure is not changed.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from briefforge.bounded_loopback_deployment import (
    DeploymentRouteItem,
    DeploymentTarget,
    _released_loopback_deployment_scope,
)
from briefforge.publication_distribution_delivery import _released_destination_scope
from briefforge.technical_publication_verification import _released_technical_verification_scope

PROFILE_IDENTITY = "briefforge:representative-terminal-static-html-profile:2.0.0"
PROFILE_VERSION = "2.0.0"
PROFILE_IMPLEMENTATION_IDENTITY = "briefforge_terminal_profile.profile"
PROFILE_IMPLEMENTATION_VERSION = "1.0.0"
PROJECT_OWNER = "project:BriefForge"

TERMINAL_OPERATIONAL_IDENTITIES = (
    "authority:briefforge-bcrp-validation",
    "authority:briefforge-publication-release",
    "authority:briefforge-controlled-renderer-invocation",
    "authority:briefforge-semantic-artifact-conformance",
    "authority:briefforge-publication-manifest-projector",
    "authority:briefforge-controlled-local-delivery",
    "authority:briefforge-bounded-loopback-deployment",
    "authority:briefforge-technical-publication-verifier",
)
TERMINAL_OPERATIONAL_ROLES = (
    "validation-authority",
    "publication-release-authority",
    "renderer-invocation-authority",
    "semantic-artifact-conformance-assessor",
    "publication-manifest-projector",
    "controlled-local-delivery-authority",
    "bounded-loopback-deployment-authority",
    "technical-publication-verification-authority",
)
_STATIC_SCOPES = (
    "BCRP-L0-L6",
    "fixed-evidence-publication-release",
    "one-controlled-renderer-invocation-act",
    "one-semantic-artifact-conformance-assessment",
    "one-publication-manifest-production",
)
_DYNAMIC_SCOPE_PROFILES = (
    "briefforge-controlled-local-directory-delivery-profile:1.0.0",
    "briefforge-bounded-loopback-static-http-profile:1.0.0",
    "briefforge-raw-http-technical-publication-profile:1.0.0",
)
# The content role is an explicit profile role rather than a residual
# "anything not operational" classification.
CONTENT_AUTHORITY_ROLE_ALLOWLIST = frozenset({"presentation-content-authority"})
_RESERVED_OPERATIONAL_IDENTITIES = frozenset(TERMINAL_OPERATIONAL_IDENTITIES)
_RESERVED_OPERATIONAL_ROLES = frozenset(TERMINAL_OPERATIONAL_ROLES)
_AUTHORITY_KEYS = frozenset({"id", "owner_identity", "role", "scope"})


class TerminalAuthorityProfileRejected(ValueError):
    """The exact closed authority profile was not supplied."""


@dataclass(frozen=True)
class TerminalAuthorityProfile:
    profile_identity: str
    profile_version: str
    operational_authorities: tuple[Mapping[str, str], ...]
    content_authorities: tuple[Mapping[str, str], ...] = ()

    @property
    def authorities(self) -> tuple[Mapping[str, str], ...]:
        return self.operational_authorities + self.content_authorities


def profile_implementation_digest() -> str:
    """Digest the exact active implementation bytes, never an archived tree."""
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _frozen_authority(identity: str, role: str, scope: str) -> Mapping[str, str]:
    return MappingProxyType({
        "id": identity,
        "owner_identity": PROJECT_OWNER,
        "role": role,
        "scope": scope,
    })


def build_terminal_authority_profile(
    *,
    destination_parent: Path,
    destination_basename: str,
    delivery_ledger: Path,
    target: DeploymentTarget,
    routes: tuple[DeploymentRouteItem, ...],
    deployment_ledger: Path,
    verification_ledger: Path,
    content_authorities: tuple[Mapping[str, str], ...] = (),
) -> TerminalAuthorityProfile:
    """Build the sole terminal profile, delegating all terminal scopes.

    In particular this public constructor does not reproduce or approximate
    delivery/deployment path, inode, route, or target canonicalization.
    """
    scopes = _STATIC_SCOPES + (
        _released_destination_scope(Path(destination_parent), destination_basename, Path(delivery_ledger)),
        _released_loopback_deployment_scope(target, routes, Path(deployment_ledger)),
        _released_technical_verification_scope(target, routes, Path(verification_ledger)),
    )
    operational = tuple(
        _frozen_authority(identity, role, scope)
        for identity, role, scope in zip(
            TERMINAL_OPERATIONAL_IDENTITIES, TERMINAL_OPERATIONAL_ROLES, scopes, strict=True
        )
    )
    if type(content_authorities) is not tuple or not 1 <= len(content_authorities) <= 8:
        raise TerminalAuthorityProfileRejected("one to eight content authorities required")
    frozen_content = tuple(MappingProxyType(dict(item)) for item in content_authorities)
    profile = TerminalAuthorityProfile(
        PROFILE_IDENTITY, PROFILE_VERSION, operational, frozen_content
    )
    verify_terminal_authority_profile(profile)
    return profile


def verify_terminal_authority_profile(profile: TerminalAuthorityProfile) -> None:
    if type(profile) is not TerminalAuthorityProfile:
        raise TerminalAuthorityProfileRejected("exact terminal authority profile required")
    if (profile.profile_identity, profile.profile_version) != (PROFILE_IDENTITY, PROFILE_VERSION):
        raise TerminalAuthorityProfileRejected("unknown terminal profile identity or version")
    if type(profile.operational_authorities) is not tuple or len(profile.operational_authorities) != 8:
        raise TerminalAuthorityProfileRejected("exactly eight operational authorities required")
    if type(profile.content_authorities) is not tuple or not 1 <= len(profile.content_authorities) <= 8:
        raise TerminalAuthorityProfileRejected("content authority cardinality is outside the closed bound")

    all_items = profile.authorities
    ids: list[str] = []
    roles: list[str] = []
    for index, item in enumerate(all_items):
        if not isinstance(item, Mapping) or set(item) != _AUTHORITY_KEYS:
            raise TerminalAuthorityProfileRejected("authority has an unexpected exact schema")
        if any(type(item[key]) is not str or not item[key] for key in _AUTHORITY_KEYS):
            raise TerminalAuthorityProfileRejected("authority fields require nonempty exact text")
        ids.append(item["id"])
        roles.append(item["role"])
        if index < 8:
            if item["id"] != TERMINAL_OPERATIONAL_IDENTITIES[index]:
                raise TerminalAuthorityProfileRejected("operational identity or order mismatch")
            if item["role"] != TERMINAL_OPERATIONAL_ROLES[index]:
                raise TerminalAuthorityProfileRejected("operational role or cross-role binding mismatch")
            if item["owner_identity"] != PROJECT_OWNER:
                raise TerminalAuthorityProfileRejected("operational owner mismatch")
            if index < 5 and item["scope"] != _STATIC_SCOPES[index]:
                raise TerminalAuthorityProfileRejected("operational scope mismatch")
            if index >= 5:
                try:
                    scope = json.loads(item["scope"])
                    canonical = json.dumps(
                        scope, ensure_ascii=False, sort_keys=True,
                        separators=(",", ":"), allow_nan=False,
                    )
                    if (type(scope) is not dict or canonical != item["scope"] or
                            scope.get("profile") != _DYNAMIC_SCOPE_PROFILES[index - 5]):
                        raise ValueError("wrong canonical terminal scope")
                    _verify_dynamic_scope(index, scope)
                except Exception as exc:
                    raise TerminalAuthorityProfileRejected("operational scope mismatch") from exc
        else:
            if item["id"] in _RESERVED_OPERATIONAL_IDENTITIES:
                raise TerminalAuthorityProfileRejected("reserved operational identity used as content")
            if item["role"] in _RESERVED_OPERATIONAL_ROLES:
                raise TerminalAuthorityProfileRejected("reserved operational role used as content")
            if item["role"] not in CONTENT_AUTHORITY_ROLE_ALLOWLIST:
                raise TerminalAuthorityProfileRejected("content role is not explicitly allowed")
    if len(ids) != len(set(ids)) or len(roles[:8]) != len(set(roles[:8])):
        raise TerminalAuthorityProfileRejected("duplicate authority identity or operational role")
    content_ids = ids[8:]
    if content_ids != sorted(content_ids):
        raise TerminalAuthorityProfileRejected("content authorities must be canonical by id")


def _exact_dict(value: object, keys: set[str]) -> dict:
    if type(value) is not dict or set(value) != keys:
        raise ValueError("dynamic scope schema differs")
    return value


def _text(value: object) -> bool:
    return type(value) is str and bool(value) and "\x00" not in value


def _boundary(value: object) -> None:
    boundary = _exact_dict(value, {"canonical_path", "device", "inode"})
    path = boundary["canonical_path"]
    if (not _text(path) or not Path(path).is_absolute() or str(Path(path).resolve()) != path
            or type(boundary["device"]) is not int or boundary["device"] < 0
            or type(boundary["inode"]) is not int or boundary["inode"] <= 0):
        raise ValueError("dynamic scope boundary differs")


def _target(value: object) -> None:
    target = _exact_dict(value, {"address", "port", "origin"})
    if (target["address"] != "127.0.0.1" or type(target["port"]) is not int
            or not 1024 <= target["port"] <= 65535
            or target["origin"] != f"http://127.0.0.1:{target['port']}"):
        raise ValueError("dynamic scope target differs")


def _routes(value: object) -> None:
    if type(value) is not list or not value:
        raise ValueError("dynamic scope routes differ")
    paths: list[str] = []
    basenames: list[str] = []
    for raw in value:
        route = _exact_dict(raw, {"path", "logical_filename", "media_type"})
        path, basename, media = route["path"], route["logical_filename"], route["media_type"]
        if (not _text(path) or not path.startswith("/") or path == "/" or "?" in path or "#" in path
                or "//" in path or "/../" in path or path.endswith("/..")
                or not _text(basename) or Path(basename).name != basename or basename in {".", ".."}
                or not _text(media) or "/" not in media):
            raise ValueError("dynamic scope route differs")
        paths.append(path); basenames.append(basename)
    if paths != sorted(paths) or len(paths) != len(set(paths)) or len(basenames) != len(set(basenames)):
        raise ValueError("dynamic scope route order or uniqueness differs")


def _verify_dynamic_scope(index: int, scope: dict) -> None:
    """Verify all release-independent bytes in each terminal scope."""
    common = {"policy", "profile", "implementation", "version", "contract", "ledger"}
    constants = (
        ("briefforge-controlled-local-delivery-policy:1.0.0", _DYNAMIC_SCOPE_PROFILES[0],
         "briefforge.publication_distribution_delivery", "1.0.0"),
        ("briefforge-bounded-loopback-deployment-policy:1.0.0", _DYNAMIC_SCOPE_PROFILES[1],
         "briefforge.bounded_loopback_deployment", "1.0.0"),
        ("briefforge-technical-publication-verification-policy:1.0.0", _DYNAMIC_SCOPE_PROFILES[2],
         "briefforge.technical_publication_verification", "1.0.0"),
    )[index - 5]
    if index == 5:
        _exact_dict(scope, common | {"destination_parent", "final_basename"})
        if scope["contract"] != {"atomic":"renameat2-noreplace", "collision":"nfc-casefold-no-alias",
                                  "no_overwrite":True, "rollback":"verified-or-indeterminate"}:
            raise ValueError("delivery contract differs")
        _boundary(scope["destination_parent"]); _boundary(scope["ledger"])
        basename = scope["final_basename"]
        if not _text(basename) or Path(basename).name != basename or basename in {".", ".."}:
            raise ValueError("delivery basename differs")
    elif index == 6:
        _exact_dict(scope, common | {"transport", "routes"})
        if scope["contract"] != {"one_act":True, "bounded":True, "no_runtime_fallback":True,
                                  "public_binding":False}:
            raise ValueError("deployment contract differs")
        transport = _exact_dict(scope["transport"], {"family","type","scheme","address","port","origin"})
        if (transport["family"], transport["type"], transport["scheme"]) != ("AF_INET","SOCK_STREAM","http"):
            raise ValueError("deployment transport differs")
        _target({k: transport[k] for k in ("address","port","origin")})
        _routes(scope["routes"]); _boundary(scope["ledger"])
    else:
        _exact_dict(scope, common | {"target", "routes"})
        if scope["contract"] != {"one_act":True, "actual_raw_transport":True, "historical_only":True}:
            raise ValueError("verification contract differs")
        _target(scope["target"]); _routes(scope["routes"]); _boundary(scope["ledger"])
    if tuple(scope[k] for k in ("policy","profile","implementation","version")) != constants:
        raise ValueError("dynamic scope static identity differs")


def verify_material_authority_profile(
    authorities: object, expected_profile: TerminalAuthorityProfile
) -> None:
    """Admit an exact 8 + 1..8 release-resident authority inventory."""
    verify_terminal_authority_profile(expected_profile)
    if type(authorities) is not list or not 9 <= len(authorities) <= 16:
        raise TerminalAuthorityProfileRejected("release requires exactly eight operational and one to eight content authorities")
    normalized = tuple(dict(item) if isinstance(item, Mapping) else item for item in expected_profile.authorities)
    if tuple(authorities) != normalized:
        raise TerminalAuthorityProfileRejected("release authority inventory differs from the selected closed profile")
