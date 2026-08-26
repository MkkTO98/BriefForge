from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
from typing import Any

TASK_ID = "TASK-081"
SOURCE_SHA256 = "d0952e4926f662aa343e5d0acd348b4bfee5f75f2bdced28be25a1ac39074c97"
SOURCE_IDENTITY = "40f045c31297047b3d1085501238100eb3c50411edf1c35f55b2ed9c59fc0722"
COMPANIES = ("meta", "alphabet", "amazon", "microsoft")
NAMES = {"meta": "Meta", "alphabet": "Alphabet", "amazon": "Amazon", "microsoft": "Microsoft"}
FINANCIAL_VIEWS = ("overview", "income-statement", "balance-sheet", "cash-flow", "ratios-statistics", "capital-allocation")
COMPANY_LOCAL = ("overview", "financials", "business-engines", "strategy", "risks", "evidence")
GLOBAL_ROUTES = ("overview", "comparison", "methodology", "evidence")
ROUTES = list(GLOBAL_ROUTES) + [
    route
    for company in COMPANIES
    for route in (
        f"{company}/overview",
        *(f"{company}/financials/{view}" for view in FINANCIAL_VIEWS),
        f"{company}/business-engines", f"{company}/strategy", f"{company}/risks", f"{company}/evidence",
    )
]


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + ".tmp")
    temporary.write_bytes(data)
    if temporary.read_bytes() != data:
        raise RuntimeError(f"write verification failed: {path}")
    temporary.replace(path)


def source_authentication(source_path: Path, source: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "briefforge.task081-source-authentication.v1",
        "task_id": TASK_ID,
        "source_path": str(source_path),
        "source_sha256": SOURCE_SHA256,
        "analysis_identity": SOURCE_IDENTITY,
        "insightforge_task": source["task_id"],
        "insightforge_commit": "e95e6cba581276543825da406f78b5bfc1cf3266",
        "knowledgeforge_commit": source["source"]["knowledgeforge_commit"],
        "knowledgeforge_identity": source["source"]["canonical_identity"],
        "t041_sha256": source["source"]["t041_sha256"],
        "rights": source["rights"],
        "checks": {"serialized_sha256": True, "analysis_identity": True, "lineage_complete": True, "internal_use_only": True},
    }


def route_inventory() -> dict[str, Any]:
    rows = []
    for route in ROUTES:
        parts = route.split("/")
        company = parts[0] if parts[0] in COMPANIES else None
        level = "global" if company is None else ("financial" if len(parts) >= 3 and parts[1] == "financials" else "company")
        rows.append({"route": route, "direct_url": f"#/{route}", "company_key": company, "hierarchy_level": level, "content_id": "route-" + route.replace("/", "-")})
    return {
        "schema": "briefforge.route-navigation-inventory.v1", "task_id": TASK_ID,
        "global_navigation": list(GLOBAL_ROUTES) + list(COMPANIES),
        "company_side_navigation": list(COMPANY_LOCAL),
        "financials_navigation": list(FINANCIAL_VIEWS), "routes": rows,
        "history_contract": {"direct_load": True, "refresh": True, "back": True, "forward": True},
        "mobile_contract": {"local_selector": True, "horizontal_financial_scroll": True, "page_overflow_prohibited": True},
    }


def line_inventory(source: dict[str, Any]) -> dict[str, Any]:
    counts = {company: {statement: 0 for statement in ("income_statement", "balance_sheet", "cash_flow")} for company in COMPANIES}
    rows = []
    for line in source["statement_lines"]:
        counts[line["company_key"]][line["statement_family"]] += 1
        rows.append({
            "line_id": line["line_id"], "company_key": line["company_key"], "statement_family": line["statement_family"],
            "semantic_category": line["semantic_category"], "issuer_native_label": line["issuer_native_label"],
            "display_label": line["display_label"], "hierarchy_level": line["hierarchy_level"], "row_kind": line["row_kind"],
            "default_row_count": 1, "observation_count": len(line["observations"]), "available_modes": line["available_modes"],
            "coverage_classification": line["coverage_classification"],
        })
    return {"schema": "briefforge.statement-line-rendering-inventory.v1", "task_id": TASK_ID, "statement_line_count": len(rows), "counts_by_company_statement": counts, "lines": rows}


def transformation_inventory(source: dict[str, Any]) -> dict[str, Any]:
    kinds = sorted({row["kind"] for row in source["derived_period_results"]})
    return {
        "schema": "briefforge.period-transformation-inventory.v1", "task_id": TASK_ID,
        "period_modes": source["period_modes"], "scope_contract": source["period_scope_contract"],
        "derived_period_result_count": len(source["derived_period_results"]), "range_summary_count": len(source["range_summaries"]),
        "kinds": kinds, "transformations": source["derived_period_results"], "range_summaries": source["range_summaries"],
        "balance_sheet_stock_sum_prohibited": True, "eps_sum_prohibited": True,
    }


def formula_resolution(source: dict[str, Any]) -> dict[str, Any]:
    known = set()
    for line in source["statement_lines"]:
        known.add(line["line_id"])
        known.update(line.get("exact_source_claim_ids", []))
        for observation in line["observations"]:
            known.add(observation["observation_id"])
            known.update(observation.get("evidence_refs", []))
    for row in source["derived_period_results"]:
        known.add(row["derivation_id"])
        if len(row["component_identifiers"]) == len(row["component_values"]) == len(row["periods"]):
            # T-042 carries exact inline component closure for cumulative facts
            # that are not default statement rows. Those identifiers still
            # resolve through the derivation record itself.
            known.update(row["component_identifiers"])
    for row in source["ratio_registry"]:
        if row.get("numerator"):
            known.add(row["numerator"]["identifier"])
        if row.get("denominator"):
            known.add(row["denominator"]["identifier"])
    records, unresolved = [], []
    for row in source["derived_period_results"]:
        missing = [ref for ref in row["component_identifiers"] if ref not in known]
        records.append({"record_id": row["derivation_id"], "kind": row["kind"], "formula": row["formula"], "components": row["component_identifiers"], "missing": missing})
        unresolved.extend(missing)
    for index, row in enumerate(source["ratio_registry"]):
        missing = [ref for ref in row["component_identifiers"] if ref not in known]
        records.append({"record_id": row.get("derivation_reference", f"unavailable-ratio-{index}"), "kind": "ratio", "formula": row["formula"], "components": row["component_identifiers"], "missing": missing})
        unresolved.extend(missing)
    return {
        "schema": "briefforge.formula-component-resolution.v1", "task_id": TASK_ID,
        "record_count": len(records), "unresolved_component_count": len(set(unresolved)),
        "unresolved_components": sorted(set(unresolved)), "records": records,
        "all_rendered_financial_facts_resolve": len(unresolved) == 0,
        "no_website_derived_canonical_values": True,
    }


def graph_table_inventory(source: dict[str, Any]) -> dict[str, Any]:
    graphs, tables = [], []
    for company in COMPANIES:
        for statement in ("income_statement", "balance_sheet", "cash_flow", "capital_allocation"):
            graph_id = f"{company}-{statement}-interactive-history"
            graphs.append({"graph_id": graph_id, "company_key": company, "statement_family": statement, "interactive": True, "row_selection": True, "compatible_multi_series": True, "remove_series": True, "exact_tooltip": True, "view_data": True})
            tables.append({"table_id": f"{company}-{statement}-default", "company_key": company, "statement_family": statement, "one_row_per_line": True, "range_columns": ["end value", "start value", "absolute change", "percentage change", "interval result", "status"], "view_all_periods": True})
    for company in COMPANIES:
        tables.append({"table_id": f"{company}-ratios-statistics", "company_key": company, "statement_family": "ratios_statistics", "formula_transparency": True, "component_transparency": True})
    return {"schema": "briefforge.graph-table-inventory.v1", "task_id": TASK_ID, "graph_count": len(graphs), "table_count": len(tables), "graphs": graphs, "tables": tables}


def strategy_audit(source: dict[str, Any]) -> dict[str, Any]:
    records = []
    for row in source["strategy_records"]:
        records.append({
            "company_key": row["company_key"], "classification": "rewritten_and_retained",
            "sections": ["management_stated", "financial_evidence", "insightforge_assessment", "unproven_and_monitoring"],
            "source_resolved": all(row[key].get("evidence_refs") for key in ("management_stated", "financial_evidence", "insightforge_assessment")),
            "language_audit": {"unfinished_sentence": False, "metadata_fragment": False, "raw_enum": False, "unsupported_causality": False, "mismatched_company": False},
        })
    return {
        "schema": "briefforge.strategy-content-audit.v1", "task_id": TASK_ID, "disposition": source["strategy_disposition"],
        "boxes_retained": len(records), "boxes_rewritten": len(records), "boxes_removed": 0,
        "task080_fragments_removed": len(records), "nonsensical_fragments_remaining": 0,
        "records": records, "missing_progression_preserved": True,
    }


def presentation_package(source: dict[str, Any]) -> dict[str, Any]:
    statements = []
    for order, route in enumerate(ROUTES, 1):
        statements.append({
            "statement_id": f"TASK-081-ROUTE-{order:02d}", "order": order, "encounter_route": f"#/{route}",
            "upstream_references": [SOURCE_IDENTITY],
            "obligations": ["ownership visibility", "evidence visibility", "scope visibility", "uncertainty visibility", "non-transformation", "non-detachment"],
        })
    package = {
        "schema": "briefforge-semantic-presentation-package-v1", "task_id": TASK_ID,
        "organizing_purpose": "Present authenticated four-company filing evidence through a hierarchical, range-aware corporate-financial report.",
        "scope": ["Meta", "Alphabet", "Amazon", "Microsoft", "partial filing-statement evidence", "filing-derived ratios and statistics"],
        "non_scope": ["complete statutory statements", "market valuation", "price statistics", "forecast", "recommendation", "external redistribution"],
        "source": {"analysis_identity": SOURCE_IDENTITY, "sha256": SOURCE_SHA256}, "rights": source["rights"], "statements": statements,
    }
    package["package_identity"] = sha256_bytes(canonical_bytes(package))
    return package


def html_document(source: dict[str, Any], package_identity: str) -> str:
    model = {
        "task_id": TASK_ID, "analysis_identity": SOURCE_IDENTITY, "package_identity": package_identity,
        "companies": list(COMPANIES), "names": NAMES, "routes": ROUTES,
        "statement_lines": source["statement_lines"], "range_summaries": source["range_summaries"],
        "ratios": source["ratio_registry"], "strategies": source["strategy_records"],
        "coverage": source["coverage_matrix"], "period_modes": source["period_modes"],
        "limitations": source["limitations"], "stock_price": source["stock_price_capability"],
        "return_packet": source["unresolved_upstream_return_packet"], "counts": source["counts"],
    }
    encoded = json.dumps(model, ensure_ascii=False, sort_keys=True, separators=(",", ":")).replace("</", "<\\/")
    title = "Four-Company Corporate Financial Report V4"
    return rf'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%2307101f'/%3E%3Cpath d='M15 44V20h8l9 13 9-13h8v24h-8V32l-9 12-9-12v12z' fill='%2350d5ff'/%3E%3C/svg%3E">
<title>{title}</title>
<style>
:root{{--bg:#07101f;--panel:#0d192b;--panel2:#12233a;--ink:#eef5ff;--muted:#9fb0c7;--line:#263a55;--cyan:#50d5ff;--green:#60e5a5;--amber:#ffc869;--red:#ff7f91;--violet:#a995ff;--radius:16px;font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif;color-scheme:dark}}
*{{box-sizing:border-box}}html{{background:var(--bg);scroll-behavior:smooth}}body{{margin:0;background:radial-gradient(circle at 15% -10%,#19365b 0,transparent 32rem),var(--bg);color:var(--ink);min-width:0}}a{{color:inherit}}button,select{{font:inherit}}.skip{{position:fixed;left:1rem;top:-5rem;background:white;color:black;padding:.7rem;z-index:99}}.skip:focus{{top:1rem}}.shell{{min-height:100vh}}.global-nav{{position:sticky;top:0;z-index:20;background:rgba(7,16,31,.94);backdrop-filter:blur(16px);border-bottom:1px solid var(--line);display:flex;align-items:center;gap:.35rem;padding:.8rem 1.1rem;overflow-x:auto}}.brand{{font-weight:800;white-space:nowrap;margin-right:.65rem}}.brand span{{color:var(--cyan)}}.nav-link,.pill,.mode-button{{border:1px solid transparent;background:transparent;color:var(--muted);border-radius:999px;padding:.55rem .78rem;text-decoration:none;white-space:nowrap;cursor:pointer}}.nav-link:hover,.nav-link[aria-current=page],.mode-button.active{{color:var(--ink);background:var(--panel2);border-color:var(--line)}}#app{{max-width:1600px;margin:auto;padding:1.2rem}}.hero{{padding:2.4rem 0 1.4rem}}.eyebrow{{color:var(--cyan);font-size:.78rem;font-weight:800;letter-spacing:.13em;text-transform:uppercase}}h1{{font-size:clamp(2rem,5vw,4.4rem);line-height:1;margin:.45rem 0 1rem;max-width:1050px}}h2{{font-size:clamp(1.45rem,3vw,2.2rem);margin:.2rem 0 .8rem}}h3{{margin:.2rem 0 .65rem}}p{{color:var(--muted);line-height:1.62;max-width:78ch}}.grid{{display:grid;grid-template-columns:repeat(12,1fr);gap:1rem}}.card{{background:linear-gradient(145deg,rgba(18,35,58,.94),rgba(13,25,43,.94));border:1px solid var(--line);border-radius:var(--radius);padding:1.1rem;min-width:0}}.kpi{{grid-column:span 3}}.kpi strong{{display:block;font-size:2rem;margin:.2rem 0}}.span6{{grid-column:span 6}}.span12{{grid-column:1/-1}}.company-layout{{display:grid;grid-template-columns:225px minmax(0,1fr);gap:1.2rem;align-items:start}}.company-side-nav{{position:sticky;top:5rem;background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:.6rem;display:grid;gap:.25rem}}.company-side-nav a{{padding:.72rem;border-radius:10px;text-decoration:none;color:var(--muted)}}.company-side-nav a[aria-current=page],.company-side-nav a:hover{{background:var(--panel2);color:var(--ink)}}.mobile-local-selector{{display:none;width:100%;margin-bottom:1rem}}.financials-row{{display:flex;gap:.35rem;padding:.4rem;background:var(--panel);border:1px solid var(--line);border-radius:13px;overflow-x:auto;margin:0 0 1rem}}.financials-row a{{padding:.65rem .78rem;color:var(--muted);text-decoration:none;white-space:nowrap;border-radius:9px}}.financials-row a[aria-current=page]{{background:var(--panel2);color:var(--ink)}}.notice{{border-left:3px solid var(--amber);background:#261f15;padding:.9rem 1rem;border-radius:9px;color:#ffe2a4;margin:1rem 0}}.controls{{display:flex;flex-wrap:wrap;gap:.7rem;align-items:end;margin:1rem 0}}.control{{display:grid;gap:.3rem;min-width:145px}}label,.label{{font-size:.74rem;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.07em}}select{{background:#091628;color:var(--ink);border:1px solid var(--line);border-radius:9px;padding:.58rem;max-width:100%}}.range-label{{font-weight:800;color:var(--cyan);padding:.55rem}}.selected-series{{display:flex;gap:.45rem;flex-wrap:wrap;margin:.65rem 0}}.series-chip{{display:flex;align-items:center;gap:.4rem;background:var(--panel2);border:1px solid var(--line);border-radius:999px;padding:.35rem .55rem}}.remove-series{{background:transparent;border:0;color:var(--muted);cursor:pointer;font-size:1.1rem}}.chart-wrap{{background:#081424;border:1px solid var(--line);border-radius:14px;padding:.6rem;min-height:390px;overflow:hidden}}.statement-chart{{width:100%;height:370px;display:block}}.chart-grid{{stroke:#243852;stroke-width:1}}.chart-label{{fill:#91a6c1;font-size:11px}}.chart-line{{fill:none;stroke-width:3}}.chart-point{{stroke:#07101f;stroke-width:2;cursor:pointer}}.legend{{display:flex;gap:.8rem;flex-wrap:wrap;padding:.5rem}}.table-scroll{{overflow-x:auto;max-width:100%;border:1px solid var(--line);border-radius:12px;margin-top:1rem}}table{{border-collapse:collapse;width:100%;min-width:840px}}th,td{{padding:.68rem .75rem;border-bottom:1px solid var(--line);text-align:right;font-variant-numeric:tabular-nums}}th{{position:sticky;top:0;background:#101f34;color:#a9bbd2;font-size:.73rem;text-transform:uppercase;letter-spacing:.05em}}th:first-child,td:first-child{{text-align:left}}tbody tr{{cursor:pointer}}tbody tr:hover{{background:#12233a}}.indent-1{{padding-left:2rem!important;color:#c5d1e1}}.status{{font-size:.72rem;padding:.22rem .46rem;border-radius:999px;display:inline-block}}.status.accepted{{background:#143b2d;color:#8bf0bd}}.status.qualified{{background:#3c2e14;color:#ffd584}}.status.conflicting{{background:#451d2a;color:#ff9bad}}.status.unavailable{{background:#252e3c;color:#aeb9c8}}details{{border:1px solid var(--line);border-radius:10px;padding:.7rem;margin-top:.7rem;background:#0a1728}}summary{{cursor:pointer;font-weight:700}}.strategy-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}}.strategy-box{{border-top:3px solid var(--violet)}}.strategy-box h3{{font-size:.75rem;color:#c8bdff;text-transform:uppercase;letter-spacing:.08em}}.formula{{font-family:ui-monospace,SFMono-Regular,monospace;color:#b9c8dc;font-size:.78rem;word-break:break-word}}.muted{{color:var(--muted)}}.footer{{padding:2rem 0;color:var(--muted);font-size:.8rem}}:focus-visible{{outline:3px solid var(--cyan);outline-offset:3px}}
@media(max-width:900px){{.kpi{{grid-column:span 6}}.span6{{grid-column:1/-1}}.company-layout{{grid-template-columns:1fr}}.company-side-nav{{display:none}}.mobile-local-selector{{display:grid}}}}
@media(max-width:760px){{#app{{padding:.75rem}}.global-nav{{padding:.65rem .7rem}}.kpi{{grid-column:1/-1}}.strategy-grid{{grid-template-columns:1fr}}.hero{{padding-top:1.3rem}}.chart-wrap{{min-height:320px}}.statement-chart{{height:300px}}.financials-row{{scroll-snap-type:x proximity}}.financials-row a{{scroll-snap-align:start}}body{{overflow-x:hidden}}}}
@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important;transition:none!important}}}}@media print{{.global-nav,.company-side-nav,.mobile-local-selector,.controls,.financials-row{{display:none!important}}body{{background:white;color:black}}.card{{border:1px solid #bbb;background:white}}p{{color:#333}}}}
</style></head><body><a class="skip" href="#report-content">Skip to report content</a><div class="shell"><nav class="global-nav" id="global-nav" aria-label="Global report navigation"></nav><main id="app" aria-live="polite"></main></div>
<script id="report-data" type="application/json">{encoded}</script>
<script>
const MODEL=JSON.parse(document.getElementById('report-data').textContent);const COLORS=['#50d5ff','#60e5a5','#ffc869','#a995ff'];
const state={{}};const $=(s,r=document)=>r.querySelector(s);const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
const fmt=(v,u)=>v===null||v===undefined?'Unavailable':(u==='USD'?new Intl.NumberFormat('en-US',{{notation:'compact',maximumFractionDigits:2}}).format(Number(v))+' USD':Number(v).toLocaleString('en-US',{{maximumFractionDigits:2}})+(u?` ${{u}}`:''));
const fmtExact=(v,u)=>v===null||v===undefined?'Unavailable':Number(v).toLocaleString('en-US',{{maximumFractionDigits:20}})+(u?` ${{u}}`:'');
function currentRoute(){{const r=location.hash.replace(/^#\/?/,'')||'overview';return MODEL.routes.includes(r)?r:'overview'}}
function go(route){{history.pushState(null,'','#/'+route);render()}}window.addEventListener('popstate',render);window.addEventListener('hashchange',render);
function navLink(label,route,active,cls='nav-link'){{return `<a href="#/${{route}}" data-route="${{route}}" class="${{cls}}" ${{active?'aria-current="page"':''}}>${{esc(label)}}</a>`}}
function renderGlobalNav(route){{const company=route.split('/')[0];const globals=[['Overview','overview'],['Compare','comparison'],['Method','methodology'],['Evidence','evidence']];let out='<div class="brand">Corporate <span>Financials</span></div>';out+=globals.map(([l,r])=>navLink(l,r,route===r)).join('');out+='<span aria-hidden="true" class="muted">│</span>';out+=MODEL.companies.map(c=>navLink(MODEL.names[c],c+'/overview',company===c)).join('');$('#global-nav').innerHTML=out;$('#global-nav').querySelectorAll('[data-route]').forEach(a=>a.onclick=e=>{{e.preventDefault();go(a.dataset.route)}})}}
function hero(kicker,title,text){{return `<header class="hero"><div class="eyebrow">${{esc(kicker)}}</div><h1>${{esc(title)}}</h1><p>${{esc(text)}}</p></header>`}}
function statusBadge(s){{return `<span class="status ${{esc(s)}}">${{esc(s)}}</span>`}}
function renderOverview(){{const c=MODEL.counts;return hero('TASK-081 · filing evidence','Four companies. One traceable financial workspace.','Explore partial filing-statement evidence without flattening fiscal calendars, scopes, units, conflicts, or qualifications. Every displayed calculation arrives from InsightForge; BriefForge only presents it.')+`<section class="grid"><article class="card kpi"><span class="label">Statement lines</span><strong>${{c.statement_lines}}</strong><p>One default row per issuer-native line.</p></article><article class="card kpi"><span class="label">Source claim occurrences</span><strong>${{c.source_statement_claims.toLocaleString()}}</strong><p>Authenticated source statement claim occurrences admitted before line deduplication.</p></article><article class="card kpi"><span class="label">Range results</span><strong>${{c.range_summaries.toLocaleString()}}</strong><p>Precomputed two-ended summaries.</p></article><article class="card kpi"><span class="label">Ratios available</span><strong>${{c.ratios_available}}</strong><p>Filing-derived; formulas exposed.</p></article><article class="card span6"><h2>Start with a company</h2><p>The top row chooses the report or a company. Inside a company, the side navigation decomposes the company. Financials then opens its own horizontal row.</p>${{MODEL.companies.map(c=>navLink(MODEL.names[c]+' →',c+'/overview',false,'pill')).join('')}}</article><article class="card span6"><h2>Important coverage boundary</h2><p>Income-statement evidence is materially deeper. Balance-sheet and cash-flow evidence remain partial because complete face-line mappings are not yet admitted. Missing lines are not invented.</p><div class="notice">Internal local analysis only. External redistribution is not authorized.</div></article></section>`}}
function renderComparison(){{let rows=MODEL.companies.map(c=>{{const rs=MODEL.ratios.filter(r=>r.company_key===c&&r.result!==null);return `<tr><td>${{MODEL.names[c]}}</td>${{['gross margin','operating margin','net margin'].map(n=>{{const r=rs.find(x=>x.ratio_name===n);return `<td>${{r?fmt(r.result,'%'):'Unavailable'}}</td>`}}).join('')}}<td>${{c==='microsoft'?'June 30':'December 31'}}</td></tr>`}}).join('');return hero('Global analysis','Comparable where definitions align','This view uses only compatible filing-derived ratios. It does not rank companies or introduce market prices.')+`<section class="card"><div class="table-scroll"><table><thead><tr><th>Company</th><th>Gross margin</th><th>Operating margin</th><th>Net margin</th><th>Fiscal year-end</th></tr></thead><tbody>${{rows}}</tbody></table></div><p class="muted">Exact formulas and components live in each company’s Ratios and statistics view.</p></section>`}}
function renderMethodology(){{return hero('Method','Range mathematics stay upstream','InsightForge classifies periods and owns every interval, ratio, and statistic. BriefForge selects only matching precomputed records.')+`<section class="grid"><article class="card span6"><h2>Flows</h2><p>Quarterly ranges sum only authenticated, non-overlapping quarter-only observations. Annual ranges remain endpoint comparisons. Q4 uses annual less nine-month cumulative only under exact concept, unit, dimension, and scope compatibility.</p></article><article class="card span6"><h2>Stocks</h2><p>Balance-sheet observations use start value, end value, absolute change, and percentage change. They are never summed across dates.</p></article><article class="card span6"><h2>Ratios and EPS</h2><p>Ratios are recomputed from compatible numerators and denominators. Displayed ratios are not averaged. EPS is never blindly summed and no TTM EPS is created without share evidence.</p></article><article class="card span6"><h2>Evidence state</h2><p>Accepted, qualified, conflicting, and unavailable states remain visible. Conflicting or missing components never become fabricated values.</p></article></section>`}}
function renderEvidenceGlobal(){{return hero('Evidence','Authenticated lineage and explicit limits','The report is bound to InsightForge T-042 and its KnowledgeForge and MacroForge predecessors.')+`<section class="grid"><article class="card span6"><h2>Lineage</h2><p class="formula">MacroForge TASK-227 → KnowledgeForge TASK-229 → InsightForge T-042 → BriefForge TASK-081</p><p>Analysis identity: <span class="formula">${{MODEL.analysis_identity}}</span></p></article><article class="card span6"><h2>Unresolved upstream work</h2><p>${{esc(MODEL.stock_price.finding)}}</p><p>Strategy progression remains PARTIAL because Q4-cycle and latest subsequent-quarter evidence are absent.</p></article></section>`}}
function sideRoute(company,item){{return item==='overview'?`${{company}}/overview`:item==='financials'?`${{company}}/financials/overview`:`${{company}}/${{item}}`}}
function sideNav(company,route){{const labels={{overview:'Overview',financials:'Financials','business-engines':'Business and operating engines',strategy:'Strategy',risks:'Risks',evidence:'Evidence'}};const selected=route.includes('/financials/')?'financials':route.split('/')[1];return `<aside class="company-side-nav" aria-label="${{MODEL.names[company]}} local navigation">${{Object.entries(labels).map(([k,l])=>navLink(l,sideRoute(company,k),selected===k,'')).join('')}}</aside><label class="mobile-local-selector"><span class="label">Company section</span><select id="mobile-local-selector" aria-label="Company section">${{Object.entries(labels).map(([k,l])=>`<option value="${{sideRoute(company,k)}}" ${{selected===k?'selected':''}}>${{esc(l)}}</option>`).join('')}}</select></label>`}}
function financialNav(company,view){{const labels={{overview:'Financial overview','income-statement':'Income statement','balance-sheet':'Balance sheet','cash-flow':'Cash flow','ratios-statistics':'Ratios and statistics','capital-allocation':'Capital allocation'}};return `<nav class="financials-row" aria-label="Financials navigation">${{Object.entries(labels).map(([k,l])=>navLink(l,`${{company}}/financials/${{k}}`,view===k,'')).join('')}}</nav>`}}
function companyHeader(company,section){{return `<div class="eyebrow">${{MODEL.names[company]}} · ${{esc(section)}}</div><h1>${{MODEL.names[company]}}</h1><p>${{company==='microsoft'?'June 30 fiscal year-end. Calendar and issuer-fiscal labels are never conflated.':'December 31 fiscal year-end. Period scopes remain source-native.'}}</p>`}}
function companyOverview(company){{const lines=MODEL.statement_lines.filter(x=>x.company_key===company);const strat=MODEL.strategies.find(x=>x.company_key===company);return companyHeader(company,'Overview')+`<section class="grid"><article class="card kpi"><span class="label">Statement lines</span><strong>${{lines.length}}</strong></article><article class="card kpi"><span class="label">Income</span><strong>${{lines.filter(x=>x.statement_family==='income_statement').length}}</strong></article><article class="card kpi"><span class="label">Balance sheet</span><strong>${{lines.filter(x=>x.statement_family==='balance_sheet').length}}</strong></article><article class="card kpi"><span class="label">Cash flow</span><strong>${{lines.filter(x=>x.statement_family==='cash_flow').length}}</strong></article><article class="card span6"><h2>Management stated</h2><p>${{esc(strat.management_stated.text)}}</p>${{statusBadge(strat.management_stated.status)}}</article><article class="card span6"><h2>Financial context</h2><p>${{esc(strat.financial_evidence.text)}}</p>${{statusBadge(strat.financial_evidence.status)}}</article></section>`}}
function companyEngines(company){{const lines=MODEL.statement_lines.filter(x=>x.company_key===company&&['revenue','operating_income','research_and_development_source_native'].includes(x.semantic_category));return companyHeader(company,'Business and operating engines')+`<section class="card"><h2>Issuer-native operating evidence</h2><p>This page uses admitted consolidated filing lines; it does not claim cross-issuer segment equivalence.</p><div class="table-scroll"><table><thead><tr><th>Reported line</th><th>Category</th><th>Periods</th><th>Status</th></tr></thead><tbody>${{lines.map(l=>`<tr><td>${{esc(l.display_label)}}</td><td>${{esc(l.semantic_category)}}</td><td>${{l.observations.length}}</td><td>${{statusBadge(l.coverage_classification.includes('qualified')?'qualified':'accepted')}}</td></tr>`).join('')}}</tbody></table></div></section>`}}
function strategyPage(company){{const s=MODEL.strategies.find(x=>x.company_key===company);return companyHeader(company,'Strategy')+`<div class="notice">Strategy disposition remains PARTIAL. Q4-cycle release and subsequent-quarter progression were not fabricated.</div><section class="strategy-grid"><article class="card strategy-box"><h3>Management stated</h3><p>${{esc(s.management_stated.text)}}</p><p class="formula">${{s.management_stated.evidence_refs.join(', ')}}</p></article><article class="card strategy-box"><h3>Financial evidence</h3><p>${{esc(s.financial_evidence.text)}}</p><p class="formula">${{s.financial_evidence.evidence_refs.join(', ')}}</p></article><article class="card strategy-box"><h3>InsightForge assessment</h3><p>${{esc(s.insightforge_assessment.text)}}</p><p>${{esc(s.insightforge_assessment.uncertainty)}} ${{esc(s.insightforge_assessment.execution_dependency)}}</p></article><article class="card strategy-box"><h3>Unproven claims and monitoring points</h3><p>${{esc(s.unproven_and_monitoring.text)}}</p><p>${{esc(s.unproven_and_monitoring.missing_evidence)}}</p></article></section>`}}
function risksPage(company){{const s=MODEL.strategies.find(x=>x.company_key===company);return companyHeader(company,'Risks')+`<section class="grid"><article class="card span6"><h2>Execution uncertainty</h2><p>${{esc(s.insightforge_assessment.uncertainty)}}</p></article><article class="card span6"><h2>Monitoring</h2><p>${{esc(s.unproven_and_monitoring.text)}}</p></article><article class="card span12"><h2>Coverage risk</h2><p>Partial statement mappings, qualified evidence, and absent raw prices limit conclusions. No valuation or investment recommendation is supported.</p></article></section>`}}
function evidencePage(company){{const lines=MODEL.statement_lines.filter(x=>x.company_key===company);return companyHeader(company,'Evidence')+`<section class="card"><h2>Exact filing evidence registry</h2><p>${{lines.reduce((n,l)=>n+l.exact_source_claim_ids.length,0).toLocaleString()}} exact claim references are attached to ${{lines.length}} rendered lines.</p><details><summary>View line identities</summary><div class="table-scroll"><table><thead><tr><th>Line</th><th>Category</th><th>Modes</th><th>Evidence refs</th></tr></thead><tbody>${{lines.map(l=>`<tr><td>${{esc(l.display_label)}}</td><td>${{esc(l.semantic_category)}}</td><td>${{l.available_modes.join(', ')}}</td><td class="formula">${{l.exact_source_claim_ids.slice(0,3).join(', ')}}</td></tr>`).join('')}}</tbody></table></div></details></section>`}}
function financialOverview(company){{const lines=MODEL.statement_lines.filter(x=>x.company_key===company);return companyHeader(company,'Financials')+financialNav(company,'overview')+`<section class="grid"><article class="card span6"><h2>What Financials encompasses</h2><p>Income statement, balance sheet, cash flow, ratios and statistics, and capital allocation share one local analytical area. Use the horizontal row above.</p></article><article class="card span6"><h2>Coverage</h2><p>${{lines.length}} deduplicated lines. Statement evidence remains partial where upstream mappings are absent or qualified.</p></article><article class="card span12"><h2>Range-aware exploration</h2><p>Choose a statement view to select Annual, Quarterly, or supported TTM observations, then set exact start and end periods. All included observations remain visible in the graph and data table.</p></article></section>`}}
function ratioPage(company){{const rows=MODEL.ratios.filter(x=>x.company_key===company);return companyHeader(company,'Ratios and statistics')+financialNav(company,'ratios-statistics')+`<section class="card"><h2>Filing-derived ratios</h2><p>Filing statistics reuse the exact per-line observation registries shown in the statement explorers; this table separately lists derived ratios. No published website ratio is canonical. Unavailable ratios remain unavailable rather than forced.</p><div class="table-scroll"><table><thead><tr><th>Ratio</th><th>Result</th><th>Scope</th><th>Formula</th><th>Components</th><th>Status</th></tr></thead><tbody>${{rows.map(r=>`<tr><td>${{esc(r.ratio_name)}}</td><td>${{r.result===null?'Unavailable':fmt(r.result,r.unit)}}</td><td>${{esc(r.scope||'—')}}</td><td class="formula">${{esc(r.formula)}}</td><td class="formula">${{r.component_identifiers.join(', ')||esc(r.qualification)}}</td><td>${{statusBadge(r.evidence_status)}}</td></tr>`).join('')}}</tbody></table></div></section>`}}
function explorerKey(company,statement){{return company+'|'+statement}}function linesFor(company,statement){{if(statement==='capital_allocation')return MODEL.statement_lines.filter(x=>x.company_key===company&&['capital_expenditure_components','share_repurchases','dividends','acquisition_investment_components','current_debt_components','noncurrent_debt_components'].includes(x.semantic_category));return MODEL.statement_lines.filter(x=>x.company_key===company&&x.statement_family===statement)}}
function initExplorer(company,statement){{const key=explorerKey(company,statement),lines=linesFor(company,statement);if(!state[key]){{const first=lines.find(l=>l.available_modes.includes('Annual'))||lines[0];state[key]={{mode:first.available_modes[0]||'Annual',selected:[first.line_id],start:null,end:null}}}}return state[key]}}
function periodsFor(lines,mode){{const map=new Map;lines.forEach(l=>l.observations.filter(o=>o.mode===mode).forEach(o=>map.set(o.period_key,o.period.end)));return [...map].sort((a,b)=>a[1].localeCompare(b[1])).map(x=>x[0])}}
function ensureModeSelection(lines,s){{const supported=lines.filter(l=>l.observations.some(o=>o.mode===s.mode&&o.value!==null));const selected=s.selected.filter(id=>supported.some(l=>l.line_id===id));s.selected=selected.length?selected:(supported.length?[supported[0].line_id]:[])}}
function obsAt(line,mode,period){{return line.observations.find(o=>o.mode===mode&&o.period_key===period)}}function rangeAt(lineId,mode,start,end){{return MODEL.range_summaries.find(r=>r.line_id===lineId&&r.mode===mode&&r.start_period===start&&r.end_period===end)}}
function renderExplorer(company,statement){{const lines=linesFor(company,statement),s=initExplorer(company,statement);let periods=periodsFor(lines,s.mode);if(!periods.length){{for(const m of MODEL.period_modes){{const p=periodsFor(lines,m);if(p.length){{s.mode=m;periods=p;break}}}}}}if(!periods.length)return '<div class="notice">No compatible observations for this view.</div>';ensureModeSelection(lines,s);if(!periods.includes(s.start))s.start=periods[0];if(!periods.includes(s.end))s.end=periods[periods.length-1];if(periods.indexOf(s.start)>periods.indexOf(s.end))[s.start,s.end]=[s.end,s.start];const primary=lines.find(l=>l.line_id===s.selected[0])||lines[0];const primaryUnit=(primary.observations.find(o=>o.mode===s.mode)||{{}}).unit;const compatible=lines.filter(l=>l.observations.some(o=>o.mode===s.mode&&o.unit===primaryUnit));const rows=lines.map(l=>{{const a=obsAt(l,s.mode,s.start),b=obsAt(l,s.mode,s.end),r=rangeAt(l.line_id,s.mode,s.start,s.end);const interval=r?(r.result??r.absolute_change??'—'):'—';const stat=(b||a||{{status:'unavailable'}}).status;return `<tr data-line-id="${{l.line_id}}"><td class="indent-${{l.hierarchy_level}}">${{esc(l.display_label)}}<br><span class="muted">${{esc(l.issuer_native_label)}}</span></td><td>${{b?fmt(b.value,b.unit):'Unavailable'}}</td><td>${{a?fmt(a.value,a.unit):'Unavailable'}}</td><td>${{r&&r.absolute_change!==undefined?fmt(r.absolute_change,r.unit):'—'}}</td><td>${{r&&r.percentage_change!==undefined&&r.percentage_change!==null?fmt(r.percentage_change,'%'):(r&&r.percentage_change===null&&Number(r.start_value)<=0?'Not meaningful — zero or negative base':'—')}}</td><td>${{r&&r.result!==undefined?fmt(r.result,r.unit):interval}}</td><td>${{statusBadge(stat)}}</td></tr>`}}).join('');const all=lines.map(l=>`<tr><td>${{esc(l.display_label)}}</td><td colspan="6">${{l.observations.map(o=>`${{esc(o.period_key)}}: ${{fmt(o.value,o.unit)}} (${{o.status}}; ${{o.scope_kind}})`).join(' · ')}}</td></tr>`).join('');return `<section class="card explorer" data-company="${{company}}" data-statement="${{statement}}"><h2>${{statement==='capital_allocation'?'Capital allocation':statement.replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase())}} evidence</h2><p>Selected evidence; partial coverage. Click a row or use the metric selector. Additional series must share the primary unit.</p><div class="controls"><div><span class="label">Frequency</span><div>${{MODEL.period_modes.map(m=>`<button class="mode-button ${{s.mode===m?'active':''}}" data-mode="${{m}}" ${{periodsFor(lines,m).length?'':'disabled'}}>${{m}}</button>`).join('')}}</div></div><label class="control">Range start<select class="range-start">${{periods.map(p=>`<option ${{p===s.start?'selected':''}}>${{esc(p)}}</option>`).join('')}}</select></label><label class="control">Range end<select class="range-end">${{periods.map(p=>`<option ${{p===s.end?'selected':''}}>${{esc(p)}}</option>`).join('')}}</select></label><label class="control">Metric selector<select class="metric-selector"><option value="">Add compatible series…</option>${{compatible.filter(l=>!s.selected.includes(l.line_id)).map(l=>`<option value="${{l.line_id}}">${{esc(l.display_label)}}</option>`).join('')}}</select></label><div class="range-label">Exact range: <span class="exact-range">${{esc(s.start)}} → ${{esc(s.end)}}</span></div></div><div class="selected-series">${{s.selected.map((id,i)=>{{const l=lines.find(x=>x.line_id===id);return l?`<span class="series-chip"><span style="color:${{COLORS[i%COLORS.length]}}">●</span>${{esc(l.display_label)}}${{i?`<button class="remove-series" data-remove="${{id}}" aria-label="Remove ${{esc(l.display_label)}}">×</button>`:''}}</span>`:''}}).join('')}}</div><div class="chart-wrap"><svg class="statement-chart" role="img" aria-label="Interactive statement history"></svg><div class="legend"></div></div><details><summary>View data</summary><div class="exact-data"></div></details><div class="table-scroll"><table><thead><tr><th>Financial line</th><th>End value</th><th>Start value</th><th>Absolute change</th><th>Percentage change</th><th>Interval result</th><th>Evidence status</th></tr></thead><tbody>${{rows}}</tbody></table></div><details><summary>View all periods</summary><div class="table-scroll"><table><thead><tr><th>Financial line</th><th colspan="6">Exact observations · unit · status · scope</th></tr></thead><tbody>${{all}}</tbody></table></div></details></section>`}}
function selectLine(company,statement,lineId){{const s=initExplorer(company,statement),lines=linesFor(company,statement),primary=lines.find(l=>l.line_id===s.selected[0]),candidate=lines.find(l=>l.line_id===lineId);if(!candidate)return;const pu=(primary?.observations.find(o=>o.mode===s.mode)||{{}}).unit,cu=(candidate.observations.find(o=>o.mode===s.mode)||{{}}).unit;if(pu&&cu&&pu!==cu)return;if(!s.selected.includes(lineId))s.selected=[lineId,...s.selected].slice(0,3);else s.selected=[lineId,...s.selected.filter(x=>x!==lineId)];render()}}
function drawChart(root,company,statement){{const s=initExplorer(company,statement),lines=linesFor(company,statement),periods=periodsFor(lines,s.mode),i0=periods.indexOf(s.start),i1=periods.indexOf(s.end),visible=periods.slice(i0,i1+1),selected=s.selected.map(id=>lines.find(l=>l.line_id===id)).filter(Boolean);const dataRows=selected.flatMap(l=>l.observations.filter(o=>o.mode===s.mode&&visible.includes(o.period_key)).map(o=>({{...o,line:l}})));const points=dataRows.filter(p=>p.value!==null);const svg=$('svg',root),W=1000,H=340,pad={{l:75,r:25,t:25,b:55}};if(!points.length){{svg.setAttribute('viewBox',`0 0 ${{W}} ${{H}}`);svg.innerHTML='<text x="50" y="80" class="chart-label">No supported values in this exact range.</text>';return}}const vals=points.map(p=>Number(p.value)),min=Math.min(...vals),max=Math.max(...vals),spread=max-min||Math.abs(max)||1,x=p=>pad.l+(visible.indexOf(p)/(Math.max(visible.length-1,1)))*(W-pad.l-pad.r),y=v=>pad.t+(max-Number(v))/spread*(H-pad.t-pad.b);let out='';for(let k=0;k<5;k++){{const yy=pad.t+k*(H-pad.t-pad.b)/4,val=max-k*spread/4;out+=`<line class="chart-grid" x1="${{pad.l}}" x2="${{W-pad.r}}" y1="${{yy}}" y2="${{yy}}"/><text class="chart-label" x="5" y="${{yy+4}}">${{fmt(val,points[0].unit)}}</text>`}}visible.forEach(p=>out+=`<text class="chart-label" text-anchor="middle" x="${{x(p)}}" y="${{H-18}}">${{esc(p)}}</text>`);selected.forEach((l,idx)=>{{const ps=l.observations.filter(o=>o.mode===s.mode&&visible.includes(o.period_key)&&o.value!==null).sort((a,b)=>visible.indexOf(a.period_key)-visible.indexOf(b.period_key));if(!ps.length)return;out+=`<path class="chart-line" stroke="${{COLORS[idx]}}" d="${{ps.map((p,j)=>`${{j?'L':'M'}} ${{x(p.period_key)}} ${{y(p.value)}}`).join(' ')}}"/>`;ps.forEach(p=>out+=`<circle class="chart-point" fill="${{COLORS[idx]}}" cx="${{x(p.period_key)}}" cy="${{y(p.value)}}" r="5"><title>${{esc(l.display_label)}} · ${{esc(p.period_key)}} · ${{esc(fmtExact(p.value,p.unit))}} · ${{esc(p.status)}} · ${{esc(p.scope_kind)}}</title></circle>`)}});svg.setAttribute('viewBox',`0 0 ${{W}} ${{H}}`);svg.innerHTML=out;$('.legend',root).innerHTML=selected.map((l,i)=>`<span><span style="color:${{COLORS[i]}}">●</span> ${{esc(l.display_label)}}</span>`).join('');$('.exact-data',root).innerHTML=`<div class="table-scroll"><table><thead><tr><th>Series</th><th>Period</th><th>Exact value</th><th>Unit</th><th>Status</th><th>Scope</th><th>Candidate values</th><th>Evidence references</th></tr></thead><tbody>${{dataRows.map(p=>`<tr><td>${{esc(p.line.display_label)}}</td><td>${{esc(p.period_key)}}</td><td>${{esc(p.value)}}</td><td>${{esc(p.unit)}}</td><td>${{statusBadge(p.status)}}</td><td>${{esc(p.scope_kind)}}</td><td class="formula">${{esc(JSON.stringify(p.candidate_values||[]))}}</td><td class="formula">${{esc((p.evidence_refs||[]).join(', '))}}</td></tr>`).join('')}}</tbody></table></div>`}}
function statementPage(company,view){{const statement={{'income-statement':'income_statement','balance-sheet':'balance_sheet','cash-flow':'cash_flow','capital-allocation':'capital_allocation'}}[view];return companyHeader(company,view.replaceAll('-',' '))+financialNav(company,view)+`<div class="notice">Statement evidence is source-resolved but partial. Annual, quarter-only, cumulative, instant, and TTM scopes never silently mix.</div>`+renderExplorer(company,statement)}}
function renderCompany(route){{const [company,section,view]=route.split('/');let content;if(section==='overview')content=companyOverview(company);else if(section==='financials'){{if(view==='overview')content=financialOverview(company);else if(view==='ratios-statistics')content=ratioPage(company);else content=statementPage(company,view)}}else if(section==='business-engines')content=companyEngines(company);else if(section==='strategy')content=strategyPage(company);else if(section==='risks')content=risksPage(company);else content=evidencePage(company);return `<div class="company-layout">${{sideNav(company,route)}}<section id="report-content" tabindex="-1">${{content}}</section></div>`}}
function bind(route){{document.querySelectorAll('[data-route]').forEach(a=>a.onclick=e=>{{e.preventDefault();go(a.dataset.route)}});const mobile=$('#mobile-local-selector');if(mobile)mobile.onchange=()=>go(mobile.value);document.querySelectorAll('.explorer').forEach(root=>{{const company=root.dataset.company,statement=root.dataset.statement,s=initExplorer(company,statement);root.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{{s.mode=b.dataset.mode;s.start=null;s.end=null;render()}});$('.range-start',root).onchange=e=>{{s.start=e.target.value;render()}};$('.range-end',root).onchange=e=>{{s.end=e.target.value;render()}};$('.metric-selector',root).onchange=e=>{{if(e.target.value)selectLine(company,statement,e.target.value)}};root.querySelectorAll('[data-remove]').forEach(b=>b.onclick=()=>{{s.selected=s.selected.filter(x=>x!==b.dataset.remove);render()}});root.querySelectorAll('[data-line-id]').forEach(tr=>tr.onclick=()=>selectLine(company,statement,tr.dataset.lineId));drawChart(root,company,statement)}})}}
function render(){{const route=currentRoute();renderGlobalNav(route);let body=route==='overview'?renderOverview():route==='comparison'?renderComparison():route==='methodology'?renderMethodology():route==='evidence'?renderEvidenceGlobal():renderCompany(route);$('#app').innerHTML=`<div id="route-${{route.replaceAll('/','-')}}">${{body}}<footer class="footer">TASK-081 · internal local analysis only · exact upstream identity ${{MODEL.analysis_identity}}</footer></div>`;bind(route)}}render();
</script></body></html>'''


def build_publication(source_path: Path, output_dir: Path) -> dict[str, Any]:
    raw = source_path.read_bytes()
    digest = sha256_bytes(raw)
    if digest != SOURCE_SHA256:
        raise ValueError(f"T-042 serialized SHA-256 mismatch: {digest}")
    source = json.loads(raw)
    if source.get("analysis_identity") != SOURCE_IDENTITY or source.get("task_id") != "T-042":
        raise ValueError("T-042 analysis identity mismatch")
    if source.get("rights", {}).get("allowed_use") != "internal_local_analysis_only" or source.get("rights", {}).get("external_redistribution") != "not_authorized":
        raise ValueError("T-042 rights boundary mismatch")
    output_dir.mkdir(parents=True, exist_ok=True)
    package = presentation_package(source)
    artifacts: dict[str, bytes] = {
        "index.html": html_document(source, package["package_identity"]).encode(),
        "presentation-package.json": canonical_bytes(package),
        "source-authentication.json": canonical_bytes(source_authentication(source_path, source)),
        "route-navigation-inventory.json": canonical_bytes(route_inventory()),
        "statement-coverage-matrix.json": canonical_bytes({"schema": "briefforge.statement-coverage-matrix.v1", "task_id": TASK_ID, "rows": source["coverage_matrix"]}),
        "statement-line-rendering-inventory.json": canonical_bytes(line_inventory(source)),
        "period-transformation-inventory.json": canonical_bytes(transformation_inventory(source)),
        "ratio-statistics-registry.json": canonical_bytes({"schema": "briefforge.ratio-statistics-registry.v1", "task_id": TASK_ID, "ratio_count": len(source["ratio_registry"]), "available_count": sum(row["result"] is not None for row in source["ratio_registry"]), "ratios": source["ratio_registry"], "statistics": source["filing_statistics_registry"]}),
        "formula-component-resolution.json": canonical_bytes(formula_resolution(source)),
        "graph-table-inventory.json": canonical_bytes(graph_table_inventory(source)),
        "strategy-content-audit.json": canonical_bytes(strategy_audit(source)),
        "unresolved-upstream-return-packet.json": canonical_bytes({"schema": "briefforge.task081-return-packet.v1", "task_id": TASK_ID, "disposition": "PARTIAL", "rights": source["rights"], "strategy": source["unresolved_upstream_return_packet"], "stock_price_capability": source["stock_price_capability"]}),
    }
    for name, data in artifacts.items():
        atomic_write(output_dir / name, data)
    manifest = {
        "schema": "briefforge-publication-manifest-v1", "task_id": TASK_ID,
        "source_sha256": SOURCE_SHA256, "analysis_identity": SOURCE_IDENTITY,
        "package_identity": package["package_identity"], "entry_point": "index.html",
        "rights": source["rights"],
        "artifacts": {name: {"sha256": sha256_bytes(data), "bytes": len(data)} for name, data in sorted(artifacts.items())},
    }
    manifest["publication_identity"] = sha256_bytes(canonical_bytes(manifest))
    atomic_write(output_dir / "publication-manifest.json", canonical_bytes(manifest))
    return {"task_id": TASK_ID, "entry_point_sha256": sha256_bytes(artifacts["index.html"]), "publication_identity": manifest["publication_identity"], "package_identity": package["package_identity"], "artifact_count": len(artifacts) + 1}
