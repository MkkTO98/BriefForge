# TASK-052 — Controlled Renderer Invocation and Publication Artifact-Evidence Boundary Proof

Status: **COMPLETED — CLEAR TO PROCEED UNDER DOCUMENTED CLOSEOUT-EVIDENCE EXCEPTION**

## Objective

Prove the smallest executable boundary:

```text
independently reverified active Publication Release
+ complete TASK-049 lifecycle scope
+ independently reverified TASK-051 compatibility Plan
+ exact fixed renderer implementation identity
+ exact one-act invocation authorization
→ one controlled invocation transaction
→ exactly one immutable artifact and audit-link/invocation evidence
```

The transaction may execute the same fixed renderer twice in independent temporary directories solely to prove byte equality; only one resulting artifact may be admitted and persisted.

## Readiness and gates

- Recovery succeeded and TASK-052 was unused before activation.
- The repository is intentionally non-Git.
- Baseline: 274 tests and 678 task-manifest paths.
- Actual-renderer gate: the existing `minimal-html-renderer` can remain the renderer if a bounded BCRP projection reaches its rendering core without reconstructing or trusting a legacy Ready package.
- Representation gate: existing `GeneratedArtifactAuditRecord` is sufficient only when its specialized extension explicitly says artifact existence/audit links are verified and semantic conformance, Manifest, distribution and successful publication remain unassessed/unauthorized.

## Scope

- independently reverify Release, lifecycle scope and TASK-051 Plan immediately before invocation;
- introduce only the fixed projection needed by the existing renderer;
- bind one exact renderer identity/version and one exact non-reusable invocation act;
- constrain environment, filesystem boundary, media type, output name/count/size, external assets and timeout semantics;
- execute the fixed renderer twice for deterministic comparison inside one invocation transaction;
- compute digest and byte length from captured bytes before persistence;
- persist exactly one artifact plus explicit invocation/audit-link evidence;
- reload and independently verify both.

## Non-goals

No semantic-conformance approval, `SemanticArtifactConformanceRecord`, `PublicationManifestRecord`, distribution, AtlasForge integration, browser automation, live data, external service, visual redesign, renderer registry, arbitrary callable/command, retry, alternate renderer or fallback execution.

## Success criteria

- One truthful synthetic governed BCRP Release/Plan reaches the fixed existing renderer without TASK-039 publication artifacts or legacy Ready renderer input.
- Every Plan mapping is consumed exactly once and only its selected expression is used.
- Exact authorization and boundary mismatches fail before usable artifact/evidence is returned.
- Two independent renderer executions are byte-identical; nondeterminism fails closed.
- Output traversal, symlink, auxiliary file, media-type, size/count, external-asset and mutation attacks fail closed.
- Artifact/evidence cross-bind Release, lifecycle scope, Plan, capability declaration, renderer implementation, authorization, input projection, output inventory, digest/length and outcome.
- No success path asserts semantic conformance, Manifest authority, distribution authority or successful publication.
- Generic BCRP remains import-independent with exactly eleven record kinds.

## Expected evidence

- `artifacts/decisions/D-20260717-controlled-renderer-invocation-and-artifact-evidence-boundary.md`
- `artifacts/specifications/controlled-renderer-invocation-and-artifact-evidence.md`
- `src/briefforge/controlled_renderer_invocation.py`
- bounded projection support in `src/briefforge/renderer_adapter.py`
- `tests/test_controlled_renderer_invocation.py`
- `artifacts/reports/R-20260717-task-052-controlled-renderer-invocation-and-publication-artifact-evidence-boundary-proof.md`
- `artifacts/decisions/D-20260730-task-052-closeout-evidence-exception-acceptance.md`

## Stop condition

Satisfied. Work stopped after generated artifact existence and invocation/audit-link evidence. No semantic-conformance evidence, Manifest, distribution authority or AtlasForge integration was created.

## Outcome

- The exact existing `renderer:minimal-html` / `minimal-html-renderer` implementation is invoked through one fixed adapter and a bounded BCRP projection; no renderer registry, legacy Ready input, fallback, callable, module path or command is accepted.
- Release, complete lifecycle scope, current active state, Plan, capability declaration, exact Plan bytes/mappings, renderer call graph, governed invocation authority and one-act authorization are independently reverified before execution.
- One transaction performs exactly two isolated executions under an effective-control-attested minimal interpreter environment, requires byte equality and admits exactly one regular HTML artifact.
- Descriptor-relative staging, inode-bound exchange, rollback, bounded inventory, canonical evidence, an external admission commitment and persisted reverification make changed bytes or metadata fail closed under the disclosed trusted local-writer boundary.
- The nine-record evidence closure marks artifact existence/audit links verified while semantic conformance remains `unassessed`, Manifest/distribution authority remains `absent` and successful publication remains `not-asserted`.
- Focused TASK-052 tests pass 22 cases; the complete suite passes 296 cases. Independent authority-critical re-review approved the final isolated-worker boundary.
- BCRP remains import-independent with exactly eleven core record kinds.
- Original mechanical closeout was **BLOCKED / NOT RECONCILED** because the required pre-task manifest was captured only after five expected TASK-052 paths had been created; exact byte accounting from the authoritative 678-path baseline remains unavailable.
- On 2026-07-30, the human project owner accepted the exact five-path count-and-identity reconstruction as sufficient closeout evidence under `D-20260730-task-052-closeout-evidence-exception-acceptance.md`. This resolves the blocker without representing direct 678-path byte accounting or weakening any technical/semantic gate.

Canonical outcome report: `artifacts/reports/R-20260717-task-052-controlled-renderer-invocation-and-publication-artifact-evidence-boundary-proof.md`.

TASK-053 is recommended but remains unactivated.
