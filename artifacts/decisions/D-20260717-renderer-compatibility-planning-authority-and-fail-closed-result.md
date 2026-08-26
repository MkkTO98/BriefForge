# D-20260717 — Renderer Compatibility Planning Authority and Fail-Closed Result

Date: 2026-07-17
Status: Accepted
Task: TASK-051

## Decision

Use the existing BCRP `RendererCapabilityDeclarationRecord` and `RendererCompatibilityPlanRecord` kinds, refined by exact required semantic extensions under a specialized BriefForge planning verifier. Add no record kind and do not weaken generic BCRP.

A successful Plan directly binds the exact immutable TASK-050 Release, governed Ready/Candidate/snapshot/publication lineage, complete TASK-049 lifecycle inventory and current state, one immutable renderer declaration and fingerprint, one planning policy/authorization, and exactly one authorized outcome for every Candidate renderer requirement.

A blocking attempt returns complete technical findings and no BCRP Plan record. A blocked Plan record would incorrectly imply downstream usability and is rejected.

Ordinary planning admits only the exact sole current active Release. Explicitly complete empty lifecycle events are valid; omitted, incomplete, stale, withdrawn, superseded, conflicting or ambiguous scope is not. No archival rendering authority is created.

Capability declarations are renderer-owned claims inside a trusted process boundary. They are not runtime detection, code introspection, credentials, signatures, output evidence, or artifact-conformance proof.

## Rationale

The core record topology already expresses the correct stages, but its minimal core fields cannot carry the authority-critical Release, lifecycle, capability inventory and per-requirement mapping closure. Required extensions refine the accepted topology without inventing a parallel record format. Specialized verification can understand those extensions while generic BCRP remains fail closed.

No usable Plan should exist when required meaning is unexpressible. Keeping negative findings outside a Plan record makes this boundary mechanically unambiguous.

## Rejected alternatives

1. Infer capabilities from renderer code or current adapter behavior — rejected as runtime coupling and false evidence.
2. Bind only Ready — rejected because the Plan could detach from one exact Release and lifecycle state.
3. Treat omitted lifecycle events as empty — rejected because omission could hide withdrawal or supersession.
4. Produce `supported: false` Plan records — rejected because downstream callers could misread them as executable plans.
5. Choose one equal fallback lexically — rejected because identity ordering is not semantic authority.
6. Use capability claims as conformance proof — rejected because output inspection is a later independent stage.
7. Add a twelfth BCRP kind — rejected because accepted core kinds already own both declaration and Plan responsibilities.

## Consequences

- Generic BCRP remains eleven kinds and fail closed on required specialized extensions.
- TASK-051 stops before renderer selection/invocation and all artifact/Manifest/distribution stages.
- Renderer version, declaration, lifecycle or Release drift makes old Plan evidence ineligible without mutation.
- A later controlled invocation task must independently consume a reverified eligible Plan and still separate output from conformance and Manifest authority.
