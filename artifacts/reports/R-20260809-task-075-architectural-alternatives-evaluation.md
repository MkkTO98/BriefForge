# TASK-075 Architectural Alternatives Evaluation

Date: 2026-08-09
Status: complete

## Evaluation criteria

Each alternative was assessed for truthfulness, authority ownership, identity stability, byte binding, deterministic reconstruction, provenance, completeness, collision and namespace handling, traversal, planner independence, validation sovereignty, frozen compatibility, migration cost, TASK-071 eligibility, parallel authority, semantic shadow risk, replay/substitution resistance, persistence/reload, and consequences for conformance/Manifest.

## Summary ruling

Accepted combination:

- Alternative 2 as the paired authority-domain foundation;
- Alternative 3 as a verified derived view, never a source authority;
- Alternative 4 as one existing planner with exact profile-dispatched resolvers, never a second planner;
- Alternative 5 only as reproducible non-authoritative evidence/cache;
- Alternative 6 for clean future authoring;
- Alternative 8 as the required versioned Plan coverage contract.

Rejected as selected solutions: Alternatives 1, 7, 9, and 10. Reauthoring remains an explicitly authorized fallback only if byte-preserving revalidation is later prohibited.

## 1. Promote paired semantics into core BCRP

Ruling: **Rejected as disproportionate**.

Benefits: first-class traversal and one generic graph. Costs: transfers paired validation sovereignty, requires a core major version, changes canonicalization/identity semantics, duplicates representations, and cannot retroactively change TASK-071 bytes. It does not by itself prove equality between the current core and paired representations. It creates high migration and frozen-history risk for little benefit.

## 2. Versioned extension-owned traversable semantic subgraph

Ruling: **Accepted foundation**.

The paired profile retains authority over paired objects, edges, ordering, requirements, and mappings. Exact owner/name/version/contract dispatch, bounded canonical decoding, complete source consumption, namespace separation, and deterministic graph digest prevent arbitrary opaque extension data from becoming semantics. Historical paired v3 bytes remain unchanged; future profiles may serialize a first-class form.

## 3. Canonical composite/effective graph

Ruling: **Accepted only as a verified derived view**.

The exact Candidate/profile bytes remain sole serialized Candidate authority. The effective graph contains domain-qualified nodes and owner-governed edges. Nontraversable counterpart consistency-proof records are attached derivation evidence outside both source graphs and are structurally unavailable to traversal/resolution APIs. The view binds Candidate and extension bytes, resolver versions, source graph digests, proof digest, and final graph digest. It cannot be edited, used as a new ontology, or trusted without reconstruction.

## 4. Planner dispatch to an exact paired resolver

Ruling: **Accepted with strict limits**.

There remains one Plan-producing planner. Exact profile dispatch calls an extension-owned resolver that returns verified planning material; the resolver cannot issue Plans. Unknown, mixed, duplicate, or partially supported semantic authority families fail closed. This preserves planner independence and paired validation sovereignty.

## 5. Governed derived semantic index/projection

Ruling: **Accepted only as non-authoritative evidence/cache**.

A persisted graph derivation record improves audit, reload, and recovery. It must bind exact source bytes and reproduce from them. It cannot authorize planning or publication by itself. Stale, foreign-Candidate, foreign-version, incomplete, or nonreproducible indexes reject. Treating it as source authority would create semantic shadow reconstruction and parallel authority.

## 6. New Candidate/profile version with first-class paired semantics

Ruling: **Accepted for future authoring**.

A profile successor should make domain, graph, requirement keys, mappings, and traversal explicit. It cannot reinterpret historical Candidates. Mixed old/new forms require an explicit composition contract. TASK-071 uses the governed legacy decoder/effective-graph route rather than changing bytes.

## 7. Reauthor TASK-071

Ruling: **Rejected as necessary/default**.

Exact TASK-071 contains sufficient governed paired bytes and all 144 mirrored local identities. Reauthoring would create a different Candidate, fingerprint, and cumulative attempt without solving an unavoidable information deficit. It remains a fallback only if separate governance later refuses byte-preserving derivation/revalidation. Historical TASK-069/TASK-071 evidence would remain immutable.

## 8. Modify or supersede Plan reference/coverage contract

Ruling: **Accepted and required through a versioned successor contract**.

Plan v1 cannot represent graph-scoped domain-qualified references, six profile-owned global requirement keys, the complete ordered row/relationship inventory, complete paired-closure and owner-inventory binding, graph digest, counterpart proof, or derivation evidence. It must not invent direct per-object planning coverage for all paired objects. Historical Plan v1 remains historically verifiable but cannot authorize new paired publication. One exact required Plan extension contract v2 on the existing Plan record is the narrowest compatible change; paired-v3 uses N mappings and TASK-071 has N=7.

## 9. Weaken coverage or treat inaccessible identities as covered

Ruling: **Rejected absolutely**.

This falsifies completeness, preserves vacuous zero-mapping success, hides omissions, weakens conformance, and permits substituted graphs. No compatibility or migration benefit justifies false coverage.

## 10. Opportunistically parse opaque JSON

Ruling: **Rejected absolutely**.

Ungoverned parsing lacks owner/version dispatch, bounds, canonicalization, completeness, namespace, and validation sovereignty. It enables parser differentials, foreign payload substitution, semantic shadowing, and replay inconsistency. The existing exact paired decoder is not opportunistic parsing; it is the only lawful source for the paired subgraph.

## Cross-criterion comparison

| Alternative | Truthful | Authority-safe | Byte-bound/deterministic | Frozen compatible | TASK-071 unchanged | Parallel/shadow risk | Selected role |
|---|---|---|---|---|---|---|---|
| 1 core promotion | possible only in major redesign | weak for current ownership | future-only | no | no | duplicate-authority risk | reject |
| 2 extension subgraph | yes | strong | strong | additive | yes via legacy decoder | low with exact owner | foundation |
| 3 effective graph | yes if derived | strong if non-authoritative | strong | additive | yes | high if promoted to source; otherwise low | derived view |
| 4 paired resolver dispatch | yes | strong with one planner | strong | additive | yes | low | planner integration |
| 5 derived index | yes as evidence | safe only if non-authoritative | strong | additive | yes | high if trusted as source | evidence/cache only |
| 6 profile successor | yes | strong | strong | historical coexistence | not itself | low | future authoring |
| 7 reauthor TASK-071 | yes but different Candidate | lawful only with new authority | strong | preserves history separately | no | low | fallback only |
| 8 Plan coverage successor | yes | strong | strong | versioned additive | yes | low | required |
| 9 weaken coverage | no | no | irrelevant | superficial only | yes | maximal | reject |
| 10 opportunistic parsing | no governed meaning | no | parser-dependent | no | nominal only | maximal | reject |

## Explicit anti-solutions

The selected architecture rejects:

- lexical equality as automatic cross-domain identity equality;
- structural resemblance as authority;
- hidden dangling references;
- zero coverage as success;
- arbitrary JSON parsing;
- caller-authored graph nodes, mappings, digests, Audit semantics, or Conformance semantics;
- a second planner, projection, renderer, conformance system, Manifest authority, or publication lifecycle;
- silent mutation of frozen BCRP, paired v3, TASK-060, TASK-062, TASK-067, or TASK-071 bytes.