"""TASK-052 fixed renderer invocation and non-conformance artifact evidence.

This specialized boundary consumes an independently reproduced TASK-051 Plan,
invokes only the fixed minimal HTML renderer, and records artifact existence and
invocation/audit links. It deliberately cannot create conformance, Manifest,
distribution, or successful-publication authority.

Trust boundary: authorization construction and ledger ownership remain inside the
trusted BriefForge process and trusted local-filesystem writer boundary. The hash
bindings are consistency and tamper-detection controls, not human authentication,
digital signatures, WORM storage, or external sandbox attestation.
"""
from __future__ import annotations

from copy import deepcopy
import ctypes
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import threading
from types import CodeType, FunctionType
from typing import Any

from .bcrp.canonical import fingerprint_bundle
from .bcrp.model import BCRPBundle, BCRPRecord, Fingerprint, PROFILE_VERSION
from .bcrp.validation import validate_bundle
from .publication_release import EvidenceSnapshot, VerifiedPublicationRelease
from .renderer_adapter import (
    MinimalHtmlProjectionEncounter,
    MinimalHtmlProjectionIdentity,
    MinimalHtmlProjectionObligation,
    MinimalHtmlProjectionPurpose,
    MinimalHtmlProjectionReference,
    MinimalHtmlProjectionStatement,
    MinimalHtmlRendererProjection,
    html_renderer_contract,
)
from .renderer_compatibility_planning import (
    LifecyclePlanningScope,
    PlanningAuthorization,
    RendererCapabilityDeclaration,
    VerifiedRendererCompatibilityPlan,
    verify_renderer_compatibility_plan,
)

CONTROLLED_INVOCATION_POLICY_ID = "briefforge-controlled-renderer-invocation-policy:1.0.0"
INVOCATION_EXTENSION_CONTRACT = "briefforge:controlled-renderer-invocation-evidence:1.0.0"
ACCEPTED_INVOCATION_AUTHORITY_IDENTITY = "authority:briefforge-controlled-renderer-invocation"
ACCEPTED_INVOCATION_AUTHORITY_OWNER = "project:BriefForge"
ACCEPTED_INVOCATION_AUTHORITY_ROLE = "renderer-invocation-authority"
FIXED_RENDERER_IDENTITY = "renderer:minimal-html"
_FIXED_OUTPUT_FILENAME = "publication.html"
_FIXED_EVIDENCE_FILENAME = "invocation-evidence.json"
_FIXED_MEDIA_TYPE = "text/html"
_FIXED_ENVIRONMENT = (
    ("LANG", "C"), ("LC_ALL", "C"), ("TZ", "UTC"),
    ("PYTHONDONTWRITEBYTECODE", "1"), ("PYTHONHASHSEED", "0"), ("PYTHONUTF8", "1"),
)
_FIXED_MODE = "one-artifact-with-determinism-replay"
_FIXED_INTERPRETER_FLAGS = ("-B", "-s", "-S", "-X", "utf8")
_EXECUTION_LOCK = threading.Lock()


@dataclass(frozen=True, order=True)
class InvocationFinding:
    code: str
    location: str
    message: str


@dataclass(frozen=True)
class RendererInvocationAuthorization:
    identity: str
    policy_identity: str
    authority_identity: str
    authority_owner: str
    authority_role: str
    authorization_time: str
    release_identity: str
    release_fingerprint: str
    lifecycle_inventory_digest: str
    plan_identity: str
    plan_fingerprint: str
    capability_identity: str
    capability_fingerprint: str
    renderer_identity: str
    renderer_adapter_id: str
    renderer_version: str
    renderer_implementation_digest: str
    projection_fingerprint: str
    authorization_ledger_directory: str
    output_directory: str
    output_filename: str
    output_count: int
    maximum_output_bytes: int
    media_type: str
    environment: tuple[tuple[str, str], ...]
    external_assets: tuple[str, ...]
    invocation_mode: str
    timeout_seconds: int
    evidence_filename: str
    fingerprint: str


@dataclass(frozen=True)
class VerifiedRendererInvocation:
    _bundle_document: str
    _artifact_bytes: bytes
    fingerprint: Fingerprint

    @property
    def bundle(self) -> BCRPBundle:
        return _deserialize_bundle(self._bundle_document)

    @property
    def artifact_bytes(self) -> bytes:
        return bytes(self._artifact_bytes)


@dataclass(frozen=True)
class ControlledInvocationResult:
    findings: tuple[InvocationFinding, ...]
    verified: VerifiedRendererInvocation | None

    @property
    def blocked(self) -> bool:
        return self.verified is None


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class _StandaloneHtmlPolicyParser(HTMLParser):
    _FORBIDDEN_TAGS = frozenset({
        "applet", "audio", "base", "embed", "frame", "frameset", "iframe",
        "img", "link", "object", "script", "source", "track", "video",
    })
    _URI_ATTRIBUTES = frozenset({
        "action", "background", "cite", "data", "formaction", "href", "manifest",
        "ping", "poster", "src", "srcdoc", "srcset", "xlink:href",
    })

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.doctypes = 0
        self.root_starts = 0
        self.root_ends = 0
        self.in_style = False

    def handle_decl(self, decl: str) -> None:
        if decl.lower() != "doctype html":
            raise ValueError("HTML output contains an unauthorized declaration.")
        self.doctypes += 1

    def handle_pi(self, data: str) -> None:
        raise ValueError("HTML output contains an unauthorized processing instruction.")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in self._FORBIDDEN_TAGS:
            raise ValueError(f"HTML output contains prohibited active or resource element <{tag}>.")
        if tag == "html":
            self.root_starts += 1
        if tag == "style":
            self.in_style = True
        normalized = {name.lower(): value for name, value in attrs}
        if any(name.startswith("on") for name in normalized):
            raise ValueError("HTML output contains a prohibited event-handler attribute.")
        for name, value in normalized.items():
            if name not in self._URI_ATTRIBUTES:
                continue
            if name == "href" and value is not None and re.fullmatch(r"#[A-Za-z0-9:._-]+", value):
                continue
            raise ValueError(f"HTML output contains prohibited URI-bearing attribute {name}.")
        if "style" in normalized:
            raise ValueError("HTML output contains an unauthorized inline style attribute.")
        if tag == "meta" and normalized.get("http-equiv", "").lower() == "refresh":
            raise ValueError("HTML output contains a prohibited meta refresh.")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() == "style":
            self.in_style = False

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "html":
            self.root_ends += 1
        if tag == "style":
            self.in_style = False

    def handle_data(self, data: str) -> None:
        if self.in_style and re.search(r"(?:@import|url\s*\(|expression\s*\()", data, re.IGNORECASE):
            raise ValueError("HTML output contains a prohibited CSS resource or executable expression.")



def _verify_standalone_html(artifact_bytes: bytes) -> None:
    try:
        document = artifact_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("HTML output is not strict UTF-8.") from exc
    if "\r" in document or "\x00" in document:
        raise ValueError("HTML output violates the authorized LF-only text encoding policy.")
    if not document.startswith("<!doctype html>\n<html lang=\"en\">\n<head>\n") or not document.endswith("</html>"):
        raise ValueError("Renderer output is not the authorized standalone HTML document shape.")
    parser = _StandaloneHtmlPolicyParser()
    parser.feed(document)
    parser.close()
    if parser.doctypes != 1 or parser.root_starts != 1 or parser.root_ends != 1:
        raise ValueError("Renderer output does not contain exactly one HTML doctype and root element.")


def _stable_code_document(code: CodeType) -> dict[str, Any]:
    def constant(value: Any) -> Any:
        if isinstance(value, CodeType):
            return {"code": _stable_code_document(value)}
        if isinstance(value, bytes):
            return {"bytes": value.hex()}
        if isinstance(value, tuple):
            return {"tuple": [constant(item) for item in value]}
        if isinstance(value, frozenset):
            items = [constant(item) for item in value]
            return {"frozenset": sorted(items, key=lambda item: json.dumps(item, sort_keys=True))}
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        raise TypeError(f"Unsupported renderer code constant type: {type(value).__name__}")

    return {
        "argcount": code.co_argcount,
        "posonlyargcount": code.co_posonlyargcount,
        "kwonlyargcount": code.co_kwonlyargcount,
        "nlocals": code.co_nlocals,
        "stacksize": code.co_stacksize,
        "flags": code.co_flags,
        "code": code.co_code.hex(),
        "consts": [constant(item) for item in code.co_consts],
        "names": list(code.co_names),
        "varnames": list(code.co_varnames),
        "freevars": list(code.co_freevars),
        "cellvars": list(code.co_cellvars),
    }


def renderer_implementation_digest() -> str:
    """Bind renderer source and the complete loaded local-function call graph."""
    from . import renderer_adapter as renderer_module

    source = Path(renderer_module.__file__).read_bytes()
    pending = [renderer_module.render_minimal_html_projection]
    discovered: dict[str, FunctionType] = {}
    bindings: set[tuple[str, str, str, str]] = set()
    while pending:
        function = pending.pop()
        qualified_name = f"{function.__module__}.{function.__qualname__}"
        if qualified_name in discovered:
            continue
        discovered[qualified_name] = function
        for name in function.__code__.co_names:
            dependency = function.__globals__.get(name)
            if isinstance(dependency, FunctionType):
                bindings.add((qualified_name, name, dependency.__module__, dependency.__qualname__))
                pending.append(dependency)
            elif dependency is not None and callable(dependency):
                if type(dependency) is not type or dependency.__module__ != renderer_module.__name__:
                    raise ValueError(
                        f"Renderer call graph contains unsupported executable binding {qualified_name}:{name}."
                    )
                bindings.add((
                    qualified_name,
                    name,
                    dependency.__module__,
                    dependency.__qualname__,
                ))
    graph = bytearray(source)
    graph.extend(b"\0bindings\0")
    graph.extend(_canonical_bytes(sorted(bindings)))
    for qualified_name, function in sorted(discovered.items()):
        graph.extend(b"\0")
        graph.extend(qualified_name.encode("utf-8"))
        graph.extend(b"\0")
        graph.extend(_canonical_bytes(_stable_code_document(function.__code__)))
    graph.extend(b"\0worker-source\0")
    graph.extend(Path(__file__).with_name("_controlled_renderer_worker.py").read_bytes())
    projection_loader = globals().get("_projection_from_document")
    if isinstance(projection_loader, FunctionType):
        graph.extend(b"\0projection-loader\0")
        graph.extend(_canonical_bytes(_stable_code_document(projection_loader.__code__)))
    return _sha256(bytes(graph))


def compute_invocation_authorization_fingerprint(authorization: RendererInvocationAuthorization) -> str:
    if type(authorization) is not RendererInvocationAuthorization:
        raise TypeError("Exact renderer invocation authorization is required.")
    document = asdict(authorization)
    document.pop("fingerprint", None)
    return _sha256(_canonical_bytes(document))


def _serialize_bundle(bundle: BCRPBundle) -> str:
    return json.dumps(
        {"profile_identity": bundle.profile_identity, "profile_version": bundle.profile_version,
         "records": [record.to_document() for record in bundle.records]},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
    )


def _deserialize_bundle(text: str) -> BCRPBundle:
    document = json.loads(text)
    if not isinstance(document, dict) or set(document) != {"profile_identity", "profile_version", "records"}:
        raise ValueError("Persisted invocation evidence envelope is malformed.")
    if not isinstance(document["records"], list):
        raise ValueError("Persisted invocation evidence record inventory is malformed.")
    return BCRPBundle(
        document["profile_identity"], document["profile_version"],
        tuple(BCRPRecord.from_document(item) for item in document["records"]),
    )


def _reverify_plan(
    *,
    verified_release: VerifiedPublicationRelease,
    evidence_snapshot: EvidenceSnapshot,
    lifecycle_scope: LifecyclePlanningScope,
    declaration: RendererCapabilityDeclaration,
    planning_authorization: PlanningAuthorization,
    verified_plan: VerifiedRendererCompatibilityPlan,
) -> VerifiedRendererCompatibilityPlan:
    if type(verified_release) is not VerifiedPublicationRelease:
        raise ValueError("Exact independently verified Publication Release is required.")
    if type(verified_plan) is not VerifiedRendererCompatibilityPlan:
        raise ValueError("Exact independently verified renderer Plan is required.")
    from .publication_release import verify_publication_release
    release = verify_publication_release(
        verified_release.bundle,
        evidence_snapshot=evidence_snapshot,
        expected_release_fingerprint=verified_release.fingerprint.digest,
    )
    reproduced = verify_renderer_compatibility_plan(
        verified_plan.bundle, evidence_snapshot=evidence_snapshot, lifecycle_scope=lifecycle_scope,
        declaration=declaration, authorization=planning_authorization,
        expected_plan_fingerprint=verified_plan.fingerprint.digest,
    )
    if (
        verified_plan._bundle_document != reproduced._bundle_document
        or verified_plan.mappings_document != reproduced.mappings_document
        or verified_plan.fingerprint != reproduced.fingerprint
    ):
        raise ValueError("Persisted renderer Plan bytes or mapping inventory differ from independent reverification.")
    if (
        tuple(record.to_document() for record in reproduced.bundle.records[:6])
        != tuple(record.to_document() for record in release.bundle.records)
    ):
        raise ValueError("Verified Release input differs from the exact Plan-bound Release closure.")
    return reproduced


def build_minimal_html_projection(
    *,
    verified_release: VerifiedPublicationRelease,
    evidence_snapshot: EvidenceSnapshot,
    lifecycle_scope: LifecyclePlanningScope,
    declaration: RendererCapabilityDeclaration,
    planning_authorization: PlanningAuthorization,
    verified_plan: VerifiedRendererCompatibilityPlan,
) -> MinimalHtmlRendererProjection:
    """Independently reverify and project one exact Plan without legacy Ready input."""

    plan = _reverify_plan(
        verified_release=verified_release, evidence_snapshot=evidence_snapshot,
        lifecycle_scope=lifecycle_scope, declaration=declaration,
        planning_authorization=planning_authorization, verified_plan=verified_plan,
    )
    contract = html_renderer_contract()
    if (
        type(declaration) is not RendererCapabilityDeclaration
        or declaration.renderer_identity != FIXED_RENDERER_IDENTITY
        or declaration.renderer_version != contract.identity.version
        or declaration.renderer_owner != "project:BriefForge"
        or declaration.renderer_role != "bounded-publication-renderer"
        or declaration.inventory_complete is not True
    ):
        raise ValueError("Capability declaration does not bind the exact fixed renderer implementation.")
    exact_constraints = {"no-external-assets", "no-runtime-detection", "single-regular-html", "standalone-only"}
    if set(declaration.declared_constraints) != exact_constraints or declaration.unsupported_capabilities:
        raise ValueError("Fixed renderer capability declaration is incomplete or contradictory.")

    bundle = plan.bundle
    candidate = bundle.one("CandidatePresentationPackageRecord")
    brief = bundle.one("PresentationBriefRecord")
    material = bundle.one("PortablePresentationMaterialRecord")
    judgment = bundle.one("ValidationJudgmentRecord")
    mappings = json.loads(plan.mappings_document)
    requirements = {item["id"]: item for item in candidate.semantic["renderer_requirements"]}
    if len(mappings) != len(requirements) or {item.get("requirement_id") for item in mappings} != set(requirements):
        raise ValueError("Plan mappings do not consume every renderer requirement exactly once.")
    if any(item.get("selected_expression_mode") != "native" for item in mappings):
        raise ValueError("The fixed renderer invocation accepts only Plan-selected native expression mappings.")
    for item in mappings:
        requirement = requirements[item["requirement_id"]]
        if item.get("capability_id") != requirement.get("capability"):
            raise ValueError("Plan selected capability does not match the exact Candidate requirement.")
        if item.get("affected_semantic_identities") != requirement.get("target_refs"):
            raise ValueError("Plan affected semantic identities drifted from the Candidate requirement.")
    planned_semantic_identities = {
        identity
        for mapping in mappings
        for identity in mapping["affected_semantic_identities"]
    }
    purpose_identity = candidate.semantic["organizing_purpose"]["id"]
    statement_identities = {item["id"] for item in candidate.semantic.get("statements", [])}
    obligation_identities = {item["id"] for item in candidate.semantic.get("obligations", [])}
    projected_semantic_identities = {purpose_identity} | statement_identities | obligation_identities
    if planned_semantic_identities != projected_semantic_identities:
        raise ValueError("Plan mappings do not cover the exact semantic material projected to the renderer.")
    claims = {claim.identity: claim for claim in declaration.capabilities}
    if set(claims) != {requirement["capability"] for requirement in requirements.values()}:
        raise ValueError("Fixed renderer declaration contains missing or undeclared capability claims.")
    if any(claim.expression_mode != "native" or claim.supported is not True for claim in claims.values()):
        raise ValueError("Fixed renderer native capability support is incomplete.")

    authorities = {item["id"]: item for item in material.semantic.get("authorities", [])}
    provenance = {item["id"]: item for item in material.semantic.get("provenance", [])}
    external = material.semantic.get("external_references", [])
    invocation_authority = authorities.get(ACCEPTED_INVOCATION_AUTHORITY_IDENTITY)
    if invocation_authority != {
        "id": ACCEPTED_INVOCATION_AUTHORITY_IDENTITY,
        "owner_identity": ACCEPTED_INVOCATION_AUTHORITY_OWNER,
        "role": ACCEPTED_INVOCATION_AUTHORITY_ROLE,
        "scope": "one-controlled-renderer-invocation-act",
    }:
        raise ValueError("Governed material does not contain the exact invocation authority binding.")
    statements_source = candidate.semantic.get("statements", [])
    obligations_source = candidate.semantic.get("obligations", [])
    required_reference_ids = {
        reference
        for statement in statements_source
        for reference in statement.get("upstream_refs", [])
    }
    if {item["id"] for item in external} != required_reference_ids:
        raise ValueError("Projected external references differ from the Plan-covered statement linkage closure.")
    if any(item.get("authority_ref") not in authorities for item in statements_source + obligations_source + external):
        raise ValueError("Projected semantic material contains an unresolved authority reference.")
    if any(item.get("provenance_ref") not in provenance for item in external):
        raise ValueError("Projected external material contains an unresolved provenance reference.")
    references = tuple(
        MinimalHtmlProjectionReference(
            reference_id=item["id"],
            owning_project=authorities.get(item.get("authority_ref"), {}).get("owner_identity", "unknown"),
            reference_kind=item.get("reference_kind", "external-reference"),
            locator=item.get("upstream_object_identity", item["id"]),
            owned_meaning=f"{item.get('authority_ref', 'unknown')} | {item.get('snapshot_ref', 'unknown')}",
            provenance_ref=item.get("provenance_ref", "unknown"),
            provenance_citation=provenance.get(item.get("provenance_ref"), {}).get("citation", "unknown"),
        )
        for item in external
    )
    obligations = tuple(
        MinimalHtmlProjectionObligation(
            obligation_id=item["id"], category=item.get("kind", "presentation-obligation"),
            requirement=item.get("kind", item["id"]), authority_ref=item.get("authority_ref", "unknown"),
            applies_to=tuple(item.get("target_refs", [])),
        )
        for item in obligations_source
    )
    statements_by_id = {item["id"]: item for item in candidate.semantic.get("statements", [])}
    encounter_order = [
        child for section in candidate.semantic.get("sections", []) for child in section.get("children", [])
        if child in statements_by_id
    ]
    if len(encounter_order) != len(statements_by_id) or len(set(encounter_order)) != len(encounter_order):
        raise ValueError("Candidate encounter order does not include every statement exactly once.")
    statements = tuple(
        MinimalHtmlProjectionStatement(
            statement_id=identity,
            encounter_meaning=statements_by_id[identity]["text"],
            encounter_semantics=MinimalHtmlProjectionEncounter(
                mode=statements_by_id[identity].get("posture", "observation"),
                description=",".join(statements_by_id[identity].get("communication_functions", []))
                or statements_by_id[identity].get("posture", "observation"),
            ),
            authority_ref=statements_by_id[identity].get("authority_ref", "unknown"),
            upstream_reference_ids=tuple(statements_by_id[identity].get("upstream_refs", [])),
            obligation_ids=tuple(item["id"] for item in obligations_source if identity in item.get("target_refs", [])),
        )
        for identity in encounter_order
    )
    sections = candidate.semantic.get("sections", [])
    purpose = candidate.semantic["organizing_purpose"]
    projection_without_fingerprint = {
        "identity": {"package_id": candidate.identity,
                     "title": sections[0].get("title", candidate.identity) if sections else candidate.identity,
                     "purpose_summary": candidate.semantic.get("scope", brief.semantic.get("scope", ""))},
        "organizing_purpose": {"statement": purpose["statement"],
                               "non_scope": candidate.semantic.get("non_scope", brief.semantic.get("non_scope", ""))},
        "statements": [asdict(item) for item in statements],
        "upstream_references": [asdict(item) for item in references],
        "obligations": [asdict(item) for item in obligations],
        "semantic_fingerprint": judgment.semantic["candidate_fingerprint"],
        "validation_policy_id": judgment.semantic["policy_id"],
        "consumed_mapping_ids": [item["requirement_id"] for item in mappings],
        "selected_expression_modes": [item["selected_expression_mode"] for item in mappings],
    }
    return MinimalHtmlRendererProjection(
        identity=MinimalHtmlProjectionIdentity(**projection_without_fingerprint["identity"]),
        organizing_purpose=MinimalHtmlProjectionPurpose(**projection_without_fingerprint["organizing_purpose"]),
        statements=statements, upstream_references=references, obligations=obligations,
        semantic_fingerprint=projection_without_fingerprint["semantic_fingerprint"],
        validation_policy_id=projection_without_fingerprint["validation_policy_id"],
        consumed_mapping_ids=tuple(projection_without_fingerprint["consumed_mapping_ids"]),
        selected_expression_modes=tuple(projection_without_fingerprint["selected_expression_modes"]),
        fingerprint=_sha256(_canonical_bytes(projection_without_fingerprint)),
    )


def _authorization_problems(
    authorization: RendererInvocationAuthorization,
    *,
    verified_release: VerifiedPublicationRelease,
    lifecycle_scope: LifecyclePlanningScope,
    declaration: RendererCapabilityDeclaration,
    plan: VerifiedRendererCompatibilityPlan,
    projection: MinimalHtmlRendererProjection,
) -> list[InvocationFinding]:
    if type(authorization) is not RendererInvocationAuthorization:
        return [InvocationFinding("invalid-authorization", "/authorization", "Exact invocation authorization is required.")]
    string_fields = (
        "identity", "policy_identity", "authority_identity", "authority_owner", "authority_role",
        "authorization_time", "release_identity", "release_fingerprint", "lifecycle_inventory_digest",
        "plan_identity", "plan_fingerprint", "capability_identity", "capability_fingerprint",
        "renderer_identity", "renderer_adapter_id", "renderer_version", "renderer_implementation_digest",
        "projection_fingerprint", "authorization_ledger_directory", "output_directory", "output_filename",
        "media_type", "invocation_mode", "evidence_filename", "fingerprint",
    )
    malformed_fields = [name for name in string_fields if type(getattr(authorization, name)) is not str]
    if type(authorization.output_count) is not int:
        malformed_fields.append("output_count")
    if type(authorization.maximum_output_bytes) is not int:
        malformed_fields.append("maximum_output_bytes")
    if type(authorization.timeout_seconds) is not int:
        malformed_fields.append("timeout_seconds")
    if (
        type(authorization.environment) is not tuple
        or any(
            type(item) is not tuple or len(item) != 2 or any(type(value) is not str for value in item)
            for item in authorization.environment
        )
    ):
        malformed_fields.append("environment")
    if type(authorization.external_assets) is not tuple or any(
        type(value) is not str for value in authorization.external_assets
    ):
        malformed_fields.append("external_assets")
    if malformed_fields:
        return [InvocationFinding(
            "invalid-authorization-field-type", "/authorization",
            f"Authorization fields have invalid runtime types: {','.join(sorted(malformed_fields))}.",
        )]
    contract = html_renderer_contract()
    expected = {
        "policy_identity": CONTROLLED_INVOCATION_POLICY_ID,
        "authority_identity": ACCEPTED_INVOCATION_AUTHORITY_IDENTITY,
        "authority_owner": ACCEPTED_INVOCATION_AUTHORITY_OWNER,
        "authority_role": ACCEPTED_INVOCATION_AUTHORITY_ROLE,
        "release_identity": verified_release.release.identity,
        "release_fingerprint": verified_release.fingerprint.digest,
        "lifecycle_inventory_digest": lifecycle_scope.inventory_digest,
        "plan_identity": plan.plan.identity,
        "plan_fingerprint": plan.fingerprint.digest,
        "capability_identity": declaration.identity,
        "capability_fingerprint": declaration.fingerprint,
        "renderer_identity": FIXED_RENDERER_IDENTITY,
        "renderer_adapter_id": contract.identity.adapter_id,
        "renderer_version": contract.identity.version,
        "renderer_implementation_digest": renderer_implementation_digest(),
        "projection_fingerprint": projection.fingerprint,
        "output_filename": _FIXED_OUTPUT_FILENAME,
        "output_count": 1,
        "media_type": _FIXED_MEDIA_TYPE,
        "environment": _FIXED_ENVIRONMENT,
        "external_assets": (),
        "invocation_mode": _FIXED_MODE,
        "evidence_filename": _FIXED_EVIDENCE_FILENAME,
    }
    findings = [
        InvocationFinding("authorization-mismatch", f"/authorization/{name}", f"Authorization {name} does not bind the exact invocation act.")
        for name, value in expected.items() if getattr(authorization, name) != value
    ]
    if authorization.fingerprint != compute_invocation_authorization_fingerprint(authorization):
        findings.append(InvocationFinding("authorization-fingerprint-mismatch", "/authorization/fingerprint", "Authorization fingerprint is stale or wrong."))
    if type(authorization.maximum_output_bytes) is not int or not 1 <= authorization.maximum_output_bytes <= 10_000_000:
        findings.append(InvocationFinding("invalid-output-size-bound", "/authorization/maximum_output_bytes", "Output byte bound is invalid."))
    if type(authorization.timeout_seconds) is not int or not 1 <= authorization.timeout_seconds <= 30:
        findings.append(InvocationFinding("invalid-timeout-bound", "/authorization/timeout_seconds", "Renderer timeout bound is invalid."))
    if (
        not authorization.identity
        or not re.fullmatch(r"[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*", authorization.identity)
        or not authorization.authorization_time
    ):
        findings.append(InvocationFinding("invalid-authorization", "/authorization", "Authorization identity must be canonical and authorization time is required."))
    else:
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", authorization.authorization_time):
                raise ValueError
            parsed_time = datetime.strptime(authorization.authorization_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if parsed_time.isoformat().replace("+00:00", "Z") != authorization.authorization_time:
                raise ValueError
        except (TypeError, ValueError):
            findings.append(InvocationFinding("invalid-authorization-time", "/authorization/authorization_time", "Authorization time must be a canonical real UTC second."))
    return findings


def _output_directory_problems(path_text: str) -> tuple[Path | None, list[InvocationFinding]]:
    findings: list[InvocationFinding] = []
    try:
        path = Path(path_text)
        if not path.is_absolute() or str(path.resolve()) != path_text:
            raise ValueError
        if path.is_symlink() or not path.is_dir():
            raise ValueError
        if any(path.iterdir()):
            findings.append(InvocationFinding("output-directory-not-empty", "/output-directory", "Authorized output directory must be empty."))
        return path, findings
    except (OSError, TypeError, ValueError):
        return None, [InvocationFinding("invalid-output-directory", "/output-directory", "Authorized output directory is absent, non-canonical, or unsafe.")]


def _open_directory_fd(path: Path) -> int:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise ValueError("Authorized output path is not a directory.")
    return descriptor


def _create_staging_directory(parent_fd: int, prefix: str) -> str:
    for _ in range(64):
        name = f"{prefix}{os.urandom(12).hex()}"
        try:
            os.mkdir(name, mode=0o700, dir_fd=parent_fd)
        except FileExistsError:
            continue
        os.fsync(parent_fd)
        return name
    raise FileExistsError("Unable to allocate an exclusive bounded staging directory.")


def _raw_exchange_directories(parent_fd: int, left_name: str, right_name: str) -> None:
    renameat2 = ctypes.CDLL(None, use_errno=True).renameat2
    renameat2.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)
    renameat2.restype = ctypes.c_int
    if renameat2(parent_fd, os.fsencode(left_name), parent_fd, os.fsencode(right_name), 2) != 0:
        error_number = ctypes.get_errno()
        raise OSError(error_number, os.strerror(error_number))


def _raw_rename_noreplace(parent_fd: int, source_name: str, destination_name: str) -> None:
    renameat2 = ctypes.CDLL(None, use_errno=True).renameat2
    renameat2.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)
    renameat2.restype = ctypes.c_int
    if renameat2(parent_fd, os.fsencode(source_name), parent_fd, os.fsencode(destination_name), 1) != 0:
        error_number = ctypes.get_errno()
        raise OSError(error_number, os.strerror(error_number))


def _remove_rejected_directory(parent_fd: int, name: str, expected_identity: tuple[int, int]) -> None:
    descriptor = os.open(
        name,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
        dir_fd=parent_fd,
    )
    try:
        info = os.fstat(descriptor)
        if (info.st_dev, info.st_ino) != expected_identity:
            raise ValueError("Rejected output directory identity changed before cleanup.")
        names = os.listdir(descriptor)
        if len(names) > 16:
            raise ValueError("Rejected output directory exceeds the bounded cleanup inventory.")
        for child_name in names:
            _read_regular(descriptor, child_name)
        for child_name in names:
            os.unlink(child_name, dir_fd=descriptor)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.rmdir(name, dir_fd=parent_fd)
    os.fsync(parent_fd)


def _exchange_directories(parent_fd: int, left_name: str, right_name: str) -> None:
    """Single audited publication exchange seam; rollback does not re-enter it."""
    _raw_exchange_directories(parent_fd, left_name, right_name)


def _cleanup_exchanged_original(parent_fd: int, name: str, expected_identity: tuple[int, int]) -> None:
    descriptor = os.open(
        name,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
        dir_fd=parent_fd,
    )
    try:
        info = os.fstat(descriptor)
        if (info.st_dev, info.st_ino) != expected_identity or os.listdir(descriptor):
            raise ValueError("Exchanged original output directory is not the expected empty inode.")
    finally:
        os.close(descriptor)
    os.rmdir(name, dir_fd=parent_fd)
    os.fsync(parent_fd)


def _write_regular_exclusive(directory_fd: int, name: str, data: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(name, flags, 0o600, dir_fd=directory_fd)
    try:
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short output write")
            view = view[written:]
        os.fsync(descriptor)
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError("Persisted output is not a regular file.")
    finally:
        os.close(descriptor)


def _read_regular(directory_fd: int, name: str, *, maximum_bytes: int = 10_000_000) -> bytes:
    descriptor = os.open(
        name,
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0),
        dir_fd=directory_fd,
    )
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("Persisted output is not a regular file.")
        if info.st_size > maximum_bytes:
            raise ValueError("Persisted output exceeds the bounded read limit.")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(1024 * 1024, maximum_bytes + 1 - total))
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
            total += len(chunk)
            if total > maximum_bytes:
                raise ValueError("Persisted output exceeds the bounded read limit.")
    finally:
        os.close(descriptor)


def _unlink_if_present(directory_fd: int, name: str) -> None:
    try:
        os.unlink(name, dir_fd=directory_fd)
    except FileNotFoundError:
        pass


def _consume_authorization(authorization: RendererInvocationAuthorization) -> InvocationFinding | None:
    try:
        ledger_path = Path(authorization.authorization_ledger_directory)
        if (
            not ledger_path.is_absolute()
            or str(ledger_path.resolve()) != authorization.authorization_ledger_directory
            or ledger_path.is_symlink()
            or not ledger_path.is_dir()
            or ledger_path == Path(authorization.output_directory)
        ):
            raise ValueError("Authorization ledger directory is absent, non-canonical, or unsafe.")
        ledger_fd = _open_directory_fd(ledger_path)
        try:
            marker_name = f"{authorization.fingerprint}.consumed"
            _write_regular_exclusive(ledger_fd, marker_name, authorization.fingerprint.encode("ascii"))
            os.fsync(ledger_fd)
        finally:
            os.close(ledger_fd)
        return None
    except FileExistsError:
        return InvocationFinding("authorization-reused", "/authorization/fingerprint", "Invocation authorization has already been consumed.")
    except (OSError, ValueError) as exc:
        return InvocationFinding("authorization-consumption-failed", "/authorization/fingerprint", str(exc))


def _ledger_directory(authorization: RendererInvocationAuthorization) -> Path:
    ledger_path = Path(authorization.authorization_ledger_directory)
    if (
        not ledger_path.is_absolute()
        or str(ledger_path.resolve()) != authorization.authorization_ledger_directory
        or ledger_path.is_symlink()
        or not ledger_path.is_dir()
        or ledger_path == Path(authorization.output_directory)
    ):
        raise ValueError("Authorization ledger directory is absent, non-canonical, or unsafe.")
    return ledger_path


def _admission_name(authorization: RendererInvocationAuthorization) -> str:
    return f"{authorization.fingerprint}.admitted"


def _admission_document(
    authorization: RendererInvocationAuthorization,
    *,
    output_identity: tuple[int, int],
    artifact_bytes: bytes,
    evidence_bytes: bytes,
) -> dict[str, Any]:
    return {
        "contract_identity": "briefforge:renderer-invocation-admission-commitment:1.0.0",
        "authorization_fingerprint": authorization.fingerprint,
        "output_directory": authorization.output_directory,
        "output_directory_device": output_identity[0],
        "output_directory_inode": output_identity[1],
        "artifact_filename": authorization.output_filename,
        "artifact_sha256": _sha256(artifact_bytes),
        "artifact_byte_length": len(artifact_bytes),
        "evidence_filename": authorization.evidence_filename,
        "evidence_sha256": _sha256(evidence_bytes),
        "evidence_byte_length": len(evidence_bytes),
    }


def _write_admission_commitment(
    authorization: RendererInvocationAuthorization,
    *,
    output_identity: tuple[int, int],
    artifact_bytes: bytes,
    evidence_bytes: bytes,
) -> bytes:
    """Create the external commitment before the staged inode is admitted."""

    commitment_bytes = _canonical_bytes(_admission_document(
        authorization,
        output_identity=output_identity,
        artifact_bytes=artifact_bytes,
        evidence_bytes=evidence_bytes,
    ))
    ledger_fd = _open_directory_fd(_ledger_directory(authorization))
    try:
        _write_regular_exclusive(ledger_fd, _admission_name(authorization), commitment_bytes)
        os.fsync(ledger_fd)
    finally:
        os.close(ledger_fd)
    return commitment_bytes


def _verify_admission_commitment(
    authorization: RendererInvocationAuthorization,
    *,
    output_identity: tuple[int, int],
    artifact_bytes: bytes,
    evidence_bytes: bytes,
) -> None:
    ledger_fd = _open_directory_fd(_ledger_directory(authorization))
    try:
        persisted = _read_regular(ledger_fd, _admission_name(authorization))
    except FileNotFoundError as exc:
        raise ValueError("Persisted invocation has no external admission commitment.") from exc
    finally:
        os.close(ledger_fd)
    expected = _canonical_bytes(_admission_document(
        authorization,
        output_identity=output_identity,
        artifact_bytes=artifact_bytes,
        evidence_bytes=evidence_bytes,
    ))
    if persisted != expected:
        raise ValueError("Persisted artifact/evidence pair does not match the external admission commitment.")


def _remove_admission_commitment(
    authorization: RendererInvocationAuthorization,
    expected_commitment_bytes: bytes,
) -> None:
    ledger_fd = _open_directory_fd(_ledger_directory(authorization))
    try:
        name = _admission_name(authorization)
        try:
            persisted = _read_regular(ledger_fd, name)
        except FileNotFoundError:
            return
        if persisted != expected_commitment_bytes:
            raise ValueError("Admission commitment changed and cannot be safely removed.")
        os.unlink(name, dir_fd=ledger_fd)
        os.fsync(ledger_fd)
    finally:
        os.close(ledger_fd)


def _directory_identity(path: Path) -> tuple[int, int]:
    descriptor = _open_directory_fd(path)
    try:
        info = os.fstat(descriptor)
        return info.st_dev, info.st_ino
    finally:
        os.close(descriptor)


def _projection_from_document(document: dict[str, Any]) -> MinimalHtmlRendererProjection:
    """Reconstruct only the fixed projection schema accepted by the isolated worker."""
    if type(document) is not dict:
        raise ValueError("Renderer projection payload must be an object.")
    expected = {
        "identity", "organizing_purpose", "statements", "upstream_references", "obligations",
        "semantic_fingerprint", "validation_policy_id", "consumed_mapping_ids",
        "selected_expression_modes", "fingerprint",
    }
    if set(document) != expected:
        raise ValueError("Renderer projection payload has an unexpected schema.")
    try:
        statements = tuple(
            MinimalHtmlProjectionStatement(
                **{
                    **item,
                    "encounter_semantics": MinimalHtmlProjectionEncounter(**item["encounter_semantics"]),
                    "upstream_reference_ids": tuple(item["upstream_reference_ids"]),
                    "obligation_ids": tuple(item["obligation_ids"]),
                }
            )
            for item in document["statements"]
        )
        references = tuple(MinimalHtmlProjectionReference(**item) for item in document["upstream_references"])
        obligations = tuple(
            MinimalHtmlProjectionObligation(**{**item, "applies_to": tuple(item["applies_to"])})
            for item in document["obligations"]
        )
        return MinimalHtmlRendererProjection(
            identity=MinimalHtmlProjectionIdentity(**document["identity"]),
            organizing_purpose=MinimalHtmlProjectionPurpose(**document["organizing_purpose"]),
            statements=statements,
            upstream_references=references,
            obligations=obligations,
            semantic_fingerprint=document["semantic_fingerprint"],
            validation_policy_id=document["validation_policy_id"],
            consumed_mapping_ids=tuple(document["consumed_mapping_ids"]),
            selected_expression_modes=tuple(document["selected_expression_modes"]),
            fingerprint=document["fingerprint"],
        )
    except (KeyError, TypeError) as exc:
        raise ValueError("Renderer projection payload is malformed.") from exc


def _render_in_subprocess(
    projection: MinimalHtmlRendererProjection,
    timeout_seconds: int,
    work_directory: Path,
    expected_renderer_digest: str,
) -> bytes:
    worker = Path(__file__).with_name("_controlled_renderer_worker.py").resolve()
    request = _canonical_bytes({
        "projection": asdict(projection),
        "renderer_implementation_digest": expected_renderer_digest,
    })
    try:
        completed = subprocess.run(
            (sys.executable, *_FIXED_INTERPRETER_FLAGS, str(worker)),
            input=request,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=work_directory,
            env=dict(_FIXED_ENVIRONMENT),
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError("fixed renderer timed out") from exc
    if completed.returncode != 0:
        message = completed.stderr.decode("utf-8", errors="replace")[:1000].strip()
        raise ValueError(message or "fixed renderer worker failed")
    try:
        effective = json.loads(completed.stderr.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Fixed renderer worker did not attest its effective interpreter controls.") from exc
    expected_effective = {
        "dont_write_bytecode": True,
        "environment": dict(_FIXED_ENVIRONMENT),
        "hash_randomization": False,
        "ignore_environment": False,
        "interpreter_flags": list(_FIXED_INTERPRETER_FLAGS),
        "utf8_mode": 1,
    }
    if effective != expected_effective:
        raise ValueError("Fixed renderer worker effective interpreter controls differ from authorization policy.")
    if tuple(work_directory.iterdir()):
        raise ValueError("fixed renderer produced undeclared auxiliary files")
    return completed.stdout


def _audit_record(
    *,
    plan: VerifiedRendererCompatibilityPlan,
    declaration: RendererCapabilityDeclaration,
    authorization: RendererInvocationAuthorization,
    projection: MinimalHtmlRendererProjection,
    artifact_bytes: bytes,
) -> BCRPRecord:
    bundle = plan.bundle
    release = bundle.one("PublicationReleaseRecord")
    ready = bundle.one("ReadyPresentationPackageRecord")
    digest = _sha256(artifact_bytes)
    artifact_id = f"artifact:{authorization.identity.split(':', 1)[-1]}"
    audit_id = f"artifact-audit:{authorization.identity.split(':', 1)[-1]}"
    payload = {
        "contract_identity": INVOCATION_EXTENSION_CONTRACT,
        "policy_identity": CONTROLLED_INVOCATION_POLICY_ID,
        "authorization_identity": authorization.identity,
        "authorization_fingerprint": authorization.fingerprint,
        "authorization_ledger_directory": authorization.authorization_ledger_directory,
        "admission_commitment_identity": _admission_name(authorization),
        "lifecycle_inventory_digest": authorization.lifecycle_inventory_digest,
        "plan_fingerprint": plan.fingerprint.digest,
        "capability_fingerprint": declaration.fingerprint,
        "renderer_identity": authorization.renderer_identity,
        "renderer_adapter_id": authorization.renderer_adapter_id,
        "renderer_version": authorization.renderer_version,
        "renderer_implementation_digest": authorization.renderer_implementation_digest,
        "projection_fingerprint": projection.fingerprint,
        "consumed_mapping_ids": list(projection.consumed_mapping_ids),
        "selected_expression_modes": list(projection.selected_expression_modes),
        "invocation_mode": authorization.invocation_mode,
        "environment": [list(item) for item in authorization.environment],
        "environment_policy": "explicit-minimal-environment-before-isolated-worker-import",
        "interpreter_flags": list(_FIXED_INTERPRETER_FLAGS),
        "effective_interpreter_controls": "verified-in-each-independent-execution",
        "external_assets": [],
        "output_directory": authorization.output_directory,
        "output_inventory": [{"filename": authorization.output_filename, "media_type": authorization.media_type,
                              "sha256": digest, "byte_length": len(artifact_bytes)}],
        "execution_digests": [digest, digest],
        "execution_byte_lengths": [len(artifact_bytes), len(artifact_bytes)],
        "invocation_outcome": "completed-deterministically",
        "artifact_existence": "verified",
        "audit_links": "verified",
        "semantic_conformance": "unassessed",
        "manifest_authority": "absent",
        "distribution_authority": "absent",
        "successful_publication": "not-asserted",
    }
    return BCRPRecord(
        kind="GeneratedArtifactAuditRecord", identity=audit_id, profile_version=PROFILE_VERSION,
        semantic={
            "release_ref": release.identity, "ready_ref": ready.identity,
            "ready_fingerprint": ready.semantic["ready_fingerprint"],
            "plan_ref": plan.plan.identity, "renderer_capability_ref": declaration.identity,
            "artifact": {"id": artifact_id, "filename": authorization.output_filename,
                         "media_type": authorization.media_type, "sha256": digest,
                         "byte_length": len(artifact_bytes)},
            "audit_links_pass": True, "invocation_time": authorization.authorization_time,
        },
        extensions=[{
            "owner_namespace": "briefforge-controlled-renderer-invocation",
            "name": "invocation-and-artifact-evidence", "version": "1.0.0",
            "authority_ref": authorization.authority_identity,
            "scope": "artifact-existence-and-invocation-audit-links-only",
            "target_refs": [release.identity, ready.identity, plan.plan.identity, declaration.identity, artifact_id],
            "criticality": "required", "character": "semantic",
            "validation_contract": INVOCATION_EXTENSION_CONTRACT,
            "preservation": "must-preserve", "payload": payload,
        }],
    )


def invoke_controlled_renderer(
    *,
    verified_release: VerifiedPublicationRelease,
    evidence_snapshot: EvidenceSnapshot,
    lifecycle_scope: LifecyclePlanningScope,
    declaration: RendererCapabilityDeclaration,
    planning_authorization: PlanningAuthorization,
    verified_plan: VerifiedRendererCompatibilityPlan,
    authorization: RendererInvocationAuthorization,
) -> ControlledInvocationResult:
    """Execute one authorized transaction; failure returns findings and no success evidence."""

    try:
        projection = build_minimal_html_projection(
            verified_release=verified_release, evidence_snapshot=evidence_snapshot,
            lifecycle_scope=lifecycle_scope, declaration=declaration,
            planning_authorization=planning_authorization, verified_plan=verified_plan,
        )
        plan = _reverify_plan(
            verified_release=verified_release, evidence_snapshot=evidence_snapshot,
            lifecycle_scope=lifecycle_scope, declaration=declaration,
            planning_authorization=planning_authorization, verified_plan=verified_plan,
        )
    except Exception as exc:
        return ControlledInvocationResult((InvocationFinding("upstream-reverification-failed", "/inputs", str(exc)),), None)
    findings = _authorization_problems(
        authorization, verified_release=verified_release, lifecycle_scope=lifecycle_scope,
        declaration=declaration, plan=plan, projection=projection,
    )
    output_path: Path | None = None
    if type(authorization) is RendererInvocationAuthorization:
        output_path, output_findings = _output_directory_problems(authorization.output_directory)
        findings.extend(output_findings)
    if findings:
        return ControlledInvocationResult(tuple(sorted(set(findings))), None)
    assert output_path is not None

    try:
        authorized_output_identity = _directory_identity(output_path)
        authorized_parent_identity = _directory_identity(output_path.parent)
    except OSError as exc:
        return ControlledInvocationResult((InvocationFinding("invalid-output-directory", "/authorization/output_directory", str(exc)),), None)
    consumption_finding = _consume_authorization(authorization)
    if consumption_finding is not None:
        return ControlledInvocationResult((consumption_finding,), None)

    try:
        with _EXECUTION_LOCK:
            with tempfile.TemporaryDirectory(prefix="briefforge-task052-a-") as first_dir, tempfile.TemporaryDirectory(prefix="briefforge-task052-b-") as second_dir:
                first = _render_in_subprocess(
                    projection, authorization.timeout_seconds, Path(first_dir), authorization.renderer_implementation_digest
                )
                second = _render_in_subprocess(
                    projection, authorization.timeout_seconds, Path(second_dir), authorization.renderer_implementation_digest
                )
    except Exception as exc:
        return ControlledInvocationResult((InvocationFinding("renderer-execution-failed", "/renderer", str(exc)),), None)
    if first != second:
        return ControlledInvocationResult((InvocationFinding("renderer-nondeterministic", "/renderer/output", "Independent renderer executions produced different bytes."),), None)
    if len(first) > authorization.maximum_output_bytes:
        return ControlledInvocationResult((InvocationFinding("output-size-exceeded", "/renderer/output", "Renderer output exceeds the authorized byte bound."),), None)
    try:
        _verify_standalone_html(first)
    except ValueError as exc:
        return ControlledInvocationResult((InvocationFinding("unsafe-or-invalid-html", "/renderer/output", str(exc)),), None)

    audit = _audit_record(plan=plan, declaration=declaration, authorization=authorization,
                          projection=projection, artifact_bytes=first)
    persisted = BCRPBundle(plan.bundle.profile_identity, plan.bundle.profile_version, plan.bundle.records + (audit,))
    evidence_text = _serialize_bundle(persisted)
    parent_path = output_path.parent
    staging_name: str | None = None
    staging_path: Path | None = None
    staging_fd: int | None = None
    parent_fd: int | None = None
    swapped = False
    committed = False
    admission_commitment_bytes: bytes | None = None
    try:
        parent_fd = _open_directory_fd(parent_path)
        parent_info = os.fstat(parent_fd)
        if (parent_info.st_dev, parent_info.st_ino) != authorized_parent_identity:
            raise ValueError("Authorized output parent identity changed before staging.")
        staging_name = _create_staging_directory(parent_fd, f".{output_path.name}.task052-stage-")
        staging_path = parent_path / staging_name
        staging_fd = os.open(
            staging_name,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        staging_info = os.fstat(staging_fd)
        staging_identity = (staging_info.st_dev, staging_info.st_ino)
        _write_regular_exclusive(staging_fd, authorization.output_filename, first)
        _write_regular_exclusive(staging_fd, authorization.evidence_filename, evidence_text.encode("utf-8"))
        staged_artifact_bytes = _read_regular(staging_fd, authorization.output_filename)
        staged_evidence_bytes = _read_regular(staging_fd, authorization.evidence_filename)
        if staged_artifact_bytes != first:
            raise ValueError("Staged artifact bytes changed before publication.")
        verified = _verify_invocation_bytes(
            artifact_bytes=staged_artifact_bytes,
            evidence_bytes=staged_evidence_bytes,
            evidence_snapshot=evidence_snapshot,
            lifecycle_scope=lifecycle_scope,
            declaration=declaration,
            planning_authorization=planning_authorization,
            authorization=authorization,
        )
        admission_commitment_bytes = _write_admission_commitment(
            authorization,
            output_identity=staging_identity,
            artifact_bytes=staged_artifact_bytes,
            evidence_bytes=staged_evidence_bytes,
        )
        os.fsync(staging_fd)
        os.close(staging_fd)
        staging_fd = None

        current_fd = os.open(output_path.name, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0), dir_fd=parent_fd)
        try:
            current_info = os.fstat(current_fd)
            if (current_info.st_dev, current_info.st_ino) != authorized_output_identity:
                raise ValueError("Authorized output directory identity changed before atomic publication.")
            if os.listdir(current_fd):
                raise ValueError("Authorized output directory changed before atomic publication.")
        finally:
            os.close(current_fd)
        preexchange_staging_fd = os.open(
            staging_name,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        try:
            preexchange_info = os.fstat(preexchange_staging_fd)
            if (preexchange_info.st_dev, preexchange_info.st_ino) != staging_identity:
                raise ValueError("Verified staging directory identity changed before atomic publication.")
        finally:
            os.close(preexchange_staging_fd)
        _exchange_directories(parent_fd, staging_name, output_path.name)
        swapped = True
        exchanged_original_fd = os.open(
            staging_name,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        published_fd = os.open(
            output_path.name,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        try:
            exchanged_info = os.fstat(exchanged_original_fd)
            published_info = os.fstat(published_fd)
            if (exchanged_info.st_dev, exchanged_info.st_ino) != authorized_output_identity:
                raise ValueError("Atomic publication exchanged an unauthorized output-directory identity.")
            if (published_info.st_dev, published_info.st_ino) != staging_identity:
                raise ValueError("Atomic publication did not publish the identity-verified staging directory.")
            if set(os.listdir(published_fd)) != {authorization.output_filename, authorization.evidence_filename}:
                raise ValueError("Published output inventory differs from the authorized two-file pair.")
            published_artifact_bytes = _read_regular(published_fd, authorization.output_filename)
            published_evidence_bytes = _read_regular(published_fd, authorization.evidence_filename)
            if published_artifact_bytes != staged_artifact_bytes or published_evidence_bytes != staged_evidence_bytes:
                raise ValueError("Published bytes changed across the atomic exchange boundary.")
            published_verified = _verify_invocation_bytes(
                artifact_bytes=published_artifact_bytes,
                evidence_bytes=published_evidence_bytes,
                evidence_snapshot=evidence_snapshot,
                lifecycle_scope=lifecycle_scope,
                declaration=declaration,
                planning_authorization=planning_authorization,
                authorization=authorization,
            )
            _verify_admission_commitment(
                authorization,
                output_identity=staging_identity,
                artifact_bytes=published_artifact_bytes,
                evidence_bytes=published_evidence_bytes,
            )
            committed = True
        finally:
            os.close(exchanged_original_fd)
            os.close(published_fd)
        os.fsync(parent_fd)
        _cleanup_exchanged_original(parent_fd, staging_name, authorized_output_identity)
        return ControlledInvocationResult((), published_verified)
    except Exception as exc:
        if parent_fd is not None and swapped and not committed:
            try:
                rollback_staging_fd = os.open(
                    staging_name,
                    os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=parent_fd,
                )
                try:
                    original_info = os.fstat(rollback_staging_fd)
                    if (original_info.st_dev, original_info.st_ino) != authorized_output_identity:
                        raise ValueError("Original output directory identity changed before rollback.")
                finally:
                    os.close(rollback_staging_fd)
                rollback_published_fd = os.open(
                    output_path.name,
                    os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=parent_fd,
                )
                try:
                    published_info = os.fstat(rollback_published_fd)
                    published_identity = (published_info.st_dev, published_info.st_ino)
                finally:
                    os.close(rollback_published_fd)
                if published_identity == staging_identity:
                    _raw_exchange_directories(parent_fd, staging_name, output_path.name)
                else:
                    rejected_name = f"{staging_name}.rejected"
                    _raw_rename_noreplace(parent_fd, output_path.name, rejected_name)
                    rejected_fd = os.open(
                        rejected_name,
                        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
                        dir_fd=parent_fd,
                    )
                    try:
                        rejected_info = os.fstat(rejected_fd)
                        if (rejected_info.st_dev, rejected_info.st_ino) != published_identity:
                            raise ValueError("Rejected output identity changed during quarantine.")
                    finally:
                        os.close(rejected_fd)
                    _raw_rename_noreplace(parent_fd, staging_name, output_path.name)
                    _remove_rejected_directory(parent_fd, rejected_name, published_identity)
                restored_fd = os.open(
                    output_path.name,
                    os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=parent_fd,
                )
                try:
                    restored_info = os.fstat(restored_fd)
                    if (restored_info.st_dev, restored_info.st_ino) != authorized_output_identity:
                        raise ValueError("Rollback did not restore the authorized output identity.")
                finally:
                    os.close(restored_fd)
                os.fsync(parent_fd)
                swapped = False
            except (OSError, TypeError, ValueError):
                pass
        failure_message = str(exc)
        if admission_commitment_bytes is not None and not swapped and not committed:
            try:
                _remove_admission_commitment(authorization, admission_commitment_bytes)
                admission_commitment_bytes = None
            except (OSError, ValueError) as cleanup_exc:
                failure_message += f"; admission commitment cleanup failed: {cleanup_exc}"
        return ControlledInvocationResult((InvocationFinding("artifact-persistence-failed", "/output", failure_message),), None)
    finally:
        if staging_fd is not None:
            os.close(staging_fd)
        if parent_fd is not None and staging_name is not None and not swapped:
            cleanup_fd: int | None = None
            try:
                cleanup_fd = os.open(
                    staging_name,
                    os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=parent_fd,
                )
                for name in (authorization.output_filename, authorization.evidence_filename):
                    try:
                        os.unlink(name, dir_fd=cleanup_fd)
                    except FileNotFoundError:
                        pass
            except OSError:
                pass
            finally:
                if cleanup_fd is not None:
                    os.close(cleanup_fd)
            try:
                os.rmdir(staging_name, dir_fd=parent_fd)
                os.fsync(parent_fd)
            except OSError:
                pass
        if parent_fd is not None:
            os.close(parent_fd)


def _verify_invocation_bytes(
    *,
    artifact_bytes: bytes,
    evidence_bytes: bytes,
    evidence_snapshot: EvidenceSnapshot,
    lifecycle_scope: LifecyclePlanningScope,
    declaration: RendererCapabilityDeclaration,
    planning_authorization: PlanningAuthorization,
    authorization: RendererInvocationAuthorization,
) -> VerifiedRendererInvocation:
    try:
        evidence_text = evidence_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Persisted invocation evidence is not UTF-8.") from exc
    bundle = _deserialize_bundle(evidence_text)
    if evidence_text != _serialize_bundle(bundle):
        raise ValueError("Persisted invocation evidence bytes are not canonical.")
    expected_kinds = (
        "PresentationBriefRecord", "PortablePresentationMaterialRecord", "CandidatePresentationPackageRecord",
        "ValidationJudgmentRecord", "ReadyPresentationPackageRecord", "PublicationReleaseRecord",
        "RendererCapabilityDeclarationRecord", "RendererCompatibilityPlanRecord", "GeneratedArtifactAuditRecord",
    )
    if len(bundle.records) != 9 or any(len(bundle.records_of_kind(kind)) != 1 for kind in expected_kinds):
        raise ValueError("Persisted invocation evidence requires exactly the eight-record Plan closure plus one artifact audit.")
    if any(record.kind not in expected_kinds for record in bundle.records):
        raise ValueError("Persisted invocation evidence contains conformance, Manifest, or unknown records.")
    generic = validate_bundle(bundle, through_layer="L5")
    specialized_extension_identities = {
        bundle.one(kind).identity for kind in (
            "ValidationJudgmentRecord",
            "ReadyPresentationPackageRecord",
            "PublicationReleaseRecord",
            "RendererCapabilityDeclarationRecord",
            "RendererCompatibilityPlanRecord",
            "GeneratedArtifactAuditRecord",
        )
    }
    unexpected_generic = [
        finding for finding in generic.findings
        if not (
            finding.family == "extension-boundary"
            and finding.semantic_identity in specialized_extension_identities
            and finding.location == "/extensions/0"
            and finding.message == "Unknown required semantic extension cannot be processed."
        )
    ]
    if unexpected_generic:
        details = "; ".join(
            f"{finding.semantic_identity}{finding.location}: {finding.message}"
            for finding in unexpected_generic
        )
        raise ValueError(f"Persisted invocation evidence fails generic BCRP validation: {details}")
    plan_bundle = BCRPBundle(bundle.profile_identity, bundle.profile_version, bundle.records[:8])
    plan = verify_renderer_compatibility_plan(
        plan_bundle, evidence_snapshot=evidence_snapshot, lifecycle_scope=lifecycle_scope,
        declaration=declaration, authorization=planning_authorization,
        expected_plan_fingerprint=authorization.plan_fingerprint,
    )
    release_bundle = BCRPBundle(bundle.profile_identity, bundle.profile_version, bundle.records[:6])
    from .publication_release import verify_publication_release
    release = verify_publication_release(release_bundle, evidence_snapshot=evidence_snapshot,
                                         expected_release_fingerprint=authorization.release_fingerprint)
    projection = build_minimal_html_projection(
        verified_release=release, evidence_snapshot=evidence_snapshot, lifecycle_scope=lifecycle_scope,
        declaration=declaration, planning_authorization=planning_authorization, verified_plan=plan,
    )
    problems = _authorization_problems(
        authorization, verified_release=release, lifecycle_scope=lifecycle_scope,
        declaration=declaration, plan=plan, projection=projection,
    )
    if problems:
        raise ValueError("Persisted invocation authorization is stale or contradictory.")
    expected_audit = _audit_record(plan=plan, declaration=declaration, authorization=authorization,
                                   projection=projection, artifact_bytes=artifact_bytes)
    if bundle.one("GeneratedArtifactAuditRecord").to_document() != expected_audit.to_document():
        raise ValueError("Persisted invocation evidence differs from exact independently reproduced evidence.")
    if len(artifact_bytes) > authorization.maximum_output_bytes:
        raise ValueError("Persisted artifact exceeds authorized bounds.")
    _verify_standalone_html(artifact_bytes)
    fingerprint = fingerprint_bundle(bundle, domain="profile-instance", require_valid=False)
    return VerifiedRendererInvocation(_serialize_bundle(bundle), bytes(artifact_bytes), fingerprint)


def verify_persisted_renderer_invocation(
    *,
    artifact_path: Path,
    evidence_path: Path,
    evidence_snapshot: EvidenceSnapshot,
    lifecycle_scope: LifecyclePlanningScope,
    declaration: RendererCapabilityDeclaration,
    planning_authorization: PlanningAuthorization,
    authorization: RendererInvocationAuthorization,
) -> VerifiedRendererInvocation:
    """Reload and independently verify exact artifact bytes and nine-record evidence."""

    if not isinstance(artifact_path, Path) or not isinstance(evidence_path, Path):
        raise ValueError("Path inputs are required for persisted verification.")
    expected_directory = Path(authorization.output_directory)
    if artifact_path != expected_directory / authorization.output_filename or evidence_path != expected_directory / authorization.evidence_filename:
        raise ValueError("Persisted paths differ from the exact authorized output paths.")
    directory_fd = _open_directory_fd(expected_directory)
    try:
        directory_info = os.fstat(directory_fd)
        output_identity = (directory_info.st_dev, directory_info.st_ino)
        if set(os.listdir(directory_fd)) != {authorization.output_filename, authorization.evidence_filename}:
            raise ValueError("Persisted output inventory contains undeclared files.")
        artifact_bytes = _read_regular(directory_fd, authorization.output_filename)
        evidence_bytes = _read_regular(directory_fd, authorization.evidence_filename)
        verified = _verify_invocation_bytes(
            artifact_bytes=artifact_bytes,
            evidence_bytes=evidence_bytes,
            evidence_snapshot=evidence_snapshot,
            lifecycle_scope=lifecycle_scope,
            declaration=declaration,
            planning_authorization=planning_authorization,
            authorization=authorization,
        )
        _verify_admission_commitment(
            authorization,
            output_identity=output_identity,
            artifact_bytes=artifact_bytes,
            evidence_bytes=evidence_bytes,
        )
        if _directory_identity(expected_directory) != output_identity:
            raise ValueError("Authorized output pathname changed during persisted verification.")
        if set(os.listdir(directory_fd)) != {authorization.output_filename, authorization.evidence_filename}:
            raise ValueError("Persisted output inventory changed during verification.")
        if (
            _read_regular(directory_fd, authorization.output_filename) != artifact_bytes
            or _read_regular(directory_fd, authorization.evidence_filename) != evidence_bytes
        ):
            raise ValueError("Persisted artifact or evidence bytes changed during verification.")
        return verified
    finally:
        os.close(directory_fd)
