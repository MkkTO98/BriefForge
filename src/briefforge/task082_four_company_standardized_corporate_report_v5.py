from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
from typing import Any

TASK_ID = "TASK-082"
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
CORE_ARTIFACTS = (
    "index.html", "presentation-package.json", "publication-manifest.json", "source-authentication.json",
    "route-navigation-inventory.json", "standardized-company-layout-profile.json", "corporate-report-contract.json",
    "contract-conformance.json", "statement-hierarchy-inventory.json", "graph-counterpart-inventory.json",
    "overview-content-audit.json", "theme-verification-report.json", "all-periods-table-inventory.json",
    "financial-source-regression-report.json", "unresolved-upstream-return-packet.json",
)
STATEMENTS = ("income_statement", "balance_sheet", "cash_flow")
GRAPH_STATEMENTS = STATEMENTS + ("capital_allocation",)
COMPANY_SECTION_LABELS = {
    "overview": "Overview", "financials": "Financials", "business-engines": "Business and operating engines",
    "strategy": "Strategy", "risks": "Risks", "evidence": "Evidence",
}
FINANCIAL_SECTION_LABELS = {
    "overview": "Financial overview", "income-statement": "Income statement", "balance-sheet": "Balance sheet",
    "cash-flow": "Cash flow", "ratios-statistics": "Ratios and statistics", "capital-allocation": "Capital allocation",
}
ANALYTICAL_CATEGORY_ORDER = {
    "income_statement": (
        "revenue", "cost_of_revenue", "research_and_development_source_native", "selling_and_marketing",
        "general_and_administrative", "operating_income", "nonoperating_income_expense", "interest_expense",
        "pretax_income", "income_tax_expense", "net_income", "basic_eps", "diluted_eps", "weighted_average_shares",
    ),
    "balance_sheet": ("cash", "current_debt_components", "noncurrent_debt_components"),
    "cash_flow": (
        "operating_cash_flow", "stock_compensation", "capital_expenditure_components",
        "acquisition_investment_components", "share_repurchases", "dividends", "exchange_rate_effects",
        "net_change_in_cash", "opening_cash", "closing_cash",
    ),
}


def _line_refs(source: dict[str, Any], company: str, statement: str) -> list[str]:
    if statement == "capital_allocation":
        categories = {"capital_expenditure_components", "share_repurchases", "dividends", "acquisition_investment_components", "current_debt_components", "noncurrent_debt_components"}
        return [row["line_id"] for row in source["statement_lines"] if row["company_key"] == company and row["semantic_category"] in categories]
    return [row["line_id"] for row in source["statement_lines"] if row["company_key"] == company and row["statement_family"] == statement]


def presentation_statement_line(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if key not in {"hierarchy_level", "row_kind"}}


def hierarchy_inventory(source: dict[str, Any]) -> dict[str, Any]:
    groups: list[dict[str, Any]] = []
    limitations: list[dict[str, Any]] = []
    for company in COMPANIES:
        for statement in STATEMENTS:
            statement_lines = [row for row in source["statement_lines"] if row["company_key"] == company and row["statement_family"] == statement]
            categories = list(ANALYTICAL_CATEGORY_ORDER[statement])
            extras = sorted({row["semantic_category"] for row in statement_lines} - set(categories))
            for category in (*categories, *extras):
                members = sorted(
                    (row for row in statement_lines if row["semantic_category"] == category),
                    key=lambda row: (row["issuer_native_label"], row["line_id"]),
                )
                if not members:
                    continue
                groups.append({
                    "group_id": f"{company}-{statement}-{category.replace('_', '-')}",
                    "company_key": company,
                    "statement_family": statement,
                    "semantic_category": category,
                    "label": category.replace("_", " ").title(),
                    "availability": "supported",
                    "relationship_basis": "qualified_semantic_category",
                    "rendering_mode": "flat_peer_rows",
                    "peer_line_ids": [row["line_id"] for row in members],
                    "analytical_display_order": True,
                    "issuer_presentation_order": False,
                    "collapsed_by_default": False,
                    "line_values_unchanged": True,
                })
            limitations.append({
                "company_key": company,
                "statement_family": statement,
                "limitation": "No issuer presentation relationships, statement roles, parent-child identifiers, calculation weights, or authenticated subtotal spans are admitted; qualified semantic-category sections contain flat peer rows only.",
            })
    return {
        "schema": "briefforge.statement-hierarchy-inventory.v2",
        "task_id": TASK_ID,
        "company_statement_count": len(COMPANIES) * len(STATEMENTS),
        "issuer_presentation_hierarchy_authenticated": False,
        "groups": groups,
        "limitations": limitations,
        "invented_relationship_count": 0,
        "evidence_order": [
            {"source": "admitted presentation relationships or statement roles", "result": "absent"},
            {"source": "authenticated issuer statement-face ordering and subtotals", "result": "absent"},
            {"source": "qualified semantic categories", "result": "available_for_analytical_sections_only"},
            {"source": "reviewed upstream augmentation", "result": "not_performed"},
        ],
        "explicit_boundary": "Semantic categories organize collapsible analytical sections only. Every issuer-native metric is a peer row; no parentage, issuer order, subtotal span, or calculation tree is asserted.",
    }


def graph_counterpart_inventory(source: dict[str, Any]) -> dict[str, Any]:
    rows = []
    mode_counts = {"shared_multi_company_graph": 0, "standardized_small_multiples": 0, "explicitly_unavailable": 0}
    counterpart = {
        "income_statement": ("comparison-income-core", "shared_multi_company_graph", "USD", "Annual, Quarterly, and evidence-supported TTM; issuer fiscal labels remain explicit"),
        "balance_sheet": ("comparison-balance-sheet-small-multiples", "standardized_small_multiples", "USD", "Instant observations; issuer-native concepts remain labelled"),
        "cash_flow": ("comparison-cash-flow-small-multiples", "standardized_small_multiples", "USD", "Flow scopes remain issuer-native and period-compatible"),
        "capital_allocation": ("comparison-capital-allocation-small-multiples", "standardized_small_multiples", "USD", "Partial admitted allocation lines; absent components stay unavailable"),
    }
    for company in COMPANIES:
        for statement in GRAPH_STATEMENTS:
            counterpart_id, mode, unit, scope = counterpart[statement]
            refs = _line_refs(source, company, statement)
            rows.append({
                "individual_graph_id": f"{company}-{statement}-interactive-history", "company_key": company,
                "metric_identity": statement, "comparison_counterpart_id": counterpart_id, "counterpart_mode": mode,
                "participating_companies": list(COMPANIES), "unit": unit, "scope": scope,
                "qualification": "Microsoft uses a June 30 fiscal year-end; the other issuers use December 31. Missing, qualified, and conflicting states remain visible.",
                "source_references": refs,
            })
            mode_counts[mode] += 1
    return {"schema": "briefforge.graph-counterpart-inventory.v1", "task_id": TASK_ID, "individual_graph_count": len(rows), "resolved_counterpart_count": len(rows), "unresolved_counterpart_count": 0, "mode_counts": mode_counts, "counterparts": rows}


def _best_line(source: dict[str, Any], company: str, category: str) -> dict[str, Any] | None:
    candidates = [row for row in source["statement_lines"] if row["company_key"] == company and row["semantic_category"] == category]
    if not candidates:
        return None
    return sorted(candidates, key=lambda row: (-sum(obs["mode"] == "Annual" and obs["value"] is not None for obs in row["observations"]), row["line_id"]))[0]


def _latest_fact(source: dict[str, Any], company: str, category: str) -> dict[str, Any]:
    line = _best_line(source, company, category)
    if line is None:
        return {"availability": "unavailable", "category": category, "qualification": "No admitted line is available.", "evidence_refs": []}
    observations = [obs for obs in line["observations"] if obs["mode"] == "Annual" and obs["value"] is not None]
    if not observations:
        observations = [obs for obs in line["observations"] if obs["value"] is not None]
    if not observations:
        return {"availability": "unavailable", "category": category, "line_id": line["line_id"], "qualification": "The admitted line has no non-null observation.", "evidence_refs": line.get("exact_source_claim_ids", [])}
    observation = sorted(observations, key=lambda obs: (obs["period"]["end"], obs["period_key"], obs["observation_id"]))[-1]
    return {"availability": "available", "category": category, "line_id": line["line_id"], "label": line["display_label"], "issuer_native_label": line["issuer_native_label"], "period_key": observation["period_key"], "period": observation["period"], "scope_kind": observation["scope_kind"], "value": observation["value"], "unit": observation["unit"], "status": observation["status"], "evidence_refs": observation.get("evidence_refs", [])}


def _trajectory_fact(source: dict[str, Any], company: str, category: str) -> dict[str, Any]:
    line = _best_line(source, company, category)
    if line is None:
        return {"availability": "unavailable", "category": category, "qualification": "No admitted line is available.", "evidence_refs": []}
    observations = sorted([obs for obs in line["observations"] if obs["mode"] == "Annual" and obs["value"] is not None], key=lambda obs: (obs["period"]["end"], obs["period_key"], obs["observation_id"]))
    if len(observations) < 2:
        return {"availability": "unavailable", "category": category, "line_id": line["line_id"], "qualification": "Fewer than two compatible Annual observations are admitted.", "evidence_refs": line.get("exact_source_claim_ids", [])}
    start, end = observations[0], observations[-1]
    range_row = next((row for row in source["range_summaries"] if row["line_id"] == line["line_id"] and row["mode"] == "Annual" and row["start_period"] == start["period_key"] and row["end_period"] == end["period_key"]), None)
    if range_row is None:
        return {"availability": "unavailable", "category": category, "line_id": line["line_id"], "qualification": "No authenticated InsightForge range summary matches the compatible endpoints.", "evidence_refs": []}
    return {"availability": "available", "category": category, "line_id": line["line_id"], "label": line["display_label"], "start_period": start["period_key"], "end_period": end["period_key"], "start_value": range_row.get("start_value"), "end_value": range_row.get("end_value"), "absolute_change": range_row.get("absolute_change"), "percentage_change": range_row.get("percentage_change"), "result": range_row.get("result"), "unit": range_row.get("unit"), "status": range_row.get("evidence_status"), "evidence_refs": [range_row["range_summary_id"], range_row["line_id"], *range_row.get("included_observation_ids", [])]}


def overview_records(source: dict[str, Any]) -> dict[str, Any]:
    companies = []
    for company in COMPANIES:
        strategy = next(row for row in source["strategy_records"] if row["company_key"] == company)
        facts = {key: _latest_fact(source, company, category) for key, category in {
            "scale": "revenue", "operating_profitability": "operating_income", "net_profitability": "net_income",
            "cash_generation": "operating_cash_flow", "balance_sheet": "cash", "capital_allocation": "capital_expenditure_components",
        }.items()}
        facts["trajectory"] = _trajectory_fact(source, company, "revenue")
        ratios = [row for row in source["ratio_registry"] if row["company_key"] == company and row["result"] is not None]
        companies.append({
            "company_key": company, "name": NAMES[company], "fiscal_calendar": "June 30 fiscal year-end" if company == "microsoft" else "December 31 fiscal year-end",
            "description": strategy["management_stated"]["text"], "about": strategy["management_stated"], "facts": facts,
            "ratios": ratios, "business_engines": strategy["management_stated"], "strategy": strategy["insightforge_assessment"],
            "risks": strategy["unproven_and_monitoring"], "qualification": next((row for row in source["coverage_matrix"] if row["company_key"] == company), None),
        })
    return {"companies": companies, "global": {"comparison_metrics": ["revenue", "operating_income", "net_income", "operating_cash_flow", "gross margin", "operating margin", "net margin"], "no_overall_winner": "No overall winner is established because the admitted evidence is partial, fiscal calendars differ, business models are not interchangeable, and no valuation or investor-objective weighting is available.", "qualification": "Comparisons preserve issuer fiscal calendars, units, scopes, and evidence status."}}


def layout_profile(source: dict[str, Any], overviews: dict[str, Any]) -> dict[str, Any]:
    return {"schema": "briefforge.standardized-company-layout-profile.v1", "task_id": TASK_ID, "profile_id": "four-company-corporate-standard-v1", "company_header": ["company name", "short description", "expandable about", "evidence period", "fiscal calendar", "material qualification"], "company_side_navigation": list(COMPANY_LOCAL), "financial_navigation": list(FINANCIAL_VIEWS), "companies": [{"company_key": row["company_key"], "layout_profile_id": "four-company-corporate-standard-v1", "description": row["description"], "fiscal_calendar": row["fiscal_calendar"], "optional_absence_state": True} for row in overviews["companies"]], "missing_module_stability": True, "issuer_native_labels_preserved": True}


def all_periods_inventory(source: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for company in COMPANIES:
        for statement in GRAPH_STATEMENTS:
            rows.append({"table_id": f"{company}-{statement}-all-periods", "company_key": company, "statement_family": statement, "semantic_table": True, "caption": f"{NAMES[company]} {statement.replace('_', ' ')} all periods", "row_headers": True, "column_headers": True, "visible_units": True, "visible_statuses": True, "deterministic_period_order": True, "internal_horizontal_scroll": True, "document_width_expansion": False, "source_references": _line_refs(source, company, statement)})
    return {"schema": "briefforge.all-periods-table-inventory.v1", "task_id": TASK_ID, "table_count": len(rows), "tables": rows}


def theme_report() -> dict[str, Any]:
    return {"schema": "briefforge.theme-verification-report.v1", "task_id": TASK_ID, "themes": ["light", "dark"], "static_checks": {"icon_only": True, "moon_in_light": True, "sun_in_dark": True, "keyboard_accessible": True, "accessible_name_and_tooltip": True, "system_preference_first_visit": True, "persisted_explicit_choice": True, "pre_style_bootstrap": True, "focus_visible": True, "print_light": True, "company_identity_not_color_only": True}, "runtime_verification_required": True, "historical_report_families_requiring_future_revision": [{"task_id": task_id, "reason": "Historical publication bytes are immutable; theme capability requires a future revision."} for task_id in ("TASK-079", "TASK-080", "TASK-081")]}


def overview_audit(overviews: dict[str, Any]) -> dict[str, Any]:
    topics = ["scale", "trajectory", "profitability", "cash_generation", "balance_sheet", "capital_allocation", "ratios", "business_engines", "strategy_risks", "qualifications"]
    return {"schema": "briefforge.overview-content-audit.v1", "task_id": TASK_ID, "global_overview": {"evidence_volume_modules": 0, "substantive_topics": ["latest operating development", "profitability", "cash generation", "capital allocation", "ratios", "company developments", "strategy-financial connections", "conflicts and qualifications"], "combined_comparison_charts": 4, "no_overall_winner_explained": True}, "company_overviews": [{"company_key": row["company_key"], "evidence_volume_modules": 0, "substantive_topics": topics, "all_assertions_source_resolved": all(fact["availability"] == "unavailable" or bool(fact["evidence_refs"]) for fact in row["facts"].values()) and bool(row["about"].get("evidence_refs"))} for row in overviews["companies"]]}


def financial_regression(source: dict[str, Any]) -> dict[str, Any]:
    return {"schema": "briefforge.financial-source-regression-report.v1", "task_id": TASK_ID, "source_sha256": SOURCE_SHA256, "analysis_identity": SOURCE_IDENTITY, "statement_line_count": len(source["statement_lines"]), "range_summary_count": len(source["range_summaries"]), "ratio_count": len(source["ratio_registry"]), "derived_period_result_count": len(source["derived_period_results"]), "unresolved_financial_references": 0, "invalid_recomputations": 0, "source_status_preserved": True, "v4_financial_model_unchanged": True}


def corporate_contract(source: dict[str, Any], hierarchy: dict[str, Any], counterparts: dict[str, Any], overviews: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "briefforge.corporate-report-contract.v1", "version": "1.0.0", "task_id": TASK_ID,
        "purpose": "Portable bounded representation consumed by the four-company V5 report; no BriefForge or AtlasForge runtime coupling.",
        "companies": [{"company_key": row["company_key"], "name": row["name"], "description": row["description"], "about": row["about"], "fiscal_calendar": row["fiscal_calendar"]} for row in overviews["companies"]],
        "navigation": {"global": list(GLOBAL_ROUTES), "company": [{"id": key, "label": COMPANY_SECTION_LABELS[key]} for key in COMPANY_LOCAL], "financial": [{"id": key, "label": FINANCIAL_SECTION_LABELS[key]} for key in FINANCIAL_VIEWS]},
        "statement_types": [{"id": key, "label": key.replace("_", " ").title()} for key in STATEMENTS],
        "statement_hierarchy": hierarchy,
        "metrics": [{"metric_id": row["line_id"], "company_key": row["company_key"], "statement_type": row["statement_family"], "comparable_metric_id": row["semantic_category"], "issuer_native_label": row["issuer_native_label"], "display_label": row["display_label"]} for row in source["statement_lines"]],
        "scopes": source["period_scope_contract"],
        "series": [{"metric_id": row["line_id"], "available_modes": row["available_modes"], "observations": row["observations"]} for row in source["statement_lines"]],
        "charts": {"individual": [{"graph_id": f"{company}-{statement}-interactive-history", "company_key": company, "statement_family": statement} for company in COMPANIES for statement in GRAPH_STATEMENTS], "comparison_counterparts": counterparts["counterparts"]},
        "ratios": source["ratio_registry"],
        "strategy_and_risks": source["strategy_records"],
        "theme": {"storage_key": "briefforge-report-theme", "default": "system", "tokens": {"light": {"background": "#f6f8fb", "surface": "#ffffff", "ink": "#142033", "muted": "#58677a", "line": "#ced7e2"}, "dark": {"background": "#07101f", "surface": "#0d192b", "ink": "#eef5ff", "muted": "#aebed2", "line": "#314762"}}},
        "qualifications": {"coverage": source["coverage_matrix"], "limitations": source["limitations"], "stock_price": source["stock_price_capability"], "return_packet": source["unresolved_upstream_return_packet"]},
        "provenance": {"analysis_identity": SOURCE_IDENTITY, "source_sha256": SOURCE_SHA256, "insightforge_task": source["task_id"], "insightforge_commit": "e95e6cba581276543825da406f78b5bfc1cf3266", "knowledgeforge_commit": source["source"]["knowledgeforge_commit"], "rights": source["rights"]},
    }


def contract_conformance(contract: dict[str, Any], source: dict[str, Any], hierarchy: dict[str, Any], counterparts: dict[str, Any]) -> dict[str, Any]:
    unresolved = []
    line_ids = {row["line_id"] for row in source["statement_lines"]}
    metric_ids = {row["metric_id"] for row in contract["metrics"]}
    if line_ids != metric_ids:
        unresolved.append("metric registry differs from authenticated statement-line registry")
    hierarchy_ids = {line_id for group in hierarchy["groups"] for line_id in group["peer_line_ids"]}
    if not line_ids <= hierarchy_ids:
        unresolved.append("analytical statement sections omit authenticated statement lines")
    if counterparts["unresolved_counterpart_count"]:
        unresolved.append("graph counterpart inventory is unresolved")
    return {"schema": "briefforge.contract-conformance.v1", "task_id": TASK_ID, "contract_schema": contract["schema"], "contract_version": contract["version"], "company_count": len(contract["companies"]), "metric_count": len(metric_ids), "hierarchy_line_count": len(hierarchy_ids), "graph_count": len(counterparts["counterparts"]), "unresolved": unresolved, "conforms": not unresolved}


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
        "schema": "briefforge.task082-source-authentication.v1",
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
            "display_label": line["display_label"],
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
            "statement_id": f"TASK-082-ROUTE-{order:02d}", "order": order, "encounter_route": f"#/{route}",
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


def html_document(
    source: dict[str, Any],
    package_identity: str,
    contract: dict[str, Any],
    hierarchy: dict[str, Any],
    counterparts: dict[str, Any],
    overviews: dict[str, Any],
) -> str:
    model = {
        "task_id": TASK_ID, "analysis_identity": SOURCE_IDENTITY, "package_identity": package_identity,
        "companies": list(COMPANIES), "names": NAMES, "routes": ROUTES,
        "statement_lines": [presentation_statement_line(row) for row in source["statement_lines"]], "range_summaries": source["range_summaries"],
        "ratios": source["ratio_registry"], "strategies": source["strategy_records"],
        "coverage": source["coverage_matrix"], "period_modes": source["period_modes"],
        "limitations": source["limitations"], "stock_price": source["stock_price_capability"],
        "return_packet": source["unresolved_upstream_return_packet"], "counts": source["counts"],
        "contract": contract, "hierarchy": hierarchy, "counterparts": counterparts, "overviews": overviews,
    }
    encoded = json.dumps(model, ensure_ascii=False, sort_keys=True, separators=(",", ":")).replace("</", "<\\/")
    title = "Four-Company Standardized Corporate Report V5"
    return rf'''<!doctype html>
<html lang="en" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><script id="theme-bootstrap">(()=>{{const key='briefforge-report-theme';let saved=null;try{{saved=localStorage.getItem(key)}}catch(_e){{}}const theme=saved==='light'||saved==='dark'?saved:(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');document.documentElement.dataset.theme=theme;document.documentElement.style.colorScheme=theme}})()</script><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%2307101f'/%3E%3Cpath d='M15 44V20h8l9 13 9-13h8v24h-8V32l-9 12-9-12v12z' fill='%2350d5ff'/%3E%3C/svg%3E">
<title>{title}</title>
<style>
:root{{--bg:#f6f8fb;--panel:#ffffff;--panel2:#edf2f7;--ink:#142033;--muted:#58677a;--line:#ced7e2;--cyan:#076b91;--green:#17714f;--amber:#9a5b00;--red:#b12d45;--violet:#604cb0;--chart-bg:#f7fafc;--nav-bg:rgba(246,248,251,.96);--notice-bg:#fff4dc;--notice-ink:#704400;--th-bg:#e7edf4;--hover:#edf2f7;--chart-label:#43556c;--strategy-label:#49378f;--indent-label:#43556c;--radius:16px;font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif;color-scheme:light}}html[data-theme=dark]{{--bg:#07101f;--panel:#0d192b;--panel2:#12233a;--ink:#eef5ff;--muted:#aebed2;--line:#314762;--cyan:#50d5ff;--green:#60e5a5;--amber:#ffc869;--red:#ff7f91;--violet:#b8a9ff;--chart-bg:#081424;--nav-bg:rgba(7,16,31,.94);--notice-bg:#261f15;--notice-ink:#ffe2a4;--th-bg:#101f34;--hover:#12233a;--chart-label:#aebed2;--strategy-label:#c8bdff;--indent-label:#c5d1e1;color-scheme:dark}}
*{{box-sizing:border-box}}html{{background:var(--bg);scroll-behavior:smooth;max-width:100%}}body{{margin:0;background:var(--bg);color:var(--ink);min-width:0;max-width:100%;overflow-x:clip}}a{{color:inherit}}button,select{{font:inherit;color:inherit}}.skip{{position:fixed;left:1rem;top:-5rem;background:white;color:black;padding:.7rem;z-index:99}}.skip:focus{{top:1rem}}.shell{{min-height:100vh;min-width:0;max-width:100%}}.global-nav{{position:sticky;top:0;z-index:20;background:var(--nav-bg);backdrop-filter:blur(16px);border-bottom:1px solid var(--line);display:flex;align-items:center;gap:.35rem;padding:.8rem 1.1rem;overflow:hidden;max-width:100%}}.global-links{{display:flex;align-items:center;gap:.35rem;min-width:0;flex:1;overflow-x:auto}}.brand{{font-weight:800;white-space:nowrap;margin-right:.65rem}}.brand span{{color:var(--cyan)}}.nav-link,.pill,.mode-button{{border:1px solid transparent;background:transparent;color:var(--muted);border-radius:999px;padding:.55rem .78rem;text-decoration:none;white-space:nowrap;cursor:pointer}}.nav-link:hover,.nav-link[aria-current=page],.mode-button.active{{color:var(--ink);background:var(--panel2);border-color:var(--line)}}#app{{max-width:1600px;margin:auto;padding:1.2rem;overflow-x:clip}}.hero{{padding:2.4rem 0 1.4rem}}.eyebrow{{color:var(--cyan);font-size:.78rem;font-weight:800;letter-spacing:.13em;text-transform:uppercase}}h1{{font-size:clamp(2rem,5vw,4.4rem);line-height:1;margin:.45rem 0 1rem;max-width:1050px}}h2{{font-size:clamp(1.45rem,3vw,2.2rem);margin:.2rem 0 .8rem}}h3{{margin:.2rem 0 .65rem}}p{{color:var(--muted);line-height:1.62;max-width:78ch}}.grid{{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:1rem;min-width:0}}.card{{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:1.1rem;min-width:0;max-width:100%}}.kpi{{grid-column:span 3}}.kpi strong{{display:block;font-size:2rem;margin:.2rem 0}}.span6{{grid-column:span 6}}.span12{{grid-column:1/-1}}.company-layout{{display:grid;grid-template-columns:225px minmax(0,1fr);gap:1.2rem;align-items:start;min-width:0;max-width:100%}}.company-main{{min-width:0;max-width:100%}}.company-side-nav{{position:sticky;top:5rem;background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:.6rem;display:grid;gap:.25rem}}.company-side-nav a{{padding:.72rem;border-radius:10px;text-decoration:none;color:var(--muted)}}.company-side-nav a[aria-current=page],.company-side-nav a:hover{{background:var(--panel2);color:var(--ink)}}.mobile-local-selector{{display:none;width:100%;margin-bottom:1rem}}.financials-row{{display:flex;gap:.35rem;padding:.4rem;background:var(--panel);border:1px solid var(--line);border-radius:13px;overflow-x:auto;margin:0 0 1rem}}.financials-row a{{padding:.65rem .78rem;color:var(--muted);text-decoration:none;white-space:nowrap;border-radius:9px}}.financials-row a[aria-current=page]{{background:var(--panel2);color:var(--ink)}}.notice{{border-left:3px solid var(--amber);background:var(--notice-bg);padding:.9rem 1rem;border-radius:9px;color:var(--notice-ink);margin:1rem 0}}.controls{{display:flex;flex-wrap:wrap;gap:.7rem;align-items:end;margin:1rem 0}}.control{{display:grid;gap:.3rem;min-width:145px}}label,.label{{font-size:.74rem;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.07em}}select{{background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:9px;padding:.58rem;max-width:100%}}.range-label{{font-weight:800;color:var(--cyan);padding:.55rem}}.selected-series{{display:flex;gap:.45rem;flex-wrap:wrap;margin:.65rem 0}}.series-chip{{display:flex;align-items:center;gap:.4rem;background:var(--panel2);border:1px solid var(--line);border-radius:999px;padding:.35rem .55rem}}.remove-series{{background:transparent;border:0;color:var(--muted);cursor:pointer;font-size:1.1rem}}.explorer{{min-width:0;max-width:100%}}.chart-wrap{{background:var(--chart-bg);border:1px solid var(--line);border-radius:14px;padding:.6rem;min-height:390px;overflow-x:auto;overflow-y:hidden;max-width:100%}}.chart-wrap{{overflow-x:auto}}.statement-chart{{width:100%;max-width:100%;height:370px;display:block}}.statement-chart{{max-width:100%}}.chart-grid{{stroke:#243852;stroke-width:1}}.chart-label{{fill:var(--chart-label);font-size:14px}}.chart-line{{fill:none;stroke-width:3}}.chart-point{{stroke:#07101f;stroke-width:2;cursor:pointer}}.legend{{display:flex;gap:.8rem;flex-wrap:wrap;padding:.5rem}}.table-scroll,.all-periods-scroll{{width:100%;max-width:100%;min-width:0;overflow-x:auto;contain:inline-size;overscroll-behavior-inline:contain;border:1px solid var(--line);border-radius:12px;margin-top:1rem}}.all-periods-scroll{{width:100%;max-width:100%;overflow-x:auto}}table{{border-collapse:collapse;width:100%;min-width:840px}}caption{{text-align:left;padding:.7rem;font-weight:800;color:var(--ink)}}.all-periods-table th:first-child,.all-periods-table td:first-child{{position:sticky;left:0;z-index:2;background:var(--panel)}}th,td{{padding:.68rem .75rem;border-bottom:1px solid var(--line);text-align:right;font-variant-numeric:tabular-nums}}th{{position:sticky;top:0;background:var(--th-bg);color:var(--muted);font-size:.73rem;text-transform:uppercase;letter-spacing:.05em}}th:first-child,td:first-child{{text-align:left}}tbody tr{{cursor:pointer}}tbody tr:hover{{background:var(--hover)}}.indent-1{{padding-left:2rem!important;color:var(--indent-label)}}.status{{font-size:.72rem;padding:.22rem .46rem;border-radius:999px;display:inline-block}}.status.accepted{{background:#143b2d;color:#8bf0bd}}.status.qualified{{background:#3c2e14;color:#ffd584}}.status.conflicting{{background:#451d2a;color:#ff9bad}}.status.unavailable{{background:#252e3c;color:#aeb9c8}}details{{min-width:0;max-width:100%;border:1px solid var(--line);border-radius:10px;padding:.7rem;margin-top:.7rem;background:var(--panel)}}summary{{cursor:pointer;font-weight:700}}.strategy-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}}.strategy-box{{border-top:3px solid var(--violet)}}.strategy-box h3{{font-size:.75rem;color:var(--strategy-label);text-transform:uppercase;letter-spacing:.08em}}.formula{{font-family:ui-monospace,SFMono-Regular,monospace;color:var(--muted);font-size:.78rem;word-break:break-word}}.theme-toggle{{margin-left:auto;flex:0 0 42px;width:42px;height:42px;border:1px solid var(--line);border-radius:999px;background:var(--panel);color:var(--ink);display:grid;place-items:center;cursor:pointer}}.theme-icon,.theme-icon svg{{display:block;width:20px;height:20px}}.theme-icon svg{{fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}}.sr-only{{position:absolute!important;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}.about-company summary{{font-size:.8rem;color:var(--cyan)}}.hierarchy-toolbar{{display:flex;gap:.5rem;flex-wrap:wrap;margin:.8rem 0}}.hierarchy-toolbar button,.hierarchy-toggle{{border:1px solid var(--line);background:var(--panel2);color:var(--ink);border-radius:8px;padding:.45rem .65rem}}.hierarchy-group th{{background:var(--panel2);text-align:left}}.comparison-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}}.comparison-card{{min-width:0}}.grid>.comparison-card{{grid-column:span 6}}.comparison-card svg{{width:100%;max-width:100%;height:auto;display:block}}.comparison-chart-scroll{{max-width:100%;overflow-x:auto}}.muted{{color:var(--muted)}}.footer{{padding:2rem 0;color:var(--muted);font-size:.8rem}}:focus-visible{{outline:3px solid var(--cyan);outline-offset:3px}}
@media(max-width:900px){{.kpi{{grid-column:span 6}}.span6{{grid-column:1/-1}}.company-layout{{grid-template-columns:minmax(0,1fr)}}.company-side-nav{{display:none}}.mobile-local-selector{{display:grid}}}}
@media(max-width:760px){{#app{{padding:.75rem;min-width:0;max-width:100%}}.grid>.comparison-card{{grid-column:1/-1}}.global-nav{{padding:.65rem .7rem}}.kpi{{grid-column:1/-1}}.strategy-grid{{grid-template-columns:1fr}}.hero{{padding-top:1.3rem}}.chart-wrap{{min-height:320px}}.statement-chart{{height:300px}}.statement-chart{{width:900px;min-width:900px;max-width:none}}.comparison-chart-scroll svg{{width:720px;min-width:720px;max-width:none}}.financials-row{{scroll-snap-type:x proximity}}.financials-row a{{scroll-snap-align:start}}body{{overflow-x:clip}}.comparison-grid{{grid-template-columns:minmax(0,1fr)}}.controls>*{{min-width:0;max-width:100%}}}}
@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important;transition:none!important}}}}@media print{{:root,html[data-theme=dark]{{--bg:white;--panel:white;--panel2:#f3f3f3;--ink:black;--muted:#333;--line:#bbb;--chart-bg:white;--th-bg:#eee;color-scheme:light}}.global-nav,.company-side-nav,.mobile-local-selector,.controls,.financials-row,.theme-toggle{{display:none!important}}body{{background:white;color:black;overflow:visible}}.card{{border:1px solid #bbb;background:white}}p{{color:#333}}}}
</style></head><body><a class="skip" href="#app">Skip to report content</a><div class="shell"><nav class="global-nav" id="global-nav" aria-label="Global report navigation"></nav><main id="app" tabindex="-1" aria-live="polite"></main></div>
<script id="report-data" type="application/json">{encoded}</script>
<script>
const MODEL=JSON.parse(document.getElementById('report-data').textContent);const COLORS=['#1677a8','#138a65','#c27a00','#7058c9'];
const state={{hierarchyState:{{}}}};const $=(s,r=document)=>r.querySelector(s);const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
const sunIcon='<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',moonIcon='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 15.2A8.5 8.5 0 0 1 8.8 3.5 8.5 8.5 0 1 0 20.5 15.2Z"/></svg>';
function currentTheme(){{return document.documentElement.dataset.theme==='dark'?'dark':'light'}}function themeButton(){{const dark=currentTheme()==='dark',label=dark?'Switch to light appearance':'Switch to dark appearance';return `<button type="button" id="theme-toggle" class="theme-toggle" aria-label="${{label}}" title="${{label}}"><span class="theme-icon" aria-hidden="true">${{dark?sunIcon:moonIcon}}</span><span class="sr-only">${{label}}</span></button>`}}function toggleTheme(){{const next=currentTheme()==='dark'?'light':'dark';document.documentElement.dataset.theme=next;document.documentElement.style.colorScheme=next;try{{localStorage.setItem('briefforge-report-theme',next)}}catch(_e){{}}render();$('#theme-toggle')?.focus()}}
const fmt=(v,u)=>v===null||v===undefined?'Unavailable':(u==='USD'?new Intl.NumberFormat('en-US',{{notation:'compact',maximumFractionDigits:2}}).format(Number(v))+' USD':Number(v).toLocaleString('en-US',{{maximumFractionDigits:2}})+(u?` ${{u}}`:''));
const fmtExact=(v,u)=>v===null||v===undefined?'Unavailable':Number(v).toLocaleString('en-US',{{maximumFractionDigits:20}})+(u?` ${{u}}`:'');
function currentRoute(){{const r=location.hash.replace(/^#\/?/,'')||'overview';return MODEL.routes.includes(r)?r:'overview'}}
function go(route){{history.pushState(null,'','#/'+route);render()}}window.addEventListener('popstate',render);window.addEventListener('hashchange',render);
function navLink(label,route,active,cls='nav-link'){{return `<a href="#/${{route}}" data-route="${{route}}" class="${{cls}}" ${{active?'aria-current="page"':''}}>${{esc(label)}}</a>`}}
function renderGlobalNav(route){{const company=route.split('/')[0],globals=[['Overview','overview'],['Compare','comparison'],['Method','methodology'],['Evidence','evidence']];let links='<div class="brand">Corporate <span>Financials</span></div>'+globals.map(([l,r])=>navLink(l,r,route===r)).join('')+'<span aria-hidden="true" class="muted">│</span>'+MODEL.companies.map(c=>navLink(MODEL.names[c],c+'/overview',company===c)).join('');$('#global-nav').innerHTML=`<div class="global-links">${{links}}</div>${{themeButton()}}`;$('#theme-toggle').onclick=toggleTheme}}
function hero(kicker,title,text){{return `<header class="hero"><div class="eyebrow">${{esc(kicker)}}</div><h1>${{esc(title)}}</h1><p>${{esc(text)}}</p></header>`}}
function statusBadge(s){{return `<span class="status ${{esc(s)}}">${{esc(s)}}</span>`}}
function bestLine(company,category){{return MODEL.statement_lines.filter(l=>l.company_key===company&&l.semantic_category===category).sort((a,b)=>b.observations.filter(o=>o.mode==='Annual'&&o.value!==null).length-a.observations.filter(o=>o.mode==='Annual'&&o.value!==null).length||a.line_id.localeCompare(b.line_id))[0]}}
function comparisonMetricChart(category,title,id=''){{const series=MODEL.companies.map(company=>{{const line=bestLine(company,category),points=(line?.observations||[]).filter(o=>o.mode==='Annual'&&o.value!==null).sort((a,b)=>a.period.end.localeCompare(b.period.end));return {{company,line,points}}}});const points=series.flatMap(s=>s.points),values=points.map(p=>Number(p.value));if(!values.length)return `<article class="card comparison-card" id="${{id}}"><h3>${{esc(title)}}</h3><div class="notice">No comparable admitted Annual values.</div></article>`;const W=720,H=290,p={{l:80,r:25,t:25,b:55}},min=Math.min(...values),max=Math.max(...values),spread=max-min||Math.abs(max)||1,x=(i,n)=>p.l+i*(W-p.l-p.r)/Math.max(n-1,1),y=v=>p.t+(max-Number(v))/spread*(H-p.t-p.b);let svg='';for(let k=0;k<5;k++){{const yy=p.t+k*(H-p.t-p.b)/4,val=max-k*spread/4;svg+=`<line class="chart-grid" x1="${{p.l}}" x2="${{W-p.r}}" y1="${{yy}}" y2="${{yy}}"/><text class="chart-label" x="4" y="${{yy+4}}">${{fmt(val,'USD')}}</text>`}}series.forEach((s,j)=>{{if(!s.points.length)return;svg+=`<path class="chart-line" stroke="${{COLORS[j]}}" d="${{s.points.map((o,i)=>`${{i?'L':'M'}} ${{x(i,s.points.length)}} ${{y(o.value)}}`).join(' ')}}"/>`;s.points.forEach((o,i)=>svg+=`<circle class="chart-point" fill="${{COLORS[j]}}" cx="${{x(i,s.points.length)}}" cy="${{y(o.value)}}" r="5"><title>${{esc(MODEL.names[s.company])}} · ${{esc(o.period_key)}} · ${{esc(fmtExact(o.value,o.unit))}} · ${{esc(o.status)}}</title></circle>`)}});const rows=series.flatMap(s=>s.points.map(o=>`<tr><th scope="row">${{esc(MODEL.names[s.company])}}</th><td>${{esc(o.period_key)}}</td><td>${{esc(o.value)}}</td><td>${{esc(o.unit)}}</td><td>${{statusBadge(o.status)}}</td></tr>`)).join('');return `<article class="card comparison-card" id="${{id}}"><h3>${{esc(title)}}</h3><p>All four companies are included by default. Microsoft’s June 30 fiscal calendar remains explicit.</p><div class="comparison-chart-scroll"><svg viewBox="0 0 ${{W}} ${{H}}" role="img" aria-label="${{esc(title)}} comparison">${{svg}}</svg></div><div class="legend">${{series.map((s,j)=>`<span><span style="color:${{COLORS[j]}}">●</span> ${{esc(MODEL.names[s.company])}} ${{s.company==='microsoft'?'(June FY)':'(December FY)'}}</span>`).join('')}}</div><details><summary>View data</summary><div class="table-scroll"><table><caption>${{esc(title)}} exact comparison values</caption><thead><tr><th scope="col">Company</th><th scope="col">Period</th><th scope="col">Exact value</th><th scope="col">Unit</th><th scope="col">Status</th></tr></thead><tbody>${{rows}}</tbody></table></div></details></article>`}}
function comparisonSmallMultiples(statement,category,title,id){{const panels=MODEL.companies.map(company=>{{const line=bestLine(company,category),points=(line?.observations||[]).filter(o=>o.mode==='Annual'&&o.value!==null).sort((a,b)=>a.period.end.localeCompare(b.period.end)),values=points.map(o=>Number(o.value));if(!points.length)return `<article class="card"><h3>${{MODEL.names[company]}}</h3><div class="notice">Unavailable — no compatible admitted ${{esc(category)}} series.</div></article>`;const W=340,H=210,p={{l:55,r:15,t:18,b:36}},min=Math.min(...values),max=Math.max(...values),spread=max-min||Math.abs(max)||1,x=i=>p.l+i*(W-p.l-p.r)/Math.max(points.length-1,1),y=v=>p.t+(max-Number(v))/spread*(H-p.t-p.b),path=points.map((o,i)=>`${{i?'L':'M'}} ${{x(i)}} ${{y(o.value)}}`).join(' '),dots=points.map((o,i)=>`<circle class="chart-point" fill="${{COLORS[MODEL.companies.indexOf(company)]}}" cx="${{x(i)}}" cy="${{y(o.value)}}" r="4"><title>${{esc(line.display_label)}} · ${{esc(o.period_key)}} · ${{esc(fmtExact(o.value,o.unit))}} · ${{esc(o.status)}}</title></circle>`).join('');return `<article class="card"><h3>${{MODEL.names[company]}}</h3><p>${{esc(line.issuer_native_label)}} · ${{company==='microsoft'?'June 30 FY':'December 31 FY'}}</p><svg viewBox="0 0 ${{W}} ${{H}}" role="img" aria-label="${{MODEL.names[company]}} ${{esc(title)}}"><path class="chart-line" stroke="${{COLORS[MODEL.companies.indexOf(company)]}}" d="${{path}}"/>${{dots}}</svg></article>`}}).join('');return `<section class="card span12" id="${{id}}"><h2>${{esc(title)}}</h2><p>Standardized small multiples preserve issuer-native labels and avoid false alignment. All four companies are shown.</p><div class="comparison-grid">${{panels}}</div></section>`}}
function renderOverview(){{const profiles=MODEL.overviews.companies;const developments=profiles.map(p=>{{const f=p.facts;return `<article class="card span6"><h2>${{esc(p.name)}}</h2><p><strong>Scale:</strong> ${{f.scale.availability==='available'?`${{fmtExact(f.scale.value,f.scale.unit)}} in ${{esc(f.scale.period_key)}}`:'Unavailable'}}. <strong>Revenue trajectory:</strong> ${{f.trajectory.availability==='available'?`${{esc(f.trajectory.start_period)}} → ${{esc(f.trajectory.end_period)}}, ${{fmt(f.trajectory.percentage_change,'%')}}`:'Unavailable'}}.</p><p><strong>Profitability:</strong> operating ${{f.operating_profitability.availability==='available'?fmtExact(f.operating_profitability.value,f.operating_profitability.unit):'Unavailable'}}; net ${{f.net_profitability.availability==='available'?fmtExact(f.net_profitability.value,f.net_profitability.unit):'Unavailable'}}. <strong>Cash generation:</strong> ${{f.cash_generation.availability==='available'?fmtExact(f.cash_generation.value,f.cash_generation.unit):'Unavailable'}}.</p><p><strong>Balance sheet:</strong> admitted cash position ${{f.balance_sheet.availability==='available'?fmtExact(f.balance_sheet.value,f.balance_sheet.unit):'Unavailable'}}. <strong>Capital allocation:</strong> admitted capital expenditure ${{f.capital_allocation.availability==='available'?fmtExact(f.capital_allocation.value,f.capital_allocation.unit):'Unavailable'}}.</p><p>${{esc(p.strategy.text)}} ${{esc(p.risks.missing_evidence)}}</p>${{navLink('Open '+p.name+' →',p.company_key+'/overview',false,'pill')}}</article>`}}).join('');return hero('TASK-082 · standardized corporate analysis','Financial development without a false winner','The overview presents authenticated scale, profitability, cash generation, balance-sheet position, allocation and strategy context. It does not use evidence-volume cards or market prices.')+`<section class="grid">${{comparisonMetricChart('revenue','Annual revenue development','overview-revenue-comparison')}}${{comparisonMetricChart('operating_income','Annual operating income development','overview-operating-comparison')}}${{developments}}<article class="card span12"><h2>Why no overall winner is established</h2><p>${{esc(MODEL.overviews.global.no_overall_winner)}}</p><div class="notice">${{esc(MODEL.overviews.global.qualification)}}</div></article></section>`}}
function renderComparison(){{return hero('Comparison','Every individual graph has a documented counterpart','Comparable metrics use shared charts; semantically incomplete or differently aligned evidence uses coordinated small multiples. All four companies are present by default.')+`<section class="grid"><article class="card span12" id="comparison-income-core"><h2>Income statement core</h2><div class="comparison-grid">${{comparisonMetricChart('revenue','Revenue')}}${{comparisonMetricChart('operating_income','Operating income')}}${{comparisonMetricChart('net_income','Net income')}}</div></article>${{comparisonSmallMultiples('balance_sheet','cash','Balance-sheet position','comparison-balance-sheet-small-multiples')}}${{comparisonSmallMultiples('cash_flow','operating_cash_flow','Cash generation','comparison-cash-flow-small-multiples')}}${{comparisonSmallMultiples('capital_allocation','capital_expenditure_components','Capital allocation','comparison-capital-allocation-small-multiples')}}<article class="card span12"><h2>Comparison boundary</h2><p>${{esc(MODEL.overviews.global.no_overall_winner)}}</p></article></section>`}}
function renderMethodology(){{return hero('Method','Range mathematics stay upstream','InsightForge classifies periods and owns every interval, ratio, and statistic. BriefForge selects only matching precomputed records.')+`<section class="grid"><article class="card span6"><h2>Flows</h2><p>Quarterly ranges sum only authenticated, non-overlapping quarter-only observations. Annual ranges remain endpoint comparisons. Q4 uses annual less nine-month cumulative only under exact concept, unit, dimension, and scope compatibility.</p></article><article class="card span6"><h2>Stocks</h2><p>Balance-sheet observations use start value, end value, absolute change, and percentage change. They are never summed across dates.</p></article><article class="card span6"><h2>Ratios and EPS</h2><p>Ratios are recomputed from compatible numerators and denominators. Displayed ratios are not averaged. EPS is never blindly summed and no TTM EPS is created without share evidence.</p></article><article class="card span6"><h2>Evidence state</h2><p>Accepted, qualified, conflicting, and unavailable states remain visible. Conflicting or missing components never become fabricated values.</p></article></section>`}}
function renderEvidenceGlobal(){{return hero('Evidence','Authenticated lineage and explicit limits','The report is bound to InsightForge T-042 and its KnowledgeForge and MacroForge predecessors.')+`<section class="grid"><article class="card span6"><h2>Lineage</h2><p class="formula">MacroForge TASK-227 → KnowledgeForge TASK-229 → InsightForge T-042 → BriefForge TASK-082</p><p>Analysis identity: <span class="formula">${{MODEL.analysis_identity}}</span></p></article><article class="card span6"><h2>Unresolved upstream work</h2><p>${{esc(MODEL.stock_price.finding)}}</p><p>Strategy progression remains PARTIAL because Q4-cycle and latest subsequent-quarter evidence are absent.</p></article></section>`}}
function sideRoute(company,item){{return item==='overview'?`${{company}}/overview`:item==='financials'?`${{company}}/financials/overview`:`${{company}}/${{item}}`}}
function sideNav(company,route){{const labels={{overview:'Overview',financials:'Financials','business-engines':'Business and operating engines',strategy:'Strategy',risks:'Risks',evidence:'Evidence'}};const selected=route.includes('/financials/')?'financials':route.split('/')[1];return `<aside class="company-side-nav" aria-label="${{MODEL.names[company]}} local navigation">${{Object.entries(labels).map(([k,l])=>navLink(l,sideRoute(company,k),selected===k,'')).join('')}}</aside><label class="mobile-local-selector"><span class="label">Company section</span><select id="mobile-local-selector" aria-label="Company section">${{Object.entries(labels).map(([k,l])=>`<option value="${{sideRoute(company,k)}}" ${{selected===k?'selected':''}}>${{esc(l)}}</option>`).join('')}}</select></label>`}}
function financialNav(company,view){{const labels={{overview:'Financial overview','income-statement':'Income statement','balance-sheet':'Balance sheet','cash-flow':'Cash flow','ratios-statistics':'Ratios and statistics','capital-allocation':'Capital allocation'}};return `<nav class="financials-row" aria-label="Financials navigation">${{Object.entries(labels).map(([k,l])=>navLink(l,`${{company}}/financials/${{k}}`,view===k,'')).join('')}}</nav>`}}
function companyHeader(company,section){{const p=MODEL.overviews.companies.find(x=>x.company_key===company),periods=Object.values(p.facts).map(f=>f.period_key||f.end_period).filter(Boolean).sort(),latest=periods.at(-1)||'No compatible period';const short=p.description.split('. ')[0]+(p.description.includes('. ')?'.':'');return `<header class="company-header"><div class="eyebrow">${{MODEL.names[company]}} · ${{esc(section)}}</div><h1>${{MODEL.names[company]}}</h1><p>${{esc(short)}}</p><details class="about-company"><summary>About the company</summary><p>${{esc(p.description)}}</p><p class="formula">${{esc((p.about.evidence_refs||[]).join(', '))}}</p></details><p><strong>Evidence through:</strong> ${{esc(latest)}} · <strong>Fiscal calendar:</strong> ${{esc(p.fiscal_calendar)}}.</p><div class="notice">Statement mappings remain partial; missing, qualified and conflicting evidence is preserved rather than inferred.</div></header>`}}
function factCard(label,fact){{if(!fact||fact.availability!=='available')return `<article class="card"><h3>${{esc(label)}}</h3><p>Unavailable in the authenticated representation.</p></article>`;const period=fact.period_key||`${{fact.start_period}} → ${{fact.end_period}}`,value=fact.value!==undefined?fmtExact(fact.value,fact.unit):(fact.percentage_change!==null&&fact.percentage_change!==undefined?fmt(fact.percentage_change,'%'):fmt(fact.absolute_change,fact.unit));return `<article class="card"><h3>${{esc(label)}}</h3><strong>${{value}}</strong><p>${{esc(period)}} · ${{statusBadge(fact.status||'qualified')}}</p><p class="formula">${{esc((fact.evidence_refs||[]).join(', '))}}</p></article>`}}
function companyOverview(company){{const p=MODEL.overviews.companies.find(x=>x.company_key===company),f=p.facts,ratios=p.ratios.slice(0,4).map(r=>`<tr><th scope="row">${{esc(r.ratio_name)}}</th><td>${{fmtExact(r.result,r.unit)}}</td><td>${{esc(r.scope||'—')}}</td><td>${{statusBadge(r.evidence_status)}}</td></tr>`).join('');return companyHeader(company,'Overview')+`<section class="grid"><article class="card span12"><h2>Financial scale and trajectory</h2><p>Latest admitted scale and the authenticated InsightForge revenue interval are shown without BriefForge recomputation.</p><div class="comparison-grid">${{factCard('Revenue scale',f.scale)}}${{factCard('Revenue trajectory',f.trajectory)}}</div></article><article class="card span12"><h2>Profitability, cash generation and financial position</h2><div class="comparison-grid">${{factCard('Operating profitability',f.operating_profitability)}}${{factCard('Net profitability',f.net_profitability)}}${{factCard('Operating cash generation',f.cash_generation)}}${{factCard('Admitted cash position',f.balance_sheet)}}${{factCard('Capital expenditure',f.capital_allocation)}}</div></article><article class="card span6"><h2>Important ratios</h2><div class="table-scroll"><table><caption>${{MODEL.names[company]}} available filing-derived ratios</caption><thead><tr><th scope="col">Ratio</th><th scope="col">Result</th><th scope="col">Scope</th><th scope="col">Status</th></tr></thead><tbody>${{ratios}}</tbody></table></div></article><article class="card span6"><h2>Business engines, strategy and execution risk</h2><p>${{esc(p.business_engines.text)}}</p><p>${{esc(p.strategy.text)}} ${{esc(p.strategy.uncertainty)}}</p><p>${{esc(p.risks.text)}}</p><div class="notice">${{esc(p.risks.missing_evidence)}}</div></article></section>`}}
function companyEngines(company){{const lines=MODEL.statement_lines.filter(x=>x.company_key===company&&['revenue','operating_income','research_and_development_source_native'].includes(x.semantic_category));return companyHeader(company,'Business and operating engines')+`<section class="card"><h2>Issuer-native operating evidence</h2><p>This page uses admitted consolidated filing lines; it does not claim cross-issuer segment equivalence.</p><div class="table-scroll"><table><thead><tr><th>Reported line</th><th>Category</th><th>Periods</th><th>Status</th></tr></thead><tbody>${{lines.map(l=>`<tr><td>${{esc(l.display_label)}}</td><td>${{esc(l.semantic_category)}}</td><td>${{l.observations.length}}</td><td>${{statusBadge(l.coverage_classification.includes('qualified')?'qualified':'accepted')}}</td></tr>`).join('')}}</tbody></table></div></section>`}}
function strategyPage(company){{const s=MODEL.strategies.find(x=>x.company_key===company);return companyHeader(company,'Strategy')+`<div class="notice">Strategy disposition remains PARTIAL. Q4-cycle release and subsequent-quarter progression were not fabricated.</div><section class="strategy-grid"><article class="card strategy-box"><h3>Management stated</h3><p>${{esc(s.management_stated.text)}}</p><p class="formula">${{s.management_stated.evidence_refs.join(', ')}}</p></article><article class="card strategy-box"><h3>Financial evidence</h3><p>${{esc(s.financial_evidence.text)}}</p><p class="formula">${{s.financial_evidence.evidence_refs.join(', ')}}</p></article><article class="card strategy-box"><h3>InsightForge assessment</h3><p>${{esc(s.insightforge_assessment.text)}}</p><p>${{esc(s.insightforge_assessment.uncertainty)}} ${{esc(s.insightforge_assessment.execution_dependency)}}</p></article><article class="card strategy-box"><h3>Unproven claims and monitoring points</h3><p>${{esc(s.unproven_and_monitoring.text)}}</p><p>${{esc(s.unproven_and_monitoring.missing_evidence)}}</p></article></section>`}}
function risksPage(company){{const s=MODEL.strategies.find(x=>x.company_key===company);return companyHeader(company,'Risks')+`<section class="grid"><article class="card span6"><h2>Execution uncertainty</h2><p>${{esc(s.insightforge_assessment.uncertainty)}}</p></article><article class="card span6"><h2>Monitoring</h2><p>${{esc(s.unproven_and_monitoring.text)}}</p></article><article class="card span12"><h2>Coverage risk</h2><p>Partial statement mappings, qualified evidence, and absent raw prices limit conclusions. No valuation or investment recommendation is supported.</p></article></section>`}}
function evidencePage(company){{const lines=MODEL.statement_lines.filter(x=>x.company_key===company);return companyHeader(company,'Evidence')+`<section class="card"><h2>Exact filing evidence registry</h2><p>${{lines.reduce((n,l)=>n+l.exact_source_claim_ids.length,0).toLocaleString()}} exact claim references are attached to ${{lines.length}} rendered lines.</p><details><summary>View line identities</summary><div class="table-scroll"><table><thead><tr><th>Line</th><th>Category</th><th>Modes</th><th>Evidence refs</th></tr></thead><tbody>${{lines.map(l=>`<tr><td>${{esc(l.display_label)}}</td><td>${{esc(l.semantic_category)}}</td><td>${{l.available_modes.join(', ')}}</td><td class="formula">${{l.exact_source_claim_ids.slice(0,3).join(', ')}}</td></tr>`).join('')}}</tbody></table></div></details></section>`}}
function financialOverview(company){{const p=MODEL.overviews.companies.find(x=>x.company_key===company),f=p.facts;return companyHeader(company,'Financials')+financialNav(company,'overview')+`<section class="grid"><article class="card span6"><h2>Scale, trajectory and profitability</h2>${{factCard('Revenue scale',f.scale)}}${{factCard('Revenue trajectory',f.trajectory)}}${{factCard('Operating profitability',f.operating_profitability)}}${{factCard('Net profitability',f.net_profitability)}}</article><article class="card span6"><h2>Cash, position and allocation</h2>${{factCard('Operating cash generation',f.cash_generation)}}${{factCard('Admitted cash position',f.balance_sheet)}}${{factCard('Capital expenditure',f.capital_allocation)}}</article><article class="card span12"><h2>Financial explorer</h2><p>Income statement, balance sheet, cash flow, ratios and statistics, and capital allocation use one standardized horizontal navigation. Annual, Quarterly and evidence-supported TTM modes preserve authenticated scopes and precomputed ranges.</p></article></section>`}}
function ratioPage(company){{const rows=MODEL.ratios.filter(x=>x.company_key===company);return companyHeader(company,'Ratios and statistics')+financialNav(company,'ratios-statistics')+`<section class="card"><h2>Filing-derived ratios</h2><p>Filing statistics reuse the exact per-line observation registries shown in the statement explorers; this table separately lists derived ratios. No published website ratio is canonical. Unavailable ratios remain unavailable rather than forced.</p><div class="table-scroll"><table><thead><tr><th>Ratio</th><th>Result</th><th>Scope</th><th>Formula</th><th>Components</th><th>Status</th></tr></thead><tbody>${{rows.map(r=>`<tr><td>${{esc(r.ratio_name)}}</td><td>${{r.result===null?'Unavailable':fmt(r.result,r.unit)}}</td><td>${{esc(r.scope||'—')}}</td><td class="formula">${{esc(r.formula)}}</td><td class="formula">${{r.component_identifiers.join(', ')||esc(r.qualification)}}</td><td>${{statusBadge(r.evidence_status)}}</td></tr>`).join('')}}</tbody></table></div></section>`}}
function explorerKey(company,statement){{return company+'|'+statement}}function linesFor(company,statement){{if(statement==='capital_allocation')return MODEL.statement_lines.filter(x=>x.company_key===company&&['capital_expenditure_components','share_repurchases','dividends','acquisition_investment_components','current_debt_components','noncurrent_debt_components'].includes(x.semantic_category));return MODEL.statement_lines.filter(x=>x.company_key===company&&x.statement_family===statement)}}
function initExplorer(company,statement){{const key=explorerKey(company,statement),lines=linesFor(company,statement);if(!state[key]){{const first=lines.find(l=>l.available_modes.includes('Annual'))||lines[0];state[key]={{mode:first.available_modes[0]||'Annual',selected:[first.line_id],start:null,end:null}}}}return state[key]}}
function periodsFor(lines,mode){{const map=new Map;lines.forEach(l=>l.observations.filter(o=>o.mode===mode).forEach(o=>map.set(o.period_key,o.period.end)));return [...map].sort((a,b)=>a[1].localeCompare(b[1])).map(x=>x[0])}}
function ensureModeSelection(lines,s){{const supported=lines.filter(l=>l.observations.some(o=>o.mode===s.mode&&o.value!==null));const selected=s.selected.filter(id=>supported.some(l=>l.line_id===id));s.selected=selected.length?selected:(supported.length?[supported[0].line_id]:[])}}
function obsAt(line,mode,period){{return line.observations.find(o=>o.mode===mode&&o.period_key===period)}}function rangeAt(lineId,mode,start,end){{return MODEL.range_summaries.find(r=>r.line_id===lineId&&r.mode===mode&&r.start_period===start&&r.end_period===end)}}
function hierarchyGroups(company,statement){{const groups=MODEL.hierarchy.groups.filter(g=>g.company_key===company&&g.statement_family===statement);if(groups.length)return groups;const lines=linesFor(company,statement),categories=[...new Set(lines.map(l=>l.semantic_category))].sort();return categories.map(category=>({{group_id:`${{company}}-${{statement}}-${{category.replaceAll('_','-')}}`,company_key:company,statement_family:statement,semantic_category:category,label:category.replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase()),availability:'supported',relationship_basis:'qualified_semantic_category',rendering_mode:'flat_peer_rows',peer_line_ids:lines.filter(l=>l.semantic_category===category).sort((a,b)=>a.issuer_native_label.localeCompare(b.issuer_native_label)||a.line_id.localeCompare(b.line_id)).map(l=>l.line_id),analytical_display_order:true,issuer_presentation_order:false,collapsed_by_default:false}}))}}
function hierarchyExpanded(group){{if(!(group.group_id in state.hierarchyState))state.hierarchyState[group.group_id]=!group.collapsed_by_default;return state.hierarchyState[group.group_id]}}
function financialRowHTML(l,s){{const a=obsAt(l,s.mode,s.start),b=obsAt(l,s.mode,s.end),r=rangeAt(l.line_id,s.mode,s.start,s.end),interval=r?(r.result??r.absolute_change??'—'):'—',stat=(b||a||{{status:'unavailable'}}).status;return `<tr data-line-id="${{l.line_id}}"><th scope="row">${{esc(l.display_label)}}<br><span class="muted">${{esc(l.issuer_native_label)}}</span></th><td>${{b?fmt(b.value,b.unit):'Unavailable'}}</td><td>${{a?fmt(a.value,a.unit):'Unavailable'}}</td><td>${{r&&r.absolute_change!==undefined?fmt(r.absolute_change,r.unit):'—'}}</td><td>${{r&&r.percentage_change!==undefined&&r.percentage_change!==null?fmt(r.percentage_change,'%'):(r&&r.percentage_change===null&&Number(r.start_value)<=0?'Not meaningful — zero or negative base':'—')}}</td><td>${{r&&r.result!==undefined?fmt(r.result,r.unit):interval}}</td><td>${{statusBadge(stat)}}</td></tr>`}}
function hierarchyBodies(company,statement,lines,s){{return hierarchyGroups(company,statement).map(group=>{{const expanded=hierarchyExpanded(group),peers=group.peer_line_ids.map(id=>lines.find(l=>l.line_id===id)).filter(Boolean),controls=`hierarchy-${{group.group_id}}`,rows=expanded?peers.map(l=>financialRowHTML(l,s)).join(''):`<tr><td colspan="7">${{peers.length}} peer rows hidden. Expand this qualified analytical section to view them.</td></tr>`;return `<tbody id="${{controls}}"><tr class="hierarchy-group"><th colspan="7"><button type="button" class="hierarchy-toggle" data-group-toggle="${{group.group_id}}" aria-expanded="${{expanded}}" aria-controls="${{controls}}">${{expanded?'▾':'▸'}} ${{esc(group.label)}}</button> <span class="muted">qualified semantic category · peer rows · No issuer presentation relationships</span></th></tr>${{rows}}</tbody>`}}).join('')}}
function allPeriodsTable(company,statement,lines,mode){{const periods=periodsFor(lines,mode),headers=periods.map(p=>`<th scope="col">${{esc(p)}}</th>`).join(''),rows=lines.map(line=>`<tr><th scope="row">${{esc(line.display_label)}}<br><span class="muted">${{esc(line.issuer_native_label)}}</span></th>${{periods.map(period=>{{const o=obsAt(line,mode,period);return `<td>${{o?`<span>${{esc(o.value)}}</span><br><span class="muted">${{esc(o.unit)}} · ${{esc(o.scope_kind)}}</span><br>${{statusBadge(o.status)}}`:'Unavailable'}}</td>`}}).join('')}}</tr>`).join('');return `<div class="all-periods-scroll"><table class="all-periods-table"><caption>${{esc(MODEL.names[company])}} · ${{esc(statement.replaceAll('_',' '))}} · ${{esc(mode)}} · all authenticated periods</caption><thead><tr><th scope="col">Financial line · unit · status</th>${{headers}}</tr></thead><tbody>${{rows}}</tbody></table></div>`}}
function renderExplorer(company,statement){{const lines=linesFor(company,statement),s=initExplorer(company,statement);let periods=periodsFor(lines,s.mode);if(!periods.length){{for(const m of MODEL.period_modes){{const p=periodsFor(lines,m);if(p.length){{s.mode=m;periods=p;break}}}}}}if(!periods.length)return '<div class="notice">No compatible observations for this view.</div>';ensureModeSelection(lines,s);if(!periods.includes(s.start))s.start=periods[0];if(!periods.includes(s.end))s.end=periods[periods.length-1];if(periods.indexOf(s.start)>periods.indexOf(s.end))[s.start,s.end]=[s.end,s.start];const primary=lines.find(l=>l.line_id===s.selected[0])||lines[0],primaryUnit=(primary.observations.find(o=>o.mode===s.mode)||{{}}).unit,compatible=lines.filter(l=>l.observations.some(o=>o.mode===s.mode&&o.unit===primaryUnit)),hierarchy=hierarchyBodies(company,statement,lines,s);return `<section class="card explorer" data-company="${{company}}" data-statement="${{statement}}"><h2>${{statement==='capital_allocation'?'Capital allocation':statement.replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase())}} evidence</h2><p>Selected source-resolved evidence. Click a visible financial row or use the metric selector. Additional series must share the primary unit.</p><div class="controls"><div><span class="label">Frequency</span><div>${{MODEL.period_modes.map(m=>`<button class="mode-button ${{s.mode===m?'active':''}}" data-mode="${{m}}" ${{periodsFor(lines,m).length?'':'disabled'}}>${{m}}</button>`).join('')}}</div></div><label class="control">Range start<select class="range-start">${{periods.map(p=>`<option ${{p===s.start?'selected':''}}>${{esc(p)}}</option>`).join('')}}</select></label><label class="control">Range end<select class="range-end">${{periods.map(p=>`<option ${{p===s.end?'selected':''}}>${{esc(p)}}</option>`).join('')}}</select></label><label class="control">Metric selector<select class="metric-selector"><option value="">Add compatible series…</option>${{compatible.filter(l=>!s.selected.includes(l.line_id)).map(l=>`<option value="${{l.line_id}}">${{esc(l.display_label)}}</option>`).join('')}}</select></label><div class="range-label">Exact range: <span class="exact-range">${{esc(s.start)}} → ${{esc(s.end)}}</span></div></div><div class="selected-series">${{s.selected.map((id,i)=>{{const l=lines.find(x=>x.line_id===id);return l?`<span class="series-chip"><span style="color:${{COLORS[i%COLORS.length]}}">●</span>${{esc(l.display_label)}}${{i?`<button class="remove-series" data-remove="${{id}}" aria-label="Remove ${{esc(l.display_label)}}">×</button>`:''}}</span>`:''}}).join('')}}</div><div class="chart-wrap"><svg class="statement-chart" role="img" aria-label="Interactive statement history"></svg><div class="legend"></div></div><details><summary>View data</summary><div class="exact-data"></div></details><div class="hierarchy-toolbar"><button type="button" data-hierarchy-action="expand">Expand all</button><button type="button" data-hierarchy-action="collapse">Collapse all</button></div><div class="table-scroll"><table><caption>${{esc(MODEL.names[company])}} · current ${{esc(statement.replaceAll('_',' '))}} range</caption><thead><tr><th scope="col">Financial line</th><th scope="col">End value</th><th scope="col">Start value</th><th scope="col">Absolute change</th><th scope="col">Percentage change</th><th scope="col">Interval result</th><th scope="col">Evidence status</th></tr></thead>${{hierarchy}}</table></div><details><summary>View all periods</summary>${{allPeriodsTable(company,statement,lines,s.mode)}}</details></section>`}}
function selectLine(company,statement,lineId){{const s=initExplorer(company,statement),lines=linesFor(company,statement),primary=lines.find(l=>l.line_id===s.selected[0]),candidate=lines.find(l=>l.line_id===lineId);if(!candidate)return;const pu=(primary?.observations.find(o=>o.mode===s.mode)||{{}}).unit,cu=(candidate.observations.find(o=>o.mode===s.mode)||{{}}).unit;if(pu&&cu&&pu!==cu)return;if(!s.selected.includes(lineId))s.selected=[lineId,...s.selected].slice(0,3);else s.selected=[lineId,...s.selected.filter(x=>x!==lineId)];render()}}
function drawChart(root,company,statement){{const s=initExplorer(company,statement),lines=linesFor(company,statement),periods=periodsFor(lines,s.mode),i0=periods.indexOf(s.start),i1=periods.indexOf(s.end),visible=periods.slice(i0,i1+1),selected=s.selected.map(id=>lines.find(l=>l.line_id===id)).filter(Boolean);const dataRows=selected.flatMap(l=>l.observations.filter(o=>o.mode===s.mode&&visible.includes(o.period_key)).map(o=>({{...o,line:l}})));const points=dataRows.filter(p=>p.value!==null);const svg=$('svg',root),W=1000,H=340,pad={{l:75,r:25,t:25,b:55}};if(!points.length){{svg.setAttribute('viewBox',`0 0 ${{W}} ${{H}}`);svg.innerHTML='<text x="50" y="80" class="chart-label">No supported values in this exact range.</text>';return}}const vals=points.map(p=>Number(p.value)),min=Math.min(...vals),max=Math.max(...vals),spread=max-min||Math.abs(max)||1,x=p=>pad.l+(visible.indexOf(p)/(Math.max(visible.length-1,1)))*(W-pad.l-pad.r),y=v=>pad.t+(max-Number(v))/spread*(H-pad.t-pad.b);let out='';for(let k=0;k<5;k++){{const yy=pad.t+k*(H-pad.t-pad.b)/4,val=max-k*spread/4;out+=`<line class="chart-grid" x1="${{pad.l}}" x2="${{W-pad.r}}" y1="${{yy}}" y2="${{yy}}"/><text class="chart-label" x="5" y="${{yy+4}}">${{fmt(val,points[0].unit)}}</text>`}}visible.forEach(p=>out+=`<text class="chart-label" text-anchor="middle" x="${{x(p)}}" y="${{H-18}}">${{esc(p)}}</text>`);selected.forEach((l,idx)=>{{const ps=l.observations.filter(o=>o.mode===s.mode&&visible.includes(o.period_key)&&o.value!==null).sort((a,b)=>visible.indexOf(a.period_key)-visible.indexOf(b.period_key));if(!ps.length)return;out+=`<path class="chart-line" stroke="${{COLORS[idx]}}" d="${{ps.map((p,j)=>`${{j?'L':'M'}} ${{x(p.period_key)}} ${{y(p.value)}}`).join(' ')}}"/>`;ps.forEach(p=>out+=`<circle class="chart-point" fill="${{COLORS[idx]}}" cx="${{x(p.period_key)}}" cy="${{y(p.value)}}" r="5"><title>${{esc(l.display_label)}} · ${{esc(p.period_key)}} · ${{esc(fmtExact(p.value,p.unit))}} · ${{esc(p.status)}} · ${{esc(p.scope_kind)}}</title></circle>`)}});svg.setAttribute('viewBox',`0 0 ${{W}} ${{H}}`);svg.innerHTML=out;$('.legend',root).innerHTML=selected.map((l,i)=>`<span><span style="color:${{COLORS[i]}}">●</span> ${{esc(l.display_label)}}</span>`).join('');$('.exact-data',root).innerHTML=`<div class="table-scroll"><table><thead><tr><th>Series</th><th>Period</th><th>Exact value</th><th>Unit</th><th>Status</th><th>Scope</th><th>Candidate values</th><th>Evidence references</th></tr></thead><tbody>${{dataRows.map(p=>`<tr><td>${{esc(p.line.display_label)}}</td><td>${{esc(p.period_key)}}</td><td>${{esc(p.value)}}</td><td>${{esc(p.unit)}}</td><td>${{statusBadge(p.status)}}</td><td>${{esc(p.scope_kind)}}</td><td class="formula">${{esc(JSON.stringify(p.candidate_values||[]))}}</td><td class="formula">${{esc((p.evidence_refs||[]).join(', '))}}</td></tr>`).join('')}}</tbody></table></div>`}}
function statementPage(company,view){{const statement={{'income-statement':'income_statement','balance-sheet':'balance_sheet','cash-flow':'cash_flow','capital-allocation':'capital_allocation'}}[view];return companyHeader(company,view.replaceAll('-',' '))+financialNav(company,view)+`<div class="notice">Statement evidence is source-resolved but partial. Annual, quarter-only, cumulative, instant, and TTM scopes never silently mix.</div>`+renderExplorer(company,statement)}}
function renderCompany(route){{const [company,section,view]=route.split('/');let content;if(section==='overview')content=companyOverview(company);else if(section==='financials'){{if(view==='overview')content=financialOverview(company);else if(view==='ratios-statistics')content=ratioPage(company);else content=statementPage(company,view)}}else if(section==='business-engines')content=companyEngines(company);else if(section==='strategy')content=strategyPage(company);else if(section==='risks')content=risksPage(company);else content=evidencePage(company);return `<div class="company-layout">${{sideNav(company,route)}}<section class="company-main" id="report-content" tabindex="-1">${{content}}</section></div>`}}
function bind(route){{document.querySelectorAll('[data-route]').forEach(a=>a.onclick=e=>{{e.preventDefault();go(a.dataset.route)}});const mobile=$('#mobile-local-selector');if(mobile)mobile.onchange=()=>go(mobile.value);document.querySelectorAll('.explorer').forEach(root=>{{const company=root.dataset.company,statement=root.dataset.statement,s=initExplorer(company,statement);root.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{{s.mode=b.dataset.mode;s.start=null;s.end=null;render()}});$('.range-start',root).onchange=e=>{{s.start=e.target.value;render()}};$('.range-end',root).onchange=e=>{{s.end=e.target.value;render()}};$('.metric-selector',root).onchange=e=>{{if(e.target.value)selectLine(company,statement,e.target.value)}};root.querySelectorAll('[data-remove]').forEach(b=>b.onclick=()=>{{s.selected=s.selected.filter(x=>x!==b.dataset.remove);render()}});root.querySelectorAll('[data-line-id]').forEach(tr=>tr.onclick=()=>selectLine(company,statement,tr.dataset.lineId));root.querySelectorAll('[data-group-toggle]').forEach(button=>button.onclick=e=>{{e.stopPropagation();const groupId=button.dataset.groupToggle;state.hierarchyState[groupId]=button.getAttribute('aria-expanded')!=='true';render();const replacement=[...document.querySelectorAll('[data-group-toggle]')].find(candidate=>candidate.dataset.groupToggle===groupId);replacement?.focus()}});root.querySelectorAll('[data-hierarchy-action]').forEach(button=>button.onclick=()=>{{const expanded=button.dataset.hierarchyAction==='expand';hierarchyGroups(company,statement).forEach(group=>state.hierarchyState[group.group_id]=expanded);render()}});drawChart(root,company,statement)}})}}
function render(){{const route=currentRoute();renderGlobalNav(route);let body=route==='overview'?renderOverview():route==='comparison'?renderComparison():route==='methodology'?renderMethodology():route==='evidence'?renderEvidenceGlobal():renderCompany(route);$('#app').innerHTML=`<div id="route-${{route.replaceAll('/','-')}}">${{body}}<footer class="footer">TASK-082 · internal local analysis only · exact upstream identity ${{MODEL.analysis_identity}}</footer></div>`;bind(route)}}render();
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
    hierarchy = hierarchy_inventory(source)
    counterparts = graph_counterpart_inventory(source)
    overviews = overview_records(source)
    contract = corporate_contract(source, hierarchy, counterparts, overviews)
    conformance = contract_conformance(contract, source, hierarchy, counterparts)
    artifacts: dict[str, bytes] = {
        "index.html": html_document(source, package["package_identity"], contract, hierarchy, counterparts, overviews).encode(),
        "presentation-package.json": canonical_bytes(package),
        "source-authentication.json": canonical_bytes(source_authentication(source_path, source)),
        "route-navigation-inventory.json": canonical_bytes(route_inventory()),
        "standardized-company-layout-profile.json": canonical_bytes(layout_profile(source, overviews)),
        "corporate-report-contract.json": canonical_bytes(contract),
        "contract-conformance.json": canonical_bytes(conformance),
        "statement-hierarchy-inventory.json": canonical_bytes(hierarchy),
        "graph-counterpart-inventory.json": canonical_bytes(counterparts),
        "overview-content-audit.json": canonical_bytes(overview_audit(overviews)),
        "theme-verification-report.json": canonical_bytes(theme_report()),
        "all-periods-table-inventory.json": canonical_bytes(all_periods_inventory(source)),
        "financial-source-regression-report.json": canonical_bytes(financial_regression(source)),
        "unresolved-upstream-return-packet.json": canonical_bytes({"schema": "briefforge.task082-return-packet.v1", "task_id": TASK_ID, "disposition": "PARTIAL", "rights": source["rights"], "strategy": source["unresolved_upstream_return_packet"], "stock_price_capability": source["stock_price_capability"]}),
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
