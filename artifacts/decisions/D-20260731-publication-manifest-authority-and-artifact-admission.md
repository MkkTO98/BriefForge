# Decision — Publication Manifest Authority and Artifact Admission

Date: 2026-07-31
Status: Accepted for TASK-054 implementation
Task: TASK-054

## Decision

1. Use the existing core `PublicationManifestRecord` as the sole Manifest carrier. Add no BCRP record kind.
2. A Manifest is an immutable derivative inventory and admission decision for one exact artifact set. It remains subordinate to Release, lifecycle, Plan, capability, invocation, artifact and semantic-conformance authority.
3. The sole accepted policy/profile are:
   - `briefforge-publication-manifest-admission-policy:1.0.0`;
   - `briefforge-publication-manifest-admission-profile:1.0.0`;
   - specialized required extension contract `briefforge:publication-manifest-admission-authority:1.0.0`.
4. Manifest-projector authority must exist exactly once in independently verified released material with role `publication-manifest-projector` and scope `one-publication-manifest-production`. Caller assertions cannot supply it after Release.
5. One authorization is bound to one exact Manifest record identity, implementation, output location, ten-record predecessor closure and canonical ordered artifact inventory. It is consumed before production and cannot be replayed.
6. The producer must call the authoritative persisted TASK-053 verifier immediately before admission. Status labels are not authority.
7. The expected artifact set is authorization-derived; filesystem enumeration cannot define admission.
8. The specialized verifier may reconcile only exact generic unknown-required-extension findings for contracts it independently verifies. All other findings remain blocking.
9. Successful admission appends exactly one Manifest to the exact verified ten-record conformance closure. The Manifest adds no Release, lifecycle, conformance, distribution, deployment, successful-publication or AtlasForge authority.
10. Historical evidence is immutable. Later lifecycle events do not rewrite a historical Manifest, but a separate current-eligibility check may reject ordinary downstream use.

## Persistence and trust

Use exclusive canonical writes, file and directory fsync, pre-production authorization consumption, independent reload, an external admission commitment and rollback before the documented commit point. These controls provide deterministic consistency and tamper detection within a trusted process/local-writer model. They are not signatures, human authentication, hostile-code sandboxing, external attestation or WORM storage.

## Consequences

- Semantic conformance is necessary but not sufficient for Manifest admission.
- Manifest existence is not distribution authorization and not proof publication occurred.
- A failed or indeterminate attempt emits findings only and no usable Manifest.
- Exactly 11 BCRP core record kinds remain authoritative.
