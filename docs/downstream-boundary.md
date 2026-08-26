# Downstream Consumption Boundary

Date: 2026-07-02
Status: Initial production implementation documentation for TASK-004

## Purpose

TASK-004 adds the smallest downstream-consumption boundary proof for BriefForge's runtime lifecycle.

The boundary answers only this question:

> May this already-ready Presentation Package be exposed for downstream semantic consumption?

It does not render, serialize, persist, export, network, visualize, template, search, map, route, dashboard, or serve anything.

## Runtime mapping

| Concept | Runtime object or function | Role |
|---|---|---|
| Downstream-consumable semantic package | `DownstreamSemanticPackage` | Immutable access wrapper around a Ready Presentation Package. |
| Downstream boundary rejection | `DownstreamBoundaryRejected` | Exception raised when a non-ready object attempts to cross the boundary. |
| Downstream boundary operation | `prepare_downstream_semantic_package(ready_package)` | Pure boundary operation accepting only Ready Presentation Packages. |

## Why downstream consumers are not semantic authorities

BriefForge owns presentation meaning. Downstream systems may encounter or use that meaning, but they do not become authorities over it.

A downstream consumer therefore receives access to:

- package identity;
- organizing purpose;
- statements;
- upstream references;
- obligations;
- validation judgment.

It does not receive authority to alter those semantics. `DownstreamSemanticPackage` is an immutable wrapper around the Ready package and exposes package substance as read-only properties. The underlying runtime records are frozen dataclasses, so tests prove downstream code cannot rewrite identity, purpose, statements, references, obligations, or the validation judgment through this boundary.

## Why only Ready Presentation Packages may cross the boundary

Candidate packages are pre-readiness. They may be incomplete, invalid, unvalidated, or not yet lifecycle-authorized. Allowing candidates to cross the downstream boundary would let downstream systems consume pre-readiness presentation meaning and would weaken the lifecycle sequence:

```text
Candidate Presentation Package
-> Validation Judgment
-> Ready Presentation Package
-> Downstream Consumption Boundary
```

TASK-004 therefore accepts only `ReadyPresentationPackage`. Candidate packages, invalid judgments, and failed promotion objects are rejected.

## Why Candidate Packages remain internal / pre-readiness

A Candidate Presentation Package is the object being evaluated and promoted. It is not yet downstream-consumable. Keeping candidates internal prevents downstream systems from:

1. treating unvalidated package substance as ready;
2. bypassing validation;
3. bypassing promotion;
4. acquiring implicit semantic authority by consuming a pre-readiness object.

## Rejected Package representation decision

TASK-004 did not require a first-class Rejected Package.

The tests demonstrated that `ValidationJudgment + PromotionRejected` is sufficient for this slice:

- invalid judgments cannot promote a candidate;
- failed promotion does not produce a Ready package;
- the downstream boundary rejects both invalid judgments and failed-promotion exception objects because neither is a `ReadyPresentationPackage`.

If later workflow needs a durable rejected state for audit, repair, or queueing, that should be documented as separate architectural evidence before implementation. No such pressure appeared here.

## Implementation Readiness Assessment

### 1. Which architectural assumptions have now been validated?

- Downstream consumption can be represented without rendering or delivery technology.
- Only Ready Presentation Packages need to cross the downstream boundary.
- Candidate packages can remain internal/pre-readiness.
- Downstream systems can receive semantic access without becoming semantic authorities.
- The boundary can reject invalid judgments, failed promotions, and candidates without requiring a Rejected Package.
- The boundary does not mutate Ready packages.

### 2. What remains architecturally unvalidated?

- Whether downstream consumption needs semantic fingerprints before real consumers exist.
- Whether validation-rule identity or policy identity should travel with Ready packages before external consumption.
- Whether a durable Rejected Package is needed for repair workflows.
- How actual renderers, exporters, portals, or APIs would consume this boundary without taking semantic authority.
- Whether access properties are sufficient for all downstream classes or whether a capability-limited interface is needed.

### 3. What is the smallest next implementation step?

Do not implement rendering yet by default.

The next minimal architectural step should be one of:

1. semantic fingerprint / readiness-stability proof, if candidate-to-judgment identity is considered too weak for downstream use; or
2. renderer-adapter boundary investigation, if and only if the next approved task needs to prove how a future renderer consumes semantic packages without owning presentation meaning.

The first option is safer because it strengthens the semantic boundary without introducing delivery technology.

### 4. Did implementation expose any contradiction in the frozen constitution?

No contradiction was exposed.

The frozen constitution says BriefForge owns presentation meaning and excludes delivery meaning. TASK-004 supports that: downstream packages expose semantic package substance while excluding renderer, browser, HTML, template, serialization, persistence, API, visualization, export, portal, dashboard, search, and map ownership.

## Explicit non-scope

TASK-004 does not implement:

- rendering;
- HTML;
- browser output;
- templates;
- serialization;
- persistence;
- APIs;
- visualization;
- exports;
- downstream consumer implementations;
- portal behavior;
- dashboard behavior;
- search;
- maps;
- Rejected Package representation;
- semantic fingerprinting;
- mutation or repair behavior.
