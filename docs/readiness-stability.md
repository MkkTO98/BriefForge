# Readiness Stability and Semantic Fingerprint

Status: TASK-005 complete.

## Purpose

TASK-005 proves that a Ready Presentation Package corresponds to the exact Candidate Presentation Package substance that was validated.

The runtime lifecycle is now:

```text
Candidate Presentation Package
-> Validation Judgment linked to candidate id and semantic fingerprint
-> Ready Presentation Package preserving the accepted fingerprint
-> Downstream Semantic Boundary exposing the fingerprint as read-only metadata
```

## Why package id alone is insufficient

Package id proves only that a judgment names the same bounded package identity. It does not prove that the candidate's semantic substance is still the same substance that was validated.

A candidate can retain the same package id while changing:

- organizing purpose;
- presentation statement encounter meaning;
- target-independent encounter semantics;
- upstream-owned reference attachments;
- presentation obligations;
- scope/non-scope fields.

Without semantic fingerprint linkage, promotion could accidentally accept a stale judgment for a same-id but semantically changed candidate. That would break readiness stability and downstream trust without requiring any renderer, storage, or API bug.

## What the fingerprint represents

`semantic_fingerprint(candidate)` hashes the Candidate Presentation Package runtime record's semantic substance:

- package identity;
- organizing purpose;
- presentation statements;
- target-independent encounter semantics;
- upstream-owned references;
- presentation obligations.

The fingerprint is deterministic over the current in-memory semantic record. It is readiness-stability metadata, not architectural authority.

## What the fingerprint does not represent

The fingerprint does not include, depend on, or create ownership of:

- rendering state;
- browser state;
- HTML;
- templates;
- file paths;
- serialization format;
- persistence location;
- API state;
- UI state;
- portal behavior;
- dashboard behavior;
- visualization output;
- exports.

## Lifecycle behavior

Validation now produces a `ValidationJudgment` linked to both:

1. `candidate_package_id`; and
2. `candidate_semantic_fingerprint`.

Promotion succeeds only when:

1. the judgment is valid;
2. the judgment candidate id matches the candidate's current id; and
3. the judgment fingerprint matches the candidate's current semantic fingerprint.

A same-id candidate whose semantic substance changes after validation is rejected at promotion.

A `ReadyPresentationPackage` preserves the accepted fingerprint from the judgment. The downstream boundary exposes that fingerprint through `DownstreamSemanticPackage.semantic_fingerprint` without granting mutation authority.

## Why this is not persistence identity

The semantic fingerprint is not a storage key, URL, file name, database id, cache key, API resource id, or serialization checksum.

It answers one readiness question only:

> Is the candidate substance being promoted the same semantic substance that was validated?

Future persistence systems may choose their own identifiers and storage formats. If they later use this fingerprint, that would be a separate architectural decision. TASK-005 does not make BriefForge a persistence owner.

## Why this does not introduce serialization ownership

The implementation uses deterministic in-memory canonicalization only to compute a hash. That implementation detail does not create a public serialization format, interchange format, document format, storage layout, export format, or API contract.

The canonical object remains the semantic Presentation Package, not a JSON document. The fingerprint is metadata derived from the semantic runtime record for readiness stability.

## Constitutional contradiction assessment

No contradiction in the frozen constitution was exposed.

The change strengthens an already stated runtime principle: a Ready Presentation Package must be semantically stable relative to the validation judgment that accepted it. The fingerprint does not add rendering, browser, API, storage, template, visualization, portal, dashboard, search, or map ownership.

It also does not shift upstream economic or analytical meaning into BriefForge. Upstream references remain upstream-owned; the fingerprint only proves attachment and presentation-local substance did not change between validation and promotion.

## Implementation Readiness Assessment

Validated by TASK-005:

- Validation judgments are linked to candidate identity and semantic fingerprint.
- Promotion succeeds when both candidate identity and semantic fingerprint match the judgment.
- Promotion rejects a same-id candidate whose semantic substance changed after validation.
- Ready Presentation Packages preserve the accepted fingerprint.
- Downstream semantic access exposes the accepted fingerprint as read-only metadata.
- The fingerprint surface remains free of delivery, rendering, browser, template, HTML, API, persistence, file-path, UI, visualization, export, portal, dashboard, search, and map ownership.

Still unvalidated:

- Validation-rule or policy identity.
- Durable Rejected Package representation.
- Renderer-adapter boundary.
- Real downstream consumer behavior.
- Persistence behavior, if ever approved.

Recommended next architectural investigation:

- Investigate validation-rule / policy identity if future changes make it important to know which validation rule set accepted a package.
- Otherwise, investigate a renderer-adapter boundary without implementing rendering.
