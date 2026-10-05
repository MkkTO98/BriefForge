"""Focused zero-authoring tests for the TASK-069 attempt boundary and drafts."""
from __future__ import annotations

import ast
from dataclasses import replace
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/author_task069_candidate.py"
_SPEC = importlib.util.spec_from_file_location("task069_candidate_authoring", SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
PROGRAM = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(PROGRAM)


class Task069CandidateAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (cls.ledger, cls.table, cls.blueprint, cls.gate,
         cls.admission) = PROGRAM.load_contracts()
        cls.prepared = PROGRAM.preflight(
            cls.ledger, cls.table, cls.blueprint, cls.gate, cls.admission)

    def _rejected(self, semantics) -> None:
        try:
            report = PROGRAM.semantic_traceability_report(
                semantics, self.ledger, self.table, self.blueprint)
        except ValueError:
            return
        self.assertFalse(report["passed"])

    def test_source_admission_and_exact_authoritative_oracle(self) -> None:
        source = self.prepared["source_authentication"]
        self.assertEqual((13, 130), (source["artifact_count"], source["locator_count"]))
        self.assertTrue(source["locators_resolved"])
        report = self.prepared["traceability"]
        self.assertTrue(report["passed"])
        self.assertTrue(report["exact_authoritative_semantics"])
        self.assertEqual(109, len(report["ledger_treatments"]))

    def test_non_string_meanings_are_labeled_exact_fragments(self) -> None:
        semantics = self.prepared["semantics"]
        statements = {item.identity: item.text for item in semantics.statements}
        for item in self.ledger["items"]:
            value = item["source_authored_meaning"]
            if type(value) is str or item["intended_candidate_destination"].startswith("value:"):
                continue
            destination = item["intended_candidate_destination"]
            if not destination.startswith("statement:"):
                continue
            fragment = PROGRAM._meaning(item)
            self.assertIn(f"[{item['item_id']}]", fragment)
            self.assertIn(fragment, statements[destination])
            self.assertNotIn(fragment, ("true", "false"))
            if type(value) is list:
                self.assertEqual([f"- {part}" for part in value], fragment.splitlines()[1:])
            else:
                self.assertTrue(fragment.endswith(json.dumps(
                    value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))))

    def test_raw_transformation_identity_is_source_supported(self) -> None:
        values = {item.identity: item for item in self.prepared["semantics"].values}
        for row in self.table["rows"]:
            for key in ("raw", "first_difference"):
                contract = row[key]
                expected = contract.get("transformation_ref", contract["transformation_state"])
                self.assertEqual(expected, values[contract["value_id"]].transformation_identity)
        self.assertNotIn("identity_v1@1.0", {item.transformation_identity for item in values.values()})

    def test_exact_operational_profile_and_candidate_stage_inventory(self) -> None:
        authorities = self.prepared["drafts"][1].semantic["authorities"]
        self.assertEqual(10, len(authorities))
        self.assertEqual(sorted(item["id"] for item in authorities[8:]),
                         [item["id"] for item in authorities[8:]])
        self.assertTrue(self.prepared["stage"]["passed"])
        self.assertEqual(3, self.prepared["stage"]["record_count"])
        self.assertEqual(1, self.prepared["stage"]["extension_count"])
        self.assertFalse(self.prepared["stage"]["lifecycle_extension_names"])
        self.assertFalse(self.prepared["stage"]["forbidden_state_or_invocation_keys"])
        scope = json.loads(authorities[6]["scope"])
        self.assertEqual(("127.0.0.1", 47609, "http://127.0.0.1:47609"),
                         (scope["transport"]["address"], scope["transport"]["port"],
                          scope["transport"]["origin"]))
        self.assertEqual("/task069-paired-terminal.html", scope["routes"][0]["path"])

    def test_local_public_dto_reconstruction_and_no_preflight_bundle(self) -> None:
        candidate = self.prepared["drafts"][2]
        self.assertEqual(self.prepared["semantics"], PROGRAM.reconstruct_exact_extension(candidate))
        self.assertNotIn("preflight_bundle", self.prepared)
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("_reconstruct_semantics", source)
        self.assertNotIn("BCRPRecord", source)
        self.assertNotIn("bundle_from_drafts", source)

    def test_adversarial_order_and_row_classification_or_evidence_mutations(self) -> None:
        semantics = self.prepared["semantics"]
        self._rejected(replace(semantics, statements=(semantics.statements[1], semantics.statements[0],
                                                       *semantics.statements[2:])))
        rows = list(semantics.table.rows)
        rows[0] = replace(rows[0], classification_ref="classification:mutated")
        self._rejected(replace(semantics, table=replace(semantics.table, rows=tuple(rows))))
        rows = list(semantics.table.rows)
        rows[0] = replace(rows[0], evidence_role_ref="evidence-role:mutated")
        self._rejected(replace(semantics, table=replace(semantics.table, rows=tuple(rows))))

    def test_adversarial_value_obligation_and_provenance_mutations(self) -> None:
        semantics = self.prepared["semantics"]
        values = list(semantics.values)
        values[0] = replace(values[0], method_ref="mutated-method@1.0")
        self._rejected(replace(semantics, values=tuple(values)))
        obligations = list(semantics.obligations)
        obligations[0] = replace(obligations[0], kind="mutated-kind")
        self._rejected(replace(semantics, obligations=tuple(obligations)))
        provenance = list(semantics.provenance)
        provenance[0] = replace(provenance[0], citation="mutated citation")
        self._rejected(replace(semantics, provenance=tuple(provenance)))


    def test_durable_marker_precedes_exactly_one_fake_call_and_survives_failure(self) -> None:
        original_marker = PROGRAM.MARKER
        original_marker_existed = original_marker.exists()
        original_author = PROGRAM._task069_author_once
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / ".single-use"
            calls = []
            def fake_author(**kwargs):
                self.assertTrue(marker.exists())
                calls.append(kwargs)
                raise RuntimeError("simulated author failure")
            PROGRAM.MARKER = marker
            PROGRAM._task069_author_once = fake_author
            try:
                with self.assertRaisesRegex(RuntimeError, "simulated"):
                    PROGRAM._consume_attempt_and_author(
                        *self.prepared["drafts"], PROGRAM._marker_payload())
                self.assertTrue(marker.exists())
                self.assertEqual(1, len(calls))
                with self.assertRaises(FileExistsError):
                    PROGRAM._consume_attempt_and_author(
                        *self.prepared["drafts"], PROGRAM._marker_payload())
                self.assertEqual(1, len(calls))
            finally:
                PROGRAM.MARKER = original_marker
                PROGRAM._task069_author_once = original_author
        self.assertEqual(original_marker_existed, original_marker.exists())






class Task069PortableSoftwareTests(unittest.TestCase):
    def test_ast_has_one_author_call_no_private_or_publication_machinery(self) -> None:
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name)
                 and node.func.id == "_task069_author_once"]
        self.assertEqual(1, len(calls))
        imports = " ".join((node.module or "") for node in ast.walk(tree)
                           if isinstance(node, ast.ImportFrom))
        for prohibited in ("publication_release", ".projection", "renderer_adapter",
                           "manifest_admission", "publication_lifecycle"):
            self.assertNotIn(prohibited, imports)
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == "_consume_attempt_and_author")
        self.assertEqual(2, sum(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                                and node.func.attr == "fsync" for node in ast.walk(function)))

    def test_staging_directory_rename_is_whole_and_failure_leaves_no_final(self) -> None:
        originals = (PROGRAM.CANDIDATE_DIR, PROGRAM.STAGING_DIR)
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            PROGRAM.CANDIDATE_DIR = parent / "candidate"
            PROGRAM.STAGING_DIR = parent / ".candidate-staging"
            try:
                PROGRAM.STAGING_DIR.mkdir()
                PROGRAM.persist_candidate_directory(b"profile", b"semantic", b"fingerprint")
                self.assertFalse(PROGRAM.STAGING_DIR.exists())
                self.assertEqual(3, len(tuple(PROGRAM.CANDIDATE_DIR.iterdir())))
                PROGRAM.CANDIDATE_DIR = parent / "candidate-failure"
                PROGRAM.STAGING_DIR = parent / ".candidate-staging-failure"
                PROGRAM.STAGING_DIR.mkdir()
                with patch.object(PROGRAM.os, "write", side_effect=OSError("write failure")):
                    with self.assertRaisesRegex(OSError, "write failure"):
                        PROGRAM.persist_candidate_directory(b"p", b"s", b"f")
                self.assertFalse(PROGRAM.CANDIDATE_DIR.exists())
            finally:
                PROGRAM.CANDIDATE_DIR, PROGRAM.STAGING_DIR = originals



class Task069LocalRecordedStateTests(unittest.TestCase):
    def test_governed_attempt_state_is_internally_consistent(self) -> None:
        if not PROGRAM.MARKER.exists():
            self.assertFalse(PROGRAM.CANDIDATE_DIR.exists())
            self.assertFalse(PROGRAM.STAGING_DIR.exists())
            self.assertFalse(PROGRAM.REPORT.exists())
            self.assertTrue(all(not path.exists() for path in PROGRAM._OUTPUTS))
            return
        report = json.loads(PROGRAM.REPORT.read_text(encoding="utf-8"))
        self.assertTrue(report["attempt_consumed"])
        self.assertEqual(1, report["authoring_call_count"])
        self.assertEqual("candidate:task065-cross-inquiry", report["candidate_identity"])
        if report["candidate_persisted"]:
            self.assertTrue(PROGRAM.CANDIDATE_DIR.is_dir())
            self.assertFalse(PROGRAM.STAGING_DIR.exists())
        else:
            self.assertFalse(PROGRAM.CANDIDATE_DIR.exists())
            self.assertTrue(PROGRAM.STAGING_DIR.is_dir())



if __name__ == "__main__":
    unittest.main()
