"""Inspectable golden-corpus access and thirty narrowly scoped mutations."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .loader import load_bundle
from .model import BCRPBundle, BCRPRecord

CASE_IDS = (
    "case-1-demographic-correlation-publication",
    "case-2-synthetic-company-comparison",
    "case-3-synthetic-company-macro-selection",
)
INVALID_VARIANT_IDS = tuple(
    [f"C1-I{index:02d}" for index in range(1, 10)]
    + [f"C2-I{index:02d}" for index in range(1, 12)]
    + [f"C3-I{index:02d}" for index in range(1, 11)]
)
_FIXTURE_ROOT = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "bcrp"


def load_case(case_id: str) -> BCRPBundle:
    if case_id not in CASE_IDS:
        raise KeyError(f"unknown BCRP corpus case {case_id!r}")
    return load_bundle(_FIXTURE_ROOT / case_id)


def _record(bundle: BCRPBundle, kind: str) -> BCRPRecord:
    return bundle.one(kind)


def _item(items: list[dict[str, Any]], identity: str) -> dict[str, Any]:
    return next(item for item in items if item.get("id") == identity)


def materialize_invalid_variant(case_id: str, variant_id: str) -> BCRPBundle:
    """Apply one explicit accepted minimal mutation to a fresh valid base.

    This is intentionally not a general patch language. Each branch names and
    performs one reviewable corpus mutation from the TASK-044 acceptance table.
    """

    if variant_id not in INVALID_VARIANT_IDS or not variant_id.startswith(case_id.split("-")[1].upper()):
        # Case IDs use "case-1" while variants use "C1".
        expected_prefix = f"C{CASE_IDS.index(case_id) + 1}-" if case_id in CASE_IDS else ""
        if variant_id not in INVALID_VARIANT_IDS or not variant_id.startswith(expected_prefix):
            raise KeyError(f"variant {variant_id!r} does not belong to {case_id!r}")
    bundle = deepcopy(load_case(case_id))
    candidate = _record(bundle, "CandidatePresentationPackageRecord")
    material = _record(bundle, "PortablePresentationMaterialRecord")
    release = _record(bundle, "PublicationReleaseRecord")
    capability = _record(bundle, "RendererCapabilityDeclarationRecord")
    plan = _record(bundle, "RendererCompatibilityPlanRecord")
    audit = _record(bundle, "GeneratedArtifactAuditRecord")
    conformance = _record(bundle, "SemanticArtifactConformanceRecord")
    manifest = _record(bundle, "PublicationManifestRecord")

    if variant_id == "C1-I01":
        _record(bundle, "PresentationBriefRecord").semantic.pop("organizing_purpose")
        candidate.semantic.pop("organizing_purpose")
    elif variant_id == "C1-I02":
        candidate.semantic["statements"][0]["upstream_refs"][0] = "external:absent-upstream"
    elif variant_id == "C1-I03":
        caveat_id = next(item["id"] for item in candidate.semantic["statements"] if item["posture"] == "caveat")
        candidate.semantic["relations"] = [item for item in candidate.semantic["relations"] if item.get("source_ref") != caveat_id]
    elif variant_id == "C1-I04":
        root = candidate.semantic["sections"][0]
        root["children"].append(root["id"])
    elif variant_id == "C1-I05":
        statement = next(item for item in candidate.semantic["statements"] if item.get("requires_comparison_universe"))
        statement.pop("comparison_universe_ref")
    elif variant_id == "C1-I06":
        plan.semantic["declared_transformations"].append("renderer-side-ranking")
    elif variant_id == "C1-I07":
        release.semantic["lifecycle_status"] = "withdrawn"
    elif variant_id == "C1-I08":
        conformance.semantic["evidence"] = {"kind": "audit-link-only", "audit_ref": audit.identity}
    elif variant_id == "C1-I09":
        audit.semantic["ready_fingerprint"] = "sha256:wrong-ready"

    elif variant_id == "C2-I01":
        recommendation = next(item for item in candidate.semantic["statements"] if item["posture"] == "recommendation")
        recommendation.pop("authority_ref")
    elif variant_id == "C2-I02":
        _item(material.semantic["values"], "value:aster-zero")["value_state"] = "missing-not-provided"
    elif variant_id == "C2-I03":
        material.semantic["values"] = [item for item in material.semantic["values"] if item["id"] != "value:boreal-suppressed"]
    elif variant_id == "C2-I04":
        conflict = material.semantic["consistency_assertions"][0]
        conflict["state"] = "consistent"
        conflict["source_value_refs"] = conflict["source_value_refs"][:1]
    elif variant_id == "C2-I05":
        value = _item(material.semantic["values"], "value:not-applicable")
        value["payload"] = {"coefficient": "12", "scale": 0}
    elif variant_id == "C2-I06":
        annotation = next(item for item in candidate.semantic["statements"] if item["posture"] == "personal-annotation")
        annotation["posture"] = "accepted-evidence"
    elif variant_id == "C2-I07":
        candidate.semantic["statements"].append(
            {
                "id": "statement:unsupported-recommendation",
                "text": "BriefForge infers a new unsupported recommendation.",
                "posture": "recommendation",
                "communication_functions": ["decision"],
                "attention": "primary",
                "purpose_ref": candidate.semantic["organizing_purpose"]["id"],
                "authority_ref": "authority:presentation",
                "upstream_refs": ["external:aster-vale-tools"],
                "inferred_by_briefforge": True,
            }
        )
    elif variant_id == "C2-I08":
        release.semantic["distribution_authorized"] = False
        release.semantic["distribution_scope"] = "public-outside-declared-scope"
    elif variant_id == "C2-I09":
        capability.semantic["capabilities"] = [item for item in capability.semantic["capabilities"] if item != "table"]
        requirement = next(item for item in candidate.semantic["renderer_requirements"] if item["capability"] == "table")
        table_fallbacks = set(requirement["fallback_refs"])
        requirement["fallback_refs"] = []
        plan.semantic["fallbacks"] = [item for item in plan.semantic["fallbacks"] if item not in table_fallbacks]
    elif variant_id == "C2-I10":
        candidate.extensions.append(
            {
                "owner_namespace": "example:security-identity",
                "name": "security-identity",
                "version": "1.0.0",
                "authority_ref": "authority:presentation",
                "scope": "record",
                "target_refs": [candidate.identity],
                "criticality": "required",
                "character": "semantic",
                "validation_contract": "example:unknown-security-contract:1.0.0",
                "preservation": "must-preserve",
                "payload": {"opaque_identity": "synthetic-only"},
            }
        )
    elif variant_id == "C2-I11":
        candidate.semantic["fiscal_period"] = {"label": "speculative-period"}

    elif variant_id == "C3-I01":
        candidate.semantic["selection_sets"][0].pop("default_state_ref")
    elif variant_id == "C3-I02":
        selection = candidate.semantic["selection_sets"][0]
        selection["state_ids"].append("*")
        selection["states"].append({"id": "*", "label": "Wildcard"})
    elif variant_id == "C3-I03":
        projection = next(item for item in candidate.semantic["selection_sets"][0]["projections"] if item["state_ref"] == "state:supply-tightness")
        projection["statement_ids"] = []
        projection["value_ids"] = []
    elif variant_id == "C3-I04":
        projection = next(item for item in candidate.semantic["selection_sets"][0]["projections"] if item["state_ref"] == "state:demand-slowdown")
        projection["statement_ids"].append("statement:baseline-conclusion")
    elif variant_id == "C3-I05":
        audit.semantic["expressed_statement_ids"].append("statement:baseline-conclusion")
    elif variant_id == "C3-I06":
        projection = next(item for item in candidate.semantic["selection_sets"][0]["projections"] if item["state_ref"] == "state:demand-slowdown")
        caveat = projection["caveat_ids"].pop()
        projection["static_expression"].remove(caveat)
        plan.semantic["fallback_missing_caveat_refs"] = [caveat]
        audit.semantic["expressed_caveat_refs"] = [item for item in audit.semantic["expressed_caveat_refs"] if item != caveat]
    elif variant_id == "C3-I07":
        capability.semantic["capabilities"] = [item for item in capability.semantic["capabilities"] if item != "state-identity-visibility"]
    elif variant_id == "C3-I08":
        requirement = next(item for item in candidate.semantic["renderer_requirements"] if item["capability"] == "print")
        removed = set(requirement["fallback_refs"])
        requirement["fallback_refs"] = []
        candidate.semantic["fallbacks"] = [item for item in candidate.semantic["fallbacks"] if item["id"] not in removed]
        plan.semantic["fallbacks"] = [item for item in plan.semantic["fallbacks"] if item not in removed]
    elif variant_id == "C3-I09":
        material.semantic["evidence_snapshots"][0]["version"] = "2"
    elif variant_id == "C3-I10":
        selection = candidate.semantic["selection_sets"][0]
        selection["state_ids"].append("state:implicit-cartesian")
        selection["states"].append({"id": "state:implicit-cartesian", "label": "Implicit combination", "generated_from_cartesian": True})
        projection = deepcopy(selection["projections"][0])
        projection["id"] = "projection:implicit-cartesian"
        projection["state_ref"] = "state:implicit-cartesian"
        selection["projections"].append(projection)
    else:
        raise KeyError(f"unimplemented BCRP invalid variant {variant_id!r}")
    return bundle
