"""Layer-separated BCRP L0-L6 validation.

Each layer retains its own authority. Validation records findings and never
repairs content or manufactures governance approval.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from .graph import inspect_graph
from .model import BCRPBundle, BCRPRecord, ValidationFinding, ValidationResult
from .structure import PROHIBITED_DOMAIN_KEYS, validate_structure

LAYERS = tuple(f"L{i}" for i in range(7))


def _finding(
    layer: str,
    family: str,
    identity: str,
    location: str,
    message: str,
    consequence: str,
    refs: Iterable[str] = (),
) -> ValidationFinding:
    return ValidationFinding(layer, family, "blocking", consequence, identity, location, message, tuple(sorted(refs)))


def _one(bundle: BCRPBundle, kind: str) -> BCRPRecord | None:
    records = bundle.records_of_kind(kind)
    return records[0] if len(records) == 1 else None


def _objects(record: BCRPRecord | None, key: str) -> list[dict[str, Any]]:
    if record is None:
        return []
    value = record.semantic.get(key, [])
    return value if isinstance(value, list) else []


def _map_objects(record: BCRPRecord | None, key: str) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in _objects(record, key) if isinstance(item, dict) and isinstance(item.get("id"), str)}


def validate_bundle(bundle: BCRPBundle, *, through_layer: str | None = None) -> ValidationResult:
    """Run deterministic validation through a named layer (all layers by default)."""

    final_index = 6 if through_layer is None else LAYERS.index(through_layer)
    findings: list[ValidationFinding] = []
    validators = (_validate_l0, _validate_l1, _validate_l2, _validate_l3, _validate_l4, _validate_l5, _validate_l6)
    for index, validator in enumerate(validators):
        if index > final_index:
            break
        findings.extend(validator(bundle))
    return ValidationResult(tuple(sorted(set(findings))), LAYERS[: final_index + 1])


def _validate_l0(bundle: BCRPBundle) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    brief = _one(bundle, "PresentationBriefRecord")
    candidate = _one(bundle, "CandidatePresentationPackageRecord")
    if brief is None or not isinstance(brief.semantic.get("organizing_purpose"), dict):
        findings.append(
            _finding(
                "L0",
                "intake-completeness-or-scope",
                brief.identity if brief else "bundle",
                "/semantic/organizing_purpose",
                "Presentation Brief requires one explicit organizing purpose.",
                "Candidate construction/promotion",
            )
        )
    if candidate is None or not isinstance(candidate.semantic.get("organizing_purpose"), dict):
        findings.append(
            _finding(
                "L0",
                "intake-completeness-or-scope",
                candidate.identity if candidate else "bundle",
                "/semantic/organizing_purpose",
                "Candidate requires one organizing purpose compatible with intake.",
                "Candidate construction/promotion",
            )
        )
    if brief and not brief.semantic.get("audiences"):
        findings.append(_finding("L0", "intake-completeness-or-scope", brief.identity, "/semantic/audiences", "Audience orientation is absent.", "Candidate construction"))
    return findings


def _validate_l1(bundle: BCRPBundle) -> list[ValidationFinding]:
    return list(validate_structure(bundle))


def _validate_l2(bundle: BCRPBundle) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    brief = _one(bundle, "PresentationBriefRecord")
    material = _one(bundle, "PortablePresentationMaterialRecord")
    candidate = _one(bundle, "CandidatePresentationPackageRecord")
    if candidate is None:
        return findings

    if brief is None or not isinstance(brief.semantic.get("organizing_purpose"), dict) or not isinstance(candidate.semantic.get("organizing_purpose"), dict):
        findings.append(_finding("L2", "intake-completeness-or-scope", candidate.identity, "/semantic/organizing_purpose", "Candidate purpose cannot be reconciled to the Presentation Brief.", "Candidate construction/promotion"))

    _, graph_problems = inspect_graph(bundle)
    for problem, source, target in graph_problems:
        if problem == "dangling-reference":
            findings.append(_finding("L2", "identity-or-reference-integrity", source, source, f"Semantic reference targets absent identity {target!r}.", "Candidate promotion", (target,)))

    authorities = _map_objects(material, "authorities")
    authorities.update(_map_objects(candidate, "authorities"))
    statements = _objects(candidate, "statements")
    statement_map = {statement.get("id"): statement for statement in statements if isinstance(statement, dict)}
    relations = _objects(candidate, "relations")

    for statement in statements:
        if not isinstance(statement, dict) or not isinstance(statement.get("id"), str):
            continue
        identity = statement["id"]
        posture = statement.get("posture")
        authority_ref = statement.get("authority_ref")
        authority = authorities.get(authority_ref, {})
        if not authority_ref or authority_ref not in authorities:
            findings.append(_finding("L2", "authority-or-provenance", identity, f"/statements/{identity}/authority_ref", "Statement authority is absent or ambiguous.", "Candidate promotion"))
        if posture in {"caveat", "uncertainty"}:
            attached = any(relation.get("kind") == "limits-target" and relation.get("source_ref") == identity and relation.get("target_ref") in statement_map for relation in relations)
            if not attached:
                findings.append(_finding("L2", "obligation-or-qualifier-attachment", identity, f"/statements/{identity}", f"{posture.title()} is orphaned from a limited target.", "Candidate promotion"))
        if statement.get("requires_comparison_universe") and not statement.get("comparison_universe_ref"):
            findings.append(_finding("L2", "authority-or-provenance", identity, f"/statements/{identity}/comparison_universe_ref", "Comparative superlative lacks its comparison-universe and method binding.", "Candidate promotion"))
        if posture == "accepted-evidence" and authority.get("role") == "personal-author":
            findings.append(_finding("L2", "authority-or-provenance", identity, f"/statements/{identity}/posture", "Personal annotation cannot be promoted to accepted evidence without new authority.", "Candidate promotion"))
        if posture == "recommendation":
            if authority.get("role") not in {"recommendation-authority", "upstream-semantic-authority"} or statement.get("inferred_by_briefforge"):
                consequence = "promotion/release" if statement.get("inferred_by_briefforge") else "Candidate promotion"
                findings.append(_finding("L2", "authority-or-provenance", identity, f"/statements/{identity}", "Recommendation lacks upstream recommendation authority or was inferred by BriefForge.", consequence))

    for obligation in _objects(candidate, "obligations"):
        if not obligation.get("target_refs"):
            findings.append(_finding("L2", "obligation-or-qualifier-attachment", obligation.get("id", candidate.identity), "/obligations/target_refs", "Presentation obligation has no canonical target.", "Candidate promotion"))

    findings.extend(_validate_values(material, candidate))
    findings.extend(_validate_composition(candidate))
    findings.extend(_validate_selection(candidate, material))

    # DSB-007 is independently enforced semantically, not only structurally.
    for location, key, identity in _find_prohibited_keys(candidate.semantic, candidate.identity):
        findings.append(_finding("L2", "domain-ownership-prohibition", identity, location, f"Deferred financial-domain semantic field {key!r} is prohibited.", "profile admission/Candidate promotion"))
    for record in bundle.records:
        for extension_index, extension in enumerate(record.extensions):
            for location, key, identity in _find_prohibited_keys(extension.get("payload"), record.identity, f"/extensions/{extension_index}/payload"):
                findings.append(_finding("L2", "domain-ownership-prohibition", identity, location, f"Deferred financial-domain extension field {key!r} is prohibited.", "profile admission/Candidate promotion"))
    return findings


def _validate_values(material: BCRPRecord | None, candidate: BCRPRecord) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    values = _map_objects(material, "values")
    required = material.semantic.get("required_value_ids", []) if material else []
    for required_id in required:
        if required_id not in values:
            findings.append(_finding("L2", "semantic-state-integrity", material.identity if material else candidate.identity, "/semantic/required_value_ids", f"Required explicitly stated value {required_id!r} was silently omitted.", "Candidate promotion", (required_id,)))
    for identity, value in values.items():
        state = value.get("value_state")
        payload = value.get("payload", "__absent__")
        if value.get("approximate") is True:
            qualifier = value.get("approximation")
            if not isinstance(qualifier, dict) or not qualifier.get("method") or not qualifier.get("bound"):
                findings.append(_finding("L2", "semantic-state-integrity", identity, f"/values/{identity}/approximation", "Approximate values require an explicit method and bound qualifier.", "Candidate promotion"))
        if state == "explicit-zero":
            if not isinstance(payload, dict) or int(payload.get("coefficient", "1")) != 0:
                findings.append(_finding("L2", "semantic-state-integrity", identity, f"/values/{identity}", "Explicit-zero state requires an exact zero payload.", "Candidate promotion"))
        elif state == "present":
            if isinstance(payload, dict) and int(payload.get("coefficient", "0")) == 0:
                findings.append(_finding("L2", "semantic-state-integrity", identity, f"/values/{identity}", "Present numeric state cannot carry semantic zero; use explicit-zero.", "Candidate promotion"))
        elif state in {"missing-not-provided", "unavailable", "not-applicable", "suppressed-withheld", "unresolved", "invalid"} and payload != "__absent__":
            findings.append(_finding("L2", "semantic-state-integrity", identity, f"/values/{identity}/payload", f"Value state {state!r} cannot carry an admitted payload.", "Candidate promotion"))
    for assertion in _objects(material, "consistency_assertions"):
        if assertion.get("known_conflict") and (assertion.get("state") != "conflicting" or len(assertion.get("source_value_refs", [])) < 2):
            findings.append(_finding("L2", "semantic-state-integrity", assertion.get("id", material.identity if material else candidate.identity), "/consistency_assertions", "Known disagreement was silently resolved or incompletely retained.", "Candidate promotion"))
    return findings


def _validate_composition(candidate: BCRPRecord) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    sections = _map_objects(candidate, "sections")
    adjacency = {identity: [child for child in section.get("children", []) if child in sections] for identity, section in sections.items()}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identity: str) -> bool:
        if identity in visiting:
            return True
        if identity in visited:
            return False
        visiting.add(identity)
        cycle = any(visit(child) for child in adjacency.get(identity, []))
        visiting.remove(identity)
        visited.add(identity)
        return cycle

    if any(visit(identity) for identity in adjacency):
        findings.append(_finding("L2", "composition-or-narrative-integrity", candidate.identity, "/semantic/sections", "Composition graph contains a cycle.", "Candidate promotion/render plan"))
    return findings


def _validate_selection(candidate: BCRPRecord, material: BCRPRecord | None) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    statement_map = _map_objects(candidate, "statements")
    caveat_ids = {identity for identity, statement in statement_map.items() if statement.get("posture") == "caveat"}
    material_snapshots = _map_objects(material, "evidence_snapshots")
    fallbacks = _map_objects(candidate, "fallbacks")
    requirements = _map_objects(candidate, "renderer_requirements")
    for selection in _objects(candidate, "selection_sets"):
        selection_id = selection.get("id", candidate.identity)
        state_ids = selection.get("state_ids", [])
        default = selection.get("default_state_ref")
        if not default:
            findings.append(_finding("L2", "selection-closure-or-state-narrative", selection_id, "/selection_sets/default_state_ref", "Finite selection lacks an authority-declared default state.", "Candidate promotion/selector release"))
        if "*" in state_ids or any(state.get("id") == "*" for state in selection.get("states", [])):
            findings.append(_finding("L2", "selection-closure-or-state-narrative", selection_id, "/selection_sets/state_ids", "Wildcard selection state is prohibited.", "Candidate promotion"))
        if any(state.get("generated_from_cartesian") for state in selection.get("states", [])):
            findings.append(_finding("L2", "selection-closure-or-state-narrative", selection_id, "/selection_sets/states", "Implicit Cartesian-product state is prohibited.", "Candidate promotion"))
        projections = selection.get("projections", [])
        projection_by_state = {projection.get("state_ref"): projection for projection in projections}
        for state_id in state_ids:
            projection = projection_by_state.get(state_id)
            if not projection:
                findings.append(_finding("L2", "selection-closure-or-state-narrative", selection_id, "/selection_sets/projections", f"State {state_id!r} lacks a complete materialized projection.", "selector publication", (state_id,)))
                continue
            required_fields = (
                "title",
                "statement_ids",
                "value_ids",
                "caveat_ids",
                "uncertainty_ids",
                "evidence_refs",
                "obligation_ids",
                "renderer_requirement_ids",
                "static_expression",
                "print_expression",
                "validation_ref",
                "evidence_snapshot_ref",
                "validated_snapshot_version",
            )
            if any(field not in projection for field in required_fields) or not projection.get("statement_ids") or not projection.get("value_ids"):
                findings.append(_finding("L2", "selection-closure-or-state-narrative", state_id, f"/selection_sets/projections/{state_id}", "Selection projection is not a complete materialized state narrative.", "selector publication"))
            for statement_id in projection.get("statement_ids", []):
                compatible = statement_map.get(statement_id, {}).get("compatible_state_refs", [])
                if compatible and state_id not in compatible:
                    findings.append(_finding("L2", "composition-or-narrative-integrity", statement_id, f"/selection_sets/projections/{state_id}/statement_ids", "Conclusion is visible in an incompatible selection state.", "Candidate promotion/selector publication", (state_id,)))
            projection_caveats = set(projection.get("caveat_ids", []))
            required_caveats = {
                statement_id
                for statement_id in caveat_ids
                if not statement_map[statement_id].get("compatible_state_refs") or state_id in statement_map[statement_id].get("compatible_state_refs", [])
            }
            if not required_caveats.issubset(projection_caveats) or not projection_caveats.issubset(set(projection.get("static_expression", []))):
                findings.append(_finding("L2", "transformation-or-fallback", state_id, f"/selection_sets/projections/{state_id}/caveat_ids", "State-specific caveat is absent from the complete static expression.", "promotion, plan, or artifact acceptance"))
            snapshot = material_snapshots.get(projection.get("evidence_snapshot_ref"), {})
            if snapshot and projection.get("validated_snapshot_version") != snapshot.get("version"):
                findings.append(_finding("L2", "lifecycle-or-version-linkage", state_id, f"/selection_sets/projections/{state_id}/validated_snapshot_version", "Evidence snapshot changed without a new state-validation identity.", "promotion/release"))

    for requirement in requirements.values():
        if requirement.get("mandatory") and requirement.get("capability") == "print" and not requirement.get("fallback_refs"):
            findings.append(_finding("L2", "transformation-or-fallback", requirement["id"], "/renderer_requirements/fallback_refs", "Mandatory print expression lacks a complete declared fallback.", "Candidate promotion/rendering"))
        for fallback_ref in requirement.get("fallback_refs", []):
            if fallback_ref not in fallbacks:
                findings.append(_finding("L2", "transformation-or-fallback", requirement["id"], "/renderer_requirements/fallback_refs", "Declared mandatory fallback is absent.", "Candidate promotion/rendering", (fallback_ref,)))
    return findings


def _find_prohibited_keys(value: Any, owner: str, location: str = "/semantic") -> list[tuple[str, str, str]]:
    found: list[tuple[str, str, str]] = []
    if isinstance(value, dict):
        current = value.get("id", owner)
        for key, child in value.items():
            child_location = f"{location}/{key}"
            if key in PROHIBITED_DOMAIN_KEYS:
                found.append((child_location, key, current))
            found.extend(_find_prohibited_keys(child, current, child_location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_find_prohibited_keys(child, owner, f"{location}/{index}"))
    return found


def _candidate_digest(bundle: BCRPBundle) -> str:
    from .canonical import fingerprint_bundle

    return fingerprint_bundle(bundle, domain="candidate-semantic", require_valid=False).digest


def _validate_l3(bundle: BCRPBundle) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    releases = bundle.records_of_kind("PublicationReleaseRecord")
    if len(releases) > 1:
        findings.append(
            _finding(
                "L3",
                "lifecycle-release-cardinality",
                "bundle",
                "/records/PublicationReleaseRecord",
                f"Lifecycle linkage requires one explicitly selected Release closure; found {len(releases)} Release roots.",
                "promotion/release/lifecycle processing",
                [record.identity for record in releases],
            )
        )
    candidate = _one(bundle, "CandidatePresentationPackageRecord")
    judgment = _one(bundle, "ValidationJudgmentRecord")
    ready = _one(bundle, "ReadyPresentationPackageRecord")
    release = _one(bundle, "PublicationReleaseRecord")
    manifest = _one(bundle, "PublicationManifestRecord")
    if not all((candidate, judgment, ready, release)):
        return findings
    digest = _candidate_digest(bundle)
    if judgment.semantic.get("candidate_ref") != candidate.identity or judgment.semantic.get("candidate_fingerprint") != digest or not judgment.semantic.get("valid"):
        findings.append(_finding("L3", "lifecycle-or-version-linkage", judgment.identity, "/semantic/candidate_fingerprint", "Judgment does not bind a successful validation to the exact Candidate fingerprint.", "promotion"))
    if ready.semantic.get("candidate_ref") != candidate.identity or ready.semantic.get("candidate_fingerprint") != digest or ready.semantic.get("judgment_ref") != judgment.identity:
        findings.append(_finding("L3", "lifecycle-or-version-linkage", ready.identity, "/semantic", "Ready record does not bind the exact Candidate and successful Judgment.", "promotion/release"))
    if release.semantic.get("ready_ref") != ready.identity or release.semantic.get("ready_fingerprint") != ready.semantic.get("ready_fingerprint"):
        findings.append(_finding("L3", "lifecycle-or-version-linkage", release.identity, "/semantic/ready_fingerprint", "Release does not bind the exact Ready package.", "release"))
    material = _one(bundle, "PortablePresentationMaterialRecord")
    snapshot_versions = {item.get("id"): item.get("version") for item in _objects(material, "evidence_snapshots")}
    declared_versions = release.semantic.get("evidence_snapshot_versions", {})
    if any(declared_versions.get(snapshot_id) != version for snapshot_id, version in snapshot_versions.items() if snapshot_id in release.semantic.get("evidence_snapshot_refs", [])):
        findings.append(_finding("L3", "lifecycle-or-version-linkage", release.identity, "/semantic/evidence_snapshot_versions", "Release evidence changed without new validation/release identity.", "promotion/release"))
    if manifest and manifest.semantic.get("lifecycle_status") != release.semantic.get("lifecycle_status"):
        findings.append(_finding("L3", "lifecycle-or-version-linkage", manifest.identity, "/semantic/lifecycle_status", "Manifest contradicts authoritative release lifecycle status.", "manifest/artifact catalogue acceptance"))
    return findings


def _validate_l4(bundle: BCRPBundle) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    releases = bundle.records_of_kind("PublicationReleaseRecord")
    if len(releases) > 1:
        findings.append(
            _finding(
                "L4",
                "lifecycle-release-cardinality",
                "bundle",
                "/records/PublicationReleaseRecord",
                f"Governance validation requires one explicitly selected Release authority; found {len(releases)} Release roots.",
                "release/lifecycle authority",
                [record.identity for record in releases],
            )
        )
    candidate = _one(bundle, "CandidatePresentationPackageRecord")
    release = _one(bundle, "PublicationReleaseRecord")
    material = _one(bundle, "PortablePresentationMaterialRecord")
    if not candidate or not release:
        return findings
    authority_ids = set(_map_objects(material, "authorities")) | set(_map_objects(candidate, "authorities"))
    if release.semantic.get("release_authority_ref") not in authority_ids:
        findings.append(_finding("L4", "governance-or-distribution-authority", release.identity, "/semantic/release_authority_ref", "Explicit release authority is absent; validation cannot manufacture approval.", "release"))
    if not release.semantic.get("distribution_authorized"):
        findings.append(_finding("L4", "governance-or-distribution-authority", release.identity, "/semantic/distribution_authorized", "Requested distribution is outside declared authorization.", "release"))
    unsupported = [statement for statement in _objects(candidate, "statements") if statement.get("posture") == "recommendation" and statement.get("inferred_by_briefforge")]
    if unsupported and release.semantic.get("includes_recommendations", True):
        findings.append(_finding("L4", "authority-or-provenance", release.identity, "/semantic/includes_recommendations", "Release includes an unsupported BriefForge-inferred recommendation.", "promotion/release", [statement["id"] for statement in unsupported]))
    return findings


def _validate_l5(bundle: BCRPBundle) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    candidate = _one(bundle, "CandidatePresentationPackageRecord")
    capability = _one(bundle, "RendererCapabilityDeclarationRecord")
    plan = _one(bundle, "RendererCompatibilityPlanRecord")
    if not candidate or not capability or not plan:
        return findings
    requirements = _map_objects(candidate, "renderer_requirements")
    fallbacks = _map_objects(candidate, "fallbacks")
    supported = set(capability.semantic.get("capabilities", []))
    permitted_transformations = {transformation for requirement in requirements.values() for transformation in requirement.get("permitted_transformations", [])}
    for transformation in plan.semantic.get("declared_transformations", []):
        if transformation not in permitted_transformations:
            findings.append(_finding("L5", "transformation-or-fallback", plan.identity, "/semantic/declared_transformations", "Renderer plan introduces an undeclared transformation.", "rendering"))
    plan_fallbacks = set(plan.semantic.get("fallbacks", []))
    for requirement in requirements.values():
        capability_name = requirement.get("capability")
        if requirement.get("mandatory") and capability_name not in supported:
            admitted = set(requirement.get("fallback_refs", [])) & set(fallbacks) & plan_fallbacks
            if not admitted:
                findings.append(_finding("L5", "renderer-capability-or-plan", requirement["id"], "/renderer_requirements", f"Renderer lacks mandatory {capability_name!r} capability and no admitted fallback is complete.", "rendering"))
    if plan.semantic.get("mode") == "native-selection" and "state-identity-visibility" not in supported:
        findings.append(_finding("L5", "renderer-capability-or-plan", plan.identity, "/semantic/mode", "Native selection lacks verified state-identity visibility.", "native selection rendering"))
    missing_caveats = plan.semantic.get("fallback_missing_caveat_refs", [])
    if missing_caveats:
        findings.append(_finding("L5", "transformation-or-fallback", plan.identity, "/semantic/fallback_missing_caveat_refs", "Static fallback omits state-specific caveat.", "promotion, plan, or artifact acceptance", missing_caveats))
    print_requirements = [item for item in requirements.values() if item.get("capability") == "print" and item.get("mandatory")]
    if print_requirements and not any(fallback.get("kind") == "print" and fallback["id"] in plan_fallbacks for fallback in fallbacks.values()):
        findings.append(_finding("L5", "transformation-or-fallback", plan.identity, "/semantic/fallbacks", "Mandatory print fallback is absent from the compatibility plan.", "Candidate promotion/rendering"))
    return findings


def _validate_l6(bundle: BCRPBundle) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    candidate = _one(bundle, "CandidatePresentationPackageRecord")
    ready = _one(bundle, "ReadyPresentationPackageRecord")
    release = _one(bundle, "PublicationReleaseRecord")
    audit = _one(bundle, "GeneratedArtifactAuditRecord")
    conformance = _one(bundle, "SemanticArtifactConformanceRecord")
    manifest = _one(bundle, "PublicationManifestRecord")
    if not all((candidate, ready, release, audit, conformance, manifest)):
        return findings
    if manifest.semantic.get("lifecycle_status") != release.semantic.get("lifecycle_status"):
        findings.append(_finding("L6", "lifecycle-or-version-linkage", manifest.identity, "/semantic/lifecycle_status", "Derivative manifest contradicts authoritative release status.", "manifest/artifact catalogue acceptance"))
    if audit.semantic.get("ready_ref") != ready.identity or audit.semantic.get("ready_fingerprint") != ready.semantic.get("ready_fingerprint"):
        findings.append(_finding("L6", "audit-link-conformance", audit.identity, "/semantic/ready_fingerprint", "Artifact audit is linked to a different Ready package.", "artifact acceptance"))
    evidence = conformance.semantic.get("evidence", {})
    if conformance.semantic.get("semantic_pass") and evidence.get("kind") == "audit-link-only":
        findings.append(_finding("L6", "semantic-artifact-conformance", conformance.identity, "/semantic/evidence", "Structural audit-link traceability was misreported as semantic conformance.", "artifact acceptance"))
    selection_sets = _objects(candidate, "selection_sets")
    if selection_sets and audit.semantic.get("selected_state_ref"):
        selection = selection_sets[0]
        projection = next((item for item in selection.get("projections", []) if item.get("state_ref") == audit.semantic.get("selected_state_ref")), {})
        admitted = set(projection.get("statement_ids", []))
        expressed = set(audit.semantic.get("expressed_statement_ids", []))
        if not expressed.issubset(admitted):
            findings.append(_finding("L6", "semantic-artifact-conformance", audit.identity, "/semantic/expressed_statement_ids", "Rendered state contains a conclusion incompatible with the selected state.", "artifact acceptance", expressed - admitted))
        statement_map = _map_objects(candidate, "statements")
        selected_state = audit.semantic.get("selected_state_ref")
        required_caveats = {
            identity
            for identity, statement in statement_map.items()
            if statement.get("posture") == "caveat"
            and (not statement.get("compatible_state_refs") or selected_state in statement.get("compatible_state_refs", []))
        }
        missing_caveats = required_caveats - set(audit.semantic.get("expressed_caveat_refs", []))
        if missing_caveats:
            findings.append(_finding("L6", "transformation-or-fallback", audit.identity, "/semantic/expressed_caveat_refs", "Rendered fallback omits a required state-specific caveat.", "promotion, plan, or artifact acceptance", missing_caveats))
    return findings
