# TASK-062 Operational-versus-Displayed Authority and Closed Successor Decision

Date: 2026-08-01
Status: accepted and implemented

## Decision

Implement one explicit successor terminal representative profile while preserving TASK-060's profile and executable closure unchanged.

- Profile identity: `briefforge:representative-terminal-static-html-profile:2.0.0`
- Profile version: `2.0.0`
- Relationship: incompatible, explicitly selected successor to TASK-060's representative projection profile `1.0.0`; never inferred from count.
- Content authorities: exactly 1–8, each transitively referenced by governed displayed semantics.
- Operational authorities: exactly one of each of the following eight roles and identities, ordered as listed:
  1. validation;
  2. Publication Release;
  3. controlled renderer invocation;
  4. semantic artifact conformance;
  5. Publication Manifest projection;
  6. controlled local delivery;
  7. bounded loopback deployment;
  8. technical-publication verification.
- Total authority cardinality: exactly 9–16. This is a consequence of the two closed sets, not an open min/max rule.
- Unknown role, unknown identity, duplicate, omission, incorrect owner, incorrect scope, incorrect order, cross-role binding, residual classification, or extension-bag substitution: rejected.

## Why all three terminal authorities belong in Release Material

The accepted TASK-055/TASK-056 implementations independently require each exact declaration in the immutable released Material before issuing an act authorization. Their scopes bind only pre-act facts:

- delivery: exact canonical destination parent/basename and ledger identity;
- deployment: exact fixed loopback target/routes and deployment-ledger identity;
- verification: exact fixed loopback target/routes and verification-ledger identity.

They do not bind delivery evidence, service tokens, deployment receipts, observations, or shutdown evidence. Therefore no circular authority is introduced. Removing Release residency would weaken accepted terminal requirements; adding after Release would violate immutability.

## Producers and consumers

Each declaration is authored before Candidate validation and Release construction through one public profile constructor that delegates to the existing canonical TASK-055/056 scope constructors. The immutable Release fingerprint transitively binds exact object bytes. TASK-055 consumes the delivery declaration; TASK-056 deployment consumes the deployment declaration; TASK-056 technical verification consumes the verification declaration. Each stage recomputes and compares the exact canonical scope and records its own separately issued one-act authorization and consumption evidence.

## Display separation

All eight operational objects are planned-zero exclusions. They cannot be referenced by statements, values, provenance, relations, obligations, distribution display semantics, tables, sections, or requirement authority labels. Renderer and assessor must prove zero realization. Their presence grants no act and asserts no Manifest, delivery, deployment, verification, public reachability, continuing availability, browser behavior, or successful-publication outcome.

## Historical implementation-identity constraint

TASK-060's renderer/assessor digests recursively close over `src/briefforge`. Before any production mutation, preserve all 39 baseline Python files byte-for-byte under `artifacts/source-closures/task060-v1/` with a canonical content-addressed manifest that reproduces the two measured TASK-060 digests. Never label active changed bytes with an archived digest.

The successor uses a BriefForge-owned fixed sibling namespace under `src/briefforge_terminal_profile/` for its profile, projection, adapter, invocation, independent conformance, Manifest facade, and fixed dispatch selector. It may call accepted immutable BCRP/Release/Plan/renderer/terminal APIs.

One narrowly additive production change is authorized in `src/briefforge/publication_distribution_delivery.py`: replace its direct historical Manifest-verifier calls with a closed two-branch selector. The selector is fixed in source, has no registration/callable/import-string surface, derives selection from an exact persisted-evidence and authorization tuple, routes historical tuples to the unchanged verifier and the successor tuple to the successor facade, and rejects every mixed or unknown tuple before verifier entry. TASK-056 modules remain unchanged and continue to consume TASK-055's exact sealed delivery types.

The successor will use:

- the unchanged real representative renderer identity/version and actual active renderer digest;
- a new adapter identity/version/digest and deterministic translation into the exact legacy renderer DTO/routing token while retaining all eight planned-zero exclusions;
- a new projection/profile identity;
- a new assessor implementation identity/version and explicit dependency-aware source closure;
- a Manifest-v2 successor facade that independently verifies the atomic successor tuple and preserves existing artifact-inventory, persistence, and exact-record guarantees;
- existing TASK-055/056 authority and execution semantics unchanged.

Invocation and evidence bind both successor and translated projection fingerprints, adapter identity/version/digest, and actual renderer identity/version/digest. Direct successor DTO routing to the old renderer is rejected. This preserves truthful adapter-versus-renderer identity and prevents mixed-profile substitution.

## Proof boundary

One newly authored synthetic Release must proceed through Candidate, Ready, successor Release, Plan, invocation, deterministic HTML, independent parsed conformance, Manifest v2, accepted delivery, accepted loopback deployment, raw-transport technical verification, persisted reload, deterministic shutdown, and port refusal. TASK-056 remains terminal.

## Rejected alternatives

- Change five to eight in TASK-060 in place: reclassifies history and changes old digests.
- Treat terminal declarations as content: semantic bypass.
- Add generic operational metadata/extensions: open authority bag.
- Inject declarations downstream: violates immutable Release residency.
- Weaken TASK-055/056: reverses accepted authority.
- Modify `src/briefforge` and pin a stale digest: implementation-identity misrepresentation.
