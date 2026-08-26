"""Renderer-independent in-memory representation for BCRP 1.0."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROFILE_ID = "briefforge-core-representation-profile"
PROFILE_VERSION = "1.0.0"
BUNDLE_FORMAT = "briefforge-bcrp-json-bundle-v1"
CANONICALIZATION_ID = "bcrp-semantic-canonicalization:1.0.0"

RECORD_KINDS = (
    "PresentationBriefRecord",
    "PortablePresentationMaterialRecord",
    "CandidatePresentationPackageRecord",
    "ValidationJudgmentRecord",
    "ReadyPresentationPackageRecord",
    "PublicationReleaseRecord",
    "RendererCapabilityDeclarationRecord",
    "RendererCompatibilityPlanRecord",
    "GeneratedArtifactAuditRecord",
    "SemanticArtifactConformanceRecord",
    "PublicationManifestRecord",
)


@dataclass
class BCRPRecord:
    """One independently addressable BCRP record."""

    kind: str
    identity: str
    profile_version: str
    semantic: dict[str, Any]
    extensions: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "BCRPRecord":
        profile = document.get("profile", {})
        return cls(
            kind=document.get("record_kind", ""),
            identity=document.get("identity", ""),
            profile_version=profile.get("version", ""),
            semantic=document.get("semantic", {}),
            extensions=document.get("extensions", []),
            metadata=document.get("metadata", {}),
        )

    def to_document(self) -> dict[str, Any]:
        document: dict[str, Any] = {
            "record_kind": self.kind,
            "identity": self.identity,
            "profile": {"identity": PROFILE_ID, "version": self.profile_version},
            "semantic": self.semantic,
            "extensions": self.extensions,
        }
        if self.metadata:
            document["metadata"] = self.metadata
        return document


@dataclass
class BCRPBundle:
    """One bounded BCRP profile instance reconstructed from a transport bundle."""

    profile_identity: str
    profile_version: str
    records: tuple[BCRPRecord, ...]
    index: dict[str, Any] = field(default_factory=dict)
    source_root: Path | None = None
    derived_reverse_index: dict[str, list[str]] = field(default_factory=dict)

    def records_of_kind(self, kind: str) -> tuple[BCRPRecord, ...]:
        return tuple(record for record in self.records if record.kind == kind)

    def one(self, kind: str) -> BCRPRecord:
        records = self.records_of_kind(kind)
        if len(records) != 1:
            raise ValueError(f"expected exactly one {kind}, found {len(records)}")
        return records[0]

    def by_identity(self) -> dict[str, BCRPRecord]:
        return {record.identity: record for record in self.records}


@dataclass(frozen=True, order=True)
class ValidationFinding:
    """A deterministic, layer-owned BCRP validation finding."""

    layer: str
    family: str
    severity: str
    blocking_consequence: str
    semantic_identity: str
    location: str
    message: str
    referenced_identities: tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidationResult:
    """Layer-preserving validation result; never an opaque Boolean."""

    findings: tuple[ValidationFinding, ...]
    executed_layers: tuple[str, ...]

    @property
    def blocking(self) -> bool:
        return any(finding.severity == "blocking" for finding in self.findings)


@dataclass(frozen=True)
class Fingerprint:
    """A digest whose equality authority is limited to its named domain."""

    domain: str
    root_identity: str
    profile_identity: str
    profile_version: str
    canonicalization: str
    algorithm: str
    digest: str
    scope: str


@dataclass(frozen=True)
class SemanticGraph:
    """Canonical forward edges plus a disposable derived reverse index."""

    identities: tuple[str, ...]
    edges: tuple[tuple[str, str, str], ...]
    reverse_index: dict[str, list[str]]
