# Toy Plain-Text Renderer Proof

Date: 2026-07-02
Task: TASK-010 Bounded Toy Renderer Proof
Status: Implemented as a deliberately non-general plain-text renderer proof.

## Purpose

TASK-010 proves that one Ready Presentation Package can be rendered through the existing renderer-adapter boundary without making renderer output a semantic authority.

The proof is intentionally small:

- one toy renderer adapter contract;
- one bounded plain-text artifact;
- audit metadata linking adapter identity, package identity, semantic fingerprint, and validation policy identity;
- no general renderer engine.

## Implemented objects

Implemented in `src/briefforge/renderer_adapter.py`:

- `ToyPlainTextRenderedArtifact`
- `toy_plain_text_renderer_contract()`
- `render_toy_plain_text(ready_package, contract=None)`

The toy renderer consumes the existing chain:

```text
Ready Presentation Package
-> Renderer Adapter Contract Compatibility Check
-> Renderer Adapter Invocation Protocol
-> Toy Plain-Text Rendered Artifact
```

## Why this renderer is deliberately non-general

The renderer is a proof object, not a product subsystem.

It deliberately avoids:

- renderer engines;
- renderer plugin registries;
- templates;
- component abstractions;
- layout systems;
- document/page models;
- HTML/PDF/browser assumptions;
- visualization/chart/map systems;
- persistence/export/network/API behavior.

Its only output field is `plain_text`. That field is sufficient to prove downstream rendering can occur, but insufficient to establish a general rendering architecture.

## Why rendering is downstream from readiness

BriefForge's semantic authority is the Presentation Package lifecycle:

```text
Candidate Presentation Package
-> Validation Judgment
-> Ready Presentation Package
```

Rendering starts only after readiness. The toy renderer accepts only a `ReadyPresentationPackage`; Candidate Presentation Packages are rejected by the existing renderer-adapter boundary.

This preserves the constitutional ordering:

1. package meaning is authored as candidate substance;
2. package substance is validated;
3. a matching successful judgment promotes it to Ready;
4. renderer adapters may consume the Ready package downstream;
5. renderer output does not feed back into readiness.

## Why renderer output is not canonical

The canonical BriefForge object remains the structured semantic Presentation Package, not renderer output.

The toy artifact is not canonical because it:

- is not a Candidate Presentation Package;
- is not a Ready Presentation Package;
- is not a Validation Judgment;
- does not expose statements, organizing purpose, upstream references, obligations, or validation judgment as authority-bearing fields;
- contains only bounded plain output and audit metadata;
- cannot validate, promote, override, reinterpret, or replace package substance.

The `plain_text` field may reflect semantic package content, but reflection is not authority. Authority remains with the Ready package and its validation identity.

## Audit metadata

`ToyPlainTextRenderedArtifact` records:

- `adapter_identity`
- `package_identity`
- `semantic_fingerprint`
- `validation_policy_id`

This links the artifact to the adapter and exact Ready package substance that produced it without making the artifact canonical.

## Rejection behavior

The toy renderer rejects:

- Candidate Presentation Packages and other non-Ready objects through `RendererAdapterRejected`;
- incompatible or non-toy adapter contracts through `RendererAdapterInvocationRejected`.

The renderer does not perform validation or promotion itself.

## Constitutional contradiction assessment

No contradiction in the frozen constitution was exposed.

TASK-010 does clarify one important boundary: BriefForge can own a minimal adapter-side proof of rendering without owning a renderer engine. The constitutional risk is not plain-text rendering itself; the risk is allowing renderer output to become canonical or allowing renderer abstractions to pull BriefForge into browser, template, component, export, dashboard, or visualization ownership.

## Implementation Readiness Assessment

Validated by TASK-010:

- A Ready Presentation Package can produce a bounded plain-text rendered artifact through the renderer-adapter boundary.
- Candidate Presentation Packages cannot render.
- Incompatible adapter contracts cannot render.
- Output contains bounded plain text plus audit metadata.
- Rendering does not mutate Ready Presentation Packages.
- Renderer output does not become semantic authority.

Still intentionally unimplemented:

- HTML;
- PDF;
- browser output;
- renderer engines;
- templates;
- charts, maps, visualization;
- exports;
- persistence;
- APIs and networking;
- portal, dashboard, search, or UI behavior;
- generalized renderer registry or plugin system.

Recommended next investigation:

If additional implementation is approved, investigate durable renderer output event records or a narrowly specified renderer-output conformance boundary before any richer target such as HTML. Do not proceed directly to browser/report infrastructure.
