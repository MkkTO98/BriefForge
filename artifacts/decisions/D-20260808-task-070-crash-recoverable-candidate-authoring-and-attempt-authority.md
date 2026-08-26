# D-20260808 — Crash-Recoverable Candidate Authoring and Attempt Authority

Date: 2026-08-08
Status: **Accepted for TASK-070**
Decision owner: BriefForge project authority through explicit TASK-070 direction
Task: TASK-070

## Context and root cause

TASK-069 durably consumed its sole attempt and successfully returned an in-memory BCRP Candidate closure. Its task-local coordinator then canonicalized and ran a fallible, order-defective validator before persistence. Canonical serialization correctly sorted records by kind and identity; the validator incorrectly expected authoring-role order. The validator rejected, the process terminated, and no Candidate bytes or fingerprint survived.

The generic `author_candidate_bundle` API is not a governed authority boundary. It is a reusable pure semantic/technical constructor that grants no attempt, identity, persistence, acceptance, lifecycle, or publication authority. TASK-069 governance lived in its wrapper. The delegated reviewer's synthetic invocation was therefore an instruction/process violation, not a bypass of a production authorization gate.

## Decision

Introduce one source-neutral governed Candidate-authoring coordinator. Keep the generic BCRP constructor callable as an explicitly pure builder. Only a durable receipt and state closure emitted through the coordinator can constitute a governed Candidate attempt.

The coordinator owns, in this order:

1. exact canonical authority and binding verification;
2. same-attempt exclusive lock;
3. durable attempt consumption;
4. one pure semantic-builder invocation;
5. canonical serialization and fingerprinting;
6. attempt-specific durable whole-directory staging;
7. durable validation-pending transition;
8. post-staging semantic validation;
9. one explicit accepted or not-accepted transition.

A governed successful-authoring receipt is returned only after staged bytes and their receipt are recoverable. Pure-builder return alone is never governed success.

## Durable monotonic state model

Each state is an immutable canonical commitment. Later states reference the exact binding and prior-state digest. Existing state files are never rewritten.

1. `PREPARED_NOT_CONSUMED`
   - exact task, Candidate, source snapshot, blueprint fingerprint, blueprint-derived campaign identity, cumulative attempt number, predecessor evidence paths and digests, attempt identity, authoring-input digest, paired semantic validation profile and expected closure digest, authority-decision path and digest, ledger root, and output path are bound;
   - no constructor call is authorized unless this canonical record already exists under the accepted authority root;
   - interruption remains unused.
2. `INVOKED_CONSUMED`
   - exclusive creation plus file and parent-directory fsync permanently consumes the attempt;
   - it proves attempt unavailability, not successful constructor entry or return.
3. `AUTHORED_OUTPUT_DURABLY_STAGED`
   - one atomically published, parent-fsynced attempt directory contains canonical profile bytes, Candidate-semantic bytes, fingerprint, exact inventory, and a binding receipt;
   - it is immutable attempt evidence, not acceptance.
4. `VALIDATION_PENDING`
   - durable staging has been authenticated and acceptance validation remains outstanding or was interrupted.
5. `VALIDATED_ACCEPTED`
   - a bound validation result passed and explicitly references the exact staged receipt and fingerprint.
6. `VALIDATED_NOT_ACCEPTED`
   - bound validation failed; staged bytes and receipt remain immutable and recoverable.
7. `INDETERMINATE_CONSUMED_NO_OUTPUT`
   - consumption exists but no complete atomically published staged closure is recoverable; the attempt remains consumed and is never repeated.

Allowed transitions:

```text
PREPARED_NOT_CONSUMED
  -> INVOKED_CONSUMED
       -> AUTHORED_OUTPUT_DURABLY_STAGED
            -> VALIDATION_PENDING
                 -> VALIDATED_ACCEPTED
                 -> VALIDATED_NOT_ACCEPTED
       -> INDETERMINATE_CONSUMED_NO_OUTPUT
```

Recovery may add `VALIDATION_PENDING` after authenticating a complete staged closure, add `INDETERMINATE_CONSUMED_NO_OUTPUT` when consumption exists without a complete staged closure, finish an authenticated durable validation result, and complete an interrupted terminal hard-link transaction. It never invokes the builder. Exact protocol-generated temporary names are authenticated and durably cleaned under the attempt lock; malformed, multiple, or contradictory residue fails closed. Contradictory terminal states, missing bindings, malformed bytes, receipt/file disagreement, unknown files, or path drift also fail closed.

## Interruption contract

- Before consumption: remain prepared and unused.
- After consumption but before complete staged publication: classify indeterminate and consumed; never rerun.
- During partial staging: retain forensic partial bytes; they do not constitute staged output or acceptance.
- After whole staged-directory publication: authenticate receipt and bytes, enter or resume validation pending, never rerun.
- After fingerprinting but before validation: fingerprint and bytes survive in staged closure; resume validation only.
- During validation before a durable result: preserve staged closure and rerun only validation on recovery. After durable validation evidence: authenticate that result and finish the terminal transaction without revalidation.
- After accepted or rejected terminal state: authenticate and return the terminal receipt; never rerun authoring or silently change disposition.

## Exact durability guarantee

On the supported local filesystem, each immutable file commitment is written to a same-directory exclusive temporary file, file-fsynced, published with an exclusive hard link, parent-directory-fsynced, and then has its temporary name durably removed. Exact crash residue is authenticated and completed or removed under the attempt lock. Terminal state and seal are hard links to one authenticated transaction inode. The staged output is written as a complete same-filesystem directory, each file and the directory are fsynced, the directory is atomically renamed, and its parent is fsynced.

This provides crash-recoverable local filesystem commitments. It does not claim atomicity across unrelated files, storage hardware beyond successful `fsync`, malicious same-user filesystem modification, or distributed systems. A crash between consumed state and staged-directory commit is intentionally indeterminate and consumed.

## Invocation authority

The pure builder remains callable for tests and ungoverned technical construction. Such calls can never create a governed receipt.

The governed entry points for authoring and recovery accept only a pre-existing canonical prepared authority record from the canonical authority root and enforce exact draft identities before consumption, fixed governed ledger/output roots, a canonical authority-decision artifact and digest under `artifacts/decisions`, exact predecessor evidence paths and digests, blueprint-derived campaign identity, cumulative attempt number, path containment, single-use consumption, and same-attempt locking. A caller cannot provide construction or validation callbacks. Copying, renaming, or changing any binding invalidates its digest and path binding. Test scope is additionally forbidden from overlapping any governed root or its ancestors/descendants.

This is repository-governance enforcement, not cryptographic protection against a malicious process with permission to rewrite canonical authority files. The accepted trust boundary is canonical project-state integrity and OS filesystem permissions.

## Serialization and validation

Canonical serialization order remains authoritative. Candidate-stage validation checks exact record identities and cardinalities without imposing authoring-role physical order. Governed validation is fixed to BCRP L0-L2 plus the versioned paired semantic-closure validator. It reconstructs the paired extension, validates its complete source-neutral topology, and requires equality to the authority-bound semantic-closure digest. This preserves exact sections, statement order, membership and attachments, qualifications, obligations, provenance, relationship-owned paired rows, values, governed columns, renderer requirements, and mappings without importing TASK-064-specific fixture logic into production.

Filesystem presence alone never means accepted. Acceptance requires a distinct terminal commitment referencing a passing bound validation result.

## Historical and cumulative attempt authority

TASK-069 remains consumed, unavailable, and not accepted. Its marker is immutable. Renaming a task or Candidate does not erase its attempt.

Attempt accounting is cumulative for the representative TASK-064 publication campaign while each durable authorization is also task-, Candidate-, and attempt-identity-specific. Campaign identity is derived from the immutable blueprint fingerprint rather than a renameable task or Candidate label. TASK-065 and TASK-068 count as zero; TASK-069 counts permanently as cumulative attempt 1. The coordinator authenticates the predecessor evidence explicitly named by authority; it deliberately does not add a generic global sibling-attempt registry. Canonical authority creation remains the governance boundary for preventing two sibling authorities from claiming the same campaign position.

A future Candidate attempt is authorized in principle only as a separately and explicitly human-authorized successor attempt after TASK-070 is accepted. It would be cumulative attempt 2, require genuinely new Brief/Material/Candidate instance identities or an explicit lineage decision for any reused semantic identities, preserve exact TASK-064 internal contract identities, bind TASK-069 as predecessor evidence, and state why it is not retry laundering. TASK-070 does not create that authority, task, identity, or attempt.

No additional Judgment is required to authorize Candidate construction unless a future lifecycle decision says otherwise. Judgment, Ready, Release, Plan, token, and publication-stage work remain separately governed and absent.
