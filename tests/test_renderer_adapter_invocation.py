"""Tests for renderer-adapter invocation protocol without rendering.

These tests cover only invocation metadata and rejection behavior. They must not
require actual rendering, HTML, PDF, browser behavior, templates, visualization,
charts, maps, exports, persistence, APIs, networking, portal behavior, dashboard
behavior, search, or UI components.
"""

from copy import deepcopy
from dataclasses import fields, is_dataclass
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
TESTS = PROJECT_ROOT / "tests"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(TESTS))

from test_renderer_adapter_boundary import ready_package  # noqa: E402


def compatible_contract():
    from briefforge.renderer_adapter import (
        RendererAdapterCapability,
        RendererAdapterContract,
        RendererAdapterIdentity,
    )

    return RendererAdapterContract(
        identity=RendererAdapterIdentity(
            adapter_id="metadata-only-adapter",
            name="Metadata Only Adapter",
            version="0.1.0",
            owner="BriefForge renderer invocation tests",
        ),
        capabilities=(
            RendererAdapterCapability(
                capability_id="metadata-invocation",
                description="Can receive package identity and readiness audit metadata.",
                package_features=(
                    "identity",
                    "semantic_fingerprint",
                    "validation_policy_id",
                ),
            ),
        ),
    )


class RendererAdapterInvocationTests(unittest.TestCase):
    def test_compatible_adapter_contract_can_be_invoked(self):
        from briefforge.renderer_adapter import (
            RendererAdapterInvocation,
            RendererAdapterInvocationResult,
            invoke_renderer_adapter,
        )

        ready = ready_package()
        contract = compatible_contract()

        result = invoke_renderer_adapter(ready, contract)

        self.assertIsInstance(result.invocation, RendererAdapterInvocation)
        self.assertIsInstance(result, RendererAdapterInvocationResult)
        self.assertEqual(result.invocation.ready_package, ready)
        self.assertEqual(result.invocation.contract, contract)
        self.assertTrue(result.invocation.compatibility.compatible)
        self.assertTrue(result.accepted)

    def test_incompatible_adapter_contract_is_rejected(self):
        from briefforge.renderer_adapter import (
            RendererAdapterCapability,
            RendererAdapterContract,
            RendererAdapterIdentity,
            RendererAdapterInvocationRejected,
            invoke_renderer_adapter,
        )

        incompatible_contract = RendererAdapterContract(
            identity=RendererAdapterIdentity(
                adapter_id="unsupported-adapter",
                name="Unsupported Adapter",
                version="0.1.0",
                owner="BriefForge renderer invocation tests",
            ),
            capabilities=(
                RendererAdapterCapability(
                    capability_id="unsupported-feature",
                    description="Declares a package feature that the Ready request boundary does not expose.",
                    package_features=("unsupported_feature",),
                ),
            ),
        )

        with self.assertRaises(RendererAdapterInvocationRejected):
            invoke_renderer_adapter(ready_package(), incompatible_contract)

    def test_invocation_result_records_adapter_and_package_metadata(self):
        from briefforge.renderer_adapter import invoke_renderer_adapter

        ready = ready_package()
        contract = compatible_contract()

        result = invoke_renderer_adapter(ready, contract)

        self.assertEqual(result.adapter_identity, contract.identity)
        self.assertEqual(result.package_identity, ready.candidate.identity)
        self.assertEqual(result.semantic_fingerprint, ready.semantic_fingerprint)
        self.assertEqual(result.validation_policy_id, ready.validation_policy_id)

    def test_invocation_does_not_mutate_ready_package(self):
        from briefforge.renderer_adapter import invoke_renderer_adapter

        ready = ready_package()
        before = deepcopy(ready)

        invoke_renderer_adapter(ready, compatible_contract())

        self.assertEqual(ready, before)

    def test_invocation_does_not_create_rendered_output(self):
        from briefforge.renderer_adapter import RendererAdapterInvocationResult, invoke_renderer_adapter

        result = invoke_renderer_adapter(ready_package(), compatible_contract())

        self.assertTrue(is_dataclass(RendererAdapterInvocationResult))
        forbidden_exact_names = {
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
        exposed_names = {field.name.lower() for field in fields(RendererAdapterInvocationResult)}
        self.assertTrue(exposed_names.isdisjoint(forbidden_exact_names))
        for forbidden_attribute in ("render", "rendered_output", "html", "pdf", "template", "export"):
            self.assertFalse(hasattr(result, forbidden_attribute))

    def test_invocation_cannot_reinterpret_semantic_package_authority(self):
        from briefforge.renderer_adapter import invoke_renderer_adapter

        result = invoke_renderer_adapter(ready_package(), compatible_contract())

        self.assertFalse(hasattr(result, "statements"))
        self.assertFalse(hasattr(result, "organizing_purpose"))
        self.assertFalse(hasattr(result, "upstream_references"))
        self.assertFalse(hasattr(result, "obligations"))
        self.assertFalse(hasattr(result, "validation_judgment"))
        self.assertFalse(hasattr(result, "semantic_authority"))
        self.assertFalse(hasattr(result, "reinterpretation"))


if __name__ == "__main__":
    unittest.main()
