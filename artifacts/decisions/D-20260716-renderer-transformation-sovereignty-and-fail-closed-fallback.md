# D-20260716 — Renderer Transformation Sovereignty and Fail-Closed Fallback

Date: 2026-07-16
Status: Accepted
Task: TASK-042

## Decision

A BriefForge renderer owns derivative mechanics only. It may encode, escape, lay out, paginate, anchor, style within scope, expose native inspection, calculate geometry, and perform a predeclared lossless expression transformation. It creates no evidence, analytical, validation, promotion, publication, default-selection, or lifecycle authority.

A renderer may not infer semantic role, prominence, narrative stage, caveat attachment, uncertainty, selector options, default state, ranking, extrema, summary, or claim strength from labels, keywords, position, or available values. Semantic sorting, derived captions, and synthesized summaries require exact preauthorization and validation; source order is preserved by default.

Future capability semantics must separately declare and verify:

- required semantic inputs;
- supported transformation/expression classes;
- supported interaction/state behavior;
- obligation preservation;
- static fallback;
- accessibility and standalone behavior;
- renderer identity/version evidence.

Current package-feature compatibility is narrow input evidence, not proof of faithful output.

Current rendered-artifact conformance is audit-link conformance. Package identity, semantic fingerprint, validation-policy identity, and adapter identity are necessary but insufficient to prove rendered semantic fidelity. Future semantic artifact conformance remains a separate required concern.

Fallback is fail closed. The permitted order is:

1. verified native expression;
2. prevalidated semantically equivalent expression;
3. deterministic complete static representation;
4. explicit authorized unsupported/unavailable expression when the publication remains non-misleading;
5. reject invocation or artifact.

Silent best effort is prohibited. A fallback must never drop required material or obligations, change evidence snapshots, use live lookup, compute values, choose an undeclared state, flatten conflict, treat zero as missing, or present stale/withdrawn material as current.

## Rationale

- Renderer adapters are downstream consumers of Ready packages, not semantic authorities.
- Existing `RendererAdapterCapability.package_features` proves only the presence of known package inputs.
- Existing conformance tests verify audit identifiers but do not inspect prose, values, ordering, caveat visibility, state, or transformation correctness.
- Existing renderer evidence includes heuristic role/prominence inference, duplication, semantic-looking extrema/summary derivation, and silent exhibit omission. These are pressure for semantic constraints, not authorization to modify the renderer in TASK-042.
- Caveat, uncertainty, provenance, distribution, and evidence-state obligations must survive target-specific expression.

## Rejected alternatives

1. Trust renderer identity as proof of output fidelity.
   - Rejected: identity and version do not prove a particular artifact preserved meaning.
2. Treat all deterministic transformations as semantic-neutral.
   - Rejected: deterministic sorting, ranking, aggregation, or summarization can create claims.
3. Allow silent omission of unsupported structures.
   - Rejected: omission can detach evidence and obligations.
4. Let metadata-only conformance stand for semantic conformance.
   - Rejected: fabricated prose can carry correct identifiers.
5. Introduce a general visualization or plugin architecture to solve capability gaps.
   - Rejected as speculative and constitutionally outside this task.

## Consequences

- No renderer or conformance implementation is changed now.
- Future renderer preflight must positively match every required semantic capability; undeclared/unverified means incompatible.
- A different renderer may generate a rerender only after independent compatibility and release-record linkage.
- Artifact failure does not rewrite Ready or semantic release validity, though inability to produce any required standalone artifact blocks successful publication.
- Renderer backlog evidence remains necessary for implementation authorization.

## Evidence anchors

- `docs/renderer-adapter-contract.md`.
- `docs/rendered-artifact-conformance.md`.
- `docs/renderer-improvement-policy.md`.
- `src/briefforge/renderer_adapter.py` (`RendererAdapterCapability`, compatibility, static exhibit, and conformance paths).
- `tests/test_renderer_adapter_contract.py`.
- `tests/test_rendered_artifact_conformance.py`.
- `artifacts/specifications/semantic-authority-evidence-states-interaction-renderer-fallback.md`.
