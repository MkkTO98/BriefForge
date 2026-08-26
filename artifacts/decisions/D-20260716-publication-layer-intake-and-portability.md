# Decision: Publication Layer, Intake, and Portability

Date: 2026-07-16
Status: accepted semantic decision; no representation or implementation authorized
Scope: TASK-041

## Decision

Accept the layer and intake model in `artifacts/specifications/publication-boundary-intake-portability-lifecycle.md`.

1. Preserve Candidate Presentation Package -> Validation Judgment -> Ready Presentation Package as the only presentation-readiness lifecycle.
2. Accept `Presentation Intake` as the governed pre-candidate boundary.
3. Treat Presentation Intake as two necessary authority-separated responsibilities:
   - `Presentation Brief`: requestor-owned communication need and constraints;
   - `Portable Presentation Material`: upstream-authority-asserted, retained material sufficient for offline presentation work.
4. Accept `Portable Presentation Material` instead of `ResolvedInput` because BriefForge does not resolve upstream meaning or disputes.
5. Associate retained portable material and its fingerprint with candidate construction; do not require semantic embedding versus external immutable association until representation planning.
6. Require explicit admitted, incomplete, or rejected intake outcomes. Admission does not create or validate a Candidate package.
7. Require fixed-evidence publication inputs to support validation/regeneration with upstream runtimes offline.

## Authority boundaries

- Requestors own the communication need, not evidence truth.
- Upstream owners retain evidence, accepted-finding, provenance, caveat, freshness, and domain-semantic authority.
- BriefForge owns intake compatibility, presentation construction, presentation validation, promotion, and publication approval.
- Renderers own no evidence, analytical, validation, promotion, or publication authority.

## Rejected alternatives

- Intake as `RendererAdapterRequest`: rejected because renderer invocation occurs after Ready and cannot govern candidate construction.
- A second readiness/promotion lifecycle: rejected as duplication.
- `ResolvedInput`: rejected because it implies analytical or data-resolution authority.
- Live upstream references as sufficient fixed-evidence input: rejected because they break standalone reproducibility.
- Wholesale mandatory embedding of upstream material: deferred as representation-shaped and potentially duplicative.
- BriefForge repair, normalization, recomputation, inference, or acceptance of missing/conflicting upstream material: rejected as an ownership violation.

## Minimum audience decision

Audience semantics are limited to who must understand/use the presentation, their decision/communication context, material knowledge/terminology assumptions, and accessibility/sensitivity/distribution constraints. Personas, segmentation, personalization, and session/user models are prohibited.

## Consequences

- TASK-039 becomes evidence of the boundary: InsightForge materialized analytical input; BriefForge constructed and validated the presentation without recomputation.
- Generic typed external references remain permitted.
- Company and financial-domain fields remain deferred under DSB-007.
- No concrete fields, schema, serialization, validator, builder, or runtime behaviour are authorized.
