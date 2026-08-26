# D-20260716 BCRP Lifecycle Authority and Legacy Compatibility

Date: 2026-07-16
Status: accepted
Task: TASK-047

## Decision

The existing governed BriefForge Candidate -> Validation Judgment -> Ready runtime remains the sole current operational approval and promotion authority. Its authority is policy-backed and system-enforced under the exact legacy validation policy identity; no human validator identity may be invented when historical evidence contains none.

BCRP L0-L2 execution is technical validation evidence only. Technical success cannot create a successful `ValidationJudgmentRecord` and cannot authorize native BCRP Ready. A native or manually assembled authority-free BCRP Judgment/Ready record remains ungoverned and downstream-ineligible.

An existing governed lifecycle result may be represented in BCRP only through the fail-closed compatibility contract in `artifacts/specifications/bcrp-lifecycle-authority-and-legacy-compatibility.md`. The adapter verifies exact legacy Candidate/Judgment/Ready closure, successful policy-backed Judgment, recomputed legacy fingerprint, explicit BCRP Candidate closure/fingerprint, identity and policy translation, complete authored BCRP material, timestamps, no competing evidence, and no semantic drift. It grants no authority.

Legacy and BCRP fingerprints remain separate named digest domains. Compatibility preserves both values and an explicit lineage assertion; it never compares them as equal-domain hashes.

The existing BCRP extension envelope is sufficient to preserve mapped lifecycle authority and fingerprint lineage. The compatibility extension is required, semantic, and must-preserve; its contract is intentionally unsupported by generic BCRP processing, so ordinary validation blocks rather than ignoring authority-critical meaning. Only the dedicated compatibility verifier may accept the expected required-extension findings and then validate the exact compatibility payload. No new record kind or BCRP 1.0 breaking change is accepted.

BriefForge accepts a trusted in-process/accepted-artifact input boundary for this bounded adapter. Governance provenance is an input precondition. The adapter verifies exact runtime closure, policy, authority role/owner, inventory completeness declaration, timestamps, identities, lineage, deterministic binding, and post-mapping consistency; it does not authenticate an untrusted issuer, and its digest is not a signature. Authenticated issuance would require a separately governed attestation artifact or trusted issuer decision and is not invented here.

A mapped BCRP Ready record represents a verified legacy Ready result only. It does not imply Publication Release, renderer compatibility/invocation, artifact acceptance, manifest authority, distribution authority, or compatibility with existing legacy downstream APIs.

Native BCRP lifecycle authority may be introduced only by a future accepted governance decision.

## Rationale

TASK-041 accepted one readiness lifecycle. TASK-046 accidentally implemented a second executable approval/promotion path by treating technical L0-L2 success as governance Judgment. The smallest correction is not to replace the stable legacy authority, but to make technical evidence non-authoritative and provide one explicit, one-way representation boundary for verified existing authority.

BCRP 1.0 already supports semantic must-preserve extensions and independently scoped fingerprints. Using that mechanism avoids a speculative new record kind or silent change to core semantics.

## Alternatives considered

- Make native BCRP the current authority — rejected; no accepted migration/governance decision or downstream adoption exists.
- Treat technical validation success as governance approval — rejected; it manufactures authority and repeats the TASK-046 defect.
- Compare legacy and BCRP digests directly — rejected; their canonicalization and scope domains differ.
- Infer missing timestamps/identity/semantics from nearby artifacts — rejected; this fabricates historical evidence.
- Add core fields or a new record kind — rejected; the accepted extension envelope is sufficient for bounded compatibility representation.
- Rewrite legacy downstream to consume BCRP — rejected as broad migration outside this task.

## Consequences

- `record_candidate_validation(...)` becomes a technical-result operation and no longer appends lifecycle Judgment.
- Native `promote_validated_candidate(...)` fails closed; mapped Ready is produced only by the compatibility boundary.
- The compatibility module remains outside `briefforge.bcrp`, preserving BCRP core import independence.
- TASK-039 may truthfully fail historical mapping if its evidence lacks required timestamps/identities; golden-case parity cannot fill those gaps.
- Publication and renderer work remain blocked from treating Ready as Release authority.
