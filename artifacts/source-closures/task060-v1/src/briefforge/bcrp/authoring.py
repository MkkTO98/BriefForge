"""Renderer-independent BCRP Candidate authoring and technical validation.

This module creates only Presentation Brief, Portable Presentation Material,
and Candidate records. It does not render, serialize, publish, emit manifests,
adapt the historical runtime, follow external references, or acquire semantic
authority from upstream systems.

L0-L2 execution returns technical evidence only. Under the current accepted
lifecycle authority, technical success cannot manufacture governance Judgment or
Ready authority. Existing governed lifecycle evidence may be represented only
through the separate fail-closed compatibility module.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from .canonical import fingerprint_bundle
from .model import BCRPBundle, BCRPRecord, PROFILE_VERSION, ValidationFinding
from .validation import validate_bundle

# Retained as the identity of the technical rule set, not a governance policy.
VALIDATION_POLICY_ID = "bcrp-validation-policy:1.0.0"
_CANDIDATE_KINDS = (
    "PresentationBriefRecord",
    "PortablePresentationMaterialRecord",
    "CandidatePresentationPackageRecord",
)
_LIFECYCLE_KINDS = (
    "ValidationJudgmentRecord",
    "ReadyPresentationPackageRecord",
    "PublicationReleaseRecord",
)


class BCRPAuthoringRejected(ValueError):
    """Raised when an authored Candidate closure cannot be admitted."""


class BCRPPromotionRejected(ValueError):
    """Raised when native BCRP attempts to exercise ungranted promotion authority."""


@dataclass(frozen=True)
class TechnicalValidationResult:
    """Non-governing BCRP L0-L2 evidence for one exact Candidate closure."""

    candidate_ref: str
    candidate_fingerprint: str
    executed_layers: tuple[str, ...]
    findings: tuple[ValidationFinding, ...]
    passed: bool


@dataclass(frozen=True)
class RecordDraft:
    """Transport-neutral input for one author-owned BCRP record body.

    The draft intentionally has no record-kind field. Named arguments assign the
    only three kinds this boundary may create, preventing authoring convenience
    from fabricating lifecycle, renderer, artifact, or manifest authority.
    """

    identity: str
    semantic: dict[str, Any]
    extensions: list[dict[str, Any]] = field(default_factory=list)


def author_candidate_bundle(
    *,
    brief: RecordDraft,
    material: RecordDraft,
    candidate: RecordDraft,
) -> BCRPBundle:
    """Create and technically validate one Brief + Material + Candidate closure."""

    drafts = (brief, material, candidate)
    if not all(isinstance(draft, RecordDraft) for draft in drafts):
        raise BCRPAuthoringRejected("Candidate authoring requires one RecordDraft for each named record role.")

    records = tuple(
        BCRPRecord(
            kind=kind,
            identity=deepcopy(draft.identity),
            profile_version=PROFILE_VERSION,
            semantic=deepcopy(draft.semantic),
            extensions=deepcopy(draft.extensions),
        )
        for kind, draft in zip(_CANDIDATE_KINDS, drafts, strict=True)
    )
    bundle = BCRPBundle(
        profile_identity="briefforge-core-representation-profile",
        profile_version=PROFILE_VERSION,
        records=records,
        index={"authored_in_memory": True},
    )
    result = validate_bundle(bundle, through_layer="L2")
    if result.blocking:
        first = next(finding for finding in result.findings if finding.severity == "blocking")
        raise BCRPAuthoringRejected(
            f"Candidate closure rejected at {first.layer}/{first.family}: {first.message}"
        )
    return bundle


def record_candidate_validation(bundle: BCRPBundle) -> TechnicalValidationResult:
    """Execute L0-L2 without creating lifecycle Judgment or approval.

    Complete findings are retained. Passing technical checks is not governance
    approval and is deliberately incapable of adding a BCRP lifecycle record.
    """

    _require_candidate_stage(bundle, operation="technical validation")
    result = validate_bundle(bundle, through_layer="L2")
    try:
        candidate_digest = fingerprint_bundle(
            bundle,
            domain="candidate-semantic",
            require_valid=False,
        ).digest
    except (TypeError, ValueError) as exc:
        raise BCRPAuthoringRejected(
            "Candidate is not canonicalizable enough to bind technical validation evidence."
        ) from exc

    return TechnicalValidationResult(
        candidate_ref=bundle.one("CandidatePresentationPackageRecord").identity,
        candidate_fingerprint=candidate_digest,
        executed_layers=result.executed_layers,
        findings=result.findings,
        passed=not result.blocking,
    )


def promote_validated_candidate(
    bundle: BCRPBundle,
    *,
    ready_identity: str,
    readiness_time: str,
) -> BCRPBundle:
    """Reject native BCRP promotion because it has no accepted authority.

    The signature remains temporarily stable so old callers receive the explicit
    fail-closed correction. Only the external legacy-compatibility adapter may
    represent an existing governed Ready result in BCRP.
    """

    del bundle, ready_identity, readiness_time
    raise BCRPPromotionRejected(
        "The governed legacy lifecycle is the sole operational promotion authority; "
        "use the fail-closed compatibility boundary to represent verified authority."
    )


def _require_candidate_stage(bundle: BCRPBundle, *, operation: str) -> None:
    if not isinstance(bundle, BCRPBundle):
        raise BCRPAuthoringRejected(f"BCRP {operation} requires a BCRPBundle.")
    counts = {kind: len(bundle.records_of_kind(kind)) for kind in _CANDIDATE_KINDS}
    if any(count != 1 for count in counts.values()):
        raise BCRPAuthoringRejected(f"BCRP {operation} requires exactly one Brief, Material, and Candidate record.")
    present_lifecycle = [kind for kind in _LIFECYCLE_KINDS if bundle.records_of_kind(kind)]
    if present_lifecycle:
        raise BCRPAuthoringRejected(
            f"BCRP {operation} input already contains lifecycle authority records: {', '.join(present_lifecycle)}."
        )
    if len(bundle.records) != 3:
        raise BCRPAuthoringRejected(f"Candidate-stage bundle contains records outside bounded {operation} scope.")
