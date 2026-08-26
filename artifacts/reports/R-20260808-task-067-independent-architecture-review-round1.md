# TASK-067 Independent Architecture Review — Round 1

Date: 2026-08-08
Disposition: `BLOCKED / NOT RECONCILED`
Task: `TASK-067 — Versioned Terminal Profile and Paired-Table Capability Implementation`

## Review boundary

Two independent read-only reviewers inspected the complete eight-module paired-terminal package, the sole additive selector edit, all six TASK-067 test modules, the synthetic fixture, the frozen TASK-066 decision/specification, and the active TASK-067 artifact. The repository is intentionally non-Git. No Candidate or publication chain was executed.

The focused suite passed 64 tests in both reviews. This was provisional because the required adversarial properties below were not established.

## Blocking and high findings

### B1 — Canonical BCRP extension and real upstream admission are not proven

`build_paired_semantic_extension()` omits the unchanged BCRP extension-envelope fields `authority_ref`, `scope`, `target_refs`, and `character`, and uses the paired contract where the outer required-extension envelope expects the accepted core extension contract. The shared fixture patches both `verify_publication_release` and `verify_renderer_compatibility_plan`, so all downstream tokens originate behind mocked upstream admission. A genuine unpatched Release/Plan path is absent.

Required correction: produce the exact core envelope with the paired contract inside the canonical payload, validate its Candidate binding, and prove token issuance through real unpatched Release and Plan verification.

### B2 — Issued opaque tokens are not sealed against private-state mutation

Weak-set membership proves only that the token object was once issued. `object.__setattr__` can replace `_plan_documents` and `_predecessor_prefix_fingerprint` on an issued token; Manifest predecessor construction then accepts a substituted authority-critical predecessor closure. The nonce is not used to authenticate all token state.

Required correction: retain an issuer-owned immutable/sealed snapshot or fingerprint covering every authority-critical token field and verify it on every token consumption/binding operation. Add independent mutations of every private field.

### B3 — Controlled invocation does not bind admitted directories to opened descriptors

Output and evidence paths are validated and later opened without comparing the opened descriptor's `(st_dev, st_ino)` to the admitted directory object. A rename/replacement between validation and open can redirect writes to an unauthorised real directory.

Required correction: capture and compare directory device/inode before any renderer or write side effect, independently for output and evidence, and add deterministic swap tests.

### H1 — Obligation/provenance N+1 tests are coupled

The 83rd obligation target and 93rd provenance target duplicate identities already in the frontier. Older variants use unresolved targets. Cardinality is therefore not the sole mutation.

Required correction: append an otherwise-valid, resolving, absent identity and assert uniqueness/resolution before testing the exact frontier rejection.

### H2 — Valid row-provenance drift is invisible to renderer and assessor

Row-adjacent renderer and assessor expectations omit authority-critical provenance fields including package identities and target topology. A valid package-identity mutation with a recomputed projection fingerprint produces identical HTML and is approved by conformance.

Required correction: ensure every required row-level provenance field is independently represented and assessed, and add one-field drift mutations proving renderer/assessor cross-detection.

### H3 — The successful public paired selector route is tested only with patched verifiers

Combinatorial tuple rejection is useful, but no real persisted paired Manifest traverses the public selector into the real paired verifier.

Required correction: add one unpatched public-selector success proof and cross-version rejection before verifier entry.

## Non-blocking adequacy findings to close with the correction

- Positively instrument and assert exactly two renderer executions on success and zero executions/writes on prevalidation failures.
- Split artifact, invocation-evidence, and conformance-evidence tamper tests so names match actual coverage.

## Preserved boundaries

Production remains source-neutral. BCRP remains eleven kinds. Historical selector branches are textually preserved except for the authorised additive paired branch. TASK-051 and TASK-066 remain unchanged. TASK-051 is not active. No successor is active.

## Required next gate

Add failing regressions for each finding, apply only the smallest evidence-required corrections, rerun focused/historical/full verification, then obtain a fresh independent PASS against the final files.
