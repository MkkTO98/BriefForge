# Renderer Adapter Contract

Date: 2026-07-02
Task: TASK-008 Concrete Renderer Adapter Contract
Status: Implemented as a minimal contract-shape proof.

## Purpose

TASK-008 defines the smallest concrete renderer-adapter contract shape needed before any renderer exists.

The contract is a declaration surface only. It lets a downstream renderer adapter identify itself and declare which Ready Presentation Package features it expects to consume. BriefForge can then check compatibility between a Ready Presentation Package and that declaration without creating rendered output and without granting the adapter semantic authority.

## Implemented contract objects

Implemented in `src/briefforge/renderer_adapter.py`:

- `RendererAdapterIdentity`
- `RendererAdapterCapability`
- `RendererAdapterContract`
- `RendererAdapterCompatibility`
- `RendererAdapterContractRejected`
- `check_renderer_adapter_compatibility(ready_package, contract)`

The pre-existing TASK-007 objects remain:

- `RendererAdapterRequest`
- `RendererAdapterRejected`
- `prepare_renderer_adapter_request(ready_package)`

## Why adapter contracts are declaration surfaces, not renderers

The contract records what an adapter says about itself and the package features it expects. It does not perform transformation, layout, rendering, serialization, exporting, navigation, persistence, networking, or display.

This is architecturally important because BriefForge owns presentation meaning, not delivery meaning. A renderer adapter may later consume a Ready Presentation Package, but the contract itself is only a boundary declaration. It does not decide what the package means, alter the package, or produce a target-specific artifact.

## Why adapter identity is useful before rendering exists

A stable adapter identity is useful before rendering because it gives BriefForge an audit handle for downstream compatibility checks. The identity records which adapter declaration asked for which semantic package features.

That enables future evidence trails such as:

- which adapter declaration was checked;
- which version of an adapter declaration was involved;
- which owner or boundary party declared the adapter capability;
- whether the Ready package supplied the requested semantic features.

This does not imply the adapter has been implemented. It only gives the compatibility boundary a stable name.

## Why this does not introduce renderer ownership into BriefForge

BriefForge still does not own renderer engines. The implemented contract shape has no HTML, PDF, browser, template, visualization, chart, map, export, persistence, API, networking, portal, dashboard, search, UI, component, or output field.

`RendererAdapterCapability` contains only:

- `capability_id`
- `description`
- `package_features`

`RendererAdapterContract` contains only:

- `identity`
- `capabilities`

`RendererAdapterCompatibility` contains only:

- `ready_package`
- `contract`
- `compatible`
- `missing_package_features`

The compatibility check uses the existing Ready-only renderer-adapter request boundary. It asks whether declared package features are present on the request. It returns a compatibility record; it does not render or reinterpret anything.

## Compatibility semantics

A contract is compatible when every declared `package_features` item is both:

1. a recognized renderer-adapter request feature; and
2. available on the immutable `RendererAdapterRequest` prepared from the Ready Presentation Package.

The currently recognized package features are:

- `identity`
- `organizing_purpose`
- `statements`
- `upstream_references`
- `obligations`
- `validation_judgment`
- `semantic_fingerprint`
- `validation_policy_id`

Unknown or unavailable declared features are reported as `missing_package_features`, making the result incompatible without mutating the Ready package.

## Rejection behavior

Malformed declarations are rejected with `RendererAdapterContractRejected` when:

- adapter identity is missing;
- identity text fields are empty or non-string;
- capability declarations are empty, non-tuples, or non-capability objects;
- capability identity or description is empty;
- capability `package_features` is not a non-empty tuple of non-empty strings.

A non-Ready package is still rejected by the existing `RendererAdapterRejected` boundary.

## Constitutional contradiction assessment

No contradiction in the frozen constitution was exposed.

The implementation strengthened the frozen boundary:

- renderer adapters remain downstream consumers;
- Ready Presentation Packages remain the only accepted semantic package input;
- adapter contracts declare needs but do not own package meaning;
- BriefForge retains presentation-contract ownership without taking ownership of renderer engines or delivery surfaces.

## Implementation Readiness Assessment

Validated by TASK-008:

- Well-formed renderer adapter contracts can be created.
- Stable adapter identity is required.
- Capabilities are declarative only.
- Ready Presentation Packages can be checked against adapter contracts.
- Malformed identities and capabilities are rejected.
- Compatibility checks do not mutate Ready Presentation Packages.
- No rendered output is produced.

Still intentionally unimplemented:

- renderer engines;
- HTML, PDF, browser output, or document output;
- templates;
- charts, maps, and visualization;
- exports;
- persistence;
- APIs and networking;
- portal or dashboard behavior;
- UI components;
- real downstream renderer behavior.

Recommended next investigation:

If rendering is later approved, investigate the smallest renderer-adapter invocation protocol that consumes a `RendererAdapterCompatibility` result and a `RendererAdapterRequest` without allowing the renderer to become a semantic authority. If auditability is more urgent, investigate durable records for rejected package and rejected contract events.
