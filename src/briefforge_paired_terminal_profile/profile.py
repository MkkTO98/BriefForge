"""Verified-Release admission boundary for paired terminal semantics.

The admitted object issued here is an immutable, process-local closure.  Its
issuer tracking prevents accidental construction and cross-binding inside the
trusted BriefForge process.  It is deliberately not represented as
authentication against hostile code running in the same Python interpreter.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import secrets
import weakref
from types import MappingProxyType

from briefforge.publication_release import verify_publication_release
from briefforge.renderer_compatibility_planning import (
    ACCEPTED_DECLARATION_PROFILE_ID, ACCEPTED_DECLARATION_PROFILE_VERSION,
    ACCEPTED_RENDERER_OWNER, ACCEPTED_RENDERER_ROLE, CAPABILITY_DECLARATION_CONTRACT,
    RendererCapabilityDeclaration, VerifiedRendererCompatibilityPlan,
    compute_capability_declaration_fingerprint, verify_renderer_compatibility_plan,
)
from briefforge_terminal_profile.profile import (
    PROFILE_IDENTITY as TERMINAL_AUTHORITY_PROFILE_IDENTITY,
    PROFILE_VERSION as TERMINAL_AUTHORITY_PROFILE_VERSION,
    TERMINAL_OPERATIONAL_IDENTITIES, TERMINAL_OPERATIONAL_ROLES,
    TerminalAuthorityProfile, verify_material_authority_profile,
    verify_terminal_authority_profile,
)

from .schema import (
    PROFILE_IDENTITY, PROFILE_VERSION, Obligation, PairedAdmissionEnvelope,
    PairedRow, PairedSchemaRejected, PairedSemanticInput, PairedTable,
    PairedValue, Provenance, QualificationEdge, Section, SectionChild,
    Statement, validate_admission_envelope, validate_paired_semantics,
)

PAIRED_SEMANTIC_VALIDATION_CONTRACT = (
    "briefforge:representative-paired-terminal-semantic-input:3.0.0"
)
PAIRED_SEMANTIC_EXTENSION_OWNER = "briefforge-paired-terminal-profile"
PAIRED_SEMANTIC_EXTENSION_NAME = "paired-semantic-input"
PAIRED_SEMANTIC_EXTENSION_VERSION = "3.0.0"
_EXTENSION_KEYS = {
    "owner_namespace", "name", "version", "criticality", "preservation",
    "authority_ref", "scope", "target_refs", "character",
    "validation_contract", "payload",
}
_CORE_EXTENSION_CONTRACT = "bcrp:core-extension-envelope:1.0.0"
_PAIRED_EXTENSION_SCOPE = "candidate-paired-semantic-input"
_CANDIDATE_KIND = "Candidate" "PresentationPackageRecord"
PAIRED_RENDERER_IDENTITY = "briefforge:representative-paired-static-html-renderer:1.0.0"
PAIRED_RENDERER_VERSION = "1.0.0"
PAIRED_CAPABILITY_DECLARATION_IDENTITY = "renderer-capability:representative-paired-static-html"
PAIRED_CAPABILITY_CLAIMS = (
    ("capability:paired-static-html", "static",
     ("one-standalone-html", "no-external-assets"), True),
)
PAIRED_DETERMINISM_CONTROLS = ("deterministic", "bounded", "offline")
PAIRED_CAPABILITY_TUPLE = (
    ("profile", "briefforge:representative-paired-terminal-static-html-profile:3.0.0"),
    ("projection_schema", "briefforge:representative-paired-static-html-projection-schema:1.0.0"),
    ("projection_implementation", "briefforge_paired_terminal_profile.projection:1.0.0"),
    ("renderer", PAIRED_RENDERER_IDENTITY),
    ("invocation_policy", "briefforge-paired-terminal-controlled-renderer-invocation-policy:1.0.0"),
    ("invocation_evidence", "briefforge:paired-terminal-controlled-renderer-invocation-evidence:1.0.0"),
    ("invocation_authorization_class", "briefforge_paired_terminal_profile.controlled_invocation.PairedTerminalRendererInvocationAuthorization"),
    ("conformance_profile", "briefforge:representative-paired-static-html-conformance-profile:1.0.0"),
    ("assessor_implementation", "briefforge_paired_terminal_profile.semantic_conformance:1.0.0"),
    ("conformance_policy", "briefforge-paired-terminal-semantic-conformance-assessment-policy:1.0.0"),
    ("conformance_evidence", "briefforge:paired-terminal-semantic-artifact-conformance-evidence:1.0.0"),
    ("conformance_authorization_class", "briefforge_paired_terminal_profile.semantic_conformance.PairedTerminalSemanticArtifactConformanceAuthorization"),
    ("manifest_policy", "briefforge-paired-terminal-publication-manifest-admission-policy:3.0.0"),
    ("manifest_profile", "briefforge:paired-terminal-publication-manifest-admission-profile:3.0.0"),
    ("manifest_contract", "briefforge:paired-terminal-publication-manifest-admission-authority:3.0.0"),
    ("manifest_implementation", "briefforge_paired_terminal_profile.manifest_admission:1.0.0"),
    ("manifest_authorization_class", "briefforge.publication_manifest_admission.PublicationManifestAuthorization"),
)


class PairedProfileRejected(ValueError):
    """The exact v3 profile did not admit the verified Release closure."""


_TOKEN_NONCE_BYTES = 32
_issued_tokens: "weakref.WeakSet[PairedUpstreamAdmissionToken]" = weakref.WeakSet()
_issued_token_seals: "weakref.WeakKeyDictionary[PairedUpstreamAdmissionToken, str]" = weakref.WeakKeyDictionary()


class PairedUpstreamAdmissionToken:
    """Immutable admitted Release semantics for a trusted process boundary.

    This is an anti-bypass API capability, not a security credential against
    hostile code with arbitrary access to this interpreter.
    """

    __slots__ = (
        "_bindings", "_content_closure_fingerprint", "_semantics", "_admission",
        "_authority_inventory", "_profile_admission_fingerprint", "_plan_documents",
        "_predecessor_prefix_fingerprint", "_capability_tuple", "_nonce", "__weakref__",
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        raise TypeError("paired upstream admission tokens are issuer-only")

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("paired upstream admission tokens are immutable")

    def __reduce__(self):
        raise TypeError("paired upstream admission tokens cannot be serialized")

    def __copy__(self):
        raise TypeError("paired upstream admission tokens cannot be copied")

    def __deepcopy__(self, memo):
        raise TypeError("paired upstream admission tokens cannot be copied")


def _semantic_closure_fingerprint(semantics: PairedSemanticInput) -> str:
    document = {"semantics": asdict(semantics),
                "mapping_trace": [list(item) for item in semantics.renderer_mappings]}
    encoded = json.dumps(document, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _fingerprint(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _release_authority_admission(release: object,
                                 semantics: PairedSemanticInput) -> tuple[tuple[dict, ...], str]:
    """Derive the authority split solely from the verified Release material."""
    try:
        authorities = release.bundle.one(
            "PortablePresentationMaterialRecord").semantic["authorities"]
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise PairedProfileRejected("verified Release lacks its authority inventory") from exc
    if type(authorities) is not list or any(type(item) is not dict for item in authorities):
        raise PairedProfileRejected("Release authorities require exact JSON objects")
    inventory = tuple(dict(item) for item in authorities)
    profile = TerminalAuthorityProfile(
        TERMINAL_AUTHORITY_PROFILE_IDENTITY, TERMINAL_AUTHORITY_PROFILE_VERSION,
        tuple(MappingProxyType(dict(item)) for item in inventory[:8]),
        tuple(MappingProxyType(dict(item)) for item in inventory[8:]),
    )
    try:
        verify_terminal_authority_profile(profile)
        verify_material_authority_profile(authorities, profile)
    except Exception as exc:
        raise PairedProfileRejected(
            "Release authority inventory differs from the exact terminal profile") from exc
    content_ids = tuple(item["id"] for item in inventory[8:])
    if semantics.content_authorities != content_ids:
        raise PairedProfileRejected(
            "semantic content authorities differ from exact Release content ids")
    reserved = set(TERMINAL_OPERATIONAL_IDENTITIES) | set(TERMINAL_OPERATIONAL_ROLES)
    display_refs = (tuple(item.authority_ref for item in semantics.statements)
        + (semantics.table.authority_ref,)
        + tuple(item.authority_ref for item in semantics.values)
        + tuple(item.authority_ref for item in semantics.qualifications)
        + tuple(item.authority_ref for item in semantics.provenance)
        + tuple(item.authority_ref for item in semantics.obligations))
    if any(ref in reserved or ref not in set(content_ids) for ref in display_refs):
        raise PairedProfileRejected(
            "display-capable authority reference is operational or unreleased")
    admission_fingerprint = _fingerprint({
        "profile_identity": PROFILE_IDENTITY, "profile_version": PROFILE_VERSION,
        "authorities": list(inventory), "content_authorities": list(content_ids),
        "semantic_source_closure_fingerprint": _semantic_closure_fingerprint(semantics),
    })
    return inventory, admission_fingerprint


def _envelope_bindings(admission: PairedAdmissionEnvelope) -> tuple[str, ...]:
    return tuple(getattr(admission, name) for name in admission.__dataclass_fields__)


def _exact_object(value: object, keys: tuple[str, ...], label: str) -> dict:
    if type(value) is not dict or set(value) != set(keys):
        raise PairedProfileRejected(f"{label} requires exact fields")
    return value


def _objects(value: object, keys: tuple[str, ...], constructor, label: str) -> tuple:
    if type(value) is not list:
        raise PairedProfileRejected(f"{label} requires an exact JSON array")
    return tuple(constructor(**_exact_object(item, keys, label)) for item in value)


def build_paired_semantic_extension(
    semantics: PairedSemanticInput, *, candidate_identity: str,
) -> dict:
    """Encode the complete paired DTO as one canonical JSON string inside BCRP.

    The string boundary keeps extension-owned identities and explicit nulls opaque to
    the unchanged eleven-kind BCRP graph while preserving exact, independently
    reconstructable bytes.
    """
    validate_paired_semantics(semantics)
    if type(candidate_identity) is not str or not candidate_identity.startswith("candidate:"):
        raise PairedProfileRejected("exact Candidate identity required for paired extension")
    if not semantics.content_authorities:
        raise PairedProfileRejected("paired extension requires a released content authority")
    canonical_semantics = json.dumps(asdict(semantics), ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False)
    payload = {
        "contract_identity": PAIRED_SEMANTIC_VALIDATION_CONTRACT,
        "contract_version": PAIRED_SEMANTIC_EXTENSION_VERSION,
        "canonical_semantics": canonical_semantics,
    }
    return {
        "owner_namespace": PAIRED_SEMANTIC_EXTENSION_OWNER,
        "name": PAIRED_SEMANTIC_EXTENSION_NAME,
        "version": PAIRED_SEMANTIC_EXTENSION_VERSION,
        "authority_ref": semantics.content_authorities[0],
        "scope": _PAIRED_EXTENSION_SCOPE, "target_refs": [candidate_identity],
        "criticality": "required", "character": "semantic",
        "preservation": "must-preserve", "validation_contract": _CORE_EXTENSION_CONTRACT,
        "payload": payload,
    }


def _reconstruct_semantics(payload: object) -> PairedSemanticInput:
    """Reconstruct the immutable DTO solely from one governed Candidate payload."""
    if type(payload) is not str or len(payload.encode("utf-8")) > 4 * 1024 * 1024:
        raise PairedProfileRejected("paired semantic payload requires bounded canonical JSON text")
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise PairedProfileRejected("paired semantic payload is malformed") from exc
    if json.dumps(parsed, ensure_ascii=False, sort_keys=True,
                  separators=(",", ":"), allow_nan=False) != payload:
        raise PairedProfileRejected("paired semantic payload is not canonical JSON")
    payload = parsed
    root_keys = (
        "sections", "statements", "table", "values", "qualifications", "provenance",
        "obligations", "evidence_snapshots", "external_references", "content_authorities",
        "renderer_requirements", "renderer_mappings",
    )
    root = _exact_object(payload, root_keys, "paired semantic payload")

    sections = []
    for item in root["sections"] if type(root["sections"]) is list else ():
        data = _exact_object(item, ("identity", "title", "order", "children"), "section")
        children = _objects(data["children"], ("kind", "target_ref"), SectionChild,
                            "section child")
        sections.append(Section(data["identity"], data["title"], data["order"], children))
    if type(root["sections"]) is not list:
        raise PairedProfileRejected("sections requires an exact JSON array")

    statements = _objects(root["statements"],
        ("identity", "role", "text", "authority_ref", "display_classification"),
        Statement, "statement")
    values = _objects(root["values"], tuple(PairedValue.__dataclass_fields__),
                      PairedValue, "paired value")
    qualifications = _objects(root["qualifications"], tuple(QualificationEdge.__dataclass_fields__),
                              QualificationEdge, "qualification")

    provenance = []
    for item in root["provenance"] if type(root["provenance"]) is list else ():
        data = _exact_object(item, tuple(Provenance.__dataclass_fields__), "provenance")
        for name in ("package_identities", "target_refs"):
            if type(data[name]) is not list:
                raise PairedProfileRejected(f"provenance {name} requires an exact JSON array")
            data[name] = tuple(data[name])
        provenance.append(Provenance(**data))
    if type(root["provenance"]) is not list:
        raise PairedProfileRejected("provenance requires an exact JSON array")

    obligations = []
    for item in root["obligations"] if type(root["obligations"]) is list else ():
        data = _exact_object(item, tuple(Obligation.__dataclass_fields__), "obligation")
        if type(data["target_refs"]) is not list:
            raise PairedProfileRejected("obligation targets require an exact JSON array")
        data["target_refs"] = tuple(data["target_refs"])
        obligations.append(Obligation(**data))
    if type(root["obligations"]) is not list:
        raise PairedProfileRejected("obligations requires an exact JSON array")

    table_data = _exact_object(root["table"], tuple(PairedTable.__dataclass_fields__), "paired table")
    table_rows = []
    if type(table_data["rows"]) is not list:
        raise PairedProfileRejected("paired rows require an exact JSON array")
    for item in table_data["rows"]:
        data = _exact_object(item, tuple(PairedRow.__dataclass_fields__), "paired row")
        for name in ("qualification_refs", "provenance_refs"):
            if type(data[name]) is not list:
                raise PairedProfileRejected(f"row {name} requires an exact JSON array")
            data[name] = tuple(data[name])
        table_rows.append(PairedRow(**data))
    for name in ("column_identities", "column_headings"):
        if type(table_data[name]) is not list:
            raise PairedProfileRejected(f"table {name} requires an exact JSON array")
        table_data[name] = tuple(table_data[name])
    table_data["rows"] = tuple(table_rows)

    tuple_names = ("evidence_snapshots", "external_references", "content_authorities")
    pairs_names = ("renderer_requirements", "renderer_mappings")
    converted = {}
    for name in tuple_names:
        if type(root[name]) is not list:
            raise PairedProfileRejected(f"{name} requires an exact JSON array")
        converted[name] = tuple(root[name])
    for name in pairs_names:
        if type(root[name]) is not list or any(type(pair) is not list for pair in root[name]):
            raise PairedProfileRejected(f"{name} requires exact JSON pair arrays")
        converted[name] = tuple(tuple(pair) for pair in root[name])

    semantics = PairedSemanticInput(
        tuple(sections), statements, PairedTable(**table_data), values, qualifications,
        tuple(provenance), tuple(obligations), converted["evidence_snapshots"],
        converted["external_references"], converted["content_authorities"],
        converted["renderer_requirements"], converted["renderer_mappings"],
    )
    return validate_paired_semantics(semantics)


def validate_candidate_paired_semantics(bundle: object) -> PairedSemanticInput:
    """Reconstruct and validate the exact paired semantic extension from a Candidate bundle."""
    try:
        candidate = bundle.one(_CANDIDATE_KIND)
        extensions = candidate.extensions
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise PairedProfileRejected("Candidate bundle does not expose its exact Candidate") from exc
    if type(extensions) not in (list, tuple):
        raise PairedProfileRejected("Candidate extensions require an exact sequence")
    matches = [item for item in extensions if type(item) is dict and
               item.get("validation_contract") == _CORE_EXTENSION_CONTRACT and
               type(item.get("payload")) is dict and
               item["payload"].get("contract_identity") == PAIRED_SEMANTIC_VALIDATION_CONTRACT]
    if len(matches) != 1:
        raise PairedProfileRejected("Candidate requires one exact paired semantic extension")
    extension = matches[0]
    if set(extension) != _EXTENSION_KEYS or (
        extension.get("owner_namespace"), extension.get("name"), extension.get("version"),
        extension.get("authority_ref"), extension.get("scope"), extension.get("target_refs"),
        extension.get("criticality"), extension.get("character"), extension.get("preservation"),
    ) != (PAIRED_SEMANTIC_EXTENSION_OWNER, PAIRED_SEMANTIC_EXTENSION_NAME,
          PAIRED_SEMANTIC_EXTENSION_VERSION, extension.get("authority_ref"),
          _PAIRED_EXTENSION_SCOPE, [candidate.identity], "required", "semantic", "must-preserve"):
        raise PairedProfileRejected("paired semantic extension contract differs")
    payload = extension["payload"]
    if set(payload) != {"contract_identity", "contract_version", "canonical_semantics"} or (
            payload.get("contract_identity"), payload.get("contract_version")) != (
                PAIRED_SEMANTIC_VALIDATION_CONTRACT, PAIRED_SEMANTIC_EXTENSION_VERSION):
        raise PairedProfileRejected("paired semantic payload contract differs")
    try:
        semantics = _reconstruct_semantics(payload["canonical_semantics"])
    except (PairedSchemaRejected, AttributeError, KeyError, TypeError, ValueError) as exc:
        raise PairedProfileRejected(str(exc)) from exc
    if extension["authority_ref"] not in semantics.content_authorities:
        raise PairedProfileRejected("paired extension authority differs from semantic closure")
    return semantics


def paired_semantic_closure_fingerprint(semantics: PairedSemanticInput) -> str:
    """Return the exact source-neutral fingerprint of a validated paired semantic closure."""
    return _semantic_closure_fingerprint(validate_paired_semantics(semantics))


def _candidate_semantics(release: object) -> PairedSemanticInput:
    try:
        bundle = release.bundle
    except AttributeError as exc:
        raise PairedProfileRejected("verified Release does not expose its exact Candidate") from exc
    return validate_candidate_paired_semantics(bundle)


def paired_predecessor_prefix_fingerprint(documents: object) -> str:
    """Fingerprint the exact eight persisted BCRP documents without reinterpreting extensions."""
    if type(documents) is not tuple or len(documents) != 8 or any(type(item) is not dict for item in documents):
        raise PairedProfileRejected("exact eight-record predecessor document tuple required")
    encoded = json.dumps(list(documents), ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _token_state_fingerprint(token: PairedUpstreamAdmissionToken) -> str:
    """Fingerprint every authority-critical field using issuer-owned state."""
    document = {
        "bindings": list(token._bindings),
        "content_closure_fingerprint": token._content_closure_fingerprint,
        "semantics": asdict(token._semantics),
        "admission": asdict(token._admission),
        "authority_inventory": list(token._authority_inventory),
        "profile_admission_fingerprint": token._profile_admission_fingerprint,
        "plan_documents": list(token._plan_documents),
        "predecessor_prefix_fingerprint": token._predecessor_prefix_fingerprint,
        "capability_tuple": [list(item) for item in token._capability_tuple],
        "nonce": token._nonce.hex(),
    }
    return _fingerprint(document)


def _issue_upstream_token(semantics: PairedSemanticInput,
                          admission: PairedAdmissionEnvelope,
                          authority_inventory: tuple[dict, ...],
                          profile_admission_fingerprint: str,
                          plan: VerifiedRendererCompatibilityPlan) -> PairedUpstreamAdmissionToken:
    token = object.__new__(PairedUpstreamAdmissionToken)
    object.__setattr__(token, "_bindings", _envelope_bindings(admission))
    object.__setattr__(token, "_content_closure_fingerprint",
                       _semantic_closure_fingerprint(semantics))
    object.__setattr__(token, "_semantics", semantics)
    object.__setattr__(token, "_admission", admission)
    object.__setattr__(token, "_authority_inventory", authority_inventory)
    object.__setattr__(token, "_profile_admission_fingerprint", profile_admission_fingerprint)
    plan_documents = tuple(record.to_document() for record in plan.bundle.records)
    object.__setattr__(token, "_plan_documents", plan_documents)
    object.__setattr__(token, "_predecessor_prefix_fingerprint",
                       paired_predecessor_prefix_fingerprint(plan_documents))
    object.__setattr__(token, "_capability_tuple", PAIRED_CAPABILITY_TUPLE)
    object.__setattr__(token, "_nonce", secrets.token_bytes(_TOKEN_NONCE_BYTES))
    _issued_tokens.add(token)
    _issued_token_seals[token] = _token_state_fingerprint(token)
    return token


def consume_paired_upstream_admission(
    admitted: object,
) -> tuple[PairedSemanticInput, PairedAdmissionEnvelope]:
    """Return the exact issuer-held closure to trusted profile components only."""
    if type(admitted) is not PairedUpstreamAdmissionToken or admitted not in _issued_tokens:
        raise PairedProfileRejected("verified process-local upstream admission required")
    try:
        sealed = _issued_token_seals.get(admitted)
        actual = _token_state_fingerprint(admitted)
    except Exception as exc:
        raise PairedProfileRejected("admitted upstream closure was altered") from exc
    if sealed is None or actual != sealed:
        raise PairedProfileRejected("admitted upstream closure was altered")
    if (_semantic_closure_fingerprint(admitted._semantics) !=
            admitted._content_closure_fingerprint or
            _envelope_bindings(admitted._admission) != admitted._bindings):
        raise PairedProfileRejected("admitted upstream closure was altered")
    return admitted._semantics, admitted._admission


def paired_upstream_evidence_bindings(admitted: object) -> tuple[tuple[dict, ...], str]:
    """Expose immutable evidence inputs only after revalidating issuer closure."""
    consume_paired_upstream_admission(admitted)
    return (tuple(dict(item) for item in admitted._authority_inventory),
            admitted._profile_admission_fingerprint)


def paired_upstream_predecessor_bindings(admitted: object) -> tuple[tuple[dict, ...], str, tuple[tuple[str, str], ...]]:
    """Expose the exact admitted Plan prefix and frozen capability family."""
    consume_paired_upstream_admission(admitted)
    return (admitted._plan_documents, admitted._predecessor_prefix_fingerprint,
            admitted._capability_tuple)


def _verify_exact_paired_declaration(declaration: object) -> RendererCapabilityDeclaration:
    if type(declaration) is not RendererCapabilityDeclaration:
        raise PairedProfileRejected("exact RendererCapabilityDeclaration required")
    expected = {
        "identity": PAIRED_CAPABILITY_DECLARATION_IDENTITY,
        "contract_identity": CAPABILITY_DECLARATION_CONTRACT,
        "capability_profile_identity": ACCEPTED_DECLARATION_PROFILE_ID,
        "capability_profile_version": ACCEPTED_DECLARATION_PROFILE_VERSION,
        "renderer_identity": PAIRED_RENDERER_IDENTITY,
        "renderer_version": PAIRED_RENDERER_VERSION,
        "renderer_owner": ACCEPTED_RENDERER_OWNER,
        "renderer_role": ACCEPTED_RENDERER_ROLE,
        "inventory_complete": True, "unsupported_capabilities": (), "extensions": (),
    }
    if any(getattr(declaration, name, None) != value for name, value in expected.items()):
        raise PairedProfileRejected(
            "capability declaration differs from the exact paired renderer declaration")
    claims = tuple((item.identity, item.expression_mode,
                    item.constraints, item.supported)
                   for item in declaration.capabilities)
    if (claims != PAIRED_CAPABILITY_CLAIMS
            or declaration.declared_constraints != PAIRED_DETERMINISM_CONTROLS):
        raise PairedProfileRejected("paired renderer capability inventory differs from the exact closed declaration")
    if declaration.fingerprint != compute_capability_declaration_fingerprint(declaration):
        raise PairedProfileRejected("paired capability declaration fingerprint is stale")
    return declaration


def _verify_exact_paired_plan(plan: object, declaration: RendererCapabilityDeclaration) -> VerifiedRendererCompatibilityPlan:
    if type(plan) is not VerifiedRendererCompatibilityPlan or len(plan.bundle.records) != 8:
        raise PairedProfileRejected("exact verified eight-record paired Plan required")
    capability = plan.bundle.one("RendererCapabilityDeclarationRecord")
    record = plan.plan
    if (capability.identity != declaration.identity
            or capability.semantic.get("declaration_identity") != declaration.identity
            or capability.semantic.get("renderer_id") != PAIRED_RENDERER_IDENTITY
            or capability.semantic.get("renderer_version") != PAIRED_RENDERER_VERSION
            or tuple(capability.semantic.get("capabilities", ())) !=
               tuple(item.identity for item in declaration.capabilities)
            or record.semantic.get("renderer_capability_ref") != declaration.identity
            or record.semantic.get("supported") is not True):
        raise PairedProfileRejected(
            "Plan does not bind the exact paired capability declaration and renderer")
    return plan


def verify_paired_upstream_admission_token(
    token: object, *, projection: object,
) -> PairedUpstreamAdmissionToken:
    """Fail closed unless the admitted closure binds this exact projection."""
    semantics, admission = consume_paired_upstream_admission(token)
    names = ("profile_identity", "profile_version", "release_identity", "release_fingerprint",
             "lifecycle_scope_fingerprint", "plan_identity", "plan_fingerprint",
             "capability_declaration_identity", "capability_declaration_fingerprint")
    try:
        bindings = tuple(getattr(projection, name) for name in names)
        closure = getattr(projection, "content_closure_fingerprint")
    except AttributeError as exc:
        raise PairedProfileRejected("token target is not an exact paired projection") from exc
    if bindings != _envelope_bindings(admission) or closure != _semantic_closure_fingerprint(semantics):
        raise PairedProfileRejected("upstream admission does not bind this projection")
    return token


def admit_paired_terminal_semantics(
    semantics: PairedSemanticInput, *, admission: PairedAdmissionEnvelope
) -> PairedSemanticInput:
    """Validate a DTO/envelope pair only; this does not grant projection authority."""
    try:
        if type(admission) is not PairedAdmissionEnvelope:
            raise PairedSchemaRejected("exact paired admission envelope required")
        validate_admission_envelope(admission)
        if admission.capability_declaration_identity != PAIRED_CAPABILITY_DECLARATION_IDENTITY:
            raise PairedSchemaRejected("capability declaration is not the exact paired renderer binding")
        return validate_paired_semantics(semantics)
    except (PairedSchemaRejected, AttributeError, TypeError) as exc:
        raise PairedProfileRejected(str(exc)) from exc


def verify_full_upstream_paired_terminal_admission(
    *, release_bundle, evidence_snapshot, lifecycle_scope, declaration,
    planning_authorization, plan_bundle,
) -> PairedUpstreamAdmissionToken:
    """Verify upstream authorities and admit semantics reconstructed from Release.

    Neither semantic DTOs nor digest envelopes are caller inputs.  The verified
    Release's Candidate extension is the sole semantic source.
    """
    try:
        release = verify_publication_release(
            release_bundle, evidence_snapshot=evidence_snapshot)
        plan = verify_renderer_compatibility_plan(
            plan_bundle, evidence_snapshot=evidence_snapshot,
            lifecycle_scope=lifecycle_scope, declaration=declaration,
            authorization=planning_authorization)
        declaration = _verify_exact_paired_declaration(declaration)
        plan = _verify_exact_paired_plan(plan, declaration)
        admission = PairedAdmissionEnvelope(
            PROFILE_IDENTITY, PROFILE_VERSION, release.release.identity,
            release.fingerprint.digest, getattr(lifecycle_scope, "inventory_digest"),
            plan.plan.identity, plan.fingerprint.digest, declaration.identity,
            declaration.fingerprint,
        )
        validate_admission_envelope(admission)
        if admission.capability_declaration_identity != PAIRED_CAPABILITY_DECLARATION_IDENTITY:
            raise PairedProfileRejected("capability declaration is not the exact paired renderer binding")
        semantics = _candidate_semantics(release)
        authority_inventory, profile_fingerprint = _release_authority_admission(release, semantics)
        return _issue_upstream_token(
            semantics, admission, authority_inventory, profile_fingerprint, plan)
    except PairedProfileRejected:
        raise
    except Exception as exc:
        raise PairedProfileRejected(str(exc)) from exc
