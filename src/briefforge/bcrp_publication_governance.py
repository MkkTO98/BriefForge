"""Source-neutral native BCRP publication governance (TASK-073).

The module authenticates an already-authored three-record Candidate.  It never
loads evidence paths: locators are inert authenticated labels and all authority
comes from exact detached bytes supplied at the boundary.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Any
import secrets
import weakref

from .bcrp.canonical import canonical_json_bytes, canonicalize_timestamp, fingerprint_bundle
from .bcrp.model import BCRPBundle, BCRPRecord, Fingerprint, PROFILE_ID, PROFILE_VERSION
from .bcrp.validation import validate_bundle

GOVERNANCE_CONTRACT = "briefforge:bcrp-publication-governance:1.0.0"
JUDGMENT_POLICY_ID = "briefforge-bcrp-publication-judgment-policy:1.0.0"
JUDGMENT_AUTHORITY_IDENTITY = "authority:briefforge-publication-judgment"
JUDGMENT_AUTHORITY_OWNER = "project:BriefForge"
JUDGMENT_AUTHORITY_ROLE = "publication-judgment-authority"
JUDGMENT_SCOPE = "exact-native-bcrp-publication-subject"
READY_POLICY_ID = "briefforge-bcrp-publication-readiness-policy:1.0.0"
READY_AUTHORITY_IDENTITY = "authority:briefforge-publication-readiness"
READY_AUTHORITY_OWNER = "project:BriefForge"
READY_AUTHORITY_ROLE = "publication-readiness-authority"
READY_SCOPE = "accepted-native-bcrp-judgment"
ACCEPTED_VALIDATOR_IDENTITY = "briefforge:bcrp-L0-L2+paired-semantic-closure:1.0.0"
ACCEPTED_VALIDATION_PROFILE = "briefforge:paired-terminal-semantic-closure:1.0.0"
ACCEPTED_EXECUTED_LAYERS = ("L0", "L1", "L2", "PAIRED-SEMANTIC")

_OWNER = "briefforge-bcrp-publication-governance"
_VERSION = "1.0.0"
_EXT_KEYS = {"owner_namespace", "name", "version", "authority_ref", "scope", "target_refs",
             "criticality", "character", "validation_contract", "preservation", "payload"}
_CANDIDATE_KINDS = ("PresentationBriefRecord", "PortablePresentationMaterialRecord",
                    "CandidatePresentationPackageRecord")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*$")
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_NATIVE_AUTHORITY_ROOT = _PROJECT_ROOT / "artifacts/governance/bcrp-publication-authority"


class NativeGovernanceRejected(ValueError):
    """No verified native-governance result may be returned."""


@dataclass(frozen=True)
class GovernedCandidateAdmission:
    """Detached authentication material for one retained Candidate attempt.

    Paths are evidence locators only.  Exact bytes, not path contents, are
    verified.  ``retained_stage_inventory_digest`` is the digest returned by
    :func:`compute_retained_stage_inventory_digest`.
    """
    profile_bytes: bytes
    candidate_semantic_bytes: bytes
    fingerprint_bytes: bytes
    inventory_bytes: bytes
    authoring_receipt_bytes: bytes
    candidate_authority_bytes: bytes
    candidate_authority_locator: str
    candidate_authority_sha256: str
    retained_stage_inventory_digest: str
    candidate_identity: str
    candidate_semantic_fingerprint: str
    profile_instance_fingerprint: str
    attempt_identity: str
    cumulative_attempt_number: int
    terminal_state: str
    authority_digest: str
    terminal_state_bytes: bytes
    terminal_seal_bytes: bytes
    terminal_state_sha256: str
    terminal_seal_sha256: str
    receipt_locator: str
    receipt_sha256: str
    paired_semantic_closure_fingerprint: str
    source_snapshot_identity: str
    blueprint_identity: str
    blueprint_fingerprint: str
    validation_evidence_locator: str
    validation_evidence_bytes: bytes
    validation_evidence_sha256: str
    validator_identity: str
    validation_profile: str
    executed_layers: tuple[str, ...]


@dataclass(frozen=True)
class VerifiedBCRPPublicationSubject:
    _profile_bytes: bytes
    _admission_document: str
    candidate_identity: str
    candidate_semantic_fingerprint: str
    profile_instance_fingerprint: str
    closure_fingerprint: str

    @property
    def bundle(self) -> BCRPBundle:
        from .bcrp.canonical import bundle_from_canonical_json
        try:
            return bundle_from_canonical_json(bytes(self._profile_bytes))
        except Exception as exc:
            raise NativeGovernanceRejected("stored publication subject is invalid") from exc

    @property
    def profile_bytes(self) -> bytes:
        return bytes(self._profile_bytes)

    @property
    def admission(self) -> GovernedCandidateAdmission:
        return _admission_from_document(self._admission_document)


@dataclass(frozen=True)
class JudgmentAuthorization:
    identity: str
    policy_identity: str
    authority_identity: str
    authority_owner: str
    authority_role: str
    scope: str
    authority_basis: str
    authorization_time: str
    decision_identity: str
    decision_time: str
    subject_closure_fingerprint: str
    candidate_identity: str
    candidate_semantic_fingerprint: str
    validation_evidence_sha256: str
    validation_profile: str
    executed_layers: tuple[str, ...]
    disposition: str
    rationale: str
    findings: tuple[str, ...]


@dataclass(frozen=True)
class VerifiedNativeJudgment:
    _bundle_document: str
    _subject: VerifiedBCRPPublicationSubject
    fingerprint: Fingerprint
    authorization: JudgmentAuthorization

    @property
    def bundle(self) -> BCRPBundle:
        return _bundle_from_text(self._bundle_document)

    @property
    def subject(self) -> VerifiedBCRPPublicationSubject:
        return _subject_again(self._subject)

    @property
    def judgment(self) -> BCRPRecord:
        return self.bundle.one("ValidationJudgmentRecord")

    @property
    def accepted(self) -> bool:
        return self.authorization.disposition == "accepted"


@dataclass(frozen=True)
class ReadyAuthorization:
    identity: str
    policy_identity: str
    authority_identity: str
    authority_owner: str
    authority_role: str
    scope: str
    authority_basis: str
    authorization_time: str
    candidate_identity: str
    subject_closure_fingerprint: str
    judgment_identity: str
    judgment_fingerprint: str
    ready_identity: str
    readiness_time: str


class _IssuerToken:
    __slots__ = ("_kind", "_evidence", "_target", "_nonce", "__weakref__")
    def __init__(self, *args, **kwargs):
        raise TypeError("native governance authorization tokens are issuer-only")
    def __copy__(self):
        raise TypeError("native governance authorization tokens cannot be copied")
    def __deepcopy__(self, memo):
        raise TypeError("native governance authorization tokens cannot be copied")
    def __reduce__(self):
        raise TypeError("native governance authorization tokens cannot be serialized")
    def __setattr__(self, name, value):
        raise AttributeError("native governance authorization tokens are immutable")


class JudgmentAuthorizationToken(_IssuerToken):
    pass


class ReadyAuthorizationToken(_IssuerToken):
    pass


_issued_authorizations: "weakref.WeakKeyDictionary[_IssuerToken, str]" = weakref.WeakKeyDictionary()


def _issue_authorization_token(cls, kind: str, evidence: bytes, target: str):
    token = object.__new__(cls)
    object.__setattr__(token, "_kind", kind)
    object.__setattr__(token, "_evidence", bytes(evidence))
    object.__setattr__(token, "_target", target)
    object.__setattr__(token, "_nonce", secrets.token_bytes(32))
    _issued_authorizations[token] = _sha(_canonical({"kind": kind, "evidence_sha256": _sha(evidence),
        "target": target, "nonce": token._nonce.hex()}))
    return token


def _reserve_authorization_token(token, cls, kind: str, target: str) -> dict[str, Any]:
    """Validate one issued token without consuming it before production succeeds."""
    if type(token) is not cls or token not in _issued_authorizations:
        raise NativeGovernanceRejected("issuer-only native governance authorization token is required")
    seal = _sha(_canonical({"kind": token._kind, "evidence_sha256": _sha(token._evidence),
        "target": token._target, "nonce": token._nonce.hex()}))
    if (_issued_authorizations.get(token) != seal or token._kind != kind or token._target != target):
        raise NativeGovernanceRejected("native governance authorization token is altered or mistargeted")
    return _json_exact(token._evidence, f"{kind} authorization evidence")


def _commit_authorization_token(token, cls, kind: str, target: str) -> None:
    """Consume only the exact token that was reserved for this completed/indeterminate act."""
    _reserve_authorization_token(token, cls, kind, target)
    del _issued_authorizations[token]


@dataclass(frozen=True)
class VerifiedNativeReady:
    _bundle_document: str
    _judgment: VerifiedNativeJudgment
    fingerprint: Fingerprint
    authorization: ReadyAuthorization

    @property
    def bundle(self) -> BCRPBundle:
        return _bundle_from_text(self._bundle_document)

    @property
    def judgment_result(self) -> VerifiedNativeJudgment:
        return verify_native_judgment(self._judgment.bundle, self._judgment.subject)

    @property
    def subject(self) -> VerifiedBCRPPublicationSubject:
        return self.judgment_result.subject

    @property
    def ready(self) -> BCRPRecord:
        return self.bundle.one("ReadyPresentationPackageRecord")


def _canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                          allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise NativeGovernanceRejected("governance material is not canonical JSON") from exc


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _open_regular_without_symlink_ancestry(path: Path, label: str) -> int:
    """Open an absolute governed file through descriptor-anchored, non-symlink ancestry."""
    absolute = path.absolute()
    if not absolute.is_absolute():
        raise NativeGovernanceRejected(f"{label} location is not absolute")
    directory_flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) |
                       getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    file_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory_fd = os.open("/", directory_flags)
    try:
        parts = absolute.parts[1:]
        for component in parts[:-1]:
            next_fd = os.open(component, directory_flags, dir_fd=directory_fd)
            info = os.fstat(next_fd)
            if (not stat.S_ISDIR(info.st_mode) or info.st_uid not in (0, os.geteuid()) or
                    bool(info.st_mode & stat.S_IWOTH)):
                os.close(next_fd)
                raise NativeGovernanceRejected(
                    f"{label} ancestry is not trusted owned non-world-writable directory state")
            os.close(directory_fd)
            directory_fd = next_fd
        return os.open(parts[-1], file_flags, dir_fd=directory_fd)
    except OSError as exc:
        raise NativeGovernanceRejected(
            f"{label} is not available through trusted non-symlink ancestry") from exc
    finally:
        os.close(directory_fd)


def _read_exact_regular(path: Path, label: str) -> bytes:
    """Read one fixed governed evidence file through trusted non-symlink ancestry."""
    fd = _open_regular_without_symlink_ancestry(path, label)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise NativeGovernanceRejected(f"{label} is not one exact regular governed evidence file")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def _read_terminal_member(path: Path, label: str) -> bytes:
    fd = _open_regular_without_symlink_ancestry(path, label)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 2:
            raise NativeGovernanceRejected(f"{label} is not one exact two-link terminal file")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def _read_terminal_hardlink_pair(state_path: Path, seal_path: Path,
        state_bytes: bytes, seal_bytes: bytes) -> None:
    """Authenticate the coordinator's exact two-name immutable terminal inode."""
    descriptors: list[int] = []
    try:
        for path, label in ((state_path, "Candidate terminal state"),
                            (seal_path, "Candidate terminal seal")):
            descriptors.append(_open_regular_without_symlink_ancestry(path, label))
        infos = tuple(os.fstat(fd) for fd in descriptors)
        if (any(not stat.S_ISREG(info.st_mode) or info.st_nlink != 2 for info in infos) or
                (infos[0].st_dev, infos[0].st_ino) != (infos[1].st_dev, infos[1].st_ino)):
            raise NativeGovernanceRejected("Candidate terminal state and seal are not the exact hard-link pair")
        observed = []
        for fd in descriptors:
            chunks = []
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            observed.append(b"".join(chunks))
        if tuple(observed) != (state_bytes, seal_bytes):
            raise NativeGovernanceRejected("Candidate terminal state or seal bytes differ from governed evidence")
    except OSError as exc:
        raise NativeGovernanceRejected("Candidate terminal hard-link closure is unavailable") from exc
    finally:
        for fd in descriptors:
            os.close(fd)


def compute_retained_stage_inventory_digest(*, profile_bytes: bytes,
        candidate_semantic_bytes: bytes, fingerprint_bytes: bytes,
        inventory_bytes: bytes, authoring_receipt_bytes: bytes) -> str:
    values = (profile_bytes, candidate_semantic_bytes, fingerprint_bytes, inventory_bytes,
              authoring_receipt_bytes)
    if any(type(item) is not bytes for item in values):
        raise NativeGovernanceRejected("retained-stage inventory requires exact immutable bytes")
    files = dict(zip(("profile.json", "candidate-semantic.json", "fingerprint.json",
                      "inventory.json", "authoring-receipt.json"), values, strict=True))
    return _sha(_canonical({"format": "briefforge-retained-candidate-stage-inventory-v1",
        "files": {name: {"sha256": _sha(data), "size": len(data)}
                  for name, data in sorted(files.items())}}))


def _json_exact(data: bytes, label: str) -> dict[str, Any]:
    if type(data) is not bytes:
        raise NativeGovernanceRejected(f"{label} must be exact bytes")
    try:
        value = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NativeGovernanceRejected(f"{label} is malformed") from exc
    if type(value) is not dict or _canonical(value) != data:
        raise NativeGovernanceRejected(f"{label} is not an exact canonical object")
    return value


def _admission_document(value: GovernedCandidateAdmission) -> dict[str, Any]:
    result = asdict(value)
    for name in ("profile_bytes", "candidate_semantic_bytes", "fingerprint_bytes", "inventory_bytes",
                 "authoring_receipt_bytes", "candidate_authority_bytes", "terminal_state_bytes", "terminal_seal_bytes",
                 "validation_evidence_bytes"):
        result[name] = getattr(value, name).hex()
    result["executed_layers"] = list(value.executed_layers)
    return result


def _semantic_admission_binding(value: GovernedCandidateAdmission) -> dict[str, Any]:
    """Location-free authority binding carried through semantic lifecycle records."""
    return {
        "candidate_identity": value.candidate_identity,
        "candidate_semantic_fingerprint": value.candidate_semantic_fingerprint,
        "profile_instance_fingerprint": value.profile_instance_fingerprint,
        "retained_stage_inventory_digest": value.retained_stage_inventory_digest,
        "attempt_identity": value.attempt_identity,
        "cumulative_attempt_number": value.cumulative_attempt_number,
        "terminal_state": value.terminal_state,
        "authority_digest": value.authority_digest,
        "terminal_state_sha256": value.terminal_state_sha256,
        "terminal_seal_sha256": value.terminal_seal_sha256,
        "receipt_sha256": value.receipt_sha256,
        "paired_semantic_closure_fingerprint": value.paired_semantic_closure_fingerprint,
        "source_snapshot_identity": value.source_snapshot_identity,
        "blueprint_identity": value.blueprint_identity,
        "blueprint_fingerprint": value.blueprint_fingerprint,
        "validation_evidence_sha256": value.validation_evidence_sha256,
        "validator_identity": value.validator_identity,
        "validation_profile": value.validation_profile,
        "executed_layers": list(value.executed_layers),
    }


def _admission_from_document(text: str) -> GovernedCandidateAdmission:
    try:
        value = json.loads(text)
        fields = set(GovernedCandidateAdmission.__dataclass_fields__)
        if type(value) is not dict or set(value) != fields or _canonical(value).decode() != text:
            raise ValueError
        for name in ("profile_bytes", "candidate_semantic_bytes", "fingerprint_bytes", "inventory_bytes",
                     "authoring_receipt_bytes", "candidate_authority_bytes", "terminal_state_bytes", "terminal_seal_bytes",
                     "validation_evidence_bytes"):
            value[name] = bytes.fromhex(value[name])
        value["executed_layers"] = tuple(value["executed_layers"])
        return GovernedCandidateAdmission(**value)
    except Exception as exc:
        raise NativeGovernanceRejected("stored admission material is invalid") from exc


def _verify_bcrp_publication_subject(bundle: BCRPBundle,
        admission: GovernedCandidateAdmission) -> VerifiedBCRPPublicationSubject:
    """Authenticate and detach one exact three-record governed BCRP Candidate."""
    if type(bundle) is not BCRPBundle or type(admission) is not GovernedCandidateAdmission:
        raise NativeGovernanceRejected("exact BCRPBundle and GovernedCandidateAdmission types are required")
    try:
        candidate = bundle.one("CandidatePresentationPackageRecord")
    except ValueError as exc:
        raise NativeGovernanceRejected("Candidate closure cardinality is wrong") from exc
    if (bundle.profile_identity, bundle.profile_version) != (PROFILE_ID, PROFILE_VERSION):
        raise NativeGovernanceRejected("unsupported BCRP profile identity or version")
    if (type(bundle.records) is not tuple or len(bundle.records) != 3 or
            any(type(item) is not BCRPRecord for item in bundle.records) or
            any(len(bundle.records_of_kind(kind)) != 1 for kind in _CANDIDATE_KINDS) or
            any(item.kind not in _CANDIDATE_KINDS for item in bundle.records)):
        raise NativeGovernanceRejected("publication subject requires the exact three-record Candidate closure")
    if any(item.profile_version != PROFILE_VERSION for item in bundle.records):
        raise NativeGovernanceRejected("Candidate record profile version is unsupported")
    result = validate_bundle(bundle, through_layer="L2")
    if result.blocking:
        raise NativeGovernanceRejected("Candidate fails technical L0-L2 validation")
    profile = canonical_json_bytes(bundle, domain="profile-instance", require_valid=False)
    semantic = canonical_json_bytes(bundle, domain="candidate-semantic", require_valid=False)
    candidate_fp = fingerprint_bundle(bundle, domain="candidate-semantic", require_valid=False)
    profile_fp = fingerprint_bundle(bundle, domain="profile-instance", require_valid=False)
    if (admission.profile_bytes != profile or admission.candidate_semantic_bytes != semantic or
            admission.candidate_identity != candidate.identity or
            admission.candidate_semantic_fingerprint != candidate_fp.digest or
            admission.profile_instance_fingerprint != profile_fp.digest):
        raise NativeGovernanceRejected("Candidate bytes, identity, or recomputed fingerprints differ from admission")

    fp_doc = _json_exact(admission.fingerprint_bytes, "fingerprint evidence")
    if fp_doc != asdict(candidate_fp):
        raise NativeGovernanceRejected("historical fingerprint evidence differs from recomputed Candidate")
    inv = _json_exact(admission.inventory_bytes, "historical inventory")
    expected_files = {name: {"sha256": _sha(data), "size": len(data)} for name, data in (
        ("candidate-semantic.json", semantic), ("fingerprint.json", admission.fingerprint_bytes),
        ("profile.json", profile))}
    if inv != {"format": "briefforge-candidate-stage-inventory-v1", "files": expected_files}:
        raise NativeGovernanceRejected("historical three-file inventory closure differs")
    retained = compute_retained_stage_inventory_digest(profile_bytes=profile,
        candidate_semantic_bytes=semantic, fingerprint_bytes=admission.fingerprint_bytes,
        inventory_bytes=admission.inventory_bytes, authoring_receipt_bytes=admission.authoring_receipt_bytes)
    if admission.retained_stage_inventory_digest != retained:
        raise NativeGovernanceRejected("complete retained five-file inventory is stale")
    receipt = _json_exact(admission.authoring_receipt_bytes, "authoring receipt")
    expected_receipt_keys = {"format", "attempt_id", "authority_digest", "candidate_id",
                             "candidate_fingerprint", "authoring_input_sha256", "inventory_sha256", "governed"}
    if (set(receipt) != expected_receipt_keys or receipt.get("format") != "briefforge-candidate-authoring-receipt-v1" or
            receipt.get("attempt_id") != admission.attempt_identity or
            receipt.get("authority_digest") != admission.authority_digest or
            receipt.get("candidate_id") != candidate.identity or
            receipt.get("candidate_fingerprint") != candidate_fp.digest or
            receipt.get("inventory_sha256") != _sha(admission.inventory_bytes) or
            receipt.get("governed") is not True or admission.receipt_sha256 != _sha(admission.authoring_receipt_bytes)):
        raise NativeGovernanceRejected("authoring receipt closure is malformed, stale, or ungoverned")
    authority = _json_exact(admission.candidate_authority_bytes, "candidate authority")
    authority_keys = {"attempt_id", "authoring_input_sha256", "authority_decision_path",
        "authority_decision_sha256", "authority_path", "blueprint_fingerprint", "brief_id",
        "campaign_id", "candidate_id", "cumulative_attempt_number", "expected_semantic_closure_sha256",
        "format", "ledger_root", "material_ids", "output_root", "predecessor_attempt_digests",
        "predecessor_evidence_paths", "scope", "semantic_validation_profile", "source_snapshot",
        "task_id", "validator_identity"}
    if (set(authority) != authority_keys or authority.get("format") != "briefforge-candidate-authority-v1" or
            admission.candidate_authority_sha256 != _sha(admission.candidate_authority_bytes) or
            admission.authority_digest != admission.candidate_authority_sha256 or
            authority.get("authority_path") != admission.candidate_authority_locator or
            authority.get("attempt_id") != admission.attempt_identity or
            authority.get("cumulative_attempt_number") != admission.cumulative_attempt_number or
            authority.get("candidate_id") != candidate.identity or
            authority.get("authoring_input_sha256") != receipt.get("authoring_input_sha256") or
            authority.get("source_snapshot") != admission.source_snapshot_identity or
            authority.get("campaign_id") != admission.blueprint_identity or
            authority.get("blueprint_fingerprint") != admission.blueprint_fingerprint or
            authority.get("expected_semantic_closure_sha256") != admission.paired_semantic_closure_fingerprint or
            authority.get("validator_identity") != admission.validator_identity or
            authority.get("semantic_validation_profile") != admission.validation_profile or
            authority.get("scope") != "governed"):
        raise NativeGovernanceRejected("candidate authority bytes do not exactly bind the admitted attempt")
    if (not _ID.fullmatch(admission.attempt_identity) or type(admission.cumulative_attempt_number) is not int or
            admission.cumulative_attempt_number < 1 or admission.terminal_state != "VALIDATED_ACCEPTED" or
            not all(_DIGEST.fullmatch(item or "") for item in (admission.authority_digest,
                admission.paired_semantic_closure_fingerprint, admission.blueprint_fingerprint))):
        raise NativeGovernanceRejected("attempt, terminal acceptance, paired closure, or blueprint binding is invalid")
    terminal = _json_exact(admission.terminal_state_bytes, "terminal state")
    terminal_keys = {"authority_digest", "detail", "format", "prior_state_digest", "sequence", "state"}
    detail_keys = {"candidate_fingerprint", "stage_receipt_sha256", "validation_evidence_file",
                   "validation_evidence_sha256", "validator_identity"}
    if (admission.terminal_state_bytes != admission.terminal_seal_bytes or
            admission.terminal_state_sha256 != _sha(admission.terminal_state_bytes) or
            admission.terminal_seal_sha256 != _sha(admission.terminal_seal_bytes) or set(terminal) != terminal_keys or
            terminal.get("format") != "briefforge-candidate-attempt-state-v1" or terminal.get("sequence") != 4 or
            terminal.get("authority_digest") != admission.authority_digest or
            not _DIGEST.fullmatch(terminal.get("prior_state_digest", "")) or
            terminal.get("state") != "VALIDATED_ACCEPTED"):
        raise NativeGovernanceRejected("terminal state and paired seal closure differ")
    detail = terminal.get("detail")
    if type(detail) is not dict or set(detail) != detail_keys or detail.get("candidate_fingerprint") != candidate_fp.digest or \
            detail.get("stage_receipt_sha256") != admission.receipt_sha256 or \
            detail.get("validator_identity") != admission.validator_identity or \
            detail.get("validation_evidence_sha256") != admission.validation_evidence_sha256 or \
            detail.get("validation_evidence_file") != admission.validation_evidence_locator.rsplit("/", 1)[-1]:
        raise NativeGovernanceRejected("terminal state does not bind receipt, Candidate, and validation evidence")
    evidence = _json_exact(admission.validation_evidence_bytes, "validation evidence")
    evidence_keys = {"candidate_fingerprint", "executed_layers", "findings", "format", "passed",
                     "result_kind", "semantic_validation", "stage_receipt_sha256", "validator_identity"}
    if (set(evidence) != evidence_keys or evidence.get("format") != "briefforge-candidate-validation-evidence-v1" or
            evidence.get("result_kind") != "bcrp-plus-paired-semantic-validation-result" or
            evidence.get("findings") != [] or admission.validation_evidence_sha256 != _sha(admission.validation_evidence_bytes) or
            evidence.get("validator_identity") != admission.validator_identity or
            evidence.get("stage_receipt_sha256") != admission.receipt_sha256 or
            evidence.get("candidate_fingerprint") != candidate_fp.digest or evidence.get("passed") is not True or
            tuple(evidence.get("executed_layers", ())) != admission.executed_layers):
        raise NativeGovernanceRejected("technical validation evidence is stale or contradictory")
    semantic_evidence = evidence.get("semantic_validation")
    if (type(semantic_evidence) is not dict or set(semantic_evidence) != {"profile", "expected_closure_sha256", "observed_closure_sha256"} or
            semantic_evidence.get("profile") != admission.validation_profile or
            semantic_evidence.get("expected_closure_sha256") != admission.paired_semantic_closure_fingerprint or
            semantic_evidence.get("observed_closure_sha256") != admission.paired_semantic_closure_fingerprint):
        raise NativeGovernanceRejected("paired semantic validation closure differs")
    try:
        from briefforge_paired_terminal_profile.profile import (
            validate_candidate_paired_semantics, paired_semantic_closure_fingerprint)
        observed_paired = paired_semantic_closure_fingerprint(validate_candidate_paired_semantics(bundle))
    except Exception as exc:
        raise NativeGovernanceRejected("Candidate paired semantics failed public profile validation") from exc
    if observed_paired != admission.paired_semantic_closure_fingerprint:
        raise NativeGovernanceRejected("Candidate paired semantic extension differs from authority and evidence")
    if (admission.validator_identity != ACCEPTED_VALIDATOR_IDENTITY or
            admission.validation_profile != ACCEPTED_VALIDATION_PROFILE or
            admission.executed_layers != ACCEPTED_EXECUTED_LAYERS):
        raise NativeGovernanceRejected("unknown validator, validation profile, or executed-layer contract")
    if (not all(type(item) is str and item for item in (admission.candidate_authority_locator,
            admission.receipt_locator, admission.source_snapshot_identity, admission.blueprint_identity,
            admission.validation_evidence_locator, admission.validator_identity, admission.validation_profile)) or
            admission.receipt_locator.rsplit("/", 1)[-1] != "authoring-receipt.json" or
            type(admission.executed_layers) is not tuple or not admission.executed_layers):
        raise NativeGovernanceRejected("source, blueprint, locator, validator, or profile metadata is incomplete")
    from .candidate_authoring import GOVERNED_AUTHORITY_ROOT, GOVERNED_LEDGER_ROOT, GOVERNED_OUTPUT_ROOT
    expected_authority = (GOVERNED_AUTHORITY_ROOT / f"{admission.attempt_identity}.authority.json").absolute()
    expected_receipt = (GOVERNED_OUTPUT_ROOT / admission.attempt_identity / "authoring-receipt.json").absolute()
    expected_evidence = (GOVERNED_LEDGER_ROOT / admission.attempt_identity / "validation-evidence-04.json").absolute()
    if (Path(admission.candidate_authority_locator).absolute() != expected_authority or
            Path(admission.receipt_locator).absolute() != expected_receipt or
            Path(admission.validation_evidence_locator).absolute() != expected_evidence):
        raise NativeGovernanceRejected("governed Candidate admission requires exact canonical evidence locators")
    stage_root = expected_receipt.parent
    ledger_root = expected_evidence.parent
    expected_files = (
        (expected_authority, admission.candidate_authority_bytes, "Candidate authority"),
        (stage_root / "profile.json", admission.profile_bytes, "Candidate profile"),
        (stage_root / "candidate-semantic.json", admission.candidate_semantic_bytes, "Candidate semantics"),
        (stage_root / "fingerprint.json", admission.fingerprint_bytes, "Candidate fingerprint"),
        (stage_root / "inventory.json", admission.inventory_bytes, "Candidate inventory"),
        (expected_receipt, admission.authoring_receipt_bytes, "Candidate receipt"),
        (expected_evidence, admission.validation_evidence_bytes, "Candidate validation evidence"),
    )
    for path, admitted_bytes, label in expected_files:
        if _read_exact_regular(path, label) != admitted_bytes:
            raise NativeGovernanceRejected(f"{label} bytes differ from canonical governed evidence")
    _read_terminal_hardlink_pair(
        ledger_root / "04-VALIDATED_ACCEPTED.json", ledger_root / "terminal.seal.json",
        admission.terminal_state_bytes, admission.terminal_seal_bytes)
    document = _canonical(_admission_document(admission)).decode()
    closure = _sha(_canonical({"profile_sha256": _sha(profile),
                               "admission": _semantic_admission_binding(admission)}))
    return VerifiedBCRPPublicationSubject(bytes(profile), document, candidate.identity,
        candidate_fp.digest, profile_fp.digest, closure)


def verify_bcrp_publication_subject(bundle: BCRPBundle,
        admission: GovernedCandidateAdmission) -> VerifiedBCRPPublicationSubject:
    """Authenticate only a Candidate rooted at the canonical governed authoring locations."""
    return _verify_bcrp_publication_subject(bundle, admission)


# Descriptive factory alias.
create_bcrp_publication_subject = verify_bcrp_publication_subject


def _time(value: Any) -> str:
    try:
        return canonicalize_timestamp(value)
    except (TypeError, ValueError) as exc:
        raise NativeGovernanceRejected("exact canonicalizable governance time is required") from exc


def _identity(value: Any) -> None:
    if type(value) is not str or not _ID.fullmatch(value):
        raise NativeGovernanceRejected("exact canonical governance identity is required")


def _subject_again(subject: VerifiedBCRPPublicationSubject) -> VerifiedBCRPPublicationSubject:
    if type(subject) is not VerifiedBCRPPublicationSubject:
        raise NativeGovernanceRejected("exact verified publication subject is required")
    fresh = _verify_bcrp_publication_subject(subject.bundle, subject.admission)
    if fresh != subject:
        raise NativeGovernanceRejected("verified publication subject wrapper was forged or altered")
    return fresh


def _governance_extension(name: str, authority: str, targets: list[str], payload: dict[str, Any]) -> dict[str, Any]:
    return {"owner_namespace": _OWNER, "name": name, "version": _VERSION,
        "authority_ref": authority, "scope": name, "target_refs": targets,
        "criticality": "required", "character": "semantic",
        "validation_contract": GOVERNANCE_CONTRACT, "preservation": "must-preserve",
        "payload": payload}


def _judgment_payload(subject: VerifiedBCRPPublicationSubject, auth: JudgmentAuthorization) -> dict[str, Any]:
    return {"contract_version": _VERSION, "authorization": asdict(auth) | {
        "executed_layers": list(auth.executed_layers), "findings": list(auth.findings)},
        "subject": {"candidate_identity": subject.candidate_identity,
            "candidate_semantic_fingerprint": subject.candidate_semantic_fingerprint,
            "profile_instance_fingerprint": subject.profile_instance_fingerprint,
            "profile_sha256": _sha(subject.profile_bytes),
            "subject_closure_fingerprint": subject.closure_fingerprint,
            "admission_binding": _semantic_admission_binding(subject.admission)},
        "authority_basis": "policy-backed-system", "technical_validation_is_prerequisite_only": True,
        "excluded_authorities": ["candidate-authoring", "technical-validation", "ready-promotion",
                                 "publication-release", "renderer", "manifest"]}


def _issue_judgment_authorization_from_governance_adapter(*, subject: VerifiedBCRPPublicationSubject,
        evidence_path: Path) -> JudgmentAuthorizationToken:
    """Verify authority-owned evidence at the fixed governed Judgment filesystem boundary."""
    subject = _subject_again(subject)
    supplied_path = Path(evidence_path).absolute()
    if supplied_path.parent != _NATIVE_AUTHORITY_ROOT.absolute():
        raise NativeGovernanceRejected("Judgment authorization requires the canonical authority root")
    evidence_bytes = _read_exact_regular(supplied_path, "Judgment authority evidence")
    doc = _json_exact(evidence_bytes, "Judgment authorization evidence")
    if set(doc) != {"format", "authorization"} or doc.get("format") != "briefforge-native-judgment-authorization-v1":
        raise NativeGovernanceRejected("Judgment authorization evidence contract is unknown")
    raw = doc.get("authorization")
    if type(raw) is not dict or set(raw) != set(JudgmentAuthorization.__dataclass_fields__) or \
            type(raw.get("executed_layers")) is not list or type(raw.get("findings")) is not list:
        raise NativeGovernanceRejected("Judgment authorization evidence is malformed")
    raw = deepcopy(raw); raw["executed_layers"] = tuple(raw["executed_layers"]); raw["findings"] = tuple(raw["findings"])
    if supplied_path.name != f"{raw['identity']}.json":
        raise NativeGovernanceRejected("Judgment authorization filename does not bind its identity")
    _verify_judgment_authorization(JudgmentAuthorization(**raw), subject)
    return _issue_authorization_token(JudgmentAuthorizationToken, "judgment", evidence_bytes,
                                      subject.closure_fingerprint)


def produce_native_judgment(*, subject: VerifiedBCRPPublicationSubject,
        authorization: JudgmentAuthorizationToken) -> VerifiedNativeJudgment:
    subject = _subject_again(subject)
    target = subject.closure_fingerprint
    doc = _reserve_authorization_token(
        authorization, JudgmentAuthorizationToken, "judgment", target)
    try:
        raw = deepcopy(doc["authorization"])
        raw["executed_layers"] = tuple(raw["executed_layers"]); raw["findings"] = tuple(raw["findings"])
        auth = JudgmentAuthorization(**raw)
        _verify_judgment_authorization(auth, subject)
        record = BCRPRecord("ValidationJudgmentRecord", auth.decision_identity, PROFILE_VERSION,
            {"candidate_ref": subject.candidate_identity,
             "candidate_fingerprint": subject.candidate_semantic_fingerprint,
             "policy_id": auth.policy_identity, "executed_layers": list(auth.executed_layers),
             "findings": list(auth.findings), "valid": auth.disposition == "accepted",
             "validation_time": _time(auth.decision_time)},
            [_governance_extension("native-validation-judgment", auth.authority_identity,
                [auth.decision_identity, subject.candidate_identity], _judgment_payload(subject, auth))])
        bundle = subject.bundle
        bundle.records += (record,)
        result = verify_native_judgment(bundle, subject)
    except Exception:
        # Deterministic rejection produced no governed result; permit an exact retry.
        raise
    except BaseException:
        # Interruption makes completion indeterminate to the caller: fail closed against replay.
        _commit_authorization_token(
            authorization, JudgmentAuthorizationToken, "judgment", target)
        raise
    _commit_authorization_token(
        authorization, JudgmentAuthorizationToken, "judgment", target)
    return result


def _verify_judgment_authorization(auth: JudgmentAuthorization, subject: VerifiedBCRPPublicationSubject) -> None:
    for value in (auth.identity, auth.decision_identity): _identity(value)
    if (auth.policy_identity, auth.authority_identity, auth.authority_owner, auth.authority_role,
            auth.scope, auth.authority_basis) != (JUDGMENT_POLICY_ID, JUDGMENT_AUTHORITY_IDENTITY,
            JUDGMENT_AUTHORITY_OWNER, JUDGMENT_AUTHORITY_ROLE, JUDGMENT_SCOPE, "policy-backed-system"):
        raise NativeGovernanceRejected("Judgment policy, authority, role, scope, or trust boundary is not accepted")
    if (auth.disposition not in {"accepted", "deferred", "rejected"} or
            type(auth.rationale) is not str or not auth.rationale or
            type(auth.findings) is not tuple or type(auth.executed_layers) is not tuple or
            any(type(item) is not str or not item for item in auth.findings)):
        raise NativeGovernanceRejected("Judgment disposition, rationale, findings, and layers are malformed")
    admission = subject.admission
    if (auth.subject_closure_fingerprint, auth.candidate_identity, auth.candidate_semantic_fingerprint,
            auth.validation_evidence_sha256, auth.validation_profile, auth.executed_layers) != (
            subject.closure_fingerprint, subject.candidate_identity, subject.candidate_semantic_fingerprint,
            admission.validation_evidence_sha256, admission.validation_profile, admission.executed_layers):
        raise NativeGovernanceRejected("Judgment authorization targets another Candidate subject or evidence")
    if datetime.fromisoformat(_time(auth.authorization_time).replace("Z", "+00:00")) > datetime.fromisoformat(
            _time(auth.decision_time).replace("Z", "+00:00")):
        raise NativeGovernanceRejected("Judgment predates its authorization")


def _verified_extension(record: BCRPRecord, name: str, authority: str, targets: list[str]) -> dict[str, Any]:
    if len(record.extensions) != 1 or type(record.extensions[0]) is not dict or set(record.extensions[0]) != _EXT_KEYS:
        raise NativeGovernanceRejected("native governance extension envelope is incomplete or mixed")
    ext = record.extensions[0]
    expected = (_OWNER, name, _VERSION, authority, name, targets, "required", "semantic",
                GOVERNANCE_CONTRACT, "must-preserve")
    actual = tuple(ext.get(key) for key in ("owner_namespace", "name", "version", "authority_ref",
        "scope", "target_refs", "criticality", "character", "validation_contract", "preservation"))
    if actual != expected or type(ext.get("payload")) is not dict:
        raise NativeGovernanceRejected("unknown, mixed, optional, or mistargeted governance extension")
    return ext["payload"]


def verify_native_judgment(bundle: BCRPBundle,
        subject: VerifiedBCRPPublicationSubject) -> VerifiedNativeJudgment:
    subject = _subject_again(subject)
    expected_kinds = _CANDIDATE_KINDS + ("ValidationJudgmentRecord",)
    if (type(bundle) is not BCRPBundle or type(bundle.records) is not tuple or
            (bundle.profile_identity, bundle.profile_version) != (PROFILE_ID, PROFILE_VERSION) or
            len(bundle.records) != 4 or any(type(r) is not BCRPRecord for r in bundle.records) or
            any(r.profile_version != PROFILE_VERSION for r in bundle.records) or
            any(len(bundle.records_of_kind(kind)) != 1 for kind in expected_kinds) or
            any(r.kind not in expected_kinds for r in bundle.records)):
        raise NativeGovernanceRejected("native Judgment requires exact four-record closure")
    candidate_records = tuple(r for r in bundle.records if r.kind in _CANDIDATE_KINDS)
    if canonical_json_bytes(BCRPBundle(bundle.profile_identity, bundle.profile_version, candidate_records),
            domain="profile-instance", require_valid=False) != subject.profile_bytes:
        raise NativeGovernanceRejected("Judgment Candidate bytes differ from publication subject")
    judgment = bundle.one("ValidationJudgmentRecord")
    payload = _verified_extension(judgment, "native-validation-judgment", JUDGMENT_AUTHORITY_IDENTITY,
                                  [judgment.identity, subject.candidate_identity])
    if set(payload) != {"contract_version", "authorization", "subject", "authority_basis",
                       "technical_validation_is_prerequisite_only", "excluded_authorities"}:
        raise NativeGovernanceRejected("Judgment governance payload has undeclared or missing fields")
    raw = payload.get("authorization")
    if type(raw) is not dict or set(raw) != set(JudgmentAuthorization.__dataclass_fields__):
        raise NativeGovernanceRejected("persisted Judgment authorization is malformed")
    raw = deepcopy(raw); raw["executed_layers"] = tuple(raw["executed_layers"]); raw["findings"] = tuple(raw["findings"])
    auth = JudgmentAuthorization(**raw)
    _verify_judgment_authorization(auth, subject)
    if payload != _judgment_payload(subject, auth):
        raise NativeGovernanceRejected("Judgment subject closure or authority payload drifted")
    expected_semantic = {"candidate_ref": subject.candidate_identity,
        "candidate_fingerprint": subject.candidate_semantic_fingerprint, "policy_id": auth.policy_identity,
        "executed_layers": list(auth.executed_layers), "findings": list(auth.findings),
        "valid": auth.disposition == "accepted", "validation_time": _time(auth.decision_time)}
    if judgment.identity != auth.decision_identity or judgment.semantic != expected_semantic:
        raise NativeGovernanceRejected("Judgment core does not exactly represent its explicit disposition")
    detached = deepcopy(bundle)
    fp = fingerprint_bundle(detached, domain="profile-instance", require_valid=False)
    return VerifiedNativeJudgment(_bundle_text(detached), subject, fp, auth)


def _issue_ready_authorization_from_governance_adapter(*, judgment: VerifiedNativeJudgment,
        evidence_path: Path) -> ReadyAuthorizationToken:
    """Verify authority-owned evidence at the fixed governed readiness filesystem boundary."""
    if type(judgment) is not VerifiedNativeJudgment:
        raise NativeGovernanceRejected("exact verified native Judgment is required")
    verified = verify_native_judgment(judgment.bundle, judgment.subject)
    if not verified.accepted:
        raise NativeGovernanceRejected("only an accepted governance Judgment can authorize readiness")
    supplied_path = Path(evidence_path).absolute()
    if supplied_path.parent != _NATIVE_AUTHORITY_ROOT.absolute():
        raise NativeGovernanceRejected("Ready authorization requires the canonical authority root")
    evidence_bytes = _read_exact_regular(supplied_path, "Ready authority evidence")
    doc = _json_exact(evidence_bytes, "Ready authorization evidence")
    if set(doc) != {"format", "authorization"} or doc.get("format") != "briefforge-native-ready-authorization-v1":
        raise NativeGovernanceRejected("Ready authorization evidence contract is unknown")
    raw = doc.get("authorization")
    if type(raw) is not dict or set(raw) != set(ReadyAuthorization.__dataclass_fields__):
        raise NativeGovernanceRejected("Ready authorization evidence is malformed")
    if supplied_path.name != f"{raw['identity']}.json":
        raise NativeGovernanceRejected("Ready authorization filename does not bind its identity")
    _verify_ready_authorization(ReadyAuthorization(**raw), verified)
    return _issue_authorization_token(ReadyAuthorizationToken, "ready", evidence_bytes,
                                      verified.fingerprint.digest)


def produce_native_ready(*, judgment: VerifiedNativeJudgment,
        authorization: ReadyAuthorizationToken) -> VerifiedNativeReady:
    if type(judgment) is not VerifiedNativeJudgment:
        raise NativeGovernanceRejected("exact verified Judgment is required")
    verified = verify_native_judgment(judgment.bundle, judgment.subject)
    target = verified.fingerprint.digest
    doc = _reserve_authorization_token(
        authorization, ReadyAuthorizationToken, "ready", target)
    try:
        auth = ReadyAuthorization(**deepcopy(doc["authorization"]))
        _verify_ready_authorization(auth, verified)
        ready_fp = _sha(_canonical({"ready_identity": auth.ready_identity,
            "candidate_identity": verified.subject.candidate_identity,
            "subject_closure_fingerprint": verified.subject.closure_fingerprint,
            "judgment_identity": verified.judgment.identity, "judgment_fingerprint": verified.fingerprint.digest}))
        payload = {"contract_version": _VERSION, "authorization": asdict(auth),
            "candidate": {"identity": verified.subject.candidate_identity,
                          "fingerprint": verified.subject.candidate_semantic_fingerprint,
                          "subject_closure_fingerprint": verified.subject.closure_fingerprint,
                          "profile_instance_fingerprint": verified.subject.profile_instance_fingerprint},
            "judgment": {"identity": verified.judgment.identity, "fingerprint": verified.fingerprint.digest},
            "prerequisites": {"disposition": "accepted",
                "validation_evidence_sha256": verified.subject.admission.validation_evidence_sha256}}
        record = BCRPRecord("ReadyPresentationPackageRecord", auth.ready_identity, PROFILE_VERSION,
            {"candidate_ref": verified.subject.candidate_identity,
             "candidate_fingerprint": verified.subject.candidate_semantic_fingerprint,
             "judgment_ref": verified.judgment.identity, "readiness_time": _time(auth.readiness_time),
             "ready_fingerprint": ready_fp},
            [_governance_extension("native-ready-promotion", auth.authority_identity,
                [auth.ready_identity, verified.judgment.identity, verified.subject.candidate_identity], payload)])
        bundle = verified.bundle; bundle.records += (record,)
        result = verify_native_ready(bundle, verified)
    except Exception:
        raise
    except BaseException:
        _commit_authorization_token(
            authorization, ReadyAuthorizationToken, "ready", target)
        raise
    _commit_authorization_token(
        authorization, ReadyAuthorizationToken, "ready", target)
    return result


def _verify_ready_authorization(auth: ReadyAuthorization, judgment: VerifiedNativeJudgment) -> None:
    for value in (auth.identity, auth.ready_identity): _identity(value)
    if (auth.policy_identity, auth.authority_identity, auth.authority_owner, auth.authority_role,
            auth.scope, auth.authority_basis) != (READY_POLICY_ID, READY_AUTHORITY_IDENTITY,
            READY_AUTHORITY_OWNER, READY_AUTHORITY_ROLE, READY_SCOPE, "policy-backed-system"):
        raise NativeGovernanceRejected("Ready authority is not accepted")
    if (auth.candidate_identity, auth.subject_closure_fingerprint, auth.judgment_identity,
            auth.judgment_fingerprint) != (judgment.subject.candidate_identity,
            judgment.subject.closure_fingerprint, judgment.judgment.identity, judgment.fingerprint.digest):
        raise NativeGovernanceRejected("Ready authorization targets another Candidate or Judgment closure")
    decision_time = datetime.fromisoformat(
        _time(judgment.authorization.decision_time).replace("Z", "+00:00"))
    authorization_time = datetime.fromisoformat(
        _time(auth.authorization_time).replace("Z", "+00:00"))
    readiness_time = datetime.fromisoformat(
        _time(auth.readiness_time).replace("Z", "+00:00"))
    if decision_time > authorization_time or authorization_time > readiness_time:
        raise NativeGovernanceRejected("Ready chronology does not follow Judgment then authorization")


def verify_native_ready(bundle: BCRPBundle, judgment: VerifiedNativeJudgment) -> VerifiedNativeReady:
    if type(judgment) is not VerifiedNativeJudgment:
        raise NativeGovernanceRejected("exact verified native Judgment is required")
    verified_j = verify_native_judgment(judgment.bundle, judgment.subject)
    expected_kinds = _CANDIDATE_KINDS + ("ValidationJudgmentRecord", "ReadyPresentationPackageRecord")
    if (not verified_j.accepted or type(bundle) is not BCRPBundle or
            type(bundle.records) is not tuple or
            (bundle.profile_identity, bundle.profile_version) != (PROFILE_ID, PROFILE_VERSION) or
            len(bundle.records) != 5 or any(type(r) is not BCRPRecord for r in bundle.records) or
            any(r.profile_version != PROFILE_VERSION for r in bundle.records) or
            any(len(bundle.records_of_kind(kind)) != 1 for kind in expected_kinds) or
            any(r.kind not in expected_kinds for r in bundle.records)):
        raise NativeGovernanceRejected("native Ready requires one accepted exact five-record closure")
    judgment_records = tuple(r for r in bundle.records if r.kind != "ReadyPresentationPackageRecord")
    if _bundle_text(BCRPBundle(bundle.profile_identity, bundle.profile_version, judgment_records)) != _bundle_text(verified_j.bundle):
        raise NativeGovernanceRejected("Ready predecessor Judgment closure differs")
    ready = bundle.one("ReadyPresentationPackageRecord")
    payload = _verified_extension(ready, "native-ready-promotion", READY_AUTHORITY_IDENTITY,
        [ready.identity, verified_j.judgment.identity, verified_j.subject.candidate_identity])
    if set(payload) != {"contract_version", "authorization", "candidate", "judgment", "prerequisites"}:
        raise NativeGovernanceRejected("Ready governance payload is malformed")
    raw = payload.get("authorization")
    if type(raw) is not dict or set(raw) != set(ReadyAuthorization.__dataclass_fields__):
        raise NativeGovernanceRejected("persisted Ready authorization is malformed")
    auth = ReadyAuthorization(**raw); _verify_ready_authorization(auth, verified_j)
    expected_fp = _sha(_canonical({"ready_identity": auth.ready_identity,
        "candidate_identity": verified_j.subject.candidate_identity,
        "subject_closure_fingerprint": verified_j.subject.closure_fingerprint,
        "judgment_identity": verified_j.judgment.identity, "judgment_fingerprint": verified_j.fingerprint.digest}))
    expected_payload = {"contract_version": _VERSION, "authorization": asdict(auth),
        "candidate": {"identity": verified_j.subject.candidate_identity,
            "fingerprint": verified_j.subject.candidate_semantic_fingerprint,
            "subject_closure_fingerprint": verified_j.subject.closure_fingerprint,
            "profile_instance_fingerprint": verified_j.subject.profile_instance_fingerprint},
        "judgment": {"identity": verified_j.judgment.identity, "fingerprint": verified_j.fingerprint.digest},
        "prerequisites": {"disposition": "accepted",
            "validation_evidence_sha256": verified_j.subject.admission.validation_evidence_sha256}}
    expected_semantic = {"candidate_ref": verified_j.subject.candidate_identity,
        "candidate_fingerprint": verified_j.subject.candidate_semantic_fingerprint,
        "judgment_ref": verified_j.judgment.identity, "readiness_time": _time(auth.readiness_time),
        "ready_fingerprint": expected_fp}
    if payload != expected_payload or ready.identity != auth.ready_identity or ready.semantic != expected_semantic:
        raise NativeGovernanceRejected("Ready core or complete governed closure drifted")
    fp = fingerprint_bundle(bundle, domain="profile-instance", require_valid=False)
    return VerifiedNativeReady(_bundle_text(bundle), verified_j, fp, auth)


@dataclass(frozen=True)
class PersistedNativeReadyBinding:
    candidate_identity: str
    candidate_semantic_fingerprint: str
    profile_instance_fingerprint: str
    subject_closure_fingerprint: str
    judgment_identity: str
    judgment_fingerprint: str
    ready_identity: str
    ready_fingerprint: str
    core_ready_fingerprint: str
    readiness_time: str
    validation_evidence_sha256: str


def _reauthenticate_persisted_governed_subject(candidate_bundle: BCRPBundle,
        binding: dict[str, Any]) -> VerifiedBCRPPublicationSubject:
    """Recover a persisted subject only by rereading its canonical governed evidence."""
    from .candidate_authoring import GOVERNED_AUTHORITY_ROOT, GOVERNED_LEDGER_ROOT, GOVERNED_OUTPUT_ROOT
    attempt = binding.get("attempt_identity")
    if type(attempt) is not str or not _ID.fullmatch(attempt):
        raise NativeGovernanceRejected("persisted admission attempt identity is invalid")
    stage = (GOVERNED_OUTPUT_ROOT / attempt).absolute()
    ledger = (GOVERNED_LEDGER_ROOT / attempt).absolute()
    authority_path = (GOVERNED_AUTHORITY_ROOT / f"{attempt}.authority.json").absolute()
    profile = _read_exact_regular(stage / "profile.json", "persisted Candidate profile")
    semantic = _read_exact_regular(stage / "candidate-semantic.json", "persisted Candidate semantics")
    fingerprint = _read_exact_regular(stage / "fingerprint.json", "persisted Candidate fingerprint")
    inventory = _read_exact_regular(stage / "inventory.json", "persisted Candidate inventory")
    receipt = _read_exact_regular(stage / "authoring-receipt.json", "persisted Candidate receipt")
    authority = _read_exact_regular(authority_path, "persisted Candidate authority")
    evidence_path = ledger / "validation-evidence-04.json"
    evidence = _read_exact_regular(evidence_path, "persisted Candidate validation evidence")
    state_path = ledger / "04-VALIDATED_ACCEPTED.json"
    seal_path = ledger / "terminal.seal.json"
    state = _read_terminal_member(state_path, "persisted Candidate terminal state")
    seal = _read_terminal_member(seal_path, "persisted Candidate terminal seal")
    _read_terminal_hardlink_pair(state_path, seal_path, state, seal)
    admission = GovernedCandidateAdmission(
        profile, semantic, fingerprint, inventory, receipt, authority, str(authority_path),
        _sha(authority), binding["retained_stage_inventory_digest"], binding["candidate_identity"],
        binding["candidate_semantic_fingerprint"], binding["profile_instance_fingerprint"], attempt,
        binding["cumulative_attempt_number"], binding["terminal_state"], binding["authority_digest"],
        state, seal, binding["terminal_state_sha256"], binding["terminal_seal_sha256"],
        str(stage / "authoring-receipt.json"), binding["receipt_sha256"],
        binding["paired_semantic_closure_fingerprint"], binding["source_snapshot_identity"],
        binding["blueprint_identity"], binding["blueprint_fingerprint"], str(evidence_path), evidence,
        binding["validation_evidence_sha256"], binding["validator_identity"],
        binding["validation_profile"], tuple(binding["executed_layers"]))
    return verify_bcrp_publication_subject(candidate_bundle, admission)


def verify_persisted_native_ready_binding(bundle: BCRPBundle) -> PersistedNativeReadyBinding:
    """Verify native Candidate/Judgment/Ready semantic bindings without stage locators."""
    expected = _CANDIDATE_KINDS + ("ValidationJudgmentRecord", "ReadyPresentationPackageRecord")
    if (type(bundle) is not BCRPBundle or type(bundle.records) is not tuple or len(bundle.records) != 5 or
            (bundle.profile_identity, bundle.profile_version) != (PROFILE_ID, PROFILE_VERSION) or
            any(type(r) is not BCRPRecord or r.profile_version != PROFILE_VERSION for r in bundle.records) or
            any(len(bundle.records_of_kind(k)) != 1 for k in expected) or
            any(r.kind not in expected for r in bundle.records)):
        raise NativeGovernanceRejected("persisted native Ready requires exact five-record topology")
    candidates = tuple(r for r in bundle.records if r.kind in _CANDIDATE_KINDS)
    candidate_bundle = BCRPBundle(PROFILE_ID, PROFILE_VERSION, candidates)
    technical = validate_bundle(candidate_bundle, through_layer="L2")
    if technical.blocking:
        raise NativeGovernanceRejected("persisted native Candidate fails L0-L2 validation")
    candidate = candidate_bundle.one("CandidatePresentationPackageRecord")
    candidate_fp = fingerprint_bundle(candidate_bundle, domain="candidate-semantic", require_valid=False).digest
    profile_fp = fingerprint_bundle(candidate_bundle, domain="profile-instance", require_valid=False).digest
    judgment = bundle.one("ValidationJudgmentRecord")
    jp = _verified_extension(judgment, "native-validation-judgment", JUDGMENT_AUTHORITY_IDENTITY,
                             [judgment.identity, candidate.identity])
    if set(jp) != {"contract_version", "authorization", "subject", "authority_basis",
                   "technical_validation_is_prerequisite_only", "excluded_authorities"}:
        raise NativeGovernanceRejected("persisted Judgment payload is malformed")
    ja = deepcopy(jp.get("authorization"))
    if type(ja) is not dict or set(ja) != set(JudgmentAuthorization.__dataclass_fields__) or \
            type(ja.get("executed_layers")) is not list or type(ja.get("findings")) is not list:
        raise NativeGovernanceRejected("persisted Judgment authorization is malformed")
    if (jp.get("contract_version") != _VERSION or
            jp.get("authority_basis") != "policy-backed-system" or
            jp.get("technical_validation_is_prerequisite_only") is not True or
            jp.get("excluded_authorities") != ["candidate-authoring", "technical-validation",
                "ready-promotion", "publication-release", "renderer", "manifest"] or
            ja.get("validation_profile") != ACCEPTED_VALIDATION_PROFILE or
            tuple(ja.get("executed_layers", ())) != ACCEPTED_EXECUTED_LAYERS or
            not _DIGEST.fullmatch(ja.get("validation_evidence_sha256", "")) or
            ja.get("disposition") != "accepted" or type(ja.get("rationale")) is not str or
            not ja.get("rationale") or any(type(item) is not str or not item for item in ja.get("findings", []))):
        raise NativeGovernanceRejected("persisted Judgment governance contract is unknown or weakened")
    if datetime.fromisoformat(_time(ja["authorization_time"]).replace("Z", "+00:00")) > datetime.fromisoformat(
            _time(ja["decision_time"]).replace("Z", "+00:00")):
        raise NativeGovernanceRejected("persisted Judgment predates its authorization")
    subject = jp.get("subject")
    subject_keys = {"candidate_identity", "candidate_semantic_fingerprint", "profile_instance_fingerprint",
                    "profile_sha256", "subject_closure_fingerprint", "admission_binding"}
    admission_binding = subject.get("admission_binding") if type(subject) is dict else None
    profile_sha = _sha(canonical_json_bytes(candidate_bundle, domain="profile-instance", require_valid=False))
    expected_subject_closure = (_sha(_canonical({"profile_sha256": profile_sha,
        "admission": admission_binding})) if type(admission_binding) is dict else "")
    if (type(subject) is not dict or set(subject) != subject_keys or
            type(admission_binding) is not dict or
            set(admission_binding) != {"candidate_identity", "candidate_semantic_fingerprint",
                "profile_instance_fingerprint", "retained_stage_inventory_digest", "attempt_identity",
                "cumulative_attempt_number", "terminal_state", "authority_digest", "terminal_state_sha256",
                "terminal_seal_sha256", "receipt_sha256", "paired_semantic_closure_fingerprint",
                "source_snapshot_identity", "blueprint_identity", "blueprint_fingerprint",
                "validation_evidence_sha256", "validator_identity", "validation_profile", "executed_layers"} or
            admission_binding.get("validator_identity") != ACCEPTED_VALIDATOR_IDENTITY or
            admission_binding.get("validation_profile") != ACCEPTED_VALIDATION_PROFILE or
            tuple(admission_binding.get("executed_layers", ())) != ACCEPTED_EXECUTED_LAYERS or
            admission_binding.get("terminal_state") != "VALIDATED_ACCEPTED" or
            admission_binding.get("candidate_identity") != candidate.identity or
            admission_binding.get("candidate_semantic_fingerprint") != candidate_fp or
            admission_binding.get("profile_instance_fingerprint") != profile_fp or
            admission_binding.get("validation_evidence_sha256") != ja.get("validation_evidence_sha256") or
            subject.get("subject_closure_fingerprint") != expected_subject_closure or
            subject.get("candidate_identity") != candidate.identity or
            subject.get("candidate_semantic_fingerprint") != candidate_fp or
            subject.get("profile_instance_fingerprint") != profile_fp or
            subject.get("profile_sha256") != _sha(canonical_json_bytes(candidate_bundle, domain="profile-instance", require_valid=False)) or
            ja.get("subject_closure_fingerprint") != subject.get("subject_closure_fingerprint") or
            ja.get("candidate_identity") != candidate.identity or ja.get("candidate_semantic_fingerprint") != candidate_fp or
            ja.get("policy_identity") != JUDGMENT_POLICY_ID or ja.get("authority_identity") != JUDGMENT_AUTHORITY_IDENTITY or
            ja.get("authority_owner") != JUDGMENT_AUTHORITY_OWNER or ja.get("authority_role") != JUDGMENT_AUTHORITY_ROLE or
            ja.get("scope") != JUDGMENT_SCOPE or ja.get("authority_basis") != "policy-backed-system" or
            ja.get("disposition") != "accepted" or judgment.identity != ja.get("decision_identity")):
        raise NativeGovernanceRejected("persisted Judgment transitive Candidate binding differs")
    reauthenticated = _reauthenticate_persisted_governed_subject(candidate_bundle, admission_binding)
    if reauthenticated.closure_fingerprint != subject["subject_closure_fingerprint"]:
        raise NativeGovernanceRejected("persisted Judgment is not rooted in current canonical governed evidence")
    expected_js = {"candidate_ref": candidate.identity, "candidate_fingerprint": candidate_fp,
        "policy_id": JUDGMENT_POLICY_ID, "executed_layers": ja["executed_layers"], "findings": ja["findings"],
        "valid": True, "validation_time": _time(ja["decision_time"])}
    if judgment.semantic != expected_js or jp.get("authority_basis") != "policy-backed-system" or \
            jp.get("technical_validation_is_prerequisite_only") is not True:
        raise NativeGovernanceRejected("persisted Judgment core differs")
    judgment_bundle = BCRPBundle(PROFILE_ID, PROFILE_VERSION, bundle.records[:4])
    judgment_fp = fingerprint_bundle(judgment_bundle, domain="profile-instance", require_valid=False).digest
    ready = bundle.one("ReadyPresentationPackageRecord")
    rp = _verified_extension(ready, "native-ready-promotion", READY_AUTHORITY_IDENTITY,
        [ready.identity, judgment.identity, candidate.identity])
    if set(rp) != {"contract_version", "authorization", "candidate", "judgment", "prerequisites"}:
        raise NativeGovernanceRejected("persisted Ready payload is malformed")
    ra = rp.get("authorization")
    if type(ra) is not dict or set(ra) != set(ReadyAuthorization.__dataclass_fields__):
        raise NativeGovernanceRejected("persisted Ready authorization is malformed")
    if (rp.get("contract_version") != _VERSION or
            any(type(ra.get(name)) is not str or not _ID.fullmatch(ra[name])
                for name in ("identity", "ready_identity")) or
            datetime.fromisoformat(_time(ja["decision_time"]).replace("Z", "+00:00")) >
            datetime.fromisoformat(_time(ra["authorization_time"]).replace("Z", "+00:00")) or
            datetime.fromisoformat(_time(ra["authorization_time"]).replace("Z", "+00:00")) >
            datetime.fromisoformat(_time(ra["readiness_time"]).replace("Z", "+00:00"))):
        raise NativeGovernanceRejected("persisted Ready contract or chronology is invalid")
    ready_closure = _sha(_canonical({"ready_identity": ready.identity, "candidate_identity": candidate.identity,
        "subject_closure_fingerprint": subject["subject_closure_fingerprint"], "judgment_identity": judgment.identity,
        "judgment_fingerprint": judgment_fp}))
    expected_candidate = {"identity": candidate.identity, "fingerprint": candidate_fp,
        "subject_closure_fingerprint": subject["subject_closure_fingerprint"],
        "profile_instance_fingerprint": profile_fp}
    if (rp.get("candidate") != expected_candidate or rp.get("judgment") != {"identity": judgment.identity, "fingerprint": judgment_fp} or
            rp.get("prerequisites") != {"disposition": "accepted", "validation_evidence_sha256": ja["validation_evidence_sha256"]} or
            tuple(ra.get(k) for k in ("policy_identity", "authority_identity", "authority_owner", "authority_role", "scope", "authority_basis")) !=
            (READY_POLICY_ID, READY_AUTHORITY_IDENTITY, READY_AUTHORITY_OWNER, READY_AUTHORITY_ROLE, READY_SCOPE, "policy-backed-system") or
            tuple(ra.get(k) for k in ("candidate_identity", "subject_closure_fingerprint", "judgment_identity", "judgment_fingerprint", "ready_identity")) !=
            (candidate.identity, subject["subject_closure_fingerprint"], judgment.identity, judgment_fp, ready.identity) or
            ready.semantic != {"candidate_ref": candidate.identity, "candidate_fingerprint": candidate_fp,
                "judgment_ref": judgment.identity, "readiness_time": _time(ra["readiness_time"]),
                "ready_fingerprint": ready_closure}):
        raise NativeGovernanceRejected("persisted Ready transitive closure differs")
    ready_fp = fingerprint_bundle(bundle, domain="profile-instance", require_valid=False).digest
    return PersistedNativeReadyBinding(candidate.identity, candidate_fp, profile_fp,
        subject["subject_closure_fingerprint"], judgment.identity, judgment_fp, ready.identity,
        ready_fp, ready_closure, _time(ra["readiness_time"]),
        ja["validation_evidence_sha256"])


# Compatibility-friendly explicit names.
create_validation_judgment = produce_native_judgment
verify_validation_judgment = verify_native_judgment
promote_accepted_judgment = produce_native_ready
verify_ready_presentation_package = verify_native_ready


def _bundle_text(bundle: BCRPBundle) -> str:
    return _canonical({"profile_identity": bundle.profile_identity, "profile_version": bundle.profile_version,
                       "records": [record.to_document() for record in bundle.records]}).decode()


def _bundle_from_text(text: str) -> BCRPBundle:
    try:
        value = json.loads(text)
        if type(value) is not dict or set(value) != {"profile_identity", "profile_version", "records"} or \
                _canonical(value).decode() != text or type(value["records"]) is not list:
            raise ValueError
        return BCRPBundle(value["profile_identity"], value["profile_version"],
                          tuple(BCRPRecord.from_document(item) for item in value["records"]))
    except Exception as exc:
        raise NativeGovernanceRejected("stored native lifecycle closure is invalid") from exc
