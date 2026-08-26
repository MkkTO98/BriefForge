# TASK-050 BCRP Publication Release Authority, Production, and Lifecycle Proof

Date: 2026-07-17
Task: TASK-050
Status: completed
Verdict: **CLEAR TO PROCEED**

## 1. Recovery and baseline

Bounded recovery passed before mutation. BriefForge is intentionally non-Git; no branch, HEAD or remote exists. TASK-050 had no task artifact before activation. The fresh governed pre-task manifest `/tmp/briefforge-before-task050-20260716.json` contained 663 included paths under the established cache/bytecode exclusions. The pre-task full suite passed 239 tests.

No Git initialization, fetch, commit, push, reset, cleanup, network, database, dependency installation or unrelated-file mutation was authorized or performed.

## 2. Phase-1 representation gate

Result: **PASS — proceed with bounded implementation**.

| Required concern | Existing carrier or implementation | Result |
|---|---|---|
| exact admitted input | TASK-047 five-record mapped Ready verifier | reuse |
| Candidate lineage | `candidate-semantic` fingerprint plus BCRP refs | reuse |
| Judgment/Ready closure | exact five-record `profile-instance` fingerprint | added binding, no new kind |
| legacy/BCRP lineage | TASK-047 required compatibility extensions | reuse |
| evidence snapshot | Material snapshot identity/version/content fingerprint plus explicit closed inventory | reuse + exact input contract |
| publication identity/version | existing Release core fields | reuse |
| Release identity/time/state | existing Release identity/core fields | reuse |
| Release policy/authorization | required semantic extension on existing Release | required addition |
| exactly one Release root | existing BCRP L3/L4 topology | reuse |
| post-Release lifecycle | TASK-049 companion `ReleaseBinding` | reuse |
| renderer/artifact/Manifest/distribution execution | later stages | prohibited here |

The evidence closure remains transitively representable through Release -> Ready -> Candidate -> Material. Explicit policy and authorization cannot be represented in existing core Release fields without ambiguity, so one required Release-owned semantic extension is necessary. This is an existing BCRP extension mechanism, not a twelfth record kind or profile-topology change.

## 3. Accepted authority contract

Accepted:

- policy: `briefforge-publication-release-policy:1.0.0`;
- extension validation contract: `briefforge:publication-release-authorization:1.0.0`;
- authority identity: `authority:briefforge-publication-release`;
- owner: `project:BriefForge`;
- role: `publication-release-authority`.

One authorization targets one exact semantic Release act. It binds its own identity/policy/authority/time, publication identity/version, Ready identity, Candidate fingerprint, full governed-Ready closure fingerprint, evidence snapshot identity/version/digest, initial active state, exact Release identity/time, recommendation state, allowed constraints and exact released constraints.

This is an authority-issued governance input at a trusted BriefForge process boundary. TASK-050 verifies exact content and the admitted Material declaration; it does not claim cryptographic authentication, human identity possession or external registry verification.

## 4. Evidence snapshot contract

The immutable snapshot input binds identity, version, scope identity, explicit-offset time, complete-inventory declaration, closed status, deterministically identity-ordered entries, exact `sha256:` entry digests and a recomputed canonical inventory digest.

An explicitly empty inventory is valid only as an authority assertion that the named external-evidence scope contains zero entries. The implementation proves integrity of the supplied closure declaration without external I/O; it does not prove evidence bytes exist. Candidate evidence/provenance obligations remain separately governed.

Material must contain exactly the matching snapshot identity/version and `content_fingerprint == sha256:<inventory_digest>`.

## 5. Implementation

Created `src/briefforge/publication_release.py` with:

- immutable evidence-entry/snapshot and authorization value types;
- deterministic inventory canonicalization/digest;
- exact mapped-Ready admission;
- explicit authority/material/time/constraint verification;
- deterministic production of exactly one `PublicationReleaseRecord`;
- exact persisted six-record verification;
- narrow generic-finding reconciliation;
- immutable serialized verified state with detached bundle/record projections;
- TASK-049 `ReleaseBinding` projection that re-verifies before use.

The producer never creates an event, renderer plan, artifact, conformance record or Manifest. Persisted verification rejects every non-six-record topology, competing Release, downstream record, embedded lifecycle claim, unknown Release/extension/payload field, snapshot drift, authority mismatch, stale fingerprint and unrelated generic finding.

## 6. Adversarial review and corrections

The first independent review found three blocking weaknesses:

1. authorization did not target exact Release identity/time/recommendation state;
2. verified output exposed mutable aliased BCRP objects and lifecycle projection could use stale verification;
3. Release semantics did not directly bind the complete Judgment/Ready compatibility closure.

Corrections:

- exact Release act fields were added to authorization and persisted extension material;
- verified content is stored as immutable deterministic text and only detached copies are exposed;
- lifecycle projection independently re-verifies the stored content and expected fingerprint;
- the exact five-record governed-Ready `profile-instance` fingerprint is authorization-bound and persisted in the Release extension.

A second independent adversarial review returned **PASS** with no remaining blocker or high-severity defect. It also reproduced fail-closed rejection of duplicate accepted authority declarations.

## 7. Test proof

`tests/test_bcrp_publication_release.py` proves:

- two materially different valid production cases;
- deterministic equivalent output;
- exact one-Release topology;
- explicit empty and non-empty evidence inventories;
- snapshot, inventory, Candidate, Judgment, Ready and compatibility drift rejection;
- policy/authority/time/identity/version/constraint mismatch rejection;
- one authorization cannot authorize a different Release act;
- native Ready, mere corpus possession and incomplete historical authority remain insufficient;
- unknown/additional payload fields, extra extensions, competing Releases and downstream records reject;
- generic BCRP reports exactly the three expected unsupported required extensions and still blocks unrelated defects;
- verified-state mutation cannot alter accepted content;
- TASK-049 initial/later lifecycle handling preserves Release identity and `release-semantic` fingerprint;
- no rendering, artifact, Manifest or distribution authority is implied.

## 8. Verification results

Commands ran with bytecode disabled.

- TASK-050 focused: 16 tests, OK.
- TASK-047/TASK-049/TASK-050 focused: 66 tests, OK.
- Full post-continuity suite: 255 tests, OK.
- Fresh `briefforge.bcrp` import: no Release-production or lifecycle module imported; 11 core kinds, OK.
- Architecture-to-reality audit: 0 blocks, 0 warnings; report `artifacts/reports/R-20260717-architecture-reality-audit.md`.
- Context health: 0 blocks, 0 warnings after handoff compaction.
- Coherence: 0 blocks, one intentional Historical Compatibility warning for retained ecosystem/advisory references.
- Bounded recovery: exit 0; reports TASK-050 completed, no active task and CLEAR TO PROCEED.

No check is claimed beyond its actual output.

## 9. Filesystem accounting

The governed pre-close comparison used the same manifest format, root and exclusions as baseline.

- included paths: 663 -> 670;
- additions: 7;
- modifications: 9;
- deletions: 0;
- type changes: 0;
- symlink-target changes: 0.

Added:

- `artifacts/decisions/D-20260716-bcrp-publication-release-authority-and-production.md`
- `artifacts/reports/R-20260716-task-050-bcrp-publication-release-authority-production-and-lifecycle-proof.md`
- `artifacts/reports/R-20260717-architecture-reality-audit.md`
- `artifacts/specifications/publication-release-authority-and-production.md`
- `artifacts/tasks/TASK-050-bcrp-publication-release-authority-production-and-lifecycle-proof.md`
- `src/briefforge/publication_release.py`
- `tests/test_bcrp_publication_release.py`

Modified:

- `artifacts/decisions/_SUMMARY.md`
- `artifacts/reports/_SUMMARY.md`
- `artifacts/specifications/_SUMMARY.md`
- `artifacts/tasks/_SUMMARY.md`
- `context/latest_handoff.md`
- `state/active_goal.md`
- `state/architecture.md`
- `state/project_state.md`
- `state/recent_changes.md`

All paths are TASK-050 implementation, proof, governance or continuity scope. The authoritative post-task manifest is generated after this report as the final repository observation; its digest is returned in the final task response. No unrelated pre-existing path was modified.

## 10. Scope exclusions preserved

No lifecycle-event producer, renderer capability/plan, renderer code/style, HTML/SVG publication, artifact, conformance evidence, Publication Manifest, distribution execution, AtlasForge, upstream project, service, database, network, dependency or financial-domain field was implemented or modified.

## 11. Gate

**CLEAR TO PROCEED**

The repository contains a deterministic, independently verifiable and fail-closed boundary from exact governed Ready to exactly one immutable Release. No unresolved duplication or contradiction blocks the next stage.

Exactly one recommended next task, not activated:

`TASK-051 — BCRP Renderer Compatibility-Plan Production and Fail-Closed Proof`

It is correctly bounded because Release production is now proven, while renderer capability negotiation is the next independently addressable BCRP stage. TASK-051 should consume only an independently verified Release and explicit renderer capability, produce one deterministic compatibility/expression plan, and stop before rendering, artifacts, conformance, Manifest production or distribution.

No commit or push occurred.
