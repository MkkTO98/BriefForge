# R-20260808 TASK-072 Phase-1 Authority Reconciliation

Status: **BLOCK — STOP BEFORE JUDGMENT**

## Question

Can the exact accepted TASK-071 BCRP Candidate enter the established canonical governed Judgment → Ready → Publication Release route without reauthoring, replacing, converting through an unaccepted bridge, or changing TASK-067 architecture?

## Candidate authentication

Canonical project recovery reported no active task and no overlapping process. Canonical TASK-071 recovery returned `VALIDATED_ACCEPTED` for `candidate:task071-cross-inquiry` without invoking construction. Before/after hashes of all five immutable staging files and the attempt ledger were byte-identical.

Independent replay authenticated:

- 13 immutable source objects and 130 locators;
- blueprint `424fd07da96e1e0914385997dcdb9f4f645f1d6228b4d9f9bb93cfdfbe4689ae`;
- Candidate fingerprint `b1c29473241648c68dfb7bb737715645b396c149094eeb70cef34feb52fb95b2`;
- paired closure `ed0d50ca4633db9d55846af949cfe1f1dc147412aefe0f418710738f69f81df0`;
- physical record order Candidate, Material, Brief;
- 109/109 editorial treatments and topology 6/76/27/5/8/7/14/5.

## Authority authentication

The requested terminal identities match production exactly:

- profile `briefforge:representative-paired-terminal-static-html-profile:3.0.0`;
- projection schema `briefforge:representative-paired-static-html-projection-schema:1.0.0`;
- projection implementation `briefforge_paired_terminal_profile.projection:1.0.0`;
- renderer `briefforge:representative-paired-static-html-renderer:1.0.0`;
- conformance profile `briefforge:representative-paired-static-html-conformance-profile:1.0.0`;
- Manifest contract `briefforge:paired-terminal-publication-manifest-admission-authority:3.0.0`.

The discrepancy is the unestablished predecessor authority.

Accepted decision `D-20260716-bcrp-lifecycle-authority-and-legacy-compatibility.md` lines 9–23 makes the legacy runtime the sole operational Judgment/Ready authority, classifies BCRP L0-L2 as technical evidence only, and requires a future accepted decision for native BCRP lifecycle authority.

Production confirms the decision:

- `src/briefforge/validation.py:37-39` accepts only `CandidatePresentationPackage` and returns a legacy `ValidationJudgment`.
- `src/briefforge/promotion.py:28-31` promotes that same legacy Candidate with its matching Judgment.
- `src/briefforge/bcrp_legacy_compatibility.py:106-135` requires an already governed legacy Candidate/Judgment/Ready plus a separate BCRP Candidate. It maps authority representation one way into BCRP and grants no authority.
- TASK-071's staged object is a canonical three-record BCRP closure, not a legacy runtime Candidate and not a five-record mapped Ready closure.

No accepted deterministic BCRP-to-legacy projection or direct BCRP Judgment API exists. A caller declaration that some separately authored legacy Candidate corresponds to TASK-071 would not prove exact lifecycle governance of the accepted Candidate. It would also breach the explicit no-reauthor/no-replace instruction.

## Additional terminal defect found before invocation

`src/briefforge_paired_terminal_profile/profile.py:536-566` independently verifies the supplied Release and supplied Plan, then builds one admission envelope from the separate Release and Plan results. `_verify_exact_paired_plan` checks paired capability/renderer fields but does not prove that the Plan's embedded six-record Release prefix equals the separately supplied Release used to reconstruct Candidate semantics. No token was issued. This defect is bounded evidence for future correction but does not authorize an architecture change in this task.

## Lifecycle accounting

No lifecycle act beyond read-only recovery and verification occurred:

- Judgment: absent;
- Ready: absent;
- Release: absent; attempts consumed: 0;
- Plan: absent;
- token issuance: absent;
- projection/rendering/conformance/Manifest: absent;
- controlled-invocation marker: absent;
- Manifest authorization consumption: absent.

## Disposition

TASK-072 must stop in Phase 1 and close blocked/not accepted. Correct resolution requires a separate explicit governance decision defining how the already accepted BCRP Candidate itself receives Judgment authority, plus correction and adversarial proof of the Release/Plan cross-binding gap. Neither may be silently invented as TASK-072 implementation detail.
