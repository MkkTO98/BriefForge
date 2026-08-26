# D-20260716 BCRP Canonicalization, Equality, Extension, and Versioning

Date: 2026-07-16
Status: accepted
Task: TASK-044

## Decision

BCRP 1.0 accepts deterministic semantic canonicalization above transport bytes. It preserves semantically ordered collections and sorts unordered collections by stable kind/scope/identity/version keys; rejects duplicate identities and duplicate canonical edges; normalizes Unicode to NFC, line endings to LF, timestamps to explicit UTC, integers mathematically, and exact decimals to coefficient/scale; preserves units and every explicit state; and excludes transport locators, comments, reverse indexes, derivative manifests, renderer mechanics, and explicitly non-semantic display metadata from Candidate semantic fingerprints.

Four equality domains remain distinct: semantic equality, profile-instance equality, artifact byte equality, and presentation equivalence. Fingerprints name their domain and canonicalization/algorithm. Equal fingerprints never establish truth, authority, analytical validity, governance approval, or presentation equivalence.

Extensions use owner/version/scope/criticality/semantic-character/validation/preservation envelopes. Unknown required semantic extensions reject. Unknown optional semantic extensions proceed only when losslessly preserved and irrelevant to the attempted operation. Unknown required presentation meaning fails renderer compatibility. Optional display-only content may be ignored only when explicitly non-semantic and discardable. Extensions cannot override core meaning or introduce DSB-007 financial semantics.

ADPM semantic version and BCRP version remain independent. BCRP patch, minor and major changes follow the rules in the profile specification; changes to canonicalization, required structure, identity, core states, or equality are major and require a migration specification.

## Rationale

A deterministic graph-level canonical form is required before transport bytes can be canonicalized safely. Equality and fingerprint scopes must remain narrower than semantic authority and rendered meaning. Fail-closed extension behavior prevents silent semantic loss while permitting bounded forward preservation.

## Alternatives considered

- byte-first canonicalization — rejected; no transport is accepted yet;
- binary floating values — rejected for exact semantic material;
- whitespace-collapsed prose — rejected because authored text may carry meaning;
- unknown-field ignore — rejected for semantic content;
- one version axis — rejected because semantic, profile, transport, renderer, artifact and manifest responsibilities have different owners.

## Consequences

- A later transport must map canonical BCRP forms one-to-one and deterministically.
- No authoritative fingerprint is emitted when canonicalization prerequisites fail.
- Old minor-version readers must preserve unknown optional semantic content or reject.
- No migration code or serialization is authorized here.
