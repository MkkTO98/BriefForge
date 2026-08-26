"""Renderer-independent, fail-closed BCRP compatibility planning.

This module consumes exact governed semantic evidence and emits at most one
compatibility Plan.  It never imports, discovers, selects, probes, or invokes a
renderer and grants no artifact, conformance, Manifest, or distribution
authority.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re
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
from .publication_release import (
    EvidenceSnapshot,
    VerifiedPublicationRelease,
    release_binding_from_verified_release,
    verify_publication_release,
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
    release_auth = release_record.extensions[0]["payload"]
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
            "candidate_fingerprint": release_auth["authorized_candidate_semantic_fingerprint"],
            "publication_identity": release_record.semantic["publication_lineage_id"],
            "publication_version": release_record.semantic["semantic_publication_version"],
            "evidence_snapshot": release_auth["authorized_evidence_snapshot"],
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
    unexpected = [
        item for item in generic.findings
        if not (item.family == "extension-boundary" and item.semantic_identity in specialized_extension_records)
    ]
    if unexpected:
        return CompatibilityPlanningResult(tuple(_finding("generic-plan-validation-failed", item.message, item.semantic_identity, item.location, item.referenced_identities) for item in unexpected), None)
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
