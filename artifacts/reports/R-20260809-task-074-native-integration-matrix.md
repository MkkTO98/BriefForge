# TASK-074 Native Candidate-to-Manifest Integration Matrix

Date: 2026-08-09
Status: source/contract trace complete; implementation proof pending

## Route and acceptance matrix

| Boundary | Production owner | Input authority/object | Exact acceptance contract | Output and durability | Native/legacy finding |
|---|---|---|---|---|---|
| Persisted Candidate → governed subject | `briefforge.bcrp_publication_governance.verify_bcrp_publication_subject` | `GovernedCandidateAdmission` plus exact accepted Candidate stage/ledger/authority closure | Exact governed roots, authority and terminal seals, inventory/receipt/validation bytes, Candidate semantic/profile fingerprints, paired semantics, scope and chronology | `VerifiedGovernedCandidate`; input evidence is durable, verified object is process-local | TASK-073 fixture manually constructs the admission. No public accepted-authoring-recovery → first-Judgment admission bridge exists. |
| Candidate → Judgment | `produce_native_judgment` / `verify_native_judgment` | Verified governed Candidate plus isolated Judgment authorization/token | Independent technical eligibility and governance decision; reserve/commit authority semantics; exact Candidate closure and decision evidence | Six-record predecessor through Judgment; persisted Judgment authority/ledger evidence | Native TASK-073 authority. Production-inaccessible root substitution is the accepted TASK-070/TASK-073 test seam. |
| Judgment → Ready | `produce_native_ready` / `verify_native_ready` | Exact verified Judgment plus Ready authorization/token | Reauthenticates governed Candidate and Judgment; reserve/commit; exact closure and chronology | Ready closure and persisted Ready authority/ledger evidence | Native TASK-073 authority. |
| Ready → native Release | `bcrp_publication_release_v2.produce_native_publication_release` | Exact `VerifiedNativeReady`, `EvidenceSnapshot`, native Release authorization | Exact six-record Candidate/Judgment/Ready closure, publication identity/version/time, evidence snapshot and authorization | `VerifiedPublicationRelease`; canonical six-record bytes retained process-locally and in returned bundle | Native-v2 Release family selected by exact extension. |
| Release → compatibility Plan | `bcrp_renderer_compatibility_planning_v2.produce_renderer_compatibility_plan` | Exact verified Release, snapshot, planning scope, capability declaration and planning authorization | Re-verifies Release; produces and re-verifies exact eight-record closure; canonical byte replay | `VerifiedRendererCompatibilityPlan`; detached canonical eight-record bundle | Planner reads legacy Candidate `renderer_requirements`/`fallbacks`, not paired extension semantics. TASK-071-shaped paired Candidates may therefore produce empty mappings despite nonempty paired requirements. |
| Release + Plan → native paired token | `bcrp_paired_terminal_admission.verify_native_bcrp_paired_terminal_admission` | Supplied native Release and Plan | Exact family dispatch; independent Release/Plan verification; supplied six Release records must equal Plan-embedded six records byte-for-byte and by fingerprint; exact authority inventory and paired semantics | `PairedUpstreamAdmissionToken`, frozen seal plus native weak-registry provenance; process-local only | Native objects are adapted only into frozen verifier DTO views; BCRP bytes are not rewritten. Unknown/mixed families fail closed. |
| Token → projection | `briefforge_paired_terminal_profile.projection.build_paired_editorial_projection` | Issuer-tracked paired token | Revalidates issuer-held token state and reconstructs semantics from the exact Candidate sealed in the admitted Release/Plan prefix | `PairedEditorialProjection`; optional canonical persisted projection evidence in an exclusive empty directory | Projection accepts generic frozen paired tokens; native provenance must be reasserted by an additive native bridge. Candidate identity is indirect through exact prefix/fingerprints. |
| Projection → controlled renderer | `bcrp_paired_terminal_admission.invoke_native_bcrp_controlled_paired_renderer` → frozen `invoke_controlled_paired_renderer` | Native token, exact projection, persisted projection evidence, exact invocation authorization | Native weak-registry provenance first; then exact projection/token/evidence/authorization bindings, canonical absolute pairwise-distinct empty directories, implementation digest, one-act authorization marker | Permanent authorization-consumption marker, HTML artifact, invocation evidence; all exclusive, fsynced and inode-bound | TASK-073 positive mocked the frozen invocation. Frozen token validation is repeatable; authorization marker—not token—was historically single-use. TASK-074 must add native token invocation consumption without modifying frozen code. |
| Rendering → conformance | `assess_persisted_paired_semantic_artifact_conformance` | Exact token, admitted semantics, projection evidence, verified invocation, invocation and conformance authorizations, canonical evidence path | Rebuilds projection from issuer-held semantics; reloads invocation evidence/artifact; independently parses exact HTML; binds all fingerprints, implementation digests, bytes and chronology | Exclusive fsynced `paired-semantic-conformance-evidence.json`; verified DTO process-local | Frozen implementation accepts any valid paired token; native wrapper must reassert native provenance. Authorization is path-unbound and reusable in another fresh caller-selected directory. |
| Conformance → ten-record predecessor | No production paired/native bridge currently exists | Verified invocation and conformance persisted evidence | Required records are `GeneratedArtifactAuditRecord` and `SemanticArtifactConformanceRecord` linked to exact Candidate→Release→Plan closure | TASK-067 test fixture fabricates the two records; no production output | Concrete implementation gap. Additive native bridge must derive records exclusively from independently reloaded production evidence and reject caller records. |
| Ten-record predecessor → Manifest | `briefforge_paired_terminal_profile.manifest_admission.produce_paired_terminal_publication_manifest` | Exact ten-record predecessor, token, projection, persisted invocation/conformance, exact artifact admission and Manifest authorization | First eight records equal token-sealed Plan prefix; exact Candidate/Judgment/Ready/Release/Plan/Audit/Conformance lineage; exact artifact path/bytes/fingerprints; 17 capabilities; chronology; authorization reserve/commit | Canonical persisted `publication-manifest.json`, consumption and commitment records; independently reloadable | Frozen paired Manifest contract is usable only after the missing predecessor bridge. Native provenance must be reasserted before entry. No distribution/deployment authority is granted. |
| Manifest selector | `briefforge_terminal_profile.manifest_admission.verify_persisted_publication_manifest` | Exact invocation/conformance/Manifest class tuple | Fixed exact-type dispatch to four historical profiles; no subclass/plugin/fallback | Verified persisted Manifest | Native upstream converges on paired v3 contract; selector itself does not encode native issuer provenance. |

## Identity and byte continuity

1. Candidate identity and semantic/profile fingerprints originate in the persisted governed Candidate closure.
2. Judgment and Ready retain and reauthenticate that exact closure.
3. Native Release retains exactly six BCRP records and binds publication/evidence identities.
4. Compatibility Plan retains those exact six records and appends declaration and Plan records.
5. Native admission compares the supplied Release against the Plan-embedded six records using canonical serialized bytes and profile-instance fingerprints.
6. The paired token seals all eight Plan documents, Release/Plan/declaration/profile identities, paired semantic closure, authority inventory, capability tuple and a process-local issuer nonce.
7. Projection is constructed only from issuer-held token semantics and carries Release, lifecycle, Plan, declaration, profile/schema and implementation bindings.
8. Invocation authorization and persisted evidence bind the projection, renderer implementation digest, canonical paths, inode identities and exact artifact bytes.
9. Conformance independently reconstructs the projection, reloads persisted invocation evidence and artifact bytes, and binds the semantic report to them.
10. Manifest must bind the exact ten-record predecessor, persisted invocation and conformance evidence, and exact artifact inventory.

## Durable boundaries and interruption points

| Point | Durable state | Retry/recovery result before TASK-074 correction |
|---|---|---|
| Before Judgment/Ready reserve | None | Safe retry. |
| After Judgment/Ready reserve, before commit | Reservation evidence | Ordinary failure releases; interruption semantics handled by TASK-073 reserve/commit design. |
| After Judgment/Ready commit | Consumed authority and lifecycle evidence | Replay rejected. |
| Native token issuance | None; weak registries and nonce are process-local | Cannot reconstruct after process exit. |
| Projection evidence write | Final-name exclusive file | No transaction; partial final-name file can remain on interruption. |
| Before invocation marker | No invocation-owned durable state | Safe retry if admitted directories remain empty. |
| After invocation marker, before artifact/evidence closure | Permanent marker, possibly partial artifact/evidence | Authorization replay rejected; ordinary failures remove owned artifact/evidence but retain marker; `BaseException`/crash can leave partial files. |
| After complete invocation | Marker, artifact, invocation evidence | Reload requires original process-local token. |
| Conformance evidence write | Final-name exclusive evidence | Same authorization can be used in a different fresh directory; interruption can leave partial final-name evidence. |
| Manifest reserve/commit | Durable consumption, evidence and external commitment | Existing paired transaction provides replay rejection and reload. |

## Authenticated defects to test and bound

1. TASK-073's native controlled-invocation positive was a mock-only call-site proof.
2. Native-v2 planning does not cross-bind paired extension renderer requirements to Plan mappings.
3. The native paired token is not single-use; historical `consume_*` is an integrity verifier, while the invocation authorization marker is the only one-act control.
4. Native issuer provenance is checked only by the optional invocation wrapper, not by projection, conformance or Manifest.
5. No production paired/native bridge derives the required Audit and Conformance BCRP records from actual persisted rendering/conformance evidence.
6. No public production bridge recovers the first `GovernedCandidateAdmission` directly from an accepted authoring closure.
7. Invocation and projection/conformance persistence use final-name exclusive writes without process-crash reconciliation; process-local tokens also prevent cross-process reload.

## Bounded correction decision

TASK-074 may add native wrappers/adapters outside frozen TASK-060/TASK-062/TASK-067 files to:

- enforce native provenance at projection, invocation, conformance and Manifest entry;
- reserve and irreversibly consume native token invocation authority exactly once while retaining read-only downstream binding verification;
- derive the two predecessor records only from independently reloaded invocation/conformance evidence;
- cross-bind paired semantic requirements to the native compatibility Plan without altering Candidate or Release bytes;
- expose a source-neutral accepted-Candidate recovery bridge if it can be implemented from existing exact persisted evidence;
- reconcile or explicitly classify interruption states without weakening frozen behavior.

If these require modifying frozen bytes, creating parallel authorities, or reconstructing unavailable evidence, TASK-074 must stop and rule the real successor not ready.
