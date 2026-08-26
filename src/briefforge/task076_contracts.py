"""Authenticated, checkout-owned generation-8 contract and Candidate inputs.

The frozen TASK-076 documents are data contracts, not executable authorities.  This
module is the sole production reader for them: callers cannot select another root
and every governed byte is authenticated before any document is returned.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import threading
from types import MappingProxyType
from typing import Any, Mapping
import weakref

from .bcrp.canonical import bundle_from_canonical_json, canonical_json_bytes, fingerprint_bundle
from .bcrp.model import BCRPBundle

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CONTRACT_ROOT = PROJECT_ROOT / "artifacts/contracts/task076"
_MANIFEST_PATH = _CONTRACT_ROOT / "final-contract-byte-manifest.json"
_CANDIDATE_PATH = PROJECT_ROOT / "artifacts/pilots/candidate-authoring-output/attempt:task071-representative-campaign-002/profile.json"
_MANIFEST_SHA256 = "b393b7fbdddbcb03792a01ba7ee25056e86a0f70a316b41c036de5314458d0a6"
_CANDIDATE_SHA256 = "62cbe5294b123c9b4043e9f721a1b2585c70a5380e2121a39e8558b5c73b1898"
_CANDIDATE_FINGERPRINT = "b1c29473241648c68dfb7bb737715645b396c149094eeb70cef34feb52fb95b2"
_MANIFEST_CONTRACT = "briefforge:task076-final-contract-byte-manifest:1.0.0"

class ContractAuthenticationError(ValueError):
    """A project-owned frozen contract or generation-8 source failed authentication."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def domain_digest(domain: str, value: Any, *, raw: bool = False) -> str:
    """Generation-8 SHA-256: ASCII domain, NUL, then canonical JSON or exact bytes."""
    if type(domain) is not str:
        raise TypeError("digest domain must be exact ASCII text")
    try:
        tag = domain.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError("digest domain must be ASCII") from exc
    body = value if raw else canonical_json(value)
    if type(body) is not bytes:
        raise TypeError("raw digest body must be exact bytes")
    return hashlib.sha256(tag + b"\0" + body).hexdigest()


def _read_regular(path: Path, label: str) -> bytes:
    try:
        if path.is_symlink() or not path.is_file():
            raise ContractAuthenticationError(f"{label} is not an exact regular file")
        return path.read_bytes()
    except OSError as exc:
        raise ContractAuthenticationError(f"cannot read {label}: {exc}") from exc


def _parse_exact(data: bytes, label: str) -> Any:
    try:
        text = data.decode("utf-8", "strict")
        return json.loads(text, object_pairs_hook=_unique_pairs,
                          parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)),
                          parse_float=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (UnicodeError, ValueError, json.JSONDecodeError, RecursionError) as exc:
        raise ContractAuthenticationError(f"{label} is not exact bounded JSON") from exc


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _freeze(value: Any) -> Any:
    if type(value) is dict:
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if type(value) is list:
        return tuple(_freeze(v) for v in value)
    return value


@dataclass(frozen=True)
class AuthenticatedContracts:
    manifest: Mapping[str, Any]
    documents: Mapping[str, Any]
    bytes_by_path: Mapping[str, bytes]

    def document(self, basename: str) -> Any:
        allowed = {"registry", "schema", "validation-rules"}
        entry = next(
            (item for item in self.manifest["entries"] if Path(item["path"]).name == basename),
            None,
        )
        if entry is None or entry["role"] not in allowed:
            raise ContractAuthenticationError(
                f"governed document {basename!r} is fixture/evidence, not production contract authority"
            )
        try:
            return self.documents[basename]
        except KeyError as exc:
            raise ContractAuthenticationError(f"unknown governed contract document {basename!r}") from exc


@dataclass(frozen=True, eq=False)
class AuthenticatedGeneration8Candidate:
    profile_bytes: bytes
    profile_document: Mapping[str, Any]
    bundle: BCRPBundle
    profile_byte_digest: str
    candidate_profile_instance_fingerprint: str
    candidate_identity: str


class Generation8CandidateAdmissionAuthority:
    """Opaque, process-local authority binding one exact Candidate byte string."""
    __slots__ = ("__weakref__",)
    def __new__(cls):
        raise TypeError("generation-8 Candidate authorities are issuer-only")
    def __copy__(self):
        raise TypeError("generation-8 Candidate authorities cannot be copied")
    def __deepcopy__(self, memo):
        raise TypeError("generation-8 Candidate authorities cannot be copied")
    def __reduce__(self):
        raise TypeError("generation-8 Candidate authorities cannot be serialized")
    def __reduce_ex__(self, protocol):
        raise TypeError("generation-8 Candidate authorities cannot be serialized")


_candidate_authorities: "weakref.WeakKeyDictionary[AuthenticatedGeneration8Candidate, Generation8CandidateAdmissionAuthority]" = weakref.WeakKeyDictionary()
_candidate_admission_authorities: "weakref.WeakKeyDictionary[Generation8CandidateAdmissionAuthority, tuple[bytes, str, str, str]]" = weakref.WeakKeyDictionary()
_candidate_authority_lock = threading.RLock()


def _register_candidate(candidate: AuthenticatedGeneration8Candidate,
                        authority: Generation8CandidateAdmissionAuthority) -> AuthenticatedGeneration8Candidate:
    with _candidate_authority_lock:
        _candidate_authorities[candidate] = authority
    return candidate


def _issue_candidate_admission_authority(profile_bytes: bytes, digest: str,
        fingerprint: str, identity: str) -> Generation8CandidateAdmissionAuthority:
    authority = object.__new__(Generation8CandidateAdmissionAuthority)
    with _candidate_authority_lock:
        _candidate_admission_authorities[authority] = (profile_bytes, digest, fingerprint, identity)
    return authority


def load_task076_contracts() -> AuthenticatedContracts:
    raw = _read_regular(_MANIFEST_PATH, "TASK-076 byte manifest")
    if hashlib.sha256(raw).hexdigest() != _MANIFEST_SHA256:
        raise ContractAuthenticationError("TASK-076 byte manifest identity differs")
    manifest = _parse_exact(raw, "TASK-076 byte manifest")
    if (type(manifest) is not dict or manifest.get("contract") != _MANIFEST_CONTRACT or
            manifest.get("task") != "TASK-076" or manifest.get("freeze_generation") != 8 or
            manifest.get("governed_entry_count") != 23 or type(manifest.get("entries")) is not list or
            len(manifest["entries"]) != 23 or
            hashlib.sha256(canonical_json(manifest["entries"])).hexdigest() != manifest.get("entries_digest_sha256")):
        raise ContractAuthenticationError("TASK-076 manifest closure differs")
    docs: dict[str, Any] = {}
    byte_map: dict[str, bytes] = {}
    seen: set[str] = set()
    required_entry_keys = {"path", "role", "profile", "length", "sha256"}
    for position, entry in enumerate(manifest["entries"]):
        if type(entry) is not dict or set(entry) != required_entry_keys:
            raise ContractAuthenticationError(f"manifest entry {position} has unknown shape")
        rel = entry["path"]
        if type(rel) is not str or rel in seen or rel.startswith("/") or ".." in Path(rel).parts:
            raise ContractAuthenticationError(f"manifest entry {position} has unsafe or duplicate path")
        seen.add(rel)
        path = (PROJECT_ROOT / rel).resolve()
        if not path.is_relative_to(PROJECT_ROOT.resolve()):
            raise ContractAuthenticationError("governed path escapes project root")
        data = _read_regular(path, f"governed entry {rel}")
        if len(data) != entry["length"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ContractAuthenticationError(f"governed entry authentication failed: {rel}")
        byte_map[rel] = data
        if rel.startswith("artifacts/contracts/task076/") and rel.endswith(".json"):
            name = Path(rel).name
            docs[name] = _freeze(_parse_exact(data, rel))
    expected_contract_inventory = {
        Path(item["path"]).name for item in manifest["entries"]
        if item["path"].startswith("artifacts/contracts/task076/")
    } | {_MANIFEST_PATH.name}
    try:
        children = tuple(_CONTRACT_ROOT.iterdir())
    except OSError as exc:
        raise ContractAuthenticationError("cannot authenticate TASK-076 contract inventory") from exc
    if (any(item.is_symlink() or not item.is_file() for item in children)
            or {item.name for item in children} != expected_contract_inventory):
        raise ContractAuthenticationError("TASK-076 contract directory inventory differs")
    return AuthenticatedContracts(_freeze(manifest), MappingProxyType(docs), MappingProxyType(byte_map))


def authenticate_generation8_candidate_bytes(profile_bytes: bytes, *,
        authority: Generation8CandidateAdmissionAuthority) -> AuthenticatedGeneration8Candidate:
    """Authenticate bytes only through an independently issued opaque authority."""
    if type(profile_bytes) is not bytes or type(authority) is not Generation8CandidateAdmissionAuthority:
        raise ContractAuthenticationError("exact Candidate bytes and opaque predecessor authority required")
    with _candidate_authority_lock:
        binding = _candidate_admission_authorities.get(authority)
    if binding is None or binding[0] != profile_bytes:
        raise ContractAuthenticationError("Candidate predecessor authority is absent or byte-substituted")
    (_, expected_profile_byte_digest, expected_candidate_profile_instance_fingerprint,
     expected_candidate_identity) = binding
    digest = hashlib.sha256(profile_bytes).hexdigest()
    if digest != expected_profile_byte_digest:
        raise ContractAuthenticationError("generation-8 Candidate profile byte digest differs")
    try:
        bundle = bundle_from_canonical_json(profile_bytes)
        reencoded = canonical_json_bytes(bundle, domain="profile-instance", require_valid=False)
        fingerprint = fingerprint_bundle(bundle, domain="candidate-semantic", require_valid=False).digest
        candidate_record = bundle.one("CandidatePresentationPackageRecord")
        extension = candidate_record.extensions
        family = tuple(extension[0].get(key) for key in (
            "owner_namespace", "name", "version", "validation_contract")) \
            if type(extension) is list and len(extension) == 1 and type(extension[0]) is dict else ()
    except Exception as exc:
        raise ContractAuthenticationError("generation-8 Candidate is not exact canonical BCRP") from exc
    if (reencoded != profile_bytes or fingerprint != expected_candidate_profile_instance_fingerprint
            or candidate_record.identity != expected_candidate_identity
            or family != ("briefforge-paired-terminal-profile", "paired-semantic-input",
                          "3.0.0", "bcrp:core-extension-envelope:1.0.0")):
        raise ContractAuthenticationError("generation-8 Candidate authority or profile/version differs")
    document = _parse_exact(profile_bytes, "generation-8 Candidate profile")
    issued = AuthenticatedGeneration8Candidate(
        profile_bytes, _freeze(document), bundle, digest, fingerprint, candidate_record.identity)
    return _register_candidate(issued, authority)


def load_generation8_candidate() -> AuthenticatedGeneration8Candidate:
    """Load the checkout-owned canonical TASK-071 generation-8 Candidate."""
    raw = _read_regular(_CANDIDATE_PATH, "generation-8 Candidate profile")
    authority = _issue_candidate_admission_authority(
        raw, _CANDIDATE_SHA256, _CANDIDATE_FINGERPRINT, "candidate:task071-cross-inquiry")
    return authenticate_generation8_candidate_bytes(raw, authority=authority)


def authenticate_generation8_candidate(candidate: object) -> AuthenticatedGeneration8Candidate:
    """Reauthenticate only a process-issued Candidate against its predecessor authority facts."""
    if type(candidate) is not AuthenticatedGeneration8Candidate:
        raise ContractAuthenticationError("authenticated generation-8 Candidate required")
    with _candidate_authority_lock:
        authority = _candidate_authorities.get(candidate)
    if authority is None:
        raise ContractAuthenticationError("generation-8 Candidate was not issued in this process")
    with _candidate_authority_lock:
        binding = _candidate_admission_authorities.get(authority)
    if binding is None:
        raise ContractAuthenticationError("generation-8 Candidate predecessor authority expired")
    _, digest, fingerprint, identity = binding
    rebound = authenticate_generation8_candidate_bytes(candidate.profile_bytes, authority=authority)
    if (candidate.profile_byte_digest != digest
            or candidate.candidate_profile_instance_fingerprint != fingerprint
            or candidate.candidate_identity != identity
            or canonical_json(_thaw_mapping(candidate.profile_document)) != candidate.profile_bytes
            or canonical_json_bytes(candidate.bundle, domain="profile-instance", require_valid=False)
               != candidate.profile_bytes):
        raise ContractAuthenticationError("generation-8 Candidate object fields differ from authenticated bytes")
    return rebound


def _generation8_candidate_authority(candidate: object) -> Generation8CandidateAdmissionAuthority:
    """Return the opaque lineage key only to production authority owners."""
    candidate = authenticate_generation8_candidate(candidate)
    with _candidate_authority_lock:
        authority = _candidate_authorities.get(candidate)
    if authority is None:
        raise ContractAuthenticationError("generation-8 Candidate lineage is unavailable")
    return authority


def _thaw_mapping(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {k: _thaw_mapping(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_thaw_mapping(v) for v in value]
    return value
