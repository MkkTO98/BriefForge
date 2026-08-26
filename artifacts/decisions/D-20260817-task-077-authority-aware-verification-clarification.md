# D-20260817 — TASK-077 Authority-Aware Verification Clarification

Status: **ACCEPTED FOR TASK-077 REMEDIATION**
Date: 2026-08-17
Decision owner: explicit human TASK-077 continuation authority
Scope: TASK-077 verification, remediation, review, and closeout only
Does not modify or supersede: TASK-076 generation-8 contract bytes, TASK-071 authority, prior TASK-077 reports, or the failed historical candidate

## Context

TASK-077's earlier literal requirement that all 63 frozen invalid fixtures reach a downstream semantic owner was overconstrained. An invalid serialized subject must not be admitted past an earlier authoritative production boundary merely to exercise a deeper validator. Such a bypass would weaken the accepted TASK-076 authority architecture and turn hostile data into authority.

This addendum clarifies implementation evidence only. It does not reinterpret explicit TASK-076 wording, weaken conformance, or authorize mutation of any frozen generation-8 artifact.

## Authority-aware evidence taxonomy

Every frozen invalid fixture is classified into exactly one category.

### 1. Semantically representable

The hostile state can be supplied through a lawful production input while valid upstream authority and context remain intact.

Required evidence:

- exercise the first lawful semantic owner;
- assert exact structured exception type, code, owner, and location;
- establish the expected outcome independently of the attacked subject;
- prove every claimed correlated field materially affects the submitted input, independent binding, oracle, or asserted relation.

### 2. Authority-blocked

The hostile bytes must fail at an earlier authoritative boundary and cannot lawfully reach the downstream semantic owner.

Required evidence:

- present the exact hostile serialized subject to the earliest authoritative production owner;
- assert exact structured authority rejection and reason;
- prove the deeper layer is sealed behind the failed authority boundary;
- do not claim unreachable downstream fields were semantically consumed.

### 3. Production-computed or non-input

The hostile state is not a caller-controlled accepted production input. It is fixed by typed constructors, immutable registries, or production derivation rules.

Required evidence:

- prove non-representability through accepted typed APIs and immutable production properties;
- do not manufacture the state with wrong Python types, mutable test switches, monkeypatching, or authority bypasses.

## Current assessed accounting

The current audit classifies the 63 fixtures as:

- 43 semantically representable;
- 17 authority-blocked;
- 3 production-computed or non-input.

The three non-input states are:

- `paired-capability-no-decoder`;
- `traversable-counterpart-proof`;
- `ambiguous-core-locator`.

These counts remain hypotheses until the final trace matrix authenticates every row and exact locator.

## TASK-076 contradiction gate

Before applying the taxonomy to a fixture, inspect its frozen TASK-076 locator.

A genuine contradiction exists if frozen TASK-076 wording explicitly and normatively requires that fixture to:

- reach a named downstream owner;
- emit a specific downstream finding; or
- be representable as an accepted production input,

while the accepted production authority architecture makes that requirement impossible.

If such wording exists, stop and report the exact frozen path, JSON pointer or line, and text. Do not reinterpret it through this clarification.

The initial locator audit found no such contradiction. TASK-076 defines abstract invariant-detector findings and non-authority fixtures; it does not assign production owners, require upstream admission, or require the production exception surface to duplicate the frozen detector code. Structural `expected_reachable` values refer to closure-graph reachability, not production-owner reachability.

## Serialized evidence versus live authority

Capability-v2 and Plan-v2 bytes, issuer DTOs, identities, digests, fingerprints, serialized records, verified objects, and reloaded objects are data or evidence only. They do not confer invocation authority.

The sole permitted live invocation authority remains the existing `NativeBCRPPairedTerminalAdmissionHandle`, issued by its existing canonical owner after authentication of exact process-local registry membership, object identity, issuer family, Candidate and Release binding, Capability and Plan binding, TTL, reservation, consumption, and replay state.

No second handle, registry, sidecar authority, test issuer, generic synthetic-Candidate authority, or reload-based issuance route is authorized.

## Deferred positive integration event

TASK-077 must implement the generation-8 native transition and prove every counterfeit and unauthorized route fails closed. Existing generic native-owner positive behavior must remain verified.

TASK-077 must not execute TASK-071 or manufacture synthetic generation-8 production authority merely to create a positive v2 chain. Real positive generation-8 native issuance and two-live-v2-chain integration evidence that depends on it are reserved for the separately authorized isolated Candidate-to-Manifest proof.

This deferral is acceptable only when it is the sole intentionally unexecuted positive integration event and all other implementation, negative evidence, preservation, verification, freeze, and unanimous-review gates pass.

## Consequences

- Remove every fixture-specific or test-only production authority surface rather than renaming or hiding it.
- Tests may construct non-authority data but may not mint, register, imitate, restore, or reissue production authority.
- The final 63-row matrix must report 43/17/3 categories separately and honestly.
- Earlier failed candidate and review artifacts remain historical and unchanged.
- No governance closeout or reserved final reconciliation is authorized before a new identical-byte candidate obtains three fresh unanimous PASS reviews.
