# D-20260801 — TASK-065 Stops Before Candidate Authoring on Accepted-Profile Representational Gap

Status: Accepted
Date: 2026-08-01
Decision owner: BriefForge
Task: TASK-065

## Context

TASK-064 established a 109-item editorial contract and an exact five-column, seven-relationship-row table contract. TASK-065 was authorized to translate that contract into exactly one fresh Candidate and, only after an independent pre-promotion gate, carry it through the existing TASK-062 terminal profile. Production capability changes, contract weakening, replacement Candidates, and renderer redesign were explicitly excluded.

Phase-1 source revalidation passed: all 13 admitted T-039 Git objects retained their exact lengths and SHA-256 identities, all 130 TASK-064 locators resolved, and the ledger/blueprint/table cross-references remained internally consistent.

Accepted-interface inspection then found hard incompatibilities before Candidate authoring:

- TASK-064 requires 76 statement identities, or at least 74 if both conditional statements are omitted; the terminal projection admits at most 32.
- TASK-064's interpretation and limitations sections require 27/29 and 32 children respectively; the accepted profile admits at most 17 children and 16 statements per leaf.
- TASK-064 requires 27 exact qualification edges; the accepted profile admits at most 16 relations and requires unique relation source identities.
- TASK-064 obligation, provenance, value-metadata, and table-support fields exceed the profile's strict schemas.
- The accepted renderer emits two slot-owned body rows per case—14 rows for seven relationships—and fixed headings, rather than the contract's seven relationship-owned rows and governed five columns.

## Decision

Stop TASK-065 before `author_candidate_bundle`.

Do not create a Candidate, Judgment, Ready record, Release, renderer output, Manifest, delivery, deployment, or TASK-056 evidence. Do not weaken or reinterpret TASK-064. Do not modify production code, tests, fixtures, TASK-063, TASK-064, or sibling projects inside TASK-065.

Close TASK-065 as `BLOCKED / NOT RECONCILED` with classification:

`TASK-064 representational-capacity conclusion does not fit the existing accepted TASK-062 terminal profile and renderer without excluded capability changes.`

## Alternatives rejected

1. **Compress 76 identities into 32 statements.** Rejected because TASK-065 requires exact destinations, identities, hierarchy, ordering, attachment topology, and no weakened composition.
2. **Omit mandatory or supporting records.** Rejected because the pre-promotion gate is fail-closed over all 109 governed treatments.
3. **Encode missing topology in unknown fields or extensions.** Rejected because accepted projection uses strict schemas and because hiding semantics outside the governed contract would be a bypass.
4. **Allow the renderer's 14 slot rows.** Rejected because this repeats TASK-063's diagnosed defect.
5. **Change the profile, renderer, schema, validator, tests, or fixtures.** Rejected as explicitly outside TASK-065.
6. **Consume the one Candidate attempt to collect failure evidence.** Rejected because the contradiction is already deterministic at Phase 1 and the task requires stopping at the earliest invalid boundary.

## Consequences

- TASK-064 remains authoritative as an editorial contract, but its statement that existing BCRP semantic capacity is sufficient is not evidence that the closed TASK-062 terminal profile can carry that contract.
- TASK-063 remains immutable failed history.
- TASK-062 remains authoritative for its accepted profile; it is not modified to fit TASK-065.
- No successor is activated or recommended as authorized work by this decision.
- Any future work must separately decide whether to revise the authoring contract, create a new versioned terminal profile/renderer, or prove a different exact representation. That is a capability/scope decision and cannot be smuggled into TASK-065.

## Evidence

- `artifacts/reports/R-20260801-task-065-source-and-contract-admission.json`
- `artifacts/reports/R-20260801-task-065-pre-authoring-interface-contradiction.json`
- `src/briefforge/representative_projection.py`
- `src/briefforge/representative_renderer.py`
- `src/briefforge_terminal_profile/projection.py`
- independent delegated read-only review recorded in TASK-065 completion evidence
