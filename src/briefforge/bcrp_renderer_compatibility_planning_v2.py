"""Renderer-independent, fail-closed BCRP compatibility planning.

This module consumes exact governed semantic evidence and emits at most one
compatibility Plan.  It never imports, discovers, selects, probes, or invokes a
renderer and grants no artifact, conformance, Manifest, or distribution
authority.
"""
from __future__ import annotations

from copy import deepcopy
import ctypes
from dataclasses import dataclass
from datetime import datetime
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Any

from .bcrp.canonical import canonicalize_timestamp, fingerprint_bundle
from .bcrp.model import BCRPBundle, BCRPRecord, Fingerprint, PROFILE_ID, PROFILE_VERSION
from .bcrp.validation import validate_bundle
from .publication_lifecycle import derive_current_state, fingerprint_event, validate_lifecycle
from .publication_lifecycle.model import (
    EventAuthority,
    LifecycleBundle,
    LifecyclePolicy,
    PublicationLifecycleEvent,
    ReleaseBinding,
    ReleaseReference,
)
from .bcrp_publication_release_v2 import (
    EvidenceSnapshot,
    VerifiedPublicationRelease,
    release_binding_from_verified_release,
    verify_publication_release,
)
from .bcrp_paired_derivation_evidence_v2 import (
    DerivationEvidenceEnvelopeV2,
    verify_derivation_evidence_envelope_v2,
)
from .bcrp_paired_semantic_interpretation_v2 import (
    PairedInterpretation, interpret_paired_candidate,
)
from .task076_contracts import (
    AuthenticatedGeneration8Candidate,
    authenticate_generation8_candidate,
    canonical_json,
    domain_digest,
)

PLANNING_POLICY_ID = "briefforge-renderer-compatibility-planning-policy:1.0.0"
CAPABILITY_DECLARATION_CONTRACT = "briefforge:renderer-capability-declaration:1.0.0"
PLAN_CONTRACT = "briefforge:renderer-compatibility-plan:1.0.0"
AUTHORIZATION_CONTRACT = "briefforge:renderer-compatibility-planning-authorization:1.0.0"
ACCEPTED_DECLARATION_PROFILE_ID = "briefforge-renderer-capability-profile"
ACCEPTED_DECLARATION_PROFILE_VERSION = "1.0.0"
ACCEPTED_RENDERER_OWNER = "project:BriefForge"
ACCEPTED_RENDERER_ROLE = "bounded-publication-renderer"
ACCEPTED_PLANNING_AUTHORITY_IDENTITY = "authority:briefforge-renderer-compatibility-planning"
ACCEPTED_PLANNING_AUTHORITY_OWNER = "project:BriefForge"
ACCEPTED_PLANNING_AUTHORITY_ROLE = "renderer-compatibility-planning-authority"
_DECLARATION_AUTHORITY_IDENTITY = "authority:briefforge-renderer-capability-declaration"
_DECLARATION_EXTENSION_OWNER = "briefforge-renderer-capability"
_DECLARATION_EXTENSION_NAME = "renderer-capability-declaration"
_PLAN_EXTENSION_OWNER = "briefforge-renderer-compatibility-planning"
_PLAN_EXTENSION_NAME = "renderer-compatibility-plan"
_EXTENSION_VERSION = "1.0.0"
_EXTENSION_KEYS = {
    "owner_namespace", "name", "version", "authority_ref", "scope", "target_refs",
    "criticality", "character", "validation_contract", "preservation", "payload",
}
_PLAN_SEMANTIC_KEYS = {
    "ready_ref", "renderer_capability_ref", "declared_transformations", "fallbacks", "supported", "mode",
}
_CAPABILITY_SEMANTIC_KEYS = {
    "renderer_id", "renderer_version", "capabilities", "declaration_identity",
    "capability_profile_identity", "capability_profile_version", "declaration_time",
    "inventory_complete", "unsupported_capabilities", "declared_constraints", "claim_character",
}
_REQUIREMENT_KEYS = {
    "id", "capability", "mandatory", "criticality", "target_refs", "authority_label_refs",
    "caveat_refs", "required_constraints", "permitted_transformations", "fallback_refs",
    "unsupported_allowed",
}
_FALLBACK_KEYS = {
    "id", "kind", "expression_mode", "required_capability", "complete", "covers_semantic_refs",
    "preserves_authority_label_refs", "preserves_caveat_refs", "transformation",
}
_FALLBACK_KIND_MODE = {
    "equivalent-expression": "equivalent",
    "static-state-expansion": "static",
    "static-table": "static",
    "static-visual": "static",
    "static-text": "static",
    "print-expression": "static",
}
_MAPPING_KEYS = {
    "requirement_id", "affected_semantic_identities", "criticality", "selected_expression_mode",
    "capability_id", "fallback_id", "transformation", "reason",
}
_EXCLUDED_AUTHORITIES = [
    "renderer-selection", "renderer-invocation", "renderer-output", "artifact",
    "artifact-conformance", "publication-manifest", "distribution",
]
_IDENTITY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*$")
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_SEMVER_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


class PlanningRejected(ValueError):
    """Raised when persisted content cannot be independently accepted."""


@dataclass(frozen=True, order=True)
class CapabilityClaim:
    identity: str
    expression_mode: str
    constraints: tuple[str, ...]
    supported: bool


@dataclass(frozen=True)
class RendererCapabilityDeclaration:
    identity: str
    contract_identity: str
    capability_profile_identity: str
    capability_profile_version: str
    renderer_identity: str
    renderer_version: str
    renderer_owner: str
    renderer_role: str
    declaration_time: str
    inventory_complete: bool
    capabilities: tuple[CapabilityClaim, ...]
    unsupported_capabilities: tuple[str, ...]
    declared_constraints: tuple[str, ...]
    extensions: tuple[str, ...]
    fingerprint: str


@dataclass(frozen=True)
class LifecyclePlanningScope:
    bundle: LifecycleBundle
    releases: tuple[ReleaseBinding, ...]
    policies: tuple[LifecyclePolicy, ...]
    inventory_complete: bool
    inventory_digest: str


@dataclass(frozen=True)
class PlanningAuthorization:
    identity: str
    policy_identity: str
    authority_identity: str
    authority_owner: str
    authority_role: str
    authorization_time: str
    release_identity: str
    release_fingerprint: str
    capability_declaration_identity: str
    capability_declaration_fingerprint: str
    plan_identity: str
    planning_time: str


@dataclass(frozen=True, order=True)
class PlanningFinding:
    code: str
    requirement_identity: str
    location: str
    message: str
    affected_identities: tuple[str, ...] = ()


@dataclass(frozen=True)
class VerifiedRendererCompatibilityPlan:
    _bundle_document: str
    fingerprint: Fingerprint
    mappings_document: str

    @property
    def bundle(self) -> BCRPBundle:
        return _deserialize_bundle(self._bundle_document)

    @property
    def plan(self) -> BCRPRecord:
        return self.bundle.one("RendererCompatibilityPlanRecord")

    @property
    def mappings(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(json.loads(self.mappings_document)))


@dataclass(frozen=True)
class CompatibilityPlanningResult:
    findings: tuple[PlanningFinding, ...]
    plan: VerifiedRendererCompatibilityPlan | None

    @property
    def blocked(self) -> bool:
        return self.plan is None


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _normal_time(value: str, label: str) -> str:
    try:
        return canonicalize_timestamp(value)
    except (TypeError, ValueError) as exc:
        raise PlanningRejected(f"{label} must be explicit and canonicalizable.") from exc


def _require_identity(value: str, label: str) -> None:
    if not isinstance(value, str) or not _IDENTITY_RE.fullmatch(value):
        raise PlanningRejected(f"{label} must be an explicit canonical identity.")


def _unique_strings(value: Any, label: str, *, nonempty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)) or not all(isinstance(item, str) and item for item in value):
        raise PlanningRejected(f"{label} must be an explicit string sequence.")
    result = tuple(value)
    if nonempty and not result:
        raise PlanningRejected(f"{label} cannot be empty.")
    if len(set(result)) != len(result):
        raise PlanningRejected(f"{label} contains duplicate identities.")
    return result


def _claim_document(item: CapabilityClaim) -> dict[str, Any]:
    return {
        "identity": item.identity,
        "expression_mode": item.expression_mode,
        "constraints": sorted(item.constraints),
        "supported": item.supported,
    }


def _declaration_fingerprint_document(declaration: RendererCapabilityDeclaration) -> dict[str, Any]:
    return {
        "contract_identity": declaration.contract_identity,
        "identity": declaration.identity,
        "capability_profile_identity": declaration.capability_profile_identity,
        "capability_profile_version": declaration.capability_profile_version,
        "renderer_identity": declaration.renderer_identity,
        "renderer_version": declaration.renderer_version,
        "renderer_owner": declaration.renderer_owner,
        "renderer_role": declaration.renderer_role,
        "declaration_time": _normal_time(declaration.declaration_time, "declaration time"),
        "inventory_complete": declaration.inventory_complete,
        "capabilities": sorted((_claim_document(item) for item in declaration.capabilities), key=lambda item: item["identity"]),
        "unsupported_capabilities": sorted(declaration.unsupported_capabilities),
        "declared_constraints": sorted(declaration.declared_constraints),
        "extensions": sorted(declaration.extensions),
        "claim_character": "renderer-owned-claim-not-conformance-proof",
    }


def compute_capability_declaration_fingerprint(declaration: RendererCapabilityDeclaration) -> str:
    """Compute one declaration digest without trusting its stored fingerprint."""

    return hashlib.sha256(_json_bytes(_declaration_fingerprint_document(declaration))).hexdigest()


def _policy_document(policy: LifecyclePolicy) -> dict[str, Any]:
    return {
        "identity": policy.identity,
        "allowed_authorities": sorted([list(item) for item in policy.allowed_authorities]),
        "allowed_event_types": sorted(policy.allowed_event_types),
        "allowed_reason_classifications": sorted(policy.allowed_reason_classifications),
        "distribution_consequences": sorted([list(item) for item in policy.distribution_consequences]),
    }


def _release_binding_document(binding: ReleaseBinding) -> dict[str, Any]:
    return {
        "identity": binding.identity, "fingerprint": binding.fingerprint,
        "fingerprint_domain": binding.fingerprint_domain,
        "fingerprint_profile_identity": binding.fingerprint_profile_identity,
        "fingerprint_profile_version": binding.fingerprint_profile_version,
        "fingerprint_canonicalization": binding.fingerprint_canonicalization,
        "fingerprint_algorithm": binding.fingerprint_algorithm,
        "fingerprint_root_identity": binding.fingerprint_root_identity,
        "publication_identity": binding.publication_identity,
        "semantic_publication_version": binding.semantic_publication_version,
        "publication_time": binding.publication_time,
    }


def _lifecycle_inventory_document(scope: LifecyclePlanningScope) -> dict[str, Any]:
    return {
        "profile_identity": scope.bundle.profile_identity,
        "profile_version": scope.bundle.profile_version,
        "inventory_complete": scope.inventory_complete,
        "releases": sorted((_release_binding_document(item) for item in scope.releases), key=lambda item: item["identity"]),
        "events": sorted(({
            "identity": item.identity,
            "fingerprint": fingerprint_event(item).digest,
        } for item in scope.bundle.events), key=lambda item: item["identity"]),
        "policies": sorted((_policy_document(item) for item in scope.policies), key=lambda item: item["identity"]),
    }


def compute_lifecycle_inventory_digest(scope: LifecyclePlanningScope) -> str:
    """Digest an explicitly complete lifecycle Release/event/policy catalog."""

    return hashlib.sha256(_json_bytes(_lifecycle_inventory_document(scope))).hexdigest()


def _finding(code: str, message: str, requirement: str = "bundle", location: str = "/", refs: tuple[str, ...] = ()) -> PlanningFinding:
    return PlanningFinding(code, requirement, location, message, tuple(sorted(refs)))


def _verify_declaration(declaration: RendererCapabilityDeclaration) -> tuple[PlanningFinding, ...]:
    findings: list[PlanningFinding] = []
    try:
        for value, label in ((declaration.identity, "declaration identity"), (declaration.renderer_identity, "renderer identity")):
            _require_identity(value, label)
        _normal_time(declaration.declaration_time, "declaration time")
    except (PlanningRejected, AttributeError, TypeError) as exc:
        findings.append(_finding("invalid-capability-declaration", str(exc), location="/declaration"))
        return tuple(findings)
    if declaration.contract_identity != CAPABILITY_DECLARATION_CONTRACT:
        findings.append(_finding("unknown-declaration-contract", "Capability declaration contract is not accepted.", location="/declaration/contract_identity"))
    if (declaration.capability_profile_identity, declaration.capability_profile_version) != (
        ACCEPTED_DECLARATION_PROFILE_ID, ACCEPTED_DECLARATION_PROFILE_VERSION
    ):
        findings.append(_finding("unknown-capability-profile", "Capability profile identity or version is not accepted.", location="/declaration/profile"))
    if declaration.renderer_owner != ACCEPTED_RENDERER_OWNER or declaration.renderer_role != ACCEPTED_RENDERER_ROLE:
        findings.append(_finding("unauthorized-declaration-authority", "Renderer declaration owner or role is outside the accepted policy.", location="/declaration/authority"))
    if not isinstance(declaration.renderer_version, str) or not _SEMVER_RE.fullmatch(declaration.renderer_version):
        findings.append(_finding("invalid-renderer-version", "Renderer implementation version/build must be explicit SemVer.", location="/declaration/renderer_version"))
    if declaration.inventory_complete is not True:
        findings.append(_finding("incomplete-capability-inventory", "Capability inventory must be explicitly complete.", location="/declaration/inventory_complete"))
    if any(type(value) is not tuple for value in (
        declaration.capabilities,
        declaration.unsupported_capabilities,
        declaration.declared_constraints,
        declaration.extensions,
    )):
        findings.append(_finding(
            "invalid-capability-inventory",
            "Every declaration inventory must be an exact immutable tuple.",
            location="/declaration",
        ))
    if not isinstance(declaration.capabilities, tuple) or not all(type(item) is CapabilityClaim for item in declaration.capabilities):
        findings.append(_finding("invalid-capability-inventory", "Capabilities must be an immutable tuple of exact claims.", location="/declaration/capabilities"))
        return tuple(sorted(set(findings)))
    seen: set[str] = set()
    for index, item in enumerate(declaration.capabilities):
        try:
            _require_identity(item.identity, "capability identity")
            _unique_strings(item.constraints, "capability constraints")
        except PlanningRejected as exc:
            findings.append(_finding("invalid-capability-claim", str(exc), str(item.identity), f"/declaration/capabilities/{index}"))
            continue
        if item.identity in seen:
            findings.append(_finding("duplicate-capability-identity", "Capability identities must be unique; duplicate matches are ambiguous.", item.identity, f"/declaration/capabilities/{index}"))
        seen.add(item.identity)
        if type(item.constraints) is not tuple:
            findings.append(_finding(
                "invalid-capability-inventory",
                "Capability constraints must be an exact immutable tuple.",
                item.identity,
                f"/declaration/capabilities/{index}/constraints",
            ))
        if type(item.expression_mode) is not str or item.expression_mode not in {"native", "equivalent", "static"} or type(item.supported) is not bool or item.supported is not True:
            findings.append(_finding("invalid-capability-claim", "Declared inventory items must be supported exact native/equivalent/static claims.", item.identity, f"/declaration/capabilities/{index}"))
    try:
        unsupported = _unique_strings(declaration.unsupported_capabilities, "unsupported capability inventory")
        _unique_strings(declaration.declared_constraints, "declaration constraints")
        _unique_strings(declaration.extensions, "declaration extensions")
        if set(unsupported) & seen:
            findings.append(_finding("contradictory-capability-inventory", "A capability cannot be both supported and explicitly unsupported.", location="/declaration/unsupported_capabilities"))
    except PlanningRejected as exc:
        findings.append(_finding("invalid-capability-inventory", str(exc), location="/declaration"))
    try:
        computed = compute_capability_declaration_fingerprint(declaration)
    except (PlanningRejected, TypeError, ValueError) as exc:
        findings.append(_finding("invalid-capability-declaration", str(exc), location="/declaration/fingerprint"))
    else:
        if declaration.fingerprint != computed or not _DIGEST_RE.fullmatch(declaration.fingerprint):
            findings.append(_finding("capability-declaration-fingerprint-mismatch", "Capability declaration fingerprint does not match its complete inventory.", location="/declaration/fingerprint"))
    return tuple(sorted(set(findings)))


def _lifecycle_event_is_immutable(event: PublicationLifecycleEvent) -> bool:
    return (
        type(event) is PublicationLifecycleEvent
        and type(event.target_release) is ReleaseReference
        and (event.predecessor_release is None or type(event.predecessor_release) is ReleaseReference)
        and (event.successor_release is None or type(event.successor_release) is ReleaseReference)
        and type(event.authority) is EventAuthority
        and type(event.predecessor_event_refs) is tuple
        and all(type(item) is str for item in event.predecessor_event_refs)
        and type(event.extension_documents) is tuple
        and all(type(item) is str for item in event.extension_documents)
    )


def _lifecycle_policy_is_immutable(policy: LifecyclePolicy) -> bool:
    return (
        type(policy) is LifecyclePolicy
        and type(policy.allowed_authorities) is tuple
        and all(type(item) is tuple and len(item) == 3 and all(type(value) is str for value in item) for item in policy.allowed_authorities)
        and type(policy.allowed_event_types) is tuple
        and all(type(item) is str for item in policy.allowed_event_types)
        and type(policy.allowed_reason_classifications) is tuple
        and all(type(item) is str for item in policy.allowed_reason_classifications)
        and type(policy.distribution_consequences) is tuple
        and all(type(item) is tuple and len(item) == 2 and all(type(value) is str for value in item) for item in policy.distribution_consequences)
    )


def _verify_lifecycle_scope(scope: LifecyclePlanningScope, release_binding: ReleaseBinding) -> tuple[tuple[PlanningFinding, ...], dict[str, Any] | None]:
    findings: list[PlanningFinding] = []
    if type(scope) is not LifecyclePlanningScope:
        return (_finding("missing-lifecycle-scope", "An explicit complete lifecycle scope is required.", location="/lifecycle"),), None
    if (
        type(scope.bundle) is not LifecycleBundle
        or type(scope.bundle.events) is not tuple
        or not all(_lifecycle_event_is_immutable(item) for item in scope.bundle.events)
        or type(scope.releases) is not tuple
        or not all(type(item) is ReleaseBinding for item in scope.releases)
        or type(scope.policies) is not tuple
        or not all(_lifecycle_policy_is_immutable(item) for item in scope.policies)
        or type(scope.inventory_digest) is not str
    ):
        return (_finding(
            "invalid-lifecycle-scope",
            "Lifecycle bundle, event, Release, policy, and digest members must use exact immutable governed types.",
            location="/lifecycle",
        ),), None
    if scope.inventory_complete is not True:
        findings.append(_finding("incomplete-lifecycle-scope", "Lifecycle inventory must be explicitly complete; omission is not empty.", location="/lifecycle/inventory_complete"))
    try:
        computed = compute_lifecycle_inventory_digest(scope)
    except (AttributeError, TypeError, ValueError) as exc:
        findings.append(_finding("invalid-lifecycle-scope", str(exc), location="/lifecycle"))
        computed = ""
    if scope.inventory_digest != computed or not _DIGEST_RE.fullmatch(scope.inventory_digest):
        findings.append(_finding("lifecycle-inventory-fingerprint-mismatch", "Lifecycle scope digest does not match its complete Release/event/policy inventory.", location="/lifecycle/inventory_digest"))
    try:
        result = validate_lifecycle(scope.bundle, scope.releases, scope.policies)
    except (AttributeError, TypeError, ValueError) as exc:
        return (_finding("invalid-lifecycle-scope", str(exc), location="/lifecycle"),), None
    for item in result.findings:
        findings.append(_finding(f"lifecycle-{item.code}", item.message, item.event_identity, item.location))
    if findings:
        return tuple(sorted(set(findings))), None
    try:
        state = derive_current_state(scope.bundle, scope.releases, scope.policies)
    except ValueError as exc:
        return (_finding("ambiguous-lifecycle-state", str(exc), location="/lifecycle"),), None
    state_map = dict(state.release_states)
    if release_binding.identity not in {item.identity for item in scope.releases}:
        findings.append(_finding("release-absent-from-lifecycle-scope", "The exact planned Release is absent from the complete lifecycle catalog.", location="/lifecycle/releases"))
    else:
        catalog_binding = next(item for item in scope.releases if item.identity == release_binding.identity)
        if catalog_binding != release_binding:
            findings.append(_finding("lifecycle-release-binding-mismatch", "Lifecycle catalog binds different immutable Release metadata.", location="/lifecycle/releases"))
    if state.current_release_identity != release_binding.identity or state_map.get(release_binding.identity) != "current":
        findings.append(_finding("release-not-active-current", "Ordinary planning admits only the exact sole graph-derived current Release.", release_binding.identity, "/lifecycle/current_release"))
    closure = {
        "inventory_complete": True,
        "inventory_digest": scope.inventory_digest,
        "release_catalog": [_release_binding_document(item) for item in sorted(scope.releases, key=lambda item: item.identity)],
        "event_inventory": [{"identity": item.identity, "fingerprint": fingerprint_event(item).digest} for item in sorted(scope.bundle.events, key=lambda item: item.identity)],
        "policy_identities": sorted(item.identity for item in scope.policies),
        "current_release_identity": state.current_release_identity or "",
        "release_states": [{"release_identity": identity, "state": value} for identity, value in state.release_states],
        "applied_event_identities": list(state.applied_event_identities),
    }
    return tuple(sorted(set(findings))), closure if not findings else None


def _verify_authorization(authorization: PlanningAuthorization, release: VerifiedPublicationRelease, declaration: RendererCapabilityDeclaration) -> tuple[PlanningFinding, ...]:
    findings: list[PlanningFinding] = []
    if type(authorization) is not PlanningAuthorization:
        return (_finding("missing-planning-authorization", "Explicit planning authorization is required.", location="/authorization"),)
    try:
        for value, label in ((authorization.identity, "authorization identity"), (authorization.plan_identity, "Plan identity")):
            _require_identity(value, label)
        auth_time = _normal_time(authorization.authorization_time, "authorization time")
        plan_time = _normal_time(authorization.planning_time, "planning time")
        declaration_time = _normal_time(declaration.declaration_time, "declaration time")
        if datetime.fromisoformat(auth_time[:-1] + "+00:00") < datetime.fromisoformat(declaration_time[:-1] + "+00:00"):
            findings.append(_finding("planning-time-contradiction", "Planning authorization predates the capability declaration.", location="/authorization/authorization_time"))
        if datetime.fromisoformat(plan_time[:-1] + "+00:00") < datetime.fromisoformat(auth_time[:-1] + "+00:00"):
            findings.append(_finding("planning-time-contradiction", "Plan time predates planning authorization.", location="/authorization/planning_time"))
    except (PlanningRejected, TypeError, AttributeError) as exc:
        findings.append(_finding("invalid-planning-authorization", str(exc), location="/authorization"))
        return tuple(findings)
    if authorization.policy_identity != PLANNING_POLICY_ID:
        findings.append(_finding("unknown-planning-policy", "Planning policy identity is not accepted.", location="/authorization/policy_identity"))
    if (authorization.authority_identity, authorization.authority_owner, authorization.authority_role) != (
        ACCEPTED_PLANNING_AUTHORITY_IDENTITY, ACCEPTED_PLANNING_AUTHORITY_OWNER, ACCEPTED_PLANNING_AUTHORITY_ROLE
    ):
        findings.append(_finding("unauthorized-planning-authority", "Planning authority identity, owner, or role is outside policy.", location="/authorization/authority"))
    expected = {
        "release_identity": release.release.identity,
        "release_fingerprint": release.fingerprint.digest,
        "capability_declaration_identity": declaration.identity,
        "capability_declaration_fingerprint": declaration.fingerprint,
    }
    for key, value in expected.items():
        if getattr(authorization, key) != value:
            findings.append(_finding("planning-authorization-binding-mismatch", f"Planning authorization binds another {key.replace('_', ' ')}.", location=f"/authorization/{key}"))
    return tuple(sorted(set(findings)))


def _candidate_material(candidate: BCRPRecord) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], tuple[PlanningFinding, ...]]:
    findings: list[PlanningFinding] = []
    requirements = candidate.semantic.get("renderer_requirements")
    fallbacks = candidate.semantic.get("fallbacks")
    if not isinstance(requirements, list):
        return [], {}, (_finding("invalid-requirement-inventory", "Renderer requirements must be an explicit list.", location="/candidate/renderer_requirements"),)
    if not isinstance(fallbacks, list):
        return [], {}, (_finding("invalid-fallback-inventory", "Fallbacks must be an explicit list.", location="/candidate/fallbacks"),)
    requirement_ids: set[str] = set()
    normalized_requirements: list[dict[str, Any]] = []
    for index, item in enumerate(requirements):
        raw_identity = item.get("id", "") if isinstance(item, dict) else ""
        identity = raw_identity if isinstance(raw_identity, str) else f"invalid-requirement:{index}"
        location = f"/candidate/renderer_requirements/{index}"
        if not isinstance(item, dict) or set(item) != _REQUIREMENT_KEYS:
            findings.append(_finding("invalid-renderer-requirement", "Requirement fields are incomplete or undeclared.", identity or "bundle", location))
            continue
        if identity in requirement_ids:
            findings.append(_finding("duplicate-renderer-requirement", "Requirement identity is duplicated.", identity, location))
        requirement_ids.add(identity)
        try:
            _require_identity(identity, "requirement identity")
            _require_identity(item["capability"], "required capability identity")
            targets = _unique_strings(item["target_refs"], "affected semantic identities", nonempty=True)
            authority_refs = _unique_strings(item["authority_label_refs"], "authority label refs")
            caveat_refs = _unique_strings(item["caveat_refs"], "caveat refs")
            constraints = _unique_strings(item["required_constraints"], "required constraints")
            transformations = _unique_strings(item["permitted_transformations"], "permitted transformations")
            fallback_refs = _unique_strings(item["fallback_refs"], "fallback refs")
        except PlanningRejected as exc:
            findings.append(_finding("invalid-renderer-requirement", str(exc), identity or "bundle", location))
            continue
        if type(item["mandatory"]) is not bool or type(item["unsupported_allowed"]) is not bool:
            findings.append(_finding("invalid-renderer-requirement", "Mandatory and unsupported-allowed flags must be explicit Booleans.", identity, location))
        expected_criticality = "required" if item["mandatory"] else "optional"
        if item["criticality"] != expected_criticality:
            findings.append(_finding("contradictory-requirement-criticality", "Mandatory and criticality semantics contradict.", identity, location))
        normalized = deepcopy(item)
        normalized["target_refs"] = list(targets)
        normalized["authority_label_refs"] = list(authority_refs)
        normalized["caveat_refs"] = list(caveat_refs)
        normalized["required_constraints"] = list(constraints)
        normalized["permitted_transformations"] = list(transformations)
        normalized["fallback_refs"] = list(fallback_refs)
        normalized_requirements.append(normalized)
    fallback_map: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(fallbacks):
        raw_identity = item.get("id", "") if isinstance(item, dict) else ""
        identity = raw_identity if isinstance(raw_identity, str) else f"invalid-fallback:{index}"
        location = f"/candidate/fallbacks/{index}"
        if not isinstance(item, dict) or set(item) != _FALLBACK_KEYS:
            findings.append(_finding("invalid-fallback", "Fallback fields are incomplete or undeclared.", identity or "bundle", location))
            continue
        if identity in fallback_map:
            findings.append(_finding("duplicate-fallback", "Fallback identity is duplicated and ambiguous.", identity, location))
        try:
            _require_identity(identity, "fallback identity")
            _require_identity(item["required_capability"], "fallback capability identity")
            _unique_strings(item["covers_semantic_refs"], "fallback semantic coverage", nonempty=True)
            _unique_strings(item["preserves_authority_label_refs"], "fallback authority coverage")
            _unique_strings(item["preserves_caveat_refs"], "fallback caveat coverage")
            _require_identity(item["transformation"], "fallback transformation")
        except PlanningRejected as exc:
            findings.append(_finding("invalid-fallback", str(exc), identity or "bundle", location))
        mode = item["expression_mode"]
        if type(mode) is not str or mode not in {"equivalent", "static"} or type(item["complete"]) is not bool:
            findings.append(_finding("invalid-fallback", "Fallback mode and completeness must be exact.", str(identity), location))
        if not isinstance(item["kind"], str) or type(mode) is not str or _FALLBACK_KIND_MODE.get(item["kind"]) != mode:
            findings.append(_finding(
                "invalid-fallback",
                "Fallback kind must be a closed accepted kind consistent with its exact expression mode.",
                str(identity),
                f"{location}/kind",
            ))
        fallback_map[identity] = deepcopy(item)
    for requirement in normalized_requirements:
        for fallback_ref in requirement["fallback_refs"]:
            if fallback_ref not in fallback_map:
                findings.append(_finding("unknown-fallback-reference", "Requirement references a fallback absent from the governed Candidate.", requirement["id"], "/candidate/renderer_requirements", (fallback_ref,)))
    return normalized_requirements, fallback_map, tuple(sorted(set(findings)))


def _capability_matches(declaration: RendererCapabilityDeclaration, identity: str, mode: str, constraints: tuple[str, ...]) -> tuple[CapabilityClaim, ...]:
    return tuple(item for item in declaration.capabilities if item.identity == identity and item.expression_mode == mode and set(constraints).issubset(item.constraints))


def _plan_requirements(requirements: list[dict[str, Any]], fallbacks: dict[str, dict[str, Any]], declaration: RendererCapabilityDeclaration) -> tuple[list[dict[str, Any]], tuple[PlanningFinding, ...]]:
    mappings: list[dict[str, Any]] = []
    findings: list[PlanningFinding] = []
    for requirement in requirements:
        identity = requirement["id"]
        targets = tuple(requirement["target_refs"])
        constraints = tuple(requirement["required_constraints"])
        native = _capability_matches(declaration, requirement["capability"], "native", constraints)
        if len(native) == 1:
            mappings.append({
                "requirement_id": identity, "affected_semantic_identities": list(targets),
                "criticality": requirement["criticality"], "selected_expression_mode": "native",
                "capability_id": native[0].identity, "fallback_id": "", "transformation": "",
                "reason": "exact-native-capability-and-constraints-declared",
            })
            continue
        if len(native) > 1:
            findings.append(_finding("ambiguous-capability-match", "Multiple exact native claims remain at the same policy rank.", identity, "/declaration/capabilities", targets))
            continue
        selected: dict[str, Any] | None = None
        for mode in ("equivalent", "static"):
            choices: list[tuple[dict[str, Any], CapabilityClaim]] = []
            for fallback_ref in requirement["fallback_refs"]:
                fallback = fallbacks.get(fallback_ref)
                if fallback is None or fallback["expression_mode"] != mode:
                    continue
                complete = (
                    fallback["complete"] is True
                    and set(targets).issubset(fallback["covers_semantic_refs"])
                    and set(requirement["authority_label_refs"]).issubset(fallback["preserves_authority_label_refs"])
                    and set(requirement["caveat_refs"]).issubset(fallback["preserves_caveat_refs"])
                    and fallback["transformation"] in requirement["permitted_transformations"]
                )
                if not complete:
                    continue
                matches = _capability_matches(declaration, fallback["required_capability"], mode, constraints)
                choices.extend((fallback, claim) for claim in matches)
            if len(choices) == 1:
                fallback, claim = choices[0]
                selected = {
                    "requirement_id": identity, "affected_semantic_identities": list(targets),
                    "criticality": requirement["criticality"], "selected_expression_mode": mode,
                    "capability_id": claim.identity, "fallback_id": fallback["id"],
                    "transformation": fallback["transformation"],
                    "reason": "predeclared-equivalent-expression-selected" if mode == "equivalent" else "predeclared-complete-static-expression-selected",
                }
            elif len(choices) > 1:
                findings.append(_finding("ambiguous-fallback-match", f"Multiple exact {mode} expressions remain at the same policy rank.", identity, "/candidate/fallbacks", targets))
            if selected is not None or len(choices) > 1:
                break
        if selected is not None:
            mappings.append(selected)
            continue
        if any(item.requirement_identity == identity for item in findings):
            continue
        if requirement["mandatory"] is False and requirement["criticality"] == "optional" and requirement["unsupported_allowed"] is True:
            if requirement["capability"] not in declaration.unsupported_capabilities:
                findings.append(_finding("undeclared-unsupported-capability", "Optional unavailability must be explicit in the declaration.", identity, "/declaration/unsupported_capabilities", targets))
            else:
                mappings.append({
                    "requirement_id": identity, "affected_semantic_identities": list(targets),
                    "criticality": "optional", "selected_expression_mode": "unsupported",
                    "capability_id": "", "fallback_id": "", "transformation": "",
                    "reason": "governed-optional-expression-explicitly-unavailable",
                })
            continue
        findings.append(_finding("required-expression-unavailable", "No exact native or authorized complete predeclared expression preserves all required meaning.", identity, "/candidate/renderer_requirements", targets))
    mapped_ids = [item["requirement_id"] for item in mappings]
    expected_ids = [item["id"] for item in requirements]
    if len(mapped_ids) != len(set(mapped_ids)):
        findings.append(_finding("duplicate-requirement-mapping", "A renderer requirement received more than one outcome.", location="/plan/mappings"))
    missing = tuple(identity for identity in expected_ids if identity not in mapped_ids and not any(item.requirement_identity == identity for item in findings))
    if missing:
        findings.append(_finding("unmapped-requirement", "One or more renderer requirements received no outcome.", location="/plan/mappings", refs=missing))
    return mappings, tuple(sorted(set(findings)))


def _capability_record(declaration: RendererCapabilityDeclaration) -> BCRPRecord:
    authority = {"id": _DECLARATION_AUTHORITY_IDENTITY, "owner": declaration.renderer_owner, "role": declaration.renderer_role}
    payload = _declaration_fingerprint_document(declaration) | {
        "declaration_fingerprint": declaration.fingerprint,
        "renderer_authority": authority,
        "fingerprint_algorithm": "sha256",
        "inventory_scope": "complete",
    }
    extension = {
        "owner_namespace": _DECLARATION_EXTENSION_OWNER, "name": _DECLARATION_EXTENSION_NAME,
        "version": _EXTENSION_VERSION, "authority_ref": _DECLARATION_AUTHORITY_IDENTITY,
        "scope": "renderer-capability-declaration", "target_refs": [declaration.identity],
        "criticality": "required", "character": "semantic",
        "validation_contract": CAPABILITY_DECLARATION_CONTRACT, "preservation": "must-preserve",
        "payload": payload,
    }
    return BCRPRecord(
        kind="RendererCapabilityDeclarationRecord", identity=declaration.identity, profile_version=PROFILE_VERSION,
        semantic={
            "renderer_id": declaration.renderer_identity, "renderer_version": declaration.renderer_version,
            "capabilities": [item.identity for item in declaration.capabilities],
            "declaration_identity": declaration.identity,
            "capability_profile_identity": declaration.capability_profile_identity,
            "capability_profile_version": declaration.capability_profile_version,
            "declaration_time": _normal_time(declaration.declaration_time, "declaration time"),
            "inventory_complete": True, "unsupported_capabilities": list(declaration.unsupported_capabilities),
            "declared_constraints": list(declaration.declared_constraints),
            "claim_character": "renderer-owned-claim-not-conformance-proof",
        },
        extensions=[extension],
    )


def _release_payload_bindings(release_record: BCRPRecord) -> tuple[str, dict[str, Any]]:
    """Exact-dispatch legacy v1 versus native v2 Release payload extraction."""
    if len(release_record.extensions) != 1 or type(release_record.extensions[0]) is not dict:
        raise PlanningRejected("Release requires one exact recognized authorization extension.")
    ext = release_record.extensions[0]
    family = tuple(ext.get(k) for k in ("owner_namespace", "name", "version", "validation_contract"))
    payload = ext.get("payload")
    if family == ("briefforge-publication-release", "publication-release-authorization", "1.0.0",
                  "briefforge:publication-release-authorization:1.0.0"):
        value = payload.get("authorized_candidate_semantic_fingerprint") if type(payload) is dict else None
        snapshot = payload.get("authorized_evidence_snapshot") if type(payload) is dict else None
    elif family == ("briefforge-publication-release", "native-publication-release-authorization", "2.0.0",
                    "briefforge:publication-release-authorization:2.0.0"):
        candidate = payload.get("candidate") if type(payload) is dict else None
        value = candidate.get("candidate_semantic_fingerprint") if type(candidate) is dict else None
        snapshot = payload.get("evidence_snapshot") if type(payload) is dict else None
    else:
        raise PlanningRejected("Release authorization extension family/version is unknown or mixed.")
    if type(value) is not str or not _DIGEST_RE.fullmatch(value):
        raise PlanningRejected("Release Candidate fingerprint binding is malformed.")
    if type(snapshot) is not dict or set(snapshot) != {"identity", "version", "inventory_digest"}:
        raise PlanningRejected("Release evidence snapshot binding is malformed.")
    return value, deepcopy(snapshot)


def _plan_record(
    release: VerifiedPublicationRelease,
    declaration: RendererCapabilityDeclaration,
    lifecycle: dict[str, Any],
    authorization: PlanningAuthorization,
    mappings: list[dict[str, Any]],
) -> BCRPRecord:
    bundle = release.bundle
    candidate = bundle.one("CandidatePresentationPackageRecord")
    ready = bundle.one("ReadyPresentationPackageRecord")
    release_record = bundle.one("PublicationReleaseRecord")
    candidate_binding, snapshot_binding = _release_payload_bindings(release_record)
    authority = {
        "id": authorization.authority_identity,
        "owner": authorization.authority_owner,
        "role": authorization.authority_role,
    }
    fallbacks = [item["fallback_id"] for item in mappings if item["fallback_id"]]
    transformations = [item["transformation"] for item in mappings if item["transformation"]]
    payload = {
        "contract_version": _EXTENSION_VERSION,
        "planning_policy": authorization.policy_identity,
        "authorization_identity": authorization.identity,
        "authorization_contract": AUTHORIZATION_CONTRACT,
        "planning_authority": authority,
        "authorization_time": _normal_time(authorization.authorization_time, "authorization time"),
        "plan_identity": authorization.plan_identity,
        "planning_time": _normal_time(authorization.planning_time, "planning time"),
        "release_binding": {
            "identity": release_record.identity, "fingerprint": release.fingerprint.digest,
            "ready_identity": ready.identity,
            "ready_fingerprint": release_record.semantic["ready_fingerprint"],
            "candidate_fingerprint": candidate_binding,
            "publication_identity": release_record.semantic["publication_lineage_id"],
            "publication_version": release_record.semantic["semantic_publication_version"],
            "evidence_snapshot": snapshot_binding,
        },
        "lifecycle_binding": lifecycle,
        "capability_binding": {
            "declaration_identity": declaration.identity,
            "declaration_fingerprint": declaration.fingerprint,
            "capability_profile_identity": declaration.capability_profile_identity,
            "capability_profile_version": declaration.capability_profile_version,
            "renderer_identity": declaration.renderer_identity,
            "renderer_version": declaration.renderer_version,
            "declaration_time": _normal_time(declaration.declaration_time, "declaration time"),
            "inventory_complete": declaration.inventory_complete,
            "complete_capability_inventory": [_claim_document(item) for item in declaration.capabilities],
            "unsupported_capabilities": list(declaration.unsupported_capabilities),
            "declared_constraints": list(declaration.declared_constraints),
        },
        "mappings": deepcopy(mappings),
        "capability_claim_character": "declaration-not-conformance-evidence",
        "plan_character": "expression-plan-not-renderer-output-or-artifact-authority",
        "excluded_authorities": list(_EXCLUDED_AUTHORITIES),
    }
    extension = {
        "owner_namespace": _PLAN_EXTENSION_OWNER, "name": _PLAN_EXTENSION_NAME,
        "version": _EXTENSION_VERSION, "authority_ref": authorization.authority_identity,
        "scope": "renderer-compatibility-plan",
        "target_refs": [authorization.plan_identity, release_record.identity, ready.identity, declaration.identity],
        "criticality": "required", "character": "semantic", "validation_contract": PLAN_CONTRACT,
        "preservation": "must-preserve", "payload": payload,
    }
    return BCRPRecord(
        kind="RendererCompatibilityPlanRecord", identity=authorization.plan_identity, profile_version=PROFILE_VERSION,
        semantic={
            "ready_ref": ready.identity, "renderer_capability_ref": declaration.identity,
            "declared_transformations": transformations, "fallbacks": fallbacks,
            "supported": True, "mode": "requirement-mapped",
        },
        extensions=[extension],
    )


def produce_renderer_compatibility_plan(
    *,
    verified_release: VerifiedPublicationRelease,
    evidence_snapshot: EvidenceSnapshot,
    lifecycle_scope: LifecyclePlanningScope,
    declaration: RendererCapabilityDeclaration | None,
    authorization: PlanningAuthorization,
) -> CompatibilityPlanningResult:
    """Return one verified Plan or complete blocking findings and no Plan."""

    findings: list[PlanningFinding] = []
    try:
        release_copy = deepcopy(verified_release)
        snapshot_copy = deepcopy(evidence_snapshot)
        lifecycle_copy = deepcopy(lifecycle_scope)
        declaration_copy = deepcopy(declaration)
        authorization_copy = deepcopy(authorization)
    except Exception:
        return CompatibilityPlanningResult((_finding("uncopyable-planning-input", "Planning inputs must be safely copyable semantic material."),), None)
    if declaration_copy is None:
        return CompatibilityPlanningResult((_finding("missing-capability-declaration", "One explicit renderer capability declaration is required.", location="/declaration"),), None)
    if type(release_copy) is not VerifiedPublicationRelease:
        findings.append(_finding("missing-verified-release", "An independently verified immutable TASK-050 Release is required.", location="/release"))
        return CompatibilityPlanningResult(tuple(findings), None)
    try:
        reverified = verify_publication_release(
            release_copy.bundle, evidence_snapshot=snapshot_copy,
            expected_release_fingerprint=release_copy.fingerprint.digest,
        )
    except Exception as exc:
        findings.append(_finding("release-reverification-failed", str(exc), location="/release"))
        return CompatibilityPlanningResult(tuple(findings), None)
    release_binding = release_binding_from_verified_release(reverified)
    declaration_findings = _verify_declaration(declaration_copy)
    findings.extend(declaration_findings)
    lifecycle_findings, lifecycle_closure = _verify_lifecycle_scope(lifecycle_copy, release_binding)
    findings.extend(lifecycle_findings)
    if not declaration_findings:
        findings.extend(_verify_authorization(authorization_copy, reverified, declaration_copy))
    candidate = reverified.bundle.one("CandidatePresentationPackageRecord")
    requirements, fallbacks, candidate_findings = _candidate_material(candidate)
    findings.extend(candidate_findings)
    if findings:
        return CompatibilityPlanningResult(tuple(sorted(set(findings))), None)
    mappings, mapping_findings = _plan_requirements(requirements, fallbacks, declaration_copy)
    findings.extend(mapping_findings)
    if findings or lifecycle_closure is None:
        return CompatibilityPlanningResult(tuple(sorted(set(findings))), None)
    capability_record = _capability_record(declaration_copy)
    plan_record = _plan_record(reverified, declaration_copy, lifecycle_closure, authorization_copy, mappings)
    output = BCRPBundle(PROFILE_ID, PROFILE_VERSION, tuple(deepcopy(reverified.bundle.records)) + (capability_record, plan_record))
    if len(output.records_of_kind("RendererCompatibilityPlanRecord")) != 1:
        return CompatibilityPlanningResult((_finding("plan-cardinality", "Successful planning must create exactly one Plan record."),), None)
    generic = validate_bundle(output, through_layer="L5")
    specialized_extension_records = {
        output.one("ValidationJudgmentRecord").identity,
        output.one("ReadyPresentationPackageRecord").identity,
        output.one("PublicationReleaseRecord").identity,
        capability_record.identity,
        plan_record.identity,
    }
    release_extension = output.one("PublicationReleaseRecord").extensions[0]
    release_family = tuple(release_extension.get(key) for key in (
        "owner_namespace", "name", "version", "validation_contract"))
    native_release_family = (
        "briefforge-publication-release", "native-publication-release-authorization", "2.0.0",
        "briefforge:publication-release-authorization:2.0.0")
    expected_native_absent = set()
    if release_family == native_release_family:
        native_refs = (
            (output.one("ValidationJudgmentRecord").identity,
             "authority:briefforge-publication-judgment"),
            (output.one("ReadyPresentationPackageRecord").identity,
             "authority:briefforge-publication-readiness"),
            (output.one("PublicationReleaseRecord").identity, evidence_snapshot.identity),
        )
        expected_native_absent = {
            (layer, identity, identity,
             f"{prefix} reference targets absent identity '{reference}'.")
            for layer, prefix in (("L1", "Canonical"), ("L2", "Semantic"))
            for identity, reference in native_refs
        }
    observed_native_absent = {
        (item.layer, item.semantic_identity, item.location, item.message)
        for item in generic.findings
        if (item.family == "identity-or-reference-integrity" and
            (item.layer, item.semantic_identity, item.location, item.message)
            in expected_native_absent)
    }
    unexpected = [
        item for item in generic.findings
        if not (item.family == "extension-boundary" and item.semantic_identity in specialized_extension_records)
        and (item.layer, item.semantic_identity, item.location, item.message)
            not in expected_native_absent
    ]
    if unexpected or observed_native_absent != expected_native_absent:
        failures = unexpected or [type("Finding", (), {
            "message": "Native Plan predecessor authority-reference reconciliation was incomplete.",
            "semantic_identity": plan_record.identity, "location": plan_record.identity,
            "referenced_identities": ()})()]
        return CompatibilityPlanningResult(tuple(_finding("generic-plan-validation-failed", item.message, item.semantic_identity, item.location, item.referenced_identities) for item in failures), None)
    fingerprint = fingerprint_bundle(output, domain="profile-instance", require_valid=False)
    verified = VerifiedRendererCompatibilityPlan(
        _serialize_bundle(output), fingerprint,
        json.dumps(mappings, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False),
    )
    return CompatibilityPlanningResult((), verified)


def verify_renderer_compatibility_plan(
    bundle: BCRPBundle,
    *,
    evidence_snapshot: EvidenceSnapshot,
    lifecycle_scope: LifecyclePlanningScope,
    declaration: RendererCapabilityDeclaration,
    authorization: PlanningAuthorization,
    expected_plan_fingerprint: str | None = None,
) -> VerifiedRendererCompatibilityPlan:
    """Independently reproduce and compare one persisted eight-record Plan closure."""

    if type(bundle) is not BCRPBundle:
        raise PlanningRejected("Persisted Plan input must be an exact BCRPBundle.")
    try:
        persisted = deepcopy(bundle)
    except Exception as exc:
        raise PlanningRejected("Persisted Plan bundle must be safely copyable.") from exc
    if type(persisted.records) is not tuple or not all(type(record) is BCRPRecord for record in persisted.records):
        raise PlanningRejected("Persisted Plan record inventory must be one exact immutable tuple of BCRP records.")
    expected_kinds = (
        "PresentationBriefRecord", "PortablePresentationMaterialRecord", "CandidatePresentationPackageRecord",
        "ValidationJudgmentRecord", "ReadyPresentationPackageRecord", "PublicationReleaseRecord",
        "RendererCapabilityDeclarationRecord", "RendererCompatibilityPlanRecord",
    )
    if len(persisted.records) != len(expected_kinds) or any(len(persisted.records_of_kind(kind)) != 1 for kind in expected_kinds):
        raise PlanningRejected("Persisted Plan closure requires exactly one each of the six Release records, capability declaration, and Plan.")
    if any(record.kind not in expected_kinds for record in persisted.records):
        raise PlanningRejected("Persisted Plan closure contains downstream or unknown record kinds.")
    release_bundle = BCRPBundle(
        persisted.profile_identity, persisted.profile_version,
        tuple(deepcopy(record) for record in persisted.records if record.kind not in {
            "RendererCapabilityDeclarationRecord", "RendererCompatibilityPlanRecord"
        }),
    )
    try:
        release_verified = verify_publication_release(release_bundle, evidence_snapshot=evidence_snapshot)
    except Exception as exc:
        raise PlanningRejected("Persisted Plan Release closure failed independent reverification.") from exc
    reproduced = produce_renderer_compatibility_plan(
        verified_release=release_verified, evidence_snapshot=evidence_snapshot,
        lifecycle_scope=lifecycle_scope, declaration=declaration, authorization=authorization,
    )
    if reproduced.blocked or reproduced.plan is None:
        codes = ", ".join(sorted({item.code for item in reproduced.findings}))
        raise PlanningRejected(f"Persisted Plan inputs are blocked or stale: {codes}")
    if _serialize_bundle(persisted) != _serialize_bundle(reproduced.plan.bundle):
        raise PlanningRejected("Persisted Plan content differs from independently reproduced authorized content.")
    fingerprint = fingerprint_bundle(persisted, domain="profile-instance", require_valid=False)
    if fingerprint != reproduced.plan.fingerprint:
        raise PlanningRejected("Persisted Plan closure fingerprint does not match independently reproduced content.")
    if expected_plan_fingerprint is not None and fingerprint.digest != expected_plan_fingerprint:
        raise PlanningRejected("Persisted Plan fingerprint differs from the exact expected fingerprint.")
    return VerifiedRendererCompatibilityPlan(
        _serialize_bundle(persisted), fingerprint, reproduced.plan.mappings_document,
    )


def _serialize_bundle(bundle: BCRPBundle) -> str:
    document = {
        "profile_identity": bundle.profile_identity,
        "profile_version": bundle.profile_version,
        "records": [record.to_document() for record in bundle.records],
    }
    return json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _deserialize_bundle(document_text: str) -> BCRPBundle:
    try:
        document = json.loads(document_text)
    except (TypeError, ValueError) as exc:
        raise PlanningRejected("Stored Plan closure is not valid deterministic JSON.") from exc
    if not isinstance(document, dict) or set(document) != {"profile_identity", "profile_version", "records"}:
        raise PlanningRejected("Stored Plan closure envelope is malformed.")
    records = document["records"]
    if not isinstance(records, list):
        raise PlanningRejected("Stored Plan closure records must be a list.")
    return BCRPBundle(
        document["profile_identity"], document["profile_version"],
        tuple(BCRPRecord.from_document(item) for item in records),
    )


# This family is additive: all historical v1 declarations and planning APIs
# above remain unchanged, and no v1 value is coerced into generation 8.
CAPABILITY_V2_CONTRACT = "briefforge:renderer-capability-declaration:2.0.0"
CAPABILITY_V2_PROFILE = (
    "briefforge:representative-paired-terminal-static-html-profile", "3.0.0")
CAPABILITY_V2_MAPPING_CONTRACT = "briefforge:paired-row-relationship-static-table:1.0.0"
_CAPABILITY_V2_FAMILY = (
    "briefforge-renderer-capability", "renderer-capability-declaration", "2.0.0",
    CAPABILITY_V2_CONTRACT)
_CAPABILITY_V1_FAMILY = (
    _DECLARATION_EXTENSION_OWNER, _DECLARATION_EXTENSION_NAME, _EXTENSION_VERSION,
    CAPABILITY_DECLARATION_CONTRACT)
_CAPABILITY_V2_SEMANTIC_KEYS = {
    "renderer_id", "renderer_version", "capabilities", "declaration_identity",
    "capability_profile_identity", "capability_profile_version", "declaration_time",
    "inventory_complete", "unsupported_capabilities", "declared_constraints", "claim_character"}
_CAPABILITY_V2_PAYLOAD_KEYS = {
    "contract", "declaration_identity", "renderer_identity", "implementation_identity",
    "implementation_digest", "owner_identity", "owner_role", "profile", "media_types",
    "output_count", "asset_count", "table_count", "column_count", "mapping_capability",
    "semantic_digest", "operation_identity", "authorization_fingerprint", "storage_identity",
    "issued_at_utc", "fingerprint"}
_CAPABILITY_V2_CAPABILITIES = (
    "renderer", "media-type", "output-count", "asset-count", "table-count", "column-count",
    "paired-row-mapping")
_CAPABILITY_V2_MAX_BYTES = 65536


class CapabilityV2Rejected(PlanningRejected):
    """A generation-8 Capability-v2 value failed independent admission."""


@dataclass(frozen=True)
class CapabilityV2IssuerInputs:
    """Issuer-held facts; no member is recovered from submitted record bytes."""
    declaration_identity: str
    renderer_identity: str
    renderer_version: str
    implementation_identity: str
    implementation_digest: str
    owner_identity: str
    owner_role: str
    media_types: tuple[str, ...]
    output_count: int
    asset_count: int
    table_count: int
    column_count: int
    declared_constraints: tuple[str, ...]
    unsupported_capabilities: tuple[str, ...]
    operation_identity: str
    authorization_fingerprint: str
    storage_identity: str
    issued_at_utc: str


@dataclass(frozen=True, eq=False)
class VerifiedRendererCapabilityV2:
    _record_document: bytes
    _bundle_document: bytes
    fingerprint: str
    bundle_fingerprint: Fingerprint

    @property
    def record(self) -> BCRPRecord:
        return _capability_v2_record_from_bytes(self._record_document)

    @property
    def bundle(self) -> BCRPBundle:
        return _capability_v2_bundle_from_bytes(self._bundle_document)


@dataclass(frozen=True, eq=False)
class PersistedRendererCapabilityV2:
    path: Path
    sha256: str
    length: int
    fingerprint: str
    bundle_fingerprint: str


def _capability_v2_identity(value: Any, label: str) -> str:
    if type(value) is not str or not _IDENTITY_RE.fullmatch(value):
        raise CapabilityV2Rejected(f"Capability-v2 {label} is not a canonical identity.")
    return value


def _capability_v2_digest(value: Any, label: str) -> str:
    if type(value) is not str or not _DIGEST_RE.fullmatch(value):
        raise CapabilityV2Rejected(f"Capability-v2 {label} is not lowercase SHA-256.")
    return value


def _capability_v2_strings(value: Any, label: str, *, nonempty: bool = False) -> tuple[str, ...]:
    if type(value) is not tuple or not all(type(item) is str and item for item in value):
        raise CapabilityV2Rejected(f"Capability-v2 {label} must be an exact immutable inventory.")
    if nonempty and not value:
        raise CapabilityV2Rejected(f"Capability-v2 {label} cannot be empty.")
    if len(set(value)) != len(value):
        raise CapabilityV2Rejected(f"Capability-v2 {label} contains duplicates.")
    return value


def _capability_v2_time(value: Any) -> str:
    if type(value) is not str or not re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value):
        raise CapabilityV2Rejected("Capability-v2 issuance time must be whole-second UTC.")
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise CapabilityV2Rejected("Capability-v2 issuance time is not a real UTC instant.") from exc
    return value


def _verify_capability_v2_issuer_inputs(value: Any) -> CapabilityV2IssuerInputs:
    if type(value) is not CapabilityV2IssuerInputs:
        raise CapabilityV2Rejected("Exact independent Capability-v2 issuer inputs are required.")
    for item, label in (
        (value.declaration_identity, "declaration identity"),
        (value.renderer_identity, "renderer identity"),
        (value.implementation_identity, "implementation identity"),
        (value.owner_identity, "owner identity"),
        (value.operation_identity, "operation identity"),
        (value.storage_identity, "storage identity")):
        _capability_v2_identity(item, label)
    _capability_v2_digest(value.implementation_digest, "implementation digest")
    _capability_v2_digest(value.authorization_fingerprint, "authorization fingerprint")
    if value.owner_identity != ACCEPTED_RENDERER_OWNER or value.owner_role != ACCEPTED_RENDERER_ROLE:
        raise CapabilityV2Rejected("Capability-v2 renderer owner or role is not accepted.")
    if type(value.renderer_version) is not str or not _SEMVER_RE.fullmatch(value.renderer_version):
        raise CapabilityV2Rejected("Capability-v2 renderer version must be SemVer.")
    _capability_v2_strings(value.media_types, "media types", nonempty=True)
    _capability_v2_strings(value.declared_constraints, "declared constraints")
    _capability_v2_strings(value.unsupported_capabilities, "unsupported capabilities")
    for label in ("output_count", "asset_count", "table_count", "column_count"):
        count = getattr(value, label)
        if type(count) is not int or count < 0:
            raise CapabilityV2Rejected(f"Capability-v2 {label} must be a nonnegative integer.")
    _capability_v2_time(value.issued_at_utc)
    return value


def capability_declaration_family(record: BCRPRecord) -> str:
    """Exact closed dispatch for historical v1 and generation-8 v2."""
    if type(record) is not BCRPRecord or record.kind != "RendererCapabilityDeclarationRecord":
        raise CapabilityV2Rejected("Capability dispatch requires the exact BCRP record kind.")
    if type(record.extensions) is not list or len(record.extensions) != 1 or type(record.extensions[0]) is not dict:
        raise CapabilityV2Rejected("Capability dispatch requires exactly one extension.")
    extension = record.extensions[0]
    family = tuple(extension.get(key) for key in (
        "owner_namespace", "name", "version", "validation_contract"))
    if family == _CAPABILITY_V1_FAMILY:
        return "v1"
    if family == _CAPABILITY_V2_FAMILY:
        return "v2"
    raise CapabilityV2Rejected("Capability extension family is unknown or mixed.")


def _construct_capability_v2_record(issuer: CapabilityV2IssuerInputs) -> BCRPRecord:
    semantic = {
        "renderer_id": issuer.renderer_identity, "renderer_version": issuer.renderer_version,
        "capabilities": list(_CAPABILITY_V2_CAPABILITIES),
        "declaration_identity": issuer.declaration_identity,
        "capability_profile_identity": ACCEPTED_DECLARATION_PROFILE_ID,
        "capability_profile_version": "2.0.0", "declaration_time": issuer.issued_at_utc,
        "inventory_complete": True, "unsupported_capabilities": list(issuer.unsupported_capabilities),
        "declared_constraints": list(issuer.declared_constraints),
        "claim_character": "renderer-owned-claim-not-conformance-proof"}
    payload = {
        "contract": CAPABILITY_V2_CONTRACT, "declaration_identity": issuer.declaration_identity,
        "renderer_identity": issuer.renderer_identity,
        "implementation_identity": issuer.implementation_identity,
        "implementation_digest": issuer.implementation_digest,
        "owner_identity": issuer.owner_identity, "owner_role": issuer.owner_role,
        "profile": list(CAPABILITY_V2_PROFILE), "media_types": list(issuer.media_types),
        "output_count": issuer.output_count, "asset_count": issuer.asset_count,
        "table_count": issuer.table_count, "column_count": issuer.column_count,
        "mapping_capability": {"contract": CAPABILITY_V2_MAPPING_CONTRACT,
            "profiles": [list(CAPABILITY_V2_PROFILE)], "mode": "static"},
        "semantic_digest": domain_digest(
            "briefforge.task076.capability-core-semantic.v1", semantic),
        "operation_identity": issuer.operation_identity,
        "authorization_fingerprint": issuer.authorization_fingerprint,
        "storage_identity": issuer.storage_identity, "issued_at_utc": issuer.issued_at_utc}
    payload["fingerprint"] = domain_digest(
        "briefforge.task075.capability-declaration.v2", payload)
    extension = {
        "owner_namespace": _CAPABILITY_V2_FAMILY[0], "name": _CAPABILITY_V2_FAMILY[1],
        "version": "2.0.0", "authority_ref": _DECLARATION_AUTHORITY_IDENTITY,
        "scope": "renderer-capability-declaration", "target_refs": [issuer.declaration_identity],
        "criticality": "required", "character": "semantic",
        "validation_contract": CAPABILITY_V2_CONTRACT, "preservation": "must-preserve",
        "payload": payload}
    return BCRPRecord("RendererCapabilityDeclarationRecord", issuer.declaration_identity,
                      PROFILE_VERSION, semantic, [extension])


def _capability_v2_predecessors(candidate: Any, envelope: Any
        ) -> tuple[AuthenticatedGeneration8Candidate, DerivationEvidenceEnvelopeV2]:
    try:
        authenticated = authenticate_generation8_candidate(candidate)
        verified = verify_derivation_evidence_envelope_v2(envelope, candidate=authenticated)
    except Exception as exc:
        raise CapabilityV2Rejected(
            "Capability-v2 requires the authenticated generation-8 Candidate and envelope.") from exc
    if tuple(verified["paired_profile"]) != CAPABILITY_V2_PROFILE:
        raise CapabilityV2Rejected("Capability-v2 predecessor profile is not paired-v3.")
    return authenticated, verified


def _verified_capability_v2(record: BCRPRecord,
        candidate: AuthenticatedGeneration8Candidate,
        evidence: DerivationEvidenceEnvelopeV2) -> VerifiedRendererCapabilityV2:
    record_bytes = canonical_json(record.to_document())
    bundle = BCRPBundle(PROFILE_ID, PROFILE_VERSION, (deepcopy(record),))
    bundle_bytes = canonical_json({"profile_identity": PROFILE_ID, "profile_version": PROFILE_VERSION,
                                   "records": [record.to_document()]})
    created = VerifiedRendererCapabilityV2(
        record_bytes, bundle_bytes, record.extensions[0]["payload"]["fingerprint"],
        fingerprint_bundle(bundle, domain="profile-instance", require_valid=False))
    return created


def construct_renderer_capability_v2(*, candidate: AuthenticatedGeneration8Candidate,
        derivation_evidence: DerivationEvidenceEnvelopeV2, issuer_inputs: CapabilityV2IssuerInputs
        ) -> VerifiedRendererCapabilityV2:
    """Construct one canonical declaration from predecessor and issuer authorities."""
    authenticated, evidence = _capability_v2_predecessors(candidate, derivation_evidence)
    issuer = _verify_capability_v2_issuer_inputs(issuer_inputs)
    return _verified_capability_v2(
        _construct_capability_v2_record(issuer), authenticated, evidence)


def _unique_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError("duplicate JSON key")
        output[key] = value
    return output


def _capability_v2_record_from_bytes(data: bytes) -> BCRPRecord:
    if type(data) is not bytes or len(data) > _CAPABILITY_V2_MAX_BYTES:
        raise CapabilityV2Rejected("Capability-v2 record bytes are not bounded.")
    try:
        document = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_json_pairs,
                              parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)))
        if canonical_json(document) != data:
            raise ValueError("noncanonical")
        return BCRPRecord.from_document(document)
    except Exception as exc:
        raise CapabilityV2Rejected("Capability-v2 record is not exact canonical BCRP JSON.") from exc


def _capability_v2_bundle_from_bytes(data: bytes) -> BCRPBundle:
    if type(data) is not bytes or len(data) > _CAPABILITY_V2_MAX_BYTES:
        raise CapabilityV2Rejected("Capability-v2 bundle bytes are not bounded.")
    try:
        document = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_json_pairs,
                              parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)))
        if canonical_json(document) != data or type(document) is not dict or set(document) != {
                "profile_identity", "profile_version", "records"}:
            raise ValueError("noncanonical or malformed")
        if document["profile_identity"] != PROFILE_ID or document["profile_version"] != PROFILE_VERSION:
            raise ValueError("foreign profile")
        if type(document["records"]) is not list or len(document["records"]) != 1:
            raise ValueError("record cardinality")
        return BCRPBundle(PROFILE_ID, PROFILE_VERSION,
                          (BCRPRecord.from_document(document["records"][0]),))
    except Exception as exc:
        raise CapabilityV2Rejected("Capability-v2 bundle is not one canonical BCRP closure.") from exc


def verify_renderer_capability_v2(value: Any, *, candidate: AuthenticatedGeneration8Candidate,
        derivation_evidence: DerivationEvidenceEnvelopeV2, issuer_inputs: CapabilityV2IssuerInputs,
        expected_fingerprint: str | None = None,
        expected_bundle_fingerprint: str | None = None
        ) -> VerifiedRendererCapabilityV2:
    """Verify data-only Capability-v2 evidence against independently derived bytes."""
    authenticated, evidence = _capability_v2_predecessors(candidate, derivation_evidence)
    issuer = _verify_capability_v2_issuer_inputs(issuer_inputs)
    if type(value) is VerifiedRendererCapabilityV2:
        record = _capability_v2_record_from_bytes(value._record_document)
        bundle = _capability_v2_bundle_from_bytes(value._bundle_document)
        if canonical_json(bundle.records[0].to_document()) != value._record_document:
            raise CapabilityV2Rejected("Capability-v2 record and bundle differ.")
    elif type(value) is BCRPRecord:
        record = deepcopy(value)
    elif type(value) is BCRPBundle:
        if (value.profile_identity != PROFILE_ID or value.profile_version != PROFILE_VERSION
                or type(value.records) is not tuple or len(value.records) != 1
                or type(value.records[0]) is not BCRPRecord):
            raise CapabilityV2Rejected("Capability-v2 bundle requires one exact record.")
        record = deepcopy(value.records[0])
    elif type(value) is bytes:
        try:
            probe = json.loads(value.decode("utf-8"), object_pairs_hook=_unique_json_pairs)
        except Exception as exc:
            raise CapabilityV2Rejected("Capability-v2 bytes are malformed.") from exc
        if type(probe) is dict and "record_kind" in probe:
            record = _capability_v2_record_from_bytes(value)
        elif type(probe) is dict and set(probe) == {"profile_identity", "profile_version", "records"}:
            record = _capability_v2_bundle_from_bytes(value).records[0]
        else:
            raise CapabilityV2Rejected("Capability-v2 byte family is unknown or mixed.")
    else:
        raise CapabilityV2Rejected("Capability-v2 requires exact record, bundle, bytes, or verified value.")
    if capability_declaration_family(record) != "v2":
        raise CapabilityV2Rejected("Historical Capability-v1 cannot satisfy Capability-v2.")
    extension = record.extensions[0]
    if set(record.semantic) != _CAPABILITY_V2_SEMANTIC_KEYS or set(extension) != _EXTENSION_KEYS:
        raise CapabilityV2Rejected("Capability-v2 record or extension is not closed.")
    payload = extension.get("payload")
    if type(payload) is not dict or set(payload) != _CAPABILITY_V2_PAYLOAD_KEYS:
        raise CapabilityV2Rejected("Capability-v2 payload is not closed.")
    unsigned = {key: deepcopy(item) for key, item in payload.items() if key != "fingerprint"}
    try:
        if payload["semantic_digest"] != domain_digest(
                "briefforge.task076.capability-core-semantic.v1", record.semantic):
            raise CapabilityV2Rejected("Capability-v2 semantic digest differs.")
        if payload["fingerprint"] != domain_digest(
                "briefforge.task075.capability-declaration.v2", unsigned):
            raise CapabilityV2Rejected("Capability-v2 outer payload fingerprint differs.")
        if not (record.identity == record.semantic["declaration_identity"]
                == payload["declaration_identity"] == extension["target_refs"][0]
                and record.semantic["renderer_id"] == payload["renderer_identity"]
                and record.semantic["declaration_time"] == payload["issued_at_utc"]):
            raise CapabilityV2Rejected("Capability-v2 cross-layer bindings differ.")
    except CapabilityV2Rejected:
        raise
    except (IndexError, KeyError, TypeError, ValueError) as exc:
        raise CapabilityV2Rejected("Capability-v2 semantic commitments are malformed.") from exc
    expected = _construct_capability_v2_record(issuer)
    if canonical_json(record.to_document()) != canonical_json(expected.to_document()):
        raise CapabilityV2Rejected("Capability-v2 differs from independently reconstructed issuer content.")
    verified = _verified_capability_v2(record, authenticated, evidence)
    if expected_fingerprint is not None and verified.fingerprint != expected_fingerprint:
        raise CapabilityV2Rejected("Capability-v2 fingerprint differs from expected authority.")
    if (expected_bundle_fingerprint is not None
            and verified.bundle_fingerprint.digest != expected_bundle_fingerprint):
        raise CapabilityV2Rejected("Capability-v2 bundle fingerprint differs from expected authority.")
    return verified


def serialize_renderer_capability_v2(value: Any, **authority: Any) -> bytes:
    """Canonical BCRP record serialization after independent admission."""
    return verify_renderer_capability_v2(value, **authority)._record_document


def serialize_renderer_capability_v2_bundle(value: Any, **authority: Any) -> bytes:
    """Canonical singleton BCRP bundle serialization after independent admission."""
    return verify_renderer_capability_v2(value, **authority)._bundle_document


def _capability_v2_safe_name(filename: str) -> None:
    if (type(filename) is not str or not filename or filename in {".", ".."}
            or Path(filename).name != filename or Path(filename).is_absolute() or "\x00" in filename):
        raise CapabilityV2Rejected("Capability-v2 persistence filename must be one safe basename.")


def _capability_v2_open_directory(directory: Path) -> int:
    if not isinstance(directory, Path) or not directory.is_absolute():
        raise CapabilityV2Rejected("Capability-v2 persistence directory must be absolute.")
    descriptor = -1
    try:
        expected = os.stat(directory, follow_symlinks=False)
        if directory.resolve(strict=True) != directory or not stat.S_ISDIR(expected.st_mode):
            raise CapabilityV2Rejected("Capability-v2 persistence directory is noncanonical or unsafe.")
        descriptor = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                             | getattr(os, "O_NOFOLLOW", 0))
        actual = os.fstat(descriptor)
        if (actual.st_dev, actual.st_ino) != (expected.st_dev, expected.st_ino):
            raise CapabilityV2Rejected("Capability-v2 persistence directory changed while opening.")
        opened = descriptor
        descriptor = -1
        return opened
    except CapabilityV2Rejected:
        raise
    except (OSError, RuntimeError) as exc:
        raise CapabilityV2Rejected("Capability-v2 persistence directory is unavailable.") from exc
    finally:
        if descriptor >= 0:
            try:
                os.close(descriptor)
            except OSError:
                pass


def _capability_v2_read(directory_fd: int, filename: str, *,
                        max_bytes: int = _CAPABILITY_V2_MAX_BYTES) -> tuple[bytes, tuple[int, int]]:
    try:
        descriptor = os.open(
            filename,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory_fd,
        )
    except OSError as exc:
        raise CapabilityV2Rejected(
            "Persisted Capability-v2 path is absent, substituted, or unsafe."
        ) from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > max_bytes:
            raise CapabilityV2Rejected("Persisted Capability-v2 is not a bounded regular file.")
        data = bytearray()
        while len(data) < before.st_size:
            part = os.read(descriptor, before.st_size - len(data))
            if not part:
                raise CapabilityV2Rejected("Persisted Capability-v2 was truncated.")
            data.extend(part)
        if os.read(descriptor, 1):
            raise CapabilityV2Rejected("Persisted Capability-v2 grew while reading.")
        after = os.fstat(descriptor)
        if (before.st_dev, before.st_ino, before.st_size) != (after.st_dev, after.st_ino, after.st_size):
            raise CapabilityV2Rejected("Persisted Capability-v2 changed while reading.")
        return bytes(data), (after.st_dev, after.st_ino)
    finally:
        os.close(descriptor)


def persist_renderer_capability_v2(value: Any, *, directory: Path,
        filename: str = "renderer-capability-v2.json", **verification: Any
        ) -> PersistedRendererCapabilityV2:
    """Persist verified serialized evidence without creating live authority."""
    verified = verify_renderer_capability_v2(value, **verification)
    data = verified._bundle_document
    _capability_v2_safe_name(filename)
    directory_fd = _capability_v2_open_directory(directory)
    descriptor = -1
    owned: tuple[int, int] | None = None
    success = False
    try:
        if os.listdir(directory_fd):
            raise CapabilityV2Rejected("Capability-v2 persistence directory must be empty.")
        descriptor = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                             | getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=directory_fd)
        state = os.fstat(descriptor)
        owned = (state.st_dev, state.st_ino)
        view = memoryview(data)
        while view:
            count = os.write(descriptor, view)
            if count <= 0:
                raise OSError("short write")
            view = view[count:]
        os.fsync(descriptor)
        final = os.fstat(descriptor)
        if (not stat.S_ISREG(final.st_mode) or final.st_size != len(data)
                or (final.st_dev, final.st_ino) != owned):
            raise CapabilityV2Rejected("Capability-v2 persistence write is incomplete.")
        os.close(descriptor)
        descriptor = -1
        os.fsync(directory_fd)
        if set(os.listdir(directory_fd)) != {filename}:
            raise CapabilityV2Rejected("Capability-v2 persistence inventory differs.")
        reread, identity = _capability_v2_read(directory_fd, filename)
        again, identity_again = _capability_v2_read(directory_fd, filename)
        if reread != data or again != data or identity != owned or identity_again != owned:
            raise CapabilityV2Rejected("Capability-v2 persisted reread differs.")
        success = True
        return PersistedRendererCapabilityV2(
            directory / filename, hashlib.sha256(data).hexdigest(), len(data),
            verified.fingerprint, verified.bundle_fingerprint.digest)
    except FileExistsError as exc:
        raise CapabilityV2Rejected("Capability-v2 persistence is exclusive-create.") from exc
    except OSError as exc:
        raise CapabilityV2Rejected(f"Cannot safely persist Capability-v2: {exc}") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if not success and owned is not None:
            try:
                current = os.stat(filename, dir_fd=directory_fd, follow_symlinks=False)
                if (current.st_dev, current.st_ino) == owned:
                    os.unlink(filename, dir_fd=directory_fd)
                    os.fsync(directory_fd)
            except FileNotFoundError:
                pass
        os.close(directory_fd)


def reload_renderer_capability_v2(path: Path, *,
        persistence_receipt: PersistedRendererCapabilityV2,
        expected_sha256: str | None = None,
        expected_fingerprint: str | None = None, expected_bundle_fingerprint: str | None = None,
        **verification: Any) -> VerifiedRendererCapabilityV2:
    """Reload and verify data-only evidence; never mint or restore live authority."""
    if type(persistence_receipt) is not PersistedRendererCapabilityV2:
        raise CapabilityV2Rejected("Exact persistence evidence shape is required.")
    if persistence_receipt.path != path:
        raise CapabilityV2Rejected("Capability-v2 persistence evidence path differs.")
    if not isinstance(path, Path) or not path.is_absolute():
        raise CapabilityV2Rejected("Capability-v2 reload path must be absolute.")
    _capability_v2_safe_name(path.name)
    directory_fd = _capability_v2_open_directory(path.parent)
    try:
        if set(os.listdir(directory_fd)) != {path.name}:
            raise CapabilityV2Rejected("Capability-v2 persisted inventory differs.")
        data, identity = _capability_v2_read(directory_fd, path.name)
        if expected_sha256 is not None and hashlib.sha256(data).hexdigest() != expected_sha256:
            raise CapabilityV2Rejected("Capability-v2 persisted byte digest differs.")
        if (hashlib.sha256(data).hexdigest() != persistence_receipt.sha256
                or len(data) != persistence_receipt.length):
            raise CapabilityV2Rejected("Capability-v2 persistence receipt differs from exact bytes.")
        verified = verify_renderer_capability_v2(
            data, expected_fingerprint=expected_fingerprint,
            expected_bundle_fingerprint=expected_bundle_fingerprint,
            **verification)
        if verified.fingerprint != persistence_receipt.fingerprint:
            raise CapabilityV2Rejected(
                "Capability-v2 persistence receipt fingerprint differs from canonical record."
            )
        if verified.bundle_fingerprint.digest != persistence_receipt.bundle_fingerprint:
            raise CapabilityV2Rejected(
                "Capability-v2 persistence receipt bundle fingerprint differs from canonical bundle."
            )
        again, identity_again = _capability_v2_read(directory_fd, path.name)
        if again != data or identity_again != identity or set(os.listdir(directory_fd)) != {path.name}:
            raise CapabilityV2Rejected("Capability-v2 changed during immutable reload.")
        return verified
    finally:
        os.close(directory_fd)


# Additive Plan-v2 production remains in the sole compatibility-planner owner.
# Frozen TASK-076 bytes are never read by these constructors or verifiers.
PLAN_V2_CONTRACT = "briefforge:renderer-compatibility-plan:2.0.0"
PLAN_V2_COMPLETENESS_CONTRACT = "briefforge:planning-completeness-evidence:1.0.0"
_PLAN_V2_FAMILY = (_PLAN_EXTENSION_OWNER, _PLAN_EXTENSION_NAME, "2.0.0", PLAN_V2_CONTRACT)
_PLAN_V2_MAX_BYTES = 4 * 1024 * 1024
_PLAN_V2_REQUIRED_KINDS = (
    "PresentationBriefRecord", "PortablePresentationMaterialRecord",
    "CandidatePresentationPackageRecord", "ValidationJudgmentRecord",
    "ReadyPresentationPackageRecord", "PublicationReleaseRecord",
    "RendererCapabilityDeclarationRecord", "RendererCompatibilityPlanRecord")
_PLAN_V2_SEMANTIC_KEYS = {
    "ready_ref", "renderer_capability_ref", "declared_transformations", "fallbacks",
    "supported", "mode"}
_PLAN_V2_PAYLOAD_KEYS = {
    "contract", "plan_identity", "candidate_profile_instance_fingerprint",
    "judgment_fingerprint", "ready_fingerprint", "release_identity", "release_fingerprint",
    "release_closure_digest", "capability_identity", "capability_fingerprint",
    "capability_contract", "resolver", "derivation", "derivation_evidence_fingerprint",
    "core_graph_digest", "paired_graph_digest", "counterpart_proof_digest",
    "effective_graph_digest", "paired_closure_digest", "requirement_inventory_digest",
    "mapping_inventory_digest", "requirement_outcomes_digest", "mapping_outcomes_digest",
    "requirement_outcomes", "mapping_outcomes", "planning_completeness_digest", "mode",
    "supported", "findings", "operation_identity", "authorization_fingerprint",
    "semantic_digest", "fingerprint"}


class PlanV2Rejected(PlanningRejected):
    """Plan-v2 construction or independent admission failed closed."""

    def __init__(self, message: str, *, code: str = "PLAN_V2_REJECTED",
                 owner: str = "renderer-compatibility-planning-v2",
                 location: str = "plan-v2", reason: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.owner = owner
        self.location = location
        self.reason = reason if reason is not None else message


@dataclass(frozen=True)
class PlanV2IssuerInputs:
    plan_identity: str
    operation_identity: str
    authorization_fingerprint: str


@dataclass(frozen=True)
class VerifiedRendererCompatibilityPlanV2:
    _bundle_document: bytes
    _completeness_document: bytes
    fingerprint: Fingerprint
    extension_fingerprint: str
    bundle_sha256: str
    @property
    def bundle(self) -> BCRPBundle: return _plan_v2_bundle_from_bytes(self._bundle_document)
    @property
    def plan(self) -> BCRPRecord: return self.bundle.one("RendererCompatibilityPlanRecord")
    @property
    def completeness(self) -> dict[str, Any]: return deepcopy(json.loads(self._completeness_document))
    @property
    def requirement_outcomes(self) -> tuple[tuple[Any, ...], ...]:
        return tuple(tuple(x) for x in self.plan.extensions[0]["payload"]["requirement_outcomes"])
    @property
    def mapping_outcomes(self) -> tuple[tuple[Any, ...], ...]:
        return tuple(tuple(x) for x in self.plan.extensions[0]["payload"]["mapping_outcomes"])


@dataclass(frozen=True)
class PersistedRendererCompatibilityPlanV2:
    path: Path
    sha256: str
    length: int
    extension_fingerprint: str
    bundle_fingerprint: str
    device: int
    inode: int


def plan_record_family(record: BCRPRecord) -> str:
    if type(record) is not BCRPRecord or record.kind != "RendererCompatibilityPlanRecord":
        raise PlanV2Rejected("Plan dispatch requires the exact Plan record kind.")
    if type(record.extensions) is not list or len(record.extensions) != 1 or type(record.extensions[0]) is not dict:
        raise PlanV2Rejected("Plan dispatch requires exactly one extension.")
    ext = record.extensions[0]
    family = tuple(ext.get(k) for k in ("owner_namespace", "name", "version", "validation_contract"))
    if family == (_PLAN_EXTENSION_OWNER, _PLAN_EXTENSION_NAME, _EXTENSION_VERSION, PLAN_CONTRACT): return "v1"
    if family == _PLAN_V2_FAMILY: return "v2"
    raise PlanV2Rejected("Plan extension family is unknown or mixed.")


def _verify_plan_v2_issuer(value: Any) -> PlanV2IssuerInputs:
    if type(value) is not PlanV2IssuerInputs: raise PlanV2Rejected("Exact Plan-v2 issuer inputs are required.")
    _capability_v2_identity(value.plan_identity, "Plan identity")
    _capability_v2_identity(value.operation_identity, "operation identity")
    _capability_v2_digest(value.authorization_fingerprint, "authorization fingerprint")
    return value


def _plan_v2_predecessors(candidate: Any, envelope: Any) -> tuple[
        AuthenticatedGeneration8Candidate, DerivationEvidenceEnvelopeV2, PairedInterpretation]:
    try:
        admitted = authenticate_generation8_candidate(candidate)
        evidence = verify_derivation_evidence_envelope_v2(envelope, candidate=admitted)
        interpretation = interpret_paired_candidate(admitted)
    except Exception as exc:
        raise PlanV2Rejected("Plan-v2 Candidate, decoded rows, or derivation evidence rejected.") from exc
    if tuple(evidence["paired_profile"]) != CAPABILITY_V2_PROFILE:
        raise PlanV2Rejected("Plan-v2 profile/version dispatch is not paired-v3.")
    count = len(interpretation.mapping_inventory)
    if len(interpretation.requirement_inventory) != 6:
        raise PlanV2Rejected("Paired profile must provide exactly six requirements.")
    if count == 0 or count != len(interpretation.semantic_document["table"]["rows"]):
        raise PlanV2Rejected("Mapping cardinality must equal the nonempty decoded-row population.")
    if (evidence["requirement_inventory_digest"] != interpretation.requirement_inventory_digest
            or evidence["mapping_inventory_digest"] != interpretation.mapping_inventory_digest
            or evidence["mapping_count"] != count or evidence["decoded_row_count"] != count):
        raise PlanV2Rejected("Derivation evidence inventory differs from owner-decoded material.")
    return admitted, evidence, interpretation


def _verify_plan_v2_release(value: Any, snapshot: Any,
                            candidate: AuthenticatedGeneration8Candidate
                            ) -> tuple[VerifiedPublicationRelease, BCRPBundle]:
    if type(value) is not VerifiedPublicationRelease or type(snapshot) is not EvidenceSnapshot:
        raise PlanV2Rejected("An independently admitted native-v2 Release and snapshot are required.")
    try:
        source_bundle = _deserialize_bundle(value.serialized_bundle)
        release = verify_publication_release(source_bundle, evidence_snapshot=snapshot,
            expected_release_fingerprint=value.fingerprint.digest)
    except Exception as exc:
        raise PlanV2Rejected("Native-v2 Release failed independent reverification.") from exc
    ext = release.release.extensions
    family = tuple(ext[0].get(k) for k in ("owner_namespace", "name", "version", "validation_contract")) \
        if type(ext) is list and len(ext) == 1 and type(ext[0]) is dict else ()
    if family != ("briefforge-publication-release", "native-publication-release-authorization",
                   "2.0.0", "briefforge:publication-release-authorization:2.0.0"):
        raise PlanV2Rejected("Plan-v2 requires exact native-v2 Release dispatch.")
    if tuple(r.to_document() for r in source_bundle.records[:3]) != tuple(
            r.to_document() for r in candidate.bundle.records):
        raise PlanV2Rejected("Release embeds another Candidate closure.")
    return release, source_bundle


_PLAN_V2_POLICIES = (
    ("renderer", "renderer_identity", "renderer-exact-v1"),
    ("media-type", "media_types", "media-type-member-v1"),
    ("output-count", "output_count", "integer-text-equality-v1"),
    ("asset-count", "asset_count", "integer-text-equality-v1"),
    ("table-count", "table_count", "integer-text-equality-v1"),
    ("column-count", "column_count", "integer-text-equality-v1"))


def _plan_v2_wire(value: Any) -> Any:
    if isinstance(value, tuple): return [_plan_v2_wire(x) for x in value]
    return value


def plan_paired_v3_inventory(requirements: tuple[tuple[Any, ...], ...],
        mappings: tuple[tuple[Any, ...], ...], capability_payload: dict[str, Any],
        *, capability_fingerprint: str) -> tuple[list[list[Any]], list[list[Any]], list[list[Any]]]:
    """Generic production core: cardinality follows owner rows, never fixture labels."""
    if type(requirements) is not tuple or type(mappings) is not tuple or type(capability_payload) is not dict:
        raise PlanV2Rejected("Planner inventories require exact typed production values.")
    if len(requirements) != 6 or tuple((x[0], x[1]) for x in requirements) != tuple(
            (i, p[0]) for i, p in enumerate(_PLAN_V2_POLICIES)):
        raise PlanV2Rejected("Requirement inventory is not the six profile-owned requirements.")
    if not mappings:
        raise PlanV2Rejected("Mapping inventory cannot be empty when requirements exist.")
    if any(type(row) is not tuple or len(row) != 3 or row[0] != i for i, row in enumerate(mappings)):
        raise PlanV2Rejected("Mapping ordinals are incomplete or reordered.")
    refs = [canonical_json(_plan_v2_wire(row[1])) for row in mappings]
    if len(set(refs)) != len(refs): raise PlanV2Rejected("Mapping inventory contains duplicate rows.")
    requirement_outcomes: list[list[Any]] = []; mapping_outcomes: list[list[Any]] = []; findings = []
    for i, inventory in enumerate(requirements):
        key, claim, policy = _PLAN_V2_POLICIES[i]; owner = inventory[2]; actual = capability_payload[claim]
        supported = owner in actual if key == "media-type" else (
            type(actual) is int and str(actual) == owner if key.endswith("count") else actual == owner)
        failure = None if supported else f"{key}-unsupported"
        requirement_outcomes.append([i,key,owner,CAPABILITY_V2_CONTRACT,capability_fingerprint,
            claim,deepcopy(actual),policy,"supported" if supported else "unsupported",failure])
        if failure: findings.append([0,i,"requirement",key,failure])
    claim = deepcopy(capability_payload["mapping_capability"])
    mapping_supported = claim == {"contract":CAPABILITY_V2_MAPPING_CONTRACT,
        "profiles":[list(CAPABILITY_V2_PROFILE)],"mode":"static"}
    for i, (_, reference, relationship) in enumerate(mappings):
        if (type(reference) is not tuple or len(reference) != 3 or type(reference[2]) is not tuple
                or reference[2][:3] != ("briefforge:paired-terminal","3.0.0","Row")
                or type(relationship) is not str or not relationship):
            raise PlanV2Rejected("Mapping row has wrong domain, kind, or content.")
        failure = None if mapping_supported else "mapping-expression-unsupported"
        mapping_outcomes.append([i,_plan_v2_wire(reference),relationship,CAPABILITY_V2_MAPPING_CONTRACT,
            CAPABILITY_V2_CONTRACT,capability_fingerprint,deepcopy(claim),"mapping-expression-exact-v1",
            "supported" if mapping_supported else "unsupported",failure])
        if failure: findings.append([1,i,"mapping",_plan_v2_wire(reference),failure])
    return requirement_outcomes, mapping_outcomes, findings


def _task077_record_fingerprint(record: BCRPRecord, label: str) -> str:
    return domain_digest(f"briefforge.task075.{label}-record.v1", record.to_document())


def _construct_plan_v2(candidate: AuthenticatedGeneration8Candidate,
        evidence: DerivationEvidenceEnvelopeV2, interpretation: PairedInterpretation,
        release: VerifiedPublicationRelease, release_bundle: BCRPBundle,
        capability: VerifiedRendererCapabilityV2,
        issuer: PlanV2IssuerInputs) -> tuple[BCRPBundle, dict[str, Any]]:
    capability_record = capability.record; cap = capability_record.extensions[0]["payload"]
    requirements, mappings, findings = plan_paired_v3_inventory(
        interpretation.requirement_inventory, interpretation.mapping_inventory, cap,
        capability_fingerprint=capability.fingerprint)
    if findings: raise PlanV2Rejected("Plan-v2 compatibility unsupported: " + ", ".join(x[4] for x in findings))
    required_release_kinds = _PLAN_V2_REQUIRED_KINDS[:6]
    if (len(release_bundle.records) != len(required_release_kinds)
            or {record.kind for record in release_bundle.records} != set(required_release_kinds)
            or len({record.identity for record in release_bundle.records}) != len(required_release_kinds)):
        raise PlanV2Rejected("Release closure contains hidden, missing, or duplicate predecessor records.")
    closure = BCRPBundle(
        PROFILE_ID, PROFILE_VERSION,
        tuple(deepcopy(release_bundle.one(kind)) for kind in required_release_kinds))
    judgment = closure.one("ValidationJudgmentRecord")
    ready = closure.one("ReadyPresentationPackageRecord"); released = closure.one("PublicationReleaseRecord")
    req_digest=domain_digest("briefforge.task075.requirement-outcomes.v1",requirements)
    map_digest=domain_digest("briefforge.task075.mapping-outcomes.v1",mappings)
    completeness={"contract":PLAN_V2_COMPLETENESS_CONTRACT,
        "candidate_profile_instance_fingerprint":candidate.candidate_profile_instance_fingerprint,
        "release_fingerprint":release.fingerprint.digest,"capability_fingerprint":capability.fingerprint,
        "derivation_evidence_fingerprint":evidence["fingerprint"],
        "effective_graph_digest":interpretation.effective_graph.digest,
        "paired_closure_digest":evidence["paired_closure_digest"],
        "requirement_inventory_digest":interpretation.requirement_inventory_digest,
        "mapping_inventory_digest":interpretation.mapping_inventory_digest,
        "requirement_outcomes_digest":req_digest,"mapping_outcomes_digest":map_digest,
        "requirement_outcomes":requirements,"mapping_outcomes":mappings,"mapping_count":len(mappings),
        "findings":[],"supported":True}
    semantic={"ready_ref":ready.identity,"renderer_capability_ref":capability_record.identity,
        "declared_transformations":[],"fallbacks":[],"supported":True,"mode":"paired-v3-static"}
    implementation=evidence["implementation_digest"]
    payload={"contract":PLAN_V2_CONTRACT,"plan_identity":issuer.plan_identity,
        "candidate_profile_instance_fingerprint":candidate.candidate_profile_instance_fingerprint,
        "judgment_fingerprint":_task077_record_fingerprint(judgment,"judgment"),
        "ready_fingerprint":_task077_record_fingerprint(ready,"ready"),"release_identity":released.identity,
        "release_fingerprint":release.fingerprint.digest,"release_closure_digest":domain_digest(
            "briefforge.task075.release-closure.v1",[r.to_document() for r in closure.records]),
        "capability_identity":capability_record.identity,"capability_fingerprint":capability.fingerprint,
        "capability_contract":CAPABILITY_V2_CONTRACT,
        "resolver":["briefforge:paired-semantic-resolver","1.0.0",implementation],
        "derivation":["briefforge:effective-semantic-graph-derivation","1.0.0",implementation],
        "derivation_evidence_fingerprint":evidence["fingerprint"],"core_graph_digest":evidence["core_graph_digest"],
        "paired_graph_digest":evidence["paired_graph_digest"],"counterpart_proof_digest":evidence["counterpart_proof_digest"],
        "effective_graph_digest":evidence["effective_graph_digest"],"paired_closure_digest":evidence["paired_closure_digest"],
        "requirement_inventory_digest":interpretation.requirement_inventory_digest,
        "mapping_inventory_digest":interpretation.mapping_inventory_digest,"requirement_outcomes_digest":req_digest,
        "mapping_outcomes_digest":map_digest,"requirement_outcomes":requirements,"mapping_outcomes":mappings,
        "planning_completeness_digest":domain_digest("briefforge.task075.planning-completeness.v1",completeness),
        "mode":"paired-v3-static","supported":True,"findings":[],"operation_identity":issuer.operation_identity,
        "authorization_fingerprint":issuer.authorization_fingerprint,
        "semantic_digest":domain_digest("briefforge.task076.plan-core-semantic.v1",semantic)}
    payload["fingerprint"]=domain_digest("briefforge.task075.plan-extension.v2",payload)
    extension={"owner_namespace":_PLAN_EXTENSION_OWNER,"name":_PLAN_EXTENSION_NAME,"version":"2.0.0",
        "authority_ref":ACCEPTED_PLANNING_AUTHORITY_IDENTITY,"scope":"renderer-compatibility-plan",
        "target_refs":[issuer.plan_identity,candidate.candidate_identity,released.identity,capability_record.identity],
        "criticality":"required","character":"semantic","validation_contract":PLAN_V2_CONTRACT,
        "preservation":"must-preserve","payload":payload}
    plan=BCRPRecord("RendererCompatibilityPlanRecord",issuer.plan_identity,PROFILE_VERSION,semantic,[extension])
    return BCRPBundle(PROFILE_ID,PROFILE_VERSION,tuple(deepcopy(closure.records))+(deepcopy(capability_record),plan)),completeness


def _make_verified_plan_v2(bundle: BCRPBundle, completeness: dict[str, Any]) -> VerifiedRendererCompatibilityPlanV2:
    data=canonical_json({"profile_identity":bundle.profile_identity,"profile_version":bundle.profile_version,
        "records":[r.to_document() for r in bundle.records]})
    plan=bundle.one("RendererCompatibilityPlanRecord")
    extfp=plan.extensions[0]["payload"]["fingerprint"]
    outer=Fingerprint(
        domain="briefforge.task075.plan-extension.v2", root_identity=plan.identity,
        profile_identity=bundle.profile_identity, profile_version=bundle.profile_version,
        canonicalization="briefforge-generation8-canonical-json:1.0.0", algorithm="sha256",
        digest=extfp, scope="Unsigned RendererCompatibilityPlan v2 extension payload")
    return VerifiedRendererCompatibilityPlanV2(
        data, canonical_json(completeness), outer, extfp, hashlib.sha256(data).hexdigest())


def _closure_binding(bundle: BCRPBundle, root_identity: str,
        allow_publication_successors: bool) -> tuple[Any, ...]:
    records = tuple(canonical_json(record.to_document()) for record in bundle.records)
    kinds = tuple(record.kind for record in bundle.records)
    identities = tuple(record.identity for record in bundle.records)
    fingerprints = tuple(domain_digest(
        "briefforge.task077.complete-record.v1",
        {"kind": record.kind, "record": record.to_document()}) for record in bundle.records)
    brief,material,candidate,judgment,ready,release,capability,plan = identities[:8]
    edges = ((brief,()),(material,()),(candidate,(brief,material)),(judgment,(candidate,)),
        (ready,(judgment,)),(release,(ready,)),(capability,()),
        (plan,(candidate,ready,release,capability)))
    if allow_publication_successors:
        audit,conformance=identities[8:]
        edges += ((audit,(release,ready,plan,capability)),(conformance,(audit,ready)))
    return (bundle.profile_identity, bundle.profile_version, records, kinds, identities,
            fingerprints, "briefforge.task077.complete-record.v1", edges, root_identity,
            len(records), frozenset(identities), allow_publication_successors)


def verify_plan_v2_predecessor_closure(bundle: BCRPBundle, *,
        expected_bundle: BCRPBundle, root_identity: str,
        allow_publication_successors: bool) -> tuple[str, ...]:
    """Compare independently supplied exact records, profile, root, and successor family."""
    if type(root_identity) is not str or not root_identity:
        raise PlanV2Rejected("Closure requires one exact independently supplied root identity.")
    if type(allow_publication_successors) is not bool:
        raise PlanV2Rejected("Closure requires one exact independently supplied successor-family policy.")
    expected_count = 10 if allow_publication_successors else 8
    for label, value in (("subject", bundle), ("expected", expected_bundle)):
        if (type(value) is not BCRPBundle
                or value.profile_identity != PROFILE_ID
                or value.profile_version != PROFILE_VERSION
                or type(value.records) is not tuple
                or len(value.records) != expected_count
                or not all(type(record) is BCRPRecord for record in value.records)):
            raise PlanV2Rejected(
                f"Closure {label} requires the exact profile and {expected_count}-record immutable family.")
    binding = _closure_binding(expected_bundle, root_identity, allow_publication_successors)
    actual = _closure_binding(bundle, root_identity, allow_publication_successors)
    if actual != binding:
        raise PlanV2Rejected("Closure complete records or independently bound metadata differ.")
    kinds=_PLAN_V2_REQUIRED_KINDS + (("GeneratedArtifactAuditRecord","SemanticArtifactConformanceRecord")
        if allow_publication_successors else ())
    if tuple(x.kind for x in bundle.records) != kinds:
        raise PlanV2Rejected("Closure inventory, cardinality, or canonical order differs.")
    identities=tuple(x.identity for x in bundle.records)
    if len(set(identities)) != len(identities): raise PlanV2Rejected("Closure contains duplicate identities.")
    if root_identity != identities[-1]: raise PlanV2Rejected("Closure terminal root is absent or substituted.")
    brief,material,candidate,judgment,ready,release,capability,plan=identities[:8]
    refs: dict[str, tuple[str, ...]] = {
        brief: (), material: (), candidate: (brief, material), judgment: (candidate,),
        ready: (judgment,), release: (ready,), capability: (),
        plan: (candidate, ready, release, capability)}
    if allow_publication_successors:
        audit,conformance=identities[8:]
        refs[audit]=(release,ready,plan,capability)
        refs[conformance]=(audit,ready)
    for record in bundle.records:
        declared=record.semantic.get("predecessor_refs") if type(record.semantic) is dict else None
        if declared is not None and (type(declared) is not list or tuple(declared) != refs[record.identity]):
            raise PlanV2Rejected("Closure record declares altered predecessor topology.")
    reachable:set[str]=set(); active:set[str]=set()
    def visit(identity: str) -> None:
        if identity in active: raise PlanV2Rejected("Closure contains a predecessor cycle.")
        if identity in reachable: return
        active.add(identity)
        for predecessor in refs.get(identity, ()): 
            if predecessor not in refs: raise PlanV2Rejected("Closure contains a dangling predecessor.")
            visit(predecessor)
        active.remove(identity); reachable.add(identity)
    visit(root_identity)
    if reachable != set(identities): raise PlanV2Rejected("Closure contains unreachable or extra records.")
    plan_record=bundle.records[7]; plan_extension=plan_record.extensions
    if (type(plan_extension) is not list or len(plan_extension)!=1 or type(plan_extension[0]) is not dict
            or plan_record.semantic.get("ready_ref")!=ready
            or plan_record.semantic.get("renderer_capability_ref")!=capability
            or plan_extension[0].get("target_refs")!=[plan,candidate,release,capability]
            or plan_extension[0].get("payload",{}).get("release_identity")!=release):
        raise PlanV2Rejected("Plan record does not bind the exact closure predecessors.")
    return identities


def construct_renderer_compatibility_plan_v2(*, candidate: AuthenticatedGeneration8Candidate,
        derivation_evidence: DerivationEvidenceEnvelopeV2, verified_release: VerifiedPublicationRelease,
        evidence_snapshot: EvidenceSnapshot, capability: VerifiedRendererCapabilityV2,
        capability_issuer_inputs: CapabilityV2IssuerInputs, issuer_inputs: PlanV2IssuerInputs
        ) -> VerifiedRendererCompatibilityPlanV2:
    admitted,evidence,interpretation=_plan_v2_predecessors(candidate,derivation_evidence)
    try:
        cap=verify_renderer_capability_v2(capability,candidate=admitted,derivation_evidence=evidence,
            issuer_inputs=capability_issuer_inputs)
    except CapabilityV2Rejected as exc:
        raise PlanV2Rejected("Plan-v2 Capability predecessor failed exact authority binding.") from exc
    release,release_bundle=_verify_plan_v2_release(verified_release,evidence_snapshot,admitted)
    bundle,completeness=_construct_plan_v2(admitted,evidence,interpretation,release,release_bundle,cap,
        _verify_plan_v2_issuer(issuer_inputs))
    verify_plan_v2_predecessor_closure(
        bundle, expected_bundle=bundle, root_identity=issuer_inputs.plan_identity,
        allow_publication_successors=False)
    return _make_verified_plan_v2(bundle,completeness)


def _plan_v2_bundle_from_bytes(data: bytes) -> BCRPBundle:
    if type(data) is not bytes or len(data)>_PLAN_V2_MAX_BYTES: raise PlanV2Rejected("Plan-v2 bytes are not bounded.")
    try:
        doc=json.loads(data.decode("utf-8"),object_pairs_hook=_unique_json_pairs,
            parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
        if canonical_json(doc)!=data or type(doc) is not dict or set(doc)!={"profile_identity","profile_version","records"}:
            raise ValueError("noncanonical")
        if (doc["profile_identity"],doc["profile_version"])!=(PROFILE_ID,PROFILE_VERSION): raise ValueError("profile")
        bundle=BCRPBundle(PROFILE_ID,PROFILE_VERSION,tuple(BCRPRecord.from_document(x) for x in doc["records"]))
        if tuple(x.kind for x in bundle.records)!=_PLAN_V2_REQUIRED_KINDS: raise ValueError("inventory")
        record=bundle.one("RendererCompatibilityPlanRecord"); ext=record.extensions[0]; payload=ext["payload"]
        if (plan_record_family(record)!="v2" or set(record.semantic)!=_PLAN_V2_SEMANTIC_KEYS
                or set(ext)!=_EXTENSION_KEYS or type(payload) is not dict or set(payload)!=_PLAN_V2_PAYLOAD_KEYS):
            raise ValueError("closed")
        if payload["semantic_digest"]!=domain_digest("briefforge.task076.plan-core-semantic.v1",record.semantic):
            raise ValueError("semantic digest")
        unsigned={k:deepcopy(v) for k,v in payload.items() if k!="fingerprint"}
        if payload["fingerprint"]!=domain_digest("briefforge.task075.plan-extension.v2",unsigned): raise ValueError("fingerprint")
        return bundle
    except Exception as exc:
        if type(exc) is PlanV2Rejected: raise
        raise PlanV2Rejected("Plan-v2 is not one exact canonical closed eight-record bundle.") from exc


def verify_renderer_compatibility_plan_v2(value: Any, *, candidate: AuthenticatedGeneration8Candidate,
        derivation_evidence: DerivationEvidenceEnvelopeV2, verified_release: VerifiedPublicationRelease,
        evidence_snapshot: EvidenceSnapshot, capability: VerifiedRendererCapabilityV2,
        capability_issuer_inputs: CapabilityV2IssuerInputs, issuer_inputs: PlanV2IssuerInputs,
        expected_extension_fingerprint: str | None = None,
        expected_bundle_fingerprint: str | None = None) -> VerifiedRendererCompatibilityPlanV2:
    admitted,evidence,interpretation=_plan_v2_predecessors(candidate,derivation_evidence)
    try:
        cap=verify_renderer_capability_v2(capability,candidate=admitted,derivation_evidence=evidence,
            issuer_inputs=capability_issuer_inputs)
    except CapabilityV2Rejected as exc:
        raise PlanV2Rejected("Plan-v2 Capability predecessor failed exact authority binding.") from exc
    release,release_bundle=_verify_plan_v2_release(verified_release,evidence_snapshot,admitted)
    issuer=_verify_plan_v2_issuer(issuer_inputs)
    persisted=_plan_v2_bundle_from_bytes(value._bundle_document if type(value) is VerifiedRendererCompatibilityPlanV2
        else canonical_json({"profile_identity":value.profile_identity,"profile_version":value.profile_version,
            "records":[r.to_document() for r in value.records]}) if type(value) is BCRPBundle else value)
    expected,completeness=_construct_plan_v2(admitted,evidence,interpretation,release,release_bundle,cap,issuer)
    expected_bytes=canonical_json({"profile_identity":expected.profile_identity,"profile_version":expected.profile_version,
        "records":[r.to_document() for r in expected.records]})
    actual_bytes=canonical_json({"profile_identity":persisted.profile_identity,"profile_version":persisted.profile_version,
        "records":[r.to_document() for r in persisted.records]})
    if actual_bytes!=expected_bytes: raise PlanV2Rejected("Plan-v2 differs from independently reconstructed predecessors.")
    verify_plan_v2_predecessor_closure(
        persisted, expected_bundle=expected, root_identity=issuer.plan_identity,
        allow_publication_successors=False)
    verified=_make_verified_plan_v2(persisted,completeness)
    if expected_extension_fingerprint is not None and verified.extension_fingerprint!=expected_extension_fingerprint:
        raise PlanV2Rejected("Plan-v2 extension fingerprint differs.")
    if expected_bundle_fingerprint is not None and verified.bundle_sha256!=expected_bundle_fingerprint:
        raise PlanV2Rejected("Plan-v2 exact bundle SHA-256 differs.")
    return verified


def serialize_renderer_compatibility_plan_v2(value: Any, **authority: Any) -> bytes:
    return verify_renderer_compatibility_plan_v2(value, **authority)._bundle_document


def _verify_plan_v2_serialized_evidence(value: Any, *, expected_bundle: BCRPBundle,
        root_identity: str, allow_publication_successors: bool
        ) -> VerifiedRendererCompatibilityPlanV2:
    """Verify serialized Plan evidence without issuing or restoring live authority."""
    if type(root_identity) is not str or not root_identity:
        raise PlanV2Rejected("Data-only Plan-v2 verification requires one exact governed root.")
    if type(allow_publication_successors) is not bool:
        raise PlanV2Rejected("Data-only Plan-v2 verification requires an exact successor-family policy.")
    if allow_publication_successors:
        raise PlanV2Rejected("Persisted Plan-v2 evidence cannot include publication successors.")
    if type(value) is VerifiedRendererCompatibilityPlanV2:
        data = value._bundle_document
    elif type(value) is BCRPBundle:
        data = canonical_json({
            "profile_identity": value.profile_identity,
            "profile_version": value.profile_version,
            "records": [record.to_document() for record in value.records],
        })
    elif type(value) is bytes:
        data = value
    else:
        raise PlanV2Rejected("Data-only Plan-v2 verification requires exact bundle, bytes, or verified data.")
    bundle = _plan_v2_bundle_from_bytes(data)
    verify_plan_v2_predecessor_closure(
        bundle,
        expected_bundle=expected_bundle,
        root_identity=root_identity,
        allow_publication_successors=allow_publication_successors,
    )
    payload = bundle.one("RendererCompatibilityPlanRecord").extensions[0]["payload"]
    completeness = {
        "contract": PLAN_V2_COMPLETENESS_CONTRACT,
        "candidate_profile_instance_fingerprint": payload["candidate_profile_instance_fingerprint"],
        "release_fingerprint": payload["release_fingerprint"],
        "capability_fingerprint": payload["capability_fingerprint"],
        "derivation_evidence_fingerprint": payload["derivation_evidence_fingerprint"],
        "effective_graph_digest": payload["effective_graph_digest"],
        "paired_closure_digest": payload["paired_closure_digest"],
        "requirement_inventory_digest": payload["requirement_inventory_digest"],
        "mapping_inventory_digest": payload["mapping_inventory_digest"],
        "requirement_outcomes_digest": payload["requirement_outcomes_digest"],
        "mapping_outcomes_digest": payload["mapping_outcomes_digest"],
        "requirement_outcomes": deepcopy(payload["requirement_outcomes"]),
        "mapping_outcomes": deepcopy(payload["mapping_outcomes"]),
        "mapping_count": len(payload["mapping_outcomes"]),
        "findings": deepcopy(payload["findings"]),
        "supported": payload["supported"],
    }
    if payload["planning_completeness_digest"] != domain_digest(
            "briefforge.task075.planning-completeness.v1", completeness):
        raise PlanV2Rejected("Plan-v2 planning completeness differs from independently reconstructed data.")
    return _make_verified_plan_v2(bundle, completeness)


def _plan_v2_publish_anonymous(
        descriptor: int, directory_fd: int, filename: str) -> None:
    """Atomically publish one owned anonymous inode without replacing a name."""
    if (type(descriptor) is not int or descriptor < 0
            or type(directory_fd) is not int or directory_fd < 0):
        raise OSError(errno.EBADF, "Plan-v2 publication requires valid file descriptors.")
    if type(filename) is not str or not filename or os.path.basename(filename) != filename:
        raise OSError(errno.EINVAL, "Plan-v2 publication requires one safe destination name.")
    encoded_name = os.fsencode(filename)
    if b"\x00" in encoded_name:
        raise OSError(errno.EINVAL, "Plan-v2 publication name contains NUL.")
    if os.name != "posix" or not hasattr(os, "O_TMPFILE"):
        raise OSError(errno.ENOTSUP, "Anonymous Plan-v2 publication is unsupported.")
    try:
        libc = ctypes.CDLL(None, use_errno=True)
        linkat = libc.linkat
    except (OSError, AttributeError) as exc:
        raise OSError(errno.ENOSYS, "Atomic anonymous Plan-v2 publication is unavailable.") from exc
    linkat.argtypes = (
        ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int)
    linkat.restype = ctypes.c_int
    ctypes.set_errno(0)
    if linkat(-100, os.fsencode(f"/proc/self/fd/{descriptor}"),
              directory_fd, encoded_name, 0x400) != 0:
        error_number = ctypes.get_errno() or errno.EIO
        raise OSError(error_number, os.strerror(error_number), filename)


def persist_renderer_compatibility_plan_v2(value: Any, *, directory: Path,
        expected_bundle: BCRPBundle, root_identity: str,
        allow_publication_successors: bool,
        filename: str = "renderer-compatibility-plan-v2.json"
        ) -> PersistedRendererCompatibilityPlanV2:
    """Persist canonical Plan evidence through one anonymous-inode commit."""
    directory_fd = -1
    descriptor = -1
    published = False
    result: PersistedRendererCompatibilityPlanV2 | None = None
    failure: PlanV2Rejected | None = None
    cleanup_failure: OSError | None = None
    try:
        verified = _verify_plan_v2_serialized_evidence(
            value,
            expected_bundle=expected_bundle,
            root_identity=root_identity,
            allow_publication_successors=allow_publication_successors,
        )
        data = verified._bundle_document
        digest = hashlib.sha256(data).hexdigest()
        _capability_v2_safe_name(filename)
        directory_fd = _capability_v2_open_directory(directory)
        if os.listdir(directory_fd):
            raise PlanV2Rejected("Plan-v2 persistence directory must be empty.")
        if os.name != "posix" or not hasattr(os, "O_TMPFILE"):
            raise OSError(errno.ENOTSUP, "Anonymous Plan-v2 persistence is unsupported.")
        descriptor = os.open(
            ".",
            os.O_RDWR | os.O_TMPFILE | os.O_CLOEXEC | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=directory_fd,
        )
        initial = os.fstat(descriptor)
        owned = (initial.st_dev, initial.st_ino)
        if (not stat.S_ISREG(initial.st_mode) or initial.st_nlink != 0
                or stat.S_IMODE(initial.st_mode) != 0o600 or initial.st_size != 0):
            raise PlanV2Rejected("Plan-v2 anonymous inode properties differ.")
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short write")
            view = view[written:]
        os.fsync(descriptor)
        final = os.fstat(descriptor)
        if (not stat.S_ISREG(final.st_mode) or final.st_nlink != 0
                or stat.S_IMODE(final.st_mode) != 0o600
                or final.st_size != len(data)
                or (final.st_dev, final.st_ino) != owned):
            raise PlanV2Rejected("Plan-v2 anonymous write differs.")
        if os.lseek(descriptor, 0, os.SEEK_SET) != 0:
            raise PlanV2Rejected("Plan-v2 anonymous reread position differs.")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(65536, _PLAN_V2_MAX_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > _PLAN_V2_MAX_BYTES:
                raise PlanV2Rejected("Plan-v2 anonymous bytes exceed the bounded maximum.")
        reread = b"".join(chunks)
        if reread != data or len(reread) != len(data):
            raise PlanV2Rejected("Plan-v2 anonymous reread differs.")
        if hashlib.sha256(reread).hexdigest() != digest:
            raise PlanV2Rejected("Plan-v2 anonymous SHA-256 differs.")
        reverified = _verify_plan_v2_serialized_evidence(
            reread,
            expected_bundle=expected_bundle,
            root_identity=root_identity,
            allow_publication_successors=allow_publication_successors,
        )
        if (reverified.extension_fingerprint != verified.extension_fingerprint
                or reverified.bundle_sha256 != verified.bundle_sha256):
            raise PlanV2Rejected("Plan-v2 anonymous canonical verification differs.")
        result = PersistedRendererCompatibilityPlanV2(
            directory / filename,
            digest,
            len(data),
            verified.extension_fingerprint,
            verified.bundle_sha256,
            owned[0],
            owned[1],
        )
        _plan_v2_publish_anonymous(descriptor, directory_fd, filename)
        published = True
    except (OSError, CapabilityV2Rejected, PlanV2Rejected) as exc:
        failure = PlanV2Rejected(
            f"Cannot safely persist Plan-v2: {exc}",
            code="PLAN_V2_PERSISTENCE_REJECTED",
            location=f"{directory}/{filename}",
            reason=str(exc),
        )
        failure.__cause__ = exc
    finally:
        if descriptor >= 0:
            try:
                os.close(descriptor)
            except OSError as exc:
                if not published:
                    cleanup_failure = exc
        if directory_fd >= 0:
            try:
                os.close(directory_fd)
            except OSError as exc:
                if not published:
                    cleanup_failure = cleanup_failure or exc
    if failure is not None:
        if cleanup_failure is not None:
            failure.add_note(
                f"Plan-v2 anonymous-descriptor cleanup also failed: {cleanup_failure}")
        raise failure
    if not published or result is None:
        raise PlanV2Rejected("Plan-v2 persistence did not reach its atomic commit point.")
    return result


def reload_renderer_compatibility_plan_v2(path: Path, *,
        persistence_receipt: PersistedRendererCompatibilityPlanV2,
        expected_bundle: BCRPBundle, root_identity: str,
        allow_publication_successors: bool,
        expected_sha256: str | None = None,
        expected_extension_fingerprint: str | None = None,
        expected_bundle_fingerprint: str | None = None
        ) -> VerifiedRendererCompatibilityPlanV2:
    """Reload and authenticate exact Plan evidence; never restore invocation authority."""
    if not isinstance(path, Path) or not path.is_absolute():
        raise PlanV2Rejected(
            "Plan-v2 reload path must be absolute.",
            code="PLAN_V2_PATH_REJECTED", location=str(path))
    if type(persistence_receipt) is not PersistedRendererCompatibilityPlanV2:
        raise PlanV2Rejected(
            "Plan-v2 reload requires the exact persistence receipt type.",
            code="PLAN_V2_RECEIPT_REJECTED", location=str(path))
    if persistence_receipt.path != path:
        raise PlanV2Rejected(
            "Plan-v2 persistence receipt path differs.",
            code="PLAN_V2_RECEIPT_REJECTED", location=str(path))
    directory_fd = -1
    try:
        _capability_v2_safe_name(path.name)
        directory_fd = _capability_v2_open_directory(path.parent)
        if set(os.listdir(directory_fd)) != {path.name}:
            raise PlanV2Rejected("Plan-v2 persisted inventory differs.")
        data, identity = _capability_v2_read(
            directory_fd, path.name, max_bytes=_PLAN_V2_MAX_BYTES)
        if identity != (persistence_receipt.device, persistence_receipt.inode):
            raise PlanV2Rejected("Plan-v2 persistence receipt storage identity differs.")
        digest = hashlib.sha256(data).hexdigest()
        if persistence_receipt.sha256 != digest:
            raise PlanV2Rejected("Plan-v2 receipt SHA-256 differs from persisted bytes.")
        if persistence_receipt.length != len(data):
            raise PlanV2Rejected("Plan-v2 receipt length differs from persisted bytes.")
        verified = _verify_plan_v2_serialized_evidence(
            data,
            expected_bundle=expected_bundle,
            root_identity=root_identity,
            allow_publication_successors=allow_publication_successors,
        )
        if persistence_receipt.extension_fingerprint != verified.extension_fingerprint:
            raise PlanV2Rejected("Plan-v2 receipt extension fingerprint differs.")
        if persistence_receipt.bundle_fingerprint != verified.bundle_sha256:
            raise PlanV2Rejected("Plan-v2 receipt bundle fingerprint differs.")
        if expected_sha256 is not None and expected_sha256 != digest:
            raise PlanV2Rejected("Plan-v2 independently expected SHA-256 differs.")
        if (expected_extension_fingerprint is not None
                and expected_extension_fingerprint != verified.extension_fingerprint):
            raise PlanV2Rejected("Plan-v2 independently expected extension fingerprint differs.")
        if (expected_bundle_fingerprint is not None
                and expected_bundle_fingerprint != verified.bundle_sha256):
            raise PlanV2Rejected("Plan-v2 independently expected bundle fingerprint differs.")
        again, identity2 = _capability_v2_read(
            directory_fd, path.name, max_bytes=_PLAN_V2_MAX_BYTES)
        if again != data or identity2 != identity or set(os.listdir(directory_fd)) != {path.name}:
            raise PlanV2Rejected("Plan-v2 changed during immutable reload.")
        return verified
    except (OSError, CapabilityV2Rejected, PlanV2Rejected) as exc:
        raise PlanV2Rejected(
            f"Cannot safely reload Plan-v2: {exc}",
            code="PLAN_V2_RELOAD_REJECTED",
            location=str(path),
            reason=str(exc),
        ) from exc
    finally:
        if directory_fd >= 0:
            try:
                os.close(directory_fd)
            except OSError as exc:
                raise PlanV2Rejected(
                    f"Plan-v2 reload cleanup failed: {exc}",
                    code="PLAN_V2_CLEANUP_REJECTED",
                    location=str(path),
                    reason=str(exc),
                ) from exc

