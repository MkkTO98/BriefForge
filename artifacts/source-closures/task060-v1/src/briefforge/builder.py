"""Authoring convenience for Candidate Presentation Packages.

The PresentationPackageBuilder constructs the existing runtime dataclasses only.
It does not introduce new semantic concepts, validation rules, promotion,
rendering, serialization, persistence, APIs, templates, components, or browser
behavior.
"""

import hashlib
import json

from .runtime import (
    CandidatePresentationPackage,
    EncounterSemantics,
    OrganizingPurpose,
    PackageIdentity,
    PresentationObligation,
    PresentationStatement,
    UpstreamReference,
)


class PresentationPackageBuildRejected(ValueError):
    """Raised when a builder cannot produce a Candidate Presentation Package."""


class PresentationPackageBuilder:
    """Small fluent helper for authoring existing Candidate Presentation Packages."""

    def __init__(self) -> None:
        self._identity: PackageIdentity | None = None
        self._organizing_purpose: OrganizingPurpose | None = None
        self._statements: list[PresentationStatement] = []
        self._upstream_references: list[UpstreamReference] = []
        self._obligations: list[PresentationObligation] = []

    def identity(
        self,
        *,
        title: str,
        purpose_summary: str,
        scope: str,
        non_scope: str,
        package_id: str | None = None,
    ) -> "PresentationPackageBuilder":
        """Set package identity using the existing PackageIdentity record.

        When ``package_id`` is omitted, a deterministic id is generated from the
        supplied identity semantics. Explicit ids are preserved unchanged.
        """

        _require_non_blank(title, "title")
        _require_non_blank(purpose_summary, "purpose_summary")
        _require_non_blank(scope, "scope")
        _require_non_blank(non_scope, "non_scope")
        resolved_package_id = _explicit_or_generated_id(
            package_id,
            "package_id",
            prefix="pkg",
            payload={
                "title": title,
                "purpose_summary": purpose_summary,
                "scope": scope,
                "non_scope": non_scope,
            },
        )
        self._identity = PackageIdentity(
            package_id=resolved_package_id,
            title=title,
            purpose_summary=purpose_summary,
            scope=scope,
            non_scope=non_scope,
        )
        return self

    def organizing_purpose(
        self,
        *,
        statement: str,
        scope: str,
        non_scope: str,
    ) -> "PresentationPackageBuilder":
        """Set organizing purpose using the existing OrganizingPurpose record."""

        _require_non_blank(statement, "organizing_purpose.statement")
        _require_non_blank(scope, "organizing_purpose.scope")
        _require_non_blank(non_scope, "organizing_purpose.non_scope")
        self._organizing_purpose = OrganizingPurpose(statement=statement, scope=scope, non_scope=non_scope)
        return self

    def add_statement(
        self,
        *,
        encounter_meaning: str,
        belongs_to_purpose: str,
        encounter_mode: str,
        encounter_description: str,
        statement_id: str | None = None,
        related_statement_ids: tuple[str, ...] = (),
        upstream_reference_ids: tuple[str, ...] = (),
        obligation_ids: tuple[str, ...] = (),
    ) -> "PresentationPackageBuilder":
        """Append a presentation statement using existing runtime records.

        When ``statement_id`` is omitted, a deterministic id is generated from
        the statement's own presentation semantics. Relationship tuples are not
        included in the generated id, which minimizes churn when unchanged
        objects are merely related differently by explicit ids.
        """

        _require_non_blank(encounter_meaning, "encounter_meaning")
        _require_non_blank(belongs_to_purpose, "belongs_to_purpose")
        _require_non_blank(encounter_mode, "encounter_mode")
        _require_non_blank(encounter_description, "encounter_description")
        related_ids = _text_tuple(related_statement_ids, "related_statement_ids")
        reference_ids = _text_tuple(upstream_reference_ids, "upstream_reference_ids")
        attached_obligation_ids = _text_tuple(obligation_ids, "obligation_ids")
        resolved_statement_id = _explicit_or_generated_id(
            statement_id,
            "statement_id",
            prefix="stmt",
            payload={
                "encounter_meaning": encounter_meaning,
                "belongs_to_purpose": belongs_to_purpose,
                "encounter_mode": encounter_mode,
                "encounter_description": encounter_description,
            },
        )
        self._statements.append(
            PresentationStatement(
                statement_id=resolved_statement_id,
                encounter_meaning=encounter_meaning,
                belongs_to_purpose=belongs_to_purpose,
                encounter_semantics=EncounterSemantics(
                    mode=encounter_mode,
                    description=encounter_description,
                    related_statement_ids=related_ids,
                ),
                upstream_reference_ids=reference_ids,
                obligation_ids=attached_obligation_ids,
            )
        )
        return self

    def add_upstream_reference(
        self,
        *,
        owning_project: str,
        reference_kind: str,
        locator: str,
        owned_meaning: str,
        reference_id: str | None = None,
    ) -> "PresentationPackageBuilder":
        """Append an upstream reference using the existing UpstreamReference record.

        When ``reference_id`` is omitted, a deterministic id is generated from
        the reference's source-ownership semantics.
        """

        _require_non_blank(owning_project, "owning_project")
        _require_non_blank(reference_kind, "reference_kind")
        _require_non_blank(locator, "locator")
        _require_non_blank(owned_meaning, "owned_meaning")
        resolved_reference_id = _explicit_or_generated_id(
            reference_id,
            "reference_id",
            prefix="ref",
            payload={
                "owning_project": owning_project,
                "reference_kind": reference_kind,
                "locator": locator,
                "owned_meaning": owned_meaning,
            },
        )
        self._upstream_references.append(
            UpstreamReference(
                reference_id=resolved_reference_id,
                owning_project=owning_project,
                reference_kind=reference_kind,
                locator=locator,
                owned_meaning=owned_meaning,
            )
        )
        return self

    def add_obligation(
        self,
        *,
        category: str,
        requirement: str,
        obligation_id: str | None = None,
        applies_to: tuple[str, ...] = (),
    ) -> "PresentationPackageBuilder":
        """Append a presentation obligation using the existing obligation record.

        When ``obligation_id`` is omitted, a deterministic id is generated from
        the obligation requirement and its explicit attachment surface.
        """

        _require_non_blank(category, "category")
        _require_non_blank(requirement, "requirement")
        applies_to_ids = _text_tuple(applies_to, "applies_to")
        resolved_obligation_id = _explicit_or_generated_id(
            obligation_id,
            "obligation_id",
            prefix="obl",
            payload={
                "category": category,
                "requirement": requirement,
                "applies_to": applies_to_ids,
            },
        )
        self._obligations.append(
            PresentationObligation(
                obligation_id=resolved_obligation_id,
                category=category,
                requirement=requirement,
                applies_to=applies_to_ids,
            )
        )
        return self

    def build(self) -> CandidatePresentationPackage:
        """Produce the existing CandidatePresentationPackage runtime object."""

        if self._identity is None:
            raise PresentationPackageBuildRejected("Cannot build Candidate Presentation Package without identity.")
        if self._organizing_purpose is None:
            raise PresentationPackageBuildRejected(
                "Cannot build Candidate Presentation Package without organizing_purpose."
            )
        if not self._statements:
            raise PresentationPackageBuildRejected("Cannot build Candidate Presentation Package without statements.")
        return CandidatePresentationPackage(
            identity=self._identity,
            organizing_purpose=self._organizing_purpose,
            statements=tuple(self._statements),
            upstream_references=tuple(self._upstream_references),
            obligations=tuple(self._obligations),
        )


def _require_non_blank(value: object, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise PresentationPackageBuildRejected(f"Required builder field {field_name} must be non-empty text.")


def _text_tuple(values: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise PresentationPackageBuildRejected(f"Builder field {field_name} must be a tuple of text values.")
    for value in values:
        _require_non_blank(value, field_name)
    return values


def _explicit_or_generated_id(
    value: str | None,
    field_name: str,
    *,
    prefix: str,
    payload: dict[str, object],
) -> str:
    if value is not None:
        _require_non_blank(value, field_name)
        return value
    return _deterministic_id(prefix, payload)


def _deterministic_id(prefix: str, payload: dict[str, object]) -> str:
    canonical_payload = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"
