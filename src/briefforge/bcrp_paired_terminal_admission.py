"""Native BCRP Release/Plan adapter for the frozen paired-terminal profile."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from types import MappingProxyType
import threading
from time import monotonic as _monotonic
import weakref

from .bcrp.canonical import fingerprint_bundle
from .bcrp.model import BCRPBundle
from .bcrp_publication_release_v2 import (
    release_binding_from_verified_release as native_release_binding,
    verify_publication_release as verify_native_publication_release,
)
from .publication_release import (
    release_binding_from_verified_release as legacy_release_binding,
    verify_publication_release as verify_legacy_publication_release,
)
from .bcrp_renderer_compatibility_planning_v2 import (
    verify_renderer_compatibility_plan as verify_native_renderer_plan,
)
from .renderer_compatibility_planning import (
    CapabilityClaim as LegacyCapabilityClaim,
    RendererCapabilityDeclaration as LegacyRendererCapabilityDeclaration,
    VerifiedRendererCompatibilityPlan as LegacyVerifiedRendererCompatibilityPlan,
    verify_renderer_compatibility_plan as verify_legacy_renderer_plan,
)
from briefforge_terminal_profile.profile import (
    PROFILE_IDENTITY as TERMINAL_AUTHORITY_PROFILE_IDENTITY,
    PROFILE_VERSION as TERMINAL_AUTHORITY_PROFILE_VERSION,
    TERMINAL_OPERATIONAL_IDENTITIES,
    TERMINAL_OPERATIONAL_ROLES,
    TerminalAuthorityProfile,
    verify_terminal_authority_profile,
)
from briefforge_paired_terminal_profile.profile import (
    PROFILE_IDENTITY,
    PROFILE_VERSION,
    PAIRED_CAPABILITY_DECLARATION_IDENTITY,
    PairedAdmissionEnvelope,
    PairedProfileRejected,
    _candidate_semantics,
    _envelope_bindings,
    _fingerprint,
    _issue_upstream_token,
    _semantic_closure_fingerprint,
    _verify_exact_paired_declaration,
    _verify_exact_paired_plan,
)
from briefforge_paired_terminal_profile.schema import validate_admission_envelope


class NativeBCRPPairedTerminalAdmissionHandle:
    """Fieldless, non-transferable reference to process-local native authority."""

    __slots__ = ("__weakref__",)

    def __new__(cls):
        raise TypeError("native admission handles are issuer-only")

    def __copy__(self):
        raise TypeError("native admission handles cannot be copied")

    def __deepcopy__(self, memo):
        raise TypeError("native admission handles cannot be copied")

    def __reduce__(self):
        raise TypeError("native admission handles cannot be serialized")

    def __reduce_ex__(self, protocol):
        raise TypeError("native admission handles cannot be serialized")


# Values, including the frozen token, exist only while their weak handle key does.
_native_invocation_states: "weakref.WeakKeyDictionary[NativeBCRPPairedTerminalAdmissionHandle, tuple[object, float, str, str]]" = (
    weakref.WeakKeyDictionary())
_native_invocation_lock = threading.RLock()
_NATIVE_INVOCATION_TTL_SECONDS = 300.0
_AVAILABLE = "available"
_RESERVED = "reserved"
_CONSUMED = "consumed"
# Same-owner replay ledger.  Its identity is stable across authenticated reloads of
# the same Candidate; a fresh in-process authority object must not create a second
# native chain.  Issuance still requires the opaque predecessor authorities.
_native_v2_chain_states: dict[tuple[str, str], str] = {}


def _register_native_invocation_authority(token: object, *, family: str = "paired-v1"
        ) -> NativeBCRPPairedTerminalAdmissionHandle:
    """Hide frozen authority behind a new fieldless process-local handle."""
    handle = object.__new__(NativeBCRPPairedTerminalAdmissionHandle)
    with _native_invocation_lock:
        _native_invocation_states[handle] = (token, _monotonic(), _AVAILABLE, family)
    return handle


def _native_state(handle: object) -> tuple[object, float, str, str]:
    """Resolve only exact issuer-registered handles without leaking container errors."""
    if type(handle) is not NativeBCRPPairedTerminalAdmissionHandle:
        raise PairedProfileRejected(
            "native TASK-073 controlled invocation requires a native-issued handle")
    state = _native_invocation_states.get(handle)
    if state is None:
        raise PairedProfileRejected("native invocation authority is unavailable")
    return state


def _serialized_release_document(release) -> str:
    if hasattr(release, "serialized_bundle"):
        return release.serialized_bundle
    bundle = release.bundle
    return json.dumps({
        "profile_identity": bundle.profile_identity,
        "profile_version": bundle.profile_version,
        "records": [record.to_document() for record in bundle.records],
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _verify_exact_release_plan_cross_binding(release, plan, evidence_snapshot=None,
        *, release_binding=None) -> None:
    release_kinds = {
        "PresentationBriefRecord", "PortablePresentationMaterialRecord",
        "CandidatePresentationPackageRecord", "ValidationJudgmentRecord",
        "ReadyPresentationPackageRecord", "PublicationReleaseRecord",
    }
    plan_bundle = plan.bundle
    release_bundle = release.bundle
    if (type(plan_bundle) is not BCRPBundle or type(release_bundle) is not BCRPBundle or
            (plan_bundle.profile_identity, plan_bundle.profile_version) !=
            (release_bundle.profile_identity, release_bundle.profile_version)):
        raise PairedProfileRejected("Plan and supplied Release use different exact profile families")
    records = tuple(record for record in plan_bundle.records if record.kind in release_kinds)
    if len(records) != 6 or {record.kind for record in records} != release_kinds:
        raise PairedProfileRejected("Plan does not contain one exact six-record Release closure")
    embedded = BCRPBundle(plan_bundle.profile_identity, plan_bundle.profile_version, records)
    document = json.dumps({
        "profile_identity": embedded.profile_identity,
        "profile_version": embedded.profile_version,
        "records": [record.to_document() for record in embedded.records],
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if document != _serialized_release_document(release):
        raise PairedProfileRejected("supplied Release bytes differ from the Plan-bound Release closure")
    binding_function = release_binding or (
        native_release_binding if type(release).__module__.endswith("bcrp_publication_release_v2")
        else legacy_release_binding)
    if (fingerprint_bundle(embedded, domain="profile-instance", require_valid=False) !=
            fingerprint_bundle(release.bundle, domain="profile-instance", require_valid=False) or
            binding_function(release).fingerprint != release.fingerprint.digest):
        raise PairedProfileRejected("supplied Release fingerprint differs from the Plan-bound Release")


def _native_authority_admission(release, semantics):
    authorities = release.bundle.one("PortablePresentationMaterialRecord").semantic.get("authorities")
    if type(authorities) is not list or any(type(item) is not dict for item in authorities):
        raise PairedProfileRejected("Release authorities require exact JSON objects")
    by_identity = {item.get("id"): item for item in authorities}
    if len(by_identity) != len(authorities) or any(
            identity not in by_identity for identity in TERMINAL_OPERATIONAL_IDENTITIES):
        raise PairedProfileRejected("Release authority inventory is incomplete or duplicated")
    operational = tuple(dict(by_identity[identity]) for identity in TERMINAL_OPERATIONAL_IDENTITIES)
    content_ids = semantics.content_authorities
    released_content_ids = set(by_identity) - set(TERMINAL_OPERATIONAL_IDENTITIES)
    if (len(set(content_ids)) != len(content_ids) or set(content_ids) != released_content_ids):
        raise PairedProfileRejected("semantic content authorities differ from exact Release content ids")
    content = tuple(dict(by_identity[identity]) for identity in sorted(released_content_ids))
    profile = TerminalAuthorityProfile(
        TERMINAL_AUTHORITY_PROFILE_IDENTITY, TERMINAL_AUTHORITY_PROFILE_VERSION,
        tuple(MappingProxyType(item) for item in operational),
        tuple(MappingProxyType(item) for item in content))
    try:
        verify_terminal_authority_profile(profile)
    except Exception as exc:
        raise PairedProfileRejected("Release authority inventory differs from the exact terminal profile") from exc
    inventory = operational + content
    reserved = set(TERMINAL_OPERATIONAL_IDENTITIES) | set(TERMINAL_OPERATIONAL_ROLES)
    references = (tuple(item.authority_ref for item in semantics.statements)
        + (semantics.table.authority_ref,)
        + tuple(item.authority_ref for item in semantics.values)
        + tuple(item.authority_ref for item in semantics.qualifications)
        + tuple(item.authority_ref for item in semantics.provenance)
        + tuple(item.authority_ref for item in semantics.obligations))
    if any(ref in reserved or ref not in set(content_ids) for ref in references):
        raise PairedProfileRejected("display-capable authority reference is operational or unreleased")
    profile_fingerprint = _fingerprint({
        "profile_identity": PROFILE_IDENTITY,
        "profile_version": PROFILE_VERSION,
        "authorities": list(inventory),
        "content_authorities": list(content_ids),
        "semantic_source_closure_fingerprint": _semantic_closure_fingerprint(semantics),
    })
    return inventory, profile_fingerprint


def _legacy_paired_profile_views(declaration, plan):
    """Project additive v2 planning proof into the frozen paired-profile DTOs."""
    if type(declaration) is LegacyRendererCapabilityDeclaration:
        legacy_declaration = declaration
    else:
        fields = asdict(declaration)
        fields["capabilities"] = tuple(
            LegacyCapabilityClaim(**asdict(item)) for item in declaration.capabilities)
        legacy_declaration = LegacyRendererCapabilityDeclaration(**fields)
    if type(plan) is LegacyVerifiedRendererCompatibilityPlan:
        legacy_plan = plan
    else:
        legacy_plan = LegacyVerifiedRendererCompatibilityPlan(
            plan._bundle_document, plan.fingerprint, plan.mappings_document)
    return legacy_declaration, legacy_plan


def verify_native_bcrp_paired_terminal_admission(*, release_bundle, evidence_snapshot,
        lifecycle_scope, declaration, planning_authorization, plan_bundle):
    """Issue one paired token only after native Release and exact Plan cross-binding."""
    try:
        supplied_release = release_bundle.one("PublicationReleaseRecord")
        extensions = supplied_release.extensions
        if (type(extensions) is not list or len(extensions) != 1 or
                type(extensions[0]) is not dict):
            raise PairedProfileRejected("Release extension family must be exactly singular and explicit")
        native_tuple = (
            extensions[0].get("owner_namespace"), extensions[0].get("name"),
            extensions[0].get("version"), extensions[0].get("scope"),
            extensions[0].get("criticality"), extensions[0].get("character"),
            extensions[0].get("validation_contract"), extensions[0].get("preservation"))
        native_family = native_tuple == (
            "briefforge-publication-release", "native-publication-release-authorization",
            "2.0.0", "native-bcrp-publication-release", "required", "semantic",
            "briefforge:publication-release-authorization:2.0.0", "must-preserve")
        if (type(extensions) is list and len(extensions) == 1 and
                extensions[0].get("name") == "native-publication-release-authorization" and
                not native_family):
            raise PairedProfileRejected("unknown or mixed native Release extension family")
        if native_family:
            release_verifier = verify_native_publication_release
            plan_verifier = verify_native_renderer_plan
            binding_function = native_release_binding
        else:
            release_verifier = verify_legacy_publication_release
            plan_verifier = verify_legacy_renderer_plan
            binding_function = legacy_release_binding
        release = release_verifier(release_bundle, evidence_snapshot=evidence_snapshot)
        plan = plan_verifier(
            plan_bundle, evidence_snapshot=evidence_snapshot, lifecycle_scope=lifecycle_scope,
            declaration=declaration, authorization=planning_authorization)
        _verify_exact_release_plan_cross_binding(
            release, plan, release_binding=binding_function)
        declaration, plan = _legacy_paired_profile_views(declaration, plan)
        declaration = _verify_exact_paired_declaration(declaration)
        plan = _verify_exact_paired_plan(plan, declaration)
        admission = PairedAdmissionEnvelope(
            PROFILE_IDENTITY, PROFILE_VERSION, release.release.identity,
            release.fingerprint.digest, getattr(lifecycle_scope, "inventory_digest"),
            plan.plan.identity, plan.fingerprint.digest, declaration.identity,
            declaration.fingerprint)
        validate_admission_envelope(admission)
        if admission.capability_declaration_identity != PAIRED_CAPABILITY_DECLARATION_IDENTITY:
            raise PairedProfileRejected("capability declaration is not the exact paired renderer binding")
        semantics = _candidate_semantics(release)
        authority_inventory, profile_fingerprint = _native_authority_admission(release, semantics)
        token = _issue_upstream_token(
            semantics, admission, authority_inventory, profile_fingerprint, plan)
        return _register_native_invocation_authority(token)
    except PairedProfileRejected:
        raise
    except Exception as exc:
        raise PairedProfileRejected(str(exc)) from exc


@dataclass(frozen=True)
class NativePairedV2AdmissionState:
    """Immutable commitments hidden behind the sole native admission handle owner."""
    candidate_bytes: bytes
    candidate_identity: str
    envelope_bytes: bytes
    release_bytes: str
    release_fingerprint: str
    capability_bytes: bytes
    capability_family: tuple[str, str, str, str]
    renderer_identity: str
    implementation_identity: str
    implementation_digest: str
    plan_bytes: bytes
    plan_extension_fingerprint: str
    chain_key: tuple[str, str]
    family: str = "paired-v3-plan-v2"


def issue_native_bcrp_paired_terminal_admission_v2(**authority):
    """Sole live/native issuance edge for one exact generation-8 authority chain."""
    from .bcrp_renderer_compatibility_planning_v2 import (
        serialize_renderer_capability_v2_bundle,
        verify_renderer_compatibility_plan_v2,
    )
    from .task076_contracts import (
        _generation8_candidate_authority,
        authenticate_generation8_candidate,
        canonical_json,
    )
    try:
        authority = dict(authority)
        candidate = authenticate_generation8_candidate(authority["candidate"])
        presented_plan = authority.pop("plan")
        plan = verify_renderer_compatibility_plan_v2(presented_plan, **authority)
        capability = authority["capability"]
        cap = capability.record.extensions[0]
        payload = cap["payload"]
        capability_bytes = serialize_renderer_capability_v2_bundle(
            capability, candidate=candidate,
            derivation_evidence=authority["derivation_evidence"],
            issuer_inputs=authority["capability_issuer_inputs"])
        release = authority["verified_release"]
        envelope_bytes = canonical_json(authority["derivation_evidence"].to_document())
        _generation8_candidate_authority(candidate)
        chain_digest = hashlib.sha256(canonical_json({
            "candidate_sha256": hashlib.sha256(candidate.profile_bytes).hexdigest(),
            "envelope_sha256": hashlib.sha256(envelope_bytes).hexdigest(),
            "release_fingerprint": release.fingerprint.digest,
            "capability_sha256": hashlib.sha256(capability_bytes).hexdigest(),
            "plan_sha256": hashlib.sha256(plan._bundle_document).hexdigest(),
        })).hexdigest()
        chain_key = (candidate.candidate_profile_instance_fingerprint, chain_digest)
        state = NativePairedV2AdmissionState(
            candidate.profile_bytes, candidate.candidate_identity, envelope_bytes,
            release.serialized_bundle, release.fingerprint.digest, capability_bytes,
            tuple(cap.get(key) for key in (
                "owner_namespace", "name", "version", "validation_contract")),
            payload["renderer_identity"], payload["implementation_identity"],
            payload["implementation_digest"], plan._bundle_document,
            plan.extension_fingerprint, chain_key)
        with _native_invocation_lock:
            if chain_key in _native_v2_chain_states:
                raise PairedProfileRejected(
                    "native paired-v3 predecessor chain was already issued")
            handle = _register_native_invocation_authority(state, family=state.family)
            _native_v2_chain_states[chain_key] = _AVAILABLE
        return handle
    except PairedProfileRejected:
        raise
    except Exception as exc:
        raise PairedProfileRejected("native paired-v3 Plan-v2 admission rejected") from exc


def verify_native_bcrp_paired_terminal_admission_v2(handle, *, plan=None):
    """Reassert exact owner/family/binding without minting new authority."""
    with _native_invocation_lock:
        state, _, availability, family = _native_state(handle)
        if family != "paired-v3-plan-v2" or type(state) is not NativePairedV2AdmissionState:
            raise PairedProfileRejected("native handle belongs to another issuer family")
        if availability == _CONSUMED:
            raise PairedProfileRejected("native invocation authority was already consumed")
        if plan is not None and (getattr(plan, "_bundle_document", None) != state.plan_bytes
                or getattr(plan, "extension_fingerprint", None) != state.plan_extension_fingerprint):
            raise PairedProfileRejected("native handle is bound to another Plan-v2")
    return handle


def consume_native_bcrp_paired_terminal_admission_v2(*, upstream_admission):
    """Spend one native-v2 handle and return immutable, nonauthority commitments."""
    verify_native_bcrp_paired_terminal_admission_v2(upstream_admission)
    state = _reserve_native_invocation(upstream_admission)
    try:
        _commit_native_invocation(upstream_admission)
    except BaseException:
        _release_native_invocation_reservation(upstream_admission)
        raise
    return state


def verify_native_bcrp_paired_terminal_token(token):
    """Reassert exact process-local handle provenance and frozen-token integrity."""
    _resolve_native_bcrp_paired_terminal_token(token)
    return token


def _resolve_native_bcrp_paired_terminal_token(handle: object) -> object:
    from briefforge_paired_terminal_profile.profile import consume_paired_upstream_admission
    with _native_invocation_lock:
        frozen_token, _, _, family = _native_state(handle)
        if family == "paired-v1":
            consume_paired_upstream_admission(frozen_token)
        return frozen_token


def _reserve_native_invocation(handle: object) -> object:
    """Atomically reserve one unexpired native invocation capability."""
    from briefforge_paired_terminal_profile.profile import consume_paired_upstream_admission
    with _native_invocation_lock:
        frozen_token, issued_at, availability, family = _native_state(handle)
        if family == "paired-v1":
            consume_paired_upstream_admission(frozen_token)
        if availability == _CONSUMED:
            raise PairedProfileRejected("native invocation authority was already consumed")
        if availability == _RESERVED:
            raise PairedProfileRejected("native invocation authority is concurrently reserved")
        if _monotonic() - issued_at >= _NATIVE_INVOCATION_TTL_SECONDS:
            raise PairedProfileRejected("native invocation authority expired")
        _native_invocation_states[handle] = (frozen_token, issued_at, _RESERVED, family)
        if type(frozen_token) is NativePairedV2AdmissionState:
            _native_v2_chain_states[frozen_token.chain_key] = _RESERVED
        return frozen_token


def _release_native_invocation_reservation(handle: object) -> None:
    with _native_invocation_lock:
        if type(handle) is not NativeBCRPPairedTerminalAdmissionHandle:
            return
        state = _native_invocation_states.get(handle)
        if state is not None and state[2] == _RESERVED:
            _native_invocation_states[handle] = (state[0], state[1], _AVAILABLE, state[3])
            if type(state[0]) is NativePairedV2AdmissionState:
                _native_v2_chain_states[state[0].chain_key] = _AVAILABLE


def _commit_native_invocation(handle: object) -> None:
    with _native_invocation_lock:
        frozen_token, issued_at, availability, family = _native_state(handle)
        if availability != _RESERVED:
            raise PairedProfileRejected("native invocation reservation was lost")
        if _monotonic() - issued_at >= _NATIVE_INVOCATION_TTL_SECONDS:
            raise PairedProfileRejected("native invocation authority expired")
        _native_invocation_states[handle] = (frozen_token, issued_at, _CONSUMED, family)
        if type(frozen_token) is NativePairedV2AdmissionState:
            _native_v2_chain_states[frozen_token.chain_key] = _CONSUMED


def _verify_native_invocation_target(token: object, projection: object) -> None:
    """Perform the last retry-safe target check before irreversible commitment."""
    from briefforge_paired_terminal_profile.profile import verify_paired_upstream_admission_token
    verify_paired_upstream_admission_token(token, projection=projection)


def consume_native_bcrp_paired_upstream_admission(*, upstream_admission):
    """Return frozen read-only semantic/envelope views without exposing authority."""
    frozen_token = _resolve_native_bcrp_paired_terminal_token(upstream_admission)
    from briefforge_paired_terminal_profile.profile import consume_paired_upstream_admission
    return consume_paired_upstream_admission(frozen_token)


def build_native_bcrp_paired_editorial_projection(*, upstream_admission):
    """Construct a projection through native process-local authority."""
    frozen_token = _resolve_native_bcrp_paired_terminal_token(upstream_admission)
    from briefforge_paired_terminal_profile.projection import build_paired_editorial_projection
    return build_paired_editorial_projection(admitted=frozen_token)


def persist_native_bcrp_paired_profile_projection_evidence(**kwargs):
    """Persist projection evidence after internally resolving native authority."""
    frozen_token = _resolve_native_bcrp_paired_terminal_token(
        kwargs.get("upstream_admission"))
    call = dict(kwargs)
    call["upstream_admission"] = frozen_token
    from briefforge_paired_terminal_profile.projection import (
        persist_paired_profile_projection_evidence)
    return persist_paired_profile_projection_evidence(**call)


def verify_native_bcrp_persisted_paired_profile_projection_evidence(**kwargs):
    """Verify projection evidence after internally resolving native authority."""
    frozen_token = _resolve_native_bcrp_paired_terminal_token(
        kwargs.get("upstream_admission"))
    call = dict(kwargs)
    call["upstream_admission"] = frozen_token
    from briefforge_paired_terminal_profile.projection import (
        verify_persisted_paired_profile_projection_evidence)
    return verify_persisted_paired_profile_projection_evidence(**call)


def assess_native_bcrp_paired_semantic_artifact_conformance(**kwargs):
    """Enter frozen conformance production with internally resolved authority."""
    frozen_token = _resolve_native_bcrp_paired_terminal_token(
        kwargs.get("upstream_admission"))
    call = dict(kwargs)
    call["upstream_admission"] = frozen_token
    from briefforge_paired_terminal_profile.semantic_conformance import (
        assess_persisted_paired_semantic_artifact_conformance)
    return assess_persisted_paired_semantic_artifact_conformance(**call)


def verify_native_bcrp_paired_semantic_artifact_conformance(**kwargs):
    """Enter frozen conformance verification with internally resolved authority."""
    frozen_token = _resolve_native_bcrp_paired_terminal_token(
        kwargs.get("upstream_admission"))
    call = dict(kwargs)
    call["upstream_admission"] = frozen_token
    from briefforge_paired_terminal_profile.semantic_conformance import (
        verify_persisted_paired_semantic_artifact_conformance)
    return verify_persisted_paired_semantic_artifact_conformance(**call)


def enter_native_bcrp_paired_manifest_bridge(**kwargs):
    """Narrow native-provenance gate for the existing Manifest entry."""
    frozen_token = _resolve_native_bcrp_paired_terminal_token(
        kwargs.get("upstream_admission"))
    call = dict(kwargs)
    call["upstream_admission"] = frozen_token
    from briefforge_paired_terminal_profile.manifest_admission import (
        produce_paired_terminal_publication_manifest)
    return produce_paired_terminal_publication_manifest(**call)


def invoke_native_bcrp_controlled_paired_renderer(*, projection, authorization,
        upstream_admission, projection_evidence):
    """Spend exactly one native token at the frozen controlled-invocation edge."""
    from briefforge_paired_terminal_profile.controlled_invocation import (
        invoke_controlled_paired_renderer)
    reservation_returned = False
    try:
        frozen_token = _reserve_native_invocation(upstream_admission)
        reservation_returned = True
        _verify_native_invocation_target(frozen_token, projection)
        _commit_native_invocation(upstream_admission)
    except BaseException as exc:
        # A reservation rejection may describe a concurrent caller's state.
        # Other interruptions can occur after reserve changed this handle but
        # before its return reached the assignment above.
        if reservation_returned or not isinstance(exc, PairedProfileRejected):
            # This is a no-op after a successful commit, preserving consumption.
            _release_native_invocation_reservation(upstream_admission)
        raise
    return invoke_controlled_paired_renderer(
        projection=projection, authorization=authorization,
        upstream_admission=frozen_token, projection_evidence=projection_evidence)
