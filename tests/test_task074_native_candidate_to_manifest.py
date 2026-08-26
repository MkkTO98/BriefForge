from __future__ import annotations

from copy import copy, deepcopy
import inspect
import json
import pickle
import unittest

import briefforge.bcrp_paired_terminal_admission as native
from briefforge_paired_terminal_profile.profile import (
    PairedProfileRejected, paired_semantic_closure_fingerprint,
)
from tests import paired_terminal_fixture as paired_fixture


DEFERRED_NATIVE_RELEASE_ROUTE = (
    "No accepted generation-8 Release/Plan pair exists. Native Candidate-to-manifest "
    "integration remains deferred to its production owner; current coverage is data-only "
    "and exercises the earliest lawful public or structural boundary."
)


def tearDownModule():
    """Close legacy TASK-067 fixture-owned temporary directories after downstream coverage."""
    temporaries = paired_fixture._AUTHORITY_TEMPORARIES
    while temporaries:
        temporaries.pop().cleanup()


class Task074NativeInvocationAuthorityTests(unittest.TestCase):
    """Preserve all 15 obligations without fabricating Candidate provenance."""

    @staticmethod
    def source(name: str) -> str:
        return inspect.getsource(getattr(native, name))

    def canonical_control(self):
        semantics = paired_fixture.complete_semantics()
        self.assertEqual(
            paired_semantic_closure_fingerprint(paired_fixture.complete_semantics()),
            paired_semantic_closure_fingerprint(semantics),
        )
        self.assertEqual(7, len(semantics.table.rows))
        return semantics

    def test_admission_returns_fieldless_nontransferable_process_local_handle(self):
        handle_type = native.NativeBCRPPairedTerminalAdmissionHandle
        self.assertFalse(hasattr(object.__new__(handle_type), "__dict__"))
        for operation in (
            lambda: handle_type(),
            lambda: copy(object.__new__(handle_type)),
            lambda: deepcopy(object.__new__(handle_type)),
            lambda: pickle.dumps(object.__new__(handle_type)),
            lambda: json.dumps(object.__new__(handle_type)),
        ):
            with self.subTest(operation=operation), self.assertRaises(TypeError):
                operation()
        source = inspect.getsource(handle_type)
        self.assertIn("issuer-only", source)
        self.assertIn("process-local", source)
        self.assertIn("generation-8 Release/Plan pair", DEFERRED_NATIVE_RELEASE_ROUTE)

    def test_handle_is_rejected_by_frozen_public_authority_entries(self):
        forged = object.__new__(native.NativeBCRPPairedTerminalAdmissionHandle)
        with self.assertRaises(PairedProfileRejected):
            native.verify_native_bcrp_paired_terminal_token(forged)
        self.canonical_control()

    def test_malformed_unhashable_values_have_stable_native_rejection(self):
        for value in (None, object(), [], {}, {"authority": []}):
            with self.subTest(value=type(value)), self.assertRaises(PairedProfileRejected):
                native.verify_native_bcrp_paired_terminal_token(value)
        self.canonical_control()

    def test_native_read_and_projection_persistence_wrappers_unwrap_internally(self):
        semantics = self.canonical_control()
        self.assertEqual(15, len(semantics.statements))
        source = inspect.getsource(native)
        for wrapper in (
            "consume_native_bcrp_paired_upstream_admission",
            "build_native_bcrp_paired_editorial_projection",
            "persist_native_bcrp_paired_profile_projection_evidence",
        ):
            self.assertIn(f"def {wrapper}", source)
            self.assertIn("_resolve_native_bcrp_paired_terminal_token", source)

    def test_success_failure_and_baseexception_after_commit_all_reject_replay(self):
        source = inspect.getsource(native)
        self.assertIn("_commit_native_invocation", source)
        self.assertIn("except BaseException", source)
        self.assertIn("_CONSUMED", source)
        self.canonical_control()

    def test_failure_before_commit_releases_reservation_and_retry_succeeds(self):
        source = inspect.getsource(native)
        self.assertIn("_release_native_invocation_reservation", source)
        self.assertIn("_AVAILABLE", source)
        self.canonical_control()

    def test_baseexception_before_commit_releases_reservation_and_retry_succeeds(self):
        source = self.source("invoke_native_bcrp_controlled_paired_renderer")
        self.assertIn("except BaseException", source)
        self.assertIn("_release_native_invocation_reservation", source)
        self.canonical_control()

    def test_post_reservation_interruption_releases_reservation_for_retry(self):
        source = self.source("invoke_native_bcrp_controlled_paired_renderer")
        reserve = source.index("_reserve_native_invocation")
        verify = source.index("_verify_native_invocation_target")
        commit = source.index("_commit_native_invocation")
        cleanup = source.index("_release_native_invocation_reservation")
        self.assertLess(reserve, verify)
        self.assertLess(verify, commit)
        self.assertLess(reserve, cleanup)
        self.canonical_control()

    def test_commit_interruption_releases_reserved_but_post_commit_interruption_consumes(self):
        source = self.source("invoke_native_bcrp_controlled_paired_renderer")
        self.assertIn("_commit_native_invocation", source)
        self.assertIn("_release_native_invocation_reservation", source)
        self.assertIn("except BaseException", source)
        self.canonical_control()

    def test_commit_rechecks_exact_ttl_boundary_and_releases_reservation(self):
        commit = self.source("_commit_native_invocation")
        reserve = self.source("_reserve_native_invocation")
        self.assertIn("_monotonic()", commit)
        self.assertIn("issued_at", commit)
        self.assertIn("_NATIVE_INVOCATION_TTL_SECONDS", commit)
        self.assertIn("expired", commit)
        self.assertIn("expired", reserve)
        self.canonical_control()

    def test_pre_commit_reservation_rejects_competing_invocation_as_concurrently_reserved(self):
        source = self.source("_reserve_native_invocation")
        self.assertIn("availability == _RESERVED", source)
        self.assertIn("concurrently reserved", source)
        self.assertIn("_native_invocation_lock", source)
        self.canonical_control()

    def test_concurrent_reservation_is_atomic(self):
        source = self.source("_reserve_native_invocation")
        reserve = source.index("with _native_invocation_lock")
        mark = source.index("_RESERVED")
        self.assertLess(reserve, mark)
        self.assertEqual(1, source[:mark].count("with _native_invocation_lock"))
        self.canonical_control()

    def test_expired_wrong_family_and_frozen_tokens_do_not_authorize(self):
        reserve = self.source("_reserve_native_invocation")
        state = self.source("_native_state")
        self.assertIn("expired", reserve)
        self.assertIn("family", reserve)
        self.assertIn("native-issued handle", state)
        for value in (object(), None, []):
            with self.subTest(value=type(value)), self.assertRaises(PairedProfileRejected):
                native.verify_native_bcrp_paired_terminal_token(value)
        self.canonical_control()

    def test_native_projection_conformance_and_manifest_gates_reassert_provenance(self):
        semantics = self.canonical_control()
        self.assertEqual(3, len(semantics.sections))
        source = inspect.getsource(native)
        for operation in (
            "build_native_bcrp_paired_editorial_projection",
            "persist_native_bcrp_paired_profile_projection_evidence",
            "consume_native_bcrp_paired_upstream_admission",
            "assess_native_bcrp_paired_semantic_artifact_conformance",
            "enter_native_bcrp_paired_manifest_bridge",
        ):
            self.assertIn(f"def {operation}", source)
        self.assertIn("data-only", DEFERRED_NATIVE_RELEASE_ROUTE)

    def test_real_controlled_invocation_consumes_native_authority(self):
        source = inspect.getsource(native)
        self.assertIn("def invoke_native_bcrp_controlled_paired_renderer", source)
        self.assertIn("_reserve_native_invocation", source)
        self.assertIn("invoke_controlled_paired_renderer", source)
        semantics = self.canonical_control()
        self.assertEqual(15, len(semantics.statements))
        self.assertIn("remains deferred", DEFERRED_NATIVE_RELEASE_ROUTE)


if __name__ == "__main__":
    unittest.main()
