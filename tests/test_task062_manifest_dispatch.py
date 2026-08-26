"""Focused TASK-062 successor Manifest admission and fixed-selector proof."""
from __future__ import annotations

from dataclasses import asdict, replace
from pathlib import Path
import unittest
from unittest.mock import patch

from briefforge.bcrp.canonical import fingerprint_bundle
from briefforge.bcrp.model import RECORD_KINDS
from briefforge.publication_manifest_admission import (
    ManifestArtifactAdmission,
    PublicationManifestAuthorization,
    compute_artifact_set_fingerprint,
    compute_manifest_authorization_fingerprint,
)
from briefforge_terminal_profile.manifest_admission import (
    MANIFEST_CONTRACT,
    MANIFEST_IMPLEMENTATION,
    MANIFEST_POLICY_ID,
    MANIFEST_PROFILE_ID,
    MANIFEST_VERSION,
    produce_terminal_publication_manifest,
    verify_persisted_publication_manifest,
    verify_persisted_terminal_publication_manifest,
)
from tests import test_task062_successor_invocation_conformance as successor_fixture


PROJECTOR_ID = "authority:briefforge-publication-manifest-projector"
PROJECTOR_OWNER = "project:BriefForge"
PROJECTOR_ROLE = "publication-manifest-projector"
MANIFEST_EXCLUSIONS = (
    "distribution-authority", "distribution-execution", "successful-publication-authority",
    "deployment-authority", "atlasforge-authority", "browser-behavior-certification",
    "accessibility-certification", "editorial-certification", "visual-certification",
    "factual-reassessment",
)


class Task062ManifestDispatchTests(unittest.TestCase):
    """Use the current synthetic terminal Release rather than a Manifest stub."""

    setUp = successor_fixture.Task062SuccessorInvocationConformanceTests.setUp
    invocation_authorization = successor_fixture.Task062SuccessorInvocationConformanceTests.invocation_authorization
    invoke = successor_fixture.Task062SuccessorInvocationConformanceTests.invoke
    conform_authorization = successor_fixture.Task062SuccessorInvocationConformanceTests.conform_authorization
    assess = successor_fixture.Task062SuccessorInvocationConformanceTests.assess

    def _successor_predecessor(self):
        invocation_authorization = self.invocation_authorization()
        invoked_result = self.invoke(invocation_authorization)
        self.assertFalse(invoked_result.blocked, invoked_result.findings)
        invoked = invoked_result.verified
        conformance_authorization = self.conform_authorization(
            invocation_authorization, invoked
        )
        conformance_result = self.assess(
            invocation_authorization, invoked, conformance_authorization
        )
        self.assertFalse(conformance_result.blocked, conformance_result.findings)
        self.assertEqual(len(conformance_result.verified.bundle.records), 10)
        return invocation_authorization, invoked, conformance_authorization, conformance_result.verified

    def _manifest_authorization(self, predecessor, manifest_directory: Path):
        invocation_authorization, invoked, conformance_authorization, conformed = predecessor
        audit_artifact = conformed.bundle.one("GeneratedArtifactAuditRecord").semantic["artifact"]
        admission = ManifestArtifactAdmission(
            identity=audit_artifact["id"],
            role="primary-semantic-publication",
            logical_filename=audit_artifact["filename"],
            media_type=audit_artifact["media_type"],
            byte_length=audit_artifact["byte_length"],
            sha256=audit_artifact["sha256"],
            order=0,
            source_path=str(Path(conformance_authorization.artifact_destination).resolve()),
            release_identity=self.inputs[1].release.identity,
            release_fingerprint=self.inputs[1].fingerprint.digest,
            plan_identity=self.inputs[5].plan.identity,
            plan_fingerprint=self.inputs[5].fingerprint.digest,
            renderer_identity=conformance_authorization.renderer_identity,
            renderer_version=conformance_authorization.renderer_version,
            invocation_authorization_identity=conformance_authorization.invocation_authorization_identity,
            invocation_evidence_fingerprint=conformance_authorization.invocation_evidence_fingerprint,
            conformance_authorization_identity=conformance_authorization.identity,
            conformance_evidence_fingerprint=conformed.fingerprint.digest,
            dependency_identities=(),
        )
        inventory = (admission,)
        values = dict(
            identity="terminal-manifest-authorization:task062",
            policy_identity=MANIFEST_POLICY_ID,
            profile_identity=MANIFEST_PROFILE_ID,
            profile_version=MANIFEST_VERSION,
            authority_identity=PROJECTOR_ID,
            authority_owner=PROJECTOR_OWNER,
            authority_role=PROJECTOR_ROLE,
            authorization_time="2026-08-01T09:05:00Z",
            release_identity=self.inputs[1].release.identity,
            release_fingerprint=self.inputs[1].fingerprint.digest,
            lifecycle_inventory_digest=self.inputs[2].inventory_digest,
            plan_identity=self.inputs[5].plan.identity,
            plan_fingerprint=self.inputs[5].fingerprint.digest,
            capability_identity=self.inputs[3].identity,
            capability_fingerprint=self.inputs[3].fingerprint,
            renderer_identity=conformance_authorization.renderer_identity,
            renderer_version=conformance_authorization.renderer_version,
            renderer_implementation_digest=conformance_authorization.renderer_implementation_digest,
            invocation_authorization_identity=invocation_authorization.identity,
            invocation_authorization_fingerprint=invocation_authorization.fingerprint,
            invocation_evidence_fingerprint=conformance_authorization.invocation_evidence_fingerprint,
            conformance_authorization_identity=conformance_authorization.identity,
            conformance_authorization_fingerprint=conformance_authorization.fingerprint,
            conformance_profile_identity=conformance_authorization.profile_identity,
            conformance_profile_version=conformance_authorization.profile_version,
            assessor_identity=conformance_authorization.authority_identity,
            conformance_evidence_fingerprint=conformed.fingerprint.digest,
            conformance_verdict="approved",
            predecessor_closure_fingerprint=fingerprint_bundle(
                conformed.bundle, domain="profile-instance", require_valid=False
            ).digest,
            artifact_inventory=inventory,
            artifact_set_fingerprint=compute_artifact_set_fingerprint(inventory),
            manifest_identity="manifest:task062-terminal",
            manifest_version=MANIFEST_VERSION,
            manifest_time="2026-08-01T09:06:00Z",
            projector_implementation=MANIFEST_IMPLEMENTATION,
            projector_version=MANIFEST_VERSION,
            evidence_directory=str(manifest_directory.resolve()),
            evidence_filename="publication-manifest.json",
            commitment_ledger_directory=str((manifest_directory.parent / "manifest-ledger").resolve()),
            record_identity="publication-manifest-record:task062-terminal",
            exclusions=MANIFEST_EXCLUSIONS,
        )
        provisional = PublicationManifestAuthorization(**values, fingerprint="")
        return replace(
            provisional,
            fingerprint=compute_manifest_authorization_fingerprint(provisional),
        )

    def _arguments(self, predecessor, authorization):
        invocation_authorization, invoked, conformance_authorization, _ = predecessor
        return dict(
            evidence_snapshot=self.inputs[0],
            verified_release=self.inputs[1],
            lifecycle_scope=self.inputs[2],
            declaration=self.inputs[3],
            planning_authorization=self.inputs[4],
            verified_plan=self.inputs[5],
            invocation_authorization=invocation_authorization,
            conformance_authorization=conformance_authorization,
            artifact_paths=(invoked.artifact_path,),
            authorization=authorization,
        )

    def test_successor_manifest_has_exact_immutable_eleven_kind_atomic_closure_and_reloads(self):
        predecessor = self._successor_predecessor()
        manifest_directory = self.root / "manifest"
        manifest_directory.mkdir()
        authorization = self._manifest_authorization(predecessor, manifest_directory)
        predecessor_documents = tuple(
            record.to_document() for record in predecessor[3].bundle.records
        )
        frozen_authorities = tuple(asdict(value) for value in (
            predecessor[0], predecessor[2], authorization
        ))
        arguments = self._arguments(predecessor, authorization)

        result = produce_terminal_publication_manifest(
            artifact_path=predecessor[1].artifact_path, **arguments
        )
        self.assertFalse(result.blocked, result.findings)
        bundle = result.verified.bundle
        self.assertEqual(tuple(record.kind for record in bundle.records), RECORD_KINDS)
        self.assertEqual(len(bundle.records), 11)
        self.assertEqual(
            tuple(record.to_document() for record in bundle.records[:10]),
            predecessor_documents,
        )

        record = bundle.one("PublicationManifestRecord")
        extension = record.extensions[0]
        self.assertEqual(extension["validation_contract"], MANIFEST_CONTRACT)
        payload = extension["payload"]
        expected_atomic = {
            "successor_profile_identity": self.profile.profile_identity,
            "successor_profile_version": self.profile.profile_version,
            "successor_projection_fingerprint": predecessor[2].successor_projection_fingerprint,
            "translated_projection_fingerprint": predecessor[2].translated_projection_fingerprint,
            "adapter_identity": predecessor[2].adapter_identity,
            "adapter_version": predecessor[2].adapter_version,
            "adapter_implementation_digest": predecessor[2].adapter_implementation_digest,
            "renderer_identity": predecessor[2].renderer_identity,
            "renderer_version": predecessor[2].renderer_version,
            "renderer_implementation_digest": predecessor[2].renderer_implementation_digest,
            "invocation_authorization_identity": predecessor[2].invocation_authorization_identity,
            "invocation_authorization_fingerprint": predecessor[2].invocation_authorization_fingerprint,
            "invocation_evidence_fingerprint": predecessor[2].invocation_evidence_fingerprint,
            "conformance_authorization_identity": predecessor[2].identity,
            "conformance_authorization_fingerprint": predecessor[2].fingerprint,
            "conformance_evidence_fingerprint": predecessor[3].fingerprint.digest,
        }
        self.assertEqual(payload["atomic_successor_tuple"], expected_atomic)
        self.assertEqual(payload["distribution_authority"], "absent")
        self.assertEqual(payload["distribution_execution"], "not-performed")
        self.assertEqual(payload["deployment_authority"], "absent")
        self.assertEqual(payload["successful_publication"], "not-asserted")
        self.assertIn("distribution-authority", payload["authority_exclusions"])
        self.assertIn("deployment-authority", payload["authority_exclusions"])

        evidence_path = manifest_directory / authorization.evidence_filename
        direct = verify_persisted_terminal_publication_manifest(
            manifest_evidence_path=evidence_path, **arguments
        )
        selected = verify_persisted_publication_manifest(
            manifest_evidence_path=evidence_path, **arguments
        )
        self.assertEqual(direct.fingerprint, result.verified.fingerprint)
        self.assertEqual(selected.fingerprint, result.verified.fingerprint)
        self.assertEqual(
            tuple(record.to_document() for record in selected.bundle.records[:10]),
            predecessor_documents,
        )
        self.assertEqual(
            tuple(asdict(value) for value in (predecessor[0], predecessor[2], authorization)),
            frozen_authorities,
        )

    def test_selector_is_fixed_for_successor_and_rejects_mixed_tuples(self):
        predecessor = self._successor_predecessor()
        manifest_directory = self.root / "manifest-selector"
        manifest_directory.mkdir()
        authorization = self._manifest_authorization(predecessor, manifest_directory)
        arguments = self._arguments(predecessor, authorization)
        produced = produce_terminal_publication_manifest(
            artifact_path=predecessor[1].artifact_path, **arguments
        )
        self.assertFalse(produced.blocked, produced.findings)
        evidence_path = manifest_directory / authorization.evidence_filename

        sentinel = object()
        with patch(
            "briefforge_terminal_profile.manifest_admission.verify_persisted_terminal_publication_manifest",
            return_value=sentinel,
        ) as successor, patch(
            "briefforge_terminal_profile.manifest_admission.historical.verify_persisted_publication_manifest",
            side_effect=AssertionError("historical verifier must not receive successor tuple"),
        ) as historical:
            selected = verify_persisted_publication_manifest(
                manifest_evidence_path=evidence_path, **arguments
            )
        self.assertIs(selected, sentinel)
        successor.assert_called_once()
        historical.assert_not_called()

        for mixed in (
            {**arguments, "invocation_authorization": object()},
            {**arguments, "conformance_authorization": object()},
        ):
            with self.subTest(mixed=type(mixed["invocation_authorization"]).__name__), \
                    self.assertRaisesRegex(ValueError, "mixed or unknown tuple"):
                verify_persisted_publication_manifest(
                    manifest_evidence_path=evidence_path, **mixed
                )

        from briefforge.publication_distribution_delivery import (
            verify_persisted_publication_manifest as delivery_selector,
        )
        delivered = delivery_selector(manifest_evidence_path=evidence_path, **arguments)
        self.assertEqual(delivered.fingerprint, produced.verified.fingerprint)

    def test_successor_authorization_chronology_identity_and_artifact_paths_fail_closed_on_produce_and_reload(self):
        predecessor = self._successor_predecessor()
        manifest_directory = self.root / "manifest-adversarial"
        manifest_directory.mkdir()
        authorization = self._manifest_authorization(predecessor, manifest_directory)
        arguments = self._arguments(predecessor, authorization)

        def signed(**changes):
            changed = replace(authorization, **changes, fingerprint="")
            return replace(changed, fingerprint=compute_manifest_authorization_fingerprint(changed))

        attacks = (
            signed(identity=" terminal-manifest-authorization:task062"),
            signed(authorization_time="not-a-time"),
            signed(authorization_time="2026-08-01T09:03:59Z"),
            signed(manifest_time="2026-08-01T09:04:59Z"),
            signed(manifest_identity=authorization.identity),
            signed(record_identity=predecessor[3].bundle.records[0].identity),
        )
        for changed in attacks:
            with self.subTest(field=changed), patch(
                "briefforge_terminal_profile.manifest_admission.historical._reserve_authorization"
            ) as reserve:
                result = produce_terminal_publication_manifest(
                    artifact_path=predecessor[1].artifact_path,
                    **{**arguments, "authorization": changed},
                )
                self.assertTrue(result.blocked)
                reserve.assert_not_called()

        invalid_path_values = ((), [], None, (predecessor[1].artifact_path, predecessor[1].artifact_path))
        for invalid_paths in invalid_path_values:
            with self.subTest(paths=invalid_paths):
                result = produce_terminal_publication_manifest(
                    artifact_path=predecessor[1].artifact_path,
                    **{**arguments, "artifact_paths": invalid_paths},
                )
                self.assertTrue(result.blocked)

        produced = produce_terminal_publication_manifest(
            artifact_path=predecessor[1].artifact_path, **arguments
        )
        self.assertFalse(produced.blocked, produced.findings)
        evidence_path = manifest_directory / authorization.evidence_filename
        for changed in attacks:
            with self.subTest(reload=changed), self.assertRaises(ValueError):
                verify_persisted_terminal_publication_manifest(
                    manifest_evidence_path=evidence_path,
                    **{**arguments, "authorization": changed},
                )
        for invalid_paths in invalid_path_values:
            with self.subTest(reload_paths=invalid_paths), self.assertRaises(ValueError):
                verify_persisted_terminal_publication_manifest(
                    manifest_evidence_path=evidence_path,
                    **{**arguments, "artifact_paths": invalid_paths},
                )


if __name__ == "__main__":
    unittest.main()
