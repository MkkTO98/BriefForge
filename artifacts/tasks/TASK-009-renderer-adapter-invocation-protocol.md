# TASK-009: Renderer Adapter Invocation Protocol

Date: 2026-07-02
Status: Complete

## Objective

Implement the smallest renderer-adapter invocation protocol without implementing actual rendering.

The task proves that a compatible renderer adapter contract can be invoked through a controlled boundary and return a non-rendered invocation result.

## Scope implemented

Implemented only:

- `RendererAdapterInvocation`
- `RendererAdapterInvocationResult`
- `RendererAdapterInvocationRejected`
- `invoke_renderer_adapter(ready_package, contract)`
- rejection of incompatible adapter contracts
- proof that invocation does not mutate Ready Presentation Packages

## Scope excluded

No rendering or delivery implementation was added.

Explicitly not implemented:

- HTML
- PDF
- browser output
- templates
- charts
- maps
- visualization
- exports
- persistence
- APIs
- networking
- portal behavior
- dashboard behavior
- UI components
- renderer engines
- downstream renderer implementations

## RED verification

Command:

```bash
python3 -m unittest tests.test_renderer_adapter_invocation -v
```

Observed RED result before implementation:

```text
Ran 6 tests in 0.015s
FAILED (errors=6)
```

Expected failure reason:

```text
ImportError: cannot import name 'RendererAdapterInvocation' from 'briefforge.renderer_adapter'
ImportError: cannot import name 'invoke_renderer_adapter' from 'briefforge.renderer_adapter'
```

The tests failed because the invocation protocol did not exist.

## GREEN verification

Command:

```bash
python3 -m unittest tests.test_renderer_adapter_invocation -v
```

Observed GREEN result after implementation:

```text
Ran 6 tests in 0.002s
OK
```

## Files modified

Implementation:

- `src/briefforge/renderer_adapter.py`
- `src/briefforge/__init__.py`

Tests:

- `tests/test_renderer_adapter_invocation.py`

Documentation:

- `docs/renderer-adapter-invocation.md`
- `artifacts/tasks/TASK-009-renderer-adapter-invocation-protocol.md`

Continuity:

- `state/project_state.md`
- `state/architecture.md`
- `state/active_goal.md`
- `state/recent_changes.md`
- `context/latest_handoff.md`

## Architectural observations

1. Invocation is separate from rendering.
2. Invocation result is metadata-only.
3. Compatible contracts can cross the invocation boundary.
4. Incompatible contracts are rejected before invocation.
5. Invocation preserves Ready Presentation Package immutability.
6. Invocation results record adapter/package audit metadata without exposing semantic package authority.
7. No contradiction in the frozen constitution was exposed.

## Implementation Readiness Assessment

Ready for the current phase:

- A compatible adapter contract can now be invoked in a controlled way.
- The invocation protocol is renderer-free and metadata-only.
- Rejection behavior exists for incompatible contracts.
- The boundary preserves package immutability and semantic authority constraints.

Not ready / still deferred:

- invoking real renderer code;
- renderer adapter output protocols;
- HTML/PDF/browser/document rendering;
- templates and UI components;
- visualization, charts, maps, exports;
- persistence, APIs, networking;
- portal or dashboard integration.

Recommended next task:

Investigate either a bounded toy renderer proof or durable rejected invocation/contract event representation. Do not begin renderer implementation without a separately approved task.
