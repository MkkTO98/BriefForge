# Publication Boundary, Intake, Portability, and Lifecycle Specification

Date: 2026-07-16
Status: accepted semantic specification; no representation or implementation authorized
Owner: BriefForge
Scope: TASK-041

## 1. Purpose and authority

This specification defines the smallest semantic foundation by which BriefForge can receive governed presentation needs and portable upstream-owned material, construct and validate a Presentation Package, publish an identified semantic release, generate derivative artifacts, and emit derivative catalogue metadata without acquiring analytical, ingestion, renderer-platform, portal, or financial-domain authority.

Authority order for this specification:

1. `CONSTITUTION.md` remains constitutional authority.
2. Existing Presentation Package, validation/promotion, renderer-adapter, and rendered-conformance contracts remain authoritative in their established scopes.
3. ADPM remains a distinct architectural decision-package domain; this specification reuses its authority-separation and immutable-lineage principles but does not merge ADPM with Presentation Packages.
4. This specification decides publication responsibilities that TASK-040 found missing or partial.
5. Representation, serialization, schema, validation implementation, and renderer implementation remain deferred.

## 2. Preserved concepts and non-duplication rules

The following are reused unchanged in responsibility:

- Presentation Contract;
- Organizing Purpose;
- Composition Semantics and Presentation Grammar;
- PresentationStatement and EncounterSemantics;
- PresentationObligation;
- UpstreamReference;
- CandidatePresentationPackage;
- ValidationJudgment;
- ReadyPresentationPackage;
- Candidate -> Judgment -> Ready;
- semantic fingerprint and deterministic authoring identifiers;
- RendererAdapterRequest and renderer capability declaration;
- renderer identity/version;
- rendered-artifact conformance;
- non-canonical rendered artifact;
- source evidence owner, semantic review, publication expression, published artifact, derived view, and local adoption authority;
- separation of ADPM semantic version from representation-profile version.

Consequent rules:

1. No publication object duplicates presentation readiness or promotion.
2. Pre-candidate intake is not RendererAdapterRequest.
3. Portable material is not acquisition, canonicalization, normalization, analysis, or upstream acceptance.
4. A manifest is not semantic authority, registry authority, or portal state.
5. A renderer consumes authoritative presentation meaning read-only and creates no evidence or analytical authority.
6. Rendered artifacts remain derivative and non-canonical.

## 3. Accepted terminology

### 3.1 Presentation Intake

`Presentation Intake` is the governed pre-candidate boundary through which a requestor supplies a bounded communication need and the material/authority declarations needed to determine whether candidate construction may begin.

It contains two distinct semantic responsibilities:

1. **Presentation Brief** — the requestor's communication instruction: purpose, audience, decision/communication context, subjects, requested publication category/output/interactions, requestor identity, and constraints.
2. **Portable Presentation Material** — materialized upstream-governed content and declarations required for offline candidate construction, validation, and regeneration.

These responsibilities are distinct because communication need does not establish evidence truth, while material authority does not establish BriefForge presentation approval. They form one intake boundary rather than two readiness lifecycles.

An intake may be incomplete, rejected, or admitted for candidate construction. Admission is not presentation validity, approval, readiness, or publication.

### 3.2 Portable Presentation Material

`Portable Presentation Material` is a retained, integrity-identifiable set of already governed or accepted upstream material sufficient for BriefForge to perform its presentation responsibilities without the upstream runtime being online.

The term is preferred over `ResolvedInput` because BriefForge does not resolve analytical disputes, missing evidence, financial meaning, or upstream authority.

### 3.3 Fixed-evidence standalone publication

A `fixed-evidence standalone publication` is a publication release bound to one identified evidence snapshot and one exact Ready Presentation Package fingerprint, reproducible from retained portable inputs, complete without AtlasForge, and deterministic at the semantic level.

The term `frozen publication` is rejected. `Freeze` already denotes constitutional and ADPM governance states; reusing it would confuse publication release with package approval/freeze authority.

### 3.4 Bounded parameterized publication

A `bounded parameterized publication` is a deferred category, not an admitted capability. It may be considered only when later semantic-authority work proves all of the following:

- finite predeclared state space;
- every selectable value/view is prevalidated;
- affected statements/components are known;
- narrative behaviour is valid for every state;
- evidence validity and obligations are preserved;
- deterministic static fallback exists;
- no analytical recomputation occurs.

TASK-041 authorizes no selector, interaction runtime, parameter representation, or parameterized publication instance.

### 3.5 Publication Release Record

A `Publication Release Record` is the immutable BriefForge-owned semantic record that a specific Ready package fingerprint, evidence snapshot, publication identity/version, and lifecycle state were released for publication at a stated time.

It is genuinely distinct from Ready Presentation Package because Ready establishes presentation validity, while a release record establishes publication identity, release time, evidence binding, publication lineage, and post-release status. It is not a second validation or promotion lifecycle and does not copy package content.

### 3.6 Publication manifest

A `publication manifest` is machine-readable, derivative catalogue and embedding metadata emitted from authoritative BriefForge records. It is not the semantic source of truth and cannot independently change publication identity, status, lineage, evidence binding, or presentation meaning.

## 4. Publication-layer model

| Layer | Owner | Semantic authority | Mutability and identity | Inputs -> outputs | Failure responsibility | Canonical/derivative | Offline existence |
|---|---|---|---|---|---|---|---|
| 1. Upstream evidence and accepted statements | Upstream evidence/analysis owner | Evidence meaning, findings, provenance, caveats, acceptance | Governed upstream; identified/versioned under upstream rules | Source work -> accepted evidence/statements | Upstream owner | Canonical only in upstream domain; referenced by BriefForge | A retained snapshot can exist offline |
| 2. Presentation Intake | Requestor for brief; upstream authority for material declarations; BriefForge for admission | Requestor owns communication need; upstream owns supplied meaning; BriefForge owns intake compatibility | Mutable until admitted/rejected; intake identity is authoring/audit identity, not publication identity | Brief + portable material -> admitted/incomplete/rejected intake | Requestor fixes brief; upstream owner fixes material/authority; BriefForge explains presentation rejection | Governed authoring input, not canonical package | Yes, when retained |
| 3. Candidate Presentation Package | BriefForge author/builder | Proposed presentation meaning only | Mutable candidate; deterministic package identity/fingerprint | Admitted intake -> candidate | Candidate constructor | Canonical candidate for review, not ready authority | Yes |
| 4. Validation Judgment | BriefForge validation/review authority | Classified presentation-validity findings, not evidence truth | Immutable judgment tied to candidate fingerprint/policy | Candidate -> judgment | BriefForge validation function; upstream issues remain upstream | Authoritative for the validation act | Yes |
| 5. Ready Presentation Package | BriefForge promotion authority | Validated presentation meaning | Immutable exact fingerprint after promotion | Valid judgment + candidate -> Ready package | Promotion authority | Canonical presentation package for downstream expression | Yes |
| 6. Publication Release Record | BriefForge publication authority | Publication identity, semantic version, evidence binding, release time, lifecycle/lineage | Immutable event/record; later events or releases do not rewrite it | Ready package + evidence snapshot + publication approval -> release record | BriefForge publication authority | Canonical only for BriefForge publication lifecycle; does not replace Ready package | Yes |
| 7. Renderer invocation | Renderer adapter boundary | No semantic/evidence authority | Request identity/version as operational audit data | Ready package + release context + declared renderer capability -> invocation/result | Adapter rejects unsupported/mismatched invocation; renderer failure remains renderer-side | Non-canonical operational instruction | Yes if renderer installed; release remains valid if not |
| 8. Generated publication artifact | Renderer/publication layer | No semantic authority | Immutable artifact instance; new generation gets new artifact identity/version | Read-only semantic inputs -> HTML/SVG/PDF/etc. | Renderer/publication pipeline; corruption does not invalidate semantic release | Derivative | Yes; standalone artifact must not require upstream runtime |
| 9. Publication manifest | BriefForge publication emitter | No independent authority | Regenerable derivative with own artifact identity/version | Release, Ready, renderer and artifact records -> metadata | Emitter must reject conflicts and regenerate from authorities | Derivative | Yes |
| 10. Downstream catalogue/embedding surface | AtlasForge or another consumer | Local catalogue/display authority only | Consumer-owned | Manifest/artifact -> link/catalogue/embed | Consumer | Derived view | BriefForge publication remains complete without it |

## 5. Presentation Intake semantics

### 5.1 Minimum Presentation Brief

A valid Presentation Brief must express, semantically rather than as a prescribed field layout:

- Organizing Purpose or enough explicit material to propose one without inventing analytical meaning;
- intended audience description;
- decision or communication context;
- subjects in scope and explicit non-scope;
- requested publication category;
- output target;
- requested interactions;
- requestor identity;
- sensitivity and distribution constraints;
- upstream evidence authority;
- BriefForge presentation approval authority;
- forbidden inferences and transformations.

Minimum audience semantics are limited to:

1. who must understand or use the presentation;
2. what decision/communication context they occupy;
3. material knowledge assumptions or terminology needs that affect truthful communication;
4. accessibility, sensitivity, or distribution constraints that affect presentation obligations.

Personas, behavioral segmentation, personalization, recommendation engines, sessions, and user profiling are prohibited.

### 5.2 Intake outcomes

- **Admitted for candidate construction** — the brief is bounded, required authority is declared, portable material is sufficient, and no prohibited responsibility is requested.
- **Incomplete** — candidate construction must not begin; missing items and responsible owner are identified without silently filling them.
- **Rejected** — the request requires prohibited analysis/ingestion/inference, lacks a lawful authority boundary, requests an unsupported publication category/interaction, or conflicts with constitutional obligations.

An intake never becomes a Candidate automatically. Candidate construction is a separate BriefForge authoring act.

### 5.3 Required rejection behaviour

BriefForge must reject or return incomplete when:

- Organizing Purpose is absent and cannot be restated from requestor-owned communication intent without new analytical inference;
- evidence authority or accepted-finding authority is absent/ambiguous;
- requested material is missing, conflicting, unverifiable, or not portable enough for the requested fixed-evidence publication;
- the request asks BriefForge to calculate, infer, rank, compare, select evidence, or create accepted findings;
- requested interaction requires analytical recomputation or unproven declared selection;
- sensitivity/distribution constraints are missing where material is governed;
- speculative company/financial semantics under DSB-007 would be required;
- output depends on a live upstream or AtlasForge runtime.

## 6. Portable Presentation Material semantics

### 6.1 Authority and materialization

The upstream semantic/evidence owner, or an explicitly authorized exporter acting for that owner, materializes and asserts the meaning of Portable Presentation Material. A requestor may transport it but cannot acquire authority merely by doing so.

BriefForge validates only:

- integrity and identity;
- declared ownership/authority;
- completeness for the requested presentation purpose;
- internal reference consistency;
- compatibility with Presentation Contract and obligations;
- presence of needed caveats, provenance, units/types/subjects, sensitivity/distribution constraints, and permitted transformations/interactions;
- ability to reproduce the fixed-evidence presentation without live upstream access.

BriefForge does not validate analytical truth, re-accept findings, normalize domain meaning, or repair upstream material.

### 6.2 Permitted semantic content

Portable material may contain only already governed/accepted presentation-relevant material, including:

- upstream reference identities and authority declarations;
- materialized exhibit values and semantic types;
- units and subjects;
- accepted upstream statements/findings;
- evidence scope and evidence-snapshot identity;
- caveats, limitations, provenance, freshness/review declarations;
- sensitivity and distribution constraints;
- permitted presentation transformations;
- requested/permitted interactions;
- generic typed external references and bounded extensions.

It must not contain speculative financial-domain canonical fields merely for future convenience.

### 6.3 Association with candidate packages

Portable Presentation Material is associated with, not automatically embedded wholesale in, CandidatePresentationPackage.

A candidate must retain:

- UpstreamReferences to authoritative identities;
- the exact material/evidence-snapshot fingerprint used;
- the presentation statements and obligations derived without altering upstream meaning;
- enough retained portable material, directly or through immutable associated artifacts, for standalone validation/regeneration.

Embedding is a later representation choice. Semantically, deletion or unavailability of all retained material needed to reconstruct a fixed-evidence release breaks reproducibility and must block release/regeneration; it must not trigger live reacquisition or silent substitution.

### 6.4 Reproducibility

Reproducibility requires integrity fingerprints over:

1. the retained Portable Presentation Material set;
2. the exact Ready Presentation Package;
3. the Publication Release Record;
4. renderer identity/version and declared capabilities for each artifact generation;
5. generated artifact bytes or equivalent deterministic artifact identity;
6. the manifest artifact when emitted.

A fingerprint proves identity/integrity, not truth or authority.

## 7. Relationship to Candidate -> Judgment -> Ready

The accepted sequence is:

```text
Upstream governed material + requestor communication need
-> Presentation Intake (admit / incomplete / reject)
-> Candidate construction
-> Candidate Presentation Package
-> Validation Judgment
-> Ready Presentation Package
-> publication approval
-> immutable Publication Release Record
-> RendererAdapterRequest / renderer invocation
-> generated publication artifact
-> rendered-artifact conformance
-> derivative publication manifest
-> optional downstream catalogue/embed
```

Rules:

- Intake admission does not imply candidate validity.
- Validation Judgment does not imply publication.
- Ready does not imply that a publication was released.
- Publication approval does not revalidate presentation semantics; it checks exact Ready/evidence binding, authority, category, and release obligations.
- Release status does not mutate Ready package status.
- Artifact conformance does not confer semantic authority.

## 8. Publication identities and version sovereignty

Distinct axes are mandatory:

| Axis | Authority and change rule |
|---|---|
| Semantic publication identity | Stable identity for one publication lineage/family across semantic versions. Changes when it is a different bounded publication purpose, not merely a correction. |
| Semantic publication version | Changes whenever released presentation meaning, organizing purpose/scope, bound evidence snapshot, or semantic obligations change. |
| Evidence-snapshot identity | Upstream-owned or upstream-authorized identity of exact material basis. Replacement requires a new semantic publication version and new validation judgment/Ready fingerprint unless proven byte/meaning identical under upstream authority. |
| Ready package identity/fingerprint | Exact immutable presentation package used by a release. Any semantic package change produces a new fingerprint and judgment. |
| Renderer identity/version | Identifies derivative transformation implementation. Changes do not by themselves change semantic publication version. |
| Generated-artifact identity/version | Identifies each generated output instance/lineage. Changes on rerender, regeneration, correction, format change, or byte change. |
| Manifest artifact identity/version | Identifies derivative manifest generation. Changes when manifest bytes/content change; never changes semantic authority by itself. |
| Publication/release time | Time the semantic version was first released; remains stable across renderer-only regeneration. |
| Lifecycle-event time | Time a correction, supersession, withdrawal, or staleness declaration occurred. |

No single version number may stand for all axes.

## 9. Publication lifecycle events

| Event | Change | Stable identity | Version consequence | New judgment? | Prior artifact | Relationship/manifest | Semantic authority effect |
|---|---|---|---|---|---|---|---|
| Initial publication | First approved release of exact Ready/evidence binding | New publication identity | Initial semantic version; initial artifact/manifest versions | Existing valid judgment required | N/A | Manifest exposes active initial release | Establishes publication release authority only |
| Semantic correction | Presentation meaning or accepted value/caveat/scope changes | Publication identity usually stable | New semantic version, Ready fingerprint, artifacts, manifest | Yes | Remains addressable and marked superseded/amended as applicable | Explicit replacement lineage required | New semantic release; old history retained |
| Renderer-only correction/rerender | CSS/layout/accessibility/output mechanics change without semantic meaning | Publication identity/version and Ready/evidence stable | New renderer version if code changed; new artifact version; manifest version changes if metadata changes | No semantic judgment; output conformance required | Remains addressable unless corrupt and access policy marks it defective | Manifest identifies replacement artifact and unchanged semantic version | None |
| Supersession | A later semantic release replaces prior release for current use | Publication lineage identity may remain stable or explicit related identity if purpose changed | New semantic version when same lineage | Yes for new Ready | Prior remains addressable | `supersedes`/`superseded_by` required | New release becomes current; old remains historically authoritative for its time |
| Withdrawal | Authority declares release should not be used | Publication/release identity stable | No automatic semantic-version change; lifecycle event/manifest versions change | No, unless replacement created | Must remain historically addressable or tombstoned with identity/evidence preserved | Withdrawal status, time, authority, reason, replacement if any | Removes active-use authority; does not erase history |
| Staleness | Upstream or publication authority declares currency concern | Publication/release identity/version stable | Lifecycle event/manifest version changes | No; replacement requires new judgment | Remains addressable with visible status | Status, declaration source/time/reason exposed | Qualifies current-use authority; no monitoring ownership implied |
| Regeneration without semantic change | Same Ready/evidence rendered again | Publication identity/version stable | New artifact identity/version; renderer version only if renderer changed | No; conformance required | Prior remains addressable according to retention policy | Manifest may point to current and retain lineage | None |
| Evidence-snapshot replacement | Material basis changes | Publication identity may remain stable if same purpose | New evidence ID, semantic version, Ready fingerprint, artifacts, manifest | Yes | Prior remains addressable | Supersession/amendment lineage required | New semantic release |
| Manifest regeneration | Derivative metadata is re-emitted from unchanged authorities | All semantic identities stable | Manifest artifact version only | No | Prior manifest may remain addressable | New manifest must reproduce authoritative state | None |

Staleness is declared or propagated from an upstream authority statement or BriefForge publication-governance decision. BriefForge is not required or authorized to poll upstream systems.

## 10. Publication-manifest property classification

Each property has one primary classification. `Required` properties may be copied/derived from authoritative records, but the manifest must contain them. `Derived` means optional redundant convenience data whose omission does not impair the minimal contract.

| Property | Classification | Authoritative source / rule |
|---|---|---|
| Manifest artifact identity and version | Required | Manifest generation record; identifies regeneration without claiming semantic authority |
| Publication identifier | Required | Publication Release Record |
| Semantic publication version | Required | Publication Release Record |
| Title | Required | Exact Ready package identity/presentation data |
| Organizing Purpose | Required | Exact Ready package |
| Publication category | Required | Publication Release Record; currently fixed-evidence standalone only |
| Evidence-snapshot identifier | Required | Upstream-authorized Portable Presentation Material / release binding |
| Ready package identity and semantic fingerprint | Required | Ready Presentation Package |
| Renderer identity/version | Required per generated artifact | Renderer invocation/result |
| Generated-artifact identity/version | Required | Artifact generation record |
| Publication/release time | Required | Publication Release Record |
| Lifecycle status | Required | Authoritative publication lifecycle record |
| Supersedes/superseded-by relationships | Optional, conditionally required when applicable | Publication lineage record |
| Withdrawal status/time/reason/authority | Optional, conditionally required when withdrawn | Lifecycle event record; historical identity retained |
| Staleness status/time/reason/declarer | Optional, conditionally required when stale | Lifecycle event or propagated upstream declaration |
| Stable section/statement identifiers and deep links | Derived | Ready identifiers + artifact anchors; only when emitted artifact supports them |
| Available artifact formats | Required | Artifact inventory |
| Standalone entry point | Required | Generated artifact inventory |
| Sensitivity/distribution designation | Required | Ready obligations + upstream constraints |
| Reproducibility fingerprint(s) | Required | Retained material, Ready, release, renderer and artifact identities |
| Optional embedding information | Optional | Artifact-safe dimensions/entry point or equivalent; no AtlasForge routes or portal semantics |
| Audience description | Derived | Ready/intake semantics; may be exposed when distribution policy permits |
| Requestor identity | Prohibited by default | Intake audit data is not catalogue metadata unless an explicit distribution obligation permits it |
| AtlasForge route, search index, rank, portal collection, user/session, or global navigation state | Prohibited | AtlasForge-owned application/platform concerns |
| Serialization/schema hints for canonical semantics | Prohibited | Manifest is derivative, not representation authority |
| Parameter state or selector definition | Deferred | Depends on later semantic-authority decision |
| Detailed missing/conflicting/invalid evidence-state vocabulary | Deferred | Later semantic-authority/failure task |

Conflict rule: if a manifest conflicts with Ready package, Publication Release Record, lifecycle event, renderer result, or artifact inventory, the manifest is invalid and must be rejected/regenerated. It never corrects an authority.

## 11. AtlasForge integration boundary

AtlasForge or another downstream surface may:

- consume emitted publication manifests;
- catalogue publication identities and semantic versions;
- link to standalone artifacts;
- embed artifacts when distribution and embedding information permit;
- retain its own local catalogue/view state.

BriefForge must not know or depend on:

- AtlasForge routes, indices, portal collections, ranking, discovery/search, users, sessions, permissions implementation, or global navigation;
- AtlasForge runtime availability;
- AtlasForge entity-page or analytical application semantics.

AtlasForge absence/failure cannot invalidate a BriefForge release, Ready package, artifact, or manifest. AtlasForge cannot mutate BriefForge semantic or lifecycle authority.

## 12. Derivative publication versus application/platform responsibility

Existing doctrine is coherent when `ownership` is read as constitutional responsibility rather than a ban on every local transformation implementation. `CONSTITUTION.md` excludes rendering engines/browser applications as BriefForge architecture while its implementation bridge permits concrete representations that preserve the frozen core. Existing adapter, minimal HTML/SVG, conformance, and TASK-039 evidence prove bounded derivative publication expression.

Permitted derivative behaviour:

- standalone generated documents;
- deterministic layout and formatting;
- stable internal navigation and anchors;
- native disclosure/inspection;
- bounded static exhibits;
- scoped styles;
- print-safe or accessible derivative forms;
- renderer-local mechanics that do not alter meaning, evidence, obligations, or authority.

Prohibited application/platform behaviour:

- persistent application state;
- analytical recalculation;
- arbitrary filtering, querying, comparison, or exploration;
- dashboards;
- routing systems and cross-report portal navigation;
- global search/discovery/ranking;
- visualization engines or grammars;
- component/template platforms;
- live entity or continuously updated company pages.

A bounded renderer implementation is therefore an approved derivative capability, not a constitutional rendering-engine responsibility. The three accepted TASK-041 decisions are sufficient clarification. No constitutional amendment is necessary now. Declared/prevalidated selection remains unresolved and deferred.

## 13. Explicit exclusions and deferrals

Rejected now:

- `frozen publication` terminology;
- publication as a mere mutable status field on Ready Presentation Package;
- publication artifact or manifest as canonical semantic authority;
- a second Candidate/Ready or promotion lifecycle;
- intake as RendererAdapterRequest;
- portable input as live upstream lookup or BriefForge-owned resolution;
- AtlasForge dependency or implementation;
- any financial-domain semantic fields under DSB-007;
- browser/application/platform expansion.

Deferred:

- bounded parameterized publication admission and declared/prevalidated selection;
- accepted statement-role taxonomy;
- interaction authority beyond navigation/inspection;
- explicit missing/conflicting/invalid/stale/withdrawn evidence-state taxonomy (publication lifecycle staleness/withdrawal are defined here, evidence semantics are not);
- renderer transformation sovereignty details and capability fallback semantics;
- all representations, serialization, schemas, validators, builders, emitters, and renderer implementation.

## 14. Gate

**CLEAR TO PROCEED** to one later specification-and-decision task: `Semantic Authority, Evidence States, Interaction, and Renderer Fallback Foundations`.

This gate authorizes only that bounded semantic task. No representation, schema, serializer, validator, runtime, renderer, interaction, manifest emitter, or AtlasForge implementation is authorized until both foundational semantic layers are coherent and separately gated.
