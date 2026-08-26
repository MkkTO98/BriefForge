"""TASK-051 renderer-independent compatibility planning and fail-closed proof."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from briefforge.bcrp import BCRPBundle, fingerprint_bundle, validate_bundle  # noqa: E402
from briefforge.bcrp.model import RECORD_KINDS  # noqa: E402
from briefforge.bcrp_legacy_compatibility import map_legacy_ready_to_bcrp  # noqa: E402
from briefforge.publication_lifecycle import (  # noqa: E402
    PROFILE_ID as LIFECYCLE_PROFILE_ID,
    PROFILE_VERSION as LIFECYCLE_PROFILE_VERSION,
    LifecycleBundle,
    ReleaseBinding,
    event_from_document,
)
from briefforge.publication_release import produce_publication_release  # noqa: E402
from briefforge.renderer_compatibility_planning import (  # noqa: E402
    ACCEPTED_DECLARATION_PROFILE_ID,
    ACCEPTED_DECLARATION_PROFILE_VERSION,
    ACCEPTED_PLANNING_AUTHORITY_IDENTITY,
    ACCEPTED_PLANNING_AUTHORITY_OWNER,
    ACCEPTED_PLANNING_AUTHORITY_ROLE,
    CAPABILITY_DECLARATION_CONTRACT,
    PLANNING_POLICY_ID,
    CapabilityClaim,
    LifecyclePlanningScope,
    PlanningAuthorization,
    PlanningRejected,
    RendererCapabilityDeclaration,
    compute_capability_declaration_fingerprint,
    compute_lifecycle_inventory_digest,
    produce_renderer_compatibility_plan,
    verify_renderer_compatibility_plan,
)
from tests import test_bcrp_lifecycle_authority_compatibility as compatibility_tests  # noqa: E402
from tests import test_bcrp_publication_release as release_tests  # noqa: E402
from tests import test_publication_lifecycle_profile as lifecycle_tests  # noqa: E402


class RendererCompatibilityPlanningTests(unittest.TestCase):
    def _requirements(self, prefix: str = "cedar") -> tuple[list[dict], list[dict]]:
        authority = f"authority:{prefix}-meaning"
        caveat = f"statement:{prefix}-caveat"
        requirements = [
            {
                "id": f"requirement:{prefix}-table", "capability": f"capability:{prefix}-table",
                "mandatory": True, "criticality": "required",
                "target_refs": [f"statement:{prefix}-evidence", authority, caveat],
                "authority_label_refs": [authority], "caveat_refs": [caveat],
                "required_constraints": ["standalone", "exact-state-labels"],
                "permitted_transformations": [f"transformation:{prefix}-table-layout"],
                "fallback_refs": [], "unsupported_allowed": False,
            },
            {
                "id": f"requirement:{prefix}-inspection", "capability": f"capability:{prefix}-inspection",
                "mandatory": True, "criticality": "required",
                "target_refs": [f"statement:{prefix}-method", authority],
                "authority_label_refs": [authority], "caveat_refs": [],
                "required_constraints": ["offline"],
                "permitted_transformations": [f"transformation:{prefix}-inline-inspection"],
                "fallback_refs": [f"fallback:{prefix}-equivalent-inspection"], "unsupported_allowed": False,
            },
            {
                "id": f"requirement:{prefix}-selection", "capability": f"capability:{prefix}-finite-selection",
                "mandatory": True, "criticality": "required",
                "target_refs": [f"state:{prefix}-one", f"state:{prefix}-two", caveat],
                "authority_label_refs": [], "caveat_refs": [caveat],
                "required_constraints": ["all-states", "visible-state-identity"],
                "permitted_transformations": [f"transformation:{prefix}-state-expansion"],
                "fallback_refs": [f"fallback:{prefix}-static-states"], "unsupported_allowed": False,
            },
            {
                "id": f"requirement:{prefix}-transition", "capability": f"capability:{prefix}-transition",
                "mandatory": False, "criticality": "optional",
                "target_refs": [f"section:{prefix}-root"],
                "authority_label_refs": [], "caveat_refs": [], "required_constraints": [],
                "permitted_transformations": [], "fallback_refs": [], "unsupported_allowed": True,
            },
        ]
        fallbacks = [
            {
                "id": f"fallback:{prefix}-equivalent-inspection", "kind": "equivalent-expression",
                "expression_mode": "equivalent", "required_capability": f"capability:{prefix}-inline-inspection",
                "complete": True, "covers_semantic_refs": [f"statement:{prefix}-method", authority],
                "preserves_authority_label_refs": [authority], "preserves_caveat_refs": [],
                "transformation": f"transformation:{prefix}-inline-inspection",
            },
            {
                "id": f"fallback:{prefix}-static-states", "kind": "static-state-expansion",
                "expression_mode": "static", "required_capability": f"capability:{prefix}-static-state-expansion",
                "complete": True, "covers_semantic_refs": [f"state:{prefix}-one", f"state:{prefix}-two", caveat],
                "preserves_authority_label_refs": [], "preserves_caveat_refs": [caveat],
                "transformation": f"transformation:{prefix}-state-expansion",
            },
        ]
        return requirements, fallbacks

    def _release(self, suffix: str = "cedar", case_index: int = 0, mutate=None):
        release_helper = release_tests.PublicationReleaseProductionTests(
            "test_complete_governed_ready_produces_exact_deterministic_immutable_release"
        )
        snapshot = release_helper._snapshot(suffix, case_index + 1)
        helper = compatibility_tests.LegacyCompatibilityContractTests(
            "test_complete_synthetic_legacy_closure_maps_successfully"
        )
        legacy_candidate, legacy_judgment, legacy_ready = helper._legacy_closure(suffix, case_index + 2)
        bcrp = helper._bcrp_candidate(case_index)
        material = bcrp.one("PortablePresentationMaterialRecord")
        old_snapshot = material.semantic["evidence_snapshots"][0]["id"]

        def replace_ref(value):
            if isinstance(value, dict):
                return {key: replace_ref(item) for key, item in value.items()}
            if isinstance(value, list):
                return [replace_ref(item) for item in value]
            return snapshot.identity if value == old_snapshot else value

        for record in bcrp.records:
            record.semantic = replace_ref(record.semantic)
        material = bcrp.one("PortablePresentationMaterialRecord")
        material.semantic["evidence_snapshots"] = [{
            "id": snapshot.identity, "version": snapshot.version,
            "content_fingerprint": f"sha256:{snapshot.inventory_digest}",
            "provenance_ref": material.semantic["provenance"][0]["id"],
        }]
        material.semantic["authorities"] = [
            item for item in material.semantic["authorities"]
            if item.get("id") != release_tests.ACCEPTED_AUTHORITY_IDENTITY
        ] + [{
            "id": release_tests.ACCEPTED_AUTHORITY_IDENTITY,
            "owner_identity": release_tests.ACCEPTED_AUTHORITY_OWNER,
            "role": release_tests.ACCEPTED_AUTHORITY_ROLE,
            "scope": "fixed-evidence-publication-release",
        }]
        requirements, fallbacks = self._requirements(suffix)
        candidate = bcrp.one("CandidatePresentationPackageRecord")
        statements = candidate.semantic["statements"]
        caveat = next(item for item in statements if item.get("posture") == "caveat")
        evidence = next((item for item in statements if item.get("posture") == "reusable-evidence"), statements[0])
        method = next(item for item in statements if item["id"] not in {caveat["id"], evidence["id"]})
        section = candidate.semantic["sections"][0]
        authority = caveat["authority_ref"]
        reference_map = {
            f"authority:{suffix}-meaning": authority,
            f"statement:{suffix}-caveat": caveat["id"],
            f"statement:{suffix}-evidence": evidence["id"],
            f"statement:{suffix}-method": method["id"],
            f"state:{suffix}-one": evidence["id"],
            f"state:{suffix}-two": method["id"],
            f"section:{suffix}-root": section["id"],
        }

        def bind_existing_refs(value):
            if isinstance(value, dict):
                return {key: bind_existing_refs(item) for key, item in value.items()}
            if isinstance(value, list):
                return [bind_existing_refs(item) for item in value]
            return reference_map.get(value, value)

        requirements = bind_existing_refs(requirements)
        fallbacks = bind_existing_refs(fallbacks)
        if mutate is not None:
            mutate(requirements, fallbacks)
        candidate.semantic["renderer_requirements"] = requirements
        candidate.semantic["fallbacks"] = fallbacks
        mapping = helper._mapping(legacy_candidate, bcrp, suffix=suffix)
        mapped = map_legacy_ready_to_bcrp(
            legacy_candidate=legacy_candidate, legacy_judgment=legacy_judgment,
            legacy_ready=legacy_ready, bcrp_candidate_bundle=bcrp, mapping=mapping,
        )
        authorization = release_helper._authorization(mapped, snapshot, suffix)
        produced = produce_publication_release(
            governed_ready=mapped, evidence_snapshot=snapshot, authorization=authorization,
            publication_identity=authorization.publication_identity,
            publication_version=authorization.publication_version,
            release_identity=authorization.release_identity, release_time=authorization.release_time,
            distribution_constraints=authorization.release_distribution_constraints,
            includes_recommendations=authorization.includes_recommendations,
        )
        return snapshot, produced

    def _declaration(self, suffix: str = "cedar", *, all_native: bool = False):
        claims = [
            CapabilityClaim(f"capability:{suffix}-table", "native", ("exact-state-labels", "standalone"), True),
        ]
        if all_native:
            claims.extend([
                CapabilityClaim(f"capability:{suffix}-inspection", "native", ("offline",), True),
                CapabilityClaim(f"capability:{suffix}-finite-selection", "native", ("all-states", "visible-state-identity"), True),
                CapabilityClaim(f"capability:{suffix}-transition", "native", (), True),
            ])
        else:
            claims.extend([
                CapabilityClaim(f"capability:{suffix}-inline-inspection", "equivalent", ("offline",), True),
                CapabilityClaim(f"capability:{suffix}-static-state-expansion", "static", ("all-states", "visible-state-identity"), True),
            ])
        base = dict(
            identity=f"renderer-capability:{suffix}", contract_identity=CAPABILITY_DECLARATION_CONTRACT,
            capability_profile_identity=ACCEPTED_DECLARATION_PROFILE_ID,
            capability_profile_version=ACCEPTED_DECLARATION_PROFILE_VERSION,
            renderer_identity=f"renderer:{suffix}", renderer_version="3.2.1+build.7",
            renderer_owner="project:BriefForge", renderer_role="bounded-publication-renderer",
            declaration_time="2026-07-17T09:00:00Z", inventory_complete=True,
            capabilities=tuple(claims),
            unsupported_capabilities=() if all_native else (f"capability:{suffix}-transition",),
            declared_constraints=("no-runtime-detection", "standalone-only"), extensions=(),
        )
        provisional = RendererCapabilityDeclaration(**base, fingerprint="")
        return replace(provisional, fingerprint=compute_capability_declaration_fingerprint(provisional))

    def _scope(self, produced, *, events=(), releases=None, policies=()):
        binding = release_tests.release_binding_from_verified_release(produced)
        release_catalog = tuple(releases or (binding,))
        bundle = LifecycleBundle(LIFECYCLE_PROFILE_ID, LIFECYCLE_PROFILE_VERSION, tuple(events))
        base = dict(bundle=bundle, releases=release_catalog, policies=tuple(policies), inventory_complete=True)
        provisional = LifecyclePlanningScope(**base, inventory_digest="")
        return replace(provisional, inventory_digest=compute_lifecycle_inventory_digest(provisional))

    def _authorization(self, produced, declaration, suffix="cedar"):
        return PlanningAuthorization(
            identity=f"planning-authorization:{suffix}", policy_identity=PLANNING_POLICY_ID,
            authority_identity=ACCEPTED_PLANNING_AUTHORITY_IDENTITY,
            authority_owner=ACCEPTED_PLANNING_AUTHORITY_OWNER,
            authority_role=ACCEPTED_PLANNING_AUTHORITY_ROLE,
            authorization_time="2026-07-17T09:01:00Z",
            release_identity=produced.release.identity, release_fingerprint=produced.fingerprint.digest,
            capability_declaration_identity=declaration.identity,
            capability_declaration_fingerprint=declaration.fingerprint,
            plan_identity=f"renderer-plan:{suffix}", planning_time="2026-07-17T09:02:00Z",
        )

    def _plan(self, suffix="cedar", *, all_native=False):
        snapshot, produced = self._release(suffix, 0 if suffix == "cedar" else 1)
        declaration = self._declaration(suffix, all_native=all_native)
        scope = self._scope(produced)
        authorization = self._authorization(produced, declaration, suffix)
        result = produce_renderer_compatibility_plan(
            verified_release=produced, evidence_snapshot=snapshot, lifecycle_scope=scope,
            declaration=declaration, authorization=authorization,
        )
        return snapshot, produced, declaration, scope, authorization, result

    def assertBlocked(self, result, code: str):
        self.assertTrue(result.blocked)
        self.assertIsNone(result.plan)
        self.assertIn(code, {finding.code for finding in result.findings})

    def test_native_success_is_deterministic_immutable_and_complete(self):
        snapshot, produced, declaration, scope, authorization, first = self._plan(all_native=True)
        self.assertFalse(first.blocked)
        self.assertIsNotNone(first.plan)
        modes = [item["selected_expression_mode"] for item in first.plan.mappings]
        self.assertEqual(modes, ["native", "native", "native", "native"])
        before_release, before_declaration, before_scope = produced.bundle, deepcopy(declaration), deepcopy(scope)
        second = produce_renderer_compatibility_plan(
            verified_release=produced, evidence_snapshot=snapshot, lifecycle_scope=scope,
            declaration=declaration, authorization=authorization,
        )
        self.assertEqual(first.plan.bundle, second.plan.bundle)
        self.assertEqual(first.plan.fingerprint, second.plan.fingerprint)
        self.assertEqual(produced.bundle, before_release)
        self.assertEqual(declaration, before_declaration)
        self.assertEqual(scope, before_scope)
        detached = first.plan.bundle
        detached.one("RendererCompatibilityPlanRecord").semantic["supported"] = False
        self.assertTrue(first.plan.plan.semantic["supported"])

    def test_equivalent_static_and_explicit_unsupported_are_distinct_success_outcomes(self):
        _, _, _, _, _, result = self._plan()
        self.assertFalse(result.blocked)
        modes = [item["selected_expression_mode"] for item in result.plan.mappings]
        self.assertEqual(modes, ["native", "equivalent", "static", "unsupported"])
        self.assertEqual(len(result.plan.bundle.records_of_kind("RendererCompatibilityPlanRecord")), 1)
        self.assertEqual(len(RECORD_KINDS), 11)

    def test_second_comprehensively_renamed_case_has_distinct_valid_plan(self):
        first = self._plan("cedar")[-1].plan
        second_data = self._plan("violet-arch")
        second = second_data[-1].plan
        self.assertNotEqual(first.fingerprint.digest, second.fingerprint.digest)
        self.assertTrue(all("cedar" not in json.dumps(item) for item in second.mappings))
        verify_renderer_compatibility_plan(
            second.bundle, evidence_snapshot=second_data[0], lifecycle_scope=second_data[3],
            declaration=second_data[2], authorization=second_data[4],
            expected_plan_fingerprint=second.fingerprint.digest,
        )

    def test_missing_required_capability_returns_complete_negative_findings_and_no_plan(self):
        snapshot, produced = self._release()
        declaration = self._declaration()
        claims = tuple(item for item in declaration.capabilities if "static-state" not in item.identity and "inline-inspection" not in item.identity)
        bad = replace(declaration, capabilities=claims, fingerprint="")
        bad = replace(bad, fingerprint=compute_capability_declaration_fingerprint(bad))
        result = produce_renderer_compatibility_plan(
            verified_release=produced, evidence_snapshot=snapshot, lifecycle_scope=self._scope(produced),
            declaration=bad, authorization=self._authorization(produced, bad),
        )
        self.assertBlocked(result, "required-expression-unavailable")
        blocked_requirements = {finding.requirement_identity for finding in result.findings if finding.code == "required-expression-unavailable"}
        self.assertEqual(blocked_requirements, {"requirement:cedar-inspection", "requirement:cedar-selection"})

    def test_missing_or_malformed_capability_declaration_fails_closed(self):
        snapshot, produced = self._release()
        scope = self._scope(produced)
        declaration = self._declaration()
        auth = self._authorization(produced, declaration)
        self.assertBlocked(produce_renderer_compatibility_plan(
            verified_release=produced, evidence_snapshot=snapshot, lifecycle_scope=scope,
            declaration=None, authorization=auth,
        ), "missing-capability-declaration")
        for bad in (
            replace(declaration, renderer_identity="renderer:other"),
            replace(declaration, renderer_version=""),
            replace(declaration, capability_profile_version="9.0.0"),
            replace(declaration, renderer_owner="project:Other"),
            replace(declaration, renderer_role="artifact-conformance-authority"),
            replace(declaration, inventory_complete=False),
            replace(declaration, fingerprint="0" * 64),
        ):
            with self.subTest(bad=bad):
                result = produce_renderer_compatibility_plan(
                    verified_release=produced, evidence_snapshot=snapshot, lifecycle_scope=scope,
                    declaration=bad, authorization=auth,
                )
                self.assertTrue(result.blocked)
                self.assertIsNone(result.plan)

    def test_duplicate_or_ambiguous_capability_match_blocks(self):
        snapshot, produced = self._release()
        declaration = self._declaration()
        duplicate = replace(declaration, capabilities=declaration.capabilities + (declaration.capabilities[0],), fingerprint="")
        duplicate = replace(duplicate, fingerprint=compute_capability_declaration_fingerprint(duplicate))
        result = produce_renderer_compatibility_plan(
            verified_release=produced, evidence_snapshot=snapshot, lifecycle_scope=self._scope(produced),
            declaration=duplicate, authorization=self._authorization(produced, duplicate),
        )
        self.assertBlocked(result, "duplicate-capability-identity")

    def test_mutable_declaration_sequences_are_rejected_even_with_matching_fingerprint(self):
        snapshot, produced = self._release()
        declaration = self._declaration()
        mutable_claim = replace(declaration.capabilities[0], constraints=list(declaration.capabilities[0].constraints))
        bad = replace(
            declaration,
            capabilities=(mutable_claim,) + declaration.capabilities[1:],
            unsupported_capabilities=list(declaration.unsupported_capabilities),
            declared_constraints=list(declaration.declared_constraints),
            extensions=[],
            fingerprint="",
        )
        bad = replace(bad, fingerprint=compute_capability_declaration_fingerprint(bad))
        result = produce_renderer_compatibility_plan(
            verified_release=produced, evidence_snapshot=snapshot,
            lifecycle_scope=self._scope(produced), declaration=bad,
            authorization=self._authorization(produced, bad),
        )
        self.assertBlocked(result, "invalid-capability-inventory")

        malformed_claim = replace(declaration.capabilities[0], identity=[])
        malformed = replace(
            declaration,
            capabilities=(malformed_claim,) + declaration.capabilities[1:],
            fingerprint="0" * 64,
        )
        malformed_result = produce_renderer_compatibility_plan(
            verified_release=produced, evidence_snapshot=snapshot,
            lifecycle_scope=self._scope(produced), declaration=malformed,
            authorization=self._authorization(produced, malformed),
        )
        self.assertBlocked(malformed_result, "invalid-capability-claim")

    def test_unknown_or_mode_inconsistent_fallback_kind_blocks(self):
        for kind, mode in (
            ("renderer-invocation", "equivalent"),
            ("static-table", "equivalent"),
            ("equivalent-expression", []),
        ):
            def mutate(_requirements, fallbacks, selected_kind=kind, selected_mode=mode):
                fallbacks[0]["kind"] = selected_kind
                fallbacks[0]["expression_mode"] = selected_mode

            with self.subTest(kind=kind, mode=mode):
                snapshot, produced = self._release(mutate=mutate)
                declaration = self._declaration()
                result = produce_renderer_compatibility_plan(
                    verified_release=produced, evidence_snapshot=snapshot,
                    lifecycle_scope=self._scope(produced), declaration=declaration,
                    authorization=self._authorization(produced, declaration),
                )
                self.assertBlocked(result, "invalid-fallback")

    def test_same_rank_fallback_ambiguity_blocks_and_equivalent_precedes_static(self):
        def ambiguous(requirements, fallbacks):
            duplicate = deepcopy(fallbacks[0])
            duplicate["id"] = "fallback:cedar-second-equivalent"
            fallbacks.append(duplicate)
            requirements[1]["fallback_refs"].append(duplicate["id"])

        snapshot, produced = self._release(mutate=ambiguous)
        declaration = self._declaration()
        result = produce_renderer_compatibility_plan(
            verified_release=produced, evidence_snapshot=snapshot,
            lifecycle_scope=self._scope(produced), declaration=declaration,
            authorization=self._authorization(produced, declaration),
        )
        self.assertBlocked(result, "ambiguous-fallback-match")

        def add_static(requirements, fallbacks):
            static = deepcopy(fallbacks[0])
            static.update({
                "id": "fallback:cedar-inspection-static",
                "kind": "static-text", "expression_mode": "static",
                "required_capability": "capability:cedar-static-inspection",
            })
            fallbacks.append(static)
            requirements[1]["fallback_refs"].append(static["id"])

        snapshot, produced = self._release(mutate=add_static)
        base = self._declaration()
        declaration = replace(
            base,
            capabilities=base.capabilities + (
                CapabilityClaim("capability:cedar-static-inspection", "static", ("offline",), True),
            ),
            fingerprint="",
        )
        declaration = replace(declaration, fingerprint=compute_capability_declaration_fingerprint(declaration))
        result = produce_renderer_compatibility_plan(
            verified_release=produced, evidence_snapshot=snapshot,
            lifecycle_scope=self._scope(produced), declaration=declaration,
            authorization=self._authorization(produced, declaration),
        )
        self.assertFalse(result.blocked)
        inspection = next(item for item in result.plan.mappings if item["requirement_id"] == "requirement:cedar-inspection")
        self.assertEqual(inspection["selected_expression_mode"], "equivalent")

    def test_release_snapshot_publication_ready_and_authorization_drift_fail(self):
        snapshot, produced, declaration, scope, authorization, _ = self._plan()
        variants = [
            replace(authorization, release_identity="release:other"),
            replace(authorization, release_fingerprint="0" * 64),
            replace(authorization, capability_declaration_identity="renderer-capability:other"),
            replace(authorization, capability_declaration_fingerprint="0" * 64),
            replace(authorization, policy_identity="policy:other"),
            replace(authorization, authority_role="renderer"),
        ]
        for bad in variants:
            with self.subTest(bad=bad):
                self.assertTrue(produce_renderer_compatibility_plan(
                    verified_release=produced, evidence_snapshot=snapshot, lifecycle_scope=scope,
                    declaration=declaration, authorization=bad,
                ).blocked)
        bad_snapshot = replace(snapshot, inventory_digest="0" * 64)
        self.assertTrue(produce_renderer_compatibility_plan(
            verified_release=produced, evidence_snapshot=bad_snapshot, lifecycle_scope=scope,
            declaration=declaration, authorization=authorization,
        ).blocked)
        drifted = produced.bundle
        drifted.one("ReadyPresentationPackageRecord").identity = "ready:other"
        with self.assertRaises(Exception):
            release_tests.verify_publication_release(drifted, evidence_snapshot=snapshot)

    def test_lifecycle_scope_must_be_explicit_complete_and_fingerprint_bound(self):
        snapshot, produced, declaration, scope, authorization, _ = self._plan()
        for bad in (
            replace(scope, inventory_complete=False),
            replace(scope, inventory_digest="0" * 64),
            replace(scope, releases=()),
        ):
            with self.subTest(bad=bad):
                self.assertTrue(produce_renderer_compatibility_plan(
                    verified_release=produced, evidence_snapshot=snapshot, lifecycle_scope=bad,
                    declaration=declaration, authorization=authorization,
                ).blocked)
        malformed = replace(scope, bundle=None)
        result = produce_renderer_compatibility_plan(
            verified_release=produced, evidence_snapshot=snapshot, lifecycle_scope=malformed,
            declaration=declaration, authorization=authorization,
        )
        self.assertBlocked(result, "invalid-lifecycle-scope")

        mutable_policy = lifecycle_tests.policy()
        mutable_policy = replace(
            mutable_policy,
            allowed_authorities=list(mutable_policy.allowed_authorities),
            allowed_event_types=list(mutable_policy.allowed_event_types),
            allowed_reason_classifications=list(mutable_policy.allowed_reason_classifications),
            distribution_consequences=list(mutable_policy.distribution_consequences),
        )
        mutable_scope = replace(scope, policies=(mutable_policy,), inventory_digest="")
        mutable_scope = replace(mutable_scope, inventory_digest=compute_lifecycle_inventory_digest(mutable_scope))
        result = produce_renderer_compatibility_plan(
            verified_release=produced, evidence_snapshot=snapshot, lifecycle_scope=mutable_scope,
            declaration=declaration, authorization=authorization,
        )
        self.assertBlocked(result, "invalid-lifecycle-scope")

    def test_withdrawn_superseded_and_ambiguous_lifecycle_states_reject(self):
        snapshot, produced = self._release()
        declaration = self._declaration()
        authorization = self._authorization(produced, declaration)
        binding = release_tests.release_binding_from_verified_release(produced)
        policy = lifecycle_tests.policy()

        withdrawal_doc = lifecycle_tests.withdrawal_document(
            identity="lifecycle-event:cedar-withdrawal", target_identity=binding.identity,
            target_fingerprint=binding.fingerprint, time="2026-07-18T10:00:00Z",
        )
        withdrawal_doc["semantic"]["publication_identity"] = binding.publication_identity
        withdrawn = self._scope(produced, events=(event_from_document(withdrawal_doc),), policies=(policy,))
        self.assertTrue(produce_renderer_compatibility_plan(
            verified_release=produced, evidence_snapshot=snapshot, lifecycle_scope=withdrawn,
            declaration=declaration, authorization=authorization,
        ).blocked)

        successor = replace(
            binding, identity="release:cedar-v2", fingerprint="b" * 64,
            fingerprint_root_identity="release:cedar-v2", semantic_publication_version="2.0.0",
            publication_time="2026-07-18T08:00:00Z",
        )
        supersession_doc = lifecycle_tests.event_document(
            identity="lifecycle-event:cedar-supersession", target_identity=binding.identity,
            target_fingerprint=binding.fingerprint, predecessor_identity=binding.identity,
            predecessor_fingerprint=binding.fingerprint, successor_identity=successor.identity,
            successor_fingerprint=successor.fingerprint, time="2026-07-18T10:00:00Z",
        )
        supersession_doc["semantic"]["publication_identity"] = binding.publication_identity
        superseded = self._scope(
            produced, events=(event_from_document(supersession_doc),),
            releases=(binding, successor), policies=(policy,),
        )
        self.assertTrue(produce_renderer_compatibility_plan(
            verified_release=produced, evidence_snapshot=snapshot, lifecycle_scope=superseded,
            declaration=declaration, authorization=authorization,
        ).blocked)

        ambiguous = replace(scope := self._scope(produced), releases=(binding, replace(
            binding, identity="release:cedar-orphan", fingerprint="c" * 64,
            fingerprint_root_identity="release:cedar-orphan",
        )), inventory_digest="")
        ambiguous = replace(ambiguous, inventory_digest=compute_lifecycle_inventory_digest(ambiguous))
        self.assertTrue(produce_renderer_compatibility_plan(
            verified_release=produced, evidence_snapshot=snapshot, lifecycle_scope=ambiguous,
            declaration=declaration, authorization=authorization,
        ).blocked)

    def test_unapproved_incomplete_or_lossy_fallbacks_and_required_unsupported_block(self):
        def unapproved(requirements, _fallbacks):
            requirements[1]["fallback_refs"] = ["fallback:unknown"]

        with self.assertRaises(Exception):
            self._release(mutate=unapproved)

        def incomplete(_requirements, fallbacks):
            fallbacks[1]["covers_semantic_refs"].pop()

        def caveat_loss(_requirements, fallbacks):
            fallbacks[1]["preserves_caveat_refs"] = []

        def authority_loss(_requirements, fallbacks):
            fallbacks[0]["preserves_authority_label_refs"] = []

        def required_unsupported(requirements, _fallbacks):
            requirements[3]["mandatory"] = True
            requirements[3]["criticality"] = "required"

        for label, mutator in (
            ("incomplete-semantic-coverage", incomplete),
            ("caveat-loss", caveat_loss),
            ("authority-label-loss", authority_loss),
            ("unsupported-required-meaning", required_unsupported),
        ):
            with self.subTest(label=label):
                snapshot, produced = self._release(mutate=mutator)
                declaration = self._declaration()
                result = produce_renderer_compatibility_plan(
                    verified_release=produced, evidence_snapshot=snapshot,
                    lifecycle_scope=self._scope(produced), declaration=declaration,
                    authorization=self._authorization(produced, declaration),
                )
                self.assertBlocked(result, "required-expression-unavailable")

    def test_persisted_verifier_rejects_malformed_or_mutable_bundle_envelopes(self):
        snapshot, _, declaration, scope, authorization, result = self._plan()
        valid = result.plan.bundle
        malformed_inputs = (
            None,
            {},
            BCRPBundle(valid.profile_identity, valid.profile_version, list(valid.records)),
            BCRPBundle(valid.profile_identity, valid.profile_version, (None,) * 8),
        )
        for malformed in malformed_inputs:
            with self.subTest(malformed_type=type(malformed).__name__), self.assertRaises(PlanningRejected):
                verify_renderer_compatibility_plan(
                    malformed, evidence_snapshot=snapshot, lifecycle_scope=scope,
                    declaration=declaration, authorization=authorization,
                )

    def test_duplicate_and_unmapped_requirements_are_rejected_from_persisted_plan(self):
        snapshot, _, declaration, scope, authorization, result = self._plan()
        for mutation in ("duplicate", "missing"):
            bundle = result.plan.bundle
            payload = bundle.one("RendererCompatibilityPlanRecord").extensions[0]["payload"]
            if mutation == "duplicate":
                payload["mappings"].append(deepcopy(payload["mappings"][0]))
            else:
                payload["mappings"].pop()
            with self.subTest(mutation=mutation), self.assertRaises(PlanningRejected):
                verify_renderer_compatibility_plan(
                    bundle, evidence_snapshot=snapshot, lifecycle_scope=scope,
                    declaration=declaration, authorization=authorization,
                )

    def test_plan_tampering_and_conformance_claim_are_rejected(self):
        snapshot, _, declaration, scope, authorization, result = self._plan()
        mutations = []
        core = result.plan.bundle
        core.one("RendererCompatibilityPlanRecord").semantic["ready_ref"] = "ready:other"
        mutations.append(core)
        payload = result.plan.bundle
        payload.one("RendererCompatibilityPlanRecord").extensions[0]["payload"]["mappings"][0]["reason"] = "caller override"
        mutations.append(payload)
        proof = result.plan.bundle
        proof.one("RendererCompatibilityPlanRecord").extensions[0]["payload"]["capability_claim_character"] = "artifact-conformance-proof"
        mutations.append(proof)
        for bundle in mutations:
            with self.subTest(), self.assertRaises(PlanningRejected):
                verify_renderer_compatibility_plan(
                    bundle, evidence_snapshot=snapshot, lifecycle_scope=scope,
                    declaration=declaration, authorization=authorization,
                )

    def test_stale_plan_after_renderer_or_lifecycle_change_is_ineligible(self):
        snapshot, produced, declaration, scope, authorization, result = self._plan()
        changed_renderer = replace(declaration, renderer_version="3.2.2", fingerprint="")
        changed_renderer = replace(changed_renderer, fingerprint=compute_capability_declaration_fingerprint(changed_renderer))
        with self.assertRaises(PlanningRejected):
            verify_renderer_compatibility_plan(
                result.plan.bundle, evidence_snapshot=snapshot, lifecycle_scope=scope,
                declaration=changed_renderer, authorization=authorization,
            )

        binding = release_tests.release_binding_from_verified_release(produced)
        document = lifecycle_tests.withdrawal_document(
            identity="lifecycle-event:cedar-later-withdrawal", target_identity=binding.identity,
            target_fingerprint=binding.fingerprint, time="2026-07-18T10:00:00Z",
        )
        document["semantic"]["publication_identity"] = binding.publication_identity
        changed_scope = self._scope(
            produced, events=(event_from_document(document),), policies=(lifecycle_tests.policy(),),
        )
        with self.assertRaises(PlanningRejected):
            verify_renderer_compatibility_plan(
                result.plan.bundle, evidence_snapshot=snapshot, lifecycle_scope=changed_scope,
                declaration=declaration, authorization=authorization,
            )

    def test_generic_bcrp_remains_fail_closed_and_core_count_and_import_boundary_hold(self):
        _, _, _, _, _, result = self._plan()
        validation = validate_bundle(result.plan.bundle, through_layer="L5")
        self.assertTrue(validation.blocking)
        self.assertIn("extension-boundary", {finding.family for finding in validation.findings})
        self.assertEqual(len(RECORD_KINDS), 11)
        script = """
import sys
import briefforge.bcrp
forbidden = ('publication_release', 'publication_lifecycle', 'renderer_compatibility_planning', 'renderer_adapter', 'renderer', 'artifact', 'manifest')
loaded = sorted(name for name in sys.modules if name.startswith('briefforge.') and any(token in name for token in forbidden))
assert loaded == [], loaded
print('BCRP compatibility-planner import independence: PASS')
"""
        completed = subprocess.run(
            [sys.executable, "-B", "-c", script], cwd=PROJECT_ROOT,
            env={"PYTHONPATH": str(PROJECT_ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"},
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_source_contains_no_fixture_or_domain_specialization_and_imports_no_renderer(self):
        source = (PROJECT_ROOT / "src" / "briefforge" / "renderer_compatibility_planning.py").read_text(encoding="utf-8")
        forbidden = (
            "TASK-039", "golden-case", "tests/fixtures", "mutation-label",
            "demographic", "company", "financial", "renderer_adapter", "importlib", "subprocess",
        )
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
