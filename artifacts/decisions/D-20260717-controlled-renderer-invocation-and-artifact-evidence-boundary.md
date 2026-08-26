# Decision — Controlled renderer invocation and artifact-evidence boundary

Date: 2026-07-17
Status: Accepted for TASK-052 implementation

## Decision

1. TASK-052 may consume only an independently verified active TASK-050 Release, complete TASK-049 lifecycle scope and independently reproduced TASK-051 Plan.
2. The existing fixed `minimal-html-renderer` is the only admitted renderer. A bounded BCRP-to-renderer projection may be added; it must not reconstruct or trust a legacy Ready package and must not create a renderer registry.
3. The exact Plan-selected expression is operational instruction. Every mapping must be consumed exactly once; unplanned or ambiguous material blocks.
4. One authorization binds one invocation transaction, exact Release/lifecycle/Plan/capability/renderer source digest/projection, a separate durable authorization ledger, output-directory/output-name/media-type/size/count/environment/external-asset policy and authorization time. Before execution, one fingerprint marker is created atomically and fsynced in that ledger. It is not reusable for another renderer, Plan, Release, output directory or invocation act. Retention and integrity of the separately authorized ledger are explicit operational authority assumptions; ledger deletion or replacement is authority-state corruption, not authorization restoration.
5. One invocation transaction performs exactly two independent freshly spawned executions of the same source-digest-bound fixed renderer for deterministic byte comparison and admits exactly one artifact. There is no retry, alternate renderer or partial-success promotion.
6. The artifact digest and byte length are computed from captured bytes before persistence. Both staged files are reread and fully verified before one Linux `renameat2(RENAME_EXCHANGE)` commit. The original and staged directory identities are checked on both sides of that exchange.
7. `GeneratedArtifactAuditRecord` may represent artifact existence and invocation/audit-link provenance. Its required specialized extension must explicitly mark semantic conformance, Manifest authority, distribution authority and successful publication as absent/unassessed.
8. Detected pre-commit failure returns complete diagnostics and no usable artifact/evidence object at the authorized path. The atomic exchange is the commit: a post-commit process failure can lose the Python return but leaves a complete, preverified pair that must be independently reverified; it cannot expose a one-file partial publication.

## Rationale

TASK-051 authorizes compatibility planning only. The existing renderer proves a real implementation exists, but its legacy Ready-facing adapter is not acceptable as BCRP authority. A narrow renderer-owned projection separates semantic authority from rendering without adding another renderer or allowing renderer inference.

The core audit record already carries Release/Ready/Plan/capability/artifact links. A strict extension can bind invocation provenance without changing BCRP's eleven core kinds or misusing semantic-conformance/Manifest records.

## Rejected alternatives

- Rendering from TASK-039 artifacts: historical evidence is not current authority.
- Reconstructing a legacy Ready package: bypasses the BCRP Plan boundary.
- Echo/dummy renderer or arbitrary callable/command: does not prove the actual renderer and creates injection authority.
- One execution with a determinism claim: insufficient evidence.
- Two separately authorized publication invocations: violates exact one-act authority and risks two admitted artifacts.
- Producing conformance or Manifest evidence here: collapses distinct authority gates.

## Consequences

The renderer adapter receives a narrow transport-neutral projection entry point with no styling change. TASK-052 remains renderer-specific and Linux-filesystem-specific because atomic pair publication requires `renameat2(RENAME_EXCHANGE)`. The child-process boundary controls the fixed renderer but does not claim hostile-code kernel sandboxing. Generalization requires later evidence and a separate decision.
