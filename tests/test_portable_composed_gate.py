"""Portable composed-chain contract obligations; never substitute accepted authority."""
import dataclasses
import importlib
import json
from pathlib import Path
import tempfile
import unittest


class PortableComposedGateTests(unittest.TestCase):
    def test_partial_states_citations_and_joins_fail_closed(self):
        support=importlib.import_module('tests.portable_gate_support')
        from briefforge import research_context_composed_payload_validation as validation
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'positive';root.mkdir()
            request,files=support.synthetic_fixture(root)
            admitted=validation.validate_research_context_composed_payload(request)
            self.assertEqual(admitted.component_states,(('equity','available'),('macro','unavailable'),('knowledge','blocked')))
            descriptor=json.loads(files['COMPOSED_PAYLOAD.json'])
            self.assertEqual([x['reason_codes'] for x in descriptor['components']],
                [[],['no_accepted_matching_artifact'],['general_company_claim_export_not_authoritative']])
            self.assertEqual([x['payload'] for x in descriptor['components'][1:]],[None,None])
            self.assertEqual(len(descriptor['compatibility_findings']),3)
            self.assertTrue(all(x['status']=='blocked' and x['authorized_join'] is False for x in descriptor['compatibility_findings']))
            self.assertNotIn('citations',json.loads(files['payloads/equity.json']))
            # Additive C5 ruling: undeclared-field schema refusal and separate declared semantic refusal.
            cases=[('unauthorized_join','SCHEMA_INVALID'),('authorized_join','UNAUTHORIZED_JOIN'),('citations','SCHEMA_INVALID'),('knowledge_claim','SCHEMA_INVALID'),('equity_state','STATE_MISMATCH')]
            for mutation,expected in cases:
                with self.subTest(mutation=mutation,expected=expected):
                    attack=Path(tmp)/mutation;attack.mkdir()
                    authored,container=support.synthetic_fixture(attack)
                    d=json.loads(container['COMPOSED_PAYLOAD.json'])
                    p=json.loads(container['payloads/equity.json'])
                    if mutation=='unauthorized_join':d['compatibility_findings'][0]['unauthorized_join']=True
                    elif mutation=='authorized_join':
                        d['compatibility_findings'][0]['authorized_join']=True
                        from jsonschema import Draft202012Validator
                        schema=json.loads(container['schemas/companion.schema.json'])
                        Draft202012Validator(schema).validate(d)
                    elif mutation=='citations':p['citations']=[{'claim':'not admitted'}]
                    elif mutation=='knowledge_claim':p['knowledge_claim']='not admitted'
                    else:d['components'][0]['state']='blocked'
                    container['COMPOSED_PAYLOAD.json']=support.canonical(d)+b'\n'
                    container['payloads/equity.json']=support.canonical(p)+b'\n'
                    authored=support.reseal_synthetic_outer(authored,container)
                    with self.assertRaises(validation.ComposedPackageError) as caught:
                        validation.validate_research_context_composed_payload(authored)
                    self.assertEqual(caught.exception.code,expected)

    def test_independent_pins_reject_resealed_tampering(self):
        from tests import portable_gate_support as s
        from briefforge import research_context_composed_payload_validation as v
        with tempfile.TemporaryDirectory() as tmp:
            for target,expected in [('payload','COMPANION_TRUST_MISMATCH'),('source','SOURCE_PACKAGE_MISMATCH')]:
                with self.subTest(target=target):
                    root=Path(tmp)/target;root.mkdir();request,files=s.synthetic_fixture(root)
                    if target=='payload':
                        p=json.loads(files['payloads/equity.json']);p['rights']='tampered';files['payloads/equity.json']=s.canonical(p)+b'\n'
                        s.reseal_synthetic_outer(request,files) # original out-of-band receipt deliberately retained
                    else:
                        files['proof/bundle-manifest.sha256']=files['proof/bundle-manifest.sha256'].replace(b'  BUNDLE.json',b'  FORGED.json')
                        request=s.reseal_synthetic_outer(request,files) # source pins deliberately retained
                    with self.assertRaises(v.ComposedPackageError) as error:v.validate_research_context_composed_payload(request)
                    self.assertEqual(error.exception.code,expected)

    def test_both_witness_orders_complete_pipeline(self):
        from tests import portable_gate_support as s
        from briefforge.research_context_composed_payload_validation import validate_research_context_composed_payload
        from briefforge.research_context_composed_payload_adapter import adapt_research_context_composed_payload
        from briefforge.validation import validate_candidate_presentation_package
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.research_context_composed_payload_html import render_research_context_composed_payload_html
        financial=[]
        with tempfile.TemporaryDirectory() as tmp:
            for source_order in ('sorted','last'):
                for acceptance_order in ('sorted','last'):
                    with self.subTest(source=source_order,acceptance=acceptance_order):
                        root=Path(tmp)/(source_order+'-'+acceptance_order);root.mkdir();request,files=s.synthetic_fixture(root)
                        for stem,order in [('bundle',source_order),('acceptance',acceptance_order)]:
                            n='proof/'+stem+'-manifest.sha256';lines=files[n].splitlines(keepends=True)
                            if order=='last':lines=[x for x in lines if not x.endswith(b'  MANIFEST.txt\n')]+[x for x in lines if x.endswith(b'  MANIFEST.txt\n')]
                            files[n]=b''.join(lines)
                        request=s.bind_synthetic_witnesses(request,files)
                        admitted=validate_research_context_composed_payload(request);adapted=adapt_research_context_composed_payload(request)
                        judgment=validate_candidate_presentation_package(adapted.candidate);self.assertTrue(judgment.valid)
                        ready=promote_candidate_presentation_package(adapted.candidate,judgment)
                        html=render_research_context_composed_payload_html(request)
                        self.assertEqual(html.accepted_identity,admitted.identity);self.assertEqual(ready.semantic_fingerprint,html.candidate_semantic_fingerprint)
                        financial.append(adapted.source_record_json)
        self.assertEqual(len(financial),4);self.assertEqual(len(set(financial)),1)

    def test_nested_manifest_coverage_and_hash_rejections(self):
        from tests import portable_gate_support as s
        from tests.test_research_context_composed_payload_validation import pin
        from briefforge import research_context_composed_payload_validation as v
        # Acceptance has one native payload; author a second witness entry to genuinely test payload order.
        # It is a synthetic ledger-only opaque entry, not another package file or accepted financial result.
        with tempfile.TemporaryDirectory() as tmp:
            for stem in ('bundle','acceptance','context'):
                for mutation in ('missing','extra','duplicate','order','payload_digest','manifest_digest'):
                    expected='SOURCE_PACKAGE_MISMATCH' if stem!='context' else {'missing':'MANIFEST_COVERAGE','extra':'MANIFEST_COVERAGE','duplicate':'MANIFEST_FORMAT','order':'MANIFEST_FORMAT','payload_digest':'HASH_MISMATCH','manifest_digest':'HASH_MISMATCH'}[mutation]
                    with self.subTest(stem=stem,mutation=mutation,expected=expected):
                        root=Path(tmp)/(stem+'-'+mutation);root.mkdir();request,files=s.synthetic_fixture(root)
                        if stem=='acceptance':
                            txt='proof/acceptance-manifest.txt';files[txt]=b'AUXILIARY.json\t2\t'+pin(b'{}').sha256.encode()+b'\n'+files[txt]
                            sha='proof/acceptance-manifest.sha256';files[sha]=pin(b'{}').sha256.encode()+b'  AUXILIARY.json\n'+pin(files[txt]).sha256.encode()+b'  MANIFEST.txt\n'+next(x+b'\n' for x in files[sha].splitlines() if x.endswith(b'  PUBLIC_CONSUMER_RESULTS.json'))
                        if stem=='context':name='context/MANIFEST.sha256'
                        else:name='proof/'+stem+'-manifest.sha256'
                        rows=files[name].splitlines(keepends=True);payload=[i for i,x in enumerate(rows) if not x.endswith(b'  MANIFEST.txt\n')];manifest=next(i for i,x in enumerate(rows) if x.endswith(b'  MANIFEST.txt\n'))
                        if mutation=='missing':rows.pop(payload[0])
                        elif mutation=='extra':rows.append(b'0'*64+b'  z-extra.json\n')
                        elif mutation=='duplicate':rows.insert(payload[0]+1,rows[payload[0]])
                        elif mutation=='order':rows[payload[0]],rows[payload[1]]=rows[payload[1]],rows[payload[0]]
                        elif mutation=='payload_digest':rows[payload[0]]=b'0'*64+rows[payload[0]][64:]
                        else:rows[manifest]=b'0'*64+rows[manifest][64:]
                        files[name]=b''.join(rows)
                        if stem=='context':
                            context=dataclasses.replace(request.trust.context,manifests=dataclasses.replace(request.trust.context.manifests,manifest_sha256=pin(files[name])))
                            request=s.reseal_synthetic_outer(dataclasses.replace(request,trust=dataclasses.replace(request.trust,context=context)),files)
                        else:request=s.bind_synthetic_witnesses(request,files)
                        with self.assertRaises(v.ComposedPackageError) as caught:v.validate_research_context_composed_payload(request)
                        self.assertEqual(caught.exception.code,expected)

    def test_exact_typed_value_and_provenance_projection(self):
        from tests import portable_gate_support as s
        with tempfile.TemporaryDirectory() as tmp:
            request,files=s.synthetic_fixture(Path(tmp));adapted,html,projection=s.assert_projection(self,request,files)
            self.assertEqual(projection['ratio_value'],'0.2125')
            self.assertEqual(json.loads(adapted.source_record_json)['numerator_cell_usable'],True)
            self.assertLessEqual(len(html.html_bytes),262144)

    def test_all_rendered_candidate_text_is_escaped(self):
        from tests import portable_gate_support as s
        from briefforge.research_context_composed_payload_adapter import adapt_research_context_composed_payload
        from briefforge.research_context_composed_payload_html import _html
        from briefforge.validation import validate_candidate_presentation_package
        hostile='<script>window.pwned=1</script>\"\' & </p><img src="https://invalid.example/a" onerror="pwned=1">Ω\u202e'
        def paths(value,prefix=()):
            if dataclasses.is_dataclass(value):
                for field in dataclasses.fields(value):yield from paths(getattr(value,field.name),prefix+(field.name,))
            elif type(value) is tuple:
                for i,item in enumerate(value):yield from paths(item,prefix+(i,))
            elif type(value) is str:yield prefix
        def inject(value,path):
            key,*tail=path
            if dataclasses.is_dataclass(value):return dataclasses.replace(value,**{key:inject(getattr(value,key),tail) if tail else hostile})
            items=list(value);items[key]=inject(items[key],tail) if tail else hostile;return tuple(items)
        with tempfile.TemporaryDirectory() as tmp:
            request,_=s.synthetic_fixture(Path(tmp));candidate=adapt_research_context_composed_payload(request).candidate
            baseline=s.parsed_html(_html(candidate));covered=[]
            for path in paths(candidate):
                # encounter_semantics is intentionally not rendered; all remaining candidate strings are rendered.
                if 'encounter_semantics' in path:continue
                with self.subTest(field=path,scope='renderer projection unit; identity/reference injection is not authority admission'):
                    changed=inject(candidate,path);judgment=validate_candidate_presentation_package(changed)
                    document=s.parsed_html(_html(changed));self.assertIn(hostile,''.join(document.text))
                    self.assertEqual([x[0] for x in document.elements],[x[0] for x in baseline.elements])
                    self.assertEqual(document.elements,baseline.elements)
                    self.assertFalse(any(tag in ('script','img','iframe') or any(k.startswith('on') or k in ('src','href') for k in attrs) for tag,attrs in document.elements))
                    covered.append(dict(path=list(path),fresh_judgment_valid=judgment.valid))
            s.runtime_output('composed/escaping.json',dict(scope='isolated projection unit only; public admission covered separately',fields=covered))

    def test_determinism_across_hash_seeds_and_synthetic_roots(self):
        import os,subprocess,sys
        from tests import portable_gate_support as s
        code="from pathlib import Path;import tempfile,json,hashlib;from tests.portable_gate_support import synthetic_fixture;from briefforge.research_context_composed_payload_html import render_research_context_composed_payload_html\nwith tempfile.TemporaryDirectory() as t:\n r,_=synthetic_fixture(Path(t));v=render_research_context_composed_payload_html(r);print(json.dumps({'html':v.html_bytes.decode(),'sha256':v.sha256,'fingerprint':v.candidate_semantic_fingerprint,'root':t}))"
        outputs=[]
        for seed in ('0','1','37'):
            for replica in range(2):
                with self.subTest(seed=seed,replica=replica):
                    p=subprocess.run([sys.executable,'-B','-c',code],env=dict(os.environ,PYTHONHASHSEED=seed),capture_output=True,text=True,check=True)
                    value=json.loads(p.stdout);self.assertNotIn(value.pop('root'),value['html']);self.assertLessEqual(len(value['html'].encode()),262144);outputs.append(value)
        self.assertEqual(len({json.dumps(x,sort_keys=True) for x in outputs}),1)
        s.runtime_output('composed/determinism.json',dict(seeds=[0,1,37],roots=6,sha256=outputs[0]['sha256'],fingerprint=outputs[0]['fingerprint']))

    def test_cross_forge_and_network_independence(self):
        import os,subprocess,sys,ast
        from tests import portable_gate_support as s
        code='''import sys,importlib.abc,socket,urllib.request,http.client,subprocess,json,tempfile,builtins
from pathlib import Path
trace=[]
class Deny(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname.split('.')[0].lower() in ('equityforge','macroforge','knowledgeforge','insightforge'):trace.append(fullname);raise RuntimeError('producer import denied')
sys.meta_path.insert(0,Deny())
def deny(*a,**kw):trace.append('forbidden network/producer execution');raise RuntimeError('denied')
socket.create_connection=deny;socket.socket.connect=deny;socket.getaddrinfo=deny;urllib.request.urlopen=deny;http.client.HTTPConnection.connect=deny;subprocess.Popen=deny
from tests.portable_gate_support import synthetic_fixture
from briefforge.research_context_composed_payload_html import render_research_context_composed_payload_html
with tempfile.TemporaryDirectory() as t:
 r,_=synthetic_fixture(Path(t));original=builtins.open
 def checked(file,*a,**kw):
  if str(file)==r.trust.address.component_path:trace.append('inert locator opened');raise RuntimeError('inert path opened')
  return original(file,*a,**kw)
 builtins.open=checked;v=render_research_context_composed_payload_html(r)
 print(json.dumps({'sha256':v.sha256,'trace':trace,'modules':[m for m in sys.modules if m.split('.')[0].lower() in ('equityforge','macroforge','knowledgeforge','insightforge')]}))
'''
        proc=subprocess.run([sys.executable,'-B','-c',code],env=os.environ,capture_output=True,text=True,check=True);result=json.loads(proc.stdout)
        self.assertEqual(result['trace'],[]);self.assertEqual(result['modules'],[])
        from tools.run_test_profile import ROOT
        imports=[]
        for name in ('validation','adapter','html'):
            tree=ast.parse((ROOT/'src/briefforge'/('research_context_composed_payload_'+name+'.py')).read_bytes())
            for node in ast.walk(tree):
                if isinstance(node,ast.Import):imports.extend(x.name for x in node.names)
                elif isinstance(node,ast.ImportFrom):imports.append(node.module or '')
        self.assertFalse(any(x.split('.')[0].lower() in ('equityforge','macroforge','knowledgeforge','insightforge') for x in imports))
        s.runtime_output('composed/independence.json',dict(child=result,inspected_imports=imports))

    def test_mobile_layout_and_csp_in_real_browser(self):
        import os,base64,hashlib
        from tests import portable_gate_support as s
        from briefforge.research_context_composed_payload_html import render_research_context_composed_payload_html

        run=Path(os.environ['BRIEFFORGE_TEST_RUN_ROOT']);out=run/'browser';out.mkdir();measurements=[]
        with tempfile.TemporaryDirectory() as tmp:
            request,_=s.synthetic_fixture(Path(tmp));view=render_research_context_composed_payload_html(request);file=out/'composed.html';file.write_bytes(view.html_bytes)
            with s.browser_runtime() as pw:
                browser=pw.chromium.launch(executable_path=os.environ['BRIEFFORGE_TEST_BROWSER'],headless=True,args=['--no-sandbox'])
                try:
                    for width,height in ((320,800),(390,844),(768,1024),(1280,800)):
                        with self.subTest(viewport=(width,height)):
                            page=browser.new_page(viewport={'width':width,'height':height});requests=[];errors=[];console=[];routed=[];finished=[];failed=[]
                            page.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) else None)
                            page.on('requestfinished',lambda r:finished.append(r.url) if r.url.startswith(('http:','https:')) else None)
                            page.on('requestfailed',lambda r:failed.append(dict(url=r.url,failure=r.failure)) if r.url.startswith(('http:','https:')) else None)
                            page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:console.append(dict(type=m.type,text=m.text)))
                            def deny(route):routed.append(route.request.url);route.abort()
                            page.route('https://**/*',deny);page.route('http://**/*',deny)
                            page.goto(file.as_uri());dimensions=page.evaluate('''() => ({viewport:[innerWidth,innerHeight],overflow:document.documentElement.scrollWidth-innerWidth,sections:Array.from(document.querySelectorAll('article section')).map(e=>({id:e.id,top:e.getBoundingClientRect().top,bottom:e.getBoundingClientRect().bottom,visible:e.getBoundingClientRect().height>0})),paragraphs:Array.from(document.querySelectorAll('p,li')).map(e=>({text:e.textContent,client:e.clientWidth,scroll:e.scrollWidth,style:getComputedStyle(e).overflowWrap})),csp:document.querySelector('[http-equiv="Content-Security-Policy"]').content,style:document.querySelector('style').textContent,viewportMeta:document.querySelector('[name=viewport]').content})''')
                            self.assertEqual(dimensions['viewport'],[width,height]);self.assertLessEqual(dimensions['overflow'],1)
                            self.assertEqual([x['id'] for x in dimensions['sections']],['observation','period-measurement','numerator','denominator','availability-provenance','component-states','limitations'])
                            self.assertTrue(all(x['visible'] for x in dimensions['sections']))
                            self.assertTrue(all(a['bottom']<=b['top'] for a,b in zip(dimensions['sections'],dimensions['sections'][1:])))
                            paragraphs=dimensions['paragraphs'];self.assertTrue(any('0.2125' in p['text'] for p in paragraphs));self.assertTrue(any('source document' in p['text'] and len(p['text'])>200 for p in paragraphs))
                            self.assertTrue(all(p['scroll']<=p['client']+1 and p['style']=='anywhere' for p in paragraphs))
                            style_hash=base64.b64encode(hashlib.sha256(dimensions['style'].encode()).digest()).decode();self.assertIn("'sha256-"+style_hash+"'",dimensions['csp']);self.assertIn("default-src 'none'",dimensions['csp'])
                            self.assertEqual(requests,[]);self.assertEqual(errors,[]);self.assertEqual(dimensions['viewportMeta'],'width=device-width, initial-scale=1')
                            shot='browser/'+str(width)+'x'+str(height)+'.png';page.screenshot(path=str(run/shot),full_page=True)
                            page.evaluate('''() => {window.violations=[];document.addEventListener('securitypolicyviolation',e=>violations.push({directive:e.effectiveDirective,blocked:e.blockedURI}));let s=document.createElement('script');s.textContent='window.inlineExecuted=true';document.body.append(s);let i=document.createElement('img');i.src='https://invalid.example/csp-image';document.body.append(i);fetch('https://invalid.example/csp-fetch').catch(()=>{});}''')
                            page.wait_for_timeout(150);enforcement=page.evaluate('''() => ({executed:window.inlineExecuted===true,violations:window.violations,imageLoaded:Array.from(document.images).some(i=>i.naturalWidth>0)})''')
                            measurements.append(dict(viewport=[width,height],overflow=dimensions['overflow'],attempted_requests=list(requests),external_requests=list(finished),routed_requests=list(routed),failed_requests=list(failed),page_errors=list(errors),console=list(console),enforcement=enforcement,dimensions=dimensions,screenshot=shot,html_sha256=view.sha256,browser_version=browser.version))
                            s.runtime_output('browser/measurements-'+str(width)+'x'+str(height)+'.json',measurements[-1])
                            # A request event records an attempt, not a network
                            # load. CSP must reject before the deny route, with
                            # no completed loads; do not credit route aborts as CSP.
                            self.assertFalse(enforcement['executed']);self.assertFalse(enforcement['imageLoaded']);self.assertEqual(routed,[]);self.assertEqual(finished,[]);self.assertEqual(errors,[])
                            self.assertEqual(requests,['https://invalid.example/csp-image'])
                            self.assertEqual([x['url'] for x in failed],requests);self.assertTrue(all(x['failure'] for x in failed))
                            # Browser network error wording is not a public
                            # contract. The policy-violation event is the proof.
                            self.assertIn({'directive':'img-src','blocked':'https://invalid.example/csp-image'},enforcement['violations'])
                            self.assertIn({'directive':'connect-src','blocked':'https://invalid.example/csp-fetch'},enforcement['violations'])
                            directives={x['directive'] for x in enforcement['violations']};self.assertTrue({'script-src-elem','img-src','connect-src'}<=directives)
                            measurements[-1].update(passed=True,csp_enforced=True)
                            page.close()
                finally:browser.close()
        s.runtime_output('browser/measurements.json',measurements)
