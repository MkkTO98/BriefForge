from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest

from briefforge.task076_contracts import (
    ContractAuthenticationError,
    load_generation8_candidate,
    load_task076_contracts,
)
from briefforge.bcrp.registry import (
    CoreRegistryError, core_registry, execute_core_registry, resolve_core_locator,
)
from briefforge.bcrp_paired_semantic_interpretation_v2 import interpret_paired_candidate
from briefforge.bcrp_paired_derivation_evidence_v2 import (
    DerivationEvidenceError,
    construct_envelope,
    persist_envelope,
    reload_envelope,
    serialize_envelope,
    verify_envelope,
)


class Task077ContractLoaderTests(unittest.TestCase):
    def test_authenticated_manifest_is_exact_and_non_authority_documents_are_not_exposed(self):
        contracts = load_task076_contracts()
        self.assertEqual(len(contracts.bytes_by_path), 23)
        self.assertEqual(len(core_registry()["entries"]), 37)
        with self.assertRaises(ContractAuthenticationError):
            contracts.document("task071-derived-populations.json")
        with self.assertRaises(ContractAuthenticationError):
            contracts.document("invalid-fixtures.json")

    def test_candidate_equal_length_byte_substitution_rejects(self):
        candidate = load_generation8_candidate()
        altered = bytearray(candidate.profile_bytes)
        altered[-2] = altered[-2] ^ 1
        forged = replace(candidate, profile_bytes=bytes(altered))
        with self.assertRaises(CoreRegistryError):
            execute_core_registry(forged)

    def test_unknown_or_kind_mismatched_locator_rejects(self):
        with self.assertRaises(CoreRegistryError):
            resolve_core_locator("/records/999", expected_kind="CandidatePresentationPackageRecord")
        candidate = next(
            item for item in execute_core_registry()[0]
            if item.dqi[2] == "CandidatePresentationPackageRecord"
        )
        with self.assertRaises(CoreRegistryError):
            resolve_core_locator(candidate.pointer, expected_kind="ValidationJudgmentRecord")

    def test_regular_file_reader_rejects_symlink_substitution(self):
        import briefforge.task076_contracts as contracts_module
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            target = directory / "target.json"
            target.write_bytes(b"{}")
            link = directory / "link.json"
            link.symlink_to(target)
            with self.assertRaises(ContractAuthenticationError):
                contracts_module._read_regular(link, "test governed entry")

    def test_production_fragments_are_deeply_immutable(self):
        node = next(
            item for item in execute_core_registry()[0]
            if item.dqi[2] == "CandidatePresentationPackageRecord"
        )
        with self.assertRaises(TypeError):
            node.fragment["semantic"]["brief_ref"] = "brief:foreign"
        interpreted = interpret_paired_candidate()
        paired = next(item for item in interpreted.inventory if item.dqi[2] == "Section")
        with self.assertRaises(TypeError):
            paired.fragment["children"][0]["target_ref"] = "statement:foreign"


class Task077GraphAndEnvelopeTests(unittest.TestCase):
    def test_generation8_core_graph_is_owned_by_authenticated_registry(self):
        from briefforge.bcrp.registry import reconstruct_core_graph
        graph = reconstruct_core_graph(load_generation8_candidate())
        self.assertEqual((len(graph.nodes), len(graph.edges)), (165, 722))

    def test_production_interpretation_matches_independent_frozen_digests(self):
        frozen = json.loads(Path(
            "artifacts/contracts/task076/task071-derivation-evidence-envelope.json"
        ).read_text(encoding="utf-8"))
        interpreted = interpret_paired_candidate()
        actual = {
            "core_graph_digest": interpreted.core_graph.digest,
            "paired_graph_digest": interpreted.paired_graph.digest,
            "counterpart_proof_digest": interpreted.counterpart_proof_digest,
            "effective_graph_digest": interpreted.effective_graph.digest,
            "requirement_inventory_digest": interpreted.requirement_inventory_digest,
            "mapping_inventory_digest": interpreted.mapping_inventory_digest,
        }
        self.assertEqual(actual, {key: frozen[key] for key in actual})
        self.assertEqual((len(interpreted.inventory), len(interpreted.paired_graph.edges)), (144, 590))
        self.assertEqual(len(interpreted.counterparts), 144)
        self.assertFalse(any(proof.traversable for proof in interpreted.counterparts))
        self.assertEqual((len(interpreted.requirement_inventory), len(interpreted.mapping_inventory)), (6, 7))
        counterpart_dqis = {
            proof.paired_dqi for proof in interpreted.counterparts
        } | {proof.core_dqi for proof in interpreted.counterparts}
        graph_dqis = {edge[0] for edge in interpreted.effective_graph.edges} | {
            edge[3] for edge in interpreted.effective_graph.edges
        }
        # Proof records themselves never become graph identities; only their source/target objects do.
        self.assertTrue(counterpart_dqis <= graph_dqis)
        self.assertFalse(any(proof.traversable for proof in interpreted.counterparts))

    def _envelope(self):
        frozen = json.loads(Path(
            "artifacts/contracts/task076/task071-derivation-evidence-envelope.json"
        ).read_text(encoding="utf-8"))
        return construct_envelope(
            evidence_identity=frozen["evidence_identity"],
            operation_identity=frozen["operation_identity"],
            authorization_fingerprint=frozen["authorization_fingerprint"],
            issued_at_utc=frozen["issued_at_utc"],
            source_locator_identity=frozen["source_locator_identity"],
        )

    def test_envelope_reconstructs_every_frozen_field_except_production_implementation_binding(self):
        frozen = json.loads(Path(
            "artifacts/contracts/task076/task071-derivation-evidence-envelope.json"
        ).read_text(encoding="utf-8"))
        produced = self._envelope().to_document()
        differing = {key for key in frozen if frozen[key] != produced[key]}
        self.assertEqual(differing, {"implementation_digest", "fingerprint"})
        self.assertNotEqual(produced["implementation_digest"], frozen["implementation_digest"])
        self.assertEqual(verify_envelope(serialize_envelope(self._envelope())).to_document(), produced)

    def test_correlated_self_reclosure_rejects_against_independent_authority(self):
        document = self._envelope().to_document()
        document["core_graph_digest"] = "0" * 64
        from briefforge.task076_contracts import domain_digest
        document["fingerprint"] = domain_digest(
            "briefforge.task076.derivation-evidence.v2",
            {key: value for key, value in document.items() if key != "fingerprint"},
        )
        with self.assertRaises(DerivationEvidenceError):
            verify_envelope(document)

    def test_persistence_requires_empty_inventory_and_reloads_exact_bytes(self):
        envelope = self._envelope()
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name).resolve()
            persisted = persist_envelope(envelope, directory=directory)
            reloaded = reload_envelope(
                persisted.path,
                expected_sha256=persisted.sha256,
                expected_fingerprint=persisted.fingerprint,
                expected_candidate_profile_byte_digest=load_generation8_candidate().profile_byte_digest,
                expected_operation_identity=envelope["operation_identity"],
                expected_authorization_fingerprint=envelope["authorization_fingerprint"],
            )
            self.assertEqual(serialize_envelope(reloaded), persisted.path.read_bytes())

    def test_persistence_rejects_preexisting_directory_inventory(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name).resolve()
            (directory / "foreign.json").write_bytes(b"{}")
            with self.assertRaises(DerivationEvidenceError):
                persist_envelope(self._envelope(), directory=directory)

    def test_reload_rejects_cross_run_binding(self):
        envelope = self._envelope()
        with tempfile.TemporaryDirectory() as name:
            persisted = persist_envelope(envelope, directory=Path(name).resolve())
            with self.assertRaises(DerivationEvidenceError):
                reload_envelope(
                    persisted.path,
                    expected_candidate_profile_byte_digest="0" * 64,
                )


if __name__ == "__main__":
    unittest.main()
