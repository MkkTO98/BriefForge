"""Fixed, finite IPv4 loopback HTTP deployment companion.

The module proves only one bounded local serving interval.  It does not confer
public, browser, reader, editorial, production, or continuing-availability
status and does not extend BCRP.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import socket
import stat
import threading
import time
from typing import Any

from .publication_distribution_delivery import (
    VerifiedControlledLocalDelivery, VerifiedControlledLocalDeliveryAuthorization,
    verify_persisted_controlled_local_delivery,
    verify_controlled_local_delivery_current_eligibility,
)

_POLICY="briefforge-bounded-loopback-deployment-policy:1.0.0"
_PROFILE="briefforge-bounded-loopback-static-http-profile:1.0.0"
_IMPLEMENTATION="briefforge.bounded_loopback_deployment"
_VERSION="1.0.0"
_AUTHORITY="authority:briefforge-bounded-loopback-deployment"
_OWNER="project:BriefForge"
_ROLE="bounded-loopback-deployment-authority"
_EXCLUSIONS=("public-internet","continuing-availability","browser","javascript","accessibility","reader","editorial","production","atlasforge-authority","hostile-process-authentication")
_MAX_REQUEST=8192
_MAX_BODY=100_000_000
_TOKEN=object()

@dataclass(frozen=True)
class DeploymentTarget:
    address: str
    port: int
    origin: str

@dataclass(frozen=True)
class DeploymentRouteItem:
    path: str
    logical_filename: str
    media_type: str

@dataclass(frozen=True, order=True)
class DeploymentFinding:
    code: str
    location: str
    message: str

@dataclass(frozen=True, order=True)
class DeploymentAuditLink:
    kind: str
    source_identity: str
    target_identity: str
    binding_fingerprint: str

@dataclass(frozen=True)
class LoopbackDeploymentAuthorization:
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
    delivery_fingerprint: str
    release_identity: str
    release_fingerprint: str
    lifecycle_inventory_digest: str
    target: DeploymentTarget
    routes: tuple[DeploymentRouteItem,...]
    attempt_identity: str
    evidence_identity: str
    implementation_identity: str
    implementation_version: str
    ledger_directory: str
    ledger_device: int
    ledger_inode: int
    request_budget: int
    time_budget_seconds: int
    exclusions: tuple[str,...]
    released_authority_scope: str
    fingerprint: str

@dataclass(frozen=True)
class DeploymentAuthorizationIssuanceEvidence:
    authorization_identity: str
    authorization_fingerprint: str
    delivery_fingerprint: str
    release_fingerprint: str
    evidence_filename: str
    commitment_filename: str
    fingerprint: str

@dataclass(frozen=True)
class DeploymentConsumption:
    authorization_identity: str
    authorization_fingerprint: str
    attempt_identity: str
    issuance_fingerprint: str

@dataclass(frozen=True)
class LoopbackDeploymentEvidence:
    evidence_identity: str
    evidence_version: str
    policy_identity: str
    profile_identity: str
    implementation_identity: str
    implementation_version: str
    authorization_identity: str
    authorization_fingerprint: str
    issuance_fingerprint: str
    delivery_fingerprint: str
    release_identity: str
    release_fingerprint: str
    lifecycle_inventory_digest: str
    target: DeploymentTarget
    routes: tuple[DeploymentRouteItem,...]
    route_sha256: tuple[str,...]
    route_lengths: tuple[int,...]
    service_instance_identity: str
    service_token_digest: str
    attempt_identity: str
    authorization_time: str
    attempt_time: str
    completion_time: str
    bounded_interval_start: str
    bounded_interval_end: str
    request_budget: int
    time_budget_seconds: int
    ledger_directory: str
    ledger_device: int
    ledger_inode: int
    evidence_path: str
    commitment_path: str
    exclusions: tuple[str,...]
    outcome: str
    audit_links: tuple[DeploymentAuditLink,...]
    fingerprint: str

@dataclass(frozen=True, init=False)
class VerifiedLoopbackDeploymentAuthorization:
    _document: str
    issuance_filename: str
    commitment_filename: str
    issuance_fingerprint: str
    _marker: object
    def __new__(cls): raise TypeError("sealed type")
    @classmethod
    def _make(cls, document, issuance, commitment, fingerprint, marker):
        if marker is not _TOKEN: raise TypeError("private constructor")
        value=object.__new__(cls)
        for k,v in (("_document",document),("issuance_filename",issuance),("commitment_filename",commitment),("issuance_fingerprint",fingerprint),("_marker",_TOKEN)): object.__setattr__(value,k,v)
        return value
    @property
    def authorization(self): return _authorization(json.loads(self._document))

@dataclass(frozen=True, init=False)
class VerifiedLoopbackDeployment:
    _document: str
    fingerprint: str
    _marker: object
    def __new__(cls): raise TypeError("sealed type")
    @classmethod
    def _make(cls, document, fingerprint, marker):
        if marker is not _TOKEN: raise TypeError("private constructor")
        value=object.__new__(cls)
        for k,v in (("_document",document),("fingerprint",fingerprint),("_marker",_TOKEN)): object.__setattr__(value,k,v)
        return value
    @property
    def evidence(self): return _evidence(json.loads(self._document))

@dataclass(frozen=True)
class LoopbackDeploymentResult:
    findings: tuple[DeploymentFinding,...]
    state: str
    verified: VerifiedLoopbackDeployment|None
    service: Any=None
    @property
    def blocked(self): return self.state != "active" and self.state != "shutdown-verified"

@dataclass(frozen=True)
class DeploymentStopEvidence:
    evidence_version: str
    authorization_identity: str
    authorization_fingerprint: str
    deployment_fingerprint: str
    target: DeploymentTarget
    service_instance_identity: str
    service_token_digest: str
    state: str
    stop_requested: bool
    thread_joined: bool
    socket_closed: bool
    residue_probe: str
    stopped_at: str
    ledger_directory: str
    ledger_device: int
    ledger_inode: int
    exclusions: tuple[str,...]
    fingerprint: str

@dataclass(frozen=True, init=False)
class RunningLoopbackDeployment:
    """Unpersisted cooperative same-process continuity receipt."""
    _listener: Any
    _thread: threading.Thread
    _stop_event: threading.Event
    _verified: VerifiedLoopbackDeployment
    _target: DeploymentTarget
    _service_token: bytes
    _marker: object
    def __new__(cls): raise TypeError("sealed type")
    @classmethod
    def _make(cls,listener,thread,stop_event,verified,target,token,marker):
        if marker is not _TOKEN: raise TypeError("private constructor")
        value=object.__new__(cls)
        for k,v in (("_listener",listener),("_thread",thread),("_stop_event",stop_event),("_verified",verified),("_target",target),("_service_token",token),("_marker",_TOKEN)): object.__setattr__(value,k,v)
        return value

def require_active_running_deployment(receipt, verified=None):
    """Validate a sealed receipt immediately before a cooperative local request."""
    if type(receipt) is not RunningLoopbackDeployment or getattr(receipt,"_marker",None) is not _TOKEN or type(getattr(receipt,"_service_token",None)) is not bytes or len(receipt._service_token)!=32:
        raise ValueError("sealed active deployment receipt required")
    if verified is not None and receipt._verified.fingerprint!=verified.fingerprint: raise ValueError("active receipt deployment mismatch")
    listener=receipt._listener
    if receipt._stop_event.is_set() or not receipt._thread.is_alive() or listener.fileno()<0: raise ValueError("deployment not active")
    if listener.getsockname()!=(receipt._target.address,receipt._target.port): raise ValueError("listener attachment changed")
    if verified is not None and hashlib.sha256(receipt._service_token).hexdigest()!=verified.evidence.service_token_digest: raise ValueError("service token mismatch")
    return receipt


def _canonical(value: Any)->bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()

def _digest(value: Any)->str: return hashlib.sha256(_canonical(value)).hexdigest()

def _name(identity: str, suffix: str)->str: return hashlib.sha256(identity.encode()).hexdigest()+"."+suffix

def _valid_target(target: DeploymentTarget)->bool:
    return type(target) is DeploymentTarget and target.address=="127.0.0.1" and type(target.port) is int and 1024<=target.port<=65535 and target.origin==f"http://127.0.0.1:{target.port}"

def _valid_routes(routes: tuple[DeploymentRouteItem,...])->bool:
    if type(routes) is not tuple or not routes or any(type(x) is not DeploymentRouteItem for x in routes): return False
    paths=[]; names=[]
    media=re.compile(r"^[A-Za-z0-9!#$&^_.+-]+/[A-Za-z0-9!#$&^_.+-]+$",re.ASCII)
    for item in routes:
        segments=item.path.split("/") if type(item.path) is str else ()
        if (type(item.path) is not str or not item.path.startswith("/") or item.path.startswith("//") or item.path.endswith("/")
            or "//" in item.path or any(x in item.path for x in ("?","#","%","\\")) or any(x in (".","..") for x in segments)
            or not item.path.isascii() or any(ord(c)<0x21 or ord(c)>0x7e for c in item.path)
            or type(item.logical_filename) is not str or not item.logical_filename or Path(item.logical_filename).name!=item.logical_filename
            or "/" in item.logical_filename or "\\" in item.logical_filename or not item.logical_filename.isascii()
            or any(ord(c)<0x21 or ord(c)>0x7e for c in item.logical_filename)
            or type(item.media_type) is not str or media.fullmatch(item.media_type) is None): return False
        paths.append(item.path); names.append(item.logical_filename)
    return len(paths)==len(set(paths)) and len(names)==len(set(names))

def validate_bounded_route_mechanics(routes: tuple[DeploymentRouteItem,...], request_budget: int):
    """Validate transport closure only; this function grants no Manifest authority."""
    if not _valid_routes(routes) or type(request_budget) is not int or request_budget < len(routes) or request_budget > 64:
        raise ValueError("route closure or request budget invalid")
    return routes

def _safe_ledger(path: Path)->tuple[int,int]:
    if not path.is_absolute(): path=path.resolve()
    if str(path.resolve())!=str(path) or path.is_symlink() or not path.is_dir(): raise ValueError("unsafe ledger")
    info=os.stat(path,follow_symlinks=False)
    if info.st_mode & 0o022: raise ValueError("writable ledger")
    return info.st_dev,info.st_ino

def _require_ledger_attachment(a: LoopbackDeploymentAuthorization)->Path:
    ledger=Path(a.ledger_directory)
    if _safe_ledger(ledger)!=(a.ledger_device,a.ledger_inode): raise ValueError("deployment ledger changed")
    return ledger

def _released_loopback_deployment_scope(target: DeploymentTarget, routes: tuple[DeploymentRouteItem,...], ledger: Path)->str:
    if not _valid_target(target) or not _valid_routes(routes): raise ValueError("invalid fixed profile")
    ledger=Path(ledger); identity=_safe_ledger(ledger)
    return _canonical({"policy":_POLICY,"profile":_PROFILE,"implementation":_IMPLEMENTATION,"version":_VERSION,
        "transport":{"family":"AF_INET","type":"SOCK_STREAM","scheme":"http","address":target.address,"port":target.port,"origin":target.origin},
        "routes":[asdict(x) for x in routes],"ledger":{"canonical_path":str(ledger.resolve()),"device":identity[0],"inode":identity[1]},
        "contract":{"one_act":True,"bounded":True,"no_runtime_fallback":True,"public_binding":False}}).decode()

def compute_deployment_authorization_fingerprint(a: LoopbackDeploymentAuthorization)->str:
    if type(a) is not LoopbackDeploymentAuthorization: raise TypeError("exact authorization required")
    doc=asdict(a); doc.pop("fingerprint",None); return _digest(doc)

def _authorization(doc):
    value=dict(doc); value["target"]=DeploymentTarget(**value["target"]); value["routes"]=tuple(DeploymentRouteItem(**x) for x in value["routes"]); value["exclusions"]=tuple(value["exclusions"])
    return LoopbackDeploymentAuthorization(**value)

def compute_deployment_evidence_fingerprint(e: LoopbackDeploymentEvidence)->str:
    doc=asdict(e); doc.pop("fingerprint",None); return _digest(doc)

def _evidence(doc):
    value=dict(doc); value["target"]=DeploymentTarget(**value["target"]); value["routes"]=tuple(DeploymentRouteItem(**x) for x in value["routes"])
    value["route_sha256"]=tuple(value["route_sha256"]); value["route_lengths"]=tuple(value["route_lengths"]); value["exclusions"]=tuple(value["exclusions"]); value["audit_links"]=tuple(DeploymentAuditLink(**x) for x in value["audit_links"])
    return LoopbackDeploymentEvidence(**value)

def _write_exclusive(directory: Path,name: str,data: bytes):
    dfd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|getattr(os,"O_NOFOLLOW",0))
    try:
        fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,"O_NOFOLLOW",0),0o600,dir_fd=dfd)
        try:
            view=memoryview(data)
            while view:
                n=os.write(fd,view)
                if n<=0: raise OSError("short write")
                view=view[n:]
            os.fsync(fd)
        finally: os.close(fd)
        os.fsync(dfd)
    finally:
        os.close(dfd)

def _read_regular(directory: Path,name: str,maximum=8*1024*1024)->bytes:
    dfd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|getattr(os,"O_NOFOLLOW",0))
    try:
        fd=os.open(name,os.O_RDONLY|getattr(os,"O_NOFOLLOW",0),dir_fd=dfd)
        try:
            before=os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_size>maximum: raise ValueError("unsafe evidence")
            data=b""
            while len(data)<before.st_size:
                part=os.read(fd,before.st_size-len(data))
                if not part: raise ValueError("truncated evidence")
                data+=part
            after=os.fstat(fd)
            if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns): raise ValueError("evidence drift")
            return data
        finally: os.close(fd)
    finally: os.close(dfd)

def _historical_arguments(arguments, historical_lifecycle_scope):
    if historical_lifecycle_scope is None: raise ValueError("historical lifecycle scope required")
    values=dict(arguments)
    values.pop("current_lifecycle_scope",None); values.pop("historical_lifecycle_scope",None)
    values["lifecycle_scope"]=historical_lifecycle_scope
    return values

def _delivery_reload(arguments, marker, historical_lifecycle_scope):
    return verify_persisted_controlled_local_delivery(**_historical_arguments(arguments,historical_lifecycle_scope),authorization=marker)

def _delivery_current(arguments, marker, verified, historical_lifecycle_scope, current_lifecycle_scope):
    if current_lifecycle_scope is None: raise ValueError("current lifecycle scope required")
    values=_historical_arguments(arguments,historical_lifecycle_scope)
    return verify_controlled_local_delivery_current_eligibility(verified,manifest_evidence_path=values["manifest_evidence_path"],manifest_authorization=values["manifest_authorization"],evidence_snapshot=values["evidence_snapshot"],verified_release=values["verified_release"],historical_lifecycle_scope=historical_lifecycle_scope,current_lifecycle_scope=current_lifecycle_scope,declaration=values["declaration"],planning_authorization=values["planning_authorization"],verified_plan=values["verified_plan"],invocation_authorization=values["invocation_authorization"],conformance_authorization=values["conformance_authorization"],artifact_paths=values["artifact_paths"])

def _validate_authorization(a, delivery, arguments):
    if type(a) is not LoopbackDeploymentAuthorization: raise ValueError("exact authorization required")
    ledger=Path(a.ledger_directory); identity=_safe_ledger(ledger)
    expected={"policy_identity":_POLICY,"profile_identity":_PROFILE,"profile_version":_VERSION,"authority_identity":_AUTHORITY,"authority_owner":_OWNER,"authority_role":_ROLE,"implementation_identity":_IMPLEMENTATION,"implementation_version":_VERSION,"delivery_fingerprint":delivery.fingerprint,"release_identity":delivery.evidence.release_identity,"release_fingerprint":delivery.evidence.release_fingerprint,"lifecycle_inventory_digest":delivery.evidence.lifecycle_inventory_digest,"ledger_device":identity[0],"ledger_inode":identity[1],"exclusions":_EXCLUSIONS}
    if any(getattr(a,k)!=v for k,v in expected.items()) or a.fingerprint!=compute_deployment_authorization_fingerprint(a): raise ValueError("authorization binding mismatch")
    if not _valid_target(a.target) or not 1<=a.time_budget_seconds<=60: raise ValueError("profile bounds invalid")
    validate_bounded_route_mechanics(a.routes,a.request_budget)
    inventory=delivery.evidence.inventory
    if tuple((x.logical_filename,x.media_type) for x in inventory)!=tuple((x.logical_filename,x.media_type) for x in a.routes): raise ValueError("route map not exact Manifest closure")
    scope=_released_loopback_deployment_scope(a.target,a.routes,ledger)
    if a.released_authority_scope!=scope: raise ValueError("scope mismatch")
    authorities=arguments["verified_release"].bundle.one("PortablePresentationMaterialRecord").semantic["authorities"]
    exact={"id":_AUTHORITY,"owner_identity":_OWNER,"role":_ROLE,"scope":scope}
    if [x for x in authorities if x.get("id")==_AUTHORITY]!=[exact]: raise ValueError("authority not released")
    try:
        times=[datetime.strptime(getattr(a,x),"%Y-%m-%dT%H:%M:%SZ") for x in ("authorization_time","attempt_time","completion_time")]
        if not times[0]<times[1]<times[2]: raise ValueError
    except Exception as exc: raise ValueError("chronology invalid") from exc

def _issuance(a,delivery_fingerprint):
    en=_name(a.identity,"deployment-authorization.json"); cn=_name(a.identity,"deployment-authorization.commitment")
    provisional=DeploymentAuthorizationIssuanceEvidence(a.identity,a.fingerprint,delivery_fingerprint,a.release_fingerprint,en,cn,"")
    evidence=DeploymentAuthorizationIssuanceEvidence(**{**asdict(provisional),"fingerprint":_digest(asdict(provisional))})
    data=_canonical({"contract":"briefforge:loopback-deployment-issuance:1.0.0","authorization":asdict(a),"issuance":asdict(evidence)})
    commitment=_canonical({"contract":"briefforge:loopback-deployment-issuance-commitment:1.0.0","evidence_filename":en,"evidence_sha256":hashlib.sha256(data).hexdigest(),"issuance_fingerprint":evidence.fingerprint})
    return en,cn,evidence,data,commitment

def _unlink_and_fsync(directory: Path, *names: str):
    dfd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|getattr(os,"O_NOFOLLOW",0))
    try:
        for name in names:
            try: os.unlink(name,dir_fd=dfd)
            except FileNotFoundError: pass
        os.fsync(dfd)
        for name in names:
            try: os.stat(name,dir_fd=dfd,follow_symlinks=False)
            except FileNotFoundError: continue
            raise OSError("rollback residue remains")
    finally: os.close(dfd)

def issue_loopback_deployment_authorization(*,delivery_arguments: dict[str,Any],delivery_authorization: VerifiedControlledLocalDeliveryAuthorization,authorization: LoopbackDeploymentAuthorization,historical_lifecycle_scope,current_lifecycle_scope):
    delivery=_delivery_reload(delivery_arguments,delivery_authorization,historical_lifecycle_scope)
    if _delivery_current(delivery_arguments,delivery_authorization,delivery,historical_lifecycle_scope,current_lifecycle_scope).blocked: raise ValueError("delivery not currently eligible")
    _validate_authorization(authorization,delivery,delivery_arguments)
    en,cn,evidence,data,commitment=_issuance(authorization,delivery.fingerprint); ledger=_require_ledger_attachment(authorization)
    _write_exclusive(ledger,en,data)
    try: _write_exclusive(ledger,cn,commitment)
    except Exception as exc:
        try: _unlink_and_fsync(ledger,en,cn)
        except Exception as rollback: raise ValueError("issuance persistence-indeterminate") from rollback
        raise ValueError("issuance commitment failed; durable full cleanup") from exc
    _require_ledger_attachment(authorization)
    return VerifiedLoopbackDeploymentAuthorization._make(_canonical(asdict(authorization)).decode(),en,cn,evidence.fingerprint,_TOKEN)

def _reload_issued(marker):
    if type(marker) is not VerifiedLoopbackDeploymentAuthorization or getattr(marker,"_marker",None) is not _TOKEN: raise ValueError("sealed authorization required")
    a=marker.authorization; ledger=_require_ledger_attachment(a)
    raw=_read_regular(ledger,marker.issuance_filename); doc=json.loads(raw); issued=_authorization(doc["authorization"])
    issuance=DeploymentAuthorizationIssuanceEvidence(**doc["issuance"])
    expected_en,expected_cn,_,expected_raw,expected_commitment=_issuance(issued,issued.delivery_fingerprint)
    if issued!=a or raw!=expected_raw or _read_regular(ledger,marker.commitment_filename)!=expected_commitment or marker.issuance_filename!=expected_en or marker.commitment_filename!=expected_cn or marker.issuance_fingerprint!=issuance.fingerprint: raise ValueError("issuance invalid")
    return issued,issuance

def _load_bytes(delivery,a):
    e=delivery.evidence; final=Path(e.destination_parent)/e.destination_basename
    dfd=os.open(final,os.O_RDONLY|os.O_DIRECTORY|getattr(os,"O_NOFOLLOW",0)); result=[]
    try:
        info=os.fstat(dfd)
        if (info.st_dev,info.st_ino)!=(e.final_directory_device,e.final_directory_inode): raise ValueError("delivery directory changed")
        for route,item in zip(a.routes,e.inventory):
            fd=os.open(route.logical_filename,os.O_RDONLY|getattr(os,"O_NOFOLLOW",0),dir_fd=dfd)
            try:
                before=os.fstat(fd)
                if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_size!=item.byte_length or before.st_size>_MAX_BODY: raise ValueError("unsafe delivered artifact")
                data=b""
                while len(data)<before.st_size:
                    part=os.read(fd,before.st_size-len(data))
                    if not part: raise ValueError("short artifact")
                    data+=part
                after=os.fstat(fd); attached=os.stat(route.logical_filename,dir_fd=dfd,follow_symlinks=False)
                keys=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_nlink)
                if keys(before)!=keys(after) or keys(after)!=keys(attached) or hashlib.sha256(data).hexdigest()!=item.sha256: raise ValueError("delivered bytes changed")
                result.append(data)
            finally: os.close(fd)
    finally: os.close(dfd)
    return tuple(result)

def parse_bounded_request(raw: bytes, expected_host: str, routes: tuple[str,...])->str:
    if type(raw) is not bytes or not raw or len(raw)>_MAX_REQUEST or not raw.endswith(b"\r\n\r\n") or b"\n" in raw.replace(b"\r\n",b""): raise ValueError("malformed framing")
    try: text=raw.decode("ascii")
    except UnicodeDecodeError as exc: raise ValueError("non-ascii request") from exc
    lines=text[:-4].split("\r\n")
    if len(lines)!=2 or lines[0].count(" ")!=2: raise ValueError("exact request line and Host required")
    method,path,version=lines[0].split(" ")
    if method!="GET" or version!="HTTP/1.1" or path not in routes or any(c in path for c in "?#%\\") or "//" in path: raise ValueError("unsupported request target")
    if lines[1]!=f"Host: {expected_host}": raise ValueError("Host mismatch")
    return path

def _links(a,delivery,service):
    raw=(("release-authorizes-target",a.release_identity,a.released_authority_scope),("delivery-supplies-deployment",delivery.fingerprint,a.identity),("authorization-consumed-by",a.identity,a.attempt_identity),("attempt-activates-service",a.attempt_identity,service))
    return tuple(DeploymentAuditLink(k,s,t,_digest({"kind":k,"source":s,"target":t})) for k,s,t in raw)

def compute_service_instance_identity(authorization_fingerprint: str, attempt_identity: str,
        target: DeploymentTarget, service_token_digest: str)->str:
    """Recompute the identity of one token-bound service attempt."""
    if (type(authorization_fingerprint) is not str or type(attempt_identity) is not str
        or type(target) is not DeploymentTarget or type(service_token_digest) is not str):
        raise TypeError("exact service identity inputs required")
    return "service:bounded-loopback:"+_digest({"authorization":authorization_fingerprint,"attempt":attempt_identity,
        "target":asdict(target),"service_token_digest":service_token_digest})

def _make_evidence(a,issuance,delivery,contents,service,token_digest,observed_start,observed_end):
    ledger=Path(a.ledger_directory); ep=ledger/_name(a.identity,"deployment-evidence.json"); cp=ledger/_name(a.identity,"deployment-evidence.commitment")
    provisional=LoopbackDeploymentEvidence(a.evidence_identity,_VERSION,_POLICY,_PROFILE,_IMPLEMENTATION,_VERSION,a.identity,a.fingerprint,issuance.fingerprint,delivery.fingerprint,a.release_identity,a.release_fingerprint,a.lifecycle_inventory_digest,a.target,a.routes,tuple(hashlib.sha256(x).hexdigest() for x in contents),tuple(len(x) for x in contents),service,token_digest,a.attempt_identity,a.authorization_time,observed_start,observed_end,observed_start,observed_end,a.request_budget,a.time_budget_seconds,a.ledger_directory,a.ledger_device,a.ledger_inode,str(ep),str(cp),a.exclusions,"bounded-loopback-listener-activated",_links(a,delivery,service),"")
    return LoopbackDeploymentEvidence(**{**asdict(provisional),"target":a.target,"routes":a.routes,"route_sha256":provisional.route_sha256,"route_lengths":provisional.route_lengths,"exclusions":a.exclusions,"audit_links":provisional.audit_links,"fingerprint":compute_deployment_evidence_fingerprint(provisional)})

def _response(route,body,token):
    return (f"HTTP/1.1 200 OK\r\nContent-Type: {route.media_type}\r\nContent-Length: {len(body)}\r\nX-BriefForge-Service-Token: {token.hex()}\r\nConnection: close\r\n\r\n".encode()+body)

def _serve(listener,stop_event,a,contents,token):
    routes={r.path:(r,b) for r,b in zip(a.routes,contents)}; deadline=time.monotonic()+a.time_budget_seconds; count=0
    listener.settimeout(.1)
    while not stop_event.is_set() and count<a.request_budget and time.monotonic()<deadline:
        try: conn,peer=listener.accept()
        except socket.timeout: continue
        except OSError: break
        count+=1
        try:
            conn.settimeout(1); raw=b""
            while b"\r\n\r\n" not in raw and len(raw)<=_MAX_REQUEST:
                part=conn.recv(min(1024,_MAX_REQUEST+1-len(raw)))
                if not part: break
                raw+=part
            try:
                path=parse_bounded_request(raw,f"127.0.0.1:{a.target.port}",tuple(routes)); route,body=routes[path]; response=_response(route,body,token)
            except ValueError: response=b"HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
            conn.sendall(response)
        except OSError: pass
        finally: conn.close()
    try: listener.close()
    except OSError: pass

def _blocked(code,state="blocked"): return LoopbackDeploymentResult((DeploymentFinding(code,"/deployment",code.replace("-"," ")),),state,None,None)

def start_bounded_loopback_deployment(*,delivery_arguments,delivery_authorization,authorization,historical_lifecycle_scope,current_lifecycle_scope):
    try: a,issuance=_reload_issued(authorization)
    except Exception: return _blocked("deployment-authorization-not-issued")
    try: ledger=_require_ledger_attachment(a)
    except Exception: return _blocked("deployment-ledger-attachment-invalid","persistence-indeterminate")
    consumed=_name(a.identity,"deployment-consumed")
    try: _write_exclusive(ledger,consumed,_canonical(asdict(DeploymentConsumption(a.identity,a.fingerprint,a.attempt_identity,issuance.fingerprint))))
    except FileExistsError: return _blocked("deployment-authorization-consumed")
    except Exception: return _blocked("deployment-consumption-persistence-indeterminate","persistence-indeterminate")
    listener=None
    evidence_written=False
    try:
        first=_delivery_reload(delivery_arguments,delivery_authorization,historical_lifecycle_scope)
        if _delivery_current(delivery_arguments,delivery_authorization,first,historical_lifecycle_scope,current_lifecycle_scope).blocked: raise PermissionError("lifecycle drift")
        _validate_authorization(a,first,delivery_arguments)
        contents=_load_bytes(first,a)                 # exact source bytes are now pinned
        listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        token=secrets.token_bytes(32)
        token_digest=hashlib.sha256(token).hexdigest()
        service=compute_service_instance_identity(a.fingerprint,a.attempt_identity,a.target,token_digest)
        observed_start=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        # Final gate: complete persisted controlled-delivery replay and current eligibility. Bind is
        # deliberately the very next operation, with no clock or source operation between.
        final=_delivery_reload(delivery_arguments,delivery_authorization,historical_lifecycle_scope)
        if final.fingerprint!=first.fingerprint or _delivery_current(delivery_arguments,delivery_authorization,final,historical_lifecycle_scope,current_lifecycle_scope).blocked: raise PermissionError("lifecycle drift")
        listener.bind((a.target.address,a.target.port))
        listener.listen(min(a.request_budget,16))
        observed_end=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        evidence=_make_evidence(a,issuance,final,contents,service,token_digest,observed_start,observed_end); data=_canonical(asdict(evidence)); ep=Path(evidence.evidence_path); cp=Path(evidence.commitment_path)
        _require_ledger_attachment(a); _write_exclusive(ledger,ep.name,data); evidence_written=True
        marker=VerifiedLoopbackDeployment._make(data.decode(),evidence.fingerprint,_TOKEN)
        try:
            _require_ledger_attachment(a)
            _write_exclusive(ledger,cp.name,_canonical({"evidence_sha256":hashlib.sha256(data).hexdigest(),"fingerprint":evidence.fingerprint,"service_instance_identity":service,"service_token_digest":token_digest}))
        except Exception:
            try: listener.close()
            except OSError: pass
            listener=None
            return LoopbackDeploymentResult((DeploymentFinding("deployment-completion-pending","/deployment","deployment evidence durable but commitment missing"),),"completion-pending",marker,None)
        verified=verify_persisted_loopback_deployment(marker,delivery_arguments=delivery_arguments,delivery_authorization=delivery_authorization,authorization=authorization,historical_lifecycle_scope=historical_lifecycle_scope,current_lifecycle_scope=current_lifecycle_scope,require_current=True)
        stop=threading.Event(); thread=threading.Thread(target=_serve,args=(listener,stop,a,contents,token),name="briefforge-bounded-loopback",daemon=False); thread.start()
        running=RunningLoopbackDeployment._make(listener,thread,stop,verified,a.target,token,_TOKEN)
        require_active_running_deployment(running,verified)
        return LoopbackDeploymentResult((),"active",verified,running)
    except PermissionError:
        if listener is not None:
            try: listener.close()
            except OSError: return _blocked("deployment-service-rollback-indeterminate","persistence-indeterminate")
        return _blocked("deployment-lifecycle-drift","deployment-failed-consumed-service-rollback-verified")
    except Exception:
        if listener is not None:
            try: listener.close()
            except OSError: return _blocked("deployment-service-rollback-indeterminate","persistence-indeterminate")
        state="completion-pending" if evidence_written else "deployment-failed-consumed-service-rollback-verified"
        return _blocked("deployment-failed-consumed",state)

def _validate_persisted_loopback_deployment(*, authorization, deployment_evidence_path,
        delivery_arguments, delivery_authorization, historical_lifecycle_scope, current_lifecycle_scope,
        require_current=False, allow_missing_commitment=False):
    a,issuance=_reload_issued(authorization)
    delivery=_delivery_reload(delivery_arguments,delivery_authorization,historical_lifecycle_scope)
    if require_current and _delivery_current(delivery_arguments,delivery_authorization,delivery,historical_lifecycle_scope,current_lifecycle_scope).blocked: raise ValueError("current delivery lifecycle ineligible")
    _validate_authorization(a,delivery,delivery_arguments)
    ledger=_require_ledger_attachment(a)
    path=Path(deployment_evidence_path); expected_ep=_name(a.identity,"deployment-evidence.json"); expected_cp=_name(a.identity,"deployment-evidence.commitment")
    if path.parent!=ledger or path.name!=expected_ep: raise ValueError("deployment evidence path binding invalid")
    data=_read_regular(ledger,expected_ep); parsed=_evidence(json.loads(data))
    if data!=_canonical(asdict(parsed)) or parsed.fingerprint!=compute_deployment_evidence_fingerprint(parsed): raise ValueError("deployment evidence invalid")
    if (parsed.ledger_directory,parsed.ledger_device,parsed.ledger_inode)!=(a.ledger_directory,a.ledger_device,a.ledger_inode): raise ValueError("deployment ledger binding invalid")
    if Path(parsed.evidence_path)!=path or Path(parsed.commitment_path)!=ledger/expected_cp: raise ValueError("deployment evidence path binding invalid")
    consumed=_canonical(asdict(DeploymentConsumption(a.identity,a.fingerprint,a.attempt_identity,issuance.fingerprint)))
    if _read_regular(ledger,_name(a.identity,"deployment-consumed"))!=consumed: raise ValueError("deployment consumption invalid")
    try:
        start=datetime.strptime(parsed.bounded_interval_start,"%Y-%m-%dT%H:%M:%S.%fZ"); end=datetime.strptime(parsed.bounded_interval_end,"%Y-%m-%dT%H:%M:%S.%fZ")
        if start>end or parsed.attempt_time!=parsed.bounded_interval_start or parsed.completion_time!=parsed.bounded_interval_end: raise ValueError
    except Exception as exc: raise ValueError("observed deployment chronology invalid") from exc
    if len(parsed.service_token_digest)!=64 or any(c not in "0123456789abcdef" for c in parsed.service_token_digest): raise ValueError("service token digest invalid")
    service=compute_service_instance_identity(a.fingerprint,a.attempt_identity,a.target,parsed.service_token_digest)
    contents=_load_bytes(delivery,a)
    expected=_make_evidence(a,issuance,delivery,contents,service,parsed.service_token_digest,parsed.bounded_interval_start,parsed.bounded_interval_end)
    if parsed!=expected: raise ValueError("deployment evidence differs from independent reproduction")
    commitment=_canonical({"evidence_sha256":hashlib.sha256(data).hexdigest(),"fingerprint":parsed.fingerprint,"service_instance_identity":service,"service_token_digest":parsed.service_token_digest})
    missing=False
    try:
        if _read_regular(ledger,expected_cp)!=commitment: raise ValueError("deployment commitment invalid")
    except FileNotFoundError:
        if not allow_missing_commitment: raise
        missing=True
    _require_ledger_attachment(a)
    return VerifiedLoopbackDeployment._make(data.decode(),parsed.fingerprint,_TOKEN),missing,commitment

def verify_persisted_loopback_deployment(verified, *, delivery_arguments, delivery_authorization, authorization,
        historical_lifecycle_scope, current_lifecycle_scope, require_current=False):
    if type(verified) is not VerifiedLoopbackDeployment or getattr(verified,"_marker",None) is not _TOKEN: raise ValueError("sealed deployment required")
    e=verified.evidence
    if verified._document!=_canonical(asdict(e)).decode() or verified.fingerprint!=e.fingerprint: raise ValueError("sealed deployment document invalid")
    loaded,_,_=_validate_persisted_loopback_deployment(authorization=authorization,deployment_evidence_path=e.evidence_path,
        delivery_arguments=delivery_arguments,delivery_authorization=delivery_authorization,
        historical_lifecycle_scope=historical_lifecycle_scope,current_lifecycle_scope=current_lifecycle_scope,require_current=require_current)
    if loaded.fingerprint!=verified.fingerprint: raise ValueError("deployment marker mismatch")
    return loaded

def _read_exact_response(target,route,expected_length,expected_digest,expected_token):
    request=f"GET {route.path} HTTP/1.1\r\nHost: 127.0.0.1:{target.port}\r\n\r\n".encode()
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.settimeout(2)
    try:
        s.connect((target.address,target.port)); s.sendall(request); raw=b""
        while len(raw)<=_MAX_BODY+8192:
            part=s.recv(65536)
            if not part: break
            raw+=part
    finally: s.close()
    head,body=raw.split(b"\r\n\r\n",1); lines=head.decode("ascii").split("\r\n")
    expected=(("Content-Type",route.media_type),("Content-Length",str(expected_length)),("X-BriefForge-Service-Token",expected_token.hex()),("Connection","close"))
    actual=tuple(tuple(line.split(": ",1)) for line in lines[1:] if ": " in line)
    if lines[0]!="HTTP/1.1 200 OK" or actual!=expected or len(body)!=expected_length or hashlib.sha256(body).hexdigest()!=expected_digest: raise ValueError("current response mismatch")
    token_value=dict(actual).get("X-BriefForge-Service-Token")
    if token_value is None or not secrets.compare_digest(bytes.fromhex(token_value),expected_token): raise ValueError("service instance continuity failed")

def verify_deployment_current_availability(verified, *, running, delivery_arguments, delivery_authorization, authorization, historical_lifecycle_scope, current_lifecycle_scope):
    try:
        persisted=verify_persisted_loopback_deployment(verified,delivery_arguments=delivery_arguments,delivery_authorization=delivery_authorization,authorization=authorization,historical_lifecycle_scope=historical_lifecycle_scope,current_lifecycle_scope=current_lifecycle_scope,require_current=True)
        receipt=require_active_running_deployment(running,persisted)
        for route,length,digest in zip(persisted.evidence.routes,persisted.evidence.route_lengths,persisted.evidence.route_sha256):
            require_active_running_deployment(receipt,persisted)
            _read_exact_response(persisted.evidence.target,route,length,digest,receipt._service_token)
        return LoopbackDeploymentResult((),"current-availability-established",persisted,running)
    except Exception: return _blocked("current-availability-not-established","not-established")

def _stop_names(e):
    return (_name(e.authorization_identity,"deployment-stop-evidence.json"),_name(e.authorization_identity,"deployment-stop-evidence.commitment"))

def _stop_evidence(doc):
    value=dict(doc); value["target"]=DeploymentTarget(**value["target"]); value["exclusions"]=tuple(value["exclusions"])
    return DeploymentStopEvidence(**value)

def _stop_fingerprint(e):
    doc=asdict(e); doc.pop("fingerprint",None); return _digest(doc)

def verify_persisted_deployment_stop(*,deployment,authorization,delivery_arguments,delivery_authorization,historical_lifecycle_scope,current_lifecycle_scope):
    persisted=verify_persisted_loopback_deployment(deployment,delivery_arguments=delivery_arguments,delivery_authorization=delivery_authorization,authorization=authorization,historical_lifecycle_scope=historical_lifecycle_scope,current_lifecycle_scope=current_lifecycle_scope)
    a,_=_reload_issued(authorization); ledger=_require_ledger_attachment(a); en,cn=_stop_names(persisted.evidence)
    data=_read_regular(ledger,en); stopped=_stop_evidence(json.loads(data))
    if data!=_canonical(asdict(stopped)) or stopped.fingerprint!=_stop_fingerprint(stopped): raise ValueError("stop evidence invalid")
    expected={"authorization_identity":a.identity,"authorization_fingerprint":a.fingerprint,"deployment_fingerprint":persisted.fingerprint,"target":a.target,"service_instance_identity":persisted.evidence.service_instance_identity,"service_token_digest":persisted.evidence.service_token_digest,"state":"shutdown-verified","stop_requested":True,"thread_joined":True,"socket_closed":True,"residue_probe":"loopback-port-refused","ledger_directory":a.ledger_directory,"ledger_device":a.ledger_device,"ledger_inode":a.ledger_inode,"exclusions":a.exclusions}
    if any(getattr(stopped,k)!=v for k,v in expected.items()): raise ValueError("stop evidence binding invalid")
    commitment=_canonical({"evidence_sha256":hashlib.sha256(data).hexdigest(),"fingerprint":stopped.fingerprint,"deployment_fingerprint":persisted.fingerprint,"service_token_digest":stopped.service_token_digest})
    if _read_regular(ledger,cn)!=commitment: raise ValueError("stop commitment invalid")
    _require_ledger_attachment(a)
    return stopped

def stop_bounded_loopback_deployment(result, *, authorization, delivery_arguments, delivery_authorization, historical_lifecycle_scope, current_lifecycle_scope):
    if type(result) is not LoopbackDeploymentResult or result.state!="active" or type(result.service) is not RunningLoopbackDeployment:
        return _blocked("shutdown-indeterminate","shutdown-indeterminate")
    running=result.service; evidence=result.verified.evidence
    try:
        existing=verify_persisted_deployment_stop(deployment=result.verified,authorization=authorization,delivery_arguments=delivery_arguments,delivery_authorization=delivery_authorization,historical_lifecycle_scope=historical_lifecycle_scope,current_lifecycle_scope=current_lifecycle_scope)
        if existing.state=="shutdown-verified": return LoopbackDeploymentResult((),"shutdown-verified",result.verified,None)
    except FileNotFoundError: pass
    except ValueError as exc:
        if "stop" in str(exc): return _blocked("shutdown-evidence-invalid","shutdown-indeterminate")
    running._stop_event.set()
    try: running._listener.shutdown(socket.SHUT_RDWR)
    except OSError: pass
    try: running._listener.close()
    except OSError: return _blocked("shutdown-listener-close-indeterminate","shutdown-indeterminate")
    running._thread.join(2)
    if running._thread.is_alive(): return _blocked("shutdown-thread-join-indeterminate","shutdown-indeterminate")
    if running._listener.fileno()!=-1: return _blocked("shutdown-listener-close-indeterminate","shutdown-indeterminate")
    probe=socket.socket(socket.AF_INET,socket.SOCK_STREAM); probe.settimeout(.2)
    try:
        if probe.connect_ex((evidence.target.address,evidence.target.port))==0: return _blocked("shutdown-residue","shutdown-indeterminate")
    finally: probe.close()
    try:
        a,_=_reload_issued(authorization); ledger=_require_ledger_attachment(a); en,cn=_stop_names(evidence)
        provisional=DeploymentStopEvidence(_VERSION,a.identity,a.fingerprint,result.verified.fingerprint,a.target,evidence.service_instance_identity,evidence.service_token_digest,"shutdown-verified",True,True,True,"loopback-port-refused",datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),a.ledger_directory,a.ledger_device,a.ledger_inode,a.exclusions,"")
        stopped=DeploymentStopEvidence(**{**asdict(provisional),"target":a.target,"exclusions":a.exclusions,"fingerprint":_stop_fingerprint(provisional)})
        data=_canonical(asdict(stopped)); _write_exclusive(ledger,en,data)
        try: _write_exclusive(ledger,cn,_canonical({"evidence_sha256":hashlib.sha256(data).hexdigest(),"fingerprint":stopped.fingerprint,"deployment_fingerprint":result.verified.fingerprint,"service_token_digest":stopped.service_token_digest}))
        except Exception: return _blocked("shutdown-evidence-completion-pending","completion-pending")
        verify_persisted_deployment_stop(deployment=result.verified,authorization=authorization,delivery_arguments=delivery_arguments,delivery_authorization=delivery_authorization,historical_lifecycle_scope=historical_lifecycle_scope,current_lifecycle_scope=current_lifecycle_scope)
    except FileExistsError:
        try: verify_persisted_deployment_stop(deployment=result.verified,authorization=authorization,delivery_arguments=delivery_arguments,delivery_authorization=delivery_authorization,historical_lifecycle_scope=historical_lifecycle_scope,current_lifecycle_scope=current_lifecycle_scope)
        except Exception: return _blocked("shutdown-evidence-invalid","shutdown-indeterminate")
    except Exception: return _blocked("shutdown-evidence-persistence-indeterminate","persistence-indeterminate")
    return LoopbackDeploymentResult((),"shutdown-verified",result.verified,None)

def _load_authorization_from_path(path):
    path=Path(path); raw=_read_regular(path.parent,path.name); doc=json.loads(raw); a=_authorization(doc["authorization"]); issuance=DeploymentAuthorizationIssuanceEvidence(**doc["issuance"])
    en,cn,expected,expected_raw,commitment=_issuance(a,a.delivery_fingerprint)
    if path.name!=en or raw!=expected_raw or issuance!=expected or _read_regular(path.parent,cn)!=commitment: raise ValueError("issuance path invalid")
    _require_ledger_attachment(a)
    return a,VerifiedLoopbackDeploymentAuthorization._make(_canonical(asdict(a)).decode(),en,cn,issuance.fingerprint,_TOKEN)

def load_persisted_loopback_deployment_authorization(authorization_evidence_path):
    """Reconstruct a sealed authorization from its canonical committed issuance."""
    return _load_authorization_from_path(authorization_evidence_path)[1]

def load_persisted_loopback_deployment(*,authorization_evidence_path,deployment_evidence_path,
        delivery_arguments,delivery_authorization,historical_lifecycle_scope,current_lifecycle_scope,require_current=False):
    """Read-only restart loader; no process-local deployment marker is trusted."""
    _,authorization=_load_authorization_from_path(authorization_evidence_path)
    loaded,_,_=_validate_persisted_loopback_deployment(authorization=authorization,deployment_evidence_path=deployment_evidence_path,
        delivery_arguments=delivery_arguments,delivery_authorization=delivery_authorization,
        historical_lifecycle_scope=historical_lifecycle_scope,current_lifecycle_scope=current_lifecycle_scope,require_current=require_current)
    return loaded

def reconcile_loopback_deployment_commitment(*,authorization_evidence_path,deployment_evidence_path,delivery_arguments,delivery_authorization,historical_lifecycle_scope,current_lifecycle_scope):
    try:
        a,authorization=_load_authorization_from_path(authorization_evidence_path); ledger=_require_ledger_attachment(a)
        verified,missing,commitment=_validate_persisted_loopback_deployment(authorization=authorization,deployment_evidence_path=deployment_evidence_path,
            delivery_arguments=delivery_arguments,delivery_authorization=delivery_authorization,
            historical_lifecycle_scope=historical_lifecycle_scope,current_lifecycle_scope=current_lifecycle_scope,allow_missing_commitment=True)
        if missing:
            _write_exclusive(ledger,_name(a.identity,"deployment-evidence.commitment"),commitment)
        # Full independent post-write reload, including the commitment.
        verified=load_persisted_loopback_deployment(authorization_evidence_path=authorization_evidence_path,
            deployment_evidence_path=deployment_evidence_path,delivery_arguments=delivery_arguments,
            delivery_authorization=delivery_authorization,historical_lifecycle_scope=historical_lifecycle_scope,
            current_lifecycle_scope=current_lifecycle_scope)
        return LoopbackDeploymentResult((),"historical-deployment-observed",verified,None)
    except Exception: return _blocked("reconciliation-blocked","persistence-indeterminate")
