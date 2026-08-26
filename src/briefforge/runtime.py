"""Minimal runtime representation for Candidate Presentation Packages.

This module intentionally represents only the frozen constitutional concepts
needed for a Candidate Presentation Package. It does not validate, render,
serialize, persist, export, network, template, visualize, or serve packages.
"""

from dataclasses import asdict, dataclass
import hashlib
import json


@dataclass(frozen=True)
class PackageIdentity:
    """Bounded self-identification of a presentation package."""

    package_id: str
    title: str
    purpose_summary: str
    scope: str
    non_scope: str


@dataclass(frozen=True)
class OrganizingPurpose:
    """Target-independent reason binding statements into one package."""

    statement: str
    scope: str
    non_scope: str


@dataclass(frozen=True)
class EncounterSemantics:
    """Target-independent encounter relationship for a presentation statement."""

    mode: str
    description: str
    related_statement_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class UpstreamReference:
    """Reference to upstream-owned material without taking ownership of meaning."""

    reference_id: str
    owning_project: str
    reference_kind: str
    locator: str
    owned_meaning: str


@dataclass(frozen=True)
class PresentationObligation:
    """Presentation-local obligation that must remain attached to meaning."""

    obligation_id: str
    category: str
    requirement: str
    applies_to: tuple[str, ...] = ()


@dataclass(frozen=True)
class PresentationStatement:
    """Smallest BriefForge-owned unit of presentation meaning."""

    statement_id: str
    encounter_meaning: str
    belongs_to_purpose: str
    encounter_semantics: EncounterSemantics
    upstream_reference_ids: tuple[str, ...] = ()
    obligation_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class CandidatePresentationPackage:
    """Package-shaped semantic object before validation or downstream use."""

    identity: PackageIdentity
    organizing_purpose: OrganizingPurpose
    statements: tuple[PresentationStatement, ...]
    upstream_references: tuple[UpstreamReference, ...] = ()
    obligations: tuple[PresentationObligation, ...] = ()


def semantic_fingerprint(package: CandidatePresentationPackage) -> str:
    """Return a deterministic fingerprint of candidate semantic substance only.

    The input surface is the Candidate Presentation Package runtime record:
    identity, organizing purpose, statements, upstream references, and
    obligations. It intentionally has no rendering, browser, HTML, template,
    serialization, persistence, API, file, or UI inputs.
    """

    canonical_substance = json.dumps(asdict(package), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_substance.encode("utf-8")).hexdigest()
