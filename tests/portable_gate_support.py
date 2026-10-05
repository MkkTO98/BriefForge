"""Disposable synthetic containers and explicit out-of-band test receipts.

No real acceptance receipt may be resealed through these helpers. Production
validation is always called normally; these helpers never mock its result.
"""
from dataclasses import replace
import json
from pathlib import Path


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=True,allow_nan=False,separators=(',',':')).encode('ascii')


def synthetic_fixture(directory):
    from tests.test_research_context_composed_payload_validation import fixture
    return fixture(Path(directory))


def reseal_synthetic_outer(request,files):
    """Author a new synthetic outer receipt; unchanged context/source pins persist.

    The package must be the explicitly authored one-row fixture under external
    TMPDIR, never the authenticated real package or any repository directory.
    """
    import tempfile
    from tools.run_test_profile import ROOT, require
    from tests.test_research_context_composed_payload_validation import ledgers, pin, record
    from briefforge.research_context_composed_payload_validation import CompanionPins, ManifestPins
    root=request.package_dir
    require(root.is_absolute() and root.is_relative_to(Path(tempfile.gettempdir())),'synthetic package outside task TMPDIR')
    require(not root.is_relative_to(ROOT),'synthetic resealing cannot target a repository')
    row=json.loads(files['proof/producer-component.json'])
    require(type(row) is list and len(row)==1 and request.trust.address.zero_based_row_index==0,'not the bounded synthetic fixture')
    descriptor=json.loads(files['COMPOSED_PAYLOAD.json'])
    payload=json.loads(files['payloads/equity.json'])
    payload['record_id']=record(payload,'record_id','rcpr1-')
    files['payloads/equity.json']=canonical(payload)+b'\n'
    descriptor['record_id']=payload['record_id']
    descriptor['components'][0]['payload'].update(bytes=len(files['payloads/equity.json']),sha256=pin(files['payloads/equity.json']).sha256)
    descriptor['companion_id']=record(descriptor,'companion_id','rcpc1-','package_build_time')
    files['COMPOSED_PAYLOAD.json']=canonical(descriptor)+b'\n'
    ledgers(files)
    receipt=CompanionPins(descriptor['companion_id'],payload['record_id'],ManifestPins(pin(files['MANIFEST.txt']),pin(files['MANIFEST.sha256'])))
    for name,raw in files.items():
        path=root/name
        require(path.is_file() and not path.is_symlink(),'synthetic member missing/linked')
        path.write_bytes(raw)
    return replace(request,expected_identity=receipt)


def bind_synthetic_witnesses(request, files):
    """Bind explicitly authored witness bytes, without repairing attacked ledgers."""
    from tests.test_research_context_composed_payload_validation import pin, record, ledgers
    from briefforge.research_context_composed_payload_validation import ManifestPins
    d=json.loads(files['COMPOSED_PAYLOAD.json']); c=json.loads(files['context/RESEARCH_CONTEXT.json']); p=json.loads(files['payloads/equity.json'])
    source=ManifestPins(pin(files['proof/bundle-manifest.txt']),pin(files['proof/bundle-manifest.sha256']))
    acceptance=ManifestPins(pin(files['proof/acceptance-manifest.txt']),pin(files['proof/acceptance-manifest.sha256']))
    d['source_binding'].update(manifest_txt_sha256=source.manifest_txt.sha256,manifest_sha256_file_sha256=source.manifest_sha256.sha256,acceptance_manifest_txt_sha256=acceptance.manifest_txt.sha256,acceptance_manifest_sha256_file_sha256=acceptance.manifest_sha256.sha256)
    e=c['components'][0];e['provenance'].update(source_package_manifest_txt_sha256=source.manifest_txt.sha256,source_package_manifest_sha256_file_sha256=source.manifest_sha256.sha256)
    e['component_id']=record(e,'component_id','rcc1-');c['context_id']=record(c,'context_id','rcv1-','context_package_build_time')
    files['context/RESEARCH_CONTEXT.json']=canonical(c)+b'\n';ledgers(files,'context/')
    context=replace(request.trust.context,context_id=c['context_id'],equity_component_id=e['component_id'],document=pin(files['context/RESEARCH_CONTEXT.json']),manifests=ManifestPins(pin(files['context/MANIFEST.txt']),pin(files['context/MANIFEST.sha256'])))
    d['context_binding'].update(context_id=c['context_id'],manifest_txt_sha256=context.manifests.manifest_txt.sha256,manifest_sha256_file_sha256=context.manifests.manifest_sha256.sha256)
    d['components'][0]['component_id']=e['component_id'];p.update(context_id=c['context_id'],component_id=e['component_id'])
    files['COMPOSED_PAYLOAD.json']=canonical(d)+b'\n';files['payloads/equity.json']=canonical(p)+b'\n'
    trust=replace(request.trust,source=replace(request.trust.source,manifests=source),acceptance=replace(request.trust.acceptance,manifests=acceptance),context=context)
    return reseal_synthetic_outer(replace(request,trust=trust),files)


def parsed_html(raw):
    from html.parser import HTMLParser
    class Document(HTMLParser):
        def __init__(self):super().__init__(convert_charrefs=True);self.elements=[];self.text=[]
        def handle_starttag(self,tag,attrs):self.elements.append((tag,dict(attrs)))
        def handle_data(self,data):self.text.append(data)
    result=Document();result.feed(raw.decode('utf-8') if isinstance(raw,bytes) else raw);return result


def assert_typed(test, expected, actual):
    test.assertIs(type(actual),type(expected))
    if type(expected) is dict:
        test.assertEqual(set(actual),set(expected))
        for key in expected:assert_typed(test,expected[key],actual[key])
    elif type(expected) is list:
        test.assertEqual(len(expected),len(actual))
        for x,y in zip(expected,actual):assert_typed(test,x,y)
    else:test.assertEqual(expected,actual)


def assert_projection(test, request, files):
    from dataclasses import asdict
    from briefforge.research_context_composed_payload_adapter import adapt_research_context_composed_payload
    from briefforge.research_context_composed_payload_html import render_research_context_composed_payload_html
    adapted=adapt_research_context_composed_payload(request)
    row=json.loads(files['proof/producer-component.json'])[request.trust.address.zero_based_row_index]
    payload=json.loads(files['payloads/equity.json']);assert_typed(test,row,json.loads(adapted.source_record_json));assert_typed(test,row,payload['source_record'])
    accepted=json.loads(files['proof/acceptance-results.json'])[request.trust.acceptance.result_key]['results'][request.trust.acceptance.result_index]
    # Reconstruct the COMPLETE accepted latest_usable projection independently from row/address/measurement.
    projection={k:row[k] for k in ('blocking_reasons','calculation_policy','derivation_status','derived_availability_basis','derived_availability_date_proxy','formula_version','period_end','period_start','ratio_unit','ratio_value','research_value_usable')}
    projection['inputs_and_provenance']={role:{k[len(role)+1:]:value for k,value in row.items() if k.startswith(role+'_')} for role in ('numerator','denominator')}
    projection['source_row_identity']=asdict(request.trust.address);projection['value_convention']=payload['measurement']['value_convention']
    assert_typed(test,accepted['latest_usable'],projection)
    html=render_research_context_composed_payload_html(request);text=' '.join(parsed_html(html.html_bytes).text)
    for k in ('ratio_value','period_start','period_end','ratio_unit','ratio_id','formula_version','source_period_class','track','derived_availability_date_proxy'):
        test.assertIn(row[k],text)
    for role in ('numerator','denominator'):
        for key in ('concept','canonical_value','unit','accession_number','filed_date','source_row_identity','source_document_sha256','selection_group_id','cell_status','metric_slot'):
            test.assertIn(row[role+'_'+key],text)
    test.assertIn('non-PIT',text);test.assertIn('display-only',text);test.assertIn(payload['rights'],text)
    test.assertIs(payload['producer_record_hash'],None);test.assertIs(payload['availability']['pit_certified'],False)
    return adapted,html,projection


def runtime_output(name,value):
    import os
    from tools.run_test_profile import save
    root=Path(os.environ['BRIEFFORGE_TEST_RUN_ROOT']);save(root,name,value)


def local_request():
    """Authenticate original external receipts before constructing public pins."""
    import os, dataclasses, typing
    from tools import run_test_profile as r
    from briefforge import research_context_composed_payload_validation as v
    e=Path(os.environ['BRIEFFORGE_TEST_EVIDENCE_ROOT']);m=r.read_profile();r.local_receipt(m,e)
    restoration=json.loads((e/'Suite-Logs'/r.RESTORATION/'AFTER.json').read_text())
    reconciliation=e/'SEC-Review/20261001T135158Z-briefforge-composed-html-narrow-correction'
    r.require_preserved(restoration['evidence'][str(reconciliation)],r.snapshot(reconciliation));r.verify_hash_ledger(reconciliation)
    a=e/r.REAL;pins=json.loads((a/'CALLER_PINS.json').read_text());rec=json.loads((reconciliation/'RECONCILIATION.json').read_text())
    def construct(cls,data):
        hints=typing.get_type_hints(cls)
        return cls(**{f.name:construct(hints[f.name],data[f.name]) if dataclasses.is_dataclass(hints[f.name]) else data[f.name] for f in dataclasses.fields(cls)})
    trust=construct(v.ConsumerTrustPins,pins);companion=construct(v.CompanionPins,rec['accepted_identity'])
    r.require(companion.companion_id=='rcpc1-a1e1b27105db8a599557350ee789ebebcb7a799acfe6d1f654292291e91dac48' and companion.record_id=='rcpr1-ac719d6558bbafb7e3b2df5fe71993a589c48d6cbcc92ada32555106cef9a19e','accepted identity differs')
    return v.ComposedPackageRequest(a/'COMPOSED_PACKAGE',trust,companion),rec


def package_bytes(root):
    from tools import run_test_profile as r
    snap=r.snapshot(root);r.require(all(v['type'] in ('file','directory') for v in snap.values()),'linked package copy')
    return {n:(Path(root)/n).read_bytes() for n,v in snap.items() if v['type']=='file'}


def copy_package(root, destination):
    files=package_bytes(root)
    for n,raw in files.items():
        p=Path(destination)/n;p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('xb') as f:f.write(raw)
    return files


from contextlib import contextmanager
@contextmanager
def browser_runtime():
    """Short disposable Unix socket paths; no executable substitution."""
    import os,tempfile
    from playwright.sync_api import sync_playwright
    previous=os.environ.get('TMPDIR')
    with tempfile.TemporaryDirectory(prefix='bf-browser-',dir='/tmp') as tmp:
        try:
            os.environ['TMPDIR']=tmp
            with sync_playwright() as pw:yield pw
        finally:
            if previous is None:os.environ.pop('TMPDIR',None)
            else:os.environ['TMPDIR']=previous


def interruption_regressions(test):
    """Real workers/supervisors; scenarios remain subcases of the frozen R3 ID."""
    import os, sys, tempfile, subprocess, shutil
    from tools import run_test_profile as r
    base = os.environ.get('BRIEFFORGE_TEST_RUN_ROOT')
    with tempfile.TemporaryDirectory(prefix='bf-interrupt-') as tmp:
        root=Path(tmp)
        for mode in ('timeout','interrupt','crash','normal'):
            phases=('before','after','active') if mode in ('timeout','interrupt') else ('active',)
            for phase in phases:
                with test.subTest(supervisor=mode,phase=phase):
                    stage=root/(mode+'-'+phase);stage.mkdir()
                    rows=[dict(original='interrupt_fixture.'+c+'.'+m,runtime='interrupt_fixture.'+c+'.'+m,layer='software',profile='portable') for c,m in [('A','test_done'),('B','test_active'),('C','test_unstarted')]]
                    (stage/'rows.json').write_text(json.dumps(rows))
                    code='import unittest,os,signal,time,subprocess\nfrom pathlib import Path\n'
                    code+="CANARY='SYNTHETIC_NON_SECRET_BF_DIAGNOSTIC_CANARY'\n"
                    child_code="import os,time;os.write(1,b'SYNTHETIC_NON_SECRET_BF_DIAGNOSTIC_CANARY');os.write(2,b'SYNTHETIC_NON_SECRET_BF_DIAGNOSTIC_CANARY');time.sleep(60)"
                    code+='def hang():\n print(CANARY);os.write(1,CANARY.encode());os.write(2,CANARY.encode())\n child=subprocess.Popen([__import__("sys").executable,"-B","-c",'+repr(child_code)+'])\n Path("descendant.pid").write_text(str(child.pid))\n Path("ready").write_text("ready")\n'
                    if mode=='interrupt':code+=' time.sleep(.1)\n os.kill(os.getppid(),signal.SIGINT)\n'
                    if mode=='crash':code+=' os._exit(7)\n'
                    if mode!='normal':code+=' time.sleep(60)\n'
                    code+='class A(unittest.TestCase):\n'
                    if phase=='before':code+=' @classmethod\n def setUpClass(cls): hang()\n'
                    if phase=='after':code+=' @classmethod\n def tearDownClass(cls): hang()\n'
                    code+=' def test_done(self):\n  with self.subTest(completed=CANARY): self.assertTrue(True)\n'
                    code+='class B(unittest.TestCase):\n def test_active(self):\n  with self.subTest(partial=CANARY): self.assertTrue(True)\n'
                    if phase=='active':code+='  hang()\n'
                    code+='class C(unittest.TestCase):\n def test_unstarted(self): pass\n'
                    (stage/'interrupt_fixture.py').write_text(code)
                    worker=stage/'worker.py'
                    worker.write_text('import sys,json\nfrom pathlib import Path\nfrom tools import run_test_profile as r\nrows=json.loads(Path("rows.json").read_text())\nreport=r.execute_selection(rows,module_prefix="",progress_path=Path("progress.jsonl"))\nr.save(Path.cwd(),"worker-results.json",report)\nsys.exit(report["exit_code"])\n')
                    supervisor=stage/'supervisor.py'
                    supervisor.write_text('import sys,json\nfrom pathlib import Path\nfrom tools import run_test_profile as r\nrows=json.loads(Path("rows.json").read_text())\nreport,process=r.supervise_worker([sys.executable,"-B","worker.py"],Path.cwd(),dict(__import__("os").environ),Path.cwd(),rows,timeout=.8,module_prefix="")\nr.save(Path.cwd(),"results.json",report)\nr.save(Path.cwd(),"process.json",process)\nr.verify_execution(report,process,rows,Path("progress.jsonl"),module_prefix="")\nr.seal(Path.cwd());r.verify_ledgers(Path.cwd())\n')
                    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(r.ROOT/'src')+os.pathsep+str(r.ROOT))
                    proc=subprocess.run([sys.executable,'-B',str(supervisor)],cwd=stage,env=env,capture_output=True,timeout=15)
                    (stage/'harness.stdout').write_bytes(proc.stdout);(stage/'harness.stderr').write_bytes(proc.stderr)
                    if base:
                        dst=Path(base)/'regressions/interruption'/stage.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(stage,dst)
                    test.assertEqual(proc.returncode,0,proc.stderr.decode())
                    report=json.loads((stage/'results.json').read_text());receipt=json.loads((stage/'process.json').read_text())
                    for name in ('results.json','process.json','progress.jsonl','stdout.log','stderr.log','harness.stdout','harness.stderr'):
                        test.assertNotIn(b'SYNTHETIC_NON_SECRET_BF_DIAGNOSTIC_CANARY',(stage/name).read_bytes(),name)
                    test.assertEqual(receipt['stream_policy'],'SUPPRESSED')
                    if mode=='normal':
                        test.assertEqual(report['counts']['passed'],3);test.assertEqual(receipt['worker_returncode'],0)
                    else:
                        test.assertEqual(report['status'],'FAIL');test.assertEqual(report['counts']['blocked'],0)
                        test.assertEqual(receipt['supervisor_outcome'],{'timeout':'TIMEOUT','interrupt':'INTERRUPTED','crash':'WORKER_ERROR'}[mode])
                        test.assertEqual(receipt['runner_exit_code'],1)
                        test.assertIsNotNone(receipt['worker_returncode']);test.assertTrue(receipt['worker_reaped'])
                        test.assertFalse(receipt['process_group_alive'])
                        child_pid=int((stage/'descendant.pid').read_text())
                        with test.assertRaises(ProcessLookupError):os.kill(child_pid,0)
                        done=report['methods'][rows[0]['runtime']];active=report['methods'][rows[1]['runtime']]
                        test.assertEqual(done['status'],'NOT_RUN' if phase=='before' else 'PASS')
                        test.assertEqual(done['completed'],phase!='before')
                        test.assertEqual(active['status'],'ERROR' if phase=='active' else 'NOT_RUN')
                        test.assertEqual(active['started'],phase=='active');test.assertFalse(active['completed'])
                        test.assertEqual(report['methods'][rows[2]['runtime']]['status'],'NOT_RUN')
                        test.assertEqual(len(report['subtests']),{'before':0,'after':1,'active':2}[phase])
                        test.assertTrue(all(s['status']=='PASS' for s in report['subtests']))
                        test.assertEqual(receipt['worker_signal'],15 if mode in ('timeout','interrupt') else None)
                        test.assertEqual(receipt['worker_exit_code'],7 if mode=='crash' else None)
                        if phase=='active':test.assertIn('execution interrupted',active['detail'])


def progress_reconstruction_regressions(test):
    import tempfile
    from tools import run_test_profile as r
    rows=[dict(original='m.T.'+n,runtime='m.T.'+n,layer='software') for n in ('done','active','later')]
    for phase in ('empty','partial-initial','partial-after-completed','partial-active'):
        with test.subTest(progress=phase),tempfile.TemporaryDirectory() as td:
            path=Path(td)/'progress.jsonl';methods=r.initial_methods(rows,'p.')
            if phase=='partial-initial':path.write_bytes(b'{"sequence":0,')
            elif phase!='empty':
                journal=r.ProgressJournal(path,rows,methods);methods['m.T.done'].update(started=True);journal.emit('method',dict(key='m.T.done',entry=methods['m.T.done']))
                sub=dict(method='m.T.done',ordinal=1,identity='m.T.done.subtest-1',status='FAIL')
                journal.emit('subtest',sub);methods['m.T.done'].update(status='FAIL',completed=True);journal.emit('method',dict(key='m.T.done',entry=methods['m.T.done']))
                if phase=='partial-active':methods['m.T.active']['started']=True;journal.emit('method',dict(key='m.T.active',entry=methods['m.T.active']))
                with path.open('ab') as f:f.write(b'{"sequence":999,')
            report,meta=r.reconstruct_progress(path,rows,'TIMEOUT','p.')
            test.assertEqual('FAIL',report['status']);test.assertEqual(0,report['counts']['blocked'])
            test.assertEqual(1 if phase=='partial-active' else 0,report['counts']['errored'])
            test.assertEqual(1 if phase=='partial-active' else 2 if phase=='partial-after-completed' else 3,report['counts']['not_run'])
            if phase in ('partial-after-completed','partial-active'):
                test.assertEqual('FAIL',report['methods']['m.T.done']['status']);test.assertTrue(report['methods']['m.T.done']['completed']);test.assertEqual([sub],report['subtests'])
            test.assertEqual(0 if phase=='empty' else len(b'{"sequence":0,') if phase=='partial-initial' else len(b'{"sequence":999,'),meta['partial_bytes'])


def diagnostic_privacy_regressions(test):
    """Synthetic non-secret fixture text is intentional; never real credentials."""
    import os, sys, tempfile, subprocess, shutil
    from unittest.mock import patch
    from tools import run_test_profile as r
    canary='SYNTHETIC_NON_SECRET_BF_DIAGNOSTIC_CANARY'
    base=os.environ.get('BRIEFFORGE_TEST_RUN_ROOT')
    fixture='''import unittest,os,sys,logging,subprocess
C='SYNTHETIC_NON_SECRET_BF_DIAGNOSTIC_CANARY'
class Hostile(Exception):
 def __str__(self): raise AssertionError(C)
 def __repr__(self): raise AssertionError(C)
class Methods(unittest.TestCase):
 def test_assertion(self): self.fail(C)
 def test_error(self): raise RuntimeError(C)
 def test_chained(self):
  try: raise ValueError(C)
  except ValueError as cause: raise RuntimeError('SYNTHETIC_NON_SECRET_BF_DIAGNOSTIC_CANARY') from cause
 def test_unknown(self):
  error=Hostile(C);error.code=C;error.secret=C;raise error
 def test_subtests(self):
  for n in [0,1]:
   with self.subTest(secret=C,n=n,hostile=Hostile(C)): self.assertEqual(n,0,C)
 def test_skip_subtest(self):
  with self.subTest(secret=C): self.skipTest(C)
 @unittest.skip(C)
 def test_skip(self): pass
 @unittest.expectedFailure
 def test_expected(self): self.fail(C)
 def test_streams(self):
  print(C);print(C,file=sys.stderr);logging.error(C)
  os.write(1,C.encode());os.write(2,C.encode())
  __import__('ctypes').CDLL(None).printf(b'SYNTHETIC_NON_SECRET_BF_DIAGNOSTIC_CANARY')
  subprocess.run([sys.executable,'-B','-c',"import os;os.write(1,b'SYNTHETIC_NON_SECRET_BF_DIAGNOSTIC_CANARY');os.write(2,b'SYNTHETIC_NON_SECRET_BF_DIAGNOSTIC_CANARY')"],check=True)
class Setup(unittest.TestCase):
 @classmethod
 def setUpClass(cls): raise RuntimeError(C)
 def test_a(self): pass
 def test_b(self): pass
'''
    with tempfile.TemporaryDirectory(prefix='bf-privacy-') as td:
        root=Path(td)
        (root/'privacy_fixture.py').write_text(fixture)
        (root/'privacy_loader.py').write_text("raise RuntimeError('"+canary+"')\n")
        names=['assertion','error','chained','unknown','subtests','skip_subtest','skip','expected','streams']
        rows=[dict(original='privacy_fixture.Methods.test_'+n,runtime='privacy_fixture.Methods.test_'+n,layer='software',profile='portable') for n in names]
        rows += [dict(original=k,runtime=k,layer='software',profile='portable') for k in ['privacy_fixture.Setup.test_a','privacy_fixture.Setup.test_b','privacy_loader.No.test_load']]
        rows=sorted(rows,key=lambda x:x['runtime'])
        (root/'rows.json').write_text(json.dumps(rows))
        (root/'worker.py').write_text('import json,sys\nfrom pathlib import Path\nfrom tools import run_test_profile as r\nrows=json.loads(Path("rows.json").read_text())\nreport=r.execute_selection(rows,module_prefix="",progress_path=Path("progress.jsonl"))\nr.save(Path.cwd(),"worker-results.json",report)\nsys.exit(report["exit_code"])\n')
        (root/'supervisor.py').write_text('import sys,os,json\nfrom pathlib import Path\nfrom tools import run_test_profile as r\nrows=json.loads(Path("rows.json").read_text())\nreport,process=r.supervise_worker([sys.executable,"-B","worker.py"],Path.cwd(),dict(os.environ),Path.cwd(),rows,timeout=15,module_prefix="")\nr.save(Path.cwd(),"results.json",report)\nr.save(Path.cwd(),"process.json",process)\nr.verify_execution(report,process,rows,Path("progress.jsonl"),module_prefix="")\n')
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(r.ROOT/'src')+os.pathsep+str(r.ROOT))
        p=subprocess.run([sys.executable,'-B','supervisor.py'],cwd=root,env=env,capture_output=True,timeout=30)
        (root/'harness.stdout').write_bytes(p.stdout);(root/'harness.stderr').write_bytes(p.stderr)
        if base:
            dst=Path(base)/'regressions/diagnostic-privacy';dst.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(root,dst)
        with test.subTest(privacy='actual-diagnostic-write-paths'):
            test.assertEqual(p.returncode,0,'synthetic supervisor must complete')
            for name in ['results.json','worker-results.json','progress.jsonl','stdout.log','stderr.log','process.json','harness.stdout','harness.stderr']:
                test.assertNotIn(canary.encode(),(root/name).read_bytes(),name)
            report=json.loads((root/'results.json').read_text());process=json.loads((root/'process.json').read_text())
            test.assertEqual(report['exit_code'],1);test.assertEqual(report['counts']['passed'],1)
            test.assertEqual(report['counts']['failed'],2);test.assertEqual(report['counts']['errored'],6)
            test.assertEqual(report['counts']['skipped'],2);test.assertEqual(report['counts']['xfailed'],1)
            test.assertEqual(report['counts']['started'],9);test.assertEqual(report['counts']['completed'],9)
            test.assertEqual(len(report['subtests']),3)
            test.assertEqual([s['ordinal'] for s in report['subtests'] if s['method'].endswith('test_subtests')],[1,2])
            test.assertEqual({s['status'] for s in report['subtests']},{'PASS','FAIL','SKIP'})
            test.assertEqual(process['worker_returncode'],1);test.assertEqual(process['stream_policy'],'SUPPRESSED')
            test.assertTrue(all(type(e.get('duration_seconds')) is float and e['duration_seconds']>=0 for e in report['methods'].values() if e['completed']))
        # Direct API must also suppress inherited fd streams, not only Popen.
        with test.subTest(privacy='direct-api'),patch.object(sys,'path',[td,*sys.path]):
            direct=r.execute_selection([x for x in rows if x['runtime'].endswith('.test_streams')],module_prefix='',progress_path=root/'direct.jsonl')
            test.assertEqual(direct['counts']['passed'],1)
            test.assertNotIn(canary,json.dumps(direct));test.assertNotIn(canary,(root/'direct.jsonl').read_text())
        with test.subTest(privacy='unknown-error-attributes'):
            class Unreviewed(RuntimeError):
                def __str__(self): raise AssertionError('must not stringify')
                def __repr__(self): raise AssertionError('must not repr')
            error=Unreviewed(canary);error.code=canary
            safe=r.exception_diagnostic((Unreviewed,error,None))
            test.assertNotIn(canary,json.dumps(safe));test.assertEqual(safe['category'],'Exception')
            test.assertNotIn('error_code',safe)
        with test.subTest(privacy='registered-code'):
            from briefforge.research_context_composed_payload_html import ComposedHtmlPolicyError
            error=ComposedHtmlPolicyError('HTML_SIZE_LIMIT')
            test.assertEqual(r.exception_diagnostic((type(error),error,None))['error_code'],'HTML_SIZE_LIMIT')
            bad=ComposedHtmlPolicyError(canary)
            test.assertNotIn('error_code',r.exception_diagnostic((type(bad),bad,None)))
        for mode in ('fatal-worker','fatal-supervisor','launch-error'):
            with test.subTest(privacy=mode):
                stage=root/mode;stage.mkdir()
                fatal_worker="import os;os.write(1,b'"+canary+"');os.write(2,b'"+canary+"');raise RuntimeError('"+canary+"')\n"
                (stage/'fatal.py').write_text(fatal_worker)
                if mode=='fatal-supervisor':
                    program='import sys,os\nfrom tools import run_test_profile as r\nfrom unittest.mock import patch\ndef bomb():\n print("'+canary+'");os.write(2,b"'+canary+'");raise RuntimeError("'+canary+'")\nwith patch.object(r,"read_profile",side_effect=bomb):\n sys.exit(r.cli(["--profile","portable","--plan-only"]))\n'
                else:
                    program='import os,sys,json\nfrom pathlib import Path\nfrom tools import run_test_profile as r\nrows='+repr(rows[:1])+'\ncmd=[sys.executable,"-B","fatal.py"]\n'
                    if mode=='launch-error':program+='cmd=["./missing-executable"]\n'
                    program+='report,process=r.supervise_worker(cmd,Path.cwd(),dict(os.environ),Path.cwd(),rows,timeout=5,module_prefix="")\nr.save(Path.cwd(),"results.json",report);r.save(Path.cwd(),"process.json",process)\nr.verify_execution(report,process,rows,Path("progress.jsonl"),module_prefix="")\n'
                (stage/'harness.py').write_text(program)
                proc=subprocess.run([sys.executable,'-B','harness.py'],cwd=stage,env=env,capture_output=True,timeout=15)
                (stage/'harness.stdout').write_bytes(proc.stdout);(stage/'harness.stderr').write_bytes(proc.stderr)
                if base:
                    dst=Path(base)/'regressions/diagnostic-fatal'/mode;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(stage,dst)
                test.assertEqual(proc.returncode,2 if mode=='fatal-supervisor' else 0)
                for name in ('harness.stdout','harness.stderr','results.json','process.json','stdout.log','stderr.log'):
                    if (stage/name).exists():test.assertNotIn(canary.encode(),(stage/name).read_bytes(),name)
                if mode=='fatal-supervisor':
                    test.assertEqual(json.loads(proc.stderr)['diagnostic']['category'],'RuntimeError')
                else:
                    receipt=json.loads((stage/'process.json').read_text());report=json.loads((stage/'results.json').read_text())
                    test.assertEqual(report['status'],'FAIL');test.assertEqual(report['counts']['started'],0)
                    test.assertEqual(report['counts']['not_run'],1)
                    test.assertEqual(receipt['supervisor_outcome'],'LAUNCH_ERROR' if mode=='launch-error' else 'WORKER_ERROR')
                    test.assertEqual(receipt['worker_returncode'],None if mode=='launch-error' else 1)


def git_preservation_regressions(test):
    import tempfile,subprocess,os
    from unittest.mock import patch
    from tools import run_test_profile as r
    with tempfile.TemporaryDirectory(prefix='bf-git-fixture-') as tmp:
        root=Path(tmp)/'checkout';root.mkdir()
        env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
        def git(*args):
            return subprocess.check_output(['git','-C',str(root),'-c','core.hooksPath=/dev/null','-c','commit.gpgsign=false','-c','user.name=Portable Fixture','-c','user.email=fixture@example.invalid',*args],env=env,stderr=subprocess.STDOUT)
        git('init','-b','main');(root/'source').write_text('versioned fixture\n');git('add','source');git('commit','-m','fixture: portable preservation baseline')
        m={'allowlist':[],'protected_repository':r.snapshot(root,True),'source_pins':{'source':r.identity(root/'source')},'head':'obsolete head','protected_git':{'obsolete':'administrative inventory'}}
        with patch.object(r,'ROOT',root):
            before=r.protected_snapshot(m,None)
            r.require_preserved(before,r.protected_snapshot(m,None))
            git('commit','--allow-empty','-m','fixture: new portable invocation HEAD')
            with test.subTest(git='new-clean-commit'):
                fresh=r.protected_snapshot(m,None)
                test.assertNotEqual(before['git'],fresh['git'])
                r.require_preserved(fresh,r.protected_snapshot(m,None))
            git('config','fixture.changed','true')
            with test.subTest(git='mid-invocation-drift'),test.assertRaises(r.ProfileError):
                r.require_preserved(fresh,r.protected_snapshot(m,None))
            (root/'source').write_text('source drift\n')
            with test.subTest(source='versioned-pin-drift'),test.assertRaises(r.ProfileError):r.protected_snapshot(m,None)
