from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "render_interactive_report.py"
sys.path.insert(0, str(ROOT / "src"))

from briefforge.interactive_report_foundation import render_report


def minimal_config() -> dict[str, object]:
    return {
        "id": "cli-proof",
        "title": "CLI proof",
        "warning": "Local deterministic proof.",
        "controls": [],
        "divisions": [
            {
                "id": "overview",
                "label": "Overview",
                "pages": [
                    {
                        "id": "summary",
                        "label": "Summary",
                        "headline": "Structured configuration renders directly.",
                    }
                ],
            }
        ],
    }


class InteractiveReportCliTests(unittest.TestCase):
    def run_tool(self, *args: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(TOOL), *(str(arg) for arg in args)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            env={"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def test_renders_config_to_explicit_output_without_changing_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "input" / "report.json"
            output_path = root / "nested" / "report" / "index.html"
            config_path.parent.mkdir()
            config = minimal_config()
            source_bytes = json.dumps(config, ensure_ascii=False, indent=2).encode("utf-8")
            config_path.write_bytes(source_bytes)

            result = self.run_tool("--config", config_path, "--output", output_path)

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(source_bytes, config_path.read_bytes())
            self.assertEqual(render_report(config), output_path.read_text(encoding="utf-8"))
            self.assertEqual(f"{output_path}\n", result.stdout)
            self.assertNotIn("Traceback", result.stderr)

    def test_rejects_missing_configuration_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_tool(
                "--config",
                Path(directory) / "missing.json",
                "--output",
                Path(directory) / "index.html",
            )

            self.assertNotEqual(0, result.returncode)
            self.assertIn("unable to read configuration", result.stderr.lower())
            self.assertNotIn("Traceback", result.stderr)

    def test_rejects_malformed_json_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "malformed.json"
            config_path.write_text('{"title":', encoding="utf-8")

            result = self.run_tool("--config", config_path, "--output", root / "index.html")

            self.assertNotEqual(0, result.returncode)
            self.assertIn("invalid json configuration", result.stderr.lower())
            self.assertNotIn("Traceback", result.stderr)

    def test_rejects_non_object_and_invalid_report_configuration_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "report.json"
            output_path = root / "index.html"
            config_path.write_text("[]", encoding="utf-8")
            non_object = self.run_tool("--config", config_path, "--output", output_path)
            self.assertNotEqual(0, non_object.returncode)
            self.assertIn("configuration must be a json object", non_object.stderr.lower())
            self.assertFalse(output_path.exists())

            config_path.write_text('{"title":"Incomplete"}', encoding="utf-8")
            invalid = self.run_tool("--config", config_path, "--output", output_path)
            self.assertNotEqual(0, invalid.returncode)
            self.assertIn("invalid interactive-report configuration", invalid.stderr.lower())
            self.assertFalse(output_path.exists())
            self.assertNotIn("Traceback", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
