# D-20260808 — Candidate-Stage Authoring Is Distinct from Release-Gated Terminal Execution

Date: 2026-08-08
Status: **Accepted for TASK-069**
Task: TASK-069

## Decision

Preserve TASK-067 authority unchanged while distinguishing two existing lifecycle stages.

Candidate-stage authority consists only of constructing the Brief + Material + Candidate closure through `author_candidate_bundle`, validating BCRP L0-L2 and the governed paired semantic extension, and persisting deterministic Candidate evidence.

Publication-stage authority begins only after a separately governed Judgment and Ready package exist. The accepted sequence remains:

```text
Judgment -> Ready -> Release -> compatibility Plan
-> PairedUpstreamAdmissionToken -> projection -> controlled rendering
-> conformance -> Manifest admission
```

Candidate-stage semantic acceptance grants no authority to enter any publication-stage operation.

## Rejected alternatives

1. Add a Candidate-stage projection or token boundary — rejected because it weakens and duplicates TASK-067 authority.
2. Construct a governed Release merely to validate a Candidate — rejected because it reverses lifecycle purpose and manufactures downstream authority prematurely.
3. Use TASK-062 projection as fallback — rejected because it cannot preserve the TASK-064 paired topology.

## Identity disposition

TASK-064 reserved fresh `task065` Candidate-stage identities. TASK-065 and TASK-068 created no Candidate and consumed zero attempts. TASK-069 is the first task authorized to instantiate exactly these reserved identities, preserving all internal TASK-064 references without namespace rewriting.

## Consequences

- `author_candidate_bundle` remains unchanged and is callable before lifecycle records exist.
- TASK-069 may prove Candidate semantic sufficiency for later TASK-067 projection, but cannot claim projection, rendering, conformance, Manifest, or visual fidelity.
- A later separately authorized task is required for Judgment → Ready → Release → Plan → token → terminal execution.
