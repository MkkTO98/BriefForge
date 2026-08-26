# D-20260808 — TASK-071 Successor Candidate Attempt Authority and Identity Lineage

Date: 2026-08-08
Status: **Accepted for TASK-071**
Decision owner: explicit human TASK-071 instruction, interpreted through the accepted TASK-070 future-attempt ruling
Task: TASK-071

## Authority gate

TASK-070 canonically ruled that a future Candidate attempt is authorized in principle only as a separately and explicitly human-authorized successor after TASK-070 acceptance. It must be cumulative attempt 2 in the same representative TASK-064 campaign, bind TASK-069 as consumed predecessor evidence, use genuinely new Brief/Material/Candidate instance identities or an explicit lineage decision, preserve TASK-064 internal contract identities, and explain why it is not retry laundering. No additional Judgment is required for Candidate construction.

The explicit TASK-071 instruction supplies exactly that human successor-attempt authorization. It does not reopen or retry TASK-069, alter its marker, reset cumulative accounting, create a new campaign, or grant publication-stage authority. The gate therefore passes.

## Governing scope and cumulative history

Attempt accounting attaches cumulatively to the immutable TASK-064 authoring-blueprint fingerprint, not to a task label or Candidate label.

- Blueprint artifact: `artifacts/reports/R-20260801-task-064-source-to-candidate-authoring-blueprint.json`
- Blueprint SHA-256: `424fd07da96e1e0914385997dcdb9f4f645f1d6228b4d9f9bb93cfdfbe4689ae`
- Campaign identity: `blueprint:424fd07da96e1e0914385997dcdb9f4f645f1d6228b4d9f9bb93cfdfbe4689ae`
- TASK-065: 0 attempts.
- TASK-068: 0 attempts.
- TASK-069: cumulative attempt 1, permanently consumed, unavailable, and not accepted.
- TASK-070: 0 attempts; coordinator capability only.
- TASK-071: exactly one authorized successor operation at cumulative attempt 2.

Changing the task number does not reset accounting. TASK-071 is legitimate because it uses a fresh outer lifecycle closure, the accepted crash-recoverable coordinator, and a new attempt position while preserving TASK-069 as predecessor evidence. It is not permission to reconstruct TASK-069 or recover its lost bytes.

## Exact identities and lineage

The new outer BCRP instance identities are:

- task: `TASK-071`
- Brief: `brief:task071-cross-inquiry`
- Material: `material:task071-t039`
- Candidate: `candidate:task071-cross-inquiry`
- attempt: `attempt:task071-representative-campaign-002`
- cumulative attempt number: `2`
- source snapshot: `source-snapshot:insightforge-t039:ab61ed6d7cde638ca8433e71a13480981a5a45364523d16cc9ee77b6d73da689`
- semantic profile: `briefforge:paired-terminal-semantic-closure:1.0.0`
- validator: `briefforge:bcrp-L0-L2+paired-semantic-closure:1.0.0`

These identities are a new lifecycle envelope. All TASK-064-authored internal section, statement, qualification, obligation, provenance, table, row, value, column, authority, snapshot, external-reference, unit, semantic-type, purpose, audience, classification, evidence-role, transformation, method, and package identities remain exact. Only the three outer record identities and the paired extension's Candidate authority/target binding change to the new Candidate. Candidate `brief_ref` and `material_refs` bind the new Brief and Material.

This is the explicit lineage decision required by TASK-070. It prevents casual namespace rewriting of the frozen editorial contract while preventing reuse of TASK-069's outer Candidate instance identity.

## Governed paths and predecessor evidence

Canonical roots remain fixed by TASK-070:

- authority root: `artifacts/governance/candidate-authoring-authority`
- ledger root: `artifacts/state/candidate-authoring-ledger`
- output root: `artifacts/pilots/candidate-authoring-output`

Attempt-specific paths are:

- authority: `artifacts/governance/candidate-authoring-authority/attempt:task071-representative-campaign-002.authority.json`
- ledger: `artifacts/state/candidate-authoring-ledger/attempt:task071-representative-campaign-002/`
- immutable staged closure: `artifacts/pilots/candidate-authoring-output/attempt:task071-representative-campaign-002/`

The sole predecessor evidence path is `artifacts/pilots/task069/.candidate-authoring-single-use`, SHA-256 `05d7d994a64b798417e21b26ba5782cbc31d87a68af39e0a13f282a073e8a70f`. It supplies the one predecessor digest required for cumulative attempt 2. TASK-069's task and reconciliation remain separately protected by baseline and closeout verification.

## Consumption, acceptance, and recovery

Preparation creates only the canonical authority record and immutable `PREPARED_NOT_CONSUMED` state. Consumption occurs only when the accepted public `governed_author_candidate` route durably appends `INVOKED_CONSUMED`. Exactly one call is authorized.

The accepted fixed production builder and paired-semantic validator are owned by the coordinator. Caller-supplied builders, validators, and fault callbacks are forbidden. Immutable whole-directory staging must precede validation. Acceptance requires exact BCRP L0-L2 and paired semantic-closure evidence. Failure preserves staged bytes and fingerprint with `VALIDATED_NOT_ACCEPTED`; consumed-without-output becomes `INDETERMINATE_CONSUMED_NO_OUTPUT`.

Recovery authority is only `governed_recover_candidate` with the exact authority path and digest. Recovery may resume validation or finish the terminal transaction but never reconstructs or repeats authoring.

## Excluded authority

No Judgment, Ready package, Release, compatibility Plan, token, projection, rendering, conformance, Manifest, delivery, deployment, HTTP evidence, TASK-056 work, TASK-051 work, AtlasForge work, publication action, retry, or automatic successor activation is authorized.
