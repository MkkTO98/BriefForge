# Promotion Boundary and Ready Presentation Package

Date: 2026-07-02
Status: Initial production implementation documentation for TASK-003

## Purpose

TASK-003 adds the smallest promotion boundary for BriefForge's runtime lifecycle.

Promotion answers only this question:

> May this already-valid Candidate Presentation Package become Ready?

Promotion does not decide whether the candidate is constitutionally valid. That question belongs to validation.

## Runtime mapping

| Concept | Runtime object or function | Role |
|---|---|---|
| Ready Presentation Package | `ReadyPresentationPackage` | Immutable lifecycle-state record containing the accepted candidate and the matching successful judgment. |
| Promotion rejection | `PromotionRejected` | Exception raised when the readiness boundary is not authorized. |
| Promotion operation | `promote_candidate_presentation_package(candidate, judgment)` | Pure boundary operation from candidate plus successful matching judgment to Ready package. |

## Why Ready Presentation Package is separate from Candidate Presentation Package

A Candidate Presentation Package is package substance before readiness authorization.

A Ready Presentation Package is not different presentation meaning. It is the same candidate substance accepted across a lifecycle boundary by a successful Validation Judgment for that same candidate.

Keeping these objects separate preserves three architectural facts:

1. Candidate construction is not readiness.
2. Validation is diagnosis, not lifecycle transition.
3. Readiness is an explicit boundary state that downstream consumers may later depend on without taking authority over validation.

The Ready record therefore contains only:

- the Candidate Presentation Package; and
- the Validation Judgment that authorized readiness.

It does not contain renderer, browser, template, serialization, persistence, API, visualization, export, portal, delivery, or downstream-consumer fields.

## Why promotion is separate from validation

Validation and promotion have different authority.

Validation asks:

> Is this candidate constitutionally valid?

Promotion asks:

> Given an existing successful judgment, may this candidate cross into readiness?

If validation also promoted, then the validator would become lifecycle authority and the runtime sequence would collapse:

```text
Candidate Presentation Package
-> Validation Judgment
-> Ready Presentation Package or Rejected Package
```

TASK-003 keeps the middle and third steps separate. The promotion operation consumes an already-produced `ValidationJudgment`; it does not run validation internally.

## Boundary rules implemented

Promotion requires:

1. A `CandidatePresentationPackage`.
2. A `ValidationJudgment`.
3. `judgment.valid == True`.
4. `judgment.candidate_package_id` matching `candidate.identity.package_id`.

Promotion rejects:

1. Invalid judgments.
2. Judgments produced for a different candidate.

Promotion does not mutate the candidate. Runtime records are frozen dataclasses, and tests preserve a before/after candidate equality check.

## Architectural assumption TASK-003 validates

TASK-003 validates this assumption from the runtime representation architecture:

> Readiness can be represented as a boundary state authorized by validation without making validation itself the promotion authority.

The implementation supports that assumption. A successful `ValidationJudgment` is necessary but not itself a Ready package. The candidate crosses the readiness boundary only through `promote_candidate_presentation_package`.

## Implementation Readiness Assessment

### 1. Which architectural assumptions have now been validated?

- A Ready Presentation Package can be represented without renderer, delivery, template, serialization, persistence, API, visualization, export, portal, or downstream-consumer concerns.
- Promotion can be a separate operation from validation.
- Promotion can depend on a successful existing Validation Judgment without re-running validation.
- Promotion can reject invalid judgments.
- Promotion can reject a successful judgment for a different candidate.
- Readiness can preserve the original Candidate Presentation Package without mutation.

### 2. What remains architecturally unvalidated?

- Whether a distinct Rejected Package representation is necessary or whether `PromotionRejected` plus `ValidationJudgment` is sufficient.
- Whether Ready packages need validation-rule identity, rule-version identity, or timestamp-like provenance before downstream use.
- Whether semantic immutability should later be backed by stronger package fingerprints rather than package identity alone.
- How downstream consumers should receive Ready packages without acquiring BriefForge authority.
- Whether future package versioning should be represented before rendering or export work begins.

### 3. What is the smallest next implementation step?

The next implementation step should still avoid rendering. The smallest reasonable next investigation is a rejected-readiness or downstream-consumption-boundary slice:

- either prove whether rejected packages need a first-class representation; or
- prove a downstream boundary can consume only Ready packages without introducing renderer, browser, export, API, persistence, template, visualization, portal, or delivery behavior.

The second option is more useful only if downstream consumption can be represented without accidentally building a renderer or API surface.

### 4. Did implementation expose any contradiction in the frozen constitution?

No constitutional contradiction was exposed.

The implementation revealed one architectural pressure: matching a judgment to a candidate required `ValidationJudgment` to carry the candidate package identity. This is not a constitutional change. It is minimal audit metadata needed to prevent a valid judgment for one package from authorizing a different package.

A future architecture task may decide whether package identity is sufficient or whether a stronger semantic fingerprint is required before real downstream consumption.

## Explicit non-scope

TASK-003 does not implement:

- rendering;
- HTML;
- browser output;
- templates;
- serialization;
- persistence;
- APIs;
- visualization;
- exports;
- downstream consumers;
- portal behavior;
- validation-rule frameworks;
- repair or mutation of candidate packages.
