# D-20260808 — Source-neutral BCRP publication subject and exact Release–Plan closure

Date: 2026-08-08
Status: **ACCEPTED FOR TASK-073 IMPLEMENTATION**
Scope: TASK-073 only

## Context and authenticated causes

TASK-071 accepted one exact three-record BCRP Candidate. Existing operational Judgment accepts the unrelated legacy runtime `CandidatePresentationPackage`; TASK-047 only maps an already-governed legacy Candidate/Judgment/Ready closure into BCRP. Treating that mapping as native admission would create a second Candidate authority and break identity/byte continuity. Separately, TASK-067 token issuance verifies a supplied Release and a Plan-embedded Release independently without proving equality between them.

## Decision

### One publication-subject architecture

The canonical publication-stage subject is an immutable, source-neutral, versioned verified BCRP publication subject, not a legacy runtime package and not copied semantic content.

For a native BCRP Candidate, the subject is a non-authoritative verified view over the exact canonical BCRP bundle bytes plus an authenticated governed-admission closure. Its only authority is to prove which existing Candidate is being adjudicated. It cannot author, normalize, convert, replace, or independently define Candidate content.

The admission closure binds, and verification recomputes or exact-compares:

- BCRP identity/version and canonicalization;
- Candidate identity and candidate-semantic fingerprint;
- exact `profile.json` bytes as the sole complete reconstructible Candidate representation and their profile-instance fingerprint;
- exact `candidate-semantic.json` equality-evidence bytes, which never become a second semantic authority;
- the historical three-file inventory document (`profile.json`, `candidate-semantic.json`, and `fingerprint.json`) and its exact digest, plus a separately computed complete five-file retained-stage inventory covering those files, `inventory.json`, and `authoring-receipt.json` without altering historical evidence;
- attempt identity, cumulative attempt, accepted terminal state, exact receipt locator/canonical bytes/SHA-256 and cross-bindings, authority digest, and terminal-state/seal digest;
- paired semantic closure;
- source snapshot and blueprint identity/fingerprint;
- exact validation-evidence locator/canonical bytes/SHA-256, validator identity, and accepted technical profile/layers.

The historical receipt and validation-evidence formats do not claim intrinsic evidence-object identities; TASK-073 does not invent them. Filesystem locations are authenticated evidence locators at admission only. They are excluded from Candidate identity and semantic Release authority, and authority is never inferred from location. The view stores detached exact serialized material, exposes detached copies only, and is issued only after exact verification.

### One Judgment/Ready lifecycle

Native BCRP admission and the preserved legacy compatibility admission converge on the same existing BCRP core lifecycle kinds: `ValidationJudgmentRecord`, `ReadyPresentationPackageRecord`, and `PublicationReleaseRecord`. No twelfth core kind and no parallel lifecycle are introduced.

A new exact publication-governance contract `briefforge:bcrp-publication-governance:1.0.0` governs native BCRP Judgment and Ready extensions. Judgment is a separate explicit governance decision (`accepted`, `deferred`, or `rejected`); technical L0–L2/paired acceptance is prerequisite evidence only and never implies publication approval.

An exact immutable Judgment authorization is mandatory. It binds the accepted governance policy/contract, fixed authority identity (`authority:briefforge-publication-judgment`), owner (`project:BriefForge`), role (`publication-judgment-authority`), scope, explicit policy-backed-system trust boundary, authorization/decision identity and canonical time, complete publication-subject closure digest, Candidate identity and candidate-semantic fingerprint, technical validation evidence SHA-256/profile/layers, disposition, and exact rationale/findings. Possession of a subject or caller-supplied disposition grants no authority. The core `ValidationJudgmentRecord.valid` field means affirmative publication-governance acceptance under this contract: `accepted` maps to `true`; `deferred` and `rejected` map to `false`. The specialized verifier alone interprets the required governance extension, and technical validity cannot set `valid=true`.

Judgment binds the complete Candidate subject closure. Ready requires an affirmative Judgment and a separate exact readiness authorization under fixed BriefForge publication-readiness authority, and binds the exact Candidate and Judgment closure. Both retain canonical detached bytes and reject mutation, substitution, unsupported profiles, mixed extension families, and stale evidence.

Historical TASK-047 legacy objects remain interpreted only by `briefforge:legacy-lifecycle-compatibility:1.0.0`. They cannot be presented as native BCRP Candidates, and native BCRP Candidates are never converted into legacy packages.

### Versioned Release integration

Historical Publication Release authorization `1.0.0` remains unchanged and legacy-specific. Native governed BCRP Ready closure uses an additive, exact v2 authorization contract under the same Release-first terminal authority. The v2 Release extension explicitly binds Candidate identity, complete subject closure, Judgment identity/fingerprint, Ready identity/fingerprint, governed Ready closure, evidence snapshot, publication/release identity and version, capabilities/boundaries, and authority constraints. Verification dispatches only by the exact recognized extension tuple and rejects unknown or mixed versions.

Downstream lifecycle, Plan, token, projection, rendering, conformance, and Manifest continue to consume the single `VerifiedPublicationRelease` abstraction and the exact six-record Release closure. Production projection remains reconstructible solely from the Candidate records bound inside that verified Release; no caller DTO becomes semantic authority.

### Exact Release–Plan relation

Before token issuance, the issuer must recover exactly the six required Release records embedded in the independently verified Plan and reconstruct their six-record bundle with the exact profile identity/version. It must require byte-for-byte equality between that bundle's deterministic persisted serialization and the immutable serialized Release representation held by the separately supplied `VerifiedPublicationRelease`; it must additionally require canonical profile-instance equality and exact agreement of Release identity/fingerprint and all derivative publication, Candidate, Judgment, Ready, snapshot, profile/version, capability, path, and Plan bindings already validated by their contracts. Any mismatch rejects before token construction. Binding is unidirectional (`Plan -> exact Release`); Release does not back-reference a later Plan.

The process-local token binds one equality-proven Release–Plan closure. Constructor opacity, non-copyability, non-serializability, state seal, nonce, and downstream exact-envelope checks remain unchanged. Token material is not persisted or exposed.

## Compatibility and recovery

- Historical legacy objects verify under their recorded v1 contracts only; no retroactive native binding is claimed.
- Historical BCRP Candidates may enter native publication governance only when their complete governed admission closure is supported and reauthenticated read-only.
- Unknown Candidate/source/profile/contract versions fail closed; future profiles require an explicit versioned verifier, not fallback.
- Interrupted pure Judgment/Ready/Release construction returns no partial verified object and consumes no single-use authority.
- Recovery reauthenticates canonical bytes and evidence; it never reconstructs content, translates to legacy, repeats a single-use operation, infers approval from technical validation, or upgrades old objects without governed migration evidence.
- Existing Plans/Releases lacking exact cross-binding are reverified under their historical interpretation but cannot obtain a new paired token unless the issuer can prove exact current Release–Plan closure.

## Alternatives rejected

1. Convert the BCRP Candidate into `CandidatePresentationPackage`: rejected as reauthoring and dual authority.
2. Treat L0–L2 acceptance as Judgment: rejected because technical validity is not governance approval.
3. Broaden TASK-047 legacy extensions in place: rejected as false historical interpretation.
4. Add separate native Judgment/Ready/Release object kinds: rejected as a parallel lifecycle.
5. Add a generic registry/plugin/service/database: rejected as speculative and unnecessary.
6. Compare only Release identity, Candidate, or root fingerprint at token issuance: rejected because independently valid mixed closures can share those public fields.

## Consequences

TASK-073 may implement the bounded native subject/Judgment/Ready and v2 Release path using synthetic governed fixtures, preserve legacy v1 unchanged, and harden token issuance. TASK-073 must not invoke this authority on TASK-071 or create any real lifecycle object. A successor may be recommended only after independent review and complete verification establish exact reconstructibility and no remaining authority gap.
