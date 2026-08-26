# Constitutional Presentation Validation

Date: 2026-07-02
Status: Initial production implementation documentation for TASK-002

## Purpose

TASK-002 adds the smallest constitutional validator for a Candidate Presentation Package.

The validator answers only this question:

> Does this Candidate Presentation Package satisfy the currently implemented constitutional requirements well enough to receive a Validation Judgment?

It does not make the package Ready. It does not render, serialize, persist, export, network, visualize, template, or serve anything.

## Runtime mapping

| Concept | Runtime object or function | Role |
|---|---|---|
| Validation Judgment | `ValidationJudgment` | Immutable result containing `valid`, judged `candidate_package_id`, and constitutional `findings`. |
| Constitutional finding | `ValidationFinding` | Immutable finding with constitutional concept, reason, and code. |
| Constitutional validation operation | `validate_candidate_presentation_package(candidate)` | Pure function from Candidate Presentation Package to Validation Judgment. |

## Why validation is separate from promotion

Validation and promotion answer different questions.

Validation asks whether a Candidate Presentation Package satisfies constitutional requirements. Promotion would create or authorize a different lifecycle state, such as a Ready Presentation Package.

Keeping them separate preserves the runtime architecture:

```text
Candidate Presentation Package
-> Validation Judgment
-> Ready Presentation Package or Rejected Package
```

TASK-002 implements only the middle object and operation. It deliberately does not implement Ready Presentation Package or promotion because those are distinct architectural acts with different authority and downstream implications.

## Why validation is a pure operation

Validation is pure because it must not change what it evaluates.

A validator that mutates a Candidate Presentation Package would blur diagnosis and repair. It would become unclear whether the judgment describes the original candidate or a corrected candidate. Pure validation preserves auditability, makes RED/GREEN tests reliable, and keeps future promotion decisions independent from repair mechanics.

In implementation terms, `validate_candidate_presentation_package(candidate)` returns a new `ValidationJudgment` and does not mutate the candidate.

## Constitutional assumptions now validated by implementation

The current validator checks only minimal constitutional requirements:

1. Package Identity is present and has bounded self-identification fields.
2. Organizing Purpose is present and has its binding fields.
3. At least one Presentation Statement exists.
4. Each statement has target-independent Encounter Semantics.
5. Statement encounter relationships point only to known statements.
6. Statement upstream-reference dependencies point only to known Upstream References.
7. Statements depending on upstream references have attached Presentation Obligations.
8. Statement obligation attachments point only to known Presentation Obligations.
9. Obligations have category and requirement text.
10. Obligation attachment targets point only to known statements or upstream references.

These checks are constitutional, not delivery-specific. They do not verify upstream truth, analytical correctness, renderer quality, visual form, browser behavior, template suitability, serialization shape, persistence, API behavior, or downstream consumption.

## Implementation Readiness Assessment

### 1. Which architectural assumptions have now been validated?

- A Candidate Presentation Package can be evaluated without rendering technology.
- Validation can be represented as a separate runtime object rather than a package mutation.
- Constitutional findings can be communicated without creating Ready packages or downstream consumers.
- Reference and obligation attachment can be checked locally from runtime package substance.
- The current runtime records are sufficient for a first constitutional validation pass.

### 2. What remains architecturally unvalidated?

- Rejected Package representation, if needed.
- Downstream consumption boundary behavior.
- Whether obligation categories should be restricted to the seven irreducible constitutional categories.
- Whether validation findings need severity levels, warning classes, or stable diagnostic taxonomy beyond minimal failure reasons.
- Whether package versions, compatibility, or validation-rule identity must be represented before readiness.
- Whether future validation should check analytical-boundary violations in text content or only structural relationships.

### 3. What is the smallest next implementation step?

The smallest next step is not general rendering. It is a narrow promotion-boundary task:

- Given a Candidate Presentation Package and a successful Validation Judgment, represent the transition boundary without mutating the candidate.
- Prove that invalid judgments cannot authorize promotion.
- Still exclude renderers, HTML, browser output, templates, serialization, persistence, APIs, visualization, exports, networking, and downstream consumers.

### 4. Did implementation expose any constitutional weakness?

No constitutional weakness was exposed.

The main implementation pressure is diagnostic specificity: the frozen constitution defines obligations semantically, but TASK-002 intentionally validates only minimal structural attachment. A later architecture decision may need to decide whether obligation categories should be enumerated and whether text-level boundary violations should be validated. That is not a constitutional contradiction; it is an implementation-depth question.
