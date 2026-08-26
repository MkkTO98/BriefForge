from __future__ import annotations

import fnmatch
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def load_policy(root: Path) -> dict:
    return json.loads((root / "publication/public-source-policy.json").read_text())


def classify_path(path: str, policy: dict) -> str:
    if any(fnmatch.fnmatchcase(path, pattern) for pattern in policy.get("blocked_globs", [])):
        return "PUBLICATION_BLOCKED"
    if any(fnmatch.fnmatchcase(path, pattern) for pattern in policy.get("local_only_globs", [])):
        return "LOCAL_ONLY"
    return "PUBLIC_CANDIDATE"


class PublicSourcePolicyTests(unittest.TestCase):
    def test_seven_reviewed_files_have_explicit_semantic_classification(self) -> None:
        policy = load_policy(ROOT)
        expected = {
            "artifacts/tasks/TASK-078-four-company-financial-browser-report.md": "PUBLIC_SAFE_ORIGINAL",
            "context/latest_handoff.md": "PUBLIC_SAFE_ORIGINAL",
            "src/briefforge/task078_four_company_report.py": "LOCAL_ONLY_RESTRICTED",
            "src/briefforge/task081_four_company_corporate_financial_report_v4.py": "PUBLIC_SAFE_ORIGINAL",
            "src/briefforge/task082_four_company_standardized_corporate_report_v5.py": "PUBLIC_SAFE_ORIGINAL",
            "tests/test_task078_four_company_browser_report.py": "LOCAL_ONLY_RESTRICTED",
            "tests/test_task081_four_company_corporate_financial_report_v4.py": "PUBLIC_SAFE_AFTER_SEPARATION",
        }
        actual = {row["path"]: row["classification"] for row in policy["reviewed_files"]}
        self.assertEqual(expected, actual)

    def test_restricted_and_runtime_directories_are_local_only(self) -> None:
        policy = load_policy(ROOT)
        for path in (
            "artifacts/inputs/TASK-078/source.json",
            "artifacts/external-release-handoffs/TASK-081/payload.json",
            "artifacts/presentations/TASK-081/index.html",
            "artifacts/publications/TASK-078/index.html",
            "artifacts/replays/TASK-078/replay.json",
            "artifacts/verification/TASK-078/screenshot.png",
            "hardware/profile.yaml",
        ):
            self.assertEqual("LOCAL_ONLY", classify_path(path, policy), path)

    def test_public_candidate_code_is_not_misclassified_from_rights_language(self) -> None:
        policy = load_policy(ROOT)
        for path in (
            "src/briefforge/task081_four_company_corporate_financial_report_v4.py",
            "src/briefforge/task082_four_company_standardized_corporate_report_v5.py",
            "context/latest_handoff.md",
        ):
            self.assertEqual("PUBLIC_CANDIDATE", classify_path(path, policy), path)

    def test_initial_candidate_manifest_binds_exact_baseline_tree(self) -> None:
        manifest_path = ROOT / "publication/initial-candidate-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual("briefforge.initial-public-candidate.v1", manifest["schema"])
        entries = manifest["files"]
        git_probe = subprocess.run(
            ["git", "-C", str(ROOT), "rev-list", "--max-parents=0", "HEAD"],
            text=True,
            capture_output=True,
        )
        if git_probe.returncode == 0:
            baseline = git_probe.stdout.strip()
            tree = subprocess.check_output(
                ["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", baseline],
                text=True,
            ).splitlines()
            self.assertEqual(sorted(tree), sorted([*entries, "publication/initial-candidate-manifest.json"]))
            for path, row in entries.items():
                data = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{baseline}:{path}"])
                self.assertEqual(row["sha256"], hashlib.sha256(data).hexdigest(), path)
                self.assertEqual(row["bytes"], len(data), path)
        else:
            for path, row in entries.items():
                data = (ROOT / path).read_bytes()
                self.assertEqual(row["sha256"], hashlib.sha256(data).hexdigest(), path)
                self.assertEqual(row["bytes"], len(data), path)
        digest_payload = "".join(f"{path}\0{row['sha256']}\n" for path, row in sorted(entries.items())).encode()
        self.assertEqual(manifest["candidate_digest"], hashlib.sha256(digest_payload).hexdigest())
        self.assertEqual(len(entries) + 1, manifest["candidate_count_including_manifest"])

    def test_separated_public_test_has_no_machine_specific_fixture_path(self) -> None:
        text = (ROOT / "tests/test_task081_four_company_corporate_financial_report_v4.py").read_text()
        self.assertNotIn("/home/mkkto", text)
        self.assertIn("BRIEFFORGE_LOCAL_T042_SOURCE", text)


if __name__ == "__main__":
    unittest.main()
