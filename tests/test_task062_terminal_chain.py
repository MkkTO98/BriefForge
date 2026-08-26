"""One synthetic end-to-end TASK-062 successor proof through unchanged TASK-056."""
from __future__ import annotations

from dataclasses import replace
import hashlib
import os
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from briefforge.bounded_loopback_deployment import (
    load_persisted_loopback_deployment,
    verify_deployment_current_availability,
    verify_persisted_deployment_stop,
)
from briefforge.publication_distribution_delivery import (
    ControlledLocalDeliveryAuthorization,
    ControlledLocalDestination,
    DeliveryInventoryItem,
    VerifiedControlledLocalDelivery,
    VerifiedControlledLocalDeliveryAuthorization,
    compute_delivery_authorization_fingerprint,
    compute_delivery_inventory_fingerprint,
    issue_controlled_local_delivery_authorization,
    perform_controlled_local_delivery,
    verify_controlled_local_delivery_current_eligibility,
    verify_persisted_controlled_local_delivery,
)
from briefforge.technical_publication_verification import (
    issue_technical_verification_authorization,
    load_persisted_technical_publication,
    verify_technical_publication_and_shutdown,
    verify_technical_publication_current_availability,
)
from briefforge_terminal_profile.controlled_invocation import (
    verify_persisted_terminal_renderer_invocation,
)
from briefforge_terminal_profile.manifest_admission import (
    produce_terminal_publication_manifest,
    verify_persisted_publication_manifest,
)
from briefforge_terminal_profile.semantic_conformance import (
    verify_persisted_terminal_semantic_artifact_conformance,
)
from briefforge_terminal_profile.profile import build_terminal_authority_profile
from briefforge_terminal_profile.projection import build_terminal_representative_projection
from tests import test_bounded_loopback_publication as task056
from tests import test_task062_manifest_dispatch as manifest_fixture
from tests import representative_fixture


_DELIVERY_EXCLUSIONS = (
    "network-distribution", "remote-receipt", "deployment-authority", "hosting-authority",
    "successful-publication-authority", "public-reachability", "browser-behavior-certification",
    "reader-access-certification", "accessibility-certification", "editorial-certification",
    "visual-certification", "factual-reassessment", "atlasforge-authority",
)


class Task062TerminalChainTests(unittest.TestCase):
    """Carry one immutable successor Release and byte string across every leaf."""

    invocation_authorization = manifest_fixture.Task062ManifestDispatchTests.invocation_authorization
    invoke = manifest_fixture.Task062ManifestDispatchTests.invoke
    conform_authorization = manifest_fixture.Task062ManifestDispatchTests.conform_authorization
    assess = manifest_fixture.Task062ManifestDispatchTests.assess
    _successor_predecessor = manifest_fixture.Task062ManifestDispatchTests._successor_predecessor
    _manifest_authorization = manifest_fixture.Task062ManifestDispatchTests._manifest_authorization
    _arguments = manifest_fixture.Task062ManifestDispatchTests._arguments

    _lifecycle_chain = task056.BoundedLoopbackPublicationTests._lifecycle_chain
    _deployment_chain = task056.BoundedLoopbackPublicationTests._deployment_chain
    _verification_chain = task056.BoundedLoopbackPublicationTests._verification_chain

    _start = task056.BoundedLoopbackPublicationTests._start

    def _deployment_auth(self, case, **changes):
        successor = dict(
            identity="deploy-auth:task062-terminal", attempt_identity="deploy-attempt:task062-terminal",
            evidence_identity="deploy-evidence:task062-terminal",
            authorization_time="2026-08-01T09:10:00Z", attempt_time="2026-08-01T09:11:00Z",
            completion_time="2026-08-01T09:12:00Z",
        )
        successor.update(changes)
        return task056.BoundedLoopbackPublicationTests._deployment_auth(self, case, **successor)

    def _verification_auth(self, deployment, **changes):
        successor = dict(
            identity="verify-auth:task062-terminal", attempt_identity="verify-attempt:task062-terminal",
            evidence_identity="verification-evidence:task062-terminal",
            authorization_time="2026-08-01T09:13:00Z", attempt_time="2026-08-01T09:14:00Z",
            completion_time="2026-08-01T09:15:00Z",
        )
        successor.update(changes)
        return task056.BoundedLoopbackPublicationTests._verification_auth(self, deployment, **successor)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.dp = self.root / "destination"; self.dl = self.root / "delivery"
        self.xl = self.root / "deployment"; self.vl = self.root / "verification"
        for directory in (self.dp, self.dl, self.xl, self.vl):
            directory.mkdir(); directory.chmod(0o700)
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]; probe.close()
        self.target = task056.DeploymentTarget(
            "127.0.0.1", port, f"http://127.0.0.1:{port}"
        )
        self.routes = (task056.DeploymentRouteItem("/brief.html", "brief.html", "text/html"),)
        self.profile = build_terminal_authority_profile(
            destination_parent=self.dp, destination_basename="brief.html",
            delivery_ledger=self.dl, target=self.target, routes=self.routes,
            deployment_ledger=self.xl, verification_ledger=self.vl,
            content_authorities=(dict(
                representative_fixture.CONTENT_AUTHORITY,
                role="presentation-content-authority",
                scope="released-presentation-semantic-content",
            ),),
        )
        original = representative_fixture.candidate_bundle
        def candidate(snapshot, *, complete_audience_edge=False):
            bundle = original(snapshot, complete_audience_edge=complete_audience_edge)
            bundle.one("PortablePresentationMaterialRecord").semantic["authorities"] = [
                dict(item) for item in self.profile.authorities
            ]
            return bundle
        with patch.object(representative_fixture, "candidate_bundle", candidate):
            self.inputs = representative_fixture.representative_chain(self, "task062-terminal-chain")
        self.projection = build_terminal_representative_projection(
            verified_release=self.inputs[1], evidence_snapshot=self.inputs[0],
            lifecycle_scope=self.inputs[2], declaration=self.inputs[3],
            planning_authorization=self.inputs[4], verified_plan=self.inputs[5],
            authority_profile=self.profile,
        )

    def _delivery_authorization(self, predecessor, manifest_auth, manifest):
        item = manifest_auth.artifact_inventory[0]
        inventory = (DeliveryInventoryItem(
            item.identity, item.role, item.logical_filename, item.media_type,
            item.byte_length, item.sha256, item.order,
        ),)
        destination_info = os.stat(self.dp, follow_symlinks=False)
        ledger_info = os.stat(self.dl, follow_symlinks=False)
        values = dict(
            identity="delivery-auth:task062-terminal",
            policy_identity="briefforge-controlled-local-delivery-policy:1.0.0",
            profile_identity="briefforge-controlled-local-directory-delivery-profile:1.0.0",
            profile_version="1.0.0",
            authority_identity="authority:briefforge-controlled-local-delivery",
            authority_owner="project:BriefForge",
            authority_role="controlled-local-delivery-authority",
            authorization_time="2026-08-01T09:07:00Z",
            attempt_time="2026-08-01T09:08:00Z",
            completion_time="2026-08-01T09:09:00Z",
            manifest_authorization_fingerprint=manifest_auth.fingerprint,
            manifest_fingerprint=manifest.fingerprint.digest,
            manifest_identity=manifest_auth.manifest_identity,
            manifest_record_identity=manifest_auth.record_identity,
            release_identity=manifest_auth.release_identity,
            release_fingerprint=manifest_auth.release_fingerprint,
            lifecycle_inventory_digest=self.inputs[2].inventory_digest,
            artifact_set_fingerprint=manifest_auth.artifact_set_fingerprint,
            delivery_inventory=inventory,
            delivery_inventory_fingerprint=compute_delivery_inventory_fingerprint(inventory),
            destination=ControlledLocalDestination(
                str(self.dp.resolve()), "brief.html",
                destination_info.st_dev, destination_info.st_ino,
            ),
            attempt_identity="delivery-attempt:task062-terminal",
            evidence_identity="delivery-evidence:task062-terminal",
            evidence_filename="controlled-local-delivery-evidence.json",
            implementation_identity="briefforge.publication_distribution_delivery",
            implementation_version="1.0.0",
            commitment_ledger_directory=str(self.dl.resolve()),
            commitment_ledger_device=ledger_info.st_dev,
            commitment_ledger_inode=ledger_info.st_ino,
            exclusions=_DELIVERY_EXCLUSIONS,
            released_authority_scope=self.profile.operational_authorities[5]["scope"],
        )
        provisional = ControlledLocalDeliveryAuthorization(**values, fingerprint="")
        return replace(
            provisional,
            fingerprint=compute_delivery_authorization_fingerprint(provisional),
        )

    def test_complete_successor_chain_preserves_release_and_artifact_and_shuts_down(self):
        predecessor = self._successor_predecessor()
        invocation_auth, invoked, conformance_auth, conformed = predecessor
        source_bytes = invoked.artifact_bytes
        source_sha = hashlib.sha256(source_bytes).hexdigest()
        release_fingerprint = self.inputs[1].fingerprint.digest

        # Independently reload the successor invocation and conformance evidence.
        loaded_invocation = verify_persisted_terminal_renderer_invocation(
            artifact_path=invoked.artifact_path, evidence_path=invoked.evidence_path,
            verified_release=self.inputs[1], evidence_snapshot=self.inputs[0],
            lifecycle_scope=self.inputs[2], declaration=self.inputs[3],
            planning_authorization=self.inputs[4], verified_plan=self.inputs[5],
            authority_profile=self.profile, authorization=invocation_auth,
        )
        loaded_conformance = verify_persisted_terminal_semantic_artifact_conformance(
            artifact_path=invoked.artifact_path,
            invocation_evidence_path=invoked.evidence_path,
            evidence_snapshot=self.inputs[0], verified_release=self.inputs[1],
            lifecycle_scope=self.inputs[2], declaration=self.inputs[3],
            planning_authorization=self.inputs[4], verified_plan=self.inputs[5],
            authority_profile=self.profile, invocation_authorization=invocation_auth,
            authorization=conformance_auth, projection=self.projection,
        )
        self.assertEqual(loaded_invocation.fingerprint, invoked.fingerprint)
        self.assertEqual(loaded_conformance.fingerprint, conformed.fingerprint)

        manifest_directory = self.root / "terminal-manifest"
        manifest_directory.mkdir()
        manifest_auth = self._manifest_authorization(predecessor, manifest_directory)
        manifest_arguments = self._arguments(predecessor, manifest_auth)
        produced = produce_terminal_publication_manifest(
            artifact_path=invoked.artifact_path, **manifest_arguments
        )
        self.assertFalse(produced.blocked, produced.findings)
        manifest_path = manifest_directory / manifest_auth.evidence_filename
        manifest = verify_persisted_publication_manifest(
            manifest_evidence_path=manifest_path, **manifest_arguments
        )

        upstream = dict(manifest_arguments)
        upstream["manifest_evidence_path"] = manifest_path
        upstream["manifest_authorization"] = upstream.pop("authorization")
        delivery_auth = self._delivery_authorization(predecessor, manifest_auth, manifest)
        delivery_marker = issue_controlled_local_delivery_authorization(
            **upstream, authorization=delivery_auth
        )
        self.assertIs(type(delivery_marker), VerifiedControlledLocalDeliveryAuthorization)
        delivered_result = perform_controlled_local_delivery(
            **upstream, authorization=delivery_marker
        )
        self.assertEqual(delivered_result.state, "completed")
        delivered = delivered_result.verified
        self.assertIs(type(delivered), VerifiedControlledLocalDelivery)
        delivered_path = self.dp / "brief.html" / "brief.html"
        self.assertEqual(delivered_path.read_bytes(), source_bytes)
        reloaded_delivery = verify_persisted_controlled_local_delivery(
            **upstream, authorization=delivery_marker
        )
        current_delivery = verify_controlled_local_delivery_current_eligibility(
            reloaded_delivery,
            **{k: v for k, v in upstream.items() if k not in {"authorization", "lifecycle_scope"}},
            historical_lifecycle_scope=self.inputs[2],
            current_lifecycle_scope=self.inputs[2],
        )
        self.assertEqual(current_delivery.state, "completed")

        case = (predecessor, upstream, delivery_marker, delivered)
        deployment_auth, deployment_marker, deployment = self._start(case)
        self.assertEqual(deployment.state, "active")
        deployment_chain = self._deployment_chain(case, deployment_marker, deployment)
        self.assertEqual(
            verify_deployment_current_availability(
                deployment.verified, **deployment_chain
            ).state,
            "current-availability-established",
        )
        loaded_deployment = load_persisted_loopback_deployment(
            authorization_evidence_path=self.xl / deployment_marker.issuance_filename,
            deployment_evidence_path=deployment.verified.evidence.evidence_path,
            delivery_arguments=upstream, delivery_authorization=delivery_marker,
            **self._lifecycle_chain(case),
        )
        self.assertEqual(loaded_deployment.fingerprint, deployment.verified.fingerprint)

        verification_chain = self._verification_chain(case, deployment, deployment_marker)
        verification_auth = self._verification_auth(deployment)
        chronology = (
            self.inputs[1].release.semantic["publication_time"], self.inputs[3].declaration_time,
            self.inputs[4].planning_time, invocation_auth.authorization_time,
            conformance_auth.authorization_time, manifest_auth.authorization_time,
            manifest_auth.manifest_time, delivery_auth.authorization_time, delivery_auth.attempt_time,
            delivery_auth.completion_time, deployment_auth.authorization_time,
            deployment_auth.attempt_time, deployment_auth.completion_time,
            verification_auth.authorization_time, verification_auth.attempt_time,
            verification_auth.completion_time,
        )
        self.assertEqual(chronology, tuple(sorted(chronology)))
        self.assertEqual(len(chronology), len(set(chronology)))
        verification_marker = issue_technical_verification_authorization(
            deployment=deployment.verified, authorization=verification_auth,
            **verification_chain,
        )
        coordinated = verify_technical_publication_and_shutdown(
            deployment_result=deployment, authorization=verification_marker,
            **verification_chain,
        )
        self.assertEqual(coordinated.verification.state, "bounded-observation-succeeded")
        self.assertEqual(coordinated.shutdown.state, "shutdown-verified")
        technical = coordinated.verification.verified
        observation = technical.evidence.observations[0]
        self.assertEqual(observation.body_sha256, source_sha)
        self.assertEqual(observation.body_length, len(source_bytes))

        loaded_technical = load_persisted_technical_publication(
            deployment_authorization_evidence_path=self.xl / deployment_marker.issuance_filename,
            deployment_evidence_path=deployment.verified.evidence.evidence_path,
            verification_authorization_evidence_path=self.vl / verification_marker.issuance_filename,
            verification_evidence_path=technical.evidence.evidence_path,
            delivery_arguments=upstream, delivery_authorization=delivery_marker,
            **self._lifecycle_chain(case),
        )
        self.assertEqual(loaded_technical.fingerprint, technical.fingerprint)
        self.assertEqual(
            verify_technical_publication_current_availability(
                loaded_technical, deployment=deployment.verified,
                authorization=verification_marker, **verification_chain,
            ).state,
            "not-established",
        )
        self.assertEqual(
            verify_persisted_deployment_stop(
                deployment=deployment.verified,
                **self._deployment_chain(case, deployment_marker),
            ).state,
            "shutdown-verified",
        )

        # Every leaf consumed the exact scope released by the terminal Release.
        self.assertEqual(delivery_auth.released_authority_scope,
                         self.profile.operational_authorities[5]["scope"])
        self.assertEqual(deployment_auth.released_authority_scope,
                         self.profile.operational_authorities[6]["scope"])
        self.assertEqual(verification_auth.released_authority_scope,
                         self.profile.operational_authorities[7]["scope"])

        # Release and bytes remain pinned in each successor leaf.
        self.assertEqual(manifest_auth.release_fingerprint, release_fingerprint)
        self.assertEqual(delivery_auth.release_fingerprint, release_fingerprint)
        self.assertEqual(delivered.evidence.release_fingerprint, release_fingerprint)
        self.assertEqual(deployment.verified.evidence.release_fingerprint, release_fingerprint)
        self.assertEqual(manifest_auth.artifact_inventory[0].sha256, source_sha)
        self.assertEqual(delivery_auth.delivery_inventory[0].sha256, source_sha)
        self.assertEqual(delivered.evidence.inventory[0].sha256, source_sha)
        self.assertEqual(delivered_path.read_bytes(), source_bytes)

        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.assertNotEqual(probe.connect_ex((self.target.address, self.target.port)), 0)
        finally:
            probe.close()


if __name__ == "__main__":
    unittest.main()
