"""Constitutional validation for Candidate Presentation Packages.

Validation is a pure operation over Candidate Presentation Package runtime
records. It produces a Validation Judgment only. It does not mutate, promote,
render, serialize, persist, export, network, template, visualize, or serve
packages.
"""

from dataclasses import dataclass

from .runtime import CandidatePresentationPackage, semantic_fingerprint


CURRENT_VALIDATION_POLICY_ID = "briefforge-constitutional-validation-policy:v1"


@dataclass(frozen=True)
class ValidationFinding:
    """A constitutional validation finding."""

    constitutional_concept: str
    reason: str
    code: str


@dataclass(frozen=True)
class ValidationJudgment:
    """Presentation-local constitutional judgment for one candidate package."""

    valid: bool
    candidate_package_id: str | None
    candidate_semantic_fingerprint: str
    validation_policy_id: str
    findings: tuple[ValidationFinding, ...] = ()


def validate_candidate_presentation_package(
    package: CandidatePresentationPackage,
) -> ValidationJudgment:
    """Validate only constitutional requirements for a candidate package."""

    findings: list[ValidationFinding] = []

    if package.identity is None:
        findings.append(_finding("Package Identity", "Package identity is required.", "missing-package-identity"))
    else:
        for field_name in ("package_id", "title", "purpose_summary", "scope", "non_scope"):
            if _blank(getattr(package.identity, field_name)):
                findings.append(
                    _finding(
                        "Package Identity",
                        f"Package identity field {field_name!r} is required for bounded self-identification.",
                        f"missing-package-identity-{field_name}",
                    )
                )

    if package.organizing_purpose is None:
        findings.append(
            _finding("Organizing Purpose", "Organizing Purpose is required.", "missing-organizing-purpose")
        )
    else:
        for field_name in ("statement", "scope", "non_scope"):
            if _blank(getattr(package.organizing_purpose, field_name)):
                findings.append(
                    _finding(
                        "Organizing Purpose",
                        f"Organizing Purpose field {field_name!r} is required to bind the package.",
                        f"missing-organizing-purpose-{field_name}",
                    )
                )

    if not package.statements:
        findings.append(
            _finding(
                "Presentation Statements",
                "At least one organized presentation statement is required.",
                "missing-presentation-statements",
            )
        )

    reference_ids = {reference.reference_id for reference in package.upstream_references}
    obligation_ids = {obligation.obligation_id for obligation in package.obligations}
    statement_ids = {statement.statement_id for statement in package.statements}
    known_attachment_ids = reference_ids | statement_ids

    for statement in package.statements:
        if statement.encounter_semantics is None:
            findings.append(
                _finding(
                    "Encounter Semantics",
                    f"Statement {statement.statement_id!r} requires target-independent encounter semantics.",
                    "missing-encounter-semantics",
                )
            )
        else:
            if _blank(statement.encounter_semantics.mode) or _blank(statement.encounter_semantics.description):
                findings.append(
                    _finding(
                        "Encounter Semantics",
                        f"Statement {statement.statement_id!r} requires described target-independent encounter semantics.",
                        "incomplete-encounter-semantics",
                    )
                )
            for related_id in statement.encounter_semantics.related_statement_ids:
                if related_id not in statement_ids:
                    findings.append(
                        _finding(
                            "Encounter Semantics",
                            f"Statement {statement.statement_id!r} relates to unknown statement {related_id!r}.",
                            "unknown-related-statement",
                        )
                    )

        for reference_id in statement.upstream_reference_ids:
            if reference_id not in reference_ids:
                findings.append(
                    _finding(
                        "Upstream References",
                        f"Statement {statement.statement_id!r} depends on unknown upstream reference {reference_id!r}.",
                        "unknown-upstream-reference",
                    )
                )

        if statement.upstream_reference_ids and not statement.obligation_ids:
            findings.append(
                _finding(
                    "Presentation Obligations",
                    f"Statement {statement.statement_id!r} depends on upstream material but has no attached obligations.",
                    "missing-obligation-attachment",
                )
            )

        for obligation_id in statement.obligation_ids:
            if obligation_id not in obligation_ids:
                findings.append(
                    _finding(
                        "Presentation Obligations",
                        f"Statement {statement.statement_id!r} attaches unknown obligation {obligation_id!r}.",
                        "unknown-presentation-obligation",
                    )
                )

    for obligation in package.obligations:
        if _blank(obligation.category) or _blank(obligation.requirement):
            findings.append(
                _finding(
                    "Presentation Obligations",
                    f"Obligation {obligation.obligation_id!r} requires category and requirement.",
                    "incomplete-presentation-obligation",
                )
            )
        for target_id in obligation.applies_to:
            if target_id not in known_attachment_ids:
                findings.append(
                    _finding(
                        "Presentation Obligations",
                        f"Obligation {obligation.obligation_id!r} applies to unknown package element {target_id!r}.",
                        "unknown-obligation-target",
                    )
                )

    candidate_package_id = None
    if package.identity is not None and isinstance(package.identity.package_id, str):
        candidate_package_id = package.identity.package_id

    return ValidationJudgment(
        valid=not findings,
        candidate_package_id=candidate_package_id,
        candidate_semantic_fingerprint=semantic_fingerprint(package),
        validation_policy_id=CURRENT_VALIDATION_POLICY_ID,
        findings=tuple(findings),
    )


def _finding(constitutional_concept: str, reason: str, code: str) -> ValidationFinding:
    return ValidationFinding(constitutional_concept=constitutional_concept, reason=reason, code=code)


def _blank(value: str) -> bool:
    return not isinstance(value, str) or not value.strip()
