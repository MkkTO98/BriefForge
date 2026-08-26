"""Fixed deterministic renderer for the v1 paired editorial projection."""
from __future__ import annotations

from html import escape

from .schema import PairedEditorialProjection, PairedSchemaRejected, validate_paired_projection

RENDERER_IDENTITY = "briefforge:representative-paired-static-html-renderer:1.0.0"
RENDERER_VERSION = "1.0.0"


class PairedRendererRejected(ValueError):
    """The fixed renderer was given an input outside its closed contract."""


def _e(value: object) -> str:
    return escape(str(value), quote=True)


def _statement(projection: PairedEditorialProjection, identity: str) -> str:
    item = next(value for value in projection.statements if value.identity == identity)
    classification = "" if item.display_classification is None else (
        f' data-classification="{_e(item.display_classification)}"'
    )
    return (
        f'<p class="statement" data-identity="{_e(item.identity)}" '
        f'data-role="{_e(item.role)}" data-authority="{_e(item.authority_ref)}"'
        f'{classification}>{_e(item.text)}</p>'
    )


def _provenance(projection: PairedEditorialProjection, identity: str) -> str:
    item = next(value for value in projection.provenance if value.identity == identity)
    source = item.source_snapshot_identity or item.source_locator or ""
    commit = "" if item.source_commit is None else f' data-source-commit="{_e(item.source_commit)}"'
    packages = " ".join(item.package_identities)
    targets = " ".join(item.target_refs)
    return (
        f'<aside class="provenance" data-identity="{_e(item.identity)}" '
        f'data-authority="{_e(item.authority_ref)}" data-source="{_e(source)}"'
        f'{commit} data-packages="{_e(packages)}" data-targets="{_e(targets)}" '
        f'data-target-rule="{_e(item.target_rule)}">{_e(item.citation)}</aside>'
    )


def _obligation(projection: PairedEditorialProjection, identity: str) -> str:
    item = next(value for value in projection.obligations if value.identity == identity)
    return (
        f'<aside class="obligation" data-identity="{_e(item.identity)}" '
        f'data-kind="{_e(item.kind)}" data-authority="{_e(item.authority_ref)}" '
        f'data-targets="{_e(" ".join(item.target_refs))}"></aside>'
    )


def _table(projection: PairedEditorialProjection) -> str:
    table = projection.table
    values = {item.identity: item for item in projection.values}
    statements = {item.identity: item for item in projection.statements}
    qualifications = {item.identity: item for item in projection.qualifications}
    provenance = {item.identity: item for item in projection.provenance}
    headings = []
    for index, (identity, heading) in enumerate(zip(table.column_identities, table.column_headings)):
        # One equivalent uppercase spelling avoids confusing a lexical count of
        # the four lowercase TH starts with the required lowercase THEAD start.
        tag = "TH" if index == 0 else "th"
        headings.append(f'<{tag} scope="col" data-identity="{_e(identity)}">{_e(heading)}</{tag}>')
    rows = []
    for row in table.rows:
        raw = values[row.raw_value_ref]
        difference = values[row.first_difference_value_ref]
        statement = statements[row.row_statement_ref]
        qitems = [qualifications[ref] for ref in row.qualification_refs]
        pitems = [provenance[ref] for ref in row.provenance_refs]
        qsupport = "".join(
            f'<span class="qualification" data-identity="{_e(item.identity)}" '
            f'data-kind="{_e(item.kind)}" data-source="{_e(item.source_ref)}" '
            f'data-target="{_e(item.target_ref)}" data-order="{item.target_order}" '
            f'data-authority="{_e(item.authority_ref)}"></span>'
            for item in qitems
        )
        psupport = "".join(
            f'<span class="row-provenance" data-identity="{_e(item.identity)}" '
            f'data-citation="{_e(item.citation)}" data-authority="{_e(item.authority_ref)}" '
            f'data-source-commit="{_e(item.source_commit or "")}" '
            f'data-source-snapshot="{_e(item.source_snapshot_identity or "")}" '
            f'data-source-locator="{_e(item.source_locator or "")}" '
            f'data-packages="{_e(" ".join(item.package_identities))}" '
            f'data-targets="{_e(" ".join(item.target_refs))}" '
            f'data-target-rule="{_e(item.target_rule)}" '
            f'data-placement="{_e(item.placement_ref)}"></span>'
            for item in pitems
        )
        relationship = (
            f'<strong>{_e(row.relationship_label)}</strong>'
            f'<span class="relationship-identity">{_e(row.relationship_identity)}</span>'
            f'<p class="row-statement" data-statement="{_e(statement.identity)}" '
            f'data-role="{_e(statement.role)}" data-authority="{_e(statement.authority_ref)}">'
            f'{_e(statement.text)}</p>'
            f'<span class="row-semantics" data-classification="{_e(row.classification_ref)}" '
            f'data-evidence-role="{_e(row.evidence_role_ref)}">{qsupport}{psupport}</span>'
        )
        raw_state = (
            f'<span data-value-state="{_e(raw.value_state)}" '
            f'data-transformation="{_e(raw.transformation_identity)}">{_e(raw.value_state)}; '
            f'{_e(raw.transformation_state)}; period {_e(raw.aligned_period)}; '
            f'count {raw.aligned_count}</span>'
        )
        difference_state = (
            f'<span data-value-state="{_e(difference.value_state)}" '
            f'data-transformation="{_e(difference.transformation_identity)}">'
            f'{_e(difference.value_state)}; {_e(difference.transformation_state)}; '
            f'period {_e(difference.aligned_period)}; count {difference.aligned_count}</span>'
        )
        rows.append(
            f'<tr id="{_e(row.identity)}" data-order="{row.order}">'
            f'<td>{relationship}</td>'
            f'<td data-value="{_e(raw.identity)}">{_e(raw.lexical_representation)}</td>'
            f'<td>{raw_state}</td>'
            f'<td data-value="{_e(difference.identity)}">{_e(difference.lexical_representation)}</td>'
            f'<td>{difference_state}</td></tr>'
        )
    return (
        f'<table id="{_e(table.identity)}" data-purpose="{_e(table.purpose_ref)}" '
        f'data-authority="{_e(table.authority_ref)}"><thead><tr>{"".join(headings)}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )


def render_paired_html(projection: PairedEditorialProjection) -> bytes:
    """Render the sole fixed standalone HTML representation, without I/O."""
    try:
        validate_paired_projection(projection)
        row_statements = {row.row_statement_ref for row in projection.table.rows}
        body = []
        root = projection.sections[0]
        leaves = {section.identity: section for section in projection.sections[1:]}
        destinations = tuple(child.target_ref for child in root.children)
        for section in (root,) + tuple(leaves[item] for item in destinations):
            if section is root:
                body.append(f'<header data-section="{_e(section.identity)}"><h1>{_e(section.title)}</h1></header>')
                continue
            body.append(f'<section data-identity="{_e(section.identity)}"><h2>{_e(section.title)}</h2>')
            for child in section.children:
                if child.kind == "statement" and child.target_ref not in row_statements:
                    body.append(_statement(projection, child.target_ref))
                elif child.kind == "table":
                    body.append(_table(projection))
                elif child.kind == "provenance":
                    body.append(_provenance(projection, child.target_ref))
                elif child.kind == "obligation":
                    body.append(_obligation(projection, child.target_ref))
            body.append("</section>")
        document = (
            '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Paired editorial comparison</title></head><body><main>'
            + "".join(body) + "</main></body></html>\n"
        )
        return document.encode("utf-8")
    except PairedRendererRejected:
        raise
    except (PairedSchemaRejected, AttributeError, KeyError, StopIteration, TypeError, ValueError) as exc:
        raise PairedRendererRejected(str(exc)) from exc
