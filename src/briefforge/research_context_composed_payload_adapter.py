"""Deterministic presentation-only projection of an admitted composed package."""
from dataclasses import dataclass
from decimal import Decimal, localcontext
import json

from .runtime import (CandidatePresentationPackage, EncounterSemantics,
                      OrganizingPurpose, PackageIdentity, PresentationObligation,
                      PresentationStatement, UpstreamReference)
from .validation import validate_candidate_presentation_package
from .research_context_composed_payload_validation import (
    CompanionPins, ComposedPackageError, ComposedPackageRequest, _PublicSignature,
    validate_research_context_composed_payload,
)

ADAPTER_VERSION = 'briefforge.research-context-composed-payload-adapter.v1.0.0'


@dataclass(frozen=True, slots=True)
class ComposedAdapterResult:
    candidate: CandidatePresentationPackage
    accepted_identity: CompanionPins
    context_id: str
    source_record_json: bytes
    adapter_version: str


def adapt_research_context_composed_payload(request: ComposedPackageRequest, /) -> ComposedAdapterResult:
    """Return one native semantic Candidate; never render, select or publish."""
    validated = validate_research_context_composed_payload(request)
    payload = json.loads(validated.equity_payload_json)
    row = payload['source_record']
    raw = row['ratio_value']
    # A label only. The source fraction and source-record bytes remain unmodified.
    with localcontext() as context:
        context.prec = max(64, len(raw) + 8)
        percent = format((Decimal(raw) * Decimal(100)).normalize(), 'f') + '%'
    address = payload['source_address']
    source = request.trust.source
    selection = payload['selection']
    states = validated.component_states
    reference_ids = ('equity-payload','producer-component','acceptance-witness','context-companion')
    references = (
        UpstreamReference(reference_ids[0],'EquityForge','authenticated composed equity observation',
                          'payloads/equity.json; record '+payload['record_id'],
                          'Exact selected observation and source-record semantics remain producer-owned.'),
        UpstreamReference(reference_ids[1],'EquityForge','inert source-component address',
                          'proof/producer-component.json; data/direct_tenq_ratios.json; sha256 '+address['component_sha256']+'; row:'+str(address['zero_based_row_index']),
                          'Addressed original member is inert provenance; local component witness is authenticated.'),
        UpstreamReference(reference_ids[2],'EquityForge','accepted-result witness',
                          'proof/acceptance-results.json; '+selection['accepted_result_key']+'; index:'+str(selection['accepted_result_index']),
                          'Acceptance and source proof are inherited, not freshly sourced.'),
        UpstreamReference(reference_ids[3],'EquityForge','context and companion',
                          'context/RESEARCH_CONTEXT.json; COMPOSED_PAYLOAD.json; '+validated.context_id+'; '+validated.identity.companion_id,
                          'Component states, compatibility findings, and no-join declarations remain producer-owned.'),
    )
    ids=('observation','period-measurement','numerator','denominator','availability-provenance','component-states','limitations')
    qualifications=', '.join(payload['qualification_codes'])
    texts=(
        f"{row['entity_name']} (CIK {row['entity_key']}): computed EquityForge net_margin {raw} as an exact raw fraction (unit ratio, scale 1; fraction_not_percent). {percent} (display-only; exact fraction {raw}). Not issuer-reported.",
        f"First-quarter direct quarterly duration {row['period_start']} through {row['period_end']}; source period class {row['source_period_class']}; track {row['track']}; formula {row['ratio_id']} / {row['formula_version']}; measurement {payload['measurement']['kind']}. Source metric-slot names are producer labels, not a claim that this observation is annual.",
        f"Numerator {row['numerator_concept']}: {row['numerator_canonical_value']} {row['numerator_unit']}; accession {row['numerator_accession_number']}; filed {row['numerator_filed_date']}; source row {row['numerator_source_row_identity']}; source document {row['numerator_source_document_sha256']}; selection group {row['numerator_selection_group_id']}; cell {row['numerator_cell_status']}; producer metric slot {row['numerator_metric_slot']} (not an annual period assertion).",
        f"Denominator {row['denominator_concept']}: {row['denominator_canonical_value']} {row['denominator_unit']}; accession {row['denominator_accession_number']}; filed {row['denominator_filed_date']}; source row {row['denominator_source_row_identity']}; source document {row['denominator_source_document_sha256']}; selection group {row['denominator_selection_group_id']}; cell {row['denominator_cell_status']}; producer metric slot {row['denominator_metric_slot']} (not an annual period assertion).",
        f"Availability {payload['availability']['date']} is max input filed-date proxy, non-PIT; not publication, retrieval, acceptance or revision-vintage time. Producer bundle {source.bundle_id}; source component {source.component_id}; source path {address['component_path']} sha256 {address['component_sha256']} row:{address['zero_based_row_index']}; accepted result {selection['accepted_result_key']} index {selection['accepted_result_index']}; context {validated.context_id}; companion {validated.identity.companion_id}; record {payload['record_id']}.",
        f"Package partial; equity {states[0][1]} (one observation), macro {states[1][1]} (no_accepted_matching_artifact), knowledge {states[2][1]} (general_company_claim_export_not_authoritative). Three blocked compatibility findings: all cross-domain joins unauthorized; no macro observation or knowledge claim/citation supplied.",
        f"Limitations and rights: {qualifications}. Not PIT-certified; historical filing completeness, fiscal calendar/issuer-country mapping, source dimensions or metric completeness not certified. Inherited authenticated-bundle source witness, not freshly verified original export. producer_record_hash null; knowledge citations absent; {payload['rights']}; no ranking, advice or cross-domain conclusion.",
    )
    attachments=((0,),(0,),(0,1),(0,1),(0,1,2),(0,3),(0,1,2,3))
    obligation_ids=('calculated-not-issuer','non-pit','partial-no-join','incomplete-source','inherited-witness-rights')
    obligations=(
        PresentationObligation(obligation_ids[0],'non-transformation','Computed by EquityForge, not issuer-reported; retain exact raw '+raw+' as fraction beside any display-only percentage.',(ids[0],ids[1])),
        PresentationObligation(obligation_ids[1],'freshness/review-state','The '+payload['availability']['date']+' filed-date proxy is non-PIT; not acceptance, publication, retrieval or revision-vintage time.',(ids[0],ids[4])),
        PresentationObligation(obligation_ids[2],'caveat/scope visibility','Package partial; macro unavailable, knowledge blocked, every cross-domain join unauthorized; do not invent claims or citations.',(ids[0],ids[5])),
        PresentationObligation(obligation_ids[3],'caveat/scope visibility','Retain qualifications: '+qualifications+'; no fiscal/country alignment or historical completeness certification.',(ids[0],ids[6])),
        PresentationObligation(obligation_ids[4],'evidence/provenance visibility','Authenticated bundled witness only, not fresh original SEC export; producer_record_hash null; rights '+payload['rights']+'; do not detach exact provenance.',(ids[0],ids[4],ids[6])),
    )
    # The primary observation carries every governing disclosure; later sections
    # repeat the applicable subset. First-use order matches the public contract.
    statement_obligations=((0,1,2,3,4),(0,3),(0,4),(0,4),(1,4),(2,),(1,2,3,4))
    statements=tuple(
        PresentationStatement(
            sid,text,'One exact accepted equity observation with visible provenance and partial-state limitations.',
            EncounterSemantics('sequence','Ordered single-observation reading path; target-independent; '+sid),
            tuple(reference_ids[j] for j in attachments[i]),
            tuple(obligation_ids[j] for j in statement_obligations[i]),
        )
        for i,(sid,text) in enumerate(zip(ids,texts))
    )
    candidate=CandidatePresentationPackage(
        identity=PackageIdentity(
            'briefforge:research-context-composed-payload:'+validated.identity.companion_id+':'+validated.identity.record_id,
            'Single admitted quarterly net-margin observation',
            'Present one authenticated source-selected ratio without economic recomputation.',
            'One equity observation and its producer-owned provenance, partial component states and limitations.',
            'No source selection, cross-domain joins, financial advice, HTML, renderer or publication.'),
        organizing_purpose=OrganizingPurpose(
            'Encounter the exact computed fraction, its two source operands, evidence, and blocked partial context together.',
            'One selected source-bound equity ratio; provenance and qualification visible.',
            'No macro or knowledge data, citation synthesis, fiscal alignment or cross-domain conclusions.'),
        statements=statements, upstream_references=references, obligations=obligations,
    )
    judgment=validate_candidate_presentation_package(candidate)
    if not judgment.valid:
        raise ComposedPackageError('CANDIDATE_INVALID','native presentation obligations rejected')
    source_record_json=json.dumps(row,sort_keys=True,ensure_ascii=True,allow_nan=False,separators=(',',':')).encode('ascii')
    return ComposedAdapterResult(candidate,validated.identity,validated.context_id,source_record_json,ADAPTER_VERSION)


setattr(adapt_research_context_composed_payload, '__signature__',
        _PublicSignature.from_callable(adapt_research_context_composed_payload))
