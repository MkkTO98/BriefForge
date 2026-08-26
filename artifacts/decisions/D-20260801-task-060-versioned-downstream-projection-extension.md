# D-20260801 — TASK-060 Versioned Downstream Projection Extension

Date: 2026-08-01
Status: accepted, implemented and verified
Task: TASK-060

## Decision

Implement one parallel downstream representative profile. Do not modify TASK-053 renderer/projection/worker/conformance modules.

## Modules

Add separate fixed modules for profile admission/projection, representative renderer/worker, controlled invocation and independently derived conformance. Renderer and assessor may share canonical BCRP primitives only—not projection construction, expected inventory, HTML parsing/generation, numeric display or conformance decisions.

## BCRP boundary

The Candidate’s fixed table exhibit carries authored case IDs, explicit order and two keyed value references inside immutable Release semantics. This is a concrete profile of BCRP’s admitted keyed exhibit/value-binding structure, not a new record kind or downstream-created analytical grouping. All admitted/prohibited fields are fixed by the content admission matrix.

## TASK-054 seam

TASK-054 gains one exact atomic chain-variant dispatch covering:

- renderer identity/version/adapter/digest;
- invocation extension contract;
- semantic profile identity/version;
- assessor implementation/version;
- conformance extension contract;
- exact audit/conformance record topology;
- exact persisted verifier.

Only the historical v1 and representative v2 tuples are allowed. Unknown, partial or mixed tuples fail before verifier execution. Manifest authority, artifact inventory, accepted aggregate verdict, lifecycle, persistence and publication semantics remain unchanged. TASK-055 and TASK-056 remain unchanged.

## Historical preservation

V1 bytes, implementation digest, behavior, records and persisted verification remain exact. V2 requires fresh declaration, Plan, invocation/conformance authorizations and derivative evidence. No previous Release, Plan, artifact, Manifest, delivery or deployment is mutated or reclassified.

## Stop conditions

Stop if implementation requires a BCRP kind/model/canonicalization change, generalized schema/template/table language, caller-defined pairing/order, broad downstream authority change, browser evidence, sibling runtime coupling, analytical interpretation or historical mutation.
