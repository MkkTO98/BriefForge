# Publication Lifecycle Event Profile 1.0

Date: 2026-07-16
Status: accepted specification
Task: TASK-049
Profile identity: `briefforge-publication-lifecycle-event-profile`
Profile version: `1.0.0`
Canonicalization: `publication-lifecycle-event-canonicalization:1.0.0`
Authority: companion profile subordinate to the constitution, TASK-041 lifecycle semantics, BCRP 1.0, and the TASK-049 decision

## 1. Scope

This profile represents immutable, attributable, append-only events that occur after an immutable BCRP `PublicationReleaseRecord`. It does not represent initial Release production, Ready promotion, rendering, artifacts, manifests, distribution execution, AtlasForge state, or upstream domain semantics.

A lifecycle profile instance is an explicitly bounded set of event records plus a separately supplied accepted catalog of exact BCRP Releases. Release bindings are inputs at a trusted in-process or accepted-artifact boundary; they are not copied into lifecycle-event records as semantic Release authority.

## 2. Compatibility decision

The profile is separate from BCRP because post-Release lifecycle authority cannot be safely ignored by lifecycle-aware operations and cannot append inside an immutable Release. Adding an event root to BCRP 1.x would be a breaking topology and canonicalization change. BCRP 2.0 is technically viable but unnecessarily migrates all eleven existing kinds. The companion profile preserves BCRP 1.0 bundles, root selection, validators, and Release fingerprints while requiring explicit lifecycle-profile negotiation.

## 3. Semantic vocabulary

### 3.1 Initial Release

The immutable BCRP `PublicationReleaseRecord` is the sole initial publication act. No lifecycle event duplicates it.

### 3.2 Supersession

A `supersession` event connects one exact predecessor Release to one exact successor Release. Both identity and `release-semantic` fingerprint are mandatory. It is never inferred from semantic-version ordering, event time, filename, or bundle order.

Its `reason_classification` is:

- `correction`: changed meaning, evidence, caveat, purpose, scope, or obligation required a new governed Ready and Release;
- `replacement`: a separately authorized new Release replaces the predecessor without claiming the predecessor was erroneous.

The companion validator verifies the Release graph and bindings. It does not manufacture the new Ready, Release, or release authority.

### 3.3 Withdrawal

A `withdrawal` event targets one exact Release and makes it ineligible for applicable future active use/distribution under the named policy. The Release remains historically addressable and its issuance-time `lifecycle_status` remains unchanged.

### 3.4 Staleness

A `staleness-declaration` event records a named authority's currency concern about one exact Release. It makes unconstrained current use ineligible under the named policy while preserving historical existence and fixed evidence.

A derived freshness/staleness validation condition is not an authority event. This profile does not poll upstream systems, default elapsed-time thresholds, or convert a later source change into a retroactive mutation.

### 3.5 Excluded or deferred concepts

- Rerender/regeneration: derivative artifact lifecycle, no semantic event.
- Reinstatement: deferred; no evidence yet establishes lawful reversal semantics.
- Expiration: deferred; no default time-based expiry is admitted.
- Distribution suspension: deferred; do not collapse it into withdrawal.
- Replacement without an explicit supersession relationship: prohibited.

## 4. Event record

One `PublicationLifecycleEventRecord` has exactly these core properties:

- `record_kind`: `PublicationLifecycleEventRecord`;
- `identity`: canonical ASCII event identity;
- `profile.identity` and `profile.version`;
- `publication_identity`;
- `event_type`;
- `target_release`: `{identity, fingerprint}`;
- `predecessor_release`: `{identity, fingerprint}` for supersession, absent otherwise;
- `successor_release`: `{identity, fingerprint}` for supersession, absent otherwise;
- `reason_classification`;
- `reason_detail`;
- `authority`: `{identity, owner, role}`;
- `policy_identity`;
- `event_time`: explicit offset, canonical UTC;
- `predecessor_event_refs`: explicit causal predecessors, possibly empty;
- `distribution_consequence`;
- `extensions`.

No field defaults to current time, filesystem time, filename order, semantic-version order, or implied authority.

Core conditional rules:

- supersession requires target = predecessor and requires a distinct successor;
- correction exists only as a supersession reason and therefore requires a new Release;
- withdrawal and staleness-declaration prohibit predecessor/successor Release fields;
- admitted distribution consequences are fixed per event type;
- an event time must be strictly later than each referenced predecessor event and every Release publication time it binds;
- extensions cannot override core fields or grant authority.

## 5. Release binding

An accepted `ReleaseBinding` contains:

- exact Release identity;
- exact `release-semantic` fingerprint object: domain, profile identity/version, canonicalization, algorithm, digest, and root identity;
- publication identity/lineage;
- semantic publication version;
- publication time.

Validation requires the event's compact fingerprint reference to equal the accepted binding digest and verifies that fingerprint metadata identifies the BCRP `release-semantic` domain and the same root Release. An unverified string or version label cannot substitute for a Release binding.

## 6. Policy and authority

A trusted `LifecyclePolicy` declares:

- exact policy identity;
- allowed `(authority identity, authority owner, authority role)` triples;
- admitted event types and reason classifications;
- event-type distribution consequences.

A validator matches all declarations exactly. Technical validation, fixtures, file possession, Ready, Release, renderer, artifact, manifest, and version ordering confer no lifecycle-event authority.

The boundary is deterministic structural authorization, not digital-signature verification or external authentication.

## 7. Topology

Canonical directions are event-owned:

- event -> target Release;
- supersession event -> predecessor Release;
- supersession event -> successor Release;
- later event -> causal predecessor event.

Releases never point to events. Reverse indexes and current-state projections are derived and non-authoritative.

The explicitly bounded instance must describe one publication identity, one connected Release graph, and exactly one initial Release root. Every later Release must be introduced by exactly one supersession edge; catalog membership alone cannot manufacture current authority. Unknown Releases, cross-publication bindings, duplicate event identities, missing or unrelated causal predecessors, cycles, self-supersession, competing predecessors or successors, repeated/contradictory terminal actions, shared ambiguous causal positions, orphaned Releases, and disconnected roots fail closed.

## 8. Canonicalization and fingerprints

Canonicalization operates on parsed immutable event values:

1. reject unsupported profile identity/version before canonicalization;
2. normalize text to Unicode NFC and line endings to LF;
3. normalize owned timestamps to UTC using the BCRP accepted rule;
4. sort object keys deterministically;
5. treat only core `predecessor_event_refs`, the core extension collection, and each extension envelope's core `target_refs` as unordered semantic sets; use path-aware sorting and preserve order in extension payload arrays even when payload keys resemble core keys;
6. preserve all core fields and semantic extensions;
7. exclude no authoritative event content;
8. reject float, null, duplicate JSON keys, malformed Unicode, and unsupported values.

Each event fingerprint is SHA-256 over canonical JSON containing the profile declaration, domain `lifecycle-event-semantic`, and that event only. Its root identity is the event identity. Appending another event therefore cannot alter an earlier event fingerprint.

The existing BCRP Release fingerprint is computed independently under `release-semantic`; lifecycle event bytes never enter it.

## 9. Validation and deterministic state

Validation returns classified findings, never a Boolean-only authority claim. Blocking findings prohibit state derivation.

Validation covers:

- structure/profile/version/closed vocabulary;
- event and Release identity uniqueness;
- exact Release fingerprint and publication binding;
- conditional event fields and distribution consequence;
- policy and authority admission;
- extension negotiation;
- causal-event and supersession graph acyclicity;
- event-time ordering;
- competing/contradictory events;
- deterministic current-state uniqueness.

State derivation starts from the validated connected Release graph, not tuple order, event transport order, lexical versions, or catalog membership alone. Supersession makes every Release with an outgoing edge non-current and leaves only the unique graph sink eligible; withdrawal makes its target withdrawn and ineligible; staleness-declaration makes its target stale and ineligible for unconstrained current use. Historical Releases and events remain independently verifiable.

If more than one eligible current Release remains, or no result is uniquely justified without a terminal withdrawal/staleness outcome, derivation fails closed as ambiguous. A state projection is derivative and grants no publication, lifecycle, renderer, artifact, manifest, or distribution authority.

## 10. Extensions and negotiation

Extension envelopes declare owner namespace, name, version, authority reference, scope, target references, criticality, character, validation contract, preservation, and payload.

- Unknown required extensions fail closed.
- Optional semantic extensions are preservable only when irrelevant to the attempted operation and remain in the event fingerprint.
- This profile admits only semantic, must-preserve extension envelopes; it defines no display-only lifecycle authority surface.
- No extension may override event type, Release binding, time, policy, authority, consequence, topology, or current-state result.

Only exact profile version `1.0.0` is initially supported. Unknown versions fail closed rather than being treated as compatible.

## 11. Corpus obligations

The independent corpus declares expected validity and expected current state separately from production validation logic. Valid cases prove:

1. one immutable initial Release with no event;
2. correction through a new Release plus explicit supersession;
3. successor withdrawal without Release mutation.

Invalid cases cover unsupported lifecycle and BCRP versions/types, missing identity/authority/policy/role/time/Release, unknown authority identity, event/reason mismatch, fingerprint mismatch, cross-publication and cross-event links, correction without successor, self/cyclic/competing supersession, disconnected/orphaned Release catalogs, conflicting terminal events, unknown withdrawal target, tampering, time/causal contradictions, malformed or undeclared input, version-order inference, mutated Release binding, duplicate event identity, unknown required extensions, empty catalogs, and ambiguous state.

Independent anti-overfitting tests use renamed identities, distinct publication domains and labels, different graph shapes/sequences, unrelated cycles/competition, a multi-hop supersession graph under all Release/event input permutations, and reordered equivalent inputs.

## 12. Non-authorizations

This profile does not authorize Release production or authorization APIs; renderer compatibility plans or declarations; renderer selection/invocation; HTML/SVG; artifacts or conformance; BCRP manifest production; distribution; AtlasForge; databases/network services; financial semantics; or broad runtime migration.
