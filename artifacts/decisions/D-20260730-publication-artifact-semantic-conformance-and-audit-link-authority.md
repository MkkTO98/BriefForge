# Decision — TASK-053 machine-verifiable semantic-realization authority

Date: 2026-07-30
Status: Accepted and implemented by TASK-053
Task: TASK-053

## Decision

1. Use the existing core `SemanticArtifactConformanceRecord` as the sole conformance carrier. Add no BCRP core kind.
2. Adopt `briefforge-static-html-semantic-realization-profile:1.0.0` as the sole TASK-053 profile. It proves only exact machine-verifiable realization of semantics carried by the authorized fixed minimal-HTML projection.
3. Adopt `briefforge-semantic-conformance-assessment-policy:1.0.0` and one required must-preserve extension contract for authorization, closure bindings, requirement outcomes, limitations and audit links.
4. One authorization binds one exact Release/lifecycle/Plan/capability/invocation/artifact/profile/assessor assessment. It grants no Manifest, distribution or successful-publication authority.
5. Expected semantics must be independently reproduced from exact persisted governed inputs. TASK-052 projection/mapping trace may be cross-checked but cannot be the sole expectation authority.
6. Actual semantics must be structurally extracted from independently reloaded and verified artifact bytes by a strict non-executing parser. Raw substring presence is not realization.
7. Every expected requirement receives exactly one outcome. Missing, duplicate, unauthorized, failed or indeterminate outcomes block approval.
8. Audit links are necessary traceability evidence but are not independently sufficient conformance proof.
9. A passing result appends one immutable conformance record to the exact nine-record TASK-052 closure. It does not rewrite TASK-052 audit evidence and does not create a `PublicationManifestRecord`.
10. Profile `1.0.0` is limited to exactly one Plan-authorized native observation statement with bounded plain text; fallback and long-document structures are not assessed.
11. Exact closure includes the full element/attribute inventory, global semantic-region order and nested hierarchy. Every independently assessable negative condition is reported; structurally unparseable bytes are blocking and indeterminate.
12. One-act authority is exclusively consumed and directory-fsynced before semantic extraction. Canonical evidence and its external commitment are independently persisted, directory-fsynced and reloaded.

## Claim limits

The profile does not prove visual attractiveness, editorial quality, comprehension, persuasion, accessibility certification, truth beyond released evidence, causal validity, universal browser/device behavior, successful publication or distribution.

## Trust model

TASK-052 trusted-process and writable-filesystem limitations remain. Hashes and admission commitments provide consistency and tamper detection, not human authentication, signatures/MACs, hostile-code sandbox attestation or WORM storage.

## Consequences

- Exactly eleven BCRP core record kinds remain.
- Generic BCRP stays fail closed and import independent.
- Specialized verification must reconcile only the exact known required extension boundary.
- Later lifecycle events may affect current eligibility but never mutate historical assessment evidence.
- TASK-053 stops before Manifest and distribution authority.
