from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.public_persistence import persist_closeout  # noqa: E402


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=check)


class PublicSourcePersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        base = Path(self.temporary.name)
        self.repo = base / "repo"
        self.remote = base / "remote.git"
        self.repo.mkdir()
        run("git", "init", "-q", "-b", "main", cwd=self.repo)
        run("git", "config", "user.name", "Test User", cwd=self.repo)
        run("git", "config", "user.email", "test@example.invalid", cwd=self.repo)
        run("git", "init", "-q", "--bare", str(self.remote), cwd=base)
        run("git", "remote", "add", "origin", str(self.remote), cwd=self.repo)
        (self.repo / "publication").mkdir()
        policy = {
            "schema": "briefforge.public-source-policy.v1",
            "default": "PUBLIC_CANDIDATE",
            "local_only_globs": [
                "artifacts/inputs/**", "artifacts/presentations/**", "hardware/profile.yaml"
            ],
            "blocked_globs": ["**/.env", "**/*.pem", "**/*.key"],
            "sensitive_patterns": [
                {"name": "private_key", "pattern": "-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"},
                {"name": "credential_assignment", "pattern": "(?i)(?:api[_-]?key|access[_-]?token|password)\\s*[:=]\\s*[A-Za-z0-9_./+\\-=]{12,}"}
            ]
        }
        (self.repo / "publication/public-source-policy.json").write_text(json.dumps(policy) + "\n")
        (self.repo / "README.md").write_text("baseline\n")
        run("git", "add", "README.md", "publication/public-source-policy.json", cwd=self.repo)
        run("git", "commit", "-q", "-m", "baseline", cwd=self.repo)
        run("git", "push", "-q", "-u", "origin", "main", cwd=self.repo)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def signal(self, closure_id: str, paths: list[str], state: str = "COMPLETED", identifier: str = "TASK-TEST") -> Path:
        path = Path(self.temporary.name) / f"{closure_id}.json"
        path.write_text(json.dumps({
            "schema": "briefforge.public-closeout.v1",
            "closure_id": closure_id,
            "kind": "task",
            "identifier": identifier,
            "terminal_state": state,
            "validation": {"status": "PASS"},
            "task_owned_paths": paths,
            "commit_message": f"chore(closeout): persist {identifier}",
        }) + "\n")
        return path

    def test_rejects_sensitive_public_candidate(self) -> None:
        (self.repo / "secret.txt").write_text("api_" + "key=abcdefghijklmnop\n")
        result = persist_closeout(self.repo, self.signal("secret", ["secret.txt"]), push=True)
        self.assertEqual("PUBLICATION_BLOCKED", result["outcome"])
        self.assertIn("sensitive", result["reason"])
        self.assertEqual("", run("git", "diff", "--cached", "--name-only", cwd=self.repo).stdout)

    def test_rejects_unrelated_dirty_file(self) -> None:
        (self.repo / "owned.txt").write_text("owned\n")
        (self.repo / "unrelated.txt").write_text("unrelated\n")
        result = persist_closeout(self.repo, self.signal("dirty", ["owned.txt"]), push=True)
        self.assertEqual("PUBLICATION_BLOCKED", result["outcome"])
        self.assertEqual(["unrelated.txt"], result["unexpected_dirty_paths"])

    def test_rejects_invalid_terminal_state(self) -> None:
        (self.repo / "owned.txt").write_text("owned\n")
        result = persist_closeout(self.repo, self.signal("blocked", ["owned.txt"], state="BLOCKED"), push=True)
        self.assertEqual("PUBLICATION_BLOCKED", result["outcome"])
        self.assertIn("terminal state", result["reason"])

    def test_exact_path_commit_push_and_remote_parity(self) -> None:
        (self.repo / "owned.txt").write_text("owned\n")
        before = run("git", "rev-parse", "HEAD", cwd=self.repo).stdout.strip()
        result = persist_closeout(self.repo, self.signal("success", ["owned.txt"]), push=True)
        self.assertEqual("REMOTE_SAVED", result["outcome"])
        self.assertNotEqual(before, result["commit"])
        self.assertEqual(["owned.txt"], result["committed_paths"])
        self.assertEqual(result["commit"], run("git", "rev-parse", "origin/main", cwd=self.repo).stdout.strip())
        self.assertEqual({"ahead": 0, "behind": 0}, result["parity"])

    def test_local_only_task_reports_no_commit(self) -> None:
        local = self.repo / "artifacts/inputs/private.json"
        local.parent.mkdir(parents=True)
        local.write_text('{"rights":"internal_local_analysis_only"}\n')
        before = run("git", "rev-parse", "HEAD", cwd=self.repo).stdout.strip()
        result = persist_closeout(self.repo, self.signal("local", ["artifacts/inputs/private.json"]), push=True)
        self.assertEqual("LOCAL_ONLY_COMPLETION", result["outcome"])
        self.assertEqual(["artifacts/inputs/private.json"], result["local_only_paths"])
        self.assertEqual(before, run("git", "rev-parse", "HEAD", cwd=self.repo).stdout.strip())

    def test_public_and_local_only_paths_report_mixed_outcome(self) -> None:
        (self.repo / "owned.txt").write_text("owned\n")
        local = self.repo / "artifacts/presentations/report.html"
        local.parent.mkdir(parents=True)
        local.write_text("restricted runtime output\n")
        result = persist_closeout(self.repo, self.signal("mixed", ["owned.txt", "artifacts/presentations/report.html"]), push=True)
        self.assertEqual("REMOTE_SAVED_WITH_LOCAL_ONLY_MATERIAL", result["outcome"])
        self.assertEqual(["owned.txt"], result["committed_paths"])
        self.assertEqual(["artifacts/presentations/report.html"], result["local_only_paths"])

    def test_push_failure_preserves_local_commit(self) -> None:
        (self.repo / "owned.txt").write_text("owned\n")
        hook = self.remote / "hooks/pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        result = persist_closeout(self.repo, self.signal("push-fail", ["owned.txt"]), push=True)
        self.assertEqual("REMOTE_SAVE_PENDING", result["outcome"])
        self.assertEqual(result["commit"], run("git", "rev-parse", "HEAD", cwd=self.repo).stdout.strip())
        self.assertIn("git push origin main", result["recovery_action"])
        self.assertEqual("", run("git", "diff", "--cached", "--name-only", cwd=self.repo).stdout)

    def test_idempotent_rerun_creates_no_duplicate_commit(self) -> None:
        (self.repo / "owned.txt").write_text("owned\n")
        signal = self.signal("repeat", ["owned.txt"])
        first = persist_closeout(self.repo, signal, push=True)
        count = run("git", "rev-list", "--count", "HEAD", cwd=self.repo).stdout.strip()
        second = persist_closeout(self.repo, signal, push=True)
        self.assertEqual(first["commit"], second["commit"])
        self.assertEqual(True, second["idempotent_replay"])
        self.assertEqual(count, run("git", "rev-list", "--count", "HEAD", cwd=self.repo).stdout.strip())


if __name__ == "__main__":
    unittest.main()
