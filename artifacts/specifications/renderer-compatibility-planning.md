# Renderer Compatibility Planning 1.0

Date: 2026-07-17
Status: accepted specification
Task: TASK-051
Policy: `briefforge-renderer-compatibility-planning-policy:1.0.0`
Authorization contract: `briefforge:renderer-compatibility-planning-authorization:1.0.0`
Declaration contract: `briefforge:renderer-capability-declaration:1.0.0`
Plan contract: `briefforge:renderer-compatibility-plan:1.0.0`

## 1. Admitted topology

Input is exactly one independently reverified TASK-050 six-record Release closure, its exact fixed evidence snapshot, an explicitly complete TASK-049 lifecycle scope, one renderer-owned capability declaration represented by the already accepted BCRP `RendererCapabilityDeclarationRecord`, and explicit BriefForge planning authorization.

Successful output adds exactly one `RendererCompatibilityPlanRecord`. Blocking output is a technical planning result containing all deterministic blocking findings and no Plan record. No new BCRP kind is introduced.

## 2. Representation refinement

Core Plan fields bind Ready and capability-record identity but cannot honestly bind Release/lifecycle/declaration/mapping authority. One required semantic Plan extension therefore binds:

- exact Release identity and `release-semantic` fingerprint;
- exact Ready identity and Candidate semantic fingerprint;
- publication identity/version and fixed evidence snapshot identity/version/inventory digest;
- complete lifecycle Release/event/policy inventory digest, event identities/fingerprints and graph-derived current state;
- capability record identity, renderer identity/version, declaration/profile identity/version/time, complete inventory, constraints and declaration fingerprint;
- planning policy, authority, authorization identity/time, Plan identity/time;
- exactly one ordered mapping outcome for every Candidate renderer requirement;
- excluded renderer/artifact/conformance/Manifest/distribution authorities.

One required declaration extension binds renderer owner/role, declaration identity/time, capability profile, complete detailed inventory, constraints, explicitly unsupported capabilities, declaration fingerprint contract, and claim-only trust character.

Generic BCRP must reject these extensions unless this specialized profile verifies them exactly.

## 3. Capability declaration

A declaration is immutable renderer-owned evidence supplied inside the trusted BriefForge planning boundary. It is not runtime detection, code introspection, a signature, renderer authentication, actual output evidence, or semantic artifact-conformance proof.

Exact accepted owner/role/profile/policy checks prevent caller-supplied labels from creating authority. Every declaration inventory and claim constraint set is an exact immutable tuple. Every capability inventory item has one exact identity, one expression mode, explicit supported state and a closed unique constraint set. Inventory is explicitly complete. Unsupported capability identities are explicit and disjoint from supported inventory. Canonical JSON over all declaration material yields the declaration fingerprint.

No renderer implementation is imported, loaded, selected, invoked or inspected.

## 4. Candidate requirement and fallback contract

Each planning-admissible renderer requirement explicitly supplies:

- unique requirement identity;
- exact capability identity;
- `mandatory` Boolean and matching `criticality` (`required` or `optional`);
- non-empty unique affected semantic `target_refs`;
- unique required constraints;
- ordered permitted transformations;
- unique fallback references;
- explicit `unsupported_allowed` Boolean.

Every referenced fallback is Candidate-owned and explicitly supplies its identity, kind, expression mode (`equivalent` or `static`), exact required capability, complete Boolean, covered semantic refs, preserved authority-label refs, preserved caveat refs, and declared transformation. There is no inferred equivalence, substring matching, display-label matching, or invented fallback.

Fallback kind/mode is closed: `equivalent-expression` maps only to `equivalent`; `static-state-expansion`, `static-table`, `static-visual`, `static-text`, and `print-expression` map only to `static`. Unknown, malformed, invocation/artifact-bearing, or mode-inconsistent kinds block.

A fallback is complete for planning only if it covers every affected semantic ref and every authority/caveat obligation the requirement declares. This proves planned coverage, not later artifact behavior.

## 5. Deterministic planning order

For every requirement, evaluate exactly:

1. exact native capability with all required constraints;
2. first uniquely admissible predeclared equivalent expression;
3. first uniquely admissible predeclared complete static expression;
4. explicit unsupported only for a non-required requirement whose own semantics allow it;
5. blocking incompatibility.

At a policy rank, more than one equally admissible choice is ambiguous and blocking; identity order is not authority. Required meaning cannot be downgraded. Missing/duplicate/contradictory requirements, unconsumed fallback ambiguity, incomplete semantic/authority/caveat coverage, or unsupported-required use blocks.

Every success mapping records requirement, affected refs, criticality, expression mode, exact capability, exact fallback if any, exact transformation, and reason. Exactly one mapping per requirement is required.

## 6. Lifecycle closure

The lifecycle scope explicitly contains complete Release, event and policy inventories plus an inventory digest. Omission is not empty. Validation and graph derivation execute against exact TASK-049 semantics. Ordinary planning admits only the exact planned Release when its graph-derived state is `current` and it is the sole current Release. Superseded, withdrawn, stale, absent, conflicting and ambiguous states block. No archival-rerender policy exists.

## 7. Production, persistence and staleness

Inputs are deep-copied; verified state is stored as immutable deterministic text and exposes detached values. Identical explicit input yields identical output. Persisted verification accepts only an exact `BCRPBundle` with an exact immutable tuple of eight BCRP records, then independently reverifies Release, snapshot, lifecycle, declaration, Candidate requirements/fallbacks, authorization, Plan structure, mappings, generic L0–L5 findings and closure fingerprint.

A Plan is ineligible for future use if Release/Ready/Candidate/publication/snapshot/lifecycle inventory or state/renderer version/declaration fingerprint/planning policy changes. Historical content remains immutable and inspectable; changed inputs require a new Plan.

## 8. Explicit exclusions

A Plan is not renderer output, renderer invocation authority, artifact authority, artifact-conformance evidence, Publication Manifest authority, or distribution authority. Capability declaration is a claim, never conformance proof. Caller override cannot turn a blocked result into a Plan. TASK-039 is not an admitted success path.
