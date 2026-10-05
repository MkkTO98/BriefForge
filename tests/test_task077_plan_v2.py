from __future__ import annotations

import copy
import ctypes
from dataclasses import replace
import errno
import hashlib
import inspect
import json
import os
from pathlib import Path
import stat
import tempfile
import threading
import unittest
from unittest import mock

from briefforge.bcrp.model import BCRPBundle, BCRPRecord
import briefforge.bcrp_renderer_compatibility_planning_v2 as planning_v2
from briefforge.bcrp_paired_derivation_evidence_v2 import construct_envelope
from briefforge.bcrp_paired_terminal_admission import (
    NativeBCRPPairedTerminalAdmissionHandle,
    verify_native_bcrp_paired_terminal_admission_v2,
)
from briefforge.task076_contracts import (
    ContractAuthenticationError,
    authenticate_generation8_candidate,
    canonical_json,
    domain_digest,
    load_generation8_candidate,
)
from briefforge.bcrp_renderer_compatibility_planning_v2 import (
    CapabilityV2IssuerInputs,
    PersistedRendererCompatibilityPlanV2,
    PlanV2Rejected,
    construct_renderer_capability_v2,
    persist_renderer_compatibility_plan_v2,
    plan_paired_v3_inventory,
    reload_renderer_compatibility_plan_v2,
    serialize_renderer_capability_v2_bundle,
    verify_plan_v2_predecessor_closure,
    verify_renderer_capability_v2,
)
from briefforge_paired_terminal_profile.profile import PairedProfileRejected

ROOT = Path(__file__).resolve().parents[1]
VALID = json.loads((ROOT / "artifacts/contracts/task076/valid-fixtures.json").read_text())
CAPABILITY = json.loads((ROOT / "artifacts/contracts/task076/capability-v2-record.json").read_text())
CAPABILITY_PAYLOAD = CAPABILITY["extensions"][0]["payload"]
REQUIREMENTS = tuple(
    (index, kind, value)
    for index, (kind, value) in enumerate((
        ("renderer", "briefforge:representative-paired-static-html-renderer:1.0.0"),
        ("media-type", "text/html;charset=utf-8"),
        ("output-count", "1"),
        ("asset-count", "0"),
        ("table-count", "1"),
        ("column-count", "5"),
    ))
)


def closure_fixture(size: int):
    fixture = next(item for item in VALID["fixtures"]
                   if item.get("id") == f"plan-v2-predecessor-closure-{size}-record")
    records = tuple(BCRPRecord.from_document(item["record"]) for item in fixture["records"])
    return fixture, BCRPBundle("briefforge-core-representation-profile", "1.0.0", records)


def generic_mappings(count: int):
    return tuple(
        (index, ("candidate-fingerprint", "effective-graph-digest",
                 ("briefforge:paired-terminal", "3.0.0", "Row", f"row:generic-{index}")),
         f"generic-{index}")
        for index in range(count)
    )


def plan_inventory(mappings):
    return plan_paired_v3_inventory(
        REQUIREMENTS, mappings, CAPABILITY_PAYLOAD,
        capability_fingerprint=CAPABILITY_PAYLOAD["fingerprint"])


def bundle_bytes(bundle: BCRPBundle) -> bytes:
    return canonical_json({
        "profile_identity": bundle.profile_identity,
        "profile_version": bundle.profile_version,
        "records": [record.to_document() for record in bundle.records],
    })


def closure_arguments(size: int):
    fixture, subject = closure_fixture(size)
    _, control = closure_fixture(size)
    return {
        "bundle": subject,
        "expected_bundle": control,
        "root_identity": fixture["root"],
        "allow_publication_successors": size == 10,
    }


def capability_issuer(**changes):
    values = {
        "declaration_identity": "capability:task076-normative-v2",
        "renderer_identity": "briefforge:representative-paired-static-html-renderer:1.0.0",
        "renderer_version": "1.0.0",
        "implementation_identity": "briefforge:paired-static-html-renderer:1.0.0",
        "implementation_digest": "c3f898a514443ada63e68459c392d67cbe42af4ad8393c446859b45834db36f2",
        "owner_identity": "project:BriefForge",
        "owner_role": "bounded-publication-renderer",
        "media_types": ("text/html;charset=utf-8",),
        "output_count": 1,
        "asset_count": 0,
        "table_count": 1,
        "column_count": 5,
        "declared_constraints": ("deterministic", "bounded", "offline"),
        "unsupported_capabilities": (),
        "operation_identity": "operation:task076-capability-fixture",
        "authorization_fingerprint": "ead882da5aa29dc7d5af416d3d5671a3a2d25cd84c53b4af2c31915842e9cb1c",
        "storage_identity": "storage:task076-capability-normative-bytes",
        "issued_at_utc": "2026-08-11T00:00:00Z",
    }
    values.update(changes)
    return CapabilityV2IssuerInputs(**values)


def canonical_envelope(candidate, *, suffix=""):
    frozen = json.loads((
        ROOT / "artifacts/contracts/task076/task071-derivation-evidence-envelope.json"
    ).read_text())
    return construct_envelope(
        evidence_identity=frozen["evidence_identity"] + suffix,
        operation_identity=frozen["operation_identity"] + suffix,
        authorization_fingerprint=("b" * 64 if suffix else frozen["authorization_fingerprint"]),
        issued_at_utc=("2026-08-11T00:00:01Z" if suffix else frozen["issued_at_utc"]),
        source_locator_identity=frozen["source_locator_identity"],
        candidate=candidate,
    )


def replace_record(bundle: BCRPBundle, position: int, record: BCRPRecord) -> BCRPBundle:
    records = list(bundle.records)
    records[position] = record
    return BCRPBundle(bundle.profile_identity, bundle.profile_version, tuple(records))


class Task077AnonymousPublicationTests(unittest.TestCase):
    """Exercise the real anonymous inode independently of Plan fixture admission."""

    def test_procfd_linkat_arguments_real_bytes_and_inode(self):
        payload = b"plan-v2 anonymous publication exact bytes\n"
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
            descriptor = os.open(".", os.O_RDWR | os.O_TMPFILE, 0o600,
                                 dir_fd=directory_fd)
            try:
                self.assertEqual(os.write(descriptor, payload), len(payload))
                os.fsync(descriptor)
                self.assertEqual(os.lseek(descriptor, 0, os.SEEK_SET), 0)
                self.assertEqual(os.read(descriptor, len(payload)), payload)
                initial = os.fstat(descriptor)
                self.assertEqual(initial.st_nlink, 0)
                libc = ctypes.CDLL(None, use_errno=True)
                actual_linkat = libc.linkat
                actual_linkat.argtypes = (ctypes.c_int, ctypes.c_char_p,
                                          ctypes.c_int, ctypes.c_char_p, ctypes.c_int)
                actual_linkat.restype = ctypes.c_int
                calls = []

                def recording_linkat(old_fd, old_path, new_fd, new_path, flags):
                    calls.append((old_fd, old_path, new_fd, new_path, flags))
                    self.assertEqual(os.fstat(descriptor).st_ino, initial.st_ino)
                    self.assertEqual(os.fstat(directory_fd).st_ino,
                                     directory.stat().st_ino)
                    return actual_linkat(old_fd, old_path, new_fd, new_path, flags)

                stub = mock.Mock(side_effect=recording_linkat)
                with mock.patch.object(planning_v2.ctypes, "CDLL",
                                       return_value=mock.Mock(linkat=stub)):
                    planning_v2._plan_v2_publish_anonymous(
                        descriptor, directory_fd, "plan.json")
                self.assertEqual(calls, [(-100, os.fsencode(f"/proc/self/fd/{descriptor}"),
                                          directory_fd, b"plan.json", 0x400)])
                published = directory / "plan.json"
                self.assertEqual(published.read_bytes(), payload)
                self.assertEqual((published.stat().st_dev, published.stat().st_ino),
                                 (initial.st_dev, initial.st_ino))
                self.assertEqual(os.fstat(descriptor).st_nlink, 1)
                self.assertEqual(list(directory.iterdir()), [published])
            finally:
                os.close(descriptor)
                os.close(directory_fd)

    def test_unavailable_procfd_fails_closed_and_cleans_public_persistence(self):
        fixture, subject = closure_fixture(8)
        _, control = closure_fixture(8)
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            before_fds = set(os.listdir("/proc/self/fd"))
            calls = []

            def missing_procfd(old_fd, old_path, new_fd, new_path, flags):
                calls.append((old_fd, old_path, new_fd, new_path, flags))
                ctypes.set_errno(errno.ENOENT)
                return -1

            stub = mock.Mock(side_effect=missing_procfd)
            with mock.patch.object(planning_v2.ctypes, "CDLL",
                                   return_value=mock.Mock(linkat=stub)):
                with self.assertRaises(PlanV2Rejected) as caught:
                    persist_renderer_compatibility_plan_v2(
                        subject, directory=directory, expected_bundle=control,
                        root_identity=fixture["root"],
                        allow_publication_successors=False)
            self.assertEqual(caught.exception.code, "PLAN_V2_PERSISTENCE_REJECTED")
            self.assertIsInstance(caught.exception.__cause__, FileNotFoundError)
            self.assertEqual(caught.exception.__cause__.errno, errno.ENOENT)
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0][0], -100)
            self.assertTrue(calls[0][1].startswith(b"/proc/self/fd/"))
            self.assertEqual(calls[0][2] >= 0, True)
            self.assertEqual(calls[0][3:], (b"renderer-compatibility-plan-v2.json", 0x400))
            self.assertEqual(list(directory.iterdir()), [])
            self.assertEqual(set(os.listdir("/proc/self/fd")), before_fds)

    def test_existing_destination_never_overwritten(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            target = directory / "plan.json"
            target.write_bytes(b"foreign bytes")
            foreign = target.stat()
            directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
            descriptor = os.open(".", os.O_RDWR | os.O_TMPFILE, 0o600,
                                 dir_fd=directory_fd)
            try:
                os.write(descriptor, b"new bytes")
                os.fsync(descriptor)
                with self.assertRaises(FileExistsError) as caught:
                    planning_v2._plan_v2_publish_anonymous(
                        descriptor, directory_fd, target.name)
                self.assertEqual(caught.exception.errno, errno.EEXIST)
                self.assertEqual(target.read_bytes(), b"foreign bytes")
                self.assertEqual(target.stat().st_ino, foreign.st_ino)
                self.assertEqual(os.fstat(descriptor).st_nlink, 0)
                self.assertEqual(list(directory.iterdir()), [target])
            finally:
                os.close(descriptor)
                os.close(directory_fd)

    def test_linkat_failure_captures_errno_and_leaves_no_entry(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
            descriptor = os.open(".", os.O_RDWR | os.O_TMPFILE, 0o600,
                                 dir_fd=directory_fd)
            try:
                os.write(descriptor, b"unpublished")
                os.fsync(descriptor)

                def failing_linkat(*args):
                    ctypes.set_errno(errno.EIO)
                    return -1

                stub = mock.Mock(side_effect=failing_linkat)
                with mock.patch.object(planning_v2.ctypes, "CDLL",
                                       return_value=mock.Mock(linkat=stub)):
                    with self.assertRaises(OSError) as caught:
                        planning_v2._plan_v2_publish_anonymous(
                            descriptor, directory_fd, "plan.json")
                self.assertEqual(caught.exception.errno, errno.EIO)
                self.assertEqual(stub.call_count, 1)
                self.assertEqual(list(directory.iterdir()), [])
                self.assertEqual(os.fstat(descriptor).st_nlink, 0)
            finally:
                os.close(descriptor)
                os.close(directory_fd)


class Task077PlanV2CompletenessTests(unittest.TestCase):
    def test_generic_n1_n7_n16_are_complete_and_deterministic(self):
        for count in (1, 7, 16):
            with self.subTest(count=count):
                first = plan_inventory(generic_mappings(count))
                second = plan_inventory(generic_mappings(count))
                self.assertEqual(first, second)
                self.assertEqual(len(first[0]), 6)
                self.assertEqual(len(first[1]), count)
                self.assertEqual([item[0] for item in first[1]], list(range(count)))

    def test_generic_n_plus_one_preserves_prior_outcomes_and_adds_exactly_one(self):
        for count in (1, 7, 15):
            with self.subTest(n=count, n_plus_one=count + 1):
                prior = plan_inventory(generic_mappings(count))
                grown = plan_inventory(generic_mappings(count + 1))
                self.assertEqual(grown[0], prior[0])
                self.assertEqual(grown[1][:-1], prior[1])
                self.assertEqual(len(grown[1]), len(prior[1]) + 1)
                self.assertEqual(grown[1][-1][0], count)
                self.assertEqual(grown[1][-1][2], f"generic-{count}")

    def test_generic_n0_fails_closed(self):
        with self.assertRaises(PlanV2Rejected):
            plan_inventory(())

    def test_duplicate_or_reordered_mapping_fails_closed(self):
        duplicate = list(generic_mappings(2))
        duplicate[1] = (1, duplicate[0][1], duplicate[0][2])
        with self.assertRaises(PlanV2Rejected):
            plan_inventory(tuple(duplicate))
        with self.assertRaises(PlanV2Rejected):
            plan_inventory(tuple(reversed(generic_mappings(2))))


class Task077SyntheticPredecessorLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = load_generation8_candidate()
        cls.candidate_b = load_generation8_candidate()
        cls.envelope = canonical_envelope(cls.candidate)
        cls.envelope_b = canonical_envelope(cls.candidate_b, suffix=":isolation-b")
        cls.issuer = capability_issuer()
        cls.issuer_b = capability_issuer(
            declaration_identity="capability:task077-plan-isolation-b",
            operation_identity="operation:task077-plan-isolation-b",
            authorization_fingerprint="c" * 64,
            storage_identity="storage:task077-plan-isolation-b",
            issued_at_utc="2026-08-11T00:00:01Z",
        )
        cls.capability = construct_renderer_capability_v2(
            candidate=cls.candidate,
            derivation_evidence=cls.envelope,
            issuer_inputs=cls.issuer,
        )
        cls.capability_b = construct_renderer_capability_v2(
            candidate=cls.candidate_b,
            derivation_evidence=cls.envelope_b,
            issuer_inputs=cls.issuer_b,
        )

    def test_generation8_conforming_synthetic_candidate_produces_verified_release(self):
        canonical = authenticate_generation8_candidate(self.candidate)
        self.assertEqual(canonical.candidate_identity, "candidate:task071-cross-inquiry")
        self.assertFalse(hasattr(canonical, "verified_release"))
        planning = __import__(
            "briefforge.bcrp_renderer_compatibility_planning_v2",
            fromlist=["construct_renderer_compatibility_plan_v2"],
        )
        self.assertFalse(hasattr(planning, "_issue_fixture_plan_v2_closure_authority"))
        self.assertFalse(hasattr(planning, "PlanV2ClosureAuthority"))
        signature = inspect.signature(planning.construct_renderer_compatibility_plan_v2)
        self.assertIs(signature.parameters["verified_release"].default, inspect.Parameter.empty)
        task071 = (ROOT / "artifacts/tasks/TASK-071-crash-recoverable-successor-candidate-authoring-and-semantic-acceptance.md").read_text()
        self.assertIn("No Judgment, Ready package, Release, Plan, token", task071)

    def test_plan_payload_fingerprint_known_answer_and_metadata_are_accurate(self):
        extension = json.loads((ROOT / "artifacts/contracts/task076/plan-v2-extension.json").read_text())
        payload = extension["payload"] if "payload" in extension else extension
        asserted = payload["fingerprint"]
        unsigned = {key: value for key, value in payload.items() if key != "fingerprint"}
        expected = "39619ff12a53fcd14907df303a6788df6835884f307255fb139e2b26e06d61b4"
        self.assertEqual(domain_digest("briefforge.task075.plan-extension.v2", unsigned), expected)
        self.assertEqual(asserted, expected)
        _, closure = closure_fixture(8)
        frozen_plan = closure.one("RendererCompatibilityPlanRecord")
        self.assertEqual(frozen_plan.extensions[0]["payload"], payload)
        self.assertEqual(frozen_plan.identity, payload["plan_identity"])
        self.assertEqual(hashlib.sha256(bundle_bytes(closure)).hexdigest(),
                         hashlib.sha256(bundle_bytes(closure_fixture(8)[1])).hexdigest())

    def test_serialized_capability_cannot_transfer_to_foreign_candidate_chain(self):
        serialized = serialize_renderer_capability_v2_bundle(
            self.capability,
            candidate=self.candidate,
            derivation_evidence=self.envelope,
            issuer_inputs=self.issuer,
        )
        control = verify_renderer_capability_v2(
            serialized,
            candidate=self.candidate,
            derivation_evidence=self.envelope,
            issuer_inputs=self.issuer,
        )
        foreign = replace(self.candidate, candidate_identity="candidate:task077-foreign")
        with self.assertRaises(ContractAuthenticationError) as caught:
            authenticate_generation8_candidate(foreign)
        self.assertIn("not issued in this process", str(caught.exception))
        self.assertEqual(
            verify_renderer_capability_v2(
                serialized,
                candidate=self.candidate,
                derivation_evidence=self.envelope,
                issuer_inputs=self.issuer,
            ).fingerprint,
            control.fingerprint,
        )

    def test_plan_verification_is_data_only_and_native_owner_is_one_use(self):
        arguments = closure_arguments(8)
        identities = verify_plan_v2_predecessor_closure(**arguments)
        self.assertEqual(len(identities), 8)
        plan_bytes = bundle_bytes(arguments["bundle"])
        self.assertFalse(hasattr(plan_bytes, "native_handle"))
        self.assertFalse(hasattr(arguments["bundle"], "native_handle"))
        with self.assertRaises(PairedProfileRejected):
            verify_native_bcrp_paired_terminal_admission_v2(plan_bytes)
        with self.assertRaises(TypeError):
            NativeBCRPPairedTerminalAdmissionHandle()
        self.assertEqual(verify_plan_v2_predecessor_closure(**arguments), identities)

    def test_rejects_substituted_paired_extension_and_decoded_population(self):
        self.assertEqual(
            authenticate_generation8_candidate(self.candidate).candidate_profile_instance_fingerprint,
            self.candidate.candidate_profile_instance_fingerprint,
        )
        extension_substitution = copy.deepcopy(self.candidate.bundle)
        extension_substitution.one("CandidatePresentationPackageRecord").extensions[0]["name"] = "foreign"
        population_substitution = copy.deepcopy(self.candidate.bundle)
        candidate_record = population_substitution.one("CandidatePresentationPackageRecord")
        canonical = json.loads(candidate_record.extensions[0]["payload"]["canonical_semantics"])
        canonical["table"]["rows"].pop()
        candidate_record.extensions[0]["payload"]["canonical_semantics"] = json.dumps(
            canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
        for bundle in (extension_substitution, population_substitution):
            with self.assertRaises(ContractAuthenticationError) as caught:
                authenticate_generation8_candidate(replace(self.candidate, bundle=bundle))
            self.assertIn("not issued in this process", str(caught.exception))
        self.assertEqual(
            authenticate_generation8_candidate(self.candidate).candidate_profile_instance_fingerprint,
            self.candidate.candidate_profile_instance_fingerprint,
        )

    def test_rejects_omitted_and_duplicated_rows_even_after_internal_recomputation(self):
        control = generic_mappings(3)
        self.assertEqual(len(plan_inventory(control)[1]), 3)
        with self.assertRaises(PlanV2Rejected):
            plan_inventory(control[:-1] + ((2, control[0][1], control[0][2]),))
        with self.assertRaises(PlanV2Rejected):
            plan_inventory(control + ((3, control[0][1], control[0][2]),))
        self.assertEqual(len(plan_inventory(control)[1]), 3)

    def test_rejects_release_and_capability_from_another_candidate(self):
        fixture, control = closure_fixture(8)
        records = list(control.records)
        capability_document = json.loads(self.capability_b._bundle_document)["records"][0]
        foreign_capability = BCRPRecord.from_document(capability_document)
        plan_doc = copy.deepcopy(records[7].to_document())
        plan_doc["semantic"]["renderer_capability_ref"] = foreign_capability.identity
        plan_doc["extensions"][0]["target_refs"][3] = foreign_capability.identity
        payload = plan_doc["extensions"][0]["payload"]
        payload["capability_identity"] = foreign_capability.identity
        payload["capability_fingerprint"] = foreign_capability.extensions[0]["payload"]["fingerprint"]
        payload["semantic_digest"] = domain_digest(
            "briefforge.task076.plan-core-semantic.v1", plan_doc["semantic"])
        payload.pop("fingerprint")
        payload["fingerprint"] = domain_digest("briefforge.task075.plan-extension.v2", payload)
        attacked = BCRPBundle(control.profile_identity, control.profile_version,
                              tuple([*records[:6], foreign_capability, BCRPRecord.from_document(plan_doc)]))
        with self.assertRaises(PlanV2Rejected):
            verify_plan_v2_predecessor_closure(
                attacked, expected_bundle=control, root_identity=fixture["root"],
                allow_publication_successors=False)
        release_doc = copy.deepcopy(records[5].to_document())
        release_doc["identity"] = "release:task077-foreign-data-only"
        foreign_release = BCRPRecord.from_document(release_doc)
        release_plan_doc = copy.deepcopy(records[7].to_document())
        release_plan_doc["extensions"][0]["target_refs"][2] = foreign_release.identity
        release_payload = release_plan_doc["extensions"][0]["payload"]
        release_payload["release_identity"] = foreign_release.identity
        release_payload["release_fingerprint"] = domain_digest(
            "briefforge.task075.release-record.v1", foreign_release.to_document())
        release_payload["release_closure_digest"] = domain_digest(
            "briefforge.task075.release-closure.v1",
            [record.to_document() for record in [*records[:5], foreign_release]],
        )
        release_payload["semantic_digest"] = domain_digest(
            "briefforge.task076.plan-core-semantic.v1", release_plan_doc["semantic"])
        release_payload.pop("fingerprint")
        release_payload["fingerprint"] = domain_digest(
            "briefforge.task075.plan-extension.v2", release_payload)
        release_attacked = BCRPBundle(
            control.profile_identity, control.profile_version,
            tuple([*records[:5], foreign_release, records[6],
                   BCRPRecord.from_document(release_plan_doc)]))
        with self.assertRaises(PlanV2Rejected):
            verify_plan_v2_predecessor_closure(
                release_attacked, expected_bundle=control, root_identity=fixture["root"],
                allow_publication_successors=False)
        self.assertEqual(verify_plan_v2_predecessor_closure(
            control, expected_bundle=closure_fixture(8)[1], root_identity=fixture["root"],
            allow_publication_successors=False), tuple(record.identity for record in control.records))

    def test_rejects_ready_from_another_judgment_after_release_fingerprint_recompute(self):
        fixture, control = closure_fixture(8)
        ready_doc = copy.deepcopy(control.records[4].to_document())
        ready_doc["identity"] = "ready:task077-foreign-data-only"
        ready_doc["semantic"]["predecessor_refs"] = ["judgment:task077-foreign"]
        foreign_ready = BCRPRecord.from_document(ready_doc)
        release_doc = copy.deepcopy(control.records[5].to_document())
        release_doc["semantic"]["predecessor_refs"] = [foreign_ready.identity]
        correlated_release = BCRPRecord.from_document(release_doc)
        plan_doc = copy.deepcopy(control.records[7].to_document())
        plan_doc["semantic"]["ready_ref"] = foreign_ready.identity
        payload = plan_doc["extensions"][0]["payload"]
        payload["ready_fingerprint"] = domain_digest(
            "briefforge.task075.ready-record.v1", foreign_ready.to_document())
        payload["release_fingerprint"] = domain_digest(
            "briefforge.task075.release-record.v1", correlated_release.to_document())
        correlated_closure = [*control.records[:4], foreign_ready, correlated_release]
        payload["release_closure_digest"] = domain_digest(
            "briefforge.task075.release-closure.v1",
            [record.to_document() for record in correlated_closure],
        )
        payload["semantic_digest"] = domain_digest(
            "briefforge.task076.plan-core-semantic.v1", plan_doc["semantic"])
        payload.pop("fingerprint")
        payload["fingerprint"] = domain_digest("briefforge.task075.plan-extension.v2", payload)
        attacked = BCRPBundle(
            control.profile_identity, control.profile_version,
            tuple([*control.records[:4], foreign_ready, correlated_release,
                   control.records[6], BCRPRecord.from_document(plan_doc)]))
        self.assertEqual(len(verify_plan_v2_predecessor_closure(
            control, expected_bundle=closure_fixture(8)[1], root_identity=fixture["root"],
            allow_publication_successors=False)), 8)
        with self.assertRaises(PlanV2Rejected):
            verify_plan_v2_predecessor_closure(
                attacked, expected_bundle=control, root_identity=fixture["root"],
                allow_publication_successors=False)
        self.assertEqual(len(verify_plan_v2_predecessor_closure(
            control, expected_bundle=closure_fixture(8)[1], root_identity=fixture["root"],
            allow_publication_successors=False)), 8)

    def test_plan_persists_and_reloads_against_same_authority_chain(self):
        fixture, subject = closure_fixture(8)
        _, control = closure_fixture(8)
        expected_bytes = bundle_bytes(subject)
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            directory_a = root / "a"
            directory_b = root / "b"
            before_directory = root / "before-race"
            failure_directory = root / "partial-failure"
            race_directory = root / "foreign-substitution"
            directory_a.mkdir(mode=0o700)
            directory_b.mkdir(mode=0o700)
            before_directory.mkdir(mode=0o700)
            failure_directory.mkdir(mode=0o700)
            race_directory.mkdir(mode=0o700)
            descriptors_before = set(os.listdir("/proc/self/fd"))
            with mock.patch(
                    "briefforge.bcrp_renderer_compatibility_planning_v2.os.write",
                    side_effect=OSError("injected partial write failure")):
                with self.assertRaises(PlanV2Rejected) as caught:
                    persist_renderer_compatibility_plan_v2(
                        subject, directory=failure_directory, expected_bundle=control,
                        root_identity=fixture["root"], allow_publication_successors=False)
            self.assertEqual(caught.exception.code, "PLAN_V2_PERSISTENCE_REJECTED")
            self.assertEqual(caught.exception.owner, "renderer-compatibility-planning-v2")
            self.assertEqual(caught.exception.location,
                             f"{failure_directory}/renderer-compatibility-plan-v2.json")
            self.assertIn("injected partial write failure", caught.exception.reason)
            self.assertEqual(list(failure_directory.iterdir()), [])
            self.assertEqual(set(os.listdir("/proc/self/fd")), descriptors_before)
            real_fstat = os.fstat
            fstat_calls = 0
            def fail_second_fstat(descriptor):
                nonlocal fstat_calls
                fstat_calls += 1
                if fstat_calls == 2:
                    raise OSError("injected file post-open fstat failure")
                return real_fstat(descriptor)
            with mock.patch(
                    "briefforge.bcrp_renderer_compatibility_planning_v2.os.fstat",
                    side_effect=fail_second_fstat):
                with self.assertRaises(PlanV2Rejected) as caught:
                    persist_renderer_compatibility_plan_v2(
                        subject, directory=failure_directory, expected_bundle=control,
                        root_identity=fixture["root"], allow_publication_successors=False)
            self.assertEqual(caught.exception.code, "PLAN_V2_PERSISTENCE_REJECTED")
            self.assertEqual(caught.exception.reason, "injected file post-open fstat failure")
            self.assertIsInstance(caught.exception.__cause__, OSError)
            self.assertEqual(str(caught.exception.__cause__),
                             "injected file post-open fstat failure")
            self.assertEqual(list(failure_directory.iterdir()), [])
            self.assertEqual(set(os.listdir("/proc/self/fd")), descriptors_before)
            persistent_fstat_calls = 0
            def fail_all_file_fstats(descriptor):
                nonlocal persistent_fstat_calls
                persistent_fstat_calls += 1
                if persistent_fstat_calls >= 2:
                    raise OSError("persistent post-create fstat failure")
                return real_fstat(descriptor)
            with mock.patch(
                    "briefforge.bcrp_renderer_compatibility_planning_v2.os.fstat",
                    side_effect=fail_all_file_fstats):
                with self.assertRaises(PlanV2Rejected) as caught:
                    persist_renderer_compatibility_plan_v2(
                        subject, directory=failure_directory, expected_bundle=control,
                        root_identity=fixture["root"], allow_publication_successors=False)
            self.assertEqual(caught.exception.code, "PLAN_V2_PERSISTENCE_REJECTED")
            self.assertEqual(caught.exception.reason,
                             "persistent post-create fstat failure")
            self.assertEqual(list(failure_directory.iterdir()), [])
            self.assertEqual(set(os.listdir("/proc/self/fd")), descriptors_before)

            with mock.patch(
                    "briefforge.bcrp_renderer_compatibility_planning_v2.os.fsync",
                    side_effect=OSError("injected anonymous durability failure")):
                with self.assertRaises(PlanV2Rejected) as caught:
                    persist_renderer_compatibility_plan_v2(
                        subject, directory=failure_directory, expected_bundle=control,
                        root_identity=fixture["root"], allow_publication_successors=False)
            self.assertEqual(caught.exception.code, "PLAN_V2_PERSISTENCE_REJECTED")
            self.assertIn("injected anonymous durability failure", caught.exception.reason)
            self.assertEqual(list(failure_directory.iterdir()), [])
            self.assertEqual(set(os.listdir("/proc/self/fd")), descriptors_before)

            with mock.patch(
                    "briefforge.bcrp_renderer_compatibility_planning_v2._plan_v2_publish_anonymous",
                    side_effect=OSError("injected anonymous publication failure")):
                with self.assertRaises(PlanV2Rejected) as caught:
                    persist_renderer_compatibility_plan_v2(
                        subject, directory=failure_directory, expected_bundle=control,
                        root_identity=fixture["root"], allow_publication_successors=False)
            self.assertEqual(caught.exception.code, "PLAN_V2_PERSISTENCE_REJECTED")
            self.assertIn("injected anonymous publication failure", caught.exception.reason)
            self.assertEqual(list(failure_directory.iterdir()), [])
            self.assertEqual(set(os.listdir("/proc/self/fd")), descriptors_before)

            real_anonymous_open = os.open
            def reject_anonymous_open(path, flags, mode=0o777, *, dir_fd=None):
                if path == "." and flags & getattr(os, "O_TMPFILE", 0):
                    raise OSError(95, "anonymous files unsupported")
                return real_anonymous_open(path, flags, mode, dir_fd=dir_fd)
            with mock.patch(
                    "briefforge.bcrp_renderer_compatibility_planning_v2.os.open",
                    side_effect=reject_anonymous_open):
                with self.assertRaises(PlanV2Rejected) as caught:
                    persist_renderer_compatibility_plan_v2(
                        subject, directory=failure_directory, expected_bundle=control,
                        root_identity=fixture["root"], allow_publication_successors=False)
            self.assertEqual(caught.exception.code, "PLAN_V2_PERSISTENCE_REJECTED")
            self.assertIn("anonymous files unsupported", caught.exception.reason)
            self.assertEqual(list(failure_directory.iterdir()), [])
            self.assertEqual(set(os.listdir("/proc/self/fd")), descriptors_before)

            before_receipt = persist_renderer_compatibility_plan_v2(
                subject, directory=before_directory, expected_bundle=control,
                root_identity=fixture["root"], allow_publication_successors=False)
            self.assertEqual(reload_renderer_compatibility_plan_v2(
                before_receipt.path, persistence_receipt=before_receipt,
                expected_bundle=control, root_identity=fixture["root"],
                allow_publication_successors=False)._bundle_document, expected_bytes)

            target = race_directory / "renderer-compatibility-plan-v2.json"
            foreign_bytes = b"independently-created-foreign-plan-evidence\n"
            race_window = threading.Event()
            replacement_written = threading.Event()
            replacement_evidence = {}
            real_stat = os.stat
            real_unlink = os.unlink
            real_open = os.open
            real_write = os.write
            real_close = os.close
            named_file_fstats = 0

            def substitute_destination():
                if not race_window.wait(5):
                    replacement_evidence["thread_error"] = "race window not reached"
                    replacement_written.set()
                    return
                try:
                    real_unlink(target)
                except FileNotFoundError:
                    pass
                descriptor = real_open(
                    target, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                    | getattr(os, "O_NOFOLLOW", 0), 0o600)
                try:
                    if real_write(descriptor, foreign_bytes) != len(foreign_bytes):
                        raise OSError("foreign replacement short write")
                    os.fsync(descriptor)
                    state = real_fstat(descriptor)
                    replacement_evidence.update({
                        "device": state.st_dev,
                        "inode": state.st_ino,
                        "bytes": foreign_bytes.decode("ascii"),
                        "sha256": hashlib.sha256(foreign_bytes).hexdigest(),
                    })
                finally:
                    real_close(descriptor)
                    replacement_written.set()

            def coordinated_fstat(descriptor):
                nonlocal named_file_fstats
                state = real_fstat(descriptor)
                if stat.S_ISREG(state.st_mode):
                    if state.st_nlink == 0 and not race_window.is_set():
                        race_window.set()
                        if not replacement_written.wait(5):
                            raise OSError("foreign replacement coordination timed out")
                    elif state.st_nlink > 0:
                        named_file_fstats += 1
                        if named_file_fstats == 2:
                            raise OSError("injected post-create validation failure")
                return state

            def coordinated_stat(path, *args, **kwargs):
                state = real_stat(path, *args, **kwargs)
                if (path == target.name and kwargs.get("dir_fd") is not None
                        and not race_window.is_set()):
                    race_window.set()
                    if not replacement_written.wait(5):
                        raise OSError("foreign replacement coordination timed out")
                return state

            worker = threading.Thread(target=substitute_destination, daemon=True)
            worker.start()
            with mock.patch(
                    "briefforge.bcrp_renderer_compatibility_planning_v2.os.fstat",
                    side_effect=coordinated_fstat), mock.patch(
                    "briefforge.bcrp_renderer_compatibility_planning_v2.os.stat",
                    side_effect=coordinated_stat):
                with self.assertRaises(PlanV2Rejected) as caught:
                    persist_renderer_compatibility_plan_v2(
                        subject, directory=race_directory, expected_bundle=control,
                        root_identity=fixture["root"], allow_publication_successors=False)
            worker.join(5)
            self.assertFalse(worker.is_alive())
            self.assertEqual(caught.exception.code, "PLAN_V2_PERSISTENCE_REJECTED")
            self.assertNotIn("thread_error", replacement_evidence)
            self.assertEqual(replacement_evidence["bytes"], foreign_bytes.decode("ascii"))
            self.assertEqual(replacement_evidence["sha256"],
                             hashlib.sha256(foreign_bytes).hexdigest())
            self.assertTrue(target.exists(),
                            f"foreign replacement was deleted: {replacement_evidence}")
            surviving = real_stat(target, follow_symlinks=False)
            self.assertEqual((surviving.st_dev, surviving.st_ino),
                             (replacement_evidence["device"],
                              replacement_evidence["inode"]))
            self.assertEqual(target.read_bytes(), foreign_bytes)
            self.assertEqual(list(race_directory.iterdir()), [target])

            receipt_a = persist_renderer_compatibility_plan_v2(
                subject, directory=directory_a, expected_bundle=control,
                root_identity=fixture["root"], allow_publication_successors=False)
            receipt_b = persist_renderer_compatibility_plan_v2(
                closure_fixture(8)[1], directory=directory_b,
                expected_bundle=closure_fixture(8)[1], root_identity=fixture["root"],
                allow_publication_successors=False)
            a1 = reload_renderer_compatibility_plan_v2(
                receipt_a.path, persistence_receipt=receipt_a,
                expected_bundle=closure_fixture(8)[1], root_identity=fixture["root"],
                allow_publication_successors=False,
                expected_sha256=receipt_a.sha256,
                expected_extension_fingerprint=receipt_a.extension_fingerprint,
                expected_bundle_fingerprint=receipt_a.bundle_fingerprint)
            b1 = reload_renderer_compatibility_plan_v2(
                receipt_b.path, persistence_receipt=receipt_b,
                expected_bundle=closure_fixture(8)[1], root_identity=fixture["root"],
                allow_publication_successors=False)
            self.assertEqual(a1._bundle_document, expected_bytes)
            self.assertEqual(b1._bundle_document, expected_bytes)
            self.assertNotEqual(receipt_a.path, receipt_b.path)
            self.assertNotEqual(receipt_a, receipt_b)
            self.assertNotEqual((receipt_a.device, receipt_a.inode),
                                (receipt_b.device, receipt_b.inode))
            self.assertEqual(receipt_a.length, len(expected_bytes))
            self.assertEqual(receipt_a.sha256, hashlib.sha256(expected_bytes).hexdigest())
            receipt_attacks = (
                replace(receipt_a, path=receipt_b.path),
                replace(receipt_a, sha256="0" * 64),
                replace(receipt_a, length=receipt_a.length + 1),
                replace(receipt_a, extension_fingerprint="1" * 64),
                replace(receipt_a, bundle_fingerprint="2" * 64),
                replace(receipt_a, device=receipt_a.device + 1),
                replace(receipt_a, inode=receipt_a.inode + 1),
            )
            for attacked_receipt in receipt_attacks:
                with self.subTest(field=attacked_receipt):
                    with self.assertRaises(PlanV2Rejected):
                        reload_renderer_compatibility_plan_v2(
                            receipt_a.path, persistence_receipt=attacked_receipt,
                            expected_bundle=closure_fixture(8)[1],
                            root_identity=fixture["root"],
                            allow_publication_successors=False)
            with self.assertRaises(PlanV2Rejected):
                reload_renderer_compatibility_plan_v2(
                    receipt_b.path,
                    persistence_receipt=replace(receipt_a, path=receipt_b.path),
                    expected_bundle=closure_fixture(8)[1], root_identity=fixture["root"],
                    allow_publication_successors=False)
            leaf_directory = root / "leaf"
            leaf_directory.mkdir(mode=0o700)
            leaf = leaf_directory / receipt_a.path.name
            leaf.symlink_to(receipt_a.path)
            leaf_receipt = replace(receipt_a, path=leaf)
            with self.assertRaises(PlanV2Rejected) as caught:
                reload_renderer_compatibility_plan_v2(
                    leaf, persistence_receipt=leaf_receipt,
                    expected_bundle=closure_fixture(8)[1], root_identity=fixture["root"],
                    allow_publication_successors=False)
            self.assertEqual(caught.exception.code, "PLAN_V2_RELOAD_REJECTED")
            self.assertEqual(caught.exception.location, str(leaf))
            self.assertTrue(caught.exception.reason)
            ancestor = root / "ancestor-link"
            ancestor.symlink_to(directory_a, target_is_directory=True)
            ancestor_path = ancestor / receipt_a.path.name
            with self.assertRaises(PlanV2Rejected) as caught:
                reload_renderer_compatibility_plan_v2(
                    ancestor_path, persistence_receipt=replace(receipt_a, path=ancestor_path),
                    expected_bundle=closure_fixture(8)[1], root_identity=fixture["root"],
                    allow_publication_successors=False)
            self.assertEqual(caught.exception.code, "PLAN_V2_RELOAD_REJECTED")
            self.assertEqual(caught.exception.location, str(ancestor_path))
            foreign_control_doc = copy.deepcopy(control.records[6].to_document())
            foreign_control_doc["metadata"] = {"chain": "foreign-b"}
            foreign_control = replace_record(
                closure_fixture(8)[1], 6, BCRPRecord.from_document(foreign_control_doc))
            with self.assertRaises(PlanV2Rejected):
                reload_renderer_compatibility_plan_v2(
                    receipt_b.path, persistence_receipt=receipt_b,
                    expected_bundle=foreign_control, root_identity=fixture["root"],
                    allow_publication_successors=False)
            with self.assertRaises(PlanV2Rejected):
                reload_renderer_compatibility_plan_v2(
                    receipt_b.path, persistence_receipt=replace(receipt_b, sha256="f" * 64),
                    expected_bundle=closure_fixture(8)[1], root_identity=fixture["root"],
                    allow_publication_successors=False)
            a2 = reload_renderer_compatibility_plan_v2(
                receipt_a.path, persistence_receipt=receipt_a,
                expected_bundle=closure_fixture(8)[1], root_identity=fixture["root"],
                allow_publication_successors=False)
            b2 = reload_renderer_compatibility_plan_v2(
                receipt_b.path, persistence_receipt=receipt_b,
                expected_bundle=closure_fixture(8)[1], root_identity=fixture["root"],
                allow_publication_successors=False)
            self.assertEqual((a1._bundle_document, b1._bundle_document),
                             (a2._bundle_document, b2._bundle_document))
            self.assertEqual(receipt_a.path.read_bytes(), expected_bytes)
            self.assertEqual(receipt_b.path.read_bytes(), expected_bytes)
            self.assertIs(type(receipt_a), PersistedRendererCompatibilityPlanV2)
            self.assertFalse(hasattr(a2, "native_handle"))
            self.assertFalse(hasattr(b2, "native_handle"))


class Task077PlanV2ClosureTests(unittest.TestCase):
    def test_frozen_eight_and_ten_record_closures_pass_production_verifier(self):
        for size in (8, 10):
            with self.subTest(size=size):
                fixture, bundle = closure_fixture(size)
                identities = verify_plan_v2_predecessor_closure(
                    bundle, expected_bundle=closure_fixture(size)[1],
                    root_identity=fixture["root"],
                    allow_publication_successors=size == 10)
                self.assertEqual(list(identities), fixture["record_order"])
                self.assertEqual(set(identities), set(fixture["expected_reachable"]))

    def test_all_36_complete_record_substitutions_fail_independent_binding(self):
        attacks = 0
        for size in (8, 10):
            fixture, bundle = closure_fixture(size)
            control = closure_fixture(size)[1]
            self.assertEqual(len(verify_plan_v2_predecessor_closure(
                bundle, expected_bundle=control, root_identity=fixture["root"],
                allow_publication_successors=size == 10)), size)
            for position, original in enumerate(bundle.records):
                minimal = BCRPRecord(
                    original.kind, original.identity, original.profile_version, {}, [])
                full_document = copy.deepcopy(original.to_document())
                full_document["metadata"] = {
                    **full_document.get("metadata", {}),
                    "task077_foreign_complete_record": position,
                }
                for substituted in (minimal, BCRPRecord.from_document(full_document)):
                    attacked = replace_record(bundle, position, substituted)
                    with self.assertRaises(PlanV2Rejected):
                        verify_plan_v2_predecessor_closure(
                            attacked, expected_bundle=control,
                            root_identity=fixture["root"],
                            allow_publication_successors=size == 10)
                    attacks += 1
            self.assertEqual(len(verify_plan_v2_predecessor_closure(
                bundle, expected_bundle=control, root_identity=fixture["root"],
                allow_publication_successors=size == 10)), size)
        self.assertEqual(attacks, 36)

    def test_reordered_duplicate_and_altered_topology_fail_closed(self):
        fixture, bundle = closure_fixture(8)
        control = closure_fixture(8)[1]
        records = list(bundle.records)
        reordered = BCRPBundle(bundle.profile_identity, bundle.profile_version,
                               tuple([records[1], records[0], *records[2:]]))
        duplicate = BCRPBundle(bundle.profile_identity, bundle.profile_version,
                               tuple([*records[:-1], records[-2]]))
        document = copy.deepcopy(records[3].to_document())
        document["semantic"]["predecessor_refs"] = [records[0].identity]
        altered = replace_record(bundle, 3, BCRPRecord.from_document(document))
        hidden = BCRPRecord(
            "GeneratedArtifactAuditRecord", "audit:hidden", "1.0.0",
            {"predecessor_refs": [fixture["root"]]}, [])
        hidden_bundle = BCRPBundle(bundle.profile_identity, bundle.profile_version,
                                   tuple([*records, hidden]))
        foreign_profile = BCRPBundle("foreign-profile", "9.9.9", tuple(records))
        empty = BCRPBundle(bundle.profile_identity, bundle.profile_version, ())
        for label, attacked, root in (
            ("reordered", reordered, fixture["root"]),
            ("duplicate", duplicate, fixture["root"]),
            ("topology", altered, fixture["root"]),
            ("root", bundle, records[2].identity),
            ("hidden", hidden_bundle, fixture["root"]),
            ("foreign-profile", foreign_profile, fixture["root"]),
            ("empty", empty, fixture["root"]),
        ):
            with self.subTest(label=label):
                with self.assertRaises(PlanV2Rejected):
                    verify_plan_v2_predecessor_closure(
                        attacked, expected_bundle=control, root_identity=root,
                        allow_publication_successors=False)
        with self.assertRaises(PlanV2Rejected):
            verify_plan_v2_predecessor_closure(
                bundle, expected_bundle=control, root_identity=fixture["root"],
                allow_publication_successors=0)
        with self.assertRaises(TypeError):
            verify_plan_v2_predecessor_closure(bundle, expected_bundle=control)
        self.assertEqual(len(verify_plan_v2_predecessor_closure(
            bundle, expected_bundle=control, root_identity=fixture["root"],
            allow_publication_successors=False)), 8)


if __name__ == "__main__":
    unittest.main()
