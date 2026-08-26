# Publication Release Authority and Production 1.0

Date: 2026-07-16
Status: accepted specification
Task: TASK-050
Policy: `briefforge-publication-release-policy:1.0.0`
Authorization contract: `briefforge:publication-release-authorization:1.0.0`

## 1. Admitted topology

Input is exactly one TASK-047-verified BCRP Ready closure: Brief, Portable Material, Candidate, mapped governed Judgment, and mapped governed Ready. Output adds exactly one `PublicationReleaseRecord`. Input containing Release, renderer, artifact, conformance, Manifest or other records rejects.

The output executes only BCRP L0–L4 plus the dedicated compatibility, snapshot and Release-authority checks. L5/L6 are not claimed.

## 2. Exact production matrix

| Concern | Required binding | Authority / validation |
|---|---|---|
| admitted stage | exact five-record mapped Ready | TASK-047 verifier |
| Candidate | identity and recomputed `candidate-semantic` digest | TASK-047 + BCRP L2/L3 |
| Judgment and Ready | exact five-record `profile-instance` closure digest, in addition to their governed identities, extensions, policies, times and internal fingerprints | TASK-047 + Release authorization |
| legacy/BCRP lineage | exact compatibility inventory, mapping and both fingerprint domains | TASK-047 required extensions |
| publication | explicit lineage identity and semantic version | Release core + authorization |
| Release | authorization-bound identity/time/recommendation state/constraints; one root; initial `active` | producer + L3/L4 |
| evidence | explicit closed snapshot identity/version/time/scope/inventory/digest | snapshot verifier; Material and authorization binding |
| policy | exact accepted Release policy | authorization extension |
| authority | exact identity/owner/role and Material declaration | authorization verifier |
| authorization | explicit identity/time and exact publication/Ready/Candidate/snapshot bindings | required Release extension |
| distribution | explicit non-empty constraints within authorized closed set | authorization verifier |
| canonical fingerprint | `release-semantic`, rooted at exact Release | BCRP canonicalization |
| lifecycle anchor | exact TASK-049 `ReleaseBinding`; zero initial events | TASK-049 profile |
| not granted | Ready, lifecycle event, renderer, artifact, conformance, Manifest, execution/distribution | explicit exclusions |

## 3. Evidence snapshot

An immutable snapshot contains exactly:

- `identity`;
- `version`;
- `scope_identity`;
- `snapshot_time` with explicit offset;
- `inventory_complete == true`;
- `closure_status == closed`;
- an identity-unique tuple of evidence/material entries, each with exact identity and `sha256:<64 lowercase hex>` digest;
- `inventory_digest`, recomputed from canonical JSON over all preceding snapshot fields and entries sorted by identity.

An explicitly complete empty inventory is admitted when the authority declares that the named external-evidence scope contains no entries. This does not mean that missing required evidence is silently converted to an empty inventory: BCRP evidence/provenance obligations remain governed by the exact Candidate closure. The snapshot contract proves the integrity of the supplied closed inventory and its scope assertion; without external I/O it does not prove existence of evidence bytes. Directory membership, paths, file metadata, current time, acquisition and implicit evidence are never consulted. The matching Material snapshot must have exactly the same identity/version and `content_fingerprint == sha256:<inventory_digest>`.

## 4. Authorization

Immutable authorization contains exactly:

- authorization identity;
- accepted policy identity;
- exact authority identity/owner/role;
- authorization time;
- authorized publication identity/version;
- authorized Ready identity;
- authorized Candidate semantic fingerprint;
- authorized exact five-record governed-Ready `profile-instance` fingerprint;
- authorized evidence snapshot identity/version/inventory digest;
- authorized initial state `active`;
- closed allowed distribution-constraint tuple;
- exact Release identity and canonical time;
- exact Release distribution-constraint tuple;
- exact recommendation-inclusion state.

The authority must be declared in Portable Material with the exact accepted identity/owner/role and release scope. Authorization time cannot precede snapshot or readiness time and cannot follow Release time. One authorization can therefore reproduce only the same semantic Release act; changing identity, time, recommendation state or constraints requires a different authorization.

This is a governance trust boundary, not a cryptographic identity system. `PublicationReleaseAuthorization` is an authority-issued input whose caller is already inside the accepted BriefForge Release-authority boundary. The producer verifies its exact content and admitted-material declaration; it does not authenticate a person, fetch a registry or manufacture authority from Candidate possession. Deployments outside that trusted process boundary would require a separately governed signature or credential verifier, which TASK-050 neither invents nor claims.

## 5. Release record

The core semantic payload has exactly the accepted BCRP Release fields used by this producer: publication lineage/version, Ready reference/fingerprint, one snapshot reference and version mapping, Release authority ref, active lifecycle status, publication time, `distribution_authorized: true`, fixed `distribution_scope: bounded-explicit-constraints`, and explicit recommendation inclusion state.

Exactly one required semantic extension carries the exact authorization material. Its target refs are the Release and Ready identities. Unknown/additional semantic keys, extension keys, payload keys or extra extensions reject.

## 6. Determinism and immutability

All inputs are deep-copied. No input object is modified. Verified output stores the six-record representation as immutable deterministic text and exposes detached bundle/record copies; mutation of a returned copy cannot alter verified state. Lifecycle projection independently re-verifies the stored closure and expected Release fingerprint. All identities, versions and times are explicit. Equivalent explicit semantic inputs produce identical record content and fingerprint. No UUID, current time, file/path name, lexical version or filesystem metadata default exists.

## 7. Independent verification

Verification starts from persisted six-record content and independently:

1. projects and verifies the five-record TASK-047 closure;
2. checks exact record cardinality and no downstream records/events;
3. recomputes Candidate linkage and the exact five-record governed-Ready closure digest;
4. verifies snapshot structure/digest and exact Material binding;
5. verifies the accepted policy/authority/authorization/time/distribution contract;
6. runs generic L0–L4 and permits only the exact three verified required-extension findings;
7. recomputes `release-semantic` fingerprint and, when supplied, requires exact expected digest equality.

## 8. Lifecycle distinctions

- Initial Release: one immutable Release, no event.
- Correction: changed Candidate/Judgment/Ready and a later new Release; no correction producer here.
- Supersession/withdrawal: TASK-049 append-only events; no Release mutation.
- Rerender: derivative and no semantic Release by itself.
- Staleness: pre-production drift blocks; later source change does not rewrite fixed history or authorize changed input.

## 9. Fail-closed and exclusions

All classes listed in TASK-050 fail closed, including native Ready, corpus possession, historical TASK-039 incompleteness, identity/fingerprint/policy/authority/time/snapshot/inventory/constraint mismatch, unknown fields, competing Release roots, tampering, embedded lifecycle claims and implicit downstream authority.

No renderer plan/capability, rendering, HTML/SVG, artifact, conformance, Manifest, distribution execution, AtlasForge, service, database, network or financial-domain behavior is in scope.
