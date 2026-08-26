"""BriefForge-owned synthetic TASK-060 representative authority-chain fixture.

This is intentionally neutral synthetic data: it models only bounded structural
and exact-value semantics, without any external domain specialization.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any

from briefforge.bcrp import RecordDraft, author_candidate_bundle
from briefforge.bcrp_legacy_compatibility import map_legacy_ready_to_bcrp
from briefforge.publication_release import produce_publication_release
from briefforge.renderer_compatibility_planning import (
    ACCEPTED_DECLARATION_PROFILE_ID,
    ACCEPTED_DECLARATION_PROFILE_VERSION,
    CAPABILITY_DECLARATION_CONTRACT,
    ACCEPTED_PLANNING_AUTHORITY_IDENTITY,
    ACCEPTED_PLANNING_AUTHORITY_OWNER,
    ACCEPTED_PLANNING_AUTHORITY_ROLE,
    PLANNING_POLICY_ID,
    CapabilityClaim,
    PlanningAuthorization,
    RendererCapabilityDeclaration,
    compute_capability_declaration_fingerprint,
    produce_renderer_compatibility_plan,
)
from tests import test_bcrp_lifecycle_authority_compatibility as compatibility_tests
from tests import test_bcrp_publication_release as release_tests
from tests import test_renderer_compatibility_planning as planning_tests

PROJECTION_PROFILE_ID = "briefforge:representative-static-html-projection-profile:1.0.0"
RENDERER_IDENTITY = "renderer:representative-static-html"
RENDERER_VERSION = "1.0.0"
RENDERER_ADAPTER_ID = "representative-static-html-renderer"
SEMANTIC_PROFILE_ID = "briefforge-static-html-semantic-realization-profile:2.0.0"
SEMANTIC_PROFILE_VERSION = "2.0.0"

GLOBAL_CONSTRAINT = "constraint:representative-static-html-profile-1.0.0"
REQUIREMENTS = (
    ("section-hierarchy", "fixed-two-level-section-hierarchy"),
    ("ordered-statements", "full-text-ordered-statements"),
    ("exact-quantitative-values", "exact-decimal-value-preservation"),
    ("qualification-attachments", "statement-targeted-qualification-edges"),
    ("provenance-references", "offline-complete-provenance"),
    ("complete-obligations", "complete-obligation-edges"),
    ("fixed-static-table", "fixed-five-column-paired-case-table"),
)
OPERATIONAL_AUTHORITIES = (
    {"id": "authority:briefforge-bcrp-validation", "owner_identity": "project:BriefForge", "role": "validation-authority", "scope": "BCRP-L0-L6"},
    {"id": "authority:briefforge-publication-release", "owner_identity": "project:BriefForge", "role": "publication-release-authority", "scope": "fixed-evidence-publication-release"},
    {"id": "authority:briefforge-controlled-renderer-invocation", "owner_identity": "project:BriefForge", "role": "renderer-invocation-authority", "scope": "one-controlled-renderer-invocation-act"},
    {"id": "authority:briefforge-semantic-artifact-conformance", "owner_identity": "project:BriefForge", "role": "semantic-artifact-conformance-assessor", "scope": "one-semantic-artifact-conformance-assessment"},
    {"id": "authority:briefforge-publication-manifest-projector", "owner_identity": "project:BriefForge", "role": "publication-manifest-projector", "scope": "one-publication-manifest-production"},
)
CONTENT_AUTHORITY = {
    "id": "authority:synthetic-representative-content",
    "owner_identity": "project:BriefForge",
    "role": "synthetic-content-authority",
    "scope": "task060-representative-fixture-only",
}


def _value(index: int) -> dict[str, Any]:
    identity = f"value:representative-{index:02d}"
    common = {
        "id": identity,
        "unit_ref": "unit:count" if index % 2 else "unit:ratio",
        "semantic_type_ref": "semantic-type:quantity" if index % 3 else "semantic-type:index",
        "source_ref": "external:representative-source",
        "authority_ref": CONTENT_AUTHORITY["id"],
    }
    if index == 12:
        return common | {"value_state": "explicit-zero", "payload": {"coefficient": "0", "scale": 0}}
    if index == 13:
        return common | {"value_state": "missing-not-provided", "reason": "The synthetic slot was deliberately not provided."}
    if index == 14:
        return common | {"value_state": "not-applicable", "reason": "The synthetic comparison does not apply to this slot."}
    value = common | {
        "value_state": "present",
        "payload": {"coefficient": str(10_000_000_000_000_000_000 + index), "scale": index % 5},
    }
    if index == 11:
        value |= {"approximate": True, "approximation": {"method": "bounded synthetic estimate", "bound": "within one authored slot"}}
    return value


def _target_sets() -> dict[str, list[str]]:
    cases = [f"case:representative-{i:02d}" for i in range(1, 8)]
    values = [f"value:representative-{i:02d}" for i in range(1, 15)]
    statements = [f"statement:representative-{name}" for name in ("alpha", "alpha-limit", "beta", "beta-limit")]
    return {
        "section-hierarchy": [
            "brief:representative", "candidate:representative", "purpose:brief-representative",
            "purpose:candidate-representative", "audience:brief-representative",
            "audience:candidate-representative", "section:representative-root",
            "section:representative-alpha", "section:representative-beta", "distribution:representative",
        ],
        "ordered-statements": statements,
        "exact-quantitative-values": cases + values + ["unit:count", "unit:ratio", "semantic-type:quantity", "semantic-type:index"],
        "qualification-attachments": [statements[1], statements[3], "relation:representative-alpha-limit", "relation:representative-beta-limit"],
        "provenance-references": [
            "material:representative", CONTENT_AUTHORITY["id"], "provenance:representative",
            "snapshot:representative", "external:representative-source",
        ],
        "complete-obligations": ["obligation:representative-source-display"],
        "fixed-static-table": ["exhibit:representative-table"] + cases + values,
    }


def candidate_bundle(snapshot, *, complete_audience_edge: bool = False):
    """Return the positive 3-section/4-statement/7-case/14-value BCRP Candidate."""
    targets = _target_sets()
    caveats = ["statement:representative-alpha-limit", "statement:representative-beta-limit"]
    requirements = []
    for stem, specific in REQUIREMENTS:
        requirements.append({
            "id": f"requirement:representative-{stem}",
            "capability": f"capability:representative-{stem}",
            "mandatory": True,
            "criticality": "required",
            "target_refs": sorted(targets[stem]),
            "authority_label_refs": [CONTENT_AUTHORITY["id"]],
            "caveat_refs": caveats if stem in {"ordered-statements", "qualification-attachments"} else [],
            "required_constraints": sorted((GLOBAL_CONSTRAINT, f"constraint:{specific}")),
            "permitted_transformations": [],
            "fallback_refs": [],
            "unsupported_allowed": False,
        })

    brief = RecordDraft("brief:representative", {
        "organizing_purpose": {"id": "purpose:brief-representative", "statement": "Present an exact bounded synthetic comparison."},
        "audiences": [{"id": "audience:brief-representative", "description": "A synthetic conformance reader <&>."}],
        "scope": "A fixed offline representative shape.",
        "non_scope": "No external data, interpretation, recommendation, or publication.",
    })
    values = [_value(i) for i in range(1, 15)]
    material = RecordDraft("material:representative", {
        "authorities": list(OPERATIONAL_AUTHORITIES) + [CONTENT_AUTHORITY],
        "provenance": [{"id": "provenance:representative", "citation": "BriefForge synthetic evidence <script>not markup</script>.", "authority_ref": CONTENT_AUTHORITY["id"]}],
        "evidence_snapshots": [{"id": "snapshot:representative", "version": "1", "content_fingerprint": f"sha256:{snapshot.inventory_digest}", "provenance_ref": "provenance:representative"}],
        "external_references": [{
            "id": "external:representative-source", "reference_kind": "synthetic-governed-fixture",
            "upstream_object_identity": "synthetic-object:representative-source", "snapshot_ref": "snapshot:representative",
            "provenance_ref": "provenance:representative", "authority_ref": CONTENT_AUTHORITY["id"],
        }],
        "units": [{"id": "unit:count", "description": "exact authored count"}, {"id": "unit:ratio", "description": "exact authored ratio"}],
        "semantic_types": [{"id": "semantic-type:quantity", "description": "synthetic quantity"}, {"id": "semantic-type:index", "description": "synthetic index"}],
        "values": values,
        "required_value_ids": [item["id"] for item in values],
        "consistency_assertions": [], "state_validations": [],
    })
    statements = [
        {"id": "statement:representative-alpha", "text": "Alpha preserves exact authored values & source identity.", "posture": "observation", "communication_functions": ["orient"], "attention": "primary", "purpose_ref": "purpose:candidate-representative", "authority_ref": CONTENT_AUTHORITY["id"], "upstream_refs": ["external:representative-source"], "requires_comparison_universe": False, "value_ref": "value:representative-01"},
        {"id": "statement:representative-alpha-limit", "text": "Alpha is bounded; do not infer beyond the fixture.", "posture": "caveat", "communication_functions": ["qualify"], "attention": "supporting", "purpose_ref": "purpose:candidate-representative", "authority_ref": CONTENT_AUTHORITY["id"], "upstream_refs": ["external:representative-source"], "requires_comparison_universe": False},
        {"id": "statement:representative-beta", "text": "Beta keeps explicit zero and absent states distinct.", "posture": "observation", "communication_functions": ["compare"], "attention": "primary", "purpose_ref": "purpose:candidate-representative", "authority_ref": CONTENT_AUTHORITY["id"], "upstream_refs": ["external:representative-source"], "requires_comparison_universe": False, "value_ref": "value:representative-12"},
        {"id": "statement:representative-beta-limit", "text": "Beta is uncertain outside the authored closure.", "posture": "uncertainty", "communication_functions": ["qualify"], "attention": "supporting", "purpose_ref": "purpose:candidate-representative", "authority_ref": CONTENT_AUTHORITY["id"], "upstream_refs": ["external:representative-source"], "requires_comparison_universe": False},
    ]
    cases = [{
        "id": f"case:representative-{i:02d}", "order": i,
        "primary_ref": f"value:representative-{2*i-1:02d}", "comparison_ref": f"value:representative-{2*i:02d}",
    } for i in range(1, 8)]
    candidate_audience = {
        "id": "audience:candidate-representative",
        "description": "A synthetic conformance reader <&>.",
    }
    # The fixed profile's Candidate audience schema is exactly {id, description}.
    # Keep the compatibility keyword while declining to synthesize an edge that
    # is absent from the normative admission matrix.
    candidate = RecordDraft("candidate:representative", {
        "brief_ref": "brief:representative", "material_refs": ["material:representative"],
        "organizing_purpose": {"id": "purpose:candidate-representative", "statement": "Present an exact bounded synthetic comparison.", "brief_purpose_ref": "purpose:brief-representative"},
        "audiences": [candidate_audience],
        "scope": "A fixed offline representative shape.", "non_scope": "No external data, interpretation, recommendation, or publication.",
        "statements": statements,
        "sections": [
            {"id": "section:representative-beta", "title": "Beta leaf", "children": ["statement:representative-beta", "statement:representative-beta-limit"]},
            {"id": "section:representative-root", "title": "Representative root", "children": ["section:representative-alpha", "section:representative-beta"]},
            {"id": "section:representative-alpha", "title": "Alpha <leaf>", "children": ["statement:representative-alpha", "exhibit:representative-table", "statement:representative-alpha-limit"]},
        ],
        "obligations": [{"id": "obligation:representative-source-display", "kind": "source-display", "authority_ref": CONTENT_AUTHORITY["id"], "target_refs": ["external:representative-source", "statement:representative-alpha", "statement:representative-beta"]}],
        "renderer_requirements": requirements, "fallbacks": [],
        "exhibits": [{"id": "exhibit:representative-table", "kind": "fixed-static-table", "purpose_ref": "purpose:candidate-representative", "case_bindings": cases, "value_ids": [item["id"] for item in values]}],
        "relations": [
            {"id": "relation:representative-alpha-limit", "kind": "limits-target", "source_ref": "statement:representative-alpha-limit", "target_ref": "statement:representative-alpha", "authority_ref": CONTENT_AUTHORITY["id"]},
            {"id": "relation:representative-beta-limit", "kind": "limits-target", "source_ref": "statement:representative-beta-limit", "target_ref": "statement:representative-beta", "authority_ref": CONTENT_AUTHORITY["id"]},
        ],
        "distribution": {"id": "distribution:representative", "designation": "fixture-only", "authority_ref": CONTENT_AUTHORITY["id"]},
        "comparison_universes": [], "selection_sets": [],
    })
    return author_candidate_bundle(brief=brief, material=material, candidate=candidate)


def representative_chain(testcase, suffix: str = "task060", *, complete_audience_edge: bool = False):
    """Build a real six-record Release and exact native seven-mapping Plan."""
    release_helper = release_tests.PublicationReleaseProductionTests(
        "test_complete_governed_ready_produces_exact_deterministic_immutable_release"
    )
    snapshot = release_helper._snapshot("representative", 1)
    candidate = candidate_bundle(snapshot, complete_audience_edge=complete_audience_edge)
    legacy_helper = compatibility_tests.LegacyCompatibilityContractTests(
        "test_complete_synthetic_legacy_closure_maps_successfully"
    )
    legacy_candidate, legacy_judgment, legacy_ready = legacy_helper._legacy_closure(suffix, 1)
    mapped = map_legacy_ready_to_bcrp(
        legacy_candidate=legacy_candidate, legacy_judgment=legacy_judgment, legacy_ready=legacy_ready,
        bcrp_candidate_bundle=candidate,
        mapping=legacy_helper._mapping(legacy_candidate, candidate, suffix=suffix),
    )
    release_authorization = release_helper._authorization(mapped, snapshot, suffix)
    release = produce_publication_release(
        governed_ready=mapped, evidence_snapshot=snapshot, authorization=release_authorization,
        publication_identity=release_authorization.publication_identity,
        publication_version=release_authorization.publication_version,
        release_identity=release_authorization.release_identity, release_time=release_authorization.release_time,
        distribution_constraints=release_authorization.release_distribution_constraints,
        includes_recommendations=False,
    )
    claims = tuple(CapabilityClaim(
        f"capability:representative-{stem}", "native",
        tuple(sorted((GLOBAL_CONSTRAINT, f"constraint:{specific}"))), True,
    ) for stem, specific in REQUIREMENTS)
    provisional = RendererCapabilityDeclaration(
        identity="renderer-capability:representative-static-html", contract_identity=CAPABILITY_DECLARATION_CONTRACT,
        capability_profile_identity=ACCEPTED_DECLARATION_PROFILE_ID,
        capability_profile_version=ACCEPTED_DECLARATION_PROFILE_VERSION,
        renderer_identity=RENDERER_IDENTITY, renderer_version=RENDERER_VERSION,
        renderer_owner="project:BriefForge", renderer_role="bounded-publication-renderer",
        declaration_time="2026-08-01T09:00:00Z", inventory_complete=True,
        capabilities=claims, unsupported_capabilities=(),
        declared_constraints=(GLOBAL_CONSTRAINT, "no-external-assets", "single-regular-html"),
        extensions=(), fingerprint="",
    )
    declaration = replace(provisional, fingerprint=compute_capability_declaration_fingerprint(provisional))
    planning_helper = planning_tests.RendererCompatibilityPlanningTests(
        "test_native_success_is_deterministic_immutable_and_complete"
    )
    scope = planning_helper._scope(release)
    planning_authorization = PlanningAuthorization(
        identity=f"planning-authorization:{suffix}", policy_identity=PLANNING_POLICY_ID,
        authority_identity=ACCEPTED_PLANNING_AUTHORITY_IDENTITY,
        authority_owner=ACCEPTED_PLANNING_AUTHORITY_OWNER,
        authority_role=ACCEPTED_PLANNING_AUTHORITY_ROLE,
        authorization_time="2026-08-01T09:01:00Z",
        release_identity=release.release.identity, release_fingerprint=release.fingerprint.digest,
        capability_declaration_identity=declaration.identity,
        capability_declaration_fingerprint=declaration.fingerprint,
        plan_identity=f"renderer-plan:{suffix}", planning_time="2026-08-01T09:02:00Z",
    )
    planned = produce_renderer_compatibility_plan(
        verified_release=release, evidence_snapshot=snapshot, lifecycle_scope=scope,
        declaration=declaration, authorization=planning_authorization,
    )
    testcase.assertFalse(planned.blocked, planned.findings)
    testcase.assertEqual(len(release.bundle.records), 6)
    testcase.assertEqual(len(planned.plan.bundle.records), 8)
    testcase.assertEqual(len(planned.plan.mappings), 7)
    return snapshot, release, scope, declaration, planning_authorization, planned.plan
