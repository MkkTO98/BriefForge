# TASK-069 — Governed Paired-Terminal Candidate Authoring and Semantic Acceptance

Date: 2026-08-08
Status: **COMPLETED — BLOCKED / NOT ACCEPTED / RECONCILED**
Task type: single governed Candidate-stage authoring and semantic acceptance

## Objective

Author exactly one governed BCRP Candidate closure from the authoritative TASK-064 source, ledger, blueprint, and seven-row table contract through the unchanged production `briefforge.bcrp.authoring.author_candidate_bundle` function. Validate Candidate-stage identity, topology, traceability, canonical serialization, and paired-terminal semantic eligibility without entering publication-stage authority.

## Lifecycle reconciliation

Candidate-stage authority is:

```text
source/blueprint admission
-> durable single-attempt accounting
-> one author_candidate_bundle call
-> BCRP L0-L2 technical validation
-> Candidate semantic acceptance
```

Publication-stage authority remains unchanged and out of scope:

```text
Judgment -> Ready -> Release -> Plan -> paired upstream token
-> projection -> controlled rendering -> conformance -> Manifest
```

TASK-069 neither creates a Candidate-stage projection/token boundary nor constructs a Release to validate a Candidate.

## Governed identities and paths

TASK-064 reserved fresh `task065` semantic identities. TASK-065 and TASK-068 instantiated none and consumed zero attempts. TASK-069 explicitly authorizes their first and only instantiation:

- Brief: `brief:task065-cross-inquiry`
- Material: `material:task065-t039`
- Candidate: `candidate:task065-cross-inquiry`
- Candidate evidence root: `artifacts/pilots/task069/candidate/`
- Attempt marker: `artifacts/pilots/task069/.candidate-authoring-single-use`
- Acceptance report: `artifacts/reports/R-20260808-task-069-candidate-semantic-acceptance.json`

The internal TASK-064 section, statement, table, row, value, qualification, provenance, and obligation identities remain exact. They are not renamed to TASK-069.

## Attempt boundary

All source, locator, blueprint, topology, extension-envelope, output-path, and preflight checks occur first. Immediately before the sole production call, write and fsync the exclusive attempt marker. No fallible operation may intervene. Once the marker exists, the attempt is permanently consumed regardless of success, exception, or interruption.

Tests may inspect or replace the call boundary but must not invoke the real production `author_candidate_bundle`; only the governed execution may do so once.

## Required topology

- 6 sections
- 76 authored statements in governed composition order
- 27 qualification edges
- 5 obligations
- 8 provenance objects
- 7 relationship-owned paired rows
- 14 values
- 5 governed columns
- exact attachment ownership and exact consumption
- explicit value-state semantics
- resolved qualification, obligation, and provenance targets

## Prohibited scope

No production authority changes; test-only construction; manual Candidate imitation; second Candidate-authoring call; Judgment; Ready; Release; Plan; upstream token; projection; renderer; conformance; Manifest; TASK-062 fallback; delivery; deployment; HTTP/TASK-056 evidence; TASK-051 work; AtlasForge work; network/database/dependency/Git action; or successor activation.

## Success criteria

- exactly one attempt consumed and exactly one production authoring call;
- Candidate identity/fingerprint and canonical bytes persisted once;
- source → blueprint → Candidate closure is exact;
- independent semantic review passes with no accidental publication machinery;
- focused, predecessor, full, security, governance, and filesystem checks pass;
- no task remains active at closeout.

## Outcome

All pre-attempt gates passed: 13 immutable InsightForge objects, 130 TASK-064 locators, exact `6/76/27/5/8/7/14/5` topology, direct semantic traceability, exact terminal authority inventory, and two independent pre-attempt reviews.

The sole governed `author_candidate_bundle` call returned successfully for `candidate:task065-cross-inquiry`, proving in-memory production L0-L2 success. A task-local post-author validator then falsely rejected the canonical reload because it required authoring-role record order after canonical serialization had correctly sorted records by kind and identity.

The exact canonical bytes and fingerprint were not persisted before that rejection. The permanent marker had already consumed the attempt. A second production call or manual reconstruction is prohibited. The Candidate is therefore not semantically accepted and TASK-069 cannot progress to any successor.

The validator defect was corrected for future use without retrying TASK-069. See `artifacts/reports/R-20260808-task-069-sole-attempt-adjudication.md`.

One delegated post-attempt reviewer separately violated its read-only instruction by invoking the production author once with unrelated synthetic in-memory identities. It produced no TASK-069 identity or artifact and does not alter the governed TASK-069 attempt count, but it is explicitly recorded as a tooling/process violation.

No Judgment, Ready package, Release, Plan, token, projection, rendering, conformance, Manifest, delivery, deployment, HTTP evidence, TASK-056 evidence, TASK-051 work, AtlasForge work, or successor activation occurred.
