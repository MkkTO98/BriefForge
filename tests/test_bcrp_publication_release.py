"""TASK-050 governed Publication Release production and lifecycle proof."""
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

from briefforge.bcrp import BCRPBundle, BCRPRecord, fingerprint_bundle, validate_bundle  # noqa: E402
from briefforge.bcrp.corpus import CASE_IDS, load_case  # noqa: E402
from briefforge.bcrp_legacy_compatibility import map_legacy_ready_to_bcrp  # noqa: E402
from briefforge.publication_lifecycle import (  # noqa: E402
    CANONICALIZATION_ID as LIFECYCLE_CANONICALIZATION_ID,
    PROFILE_ID as LIFECYCLE_PROFILE_ID,
    PROFILE_VERSION as LIFECYCLE_PROFILE_VERSION,
    EventAuthority,
    LifecycleBundle,
    LifecyclePolicy,
    PublicationLifecycleEvent,
    ReleaseReference,
    derive_current_state,
    validate_lifecycle,
)
from briefforge.publication_release import (  # noqa: E402
    ACCEPTED_AUTHORITY_IDENTITY,
    ACCEPTED_AUTHORITY_OWNER,
    ACCEPTED_AUTHORITY_ROLE,
    RELEASE_POLICY_ID,
    EvidenceInventoryItem,
    EvidenceSnapshot,
    PublicationReleaseAuthorization,
    ReleaseRejected,
    compute_evidence_inventory_digest,
    produce_publication_release,
    release_binding_from_verified_release,
    verify_publication_release,
)
from tests import test_bcrp_lifecycle_authority_compatibility as compatibility_tests  # noqa: E402


class PublicationReleaseProductionTests(unittest.TestCase):
    constraints = ("public-static-read", "standalone-operation")

    def _mapped_ready(self, suffix: str, case_index: int, snapshot: EvidenceSnapshot) -> BCRPBundle:
        helper = compatibility_tests.LegacyCompatibilityContractTests(
            "test_complete_synthetic_legacy_closure_maps_successfully"
        )
        legacy_candidate, legacy_judgment, legacy_ready = helper._legacy_closure(suffix, case_index + 2)
        bcrp = helper._bcrp_candidate(case_index)
        material = bcrp.one("PortablePresentationMaterialRecord")
        old_snapshot_identity = material.semantic["evidence_snapshots"][0]["id"]

        def replace_snapshot_reference(value):
            if isinstance(value, dict):
                return {key: replace_snapshot_reference(item) for key, item in value.items()}
            if isinstance(value, list):
                return [replace_snapshot_reference(item) for item in value]
            return snapshot.identity if value == old_snapshot_identity else value

        for record in bcrp.records:
            record.semantic = replace_snapshot_reference(record.semantic)
        material = bcrp.one("PortablePresentationMaterialRecord")
        material.semantic["evidence_snapshots"] = [{
            "id": snapshot.identity,
            "version": snapshot.version,
            "content_fingerprint": f"sha256:{snapshot.inventory_digest}",
            "provenance_ref": material.semantic["provenance"][0]["id"],
        }]
        material.semantic["authorities"] = [
            authority for authority in material.semantic["authorities"]
            if authority.get("id") != ACCEPTED_AUTHORITY_IDENTITY
        ] + [{
            "id": ACCEPTED_AUTHORITY_IDENTITY,
            "owner_identity": ACCEPTED_AUTHORITY_OWNER,
            "role": ACCEPTED_AUTHORITY_ROLE,
            "scope": "fixed-evidence-publication-release",
        }]
        mapping = helper._mapping(legacy_candidate, bcrp, suffix=suffix)
        return map_legacy_ready_to_bcrp(
            legacy_candidate=legacy_candidate,
            legacy_judgment=legacy_judgment,
            legacy_ready=legacy_ready,
            bcrp_candidate_bundle=bcrp,
            mapping=mapping,
        )

    def _snapshot(self, suffix: str, count: int = 2, *, time: str = "2026-07-16T11:00:00Z") -> EvidenceSnapshot:
        items = tuple(
            EvidenceInventoryItem(f"evidence:{suffix}-{index}", f"sha256:{index + 1:064x}")
            for index in range(count)
        )
        values = dict(
            identity=f"snapshot:{suffix}", version="1", scope_identity=f"scope:{suffix}",
            snapshot_time=time, inventory_complete=True, closure_status="closed", inventory=items,
        )
        return EvidenceSnapshot(**values, inventory_digest=compute_evidence_inventory_digest(**values))

    def _authorization(
        self, mapped: BCRPBundle, snapshot: EvidenceSnapshot, suffix: str, *,
        publication_identity: str | None = None, publication_version: str = "1.0.0",
        authorization_time: str = "2026-07-16T12:03:00Z",
        release_identity: str | None = None,
        release_time: str = "2026-07-16T12:04:00Z",
        release_constraints: tuple[str, ...] | None = None,
        includes_recommendations: bool = False,
    ) -> PublicationReleaseAuthorization:
        candidate_digest = fingerprint_bundle(mapped, domain="candidate-semantic", require_valid=False).digest
        closure_digest = fingerprint_bundle(mapped, domain="profile-instance", require_valid=False).digest
        return PublicationReleaseAuthorization(
            identity=f"authorization:{suffix}", policy_identity=RELEASE_POLICY_ID,
            authority_identity=ACCEPTED_AUTHORITY_IDENTITY, authority_owner=ACCEPTED_AUTHORITY_OWNER,
            authority_role=ACCEPTED_AUTHORITY_ROLE, authorization_time=authorization_time,
            publication_identity=publication_identity or f"publication:{suffix}",
            publication_version=publication_version,
            ready_identity=mapped.one("ReadyPresentationPackageRecord").identity,
            candidate_fingerprint=candidate_digest,
            governed_ready_closure_fingerprint=closure_digest,
            evidence_snapshot_identity=snapshot.identity, evidence_snapshot_version=snapshot.version,
            evidence_inventory_digest=snapshot.inventory_digest, initial_release_state="active",
            distribution_constraints=self.constraints,
            release_identity=release_identity or f"release:{suffix}",
            release_time=release_time,
            release_distribution_constraints=release_constraints or self.constraints,
            includes_recommendations=includes_recommendations,
        )

    def _produce(
        self, suffix: str = "crimson-forest", case_index: int = 1, *,
        publication_identity: str | None = None, publication_version: str = "1.0.0",
        release_time: str = "2026-07-16T12:04:00Z",
    ):
        snapshot = self._snapshot(suffix, case_index + 1)
        mapped = self._mapped_ready(suffix, case_index, snapshot)
        authorization = self._authorization(
            mapped, snapshot, suffix, publication_identity=publication_identity,
            publication_version=publication_version, release_time=release_time,
        )
        produced = produce_publication_release(
            governed_ready=mapped, evidence_snapshot=snapshot, authorization=authorization,
            publication_identity=authorization.publication_identity,
            publication_version=publication_version, release_identity=f"release:{suffix}",
            release_time=release_time, distribution_constraints=self.constraints,
            includes_recommendations=False,
        )
        return mapped, snapshot, authorization, produced

    def test_complete_governed_ready_produces_exact_deterministic_immutable_release(self):
        mapped, snapshot, authorization, first = self._produce()
        before_bundle, before_snapshot, before_authorization = deepcopy(mapped), deepcopy(snapshot), deepcopy(authorization)
        second = produce_publication_release(
            governed_ready=mapped, evidence_snapshot=snapshot, authorization=authorization,
            publication_identity=authorization.publication_identity,
            publication_version=authorization.publication_version,
            release_identity="release:crimson-forest", release_time="2026-07-16T12:04:00Z",
            distribution_constraints=self.constraints, includes_recommendations=False,
        )
        self.assertEqual(first.bundle, second.bundle)
        self.assertEqual(first.fingerprint, second.fingerprint)
        self.assertEqual(len(first.bundle.records_of_kind("PublicationReleaseRecord")), 1)
        self.assertEqual(mapped, before_bundle)
        self.assertEqual(snapshot, before_snapshot)
        self.assertEqual(authorization, before_authorization)
        verified = verify_publication_release(
            first.bundle, evidence_snapshot=snapshot, expected_release_fingerprint=first.fingerprint.digest
        )
        self.assertEqual(verified.fingerprint, first.fingerprint)

    def test_one_authorization_targets_only_one_exact_release_act(self):
        mapped, snapshot, authorization, produced = self._produce("one-act", 0)
        self.assertEqual(produced.release.identity, authorization.release_identity)
        variants = (
            {"release_identity": "release:second"},
            {"release_time": "2026-07-16T12:05:00Z"},
            {"includes_recommendations": True},
            {"distribution_constraints": ("public-static-read",)},
        )
        base = dict(
            governed_ready=mapped,
            evidence_snapshot=snapshot,
            authorization=authorization,
            publication_identity=authorization.publication_identity,
            publication_version=authorization.publication_version,
            release_identity=authorization.release_identity,
            release_time=authorization.release_time,
            distribution_constraints=authorization.release_distribution_constraints,
            includes_recommendations=authorization.includes_recommendations,
        )
        for change in variants:
            with self.subTest(change=change), self.assertRaises(ReleaseRejected):
                produce_publication_release(**(base | change))

    def test_verified_output_is_detached_and_lifecycle_projection_reverifies(self):
        _, _, _, produced = self._produce("detached", 0)
        fingerprint = produced.fingerprint
        release_copy = produced.release
        bundle_copy = produced.bundle
        release_copy.semantic["publication_lineage_id"] = "publication:mutated"
        bundle_copy.one("PublicationReleaseRecord").semantic["publication_lineage_id"] = "publication:also-mutated"
        self.assertEqual(produced.release.semantic["publication_lineage_id"], "publication:detached")
        self.assertEqual(produced.fingerprint, fingerprint)
        binding = release_binding_from_verified_release(produced)
        self.assertEqual(binding.publication_identity, "publication:detached")
        self.assertEqual(binding.fingerprint, fingerprint.digest)

    def test_release_binds_exact_judgment_and_ready_compatibility_closure(self):
        _, snapshot, _, produced = self._produce("closure-binding", 0)
        drifted = produced.bundle
        for kind in ("ValidationJudgmentRecord", "ReadyPresentationPackageRecord"):
            drifted.one(kind).extensions[0]["payload"]["mapping_attestation"]["attestation_time"] = (
                "2026-07-16T12:02:30Z"
            )
        self.assertEqual(
            fingerprint_bundle(drifted, domain="release-semantic", require_valid=False).digest,
            produced.fingerprint.digest,
        )
        with self.assertRaises(ReleaseRejected):
            verify_publication_release(drifted, evidence_snapshot=snapshot)

    def test_materially_different_second_case_produces_different_valid_release(self):
        _, snapshot_a, _, first = self._produce("umber-orbit", 0)
        _, snapshot_b, _, second = self._produce("teal-harbor", 2)
        self.assertNotEqual(first.fingerprint.digest, second.fingerprint.digest)
        self.assertNotEqual(snapshot_a.inventory_digest, snapshot_b.inventory_digest)
        self.assertEqual(len(second.bundle.one("CandidatePresentationPackageRecord").semantic["statements"]), 9)
        verify_publication_release(second.bundle, evidence_snapshot=snapshot_b)

    def test_native_ready_and_corpus_possession_have_no_operational_authority(self):
        corpus = load_case(CASE_IDS[0])
        with self.assertRaises(ReleaseRejected):
            verify_publication_release(corpus, evidence_snapshot=self._snapshot("corpus"))
        native = deepcopy(corpus)
        native.records = tuple(record for record in native.records if record.kind not in {
            "PublicationReleaseRecord", "RendererCapabilityDeclarationRecord", "RendererCompatibilityPlanRecord",
            "GeneratedArtifactAuditRecord", "SemanticArtifactConformanceRecord", "PublicationManifestRecord",
        })
        with self.assertRaises(ReleaseRejected):
            produce_publication_release(
                governed_ready=native, evidence_snapshot=self._snapshot("native"),
                authorization=object(), publication_identity="publication:native", publication_version="1.0.0",
                release_identity="release:native", release_time="2026-07-16T12:04:00Z",
                distribution_constraints=self.constraints, includes_recommendations=False,
            )

    def test_authorization_mismatches_fail_closed(self):
        snapshot = self._snapshot("authorization")
        mapped = self._mapped_ready("authorization", 0, snapshot)
        valid = self._authorization(mapped, snapshot, "authorization")
        variants = (
            replace(valid, policy_identity="policy:unknown"),
            replace(valid, authority_owner="project:Other"),
            replace(valid, authority_role="validation-authority"),
            replace(valid, publication_identity="publication:other"),
            replace(valid, publication_version="2.0.0"),
            replace(valid, ready_identity="ready:other"),
            replace(valid, candidate_fingerprint="0" * 64),
            replace(valid, governed_ready_closure_fingerprint="0" * 64),
            replace(valid, evidence_snapshot_identity="snapshot:other"),
            replace(valid, distribution_constraints=("unbounded-distribution",)),
            replace(valid, release_identity="release:other"),
            replace(valid, release_time="2026-07-16T12:05:00Z"),
            replace(valid, release_distribution_constraints=("public-static-read",)),
            replace(valid, includes_recommendations=True),
        )
        for variant in variants:
            with self.subTest(variant=variant), self.assertRaises(ReleaseRejected):
                produce_publication_release(
                    governed_ready=mapped, evidence_snapshot=snapshot, authorization=variant,
                    publication_identity=valid.publication_identity, publication_version=valid.publication_version,
                    release_identity="release:authorization", release_time="2026-07-16T12:04:00Z",
                    distribution_constraints=self.constraints, includes_recommendations=False,
                )

    def test_required_explicit_identity_version_time_snapshot_inventory_and_constraints_fail_closed(self):
        snapshot = self._snapshot("required")
        mapped = self._mapped_ready("required", 0, snapshot)
        auth = self._authorization(mapped, snapshot, "required")
        common = dict(governed_ready=mapped, evidence_snapshot=snapshot, authorization=auth,
                      publication_identity=auth.publication_identity, publication_version=auth.publication_version,
                      release_identity="release:required", release_time="2026-07-16T12:04:00Z",
                      distribution_constraints=self.constraints, includes_recommendations=False)
        for key, value in (("publication_identity", ""), ("publication_version", ""),
                           ("release_identity", ""), ("release_time", ""),
                           ("distribution_constraints", ())):
            with self.subTest(key=key), self.assertRaises(ReleaseRejected):
                produce_publication_release(**(common | {key: value}))
        for invalid in (
            replace(snapshot, inventory_complete=False), replace(snapshot, closure_status="open"),
            replace(snapshot, inventory_digest="0" * 64), replace(snapshot, snapshot_time=""),
        ):
            with self.subTest(snapshot=invalid), self.assertRaises(ReleaseRejected):
                produce_publication_release(**(common | {"evidence_snapshot": invalid}))

    def test_explicitly_empty_complete_inventory_is_not_missing_information(self):
        snapshot = self._snapshot("empty", 0)
        mapped = self._mapped_ready("empty", 0, snapshot)
        auth = self._authorization(mapped, snapshot, "empty")
        produced = produce_publication_release(
            governed_ready=mapped, evidence_snapshot=snapshot, authorization=auth,
            publication_identity=auth.publication_identity, publication_version="1.0.0",
            release_identity="release:empty", release_time="2026-07-16T12:04:00Z",
            distribution_constraints=self.constraints, includes_recommendations=False,
        )
        verify_publication_release(produced.bundle, evidence_snapshot=snapshot)

    def test_persisted_unknown_fields_tampering_roots_states_and_embedded_events_fail(self):
        _, snapshot, _, produced = self._produce("persisted", 1)
        mutations = []
        unknown_semantic = deepcopy(produced.bundle)
        unknown_semantic.one("PublicationReleaseRecord").semantic["undeclared"] = True
        mutations.append(unknown_semantic)
        unknown_payload = deepcopy(produced.bundle)
        unknown_payload.one("PublicationReleaseRecord").extensions[0]["payload"]["undeclared"] = True
        mutations.append(unknown_payload)
        tampered = deepcopy(produced.bundle)
        tampered.one("PublicationReleaseRecord").semantic["semantic_publication_version"] = "9.9.9"
        mutations.append(tampered)
        competing = deepcopy(produced.bundle)
        competing.records += (deepcopy(competing.one("PublicationReleaseRecord")),)
        mutations.append(competing)
        unsupported = deepcopy(produced.bundle)
        unsupported.one("PublicationReleaseRecord").semantic["lifecycle_status"] = "withdrawn"
        mutations.append(unsupported)
        embedded = deepcopy(produced.bundle)
        embedded.one("PublicationReleaseRecord").semantic["lifecycle_events"] = []
        mutations.append(embedded)
        extra_extension = deepcopy(produced.bundle)
        extra_extension.one("PublicationReleaseRecord").extensions.append(
            deepcopy(extra_extension.one("PublicationReleaseRecord").extensions[0])
        )
        mutations.append(extra_extension)
        for bundle in mutations:
            with self.subTest(), self.assertRaises(ReleaseRejected):
                verify_publication_release(bundle, evidence_snapshot=snapshot)
        with self.assertRaises(ReleaseRejected):
            verify_publication_release(
                produced.bundle, evidence_snapshot=snapshot, expected_release_fingerprint="0" * 64
            )

    def test_snapshot_inventory_and_material_drift_fail_closed(self):
        _, snapshot, _, produced = self._produce("snapshot-drift", 0)
        drift = replace(snapshot, inventory=(EvidenceInventoryItem("evidence:added", "sha256:" + "a" * 64),) + snapshot.inventory)
        with self.assertRaises(ReleaseRejected):
            verify_publication_release(produced.bundle, evidence_snapshot=drift)
        material_drift = deepcopy(produced.bundle)
        material_drift.one("PortablePresentationMaterialRecord").semantic["evidence_snapshots"][0]["content_fingerprint"] = "sha256:" + "f" * 64
        with self.assertRaises(ReleaseRejected):
            verify_publication_release(material_drift, evidence_snapshot=snapshot)

    def test_generic_validation_remains_fail_closed_and_dedicated_path_is_narrow(self):
        _, snapshot, _, produced = self._produce("narrow", 1)
        generic = validate_bundle(produced.bundle, through_layer="L4")
        unsupported = [finding for finding in generic.findings if finding.message == "Unknown required semantic extension cannot be processed."]
        self.assertTrue(generic.blocking)
        self.assertEqual(
            {
                (finding.layer, finding.family, finding.severity, finding.semantic_identity, finding.location)
                for finding in unsupported
            },
            {
                ("L1", "extension-boundary", "blocking", produced.bundle.one("ValidationJudgmentRecord").identity, "/extensions/0"),
                ("L1", "extension-boundary", "blocking", produced.bundle.one("ReadyPresentationPackageRecord").identity, "/extensions/0"),
                ("L1", "extension-boundary", "blocking", produced.release.identity, "/extensions/0"),
            },
        )
        verified = verify_publication_release(produced.bundle, evidence_snapshot=snapshot)
        self.assertEqual(verified.executed_layers, ("L0", "L1", "L2", "L3", "L4"))
        broken = deepcopy(produced.bundle)
        broken.one("CandidatePresentationPackageRecord").semantic["statements"][0].pop("authority_ref")
        with self.assertRaises(ReleaseRejected):
            verify_publication_release(broken, evidence_snapshot=snapshot)

    def test_output_grants_no_manifest_renderer_artifact_conformance_distribution_or_event_authority(self):
        _, _, _, produced = self._produce("bounded", 2)
        self.assertEqual(len(produced.bundle.records), 6)
        for kind in ("RendererCapabilityDeclarationRecord", "RendererCompatibilityPlanRecord",
                     "GeneratedArtifactAuditRecord", "SemanticArtifactConformanceRecord", "PublicationManifestRecord"):
            self.assertEqual(produced.bundle.records_of_kind(kind), ())
        release = produced.bundle.one("PublicationReleaseRecord")
        payload = release.extensions[0]["payload"]
        self.assertEqual(payload["excluded_authorities"], [
            "candidate-authoring", "technical-validation", "governance-judgment", "ready-promotion",
            "legacy-compatibility-mapping", "lifecycle-event", "renderer", "artifact", "manifest",
            "distribution-execution",
        ])
        self.assertNotIn("lifecycle_events", release.semantic)

    def test_task049_zero_event_anchor_and_later_event_preserve_release(self):
        publication = "publication:lifecycle-proof"
        _, snapshot_a, _, first = self._produce("lifecycle-a", 0, publication_identity=publication, publication_version="1.0.0")
        _, snapshot_b, _, second = self._produce("lifecycle-b", 2, publication_identity=publication, publication_version="2.0.0", release_time="2026-07-16T13:04:00Z")
        first_binding = release_binding_from_verified_release(first)
        second_binding = release_binding_from_verified_release(second)
        initial = LifecycleBundle(LIFECYCLE_PROFILE_ID, LIFECYCLE_PROFILE_VERSION, ())
        self.assertFalse(validate_lifecycle(initial, (first_binding,), ()).blocking)
        self.assertEqual(derive_current_state(initial, (first_binding,), ()).current_release_identity, first.release.identity)
        before_first, before_second = first.fingerprint.digest, second.fingerprint.digest
        authority = EventAuthority("authority:lifecycle-governor", "project:BriefForge", "lifecycle-authority")
        policy = LifecyclePolicy(
            "policy:lifecycle-proof", ((authority.identity, authority.owner, authority.role),),
            ("supersession",), ("correction",),
            (("supersession", "predecessor-ineligible-successor-current"),),
        )
        event = PublicationLifecycleEvent(
            identity="event:lifecycle-proof-supersession", profile_identity=LIFECYCLE_PROFILE_ID,
            profile_version=LIFECYCLE_PROFILE_VERSION, publication_identity=publication,
            event_type="supersession", target_release=ReleaseReference(first_binding.identity, first_binding.fingerprint),
            predecessor_release=ReleaseReference(first_binding.identity, first_binding.fingerprint),
            successor_release=ReleaseReference(second_binding.identity, second_binding.fingerprint),
            reason_classification="correction", reason_detail="New governed semantics and snapshot.",
            authority=authority, policy_identity=policy.identity, event_time="2026-07-16T14:00:00Z",
            predecessor_event_refs=(), distribution_consequence="predecessor-ineligible-successor-current",
            extension_documents=(),
        )
        lifecycle = LifecycleBundle(LIFECYCLE_PROFILE_ID, LIFECYCLE_PROFILE_VERSION, (event,))
        self.assertFalse(validate_lifecycle(lifecycle, (first_binding, second_binding), (policy,)).blocking)
        state = derive_current_state(lifecycle, (first_binding, second_binding), (policy,))
        self.assertEqual(state.current_release_identity, second.release.identity)
        self.assertNotEqual(first.release.semantic["ready_ref"], second.release.semantic["ready_ref"])
        self.assertEqual(first.fingerprint.digest, before_first)
        self.assertEqual(second.fingerprint.digest, before_second)
        verify_publication_release(first.bundle, evidence_snapshot=snapshot_a, expected_release_fingerprint=before_first)
        verify_publication_release(second.bundle, evidence_snapshot=snapshot_b, expected_release_fingerprint=before_second)

    def test_release_time_and_authorization_time_ordering_fail_closed(self):
        snapshot = self._snapshot("times")
        mapped = self._mapped_ready("times", 0, snapshot)
        late = self._authorization(mapped, snapshot, "times", authorization_time="2026-07-16T13:00:00Z")
        with self.assertRaises(ReleaseRejected):
            produce_publication_release(
                governed_ready=mapped, evidence_snapshot=snapshot, authorization=late,
                publication_identity=late.publication_identity, publication_version=late.publication_version,
                release_identity="release:times", release_time="2026-07-16T12:04:00Z",
                distribution_constraints=self.constraints, includes_recommendations=False,
            )

    def test_importing_bcrp_imports_no_release_compatibility_lifecycle_or_downstream_modules(self):
        script = """
import json, sys
import briefforge.bcrp
blocked = ('bcrp_legacy_compatibility', 'publication_release', 'publication_lifecycle', 'renderer')
print(json.dumps(sorted(name for name in sys.modules if name.startswith('briefforge.') and any(part in name for part in blocked))))
"""
        result = subprocess.run(
            [sys.executable, "-B", "-c", script], cwd=PROJECT_ROOT,
            env={"PYTHONPATH": str(PROJECT_ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"},
            text=True, capture_output=True, check=True,
        )
        self.assertEqual(json.loads(result.stdout), [])


if __name__ == "__main__":
    unittest.main()
