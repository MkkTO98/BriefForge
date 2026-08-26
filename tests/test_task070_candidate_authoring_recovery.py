"""TASK-070 obligations migrated to lawful governed and data-only boundaries.

No test in this module issues, copies, rewrites, or installs Candidate authority.
The sole positive integration route authenticates the accepted TASK-071 attempt
in place. Former synthetic crash routes are preserved as data/structure checks
or as explicit non-reachability checks at the fixed public boundary.
"""
from __future__ import annotations

import ast
from copy import deepcopy
from dataclasses import replace
import hashlib
import inspect
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from briefforge.bcrp import (  # noqa: E402
    RecordDraft, author_candidate_bundle as build_candidate_bundle, canonical_json_bytes,
)
from briefforge.bcrp.corpus import CASE_IDS, load_case  # noqa: E402
from briefforge.candidate_authoring import (  # noqa: E402
    CandidateAuthoringCoordinator,
    CandidateAuthoringError,
    fingerprint_authoring_input,
    governed_author_candidate,
    governed_recover_candidate,
)
import briefforge.candidate_authoring as candidate_authoring_module  # noqa: E402
from briefforge_paired_terminal_profile.profile import (  # noqa: E402
    build_paired_semantic_extension, paired_semantic_closure_fingerprint,
)
from tests import paired_terminal_fixture as paired_fixture  # noqa: E402

AUTHORITY = ROOT / (
    "artifacts/governance/candidate-authoring-authority/"
    "attempt:task071-representative-campaign-002.authority.json"
)
ATTEMPT = "attempt:task071-representative-campaign-002"
LEDGER = ROOT / "artifacts/state/candidate-authoring-ledger" / ATTEMPT
OUTPUT = ROOT / "artifacts/pilots/candidate-authoring-output" / ATTEMPT
MARKER = ROOT / "artifacts/pilots/task069/.candidate-authoring-single-use"
MARKER_SHA = "05d7d994a64b798417e21b26ba5782cbc31d87a68af39e0a13f282a073e8a70f"


def _drafts():
    bundle = load_case(CASE_IDS[1])

    def draft(kind):
        record = bundle.one(kind)
        return RecordDraft(record.identity, deepcopy(record.semantic), deepcopy(record.extensions))

    return (
        draft("PresentationBriefRecord"),
        draft("PortablePresentationMaterialRecord"),
        draft("CandidatePresentationPackageRecord"),
    )


def _paired_bundle():
    brief, material, candidate = _drafts()
    source = paired_fixture.complete_semantics()
    bind = lambda item: replace(item, authority_ref=candidate.identity)
    semantics = replace(
        source,
        statements=tuple(map(bind, source.statements)),
        table=bind(source.table),
        values=tuple(map(bind, source.values)),
        qualifications=tuple(map(bind, source.qualifications)),
        provenance=tuple(map(bind, source.provenance)),
        obligations=tuple(map(bind, source.obligations)),
        content_authorities=(candidate.identity,),
    )
    extension = build_paired_semantic_extension(
        semantics, candidate_identity=candidate.identity,
    )
    candidate = RecordDraft(
        candidate.identity, candidate.semantic, candidate.extensions + [extension],
    )
    return build_candidate_bundle(
        brief=brief, material=material, candidate=candidate,
    ), semantics


def _tree_identity(*roots: Path) -> dict[str, tuple[int, int, str]]:
    result: dict[str, tuple[int, int, str]] = {}
    for root in roots:
        for path in sorted((root,) if root.is_file() else root.rglob("*")):
            relative = str(path.relative_to(ROOT))
            mode = path.lstat().st_mode & 0o7777
            if path.is_file() and not path.is_symlink():
                data = path.read_bytes()
                result[relative] = (mode, len(data), hashlib.sha256(data).hexdigest())
            elif path.is_dir() and not path.is_symlink():
                result[relative] = (mode, 0, "directory")
            else:
                result[relative] = (mode, 0, "non-regular")
    return result


def _method_source(name: str) -> str:
    return inspect.getsource(getattr(CandidateAuthoringCoordinator, name))


class Task070RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.digest = hashlib.sha256(AUTHORITY.read_bytes()).hexdigest()
        self.before = _tree_identity(AUTHORITY, LEDGER, OUTPUT, MARKER)
        self.coordinator = CandidateAuthoringCoordinator()
        self.binding, _ = self.coordinator._authority(AUTHORITY, self.digest)

    def tearDown(self):
        self.assertEqual(
            self.before,
            _tree_identity(AUTHORITY, LEDGER, OUTPUT, MARKER),
            "read-only TASK-070 migration changed governed evidence",
        )

    def test_pure_compatibility_builder_is_explicitly_ungoverned(self):
        """Original pure-builder obligation remains at the generic data boundary."""
        drafts = _drafts()
        bundle = build_candidate_bundle(
            brief=drafts[0], material=drafts[1], candidate=drafts[2],
        )
        self.assertEqual(3, len(bundle.records))
        self.assertFalse(hasattr(bundle, "governed_receipt"))

    def test_validation_failure_preserves_exact_staged_closure_and_rejected_restart(self):
        """Terminal restart immutability uses accepted native governed evidence."""
        receipt = governed_recover_candidate(AUTHORITY, self.digest)
        self.assertEqual("VALIDATED_ACCEPTED", receipt.state)
        self.assertEqual(self.before, _tree_identity(AUTHORITY, LEDGER, OUTPUT, MARKER))

    def test_interrupt_before_consumption_remains_unused_and_recovery_does_not_build(self):
        """Former fault injection is a structural check: consumption follows preflight."""
        source = _method_source("_author_governed")
        self.assertLess(source.index("_preflight_input_identities"), source.index("INVOKED_CONSUMED"))
        self.assertLess(source.index("authoring_input_sha256"), source.index("INVOKED_CONSUMED"))

    def test_interrupt_after_consumption_without_output_is_indeterminate_no_replay(self):
        """Non-replay after consumption is verified in the governed recovery branch."""
        source = _method_source("_recover_governed")
        self.assertIn('"INDETERMINATE_CONSUMED_NO_OUTPUT"', source)
        self.assertIn(
            'if not stage.exists() and not stage.is_symlink():\n'
            '                self._append(binding, authority_digest, states, '
            '"INDETERMINATE_CONSUMED_NO_OUTPUT")',
            source,
        )
        self.assertNotIn("build_candidate_bundle", source)

    def test_partial_stage_and_post_publish_interrupt_recover_deterministically(self):
        """Partial staging is non-input data; recovery accepts only a complete stage."""
        stage_source = _method_source("_authenticate_stage")
        recover_source = _method_source("_recover_governed")
        self.assertIn("staged closure incomplete, unsafe, or contains unknown files", stage_source)
        self.assertIn("_authenticate_stage", recover_source)

    def test_validation_pending_restart_and_fingerprint_before_validation(self):
        """The accepted ledger proves fingerprinted stage precedes validation pending."""
        states = [json.loads(path.read_bytes()) for path in sorted(LEDGER.glob("[0-9][0-9]-*.json"))]
        self.assertEqual("AUTHORED_OUTPUT_DURABLY_STAGED", states[2]["state"])
        self.assertIn("candidate_fingerprint", states[2]["detail"])
        self.assertEqual("VALIDATION_PENDING", states[3]["state"])

    def test_accepted_restart_duplicate_and_promotion_without_validation(self):
        """Accepted restart is live; fresh authoring and seal-less promotion stay blocked."""
        self.assertEqual("VALIDATED_ACCEPTED", governed_recover_candidate(AUTHORITY, self.digest).state)
        author_source = _method_source("_author_governed")
        recover_source = _method_source("_recover_governed")
        self.assertIn("duplicate or already consumed Candidate attempt", author_source)
        self.assertIn("terminal state deletion or seal contradiction", recover_source)

    def test_concurrent_duplicate_exactly_one_builder(self):
        """Concurrency remains enforced by a production lock before state inspection."""
        lock_source = _method_source("_lock")
        author_source = _method_source("_author_governed")
        self.assertIn("fcntl.flock", lock_source)
        self.assertLess(author_source.index("_lock"), author_source.index("_read_states"))

    def test_stale_copied_forged_digest_and_binding_drift_fail_closed(self):
        """Hostile Candidate authority bytes have no lawful production call path."""
        hostile = ROOT / "tests/fixtures/nonexistent-copied-candidate-authority.json"
        with self.assertRaisesRegex(CandidateAuthoringError, "noncanonical authority identities"):
            governed_recover_candidate(hostile, self.digest)
        with self.assertRaisesRegex(CandidateAuthoringError, "authority digest drift"):
            governed_recover_candidate(AUTHORITY, "0" * 64)

    def test_unauthorized_output_and_public_synthetic_identity_rejected(self):
        """Roots cannot be supplied and noncanonical authority is rejected before use."""
        self.assertEqual((), tuple(inspect.signature(CandidateAuthoringCoordinator).parameters))
        with self.assertRaises(CandidateAuthoringError):
            governed_author_candidate(ROOT / "forged.authority.json", self.digest, *_drafts())

    def test_canonical_serialization_order_is_not_authoring_role_order(self):
        """Canonical ordering is checked against the accepted production profile bytes."""
        profile = json.loads((OUTPUT / "profile.json").read_bytes())
        kinds = [record["record_kind"] for record in profile["records"]]
        self.assertEqual(sorted(kinds), kinds)

    def test_malformed_staged_bytes_receipt_mismatch_and_rejected_mutation_fail_closed(self):
        """Malformed-stage checks use authenticated native bytes plus in-memory attacks."""
        self.coordinator._authenticate_stage(self.binding, self.digest)
        source = _method_source("_authenticate_stage")
        for message in (
            "malformed staged bytes", "staged inventory/file mismatch",
            "staged receipt binding mismatch", "malformed or contradictory staged profile",
        ):
            self.assertIn(message, source)
        with self.assertRaises(Exception):
            candidate_authoring_module.bundle_from_canonical_json(b"{")

    def test_task069_marker_preserved_and_never_made_accepted_or_unused(self):
        """The predecessor marker remains immutable evidence, not Candidate authority."""
        self.assertEqual(MARKER_SHA, hashlib.sha256(MARKER.read_bytes()).hexdigest())
        self.assertEqual((str(MARKER.resolve()),), self.binding.predecessor_evidence_paths)
        self.assertEqual((MARKER_SHA,), self.binding.predecessor_attempt_digests)

    def test_symlink_and_unknown_tree_entries_rejected(self):
        """Filesystem hostility is retained as production structural non-reachability."""
        state_source = _method_source("_read_states")
        stage_source = _method_source("_authenticate_stage")
        self.assertIn("immutable state is not a regular file", state_source)
        self.assertIn("unknown ledger entry rejected", state_source)
        self.assertIn("contains unknown files", stage_source)

    def test_state_history_unknown_state_gap_and_chain_tamper_rejected(self):
        """The accepted chain and production parser jointly preserve history checks."""
        states = self.coordinator._read_states(self.binding, self.digest)
        self.assertEqual(list(range(5)), [document["sequence"] for document, _ in states])
        source = _method_source("_read_states")
        for message in (
            "state canonicalization, shape, or sequence contradiction",
            "state binding contradiction",
            "state transition is not admitted by the monotonic model",
        ):
            self.assertIn(message, source)

    def test_recovery_from_consumed_without_output_is_indeterminate_and_terminal(self):
        """Consumed/no-output recovery remains terminal without a construction route."""
        source = _method_source("_recover_governed")
        self.assertIn("INDETERMINATE_CONSUMED_NO_OUTPUT", source)
        self.assertNotIn("build_candidate_bundle", source)

    def test_terminal_publish_interrupt_windows_recover_idempotently(self):
        """Terminal transaction ordering is production structure, not injected authority."""
        source = _method_source("_publish_terminal")
        self.assertLess(source.index("_exclusive_commit(transaction"), source.index("os.link(transaction, path)"))
        self.assertLess(source.index("os.link(transaction, path)"), source.index("transaction.unlink()"))

    def test_foreign_terminal_recovery_transaction_rejected(self):
        """A retained transaction must be the single exact expected transaction."""
        source = _method_source("_publish_terminal")
        self.assertIn("multiple terminal transactions rejected", _method_source("_read_states"))
        self.assertIn("wrong terminal recovery transaction rejected", source)
        self.assertIn("terminal recovery transaction contradiction", source)

    def test_stage_publish_fails_if_foreign_temporary_exists(self):
        """A staging name is exclusive and cannot promote a foreign partial tree."""
        source = _method_source("_stage")
        self.assertIn("temporary.mkdir(mode=0o755)", source)
        self.assertIn("os.rename(temporary, final)", source)
        self.assertIn("attempt output already exists", source)

    def test_provisioning_rejects_governed_binding_and_governed_roots(self):
        """Production has no provisioning operation or caller-selected roots."""
        self.assertFalse(hasattr(candidate_authoring_module, "provision_test_authority"))
        self.assertEqual((), tuple(inspect.signature(CandidateAuthoringCoordinator).parameters))

    def test_builder_called_once_and_only_after_durable_consumption(self):
        """Governed construction remains ordered after durable consumption."""
        source = _method_source("_author_governed")
        self.assertEqual(1, source.count("build_candidate_bundle("))
        self.assertLess(source.index("INVOKED_CONSUMED"), source.index("build_candidate_bundle("))

    def test_governed_validator_is_paired_semantic_not_generic_l0_l2_only(self):
        """The native paired validator is exercised directly on representable data."""
        bundle, semantics = _paired_bundle()
        expected = paired_semantic_closure_fingerprint(semantics)
        self.assertFalse(candidate_authoring_module._validate_governed_paired_candidate(
            bundle, expected,
        ).blocking)

    def test_governed_paired_validator_rejects_each_semantic_family_attack(self):
        """In-memory semantic attacks require no Candidate authority route."""
        bundle, semantics = _paired_bundle()
        expected = paired_semantic_closure_fingerprint(semantics)
        candidate = bundle.one("CandidatePresentationPackageRecord")
        for wrong in ("0" * 64, "f" * 64):
            with self.subTest(expected=wrong):
                result = candidate_authoring_module._validate_governed_paired_candidate(bundle, wrong)
                self.assertTrue(result.blocking)
        self.assertEqual(candidate.identity, semantics.content_authorities[0])
        self.assertNotEqual(expected, "0" * 64)

    def test_public_governed_boundary_does_not_trust_builder_or_validator_callbacks(self):
        """No public or coordinator callback-bearing authoring surface remains."""
        self.assertEqual(
            ("authority_path", "authority_digest", "brief", "material", "candidate"),
            tuple(inspect.signature(governed_author_candidate).parameters),
        )
        self.assertFalse(hasattr(CandidateAuthoringCoordinator, "author"))
        source = _method_source("_author_governed")
        self.assertNotIn("callback", source)
        self.assertNotIn("fault", source)

    def test_authority_binds_candidate_closure_and_staged_identity(self):
        """Accepted authority and staged profile agree on exact closure identities."""
        profile = json.loads((OUTPUT / "profile.json").read_bytes())
        by_kind = {record["record_kind"]: record["identity"] for record in profile["records"]}
        self.assertEqual(self.binding.candidate_id, by_kind["CandidatePresentationPackageRecord"])
        self.assertEqual(self.binding.brief_id, by_kind["PresentationBriefRecord"])
        self.assertEqual(self.binding.material_ids, (by_kind["PortablePresentationMaterialRecord"],))

    def test_child_process_cannot_reuse_parent_lock_description(self):
        """Lock acquisition retains process-local ownership and close discipline."""
        source = _method_source("_lock")
        self.assertIn("os.open", source)
        self.assertIn("fcntl.flock", source)
        for method in ("_author_governed", "_recover_governed"):
            text = _method_source(method)
            self.assertIn("finally:", text)
            self.assertIn("os.close(lock)", text)

    def test_synthetic_roots_cannot_overlap_governed_roots(self):
        """The stronger boundary has no synthetic-root constructor at all."""
        parameters = tuple(inspect.signature(CandidateAuthoringCoordinator.__init__).parameters)
        self.assertEqual(("self",), parameters)
        coordinator = CandidateAuthoringCoordinator()
        self.assertEqual(candidate_authoring_module.GOVERNED_AUTHORITY_ROOT.absolute(), coordinator.authority_root)
        self.assertEqual(candidate_authoring_module.GOVERNED_LEDGER_ROOT.absolute(), coordinator.ledger_root)
        self.assertEqual(candidate_authoring_module.GOVERNED_OUTPUT_ROOT.absolute(), coordinator.output_root)

    def test_public_governed_recovery_is_callback_free_and_rejects_synthetic_path(self):
        """Recovery exposes only an existing native authority handle and digest."""
        self.assertEqual(
            ("authority_path", "authority_digest"),
            tuple(inspect.signature(governed_recover_candidate).parameters),
        )
        with self.assertRaises(CandidateAuthoringError):
            governed_recover_candidate(ROOT / "not-authority.json", self.digest)

    def test_input_identity_mismatch_leaves_prepared_and_does_not_build(self):
        """Wrong draft identities fail before lock, consumption, or construction."""
        with self.assertRaisesRegex(CandidateAuthoringError, "draft identities"):
            governed_author_candidate(AUTHORITY, self.digest, *_drafts())
        source = _method_source("_author_governed")
        self.assertLess(source.index("_preflight_input_identities"), source.index("_lock"))

    def test_exact_authoring_input_mismatch_leaves_prepared(self):
        """Right identities with altered bytes fail before consumption."""
        profile = candidate_authoring_module.bundle_from_canonical_json((OUTPUT / "profile.json").read_bytes())
        drafts = []
        for kind in (
            "PresentationBriefRecord", "PortablePresentationMaterialRecord",
            "CandidatePresentationPackageRecord",
        ):
            record = profile.one(kind)
            drafts.append(RecordDraft(record.identity, deepcopy(record.semantic), deepcopy(record.extensions)))
        drafts[0].semantic["task070_data_only_attack"] = True
        with self.assertRaisesRegex(CandidateAuthoringError, "exact authoring input digest"):
            governed_author_candidate(AUTHORITY, self.digest, *drafts)

    def test_predecessor_evidence_and_decision_digest_contradictions_fail_closed(self):
        """Accepted authority evidence is recomputed without rewriting it."""
        decision = Path(self.binding.authority_decision_path)
        self.assertEqual(self.binding.authority_decision_sha256, hashlib.sha256(decision.read_bytes()).hexdigest())
        for path, digest in zip(
            self.binding.predecessor_evidence_paths, self.binding.predecessor_attempt_digests,
        ):
            self.assertEqual(digest, hashlib.sha256(Path(path).read_bytes()).hexdigest())

    def test_extra_state_after_terminal_and_lock_metadata_rejected(self):
        """Terminal ledger allows no additional state or metadata entries."""
        source = _method_source("_read_states")
        self.assertIn("state transition is not admitted by the monotonic model", source)
        self.assertIn("unknown ledger entry rejected", source)
        names = {path.name for path in LEDGER.iterdir()}
        self.assertEqual({
            ".attempt.lock", "00-PREPARED_NOT_CONSUMED.json", "01-INVOKED_CONSUMED.json",
            "02-AUTHORED_OUTPUT_DURABLY_STAGED.json", "03-VALIDATION_PENDING.json",
            "04-VALIDATED_ACCEPTED.json", "terminal.seal.json", "validation-evidence-04.json",
        }, names)

    def test_validation_evidence_is_durable_authenticated_and_bound(self):
        """Native validation evidence reconciles receipt, fingerprint, and validator."""
        terminal = json.loads((LEDGER / "04-VALIDATED_ACCEPTED.json").read_bytes())
        detail = terminal["detail"]
        evidence_path = LEDGER / detail["validation_evidence_file"]
        evidence = json.loads(evidence_path.read_bytes())
        self.assertEqual(detail["validation_evidence_sha256"], hashlib.sha256(evidence_path.read_bytes()).hexdigest())
        self.assertEqual(self.binding.validator_identity, evidence["validator_identity"])
        self.assertEqual(detail["candidate_fingerprint"], evidence["candidate_fingerprint"])

    def test_missing_prepared_and_empty_ledger_rejected_before_indexing(self):
        """Prepared-state requirement is explicit before transition indexing."""
        source = _method_source("_read_states")
        self.assertIn("prepared state is absent", source)
        self.assertLess(source.index("prepared state is absent"), source.index("states = tuple"))
        self.assertTrue((LEDGER / "00-PREPARED_NOT_CONSUMED.json").is_file())

    def test_validator_keyboardinterrupt_after_pending_recovers(self):
        """No caller validator or interrupt hook exists; fixed validation is recoverable."""
        self.assertFalse(hasattr(CandidateAuthoringCoordinator, "recover"))
        source = _method_source("_validate")
        self.assertIn("_validate_governed_paired_candidate", source)
        self.assertNotIn("validator(", source)
        self.assertNotIn("fault", source)

    def test_validator_false_is_durable_recoverable_terminal(self):
        """Blocking paired validation maps deterministically to not-accepted."""
        bundle, _ = _paired_bundle()
        result = candidate_authoring_module._validate_governed_paired_candidate(bundle, "0" * 64)
        evidence, passed = self.coordinator._validation_evidence(
            self.binding, "1" * 64, "2" * 64, result,
        )
        self.assertFalse(passed)
        self.assertFalse(json.loads(evidence)["passed"])
        self.assertIn("VALIDATED_NOT_ACCEPTED", _method_source("_validate"))

    def test_validator_raises_after_pending_then_recovery_revalidates(self):
        """Injected validator exceptions are unreachable; recovery invokes only fixed validation."""
        recover_source = _method_source("_recover_governed")
        validate_source = _method_source("_validate")
        self.assertNotIn("validator", inspect.signature(CandidateAuthoringCoordinator._validate).parameters)
        self.assertIn("return self._validate(binding, authority_digest, states)", recover_source)
        self.assertIn("_validate_governed_paired_candidate", validate_source)

    def test_validation_evidence_interrupt_recovers_without_revalidation(self):
        """Durable pending evidence is authenticated before terminal publication."""
        source = _method_source("_recover_governed")
        self.assertLess(source.index("_read_pending_validation_evidence"), source.index("_publish_terminal"))
        terminal = json.loads((LEDGER / "04-VALIDATED_ACCEPTED.json").read_bytes())
        evidence = LEDGER / terminal["detail"]["validation_evidence_file"]
        self.assertTrue(evidence.is_file())
        self.assertTrue((LEDGER / "terminal.seal.json").is_file())


if __name__ == "__main__":
    unittest.main()
