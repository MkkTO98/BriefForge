"""TASK-060 acceptance RED tests for the complete v2 authority chain.

The representative profile must preserve the transactional and BCRP evidence
properties proved by TASK-052/053, rather than merely writing two loose files.
"""
from __future__ import annotations

from dataclasses import fields, replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from briefforge.representative_controlled_invocation import (
    RepresentativeRendererInvocationAuthorization,
    compute_representative_invocation_authorization_fingerprint,
    invoke_controlled_representative_renderer,
    representative_renderer_implementation_digest,
    verify_persisted_representative_renderer_invocation,
)
from briefforge.representative_projection import build_representative_projection
from briefforge.representative_semantic_conformance import (
    RepresentativeSemanticArtifactConformanceAuthorization,
    assess_representative_semantic_artifact_conformance,
    compute_representative_conformance_authorization_fingerprint,
    representative_assessor_implementation_digest,
    verify_persisted_representative_semantic_artifact_conformance,
)
from briefforge.bcrp.canonical import fingerprint_bundle
from briefforge.publication_manifest_admission import (
    ManifestArtifactAdmission,
    PublicationManifestAuthorization,
    compute_artifact_set_fingerprint,
    compute_manifest_authorization_fingerprint,
    produce_publication_manifest,
    verify_persisted_publication_manifest,
)
from tests.representative_fixture import representative_chain


MANIFEST_EXCLUSIONS = (
    "distribution-authority", "distribution-execution", "successful-publication-authority",
    "deployment-authority", "atlasforge-authority", "browser-behavior-certification",
    "accessibility-certification", "editorial-certification", "visual-certification",
    "factual-reassessment",
)


EXPECTED_INVOCATION_AUTHORIZATION_FIELDS = {
    "identity", "policy_identity", "authority_identity", "authority_owner", "authority_role",
    "authorization_time", "release_identity", "release_fingerprint",
    "lifecycle_inventory_digest", "plan_identity", "plan_fingerprint",
    "capability_identity", "capability_fingerprint", "renderer_identity",
    "renderer_adapter_id", "renderer_version", "renderer_implementation_digest",
    "projection_fingerprint", "authorization_ledger_directory", "output_directory",
    "output_filename", "output_count", "maximum_output_bytes", "media_type", "environment",
    "external_assets", "invocation_mode", "timeout_seconds", "evidence_filename", "fingerprint",
}
EXPECTED_CONFORMANCE_AUTHORIZATION_FIELDS = {
    "identity", "policy_identity", "authority_identity", "authority_owner", "authority_role",
    "authorization_time", "profile_identity", "profile_version", "assessor_identity",
    "release_identity", "release_fingerprint", "lifecycle_inventory_digest", "plan_identity",
    "plan_fingerprint", "capability_identity", "capability_fingerprint",
    "invocation_authorization_identity", "invocation_authorization_fingerprint",
    "invocation_evidence_fingerprint", "artifact_identity", "artifact_sha256",
    "artifact_filename", "artifact_media_type", "artifact_byte_length", "projection_fingerprint",
    "renderer_identity", "renderer_version", "renderer_implementation_digest",
    "assessor_implementation", "assessor_version", "assessor_implementation_digest",
    "output_class", "maximum_artifact_bytes",
    "exclusions", "artifact_destination", "invocation_evidence_destination",
    "evidence_directory", "evidence_filename", "commitment_ledger_directory",
    "record_identity", "fingerprint",
}


class RepresentativeAuthorityChainTests(unittest.TestCase):
    def _inputs(self):
        return representative_chain(self, "task060-chain")

    def _projection(self, inputs):
        return build_representative_projection(
            verified_release=inputs[1], evidence_snapshot=inputs[0], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
        )

    def _current_invocation_authorization(self, inputs, output: Path, evidence: Path, **changes):
        projection = self._projection(inputs)
        self.assertEqual(output.parent, evidence.parent)
        ledger = output.parent / "authorization-ledger"
        ledger.mkdir(exist_ok=True)
        values = dict(
            identity="renderer-invocation-authorization:task060-chain",
            policy_identity="briefforge-controlled-renderer-invocation-policy:1.0.0",
            authority_identity="authority:briefforge-controlled-renderer-invocation",
            authority_owner="project:BriefForge",
            authority_role="renderer-invocation-authority",
            authorization_time="2026-08-01T09:03:00Z",
            release_identity=inputs[1].release.identity,
            release_fingerprint=inputs[1].fingerprint.digest,
            lifecycle_inventory_digest=inputs[2].inventory_digest,
            plan_identity=inputs[5].plan.identity,
            plan_fingerprint=inputs[5].fingerprint.digest,
            capability_identity=inputs[3].identity,
            capability_fingerprint=inputs[3].fingerprint,
            renderer_identity="renderer:representative-static-html",
            renderer_adapter_id="representative-static-html-renderer",
            renderer_version="1.0.0",
            renderer_implementation_digest=representative_renderer_implementation_digest(),
            projection_fingerprint=projection.fingerprint,
            authorization_ledger_directory=str(ledger.resolve()),
            output_directory=str(output.parent.resolve()),
            output_filename=f"{output.name}/brief.html",
            output_count=1,
            maximum_output_bytes=1_000_000,
            media_type="text/html",
            environment=(
                ("LANG", "C"), ("LC_ALL", "C"), ("TZ", "UTC"),
                ("PYTHONDONTWRITEBYTECODE", "1"), ("PYTHONHASHSEED", "0"),
                ("PYTHONUTF8", "1"),
            ),
            external_assets=(),
            invocation_mode="one-artifact-with-determinism-replay",
            timeout_seconds=2,
            evidence_filename=f"{evidence.name}/representative-invocation-evidence.json",
        )
        values.update(changes)
        provisional = RepresentativeRendererInvocationAuthorization(**values, fingerprint="")
        return replace(
            provisional,
            fingerprint=compute_representative_invocation_authorization_fingerprint(provisional),
        )

    def _invoke(self, inputs, authorization):
        return invoke_controlled_representative_renderer(
            verified_release=inputs[1], evidence_snapshot=inputs[0], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
            authorization=authorization,
        )

    def test_authorization_contracts_are_complete_one_act_authority_bindings(self):
        self.assertEqual(
            {field.name for field in fields(RepresentativeRendererInvocationAuthorization)},
            EXPECTED_INVOCATION_AUTHORIZATION_FIELDS,
        )
        self.assertEqual(
            {field.name for field in fields(RepresentativeSemanticArtifactConformanceAuthorization)},
            EXPECTED_CONFORMANCE_AUTHORIZATION_FIELDS,
        )

    def test_successful_invocation_is_verified_nine_record_bcrp_and_replay_is_permanently_rejected(self):
        inputs = self._inputs()
        with tempfile.TemporaryDirectory() as root_name:
            root = Path(root_name); output = root / "artifact"; evidence = root / "evidence"
            output.mkdir(); evidence.mkdir()
            authorization = self._current_invocation_authorization(inputs, output, evidence)
            result = self._invoke(inputs, authorization)
            self.assertFalse(result.blocked, result.findings)
            self.assertEqual(len(result.verified.bundle.records), 9)
            self.assertEqual(len(result.verified.bundle.records_of_kind("GeneratedArtifactAuditRecord")), 1)
            self.assertFalse(result.verified.bundle.records_of_kind("SemanticArtifactConformanceRecord"))
            audit = result.verified.bundle.one("GeneratedArtifactAuditRecord")
            self.assertEqual(audit.extensions[0]["payload"]["semantic_conformance"], "unassessed")
            verify_persisted_representative_renderer_invocation(
                artifact_path=output / "brief.html",
                evidence_path=evidence / "representative-invocation-evidence.json",
                verified_release=inputs[1], evidence_snapshot=inputs[0], lifecycle_scope=inputs[2],
                declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
                authorization=authorization,
            )
            (output / "brief.html").unlink()
            (evidence / "representative-invocation-evidence.json").unlink()
            replay = self._invoke(inputs, authorization)
            self.assertTrue(replay.blocked)
            self.assertIsNone(replay.verified)
            self.assertIn("authorization", " ".join(map(str, replay.findings)).lower())
            self.assertEqual(tuple(output.iterdir()), ())
            self.assertEqual(tuple(evidence.iterdir()), ())

    def test_invocation_authorization_remains_consumed_after_outputs_are_deleted(self):
        inputs = self._inputs()
        with tempfile.TemporaryDirectory() as root_name:
            root = Path(root_name); output = root / "artifact"; evidence = root / "evidence"
            output.mkdir(); evidence.mkdir()
            authorization = self._current_invocation_authorization(inputs, output, evidence)
            first = self._invoke(inputs, authorization)
            self.assertFalse(first.blocked, first.findings)
            (output / "brief.html").unlink()
            (evidence / "representative-invocation-evidence.json").unlink()
            replay = self._invoke(inputs, authorization)
            self.assertTrue(replay.blocked)
            self.assertIsNone(replay.verified)
            self.assertEqual(tuple(output.iterdir()), ())
            self.assertEqual(tuple(evidence.iterdir()), ())

    def test_invocation_failure_emits_no_record_and_artifact_evidence_tampering_is_rejected(self):
        inputs = self._inputs()
        with tempfile.TemporaryDirectory() as root_name:
            root = Path(root_name); output = root / "artifact"; evidence = root / "evidence"
            output.mkdir(); evidence.mkdir()
            invalid = self._current_invocation_authorization(
                inputs, output, evidence, projection_fingerprint="0" * 64)
            failed = self._invoke(inputs, invalid)
            self.assertTrue(failed.blocked)
            self.assertIsNone(failed.verified)
            self.assertEqual(tuple(output.iterdir()), ())
            self.assertEqual(tuple(evidence.iterdir()), ())

        for target in ("artifact", "evidence"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as root_name:
                root = Path(root_name); output = root / "artifact"; evidence = root / "evidence"
                output.mkdir(); evidence.mkdir()
                authorization = self._current_invocation_authorization(inputs, output, evidence)
                self.assertFalse(self._invoke(inputs, authorization).blocked)
                artifact_path = output / "brief.html"
                evidence_path = evidence / "representative-invocation-evidence.json"
                path = artifact_path if target == "artifact" else evidence_path
                path.write_bytes(path.read_bytes() + b"x")
                with self.assertRaises(Exception):
                    verify_persisted_representative_renderer_invocation(
                        artifact_path=artifact_path, evidence_path=evidence_path,
                        verified_release=inputs[1], evidence_snapshot=inputs[0],
                        lifecycle_scope=inputs[2], declaration=inputs[3],
                        planning_authorization=inputs[4], verified_plan=inputs[5],
                        authorization=authorization,
                    )

    def test_coordinated_artifact_evidence_pair_rewrite_cannot_forge_replay(self):
        inputs = self._inputs()
        with tempfile.TemporaryDirectory() as root_name:
            root = Path(root_name); output = root / "artifact"; evidence = root / "evidence"
            output.mkdir(); evidence.mkdir()
            authorization = self._current_invocation_authorization(inputs, output, evidence)
            self.assertFalse(self._invoke(inputs, authorization).blocked)
            artifact_path = output / "brief.html"
            evidence_path = evidence / "representative-invocation-evidence.json"
            forged = artifact_path.read_bytes().replace(b"Representative root", b"Forged root", 1)
            artifact_path.write_bytes(forged)
            document = json.loads(evidence_path.read_text(encoding="utf-8"))
            digest = hashlib.sha256(forged).hexdigest()
            document["artifact_sha256"] = digest
            document["artifact_byte_length"] = len(forged)
            document["execution_sha256"] = [digest, digest]
            evidence_path.write_text(
                json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                encoding="utf-8",
            )
            with self.assertRaises(Exception):
                verify_persisted_representative_renderer_invocation(
                    artifact_path=artifact_path, evidence_path=evidence_path,
                    verified_release=inputs[1], evidence_snapshot=inputs[0],
                    lifecycle_scope=inputs[2], declaration=inputs[3],
                    planning_authorization=inputs[4], verified_plan=inputs[5],
                    authorization=authorization,
                )

    def _current_conformance_authorization(self, inputs, projection, invocation_authorization,
                                           invoked, directory: Path, **changes):
        artifact = invoked.artifact_path.read_bytes()
        audit_artifact = invoked.bundle.one("GeneratedArtifactAuditRecord").semantic["artifact"]
        values = dict(
            identity="semantic-conformance-authorization:task060-chain",
            policy_identity="briefforge-semantic-conformance-assessment-policy:1.0.0",
            authority_identity="authority:briefforge-semantic-artifact-conformance",
            authority_owner="project:BriefForge",
            authority_role="semantic-artifact-conformance-assessor",
            authorization_time="2026-08-01T09:04:00Z",
            profile_identity="briefforge-static-html-semantic-realization-profile:2.0.0",
            profile_version="2.0.0",
            assessor_identity="authority:briefforge-semantic-artifact-conformance",
            release_identity=inputs[1].release.identity,
            release_fingerprint=inputs[1].fingerprint.digest,
            lifecycle_inventory_digest=inputs[2].inventory_digest,
            plan_identity=inputs[5].plan.identity,
            plan_fingerprint=inputs[5].fingerprint.digest,
            capability_identity=inputs[3].identity,
            capability_fingerprint=inputs[3].fingerprint,
            invocation_authorization_identity=invocation_authorization.identity,
            invocation_authorization_fingerprint=invocation_authorization.fingerprint,
            invocation_evidence_fingerprint=invoked.fingerprint.digest,
            artifact_identity=audit_artifact["id"],
            artifact_sha256=hashlib.sha256(artifact).hexdigest(),
            artifact_filename=audit_artifact["filename"],
            artifact_media_type=audit_artifact["media_type"],
            artifact_byte_length=len(artifact),
            projection_fingerprint=projection.fingerprint,
            renderer_identity=invocation_authorization.renderer_identity,
            renderer_version=invocation_authorization.renderer_version,
            renderer_implementation_digest=invocation_authorization.renderer_implementation_digest,
            assessor_implementation="briefforge.representative_semantic_artifact_conformance",
            assessor_version="2.0.0",
            assessor_implementation_digest=representative_assessor_implementation_digest(),
            output_class="standalone-representative-static-html-semantic-realization",
            maximum_artifact_bytes=invocation_authorization.maximum_output_bytes,
            exclusions=("manifest-authority", "distribution-authority",
                        "successful-publication-authority", "external-assets", "active-content"),
            artifact_destination=str(invoked.artifact_path),
            invocation_evidence_destination=str(invoked.evidence_path),
            evidence_directory=str(directory.resolve()),
            evidence_filename="semantic-conformance-evidence.json",
            commitment_ledger_directory=invocation_authorization.authorization_ledger_directory,
            record_identity="semantic-conformance:task060-chain",
        )
        values.update(changes)
        provisional = RepresentativeSemanticArtifactConformanceAuthorization(**values, fingerprint="")
        return replace(
            provisional,
            fingerprint=compute_representative_conformance_authorization_fingerprint(provisional),
        )

    def _real_v2_conformance(self, root: Path):
        inputs = self._inputs()
        output = root / "artifact"; invocation_dir = root / "invoke"
        conformance_dir = root / "conform"
        output.mkdir(); invocation_dir.mkdir(); conformance_dir.mkdir()
        invocation_auth = self._current_invocation_authorization(inputs, output, invocation_dir)
        invoked_result = self._invoke(inputs, invocation_auth)
        self.assertFalse(invoked_result.blocked, invoked_result.findings)
        invoked = invoked_result.verified
        projection = self._projection(inputs)
        conformance_auth = self._current_conformance_authorization(
            inputs, projection, invocation_auth, invoked, conformance_dir)
        conformance_result = assess_representative_semantic_artifact_conformance(
            artifact_path=invoked.artifact_path, projection=projection,
            invocation_evidence_path=invoked.evidence_path,
            evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
            invocation_authorization=invocation_auth,
            invocation_evidence_fingerprint=invoked.fingerprint.digest,
            authorization=conformance_auth,
        )
        self.assertFalse(conformance_result.blocked, conformance_result.findings)
        return inputs, projection, invocation_auth, invoked, conformance_auth, conformance_result.verified

    def _manifest_authorization(self, case, manifest_dir: Path, **changes):
        inputs, _, invocation_auth, invoked, conformance_auth, conformed = case
        artifact = invoked.artifact_path.read_bytes()
        audit_artifact = conformed.bundle.one("GeneratedArtifactAuditRecord").semantic["artifact"]
        admission = ManifestArtifactAdmission(
            identity=audit_artifact["id"], role="primary-semantic-publication",
            logical_filename=audit_artifact["filename"], media_type=audit_artifact["media_type"],
            byte_length=len(artifact), sha256=hashlib.sha256(artifact).hexdigest(), order=0,
            source_path=str(invoked.artifact_path.resolve()),
            release_identity=inputs[1].release.identity,
            release_fingerprint=inputs[1].fingerprint.digest,
            plan_identity=inputs[5].plan.identity, plan_fingerprint=inputs[5].fingerprint.digest,
            renderer_identity=invocation_auth.renderer_identity,
            renderer_version=invocation_auth.renderer_version,
            invocation_authorization_identity=invocation_auth.identity,
            invocation_evidence_fingerprint=invoked.fingerprint.digest,
            conformance_authorization_identity=conformance_auth.identity,
            conformance_evidence_fingerprint=conformed.fingerprint.digest,
            dependency_identities=(),
        )
        values = dict(
            identity="manifest-authorization:task060-v2",
            policy_identity="briefforge-publication-manifest-admission-policy:1.0.0",
            profile_identity="briefforge-publication-manifest-admission-profile:1.0.0",
            profile_version="1.0.0",
            authority_identity="authority:briefforge-publication-manifest-projector",
            authority_owner="project:BriefForge", authority_role="publication-manifest-projector",
            authorization_time="2026-08-01T09:05:00Z",
            release_identity=inputs[1].release.identity,
            release_fingerprint=inputs[1].fingerprint.digest,
            lifecycle_inventory_digest=inputs[2].inventory_digest,
            plan_identity=inputs[5].plan.identity, plan_fingerprint=inputs[5].fingerprint.digest,
            capability_identity=inputs[3].identity, capability_fingerprint=inputs[3].fingerprint,
            renderer_identity=invocation_auth.renderer_identity,
            renderer_version=invocation_auth.renderer_version,
            renderer_implementation_digest=invocation_auth.renderer_implementation_digest,
            invocation_authorization_identity=invocation_auth.identity,
            invocation_authorization_fingerprint=invocation_auth.fingerprint,
            invocation_evidence_fingerprint=invoked.fingerprint.digest,
            conformance_authorization_identity=conformance_auth.identity,
            conformance_authorization_fingerprint=conformance_auth.fingerprint,
            conformance_profile_identity=conformance_auth.profile_identity,
            conformance_profile_version=conformance_auth.profile_version,
            assessor_identity=conformance_auth.assessor_identity,
            conformance_evidence_fingerprint=conformed.fingerprint.digest,
            conformance_verdict="approved",
            predecessor_closure_fingerprint=fingerprint_bundle(
                conformed.bundle, domain="profile-instance", require_valid=False).digest,
            artifact_inventory=(admission,),
            artifact_set_fingerprint=compute_artifact_set_fingerprint((admission,)),
            manifest_identity="manifest:task060-v2", manifest_version="1.0.0",
            manifest_time="2026-08-01T09:06:00Z",
            projector_implementation="briefforge.publication_manifest_admission",
            projector_version="1.0.0", evidence_directory=str(manifest_dir.resolve()),
            evidence_filename="publication-manifest.json",
            commitment_ledger_directory=str((manifest_dir.parent / "manifest-ledger").resolve()),
            record_identity="publication-manifest-record:task060-v2",
            exclusions=MANIFEST_EXCLUSIONS,
        )
        values.update(changes)
        provisional = PublicationManifestAuthorization(**values, fingerprint="")
        return replace(provisional,
                       fingerprint=compute_manifest_authorization_fingerprint(provisional))

    @staticmethod
    def _manifest_arguments(case, authorization):
        inputs, _, invocation_auth, invoked, conformance_auth, _ = case
        return dict(
            evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
            invocation_authorization=invocation_auth, artifact_path=invoked.artifact_path,
            invocation_evidence_path=invoked.evidence_path,
            conformance_authorization=conformance_auth,
            conformance_evidence_path=(Path(conformance_auth.evidence_directory) /
                                       conformance_auth.evidence_filename),
            authorization=authorization,
        )

    def test_v2_conformance_produces_exact_manifest_closure_and_persisted_reload(self):
        with tempfile.TemporaryDirectory() as root_name:
            root = Path(root_name)
            case = self._real_v2_conformance(root)
            manifest_dir = root / "manifest"; manifest_dir.mkdir()
            authorization = self._manifest_authorization(case, manifest_dir)
            result = produce_publication_manifest(**self._manifest_arguments(case, authorization))
            self.assertFalse(result.blocked, result.findings)
            self.assertEqual(len(result.verified.bundle.records), 11)
            self.assertEqual(len(result.verified.bundle.records_of_kind("PublicationManifestRecord")), 1)
            args = self._manifest_arguments(case, authorization)
            reloaded = verify_persisted_publication_manifest(
                manifest_evidence_path=manifest_dir / authorization.evidence_filename,
                evidence_snapshot=args["evidence_snapshot"], verified_release=args["verified_release"],
                lifecycle_scope=args["lifecycle_scope"], declaration=args["declaration"],
                planning_authorization=args["planning_authorization"], verified_plan=args["verified_plan"],
                invocation_authorization=args["invocation_authorization"],
                conformance_authorization=args["conformance_authorization"],
                artifact_paths=(case[3].artifact_path,), authorization=authorization,
            )
            self.assertEqual(reloaded.fingerprint, result.verified.fingerprint)

    def test_manifest_rejects_mixed_unknown_profile_tuple_and_wrong_representative_renderer(self):
        attacks = (
            {"profile_identity": "briefforge-static-html-semantic-realization-profile",
             "profile_version": "1.0.0"},
            {"profile_identity": "briefforge-static-html-semantic-realization-profile:99.0.0",
             "profile_version": "99.0.0"},
            {"renderer_identity": "renderer:minimal-html", "renderer_version": "0.2.0"},
        )
        for index, changes in enumerate(attacks):
            with self.subTest(changes=changes), tempfile.TemporaryDirectory() as root_name:
                root = Path(root_name)
                case = self._real_v2_conformance(root)
                manifest_dir = root / "manifest"; manifest_dir.mkdir()
                changed_conformance = replace(case[4], **changes, fingerprint="")
                changed_conformance = replace(
                    changed_conformance,
                    fingerprint=compute_representative_conformance_authorization_fingerprint(
                        changed_conformance),
                )
                attacked_case = (*case[:4], changed_conformance, case[5])
                authorization = self._manifest_authorization(
                    attacked_case, manifest_dir,
                    identity=f"manifest-authorization:task060-attack-{index}",
                    record_identity=f"publication-manifest-record:task060-attack-{index}",
                    manifest_identity=f"manifest:task060-attack-{index}",
                )
                result = produce_publication_manifest(
                    **self._manifest_arguments(attacked_case, authorization))
                self.assertTrue(result.blocked)
                self.assertIsNone(result.verified)
                self.assertFalse((manifest_dir / authorization.evidence_filename).exists())

    def test_successful_conformance_is_verified_ten_record_bcrp_and_reloads(self):
        inputs = self._inputs()
        with tempfile.TemporaryDirectory() as root_name:
            root = Path(root_name); output = root / "artifact"; invocation_evidence = root / "invoke"
            conformance_evidence = root / "conform"
            output.mkdir(); invocation_evidence.mkdir(); conformance_evidence.mkdir()
            invocation_auth = self._current_invocation_authorization(inputs, output, invocation_evidence)
            invoked = self._invoke(inputs, invocation_auth).verified
            self.assertIsNotNone(invoked)
            projection = self._projection(inputs)
            authorization = self._current_conformance_authorization(
                inputs, projection, invocation_auth, invoked, conformance_evidence)
            result = assess_representative_semantic_artifact_conformance(
                artifact_path=invoked.artifact_path, projection=projection,
                invocation_evidence_path=invoked.evidence_path,
                evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2],
                declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
                invocation_authorization=invocation_auth,
                invocation_evidence_fingerprint=invoked.fingerprint.digest, authorization=authorization,
            )
            self.assertFalse(result.blocked, result.findings)
            self.assertEqual(len(result.verified.bundle.records), 10)
            self.assertEqual(len(result.verified.bundle.records_of_kind(
                "SemanticArtifactConformanceRecord")), 1)
            record = result.verified.bundle.one("SemanticArtifactConformanceRecord")
            self.assertTrue(record.semantic["semantic_pass"])
            reloaded = verify_persisted_representative_semantic_artifact_conformance(
                artifact_path=invoked.artifact_path, projection=projection,
                invocation_evidence_path=invoked.evidence_path,
                evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2],
                declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
                invocation_authorization=invocation_auth,
                invocation_evidence_fingerprint=invoked.fingerprint.digest, authorization=authorization,
            )
            self.assertEqual(reloaded.fingerprint, result.verified.fingerprint)

    def test_nonconforming_and_indeterminate_assessments_emit_no_record_or_evidence(self):
        inputs = self._inputs()
        for artifact in (b"not html", b"<!doctype html><html><body>"):
            with self.subTest(artifact=artifact), tempfile.TemporaryDirectory() as root_name:
                root = Path(root_name); output = root / "artifact"; invoke_dir = root / "invoke"
                conform_dir = root / "conform"
                output.mkdir(); invoke_dir.mkdir(); conform_dir.mkdir()
                invocation_auth = self._current_invocation_authorization(inputs, output, invoke_dir)
                invoked = self._invoke(inputs, invocation_auth).verified
                self.assertIsNotNone(invoked)
                invoked.artifact_path.write_bytes(artifact)
                projection = self._projection(inputs)
                authorization = self._current_conformance_authorization(
                    inputs, projection, invocation_auth, invoked, conform_dir)
                result = assess_representative_semantic_artifact_conformance(
                    artifact_path=invoked.artifact_path, projection=projection,
                    invocation_evidence_path=invoked.evidence_path,
                    evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2],
                    declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
                    invocation_authorization=invocation_auth,
                    invocation_evidence_fingerprint=invoked.fingerprint.digest, authorization=authorization,
                )
                self.assertTrue(result.blocked)
                self.assertIsNone(result.verified)
                self.assertEqual(tuple(conform_dir.iterdir()), ())


if __name__ == "__main__":
    unittest.main()
