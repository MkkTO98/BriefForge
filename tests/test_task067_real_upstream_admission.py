"""TASK-067 regression: real upstream Release/Plan verification issues admission."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from briefforge.bcrp_legacy_compatibility import map_legacy_ready_to_bcrp
from briefforge.bcrp import validate_bundle
from briefforge.bounded_loopback_deployment import DeploymentRouteItem, DeploymentTarget
from briefforge.publication_release import produce_publication_release
from briefforge.renderer_compatibility_planning import produce_renderer_compatibility_plan
from briefforge_terminal_profile.profile import build_terminal_authority_profile
from briefforge_paired_terminal_profile.profile import (
    PairedProfileRejected,
    build_paired_semantic_extension,
    consume_paired_upstream_admission,
    verify_full_upstream_paired_terminal_admission,
)
from briefforge_paired_terminal_profile.projection import build_paired_editorial_projection
from tests import paired_terminal_fixture as semantic_fixture
from tests import test_bcrp_lifecycle_authority_compatibility as compatibility_tests
from tests import test_bcrp_publication_release as release_tests
from tests import test_renderer_compatibility_planning as planning_tests


def _semantic_authority(authority_identity: str):
    """Bind every test-only display authority to one real BCRP record identity."""
    source = semantic_fixture.complete_semantics()
    bind = lambda item: replace(item, authority_ref=authority_identity)
    return replace(
        source,
        statements=tuple(map(bind, source.statements)),
        table=bind(source.table),
        values=tuple(map(bind, source.values)),
        qualifications=tuple(map(bind, source.qualifications)),
        provenance=tuple(map(bind, source.provenance)),
        obligations=tuple(map(bind, source.obligations)),
        content_authorities=(authority_identity,),
    )


class RealUpstreamAdmissionProof(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def _inputs(self, *, mutate_extension: bool = False):
        planning = planning_tests.RendererCompatibilityPlanningTests(
            "test_native_success_is_deterministic_immutable_and_complete")
        release_helper = release_tests.PublicationReleaseProductionTests(
            "test_complete_governed_ready_produces_exact_deterministic_immutable_release")
        compatibility = compatibility_tests.LegacyCompatibilityContractTests(
            "test_complete_synthetic_legacy_closure_maps_successfully")
        suffix = "task067-real-upstream"
        snapshot = release_helper._snapshot(suffix, 1)
        legacy_candidate, legacy_judgment, legacy_ready = compatibility._legacy_closure(suffix, 2)
        bcrp = compatibility._bcrp_candidate(0)
        material = bcrp.one("PortablePresentationMaterialRecord")
        # Reuse a semantic identity already defined by this governed BCRP record;
        # an invented authority label is not a resolvable BCRP identity.
        content_authority_identity = next(
            item["id"] for item in material.semantic["authorities"]
            if item.get("role") == "presentation-author"
        )
        old_snapshot = material.semantic["evidence_snapshots"][0]["id"]
        old_authorities = {
            item["id"] for item in material.semantic["authorities"] if type(item) is dict
        }

        def replace_refs(value):
            if isinstance(value, dict):
                return {key: replace_refs(item) for key, item in value.items()}
            if isinstance(value, list):
                return [replace_refs(item) for item in value]
            if value == old_snapshot:
                return snapshot.identity
            if value in old_authorities:
                return content_authority_identity
            return value

        for record in bcrp.records:
            record.semantic = replace_refs(record.semantic)

        directories = tuple(self.root / name for name in (
            "destination", "delivery", "deployment", "verification"))
        for directory in directories:
            directory.mkdir()
            directory.chmod(0o700)
        authority_profile = build_terminal_authority_profile(
            destination_parent=directories[0], destination_basename="paired.html",
            delivery_ledger=directories[1],
            target=DeploymentTarget("127.0.0.1", 38127, "http://127.0.0.1:38127"),
            routes=(DeploymentRouteItem("/paired.html", "paired.html", "text/html"),),
            deployment_ledger=directories[2], verification_ledger=directories[3],
            content_authorities=({
                "id": content_authority_identity,
                "owner_identity": "project:BriefForge",
                "role": "presentation-content-authority",
                "scope": "released-synthetic-paired-content",
            },),
        )
        material.semantic["evidence_snapshots"] = [{
            "id": snapshot.identity,
            "version": snapshot.version,
            "content_fingerprint": f"sha256:{snapshot.inventory_digest}",
            "provenance_ref": material.semantic["provenance"][0]["id"],
        }]
        material.semantic["authorities"] = [dict(item) for item in authority_profile.authorities]
        candidate = bcrp.one("CandidatePresentationPackageRecord")
        candidate.semantic["renderer_requirements"] = []
        candidate.semantic["fallbacks"] = []
        extension = build_paired_semantic_extension(
            _semantic_authority(content_authority_identity),
            candidate_identity=candidate.identity,
        )
        if mutate_extension:
            extension["payload"]["canonical_semantics"] += " "
        candidate.extensions.append(extension)

        validation = validate_bundle(bcrp)
        if validation.blocking:
            raise AssertionError(validation.findings)

        mapping = compatibility._mapping(legacy_candidate, bcrp, suffix=suffix)
        mapped = map_legacy_ready_to_bcrp(
            legacy_candidate=legacy_candidate,
            legacy_judgment=legacy_judgment,
            legacy_ready=legacy_ready,
            bcrp_candidate_bundle=bcrp,
            mapping=mapping,
        )
        authorization = release_helper._authorization(mapped, snapshot, suffix)
        release = produce_publication_release(
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
        declaration = semantic_fixture._paired_declaration()
        scope = planning._scope(release)
        plan_authorization = replace(
            planning._authorization(release, declaration, suffix),
            authorization_time="2026-08-02T10:00:00Z",
            planning_time="2026-08-02T10:01:00Z",
        )
        planned = produce_renderer_compatibility_plan(
            verified_release=release,
            evidence_snapshot=snapshot,
            lifecycle_scope=scope,
            declaration=declaration,
            authorization=plan_authorization,
        )
        self.assertFalse(planned.blocked, planned.findings)
        return release, snapshot, scope, declaration, plan_authorization, planned

    def test_real_unpatched_release_and_plan_verifiers_issue_and_consume_token(self):
        inputs = self._inputs()
        import briefforge_paired_terminal_profile.profile as profile

        with patch.object(
            profile, "verify_publication_release",
            wraps=profile.verify_publication_release,
        ) as release_verifier, patch.object(
            profile, "verify_renderer_compatibility_plan",
            wraps=profile.verify_renderer_compatibility_plan,
        ) as plan_verifier:
            release, snapshot, scope, declaration, authorization, planned = inputs
            token = verify_full_upstream_paired_terminal_admission(
                release_bundle=release.bundle,
                evidence_snapshot=snapshot,
                lifecycle_scope=scope,
                declaration=declaration,
                planning_authorization=authorization,
                plan_bundle=planned.plan.bundle,
            )

        self.assertEqual(release_verifier.call_count, 1)
        self.assertEqual(plan_verifier.call_count, 1)
        semantics, envelope = consume_paired_upstream_admission(token)
        self.assertEqual(len(semantics.table.rows), 7)
        authority_ids = tuple(item["id"] for item in release.bundle.one(
            "PortablePresentationMaterialRecord").semantic["authorities"])
        self.assertIn(semantics.content_authorities[0], authority_ids)
        projection = build_paired_editorial_projection(admitted=token)
        self.assertEqual(projection.release_identity, envelope.release_identity)

    def test_mutated_candidate_extension_is_rejected_before_token_issuance(self):
        import briefforge_paired_terminal_profile.profile as profile

        with patch.object(profile, "_issue_upstream_token",
                          wraps=profile._issue_upstream_token) as issuer:
            inputs = self._inputs(mutate_extension=True)
            with self.assertRaises(PairedProfileRejected):
                verify_full_upstream_paired_terminal_admission(
                    release_bundle=inputs[0].bundle,
                    evidence_snapshot=inputs[1], lifecycle_scope=inputs[2],
                    declaration=inputs[3], planning_authorization=inputs[4],
                    plan_bundle=inputs[5].plan.bundle,
                )
        self.assertEqual(issuer.call_count, 0)


if __name__ == "__main__":
    unittest.main()
