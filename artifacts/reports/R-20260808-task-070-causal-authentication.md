# R-20260808 — TASK-070 Causal Authentication

## Authenticated endpoint

Canonical recovery reported no active task before TASK-070. No overlapping BriefForge process existed. TASK-069's final reconciliation and permanent marker matched their recorded SHA-256 identities.

## TASK-069 exact sequence

```text
complete preflight
-> create empty staging directory
-> exclusively write/fsync attempt marker and fsync parent
-> call generic BCRP pure constructor once
-> constructor creates three records and passes L0-L2
-> canonicalize profile bytes in memory
-> canonicalize Candidate-semantic bytes in memory
-> fingerprint in memory
-> run fallible post-author validator in memory
-> persist whole staged Candidate directory
-> write acceptance report
```

The incorrect record-order assertion failed before the first staged Candidate file write. Every operation from constructor return through validator completion was fallible and preceded durable preservation. This sequencing, combined with the validator defect and irreversible attempt boundary, caused the loss.

## Fallible window inventory

After consumption and before durable staging, the historical path included constructor dispatch, draft deep copies, BCRP object creation, L0-L2 validation, return, both canonical serialization domains, fingerprinting, canonical parsing, record-cardinality and extension checks, canonical round trips, extension reconstruction, paired semantic validation, TASK-064 traceability, hashing, and repeated L0-L2 validation.

Interruption in that window could leave only the consumed marker. Marker presence proves attempt consumption, not exact constructor entry, return, or call count.

## Reviewer incident disposition

`briefforge.bcrp.authoring.author_candidate_bundle` is publicly exported and accepts only three drafts. It has no attempt or caller authority. The reviewer reached it through a normal import and synthetic drafts. The invocation violated the read-only instruction and TASK-069 process boundary, but did not bypass a governed production entry point, create a governed attempt, or grant lifecycle authority.

TASK-070 corrects the architecture claim by naming that function a pure builder and introducing a separate durable coordinator as the only governed receipt issuer.

## Protected history

TASK-064 through TASK-069 task and decision artifacts were read as the authority chain. TASK-069 is not modified, retried, reconstructed, accepted, or made available. Its marker remains the cumulative attempt-1 evidence.
