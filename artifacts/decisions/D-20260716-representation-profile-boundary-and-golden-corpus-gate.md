# D-20260716 Representation Profile Boundary and Golden Corpus Gate

Date: 2026-07-16
Status: accepted
Task: TASK-043

## Decision

A Representation Profile is a named, versioned mapping from the accepted semantic representation contract to one concrete abstract record/graph shape. It may decide containment versus references, canonical relationship direction, required profile properties, explicit state/absence encoding, extension namespaces, canonicalization, fingerprint prerequisites, and profile-level structural constraints.

It may not redefine semantic roles or authority, merge independent states, make transport null semantic, add requirements for serialization convenience, use renderer input as ontology, make Markdown canonical, or import speculative financial-domain fields.

ADPM semantic version, Representation Profile version, transport serialization version, renderer version, artifact version, and manifest-projection version remain separate axes.

Golden-corpus verdict: design is now justified, but corpus materialization is blocked until one initial Representation Profile is accepted with deterministic canonicalization, semantic equality, structural/semantic finding separation, extension behavior, and redaction/reference-fixture rules.

The exact successor is:

`TASK-044 — Initial Representation Profile and Golden Corpus Acceptance Specification`

It will define exactly one renderer-independent profile and specify—but not implement—the corpus inventory and expected layered findings. It will issue the later implementation gate.

## Rationale

A corpus created before a profile would accidentally make whichever handwritten JSON/YAML/Python shape appears first into semantic authority. Conversely, implementing several formats would create divergence before one coherent mapping has been tested.

TASK-039, ADPM, explicit state, conflict, finite selection, fallback, lifecycle, and manifest cases provide sufficient semantic pressure to design the corpus after the profile mapping is accepted.

## Alternatives considered

- Create corpus files immediately from TASK-039 JSON — rejected; current runtime is incomplete and TASK-039 carries a known renderer-audit table metadata inconsistency.
- Implement JSON schema next — rejected; schema remains derived and a semantic profile is not yet accepted.
- Specify several profiles/transports together — rejected; no operational need justifies multi-format control cost.
- Skip examples until implementation — rejected; adversarial examples are needed before implementation, but only after profile semantics are stable.
- Let a renderer contract define the profile — rejected; renderer convenience cannot own the canonical package.

## Consequences

- TASK-044 is specification-only.
- No schema, serializer, validator, builder, runtime, fixture, golden corpus, renderer, or API is authorized now.
- Future corpus cases must include positive and adversarial expected findings by layer.
- Existing fixtures remain evidence sources, not automatically accepted golden examples.
