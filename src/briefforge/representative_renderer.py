"""Deterministic, standalone, fixed-profile representative HTML renderer."""
from __future__ import annotations
from dataclasses import asdict
from html import escape
import json

from .representative_projection import (
    PROJECTION_PROFILE_ID, PROJECTION_PROFILE_VERSION, RepresentativeProjection,
    RepresentativeProjectionRejected, verify_representative_projection,
)

RENDERER_IDENTITY = "renderer:representative-static-html"
RENDERER_VERSION = "1.0.0"
RENDERER_ADAPTER_ID = "representative-static-html-renderer"


def _e(value: object) -> str:
    return escape(str(value), quote=True)


def _value_display(item) -> str:
    if item.value_state in {"present", "explicit-zero"}:
        suffix = f" scale={item.scale}"
        if item.approximate:
            suffix += f" approximate={_e(item.approximation_method)} bound={_e(item.approximation_bound)}"
        return f"{_e(item.coefficient)}{suffix}"
    return _e(item.reason)


_EDGE_ROLES = {"brief_ref","material_refs","organizing_purpose_ref","audience_refs","distribution_ref","exhibit_refs",
    "brief_purpose_ref","brief_audience_ref","children","purpose_ref","authority_ref","upstream_refs","value_ref",
    "source_ref","target_ref","primary_ref","comparison_ref","provenance_ref","snapshot_ref","target_refs","value_ids",
    "required_value_ids","unit_ref","semantic_type_ref"}

def _semantic_entries(p):
    """Renderer-owned deterministic inventory of displayed fields and directed edges."""
    half=len(p.audiences)//2
    entities={
        p.brief_identity:{"identity":p.brief_identity,"organizing_purpose_ref":p.brief_purpose.identity,
                          "audience_refs":tuple(x.identity for x in p.audiences[:half]),
                          "scope":p.brief_scope,"non_scope":p.brief_non_scope},
        p.package_identity:{"identity":p.package_identity,"brief_ref":p.brief_identity,
                            "material_refs":p.material_identities,"organizing_purpose_ref":p.candidate_purpose.identity,
                            "audience_refs":tuple(x.identity for x in p.audiences[half:]),
                            "scope":p.candidate_scope,"non_scope":p.candidate_non_scope,
                            "distribution_ref":p.distribution.identity,"exhibit_refs":(p.exhibit.identity,)},
    }
    for identity in p.material_identities:
        entities[identity]={"identity":identity,"required_value_ids":p.required_value_ids}
    for collection in (p.sections,p.statements,p.qualifications,p.case_bindings,p.values,p.provenance,
                       p.evidence_snapshots,p.external_references,p.units,p.semantic_types,p.obligations,
                       p.content_authorities,p.audiences):
        for item in collection: entities[item.identity]=asdict(item)
    for item in (p.brief_purpose,p.candidate_purpose,p.exhibit,p.distribution):
        entities[item.identity]=asdict(item)
    entries=[]
    for identity in sorted(entities):
        for role,value in sorted(entities[identity].items()):
            if value is None: continue
            values=list(value) if role in _EDGE_ROLES and isinstance(value,(tuple,list)) else [value]
            if role in _EDGE_ROLES:
                for ordinal,target in enumerate(values):
                    entries.append((f"edge:{identity}:{role}:{ordinal:04d}","edge",target))
            else:
                entries.append((f"field:{identity}:{role}","field",value))
    return entries


def render_representative_html(projection):
    """Render every governed field/edge as one visible authoritative node."""
    if type(projection) is not RepresentativeProjection:
        raise RepresentativeProjectionRejected("exact representative projection required")
    verify_representative_projection(projection)
    if (projection.profile_identity, projection.profile_version, projection.renderer_identity,
        projection.renderer_version, projection.renderer_adapter_id) != (
        PROJECTION_PROFILE_ID, PROJECTION_PROFILE_VERSION, RENDERER_IDENTITY,
        RENDERER_VERSION, RENDERER_ADAPTER_ID):
        raise RepresentativeProjectionRejected("projection is routed to the wrong fixed renderer")
    entries={key:(role,value) for key,role,value in _semantic_entries(projection)}
    emitted=set()
    def node(key):
        role,value=entries[key]; emitted.add(key)
        canonical=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
        return f'<span data-semantic-key="{_e(key)}" data-semantic-role="{role}">{_e(canonical)}</span>'
    def matching(prefix):
        return " ".join(node(key) for key in sorted(entries) if key.startswith(prefix) and key not in emitted)
    lines=["<!doctype html>",'<html lang="en">',"<head>",'<meta charset="utf-8">',
           '<title>BriefForge representative projection</title>',"</head>","<body>","<main>",
           "<h1>BriefForge representative projection</h1>"]
    values={x.identity:x for x in projection.values}
    sections={x.identity:x for x in projection.sections}
    statements={x.identity:x for x in projection.statements}

    def emit_table():
        lines.extend(('<section data-region="fixed-table"><h4>Authored paired cases</h4>',
                      "<p>"+matching(f"field:{projection.exhibit.identity}:")+
                      " "+matching(f"edge:{projection.exhibit.identity}:")+"</p>",
                      '<table><thead><tr><th>case + slot</th><th>value/state</th><th>unit</th><th>type</th><th>source</th></tr></thead><tbody>'))
        for case in projection.case_bindings:
            for slot,ref in (("primary",case.primary_ref),("comparison",case.comparison_ref)):
                case_prefix=f"field:{case.identity}:" if slot=="primary" else ""
                edge=f"edge:{case.identity}:{slot}_ref:0000"
                value=values[ref]
                case_fields=matching(case_prefix) if case_prefix else ""
                lines.append("<tr><td>"+case_fields+(node(edge) if edge in entries else "")+
                    "</td><td>"+matching(f"field:{value.identity}:")+"</td><td>"+
                    node(f"edge:{value.identity}:unit_ref:0000")+"</td><td>"+
                    node(f"edge:{value.identity}:semantic_type_ref:0000")+"</td><td>"+
                    node(f"edge:{value.identity}:source_ref:0000")+"</td></tr>")
        lines.extend(("</tbody></table></section>",))

    root=sections[projection.section_preorder[0]]
    lines.extend(('<section data-region="authored-root-section"><h2>Authored root section</h2>',
                  "<p>"+matching(f"field:{root.identity}:")+" "+matching(f"edge:{root.identity}:")+"</p>"))
    for leaf_identity in root.children:
        leaf=sections[leaf_identity]
        lines.extend(('<section data-region="authored-leaf-section"><h3>Authored leaf section</h3>',
                      "<p>"+matching(f"field:{leaf.identity}:")+" "+matching(f"edge:{leaf.identity}:")+"</p>"))
        for child_identity in leaf.children:
            if child_identity in statements:
                lines.append('<article data-region="authored-statement">'+
                    matching(f"field:{child_identity}:")+" "+matching(f"edge:{child_identity}:")+"</article>")
            elif child_identity==projection.exhibit_identity:
                emit_table()
            else:
                raise RepresentativeProjectionRejected("section child is outside fixed authored closure")
        lines.append("</section>")
    lines.extend(("</section>",'<section data-region="semantic-closure"><h2>Remaining governed semantic content</h2><ol>'))
    for key in sorted(entries):
        if key not in emitted:
            lines.append(f"<li>{node(key)}</li>")
    if emitted != set(entries):
        raise RepresentativeProjectionRejected("renderer semantic realization accounting is incomplete")
    lines.extend(("</ol></section>","</main>","</body>","</html>"))
    return "\n".join(lines).encode("utf-8")
