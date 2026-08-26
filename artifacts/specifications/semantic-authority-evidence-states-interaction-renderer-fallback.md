# Semantic Authority, Evidence States, Interaction, and Renderer Fallback Foundations

Date: 2026-07-16
Status: Accepted semantic specification
Owner: BriefForge
Task: TASK-042
Scope: semantic authority, explicit state, bounded interaction, renderer transformation, capability, narrative-consistency, and fallback foundations

## 1. Purpose

This specification defines semantic responsibilities that must exist before BriefForge designs representation contracts, schemas, validators, or new renderer behavior for authority-sensitive statements, bounded selection, explicit evidence/value states, or renderer fallback.

It refines existing concepts rather than replacing them:

- Presentation Contract, Organizing Purpose, Composition Semantics, Presentation Statements, Presentation Validation Obligations, and Presentation Grammar;
- Candidate Presentation Package -> Validation Judgment -> Ready Presentation Package;
- TASK-041 Presentation Intake, fixed-evidence standalone publication, Publication Release Record, and derivative publication manifest;
- ADPM's renderer-independent authority, evidence, recommendation, uncertainty, and lifecycle semantics;
- renderer-adapter and rendered-artifact-conformance boundaries;
- experimental Encounter Semantics and Communication Intent evidence.

This is a semantic specification only. It defines no serialization, schema, builder, validator, serializer, renderer, browser runtime, interaction implementation, or manifest emitter.

## 2. Fixed boundaries

### 2.1 BriefForge authority

BriefForge owns presentation-local meaning: organizing purpose, presentation statement construction, composition and encounter obligations, communication function, narrative coherence, presentation validation, release binding, and derivative-publication conformance requirements.

BriefForge does not own source acquisition, canonicalization, analytical calculation, statistical truth, accepted upstream findings, investment theses, company-data semantics, arbitrary querying, global discovery, or open-ended exploration.

### 2.2 Fixed TASK-041 inputs

This specification does not reopen:

- Presentation Brief and Portable Presentation Material responsibilities;
- fixed-evidence standalone publication terminology;
- Candidate -> Judgment -> Ready as the only presentation-readiness lifecycle;
- immutable Publication Release Record;
- separate semantic-publication, evidence-snapshot, Ready-package, renderer, generated-artifact, and manifest versions;
- derivative manifest and optional AtlasForge consumption;
- exclusion of live entity pages and open-ended exploratory workspaces.

### 2.3 Independence

All states and bounded selections must be reproducible from retained material while upstream systems, AtlasForge, and network services are unavailable. AtlasForge may catalogue or embed a publication but receives no semantic, lifecycle, selection, or fallback authority.

## 3. Governing principle: independent semantic dimensions

A Presentation Statement is not governed by one universal `type`, `mode`, or `status`. At minimum, authority-sensitive presentation meaning must distinguish these independent dimensions:

1. semantic content role;
2. scoped authority and provenance;
3. communication function;
4. encounter and composition relations;
5. attention/prominence obligation;
6. evidence state;
7. value state;
8. consistency state;
9. upstream and publication lifecycle references;
10. attached presentation obligations.

No dimension may silently imply another.

Examples:

- a statement presented as a conclusion does not become a BriefForge-authored finding;
- `quantify` does not prove a value valid;
- primary prominence does not imply high confidence;
- first encounter does not imply analytical priority;
- stale evidence does not withdraw a historical release;
- a caveat role does not establish who authored or accepted the caveat;
- a renderer capability declaration does not prove faithful output.

Composite material must be split when its constituents differ materially in role, authority, state, or obligations. Convenience is not sufficient reason to collapse authority boundaries.

## 4. Statement semantic roles

### 4.1 Role is upstream semantic posture, not layout

The following distinctions are admitted as semantic postures that BriefForge must preserve when supplied or authored under valid authority:

| Role | Semantic meaning | Authority rule |
| --- | --- | --- |
| Observation | A bounded observed or reported condition without analytical elevation. | Observation meaning and observation basis remain upstream-owned unless the observation is purely presentation-local. |
| Reusable evidence | Material accepted by its authority for reuse as evidence beyond one sentence or display. | BriefForge may reference and present it but cannot grant reusable-evidence status. |
| Accepted finding | An authority-accepted analytical or evidential result. | The declared upstream acceptance authority owns finding status and scope. |
| Interpretation | Meaning assigned to observations, evidence, or findings. | Must identify the interpretation authority and supporting/limiting material. |
| Hypothesis | A testable proposed explanation or relationship not accepted as a finding. | Must remain visibly provisional and identify tests, alternatives, or falsifiers when supplied. |
| Scenario | A conditional possible state or path, not a forecast by default. | Assumptions, conditions, horizon, and scenario authority remain attached. |
| Recommendation | A proposed action with owner, rationale, confidence, dependencies, uncertainty, and decision context as required by ADPM. | Recommendation authority remains upstream or explicitly requestor-owned; BriefForge does not invent it. |
| Uncertainty | A bounded statement of unknowns, confidence limits, sensitivity, or unresolved evidence. | Must remain attached to affected material; uncertainty is not itself a generic caveat. |
| Caveat | A condition limiting interpretation, use, comparability, scope, or distribution. | Must identify affected material and cannot be detached by composition or fallback. |
| Personal annotation | A clearly attributed personal note that is neither accepted evidence nor an upstream finding. | Annotation owner, non-authoritative status, visibility scope, and relation to governed material must be explicit. |

These are not mutually exclusive content labels to be forced into one enum. A recommendation may carry uncertainty; a finding may be supported by reusable evidence and constrained by caveats. One primary semantic posture may be declared for reader orientation, but all material distinctions must remain expressible without type coercion.

### 4.2 Presentation-local material

BriefForge may author:

- framing, scope, non-scope, and organizing-purpose statements;
- faithful presentation synthesis that restates already-authorized material;
- presentation instructions and provenance navigation;
- explicit declarations that material is missing, conflicting, stale, withdrawn, or unsupported when that state is supplied by the responsible authority or is a bounded presentation-contract finding.

A presentation synthesis must trace to its source assertions and qualifications. It must not increase claim strength, resolve disagreement, create a ranking, infer causation, produce a recommendation, or replace upstream wording where exact wording is obligatory.

### 4.3 Scoped authority

A substantive statement may involve distinct authorities:

- originator;
- semantic/acceptance authority;
- evidence authority;
- exporter/materializer;
- requestor/transporter;
- presentation author;
- presentation validation authority;
- publication release/lifecycle authority.

These roles are not synonyms. Integrity proves identity, not truth or authority. Unknown, ambiguous, or contradictory authority blocks admission of the affected substantive material.

TASK-039 provides the reusable pattern: InsightForge owns question selection and interpretation while KnowledgeForge owns accepted coefficients, methods, provenance, and validation state. BriefForge owns their bounded presentation, not either upstream meaning.

### 4.4 Superlatives, rankings, and selections

Words such as `strongest`, `top`, `priority`, `best`, `representative`, or `selected` require explicit upstream authority, comparison universe, exclusions, method, and evidence snapshot. A renderer or BriefForge author must not infer the comparison universe from the material present.

## 5. Communication function, attention, and encounter semantics

### 5.1 Communication function

Communication function states what a presentation statement is intended to do for the reader. The experimental vocabulary remains useful evidence:

- orient;
- summarize;
- explain;
- compare;
- quantify;
- warn;
- qualify;
- trace;
- conclude.

This specification accepts the distinction, not the existing heuristic derivation implementation. Communication function must be explicitly authored or reviewed before it can govern validation, transformation, or fallback. Keyword inference remains non-canonical experimental evidence.

A function does not establish content role, truth, authority, attention level, layout, or renderer feature. In particular:

- `compare` does not authorize BriefForge to select comparison entities;
- `quantify` does not validate a number;
- `conclude` does not authorize stronger synthesis;
- `warn` prevents harmful misuse;
- `qualify` bounds strength or applicability;
- `trace` exposes authority/provenance but does not make material evidential support.

### 5.2 Attention/prominence

Presentation Grammar attention levels—primary, secondary, supporting, and discoverable—remain separate from role, communication function, confidence, lifecycle, and order. Discoverable material must still satisfy visibility and non-detachment obligations.

### 5.3 Encounter and composition relations

Encounter semantics describe target-independent organization and traversal. They may express:

- order or required precedence;
- grouping;
- hierarchy;
- required co-encounter/proximity;
- bounded alternate paths;
- entry and continuation relationships.

They do not express evidential support, contradiction, derivation, causality, analytical importance, confidence, or authority.

Requirements:

- relations reference stable statement or group identities;
- strict ordering and hierarchy are acyclic;
- generic relatedness cannot imply order or support;
- a materially limiting caveat can require co-encounter or prior encounter without prescribing a card, tab, coordinate, or browser mechanism;
- multiple valid encounter paths are allowed when no total order is semantically required.

The current `EncounterSemantics.mode` is implementation evidence, not sufficient future semantics. TASK-039 uses `orientation`, `conclusion`, `methodology`, `finding`, `evidence`, `caveat`, and `provenance` as modes; those values mix content role and communication function with encounter relationship. No runtime repair is authorized here.

## 6. Explicit state model

No universal status vocabulary is accepted. States are scoped to the semantic object and authority that owns them.

### 6.1 Evidence state

Evidence state concerns an evidence reference or snapshot, not the truth of a presentation statement. It separates:

- availability: available, partial, missing, unavailable;
- integrity: verified, unverified, mismatch;
- upstream acceptance/authority: accepted by declared authority, not accepted, ambiguous, unauthorized;
- review status: exact upstream-declared review state;
- freshness: current, stale, unknown, or not applicable;
- active-use status: active or withdrawn when declared by the responsible authority.

BriefForge may validate declarations, identity, referential integrity, and compatibility with presentation obligations. It cannot independently decide analytical truth or silently refresh stale/withdrawn material.

### 6.2 Value state

A materialized value must distinguish:

- present value;
- explicit zero;
- missing/not provided;
- unavailable;
- not applicable;
- suppressed/withheld;
- unresolved;
- invalid as declared by the responsible authority or by bounded contract validation.

Rules:

- zero, false, an empty collection, and an empty string are not automatically missing;
- unavailable is not zero;
- not applicable is not missing;
- suppressed is not unavailable and must preserve the responsible authority/reason where distribution permits;
- unresolved is not invalid;
- an explanatory label is presentation expression, not a substitute value;
- no renderer may impute, coerce, calculate, or substitute a value.

### 6.3 Consistency state

Consistency is a scoped finding over identified material:

- consistent;
- conflicting;
- unresolved/indeterminate;
- invalid under a named contract;
- not checked.

Every conflict declaration identifies affected material, conflict kind, detection authority, resolution authority, and blocking consequence.

Accidental contradiction, undeclared incompatibility, authority ambiguity, and broken reference consistency block readiness. Intentionally presented disagreement, opposing evidence, alternatives, counterarguments, and historical change may be valid when explicitly attributed, scoped, and qualified. BriefForge may present a conflict; it may not choose the winner.

### 6.4 Lifecycle state

The following remain independent:

- upstream evidence/finding lifecycle;
- Candidate -> Judgment -> Ready presentation-readiness lifecycle;
- Publication Release Record status and lifecycle events;
- generated-artifact state;
- derivative-manifest generation state.

No second mutable BriefForge statement lifecycle is introduced. An upstream stale or withdrawn declaration is preserved; BriefForge publication governance may issue a corresponding current-use lifecycle event without rewriting the historical release. Ready status remains historical fact. Artifact corruption does not invalidate the semantic release. Manifest regeneration cannot restore active status.

A Candidate is revisable by producing a replacement Candidate before promotion. An individual fingerprinted Candidate instance may remain immutable in implementation; this does not contradict conceptual revisability.

## 7. Interaction authority taxonomy

### 7.1 Navigation — admitted

Navigation changes reader location, not substantive state. Internal anchors, contents links, statement deep links, and equivalent in-publication traversal are admitted. Global discovery, cross-report navigation, routing, and search remain outside BriefForge.

### 7.2 Presentation inspection — admitted

Inspection reveals already-present material such as provenance, methodology, caveats, exact values, or audit metadata. It must not change evidence population, claim, narrative, value, or obligation. A complete static expression must preserve inspectable material when the native mechanic is unavailable.

### 7.3 Declared/prevalidated selection — conditionally admissible

Selection may choose only among a finite, closed, authority-declared set of complete prevalidated presentation states. It is presentation-state choice, not filtering, querying, or analysis.

All of the following are required:

1. upstream authority for every selectable dimension, value, and accepted state;
2. finite enumerated valid states, not a wildcard, interval, free text, or implied Cartesian product;
3. stable semantic identity for every state;
4. exact retained evidence-snapshot binding for every state;
5. no live lookup, refresh, substitution, calculation, aggregation, ranking, or interpretation;
6. exact state-to-statement, exhibit, reference, and obligation projection authored before rendering;
7. independent narrative validation of title, scope, purpose, claims, methods, values, caveats, uncertainty, provenance, and non-scope in every state;
8. cross-state checks preventing stale titles, summaries, periods, sample sizes, rankings, caveats, or provenance;
9. obligation preservation in every state;
10. a semantic-publication-authority-declared default state;
11. a deterministic, semantically complete static fallback;
12. renderer preflight against every required state, transformation, inspection, accessibility, fallback, and obligation capability;
13. visible/auditable selected-state identity, including deep-linked or copied views;
14. offline regeneration for every state and fallback;
15. new judgment, Ready fingerprint, semantic publication version, and release when state space, default, evidence binding, state narrative, or obligations change.

Failure of any prerequisite blocks selector publication. A separately valid fixed-state publication may still proceed.

### 7.4 Analytical recalculation — prohibited

Date sliders, recomputed correlations, runtime aggregation, new ratios, arbitrary sorting that creates rankings, interpolated scenarios, dynamic significance, forecasts, or other analytical transformations remain upstream responsibilities.

### 7.5 Open-ended exploration — prohibited

Free-text evidence search, arbitrary entity/metric/date selection, global comparison, querying, live filters, and exploratory workspaces are not BriefForge interactions.

## 8. Narrative consistency

Narrative consistency is semantic, not cosmetic. Every fixed or selectable state must satisfy:

- organizing purpose and scope remain true;
- primary and supporting messages are explicitly declared, not inferred from first position or visual size;
- conclusion strength does not exceed evidence and accepted authority;
- titles, summaries, units, periods, populations, sample sizes, rankings, and provenance match the selected state;
- caveats and uncertainty remain attached at the required encounter point;
- absence, suppression, conflict, staleness, and withdrawal are not hidden;
- no dangling comparison, superlative, pronoun, caption, or cross-reference remains;
- duplicate expression cannot create a stronger or misleading encounter context;
- static fallback is coherent as a publication, not merely a dump of hidden states.

A narrative inconsistency blocks the affected state or artifact. The renderer may not repair it by guessing.

## 9. Renderer transformation sovereignty

### 9.1 Permitted renderer-owned mechanics

Subject to declared semantics, a renderer may own:

- target encoding and escaping;
- deterministic layout, wrapping, pagination, and coordinates;
- scoped styling and accessible markup;
- stable anchors and in-publication navigation;
- native inspection mechanics;
- lossless formatting of already-supplied values;
- expression of one already-authorized presentation state;
- deterministic transformation to a predeclared semantically equivalent fallback.

### 9.2 Prohibited renderer authority

A renderer may not:

- create or accept evidence, findings, interpretations, scenarios, recommendations, rankings, or selector values;
- choose a substantive default;
- infer roles, prominence, narrative stage, uncertainty, or caveat attachment from keywords, labels, or position;
- select extrema, calculate first/last summaries, reorder evidence semantically, or synthesize claims unless that exact transformation is preauthorized and validated;
- detach, hide, weaken, or genericize obligations;
- silently omit malformed or unsupported material;
- use a live upstream lookup or substitute another evidence snapshot;
- claim semantic equivalence merely because audit identifiers match.

Source order is preserved by default. Geometry is mechanical; semantic sorting and derived summaries are not.

### 9.3 Duplication and progressive disclosure

Duplicating material into a summary, caption, uncertainty section, or primary-message region creates a new encounter context. Duplication is allowed only when declared and validated with all affected obligations. Progressive disclosure is allowed only when the complete static form preserves discoverability, proximity, and standalone operation.

## 10. Renderer capability and conformance obligations

Existing `RendererAdapterCapability.package_features` proves only a narrow package-input declaration. It does not prove transformation fidelity, interaction support, fallback, accessibility, narrative support, obligation preservation, offline operation, or successful output.

Future capability semantics must distinguish:

- required semantic inputs;
- supported expression/transformation classes;
- supported interaction classes;
- supported state/narrative behavior;
- obligation-preservation behavior;
- static fallback behavior;
- accessibility/standalone requirements;
- evidence that the capability was verified for the renderer identity/version.

Absence, ambiguity, or lack of verification means incompatible for that requirement.

Current rendered-artifact conformance checks audit linkage—package identity, semantic fingerprint, validation-policy identity, and recorded adapter identity. Audit linkage is necessary but insufficient. It does not prove that rendered prose, values, order, caveats, state, interactions, or transformations preserve semantics. Future semantic artifact conformance must remain a separate concern and must match the authorized renderer identity/version.

## 11. Failure and fallback policy

### 11.1 Failure families

Failures are classified at least as:

- authority: missing, ambiguous, exceeded, conflicting;
- evidence: missing, unavailable, unverifiable, invalid under contract, conflicting, stale, withdrawn;
- value: missing, unavailable, not applicable, suppressed, unresolved, invalid, or type/unit mismatch;
- selection: undeclared, open-ended, unknown state, unvalidated combination, unbound evidence, inconsistent narrative, detached obligation, recalculation required, undeclared default, unavailable fallback;
- capability: malformed, undeclared, incompatible, unverified, required semantics unsupported, required interaction unsupported, fallback unsupported;
- transformation/narrative: unauthorized, lossy, claim-creating, inferred role, changed order, inconsistent state, hidden obligation, weakened provenance, overstated scope/confidence;
- artifact: execution failure, malformed artifact, audit-link mismatch, renderer-identity mismatch, semantic nonconformance, corrupt artifact, unauthorized or non-equivalent fallback.

A failure finding must identify scope, authority, affected identities, consequence, and whether a different fixed publication remains possible.

### 11.2 Fallback hierarchy

A fallback is allowed only when predeclared and semantically equivalent for the affected obligations. Use this order:

1. native expression supported and verified;
2. prevalidated semantically equivalent expression preserving all values, relationships, states, authority, and obligations;
3. deterministic complete static representation, such as source table/text or enumerated validated states;
4. explicit unsupported/unavailable statement when that expression is itself authorized and does not create a misleadingly incomplete publication;
5. fail closed and reject invocation or artifact.

Silent best effort is prohibited.

Never fall back by:

- dropping required material or obligations;
- converting zero to missing or missing to zero;
- choosing the first available selector state;
- changing evidence snapshot or renderer without authorization;
- querying upstream live systems;
- recomputing or interpolating values;
- replacing an exhibit with a lossy summary;
- presenting stale or withdrawn material as current;
- flattening conflict into one chosen value.

Unsupported optional enhancement may be omitted only when omission is explicitly allowed and the base publication remains semantically complete. Unsupported required interaction or exhibit requires the complete declared static fallback or failure.

## 12. Cross-domain adversarial scenarios

| Scenario | Required disposition |
| --- | --- |
| A measured zero is blanked by a truthiness check. | Reject: explicit zero is present, not missing. |
| A withheld value is displayed as unavailable. | Reject: suppression authority/reason and unavailable state differ. |
| Two accepted sources disagree. | Present scoped conflict if purpose-authorized; do not choose a winner. |
| An ADPM counterargument triggers package-invalid conflict. | Reject the validator reasoning: structured disagreement is not accidental inconsistency. |
| A hypothesis is styled as a finding. | Reject artifact: presentation strength exceeds role. |
| A scenario slider interpolates between accepted endpoints. | Prohibited analytical creation; only enumerated accepted scenarios may be selected. |
| A personal note appears beside evidence without attribution. | Reject: annotation must remain non-authoritative and attributed. |
| A recommendation loses confidence and dependency qualifiers in fallback. | Reject fallback as lossy. |
| A TASK-039 country selector changes Norway to Denmark. | Reject: missing admitted evidence and invalid narrative scope. |
| A TASK-039 date slider recomputes `r` or `n`. | Prohibited upstream analysis. |
| Raw-level and first-difference results are toggled while the same conclusion remains. | Reject: state-specific thesis, method, and caveats are inconsistent. |
| `strongest` is rendered without the upstream comparison universe. | Reject admission as incomplete. |
| A renderer makes the first orientation statement the primary analytical message. | Reject inferred narrative authority. |
| A renderer parses values, sorts periods, and emits extrema captions. | Reject unless exact transformations and claims were upstream-authorized and prevalidated. |
| A renderer lacks caveat-link support and moves all caveats to an obscure footer. | Reject: attachment/proximity obligation lost. |
| A renderer lacks an exhibit but preserves complete source table/text. | Accept only if that fallback was declared and validated. |
| Correct audit identifiers accompany fabricated prose. | Audit linkage may pass; semantic artifact conformance must fail. |
| A selector state becomes stale after release. | Preserve historical identity; expose lifecycle status and fail active use if narrative completeness cannot be maintained. |
| AtlasForge embedding fails. | Consumer-local failure; standalone BriefForge publication remains valid. |
| Company/fiscal-period selectors are proposed before upstream semantics stabilize. | Defer; generic references cannot substitute speculative financial-domain meaning. |
| A locator changes while evidence meaning is claimed unchanged. | Upstream authority must establish equivalence; BriefForge cannot infer it. |
| Encounter relations contain a cycle. | Block readiness; renderer must not select an arbitrary order. |
| A statement cites an obligation that does not cite the statement back. | Block consistency unless one direction is explicitly authoritative; future representation should prefer bidirectional validation. |

## 13. Current implementation evidence and non-retroactivity

The current runtime and renderer remain evidence/test fixtures. This specification does not retroactively invalidate completed publications or authorize repairs.

Observed pressure:

- current `EncounterSemantics.mode` overloads role/function/encounter concerns;
- Communication Intent derivation is heuristic and explicitly non-canonical;
- TASK-039 contains mixed role-like modes and absolute upstream locators predating TASK-041 portability;
- TASK-039 obligation attachment is not bidirectionally complete;
- existing renderer capability checks establish package-field compatibility only;
- existing rendered-artifact conformance proves audit linkage only;
- current renderer heuristics can infer prominence/narrative stage and derive semantic-looking summaries;
- silent exhibit omission is not an accepted fallback contract.

These are requirements for later representation/validation planning or bounded defect tasks, not implementation authorization in TASK-042.

## 14. Financial-domain semantic deferral

The accepted DSB-007 deferral remains binding. BriefForge does not presently define canonical semantics for fiscal periods, reporting dates, restatements, corporate actions, currency conversion, consolidation, security identity, segments, reported-versus-adjusted values, or related company/financial concepts. MacroForge should stabilize them through operational evidence first. Later BriefForge compatibility review may consume upstream definitions and add only presentation-specific obligations.

This is not a runtime dependency or generic-development blocker. It does not defer BriefForge-owned publication identity, semantic publication version, evidence-snapshot reference, renderer/generated-artifact versions, publication time, correction, rerender, supersession, withdrawal, or staleness.

## 15. Consequences and next gate

Accepted now:

- independent semantic dimensions rather than one role/status;
- scoped authority and provenance;
- explicit evidence, value, consistency, and lifecycle distinctions;
- navigation and inspection authority;
- conditional admission criteria for finite declared/prevalidated selection;
- narrative consistency requirements;
- renderer transformation sovereignty;
- fail-closed capability and fallback obligations;
- audit linkage as necessary but not sufficient conformance evidence.

Not accepted or implemented now:

- concrete representation fields or vocabulary encoding;
- schema or transport format;
- validator layers or error codes;
- runtime model changes;
- selector, renderer, conformance, or fallback implementation;
- Communication Intent promotion;
- TASK-039 repair;
- financial-domain semantics.

The next task must plan a semantic representation contract and layered validation specifications for accepted TASK-041 and TASK-042 semantics before any schema, example corpus, or implementation. It must resolve location-sensitive identity, obligation-reference direction, state-scope representation, and compatibility between fixed runtime evidence and accepted semantic doctrine without modifying runtime code.
