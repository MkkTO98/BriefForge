# Renderer Adapter Invocation Protocol

Date: 2026-07-02
Task: TASK-009 Renderer Adapter Invocation Protocol
Status: Implemented as a metadata-only invocation proof.

## Purpose

TASK-009 defines the smallest renderer-adapter invocation protocol that can invoke a compatible renderer-adapter contract without implementing rendering.

The invocation protocol proves that BriefForge can cross from a Ready Presentation Package and a compatible adapter contract into a controlled invocation record, then return metadata-only evidence of invocation.

## Implemented invocation objects

Implemented in `src/briefforge/renderer_adapter.py`:

- `RendererAdapterInvocation`
- `RendererAdapterInvocationResult`
- `RendererAdapterInvocationRejected`
- `invoke_renderer_adapter(ready_package, contract)`

The invocation function depends on the existing TASK-008 compatibility check:

- incompatible contracts are rejected;
- compatible contracts produce metadata-only invocation records;
- Ready Presentation Packages are not mutated;
- no rendered output is created.

## Why invocation is separate from rendering

Invocation means a compatible adapter contract has been accepted at the boundary. Rendering means producing a target-specific artifact or surface. Those are different responsibilities.

BriefForge may need to prove that a renderer adapter can be invoked, but that does not require BriefForge to own layout, HTML, PDF, browser behavior, templates, visualization, export, or UI behavior. Separating invocation from rendering preserves the constitutional boundary: BriefForge owns presentation meaning and adapter boundary protocols, not renderer engines.

## Why invocation result is metadata only

`RendererAdapterInvocationResult` records only:

- the invocation record;
- whether the invocation was accepted;
- adapter identity;
- package identity;
- semantic fingerprint;
- validation policy identity.

This metadata is enough to prove that the correct adapter declaration was invoked against the correct Ready Presentation Package under the correct validation identity. It is not enough to display, serialize, export, or transform the package, and that limitation is intentional.

## Preparing for a future toy renderer without renderer ownership

A future toy renderer can consume the existing boundary chain:

```text
Ready Presentation Package
-> Renderer Adapter Contract compatibility check
-> Renderer Adapter Invocation
-> future renderer-specific adapter work
```

TASK-009 stops before the final step. This gives a future toy renderer a stable entry point while keeping renderer behavior outside BriefForge's current implementation scope.

A future renderer should be added only under a separately approved task. It should consume existing invocation metadata and immutable request access rather than gaining authority to reinterpret package meaning.

## Rejection behavior

`invoke_renderer_adapter` rejects incompatible adapter contracts with `RendererAdapterInvocationRejected`.

Compatibility is still determined by `check_renderer_adapter_compatibility`, which checks declared package features against the Ready-only renderer-adapter request boundary.

## Constitutional contradiction assessment

No contradiction in the frozen constitution was exposed.

The implementation preserves all current boundaries:

- only Ready Presentation Packages can enter the renderer-adapter boundary;
- only compatible contracts can be invoked;
- invocation result is metadata-only;
- invocation does not render;
- invocation does not mutate package substance;
- invocation does not reinterpret semantic authority.

## Implementation Readiness Assessment

Validated by TASK-009:

- Compatible adapter contracts can be invoked.
- Incompatible adapter contracts are rejected.
- Invocation results record adapter identity, package identity, semantic fingerprint, and validation policy identity.
- Invocation does not mutate Ready Presentation Packages.
- Invocation does not create rendered output.
- Invocation results do not expose semantic package authority fields.

Still intentionally unimplemented:

- real renderer adapters;
- renderer engines;
- HTML, PDF, browser, or document output;
- templates;
- charts, maps, and visualization;
- exports;
- persistence;
- APIs and networking;
- portal, dashboard, search, or UI behavior.

Recommended next investigation:

If rendering is now genuinely needed, the next minimal task should be a toy renderer proof that consumes invocation metadata and immutable request access while producing a deliberately bounded non-production artifact. If auditability is more important, investigate durable records for rejected invocation and contract events first.
