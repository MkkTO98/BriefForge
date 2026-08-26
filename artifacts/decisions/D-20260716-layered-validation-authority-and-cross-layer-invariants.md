# D-20260716 Layered Validation Authority and Cross-Layer Invariants

Date: 2026-07-16
Status: accepted
Task: TASK-043

## Decision

BriefForge accepts layered validation with explicit authority ownership:

1. intake admission — BriefForge presentation-intake authority with upstream/requestor authority for supplied meaning;
2. representation-profile structural validation — named profile contract;
3. semantic contract validation — BriefForge semantic contract plus declared upstream authorities for upstream-owned assertions;
4. lifecycle/readiness validation — BriefForge lifecycle policy;
5. governance approval — declared human/project decision or publication authority;
6. renderer compatibility and deterministic expression/fallback planning — BriefForge adapter contract plus truthful renderer-owner declarations;
7. output conformance — separate audit-link and semantic-artifact finding families under BriefForge publication/output conformance authority.

One tool may execute several layers, but it must preserve layer identity, policy identity, findings, evidence, blocking consequences, and resolution authority. No layer may manufacture authority owned by another.

Traceability and semantic conformance remain distinct. Correct package, fingerprint, policy, renderer, and artifact identifiers are necessary audit evidence but cannot prove that prose, values, roles, states, order, caveats, selection, or fallback preserve meaning.

The cross-layer invariants in `artifacts/specifications/semantic-representation-contract-and-layered-validation.md` are normative, including semantic reconstruction, identity, reference, obligation, explicit-state, selection closure, narrative, transformation, fallback, traceability, version, and standalone-publication invariants.

## Rationale

TASK-038 accepted structural, semantic, lifecycle, governance, compatibility, and renderer/output layers. TASK-041 and TASK-042 introduced intake, release, finite selection, multidimensional state, renderer requirements, fallback, and the explicit finding that current conformance is audit-link-only. Authority must therefore remain visible across the complete lifecycle.

A monolithic boolean validator would conceal whether a failure belongs to profile structure, BriefForge semantics, upstream authority, readiness, governance, renderer capability, or output expression. It would also invite structural schemas to become ontology authorities.

## Alternatives considered

- One validator/one pass-fail — rejected as an authority model.
- Structural schema success implies valid package — rejected.
- Ready implies governance/release approval — rejected.
- Audit identifiers imply faithful artifact — rejected.
- Renderer self-certification implies conformance — rejected.
- Separate tools required for every layer — rejected as unnecessary implementation prescription; authority separation, not process proliferation, is required.

## Consequences

- Future findings and corpus expectations must name their layer and owner.
- Semantic equality and round-trip tests must operate above transport syntax.
- Output checks must report audit-link and semantic failures separately.
- Governance decisions remain human/project records and cannot be inferred from validation.
- No validator implementation is authorized by this decision.
