"""Closed synthetic composed-package fixtures and independent admission tests."""
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from briefforge import research_context_composed_payload_validation as v

# Only neutral resources are copied; example data are independently authored below.
_RESOURCE_REL = {
    'companion_schema': 'contracts/research_context_composed_payload_v1/schemas/companion.schema.json',
    'equity_schema': 'contracts/research_context_composed_payload_v1/schemas/equity-observation.schema.json',
    'directory_allowlist': 'contracts/research_context_composed_payload_v1/DIRECTORY_ALLOWLIST.json',
    'context_registry': 'contracts/research_context_v1/producer_registry.json',
    'context_registry_schema': 'contracts/research_context_v1/schemas/producer_registry.schema.json',
    'context_schema': 'contracts/research_context_v1/schemas/research_context.schema.json',
}
_ROOT = Path(__file__).absolute().parents[1]


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(',', ':')).encode('ascii')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(raw):
    return v.FilePin(len(raw), digest(raw))


def record(obj, field, prefix, *other_exclusions):
    return prefix + digest(canonical({k: x for k, x in obj.items() if k not in (field, *other_exclusions)}))


def ledgers(files, prefix=''):
    names = sorted(n[len(prefix):] for n in files if n.startswith(prefix) and n not in {prefix+'MANIFEST.txt', prefix+'MANIFEST.sha256'})
    files[prefix+'MANIFEST.txt'] = ''.join(f'{n}\t{len(files[prefix+n])}\t{digest(files[prefix+n])}\n' for n in names).encode('ascii')
    names = sorted([*names, 'MANIFEST.txt'])
    files[prefix+'MANIFEST.sha256'] = ''.join(f'{digest(files[prefix+n])}  {n}\n' for n in names).encode('ascii')


def authored_example() -> dict:
    """Invented Lantern Orchard test example, not an accepted producer observation.

    The contract's rights vocabulary is retained as a behavior under test, not
    as a claim that upstream restricted records were redistributed. Every data
    object below is constructed independently; only neutral contract resources
    are copied. Hashes and semantic IDs are derived from these authored bytes.
    """
    entity = 'rce1-fictional-lantern-orchard'
    cik, name = '0000999901', 'Lantern Orchard Fictional Co.'
    start, end, filed = '2042-01-01', '2042-03-31', '2042-05-09'
    grain = dict(entity_key=cik, period_start=start, period_end=end,
                 ratio_id='net_margin', source_period_class='first_quarter_duration',
                 track='direct_quarter_duration')
    row = dict(grain, entity_name=name, formula_version='tenq_ratio_research.v1',
               numerator_metric_slot='annual_net_income', denominator_metric_slot='annual_revenue',
               derivation_status='computed', blocking_reasons=[], ratio_value='0.2125',
               ratio_unit='ratio', research_value_usable=True,
               calculation_policy='decimal_localcontext_prec28_round_half_even_12dp_strip_trailing_zeros_fraction',
               derived_availability_date_proxy=filed,
               derived_availability_basis='max_input_filed_date_proxy_non_pit')
    operands = {}
    for role, value, concept in (('numerator', '1700', 'NetIncomeLoss'),
                                 ('denominator', '8000', 'RevenueFromContractWithCustomerExcludingAssessedTax')):
        operand = dict(metric_slot='annual_net_income' if role == 'numerator' else 'annual_revenue',
                       cell_status='single_exact_concept', cell_usable=True,
                       canonical_value=value, unit='USD', concept=concept, filed_date=filed,
                       source_row_identity='fictional-cell-' + role,
                       selection_group_id=digest(('invented-lantern-selection-' + role).encode('ascii')),
                       accession_number='0000999901-42-999001',
                       source_document_sha256=digest(('invented-lantern-document-' + role).encode('ascii')))
        operands[role] = operand
        row.update({role + '_' + k: value for k, value in operand.items()})
    address = dict(component_path='data/direct_tenq_ratios.json', component_sha256='0'*64,
                   grain=dict(grain), zero_based_row_index=0)
    versions = dict(formula_version='tenq_ratio_research.v1',
                    producer_profile_version='not_declared_in_source_artifact',
                    producer_schema_version='tenq_ratio_research_coverage.v1 (coverage metadata only; row schema not declared)')
    producer = dict(name='EquityForge research bundle builder', module='src.filing_observations.research_bundle',
                    version='research_bundle.v1',
                    git_commit=digest(b'invented-producer-commit')[:40],
                    git_tree=digest(b'invented-producer-tree')[:40])
    inherited = dict(component_file='data/direct_tenq_ratios.json', component_file_sha256='0'*64,
                     leaf='fictional-lantern-leaf', source_package_id='efsp1-' + digest(b'invented-lantern-input'),
                     manifest_txt_sha256=digest(b'invented-input-manifest-txt'),
                     manifest_sha256_file_sha256=digest(b'invented-input-checksum-ledger'))
    qualifications = [dict(code=code, severity='limitation', text=text) for code, text in (
        ('historical_filing_completeness_not_certified', 'Invented test dates do not establish filing completeness.'),
        ('sparse_direct_ocf', 'This invented one-ratio example contains no cash-flow observation.'))]
    quality = dict(bundle_id='efb1-' + digest(b'invented-lantern-bundle'), quality_id='fictional-lantern-quality',
                   schema_version='equityforge.research-bundle.data-quality.v1.0.0',
                   bundle_validation_state='pass', qualifications=qualifications)
    descriptor: dict = dict(bundle_id=quality['bundle_id'],
                      bundle_contract_version='equityforge.research-bundle.contract.v1.0.0',
                      profile=dict(profile_id='efp1-' + digest(b'invented-lantern-profile'), profile_contract_version='equityforge.research-bundle.profile.base.v1.0.0'),
                      producer=producer, analytical_qualifications=qualifications,
                      quality_document=dict(document_id=quality['quality_id'], relative_path='quality/data_quality.json', byte_size=0, file_sha256='0'*64),
                      components=[dict(stable_component_name='direct_tenq_ratios', component_id='efc1-' + digest(b'invented-lantern-ratio-component'),
                                       component_contract_version='equityforge.component.direct-tenq-ratios.v1.0.0', relative_path=address['component_path'],
                                       byte_size=0, file_sha256='0'*64, record_count=1, cell_count=1,
                                       source_package_identity=inherited, inherited_versions=versions)],
                      identity_core=dict(components=[dict(component_name='direct_tenq_ratios', record_count=1, cell_count=1)]))
    accepted_record: dict = {k: row[k] for k in ('blocking_reasons', 'calculation_policy', 'derivation_status',
        'derived_availability_basis', 'derived_availability_date_proxy', 'formula_version',
        'period_start', 'period_end', 'ratio_unit', 'ratio_value', 'research_value_usable')}
    accepted_record.update(source_row_identity=dict(address), inputs_and_provenance=operands,
                           value_convention='fraction_not_percent')
    # These acceptance coordinates are a fabricated interface witness only.
    accepted = dict(entity_key=cik, entity_name=name, candidate_record_count=1,
                    latest_usable=accepted_record, latest_attempted=dict(accepted_record))
    def temporal(value=None, authority=None):
        return dict(state='value' if value else 'unavailable', value=value,
                    precision='date' if value else None, authority=authority,
                    reason=None if value else 'No invented value supplied.')
    def measurement(available):
        return dict(state='available' if available else 'unavailable',
                    concept_or_indicator_id='net_margin' if available else None,
                    namespace='us-gaap' if available else None, unit='ratio' if available else None,
                    scale='1' if available else None, currency='USD' if available else None,
                    frequency='quarterly' if available else None,
                    seasonal_adjustment='not_applicable' if available else None,
                    nominal_real_status='not_applicable' if available else None,
                    formula_id='net_margin' if available else None,
                    formula_version='tenq_ratio_research.v1' if available else None,
                    source_period_class='duration' if available else None,
                    reason=None if available else 'No invented measurement supplied.')
    components = []
    for i, (slot, authority, domain, state, reasons) in enumerate((
        ('equity', 'equityforge', 'equity_financial_research', 'available', []),
        ('macro', 'macroforge', 'macroeconomic', 'unavailable', ['no_accepted_matching_artifact']),
        ('knowledge', 'knowledgeforge', 'sourced_knowledge', 'blocked', ['general_company_claim_export_not_authoritative']))):
        times = {k: temporal() for k in ('observation_time', 'period_start', 'period_end', 'filing_date',
            'acceptance_timestamp', 'publication_time', 'effective_time', 'retrieval_time', 'revision_vintage_time', 'component_build_time')}
        provenance = None
        if i == 0:
            times.update(period_start=temporal(start, 'producer_declared'), period_end=temporal(end, 'producer_declared'),
                         filing_date=temporal(filed, 'proxy'), effective_time=temporal(filed, 'proxy'))
            provenance = dict(source_record_ids=[], source_package_id=quality['bundle_id'],
                              source_package_manifest_txt_sha256='0'*64, source_package_manifest_sha256_file_sha256='0'*64,
                              source_artifact_relative_path=address['component_path'], source_artifact_byte_size=0,
                              source_artifact_sha256='0'*64, producer_id=authority, producer_version=producer['version'],
                              source_contract_id=descriptor['bundle_contract_version'], source_contract_version='1.0.0',
                              selection_method='producer_selected_no_composer_reselection', transformation_lineage=['Invented operands 1700 and 8000; exact fraction 0.2125; no accepted producer observation.'],
                              evidence_citation_ids=[], validation_profile_id=descriptor['profile']['profile_contract_version'], validation_result='pass')
        components.append(dict(component_id='rcc1-'+'0'*64, component_slot=slot, domain=domain, authority=authority,
                               producer_id=authority, component_envelope_version='research-context.component-envelope.v1.0.0',
                               state=state, usable=i==0, state_reason_codes=reasons, ambiguous_candidate_ids=[],
                               entity_ids=[entity] if i==0 else [], period_kind='duration' if i==0 else 'not_applicable',
                               time_identity=times, measurement_identity=measurement(i==0), provenance=provenance))
    findings = [dict(finding_id='rcf1-'+'0'*64, left_slot=left, right_slot=right, status='blocked',
                     entity_predicate='No cross-domain fictional entity mapping.',
                     temporal_predicate='No cross-domain fictional time match.',
                     measurement_predicate='No cross-domain fictional measurement match.',
                     authorized_join=False, reason_codes=['component_not_available'])
                for left, right in (('equity','macro'), ('equity','knowledge'), ('macro','knowledge'))]
    context: dict = dict(contract_id='research_context.v1', contract_version='research-context.contract.v1.0.0',
                   canonicalization_policy='research-context.canonical-json.v1.0.0', hash_policy='research-context.sha256.v1.0.0',
                   profile_id='research-context.profile.base.v1.0.0', context_id='rcv1-'+'0'*64,
                   composer=dict(producer_id='research-context.reference-composer', producer_version='research-context.reference-composer.v1.0.0'),
                   context_package_build_time='2042-05-10T00:00:00Z', components=components,
                   compatibility_findings=findings, package_status='partial',
                   entity_mappings=[dict(entity_id=entity, entity_kind='issuer', mapping_status='resolved',
                       mapping_method='invented_test_identity', mapping_evidence_ids=[], effective_interval=dict(start=temporal(), end=temporal()),
                       identifiers=dict(cik=dict(state='value', value=cik, authority='invented_test_identity', reason=None),
                           lei=dict(state='unavailable', value=None, authority=None, reason='Fictional issuer has no LEI.'),
                           tickers=[], countries=[], producer_native_ids=[],
                           aliases=[dict(alias=name, alias_type='display_name', authority='invented_test_identity',
                                         effective_interval=dict(start=temporal(),end=temporal()), status='resolved')]))])
    payload: dict = dict(record_id='rcpr1-'+'0'*64, context_id=context['context_id'], component_id=components[0]['component_id'],
                   entity_id=entity, source_address=address, source_record=row,
                   source_component_id=descriptor['components'][0]['component_id'], source_bundle_id=quality['bundle_id'],
                   source_package_identity=inherited, inherited_versions=versions, producer=producer,
                   measurement=dict(duration_class='first_quarter', formula_id='net_margin', formula_version='tenq_ratio_research.v1',
                       frequency='quarterly', input_currency='USD', input_scale='1', kind='equityforge_calculated_ratio',
                       nominal_real_status='not_applicable', scale='1', seasonal_adjustment='not_applicable', taxonomy='us-gaap',
                       unit='ratio', value_convention='fraction_not_percent', view='net_margin'),
                   availability=dict(date=filed, basis='max_input_filed_date_proxy_non_pit', accepted_at=None, pit_certified=False,
                                     publication_time=None,retrieval_time=None,revision_vintage_time=None),
                   qualification_codes=[x['code'] for x in qualifications],
                   selection=dict(policy='accepted_source_bound_record_no_reselection', accepted_result_key='fictional_net_margin',
                                  accepted_result_index=0, accepted_record_field='latest_usable', context_record_alias=''),
                   authority_mode='complete_semantic_record_with_byte_exact_container_witness', producer_record_hash=None,
                   rights='local_evidence_review_only_no_redistribution_grant')
    companion: dict = dict(contract_id='research_context.composed_payload.v1', contract_version='research-context.composed-payload.contract.v1.0.0',
                     profile_id='research-context.composed-payload.profile.single-net-margin-partial.v1.0.0', companion_id='rcpc1-'+'0'*64,
                     composer=dict(producer_id='research-context.reference-composer', producer_version='research-context.composed-payload-composer.v1.0.0'),
                     package_status='partial', purpose='contract_fixture_not_production', package_build_time='2042-05-10T00:00:00Z',
                     context_binding=dict(context_id=context['context_id'], manifest_txt_sha256='0'*64, manifest_sha256_file_sha256='0'*64,
                                          contract_version=context['contract_version'], profile_id=context['profile_id'], relative_path='context'),
                     components=[dict(slot=x['component_slot'], component_id=x['component_id'], state=x['state'], reason_codes=x['state_reason_codes'],
                                      payload=dict(path='payloads/equity.json', bytes=0, sha256='0'*64, media_type='application/json') if i==0 else None)
                                 for i,x in enumerate(components)], compatibility_findings=findings,
                     source_binding=dict(bundle_id=quality['bundle_id'], manifest_txt_sha256='0'*64, manifest_sha256_file_sha256='0'*64,
                         component_id=payload['source_component_id'], component_sha256='0'*64, component_bytes=0,
                         component_path=address['component_path'], source_address=address,
                         acceptance_manifest_txt_sha256='0'*64, acceptance_manifest_sha256_file_sha256='0'*64),
                     record_id=payload['record_id'], selection_policy='accepted_source_bound_record_no_reselection',
                     canonicalization_policy='research-context.composed-payload.canonical-json.v1.0.0', hash_policy='sha256-lowercase-hex',
                     projection_version='research-context.complete-semantic-ratio-record.v1.0.0', resource_hashes={})
    return dict(accepted=accepted, companion=companion, context=context, descriptor=descriptor,
                payload=payload, quality=quality, row=row)


def fixture(directory, *, bundle_witness_mutation=None):
    """One-row synthetic witness, with independent pins derived before admission."""
    t = authored_example()
    d, c, p, descriptor, quality, row, accepted = (t[k] for k in ('companion','context','payload','descriptor','quality','row','accepted'))
    files = {}
    resource = {k: (_ROOT / rel).read_bytes() for k, rel in _RESOURCE_REL.items()}
    d['resource_hashes'] = {'companion_schema_sha256': digest(resource['companion_schema']),
                            'equity_schema_sha256': digest(resource['equity_schema'])}
    files['schemas/companion.schema.json'] = resource['companion_schema']
    files['schemas/equity-observation.schema.json'] = resource['equity_schema']
    files['context/registry/producer_registry.json'] = resource['context_registry']
    files['context/schemas/producer_registry.schema.json'] = resource['context_registry_schema']
    files['context/schemas/research_context.schema.json'] = resource['context_schema']
    source_bytes = canonical([row]) + b'\n'
    files['proof/producer-component.json'] = source_bytes
    src_digest = digest(source_bytes)
    address = p['source_address']
    address['component_sha256'] = src_digest
    address['zero_based_row_index'] = 0
    d['source_binding']['source_address'] = address
    d['source_binding']['component_sha256'] = src_digest
    d['source_binding']['component_bytes'] = len(source_bytes)
    p['source_package_identity']['component_file_sha256'] = src_digest
    p['selection']['context_record_alias'] = f'ef-address:{src_digest}:row:0'
    accepted['latest_usable']['source_row_identity'] = address
    accepted['latest_attempted']['source_row_identity'] = address
    descriptor['components'] = [x for x in descriptor['components'] if x['stable_component_name'] == 'direct_tenq_ratios']
    source_component = descriptor['components'][0]
    source_component.update(byte_size=len(source_bytes), file_sha256=src_digest, record_count=1, cell_count=1, source_package_identity=p['source_package_identity'])
    descriptor['identity_core']['components'] = [x for x in descriptor['identity_core']['components'] if x['component_name'] == 'direct_tenq_ratios']
    descriptor['identity_core']['components'][0].update(record_count=1, cell_count=1)
    files['proof/bundle-quality.json'] = canonical(quality)+b'\n'
    descriptor['quality_document'].update(byte_size=len(files['proof/bundle-quality.json']),file_sha256=digest(files['proof/bundle-quality.json']))
    files['proof/bundle-descriptor.json'] = canonical(descriptor)+b'\n'
    accepted['candidate_record_count'] = 1
    files['proof/acceptance-results.json'] = canonical({p['selection']['accepted_result_key']:{'results':[accepted]}})+b'\n'
    def proof_manifest(stem, source):
        txt = ''.join(f'{original}\t{len(files[local])}\t{digest(files[local])}\n' for original,local in sorted(source.items())).encode()
        sha = ''.join(f'{digest(txt) if n == "MANIFEST.txt" else digest(files[source[n]])}  {n}\n' for n in sorted([*source, 'MANIFEST.txt'])).encode()
        if stem == 'bundle' and bundle_witness_mutation is not None:
            txt, sha = bundle_witness_mutation(txt, sha)
        files[f'proof/{stem}-manifest.txt'] = txt
        files[f'proof/{stem}-manifest.sha256'] = sha
        return v.ManifestPins(pin(txt),pin(sha))
    source_man = proof_manifest('bundle',{'BUNDLE.json':'proof/bundle-descriptor.json','data/direct_tenq_ratios.json':'proof/producer-component.json','quality/data_quality.json':'proof/bundle-quality.json'})
    acceptance_man = proof_manifest('acceptance',{'PUBLIC_CONSUMER_RESULTS.json':'proof/acceptance-results.json'})
    d['source_binding'].update(manifest_txt_sha256=source_man.manifest_txt.sha256,manifest_sha256_file_sha256=source_man.manifest_sha256.sha256,acceptance_manifest_txt_sha256=acceptance_man.manifest_txt.sha256,acceptance_manifest_sha256_file_sha256=acceptance_man.manifest_sha256.sha256)
    e = c['components'][0]
    e['provenance'].update(source_artifact_byte_size=len(source_bytes),source_artifact_sha256=src_digest,source_package_manifest_txt_sha256=source_man.manifest_txt.sha256,source_package_manifest_sha256_file_sha256=source_man.manifest_sha256.sha256,source_record_ids=[p['selection']['context_record_alias']])
    c['entity_mappings'][0]['mapping_evidence_ids']=[p['selection']['context_record_alias']]
    for component in c['components']:
        component['component_id'] = record(component,'component_id','rcc1-')
    for finding in c['compatibility_findings']:
        finding['finding_id'] = record(finding,'finding_id','rcf1-')
    c['context_id'] = record(c,'context_id','rcv1-','context_package_build_time')
    e=c['components'][0]
    p.update(context_id=c['context_id'],component_id=e['component_id'])
    p['record_id'] = record(p,'record_id','rcpr1-')
    files['context/RESEARCH_CONTEXT.json']=canonical(c)+b'\n'
    ledgers(files,'context/')
    d['context_binding'].update(context_id=c['context_id'],manifest_txt_sha256=digest(files['context/MANIFEST.txt']),manifest_sha256_file_sha256=digest(files['context/MANIFEST.sha256']))
    d['record_id']=p['record_id']
    d['components'][0]['component_id']=e['component_id']
    d['components'][0]['payload'].update(bytes=0,sha256='0'*64)
    d['components'][1]['component_id']=c['components'][1]['component_id']
    d['components'][2]['component_id']=c['components'][2]['component_id']
    d['compatibility_findings']=c['compatibility_findings']
    files['payloads/equity.json']=canonical(p)+b'\n'
    d['components'][0]['payload'].update(bytes=len(files['payloads/equity.json']),sha256=digest(files['payloads/equity.json']))
    d['companion_id']=record(d,'companion_id','rcpc1-','package_build_time')
    files['COMPOSED_PAYLOAD.json']=canonical(d)+b'\n'
    ledgers(files)
    for name, raw in files.items():
        path=directory/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    resources=v.ResourcePins(**{k:pin(raw) for k,raw in resource.items()})
    context=v.ContextPins(c['context_id'],e['component_id'],p['entity_id'],c['contract_version'],c['profile_id'],pin(files['context/RESEARCH_CONTEXT.json']),v.ManifestPins(pin(files['context/MANIFEST.txt']),pin(files['context/MANIFEST.sha256'])))
    source=v.SourcePins(descriptor['bundle_id'],descriptor['bundle_contract_version'],descriptor['profile']['profile_id'],descriptor['profile']['profile_contract_version'],source_component['component_id'],source_component['component_contract_version'],source_component['relative_path'],pin(source_bytes),pin(files['proof/bundle-descriptor.json']),pin(files['proof/bundle-quality.json']),source_man,v.ProducerPins(**p['producer']),v.InheritedSourcePins(**p['source_package_identity']),v.InheritedVersionPins(**p['inherited_versions']))
    address_pin=v.SourceAddress(address['component_path'],address['component_sha256'],0,v.SourceGrain(**address['grain']))
    acceptance=v.AcceptancePins(pin(files['proof/acceptance-results.json']),acceptance_man,p['selection']['accepted_result_key'],0)
    trust=v.ConsumerTrustPins(d['contract_version'],d['profile_id'],context,source,acceptance,address_pin,resources)
    receipt=v.CompanionPins(d['companion_id'],p['record_id'],v.ManifestPins(pin(files['MANIFEST.txt']),pin(files['MANIFEST.sha256'])))
    return v.ComposedPackageRequest(directory,trust,receipt), files


class ValidationContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'package';self.root.mkdir()
        self.request,self.files=fixture(self.root)

    def reject(self, code, request=None):
        with self.assertRaises(v.ComposedPackageError) as error:
            v.validate_research_context_composed_payload(request or self.request)
        self.assertEqual(error.exception.code,code)
        self.assertNotIn(str(self.root),error.exception.detail)
        return error.exception

    def bundle_witness(self, mutation):
        self.request, self.files = fixture(self.root, bundle_witness_mutation=mutation)
        self.assertEqual(pin(self.files['proof/bundle-manifest.txt']), self.request.trust.source.manifests.manifest_txt)
        self.assertEqual(pin(self.files['proof/bundle-manifest.sha256']), self.request.trust.source.manifests.manifest_sha256)

    def test_bundle_checksum_ledger_accepts_manifest_last(self):
        self.bundle_witness(self.manifest_last)
        self.assertEqual(v.validate_research_context_composed_payload(self.request).identity,
                         self.request.expected_identity)

    @staticmethod
    def manifest_last(txt, sha):
        rows = sha.splitlines(keepends=True)
        manifest = [row for row in rows if row.endswith(b'  MANIFEST.txt\n')]
        assert len(manifest) == 1
        return txt, b''.join([*(row for row in rows if row != manifest[0]), manifest[0]])

    def test_bundle_checksum_ledger_rejects_misplaced_payload_entry(self):
        def misplaced(txt, sha):
            _, ordered = self.manifest_last(txt, sha)
            payload = ordered.splitlines(keepends=True)
            payload[0], payload[1] = payload[1], payload[0]
            return txt, b''.join(payload)
        self.bundle_witness(misplaced)
        self.assertEqual(self.reject('SOURCE_PACKAGE_MISMATCH').detail, 'source witness ordering invalid')

    def test_bundle_checksum_ledger_rejects_duplicate_entry(self):
        def duplicate(txt, sha):
            _, ordered = self.manifest_last(txt, sha)
            rows = ordered.splitlines(keepends=True)
            return txt, b''.join([*rows[:-1], rows[0], rows[-1]])
        self.bundle_witness(duplicate)
        self.assertEqual(self.reject('SOURCE_PACKAGE_MISMATCH').detail, 'source witness member invalid')

    def test_bundle_checksum_ledger_rejects_missing_entry(self):
        def missing(txt, sha):
            _, ordered = self.manifest_last(txt, sha)
            rows = ordered.splitlines(keepends=True)
            return txt, b''.join([*rows[1:]])
        self.bundle_witness(missing)
        self.assertEqual(self.reject('SOURCE_PACKAGE_MISMATCH').detail, 'source witness ledger mismatch')

    def test_bundle_checksum_ledger_rejects_wrong_member_hash(self):
        def wrong_member(txt, sha):
            _, sha = self.manifest_last(txt, sha)
            row = next(line for line in txt.splitlines() if line.startswith(b'data/direct_tenq_ratios.json\t'))
            original = row.rsplit(b'\t', 1)[1]
            altered_txt = txt.replace(original, b'0'*64, 1)
            altered_sha = sha.replace(original+b'  data/direct_tenq_ratios.json',
                                      b'0'*64+b'  data/direct_tenq_ratios.json', 1)
            altered_sha = altered_sha.replace(digest(txt).encode()+b'  MANIFEST.txt',
                                              digest(altered_txt).encode()+b'  MANIFEST.txt', 1)
            return altered_txt, altered_sha
        self.bundle_witness(wrong_member)
        error = self.reject('SOURCE_COMPONENT_MISMATCH')
        self.assertEqual(error.detail, 'source witness member differs')
        self.assertEqual(error.relative_path, 'proof/producer-component.json')

    def test_bundle_checksum_ledger_rejects_wrong_manifest_hash(self):
        def wrong_manifest(txt, sha):
            _, sha = self.manifest_last(txt, sha)
            rows = sha.splitlines(keepends=True)
            rows[-1] = b'0'*64+b'  MANIFEST.txt\n'
            return txt, b''.join(rows)
        self.bundle_witness(wrong_manifest)
        self.assertEqual(self.reject('SOURCE_PACKAGE_MISMATCH').detail, 'source witness ledger mismatch')

    def test_exact_native_admission_and_states(self):
        x=v.validate_research_context_composed_payload(self.request)
        self.assertEqual(x.identity,self.request.expected_identity)
        self.assertEqual(x.status,'partial')
        self.assertEqual(x.component_states,(('equity','available'),('macro','unavailable'),('knowledge','blocked')))
        self.assertEqual(x.regular_file_count,20)
        self.assertEqual(x.equity_payload_json,self.files['payloads/equity.json'])

    def test_wrong_request_type_before_io(self):
        self.reject('TRUST_INPUT_INVALID',object())

    def test_missing_explicit_absolute_path(self):
        self.reject('INPUT_PATH_INVALID',dataclasses.replace(self.request,package_dir=Path('relative')))

    def test_unsupported_caller_profile_precedes_path(self):
        t=dataclasses.replace(self.request.trust,profile_id='unknown')
        self.reject('UNSUPPORTED_PROFILE',dataclasses.replace(self.request,trust=t,package_dir=Path('relative')))

    def test_extra_file_is_rejected(self):
        (self.root/'extra.txt').write_text('x')
        self.reject('UNDECLARED_FILE')

    def test_missing_file_is_rejected(self):
        (self.root/'payloads/equity.json').unlink()
        self.reject('MISSING_FILE')

    def test_symlink_member_is_rejected_without_following(self):
        x=self.root/'payloads/equity.json';x.unlink();x.symlink_to('/etc/passwd')
        self.reject('SYMLINK_FORBIDDEN')

    def test_hardlink_member_is_rejected(self):
        os.link(self.root/'payloads/equity.json',self.root/'payloads/alias')
        self.reject('HARDLINK_FORBIDDEN')

    def test_case_collision_is_rejected(self):
        (self.root/'composed_payload.json').write_bytes(b'hi')
        self.reject('CASE_COLLISION')

    def test_member_tamper_precedes_json(self):
        (self.root/'payloads/equity.json').write_bytes(b'{}\n')
        self.reject('SIZE_MISMATCH')

    def test_manifest_tamper_is_rejected(self):
        (self.root/'MANIFEST.txt').write_bytes(b'bad\n')
        self.reject('MANIFEST_FORMAT')

    def test_caller_receipt_mismatch_after_manifests(self):
        bad=v.FilePin(1,'a'*64)
        identity=dataclasses.replace(self.request.expected_identity,manifests=dataclasses.replace(self.request.expected_identity.manifests,manifest_sha256=bad))
        self.reject('COMPANION_TRUST_MISMATCH',dataclasses.replace(self.request,expected_identity=identity))

    def test_resource_pin_mismatch(self):
        altered=dataclasses.replace(self.request.trust.resources,equity_schema=v.FilePin(1,'a'*64))
        self.reject('RESOURCE_HASH_MISMATCH',dataclasses.replace(self.request,trust=dataclasses.replace(self.request.trust,resources=altered)))

    def test_validation_has_no_network_provider_or_foreign_forge_dependency(self):
        import ast
        tree=ast.parse((_ROOT/'src/briefforge/research_context_composed_payload_validation.py').read_text())
        names=[x.module or '' for x in ast.walk(tree) if isinstance(x,ast.ImportFrom)]
        names += [a.name for x in ast.walk(tree) if isinstance(x,ast.Import) for a in x.names]
        self.assertFalse(any(n.lower().startswith(('equityforge','macroforge','knowledgeforge','src.research_context','requests','urllib','http','socket','sqlite3')) for n in names))


if __name__=='__main__':unittest.main()
