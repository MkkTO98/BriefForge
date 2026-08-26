"""Acceptance-complete controlled invocation boundary for the representative renderer.

The boundary independently reproduces the Release/Plan/projection, consumes one
exact authorization, performs two isolated executions, and persists the exact
nine-record BCRP artifact-evidence closure.  The external ledger is part of the
trusted local-filesystem writer boundary; its hashes detect tampering but are
not signatures or external attestation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import threading
import shutil
from typing import Any

from .bcrp.canonical import fingerprint_bundle
from .bcrp.model import BCRPBundle, BCRPRecord, PROFILE_VERSION
from .bcrp.validation import validate_bundle
from .publication_release import verify_publication_release
from .renderer_compatibility_planning import verify_renderer_compatibility_plan
from .representative_projection import (
    Audience, Authority, CaseBinding, DescribedIdentity, Distribution, EvidenceSnapshot,
    ExactValue, Exhibit, ExternalReference, Obligation, PROJECTION_PROFILE_ID,
    PROJECTION_PROFILE_VERSION, Provenance, Purpose, Qualification, RENDERER_ADAPTER_ID,
    RENDERER_IDENTITY, RENDERER_VERSION, RepresentativeProjection, RequirementMapping,
    Section, Statement, build_representative_projection,
)

INVOCATION_EVIDENCE_CONTRACT = "briefforge:representative-controlled-renderer-invocation-evidence:1.0.0"
CONTROLLED_INVOCATION_POLICY_ID = "briefforge-controlled-renderer-invocation-policy:1.0.0"
ACCEPTED_INVOCATION_AUTHORITY_IDENTITY = "authority:briefforge-controlled-renderer-invocation"
ACCEPTED_INVOCATION_AUTHORITY_OWNER = "project:BriefForge"
ACCEPTED_INVOCATION_AUTHORITY_ROLE = "renderer-invocation-authority"
_FIXED_MEDIA_TYPE = "text/html"
_FIXED_MODE = "one-artifact-with-determinism-replay"
_FIXED_ENVIRONMENT = (("LANG", "C"), ("LC_ALL", "C"), ("TZ", "UTC"),
                      ("PYTHONDONTWRITEBYTECODE", "1"), ("PYTHONHASHSEED", "0"),
                      ("PYTHONUTF8", "1"))
_FIXED_FLAGS = ("-B", "-s", "-S", "-X", "utf8")
_EXECUTION_LOCK = threading.Lock()
_ID = re.compile(r"[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*")


class RepresentativeInvocationRejected(ValueError):
    pass


@dataclass(frozen=True)
class RepresentativeRendererInvocationAuthorization:
    identity: str
    policy_identity: str
    authority_identity: str
    authority_owner: str
    authority_role: str
    authorization_time: str
    release_identity: str
    release_fingerprint: str
    lifecycle_inventory_digest: str
    plan_identity: str
    plan_fingerprint: str
    capability_identity: str
    capability_fingerprint: str
    renderer_identity: str
    renderer_adapter_id: str
    renderer_version: str
    renderer_implementation_digest: str
    projection_fingerprint: str
    authorization_ledger_directory: str
    output_directory: str
    output_filename: str
    output_count: int
    maximum_output_bytes: int
    media_type: str
    environment: tuple[tuple[str, str], ...]
    external_assets: tuple[str, ...]
    invocation_mode: str
    timeout_seconds: int
    evidence_filename: str
    fingerprint: str


@dataclass(frozen=True)
class VerifiedRepresentativeRendererInvocation:
    _bundle_document: str
    artifact_bytes: bytes
    evidence_bytes: bytes
    artifact_path: Path
    evidence_path: Path
    fingerprint: Any

    @property
    def bundle(self) -> BCRPBundle:
        return _deserialize_bundle(self._bundle_document)


@dataclass(frozen=True)
class RepresentativeInvocationResult:
    findings: tuple[str, ...]
    verified: VerifiedRepresentativeRendererInvocation | None

    @property
    def blocked(self) -> bool:
        return self.verified is None


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def compute_representative_invocation_authorization_fingerprint(authorization):
    if type(authorization) is not RepresentativeRendererInvocationAuthorization:
        raise TypeError("exact authorization required")
    document = asdict(authorization)
    document.pop("fingerprint")
    return _sha256(_canonical(document))


def representative_renderer_implementation_digest() -> str:
    """Bind the complete fixed executable source closure, including this loader."""
    base = Path(__file__).parent
    names = _RENDERER_SOURCE_CLOSURE
    closure = bytearray(b"briefforge-representative-renderer-closure-v1\0")
    for name in names:
        closure.extend(name.encode("ascii") + b"\0" + (base / name).read_bytes() + b"\0")
    interpreter = {
        "executable_realpath": os.path.realpath(sys.executable),
        "version": sys.version,
        "implementation": sys.implementation.name,
        "cache_tag": sys.implementation.cache_tag,
    }
    closure.extend(b"interpreter\0" + _canonical(interpreter) + b"\0")
    return _sha256(bytes(closure))


_RENDERER_SOURCE_CLOSURE = tuple(
    path.relative_to(Path(__file__).parent).as_posix()
    for path in sorted(Path(__file__).parent.rglob("*.py"))
)


def _exact(cls, document):
    if type(document) is not dict or set(document) != {item.name for item in fields(cls)}:
        raise RepresentativeInvocationRejected(f"invalid {cls.__name__} schema")
    return cls(**document)


def _projection_from_document(document):
    if type(document) is not dict or set(document) != {item.name for item in fields(RepresentativeProjection)}:
        raise RepresentativeInvocationRejected("invalid projection schema")
    collections = {
        "audiences": Audience, "sections": Section, "statements": Statement,
        "qualifications": Qualification, "case_bindings": CaseBinding, "values": ExactValue,
        "provenance": Provenance, "evidence_snapshots": EvidenceSnapshot,
        "external_references": ExternalReference, "units": DescribedIdentity,
        "semantic_types": DescribedIdentity, "obligations": Obligation,
        "content_authorities": Authority, "operational_authority_exclusions": Authority,
        "requirement_mappings": RequirementMapping,
    }
    singletons = {"brief_purpose": Purpose, "candidate_purpose": Purpose,
                  "exhibit": Exhibit, "distribution": Distribution}
    tuple_fields = {"material_identities", "required_value_ids", "fallbacks",
                    "comparison_universes", "selection_sets", "consistency_assertions",
                    "state_validations", "section_preorder", "case_order", "children",
                    "communication_functions", "upstream_refs", "target_refs", "constraints",
                    "authority_label_refs", "caveat_refs", "permitted_transformations",
                    "fallback_refs", "value_ids"}
    converted = dict(document)

    def make(cls, value):
        if type(value) is not dict:
            raise RepresentativeInvocationRejected("invalid projection member")
        item = dict(value)
        for key in tuple_fields & set(item):
            if type(item[key]) is not list:
                raise RepresentativeInvocationRejected("invalid projection tuple")
            item[key] = tuple(item[key])
        return _exact(cls, item)

    for name, cls in collections.items():
        if type(document[name]) is not list:
            raise RepresentativeInvocationRejected("invalid projection collection")
        converted[name] = tuple(make(cls, item) for item in document[name])
    for name, cls in singletons.items():
        converted[name] = make(cls, document[name])
    for name in tuple_fields & set(converted):
        if type(converted[name]) is not list:
            raise RepresentativeInvocationRejected("invalid projection tuple")
        converted[name] = tuple(converted[name])
    return _exact(RepresentativeProjection, converted)


def _render_in_subprocess(projection, timeout_seconds, work_directory=None, expected_digest=None):
    digest = expected_digest or representative_renderer_implementation_digest()
    request = _canonical({"projection": asdict(projection), "renderer_digest": digest})
    own_temporary = work_directory is None
    temporary = tempfile.TemporaryDirectory(prefix="briefforge-representative-worker-") if own_temporary else None
    directory = Path(temporary.name) if temporary is not None else Path(work_directory)
    try:
        # Execute a private snapshot of the exact bytes measured by the digest.  No
        # import is allowed to drift back to the ambient project tree.
        source_root = Path(__file__).parent
        stage = Path(tempfile.mkdtemp(prefix="briefforge-representative-source-"))
        package = stage / "briefforge"
        for name in _RENDERER_SOURCE_CLOSURE:
            destination = package / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((source_root / name).read_bytes())
        worker = package / "_representative_renderer_worker.py"
        try:
            with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
                done = subprocess.run(
                    (sys.executable, *_FIXED_FLAGS, str(worker)), input=request,
                    stdout=stdout_file, stderr=stderr_file, env=dict(_FIXED_ENVIRONMENT),
                    cwd=directory, timeout=timeout_seconds, check=False,
                )
                if stdout_file.tell() > 1_000_000 or stderr_file.tell() > 64_000:
                    raise RepresentativeInvocationRejected("worker output exceeds fixed byte bound")
                stdout_file.seek(0); stderr_file.seek(0)
                output, error = stdout_file.read(), stderr_file.read()
        except subprocess.TimeoutExpired as exc:
            raise RepresentativeInvocationRejected("renderer timed out") from exc
        if done.returncode:
            raise RepresentativeInvocationRejected(error.decode("utf-8", "replace")[:1000] or "worker failed")
        try:
            attestation = json.loads(error.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RepresentativeInvocationRejected("worker control attestation malformed") from exc
        expected = {"dont_write_bytecode": True, "environment": dict(_FIXED_ENVIRONMENT),
                    "hash_randomization": False, "ignore_environment": False,
                    "interpreter_flags": list(_FIXED_FLAGS), "utf8_mode": 1}
        if attestation != expected:
            raise RepresentativeInvocationRejected("worker effective controls differ from policy")
        if tuple(directory.iterdir()):
            raise RepresentativeInvocationRejected("renderer produced undeclared auxiliary files")
        return output
    finally:
        if "stage" in locals():
            shutil.rmtree(stage, ignore_errors=True)
        if temporary is not None:
            temporary.cleanup()


def render_representative_in_isolation(projection, timeout_seconds=5):
    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 30:
        raise RepresentativeInvocationRejected("timeout bound invalid")
    with _EXECUTION_LOCK:
        with tempfile.TemporaryDirectory(prefix="briefforge-representative-a-") as first_dir, \
             tempfile.TemporaryDirectory(prefix="briefforge-representative-b-") as second_dir:
            digest = representative_renderer_implementation_digest()
            first = _render_in_subprocess(projection, timeout_seconds, Path(first_dir), digest)
            second = _render_in_subprocess(projection, timeout_seconds, Path(second_dir), digest)
    if first != second:
        raise RepresentativeInvocationRejected("independent renderer runs are nondeterministic")
    if len(first) > 1_000_000:
        raise RepresentativeInvocationRejected("artifact exceeds fixed profile bound")
    return first


def _serialize_bundle(bundle: BCRPBundle) -> str:
    return json.dumps({"profile_identity": bundle.profile_identity,
                       "profile_version": bundle.profile_version,
                       "records": [record.to_document() for record in bundle.records]},
                      ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _deserialize_bundle(text: str) -> BCRPBundle:
    document = json.loads(text)
    if type(document) is not dict or set(document) != {"profile_identity", "profile_version", "records"} or type(document["records"]) is not list:
        raise RepresentativeInvocationRejected("persisted invocation evidence envelope malformed")
    return BCRPBundle(document["profile_identity"], document["profile_version"],
                      tuple(BCRPRecord.from_document(item) for item in document["records"]))


def _canonical_time(value: str) -> bool:
    try:
        if type(value) is not str or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value):
            return False
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return parsed.isoformat().replace("+00:00", "Z") == value
    except ValueError:
        return False


def _safe_relative_filename(value: str, expected_basename: str) -> bool:
    if type(value) is not str:
        return False
    path = Path(value)
    return (not path.is_absolute() and path.name == expected_basename and ".." not in path.parts
            and 1 <= len(path.parts) <= 2 and all(part not in ("", ".") for part in path.parts))


def _paths(authorization):
    root = Path(authorization.output_directory)
    artifact = root / authorization.output_filename
    evidence = root / authorization.evidence_filename
    return root, artifact, evidence


def _authorization_problems(a, projection, release, scope, declaration, plan,
                            planning_authorization=None):
    if type(a) is not RepresentativeRendererInvocationAuthorization:
        return ["exact invocation authorization is required"]
    malformed = []
    for field in fields(a):
        if field.name in {"output_count", "maximum_output_bytes", "timeout_seconds"}:
            if type(getattr(a, field.name)) is not int:
                malformed.append(field.name)
        elif field.name == "environment":
            value = getattr(a, field.name)
            if type(value) is not tuple or any(type(x) is not tuple or len(x) != 2 or any(type(y) is not str for y in x) for x in value):
                malformed.append(field.name)
        elif field.name == "external_assets":
            value = getattr(a, field.name)
            if type(value) is not tuple or any(type(x) is not str for x in value):
                malformed.append(field.name)
        elif type(getattr(a, field.name)) is not str:
            malformed.append(field.name)
    if malformed:
        return ["authorization fields have invalid types: " + ",".join(sorted(malformed))]
    expected = {
        "policy_identity": CONTROLLED_INVOCATION_POLICY_ID,
        "authority_identity": ACCEPTED_INVOCATION_AUTHORITY_IDENTITY,
        "authority_owner": ACCEPTED_INVOCATION_AUTHORITY_OWNER,
        "authority_role": ACCEPTED_INVOCATION_AUTHORITY_ROLE,
        "release_identity": release.release.identity, "release_fingerprint": release.fingerprint.digest,
        "lifecycle_inventory_digest": scope.inventory_digest,
        "plan_identity": plan.plan.identity, "plan_fingerprint": plan.fingerprint.digest,
        "capability_identity": declaration.identity, "capability_fingerprint": declaration.fingerprint,
        "renderer_identity": RENDERER_IDENTITY, "renderer_adapter_id": RENDERER_ADAPTER_ID,
        "renderer_version": RENDERER_VERSION,
        "renderer_implementation_digest": representative_renderer_implementation_digest(),
        "projection_fingerprint": projection.fingerprint, "output_count": 1,
        "media_type": _FIXED_MEDIA_TYPE, "environment": _FIXED_ENVIRONMENT,
        "external_assets": (), "invocation_mode": _FIXED_MODE,
    }
    problems = [f"authorization {name} does not bind the exact invocation act"
                for name, expected_value in expected.items() if getattr(a, name) != expected_value]
    if not a.identity or not _ID.fullmatch(a.identity) or not _canonical_time(a.authorization_time):
        problems.append("authorization identity or canonical UTC time is invalid")
    elif planning_authorization is not None:
        try:
            invocation_time = datetime.strptime(a.authorization_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            predecessors = (release.release.semantic["publication_time"], declaration.declaration_time,
                            planning_authorization.authorization_time, planning_authorization.planning_time)
            if any(invocation_time < datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                   for value in predecessors):
                problems.append("invocation authorization predates a bound predecessor")
        except (KeyError, TypeError, ValueError):
            problems.append("bound predecessor chronology is invalid")
    if a.fingerprint != compute_representative_invocation_authorization_fingerprint(a):
        problems.append("authorization fingerprint is stale")
    if not 1 <= a.maximum_output_bytes <= 1_000_000 or not 1 <= a.timeout_seconds <= 30:
        problems.append("authorization resource bound invalid")
    if not _safe_relative_filename(a.output_filename, "brief.html") or not _safe_relative_filename(a.evidence_filename, "representative-invocation-evidence.json"):
        problems.append("authorization output inventory is unsafe")
    return problems


def _open_directory(path: Path) -> int:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise RepresentativeInvocationRejected("path is not a directory")
    return descriptor


def _read_regular(path: Path, maximum=10_000_000) -> bytes:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_size > maximum:
            raise RepresentativeInvocationRejected("persisted path is not a bounded regular file")
        chunks, total = [], 0
        while True:
            chunk = os.read(descriptor, min(1024 * 1024, maximum + 1 - total))
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk); total += len(chunk)
            if total > maximum:
                raise RepresentativeInvocationRejected("persisted file exceeds bound")
    finally:
        os.close(descriptor)


def _write_exclusive(path: Path, data: bytes) -> None:
    """Legacy compatibility seam; controlled persistence uses descriptor-relative I/O."""
    directory = _open_directory(path.parent)
    try:
        _write_exclusive_at(directory, path.name, data)
        os.fsync(directory)
    finally:
        os.close(directory)


def _write_exclusive_at(directory_fd: int, name: str, data: bytes, created=None) -> None:
    if not name or name in {".", ".."} or "/" in name or os.sep in name:
        raise RepresentativeInvocationRejected("unsafe descriptor-relative filename")
    descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                         getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=directory_fd)
    opened = os.fstat(descriptor)
    owned_identity = (opened.st_dev, opened.st_ino)
    try:
        view = memoryview(data)
        while view:
            count = os.write(descriptor, view)
            if count <= 0:
                raise OSError("short write")
            view = view[count:]
        os.fsync(descriptor)
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_size != len(data):
            raise RepresentativeInvocationRejected("incomplete durable write")
        os.fsync(directory_fd)
        if created is not None:
            created[0] = owned_identity
    except BaseException:
        raise
    finally:
        os.close(descriptor)


def _unlink_owned_at(directory_fd: int, name: str, owned_identity) -> None:
    current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    if (current.st_dev, current.st_ino) != owned_identity:
        return
    os.unlink(name, dir_fd=directory_fd)
    os.fsync(directory_fd)


def _read_regular_at(directory_fd: int, name: str, maximum=10_000_000) -> bytes:
    descriptor = os.open(name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory_fd)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_size > maximum:
            raise RepresentativeInvocationRejected("persisted path is not a bounded regular file")
        result = bytearray()
        while len(result) < info.st_size:
            chunk = os.read(descriptor, min(65536, info.st_size - len(result)))
            if not chunk:
                raise RepresentativeInvocationRejected("persisted file was truncated")
            result.extend(chunk)
        after = os.fstat(descriptor)
        if (after.st_dev, after.st_ino, after.st_size) != (info.st_dev, info.st_ino, info.st_size):
            raise RepresentativeInvocationRejected("persisted file changed while read")
        return bytes(result)
    finally:
        os.close(descriptor)


def _ledger_path(a) -> Path:
    path = Path(a.authorization_ledger_directory)
    if (not path.is_absolute() or str(path.resolve()) != a.authorization_ledger_directory
            or path.is_symlink() or not path.is_dir()):
        raise RepresentativeInvocationRejected("authorization ledger directory is unsafe")
    return path


def _identity_key(a) -> str:
    return _sha256(a.identity.encode("utf-8"))


def _consumption_name(a) -> str:
    return f"{_identity_key(a)}.consumed"


def _consume(a, ledger_fd=None) -> None:
    own_descriptor = ledger_fd is None
    if own_descriptor:
        ledger_fd = _open_directory(_ledger_path(a))
    try:
        _write_exclusive_at(ledger_fd, _consumption_name(a), a.fingerprint.encode("ascii"))
        os.fsync(ledger_fd)
    except FileExistsError as exc:
        raise RepresentativeInvocationRejected("authorization identity has already been consumed") from exc
    finally:
        if own_descriptor:
            os.close(ledger_fd)


def _commitment_name(a) -> str:
    return f"{a.fingerprint}.admitted"


def _commitment(a, artifact: bytes, evidence: bytes) -> bytes:
    return _canonical({"contract_identity": "briefforge:representative-invocation-admission-commitment:1.0.0",
                       "authorization_fingerprint": a.fingerprint,
                       "artifact_path": str(_paths(a)[1]), "artifact_sha256": _sha256(artifact),
                       "artifact_byte_length": len(artifact), "evidence_path": str(_paths(a)[2]),
                       "evidence_sha256": _sha256(evidence), "evidence_byte_length": len(evidence)})


def _verify_commitment(a, artifact: bytes, evidence: bytes) -> None:
    if _read_regular(_ledger_path(a) / _commitment_name(a)) != _commitment(a, artifact, evidence):
        raise RepresentativeInvocationRejected("artifact/evidence pair differs from external admission commitment")


def _audit_record(plan, declaration, authorization, projection, artifact):
    bundle = plan.bundle
    release = bundle.one("PublicationReleaseRecord")
    ready = bundle.one("ReadyPresentationPackageRecord")
    digest = _sha256(artifact)
    suffix = authorization.identity.split(":", 1)[-1]
    artifact_id = f"artifact:{suffix}"
    payload = {
        "contract_identity": INVOCATION_EVIDENCE_CONTRACT,
        "policy_identity": CONTROLLED_INVOCATION_POLICY_ID,
        "authorization_identity": authorization.identity,
        "authorization_fingerprint": authorization.fingerprint,
        "authorization_ledger_directory": authorization.authorization_ledger_directory,
        "admission_commitment_identity": _commitment_name(authorization),
        "lifecycle_inventory_digest": authorization.lifecycle_inventory_digest,
        "plan_fingerprint": plan.fingerprint.digest,
        "capability_fingerprint": declaration.fingerprint,
        "renderer_identity": RENDERER_IDENTITY, "renderer_adapter_id": RENDERER_ADAPTER_ID,
        "renderer_version": RENDERER_VERSION,
        "renderer_implementation_digest": authorization.renderer_implementation_digest,
        "projection_profile_identity": PROJECTION_PROFILE_ID,
        "projection_profile_version": PROJECTION_PROFILE_VERSION,
        "projection_fingerprint": projection.fingerprint,
        "projection_closure_fingerprint": projection.fingerprint,
        "consumed_mapping_ids": [item.requirement_id for item in projection.requirement_mappings],
        "selected_expression_modes": [item.expression_mode for item in projection.requirement_mappings],
        "invocation_mode": _FIXED_MODE, "environment": [list(item) for item in _FIXED_ENVIRONMENT],
        "environment_policy": "explicit-minimal-environment-before-isolated-worker-import",
        "interpreter_flags": list(_FIXED_FLAGS),
        "effective_interpreter_controls": "verified-in-each-independent-execution",
        "external_assets": [], "output_directory": authorization.output_directory,
        "output_inventory": [{"filename": authorization.output_filename, "media_type": _FIXED_MEDIA_TYPE,
                              "sha256": digest, "byte_length": len(artifact)}],
        "execution_digests": [digest, digest], "execution_byte_lengths": [len(artifact), len(artifact)],
        "invocation_outcome": "completed-deterministically", "artifact_existence": "verified",
        "audit_links": "verified", "semantic_conformance": "unassessed",
        "manifest_authority": "absent", "distribution_authority": "absent",
        "successful_publication": "not-asserted",
    }
    return BCRPRecord(
        kind="GeneratedArtifactAuditRecord", identity=f"artifact-audit:{suffix}",
        profile_version=PROFILE_VERSION,
        semantic={"release_ref": release.identity, "ready_ref": ready.identity,
                  "ready_fingerprint": ready.semantic["ready_fingerprint"],
                  "plan_ref": plan.plan.identity, "renderer_capability_ref": declaration.identity,
                  "artifact": {"id": artifact_id, "filename": "brief.html", "media_type": _FIXED_MEDIA_TYPE,
                               "sha256": digest, "byte_length": len(artifact)},
                  "audit_links_pass": True, "invocation_time": authorization.authorization_time},
        extensions=[{"owner_namespace": "briefforge-representative-controlled-renderer-invocation",
                     "name": "invocation-and-artifact-evidence", "version": "1.0.0",
                     "authority_ref": authorization.authority_identity,
                     "scope": "artifact-existence-and-invocation-audit-links-only",
                     "target_refs": [release.identity, ready.identity, plan.plan.identity,
                                     declaration.identity, artifact_id],
                     "criticality": "required", "character": "semantic",
                     "validation_contract": INVOCATION_EVIDENCE_CONTRACT,
                     "preservation": "must-preserve", "payload": payload}],
    )


def _verify_bytes(*, artifact, evidence, evidence_snapshot, lifecycle_scope, declaration,
                  planning_authorization, authorization):
    try:
        text = evidence.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RepresentativeInvocationRejected("evidence is not UTF-8") from exc
    bundle = _deserialize_bundle(text)
    if text != _serialize_bundle(bundle):
        raise RepresentativeInvocationRejected("evidence bytes are not canonical")
    kinds = ("PresentationBriefRecord", "PortablePresentationMaterialRecord",
             "CandidatePresentationPackageRecord", "ValidationJudgmentRecord",
             "ReadyPresentationPackageRecord", "PublicationReleaseRecord",
             "RendererCapabilityDeclarationRecord", "RendererCompatibilityPlanRecord",
             "GeneratedArtifactAuditRecord")
    if len(bundle.records) != 9 or tuple(record.kind for record in bundle.records) != kinds:
        raise RepresentativeInvocationRejected("exact eight-record Plan closure plus artifact audit required")
    generic = validate_bundle(bundle, through_layer="L5")
    specialized = {bundle.one(kind).identity for kind in kinds[3:]}
    unexpected = [finding for finding in generic.findings if not (
        finding.layer == "L1" and finding.family == "extension-boundary" and finding.severity == "blocking"
        and finding.blocking_consequence == "all dependent processing" and finding.semantic_identity in specialized
        and finding.location == "/extensions/0"
        and finding.message == "Unknown required semantic extension cannot be processed."
        and finding.referenced_identities == ())]
    if unexpected:
        raise RepresentativeInvocationRejected("nine-record evidence fails generic BCRP validation")
    release_bundle = BCRPBundle(bundle.profile_identity, bundle.profile_version, bundle.records[:6])
    release = verify_publication_release(release_bundle, evidence_snapshot=evidence_snapshot,
                                         expected_release_fingerprint=authorization.release_fingerprint)
    plan_bundle = BCRPBundle(bundle.profile_identity, bundle.profile_version, bundle.records[:8])
    plan = verify_renderer_compatibility_plan(
        plan_bundle, evidence_snapshot=evidence_snapshot, lifecycle_scope=lifecycle_scope,
        declaration=declaration, authorization=planning_authorization,
        expected_plan_fingerprint=authorization.plan_fingerprint)
    projection = build_representative_projection(
        verified_release=release, evidence_snapshot=evidence_snapshot, lifecycle_scope=lifecycle_scope,
        declaration=declaration, planning_authorization=planning_authorization, verified_plan=plan)
    if _authorization_problems(authorization, projection, release, lifecycle_scope, declaration, plan,
                               planning_authorization):
        raise RepresentativeInvocationRejected("persisted authorization is stale")
    expected = _audit_record(plan, declaration, authorization, projection, artifact)
    if bundle.records[:8] != plan.bundle.records or bundle.records[8].to_document() != expected.to_document():
        raise RepresentativeInvocationRejected("evidence differs from exact independently reproduced record")
    if len(artifact) > authorization.maximum_output_bytes:
        raise RepresentativeInvocationRejected("artifact exceeds authorization")
    from .representative_renderer import render_representative_html
    if artifact != render_representative_html(projection):
        raise RepresentativeInvocationRejected("artifact differs from independently reproduced renderer output")
    fingerprint = fingerprint_bundle(bundle, domain="profile-instance", require_valid=False)
    return bundle, fingerprint


def invoke_controlled_representative_renderer(*, verified_release, evidence_snapshot,
                                               lifecycle_scope, declaration,
                                               planning_authorization, verified_plan,
                                               authorization):
    artifact_fd = evidence_fd = ledger_fd = -1
    artifact_name = evidence_name = commitment_name = None
    consumed = False
    commitment_state = [False]; artifact_state = [False]; evidence_state = [False]
    try:
        # Reverification is performed by projection construction and repeated from persisted Plan bytes.
        projection = build_representative_projection(
            verified_release=verified_release, evidence_snapshot=evidence_snapshot,
            lifecycle_scope=lifecycle_scope, declaration=declaration,
            planning_authorization=planning_authorization, verified_plan=verified_plan)
        plan = verify_renderer_compatibility_plan(
            verified_plan.bundle, evidence_snapshot=evidence_snapshot, lifecycle_scope=lifecycle_scope,
            declaration=declaration, authorization=planning_authorization,
            expected_plan_fingerprint=verified_plan.fingerprint.digest)
        problems = _authorization_problems(authorization, projection, verified_release,
                                           lifecycle_scope, declaration, plan, planning_authorization)
        if problems:
            raise RepresentativeInvocationRejected("; ".join(problems))
        root, artifact_path, evidence_path = _paths(authorization)
        if (not root.is_absolute() or str(root.resolve()) != authorization.output_directory
                or root.is_symlink() or not root.is_dir()):
            raise RepresentativeInvocationRejected("authorized output directory is unsafe")
        for parent in {artifact_path.parent, evidence_path.parent}:
            if parent.is_symlink() or not parent.is_dir() or parent.parent != root or tuple(parent.iterdir()):
                raise RepresentativeInvocationRejected("authorized destination inventory is unsafe or nonempty")
        if artifact_path.parent == evidence_path.parent:
            raise RepresentativeInvocationRejected("artifact and evidence destinations must be isolated")
        _ledger_path(authorization)
        # Hold all authorized directory objects before consuming authority. Every
        # subsequent inventory/read/write/unlink/fsync is relative to these fds.
        artifact_fd = _open_directory(artifact_path.parent)
        evidence_fd = _open_directory(evidence_path.parent)
        ledger_fd = _open_directory(_ledger_path(authorization))
        artifact_identity = tuple(os.fstat(artifact_fd)[i] for i in (stat.ST_DEV, stat.ST_INO))
        evidence_identity = tuple(os.fstat(evidence_fd)[i] for i in (stat.ST_DEV, stat.ST_INO))
        ledger_identity = tuple(os.fstat(ledger_fd)[i] for i in (stat.ST_DEV, stat.ST_INO))
        if len({artifact_identity, evidence_identity, ledger_identity}) != 3:
            raise RepresentativeInvocationRejected("artifact, evidence, and ledger directories must be distinct")
        identities = {
            artifact_path.parent: artifact_identity,
            evidence_path.parent: evidence_identity,
            _ledger_path(authorization): ledger_identity,
        }
        if os.listdir(artifact_fd) or os.listdir(evidence_fd):
            raise RepresentativeInvocationRejected("authorized destination inventory is nonempty")
        _consume(authorization, ledger_fd); consumed = True
        artifact = render_representative_in_isolation(projection, authorization.timeout_seconds)
        if len(artifact) > authorization.maximum_output_bytes:
            raise RepresentativeInvocationRejected("authorized output bound exceeded")
        audit = _audit_record(plan, declaration, authorization, projection, artifact)
        bundle = BCRPBundle(plan.bundle.profile_identity, plan.bundle.profile_version,
                            plan.bundle.records + (audit,))
        evidence = _serialize_bundle(bundle).encode("utf-8")
        _verify_bytes(artifact=artifact, evidence=evidence, evidence_snapshot=evidence_snapshot,
                      lifecycle_scope=lifecycle_scope, declaration=declaration,
                      planning_authorization=planning_authorization, authorization=authorization)
        commitment_name = _commitment_name(authorization)
        artifact_name, evidence_name = artifact_path.name, evidence_path.name
        _write_exclusive_at(artifact_fd, artifact_name, artifact, artifact_state)
        _write_exclusive_at(evidence_fd, evidence_name, evidence, evidence_state)
        # Re-open only to attest that each pathname still designates the held
        # directory object; never use that pathname for data operations.
        for path, expected_identity in identities.items():
            check = _open_directory(path)
            try:
                info = os.fstat(check)
                if (info.st_dev, info.st_ino) != expected_identity:
                    raise RepresentativeInvocationRejected("authorized directory identity changed")
            finally:
                os.close(check)
        persisted_artifact = _read_regular_at(artifact_fd, artifact_name, authorization.maximum_output_bytes)
        persisted_evidence = _read_regular_at(evidence_fd, evidence_name)
        reloaded_bundle, fingerprint = _verify_bytes(
            artifact=persisted_artifact, evidence=persisted_evidence,
            evidence_snapshot=evidence_snapshot, lifecycle_scope=lifecycle_scope,
            declaration=declaration, planning_authorization=planning_authorization,
            authorization=authorization)
        if tuple(record.to_document() for record in verified_release.bundle.records) != tuple(
                record.to_document() for record in reloaded_bundle.records[:6]):
            raise RepresentativeInvocationRejected("supplied Release differs from persisted Release closure")
        if tuple(record.to_document() for record in plan.bundle.records) != tuple(
                record.to_document() for record in reloaded_bundle.records[:8]):
            raise RepresentativeInvocationRejected("supplied Plan differs from persisted Plan closure")
        _write_exclusive_at(ledger_fd, commitment_name,
                            _commitment(authorization, persisted_artifact, persisted_evidence), commitment_state)
        check = _open_directory(_ledger_path(authorization))
        try:
            info = os.fstat(check)
            if (info.st_dev, info.st_ino) != identities[_ledger_path(authorization)]:
                raise RepresentativeInvocationRejected("authorized ledger identity changed")
        finally:
            os.close(check)
        verified = VerifiedRepresentativeRendererInvocation(
            _serialize_bundle(reloaded_bundle), bytes(persisted_artifact), bytes(persisted_evidence),
            artifact_path, evidence_path, fingerprint)
        return RepresentativeInvocationResult((), verified)
    except Exception as exc:
        # Consumption and any incomplete, unadmitted bytes are retained.  The
        # admission commitment is written last, so failed products are unusable
        # and rollback never deletes a concurrently replaced directory entry.
        return RepresentativeInvocationResult((str(exc),), None)
    finally:
        for descriptor in (artifact_fd, evidence_fd, ledger_fd):
            if descriptor >= 0:
                os.close(descriptor)


def verify_persisted_representative_renderer_invocation(*, artifact_path, evidence_path,
                                                         verified_release, evidence_snapshot,
                                                         lifecycle_scope, declaration,
                                                         planning_authorization, verified_plan,
                                                         authorization):
    if not isinstance(artifact_path, Path) or not isinstance(evidence_path, Path):
        raise RepresentativeInvocationRejected("exact Path inputs required")
    root, expected_artifact, expected_evidence = _paths(authorization)
    if artifact_path != expected_artifact or evidence_path != expected_evidence:
        raise RepresentativeInvocationRejected("persisted paths differ from authorization")
    for parent, expected_name in ((artifact_path.parent, artifact_path.name),
                                  (evidence_path.parent, evidence_path.name)):
        descriptor = _open_directory(parent)
        try:
            if set(os.listdir(descriptor)) != {expected_name}:
                raise RepresentativeInvocationRejected("persisted destination inventory differs from exact one-file inventory")
        finally:
            os.close(descriptor)
    artifact = _read_regular(artifact_path, authorization.maximum_output_bytes)
    evidence = _read_regular(evidence_path)
    bundle, fingerprint = _verify_bytes(
        artifact=artifact, evidence=evidence, evidence_snapshot=evidence_snapshot,
        lifecycle_scope=lifecycle_scope, declaration=declaration,
        planning_authorization=planning_authorization, authorization=authorization)
    # The caller's supplied verified objects are not trusted shortcuts: compare them to reloaded bytes.
    if tuple(record.to_document() for record in verified_release.bundle.records) != tuple(
            record.to_document() for record in bundle.records[:6]):
        raise RepresentativeInvocationRejected("supplied Release differs from persisted Release closure")
    if tuple(record.to_document() for record in verified_plan.bundle.records) != tuple(
            record.to_document() for record in bundle.records[:8]):
        raise RepresentativeInvocationRejected("supplied Plan differs from persisted Plan closure")
    _verify_commitment(authorization, artifact, evidence)
    ledger_fd = _open_directory(_ledger_path(authorization))
    try:
        consumption = _read_regular_at(ledger_fd, _consumption_name(authorization), 4096)
        if consumption != authorization.fingerprint.encode("ascii"):
            raise RepresentativeInvocationRejected("invocation authorization consumption mismatch")
    finally:
        os.close(ledger_fd)
    if _read_regular(artifact_path, authorization.maximum_output_bytes) != artifact or _read_regular(evidence_path) != evidence:
        raise RepresentativeInvocationRejected("persisted bytes changed during verification")
    return VerifiedRepresentativeRendererInvocation(_serialize_bundle(bundle), bytes(artifact), bytes(evidence),
                                                     artifact_path, evidence_path, fingerprint)
