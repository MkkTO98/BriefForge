# Decision: BCRP Publication Release Authority and Production

Date: 2026-07-16
Status: accepted
Task: TASK-050

## Decision

Adopt `briefforge-publication-release-policy:1.0.0` and `briefforge:publication-release-authorization:1.0.0` as the sole initial TASK-050 policy and required Release-authorization extension contract.

One publication act accepts exactly one TASK-047-verified five-record governed BCRP Ready closure and creates exactly one immutable core `PublicationReleaseRecord`. The Release extension is part of the existing `release-semantic` fingerprint; no record kind or BCRP profile topology is added.

## Authority

The accepted authority is a policy-backed BriefForge system role:

- identity: `authority:briefforge-publication-release`;
- owner: `project:BriefForge`;
- role: `publication-release-authority`.

No human approver, digital signature, external authentication or identity-possession claim is invented. `PublicationReleaseAuthorization` is an authority-issued governance input whose caller is already inside the accepted BriefForge Release-authority process boundary. TASK-050 verifies exact content and the admitted Material declaration; an external deployment that needs cryptographic provenance requires a separately governed verifier.

Authorization must exactly bind its own identity, policy, authority triple, time, publication identity/version, Ready identity, Candidate semantic fingerprint, exact five-record governed-Ready `profile-instance` fingerprint, evidence-snapshot identity/version/inventory digest, initial `active` state, exact Release identity/time/recommendation state, the exact released constraints, and a closed allowed constraint set. The released constraints must be an exact authorization target and a non-empty subset of the allowed set.

## Evidence closure

The explicit snapshot input has identity, version, scope identity, canonical snapshot time, complete-inventory declaration, closed status, deterministically ordered evidence/material identity+digest entries, and deterministic inventory digest. Empty inventory is valid only as an explicit authority assertion that the named external-evidence scope is complete with zero entries; this module proves the declaration's integrity, not existence of external bytes, while BCRP evidence/provenance obligations remain governed in the exact Candidate closure.

The existing BCRP chain binds the closure without a new evidence record:

```text
Release ready_ref/ready_fingerprint
-> Ready candidate fingerprint
-> Candidate transitive Material semantics
-> Material evidence snapshot identity/version/content fingerprint
```

The authorization extension additionally binds the admitted snapshot identity/version/digest. The producer never fetches, refreshes, infers, repairs or mutates evidence.

## Dedicated validation

Generic BCRP continues to reject the TASK-047 Judgment/Ready required extensions and the TASK-050 Release required extension. The dedicated path:

1. verifies the exact five-record TASK-047 closure unchanged;
2. verifies the exact Release extension and snapshot/authorization material;
3. runs generic BCRP through L4;
4. reconciles only the three exact already-verified unsupported-extension findings;
5. preserves and blocks on every unrelated finding.

It claims no L5/L6, renderer, artifact, conformance, Manifest or distribution authority.

## Lifecycle compatibility

Initial publication is only the immutable Release. TASK-049 receives its exact identity and `release-semantic` fingerprint as an out-of-band `ReleaseBinding`, needs no event for initial state, and cannot mutate the Release. Correction requires a new governed Ready and Release; supersession/withdrawal remain companion events; rerender remains derivative.

## Consequences

- Exactly one unambiguous Release root exists per production act.
- Caller-controlled time, UUID, path, filename, version inference and current-time defaults are prohibited.
- Unknown persisted Release semantic or authorization payload fields fail closed.
- Later external/source change cannot rewrite the fixed historical Release; changed semantics or snapshot cannot reuse its authorization.
