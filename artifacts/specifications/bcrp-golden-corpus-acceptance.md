# BCRP 1.0 Golden Corpus Acceptance Specification

Date: 2026-07-16
Status: accepted specification
Task: TASK-044
Profile: `briefforge-core-representation-profile` `1.0.0`
Corpus identity: `briefforge-bcrp-golden-corpus-plan`
Corpus plan version: `1.0.0`

## 1. Purpose and non-implementation boundary

This specification accepts the future test inventory for BCRP 1.0. It specifies exactly three primary cases, valid expectations, minimal invalid mutations, validation-layer ownership, blocking consequences, coverage, and fixture-safety rules.

It does not create profile instances, schemas, fixture files, loaders, validators, serializers, renderers, selectors, fallbacks, manifests, or AtlasForge integration. TASK-039 JSON is evidence, not a canonical profile instance.

## 2. Finding expectation vocabulary

Expected findings use stable families rather than premature error codes:

- `intake-completeness-or-scope`
- `profile-structure-or-version`
- `identity-or-reference-integrity`
- `authority-or-provenance`
- `semantic-state-integrity`
- `obligation-or-qualifier-attachment`
- `composition-or-narrative-integrity`
- `selection-closure-or-state-narrative`
- `lifecycle-or-version-linkage`
- `governance-or-distribution-authority`
- `renderer-capability-or-plan`
- `transformation-or-fallback`
- `audit-link-conformance`
- `semantic-artifact-conformance`
- `extension-boundary`
- `domain-ownership-prohibition`

Severities are `warning` or `blocking`. A blocking finding stops the affected boundary shown in the variant tables. Validators may continue collecting independent findings when safe; they must not promote, release, render, or accept an artifact past a blocking boundary.

## 3. Case 1 — demographic/correlation fixed-evidence publication

### 3.1 Evidence basis and valid instance

Case identity: `case-1-demographic-correlation-publication`.

The case is a reduced, transport-neutral re-expression of the TASK-039 evidence chain, not a copy or canonization of TASK-039 JSON. It uses:

- InsightForge source fixture `../InsightForge/artifacts/fixtures/T-035-demographic-growth-correlation-report-input.json` as historical public/internal test evidence at materialization time only;
- TASK-039 Candidate, Judgment, Ready, HTML, conformance, renderer audit, and inspection records under `artifacts/presentations/TASK-039-demographic-correlation-browser-report/`;
- the authority split recorded in `D-20260713-demographic-correlation-browser-report-boundary.md` and TASK-043 worked trace 13.4.

The expected-valid BCRP instance represents:

- a Presentation Brief with one organizing purpose and audience orientation;
- Portable Presentation Material with separate InsightForge question/interpretation authority and KnowledgeForge coefficient/method/provenance authority;
- one evidence snapshot and multiple generic upstream references;
- exact materialized coefficients with units/types and explicit present states;
- accepted-finding and reusable-evidence statements, methodology, provenance, uncertainty and caveat statements;
- explicit comparison-universe/method binding for any `strongest` claim;
- ordered sections, static table and key-number exhibit intents, and caveat co-encounter obligations;
- no selector or live computation;
- required standalone HTML/SVG-compatible static expression, complete static/print fallback, and scoped-style/deep-link obligations;
- Candidate -> successful Judgment -> Ready linkage;
- fixed-evidence Release Record, renderer compatibility/expression plan, generated-artifact audit, separate audit-link and semantic-conformance records, and derivative manifest;
- optional AtlasForge catalogue consumption only through the manifest.

Expected valid result: L0–L6 applicable checks pass; no blocking findings; Candidate may be promoted; an authorized release may occur; rendering may occur only under the accepted plan; artifact acceptance requires both audit-link and semantic conformance.

The historical mismatch—`renderer_audit_metadata.json` says `table_exhibit_present: false` while HTML and inspection evidence contain a table—is retained as source-history evidence and invalid-mutation inspiration. It is not an expected-valid outcome and TASK-039 is not repaired.

### 3.2 Minimal invalid mutations

| ID | Minimal mutation | Expected layer | Finding family | Severity / collection | Blocked consequence |
|---|---|---|---|---|---|
| C1-I01 | remove organizing purpose from Brief/Candidate | L0 then L2 | intake-completeness-or-scope | blocking; continue independent shape checks | Candidate construction/promotion |
| C1-I02 | change one statement upstream ref to an absent identity | L1/L2 | identity-or-reference-integrity | blocking; continue safe reference scan | Candidate promotion |
| C1-I03 | remove the caveat's `limits-target` edge only | L2 | obligation-or-qualifier-attachment | blocking | Candidate promotion |
| C1-I04 | add one hierarchy edge producing a section cycle | L2 | composition-or-narrative-integrity | blocking | Candidate promotion/render plan |
| C1-I05 | retain `strongest` wording but remove comparison-universe binding | L2 | authority-or-provenance | blocking | Candidate promotion |
| C1-I06 | plan renderer-side ranking/caption creation not declared by a requirement | L5 | transformation-or-fallback | blocking | rendering |
| C1-I07 | make manifest lifecycle status `active` while release authority says `withdrawn` | L3/L6 | lifecycle-or-version-linkage | blocking; source release unchanged | manifest/artifact catalogue acceptance |
| C1-I08 | report audit-link pass as semantic-conformance pass without semantic evidence | L6 | semantic-artifact-conformance | blocking | artifact acceptance |
| C1-I09 | artifact audit references a different Ready fingerprint | L6 | audit-link-conformance | blocking | artifact acceptance |

## 4. Case 2 — synthetic fictional-company comparison decision publication

### 4.1 Valid instance

Case identity: `case-2-synthetic-company-comparison`.

The case uses clearly fictional `Aster Vale Tools` and `Boreal Kite Systems` through generic typed external references. No real security, fiscal period, consolidation, currency-conversion, reporting-segment, adjusted-value, or other deferred financial semantics appear.

The expected-valid BCRP instance represents:

- a standalone fixed-evidence comparison/decision-support publication with an ADPM semantic-version binding;
- a Presentation Brief, organizing purpose, decision audience, explicit scope/non-scope, and distribution designation;
- generic external company/material refs and separate upstream semantic, evidence, exporter, presentation-author, validation, and release authorities;
- observation, reusable evidence, accepted evidence-bound interpretation, a bounded upstream-authorized recommendation, and a personal annotation explicitly scoped as personal rather than evidence;
- exact values showing one explicit zero, one missing/not-provided value, one unavailable value, and one suppressed/withheld value with suppression authority/reason but no embedded sensitive payload;
- two attributed conflicting upstream values represented without choosing a winner;
- comparison universe and method, provenance, caveats, uncertainty, unit/type declarations, and ADPM alternatives/decision relationships sufficient for the admitted recommendation;
- sensitivity/distribution obligations, table exhibit intent, complete static table fallback, standalone/print obligations, and no live data;
- full Candidate/Judgment/Ready/release/artifact/conformance/manifest chain.

Expected valid result: all applicable L0–L6 checks pass. Layer 4 contains an explicit synthetic release/distribution authorization record; validation does not infer it. The personal annotation is visibly attributed and does not change the recommendation's evidence authority.

### 4.2 Minimal invalid mutations

| ID | Minimal mutation | Expected layer | Finding family | Severity / collection | Blocked consequence |
|---|---|---|---|---|---|
| C2-I01 | remove semantic authority from the recommendation while leaving two possible owners | L2 | authority-or-provenance | blocking | Candidate promotion |
| C2-I02 | encode the exact zero as `missing-not-provided` | L2 | semantic-state-integrity | blocking | Candidate promotion |
| C2-I03 | omit the suppressed value object and suppression assertion entirely | L2 | semantic-state-integrity | blocking | Candidate promotion |
| C2-I04 | retain only one conflicting source and mark consistency `consistent` | L2 | semantic-state-integrity | blocking | Candidate promotion |
| C2-I05 | attach payload `12` to a `not-applicable` value state | L1/L2 | profile-structure-or-version; semantic-state-integrity | blocking; continue independent checks | Candidate promotion |
| C2-I06 | present the personal annotation as accepted evidence without authority change | L2 | authority-or-provenance | blocking | Candidate promotion |
| C2-I07 | add an unsupported recommendation inferred by BriefForge from the comparison | L2/L4 | authority-or-provenance | blocking | promotion/release |
| C2-I08 | release material outside its declared distribution without authorization | L4 | governance-or-distribution-authority | blocking; validator records but cannot approve | release |
| C2-I09 | renderer lacks required table capability and the required table fallback is absent | L5 | renderer-capability-or-plan | blocking | rendering |
| C2-I10 | add unknown required semantic extension `example:security-identity` | L1 | extension-boundary | blocking | all dependent processing |
| C2-I11 | add a core or extension field defining fiscal period or adjusted value | L1/L2 | domain-ownership-prohibition | blocking | profile admission/Candidate promotion |

## 5. Case 3 — synthetic company–macro relationship with finite selection

### 5.1 Valid instance

Case identity: `case-3-synthetic-company-macro-selection`.

The case uses fictional `Cinder Atlas Components` and generic upstream macro/material references. Its purpose is communication of already materialized, prevalidated state narratives—not calculation.

The expected-valid BCRP instance represents:

- accepted finding plus a clearly distinguished hypothesis and scenario, scoped uncertainty, caveats and multiple evidence scopes;
- one finite Selection Set with exactly three states: `baseline`, `supply-tightness`, and `demand-slowdown`;
- one authority-declared deterministic default (`baseline`);
- complete materialized state projections with explicit statements, titles/labels, exhibits, values, caveats, uncertainty, evidence, provenance, obligations, and renderer requirements;
- invariant methodology/scope statements explicitly included in all three projections;
- state-specific conclusions whose visibility is limited to compatible states;
- exact evidence binding and independent validation identity for every state;
- no wildcard, Cartesian product, live query, computed value, derived ranking, or newly inferred comparison;
- required state identity visibility, bounded navigation, complete static state enumeration, print fallback, standalone/offline reproduction, and semantic conformance audit;
- release/manifest semantics consumable optionally by AtlasForge without dependency.

The valid case also contains a **non-admitted adversarial candidate state** as test design metadata, not as part of the valid profile instance: if a visible baseline conclusion were reused in `demand-slowdown`, it would be false or materially misleading. This supplies a discriminating semantic-conformance mutation.

Expected valid result: all applicable L0–L6 checks pass; every state is independently valid; renderer compatibility either admits native finite selection or deterministically selects the complete static fallback; print output contains coherent state sections rather than hidden-state dumps.

### 5.2 Minimal invalid mutations

| ID | Minimal mutation | Expected layer | Finding family | Severity / collection | Blocked consequence |
|---|---|---|---|---|---|
| C3-I01 | remove the authority-declared default state | L1/L2 | selection-closure-or-state-narrative | blocking | Candidate promotion/selector release |
| C3-I02 | add wildcard state `*` | L1/L2 | selection-closure-or-state-narrative | blocking | Candidate promotion |
| C3-I03 | remove materialized statement/value lists from `supply-tightness` | L2 | selection-closure-or-state-narrative | blocking | selector publication |
| C3-I04 | include the baseline conclusion in `demand-slowdown` without a valid authored variant | L2 | composition-or-narrative-integrity | blocking | Candidate promotion/selector publication |
| C3-I05 | rendered `demand-slowdown` output visibly retains that incompatible conclusion | L6 | semantic-artifact-conformance | blocking even with correct audit links | artifact acceptance |
| C3-I06 | omit a state-specific caveat from static fallback | L2/L5/L6 | transformation-or-fallback | blocking at earliest detected boundary | promotion, plan, or artifact acceptance |
| C3-I07 | renderer declares navigation but lacks verified required state-identity visibility | L5 | renderer-capability-or-plan | blocking | native selection rendering; complete static fallback may proceed if independently admitted |
| C3-I08 | remove print fallback while print is mandatory | L2/L5 | transformation-or-fallback | blocking | Candidate promotion/rendering |
| C3-I09 | change one state evidence snapshot without new validation identity/release semantics | L2/L3 | lifecycle-or-version-linkage | blocking | promotion/release |
| C3-I10 | derive a fourth state from an implicit two-by-two combination | L2 | selection-closure-or-state-narrative | blocking | Candidate promotion |

## 6. Lifecycle and processing expectations

For every valid case, the future corpus materialization must include enough independently addressable records to test:

1. Presentation Brief admission;
2. Portable Presentation Material closure and offline retention;
3. Candidate semantic reconstruction and fingerprint;
4. layer-separated Validation Judgment;
5. exact Ready promotion binding;
6. explicit governance/release authority rather than inferred approval;
7. Publication Release Record and lifecycle identity;
8. renderer capability/compatibility/expression plan;
9. generated-artifact audit-link evidence;
10. semantic artifact-conformance evidence;
11. derivative manifest projection and contradiction rejection.

Invalid mutations remain minimal: one authorized base instance plus one semantic/structural change wherever possible. A validator may continue collecting unrelated findings, but a blocking result cannot be bypassed by later-layer success.

## 7. Two-dimensional coverage matrix

Legend: `P` positive exercise in the valid case; an invalid-mutation ID is a negative exercise; `—` deliberately not applicable. Every row has positive or negative coverage. Rows combine only where BCRP assigns one inseparable validation responsibility; independently owned responsibilities remain separate.

### 7.1 Mandatory semantic responsibilities

| Responsibility | C1 valid | C1 invalid | C2 valid | C2 invalid | C3 valid | C3 invalid |
|---|---|---|---|---|---|---|
| Organizing purpose | P | C1-I01 | P | — | P | — |
| Audience description | P | — | P | — | P | — |
| Generic subjects/external refs | P | C1-I02 | P | C2-I11 | P | — |
| Upstream authority | P | C1-I05 | P | C2-I01 | P | — |
| Provenance | P | C1-I05 | P | C2-I04 | P | — |
| Evidence-snapshot identity | P | — | P | — | P | C3-I09 |
| Materialized values | P | — | P | C2-I02–I05 | P | C3-I03 |
| Semantic types and units | P | — | P | C2-I05 | P | — |
| Value state | P | — | P | C2-I02–I05 | P | — |
| Evidence state | P | — | P | C2-I03–I04 | P | C3-I09 |
| Consistency state | P | — | P | C2-I04 | P | — |
| Lifecycle references | P | C1-I07 | P | — | P | C3-I09 |
| Presentation statements | P | — | P | C2-I06–I07 | P | C3-I03–I05 |
| Content posture | P | — | P | C2-I06–I07 | P | C3-I04 |
| Communication function | P | — | P | — | P | — |
| Attention/prominence | P | — | P | — | P | — |
| Encounter/composition | P | C1-I04 | P | — | P | C3-I04 |
| Caveats | P | C1-I03 | P | — | P | C3-I06 |
| Uncertainty | P | — | P | — | P | C3-I06 |
| Personal annotations | — | — | P | C2-I06 | — | — |
| Presentation obligations | P | C1-I03 | P | — | P | C3-I06 |
| Sections/navigation intent | P | C1-I04 | P | — | P | C3-I07 |
| Exhibit/visualization intent | P | C1-I06 | P | C2-I09 | P | C3-I03 |
| Sensitivity/distribution | P | — | P | C2-I08 | P | — |
| Transformation permissions | P | C1-I06 | P | — | P | C3-I06 |
| Renderer requirements | P | C1-I06 | P | C2-I09 | P | C3-I07–I08 |
| Fallback declarations | P | — | P | C2-I09 | P | C3-I06–I08 |
| Selection sets | — | — | — | — | P | C3-I01–I10 |
| Selection states | — | — | — | — | P | C3-I01–I10 |
| State-specific applicability | — | — | — | — | P | C3-I03–I06 |
| Narrative invariants/variants | — | — | — | — | P | C3-I04–I06 |
| Candidate/Judgment/Ready linkage | P | — | P | — | P | C3-I09 |
| Release identity/lifecycle | P | C1-I07 | P | — | P | C3-I09 |
| Manifest derivation | P | C1-I07 | P | — | P | — |
| Renderer/artifact identity | P | C1-I09 | P | — | P | — |
| Traceability evidence | P | C1-I02/I09 | P | C2-I04 | P | C3-I09 |
| Semantic conformance evidence | P | C1-I08 | P | — | P | C3-I05–I06 |

### 7.2 Validation layers

| Layer | C1 valid | C1 invalid | C2 valid | C2 invalid | C3 valid | C3 invalid |
|---|---|---|---|---|---|---|
| L0 intake | P | C1-I01 block | P | — | P | — |
| L1 profile structure | P | C1-I02 block | P | C2-I05/I10/I11 block | P | C3-I01/I02 block |
| L2 semantic contract | P | C1-I03–I05 block | P | C2-I01–I07/I11 block | P | C3-I01–I10 block |
| L3 lifecycle/readiness | P | C1-I07 block | P | — | P | C3-I09 block |
| L4 governance approval | P explicit release authority | — | P explicit synthetic authority | C2-I08 block | P explicit release authority | — |
| L5 compatibility/plan | P | C1-I06 block | P | C2-I09 block | P | C3-I06–I08 block/native-fallback branch |
| L6 output conformance | P audit + semantic | C1-I07–I09 block | P audit + semantic | — | P audit + semantic | C3-I05/I06 block |

Layer 4 legitimately has no machine-derived “pass”; the corpus proves presence or absence of an explicit governance record and expects the validator to refuse inference. C2-I08 supplies its blocking case.

### 7.3 TASK-043 cross-layer invariants

| Invariant | C1 valid | C1 invalid | C2 valid | C2 invalid | C3 valid | C3 invalid |
|---|---|---|---|---|---|---|
| 1 semantic reconstruction | P | C1-I02 | P | C2-I10 | P | C3-I02 |
| 2 round trip | P | — | P | — | P | — |
| 3 authority | P | C1-I05 | P | C2-I01/I06/I07 | P | — |
| 4 identity separation | P | C1-I09 | P | — | P | C3-I09 |
| 5 fingerprint scope | P | C1-I09 | P | — | P | C3-I09 |
| 6 reference integrity | P | C1-I02 | P | — | P | — |
| 7 obligation reachability | P | C1-I03 | P | — | P | C3-I06 |
| 8 explicit states | P | — | P | C2-I02–I05 | P | C3-I09 |
| 9 composition acyclicity/order | P | C1-I04 | P | — | P | C3-I04 |
| 10 selection closure | — | — | — | — | P | C3-I01–I03/I10 |
| 11 narrative consistency | P | C1-I05 | P | C2-I06/I07 | P | C3-I04–I06 |
| 12 transformation authorization | P | C1-I06 | P | — | P | C3-I05–I07 |
| 13 fallback completeness | P | — | P | C2-I09 | P | C3-I06–I08 |
| 14 traceability not conformance | P | C1-I08/I09 | P | — | P | C3-I05 |
| 15 version sovereignty | P | C1-I07 | P | — | P | C3-I09 |
| 16 standalone operation | P | — | P | — | P | C3-I06/I08 |
| 17 scope/AtlasForge/finance boundary | P | — | P | C2-I11 | P | — |

### 7.4 Lifecycle and renderer/fallback boundaries

| Boundary/responsibility | C1 valid | C1 invalid | C2 valid | C2 invalid | C3 valid | C3 invalid |
|---|---|---|---|---|---|---|
| Brief -> portable material | P | C1-I01 | P | — | P | — |
| material -> Candidate | P | C1-I02/I05 | P | C2-I01–I05 | P | C3-I03 |
| Candidate -> Judgment -> Ready | P | C1-I03–I05 | P | C2-I01–I07 | P | C3-I01–I04 |
| Ready -> release | P | C1-I07 | P | C2-I08 | P | C3-I09 |
| release -> compatibility plan | P | C1-I06 | P | C2-I09 | P | C3-I07/I08 |
| plan -> artifact/audit | P | C1-I09 | P | — | P | C3-I05 |
| artifact -> semantic acceptance | P | C1-I08/I09 | P | — | P | C3-I05/I06 |
| release/artifact -> manifest | P | C1-I07 | P | — | P | — |
| native verified expression | P | — | P | C2-I09 | P | C3-I07 |
| equivalent expression | P | C1-I06 | P | — | P | C3-I06 |
| complete static fallback | P | — | P | C2-I09 | P | C3-I06 |
| print fallback | P | — | P | — | P | C3-I08 |
| explicit unsupported/fail closed | P | C1-I06 | P | C2-I09 | P | C3-I07 |
| scoped styles/deep links/standalone | P | — | P | — | P | C3-I07 |
| optional AtlasForge catalogue | P | C1-I07 | P | — | P | — |

No mandatory responsibility is unexercised. A fourth primary case is neither necessary nor authorized.

## 8. Fixture safety, redaction and durability

Future materialized fixtures must satisfy all of the following:

- no secrets, credentials, tokens, personal data, proprietary raw data, or actual sensitive content;
- no live API, database, network, AtlasForge, or mutable upstream-path dependency;
- no absolute machine-specific paths in profile semantics or expected output;
- deterministic local reproduction from retained fixture material;
- public-source attribution retained where public evidence is used;
- fictional company names conspicuously marked synthetic in brief, package, publication, and manifest;
- sensitivity/distribution tested with labels, authority and withheld placeholders, never real sensitive payload;
- small bounded values and narratives sufficient to expose each failure; no raw-data dump;
- integrity fingerprints computed only after canonicalization prerequisites pass;
- invalid variants produced mechanically from accepted valid bases where practical, not separately drifting handwritten copies.

### 8.1 TASK-039 reuse rule

When Case 1 is later materialized:

- **May copy:** bounded public/non-sensitive coefficient values, method descriptions, caveat text, source attribution, and organizing-purpose substance when licensing/ownership permits.
- **May transform:** overloaded current statements into BCRP's independent posture/function/attention/relation/state forms; absolute paths into stable generic external refs plus retained fixture-relative source notes; Markdown table content into materialized values and exhibit intent.
- **May reference:** TASK-039 task/report/decision and retained publication evidence as historical provenance during corpus construction.
- **Must reduce:** source material to the minimum deterministic evidence needed for the case.
- **Must not copy as canonical:** current Candidate/Ready JSON shape, current fingerprint, renderer-input shape, absolute paths, or audit metadata assertion that no table exists.
- **Must not modify:** any TASK-039 artifact or the InsightForge source fixture.

The known table-metadata inconsistency is an invalid historical input condition. The future valid case must make exhibit intent and artifact evidence agree.

## 9. Acceptance gate

The three cases jointly cover every mandatory profile responsibility, every TASK-043 validation layer, all 17 cross-layer invariants, publication lifecycle boundaries, renderer compatibility, fail-closed fallback, audit linkage, semantic conformance, DSB-007, and optional AtlasForge consumption without dependency.

The corpus plan therefore passes acceptance for later bounded materialization under TASK-045. Materialization remains prohibited in TASK-044.
