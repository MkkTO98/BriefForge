"""Fail-closed, no-overwrite controlled local-directory delivery companion.

This is a leaf profile, not a BCRP extension.  It installs only bytes admitted by
an independently reloaded Publication Manifest and makes no remote publication,
deployment, hosting, or receipt claim.
"""
from __future__ import annotations

from collections import Counter
import ctypes
from dataclasses import asdict, dataclass
import errno
import hashlib
import json
import os
from pathlib import Path
import stat
import unicodedata
from datetime import datetime, timezone
from typing import Any

from .publication_manifest_admission import (
    PublicationManifestAuthorization,
    VerifiedPublicationManifest,
    verify_manifest_current_eligibility,
    verify_persisted_publication_manifest,
)

_POLICY = "briefforge-controlled-local-delivery-policy:1.0.0"
_PROFILE = "briefforge-controlled-local-directory-delivery-profile:1.0.0"
_AUTHORITY_ID = "authority:briefforge-controlled-local-delivery"
_AUTHORITY_OWNER = "project:BriefForge"
_AUTHORITY_ROLE = "controlled-local-delivery-authority"
_AUTHORITY_SCOPE = "one-fixed-controlled-local-directory-delivery"
_IMPLEMENTATION = "briefforge.publication_distribution_delivery"
_VERSION = "1.0.0"
_EXCLUSIONS = (
    "network-distribution", "remote-receipt", "deployment-authority", "hosting-authority",
    "successful-publication-authority", "public-reachability", "browser-behavior-certification",
    "reader-access-certification", "accessibility-certification", "editorial-certification",
    "visual-certification", "factual-reassessment", "atlasforge-authority",
)
_MAX_ARTIFACT = 100_000_000
_MAX_EVIDENCE = 8 * 1024 * 1024
_MAX_ARTIFACT_COUNT = 64
_MAX_AGGREGATE_BYTES = 250_000_000
_HEX = frozenset("0123456789abcdef")


@dataclass(frozen=True)
class ControlledLocalDestination:
    parent_directory: str
    basename: str
    parent_device: int
    parent_inode: int


@dataclass(frozen=True)
class DeliveryInventoryItem:
    identity: str
    role: str
    logical_filename: str
    media_type: str
    byte_length: int
    sha256: str
    order: int


@dataclass(frozen=True, order=True)
class DeliveryFinding:
    code: str
    location: str
    message: str


@dataclass(frozen=True, order=True)
class DeliveryAuditLink:
    kind: str
    source_identity: str
    target_identity: str
    binding_fingerprint: str


@dataclass(frozen=True)
class ControlledLocalDeliveryAuthorization:
    identity: str
    policy_identity: str
    profile_identity: str
    profile_version: str
    authority_identity: str
    authority_owner: str
    authority_role: str
    authorization_time: str
    attempt_time: str
    completion_time: str
    manifest_authorization_fingerprint: str
    manifest_fingerprint: str
    manifest_identity: str
    manifest_record_identity: str
    release_identity: str
    release_fingerprint: str
    lifecycle_inventory_digest: str
    artifact_set_fingerprint: str
    delivery_inventory: tuple[DeliveryInventoryItem, ...]
    delivery_inventory_fingerprint: str
    destination: ControlledLocalDestination
    attempt_identity: str
    evidence_identity: str
    evidence_filename: str
    implementation_identity: str
    implementation_version: str
    commitment_ledger_directory: str
    commitment_ledger_device: int
    commitment_ledger_inode: int
    exclusions: tuple[str, ...]
    released_authority_scope: str
    fingerprint: str


@dataclass(frozen=True)
class ControlledLocalDeliveryEvidence:
    evidence_identity: str
    evidence_version: str
    policy_identity: str
    profile_identity: str
    profile_version: str
    implementation_identity: str
    implementation_version: str
    authorization_identity: str
    authorization_fingerprint: str
    authorization_issuance_evidence_path: str
    authorization_issuance_evidence_sha256: str
    authorization_issuance_fingerprint: str
    authorization_issuance_commitment_path: str
    authority_identity: str
    authority_owner: str
    authority_role: str
    authorization_time: str
    attempt_identity: str
    attempt_time: str
    completion_time: str
    manifest_identity: str
    manifest_fingerprint: str
    manifest_authorization_fingerprint: str
    release_identity: str
    release_fingerprint: str
    lifecycle_inventory_digest: str
    artifact_set_fingerprint: str
    delivery_inventory_fingerprint: str
    destination_parent: str
    destination_basename: str
    destination_parent_device: int
    destination_parent_inode: int
    commitment_ledger_directory: str
    commitment_ledger_device: int
    commitment_ledger_inode: int
    final_directory_device: int
    final_directory_inode: int
    inventory: tuple[DeliveryInventoryItem, ...]
    source_paths: tuple[str, ...]
    delivered_paths: tuple[str, ...]
    released_authority_scope: str
    audit_links: tuple[DeliveryAuditLink, ...]
    artifact_count: int
    aggregate_byte_length: int
    exclusions: tuple[str, ...]
    outcome: str
    fingerprint: str


_VERIFIED = object()


@dataclass(frozen=True, init=False)
class VerifiedControlledLocalDeliveryAuthorization:
    """Sealed evidence of one trusted-process authorization issuance.

    This marker makes no human-authentication or signature claim.  It is valid
    only while its exact immutable issuance evidence and commitment reload.
    """
    _authorization_document: str
    issuance_evidence_filename: str
    issuance_evidence_sha256: str
    issuance_fingerprint: str
    issuance_commitment_filename: str
    _marker: object

    @classmethod
    def _verified(cls, document: str, evidence_name: str, evidence_digest: str,
                  fingerprint: str, commitment_name: str) -> "VerifiedControlledLocalDeliveryAuthorization":
        value = object.__new__(cls)
        for name, item in (("_authorization_document", document), ("issuance_evidence_filename", evidence_name),
                           ("issuance_evidence_sha256", evidence_digest), ("issuance_fingerprint", fingerprint),
                           ("issuance_commitment_filename", commitment_name), ("_marker", _VERIFIED)):
            object.__setattr__(value, name, item)
        return value

    @property
    def authorization(self) -> ControlledLocalDeliveryAuthorization:
        return _authorization_from_document(json.loads(self._authorization_document))


@dataclass(frozen=True, init=False)
class VerifiedControlledLocalDelivery:
    _document: str
    fingerprint: str
    _marker: object

    @classmethod
    def _verified(cls, document: str, fingerprint: str) -> "VerifiedControlledLocalDelivery":
        value = object.__new__(cls)
        object.__setattr__(value, "_document", document)
        object.__setattr__(value, "fingerprint", fingerprint)
        object.__setattr__(value, "_marker", _VERIFIED)
        return value

    @property
    def evidence(self) -> ControlledLocalDeliveryEvidence:
        return _evidence_from_document(json.loads(self._document))


@dataclass(frozen=True)
class ControlledLocalDeliveryResult:
    findings: tuple[DeliveryFinding, ...]
    state: str
    verified: VerifiedControlledLocalDelivery | None

    @property
    def blocked(self) -> bool:
        return self.state != "completed"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _released_destination_scope(parent: Path, basename: str, ledger: Path) -> str:
    """Produce the sole release-authorable destination contract.

    Paths must already exist: this scope is a statement by Release, not a value a
    delivery caller can broaden after release.
    """
    parent = Path(parent); ledger = Path(ledger)
    if not _safe_basename(basename):
        raise ValueError("unsafe destination basename")
    for value in (parent, ledger):
        if not value.is_absolute():
            value = value.resolve()
        if str(value.resolve()) != str(value) or value.is_symlink() or not value.is_dir():
            raise ValueError("released boundary must be an existing canonical directory")
    ps, ls = os.stat(parent, follow_symlinks=False), os.stat(ledger, follow_symlinks=False)
    document = {
        "contract": {"atomic":"renameat2-noreplace", "collision":"nfc-casefold-no-alias",
                     "no_overwrite":True, "rollback":"verified-or-indeterminate"},
        "destination_parent":{"canonical_path":str(parent.resolve()),"device":ps.st_dev,"inode":ps.st_ino},
        "final_basename":basename,
        "ledger":{"canonical_path":str(ledger.resolve()),"device":ls.st_dev,"inode":ls.st_ino},
        "policy":_POLICY,"profile":_PROFILE,"implementation":_IMPLEMENTATION,"version":_VERSION,
    }
    return _canonical(document).decode("utf-8")


def _strict_utc(value: object) -> datetime:
    if type(value) is not str or len(value) != 20 or not value.endswith("Z"):
        raise ValueError("strict UTC second timestamp required")
    parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        raise ValueError("noncanonical UTC timestamp")
    return parsed


def _item_document(item: DeliveryInventoryItem) -> dict[str, Any]:
    return asdict(item)


def compute_delivery_inventory_fingerprint(inventory: tuple[DeliveryInventoryItem, ...]) -> str:
    if type(inventory) is not tuple or any(type(item) is not DeliveryInventoryItem for item in inventory):
        raise TypeError("Exact immutable delivery inventory required.")
    return hashlib.sha256(_canonical([_item_document(item) for item in inventory])).hexdigest()


def compute_delivery_authorization_fingerprint(authorization: ControlledLocalDeliveryAuthorization) -> str:
    if type(authorization) is not ControlledLocalDeliveryAuthorization:
        raise TypeError("Exact immutable delivery authorization required.")
    document = asdict(authorization); document.pop("fingerprint", None)
    return hashlib.sha256(_canonical(document)).hexdigest()


def _authorization_from_document(document: object) -> ControlledLocalDeliveryAuthorization:
    if type(document) is not dict:
        raise ValueError("Authorization document malformed")
    value = dict(document)
    value["destination"] = ControlledLocalDestination(**value["destination"])
    value["delivery_inventory"] = tuple(DeliveryInventoryItem(**item) for item in value["delivery_inventory"])
    value["exclusions"] = tuple(value["exclusions"])
    return ControlledLocalDeliveryAuthorization(**value)


def compute_delivery_evidence_fingerprint(evidence: ControlledLocalDeliveryEvidence) -> str:
    if type(evidence) is not ControlledLocalDeliveryEvidence:
        raise TypeError("Exact immutable delivery evidence required.")
    document = asdict(evidence); document.pop("fingerprint", None)
    return hashlib.sha256(_canonical(document)).hexdigest()


def _finding(code: str, location: str, message: str) -> DeliveryFinding:
    return DeliveryFinding(code, location, message)


def _sorted(values: list[DeliveryFinding] | tuple[DeliveryFinding, ...]) -> tuple[DeliveryFinding, ...]:
    return tuple(sorted(set(values)))


def _safe_basename(value: object) -> bool:
    return (type(value) is str and bool(value) and value not in {".", ".."}
            and value == unicodedata.normalize("NFC", value)
            and "\0" not in value and "/" not in value and "\\" not in value
            and not Path(value).is_absolute() and Path(value).name == value)


def validate_delivery_inventory(inventory: tuple[DeliveryInventoryItem, ...]) -> tuple[DeliveryFinding, ...]:
    if type(inventory) is not tuple or any(type(item) is not DeliveryInventoryItem for item in inventory):
        return (_finding("invalid-delivery-inventory", "/inventory", "Exact immutable inventory required."),)
    findings: list[DeliveryFinding] = []
    if not inventory or len(inventory) > _MAX_ARTIFACT_COUNT:
        findings.append(_finding("delivery-artifact-count-out-of-bounds", "/inventory", "Artifact count is outside the controlled bound."))
    if sum(x.byte_length for x in inventory if type(x.byte_length) is int and x.byte_length >= 0) > _MAX_AGGREGATE_BYTES:
        findings.append(_finding("delivery-aggregate-length-out-of-bounds", "/inventory", "Aggregate bytes exceed the controlled bound."))
    fields = (("identity", "duplicate-delivery-identity"), ("role", "duplicate-delivery-role"),
              ("logical_filename", "duplicate-delivery-basename"), ("order", "duplicate-delivery-order"))
    for field, code in fields:
        if any(count > 1 for count in Counter(getattr(item, field) for item in inventory).values()):
            findings.append(_finding(code, f"/inventory/{field}", f"Delivery {field} is duplicated."))
    portable = [unicodedata.normalize("NFC", item.logical_filename).casefold() for item in inventory]
    if len(portable) != len(set(portable)):
        findings.append(_finding("delivery-basename-collision", "/inventory/logical_filename", "Names collide under NFC and casefold."))
    for index, item in enumerate(inventory):
        location = f"/inventory/{index}"
        if not _safe_basename(item.logical_filename):
            findings.append(_finding("unsafe-delivery-basename", location + "/logical_filename", "Name is not one safe NFC basename."))
        if type(item.order) is not int or item.order != index:
            findings.append(_finding("delivery-order-mismatch", location + "/order", "Order is not exact contiguous encounter order."))
        if type(item.byte_length) is not int or item.byte_length < 0 or item.byte_length > _MAX_ARTIFACT:
            findings.append(_finding("invalid-delivery-length", location + "/byte_length", "Length is outside the controlled bound."))
        if type(item.sha256) is not str or len(item.sha256) != 64 or any(c not in _HEX for c in item.sha256):
            findings.append(_finding("invalid-delivery-digest", location + "/sha256", "Digest is not lowercase SHA-256."))
        for field in ("identity", "role", "media_type"):
            value = getattr(item, field)
            if type(value) is not str or not value or value != value.strip():
                findings.append(_finding("invalid-delivery-field", location + "/" + field, "Field requires stable nonempty text."))
    return _sorted(findings)


def _manifest_kwargs(*, manifest_evidence_path: Path, manifest_authorization: Any, evidence_snapshot: Any,
                     verified_release: Any, lifecycle_scope: Any, declaration: Any,
                     planning_authorization: Any, verified_plan: Any, invocation_authorization: Any,
                     conformance_authorization: Any, artifact_paths: tuple[Path, ...]) -> dict[str, Any]:
    return dict(manifest_evidence_path=manifest_evidence_path, evidence_snapshot=evidence_snapshot,
                verified_release=verified_release, lifecycle_scope=lifecycle_scope, declaration=declaration,
                planning_authorization=planning_authorization, verified_plan=verified_plan,
                invocation_authorization=invocation_authorization,
                conformance_authorization=conformance_authorization, artifact_paths=artifact_paths,
                authorization=manifest_authorization)


def _reload_manifest(arguments: dict[str, Any]) -> VerifiedPublicationManifest:
    return verify_persisted_publication_manifest(**arguments)


def _manifest_inventory(verified: VerifiedPublicationManifest) -> tuple[DeliveryInventoryItem, ...]:
    payload = verified.bundle.one("PublicationManifestRecord").extensions[0]["payload"]
    result = []
    for item in payload["artifact_inventory"]:
        result.append(DeliveryInventoryItem(item["identity"], item["role"], item["logical_filename"],
                                            item["media_type"], item["byte_length"], item["sha256"], item["order"]))
    return tuple(result)


def _authorization_findings(authorization: object, *, manifest_authorization: Any,
                            verified_manifest: VerifiedPublicationManifest, verified_release: Any,
                            lifecycle_scope: Any) -> tuple[DeliveryFinding, ...]:
    if type(authorization) is not ControlledLocalDeliveryAuthorization:
        return (_finding("missing-delivery-authorization", "/authorization", "Exact immutable authorization required."),)
    findings: list[DeliveryFinding] = list(validate_delivery_inventory(authorization.delivery_inventory))
    expected_inventory = _manifest_inventory(verified_manifest)
    if authorization.delivery_inventory != expected_inventory:
        findings.append(_finding("delivery-manifest-inventory-mismatch", "/authorization/delivery_inventory", "Inventory differs from verified Manifest."))
    expected = {
        "policy_identity": _POLICY, "profile_identity": _PROFILE, "profile_version": _VERSION,
        "authority_identity": _AUTHORITY_ID, "authority_owner": _AUTHORITY_OWNER,
        "authority_role": _AUTHORITY_ROLE, "manifest_authorization_fingerprint": manifest_authorization.fingerprint,
        "manifest_fingerprint": verified_manifest.fingerprint.digest,
        "manifest_identity": manifest_authorization.manifest_identity,
        "manifest_record_identity": manifest_authorization.record_identity,
        "release_identity": manifest_authorization.release_identity,
        "release_fingerprint": manifest_authorization.release_fingerprint,
        "lifecycle_inventory_digest": lifecycle_scope.inventory_digest,
        "artifact_set_fingerprint": manifest_authorization.artifact_set_fingerprint,
        "delivery_inventory_fingerprint": compute_delivery_inventory_fingerprint(authorization.delivery_inventory),
        "implementation_identity": _IMPLEMENTATION, "implementation_version": _VERSION,
        "exclusions": _EXCLUSIONS,
    }
    for name, value in expected.items():
        if getattr(authorization, name, None) != value:
            findings.append(_finding("delivery-authorization-binding-mismatch", f"/authorization/{name}", f"Authorization binds stale or different {name}."))
    if authorization.fingerprint != compute_delivery_authorization_fingerprint(authorization):
        findings.append(_finding("delivery-authorization-fingerprint-mismatch", "/authorization/fingerprint", "Authorization fingerprint is stale."))
    if type(authorization.destination) is not ControlledLocalDestination or not _safe_basename(getattr(authorization.destination, "basename", None)):
        findings.append(_finding("invalid-delivery-destination", "/authorization/destination", "Destination requires one safe basename."))
    for field in ("identity", "attempt_identity", "evidence_identity", "authorization_time"):
        value = getattr(authorization, field, None)
        if type(value) is not str or not value or value != value.strip():
            findings.append(_finding("invalid-delivery-authorization-field", f"/authorization/{field}", "Stable nonempty text required."))
    if authorization.evidence_filename != "controlled-local-delivery-evidence.json":
        findings.append(_finding("invalid-delivery-evidence-filename", "/authorization/evidence_filename", "Evidence filename differs from profile."))
    try:
        parent = Path(authorization.destination.parent_directory)
        ledger = Path(authorization.commitment_ledger_directory)
        if not parent.is_absolute() or str(parent.resolve()) != str(parent) or parent.is_symlink() or not parent.is_dir(): raise ValueError
        if not ledger.is_absolute() or str(ledger.resolve()) != str(ledger) or ledger.is_symlink() or not ledger.is_dir(): raise ValueError
        ps=os.stat(parent,follow_symlinks=False); ls=os.stat(ledger,follow_symlinks=False)
        if (ps.st_dev,ps.st_ino)!=(authorization.destination.parent_device,authorization.destination.parent_inode): raise ValueError
        if (ls.st_dev,ls.st_ino)!=(authorization.commitment_ledger_device,authorization.commitment_ledger_inode): raise ValueError
        if ps.st_mode & 0o022 or ls.st_mode & 0o022: raise ValueError
        boundaries=[parent,ledger,Path(manifest_authorization.evidence_directory),Path(manifest_authorization.commitment_ledger_directory)]
        boundaries.extend(Path(item.source_path) for item in manifest_authorization.artifact_inventory)
        identities=[]
        for path in boundaries:
            resolved=path.resolve(strict=True); info=os.stat(resolved,follow_symlinks=False)
            identities.append((str(resolved),info.st_dev,info.st_ino))
        if len({(x[1],x[2]) for x in identities}) != len(identities): raise ValueError
    except Exception:
        findings.append(_finding("invalid-delivery-persistence-boundary", "/authorization/destination", "Parent or ledger is absent, writable by other principals, aliased, noncanonical, or unsafe."))
    try:
        expected_scope=_released_destination_scope(parent,authorization.destination.basename,ledger)
        if authorization.released_authority_scope != expected_scope: raise ValueError
        authorities = verified_release.bundle.one("PortablePresentationMaterialRecord").semantic["authorities"]
        exact = {"id": _AUTHORITY_ID, "owner_identity": _AUTHORITY_OWNER, "role": _AUTHORITY_ROLE, "scope": expected_scope}
        if [item for item in authorities if item.get("id") == _AUTHORITY_ID] != [exact]: raise ValueError
    except Exception:
        findings.append(_finding("unreleased-delivery-authority", "/release/authorities", "Exact independently released destination authority and contract are absent."))
    try:
        times=(_strict_utc(manifest_authorization.manifest_time),_strict_utc(authorization.authorization_time),
               _strict_utc(authorization.attempt_time),_strict_utc(authorization.completion_time))
        if not all(left < right for left,right in zip(times,times[1:])): raise ValueError
        if len({authorization.identity,authorization.attempt_identity,authorization.evidence_identity}) != 3: raise ValueError
    except Exception:
        findings.append(_finding("delivery-chronology-invalid","/authorization/authorization_time","Strict UTC times and distinct causal act identities are required in Manifest < authorization < attempt < completion order."))
    return _sorted(findings)


def _open_directory(path: Path) -> tuple[int, tuple[int, int]]:
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    info = os.fstat(fd)
    if not stat.S_ISDIR(info.st_mode): os.close(fd); raise ValueError("Not a directory")
    return fd, (info.st_dev, info.st_ino)


def _assert_path_attachment(path: Path, identity: tuple[int, int]) -> None:
    info = os.stat(path, follow_symlinks=False)
    if not stat.S_ISDIR(info.st_mode) or (info.st_dev, info.st_ino) != identity:
        raise ValueError("Canonical directory pathname attachment changed")


def _read_source(path: Path, expected: DeliveryInventoryItem) -> bytes:
    if not path.is_absolute() or str(path.resolve()) != str(path) or path.name != expected.logical_filename:
        raise ValueError("Source path is not exact canonical Manifest ordering.")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size != expected.byte_length: raise ValueError("Unsafe source")
        data = bytearray()
        while len(data) < before.st_size:
            chunk = os.read(fd, before.st_size - len(data))
            if not chunk: raise ValueError("Short source")
            data.extend(chunk)
        after = os.fstat(fd)
        attached=os.stat(path,follow_symlinks=False)
        key = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_nlink)
        if key(before) != key(after) or key(after) != key(attached) or hashlib.sha256(data).hexdigest() != expected.sha256: raise ValueError("Source changed")
        return bytes(data)
    finally: os.close(fd)


def _write_exclusive(directory_fd: int, name: str, data: bytes, mode: int = 0o600) -> None:
    if not _safe_basename(name): raise ValueError("Unsafe output name")
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), mode, dir_fd=directory_fd)
    try:
        view = memoryview(data)
        while view:
            count = os.write(fd, view)
            if count <= 0: raise OSError("No write progress")
            view = view[count:]
        os.fsync(fd)
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size != len(data): raise ValueError("Unsafe persisted file")
    finally: os.close(fd)


def _read_regular(directory_fd: int, name: str, maximum: int) -> bytes:
    fd = os.open(name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory_fd)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > maximum: raise ValueError("Unsafe file")
        data = bytearray()
        while len(data) < info.st_size:
            chunk = os.read(fd, info.st_size-len(data))
            if not chunk: raise ValueError("Truncated file")
            data.extend(chunk)
        after = os.fstat(fd)
        if (info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns): raise ValueError("File changed")
        return bytes(data)
    finally: os.close(fd)


def _ledger_name(authorization: ControlledLocalDeliveryAuthorization, suffix: str) -> str:
    return hashlib.sha256(authorization.identity.encode()).hexdigest() + "." + suffix


def _issuance_names(a: ControlledLocalDeliveryAuthorization) -> tuple[str, str]:
    return _ledger_name(a, "authorization.json"), _ledger_name(a, "authorization.commitment")


def _issuance_bytes(a: ControlledLocalDeliveryAuthorization) -> bytes:
    authorization_document = _canonical(asdict(a))
    evidence_name, commitment_name = _issuance_names(a)
    fingerprint = hashlib.sha256(_canonical({"contract":"briefforge:controlled-local-delivery-authorization-issuance:1.0.0",
        "authorization_sha256":hashlib.sha256(authorization_document).hexdigest(),
        "authorization_identity":a.identity,"evidence_filename":evidence_name,
        "commitment_filename":commitment_name,"parent_identity":[a.destination.parent_device,a.destination.parent_inode],
        "ledger_identity":[a.commitment_ledger_device,a.commitment_ledger_inode]})).hexdigest()
    return _canonical({"contract":"briefforge:controlled-local-delivery-authorization-issuance:1.0.0",
        "authorization":asdict(a),"issuance_fingerprint":fingerprint,
        "evidence_filename":evidence_name,"commitment_filename":commitment_name})


def _issuance_commitment_bytes(a: ControlledLocalDeliveryAuthorization, evidence: bytes) -> bytes:
    evidence_name, commitment_name = _issuance_names(a)
    doc = json.loads(evidence)
    return _canonical({"contract":"briefforge:controlled-local-delivery-authorization-commitment:1.0.0",
        "authorization_identity":a.identity,"authorization_fingerprint":a.fingerprint,
        "issuance_evidence_filename":evidence_name,"issuance_evidence_sha256":hashlib.sha256(evidence).hexdigest(),
        "issuance_fingerprint":doc["issuance_fingerprint"],"commitment_filename":commitment_name})


def _reload_issued_authorization(marker: object, ledger_fd: int | None = None) -> tuple[ControlledLocalDeliveryAuthorization, bytes]:
    if type(marker) is not VerifiedControlledLocalDeliveryAuthorization or marker._marker is not _VERIFIED:
        raise ValueError("A sealed issued authorization is required")
    a = marker.authorization
    owned = ledger_fd is None
    if owned:
        ledger_fd, identity = _open_directory(Path(a.commitment_ledger_directory))
        if identity != (a.commitment_ledger_device, a.commitment_ledger_inode):
            os.close(ledger_fd); raise ValueError("Issued ledger inode changed")
    assert ledger_fd is not None
    try:
        evidence = _read_regular(ledger_fd, marker.issuance_evidence_filename, _MAX_EVIDENCE)
        commitment = _read_regular(ledger_fd, marker.issuance_commitment_filename, 8192)
        if evidence != _issuance_bytes(a) or commitment != _issuance_commitment_bytes(a, evidence):
            raise ValueError("Authorization issuance mismatch")
        doc = json.loads(evidence)
        if (marker.issuance_evidence_sha256 != hashlib.sha256(evidence).hexdigest()
                or marker.issuance_fingerprint != doc["issuance_fingerprint"]
                or marker.issuance_evidence_filename != _issuance_names(a)[0]
                or marker.issuance_commitment_filename != _issuance_names(a)[1]):
            raise ValueError("Authorization marker mismatch")
        return a, evidence
    finally:
        if owned: os.close(ledger_fd)


def issue_controlled_local_delivery_authorization(*, manifest_evidence_path: Path,
        manifest_authorization: PublicationManifestAuthorization, evidence_snapshot: Any,
        verified_release: Any, lifecycle_scope: Any, declaration: Any, planning_authorization: Any,
        verified_plan: Any, invocation_authorization: Any, conformance_authorization: Any,
        artifact_paths: tuple[Path,...], authorization: ControlledLocalDeliveryAuthorization) -> VerifiedControlledLocalDeliveryAuthorization:
    """Trusted-process issuer for one exact released local-delivery act.

    Project authorization permits this trusted-process boundary; this API does
    not claim to authenticate a human or create a signature.
    """
    arguments = _manifest_kwargs(manifest_evidence_path=manifest_evidence_path, manifest_authorization=manifest_authorization,
        evidence_snapshot=evidence_snapshot, verified_release=verified_release, lifecycle_scope=lifecycle_scope,
        declaration=declaration, planning_authorization=planning_authorization, verified_plan=verified_plan,
        invocation_authorization=invocation_authorization, conformance_authorization=conformance_authorization,
        artifact_paths=artifact_paths)
    manifest = _reload_manifest(arguments)
    if verify_manifest_current_eligibility(manifest, lifecycle_scope=lifecycle_scope).blocked:
        raise ValueError("Manifest is not currently eligible")
    findings = _authorization_findings(authorization, manifest_authorization=manifest_authorization,
        verified_manifest=manifest, verified_release=verified_release, lifecycle_scope=lifecycle_scope)
    if findings:
        raise ValueError("Authorization invalid: " + ",".join(x.code for x in findings))
    parent_fd, parent_identity = _open_directory(Path(authorization.destination.parent_directory))
    ledger_fd, ledger_identity = _open_directory(Path(authorization.commitment_ledger_directory))
    try:
        if parent_identity != (authorization.destination.parent_device,authorization.destination.parent_inode): raise ValueError("Parent inode changed")
        if ledger_identity != (authorization.commitment_ledger_device,authorization.commitment_ledger_inode): raise ValueError("Ledger inode changed")
        evidence = _issuance_bytes(authorization); evidence_name, commitment_name = _issuance_names(authorization)
        _write_exclusive(ledger_fd,evidence_name,evidence); os.fsync(ledger_fd)
        try:
            _write_exclusive(ledger_fd,commitment_name,_issuance_commitment_bytes(authorization,evidence)); os.fsync(ledger_fd)
        except Exception as exc:
            try:
                commitment_bytes=_issuance_commitment_bytes(authorization,evidence)
                try:
                    if _read_regular(ledger_fd,commitment_name,_MAX_EVIDENCE) != commitment_bytes:
                        raise ValueError("Partial issuance commitment changed")
                    os.unlink(commitment_name,dir_fd=ledger_fd)
                except FileNotFoundError:
                    pass
                if _read_regular(ledger_fd,evidence_name,_MAX_EVIDENCE) != evidence:
                    raise ValueError("Partial issuance evidence changed")
                os.unlink(evidence_name,dir_fd=ledger_fd); os.fsync(ledger_fd)
                for removed in (commitment_name,evidence_name):
                    try: os.stat(removed,dir_fd=ledger_fd,follow_symlinks=False)
                    except FileNotFoundError: continue
                    raise ValueError("Partial issuance residue remains")
            except Exception as cleanup:
                raise ValueError("Authorization issuance rollback is indeterminate") from cleanup
            raise ValueError("Authorization issuance commitment failed and exact rollback was verified") from exc
        _assert_path_attachment(Path(authorization.destination.parent_directory),parent_identity)
        _assert_path_attachment(Path(authorization.commitment_ledger_directory),ledger_identity)
        doc=json.loads(evidence)
        return VerifiedControlledLocalDeliveryAuthorization._verified(_canonical(asdict(authorization)).decode(),evidence_name,
            hashlib.sha256(evidence).hexdigest(),doc["issuance_fingerprint"],commitment_name)
    finally:
        os.close(parent_fd); os.close(ledger_fd)


def _issuance_binding(marker: VerifiedControlledLocalDeliveryAuthorization, a: ControlledLocalDeliveryAuthorization) -> dict[str,str]:
    return {"authorization_issuance_evidence_path":str(Path(a.commitment_ledger_directory)/marker.issuance_evidence_filename),
            "authorization_issuance_evidence_sha256":marker.issuance_evidence_sha256,
            "authorization_issuance_fingerprint":marker.issuance_fingerprint,
            "authorization_issuance_commitment_path":str(Path(a.commitment_ledger_directory)/marker.issuance_commitment_filename)}


def _consumed_bytes(a: ControlledLocalDeliveryAuthorization, marker: VerifiedControlledLocalDeliveryAuthorization) -> bytes:
    return _canonical({"contract":"briefforge:controlled-local-delivery-consumed:1.0.0","authorization_identity":a.identity,"authorization_fingerprint":a.fingerprint,"attempt_identity":a.attempt_identity,"scope":"one-delivery-act",**_issuance_binding(marker,a)})


def _prepared_bytes(a: ControlledLocalDeliveryAuthorization, evidence: bytes) -> bytes:
    return _canonical({"contract":"briefforge:controlled-local-delivery-prepared:1.0.0","authorization_fingerprint":a.fingerprint,"evidence_sha256":hashlib.sha256(evidence).hexdigest(),"inventory_fingerprint":a.delivery_inventory_fingerprint,"destination":asdict(a.destination)})


def _completed_bytes(a: ControlledLocalDeliveryAuthorization, evidence: bytes, identity: tuple[int,int]) -> bytes:
    return _canonical({"contract":"briefforge:controlled-local-delivery-completed:1.0.0","authorization_fingerprint":a.fingerprint,"evidence_sha256":hashlib.sha256(evidence).hexdigest(),"prepared_sha256":hashlib.sha256(_prepared_bytes(a,evidence)).hexdigest(),"final_directory_device":identity[0],"final_directory_inode":identity[1]})


def _reserve_authorization(a: ControlledLocalDeliveryAuthorization,
                           marker: VerifiedControlledLocalDeliveryAuthorization, fd: int) -> None:
    _reload_issued_authorization(marker, fd)
    _write_exclusive(fd, _ledger_name(a,"consumed"), _consumed_bytes(a,marker)); os.fsync(fd)
    info=os.fstat(fd)
    if (info.st_dev,info.st_ino)!=(a.commitment_ledger_device,a.commitment_ledger_inode): raise ValueError("Ledger changed")


def _write_prepared_commitment(a: ControlledLocalDeliveryAuthorization, evidence: bytes, fd: int) -> None:
    _write_exclusive(fd,_ledger_name(a,"prepared"),_prepared_bytes(a,evidence)); os.fsync(fd)


def _write_completed_commitment(a: ControlledLocalDeliveryAuthorization, evidence: bytes, identity: tuple[int,int], fd: int) -> None:
    _write_exclusive(fd,_ledger_name(a,"completed"),_completed_bytes(a,evidence,identity)); os.fsync(fd)


def _atomic_install_noreplace(parent_fd: int, stage: str, destination: str) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    function = getattr(libc, "renameat2", None)
    if function is None: raise OSError(errno.ENOTSUP, "renameat2 unavailable; fail closed")
    function.argtypes = [ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint]
    function.restype = ctypes.c_int
    if function(parent_fd,stage.encode(),parent_fd,destination.encode(),1) != 0:
        value=ctypes.get_errno(); raise OSError(value,os.strerror(value))


class RollbackIndeterminate(RuntimeError):
    pass


def _stage_identity(parent_fd: int, stage: str) -> tuple[int,int]:
    info=os.stat(stage,dir_fd=parent_fd,follow_symlinks=False)
    if not stat.S_ISDIR(info.st_mode): raise RollbackIndeterminate("Stage is not a directory")
    return info.st_dev,info.st_ino


def _remove_stage(parent_fd: int, stage: str, names: tuple[str,...], expected_identity: tuple[int,int]) -> bool:
    if _stage_identity(parent_fd,stage) != expected_identity:
        raise RollbackIndeterminate("Stage inode changed")
    fd=os.open(stage,os.O_RDONLY|getattr(os,"O_DIRECTORY",0)|getattr(os,"O_NOFOLLOW",0),dir_fd=parent_fd)
    try:
        info=os.fstat(fd)
        actual=tuple(os.listdir(fd))
        if (info.st_dev,info.st_ino)!=expected_identity or not set(actual).issubset(names):
            raise RollbackIndeterminate("Stage inventory contains bytes not exactly owned")
        for name in actual: os.unlink(name,dir_fd=fd)
        if os.listdir(fd): raise RollbackIndeterminate("Stage cleanup left unknown entries")
        os.fsync(fd)
    except Exception as exc:
        if isinstance(exc,RollbackIndeterminate): raise
        raise RollbackIndeterminate("Stage cleanup failed") from exc
    finally: os.close(fd)
    try:
        os.rmdir(stage,dir_fd=parent_fd); os.fsync(parent_fd)
    except Exception as exc: raise RollbackIndeterminate("Stage removal durability failed") from exc
    try: os.stat(stage,dir_fd=parent_fd,follow_symlinks=False)
    except FileNotFoundError: return True
    raise RollbackIndeterminate("Stage remains attached")


def _delete_prepared(a: ControlledLocalDeliveryAuthorization, fd: int) -> bool:
    try:
        os.unlink(_ledger_name(a,"prepared"),dir_fd=fd); os.fsync(fd)
    except FileNotFoundError:
        return True
    except Exception as exc: raise RollbackIndeterminate("Prepared commitment cleanup failed") from exc
    return True


def _audit_links(a: ControlledLocalDeliveryAuthorization, marker: VerifiedControlledLocalDeliveryAuthorization,
                 source_paths: tuple[Path,...]) -> tuple[DeliveryAuditLink, ...]:
    final=str(Path(a.destination.parent_directory)/a.destination.basename)
    scope_node=hashlib.sha256(a.released_authority_scope.encode()).hexdigest()
    raw=[
        ("release-authorizes-scope",a.release_identity,scope_node),
        ("scope-authorizes-act",scope_node,a.identity),
        ("issuance-evidence-authorizes-act",str(Path(a.commitment_ledger_directory)/marker.issuance_evidence_filename),a.identity),
        ("issuance-commitment-binds-evidence",str(Path(a.commitment_ledger_directory)/marker.issuance_commitment_filename),marker.issuance_evidence_sha256),
        ("authorization-consumed-by",a.identity,_ledger_name(a,"consumed")),
        ("authorization-binds-manifest-record",a.identity,a.manifest_record_identity),
        ("manifest-record-verifies-as",a.manifest_record_identity,a.manifest_fingerprint),
        ("manifest-current-eligibility",a.manifest_fingerprint,a.lifecycle_inventory_digest),
        ("authorization-binds-destination",a.identity,final),
        ("implementation-executes-attempt",a.implementation_identity,a.attempt_identity),
        ("attempt-aggregates-verdict",a.attempt_identity,"exact-local-directory-delivery-completed"),
        ("attempt-produces-evidence",a.attempt_identity,a.evidence_identity),
        ("evidence-binds-prepared",a.evidence_identity,_ledger_name(a,"prepared")),
        ("evidence-binds-completed",a.evidence_identity,_ledger_name(a,"completed")),
    ]
    for item,source_path in zip(a.delivery_inventory,source_paths):
        raw.append(("manifest-admits-source-artifact",a.manifest_record_identity,item.identity))
        raw.append(("source-artifact-read-from",item.identity,str(source_path)))
        raw.append(("attempt-produces-destination-artifact",a.attempt_identity,
                    f"{final}/{item.logical_filename}#{item.sha256}"))
    result=[]
    for kind,source,target in raw:
        binding=hashlib.sha256(_canonical({"kind":kind,"source":source,"target":target})).hexdigest()
        result.append(DeliveryAuditLink(kind,source,target,binding))
    links=tuple(sorted(result))
    if len(links)!=len(set(links)): raise ValueError("duplicate audit link")
    return links


def _evidence(a: ControlledLocalDeliveryAuthorization, marker: VerifiedControlledLocalDeliveryAuthorization,
              source_paths: tuple[Path,...], identity: tuple[int,int]) -> ControlledLocalDeliveryEvidence:
    final=str(Path(a.destination.parent_directory)/a.destination.basename)
    provisional=ControlledLocalDeliveryEvidence(
        evidence_identity=a.evidence_identity,evidence_version=_VERSION,policy_identity=a.policy_identity,
        profile_identity=a.profile_identity,profile_version=a.profile_version,
        implementation_identity=a.implementation_identity,implementation_version=a.implementation_version,
        authorization_identity=a.identity,authorization_fingerprint=a.fingerprint,
        **_issuance_binding(marker,a),
        authority_identity=a.authority_identity,authority_owner=a.authority_owner,authority_role=a.authority_role,
        authorization_time=a.authorization_time,attempt_identity=a.attempt_identity,attempt_time=a.attempt_time,
        completion_time=a.completion_time,manifest_identity=a.manifest_identity,manifest_fingerprint=a.manifest_fingerprint,
        manifest_authorization_fingerprint=a.manifest_authorization_fingerprint,release_identity=a.release_identity,
        release_fingerprint=a.release_fingerprint,lifecycle_inventory_digest=a.lifecycle_inventory_digest,
        artifact_set_fingerprint=a.artifact_set_fingerprint,delivery_inventory_fingerprint=a.delivery_inventory_fingerprint,
        destination_parent=a.destination.parent_directory,destination_basename=a.destination.basename,
        destination_parent_device=a.destination.parent_device,destination_parent_inode=a.destination.parent_inode,
        commitment_ledger_directory=a.commitment_ledger_directory,
        commitment_ledger_device=a.commitment_ledger_device,commitment_ledger_inode=a.commitment_ledger_inode,
        final_directory_device=identity[0],final_directory_inode=identity[1],inventory=a.delivery_inventory,
        source_paths=tuple(str(p) for p in source_paths),
        delivered_paths=tuple(str(Path(final)/item.logical_filename) for item in a.delivery_inventory),
        released_authority_scope=a.released_authority_scope,audit_links=_audit_links(a,marker,source_paths),
        artifact_count=len(a.delivery_inventory),aggregate_byte_length=sum(x.byte_length for x in a.delivery_inventory),
        exclusions=a.exclusions,outcome="exact-local-directory-delivery-completed",fingerprint="")
    return ControlledLocalDeliveryEvidence(**{**asdict(provisional),"inventory":provisional.inventory,
                                               "source_paths":provisional.source_paths,"delivered_paths":provisional.delivered_paths,
                                               "audit_links":provisional.audit_links,"exclusions":provisional.exclusions,
                                               "fingerprint":compute_delivery_evidence_fingerprint(provisional)})


def _evidence_from_document(document: object) -> ControlledLocalDeliveryEvidence:
    if type(document) is not dict: raise ValueError("Evidence envelope malformed")
    value=dict(document)
    value["inventory"]=tuple(DeliveryInventoryItem(**item) for item in value["inventory"])
    value["audit_links"]=tuple(DeliveryAuditLink(**item) for item in value["audit_links"])
    for field in ("source_paths","delivered_paths","exclusions"): value[field]=tuple(value[field])
    return ControlledLocalDeliveryEvidence(**value)


def _blocked(code: str, location: str, message: str) -> ControlledLocalDeliveryResult:
    return ControlledLocalDeliveryResult((_finding(code,location,message),),"blocked",None)


def _verify_inventory_transaction(directory_fd: int, inventory: tuple[DeliveryInventoryItem,...],
                                  evidence_filename: str, evidence_bytes: bytes,
                                  expected_identity: tuple[int,int]) -> None:
    info=os.fstat(directory_fd)
    if not stat.S_ISDIR(info.st_mode) or (info.st_dev,info.st_ino)!=expected_identity: raise ValueError("Directory inode changed")
    expected_names=[x.logical_filename for x in inventory]+[evidence_filename]
    if sorted(os.listdir(directory_fd))!=sorted(expected_names): raise ValueError("Inventory has omissions or extras")
    for item in inventory:
        data=_read_regular(directory_fd,item.logical_filename,_MAX_ARTIFACT)
        if len(data)!=item.byte_length or hashlib.sha256(data).hexdigest()!=item.sha256: raise ValueError("Inventory bytes differ")
    if _read_regular(directory_fd,evidence_filename,_MAX_EVIDENCE)!=evidence_bytes: raise ValueError("Evidence bytes differ")


def _execute_inventory_transaction(stage_fd: int, inventory: tuple[DeliveryInventoryItem,...],
                                   contents: tuple[bytes,...], evidence_filename: str,
                                   evidence_bytes: bytes, stage_identity: tuple[int,int]) -> None:
    """Bounded generic transaction mechanics for an already-governed inventory."""
    findings=validate_delivery_inventory(inventory)
    if findings or len(contents)!=len(inventory): raise ValueError("Invalid generic transaction inputs")
    for item,data in zip(inventory,contents):
        if len(data)!=item.byte_length or hashlib.sha256(data).hexdigest()!=item.sha256: raise ValueError("Input bytes differ")
        _write_exclusive(stage_fd,item.logical_filename,data,0o600)
    _write_exclusive(stage_fd,evidence_filename,evidence_bytes)
    os.fsync(stage_fd)
    _verify_inventory_transaction(stage_fd,inventory,evidence_filename,evidence_bytes,stage_identity)


def _after_final_open_before_return() -> None:
    """Fixed race-test seam; production intentionally does nothing."""


def perform_controlled_local_delivery(*, manifest_evidence_path: Path,
        manifest_authorization: PublicationManifestAuthorization, evidence_snapshot: Any,
        verified_release: Any, lifecycle_scope: Any, declaration: Any, planning_authorization: Any,
        verified_plan: Any, invocation_authorization: Any, conformance_authorization: Any,
        artifact_paths: tuple[Path,...], authorization: VerifiedControlledLocalDeliveryAuthorization) -> ControlledLocalDeliveryResult:
    """Consume one exact persisted issuance, stage exact bytes, and atomically install."""
    try:
        issued, _ = _reload_issued_authorization(authorization)
    except Exception:
        return _blocked("delivery-authorization-not-issued","/authorization","Exact persisted authorization issuance and commitment are required.")
    a=issued
    arguments=_manifest_kwargs(manifest_evidence_path=manifest_evidence_path,manifest_authorization=manifest_authorization,
        evidence_snapshot=evidence_snapshot,verified_release=verified_release,lifecycle_scope=lifecycle_scope,
        declaration=declaration,planning_authorization=planning_authorization,verified_plan=verified_plan,
        invocation_authorization=invocation_authorization,conformance_authorization=conformance_authorization,
        artifact_paths=artifact_paths)
    try:
        manifest=_reload_manifest(arguments)
        if verify_manifest_current_eligibility(manifest,lifecycle_scope=lifecycle_scope).blocked:
            return _blocked("delivery-manifest-ineligible","/lifecycle","Manifest is not currently eligible.")
        findings=_authorization_findings(a,manifest_authorization=manifest_authorization,verified_manifest=manifest,
                                         verified_release=verified_release,lifecycle_scope=lifecycle_scope)
    except Exception:
        return _blocked("persisted-manifest-invalid","/manifest","Persisted Manifest or upstream chain failed independent verification.")
    if findings: return ControlledLocalDeliveryResult(findings,"blocked",None)
    parent_fd=ledger_fd=-1; stage_fd=-1; stage=""; stage_created=False; renamed=False
    stage_identity=(-1,-1); evidence_bytes=b""
    staged_names=tuple(item.logical_filename for item in a.delivery_inventory)+(a.evidence_filename,)
    try:
        parent_fd,parent_identity=_open_directory(Path(a.destination.parent_directory))
        ledger_fd,ledger_identity=_open_directory(Path(a.commitment_ledger_directory))
        if parent_identity!=(a.destination.parent_device,a.destination.parent_inode) or ledger_identity!=(a.commitment_ledger_device,a.commitment_ledger_inode): raise ValueError("Released inode changed")
        _reload_issued_authorization(authorization,ledger_fd)
        try: _reserve_authorization(a,authorization,ledger_fd)
        except FileExistsError: return _blocked("delivery-authorization-consumed","/authorization/identity","Authorization identity has already been consumed.")
        if type(artifact_paths) is not tuple or len(artifact_paths)!=len(a.delivery_inventory):
            return _blocked("delivery-source-closure-mismatch","/artifact_paths","Source path count differs from Manifest.")
        try: contents=tuple(_read_source(Path(path),item) for path,item in zip(artifact_paths,a.delivery_inventory))
        except Exception: return _blocked("delivery-source-invalid","/artifact_paths","A source is unsafe, changed, linked, or differs from Manifest.")
        destination_key=unicodedata.normalize("NFC",a.destination.basename).casefold()
        if any(unicodedata.normalize("NFC",name).casefold()==destination_key for name in os.listdir(parent_fd)): raise FileExistsError("Destination collision")
        stage="."+a.destination.basename+"."+hashlib.sha256(a.attempt_identity.encode()).hexdigest()[:20]+".stage"
        os.mkdir(stage,0o700,dir_fd=parent_fd); stage_created=True
        stage_fd=os.open(stage,os.O_RDONLY|getattr(os,"O_DIRECTORY",0)|getattr(os,"O_NOFOLLOW",0),dir_fd=parent_fd)
        stage_info=os.fstat(stage_fd); stage_identity=(stage_info.st_dev,stage_info.st_ino)
        evidence=_evidence(a,authorization,tuple(Path(p) for p in artifact_paths),stage_identity)
        evidence_bytes=_canonical(asdict(evidence))
        _execute_inventory_transaction(stage_fd,a.delivery_inventory,contents,a.evidence_filename,evidence_bytes,stage_identity)
        os.close(stage_fd); stage_fd=-1
        _write_prepared_commitment(a,evidence_bytes,ledger_fd)
        second=_reload_manifest(arguments)
        if verify_manifest_current_eligibility(second,lifecycle_scope=lifecycle_scope).blocked: raise PermissionError("eligibility changed")
        if _stage_identity(parent_fd,stage)!=stage_identity: raise ValueError("Stage reattached")
        check_fd=os.open(stage,os.O_RDONLY|getattr(os,"O_DIRECTORY",0)|getattr(os,"O_NOFOLLOW",0),dir_fd=parent_fd)
        try: _verify_inventory_transaction(check_fd,a.delivery_inventory,a.evidence_filename,evidence_bytes,stage_identity)
        finally: os.close(check_fd)
        _assert_path_attachment(Path(a.destination.parent_directory),parent_identity)
        _assert_path_attachment(Path(a.commitment_ledger_directory),ledger_identity)
        _atomic_install_noreplace(parent_fd,stage,a.destination.basename); renamed=True
        if _stage_identity(parent_fd,a.destination.basename)!=stage_identity: raise ValueError("Final inode mismatch")
        try: os.fsync(parent_fd)
        except Exception as exc:
            try:
                _atomic_install_noreplace(parent_fd,a.destination.basename,stage); renamed=False
                os.fsync(parent_fd); _remove_stage(parent_fd,stage,staged_names,stage_identity); stage_created=False
                _delete_prepared(a,ledger_fd)
            except Exception as rollback: raise RollbackIndeterminate("Post-rename parent fsync rollback indeterminate") from rollback
            raise OSError("Parent fsync failed; rollback verified") from exc
        _write_completed_commitment(a,evidence_bytes,stage_identity,ledger_fd)
        delivery_arguments=dict(arguments); delivery_arguments["manifest_authorization"]=delivery_arguments.pop("authorization")
        verified=verify_persisted_controlled_local_delivery(**delivery_arguments,authorization=authorization)
        return ControlledLocalDeliveryResult((),"completed",verified)
    except PermissionError:
        try:
            if stage_created and not renamed: _remove_stage(parent_fd,stage,staged_names,stage_identity); stage_created=False
            _delete_prepared(a,ledger_fd)
        except Exception: return ControlledLocalDeliveryResult((_finding("delivery-rollback-indeterminate","/destination","Eligibility rollback could not be proven."),),"rollback-indeterminate",None)
        return ControlledLocalDeliveryResult((_finding("delivery-no-longer-eligible","/lifecycle","Manifest eligibility changed immediately before commit."),),"rollback-verified",None)
    except RollbackIndeterminate:
        return ControlledLocalDeliveryResult((_finding("delivery-rollback-indeterminate","/destination","Exact rollback could not be proven."),),"rollback-indeterminate",None)
    except Exception:
        if renamed:
            return ControlledLocalDeliveryResult((_finding("delivery-completion-pending","/destination","Exact destination is installed but completion is pending reconciliation."),),"completion-pending",None)
        try:
            if stage_created: _remove_stage(parent_fd,stage,staged_names,stage_identity); stage_created=False
            if ledger_fd>=0: _delete_prepared(a,ledger_fd)
        except Exception:
            return ControlledLocalDeliveryResult((_finding("delivery-rollback-indeterminate","/destination","Exact rollback could not be proven."),),"rollback-indeterminate",None)
        return ControlledLocalDeliveryResult((_finding("delivery-transaction-failed","/destination","Transaction failed and exact rollback was verified."),),"rollback-verified",None)
    finally:
        if stage_fd>=0: os.close(stage_fd)
        if parent_fd>=0: os.close(parent_fd)
        if ledger_fd>=0: os.close(ledger_fd)


def verify_persisted_controlled_local_delivery(*, manifest_evidence_path: Path,
        manifest_authorization: PublicationManifestAuthorization, evidence_snapshot: Any,
        verified_release: Any, lifecycle_scope: Any, declaration: Any, planning_authorization: Any,
        verified_plan: Any, invocation_authorization: Any, conformance_authorization: Any,
        artifact_paths: tuple[Path,...], authorization: VerifiedControlledLocalDeliveryAuthorization) -> VerifiedControlledLocalDelivery:
    """Verify the exact historical delivery using its original lifecycle scope."""
    arguments=_manifest_kwargs(manifest_evidence_path=manifest_evidence_path,manifest_authorization=manifest_authorization,
        evidence_snapshot=evidence_snapshot,verified_release=verified_release,lifecycle_scope=lifecycle_scope,
        declaration=declaration,planning_authorization=planning_authorization,verified_plan=verified_plan,
        invocation_authorization=invocation_authorization,conformance_authorization=conformance_authorization,
        artifact_paths=artifact_paths)
    a,_=_reload_issued_authorization(authorization)
    manifest=_reload_manifest(arguments)
    # Deliberately no current-eligibility call: this proves a durable historical fact.
    if _authorization_findings(a,manifest_authorization=manifest_authorization,verified_manifest=manifest,
                               verified_release=verified_release,lifecycle_scope=lifecycle_scope): raise ValueError("Authorization stale")
    parent_fd,parent_identity=_open_directory(Path(a.destination.parent_directory))
    ledger_fd,ledger_identity=_open_directory(Path(a.commitment_ledger_directory))
    final_fd=-1
    try:
        if parent_identity!=(a.destination.parent_device,a.destination.parent_inode) or ledger_identity!=(a.commitment_ledger_device,a.commitment_ledger_inode): raise ValueError("Released inode changed")
        _reload_issued_authorization(authorization,ledger_fd)
        final_fd=os.open(a.destination.basename,os.O_RDONLY|getattr(os,"O_DIRECTORY",0)|getattr(os,"O_NOFOLLOW",0),dir_fd=parent_fd)
        final_info=os.fstat(final_fd); final_identity=(final_info.st_dev,final_info.st_ino)
        evidence_bytes=_read_regular(final_fd,a.evidence_filename,_MAX_EVIDENCE)
        evidence=_evidence_from_document(json.loads(evidence_bytes.decode("utf-8")))
        if evidence_bytes!=_canonical(asdict(evidence)) or evidence.fingerprint!=compute_delivery_evidence_fingerprint(evidence): raise ValueError("Evidence invalid")
        expected=_evidence(a,authorization,tuple(Path(p) for p in artifact_paths),final_identity)
        if evidence!=expected: raise ValueError("Evidence differs from independent reproduction")
        _verify_inventory_transaction(final_fd,a.delivery_inventory,a.evidence_filename,evidence_bytes,final_identity)
        try:
            consumed=_read_regular(ledger_fd,_ledger_name(a,"consumed"),8192)
            prepared=_read_regular(ledger_fd,_ledger_name(a,"prepared"),8192)
            completed=_read_regular(ledger_fd,_ledger_name(a,"completed"),8192)
        except OSError as exc: raise ValueError("Required delivery commitment is missing or unreadable") from exc
        if consumed!=_consumed_bytes(a,authorization) or prepared!=_prepared_bytes(a,evidence_bytes) or completed!=_completed_bytes(a,evidence_bytes,final_identity): raise ValueError("Commitment mismatch")
        pi,li=os.fstat(parent_fd),os.fstat(ledger_fd)
        if (pi.st_dev,pi.st_ino)!=parent_identity or (li.st_dev,li.st_ino)!=ledger_identity: raise ValueError("Directory identity changed")
        _after_final_open_before_return()
        attached=os.stat(a.destination.basename,dir_fd=parent_fd,follow_symlinks=False)
        if not stat.S_ISDIR(attached.st_mode) or (attached.st_dev,attached.st_ino)!=final_identity: raise ValueError("Final pathname reattached")
        _assert_path_attachment(Path(a.destination.parent_directory),parent_identity)
        _assert_path_attachment(Path(a.commitment_ledger_directory),ledger_identity)
        return VerifiedControlledLocalDelivery._verified(evidence_bytes.decode("utf-8"),evidence.fingerprint)
    finally:
        if final_fd>=0: os.close(final_fd)
        os.close(parent_fd); os.close(ledger_fd)


def verify_controlled_local_delivery_current_eligibility(verified_delivery: VerifiedControlledLocalDelivery, *,
        manifest_evidence_path: Path, manifest_authorization: PublicationManifestAuthorization,
        evidence_snapshot: Any, verified_release: Any, historical_lifecycle_scope: Any,
        current_lifecycle_scope: Any, declaration: Any,
        planning_authorization: Any, verified_plan: Any, invocation_authorization: Any,
        conformance_authorization: Any, artifact_paths: tuple[Path,...]) -> ControlledLocalDeliveryResult:
    """Evaluate current eligibility separately, without rewriting historical delivery."""
    if type(verified_delivery) is not VerifiedControlledLocalDelivery or verified_delivery._marker is not _VERIFIED:
        return _blocked("historical-delivery-unverified","/delivery","An independently verified historical delivery is required.")
    arguments=_manifest_kwargs(manifest_evidence_path=manifest_evidence_path,manifest_authorization=manifest_authorization,
        evidence_snapshot=evidence_snapshot,verified_release=verified_release,lifecycle_scope=historical_lifecycle_scope,
        declaration=declaration,planning_authorization=planning_authorization,verified_plan=verified_plan,
        invocation_authorization=invocation_authorization,conformance_authorization=conformance_authorization,
        artifact_paths=artifact_paths)
    try:
        manifest=_reload_manifest(arguments)
        historical=verified_delivery.evidence
        exact_bindings=(
            historical.manifest_identity == manifest_authorization.manifest_identity,
            historical.manifest_fingerprint == manifest.fingerprint.digest,
            historical.manifest_authorization_fingerprint == manifest_authorization.fingerprint,
            historical.release_identity == manifest_authorization.release_identity,
            historical.release_fingerprint == manifest_authorization.release_fingerprint,
            historical.artifact_set_fingerprint == manifest_authorization.artifact_set_fingerprint,
        )
        if not all(exact_bindings):
            return _blocked("current-eligibility-cross-authority-mismatch","/manifest",
                            "Current eligibility inputs do not bind the historical delivery Manifest and artifact set.")
        result=verify_manifest_current_eligibility(manifest,lifecycle_scope=current_lifecycle_scope)
    except Exception: return _blocked("current-eligibility-verification-failed","/lifecycle","Current Manifest/lifecycle verification failed.")
    if result.blocked: return _blocked("delivery-manifest-ineligible","/lifecycle","Historical delivery's Manifest is no longer currently eligible.")
    return ControlledLocalDeliveryResult((),"completed",verified_delivery)


def reconcile_pending_controlled_local_delivery(*, manifest_evidence_path: Path,
        manifest_authorization: PublicationManifestAuthorization, evidence_snapshot: Any,
        verified_release: Any, lifecycle_scope: Any, declaration: Any, planning_authorization: Any,
        verified_plan: Any, invocation_authorization: Any, conformance_authorization: Any,
        artifact_paths: tuple[Path,...], authorization: VerifiedControlledLocalDeliveryAuthorization) -> ControlledLocalDeliveryResult:
    """Complete only a reproducible post-rename transaction; never issue or copy bytes."""
    arguments=_manifest_kwargs(manifest_evidence_path=manifest_evidence_path,manifest_authorization=manifest_authorization,
        evidence_snapshot=evidence_snapshot,verified_release=verified_release,lifecycle_scope=lifecycle_scope,
        declaration=declaration,planning_authorization=planning_authorization,verified_plan=verified_plan,
        invocation_authorization=invocation_authorization,conformance_authorization=conformance_authorization,
        artifact_paths=artifact_paths)
    parent_fd=ledger_fd=final_fd=-1
    try:
        a,_=_reload_issued_authorization(authorization)
        manifest=_reload_manifest(arguments)
        if _authorization_findings(a,manifest_authorization=manifest_authorization,verified_manifest=manifest,
                verified_release=verified_release,lifecycle_scope=lifecycle_scope): raise ValueError("Authorization stale")
        parent_fd,parent_identity=_open_directory(Path(a.destination.parent_directory)); ledger_fd,ledger_identity=_open_directory(Path(a.commitment_ledger_directory))
        if parent_identity!=(a.destination.parent_device,a.destination.parent_inode) or ledger_identity!=(a.commitment_ledger_device,a.commitment_ledger_inode): raise ValueError("Released inode changed")
        _reload_issued_authorization(authorization,ledger_fd)
        final_fd=os.open(a.destination.basename,os.O_RDONLY|getattr(os,"O_DIRECTORY",0)|getattr(os,"O_NOFOLLOW",0),dir_fd=parent_fd)
        info=os.fstat(final_fd); identity=(info.st_dev,info.st_ino)
        evidence_bytes=_read_regular(final_fd,a.evidence_filename,_MAX_EVIDENCE)
        evidence=_evidence_from_document(json.loads(evidence_bytes)); expected=_evidence(a,authorization,tuple(Path(p) for p in artifact_paths),identity)
        if evidence_bytes!=_canonical(asdict(evidence)) or evidence!=expected: raise ValueError("Final evidence mismatch")
        _verify_inventory_transaction(final_fd,a.delivery_inventory,a.evidence_filename,evidence_bytes,identity)
        if _read_regular(ledger_fd,_ledger_name(a,"consumed"),8192)!=_consumed_bytes(a,authorization): raise ValueError("Consumption mismatch")
        if _read_regular(ledger_fd,_ledger_name(a,"prepared"),8192)!=_prepared_bytes(a,evidence_bytes): raise ValueError("Prepared mismatch")
        try: _read_regular(ledger_fd,_ledger_name(a,"completed"),8192)
        except FileNotFoundError: pass
        else: raise ValueError("Completion already exists or is ambiguous")
        attached=os.stat(a.destination.basename,dir_fd=parent_fd,follow_symlinks=False)
        if (attached.st_dev,attached.st_ino)!=identity: raise ValueError("Final reattached")
        _assert_path_attachment(Path(a.destination.parent_directory),parent_identity); _assert_path_attachment(Path(a.commitment_ledger_directory),ledger_identity)
        _write_completed_commitment(a,evidence_bytes,identity,ledger_fd)
        delivery_arguments=dict(arguments); delivery_arguments["manifest_authorization"]=delivery_arguments.pop("authorization")
        verified=verify_persisted_controlled_local_delivery(**delivery_arguments,authorization=authorization)
        return ControlledLocalDeliveryResult((),"completed",verified)
    except Exception:
        return _blocked("delivery-reconciliation-blocked","/destination","Pending completion facts are missing, altered, alien, or ambiguous.")
    finally:
        if final_fd>=0: os.close(final_fd)
        if parent_fd>=0: os.close(parent_fd)
        if ledger_fd>=0: os.close(ledger_fd)
