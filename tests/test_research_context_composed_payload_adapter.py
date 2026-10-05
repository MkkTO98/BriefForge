"""RED-first contract tests: the adapter module is intentionally absent at authoring time."""
import ast
import dataclasses
import inspect
import json
from pathlib import Path
import tempfile
import unittest

from briefforge.research_context_composed_payload_adapter import (
    ComposedAdapterResult, adapt_research_context_composed_payload,
)
from briefforge.research_context_composed_payload_validation import ComposedPackageError
from briefforge.runtime import CandidatePresentationPackage, semantic_fingerprint
from briefforge.validation import validate_candidate_presentation_package
from briefforge.promotion import promote_candidate_presentation_package
from test_research_context_composed_payload_validation import fixture, canonical


class AdapterContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'synthetic';self.root.mkdir()
        self.request,self.files=fixture(self.root)

    def run_adapter(self):
        result=adapt_research_context_composed_payload(self.request)
        self.assertIs(type(result),ComposedAdapterResult)
        self.assertIs(type(result.candidate),CandidatePresentationPackage)
        return result

    def test_exact_positional_only_public_signature_and_return(self):
        signature=inspect.signature(adapt_research_context_composed_payload)
        self.assertEqual(str(signature),'(request: ComposedPackageRequest, /) -> ComposedAdapterResult')
        self.assertEqual([f.name for f in dataclasses.fields(ComposedAdapterResult)],['candidate','accepted_identity','context_id','source_record_json','adapter_version'])

    def test_deterministic_single_native_candidate(self):
        a=self.run_adapter();b=self.run_adapter()
        self.assertEqual(semantic_fingerprint(a.candidate),semantic_fingerprint(b.candidate))
        self.assertEqual(a.source_record_json,b.source_record_json)
        self.assertEqual(a.accepted_identity,self.request.expected_identity)
        self.assertEqual(a.context_id,self.request.trust.context.context_id)
        self.assertEqual(a.adapter_version,'briefforge.research-context-composed-payload-adapter.v1.0.0')

    def test_raw_fraction_exact_and_percent_display_only(self):
        result=self.run_adapter()
        body='\n'.join(s.encounter_meaning for s in result.candidate.statements)
        self.assertIn('0.2125',body)
        self.assertIn('21.25%',body)
        self.assertIn('fraction',body.lower())
        source=json.loads(self.files['payloads/equity.json'])['source_record']
        self.assertEqual(result.source_record_json,canonical(source))
        self.assertEqual(source['ratio_value'],'0.2125')

    def test_candidate_constitutionally_valid_without_renderer(self):
        result=self.run_adapter();judgment=validate_candidate_presentation_package(result.candidate)
        self.assertTrue(judgment.valid,judgment.findings)
        ready=promote_candidate_presentation_package(result.candidate,judgment)
        self.assertIs(ready.candidate,result.candidate)

    def test_typed_partial_absences_and_no_joins_are_visible(self):
        result=self.run_adapter()
        visible='\n'.join([*(s.encounter_meaning for s in result.candidate.statements),*(o.requirement for o in result.candidate.obligations)])
        for text in ('partial','equity','available','macro','unavailable','knowledge','blocked','no_accepted_matching_artifact','general_company_claim_export_not_authoritative','unauthorized'):
            self.assertIn(text,visible)
        self.assertEqual(len(result.candidate.upstream_references),4)
        self.assertEqual(len({s.statement_id for s in result.candidate.statements}),len(result.candidate.statements))

    def test_numerator_denominator_provenance_and_limitations(self):
        result=self.run_adapter()
        text='\n'.join([*(s.encounter_meaning for s in result.candidate.statements),*(o.requirement for o in result.candidate.obligations),*(r.locator for r in result.candidate.upstream_references)])
        for fragment in ('Lantern Orchard Fictional Co.','0000999901','2042-01-01','2042-03-31','1700','8000','NetIncomeLoss','RevenueFromContractWithCustomerExcludingAssessedTax','0000999901-42-999001','2042-05-09','non-PIT','computed','local_evidence_review_only_no_redistribution_grant','data/direct_tenq_ratios.json','row:0','historical_filing_completeness_not_certified','sparse_direct_ocf'):
            self.assertIn(fragment,text)

    def test_no_html_publication_or_cli_surface(self):
        r=self.run_adapter()
        self.assertFalse(hasattr(r,'html'))
        self.assertFalse(any('<html' in s.encounter_meaning.lower() for s in r.candidate.statements))
        root=Path(__file__).absolute().parents[1]
        source=(root/'src/briefforge/research_context_composed_payload_adapter.py').read_text()
        tree=ast.parse(source)
        names=[n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        names += [a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names]
        self.assertFalse(any(x.lower().startswith(('equityforge','macroforge','knowledgeforge','src.research_context','socket','requests','urllib','sqlite3')) for x in names))
        self.assertNotIn('if __name__',source)
        self.assertNotIn('render_minimal_html',source)
        self.assertNotIn('write_report',source)
        self.assertNotIn('argparse',source)

    def test_bad_manifest_does_not_return_candidate(self):
        (self.root/'MANIFEST.txt').write_bytes(b'invalid\n')
        with self.assertRaises(ComposedPackageError) as e:adapt_research_context_composed_payload(self.request)
        self.assertEqual(e.exception.code,'MANIFEST_FORMAT')

    def test_inert_address_is_not_read_from_original_source(self):
        result=self.run_adapter()
        self.assertIsInstance(result.candidate,CandidatePresentationPackage)
        self.assertFalse((self.root/'data').exists())

    def test_frozen_package_not_mutated_by_adaptation(self):
        before={n:(self.root/n).read_bytes() for n in self.files}
        self.run_adapter()
        self.assertEqual(before,{n:(self.root/n).read_bytes() for n in self.files})
        self.assertEqual(set(before),set(self.files))


if __name__=='__main__':unittest.main()
