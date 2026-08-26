# Decision: Publication Lifecycle-Event Companion Profile

Date: 2026-07-16
Status: accepted
Task: TASK-049

## Decision

Adopt `briefforge-publication-lifecycle-event-profile` version `1.0.0` as a separately versioned BriefForge companion profile for immutable, append-only post-Release lifecycle events.

The companion profile references exact immutable BCRP 1.0 `PublicationReleaseRecord` identities and `release-semantic` fingerprints. BCRP 1.0 remains unchanged at eleven root kinds and exactly one Release in a complete publication bundle. A Release never points back to lifecycle events and is never rewritten by them.

## Why this is not BCRP 1.x

Adding a lifecycle-event root to BCRP 1.x would not be a compatible minor addition. Lifecycle-aware consumers cannot safely ignore an event that changes current-use authority, old BCRP validators reject unknown roots, and the accepted versioning doctrine classifies required relationship/topology and canonicalization changes as major.

Embedding an event in a Release or attaching it as a Release extension is rejected because appending a later event would mutate the issued Release and change its `release-semantic` fingerprint. An optional extension cannot establish fail-closed authority; a required extension remains Release-attached and still cannot append without mutation.

## Why BCRP 2.0 is not selected

A BCRP 2.0 event root could represent the semantics honestly, but would force migration of the entire eleven-kind core profile, bundle topology, canonicalization, validators, and corpus. No current implementation dependency requires that broad break. A companion profile preserves exact BCRP 1.0 Releases while making lifecycle support explicit through independent version negotiation.

BCRP 2.0 remains the fallback only if later evidence shows lifecycle events must become inseparable from every BCRP operation.

## Event model

The initial publication act remains the BCRP Release and is not duplicated as an event.

Admitted event types are only:

- `supersession`: exact predecessor Release replaced by an exact successor Release;
- `withdrawal`: exact target Release loses applicable future active-use/distribution eligibility while history remains intact;
- `staleness-declaration`: a named authority declares a currency concern for an exact Release.

`correction` is a reason classification for `supersession`, not a separate event. A correction requires a new governed Ready and new Release outside this task. `replacement` is the only other admitted supersession reason and does not imply correction. Rerendering is derivative artifact work and is not a lifecycle event.

Derived staleness and an authoritative staleness declaration are distinct. The companion profile records only declarations. Derived checks may report a condition under a named validation policy but may not manufacture a governance event.

Reinstatement, expiration, replacement without explicit supersession, and distribution suspension are deferred for lack of demonstrated need.

## Authority and validation boundary

Every event declares its own identity, profile, publication identity, type, exact target/predecessor/successor Release bindings, reason, authority identity/owner/role, policy, event time, causal predecessor-event references, distribution consequence, and extensions.

Authority is supplied through a trusted in-process or accepted-artifact policy registry. This proves deterministic structural authorization under named policy; it does not prove digital signatures, external authentication, identity possession, or distribution execution.

Event authority is separate from Candidate authoring, technical validation, lifecycle Judgment, Ready promotion, initial Release authorization, renderer capability, artifact conformance, manifest authority, and distribution execution.

## Canonicalization and fingerprints

Each event has a domain-separated `lifecycle-event-semantic` SHA-256 fingerprint under `publication-lifecycle-event-canonicalization:1.0.0`. Canonicalization uses accepted BriefForge Unicode NFC, LF line endings, explicit-offset-to-UTC timestamp normalization, deterministic object ordering, and path-scoped unordered-set sorting only for owned core set fields. Arbitrary extension payload list order remains semantic.

Appending a new event changes no prior Release or event canonical bytes or fingerprint. Current state is a derivative projection of an explicitly bounded, single-root, connected Release graph and event set, never authority itself. Every non-root Release must be introduced by one supersession edge; catalog membership alone confers no current authority.

## Failure rules

Validation fails closed on unsupported profile versions, unknown event types, event/reason mismatch, malformed or duplicate identities, absent/mismatched Release bindings, disconnected or orphaned Releases, cross-publication and unrelated causal links, self-supersession, release/event cycles, competing predecessors or successors, contradictory terminal events, ambiguous causal positions or current state, unauthorized policy/authority identity-owner-role triples, unknown required extensions, and event-time contradictions.

No state is derived from filename, file order, current time, filesystem time, lexical semantic-version ordering, or latest-timestamp-wins.

## BCRP 1.0 conformance correction boundary

Focused BCRP 1.0 corrections may reject unsupported core `lifecycle_status`, explicit undeclared embedded `lifecycle_events`, and multi-Release complete-publication ambiguity already prohibited by accepted specification. Properly enveloped optional extensions remain preservable but grant no lifecycle authority and cannot affect governed state.

These corrections do not add the companion event model to BCRP 1.0.

## Consequences

- Existing BCRP 1.0 release fingerprints remain valid.
- Generic BCRP consumers do not pretend to understand lifecycle-event authority.
- Lifecycle consumers must negotiate the companion profile explicitly.
- No database, service, network, AtlasForge, renderer, artifact, manifest producer, Release producer, or financial-domain dependency is introduced.
