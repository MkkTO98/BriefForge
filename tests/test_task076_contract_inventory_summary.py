"""The TASK-076 directory admits documentation, not unauthenticated authority."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from briefforge import task076_contracts as contracts


SOURCE_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_REL = Path("artifacts/contracts/task076/final-contract-byte-manifest.json")
CONTRACT_REL = MANIFEST_REL.parent


class Task076ContractInventorySummaryTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        source_manifest = SOURCE_ROOT / MANIFEST_REL
        manifest = json.loads(source_manifest.read_bytes())
        self.members = tuple(entry["path"] for entry in manifest["entries"])
        for rel in (*self.members, MANIFEST_REL.as_posix()):
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE_ROOT / rel, target)
        self.contract_dir = self.root / CONTRACT_REL
        (self.contract_dir / "_SUMMARY.md").write_text(
            "Synthetic ancillary navigation; not governed authority.\n", encoding="utf-8")
        for attr, value in (("PROJECT_ROOT", self.root),
                            ("_CONTRACT_ROOT", self.contract_dir),
                            ("_MANIFEST_PATH", self.root / MANIFEST_REL)):
            override = patch.object(contracts, attr, value)
            override.start()
            self.addCleanup(override.stop)

    def test_regular_summary_is_admitted_without_becoming_governed_authority(self):
        loaded = contracts.load_task076_contracts()
        self.assertEqual(set(loaded.bytes_by_path), set(self.members))
        self.assertNotIn("_SUMMARY.md", loaded.documents)
        self.assertNotIn((CONTRACT_REL / "_SUMMARY.md").as_posix(), loaded.bytes_by_path)
        self.assertEqual(len(loaded.manifest["entries"]), len(self.members))
        summary = self.contract_dir / "_SUMMARY.md"
        summary.unlink()
        with self.subTest(summary="absent"):
            absent = contracts.load_task076_contracts()
            self.assertEqual(absent.bytes_by_path, loaded.bytes_by_path)
        summary.write_text("arbitrary ancillary navigation, not authority\n")
        with self.subTest(summary="present"):
            self.assertEqual(contracts.load_task076_contracts().bytes_by_path, loaded.bytes_by_path)

    def test_unexpected_markdown_is_not_a_general_documentation_exemption(self):
        (self.contract_dir / "OTHER.md").write_text("not authorized\n")
        with self.assertRaisesRegex(contracts.ContractAuthenticationError,
                                    "contract directory inventory differs"):
            contracts.load_task076_contracts()

    def test_arbitrary_unexpected_file_is_rejected(self):
        (self.contract_dir / "surprise.txt").write_text("not authorized\n")
        with self.assertRaisesRegex(contracts.ContractAuthenticationError,
                                    "contract directory inventory differs"):
            contracts.load_task076_contracts()

    def test_summary_symlink_is_rejected_even_when_target_is_regular(self):
        summary = self.contract_dir / "_SUMMARY.md"
        summary.unlink()
        summary.symlink_to("final-contract-byte-manifest.json")
        with self.assertRaisesRegex(contracts.ContractAuthenticationError,
                                    "contract directory inventory differs"):
            contracts.load_task076_contracts()
        summary.unlink()
        summary.mkdir()
        with self.subTest(summary="directory"), self.assertRaisesRegex(
                contracts.ContractAuthenticationError, "contract directory inventory differs"):
            contracts.load_task076_contracts()

    def test_altered_authenticated_member_is_rejected_with_summary_present(self):
        member = self.contract_dir / "validation-rules.json"
        member.write_bytes(member.read_bytes() + b" ")
        with self.assertRaisesRegex(contracts.ContractAuthenticationError,
                                    "governed entry authentication failed"):
            contracts.load_task076_contracts()

    def test_missing_authenticated_member_cannot_be_replaced_by_summary(self):
        (self.contract_dir / "validation-rules.json").unlink()
        with self.assertRaisesRegex(contracts.ContractAuthenticationError,
                                    "governed entry .*not an exact regular file"):
            contracts.load_task076_contracts()

    def test_authenticated_member_symlink_is_rejected_at_member_check(self):
        member = self.contract_dir / "validation-rules.json"
        duplicate = self.root / "validation-rules-copy.json"
        shutil.copyfile(member, duplicate)
        member.unlink()
        member.symlink_to(duplicate)
        with self.assertRaisesRegex(contracts.ContractAuthenticationError,
                                    "governed entry .*not an exact regular file"):
            contracts.load_task076_contracts()


if __name__ == "__main__":
    unittest.main()
