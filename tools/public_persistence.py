from __future__ import annotations

import fnmatch
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any

_ALLOWED_STATES = {"COMPLETED", "ACCEPTED", "CLOSED"}


class PersistenceError(RuntimeError):
    pass


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        check=check,
    )


def _paths_from_z(data: bytes) -> list[str]:
    return sorted(item.decode("utf-8", "surrogateescape") for item in data.split(b"\0") if item)


def _dirty_paths(root: Path) -> list[str]:
    records = _git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout.split(b"\0")
    paths: list[str] = []
    index = 0
    while index < len(records):
        record = records[index]
        if not record:
            index += 1
            continue
        status = record[:2]
        paths.append(record[3:].decode("utf-8", "surrogateescape"))
        if b"R" in status or b"C" in status:
            index += 1
            if index < len(records) and records[index]:
                paths.append(records[index].decode("utf-8", "surrogateescape"))
        index += 1
    return sorted(set(paths))


def _matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def load_policy(root: Path) -> dict[str, Any]:
    path = root / "publication/public-source-policy.json"
    policy = json.loads(path.read_text(encoding="utf-8"))
    if policy.get("schema") != "briefforge.public-source-policy.v1":
        raise PersistenceError("unsupported public-source policy")
    return policy


def classify_path(path: str, policy: dict[str, Any]) -> str:
    if path.startswith("/") or ".." in Path(path).parts:
        return "PUBLICATION_BLOCKED"
    if _matches(path, policy.get("blocked_globs", [])):
        return "PUBLICATION_BLOCKED"
    if _matches(path, policy.get("local_only_globs", [])):
        return "LOCAL_ONLY"
    return "PUBLIC_CANDIDATE"


def _sensitive_findings(root: Path, paths: list[str], policy: dict[str, Any]) -> list[dict[str, str]]:
    patterns = [(row["name"], re.compile(row["pattern"])) for row in policy.get("sensitive_patterns", [])]
    findings: list[dict[str, str]] = []
    for relative in paths:
        path = root / relative
        if not path.exists() or not path.is_file():
            continue
        if path.is_symlink():
            try:
                path.resolve().relative_to(root.resolve())
            except ValueError:
                findings.append({"path": relative, "kind": "escaping_symlink"})
                continue
        data = path.read_bytes()
        if b"\0" in data:
            continue
        text = data.decode("utf-8", "replace")
        for name, pattern in patterns:
            if pattern.search(text):
                findings.append({"path": relative, "kind": name})
    return findings


def _blocked(reason: str, **extra: Any) -> dict[str, Any]:
    return {"outcome": "PUBLICATION_BLOCKED", "reason": reason, **extra}


def _parity(root: Path) -> dict[str, int]:
    counts = _git(root, "rev-list", "--left-right", "--count", "HEAD...origin/main").stdout.decode().strip().split()
    return {"ahead": int(counts[0]), "behind": int(counts[1])}


def persist_closeout(root: Path | str, signal_path: Path | str, *, push: bool = True) -> dict[str, Any]:
    root = Path(root).resolve()
    signal = json.loads(Path(signal_path).read_text(encoding="utf-8"))
    if signal.get("schema") != "briefforge.public-closeout.v1":
        return _blocked("invalid closeout schema")
    state = signal.get("terminal_state")
    if state not in _ALLOWED_STATES or (state == "CLOSED" and not signal.get("fully_reconciled", False)):
        return _blocked(f"invalid terminal state: {state}")
    if signal.get("validation", {}).get("status") != "PASS":
        return _blocked("closeout validation did not pass")
    if signal.get("kind") == "milestone" and signal.get("persistence_eligible") is not True:
        return _blocked("milestone is not explicitly persistence eligible")
    if signal.get("kind") not in {"task", "milestone"}:
        return _blocked("invalid closeout kind")

    owned = sorted(set(signal.get("task_owned_paths", [])))
    if not owned or any(not isinstance(path, str) or not path for path in owned):
        return _blocked("task-owned paths are absent or invalid")
    try:
        policy = load_policy(root)
    except (OSError, ValueError, PersistenceError) as exc:
        return _blocked(f"publication policy unavailable: {exc}")

    classifications = {path: classify_path(path, policy) for path in owned}
    unresolved = sorted(path for path, value in classifications.items() if value == "PUBLICATION_BLOCKED")
    if unresolved:
        return _blocked("task-owned path has unresolved publication status", unresolved_paths=unresolved)
    public = sorted(path for path, value in classifications.items() if value == "PUBLIC_CANDIDATE")
    local_only = sorted(path for path, value in classifications.items() if value == "LOCAL_ONLY")

    git_dir_result = _git(root, "rev-parse", "--git-dir", check=False)
    if git_dir_result.returncode:
        return _blocked("BriefForge is not a Git repository")
    git_dir = Path(git_dir_result.stdout.decode().strip())
    if not git_dir.is_absolute():
        git_dir = root / git_dir
    lock = git_dir / "public-persistence.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return _blocked("overlapping BriefForge persistence writer")

    try:
        os.write(descriptor, f"pid={os.getpid()}\n".encode())
        os.close(descriptor)
        receipt_dir = git_dir / "public-persistence-receipts"
        receipt_path = receipt_dir / (signal["closure_id"] + ".json")
        if receipt_path.exists():
            result = json.loads(receipt_path.read_text(encoding="utf-8"))
            result["idempotent_replay"] = True
            return result

        if _git(root, "diff", "--name-only", "--diff-filter=U", "-z").stdout:
            return _blocked("unresolved merge conflicts")
        dirty = _dirty_paths(root)
        unexpected = sorted(set(dirty) - set(owned))
        if unexpected:
            return _blocked("dirty tree contains unrelated changes", unexpected_dirty_paths=unexpected)

        fetch = _git(root, "fetch", "--quiet", "origin", "main", check=False)
        if fetch.returncode:
            return _blocked("could not authenticate origin/main before persistence", git_error=fetch.stderr.decode("utf-8", "replace").strip())
        parity_before = _parity(root)
        if parity_before != {"ahead": 0, "behind": 0}:
            return _blocked("remote divergence detected", parity=parity_before)

        changed_public = sorted(set(dirty) & set(public))
        findings = _sensitive_findings(root, changed_public, policy)
        if findings:
            return _blocked("sensitive material detected in public candidate", sensitive_findings=findings)

        if not changed_public:
            result = {
                "outcome": "LOCAL_ONLY_COMPLETION" if local_only else "REMOTE_SAVED",
                "commit": _git(root, "rev-parse", "HEAD").stdout.decode().strip(),
                "committed_paths": [],
                "local_only_paths": local_only,
                "no_commit_needed": True,
                "parity": parity_before,
                "idempotent_replay": False,
            }
            receipt_dir.mkdir(exist_ok=True)
            receipt_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            return result

        stage = _git(root, "add", "--", *changed_public, check=False)
        if stage.returncode:
            return _blocked("exact-path staging failed", git_error=stage.stderr.decode("utf-8", "replace").strip())
        staged = _paths_from_z(_git(root, "diff", "--cached", "--name-only", "-z").stdout)
        if staged != changed_public:
            return _blocked("staged paths differ from validated exact paths", staged_paths=staged, expected_paths=changed_public)
        message = signal.get("commit_message", "")
        if signal.get("identifier") not in message:
            return _blocked("commit message does not identify task or milestone")
        commit_result = _git(root, "commit", "--quiet", "-m", message, check=False)
        if commit_result.returncode:
            return _blocked("commit failed; staged work preserved", git_error=commit_result.stderr.decode("utf-8", "replace").strip())
        commit = _git(root, "rev-parse", "HEAD").stdout.decode().strip()

        if push:
            pushed = _git(root, "push", "--quiet", "origin", "HEAD:main", check=False)
            if pushed.returncode:
                return {
                    "outcome": "REMOTE_SAVE_PENDING",
                    "reason": "local commit succeeded but push failed",
                    "commit": commit,
                    "committed_paths": changed_public,
                    "local_only_paths": local_only,
                    "recovery_action": "git push origin main",
                    "git_error": pushed.stderr.decode("utf-8", "replace").strip(),
                    "idempotent_replay": False,
                }
        _git(root, "fetch", "--quiet", "origin", "main")
        parity_after = _parity(root)
        if parity_after != {"ahead": 0, "behind": 0}:
            return _blocked("remote parity verification failed after push", commit=commit, parity=parity_after)
        result = {
            "outcome": "REMOTE_SAVED_WITH_LOCAL_ONLY_MATERIAL" if local_only else "REMOTE_SAVED",
            "commit": commit,
            "committed_paths": changed_public,
            "local_only_paths": local_only,
            "no_commit_needed": False,
            "parity": parity_after,
            "idempotent_replay": False,
        }
        receipt_dir.mkdir(exist_ok=True)
        receipt_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return result
    finally:
        try:
            lock.unlink()
        except FileNotFoundError:
            pass


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Persist an exact-path governed BriefForge closeout")
    parser.add_argument("signal", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--no-push", action="store_true")
    arguments = parser.parse_args()
    result = persist_closeout(arguments.root, arguments.signal, push=not arguments.no_push)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["outcome"] in {"REMOTE_SAVED", "REMOTE_SAVED_WITH_LOCAL_ONLY_MATERIAL", "LOCAL_ONLY_COMPLETION"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
