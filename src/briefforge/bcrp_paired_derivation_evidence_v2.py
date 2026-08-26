"""Generation-8 paired derivation-evidence-envelope v2 authority boundary."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from types import MappingProxyType
from typing import Any, Mapping

from briefforge.bcrp.registry import core_registry
from briefforge.bcrp_paired_semantic_interpretation_v2 import interpret_paired_candidate
from briefforge.task076_contracts import (
    AuthenticatedGeneration8Candidate, authenticate_generation8_candidate, canonical_json,
    domain_digest, load_generation8_candidate,
)

CONTRACT = "briefforge:paired-semantic-derivation-evidence:2.0.0"
ISSUER = "briefforge:paired-semantic-derivation-issuer:2.0.0"
VERIFIER = "briefforge:paired-semantic-derivation-verifier:2.0.0"
IMPLEMENTATION_CONTRACT = "briefforge:effective-semantic-graph-derivation:1.0.0"
_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_TIME = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
_INVARIANTS = (("exact-profile-dispatch", "pass"), ("complete-decode", "pass"),
 ("canonical-reencode-equality", "pass"), ("unique-paired-identities", "pass"),
 ("closed-edge-emission", "pass"), ("core-registry-resolution", "pass"),
 ("counterpart-bijection", "pass"), ("counterpart-nontraversability", "pass"),
 ("six-requirements", "pass"), ("all-owner-mappings", "pass"),
 ("mapping-count-equals-decoded-row-count", "pass"),
 ("effective-graph-derived-only", "pass"))
_EXCLUSIONS = (("Section", "order", "paired-owned;core-array-position-nonauthoritative"),)
_CLASSIFICATIONS = (("Provenance", "source_snapshot_identity",
 "owner-typed-token-not-core-reference-for-task071;emit-snapshot-edge-only-when-exact-EvidenceSnapshot-resolves"),)
_FIELDS = ("contract","evidence_identity","issuer_identity","verifier_identity","implementation_contract",
 "implementation_digest","registry_identity","registry_digest","bcrp_profile","paired_profile",
 "candidate_identity","candidate_profile_instance_fingerprint","candidate_profile_byte_digest",
 "source_locator_identity","extension_tuple","extension_envelope_digest","paired_payload_digest",
 "paired_closure_digest","decoded_paired_population_digest","decoded_paired_object_count",
 "core_graph_digest","paired_graph_digest","counterpart_proof_digest","effective_graph_digest",
 "requirement_inventory_digest","mapping_inventory_digest","mapping_count","decoded_row_count","counts",
 "counterpart_exclusions","graph_emission_classifications","invariant_results","findings","rejection_state",
 "operation_identity","authorization_fingerprint","issued_at_utc","fingerprint")

DERIVATION_ERROR_OWNER = "paired-derivation-evidence-v2"


class DerivationEvidenceError(ValueError):
    """Immutable structured rejection owned by derivation-evidence v2."""

    __slots__ = ("_message", "_code", "_owner", "_location", "_reason", "_sealed")
    _IMMUTABLE = frozenset({
        "args", "message", "code", "owner", "location", "reason",
        "__cause__", "__context__", "__suppress_context__",
        "_message", "_code", "_owner", "_location", "_reason", "_sealed",
    })

    def __init__(self, message: str, *, code: str, owner: str,
                 location: str, reason: str | None = None) -> None:
        object.__setattr__(self, "_message", message)
        super().__init__(message)
        object.__setattr__(self, "_code", code)
        object.__setattr__(self, "_owner", owner)
        object.__setattr__(self, "_location", location)
        object.__setattr__(self, "_reason", message if reason is None else reason)
        object.__setattr__(self, "_sealed", True)

    @property
    def args(self) -> tuple[str]:
        return (self._message,)

    @property
    def message(self) -> str:
        return self._message

    @property
    def code(self) -> str:
        return self._code

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def location(self) -> str:
        return self._location

    @property
    def reason(self) -> str:
        return self._reason

    @property
    def __cause__(self) -> None:
        return None

    @property
    def __context__(self) -> None:
        return None

    @property
    def __suppress_context__(self) -> bool:
        return True

    def __str__(self) -> str:
        return self._message

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._message!r})"

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_sealed", False) and name in self._IMMUTABLE:
            raise AttributeError(f"{name} is immutable")
        object.__setattr__(self, name, value)

    def __delattr__(self, name: str) -> None:
        if getattr(self, "_sealed", False) and name in self._IMMUTABLE:
            raise AttributeError(f"{name} is immutable")
        object.__delattr__(self, name)


def _error(message: str, *, code: str, location: str) -> DerivationEvidenceError:
    return DerivationEvidenceError(
        message, code=code, owner=DERIVATION_ERROR_OWNER,
        location=location, reason=message,
    )


@dataclass(frozen=True)
class DerivationEvidenceEnvelopeV2:
    _document: Mapping[str, Any]
    def to_document(self) -> dict[str, Any]: return _thaw(self._document)
    def __getitem__(self, key: str) -> Any: return self._document[key]
    def get(self, key: str, default=None) -> Any: return self._document.get(key, default)


@dataclass(frozen=True)
class PersistedDerivationEvidence:
    path: Path
    sha256: str
    length: int
    fingerprint: str


def _freeze(value: Any) -> Any:
    if type(value) is dict: return MappingProxyType({k:_freeze(v) for k,v in value.items()})
    if type(value) is list: return tuple(_freeze(x) for x in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping): return {k:_thaw(v) for k,v in value.items()}
    if isinstance(value, tuple): return [_thaw(x) for x in value]
    return value


def _implementation_digest() -> str:
    failure = None
    try:
        implementation_bytes = Path(__file__).read_bytes()
    except OSError:
        failure = _error(
            "derivation implementation bytes are unavailable",
            code="DERIVATION_RECONSTRUCTION_MISMATCH",
            location="/implementation_digest",
        )
    if failure is not None:
        raise failure
    return hashlib.sha256(implementation_bytes).hexdigest()


def _exact_time(value: str) -> str:
    if type(value) is not str or not _TIME.fullmatch(value):
        raise _error(
            "issued_at_utc requires canonical whole-second UTC",
            code="DERIVATION_INPUT_INVALID", location="/issued_at_utc",
        )
    failure = None
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        failure = _error(
            "issued_at_utc is not a real UTC instant",
            code="DERIVATION_INPUT_INVALID", location="/issued_at_utc",
        )
    if failure is not None:
        raise failure
    return value


def _identity(value: str, label: str) -> str:
    if type(value) is not str or not _ID.fullmatch(value):
        raise _error(
            f"invalid {label}", code="DERIVATION_INPUT_INVALID",
            location=f"/{label.replace(' ', '_')}",
        )
    return value


def construct_derivation_evidence_envelope_v2(*, evidence_identity: str,
        operation_identity: str, authorization_fingerprint: str, issued_at_utc: str,
        candidate: AuthenticatedGeneration8Candidate | None = None,
        source_locator_identity: str = "storage:task071-canonical-profile") -> DerivationEvidenceEnvelopeV2:
    candidate = authenticate_generation8_candidate(candidate or load_generation8_candidate())
    _identity(evidence_identity, "evidence identity"); _identity(operation_identity, "operation identity")
    _identity(source_locator_identity, "source locator identity"); _exact_time(issued_at_utc)
    if type(authorization_fingerprint) is not str or not _DIGEST.fullmatch(authorization_fingerprint):
        raise _error(
            "authorization fingerprint requires lowercase SHA-256",
            code="DERIVATION_INPUT_INVALID", location="/authorization_fingerprint",
        )
    interpretation = interpret_paired_candidate(candidate)
    registry = core_registry()
    candidate_record = candidate.bundle.one("CandidatePresentationPackageRecord")
    matches = [x for x in candidate_record.extensions if x.get("owner_namespace") == "briefforge-paired-terminal-profile"
               and x.get("name") == "paired-semantic-input" and x.get("version") == "3.0.0"]
    if len(matches) != 1:
        raise _error(
            "one exact paired-v3 extension required",
            code="DERIVATION_INPUT_INVALID",
            location="/candidate/extensions/paired-semantic-input",
        )
    extension = matches[0]; payload = extension["payload"]
    extension_tuple = [extension["owner_namespace"], extension["name"], extension["version"],
        extension["authority_ref"], extension["scope"], extension["target_refs"],
        extension["criticality"], extension["character"], extension["validation_contract"],
        extension["preservation"], payload["contract_identity"], payload["contract_version"]]
    sem = _thaw(interpretation.semantic_document)
    counts = {"core_nodes":len(interpretation.core_graph.nodes), "core_edges":len(interpretation.core_graph.edges),
        "paired_nodes":len(interpretation.paired_graph.nodes), "paired_edges":len(interpretation.paired_graph.edges),
        "counterparts":len(interpretation.counterparts), "sections":len(sem["sections"]),
        "statements":len(sem["statements"]), "tables":1, "rows":len(sem["table"]["rows"]),
        "values":len(sem["values"]), "qualifications":len(sem["qualifications"]),
        "provenance":len(sem["provenance"]), "obligations":len(sem["obligations"])}
    raw_payload = payload["canonical_semantics"].encode("utf-8")
    document = {"contract":CONTRACT, "evidence_identity":evidence_identity, "issuer_identity":ISSUER,
        "verifier_identity":VERIFIER, "implementation_contract":IMPLEMENTATION_CONTRACT,
        "implementation_digest":_implementation_digest(), "registry_identity":registry["registry_identity"],
        "registry_digest":registry["registry_digest"],
        "bcrp_profile":["briefforge-core-representation-profile","1.0.0"],
        "paired_profile":["briefforge:representative-paired-terminal-static-html-profile","3.0.0"],
        "candidate_identity":candidate.candidate_identity,
        "candidate_profile_instance_fingerprint":candidate.candidate_profile_instance_fingerprint,
        "candidate_profile_byte_digest":candidate.profile_byte_digest,
        "source_locator_identity":source_locator_identity, "extension_tuple":extension_tuple,
        "extension_envelope_digest":domain_digest("briefforge.task075.extension-envelope.v1", extension),
        "paired_payload_digest":domain_digest("briefforge.task075.paired-payload.v1", raw_payload, raw=True),
        "paired_closure_digest":domain_digest("briefforge.task075.paired-closure.v1", sem),
        "decoded_paired_population_digest":domain_digest("briefforge.task076.decoded-paired-population.v1",
                                                         [x.wire() for x in interpretation.inventory]),
        "decoded_paired_object_count":len(interpretation.inventory),
        "core_graph_digest":interpretation.core_graph.digest,
        "paired_graph_digest":interpretation.paired_graph.digest,
        "counterpart_proof_digest":interpretation.counterpart_proof_digest,
        "effective_graph_digest":interpretation.effective_graph.digest,
        "requirement_inventory_digest":interpretation.requirement_inventory_digest,
        "mapping_inventory_digest":interpretation.mapping_inventory_digest,
        "mapping_count":len(interpretation.mapping_inventory), "decoded_row_count":len(sem["table"]["rows"]),
        "counts":counts, "counterpart_exclusions":[list(x) for x in _EXCLUSIONS],
        "graph_emission_classifications":[list(x) for x in _CLASSIFICATIONS],
        "invariant_results":[list(x) for x in _INVARIANTS], "findings":[], "rejection_state":"none",
        "operation_identity":operation_identity, "authorization_fingerprint":authorization_fingerprint,
        "issued_at_utc":issued_at_utc}
    document["fingerprint"] = domain_digest("briefforge.task076.derivation-evidence.v2", document)
    return DerivationEvidenceEnvelopeV2(_freeze(document))


def serialize_derivation_evidence_envelope_v2(envelope: DerivationEvidenceEnvelopeV2) -> bytes:
    verified = verify_derivation_evidence_envelope_v2(envelope)
    return canonical_json(verified.to_document())


def _input_document(value: Any) -> tuple[dict[str, Any], bytes | None]:
    if type(value) is DerivationEvidenceEnvelopeV2: return value.to_document(), None
    if type(value) is bytes:
        if len(value) > 65536:
            raise _error(
                "evidence exceeds persistence bound",
                code="DERIVATION_ENVELOPE_INVALID", location="/envelope-bytes",
            )
        failure = None
        try:
            doc = json.loads(value.decode("utf-8"), object_pairs_hook=_unique_pairs)
        except Exception:
            failure = _error(
                "evidence is malformed JSON",
                code="DERIVATION_ENVELOPE_INVALID", location="/envelope-bytes",
            )
        if failure is not None:
            raise failure
        if canonical_json(doc) != value:
            raise _error(
                "evidence bytes are not canonical",
                code="DERIVATION_ENVELOPE_INVALID", location="/envelope-bytes",
            )
        return doc, value
    if type(value) is dict: return _thaw(value), None
    raise _error(
        "exact envelope object, document, or bytes required",
        code="DERIVATION_ENVELOPE_INVALID", location="/envelope",
    )


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out = {}
    for k,v in pairs:
        if k in out: raise ValueError("duplicate key")
        out[k]=v
    return out


def verify_derivation_evidence_envelope_v2(envelope: Any, *,
        candidate: AuthenticatedGeneration8Candidate | None = None,
        expected_evidence_identity: str | None = None, expected_operation_identity: str | None = None,
        expected_authorization_fingerprint: str | None = None,
        expected_source_locator_identity: str | None = None,
        expected_issued_at_utc: str | None = None) -> DerivationEvidenceEnvelopeV2:
    document, _ = _input_document(envelope)
    if type(document) is not dict or set(document) != set(_FIELDS):
        raise _error(
            "envelope requires exact closed fields",
            code="DERIVATION_ENVELOPE_INVALID", location="/envelope",
        )
    if document.get("contract") != CONTRACT or document.get("fingerprint") != domain_digest(
            "briefforge.task076.derivation-evidence.v2", {k:v for k,v in document.items() if k != "fingerprint"}):
        raise _error(
            "envelope contract or fingerprint differs",
            code="DERIVATION_ENVELOPE_AUTHENTICATION_FAILED",
            location="/fingerprint",
        )
    bindings = (("evidence_identity", expected_evidence_identity), ("operation_identity", expected_operation_identity),
                ("authorization_fingerprint", expected_authorization_fingerprint),
                ("source_locator_identity", expected_source_locator_identity), ("issued_at_utc", expected_issued_at_utc))
    for key, expected in bindings:
        if expected is not None and document.get(key) != expected:
            raise _error(
                f"envelope {key} differs from accepted authority",
                code="DERIVATION_AUTHORITY_BINDING_MISMATCH", location=f"/{key}",
            )
    candidate = candidate or load_generation8_candidate()
    expected = construct_derivation_evidence_envelope_v2(evidence_identity=document["evidence_identity"],
        operation_identity=document["operation_identity"], authorization_fingerprint=document["authorization_fingerprint"],
        issued_at_utc=document["issued_at_utc"], candidate=candidate,
        source_locator_identity=document["source_locator_identity"]).to_document()
    if document != expected:
        for key in _FIELDS:
            if document.get(key) != expected.get(key):
                raise _error(
                    f"independently reconstructed envelope differs at {key}",
                    code="DERIVATION_RECONSTRUCTION_MISMATCH", location=f"/{key}",
                )
        raise _error(
            "independently reconstructed envelope differs",
            code="DERIVATION_RECONSTRUCTION_MISMATCH", location="/envelope",
        )
    return DerivationEvidenceEnvelopeV2(_freeze(document))


def _open_directory(directory: Path) -> int:
    if not isinstance(directory, Path) or not directory.is_absolute():
        raise _error("persistence directory must be an existing absolute directory", code="DERIVATION_PERSISTENCE_REJECTED", location="/persistence-directory")
    failure = None
    try:
        expected = os.stat(directory, follow_symlinks=False)
        if directory.resolve(strict=True) != directory or not stat.S_ISDIR(expected.st_mode):
            raise _error("persistence directory is noncanonical or unsafe", code="DERIVATION_PERSISTENCE_REJECTED", location="/persistence-directory")
        descriptor = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
                             getattr(os, "O_NOFOLLOW", 0))
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (expected.st_dev, expected.st_ino):
            os.close(descriptor)
            raise _error("persistence directory changed while opening", code="DERIVATION_PERSISTENCE_REJECTED", location="/persistence-directory")
        return descriptor
    except DerivationEvidenceError:
        raise
    except (OSError, RuntimeError):
        failure = _error("persistence directory is unavailable or unsafe", code="DERIVATION_PERSISTENCE_REJECTED", location="/persistence-directory")
    if failure is not None:
        raise failure


def _safe_filename(filename: str) -> None:
    if (type(filename) is not str or not filename or filename in {".", ".."}
            or Path(filename).name != filename or Path(filename).is_absolute()
            or "\x00" in filename):
        raise _error("persistence filename must be one safe basename", code="DERIVATION_PERSISTENCE_REJECTED", location="/filename")


def _read_bound_file(directory_fd: int, filename: str) -> tuple[bytes, tuple[int, int]]:
    descriptor = -1
    failure = None
    try:
        try:
            descriptor = os.open(
                filename, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=directory_fd,
            )
            before = os.fstat(descriptor)
            if not stat.S_ISREG(before.st_mode) or before.st_size > 65536:
                raise _error("persisted evidence is not a bounded regular file", code="DERIVATION_RELOAD_MISMATCH", location=f"/{filename}")
            data = bytearray()
            while len(data) < before.st_size:
                chunk = os.read(descriptor, min(65536, before.st_size - len(data)))
                if not chunk:
                    raise _error("persisted evidence was truncated", code="DERIVATION_RELOAD_MISMATCH", location=f"/{filename}")
                data.extend(chunk)
            if os.read(descriptor, 1):
                raise _error("persisted evidence grew during reload", code="DERIVATION_RELOAD_MISMATCH", location=f"/{filename}")
            after = os.fstat(descriptor)
            if (before.st_dev, before.st_ino, before.st_size) != (after.st_dev, after.st_ino, after.st_size):
                raise _error("persisted evidence changed during reload", code="DERIVATION_RELOAD_MISMATCH", location=f"/{filename}")
            return bytes(data), (after.st_dev, after.st_ino)
        finally:
            if descriptor >= 0:
                os.close(descriptor)
    except DerivationEvidenceError:
        raise
    except OSError:
        failure = _error(
            "persisted evidence is unavailable or unsafe",
            code="DERIVATION_RELOAD_MISMATCH", location=f"/{filename}",
        )
    if failure is not None:
        raise failure


def persist_derivation_evidence_envelope_v2(envelope: Any, *, directory: Path,
                                             filename: str = "derivation-evidence-v2.json",
                                             candidate: AuthenticatedGeneration8Candidate | None = None) -> PersistedDerivationEvidence:
    verified = verify_derivation_evidence_envelope_v2(envelope, candidate=candidate)
    _safe_filename(filename)
    data = canonical_json(verified.to_document())
    if len(data) > 65536:
        raise _error("evidence exceeds persistence bound", code="DERIVATION_PERSISTENCE_REJECTED", location="/envelope-bytes")
    directory_fd = _open_directory(directory)
    descriptor = -1
    owned_identity: tuple[int, int] | None = None
    succeeded = False
    try:
        if os.listdir(directory_fd):
            raise _error("evidence directory must be empty", code="DERIVATION_PERSISTENCE_REJECTED", location="/persistence-directory")
        descriptor = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                             getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=directory_fd)
        created = os.fstat(descriptor)
        owned_identity = (created.st_dev, created.st_ino)
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short write")
            view = view[written:]
        os.fsync(descriptor)
        final = os.fstat(descriptor)
        if (not stat.S_ISREG(final.st_mode) or final.st_size != len(data)
                or (final.st_dev, final.st_ino) != owned_identity):
            raise _error("persisted evidence write is incomplete", code="DERIVATION_PERSISTENCE_REJECTED", location=f"/{filename}")
        os.close(descriptor)
        descriptor = -1
        os.fsync(directory_fd)
        if set(os.listdir(directory_fd)) != {filename}:
            raise _error("persisted evidence inventory differs", code="DERIVATION_RELOAD_MISMATCH", location="/persistence-directory")
        reloaded, identity = _read_bound_file(directory_fd, filename)
        if reloaded != data or identity != owned_identity:
            raise _error("persisted evidence reread differs", code="DERIVATION_RELOAD_MISMATCH", location=f"/{filename}")
        again, again_identity = _read_bound_file(directory_fd, filename)
        if again != reloaded or again_identity != identity:
            raise _error(
                "persisted evidence changed during immutable reload",
                code="DERIVATION_RELOAD_MISMATCH", location=f"/{filename}",
            )
        succeeded = True
        return PersistedDerivationEvidence(directory / filename, hashlib.sha256(data).hexdigest(),
                                           len(data), verified["fingerprint"])
    except FileExistsError as exc:
        raise _error("evidence persistence is exclusive-create", code="DERIVATION_PERSISTENCE_REJECTED", location=f"/{filename}") from exc
    except OSError as exc:
        raise _error(
            "cannot safely persist evidence",
            code="DERIVATION_PERSISTENCE_REJECTED", location=f"/{filename}",
        ) from exc
    finally:
        if descriptor >= 0:
            try:
                os.close(descriptor)
            except OSError as exc:
                raise _error(
                    "persisted evidence descriptor could not be closed",
                    code="DERIVATION_PERSISTENCE_REJECTED", location=f"/{filename}",
                ) from exc
        if not succeeded and owned_identity is not None:
            try:
                current = os.stat(filename, dir_fd=directory_fd, follow_symlinks=False)
                if (current.st_dev, current.st_ino) == owned_identity:
                    os.unlink(filename, dir_fd=directory_fd)
                    os.fsync(directory_fd)
            except FileNotFoundError:
                pass
            except OSError as exc:
                raise _error(
                    "failed to remove incomplete persisted evidence",
                    code="DERIVATION_PERSISTENCE_REJECTED", location=f"/{filename}",
                ) from exc
        try:
            os.close(directory_fd)
        except OSError as exc:
            raise _error(
                "persistence directory descriptor could not be closed",
                code="DERIVATION_PERSISTENCE_REJECTED", location="/persistence-directory",
            ) from exc


def reload_derivation_evidence_envelope_v2(path: Path, *,
        candidate: AuthenticatedGeneration8Candidate | None = None,
        expected_sha256: str | None = None, expected_fingerprint: str | None = None,
        expected_candidate_profile_byte_digest: str | None = None,
        expected_operation_identity: str | None = None,
        expected_authorization_fingerprint: str | None = None) -> DerivationEvidenceEnvelopeV2:
    if not isinstance(path, Path) or not path.is_absolute():
        raise _error("reload path must be absolute", code="DERIVATION_RELOAD_MISMATCH", location="/path")
    _safe_filename(path.name)
    directory_fd = _open_directory(path.parent)
    try:
        if set(os.listdir(directory_fd)) != {path.name}:
            raise _error("persisted evidence inventory differs", code="DERIVATION_RELOAD_MISMATCH", location="/persistence-directory")
        data, identity = _read_bound_file(directory_fd, path.name)
        sha = hashlib.sha256(data).hexdigest()
        if expected_sha256 is not None and sha != expected_sha256:
            raise _error("persisted byte inventory differs", code="DERIVATION_RELOAD_MISMATCH", location=f"/{path.name}")
        verified = verify_derivation_evidence_envelope_v2(data, candidate=candidate,
            expected_operation_identity=expected_operation_identity,
            expected_authorization_fingerprint=expected_authorization_fingerprint)
        if expected_fingerprint is not None and verified["fingerprint"] != expected_fingerprint:
            raise _error("persisted evidence fingerprint differs", code="DERIVATION_RELOAD_MISMATCH", location="/fingerprint")
        if (expected_candidate_profile_byte_digest is not None
                and verified["candidate_profile_byte_digest"] != expected_candidate_profile_byte_digest):
            raise _error("persisted evidence is stale or from another Candidate run", code="DERIVATION_RELOAD_MISMATCH", location="/candidate_profile_byte_digest")
        again, again_identity = _read_bound_file(directory_fd, path.name)
        if again != data or again_identity != identity:
            raise _error(
                "persisted evidence changed during immutable reload",
                code="DERIVATION_RELOAD_MISMATCH", location=f"/{path.name}",
            )
        if set(os.listdir(directory_fd)) != {path.name}:
            raise _error("persisted evidence inventory changed during reload", code="DERIVATION_RELOAD_MISMATCH", location="/persistence-directory")
        return verified
    except DerivationEvidenceError:
        raise
    except OSError as exc:
        raise _error(
            "persisted evidence reload is unavailable or unsafe",
            code="DERIVATION_RELOAD_MISMATCH", location=f"/{path.name}",
        ) from exc
    finally:
        try:
            os.close(directory_fd)
        except OSError as exc:
            raise _error(
                "persistence directory descriptor could not be closed",
                code="DERIVATION_RELOAD_MISMATCH", location="/persistence-directory",
            ) from exc

# Concise public aliases used by production callers.
construct_envelope = construct_derivation_evidence_envelope_v2
verify_envelope = verify_derivation_evidence_envelope_v2
serialize_envelope = serialize_derivation_evidence_envelope_v2
persist_envelope = persist_derivation_evidence_envelope_v2
reload_envelope = reload_derivation_evidence_envelope_v2
