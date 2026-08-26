# Publication Manifest Authority and Artifact-Admission Specification

Version: 1.0.0
Status: accepted for TASK-054 implementation
Policy: `briefforge-publication-manifest-admission-policy:1.0.0`
Profile: `briefforge-publication-manifest-admission-profile:1.0.0`
Extension contract: `briefforge:publication-manifest-admission-authority:1.0.0`

## Claim

A conforming Manifest proves that one exact ordered artifact inventory, independently derived from governed authorization and exact persisted predecessor evidence, was admitted into one immutable publication set. It proves no distribution, deployment or successful publication.

## Required authority chain

Immediately before production the implementation must independently verify:

1. governed Ready and immutable Publication Release;
2. complete lifecycle scope and unique current active Release;
3. exact compatibility Plan/capability and complete nonblocking mappings;
4. controlled invocation authorization, exact artifact bytes/evidence and external commitment;
5. semantic-conformance authorization consumption, profile/assessor applicability, complete requirement outcomes, passing verdict, audit links, persisted evidence and commitment;
6. Manifest-projector authority released before Release;
7. one exact unused Manifest authorization.

## Authorization

The authorization binds identity/fingerprint, policy/profile, authority identity/owner/role/time, Release and lifecycle scope, Plan/capability/renderer, invocation authorization/evidence, conformance authorization/profile/assessor/evidence/verdict, ordered artifact inventory/set fingerprint, allowed Manifest identity/version/implementation/output filename and directory, and explicit authority exclusions.

Authorization is consumed with exclusive persistence before Manifest derivation. Replay/concurrent reuse blocks. Crash after consumption leaves the act consumed and no implicit retry authority.

## Artifact inventory

Each entry has a stable identity, governed role, safe logical filename, media type, exact byte length/digest, order, Release/Plan/renderer/invocation/conformance bindings and optional dependency identities. The expected set comes only from authorization plus verified evidence.

Reject omission, extras, duplicate identities/roles/filenames/order, conflicting roles, unsafe separators, absolute/traversal paths, normalization or case collisions, symlinks, changed bytes/metadata and cross-authority mixing. Ordering is explicit and canonical, never filesystem-derived.

The current production path admits one HTML artifact. The inventory verifier is generic over a bounded in-memory multi-artifact set, without adding a renderer/output format or scanning a directory.

## Manifest representation

Append exactly one core `PublicationManifestRecord` to the exact verified ten-record conformance bundle. Core semantics bind the Release, immutable issuance lifecycle status, exact artifact-audit and conformance references, policy/profile/version/time and deterministic catalog fields. One required semantic must-preserve specialized extension carries exact authority, lifecycle-scope, predecessor-closure, artifact-inventory, audit-link, complete-outcome, persistence and non-authority bindings.

The extension elaborates and cross-checks core meaning; it never overrides it. Generic validation remains fail closed and only the exact independently verified extension-boundary finding may be reconciled.

## Complete findings

Every applicable requirement has exactly one stable outcome. Blocking outcomes distinguish missing, duplicate, contradictory, stale, malformed, unauthorized, indeterminate and unsupported conditions. No caller override/suppression exists. Approval requires all outcomes conformant.

## Persistence

Persist canonical Manifest evidence and an external admission commitment using exclusive regular-file writes, no symlinks, bounded filenames, file and directory fsync and independent reload. Verify canonical bytes, implementation identity, authorization consumption, complete predecessor closure, Manifest fingerprint, artifact inventory and commitment. Pre-commit failures remove partial output; no staging/orphan residue is permitted.

## Current eligibility

Historical Manifest bytes are immutable. A later lifecycle scope may make current downstream use ineligible when the bound Release is no longer unique/current/active. This eligibility decision does not rewrite the Manifest and grants no distribution authority.

## Explicit non-authority

The record and verifier must state:

- `distribution_authority = absent`;
- `distribution_execution = not-performed`;
- `successful_publication = not-asserted`;
- `atlasforge_authority = absent`;
- no browser/deployment/accessibility/editorial/visual/factual-reassessment claim.

## Trust limit

Hashes, canonical fingerprints, exclusive persistence, fsync and commitments provide deterministic consistency/tamper detection under the trusted-process/local-writer model. No signature, authenticated human identity, hostile-code sandbox, external attestation or WORM guarantee is claimed.
