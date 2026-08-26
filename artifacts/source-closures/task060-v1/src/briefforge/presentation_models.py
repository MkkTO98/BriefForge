"""Semantic presentation models for BriefForge authoring.

Presentation models are authoring abstractions. They produce the existing
Candidate Presentation Package through the existing builder and runtime. They
are not templates, renderers, browser pages, visualizations, APIs, persistence
layers, or new runtime concepts.
"""

from dataclasses import dataclass

from .builder import PresentationPackageBuildRejected, PresentationPackageBuilder
from .runtime import CandidatePresentationPackage


@dataclass(frozen=True)
class CountryProfilePresentation:
    """Small semantic country-profile authoring model.

    The model holds the already-built candidate package as its output surface so
    callers can cross the existing BriefForge lifecycle without any new runtime
    object or lifecycle stage.
    """

    country_name: str
    candidate: CandidatePresentationPackage

    def to_candidate_presentation_package(self) -> CandidatePresentationPackage:
        """Return the existing Candidate Presentation Package runtime object."""

        return self.candidate


class CountryProfileBuilder:
    """Author a deliberately small country profile with the existing builder."""

    def __init__(self, *, country_name: str) -> None:
        _require_non_blank(country_name, "country_name")
        self._country_name = country_name
        self._builder = PresentationPackageBuilder()

    def identity(
        self,
        *,
        title: str,
        purpose_summary: str,
        scope: str,
        non_scope: str,
        package_id: str | None = None,
    ) -> "CountryProfileBuilder":
        self._builder.identity(
            package_id=package_id,
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
    ) -> "CountryProfileBuilder":
        self._builder.organizing_purpose(statement=statement, scope=scope, non_scope=non_scope)
        return self

    def reference(
        self,
        *,
        owning_project: str,
        reference_kind: str,
        locator: str,
        owned_meaning: str,
        reference_id: str | None = None,
    ) -> "CountryProfileBuilder":
        self._builder.add_upstream_reference(
            reference_id=reference_id,
            owning_project=owning_project,
            reference_kind=reference_kind,
            locator=locator,
            owned_meaning=owned_meaning,
        )
        return self

    def obligation(
        self,
        *,
        category: str,
        requirement: str,
        obligation_id: str | None = None,
        applies_to: tuple[str, ...] = (),
    ) -> "CountryProfileBuilder":
        self._builder.add_obligation(
            obligation_id=obligation_id,
            category=category,
            requirement=requirement,
            applies_to=applies_to,
        )
        return self

    def overview(
        self,
        *,
        encounter_meaning: str,
        encounter_description: str,
        statement_id: str | None = None,
        related_statement_ids: tuple[str, ...] = (),
        upstream_reference_ids: tuple[str, ...] = (),
        obligation_ids: tuple[str, ...] = (),
    ) -> "CountryProfileBuilder":
        return self.section(
            statement_id=statement_id,
            section_kind="overview",
            encounter_meaning=encounter_meaning,
            encounter_mode="orientation",
            encounter_description=encounter_description,
            related_statement_ids=related_statement_ids,
            upstream_reference_ids=upstream_reference_ids,
            obligation_ids=obligation_ids,
        )

    def economy(
        self,
        *,
        encounter_meaning: str,
        encounter_mode: str,
        encounter_description: str,
        statement_id: str | None = None,
        related_statement_ids: tuple[str, ...] = (),
        upstream_reference_ids: tuple[str, ...] = (),
        obligation_ids: tuple[str, ...] = (),
    ) -> "CountryProfileBuilder":
        return self.section(
            statement_id=statement_id,
            section_kind="economy",
            encounter_meaning=encounter_meaning,
            encounter_mode=encounter_mode,
            encounter_description=encounter_description,
            related_statement_ids=related_statement_ids,
            upstream_reference_ids=upstream_reference_ids,
            obligation_ids=obligation_ids,
        )

    def demographics(
        self,
        *,
        encounter_meaning: str,
        encounter_mode: str,
        encounter_description: str,
        statement_id: str | None = None,
        related_statement_ids: tuple[str, ...] = (),
        upstream_reference_ids: tuple[str, ...] = (),
        obligation_ids: tuple[str, ...] = (),
    ) -> "CountryProfileBuilder":
        return self.section(
            statement_id=statement_id,
            section_kind="demographics",
            encounter_meaning=encounter_meaning,
            encounter_mode=encounter_mode,
            encounter_description=encounter_description,
            related_statement_ids=related_statement_ids,
            upstream_reference_ids=upstream_reference_ids,
            obligation_ids=obligation_ids,
        )

    def section(
        self,
        *,
        section_kind: str,
        encounter_meaning: str,
        encounter_mode: str,
        encounter_description: str,
        statement_id: str | None = None,
        related_statement_ids: tuple[str, ...] = (),
        upstream_reference_ids: tuple[str, ...] = (),
        obligation_ids: tuple[str, ...] = (),
    ) -> "CountryProfileBuilder":
        """Add a country-profile statement through the existing package builder.

        ``section_kind`` is authoring context only. It is validated as non-empty
        but is not emitted as a runtime field because the frozen runtime model
        has no country-profile section object.
        """

        _require_non_blank(section_kind, "section_kind")
        self._builder.add_statement(
            statement_id=statement_id,
            encounter_meaning=encounter_meaning,
            belongs_to_purpose=f"{self._country_name} country-profile organizing purpose",
            encounter_mode=encounter_mode,
            encounter_description=encounter_description,
            related_statement_ids=related_statement_ids,
            upstream_reference_ids=upstream_reference_ids,
            obligation_ids=obligation_ids,
        )
        return self

    def build(self) -> CountryProfilePresentation:
        return CountryProfilePresentation(
            country_name=self._country_name,
            candidate=self._builder.build(),
        )


@dataclass(frozen=True)
class CountryComparisonPresentation:
    """Small semantic country-comparison authoring model.

    Like other Presentation Models, this object is not canonical runtime
    substance. It only exposes conversion to the existing Candidate
    Presentation Package produced by the existing builder.
    """

    compared_countries: tuple[str, ...]
    candidate: CandidatePresentationPackage

    def to_candidate_presentation_package(self) -> CandidatePresentationPackage:
        """Return the existing Candidate Presentation Package runtime object."""

        return self.candidate


class CountryComparisonBuilder:
    """Author a deliberately small country comparison with the existing builder."""

    def __init__(self, *, compared_countries: tuple[str, ...]) -> None:
        self._compared_countries = _require_country_pair(compared_countries)
        self._builder = PresentationPackageBuilder()

    def identity(
        self,
        *,
        title: str,
        purpose_summary: str,
        scope: str,
        non_scope: str,
        package_id: str | None = None,
    ) -> "CountryComparisonBuilder":
        self._builder.identity(
            package_id=package_id,
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
    ) -> "CountryComparisonBuilder":
        self._builder.organizing_purpose(statement=statement, scope=scope, non_scope=non_scope)
        return self

    def reference(
        self,
        *,
        owning_project: str,
        reference_kind: str,
        locator: str,
        owned_meaning: str,
        reference_id: str | None = None,
    ) -> "CountryComparisonBuilder":
        self._builder.add_upstream_reference(
            reference_id=reference_id,
            owning_project=owning_project,
            reference_kind=reference_kind,
            locator=locator,
            owned_meaning=owned_meaning,
        )
        return self

    def obligation(
        self,
        *,
        category: str,
        requirement: str,
        obligation_id: str | None = None,
        applies_to: tuple[str, ...] = (),
    ) -> "CountryComparisonBuilder":
        self._builder.add_obligation(
            obligation_id=obligation_id,
            category=category,
            requirement=requirement,
            applies_to=applies_to,
        )
        return self

    def overview(
        self,
        *,
        encounter_meaning: str,
        encounter_description: str,
        statement_id: str | None = None,
        related_statement_ids: tuple[str, ...] = (),
        upstream_reference_ids: tuple[str, ...] = (),
        obligation_ids: tuple[str, ...] = (),
    ) -> "CountryComparisonBuilder":
        return self.section(
            statement_id=statement_id,
            section_kind="overview",
            encounter_meaning=encounter_meaning,
            encounter_mode="comparison-orientation",
            encounter_description=encounter_description,
            related_statement_ids=related_statement_ids,
            upstream_reference_ids=upstream_reference_ids,
            obligation_ids=obligation_ids,
        )

    def indicator(
        self,
        *,
        indicator_name: str,
        encounter_meaning: str,
        encounter_description: str,
        statement_id: str | None = None,
        related_statement_ids: tuple[str, ...] = (),
        upstream_reference_ids: tuple[str, ...] = (),
        obligation_ids: tuple[str, ...] = (),
    ) -> "CountryComparisonBuilder":
        _require_non_blank(indicator_name, "indicator_name")
        return self.section(
            statement_id=statement_id,
            section_kind=f"indicator:{indicator_name}",
            encounter_meaning=encounter_meaning,
            encounter_mode="comparative-indicator",
            encounter_description=encounter_description,
            related_statement_ids=related_statement_ids,
            upstream_reference_ids=upstream_reference_ids,
            obligation_ids=obligation_ids,
        )

    def similarity(
        self,
        *,
        encounter_meaning: str,
        encounter_description: str,
        statement_id: str | None = None,
        related_statement_ids: tuple[str, ...] = (),
        upstream_reference_ids: tuple[str, ...] = (),
        obligation_ids: tuple[str, ...] = (),
    ) -> "CountryComparisonBuilder":
        return self.section(
            statement_id=statement_id,
            section_kind="similarity",
            encounter_meaning=encounter_meaning,
            encounter_mode="comparative-similarity",
            encounter_description=encounter_description,
            related_statement_ids=related_statement_ids,
            upstream_reference_ids=upstream_reference_ids,
            obligation_ids=obligation_ids,
        )

    def difference(
        self,
        *,
        encounter_meaning: str,
        encounter_description: str,
        statement_id: str | None = None,
        related_statement_ids: tuple[str, ...] = (),
        upstream_reference_ids: tuple[str, ...] = (),
        obligation_ids: tuple[str, ...] = (),
    ) -> "CountryComparisonBuilder":
        return self.section(
            statement_id=statement_id,
            section_kind="difference",
            encounter_meaning=encounter_meaning,
            encounter_mode="comparative-difference",
            encounter_description=encounter_description,
            related_statement_ids=related_statement_ids,
            upstream_reference_ids=upstream_reference_ids,
            obligation_ids=obligation_ids,
        )

    def section(
        self,
        *,
        section_kind: str,
        encounter_meaning: str,
        encounter_mode: str,
        encounter_description: str,
        statement_id: str | None = None,
        related_statement_ids: tuple[str, ...] = (),
        upstream_reference_ids: tuple[str, ...] = (),
        obligation_ids: tuple[str, ...] = (),
    ) -> "CountryComparisonBuilder":
        """Add a comparison statement through the existing package builder.

        ``section_kind`` and compared countries are authoring context only; they
        are not emitted as runtime fields because the frozen runtime has no
        comparison-specific object.
        """

        _require_non_blank(section_kind, "section_kind")
        comparison_label = " vs ".join(self._compared_countries)
        self._builder.add_statement(
            statement_id=statement_id,
            encounter_meaning=encounter_meaning,
            belongs_to_purpose=f"{comparison_label} country-comparison organizing purpose",
            encounter_mode=encounter_mode,
            encounter_description=encounter_description,
            related_statement_ids=related_statement_ids,
            upstream_reference_ids=upstream_reference_ids,
            obligation_ids=obligation_ids,
        )
        return self

    def build(self) -> CountryComparisonPresentation:
        return CountryComparisonPresentation(
            compared_countries=self._compared_countries,
            candidate=self._builder.build(),
        )


@dataclass(frozen=True)
class InvestmentThesisPresentation:
    """Small semantic investment-thesis authoring model.

    The model is authoring vocabulary only. Its conversion surface is the
    existing Candidate Presentation Package, not a new thesis runtime object.
    """

    subject: str
    candidate: CandidatePresentationPackage

    def to_candidate_presentation_package(self) -> CandidatePresentationPackage:
        """Return the existing Candidate Presentation Package runtime object."""

        return self.candidate


class InvestmentThesisBuilder:
    """Author a deliberately small investment thesis with the existing builder."""

    def __init__(self, *, subject: str) -> None:
        _require_non_blank(subject, "subject")
        self._subject = subject
        self._builder = PresentationPackageBuilder()

    def identity(
        self,
        *,
        title: str,
        purpose_summary: str,
        scope: str,
        non_scope: str,
        package_id: str | None = None,
    ) -> "InvestmentThesisBuilder":
        self._builder.identity(
            package_id=package_id,
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
    ) -> "InvestmentThesisBuilder":
        self._builder.organizing_purpose(statement=statement, scope=scope, non_scope=non_scope)
        return self

    def reference(
        self,
        *,
        owning_project: str,
        reference_kind: str,
        locator: str,
        owned_meaning: str,
        reference_id: str | None = None,
    ) -> "InvestmentThesisBuilder":
        self._builder.add_upstream_reference(
            reference_id=reference_id,
            owning_project=owning_project,
            reference_kind=reference_kind,
            locator=locator,
            owned_meaning=owned_meaning,
        )
        return self

    def obligation(
        self,
        *,
        category: str,
        requirement: str,
        obligation_id: str | None = None,
        applies_to: tuple[str, ...] = (),
    ) -> "InvestmentThesisBuilder":
        self._builder.add_obligation(
            obligation_id=obligation_id,
            category=category,
            requirement=requirement,
            applies_to=applies_to,
        )
        return self

    def thesis_statement(
        self,
        *,
        encounter_meaning: str,
        encounter_description: str,
        statement_id: str | None = None,
        related_statement_ids: tuple[str, ...] = (),
        upstream_reference_ids: tuple[str, ...] = (),
        obligation_ids: tuple[str, ...] = (),
    ) -> "InvestmentThesisBuilder":
        return self.section(
            statement_id=statement_id,
            section_kind="thesis-statement",
            encounter_meaning=encounter_meaning,
            encounter_mode="investment-thesis-claim",
            encounter_description=encounter_description,
            related_statement_ids=related_statement_ids,
            upstream_reference_ids=upstream_reference_ids,
            obligation_ids=obligation_ids,
        )

    def supporting_evidence(
        self,
        *,
        encounter_meaning: str,
        encounter_description: str,
        statement_id: str | None = None,
        related_statement_ids: tuple[str, ...] = (),
        upstream_reference_ids: tuple[str, ...] = (),
        obligation_ids: tuple[str, ...] = (),
    ) -> "InvestmentThesisBuilder":
        return self.section(
            statement_id=statement_id,
            section_kind="supporting-evidence",
            encounter_meaning=encounter_meaning,
            encounter_mode="investment-thesis-evidence",
            encounter_description=encounter_description,
            related_statement_ids=related_statement_ids,
            upstream_reference_ids=upstream_reference_ids,
            obligation_ids=obligation_ids,
        )

    def risk(
        self,
        *,
        encounter_meaning: str,
        encounter_description: str,
        statement_id: str | None = None,
        related_statement_ids: tuple[str, ...] = (),
        upstream_reference_ids: tuple[str, ...] = (),
        obligation_ids: tuple[str, ...] = (),
    ) -> "InvestmentThesisBuilder":
        return self.section(
            statement_id=statement_id,
            section_kind="risk",
            encounter_meaning=encounter_meaning,
            encounter_mode="investment-thesis-risk",
            encounter_description=encounter_description,
            related_statement_ids=related_statement_ids,
            upstream_reference_ids=upstream_reference_ids,
            obligation_ids=obligation_ids,
        )

    def counterargument(
        self,
        *,
        encounter_meaning: str,
        encounter_description: str,
        statement_id: str | None = None,
        related_statement_ids: tuple[str, ...] = (),
        upstream_reference_ids: tuple[str, ...] = (),
        obligation_ids: tuple[str, ...] = (),
    ) -> "InvestmentThesisBuilder":
        return self.section(
            statement_id=statement_id,
            section_kind="counterargument",
            encounter_meaning=encounter_meaning,
            encounter_mode="investment-thesis-counterargument",
            encounter_description=encounter_description,
            related_statement_ids=related_statement_ids,
            upstream_reference_ids=upstream_reference_ids,
            obligation_ids=obligation_ids,
        )

    def conclusion(
        self,
        *,
        encounter_meaning: str,
        encounter_description: str,
        statement_id: str | None = None,
        related_statement_ids: tuple[str, ...] = (),
        upstream_reference_ids: tuple[str, ...] = (),
        obligation_ids: tuple[str, ...] = (),
    ) -> "InvestmentThesisBuilder":
        return self.section(
            statement_id=statement_id,
            section_kind="conclusion",
            encounter_meaning=encounter_meaning,
            encounter_mode="investment-thesis-conclusion",
            encounter_description=encounter_description,
            related_statement_ids=related_statement_ids,
            upstream_reference_ids=upstream_reference_ids,
            obligation_ids=obligation_ids,
        )

    def section(
        self,
        *,
        section_kind: str,
        encounter_meaning: str,
        encounter_mode: str,
        encounter_description: str,
        statement_id: str | None = None,
        related_statement_ids: tuple[str, ...] = (),
        upstream_reference_ids: tuple[str, ...] = (),
        obligation_ids: tuple[str, ...] = (),
    ) -> "InvestmentThesisBuilder":
        """Add an investment-thesis statement through the existing builder.

        ``section_kind`` and subject are authoring context only. They are not
        emitted as runtime fields because the frozen runtime has no
        thesis-specific object.
        """

        _require_non_blank(section_kind, "section_kind")
        self._builder.add_statement(
            statement_id=statement_id,
            encounter_meaning=encounter_meaning,
            belongs_to_purpose=f"{self._subject} investment-thesis organizing purpose",
            encounter_mode=encounter_mode,
            encounter_description=encounter_description,
            related_statement_ids=related_statement_ids,
            upstream_reference_ids=upstream_reference_ids,
            obligation_ids=obligation_ids,
        )
        return self

    def build(self) -> InvestmentThesisPresentation:
        return InvestmentThesisPresentation(
            subject=self._subject,
            candidate=self._builder.build(),
        )


def _require_country_pair(value: object) -> tuple[str, ...]:
    if not isinstance(value, tuple) or len(value) != 2:
        raise PresentationPackageBuildRejected("Country comparison requires exactly two compared countries.")
    countries = tuple(country.strip() for country in value if isinstance(country, str) and country.strip())
    if len(countries) != 2:
        raise PresentationPackageBuildRejected("Country comparison countries must be non-empty text.")
    if countries[0] == countries[1]:
        raise PresentationPackageBuildRejected("Country comparison requires two distinct countries.")
    return countries


def _require_non_blank(value: object, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise PresentationPackageBuildRejected(f"Required presentation model field {field_name} must be non-empty text.")
