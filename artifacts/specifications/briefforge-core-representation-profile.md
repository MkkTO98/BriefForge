# BriefForge Core Representation Profile

Date: 2026-07-16
Status: accepted specification
Task: TASK-044
Profile identity: `briefforge-core-representation-profile`
Profile version: `1.0.0`
Short name: BCRP 1.0
Authority: renderer-independent profile subordinate to `CONSTITUTION.md`, ADPM doctrine, and the accepted TASK-041 through TASK-043 specifications

## 1. Decision and scope

BriefForge accepts exactly one initial Representation Profile: **BriefForge Core Representation Profile 1.0.0 (BCRP 1.0)**.

BCRP is a transport-neutral mapping from the TASK-043 semantic graph to independently addressable typed records joined by stable identity references. It is not a serialization, schema, renderer request, database model, API, template system, or UI ontology. It preserves Candidate -> Validation Judgment -> Ready and the TASK-041 publication lifecycle rather than duplicating either.

BCRP 1.0 targets fixed-evidence standalone publications and also represents finite, fully materialized prevalidated selection. It does not admit live queries, computed selections, mutable upstream state, or open-ended exploration.

## 2. Profile and bundle topology

A **BCRP bundle** is a bounded set of records sufficient for the intended operation. It need not be one file or one monolithic record. A non-semantic `ProfileBundleIndex` may inventory record kind, stable record identity, profile version, content-integrity digest, and relative transport locator. Index order and locator are not semantic. Missing records required by the dependency closure block processing.

Canonical status below means authoritative for the named responsibility, not canonical for upstream domain meaning.

| Independently addressable record | Semantic owner | Identity and version binding | Status | Permitted dependencies | Offline retention | Candidate semantic fingerprint | Regeneration / lifecycle |
|---|---|---|---|---|---|---|---|
| `PresentationBriefRecord` | presentation requestor plus BriefForge intake authority | brief ID; BCRP version; intake-contract version | canonical intake record | authority declarations, generic external refs, organizing purpose/audience/scope obligations | required through intake audit; retained with released reproduction evidence when relied upon | excluded; Candidate keeps trace refs | may precede material/Candidate; replacement gets new identity or explicit lineage |
| `PortablePresentationMaterialRecord` | upstream semantic/evidence owners; exporter owns materialization | material ID/version; BCRP version; upstream object/snapshot IDs | canonical portable-input record, not canonical package | external refs, authority assertions, materialized values, source states, obligations, authorized transformations | required for offline validation/regeneration of any dependent release | included only through Candidate-referenced semantic dependencies; unrelated material excluded | may precede Candidate; immutable referenced instance; rematerialization gets new version/fingerprint |
| `CandidatePresentationPackageRecord` | BriefForge presentation author | package lineage ID + Candidate instance ID; ADPM semantic version where applicable; BCRP version | canonical presentation proposal | brief/material trace refs; purpose; audience; statements; relations; states; obligations; selections; renderer requirements | required | defines the Candidate semantic fingerprint over its transitive canonical semantic closure | revisable conceptually; each fingerprinted instance immutable; replacement precedes new Judgment |
| `ValidationJudgmentRecord` | named validation authorities by layer | judgment ID; exact Candidate ID/fingerprint; policy/contract/profile versions | canonical finding/judgment record | Candidate, executed-layer declarations, findings | required with Ready | excluded from Candidate fingerprint; has its own profile-instance fingerprint | may follow Candidate only; may be rerun as new judgment; cannot rewrite prior judgment |
| `ReadyPresentationPackageRecord` | BriefForge readiness policy | Ready ID; exact Candidate ID/fingerprint; one successful Judgment ID | canonical readiness binding | Candidate and successful Judgment only | required | excluded; binds but does not alter Candidate fingerprint | follows successful Judgment; immutable historical fact; cannot absorb release/artifact identity |
| `PublicationReleaseRecord` | publication release/lifecycle authority | publication lineage ID, semantic publication version, release ID; exact Ready fingerprint and evidence snapshots | canonical publication identity/lifecycle record | Ready, snapshots, lifecycle events, release authority; artifact-record refs | required | excluded from Candidate fingerprint; release semantic fingerprint is separately scoped | follows Ready/governance authority; corrected meaning creates new semantic version/release; lifecycle events append without rewriting history |
| `RendererCapabilityDeclarationRecord` | renderer owner | renderer ID/version + capability-declaration version | authoritative renderer declaration, non-canonical to package | verification evidence and supported requirement/fallback classes | retained for every released artifact | excluded | may precede plan; replace/version when capability evidence changes |
| `RendererCompatibilityPlanRecord` | BriefForge adapter/compatibility authority | plan ID/version; exact Ready, renderer, capability declaration, policy | authoritative compatibility/expression determination, not package semantics | Ready requirements; renderer declaration; admitted fallbacks | required for reproduction/conformance | excluded | follows Ready and capability declaration; may be regenerated only to the same canonical result under same inputs/policy, otherwise new plan ID/version |
| `GeneratedArtifactAuditRecord` | renderer invocation/audit producer under BriefForge audit contract | audit ID; request ID; release, Ready, plan, renderer and artifact IDs/versions | derivative audit evidence | release; Ready; renderer request/plan; renderer; generated artifact integrity | required for accepted artifact | excluded | follows rendering; regenerated evidence is a new audit record and cannot alter source authorities |
| `SemanticArtifactConformanceRecord` | BriefForge output-conformance authority | conformance ID; policy; exact audit/artifact/plan/release identities | canonical conformance finding record, not semantic package | artifact audit; expression plan; Ready graph; output inspection evidence | required for accepted artifact | excluded | follows artifact; rerun creates new record; cannot make a failed artifact valid by relabelling |
| `PublicationManifestRecord` | BriefForge manifest projector | manifest artifact ID/version + projection-policy version | derivative projection | authoritative release, lifecycle, accepted artifact audits/conformance | required with standalone publication and optional catalogue handoff | excluded | follows release/artifacts; may regenerate only from current authorities; never overrides them |

A bundle may contain several instances of a record kind. Record identity, never file position, determines addressability. Transport locators are relative conveniences and must not become identity.

## 3. Shared profile record forms

BCRP uses the following abstract forms. Concrete field syntax is deferred to a transport profile.

- `Identity`: stable identifier, declared scope (`bundle`, `package`, `release-lineage`, `project`, or `external-authority`), object kind, and optional explicit version/lineage reference.
- `TypedReference`: relationship kind, target identity, target kind, and external-boundary declaration when the target is not retained locally.
- `AuthorityAssertion`: assertion ID, authority role, owner identity, exact scope/subjects, source/provenance references, and limitations. Authority is never inferred from record location.
- `ExternalReference`: package-stable reference ID, owner, generic reference kind, upstream object identity/version/fingerprint where supplied, evidence-snapshot identity, optional locator, and declared limitations. A locator is not identity.
- `MaterializedValue`: value ID, semantic type, unit reference where applicable, exact payload when permitted, one value-state assertion, source/authority refs, and display instructions separately.
- `ScopedStateAssertion`: assertion ID, state family, exact subject/kind, vocabulary value, authority, effective snapshot/event, reason where required, affected obligations, conflict sources where applicable, blocking consequence, and resolution authority.
- `TypedRelation`: relation ID only when the relation itself carries authority, scope, provenance, state, or obligation; otherwise the owning record carries a typed target reference.
- `ExtensionBlock`: the extension envelope specified in section 13.

## 4. Mandatory semantic coverage matrix

`L0` through `L6` are TASK-043 validation layers. `R` means required; `O` optional only when semantically inapplicable. Failure consequences are minimum consequences.

| Responsibility | Canonical owning record | Representation, cardinality, scope | Req. | Layer | Fallback / failure |
|---|---|---|---|---|---|
| Organizing purpose | Candidate | one purpose object; package scope; brief trace | R | L0/L2 | absent or incompatible blocks Candidate |
| Audience description | Brief then Candidate | one or more authored audience-orientation entries; package/use scope | R | L0/L2 | no inferred audience; missing blocks |
| Subjects | Material/Candidate | 0..n generic typed external refs; statement/package scope | O | L1/L2 | unknown required subject ref blocks; no company fields |
| Upstream authority | Material | 1..n scoped authority assertions referenced by supplied semantics | R for upstream material | L0/L2 | ambiguous/unauthorized substantive material blocks |
| Provenance | Material | source/provenance refs on every substantive supplied object | R | L2 | missing traceability blocks affected material |
| Evidence-snapshot identity | Material and Release | exact snapshot refs; per material/value/state and release set | R for evidence-backed release | L2/L3 | no live refresh; mismatch blocks |
| Materialized values | Material; Candidate references | 0..n exact value objects | O | L1/L2 | no imputation; invalid state blocks use |
| Semantic types and units | Material | type ID and unit ID on each applicable value | R when value present/zero | L1/L2 | unknown/incompatible unit blocks |
| Value state | Material/Candidate | exactly one value-state assertion per materialized value | R | L1/L2 | never infer from absent/null; invalid combinations block |
| Evidence state | Material | independent availability, integrity, authority, review, freshness, active-use assertions as applicable | R for evidence refs | L2 | stale/withdrawn visibly constrained; unauthorized blocks |
| Consistency state | Material/Candidate | scoped consistency finding over named subjects | R when checked or conflict known | L2 | undeclared conflict/ambiguity blocks; disagreement retained |
| Lifecycle references | record owning event | typed refs to upstream/release/artifact events | R when applicable | L2/L3 | history preserved; withdrawn/stale never presented current |
| Presentation statements | Candidate | 1..n stable statement records | R | L1/L2 | missing substantive package blocks |
| Content posture | Candidate statement | one primary posture plus 0..n attached distinctions | R | L2 | no universal type; unsupported/ambiguous posture blocks |
| Communication function | Candidate statement | 1..n authored/reviewed function refs | R for substantive statements | L2 | no heuristic canonicalization; absent blocks where needed |
| Attention/prominence | Candidate statement | exactly one attention obligation | R | L2 | renderer may not infer; absence blocks required narrative |
| Encounter/composition | Candidate | typed relations; parent owns ordered children; partial-order edges otherwise | R for navigable package | L1/L2 | cycles block; source order only when explicitly authored |
| Caveats | Candidate | caveat statement plus canonical `limits-target` relation | R when supplied/applicable | L2/L6 | orphan/detached caveat blocks Candidate/artifact |
| Uncertainty | Candidate | uncertainty statement/state plus `limits-target` relation | R when supplied/applicable | L2/L6 | omission or claim-strength increase blocks |
| Personal annotations | Candidate | annotation statement with personal author authority and distribution scope | O | L2/L4 | cannot masquerade as evidence/finding; unsafe distribution blocks release |
| Presentation obligations | Candidate | 0..n obligation records with canonical target refs | R for supplied obligations | L2 | dangling/detached target blocks |
| Sections/navigation intent | Candidate | section records; parent ordered-child containment; entry/continuation/deep-link intent | R for multi-part package | L1/L2 | no global navigation; broken order/link blocks |
| Exhibit/visualization intent | Candidate | exhibit-intent records referencing value bindings and statement purpose | O | L2/L5 | unsupported required exhibit uses admitted fallback or fails closed |
| Sensitivity/distribution | Material/Candidate/Release | scoped obligations and governance authority refs | R where declared | L2/L4 | suppression is not distribution; unauthorized release blocks |
| Transformation permissions | Candidate renderer requirement | explicit permitted mechanical/equivalent transformation classes | R when transformation occurs | L2/L5/L6 | undeclared transformation blocks plan/artifact |
| Renderer requirements | Candidate | 0..n requirement records with subjects, mandatory flag, fallback | R for release | L2/L5 | unsupported mandatory requirement falls back or rejects |
| Fallback declarations | Candidate | requirement -> admitted fallback records; static and print where needed | R for required capability/selection | L2/L5 | missing/incomplete fallback fails closed |
| Selection sets | Candidate | 0..n closed finite sets | O | L1/L2 | wildcard/computation/implied combinations block |
| Selection states | Candidate | 2..n complete state projections per admitted set | R when set exists | L2 | incomplete or invalid state blocks selector publication |
| State-specific applicability | Candidate projection | complete lists of active statements, exhibits, labels, caveats, uncertainty, evidence, obligations | R when selection exists | L2 | no implicit inheritance; omission blocks |
| Narrative invariants/variants | Candidate projection | invariant IDs repeated in each projection; authored variant IDs explicit | R when selection exists | L2 | misleading state blocks selector publication |
| Candidate/Judgment/Ready linkage | Judgment and Ready | judgment -> exact Candidate; Ready -> exact Candidate + successful judgment | R | L3 | mismatch blocks promotion |
| Release identity/lifecycle | Release | publication lineage, semantic version, exact Ready/snapshots, events/status | R for publication | L3/L4 | invalid authority/version/event blocks release |
| Manifest derivation | Manifest | projection refs to release/artifact records plus derived catalogue fields | R for released standalone package | L1/L3/L6 | contradiction rejects/regenerates manifest |
| Renderer/artifact identity | capability, plan, audit | exact independent IDs/versions linked by typed refs | R for artifact | L5/L6 | mismatch blocks artifact acceptance |
| Traceability evidence | Material through audit | typed identity path and integrity evidence | R for substantive material | L2/L6 | broken link blocks affected stage; never proves meaning |
| Semantic conformance evidence | conformance record | findings against exact Ready, plan, renderer and artifact | R for accepted artifact | L6 | semantic failure blocks artifact even if audit links pass |

No responsibility is stored twice for traversal convenience. A consumer may build an in-memory reverse index from canonical edges; that index is non-semantic, disposable, excluded from fingerprints, and must never be serialized as authority.

## 5. Canonical relationship directions

| Relationship | Canonical direction | Rule |
|---|---|---|
| statement to upstream reference | statement -> external/material reference | reverse `used-by` is derived only |
| statement to authority assertion | statement -> scoped authority assertion | authority assertion does not list statements unless its scope itself is a canonical relationship record |
| statement to organizing purpose | statement -> Candidate purpose ID | one explicit purpose compatibility ref; package containment alone is insufficient |
| caveat/uncertainty to limited target | qualifier -> `limits-target` typed relation | qualifier without target is orphaned; target does not duplicate qualifier IDs |
| obligation to target | obligation -> one or more typed target refs | statement/target does not store obligation IDs; reverse attachment is derived and validated |
| composition parent to ordered children | parent section/group -> ordered child edge sequence | child has no canonical parent backref; multi-parent grouping uses separate relation records |
| exhibit to value bindings | exhibit intent -> ordered or keyed value refs | values do not list exhibits |
| selection state applicability | complete state projection -> statements, relations, exhibits, labels, caveats, uncertainty, evidence, obligations, requirements/fallbacks | components do not list applicable states; reverse index derived |
| renderer requirement to fallback | requirement -> ordered admitted fallback refs | fallback may be shared but does not list requirements |
| Ready to judgment | Ready -> exact successful judgment and Candidate | judgment -> Candidate remains canonical for what it assessed; this is not duplicate inverse authority |
| release to Ready/snapshot | release -> exact Ready and evidence snapshots | Ready/snapshots do not list releases |
| artifact audit links | audit -> request, compatibility plan, release, Ready, renderer, artifact | source records do not list audits except Release may inventory accepted artifact-record IDs as publication lifecycle responsibility |
| manifest projection | manifest -> authoritative release and accepted artifact/audit/conformance records | source authorities never point to or accept corrections from manifest |

A separate `TypedRelation` is mandatory when an edge has its own authority, provenance, state, temporal scope, or obligations. Plain references are used only where the owning source record fully owns the relationship.

Validators reject orphan qualifiers, dangling targets, target-kind mismatches, duplicate canonical edges with contradictory attributes, duplicate identities, and semantic references encoded by path/position/DOM/CSS. A manifest conflict is a manifest failure, never an update to source records.

## 6. State representation

BCRP selects **explicit scoped state assertions**. State is never inferred from payload, omitted property, transport null, false, zero, empty text, or empty collection.

### 6.1 Value state

Every `MaterializedValue` has exactly one value-state assertion:

- `present`: payload required and semantically non-zero when numeric;
- `explicit-zero`: exact zero payload required;
- `missing-not-provided`: payload prohibited; reason/source expected when known;
- `unavailable`: payload prohibited; reason and declaring authority required;
- `not-applicable`: payload prohibited; applicability rationale and authority required;
- `suppressed-withheld`: payload prohibited in the distributable instance; suppression authority/reason required when permitted to disclose;
- `unresolved`: no accepted payload; candidate alternatives/conflict refs may be attached;
- `invalid`: rejected payload may be retained only in quarantined evidence, never as the admitted semantic payload; named contract/finding required.

A present or explicit-zero value may coexist with independent qualifiers such as uncertainty, evidence freshness, distribution restriction, display rounding, and consistency state. It may not coexist with another value-state value. Suppression describes value disclosure; a distribution restriction governs who may receive a record or artifact. Neither implies the other.

### 6.2 Consistency and conflict

Consistency assertions use `consistent`, `conflicting`, `unresolved`, `invalid-under-contract`, or `not-checked`. `conflicting` references every known disagreeing source/value assertion, conflict kind, detection authority, resolution authority, and blocking consequence. No winner is selected by BriefForge. `not-checked` is an explicit fact, not absent validation.

### 6.3 Evidence and lifecycle

Evidence dimensions remain separate: availability, integrity, authority acceptance, exact upstream review state, freshness, and active use. Upstream lifecycle references and publication lifecycle events are distinct record kinds. `stale`, `withdrawn`, and `superseded` point to the authority/event that asserted the condition; they never mutate or erase the prior record. Current-use status is derived from the authoritative event chain under a named lifecycle policy, while the events themselves are asserted.

Unknown core state values under an unsupported profile version cause structural rejection. A new core state value is not silently mapped to `unknown`; it requires a compatible extension or a profile major-version decision. Unknown upstream review values remain opaque external vocabulary values with owner/version, not BCRP core states.

## 7. Finite selection-set representation

BCRP admits one canonical design: **complete materialized state projections**. Deltas, inheritance, wildcards, intervals, free parameters, implied Cartesian products, live queries, computed values, rankings, and inferred comparisons are prohibited.

Each `SelectionSet` contains:

- stable set identity and semantic/publication authority;
- at least two finite state identities in deterministic authored order;
- exactly one authority-declared default state;
- one complete `PresentationStateProjection` per state;
- exact evidence binding and independent validation identity per state;
- a package-owned renderer requirement for state identity visibility and navigation;
- complete static fallback and print fallback declarations;
- audit requirements for selected-state identity and expression plan.

Every projection explicitly enumerates all applicable purpose/scope refs, titles/labels, statements, relations, exhibits/value bindings, evidence/provenance, caveats, uncertainty, obligations, renderer requirements, static expression, and print expression. Invariant statements are declared at set level for review but are still explicitly included in every projection; the set-level list is non-authoritative convenience and validators prove equality. No inherited item can survive invisibly into an incompatible state.

A state lacking complete materialized content, evidence, narrative validity, caveats, or fallback blocks selector publication. A separately valid fixed-state release may proceed only through a distinct Candidate/Ready/release path.

## 8. Deterministic semantic canonicalization

BCRP canonicalization operates on the reconstructed abstract profile, not bytes.

1. Validate profile structure and identity uniqueness before canonicalization.
2. Resolve canonical references and reject dangling or kind-mismatched edges.
3. Exclude transport locators, bundle file order, comments, caches, reverse indexes, integrity digests of the transport itself, renderer bytes, and explicitly non-semantic display-only extensions.
4. Preserve semantically ordered collections exactly where order is declared: section children, required encounter order, selection-state authored order, fallback preference order, narrative sequence, exhibit series/category order when meaning-bearing, and lifecycle event order after event-time/sequence validation.
5. Treat all other sets as unordered and sort by `(object-kind, identity-scope, canonical-identity, semantic-version-or-empty)`. Typed references additionally sort by `(relationship-kind, target-kind, target-identity)`.
6. Reject duplicate semantic identities; do not deduplicate silently. Duplicate identical edges are invalid profile noise; contradictory duplicates are semantic failures.
7. Normalize text to Unicode NFC and line ending LF. In prose, all remaining code points and whitespace are significant; no trimming, wrapping, or whitespace collapsing occurs. Identifiers are ASCII, case-sensitive, already in canonical syntax, and are rejected rather than case-folded. External URI identifiers normalize only scheme/host according to the declared URI profile; path/query remain exact.
8. Normalize timestamps to UTC as `YYYY-MM-DDTHH:MM:SS[.fraction]Z`, with 1–6 fractional digits only when non-zero, trailing fractional zeros removed, explicit original offset required at admission, and no implicit local time or leap-second coercion.
9. Normalize integers mathematically. Normalize exact decimals to sign, integer coefficient, and base-10 scale with trailing decimal zeros removed; all zeros become positive coefficient `0`, scale `0`. Binary floating payloads are not admitted as exact semantic numbers.
10. Preserve unit identity and semantic type; numerically equal quantities with different units are not equal unless an upstream-authorized exact conversion is represented as a separate transformation and value.
11. Preserve every explicit state. Absence of an optional object means only “not part of this profile instance”; it never supplies a semantic default. Defaults are semantic only when explicitly declared by the owning contract and are materialized before fingerprinting.
12. Canonicalize semantic extension blocks after core objects by `(owner-namespace, extension-name, extension-version, scope, target-identity)` and include their canonical generic payload. Non-semantic display-only extensions are excluded.
13. Derived manifests, reverse indexes, deep-link strings, display rounding, generated labels explicitly marked display-only, and audit metadata do not enter Candidate semantic canonicalization. An authored title/label required for narrative or selection does enter.

## 9. Equality domains and fingerprints

- **Semantic equality:** two instances reconstruct the same authoritative semantic graph: same semantic identities, values, roles, authorities, states, canonical relations, obligations, selection projections, and required narrative under BCRP canonicalization. Non-semantic profile metadata may differ.
- **Profile-instance equality:** two BCRP instances contain the same semantic graph plus the same BCRP-level optional semantic extensions and retained profile information after canonicalization. Bundle locators and comments remain excluded.
- **Artifact equality:** generated bytes and file inventory are identical under the artifact's own byte-digest rule. This says nothing about semantic fidelity.
- **Presentation equivalence:** two derivative expressions preserve all required meaning, visibility, order/proximity, state identity, caveats, uncertainty, provenance, obligations, interaction and fallback semantics. It is established by named transformation authorization and output validation, not by profile canonicalization alone.

Fingerprint domains must be declared in the digest metadata:

1. `candidate-semantic`: BCRP semantic canonical form of the Candidate and its transitive canonical semantic dependencies;
2. `profile-instance`: all canonical BCRP profile information for a declared record closure, including preservable semantic extensions;
3. `release-semantic`: release identity/version, exact Ready fingerprint, evidence snapshots, and authoritative lifecycle substance, excluding artifacts/manifests;
4. `artifact-bytes`: exact artifact files/bytes under a declared inventory rule;
5. `manifest-instance`: derivative manifest profile content under its projection version.

Equal fingerprints establish equality only in the named domain under the named algorithm/canonicalization version. They do not establish truth, authority, analytical validity, governance approval, or presentation equivalence.

A later serialization must define a one-to-one mapping for every BCRP scalar/container, reject ambiguous lexical forms, preserve ordered versus unordered collections, emit normalized text/numbers/timestamps, and produce deterministic bytes from the BCRP canonical form. Byte canonicalization is a transport concern and may not alter these rules.

## 10. Numeric discipline

- Integers are exact mathematical integers.
- Exact decimals use coefficient-and-scale semantics; a transport may encode them as structured records or canonical strings, not binary floats.
- Approximate numeric values require an exact represented central value plus an explicit approximation qualifier such as tolerance, interval, significant digits, or upstream method. “Approximate” never licenses silent rounding.
- Numeric lexical spelling is representational, not semantic, after exact parsing; `1`, `1.0`, and `1.00` are semantically equal exact decimals only when semantic type/unit and approximation qualifiers match.
- Negative zero canonicalizes to explicit positive zero while retaining the `explicit-zero` value state; a source-specific negative-zero distinction, if meaningful, must be preserved as an upstream extension and cannot change the core value.
- Units are stable semantic references. Display conversion or rounding is a separate authorized presentation transformation.
- Renderer-rounded zero must never replace a small non-zero semantic value. A display may show a rounded form only while preserving an inspectable exact value and non-zero state.

## 11. Temporal discipline

BCRP interprets only BriefForge-owned timestamps: intake disposition, validation execution, readiness binding, publication release, lifecycle events, renderer invocation, conformance, and manifest generation. Every admitted timestamp has an explicit offset and canonical UTC form; implicit local time is invalid.

Evidence-snapshot identity is not publication time. Lifecycle-event time is not semantic publication version. Upstream temporal material is carried through generic typed external references and exact source text/value semantics without BriefForge defining its domain meaning.

BCRP does not define fiscal periods, financial-reporting dates, restatements, corporate-action dates, consolidation dates, or related deferred semantics.

## 12. Fingerprint prerequisites

A semantic/profile fingerprint may be computed only after:

1. profile identity/version support is established;
2. Layer 1 structure passes for the fingerprinted closure;
3. identities are unique and all canonical internal refs resolve to correct kinds;
4. ordered/unordered collection status is known;
5. exact numeric, timestamp, text, unit and state forms are admitted;
6. required semantic extensions are understood and optional semantic extensions are canonically preserved;
7. no derived reverse index or transport locator is included;
8. the fingerprint domain, canonicalization version, and digest algorithm are declared.

A failed prerequisite yields no authoritative fingerprint, not a best-effort digest.

## 13. Extension model

Every extension is an `ExtensionBlock` declaring:

- owner namespace/identity;
- extension name and version;
- authority owner;
- exact scope and target identities;
- criticality: `required` or `optional`;
- character: `semantic` or `display-only`;
- validation contract/policy identity;
- preservation: `must-preserve` or `discardable` (discardable is permitted only for optional display-only content);
- canonical generic payload and any external refs.

Rules:

1. Extensions cannot override core meaning, redefine identities, replace mandatory records, collapse state dimensions, alter canonical relations, or weaken validation/fallback.
2. Unknown required semantic extensions cause rejection at Layer 1 and block every dependent stage.
3. Unknown optional semantic extensions may be accepted only by a reader that can preserve their canonical generic payload losslessly and declares that their scope is not required for the attempted operation. They remain in profile-instance fingerprints. A reader unable to preserve them rejects.
4. Unknown required presentation meaning, even if labelled optional incorrectly, causes renderer compatibility failure when the extension's scope affects required expression.
5. Unknown display-only extensions may be ignored only when explicitly optional, non-semantic, and discardable. Must-preserve display content survives round trips but is excluded from semantic equality.
6. Extension namespaces are stable owner identifiers, not file paths, Python module names, DOM/CSS selectors, or AtlasForge routes.
7. Core validators still inspect extension envelopes and prohibition rules. An extension validator owns only its namespaced payload.
8. DSB-007 remains binding. No extension in BCRP 1.0 may introduce canonical fiscal-period, reporting-date, restatement, corporate-action, currency-conversion, consolidation, security-identity, reporting-segment, or reported-versus-adjusted semantics.

## 14. Representation-profile versioning

BCRP uses semantic versioning independently from ADPM semantic, transport serialization, validation policy, renderer, artifact, and manifest-projection versions.

- **Patch:** clarification or defect correction that changes neither admitted profile information nor canonicalization/equality. No migration.
- **Minor compatible additive:** optional profile information or optional extension envelope capability that old readers can losslessly preserve and safely ignore for their declared operation. Existing canonical meaning and fingerprints for instances not using it are unchanged.
- **Major incompatible:** required property, identity/relationship change, canonicalization/equality change, new core state that old readers cannot interpret, removal/renaming, changed default, or altered fingerprint scope. Migration specification required before implementation.
- **Semantic change:** change to ADPM/TASK-041/TASK-042/TASK-043 meaning; increments the owning semantic version even if BCRP shape is unchanged.
- **Extension-only change:** changes one extension version; BCRP changes only if envelope/core compatibility changes.
- **Validation-policy change:** changes finding policy/version, not BCRP, unless profile admissibility or canonicalization changes.

A reader declares supported BCRP major and maximum minor, extension preservation capability, and operation scope. A 1.x reader may process a later 1.x instance only when all unknown content is optional under the above rules and can be preserved. It must reject unknown required content, unknown core states, or optional semantic content that affects its operation. No migration code is authorized here.

## 15. Initial serialization direction for TASK-045

If implementation is authorized, the one initial serialization should be **canonical JSON documents for BCRP 1.0**, with multiple root documents permitted in one deterministic bundle.

Reasons:

- JSON maps the accepted record/reference graph without forcing monolithic nesting;
- deterministic object/member and array rules can derive from BCRP canonicalization;
- JSON Schema and Python validators have mature offline tooling;
- exact decimals can be represented as canonical strings or coefficient/scale records rather than JSON binary numbers;
- states and extension envelopes remain explicit;
- fixtures are inspectable and diffable;
- Python's standard library provides stable offline parsing, while schema support can be bounded as one dependency if separately accepted;
- record separation resists renderer-input coupling.

Markdown is not canonical. YAML, XML, TOML, database storage, and converters are not recommended for TASK-045. This recommendation does not authorize serialization in TASK-044.

## 16. Acceptance and implementation gate

BCRP 1.0 settles profile topology, canonical direction, state encoding, containment/reference, ordering, canonicalization, equality, fingerprints, extensions, and versioning without company-specific fields or renderer authority.

Implementation remains contingent on the separately accepted golden-corpus specification and final TASK-044 gate. No schema, instance, serializer, loader, validator, fixture, runtime migration, renderer integration, selector, or manifest emitter is created by this specification.
