from __future__ import annotations
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from briefforge.interactive_report_configs import macro_config, norway_config
from briefforge.interactive_report_foundation import CHART_KINDS, render_report, write_report

FIXTURE = Path("/home/mkkto/srv/EIP/projects/InsightForge/artifacts/fixtures/T-035-demographic-growth-correlation-report-input.json")


class ReusableInteractiveFoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_macro_has_required_shape_controls_and_chart_grammar(self) -> None:
        config = macro_config()
        self.assertEqual(7, len(config["divisions"]))
        self.assertTrue(all(len(x["pages"]) == 4 for x in config["divisions"]))
        self.assertEqual(6, len(config["controls"]))
        kinds = {c["kind"] for d in config["divisions"] for p in d["pages"] for c in p.get("charts", [])}
        self.assertEqual(CHART_KINDS, kinds)
        html = render_report(config)
        self.assertIn("illustrative only; not analytical evidence", html)
        self.assertIn("history.pushState", html)
        self.assertIn("mobile-drawer", html)
        self.assertIn("set.delete", html)
        self.assertIn("set.add", html)

    def test_norway_uses_exact_t035_values_and_one_evidence_table(self) -> None:
        config = norway_config(self.data, FIXTURE)
        self.assertLess(len(config["divisions"]), 7)
        self.assertEqual(["theme"], [c["id"] for c in config["controls"]])
        html = render_report(config)
        for value in ("0.3855860099", "-0.207863151096", "-0.083376899169", "31", "33", "34", "1991–2021", "1991–2023", "1991–2024", "wdi_annual_scalar_first_difference_v1", "wdi_annual_scalar_first_difference_pearson_v1"):
            self.assertIn(value, html)
        self.assertEqual(1, html.count('"kind":"evidence-table"'))
        self.assertIn("Correlation ≠ causation", html)
        self.assertIn("Rejected interpretations", html)
        self.assertIn(self.data["content_sha256"], html)

    def test_page_owned_subnavigation_is_bespoke_optional_and_shared(self) -> None:
        macro = macro_config()
        norway = norway_config(self.data, FIXTURE)
        macro_subs = [p.get("subsections") for d in macro["divisions"] for p in d["pages"]]
        norway_subs = [p.get("subsections") for d in norway["divisions"] for p in d["pages"]]
        self.assertIn([{"id": "summary", "label": "Summary"}, {"id": "evidence", "label": "Evidence"}, {"id": "interpretation", "label": "Interpretation"}], macro_subs)
        self.assertTrue(any(x is None or x == [] for x in macro_subs))
        self.assertTrue(any(x and "Exact coefficients" in {s["label"] for s in x} for x in norway_subs))
        self.assertTrue(any(x and "Rejected interpretations" in {s["label"] for s in x} for x in norway_subs))
        html = render_report(norway)
        self.assertIn("pageSubs", html)
        self.assertIn("mobile-subnav", html)
        self.assertNotIn("subs=[['summary'", html)

    def test_macro_controls_have_functional_types_and_ten_point_data(self) -> None:
        config = macro_config()
        self.assertEqual("Nordic Macroeconomic Monitor — Interactive Model Report", config["title"])
        controls = {c["id"]: c for c in config["controls"]}
        self.assertEqual("primary-geography", controls["geography"]["type"])
        self.assertEqual("multi-checkbox", controls["compare"]["type"])
        self.assertEqual({"type": "range", "min": 0, "max": 2, "step": 1}, {k: controls["horizon"][k] for k in ("type", "min", "max", "step")})
        self.assertEqual("segmented", controls["display"]["type"])
        timelines = [c for d in config["divisions"] for p in d["pages"] for c in p.get("charts", []) if c["kind"] == "timeline"]
        self.assertTrue(timelines)
        self.assertTrue(all(len(c["labels"]) == 10 and all(len(s["values"]) == 10 for s in c["data"]) for c in timelines))
        html = render_report(config)
        for contract in ("previousPrimary", "validComparators", "slice(-horizonCount", "indexedValues", "relevantData", "scenario-emphasis", 'type="range"', 'type="checkbox"'):
            self.assertIn(contract, html)

    def test_norway_only_exposes_appearance_and_exact_chart_metadata(self) -> None:
        config = norway_config(self.data, FIXTURE)
        self.assertEqual(["theme"], [c["id"] for c in config["controls"]])
        charts = [c for d in config["divisions"] for p in d["pages"] for c in p.get("charts", [])]
        coefficient = next(c for c in charts if c["kind"] == "coefficient")
        dumbbell = next(c for c in charts if c["kind"] == "dumbbell")
        self.assertTrue(coefficient["selectable"])
        self.assertEqual("Pearson r", coefficient["unit"])
        self.assertEqual("Pearson r", dumbbell["unit"])
        self.assertEqual(["Raw level", "First difference"], dumbbell["series"])
        for point in coefficient["data"]:
            self.assertRegex(point["exact"], r"^-?0\.\d+$")
            self.assertIn("n", point)
            self.assertIn("period", point)
            self.assertIn("transformation", point)
            self.assertIn("method", point)
        for point in dumbbell["data"]:
            self.assertIn("raw_exact", point)
            self.assertIn("difference_exact", point)
        html = render_report(config)
        self.assertIn("zero-line", html)
        self.assertIn("horizontal-coefficient", html)
        self.assertIn("Raw level", html)
        self.assertIn("First difference", html)

    def test_kpi_counts_are_page_variable(self) -> None:
        pages = [p for d in macro_config()["divisions"] for p in d["pages"]]
        counts = [len(p.get("kpis", [])) for p in pages]
        self.assertEqual(6, counts[0])
        self.assertIn(0, counts)
        self.assertTrue(any(0 < count < 6 for count in counts[1:]))

    def test_macro_contributions_are_components_and_kpis_respond_to_geography(self) -> None:
        config = macro_config()
        charts = [c for d in config["divisions"] for p in d["pages"] for c in p.get("charts", [])]
        contribution = next(c for c in charts if c["kind"] == "contribution")
        self.assertEqual(
            ["Consumption", "Investment", "Public demand", "Net trade"],
            [row["name"] for row in contribution["data"]],
        )
        self.assertTrue(contribution["selectable"])
        executive = config["divisions"][0]["pages"][0]
        self.assertTrue(all(set(k["values_by_geography"]) == {"Norway", "Denmark", "Sweden"} for k in executive["kpis"]))
        self.assertIn("values_by_geography", render_report(config))

    def test_mobile_page_transitions_reset_reading_position_and_source_hash_wraps(self) -> None:
        html = render_report(norway_config(self.data, FIXTURE))
        self.assertIn("scrollTarget", html)
        self.assertIn("window.scrollTo(0,0)", html)
        self.assertIn(".source-note{overflow-wrap:anywhere}", html)

    def test_keyboard_focus_is_preserved_after_rerender_and_drawer_close(self) -> None:
        html = render_report(norway_config(self.data, FIXTURE))
        self.assertIn("focusTarget", html)
        self.assertIn("restoreFocus", html)
        self.assertIn("wasOpen", html)
        self.assertIn("menu.focus()", html)

    def test_reader_charts_expose_units_latest_labels_and_endpoint_values(self) -> None:
        html = render_report(macro_config())
        for contract in (
            'class="axis-unit"',
            'class="latest-value-label"',
            'class="endpoint-value"',
            "formatValue",
            "c.unit",
        ):
            self.assertIn(contract, html)
        self.assertIn("a.exact??a.value,color=colors", html)
        self.assertIn(".chart{max-width:100%;overflow-x:auto", html)
        self.assertIn(".chart svg{width:600px", html)

    def test_appearance_toggle_is_icon_only_and_accessibly_labelled(self) -> None:
        html = render_report(macro_config())
        self.assertIn('class="theme-icon"', html)
        self.assertIn('Switch to dark appearance', html)
        self.assertIn('Switch to light appearance', html)
        self.assertNotIn("${value?'Dark':'Light'}</button>", html)

    def test_comparison_geographies_default_to_foldable_multiselect(self) -> None:
        html = render_report(macro_config())
        self.assertIn('class="multi-trigger"', html)
        self.assertIn('class="multi-popover ${open?', html)
        self.assertIn('data-multi-close', html)
        self.assertIn("c.presentation==='inline'", html)
        self.assertIn("multiOpen", html)

    def test_kpi_context_and_breakdown_are_distinct_optional_details(self) -> None:
        config = macro_config()
        config["divisions"][0]["pages"][0]["kpis"][0]["context_detail"] = {
            "title": "Context & explanation",
            "items": ["Definition", "Coverage caveat"],
        }
        config["divisions"][0]["pages"][0]["kpis"][0]["breakdown_detail"] = {
            "title": "Evidence & breakdown",
            "columns": ["Period", "Value"],
            "rows": [["2023", "1.0"], ["2024", "2.0"]],
        }
        html = render_report(config)
        self.assertIn("context_detail", html)
        self.assertIn("breakdown_detail", html)
        self.assertIn("kpiHasDetail", html)
        self.assertIn("Context & explanation", html)
        self.assertIn("Evidence & breakdown", html)
        self.assertIn("kpi-detail-context", html)
        self.assertIn("kpi-detail-breakdown", html)

    def test_real_report_reader_defects_have_bounded_foundation_support(self) -> None:
        html = render_report(macro_config())
        for contract in (
            "horizonControl?.options",
            "state.controls.display!==undefined",
            "state.controls.scenario!==undefined",
            "exact_values",
            "c.value_label||'Latest'",
            "c.other_label||'Earlier'",
            "c.y_decimals??1",
            "labels.forEach((lab,i)",
            "document.addEventListener('focusin'",
        ):
            self.assertIn(contract, html)

    def test_output_is_deterministic_and_self_contained(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = write_report(macro_config(), Path(td) / "index.html")
            html = path.read_text(encoding="utf-8")
            self.assertNotIn("<script src=", html)
            self.assertNotIn("<link rel=\"stylesheet\"", html)
            self.assertEqual(html, render_report(macro_config()))


if __name__ == "__main__":
    unittest.main()
