"""BriefForge package exports.

Exports are resolved lazily so renderer-independent subpackages such as BCRP do
not import the existing runtime, presentation models, or renderer adapter.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORT_MODULE = {
    "CandidatePresentationPackage": ".runtime",
    "CountryComparisonBuilder": ".presentation_models",
    "CountryComparisonPresentation": ".presentation_models",
    "CountryProfileBuilder": ".presentation_models",
    "CountryProfilePresentation": ".presentation_models",
    "CURRENT_VALIDATION_POLICY_ID": ".validation",
    "DownstreamBoundaryRejected": ".downstream",
    "DownstreamSemanticPackage": ".downstream",
    "EncounterSemantics": ".runtime",
    "HtmlRenderedArtifact": ".renderer_adapter",
    "InvestmentThesisBuilder": ".presentation_models",
    "InvestmentThesisPresentation": ".presentation_models",
    "OrganizingPurpose": ".runtime",
    "PackageIdentity": ".runtime",
    "PresentationObligation": ".runtime",
    "PresentationPackageBuildRejected": ".builder",
    "PresentationPackageBuilder": ".builder",
    "PresentationStatement": ".runtime",
    "PromotionRejected": ".promotion",
    "ReadyPresentationPackage": ".promotion",
    "RenderedArtifactConformance": ".renderer_adapter",
    "RenderedArtifactConformanceRejected": ".renderer_adapter",
    "RendererAdapterCapability": ".renderer_adapter",
    "RendererAdapterCompatibility": ".renderer_adapter",
    "RendererAdapterContract": ".renderer_adapter",
    "RendererAdapterContractRejected": ".renderer_adapter",
    "RendererAdapterIdentity": ".renderer_adapter",
    "RendererAdapterInvocation": ".renderer_adapter",
    "RendererAdapterInvocationRejected": ".renderer_adapter",
    "RendererAdapterInvocationResult": ".renderer_adapter",
    "RendererAdapterRejected": ".renderer_adapter",
    "RendererAdapterRequest": ".renderer_adapter",
    "ToyPlainTextRenderedArtifact": ".renderer_adapter",
    "UpstreamReference": ".runtime",
    "ValidationFinding": ".validation",
    "ValidationJudgment": ".validation",
    "check_rendered_artifact_conformance": ".renderer_adapter",
    "check_renderer_adapter_compatibility": ".renderer_adapter",
    "html_renderer_contract": ".renderer_adapter",
    "invoke_renderer_adapter": ".renderer_adapter",
    "prepare_downstream_semantic_package": ".downstream",
    "prepare_renderer_adapter_request": ".renderer_adapter",
    "promote_candidate_presentation_package": ".promotion",
    "render_minimal_html": ".renderer_adapter",
    "render_toy_plain_text": ".renderer_adapter",
    "semantic_fingerprint": ".runtime",
    "toy_plain_text_renderer_contract": ".renderer_adapter",
    "validate_candidate_presentation_package": ".validation",
}

__all__ = list(_EXPORT_MODULE)


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name, __name__), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
