"""Bounded interactive renderer for the T-035 Norway correlation report.

This vertical slice reads authenticated upstream coefficients and renders them
without recomputation. It is intentionally report-specific rather than a chart
framework or dashboard platform.
"""

from __future__ import annotations

from collections.abc import Mapping
from html import escape
import json
from pathlib import Path
from typing import Any

EXPECTED_PACKAGE_ID = "insightforge-t035-demographic-growth-correlation-report-input-v1"
REPORT_FILENAME = "norway_demographic_growth_interactive_report.html"

_LABELS = {
    "SP.DYN.LE00.IN": "Life expectancy",
    "EG.ELC.RNWX.ZS": "Non-hydro renewable electricity share",
    "EG.ELC.FOSL.ZS": "Fossil electricity share",
}


def _text(value: object) -> str:
    return escape(str(value), quote=True)


def _coefficient(value: object) -> float:
    number = float(str(value))
    if not -1.0 <= number <= 1.0:
        raise ValueError(f"Correlation coefficient outside [-1, 1]: {value}")
    return number


def _display_coefficient(value: object) -> str:
    return f"{_coefficient(value):+.3f}"


def _exact_coefficient(value: object) -> str:
    text = str(value)
    _coefficient(text)
    return text if text.startswith("-") else f"+{text}"


def _label(row: Mapping[str, Any]) -> str:
    code = str(row["series_a_code"])
    return _LABELS.get(code, str(row["series_a_name"]))


def _period(row: Mapping[str, Any]) -> str:
    return f"{row['aligned_period_start']}–{row['aligned_period_end']}"


def _transformation(row: Mapping[str, Any]) -> str:
    return "First difference (annual change)" if row["transformation_id"] != "raw" else "Raw level"


def _tooltip(row: Mapping[str, Any]) -> str:
    return " · ".join(
        (
            _label(row),
            f"r = {_exact_coefficient(row['coefficient'])}",
            f"n = {row['aligned_observation_count']}",
            f"period {_period(row)}",
            _transformation(row),
        )
    )


def _ordered_rows(data: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    rows = list(data[key])
    by_code = {str(row["series_a_code"]): row for row in rows}
    expected = tuple(_LABELS)
    if set(by_code) != set(expected) or len(rows) != len(expected):
        raise ValueError(f"Expected exactly the three T-035 selected relationships in {key}")
    return [by_code[code] for code in expected]


def _annual_chart(rows: list[Mapping[str, Any]]) -> str:
    rendered = []
    for row in rows:
        coefficient = _coefficient(row["coefficient"])
        width = abs(coefficient) * 50
        side = "positive" if coefficient >= 0 else "negative"
        style = f"--magnitude:{width:.6f}%;"
        rendered.append(
            f"""<div class="bar-row">
              <div class="chart-label"><strong>{_text(_label(row))}</strong><span>n={_text(row['aligned_observation_count'])} · {_text(_period(row))}</span></div>
              <div class="correlation-track"><span class="zero-line" aria-hidden="true"></span>
                <button class="correlation-bar mark {side}" style="{style}" type="button"
                  aria-label="{_text(_tooltip(row))}" data-tooltip="{_text(_tooltip(row))}">
                  <span>{_text(_display_coefficient(row['coefficient']))}</span>
                </button>
              </div>
            </div>"""
        )
    return "".join(rendered)


def _comparison_chart(
    raw_rows: list[Mapping[str, Any]], difference_rows: list[Mapping[str, Any]]
) -> str:
    raw_by_code = {str(row["series_a_code"]): row for row in raw_rows}
    diff_by_code = {str(row["series_a_code"]): row for row in difference_rows}
    rendered = []
    for code in _LABELS:
        raw = raw_by_code[code]
        diff = diff_by_code[code]
        raw_position = (_coefficient(raw["coefficient"]) + 1) * 50
        diff_position = (_coefficient(diff["coefficient"]) + 1) * 50
        left = min(raw_position, diff_position)
        span = abs(raw_position - diff_position)
        reversal = _coefficient(raw["coefficient"]) * _coefficient(diff["coefficient"]) < 0
        rendered.append(
            f"""<div class="comparison-row{' sign-reversal' if reversal else ''}" data-relationship="{_text(code)}">
              <div class="chart-label"><strong>{_text(_LABELS[code])}</strong>{'<span class="reversal-tag">Sign change across estimands</span>' if reversal else ''}</div>
              <div class="comparison-track">
                <span class="zero-line"></span>
                <span class="connector" style="left:{left:.6f}%;width:{span:.6f}%"></span>
                <button class="comparison-dot raw-dot mark" type="button" style="left:{raw_position:.6f}%"
                  aria-label="{_text(_tooltip(raw))}" data-tooltip="{_text(_tooltip(raw))}"><span>Raw {_text(_display_coefficient(raw['coefficient']))}</span></button>
                <button class="comparison-dot difference-dot mark" type="button" style="left:{diff_position:.6f}%"
                  aria-label="{_text(_tooltip(diff))}" data-tooltip="{_text(_tooltip(diff))}"><span>Change {_text(_display_coefficient(diff['coefficient']))}</span></button>
              </div>
            </div>"""
        )
    return "".join(rendered)


def _evidence_table(rows: list[Mapping[str, Any]]) -> str:
    body = "".join(
        f"""<tr><th scope="row">{_text(_label(row))}</th>
          <td class="numeric">{_text(_exact_coefficient(row['coefficient']))}</td>
          <td class="numeric">{_text(row['aligned_observation_count'])}</td>
          <td>{_text(_period(row))}</td>
          <td>{_text(_transformation(row))}</td></tr>"""
        for row in rows
    )
    return f"""<div class="table-wrap"><table data-evidence-table="selected-first-difference">
      <caption>Selected annual-change relationships with under-5 mortality</caption>
      <thead><tr><th>Relationship</th><th>r</th><th>n</th><th>Aligned period</th><th>Transformation</th></tr></thead>
      <tbody>{body}</tbody>
    </table></div>"""


def _list(items: list[object]) -> str:
    return "<ul>" + "".join(f"<li>{_text(item)}</li>" for item in items) + "</ul>"


def _methodology(data: Mapping[str, Any]) -> str:
    method = data["methodology"]
    rows = (
        ("Source of coefficients", method["correlation_source"]),
        ("Transformation", method["primary_transformation"]),
        ("Method", method["correlation_method"]),
        ("Alignment", method["annual_alignment_and_lag_semantics"]),
        ("Scope", method["pooled_vs_country_specific"]),
        ("Study form", method["cross_sectional_vs_time_series"]),
        ("Raw-level risk", method["common_trends_spurious_correlation"]),
        ("Selection", method["selection_mode"]),
        ("Comparability", method["ranking_comparability"]),
    )
    return "".join(
        f"<div class=\"definition\"><dt>{_text(label)}</dt><dd>{_text(value)}</dd></div>"
        for label, value in rows
    )


def _provenance(data: Mapping[str, Any]) -> str:
    refs = data["provenance_references"]
    return "<ol class=\"provenance-list\">" + "".join(
        f"<li><code>{_text(Path(str(ref)).name)}</code></li>" for ref in refs
    ) + "</ol>"


def render_t035_interactive_report(data: Mapping[str, Any], source_path: str | Path) -> str:
    """Render a self-contained bounded microsite from the authoritative T-035 package."""

    if data.get("package_id") != EXPECTED_PACKAGE_ID:
        raise ValueError("This vertical slice accepts only the authoritative T-035 package")
    difference_rows = _ordered_rows(data, "selected_correlates")
    raw_rows = _ordered_rows(data, "raw_level_context_not_primary")
    sample_sizes = [int(row["aligned_observation_count"]) for row in difference_rows]
    source = Path(source_path)
    target = data["target_indicator_definition"]
    thesis = data["results"]["report_thesis"]
    interpretation = data["analytical_review"]["interpretation"]
    causality = data["methodology"]["correlation_vs_causation"]
    raw_risk = data["methodology"]["common_trends_spurious_correlation"]
    reversal_reason = next(
        item["reason"]
        for item in data["rejected_or_misleading_relationships"]
        if "non-hydro renewable" in item["relationship"].lower()
    )

    html = f"""<!doctype html>
<html lang="en" data-report="norway-demographic-growth-t035">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Norway demographic-growth correlation report · Under-5 mortality changes</title>
<style>{_CSS}</style>
</head>
<body>
<button class="mobile-nav-toggle" type="button" aria-expanded="false" aria-controls="report-nav"><span>Report sections</span><span aria-hidden="true">☰</span></button>
<aside class="sidebar" id="report-nav" aria-label="Report navigation">
  <div class="brand"><span class="brand-mark">BF</span><span>BriefForge<br><small>Economic research</small></span></div>
  <nav><a href="#overview" class="active">Overview</a><a href="#annual-change">Annual-change evidence</a><a href="#comparison">Raw versus transformed</a><a href="#methodology">Methodology</a><a href="#sources">Sources</a></nav>
  <p class="nav-note">Norway · WDI · descriptive evidence</p>
</aside>
<main>
<section class="hero" id="overview">
  <p class="eyebrow">Norway · demographic growth evidence</p>
  <h1>Annual changes tell a much weaker story than raw levels.</h1>
  <p class="question">{_text(data['precise_analytical_question'])}</p>
  <p class="conclusion">{_text(interpretation)}</p>
  <div class="kpi-grid">
    <article class="kpi"><span>Country &amp; period</span><strong>Norway</strong><small>Nominal 1991–2024</small></article>
    <article class="kpi"><span>Selected relationships</span><strong>{len(difference_rows)}</strong><small>One target, three comparisons</small></article>
    <article class="kpi"><span>Aligned samples</span><strong>{min(sample_sizes)}–{max(sample_sizes)}</strong><small>annual observations</small></article>
    <article class="kpi caution"><span>Interpretive status</span><strong>Descriptive</strong><small>not causal</small></article>
  </div>
  <div class="causality-warning" role="note"><strong>Correlation ≠ causation.</strong><span>{_text(causality)}</span></div>
</section>

<section id="annual-change" class="report-section">
  <header class="section-heading"><div><p class="eyebrow">Primary result</p><h2>Annual-change evidence</h2></div><p>First differences compare year-to-year movement in original WDI units—not percentage growth.</p></header>
  <article class="chart-card" data-chart="annual-change-correlation">
    <div class="chart-intro"><div><h3>Selected first-difference correlations</h3><p>Correlation with annual changes in {_text(str(target['target']).lower())}</p></div><div class="legend"><span><i class="positive-key"></i>Positive</span><span><i class="negative-key"></i>Negative</span></div></div>
    <div class="axis-labels"><span>−1.0</span><span>0</span><span>+1.0</span></div>
    <div class="bar-chart">{_annual_chart(difference_rows)}</div>
    <p class="chart-note">Numerical ordering is restricted to these three selected relationships. Windows and samples differ.</p>
  </article>
  <div class="finding-grid">
    <article><span>Largest positive</span><strong>{_text(_label(data['results']['strongest_positive']))}</strong><em>r = {_text(_display_coefficient(data['results']['strongest_positive']['coefficient']))}</em></article>
    <article><span>Most negative</span><strong>{_text(_label(data['results']['strongest_negative']))}</strong><em>r = {_text(_display_coefficient(data['results']['strongest_negative']['coefficient']))}</em></article>
    <article><span>Closest to zero</span><strong>{_text(_label(data['results']['numerically_closest_to_zero_in_selected_set']))}</strong><em>r = {_text(_display_coefficient(data['results']['numerically_closest_to_zero_in_selected_set']['coefficient']))}</em></article>
  </div>
</section>

<section id="comparison" class="report-section">
  <header class="section-heading"><div><p class="eyebrow">Robustness context</p><h2>Raw level versus first difference</h2></div><p>{_text(raw_risk)}</p></header>
  <article class="chart-card comparison-card" data-chart="raw-versus-first-difference" data-view="both">
    <div class="chart-intro"><div><h3>How the estimand changes the coefficient</h3><p>Move between raw levels and annual changes. This control changes the chart.</p></div>
      <fieldset class="view-control" aria-label="Coefficient view"><legend>Display</legend>
        <label><input type="radio" name="coefficient-view" value="both" checked> Both</label>
        <label><input type="radio" name="coefficient-view" value="raw"> Raw level</label>
        <label><input type="radio" name="coefficient-view" value="difference"> First difference</label>
      </fieldset>
    </div>
    <div class="comparison-legend"><span class="raw-legend">● Raw level</span><span class="difference-legend">● First difference</span></div>
    <div class="axis-labels"><span>−1.0</span><span>0</span><span>+1.0</span></div>
    <div class="comparison-chart">{_comparison_chart(raw_rows, difference_rows)}</div>
    <p class="chart-status" aria-live="polite">Showing raw-level and first-difference coefficients.</p>
  </article>
  <article class="reversal-callout"><span class="callout-icon" aria-hidden="true">↗</span><div><h3>The renewable relationship changes sign</h3><p>{_text(reversal_reason)}</p><p>This matters because the strong negative raw-level association does not survive as the same annual-change relationship. The admitted evidence does not identify why.</p></div></article>
</section>

<section id="evidence" class="report-section compact-section">
  <header class="section-heading"><div><p class="eyebrow">Exact evidence</p><h2>Selected relationship values</h2></div><p>One supporting table preserves the precise values behind the primary chart.</p></header>
  {_evidence_table(difference_rows)}
</section>

<section id="methodology" class="report-section detail-section">
  <header class="section-heading"><div><p class="eyebrow">Expandable detail</p><h2>Methodology &amp; limitations</h2></div><p>The central conclusion remains above; technical detail is available on demand.</p></header>
  <div class="disclosure-grid">
    <details><summary>Methodology and alignment <span>+</span></summary><dl>{_methodology(data)}</dl></details>
    <details><summary>Transformation definitions <span>+</span></summary><p><strong>Target:</strong> {_text(target['growth_semantics'])}</p><p><strong>Raw level:</strong> contemporaneous Pearson correlation between source levels.</p><p><strong>First difference:</strong> contemporaneous Pearson correlation after annual first differences, labelled by ending year t.</p></details>
    <details><summary>Limitations and rejected interpretations <span>+</span></summary>{_list(data['limitations'])}<h4>Explicitly excluded</h4>{_list(data['analytical_review']['unsupported_speculation_excluded'])}</details>
    <details><summary>Alternatives the evidence cannot distinguish <span>+</span></summary>{_list(data['analytical_review']['plausible_alternatives'])}<p>{_text(data['analytical_review']['discrimination_limit'])}</p></details>
  </div>
</section>

<section id="sources" class="report-section detail-section">
  <header class="section-heading"><div><p class="eyebrow">Evidence chain</p><h2>Sources &amp; provenance</h2></div><p>Coefficients originate in accepted KnowledgeForge packages and were curated by InsightForge for BriefForge presentation.</p></header>
  <details><summary>Authoritative report input <span>+</span></summary><p><code>{_text(source)}</code></p><p>Package: <code>{_text(data['package_id'])}</code></p><p>Content SHA-256 declared upstream: <code>{_text(data['content_sha256'])}</code></p></details>
  <details><summary>Upstream evidence packages ({len(data['provenance_references'])}) <span>+</span></summary>{_provenance(data)}</details>
  <p class="ownership-note">{_text(data['handoff_boundary']['analytical_owner'])} {_text(data['handoff_boundary']['presentation_owner'])}</p>
</section>
<footer><p>{_text(thesis)}</p><span>BriefForge bounded interactive presentation · generated from T-035</span></footer>
</main>
<div class="tooltip" role="tooltip" hidden></div>
<script>{_JS}</script>
</body></html>"""
    return html


def render_t035_file(source_path: str | Path, output_directory: str | Path) -> Path:
    source = Path(source_path).resolve()
    output = Path(output_directory).resolve()
    data = json.loads(source.read_text(encoding="utf-8"))
    html = render_t035_interactive_report(data, source)
    output.mkdir(parents=True, exist_ok=True)
    report_path = output / REPORT_FILENAME
    report_path.write_text(html, encoding="utf-8")
    return report_path


_CSS = r"""
:root{--nav:#081a2c;--nav-soft:#102c48;--ink:#122033;--muted:#5d6b7c;--paper:#f4f7fa;--card:#fff;--line:#dce4ec;--blue:#2878c7;--cyan:#28a8a5;--coral:#d9685a;--amber:#e9b44c;--raw:#334e68;--shadow:0 14px 38px rgba(18,32,51,.08);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink);background:var(--paper)}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:24px}body{margin:0;background:var(--paper)}a{color:inherit}button,input,summary{font:inherit}.sidebar{position:fixed;inset:0 auto 0 0;width:260px;padding:34px 24px;background:var(--nav);color:#dce8f4;display:flex;flex-direction:column;z-index:20}.brand{display:flex;align-items:center;gap:12px;font-weight:750;letter-spacing:.02em}.brand small{font-weight:500;color:#88a4bf}.brand-mark{display:grid;place-items:center;width:42px;height:42px;border:1px solid #47637e;border-radius:12px;color:#fff;background:var(--nav-soft)}.sidebar nav{display:grid;gap:8px;margin-top:68px}.sidebar nav a{padding:12px 14px;border-radius:9px;text-decoration:none;color:#a9bed1;font-size:.93rem}.sidebar nav a:hover,.sidebar nav a:focus-visible,.sidebar nav a.active{background:var(--nav-soft);color:#fff;outline:none}.nav-note{margin-top:auto;color:#7894ae;font-size:.8rem}.mobile-nav-toggle{display:none}main{margin-left:260px}.hero,.report-section,footer{max-width:1160px;margin:0 auto;padding:84px 64px}.hero{min-height:720px;display:flex;flex-direction:column;justify-content:center}.eyebrow{text-transform:uppercase;letter-spacing:.16em;font-size:.72rem;font-weight:800;color:var(--blue);margin:0 0 15px}.hero h1{font-family:Georgia,"Times New Roman",serif;font-size:clamp(3rem,6vw,5.9rem);font-weight:500;line-height:.98;letter-spacing:-.045em;max-width:950px;margin:0}.question{font-size:1.12rem;line-height:1.65;max-width:820px;color:var(--muted);margin:34px 0 10px}.conclusion{font-size:1.25rem;line-height:1.55;max-width:850px;font-weight:650}.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:34px}.kpi{background:var(--card);border-top:3px solid var(--cyan);padding:21px;border-radius:4px;box-shadow:var(--shadow);min-width:0}.kpi.caution{border-color:var(--amber)}.kpi span,.kpi small{display:block;color:var(--muted);font-size:.76rem}.kpi strong{display:block;font-size:1.55rem;margin:9px 0 4px}.causality-warning{display:flex;align-items:center;gap:16px;margin-top:24px;padding:18px 22px;background:#fff6df;border-left:5px solid var(--amber);box-shadow:0 5px 20px rgba(85,63,20,.06)}.causality-warning strong{white-space:nowrap}.causality-warning span{color:#624f25}.report-section{padding-top:92px;padding-bottom:92px;border-top:1px solid var(--line)}.section-heading{display:grid;grid-template-columns:1fr 1fr;gap:70px;align-items:end;margin-bottom:36px}.section-heading h2{font-family:Georgia,"Times New Roman",serif;font-size:clamp(2.2rem,4vw,3.7rem);font-weight:500;letter-spacing:-.035em;line-height:1.05;margin:0}.section-heading>p{color:var(--muted);line-height:1.65;margin:0}.chart-card{position:relative;background:var(--card);padding:34px;border-radius:8px;box-shadow:var(--shadow);overflow:visible}.chart-intro{display:flex;align-items:flex-start;justify-content:space-between;gap:20px}.chart-intro h3{font-size:1.15rem;margin:0 0 6px}.chart-intro p,.chart-note{color:var(--muted);margin:0;font-size:.9rem}.legend,.comparison-legend{display:flex;gap:18px;color:var(--muted);font-size:.78rem}.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px}.positive-key{background:var(--cyan)}.negative-key{background:var(--coral)}.axis-labels{display:grid;grid-template-columns:1fr 1fr 1fr;margin:30px 0 10px;padding-left:255px;color:#8390a0;font-size:.72rem}.axis-labels span:nth-child(2){text-align:center}.axis-labels span:last-child{text-align:right}.bar-row,.comparison-row{display:grid;grid-template-columns:235px minmax(0,1fr);gap:20px;align-items:center;min-height:82px;border-top:1px solid #edf1f5}.chart-label strong,.chart-label span{display:block}.chart-label strong{font-size:.9rem;line-height:1.25}.chart-label span{color:var(--muted);font-size:.72rem;margin-top:5px}.correlation-track,.comparison-track{height:42px;position:relative;background:linear-gradient(to right,transparent 49.85%,#97a6b5 49.85%,#97a6b5 50.15%,transparent 50.15%)}.zero-line{position:absolute;left:50%;top:0;bottom:0;width:1px;background:#9bacbb}.correlation-bar{position:absolute;top:8px;height:27px;width:var(--magnitude);border:0;cursor:pointer;min-width:4px;transition:filter .15s,transform .15s}.correlation-bar:hover,.correlation-bar:focus-visible{filter:brightness(.88);transform:scaleY(1.15);outline:3px solid rgba(40,120,199,.2);outline-offset:2px}.correlation-bar.positive{left:50%;background:var(--cyan);border-radius:0 4px 4px 0}.correlation-bar.negative{right:50%;background:var(--coral);border-radius:4px 0 0 4px}.correlation-bar span{position:absolute;white-space:nowrap;top:4px;font-weight:750;font-size:.76rem}.correlation-bar.positive span{left:calc(100% + 7px);color:#167a78}.correlation-bar.negative span{right:calc(100% + 7px);color:#a84237}.chart-note{margin-top:24px;padding-top:18px;border-top:1px solid var(--line)}.finding-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:16px}.finding-grid article{padding:22px;background:#eaf1f7}.finding-grid span,.finding-grid strong,.finding-grid em{display:block}.finding-grid span{color:var(--muted);font-size:.72rem;text-transform:uppercase;letter-spacing:.1em;font-weight:800}.finding-grid strong{margin:12px 0 6px}.finding-grid em{font-style:normal;color:var(--blue);font-weight:750}.view-control{display:flex;flex-wrap:wrap;gap:4px;border:0;padding:0;margin:0}.view-control legend{font-size:.7rem;color:var(--muted);margin:0 0 6px}.view-control label{cursor:pointer;padding:8px 10px;border:1px solid var(--line);font-size:.76rem;background:#fff}.view-control label:has(input:checked){background:var(--nav);color:#fff;border-color:var(--nav)}.view-control input{position:absolute;opacity:0}.view-control label:focus-within{outline:3px solid rgba(40,120,199,.25)}.comparison-legend{justify-content:flex-end;margin-top:23px}.raw-legend{color:var(--raw)}.difference-legend{color:var(--blue)}.comparison-track{height:68px}.connector{position:absolute;top:33px;height:2px;background:#aebbc7}.comparison-dot{position:absolute;top:25px;width:18px;height:18px;transform:translateX(-50%);border-radius:50%;border:3px solid #fff;box-shadow:0 0 0 2px currentColor;cursor:pointer;transition:transform .2s,opacity .2s}.comparison-dot:hover,.comparison-dot:focus-visible{transform:translateX(-50%) scale(1.35);outline:none}.comparison-dot span{position:absolute;white-space:nowrap;top:23px;left:50%;transform:translateX(-50%);font-size:.67rem;font-weight:750}.raw-dot{background:var(--raw);color:var(--raw)}.difference-dot{background:var(--blue);color:var(--blue)}.comparison-card[data-view="raw"] .difference-dot,.comparison-card[data-view="difference"] .raw-dot{display:none}.comparison-card[data-view="raw"] .connector,.comparison-card[data-view="difference"] .connector{display:none}.sign-reversal{background:linear-gradient(90deg,rgba(233,180,76,.09),transparent)}.reversal-tag{display:inline-block!important;color:#735715!important;background:#fff1c8;padding:4px 7px;margin-top:7px!important}.chart-status{color:var(--muted);font-size:.8rem;border-top:1px solid var(--line);padding-top:18px;margin-bottom:0}.reversal-callout{display:flex;gap:18px;margin-top:18px;padding:27px;background:var(--nav);color:#eaf3fb}.reversal-callout h3{margin:0 0 8px}.reversal-callout p{color:#b8cadb;line-height:1.55;margin:6px 0}.callout-icon{font-size:2rem;color:var(--amber)}.compact-section{padding-top:76px}.table-wrap{overflow-x:auto;background:var(--card);box-shadow:var(--shadow);padding:12px 22px}table{width:100%;border-collapse:collapse;font-size:.87rem}caption{text-align:left;padding:16px 0;font-weight:750}th,td{text-align:left;padding:16px 12px;border-top:1px solid var(--line);vertical-align:top}thead th{color:var(--muted);font-size:.7rem;text-transform:uppercase;letter-spacing:.08em}.numeric{font-variant-numeric:tabular-nums;font-weight:700}.disclosure-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}details{background:var(--card);border-bottom:1px solid var(--line);padding:0 22px}summary{cursor:pointer;list-style:none;font-weight:750;padding:20px 0;display:flex;justify-content:space-between}summary::-webkit-details-marker{display:none}details[open] summary span{transform:rotate(45deg)}details>p,details>ul,details>ol,details>dl{color:var(--muted);line-height:1.6;font-size:.88rem;margin:0 0 22px}.definition{display:grid;grid-template-columns:140px 1fr;gap:18px;border-top:1px solid var(--line);padding:12px 0}.definition dt{font-weight:750;color:var(--ink)}.definition dd{margin:0}.provenance-list code{word-break:break-word}.ownership-note{color:var(--muted);line-height:1.6}footer{padding-top:54px;padding-bottom:72px;border-top:1px solid var(--line);color:var(--muted)}footer p{font-family:Georgia,"Times New Roman",serif;color:var(--ink);font-size:1.35rem;line-height:1.45;max-width:900px}footer span{font-size:.72rem;text-transform:uppercase;letter-spacing:.1em}.tooltip{position:fixed;z-index:100;background:var(--nav);color:#fff;padding:10px 12px;border-radius:5px;font-size:.75rem;max-width:330px;box-shadow:0 8px 26px rgba(0,0,0,.2);pointer-events:none}
@media(max-width:900px){.sidebar{width:220px}.sidebar nav{margin-top:40px}main{margin-left:220px}.hero,.report-section,footer{padding-left:32px;padding-right:32px}.kpi-grid{grid-template-columns:1fr 1fr}.section-heading{grid-template-columns:1fr;gap:18px}.bar-row,.comparison-row{grid-template-columns:180px minmax(0,1fr)}.axis-labels{padding-left:200px}.disclosure-grid{grid-template-columns:1fr}}
@media(max-width:680px){html{scroll-padding-top:68px}.mobile-nav-toggle{display:flex;position:sticky;top:0;z-index:30;width:100%;height:58px;border:0;padding:0 18px;background:var(--nav);color:#fff;align-items:center;justify-content:space-between;font-weight:750}.sidebar{display:none;position:fixed;top:58px;width:100%;height:auto;bottom:auto;padding:15px 18px 20px;box-shadow:0 12px 28px rgba(0,0,0,.25)}.sidebar.open{display:block}.sidebar .brand,.sidebar .nav-note{display:none}.sidebar nav{margin:0;grid-template-columns:1fr 1fr}.sidebar nav a{padding:10px}main{margin-left:0}.hero{min-height:auto;padding-top:54px;padding-bottom:64px}.hero,.report-section,footer{padding-left:18px;padding-right:18px}.hero h1{font-size:clamp(2.7rem,14vw,4.2rem)}.question{margin-top:26px}.kpi-grid{grid-template-columns:1fr 1fr;gap:9px}.kpi{padding:16px}.causality-warning{align-items:flex-start;flex-direction:column;gap:5px}.report-section{padding-top:64px;padding-bottom:64px}.chart-card{padding:19px 14px}.chart-intro{display:block}.legend,.comparison-legend{justify-content:flex-start;margin-top:14px}.view-control{margin-top:18px}.axis-labels{padding-left:0;margin-top:26px}.bar-row,.comparison-row{grid-template-columns:1fr;gap:7px;padding:15px 0;min-height:106px}.correlation-track,.comparison-track{width:calc(100% - 18px);margin:0 9px}.comparison-track{height:64px}.finding-grid{grid-template-columns:1fr}.reversal-callout{padding:22px 18px}.disclosure-grid{display:block}.disclosure-grid details{margin-bottom:9px}.definition{grid-template-columns:1fr;gap:4px}.section-heading h2{font-size:2.4rem}.section-heading{margin-bottom:25px}.table-wrap{padding:6px 10px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.correlation-bar,.comparison-dot{transition:none}}
"""

_JS = r"""
(() => {
  const nav = document.getElementById('report-nav');
  const navToggle = document.querySelector('.mobile-nav-toggle');
  navToggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', String(open));
  });
  nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    nav.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
  }));
  const sections = [...document.querySelectorAll('main section[id]')];
  const links = [...nav.querySelectorAll('a')];
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) links.forEach(link => link.classList.toggle('active', link.hash === '#' + entry.target.id));
    });
  }, {rootMargin:'-25% 0px -65% 0px'});
  sections.forEach(section => observer.observe(section));

  const tooltip = document.querySelector('.tooltip');
  const showTooltip = (mark, event) => {
    tooltip.textContent = mark.dataset.tooltip;
    tooltip.hidden = false;
    const rect = mark.getBoundingClientRect();
    const x = event && event.clientX ? event.clientX : rect.left + rect.width / 2;
    const y = event && event.clientY ? event.clientY : rect.top;
    tooltip.style.left = Math.max(8, Math.min(window.innerWidth - tooltip.offsetWidth - 8, x + 12)) + 'px';
    tooltip.style.top = Math.max(8, y - tooltip.offsetHeight - 12) + 'px';
  };
  document.querySelectorAll('.mark').forEach(mark => {
    mark.addEventListener('pointerenter', event => showTooltip(mark, event));
    mark.addEventListener('pointermove', event => showTooltip(mark, event));
    mark.addEventListener('pointerleave', () => tooltip.hidden = true);
    mark.addEventListener('focus', event => showTooltip(mark, event));
    mark.addEventListener('blur', () => tooltip.hidden = true);
  });

  const comparison = document.querySelector('[data-chart="raw-versus-first-difference"]');
  const status = comparison.querySelector('.chart-status');
  const messages = {both:'Showing raw-level and first-difference coefficients.',raw:'Showing raw-level coefficients only.',difference:'Showing first-difference coefficients only.'};
  comparison.querySelectorAll('input[name="coefficient-view"]').forEach(input => input.addEventListener('change', () => {
    if (!input.checked) return;
    comparison.dataset.view = input.value;
    status.textContent = messages[input.value];
  }));
})();
"""
