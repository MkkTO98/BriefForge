# TASK-049 Append-Only Publication Lifecycle-Event Profile and Corpus Proof

Date: 2026-07-16
Task: TASK-049
Verdict: **CLEAR TO PROCEED**

## 1. Recovery and baseline

Normal bounded recovery completed successfully before mutation. The repository remained intentionally non-Git. TASK-049 had no task artifact and was unused as an activated identifier; prior mentions were only an unactivated renderer placeholder. The pre-task manifest was created at `/tmp/briefforge-before-task049-20260716.json` through the established helper without accessing earlier task manifests or separately hashing it. The helper reported 650 included paths. The full bytecode-disabled baseline ran 206 tests successfully.

Authoritative inputs included the constitution and instructions, state and handoff, TASK-041 through TASK-048 artifacts, accepted BCRP decisions/specifications, BCRP model/loader/structure/canonicalization/validation/authoring/corpus, valid fixtures, lifecycle compatibility adapter, and relevant tests.

## 2. TASK-048 terminology correction

TASK-048 remains an honest **BLOCKED / NOT RECONCILED** result. No repository artifact described it as both activated and reconciled. Its historical unactivated renderer placeholder used the `TASK-049` identifier, however. The TASK-048 task/report now preserve that history while recording that the placeholder was superseded by the human-authorized TASK-049 lifecycle allocation. No TASK-048 evidence, blocker, or history was erased.

## 3. Representation alternative evaluation

| Alternative | Immutability and fingerprint | Topology and consumers | Compatibility/versioning | Verdict |
|---|---|---|---|---|
| A. Add an event kind to BCRP 1.x | Could keep Release bytes immutable only by changing the complete bundle topology and canonical root set | Old validators cannot understand lifecycle authority and currently admit exactly eleven kinds | Required authority/topology/canonicalization change is breaking, not minor | Rejected |
| B. BCRP 2.0 | Can represent the model honestly | Requires all eleven current kinds, bundles, validators, canonicalization, and corpus to migrate | Defensible major version but disproportionate to one post-Release concern | Deferred fallback |
| C. Separate companion profile | Leaves BCRP Releases and exact-one bundle topology unchanged; events have independent identities/fingerprints | Requires explicit profile negotiation and lets generic BCRP remain fail-closed | Backward-compatible because no BCRP contract changes | **Accepted** |
| D. Existing doctrine-supported alternative | TASK-041 prose anticipated distinct lifecycle events, but BCRP 1.0 supplied no independently addressable carrier | Embedded fields, multiple Release roots, and required extensions fail TASK-048's proofs | No better already-implemented carrier exists | None selected |

Decision: `artifacts/decisions/D-20260716-publication-lifecycle-event-companion-profile.md`.

## 4. Accepted semantic model

- Initial Release remains the immutable BCRP `PublicationReleaseRecord`; it is not duplicated as an event.
- `correction` is a supersession reason requiring a separately governed Ready and new Release; it never mutates the corrected Release.
- `supersession` binds exact predecessor and successor Release identities and `release-semantic` fingerprints. Version ordering confers no relationship.
- `withdrawal` is an append-only authority event against one exact Release. It changes derivative future-use eligibility without rewriting issuance history.
- Rerender is artifact regeneration, not semantic correction or a lifecycle event.
- Staleness has two non-equivalent meanings: a derived freshness finding and an authoritative `staleness-declaration`. The implemented profile records only the declaration. Source changes never rewrite fixed Release evidence.
- Reinstatement, expiration, and distribution suspension remain deferred. Replacement is admitted only as an explicit supersession reason.

## 5. Authority, topology, and validation

`PublicationLifecycleEventRecord` owns exact event identity/profile/publication/type/Release references/reason/authority/policy/time/causal references/distribution consequence/extensions.

Authority admission binds the exact `(authority identity, authority owner, authority role)` triple under an explicitly supplied policy. It is trusted in-process or accepted-artifact structural authorization only; no digital signature or external authentication claim is made.

The bounded state projection requires:

- one publication identity;
- at least one exact negotiated BCRP 1.0 Release binding;
- exactly one initial Release root;
- one connected Release graph;
- every later Release introduced by exactly one supersession edge;
- no self-edge, cycle, competing predecessor/successor, cross-publication edge, unrelated causal predecessor, duplicate identity, ambiguous causal position, or conflicting terminal event.

Catalog membership, tuple order, event order, timestamps, filenames, and lexical versions confer no current authority. The validated graph sink supplies the only eligible current Release; terminal withdrawal/staleness can leave no current Release without deleting history.

## 6. Canonicalization and append-only proof

Each event uses domain `lifecycle-event-semantic`, profile `briefforge-publication-lifecycle-event-profile:1.0.0`, canonicalization `publication-lifecycle-event-canonicalization:1.0.0`, and SHA-256.

Canonicalization normalizes NFC, LF, and owned explicit-offset timestamps; sorts object keys; sorts only path-owned unordered core collections; preserves arbitrary extension payload list order; and rejects unsupported values and Unicode-normalized duplicate keys.

Proofs cover:

- key/order/Unicode/line-ending/timestamp-equivalent inputs producing equal event fingerprints;
- payload tampering producing a different event fingerprint;
- order-sensitive extension payloads, including core-like payload key names, remaining distinct;
- appending a later event changing no earlier event fingerprint;
- adding lifecycle events changing no BCRP Release fingerprint;
- all Release/event permutations of a multi-hop supersession graph producing one identical current Release.

## 7. BCRP 1.0 conformance corrections

TASK-048's probes were classified against accepted BCRP 1.0 obligations and corrected without importing the companion model into BCRP:

1. Multiple Release roots now receive explicit Release-specific L3 and L4 `lifecycle-release-cardinality` findings in addition to structural findings.
2. Core Release and Manifest lifecycle status are closed to the issuance-time state `active`; an unknown matching pair no longer passes.
3. Undeclared embedded core `lifecycle_events` material is rejected.
4. Properly enveloped optional BCRP extension payload remains preservable but grants no lifecycle authority and cannot mutate core governed state.

The eleven-kind BCRP contract and exact-one complete-publication Release topology remain unchanged.

## 8. Corpus and anti-overfitting evidence

`tests/fixtures/publication_lifecycle/corpus.json` contains 38 static cases: four valid cases and 34 invalid cases. The corpus declares expected validity, expected finding codes, and expected current state independently from production validation.

Valid cases cover:

1. initial Release without later event;
2. correction through new Release plus supersession;
3. successor withdrawal without Release mutation;
4. multi-hop supersession with reordered Release/event inputs.

Invalid cases include every user-required class plus unknown authority identity, event/reason mismatch, disconnected catalogs, cross-publication causal events, withdrawal/staleness competition, malformed/undeclared transport input, unsupported BCRP binding version, and empty catalogs.

Production companion source contains no TASK-039 identifier, case identifier, fixture path, mutation label, demographic/company/financial specialization, renderer, artifact, manifest, AtlasForge, database, or network dependency.

## 9. Adversarial review corrections

A first independent review found transport-order state derivation, disconnected-catalog authority, authority-identity omission, reason-matrix, causal, parser, version, extension, canonicalization, and terminal-conflict weaknesses. Focused RED tests reproduced these failures before correction.

A second review found a reserved-name collision where extension payload arrays could be sorted because their key resembled a core unordered field. A focused RED test reproduced equal fingerprints for distinct ordered payloads. Canonicalization was changed to path-scoped sorting and the regression now passes.

These were implementation defects discovered and corrected within TASK-049, not residual blockers.

## 10. Gate assessment

All TASK-049 gate conditions are met:

- companion-profile version decision is explicit and compatibility-defensible;
- BCRP Releases remain immutable and independently fingerprinted;
- lifecycle history is append-only and event fingerprints are independent;
- correction, supersession, withdrawal, rerender, derived staleness, and staleness declaration are distinct;
- exact event authority cannot arise from technical validation, Ready, Release, renderer, fixture possession, catalog membership, or version ordering;
- deterministic state is graph-derived and ambiguity fails closed;
- TASK-048 BCRP conformance gaps are resolved or bounded as non-authoritative extension preservation;
- generalized valid/invalid corpus and anti-overfitting proofs pass;
- full suite passes;
- no excluded subsystem was implemented.

Verdict: **CLEAR TO PROCEED**.

## 11. Exactly one next task

Recommend, but do not activate:

**TASK-050 — BCRP Publication Release Authority, Production, and Lifecycle Proof**

Why bounded: TASK-049 resolves only the representation blocker that stopped TASK-048. The next proof can now resume exact governed Ready -> explicit Publication Release authority -> one immutable Release while consuming, but not producing renderer/artifact work. Renderer compatibility planning must receive a later identifier and remains premature until Release production is complete.

## 12. Verification and mutation accounting

Commands executed with `PYTHONDONTWRITEBYTECODE=1` and no `compileall`:

- `PYTHONPATH=src python3 -B -m unittest tests.test_publication_lifecycle_profile ...` — 33 focused lifecycle tests, OK;
- focused lifecycle/BCRP/TASK-047 modules — 85 tests, OK;
- `PYTHONPATH=src python3 -B -m unittest discover -s tests` — 239 tests, OK after continuity edits;
- `/tmp/task049_static_verify.py` — five companion source files, four valid and 34 invalid cases, zero forbidden specialization/import/dynamic-call hits, zero companion modules loaded by fresh BCRP import;
- `tools/architecture_reality_audit.py --project . --write-report` — 0 blocks, 0 warnings;
- `tools/check_coherence.py --project . --json`, `tools/context_health.py --project . --json`, and `tools/recover_session.py --project . --json` — rerun after final continuity compaction.

The deterministic preliminary comparison used the same helper/schema/exclusions as the 650-path baseline. It found 663 included paths: 13 additions (11 files plus two directories), 14 changed files, no deletion, no type change and no symlink-target change. Format, root and exclusions matched.

Added paths:

- `artifacts/decisions/D-20260716-publication-lifecycle-event-companion-profile.md`
- `artifacts/reports/R-20260716-task-049-append-only-publication-lifecycle-event-profile-and-corpus-proof.md`
- `artifacts/specifications/publication-lifecycle-event-profile.md`
- `artifacts/tasks/TASK-049-append-only-publication-lifecycle-event-profile-and-corpus-proof.md`
- `src/briefforge/publication_lifecycle/` and its five Python files
- `tests/fixtures/publication_lifecycle/` and `corpus.json`
- `tests/test_publication_lifecycle_profile.py`

Changed files:

- `artifacts/decisions/_SUMMARY.md`
- `artifacts/reports/R-20260716-architecture-reality-audit.md`
- `artifacts/reports/R-20260716-task-048-publication-release-representation-gap.md`
- `artifacts/reports/_SUMMARY.md`
- `artifacts/specifications/_SUMMARY.md`
- `artifacts/tasks/TASK-048-bcrp-publication-release-authority-production-and-lifecycle-proof.md`
- `artifacts/tasks/_SUMMARY.md`
- `context/latest_handoff.md`
- `src/briefforge/bcrp/structure.py`
- `src/briefforge/bcrp/validation.py`
- `state/active_goal.md`
- `state/architecture.md`
- `state/project_state.md`
- `state/recent_changes.md`

The authoritative final post-manifest is created only after this evidence insertion and final checks. No repository write is permitted afterward.
