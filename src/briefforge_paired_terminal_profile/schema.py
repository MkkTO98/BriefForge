"""Immutable, source-neutral DTOs for the paired terminal projection schema.

This module deliberately has no dependency on BCRP, Release, Plan, or renderer
code.  It defines the exact in-memory wire shape and its closed semantic
constraints only.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

SCHEMA_IDENTITY = "briefforge:representative-paired-static-html-projection-schema:1.0.0"
SCHEMA_VERSION = "1.0.0"
PROFILE_IDENTITY = "briefforge:representative-paired-terminal-static-html-profile:3.0.0"
PROFILE_VERSION = "3.0.0"
PROJECTION_IMPLEMENTATION = "briefforge_paired_terminal_profile.projection:1.0.0"
RENDERER_REQUIREMENTS = (
    ("renderer", "briefforge:representative-paired-static-html-renderer:1.0.0"),
    ("media-type", "text/html;charset=utf-8"),
    ("output-count", "1"),
    ("asset-count", "0"),
    ("table-count", "1"),
    ("column-count", "5"),
)

COLUMN_IDENTITIES = (
    "column:relationship-case",
    "column:raw-pearson-coefficient",
    "column:raw-state",
    "column:first-difference-pearson-coefficient",
    "column:first-difference-state",
)
COLUMN_HEADINGS = (
    "Relationship case",
    "Raw Pearson coefficient",
    "Raw state",
    "First-difference Pearson coefficient",
    "First-difference state",
)

_IDENTITY = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_DECIMAL = re.compile(r"^(-?)([0-9]+)(?:\.([0-9]+))?$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")
_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._@-]*$")
_PERIOD = re.compile(r"^[0-9]{4}-[0-9]{4}$")


class PairedSchemaRejected(ValueError):
    """The exact paired schema or its closed topology was not supplied."""


@dataclass(frozen=True)
class PairedAdmissionEnvelope:
    profile_identity: str
    profile_version: str
    release_identity: str
    release_fingerprint: str
    lifecycle_scope_fingerprint: str
    plan_identity: str
    plan_fingerprint: str
    capability_declaration_identity: str
    capability_declaration_fingerprint: str


@dataclass(frozen=True)
class SectionChild:
    kind: str
    target_ref: str


@dataclass(frozen=True)
class Section:
    identity: str
    title: str
    order: int
    children: tuple[SectionChild, ...]


@dataclass(frozen=True)
class Statement:
    identity: str
    role: str
    text: str
    authority_ref: str
    display_classification: str | None


@dataclass(frozen=True)
class QualificationEdge:
    identity: str
    kind: str
    source_ref: str
    target_ref: str
    target_order: int
    authority_ref: str


@dataclass(frozen=True)
class Obligation:
    identity: str
    kind: str
    target_refs: tuple[str, ...]
    authority_ref: str
    placement_ref: str


@dataclass(frozen=True)
class Provenance:
    identity: str
    citation: str
    authority_ref: str
    source_commit: str | None
    source_snapshot_identity: str | None
    source_locator: str | None
    package_identities: tuple[str, ...]
    target_refs: tuple[str, ...]
    target_rule: str
    placement_ref: str


@dataclass(frozen=True)
class PairedValue:
    identity: str
    relationship_identity: str
    coefficient: int
    scale: int
    value_state: str
    lexical_representation: str
    transformation_identity: str
    transformation_state: str
    aligned_period: str
    aligned_count: int
    unit_ref: str
    semantic_type_ref: str
    source_ref: str
    authority_ref: str
    method_ref: str
    package_identity: str


@dataclass(frozen=True)
class PairedRow:
    identity: str
    order: int
    relationship_identity: str
    relationship_label: str
    row_statement_ref: str
    raw_value_ref: str
    first_difference_value_ref: str
    classification_ref: str
    evidence_role_ref: str
    qualification_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class PairedTable:
    identity: str
    purpose_ref: str
    column_identities: tuple[str, ...]
    column_headings: tuple[str, ...]
    rows: tuple[PairedRow, ...]
    authority_ref: str


@dataclass(frozen=True)
class PairedSemanticInput:
    sections: tuple[Section, ...]
    statements: tuple[Statement, ...]
    table: PairedTable
    values: tuple[PairedValue, ...]
    qualifications: tuple[QualificationEdge, ...]
    provenance: tuple[Provenance, ...]
    obligations: tuple[Obligation, ...]
    evidence_snapshots: tuple[str, ...]
    external_references: tuple[str, ...]
    content_authorities: tuple[str, ...]
    renderer_requirements: tuple[tuple[str, str], ...]
    renderer_mappings: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class PairedEditorialProjection:
    schema_identity: str
    schema_version: str
    profile_identity: str
    profile_version: str
    projection_implementation: str
    release_identity: str
    release_fingerprint: str
    lifecycle_scope_fingerprint: str
    plan_identity: str
    plan_fingerprint: str
    capability_declaration_identity: str
    capability_declaration_fingerprint: str
    sections: tuple[Section, ...]
    statements: tuple[Statement, ...]
    table: PairedTable
    values: tuple[PairedValue, ...]
    qualifications: tuple[QualificationEdge, ...]
    provenance: tuple[Provenance, ...]
    obligations: tuple[Obligation, ...]
    evidence_snapshots: tuple[str, ...]
    external_references: tuple[str, ...]
    content_authorities: tuple[str, ...]
    renderer_requirements: tuple[tuple[str, str], ...]
    renderer_mappings: tuple[tuple[str, str], ...]
    content_closure_fingerprint: str
    projection_fingerprint: str


def _reject(message: str) -> None:
    raise PairedSchemaRejected(message)


def _text(value: object, label: str, *, maximum: int | None = None) -> str:
    if type(value) is not str or not value or "\x00" in value:
        _reject(f"{label} requires nonempty exact text")
    if maximum is not None and len(value.encode("utf-8")) > maximum:
        _reject(f"{label} exceeds its UTF-8 byte bound")
    return value


def _identity(value: object, label: str) -> str:
    text = _text(value, label)
    if not _IDENTITY.fullmatch(text):
        _reject(f"{label} is not a canonical identity")
    return text


def _token(value: object, label: str, *, maximum: int = 512) -> str:
    text = _text(value, label, maximum=maximum)
    if not _TOKEN.fullmatch(text):
        _reject(f"{label} is not a bounded token")
    return text


def _exact_tuple(value: object, member_type: type, label: str) -> tuple:
    if type(value) is not tuple or not all(type(item) is member_type for item in value):
        _reject(f"{label} requires an exact immutable tuple")
    return value


def _string_tuple(value: object, label: str, *, minimum: int = 0, maximum: int | None = None) -> tuple[str, ...]:
    if type(value) is not tuple or not all(type(item) is str and item for item in value):
        _reject(f"{label} requires an exact immutable text tuple")
    if len(value) < minimum or (maximum is not None and len(value) > maximum):
        _reject(f"{label} cardinality is outside the closed bound")
    if len(value) != len(set(value)):
        _reject(f"{label} contains duplicates")
    return value


def _pairs(value: object, label: str) -> tuple[tuple[str, str], ...]:
    if type(value) is not tuple or not all(
        type(item) is tuple and len(item) == 2 and all(type(part) is str and part for part in item)
        for item in value
    ):
        _reject(f"{label} requires exact immutable text pairs")
    if len(value) != len(set(value)):
        _reject(f"{label} contains duplicate mappings")
    return value


def validate_admission_envelope(envelope: object) -> PairedAdmissionEnvelope:
    if type(envelope) is not PairedAdmissionEnvelope:
        _reject("exact paired admission envelope required")
    if (envelope.profile_identity, envelope.profile_version) != (PROFILE_IDENTITY, PROFILE_VERSION):
        _reject("unknown paired profile identity or version")
    for name in ("release_identity", "plan_identity", "capability_declaration_identity"):
        _identity(getattr(envelope, name), name)
    for name in ("release_fingerprint", "lifecycle_scope_fingerprint", "plan_fingerprint",
                 "capability_declaration_fingerprint"):
        value = getattr(envelope, name)
        if type(value) is not str or not _DIGEST.fullmatch(value):
            _reject(f"{name} requires an exact SHA-256 digest")
    return envelope


def _validate_decimal(value: PairedValue) -> None:
    if type(value.coefficient) is not int or type(value.scale) is not int or not 0 <= value.scale <= 18:
        _reject("paired value coefficient/scale must be exact bounded integers")
    lexical = _text(value.lexical_representation, "value lexical representation")
    match = _DECIMAL.fullmatch(lexical)
    if match is None:
        _reject("value lexical representation is not an exact finite decimal")
    fraction = match.group(3) or ""
    if len(fraction) != value.scale:
        _reject("value lexical scale differs from the declared scale")
    computed = int(match.group(2) + fraction)
    if match.group(1):
        computed = -computed
    if computed != value.coefficient or (computed == 0 and bool(match.group(1))):
        _reject("value lexical coefficient or sign differs")


def validate_paired_semantics(semantics: object) -> PairedSemanticInput:
    if type(semantics) is not PairedSemanticInput:
        _reject("exact paired semantic input required")
    sections = _exact_tuple(semantics.sections, Section, "sections")
    statements = _exact_tuple(semantics.statements, Statement, "statements")
    values = _exact_tuple(semantics.values, PairedValue, "values")
    qualifications = _exact_tuple(semantics.qualifications, QualificationEdge, "qualifications")
    provenance = _exact_tuple(semantics.provenance, Provenance, "provenance")
    obligations = _exact_tuple(semantics.obligations, Obligation, "obligations")
    if type(semantics.table) is not PairedTable:
        _reject("exactly one exact paired table is required")
    if not 2 <= len(sections) <= 8 or not 2 <= len(statements) <= 76:
        _reject("section or statement cardinality is outside the closed bound")
    if not 1 <= len(qualifications) <= 27 or not 1 <= len(provenance) <= 16 or not 1 <= len(obligations) <= 16:
        _reject("relation, provenance, or obligation cardinality is outside the closed bound")

    identity_objects = (*sections, *statements, semantics.table, *semantics.table.rows,
                        *values, *qualifications, *provenance, *obligations)
    identities = [_identity(item.identity, "semantic identity") for item in identity_objects]
    if len(identities) != len(set(identities)):
        _reject("semantic identities must be globally unique")
    known = set(identities)
    authority_ids = set(_string_tuple(semantics.content_authorities, "content authorities", minimum=1))
    for authority in authority_ids:
        _identity(authority, "content authority")

    # Exact depth-two authored composition: one root followed by ordered leaves.
    if tuple(section.order for section in sections) != tuple(range(1, len(sections) + 1)):
        _reject("section order must be 1-based contiguous authored order")
    root = sections[0]
    leaf_ids = tuple(section.identity for section in sections[1:])
    if tuple((child.kind, child.target_ref) for child in root.children) != tuple(("section", item) for item in leaf_ids):
        _reject("root must contain every leaf once in authored order")

    by_kind = {
        "section": {item.identity for item in sections},
        "statement": {item.identity for item in statements},
        "table": {semantics.table.identity},
        "provenance": {item.identity for item in provenance},
        "obligation": {item.identity for item in obligations},
    }
    composed_statements: list[str] = []
    table_occurrences = 0
    section_attachments: list[str] = []
    section_placement: dict[str, str] = {}
    for section in sections:
        _text(section.title, "section title", maximum=4096)
        children = _exact_tuple(section.children, SectionChild, "section children")
        if not 1 <= len(children) <= 32:
            _reject("children per section are outside the closed bound")
        if section is not root and any(child.kind == "section" for child in children):
            _reject("paired hierarchy has exact depth two")
        for child in children:
            if child.kind not in by_kind:
                _reject("unknown section child kind")
            _identity(child.target_ref, "section child reference")
            if child.target_ref not in by_kind[child.kind]:
                _reject("section child reference does not resolve by exact kind")
            if child.kind == "statement":
                composed_statements.append(child.target_ref)
            elif child.kind == "table":
                table_occurrences += 1
            elif child.kind in {"provenance", "obligation"}:
                section_attachments.append(child.target_ref)
                section_placement[child.target_ref] = section.identity
    if (composed_statements != [item.identity for item in statements]
            or len(composed_statements) != len(set(composed_statements))
            or table_occurrences != 1
            or len(section_attachments) != len(set(section_attachments))):
        _reject("authored section composition is not exact")

    statement_ids = {item.identity for item in statements}
    for item in statements:
        _text(item.role, "statement role")
        _text(item.text, "statement text", maximum=4096)
        if item.authority_ref not in authority_ids:
            _reject("statement authority is outside content authority closure")
        if item.display_classification is not None:
            _identity(item.display_classification, "display classification")

    table = semantics.table
    if (table.column_identities, table.column_headings) != (COLUMN_IDENTITIES, COLUMN_HEADINGS):
        _reject("paired table column contract differs")
    if table.authority_ref not in authority_ids or table.purpose_ref not in statement_ids:
        _reject("paired table purpose or authority does not resolve")
    rows = _exact_tuple(table.rows, PairedRow, "paired rows")
    if not 1 <= len(rows) <= 16 or len(values) != 2 * len(rows) or len(values) > 32:
        _reject("paired row/value cardinality differs")
    if tuple(row.order for row in rows) != tuple(range(1, len(rows) + 1)):
        _reject("row order must be 1-based contiguous authored order")
    row_statement_order = tuple(row.row_statement_ref for row in rows)
    row_statement_ids = set(row_statement_order)
    authored_row_statement_order = tuple(
        ref for ref in composed_statements if ref in row_statement_ids
    )
    if (len(row_statement_order) != len(row_statement_ids)
            or authored_row_statement_order != row_statement_order):
        _reject("authored row statement order differs from paired row order")
    relationship_ids = []
    consumed: list[str] = []
    consumed_row_provenance: list[str] = []
    value_by = {item.identity: item for item in values}
    qualification_by = {item.identity: item for item in qualifications}
    provenance_by = {item.identity: item for item in provenance}
    for row in rows:
        relationship_ids.append(_token(row.relationship_identity, "relationship identity"))
        _text(row.relationship_label, "relationship label", maximum=4096)
        if row.row_statement_ref not in statement_ids:
            _reject("row statement reference does not resolve")
        for ref in (row.classification_ref, row.evidence_role_ref):
            _identity(ref, "row semantic reference")
        qrefs = _string_tuple(row.qualification_refs, "row qualification references", minimum=1, maximum=3)
        prefs = _string_tuple(row.provenance_refs, "row provenance references", minimum=1, maximum=1)
        if not set(qrefs) <= set(qualification_by) or not set(prefs) <= set(provenance_by):
            _reject("row support reference does not resolve")
        raw = value_by.get(row.raw_value_ref)
        difference = value_by.get(row.first_difference_value_ref)
        if raw is None or difference is None or raw.transformation_state != "raw" or difference.transformation_state != "first_difference":
            _reject("row raw/first-difference pairing differs")
        if raw.identity == difference.identity:
            _reject("row reuses one value in both slots")
        if raw.relationship_identity != row.relationship_identity or difference.relationship_identity != row.relationship_identity:
            _reject("paired value relationship differs from its owning row")
        consumed.extend((raw.identity, difference.identity))
        closure = (row.row_statement_ref, raw.identity, difference.identity)
        row_edges = tuple(qualification_by[ref] for ref in qrefs)
        if (tuple(edge.target_ref for edge in row_edges) != closure[:len(row_edges)]
                or tuple(edge.target_order for edge in row_edges) != tuple(range(len(row_edges)))
                or len({edge.source_ref for edge in row_edges}) != 1):
            _reject("row qualifications do not preserve their ordered row/value closure")
        attachment = provenance_by[prefs[0]]
        if attachment.placement_ref != row.identity or attachment.target_refs != closure:
            _reject("row provenance does not preserve exact row/value closure")
        consumed_row_provenance.append(attachment.identity)
    if len(relationship_ids) != len(set(relationship_ids)) or consumed != [item.identity for item in values] or len(consumed) != len(set(consumed)):
        _reject("row ownership/order does not consume every paired value exactly once")
    if len(consumed_row_provenance) != len(set(consumed_row_provenance)):
        _reject("row provenance may not be borrowed across rows")

    for value in values:
        _validate_decimal(value)
        if value.value_state != "present" or value.transformation_state not in {"raw", "first_difference"}:
            _reject("paired value state is outside the closed vocabulary")
        if type(value.aligned_count) is not int or value.aligned_count <= 0:
            _reject("aligned count must be a positive exact integer")
        _token(value.relationship_identity, "value relationship identity")
        _token(value.transformation_identity, "transformation identity", maximum=256)
        period = _text(value.aligned_period, "aligned period", maximum=9)
        if not _PERIOD.fullmatch(period) or int(period[:4]) > int(period[5:]):
            _reject("aligned period is not an exact bounded year range")
        for name in ("unit_ref", "semantic_type_ref", "source_ref", "authority_ref"):
            _identity(getattr(value, name), name)
        _token(value.method_ref, "method reference", maximum=256)
        _token(value.package_identity, "package identity", maximum=512)
        if value.authority_ref not in authority_ids:
            _reject("value authority is outside content authority closure")

    target_ids = statement_ids | {item.identity for item in values} | {table.identity}
    grouped: dict[str, list[int]] = {}
    triples = set()
    for edge in qualifications:
        if edge.kind != "limits-target" or edge.source_ref not in statement_ids or edge.target_ref not in target_ids:
            _reject("qualification kind/source/target is outside the closed relation")
        if type(edge.target_order) is not int or edge.target_order < 0 or edge.authority_ref not in authority_ids:
            _reject("qualification order or authority differs")
        triple = (edge.kind, edge.source_ref, edge.target_ref)
        if triple in triples:
            _reject("duplicate qualification relation")
        triples.add(triple)
        grouped.setdefault(edge.source_ref, []).append(edge.target_order)
    if any(sorted(orders) != list(range(len(orders))) or len(orders) > 3 for orders in grouped.values()):
        _reject("qualification targets must be bounded and contiguously ordered per source")
    for statement in statements:
        if statement.role in {"caveat", "uncertainty"} and statement.identity not in grouped:
            _reject("every caveat or uncertainty statement requires a qualification")

    evidence = set(_string_tuple(semantics.evidence_snapshots, "evidence snapshots"))
    external = set(_string_tuple(semantics.external_references, "external references"))
    for ref in evidence | external:
        _identity(ref, "evidence/external reference")
    for item in provenance:
        _text(item.citation, "provenance citation", maximum=4096)
        if item.authority_ref not in authority_ids or item.target_rule != "exact-targets":
            _reject("provenance authority or target rule differs")
        packages = _string_tuple(item.package_identities, "provenance package identities", maximum=2)
        for package in packages:
            _token(package, "provenance package identity", maximum=512)
        targets = _string_tuple(item.target_refs, "provenance targets", minimum=1, maximum=92)
        if not set(targets) <= known:
            _reject("provenance target does not resolve exactly")
        if item.identity in consumed_row_provenance:
            if item.placement_ref not in {row.identity for row in rows}:
                _reject("row provenance placement does not resolve exactly")
        elif section_placement.get(item.identity) != item.placement_ref:
            _reject("section provenance is not consumed at its authored placement")
        snapshot_form = (item.source_commit is not None and item.source_snapshot_identity is not None and item.source_locator is None)
        locator_form = (item.source_commit is None and item.source_snapshot_identity is None and item.source_locator is not None)
        if not (snapshot_form or locator_form):
            _reject("provenance source combination is outside the closed table")
        if snapshot_form:
            if type(item.source_commit) is not str or not _COMMIT.fullmatch(item.source_commit) or item.source_snapshot_identity not in evidence:
                _reject("provenance commit/snapshot binding differs")
        else:
            _text(item.source_locator, "provenance source locator", maximum=4096)

    section_provenance = [ref for ref in section_attachments if ref in provenance_by]
    if (set(consumed_row_provenance) | set(section_provenance) != set(provenance_by)
            or set(consumed_row_provenance) & set(section_provenance)
            or len(consumed_row_provenance) + len(section_provenance) != len(provenance)):
        _reject("every provenance object must be consumed exactly once")

    obligation_kinds = {"preserve-source-meaning", "source-display", "qualification-display",
                        "exclusion-display", "future-work-language"}
    for item in obligations:
        if item.kind not in obligation_kinds or item.authority_ref not in authority_ids:
            _reject("obligation kind or authority differs")
        targets = _string_tuple(item.target_refs, "obligation targets", minimum=1, maximum=82)
        if not set(targets) <= known:
            _reject("obligation target does not resolve exactly")
        if section_placement.get(item.identity) != item.placement_ref:
            _reject("obligation is not consumed at its authored section placement")
    section_obligations = [ref for ref in section_attachments if ref in {item.identity for item in obligations}]
    if len(section_obligations) != len(obligations) or set(section_obligations) != {item.identity for item in obligations}:
        _reject("every obligation must be consumed exactly once")

    requirements = _pairs(semantics.renderer_requirements, "renderer requirements")
    if requirements != RENDERER_REQUIREMENTS:
        _reject("renderer requirements differ from the frozen static HTML contract")
    mappings = _pairs(semantics.renderer_mappings, "renderer mappings")
    expected_mappings = tuple((row.identity, row.relationship_identity) for row in rows)
    if mappings != expected_mappings:
        _reject("renderer mappings must consume every row in authored order")
    return semantics


def validate_paired_projection(projection: object) -> PairedEditorialProjection:
    if type(projection) is not PairedEditorialProjection:
        _reject("exact paired editorial projection required")
    if (projection.schema_identity, projection.schema_version, projection.profile_identity,
            projection.profile_version, projection.projection_implementation) != (
            SCHEMA_IDENTITY, SCHEMA_VERSION, PROFILE_IDENTITY, PROFILE_VERSION, PROJECTION_IMPLEMENTATION):
        _reject("projection schema/profile/implementation tuple differs")
    validate_admission_envelope(PairedAdmissionEnvelope(
        projection.profile_identity, projection.profile_version, projection.release_identity,
        projection.release_fingerprint, projection.lifecycle_scope_fingerprint,
        projection.plan_identity, projection.plan_fingerprint,
        projection.capability_declaration_identity, projection.capability_declaration_fingerprint,
    ))
    validate_paired_semantics(PairedSemanticInput(
        projection.sections, projection.statements, projection.table, projection.values,
        projection.qualifications, projection.provenance, projection.obligations,
        projection.evidence_snapshots, projection.external_references,
        projection.content_authorities, projection.renderer_requirements,
        projection.renderer_mappings,
    ))
    for name in ("content_closure_fingerprint", "projection_fingerprint"):
        value = getattr(projection, name)
        if type(value) is not str or not _DIGEST.fullmatch(value):
            _reject(f"{name} is not an exact SHA-256 digest")
    return projection
