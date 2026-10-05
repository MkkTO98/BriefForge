"""Authenticated external composed package; copies are disposable, originals read-only."""
import dataclasses
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from tests import portable_gate_support as s


class LocalComposedIntegrationTests(unittest.TestCase):
    def test_real_judgment_promotion_and_bounded_html(self):
        from tools import run_test_profile as r
        from briefforge.research_context_composed_payload_validation import validate_research_context_composed_payload
        from briefforge.validation import validate_candidate_presentation_package
        from briefforge.promotion import promote_candidate_presentation_package
        request,reconciliation=s.local_request();before=r.snapshot(request.package_dir)
        import sys
        from briefforge.research_context_composed_payload_html import render_research_context_composed_payload_html
        trace=[]
        def record(frame,event,arg):
            if event=='call' and frame.f_code.co_name in ('adapt_research_context_composed_payload','validate_candidate_presentation_package','promote_candidate_presentation_package') and '/src/briefforge/' in frame.f_code.co_filename:trace.append(frame.f_code.co_name)
        old=sys.getprofile()
        try:
            sys.setprofile(record);first=render_research_context_composed_payload_html(request);second=render_research_context_composed_payload_html(request)
        finally:sys.setprofile(old)
        self.assertEqual(first,second);self.assertLessEqual(len(first.html_bytes),262144)
        for name in ('adapt_research_context_composed_payload','validate_candidate_presentation_package','promote_candidate_presentation_package'):self.assertGreaterEqual(trace.count(name),2)
        self.assertEqual(first.sha256,reconciliation['sha256']);self.assertEqual(len(first.html_bytes),reconciliation['html_bytes'])
        admitted=validate_research_context_composed_payload(request);adapted,html,projection=s.assert_projection(self,request,s.package_bytes(request.package_dir))
        judgment=validate_candidate_presentation_package(adapted.candidate);self.assertTrue(judgment.valid);ready=promote_candidate_presentation_package(adapted.candidate,judgment)
        self.assertEqual(admitted.identity,request.expected_identity);self.assertEqual(html.candidate_semantic_fingerprint,'2e5cfba2ad3ef94ae90f4cb3354dcf992eb4c9ce51dd5c0874332d3bdca323dc');self.assertEqual(ready.semantic_fingerprint,html.candidate_semantic_fingerprint)
        self.assertEqual(reconciliation['candidate_semantic_fingerprint'],html.candidate_semantic_fingerprint);self.assertEqual(projection['ratio_value'],'0.292836472912');r.require_preserved(before,r.snapshot(request.package_dir))
        self.assertEqual(first,html);d=json.loads((request.package_dir/'COMPOSED_PAYLOAD.json').read_bytes());p=json.loads((request.package_dir/'payloads/equity.json').read_bytes())
        self.assertEqual([c['state'] for c in d['components']],['available','unavailable','blocked']);self.assertTrue(all(not f['authorized_join'] and f['status']=='blocked' for f in d['compatibility_findings']));self.assertNotIn('citations',p);self.assertNotIn('knowledge_claim',p)
        s.runtime_output('local/render-trace.json',dict(accepted_identity=dataclasses.asdict(admitted.identity),original_external_trust=dataclasses.asdict(request.trust),fingerprint=html.candidate_semantic_fingerprint,html_sha256=html.sha256,actual_profile_calls=trace,public_renders=2,preserved=True))

    def test_exact_real_financial_record_and_provenance(self):
        from tools import run_test_profile as r
        request,_=s.local_request();before=r.snapshot(request.package_dir);files=s.package_bytes(request.package_dir)
        adapted,html,projection=s.assert_projection(self,request,files)
        self.assertEqual(request.trust.address.zero_based_row_index,1300);self.assertEqual(json.loads(adapted.source_record_json)['entity_key'],'0000320193');self.assertEqual(projection['value_convention'],'fraction_not_percent')
        self.assertIsNone(json.loads(files['payloads/equity.json'])['producer_record_hash']);self.assertIs(projection['research_value_usable'],True);self.assertEqual(projection['blocking_reasons'],[])
        self.assertEqual(set(projection['inputs_and_provenance']),{'numerator','denominator'});r.require_preserved(before,r.snapshot(request.package_dir))
        s.runtime_output('local/projection.json',dict(address=dataclasses.asdict(request.trust.address),complete_typed_projection=projection,source_row=json.loads(adapted.source_record_json),preserved=True))

    def test_real_package_relocation_without_authority_migration(self):
        from tools import run_test_profile as r
        from briefforge.research_context_composed_payload_html import render_research_context_composed_payload_html
        from briefforge.research_context_composed_payload_adapter import adapt_research_context_composed_payload
        request,_=s.local_request();before=r.snapshot(request.package_dir);original=render_research_context_composed_payload_html(request)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'relocated';root.mkdir();files=s.copy_package(request.package_dir,root);copied=dataclasses.replace(request,package_dir=root)
            self.assertEqual(copied.trust,request.trust);self.assertEqual(copied.expected_identity,request.expected_identity)
            relocated=render_research_context_composed_payload_html(copied);self.assertEqual(relocated,original)
            self.assertEqual(adapt_research_context_composed_payload(copied),adapt_research_context_composed_payload(request));self.assertEqual(files,s.package_bytes(request.package_dir));self.assertNotIn(str(root),relocated.html_bytes.decode())
        r.require_preserved(before,r.snapshot(request.package_dir));s.runtime_output('local/relocation.json',dict(html_sha256=original.sha256,original_independent_pins_unchanged=True,byte_container_relocation_only=True,preserved=True))

    def test_real_input_tampering_rejected_without_mutation(self):
        from tools import run_test_profile as r
        from briefforge.research_context_composed_payload_validation import validate_research_context_composed_payload,ComposedPackageError
        request,_=s.local_request();before=r.snapshot(request.package_dir);cases=[]
        with tempfile.TemporaryDirectory() as tmp:
            for mutation in ('raw_payload_byte','row','acceptance','entity','period','operand','schema','unauthorized_join','link'):
                # Public filesystem contract, not a code inferred from the run:
                # validator scan rejects links as SYMLINK_FORBIDDEN before trust.
                expected='SYMLINK_FORBIDDEN' if mutation=='link' else ('HASH_MISMATCH' if mutation=='raw_payload_byte' else 'COMPANION_TRUST_MISMATCH')
                with self.subTest(mutation=mutation,expected=expected):
                    root=Path(tmp)/mutation;root.mkdir();files=s.copy_package(request.package_dir,root);copied=dataclasses.replace(request,package_dir=root)
                    if mutation=='raw_payload_byte':
                        target=root/'payloads/equity.json';raw=target.read_bytes();target.write_bytes(raw.replace(b'0.292836472912',b'0.292836472913',1))
                    elif mutation=='link':
                        target=root/'payloads/equity.json';target.unlink();target.symlink_to(root/'proof/producer-component.json')
                    else:
                        if mutation=='schema':files['schemas/equity-observation.schema.json']+=b' '
                        elif mutation=='row':
                            rows=json.loads(files['proof/producer-component.json']);rows[1300]['ratio_value']='0.1';files['proof/producer-component.json']=s.canonical(rows)+b'\n'
                        elif mutation=='acceptance':
                            results=json.loads(files['proof/acceptance-results.json']);results[request.trust.acceptance.result_key]['results'][0]['latest_usable']['ratio_value']='0.1';files['proof/acceptance-results.json']=s.canonical(results)+b'\n'
                        elif mutation=='unauthorized_join':
                            d=json.loads(files['COMPOSED_PAYLOAD.json']);d['compatibility_findings'][0]['authorized_join']=True;files['COMPOSED_PAYLOAD.json']=s.canonical(d)+b'\n'
                        else:
                            p=json.loads(files['payloads/equity.json']);field={'entity':'entity_key','period':'period_end','operand':'numerator_canonical_value'}[mutation];p['source_record'][field]={'entity':'0000000000','period':'2025-12-26','operand':'1'}[mutation];files['payloads/equity.json']=s.canonical(p)+b'\n'
                        # Only the disposable container is resealed. Original
                        # caller trust and expected companion identity stay fixed.
                        self.assertNotEqual(root,request.package_dir);self.assertEqual(copied.trust,request.trust);self.assertEqual(copied.expected_identity,request.expected_identity)
                        names=sorted(set(files)-{'MANIFEST.txt','MANIFEST.sha256'})
                        files['MANIFEST.txt']=''.join(n+'\t'+str(len(files[n]))+'\t'+hashlib.sha256(files[n]).hexdigest()+'\n' for n in names).encode()
                        files['MANIFEST.sha256']=''.join(hashlib.sha256(files[n]).hexdigest()+'  '+n+'\n' for n in sorted(names+['MANIFEST.txt'])).encode()
                        for name,raw in files.items():
                            target=root/name;self.assertFalse(target.is_symlink());target.write_bytes(raw)
                    with self.assertRaises(ComposedPackageError) as error:validate_research_context_composed_payload(copied)
                    self.assertEqual(error.exception.code,expected);cases.append(dict(mutation=mutation,expected=expected,actual=error.exception.code,original_external_pins_retained=True))
        r.require_preserved(before,r.snapshot(request.package_dir));s.runtime_output('local/negative.json',dict(cases=cases,scope='independent authority rejection; not claimed as deeper semantic branch coverage',preserved=True))

    def test_authenticated_external_inputs_and_independent_request(self):
        import os,copy
        from tools import run_test_profile as r
        m=r.read_profile();e=Path(os.environ['BRIEFFORGE_TEST_EVIDENCE_ROOT']);original=r.local_receipt(m,e);before=r.snapshot(e/'Suite-Logs'/r.RESTORATION)
        from briefforge.research_context_composed_payload_validation import validate_research_context_composed_payload
        request,_=s.local_request();admitted=validate_research_context_composed_payload(request);self.assertEqual(admitted.identity,request.expected_identity)
        self.assertEqual(set(s.package_bytes(request.package_dir)),set(r.ledger_rows(request.package_dir/'MANIFEST.sha256'))|{'MANIFEST.sha256'})
        with tempfile.TemporaryDirectory() as tmp:
            with self.subTest(challenge='missing provenance'):
                with self.assertRaises(r.ProfileError):r.local_receipt(m,Path(tmp))
            for field in ('preflight_manifest_sha256','local_result_pin'):
                with self.subTest(challenge='stale '+field):
                    altered=copy.deepcopy(m)
                    if field=='preflight_manifest_sha256':altered[field]='0'*64
                    else:altered['local_pins']['VERIFICATION_SUMMARY.json']['sha256']='0'*64
                    with self.assertRaises(r.ProfileError):r.local_receipt(altered,e)
        self.assertEqual(r.local_receipt(m,e),original);r.require_preserved(before,r.snapshot(e/'Suite-Logs'/r.RESTORATION));s.runtime_output('local/provenance-challenges.json',dict(admission=original,missing_rejected=True,stale_rejected=True,preserved=True))
