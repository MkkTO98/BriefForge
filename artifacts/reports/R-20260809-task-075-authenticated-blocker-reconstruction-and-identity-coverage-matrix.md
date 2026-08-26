# TASK-075 Authenticated Blocker Reconstruction and Identity/Coverage Matrix

Date: 2026-08-09
Task: TASK-075
Status: independently reproduced; materially corrects TASK-074 provenance

## Authority and method

This report was derived from the exact TASK-071 `profile.json` and `candidate-semantic.json`, production BCRP canonical reconstruction, `inspect_graph`, L0-L2 validation, the exact paired profile decoder/validator, and a separate in-memory reproduction using the TASK-073/TASK-074 synthetic paired fixture. No production file or governed lifecycle object was created.

TASK-071 Candidate SHA-256 remains:

`b1c29473241648c68dfb7bb737715645b396c149094eeb70cef34feb52fb95b2`

Canonical profile reconstruction reproduced the persisted Candidate semantic bytes exactly.

## Material correction to TASK-074

TASK-074 correctly established the planner-visibility and vacuous-coverage defect, but incorrectly attributed the synthetic fixture's identity and dangling-reference counts to the exact TASK-071 Candidate.

### Exact TASK-071 results

| Measure | Reproduced result |
|---|---:|
| Core renderer requirements | 0 |
| Core fallbacks | 0 |
| Paired renderer requirements | 6 |
| Paired renderer mappings | 7 |
| Paired sections | 6 |
| Paired statements | 76 |
| Paired table | 1 |
| Paired rows | 7 |
| Paired values | 14 |
| Paired qualifications | 27 |
| Paired provenance objects | 8 |
| Paired obligations | 5 |
| Total paired object identities | 144 |
| Paired identities also present in traversable core graph | 144 |
| Paired identities absent from traversable core graph | 0 |
| Dangling identities after adding two core references per paired identity | 0 |
| Dangling edges | 0 |
| L1 identity/reference findings | 0 |
| L2 identity/reference findings | 0 |

All 144 local identity strings are mirrored in traversable core objects. This proves lexical addressability in the exact TASK-071 closure. It does not prove cross-domain semantic equality, requirement completeness, or planner coverage.

### Synthetic TASK-073/TASK-074 fixture results

| Measure | Reproduced result |
|---|---:|
| Sections | 3 |
| Statements | 15 |
| Table | 1 |
| Rows | 7 |
| Values | 14 |
| Qualifications | 21 |
| Provenance objects | 8 |
| Obligations | 2 |
| Total paired identities | 71 |
| Unique dangling identities in nonmirroring core fixture | 71 |
| Dangling edges from one requirement and one fallback per identity | 142 |
| L1 identity/reference findings | 142 |
| L2 identity/reference findings | 142 |

The 71/142/142 result is valid synthetic negative evidence. It is not a count of the exact TASK-071 Candidate.

Historical TASK-074 artifacts remain immutable evidence of what was concluded. This report supersedes only the provenance of those counts and the claim that the exact TASK-071 object identities are absent from the core graph. TASK-074's `NOT READY` ruling remains correct because planner coverage and publication-evidence authority remain absent.

## Exact representation and validation path

### Core domain

- BCRP records are first-class identities.
- Nested dictionaries with string `id` fields are traversable identities.
- `_ref`, `_refs`, and the closed reference-list keys produce graph edges.
- Strings are not decoded by the core graph.
- Core structural authority and L2 independently reject dangling edges.
- TASK-071 contains traversable core counterparts for all 144 paired object local identities.

### Paired domain

- The paired extension envelope is traversable as an extension object, but `payload.canonical_semantics` is one canonical JSON string.
- The paired profile owns exact dispatch, bounded decoding, DTO reconstruction, identity uniqueness, reference resolution, ordering, six renderer requirements, and seven row/relationship mappings.
- The core graph does not parse that string.
- The paired decoder does not currently issue a cross-domain correspondence proof or planning inventory.

### Planner

- Native-v2 `_candidate_material()` reads only core `candidate.semantic["renderer_requirements"]` and `candidate.semantic["fallbacks"]`.
- It does not dispatch to the paired decoder.
- Both arrays are empty in TASK-071.
- `_plan_requirements()` iterates zero requirements and compares an empty mapped set with an empty expected set.
- The resulting Plan is `supported=True` with zero mappings.

### Why rendering was reachable

- Native admission checks Release/Plan/declaration byte and fingerprint bindings plus the frozen paired capability tuple.
- Frozen paired Plan verification checks supported status and capability binding, not paired requirement/mapping completeness.
- Projection reconstructs the paired extension independently and copies its six requirements and seven mappings.
- Controlled invocation binds the projection and upstream fingerprints.
- The renderer consumes the paired projection directly and never consumes the core Plan mapping inventory.

The Plan was strongly fingerprint-bound but semantically vacuous. Rendering therefore proved actual authority-path containment and renderer reachability, not planning coverage.

## Identity-and-coverage matrix

| Semantic class | Identity namespace | Authoritative serialized location | First-class graph membership | Planner visibility now | Permitted successor references | Coverage obligation | Downstream consumers | Current failure mode |
|---|---|---|---|---|---|---|---|---|
| BCRP records | core BCRP 1.0 | profile-instance record documents | core graph | release/plan lifecycle logic | structured core-domain identity | exact lifecycle closure | Judgment, Ready, Release, Plan, Audit, Conformance, Manifest | none for identity; predecessor derivation gaps remain |
| Core sections | core BCRP 1.0 | Candidate semantic dictionaries | core graph | only if referenced by core requirements | core-domain qualified identity | profile-owned expression coverage | planner, validators | paired profile obligations undiscovered |
| Core statements | core BCRP 1.0 | Candidate semantic dictionaries | core graph | only through core requirements/fallbacks | core-domain qualified identity | target/authority/caveat coverage | planner, validators | same local names do not prove paired correspondence |
| Core table/rows | core BCRP 1.0 | Candidate semantic dictionaries | core graph | only through core requirements | core-domain qualified identity | exact table/row expression | planner, projection source comparison | seven paired mappings invisible |
| Core values | core BCRP 1.0 | Candidate/Material semantics | core graph | only through core references | core-domain qualified identity | state/unit/source preservation | validators, conformance | no paired coverage ledger |
| Core qualifications | core BCRP 1.0 | Candidate semantics | core graph | only through core references | core-domain qualified identity | caveat/limitation preservation | validators, conformance | no paired correspondence proof |
| Core provenance | core BCRP 1.0 | Material/Candidate semantics | core graph | only through core references | core-domain qualified identity | provenance preservation | validators, projection, conformance | no effective-graph binding |
| Core obligations | core BCRP 1.0 | Candidate semantics | core graph | only through core references | core-domain qualified identity | obligation expression | validators, conformance | no paired coverage ledger |
| Paired sections | paired v3 | opaque canonical paired JSON | paired decoder graph only | invisible | paired-domain qualified identity | authored ordering and narrative coverage | projection, renderer, conformance | no planner resolver/correspondence proof |
| Paired statements | paired v3 | opaque canonical paired JSON | paired decoder graph only | invisible | paired-domain qualified identity | exact statement expression | projection, renderer, conformance | same local core identity is not governed alias |
| Paired table/rows | paired v3 | opaque canonical paired JSON | paired decoder graph only | invisible | paired-domain row identity; typed relationship token | all seven row mappings exactly once | planner successor, projection, renderer, conformance | zero Plan mappings |
| Paired values | paired v3 | opaque canonical paired JSON | paired decoder graph only | invisible | paired-domain qualified identity | exact states, units, sources | renderer, conformance | no Plan coverage |
| Paired qualifications | paired v3 | opaque canonical paired JSON | paired decoder graph only | invisible | paired-domain qualified identity | exact limitation edges | renderer, conformance | no Plan coverage |
| Paired provenance | paired v3 | opaque canonical paired JSON | paired decoder graph only | invisible | paired-domain qualified identity | exact provenance realization | renderer, conformance | no Plan coverage |
| Paired obligations | paired v3 | opaque canonical paired JSON | paired decoder graph only | invisible | paired-domain qualified identity | exact obligation realization | renderer, conformance | no Plan coverage |
| Six paired renderer requirements | paired profile vocabulary | canonical paired JSON tuple pairs | not object identities | invisible | profile-qualified requirement keys, not fabricated Candidate IDs | all six outcomes pass exactly once | planner/admission/conformance | absent from Plan |
| Seven paired renderer mappings | paired profile mapping inventory | canonical paired JSON ordered pairs | row identity is paired object; relationship is typed value | invisible | paired row DQI + exact typed relationship token | seven exact ordered outcomes | planner/projection/renderer/conformance | absent from Plan |
| Extension envelope | core extension boundary + paired owner | Candidate extensions list | core sees envelope refs; paired owns payload interpretation | no semantic dispatch | exact owner/name/version/contract dispatch | preservation and complete decode | validator/resolver | planner ignores semantic criticality |
| Effective graph | successor derived domain | not Candidate authority; reproducible evidence only | derived verified view | future mandatory input | domain-qualified refs bound to graph digest | complete source consumption and coverage | planner through Manifest | absent |
| Plan coverage evidence | successor Plan contract | required versioned Plan extension | contract-owned resolver | absent | exact graph-domain references | six global outcomes, seven mapping outcomes, complete semantic ledger | admission through Manifest | Plan v1 cannot express paired coverage |
| Projection evidence | paired projection contract | persisted canonical evidence | projection-owned exact content | consumes extension independently | binds Plan and graph coverage transitively | exact projection/material closure | renderer, conformance, Manifest | Plan fingerprint currently carries vacuous coverage |
| Rendering evidence | paired invocation contract | artifact/evidence/ledger files | evidence identity/fingerprints | downstream | graph/Plan/projection-bound evidence | exact artifact and implementation closure | Audit/conformance/Manifest | no production Audit derivation |
| Audit record | core BCRP | predecessor record | core graph | downstream | derived only from reloaded invocation evidence | exact artifact/Plan/graph link | Conformance, Manifest | currently caller-supplied |
| Conformance record | core BCRP + paired evidence | predecessor record and persisted evidence | core graph plus paired evidence authority | downstream | derived only from reloaded conformance evidence | exact semantic realization and Audit binding | Manifest | currently caller-supplied |
| Manifest | core BCRP + paired manifest contract | persisted Manifest/evidence closure | core terminal record | downstream terminal | exact predecessor/graph/coverage/evidence bindings | complete chain reauthentication | reload/adjudication | secure predecessor derivation and restart authority absent |

## Corrected counterpart-proof execution

A post-review, read-only model reran the final counterpart table against exact TASK-071 bytes after removing paired `Section.order` from cross-domain comparison. Core canonical section order is not paired authored order and therefore is not a valid counterpart field.

Execution returned:

`TASK-075 corrected counterpart model PASS: counts={'sections': 6, 'statements': 76, 'tables': 1, 'rows': 7, 'values': 14, 'qualifications': 27, 'provenance': 8, 'obligations': 5}; total=144; mismatches=0; section_order_excluded=true`

This closes the object-correspondence count and equality model only. It does not close the remaining exact persisted-wire contracts listed by the conditional architecture decision.

## Corrected blocker statement

The exact TASK-071 Candidate is not blocked because its paired object local identities are absent from the core graph. It is blocked because:

1. cross-domain ownership and correspondence are not governed by lexical equality;
2. the six paired requirements and seven paired mappings are invisible to the sole planner;
3. Plan v1 has no domain-qualified, graph-bound complete paired coverage contract;
4. zero mappings pass vacuously;
5. secure bootstrap, Audit derivation, Conformance derivation, complete persisted reauthentication, and interruption recovery remain absent.

This corrected reconstruction is the basis for TASK-075 architecture adjudication.