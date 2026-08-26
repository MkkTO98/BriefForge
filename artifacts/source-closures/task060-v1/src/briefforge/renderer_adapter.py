"""Renderer-adapter boundary for Ready Presentation Packages.

This module proves that renderer adapters can receive semantic package access
through a controlled boundary without becoming BriefForge semantic authorities.
It includes only bounded renderer proofs. It does not generalize rendering,
serialize, persist, export, network, template, map, search, route, dashboard,
or serve packages. Its static evidence exhibits remain renderer-local and non-canonical.
"""

from dataclasses import dataclass
from html import escape
import re

from .promotion import ReadyPresentationPackage


_ALLOWED_PACKAGE_FEATURES = frozenset(
    {
        "identity",
        "organizing_purpose",
        "statements",
        "upstream_references",
        "obligations",
        "validation_judgment",
        "semantic_fingerprint",
        "validation_policy_id",
    }
)


def _require_non_empty_text(value: object, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise RendererAdapterContractRejected(f"Renderer adapter contract requires non-empty {label}.")


class RendererAdapterContractRejected(ValueError):
    """Raised when a renderer-adapter contract declaration is malformed."""


@dataclass(frozen=True)
class RendererAdapterIdentity:
    """Stable declaration of the downstream adapter asking for semantic access."""

    adapter_id: str
    name: str
    version: str
    owner: str

    def __post_init__(self) -> None:
        _require_non_empty_text(self.adapter_id, "adapter_id")
        _require_non_empty_text(self.name, "name")
        _require_non_empty_text(self.version, "version")
        _require_non_empty_text(self.owner, "owner")


@dataclass(frozen=True)
class RendererAdapterCapability:
    """Declarative statement of package features an adapter can consume."""

    capability_id: str
    description: str
    package_features: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_non_empty_text(self.capability_id, "capability_id")
        _require_non_empty_text(self.description, "description")
        if not isinstance(self.package_features, tuple) or not self.package_features:
            raise RendererAdapterContractRejected(
                "Renderer adapter capability requires a non-empty tuple of package features."
            )
        for feature in self.package_features:
            _require_non_empty_text(feature, "package_feature")


@dataclass(frozen=True)
class RendererAdapterContract:
    """Declarative contract shape for checking adapter/package compatibility."""

    identity: RendererAdapterIdentity
    capabilities: tuple[RendererAdapterCapability, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.identity, RendererAdapterIdentity):
            raise RendererAdapterContractRejected("Renderer adapter contract requires stable adapter identity.")
        if not isinstance(self.capabilities, tuple) or not self.capabilities:
            raise RendererAdapterContractRejected(
                "Renderer adapter contract requires at least one declarative capability."
            )
        for capability in self.capabilities:
            if not isinstance(capability, RendererAdapterCapability):
                raise RendererAdapterContractRejected(
                    "Renderer adapter contract capabilities must be RendererAdapterCapability declarations."
                )


@dataclass(frozen=True)
class RendererAdapterCompatibility:
    """Result of comparing a Ready package with a renderer-adapter contract."""

    ready_package: ReadyPresentationPackage
    contract: RendererAdapterContract
    compatible: bool
    missing_package_features: tuple[str, ...] = ()


class RendererAdapterInvocationRejected(ValueError):
    """Raised when a renderer-adapter invocation cannot cross the boundary."""


@dataclass(frozen=True)
class RendererAdapterInvocation:
    """Metadata-only invocation record for a compatible adapter contract."""

    ready_package: ReadyPresentationPackage
    contract: RendererAdapterContract
    compatibility: RendererAdapterCompatibility


@dataclass(frozen=True)
class RendererAdapterInvocationResult:
    """Metadata-only result proving invocation occurred without rendering."""

    invocation: RendererAdapterInvocation
    accepted: bool
    adapter_identity: RendererAdapterIdentity
    package_identity: object
    semantic_fingerprint: str
    validation_policy_id: str


@dataclass(frozen=True)
class ToyPlainTextRenderedArtifact:
    """Deliberately bounded non-canonical plain-text rendering plus audit metadata."""

    plain_text: str
    adapter_identity: RendererAdapterIdentity
    package_identity: object
    semantic_fingerprint: str
    validation_policy_id: str

@dataclass(frozen=True)
class HtmlRenderedArtifact:
    """Deliberately bounded non-canonical static HTML output plus audit metadata."""

    html: str
    adapter_identity: RendererAdapterIdentity
    package_identity: object
    semantic_fingerprint: str
    validation_policy_id: str

@dataclass(frozen=True)
class RenderedArtifactConformance:

    """Downstream audit-link conformance result for rendered artifacts."""

    conforms: bool
    findings: tuple[str, ...]
    adapter_identity: RendererAdapterIdentity
    package_identity: object
    semantic_fingerprint: str
    validation_policy_id: str


class RenderedArtifactConformanceRejected(TypeError):
    """Raised when a rendered artifact cannot enter conformance checking."""


@dataclass(frozen=True)
class RendererAdapterRequest:
    """Read-only semantic request handed to downstream renderer adapters."""

    ready_package: ReadyPresentationPackage

    @property
    def identity(self):
        return self.ready_package.candidate.identity

    @property
    def organizing_purpose(self):
        return self.ready_package.candidate.organizing_purpose

    @property
    def statements(self):
        return self.ready_package.candidate.statements

    @property
    def upstream_references(self):
        return self.ready_package.candidate.upstream_references

    @property
    def obligations(self):
        return self.ready_package.candidate.obligations

    @property
    def validation_judgment(self):
        return self.ready_package.validation_judgment

    @property
    def semantic_fingerprint(self):
        return self.ready_package.semantic_fingerprint

    @property
    def validation_policy_id(self):
        return self.ready_package.validation_policy_id


@dataclass(frozen=True)
class MinimalHtmlProjectionIdentity:
    """Renderer-owned identity view for a non-legacy BCRP projection."""

    package_id: str
    title: str
    purpose_summary: str


@dataclass(frozen=True)
class MinimalHtmlProjectionPurpose:
    statement: str
    non_scope: str


@dataclass(frozen=True)
class MinimalHtmlProjectionEncounter:
    mode: str
    description: str


@dataclass(frozen=True)
class MinimalHtmlProjectionStatement:
    statement_id: str
    encounter_meaning: str
    encounter_semantics: MinimalHtmlProjectionEncounter
    authority_ref: str
    upstream_reference_ids: tuple[str, ...]
    obligation_ids: tuple[str, ...]


@dataclass(frozen=True)
class MinimalHtmlProjectionReference:
    reference_id: str
    owning_project: str
    reference_kind: str
    locator: str
    owned_meaning: str
    provenance_ref: str
    provenance_citation: str


@dataclass(frozen=True)
class MinimalHtmlProjectionObligation:
    obligation_id: str
    category: str
    requirement: str
    authority_ref: str
    applies_to: tuple[str, ...]


@dataclass(frozen=True)
class MinimalHtmlRendererProjection:
    """Exact renderer input projected from a verified BCRP Plan.

    This is not a Ready package and grants no validation, release, conformance,
    Manifest, distribution, or publication authority.
    """

    identity: MinimalHtmlProjectionIdentity
    organizing_purpose: MinimalHtmlProjectionPurpose
    statements: tuple[MinimalHtmlProjectionStatement, ...]
    upstream_references: tuple[MinimalHtmlProjectionReference, ...]
    obligations: tuple[MinimalHtmlProjectionObligation, ...]
    semantic_fingerprint: str
    validation_policy_id: str
    consumed_mapping_ids: tuple[str, ...]
    selected_expression_modes: tuple[str, ...]
    fingerprint: str


@dataclass(frozen=True)
class _MinimalHtmlProjectionInvocation:
    adapter_identity: RendererAdapterIdentity
    package_identity: MinimalHtmlProjectionIdentity
    semantic_fingerprint: str
    validation_policy_id: str


class RendererAdapterRejected(TypeError):
    """Raised when a non-ready object attempts to enter the renderer-adapter boundary."""


def prepare_renderer_adapter_request(ready_package: ReadyPresentationPackage) -> RendererAdapterRequest:
    """Prepare read-only semantic access for downstream renderer adapters only."""

    if not isinstance(ready_package, ReadyPresentationPackage):
        raise RendererAdapterRejected("Only Ready Presentation Packages may enter the renderer-adapter boundary.")

    return RendererAdapterRequest(ready_package=ready_package)


def check_renderer_adapter_compatibility(
    ready_package: ReadyPresentationPackage,
    contract: RendererAdapterContract,
) -> RendererAdapterCompatibility:
    """Check declared adapter needs against a Ready package without rendering."""

    request = prepare_renderer_adapter_request(ready_package)
    if not isinstance(contract, RendererAdapterContract):
        raise RendererAdapterContractRejected("Renderer adapter compatibility check requires a valid contract.")

    required_features = tuple(
        feature
        for capability in contract.capabilities
        for feature in capability.package_features
    )
    missing_features = tuple(
        feature
        for feature in required_features
        if feature not in _ALLOWED_PACKAGE_FEATURES or not hasattr(request, feature)
    )

    return RendererAdapterCompatibility(
        ready_package=ready_package,
        contract=contract,
        compatible=not missing_features,
        missing_package_features=missing_features,
    )


def invoke_renderer_adapter(
    ready_package: ReadyPresentationPackage,
    contract: RendererAdapterContract,
) -> RendererAdapterInvocationResult:
    """Invoke a compatible renderer adapter boundary without rendering."""

    compatibility = check_renderer_adapter_compatibility(ready_package, contract)
    if not compatibility.compatible:
        raise RendererAdapterInvocationRejected("Cannot invoke incompatible renderer adapter contract.")

    invocation = RendererAdapterInvocation(
        ready_package=ready_package,
        contract=contract,
        compatibility=compatibility,
    )
    return RendererAdapterInvocationResult(
        invocation=invocation,
        accepted=True,
        adapter_identity=contract.identity,
        package_identity=ready_package.candidate.identity,
        semantic_fingerprint=ready_package.semantic_fingerprint,
        validation_policy_id=ready_package.validation_policy_id,
    )


def toy_plain_text_renderer_contract() -> RendererAdapterContract:
    """Return the one deliberately bounded toy renderer contract."""

    return RendererAdapterContract(
        identity=RendererAdapterIdentity(
            adapter_id="toy-plain-text-renderer",
            name="Toy Plain Text Renderer",
            version="0.1.0",
            owner="BriefForge architecture proof",
        ),
        capabilities=(
            RendererAdapterCapability(
                capability_id="toy-plain-text-ready-package-read",
                description="Reads only the Ready package fields needed for bounded plain-text proof output.",
                package_features=(
                    "identity",
                    "organizing_purpose",
                    "statements",
                    "semantic_fingerprint",
                    "validation_policy_id",
                ),
            ),
        ),
    )


def render_toy_plain_text(
    ready_package: ReadyPresentationPackage,
    contract: RendererAdapterContract | None = None,
) -> ToyPlainTextRenderedArtifact:
    """Render one bounded, non-canonical plain-text artifact from a Ready package.

    This is a toy proof only. It consumes semantic content downstream from
    readiness, emits plain text, and returns audit metadata. It does not validate,
    promote, reinterpret, persist, export, template, visualize, map, chart,
    network, serve, or create browser/HTML/PDF output.
    """

    selected_contract = contract if contract is not None else toy_plain_text_renderer_contract()
    expected_contract = toy_plain_text_renderer_contract()
    if selected_contract != expected_contract:
        raise RendererAdapterInvocationRejected("Toy plain-text rendering requires the toy renderer contract.")

    invocation = invoke_renderer_adapter(ready_package, selected_contract)
    request = RendererAdapterRequest(ready_package=ready_package)
    statement_lines = tuple(
        f"- {statement.statement_id}: {statement.encounter_meaning}"
        for statement in request.statements
    )
    plain_text = "\n".join(
        (
            f"Title: {request.identity.title}",
            f"Purpose: {request.organizing_purpose.statement}",
            "Statements:",
            *statement_lines,
        )
    )

    return ToyPlainTextRenderedArtifact(
        plain_text=plain_text,
        adapter_identity=invocation.adapter_identity,
        package_identity=invocation.package_identity,
        semantic_fingerprint=invocation.semantic_fingerprint,
        validation_policy_id=invocation.validation_policy_id,
    )


def html_renderer_contract() -> RendererAdapterContract:
    """Return the one deliberately bounded minimal HTML renderer contract."""

    return RendererAdapterContract(
        identity=RendererAdapterIdentity(
            adapter_id="minimal-html-renderer",
            name="Minimal HTML Renderer",
            version="0.2.0",
            owner="BriefForge architecture proof",
        ),
        capabilities=(
            RendererAdapterCapability(
                capability_id="minimal-html-bounded-input-read",
                description="Reads the bounded semantic fields needed from either governed legacy Ready input or an exact verified BCRP Plan projection.",
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


def _html_escape(value: object) -> str:
    return escape(str(value), quote=True)


def _html_text(value: object) -> str:
    return escape(str(value), quote=False)


def _inline_source_markup(text: str) -> str:
    """Render conservative inline source markup without interpreting meaning."""

    escaped = _html_text(text)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)


def _source_block_role(label: str) -> str:
    normalized = label.lower()
    if any(term in normalized for term in ("why not accepted", "missing evidence", "risk", "failure mode", "caveat", "alternative explanation")):
        return "caveat"
    if any(term in normalized for term in ("method", "assumption", "controlled pressure test", "evidence requirement", "activation path")):
        return "methodology"
    if any(term in normalized for term in ("recommendation", "preferred choice", "conclusion", "assessment")):
        return "recommendation"
    return "section"


def _source_table_present(lines: tuple[str, ...]) -> bool:
    for index, line in enumerate(lines[:-1]):
        if line.strip().startswith("|") and line.strip().endswith("|"):
            separator = lines[index + 1].strip()
            if separator.startswith("|") and set(separator.replace("|", "").replace("-", "").replace(":", "").strip()) == set():
                return True
    return False


def _render_source_list(lines: list[str], ordered: bool) -> str:
    tag = "ol" if ordered else "ul"
    stack_depth = 0
    output: list[str] = []
    for raw in lines:
        stripped = raw.lstrip()
        indent = len(raw) - len(stripped)
        depth = indent // 2 + 1
        marker_text = re.sub(r"^(?:[-*+] |\d+\.\s+)", "", stripped).strip()
        while stack_depth < depth:
            if not ordered and stack_depth == 0:
                output.append('<ul data-source-list="unordered">')
            elif not ordered:
                output.append('<ul data-source-list="unordered-nested">')
            else:
                output.append('<ol data-source-list="ordered">')
            stack_depth += 1
        while stack_depth > depth:
            output.append(f"</{tag}>")
            stack_depth -= 1
        output.append(f"<li>{_inline_source_markup(marker_text)}</li>")
    while stack_depth:
        output.append(f"</{tag}>")
        stack_depth -= 1
    return "".join(output)


def _render_source_table(lines: list[str]) -> str:
    header = [cell.strip() for cell in lines[0].strip().strip("|").split("|")]
    body_lines = lines[2:]
    head = "".join(f"<th>{_inline_source_markup(cell)}</th>" for cell in header)
    rows = []
    for raw in body_lines:
        cells = [cell.strip() for cell in raw.strip().strip("|").split("|")]
        rows.append("<tr>" + "".join(f"<td>{_inline_source_markup(cell)}</td>" for cell in cells) + "</tr>")
    return '<table data-source-structure="table"><thead><tr>' + head + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>"


def _render_source_structured_text(text: str) -> str:
    """Preserve renderer-visible source structure already present in text.

    This is a bounded renderer-side markdown subset. It only preserves concrete
    upstream structure present in the statement text; it does not infer new
    claims, sections, source metadata, or semantic package fields.
    """

    lines = tuple(str(text).splitlines())
    tables_present = _source_table_present(lines)
    output: list[str] = [
        f'<div data-source-structure="preserved-v0.1" data-source-tables="{"present" if tables_present else "absent"}">'
    ]
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            output.append("<p>" + " ".join(_inline_source_markup(part.strip()) for part in paragraph if part.strip()) + "</p>")
            paragraph.clear()

    index = 0
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped:
            flush_paragraph()
            index += 1
            continue

        if stripped.startswith("|") and index + 1 < len(lines) and lines[index + 1].strip().startswith("|") and "---" in lines[index + 1]:
            flush_paragraph()
            table_lines = [raw]
            index += 1
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            output.append(_render_source_table(table_lines))
            continue

        if stripped.startswith("> "):
            flush_paragraph()
            quote_lines = []
            while index < len(lines) and lines[index].strip().startswith("> "):
                quote_lines.append(lines[index].strip()[2:].strip())
                index += 1
            output.append("<blockquote>" + " ".join(_inline_source_markup(part) for part in quote_lines) + "</blockquote>")
            continue

        if re.match(r"^\s*[-*+]\s+", raw):
            flush_paragraph()
            list_lines = []
            while index < len(lines) and re.match(r"^\s*[-*+]\s+", lines[index]):
                list_lines.append(lines[index])
                index += 1
            output.append(_render_source_list(list_lines, ordered=False))
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading_match:
            flush_paragraph()
            level = min(len(heading_match.group(1)) + 2, 6)
            label = heading_match.group(2).strip()
            output.append(f"<h{level} data-source-block=\"{_html_escape(_source_block_role(label))}\">{_inline_source_markup(label)}</h{level}>")
            index += 1
            continue

        if stripped.endswith(":") and len(stripped) <= 96:
            flush_paragraph()
            label = stripped[:-1]
            output.append(f"<h4 data-source-block=\"{_html_escape(_source_block_role(label))}\">{_inline_source_markup(label)}</h4>")
            index += 1
            continue

        if index == 0 and len(stripped) <= 140:
            flush_paragraph()
            output.append(f"<h4 data-source-block=\"{_html_escape(_source_block_role(stripped))}\">{_inline_source_markup(stripped)}</h4>")
            index += 1
            continue

        if re.match(r"^\s*\d+\.\s+", raw):
            flush_paragraph()
            list_lines = []
            while index < len(lines) and re.match(r"^\s*\d+\.\s+", lines[index]):
                list_lines.append(lines[index])
                index += 1
            output.append(_render_source_list(list_lines, ordered=True))
            continue

        paragraph.append(raw)
        index += 1

    flush_paragraph()
    output.append("</div>")
    return "".join(output)


def _source_title(text: str) -> str:
    for line in str(text).splitlines():
        stripped = line.strip()
        if stripped:
            if stripped.startswith("#"):
                return re.sub(r"^#+\s+", "", stripped).strip()
            return stripped.rstrip(":")
    return "Evidence"


def _source_key_value_pairs(text: str) -> tuple[tuple[str, str], ...]:
    pairs: list[tuple[str, str]] = []
    for raw in str(text).splitlines()[1:]:
        stripped = raw.strip()
        if not stripped or stripped.startswith("|") or stripped.startswith("-") or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        label, value = stripped.split(":", 1)
        label = label.strip()
        value = value.strip()
        if label and value and len(label) <= 48:
            pairs.append((label, value))
    return tuple(pairs)


def _source_markdown_table_blocks(text: str) -> tuple[tuple[str, tuple[str, ...]], ...]:
    lines = tuple(str(text).splitlines())
    title = _source_title(text)
    tables: list[tuple[str, tuple[str, ...]]] = []
    index = 0
    while index < len(lines):
        if lines[index].strip().startswith("|") and index + 1 < len(lines) and lines[index + 1].strip().startswith("|") and "---" in lines[index + 1]:
            table_lines: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            tables.append((title, tuple(table_lines)))
            continue
        index += 1
    return tuple(tables)


def _table_exhibit_type(table_lines: tuple[str, ...]) -> str:
    header = table_lines[0].lower() if table_lines else ""
    if all(term in header for term in ("territory", "period", "value")):
        return "comparison-table"
    return "small-statistical-table"


def _table_shape(table_lines: tuple[str, ...]) -> tuple[int, int]:
    if not table_lines:
        return (0, 0)
    columns = len([cell for cell in table_lines[0].strip().strip("|").split("|")])
    rows = max(len(table_lines) - 2, 0)
    return rows, columns




def _parse_source_table(table_lines: tuple[str, ...]) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
    if len(table_lines) < 3:
        return (), ()
    headers = tuple(cell.strip() for cell in table_lines[0].strip().strip("|").split("|"))
    rows: list[tuple[str, ...]] = []
    for raw in table_lines[2:]:
        cells = tuple(cell.strip() for cell in raw.strip().strip("|").split("|"))
        if len(cells) == len(headers):
            rows.append(cells)
    return headers, tuple(rows)


def _period_sort_key(period: str) -> tuple[int, int]:
    normalized = period.strip().replace(" ", "-").upper()
    month_match = re.match(r"^(\d{4})-M(\d{1,2})$", normalized)
    if month_match:
        return int(month_match.group(1)), int(month_match.group(2))
    quarter_match = re.match(r"^(\d{4})-?Q([1-4])$", normalized)
    if quarter_match:
        return int(quarter_match.group(1)), int(quarter_match.group(2)) * 3
    year_match = re.match(r"^(\d{4})$", normalized)
    if year_match:
        return int(year_match.group(1)), 12
    raise ValueError("unsupported period")


def _time_series_points_from_table(table_lines: tuple[str, ...]) -> tuple[tuple[str, float], ...]:
    headers, rows = _parse_source_table(table_lines)
    lower_headers = tuple(header.lower() for header in headers)
    if "period" not in lower_headers or "value" not in lower_headers:
        return ()
    period_index = lower_headers.index("period")
    value_index = lower_headers.index("value")
    comparable_columns = [
        index
        for index, header in enumerate(lower_headers)
        if index not in {period_index, value_index} and header not in {"unit", "frequency"}
    ]
    for index in comparable_columns:
        if len({row[index] for row in rows if row[index]}) > 1:
            return ()
    points: list[tuple[str, float]] = []
    for row in rows:
        period = row[period_index].strip()
        value_text = row[value_index].replace(",", "").strip()
        try:
            _period_sort_key(period)
            value = float(value_text)
        except ValueError:
            return ()
        points.append((period, value))
    if len(points) < 3:
        return ()
    unique_periods = {period for period, _value in points}
    if len(unique_periods) != len(points):
        return ()
    return tuple(sorted(points, key=lambda item: _period_sort_key(item[0])))


def _source_unit_from_table(table_lines: tuple[str, ...]) -> str:
    headers, rows = _parse_source_table(table_lines)
    lower_headers = tuple(header.lower() for header in headers)
    if "unit" not in lower_headers:
        return "value"
    unit_index = lower_headers.index("unit")
    units = tuple(row[unit_index] for row in rows if row[unit_index])
    return units[0] if units and len(set(units)) == 1 else "value"


def _render_static_svg_time_series_exhibit(title: str, statement_id: str, table_lines: tuple[str, ...]) -> str:
    points = _time_series_points_from_table(table_lines)
    if not points:
        return ""
    width = 640
    height = 260
    left = 54
    right = 24
    top = 24
    bottom = 44
    plot_width = width - left - right
    plot_height = height - top - bottom
    values = tuple(value for _period, value in points)
    min_value = min(values)
    max_value = max(values)
    value_range = max_value - min_value or 1.0
    svg_points: list[str] = []
    for index, (_period, value) in enumerate(points):
        x = left + (plot_width * index / max(len(points) - 1, 1))
        y = top + plot_height - ((value - min_value) / value_range * plot_height)
        svg_points.append(f"{x:.1f},{y:.1f}")
    first_period, first_value = points[0]
    last_period, last_value = points[-1]
    unit = _source_unit_from_table(table_lines)
    point_markers = "".join(
        f'<circle cx="{pair.split(",")[0]}" cy="{pair.split(",")[1]}" r="2.8"><title>{_html_text(period)}: {_html_text(value)} {_html_text(unit)}</title></circle>'
        for pair, (period, value) in zip(svg_points, points)
    )
    return (
        '<aside data-renderer-exhibit="static-v0.1" data-exhibit-type="time-series-svg" '
        'data-visualization-class="time-series" data-exhibit-inference="renderer-side-existing-evidence" '
        'data-exhibit-policy="no-runtime-object" data-svg-policy="static-only" '
        f'data-exhibit-source-statement="{_html_escape(statement_id)}">'
        f'<h4>Evidence exhibit: {_html_text(title)}</h4>'
        '<figure class="time-series-figure">'
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Static time-series exhibit for {_html_escape(title)}">'
        f'<line x1="{left}" y1="{top + plot_height}" x2="{width - right}" y2="{top + plot_height}" stroke="#6b7280" stroke-width="1" />'
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#6b7280" stroke-width="1" />'
        f'<polyline points="{" ".join(svg_points)}" fill="none" stroke="#174ea6" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'
        + point_markers +
        f'<text x="{left}" y="{height - 14}">{_html_text(first_period)}</text>'
        f'<text x="{width - right - 72}" y="{height - 14}">{_html_text(last_period)}</text>'
        f'<text x="{left}" y="18">{_html_text(f"{max_value:g} {unit}")}</text>'
        f'<text x="{left}" y="{top + plot_height - 6}">{_html_text(f"{min_value:g} {unit}")}</text>'
        '</svg>'
        f'<figcaption>{len(points)} observed source periods; first value {first_value:g} {unit}, last value {last_value:g} {unit}. Static SVG generated downstream from existing table evidence only.</figcaption>'
        '</figure>'
        '</aside>'
    )


def _render_static_exhibits(statement) -> str:
    exhibits: list[str] = []
    pairs = _source_key_value_pairs(statement.encounter_meaning)
    if len(pairs) >= 3 and not _source_markdown_table_blocks(statement.encounter_meaning):
        items = "".join(
            "<li>"
            f"<span class=\"exhibit-label\">{_html_text(label)}</span>"
            f"<strong>{_html_text(value)}</strong>"
            "</li>"
            for label, value in pairs[:6]
        )
        exhibits.append(
            "<aside data-renderer-exhibit=\"static-v0.1\" data-exhibit-type=\"key-number\" "
            "data-exhibit-inference=\"renderer-side-existing-evidence\" data-exhibit-policy=\"no-runtime-object\" "
            f"data-exhibit-source-statement=\"{_html_escape(statement.statement_id)}\">"
            f"<h4>Evidence exhibit: {_html_text(_source_title(statement.encounter_meaning))}</h4>"
            "<ul class=\"exhibit-key-grid\">" + items + "</ul>"
            "<p>Static key-number exhibit derived only from existing source lines.</p>"
            "</aside>"
        )

    time_series_rendered = False
    for title, table_lines in _source_markdown_table_blocks(statement.encounter_meaning):
        if not time_series_rendered:
            time_series_exhibit = _render_static_svg_time_series_exhibit(title, statement.statement_id, table_lines)
            if time_series_exhibit:
                exhibits.append(time_series_exhibit)
                time_series_rendered = True
        rows, columns = _table_shape(table_lines)
        exhibit_type = _table_exhibit_type(table_lines)
        exhibits.append(
            "<aside data-renderer-exhibit=\"static-v0.1\" "
            f"data-exhibit-type=\"{_html_escape(exhibit_type)}\" "
            "data-exhibit-inference=\"renderer-side-existing-evidence\" data-exhibit-policy=\"no-runtime-object\" "
            f"data-exhibit-source-statement=\"{_html_escape(statement.statement_id)}\">"
            f"<h4>Evidence exhibit: {_html_text(title)}</h4>"
            f"<p>{rows} rows × {columns} columns preserved from the source table.</p>"
            + _render_source_table(list(table_lines)) +
            "<p>Static table exhibit; no chart object, script, or runtime exhibit object is introduced.</p>"
            "</aside>"
        )
    return "".join(exhibits)


def _request_has_static_exhibits(request: RendererAdapterRequest) -> bool:
    return any(_render_static_exhibits(statement) for statement in request.statements)


def _render_static_exhibit_region(request: RendererAdapterRequest) -> str:
    exhibit_statements = [statement for statement in request.statements if _render_static_exhibits(statement)]
    if not exhibit_statements:
        return '<section data-exhibit-region="none-detected" data-attention="supporting"><h2>Evidence exhibits</h2><p>No renderer-visible exhibit candidates detected in existing source evidence.</p></section>'
    links = "".join(
        f"<li><a href=\"#statement-{_html_escape(statement.statement_id)}\">{_html_text(statement.statement_id)}</a></li>"
        for statement in exhibit_statements
    )
    return (
        '<section data-exhibit-region="static-v0.1" data-attention="supporting">'
        '<h2>Evidence exhibits</h2>'
        '<p>Renderer-side static exhibits detected from existing evidence only.</p>'
        '<ol>' + links + '</ol>'
        '</section>'
    )


def _static_reader_experience_css() -> str:
    """Return bounded static CSS for reader comfort.

    This is renderer-level readability polish justified by RB-001. It is not a
    template system, CSS framework, design system, browser app, dashboard,
    JavaScript behavior, visualization layer, or semantic/runtime change.
    """

    return """<style>
:root {
  color-scheme: light;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #f6f4ef;
  color: #1f2933;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: #f6f4ef; }
main {
  max-width: 980px;
  margin: 0 auto;
  padding: 48px 28px 72px;
  line-height: 1.62;
  font-size: 17px;
}
a { color: #174ea6; text-decoration-thickness: 0.08em; text-underline-offset: 0.18em; }
h1, h2, h3, h4 { color: #111827; line-height: 1.18; margin: 0 0 0.65em; }
h1 { font-size: clamp(2rem, 5vw, 3.4rem); letter-spacing: -0.04em; }
h2 { font-size: 1.55rem; margin-top: 1.6em; border-bottom: 1px solid #d9d5cc; padding-bottom: 0.35em; }
h3 { font-size: 1.02rem; letter-spacing: 0.08em; text-transform: uppercase; color: #53606f; }
h4 { font-size: 1rem; color: #243b53; margin-top: 1.4em; }
p, li { max-width: 76ch; }
blockquote { border-left: 4px solid #8a6d3b; margin: 1em 0; padding: 0.5em 1em; background: #f8fafc; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.95rem; }
[data-renderer-exhibit="static-v0.1"] { background: #f0f7ff; border: 1px solid #b6d4fe; border-radius: 14px; padding: 18px; margin: 1em 0 1.2em; }
[data-renderer-exhibit="static-v0.1"] h4 { margin-top: 0; color: #174ea6; }
.exhibit-key-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; list-style: none; margin: 1em 0; padding: 0; }
.exhibit-key-grid li { background: #fff; border: 1px solid #d7e7ff; border-radius: 10px; padding: 12px; }
.exhibit-label { display: block; color: #53606f; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; }
th, td { border: 1px solid #d9d5cc; padding: 0.55em 0.7em; text-align: left; vertical-align: top; }
th { background: #eef2f7; }
[data-source-structure="preserved-v0.1"] ul, [data-source-structure="preserved-v0.1"] ol { margin: 0.7em 0 1em 1.25em; padding-left: 1.1em; }
[data-source-block="caveat"] { color: #7c2d12; }
[data-source-block="methodology"] { color: #5f3dc4; }
[data-source-block="recommendation"] { color: #166534; }
header, section, article, nav, details {
  background: #fffdf8;
  border: 1px solid #e3dfd5;
  border-radius: 16px;
  padding: 24px;
  margin: 22px 0;
  box-shadow: 0 1px 2px rgba(17, 24, 39, 0.04);
}
header { border-top: 6px solid #243b53; }
article { padding: 22px; border-left: 4px solid #d0d7de; }
article[data-attention="primary"] { border-left-color: #174ea6; }
article[data-attention="supporting"] { border-left-color: #8a6d3b; }
nav ol, nav ul { columns: 2; column-gap: 40px; }
[data-attention="primary"] > h2, [data-attention="primary"] > h3 { color: #0f3f8f; }
section { border-left: 6px solid #d0d7de; }
details { background: #f8fafc; }
summary { cursor: pointer; font-weight: 700; }
code { background: #eef2f7; border-radius: 4px; padding: 0.1em 0.25em; }
@media (max-width: 720px) {
  main { padding: 24px 14px 48px; font-size: 16px; }
  header, section, article, nav, details { padding: 18px; border-radius: 12px; }
  nav ol, nav ul { columns: 1; }
}
</style>"""


def _statement_attention(mode: str) -> str:
    normalized = mode.lower()
    if normalized in {"orientation", "synthesis", "thesis", "conclusion"}:
        return "primary"
    if "risk" in normalized or "caveat" in normalized or "counter" in normalized:
        return "supporting"
    return "secondary"


def _statement_stage(mode: str) -> str:
    normalized = mode.lower()
    if normalized == "orientation":
        return "state-main-point"
    if normalized == "synthesis" or "conclusion" in normalized:
        return "close"
    if "risk" in normalized or "caveat" in normalized or "counter" in normalized:
        return "qualify"
    return "elaborate"


def _linked_reference_items(statement, references_by_id: dict[str, object], compact: bool = False) -> str:
    items = []
    for reference_id in statement.upstream_reference_ids:
        reference = references_by_id.get(reference_id)
        label = reference.reference_kind if reference is not None else reference_id
        if compact:
            items.append(
                "<li>"
                f"<a href=\"#reference-{_html_escape(reference_id)}\">{_html_text(reference_id)}</a>"
                "</li>"
            )
        else:
            items.append(
                "<li>"
                f"<a href=\"#reference-{_html_escape(reference_id)}\">{_html_text(reference_id)}</a>"
                f" <span>Source owner: {_html_text(reference.owning_project if reference is not None else 'unknown')}</span>"
                f" <span>Kind: {_html_text(label)}</span>"
                "</li>"
            )
    if not items:
        return ""
    heading = "Evidence links" if compact else "Evidence-linked references"
    return f"<div data-attention=\"supporting\"><p>{heading}</p><ul>" + "".join(items) + "</ul></div>"


def _linked_obligation_items(statement, obligations_by_id: dict[str, object], compact: bool = False) -> str:
    items = []
    for obligation_id in statement.obligation_ids:
        obligation = obligations_by_id.get(obligation_id)
        label = obligation.category if obligation is not None else obligation_id
        if compact:
            items.append(
                "<li>"
                f"<a href=\"#obligation-{_html_escape(obligation_id)}\">{_html_text(obligation_id)}</a>"
                "</li>"
            )
        else:
            items.append(
                "<li>"
                f"<a href=\"#obligation-{_html_escape(obligation_id)}\">{_html_text(obligation_id)}</a>"
                f" <span>{_html_text(label)}</span>"
                "</li>"
            )
    if not items:
        return ""
    heading = "Obligation links" if compact else "Contextual obligations"
    return f"<div data-attention=\"supporting\"><p>{heading}</p><ul>" + "".join(items) + "</ul></div>"


def _render_statement_article(
    statement,
    references_by_id: dict[str, object],
    obligations_by_id: dict[str, object],
    compact_links: bool = False,
) -> str:
    attention = _statement_attention(statement.encounter_semantics.mode)
    stage = _statement_stage(statement.encounter_semantics.mode)
    return "\n".join(
        (
            f"<article id=\"statement-{_html_escape(statement.statement_id)}\" data-statement-id=\"{_html_escape(statement.statement_id)}\" data-grammar-stage=\"{_html_escape(stage)}\" data-attention=\"{_html_escape(attention)}\">",
            f"<h3>{_html_text(statement.encounter_semantics.mode.replace('-', ' ').title())}</h3>",
            _render_static_exhibits(statement),
            _render_source_structured_text(statement.encounter_meaning),
            (
                f"<p data-attention=\"supporting\">Authority: {_html_text(statement.authority_ref)}</p>"
                if getattr(statement, "authority_ref", "") else ""
            ),
            f"<p data-attention=\"supporting\">Reader role: {_html_text(statement.encounter_semantics.description)}</p>",
            _linked_reference_items(statement, references_by_id, compact=compact_links),
            _linked_obligation_items(statement, obligations_by_id, compact=compact_links),
            "</article>",
        )
    )


def _is_long_document(request: RendererAdapterRequest) -> bool:
    return len(request.statements) >= 12


def _render_long_document_outline(request: RendererAdapterRequest) -> str:
    close_links = "".join(
        f"<li><a href=\"#statement-{_html_escape(statement.statement_id)}\">{_html_text(statement.statement_id)}</a></li>"
        for statement in request.statements
        if _statement_stage(statement.encounter_semantics.mode) == "close"
    )
    close_section = "" if not close_links else "<p>Recommendation recovery</p><ul>" + close_links + "</ul>"
    return "\n".join(
        (
            "<nav aria-label=\"Long-document structure\" data-attention=\"secondary\">",
            "<h2>Long-document structure</h2>",
            "<ol>",
            "<li><a href=\"#long-document-region-core-narrative\">Core Narrative</a></li>",
            "<li><a href=\"#long-document-region-supporting-evidence\">Supporting Evidence</a></li>",
            "<li><a href=\"#long-document-region-references\">References</a></li>",
            "<li><a href=\"#long-document-region-obligations\">Obligations</a></li>",
            "<li><a href=\"#long-document-region-audit-metadata\">Audit Metadata</a></li>",
            "</ol>",
            close_section,
            "</nav>",
        )
    )


def _render_reference_inventory(references: tuple[object, ...], long_document: bool = False) -> str:
    items = []
    for reference in references:
        items.append(
            "\n".join(
                (
                    f"<li id=\"reference-{_html_escape(reference.reference_id)}\" data-reference-id=\"{_html_escape(reference.reference_id)}\">",
                    f"<p><strong>{_html_text(reference.reference_id)}</strong></p>",
                    f"<p>Source owner: {_html_text(reference.owning_project)}</p>",
                    f"<p>Kind: {_html_text(reference.reference_kind)}</p>",
                    f"<p>Locator: {_html_text(reference.locator)}</p>",
                    f"<p>Owned meaning: {_html_text(reference.owned_meaning)}</p>",
                    (
                        f"<p>Provenance: {_html_text(reference.provenance_ref)} — {_html_text(reference.provenance_citation)}</p>"
                        if getattr(reference, "provenance_ref", "") else ""
                    ),
                    "</li>",
                )
            )
        )
    region_attrs = (
        " id=\"long-document-region-references\" data-long-document-region=\"references\""
        if long_document
        else ""
    )
    return f"<section{region_attrs} data-grammar-stage=\"trace\" data-attention=\"supporting\"><h2>Reference inventory</h2><ol>" + "".join(items) + "</ol></section>"


def _render_obligation_inventory(obligations: tuple[object, ...], long_document: bool = False) -> str:
    items = []
    for obligation in obligations:
        applies_to = ", ".join(obligation.applies_to) if obligation.applies_to else "whole package"
        items.append(
            "\n".join(
                (
                    f"<li id=\"obligation-{_html_escape(obligation.obligation_id)}\" data-obligation-id=\"{_html_escape(obligation.obligation_id)}\">",
                    f"<p><strong>{_html_text(obligation.category)}</strong>: {_html_text(obligation.requirement)}</p>",
                    (
                        f"<p>Authority: {_html_text(obligation.authority_ref)}</p>"
                        if getattr(obligation, "authority_ref", "") else ""
                    ),
                    f"<p>Applies to: {_html_text(applies_to)}</p>",
                    "</li>",
                )
            )
        )
    region_attrs = (
        " id=\"long-document-region-obligations\" data-long-document-region=\"obligations\""
        if long_document
        else ""
    )
    heading = "Grouped obligations" if long_document else "Obligation inventory"
    return f"<section{region_attrs} data-grammar-stage=\"trace\" data-attention=\"supporting\"><h2>Obligation inventory</h2><p>{heading}</p><ol>" + "".join(items) + "</ol></section>"


def _render_uncertainty_section(request: RendererAdapterRequest, long_document: bool = False) -> str:
    qualifying_statements = [
        statement
        for statement in request.statements
        if _statement_stage(statement.encounter_semantics.mode) == "qualify"
        or any("forecast" in obligation_id or "approximate" in obligation_id for obligation_id in statement.obligation_ids)
    ]
    statement_items = "".join(
        f"<li><a href=\"#statement-{_html_escape(statement.statement_id)}\">{_html_text(statement.statement_id)}</a>: {_html_text(statement.encounter_meaning)}</li>"
        for statement in qualifying_statements
    )
    obligation_items = "".join(
        f"<li>{_html_text(obligation.requirement)}</li>"
        for obligation in request.obligations
        if any(term in obligation.category.lower() or term in obligation.requirement.lower() for term in ("scope", "quality", "forecast", "canonical"))
    )
    region_attrs = (
        " id=\"long-document-region-supporting-evidence\" data-long-document-region=\"supporting-evidence\""
        if long_document
        else ""
    )
    return "\n".join(
        (
            f"<section{region_attrs} data-grammar-stage=\"qualify\" data-attention=\"supporting\">",
            "<h2>Uncertainty and caveats</h2>",
            f"<p>{_html_text(request.organizing_purpose.non_scope)}</p>",
            "<ul>",
            statement_items,
            obligation_items,
            "</ul>",
            "</section>",
        )
    )


def render_minimal_html(
    ready_package: ReadyPresentationPackage,
    contract: RendererAdapterContract | None = None,
) -> HtmlRenderedArtifact:
    """Render bounded static HTML from the governed legacy Ready boundary."""

    selected_contract = contract if contract is not None else html_renderer_contract()
    expected_contract = html_renderer_contract()
    if selected_contract != expected_contract:
        raise RendererAdapterInvocationRejected("Minimal HTML rendering requires the minimal HTML renderer contract.")
    invocation = invoke_renderer_adapter(ready_package, selected_contract)
    return _render_minimal_html_request(RendererAdapterRequest(ready_package=ready_package), invocation)


def render_minimal_html_projection(
    projection: MinimalHtmlRendererProjection,
    contract: RendererAdapterContract | None = None,
) -> HtmlRenderedArtifact:
    """Render the fixed non-legacy projection produced from one verified BCRP Plan."""

    if type(projection) is not MinimalHtmlRendererProjection:
        raise RendererAdapterInvocationRejected("Minimal HTML BCRP rendering requires the exact fixed projection type.")
    selected_contract = contract if contract is not None else html_renderer_contract()
    if selected_contract != html_renderer_contract():
        raise RendererAdapterInvocationRejected("Minimal HTML rendering requires the minimal HTML renderer contract.")
    if not projection.fingerprint or not projection.semantic_fingerprint or not projection.validation_policy_id:
        raise RendererAdapterInvocationRejected("Minimal HTML BCRP projection metadata is incomplete.")
    invocation = _MinimalHtmlProjectionInvocation(
        adapter_identity=selected_contract.identity,
        package_identity=projection.identity,
        semantic_fingerprint=projection.semantic_fingerprint,
        validation_policy_id=projection.validation_policy_id,
    )
    return _render_minimal_html_request(projection, invocation)


def _render_minimal_html_request(request, invocation) -> HtmlRenderedArtifact:
    """Single rendering core shared by legacy Ready and verified BCRP projection adapters."""

    references_by_id = {reference.reference_id: reference for reference in request.upstream_references}
    obligations_by_id = {obligation.obligation_id: obligation for obligation in request.obligations}
    long_document = _is_long_document(request)
    statement_articles = "\n".join(
        _render_statement_article(
            statement,
            references_by_id,
            obligations_by_id,
            compact_links=long_document,
        )
        for statement in request.statements
    )
    front_matter_open = (
        "<header id=\"long-document-region-front-matter\" data-long-document-region=\"front-matter\" data-grammar-stage=\"orient\" data-attention=\"primary\">"
        if long_document
        else "<header data-grammar-stage=\"orient\" data-attention=\"primary\">"
    )
    long_document_outline = _render_long_document_outline(request) if long_document else ""
    core_region_open = (
        "<section id=\"long-document-region-core-narrative\" data-long-document-region=\"core-narrative\" data-grammar-stage=\"elaborate\" data-attention=\"secondary\">"
        if long_document
        else "<section data-grammar-stage=\"elaborate\" data-attention=\"secondary\">"
    )
    audit_region_open = (
        "<details id=\"long-document-region-audit-metadata\" data-long-document-region=\"audit-metadata\" data-grammar-stage=\"trace\" data-attention=\"discoverable\">"
        if long_document
        else "<details data-grammar-stage=\"trace\" data-attention=\"discoverable\">"
    )
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
            f"<title>{_html_text(request.identity.title)}</title>",
            _static_reader_experience_css(),
            "</head>",
            "<body data-grammar=\"presentation-grammar-v1\" data-reader-experience=\"static-v0.3\">",
            "<main>",
            front_matter_open,
            f"<h1>{_html_text(request.identity.title)}</h1>",
            f"<p><strong>Purpose:</strong> {_html_text(request.organizing_purpose.statement)}</p>",
            f"<p data-attention=\"secondary\">{_html_text(request.identity.purpose_summary)}</p>",
            long_document_outline,
            "</header>",
            "<section data-grammar-stage=\"state-main-point\" data-attention=\"primary\">",
            "<h2>Primary message</h2>",
            _render_source_structured_text(request.statements[0].encounter_meaning if request.statements else request.organizing_purpose.statement),
            "</section>",
            _render_static_exhibit_region(request),
            core_region_open,
            "<h2>Supporting details</h2>",
            statement_articles,
            "</section>",
            _render_uncertainty_section(request, long_document=long_document),
            _render_reference_inventory(request.upstream_references, long_document=long_document),
            _render_obligation_inventory(request.obligations, long_document=long_document),
            audit_region_open,
            "<summary>Validation and audit metadata</summary>",
            f"<p>Adapter: {_html_text(invocation.adapter_identity.adapter_id)}</p>",
            f"<p>Package: {_html_text(request.identity.package_id)}</p>",
            f"<p>Semantic fingerprint: {_html_text(invocation.semantic_fingerprint)}</p>",
            f"<p>Validation policy: {_html_text(invocation.validation_policy_id)}</p>",
            "</details>",
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


def check_rendered_artifact_conformance(
    ready_package: ReadyPresentationPackage,
    artifact: ToyPlainTextRenderedArtifact | HtmlRenderedArtifact,
) -> RenderedArtifactConformance:
    """Check a downstream rendered artifact's audit link to a Ready package.

    This is downstream output conformance, not constitutional validation. It does
    not validate, promote, reinterpret, persist, export, template, visualize,
    route, serve, or make rendered output canonical.
    """

    prepare_renderer_adapter_request(ready_package)
    if not isinstance(artifact, (ToyPlainTextRenderedArtifact, HtmlRenderedArtifact)):
        raise RenderedArtifactConformanceRejected(
            "Rendered artifact conformance requires a known rendered artifact shape."
        )

    findings = []
    if artifact.package_identity != ready_package.candidate.identity:
        findings.append("package_identity")
    if artifact.semantic_fingerprint != ready_package.semantic_fingerprint:
        findings.append("semantic_fingerprint")
    if artifact.validation_policy_id != ready_package.validation_policy_id:
        findings.append("validation_policy_id")

    return RenderedArtifactConformance(
        conforms=not findings,
        findings=tuple(findings),
        adapter_identity=artifact.adapter_identity,
        package_identity=artifact.package_identity,
        semantic_fingerprint=artifact.semantic_fingerprint,
        validation_policy_id=artifact.validation_policy_id,
    )
