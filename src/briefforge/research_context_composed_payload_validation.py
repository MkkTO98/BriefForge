"""Independent, closed local admission of research_context.v1 composed packages.

The inert producer address is provenance, never a filesystem input. This module owns
transport and consistency checks, not economic selection, arithmetic or publication.
"""
from dataclasses import asdict, dataclass, fields
import hashlib
import inspect
import json
import os
from pathlib import Path
import re
import stat
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

VALIDATOR_VERSION = 'briefforge.research-context-composed-payload-validator.v1.0.0'
CONTRACT_VERSION = 'research-context.composed-payload.contract.v1.0.0'
PROFILE_ID = 'research-context.composed-payload.profile.single-net-margin-partial.v1.0.0'
_HASH = re.compile(r'[0-9a-f]{64}\Z')
_SAFE = re.compile(r'[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*\Z')
_ROOT = Path(__file__).absolute().parents[2]
# These constants are consumer-owned. Packaged self-assertions never replace them.
_RESOURCE_TABLE = {
    'companion_schema': ('contracts/research_context_composed_payload_v1/schemas/companion.schema.json',6173,'86d25cef5c1a4df600fa38a00ab1364d4b89420e1c7895256ab87c86f4e266b7'),
    'equity_schema': ('contracts/research_context_composed_payload_v1/schemas/equity-observation.schema.json',8638,'1be88b77c7a0a2ab4a063d804874be982735d30fe46be0d2e966e4770911242e'),
    'directory_allowlist': ('contracts/research_context_composed_payload_v1/DIRECTORY_ALLOWLIST.json',898,'8042adfb1b73f3c09ffbc2f03f291a1fff4f9e567ce47872dc73c8c1856d7c06'),
    'context_registry': ('contracts/research_context_v1/producer_registry.json',1292,'b552acf8e9b216b6204d98ab452d9af15132eef6d5171e331fe8973f83b0ab25'),
    'context_registry_schema': ('contracts/research_context_v1/schemas/producer_registry.schema.json',3054,'c80bf65df0d8c8f3c056c319a6e96d6d05344ad9f91c159326ac026f07a0ed4d'),
    'context_schema': ('contracts/research_context_v1/schemas/research_context.schema.json',11721,'84aa21bd81447502092bd8faaba58b665baf4ea83e4e443278466236e360f3a8'),
}
_STATES = (('equity','available'),('macro','unavailable'),('knowledge','blocked'))
_REASONS = ([],['no_accepted_matching_artifact'],['general_company_claim_export_not_authoritative'])
_PAIRS = (('equity','macro'),('equity','knowledge'),('macro','knowledge'))


@dataclass(frozen=True, slots=True)
class FilePin:
    byte_size: int
    sha256: str


@dataclass(frozen=True, slots=True)
class ManifestPins:
    manifest_txt: FilePin
    manifest_sha256: FilePin


@dataclass(frozen=True, slots=True)
class ContextPins:
    context_id: str
    equity_component_id: str
    entity_id: str
    contract_version: str
    profile_id: str
    document: FilePin
    manifests: ManifestPins


@dataclass(frozen=True, slots=True)
class SourceGrain:
    entity_key: str
    track: str
    source_period_class: str
    period_start: str
    period_end: str
    ratio_id: str


@dataclass(frozen=True, slots=True)
class SourceAddress:
    component_path: str
    component_sha256: str
    zero_based_row_index: int
    grain: SourceGrain


@dataclass(frozen=True, slots=True)
class AcceptancePins:
    results: FilePin
    manifests: ManifestPins
    result_key: str
    result_index: int


@dataclass(frozen=True, slots=True)
class InheritedSourcePins:
    component_file: str
    component_file_sha256: str
    leaf: str
    manifest_sha256_file_sha256: str
    manifest_txt_sha256: str
    source_package_id: str


@dataclass(frozen=True, slots=True)
class ProducerPins:
    git_commit: str
    git_tree: str
    module: str
    name: str
    version: str


@dataclass(frozen=True, slots=True)
class InheritedVersionPins:
    formula_version: str
    producer_profile_version: str
    producer_schema_version: str


@dataclass(frozen=True, slots=True)
class SourcePins:
    bundle_id: str
    bundle_contract_version: str
    bundle_profile_id: str
    bundle_profile_version: str
    component_id: str
    component_contract_version: str
    component_path: str
    component: FilePin
    descriptor: FilePin
    quality: FilePin
    manifests: ManifestPins
    producer: ProducerPins
    inherited_source: InheritedSourcePins
    inherited_versions: InheritedVersionPins


@dataclass(frozen=True, slots=True)
class ResourcePins:
    companion_schema: FilePin
    equity_schema: FilePin
    directory_allowlist: FilePin
    context_registry: FilePin
    context_registry_schema: FilePin
    context_schema: FilePin


@dataclass(frozen=True, slots=True)
class ConsumerTrustPins:
    contract_version: str
    profile_id: str
    context: ContextPins
    source: SourcePins
    acceptance: AcceptancePins
    address: SourceAddress
    resources: ResourcePins


@dataclass(frozen=True, slots=True)
class CompanionPins:
    companion_id: str
    record_id: str
    manifests: ManifestPins


@dataclass(frozen=True, slots=True)
class ComposedPackageRequest:
    package_dir: Path
    trust: ConsumerTrustPins
    expected_identity: CompanionPins


@dataclass(frozen=True, slots=True)
class ValidatedComposedPackage:
    identity: CompanionPins
    context_id: str
    status: str
    component_states: tuple[tuple[str,str], ...]
    equity_payload_json: bytes
    regular_file_count: int
    total_bytes: int


@dataclass(frozen=True, slots=True)
class ComposedPackageError(Exception):
    code: str
    detail: str
    relative_path: str | None = None


class _PublicSignature(inspect.Signature):
    """Display real class annotations by their contract names, not module paths."""

    def __str__(self) -> str:
        rendered = super().__str__()
        for parameter in self.parameters.values():
            annotation = parameter.annotation
            if isinstance(annotation, type):
                rendered = rendered.replace(annotation.__module__ + '.' + annotation.__qualname__,
                                            annotation.__qualname__)
        annotation = self.return_annotation
        if isinstance(annotation, type):
            rendered = rendered.replace(annotation.__module__ + '.' + annotation.__qualname__,
                                        annotation.__qualname__)
        return rendered


def _fail(code: str, detail: str = 'contract binding differs', relative_path: str | None = None) -> None:
    raise ComposedPackageError(code, detail, relative_path)


def _need(condition: bool, code: str, detail: str = 'contract binding differs', relative_path: str | None = None) -> None:
    if not condition:
        _fail(code, detail, relative_path)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(',', ':')).encode('ascii')


def _same(a: Any, b: Any) -> bool:
    return _canonical(a) == _canonical(b)


def _record(obj: dict, excluded: tuple[str,...], prefix: str) -> str:
    return prefix + _sha(_canonical({k:v for k,v in obj.items() if k not in excluded}))


def _safe(value: str) -> bool:
    return type(value) is str and len(value)<=240 and bool(_SAFE.fullmatch(value)) and all(s not in ('.','..') for s in value.split('/'))


def _pin_type(value: Any, cls: type) -> None:
    _need(type(value) is cls,'TRUST_INPUT_INVALID','typed caller pin required')
    nested = {
        ManifestPins: {'manifest_txt':FilePin,'manifest_sha256':FilePin},
        ContextPins:{'document':FilePin,'manifests':ManifestPins},
        SourceAddress:{'grain':SourceGrain},
        AcceptancePins:{'results':FilePin,'manifests':ManifestPins},
        SourcePins:{'component':FilePin,'descriptor':FilePin,'quality':FilePin,'manifests':ManifestPins,'producer':ProducerPins,'inherited_source':InheritedSourcePins,'inherited_versions':InheritedVersionPins},
        ConsumerTrustPins:{'context':ContextPins,'source':SourcePins,'acceptance':AcceptancePins,'address':SourceAddress,'resources':ResourcePins},
        CompanionPins:{'manifests':ManifestPins},
    }
    hash_fields={'sha256','component_sha256','component_file_sha256','manifest_sha256_file_sha256','manifest_txt_sha256'}
    prefixes={'context_id':'rcv1-','equity_component_id':'rcc1-','bundle_id':'efb1-','bundle_profile_id':'efp1-','source_package_id':'efsp1-','companion_id':'rcpc1-','record_id':'rcpr1-'}
    for f in fields(cls):
        x=getattr(value,f.name)
        sub=(FilePin if cls is ResourcePins else nested.get(cls,{}).get(f.name))
        if sub:
            _pin_type(x,sub)
        elif f.name in ('byte_size','zero_based_row_index','result_index'):
            _need(type(x) is int and 0<=x<=9007199254740991,'TRUST_INPUT_INVALID','integer pin invalid')
        else:
            _need(type(x) is str and 0<len(x)<=512 and not any(ord(c)<32 or ord(c)==127 for c in x),'TRUST_INPUT_INVALID','text pin invalid')
            if f.name in hash_fields or (cls is ProducerPins and f.name in ('git_commit','git_tree')):
                _need(bool(_HASH.fullmatch(x)) if f.name in hash_fields else bool(re.fullmatch(r'[0-9a-f]{40}',x)),'TRUST_INPUT_INVALID','digest syntax invalid')
            if f.name in prefixes:
                _need(x.startswith(prefixes[f.name]) and bool(_HASH.fullmatch(x[len(prefixes[f.name]):])),'TRUST_INPUT_INVALID','identity syntax invalid')
            if f.name=='component_id':
                prefix='efc1-' if cls is SourcePins else 'rcc1-'
                _need(x.startswith(prefix) and bool(_HASH.fullmatch(x[len(prefix):])),'TRUST_INPUT_INVALID','component identity invalid')
            if f.name in ('component_path','result_key','component_file','leaf'):
                _need(_safe(x),'TRUST_INPUT_INVALID','unsafe inert source label')


def _trust(request: ComposedPackageRequest) -> None:
    _need(type(request) is ComposedPackageRequest,'TRUST_INPUT_INVALID','typed request required')
    _pin_type(request.trust,ConsumerTrustPins)
    _pin_type(request.expected_identity,CompanionPins)
    t=request.trust
    fixed={
        'contract': (t.contract_version,CONTRACT_VERSION,'UNSUPPORTED_CONTRACT'),
        'profile': (t.profile_id,PROFILE_ID,'UNSUPPORTED_PROFILE'),
        'context_contract':(t.context.contract_version,'research-context.contract.v1.0.0','UNSUPPORTED_CONTRACT'),
        'context_profile':(t.context.profile_id,'research-context.profile.base.v1.0.0','UNSUPPORTED_PROFILE'),
        'bundle_contract':(t.source.bundle_contract_version,'equityforge.research-bundle.contract.v1.0.0','UNSUPPORTED_CONTRACT'),
        'bundle_profile':(t.source.bundle_profile_version,'equityforge.research-bundle.profile.base.v1.0.0','UNSUPPORTED_PROFILE'),
        'component_contract':(t.source.component_contract_version,'equityforge.component.direct-tenq-ratios.v1.0.0','UNSUPPORTED_SCHEMA_VERSION'),
        'producer_module':(t.source.producer.module,'src.filing_observations.research_bundle','UNSUPPORTED_PRODUCER'),
        'producer_name':(t.source.producer.name,'EquityForge research bundle builder','UNSUPPORTED_PRODUCER'),
        'producer_version':(t.source.producer.version,'research_bundle.v1','UNSUPPORTED_PRODUCER'),
        'formula':(t.source.inherited_versions.formula_version,'tenq_ratio_research.v1','UNSUPPORTED_SCHEMA_VERSION'),
        'source_profile':(t.source.inherited_versions.producer_profile_version,'not_declared_in_source_artifact','UNSUPPORTED_PROFILE'),
        'source_schema':(t.source.inherited_versions.producer_schema_version,'tenq_ratio_research_coverage.v1 (coverage metadata only; row schema not declared)','UNSUPPORTED_SCHEMA_VERSION'),
        'component_path':(t.source.component_path,'data/direct_tenq_ratios.json','UNSUPPORTED_CONTRACT'),
        'address_path':(t.address.component_path,'data/direct_tenq_ratios.json','UNSUPPORTED_CONTRACT'),
    }
    for _,(actual,want,code) in fixed.items():
        _need(actual==want,code,'unsupported caller pin')
    _need(t.address.component_sha256==t.source.component.sha256,'TRUST_INPUT_INVALID','source address digest differs')


def _path(root: Path) -> Path:
    _need(isinstance(root,Path) and root.is_absolute(),'INPUT_PATH_INVALID','explicit absolute Path required')
    raw=str(root)
    _need(not raw.startswith('//') and '\\' not in raw and not any(ord(c)<32 or ord(c)==127 for c in raw) and all(x not in ('.','..') for x in raw.split('/')[1:]),'UNSAFE_PATH','unsafe directory spelling')
    return root


def _key(s: os.stat_result) -> tuple[int,...]:
    return (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)


def _ancestors(root: Path) -> os.stat_result:
    try:
        for path in reversed((root,*root.parents)):
            s=path.lstat()
            _need(not stat.S_ISLNK(s.st_mode),'SYMLINK_FORBIDDEN','link in directory ancestry')
            _need(stat.S_ISDIR(s.st_mode),'INPUT_PATH_INVALID','directory unavailable')
        return root.lstat()
    except OSError as exc:
        raise ComposedPackageError('INPUT_PATH_INVALID','directory unavailable') from exc


def _resource(name: str) -> bytes:
    path,size,digest=_RESOURCE_TABLE[name]
    try:
        before=(_ROOT/path).lstat()
        _need(stat.S_ISREG(before.st_mode) and before.st_nlink==1,'RESOURCE_HASH_MISMATCH','local resource invalid',path)
        with (_ROOT/path).open('rb') as stream:raw=stream.read(1048577)
        _need(_key(before)==_key((_ROOT/path).lstat()),'RESOURCE_CHANGED_DURING_VALIDATION','resource changed',path)
    except OSError as exc:raise ComposedPackageError('RESOURCE_HASH_MISMATCH','consumer resource unreadable',path) from exc
    _need(len(raw)==size and _sha(raw)==digest,'RESOURCE_HASH_MISMATCH','consumer resource drift',path)
    return raw


def _inventory(root: Path, allow: dict) -> dict[str,os.stat_result]:
    base=_ancestors(root)
    seen={'':base}; problems=[];dirs=set();files=set()
    def walk(parent: Path, prefix: str):
        try:
            with os.scandir(parent) as stream:entries=sorted(stream,key=lambda e:e.name.encode('utf-8','surrogateescape'))
        except OSError as exc:raise ComposedPackageError('INPUT_PATH_INVALID','cannot enumerate package') from exc
        for e in entries:
            name=prefix+e.name
            try:s=e.stat(follow_symlinks=False)
            except OSError as exc:raise ComposedPackageError('UNSAFE_PATH','cannot inspect member',name) from exc
            seen[name]=s
            if not _safe(name):problems.append((3,name,'UNSAFE_PATH'))
            if stat.S_ISLNK(s.st_mode):problems.append((3,name,'SYMLINK_FORBIDDEN'))
            elif s.st_dev!=base.st_dev:problems.append((3,name,'MOUNT_CROSSING_FORBIDDEN'))
            elif stat.S_ISDIR(s.st_mode):
                dirs.add(name)
                if name in allow['directories'] and name.count('/')<allow['maximum_depth']:walk(parent/e.name,name+'/')
            elif stat.S_ISREG(s.st_mode):
                files.add(name)
                if s.st_nlink!=1:problems.append((3,name,'HARDLINK_FORBIDDEN'))
            else:problems.append((3,name,'SPECIAL_FILE_FORBIDDEN'))
    walk(root,'')
    names=list(seen); folded={}
    for name in names[1:]:
        previous=folded.setdefault(name.casefold(),name)
        if previous!=name:problems.append((3,min(previous,name),'CASE_COLLISION'))
    want_files=set(allow['files']);want_dirs=set(allow['directories'])
    for group,desired,extra,missing in ((files,want_files,'UNDECLARED_FILE','MISSING_FILE'),(dirs,want_dirs,'UNDECLARED_DIRECTORY','MISSING_DIRECTORY')):
        problems.extend((4,n,extra) for n in group-desired)
        problems.extend((4,n,missing) for n in desired-group)
    declared_files=files & want_files
    if len(declared_files)>allow['maximum_files']:problems.append((4,'','PACKAGE_TOO_LARGE'))
    for n in files:
        if seen[n].st_size>allow['maximum_file_bytes']:problems.append((4,n,'FILE_TOO_LARGE'))
    if sum(seen[n].st_size for n in declared_files)>allow['maximum_total_bytes']:problems.append((4,'','PACKAGE_TOO_LARGE'))
    if problems:
        code_order={
            3:('INPUT_PATH_INVALID','UNSAFE_PATH','SYMLINK_FORBIDDEN','HARDLINK_FORBIDDEN',
               'MOUNT_CROSSING_FORBIDDEN','SPECIAL_FILE_FORBIDDEN','CASE_COLLISION'),
            4:('UNDECLARED_FILE','MISSING_FILE','UNDECLARED_DIRECTORY',
               'MISSING_DIRECTORY','FILE_TOO_LARGE','PACKAGE_TOO_LARGE'),
        }
        _,name,code=min(problems,key=lambda p:(p[0],p[1]=='',
                         p[1].encode('utf-8','surrogateescape'),code_order[p[0]].index(p[2])))
        _fail(code,'closed package inventory rejected',name or None)
    return seen


def _read(root: Path, name: str, expected: os.stat_result, limit: int) -> bytes:
    try:
        path=root/name
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        try:
            _need(_key(os.fstat(fd))==_key(expected),'PACKAGE_CHANGED_DURING_VALIDATION','member changed',name)
            with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(limit+1)
            current=os.fstat(fd)
        finally:os.close(fd)
        _need(len(raw)<=limit,'FILE_TOO_LARGE','member exceeds bound',name)
        _need(_key(current)==_key(expected)==_key(path.lstat()) and len(raw)==expected.st_size,'PACKAGE_CHANGED_DURING_VALIDATION','member changed',name)
        return raw
    except ComposedPackageError:raise
    except OSError as exc:raise ComposedPackageError('PACKAGE_CHANGED_DURING_VALIDATION','member inaccessible',name) from exc


def _manifest(raw: bytes, data: dict[str,bytes], names: set[str], *, inner: bool, prefix: str='') -> None:
    try:text=raw.decode('ascii')
    except UnicodeError as exc:raise ComposedPackageError('MANIFEST_FORMAT','non-ascii manifest',prefix or None) from exc
    _need(raw.endswith(b'\n') and b'\r' not in raw,'MANIFEST_FORMAT','noncanonical manifest',prefix or None)
    entries=[]
    for line in text.splitlines():
        parts=line.split('  ') if not inner else line.split('\t')
        _need(len(parts)==(3 if inner else 2),'MANIFEST_FORMAT','invalid manifest row',prefix or None)
        name=parts[0] if inner else parts[1]
        count=parts[1] if inner else None
        digest=parts[2] if inner else parts[0]
        _need(_safe(name) and bool(_HASH.fullmatch(digest)) and (count is None or bool(re.fullmatch(r'0|[1-9][0-9]*',count))),'MANIFEST_FORMAT','invalid manifest entry',prefix or None)
        entries.append((name,int(count) if count is not None else None,digest))
    listed=[x[0] for x in entries]
    _need(listed==sorted(set(listed)),'MANIFEST_FORMAT','manifest order or uniqueness differs',prefix or None)
    _need(set(listed)==names,'MANIFEST_COVERAGE','manifest member coverage differs',prefix or None)
    for name,size,digest in entries:
        if size is not None:_need(len(data[prefix+name])==size,'SIZE_MISMATCH','manifest member size differs',prefix+name)
        _need(_sha(data[prefix+name])==digest,'HASH_MISMATCH','manifest digest differs',prefix+name)


def _pairs(pairs):
    result={}
    for key,value in pairs:
        _need(key not in result,'JSON_DUPLICATE_KEY','duplicate JSON object key')
        result[key]=value
    return result


def _reject_float(_):_fail('JSON_FLOAT_FORBIDDEN','floating JSON number prohibited')


def _parse(raw: bytes, name: str, *, proof: bool=False) -> Any:
    try:
        obj=json.loads(raw.decode('utf-8'),object_pairs_hook=_pairs,parse_float=_reject_float,parse_constant=_reject_float)
        def walk(x,depth=0):
            _need(depth<=128,'JSON_INVALID','JSON nesting bound exceeded',name)
            if isinstance(x,str):_need(not any(0xd800<=ord(c)<=0xdfff for c in x),'JSON_INVALID','invalid unicode scalar',name)
            elif isinstance(x,dict):
                for k,value in x.items():walk(k,depth+1);walk(value,depth+1)
            elif isinstance(x,list):
                for value in x:walk(value,depth+1)
        walk(obj)
        if not proof:_need(raw==_canonical(obj)+b'\n','NONCANONICAL_JSON','noncanonical JSON bytes',name)
        return obj
    except ComposedPackageError:raise
    except (UnicodeError,ValueError,RecursionError,TypeError,OverflowError) as exc:
        raise ComposedPackageError('JSON_INVALID','invalid JSON document',name) from exc


def _local_refs(obj):
    if isinstance(obj,dict):
        for key,value in obj.items():
            if key in ('$ref','$dynamicRef'):
                _need(type(value) is str and value.startswith('#/$defs/'),'LOCAL_REF_INVALID','nonlocal schema reference')
            _local_refs(value)
    elif isinstance(obj,list):
        for value in obj:_local_refs(value)


def _schema(schema,instance,name):
    _local_refs(schema)
    try:
        Draft202012Validator.check_schema(schema)
        errors=list(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(instance))
    except Exception as exc:raise ComposedPackageError('SCHEMA_INVALID','invalid local schema',name) from exc
    _need(not errors,'SCHEMA_INVALID','schema rejected document',name)


def _pinned(pin: FilePin, raw: bytes, code: str, name: str) -> None:
    _need(len(raw)==pin.byte_size and _sha(raw)==pin.sha256,code,'independent receipt differs',name)


def _witness(data,stem,pins,mapping):
    txt=data[f'proof/{stem}-manifest.txt'];sha=data[f'proof/{stem}-manifest.sha256']
    _pinned(pins.manifest_txt,txt,'SOURCE_PACKAGE_MISMATCH',f'proof/{stem}-manifest.txt')
    _pinned(pins.manifest_sha256,sha,'SOURCE_PACKAGE_MISMATCH',f'proof/{stem}-manifest.sha256')
    def parse(raw,inner):
        try:lines=raw.decode('ascii').splitlines()
        except UnicodeError as exc:raise ComposedPackageError('SOURCE_PACKAGE_MISMATCH','non-ascii source witness') from exc
        _need(raw.endswith(b'\n'),'SOURCE_PACKAGE_MISMATCH','source witness newline missing')
        out={}
        for line in lines:
            parts=line.split('\t') if inner else line.split('  ')
            _need(len(parts)==(3 if inner else 2),'SOURCE_PACKAGE_MISMATCH','source witness format')
            name=parts[0] if inner else parts[1];size=parts[1] if inner else None;digest=parts[2] if inner else parts[0]
            _need(_safe(name) and name not in out and bool(_HASH.fullmatch(digest)) and (size is None or bool(re.fullmatch(r'0|[1-9][0-9]*',size))),'SOURCE_PACKAGE_MISMATCH','source witness member invalid')
            out[name]=(int(size) if size is not None else None,digest)
        ordered=list(out)
        _need(ordered==sorted(ordered) or (not inner and ordered==sorted(n for n in ordered if n!='MANIFEST.txt')+['MANIFEST.txt']),'SOURCE_PACKAGE_MISMATCH','source witness ordering invalid')
        return out
    a=parse(txt,True);b=parse(sha,False)
    _need(set(b)==set(a)|{'MANIFEST.txt'} and b['MANIFEST.txt'][1]==_sha(txt) and all(b[n][1]==v[1] for n,v in a.items()),'SOURCE_PACKAGE_MISMATCH','source witness ledger mismatch')
    for original,local,pin in mapping:
        _need(original in a,'SOURCE_PACKAGE_MISMATCH','source witness member absent',local)
        _need(a[original]==(len(data[local]),_sha(data[local])),'SOURCE_SIZE_MISMATCH' if a[original][0]!=len(data[local]) else 'SOURCE_COMPONENT_MISMATCH','source witness member differs',local)
        _pinned(pin,data[local],'SOURCE_COMPONENT_MISMATCH',local)


def _semantic(data,documents,trust,receipt):
    d=documents['COMPOSED_PAYLOAD.json'];p=documents['payloads/equity.json'];c=documents['context/RESEARCH_CONTEXT.json'];r=p['source_record']
    _need(d['package_status']==c['package_status']=='partial','PACKAGE_STATUS_MISMATCH','only partial package admitted')
    dc=d['components'];cc=c['components']
    _need(len(dc)==len(cc)==3 and set(x['slot'] for x in dc)=={'equity','macro','knowledge'},'COMPONENT_SET','fixed component set required')
    _need([x['slot'] for x in dc]==[x['component_slot'] for x in cc]==[x[0] for x in _STATES],'COMPONENT_ORDER','fixed component order required')
    for i,(component,context) in enumerate(zip(dc,cc)):
        _need(component['state']==context['state']==_STATES[i][1] and context['usable'] is (i==0),'STATE_MISMATCH','typed component state differs')
        _need((component['payload'] is not None)==(i==0) and (context['provenance'] is not None)==(i==0),'STATE_PAYLOAD_MISMATCH','absent component claims payload')
        _need(component['reason_codes']==context['state_reason_codes']==_REASONS[i],'STATE_REASON_MISMATCH','typed reason differs')
        _need(component['component_id']==context['component_id'],'COMPONENT_ID_MISMATCH','component identity differs')
        _need(context['producer_id']==context['authority']==('equityforge','macroforge','knowledgeforge')[i] and context['domain']==('equity_financial_research','macroeconomic','sourced_knowledge')[i] and context['component_envelope_version']=='research-context.component-envelope.v1.0.0' and not context['ambiguous_candidate_ids'],'STATE_MISMATCH','component authority differs')
    _need([(x['left_slot'],x['right_slot']) for x in d['compatibility_findings']]==list(_PAIRS),'UNAUTHORIZED_JOIN','compatibility pair order differs')
    _need(_same(d['compatibility_findings'],c['compatibility_findings']) and all(x['status']=='blocked' and x['authorized_join'] is False and x['reason_codes']==sorted(set(x['reason_codes'])) for x in d['compatibility_findings']),'UNAUTHORIZED_JOIN','cross-domain join unauthorized')
    _need(d['context_binding']['context_id']==c['context_id']==p['context_id']==trust.context.context_id,'CONTEXT_ID_MISMATCH','context identity differs')
    _need(p['component_id']==cc[0]['component_id']==trust.context.equity_component_id,'COMPONENT_ID_MISMATCH','equity component differs')
    _need(p['entity_id']==trust.context.entity_id,'ENTITY_MISMATCH','entity identity differs')
    cb=d['context_binding'];source=d['source_binding'];v=cc[0]['provenance'];address=p['source_address']
    _need(cb['manifest_txt_sha256']==trust.context.manifests.manifest_txt.sha256 and cb['manifest_sha256_file_sha256']==trust.context.manifests.manifest_sha256.sha256 and cb['profile_id']==trust.context.profile_id and cb['contract_version']==trust.context.contract_version and cb['relative_path']=='context','CONTEXT_TRUST_MISMATCH','embedded context receipt differs')
    ref=dc[0]['payload']
    _need(ref['path']=='payloads/equity.json' and ref['media_type']=='application/json','STATE_PAYLOAD_MISMATCH','equity payload location differs')
    _need(ref['bytes']==len(data['payloads/equity.json']),'SIZE_MISMATCH','equity payload bytes differ','payloads/equity.json')
    _need(ref['sha256']==_sha(data['payloads/equity.json']),'HASH_MISMATCH','equity payload digest differs','payloads/equity.json')
    _need(d['resource_hashes']=={'companion_schema_sha256':trust.resources.companion_schema.sha256,'equity_schema_sha256':trust.resources.equity_schema.sha256},'RESOURCE_HASH_MISMATCH','schema resource assertion differs')
    _need(all(x=='data/direct_tenq_ratios.json' for x in (address['component_path'],source['component_path'],v['source_artifact_relative_path'])),'SOURCE_COMPONENT_MISMATCH','inert address differs')
    _witness(data,'bundle',trust.source.manifests,(('BUNDLE.json','proof/bundle-descriptor.json',trust.source.descriptor),('data/direct_tenq_ratios.json','proof/producer-component.json',trust.source.component),('quality/data_quality.json','proof/bundle-quality.json',trust.source.quality)))
    _witness(data,'acceptance',trust.acceptance.manifests,(('PUBLIC_CONSUMER_RESULTS.json','proof/acceptance-results.json',trust.acceptance.results),))
    descriptor=documents['proof/bundle-descriptor.json']
    matches=[x for x in descriptor['components'] if isinstance(x,dict) and x.get('stable_component_name')=='direct_tenq_ratios']
    _need(len(matches)==1,'SOURCE_COMPONENT_MISMATCH','source component not unique')
    component=matches[0]
    _need(source['manifest_txt_sha256']==v['source_package_manifest_txt_sha256']==trust.source.manifests.manifest_txt.sha256 and source['manifest_sha256_file_sha256']==v['source_package_manifest_sha256_file_sha256']==trust.source.manifests.manifest_sha256.sha256 and source['acceptance_manifest_txt_sha256']==trust.acceptance.manifests.manifest_txt.sha256 and source['acceptance_manifest_sha256_file_sha256']==trust.acceptance.manifests.manifest_sha256.sha256,'SOURCE_PACKAGE_MISMATCH','source manifest binding differs')
    _need(source['bundle_id']==p['source_bundle_id']==descriptor['bundle_id']==v['source_package_id']==trust.source.bundle_id,'SOURCE_PACKAGE_MISMATCH','bundle identity differs')
    _need(_same(p['source_package_identity'],component['source_package_identity']) and _same(p['source_package_identity'],asdict(trust.source.inherited_source)) and _same(p['inherited_versions'],component['inherited_versions']) and _same(p['inherited_versions'],asdict(trust.source.inherited_versions)) and _same(p['producer'],descriptor['producer']) and _same(p['producer'],asdict(trust.source.producer)),'SOURCE_PACKAGE_MISMATCH','inherited source pin differs')
    _need(descriptor['bundle_contract_version']==trust.source.bundle_contract_version and descriptor['profile']['profile_id']==trust.source.bundle_profile_id and descriptor['profile']['profile_contract_version']==trust.source.bundle_profile_version and component['component_contract_version']==trust.source.component_contract_version and v['source_contract_id']==trust.source.bundle_contract_version and v['source_contract_version']=='1.0.0' and v['validation_profile_id']==trust.source.bundle_profile_version and v['producer_version']==trust.source.producer.version and v['validation_result']=='pass','SOURCE_PACKAGE_MISMATCH','source version or validation differs')
    _need(source['component_id']==p['source_component_id']==component['component_id']==trust.source.component_id,'SOURCE_COMPONENT_MISMATCH','source component identity differs')
    _need(source['component_bytes']==v['source_artifact_byte_size']==component['byte_size']==len(data['proof/producer-component.json']),'SOURCE_SIZE_MISMATCH','source size differs')
    _need(source['component_sha256']==address['component_sha256']==v['source_artifact_sha256']==component['file_sha256']==trust.source.component.sha256,'SOURCE_COMPONENT_MISMATCH','source digest differs')
    _need(source['component_path']==address['component_path']==v['source_artifact_relative_path']==component['relative_path']==trust.source.component_path,'SOURCE_COMPONENT_MISMATCH','source path differs')
    selection=p['selection'];result_key=trust.acceptance.result_key;idx=trust.acceptance.result_index
    _need(selection['accepted_result_key']==result_key and type(selection['accepted_result_index']) is int and selection['accepted_result_index']==idx and selection['accepted_record_field']=='latest_usable' and selection['policy']=='accepted_source_bound_record_no_reselection','SOURCE_RECORD_MISMATCH','acceptance coordinates differ')
    try:
        selected=documents['proof/acceptance-results.json'][result_key]['results'][idx]
        accepted=selected['latest_usable']
        rows=documents['proof/producer-component.json']
        _need(type(rows) is list and trust.address.zero_based_row_index<len(rows) and type(accepted) is dict,'SOURCE_RECORD_MISMATCH','addressed witness absent')
        row=rows[trust.address.zero_based_row_index]
    except (KeyError,TypeError,IndexError) as exc:raise ComposedPackageError('SOURCE_RECORD_MISMATCH','addressed witness absent') from exc
    _need(_same(address,source['source_address']) and _same(address,accepted['source_row_identity']) and _same(address,asdict(trust.address)),'SOURCE_RECORD_MISMATCH','address differs')
    _need(selected['entity_key']==row['entity_key'] and selected['entity_name']==row['entity_name'],'ENTITY_MISMATCH','accepted entity differs')
    entity=c['entity_mappings'];_need(len(entity)==1,'ENTITY_MISMATCH','single entity required');entity=entity[0]
    _need(entity['entity_id']==p['entity_id'] and entity['mapping_status']=='resolved' and cc[0]['entity_ids']==[p['entity_id']] and entity['identifiers']['cik']['value']==r['entity_key']==address['grain']['entity_key']==row['entity_key'] and entity['identifiers']['aliases'][0]['alias']==r['entity_name']==row['entity_name'],'ENTITY_MISMATCH','entity binding differs')
    for field in ('period_start','period_end'):_need(r[field]==address['grain'][field]==row[field]==cc[0]['time_identity'][field]['value'],'PERIOD_MISMATCH','period differs')
    _need(r['period_start']<=r['period_end'],'PERIOD_MISMATCH','period reversed')
    availability=p['availability']
    _need(availability['date']==r['derived_availability_date_proxy']==row['derived_availability_date_proxy']==cc[0]['time_identity']['filing_date']['value']==cc[0]['time_identity']['effective_time']['value'] and availability['basis']==r['derived_availability_basis']=='max_input_filed_date_proxy_non_pit' and availability['pit_certified'] is False and all(availability[k] is None for k in ('accepted_at','publication_time','retrieval_time','revision_vintage_time')),'AVAILABILITY_MISMATCH','availability proxy differs')
    _need(cc[0]['time_identity']['filing_date']['authority']==cc[0]['time_identity']['effective_time']['authority']=='proxy' and all(cc[0]['time_identity'][k]['value'] is None for k in ('acceptance_timestamp','publication_time','retrieval_time','revision_vintage_time')),'AVAILABILITY_MISMATCH','time authority differs')
    measurement=p['measurement'];m=cc[0]['measurement_identity']
    _need(m['formula_id']==r['ratio_id']==measurement['formula_id']=='net_margin' and m['formula_version']==r['formula_version']==measurement['formula_version']=='tenq_ratio_research.v1' and measurement['kind']=='equityforge_calculated_ratio' and measurement['frequency']=='quarterly' and measurement['duration_class']=='first_quarter','MEASUREMENT_MISMATCH','measurement differs')
    _need(m['unit']==r['ratio_unit']==measurement['unit']=='ratio' and m['scale']==measurement['scale']=='1' and measurement['value_convention']=='fraction_not_percent' and measurement['input_currency']=='USD','UNIT_MISMATCH','unit differs')
    _need(_same(r,row) and all(_same(r[k],value) for k,value in address['grain'].items()),'SOURCE_RECORD_MISMATCH','full addressed row differs')
    for key in ('blocking_reasons','calculation_policy','derivation_status','derived_availability_basis','derived_availability_date_proxy','formula_version','period_start','period_end','ratio_unit','ratio_value','research_value_usable'):
        _need(_same(r[key],accepted[key]),'SOURCE_RECORD_MISMATCH','accepted scalar differs')
    for role in ('numerator','denominator'):
        for key,value in accepted['inputs_and_provenance'][role].items():
            _need(role+'_'+key in r and _same(r[role+'_'+key],value),'SOURCE_RECORD_MISMATCH','accepted operand differs')
    alias='ef-address:'+address['component_sha256']+':row:'+str(trust.address.zero_based_row_index)
    _need(selection['context_record_alias']==alias and v['source_record_ids']==entity['mapping_evidence_ids']==[alias] and v['selection_method']=='producer_selected_no_composer_reselection','SOURCE_RECORD_MISMATCH','source selection alias differs')
    _need(r['research_value_usable'] is True and r['derivation_status']=='computed' and r['blocking_reasons']==[] and type(r['ratio_value']) is str and bool(re.fullmatch(r'0\.[0-9]+',r['ratio_value'])),'MEASUREMENT_MISMATCH','one usable computed fraction required')
    _need(p['qualification_codes']==[x['code'] for x in descriptor['analytical_qualifications']],'QUALITY_MISMATCH','qualification codes differ')
    quality=documents['proof/bundle-quality.json'];qd=descriptor['quality_document']
    _need(quality['bundle_id']==descriptor['bundle_id'] and quality['schema_version']=='equityforge.research-bundle.data-quality.v1.0.0' and quality['bundle_validation_state']=='pass' and quality['quality_id']==qd['document_id'] and qd['relative_path']=='quality/data_quality.json' and qd['byte_size']==trust.source.quality.byte_size and qd['file_sha256']==trust.source.quality.sha256 and [(x['code'],x['severity'],x['text']) for x in quality['qualifications']]==[(x['code'],x['severity'],x['text']) for x in descriptor['analytical_qualifications']],'QUALITY_MISMATCH','quality witness differs')
    for component in cc:_need(component['component_id']==_record(component,('component_id',),'rcc1-'),'COMPONENT_ID_MISMATCH','context component identity differs')
    for finding in c['compatibility_findings']:_need(finding['finding_id']==_record(finding,('finding_id',),'rcf1-'),'FINDING_ID_MISMATCH','finding identity differs')
    _need(c['context_id']==_record(c,('context_id','context_package_build_time'),'rcv1-'),'CONTEXT_ID_MISMATCH','embedded context identity differs')
    _need(p['record_id']==d['record_id']==receipt.record_id==_record(p,('record_id',),'rcpr1-'),'RECORD_ID_MISMATCH','semantic record identity differs')
    _need(d['companion_id']==receipt.companion_id==_record(d,('companion_id','package_build_time'),'rcpc1-'),'COMPANION_ID_MISMATCH','companion identity differs')
    _need(c['contract_id']=='research_context.v1' and c['contract_version']=='research-context.contract.v1.0.0' and c['profile_id']=='research-context.profile.base.v1.0.0' and c['composer']=={'producer_id':'research-context.reference-composer','producer_version':'research-context.reference-composer.v1.0.0'} and c['canonicalization_policy']=='research-context.canonical-json.v1.0.0','EMBEDDED_CONTEXT_INVALID','embedded context unsupported')
    _need(p['rights']=='local_evidence_review_only_no_redistribution_grant' and p['producer_record_hash'] is None and p['authority_mode']=='complete_semantic_record_with_byte_exact_container_witness','SOURCE_PACKAGE_MISMATCH','rights or proof mode differs')


def validate_research_context_composed_payload(request: ComposedPackageRequest, /) -> ValidatedComposedPackage:
    """Admit one explicitly addressed, independently pinned, closed local package."""
    _trust(request)
    root=_path(request.package_dir)
    allow=json.loads(_resource('directory_allowlist'))
    _need(len(allow['files'])==20 and len(set(allow['files']))==20 and allow['maximum_depth']==3 and allow['maximum_file_bytes']==5242880 and allow['maximum_total_bytes']==8388608,'RESOURCE_HASH_MISMATCH','closed allowlist differs')
    before=_inventory(root,allow)
    names=sorted(n for n in before if n and stat.S_ISREG(before[n].st_mode))
    data={n:_read(root,n,before[n],allow['maximum_file_bytes']) for n in names}
    outer=set(names)-{'MANIFEST.txt','MANIFEST.sha256'}
    _manifest(data['MANIFEST.txt'],data,outer,inner=True)
    _manifest(data['MANIFEST.sha256'],data,outer|{'MANIFEST.txt'},inner=False)
    inner={n.removeprefix('context/') for n in names if n.startswith('context/')}
    _manifest(data['context/MANIFEST.txt'],data,inner-{'MANIFEST.txt','MANIFEST.sha256'},inner=True,prefix='context/')
    _manifest(data['context/MANIFEST.sha256'],data,inner-{'MANIFEST.sha256'},inner=False,prefix='context/')
    t=request.trust;receipt=request.expected_identity
    _pinned(receipt.manifests.manifest_txt,data['MANIFEST.txt'],'COMPANION_TRUST_MISMATCH','MANIFEST.txt')
    _pinned(receipt.manifests.manifest_sha256,data['MANIFEST.sha256'],'COMPANION_TRUST_MISMATCH','MANIFEST.sha256')
    for pin,name in ((t.context.document,'context/RESEARCH_CONTEXT.json'),(t.context.manifests.manifest_txt,'context/MANIFEST.txt'),(t.context.manifests.manifest_sha256,'context/MANIFEST.sha256')):
        _pinned(pin,data[name],'CONTEXT_TRUST_MISMATCH',name)
    resources={name:_resource(name) for name in _RESOURCE_TABLE}
    for name,raw in resources.items():_pinned(getattr(t.resources,name),raw,'RESOURCE_HASH_MISMATCH',_RESOURCE_TABLE[name][0])
    for key,name in (('companion_schema','schemas/companion.schema.json'),('equity_schema','schemas/equity-observation.schema.json'),('context_registry','context/registry/producer_registry.json'),('context_registry_schema','context/schemas/producer_registry.schema.json'),('context_schema','context/schemas/research_context.schema.json')):
        _need(data[name]==resources[key],'RESOURCE_HASH_MISMATCH','packaged resource differs',name)
    documents={n:_parse(data[n],n,proof=n.startswith('proof/')) for n in names if n.endswith('.json')}
    d=documents['COMPOSED_PAYLOAD.json']
    _need(type(d) is dict and d.get('contract_id')=='research_context.composed_payload.v1' and d.get('contract_version')==CONTRACT_VERSION,'UNSUPPORTED_CONTRACT','companion contract unsupported')
    _need(d.get('profile_id')==PROFILE_ID,'UNSUPPORTED_PROFILE','companion profile unsupported')
    _need(d.get('composer')=={'producer_id':'research-context.reference-composer','producer_version':'research-context.composed-payload-composer.v1.0.0'},'UNSUPPORTED_COMPOSER','composer unsupported')
    _need(d.get('projection_version')=='research-context.complete-semantic-ratio-record.v1.0.0' and d.get('canonicalization_policy')=='research-context.composed-payload.canonical-json.v1.0.0','UNSUPPORTED_SCHEMA_VERSION','serialization or projection unsupported')
    _need(documents['context/RESEARCH_CONTEXT.json'].get('contract_version')=='research-context.contract.v1.0.0','UNSUPPORTED_CONTRACT','embedded version unsupported')
    for schema_name,instance_name in (('schemas/companion.schema.json','COMPOSED_PAYLOAD.json'),('schemas/equity-observation.schema.json','payloads/equity.json'),('context/schemas/research_context.schema.json','context/RESEARCH_CONTEXT.json'),('context/schemas/producer_registry.schema.json','context/registry/producer_registry.json')):
        _schema(documents[schema_name],documents[instance_name],instance_name)
    try:_semantic(data,documents,t,receipt)
    except (KeyError,IndexError,TypeError,AttributeError) as exc:raise ComposedPackageError('SCHEMA_INVALID','required semantic binding absent') from exc
    after=_inventory(root,allow)
    _need({n:_key(x) for n,x in before.items()}=={n:_key(x) for n,x in after.items()},'PACKAGE_CHANGED_DURING_VALIDATION','package tree changed')
    for name in names:_need(_read(root,name,after[name],allow['maximum_file_bytes'])==data[name],'PACKAGE_CHANGED_DURING_VALIDATION','member changed',name)
    for name,raw in resources.items():_need(_resource(name)==raw,'RESOURCE_CHANGED_DURING_VALIDATION','consumer resource changed',_RESOURCE_TABLE[name][0])
    return ValidatedComposedPackage(receipt,t.context.context_id,'partial',_STATES,data['payloads/equity.json'],len(names),sum(map(len,data.values())))


setattr(validate_research_context_composed_payload, '__signature__',
        _PublicSignature.from_callable(validate_research_context_composed_payload))
