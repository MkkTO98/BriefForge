"""Experimental Communication Intent layer for BriefForge TASK-027.

This module is deliberately separate from the frozen runtime, validation,
promotion, Presentation Grammar, and renderer implementation. It reads existing
semantic package content and derives renderer-independent communication intent
annotations for investigation only.

It does not create a canonical runtime object, does not validate, does not
promote, does not render, does not template, does not choose charts, does not
write CSS/JavaScript, and does not change existing renderer behavior.
"""

from dataclasses import dataclass

from .runtime import CandidatePresentationPackage, PresentationStatement


VOCABULARY_VERSION = "communication-intent-experiment-v0.1"
LAYER_STATUS = "experimental-noncanonical"

CANONICAL_INTENTS = (
    "orient",
    "summarize",
    "explain",
    "compare",
    "quantify",
    "warn",
    "qualify",
    "trace",
    "conclude",
)

_INTENT_STRATEGIES = {
    "orient": (
        "Establish the reader question, subject, scope, non-scope, source owner, "
        "and why the presentation exists before details."
    ),
    "summarize": (
        "Provide an executive capsule: the main point, bounded implication, and "
        "confidence or uncertainty marker before supporting material."
    ),
    "explain": (
        "Use claim-evidence-implication sequencing so the reader can connect a "
        "statement to its reason and consequence."
    ),
    "compare": (
        "Keep the comparison basis, comparable entities, dimensions, units, and "
        "non-comparability caveats visible."
    ),
    "quantify": (
        "Preserve exact metric meaning: unit, geography, time period, source, "
        "definition, and whether numbers are observed, approximate, forecast, or scenario."
    ),
    "warn": (
        "Surface interpretation hazards early enough to prevent misuse: non-advice, "
        "non-ranking, source limits, stale data, or missing evidence."
    ),
    "qualify": (
        "Attach uncertainty, risk, caveat, counterargument, assumption, confidence, "
        "or status context to the affected claim rather than burying it later."
    ),
    "trace": (
        "Maintain an evidence register: source ownership, references, obligations, "
        "and audit identity remain inspectable without overwhelming first reading."
    ),
    "conclude": (
        "Close with bounded synthesis that states what the reader should take away "
        "without increasing claim strength beyond the package evidence."
    ),
}


@dataclass(frozen=True)
class StatementCommunicationIntent:
    """Experimental intent annotation for one existing PresentationStatement."""

    statement_id: str
    primary_intent: str
    supporting_intents: tuple[str, ...]
    source_mode: str
    evidence_basis: tuple[str, ...]
    communication_strategy: str


@dataclass(frozen=True)
class PackageCommunicationIntentProfile:
    """Experimental package-level intent profile derived from existing semantics."""

    package_id: str
    vocabulary_version: str
    layer_status: str
    package_intents: tuple[str, ...]
    statement_intents: tuple[StatementCommunicationIntent, ...]


def strategy_for_intent(intent: str) -> str:
    """Return the renderer-independent communication strategy for an intent."""

    if intent not in _INTENT_STRATEGIES:
        raise ValueError(f"Unknown communication intent: {intent}")
    return _INTENT_STRATEGIES[intent]


def intent_strategy_mapping() -> dict[str, str]:
    """Return all intent-to-communication-strategy mappings."""

    return dict(_INTENT_STRATEGIES)


def derive_communication_intent_profile(package: object) -> PackageCommunicationIntentProfile:
    """Derive experimental Communication Intent from existing semantic content.

    ``package`` may be a CandidatePresentationPackage or an object with a
    ``candidate`` attribute, such as ReadyPresentationPackage. The returned
    profile is non-canonical evidence for TASK-027 only.
    """

    candidate = _candidate_from(package)
    statement_profiles = tuple(
        _derive_statement_communication_intent(statement) for statement in candidate.statements
    )
    package_intents = _ordered_unique(
        intent
        for statement_profile in statement_profiles
        for intent in (statement_profile.primary_intent, *statement_profile.supporting_intents)
    )
    return PackageCommunicationIntentProfile(
        package_id=candidate.identity.package_id,
        vocabulary_version=VOCABULARY_VERSION,
        layer_status=LAYER_STATUS,
        package_intents=package_intents,
        statement_intents=statement_profiles,
    )


def _candidate_from(package: object) -> CandidatePresentationPackage:
    if isinstance(package, CandidatePresentationPackage):
        return package
    candidate = getattr(package, "candidate", None)
    if isinstance(candidate, CandidatePresentationPackage):
        return candidate
    raise TypeError("Communication Intent experiment requires a Candidate or Ready Presentation Package.")


def _derive_statement_communication_intent(statement: PresentationStatement) -> StatementCommunicationIntent:
    mode = statement.encounter_semantics.mode.lower()
    description = statement.encounter_semantics.description.lower()
    meaning = statement.encounter_meaning.lower()
    text = " ".join((mode, description, meaning))

    intents: list[str] = []
    basis: list[str] = []

    def add(intent: str, reason: str) -> None:
        if intent not in intents:
            intents.append(intent)
        if reason not in basis:
            basis.append(reason)

    if mode == "orientation" or any(term in text for term in ("introduce", "first encounter", "source artifact", "question")):
        add("orient", "orientation mode or reader-framing language")

    if any(term in text for term in ("overview", "summary", "main", "key takeaway", "at a glance")):
        add("summarize", "summary/overview language")

    if any(
        term in text
        for term in (
            "compare",
            "comparison",
            "similarity",
            "difference",
            "versus",
            " vs ",
            "relative",
            "shared",
        )
    ):
        add("compare", "comparison language or comparative encounter mode")

    if any(
        term in text
        for term in (
            "indicator",
            "quantitative",
            "gdp",
            "population",
            "rate",
            "metric",
            "table",
            "coverage",
            "missingness",
            "data quality",
            "statistical",
            "number",
            "scale",
            "series",
        )
    ):
        add("quantify", "metric/data/scale language")

    if any(
        term in text
        for term in (
            "risk",
            "warning",
            "hazard",
            "misuse",
            "do not",
            "non-advice",
            "not investment advice",
            "recommendation",
        )
    ):
        add("warn", "risk, warning, or misuse-prevention language")

    if any(
        term in text
        for term in (
            "caveat",
            "uncertain",
            "uncertainty",
            "counterargument",
            "counter",
            "confidence",
            "assumption",
            "limitation",
            "boundary",
            "approximate",
            "missing",
            "failure mode",
            "forecast",
            "scenario",
        )
    ):
        add("qualify", "uncertainty/caveat/boundary language")

    if statement.upstream_reference_ids or statement.obligation_ids:
        add("trace", "statement carries references or obligations")

    if any(term in text for term in ("conclusion", "conclude", "synthesis", "takeaway", "recommendation recovery", "close")):
        add("conclude", "conclusion/synthesis language")

    if any(
        term in text
        for term in (
            "because",
            "evidence",
            "show",
            "explain",
            "plausible",
            "support",
            "hypothesis",
            "analysis",
            "methodology",
            "context",
            "why",
        )
    ):
        add("explain", "explanatory, analytical, or evidence language")

    if not intents:
        add("explain", "default for semantic statement without specialized signal")

    primary = _select_primary_intent(intents)
    supporting = tuple(intent for intent in intents if intent != primary)
    return StatementCommunicationIntent(
        statement_id=statement.statement_id,
        primary_intent=primary,
        supporting_intents=supporting,
        source_mode=statement.encounter_semantics.mode,
        evidence_basis=tuple(basis),
        communication_strategy=strategy_for_intent(primary),
    )


def _select_primary_intent(intents: list[str]) -> str:
    priority = (
        "orient",
        "conclude",
        "compare",
        "warn",
        "qualify",
        "quantify",
        "summarize",
        "explain",
        "trace",
    )
    for intent in priority:
        if intent in intents:
            return intent
    return intents[0]


def _ordered_unique(values) -> tuple[str, ...]:
    seen: list[str] = []
    for value in values:
        if value not in seen:
            seen.append(value)
    return tuple(seen)
