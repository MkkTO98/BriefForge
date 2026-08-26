"""The single executable structural authority for BCRP 1.0.

The accepted human-readable BCRP specification remains semantic authority. This
module is deliberately the only machine structural definition: runtime and tests
execute these rules directly, so no decorative schema can drift independently.
"""

from __future__ import annotations

import re
from typing import Any

from .graph import inspect_graph
from .model import BCRPBundle, PROFILE_ID, RECORD_KINDS, ValidationFinding

STRUCTURE_AUTHORITY_ID = "bcrp-native-structure-authority:1.0.0"

IDENTITY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*$")
REQUIRED_SEMANTIC_KEYS = {
    "PresentationBriefRecord": ("organizing_purpose", "audiences", "scope", "non_scope"),
    "PortablePresentationMaterialRecord": (
        "authorities",
        "provenance",
        "evidence_snapshots",
        "external_references",
        "values",
        "consistency_assertions",
    ),
    "CandidatePresentationPackageRecord": (
        "brief_ref",
        "material_refs",
        "organizing_purpose",
        "audiences",
        "statements",
        "sections",
        "obligations",
        "renderer_requirements",
        "fallbacks",
        "selection_sets",
    ),
    "ValidationJudgmentRecord": ("candidate_ref", "candidate_fingerprint", "policy_id", "executed_layers", "valid"),
    "ReadyPresentationPackageRecord": ("candidate_ref", "candidate_fingerprint", "judgment_ref"),
    "PublicationReleaseRecord": (
        "publication_lineage_id",
        "semantic_publication_version",
        "ready_ref",
        "ready_fingerprint",
        "evidence_snapshot_refs",
        "release_authority_ref",
        "lifecycle_status",
        "publication_time",
    ),
    "RendererCapabilityDeclarationRecord": ("renderer_id", "renderer_version", "capabilities"),
    "RendererCompatibilityPlanRecord": (
        "ready_ref",
        "renderer_capability_ref",
        "declared_transformations",
        "fallbacks",
        "supported",
    ),
    "GeneratedArtifactAuditRecord": (
        "release_ref",
        "ready_ref",
        "ready_fingerprint",
        "plan_ref",
        "renderer_capability_ref",
        "artifact",
        "audit_links_pass",
    ),
    "SemanticArtifactConformanceRecord": ("audit_ref", "ready_ref", "audit_link_pass", "semantic_pass", "evidence"),
    "PublicationManifestRecord": ("release_ref", "lifecycle_status", "artifact_audit_refs", "conformance_refs"),
}

EXTENSION_KEYS = {
    "owner_namespace",
    "name",
    "version",
    "authority_ref",
    "scope",
    "target_refs",
    "criticality",
    "character",
    "validation_contract",
    "preservation",
    "payload",
}
SUPPORTED_EXTENSION_CONTRACTS = {"bcrp:core-extension-envelope:1.0.0"}
PROHIBITED_DOMAIN_KEYS = {
    "fiscal_period",
    "financial_reporting_date",
    "restatement",
    "corporate_action",
    "currency_conversion",
    "company_consolidation",
    "security_identity",
    "reporting_segment",
    "reported_value",
    "adjusted_value",
}
NO_PAYLOAD_STATES = {
    "missing-not-provided",
    "unavailable",
    "not-applicable",
    "suppressed-withheld",
    "unresolved",
    "invalid",
}
VALUE_STATES = {"present", "explicit-zero"} | NO_PAYLOAD_STATES
# BCRP Release records capture issuance-time state. Post-Release supersession,
# withdrawal, and staleness are separate append-only authority events.
RELEASE_LIFECYCLE_STATES = {"active"}


def _finding(
    family: str,
    identity: str,
    location: str,
    message: str,
    consequence: str = "profile admission",
    refs: tuple[str, ...] = (),
) -> ValidationFinding:
    return ValidationFinding("L1", family, "blocking", consequence, identity, location, message, refs)


def validate_structure(bundle: BCRPBundle) -> tuple[ValidationFinding, ...]:
    findings: list[ValidationFinding] = []
    if bundle.profile_identity != PROFILE_ID:
        findings.append(_finding("profile-structure-or-version", "bundle", "/profile/identity", "Unsupported profile identity."))
    if not isinstance(bundle.profile_version, str) or not bundle.profile_version.startswith("1."):
        findings.append(_finding("profile-structure-or-version", "bundle", "/profile/version", "Unsupported BCRP profile major version."))

    kind_counts = {kind: 0 for kind in RECORD_KINDS}
    record_ids: set[str] = set()
    for record in bundle.records:
        if record.kind not in RECORD_KINDS:
            findings.append(_finding("profile-structure-or-version", record.identity, "/record_kind", f"Unknown record kind {record.kind!r}."))
            continue
        kind_counts[record.kind] += 1
        if record.identity in record_ids:
            findings.append(_finding("identity-or-reference-integrity", record.identity, "/identity", "Duplicate root record identity."))
        record_ids.add(record.identity)
        if not _valid_identity(record.identity):
            findings.append(_finding("profile-structure-or-version", record.identity, "/identity", "Identity is not canonical ASCII BCRP syntax."))
        if record.profile_version != bundle.profile_version:
            findings.append(_finding("profile-structure-or-version", record.identity, "/profile/version", "Record and bundle profile versions differ."))
        if not isinstance(record.semantic, dict):
            findings.append(_finding("profile-structure-or-version", record.identity, "/semantic", "Record semantic body must be an object."))
            continue
        for key in REQUIRED_SEMANTIC_KEYS[record.kind]:
            if key not in record.semantic:
                findings.append(_finding("profile-structure-or-version", record.identity, f"/semantic/{key}", f"Required property {key!r} is absent."))
        if record.kind == "PublicationReleaseRecord":
            lifecycle_status = record.semantic.get("lifecycle_status")
            if lifecycle_status not in RELEASE_LIFECYCLE_STATES:
                findings.append(
                    _finding(
                        "profile-structure-or-version",
                        record.identity,
                        "/semantic/lifecycle_status",
                        f"Unsupported core Release lifecycle state {lifecycle_status!r}.",
                    )
                )
            if "lifecycle_events" in record.semantic:
                findings.append(
                    _finding(
                        "extension-boundary",
                        record.identity,
                        "/semantic/lifecycle_events",
                        "Undeclared embedded lifecycle event material cannot grant lifecycle authority; use a negotiated independent event profile.",
                        "all lifecycle-dependent processing",
                    )
                )
        _inspect_semantic_shape(record.semantic, record.identity, "/semantic", findings)
        _inspect_extensions(record.extensions, record.identity, findings)

    # A release/manifest profile instance is a complete publication closure.
    if kind_counts["PublicationManifestRecord"]:
        for kind, count in kind_counts.items():
            if count != 1:
                findings.append(
                    _finding(
                        "profile-structure-or-version",
                        "bundle",
                        f"/records/{kind}",
                        f"A publication bundle requires exactly one {kind}; found {count}.",
                    )
                )

    graph, graph_problems = inspect_graph(bundle)
    del graph
    for problem, location, value in graph_problems:
        if problem == "dangling-reference":
            findings.append(
                _finding(
                    "identity-or-reference-integrity",
                    location,
                    location,
                    f"Canonical reference targets absent identity {value!r}.",
                    "Candidate promotion",
                    (value,),
                )
            )
        elif problem == "duplicate-edge":
            findings.append(_finding("identity-or-reference-integrity", location, location, f"Duplicate canonical edge {value!r}."))
        else:
            findings.append(_finding("identity-or-reference-integrity", value, location, f"Duplicate semantic identity {value!r}."))

    return tuple(sorted(set(findings)))


def _valid_identity(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        value.encode("ascii")
    except UnicodeEncodeError:
        return False
    return bool(IDENTITY_RE.fullmatch(value))


def _inspect_semantic_shape(value: Any, owner: str, location: str, findings: list[ValidationFinding]) -> None:
    if isinstance(value, float) or value is None:
        findings.append(_finding("profile-structure-or-version", owner, location, "Null and binary floating values are not admitted."))
        return
    if isinstance(value, dict):
        object_id = value.get("id")
        if object_id is not None and not _valid_identity(object_id):
            findings.append(_finding("profile-structure-or-version", owner, f"{location}/id", "Nested identity is not canonical ASCII BCRP syntax."))
        for key in value:
            if key in PROHIBITED_DOMAIN_KEYS:
                findings.append(
                    _finding(
                        "domain-ownership-prohibition",
                        object_id or owner,
                        f"{location}/{key}",
                        f"BCRP 1.0 cannot define deferred financial-domain field {key!r}.",
                        "profile admission/Candidate promotion",
                    )
                )
        if "state_ids" in value:
            if "default_state_ref" not in value:
                findings.append(
                    _finding(
                        "selection-closure-or-state-narrative",
                        object_id or owner,
                        f"{location}/default_state_ref",
                        "Selection set requires one authority-declared default state.",
                        "Candidate promotion/selector release",
                    )
                )
            if "*" in value.get("state_ids", []):
                findings.append(
                    _finding(
                        "selection-closure-or-state-narrative",
                        object_id or owner,
                        f"{location}/state_ids",
                        "Wildcard state is not a finite BCRP identity.",
                        "Candidate promotion",
                    )
                )
        if "value_state" in value:
            state = value["value_state"]
            if state not in VALUE_STATES:
                findings.append(_finding("profile-structure-or-version", object_id or owner, f"{location}/value_state", f"Unknown core value state {state!r}."))
            payload_present = "payload" in value
            if state in {"present", "explicit-zero"} and not payload_present:
                findings.append(_finding("profile-structure-or-version", object_id or owner, f"{location}/payload", f"State {state!r} requires a payload."))
            if state in NO_PAYLOAD_STATES and payload_present:
                findings.append(_finding("profile-structure-or-version", object_id or owner, f"{location}/payload", f"State {state!r} prohibits an admitted payload.", "Candidate promotion"))
        if "coefficient" in value or "scale" in value:
            coefficient = value.get("coefficient")
            scale = value.get("scale")
            if set(value) != {"coefficient", "scale"} or not isinstance(coefficient, str) or not re.fullmatch(r"-?[0-9]+", coefficient) or not isinstance(scale, int) or scale < 0:
                findings.append(_finding("profile-structure-or-version", owner, location, "Exact decimal must be a coefficient string and non-negative integer scale."))
        for key, child in value.items():
            _inspect_semantic_shape(child, object_id or owner, f"{location}/{key}", findings)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _inspect_semantic_shape(child, owner, f"{location}/{index}", findings)


def _inspect_extensions(extensions: Any, owner: str, findings: list[ValidationFinding]) -> None:
    if not isinstance(extensions, list):
        findings.append(_finding("profile-structure-or-version", owner, "/extensions", "Extensions must be an array."))
        return
    for index, extension in enumerate(extensions):
        location = f"/extensions/{index}"
        if not isinstance(extension, dict) or set(extension) != EXTENSION_KEYS:
            findings.append(_finding("extension-boundary", owner, location, "Extension envelope is incomplete or contains undeclared envelope fields."))
            continue
        criticality = extension.get("criticality")
        character = extension.get("character")
        preservation = extension.get("preservation")
        if criticality not in {"required", "optional"} or character not in {"semantic", "display-only"} or preservation not in {"must-preserve", "discardable"}:
            findings.append(_finding("extension-boundary", owner, location, "Extension criticality, character, or preservation is invalid."))
        if character == "semantic" and preservation != "must-preserve":
            findings.append(_finding("extension-boundary", owner, location, "Semantic extensions must be preserved losslessly."))
        if criticality == "required" and extension.get("validation_contract") not in SUPPORTED_EXTENSION_CONTRACTS:
            findings.append(
                _finding(
                    "extension-boundary",
                    owner,
                    location,
                    "Unknown required semantic extension cannot be processed.",
                    "all dependent processing",
                )
            )
        _inspect_semantic_shape(extension.get("payload"), owner, f"{location}/payload", findings)
