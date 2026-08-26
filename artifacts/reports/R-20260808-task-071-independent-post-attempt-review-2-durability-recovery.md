# R-20260808 — TASK-071 Independent Post-Attempt Review 2: Durability and Recovery

Status: **PASS**
Mode: strictly read-only static inspection; no coordinator, constructor, recovery, test, script, command, or mutation.

## Findings

- Authority SHA-256 is `9870ff3aca5630de86a97de815415b9d183782e7255a0340640b47e9a226fe04` and binds exact task/campaign/attempt/input/source/profile/validator/predecessor/paths.
- Staged output is exactly five files, with no surplus:
  - `profile.json`: 181126 bytes, SHA-256 `62cbe5294b123c9b4043e9f721a1b2585c70a5380e2121a39e8558b5c73b1898`;
  - `candidate-semantic.json`: 181128 bytes, SHA-256 `b1c29473241648c68dfb7bb737715645b396c149094eeb70cef34feb52fb95b2`;
  - `fingerprint.json`: 477 bytes, SHA-256 `34976737eb19ea11903f79f37bbac2f3ab3d242677894862ee079b1cd3158cf1`;
  - `inventory.json`: SHA-256 `c5032937785592c2327ad3b5dc70089f8ac4ee0769c741cd77d6bac3d00a4302`;
  - `authoring-receipt.json`: SHA-256 `51d2c7712915aa98011fa93a03a3429a4ae90b4b3f3f8911c467280351c4b798`.
- Immutable state SHA-256 chain is `286ccc1e… → 4c7fd9b6… → 29bf6f5e… → 2a707ea1… → 59683876…`; every prior digest and authority binding agrees.
- `04-VALIDATED_ACCEPTED.json` and `terminal.seal.json` are exact dual terminal evidence.
- Recovery statically authenticates terminal evidence and never calls the builder. Independent adjudication records recovery performed, construction not repeated, and exactly one consumption.

The author/recovery APIs intentionally emit the same terminal receipt bytes. `R-20260808-task-071-recovery-route-attestation.md` supplies route provenance without changing immutable evidence.

Disposition: PASS. Whole-directory staging, inventory, receipt, state chain, validation evidence, terminal evidence, and recovery behavior are exact.
