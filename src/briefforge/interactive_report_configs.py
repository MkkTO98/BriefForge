"""Report-specific structured content for the reusable interactive foundation."""
from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping


def _chart(kind: str, title: str, seed: int) -> dict[str, Any]:
    labels = [str(year) for year in range(2017, 2027)]
    series = [
        {"name": "Norway", "values": [98 + seed, 99 + seed, 101 + seed, 102 + seed, 104 + seed, 103 + seed, 105 + seed, 104 + seed, 106 + seed, 107 + seed]},
        {"name": "Denmark", "values": [97 + seed, 98 + seed, 100 + seed, 102 + seed, 105 + seed, 104 + seed, 106 + seed, 107 + seed, 108 + seed, 109 + seed]},
        {"name": "Sweden", "values": [99 + seed, 100 + seed, 102 + seed, 104 + seed, 103 + seed, 102 + seed, 101 + seed, 103 + seed, 104 + seed, 105 + seed]},
    ]
    if kind in {"timeline", "scenario"}:
        if kind == "scenario":
            series = [{"name": "baseline", "values": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]}, {"name": "upside", "values": [100, 101, 103, 105, 107, 109, 111, 113, 116, 119]}, {"name": "downside", "values": [100, 99, 99, 98, 98, 99, 100, 100, 101, 102]}]
        return {"kind": kind, "title": title, "subtitle": "Embedded demonstration paths", "labels": labels, "data": series, "series": [x["name"] for x in series], "selectable": kind == "timeline", "filter_geography": kind == "timeline", "min": 90, "max": 150, "source": "Interface-model data · illustrative only"}
    if kind == "scatter":
        return {"kind": kind, "title": title, "filter_geography": True, "data": [{"name": "Norway", "x": 1.8, "y": 2.2}, {"name": "Denmark", "x": 2.2, "y": 1.8}, {"name": "Sweden", "x": 1.4, "y": 2.3}], "xmin": 1, "xmax": 2.5, "min": 1, "max": 2.7, "source": "Interface-model data · illustrative only"}
    if kind == "heatmap":
        return {"kind": kind, "title": title, "columns": ["", "NO 24", "NO 26", "DK 24", "SE 24"], "data": [["Activity", {"value": "2.1", "level": 1}, {"value": "1.8", "level": -1}, {"value": "2.3", "level": 2}, {"value": "1.4", "level": -2}], ["Prices", {"value": "2.7", "level": 2}, {"value": "2.2", "level": 1}, {"value": "1.8", "level": -1}, {"value": "2.3", "level": 1}]], "source": "Interface-model regime scores · illustrative only"}
    if kind == "evidence-table":
        return {"kind": kind, "title": title, "columns": ["Indicator", "Country", "Status", "Cadence"], "data": [["Housing turnover", "Norway", "Elevated", "Monthly"], ["Services pressure", "Denmark", "Watch", "Quarterly"], ["Real income", "Sweden", "Improving", "Quarterly"]], "source": "Interface-model register · illustrative only"}
    if kind == "contribution":
        data = [
            {"name": "Consumption", "value": 0.8},
            {"name": "Investment", "value": 0.5},
            {"name": "Public demand", "value": 0.7},
            {"name": "Net trade", "value": -0.2},
        ]
        return {"kind": kind, "title": title, "subtitle": "Positive and negative demand components share a visible zero line", "data": data, "series": [x["name"] for x in data], "selectable": True, "min": -1, "max": 1.5, "source": "Interface-model contributions · illustrative only"}
    data = [{"name": "Norway", "value": .7 + seed / 50, "other": .3}, {"name": "Denmark", "value": .4, "other": .8}, {"name": "Sweden", "value": -.2, "other": .2}]
    return {"kind": kind, "title": title, "subtitle": "Direct labels preserve the evidence frame", "data": data, "series": [], "selectable": False, "filter_geography": kind == "comparison", "min": -1, "max": 1.5, "source": "Interface-model data · illustrative only"}


def macro_config() -> dict[str, Any]:
    divisions = [
        ("overview", "Overview", ["Executive pulse", "Key developments", "Cross-country comparison", "Watch list"]),
        ("activity", "Activity & Demand", ["Growth", "Consumption", "Investment", "Production"]),
        ("prices", "Prices & Rates", ["Inflation", "Components", "Policy rates", "Financial conditions"]),
        ("labour", "Labour & Households", ["Labour market", "Wages", "Households", "Housing"]),
        ("external", "External & Energy", ["Trade", "Currency", "Energy", "External exposure"]),
        ("risks", "Risks & Scenarios", ["Scenario paths", "Risk map", "Transmission", "Early signals"]),
        ("methods", "Methods & Sources", ["Methodology", "Definitions", "Source structure", "Accessibility"]),
    ]
    kinds = ["timeline", "contribution", "comparison", "heatmap", "scatter", "scenario", "coefficient", "dumbbell", "evidence-table"]
    ds = []
    n = 0
    standard_subsections = [{"id": "summary", "label": "Summary"}, {"id": "evidence", "label": "Evidence"}, {"id": "interpretation", "label": "Interpretation"}]
    for did, label, pages in divisions:
        configured = []
        for page_label in pages:
            kind = kinds[n % len(kinds)]
            configured.append({
                "id": page_label.lower().replace(" & ", "-").replace(" ", "-"), "label": page_label,
                "headline": {"Overview": "A softer landing, with the margin for error still narrow."}.get(label, f"{page_label}: the composition matters more than the headline."),
                "lead": "An editorial model page demonstrating bounded interaction, legible evidence and explicit uncertainty without claiming current facts.",
                "meta": "Nordic model edition", "status": "Illustrative interface model",
                "summary": "The selected geography receives emphasis while declared comparators remain visible and reversible.",
                "subsections": [] if did == "methods" else standard_subsections,
                "kpis": ([{"label": "Activity pulse", "value": "1.8%", "note": "moderate", "detail": "Illustrative composite for interface review; not an observed statistic."}, {"label": "Inflation regime", "value": "2.2%", "note": "easing", "detail": "A coherent demonstration value used only to exercise hierarchy."}, {"label": "Policy setting", "value": "3.6%", "note": "restrictive", "detail": "No forecast or policy recommendation is implied."}, {"label": "Household pulse", "value": "0.9%", "note": "soft", "detail": "Illustrative only."}, {"label": "External balance", "value": "4.1%", "note": "supportive", "detail": "Illustrative only."}, {"label": "Risk breadth", "value": "3 / 5", "note": "contained", "detail": "Illustrative only."}] if n == 0 else [] if did == "methods" else [{"label": "Activity pulse", "value": "1.8%", "note": "moderate", "detail": "Illustrative composite for interface review; not an observed statistic."}, {"label": "Policy setting", "value": "3.6%", "note": "restrictive", "detail": "No forecast or policy recommendation is implied."}]),
                "charts": [_chart(kind, f"{page_label} evidence", n), _chart("timeline" if kind != "timeline" else "comparison", "Context view", n)],
                "prose": "Evidence should be interpreted as a coherent visual demonstration, not as economic measurement.",
                "interpretation": "Model paths are illustrative only. Selection changes emphasis, never the declared evidence universe.",
                "details": [{"title": "Method note", "text": "Hand-authored static values exercise report hierarchy, chart grammar, accessibility and responsive behavior."}],
                "bespoke": [{"title": "What changed in this model edition", "text": "A bounded editorial subsection can be declared by a report without entering the generic renderer."}] if n in {1, 18} else [],
            })
            n += 1
        ds.append({"id": did, "label": label, "pages": configured})
    kpi_values = {
        "Activity pulse": {"Norway": "1.8%", "Denmark": "2.2%", "Sweden": "1.4%"},
        "Inflation regime": {"Norway": "2.2%", "Denmark": "1.8%", "Sweden": "2.3%"},
        "Policy setting": {"Norway": "3.6%", "Denmark": "3.2%", "Sweden": "3.1%"},
        "Household pulse": {"Norway": "0.9%", "Denmark": "1.2%", "Sweden": "0.5%"},
        "External balance": {"Norway": "4.1%", "Denmark": "3.4%", "Sweden": "2.2%"},
        "Risk breadth": {"Norway": "3 / 5", "Denmark": "2 / 5", "Sweden": "4 / 5"},
    }
    for division in ds:
        for page in division["pages"]:
            for kpi in page.get("kpis", []):
                kpi["values_by_geography"] = kpi_values[kpi["label"]]
    return {
        "id": "nordic-macro-interface-model", "title": "Nordic Macroeconomic Monitor — Interactive Model Report", "edition": "01 / 2026",
        "warning": "Interface-model data — illustrative only; not analytical evidence.", "status": "Static design-reference content; do not cite as evidence.",
        "source_label": "Embedded interface-model series · no live data",
        "controls": [
            {"id": "geography", "label": "Primary geography", "type": "primary-geography", "options": ["Norway", "Denmark", "Sweden"], "value": "Norway"},
            {"id": "compare", "label": "Comparison geography", "type": "multi-checkbox", "options": ["Norway", "Denmark", "Sweden"], "value": ["Denmark", "Sweden"]},
            {"id": "horizon", "label": "Horizon", "type": "range", "min": 0, "max": 2, "step": 1, "options": ["3Y", "6Y", "10Y"], "value": 2},
            {"id": "display", "label": "Display", "type": "segmented", "options": ["Absolute", "Indexed"], "value": "Absolute"},
            {"id": "scenario", "label": "Scenario", "type": "select", "options": ["baseline", "upside", "downside"], "value": "baseline"},
            {"id": "theme", "label": "Appearance", "type": "toggle", "value": False},
        ], "divisions": ds,
    }


def norway_config(data: Mapping[str, Any], source_path: str | Path) -> dict[str, Any]:
    selected = list(data["selected_correlates"])
    raw = {x["series_a_code"]: x for x in data["raw_level_context_not_primary"]}
    labels = {"SP.DYN.LE00.IN": "Life expectancy", "EG.ELC.RNWX.ZS": "Non-hydro renewable electricity share", "EG.ELC.FOSL.ZS": "Fossil electricity share"}
    coefficient_data = [{"name": labels[x["series_a_code"]], "relationship": x["series_a_name"] + " ↔ " + x["series_b_name"], "value": float(x["coefficient"]), "exact": x["coefficient"], "n": x["aligned_observation_count"], "period": f"{x['aligned_period_start']}–{x['aligned_period_end']}", "transformation": x["transformation_id"], "method": x["method_id"]} for x in selected]
    dumbbell_data = [{"name": labels[x["series_a_code"]], "value": float(x["coefficient"]), "difference_exact": x["coefficient"], "other": float(raw[x["series_a_code"]]["coefficient"]), "raw_exact": raw[x["series_a_code"]]["coefficient"]} for x in selected]
    evidence_rows = [[labels[x["series_a_code"]], x["series_a_code"], x["coefficient"], str(x["aligned_observation_count"]), f"{x['aligned_period_start']}–{x['aligned_period_end']}", x["transformation_id"], x["method_id"], x["package_id"]] for x in selected]
    exact_finding = data["analytical_review"]["numerical_comparison"]
    common_details = [{"title": "Causality warning", "text": data["methodology"]["correlation_vs_causation"]}, {"title": "Confidence", "text": data["analytical_review"]["confidence"]}]
    divisions = [
        {"id": "question", "label": "Question & selection", "pages": [
            {"id": "analytical-question", "label": "Analytical question", "subsections": [{"id": "summary", "label": "Finding"}, {"id": "evidence", "label": "Transformation evidence"}, {"id": "interpretation", "label": "Boundaries"}], "headline": "Annual changes tell a much weaker story than raw levels.", "lead": data["precise_analytical_question"], "meta": "Norway · 1991–2024 nominal scope", "status": data["task_type"], "summary": data["selection_rationale"], "kpis": [{"label": "Selected relationships", "value": "3", "note": "one target", "detail": "Three admitted first-difference companions share Norway and under-5 mortality as target."}, {"label": "Aligned samples", "value": "31–34", "note": "annual observations", "detail": "Aligned windows differ: 1991–2021, 1991–2023 and 1991–2024."}], "prose": data["results"]["report_thesis"], "interpretation": data["analytical_review"]["interpretation"], "details": common_details},
            {"id": "bounded-selection", "label": "Bounded selection", "headline": "Selection was result-informed and disclosed.", "lead": data["selection_procedure"]["candidate_universe"], "summary": data["selection_procedure"]["ranking_basis"], "meta": "Four candidate questions", "status": "Not coefficient-blind; not autonomous discovery", "bespoke": [{"title": "Superlative boundary", "text": data["selection_procedure"]["superlative_boundary"]}], "interpretation": data["methodology"]["multiple_comparison_risk"], "details": [{"title": "Selection timing", "text": data["selection_procedure"]["selection_timing"]}]},
        ]},
        {"id": "findings", "label": "Findings", "pages": [
            {"id": "annual-change", "label": "Annual-change evidence", "subsections": [{"id": "summary", "label": "Finding"}, {"id": "evidence", "label": "Exact coefficients"}, {"id": "interpretation", "label": "Boundaries"}], "headline": "Three exact coefficients, bounded to one selected set.", "lead": exact_finding, "meta": "First differences", "status": "Descriptive finite-window association", "summary": data["results"]["report_thesis"], "kpis": [{"label": "Largest positive", "value": "+0.3855860099", "note": "n=31 · 1991–2021", "detail": labels["EG.ELC.RNWX.ZS"]}, {"label": "Most negative", "value": "−0.207863151096", "note": "n=34 · 1991–2024", "detail": labels["SP.DYN.LE00.IN"]}, {"label": "Closest to zero", "value": "−0.083376899169", "note": "n=33 · 1991–2023", "detail": labels["EG.ELC.FOSL.ZS"]}], "charts": [{"kind": "coefficient", "title": "Selected first-difference Pearson coefficients", "subtitle": "Exact values available in the single evidence table", "data": coefficient_data, "series": [x["name"] for x in coefficient_data], "selectable": True, "min": -1, "max": 1, "unit": "Pearson r", "x_decimals": 2, "y_decimals": 3, "source": data["methodology"]["correlation_source"]}], "interpretation": data["methodology"]["ranking_comparability"], "details": common_details},
            {"id": "estimand-comparison", "label": "Raw vs transformed", "subsections": [{"id": "summary", "label": "Finding"}, {"id": "evidence", "label": "Transformation evidence"}, {"id": "interpretation", "label": "Rejected interpretations"}], "headline": "Changing the estimand changes the story.", "lead": data["methodology"]["common_trends_spurious_correlation"], "meta": "Raw level → first difference", "status": "Different estimands; not a reversal mechanism", "charts": [{"kind": "dumbbell", "title": "Raw-level and first-difference coefficients", "subtitle": "Blue: first difference · amber: raw level", "data": dumbbell_data, "series": ["Raw level", "First difference"], "selectable": True, "min": -1, "max": 1, "unit": "Pearson r", "x_decimals": 2, "y_decimals": 3, "source": "Accepted KnowledgeForge raw and first-difference packages"}], "summary": data["analytical_review"]["material_counterevidence"], "interpretation": data["analytical_review"]["discrimination_limit"], "details": [{"title": "Rejected interpretations", "text": "; ".join(data["analytical_review"]["unsupported_speculation_excluded"])}]},
        ]},
        {"id": "method", "label": "Method & limits", "pages": [
            {"id": "transformation", "label": "Transformation", "headline": "Annual first differences are not percentage growth.", "lead": data["target_indicator_definition"]["growth_semantics"], "meta": data["methodology"]["primary_transformation"], "status": data["methodology"]["correlation_method"], "summary": data["methodology"]["annual_alignment_and_lag_semantics"], "kpis": [{"label": "Entity", "value": "NOR", "note": "country-specific", "detail": data["methodology"]["pooled_vs_country_specific"]}, {"label": "Samples", "value": "31 / 33 / 34", "note": "aligned n", "detail": data["methodology"]["minimum_overlap"]}], "interpretation": data["methodology"]["cross_sectional_vs_time_series"], "details": [{"title": "Zero, negative and missing behavior", "text": data["methodology"]["zero_negative_missing_behavior"]}, {"title": "Outlier sensitivity", "text": data["methodology"]["outlier_sensitivity"]}]},
            {"id": "limitations", "label": "Limitations", "headline": "What this evidence cannot establish.", "lead": data["analytical_review"]["discrimination_limit"], "meta": "Interpretation boundary", "status": data["analytical_review"]["confidence"], "summary": " ".join(data["limitations"]), "bespoke": [{"title": "Plausible alternatives", "text": "; ".join(data["analytical_review"]["plausible_alternatives"])}], "interpretation": data["methodology"]["correlation_vs_causation"], "details": [{"title": "Rejected interpretations", "text": "; ".join(data["analytical_review"]["unsupported_speculation_excluded"])}]},
        ]},
        {"id": "evidence", "label": "Evidence & provenance", "pages": [
            {"id": "register", "label": "Evidence register", "headline": "Exact admitted evidence in one place.", "lead": "This is the report’s only evidence table; coefficients are transcribed without recomputation.", "meta": "3 selected packages", "status": "Accepted · validation pass", "charts": [{"kind": "evidence-table", "title": "Selected annual-change relationships", "columns": ["Relationship", "Code", "Exact r", "n", "Aligned period", "Transformation", "Method", "Package identity"], "data": evidence_rows, "source": data["methodology"]["correlation_source"]}], "summary": data["analytical_review"]["admitted_evidence"], "interpretation": data["methodology"]["ranking_comparability"], "details": common_details},
            {"id": "provenance", "label": "Provenance", "headline": "Package identity and ownership remain visible.", "lead": data["handoff_boundary"]["consumer_contract"], "meta": data["package_id"], "status": data["artifact_status"], "summary": f"Authoritative input: {Path(source_path)} · declared content SHA-256: {data['content_sha256']}", "bespoke": [{"title": "Evidence package references", "text": "; ".join(Path(x).name for x in data["provenance_references"])}], "interpretation": data["handoff_boundary"]["locator_rule"], "details": [{"title": "Ownership", "text": data["handoff_boundary"]["analytical_owner"] + " " + data["handoff_boundary"]["presentation_owner"]}]},
        ]},
    ]
    return {"id": "norway-t035", "title": "Norway demographic-growth correlation report", "edition": "T-035", "warning": "Correlation ≠ causation. Descriptive finite-window association only; no mechanism, forecast, significance, policy or investment inference.", "status": data["artifact_status"], "source_label": f"T-035 · {data['content_sha256']}", "controls": [{"id": "theme", "label": "Appearance", "type": "toggle", "value": False}], "divisions": divisions}
