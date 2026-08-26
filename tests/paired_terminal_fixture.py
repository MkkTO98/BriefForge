"""Source-neutral, hand-authored fixtures for the TASK-067 paired capability.

This module constructs semantic DTOs only.  It never constructs or persists a
Candidate, Judgment, Ready, Release, Manifest, or governed evidence artifact.
"""
from __future__ import annotations

from dataclasses import asdict, replace
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

from briefforge.bcrp.model import BCRPBundle, BCRPRecord, Fingerprint
from briefforge.bcrp.canonical import fingerprint_bundle
from briefforge.renderer_compatibility_planning import (
    ACCEPTED_DECLARATION_PROFILE_ID, ACCEPTED_DECLARATION_PROFILE_VERSION,
    ACCEPTED_RENDERER_OWNER, ACCEPTED_RENDERER_ROLE, CAPABILITY_DECLARATION_CONTRACT,
    CapabilityClaim, RendererCapabilityDeclaration, VerifiedRendererCompatibilityPlan,
    compute_capability_declaration_fingerprint,
)
from briefforge.bounded_loopback_deployment import DeploymentRouteItem, DeploymentTarget
from briefforge_terminal_profile.profile import build_terminal_authority_profile

from briefforge_paired_terminal_profile.schema import (
    Obligation,
    PairedAdmissionEnvelope,
    PairedEditorialProjection,
    PairedRow,
    PairedSemanticInput,
    PairedTable,
    PairedValue,
    Provenance,
    QualificationEdge,
    RENDERER_REQUIREMENTS,
    Section,
    SectionChild,
    Statement,
)
from briefforge_paired_terminal_profile.profile import (
    PAIRED_CAPABILITY_DECLARATION_IDENTITY,
    PAIRED_SEMANTIC_EXTENSION_NAME, PAIRED_SEMANTIC_EXTENSION_OWNER,
    PAIRED_SEMANTIC_EXTENSION_VERSION, PAIRED_SEMANTIC_VALIDATION_CONTRACT,
    build_paired_semantic_extension,
    verify_full_upstream_paired_terminal_admission,
)
from briefforge_paired_terminal_profile.projection import (
    build_paired_editorial_projection, persist_paired_profile_projection_evidence,
)

PROFILE_ID = "briefforge:representative-paired-terminal-static-html-profile:3.0.0"
PROFILE_VERSION = "3.0.0"
SCHEMA_ID = "briefforge:representative-paired-static-html-projection-schema:1.0.0"
SCHEMA_VERSION = "1.0.0"
PROJECTION_IMPLEMENTATION = "briefforge_paired_terminal_profile.projection:1.0.0"
RENDERER_ID = "briefforge:representative-paired-static-html-renderer:1.0.0"
RENDERER_VERSION = "1.0.0"
CONFORMANCE_ID = "briefforge:representative-paired-static-html-conformance-profile:1.0.0"
CONFORMANCE_VERSION = "1.0.0"
_AUTHORITY_TEMPORARIES = []

COLUMN_IDS = (
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


def admission_envelope(**changes) -> PairedAdmissionEnvelope:
    """Already independently verified exact upstream bindings, not a chain stub."""
    values = dict(
        profile_identity=PROFILE_ID,
        profile_version=PROFILE_VERSION,
        release_identity="release:synthetic-paired-v3",
        release_fingerprint="1" * 64,
        lifecycle_scope_fingerprint="2" * 64,
        plan_identity="plan:synthetic-paired-v3",
        plan_fingerprint="3" * 64,
        capability_declaration_identity=PAIRED_CAPABILITY_DECLARATION_IDENTITY,
        capability_declaration_fingerprint="4" * 64,
    )
    values.update(changes)
    return PairedAdmissionEnvelope(**values)


def _value(row: int, state: str) -> PairedValue:
    raw = state == "raw"
    lexical = f"0.{row}25" if raw else f"-0.0{row}7"
    digits = lexical.lstrip("-").replace(".", "")
    coefficient = int(digits) * (-1 if lexical.startswith("-") else 1)
    scale = len(lexical.split(".")[1])
    suffix = "raw" if raw else "difference"
    return PairedValue(
        identity=f"value:synthetic-{row}:{suffix}",
        relationship_identity=f"synthetic-relationship-{row}",
        coefficient=coefficient,
        scale=scale,
        value_state="present",
        lexical_representation=lexical,
        transformation_identity=f"synthetic-{suffix}",
        transformation_state="raw" if raw else "first_difference",
        aligned_period=f"1990-{2010 + row}" if raw else f"1991-{2010 + row}",
        aligned_count=20 + row,
        unit_ref="unit:dimensionless",
        semantic_type_ref="semantic-type:coefficient",
        source_ref=f"source:synthetic-{row}",
        authority_ref="authority:synthetic-content",
        method_ref="synthetic-paired",
        package_identity=f"synthetic-package-{row}",
    )


def _row(row: int, qualification_count: int = 3) -> PairedRow:
    return PairedRow(
        identity=f"row:synthetic-{row}",
        order=row,
        relationship_identity=f"synthetic-relationship-{row}",
        relationship_label=f"Synthetic relationship {row} <literal>",
        row_statement_ref=f"statement:row-{row}",
        raw_value_ref=f"value:synthetic-{row}:raw",
        first_difference_value_ref=f"value:synthetic-{row}:difference",
        classification_ref=f"classification:synthetic-{row}",
        evidence_role_ref=f"evidence-role:synthetic-{row}",
        qualification_refs=tuple(
            f"qualification:synthetic-{row}-{order}" for order in range(qualification_count)
        ),
        provenance_refs=(f"provenance:row-{row}",),
    )


def complete_semantics(*, row_count: int = 7) -> PairedSemanticInput:
    """Complete seven-row/fourteen-value/five-column synthetic case by default."""
    row_statements = tuple(
        Statement(
            identity=f"statement:row-{i}", role="observation",
            text=f"Authored synthetic statement {i} & retained.",
            authority_ref="authority:synthetic-content",
            display_classification=f"classification:synthetic-{i}",
        )
        for i in range(1, row_count + 1)
    )
    qualification_statements = tuple(
        Statement(
            identity=f"statement:qualification-{i}", role="caveat",
            text=f"Synthetic qualification {i}.",
            authority_ref="authority:synthetic-content",
            display_classification="classification:caveat",
        )
        for i in range(1, row_count + 1)
    )
    statements = (
        Statement("statement:introduction", "context", "Synthetic paired comparison.",
                  "authority:synthetic-content", None),
    ) + row_statements + qualification_statements
    source_child = () if row_count == 16 else (SectionChild("provenance", "provenance:source"),)
    sections = (
        Section(
            "section:root", "Synthetic brief <root>", 1,
            (SectionChild("section", "section:table"),
             SectionChild("section", "section:support")),
        ),
        Section(
            "section:table", "Paired values & rows", 2,
            (SectionChild("statement", "statement:introduction"),
             SectionChild("table", "table:synthetic-paired"))
            + tuple(SectionChild("statement", f"statement:row-{i}") for i in range(1, row_count + 1)),
        ),
        Section(
            "section:support", "Qualifications & attachments", 3,
            tuple(SectionChild("statement", f"statement:qualification-{i}")
                  for i in range(1, row_count + 1))
            + source_child
            + (SectionChild("obligation", "obligation:preserve"),
               SectionChild("obligation", "obligation:qualification")),
        ),
    )
    values = tuple(value for i in range(1, row_count + 1)
                   for value in (_value(i, "raw"), _value(i, "difference")))
    # Keep the exact seven-row topology fixture at three edges per row.  Generic
    # larger cases use one row-closure edge so sixteen rows are reachable under
    # the independent twenty-seven-edge frontier.
    qualification_count = 3 if row_count <= 9 else 1
    rows = tuple(_row(i, qualification_count) for i in range(1, row_count + 1))
    qualifications = tuple(
        QualificationEdge(
            identity=f"qualification:synthetic-{i}-{order}", kind="limits-target",
            source_ref=f"statement:qualification-{i}",
            target_ref=target,
            target_order=order,
            authority_ref="authority:synthetic-content",
        )
        for i in range(1, row_count + 1)
        for order, target in enumerate((
            f"statement:row-{i}",
            f"value:synthetic-{i}:raw",
            f"value:synthetic-{i}:difference",
        )[:qualification_count])
    )
    source_provenance = Provenance(
        identity="provenance:source", citation="Synthetic source <not a URL>",
        authority_ref="authority:synthetic-content", source_commit="a" * 40,
        source_snapshot_identity="snapshot:synthetic", source_locator=None,
        package_identities=("synthetic-source-package",),
        target_refs=tuple(v.identity for v in values), target_rule="exact-targets",
        placement_ref="section:support",
    )
    row_provenance = tuple(
        Provenance(
            identity=f"provenance:row-{i}", citation=f"Synthetic row source {i}",
            authority_ref="authority:synthetic-content", source_commit=None,
            source_snapshot_identity=None, source_locator=f"locator:row-{i}",
            package_identities=(f"synthetic-package-{i}", f"synthetic-difference-package-{i}"),
            target_refs=(f"statement:row-{i}", f"value:synthetic-{i}:raw",
                         f"value:synthetic-{i}:difference"),
            target_rule="exact-targets", placement_ref=f"row:synthetic-{i}",
        )
        for i in range(1, row_count + 1)
    )
    # At the exact sixteen-row frontier, use the sixteen row-owned provenance
    # objects only.  The frozen profile permits at most sixteen provenance
    # objects; the source-level object is not required for this synthetic
    # boundary variant.
    provenance = row_provenance if row_count == 16 else (source_provenance,) + row_provenance

    obligations = (
        Obligation(
            "obligation:preserve", "preserve-source-meaning",
            tuple(statement.identity for statement in statements),
            "authority:synthetic-content", "section:support",
        ),
        Obligation(
            "obligation:qualification", "qualification-display",
            tuple(edge.identity for edge in qualifications),
            "authority:synthetic-content", "section:support",
        ),
    )
    table = PairedTable(
        identity="table:synthetic-paired", purpose_ref="statement:introduction",
        column_identities=COLUMN_IDS, column_headings=COLUMN_HEADINGS,
        rows=rows, authority_ref="authority:synthetic-content",
    )
    return PairedSemanticInput(
        sections=sections, statements=statements, table=table,
        values=values, qualifications=qualifications, provenance=provenance,
        obligations=obligations,
        evidence_snapshots=("snapshot:synthetic",),
        external_references=(),
        content_authorities=("authority:synthetic-content",),
        renderer_requirements=RENDERER_REQUIREMENTS,
        renderer_mappings=tuple((row.identity, row.relationship_identity) for row in rows),
    )


def paired_semantic_extension(semantics: PairedSemanticInput) -> dict:
    """Build the exact source-neutral governed Candidate extension."""
    return build_paired_semantic_extension(
        semantics, candidate_identity="candidate:synthetic-paired")

def _paired_declaration() -> RendererCapabilityDeclaration:
    claims = (
        CapabilityClaim("capability:paired-static-html", "static",
                        ("one-standalone-html", "no-external-assets"), True),
    )
    provisional = RendererCapabilityDeclaration(
        PAIRED_CAPABILITY_DECLARATION_IDENTITY, CAPABILITY_DECLARATION_CONTRACT,
        ACCEPTED_DECLARATION_PROFILE_ID, ACCEPTED_DECLARATION_PROFILE_VERSION,
        RENDERER_ID, RENDERER_VERSION, ACCEPTED_RENDERER_OWNER,
        ACCEPTED_RENDERER_ROLE, "2026-08-02T09:59:00Z", True, claims, (),
        ("deterministic", "bounded", "offline"), (), "",
    )
    return replace(provisional,
        fingerprint=compute_capability_declaration_fingerprint(provisional))


def _synthetic_chain(semantics: PairedSemanticInput, binding: PairedAdmissionEnvelope,
                     authorities: list[dict], declaration: RendererCapabilityDeclaration
                     ) -> tuple[BCRPBundle, VerifiedRendererCompatibilityPlan]:
    ids = ["brief:synthetic-paired", "material:synthetic-paired",
           "candidate:synthetic-paired", "judgment:synthetic-paired",
           "ready:synthetic-paired", binding.release_identity,
           declaration.identity, binding.plan_identity,
           "artifact-audit:synthetic-paired", "artifact-conformance:synthetic-paired"]
    records = (
        BCRPRecord("PresentationBriefRecord", ids[0], "1.0.0", {}, []),
        BCRPRecord("PortablePresentationMaterialRecord", ids[1], "1.0.0",
                   {"authorities": authorities}, []),
        BCRPRecord("CandidatePresentationPackageRecord", ids[2], "1.0.0", {},
                   [paired_semantic_extension(semantics)]),
        BCRPRecord("ValidationJudgmentRecord", ids[3], "1.0.0",
                   {"candidate_ref": ids[2], "valid": True}, []),
        BCRPRecord("ReadyPresentationPackageRecord", ids[4], "1.0.0",
                   {"candidate_ref": ids[2], "judgment_ref": ids[3]}, []),
        BCRPRecord("PublicationReleaseRecord", ids[5], "1.0.0",
                   {"ready_ref": ids[4], "lifecycle_status": "current"}, []),
        BCRPRecord("RendererCapabilityDeclarationRecord", ids[6], "1.0.0", {
            "declaration_identity": declaration.identity,
            "renderer_id": declaration.renderer_identity,
            "renderer_version": declaration.renderer_version,
            "capabilities": [item.identity for item in declaration.capabilities],
        }, []),
        BCRPRecord("RendererCompatibilityPlanRecord", ids[7], "1.0.0", {
            "ready_ref": ids[4], "renderer_capability_ref": ids[6],
            "supported": True, "mode": "static",
            "declared_transformations": [], "fallbacks": [],
        }, []),
        BCRPRecord("GeneratedArtifactAuditRecord", ids[8], "1.0.0", {
            "release_ref": ids[5], "ready_ref": ids[4], "plan_ref": ids[7],
            "renderer_capability_ref": ids[6], "audit_links_pass": True,
        }, []),
        BCRPRecord("SemanticArtifactConformanceRecord", ids[9], "1.0.0", {
            "audit_ref": ids[8], "ready_ref": ids[4],
            "audit_link_pass": True, "semantic_pass": True,
        }, []),
    )
    bundle = BCRPBundle("briefforge-core-representation-profile", "1.0.0", records)
    prefix = BCRPBundle(bundle.profile_identity, bundle.profile_version, records[:8])
    fp = Fingerprint("profile-instance", records[0].identity, prefix.profile_identity,
        prefix.profile_version, "bcrp-semantic-c14n-v1", "sha256",
        binding.plan_fingerprint, "synthetic verified Plan closure")
    document = json.dumps({"profile_identity": prefix.profile_identity,
        "profile_version": prefix.profile_version,
        "records": [record.to_document() for record in prefix.records]},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    verified = VerifiedRendererCompatibilityPlan(document, fp, "[]")
    return bundle, verified


def admitted_semantics(semantics: PairedSemanticInput | None = None, *, envelope=None):
    """Issue a genuine process-local admission from one exact synthetic chain."""
    semantics = semantics or complete_semantics()
    binding = envelope or admission_envelope()
    temporary = tempfile.TemporaryDirectory()
    _AUTHORITY_TEMPORARIES.append(temporary)
    root = Path(temporary.name)
    directories = tuple(root / name for name in ("destination", "delivery", "deployment", "verification"))
    for directory in directories:
        directory.mkdir(); directory.chmod(0o700)
    authority_profile = build_terminal_authority_profile(
        destination_parent=directories[0], destination_basename="paired.html",
        delivery_ledger=directories[1],
        target=DeploymentTarget("127.0.0.1", 38127, "http://127.0.0.1:38127"),
        routes=(DeploymentRouteItem("/paired.html", "paired.html", "text/html"),),
        deployment_ledger=directories[2], verification_ledger=directories[3],
        content_authorities=({"id": "authority:synthetic-content",
                              "owner_identity": "project:BriefForge",
                              "role": "presentation-content-authority",
                              "scope": "released-synthetic-paired-content"},),
    )
    authorities = [dict(item) for item in authority_profile.authorities]
    declaration = _paired_declaration()
    binding = replace(binding,
        capability_declaration_identity=declaration.identity,
        capability_declaration_fingerprint=declaration.fingerprint)
    chain, plan = _synthetic_chain(semantics, binding, authorities, declaration)
    binding = replace(binding, plan_fingerprint=plan.fingerprint.digest)
    release = SimpleNamespace(
        release=SimpleNamespace(identity=binding.release_identity),
        fingerprint=SimpleNamespace(digest=binding.release_fingerprint), bundle=chain,
    )
    lifecycle = SimpleNamespace(inventory_digest=binding.lifecycle_scope_fingerprint)
    with patch("briefforge_paired_terminal_profile.profile.verify_publication_release",
               return_value=release), patch(
        "briefforge_paired_terminal_profile.profile.verify_renderer_compatibility_plan",
        return_value=plan,
    ):
        token = verify_full_upstream_paired_terminal_admission(
            release_bundle=object(), evidence_snapshot=object(), lifecycle_scope=lifecycle,
            declaration=declaration, planning_authorization=object(), plan_bundle=object())
    return token


def synthetic_predecessor(token) -> BCRPBundle:
    """Complete the exact admitted eight-record prefix with synthetic audit evidence."""
    records = tuple(BCRPRecord.from_document(item) for item in token._plan_documents)
    ready, release, capability, plan = records[4], records[5], records[6], records[7]
    audit = BCRPRecord("GeneratedArtifactAuditRecord", "artifact-audit:synthetic-paired", "1.0.0", {
        "release_ref": release.identity, "ready_ref": ready.identity,
        "plan_ref": plan.identity, "renderer_capability_ref": capability.identity,
        "audit_links_pass": True,
    }, [])
    conformance = BCRPRecord("SemanticArtifactConformanceRecord",
        "artifact-conformance:synthetic-paired", "1.0.0", {
            "audit_ref": audit.identity, "ready_ref": ready.identity,
            "audit_link_pass": True, "semantic_pass": True,
        }, [])
    return BCRPBundle("briefforge-core-representation-profile", "1.0.0",
                      records + (audit, conformance))


def projection(*, row_count: int = 7, envelope=None,
               semantics: PairedSemanticInput | None = None) -> PairedEditorialProjection:
    semantic = semantics or complete_semantics(row_count=row_count)
    return build_paired_editorial_projection(
        admitted=admitted_semantics(semantic, envelope=envelope))


def persisted_projection_evidence(projection, token, parent: Path):
    directory = parent / "profile-projection"
    directory.mkdir()
    return persist_paired_profile_projection_evidence(
        projection=projection, upstream_admission=token,
        evidence_directory=directory.resolve(), evidence_filename="evidence.json")


def replaced_semantics(semantics: PairedSemanticInput, **changes) -> PairedSemanticInput:
    return replace(semantics, **changes)


def task064_topology_semantics() -> PairedSemanticInput:
    """Construct a non-governed DTO that mechanically matches TASK-064 topology.

    The production package remains source-neutral.  This test-only proof reads the
    frozen TASK-064 blueprint to exercise its exact 76/27/5/8/7/14 shape and
    authored identities without creating a Candidate or consuming an attempt.
    Text and coefficient payloads remain deliberately synthetic.
    """
    path = (Path(__file__).parents[1] / "artifacts" / "reports" /
            "R-20260801-task-064-source-to-candidate-authoring-blueprint.json")
    blueprint = json.loads(path.read_text(encoding="utf-8"))
    hierarchy = blueprint["deterministic_section_hierarchy"]
    statement_ids = tuple(
        item["statement_id"] for item in blueprint["statement_contract"]["ledger_statement_index"]
    )
    if len(statement_ids) != 76 or len(set(statement_ids)) != 76:
        raise AssertionError("authoritative TASK-064 statement inventory drifted")

    conditional = tuple(item["statement_id"] for item in blueprint["conditional_composition"])
    sections = []
    for entry in hierarchy:
        child_ids = list(entry["children"])
        if entry["section_id"] == "section:task065-interpretation":
            child_ids.extend(item for item in conditional if item not in child_ids)
        if entry["section_id"] == "section:task065-provenance-and-obligations":
            child_ids.append("obligation:future-work-language-task065")
        children = tuple(
            SectionChild(
                "section" if target.startswith("section:") else
                "statement" if target.startswith("statement:") else
                "table" if target.startswith("table:") else
                "provenance" if target.startswith("provenance:") else "obligation",
                target,
            ) for target in child_ids
        )
        sections.append(Section(entry["section_id"], f"Synthetic {entry['section_id']}",
                                entry["order"], children))

    ordered_statement_ids = tuple(
        child.target_ref for section in sections for child in section.children
        if child.kind == "statement"
    )
    if set(ordered_statement_ids) != set(statement_ids) or len(ordered_statement_ids) != 76:
        raise AssertionError("TASK-064 hierarchy and statement inventory differ")
    qualification_targets = blueprint["qualification_targets"]
    statements = tuple(
        Statement(identity, "caveat" if identity in qualification_targets else "observation",
                  f"Synthetic governed meaning for {identity}.",
                  "authority:synthetic-content",
                  f"classification:{identity.split(':', 1)[1]}" if "-row-" in identity else None)
        for identity in ordered_statement_ids
    )

    edges = []
    edge_refs_by_source = {}
    for source, targets in qualification_targets.items():
        refs = []
        for order, target in enumerate(targets):
            identity = f"qualification:{source.split(':', 1)[1]}-{order}"
            refs.append(identity)
            edges.append(QualificationEdge(identity, "limits-target", source, target, order,
                                           "authority:synthetic-content"))
        edge_refs_by_source[source] = tuple(refs)
    qualifications = tuple(edges)
    if len(qualifications) != 27:
        raise AssertionError("authoritative TASK-064 qualification inventory drifted")

    provenance_specs = blueprint["provenance_attachments"]
    row_provenance_by_targets = {
        tuple(item["targets"]): item for item in provenance_specs[1:]
    }
    rows = []
    values = []
    table_contract = blueprint["table_contract"]
    for order, row_id in enumerate(table_contract["row_ids"], 1):
        cell = table_contract["cell_contract"][row_id]
        relationship = cell["relationship_case"]
        raw_id = cell["raw_coefficient"]
        difference_id = cell["first_difference_coefficient"]
        row_statement = f"statement:task065-row-{order:02d}"
        source = f"statement:task065-qualification-{order:02d}"
        prov = row_provenance_by_targets[(row_statement, raw_id, difference_id)]
        for value_id, state, lexical, meta, package in (
            (raw_id, "raw", f"0.{order}25", cell["raw_state"], prov["package_ids"][0]),
            (difference_id, "first_difference", f"-0.0{order}7",
             cell["first_difference_state"], prov["package_ids"][1]),
        ):
            digits = lexical.lstrip("-").replace(".", "")
            coefficient = int(digits) * (-1 if lexical.startswith("-") else 1)
            values.append(PairedValue(
                value_id, relationship, coefficient, len(lexical.split(".")[1]), "present",
                lexical, f"task064-{state}-v1@1.0", state, meta["period"],
                meta["aligned_count"], "unit:dimensionless",
                "semantic-type:pearson-coefficient", f"external:task064-row-{order}",
                "authority:synthetic-content", "pearson-paired-v1@1.0", package,
            ))
        rows.append(PairedRow(
            row_id, order, relationship, f"Synthetic label for {relationship}", row_statement,
            raw_id, difference_id, f"classification:{relationship}",
            f"evidence-role:{relationship}", edge_refs_by_source[source],
            (prov["provenance_id"],),
        ))

    provenance = []
    source = provenance_specs[0]
    provenance.append(Provenance(
        source["provenance_id"], "Synthetic TASK-064 source snapshot",
        "authority:synthetic-content", source["source_commit"], source["source_snapshot"],
        None, (), tuple(source["targets"]), "exact-targets",
        "section:task065-provenance-and-obligations",
    ))
    for item in provenance_specs[1:]:
        row_id = next(row.identity for row in rows if row.row_statement_ref == item["targets"][0])
        provenance.append(Provenance(
            item["provenance_id"], "Synthetic TASK-064 row source",
            "authority:synthetic-content", None, None, item["source_locator"],
            tuple(item["package_ids"]), tuple(item["targets"]), "exact-targets", row_id,
        ))

    obligation_kinds = {
        "obligation:preserve-source-meaning-task065": "preserve-source-meaning",
        "obligation:display-source-task065": "source-display",
        "obligation:qualification-attachment-task065": "qualification-display",
        "obligation:display-exclusions-task065": "exclusion-display",
        "obligation:future-work-language-task065": "future-work-language",
    }
    obligations = tuple(
        Obligation(item["obligation_id"], obligation_kinds[item["obligation_id"]],
                   tuple(item["targets"]), "authority:synthetic-content",
                   "section:task065-provenance-and-obligations")
        for item in blueprint["obligation_attachments"]
    )
    table = PairedTable(
        table_contract["table_identity"], "statement:task065-introduction",
        tuple(table_contract["column_ids"]), tuple(table_contract["headings"]),
        tuple(rows), "authority:synthetic-content",
    )
    return PairedSemanticInput(
        tuple(sections), statements, table, tuple(values), qualifications,
        tuple(provenance), obligations, (source["source_snapshot"],),
        tuple(f"external:task064-row-{i}" for i in range(1, 8)),
        ("authority:synthetic-content",), RENDERER_REQUIREMENTS,
        tuple((row.identity, row.relationship_identity) for row in rows),
    )
