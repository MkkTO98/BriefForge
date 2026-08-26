# Decision: Publication Lifecycle and Manifest Boundary

Date: 2026-07-16
Status: accepted semantic decision; no representation or implementation authorized
Scope: TASK-041

## Decision

Accept `Fixed-evidence standalone publication` as the primary publication category and `Publication Release Record` as the smallest coherent post-Ready semantic responsibility.

A Publication Release Record is an immutable record of a publication act binding:

- one semantic publication identity and version;
- one exact Ready Presentation Package identity/fingerprint;
- one evidence-snapshot identity;
- publication category and release time;
- publication lifecycle status and lineage.

It does not copy package content, validate presentation meaning, or create a second readiness lifecycle.

## Why a distinct release record is necessary

Ready status proves presentation validity but does not record whether publication occurred, when it occurred, which semantic publication lineage/version was released, which evidence snapshot was bound, or later publication-level withdrawal/staleness/supersession. A mutable Ready status would weaken immutability and conflate validation with publication authority.

## Accepted independent axes

Keep distinct:

1. semantic publication identity;
2. semantic publication version;
3. evidence-snapshot identity;
4. Ready package identity/fingerprint;
5. renderer identity/version;
6. generated-artifact identity/version;
7. manifest artifact identity/version;
8. publication/release time;
9. lifecycle-event time.

## Accepted lifecycle semantics

- Semantic correction or evidence-snapshot replacement requires a new semantic version, new Ready fingerprint, and new Validation Judgment.
- Renderer-only correction, rerender, or regeneration retains semantic publication version and requires a new artifact identity/version plus output conformance.
- Supersession creates explicit lineage; prior releases remain addressable.
- Withdrawal preserves identity/history and removes active-use authority; it does not silently delete.
- Staleness is declared or propagated from an authority statement; it does not authorize live monitoring.
- Manifest regeneration changes only derivative manifest identity/version when authorities are unchanged.

## Publication manifest

Accept a publication manifest only as derivative, machine-readable catalogue/embedding metadata emitted from authoritative BriefForge records.

The manifest must fail closed on conflict with Ready, release/lifecycle records, renderer results, or artifact inventory. It cannot correct those authorities.

AtlasForge may catalogue, link, or embed by consuming emitted metadata. BriefForge remains complete and valid without AtlasForge and knows no AtlasForge route, index, search, portal, user, session, or global-navigation state.

## Rejected/deferred alternatives

- `Frozen publication`: rejected because freeze already has constitutional and ADPM meanings.
- Publication as only a Ready status/event with no immutable record: rejected as insufficient for identity/lineage/audit.
- Manifest as semantic authority, portal database, registry, or discovery service: rejected.
- One version number for semantic release, evidence, Ready, renderer, artifact, and manifest: rejected.
- Bounded parameterized publication admission: deferred to the next semantic-authority task.

## Non-authorization

No manifest serialization, schema, emitter, lifecycle validator, catalogue, AtlasForge integration, renderer change, or runtime implementation is authorized.
