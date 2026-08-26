# BCRP Lifecycle Authority and Legacy Compatibility Contract

Status: accepted
Version: 1.0.0
Date: 2026-07-16
Task: TASK-047

## 1. Purpose

This contract removes the accidental parallel approval/promotion path introduced by TASK-046. It defines exactly one current operational lifecycle authority and a one-way, fail-closed representation boundary from already-governed legacy lifecycle evidence into BCRP.

It does not authorize native BCRP governance, renderer planning, rendering, publication release, artifact production, manifests, AtlasForge integration, or migration of the legacy runtime.

## 2. Sole operational authority

The existing governed BriefForge runtime lifecycle is the sole current operational approval and promotion authority:

1. `validate_candidate_presentation_package(...)` produces the governed legacy `ValidationJudgment` under `briefforge-constitutional-validation-policy:v1`.
2. `promote_candidate_presentation_package(...)` verifies successful Judgment, policy identity, exact Candidate identity, and recomputed legacy semantic fingerprint before producing legacy `ReadyPresentationPackage`.
3. The authority is policy-backed and system-enforced. Historical evidence contains no human validator identity; none may be invented.

BCRP does not currently own an independent approval or promotion authority. Native BCRP authority requires a future accepted governance decision.

## 3. Technical validation is not Judgment

BCRP L0-L2 validation is technical evidence only. Its result must preserve:

- exact Candidate identity and BCRP candidate-semantic fingerprint when canonicalizable;
- every finding and executed layer;
- technical pass/fail status.

Technical success does not establish governance approval, cannot produce a successful `ValidationJudgmentRecord`, and cannot authorize Ready. Negative findings remain technical findings; they are not misrepresented as a governed lifecycle Judgment.

An authority-free BCRP `ValidationJudgmentRecord` or `ReadyPresentationPackageRecord`, even if structurally valid, is ungoverned and downstream-ineligible.

## 4. Compatibility direction and non-authority

The adapter is one-way:

```text
verified legacy Candidate + Judgment + Ready
+ explicit BCRP Candidate closure
+ explicit governed mapping material
-> mapped BCRP Judgment + mapped BCRP Ready representation
```

The adapter grants no authority. It verifies and represents authority already established by the legacy lifecycle. It never converts BCRP technical validation into approval and never maps BCRP back into legacy authority.

## 5. Required input evidence

A mapping attempt requires all of the following, supplied explicitly:

1. one exact legacy `CandidatePresentationPackage`;
2. one exact legacy `ValidationJudgment`;
3. one exact legacy `ReadyPresentationPackage`;
4. one BCRP bundle containing exactly one Brief, one Portable Material, and one Candidate and no lifecycle/release/renderer/artifact/manifest records;
5. explicit identities for the mapped BCRP Judgment and Ready;
6. explicit legacy evidence identities for Candidate, Judgment, and Ready;
7. explicit validation and readiness timestamps with offsets, traceable to governed evidence rather than guessed from unrelated generation metadata;
8. one complete-scope lifecycle evidence inventory declaration: scope identity, Candidate/Judgment/Ready evidence identities, `inventory_complete=true`, an explicit empty competitor list, and a deterministic inventory digest;
9. one mapping attestation identity, attestation time, and attesting BCRP validation-authority identity, with attestation time not earlier than readiness;
10. the accepted policy translation from legacy `briefforge-constitutional-validation-policy:v1` to BCRP `bcrp-legacy-compatibility-policy:1.0.0`;
11. one explicit BCRP authority identity whose authored object has role `validation-authority` and owner `project:BriefForge`;
12. explicit identity mapping between legacy Candidate package identity and BCRP Candidate, mapped Judgment, and mapped Ready identities;
13. explicitly asserted legacy and BCRP candidate fingerprint values in their separate named domains;
14. an explicit declaration that all BCRP-required Brief, material, statement, section, value, obligation, fallback, and related semantics were authored rather than inferred.

Absence is failure. The adapter does not default, infer, repair, synthesize, or search for any item.

## 6. Exact legacy closure verification

The adapter must verify all of these conditions independently:

- the supplied objects have the exact legacy runtime types;
- the Ready object's Candidate equals the separately supplied Candidate;
- the Ready object's Judgment equals the separately supplied Judgment;
- the Judgment is successful and finding-free;
- Candidate package identity equals Judgment candidate identity;
- the legacy Candidate semantic fingerprint is recomputed from the supplied Candidate;
- recomputed fingerprint equals Judgment fingerprint, Ready fingerprint, and the explicitly declared legacy-domain digest;
- Judgment, Ready, and translation use one exact legacy policy identity;
- no competing lifecycle record is present;
- validation time does not follow readiness time;
- no Candidate semantic drift occurred after Judgment or before Ready.

Any disagreement is stale, incomplete, ambiguous, or competing evidence and fails closed.

## 7. BCRP closure and explicit material verification

The adapter must:

- execute BCRP L0-L2 technical validation and reject any blocking finding;
- recompute the exact BCRP `candidate-semantic` fingerprint;
- require the explicit BCRP fingerprint declaration to match it;
- require exact legacy-to-BCRP Candidate identity mapping;
- verify the declared BCRP authority identity exists in the Candidate closure's authored authority material;
- reject empty or false semantic-completeness declarations;
- reject any pre-existing BCRP Judgment, Ready, Release, renderer, artifact, conformance, or manifest record;
- reject post-verification BCRP mutation by binding mapped records to the recomputed Candidate fingerprint.

No semantic parity between the legacy Candidate and BCRP Candidate is inferred. The explicit mapping material is the governed assertion of relationship; technical validation proves only that the BCRP side is internally admissible.

## 8. Policy identity and authority representation

Legacy policy and BCRP policy identities are explicit and non-equivalent. TASK-047 accepts exactly one current translation:

- legacy policy: `briefforge-constitutional-validation-policy:v1`;
- BCRP compatibility policy: `bcrp-legacy-compatibility-policy:1.0.0`;
- authority basis: `policy-backed-system`;
- BCRP authority owner: `project:BriefForge`;
- BCRP authority role: `validation-authority`.

BriefForge accepts a trusted in-process/accepted-artifact boundary for this bounded adapter. Governance provenance is therefore an input precondition: the caller or accepted artifact boundary must supply genuinely governed evidence. The complete-scope inventory and mapping attestation are explicit input material, and their deterministic digest binds evidence identities, lifecycle times, legacy digest, policy, scope, and competitor inventory. The digest detects mutation and inconsistency; it is not a digital signature and does not authenticate an otherwise untrusted issuer. The adapter verifies closure, consistency, policy, authority representation, and binding only. Authenticated issuance, if later required, must consume a separately governed attestation artifact or trusted issuer boundary rather than inventing a signature, timestamp, or token here.

Any other translation, blank identity, non-system authority basis, wrong authority role/owner, missing attestation, or an authority identity absent from the BCRP closure fails closed. No person identity is inferred.

## 9. Fingerprint domains and lineage

Legacy and BCRP fingerprints are intentionally separate:

- legacy domain: `legacy-candidate-semantic` using legacy runtime canonicalization;
- BCRP domain: `candidate-semantic` under the BCRP profile/canonicalization declaration.

The values must never be compared for equality as if they shared a digest domain. A mapped record preserves both domain names and digests and states the relationship as `explicit-governed-mapping`, not semantic/byte equality.

## 10. BCRP representation mechanism

No new record kind or BCRP breaking change is required. The accepted BCRP extension envelope represents compatibility authority and lineage.

Mapped Judgment and Ready records use existing BCRP kinds and carry a semantic, must-preserve extension:

- owner namespace: `briefforge-legacy-lifecycle-compatibility`;
- name: `governed-lifecycle-lineage`;
- version: `1.0.0`;
- scope: `legacy-to-bcrp-lifecycle-representation`;
- criticality: `required`;
- validation contract: `briefforge:legacy-lifecycle-compatibility:1.0.0`, intentionally unsupported by generic BCRP validation;
- authority reference: exact authored BCRP authority identity;
- preservation: `must-preserve`.

The compatibility module owns the exact payload contract. Unknown/missing payload fields, cross-record disagreement, wrong authority role, stale inventory digest, or unsupported policy translation reject mapping. Generic `validate_bundle(...)` must reject these mapped records because it does not support the required compatibility contract. Only `verify_mapped_legacy_ready(...)` may recognize the two expected unknown-required-extension findings, validate the complete compatibility contract, and return an eligible mapped closure. This makes compatibility opt-in and fail-closed rather than permitting generic BCRP processing to mistake mapped core kinds for native authority.

## 11. Mapped status and downstream eligibility

A successfully mapped `ReadyPresentationPackageRecord` has status `mapped-governed-ready-representation` within its extension payload.

It is:

- evidence that an exact legacy governed Ready closure was verified and represented;
- eligible only for BCRP consumers that explicitly verify this compatibility extension;
- not a replacement legacy `ReadyPresentationPackage` for existing legacy downstream code;
- not Publication Release;
- not renderer compatibility, selection, invocation, artifact, conformance, manifest, distribution, or catalogue authority.

An authority-free native BCRP Ready record has status `ungoverned-native-record` by policy and is downstream-ineligible even if structurally valid.

## 12. Historical missing data

Missing historical timestamps, evidence identities, or authority fields cannot be reconstructed from filesystem mtimes, report creation prose, renderer metadata, current time, or convenient defaults. They may be supplied only by separately governed evidence that actually establishes them.

If actual historical TASK-039 evidence lacks required lifecycle timestamps or evidence identities, TASK-039 mapping fails closed. That result does not invalidate the historical legacy lifecycle; it means the evidence cannot support a truthful BCRP compatibility representation under this contract.

## 13. Failure behavior

The adapter raises one explicit compatibility rejection and emits no partial Judgment or Ready when evidence is:

- unsuccessful;
- stale or drifted;
- missing timestamps, identities, policy translation, authority, semantics, or fingerprints;
- ambiguous or competing;
- internally contradictory;
- BCRP-invalid;
- already lifecycle-bearing;
- based on unknown policy translation;
- based on equal-domain fingerprint assumptions.

Input objects and bundles remain unmodified.

## 14. TASK-039, golden corpus, and native authoring distinctions

The three exercises answer different questions:

1. Actual TASK-039 Candidate/Judgment/Ready proves historical legacy lifecycle evidence only. It maps only if all contract evidence exists.
2. Golden case 1 proves accepted BCRP semantic/profile behavior; it is not historical lifecycle evidence.
3. TASK-046 native authoring proves explicit BCRP Candidate construction; its L0-L2 success is technical evidence only.

Golden parity and native authoring must never be reported as historical authority inheritance.

## 15. Lifecycle topology after this decision

```text
legacy Candidate
  -> legacy governed Validation Judgment
  -> legacy governed Ready                    [sole current operational authority]
       -> fail-closed compatibility verification
       -> mapped BCRP Judgment representation
       -> mapped BCRP Ready representation    [no new authority]

native BCRP Candidate
  -> L0-L2 technical result only
  -X-> native Judgment/Ready authority
```

A future BCRP-native lifecycle requires an accepted governance decision and must not emerge through convenience APIs.
