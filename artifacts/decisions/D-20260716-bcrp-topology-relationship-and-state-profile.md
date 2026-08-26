# D-20260716 BCRP Topology, Relationship, and State Profile

Date: 2026-07-16
Status: accepted
Task: TASK-044

## Decision

BriefForge accepts `briefforge-core-representation-profile` version `1.0.0` (BCRP 1.0) as the single initial renderer-independent Representation Profile.

BCRP is a bounded bundle of independently addressable typed records joined by stable identity references. It is not one monolithic document and does not prescribe a transport. Its root kinds cover Presentation Brief, Portable Presentation Material, Candidate, Validation Judgment, Ready, Publication Release Record, renderer capability and compatibility/expression plan, generated-artifact audit, semantic artifact conformance, and derivative Publication Manifest.

Canonical relationship directions are source-owned and one-way. Qualifiers and obligations point to limited targets; composition parents own ordered child edges; state projections point to every applicable component; release points to Ready/snapshots; audit points to request/plan/release/Ready/renderer/artifact; manifest points to source authorities. Reverse indexes are derived, disposable, non-authoritative, and excluded from fingerprints.

BCRP represents independent value, evidence, consistency, and lifecycle dimensions through explicit scoped state assertions. Transport null and property absence have no semantic meaning. Finite selection uses complete materialized state projections; deltas, inheritance, wildcards, Cartesian products, live queries, and computation are rejected.

## Rationale

TASK-043 fixed the graph and authority boundaries but deferred profile topology, canonical direction, and concrete state/selection representation. One-way canonical edges avoid contradictory duplicate authority. Complete selection projections cost more space but make misleading inherited statements, caveats, labels, or evidence directly detectable.

## Alternatives considered

- one monolithic package document — rejected; lifecycle and derivative records have independent owners and times;
- canonical bidirectional links — rejected; divergence would create dual authority;
- universal status/null — rejected; it collapses independent semantics;
- selection deltas or generated combinations — rejected; compactness does not justify narrative risk;
- current runtime dataclasses — rejected as incomplete implementation evidence.

## Consequences

- Every mandatory TASK-041 through TASK-043 responsibility has one canonical owning record.
- Candidate -> Judgment -> Ready and publication lifecycle remain unchanged.
- Reverse traversal is built at read time and never corrects source records.
- DSB-007 remains intact; generic external references are sufficient.
- No implementation is authorized by this decision.
