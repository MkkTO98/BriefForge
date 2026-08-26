"""One-act filesystem boundary for the fixed paired renderer."""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any

from .profile import PairedUpstreamAdmissionToken, verify_paired_upstream_admission_token
from .projection import (
    PersistedPairedProfileProjectionEvidence, compute_projection_fingerprint,
    verify_persisted_paired_profile_projection_evidence,
)
from .renderer import RENDERER_IDENTITY, RENDERER_VERSION, render_paired_html
from .schema import (
    PROFILE_IDENTITY,
    PROFILE_VERSION,
    SCHEMA_IDENTITY,
    SCHEMA_VERSION,
    PairedEditorialProjection,
    validate_paired_projection,
)

INVOCATION_POLICY_IDENTITY = "briefforge-paired-terminal-controlled-renderer-invocation-policy:1.0.0"
INVOCATION_EVIDENCE_IDENTITY = "briefforge:paired-terminal-controlled-renderer-invocation-evidence:1.0.0"
_FIXED_MEDIA_TYPE = "text/html"
_FIXED_MODE = "deterministic-replay"
_FIXED_ENVIRONMENT = (("LANG", "C"), ("LC_ALL", "C"), ("TZ", "UTC"),
                      ("PYTHONDONTWRITEBYTECODE", "1"), ("PYTHONHASHSEED", "0"),
                      ("PYTHONUTF8", "1"))
_DIGEST = re.compile(r"[0-9a-f]{64}")
_IDENTITY = re.compile(r"[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*")
_TIME = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")


class PairedRendererInvocationRejected(ValueError):
    """Authorization, deterministic execution, or persistence was rejected."""


@dataclass(frozen=True)
class PairedTerminalRendererInvocationAuthorization:
    identity: str
    policy_identity: str
    evidence_identity: str
    authorization_time: str
    release_identity: str
    release_fingerprint: str
    lifecycle_scope_fingerprint: str
    plan_identity: str
    plan_fingerprint: str
    capability_declaration_identity: str
    capability_declaration_fingerprint: str
    profile_identity: str
    profile_version: str
    schema_identity: str
    schema_version: str
    projection_fingerprint: str
    renderer_identity: str
    renderer_version: str
    renderer_implementation_digest: str
    output_directory: str
    output_filename: str
    evidence_directory: str
    evidence_filename: str
    authorization_ledger_directory: str
    output_count: int
    maximum_output_bytes: int
    media_type: str
    invocation_mode: str
    environment: tuple[tuple[str, str], ...]
    external_assets: tuple[str, ...]
    fingerprint: str


@dataclass(frozen=True)
class VerifiedPairedRendererInvocation:
    artifact_bytes: bytes
    evidence_bytes: bytes
    artifact_path: Path
    evidence_path: Path
    fingerprint: str


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def paired_renderer_implementation_digest() -> str:
    """Bind all local executable source used by the fixed renderer act."""
    directory = Path(__file__).resolve().parent
    measured = bytearray(b"paired-renderer-closure-v1\0")
    for name in ("controlled_invocation.py", "renderer.py", "schema.py",
                 "projection.py", "profile.py"):
        measured.extend(name.encode() + b"\0" + (directory / name).read_bytes() + b"\0")
    measured.extend(
        f"{sys.implementation.name}:{sys.implementation.cache_tag}:{sys.version_info[:3]}".encode()
    )
    return _sha256(bytes(measured))


def compute_paired_invocation_authorization_fingerprint(
    authorization: PairedTerminalRendererInvocationAuthorization,
) -> str:
    if type(authorization) is not PairedTerminalRendererInvocationAuthorization:
        raise TypeError("exact paired invocation authorization required")
    document = asdict(authorization)
    document.pop("fingerprint")
    return _sha256(_canonical(document))


def _canonical_time(value: object) -> bool:
    if type(value) is not str or _TIME.fullmatch(value) is None:
        return False
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return False
    return parsed.strftime("%Y-%m-%dT%H:%M:%SZ") == value


def _safe_basename(value: object) -> bool:
    if type(value) is not str or not value or value in {".", ".."} or "\x00" in value:
        return False
    path = Path(value)
    return not path.is_absolute() and path.name == value and len(path.parts) == 1


def _validate_field_types(a: PairedTerminalRendererInvocationAuthorization) -> None:
    integer_names = {"output_count", "maximum_output_bytes"}
    for item in fields(a):
        value = getattr(a, item.name)
        if item.name in integer_names:
            if type(value) is not int:
                raise PairedRendererInvocationRejected(f"{item.name} requires an exact integer")
        elif item.name == "environment":
            if type(value) is not tuple or any(
                type(pair) is not tuple or len(pair) != 2
                or any(type(part) is not str for part in pair) for pair in value
            ):
                raise PairedRendererInvocationRejected("environment requires exact immutable pairs")
        elif item.name == "external_assets":
            if type(value) is not tuple or any(type(member) is not str for member in value):
                raise PairedRendererInvocationRejected("external assets require an exact immutable tuple")
        elif type(value) is not str:
            raise PairedRendererInvocationRejected(f"{item.name} requires exact text")


def _validate_authorization(a: object, projection: PairedEditorialProjection) -> PairedTerminalRendererInvocationAuthorization:
    if type(a) is not PairedTerminalRendererInvocationAuthorization:
        raise PairedRendererInvocationRejected("exact paired invocation authorization required")
    _validate_field_types(a)
    expected = {
        "policy_identity": INVOCATION_POLICY_IDENTITY,
        "evidence_identity": INVOCATION_EVIDENCE_IDENTITY,
        "release_identity": projection.release_identity,
        "release_fingerprint": projection.release_fingerprint,
        "lifecycle_scope_fingerprint": projection.lifecycle_scope_fingerprint,
        "plan_identity": projection.plan_identity,
        "plan_fingerprint": projection.plan_fingerprint,
        "capability_declaration_identity": projection.capability_declaration_identity,
        "capability_declaration_fingerprint": projection.capability_declaration_fingerprint,
        "profile_identity": PROFILE_IDENTITY,
        "profile_version": PROFILE_VERSION,
        "schema_identity": SCHEMA_IDENTITY,
        "schema_version": SCHEMA_VERSION,
        "projection_fingerprint": projection.projection_fingerprint,
        "renderer_identity": RENDERER_IDENTITY,
        "renderer_version": RENDERER_VERSION,
        "renderer_implementation_digest": paired_renderer_implementation_digest(),
        "output_count": 1,
        "media_type": _FIXED_MEDIA_TYPE,
        "invocation_mode": _FIXED_MODE,
        "environment": _FIXED_ENVIRONMENT,
        "external_assets": (),
    }
    if any(getattr(a, name) != value for name, value in expected.items()):
        raise PairedRendererInvocationRejected("authorization does not bind the exact invocation tuple")
    if _IDENTITY.fullmatch(a.identity) is None or not _canonical_time(a.authorization_time):
        raise PairedRendererInvocationRejected("authorization identity or canonical time is invalid")
    digest_names = ("release_fingerprint", "lifecycle_scope_fingerprint", "plan_fingerprint",
                    "capability_declaration_fingerprint", "projection_fingerprint",
                    "renderer_implementation_digest", "fingerprint")
    if any(_DIGEST.fullmatch(getattr(a, name)) is None for name in digest_names):
        raise PairedRendererInvocationRejected("authorization contains a malformed digest")
    if a.fingerprint != compute_paired_invocation_authorization_fingerprint(a):
        raise PairedRendererInvocationRejected("authorization fingerprint is stale")
    if not 1 <= a.maximum_output_bytes <= 1_000_000:
        raise PairedRendererInvocationRejected("maximum output byte bound is invalid")
    if not _safe_basename(a.output_filename) or not _safe_basename(a.evidence_filename):
        raise PairedRendererInvocationRejected("authorized filename is unsafe")
    return a


def _safe_directory(value: str) -> tuple[Path, tuple[int, int]]:
    path = Path(value)
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PairedRendererInvocationRejected("authorized directory does not pre-exist") from exc
    if not path.is_absolute() or str(resolved) != value:
        raise PairedRendererInvocationRejected("authorized directory is not canonical and safe")
    try:
        admitted = os.stat(path, follow_symlinks=False)
    except OSError as exc:
        raise PairedRendererInvocationRejected("authorized directory is not canonical and safe") from exc
    if not stat.S_ISDIR(admitted.st_mode):
        raise PairedRendererInvocationRejected("authorized directory is not canonical and safe")
    return path, (admitted.st_dev, admitted.st_ino)


def _open_directory(path: Path) -> int:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
                         getattr(os, "O_NOFOLLOW", 0))
    if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise PairedRendererInvocationRejected("authorized path is not a directory")
    return descriptor


def _open_admitted_directory(path: Path, admitted: tuple[int, int]) -> int:
    descriptor = _open_directory(path)
    opened = os.fstat(descriptor)
    if (opened.st_dev, opened.st_ino) != admitted:
        os.close(descriptor)
        raise PairedRendererInvocationRejected("authorized directory changed while opening")
    return descriptor


def _verify_directory_path_identity(path: Path, admitted: tuple[int, int]) -> None:
    """Require the authorized pathname still to name the admitted directory."""
    try:
        current = os.stat(path, follow_symlinks=False)
    except OSError as exc:
        raise PairedRendererInvocationRejected(
            "authorized directory pathname changed during invocation") from exc
    if (not stat.S_ISDIR(current.st_mode)
            or (current.st_dev, current.st_ino) != admitted):
        raise PairedRendererInvocationRejected(
            "authorized directory pathname changed during invocation")


def _write_exclusive_at(directory: int, name: str, data: bytes,
                        created: list[tuple[int, int] | None]) -> None:
    descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                         getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=directory)
    try:
        identity = os.fstat(descriptor)
        created[0] = (identity.st_dev, identity.st_ino)
        view = memoryview(data)
        while view:
            count = os.write(descriptor, view)
            if count <= 0:
                raise OSError("short write")
            view = view[count:]
        os.fsync(descriptor)
        final = os.fstat(descriptor)
        if not stat.S_ISREG(final.st_mode) or final.st_size != len(data):
            raise PairedRendererInvocationRejected("persisted write is incomplete")
        os.fsync(directory)
    finally:
        os.close(descriptor)


def _write_evidence_exclusive_at(
    directory: int, name: str, build: Any,
    created: list[tuple[int, int] | None],
) -> bytes:
    descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                         getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=directory)
    try:
        opened = os.fstat(descriptor)
        identity = (opened.st_dev, opened.st_ino)
        created[0] = identity
        data = build(identity)
        view = memoryview(data)
        while view:
            count = os.write(descriptor, view)
            if count <= 0:
                raise OSError("short write")
            view = view[count:]
        os.fsync(descriptor)
        final = os.fstat(descriptor)
        if not stat.S_ISREG(final.st_mode) or final.st_size != len(data):
            raise PairedRendererInvocationRejected("persisted write is incomplete")
        os.fsync(directory)
        return data
    finally:
        os.close(descriptor)


def _filesystem_binding(
    directories: dict[str, tuple[int, int]], artifact_identity: tuple[int, int],
    evidence_identity: tuple[int, int], marker_name: str, marker: bytes,
) -> dict[str, Any]:
    return {
        "directory_identities": {
            key: _identity_document(value) for key, value in sorted(directories.items())
        },
        "file_identities": {
            "artifact": _identity_document(artifact_identity),
            "evidence": _identity_document(evidence_identity),
        },
        "authorization_marker": {
            "filename": marker_name, "byte_length": len(marker), "sha256": _sha256(marker),
        },
    }


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


def _read_regular_at_with_identity(directory: int, name: str,
                                   maximum: int) -> tuple[bytes, tuple[int, int]]:
    descriptor = os.open(name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise PairedRendererInvocationRejected("persisted file is not a bounded regular file")
        result = bytearray()
        while len(result) < before.st_size:
            chunk = os.read(descriptor, min(65536, before.st_size - len(result)))
            if not chunk:
                raise PairedRendererInvocationRejected("persisted file was truncated")
            result.extend(chunk)
        after = os.fstat(descriptor)
        if (before.st_dev, before.st_ino, before.st_size) != (after.st_dev, after.st_ino, after.st_size):
            raise PairedRendererInvocationRejected("persisted file changed during reload")
        return bytes(result), (after.st_dev, after.st_ino)
    finally:
        os.close(descriptor)


def _read_regular_at(directory: int, name: str, maximum: int) -> bytes:
    return _read_regular_at_with_identity(directory, name, maximum)[0]


def _identity_document(identity: tuple[int, int]) -> list[int]:
    return [identity[0], identity[1]]


def _consumption_marker(a: PairedTerminalRendererInvocationAuthorization,
                        identities: dict[str, tuple[int, int]]) -> tuple[str, bytes]:
    name = f"{a.fingerprint}.consumed"
    document = {
        "authorization_fingerprint": a.fingerprint,
        "directory_identities": {
            key: _identity_document(value) for key, value in sorted(identities.items())
        },
        "marker_identity": "briefforge:paired-terminal-one-act-consumption:1.0.0",
    }
    return name, _canonical(document)


def _evidence_document(projection: PairedEditorialProjection,
                       a: PairedTerminalRendererInvocationAuthorization,
                       artifact: bytes,
                       filesystem_binding: dict[str, Any]) -> dict[str, Any]:
    digest = _sha256(artifact)
    document: dict[str, Any] = {
        "evidence_identity": INVOCATION_EVIDENCE_IDENTITY,
        "authorization": asdict(a),
        "projection_binding": {
            "release_identity": projection.release_identity,
            "release_fingerprint": projection.release_fingerprint,
            "lifecycle_scope_fingerprint": projection.lifecycle_scope_fingerprint,
            "plan_identity": projection.plan_identity,
            "plan_fingerprint": projection.plan_fingerprint,
            "capability_declaration_identity": projection.capability_declaration_identity,
            "capability_declaration_fingerprint": projection.capability_declaration_fingerprint,
            "profile_identity": projection.profile_identity,
            "profile_version": projection.profile_version,
            "schema_identity": projection.schema_identity,
            "schema_version": projection.schema_version,
            "content_closure_fingerprint": projection.content_closure_fingerprint,
            "projection_fingerprint": projection.projection_fingerprint,
        },
        "renderer_identity": RENDERER_IDENTITY,
        "renderer_version": RENDERER_VERSION,
        "renderer_implementation_digest": a.renderer_implementation_digest,
        "filesystem_binding": filesystem_binding,
        "execution_sha256": [digest, digest],
        "artifact": {"filename": a.output_filename, "media_type": a.media_type,
                     "byte_length": len(artifact), "sha256": digest},
        "outcome": "completed-deterministically",
        "fingerprint": "",
    }
    fingerprint_input = dict(document)
    fingerprint_input.pop("fingerprint")
    document["fingerprint"] = _sha256(_canonical(fingerprint_input))
    return document


def _verify_bytes(projection: PairedEditorialProjection,
                  a: PairedTerminalRendererInvocationAuthorization,
                  artifact: bytes, evidence: bytes, *, verify_renderer: bool,
                  filesystem_binding: dict[str, Any]) -> str:
    if len(artifact) > a.maximum_output_bytes:
        raise PairedRendererInvocationRejected("artifact exceeds its authorized bound")
    try:
        document = json.loads(evidence.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PairedRendererInvocationRejected("invocation evidence is malformed") from exc
    expected = _evidence_document(projection, a, artifact, filesystem_binding)
    canonical_expected = _canonical(expected)
    normalized_expected = json.loads(canonical_expected.decode("utf-8"))
    if type(document) is not dict or document != normalized_expected or evidence != canonical_expected:
        raise PairedRendererInvocationRejected("invocation evidence is noncanonical or differs")
    if verify_renderer and artifact != render_paired_html(projection):
        raise PairedRendererInvocationRejected("persisted artifact differs from the fixed renderer")
    return expected["fingerprint"]


def invoke_controlled_paired_renderer(*, projection: PairedEditorialProjection,
                                      authorization: PairedTerminalRendererInvocationAuthorization,
                                      upstream_admission: PairedUpstreamAdmissionToken,
                                      projection_evidence: PersistedPairedProfileProjectionEvidence,
                                      ) -> VerifiedPairedRendererInvocation:
    output_fd = evidence_fd = ledger_fd = -1
    artifact_owned: list[tuple[int, int] | None] = [None]
    evidence_owned: list[tuple[int, int] | None] = [None]
    marker_owned: list[tuple[int, int] | None] = [None]
    artifact_name = evidence_name = ""
    try:
        validate_paired_projection(projection)
        if projection.projection_fingerprint != compute_projection_fingerprint(projection):
            raise PairedRendererInvocationRejected("projection fingerprint is stale")
        verify_paired_upstream_admission_token(upstream_admission, projection=projection)
        verify_persisted_paired_profile_projection_evidence(
            projection=projection, upstream_admission=upstream_admission,
            evidence=projection_evidence)
        a = _validate_authorization(authorization, projection)
        output_directory, output_admitted = _safe_directory(a.output_directory)
        evidence_directory, evidence_admitted = _safe_directory(a.evidence_directory)
        ledger_directory, ledger_admitted = _safe_directory(a.authorization_ledger_directory)
        output_fd = _open_admitted_directory(output_directory, output_admitted)
        evidence_fd = _open_admitted_directory(evidence_directory, evidence_admitted)
        ledger_fd = _open_admitted_directory(ledger_directory, ledger_admitted)
        directories = {"output": output_admitted, "evidence": evidence_admitted,
                       "authorization_ledger": ledger_admitted}
        if len(set(directories.values())) != 3:
            raise PairedRendererInvocationRejected("authorized directories must be pairwise distinct")
        if os.listdir(output_fd) or os.listdir(evidence_fd) or os.listdir(ledger_fd):
            raise PairedRendererInvocationRejected("authorized destination directory is nonempty")
        marker_name, marker = _consumption_marker(a, directories)
        # This is the one-act boundary.  The marker is intentionally never cleaned up.
        _write_exclusive_at(ledger_fd, marker_name, marker, marker_owned)
        artifact_name, evidence_name = a.output_filename, a.evidence_filename
        try:
            first = render_paired_html(projection)
            second = render_paired_html(projection)
        except Exception as exc:
            raise PairedRendererInvocationRejected("fixed renderer execution failed") from exc
        if type(first) is not bytes or type(second) is not bytes or first != second:
            raise PairedRendererInvocationRejected("independent renderer calls are nondeterministic")
        if len(first) > a.maximum_output_bytes:
            raise PairedRendererInvocationRejected("authorized output byte bound exceeded")
        if os.listdir(output_fd) or os.listdir(evidence_fd):
            raise PairedRendererInvocationRejected("renderer produced undeclared auxiliary output")
        _write_exclusive_at(output_fd, artifact_name, first, artifact_owned)
        assert artifact_owned[0] is not None
        binding_holder: dict[str, Any] = {}
        def build_evidence(evidence_identity: tuple[int, int]) -> bytes:
            binding = _filesystem_binding(directories, artifact_owned[0], evidence_identity,
                                          marker_name, marker)
            binding_holder.update(binding)
            return _canonical(_evidence_document(projection, a, first, binding))
        _write_evidence_exclusive_at(evidence_fd, evidence_name, build_evidence, evidence_owned)
        if set(os.listdir(output_fd)) != {artifact_name} or set(os.listdir(evidence_fd)) != {evidence_name}:
            raise PairedRendererInvocationRejected("persisted inventory differs from one file per directory")
        persisted_artifact, artifact_identity = _read_regular_at_with_identity(
            output_fd, artifact_name, a.maximum_output_bytes)
        persisted_evidence, evidence_identity = _read_regular_at_with_identity(
            evidence_fd, evidence_name, 2_000_000)
        if artifact_identity != artifact_owned[0] or evidence_identity != evidence_owned[0]:
            raise PairedRendererInvocationRejected("persisted pathname identity changed")
        fingerprint = _verify_bytes(projection, a, persisted_artifact, persisted_evidence,
                                    verify_renderer=False, filesystem_binding=binding_holder)
        # Descriptor-relative writes protect the admitted inodes; this final
        # check also prevents returning stale pathnames after a concurrent
        # rename/replacement of an authorized directory.
        _verify_directory_path_identity(output_directory, output_admitted)
        _verify_directory_path_identity(evidence_directory, evidence_admitted)
        _verify_directory_path_identity(ledger_directory, ledger_admitted)
        return VerifiedPairedRendererInvocation(
            persisted_artifact, persisted_evidence, output_directory / artifact_name,
            evidence_directory / evidence_name, fingerprint,
        )
    except PairedRendererInvocationRejected:
        if output_fd >= 0:
            _unlink_owned(output_fd, artifact_name, artifact_owned[0])
        if evidence_fd >= 0:
            _unlink_owned(evidence_fd, evidence_name, evidence_owned[0])
        raise
    except Exception as exc:
        if output_fd >= 0:
            _unlink_owned(output_fd, artifact_name, artifact_owned[0])
        if evidence_fd >= 0:
            _unlink_owned(evidence_fd, evidence_name, evidence_owned[0])
        raise PairedRendererInvocationRejected(str(exc)) from exc
    finally:
        for descriptor in (output_fd, evidence_fd, ledger_fd):
            if descriptor >= 0:
                os.close(descriptor)


def _load_bound_persisted(
    projection: PairedEditorialProjection, a: PairedTerminalRendererInvocationAuthorization,
    *, verify_renderer: bool,
) -> tuple[bytes, bytes, str, Path, Path]:
    descriptors: list[int] = []
    try:
        output_directory, output_identity = _safe_directory(a.output_directory)
        evidence_directory, evidence_identity = _safe_directory(a.evidence_directory)
        ledger_directory, ledger_identity = _safe_directory(a.authorization_ledger_directory)
        directory_identities = {"output": output_identity, "evidence": evidence_identity,
                                "authorization_ledger": ledger_identity}
        if len(set(directory_identities.values())) != 3:
            raise PairedRendererInvocationRejected("authorized directories must be pairwise distinct")
        output_fd = _open_admitted_directory(output_directory, output_identity)
        descriptors.append(output_fd)
        evidence_fd = _open_admitted_directory(evidence_directory, evidence_identity)
        descriptors.append(evidence_fd)
        ledger_fd = _open_admitted_directory(ledger_directory, ledger_identity)
        descriptors.append(ledger_fd)
        marker_name, marker = _consumption_marker(a, directory_identities)
        if (set(os.listdir(output_fd)) != {a.output_filename}
                or set(os.listdir(evidence_fd)) != {a.evidence_filename}
                or set(os.listdir(ledger_fd)) != {marker_name}):
            raise PairedRendererInvocationRejected("persisted inventory differs from authorized files")
        artifact, artifact_identity = _read_regular_at_with_identity(
            output_fd, a.output_filename, a.maximum_output_bytes)
        evidence, evidence_file_identity = _read_regular_at_with_identity(
            evidence_fd, a.evidence_filename, 2_000_000)
        persisted_marker, marker_identity = _read_regular_at_with_identity(
            ledger_fd, marker_name, 2_000_000)
        if persisted_marker != marker:
            raise PairedRendererInvocationRejected("authorization consumption marker differs")
        binding = _filesystem_binding(directory_identities, artifact_identity,
                                      evidence_file_identity, marker_name, marker)
        fingerprint = _verify_bytes(projection, a, artifact, evidence,
                                    verify_renderer=verify_renderer,
                                    filesystem_binding=binding)
        # Descriptor-relative second reads close the mutation window.
        if (_read_regular_at(output_fd, a.output_filename, a.maximum_output_bytes) != artifact
                or _read_regular_at(evidence_fd, a.evidence_filename, 2_000_000) != evidence
                or _read_regular_at(ledger_fd, marker_name, 2_000_000) != marker):
            raise PairedRendererInvocationRejected("persisted bytes changed during verification")
        _verify_directory_path_identity(output_directory, output_identity)
        _verify_directory_path_identity(evidence_directory, evidence_identity)
        _verify_directory_path_identity(ledger_directory, ledger_identity)
        return (artifact, evidence, fingerprint, output_directory / a.output_filename,
                evidence_directory / a.evidence_filename)
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def reverify_paired_renderer_invocation_evidence(
    *, projection: PairedEditorialProjection,
    authorization: PairedTerminalRendererInvocationAuthorization,
    upstream_admission: PairedUpstreamAdmissionToken,
    projection_evidence: PersistedPairedProfileProjectionEvidence,
    invocation: VerifiedPairedRendererInvocation,
) -> VerifiedPairedRendererInvocation:
    """Reload invocation bytes/evidence without using renderer output as an oracle."""
    try:
        if type(invocation) is not VerifiedPairedRendererInvocation:
            raise PairedRendererInvocationRejected("exact verified paired invocation required")
        validate_paired_projection(projection)
        if projection.projection_fingerprint != compute_projection_fingerprint(projection):
            raise PairedRendererInvocationRejected("projection fingerprint is stale")
        verify_paired_upstream_admission_token(upstream_admission, projection=projection)
        verify_persisted_paired_profile_projection_evidence(
            projection=projection, upstream_admission=upstream_admission,
            evidence=projection_evidence)
        a = _validate_authorization(authorization, projection)
        artifact, evidence, fingerprint, artifact_path, evidence_path = _load_bound_persisted(
            projection, a, verify_renderer=False)
        reloaded = VerifiedPairedRendererInvocation(
            artifact, evidence, artifact_path, evidence_path, fingerprint)
        if reloaded != invocation:
            raise PairedRendererInvocationRejected(
                "supplied verified invocation differs from persisted evidence")
        return reloaded
    except PairedRendererInvocationRejected:
        raise
    except Exception as exc:
        raise PairedRendererInvocationRejected(str(exc)) from exc


def verify_persisted_paired_renderer_invocation(*, projection: PairedEditorialProjection,
                                                 authorization: PairedTerminalRendererInvocationAuthorization,
                                                 upstream_admission: PairedUpstreamAdmissionToken,
                                                 projection_evidence: PersistedPairedProfileProjectionEvidence,
                                                 artifact_path: Path, evidence_path: Path,
                                                 ) -> VerifiedPairedRendererInvocation:
    try:
        validate_paired_projection(projection)
        if projection.projection_fingerprint != compute_projection_fingerprint(projection):
            raise PairedRendererInvocationRejected("projection fingerprint is stale")
        verify_paired_upstream_admission_token(upstream_admission, projection=projection)
        verify_persisted_paired_profile_projection_evidence(
            projection=projection, upstream_admission=upstream_admission,
            evidence=projection_evidence)
        a = _validate_authorization(authorization, projection)
        if not isinstance(artifact_path, Path) or not isinstance(evidence_path, Path):
            raise PairedRendererInvocationRejected("persisted paths must be Path values")
        artifact, evidence, fingerprint, expected_artifact, expected_evidence = _load_bound_persisted(
            projection, a, verify_renderer=True)
        if artifact_path != expected_artifact or evidence_path != expected_evidence:
            raise PairedRendererInvocationRejected("persisted paths differ from authorization")
        return VerifiedPairedRendererInvocation(artifact, evidence, expected_artifact,
                                                 expected_evidence, fingerprint)
    except PairedRendererInvocationRejected:
        raise
    except Exception as exc:
        raise PairedRendererInvocationRejected(str(exc)) from exc
