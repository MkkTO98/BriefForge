# TASK-048 — Publication Release Representation-Gap Report

Date: 2026-07-16
Status: complete Phase 1 reconciliation; implementation blocked
Task: `artifacts/tasks/TASK-048-bcrp-publication-release-authority-production-and-lifecycle-proof.md`
Gate: **BLOCKED / NOT RECONCILED**

## 1. Executive finding

TASK-048 cannot proceed to Release authority-contract or source implementation under BCRP 1.0.

The accepted semantics require an immutable `PublicationReleaseRecord` and append-only, attributable later lifecycle events. The executable profile has no independently addressable publication lifecycle-event record. It provides only a `lifecycle_status` field and admits arbitrary embedded `lifecycle_events` inside the Release. Updating either changes the immutable Release and its `release-semantic` fingerprint. A second Release cannot honestly represent withdrawal or staleness, and the executable topology, L3/L4 validators and release fingerprint root assume exactly one Release.

This is a representation/profile gap, not a safe local validator defect. A required extension cannot solve it because there is no immutable later event root to carry that extension. Per TASK-048's explicit stop rule, no production source, validator, Release contract/specification/decision, RED test, renderer code or manifest code was created.

## 2. Recovery and preflight

- Recovery: `PYTHONDONTWRITEBYTECODE=1 python3 -B tools/recover_session.py --project . --json`; exit 0.
- Applicable instructions: root `AGENTS.md`; no nested `AGENTS.md` exists.
- Constitution, work methodology, state, architecture and latest handoff were inspected before repository mutation.
- `TASK-048` had no pre-existing task artifact; its prior occurrences were unactivated recommendations and backlog references.
- Repository boundary: intentionally non-Git; no Git initialization or remote operation was attempted.
- Fresh pre-task manifest: `/tmp/briefforge-before-task048-20260716.json`.
- Included paths: 648.
- Digest reported by the established helper: `89d16086a604434c316ae68052dfa98d282f4f9360fa98949671c93c98e5ef19`.
- Complete pre-mutation suite: 206 tests, OK.

## 3. Evidence inspected

Governance and semantics:

- `CONSTITUTION.md`, especially frozen ownership/non-scope and implementation bridge;
- `artifacts/specifications/publication-boundary-intake-portability-lifecycle.md`, especially §§3.5, 4, 7 and 8;
- `artifacts/specifications/semantic-authority-interaction-and-failure-behaviour.md`;
- `artifacts/specifications/semantic-representation-contract-and-layered-validation.md`, especially §§11.3–11.6 and 13.5;
- `artifacts/specifications/briefforge-core-representation-profile.md`, especially §§6.3, 8, 9, 11, 13 and 14;
- accepted TASK-041 through TASK-047 task, decision, specification and report lineage;
- `artifacts/decisions/D-20260716-bcrp-topology-relationship-and-state-profile.md`;
- `artifacts/specifications/bcrp-lifecycle-authority-and-legacy-compatibility.md` and its accepted decision/report.

Implementation and executable evidence:

- `src/briefforge/bcrp/model.py` record-kind inventory;
- `src/briefforge/bcrp/structure.py` required Release shape and complete-publication cardinality;
- `src/briefforge/bcrp/canonical.py` release domain and exactly-one root behavior;
- `src/briefforge/bcrp/validation.py` L3/L4 release checks;
- `src/briefforge/bcrp/corpus.py` invalid lifecycle mutation;
- `src/briefforge/bcrp_legacy_compatibility.py` exact governed Ready verification and authority exclusions;
- all three accepted `PublicationReleaseRecord` golden fixtures and relevant golden-corpus tests.

## 4. Field-and-authority reconciliation matrix

Primary states mean: **represented**, **partial**, or **gap**. “Represented” does not imply full validation or operational authority.

| Required distinction | Existing carrier and authority | State | Executable evidence and consequence |
|---|---|---|---|
| Publication identity | `PublicationReleaseRecord.semantic.publication_lineage_id`; Release owns publication identity | represented | Required by `src/briefforge/bcrp/structure.py:43-52`; semantics in `publication-boundary-intake-portability-lifecycle.md:92-96`. No publication-specific syntax or uniqueness policy is implemented. |
| Publication semantic version | `semantic_publication_version` | partial | Structurally required at `structure.py:43-52`; semantic version rules are accepted in `publication-boundary-intake-portability-lifecycle.md` §8 but syntax/change/ordering rules are not executable. |
| Release record identity | Root `BCRPRecord.identity` | represented | Independently addressable identity in `model.py:29-38`; generic uniqueness/syntax in `structure.py:129-149`. |
| Exact Ready reference | `ready_ref` and `ready_fingerprint` | represented | L3 compares Release to Ready at `validation.py:295-315`. |
| Candidate/Judgment/Ready lineage | Release → Ready; Ready → Candidate/Judgment | represented for one closure | TASK-047's dedicated verifier establishes governed mapped closure; generic BCRP validity is not lifecycle authority. See `bcrp_legacy_compatibility.py` mapping/verification and `D-20260716-bcrp-lifecycle-authority-and-legacy-compatibility.md`. |
| Admitted governed Ready authority | Required legacy compatibility extension verified only at dedicated boundary | represented conditionally | TASK-047 specification §§5–8. Native Ready, fixtures and generic-validation success remain unauthorized. |
| BCRP Candidate semantic fingerprint | Candidate fingerprint fields plus recomputation | represented | `canonical.py:161-175,248-275`; TASK-047 dedicated verification rejects drift. |
| Legacy/BCRP fingerprint-domain lineage | TASK-047 compatibility payload `fingerprint_lineage` | represented conditionally | Explicit separate domains and governed mapping in `bcrp_legacy_compatibility.py`; not directly carried in Release core semantics. |
| Release-semantic fingerprint | `release-semantic` domain rooted at one Release | partial | `canonical.py:172-175,233-275`. It fingerprints Release substance but requires exactly one Release and does not transitively bind the Ready compatibility extension. |
| Evidence-snapshot identity | `evidence_snapshot_refs` | represented | Structurally required at `structure.py:43-52`. |
| Evidence inventory/version/digest closure | Fixture-only `evidence_snapshot_versions`; material snapshots carry identity/version/fingerprint | partial | L3 checks only declared versions for selected snapshots at `validation.py:311-315`; exact transitive completeness, undeclared additions and one deterministic snapshot digest are not established by current generic validation. |
| Release state | `lifecycle_status` | gap as governed vocabulary | Required string, but no accepted executable vocabulary or transition rules. An unknown value passes when the Manifest agrees. |
| Release time | `publication_time` | partial | Required and UTC-normalizable under `canonical.py`; no L4 ordering rule binds it to Ready/authorization times. |
| Release authority | `release_authority_ref` to an authority object | partial | L4 checks only reference membership at `validation.py:321-335`; it does not enforce release-authority role, owner, scope, authorization identity/time or exact subject. |
| Release policy | No required core field | gap for implementation | Accepted governance requires a named policy, but no core carrier or accepted required extension contract exists. |
| Distribution constraints | Fixture fields `distribution_scope` and `distribution_authorized` | partial | L4 checks truthiness only at `validation.py:328-335`; no exact constraint-set reconciliation or explicit-empty semantics exists. |
| Correction | New governed Candidate/Judgment/Ready and new Release with explicit relationship | partial semantically; gap executable | Accepted at `publication-boundary-intake-portability-lifecycle.md` §8 and `semantic-representation-contract-and-layered-validation.md:511-517`; no concrete correction relation or multi-Release closure validation exists. |
| Supersession | Explicit later relation preserving old Release | gap executable | Accepted doctrine requires explicit lineage, but two Release roots break the one-root fingerprint and complete-publication assumptions. Version order cannot supply authority. |
| Withdrawal | Later attributable event preserving Release | hard gap | Accepted doctrine says later event, no mutation. No lifecycle-event root kind exists in `model.py:14-26`; changing Release status/events mutates its fingerprint. A new Release would falsely assert another publication act. |
| Staleness | Later authority/time/reason preserving historical Release | hard gap | Same missing append-only event carrier as withdrawal. Historical fixed-evidence validity cannot be represented separately from current-use eligibility. |
| Rerender | Later renderer/artifact record; unchanged semantic Release | represented only downstream | `GeneratedArtifactAuditRecord` can later identify a new artifact. TASK-048 correctly excludes production. Rerender must not create or mutate a semantic Release. |
| Extensions | Required/optional semantic/display extension envelope | partial | `structure.py:74-87,258-284` and BCRP profile §13. Suitable for issuance attestations only; cannot create an independent later event by attaching to an immutable Release. |
| Authority explicitly granted | Publication identity/version, fixed Ready/snapshot, release act/status under explicit authority | partial | Semantic ownership exists in TASK-041; executable L4 authority is too weak for production. |
| Authority explicitly not granted | Renderer compatibility/selection, rendering, artifact, conformance, manifest, distribution execution, AtlasForge | represented in accepted doctrine/TASK-047 exclusion payload | TASK-047 decision/specification and `bcrp_legacy_compatibility.py` preserve these exclusions. A future Release contract must repeat its own narrower downstream grant without weakening them. |

## 5. Exact immutable-lifecycle gap

Accepted doctrine is unambiguous:

1. A Publication Release is an immutable publication act (`publication-boundary-intake-portability-lifecycle.md:92-96,104-115`).
2. Corrected, superseded, withdrawn and stale states do not rewrite history (`semantic-representation-contract-and-layered-validation.md:420-425`).
3. `stale`, `withdrawn` and `superseded` point to the later authority/event, and current-use status derives from the event chain (`briefforge-core-representation-profile.md:145-149`).
4. Later withdrawal creates a lifecycle event and does not erase prior releases (`semantic-representation-contract-and-layered-validation.md:511-517`).

Executable BCRP 1.0 cannot satisfy those requirements:

- `model.py:14-26` has no `PublicationLifecycleEventRecord` or equivalent independent root.
- `structure.py:43-52` requires only a current `lifecycle_status` and `publication_time` on the Release.
- `canonical.py` recognizes `lifecycle_events` only as an ordered key; it defines no event shape/authority/transition contract.
- `structure.py:152-163` requires exactly one record of every kind when a Manifest exists.
- `validation.py:295-336` uses an exactly-one helper; multiple Releases cause Release-specific L3/L4 logic to be skipped.
- `canonical.py:233-245` rejects a release-semantic fingerprint unless exactly one Release root exists.

Therefore:

- embedding a later event rewrites the Release and changes its release fingerprint;
- changing `lifecycle_status` rewrites the Release;
- creating another Release cannot represent withdrawal or staleness without falsely asserting another publication act;
- a required extension cannot repair the absent append-only root topology;
- implementing only initial Release would leave mandatory lifecycle behavior unrepresentable and violate TASK-048's explicit stop condition.

## 6. Independent adversarial runtime probes

A read-only in-memory probe loaded accepted golden case 1 and executed current BCRP code:

```text
unknown_status_findings: []
embedded_event_blocking: False
embedded_event_findings: 0
release_digest_changed: True
two_release_l3_l4_findings: []
two_release_fingerprint_error:
  ValueError: release-semantic requires exactly one root record
```

Interpretation:

1. An unrecognized lifecycle status passes when Release and Manifest agree.
2. Appending an apparently plausible withdrawal event passes all generic layers but changes the supposedly immutable Release digest.
3. Two Release records receive no Release-specific L3/L4 findings in a bundle without the Manifest cardinality trigger, while release fingerprinting refuses the topology.

Classification: **repository/architecture inconsistency** between accepted immutable event-chain semantics and BCRP 1.0 executable topology. It is not an environment/tooling issue and not evidence that doctrine should be weakened.

## 7. Authority implications

TASK-047 remains intact and authoritative:

- only the dedicated legacy compatibility boundary can admit an exact governed mapped Ready;
- generic BCRP validation must continue rejecting its required authority-critical extension;
- native BCRP Ready and corpus fixtures cannot manufacture Release authority;
- actual TASK-039 historical evidence remains insufficient for mapped Ready and cannot be released;
- deterministic binding is not external authentication.

No Release producer was implemented because even a correctly admitted Ready cannot yield an honest complete lifecycle under the current profile.

## 8. Why no specification, decision, RED tests or source were added

The user authorized those artifacts only after Phase 1 confirmed representability. It did not. Creating a Release contract around ambiguous fields would silently bless an incomplete topology; tests would then encode the defect. The correct bounded action is a task/report record and continuity update, not speculative implementation.

No accepted decision was created because no replacement topology has yet been reviewed. Historical accepted decisions remain evidence; they are not rewritten.

## 9. Gate verdict

**BLOCKED / NOT RECONCILED.**

Unmet gate conditions:

- immutable withdrawal cannot be represented;
- immutable staleness cannot be represented;
- explicit supersession/correction lineage cannot be validated over a complete multi-Release history;
- Release state vocabulary/policy and later-event authority are not executable;
- release-semantic fingerprint topology cannot cover the required history.

The other desired Release authority and production rules are potentially implementable, but implementing them now would knowingly produce an incomplete and contradictory lifecycle contract.

Do not proceed into Release production or renderer work.

## 10. Exactly one recommended next task

Unactivated title: **BCRP Append-Only Publication Lifecycle-Event Profile Evolution and Corpus Proof**.

Correctly bounded scope:

1. Decide whether the minimal honest carrier is a new independently addressable `PublicationLifecycleEventRecord` or an equivalently explicit immutable authority object.
2. Decide BCRP semantic/profile version impact before implementation; do not smuggle a major topology change into 1.0.
3. Specify event identity, subject Release/publication, event kind, UTC time, authority role/owner, policy, authorization identity, reason, correction/supersession/replacement relation, current-use consequence and explicit downstream exclusions.
4. Define canonical edges, event-chain ordering, fingerprint domains and derivation of current-use state without mutating prior records.
5. Define exact L3/L4 validation and generalized positive/adversarial corpus cases for initial release, correction, supersession, withdrawal and staleness.
6. Stop before Release production, renderer compatibility planning, rendering, artifacts, manifests or distribution.

Why this task and no broader one: it resolves the single architecture-caused blocker exposed by Phase 1. Publication Release production can resume only after the profile can preserve immutable history.

Historical identifier note: the unactivated renderer-compatibility placeholder formerly labelled `TASK-049` was never activated and is superseded by the human-authorized allocation of `TASK-049` to append-only lifecycle-event work. Renderer compatibility planning remains deferred to a later identifier and is not recommended before Release production is complete.

## 11. Verification results

Commands actually run with bytecode generation disabled:

```text
Recovery
python3 -B tools/recover_session.py --project . --json
exit 0

Pre-mutation complete suite
PYTHONPATH=src python3 -B -m unittest discover -s tests -v
206 tests — OK

Focused BCRP authoring/lifecycle/compatibility suite
PYTHONPATH=src python3 -B -m unittest \
  tests.test_bcrp_authoring_lifecycle \
  tests.test_bcrp_lifecycle_authority_compatibility -v
23 tests — OK

Post-reconciliation complete suite
PYTHONPATH=src python3 -B -m unittest discover -s tests -v
206 tests — OK

Fresh BCRP forbidden-module inventory
[]

Compatibility AST/specialization/danger scan
1 path parsed; 0 forbidden hits

Architecture-to-Reality Audit
python3 -B tools/architecture_reality_audit.py --project . --write-report
0 blocks; 0 warnings
```

The in-memory lifecycle probe reproduced every reported representation defect without writing repository files. No focused TASK-048 production tests were added or run because Phase 1 triggered the mandatory stop before contract/test/source implementation.

Coherence and context health had no blocks. Context pointers were trimmed within configured size budgets; the only retained coherence notice is the established Historical Compatibility classification for EIP/MetaHarvest boundary references. Final bounded recovery identified TASK-048 as blocked and the correct unactivated profile-evolution next action.

`compileall` was not run.

## 12. Filesystem accounting

Authoritative before manifest:

`/tmp/briefforge-before-task048-20260716.json`

Authoritative final after manifest:

`/tmp/briefforge-after-task048-20260716.json`

Before: 648 included paths. After: 650 included paths.

Added (2):

- `artifacts/reports/R-20260716-task-048-publication-release-representation-gap.md` — canonical Phase 1 blocker report;
- `artifacts/tasks/TASK-048-bcrp-publication-release-authority-production-and-lifecycle-proof.md` — activated task and blocked outcome.

Modified (8):

- `artifacts/reports/R-20260716-architecture-reality-audit.md` — required refreshed audit evidence;
- `artifacts/reports/_SUMMARY.md` — affected report inventory and blocker navigation;
- `artifacts/tasks/_SUMMARY.md` — affected task inventory and blocker navigation;
- `context/latest_handoff.md` — recovery continuity;
- `state/active_goal.md` — current blocked goal and exact successor;
- `state/architecture.md` — executable lifecycle gap and gate;
- `state/project_state.md` — current operating state;
- `state/recent_changes.md` — bounded current history.

Deleted: none.

Path-type or symlink changes: none.

Unexpected differences: none. Every changed repository path is classified above. No `src/`, `tests/`, fixture, renderer, AtlasForge, upstream or unrelated path changed.

The `/tmp` manifests and helper-output files are operational verification evidence outside the repository and are not BCRP `PublicationManifestRecord` production.

## 13. Scope preservation

No changes were made to:

- `src/` or `tests/`;
- BCRP record kinds, canonicalization, validators or compatibility adapter;
- renderer/runtime/HTML/SVG code;
- golden corpus;
- AtlasForge or upstream projects;
- financial-domain semantics;
- repository Git status.

No network, database, package installation, compileall, Git initialization, commit or push occurred.
