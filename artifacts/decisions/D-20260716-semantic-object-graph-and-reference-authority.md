# D-20260716 Semantic Object Graph and Reference Authority

Date: 2026-07-16
Status: accepted
Task: TASK-043

## Decision

BriefForge accepts a renderer-independent semantic object graph joining the existing Presentation Brief, Portable Presentation Material, Candidate -> Validation Judgment -> Ready lifecycle, Publication Release Record, renderer requirements, derivative artifacts, and manifest projection through stable identities and typed authority-preserving relationships.

The graph is semantic, not a required serialized nesting. Existing names remain authoritative. `PresentationRequest` and `ResolvedPresentationInput` are not new parallel concepts; a future profile may use them only as explicit implementation labels mapped respectively to Presentation Brief and Portable Presentation Material.

Presentation Statement representation must preserve independent dimensions for content posture, authority/provenance, communication function, attention, encounter/composition, evidence state, value state, consistency state, lifecycle references, and obligations. One universal type/mode/status is rejected.

References target stable semantic identities and relationship kinds, never array positions, serialization paths, DOM paths, or renderer identifiers. Fingerprints prove integrity under a named rule, not truth or authority.

Package-owned renderer requirements remain distinct from downstream renderer capability declarations. A finite Selection Set may contain only closed, fully authored, evidence-bound, independently valid presentation states.

## Rationale

TASK-041 and TASK-042 already decide the responsibilities but not their representation allocation. The current runtime proves a small lifecycle but omits publication, multidimensional role/state, selection, renderer requirement, semantic fallback, and semantic conformance responsibilities. Treating it as canonical would freeze known incompleteness.

Typed identity edges preserve renderer independence, partial encounter order, external authority, and transport freedom. Reusing accepted concepts prevents duplicate intake/resolution layers.

## Alternatives considered

- Current Python dataclasses as the contract — rejected; implementation evidence is incomplete and non-authoritative.
- Schema-first nested document — rejected; structure would define ontology before semantics.
- One statement enum — rejected; it collapses distinct authorities and produces invalid implication.
- Renderer-input graph — rejected; it transfers semantic authority to delivery mechanics.
- Bidirectionally serialize every relationship — deferred to the initial profile; semantic consistency is required, duplicate storage is not.

## Consequences

- One future Representation Profile must map this graph without semantic loss.
- Current runtime and TASK-039 artifacts are not retroactively invalidated or modified.
- Generic typed external references remain sufficient while financial-domain semantics are deferred.
- AtlasForge manifest/catalog fields remain derivative consumer boundaries.
- No runtime, schema, serializer, validator, renderer, or fixture implementation is authorized.
