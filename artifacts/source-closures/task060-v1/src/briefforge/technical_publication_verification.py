"""Separately authorized raw-transport technical observation companion.

A verified value is historical evidence for exact responses during one bounded
IPv4 loopback interval.  It explicitly says nothing about public reachability,
continuing service, browsers, accessibility, readers, editorial quality, or
production readiness.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
from typing import Any

from .bounded_loopback_deployment import (
    DeploymentRouteItem, DeploymentTarget, LoopbackDeploymentResult,
    VerifiedLoopbackDeployment, verify_persisted_loopback_deployment,
    load_persisted_loopback_deployment, load_persisted_loopback_deployment_authorization,
    verify_deployment_current_availability,
    RunningLoopbackDeployment, require_active_running_deployment,
    validate_bounded_route_mechanics, stop_bounded_loopback_deployment,
)

_POLICY="briefforge-technical-publication-verification-policy:1.0.0"
_PROFILE="briefforge-raw-http-technical-publication-profile:1.0.0"
_IMPLEMENTATION="briefforge.technical_publication_verification"
_VERSION="1.0.0"
_AUTHORITY="authority:briefforge-technical-publication-verifier"
_OWNER="project:BriefForge"
_ROLE="technical-publication-verification-authority"
_EXCLUSIONS=("public-internet","continuing-availability","browser","javascript","accessibility","reader","editorial","production","atlasforge-authority","hostile-process-authentication")
_TOKEN=object()
_MAX_RESPONSE=100_010_000

@dataclass(frozen=True, order=True)
class TechnicalPublicationFinding:
    code: str
    location: str
    message: str

@dataclass(frozen=True, order=True)
class TechnicalPublicationAuditLink:
    kind: str
    source_identity: str
    target_identity: str
    binding_fingerprint: str

@dataclass(frozen=True)
class TechnicalVerificationAuthorization:
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
    deployment_fingerprint: str
    service_instance_identity: str
    service_token_digest: str
    target: DeploymentTarget
    routes: tuple[DeploymentRouteItem,...]
    attempt_identity: str
    evidence_identity: str
    implementation_identity: str
    implementation_version: str
    ledger_directory: str
    ledger_device: int
    ledger_inode: int
    exclusions: tuple[str,...]
    released_authority_scope: str
    fingerprint: str

@dataclass(frozen=True)
class TechnicalVerificationIssuanceEvidence:
    authorization_identity: str
    authorization_fingerprint: str
    deployment_fingerprint: str
    service_instance_identity: str
    service_token_digest: str
    evidence_filename: str
    commitment_filename: str
    fingerprint: str

@dataclass(frozen=True)
class TechnicalVerificationConsumption:
    authorization_identity: str
    authorization_fingerprint: str
    attempt_identity: str
    issuance_fingerprint: str

@dataclass(frozen=True)
class RouteTransportObservation:
    route: str
    request_sha256: str
    status_line: str
    headers: tuple[tuple[str,str],...]
    body_length: int
    body_sha256: str
    service_instance_identity: str
    service_token_digest: str
    outcome: str

@dataclass(frozen=True)
class TechnicalPublicationEvidence:
    evidence_identity: str
    evidence_version: str
    policy_identity: str
    profile_identity: str
    implementation_identity: str
    implementation_version: str
    authorization_identity: str
    authorization_fingerprint: str
    issuance_fingerprint: str
    deployment_fingerprint: str
    service_instance_identity: str
    service_token_digest: str
    target: DeploymentTarget
    routes: tuple[DeploymentRouteItem,...]
    observations: tuple[RouteTransportObservation,...]
    attempt_identity: str
    authorization_time: str
    attempt_time: str
    completion_time: str
    bounded_interval_start: str
    bounded_interval_end: str
    ledger_directory: str
    ledger_device: int
    ledger_inode: int
    evidence_path: str
    commitment_path: str
    exclusions: tuple[str,...]
    outcome: str
    audit_links: tuple[TechnicalPublicationAuditLink,...]
    fingerprint: str

@dataclass(frozen=True, init=False)
class VerifiedTechnicalVerificationAuthorization:
    _document: str
    issuance_filename: str
    commitment_filename: str
    issuance_fingerprint: str
    _marker: object
    def __new__(cls): raise TypeError("sealed type")
    @classmethod
    def _make(cls,document,issuance,commitment,fingerprint,marker):
        if marker is not _TOKEN: raise TypeError("private constructor")
        value=object.__new__(cls)
        for k,v in (("_document",document),("issuance_filename",issuance),("commitment_filename",commitment),("issuance_fingerprint",fingerprint),("_marker",_TOKEN)): object.__setattr__(value,k,v)
        return value
    @property
    def authorization(self): return _authorization(json.loads(self._document))

@dataclass(frozen=True, init=False)
class VerifiedTechnicalPublication:
    _document: str
    fingerprint: str
    _marker: object
    def __new__(cls): raise TypeError("sealed type")
    @classmethod
    def _make(cls,document,fingerprint,marker):
        if marker is not _TOKEN: raise TypeError("private constructor")
        value=object.__new__(cls)
        for k,v in (("_document",document),("fingerprint",fingerprint),("_marker",_TOKEN)): object.__setattr__(value,k,v)
        return value
    @property
    def evidence(self): return _evidence(json.loads(self._document))

@dataclass(frozen=True)
class TechnicalVerificationResult:
    findings: tuple[TechnicalPublicationFinding,...]
    state: str
    verified: VerifiedTechnicalPublication|None
    @property
    def blocked(self): return self.state!="bounded-observation-succeeded"

@dataclass(frozen=True)
class CoordinatedTechnicalVerificationResult:
    """The inseparable observation/shutdown outcome for a live deployment."""
    verification: TechnicalVerificationResult
    shutdown: LoopbackDeploymentResult


def _canonical(value: Any)->bytes: return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
def _digest(value: Any)->str: return hashlib.sha256(_canonical(value)).hexdigest()
def _name(identity,suffix): return hashlib.sha256(identity.encode()).hexdigest()+"."+suffix

def _safe_ledger(path):
    path=Path(path)
    if not path.is_absolute(): path=path.resolve()
    if str(path.resolve())!=str(path) or path.is_symlink() or not path.is_dir(): raise ValueError("unsafe ledger")
    info=os.stat(path,follow_symlinks=False)
    if info.st_mode & 0o022: raise ValueError("unsafe permissions")
    return info.st_dev,info.st_ino

def _released_technical_verification_scope(target: DeploymentTarget,routes: tuple[DeploymentRouteItem,...],ledger: Path)->str:
    if (type(target) is not DeploymentTarget or target.address!="127.0.0.1" or type(target.port) is not int or not 1024<=target.port<=65535
        or target.origin!=f"http://127.0.0.1:{target.port}" or type(routes) is not tuple or not routes): raise ValueError("invalid fixed target")
    validate_bounded_route_mechanics(routes,len(routes))
    identity=_safe_ledger(ledger)
    return _canonical({"policy":_POLICY,"profile":_PROFILE,"implementation":_IMPLEMENTATION,"version":_VERSION,"target":asdict(target),"routes":[asdict(x) for x in routes],"ledger":{"canonical_path":str(Path(ledger).resolve()),"device":identity[0],"inode":identity[1]},"contract":{"one_act":True,"actual_raw_transport":True,"historical_only":True}}).decode()

def compute_verification_authorization_fingerprint(a):
    if type(a) is not TechnicalVerificationAuthorization: raise TypeError("exact authorization required")
    doc=asdict(a); doc.pop("fingerprint",None); return _digest(doc)

def _authorization(doc):
    value=dict(doc); value["target"]=DeploymentTarget(**value["target"]); value["routes"]=tuple(DeploymentRouteItem(**x) for x in value["routes"]); value["exclusions"]=tuple(value["exclusions"])
    return TechnicalVerificationAuthorization(**value)

def compute_technical_publication_evidence_fingerprint(e):
    doc=asdict(e); doc.pop("fingerprint",None); return _digest(doc)

def _evidence(doc):
    value=dict(doc); value["target"]=DeploymentTarget(**value["target"]); value["routes"]=tuple(DeploymentRouteItem(**x) for x in value["routes"])
    observations=[]
    for item in value["observations"]:
        item=dict(item); item["headers"]=tuple(tuple(x) for x in item["headers"]); observations.append(RouteTransportObservation(**item))
    value["observations"]=tuple(observations); value["exclusions"]=tuple(value["exclusions"]); value["audit_links"]=tuple(TechnicalPublicationAuditLink(**x) for x in value["audit_links"])
    return TechnicalPublicationEvidence(**value)

def _write_exclusive(directory,name,data):
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
    finally: os.close(dfd)

def _read_regular(directory,name,maximum=8*1024*1024):
    dfd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|getattr(os,"O_NOFOLLOW",0))
    try:
        fd=os.open(name,os.O_RDONLY|getattr(os,"O_NOFOLLOW",0),dir_fd=dfd)
        try:
            before=os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_size>maximum: raise ValueError("unsafe evidence")
            data=b""
            while len(data)<before.st_size:
                part=os.read(fd,before.st_size-len(data))
                if not part: raise ValueError("short evidence")
                data+=part
            after=os.fstat(fd)
            if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns): raise ValueError("evidence drift")
            return data
        finally: os.close(fd)
    finally: os.close(dfd)

def _validate(a,deployment,verified_release):
    if type(a) is not TechnicalVerificationAuthorization: raise ValueError("exact authorization required")
    identity=_safe_ledger(a.ledger_directory); e=deployment.evidence
    expected={"policy_identity":_POLICY,"profile_identity":_PROFILE,"profile_version":_VERSION,"authority_identity":_AUTHORITY,"authority_owner":_OWNER,"authority_role":_ROLE,"implementation_identity":_IMPLEMENTATION,"implementation_version":_VERSION,"deployment_fingerprint":deployment.fingerprint,"service_instance_identity":e.service_instance_identity,"service_token_digest":e.service_token_digest,"target":e.target,"routes":e.routes,"ledger_device":identity[0],"ledger_inode":identity[1],"exclusions":_EXCLUSIONS}
    if any(getattr(a,k)!=v for k,v in expected.items()) or a.fingerprint!=compute_verification_authorization_fingerprint(a): raise ValueError("authorization binding mismatch")
    scope=_released_technical_verification_scope(a.target,a.routes,Path(a.ledger_directory))
    if a.released_authority_scope!=scope: raise ValueError("scope mismatch")
    authorities=verified_release.bundle.one("PortablePresentationMaterialRecord").semantic["authorities"]
    exact={"id":_AUTHORITY,"owner_identity":_OWNER,"role":_ROLE,"scope":scope}
    if [x for x in authorities if x.get("id")==_AUTHORITY]!=[exact]: raise ValueError("verification authority not released")
    try:
        times=[datetime.strptime(getattr(a,x),"%Y-%m-%dT%H:%M:%SZ") for x in ("authorization_time","attempt_time","completion_time")]
        if not times[0]<times[1]<times[2]: raise ValueError
    except Exception as exc: raise ValueError("chronology invalid") from exc

def _require_ledger_attachment(a):
    identity=_safe_ledger(a.ledger_directory)
    if identity!=(a.ledger_device,a.ledger_inode): raise ValueError("verification ledger changed")
    return Path(a.ledger_directory)

def _issuance(a):
    en=_name(a.identity,"technical-verification-authorization.json"); cn=_name(a.identity,"technical-verification-authorization.commitment")
    provisional=TechnicalVerificationIssuanceEvidence(a.identity,a.fingerprint,a.deployment_fingerprint,a.service_instance_identity,a.service_token_digest,en,cn,"")
    issuance=TechnicalVerificationIssuanceEvidence(**{**asdict(provisional),"fingerprint":_digest(asdict(provisional))})
    data=_canonical({"contract":"briefforge:technical-verification-issuance:1.0.0","authorization":asdict(a),"issuance":asdict(issuance)})
    commitment=_canonical({"contract":"briefforge:technical-verification-issuance-commitment:1.0.0","evidence_sha256":hashlib.sha256(data).hexdigest(),"issuance_fingerprint":issuance.fingerprint})
    return en,cn,issuance,data,commitment

def _reload_deployment_chain(deployment,deployment_authorization,delivery_arguments,delivery_authorization,historical_lifecycle_scope,current_lifecycle_scope,require_current):
    if deployment_authorization is None or delivery_arguments is None or delivery_authorization is None or historical_lifecycle_scope is None or current_lifecycle_scope is None:
        raise ValueError("complete controlled-delivery/deployment chain and distinct lifecycle scopes required")
    return verify_persisted_loopback_deployment(deployment,delivery_arguments=delivery_arguments,
        delivery_authorization=delivery_authorization,authorization=deployment_authorization,historical_lifecycle_scope=historical_lifecycle_scope,
        current_lifecycle_scope=current_lifecycle_scope,require_current=require_current)

def issue_technical_verification_authorization(*,deployment: VerifiedLoopbackDeployment,running: RunningLoopbackDeployment,deployment_authorization,authorization: TechnicalVerificationAuthorization,
        delivery_arguments,delivery_authorization,historical_lifecycle_scope,current_lifecycle_scope):
    reloaded=_reload_deployment_chain(deployment,deployment_authorization,delivery_arguments,delivery_authorization,historical_lifecycle_scope,current_lifecycle_scope,True)
    receipt=require_active_running_deployment(running,reloaded)
    if hashlib.sha256(receipt._service_token).hexdigest()!=authorization.service_token_digest: raise ValueError("active service token binding mismatch")
    # Authority is taken only from the independently replayed controlled-delivery Release.
    independently_reloaded_release=delivery_arguments["verified_release"]
    _validate(authorization,reloaded,independently_reloaded_release)
    en,cn,issuance,data,commitment=_issuance(authorization); ledger=Path(authorization.ledger_directory)
    _write_exclusive(ledger,en,data)
    try: _write_exclusive(ledger,cn,commitment)
    except Exception as exc:
        dfd=os.open(ledger,os.O_RDONLY|os.O_DIRECTORY|getattr(os,"O_NOFOLLOW",0))
        try:
            for name in (en,cn):
                try: os.unlink(name,dir_fd=dfd)
                except FileNotFoundError: pass
            os.fsync(dfd)
        except Exception as rollback: raise ValueError("issuance persistence-indeterminate") from rollback
        finally: os.close(dfd)
        raise ValueError("issuance commitment failed; durable full cleanup") from exc
    _require_ledger_attachment(authorization)
    return VerifiedTechnicalVerificationAuthorization._make(_canonical(asdict(authorization)).decode(),en,cn,issuance.fingerprint,_TOKEN)

def _reload_issued(marker):
    if type(marker) is not VerifiedTechnicalVerificationAuthorization or getattr(marker,"_marker",None) is not _TOKEN: raise ValueError("sealed authorization required")
    a=marker.authorization; en,cn,issuance,data,commitment=_issuance(a); ledger=_require_ledger_attachment(a)
    if marker.issuance_filename!=en or marker.commitment_filename!=cn or marker.issuance_fingerprint!=issuance.fingerprint or _read_regular(ledger,en)!=data or _read_regular(ledger,cn)!=commitment: raise ValueError("issuance invalid")
    return a,issuance

def _load_authorization_from_path(path):
    path=Path(path); raw=_read_regular(path.parent,path.name); doc=json.loads(raw)
    a=_authorization(doc["authorization"]); issued=TechnicalVerificationIssuanceEvidence(**doc["issuance"])
    en,cn,expected,data,commitment=_issuance(a)
    if path.parent!=Path(a.ledger_directory) or path.name!=en or raw!=data or issued!=expected or _read_regular(path.parent,cn)!=commitment: raise ValueError("technical issuance path invalid")
    _require_ledger_attachment(a)
    return a,VerifiedTechnicalVerificationAuthorization._make(_canonical(asdict(a)).decode(),en,cn,issued.fingerprint,_TOKEN)

def _raw_observe(a,route,expected_length,expected_digest,running,deployment,current_gate):
    receipt=require_active_running_deployment(running,deployment)
    request=f"GET {route.path} HTTP/1.1\r\nHost: 127.0.0.1:{a.target.port}\r\n\r\n".encode()
    # Re-run the complete persisted/current authority chain as the final operation
    # before opening this request's transport.
    current,receipt=current_gate()
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.settimeout(2)
    try:
        s.connect((a.target.address,a.target.port)); s.sendall(request); raw=b""
        while len(raw)<=_MAX_RESPONSE:
            part=s.recv(65536)
            if not part: break
            raw+=part
        if len(raw)>_MAX_RESPONSE: raise ValueError("response exceeds bound")
    finally: s.close()
    try: head,body=raw.split(b"\r\n\r\n",1); lines=head.decode("ascii").split("\r\n")
    except Exception as exc: raise ValueError("response framing invalid") from exc
    expected_headers=(("Content-Type",route.media_type),("Content-Length",str(expected_length)),("X-BriefForge-Service-Token",receipt._service_token.hex()),("Connection","close"))
    actual=[]
    for line in lines[1:]:
        if ": " not in line: raise ValueError("header malformed")
        actual.append(tuple(line.split(": ",1)))
    if lines[0]!="HTTP/1.1 200 OK" or tuple(actual)!=expected_headers or len(body)!=expected_length or hashlib.sha256(body).hexdigest()!=expected_digest: raise ValueError("response differs from exact deployment evidence")
    raw_token=bytes.fromhex(dict(actual)["X-BriefForge-Service-Token"])
    if not hashlib.sha256(raw_token).hexdigest()==a.service_token_digest or raw_token!=receipt._service_token: raise ValueError("service instance token mismatch")
    return RouteTransportObservation(route.path,hashlib.sha256(request).hexdigest(),lines[0],tuple(actual),len(body),hashlib.sha256(body).hexdigest(),a.service_instance_identity,a.service_token_digest,"exact-response-observed")

def _links(a):
    raw=(("deployment-authorizes-observation",a.deployment_fingerprint,a.identity),("verification-authorization-consumed-by",a.identity,a.attempt_identity),("attempt-observes-service",a.attempt_identity,a.service_instance_identity),("attempt-produces-evidence",a.attempt_identity,a.evidence_identity))
    return tuple(TechnicalPublicationAuditLink(k,s,t,_digest({"kind":k,"source":s,"target":t})) for k,s,t in raw)

def _make_evidence(a,issuance,observations,observed_start,observed_end):
    ledger=Path(a.ledger_directory); ep=ledger/_name(a.identity,"technical-observation-evidence.json"); cp=ledger/_name(a.identity,"technical-observation-evidence.commitment")
    provisional=TechnicalPublicationEvidence(a.evidence_identity,_VERSION,_POLICY,_PROFILE,_IMPLEMENTATION,_VERSION,a.identity,a.fingerprint,issuance.fingerprint,a.deployment_fingerprint,a.service_instance_identity,a.service_token_digest,a.target,a.routes,observations,a.attempt_identity,a.authorization_time,observed_start,observed_end,observed_start,observed_end,a.ledger_directory,a.ledger_device,a.ledger_inode,str(ep),str(cp),a.exclusions,"exact-bounded-loopback-responses-observed",_links(a),"")
    return TechnicalPublicationEvidence(**{**asdict(provisional),"target":a.target,"routes":a.routes,"observations":observations,"exclusions":a.exclusions,"audit_links":provisional.audit_links,"fingerprint":compute_technical_publication_evidence_fingerprint(provisional)})

def _blocked(code,state="deployment-completed-verification-failed"):
    return TechnicalVerificationResult((TechnicalPublicationFinding(code,"/verification",code.replace("-"," ")),),state,None)

def verify_technical_publication(*,deployment: VerifiedLoopbackDeployment,running: RunningLoopbackDeployment,deployment_authorization,authorization,
        delivery_arguments,delivery_authorization,historical_lifecycle_scope,current_lifecycle_scope):
    try: a,issuance=_reload_issued(authorization)
    except Exception: return _blocked("verification-authorization-not-issued")
    ledger=Path(a.ledger_directory)
    try: _write_exclusive(ledger,_name(a.identity,"technical-verification-consumed"),_canonical(asdict(TechnicalVerificationConsumption(a.identity,a.fingerprint,a.attempt_identity,issuance.fingerprint))))
    except FileExistsError: return _blocked("verification-authorization-consumed")
    except Exception: return _blocked("verification-consumption-persistence-indeterminate","verification-consumption-indeterminate")
    try:
        def current_gate():
            try:
                current=_reload_deployment_chain(deployment,deployment_authorization,delivery_arguments,delivery_authorization,historical_lifecycle_scope,current_lifecycle_scope,True)
                receipt=require_active_running_deployment(running,current)
                if (current.fingerprint!=a.deployment_fingerprint or current.evidence.service_instance_identity!=a.service_instance_identity
                    or current.evidence.service_token_digest!=a.service_token_digest or current.evidence.target!=a.target or current.evidence.routes!=a.routes
                    or hashlib.sha256(receipt._service_token).hexdigest()!=a.service_token_digest): raise ValueError("deployment binding drift")
                return current,receipt
            except Exception as exc: raise PermissionError("technical lifecycle drift") from exc
        reloaded,_=current_gate()
        observed_start=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        observations=tuple(_raw_observe(a,r,n,d,running,reloaded,current_gate) for r,n,d in zip(a.routes,reloaded.evidence.route_lengths,reloaded.evidence.route_sha256))
        observed_end=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        if len(observations)!=len(a.routes): raise ValueError("route closure incomplete")
        evidence=_make_evidence(a,issuance,observations,observed_start,observed_end); data=_canonical(asdict(evidence)); ep=Path(evidence.evidence_path); cp=Path(evidence.commitment_path)
        current_gate()  # final complete gate immediately before the first success write
        _write_exclusive(ledger,ep.name,data)
        marker=VerifiedTechnicalPublication._make(data.decode(),evidence.fingerprint,_TOKEN)
        try: _write_exclusive(ledger,cp.name,_canonical({"evidence_sha256":hashlib.sha256(data).hexdigest(),"fingerprint":evidence.fingerprint,"deployment_fingerprint":a.deployment_fingerprint,"service_instance_identity":a.service_instance_identity,"service_token_digest":a.service_token_digest}))
        except Exception: return TechnicalVerificationResult((TechnicalPublicationFinding("technical-observation-completion-pending","/verification","technical observation evidence durable but commitment missing"),),"completion-pending",marker)
        return TechnicalVerificationResult((),"bounded-observation-succeeded",verify_persisted_technical_publication(deployment=reloaded,deployment_authorization=deployment_authorization,authorization=authorization,verified=marker,delivery_arguments=delivery_arguments,delivery_authorization=delivery_authorization,historical_lifecycle_scope=historical_lifecycle_scope,current_lifecycle_scope=current_lifecycle_scope))
    except PermissionError: return _blocked("technical-lifecycle-drift","deployment-completed-verification-failed-consumed-lifecycle-drift")
    except Exception: return _blocked("technical-transport-observation-failed")

def _validate_persisted_technical_publication(*,deployment,deployment_authorization,authorization,verification_evidence_path,
        delivery_arguments,delivery_authorization,historical_lifecycle_scope,current_lifecycle_scope,allow_missing_commitment=False):
    a,issuance=_reload_issued(authorization)
    reloaded=_reload_deployment_chain(deployment,deployment_authorization,delivery_arguments,delivery_authorization,historical_lifecycle_scope,current_lifecycle_scope,False)
    _validate(a,reloaded,delivery_arguments["verified_release"])
    ledger=_require_ledger_attachment(a); path=Path(verification_evidence_path)
    expected_ep=_name(a.identity,"technical-observation-evidence.json"); expected_cp=_name(a.identity,"technical-observation-evidence.commitment")
    if path.parent!=ledger or path.name!=expected_ep: raise ValueError("technical evidence path binding invalid")
    data=_read_regular(ledger,expected_ep); parsed=_evidence(json.loads(data))
    if data!=_canonical(asdict(parsed)) or parsed.fingerprint!=compute_technical_publication_evidence_fingerprint(parsed): raise ValueError("technical evidence invalid")
    if (parsed.ledger_directory,parsed.ledger_device,parsed.ledger_inode)!=(a.ledger_directory,a.ledger_device,a.ledger_inode): raise ValueError("technical ledger binding invalid")
    if Path(parsed.evidence_path)!=path or Path(parsed.commitment_path)!=ledger/expected_cp: raise ValueError("technical evidence path binding invalid")
    if parsed.deployment_fingerprint!=reloaded.fingerprint or parsed.service_instance_identity!=reloaded.evidence.service_instance_identity or parsed.service_token_digest!=reloaded.evidence.service_token_digest or parsed.authorization_fingerprint!=a.fingerprint or parsed.issuance_fingerprint!=issuance.fingerprint: raise ValueError("technical evidence cross-binding invalid")
    expected=tuple(zip(reloaded.evidence.routes,reloaded.evidence.route_lengths,reloaded.evidence.route_sha256))
    if len(parsed.observations)!=len(expected): raise ValueError("observation closure invalid")
    consumption=_canonical(asdict(TechnicalVerificationConsumption(a.identity,a.fingerprint,a.attempt_identity,issuance.fingerprint)))
    if _read_regular(ledger,_name(a.identity,"technical-verification-consumed"))!=consumption: raise ValueError("verification consumption invalid")
    try:
        start=datetime.strptime(parsed.bounded_interval_start,"%Y-%m-%dT%H:%M:%S.%fZ"); end=datetime.strptime(parsed.bounded_interval_end,"%Y-%m-%dT%H:%M:%S.%fZ")
        if start>end or parsed.attempt_time!=parsed.bounded_interval_start or parsed.completion_time!=parsed.bounded_interval_end: raise ValueError
    except Exception as exc: raise ValueError("observation chronology invalid") from exc
    for observation,(route,length,digest) in zip(parsed.observations,expected):
        request=f"GET {route.path} HTTP/1.1\r\nHost: 127.0.0.1:{a.target.port}\r\n\r\n".encode()
        headers=(("Content-Type",route.media_type),("Content-Length",str(length)),("X-BriefForge-Service-Token",None),("Connection","close"))
        if (observation.route!=route.path or observation.request_sha256!=hashlib.sha256(request).hexdigest()
            or observation.status_line!="HTTP/1.1 200 OK" or len(observation.headers)!=len(headers)
            or tuple((k,None if k=="X-BriefForge-Service-Token" else v) for k,v in observation.headers)!=headers
            or hashlib.sha256(bytes.fromhex(dict(observation.headers)["X-BriefForge-Service-Token"])).hexdigest()!=a.service_token_digest
            or observation.service_instance_identity!=a.service_instance_identity or observation.service_token_digest!=a.service_token_digest
            or observation.body_length!=length or observation.body_sha256!=digest or observation.outcome!="exact-response-observed"): raise ValueError("observation differs")
    reproduced=_make_evidence(a,issuance,parsed.observations,parsed.bounded_interval_start,parsed.bounded_interval_end)
    if parsed!=reproduced: raise ValueError("technical evidence differs from independent reproduction")
    commitment=_canonical({"evidence_sha256":hashlib.sha256(data).hexdigest(),"fingerprint":parsed.fingerprint,"deployment_fingerprint":a.deployment_fingerprint,"service_instance_identity":a.service_instance_identity,"service_token_digest":a.service_token_digest})
    missing=False
    try:
        if _read_regular(ledger,expected_cp)!=commitment: raise ValueError("technical commitment invalid")
    except FileNotFoundError:
        if not allow_missing_commitment: raise
        missing=True
    _require_ledger_attachment(a)
    return VerifiedTechnicalPublication._make(data.decode(),parsed.fingerprint,_TOKEN),missing,commitment

def verify_persisted_technical_publication(*,deployment,deployment_authorization,authorization,verified,
        delivery_arguments,delivery_authorization,historical_lifecycle_scope,current_lifecycle_scope):
    if type(verified) is not VerifiedTechnicalPublication or getattr(verified,"_marker",None) is not _TOKEN: raise ValueError("sealed technical evidence required")
    e=verified.evidence
    if verified._document!=_canonical(asdict(e)).decode() or verified.fingerprint!=e.fingerprint: raise ValueError("sealed technical document invalid")
    loaded,_,_=_validate_persisted_technical_publication(deployment=deployment,deployment_authorization=deployment_authorization,
        authorization=authorization,verification_evidence_path=e.evidence_path,delivery_arguments=delivery_arguments,
        delivery_authorization=delivery_authorization,historical_lifecycle_scope=historical_lifecycle_scope,current_lifecycle_scope=current_lifecycle_scope)
    if loaded.fingerprint!=verified.fingerprint: raise ValueError("technical marker mismatch")
    return loaded

def verify_technical_publication_current_availability(verified, *, deployment,running,deployment_authorization,authorization,
        delivery_arguments,delivery_authorization,historical_lifecycle_scope,current_lifecycle_scope):
    try:
        persisted=verify_persisted_technical_publication(deployment=deployment,deployment_authorization=deployment_authorization,
            authorization=authorization,verified=verified,delivery_arguments=delivery_arguments,
            delivery_authorization=delivery_authorization,historical_lifecycle_scope=historical_lifecycle_scope,
            current_lifecycle_scope=current_lifecycle_scope)
        current=verify_deployment_current_availability(deployment,running=running,delivery_arguments=delivery_arguments,
            delivery_authorization=delivery_authorization,authorization=deployment_authorization,
            historical_lifecycle_scope=historical_lifecycle_scope,current_lifecycle_scope=current_lifecycle_scope)
        if current.state!="current-availability-established": raise ValueError("deployment unavailable")
        return TechnicalVerificationResult((),"current-availability-established",persisted)
    except Exception: return _blocked("current-availability-not-established","not-established")

def verify_technical_publication_and_shutdown(*,deployment_result,deployment_authorization,authorization,
        running,delivery_arguments,delivery_authorization,
        historical_lifecycle_scope,current_lifecycle_scope):
    """Run the fixed verifier and unconditionally stop its bounded listener."""
    if type(deployment_result) is not LoopbackDeploymentResult or deployment_result.state!="active":
        return CoordinatedTechnicalVerificationResult(
            _blocked("active-deployment-required"),
            stop_bounded_loopback_deployment(deployment_result,authorization=deployment_authorization,
                delivery_arguments=delivery_arguments,delivery_authorization=delivery_authorization,
                historical_lifecycle_scope=historical_lifecycle_scope,current_lifecycle_scope=current_lifecycle_scope),
        )
    try:
        verification=verify_technical_publication(
            deployment=deployment_result.verified,running=running,deployment_authorization=deployment_authorization,authorization=authorization,
            delivery_arguments=delivery_arguments,
            delivery_authorization=delivery_authorization,
            historical_lifecycle_scope=historical_lifecycle_scope,
            current_lifecycle_scope=current_lifecycle_scope,
        )
    finally:
        shutdown=stop_bounded_loopback_deployment(deployment_result,authorization=deployment_authorization,
            delivery_arguments=delivery_arguments,delivery_authorization=delivery_authorization,
            historical_lifecycle_scope=historical_lifecycle_scope,current_lifecycle_scope=current_lifecycle_scope)
    return CoordinatedTechnicalVerificationResult(verification,shutdown)

def load_persisted_technical_publication(*,deployment_authorization_evidence_path,deployment_evidence_path,
        verification_authorization_evidence_path,verification_evidence_path,delivery_arguments,delivery_authorization,
        historical_lifecycle_scope,current_lifecycle_scope):
    """Read-only restart loader for the complete technical-publication authority chain."""
    deployment=load_persisted_loopback_deployment(authorization_evidence_path=deployment_authorization_evidence_path,
        deployment_evidence_path=deployment_evidence_path,delivery_arguments=delivery_arguments,
        delivery_authorization=delivery_authorization,historical_lifecycle_scope=historical_lifecycle_scope,
        current_lifecycle_scope=current_lifecycle_scope)
    deployment_authorization_marker=load_persisted_loopback_deployment_authorization(deployment_authorization_evidence_path)
    _,authorization=_load_authorization_from_path(verification_authorization_evidence_path)
    loaded,_,_=_validate_persisted_technical_publication(deployment=deployment,deployment_authorization=deployment_authorization_marker,
        authorization=authorization,verification_evidence_path=verification_evidence_path,delivery_arguments=delivery_arguments,
        delivery_authorization=delivery_authorization,historical_lifecycle_scope=historical_lifecycle_scope,current_lifecycle_scope=current_lifecycle_scope)
    return loaded

def reconcile_technical_observation_commitment(*,deployment_authorization_evidence_path,deployment_evidence_path,
        verification_authorization_evidence_path,verification_evidence_path,delivery_arguments,delivery_authorization,
        historical_lifecycle_scope,current_lifecycle_scope):
    try:
        deployment=load_persisted_loopback_deployment(authorization_evidence_path=deployment_authorization_evidence_path,
            deployment_evidence_path=deployment_evidence_path,delivery_arguments=delivery_arguments,
            delivery_authorization=delivery_authorization,historical_lifecycle_scope=historical_lifecycle_scope,
            current_lifecycle_scope=current_lifecycle_scope)
        deployment_authorization=load_persisted_loopback_deployment_authorization(deployment_authorization_evidence_path)
        a,authorization=_load_authorization_from_path(verification_authorization_evidence_path); ledger=_require_ledger_attachment(a)
        verified,missing,commitment=_validate_persisted_technical_publication(deployment=deployment,deployment_authorization=deployment_authorization,
            authorization=authorization,verification_evidence_path=verification_evidence_path,delivery_arguments=delivery_arguments,
            delivery_authorization=delivery_authorization,historical_lifecycle_scope=historical_lifecycle_scope,
            current_lifecycle_scope=current_lifecycle_scope,allow_missing_commitment=True)
        if missing: _write_exclusive(ledger,_name(a.identity,"technical-observation-evidence.commitment"),commitment)
        verified=load_persisted_technical_publication(deployment_authorization_evidence_path=deployment_authorization_evidence_path,
            deployment_evidence_path=deployment_evidence_path,verification_authorization_evidence_path=verification_authorization_evidence_path,
            verification_evidence_path=verification_evidence_path,delivery_arguments=delivery_arguments,
            delivery_authorization=delivery_authorization,historical_lifecycle_scope=historical_lifecycle_scope,
            current_lifecycle_scope=current_lifecycle_scope)
        return TechnicalVerificationResult((),"bounded-observation-succeeded",verified)
    except Exception: return _blocked("technical-reconciliation-blocked","deployment-completed-verification-indeterminate")
