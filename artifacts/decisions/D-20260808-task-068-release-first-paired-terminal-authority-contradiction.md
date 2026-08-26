# D-20260808 — TASK-068 Release-First Paired-Terminal Authority Contradiction

Date: 2026-08-08
Status: **Deferred — blocking question preserved; no architecture change authorized**
Task: TASK-068

## Context

TASK-068 requires one governed Candidate to traverse the exact TASK-067 controlled paired-terminal route while prohibiting governed Publication Release construction. TASK-067 intentionally made projection authority Release-first.

## Finding

The two constraints cannot both hold:

- paired projection requires an issuer-held `PairedUpstreamAdmissionToken`;
- the sole issuer verifies a Publication Release and Plan, reconstructs semantics from the Release-resident Candidate, and only then issues the token;
- controlled rendering, conformance, and Manifest admission all depend transitively on that token and Release closure.

No direct DTO, pure renderer, fixture, forged token, historical fallback, or task-local wrapper is an accepted substitute.

## Decision

Do not select an architecture change inside TASK-068. Stop before Candidate construction and preserve zero Candidate attempts consumed.

A future separately authorized reconciliation may choose exactly one bounded route:

1. permit the existing Release-first chronology for the one governed Candidate; or
2. specify and implement a separately versioned Candidate-stage admission/projection authority before retrying authoring.

Neither route is selected or activated by this decision.

## Preserved boundaries

TASK-064 through TASK-067 remain authoritative and unchanged. TASK-065 remains historical blocked evidence with zero attempts consumed. TASK-062 and all historical routes remain unchanged. No Candidate, Release, publication-chain act, production change, or successor activation is authorized.
