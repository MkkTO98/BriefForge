"""Crash-recoverable, file-backed authority boundary for Candidate authoring.

All authority, ledger, and output roots and all construction and validation
operations are fixed by the governed production boundary. The filesystem
protocol provides recoverable, individually durable commitments; it does not
claim cross-file atomicity or protection from a malicious same-user rewrite.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Any

from .bcrp.authoring import RecordDraft, author_candidate_bundle as build_candidate_bundle
from .bcrp.canonical import bundle_from_canonical_json, canonical_json_bytes, fingerprint_bundle
from .bcrp.model import BCRPBundle, ValidationFinding, ValidationResult
from .bcrp.validation import validate_bundle
from briefforge_paired_terminal_profile.profile import (
    PairedProfileRejected,
    paired_semantic_closure_fingerprint,
    validate_candidate_paired_semantics,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GOVERNED_AUTHORITY_ROOT = PROJECT_ROOT / "artifacts/governance/candidate-authoring-authority"
GOVERNED_LEDGER_ROOT = PROJECT_ROOT / "artifacts/state/candidate-authoring-ledger"
GOVERNED_OUTPUT_ROOT = PROJECT_ROOT / "artifacts/pilots/candidate-authoring-output"
PAIRED_SEMANTIC_VALIDATION_PROFILE = "briefforge:paired-terminal-semantic-closure:1.0.0"
PAIRED_CANDIDATE_VALIDATOR_IDENTITY = "briefforge:bcrp-L0-L2+paired-semantic-closure:1.0.0"

_STATES = (
    "PREPARED_NOT_CONSUMED", "INVOKED_CONSUMED",
    "AUTHORED_OUTPUT_DURABLY_STAGED", "VALIDATION_PENDING",
    "VALIDATED_ACCEPTED", "VALIDATED_NOT_ACCEPTED",
    "INDETERMINATE_CONSUMED_NO_OUTPUT",
)
_TERMINAL = {"VALIDATED_ACCEPTED", "VALIDATED_NOT_ACCEPTED", "INDETERMINATE_CONSUMED_NO_OUTPUT"}
_STAGE_FILES = {"profile.json", "candidate-semantic.json", "fingerprint.json",
                "inventory.json", "authoring-receipt.json"}
_STATE_KEYS = {"format", "sequence", "state", "authority_digest", "prior_state_digest", "detail"}


class CandidateAuthoringError(RuntimeError):
    """Authority, state, staging, or replay authentication failed closed."""


class RecoveryRequired(CandidateAuthoringError):
    """The attempt was consumed and must be handled through recovery."""


@dataclass(frozen=True)
class AuthorityBinding:
    task_id: str
    campaign_id: str
    candidate_id: str
    brief_id: str
    material_ids: tuple[str, ...]
    source_snapshot: str
    blueprint_fingerprint: str
    attempt_id: str
    cumulative_attempt_number: int
    predecessor_attempt_digests: tuple[str, ...]
    predecessor_evidence_paths: tuple[str, ...]
    authoring_input_sha256: str
    semantic_validation_profile: str
    expected_semantic_closure_sha256: str
    validator_identity: str
    authority_decision_path: str
    authority_decision_sha256: str
    ledger_root: str
    output_root: str
    scope: str = "governed"


@dataclass(frozen=True)
class AuthoringReceipt:
    attempt_id: str
    state: str
    candidate_id: str
    candidate_fingerprint: str | None
    stage_receipt_sha256: str | None
    governed: bool


@dataclass(frozen=True)
class _GovernedValidationResult:
    technical: ValidationResult
    semantic_validation_profile: str
    expected_semantic_closure_sha256: str
    observed_semantic_closure_sha256: str | None

    @property
    def blocking(self) -> bool:
        return self.technical.blocking


def _validate_governed_paired_candidate(
    bundle: BCRPBundle, expected_semantic_closure_sha256: str,
) -> _GovernedValidationResult:
    """Run fixed technical validation plus exact paired semantic-closure validation."""
    technical = validate_bundle(bundle, through_layer="L2")
    findings = list(technical.findings)
    observed = None
    try:
        semantics = validate_candidate_paired_semantics(bundle)
        observed = paired_semantic_closure_fingerprint(semantics)
        if observed != expected_semantic_closure_sha256:
            raise PairedProfileRejected("paired semantic closure differs from prepared authority")
    except PairedProfileRejected as exc:
        findings.append(ValidationFinding(
            layer="PAIRED-SEMANTIC", family="paired-semantic-closure",
            severity="blocking", blocking_consequence="Candidate semantic acceptance denied",
            semantic_identity="candidate-paired-semantic-closure",
            location="CandidatePresentationPackageRecord.extensions",
            message=str(exc), referenced_identities=(),
        ))
    combined = ValidationResult(tuple(findings), tuple(technical.executed_layers) + ("PAIRED-SEMANTIC",))
    return _GovernedValidationResult(
        combined, PAIRED_SEMANTIC_VALIDATION_PROFILE,
        expected_semantic_closure_sha256, observed,
    )


def _canonical(document: dict[str, Any]) -> bytes:
    try:
        return json.dumps(document, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise CandidateAuthoringError("commitment is not canonical JSON") from exc


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _safe_identity(value: Any) -> bool:
    return isinstance(value, str) and bool(value) and value not in {".", ".."} and all(
        c.isalnum() or c in "-_.:" for c in value)


def fingerprint_authoring_input(brief: RecordDraft, material: RecordDraft,
                                candidate: RecordDraft) -> str:
    """Fingerprint the three named RecordDraft inputs in fixed role order."""
    if not all(isinstance(item, RecordDraft) for item in (brief, material, candidate)):
        raise CandidateAuthoringError("authoring input requires three RecordDraft values")
    document = {
        "format": "briefforge-candidate-authoring-input-v1",
        "brief": asdict(brief), "material": asdict(material), "candidate": asdict(candidate),
    }
    return _digest(_canonical(document))


# Descriptive alias for callers that prefer a digest verb.
authoring_input_sha256 = fingerprint_authoring_input


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _durable_mkdir(path: Path) -> None:
    """Create missing directory components and fsync each containing directory."""
    path = Path(path)
    missing: list[Path] = []
    cursor = path
    while not cursor.exists():
        missing.append(cursor)
        cursor = cursor.parent
    if cursor.is_symlink() or not cursor.is_dir():
        raise CandidateAuthoringError("directory ancestry is not a real directory")
    for directory in reversed(missing):
        directory.mkdir()
        _fsync_directory(directory.parent)


def _require_real_directory(path: Path, message: str) -> None:
    try:
        mode = path.lstat().st_mode
    except OSError as exc:
        raise CandidateAuthoringError(message) from exc
    if not stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
        raise CandidateAuthoringError(message)


def _require_regular_file(path: Path, message: str) -> None:
    try:
        mode = path.lstat().st_mode
    except OSError as exc:
        raise CandidateAuthoringError(message) from exc
    if not stat.S_ISREG(mode) or stat.S_ISLNK(mode):
        raise CandidateAuthoringError(message)


def _exclusive_commit(path: Path, data: bytes) -> None:
    """Publish with an exclusive hard link, then durably remove its temporary name."""
    _durable_mkdir(path.parent)
    temporary = path.parent / f".{path.name}.{os.getpid()}.tmp"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(temporary, flags, 0o644)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as exc:
            raise CandidateAuthoringError(f"immutable commitment already exists: {path.name}") from exc
        _fsync_directory(path.parent)
    finally:
        try:
            temporary.unlink()
            _fsync_directory(path.parent)
        except FileNotFoundError:
            pass


def _validate_binding(binding: AuthorityBinding) -> None:
    predecessors = binding.predecessor_attempt_digests
    evidence_paths = binding.predecessor_evidence_paths
    if (not _safe_identity(binding.task_id) or not _safe_identity(binding.campaign_id) or
            not _safe_identity(binding.attempt_id) or not isinstance(predecessors, tuple) or
            not isinstance(evidence_paths, tuple) or len(evidence_paths) != len(predecessors) or
            not all(_sha256(item) for item in predecessors) or len(set(predecessors)) != len(predecessors) or
            type(binding.cumulative_attempt_number) is not int or
            binding.cumulative_attempt_number != len(predecessors) + 1 or
            not _sha256(binding.blueprint_fingerprint) or
            binding.campaign_id != f"blueprint:{binding.blueprint_fingerprint}" or
            not _sha256(binding.authoring_input_sha256) or
            not _safe_identity(binding.semantic_validation_profile) or
            not _sha256(binding.expected_semantic_closure_sha256) or
            not _sha256(binding.authority_decision_sha256)):
        raise CandidateAuthoringError("invalid campaign, history, attempt, input, or decision binding")


def _binding_document(binding: AuthorityBinding, path: Path) -> dict[str, Any]:
    """Serialize only a governed binding at the fixed authority root.

    The bounded TASK-071 operation imports this data helper. Publication remains
    an exclusive, separately authorized operation owned by that operation.
    """
    path = Path(path).absolute()
    _validate_binding(binding)
    if binding.scope != "governed" or path.parent != GOVERNED_AUTHORITY_ROOT.absolute():
        raise CandidateAuthoringError("authority serialization requires the fixed governed root")
    document = asdict(binding)
    document["material_ids"] = list(binding.material_ids)
    document["predecessor_attempt_digests"] = list(binding.predecessor_attempt_digests)
    document["predecessor_evidence_paths"] = list(binding.predecessor_evidence_paths)
    document["format"] = "briefforge-candidate-authority-v1"
    document["authority_path"] = str(path)
    return document


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _authenticated_file(path_text: str, expected_digest: str, message: str) -> Path:
    path = Path(path_text)
    if not path.is_absolute():
        raise CandidateAuthoringError(message)
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise CandidateAuthoringError(message) from exc
    if path != resolved:
        raise CandidateAuthoringError(message)
    _require_regular_file(path, message)
    if _digest(path.read_bytes()) != expected_digest:
        raise CandidateAuthoringError(message)
    return path


def _authenticate_authority_evidence(
    binding: AuthorityBinding,
    authority_root: Path | None = None,
    expected_scope: str | None = None,
) -> None:
    """Authenticate explicit evidence, not a generic sibling-attempt registry.

    Canonical authority creation remains the governance boundary. This module can
    authenticate only bound predecessors and cannot detect unlisted siblings.
    Legacy arguments are accepted only when they restate the fixed governed root
    and scope; they cannot select an alternate authority domain.
    """
    if (authority_root is not None and
            Path(authority_root).absolute() != GOVERNED_AUTHORITY_ROOT.absolute()):
        raise CandidateAuthoringError("authority evidence root must be the fixed governed root")
    if expected_scope is not None and expected_scope != "governed":
        raise CandidateAuthoringError("authority evidence scope must be governed")
    decision = _authenticated_file(binding.authority_decision_path,
                                   binding.authority_decision_sha256,
                                   "authority decision evidence is absent or contradictory")
    predecessors = tuple(
        _authenticated_file(path, digest, "predecessor evidence is absent or contradictory")
        for path, digest in zip(binding.predecessor_evidence_paths,
                                binding.predecessor_attempt_digests)
    )
    if len(set(predecessors)) != len(predecessors):
        raise CandidateAuthoringError("predecessor evidence paths must be distinct")
    decisions_root = (PROJECT_ROOT / "artifacts/decisions").absolute()
    if not _is_within(decision, decisions_root) or any(
            not _is_within(path, PROJECT_ROOT.absolute()) for path in predecessors):
        raise CandidateAuthoringError("governed authority evidence path is outside fixed roots")


class CandidateAuthoringCoordinator:
    """Internal coordinator fixed to the canonical governed roots and operations."""

    def __init__(self):
        self.authority_root = GOVERNED_AUTHORITY_ROOT.absolute()
        self.ledger_root = GOVERNED_LEDGER_ROOT.absolute()
        self.output_root = GOVERNED_OUTPUT_ROOT.absolute()
        for root in (self.authority_root, self.ledger_root, self.output_root):
            if root.exists() and (root.is_symlink() or not root.is_dir()):
                raise CandidateAuthoringError("coordinator roots must be real directories")

    def _authority(self, path: Path, expected_digest: str) -> tuple[AuthorityBinding, bytes]:
        path = Path(path).absolute()
        if path.parent != self.authority_root:
            raise CandidateAuthoringError("authority path is outside the canonical authority root")
        _require_regular_file(path, "authority must be a regular non-symlink file")
        data = path.read_bytes()
        if not _sha256(expected_digest) or _digest(data) != expected_digest:
            raise CandidateAuthoringError("authority digest drift")
        try:
            document = json.loads(data)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CandidateAuthoringError("malformed authority JSON") from exc
        if not isinstance(document, dict) or _canonical(document) != data:
            raise CandidateAuthoringError("authority is not exact canonical JSON")
        fields = set(AuthorityBinding.__dataclass_fields__)
        if document.get("format") != "briefforge-candidate-authority-v1" or set(document) != fields | {"format", "authority_path"}:
            raise CandidateAuthoringError("authority format or field drift")
        if document.get("authority_path") != str(path):
            raise CandidateAuthoringError("copied, renamed, or stale authority path")
        values = {name: document[name] for name in fields}
        try:
            values["material_ids"] = tuple(values["material_ids"])
            values["predecessor_attempt_digests"] = tuple(values["predecessor_attempt_digests"])
            values["predecessor_evidence_paths"] = tuple(values["predecessor_evidence_paths"])
            binding = AuthorityBinding(**values)
        except (TypeError, KeyError) as exc:
            raise CandidateAuthoringError("malformed authority binding") from exc
        _validate_binding(binding)
        _authenticate_authority_evidence(binding)
        if (binding.scope != "governed" or Path(binding.ledger_root).absolute() != self.ledger_root or
                Path(binding.output_root).absolute() != self.output_root or
                path.name != f"{binding.attempt_id}.authority.json"):
            raise CandidateAuthoringError("authority binding or configured path drift")
        if (binding.validator_identity != PAIRED_CANDIDATE_VALIDATOR_IDENTITY or
                binding.semantic_validation_profile != PAIRED_SEMANTIC_VALIDATION_PROFILE):
            raise CandidateAuthoringError("governed paired semantic validator identity is fixed")
        return binding, data

    def _directory(self, binding: AuthorityBinding) -> Path:
        _require_real_directory(self.ledger_root, "ledger root is absent or unsafe")
        directory = self.ledger_root / binding.attempt_id
        _require_real_directory(directory, "pre-existing prepared ledger is absent or unsafe")
        return directory

    def _lock(self, binding: AuthorityBinding):
        directory = self._directory(binding)
        lock_path = directory / ".attempt.lock"
        if lock_path.exists() or lock_path.is_symlink():
            _require_regular_file(lock_path, "attempt lock is not a regular file")
        flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(lock_path, flags, 0o600)
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                raise CandidateAuthoringError("attempt lock symlink rejected") from exc
            raise
        fcntl.flock(fd, fcntl.LOCK_EX)
        return fd

    def _recover_commit_temporary(self, directory: Path) -> None:
        """Resolve the sole exact `_exclusive_commit` crash residue under the lock."""
        temporaries = [path for path in directory.iterdir() if path.name.endswith(".tmp")]
        if not temporaries:
            return
        if len(temporaries) != 1:
            raise CandidateAuthoringError("multiple private commit temporaries rejected")
        temporary = temporaries[0]
        match = re.fullmatch(r"\.(.+)\.([0-9]+)\.tmp", temporary.name)
        if match is None:
            raise CandidateAuthoringError("malformed private commit temporary rejected")
        target_name = match.group(1)
        state_match = re.fullmatch(r"[0-9]{2}-(.+)\.json", target_name)
        admitted = bool(state_match and state_match.group(1) in _STATES)
        admitted = admitted or bool(re.fullmatch(r"validation-evidence-[0-9]{2}\.json", target_name))
        admitted = admitted or bool(re.fullmatch(
            r"\.terminal-[0-9]{2}-[0-9a-f]{64}\.txn", target_name))
        if not admitted:
            raise CandidateAuthoringError("unrecognized private commit target rejected")
        _require_regular_file(temporary, "private commit temporary is unsafe")
        target = directory/target_name
        if target.exists() or target.is_symlink():
            _require_regular_file(target, "private commit target is unsafe")
            if (target.stat().st_ino != temporary.stat().st_ino or
                    target.read_bytes() != temporary.read_bytes()):
                raise CandidateAuthoringError("private commit temporary/target contradiction")
        temporary.unlink()
        _fsync_directory(directory)

    def _ledger_inventory(self, directory: Path) -> set[str]:
        names: set[str] = set()
        for path in directory.iterdir():
            if path.is_symlink():
                raise CandidateAuthoringError("ledger symlink entry rejected")
            names.add(path.name)
        return names

    def _read_states(self, binding: AuthorityBinding, authority_digest: str) -> list[tuple[dict[str, Any], str]]:
        directory = self._directory(binding)
        self._recover_commit_temporary(directory)
        names_on_disk = self._ledger_inventory(directory)
        paths = sorted(p for p in directory.iterdir() if p.name[:2].isdigit() and p.name.endswith(".json"))
        if not paths:
            raise CandidateAuthoringError("prepared state is absent")
        result: list[tuple[dict[str, Any], str]] = []
        prior = None
        for sequence, path in enumerate(paths):
            _require_regular_file(path, "immutable state is not a regular file")
            data = path.read_bytes()
            try:
                document = json.loads(data)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise CandidateAuthoringError("malformed immutable state") from exc
            if (not isinstance(document, dict) or set(document) != _STATE_KEYS or _canonical(document) != data or
                    document.get("format") != "briefforge-candidate-attempt-state-v1" or
                    document.get("sequence") != sequence):
                raise CandidateAuthoringError("state canonicalization, shape, or sequence contradiction")
            state = document.get("state")
            if state not in _STATES or document.get("authority_digest") != authority_digest or document.get("prior_state_digest") != prior:
                raise CandidateAuthoringError("state binding contradiction")
            if path.name != f"{sequence:02d}-{state}.json":
                raise CandidateAuthoringError("state path drift")
            if not isinstance(document["detail"], dict):
                raise CandidateAuthoringError("state detail is malformed")
            if state in {"PREPARED_NOT_CONSUMED", "INVOKED_CONSUMED",
                         "INDETERMINATE_CONSUMED_NO_OUTPUT"} and document["detail"] != {}:
                raise CandidateAuthoringError("state detail contradicts its stage")
            digest = _digest(data)
            result.append((document, digest))
            prior = digest
        states = tuple(item[0]["state"] for item in result)
        admitted = {
            ("PREPARED_NOT_CONSUMED",),
            ("PREPARED_NOT_CONSUMED", "INVOKED_CONSUMED"),
            ("PREPARED_NOT_CONSUMED", "INVOKED_CONSUMED", "INDETERMINATE_CONSUMED_NO_OUTPUT"),
            ("PREPARED_NOT_CONSUMED", "INVOKED_CONSUMED", "AUTHORED_OUTPUT_DURABLY_STAGED"),
            ("PREPARED_NOT_CONSUMED", "INVOKED_CONSUMED", "AUTHORED_OUTPUT_DURABLY_STAGED", "VALIDATION_PENDING"),
            ("PREPARED_NOT_CONSUMED", "INVOKED_CONSUMED", "AUTHORED_OUTPUT_DURABLY_STAGED", "VALIDATION_PENDING", "VALIDATED_ACCEPTED"),
            ("PREPARED_NOT_CONSUMED", "INVOKED_CONSUMED", "AUTHORED_OUTPUT_DURABLY_STAGED", "VALIDATION_PENDING", "VALIDATED_NOT_ACCEPTED"),
        }
        if states not in admitted:
            raise CandidateAuthoringError("state transition is not admitted by the monotonic model")
        allowed = {".attempt.lock", *(p.name for p in paths)}
        transactions = {name for name in names_on_disk
                        if re.fullmatch(r"\.terminal-[0-9]{2}-[0-9a-f]{64}\.txn", name)}
        if len(transactions) > 1:
            raise CandidateAuthoringError("multiple terminal transactions rejected")
        if states[-1] == "VALIDATION_PENDING":
            evidence_name = f"validation-evidence-{len(result):02d}.json"
            allowed.add(evidence_name)
            if evidence_name in names_on_disk:
                allowed.update(transactions)
        if states[-1] in {"VALIDATED_ACCEPTED", "VALIDATED_NOT_ACCEPTED"}:
            detail = result[-1][0]["detail"]
            evidence_name = detail.get("validation_evidence_file")
            if isinstance(evidence_name, str):
                allowed.add(evidence_name)
            allowed.add("terminal.seal.json")
            allowed.add(self._terminal_tx_name(result[-1][0], result[-1][1]))
        if names_on_disk - allowed:
            raise CandidateAuthoringError("unknown ledger entry rejected")
        return result

    def _append(self, binding: AuthorityBinding, authority_digest: str, states, state: str, detail=None):
        sequence = len(states)
        document = {"format": "briefforge-candidate-attempt-state-v1", "sequence": sequence,
                    "state": state, "authority_digest": authority_digest,
                    "prior_state_digest": states[-1][1], "detail": detail or {}}
        data = _canonical(document)
        _exclusive_commit(self._directory(binding)/f"{sequence:02d}-{state}.json", data)
        states.append((document, _digest(data)))

    def _stage(self, binding: AuthorityBinding, authority_digest: str,
               bundle: BCRPBundle) -> tuple[str, str]:
        final = self.output_root / binding.attempt_id
        if final.exists() or final.is_symlink():
            raise CandidateAuthoringError("attempt output already exists")
        _durable_mkdir(self.output_root)
        _require_real_directory(self.output_root, "output root is unsafe")
        temporary = self.output_root / f".{binding.attempt_id}.staging"
        temporary.mkdir(mode=0o755)
        _fsync_directory(self.output_root)
        profile = canonical_json_bytes(bundle, domain="profile-instance", require_valid=False)
        semantic = canonical_json_bytes(bundle, domain="candidate-semantic", require_valid=False)
        fingerprint = fingerprint_bundle(bundle, domain="candidate-semantic", require_valid=False)
        payload = {"profile.json": profile, "candidate-semantic.json": semantic,
                   "fingerprint.json": _canonical(asdict(fingerprint))}
        inventory = {name: {"sha256": _digest(data), "size": len(data)} for name, data in sorted(payload.items())}
        inventory_bytes = _canonical({"format": "briefforge-candidate-stage-inventory-v1", "files": inventory})
        receipt_doc = {"format": "briefforge-candidate-authoring-receipt-v1",
                       "attempt_id": binding.attempt_id, "authority_digest": authority_digest,
                       "candidate_id": binding.candidate_id, "candidate_fingerprint": fingerprint.digest,
                       "authoring_input_sha256": binding.authoring_input_sha256,
                       "inventory_sha256": _digest(inventory_bytes), "governed": True}
        receipt_bytes = _canonical(receipt_doc)
        payload.update({"inventory.json": inventory_bytes, "authoring-receipt.json": receipt_bytes})
        for name, data in payload.items():
            _exclusive_commit(temporary/name, data)
        _fsync_directory(temporary)
        os.rename(temporary, final)
        _fsync_directory(self.output_root)
        return _digest(receipt_bytes), fingerprint.digest

    def _authenticate_stage(self, binding: AuthorityBinding, authority_digest: str) -> tuple[BCRPBundle, str, str]:
        stage = self.output_root / binding.attempt_id
        _require_real_directory(stage, "staged closure absent or unsafe")
        entries = list(stage.iterdir())
        if any(p.is_symlink() or not p.is_file() for p in entries) or {p.name for p in entries} != _STAGE_FILES:
            raise CandidateAuthoringError("staged closure incomplete, unsafe, or contains unknown files")
        try:
            files = {name: (stage/name).read_bytes() for name in _STAGE_FILES}
            inventory = json.loads(files["inventory.json"])
            receipt = json.loads(files["authoring-receipt.json"])
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CandidateAuthoringError("malformed staged bytes") from exc
        if _canonical(inventory) != files["inventory.json"] or _canonical(receipt) != files["authoring-receipt.json"]:
            raise CandidateAuthoringError("noncanonical staged commitment")
        expected_inventory = {name: {"sha256": _digest(files[name]), "size": len(files[name])}
                              for name in sorted(("profile.json", "candidate-semantic.json", "fingerprint.json"))}
        if inventory != {"format": "briefforge-candidate-stage-inventory-v1", "files": expected_inventory}:
            raise CandidateAuthoringError("staged inventory/file mismatch")
        expected_receipt = {"format": "briefforge-candidate-authoring-receipt-v1",
                            "attempt_id": binding.attempt_id, "authority_digest": authority_digest,
                            "candidate_id": binding.candidate_id,
                            "candidate_fingerprint": receipt.get("candidate_fingerprint"),
                            "authoring_input_sha256": binding.authoring_input_sha256,
                            "inventory_sha256": _digest(files["inventory.json"]),
                            "governed": True}
        if receipt != expected_receipt:
            raise CandidateAuthoringError("staged receipt binding mismatch")
        try:
            bundle = bundle_from_canonical_json(files["profile.json"])
            profile = canonical_json_bytes(bundle, domain="profile-instance", require_valid=False)
            semantic = canonical_json_bytes(bundle, domain="candidate-semantic", require_valid=False)
            fingerprint = fingerprint_bundle(bundle, domain="candidate-semantic", require_valid=False)
            fingerprint_doc = json.loads(files["fingerprint.json"])
        except Exception as exc:
            raise CandidateAuthoringError("malformed or contradictory staged profile") from exc
        if (profile != files["profile.json"] or semantic != files["candidate-semantic.json"] or
                fingerprint_doc != asdict(fingerprint) or receipt.get("candidate_fingerprint") != fingerprint.digest):
            raise CandidateAuthoringError("staged profile/semantic/fingerprint/receipt disagreement")
        candidate_ids = tuple(record.identity for record in bundle.records_of_kind("CandidatePresentationPackageRecord"))
        brief_ids = tuple(record.identity for record in bundle.records_of_kind("PresentationBriefRecord"))
        material_ids = tuple(record.identity for record in bundle.records_of_kind("PortablePresentationMaterialRecord"))
        if candidate_ids != (binding.candidate_id,) or brief_ids != (binding.brief_id,) or material_ids != binding.material_ids or len(bundle.records) != 3:
            raise CandidateAuthoringError("staged Candidate closure identity differs from prepared authority")
        return bundle, _digest(files["authoring-receipt.json"]), fingerprint.digest

    def _authenticate_state_details(self, states, stage_digest: str, fingerprint: str) -> None:
        for document, _ in states:
            state, detail = document["state"], document["detail"]
            if state in {"PREPARED_NOT_CONSUMED", "INVOKED_CONSUMED"} and detail != {}:
                raise CandidateAuthoringError("state detail contradicts its stage")
            if state == "AUTHORED_OUTPUT_DURABLY_STAGED" and detail != {
                    "stage_receipt_sha256": stage_digest, "candidate_fingerprint": fingerprint}:
                raise CandidateAuthoringError("authored state detail/stage mismatch")
            if state == "VALIDATION_PENDING" and detail != {"stage_receipt_sha256": stage_digest}:
                raise CandidateAuthoringError("pending state detail/stage mismatch")

    def _validation_evidence(self, binding, stage_digest, fingerprint, result) -> tuple[bytes, bool]:
        if isinstance(result, _GovernedValidationResult):
            passed = not result.blocking
            layers = list(result.technical.executed_layers)
            findings = [asdict(item) for item in result.technical.findings]
            result_kind = "bcrp-plus-paired-semantic-validation-result"
            semantic_evidence = {
                "profile": result.semantic_validation_profile,
                "expected_closure_sha256": result.expected_semantic_closure_sha256,
                "observed_closure_sha256": result.observed_semantic_closure_sha256,
            }
        else:
            raise CandidateAuthoringError("governed validation requires paired semantic evidence")
        evidence = {"format": "briefforge-candidate-validation-evidence-v1",
                    "validator_identity": binding.validator_identity,
                    "stage_receipt_sha256": stage_digest,
                    "candidate_fingerprint": fingerprint,
                    "passed": passed, "result_kind": result_kind,
                    "executed_layers": layers, "findings": findings,
                    "semantic_validation": semantic_evidence}
        return _canonical(evidence), passed

    def _semantic_evidence_matches(self, binding, evidence) -> bool:
        semantic = evidence.get("semantic_validation")
        if (type(semantic) is not dict or set(semantic) != {
                "profile", "expected_closure_sha256", "observed_closure_sha256"} or
                semantic.get("profile") != binding.semantic_validation_profile or
                semantic.get("expected_closure_sha256") != binding.expected_semantic_closure_sha256):
            return False
        observed = semantic.get("observed_closure_sha256")
        if observed is not None and not _sha256(observed):
            return False
        return not evidence.get("passed") or observed == binding.expected_semantic_closure_sha256

    def _read_pending_validation_evidence(self, binding, states, stage_digest, fingerprint):
        """Authenticate a durable validator result written before terminal publication."""
        name = f"validation-evidence-{len(states):02d}.json"
        path = self._directory(binding) / name
        _require_regular_file(path, "pending validation evidence absent or unsafe")
        data = path.read_bytes()
        try:
            evidence = json.loads(data)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CandidateAuthoringError("pending validation evidence malformed") from exc
        required = {
            "format", "validator_identity", "stage_receipt_sha256",
            "candidate_fingerprint", "passed", "result_kind",
            "executed_layers", "findings", "semantic_validation",
        }
        if (not isinstance(evidence, dict) or set(evidence) != required or
                _canonical(evidence) != data or
                evidence.get("format") != "briefforge-candidate-validation-evidence-v1" or
                evidence.get("validator_identity") != binding.validator_identity or
                evidence.get("stage_receipt_sha256") != stage_digest or
                evidence.get("candidate_fingerprint") != fingerprint or
                not isinstance(evidence.get("passed"), bool) or
                not isinstance(evidence.get("executed_layers"), list) or
                not isinstance(evidence.get("findings"), list) or
                not self._semantic_evidence_matches(binding, evidence)):
            raise CandidateAuthoringError("pending validation evidence binding contradiction")
        return name, data, evidence["passed"]

    def _terminal_tx_name(self, document, digest: str) -> str:
        return f".terminal-{document['sequence']:02d}-{digest}.txn"

    def _publish_terminal(self, binding, authority_digest, states, terminal, detail):
        """Complete the terminal hard-link transaction idempotently in every window."""
        sequence = len(states)
        document = {"format": "briefforge-candidate-attempt-state-v1", "sequence": sequence,
                    "state": terminal, "authority_digest": authority_digest,
                    "prior_state_digest": states[-1][1], "detail": detail}
        data = _canonical(document)
        digest = _digest(data)
        directory = self._directory(binding)
        transaction = directory / self._terminal_tx_name(document, digest)
        state_path = directory / f"{sequence:02d}-{terminal}.json"
        seal_path = directory / "terminal.seal.json"
        retained = {path for path in directory.iterdir()
                    if re.fullmatch(r"\.terminal-[0-9]{2}-[0-9a-f]{64}\.txn", path.name)}
        if retained - {transaction}:
            raise CandidateAuthoringError("wrong terminal recovery transaction rejected")
        if transaction.exists() or transaction.is_symlink():
            _require_regular_file(transaction, "terminal recovery transaction is unsafe")
            if transaction.read_bytes() != data:
                raise CandidateAuthoringError("terminal recovery transaction contradiction")
        else:
            if state_path.exists() or state_path.is_symlink() or seal_path.exists() or seal_path.is_symlink():
                raise CandidateAuthoringError("terminal links exist without exact transaction")
            _exclusive_commit(transaction, data)
        for path in (state_path, seal_path):
            if path.exists() or path.is_symlink():
                _require_regular_file(path, "terminal hard-link evidence is unsafe")
                if (path.read_bytes() != data or
                        path.stat().st_ino != transaction.stat().st_ino):
                    raise CandidateAuthoringError("terminal hard-link evidence contradiction")
            else:
                os.link(transaction, path)
                _fsync_directory(directory)

        transaction.unlink()
        _fsync_directory(directory)
        states.append((document, digest))

    def _complete_or_authenticate_terminal(self, binding, states) -> None:
        directory = self._directory(binding)
        document, digest = states[-1]
        state_path = directory / f"{document['sequence']:02d}-{document['state']}.json"
        seal_path = directory / "terminal.seal.json"
        transaction = directory / self._terminal_tx_name(document, digest)
        if transaction.exists() or transaction.is_symlink():
            _require_regular_file(transaction, "terminal recovery transaction is unsafe")
            if (transaction.read_bytes() != state_path.read_bytes() or
                    transaction.stat().st_ino != state_path.stat().st_ino):
                raise CandidateAuthoringError("terminal recovery transaction contradiction")
        elif not seal_path.exists():
            raise CandidateAuthoringError("terminal seal is absent without exact recovery transaction")
        if not seal_path.exists():
            os.link(transaction, seal_path)
            _fsync_directory(directory)
        _require_regular_file(seal_path, "terminal seal is unsafe")
        if seal_path.read_bytes() != state_path.read_bytes() or seal_path.stat().st_ino != state_path.stat().st_ino:
            raise CandidateAuthoringError("terminal dual evidence contradiction")
        if transaction.exists():
            transaction.unlink()
            _fsync_directory(directory)

    def _authenticate_evidence(self, binding, terminal_document, stage_digest, fingerprint) -> None:
        detail = terminal_document["detail"]
        required = {"stage_receipt_sha256", "candidate_fingerprint", "validator_identity",
                    "validation_evidence_file", "validation_evidence_sha256"}
        if set(detail) != required or detail["stage_receipt_sha256"] != stage_digest or detail["candidate_fingerprint"] != fingerprint or detail["validator_identity"] != binding.validator_identity:
            raise CandidateAuthoringError("terminal detail/stage contradiction")
        name = detail["validation_evidence_file"]
        if name != f"validation-evidence-{terminal_document['sequence']:02d}.json" or not _sha256(detail["validation_evidence_sha256"]):
            raise CandidateAuthoringError("terminal validation evidence reference is unsafe")
        path = self._directory(binding) / name
        _require_regular_file(path, "validation evidence absent or unsafe")
        data = path.read_bytes()
        try:
            evidence = json.loads(data)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CandidateAuthoringError("validation evidence malformed") from exc
        if _canonical(evidence) != data or _digest(data) != detail["validation_evidence_sha256"]:
            raise CandidateAuthoringError("validation evidence digest/canonicalization mismatch")
        if (evidence.get("validator_identity") != binding.validator_identity or
                evidence.get("stage_receipt_sha256") != stage_digest or
                evidence.get("candidate_fingerprint") != fingerprint or
                not isinstance(evidence.get("passed"), bool) or
                evidence["passed"] != (terminal_document["state"] == "VALIDATED_ACCEPTED") or
                not isinstance(evidence.get("executed_layers"), list) or
                not isinstance(evidence.get("findings"), list) or
                not self._semantic_evidence_matches(binding, evidence)):
            raise CandidateAuthoringError("validation evidence binding contradiction")

    def _receipt(self, binding, state, fingerprint=None, stage_digest=None):
        return AuthoringReceipt(binding.attempt_id, state, binding.candidate_id,
                                fingerprint, stage_digest, True)

    def _author_governed(self, authority_path, authority_digest, brief, material, candidate):
        binding, _ = self._authority(authority_path, authority_digest)
        drafts = (brief, material, candidate)
        self._preflight_input_identities(binding, drafts)
        input_digest = fingerprint_authoring_input(*drafts)
        if input_digest != binding.authoring_input_sha256:
            raise CandidateAuthoringError("exact authoring input digest differs from authority")
        lock = self._lock(binding)
        try:
            states = self._read_states(binding, authority_digest)
            if len(states) != 1:
                raise CandidateAuthoringError("duplicate or already consumed Candidate attempt")
            self._append(binding, authority_digest, states, "INVOKED_CONSUMED")
            bundle = build_candidate_bundle(
                brief=brief, material=material, candidate=candidate)
            stage_digest, fingerprint = self._stage(binding, authority_digest, bundle)
            self._append(binding, authority_digest, states, "AUTHORED_OUTPUT_DURABLY_STAGED",
                         {"stage_receipt_sha256": stage_digest, "candidate_fingerprint": fingerprint})
            self._append(binding, authority_digest, states, "VALIDATION_PENDING",
                         {"stage_receipt_sha256": stage_digest})
            return self._validate(binding, authority_digest, states)
        finally:
            os.close(lock)

    def _preflight_input_identities(self, binding, drafts) -> None:
        if (not isinstance(drafts, tuple) or len(drafts) != 3 or
                not all(isinstance(draft, RecordDraft) for draft in drafts)):
            raise CandidateAuthoringError("governed authoring requires the exact three draft roles")
        brief, material, candidate = drafts
        if (brief.identity != binding.brief_id or
                binding.material_ids != (material.identity,) or
                candidate.identity != binding.candidate_id):
            raise CandidateAuthoringError("draft identities or material cardinality differ from authority")

    def _validate(self, binding, authority_digest, states):
        bundle, stage_digest, fingerprint = self._authenticate_stage(binding, authority_digest)
        self._authenticate_state_details(states, stage_digest, fingerprint)
        result = _validate_governed_paired_candidate(
            bundle, binding.expected_semantic_closure_sha256)
        evidence_bytes, passed = self._validation_evidence(binding, stage_digest, fingerprint, result)
        evidence_name = f"validation-evidence-{len(states):02d}.json"
        _exclusive_commit(self._directory(binding)/evidence_name, evidence_bytes)
        evidence_digest = _digest(evidence_bytes)
        terminal = "VALIDATED_ACCEPTED" if passed else "VALIDATED_NOT_ACCEPTED"
        detail = {"stage_receipt_sha256": stage_digest, "candidate_fingerprint": fingerprint,
                  "validator_identity": binding.validator_identity,
                  "validation_evidence_file": evidence_name,
                  "validation_evidence_sha256": evidence_digest}
        self._publish_terminal(binding, authority_digest, states, terminal, detail)
        return self._receipt(binding, terminal, fingerprint, stage_digest)

    def _recover_governed(self, authority_path, authority_digest):
        binding, _ = self._authority(authority_path, authority_digest)
        lock = self._lock(binding)
        try:
            states = self._read_states(binding, authority_digest)
            names = [item[0]["state"] for item in states]
            seal_path = self._directory(binding)/"terminal.seal.json"
            if names[-1] in {"VALIDATED_ACCEPTED", "VALIDATED_NOT_ACCEPTED"}:
                bundle, stage_digest, fingerprint = self._authenticate_stage(binding, authority_digest)
                del bundle
                self._authenticate_state_details(states, stage_digest, fingerprint)
                self._authenticate_evidence(binding, states[-1][0], stage_digest, fingerprint)
                self._complete_or_authenticate_terminal(binding, states)
                return self._receipt(binding, names[-1], fingerprint, stage_digest)
            if seal_path.exists() or seal_path.is_symlink():
                raise CandidateAuthoringError("terminal state deletion or seal contradiction")
            if names[-1] == "INDETERMINATE_CONSUMED_NO_OUTPUT" or names == ["PREPARED_NOT_CONSUMED"]:
                return self._receipt(binding, names[-1])
            stage = self.output_root/binding.attempt_id
            if not stage.exists() and not stage.is_symlink():
                self._append(binding, authority_digest, states, "INDETERMINATE_CONSUMED_NO_OUTPUT")
                return self._receipt(binding, "INDETERMINATE_CONSUMED_NO_OUTPUT")
            bundle, stage_digest, fingerprint = self._authenticate_stage(binding, authority_digest)
            del bundle
            self._authenticate_state_details(states, stage_digest, fingerprint)
            if "AUTHORED_OUTPUT_DURABLY_STAGED" not in names:
                self._append(binding, authority_digest, states, "AUTHORED_OUTPUT_DURABLY_STAGED",
                             {"stage_receipt_sha256": stage_digest, "candidate_fingerprint": fingerprint})
            if "VALIDATION_PENDING" not in names:
                self._append(binding, authority_digest, states, "VALIDATION_PENDING",
                             {"stage_receipt_sha256": stage_digest})
            evidence_path = self._directory(binding) / f"validation-evidence-{len(states):02d}.json"
            if evidence_path.exists() or evidence_path.is_symlink():
                evidence_name, evidence_bytes, passed = self._read_pending_validation_evidence(
                    binding, states, stage_digest, fingerprint,
                )
                terminal = "VALIDATED_ACCEPTED" if passed else "VALIDATED_NOT_ACCEPTED"
                detail = {
                    "stage_receipt_sha256": stage_digest,
                    "candidate_fingerprint": fingerprint,
                    "validator_identity": binding.validator_identity,
                    "validation_evidence_file": evidence_name,
                    "validation_evidence_sha256": _digest(evidence_bytes),
                }
                self._publish_terminal(
                    binding, authority_digest, states, terminal, detail,
                )
                return self._receipt(binding, terminal, fingerprint, stage_digest)
            return self._validate(binding, authority_digest, states)
        finally:
            os.close(lock)


def governed_recover_candidate(authority_path: Path, authority_digest: str) -> AuthoringReceipt:
    """Recover governed authoring with fixed roots and fixed paired semantic validation."""
    path = Path(authority_path).absolute()
    if path.parent != GOVERNED_AUTHORITY_ROOT.absolute():
        raise CandidateAuthoringError("public governed boundary rejects noncanonical authority identities")
    coordinator = CandidateAuthoringCoordinator()
    return coordinator._recover_governed(path, authority_digest)


def governed_author_candidate(authority_path: Path, authority_digest: str,
                              brief: RecordDraft, material: RecordDraft,
                              candidate: RecordDraft) -> AuthoringReceipt:
    """Governed boundary with fixed construction, paired semantic validation, and roots."""
    path = Path(authority_path).absolute()
    if path.parent != GOVERNED_AUTHORITY_ROOT.absolute():
        raise CandidateAuthoringError("public governed boundary rejects noncanonical authority identities")
    coordinator = CandidateAuthoringCoordinator()
    return coordinator._author_governed(path, authority_digest, brief, material, candidate)
