"""Tests for concrete renderer-adapter contract declarations.

These tests cover only renderer-adapter identity, capability declarations,
contract shape, and compatibility checking against a Ready Presentation Package.
They must not require actual rendering, HTML, PDF, browser behavior, templates,
visualization, charts, maps, exports, persistence, APIs, networking, portal
behavior, dashboard behavior, search, or UI components.
"""

from copy import deepcopy
from dataclasses import FrozenInstanceError, fields, is_dataclass
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
TESTS = PROJECT_ROOT / "tests"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(TESTS))

from test_renderer_adapter_boundary import ready_package  # noqa: E402


class RendererAdapterContractTests(unittest.TestCase):
    def test_well_formed_renderer_adapter_contract_can_be_created(self):
        from briefforge.renderer_adapter import (
            RendererAdapterCapability,
            RendererAdapterContract,
            RendererAdapterIdentity,
        )

        identity = RendererAdapterIdentity(
            adapter_id="static-html-adapter",
            name="Static HTML Adapter",
            version="0.1.0",
            owner="BriefForge renderer boundary tests",
        )
        capability = RendererAdapterCapability(
            capability_id="linear-statement-flow",
            description="Can consume ordered presentation statements.",
            package_features=("statements", "organizing_purpose"),
        )
        contract = RendererAdapterContract(identity=identity, capabilities=(capability,))

        self.assertEqual(contract.identity, identity)
        self.assertEqual(contract.capabilities, (capability,))
        self.assertTrue(is_dataclass(RendererAdapterIdentity))
        self.assertTrue(is_dataclass(RendererAdapterCapability))
        self.assertTrue(is_dataclass(RendererAdapterContract))

    def test_renderer_adapter_contract_requires_stable_adapter_identity(self):
        from briefforge.renderer_adapter import (
            RendererAdapterCapability,
            RendererAdapterContract,
            RendererAdapterContractRejected,
            RendererAdapterIdentity,
        )

        capability = RendererAdapterCapability(
            capability_id="statement-flow",
            description="Can consume statements.",
            package_features=("statements",),
        )

        with self.assertRaises(RendererAdapterContractRejected):
            RendererAdapterContract(identity=None, capabilities=(capability,))
        with self.assertRaises(RendererAdapterContractRejected):
            RendererAdapterIdentity(adapter_id="", name="Adapter", version="0.1.0", owner="tests")
        with self.assertRaises(RendererAdapterContractRejected):
            RendererAdapterIdentity(adapter_id="adapter", name="", version="0.1.0", owner="tests")
        with self.assertRaises(RendererAdapterContractRejected):
            RendererAdapterIdentity(adapter_id="adapter", name="Adapter", version="", owner="tests")

    def test_capabilities_are_declarative_only_and_do_not_render(self):
        from briefforge.renderer_adapter import RendererAdapterCapability

        capability = RendererAdapterCapability(
            capability_id="semantic-outline",
            description="Can consume package identity and statements for an outline-shaped adapter.",
            package_features=("identity", "statements"),
        )

        forbidden_terms = {
            "html",
            "pdf",
            "browser",
            "template",
            "visualization",
            "visualisation",
            "chart",
            "map",
            "export",
            "persistence",
            "database",
            "api",
            "network",
            "portal",
            "dashboard",
            "search",
            "ui",
            "component",
            "output",
            "artifact",
            "document",
            "rendered",
            "content",
        }
        field_names = {field.name.lower() for field in fields(RendererAdapterCapability)}
        for forbidden in forbidden_terms:
            self.assertFalse(
                any(forbidden in field_name for field_name in field_names),
                f"RendererAdapterCapability leaks excluded output assumption {forbidden!r}",
            )
        for forbidden_attribute in ("render", "rendered_output", "html", "pdf", "template", "export"):
            self.assertFalse(hasattr(capability, forbidden_attribute))

        with self.assertRaises(FrozenInstanceError):
            capability.package_features = ()

    def test_ready_presentation_package_can_be_checked_against_contract(self):
        from briefforge.renderer_adapter import (
            RendererAdapterCapability,
            RendererAdapterContract,
            RendererAdapterIdentity,
            check_renderer_adapter_compatibility,
        )

        ready = ready_package()
        contract = RendererAdapterContract(
            identity=RendererAdapterIdentity(
                adapter_id="semantic-outline-adapter",
                name="Semantic Outline Adapter",
                version="0.1.0",
                owner="BriefForge renderer boundary tests",
            ),
            capabilities=(
                RendererAdapterCapability(
                    capability_id="semantic-outline",
                    description="Can consume identity, organizing purpose, statements, references, obligations, and validation metadata.",
                    package_features=(
                        "identity",
                        "organizing_purpose",
                        "statements",
                        "upstream_references",
                        "obligations",
                        "validation_judgment",
                        "semantic_fingerprint",
                        "validation_policy_id",
                    ),
                ),
            ),
        )

        compatibility = check_renderer_adapter_compatibility(ready, contract)

        self.assertTrue(compatibility.compatible)
        self.assertEqual(compatibility.ready_package, ready)
        self.assertEqual(compatibility.contract, contract)
        self.assertEqual(compatibility.missing_package_features, ())

    def test_malformed_identity_or_capability_declarations_are_rejected(self):
        from briefforge.renderer_adapter import (
            RendererAdapterCapability,
            RendererAdapterContract,
            RendererAdapterContractRejected,
            RendererAdapterIdentity,
        )

        identity = RendererAdapterIdentity(
            adapter_id="adapter",
            name="Adapter",
            version="0.1.0",
            owner="tests",
        )

        with self.assertRaises(RendererAdapterContractRejected):
            RendererAdapterCapability(capability_id="", description="Can consume statements.", package_features=("statements",))
        with self.assertRaises(RendererAdapterContractRejected):
            RendererAdapterCapability(capability_id="statements", description="", package_features=("statements",))
        with self.assertRaises(RendererAdapterContractRejected):
            RendererAdapterCapability(capability_id="statements", description="Can consume statements.", package_features=("",))
        with self.assertRaises(RendererAdapterContractRejected):
            RendererAdapterCapability(capability_id="statements", description="Can consume statements.", package_features="statements")
        with self.assertRaises(RendererAdapterContractRejected):
            RendererAdapterContract(identity=identity, capabilities=())
        with self.assertRaises(RendererAdapterContractRejected):
            RendererAdapterContract(identity=identity, capabilities=("not-a-capability",))

    def test_compatibility_check_does_not_mutate_ready_package(self):
        from briefforge.renderer_adapter import (
            RendererAdapterCapability,
            RendererAdapterContract,
            RendererAdapterIdentity,
            check_renderer_adapter_compatibility,
        )

        ready = ready_package()
        before = deepcopy(ready)
        contract = RendererAdapterContract(
            identity=RendererAdapterIdentity(
                adapter_id="minimal-adapter",
                name="Minimal Adapter",
                version="0.1.0",
                owner="tests",
            ),
            capabilities=(
                RendererAdapterCapability(
                    capability_id="statements",
                    description="Can consume statements.",
                    package_features=("statements",),
                ),
            ),
        )

        check_renderer_adapter_compatibility(ready, contract)

        self.assertEqual(ready, before)

    def test_contract_compatibility_check_does_not_create_rendered_output(self):
        from briefforge.renderer_adapter import (
            RendererAdapterCapability,
            RendererAdapterCompatibility,
            RendererAdapterContract,
            RendererAdapterIdentity,
            check_renderer_adapter_compatibility,
        )

        contract = RendererAdapterContract(
            identity=RendererAdapterIdentity(
                adapter_id="minimal-adapter",
                name="Minimal Adapter",
                version="0.1.0",
                owner="tests",
            ),
            capabilities=(
                RendererAdapterCapability(
                    capability_id="statements",
                    description="Can consume statements.",
                    package_features=("statements",),
                ),
            ),
        )
        compatibility = check_renderer_adapter_compatibility(ready_package(), contract)

        self.assertIsInstance(compatibility, RendererAdapterCompatibility)
        forbidden_terms = {
            "html",
            "pdf",
            "browser",
            "template",
            "visualization",
            "visualisation",
            "chart",
            "map",
            "export",
            "persistence",
            "database",
            "api",
            "network",
            "portal",
            "dashboard",
            "search",
            "ui",
            "component",
            "output",
            "artifact",
            "document",
            "rendered",
            "content",
        }
        exposed_names = {field.name.lower() for field in fields(RendererAdapterCompatibility)}
        for forbidden in forbidden_terms:
            self.assertFalse(
                any(forbidden in exposed_name for exposed_name in exposed_names),
                f"RendererAdapterCompatibility leaks excluded output assumption {forbidden!r}",
            )
        for forbidden_attribute in ("render", "rendered_output", "html", "pdf", "template", "export"):
            self.assertFalse(hasattr(compatibility, forbidden_attribute))


if __name__ == "__main__":
    unittest.main()
