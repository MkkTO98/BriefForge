# Representative Accepted-Chain Authority-Closure Incompatibility

Date: 2026-08-01
Status: accepted pilot finding; no implementation change authorized
Task: TASK-061
Disposition: BLOCKED / NOT RECONCILED — existing capability insufficient

## Decision

Do not execute TASK-061 by classifying TASK-055/056 operational authorities as TASK-060 displayed content authorities. Do not shorten the successful pilot boundary to Manifest v2. Stop before Candidate authoring and accepted-chain invocation.

## Evidence

TASK-060's accepted profile requires exactly five operational Material authorities and explicitly rejects any other operational role or identity. It permits 1–8 separately derived, transitively referenced content authorities. The two classes are disjoint: the five operational identities are planned-zero audit exclusions; content authorities are realized in HTML.

Authoritative locations:

- `artifacts/decisions/D-20260801-task-060-exact-bounds-and-cardinalities.md`
- `artifacts/specifications/representative-projection-content-admission-matrix.md`, especially authority rules and audit-exclusion closure
- `artifacts/specifications/representative-static-html-projection-profile-1.0.0.md`

The terminal accepted chain requires three additional exact operational authorities in the same immutable Release Material inventory:

1. `authority:briefforge-controlled-local-delivery`;
2. `authority:briefforge-bounded-loopback-deployment`;
3. `authority:briefforge-technical-publication-verifier`.

The public delivery, deployment and verification operations fail unless those exact Release-resident authority objects exist with path/inode/route-bound scopes. TASK-059's representative-pilot standard requires one delivery and one TASK-056 observation; TASK-056 remains the terminal accepted technical-publication boundary. Manifest v2 is therefore not a complete successful pilot.

## Implementation discrepancy

`representative_projection.py` recognizes operational authority only by membership in its fixed five-identity tuple. It subtracts those five and treats every remaining authority as content. Therefore the implementation can mechanically accept the three TASK-055/056 operational roles if a caller falsely wires them into displayed semantic edges.

That behavior is under-enforcement, not accepted compatibility. It contradicts the accepted matrix rule “No other operational role or identity is admitted” and would display publication infrastructure as analytical content. TASK-061 forbids modifying a capability to pass and forbids semantic or authority bypasses. The discrepancy was independently reproduced in memory and independently reviewed.

## Additional accepted-API gap

Exact release-authorable scopes are constructible in production only through underscore-prefixed helpers:

- `_released_destination_scope`;
- `_released_loopback_deployment_scope`;
- `_released_technical_verification_scope`.

Historical tests import these internals. Their presence proves implementation mechanics, not an accepted public authoring API. This is secondary to the authority-model contradiction but independently prevents a strict “existing accepted APIs only” pilot.

## Alternatives rejected

- Treat the three operational authorities as content: semantic and authority bypass.
- Omit them: delivery/deployment/TASK-056 reject the Release.
- Stop at Manifest v2 and claim success: incomplete chain.
- Modify TASK-060 classification, TASK-055/056 authority placement or public APIs within TASK-061: explicitly prohibited capability change.
- Use private helpers as if public: does not resolve the normative authority contradiction.

## Consequences

- T-039 source admission passes.
- No Candidate, Ready mapping, Release, Plan, invocation authorization, HTML, conformance evidence, Manifest, delivery, deployment or TASK-056 evidence is created.
- No authorization is consumed and no failed act is hidden.
- Production, tests, fixtures, BCRP and historical artifacts remain unchanged.
- TASK-061 closes `BLOCKED / NOT RECONCILED` with principal reason exactly `existing capability insufficient`.
- No successor is activated. At most one narrow corrective task may be recommended for user decision; it remains unactivated.
