"""TASK-052 controlled fixed-renderer invocation and artifact-evidence proof."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import tempfile
import time
import unittest
import uuid
from unittest.mock import patch

from briefforge.bcrp import RecordDraft, author_candidate_bundle
from briefforge.bcrp.validation import validate_bundle
from briefforge.bcrp_legacy_compatibility import map_legacy_ready_to_bcrp
from briefforge.controlled_renderer_invocation import (
    ACCEPTED_INVOCATION_AUTHORITY_IDENTITY,
    ACCEPTED_INVOCATION_AUTHORITY_OWNER,
    ACCEPTED_INVOCATION_AUTHORITY_ROLE,
    CONTROLLED_INVOCATION_POLICY_ID,
    FIXED_RENDERER_IDENTITY,
    RendererInvocationAuthorization,
    build_minimal_html_projection,
    compute_invocation_authorization_fingerprint,
    invoke_controlled_renderer,
    renderer_implementation_digest,
    verify_persisted_renderer_invocation,
)
from briefforge.publication_release import (
    ACCEPTED_AUTHORITY_IDENTITY,
    ACCEPTED_AUTHORITY_OWNER,
    ACCEPTED_AUTHORITY_ROLE,
    produce_publication_release,
)
from briefforge.renderer_adapter import html_renderer_contract
from briefforge.renderer_compatibility_planning import (
    ACCEPTED_DECLARATION_PROFILE_ID,
    ACCEPTED_DECLARATION_PROFILE_VERSION,
    CAPABILITY_DECLARATION_CONTRACT,
    CapabilityClaim,
    RendererCapabilityDeclaration,
    compute_capability_declaration_fingerprint,
    produce_renderer_compatibility_plan,
)
from tests import test_bcrp_lifecycle_authority_compatibility as compatibility_tests
from tests import test_bcrp_publication_release as release_tests
from tests import test_renderer_compatibility_planning as planning_tests


class _CallableRendererHelper:
    def __call__(self, value):
        return str(value)


def _cleanup_ledger_prefix(prefix):
    """Remove only directories carrying this proof object's unguessable prefix."""
    temporary_root = Path(tempfile.gettempdir()).resolve(strict=True)
    for candidate in temporary_root.iterdir():
        if not candidate.name.startswith(prefix):
            continue
        try:
            resolved = candidate.resolve(strict=True)
        except FileNotFoundError:
            continue
        if candidate.is_symlink() or resolved.parent != temporary_root or not resolved.is_dir():
            continue
        shutil.rmtree(resolved)


class ControlledRendererInvocationTests(unittest.TestCase):
    def setUp(self):
        self._ledger_by_output = {}

    def _ledger_directory(self, output_directory):
        key = str(Path(output_directory).resolve())
        if key not in self._ledger_by_output:
            prefix = f"briefforge-task052-ledger-{uuid.uuid4().hex}-"
            self.addCleanup(_cleanup_ledger_prefix, prefix)
            path = tempfile.mkdtemp(prefix=prefix)
            self._ledger_by_output[key] = path
        return self._ledger_by_output[key]

    def _candidate(self, snapshot):
        brief = RecordDraft(
            "brief:task052",
            {
                "organizing_purpose": {"id": "purpose:brief-task052", "statement": "Explain one reviewed synthetic observation."},
                "audiences": [{"id": "audience:brief-task052", "description": "A bounded synthetic reader."}],
                "scope": "One static synthetic presentation.",
                "non_scope": "No analysis, live data, discovery, or distribution.",
            },
        )
        material = RecordDraft(
            "material:task052",
            {
                "authorities": [
                    {"id": "authority:synthetic-upstream", "owner_identity": "project:SyntheticUpstream", "role": "upstream-semantic-authority", "scope": "synthetic-observation"},
                    {"id": "authority:presentation-task052", "owner_identity": "project:BriefForge", "role": "presentation-author", "scope": "presentation-only"},
                    {"id": "authority:validation-task052", "owner_identity": "project:BriefForge", "role": "validation-authority", "scope": "BCRP-L0-L6"},
                    {"id": ACCEPTED_AUTHORITY_IDENTITY, "owner_identity": ACCEPTED_AUTHORITY_OWNER, "role": ACCEPTED_AUTHORITY_ROLE, "scope": "fixed-evidence-publication-release"},
                    {"id": ACCEPTED_INVOCATION_AUTHORITY_IDENTITY, "owner_identity": ACCEPTED_INVOCATION_AUTHORITY_OWNER, "role": ACCEPTED_INVOCATION_AUTHORITY_ROLE, "scope": "one-controlled-renderer-invocation-act"},
                ],
                "provenance": [{"id": "provenance:task052", "authority_ref": "authority:synthetic-upstream", "citation": "Synthetic governed evidence constructed for TASK-052."}],
                "evidence_snapshots": [{"id": snapshot.identity, "version": snapshot.version, "content_fingerprint": f"sha256:{snapshot.inventory_digest}", "provenance_ref": "provenance:task052"}],
                "external_references": [{"id": "external:task052", "reference_kind": "synthetic-reviewed-evidence", "upstream_object_identity": "SyntheticUpstream:observation-1", "snapshot_ref": snapshot.identity, "provenance_ref": "provenance:task052", "authority_ref": "authority:synthetic-upstream"}],
                "values": [], "required_value_ids": [], "consistency_assertions": [],
            },
        )
        candidate = RecordDraft(
            "candidate:task052",
            {
                "brief_ref": "brief:task052", "material_refs": ["material:task052"],
                "organizing_purpose": {"id": "purpose:candidate-task052", "statement": "Explain one reviewed synthetic observation.", "brief_purpose_ref": "purpose:brief-task052"},
                "audiences": [{"id": "audience:candidate-task052", "description": "A bounded synthetic reader.", "brief_audience_ref": "audience:brief-task052"}],
                "statements": [{"id": "statement:task052-observation", "posture": "observation", "text": "The synthetic reviewed observation is explicitly bounded.", "authority_ref": "authority:synthetic-upstream", "upstream_refs": ["external:task052"], "communication_functions": ["orient"]}],
                "sections": [{"id": "section:task052", "title": "Synthetic observation", "children": ["statement:task052-observation"]}],
                "relations": [],
                "obligations": [{"id": "obligation:task052-provenance", "kind": "provenance-visible", "authority_ref": "authority:presentation-task052", "target_refs": ["statement:task052-observation"]}],
                "renderer_requirements": [{
                    "id": "requirement:task052-static-html", "capability": "capability:bounded-static-html", "mandatory": True,
                    "criticality": "required",
                    "target_refs": ["purpose:candidate-task052", "statement:task052-observation", "obligation:task052-provenance"],
                    "authority_label_refs": ["authority:synthetic-upstream", "authority:presentation-task052"],
                    "caveat_refs": [],
                    "required_constraints": ["authority-and-provenance-links", "encounter-order", "escaped-semantic-text", "offline", "obligation-visibility", "single-regular-html", "standalone"],
                    "permitted_transformations": [], "fallback_refs": [], "unsupported_allowed": False,
                }],
                "fallbacks": [], "selection_sets": [],
                "scope": "One static synthetic presentation.", "non_scope": "No analysis, live data, discovery, or distribution.",
            },
        )
        return author_candidate_bundle(brief=brief, material=material, candidate=candidate)

    def _inputs(self):
        release_helper = release_tests.PublicationReleaseProductionTests("test_complete_governed_ready_produces_exact_deterministic_immutable_release")
        snapshot = release_helper._snapshot("task052", 1)
        bcrp = self._candidate(snapshot)
        legacy_helper = compatibility_tests.LegacyCompatibilityContractTests("test_complete_synthetic_legacy_closure_maps_successfully")
        legacy_candidate, legacy_judgment, legacy_ready = legacy_helper._legacy_closure("task052", 1)
        mapped = map_legacy_ready_to_bcrp(
            legacy_candidate=legacy_candidate,
            legacy_judgment=legacy_judgment,
            legacy_ready=legacy_ready,
            bcrp_candidate_bundle=bcrp,
            mapping=legacy_helper._mapping(legacy_candidate, bcrp, suffix="task052"),
        )
        release_authorization = release_helper._authorization(mapped, snapshot, "task052")
        release = produce_publication_release(
            governed_ready=mapped, evidence_snapshot=snapshot, authorization=release_authorization,
            publication_identity=release_authorization.publication_identity,
            publication_version=release_authorization.publication_version,
            release_identity=release_authorization.release_identity,
            release_time=release_authorization.release_time,
            distribution_constraints=release_authorization.release_distribution_constraints,
            includes_recommendations=False,
        )
        claim = CapabilityClaim(
            "capability:bounded-static-html", "native",
            ("authority-and-provenance-links", "encounter-order", "escaped-semantic-text", "offline", "obligation-visibility", "single-regular-html", "standalone"), True,
        )
        declaration_base = dict(
            identity="renderer-capability:minimal-html-task052",
            contract_identity=CAPABILITY_DECLARATION_CONTRACT,
            capability_profile_identity=ACCEPTED_DECLARATION_PROFILE_ID,
            capability_profile_version=ACCEPTED_DECLARATION_PROFILE_VERSION,
            renderer_identity=FIXED_RENDERER_IDENTITY,
            renderer_version=html_renderer_contract().identity.version,
            renderer_owner="project:BriefForge", renderer_role="bounded-publication-renderer",
            declaration_time="2026-07-17T08:00:00Z", inventory_complete=True,
            capabilities=(claim,), unsupported_capabilities=(),
            declared_constraints=("no-external-assets", "no-runtime-detection", "single-regular-html", "standalone-only"), extensions=(),
        )
        provisional = RendererCapabilityDeclaration(**declaration_base, fingerprint="")
        declaration = replace(provisional, fingerprint=compute_capability_declaration_fingerprint(provisional))
        planning_helper = planning_tests.RendererCompatibilityPlanningTests("test_native_success_is_deterministic_immutable_and_complete")
        lifecycle_scope = planning_helper._scope(release)
        planning_authorization = planning_helper._authorization(release, declaration, "task052")
        plan_result = produce_renderer_compatibility_plan(
            verified_release=release, evidence_snapshot=snapshot, lifecycle_scope=lifecycle_scope,
            declaration=declaration, authorization=planning_authorization,
        )
        self.assertFalse(plan_result.blocked)
        return snapshot, release, lifecycle_scope, declaration, planning_authorization, plan_result.plan

    def _authorization(self, inputs, output_directory, **changes):
        snapshot, release, scope, declaration, planning_authorization, plan = inputs
        projection = build_minimal_html_projection(
            verified_release=release, evidence_snapshot=snapshot, lifecycle_scope=scope,
            declaration=declaration, planning_authorization=planning_authorization, verified_plan=plan,
        )
        contract = html_renderer_contract()
        base = dict(
            identity="renderer-invocation-authorization:task052", policy_identity=CONTROLLED_INVOCATION_POLICY_ID,
            authority_identity=ACCEPTED_INVOCATION_AUTHORITY_IDENTITY,
            authority_owner=ACCEPTED_INVOCATION_AUTHORITY_OWNER,
            authority_role=ACCEPTED_INVOCATION_AUTHORITY_ROLE,
            authorization_time="2026-07-17T10:03:00Z",
            release_identity=release.release.identity, release_fingerprint=release.fingerprint.digest,
            lifecycle_inventory_digest=scope.inventory_digest,
            plan_identity=plan.plan.identity, plan_fingerprint=plan.fingerprint.digest,
            capability_identity=declaration.identity, capability_fingerprint=declaration.fingerprint,
            renderer_identity=FIXED_RENDERER_IDENTITY, renderer_adapter_id=contract.identity.adapter_id,
            renderer_version=contract.identity.version,
            renderer_implementation_digest=renderer_implementation_digest(),
            projection_fingerprint=projection.fingerprint,
            authorization_ledger_directory=self._ledger_directory(output_directory),
            output_directory=str(Path(output_directory).resolve()), output_filename="publication.html",
            output_count=1, maximum_output_bytes=1_000_000, media_type="text/html",
            environment=(
                ("LANG", "C"), ("LC_ALL", "C"), ("TZ", "UTC"),
                ("PYTHONDONTWRITEBYTECODE", "1"), ("PYTHONHASHSEED", "0"), ("PYTHONUTF8", "1"),
            ),
            external_assets=(), invocation_mode="one-artifact-with-determinism-replay",
            timeout_seconds=2, evidence_filename="invocation-evidence.json",
        )
        base.update(changes)
        provisional = RendererInvocationAuthorization(**base, fingerprint="")
        return replace(provisional, fingerprint=compute_invocation_authorization_fingerprint(provisional))

    def _invoke(self, inputs, output_directory, authorization=None):
        snapshot, release, scope, declaration, planning_authorization, plan = inputs
        authorization = authorization or self._authorization(inputs, output_directory)
        return invoke_controlled_renderer(
            verified_release=release, evidence_snapshot=snapshot, lifecycle_scope=scope,
            declaration=declaration, planning_authorization=planning_authorization,
            verified_plan=plan, authorization=authorization,
        )

    def test_exact_fixed_renderer_succeeds_deterministically_and_reload_verifies(self):
        inputs = self._inputs()
        with tempfile.TemporaryDirectory() as directory:
            result = self._invoke(inputs, directory)
            self.assertFalse(result.blocked)
            self.assertEqual(result.findings, ())
            verified = result.verified
            self.assertEqual(verified.artifact_bytes[:15], b"<!doctype html>")
            self.assertEqual(len(verified.bundle.records), 9)
            self.assertEqual(len(verified.bundle.records_of_kind("GeneratedArtifactAuditRecord")), 1)
            self.assertFalse(verified.bundle.records_of_kind("SemanticArtifactConformanceRecord"))
            self.assertFalse(verified.bundle.records_of_kind("PublicationManifestRecord"))
            reloaded = verify_persisted_renderer_invocation(
                artifact_path=Path(directory) / "publication.html",
                evidence_path=Path(directory) / "invocation-evidence.json",
                evidence_snapshot=inputs[0], lifecycle_scope=inputs[2], declaration=inputs[3],
                planning_authorization=inputs[4], authorization=self._authorization(inputs, directory),
            )
            self.assertEqual(reloaded.fingerprint, verified.fingerprint)
            payload = reloaded.bundle.one("GeneratedArtifactAuditRecord").extensions[0]["payload"]
            self.assertEqual(payload["semantic_conformance"], "unassessed")
            self.assertEqual(payload["manifest_authority"], "absent")
            self.assertEqual(payload["distribution_authority"], "absent")
            self.assertEqual(payload["successful_publication"], "not-asserted")
            self.assertEqual(payload["execution_digests"][0], payload["execution_digests"][1])

    def test_authorization_is_exact_and_not_reusable(self):
        inputs = self._inputs()
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as other:
            valid = self._authorization(inputs, directory)
            variants = (
                replace(valid, renderer_version="9.9.9"),
                replace(valid, renderer_implementation_digest="0" * 64),
                replace(valid, plan_fingerprint="0" * 64),
                replace(valid, output_directory=str(Path(other).resolve())),
                replace(valid, output_filename="../escape.html"),
                replace(valid, media_type="application/json"),
                replace(valid, external_assets=("https://example.invalid/x",)),
                replace(valid, fingerprint="0" * 64),
            )
            for variant in variants:
                with self.subTest(variant=variant):
                    result = self._invoke(inputs, directory, variant)
                    self.assertTrue(result.blocked)
                    self.assertIsNone(result.verified)
            self.assertEqual(tuple(Path(directory).iterdir()), ())

            successful = self._invoke(inputs, directory, valid)
            self.assertFalse(successful.blocked)
            marker = Path(valid.authorization_ledger_directory) / f"{valid.fingerprint}.consumed"
            self.assertEqual(marker.read_bytes(), valid.fingerprint.encode("ascii"))
            for path in Path(directory).iterdir():
                path.unlink()
            Path(directory).rmdir()
            Path(directory).mkdir()
            reused = self._invoke(inputs, directory, valid)
            self.assertTrue(reused.blocked)
            self.assertIn("authorization-reused", {item.code for item in reused.findings})
            self.assertEqual(tuple(Path(directory).iterdir()), ())

    def test_mutated_release_scope_plan_declaration_or_authorization_blocks_before_output(self):
        inputs = self._inputs()
        for index in (1, 2, 3, 5):
            altered = list(inputs)
            altered[index] = deepcopy(altered[index])
            if index == 1:
                altered[index] = replace(
                    altered[index],
                    _bundle_document=altered[index]._bundle_document.replace(
                        "2026-07-16T12:04:00Z", "2026-07-17T11:00:00Z"
                    ),
                )
            elif index == 2:
                altered[index] = replace(altered[index], inventory_digest="0" * 64)
            elif index == 3:
                altered[index] = replace(altered[index], fingerprint="0" * 64)
            else:
                altered[index] = replace(
                    altered[index],
                    _bundle_document=altered[index]._bundle_document.replace('"supported":true', '"supported":false'),
                )
            with tempfile.TemporaryDirectory() as directory:
                result = self._invoke(tuple(altered), directory, self._authorization(inputs, directory))
                self.assertTrue(result.blocked)
                self.assertIsNone(result.verified)
                self.assertEqual(tuple(Path(directory).iterdir()), ())

    def test_nondeterministic_or_oversized_renderer_output_has_no_success_evidence(self):
        inputs = self._inputs()
        with tempfile.TemporaryDirectory() as directory:
            from briefforge import controlled_renderer_invocation as module
            real = module._render_in_subprocess
            calls = 0
            def varying(projection, timeout_seconds, work_directory, renderer_digest):
                nonlocal calls
                calls += 1
                output = real(projection, timeout_seconds, work_directory, renderer_digest)
                return output + (b"x" if calls == 2 else b"")
            with patch.object(module, "_render_in_subprocess", varying):
                result = self._invoke(inputs, directory)
            self.assertTrue(result.blocked)
            self.assertIsNone(result.verified)
            self.assertEqual(tuple(Path(directory).iterdir()), ())
        with tempfile.TemporaryDirectory() as directory:
            auth = self._authorization(inputs, directory, maximum_output_bytes=8)
            auth = replace(auth, fingerprint=compute_invocation_authorization_fingerprint(replace(auth, fingerprint="")))
            result = self._invoke(inputs, directory, auth)
            self.assertTrue(result.blocked)
            self.assertEqual(tuple(Path(directory).iterdir()), ())

    def test_actual_child_timeout_terminates_without_output(self):
        inputs = self._inputs()
        from briefforge import controlled_renderer_invocation as module

        projection = build_minimal_html_projection(
            verified_release=inputs[1], evidence_snapshot=inputs[0], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
        )
        with tempfile.TemporaryDirectory() as directory:
            started = time.monotonic()
            with self.assertRaisesRegex(TimeoutError, "timed out"):
                module._render_in_subprocess(
                    projection, 0.001, Path(directory), renderer_implementation_digest()
                )
            self.assertLess(time.monotonic() - started, 4)
            self.assertEqual(tuple(Path(directory).iterdir()), ())

    def test_timeout_exception_auxiliary_output_and_symlink_fail_closed(self):
        inputs = self._inputs()
        from briefforge import controlled_renderer_invocation as module
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(module, "_render_in_subprocess", side_effect=RuntimeError("renderer failure")):
                result = self._invoke(inputs, directory)
            self.assertTrue(result.blocked)
            self.assertIn("renderer-execution-failed", {item.code for item in result.findings})
            self.assertEqual(tuple(Path(directory).iterdir()), ())
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "undeclared.txt").write_text("x", encoding="utf-8")
            result = self._invoke(inputs, directory)
            self.assertTrue(result.blocked)
            self.assertIsNone(result.verified)
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as target:
            authorization = self._authorization(inputs, directory)
            Path(directory).rmdir()
            Path(directory).symlink_to(target, target_is_directory=True)
            result = self._invoke(inputs, directory, authorization)
            self.assertTrue(result.blocked)
            self.assertIsNone(result.verified)

    def test_exactly_two_isolated_renderer_executions_are_attested(self):
        inputs = self._inputs()
        from briefforge import controlled_renderer_invocation as module
        real = module._render_in_subprocess
        working_directories = []
        parent_environment = dict(os.environ)

        def observed(projection, timeout_seconds, work_directory, renderer_digest):
            working_directories.append(work_directory)
            return real(projection, timeout_seconds, work_directory, renderer_digest)

        with tempfile.TemporaryDirectory() as directory:
            with patch.object(module, "_render_in_subprocess", observed):
                result = self._invoke(inputs, directory)
            self.assertFalse(result.blocked)
            self.assertEqual(len(working_directories), 2)
            self.assertEqual(len(set(working_directories)), 2)
            self.assertTrue(all(path.name.startswith("briefforge-task052-") for path in working_directories))
            self.assertEqual(dict(os.environ), parent_environment)
            audit = result.verified.bundle.one("GeneratedArtifactAuditRecord")
            payload = audit.extensions[0]["payload"]
            self.assertEqual(payload["effective_interpreter_controls"], "verified-in-each-independent-execution")
            self.assertEqual(payload["interpreter_flags"], ["-B", "-s", "-S", "-X", "utf8"])

    def test_relative_auxiliary_renderer_write_is_detected_in_isolated_directory(self):
        inputs = self._inputs()
        from briefforge import controlled_renderer_invocation as module
        real = module._render_in_subprocess

        def writes_auxiliary_file(projection, timeout_seconds, work_directory, renderer_digest):
            (work_directory / "undeclared.txt").write_text("x", encoding="utf-8")
            return real(projection, timeout_seconds, work_directory, renderer_digest)

        with tempfile.TemporaryDirectory() as directory:
            with patch.object(module, "_render_in_subprocess", writes_auxiliary_file):
                result = self._invoke(inputs, directory)
            self.assertTrue(result.blocked)
            self.assertIn("renderer-execution-failed", {item.code for item in result.findings})
            self.assertEqual(tuple(Path(directory).iterdir()), ())

    def test_malformed_authorization_runtime_types_fail_with_findings_before_renderer(self):
        inputs = self._inputs()
        from briefforge import controlled_renderer_invocation as module

        malformed_changes = (
            {"output_directory": None},
            {"authorization_ledger_directory": 7},
            {"maximum_output_bytes": True},
            {"timeout_seconds": False},
            {"environment": [["LANG", "C"]]},
            {"external_assets": ["asset"]},
        )
        for changes in malformed_changes:
            with self.subTest(changes=changes), tempfile.TemporaryDirectory() as directory:
                valid = self._authorization(inputs, directory)
                malformed = replace(valid, **changes)
                with patch.object(module, "_render_in_subprocess") as render:
                    result = invoke_controlled_renderer(
                        verified_release=inputs[1], evidence_snapshot=inputs[0], lifecycle_scope=inputs[2],
                        declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
                        authorization=malformed,
                    )
                self.assertTrue(result.blocked)
                self.assertIn("invalid-authorization-field-type", {finding.code for finding in result.findings})
                render.assert_not_called()
                self.assertEqual(tuple(Path(directory).iterdir()), ())

    def test_malformed_authorization_time_blocks_before_renderer_execution(self):
        inputs = self._inputs()
        with tempfile.TemporaryDirectory() as directory:
            invalid = self._authorization(inputs, directory, authorization_time="not-a-time")
            invalid = replace(
                invalid,
                fingerprint=compute_invocation_authorization_fingerprint(replace(invalid, fingerprint="")),
            )
            from briefforge import controlled_renderer_invocation as module
            with patch.object(module, "_render_in_subprocess") as renderer:
                result = self._invoke(inputs, directory, invalid)
            self.assertTrue(result.blocked)
            renderer.assert_not_called()

    def test_noncanonical_evidence_bytes_are_rejected(self):
        inputs = self._inputs()
        with tempfile.TemporaryDirectory() as directory:
            authorization = self._authorization(inputs, directory)
            result = self._invoke(inputs, directory, authorization)
            self.assertFalse(result.blocked)
            evidence_path = Path(directory) / "invocation-evidence.json"
            evidence_path.write_bytes(evidence_path.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "canonical"):
                verify_persisted_renderer_invocation(
                    artifact_path=Path(directory) / "publication.html",
                    evidence_path=evidence_path,
                    evidence_snapshot=inputs[0], lifecycle_scope=inputs[2], declaration=inputs[3],
                    planning_authorization=inputs[4], authorization=authorization,
                )

    def test_atomic_directory_exchange_failure_restores_empty_consumed_destination(self):
        inputs = self._inputs()
        from briefforge import controlled_renderer_invocation as module

        with tempfile.TemporaryDirectory() as directory:
            authorization = self._authorization(inputs, directory)
            with patch.object(module, "_exchange_directories", side_effect=OSError("simulated atomic exchange failure")):
                result = self._invoke(inputs, directory, authorization)
            self.assertTrue(result.blocked)
            self.assertEqual(tuple(Path(directory).iterdir()), ())
            marker = Path(authorization.authorization_ledger_directory) / f"{authorization.fingerprint}.consumed"
            self.assertEqual(marker.read_bytes(), authorization.fingerprint.encode("ascii"))
            self.assertFalse(any(Path(directory).parent.glob(f".{Path(directory).name}.task052-stage-*")))

    def test_staging_name_substitution_is_rejected_and_authorized_output_is_restored(self):
        inputs = self._inputs()
        from briefforge import controlled_renderer_invocation as module
        real_exchange = module._exchange_directories
        displaced = []

        def substitute_then_exchange(parent_fd, staging_name, output_name):
            parent_path = Path(os.readlink(f"/proc/self/fd/{parent_fd}"))
            genuine = parent_path / f"{staging_name}.genuine"
            (parent_path / staging_name).rename(genuine)
            replacement = parent_path / staging_name
            replacement.mkdir()
            (replacement / "publication.html").write_bytes(b"MALICIOUS")
            (replacement / "invocation-evidence.json").write_bytes(b"{}")
            displaced.append(genuine)
            return real_exchange(parent_fd, staging_name, output_name)

        with tempfile.TemporaryDirectory() as directory:
            with patch.object(module, "_exchange_directories", substitute_then_exchange):
                result = self._invoke(inputs, directory)
            self.assertTrue(result.blocked)
            self.assertEqual(tuple(Path(directory).iterdir()), ())
            for path in displaced:
                shutil.rmtree(path, ignore_errors=True)

    def test_postcommit_cleanup_failure_leaves_complete_preverified_pair(self):
        inputs = self._inputs()
        from briefforge import controlled_renderer_invocation as module

        with tempfile.TemporaryDirectory() as directory:
            authorization = self._authorization(inputs, directory)
            with patch.object(module, "_cleanup_exchanged_original", side_effect=OSError("simulated postcommit cleanup failure")):
                result = self._invoke(inputs, directory, authorization)
            self.assertTrue(result.blocked)
            self.assertEqual({path.name for path in Path(directory).iterdir()}, {"publication.html", "invocation-evidence.json"})
            verify_persisted_renderer_invocation(
                artifact_path=Path(directory) / "publication.html",
                evidence_path=Path(directory) / "invocation-evidence.json",
                evidence_snapshot=inputs[0], lifecycle_scope=inputs[2], declaration=inputs[3],
                planning_authorization=inputs[4], authorization=authorization,
            )

    def test_persisted_artifact_and_evidence_tampering_are_independently_rejected(self):
        inputs = self._inputs()
        with tempfile.TemporaryDirectory() as directory:
            self._invoke(inputs, directory)
            artifact_path = Path(directory) / "publication.html"
            evidence_path = Path(directory) / "invocation-evidence.json"
            artifact_path.write_bytes(artifact_path.read_bytes() + b"x")
            with self.assertRaises(ValueError):
                verify_persisted_renderer_invocation(
                    artifact_path=artifact_path, evidence_path=evidence_path,
                    evidence_snapshot=inputs[0], lifecycle_scope=inputs[2], declaration=inputs[3],
                    planning_authorization=inputs[4], authorization=self._authorization(inputs, directory),
                )
        with tempfile.TemporaryDirectory() as directory:
            self._invoke(inputs, directory)
            evidence_path = Path(directory) / "invocation-evidence.json"
            document = json.loads(evidence_path.read_text(encoding="utf-8"))
            document["records"][8]["extensions"][0]["payload"]["semantic_conformance"] = "passed"
            evidence_path.write_text(json.dumps(document, sort_keys=True, separators=(",", ":")), encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_persisted_renderer_invocation(
                    artifact_path=Path(directory) / "publication.html", evidence_path=evidence_path,
                    evidence_snapshot=inputs[0], lifecycle_scope=inputs[2], declaration=inputs[3],
                    planning_authorization=inputs[4], authorization=self._authorization(inputs, directory),
                )

    def test_coordinated_artifact_and_evidence_forgery_is_rejected_by_external_admission_commitment(self):
        inputs = self._inputs()
        with tempfile.TemporaryDirectory() as directory:
            authorization = self._authorization(inputs, directory)
            result = self._invoke(inputs, directory, authorization)
            self.assertFalse(result.blocked)
            artifact_path = Path(directory) / "publication.html"
            evidence_path = Path(directory) / "invocation-evidence.json"
            original = artifact_path.read_bytes()
            forged = original.replace(
                b"The synthetic reviewed observation is explicitly bounded.",
                b"The forged reviewed observation is explicitly bounded.",
                1,
            )
            self.assertNotEqual(forged, original)
            artifact_path.write_bytes(forged)
            import hashlib
            digest = hashlib.sha256(forged).hexdigest()
            document = json.loads(evidence_path.read_text(encoding="utf-8"))
            audit = document["records"][8]
            audit["semantic"]["artifact"]["sha256"] = digest
            audit["semantic"]["artifact"]["byte_length"] = len(forged)
            payload = audit["extensions"][0]["payload"]
            payload["output_inventory"][0]["sha256"] = digest
            payload["output_inventory"][0]["byte_length"] = len(forged)
            payload["execution_digests"] = [digest, digest]
            payload["execution_byte_lengths"] = [len(forged), len(forged)]
            evidence_path.write_text(
                json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "commitment|admission"):
                verify_persisted_renderer_invocation(
                    artifact_path=artifact_path, evidence_path=evidence_path,
                    evidence_snapshot=inputs[0], lifecycle_scope=inputs[2], declaration=inputs[3],
                    planning_authorization=inputs[4], authorization=authorization,
                )

    def test_staged_file_mutation_between_verification_and_exchange_is_rejected(self):
        inputs = self._inputs()
        from briefforge import controlled_renderer_invocation as module
        real_exchange = module._exchange_directories

        def mutate_then_exchange(parent_fd, staging_name, output_name):
            parent_path = Path(os.readlink(f"/proc/self/fd/{parent_fd}"))
            (parent_path / staging_name / "publication.html").write_bytes(
                b"<!doctype html><html><body>mutated in place</body></html>"
            )
            return real_exchange(parent_fd, staging_name, output_name)

        with tempfile.TemporaryDirectory() as directory:
            with patch.object(module, "_exchange_directories", mutate_then_exchange):
                result = self._invoke(inputs, directory)
            self.assertTrue(result.blocked)
            self.assertEqual(tuple(Path(directory).iterdir()), ())

    def test_generated_artifact_audit_uses_valid_extension_envelope(self):
        inputs = self._inputs()
        with tempfile.TemporaryDirectory() as directory:
            result = self._invoke(inputs, directory)
            self.assertFalse(result.blocked)
            audit = result.verified.bundle.one("GeneratedArtifactAuditRecord")
            extension = audit.extensions[0]
            self.assertEqual(extension["criticality"], "required")
            self.assertEqual(extension["preservation"], "must-preserve")
            validation = validate_bundle(result.verified.bundle, through_layer="L5")
            malformed = [
                finding for finding in validation.findings
                if finding.semantic_identity == audit.identity and finding.family != "extension-boundary"
            ]
            self.assertEqual(malformed, [])

    def test_withdrawn_superseded_incomplete_lifecycle_and_mapping_drift_block_before_renderer(self):
        inputs = self._inputs()
        from briefforge import controlled_renderer_invocation as module

        incomplete_scope = replace(inputs[2], inventory_complete=False)
        lifecycle_variants = [incomplete_scope]
        binding = release_tests.release_binding_from_verified_release(inputs[1])
        policy = planning_tests.lifecycle_tests.policy()
        withdrawal = planning_tests.lifecycle_tests.withdrawal_document(
            identity="lifecycle-event:task052-withdrawal",
            target_identity=binding.identity,
            target_fingerprint=binding.fingerprint,
            time="2026-07-18T10:00:00Z",
        )
        withdrawal["semantic"]["publication_identity"] = binding.publication_identity
        lifecycle_variants.append(planning_tests.RendererCompatibilityPlanningTests("test_withdrawn_superseded_and_ambiguous_lifecycle_states_reject")._scope(
            inputs[1], events=(planning_tests.event_from_document(withdrawal),), policies=(policy,)
        ))
        successor = replace(
            binding,
            identity="release:task052-v2",
            fingerprint="b" * 64,
            fingerprint_root_identity="release:task052-v2",
            semantic_publication_version="2.0.0",
            publication_time="2026-07-18T08:00:00Z",
        )
        supersession = planning_tests.lifecycle_tests.event_document(
            identity="lifecycle-event:task052-supersession",
            target_identity=binding.identity,
            target_fingerprint=binding.fingerprint,
            predecessor_identity=binding.identity,
            predecessor_fingerprint=binding.fingerprint,
            successor_identity=successor.identity,
            successor_fingerprint=successor.fingerprint,
            time="2026-07-18T10:00:00Z",
        )
        supersession["semantic"]["publication_identity"] = binding.publication_identity
        lifecycle_variants.append(planning_tests.RendererCompatibilityPlanningTests("test_withdrawn_superseded_and_ambiguous_lifecycle_states_reject")._scope(
            inputs[1], events=(planning_tests.event_from_document(supersession),),
            releases=(binding, successor), policies=(policy,)
        ))

        for altered_scope in lifecycle_variants:
            with self.subTest(scope=altered_scope), tempfile.TemporaryDirectory() as directory:
                altered = (inputs[0], inputs[1], altered_scope, inputs[3], inputs[4], inputs[5])
                with patch.object(module, "_render_in_subprocess") as renderer:
                    result = self._invoke(altered, directory, self._authorization(inputs, directory))
                self.assertTrue(result.blocked)
                renderer.assert_not_called()
                self.assertEqual(tuple(Path(directory).iterdir()), ())

        mappings = list(inputs[5].mappings)
        mapping_variants = (
            [],
            mappings + mappings,
            mappings + [{**mappings[0], "requirement_id": "requirement:unplanned"}],
            [{**mappings[0], "selected_expression_mode": "fallback"}],
        )
        for changed_mappings in mapping_variants:
            altered_plan = replace(
                inputs[5],
                mappings_document=json.dumps(changed_mappings, sort_keys=True, separators=(",", ":")),
            )
            altered = (inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], altered_plan)
            with self.subTest(mappings=changed_mappings), tempfile.TemporaryDirectory() as directory:
                with patch.object(module, "_render_in_subprocess") as renderer:
                    result = self._invoke(altered, directory, self._authorization(inputs, directory))
                self.assertTrue(result.blocked)
                renderer.assert_not_called()
                self.assertEqual(tuple(Path(directory).iterdir()), ())

    def test_html_media_and_external_resource_policy_fails_closed(self):
        inputs = self._inputs()
        prefix = b'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        suffix = b'\n</head>\n<body><main>bounded</main></body>\n</html>'
        attacks = (
            b"not html",
            b"\xff\xfe",
            (prefix + b"<title>x</title>" + suffix).replace(b"\n", b"\r\n"),
            prefix + b"<title>x</title><script>alert(1)</script>" + suffix,
            prefix + b'<title>x</title><img srcset="https://evil.invalid/a 1x">' + suffix,
            prefix + b'<title>x</title><form action="https://evil.invalid/"></form>' + suffix,
            prefix + b'<title>x</title><a href="javascript:alert(1)">x</a>' + suffix,
            prefix + b'<title>x</title><meta http-equiv="refresh" content="0;url=https://evil.invalid/">' + suffix,
            prefix + b'<title>x</title><div onclick="alert(1)">x</div>' + suffix,
            prefix + b"<title>x</title><style>@import 'https://evil.invalid/a.css';</style>" + suffix,
            prefix + b"<title>x</title><style>body{background:url(https://evil.invalid/a)}</style>" + suffix,
        )
        from briefforge import controlled_renderer_invocation as module

        for attack in attacks:
            with self.subTest(attack=attack[:60]), tempfile.TemporaryDirectory() as directory:
                with patch.object(module, "_render_in_subprocess", return_value=attack):
                    result = self._invoke(inputs, directory)
                self.assertTrue(result.blocked)
                self.assertEqual(tuple(Path(directory).iterdir()), ())
                self.assertFalse(any(finding.code == "renderer-nondeterministic" for finding in result.findings))

    def test_malformed_evidence_identity_and_loaded_helper_graph_drift_fail_closed(self):
        inputs = self._inputs()
        from briefforge import controlled_renderer_invocation as module
        from briefforge import renderer_adapter

        with tempfile.TemporaryDirectory() as directory:
            malformed = self._authorization(inputs, directory, identity="not canonical")
            with patch.object(module, "_render_in_subprocess") as renderer:
                result = self._invoke(inputs, directory, malformed)
            self.assertTrue(result.blocked)
            renderer.assert_not_called()
            self.assertEqual(tuple(Path(directory).iterdir()), ())

        original_digest = renderer_implementation_digest()
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(renderer_adapter, "_html_text", lambda value: str(value)):
                substituted_digest = renderer_implementation_digest()
                self.assertNotEqual(substituted_digest, original_digest)
                authorization = self._authorization(inputs, directory)
            with patch.object(module, "_render_in_subprocess") as renderer:
                result = self._invoke(inputs, directory, authorization)
            self.assertTrue(result.blocked)
            renderer.assert_not_called()
            self.assertEqual(tuple(Path(directory).iterdir()), ())
        with patch.object(renderer_adapter, "_html_text", _CallableRendererHelper()):
            with self.assertRaisesRegex(ValueError, "unsupported executable binding"):
                renderer_implementation_digest()

    def test_projection_uses_no_legacy_ready_and_consumes_all_plan_mappings_once(self):
        inputs = self._inputs()
        projection = build_minimal_html_projection(
            verified_release=inputs[1], evidence_snapshot=inputs[0], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
        )
        self.assertEqual(projection.consumed_mapping_ids, ("requirement:task052-static-html",))
        self.assertEqual(projection.selected_expression_modes, ("native",))
        self.assertEqual(projection.statements[0].encounter_meaning, "The synthetic reviewed observation is explicitly bounded.")
        self.assertEqual(projection.statements[0].authority_ref, "authority:synthetic-upstream")
        self.assertEqual(projection.upstream_references[0].provenance_ref, "provenance:task052")
        self.assertEqual(projection.obligations[0].authority_ref, "authority:presentation-task052")
        self.assertEqual(
            projection.upstream_references[0].provenance_citation,
            "Synthetic governed evidence constructed for TASK-052.",
        )
        self.assertNotIn("ReadyPresentationPackage", {base.__name__ for base in type(projection).__mro__})


if __name__ == "__main__":
    unittest.main()
