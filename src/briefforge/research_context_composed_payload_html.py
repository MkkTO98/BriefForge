"""Offline, bounded HTML bytes for one freshly admitted composed presentation.

This local view is not a BCRP release, controlled invocation or publisher.
Economic selection, values, states and reasons belong to the admitted adapter.
"""
from dataclasses import dataclass
from base64 import b64encode
import hashlib
from html import escape

from .promotion import PromotionRejected, promote_candidate_presentation_package
from .research_context_composed_payload_adapter import (
    ADAPTER_VERSION, adapt_research_context_composed_payload,
)
from .research_context_composed_payload_validation import (
    CompanionPins, ComposedPackageRequest, _PublicSignature,
)
from .runtime import semantic_fingerprint
from .validation import validate_candidate_presentation_package

RENDERER_VERSION = 'briefforge.research-context-composed-payload-html.v1.0.0'
_MAX_HTML_BYTES = 262144
_CSS = 'p, li { overflow-wrap: anywhere; }'
_STYLE_HASH = b64encode(hashlib.sha256(_CSS.encode('utf-8')).digest()).decode('ascii')
_CSP = ("default-src 'none'; base-uri 'none'; form-action 'none'; object-src 'none'; "
        "style-src 'sha256-" + _STYLE_HASH + "'")
_SECTION_IDS = ('observation', 'period-measurement', 'numerator', 'denominator',
                'availability-provenance', 'component-states', 'limitations')
_SECTION_TITLES = ('Observation', 'Period and measurement', 'Numerator', 'Denominator',
                   'Availability and provenance', 'Partial component states', 'Limitations and rights')


@dataclass(frozen=True, slots=True)
class ComposedHtmlView:
    html_bytes: bytes
    sha256: str
    accepted_identity: CompanionPins
    context_id: str
    candidate_semantic_fingerprint: str
    renderer_version: str


class ComposedHtmlPolicyError(ValueError):
    """Renderer-only refusal; package admission errors remain ComposedPackageError."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _text(value: str) -> str:
    return escape(value, quote=True)


def _html(candidate) -> str:
    identity = candidate.identity
    purpose = candidate.organizing_purpose
    lines = [
        '<!doctype html>', '<html lang="en">', '<head>',
        '<meta charset="utf-8">',
        '<meta http-equiv="Content-Security-Policy" content="' + _text(_CSP) + '">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<style>' + _CSS + '</style>',
        '<title>' + _text(identity.title) + '</title>',
        '</head>', '<body>', '<main>',
        '<header><h1>' + _text(identity.title) + '</h1>',
        '<p>Package identity: ' + _text(identity.package_id) + '</p>',
        '<p>Purpose: ' + _text(identity.purpose_summary) + '</p>',
        '<p>Scope: ' + _text(identity.scope) + '</p>',
        '<p>Outside scope: ' + _text(identity.non_scope) + '</p>',
        '<p>Organizing purpose: ' + _text(purpose.statement) + '</p>',
        '<p>Organizing scope: ' + _text(purpose.scope) + '</p>',
        '<p>Organizing non-scope: ' + _text(purpose.non_scope) + '</p></header>',
        '<nav aria-label="Reading order"><ol>',
    ]
    for title in _SECTION_TITLES:
        lines.append('<li>' + title + '</li>')
    lines.extend(['</ol></nav>', '<article aria-label="Single partial research observation">'])
    for section_id, title, statement in zip(_SECTION_IDS, _SECTION_TITLES, candidate.statements):
        lines.extend([
            '<section id="' + section_id + '" aria-labelledby="heading-' + section_id + '">',
            '<h2 id="heading-' + section_id + '">' + title + '</h2>',
            '<p>Statement identity: ' + _text(statement.statement_id) + '</p>',
            '<p>' + _text(statement.encounter_meaning) + '</p>',
            '<p>Why included: ' + _text(statement.belongs_to_purpose) + '</p>',
            '<p>Source references: ' + ', '.join(_text(x) for x in statement.upstream_reference_ids) + '</p>',
            '<p>Attached obligations: ' + ', '.join(_text(x) for x in statement.obligation_ids) + '</p>',
            '</section>',
        ])
    lines.extend(['</article>', '<aside aria-label="Source provenance"><h2>Upstream references</h2><ol>'])
    for ref in candidate.upstream_references:
        lines.append('<li>' + '; '.join(_text(x) for x in (
            ref.reference_id, ref.owning_project, ref.reference_kind, ref.locator,
            ref.owned_meaning)) + '</li>')
    lines.extend(['</ol></aside>', '<aside aria-label="Presentation obligations"><h2>Obligations</h2><ol>'])
    for obligation in candidate.obligations:
        lines.append('<li>' + '; '.join(_text(x) for x in (
            obligation.obligation_id, obligation.category, obligation.requirement,
            *obligation.applies_to)) + '</li>')
    lines.extend(['</ol></aside>', '</main>', '</body>', '</html>', ''])
    return '\n'.join(lines)


def render_research_context_composed_payload_html(request: ComposedPackageRequest, /) -> ComposedHtmlView:
    """Re-admit independent pins, require Ready, return deterministic inert HTML bytes."""
    adapted = adapt_research_context_composed_payload(request)
    if adapted.adapter_version != ADAPTER_VERSION:
        raise ComposedHtmlPolicyError('ADAPTER_VERSION_UNSUPPORTED')
    judgment = validate_candidate_presentation_package(adapted.candidate)
    if not judgment.valid:
        raise ComposedHtmlPolicyError('CANDIDATE_REJECTED')
    try:
        ready = promote_candidate_presentation_package(adapted.candidate, judgment)
    except PromotionRejected as error:
        raise ComposedHtmlPolicyError('PROMOTION_REJECTED') from error
    candidate = ready.candidate
    if (len(candidate.statements) != len(_SECTION_IDS) or
            tuple(s.statement_id for s in candidate.statements) != _SECTION_IDS):
        raise ComposedHtmlPolicyError('CANDIDATE_REJECTED')
    fingerprint = semantic_fingerprint(candidate)
    try:
        raw = _html(candidate).encode('utf-8')
    except UnicodeEncodeError as error:
        raise ComposedHtmlPolicyError('HTML_ENCODING_ERROR') from error
    if len(raw) > _MAX_HTML_BYTES:
        raise ComposedHtmlPolicyError('HTML_SIZE_LIMIT')
    return ComposedHtmlView(raw, hashlib.sha256(raw).hexdigest(), adapted.accepted_identity,
                            adapted.context_id, fingerprint, RENDERER_VERSION)


setattr(render_research_context_composed_payload_html, '__signature__',
        _PublicSignature.from_callable(render_research_context_composed_payload_html))
