"""TASK-077 authority-surface and provenance safeguards.

These tests are source-architecture gates: production must not retain fixture-only
issuers, scopes, dispatch, or sidecar authorities. Capability/Plan values and
persistence receipts remain data; the sole live v2 invocation authority is the
existing native admission handle owned by the native admission module.
"""
from __future__ import annotations

import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


class Task077AuthoritySurfaceRemediationTests(unittest.TestCase):
    def test_named_fixture_authority_surfaces_are_absent_from_production(self):
        forbidden = {
            "_issue_bounded_synthetic_candidate_authority",
            "_issue_fixture_plan_v2_closure_authority",
            "_verify_synthetic_bcrp_publication_subject_fixture",
            "synthetic-test-fixture",
            "CapabilityV2SerializedEvidenceAuthority",
            "PlanV2ClosureAuthority",
            "provision_test_authority",
        }
        hits = {}
        for path in sorted(SRC.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            found = sorted(item for item in forbidden if item in text)
            if found:
                hits[path.relative_to(ROOT).as_posix()] = found
        self.assertEqual(hits, {})

    def test_production_has_no_test_fixture_import_or_fixture_path_dependency(self):
        hits = []
        for path in sorted(SRC.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module and (
                        node.module == "tests" or node.module.startswith("tests.")):
                    hits.append((path.relative_to(ROOT).as_posix(), node.lineno, node.module))
            if "tests/fixtures" in text:
                hits.append((path.relative_to(ROOT).as_posix(), 0, "tests/fixtures"))
        self.assertEqual(hits, [])

    def test_candidate_authoring_production_has_no_test_scope_dispatch(self):
        path = SRC / "briefforge/candidate_authoring.py"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn('scope == "test"', text)
        self.assertNotIn('scope != "test"', text)
        self.assertNotIn('{"test", "governed"}', text)
        self.assertNotIn("test-only", text)
        self.assertNotIn("test-scoped", text)

    def test_candidate_coordinator_has_only_fixed_governed_operations(self):
        path = SRC / "briefforge/candidate_authoring.py"
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(path))
        coordinator = next(
            node for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "CandidateAuthoringCoordinator"
        )
        methods = {
            node.name: node for node in coordinator.body if isinstance(node, ast.FunctionDef)
        }
        self.assertNotIn("author", methods)
        self.assertNotIn("recover", methods)
        self.assertEqual(
            ["self"],
            [argument.arg for argument in methods["__init__"].args.args],
        )
        forbidden_parameters = {"scope", "builder", "validator", "fault"}
        exposed = {}
        for name, method in methods.items():
            parameters = {
                argument.arg
                for argument in (*method.args.posonlyargs, *method.args.args,
                                 *method.args.kwonlyargs)
            }
            found = sorted(parameters & forbidden_parameters)
            if found:
                exposed[name] = found
        self.assertEqual(exposed, {})
        dynamic_lookups = []
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "getattr"):
                continue
            if not node.args or not isinstance(node.args[0], ast.Name) or node.args[0].id != "os":
                dynamic_lookups.append(node.lineno)
        self.assertEqual(dynamic_lookups, [])
        self.assertNotIn("globals()", text)
        self.assertNotIn("os.getenv", text)
        self.assertNotIn("os.environ", text)

    def test_task070_recovery_coverage_no_longer_issues_or_injects_authority(self):
        path = ROOT / "tests/test_task070_candidate_authoring_recovery.py"
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(path))
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }
        self.assertNotIn("provision_test_authority", imported)
        forbidden_calls = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"author", "recover"}:
                forbidden_calls.append((node.lineno, node.func.attr))
        self.assertEqual(forbidden_calls, [])

    def test_no_executable_test_owned_candidate_authority_equivalent(self):
        """Reject semantic equivalents, while ignoring inert text and this absence gate."""
        protocol_formats = {
            "briefforge-candidate-authority-v1",
            "briefforge-candidate-authoring-receipt-v1",
            "briefforge-candidate-validation-evidence-v1",
            "briefforge-candidate-attempt-state-v1",
        }
        governed_roots = {
            "GOVERNED_AUTHORITY_ROOT", "GOVERNED_LEDGER_ROOT", "GOVERNED_OUTPUT_ROOT",
            "_NATIVE_AUTHORITY_ROOT",
        }
        closure_fields = {
            "candidate_authority_bytes", "candidate_authority_sha256", "authority_digest",
            "authoring_receipt_bytes", "receipt_sha256", "validation_evidence_bytes",
            "validation_evidence_sha256", "terminal_state_bytes", "terminal_seal_bytes",
            "terminal_state_sha256", "terminal_seal_sha256",
        }
        findings = []
        candidates = [
            path for path in sorted((ROOT / "tests").rglob("*.py"))
            if path != Path(__file__).resolve()
        ]
        candidates.extend(
            path for path in sorted((ROOT / "tools").rglob("*.py"))
            if path.name != "task071_candidate_operation.py"
        )
        for path in candidates:
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
            relative = path.relative_to(ROOT).as_posix()
            parents = {}
            for parent in ast.walk(tree):
                for child in ast.iter_child_nodes(parent):
                    parents[child] = parent
            candidate_context = any(
                isinstance(item, ast.Constant) and item.value in protocol_formats
                for item in ast.walk(tree)
            ) or any(
                isinstance(item, ast.Call)
                and ((isinstance(item.func, ast.Name) and item.func.id == "GovernedCandidateAdmission")
                     or (isinstance(item.func, ast.Attribute)
                         and item.func.attr == "GovernedCandidateAdmission"))
                for item in ast.walk(tree)
            )
            for node in ast.walk(tree):
                if isinstance(node, ast.Dict):
                    literal_values = {
                        value.value for value in node.values
                        if isinstance(value, ast.Constant) and isinstance(value.value, str)
                    }
                    if literal_values & protocol_formats:
                        findings.append((relative, node.lineno, "manual Candidate protocol document"))
                if not isinstance(node, ast.Call):
                    continue
                name = (node.func.id if isinstance(node.func, ast.Name)
                        else node.func.attr if isinstance(node.func, ast.Attribute) else None)
                if name == "GovernedCandidateAdmission":
                    findings.append((relative, node.lineno, "direct governed admission construction"))
                if name == "replace" and set(keyword.arg for keyword in node.keywords if keyword.arg) & closure_fields:
                    findings.append((relative, node.lineno, "Candidate authority-chain reclosure"))
                if name in {"getattr", "setattr"}:
                    literals = {
                        argument.value for argument in node.args
                        if isinstance(argument, ast.Constant) and isinstance(argument.value, str)
                    }
                    if literals & governed_roots:
                        findings.append((relative, node.lineno, "dynamic governed-root access"))
                if name == "object" and isinstance(node.func, ast.Attribute) and node.func.attr == "object":
                    literal_args = {
                        argument.value for argument in node.args
                        if isinstance(argument, ast.Constant) and isinstance(argument.value, str)
                    }
                    if literal_args & governed_roots:
                        findings.append((relative, node.lineno, "governed-root patch"))
                if name == "write_bytes" and node.args and candidate_context:
                    argument_names = {
                        child.id for child in ast.walk(node.args[0]) if isinstance(child, ast.Name)
                    }
                    if argument_names & {"authority_bytes", "receipt_bytes", "evidence_bytes", "terminal_bytes"}:
                        findings.append((relative, node.lineno, "Candidate authority-chain installation"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                    continue
                if node.func.attr != "object" or not isinstance(node.func.value, ast.Name) or node.func.value.id != "patch":
                    continue
                literal_args = {
                    argument.value for argument in node.args
                    if isinstance(argument, ast.Constant) and isinstance(argument.value, str)
                }
                if literal_args & governed_roots:
                    findings.append((relative, node.lineno, "governed-root replacement"))
        self.assertEqual(findings, [])

    def test_only_existing_native_handle_is_live_task077_invocation_authority(self):
        native = (SRC / "briefforge/bcrp_paired_terminal_admission.py").read_text(
            encoding="utf-8")
        self.assertIn("class NativeBCRPPairedTerminalAdmissionHandle", native)
        self.assertIn("_native_invocation_states", native)
        self.assertIn("issue_native_bcrp_paired_terminal_admission_v2", native)
        for path in sorted((SRC / "briefforge").rglob("*.py")):
            if path.name == "bcrp_paired_terminal_admission.py":
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("NativeBCRPPairedTerminalAdmissionHandle", text,
                             path.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    unittest.main()
