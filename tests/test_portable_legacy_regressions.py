"""Artifact-independent legacy proofs; no recorded reports are opened."""
import dataclasses
import hashlib
import json
import unittest
from tests import portable_gate_support as s


def ordinary_candidate(count=3, meanings=None):
    from briefforge.runtime import CandidatePresentationPackage,PackageIdentity,OrganizingPurpose,PresentationStatement,EncounterSemantics,UpstreamReference,PresentationObligation
    purpose='Present explicitly synthetic evidence with ownership and caveats.'
    return CandidatePresentationPackage(PackageIdentity('portable-synthetic','Synthetic report','Bounded regression','Synthetic evidence','No empirical authority'),OrganizingPurpose(purpose,'Synthetic material','No forecasts'),tuple(PresentationStatement('statement-'+str(i),(meanings[i] if meanings else 'Synthetic observation '+str(i)),purpose,EncounterSemantics('evidence','Read synthetic evidence in order',('statement-'+str(i-1),) if i else ()),('reference-'+str(i%3),),('obligation-'+str(i%3),)) for i in range(count)),tuple(UpstreamReference('reference-'+str(i),'Synthetic source','source-statistic','synthetic:'+str(i),'Synthetic source owns the observations.') for i in range(3)),tuple(PresentationObligation('obligation-'+str(i),'scope-control','Synthetic only; preserve caveat '+str(i),tuple('statement-'+str(j) for j in range(count) if j%3==i)) for i in range(3)))


def lifecycle(test,candidate):
    from briefforge.validation import validate_candidate_presentation_package
    from briefforge.promotion import promote_candidate_presentation_package
    from briefforge.renderer_adapter import render_minimal_html,html_renderer_contract,check_rendered_artifact_conformance
    from briefforge.runtime import semantic_fingerprint
    digest=semantic_fingerprint(candidate);judgment=validate_candidate_presentation_package(candidate);test.assertTrue(judgment.valid,judgment.findings)
    ready=promote_candidate_presentation_package(candidate,judgment);artifact=render_minimal_html(ready,html_renderer_contract());conformance=check_rendered_artifact_conformance(ready,artifact)
    test.assertTrue(conformance.conforms,conformance.findings);test.assertEqual(digest,ready.semantic_fingerprint);test.assertEqual(digest,artifact.semantic_fingerprint);test.assertEqual(digest,semantic_fingerprint(candidate))
    order=[attrs['data-statement-id'] for tag,attrs in s.parsed_html(artifact.html).elements if 'data-statement-id' in attrs]
    test.assertEqual(order,[x.statement_id for x in candidate.statements]);return artifact


class PortableLegacyRegressionTests(unittest.TestCase):
    def test_country_profile_migration_preserves_fingerprint(self):
        from briefforge.presentation_models import CountryProfileBuilder
        from briefforge.runtime import semantic_fingerprint
        original=ordinary_candidate();country='Synthetic Republic'
        original=dataclasses.replace(original,statements=tuple(dataclasses.replace(x,belongs_to_purpose=country+' country-profile organizing purpose') for x in original.statements))
        builder=CountryProfileBuilder(country_name=country).identity(**dataclasses.asdict(original.identity)).organizing_purpose(**dataclasses.asdict(original.organizing_purpose))
        for ref in original.upstream_references:builder.reference(**dataclasses.asdict(ref))
        for ob in original.obligations:builder.obligation(obligation_id=ob.obligation_id,category=ob.category,requirement=ob.requirement,applies_to=ob.applies_to)
        for st in original.statements:builder.section(statement_id=st.statement_id,section_kind='synthetic',encounter_meaning=st.encounter_meaning,encounter_mode=st.encounter_semantics.mode,encounter_description=st.encounter_semantics.description,related_statement_ids=st.encounter_semantics.related_statement_ids,upstream_reference_ids=st.upstream_reference_ids,obligation_ids=st.obligation_ids)
        migrated=builder.build().to_candidate_presentation_package();self.assertEqual(migrated,original)
        independent=hashlib.sha256(json.dumps(dataclasses.asdict(original),sort_keys=True,separators=(',',':')).encode()).hexdigest()
        self.assertEqual(semantic_fingerprint(migrated),independent);lifecycle(self,migrated)

    def test_large_report_structure_semantics_and_conformance(self):
        from briefforge.builder import PresentationPackageBuilder
        meanings=tuple('Synthetic analytical section '+str(i)+'\n\n## Evidence\n### Details\n- Parent item\n  - Nested detail\n\nCaveat: synthetic only.\nMethodology: explicit construction.\nRecommendation: preserve limits.\n\n| Kind | Evidence |\n| --- | --- |\n| Qualitative | Synthetic |\n\n'+('Bounded qualitative evidence and explicit source attribution. '*40) for i in range(36))
        spec=ordinary_candidate(36,meanings);builder=PresentationPackageBuilder().identity(**dataclasses.asdict(spec.identity)).organizing_purpose(**dataclasses.asdict(spec.organizing_purpose))
        for ref in spec.upstream_references:builder.add_upstream_reference(**dataclasses.asdict(ref))
        for ob in spec.obligations:builder.add_obligation(obligation_id=ob.obligation_id,category=ob.category,requirement=ob.requirement,applies_to=ob.applies_to)
        for st in spec.statements:builder.add_statement(statement_id=st.statement_id,encounter_meaning=st.encounter_meaning,belongs_to_purpose=st.belongs_to_purpose,encounter_mode=st.encounter_semantics.mode,encounter_description=st.encounter_semantics.description,related_statement_ids=st.encounter_semantics.related_statement_ids,upstream_reference_ids=st.upstream_reference_ids,obligation_ids=st.obligation_ids)
        candidate=builder.build();self.assertEqual(candidate,spec);self.assertGreater(sum(len(x.encounter_meaning) for x in candidate.statements),20000)
        before=dataclasses.asdict(candidate);artifact=lifecycle(self,candidate);self.assertEqual(before,dataclasses.asdict(candidate))
        self.assertEqual(len(candidate.statements),36);self.assertEqual(len(candidate.upstream_references),3);self.assertEqual(len(candidate.obligations),3)
        self.assertNotIn('<svg',artifact.html);self.assertIn('<table',artifact.html);self.assertIn('<ul',artifact.html);self.assertIn('Nested detail',artifact.html)
        for value in ('Caveat: synthetic only.','Methodology: explicit construction.','Recommendation: preserve limits.'):self.assertIn(value,artifact.html)
        for st in candidate.statements:self.assertIn(st.encounter_meaning.split('\n')[0],artifact.html)
        for ref in candidate.upstream_references:self.assertIn(ref.locator,artifact.html)
        for ob in candidate.obligations:self.assertIn(ob.requirement,artifact.html)

    def test_bounded_exhibits_and_no_fabricated_data(self):
        table='Synthetic comparison evidence\n\nSource: synthetic producer\n\n| Country | GDP | Unit |\n| --- | --- | --- |\n| Alpha | 10 | USD |\n| Beta | 20 | USD |\n| Gamma | 30 | USD |'
        candidate=ordinary_candidate(3,(table,'Synthetic nonnumeric commentary','Synthetic interpretation boundary'));artifact=lifecycle(self,candidate);document=s.parsed_html(artifact.html)
        exhibits=[attrs for tag,attrs in document.elements if 'data-exhibit-type' in attrs]
        self.assertTrue(exhibits);self.assertTrue(all(e.get('data-exhibit-source-statement')=='statement-0' for e in exhibits))
        self.assertTrue(all(e['data-exhibit-type'] in ('key-number','small-statistical-table','comparison-table') for e in exhibits))
        self.assertFalse(any(tag in ('svg','canvas','script','iframe') or any(k.startswith('on') for k in attrs) for tag,attrs in document.elements))
        for value in ('Alpha','Beta','Gamma','10','20','30','USD'):self.assertIn(value,''.join(document.text))
        plain=lifecycle(self,ordinary_candidate());plain_doc=s.parsed_html(plain.html)
        self.assertFalse(any('data-renderer-exhibit' in attrs or 'data-exhibit-type' in attrs for tag,attrs in plain_doc.elements))
        self.assertIn('data-exhibit-region="none-detected"',plain.html)

    def test_svg_preserves_values_units_and_no_javascript(self):
        periods=('2024-M01','2024-M02','2024-M03','2024-M04');values=('1','3','2','4')
        table='Synthetic monthly values\n\nSource: synthetic producer\nFrequency: monthly\n\n| Period | Value | Unit |\n| --- | --- | --- |\n'+'\n'.join('| '+p+' | '+v+' | ratio |' for p,v in zip(periods,values))
        candidate=ordinary_candidate(3,(table,'Synthetic caveat','Synthetic close'));artifact=lifecycle(self,candidate);doc=s.parsed_html(artifact.html)
        self.assertEqual(sum(tag=='svg' for tag,attrs in doc.elements),1);self.assertEqual(sum(tag=='circle' for tag,attrs in doc.elements),4)
        polyline=next(attrs['points'] for tag,attrs in doc.elements if tag=='polyline')
        self.assertEqual(polyline,'54.0,216.0 241.3,88.0 428.7,152.0 616.0,24.0')
        for p,v in zip(periods,values):self.assertIn(p+': '+str(float(v))+' ratio',''.join(doc.text))
        self.assertFalse(any(tag in ('script','canvas') or any(k.startswith('on') for k in attrs) for tag,attrs in doc.elements))
        self.assertNotIn('ChartSpec',artifact.html)
        self.assertNotIn('<svg',lifecycle(self,ordinary_candidate()).html)

    def test_interactive_navigation_with_explicit_synthetic_data(self):
        from briefforge.interactive_report_configs import norway_config
        from briefforge.interactive_report_foundation import render_report
        selected=[];raw=[]
        for code,name,value,n in [('SP.DYN.LE00.IN','Synthetic life expectancy','-0.207863151096',34),('EG.ELC.RNWX.ZS','Synthetic renewable','0.3855860099',31),('EG.ELC.FOSL.ZS','Synthetic fossil','-0.083376899169',33)]:
            selected.append(dict(series_a_code=code,series_a_name=name,series_b_name='Synthetic target',coefficient=value,aligned_observation_count=n,aligned_period_start=1991,aligned_period_end=1990+n,transformation_id='synthetic-first-difference',method_id='synthetic-pearson',package_id='synthetic:'+code));raw.append(dict(series_a_code=code,coefficient='0.75'))
        data=dict(selected_correlates=selected,raw_level_context_not_primary=raw,analytical_review={k:'Synthetic bounded interpretation' for k in ('numerical_comparison','confidence','interpretation','material_counterevidence','discrimination_limit','admitted_evidence')},methodology={k:'Synthetic methodology boundary' for k in ('correlation_vs_causation','multiple_comparison_risk','correlation_source','ranking_comparability','common_trends_spurious_correlation','primary_transformation','correlation_method','annual_alignment_and_lag_semantics','pooled_vs_country_specific','minimum_overlap','cross_sectional_vs_time_series','zero_negative_missing_behavior','outlier_sensitivity')},results={'report_thesis':'Synthetic descriptive association'},selection_procedure={k:'Synthetic disclosed selection' for k in ('candidate_universe','ranking_basis','superlative_boundary','selection_timing')},target_indicator_definition={'growth_semantics':'First differences, not growth'},handoff_boundary={k:'Synthetic ownership' for k in ('consumer_contract','locator_rule','analytical_owner','presentation_owner')},limitations=['Synthetic limitation'],precise_analytical_question='Synthetic question',task_type='synthetic',selection_rationale='Synthetic selection',package_id='synthetic-norway',artifact_status='synthetic-not-authority',content_sha256='a'*64,provenance_references=['synthetic:source'])
        data['analytical_review'].update(unsupported_speculation_excluded=['No causal inference'],plausible_alternatives=['Common trends'])
        config=norway_config(data,'synthetic:input');html=render_report(config)
        self.assertEqual([c['id'] for c in config['controls']],['theme']);self.assertEqual(len(config['divisions']),4)
        charts=[c for d in config['divisions'] for p in d['pages'] for c in p.get('charts',[])]
        self.assertEqual(sum(c['kind']=='evidence-table' for c in charts),1)
        coefficient=next(c for c in charts if c['kind']=='coefficient');self.assertEqual([x['exact'] for x in coefficient['data']],[x['coefficient'] for x in selected])
        dumbbell=next(c for c in charts if c['kind']=='dumbbell');self.assertEqual(dumbbell['series'],['Raw level','First difference'])
        for st in selected:
            for key in ('coefficient','transformation_id','method_id','package_id'):self.assertIn(st[key],html)
        self.assertIn('Correlation ≠ causation',html);self.assertIn('No causal inference',html);self.assertIn('synthetic-not-authority',html)
        self.assertEqual(html.count('"kind":"evidence-table"'),1)
        self.assertEqual(render_report(config),html)
        for hook in ('pageSubs','mobile-subnav','focusTarget','restoreFocus','scrollTarget','window.scrollTo(0,0)','menu.focus()','.source-note{overflow-wrap:anywhere}'):
            self.assertIn(hook,html)
        self.assertIn('a'*64,html);self.assertNotIn('http://',html);self.assertNotIn('https://',html)
        pages=[p for d in config['divisions'] for p in d['pages']];self.assertTrue(any('subsections' not in p for p in pages));self.assertTrue(any(p.get('subsections') for p in pages))

    def test_communication_intent_static_hierarchy(self):
        from briefforge.validation import validate_candidate_presentation_package
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.communication_intent_renderer_experiment import render_communication_intent_html
        from briefforge.renderer_adapter import render_minimal_html
        from briefforge.communication_intent_experiment import derive_communication_intent_profile as derive_communication_intent
        # Explicit language triggers each frozen reading-flow intent. A generic
        # all-caveat fixture legitimately omits explain/conclude sections.
        triggers=('Introduce synthetic scope','Summary of synthetic material','Explain synthetic evidence','Uncertainty and caveats','Close with synthetic synthesis')
        candidate=ordinary_candidate(30,tuple(triggers[i%5]+' '+str(i)+'\n\n'+('Synthetic descriptive material only. '*30) for i in range(30)))
        ready=promote_candidate_presentation_package(candidate,validate_candidate_presentation_package(candidate));intent=derive_communication_intent(ready)
        current=render_minimal_html(ready);experimental=render_communication_intent_html(ready)
        self.assertEqual(experimental.semantic_fingerprint,ready.semantic_fingerprint);self.assertEqual(current.semantic_fingerprint,ready.semantic_fingerprint);self.assertNotEqual(current.adapter_identity.adapter_id,experimental.adapter_identity.adapter_id)
        labels=('Executive capsule','Claim-evidence-implication flow','Uncertainty and risk','Evidence register','Methodology and obligations','Bounded synthesis')
        positions=[experimental.html.index(x) for x in labels];self.assertEqual(positions,sorted(positions))
        self.assertEqual([x.primary_intent for x in intent.statement_intents],['orient','summarize','explain','qualify','conclude']*6)
        for statement in candidate.statements:self.assertIn(statement.encounter_meaning.split('\n')[0],experimental.html)
        for mode in ('orient','explain','qualify','trace','conclude'):self.assertIn('data-intent="'+mode+'"',experimental.html)
        self.assertFalse(any(tag in ('script','canvas','svg') for tag,attrs in s.parsed_html(experimental.html).elements))
        self.assertEqual(derive_communication_intent(ready),intent);self.assertEqual(render_communication_intent_html(ready),experimental)

    def test_missing_legacy_lifecycle_times_fail_closed(self):
        from tests.test_bcrp_lifecycle_authority_compatibility import LegacyCompatibilityContractTests
        from briefforge.bcrp_legacy_compatibility import map_legacy_ready_to_bcrp,CompatibilityRejected
        helper=LegacyCompatibilityContractTests();candidate,judgment,ready=helper._legacy_closure();bcrp=helper._bcrp_candidate();mapping=helper._mapping(candidate,bcrp)
        valid=map_legacy_ready_to_bcrp(legacy_candidate=candidate,legacy_judgment=judgment,legacy_ready=ready,bcrp_candidate_bundle=bcrp,mapping=mapping);self.assertEqual(len(valid.records_of_kind('ReadyPresentationPackageRecord')),1)
        for field in ('validation_time','readiness_time','mapping_attestation_time'):
            with self.subTest(missing=field):
                incomplete=dataclasses.replace(mapping,evidence=dataclasses.replace(mapping.evidence,**{field:''}))
                with self.assertRaises(CompatibilityRejected):map_legacy_ready_to_bcrp(legacy_candidate=candidate,legacy_judgment=judgment,legacy_ready=ready,bcrp_candidate_bundle=bcrp,mapping=incomplete)
