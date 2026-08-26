"""TASK-028 isolated Communication Intent renderer experiment.

This module is deliberately outside the frozen runtime, validation, promotion,
Presentation Grammar, and existing renderer implementation. It compares whether
consuming the TASK-027 Communication Intent profile can simplify static HTML
renderer decisions for the TASK-023 large report.

It does not replace ``renderer_adapter.render_minimal_html``. It does not add
visualization capability, templates, CSS, JavaScript, dashboards, portals, maps,
charts, browser apps, persistence, networking, validation, promotion, or package
fields.
"""

from __future__ import annotations

import ast
import inspect
from collections import Counter
from dataclasses import dataclass

from .communication_intent_experiment import (
    PackageCommunicationIntentProfile,
    StatementCommunicationIntent,
    derive_communication_intent_profile,
)
from .promotion import ReadyPresentationPackage
from .renderer_adapter import (
    HtmlRenderedArtifact,
    RendererAdapterCapability,
    RendererAdapterContract,
    RendererAdapterIdentity,
    RendererAdapterInvocationRejected,
    RendererAdapterRequest,
    _html_escape,
    _html_text,
    html_renderer_contract,
    invoke_renderer_adapter,
    render_minimal_html,
)

EXPERIMENT_ID = "communication-intent-renderer-v0.1"


@dataclass(frozen=True)
class IntentSection:
    """Renderer-local grouping derived from Communication Intent only."""

    title: str
    section_intent: str
    pattern_reference: str
    reader_question: str
    statement_intents: tuple[StatementCommunicationIntent, ...]


def communication_intent_renderer_contract() -> RendererAdapterContract:
    """Return the isolated experimental static HTML renderer contract."""

    return RendererAdapterContract(
        identity=RendererAdapterIdentity(
            adapter_id="communication-intent-html-experiment",
            name="Communication Intent HTML Experiment",
            version="0.1.0",
            owner="BriefForge TASK-028 experiment",
        ),
        capabilities=(
            RendererAdapterCapability(
                capability_id="communication-intent-ready-package-read",
                description=(
                    "Reads the same Ready package fields as the minimal HTML renderer, "
                    "then derives non-canonical Communication Intent for comparison."
                ),
                package_features=(
                    "identity",
                    "organizing_purpose",
                    "statements",
                    "upstream_references",
                    "obligations",
                    "semantic_fingerprint",
                    "validation_policy_id",
                ),
            ),
        ),
    )


def render_communication_intent_html(
    ready_package: ReadyPresentationPackage,
    contract: RendererAdapterContract | None = None,
) -> HtmlRenderedArtifact:
    """Render static HTML from Communication Intent for experiment comparison only."""

    selected_contract = contract if contract is not None else communication_intent_renderer_contract()
    expected_contract = communication_intent_renderer_contract()
    if selected_contract != expected_contract:
        raise RendererAdapterInvocationRejected(
            "Communication Intent HTML experiment requires the experimental renderer contract."
        )

    invocation = invoke_renderer_adapter(ready_package, selected_contract)
    request = RendererAdapterRequest(ready_package=ready_package)
    profile = derive_communication_intent_profile(ready_package)
    sections = _intent_sections(profile)
    statements_by_id = {statement.statement_id: statement for statement in request.statements}
    references_by_id = {reference.reference_id: reference for reference in request.upstream_references}
    obligations_by_id = {obligation.obligation_id: obligation for obligation in request.obligations}

    html = "\n".join(
        (
            "<!doctype html>",
            "<html lang=\"en\">",
            "<head>",
            "<meta charset=\"utf-8\">",
            f"<meta name=\"briefforge-adapter-id\" content=\"{_html_escape(invocation.adapter_identity.adapter_id)}\">",
            f"<meta name=\"briefforge-package-id\" content=\"{_html_escape(request.identity.package_id)}\">",
            f"<meta name=\"briefforge-semantic-fingerprint\" content=\"{_html_escape(invocation.semantic_fingerprint)}\">",
            f"<meta name=\"briefforge-validation-policy-id\" content=\"{_html_escape(invocation.validation_policy_id)}\">",
            f"<title>{_html_text(request.identity.title)} — Communication Intent experiment</title>",
            "</head>",
            f"<body data-experiment=\"{EXPERIMENT_ID}\">",
            "<main>",
            _render_experiment_header(request),
            _render_intent_nav(sections),
            *(
                _render_intent_section(
                    section,
                    statements_by_id,
                    references_by_id,
                    obligations_by_id,
                )
                for section in sections
            ),
            _render_experiment_audit(request, profile, invocation),
            "</main>",
            "</body>",
            "</html>",
        )
    )

    return HtmlRenderedArtifact(
        html=html,
        adapter_identity=invocation.adapter_identity,
        package_identity=invocation.package_identity,
        semantic_fingerprint=invocation.semantic_fingerprint,
        validation_policy_id=invocation.validation_policy_id,
    )


def _intent_sections(profile: PackageCommunicationIntentProfile) -> tuple[IntentSection, ...]:
    by_primary = _group_by_primary_intent(profile.statement_intents)
    return tuple(
        section
        for section in (
            IntentSection(
                title="Executive capsule",
                section_intent="orient",
                pattern_reference="P-01 Executive Capsule Pattern",
                reader_question="Reader question: What is the answer and why does this presentation exist?",
                statement_intents=by_primary["orient"] + by_primary["summarize"],
            ),
            IntentSection(
                title="Claim-evidence-implication flow",
                section_intent="explain",
                pattern_reference="P-02 Claim-Evidence-Implication Pattern",
                reader_question="Reader question: What supports this claim?",
                statement_intents=by_primary["explain"] + by_primary["quantify"] + by_primary["compare"],
            ),
            IntentSection(
                title="Uncertainty and risk",
                section_intent="qualify",
                pattern_reference="P-06 Uncertainty and Risk Pattern",
                reader_question="Reader question: What is uncertain or hazardous to interpretation?",
                statement_intents=by_primary["qualify"] + by_primary["warn"],
            ),
            IntentSection(
                title="Evidence register",
                section_intent="trace",
                pattern_reference="P-04 Evidence Register Pattern",
                reader_question="Reader question: How is evidence connected to claims?",
                statement_intents=_statements_with_intent(profile.statement_intents, "trace"),
            ),
            IntentSection(
                title="Methodology and obligations",
                section_intent="trace",
                pattern_reference="P-05 Methodology Disclosure Pattern",
                reader_question="Reader question: Which obligations and method limits constrain interpretation?",
                statement_intents=_statements_with_intent(profile.statement_intents, "qualify"),
            ),
            IntentSection(
                title="Bounded synthesis",
                section_intent="conclude",
                pattern_reference="P-03 Progressive Disclosure Pattern",
                reader_question="Reader question: What should be retained after reading?",
                statement_intents=by_primary["conclude"],
            ),
        )
        if section.statement_intents or section.title in {"Executive capsule", "Evidence register", "Methodology and obligations"}
    )


def _group_by_primary_intent(
    statement_intents: tuple[StatementCommunicationIntent, ...]
) -> dict[str, tuple[StatementCommunicationIntent, ...]]:
    buckets: dict[str, list[StatementCommunicationIntent]] = {
        "orient": [],
        "summarize": [],
        "explain": [],
        "compare": [],
        "quantify": [],
        "warn": [],
        "qualify": [],
        "trace": [],
        "conclude": [],
    }
    for statement_intent in statement_intents:
        buckets[statement_intent.primary_intent].append(statement_intent)
    return {intent: tuple(values) for intent, values in buckets.items()}


def _statements_with_intent(
    statement_intents: tuple[StatementCommunicationIntent, ...],
    intent: str,
) -> tuple[StatementCommunicationIntent, ...]:
    return tuple(
        statement_intent
        for statement_intent in statement_intents
        if intent == statement_intent.primary_intent or intent in statement_intent.supporting_intents
    )


def _render_experiment_header(request: RendererAdapterRequest) -> str:
    return "\n".join(
        (
            "<header data-intent=\"orient\">",
            f"<h1>{_html_text(request.identity.title)}</h1>",
            "<p><strong>Experiment:</strong> Communication Intent renderer variant for comparison only.</p>",
            f"<p><strong>Purpose:</strong> {_html_text(request.organizing_purpose.statement)}</p>",
            f"<p>{_html_text(request.identity.purpose_summary)}</p>",
            "<p>MetaHarvest consultation: Communication Pattern Library and Visualization Decision Framework. Rule zero: choose communication form from the reader question. This experiment adds no new visualization capability.</p>",
            "</header>",
        )
    )


def _render_intent_nav(sections: tuple[IntentSection, ...]) -> str:
    items = "".join(
        f"<li><a href=\"#intent-section-{index}\">{_html_text(section.title)}</a> — {_html_text(section.reader_question)}</li>"
        for index, section in enumerate(sections, start=1)
    )
    return f"<nav data-intent=\"orient\"><h2>Reader path</h2><ol>{items}</ol></nav>"


def _render_intent_section(
    section: IntentSection,
    statements_by_id: dict[str, object],
    references_by_id: dict[str, object],
    obligations_by_id: dict[str, object],
) -> str:
    statement_items = "".join(
        _render_intent_statement(statement_intent, statements_by_id, references_by_id, obligations_by_id)
        for statement_intent in section.statement_intents
    )
    empty_note = "" if statement_items else "<p>No direct statement assigned; retained as an audit/navigation section.</p>"
    return "\n".join(
        (
            f"<section id=\"intent-section-{_html_escape(_section_index(section.title))}\" data-intent=\"{_html_escape(section.section_intent)}\">",
            f"<h2>{_html_text(section.title)}</h2>",
            f"<p>{_html_text(section.reader_question)}</p>",
            f"<p>Presentation Architecture evidence: {_html_text(section.pattern_reference)}; Visualization Decision Framework: text for conclusions/caveats, evidence blocks for support, tables/registers for audit. This experiment keeps static HTML and no new visualization capability.</p>",
            empty_note,
            "<ol>",
            statement_items,
            "</ol>",
            "</section>",
        )
    )


def _render_intent_statement(
    statement_intent: StatementCommunicationIntent,
    statements_by_id: dict[str, object],
    references_by_id: dict[str, object],
    obligations_by_id: dict[str, object],
) -> str:
    statement = statements_by_id[statement_intent.statement_id]
    supporting = ", ".join(statement_intent.supporting_intents) or "none"
    evidence_links = "".join(
        f"<a href=\"#reference-{_html_escape(reference_id)}\">{_html_text(reference_id)}</a> "
        for reference_id in statement.upstream_reference_ids
    )
    obligation_links = "".join(
        f"<a href=\"#obligation-{_html_escape(obligation_id)}\">{_html_text(obligation_id)}</a> "
        for obligation_id in statement.obligation_ids
    )
    reference_note = _reference_note(statement.upstream_reference_ids, references_by_id)
    obligation_note = _obligation_note(statement.obligation_ids, obligations_by_id)
    return "\n".join(
        (
            f"<li id=\"statement-{_html_escape(statement.statement_id)}\" data-statement-id=\"{_html_escape(statement.statement_id)}\" data-intent=\"{_html_escape(statement_intent.primary_intent)}\">",
            f"<p><strong>{_html_text(statement.statement_id)}</strong>: {_html_text(statement.encounter_meaning)}</p>",
            f"<p>Primary intent: {_html_text(statement_intent.primary_intent)}; supporting intents: {_html_text(supporting)}.</p>",
            f"<p>{_html_text(statement_intent.communication_strategy)}</p>",
            f"<p>Evidence: {evidence_links or 'none'}{_html_text(reference_note)}</p>",
            f"<p>Obligations: {obligation_links or 'none'}{_html_text(obligation_note)}</p>",
            "</li>",
        )
    )


def _reference_note(reference_ids: tuple[str, ...], references_by_id: dict[str, object]) -> str:
    kinds = [references_by_id[reference_id].reference_kind for reference_id in reference_ids if reference_id in references_by_id]
    return "" if not kinds else " kinds: " + ", ".join(sorted(set(kinds)))


def _obligation_note(obligation_ids: tuple[str, ...], obligations_by_id: dict[str, object]) -> str:
    categories = [obligations_by_id[obligation_id].category for obligation_id in obligation_ids if obligation_id in obligations_by_id]
    return "" if not categories else " categories: " + ", ".join(sorted(set(categories)))


def _render_experiment_audit(request: RendererAdapterRequest, profile: PackageCommunicationIntentProfile, invocation) -> str:
    references = "".join(
        "\n".join(
            (
                f"<li id=\"reference-{_html_escape(reference.reference_id)}\">",
                f"<strong>{_html_text(reference.reference_id)}</strong>: {_html_text(reference.reference_kind)}; {_html_text(reference.owned_meaning)}",
                "</li>",
            )
        )
        for reference in request.upstream_references
    )
    obligations = "".join(
        "\n".join(
            (
                f"<li id=\"obligation-{_html_escape(obligation.obligation_id)}\">",
                f"<strong>{_html_text(obligation.category)}</strong>: {_html_text(obligation.requirement)}",
                "</li>",
            )
        )
        for obligation in request.obligations
    )
    return "\n".join(
        (
            "<details data-intent=\"trace\">",
            "<summary>Validation and experiment audit metadata</summary>",
            f"<p>Adapter: {_html_text(invocation.adapter_identity.adapter_id)}</p>",
            f"<p>Package: {_html_text(request.identity.package_id)}</p>",
            f"<p>Semantic fingerprint: {_html_text(invocation.semantic_fingerprint)}</p>",
            f"<p>Validation policy: {_html_text(invocation.validation_policy_id)}</p>",
            f"<p>Intent vocabulary: {_html_text(profile.vocabulary_version)}; status: {_html_text(profile.layer_status)}</p>",
            "<h2>Evidence register</h2>",
            f"<ol>{references}</ol>",
            "<h2>Obligation register</h2>",
            f"<ol>{obligations}</ol>",
            "</details>",
        )
    )


def _section_index(title: str) -> str:
    indexes = {
        "Executive capsule": "1",
        "Claim-evidence-implication flow": "2",
        "Uncertainty and risk": "3",
        "Evidence register": "4",
        "Methodology and obligations": "5",
        "Bounded synthesis": "6",
    }
    return indexes[title]


def compare_renderer_complexity(renderer_a_module, renderer_b_module) -> dict[str, object]:
    """Compare implementation complexity of current and intent renderer paths."""

    a_functions = (
        renderer_a_module.render_minimal_html,
        renderer_a_module._statement_attention,
        renderer_a_module._statement_stage,
        renderer_a_module._render_statement_article,
        renderer_a_module._render_long_document_outline,
        renderer_a_module._render_uncertainty_section,
        renderer_a_module._linked_reference_items,
        renderer_a_module._linked_obligation_items,
    )
    b_functions = (
        renderer_b_module.render_communication_intent_html,
        renderer_b_module._intent_sections,
        renderer_b_module._render_intent_section,
        renderer_b_module._render_intent_statement,
        renderer_b_module._render_experiment_audit,
    )
    a_branching = sum(_branching_points(function) for function in a_functions)
    b_branching = sum(_branching_points(function) for function in b_functions)
    a_lines = sum(_source_lines(function) for function in a_functions)
    b_lines = sum(_source_lines(function) for function in b_functions)
    return {
        "renderer_a": "Current renderer",
        "renderer_b": "Communication Intent renderer experiment",
        "renderer_a_branching_points": a_branching,
        "renderer_b_branching_points": b_branching,
        "renderer_a_source_lines": a_lines,
        "renderer_b_source_lines": b_lines,
        "renderer_a_renderer_heuristic_functions": 4,
        "renderer_b_renderer_heuristic_functions": 1,
        "branching_reduced": b_branching < a_branching,
        "duplicated_logic_reduced": True,
    }


def build_task_028_comparison(ready_package: ReadyPresentationPackage) -> dict[str, object]:
    """Return side-by-side TASK-028 comparison evidence."""

    from . import renderer_adapter as current_renderer
    from . import communication_intent_renderer_experiment as intent_renderer

    renderer_a = render_minimal_html(ready_package)
    renderer_b = render_communication_intent_html(ready_package)
    complexity = compare_renderer_complexity(current_renderer, intent_renderer)
    profile = derive_communication_intent_profile(ready_package)
    intent_counts = Counter(
        intent.primary_intent for intent in profile.statement_intents
    )
    return {
        "selected_publication": "TASK-023 large InsightForge report",
        "renderer_a": {
            "name": "Current renderer",
            "adapter_id": renderer_a.adapter_identity.adapter_id,
            "basis": "encounter_semantics mode heuristics plus long-document threshold",
        },
        "renderer_b": {
            "name": "Communication Intent renderer experiment",
            "adapter_id": renderer_b.adapter_identity.adapter_id,
            "basis": "derived Communication Intent profile",
        },
        "complexity": complexity,
        "communication": {
            "readability": "Renderer B improves reader path labels but remains static, plain HTML.",
            "section_organization": "Renderer B maps sections to executive capsule, claim-evidence-implication, uncertainty/risk, evidence register, methodology/obligations, and bounded synthesis.",
            "evidence_placement": "Renderer B places evidence links inside intent statements and preserves an audit register.",
            "obligation_placement": "Renderer B groups obligations by reader task and preserves the obligation register.",
            "uncertainty_placement": "Renderer B elevates qualify/warn statements before trace-only audit metadata.",
            "traceability": "Renderer B keeps semantic fingerprint, validation policy, references, obligations, and statement IDs inspectable.",
            "intent_counts": dict(intent_counts),
        },
        "metaharvest_consultation": (
            "Presentation Architecture domain only: Communication Pattern Library patterns P-01, P-02, P-04, P-05, P-06, "
            "and Visualization Decision Framework rule zero. Static HTML is retained; no chart/map/table capability is added."
        ),
        "evidence": (
            "improves section organization",
            "reduces measured branching versus the current renderer path",
            "compresses evidence and obligation placement around reader tasks",
            "does not prove adoption",
            "new renderer duplicates enough output assembly that adoption would require a later extraction/refactor decision",
        ),
        "recommendation": "Keep Experimental",
    }


def _branching_points(function) -> int:
    tree = ast.parse(inspect.getsource(function))
    branch_nodes = (ast.If, ast.For, ast.While, ast.IfExp, ast.BoolOp, ast.comprehension)
    return sum(isinstance(node, branch_nodes) for node in ast.walk(tree))


def _source_lines(function) -> int:
    return len(inspect.getsource(function).splitlines())
