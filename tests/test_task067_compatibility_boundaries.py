"""TASK-067 RED contract: compatibility, import, leakage, and closure boundaries."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import unittest

from briefforge.bcrp.model import RECORD_KINDS
from tests import paired_terminal_fixture as fixture


ROOT = Path(__file__).resolve().parents[1]
PAIRED_PACKAGE = ROOT / "src" / "briefforge_paired_terminal_profile"

EXPECTED_ELEVEN_KINDS = (
    "PresentationBriefRecord",
    "PortablePresentationMaterialRecord",
    "CandidatePresentationPackageRecord",
    "ValidationJudgmentRecord",
    "ReadyPresentationPackageRecord",
    "PublicationReleaseRecord",
    "RendererCapabilityDeclarationRecord",
    "RendererCompatibilityPlanRecord",
    "GeneratedArtifactAuditRecord",
    "SemanticArtifactConformanceRecord",
    "PublicationManifestRecord",
)

# Byte fingerprints captured before TASK-067 production implementation.  The
# selector is deliberately excluded because its one additive branch is the only
# historical package file authorized to change.
TASK062_PRESERVATION = {
    "src/briefforge_terminal_profile/profile.py": "01e5c2593b17affa15d82759794e0fd8ec697b76dbe3d4cd157e0774d613f855",
    "src/briefforge_terminal_profile/projection.py": "8fb8a09b75fe42a86daa9bf0ee6d555ca42f89b63116e6e685348504e819a53d",
    "src/briefforge_terminal_profile/renderer_adapter.py": "0f20ce073d166509a909c22b4077adce973ec097780bdc1175c389086ca58cfc",
    "src/briefforge_terminal_profile/controlled_invocation.py": "b32e00dfb89a1b601fb10beadb8b556c7476725cf191fbbf7137042c35d9de22",
    "src/briefforge_terminal_profile/semantic_conformance.py": "e2dcf8047398ceaf5a8088b849a6e7cb8c1556c7cc59f42bcecef9025d8b8467",
    "src/briefforge/publication_distribution_delivery.py": "b75bbf3bd0c219595a9f93c4cc0409dd7e1665a8425a62ce80293affe355d5b3",
}

CAP_COVERAGE = {
    "CAP-001": "76-statement exact frontier and 77 rejection",
    "CAP-002": "32-child exact frontier and 33 rejection",
    "CAP-003": "typed provenance and obligation section children",
    "CAP-004": "27 qualification-edge frontier and 28 rejection",
    "CAP-005": "one-to-many qualification topology and four-target rejection",
    "CAP-006": "closed ordered statement/value/table target domain",
    "CAP-007": "five closed obligation kinds",
    "CAP-008": "82 obligation-target frontier and 83 rejection",
    "CAP-009": "92 provenance targets/two packages and N+1 rejection",
    "CAP-010": "explicit present state, lexical decimal, and metadata",
    "CAP-011": "relationship-owned five-column paired row closure",
    "CAP-012": "one rendered row per relationship",
    "CAP-013": "row-adjacent qualifications/provenance/classification/role",
    "CAP-014": "exact complete version tuple and historical rejection",
}


class Task067CompatibilityBoundaryTests(unittest.TestCase):
    def test_cap001_through_cap014_have_explicit_focused_proof_inventory(self):
        self.assertEqual(tuple(CAP_COVERAGE),
                         tuple(f"CAP-{index:03d}" for index in range(1, 15)))
        corpus = "\n".join((ROOT / "tests" / name).read_text("utf-8") for name in (
            "test_task067_schema_projection.py",
            "test_task067_renderer_invocation.py",
            "test_task067_conformance_manifest.py",
            "test_task067_compatibility_boundaries.py",
        ))
        for capability, proof in CAP_COVERAGE.items():
            with self.subTest(capability=capability):
                self.assertIn(capability, corpus)
                self.assertTrue(proof)

    def test_bcrp_core_remains_exactly_eleven_hand_authored_kinds(self):
        self.assertEqual(RECORD_KINDS, EXPECTED_ELEVEN_KINDS)
        self.assertEqual(len(RECORD_KINDS), 11)
        self.assertEqual(len(set(RECORD_KINDS)), 11)

    def test_bcrp_never_imports_paired_package(self):
        for path in sorted((ROOT / "src" / "briefforge" / "bcrp").glob("*.py")):
            source = path.read_text("utf-8")
            with self.subTest(path=path.name):
                self.assertNotIn("briefforge_paired_terminal_profile", source)
                self.assertNotIn("paired_terminal", source)

    def test_schema_imports_neither_bcrp_verifiers_nor_renderer(self):
        path = PAIRED_PACKAGE / "schema.py"
        tree = ast.parse(path.read_text("utf-8"), filename=str(path))
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        for name in imported:
            with self.subTest(name=name):
                self.assertNotIn("briefforge.bcrp", name)
                self.assertNotIn("renderer", name)
                self.assertNotIn("publication_release", name)

    def test_projection_imports_no_renderer_and_renderer_imports_dtos_only(self):
        projection_source = (PAIRED_PACKAGE / "projection.py").read_text("utf-8")
        renderer_path = PAIRED_PACKAGE / "renderer.py"
        renderer_tree = ast.parse(renderer_path.read_text("utf-8"), filename=str(renderer_path))
        self.assertNotIn("renderer", "\n".join(
            line for line in projection_source.splitlines() if line.lstrip().startswith(("import ", "from "))))
        for node in ast.walk(renderer_tree):
            if isinstance(node, ast.ImportFrom) and node.level == 1:
                self.assertEqual(node.module, "schema")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertFalse(alias.name.startswith("briefforge."))

    def test_new_production_has_no_pilot_domain_or_governance_identity_leakage(self):
        forbidden = (
            "InsightForge", "insightforge", "T-039", "TASK-064", "TASK-065",
            "produce_publication_release",
        )
        for path in sorted(PAIRED_PACKAGE.glob("*.py")):
            source = path.read_text("utf-8")
            for token in forbidden:
                with self.subTest(path=path.name, token=token):
                    self.assertNotIn(token, source)

    def test_fixture_is_source_neutral_and_creates_no_governed_chain(self):
        path = ROOT / "tests" / "paired_terminal_fixture.py"
        source = path.read_text("utf-8").split("\ndef task064_topology_semantics", 1)[0]
        for token in ("InsightForge", "insightforge", "T-039", "TASK-064", "TASK-065",
                      "candidate_bundle", "representative_chain", "produce_publication_release"):
            self.assertNotIn(token, source)
        semantic = fixture.complete_semantics()
        self.assertEqual(len(semantic.table.rows), 7)
        self.assertEqual(len(semantic.values), 14)
        self.assertTrue(all("synthetic" in row.identity for row in semantic.table.rows))

    def test_task062_implementation_bytes_are_preserved(self):
        for relative, expected in TASK062_PRESERVATION.items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            with self.subTest(path=relative):
                self.assertEqual(actual, expected)

    def test_task062_delivery_source_closure_constant_remains_truthful(self):
        selector = (ROOT / "src" / "briefforge_terminal_profile" /
                    "manifest_admission.py").read_text("utf-8")
        digest = hashlib.sha256((ROOT / "src" / "briefforge" /
                                 "publication_distribution_delivery.py").read_bytes()).hexdigest()
        self.assertIn(f'_ACTIVE_DELIVERY_DIGEST = "{digest}"', selector)
        self.assertEqual(digest, TASK062_PRESERVATION[
            "src/briefforge/publication_distribution_delivery.py"])

    def test_historical_selector_literals_and_verifier_routes_survive_additive_branch(self):
        source = (ROOT / "src" / "briefforge_terminal_profile" /
                  "manifest_admission.py").read_text("utf-8")
        required = (
            "briefforge:terminal-publication-manifest-admission-authority:2.0.0",
            "briefforge:representative-terminal-static-html-profile:2.0.0",
            "verify_persisted_terminal_publication_manifest",
            "historical.verify_persisted_publication_manifest",
            "_ARCHIVE_MANIFEST_DIGEST",
            "_ACTIVE_DELIVERY_DIGEST",
        )
        for literal in required:
            with self.subTest(literal=literal):
                self.assertIn(literal, source)

    def test_no_registry_plugin_dynamic_import_range_alias_or_environment_dispatch(self):
        sources = "\n".join(path.read_text("utf-8") for path in sorted(PAIRED_PACKAGE.glob("*.py")))
        forbidden = ("importlib", "entry_points", "pkg_resources", "__import__(", "eval(",
                     "exec(", "os.environ", "semver", "compatible_major", "latest",
                     "plugin", "registry", "fallback")
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, sources)


if __name__ == "__main__":
    unittest.main()
