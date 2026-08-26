# Publication Distribution Authorization and Controlled Local Delivery

Status: Implemented by TASK-055
Date: 2026-07-31

## Purpose

Define the first fail-closed boundary after Publication Manifest admission: one exact issued authorization may copy the exact Manifest-admitted bytes to one exact controlled local directory and persist independently verifiable delivery evidence.

## Inputs

- persisted `PublicationManifestRecord` evidence and TASK-054 authorization;
- complete TASK-047–054 evidence and authorities;
- exact artifact source paths admitted by the Manifest;
- released controlled-local-delivery authority scope;
- immutable `ControlledLocalDeliveryAuthorization`;
- exact destination parent/basename and commitment-ledger path/device/inode identities.

## Profiles

- Policy: `briefforge-controlled-local-delivery-policy:1.0.0`
- Profile: `briefforge-controlled-local-directory-delivery-profile:1.0.0`
- Implementation: `briefforge-controlled-local-directory-delivery:1.0.0`
- Output-boundary class: controlled local directory only.

## Authority model

`issue_controlled_local_delivery_authorization` independently reloads the Manifest and upstream chain, verifies current eligibility and exact released destination scope, then exclusively persists canonical authorization issuance evidence plus an external commitment. The resulting sealed marker is required for execution. A caller-created authorization dataclass is not executable.

Authorization binds exact policy/profile/implementation, authority identity/owner/role, causal times, Manifest/Release/lifecycle/artifact-set fingerprints, ordered delivery inventory, destination and ledger identities, attempt/evidence identities, output limits and explicit exclusions.

## Execution

`perform_controlled_local_delivery`:

1. independently reloads issued authorization, Manifest and complete upstream authority chain;
2. verifies current lifecycle eligibility and exact authorization bindings;
3. opens and checks destination/ledger directories and their released inode identities;
4. consumes the authorization by identity before source-byte execution;
5. independently reads exact regular source files and verifies digest/length against Manifest inventory;
6. creates a deterministic owner-only staging directory, writes exact inventory and canonical evidence with exclusive descriptor-relative operations, fsyncs and independently verifies closure;
7. writes a prepared commitment;
8. reverifies Manifest/current eligibility, stage identity/inventory and path attachment immediately before commit;
9. installs with `renameat2(RENAME_NOREPLACE)`, verifies final inode and fsyncs the parent;
10. writes a completed commitment and independently reloads evidence and destination bytes.

No overwrite, merge, arbitrary path, callback, dynamic import, network, database, shell or environment-selected delivery mechanism exists.

## Failure and recovery

- Preexisting destination or stage: fail closed; never delete unknown/preexisting state.
- Pre-rename failure: exact owned stage and prepared commitment are removed and verified, or state is `rollback-indeterminate`.
- Parent-fsync failure: exact final directory is moved back and verified before cleanup, or state is indeterminate.
- Post-durable-rename completion failure: state is `completion-pending`; destination bytes exist but no usable verified delivery result is returned.
- `reconcile_pending_controlled_local_delivery` may write only the missing completion commitment after reproducing every exact fact. It never reissues authorization or recopies bytes.
- Replay and concurrent reuse: identity-keyed exclusive consumption permits exactly one winner.

## Evidence

`ControlledLocalDeliveryEvidence` binds issuance evidence/commitment, Release, Manifest, artifact set, source paths, ordered inventory, destination paths/inodes, implementation, authorization, attempt, times, byte totals and typed directed audit links. Persistence verification reproduces canonical evidence and all commitments and rechecks final pathname attachment.

## Lifecycle

Historical delivery verification uses the original bound lifecycle scope and does not rewrite history. `verify_controlled_local_delivery_current_eligibility` separately binds the verified historical delivery to its exact Manifest, then evaluates a separately supplied current lifecycle scope.

## Explicit non-claims

The boundary proves only exact authorization and controlled local placement. It does not prove or authorize:

- internet or network distribution;
- deployment or hosting;
- public availability or reachability;
- reader usability or accessibility;
- successful publication;
- semantic conformance beyond TASK-053;
- Manifest authority beyond TASK-054;
- AtlasForge integration.

## BCRP and multi-artifact boundary

BCRP remains exactly eleven core kinds and imports no delivery module. TASK-054 production remains one artifact. A bounded generic transaction test proves two-artifact exact inventory mechanics without manufacturing Manifest authority or modifying TASK-054.
