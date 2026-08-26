"""TASK-054 publication Manifest authority and exact artifact-admission tests.

These tests intentionally describe the smallest public boundary wanted from the
TASK-054 implementation.  They use real TASK-050..053 objects and real files;
none of the identities below is intended to be a production fixture.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, fields, replace
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
import inspect
from unittest.mock import patch

from briefforge.bcrp.canonical import fingerprint_bundle
from briefforge.bcrp.model import BCRPBundle, BCRPRecord, RECORD_KINDS
from briefforge.publication_manifest_admission import (
    ManifestArtifactAdmission,
    ManifestFinding,
    PublicationManifestAuthorization,
    PublicationManifestResult,
    VerifiedPublicationManifest,
    compute_artifact_set_fingerprint,
    compute_manifest_authorization_fingerprint,
    produce_publication_manifest,
    validate_artifact_set_closure,
    verify_manifest_current_eligibility,
    verify_persisted_publication_manifest,
)
from briefforge.semantic_artifact_conformance import (
    ACCEPTED_ASSESSOR_IDENTITY,
    ACCEPTED_ASSESSOR_OWNER,
    ACCEPTED_ASSESSOR_ROLE,
    assess_semantic_artifact_conformance,
)
from briefforge.publication_lifecycle import LifecycleBundle, event_from_document
from briefforge.renderer_compatibility_planning import compute_lifecycle_inventory_digest
from tests import test_semantic_artifact_conformance as semantic_tests
from tests import test_publication_lifecycle_profile as lifecycle_tests


POLICY = "briefforge-publication-manifest-admission-policy:1.0.0"
PROFILE = "briefforge-publication-manifest-admission-profile:1.0.0"
PROJECTOR_ID = "authority:briefforge-publication-manifest-projector"
PROJECTOR_OWNER = "project:BriefForge"
PROJECTOR_ROLE = "publication-manifest-projector"
PROJECTOR_SCOPE = "one-publication-manifest-production"
IMPLEMENTATION = "briefforge.publication_manifest_admission"
IMPLEMENTATION_VERSION = "1.0.0"
EXCLUSIONS = (
    "distribution-authority", "distribution-execution", "successful-publication-authority",
    "deployment-authority", "atlasforge-authority", "browser-behavior-certification",
    "accessibility-certification", "editorial-certification", "visual-certification",
    "factual-reassessment",
)


class PublicationManifestAdmissionTests(unittest.TestCase):
    """Real predecessor chain plus mutation-isolated authority attacks."""

    setUp = semantic_tests.SemanticArtifactConformanceTests.setUp
    _ledger_directory = semantic_tests.SemanticArtifactConformanceTests._ledger_directory
    _inputs = semantic_tests.SemanticArtifactConformanceTests._inputs
    _authorization = semantic_tests.SemanticArtifactConformanceTests._authorization
    _invoke = semantic_tests.SemanticArtifactConformanceTests._invoke
    _conformance_authorization = semantic_tests.SemanticArtifactConformanceTests._conformance_authorization

    @staticmethod
    def _immutable_snapshot(case, authorization):
        inputs, invocation, conformance, verified = case
        return (
            tuple(record.to_document() for record in inputs[1].bundle.records),
            tuple(record.to_document() for record in inputs[5].bundle.records),
            tuple(record.to_document() for record in verified.bundle.records),
            asdict(invocation), asdict(conformance), asdict(authorization),
        )

    def _candidate(self, snapshot):
        # Both authorities are authored into material before Ready/Release.  In
        # particular, no caller-side assertion is allowed to invent either.
        base = semantic_tests.SemanticArtifactConformanceTests._candidate(self, snapshot)
        records = []
        for record in base.records:
            document = record.to_document()
            if record.kind == "PortablePresentationMaterialRecord":
                document["semantic"]["authorities"].append({
                    "id": PROJECTOR_ID,
                    "owner_identity": PROJECTOR_OWNER,
                    "role": PROJECTOR_ROLE,
                    "scope": PROJECTOR_SCOPE,
                })
            if record.kind == "CandidatePresentationPackageRecord" and getattr(self, "_task054_variant_text", None):
                document["semantic"]["statements"][0]["text"] = self._task054_variant_text
                document["semantic"]["sections"][0]["title"] = "Alternate governed observation"
            records.append(BCRPRecord.from_document(document))
        return BCRPBundle(base.profile_identity, base.profile_version, tuple(records))

    def _real_predecessor(self, root: Path, *, suffix: str = "task054"):
        inputs = self._inputs()
        output = root / "renderer"
        conformance = root / "conformance"
        output.mkdir()
        conformance.mkdir()
        invocation_auth = self._authorization(
            inputs, output, identity=f"renderer-invocation-authorization:{suffix}"
        )
        invoked = self._invoke(inputs, output, invocation_auth)
        self.assertFalse(invoked.blocked, invoked.findings)
        conformance_auth = self._conformance_authorization(
            inputs, invocation_auth, conformance,
            identity=f"semantic-conformance-authorization:{suffix}",
            record_identity=f"semantic-conformance:{suffix}",
        )
        assessed = assess_semantic_artifact_conformance(
            artifact_path=output / "publication.html",
            invocation_evidence_path=output / "invocation-evidence.json",
            evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
            invocation_authorization=invocation_auth, authorization=conformance_auth,
        )
        self.assertFalse(assessed.blocked, assessed.findings)
        self.assertEqual(len(assessed.verified.bundle.records), 10)
        return inputs, invocation_auth, conformance_auth, assessed.verified

    def _admission(self, inputs, invocation_auth, conformance_auth, order=0, **changes):
        artifact = Path(invocation_auth.output_directory) / invocation_auth.output_filename
        data = artifact.read_bytes()
        values = dict(
            identity=conformance_auth.artifact_identity,
            role="primary-semantic-publication",
            logical_filename=invocation_auth.output_filename,
            media_type=invocation_auth.media_type,
            byte_length=len(data), sha256=hashlib.sha256(data).hexdigest(), order=order,
            source_path=str(artifact.resolve()),
            release_identity=inputs[1].release.identity,
            release_fingerprint=inputs[1].fingerprint.digest,
            plan_identity=inputs[5].plan.identity, plan_fingerprint=inputs[5].fingerprint.digest,
            renderer_identity=invocation_auth.renderer_identity,
            renderer_version=invocation_auth.renderer_version,
            invocation_authorization_identity=invocation_auth.identity,
            invocation_evidence_fingerprint=conformance_auth.invocation_evidence_fingerprint,
            conformance_authorization_identity=conformance_auth.identity,
            conformance_evidence_fingerprint="",  # filled after persisted TASK-053 reload
            dependency_identities=(),
        )
        values.update(changes)
        return ManifestArtifactAdmission(**values)

    def _manifest_authorization(self, case, manifest_dir: Path, admissions=None, **changes):
        inputs, invocation_auth, conformance_auth, verified_conformance = case
        conformance_evidence = Path(conformance_auth.evidence_directory) / conformance_auth.evidence_filename
        persisted = semantic_tests.verify_persisted_semantic_artifact_conformance(
            artifact_path=Path(invocation_auth.output_directory) / invocation_auth.output_filename,
            invocation_evidence_path=Path(invocation_auth.output_directory) / invocation_auth.evidence_filename,
            conformance_evidence_path=conformance_evidence,
            evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
            invocation_authorization=invocation_auth, authorization=conformance_auth,
        )
        if admissions is None:
            admissions = (self._admission(
                inputs, invocation_auth, conformance_auth,
                conformance_evidence_fingerprint=persisted.fingerprint.digest,
            ),)
        values = dict(
            identity="manifest-authorization:task054-real",
            policy_identity=POLICY, profile_identity=PROFILE, profile_version="1.0.0",
            authority_identity=PROJECTOR_ID, authority_owner=PROJECTOR_OWNER,
            authority_role=PROJECTOR_ROLE, authorization_time="2026-07-31T12:00:00Z",
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
            invocation_evidence_fingerprint=conformance_auth.invocation_evidence_fingerprint,
            conformance_authorization_identity=conformance_auth.identity,
            conformance_authorization_fingerprint=conformance_auth.fingerprint,
            conformance_profile_identity=conformance_auth.profile_identity,
            conformance_profile_version=conformance_auth.profile_version,
            assessor_identity=conformance_auth.assessor_identity,
            conformance_evidence_fingerprint=persisted.fingerprint.digest,
            conformance_verdict="approved",
            predecessor_closure_fingerprint=fingerprint_bundle(
                persisted.bundle, domain="profile-instance", require_valid=False
            ).digest,
            artifact_inventory=tuple(admissions),
            artifact_set_fingerprint=compute_artifact_set_fingerprint(tuple(admissions)),
            manifest_identity="manifest:task054-real", manifest_version="1.0.0",
            manifest_time="2026-07-31T12:01:00Z",
            projector_implementation=IMPLEMENTATION, projector_version=IMPLEMENTATION_VERSION,
            evidence_directory=str(manifest_dir.resolve()), evidence_filename="publication-manifest.json",
            commitment_ledger_directory=str((manifest_dir.parent / "manifest-ledger").resolve()),
            record_identity="publication-manifest-record:task054-real",
            exclusions=EXCLUSIONS,
        )
        values.update(changes)
        provisional = PublicationManifestAuthorization(**values, fingerprint="")
        return replace(provisional, fingerprint=compute_manifest_authorization_fingerprint(provisional))

    def _call(self, case, authorization, **changes):
        inputs, invocation_auth, conformance_auth, _ = case
        args = dict(
            evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
            invocation_authorization=invocation_auth,
            artifact_path=Path(invocation_auth.output_directory) / invocation_auth.output_filename,
            invocation_evidence_path=Path(invocation_auth.output_directory) / invocation_auth.evidence_filename,
            conformance_authorization=conformance_auth,
            conformance_evidence_path=Path(conformance_auth.evidence_directory) / conformance_auth.evidence_filename,
            authorization=authorization,
        )
        args.update(changes)
        return produce_publication_manifest(**args)

    def test_real_task053_path_produces_exact_one_manifest_eleven_record_closure_and_reloads(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            case = self._real_predecessor(root)
            manifest_dir = root / "manifest"
            manifest_dir.mkdir()
            authorization = self._manifest_authorization(case, manifest_dir)
            frozen_inputs = self._immutable_snapshot(case, authorization)
            result = self._call(case, authorization)
            self.assertIsInstance(result, PublicationManifestResult)
            self.assertFalse(result.blocked, result.findings)
            self.assertEqual(result.findings, ())
            self.assertIsInstance(result.verified, VerifiedPublicationManifest)
            bundle = result.verified.bundle
            self.assertEqual(len(bundle.records), 11)
            self.assertEqual(len(bundle.records_of_kind("PublicationManifestRecord")), 1)
            record = bundle.one("PublicationManifestRecord")
            self.assertEqual(record.identity, authorization.record_identity)
            self.assertEqual(record.semantic["release_ref"], authorization.release_identity)
            self.assertEqual(record.semantic["artifact_ids"], [authorization.artifact_inventory[0].identity])
            payload = record.extensions[0]["payload"]
            self.assertEqual(payload["distribution_authority"], "absent")
            self.assertEqual(payload["distribution_execution"], "not-performed")
            self.assertEqual(payload["successful_publication"], "not-asserted")
            self.assertEqual(payload["atlasforge_authority"], "absent")
            self.assertEqual(tuple(payload["authority_exclusions"]), EXCLUSIONS)
            admission = payload["admission_requirement_outcomes"]
            self.assertEqual(
                [item["requirement_id"] for item in admission],
                payload["admission_requirement_ids"],
            )
            self.assertEqual(len(admission), len({item["requirement_id"] for item in admission}))
            self.assertEqual({item["outcome"] for item in admission}, {"conformant"})
            links = payload["authority_audit_links"]
            self.assertEqual(len(links), len({item["role"] for item in links}))
            self.assertTrue(all(item["source_identity"] == authorization.record_identity for item in links))
            self.assertEqual(payload["aggregate_manifest_verdict"], "approved")
            self.assertEqual(payload["verification_status"], "verified")
            reloaded = verify_persisted_publication_manifest(
                manifest_evidence_path=manifest_dir / authorization.evidence_filename,
                evidence_snapshot=case[0][0], verified_release=case[0][1],
                lifecycle_scope=case[0][2], declaration=case[0][3],
                planning_authorization=case[0][4], verified_plan=case[0][5],
                invocation_authorization=case[1], conformance_authorization=case[2],
                artifact_paths=(Path(case[1].output_directory) / case[1].output_filename,),
                authorization=authorization,
            )
            self.assertEqual(reloaded.fingerprint, result.verified.fingerprint)
            self.assertEqual(self._immutable_snapshot(case, authorization), frozen_inputs)

    def test_second_materially_different_real_governed_case_has_distinct_chain_and_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first_root = root / "first"; first_root.mkdir()
            first = self._real_predecessor(first_root, suffix="task054-first")
            first_manifest = first_root / "manifest"; first_manifest.mkdir()
            first_authorization = self._manifest_authorization(
                first, first_manifest,
                identity="manifest-production-authorization:task054-first",
                manifest_identity="manifest:task054-first",
                record_identity="publication-manifest-record:task054-first",
            )
            first_result = self._call(first, first_authorization)
            self.assertFalse(first_result.blocked, first_result.findings)

            second_root = root / "second"; second_root.mkdir()
            self._task054_variant_text = "A second independently governed observation has different semantic bytes."
            try:
                second = self._real_predecessor(second_root, suffix="task054-second")
            finally:
                del self._task054_variant_text
            second_manifest = second_root / "manifest"; second_manifest.mkdir()
            second_authorization = self._manifest_authorization(
                second, second_manifest,
                identity="manifest-production-authorization:task054-second",
                manifest_identity="manifest:task054-second",
                record_identity="publication-manifest-record:task054-second",
            )
            second_result = self._call(second, second_authorization)
            self.assertFalse(second_result.blocked, second_result.findings)
            self.assertNotEqual(first[0][5].fingerprint, second[0][5].fingerprint)
            self.assertNotEqual(first[1].identity, second[1].identity)
            self.assertNotEqual(first[2].identity, second[2].identity)
            self.assertNotEqual(
                first_authorization.artifact_inventory[0].identity,
                second_authorization.artifact_inventory[0].identity,
            )
            self.assertNotEqual(first_result.verified.fingerprint, second_result.verified.fingerprint)

    def test_derivation_and_reload_are_deterministic_for_identical_governed_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            case = self._real_predecessor(root)
            destination = root / "manifest"
            destination.mkdir()
            authorization = self._manifest_authorization(case, destination)
            produced = self._call(case, authorization)
            self.assertFalse(produced.blocked, produced.findings)
            arguments = dict(
                manifest_evidence_path=destination / authorization.evidence_filename,
                evidence_snapshot=case[0][0], verified_release=case[0][1],
                lifecycle_scope=case[0][2], declaration=case[0][3],
                planning_authorization=case[0][4], verified_plan=case[0][5],
                invocation_authorization=case[1], conformance_authorization=case[2],
                artifact_paths=(Path(case[1].output_directory) / case[1].output_filename,),
                authorization=authorization,
            )
            first = verify_persisted_publication_manifest(**arguments)
            second = verify_persisted_publication_manifest(**arguments)
            self.assertEqual(
                [record.to_document() for record in first.bundle.records],
                [record.to_document() for record in second.bundle.records],
            )
            self.assertEqual(first.fingerprint, second.fingerprint)
            self.assertEqual(first.fingerprint, produced.verified.fingerprint)

    def test_producer_independently_invokes_persisted_conformance_verifier(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); case = self._real_predecessor(root)
            destination = root / "manifest"; destination.mkdir()
            authorization = self._manifest_authorization(case, destination)
            target = "briefforge.publication_manifest_admission.verify_persisted_semantic_artifact_conformance"
            with patch(target, wraps=semantic_tests.verify_persisted_semantic_artifact_conformance) as verifier:
                result = self._call(case, authorization)
            self.assertFalse(result.blocked, result.findings)
            self.assertEqual(verifier.call_count, 2)  # initial gate plus final persisted reload

    def test_no_predecessor_bypass_and_deleted_task053_evidence_blocks_final_reload(self):
        self.assertNotIn("_verified_predecessor", inspect.signature(verify_persisted_publication_manifest).parameters)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); case = self._real_predecessor(root)
            destination = root / "manifest"; destination.mkdir()
            authorization = self._manifest_authorization(case, destination)
            evidence = Path(case[2].evidence_directory) / case[2].evidence_filename
            real = semantic_tests.verify_persisted_semantic_artifact_conformance
            calls = 0
            def deleting_verifier(**kwargs):
                nonlocal calls
                calls += 1
                if calls == 2:
                    evidence.unlink()
                return real(**kwargs)
            with patch("briefforge.publication_manifest_admission.verify_persisted_semantic_artifact_conformance", side_effect=deleting_verifier):
                result = self._call(case, authorization)
            self.assertTrue(result.blocked)
            self.assertEqual({f.code for f in result.findings}, {"manifest-persistence-failed"})
            self.assertFalse((destination / authorization.evidence_filename).exists())

    def test_production_inventory_is_derived_single_role_and_dependency_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); case = self._real_predecessor(root)
            base = self._manifest_authorization(case, root).artifact_inventory[0]
            attacks = (
                (replace(base, identity="artifact:invented"), "artifact-governed-evidence-mismatch"),
                (replace(base, role="publication-authority"), "unauthorized-artifact-role"),
                (replace(base, dependency_identities=("artifact:invented",)), "unauthorized-artifact-dependencies"),
            )
            for index, (item, code) in enumerate(attacks):
                destination = root / f"attack-{index}"; destination.mkdir()
                auth = self._manifest_authorization(case, destination, admissions=(item,))
                result = self._call(case, auth)
                self.assertTrue(result.blocked)
                self.assertIn(code, {finding.code for finding in result.findings})

    def test_generic_bounded_multi_artifact_closure_is_ordered_and_not_directory_derived(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = (root / "index.html", root / "notice.txt", root / "chart.svg")
            contents = (b"<p>separate governed case</p>", b"terms\n", b"<svg/>\n")
            roles = ("primary", "legal-notice", "static-exhibit")
            media = ("text/html", "text/plain", "image/svg+xml")
            items = []
            for order, (path, content, role, media_type) in enumerate(zip(paths, contents, roles, media)):
                path.write_bytes(content)
                items.append(ManifestArtifactAdmission(
                    identity=f"artifact:bounded-{order}", role=role,
                    logical_filename=path.name, media_type=media_type,
                    byte_length=len(content), sha256=hashlib.sha256(content).hexdigest(), order=order,
                    source_path=str(path.resolve()), release_identity="release:bounded",
                    release_fingerprint="1" * 64, plan_identity="plan:bounded",
                    plan_fingerprint="2" * 64, renderer_identity="renderer:bounded",
                    renderer_version="1.0.0", invocation_authorization_identity="invocation:bounded",
                    invocation_evidence_fingerprint="3" * 64,
                    conformance_authorization_identity="conformance:bounded",
                    conformance_evidence_fingerprint="4" * 64, dependency_identities=(),
                ))
            (root / "unrelated.bin").write_bytes(b"must not be enumerated")
            first = validate_artifact_set_closure(tuple(items), tuple(paths))
            second = validate_artifact_set_closure(tuple(items), tuple(reversed(paths)))
            self.assertEqual(first, ())
            self.assertTrue(second)
            self.assertIn("artifact-order-mismatch", {finding.code for finding in second})
            self.assertEqual(compute_artifact_set_fingerprint(tuple(items)),
                             compute_artifact_set_fingerprint(tuple(deepcopy(items))))
            self.assertEqual(len({i.identity for i in items}), 3)
            self.assertEqual(len({i.role for i in items}), 3)

    def test_unsafe_filenames_and_portable_collisions_are_all_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); path = root / "safe.html"; path.write_bytes(b"x")
            base = ManifestArtifactAdmission(
                identity="artifact:safe", role="primary", logical_filename="safe.html",
                media_type="text/html", byte_length=1, sha256=hashlib.sha256(b"x").hexdigest(),
                order=0, source_path=str(path), release_identity="release:x", release_fingerprint="1"*64,
                plan_identity="plan:x", plan_fingerprint="2"*64, renderer_identity="renderer:x",
                renderer_version="1", invocation_authorization_identity="invocation:x",
                invocation_evidence_fingerprint="3"*64, conformance_authorization_identity="conformance:x",
                conformance_evidence_fingerprint="4"*64, dependency_identities=(),
            )
            unsafe = ("../x", "a/../x", "/tmp/x", "C:\\x", "a/b", "a\\b", ".", "..", "", "x\x00.html")
            for name in unsafe:
                with self.subTest(name=repr(name)):
                    findings = validate_artifact_set_closure((replace(base, logical_filename=name),), (path,))
                    self.assertIn("unsafe-artifact-filename", {f.code for f in findings})
            collision_sets = (
                ("Readme.HTML", "readme.html"),
                ("caf\u00e9.html", "cafe\u0301.html"),
            )
            for left, right in collision_sets:
                items = (replace(base, logical_filename=left), replace(base, identity="artifact:two", role="two", logical_filename=right, order=1))
                with self.subTest(names=(left, right)):
                    self.assertIn("artifact-filename-collision", {f.code for f in validate_artifact_set_closure(items, (path, path))})

    def test_inventory_omission_extra_duplicate_and_conflict_findings_are_specific(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); case = self._real_predecessor(root)
            item = self._manifest_authorization(case, root).artifact_inventory[0]
            source = Path(item.source_path)
            other = root / "other.html"; other.write_bytes(source.read_bytes())
            attacks = {
                "artifact-omitted": ((item,), ()),
                "unexpected-artifact": ((item,), (source, other)),
                "duplicate-artifact-identity": ((item, replace(item, order=1)), (source, source)),
                "duplicate-artifact-role": ((item, replace(item, identity="artifact:two", order=1)), (source, source)),
                "duplicate-artifact-filename": ((item, replace(item, identity="artifact:two", role="two", order=1)), (source, source)),
                "duplicate-artifact-order": ((item, replace(item, identity="artifact:two", role="two", logical_filename="two.html")), (source, source)),
                "conflicting-artifact-role": ((item, replace(item, role="secondary")), (source, source)),
            }
            for expected_code, (inventory, paths) in attacks.items():
                with self.subTest(expected_code=expected_code):
                    codes = {f.code for f in validate_artifact_set_closure(inventory, paths)}
                    self.assertIn(expected_code, codes)

    def test_every_authority_chain_binding_drift_blocks_without_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); case = self._real_predecessor(root)
            changes = (
                {"release_fingerprint": "0"*64}, {"lifecycle_inventory_digest": "0"*64},
                {"plan_fingerprint": "0"*64}, {"capability_fingerprint": "0"*64},
                {"invocation_authorization_fingerprint": "0"*64},
                {"invocation_evidence_fingerprint": "0"*64},
                {"conformance_authorization_fingerprint": "0"*64},
                {"conformance_evidence_fingerprint": "0"*64},
                {"predecessor_closure_fingerprint": "0"*64},
                {"profile_identity": "profile:other"}, {"profile_version": "9"},
                {"assessor_identity": "authority:other"}, {"authority_identity": "authority:other"},
                {"artifact_set_fingerprint": "0"*64}, {"projector_implementation": "other.impl"},
                {"projector_version": "9"}, {"record_identity": "release:task052"},
                {"exclusions": ()},
            )
            for index, change in enumerate(changes):
                destination = root / f"failed-{index}"; destination.mkdir()
                auth = self._manifest_authorization(case, destination, **change)
                result = self._call(case, auth)
                with self.subTest(change=change):
                    self.assertTrue(result.blocked)
                    self.assertIsNone(result.verified)
                    self.assertTrue(result.findings)
                    self.assertEqual(tuple(destination.iterdir()), ())

    def test_artifact_and_audit_link_drift_blocks(self):
        mutations = (b"tamper", b"<html></html>")
        for mutation in mutations:
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary); case = self._real_predecessor(root)
                destination = root / "manifest"; destination.mkdir()
                auth = self._manifest_authorization(case, destination)
                Path(auth.artifact_inventory[0].source_path).write_bytes(mutation)
                result = self._call(case, auth)
                self.assertTrue(result.blocked)
                self.assertTrue({"artifact-digest-mismatch", "persisted-conformance-invalid"} & {f.code for f in result.findings})
                self.assertEqual(tuple(destination.iterdir()), ())

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); case = self._real_predecessor(root)
            destination = root / "manifest"; destination.mkdir()
            auth = self._manifest_authorization(case, destination)
            evidence = Path(case[2].evidence_directory) / case[2].evidence_filename
            document = json.loads(evidence.read_text(encoding="utf-8"))
            conformance = next(record for record in document["records"]
                               if record["record_kind"] == "SemanticArtifactConformanceRecord")
            conformance["semantic"]["audit_ref"] = "generated-artifact-audit:cross-authority"
            evidence.write_text(json.dumps(document, sort_keys=True, separators=(",", ":")), encoding="utf-8")
            result = self._call(case, auth)
            self.assertTrue(result.blocked)
            self.assertIn("persisted-conformance-invalid", {f.code for f in result.findings})
            self.assertEqual(tuple(destination.iterdir()), ())

    def test_unsupported_status_string_is_not_treated_as_authority(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); case = self._real_predecessor(root)
            for status in ("pass", "successful", "APPROVED", "unknown", "unsupported", ""):
                destination = root / ("status-" + (status or "empty")); destination.mkdir()
                auth = self._manifest_authorization(case, destination, conformance_verdict=status)
                result = self._call(case, auth)
                with self.subTest(status=status):
                    self.assertTrue(result.blocked)
                    self.assertIn("unsupported-conformance-status", {f.code for f in result.findings})
                    self.assertEqual(tuple(destination.iterdir()), ())

    def test_manifest_authorization_and_creation_chronology_is_causal(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); case = self._real_predecessor(root)
            attacks = (
                {"authorization_time": "2026-08-02T12:00:00Z"},
                {"authorization_time": "2026-07-17T09:00:00Z"},
                {"manifest_time": "2026-07-17T10:59:59Z"},
            )
            for index, changes in enumerate(attacks):
                destination = root / f"chronology-{index}"; destination.mkdir()
                authorization = self._manifest_authorization(case, destination, **changes)
                result = self._call(case, authorization)
                self.assertTrue(result.blocked)
                self.assertIn("manifest-authorization-chronology-invalid", {f.code for f in result.findings})
                self.assertFalse((destination / authorization.evidence_filename).exists())

    def test_authorization_replay_and_concurrent_reuse_have_exactly_one_winner(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); case = self._real_predecessor(root)
            destination = root / "manifest"; destination.mkdir()
            auth = self._manifest_authorization(case, destination)
            barrier = threading.Barrier(2)
            results = []
            def attempt():
                barrier.wait()
                results.append(self._call(case, auth))
            threads = [threading.Thread(target=attempt) for _ in range(2)]
            for thread in threads: thread.start()
            for thread in threads: thread.join()
            self.assertEqual(sum(not result.blocked for result in results), 1)
            loser = next(result for result in results if result.blocked)
            self.assertEqual({f.code for f in loser.findings}, {"manifest-authorization-consumed"})
            replay = self._call(case, auth)
            self.assertTrue(replay.blocked)
            self.assertEqual({f.code for f in replay.findings}, {"manifest-authorization-consumed"})

    def test_same_authorization_identity_with_different_fingerprint_is_consumed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); case = self._real_predecessor(root)
            first_dir = root / "first"; first_dir.mkdir()
            first = self._manifest_authorization(case, first_dir)
            self.assertFalse(self._call(case, first).blocked)
            second_dir = root / "second"; second_dir.mkdir()
            second = self._manifest_authorization(
                case, second_dir, identity=first.identity,
                manifest_identity="manifest:task054-different-fingerprint",
                record_identity="publication-manifest-record:task054-different-fingerprint",
                manifest_time="2026-07-31T12:02:00+00:00",
            )
            self.assertNotEqual(first.fingerprint, second.fingerprint)
            result = self._call(case, second)
            self.assertTrue(result.blocked)
            self.assertEqual({f.code for f in result.findings}, {"manifest-authorization-consumed"})
            self.assertEqual(tuple(second_dir.iterdir()), ())

    def test_second_independently_built_full_single_artifact_chain_produces_and_reloads(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); inputs = self._inputs()
            output = root / "renderer-second"; output.mkdir()
            conformance_dir = root / "conformance-second"; conformance_dir.mkdir()
            invocation = self._authorization(
                inputs, output, identity="renderer-invocation-authorization:task054-second",
                authorization_time="2026-07-17T10:04:00Z",
            )
            invoked = self._invoke(inputs, output, invocation)
            self.assertFalse(invoked.blocked, invoked.findings)
            conformance = self._conformance_authorization(
                inputs, invocation, conformance_dir,
                identity="semantic-conformance-authorization:task054-second",
                record_identity="semantic-conformance:task054-second",
                authorization_time="2026-07-17T11:01:00Z",
            )
            assessed = assess_semantic_artifact_conformance(
                artifact_path=output / invocation.output_filename,
                invocation_evidence_path=output / invocation.evidence_filename,
                evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2],
                declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
                invocation_authorization=invocation, authorization=conformance,
            )
            self.assertFalse(assessed.blocked, assessed.findings)
            case = (inputs, invocation, conformance, assessed.verified)
            destination = root / "manifest-second"; destination.mkdir()
            authorization = self._manifest_authorization(
                case, destination, identity="manifest-authorization:task054-second",
                manifest_identity="manifest:task054-second", record_identity="publication-manifest-record:task054-second",
            )
            result = self._call(case, authorization)
            self.assertFalse(result.blocked, result.findings)
            self.assertEqual(result.verified.bundle.one("PublicationManifestRecord").semantic["artifact_ids"],
                             ["artifact:task054-second"])
            reloaded = verify_persisted_publication_manifest(
                manifest_evidence_path=destination / authorization.evidence_filename,
                evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2],
                declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
                invocation_authorization=invocation, conformance_authorization=conformance,
                artifact_paths=(output / invocation.output_filename,), authorization=authorization,
            )
            self.assertEqual(reloaded.fingerprint, result.verified.fingerprint)

    def test_complete_negative_findings_are_stable_sorted_and_not_short_circuited(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); case = self._real_predecessor(root)
            destination = root / "manifest"; destination.mkdir()
            auth = self._manifest_authorization(
                case, destination, policy_identity="policy:wrong", profile_identity="profile:wrong",
                authority_role="wrong-role", release_fingerprint="0"*64,
                plan_fingerprint="0"*64, exclusions=(), conformance_verdict="unsupported",
            )
            before = deepcopy(auth)
            first = self._call(case, auth)
            second_destination = root / "manifest-second"; second_destination.mkdir()
            second_auth = replace(auth, evidence_directory=str(second_destination), identity="manifest-authorization:second", fingerprint="")
            second_auth = replace(second_auth, fingerprint=compute_manifest_authorization_fingerprint(second_auth))
            second = self._call(case, second_auth)
            first_triplets = tuple((f.code, f.location, f.message) for f in first.findings)
            second_triplets = tuple((f.code, f.location, f.message) for f in second.findings)
            self.assertGreaterEqual(len(first_triplets), 7)
            self.assertEqual(first_triplets, tuple(sorted(set(first_triplets))))
            self.assertEqual(first_triplets, second_triplets)
            self.assertTrue(all(isinstance(f, ManifestFinding) for f in first.findings))
            self.assertEqual(auth, before)

    def test_persistence_failure_rolls_back_and_leaves_no_staging_or_orphan(self):
        for failure in (OSError("disk full"), RuntimeError("fsync failed")):
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary); case = self._real_predecessor(root)
                destination = root / "manifest"; destination.mkdir()
                auth = self._manifest_authorization(case, destination)
                with patch("briefforge.publication_manifest_admission._persist_manifest_transaction", side_effect=failure):
                    result = self._call(case, auth)
                self.assertTrue(result.blocked)
                self.assertIn("manifest-persistence-failed", {f.code for f in result.findings})
                self.assertEqual(tuple(destination.iterdir()), ())
                ledger = Path(auth.commitment_ledger_directory)
                residue = tuple(ledger.iterdir()) if ledger.exists() else ()
                self.assertEqual(len(residue), 1)
                self.assertTrue(residue[0].name.endswith(".manifest-authorization-identity-consumed"))
                self.assertFalse(any("tmp" in path.name or "stage" in path.name for path in root.rglob("*")))

    def test_persisted_tampering_and_coordinated_manifest_rewrite_are_detected(self):
        for coordinated in (False, True):
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary); case = self._real_predecessor(root)
                destination = root / "manifest"; destination.mkdir()
                auth = self._manifest_authorization(case, destination)
                result = self._call(case, auth); self.assertFalse(result.blocked)
                evidence = destination / auth.evidence_filename
                document = json.loads(evidence.read_text(encoding="utf-8"))
                document["records"][-1]["semantic"]["manifest_version"] = "9.9.9"
                evidence.write_text(json.dumps(document, sort_keys=True, separators=(",", ":")), encoding="utf-8")
                if coordinated:
                    # Rewriting a sibling commitment with a digest cannot forge the
                    # authorization-consumption commitment bound before production.
                    for commitment in Path(auth.commitment_ledger_directory).glob("*"):
                        commitment.write_text(hashlib.sha256(evidence.read_bytes()).hexdigest(), encoding="ascii")
                with self.subTest(coordinated=coordinated), self.assertRaises(ValueError):
                    verify_persisted_publication_manifest(
                        manifest_evidence_path=evidence, evidence_snapshot=case[0][0],
                        verified_release=case[0][1], lifecycle_scope=case[0][2], declaration=case[0][3],
                        planning_authorization=case[0][4], verified_plan=case[0][5],
                        invocation_authorization=case[1], conformance_authorization=case[2],
                        artifact_paths=(Path(case[1].output_directory) / case[1].output_filename,),
                        authorization=auth,
                    )

    def test_later_lifecycle_change_does_not_rewrite_history_but_blocks_current_eligibility(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); case = self._real_predecessor(root)
            destination = root / "manifest"; destination.mkdir()
            auth = self._manifest_authorization(case, destination)
            produced = self._call(case, auth); self.assertFalse(produced.blocked)
            evidence = destination / auth.evidence_filename
            historical = evidence.read_bytes()
            scope = case[0][2]
            binding = scope.releases[0]
            withdrawal = lifecycle_tests.withdrawal_document(
                identity="lifecycle-event:task054-later-withdrawal",
                target_identity=binding.identity, target_fingerprint=binding.fingerprint,
                time="2026-08-01T10:00:00Z",
            )
            withdrawal["semantic"]["publication_identity"] = binding.publication_identity
            changed = replace(
                scope,
                bundle=LifecycleBundle(scope.bundle.profile_identity, scope.bundle.profile_version,
                                       (event_from_document(withdrawal),)),
                policies=(lifecycle_tests.policy(),), inventory_digest="",
            )
            changed = replace(changed, inventory_digest=compute_lifecycle_inventory_digest(changed))
            current = verify_manifest_current_eligibility(produced.verified, lifecycle_scope=changed)
            self.assertTrue(current.blocked)
            self.assertIn("manifest-not-currently-eligible", {f.code for f in current.findings})
            self.assertEqual(evidence.read_bytes(), historical)
            eligible = verify_manifest_current_eligibility(produced.verified, lifecycle_scope=case[0][2])
            self.assertFalse(eligible.blocked, eligible.findings)
            self.assertEqual(evidence.read_bytes(), historical)

    def test_inputs_and_verified_outputs_are_detached_and_immutable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); case = self._real_predecessor(root)
            destination = root / "manifest"; destination.mkdir()
            auth = self._manifest_authorization(case, destination)
            before = self._immutable_snapshot(case, auth)
            result = self._call(case, auth); self.assertFalse(result.blocked)
            self.assertEqual(self._immutable_snapshot(case, auth), before)
            detached = result.verified.bundle
            detached.one("PublicationManifestRecord").semantic["manifest_version"] = "mutated"
            self.assertEqual(result.verified.bundle.one("PublicationManifestRecord").semantic["manifest_version"], "1.0.0")
            with self.assertRaises((AttributeError, TypeError)):
                result.verified.fingerprint = None

    def test_exactly_eleven_core_kinds_and_bcrp_import_isolation_remain(self):
        self.assertEqual(len(RECORD_KINDS), 11)
        self.assertEqual(RECORD_KINDS[-1], "PublicationManifestRecord")
        import briefforge.bcrp.model as model
        import briefforge.bcrp.validation as validation
        self.assertFalse(hasattr(model, "PublicationManifestAuthorization"))
        self.assertFalse(hasattr(validation, "produce_publication_manifest"))
        self.assertEqual(
            {field.name for field in fields(ManifestFinding)},
            {"code", "location", "message"},
        )

    def test_projector_must_be_released_and_forbidden_downstream_authority_never_bootstraps_it(self):
        # TASK-053 helper has released assessor authority but no Manifest projector.
        ungoverned = semantic_tests.SemanticArtifactConformanceTests()
        ungoverned.setUp()
        self.addCleanup(ungoverned.doCleanups)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            # Build through its own helper so caller authorization still claims the
            # projector; independently verified Release must defeat that claim.
            inputs = ungoverned._inputs()
            output = root / "renderer"; output.mkdir()
            evidence = root / "conformance"; evidence.mkdir()
            invocation = ungoverned._authorization(inputs, output)
            ungoverned._invoke(inputs, output, invocation)
            conformance_auth = ungoverned._conformance_authorization(inputs, invocation, evidence)
            assessed = assess_semantic_artifact_conformance(
                artifact_path=output / "publication.html", invocation_evidence_path=output / "invocation-evidence.json",
                evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2], declaration=inputs[3],
                planning_authorization=inputs[4], verified_plan=inputs[5], invocation_authorization=invocation,
                authorization=conformance_auth,
            )
            self.assertFalse(assessed.blocked)
            case = (inputs, invocation, conformance_auth, assessed.verified)
            destination = root / "manifest"; destination.mkdir()
            auth = self._manifest_authorization(case, destination)
            auth = replace(auth, exclusions=EXCLUSIONS + ("caller-claims-distribution-authority",), fingerprint="")
            auth = replace(auth, fingerprint=compute_manifest_authorization_fingerprint(auth))
            result = self._call(case, auth)
            self.assertTrue(result.blocked)
            codes = {f.code for f in result.findings}
            self.assertIn("unreleased-manifest-projector-authority", codes)
            self.assertNotIn("approved", codes)
            self.assertEqual(tuple(destination.iterdir()), ())


if __name__ == "__main__":
    unittest.main()
