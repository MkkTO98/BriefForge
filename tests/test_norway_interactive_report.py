"""Focused checks for the T-035 bounded interactive report vertical slice."""

from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
INPUT = PROJECT_ROOT.parent / "InsightForge" / "artifacts" / "fixtures" / "T-035-demographic-growth-correlation-report-input.json"
sys.path.insert(0, str(SRC))

from briefforge.norway_interactive_report import (  # noqa: E402
    REPORT_FILENAME,
    render_t035_file,
    render_t035_interactive_report,
)


class _StructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))


class NorwayInteractiveReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(INPUT.read_text(encoding="utf-8"))
        cls.html = render_t035_interactive_report(cls.data, INPUT)
        cls.parser = _StructureParser()
        cls.parser.feed(cls.html)

    def test_annual_change_chart_preserves_upstream_coefficients_samples_periods_and_tooltips(self):
        self.assertIn('data-chart="annual-change-correlation"', self.html)
        for row in self.data["selected_correlates"]:
            signed = str(row["coefficient"])
            if not signed.startswith("-"):
                signed = "+" + signed
            tooltip = (
                f"r = {signed} · n = {row['aligned_observation_count']} · "
                f"period {row['aligned_period_start']}–{row['aligned_period_end']} · "
                "First difference (annual change)"
            )
            self.assertIn(tooltip, self.html)
        annual_chart = self.html.split('data-chart="annual-change-correlation"', 1)[1].split("</article>", 1)[0]
        self.assertEqual(3, annual_chart.count("correlation-bar mark"))
        self.assertIn("zero-line", annual_chart)

    def test_raw_difference_control_has_three_finite_states_and_changes_chart_visibility(self):
        self.assertIn('data-chart="raw-versus-first-difference" data-view="both"', self.html)
        for state in ("both", "raw", "difference"):
            self.assertIn(f'value="{state}"', self.html)
        self.assertIn('comparison.dataset.view = input.value', self.html)
        self.assertIn('.comparison-card[data-view="raw"] .difference-dot', self.html)
        self.assertIn('.comparison-card[data-view="difference"] .raw-dot', self.html)
        self.assertIn('comparison-card[data-view="raw"] .connector', self.html)
        for row in self.data["raw_level_context_not_primary"]:
            signed = str(row["coefficient"])
            if not signed.startswith("-"):
                signed = "+" + signed
            self.assertIn(f"r = {signed}", self.html)

    def test_one_evidence_table_and_prominent_causality_warning_are_preserved(self):
        tables = [attrs for tag, attrs in self.parser.tags if tag == "table"]
        self.assertEqual([{"data-evidence-table": "selected-first-difference"}], tables)
        self.assertEqual(1, self.html.count("<table"))
        self.assertIn('class="causality-warning" role="note"', self.html)
        self.assertIn("Correlation ≠ causation.", self.html)
        self.assertIn(self.data["methodology"]["correlation_vs_causation"], self.html)

    def test_navigation_disclosures_and_responsive_mobile_structure_exist(self):
        hrefs = {attrs.get("href") for tag, attrs in self.parser.tags if tag == "a"}
        self.assertTrue({"#overview", "#annual-change", "#comparison", "#methodology", "#sources"} <= hrefs)
        self.assertIn('class="sidebar" id="report-nav"', self.html)
        self.assertIn('class="mobile-nav-toggle"', self.html)
        self.assertIn("position:fixed", self.html)
        self.assertIn("@media(max-width:680px)", self.html)
        self.assertEqual(6, sum(tag == "details" for tag, _attrs in self.parser.tags))
        self.assertIn("nav.classList.toggle('open')", self.html)

    def test_output_is_self_contained_deterministic_and_report_specific(self):
        self.assertEqual(self.html, render_t035_interactive_report(self.data, INPUT))
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("localStorage", self.html)
        self.assertNotIn("<canvas", self.html)
        with tempfile.TemporaryDirectory() as directory:
            report = render_t035_file(INPUT, directory)
            self.assertEqual(REPORT_FILENAME, report.name)
            self.assertEqual(self.html, report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
