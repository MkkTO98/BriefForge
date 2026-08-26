from __future__ import annotations

import copy
from dataclasses import replace
import errno
import hashlib
import json
from pathlib import Path
import pickle
import tempfile
import unittest

from briefforge.bcrp.model import BCRPBundle, BCRPRecord
from briefforge.bcrp_paired_derivation_evidence_v2 import construct_envelope
from briefforge.bcrp_paired_terminal_admission import (
    NativeBCRPPairedTerminalAdmissionHandle,
    verify_native_bcrp_paired_terminal_admission_v2,
)
from briefforge.task076_contracts import canonical_json, domain_digest, load_generation8_candidate
from briefforge.bcrp_renderer_compatibility_planning_v2 import (
    CapabilityV2IssuerInputs,
    CapabilityV2Rejected,
    capability_declaration_family,
    construct_renderer_capability_v2,
    persist_renderer_capability_v2,
    reload_renderer_capability_v2,
    serialize_renderer_capability_v2,
    serialize_renderer_capability_v2_bundle,
    verify_renderer_capability_v2,
)
from briefforge_paired_terminal_profile.profile import PairedProfileRejected


class Task077CapabilityV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = load_generation8_candidate()
        cls.candidate_b = load_generation8_candidate()
        frozen = json.loads(Path(
            "artifacts/contracts/task076/task071-derivation-evidence-envelope.json"
        ).read_text(encoding="utf-8"))
        cls.envelope = construct_envelope(
            evidence_identity=frozen["evidence_identity"],
            operation_identity=frozen["operation_identity"],
            authorization_fingerprint=frozen["authorization_fingerprint"],
            issued_at_utc=frozen["issued_at_utc"],
            source_locator_identity=frozen["source_locator_identity"],
            candidate=cls.candidate,
        )
        cls.envelope_b = construct_envelope(
            evidence_identity="evidence:task077-capability-isolation-b",
            operation_identity="operation:task077-capability-isolation-b",
            authorization_fingerprint="b" * 64,
            issued_at_utc="2026-08-11T00:00:01Z",
            source_locator_identity="storage:task071-canonical-profile",
            candidate=cls.candidate_b,
        )
        cls.issuer = CapabilityV2IssuerInputs(
            declaration_identity="capability:task076-normative-v2",
            renderer_identity="briefforge:representative-paired-static-html-renderer:1.0.0",
            renderer_version="1.0.0",
            implementation_identity="briefforge:paired-static-html-renderer:1.0.0",
            implementation_digest="c3f898a514443ada63e68459c392d67cbe42af4ad8393c446859b45834db36f2",
            owner_identity="project:BriefForge",
            owner_role="bounded-publication-renderer",
            media_types=("text/html;charset=utf-8",),
            output_count=1,
            asset_count=0,
            table_count=1,
            column_count=5,
            declared_constraints=("deterministic", "bounded", "offline"),
            unsupported_capabilities=(),
            operation_identity="operation:task076-capability-fixture",
            authorization_fingerprint="ead882da5aa29dc7d5af416d3d5671a3a2d25cd84c53b4af2c31915842e9cb1c",
            storage_identity="storage:task076-capability-normative-bytes",
            issued_at_utc="2026-08-11T00:00:00Z",
        )
        cls.issuer_b = replace(
            cls.issuer,
            declaration_identity="capability:task077-isolation-b",
            operation_identity="operation:task077-capability-isolation-b",
            authorization_fingerprint="c" * 64,
            storage_identity="storage:task077-capability-isolation-b",
            issued_at_utc="2026-08-11T00:00:01Z",
        )

    def authority(self, **changes):
        authority = {
            "candidate": self.candidate,
            "derivation_evidence": self.envelope,
            "issuer_inputs": self.issuer,
        }
        authority.update(changes)
        return authority

    def authority_b(self, **changes):
        authority = {
            "candidate": self.candidate_b,
            "derivation_evidence": self.envelope_b,
            "issuer_inputs": self.issuer_b,
        }
        authority.update(changes)
        return authority

    def produced(self):
        return construct_renderer_capability_v2(**self.authority())

    def produced_b(self):
        return construct_renderer_capability_v2(**self.authority_b())

    def assert_not_live_authority(self, value):
        self.assertNotIsInstance(value, NativeBCRPPairedTerminalAdmissionHandle)
        with self.assertRaises(PairedProfileRejected):
            verify_native_bcrp_paired_terminal_admission_v2(value)

    def test_constructs_exact_frozen_record_and_serializes_bundle(self):
        produced = self.produced()
        frozen = Path("artifacts/contracts/task076/capability-v2-record.json").read_bytes()
        self.assertEqual(serialize_renderer_capability_v2(produced, **self.authority()), frozen)
        self.assertEqual(capability_declaration_family(produced.record), "v2")
        serialized = serialize_renderer_capability_v2_bundle(produced, **self.authority())
        admitted_bundle = verify_renderer_capability_v2(serialized, **self.authority())
        admitted_record = verify_renderer_capability_v2(frozen, **self.authority())
        admitted_value = verify_renderer_capability_v2(produced, **self.authority())
        self.assertEqual(admitted_bundle.fingerprint, produced.fingerprint)
        self.assertEqual(admitted_record.fingerprint, produced.fingerprint)
        self.assertEqual(admitted_value.fingerprint, produced.fingerprint)
        self.assertEqual(
            serialize_renderer_capability_v2_bundle(admitted_bundle, **self.authority()),
            serialized,
        )
        for value in (produced, admitted_bundle, admitted_record, serialized, frozen):
            self.assert_not_live_authority(value)
        with self.assertRaises(TypeError):
            NativeBCRPPairedTerminalAdmissionHandle()
        lookalike = object.__new__(NativeBCRPPairedTerminalAdmissionHandle)
        with self.assertRaises(PairedProfileRejected):
            verify_native_bcrp_paired_terminal_admission_v2(lookalike)
        with self.assertRaises(TypeError):
            copy.copy(lookalike)
        with self.assertRaises(TypeError):
            pickle.dumps(lookalike)

    def test_rejects_v1_core_only_unknown_mixed_duplicate_and_extra_records(self):
        v1 = BCRPRecord(
            "RendererCapabilityDeclarationRecord",
            "capability:v1",
            "1.0.0",
            {},
            [{
                "owner_namespace": "briefforge-renderer-capability",
                "name": "renderer-capability-declaration",
                "version": "1.0.0",
                "validation_contract": "briefforge:renderer-capability-declaration:1.0.0",
            }],
        )
        self.assertEqual(capability_declaration_family(v1), "v1")
        with self.assertRaises(CapabilityV2Rejected):
            verify_renderer_capability_v2(v1, **self.authority())
        for mutation in ("unknown", "mixed", "duplicate", "missing"):
            record = self.produced().record
            if mutation == "unknown":
                record.extensions[0]["name"] = "foreign"
            elif mutation == "mixed":
                record.extensions[0]["version"] = "1.0.0"
            elif mutation == "duplicate":
                record.extensions.append(record.extensions[0].copy())
            else:
                record.extensions.clear()
            with self.assertRaises(CapabilityV2Rejected, msg=mutation):
                verify_renderer_capability_v2(record, **self.authority())
        bundle = self.produced().bundle
        with self.assertRaises(CapabilityV2Rejected):
            verify_renderer_capability_v2(
                BCRPBundle(
                    bundle.profile_identity,
                    bundle.profile_version,
                    (bundle.records[0], bundle.records[0]),
                ),
                **self.authority(),
            )

    def test_rejects_altered_reordered_foreign_and_recomputed_substitution(self):
        altered = self.produced().record
        altered.extensions[0]["payload"]["column_count"] = 6
        reordered = self.produced().record
        reordered.semantic["capabilities"] = list(reversed(reordered.semantic["capabilities"]))
        correlated = self.produced().record
        correlated.semantic["renderer_id"] = "renderer:foreign"
        payload = correlated.extensions[0]["payload"]
        payload["renderer_identity"] = "renderer:foreign"
        payload["semantic_digest"] = domain_digest(
            "briefforge.task076.capability-core-semantic.v1", correlated.semantic
        )
        payload["fingerprint"] = domain_digest(
            "briefforge.task075.capability-declaration.v2",
            {key: value for key, value in payload.items() if key != "fingerprint"},
        )
        for record in (altered, reordered, correlated):
            with self.assertRaises(CapabilityV2Rejected):
                verify_renderer_capability_v2(record, **self.authority())
        with self.assertRaises(CapabilityV2Rejected):
            verify_renderer_capability_v2(
                self.produced(),
                **self.authority(
                    issuer_inputs=replace(self.issuer, authorization_fingerprint="2" * 64)
                ),
            )
        serialized = serialize_renderer_capability_v2_bundle(self.produced(), **self.authority())
        document = json.loads(serialized)
        reordered_document = dict(reversed(tuple(document.items())))
        attacks = (
            serialized[:-1],
            json.dumps(reordered_document, separators=(",", ":")).encode("utf-8"),
            canonical_json({**document, "profile_identity": "bcrp:foreign"}),
        )
        for attack in attacks:
            with self.assertRaises(CapabilityV2Rejected):
                verify_renderer_capability_v2(attack, **self.authority())

    def test_rejects_foreign_candidate_and_recomputed_envelope(self):
        with self.assertRaises(TypeError):
            copy.deepcopy(self.candidate)
        for copied in (
            replace(self.candidate, profile_byte_digest="0" * 64),
            copy.copy(self.candidate),
        ):
            with self.assertRaises(CapabilityV2Rejected):
                construct_renderer_capability_v2(**self.authority(candidate=copied))
        foreign = self.envelope.to_document()
        foreign["core_graph_digest"] = "0" * 64
        foreign["fingerprint"] = domain_digest(
            "briefforge.task076.derivation-evidence.v2",
            {key: value for key, value in foreign.items() if key != "fingerprint"},
        )
        with self.assertRaises(CapabilityV2Rejected):
            construct_renderer_capability_v2(**self.authority(derivation_evidence=foreign))

    def test_exclusive_persistence_reload_stale_and_residue_rejection(self):
        produced_a = self.produced()
        produced_b = self.produced_b()
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            directory_a = root / "a"
            directory_b = root / "b"
            directory_a.mkdir()
            directory_b.mkdir()
            persisted_a = persist_renderer_capability_v2(
                produced_a, directory=directory_a, **self.authority()
            )
            persisted_b = persist_renderer_capability_v2(
                produced_b, directory=directory_b, **self.authority_b()
            )
            bytes_a = persisted_a.path.read_bytes()
            bytes_b = persisted_b.path.read_bytes()

            # A1, B1: each closure reloads only against independently supplied inputs.
            a1 = reload_renderer_capability_v2(
                persisted_a.path,
                persistence_receipt=persisted_a,
                expected_sha256=persisted_a.sha256,
                expected_fingerprint=persisted_a.fingerprint,
                expected_bundle_fingerprint=persisted_a.bundle_fingerprint,
                **self.authority(),
            )
            b1 = reload_renderer_capability_v2(
                persisted_b.path,
                persistence_receipt=persisted_b,
                expected_sha256=persisted_b.sha256,
                expected_fingerprint=persisted_b.fingerprint,
                expected_bundle_fingerprint=persisted_b.bundle_fingerprint,
                **self.authority_b(),
            )
            original_receipt_a = persisted_a
            for receipt_field in ("fingerprint", "bundle_fingerprint"):
                with self.subTest(forged_receipt_field=receipt_field):
                    control_before = reload_renderer_capability_v2(
                        persisted_a.path,
                        persistence_receipt=persisted_a,
                        **self.authority(),
                    )
                    forged_receipt = replace(
                        persisted_a,
                        **{receipt_field: "0" * 64},
                    )
                    rejection = None
                    probe_result = None
                    try:
                        probe_result = reload_renderer_capability_v2(
                            persisted_a.path,
                            persistence_receipt=forged_receipt,
                            **self.authority(),
                        )
                    except CapabilityV2Rejected as exc:
                        rejection = exc
                    control_after = reload_renderer_capability_v2(
                        persisted_a.path,
                        persistence_receipt=persisted_a,
                        **self.authority(),
                    )
                    self.assertEqual(persisted_a, original_receipt_a)
                    self.assertEqual(persisted_a.path.read_bytes(), bytes_a)
                    self.assertEqual(persisted_b.path.read_bytes(), bytes_b)
                    self.assertEqual(
                        serialize_renderer_capability_v2_bundle(
                            control_before, **self.authority()
                        ),
                        serialize_renderer_capability_v2_bundle(
                            control_after, **self.authority()
                        ),
                    )
                    self.assertEqual(
                        serialize_renderer_capability_v2_bundle(a1, **self.authority()),
                        serialize_renderer_capability_v2_bundle(
                            control_after, **self.authority()
                        ),
                    )
                    if probe_result is not None:
                        self.assert_not_live_authority(probe_result)
                    self.assertIsNotNone(
                        rejection,
                        f"forged receipt {receipt_field} was incorrectly accepted",
                    )
            with self.assertRaises(CapabilityV2Rejected):
                reload_renderer_capability_v2(
                    persisted_a.path,
                    persistence_receipt=persisted_a,
                    **self.authority_b(),
                )
            self.assertEqual((persisted_a.path.read_bytes(), persisted_b.path.read_bytes()),
                             (bytes_a, bytes_b))

            # A2, B2: the failed cross-call did not mutate either prior valid sequence.
            a2 = reload_renderer_capability_v2(
                persisted_a.path, persistence_receipt=persisted_a, **self.authority()
            )
            b2 = reload_renderer_capability_v2(
                persisted_b.path, persistence_receipt=persisted_b, **self.authority_b()
            )
            self.assertEqual(
                serialize_renderer_capability_v2_bundle(a1, **self.authority()),
                serialize_renderer_capability_v2_bundle(a2, **self.authority()),
            )
            self.assertEqual(
                serialize_renderer_capability_v2_bundle(b1, **self.authority_b()),
                serialize_renderer_capability_v2_bundle(b2, **self.authority_b()),
            )
            self.assertNotEqual(bytes_a, bytes_b)
            for value in (persisted_a, persisted_b, a1, b1, a2, b2):
                self.assert_not_live_authority(value)

            with self.assertRaises(CapabilityV2Rejected):
                persist_renderer_capability_v2(
                    produced_a, directory=directory_a, **self.authority()
                )
            with self.assertRaises(CapabilityV2Rejected):
                reload_renderer_capability_v2(
                    persisted_a.path,
                    persistence_receipt=persisted_a,
                    **self.authority(
                        issuer_inputs=replace(
                            self.issuer, storage_identity="storage:foreign"
                        )
                    ),
                )
            with self.assertRaises(CapabilityV2Rejected):
                reload_renderer_capability_v2(
                    persisted_b.path,
                    persistence_receipt=persisted_a,
                    **self.authority_b(),
                )
            self.assertEqual((persisted_a.path.read_bytes(), persisted_b.path.read_bytes()),
                             (bytes_a, bytes_b))

            attack_builders = {
                "altered": lambda data: data[:-2] + bytes([data[-2] ^ 1]) + data[-1:],
                "truncated": lambda data: data[:-1],
                "reordered": lambda data: json.dumps(
                    dict(reversed(tuple(json.loads(data).items()))),
                    separators=(",", ":"),
                ).encode("utf-8"),
                "foreign": lambda data: canonical_json({
                    **json.loads(data), "profile_identity": "bcrp:foreign"
                }),
                "mixed-version": lambda data: self._mixed_version_bundle(data),
            }
            for label, builder in attack_builders.items():
                directory = root / label
                directory.mkdir()
                receipt = persist_renderer_capability_v2(
                    produced_a, directory=directory, **self.authority()
                )
                attacked = builder(receipt.path.read_bytes())
                receipt.path.write_bytes(attacked)
                forged_receipt = replace(
                    receipt,
                    sha256=hashlib.sha256(attacked).hexdigest(),
                    length=len(attacked),
                )
                with self.assertRaises(CapabilityV2Rejected, msg=label):
                    reload_renderer_capability_v2(
                        receipt.path,
                        persistence_receipt=forged_receipt,
                        **self.authority(),
                    )
                self.assertEqual(receipt.path.read_bytes(), attacked, label)
                self.assertEqual(persisted_b.path.read_bytes(), bytes_b, label)

            with self.subTest(symlinked_final_filename=True):
                symlink_directory = root / "symlink-final"
                symlink_directory.mkdir()
                symlink_receipt = persist_renderer_capability_v2(
                    produced_a, directory=symlink_directory, **self.authority()
                )
                symlink_control_before = reload_renderer_capability_v2(
                    symlink_receipt.path,
                    persistence_receipt=symlink_receipt,
                    **self.authority(),
                )
                source = root / "symlink-final-source.json"
                symlink_receipt.path.replace(source)
                source_bytes = source.read_bytes()
                source_identity = source.stat(follow_symlinks=False)
                symlink_receipt.path.symlink_to(source)
                rejection = None
                raw_filesystem_error = None
                try:
                    reload_renderer_capability_v2(
                        symlink_receipt.path,
                        persistence_receipt=symlink_receipt,
                        **self.authority(),
                    )
                except CapabilityV2Rejected as exc:
                    rejection = exc
                except OSError as exc:
                    raw_filesystem_error = exc
                self.assertTrue(symlink_receipt.path.is_symlink())
                self.assertEqual(source.read_bytes(), source_bytes)
                current_source_identity = source.stat(follow_symlinks=False)
                self.assertEqual(
                    (current_source_identity.st_dev, current_source_identity.st_ino),
                    (source_identity.st_dev, source_identity.st_ino),
                )
                no_follow_error = (
                    rejection.__cause__ if rejection is not None
                    else raw_filesystem_error
                )
                self.assertIsInstance(no_follow_error, OSError)
                self.assertEqual(no_follow_error.errno, errno.ELOOP)
                symlink_receipt.path.unlink()
                source.replace(symlink_receipt.path)
                symlink_control_after = reload_renderer_capability_v2(
                    symlink_receipt.path,
                    persistence_receipt=symlink_receipt,
                    **self.authority(),
                )
                self.assertEqual(symlink_receipt.path.read_bytes(), source_bytes)
                self.assertEqual(persisted_a.path.read_bytes(), bytes_a)
                self.assertEqual(persisted_b.path.read_bytes(), bytes_b)
                self.assertEqual(
                    serialize_renderer_capability_v2_bundle(
                        symlink_control_before, **self.authority()
                    ),
                    serialize_renderer_capability_v2_bundle(
                        symlink_control_after, **self.authority()
                    ),
                )
                self.assertEqual(
                    serialize_renderer_capability_v2_bundle(a1, **self.authority()),
                    serialize_renderer_capability_v2_bundle(
                        symlink_control_after, **self.authority()
                    ),
                )
                self.assertIsNone(
                    raw_filesystem_error,
                    "final-component symlink leaked a raw filesystem exception",
                )
                self.assertIsNotNone(rejection)

            residue = root / "residue"
            residue.mkdir()
            (residue / "foreign").write_bytes(b"x")
            with self.assertRaises(CapabilityV2Rejected):
                persist_renderer_capability_v2(
                    produced_a, directory=residue, **self.authority()
                )
            self.assertEqual((residue / "foreign").read_bytes(), b"x")

    def _mixed_version_bundle(self, data: bytes) -> bytes:
        document = json.loads(data)
        document["records"][0]["extensions"][0]["version"] = "1.0.0"
        return canonical_json(document)

    def test_persistence_rejects_symlink_directory(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            actual = root / "actual"
            actual.mkdir()
            link = root / "link"
            link.symlink_to(actual, target_is_directory=True)
            with self.assertRaises(CapabilityV2Rejected):
                persist_renderer_capability_v2(
                    self.produced(), directory=link, **self.authority()
                )
            self.assertEqual(tuple(actual.iterdir()), ())


if __name__ == "__main__":
    unittest.main()
