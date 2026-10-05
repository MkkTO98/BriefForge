"""Adversarial contract tests for exact, non-laundered profile accounting."""
import copy
import importlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


def runner():
    return importlib.import_module('tools.run_test_profile')


def row(identity, layer='software'):
    return dict(original=identity, runtime=identity, profile='portable', layer=layer)


class PortableProfileRunnerTests(unittest.TestCase):
    def test_membership_partition_and_moves_are_exact(self):
        r=runner(); m=r.read_profile()
        actual=r.reconcile(m)
        self.assertEqual(actual, m['counts'])
        self.assertEqual(len(m['rows']),823)
        self.assertEqual(len(m['moves']),40)
        for mutation in ('duplicate','unknown','removed','overlap','ast'):
            bad=copy.deepcopy(m)
            if mutation=='duplicate': bad['rows'].append(copy.deepcopy(bad['rows'][0]))
            if mutation=='unknown': bad['rows'][0]['runtime']='test_unknown.Unknown.test_new'
            if mutation=='removed': bad['rows'].pop()
            if mutation=='overlap': bad['rows'][0]['profile']='historical'
            if mutation=='ast': bad['baseline_method_ast'][bad['rows'][0]['original']]='changed AST'
            with self.subTest(mutation=mutation), self.assertRaises(r.ProfileError):
                r.reconcile(bad)

        # Exact candidate bindings reject altered old/revised/module pins and membership.
        for key in sorted(r.SYNTHETIC_AST):
            for field in ('original_ast_sha256','revised_ast_sha256','original','runtime'):
                bad=copy.deepcopy(m);bad['synthetic_correction_ast'][key][field]='0'*64
                with self.subTest(correction=key,field=field),self.assertRaises(r.ProfileError):r.reconcile(bad)
            bad=copy.deepcopy(m);bad['baseline_method_ast'][key]['historical_ast_sha256']='0'*64
            with self.subTest(correction=key,field='historical_digest'),self.assertRaises(r.ProfileError):r.reconcile(bad)
        for path in sorted(r.SYNTHETIC_MODULE_PINS):
            bad=copy.deepcopy(m);bad['synthetic_correction_module_pins'][path]['sha256']='0'*64
            with self.subTest(correction=path,field='module_pin'),self.assertRaises(r.ProfileError):r.reconcile(bad)
            bad=copy.deepcopy(m);bad['source_pins'][path]['sha256']='0'*64
            with self.subTest(correction=path,field='source_pin'),self.assertRaises(r.ProfileError):r.reconcile(bad)
        for mutation in ('missing','extra'):
            bad=copy.deepcopy(m)
            if mutation=='missing':bad['synthetic_correction_ast'].pop(next(iter(r.SYNTHETIC_AST)))
            else:bad['synthetic_correction_ast']['test_unknown.Unknown.test_new']=copy.deepcopy(next(iter(bad['synthetic_correction_ast'].values())))
            with self.subTest(correction=mutation),self.assertRaises(r.ProfileError):r.reconcile(bad)

    def test_historical_modules_not_imported_for_portable(self):
        r=runner()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'portable_sentinel.py').write_text('import unittest\nclass Safe(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\nclass Historical(unittest.TestCase):\n @classmethod\n def setUpClass(cls): raise AssertionError("historical setup invoked")\n def test_blocked(self): pass\n')
            (root/'historical_sentinel.py').write_text('raise AssertionError("historical module imported")\n')
            with patch.object(__import__('sys'),'path',[tmp,*__import__('sys').path]):
                report=r.execute_selection([row('portable_sentinel.Safe.test_ok')],module_prefix='')
            self.assertEqual(report['counts']['passed'],1)
            self.assertNotIn('historical_sentinel',__import__('sys').modules)
            self.assertEqual(report['loader_errors'],[])

    def test_failures_errors_and_loader_failures_cannot_be_hidden(self):
        r=runner()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'failure_fixture.py').write_text('import unittest\nclass Methods(unittest.TestCase):\n def test_fail(self): self.fail("fixture assertion")\n def test_error(self): raise RuntimeError("fixture error")\n def test_sub(self):\n  for n in [0,1]:\n   with self.subTest(n=n): self.assertEqual(n,0)\nclass Setup(unittest.TestCase):\n @classmethod\n def setUpClass(cls): raise RuntimeError("setup fixture")\n def test_a(self): pass\n def test_b(self): pass\n')
            ids=['failure_fixture.Methods.test_fail','failure_fixture.Methods.test_error','failure_fixture.Methods.test_sub','failure_fixture.Setup.test_a','failure_fixture.Setup.test_b','missing_fixture.No.test_import']
            with patch.object(__import__('sys'),'path',[tmp,*__import__('sys').path]):
                report=r.execute_selection(list(map(row,ids)),module_prefix='')
            self.assertEqual(report['exit_code'],1)
            self.assertEqual(set(report['methods']),set(ids))
            self.assertEqual(report['counts']['passed'],0)
            self.assertEqual(report['counts']['failed'],2)
            self.assertEqual(report['counts']['errored'],4)
            self.assertEqual(report['counts']['started'],3)
            self.assertEqual(report['counts']['completed'],3)
            self.assertEqual(len(report['setup_errors']),1)
            self.assertEqual(len(report['loader_errors']),1)
            self.assertEqual(len(report['subtests']),2)
        from tests.portable_gate_support import interruption_regressions, progress_reconstruction_regressions
        interruption_regressions(self)
        progress_reconstruction_regressions(self)
        from tests.portable_gate_support import diagnostic_privacy_regressions
        diagnostic_privacy_regressions(self)

    def test_missing_inputs_skips_and_unexpected_success_block_pass(self):
        r=runner()
        with tempfile.TemporaryDirectory() as tmp:
            missing=Path(tmp)/'not-present'
            admission=r.admit_dependencies({'paths':[str(missing)],'browser':str(missing),'platform':'unsupported'})
            self.assertEqual(admission['exit_code'],2)
            self.assertEqual(admission['status'],'BLOCKED')
            self.assertGreaterEqual(len(admission['missing']),3)
            p=Path(tmp)/'outcomes_fixture.py'
            p.write_text('import unittest\nclass Outcomes(unittest.TestCase):\n @unittest.skip("fixture skip")\n def test_skip(self): pass\n @unittest.expectedFailure\n def test_xfail(self): self.fail("expected")\n @unittest.expectedFailure\n def test_xpass(self): pass\n')
            with patch.object(__import__('sys'),'path',[tmp,*__import__('sys').path]):
                report=r.execute_selection([row('outcomes_fixture.Outcomes.'+n) for n in ('test_skip','test_xfail','test_xpass')],module_prefix='')
            self.assertEqual(report['exit_code'],1)
            self.assertEqual({x['status'] for x in report['methods'].values()},{'SKIP','XFAIL','XPASS'})
            self.assertEqual(report['counts']['passed'],0)
        m=r.read_profile();software=r.select(m,'portable','software');local=r.select(m,'portable','local')
        with self.subTest(admission='software-independent'), patch.object(r,'local_receipt',side_effect=AssertionError('unexpected local input read')):
            self.assertEqual(r.local_admission(m,None,software)['status'],'NOT_SELECTED')
            preserved=r.protected_snapshot(m,None)
            self.assertNotIn('local',preserved)
        with self.subTest(admission='missing-local'):
            admitted=r.local_admission(m,None,local)
            self.assertEqual(admitted['status'],'BLOCKED')
            methods=r.initial_methods(local,blocked={x['runtime']:'local inputs missing' for x in local})
            self.assertEqual(r.report_for(methods)['counts']['blocked'],20)
            self.assertEqual(r.report_for(methods)['counts']['started'],0)

    def test_order_hash_and_counts_are_deterministic(self):
        r=runner(); m=r.read_profile()
        a=r.select(m,'portable','all'); b=r.select(dict(m,rows=list(reversed(m['rows']))),'portable','all')
        self.assertEqual(a,b)
        self.assertEqual(r.selection_hash(a),r.selection_hash(b))
        self.assertEqual([x['runtime'] for x in a],sorted(x['runtime'] for x in a))
        software=r.select(m,'portable','software'); local=r.select(m,'portable','local')
        self.assertEqual(len(software),726); self.assertEqual(len(local),20)
        self.assertFalse({x['runtime'] for x in software}&{x['runtime'] for x in local})
        self.assertEqual({x['runtime'] for x in a},{x['runtime'] for x in software+local})
        historical=r.select(m,'historical','all')
        self.assertEqual(len(historical),77)
        self.assertTrue(all(x['prerequisites'] for x in historical))

    def test_outputs_and_protected_state_are_fail_closed(self):
        r=runner()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); existing=root/'existing'; existing.mkdir()
            link=root/'link'; link.symlink_to(existing,target_is_directory=True)
            for p in (existing,link/'escaped',r.ROOT/'fresh-evidence'):
                with self.subTest(path=str(p)),self.assertRaises(r.ProfileError): r.output_destination(p)
            repo=root/'other-repo'; repo.mkdir(); (repo/'.git').mkdir()
            with self.assertRaises(r.ProfileError):r.output_destination(repo/'result')
            protected=root/'protected'; protected.mkdir(); (protected/'input').write_text('frozen')
            before=r.snapshot(protected); (protected/'input').write_text('drift')
            with self.assertRaises(r.ProfileError): r.require_preserved(before,r.snapshot(protected))
            stage=root/'stage'; stage.mkdir(); (stage/'result.json').write_text('{"fixture":true}\n')
            r.seal(stage); r.verify_ledgers(stage)
            final=root/'fresh'; r.publish(stage,final)
            self.assertTrue((final/'MANIFEST.sha256').is_file())
            with self.assertRaises(r.ProfileError):r.publish(final,existing)
            (final/'result.json').write_text('tampered')
            with self.assertRaises(r.ProfileError):r.verify_ledgers(final)
            inherited=tempfile.gettempdir(); inherited_env=os.environ.get('TMPDIR')
            for key in (r.LEGACY_LITERAL_TMP_METHOD, 'fixture.Other.test_unrelated'):
                with self.subTest(tmp_policy=key):
                    with r.legacy_tmp_runtime(key) as policy:
                        self.assertEqual(tempfile.gettempdir(),'/tmp' if key==r.LEGACY_LITERAL_TMP_METHOD else inherited)
                        self.assertEqual(policy['exception_applied'],key==r.LEGACY_LITERAL_TMP_METHOD)
                    self.assertEqual(tempfile.gettempdir(),inherited);self.assertEqual(os.environ.get('TMPDIR'),inherited_env)
            with self.assertRaisesRegex(RuntimeError,'temporary policy challenge'):
                with r.legacy_tmp_runtime(r.LEGACY_LITERAL_TMP_METHOD):raise RuntimeError('temporary policy challenge')
            self.assertEqual(tempfile.gettempdir(),inherited);self.assertEqual(os.environ.get('TMPDIR'),inherited_env)
            owned=root/'owned-stage';owned.mkdir();scratch=owned/'tmp';scratch.mkdir()
            (scratch/'residual').write_bytes(b'disposable residue');(scratch/'link').symlink_to(protected/'input')
            outside_before=r.snapshot(protected);r.finalize_temporary_state(owned)
            self.assertFalse(scratch.exists());self.assertEqual(r.snapshot(protected),outside_before)
            residue=json.loads((owned/'temporary-state.json').read_text())
            self.assertEqual(residue['entries']['link']['type'],'symlink');self.assertEqual(residue['entries']['link']['target'],str(protected/'input'))
            self.assertEqual((owned/'temporary-state-files/residual').read_bytes(),b'disposable residue')
            r.seal(owned);self.assertTrue(r.verify_ledgers(owned))
        from tests.portable_gate_support import git_preservation_regressions
        git_preservation_regressions(self)
