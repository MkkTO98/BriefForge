"""TASK-060 adversarial RED tests for one-act and local security boundaries.

These tests are intentionally narrower than the representative acceptance corpus:
they exercise authorization identity uniqueness, TOCTOU-resistant filesystem use,
complete executable digests, failure durability, and the HTML parser allowlist.
All probes use synthetic data and temporary local directories only.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from briefforge.representative_renderer import render_representative_html
from tests import test_task060_representative_chain as chain_tests


class Task060AuthorityFilesystemDigestParserSecurityTests(unittest.TestCase):
    def _helper(self):
        return chain_tests.RepresentativeAuthorityChainTests(
            "test_authorization_contracts_are_complete_one_act_authority_bindings"
        )

    def _invocation_case(self, root: Path):
        helper = self._helper()
        inputs = helper._inputs()
        output = root / "artifact"
        evidence = root / "invoke"
        output.mkdir()
        evidence.mkdir()
        authorization = helper._current_invocation_authorization(inputs, output, evidence)
        return helper, inputs, output, evidence, authorization

    @staticmethod
    def _conformance_call(case, authorization):
        helper, inputs, projection, invocation_authorization, invoked, _ = case
        from briefforge.representative_semantic_conformance import (
            assess_representative_semantic_artifact_conformance,
        )
        return assess_representative_semantic_artifact_conformance(
            artifact_path=invoked.artifact_path,
            projection=projection,
            invocation_evidence_path=invoked.evidence_path,
            evidence_snapshot=inputs[0],
            verified_release=inputs[1],
            lifecycle_scope=inputs[2],
            declaration=inputs[3],
            planning_authorization=inputs[4],
            verified_plan=inputs[5],
            invocation_authorization=invocation_authorization,
            invocation_evidence_fingerprint=invoked.fingerprint.digest,
            authorization=authorization,
        )

    def _unassessed_conformance_case(self, root: Path):
        helper, inputs, _, _, invocation_authorization = self._invocation_case(root)
        invoked_result = helper._invoke(inputs, invocation_authorization)
        self.assertFalse(invoked_result.blocked, invoked_result.findings)
        invoked = invoked_result.verified
        projection = helper._projection(inputs)
        evidence = root / "conform"
        evidence.mkdir()
        authorization = helper._current_conformance_authorization(
            inputs, projection, invocation_authorization, invoked, evidence
        )
        return helper, inputs, projection, invocation_authorization, invoked, authorization

    def test_invocation_identity_is_one_act_across_different_fingerprints(self):
        helper = self._helper()
        inputs = helper._inputs()
        with tempfile.TemporaryDirectory() as root_name:
            root = Path(root_name)
            output = root / "artifact"; evidence = root / "invoke"
            output.mkdir(); evidence.mkdir()
            first = helper._current_invocation_authorization(inputs, output, evidence)
            variant = helper._current_invocation_authorization(
                inputs, output, evidence, authorization_time="2026-08-01T09:03:01Z"
            )
            self.assertEqual(first.identity, variant.identity)
            self.assertNotEqual(first.fingerprint, variant.fingerprint)
            accepted = helper._invoke(inputs, first)
            self.assertFalse(accepted.blocked, accepted.findings)
            (output / "brief.html").unlink()
            (evidence / "representative-invocation-evidence.json").unlink()
            rejected = helper._invoke(inputs, variant)
            self.assertTrue(rejected.blocked)
            self.assertIn("identity", " ".join(map(str, rejected.findings)).lower())
            ledger = Path(first.authorization_ledger_directory)
            self.assertFalse((ledger / f"{variant.fingerprint}.consumed").exists())

    def test_invocation_rejects_ledger_alias_with_artifact_or_evidence_directory(self):
        from briefforge import representative_controlled_invocation as module
        for alias in ("artifact", "evidence"):
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as root_name:
                helper, inputs, output, evidence, valid = self._invocation_case(Path(root_name))
                directory = output if alias == "artifact" else evidence
                changed = replace(valid, authorization_ledger_directory=str(directory), fingerprint="")
                changed = replace(changed, fingerprint=module.compute_representative_invocation_authorization_fingerprint(changed))
                result = helper._invoke(inputs, changed)
                self.assertTrue(result.blocked)
                self.assertIn("distinct", " ".join(map(str, result.findings)).lower())

    def test_invocation_authorization_cannot_predate_release_and_plan(self):
        from briefforge import representative_controlled_invocation as module
        with tempfile.TemporaryDirectory() as root_name:
            helper, inputs, _, _, valid = self._invocation_case(Path(root_name))
            stale = replace(valid, authorization_time="2000-01-01T00:00:00Z", fingerprint="")
            stale = replace(stale, fingerprint=module.compute_representative_invocation_authorization_fingerprint(stale))
            result = helper._invoke(inputs, stale)
            self.assertTrue(result.blocked)
            self.assertIn("predates", " ".join(map(str, result.findings)).lower())

    def test_concurrent_invocation_variants_with_one_identity_consume_exactly_one_act(self):
        from briefforge import representative_controlled_invocation as module
        helper = self._helper()
        inputs = helper._inputs()
        with tempfile.TemporaryDirectory() as root_name:
            root = Path(root_name)
            output = root / "artifact"; evidence = root / "invoke"
            output.mkdir(); evidence.mkdir()
            authorizations = tuple(
                helper._current_invocation_authorization(
                    inputs, output, evidence,
                    authorization_time=f"2026-08-01T09:03:0{index}Z",
                ) for index in (1, 2)
            )
            self.assertEqual(len({a.identity for a in authorizations}), 1)
            self.assertEqual(len({a.fingerprint for a in authorizations}), 2)
            artifact = render_representative_html(helper._projection(inputs))
            with patch.object(module, "render_representative_in_isolation", return_value=artifact):
                with ThreadPoolExecutor(max_workers=2) as pool:
                    results = tuple(pool.map(lambda a: helper._invoke(inputs, a), authorizations))
            ledger = Path(authorizations[0].authorization_ledger_directory)
            consumed = tuple(ledger.glob("*.consumed"))
            admitted = tuple(ledger.glob("*.admitted"))
            self.assertEqual(sum(not result.blocked for result in results), 1)
            self.assertEqual(len(consumed), 1, "one identity must have one durable consumption fact")
            self.assertEqual(len(admitted), 1)

    def test_conformance_identity_is_one_act_across_different_fingerprints(self):
        with tempfile.TemporaryDirectory() as root_name:
            root = Path(root_name)
            case = self._unassessed_conformance_case(root)
            valid = case[-1]
            variant = replace(valid, authorization_time="2026-08-01T09:04:01Z", fingerprint="")
            from briefforge.representative_semantic_conformance import (
                compute_representative_conformance_authorization_fingerprint,
            )
            variant = replace(
                variant,
                fingerprint=compute_representative_conformance_authorization_fingerprint(variant),
            )
            self.assertEqual(valid.identity, variant.identity)
            self.assertNotEqual(valid.fingerprint, variant.fingerprint)
            self.assertFalse(self._conformance_call(case, valid).blocked)
            replay = self._conformance_call(case, variant)
            self.assertTrue(replay.blocked)
            codes = {finding.code for finding in replay.findings}
            self.assertIn("assessment-authorization-identity-consumed", codes)
            ledger = Path(valid.commitment_ledger_directory)
            self.assertFalse((ledger / f"{variant.fingerprint}.conformance-assessment-consumed").exists())

    def test_conformance_authorization_cannot_predate_invocation(self):
        from briefforge import representative_semantic_conformance as module
        with tempfile.TemporaryDirectory() as root_name:
            case = self._unassessed_conformance_case(Path(root_name))
            valid = case[-1]
            stale = replace(valid, authorization_time="2000-01-01T00:00:00Z", fingerprint="")
            stale = replace(stale, fingerprint=module.compute_representative_conformance_authorization_fingerprint(stale))
            result = self._conformance_call(case, stale)
            self.assertTrue(result.blocked)
            self.assertIn("conformance-time-contradiction", {finding.code for finding in result.findings})

    def test_concurrent_conformance_variants_with_one_identity_consume_exactly_one_act(self):
        from briefforge import representative_semantic_conformance as module
        with tempfile.TemporaryDirectory() as root_name:
            root = Path(root_name)
            case = self._unassessed_conformance_case(root)
            base = case[-1]
            authorizations = []
            for second in (1, 2):
                item = replace(base, authorization_time=f"2026-08-01T09:04:0{second}Z", fingerprint="")
                item = replace(item, fingerprint=module.compute_representative_conformance_authorization_fingerprint(item))
                authorizations.append(item)
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = tuple(pool.map(lambda a: self._conformance_call(case, a), authorizations))
            ledger = Path(base.commitment_ledger_directory)
            consumed = tuple(ledger.glob("*.conformance-assessment-consumed"))
            commitments = tuple(ledger.glob("*.conformance-admitted"))
            self.assertEqual(sum(not result.blocked for result in results), 1)
            self.assertEqual(len(consumed), 1, "one identity must have one durable assessment fact")
            self.assertEqual(len(commitments), 1)

    def test_invocation_directory_symlink_swaps_never_touch_outside_destinations(self):
        """Swap each authorized directory at the final write seam, after path validation."""
        from briefforge import representative_controlled_invocation as module

        for target in ("output", "evidence", "ledger", "commitment"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as root_name:
                root = Path(root_name)
                helper, inputs, output, evidence, authorization = self._invocation_case(root)
                outside = root / "outside"; outside.mkdir()
                outside_sentinel = outside / "sentinel"
                outside_sentinel.write_bytes(b"outside-must-not-change")
                original_inventory = {p.name: p.read_bytes() for p in outside.iterdir()}
                real_write = module._write_exclusive_at
                swapped = False
                observed_outside_write = False

                def swap_then_write(directory_fd, name, data, *args):
                    nonlocal swapped, observed_outside_write
                    is_target = (
                        (target == "output" and name == "brief.html") or
                        (target == "evidence" and name == "representative-invocation-evidence.json") or
                        (target == "ledger" and name.endswith(".consumed")) or
                        (target == "commitment" and name.endswith(".admitted"))
                    )
                    if is_target and not swapped:
                        parent = (output if target == "output" else evidence if target == "evidence"
                                  else Path(authorization.authorization_ledger_directory))
                        displaced = parent.with_name(parent.name + "-authorized-original")
                        parent.rename(displaced)
                        parent.symlink_to(outside, target_is_directory=True)
                        swapped = True
                    result = real_write(directory_fd, name, data)
                    if swapped and (outside / name).exists():
                        observed_outside_write = True
                    return result

                artifact = render_representative_html(helper._projection(inputs))
                with patch.object(module, "_write_exclusive_at", side_effect=swap_then_write), \
                     patch.object(module, "render_representative_in_isolation", return_value=artifact):
                    result = helper._invoke(inputs, authorization)
                self.assertTrue(result.blocked)
                self.assertTrue(swapped, "probe did not reach its intended write seam")
                self.assertFalse(observed_outside_write, "an authorized-path swap caused an outside write")
                self.assertEqual(
                    {p.name: p.read_bytes() for p in outside.iterdir()}, original_inventory,
                    "outside content was written or deleted during rollback",
                )

    def test_persisted_verifiers_do_not_follow_swapped_artifact_evidence_or_ledger_directories(self):
        from briefforge.representative_controlled_invocation import (
            verify_persisted_representative_renderer_invocation,
        )
        from briefforge.representative_semantic_conformance import (
            verify_persisted_representative_semantic_artifact_conformance,
        )
        for target in ("artifact", "invocation-evidence", "conformance-evidence", "ledger"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as root_name:
                root = Path(root_name)
                helper = self._helper()
                complete = helper._real_v2_conformance(root)
                inputs, projection, invocation_authorization, invoked, conformance_authorization, _ = complete
                if target == "artifact":
                    directory, source = invoked.artifact_path.parent, invoked.artifact_path
                elif target == "invocation-evidence":
                    directory, source = invoked.evidence_path.parent, invoked.evidence_path
                elif target == "conformance-evidence":
                    source = Path(conformance_authorization.evidence_directory) / conformance_authorization.evidence_filename
                    directory = source.parent
                else:
                    directory = Path(conformance_authorization.commitment_ledger_directory)
                    source = next(directory.iterdir())
                outside = root / "outside"; outside.mkdir()
                (outside / source.name).write_bytes(source.read_bytes())
                sentinel = outside / "outside-sentinel"; sentinel.write_bytes(b"unread-and-undeleted")
                displaced = directory.with_name(directory.name + "-verified-original")
                directory.rename(displaced)
                directory.symlink_to(outside, target_is_directory=True)
                if target in {"artifact", "invocation-evidence"}:
                    with self.assertRaises(Exception):
                        verify_persisted_representative_renderer_invocation(
                            artifact_path=invoked.artifact_path,
                            evidence_path=invoked.evidence_path,
                            verified_release=inputs[1], evidence_snapshot=inputs[0],
                            lifecycle_scope=inputs[2], declaration=inputs[3],
                            planning_authorization=inputs[4], verified_plan=inputs[5],
                            authorization=invocation_authorization,
                        )
                else:
                    with self.assertRaises(Exception):
                        verify_persisted_representative_semantic_artifact_conformance(
                            artifact_path=invoked.artifact_path, projection=projection,
                            invocation_evidence_path=invoked.evidence_path,
                            evidence_snapshot=inputs[0], verified_release=inputs[1],
                            lifecycle_scope=inputs[2], declaration=inputs[3],
                            planning_authorization=inputs[4], verified_plan=inputs[5],
                            invocation_authorization=invocation_authorization,
                            invocation_evidence_fingerprint=invoked.fingerprint.digest,
                            authorization=conformance_authorization,
                        )
                self.assertEqual(sentinel.read_bytes(), b"unread-and-undeleted")

    def test_invocation_post_write_failures_leave_no_usable_admission_and_preserve_consumption(self):
        from briefforge import representative_controlled_invocation as module
        for failure_point in ("commitment", "artifact", "evidence"):
            with self.subTest(failure_point=failure_point), tempfile.TemporaryDirectory() as root_name:
                root = Path(root_name)
                helper, inputs, output, evidence, authorization = self._invocation_case(root)
                real_write = module._write_exclusive_at

                def write_then_crash(directory_fd, name, data, *args):
                    matches = (
                        (failure_point == "commitment" and name.endswith(".admitted")) or
                        (failure_point == "artifact" and name == "brief.html") or
                        (failure_point == "evidence" and name == "representative-invocation-evidence.json")
                    )
                    if matches:
                        if failure_point == "commitment":
                            raise OSError("simulated failure before final admission")
                        real_write(directory_fd, name, data, *args)
                        raise OSError(f"simulated crash after durable {failure_point} write")
                    return real_write(directory_fd, name, data, *args)

                artifact = render_representative_html(helper._projection(inputs))
                with patch.object(module, "_write_exclusive_at", side_effect=write_then_crash), \
                     patch.object(module, "render_representative_in_isolation", return_value=artifact):
                    result = helper._invoke(inputs, authorization)
                self.assertTrue(result.blocked)
                ledger = Path(authorization.authorization_ledger_directory)
                identity_key = hashlib.sha256(authorization.identity.encode("utf-8")).hexdigest()
                marker = ledger / f"{identity_key}.consumed"
                self.assertEqual(marker.read_bytes(), authorization.fingerprint.encode("ascii"))
                self.assertFalse((ledger / f"{identity_key}.admitted").exists())

    def test_conformance_post_write_failures_leave_no_usable_admission(self):
        from briefforge import representative_semantic_conformance as module
        for failure_point in ("evidence", "commitment"):
            with self.subTest(failure_point=failure_point), tempfile.TemporaryDirectory() as root_name:
                root = Path(root_name)
                case = self._unassessed_conformance_case(root)
                authorization = case[-1]
                real_write = module._write_exclusive_at

                def write_then_crash(directory_fd, name, data, *args):
                    matches = (
                        (failure_point == "evidence" and name == authorization.evidence_filename) or
                        (failure_point == "commitment" and name.endswith(".conformance-admitted"))
                    )
                    if matches:
                        if failure_point == "commitment":
                            raise OSError("simulated failure before final admission")
                        real_write(directory_fd, name, data, *args)
                        raise OSError(f"simulated crash after durable {failure_point} write")
                    return real_write(directory_fd, name, data, *args)

                with patch.object(module, "_write_exclusive_at", side_effect=write_then_crash):
                    result = self._conformance_call(case, authorization)
                self.assertTrue(result.blocked)
                evidence_path = Path(authorization.evidence_directory) / authorization.evidence_filename
                ledger = Path(authorization.commitment_ledger_directory)
                identity_key = hashlib.sha256(authorization.identity.encode("utf-8")).hexdigest()
                consumed = ledger / f"{identity_key}.conformance-assessment-consumed"
                commitment = ledger / f"{identity_key}.conformance-admitted"
                self.assertEqual(consumed.read_bytes(), module._consumption_bytes(authorization))
                self.assertTrue(evidence_path.exists())
                self.assertFalse(commitment.exists())

    def test_failed_owned_write_never_unlinks_a_raced_replacement(self):
        from briefforge import representative_controlled_invocation as invocation
        from briefforge import representative_semantic_conformance as conformance
        for module in (invocation, conformance):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as root_name:
                root = Path(root_name); directory_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
                real_write = os.write
                def replace_then_fail(descriptor, data):
                    os.unlink("owned", dir_fd=directory_fd)
                    replacement = os.open("owned", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600,
                                          dir_fd=directory_fd)
                    try: real_write(replacement, b"replacement")
                    finally: os.close(replacement)
                    raise OSError("forced write failure after pathname replacement")
                try:
                    with patch.object(module.os, "write", side_effect=replace_then_fail):
                        with self.assertRaises(OSError):
                            module._write_exclusive_at(directory_fd, "owned", b"payload")
                    self.assertEqual((root / "owned").read_bytes(), b"replacement")
                finally:
                    os.close(directory_fd)

    def test_renderer_digest_binds_every_local_executable_source_in_import_closure(self):
        from briefforge import representative_controlled_invocation as module
        baseline = module.representative_renderer_implementation_digest()
        source_names = (
            "representative_controlled_invocation.py",
            "representative_projection.py",
            "representative_renderer.py",
            "_representative_renderer_worker.py",
            "bcrp/canonical.py",
            "bcrp/model.py",
            "bcrp/validation.py",
            "publication_release.py",
            "renderer_compatibility_planning.py",
        )
        package = Path(module.__file__).parent
        original_read = Path.read_bytes
        for name in source_names:
            target = (package / name).resolve()

            def changed_read(path, *, selected=target):
                data = original_read(path)
                return data + b"\n# adversarial executable-source mutation\n" if path.resolve() == selected else data

            with self.subTest(source=name), patch.object(Path, "read_bytes", changed_read):
                self.assertNotEqual(module.representative_renderer_implementation_digest(), baseline)

    def test_renderer_digest_binds_exact_interpreter_identity(self):
        from briefforge import representative_controlled_invocation as module
        baseline = module.representative_renderer_implementation_digest()
        with patch.object(module.sys, "executable", "/synthetic/other-python"):
            self.assertNotEqual(module.representative_renderer_implementation_digest(), baseline)

    def test_assessor_has_complete_source_closure_and_interpreter_digest(self):
        from briefforge import representative_semantic_conformance as module
        self.assertTrue(
            hasattr(module, "representative_assessor_implementation_digest"),
            "assessor authorization must bind executable source closure, not only a name/version",
        )
        digest = module.representative_assessor_implementation_digest
        baseline = digest()
        self.assertRegex(baseline, r"^[0-9a-f]{64}$")
        target = Path(module.__file__).resolve()
        original_read = Path.read_bytes

        def changed_read(path):
            data = original_read(path)
            return data + b"\n# assessor mutation\n" if path.resolve() == target else data

        with patch.object(Path, "read_bytes", changed_read):
            self.assertNotEqual(digest(), baseline)
        with patch.object(module.sys, "executable", "/synthetic/other-python"):
            self.assertNotEqual(digest(), baseline)

    def test_html_parser_rejects_every_nonallowlisted_tag_and_attribute(self):
        from briefforge import representative_semantic_conformance as module
        helper = self._helper()
        projection = helper._projection(helper._inputs())
        valid = render_representative_html(projection)
        tag_attacks = (
            b"<custom-element>invented</custom-element>",
            b"<form></form>", b"<svg></svg>", b"<math></math>",
            b"<audio></audio>", b"<video></video>", b"<template></template>",
        )
        attribute_attacks = (
            b' class="invented"', b' id="invented"', b' style="display:block"',
            b' data-unknown="invented"', b' aria-label="invented"',
            b' formaction="https://outside.invalid"', b' srcset="https://outside.invalid/a 1x"',
        )
        for markup in tag_attacks:
            attack = valid.replace(b"</main>", markup + b"</main>", 1)
            with self.subTest(tag=markup), self.assertRaises(Exception):
                module._well_formed(attack)
        for attribute in attribute_attacks:
            attack = valid.replace(b"<main>", b"<main" + attribute + b">", 1)
            with self.subTest(attribute=attribute), self.assertRaises(Exception):
                module._well_formed(attack)


if __name__ == "__main__":
    unittest.main()
