"""Independent HTML parsing and semantic assessment for the paired profile."""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from datetime import datetime, timezone
from html.parser import HTMLParser
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any

from .controlled_invocation import (
    PairedTerminalRendererInvocationAuthorization,
    VerifiedPairedRendererInvocation, paired_renderer_implementation_digest,
    reverify_paired_renderer_invocation_evidence,
)
from .profile import (
    PairedUpstreamAdmissionToken, consume_paired_upstream_admission,
    verify_paired_upstream_admission_token,
)
from .projection import build_paired_editorial_projection, compute_projection_fingerprint
from .schema import (
    PairedEditorialProjection,
    PairedSemanticInput,
    validate_paired_projection,
)

CONFORMANCE_PROFILE_IDENTITY = "briefforge:representative-paired-static-html-conformance-profile:1.0.0"
CONFORMANCE_PROFILE_VERSION = "1.0.0"
CONFORMANCE_POLICY_IDENTITY = "briefforge-paired-terminal-semantic-conformance-assessment-policy:1.0.0"
CONFORMANCE_EVIDENCE_IDENTITY = "briefforge:paired-terminal-semantic-artifact-conformance-evidence:1.0.0"
ASSESSOR_IMPLEMENTATION = "briefforge_paired_terminal_profile.semantic_conformance:1.0.0"
_FIXED_MEDIA_TYPE = "text/html"
_DIGEST = re.compile(r"[0-9a-f]{64}")
_IDENTITY = re.compile(r"[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*")
_TIME = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
_VOID = frozenset({"meta"})
_BLOCKED_ELEMENTS = frozenset({"script", "style", "iframe", "object", "embed", "img", "audio", "video", "source", "link", "base", "form", "input", "button", "svg", "math"})
_RESOURCE_ATTRIBUTES = frozenset({"href", "src", "srcset", "action", "formaction", "poster", "data"})
_MAX_EVIDENCE_BYTES = 2_000_000
_EVIDENCE_FILENAME = "paired-semantic-conformance-evidence.json"


class PairedSemanticConformanceRejected(ValueError):
    """Parsed artifact or exact assessment authorization was rejected."""


@dataclass(frozen=True)
class PairedTerminalSemanticArtifactConformanceAuthorization:
    identity: str
    policy_identity: str
    evidence_identity: str
    authorization_time: str
    release_identity: str
    release_fingerprint: str
    lifecycle_scope_fingerprint: str
    plan_identity: str
    plan_fingerprint: str
    capability_declaration_identity: str
    capability_declaration_fingerprint: str
    profile_identity: str
    profile_version: str
    projection_fingerprint: str
    renderer_identity: str
    renderer_version: str
    renderer_implementation_digest: str
    assessor_implementation_digest: str
    invocation_authorization_identity: str
    invocation_authorization_fingerprint: str
    invocation_evidence_fingerprint: str
    artifact_sha256: str
    artifact_byte_length: int
    artifact_media_type: str
    fingerprint: str


# The shorter name remains a source-compatible spelling for callers of the
# focused assessment API; it denotes the same frozen exact class.
PairedSemanticArtifactConformanceAuthorization = PairedTerminalSemanticArtifactConformanceAuthorization


@dataclass(frozen=True)
class PairedSemanticRealizationReport:
    verdict: str
    artifact_sha256: str
    artifact_byte_length: int
    table_count: int
    column_identities: tuple[str, ...]
    column_headings: tuple[str, ...]
    row_identities: tuple[str, ...]
    relationship_identities: tuple[str, ...]
    value_identities: tuple[str, ...]
    value_states: tuple[str, ...]
    transformation_states: tuple[str, ...]
    row_metadata: tuple[tuple[str, str, str, str, str], ...]
    qualification_identities: tuple[tuple[str, ...], ...]
    provenance_identities: tuple[tuple[str, ...], ...]
    projection_fingerprint: str


@dataclass(frozen=True)
class VerifiedPairedSemanticArtifactConformance:
    """Result of independently reloading persisted conformance evidence.

    This is integrity evidence within the trusted process.  It makes no claim
    of security against a hostile interpreter or modified process runtime.
    """

    evidence_bytes: bytes
    evidence_path: Path
    fingerprint: str
    report: PairedSemanticRealizationReport


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def compute_paired_conformance_authorization_fingerprint(
    authorization: PairedTerminalSemanticArtifactConformanceAuthorization,
) -> str:
    if type(authorization) is not PairedTerminalSemanticArtifactConformanceAuthorization:
        raise TypeError("exact paired conformance authorization required")
    document = asdict(authorization)
    document.pop("fingerprint")
    return _sha256(_canonical(document))


def _attrs(*pairs: tuple[str, object]) -> tuple[tuple[str, str | None], ...]:
    return tuple((name, None if value is None else str(value)) for name, value in pairs)


class _SemanticParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.events: list[tuple[Any, ...]] = []
        self.stack: list[str] = []
        self.failure: str | None = None

    def handle_decl(self, decl: str) -> None:
        self.events.append(("decl", decl))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _BLOCKED_ELEMENTS:
            self.failure = "active, embedded, or external-resource element is forbidden"
        names = [name for name, _ in attrs]
        if len(names) != len(set(names)):
            self.failure = "duplicate attributes are forbidden"
        for name, value in attrs:
            lowered = name.lower()
            if lowered.startswith("on") or lowered in _RESOURCE_ATTRIBUTES:
                self.failure = "active or external-resource attribute is forbidden"
            if lowered in {"hidden", "aria-hidden"} or (lowered == "style" and value is not None):
                self.failure = "hidden content is forbidden"
        self.events.append(("start", tag, tuple(attrs)))
        if tag not in _VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.failure = "self-closing syntax is outside the exact realization"
        self.events.append(("startend", tag, tuple(attrs)))

    def handle_endtag(self, tag: str) -> None:
        if not self.stack or self.stack[-1] != tag:
            self.failure = "HTML element nesting is malformed"
        else:
            self.stack.pop()
        self.events.append(("end", tag))

    def handle_data(self, data: str) -> None:
        self.events.append(("data", data))

    def handle_comment(self, data: str) -> None:
        self.failure = "comments are outside the exact realization"
        self.events.append(("comment", data))

    def handle_pi(self, data: str) -> None:
        self.failure = "processing instructions are outside the exact realization"
        self.events.append(("pi", data))

    def unknown_decl(self, data: str) -> None:
        self.failure = "unknown declarations are outside the exact realization"
        self.events.append(("unknown", data))


def _start(events: list[tuple[Any, ...]], tag: str,
           attrs: tuple[tuple[str, str | None], ...] = ()) -> None:
    events.append(("start", tag, attrs))


def _end(events: list[tuple[Any, ...]], tag: str) -> None:
    events.append(("end", tag))


def _text_element(events: list[tuple[Any, ...]], tag: str, text: str,
                  attrs: tuple[tuple[str, str | None], ...] = ()) -> None:
    _start(events, tag, attrs)
    if text:
        events.append(("data", text))
    _end(events, tag)


def _expected_statement(events: list[tuple[Any, ...]], item: Any) -> None:
    pairs: list[tuple[str, object]] = [
        ("class", "statement"), ("data-identity", item.identity),
        ("data-role", item.role), ("data-authority", item.authority_ref),
    ]
    if item.display_classification is not None:
        pairs.append(("data-classification", item.display_classification))
    _text_element(events, "p", item.text, _attrs(*pairs))


def _expected_provenance(events: list[tuple[Any, ...]], item: Any) -> None:
    pairs: list[tuple[str, object]] = [
        ("class", "provenance"), ("data-identity", item.identity),
        ("data-authority", item.authority_ref),
        ("data-source", item.source_snapshot_identity or item.source_locator or ""),
    ]
    if item.source_commit is not None:
        pairs.append(("data-source-commit", item.source_commit))
    pairs.extend((("data-packages", " ".join(item.package_identities)),
                  ("data-targets", " ".join(item.target_refs)),
                  ("data-target-rule", item.target_rule)))
    _text_element(events, "aside", item.citation, _attrs(*pairs))


def _expected_obligation(events: list[tuple[Any, ...]], item: Any) -> None:
    _text_element(events, "aside", "", _attrs(
        ("class", "obligation"), ("data-identity", item.identity),
        ("data-kind", item.kind), ("data-authority", item.authority_ref),
        ("data-targets", " ".join(item.target_refs)),
    ))


def _expected_table(events: list[tuple[Any, ...]], projection: PairedEditorialProjection) -> None:
    table = projection.table
    values = {item.identity: item for item in projection.values}
    statements = {item.identity: item for item in projection.statements}
    qualifications = {item.identity: item for item in projection.qualifications}
    provenance = {item.identity: item for item in projection.provenance}
    _start(events, "table", _attrs(("id", table.identity), ("data-purpose", table.purpose_ref),
                                    ("data-authority", table.authority_ref)))
    _start(events, "thead"); _start(events, "tr")
    for identity, heading in zip(table.column_identities, table.column_headings):
        _text_element(events, "th", heading, _attrs(("scope", "col"), ("data-identity", identity)))
    _end(events, "tr"); _end(events, "thead"); _start(events, "tbody")
    for row in table.rows:
        raw, difference = values[row.raw_value_ref], values[row.first_difference_value_ref]
        statement = statements[row.row_statement_ref]
        _start(events, "tr", _attrs(("id", row.identity), ("data-order", row.order)))
        _start(events, "td")
        _text_element(events, "strong", row.relationship_label)
        _text_element(events, "span", row.relationship_identity,
                      _attrs(("class", "relationship-identity")))
        _text_element(events, "p", statement.text, _attrs(
            ("class", "row-statement"), ("data-statement", statement.identity),
            ("data-role", statement.role), ("data-authority", statement.authority_ref),
        ))
        _start(events, "span", _attrs(("class", "row-semantics"),
                                       ("data-classification", row.classification_ref),
                                       ("data-evidence-role", row.evidence_role_ref)))
        for ref in row.qualification_refs:
            item = qualifications[ref]
            _text_element(events, "span", "", _attrs(
                ("class", "qualification"), ("data-identity", item.identity),
                ("data-kind", item.kind), ("data-source", item.source_ref),
                ("data-target", item.target_ref), ("data-order", item.target_order),
                ("data-authority", item.authority_ref),
            ))
        for ref in row.provenance_refs:
            item = provenance[ref]
            _text_element(events, "span", "", _attrs(
                ("class", "row-provenance"), ("data-identity", item.identity),
                ("data-citation", item.citation), ("data-authority", item.authority_ref),
                ("data-source-commit", item.source_commit or ""),
                ("data-source-snapshot", item.source_snapshot_identity or ""),
                ("data-source-locator", item.source_locator or ""),
                ("data-packages", " ".join(item.package_identities)),
                ("data-targets", " ".join(item.target_refs)),
                ("data-target-rule", item.target_rule),
                ("data-placement", item.placement_ref),
            ))
        _end(events, "span"); _end(events, "td")
        _text_element(events, "td", raw.lexical_representation, _attrs(("data-value", raw.identity)))
        _start(events, "td")
        _text_element(events, "span", f"{raw.value_state}; {raw.transformation_state}; period {raw.aligned_period}; count {raw.aligned_count}",
                      _attrs(("data-value-state", raw.value_state),
                             ("data-transformation", raw.transformation_identity)))
        _end(events, "td")
        _text_element(events, "td", difference.lexical_representation,
                      _attrs(("data-value", difference.identity)))
        _start(events, "td")
        _text_element(events, "span", f"{difference.value_state}; {difference.transformation_state}; period {difference.aligned_period}; count {difference.aligned_count}",
                      _attrs(("data-value-state", difference.value_state),
                             ("data-transformation", difference.transformation_identity)))
        _end(events, "td"); _end(events, "tr")
    _end(events, "tbody"); _end(events, "table")


def _expected_events(projection: PairedEditorialProjection) -> tuple[tuple[Any, ...], ...]:
    events: list[tuple[Any, ...]] = [("decl", "doctype html"), ("data", "\n")]
    _start(events, "html", _attrs(("lang", "en"))); _start(events, "head")
    _start(events, "meta", _attrs(("charset", "utf-8")))
    _start(events, "meta", _attrs(("name", "viewport"),
                                   ("content", "width=device-width,initial-scale=1")))
    _text_element(events, "title", "Paired editorial comparison")
    _end(events, "head"); _start(events, "body"); _start(events, "main")
    statements = {item.identity: item for item in projection.statements}
    provenance = {item.identity: item for item in projection.provenance}
    obligations = {item.identity: item for item in projection.obligations}
    row_statements = {row.row_statement_ref for row in projection.table.rows}
    root = projection.sections[0]
    leaves = {section.identity: section for section in projection.sections[1:]}
    destinations = tuple(child.target_ref for child in root.children)
    for section in (root,) + tuple(leaves[item] for item in destinations):
        if section is root:
            _start(events, "header", _attrs(("data-section", section.identity)))
            _text_element(events, "h1", section.title); _end(events, "header")
            continue
        _start(events, "section", _attrs(("data-identity", section.identity)))
        _text_element(events, "h2", section.title)
        for child in section.children:
            if child.kind == "statement" and child.target_ref not in row_statements:
                _expected_statement(events, statements[child.target_ref])
            elif child.kind == "table":
                _expected_table(events, projection)
            elif child.kind == "provenance":
                _expected_provenance(events, provenance[child.target_ref])
            elif child.kind == "obligation":
                _expected_obligation(events, obligations[child.target_ref])
        _end(events, "section")
    _end(events, "main"); _end(events, "body"); _end(events, "html"); events.append(("data", "\n"))
    return tuple(events)


def _parse(artifact_bytes: bytes) -> tuple[tuple[Any, ...], ...]:
    if type(artifact_bytes) is not bytes or not artifact_bytes or len(artifact_bytes) > 1_000_000:
        raise PairedSemanticConformanceRejected("artifact requires bounded nonempty exact bytes")
    try:
        text = artifact_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PairedSemanticConformanceRejected("artifact is not exact UTF-8") from exc
    if "\x00" in text:
        raise PairedSemanticConformanceRejected("artifact contains a null character")
    parser = _SemanticParser()
    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:
        raise PairedSemanticConformanceRejected("artifact HTML parsing failed") from exc
    if parser.failure is not None or parser.stack:
        raise PairedSemanticConformanceRejected(parser.failure or "HTML elements remain unclosed")
    return tuple(parser.events)


def verify_exact_paired_html(artifact_bytes: bytes, *, projection: PairedEditorialProjection) -> PairedSemanticRealizationReport:
    """Compare parsed supplied semantics with a DTO-derived exact realization."""
    try:
        validate_paired_projection(projection)
        if projection.projection_fingerprint != compute_projection_fingerprint(projection):
            raise PairedSemanticConformanceRejected("projection fingerprint is stale")
        measured = _parse(artifact_bytes)
        expected = _expected_events(projection)
        if measured != expected:
            raise PairedSemanticConformanceRejected("parsed semantic realization differs from the exact projection")
        rows = projection.table.rows
        values = {item.identity: item for item in projection.values}
        ordered_values = tuple(values[ref] for row in rows
                               for ref in (row.raw_value_ref, row.first_difference_value_ref))
        return PairedSemanticRealizationReport(
            "approved", _sha256(artifact_bytes), len(artifact_bytes), 1,
            projection.table.column_identities, projection.table.column_headings,
            tuple(row.identity for row in rows), tuple(row.relationship_identity for row in rows),
            tuple(item.identity for item in ordered_values),
            tuple(item.value_state for item in ordered_values),
            tuple(item.transformation_state for item in ordered_values),
            tuple((row.classification_ref, row.evidence_role_ref, row.row_statement_ref,
                   row.raw_value_ref, row.first_difference_value_ref) for row in rows),
            tuple(row.qualification_refs for row in rows),
            tuple(row.provenance_refs for row in rows), projection.projection_fingerprint,
        )
    except PairedSemanticConformanceRejected:
        raise
    except Exception as exc:
        raise PairedSemanticConformanceRejected(str(exc)) from exc


def _canonical_time(value: object) -> bool:
    if type(value) is not str or _TIME.fullmatch(value) is None:
        return False
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return False
    return parsed.strftime("%Y-%m-%dT%H:%M:%SZ") == value


def _validate_authorization(
    a: object,
    projection: PairedEditorialProjection,
    artifact: bytes,
    *,
    invocation_authorization: PairedTerminalRendererInvocationAuthorization | None = None,
    invocation_evidence_fingerprint: str | None = None,
) -> PairedTerminalSemanticArtifactConformanceAuthorization:
    if type(a) is not PairedTerminalSemanticArtifactConformanceAuthorization:
        raise PairedSemanticConformanceRejected("exact paired conformance authorization required")
    for item in fields(a):
        value = getattr(a, item.name)
        if item.name == "artifact_byte_length":
            if type(value) is not int:
                raise PairedSemanticConformanceRejected("artifact byte length requires an exact integer")
        elif type(value) is not str:
            raise PairedSemanticConformanceRejected(f"{item.name} requires exact text")
    expected = {
        "policy_identity": CONFORMANCE_POLICY_IDENTITY,
        "evidence_identity": CONFORMANCE_EVIDENCE_IDENTITY,
        "release_identity": projection.release_identity,
        "release_fingerprint": projection.release_fingerprint,
        "lifecycle_scope_fingerprint": projection.lifecycle_scope_fingerprint,
        "plan_identity": projection.plan_identity,
        "plan_fingerprint": projection.plan_fingerprint,
        "capability_declaration_identity": projection.capability_declaration_identity,
        "capability_declaration_fingerprint": projection.capability_declaration_fingerprint,
        "profile_identity": CONFORMANCE_PROFILE_IDENTITY,
        "profile_version": CONFORMANCE_PROFILE_VERSION,
        "projection_fingerprint": projection.projection_fingerprint,
        "renderer_identity": "briefforge:representative-paired-static-html-renderer:1.0.0",
        "renderer_version": "1.0.0",
        "renderer_implementation_digest": paired_renderer_implementation_digest(),
        "assessor_implementation_digest": paired_assessor_source_digest(),
        "artifact_sha256": _sha256(artifact),
        "artifact_byte_length": len(artifact),
        "artifact_media_type": _FIXED_MEDIA_TYPE,
    }
    if invocation_authorization is not None:
        if type(invocation_authorization) is not PairedTerminalRendererInvocationAuthorization:
            raise PairedSemanticConformanceRejected("exact paired invocation authorization required")
        if type(invocation_evidence_fingerprint) is not str:
            raise PairedSemanticConformanceRejected("verified invocation evidence fingerprint required")
        expected.update({
            "invocation_authorization_identity": invocation_authorization.identity,
            "invocation_authorization_fingerprint": invocation_authorization.fingerprint,
            "invocation_evidence_fingerprint": invocation_evidence_fingerprint,
        })
        try:
            if datetime.strptime(a.authorization_time, "%Y-%m-%dT%H:%M:%SZ") < datetime.strptime(
                invocation_authorization.authorization_time, "%Y-%m-%dT%H:%M:%SZ"
            ):
                raise PairedSemanticConformanceRejected("conformance authorization predates invocation")
        except ValueError as exc:
            raise PairedSemanticConformanceRejected("authorization time is invalid") from exc
    if any(getattr(a, name) != value for name, value in expected.items()):
        raise PairedSemanticConformanceRejected("authorization differs from exact projection or artifact bindings")
    if _IDENTITY.fullmatch(a.identity) is None or _IDENTITY.fullmatch(a.invocation_authorization_identity) is None:
        raise PairedSemanticConformanceRejected("authorization identity binding is malformed")
    if not _canonical_time(a.authorization_time):
        raise PairedSemanticConformanceRejected("authorization time is not canonical UTC")
    digests = (a.release_fingerprint, a.lifecycle_scope_fingerprint, a.plan_fingerprint,
               a.capability_declaration_fingerprint, a.projection_fingerprint,
               a.renderer_implementation_digest, a.assessor_implementation_digest,
               a.invocation_authorization_fingerprint, a.invocation_evidence_fingerprint,
               a.artifact_sha256, a.fingerprint)
    if any(type(value) is not str or _DIGEST.fullmatch(value) is None for value in digests):
        raise PairedSemanticConformanceRejected("authorization contains a malformed digest")
    if a.fingerprint != compute_paired_conformance_authorization_fingerprint(a):
        raise PairedSemanticConformanceRejected("authorization fingerprint is stale")
    return a


def assess_paired_semantic_artifact_conformance(*, artifact_bytes: bytes,
                                                 projection: PairedEditorialProjection,
                                                 authorization: PairedTerminalSemanticArtifactConformanceAuthorization,
                                                 ) -> PairedSemanticRealizationReport:
    """Compatibility-only in-memory semantic check; this emits no provenance evidence."""
    try:
        validate_paired_projection(projection)
        _validate_authorization(authorization, projection, artifact_bytes)
        return verify_exact_paired_html(artifact_bytes, projection=projection)
    except PairedSemanticConformanceRejected:
        raise
    except Exception as exc:
        raise PairedSemanticConformanceRejected(str(exc)) from exc


# Evidence below is integrity evidence in a trusted process.  It makes no claim
# against a hostile interpreter or modified process runtime.
def paired_assessor_source_digest() -> str:
    directory = Path(__file__).resolve().parent
    measured = bytearray(b"paired-assessor-closure-v1\0")
    for name in ("semantic_conformance.py", "schema.py", "profile.py", "projection.py"):
        measured.extend(name.encode() + b"\0" + (directory / name).read_bytes() + b"\0")
    measured.extend(f"{sys.implementation.name}:{sys.implementation.cache_tag}:{sys.version_info[:3]}".encode())
    return _sha256(bytes(measured))


def _derived_projection(semantics, token, ia):
    if type(semantics) is not PairedSemanticInput:
        raise PairedSemanticConformanceRejected("exact admitted paired semantic object required")
    if type(token) is not PairedUpstreamAdmissionToken:
        raise PairedSemanticConformanceRejected("exact verified upstream admission token required")
    if type(ia) is not PairedTerminalRendererInvocationAuthorization:
        raise PairedSemanticConformanceRejected("exact paired invocation authorization required")
    try:
        issued_semantics, _ = consume_paired_upstream_admission(token)
    except Exception as exc:
        raise PairedSemanticConformanceRejected(f"upstream admission failed: {exc}") from exc
    if semantics != issued_semantics:
        raise PairedSemanticConformanceRejected(
            "caller semantic object differs from the verified Release closure")
    projection = build_paired_editorial_projection(admitted=token)
    verify_paired_upstream_admission_token(token, projection=projection)
    expected = (
        ia.profile_identity, ia.profile_version, ia.release_identity, ia.release_fingerprint,
        ia.lifecycle_scope_fingerprint, ia.plan_identity, ia.plan_fingerprint,
        ia.capability_declaration_identity, ia.capability_declaration_fingerprint,
        ia.projection_fingerprint,
    )
    actual = (
        projection.profile_identity, projection.profile_version,
        projection.release_identity, projection.release_fingerprint,
        projection.lifecycle_scope_fingerprint, projection.plan_identity,
        projection.plan_fingerprint, projection.capability_declaration_identity,
        projection.capability_declaration_fingerprint, projection.projection_fingerprint,
    )
    if expected != actual:
        raise PairedSemanticConformanceRejected(
            "invocation authorization differs from verified Release projection")
    return projection


def _secure_inputs(semantics, token, projection_evidence, invocation, ia, authorization):
    if type(invocation) is not VerifiedPairedRendererInvocation:
        raise PairedSemanticConformanceRejected("exact verified paired invocation required")
    projection = _derived_projection(semantics, token, ia)
    try:
        verified = reverify_paired_renderer_invocation_evidence(
            projection=projection, authorization=ia, upstream_admission=token,
            projection_evidence=projection_evidence, invocation=invocation)
    except Exception as exc:
        raise PairedSemanticConformanceRejected(f"invocation re-verification failed: {exc}") from exc
    a = _validate_authorization(
        authorization, projection, verified.artifact_bytes,
        invocation_authorization=ia, invocation_evidence_fingerprint=verified.fingerprint)
    return projection, verified, a, verify_exact_paired_html(
        verified.artifact_bytes, projection=projection)


def _persisted_document(projection, invocation, ia, a, report):
    document = {
        "evidence_identity": CONFORMANCE_EVIDENCE_IDENTITY,
        "policy_identity": CONFORMANCE_POLICY_IDENTITY,
        "profile_identity": CONFORMANCE_PROFILE_IDENTITY,
        "profile_version": CONFORMANCE_PROFILE_VERSION,
        "assessor": {"implementation": ASSESSOR_IMPLEMENTATION,
                     "source_digest": paired_assessor_source_digest()},
        "authorization": asdict(a),
        "release_closure": {
            "release_identity": projection.release_identity,
            "release_fingerprint": projection.release_fingerprint,
            "lifecycle_scope_fingerprint": projection.lifecycle_scope_fingerprint,
            "plan_identity": projection.plan_identity,
            "plan_fingerprint": projection.plan_fingerprint,
            "capability_declaration_identity": projection.capability_declaration_identity,
            "capability_declaration_fingerprint": projection.capability_declaration_fingerprint,
            "content_closure_fingerprint": projection.content_closure_fingerprint,
            "projection_fingerprint": projection.projection_fingerprint},
        "invocation": {"authorization_identity": ia.identity,
                       "authorization_fingerprint": ia.fingerprint,
                       "evidence_fingerprint": invocation.fingerprint,
                       "evidence_sha256": _sha256(invocation.evidence_bytes),
                       "artifact_path": str(invocation.artifact_path),
                       "evidence_path": str(invocation.evidence_path)},
        "artifact": {"sha256": report.artifact_sha256,
                     "byte_length": report.artifact_byte_length,
                     "media_type": _FIXED_MEDIA_TYPE},
        "findings": [], "semantic_report": asdict(report), "verdict": "approved",
        "authority_scope": "semantic-artifact-conformance-only",
        "manifest_authority": "absent", "distribution_authority": "absent",
        "successful_publication": "not-asserted",
        "trusted_process_limitation": "no security claim against a hostile interpreter",
        "fingerprint": ""}
    material = dict(document); material.pop("fingerprint")
    document["fingerprint"] = _sha256(_canonical(material))
    return document


def _evidence_location(value):
    if not isinstance(value, Path) or not value.is_absolute() or value.name != _EVIDENCE_FILENAME:
        raise PairedSemanticConformanceRejected("exact absolute conformance evidence path required")
    try:
        expected = os.stat(value.parent, follow_symlinks=False)
        parent = value.parent.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PairedSemanticConformanceRejected("evidence directory must pre-exist") from exc
    if parent != value.parent or not stat.S_ISDIR(expected.st_mode):
        raise PairedSemanticConformanceRejected("evidence directory is unsafe")
    fd = os.open(parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
                 getattr(os, "O_NOFOLLOW", 0))
    opened = os.fstat(fd)
    if (not stat.S_ISDIR(opened.st_mode)
            or (opened.st_dev, opened.st_ino) != (expected.st_dev, expected.st_ino)):
        os.close(fd)
        raise PairedSemanticConformanceRejected("evidence directory changed while opening")
    return fd


def _read_evidence(fd, name):
    f = os.open(name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=fd)
    try:
        before = os.fstat(f)
        if not stat.S_ISREG(before.st_mode) or not 0 < before.st_size <= _MAX_EVIDENCE_BYTES:
            raise PairedSemanticConformanceRejected("evidence is not a bounded regular file")
        data = bytearray()
        while len(data) < before.st_size:
            chunk = os.read(f, min(65536, before.st_size-len(data)))
            if not chunk: raise PairedSemanticConformanceRejected("evidence truncated")
            data.extend(chunk)
        if os.read(f, 1):
            raise PairedSemanticConformanceRejected("evidence grew during reload")
        after = os.fstat(f)
        if (before.st_dev, before.st_ino, before.st_size) != (after.st_dev, after.st_ino, after.st_size):
            raise PairedSemanticConformanceRejected("evidence changed during read")
        return bytes(data)
    finally: os.close(f)


def _reproduce(evidence, path, projection, invocation, ia, a, report):
    expected = _canonical(_persisted_document(projection, invocation, ia, a, report))
    try: parsed = json.loads(evidence.decode())
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PairedSemanticConformanceRejected("malformed conformance evidence") from exc
    if type(parsed) is not dict or evidence != expected:
        raise PairedSemanticConformanceRejected("evidence differs from independent reproduction")
    return VerifiedPairedSemanticArtifactConformance(evidence, path, parsed["fingerprint"], report)


def assess_persisted_paired_semantic_artifact_conformance(
    *, admitted_semantics: PairedSemanticInput, upstream_admission: PairedUpstreamAdmissionToken,
    projection_evidence: object, invocation: VerifiedPairedRendererInvocation,
    invocation_authorization: PairedTerminalRendererInvocationAuthorization,
    authorization: PairedTerminalSemanticArtifactConformanceAuthorization,
    evidence_path: Path) -> VerifiedPairedSemanticArtifactConformance:
    projection, invocation, a, report = _secure_inputs(
        admitted_semantics, upstream_admission, projection_evidence, invocation,
        invocation_authorization, authorization)
    evidence = _canonical(_persisted_document(projection, invocation, invocation_authorization, a, report))
    fd = _evidence_location(evidence_path); owned = None
    try:
        if os.listdir(fd): raise PairedSemanticConformanceRejected("evidence directory must be empty")
        f = os.open(evidence_path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                    getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=fd)
        try:
            st = os.fstat(f); owned = (st.st_dev, st.st_ino); view = memoryview(evidence)
            while view:
                count = os.write(f, view)
                if count <= 0: raise OSError("short write")
                view = view[count:]
            os.fsync(f)
        finally: os.close(f)
        os.fsync(fd)
        if set(os.listdir(fd)) != {evidence_path.name}:
            raise PairedSemanticConformanceRejected("conformance evidence inventory differs after write")
        persisted = _read_evidence(fd, evidence_path.name)
        result = _reproduce(persisted, evidence_path, projection, invocation,
                            invocation_authorization, a, report)
        if (_read_evidence(fd, evidence_path.name) != persisted
                or set(os.listdir(fd)) != {evidence_path.name}):
            raise PairedSemanticConformanceRejected("evidence or inventory changed during reload")
        return result
    except Exception as exc:
        if owned is not None:
            try:
                st = os.stat(evidence_path.name, dir_fd=fd, follow_symlinks=False)
                if (st.st_dev, st.st_ino) == owned: os.unlink(evidence_path.name, dir_fd=fd); os.fsync(fd)
            except FileNotFoundError: pass
        if isinstance(exc, PairedSemanticConformanceRejected): raise
        raise PairedSemanticConformanceRejected(str(exc)) from exc
    finally: os.close(fd)


def verify_persisted_paired_semantic_artifact_conformance(
    *, admitted_semantics: PairedSemanticInput, upstream_admission: PairedUpstreamAdmissionToken,
    projection_evidence: object, invocation: VerifiedPairedRendererInvocation,
    invocation_authorization: PairedTerminalRendererInvocationAuthorization,
    authorization: PairedTerminalSemanticArtifactConformanceAuthorization,
    evidence_path: Path) -> VerifiedPairedSemanticArtifactConformance:
    projection, invocation, a, report = _secure_inputs(
        admitted_semantics, upstream_admission, projection_evidence, invocation,
        invocation_authorization, authorization)
    fd = _evidence_location(evidence_path)
    try:
        if set(os.listdir(fd)) != {evidence_path.name}:
            raise PairedSemanticConformanceRejected("conformance evidence inventory differs")
        evidence = _read_evidence(fd, evidence_path.name)
        result = _reproduce(evidence, evidence_path, projection, invocation,
                            invocation_authorization, a, report)
        if (_read_evidence(fd, evidence_path.name) != evidence
                or set(os.listdir(fd)) != {evidence_path.name}):
            raise PairedSemanticConformanceRejected("evidence or inventory changed during reload")
        return result
    finally: os.close(fd)
