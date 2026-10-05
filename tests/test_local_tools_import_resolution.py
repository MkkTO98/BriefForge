"""The repository's tools package must win over an installed namesake."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class LocalToolsImportResolutionTests(unittest.TestCase):
    def test_repository_tools_and_task071_module_win_over_competing_package(self):
        with tempfile.TemporaryDirectory() as temporary:
            competitor = Path(temporary) / "tools"
            competitor.mkdir()
            (competitor / "__init__.py").write_text("ORIGIN = 'competing package'\n")
            (competitor / "task071_candidate_operation.py").write_text(
                "ORIGIN = 'competing module'\n"
            )
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join(
                (str(ROOT), str(ROOT / "src"), temporary)
            )
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env["PYTHONNOUSERSITE"] = "1"
            probe = subprocess.run(
                (
                    sys.executable,
                    "-c",
                    "import json, tools\n"
                    "from tools import task071_candidate_operation as operation\n"
                    "print(json.dumps({'package': tools.__file__, "
                    "'module': operation.__file__}))\n",
                ),
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, probe.returncode, probe.stdout + probe.stderr)
            resolved = json.loads(probe.stdout)
            self.assertEqual(str(ROOT / "tools" / "__init__.py"), resolved["package"])
            self.assertEqual(
                str(ROOT / "tools" / "task071_candidate_operation.py"),
                resolved["module"],
            )


if __name__ == "__main__":
    unittest.main()
