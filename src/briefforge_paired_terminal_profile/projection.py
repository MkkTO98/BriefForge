"""Deterministic, lossless projector for exact paired terminal semantics."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from typing import Any

from .profile import (
    PairedProfileRejected, consume_paired_upstream_admission,
    admit_paired_terminal_semantics, paired_upstream_evidence_bindings,
    verify_paired_upstream_admission_token,
)
from .schema import (
    PROJECTION_IMPLEMENTATION,
    PROFILE_IDENTITY,
    PROFILE_VERSION,
    SCHEMA_IDENTITY,
    SCHEMA_VERSION,
    PairedAdmissionEnvelope,
    PairedEditorialProjection,
    PairedSchemaRejected,
    PairedSemanticInput,
    validate_paired_projection,
)


class PairedProjectionRejected(ValueError):
    """Projection construction, consumption, or deterministic binding failed."""


PROFILE_PROJECTION_EVIDENCE_IDENTITY = "briefforge:paired-terminal-profile-projection-evidence:1.0.0"
_MAX_EVIDENCE_BYTES = 2_000_000
_PROJECTION_SOURCE_FILES = ("projection.py", "schema.py", "profile.py")


@dataclass(frozen=True)
class PersistedPairedProfileProjectionEvidence:
    evidence_bytes: bytes
    evidence_path: Path
    fingerprint: str


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def paired_projection_implementation_digest() -> str:
    """Digest the exact projector source closure and interpreter identity."""
    directory = Path(__file__).resolve().parent
    measured = bytearray(b"paired-projector-closure-v1\0")
    for name in _PROJECTION_SOURCE_FILES:
        measured.extend(name.encode() + b"\0" + (directory / name).read_bytes() + b"\0")
    measured.extend(
        f"{sys.implementation.name}:{sys.implementation.cache_tag}:{sys.version_info[:3]}".encode()
    )
    return hashlib.sha256(bytes(measured)).hexdigest()


def compute_content_closure_fingerprint(semantics: PairedSemanticInput) -> str:
    """Bind canonical semantic input and its complete ordered mapping trace."""
    document = {
        "semantics": asdict(semantics),
        "mapping_trace": [list(item) for item in semantics.renderer_mappings],
    }
    return hashlib.sha256(_canonical(document)).hexdigest()


def _projection_document(projection: PairedEditorialProjection) -> dict[str, Any]:
    document = asdict(projection)
    document.pop("projection_fingerprint")
    return document


def compute_projection_fingerprint(projection: PairedEditorialProjection) -> str:
    """Bind every projection schema field except the digest's own value."""
    return hashlib.sha256(_canonical(_projection_document(projection))).hexdigest()


def build_paired_editorial_projection(
    *, admitted: object,
) -> PairedEditorialProjection:
    """Project only an issuer-held, independently verified Release closure."""
    try:
        semantics, admission = consume_paired_upstream_admission(admitted)
        values = dict(
            schema_identity=SCHEMA_IDENTITY,
            schema_version=SCHEMA_VERSION,
            profile_identity=PROFILE_IDENTITY,
            profile_version=PROFILE_VERSION,
            projection_implementation=PROJECTION_IMPLEMENTATION,
            release_identity=admission.release_identity,
            release_fingerprint=admission.release_fingerprint,
            lifecycle_scope_fingerprint=admission.lifecycle_scope_fingerprint,
            plan_identity=admission.plan_identity,
            plan_fingerprint=admission.plan_fingerprint,
            capability_declaration_identity=admission.capability_declaration_identity,
            capability_declaration_fingerprint=admission.capability_declaration_fingerprint,
            sections=semantics.sections,
            statements=semantics.statements,
            table=semantics.table,
            values=semantics.values,
            qualifications=semantics.qualifications,
            provenance=semantics.provenance,
            obligations=semantics.obligations,
            evidence_snapshots=semantics.evidence_snapshots,
            external_references=semantics.external_references,
            content_authorities=semantics.content_authorities,
            renderer_requirements=semantics.renderer_requirements,
            renderer_mappings=semantics.renderer_mappings,
            content_closure_fingerprint=compute_content_closure_fingerprint(semantics),
            projection_fingerprint="",
        )
        provisional = PairedEditorialProjection(**values)
        result = PairedEditorialProjection(
            **(values | {"projection_fingerprint": compute_projection_fingerprint(provisional)})
        )
        verify_paired_editorial_projection(result, admission=admission)
        return result
    except PairedProjectionRejected:
        raise
    except (PairedProfileRejected, PairedSchemaRejected, TypeError, ValueError) as exc:
        raise PairedProjectionRejected(str(exc)) from exc


def verify_paired_editorial_projection(
    projection: PairedEditorialProjection, *, admission: PairedAdmissionEnvelope
) -> None:
    """Independently reload-check schema, exact bindings, closure, and both digests."""
    try:
        validate_paired_projection(projection)
        if type(admission) is not PairedAdmissionEnvelope:
            raise PairedProjectionRejected("exact paired admission envelope required")
        bindings = (
            projection.profile_identity,
            projection.profile_version,
            projection.release_identity,
            projection.release_fingerprint,
            projection.lifecycle_scope_fingerprint,
            projection.plan_identity,
            projection.plan_fingerprint,
            projection.capability_declaration_identity,
            projection.capability_declaration_fingerprint,
        )
        if bindings != tuple(getattr(admission, name) for name in admission.__dataclass_fields__):
            raise PairedProjectionRejected("projection differs from its exact admission bindings")
        semantics = PairedSemanticInput(
            projection.sections,
            projection.statements,
            projection.table,
            projection.values,
            projection.qualifications,
            projection.provenance,
            projection.obligations,
            projection.evidence_snapshots,
            projection.external_references,
            projection.content_authorities,
            projection.renderer_requirements,
            projection.renderer_mappings,
        )
        admit_paired_terminal_semantics(semantics, admission=admission)
        if projection.content_closure_fingerprint != compute_content_closure_fingerprint(semantics):
            raise PairedProjectionRejected("content closure fingerprint is stale or forged")
        if projection.projection_fingerprint != compute_projection_fingerprint(projection):
            raise PairedProjectionRejected("projection fingerprint is stale or forged")
    except PairedProjectionRejected:
        raise
    except (PairedProfileRejected, PairedSchemaRejected, AttributeError, TypeError, ValueError) as exc:
        raise PairedProjectionRejected(str(exc)) from exc


def _profile_projection_evidence_document(projection, upstream_admission) -> dict[str, Any]:
    verify_paired_upstream_admission_token(upstream_admission, projection=projection)
    inventory, profile_fingerprint = paired_upstream_evidence_bindings(upstream_admission)
    binding_names = (
        "release_identity", "release_fingerprint", "lifecycle_scope_fingerprint",
        "plan_identity", "plan_fingerprint", "capability_declaration_identity",
        "capability_declaration_fingerprint", "profile_identity", "profile_version",
        "schema_identity", "schema_version", "projection_fingerprint")
    document = {
        "evidence_identity": PROFILE_PROJECTION_EVIDENCE_IDENTITY,
        "complete_projection": asdict(projection),
        "mapping_trace": [list(item) for item in projection.renderer_mappings],
        "semantic_source_closure_fingerprint": projection.content_closure_fingerprint,
        "projection_implementation_digest": paired_projection_implementation_digest(),
        "profile_admission_fingerprint": profile_fingerprint,
        "release_authority_inventory": list(inventory),
        "upstream_bindings": {name: getattr(projection, name) for name in binding_names},
        "findings": [
            {"code": "exact-terminal-authority-profile-admitted", "outcome": "pass"},
            {"code": "complete-lossless-projection-reproduced", "outcome": "pass"},
        ],
        "fingerprint": "",
    }
    unsigned = dict(document); unsigned.pop("fingerprint")
    document["fingerprint"] = hashlib.sha256(_canonical(unsigned)).hexdigest()
    return document


def _open_evidence_directory(value: Path) -> tuple[Path, int]:
    """Open one canonical directory descriptor and bind it to the checked inode."""
    if not isinstance(value, Path) or not value.is_absolute():
        raise PairedProjectionRejected("evidence directory requires an absolute Path")
    try:
        expected = os.stat(value, follow_symlinks=False)
        resolved = value.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PairedProjectionRejected("evidence directory does not pre-exist") from exc
    if resolved != value or not stat.S_ISDIR(expected.st_mode):
        raise PairedProjectionRejected("evidence directory is noncanonical or unsafe")
    descriptor = os.open(value, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
                         getattr(os, "O_NOFOLLOW", 0))
    opened = os.fstat(descriptor)
    if (opened.st_dev, opened.st_ino) != (expected.st_dev, expected.st_ino):
        os.close(descriptor)
        raise PairedProjectionRejected("evidence directory changed while opening")
    return value, descriptor


def _safe_filename(value: str) -> None:
    if (type(value) is not str or not value or value in {".", ".."}
            or Path(value).name != value or Path(value).is_absolute() or "\x00" in value):
        raise PairedProjectionRejected("evidence filename is unsafe")


def _read_persisted_evidence(directory: int, name: str) -> tuple[bytes, tuple[int, int]]:
    descriptor = os.open(name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > _MAX_EVIDENCE_BYTES:
            raise PairedProjectionRejected("projection evidence is not a bounded regular file")
        data = bytearray()
        while len(data) < before.st_size:
            chunk = os.read(descriptor, min(65536, before.st_size - len(data)))
            if not chunk:
                raise PairedProjectionRejected("projection evidence was truncated")
            data.extend(chunk)
        if os.read(descriptor, 1):
            raise PairedProjectionRejected("projection evidence grew during reload")
        after = os.fstat(descriptor)
        if (before.st_dev, before.st_ino, before.st_size) != (after.st_dev, after.st_ino, after.st_size):
            raise PairedProjectionRejected("projection evidence changed during reload")
        return bytes(data), (after.st_dev, after.st_ino)
    finally:
        os.close(descriptor)


def _unlink_owned(directory: int, name: str, identity: tuple[int, int] | None) -> None:
    if identity is None:
        return
    try:
        current = os.stat(name, dir_fd=directory, follow_symlinks=False)
        if (current.st_dev, current.st_ino) == identity:
            os.unlink(name, dir_fd=directory)
            os.fsync(directory)
    except FileNotFoundError:
        pass


def _verify_evidence_bytes(projection, upstream_admission, evidence, reloaded):
    expected = _profile_projection_evidence_document(projection, upstream_admission)
    try:
        document = json.loads(reloaded.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PairedProjectionRejected("persisted projection evidence is malformed") from exc
    if (reloaded != _canonical(expected)
            or document != json.loads(_canonical(expected))
            or document.get("complete_projection") != json.loads(_canonical(asdict(projection)))
            or evidence.evidence_bytes != reloaded
            or evidence.fingerprint != expected["fingerprint"]):
        raise PairedProjectionRejected(
            "persisted projection evidence does not independently reproduce")
    return evidence


def persist_paired_profile_projection_evidence(
    *, projection: PairedEditorialProjection, upstream_admission: object,
    evidence_directory: Path, evidence_filename: str,
) -> PersistedPairedProfileProjectionEvidence:
    """Persist through one inode-bound directory descriptor and immutable reload."""
    _safe_filename(evidence_filename)
    directory, directory_fd = _open_evidence_directory(evidence_directory)
    document = _profile_projection_evidence_document(projection, upstream_admission)
    expected = _canonical(document)
    if len(expected) > _MAX_EVIDENCE_BYTES:
        os.close(directory_fd)
        raise PairedProjectionRejected("projection evidence exceeds its bound")
    path = directory / evidence_filename
    descriptor = -1
    owned_identity = None
    try:
        if os.listdir(directory_fd):
            raise PairedProjectionRejected("evidence directory must be empty")
        descriptor = os.open(evidence_filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                             getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=directory_fd)
        created = os.fstat(descriptor)
        owned_identity = (created.st_dev, created.st_ino)
        view = memoryview(expected)
        while view:
            count = os.write(descriptor, view)
            if count <= 0:
                raise OSError("short write")
            view = view[count:]
        os.fsync(descriptor)
        final = os.fstat(descriptor)
        if (not stat.S_ISREG(final.st_mode) or final.st_size != len(expected)
                or (final.st_dev, final.st_ino) != owned_identity):
            raise PairedProjectionRejected("projection evidence write is incomplete")
        os.close(descriptor)
        descriptor = -1
        os.fsync(directory_fd)
        if set(os.listdir(directory_fd)) != {evidence_filename}:
            raise PairedProjectionRejected("projection evidence inventory differs")
        reloaded, identity = _read_persisted_evidence(directory_fd, evidence_filename)
        persisted = PersistedPairedProfileProjectionEvidence(
            reloaded, path, document["fingerprint"])
        _verify_evidence_bytes(projection, upstream_admission, persisted, reloaded)
        again, again_identity = _read_persisted_evidence(directory_fd, evidence_filename)
        if again != reloaded or again_identity != identity:
            raise PairedProjectionRejected("projection evidence changed during immutable reload")
        if set(os.listdir(directory_fd)) != {evidence_filename}:
            raise PairedProjectionRejected("projection evidence inventory changed during reload")
        return persisted
    except Exception:
        if descriptor >= 0:
            os.close(descriptor)
        _unlink_owned(directory_fd, evidence_filename, owned_identity)
        raise
    finally:
        os.close(directory_fd)


def verify_persisted_paired_profile_projection_evidence(
    *, projection: PairedEditorialProjection, upstream_admission: object,
    evidence: PersistedPairedProfileProjectionEvidence,
) -> PersistedPairedProfileProjectionEvidence:
    """Independently reload through one descriptor and reproduce exact evidence."""
    if type(evidence) is not PersistedPairedProfileProjectionEvidence:
        raise PairedProjectionRejected("exact persisted projection evidence required")
    path = evidence.evidence_path
    if not isinstance(path, Path) or not path.is_absolute():
        raise PairedProjectionRejected("persisted projection path must be absolute")
    _safe_filename(path.name)
    _, directory_fd = _open_evidence_directory(path.parent)
    try:
        if set(os.listdir(directory_fd)) != {path.name}:
            raise PairedProjectionRejected("projection evidence inventory differs")
        reloaded, identity = _read_persisted_evidence(directory_fd, path.name)
        result = _verify_evidence_bytes(projection, upstream_admission, evidence, reloaded)
        again, again_identity = _read_persisted_evidence(directory_fd, path.name)
        if again != reloaded or again_identity != identity:
            raise PairedProjectionRejected("projection evidence changed during immutable reload")
        if set(os.listdir(directory_fd)) != {path.name}:
            raise PairedProjectionRejected("projection evidence inventory changed during reload")
        return result
    finally:
        os.close(directory_fd)
