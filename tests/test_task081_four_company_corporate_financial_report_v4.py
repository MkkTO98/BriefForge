from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from briefforge.task081_four_company_corporate_financial_report_v4 import build_publication
from tools.verify_task081_source_instances import verify_source_instances

def local_path(variable: str) -> Path | None:
    value = os.environ.get(variable)
    return Path(value) if value else None


SOURCE = local_path("BRIEFFORGE_LOCAL_T042_SOURCE")
TASK229_SOURCE = local_path("BRIEFFORGE_LOCAL_TASK229_SOURCE")
T041_SOURCE = local_path("BRIEFFORGE_LOCAL_T041_SOURCE")
LOCAL_PRESENTATIONS = local_path("BRIEFFORGE_LOCAL_PRESENTATIONS_ROOT")
SOURCE_SHA = "d0952e4926f662aa343e5d0acd348b4bfee5f75f2bdced28be25a1ac39074c97"
SOURCE_IDENTITY = "40f045c31297047b3d1085501238100eb3c50411edf1c35f55b2ed9c59fc0722"
HISTORICAL = {
    "TASK-079-four-company-deep-financial-report-v2/index.html": "e971fb1d0db85f4d9a0944be7b2fd850b6dd3f4fb87fdec30f26e86643bf8d56",
    "TASK-080-four-company-financial-usability-report-v3/index.html": "da58c634d5404b99627c577f4fb883d9a364c1077f53b392d27afb272ae62b5d",
    "TASK-080-four-company-financial-usability-report-v3/publication-manifest.json": "1d7937e5e170b9871e88de8d8d1ff478bd0a994448fe5fc015f0ccca1e20c240",
    "TASK-080-four-company-financial-usability-report-v3/final-byte-qa-binding.json": "41ee8e40dcdda76a733572b26dc967ff663f7d51362d4bd22630da400586ae4b",
}
COMPANIES = ("meta", "alphabet", "amazon", "microsoft")
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


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@unittest.skipUnless(
    all(path is not None and path.exists() for path in (SOURCE, TASK229_SOURCE, T041_SOURCE, LOCAL_PRESENTATIONS)),
    "restricted integration fixtures are available only through explicit BRIEFFORGE_LOCAL_* paths",
)
class Task081CorporateFinancialReportV4Tests(unittest.TestCase):
    def test_source_and_historical_releases_are_authenticated(self):
        self.assertEqual(SOURCE_SHA, sha(SOURCE))
        self.assertEqual(SOURCE_IDENTITY, json.loads(SOURCE.read_text())["analysis_identity"])
        self.assertEqual(HISTORICAL, {rel: sha(LOCAL_PRESENTATIONS / rel) for rel in HISTORICAL})

    def test_build_is_deterministic_and_manifest_binds_exact_core_files(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            first = build_publication(SOURCE, Path(a))
            second = build_publication(SOURCE, Path(b))
            self.assertEqual(first, second)
            files_a = {p.name for p in Path(a).iterdir() if p.is_file()}
            files_b = {p.name for p in Path(b).iterdir() if p.is_file()}
            self.assertEqual(files_a, files_b)
            self.assertEqual(files_a, {
                "index.html", "presentation-package.json", "publication-manifest.json", "source-authentication.json",
                "route-navigation-inventory.json", "statement-coverage-matrix.json", "statement-line-rendering-inventory.json",
                "period-transformation-inventory.json", "ratio-statistics-registry.json", "formula-component-resolution.json",
                "graph-table-inventory.json", "strategy-content-audit.json", "unresolved-upstream-return-packet.json",
            })
            for name in files_a:
                self.assertEqual((Path(a) / name).read_bytes(), (Path(b) / name).read_bytes())
            manifest = json.loads((Path(a) / "publication-manifest.json").read_text())
            self.assertEqual("TASK-081", manifest["task_id"])
            self.assertEqual(SOURCE_SHA, manifest["source_sha256"])
            self.assertEqual(SOURCE_IDENTITY, manifest["analysis_identity"])
            self.assertEqual({name: sha(Path(a) / name) for name in manifest["artifacts"]}, {name: row["sha256"] for name, row in manifest["artifacts"].items()})

    def test_route_hierarchy_has_distinct_global_company_and_financial_levels(self):
        with tempfile.TemporaryDirectory() as td:
            build_publication(SOURCE, Path(td))
            inventory = json.loads((Path(td) / "route-navigation-inventory.json").read_text())
            self.assertEqual(ROUTES, [row["route"] for row in inventory["routes"]])
            self.assertEqual(list(GLOBAL_ROUTES) + list(COMPANIES), inventory["global_navigation"])
            self.assertEqual(list(COMPANY_LOCAL), inventory["company_side_navigation"])
            self.assertEqual(list(FINANCIAL_VIEWS), inventory["financials_navigation"])
            self.assertTrue(all(row["direct_url"] == f"#/{row['route']}" and row["content_id"] for row in inventory["routes"]))
            html = (Path(td) / "index.html").read_text()
            for token in ("global-nav", "company-side-nav", "financials-row", "mobile-local-selector", "hashchange", "popstate", "history.pushState"):
                self.assertIn(token, html)

    def test_statement_explorer_has_range_modes_graph_selection_and_one_row_per_line(self):
        with tempfile.TemporaryDirectory() as td:
            build_publication(SOURCE, Path(td))
            inventory = json.loads((Path(td) / "statement-line-rendering-inventory.json").read_text())
            self.assertEqual(99, inventory["statement_line_count"])
            self.assertEqual(99, len({row["line_id"] for row in inventory["lines"]}))
            self.assertTrue(all(row["default_row_count"] == 1 for row in inventory["lines"]))
            counts = inventory["counts_by_company_statement"]
            self.assertEqual(set(COMPANIES), set(counts))
            self.assertTrue(all(all(counts[c][s] > 0 for s in ("income_statement", "balance_sheet", "cash_flow")) for c in COMPANIES))
            html = (Path(td) / "index.html").read_text()
            for token in ("Annual", "Quarterly", "TTM", "range-start", "range-end", "Exact range", "metric-selector", "selected-series", "data-line-id", "View data", "View all periods", "statement-chart", "remove-series"):
                self.assertIn(token, html)
            self.assertIn("<svg", html)
            self.assertIn("renderExplorer", html)
            self.assertIn("selectLine", html)
            self.assertIn("range_summaries", html)

    def test_period_transformations_ratios_and_exact_formula_resolution_are_upstream_owned(self):
        with tempfile.TemporaryDirectory() as td:
            build_publication(SOURCE, Path(td))
            transforms = json.loads((Path(td) / "period-transformation-inventory.json").read_text())
            self.assertEqual(747, transforms["derived_period_result_count"])
            self.assertEqual(5833, transforms["range_summary_count"])
            self.assertTrue({"q4", "ttm", "cumulative_endpoint_difference"} <= set(transforms["kinds"]))
            self.assertTrue(transforms["balance_sheet_stock_sum_prohibited"])
            self.assertTrue(transforms["eps_sum_prohibited"])
            ratios = json.loads((Path(td) / "ratio-statistics-registry.json").read_text())
            self.assertEqual(44, ratios["ratio_count"])
            self.assertEqual(34, ratios["available_count"])
            self.assertTrue(all(row["formula"] and "evidence_status" in row for row in ratios["ratios"]))
            resolution = json.loads((Path(td) / "formula-component-resolution.json").read_text())
            self.assertEqual(0, resolution["unresolved_component_count"])
            self.assertTrue(resolution["no_website_derived_canonical_values"])

    def test_strategy_audit_removes_weak_content_and_preserves_partial_limit(self):
        with tempfile.TemporaryDirectory() as td:
            build_publication(SOURCE, Path(td))
            audit = json.loads((Path(td) / "strategy-content-audit.json").read_text())
            self.assertEqual("PARTIAL", audit["disposition"])
            self.assertEqual(4, audit["boxes_retained"])
            self.assertEqual(4, audit["boxes_rewritten"])
            self.assertGreaterEqual(audit["task080_fragments_removed"], 4)
            self.assertEqual(0, audit["nonsensical_fragments_remaining"])
            html = (Path(td) / "index.html").read_text().lower()
            strategies = json.loads((Path(td) / "strategy-content-audit.json").read_text())
            strategy_text = json.dumps(strategies).lower()
            for label in ("management stated", "financial evidence", "insightforge assessment", "unproven claims and monitoring points"):
                self.assertIn(label, html)
            for broken in ("latest accepted sequential_growth", "[object object]", "none none", "undefined", "null null"):
                self.assertNotIn(broken, strategy_text)
            self.assertIn("q4-cycle", html)
            self.assertIn("generally do not file a separate q4 10-q", html)

    def test_review_remediation_exposes_conflicts_exact_tooltips_and_mode_compatible_selection(self):
        with tempfile.TemporaryDirectory() as td:
            build_publication(SOURCE, Path(td))
            html = (Path(td) / "index.html").read_text()
            for token in (
                "ensureModeSelection", "fmtExact", "const dataRows", "Candidate values", "Evidence references",
                "source statement claim occurrences admitted",
                "Filing statistics reuse the exact per-line observation registries",
                "Not meaningful — zero or negative base",
            ):
                self.assertIn(token, html)
            source = json.loads(SOURCE.read_text())
            for line in source["statement_lines"]:
                for observation in line["observations"]:
                    if observation["mode"] == "Annual" and observation["scope_kind"] == "annual":
                        expected = ("07-01", "06-30") if line["company_key"] == "microsoft" else ("01-01", "12-31")
                        self.assertEqual(expected, (observation["period"]["start"][5:], observation["period"]["end"][5:]))
            self.assertTrue(all(row.get("percentage_change") is None for row in source["range_summaries"] if row.get("start_value") is not None and float(row["start_value"]) <= 0))

    def test_exhaustive_rendered_source_instances_resolve(self):
        package = LOCAL_PRESENTATIONS / "TASK-081-four-company-corporate-financial-report-v4"
        report = verify_source_instances(package / "index.html", SOURCE, TASK229_SOURCE, T041_SOURCE)
        self.assertEqual(7612, report["counts"]["total_rendered_instances"])
        self.assertEqual(1260, report["counts"]["directly_sourced_instances"])
        self.assertEqual(6326, report["counts"]["derived_instances"])
        self.assertEqual(16, report["counts"]["qualified_only_instances"])
        self.assertEqual(11, report["counts"]["conflicting_instances"])
        self.assertEqual(10, report["counts"]["unavailable_instances"])
        self.assertEqual(0, report["counts"]["unresolved_instances"])
        self.assertEqual([], report["unresolved_references"])
        self.assertTrue(all(report["exact_model_bindings"].values()))
        self.assertEqual(0, report["counts"]["independently_rendered_statistics"])
        self.assertEqual(99, report["counts"]["package_only_filing_statistics"])

    def test_accessibility_mobile_overflow_and_internal_only_boundaries_are_explicit(self):
        with tempfile.TemporaryDirectory() as td:
            build_publication(SOURCE, Path(td))
            html = (Path(td) / "index.html").read_text()
            for token in ("Skip to report content", "focus-visible", "prefers-reduced-motion", "@media(max-width:760px)", "overflow-x:auto", "aria-live", "aria-current", "aria-label", "role=\"img\"", "rel=\"icon\" href=\"data:image/svg+xml"):
                self.assertIn(token, html)
            packet = json.loads((Path(td) / "unresolved-upstream-return-packet.json").read_text())
            self.assertFalse(packet["stock_price_capability"]["available"])
            self.assertTrue(packet["strategy"]["strategy_progression_missing"])
            self.assertEqual("internal_local_analysis_only", packet["rights"]["allowed_use"])


if __name__ == "__main__":
    unittest.main()
