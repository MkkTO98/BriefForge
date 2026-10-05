"""Exact dependency-defined unittest gate; no installation or historical execution."""
from __future__ import annotations
import argparse
import ast
from collections import Counter
import contextlib
import ctypes
import hashlib
import importlib
import importlib.metadata
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import math
import unittest

ROOT=Path(__file__).resolve().parents[1]
COUNTS={'baseline':796,'existing_portable':719,'historical':77,'new':27,'portable':746,'software':726,'local':20,'total':823}
DEFINITION_HASH='2856904ac3ace77356d524433d421c47a143e17e95215d9898e25fbb94d37887'
PREFLIGHT='20261004T023419240505529Z-briefforge-portable-preflight'
RESTORATION='20261002T090856859421Z-briefforge-task020-finding-restoration-verified'
REAL='SEC-Review/20260929T120902008429Z-research-context-v1-composed-payload-real-data-verification'
STATUSES=('PASS','FAIL','ERROR','SKIP','XFAIL','XPASS','BLOCKED','NOT_RUN')
AST_EXCEPTION=('test_task070_candidate_authoring_recovery.Task070RecoveryTests.test_extra_state_after_terminal_and_lock_metadata_rejected','e07a178276be04a5fb3adce64b0d50381127e6bcb6a92e0835140475d2d33aff','0d965cc5a488720fd9be63491c88aee64577e6738338a041dc6ec3d3a47a36a3')
LEGACY_LITERAL_TMP_METHOD='test_semantic_artifact_conformance.SemanticArtifactConformanceTests.test_assessor_authority_must_be_carried_by_independently_verified_release'

CORRECTION_AST={'test_task076_contract_inventory_summary.Task076ContractInventorySummaryTests.test_regular_summary_is_admitted_without_becoming_governed_authority': ('d3c0b2afa6399ba74ce5a04d3cdeb1e57dc4c8a960f37a0cf55afb43fe75db64', 'b71b0a5f59af029b70dcfecf1b403254e1c775e00447a9e19a079760a0c24185'), 'test_task076_contract_inventory_summary.Task076ContractInventorySummaryTests.test_summary_symlink_is_rejected_even_when_target_is_regular': ('e815f45489bf5ac93192fa3fe6c1c17531a174c6e84ae0b588a46d1c1ed9d233', 'd9e0313edc9c0b75f4e9c1074ec476b3ef37fb612f1298a6149fa12e4eb4e6c7')}

# Exact publication correction, not an extensible exception registry.
SYNTHETIC_AST={'test_research_context_composed_payload_adapter.AdapterContractTests.test_numerator_denominator_provenance_and_limitations': ('6e9d99daa6ecf9d70fdf4632d5c91bfcdf8c4e9250c919fbc67eab4cac73f67d', '92a496a04f18db43f3b38c71e92a7626fbaf42450ffd5f1de1a40e7408e2e568'), 'test_research_context_composed_payload_adapter.AdapterContractTests.test_raw_fraction_exact_and_percent_display_only': ('7fe7461162c4cc66d3afed21ab05f3b516fd6bf3b1c584a836018ea3774d4047', 'ae858e6bf71f868c8e717daebeb9ed00ae242f5306f5a519218b547f7d80e86b'), 'test_research_context_composed_payload_html.ComposedHtmlTests.test_exact_semantic_parity_all_statements_references_obligations': ('d1aae49570339b510ae34227cbfbbe5758f711dab42df74fd7c7054b321a8a8f', 'd5a3772bddaa7f5a3fb3b6135e778e79e18f4e3271956ca0b9774028a7fb6859'), 'test_research_context_composed_payload_html.ComposedHtmlTests.test_partial_states_provenance_non_pit_and_rights_visible': ('53d939f9b3cca6d615d6d220d5d0980dcd7a1eadb887f7781787622fc6883157', 'c7a337759ebf758fe14ecae80377f089695d08cb89bcf23cd56478cd3e873f19')}
SYNTHETIC_MODULE_PINS={'tests/test_research_context_composed_payload_validation.py': {'bytes': 32519, 'mode': 33188, 'sha256': 'fcaf422b4ea2015586206abf83dfcd69df488790b0a21396ea0e57e68af473d1', 'type': 'file'}, 'tests/test_research_context_composed_payload_adapter.py': {'bytes': 6329, 'mode': 33188, 'sha256': 'bfd55e0340f50f83f84aecac10065dde8b06556a6cba08acbf9945fb1688124c', 'type': 'file'}, 'tests/test_research_context_composed_payload_html.py': {'bytes': 14609, 'mode': 33188, 'sha256': '7b79b77f9a02a7214d24128d94866e0dd08036198ebb19094899ec0556ea1f5d', 'type': 'file'}}

class ProfileError(ValueError): pass

def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')
def sha(raw): return hashlib.sha256(raw).hexdigest()
def digest(path): return sha(Path(path).read_bytes())
def save(root,name,value):
    path=Path(root)/name; path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:f.write(json.dumps(value,sort_keys=True,indent=2)+'\n')
def read_profile(): return json.loads((ROOT/'tests/portable_profiles.json').read_text())
def require(condition,detail):
    if not condition: raise ProfileError(detail)

def identity(path):
    p=Path(path); s=p.lstat()
    if stat.S_ISREG(s.st_mode):return dict(type='file',mode=s.st_mode,bytes=s.st_size,sha256=digest(p))
    if stat.S_ISDIR(s.st_mode):return dict(type='directory',mode=s.st_mode)
    if stat.S_ISLNK(s.st_mode):return dict(type='symlink',mode=s.st_mode,target=os.readlink(p))
    return dict(type='other',mode=s.st_mode)

def snapshot(root,omit_git=False):
    root=Path(root); result={}
    for current,dirs,files in os.walk(root,followlinks=False):
        if omit_git and Path(current)==root: dirs[:]=[n for n in dirs if n!='.git']
        for name in sorted(dirs+files):
            p=Path(current)/name;result[p.relative_to(root).as_posix()]=identity(p)
    return dict(sorted(result.items()))

def require_preserved(before,after):require(before==after,'protected-byte/membership/type/mode drift')

@contextlib.contextmanager
def legacy_tmp_runtime(key):
    """One unchanged baseline proof enumerates literal /tmp; never alter its assertions."""
    policy={'exception_applied':key==LEGACY_LITERAL_TMP_METHOD}
    if not policy['exception_applied']:
        yield policy;return
    old_cache=tempfile.tempdir;old_env=os.environ.get('TMPDIR')
    def ledgers():
        return {str(p):{'identity':identity(p),'entries':snapshot(p) if p.is_dir() and not p.is_symlink() else None} for p in Path('/tmp').iterdir() if p.name.startswith('briefforge-task052-ledger-')}
    before=ledgers();policy.update(tmpdir='/tmp',ledger_before=before)
    try:
        os.environ['TMPDIR']='/tmp';tempfile.tempdir='/tmp'
        yield policy
    finally:
        tempfile.tempdir=old_cache
        if old_env is None:os.environ.pop('TMPDIR',None)
        else:os.environ['TMPDIR']=old_env
        after=ledgers();policy.update(ledger_after=after,preserved=before==after)
        require_preserved(before,after)

def finalize_temporary_state(stage):
    """Archive own scratch bytes/link metadata, then dispose without following links."""
    stage=Path(stage);tmp=stage/'tmp'
    require(stage.is_absolute() and stage.is_dir() and not stage.is_symlink(),'nonregular staging root')
    require(not stage.is_relative_to(ROOT) and all(not p.is_symlink() and not (p/'.git').exists() for p in [stage,*stage.parents]),'unsafe staging root')
    require(tmp.is_dir() and not tmp.is_symlink(),'nonregular owned scratch root')
    entries=snapshot(tmp);require(all(v['type'] in ('file','directory','symlink') for v in entries.values()),'unsupported temporary entry')
    for n,v in entries.items():
        if v['type']=='file':
            raw=(tmp/n).read_bytes();require(sha(raw)==v['sha256'],'temporary byte drift')
            out=stage/'temporary-state-files'/n;out.parent.mkdir(parents=True,exist_ok=True)
            with out.open('xb') as f:f.write(raw)
    save(stage,'temporary-state.json',{'root':str(tmp),'entries':entries,'disposal':'task-owned tree only; links not followed'})
    require_preserved(entries,snapshot(tmp));shutil.rmtree(tmp)
    require(not os.path.lexists(tmp),'temporary disposal incomplete')

def definition_hash(rows):return sha(canonical(sorted((r['original'],r['runtime'],r['profile'],r['layer']) for r in rows)))
def selection_hash(rows):return sha(canonical(rows))
def select(m,profile,layer):
    require(profile in ('portable','historical'),'unknown profile')
    require(layer in ('all','software','local'),'unknown layer')
    return sorted([r for r in m['rows'] if r['profile']==profile and (layer=='all' or r['layer']==layer)],key=lambda r:r['runtime'])

def reconcile(m):
    require(m['counts']==COUNTS,'declared counts differ')
    exceptions=m.get('authorized_ast_exceptions',{})
    require(set(exceptions)=={AST_EXCEPTION[0]},'authorized AST exception set differs')
    exception=exceptions[AST_EXCEPTION[0]]
    require(exception['original_ast_sha256']==AST_EXCEPTION[1] and exception['revised_ast_sha256']==AST_EXCEPTION[2] and exception['original']==AST_EXCEPTION[0] and exception['runtime']==m['moves'][AST_EXCEPTION[0]],'authorized AST exception identity differs')
    corrections=m.get('correction_ast_exceptions',{})
    require(set(corrections)==set(CORRECTION_AST),'correction AST set differs')
    for key,pins in CORRECTION_AST.items():
        entry=corrections[key]
        require(entry['original']==entry['runtime']==key and (entry['original_ast_sha256'],entry['revised_ast_sha256'])==pins,'correction AST authority differs')
    require(m.get('synthetic_correction_module_pins')==SYNTHETIC_MODULE_PINS,'synthetic module correction authority differs')
    synthetic=m.get('synthetic_correction_ast',{})
    require(set(synthetic)==set(SYNTHETIC_AST),'synthetic AST correction set differs')
    for key,pins in SYNTHETIC_AST.items():
        entry=synthetic[key]
        require(entry['original']==entry['runtime']==key and (entry['original_ast_sha256'],entry['revised_ast_sha256'])==pins,'synthetic AST correction authority differs')
    for name,pin in SYNTHETIC_MODULE_PINS.items():
        require(m['source_pins'][name]==pin and identity(ROOT/name)==pin,'synthetic module correction bytes differ')
    rows=m['rows']; require(len(rows)==823,'inventory length differs')
    require(len({r['original'] for r in rows})==823 and len({r['runtime'] for r in rows})==823,'duplicate identity')
    require(definition_hash(rows)==DEFINITION_HASH,'fixed partition/moves differ')
    require(m['moves']=={r['original']:r['runtime'] for r in rows if r['original']!=r['runtime']} and len(m['moves'])==40,'move bijection differs')
    runtime_ast={}; modules={r['runtime'].split('.')[0] for r in rows}
    require({p.stem for p in (ROOT/'tests').glob('test*.py')}==modules,'unknown/unclassified module')
    for mod in sorted(modules):
        path=ROOT/'tests'/(mod+'.py');require(path.is_file() and not path.is_symlink(),'missing/linked test module '+mod)
        tree=ast.parse(path.read_bytes())
        for cls in tree.body:
            if isinstance(cls,ast.ClassDef) and any(isinstance(b,ast.Attribute) and b.attr=='TestCase' for b in cls.bases):
                for f in cls.body:
                    if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)) and f.name.startswith('test'):
                        runtime_ast[mod+'.'+cls.name+'.'+f.name]=ast.dump(f,include_attributes=False)
        if mod in m['baseline_module_sha256'] and 'tests/'+mod+'.py' not in m['allowlist']:
            if 'tests/'+mod+'.py' in SYNTHETIC_MODULE_PINS:
                require(identity(path)==SYNTHETIC_MODULE_PINS['tests/'+mod+'.py'],'corrected module drift '+mod)
            else:require(digest(path)==m['baseline_module_sha256'][mod],'baseline module drift '+mod)
    require(set(runtime_ast)=={r['runtime'] for r in rows},'unknown/removed/duplicate method inventory')
    for r in rows:
        if not r['new']:
            original=m['baseline_method_ast'][r['original']]
            revised=runtime_ast[r['runtime']]
            if r['original'] in SYNTHETIC_AST:
                pins=SYNTHETIC_AST[r['original']]
                require(original==dict(historical_ast_sha256=pins[0],representation='digest_only_historical_reference'),'historical digest reference differs')
                require(sha(revised.encode())==pins[1],'synthetic revised method AST drift')
            elif r['original']==AST_EXCEPTION[0]:
                require(sha(original.encode())==AST_EXCEPTION[1] and sha(revised.encode())==AST_EXCEPTION[2],'authorized method AST drift')
            elif r['original'] in CORRECTION_AST:
                require((sha(original.encode()),sha(revised.encode()))==CORRECTION_AST[r['original']],'correction method AST drift')
            else:require(revised==original,'method AST drift '+r['original'])
        if r['profile']=='historical':require(bool(r.get('prerequisites')),'missing historical prerequisite record')
    actual=dict(baseline=sum(not r['new'] for r in rows),existing_portable=sum(not r['new'] and r['profile']=='portable' for r in rows),historical=sum(r['profile']=='historical' for r in rows),new=sum(r['new'] for r in rows),portable=sum(r['profile']=='portable' for r in rows),software=sum(r['layer']=='software' for r in rows),local=sum(r['layer']=='local' for r in rows),total=len(rows))
    require(actual==COUNTS,'observed inventory counts differ')
    return actual

def output_destination(path):
    p=Path(path)
    require(p.is_absolute() and '..' not in p.parts,'absolute non-traversing output required')
    require(not os.path.lexists(p),'output already exists')
    for parent in [p.parent,*p.parent.parents]:
        require(not parent.is_symlink(),'output symlink ancestor')
        require(not (parent/'.git').exists(),'output inside repository')
        require(parent!=ROOT,'output inside BriefForge')
    require(p.parent.is_dir(),'output parent missing')
    return p

def publish(stage,destination):
    destination=output_destination(destination);stage=Path(stage)
    require(stage.parent==destination.parent and stage.is_dir() and not stage.is_symlink(),'same-parent regular staging required')
    libc=ctypes.CDLL(None,use_errno=True)
    require(hasattr(libc,'renameat2'),'atomic no-replace unavailable')
    rc=libc.renameat2(-100,os.fsencode(stage),-100,os.fsencode(destination),1)
    if rc:raise ProfileError('atomic no-replace publication refused: '+os.strerror(ctypes.get_errno()))

def ledger_rows(path):
    raw=Path(path).read_text('ascii');rows={}
    for line in raw.splitlines():
        match=re.fullmatch(r'([0-9a-f]{64})  (.+)',line)
        require(match is not None,'malformed checksum ledger')
        h,n=match.groups();require(n not in rows and not Path(n).is_absolute() and '..' not in Path(n).parts,'unsafe/duplicate ledger member')
        rows[n]=h
    require(bool(rows),'empty ledger');return rows

def verify_hash_ledger(root):
    root=Path(root)
    for n,h in ledger_rows(root/'MANIFEST.sha256').items():
        p=root/n;require(p.is_file() and not p.is_symlink(),'nonregular ledger member')
        require(all(not (root/Path(*Path(n).parts[:i])).is_symlink() for i in range(1,len(Path(n).parts))),'linked ledger ancestor')
        require(digest(p)==h,'ledger hash mismatch '+n)

def seal(root):
    root=Path(root);entries=snapshot(root)
    require(all(v['type'] in ('file','directory') for v in entries.values()),'nonregular output')
    names=sorted(n for n,v in entries.items() if v['type']=='file')
    require('MANIFEST.txt' not in names and 'MANIFEST.sha256' not in names,'already sealed')
    (root/'MANIFEST.txt').write_text(''.join(f'{n}\t{(root/n).stat().st_size}\t{digest(root/n)}\n' for n in names),encoding='ascii')
    (root/'MANIFEST.sha256').write_text(''.join(f'{digest(root/n)}  {n}\n' for n in sorted([*names,'MANIFEST.txt'])),encoding='ascii')

def verify_ledgers(root):
    root=Path(root);verify_hash_ledger(root)
    snap=snapshot(root);require(all(v['type'] in ('file','directory') for v in snap.values()),'linked/nonregular evidence')
    files={n for n,v in snap.items() if v['type']=='file'}; rows=ledger_rows(root/'MANIFEST.sha256')
    require(set(rows)==files-{'MANIFEST.sha256'},'checksum coverage differs')
    members={}
    for line in (root/'MANIFEST.txt').read_text('ascii').splitlines():
        parts=line.split('\t'); require(len(parts)==3,'manifest format')
        n,s,h=parts; require(n not in members,'duplicate manifest member')
        require(n in rows and str((root/n).stat().st_size)==s and rows[n]==h,'manifest byte/hash mismatch')
        members[n]=h
    require(set(members)==files-{'MANIFEST.sha256','MANIFEST.txt'},'closed manifest differs')
    implied={str(parent) for n in files for parent in Path(n).parents if str(parent)!='.'}
    require({n for n,v in snap.items() if v['type']=='directory'}==implied,'extra empty directory')
    return True

# Diagnostic vocabulary is independent of exception messages and caller attributes.
# Source frames are deliberately omitted: fixture filenames/source may be sensitive.
EXCEPTION_CATEGORIES={t:t.__name__ for t in (AssertionError,RuntimeError,ValueError,TypeError,KeyError,IndexError,ImportError,ModuleNotFoundError,OSError,FileNotFoundError,PermissionError,TimeoutError,KeyboardInterrupt,SystemExit,unittest.SkipTest,ProfileError)}
REGISTERED_ERROR_CODES={
    ('briefforge.research_context_composed_payload_html','ComposedHtmlPolicyError'):frozenset(('ADAPTER_VERSION_UNSUPPORTED','CANDIDATE_REJECTED','PROMOTION_REJECTED','HTML_ENCODING_ERROR','HTML_SIZE_LIMIT')),
    ('briefforge.research_context_composed_payload_validation','ComposedPackageError'):frozenset(('AVAILABILITY_MISMATCH','COMPANION_ID_MISMATCH','COMPANION_TRUST_MISMATCH','COMPONENT_ID_MISMATCH','COMPONENT_ORDER','COMPONENT_SET','CONTEXT_ID_MISMATCH','CONTEXT_TRUST_MISMATCH','EMBEDDED_CONTEXT_INVALID','ENTITY_MISMATCH','FILE_TOO_LARGE','FINDING_ID_MISMATCH','HASH_MISMATCH','INPUT_PATH_INVALID','JSON_DUPLICATE_KEY','JSON_FLOAT_FORBIDDEN','JSON_INVALID','LOCAL_REF_INVALID','MANIFEST_COVERAGE','MANIFEST_FORMAT','MEASUREMENT_MISMATCH','NONCANONICAL_JSON','PACKAGE_CHANGED_DURING_VALIDATION','PACKAGE_STATUS_MISMATCH','PERIOD_MISMATCH','QUALITY_MISMATCH','RECORD_ID_MISMATCH','RESOURCE_CHANGED_DURING_VALIDATION','RESOURCE_HASH_MISMATCH','SCHEMA_INVALID','SIZE_MISMATCH','SOURCE_COMPONENT_MISMATCH','SOURCE_PACKAGE_MISMATCH','SOURCE_RECORD_MISMATCH','SOURCE_SIZE_MISMATCH','STATE_MISMATCH','STATE_PAYLOAD_MISMATCH','STATE_REASON_MISMATCH','SYMLINK_FORBIDDEN','TRUST_INPUT_INVALID','UNAUTHORIZED_JOIN','UNIT_MISMATCH','UNSAFE_PATH','UNSUPPORTED_COMPOSER','UNSUPPORTED_CONTRACT','UNSUPPORTED_PROFILE','UNSUPPORTED_SCHEMA_VERSION')),
}

def exception_diagnostic(err):
    typ,exc,_=err
    category=EXCEPTION_CATEGORIES.get(typ,'Exception' if isinstance(exc,Exception) else 'BaseException')
    result=dict(category=category,message_policy='OMITTED',frames_policy='OMITTED')
    for (module,name),codes in REGISTERED_ERROR_CODES.items():
        admitted=sys.modules.get(module)
        if admitted is not None and typ is vars(admitted).get(name):
            # Reviewed code field only; no other attributes, properties or str/repr.
            try:code=object.__getattribute__(exc,'code')
            except (AttributeError,TypeError):break
            if type(code) is str and code in codes:result['error_code']=code
            break
    return result

def safe_diagnostic(value):
    if type(value) is not dict:return None
    out={}
    categories=set(EXCEPTION_CATEGORIES.values())|{'Exception','BaseException'}
    if type(value.get('category')) is str and value['category'] in categories:out['category']=value['category']
    if not out:return None
    out.update(message_policy='OMITTED',frames_policy='OMITTED')
    code=value.get('error_code')
    if type(code) is str and any(code in codes for codes in REGISTERED_ERROR_CODES.values()):out['error_code']=code
    return out

@contextlib.contextmanager
def suppressed_streams():
    """Discard Python and inherited fd 1/2 output before it reaches any spool."""
    with open(os.devnull,'w') as sink:
        saved=[os.dup(fd) for fd in (1,2)]
        try:
            for fd in (1,2):os.dup2(sink.fileno(),fd)
            with contextlib.redirect_stdout(sink),contextlib.redirect_stderr(sink):yield
        finally:
            # Discard buffered output while descriptors still point to /dev/null.
            for stream in (sys.stdout,sys.stderr):
                try:stream.flush()
                except Exception:pass
            ctypes.CDLL(None).fflush(None)
            for fd,old in zip((1,2),saved):os.dup2(old,fd);os.close(old)

SAFE_DETAILS=frozenset(('diagnostic text omitted','local prerequisites unavailable','runtime prerequisites unavailable','execution interrupted: TIMEOUT','execution interrupted: INTERRUPTED','execution interrupted: WORKER_ERROR','execution interrupted: LAUNCH_ERROR','method interrupted'))

def safe_method(entry):
    out={k:entry[k] for k in ('original','raw_id','status','started','completed','layer')}
    require(out['status'] in STATUSES and type(out['started']) is bool and type(out['completed']) is bool,'invalid diagnostic outcome')
    if 'detail' in entry:out['detail']=entry['detail'] if type(entry['detail']) is str and entry['detail'] in SAFE_DETAILS else 'diagnostic text omitted'
    diagnostic=safe_diagnostic(entry.get('diagnostic'))
    if diagnostic:out['diagnostic']=diagnostic
    if out['status']=='SKIP':out['reason_policy']='OMITTED'
    if entry.get('interrupted') is True:out['interrupted']=True
    duration=entry.get('duration_seconds')
    if type(duration) is float and math.isfinite(duration) and duration>=0:out['duration_seconds']=duration
    # This separate protected-state receipt is constructed from reviewed paths,
    # not exception diagnostics. It is retained for the preceding tmp correction.
    if 'temporary_runtime_policy' in entry:out['temporary_runtime_policy']=entry['temporary_runtime_policy']
    return out

def safe_subtest(value):
    method=value['method'];ordinal=value['ordinal']
    require(type(ordinal) is int and ordinal>0 and value['status'] in ('PASS','FAIL','ERROR','SKIP'),'invalid subtest diagnostic')
    out=dict(method=method,ordinal=ordinal,identity=method+'.subtest-'+str(ordinal),status=value['status'])
    diagnostic=safe_diagnostic(value.get('diagnostic'))
    if diagnostic:out['diagnostic']=diagnostic
    if value['status']=='SKIP':out['reason_policy']='OMITTED'
    return out

def safe_error_entry(value):
    out={k:value[k] for k in ('identity','affected') if k in value}
    diagnostic=safe_diagnostic(value.get('diagnostic'))
    if diagnostic:out['diagnostic']=diagnostic
    return out

def initial_methods(rows,module_prefix='tests.',blocked=None):
    blocked=blocked or {}
    return {r['runtime']:dict(original=r['original'],raw_id=module_prefix+r['runtime'],status='BLOCKED' if r['runtime'] in blocked else 'NOT_RUN',started=False,completed=False,layer=r['layer'],**({'detail':blocked[r['runtime']] if type(blocked[r['runtime']]) is str and blocked[r['runtime']] in SAFE_DETAILS else 'diagnostic text omitted'} if r['runtime'] in blocked else {})) for r in sorted(rows,key=lambda r:r['runtime'])}

class ProgressJournal:
    """Append-only, fsynced events; no terminal worker result inferred from silence."""
    def __init__(self,path,rows,methods):
        self.path=Path(path) if path is not None else None;self.sequence=0
        self.identities={k:{n:v[n] for n in ('original','raw_id','layer')} for k,v in methods.items()}
        if self.path is not None:
            with self.path.open('xb'):pass
            self.emit('initial',dict(selection_sha256=selection_hash(rows),methods=methods))
    def emit(self,kind,value):
        if kind in ('initial','final'):
            methods=value['methods']
            require(set(methods)==set(self.identities),'diagnostic method coverage')
            for k,v in methods.items():require(all(v[n]==pin for n,pin in self.identities[k].items()),'diagnostic identity drift')
            if kind=='initial':value=dict(selection_sha256=value['selection_sha256'],methods={k:safe_method(v) for k,v in methods.items()})
            else:value=report_for(methods,value['loader_errors'],value['setup_errors'],value['subtests'],execution_errors=value['execution_errors'])
        elif kind=='method':
            k=value['key'];require(k in self.identities,'unknown diagnostic method')
            require(all(value['entry'][n]==pin for n,pin in self.identities[k].items()),'diagnostic identity drift')
            value=dict(key=k,entry=safe_method(value['entry']))
        elif kind=='subtest':
            require(value['method'] in self.identities,'unknown diagnostic subtest');value=safe_subtest(value)
        elif kind in ('setup','loader'):
            value=safe_error_entry(value)
            require(type(value.get('affected')) is list and all(k in self.identities for k in value['affected']),'unknown diagnostic affected method')
            allowed={'setup outcome (unresolved)',*self.identities}
            for entry in self.identities.values():
                cls=entry['raw_id'].rsplit('.',1)[0];mod=cls.rsplit('.',1)[0]
                allowed.update(h+' ('+c+')' for h,c in [('setUpClass',cls),('tearDownClass',cls),('setUpModule',mod),('tearDownModule',mod)])
            require(type(value.get('identity')) is str and value['identity'] in allowed,'unknown setup/loader diagnostic identity')
        else:raise ProfileError('unknown diagnostic event')
        if self.path is None:return
        event=dict(sequence=self.sequence,kind=kind,value=value)
        with self.path.open('ab',buffering=0) as f:
            raw=canonical(event)+b'\n'; written=0
            while written<len(raw):written+=f.write(raw[written:])
            os.fsync(f.fileno())
        self.sequence+=1

class AccountingResult(unittest.TestResult):
    """No TextTestResult formatting: even its in-memory formatting calls str/repr."""
    def __init__(self,methods,journal):
        super().__init__();self.methods=methods;self.journal=journal;self.subtests=[];self.setup_errors=[];self.tmp_contexts={};self.admitted={};self.started_at={};self.ordinals=Counter()
    def admit(self,test,key):self.admitted[id(test)]=key
    def key(self,test):return self.admitted.get(id(test))
    def progress(self,key):
        if key in self.started_at:self.methods[key]['duration_seconds']=float(max(0,time.monotonic()-self.started_at[key]))
        self.journal.emit('method',dict(key=key,entry=self.methods[key]))
    def startTest(self,test):
        super().startTest(test);k=self.key(test);require(k in self.methods,'unadmitted method started')
        self.started_at[k]=time.monotonic();self.methods[k]['started']=True;self.progress(k)
        if k==LEGACY_LITERAL_TMP_METHOD:
            context=legacy_tmp_runtime(k);self.tmp_contexts[k]=context;self.methods[k]['temporary_runtime_policy']=context.__enter__();self.progress(k)
    def stopTest(self,test):
        k=self.key(test);interrupted=sys.exc_info()[0]
        self.methods[k]['completed']=not (interrupted and not issubclass(interrupted,Exception))
        if self.methods[k]['status']=='NOT_RUN':self.methods[k]['status']='ERROR'
        if not self.methods[k]['completed']:self.methods[k].update(interrupted=True,detail='method interrupted',diagnostic=exception_diagnostic(sys.exc_info()))
        if k in self.tmp_contexts:self.tmp_contexts.pop(k).__exit__(None,None,None)
        self.progress(k);super().stopTest(test)
    def mark(self,test,status,err=None):
        k=self.key(test);diagnostic=exception_diagnostic(err) if err else None
        if k is None:
            # Only unittest's reviewed holder description is used to match exact
            # admitted class/module coordinates. Never call holder.id()/str().
            desc=vars(test).get('description') if type(test) is unittest.suite._ErrorHolder else None
            affected=[];identity='setup outcome (unresolved)'
            for key,entry in self.methods.items():
                cls=entry['raw_id'].rsplit('.',1)[0];mod=cls.rsplit('.',1)[0]
                if type(desc) is str and desc in tuple(h+' ('+c+')' for h,c in [('setUpClass',cls),('tearDownClass',cls),('setUpModule',mod),('tearDownModule',mod)]):
                    affected.append(key);identity=desc
            entry=dict(identity=identity,affected=affected)
            if diagnostic:entry['diagnostic']=diagnostic
            self.setup_errors.append(entry);self.journal.emit('setup',entry)
            for x in affected:
                if not self.methods[x]['completed']:
                    self.methods[x]['status']=status
                    if diagnostic:self.methods[x]['diagnostic']=diagnostic
                    self.progress(x)
        else:
            # ERROR outranks FAIL/SKIP; later passing subtests never launder it.
            prior=self.methods[k]['status']
            if prior not in ('ERROR','FAIL') or status=='ERROR':self.methods[k]['status']=status
            if diagnostic:self.methods[k]['diagnostic']=diagnostic
            self.progress(k)
    def addSuccess(self,test):
        if self.methods[self.key(test)]['status']=='NOT_RUN':self.mark(test,'PASS')
    def addFailure(self,test,err):self.mark(test,'FAIL',err);self.failures.append((test,None))
    def addError(self,test,err):self.mark(test,'ERROR',err);self.errors.append((test,None))
    def addSkip(self,test,reason):
        if type(test) is unittest.case._SubTest:
            parent=vars(test).get('test_case');self.subtest(parent,'SKIP');self.mark(parent,'SKIP')
        else:self.mark(test,'SKIP')
        self.skipped.append((test,None))
    def addExpectedFailure(self,test,err):self.mark(test,'XFAIL',err);self.expectedFailures.append((test,None))
    def addUnexpectedSuccess(self,test):self.mark(test,'XPASS');self.unexpectedSuccesses.append(test)
    def subtest(self,test,status,err=None):
        k=self.key(test);require(k in self.methods,'unadmitted subtest');self.ordinals[k]+=1
        entry=dict(method=k,ordinal=self.ordinals[k],status=status)
        if err:entry['diagnostic']=exception_diagnostic(err)
        entry=safe_subtest(entry);self.subtests.append(entry);self.journal.emit('subtest',entry);self.progress(k)
    def addSubTest(self,test,subtest,err):
        status='PASS' if err is None else ('FAIL' if issubclass(err[0],test.failureException) else 'ERROR')
        self.subtest(test,status,err)
        if err:
            self.mark(test,status,err)
            (self.failures if status=='FAIL' else self.errors).append((test,None))

def method_counts(methods):
    counts=Counter(x['status'] for x in methods.values())
    return dict(selected=len(methods),started=sum(x['started'] for x in methods.values()),completed=sum(x['completed'] for x in methods.values()),passed=counts['PASS'],failed=counts['FAIL'],errored=counts['ERROR'],skipped=counts['SKIP'],xfailed=counts['XFAIL'],xpassed=counts['XPASS'],blocked=counts['BLOCKED'],not_run=counts['NOT_RUN'])

def report_for(methods,loader_errors=None,setup_errors=None,subtests=None,log='',execution_errors=None):
    methods={k:safe_method(v) for k,v in methods.items()}
    loader_errors=[safe_error_entry(e) for e in (loader_errors or [])];setup_errors=[safe_error_entry(e) for e in (setup_errors or [])]
    subtests=[safe_subtest(s) for s in (subtests or [])]
    execution_errors=[safe_diagnostic(e) or (e if type(e) is str and e in SAFE_DETAILS else 'diagnostic text omitted') for e in (execution_errors or [])]
    counts=method_counts(methods)
    passed=counts['selected']==counts['started']==counts['completed']==counts['passed'] and not loader_errors and not setup_errors and not execution_errors and all(s['status']=='PASS' for s in subtests)
    failed=bool(execution_errors or loader_errors or setup_errors or any(counts[k] for k in ('failed','errored','skipped','xfailed','xpassed','not_run')))
    status='PASS' if passed else 'FAIL' if failed else 'BLOCKED'
    return dict(status=status,exit_code=0 if passed else 1 if failed else 2,counts=counts,methods=methods,loader_errors=loader_errors,setup_errors=setup_errors,subtests=subtests,unittest_log='',stream_policy='SUPPRESSED',diagnostic_policy='STRUCTURED_ALLOWLIST_V1',execution_errors=execution_errors)

def execute_selection(rows,module_prefix='tests.',progress_path=None,blocked=None):
    with suppressed_streams():
        return _execute_selection(rows,module_prefix,progress_path,blocked)


def _execute_selection(rows,module_prefix,progress_path,blocked):
    rows=sorted(rows,key=lambda r:r['runtime']);methods=initial_methods(rows,module_prefix,blocked)
    require(len(methods)==len(rows),'duplicate execution selection')
    journal=ProgressJournal(progress_path,rows,methods);loader_errors=[];suite=unittest.TestSuite()
    result=AccountingResult(methods,journal);execution_errors=[]
    try:
        for row in rows:
            key=row['runtime'];mod,cls,method=key.split('.')
            if methods[key]['status']=='BLOCKED':continue
            try:
                module=importlib.import_module(module_prefix+mod)
                if module_prefix=='tests.':require(Path(module.__file__).resolve()==ROOT/'tests'/(mod+'.py'),'installed module substitution')
                klass=getattr(module,cls);require(issubclass(klass,unittest.TestCase),'non-TestCase selector')
                require(method in klass.__dict__,'inherited/missing method')
                test=klass(method);require(unittest.TestCase.id(test)==module_prefix+key,'raw loaded identity differs')
                result.admit(test,key);suite.addTest(test)
            except Exception:
                diagnostic=exception_diagnostic(sys.exc_info());methods[key].update(status='ERROR',diagnostic=diagnostic);journal.emit('method',dict(key=key,entry=methods[key]))
                entry=dict(identity=key,affected=[key],diagnostic=diagnostic);loader_errors.append(entry);journal.emit('loader',entry)
        result.startTestRun()
        try:suite.run(result)
        finally:result.stopTestRun()
    except BaseException:
        diagnostic=exception_diagnostic(sys.exc_info());execution_errors.append(diagnostic)
        for key,entry in methods.items():
            if entry['started'] and not entry['completed']:
                entry.update(status='ERROR',interrupted=True,detail='method interrupted',diagnostic=diagnostic);journal.emit('method',dict(key=key,entry=entry))
    report=report_for(methods,loader_errors,result.setup_errors,result.subtests,execution_errors=execution_errors)
    journal.emit('final',report);return report

def read_progress(path,rows,module_prefix='tests.',blocked=None):
    methods=initial_methods(rows,module_prefix,blocked);report=report_for(methods);report['unittest_log']=''
    raw=Path(path).read_bytes() if Path(path).is_file() else b'';lines=raw.splitlines(keepends=True);events=[];partial=b''
    for line in lines:
        if not line.endswith(b'\n'):partial=line;break
        try:event=json.loads(line)
        except (ValueError,UnicodeError) as exc:raise ProfileError('malformed durable progress') from exc
        require(set(event)=={'sequence','kind','value'} and event['sequence']==len(events),'progress sequence differs')
        events.append(event);kind=event['kind'];value=event['value']
        if len(events)==1:require(kind=='initial' and value==dict(selection_sha256=selection_hash(rows),methods=methods),'progress selection/initial state differs');continue
        require(not any(e['kind']=='final' for e in events[:-1]),'progress after final result')
        if kind=='method':
            k=value['key'];require(k in methods,'unknown progress method');old=methods[k];entry=value['entry']
            require(all(entry[n]==old[n] for n in ('original','raw_id','layer')),'progress method identity drift')
            require(entry['status'] in STATUSES and type(entry['started']) is bool and type(entry['completed']) is bool,'invalid progress outcome')
            require(not old['started'] or entry['started'],'started progress regressed');require(not old['completed'] or entry==old,'completed progress changed')
            require(entry==safe_method(entry),'unsafe method diagnostic fields');methods[k]=entry
        elif kind=='subtest':
            require(value['method'] in methods and methods[value['method']]['started'] and value==safe_subtest(value),'invalid subtest progress')
            require(value['ordinal']==1+sum(s['method']==value['method'] for s in report['subtests']),'subtest ordinal drift');report['subtests'].append(value)
        elif kind=='loader':require(value==safe_error_entry(value),'unsafe loader diagnostics');report['loader_errors'].append(value)
        elif kind=='setup':require(value==safe_error_entry(value),'unsafe setup diagnostics');report['setup_errors'].append(value)
        elif kind=='final':
            require(value['methods']==methods and value['subtests']==report['subtests'] and value['loader_errors']==report['loader_errors'] and value['setup_errors']==report['setup_errors'],'final progress contradicts events')
            require(value==report_for(methods,value['loader_errors'],value['setup_errors'],value['subtests'],value['unittest_log'],value['execution_errors']),'final classification/counts contradict progress')
            report=value
        else:raise ProfileError('unknown progress event')
    # A killed worker may leave only a fragment of its initial event. Selection
    # is independently frozen by the supervisor; silence/fragments prove no starts.
    require(not raw or bool(events) or bool(partial),'progress lacks evidence')
    report['methods']=methods;report['counts']=method_counts(methods)
    return report,dict(events=len(events),partial_bytes=len(partial),sha256=sha(raw),final=bool(events and events[-1]['kind']=='final'))

def reconstruct_progress(path,rows,outcome,module_prefix='tests.',blocked=None):
    report,progress=read_progress(path,rows,module_prefix,blocked)
    if outcome!='COMPLETED':
        detail='execution interrupted: '+outcome
        for entry in report['methods'].values():
            if entry['started'] and not entry['completed']:entry.update(status='ERROR',interrupted=True,detail=detail)
        report=report_for(report['methods'],report['loader_errors'],report['setup_errors'],report['subtests'],report['unittest_log'],[*report.get('execution_errors',[]),detail])
    return report,progress

class WorkerInterruption(BaseException):
    def __init__(self,signum):self.signum=signum

def supervise_worker(cmd,cwd,env,stage,rows,timeout=1800,module_prefix='tests.',blocked=None):
    """Supervise/reap the worker process group and reconstruct durable progress."""
    import signal,time
    stage=Path(stage);proc=None;outcome='COMPLETED';supervisor_signal=None;old_handlers={};cleanup=[]
    libc=ctypes.CDLL(None,use_errno=True);previous=ctypes.c_int()
    require(libc.prctl(37,ctypes.byref(previous),0,0,0)==0 and libc.prctl(36,1,0,0,0)==0,'Linux child-subreaper unavailable')
    def interrupt(signum,frame):raise WorkerInterruption(signum)
    for sig in (signal.SIGINT,signal.SIGTERM):old_handlers[sig]=signal.signal(sig,interrupt)
    def alive():
        if proc is None:return False
        try:os.killpg(proc.pid,0);return True
        except ProcessLookupError:return False
    launch_error=None
    try:
        with (stage/'stdout.log').open('xb') as out,(stage/'stderr.log').open('xb') as err:
            try:
                proc=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:outcome='TIMEOUT'
            except WorkerInterruption as exc:outcome='INTERRUPTED';supervisor_signal=exc.signum
            except OSError:outcome='LAUNCH_ERROR';launch_error=exception_diagnostic(sys.exc_info())
            finally:
                # Prevent a second handled signal from aborting evidence/cleanup.
                for sig in old_handlers:signal.signal(sig,signal.SIG_IGN)
                if alive():
                    os.killpg(proc.pid,signal.SIGTERM);cleanup.append('SIGTERM process group')
                if proc is not None:
                    try:proc.wait(timeout=.5)
                    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);cleanup.append('SIGKILL process group');proc.wait()
                if alive():
                    os.killpg(proc.pid,signal.SIGKILL);cleanup.append('SIGKILL remaining descendants')
                until=time.monotonic()+3
                while alive() and time.monotonic()<until:
                    try:
                        while os.waitpid(-proc.pid,os.WNOHANG)[0]:pass
                    except ChildProcessError:pass
                    time.sleep(.01)
        code=None if proc is None else proc.returncode
        progress_report,meta=read_progress(stage/'progress.jsonl',rows,module_prefix,blocked)
        if outcome=='COMPLETED' and (code not in (0,1,2) or not meta['final']):outcome='WORKER_ERROR'
        report,meta=reconstruct_progress(stage/'progress.jsonl',rows,outcome,module_prefix,blocked)
        if outcome=='COMPLETED':
            require((stage/'worker-results.json').is_file(),'worker final receipt absent')
            require(json.loads((stage/'worker-results.json').read_text())==report,'worker/progress result mismatch')
            require(code==report['exit_code'],'actual worker/report exit mismatch')
        receipt=dict(worker_returncode=code,worker_exit_code=code if code is not None and code>=0 else None,worker_signal=-code if code is not None and code<0 else None,worker_reaped=proc is not None and proc.poll() is not None,worker_pid=None if proc is None else proc.pid,supervisor_outcome=outcome,supervisor_signal=supervisor_signal,runner_exit_code=report['exit_code'],process_group_alive=alive(),cleanup=cleanup,progress=meta,launch_error=launch_error,cmd=cmd,cwd=str(cwd),timeout_seconds=timeout,stream_policy='SUPPRESSED',stdout_policy='SUPPRESSED_NOT_OBSERVED',stderr_policy='SUPPRESSED_NOT_OBSERVED')
        require(not receipt['process_group_alive'],'worker process group survived cleanup')
        return report,receipt
    finally:
        for sig,handler in old_handlers.items():signal.signal(sig,handler)
        require(libc.prctl(36,previous.value,0,0,0)==0,'child-subreaper restoration failed')

def verify_execution(report,process,rows,progress_path,module_prefix='tests.',blocked=None):
    require(report['stream_policy']=='SUPPRESSED' and report['diagnostic_policy']=='STRUCTURED_ALLOWLIST_V1' and report['unittest_log']=='','diagnostic policy mismatch')
    require(process['stream_policy']=='SUPPRESSED' and process['stdout_policy']==process['stderr_policy']=='SUPPRESSED_NOT_OBSERVED','worker stream policy mismatch')
    require(method_counts(report['methods'])==report['counts'],'result accounting mismatch')
    require(set(report['methods'])=={r['runtime'] for r in rows},'result method coverage')
    expected,meta=reconstruct_progress(progress_path,rows,process['supervisor_outcome'],module_prefix,blocked)
    require(expected==report and meta==process['progress'],'progress/result/process disagreement')
    code=process['worker_returncode']
    require(process['worker_exit_code']==(code if code is not None and code>=0 else None) and process['worker_signal']==(-code if code is not None and code<0 else None),'worker exit/signal disagreement')
    require(process['runner_exit_code']==report['exit_code'] and not process['process_group_alive'],'supervisor accounting/cleanup mismatch')
    if process['supervisor_outcome']=='COMPLETED':require(code==report['exit_code'] and meta['final'] and process['worker_reaped'],'incomplete normal worker receipt')
    else:require(report['status']=='FAIL' and report['exit_code']==1,'interruption laundered')
    for row in rows:
        entry=report['methods'][row['runtime']]
        require(entry['original']==row['original'] and entry['raw_id']==module_prefix+row['runtime'] and entry['layer']==row['layer'],'identity/layer mismatch')
        require(entry['status'] in STATUSES and type(entry['started']) is bool and type(entry['completed']) is bool,'invalid terminal outcome')
        if entry['status']=='PASS':require(entry['started'] and entry['completed'],'unexecuted PASS')
        if entry['status']=='BLOCKED':require(row['runtime'] in (blocked or {}) and not entry['started'] and not entry['completed'],'executed or unexplained BLOCKED')
    return True

def admit_dependencies(requirements):
    missing=[]
    for p in requirements.get('paths',[]):
        if not Path(p).exists():missing.append('required input unavailable')
    b=requirements.get('browser')
    if b is not None and (not Path(b).is_file() or not os.access(b,os.X_OK)):missing.append('Chromium executable unavailable')
    if requirements.get('platform',sys.platform)!='linux':missing.append('unsupported Linux filesystem/procfs platform')
    for n in requirements.get('imports',[]):
        if importlib.util.find_spec(n) is None:missing.append('required Python package unavailable')
    return dict(status='BLOCKED' if missing else 'READY',exit_code=2 if missing else 0,missing=missing)

def local_preservation(m,evidence):
    """Only selected local methods admit original, independently pinned inputs."""
    evidence=Path(evidence);record_path=evidence/'Suite-Logs'/RESTORATION/'AFTER.json'
    require(digest(record_path)=='c4d01c3fc2d32ab007875fb41fc829492848cca488e3d14022f58f1ecc717717','restoration receipt drift')
    record=json.loads(record_path.read_text());external={}
    for root,expected in record['evidence'].items():
        actual=snapshot(root);require_preserved(expected,actual);external[root]=actual
    p=evidence/'Suite-Logs'/PREFLIGHT
    require(digest(p/'MANIFEST.sha256')==m['preflight_manifest_sha256'],'preflight manifest drift');verify_hash_ledger(p)
    legacy=ledger_rows(p/'MANIFEST.txt');checksums=ledger_rows(p/'MANIFEST.sha256')
    require(checksums==dict(legacy,**{'MANIFEST.txt':digest(p/'MANIFEST.txt')}),'legacy preflight cross-ledger mismatch')
    require(set(checksums)=={n for n,v in snapshot(p).items() if v['type']=='file'}-{'MANIFEST.sha256'},'legacy preflight coverage')
    require(digest(evidence/'BriefForge-Portable-Testing-Contract.md')==m['controlling_contract_sha256'],'original contract drift')
    rows=json.loads((p/'selection-definition.json').read_text())['proposed_contract_selection']
    require(definition_hash(rows)==definition_hash(m['rows']),'preflight partition differs')
    external[str(p)]=snapshot(p)
    finding=ROOT.parent/'InsightForge/artifacts/analytical/IF-A-20260619-002-eurostat-deu-fra-quarterly-direction.md'
    require(digest(finding)=='2b5ad2b60b4ede9e95c70dbb6b6015e7621db24b094677b21469342349ebd458','TASK020 finding drift')
    return dict(evidence=external,finding=identity(finding),contract=identity(evidence/'BriefForge-Portable-Testing-Contract.md'))

def git_snapshot():
    env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
    def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],env=env)
    gitdir=Path(os.fsdecode(git('rev-parse','--absolute-git-dir')).strip())
    common=Path(os.fsdecode(git('rev-parse','--path-format=absolute','--git-common-dir')).strip())
    return dict(head=git('rev-parse','HEAD').hex(),refs=git('show-ref','--head').hex(),status=git('status','--porcelain=v1','-z','--untracked-files=all').hex(),cached_diff=git('diff','--cached','--binary').hex(),administrative=snapshot(gitdir),common_administrative=snapshot(common) if common!=gitdir else None,dot_git=identity(ROOT/'.git'))

def protected_snapshot(m,evidence=None,local=None):
    # Admission is versioned source/resource identity, not prior Git/residue state.
    for name,pin in m['source_pins'].items():
        require(not Path(name).is_absolute() and '..' not in Path(name).parts,'unsafe source pin')
        require(identity(ROOT/name)==pin,'versioned source/resource drift '+name)
    current=dict(repository=snapshot(ROOT,True),git=git_snapshot())
    if evidence is not None and local is not None:current['local']=local_preservation(m,evidence)
    return current

def local_admission(m,e,rows):
    selected=[r for r in rows if r['layer']=='local']
    if not selected:return dict(status='NOT_SELECTED',inputs={},preservation=None,missing=[])
    if e is None:return dict(status='BLOCKED',inputs={},preservation=None,missing=['local evidence root not supplied'])
    required=[e/'Suite-Logs'/PREFLIGHT/'MANIFEST.sha256',e/'Suite-Logs'/RESTORATION/'AFTER.json',e/'BriefForge-Portable-Testing-Contract.md',ROOT.parent/'InsightForge/artifacts/analytical/IF-A-20260619-002-eurostat-deu-fra-quarterly-direction.md',*(e/REAL/n for n in m['local_pins'])]
    required += [e/n/'MANIFEST.sha256' for n in ['Exports/20260912T180129Z-equityforge-research-bundle-v1-source-bound','SEC-Review/20260914T034316Z-apple-microsoft-two-issuer-investor-acceptance','SEC-Review/20261001T135158Z-briefforge-composed-html-narrow-correction']]
    missing=['required local input unavailable' for p in required if not p.is_file()]
    if missing:return dict(status='BLOCKED',inputs={},preservation=None,missing=missing)
    inputs=local_receipt(m,e);preservation=local_preservation(m,e)
    return dict(status='READY',inputs=inputs,preservation=preservation,missing=[])


def local_receipt(m,e):
    preflight=e/'Suite-Logs'/PREFLIGHT
    require((preflight/'MANIFEST.sha256').is_file() and digest(preflight/'MANIFEST.sha256')==m['preflight_manifest_sha256'],'missing/stale preflight authority')
    verify_hash_ledger(preflight)
    restoration=e/'Suite-Logs'/RESTORATION
    require((restoration/'AFTER.json').is_file() and digest(restoration/'AFTER.json')=='c4d01c3fc2d32ab007875fb41fc829492848cca488e3d14022f58f1ecc717717','missing/stale restoration authority')
    verify_hash_ledger(restoration)
    a=e/REAL; receipt={}
    for rel,pin in m['local_pins'].items():
        p=a/rel; require(p.is_file() and not p.is_symlink(),'local input missing/linked '+rel)
        require(p.stat().st_size==pin['bytes'] and digest(p)==pin['sha256'],'local independent pin mismatch '+rel)
        receipt[rel]=pin
    verify_hash_ledger(a); verify_hash_ledger(a/'COMPOSED_PACKAGE')
    for p in (a/'COMPOSED_PACKAGE').rglob('MANIFEST.sha256'):verify_hash_ledger(p.parent)
    for rel in ['Exports/20260912T180129Z-equityforge-research-bundle-v1-source-bound','SEC-Review/20260914T034316Z-apple-microsoft-two-issuer-investor-acceptance']:verify_hash_ledger(e/rel)
    return receipt

def environment_admission(browser,tmp):
    info=dict(executable=sys.executable,version=sys.version,prefix=sys.prefix,base_prefix=sys.base_prefix,interpreter_sha256=digest(Path(sys.executable).resolve()),environment_policy='AMBIENT_VALUES_NOT_RECORDED',packages={})
    require(sys.version_info[:2]==(3,12),'Python 3.12 required')
    for n in ('playwright','pyee','greenlet','typing_extensions','jsonschema','attrs','referencing','rpds-py','jsonschema-specifications'):
        d=importlib.metadata.distribution(n);info['packages'][n]=dict(version=d.version,origin=str(d.locate_file('')))
    dep=admit_dependencies({'browser':browser,'imports':['jsonschema','playwright'],'paths':['/proc/self/fd']})
    require(dep['exit_code']==0,'; '.join(dep['missing']))
    version=subprocess.check_output([browser,'--version'],text=True,stderr=subprocess.DEVNULL).strip()
    match=re.fullmatch(r'(?:Chromium|Google Chrome|Chrome for Testing) ([0-9]{1,4}(?:\.[0-9]{1,8}){3})',version)
    info['browser']=dict(path=browser,sha256=digest(browser),version=match.group(1) if match else 'UNRECOGNIZED_VERSION_OMITTED')
    probe=Path(tempfile.mkdtemp(prefix='capability-',dir=tmp));fd=None
    try:
        (probe/'source').write_bytes(b'capability');os.link(probe/'source',probe/'hard');(probe/'sym').symlink_to('source')
        require((probe/'sym').read_bytes()==b'capability' and os.stat(probe/'hard').st_ino==os.stat(probe/'source').st_ino,'link support absent')
        fd=os.open(probe,os.O_RDWR|os.O_TMPFILE,0o600);os.write(fd,b'anonymous bytes')
        libc=ctypes.CDLL(None,use_errno=True)
        rc=libc.linkat(fd,b'',-100,os.fsencode(probe/'published'),0x1000)
        mode='AT_EMPTY_PATH';first_errno=ctypes.get_errno() if rc else None
        if rc:
            rc=libc.linkat(-100,os.fsencode('/proc/self/fd/'+str(fd)),-100,os.fsencode(probe/'published'),0x400)
            mode='procfd/AT_SYMLINK_FOLLOW'
        require(rc==0,'linkat anonymous file unsupported: '+os.strerror(ctypes.get_errno()))
        require(os.fstat(fd).st_ino==os.stat(probe/'published').st_ino and (probe/'published').read_bytes()==b'anonymous bytes','anonymous inode/byte mismatch')
        info['capabilities']={'symlink':True,'hardlink':True,'procfs':True,'O_TMPFILE':True,'linkat':True,'linkat_mode':mode,'AT_EMPTY_PATH_errno':first_errno}
    finally:
        if fd is not None:os.close(fd)
        # Only these explicitly task-owned temporary probe files are removed.
        for p in probe.iterdir():p.unlink()
        probe.rmdir()
    return info

def candidate_hashes(m):return {p:identity(ROOT/p) for p in sorted(set(m['allowlist'])|set(SYNTHETIC_MODULE_PINS))}

def verify_result(root):
    root=Path(root);verify_ledgers(root);m=read_profile();reconcile(m)
    sel=json.loads((root/'selection.json').read_text());rows=select(m,sel['profile'],sel['layer'])
    require(sel['rows']==rows and sel['sha256']==selection_hash(rows),'selection mismatch')
    report=json.loads((root/'results.json').read_text());process=json.loads((root/'process.json').read_text())
    local=json.loads((root/'local-inputs.json').read_text())
    require(local==local_admission(m,Path(sel['evidence_root']) if sel['evidence_root'] else None,rows),'local admission receipt differs')
    if process['supervisor_outcome']=='PREREQUISITE_BLOCKED':
        require(process['worker_returncode'] is None and process['worker_exit_code'] is None and process['worker_signal'] is None and not process['worker_reaped'],'fabricated blocked worker')
        require(report['status']=='BLOCKED' and report['counts']['blocked']==len(rows) and report['counts']['started']==report['counts']['completed']==0 and report['exit_code']==process['runner_exit_code']==2,'prerequisite block accounting differs')
        expected,meta=read_progress(root/'progress.jsonl',rows,blocked=sel['blocked'])
        require(expected==report and meta==process['progress'] and meta['final'],'blocked progress differs')
    else:verify_execution(report,process,rows,root/'progress.jsonl',blocked=sel['blocked'])
    preservation=json.loads((root/'preservation.json').read_text())
    require(preservation['equal'] and preservation['before']==preservation['after'],'protected identities changed')
    require(report['stream_policy']=='SUPPRESSED' and report['unittest_log']=='','report stream policy mismatch')
    for name in ('stdout.log','stderr.log'):
        if (root/name).exists():require((root/name).read_bytes()==b'','unsafe stored process output')
    e=Path(sel['evidence_root']) if sel['evidence_root'] else None
    # Sealed invocation Git is checked against itself, not imposed on future HEADs.
    for name,pin in m['source_pins'].items():require(identity(ROOT/name)==pin,'current versioned source/resource differs '+name)
    if local['preservation'] is not None:require(preservation['after']['local']==local['preservation'],'authenticated local preservation differs')
    require(json.loads((root/'candidate-hashes.json').read_text())==candidate_hashes(m),'candidate receipt differs')
    counts=report['counts'];full=sel['profile']=='portable' and sel['layer']=='all'
    if report['status']=='PASS':
        require(report['exit_code']==process['runner_exit_code']==0 and process['supervisor_outcome']=='COMPLETED','PASS nonzero/incomplete exit')
        require(counts['selected']==counts['started']==counts['completed']==counts['passed']==len(rows),'PASS cardinality')
        require(not any(counts[n] for n in ('failed','errored','skipped','xfailed','xpassed','blocked','not_run')),'non-PASS outcomes')
        require(not report['setup_errors'] and not report['loader_errors'] and not report['execution_errors'] and all(s['status']=='PASS' for s in report['subtests']),'error/subtest laundering')
        br=json.loads((root/'browser/measurements.json').read_text())
        require([x['viewport'] for x in br]==[[320,800],[390,844],[768,1024],[1280,800]],'browser viewport coverage')
        require(all(x['passed'] and x['overflow']<=1 and not x['external_requests'] and x['csp_enforced'] for x in br),'browser refusal/overflow evidence')
        require(all((root/x['screenshot']).is_file() for x in br),'missing viewport screenshot')
        if full:
            require(counts['selected']==746 and local['status']=='READY','full count/local admission mismatch')
            require((root/'local/render-trace.json').is_file(),'local admission trace missing')
    return dict(integrity='VERIFIED',gate_status=report['status'],portable_pass=full and report['status']=='PASS',counts=counts,subtests=dict(Counter(s['status'] for s in report['subtests'])))

def main(argv=None):
    with suppressed_streams():status,value=_main(argv)
    print(json.dumps(value,sort_keys=True,indent=2));return status

def _main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',choices=['portable','historical']);parser.add_argument('--layer',choices=['all','software','local'],default='all')
    parser.add_argument('--evidence-root',type=Path);parser.add_argument('--browser-executable');parser.add_argument('--plan-only',action='store_true');parser.add_argument('--output',type=Path);parser.add_argument('--verify-result',type=Path)
    parser.add_argument('--timeout-seconds',type=float,default=1800);parser.add_argument('--_worker',type=Path,help=argparse.SUPPRESS)
    args=parser.parse_args(argv)
    if args._worker:
        receipt=json.loads(args._worker.read_text());m=read_profile();reconcile(m)
        require(receipt['profile']=='portable','historical worker forbidden')
        rows=select(m,'portable',receipt['layer']);require(receipt['rows']==rows and receipt['sha256']==selection_hash(rows),'worker selection drift')
        for path in [ROOT,ROOT/'src',ROOT/'tests']:
            if str(path) not in sys.path:sys.path.insert(0,str(path))
        report=execute_selection(rows,progress_path=args._worker.parent/'progress.jsonl',blocked=receipt['blocked'])
        save(args._worker.parent,'worker-results.json',report);return report['exit_code'],dict(status=report['status'],stream_policy='SUPPRESSED')
    if args.verify_result:return 0,verify_result(args.verify_result)
    require(args.profile is not None,'profile required');m=read_profile();reconcile(m);rows=select(m,args.profile,args.layer)
    if args.plan_only:
        prerequisites=['Python 3.12','jsonschema','Linux procfs/O_TMPFILE/linkat','installed Playwright and explicit Chromium']
        if any(r['layer']=='local' for r in rows):prerequisites.append('authenticated local inputs')
        if args.profile=='historical':prerequisites=sorted({c for r in rows for c in r['dependencies']})
        return 0,dict(profile=args.profile,layer=args.layer,counts=COUNTS,selected=len(rows),selection_sha256=selection_hash(rows),rows=rows,tests_imported=False,executed=False,prerequisites=prerequisites)
    require(args.profile=='portable','historical execution not authorized');require(args.output is not None and args.browser_executable is not None,'output/browser required')
    require(args.timeout_seconds>0,'positive timeout required')
    destination=output_destination(args.output);e=args.evidence_root.resolve() if args.evidence_root else None
    local=local_admission(m,e,rows);before=protected_snapshot(m,e,local['preservation'])
    stage=Path(tempfile.mkdtemp(prefix='.'+destination.name+'-staging-',dir=destination.parent));tmp=stage/'tmp';tmp.mkdir()
    blocked={r['runtime']:'local prerequisites unavailable' for r in rows if r['layer']=='local' and local['status']=='BLOCKED'}
    admission_error=None
    try:environment=environment_admission(args.browser_executable,tmp)
    except Exception:
        admission_error=exception_diagnostic(sys.exc_info());environment=dict(status='BLOCKED',diagnostic=admission_error)
        blocked={r['runtime']:'runtime prerequisites unavailable' for r in rows}
    selection=dict(profile='portable',layer=args.layer,rows=rows,sha256=selection_hash(rows),declared=COUNTS,evidence_root=None if e is None else str(e),blocked=blocked)
    save(stage,'selection.json',selection);save(stage,'candidate-hashes.json',candidate_hashes(m));save(stage,'local-inputs.json',local);save(stage,'environment.json',environment)
    if admission_error or len(blocked)==len(rows):
        report=report_for(initial_methods(rows,blocked=blocked));journal=ProgressJournal(stage/'progress.jsonl',rows,report['methods']);journal.emit('final',report)
        _,meta=read_progress(stage/'progress.jsonl',rows,blocked=blocked)
        process=dict(worker_returncode=None,worker_exit_code=None,worker_signal=None,worker_reaped=False,worker_pid=None,supervisor_outcome='PREREQUISITE_BLOCKED',supervisor_signal=None,runner_exit_code=2,process_group_alive=False,cleanup=[],progress=meta,launch_error=None,cmd=None,cwd=str(ROOT),timeout_seconds=args.timeout_seconds,stream_policy='NOT_STARTED',stdout_policy='NO_WORKER',stderr_policy='NO_WORKER')
    else:
        childenv=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0',PYTHONHASHSEED='0',PYTHONPATH=str(ROOT/'src')+os.pathsep+str(ROOT),TMPDIR=str(tmp),BRIEFFORGE_TEST_BROWSER=args.browser_executable,BRIEFFORGE_TEST_RUN_ROOT=str(stage))
        childenv.pop('BRIEFFORGE_TEST_EVIDENCE_ROOT',None)
        if local['status']=='READY':childenv['BRIEFFORGE_TEST_EVIDENCE_ROOT']=str(e)
        cmd=[sys.executable,'-B',str(Path(__file__).resolve()),'--_worker',str(stage/'selection.json')]
        report,process=supervise_worker(cmd,ROOT,childenv,stage,rows,args.timeout_seconds,blocked=blocked)
        verify_execution(report,process,rows,stage/'progress.jsonl',blocked=blocked)
    save(stage,'results.json',report);status=report['exit_code']
    try:
        after=protected_snapshot(m,e,local['preservation']);require_preserved(before,after);pres=dict(equal=True,before=before,after=after)
    except Exception:status=1;pres=dict(equal=False,before=before,after=None,diagnostic=exception_diagnostic(sys.exc_info()))
    save(stage,'preservation.json',pres)
    process.update(argv=sys.argv if argv is None else argv,cwd=str(ROOT),runner_exit_code=status,authoritative=args.layer=='all');save(stage,'process.json',process)
    finalize_temporary_state(stage);seal(stage);verify_ledgers(stage);publish(stage,destination)
    return status,dict(output=str(destination),status=report['status'],exit_code=status,counts=report['counts'],subtests=dict(Counter(s['status'] for s in report['subtests'])),stream_policy=process['stream_policy'])


def cli(argv=None):
    try:return main(argv)
    except BaseException:
        diagnostic=exception_diagnostic(sys.exc_info())
        print(json.dumps(dict(status='BLOCKED',diagnostic=diagnostic),sort_keys=True),file=sys.stderr);return 2

if __name__=='__main__':sys.exit(cli())
