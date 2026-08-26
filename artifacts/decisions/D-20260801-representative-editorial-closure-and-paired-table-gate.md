# Decision: Representative Editorial Closure and Paired-Table Gate

Date: 2026-08-01
Status: Accepted
Decision owner: BriefForge project authority
Related task: TASK-064

## Context

TASK-063 mechanically completed the accepted terminal publication chain but failed independent editorial reconciliation. Material T-039 synthesis, dependence, selection, and methodological content was omitted or compressed, and an intended seven-row paired relationship table became fourteen generic value-slot rows.

TASK-064 assessed whether this defect required a BCRP capability change or could be corrected through a complete source-to-Candidate authoring contract and a pre-release gate.

## Decision

1. Existing BCRP semantic representation capacity is sufficient. Exact decimals, statements, ordered sections, graph references, qualifications, provenance, obligations, and finite selections can express the corrected source meaning and seven paired relationship rows without production changes.
2. A representative Candidate must not be promoted until it passes the versioned editorial-closure and paired-table pre-release gate.
3. Every ledger-declared provenance and obligation attachment is exact and non-transitive; parent or root targeting does not substitute for an item’s declared destination.
4. Independent editorial and source-to-content mapping review occurs before Judgment, Ready, Release, or any terminal publication act.
5. TASK-063 remains immutable and `BLOCKED / NOT RECONCILED`; its mechanical success is historical evidence, not editorial authority.
6. The selected next disposition is a later fresh Candidate attempt under a single unactivated successor task. No capability-correction task is justified by current evidence.

## Alternatives considered

### Expand BCRP or change production code

Rejected. Existing representation surfaces are sufficient, and no demonstrated schema or validator gap requires production change.

### Repair or retry TASK-063

Rejected. TASK-063 is completed failed history and its Candidate, Release, artifact, and lifecycle evidence are immutable.

### Treat renderer mechanics as editorial proof

Rejected. Mechanical completion cannot establish complete source consumption or correct editorial topology.

### Leave review after Release construction

Rejected. This allowed the TASK-063 defect to pass through the technical chain. Review is now a pre-release gate.

## Consequences

- A later Candidate must consume the complete ledger and exact paired-table contract.
- Fourteen generic value rows fail closed.
- Missing, dangling, transitive-only, or namespace-drifted provenance/obligation attachments fail closed.
- No production, test, fixture, renderer, schema, or BCRP change follows from this decision.
- TASK-064 creates no Candidate or downstream publication authority.

## Next disposition

Recommend, but do not activate:

`TASK-065 — Fresh Representative Candidate Authoring Under Editorial-Closure and Paired-Table Gate`
