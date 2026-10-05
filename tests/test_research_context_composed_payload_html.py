"""Bounded local composed-payload HTML: synthetic, offline, test-first contract."""
import dataclasses
import base64
import hashlib
from html.parser import HTMLParser
import inspect
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from briefforge import research_context_composed_payload_html as view
from briefforge.research_context_composed_payload_adapter import adapt_research_context_composed_payload
from briefforge.research_context_composed_payload_validation import ComposedPackageError
from briefforge.runtime import semantic_fingerprint
from test_research_context_composed_payload_validation import fixture


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        self.text.append(data)


class ComposedHtmlTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'package'
        self.root.mkdir()
        self.request, self.files = fixture(self.root)

    def render(self):
        result = view.render_research_context_composed_payload_html(self.request)
        doc = Document()
        doc.feed(result.html_bytes.decode('utf-8'))
        doc.close()
        return result, doc

    def test_public_signature_frozen_slotted_result_and_exact_identities(self):
        self.assertEqual(str(inspect.signature(view.render_research_context_composed_payload_html)),
                         '(request: ComposedPackageRequest, /) -> ComposedHtmlView')
        self.assertEqual([f.name for f in dataclasses.fields(view.ComposedHtmlView)],
                         ['html_bytes', 'sha256', 'accepted_identity', 'context_id',
                          'candidate_semantic_fingerprint', 'renderer_version'])
        result, _ = self.render()
        self.assertTrue(result.__dataclass_params__.frozen)
        self.assertFalse(hasattr(result, '__dict__'))
        self.assertIs(type(result.html_bytes), bytes)
        self.assertEqual(result.sha256, hashlib.sha256(result.html_bytes).hexdigest())
        adapter = adapt_research_context_composed_payload(self.request)
        self.assertEqual(result.accepted_identity, adapter.accepted_identity)
        self.assertEqual(result.context_id, adapter.context_id)
        self.assertEqual(result.candidate_semantic_fingerprint, semantic_fingerprint(adapter.candidate))
        self.assertEqual(result.renderer_version, 'briefforge.research-context-composed-payload-html.v1.0.0')
        self.assertRaises(dataclasses.FrozenInstanceError, setattr, result, 'sha256', '0')

    def test_exact_semantic_parity_all_statements_references_obligations(self):
        result, doc = self.render()
        candidate = adapt_research_context_composed_payload(self.request).candidate
        text = ''.join(doc.text)
        for source in (candidate.identity.package_id, candidate.identity.title,
                       candidate.identity.purpose_summary, candidate.identity.scope,
                       candidate.identity.non_scope, candidate.organizing_purpose.statement,
                       candidate.organizing_purpose.scope, candidate.organizing_purpose.non_scope):
            self.assertIn(source, text)
        for statement in candidate.statements:
            for field in (statement.statement_id, statement.encounter_meaning,
                          statement.belongs_to_purpose, *statement.upstream_reference_ids,
                          *statement.obligation_ids):
                self.assertIn(field, text)
        for reference in candidate.upstream_references:
            for field in dataclasses.astuple(reference):
                self.assertIn(field, text)
        for obligation in candidate.obligations:
            for field in (obligation.obligation_id, obligation.category,
                          obligation.requirement, *obligation.applies_to):
                self.assertIn(field, text)
        self.assertEqual([a.get('id') for tag, a in doc.elements if tag == 'section'],
                         [s.statement_id for s in candidate.statements])
        self.assertLess(text.index('0.2125'), text.index('21.25%'))
        self.assertLessEqual(len(result.html_bytes), 262144)

    def test_partial_states_provenance_non_pit_and_rights_visible(self):
        _, doc = self.render()
        text = ''.join(doc.text)
        for value in ('Lantern Orchard Fictional Co.', '0000999901', '0.2125', '21.25%',
                      'display-only', 'fraction_not_percent', 'Not issuer-reported',
                      'net_margin', 'tenq_ratio_research.v1', '2042-01-01', '2042-03-31',
                      '1700', '8000', 'NetIncomeLoss',
                      'RevenueFromContractWithCustomerExcludingAssessedTax',
                      '0000999901-42-999001', '2042-05-09', 'non-PIT',
                      'partial', 'equity available', 'macro unavailable', 'knowledge blocked',
                      'no_accepted_matching_artifact',
                      'general_company_claim_export_not_authoritative',
                      'unauthorized', 'no macro observation or knowledge claim/citation supplied',
                      'local_evidence_review_only_no_redistribution_grant',
                      'producer_record_hash null', 'not freshly verified original export'):
            self.assertIn(value.lower(), text.lower())
        self.assertNotIn(str(self.root), result_text := text)
        self.assertNotIn(str(Path.home()), result_text)

    def test_actual_elements_attributes_csp_and_inert_hostile_text(self):
        original = adapt_research_context_composed_payload(self.request)
        hostile = '<img src="https://evil.test/a" onerror="run()"> https://example.test onload=ok & " \' </script>'
        candidate = dataclasses.replace(original.candidate, statements=(
            dataclasses.replace(original.candidate.statements[0],
                                encounter_meaning=original.candidate.statements[0].encounter_meaning + hostile),
            *original.candidate.statements[1:]))
        altered = dataclasses.replace(original, candidate=candidate)
        with patch.object(view, 'adapt_research_context_composed_payload', return_value=altered):
            result, doc = self.render()
        html = result.html_bytes.decode('utf-8')
        self.assertIn(hostile, ''.join(doc.text))
        self.assertIn('&lt;img', html)
        forbidden = {'script', 'img', 'iframe', 'object', 'embed', 'link', 'audio',
                     'video', 'source', 'form', 'input', 'button', 'base', 'svg', 'a'}
        self.assertFalse(forbidden & {tag for tag, _ in doc.elements})
        for tag, attrs in doc.elements:
            self.assertFalse(any(key.lower().startswith('on') for key in attrs), (tag, attrs))
            self.assertFalse(any(key.lower() in {'src', 'href', 'srcset', 'action', 'style'}
                                 for key in attrs), (tag, attrs))
        csp = [a.get('content') for t, a in doc.elements if t == 'meta' and a.get('http-equiv') == 'Content-Security-Policy']
        self.assertEqual(len(csp), 1)
        self.assertTrue(csp[0].startswith("default-src 'none'; base-uri 'none'; form-action 'none'; object-src 'none'; style-src 'sha256-"))
        styles = re.findall(r'<style>(.*?)</style>', html, re.DOTALL)
        self.assertEqual(len(styles), 1)
        digest = base64.b64encode(hashlib.sha256(styles[0].encode('utf-8')).digest()).decode('ascii')
        self.assertEqual(csp[0], "default-src 'none'; base-uri 'none'; form-action 'none'; object-src 'none'; style-src 'sha256-" + digest + "'")

    def test_independent_pins_and_package_corruption_preserve_adapter_error(self):
        bad_pin = dataclasses.replace(self.request.expected_identity.manifests.manifest_txt,
                                      sha256='0' * 64)
        bad_manifests = dataclasses.replace(self.request.expected_identity.manifests,
                                            manifest_txt=bad_pin)
        bad = dataclasses.replace(self.request, expected_identity=dataclasses.replace(
            self.request.expected_identity, manifests=bad_manifests))
        with self.assertRaises(ComposedPackageError) as caught:
            view.render_research_context_composed_payload_html(bad)
        self.assertEqual(caught.exception.code, 'COMPANION_TRUST_MISMATCH')
        (self.root / 'MANIFEST.txt').write_bytes(b'invalid\n')
        with self.assertRaises(ComposedPackageError) as caught:
            view.render_research_context_composed_payload_html(self.request)
        self.assertEqual(caught.exception.code, 'MANIFEST_FORMAT')

    def test_mandatory_fresh_judgment_and_promotion_order(self):
        from briefforge.validation import validate_candidate_presentation_package
        from briefforge.promotion import promote_candidate_presentation_package
        calls = []
        actual_adapt = view.adapt_research_context_composed_payload
        def adapt(request):
            calls.append('adapt')
            return actual_adapt(request)
        def judge(candidate):
            calls.append('judge')
            return validate_candidate_presentation_package(candidate)
        def promote(candidate, judgment):
            calls.append('promote')
            return promote_candidate_presentation_package(candidate, judgment)
        with patch.object(view, 'adapt_research_context_composed_payload', side_effect=adapt), \
             patch.object(view, 'validate_candidate_presentation_package', side_effect=judge), \
             patch.object(view, 'promote_candidate_presentation_package', side_effect=promote):
            self.render()
            self.render()
        self.assertEqual(calls, ['adapt', 'judge', 'promote'] * 2)

    def test_renderer_policy_rejection_for_invalid_judgment_or_promotion(self):
        from briefforge.promotion import PromotionRejected
        from briefforge.validation import validate_candidate_presentation_package
        actual = adapt_research_context_composed_payload(self.request)
        judgment = dataclasses.replace(validate_candidate_presentation_package(actual.candidate), valid=False)
        with patch.object(view, 'validate_candidate_presentation_package', return_value=judgment), \
             patch.object(view, 'promote_candidate_presentation_package') as promote:
            with self.assertRaises(view.ComposedHtmlPolicyError) as caught:
                self.render()
            self.assertEqual(caught.exception.code, 'CANDIDATE_REJECTED')
            promote.assert_not_called()
        with patch.object(view, 'promote_candidate_presentation_package', side_effect=PromotionRejected('bad')):
            with self.assertRaises(view.ComposedHtmlPolicyError) as caught:
                self.render()
            self.assertEqual(caught.exception.code, 'PROMOTION_REJECTED')

    def test_unsupported_adapter_and_size_limit_have_explicit_policy_errors(self):
        actual = adapt_research_context_composed_payload(self.request)
        with patch.object(view, 'adapt_research_context_composed_payload',
                          return_value=dataclasses.replace(actual, adapter_version='unknown')):
            with self.assertRaises(view.ComposedHtmlPolicyError) as caught:
                self.render()
            self.assertEqual(caught.exception.code, 'ADAPTER_VERSION_UNSUPPORTED')
        candidate = dataclasses.replace(actual.candidate, statements=(
            dataclasses.replace(actual.candidate.statements[0], encounter_meaning='x' * 262145),
            *actual.candidate.statements[1:]))
        with patch.object(view, 'adapt_research_context_composed_payload',
                          return_value=dataclasses.replace(actual, candidate=candidate)):
            with self.assertRaises(view.ComposedHtmlPolicyError) as caught:
                self.render()
            self.assertEqual(caught.exception.code, 'HTML_SIZE_LIMIT')

    def test_deterministic_bytes_no_filesystem_mutation_or_ambient_state(self):
        before = {p.relative_to(self.root): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in self.root.rglob('*') if p.is_file()}
        first, _ = self.render()
        second, _ = self.render()
        after = {p.relative_to(self.root): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(first, second)
        self.assertEqual(before, after)
        self.assertEqual(len(before), 20)
        self.assertEqual(set(before), {p.relative_to(self.root) for p in self.root.rglob('*') if p.is_file()})
        self.assertNotIn(str(self.root).encode(), first.html_bytes)

    def test_source_reference_and_heading_are_escaped_as_inert_text(self):
        actual = adapt_research_context_composed_payload(self.request)
        hostile = '<form action="https://evil.test" onsubmit="run()"> & broken'
        candidate = dataclasses.replace(actual.candidate,
            identity=dataclasses.replace(actual.candidate.identity, title=hostile),
            upstream_references=(dataclasses.replace(actual.candidate.upstream_references[0],
                locator=hostile), *actual.candidate.upstream_references[1:]))
        with patch.object(view, 'adapt_research_context_composed_payload',
                          return_value=dataclasses.replace(actual, candidate=candidate)):
            rendered, doc = self.render()
        self.assertIn(hostile, ''.join(doc.text))
        self.assertNotIn('<form', rendered.html_bytes.decode())
        self.assertNotIn('form', {tag for tag, _ in doc.elements})

    def test_unencodable_source_text_is_a_named_renderer_policy_failure(self):
        actual = adapt_research_context_composed_payload(self.request)
        candidate = dataclasses.replace(actual.candidate,
            identity=dataclasses.replace(actual.candidate.identity, title='bad' + chr(0xd800)))
        with patch.object(view, 'adapt_research_context_composed_payload',
                          return_value=dataclasses.replace(actual, candidate=candidate)):
            with self.assertRaises(view.ComposedHtmlPolicyError) as caught:
                self.render()
        self.assertEqual(caught.exception.code, 'HTML_ENCODING_ERROR')


if __name__ == '__main__':
    unittest.main()
