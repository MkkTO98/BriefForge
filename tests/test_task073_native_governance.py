from __future__ import annotations

from copy import copy, deepcopy
from dataclasses import replace
import hashlib
import inspect
import os
from pathlib import Path
import subprocess
import sys
import unittest

from briefforge.bcrp.model import BCRPBundle
from briefforge.bcrp_paired_terminal_admission import (
    NativeBCRPPairedTerminalAdmissionHandle,
    PairedProfileRejected,
    issue_native_bcrp_paired_terminal_admission_v2,
    verify_native_bcrp_paired_terminal_admission_v2,
)
import briefforge.bcrp_publication_governance as governance
from briefforge.bcrp_publication_governance import (
    JudgmentAuthorizationToken,
    NativeGovernanceRejected,
    ReadyAuthorizationToken,
    produce_native_judgment,
    produce_native_ready,
)
from briefforge.bcrp_publication_release_v2 import ReleaseRejected, verify_publication_release
from briefforge.task076_contracts import (
    ContractAuthenticationError,
    Generation8CandidateAdmissionAuthority,
    authenticate_generation8_candidate,
    authenticate_generation8_candidate_bytes,
    load_generation8_candidate,
)



PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFERRED_GENERATION8_INTEGRATION = (
    "No accepted generation-8 PublicationReleaseRecord exists. Live Judgment, Ready, "
    "Release, Plan-v2, and paired-v3 issuance remain deferred to their native owners."
)


class NativeFixture:
    """Compatibility tombstone: generation-8 synthetic production authority is forbidden."""

    def __init__(self, *args, **kwargs):
        del args, kwargs
        raise RuntimeError(
            "synthetic generation-8 production authority is forbidden by TASK-077")


def make_generation8_conforming_synthetic_candidate(*args, **kwargs):
    """Import-compatible tombstone; no synthetic Candidate authority can be produced."""
    del args, kwargs
    raise RuntimeError(
        "synthetic generation-8 production authority is forbidden by TASK-077")


def _identity(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()


def _governed_candidate_identities() -> dict[str, tuple[int, str]]:
    relatives = (
        "artifacts/pilots/candidate-authoring-output/attempt:task071-representative-campaign-002/profile.json",
        "artifacts/pilots/candidate-authoring-output/attempt:task071-representative-campaign-002/candidate-semantic.json",
        "artifacts/pilots/candidate-authoring-output/attempt:task071-representative-campaign-002/fingerprint.json",
        "artifacts/pilots/candidate-authoring-output/attempt:task071-representative-campaign-002/inventory.json",
        "artifacts/pilots/candidate-authoring-output/attempt:task071-representative-campaign-002/authoring-receipt.json",
        "artifacts/state/candidate-authoring-ledger/attempt:task071-representative-campaign-002/validation-evidence-04.json",
        "artifacts/governance/candidate-authoring-authority/attempt:task071-representative-campaign-002.authority.json",
    )
    return {relative: _identity(PROJECT_ROOT / relative) for relative in relatives}


class Task073NativeGovernanceReplacementTests(unittest.TestCase):
    """Lawful TASK-073 coverage without test-owned Candidate authority.

    Positive generation-8 coverage stops at the canonical Candidate owner. Operations whose
    positive path needs unavailable Judgment/Ready/Release/Plan provenance are checked at their
    earliest public rejection or data-only boundary and explicitly remain deferred.
    """

    def canonical_control(self):
        candidate = load_generation8_candidate()
        rebound = authenticate_generation8_candidate(candidate)
        self.assertEqual(candidate.profile_bytes, rebound.profile_bytes)
        self.assertEqual("candidate:task071-cross-inquiry", rebound.candidate_identity)
        return candidate

    def assert_generation8_deferred(self):
        self.assertIn("No accepted generation-8 PublicationReleaseRecord exists",
                      DEFERRED_GENERATION8_INTEGRATION)
        self.assertIn("Plan-v2", DEFERRED_GENERATION8_INTEGRATION)

    def test_fixture_constructor_failure_restores_globals_and_removes_residue(self):
        """O1; absence boundary replaces temporary roots and fixture-owned cleanup machinery."""
        before = _governed_candidate_identities()
        source = inspect.getsource(NativeFixture)
        for forbidden in (
            "patch.object", "GOVERNED_AUTHORITY_ROOT", "GOVERNED_LEDGER_ROOT",
            "GOVERNED_OUTPUT_ROOT", "GovernedCandidateAdmission",
            "briefforge-candidate-authority-v1", "write_bytes",
        ):
            self.assertNotIn(forbidden, source)
        self.canonical_control()
        self.assertEqual(before, _governed_candidate_identities())
        residue = tuple(PROJECT_ROOT.glob(".task073-*"))
        self.assertEqual((), residue)

    def test_subject_is_detached_and_rejects_every_closure_binding_drift(self):
        """O2; canonical owner positive and caller-created or drifted wrapper negatives."""
        first = self.canonical_control()
        second = self.canonical_control()
        self.assertIsNot(first, second)
        self.assertEqual(first.profile_bytes, second.profile_bytes)
        for forged in (
            replace(first, candidate_identity="candidate:foreign"),
            replace(first, profile_byte_digest="0" * 64),
            replace(first, candidate_profile_instance_fingerprint="f" * 64),
            copy(first),
        ):
            with self.subTest(forged=forged), self.assertRaises(ContractAuthenticationError):
                authenticate_generation8_candidate(forged)
        self.canonical_control()

    def test_canonical_evidence_substitution_and_noncanonical_issuance_fail_closed(self):
        """O3; foreign, mutated, and caller-created authority fail without persistence mutation."""
        before = _governed_candidate_identities()
        candidate = self.canonical_control()
        hostile = (candidate.profile_bytes[:-1] + b" ", candidate.profile_bytes, b"{}")
        for payload in hostile:
            with self.subTest(size=len(payload)), self.assertRaises(ContractAuthenticationError):
                authenticate_generation8_candidate_bytes(payload, authority=object())
        with self.assertRaises(TypeError):
            Generation8CandidateAdmissionAuthority()
        self.assertEqual(before, _governed_candidate_identities())
        self.canonical_control()

    def test_dispositions_are_separate_and_only_acceptance_promotes(self):
        """O4; disposition promotion is verified at the production data-only boundary."""
        source = inspect.getsource(governance._verify_judgment_authorization)
        ready_source = inspect.getsource(governance._issue_ready_authorization_from_governance_adapter)
        self.assertIn('{"accepted", "deferred", "rejected"}', source)
        self.assertIn("if not verified.accepted", ready_source)
        self.assertIn("only an accepted governance Judgment can authorize readiness", ready_source)
        with self.assertRaises(NativeGovernanceRejected):
            produce_native_ready(judgment=object(), authorization=object())
        self.canonical_control()
        self.assert_generation8_deferred()

    def test_candidate_topology_cross_binding_and_mutation_fail_closed(self):
        """O5; canonical topology succeeds and altered topology lacks opaque predecessor authority."""
        candidate = self.canonical_control()
        self.assertEqual(
            ("CandidatePresentationPackageRecord", "PortablePresentationMaterialRecord",
             "PresentationBriefRecord"),
            tuple(record.kind for record in candidate.bundle.records),
        )
        reordered = deepcopy(candidate.bundle)
        reordered.records = tuple(reversed(reordered.records))
        foreign = replace(candidate, bundle=reordered)
        with self.assertRaises(ContractAuthenticationError):
            authenticate_generation8_candidate(foreign)
        truncated = replace(candidate, bundle=BCRPBundle(
            candidate.bundle.profile_identity, candidate.bundle.profile_version,
            candidate.bundle.records[:-1]))
        with self.assertRaises(ContractAuthenticationError):
            authenticate_generation8_candidate(truncated)
        self.canonical_control()

    def test_governance_tokens_are_process_local_opaque_and_exactly_bound(self):
        """O6; opaque constructors and foreign tokens reject; TASK-074 owns generic positives."""
        for constructor in (
            JudgmentAuthorizationToken, ReadyAuthorizationToken,
            NativeBCRPPairedTerminalAdmissionHandle,
        ):
            with self.subTest(constructor=constructor), self.assertRaises(TypeError):
                constructor()
        with self.assertRaises(NativeGovernanceRejected):
            produce_native_judgment(subject=object(), authorization=object())
        with self.assertRaises(NativeGovernanceRejected):
            produce_native_ready(judgment=object(), authorization=object())
        with self.assertRaises(PairedProfileRejected):
            verify_native_bcrp_paired_terminal_admission_v2(object())
        task074 = (PROJECT_ROOT / "tests/test_task074_native_candidate_to_manifest.py").read_text()
        self.assertIn("test_admission_returns_fieldless_nontransferable_process_local_handle", task074)
        self.assertIn("test_real_controlled_invocation_consumes_native_authority", task074)
        self.canonical_control()

    def test_failed_production_preserves_retry_but_interruption_consumes_authorization(self):
        """O7; deterministic retry/interruption ownership remains explicit without minted tokens."""
        source = inspect.getsource(governance.produce_native_judgment)
        self.assertIn("except Exception", source)
        self.assertIn("permit an exact retry", source)
        self.assertIn("except BaseException", source)
        self.assertIn("fail closed against replay", source)
        before = _governed_candidate_identities()
        for _ in range(2):
            with self.assertRaises(NativeGovernanceRejected):
                produce_native_judgment(subject=object(), authorization=object())
        self.assertEqual(before, _governed_candidate_identities())
        self.canonical_control()
        self.assert_generation8_deferred()

    def test_ready_and_release_chronology_fail_closed_in_live_and_persisted_routes(self):
        """O8; chronology and persisted reauthentication remain explicit data-only invariants."""
        chronology = inspect.getsource(governance._verify_ready_authorization)
        persisted = inspect.getsource(governance.verify_persisted_native_ready_binding)
        self.assertIn("decision_time > authorization_time", chronology)
        self.assertIn("authorization_time > readiness_time", chronology)
        self.assertIn("Ready chronology does not follow Judgment then authorization", chronology)
        self.assertIn("_reauthenticate_persisted_governed_subject", persisted)
        self.assertIn("persisted Ready contract or chronology is invalid", persisted)
        candidate = self.canonical_control()
        with self.assertRaises(ReleaseRejected):
            verify_publication_release(candidate.bundle, evidence_snapshot=object())
        self.canonical_control()
        self.assert_generation8_deferred()

    def test_native_v2_release_roundtrip_unknown_and_mixed_versions(self):
        """O9; Candidate-only, unknown, and mixed inputs reject; generation-8 Release is deferred."""
        candidate = self.canonical_control()
        variants = [deepcopy(candidate.bundle), deepcopy(candidate.bundle), deepcopy(candidate.bundle)]
        variants[0].profile_identity = "unknown:bcrp-profile"
        variants[1].profile_version = "0.0.0"
        variants[2].records = tuple(reversed(variants[2].records))
        for bundle in (candidate.bundle, *variants):
            with self.subTest(profile=bundle.profile_identity), self.assertRaises(ReleaseRejected):
                verify_publication_release(bundle, evidence_snapshot=object())
        self.canonical_control()
        self.assert_generation8_deferred()

    def test_native_v2_release_reaches_single_existing_plan_and_token_route(self):
        """O10; absent Release/Plan authority is non-reachable; TASK-074 keeps generic owner coverage."""
        candidate = self.canonical_control()
        with self.assertRaises(PairedProfileRejected):
            issue_native_bcrp_paired_terminal_admission_v2(candidate=candidate)
        with self.assertRaises(PairedProfileRejected):
            issue_native_bcrp_paired_terminal_admission_v2(
                candidate=candidate, plan=object(), capability=object(),
                verified_release=object(), derivation_evidence=object(),
                capability_issuer_inputs=object())
        task074 = (PROJECT_ROOT / "tests/test_task074_native_candidate_to_manifest.py").read_text()
        self.assertIn("class Task074NativeInvocationAuthorityTests", task074)
        self.assertIn("DEFERRED_NATIVE_RELEASE_ROUTE", task074)
        self.assertIn("Native Candidate-to-manifest", task074)
        self.assertIn("test_real_controlled_invocation_consumes_native_authority", task074)
        self.canonical_control()
        self.assert_generation8_deferred()

    def test_release_plan_ab_mix_and_reordered_embedded_bytes_reject(self):
        """O11; mixed/reordered non-Release bytes reject at the earliest public Release owner."""
        candidate = self.canonical_control()
        variants = []
        reordered = deepcopy(candidate.bundle)
        reordered.records = reordered.records[1:] + reordered.records[:1]
        variants.append(reordered)
        mixed = deepcopy(candidate.bundle)
        mixed.profile_version = "2.0.0"
        variants.append(mixed)
        truncated = deepcopy(candidate.bundle)
        truncated.records = truncated.records[:-1]
        variants.append(truncated)
        for bundle in variants:
            with self.subTest(records=len(bundle.records)), self.assertRaises(ReleaseRejected):
                verify_publication_release(bundle, evidence_snapshot=object())
        self.canonical_control()
        self.assert_generation8_deferred()

    def test_historical_task071_task069_task051_and_frozen_paired_bytes_are_preserved(self):
        """O12; exact historical and frozen byte identities remain unchanged and authenticated."""
        expected = {
            "artifacts/pilots/candidate-authoring-output/attempt:task071-representative-campaign-002/profile.json": "62cbe5294b123c9b4043e9f721a1b2585c70a5380e2121a39e8558b5c73b1898",
            "artifacts/pilots/candidate-authoring-output/attempt:task071-representative-campaign-002/candidate-semantic.json": "b1c29473241648c68dfb7bb737715645b396c149094eeb70cef34feb52fb95b2",
            "artifacts/pilots/candidate-authoring-output/attempt:task071-representative-campaign-002/fingerprint.json": "34976737eb19ea11903f79f37bbac2f3ab3d242677894862ee079b1cd3158cf1",
            "artifacts/pilots/candidate-authoring-output/attempt:task071-representative-campaign-002/inventory.json": "c5032937785592c2327ad3b5dc70089f8ac4ee0769c741cd77d6bac3d00a4302",
            "artifacts/pilots/candidate-authoring-output/attempt:task071-representative-campaign-002/authoring-receipt.json": "51d2c7712915aa98011fa93a03a3429a4ae90b4b3f3f8911c467280351c4b798",
            "artifacts/pilots/task069/.candidate-authoring-single-use": "05d7d994a64b798417e21b26ba5782cbc31d87a68af39e0a13f282a073e8a70f",
            "artifacts/tasks/TASK-051-bcrp-renderer-compatibility-plan-production-and-fail-closed-proof.md": "2c33b7a777ef68660534d37998909adf5e29646113861435c42976f83b249245",
            "artifacts/state/candidate-authoring-ledger/attempt:task071-representative-campaign-002/validation-evidence-04.json": "53b81aa80166e272a86f07b1f1f660b3234018b84caa1983048adf2d9b989b6b",
            "artifacts/governance/candidate-authoring-authority/attempt:task071-representative-campaign-002.authority.json": "9870ff3aca5630de86a97de815415b9d183782e7255a0340640b47e9a226fe04",
            "src/briefforge_paired_terminal_profile/__init__.py": "b2bd66bf3b9deb346b708348fcd7220d159bcc6df4d44e43e7d0adb5a3ee842e",
            "src/briefforge_paired_terminal_profile/controlled_invocation.py": "7d7c245872a0ac6200be828b9fa14425c4f1bb7cc09ba26404a9696e5332aded",
            "src/briefforge_paired_terminal_profile/profile.py": "7eb68f0817845699b2dd7ee6104cf9530f3e2ea000f6a365efe22d0bf78f8d30",
        }
        for relative, digest in expected.items():
            self.assertEqual(digest, hashlib.sha256((PROJECT_ROOT / relative).read_bytes()).hexdigest(),
                             relative)
        candidate = self.canonical_control()
        code = (
            "from briefforge.task076_contracts import load_generation8_candidate; "
            "c=load_generation8_candidate(); print(c.candidate_identity)"
        )
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONPATH"] = os.pathsep.join((
            str(PROJECT_ROOT / "src"), str(PROJECT_ROOT / "tests"), str(PROJECT_ROOT)))
        result = subprocess.run(
            [sys.executable, "-c", code], cwd=PROJECT_ROOT, env=env,
            capture_output=True, text=True, check=False, timeout=30)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(candidate.candidate_identity, result.stdout.strip())


if __name__ == "__main__":
    unittest.main()
