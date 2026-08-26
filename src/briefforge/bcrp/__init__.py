"""BriefForge Core Representation Profile 1.0 vertical-slice API.

This package is intentionally independent of the existing runtime and renderer.
"""

from .authoring import (
    BCRPAuthoringRejected,
    BCRPPromotionRejected,
    RecordDraft,
    TechnicalValidationResult,
    VALIDATION_POLICY_ID,
    author_candidate_bundle,
    promote_validated_candidate,
    record_candidate_validation,
)
from .canonical import (
    artifact_equal,
    bundle_from_canonical_json,
    canonical_json_bytes,
    canonicalize_exact_decimal,
    canonicalize_timestamp,
    fingerprint_bundle,
    presentation_equivalent,
    profile_instance_equal,
    semantic_equal,
)
from .graph import GraphReconstructionError, reconstruct_graph
from .loader import BundleLoadError, load_bundle
from .model import (
    BCRPBundle,
    BCRPRecord,
    Fingerprint,
    PROFILE_ID,
    PROFILE_VERSION,
    SemanticGraph,
    ValidationFinding,
    ValidationResult,
)
from .validation import validate_bundle

__all__ = [
    "BCRPAuthoringRejected",
    "BCRPBundle",
    "BCRPPromotionRejected",
    "BCRPRecord",
    "BundleLoadError",
    "Fingerprint",
    "GraphReconstructionError",
    "PROFILE_ID",
    "PROFILE_VERSION",
    "RecordDraft",
    "SemanticGraph",
    "TechnicalValidationResult",
    "VALIDATION_POLICY_ID",
    "ValidationFinding",
    "ValidationResult",
    "artifact_equal",
    "author_candidate_bundle",
    "bundle_from_canonical_json",
    "canonical_json_bytes",
    "canonicalize_exact_decimal",
    "canonicalize_timestamp",
    "fingerprint_bundle",
    "load_bundle",
    "presentation_equivalent",
    "profile_instance_equal",
    "promote_validated_candidate",
    "reconstruct_graph",
    "record_candidate_validation",
    "semantic_equal",
    "validate_bundle",
]
