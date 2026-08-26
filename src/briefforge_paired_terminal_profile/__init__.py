"""Versioned representative paired terminal profile core."""
from .schema import (
    Obligation,
    PairedAdmissionEnvelope,
    PairedEditorialProjection,
    PairedRow,
    PairedSchemaRejected,
    PairedSemanticInput,
    PairedTable,
    PairedValue,
    Provenance,
    QualificationEdge,
    Section,
    SectionChild,
    Statement,
    validate_paired_projection,
    validate_paired_semantics,
)
from .profile import (
    PairedProfileRejected,
    PairedUpstreamAdmissionToken,
    admit_paired_terminal_semantics,
    verify_full_upstream_paired_terminal_admission,
    verify_paired_upstream_admission_token,
)
from .projection import (
    PairedProjectionRejected,
    build_paired_editorial_projection,
    verify_paired_editorial_projection,
)

__all__ = (
    "Obligation", "PairedAdmissionEnvelope", "PairedEditorialProjection", "PairedRow",
    "PairedSchemaRejected", "PairedSemanticInput", "PairedTable", "PairedValue",
    "Provenance", "QualificationEdge", "Section", "SectionChild", "Statement",
    "validate_paired_projection", "validate_paired_semantics", "PairedProfileRejected",
    "PairedUpstreamAdmissionToken", "admit_paired_terminal_semantics",
    "verify_full_upstream_paired_terminal_admission", "verify_paired_upstream_admission_token",
    "PairedProjectionRejected", "build_paired_editorial_projection",
    "verify_paired_editorial_projection",
)
