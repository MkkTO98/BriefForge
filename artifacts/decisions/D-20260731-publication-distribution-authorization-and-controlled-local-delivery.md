# Decision: Controlled Local Delivery Is a Separate Leaf Authority

Status: Accepted
Date: 2026-07-31
Decision ID: D-20260731-publication-distribution-authorization-and-controlled-local-delivery

## Context

TASK-054 admits exact artifact bytes into one governed `PublicationManifestRecord`. It does not authorize transfer, destination placement, deployment, public availability or successful publication. TASK-055 requires the first downstream act while preserving those distinctions and BriefForge's presentation-only constitution.

## Decision

BriefForge may implement one specialized leaf companion for exact local-filesystem placement of Manifest-admitted derivative bytes when directly authorized. This is a controlled local delivery proof, not ownership of distribution infrastructure.

The boundary requires:

1. independent reload of the persisted Manifest and complete upstream authority chain;
2. current lifecycle eligibility immediately before delivery commit;
3. exact destination and ledger path/device/inode scope released by an authority in the Publication Release;
4. a canonical exact one-act authorization issued and externally committed by the trusted process after Manifest verification;
5. exclusive identity-keyed consumption before source-byte execution;
6. descriptor-relative staging, exact inventory verification and Linux `renameat2(RENAME_NOREPLACE)` installation;
7. durable prepared/completed commitments, independent reload and explicit rollback/pending/reconciliation states;
8. typed directed audit links and explicit negative claim scope.

Authorization, Manifest admission, controlled transfer, deployment and successful-publication claims remain distinct.

## Representation

TASK-055 uses immutable specialized companion dataclasses outside generic BCRP. It adds no BCRP core kind and does not encode delivery or deployment authority in `PublicationManifestRecord` extensions.

## Trust model

The issuer/executor is a trusted BriefForge process operating in controlled owner-only local directories. The proof does not claim human authentication, signatures/MACs, hostile-writer resistance, sandbox attestation, WORM storage, network delivery or public reachability.

## Alternatives rejected

- Treat Manifest existence as delivery authority: collapses separate claims.
- Caller-supplied destination/authorization strings: not independently governed.
- Reusable authorization or overwrite delivery: violates one-act exactness.
- Dynamic destinations, adapters or delivery runtimes: unnecessary and unsafe.
- New BCRP record kind: not required for this leaf companion.
- Modify TASK-054 for multi-artifact production: prohibited and unnecessary; generic mechanics are tested separately.

## Consequences

- Exact local placement can be proven and independently reloaded.
- Failure after durable installation is explicit `completion-pending` and can only be completed by exact reconciliation; no replay performs a second transfer.
- Historical delivery remains immutable while current eligibility is evaluated separately using historical and current lifecycle scopes.
- Deployment, hosting, reachability, reader access and publication success remain unauthorized future boundaries.
