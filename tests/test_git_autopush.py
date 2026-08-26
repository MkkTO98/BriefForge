from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tools/git_autopush.py"


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=check)


class GitAutopushTests(unittest.TestCase):
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
        (self.repo / "README.md").write_text("baseline\n")
        run("git", "add", "README.md", cwd=self.repo)
        run("git", "commit", "-q", "-m", "baseline", cwd=self.repo)
        run("git", "push", "-q", "-u", "origin", "main", cwd=self.repo)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def closeout(self, *paths: str) -> subprocess.CompletedProcess[str]:
        return run(
            sys.executable,
            str(HELPER),
            "--project",
            str(self.repo),
            "--message",
            "chore: preserve milestone",
            "--commit",
            "--push",
            "--yes-push",
            "--paths",
            *paths,
            cwd=self.repo,
            check=False,
        )

    def test_commits_and_pushes_only_authorized_paths(self) -> None:
        (self.repo / "authorized.txt").write_text("authorized\n")
        (self.repo / "unrelated.txt").write_text("unrelated\n")

        result = self.closeout("authorized.txt")

        self.assertEqual(0, result.returncode, result.stderr)
        committed = run("git", "show", "--format=", "--name-only", "HEAD", cwd=self.repo).stdout.splitlines()
        self.assertEqual(["authorized.txt"], committed)
        self.assertTrue((self.repo / "unrelated.txt").exists())
        self.assertIn("?? unrelated.txt", run("git", "status", "--short", cwd=self.repo).stdout)
        self.assertEqual(
            run("git", "rev-parse", "HEAD", cwd=self.repo).stdout,
            run("git", "rev-parse", "origin/main", cwd=self.repo).stdout,
        )

    def test_push_failure_preserves_local_commit(self) -> None:
        hook = self.remote / "hooks/pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        (self.repo / "authorized.txt").write_text("authorized\n")
        remote_before = run("git", "rev-parse", "origin/main", cwd=self.repo).stdout.strip()

        result = self.closeout("authorized.txt")

        self.assertNotEqual(0, result.returncode)
        self.assertNotEqual(remote_before, run("git", "rev-parse", "HEAD", cwd=self.repo).stdout.strip())
        self.assertEqual(remote_before, run("git", "rev-parse", "origin/main", cwd=self.repo).stdout.strip())
        self.assertEqual("", run("git", "diff", "--cached", "--name-only", cwd=self.repo).stdout)

    def test_no_change_rerun_creates_no_commit(self) -> None:
        (self.repo / "authorized.txt").write_text("authorized\n")
        first = self.closeout("authorized.txt")
        self.assertEqual(0, first.returncode, first.stderr)
        head = run("git", "rev-parse", "HEAD", cwd=self.repo).stdout.strip()
        count = run("git", "rev-list", "--count", "HEAD", cwd=self.repo).stdout.strip()

        second = self.closeout("authorized.txt")

        self.assertEqual(0, second.returncode, second.stderr)
        self.assertEqual(head, run("git", "rev-parse", "HEAD", cwd=self.repo).stdout.strip())
        self.assertEqual(count, run("git", "rev-list", "--count", "HEAD", cwd=self.repo).stdout.strip())


if __name__ == "__main__":
    unittest.main()
