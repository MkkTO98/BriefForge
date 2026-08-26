# Report: BriefForge Constitutional Methodology Recommendation for ProjectForge

Date: 2026-07-01
Type: methodology-recommendation
Status: Recommendation Only
Owner: BriefForge
Scope: evaluate whether BriefForge's constitutional process should become reusable ProjectForge methodology

## 1. Scope

This report evaluates the constitutional process used for BriefForge as a possible reusable ProjectForge methodology.

This report does not modify ProjectForge.

It creates recommendations only.

## 2. Process evaluated

BriefForge used this sequence:

```text
Instantiation
-> Constitution Proposal
-> Architectural Review
-> Architectural Revision
-> Adversarial Review
-> Canonical Object Discovery
-> Expressiveness Proof
-> Constitution Freeze
-> Implementation Constitution
-> Implementation
```

## 3. Overall recommendation

Recommendation:

> ProjectForge should eventually support this as an optional high-uncertainty constitutional track, not as the default lifecycle for every generated project.

Reason:

The process was valuable because BriefForge had high architectural uncertainty, strong boundary risks, sibling-project coupling risks, and major future implementation gravity.

For simpler projects, requiring the full process would create governance overhead and delay execution without proportional benefit.

## 4. Universally applicable stages

These stages are broadly applicable to ProjectForge-managed projects:

### 4.1 Instantiation

Universally applicable.

Every project needs a scaffold, identity artifact, state files, context policy, and basic verification.

### 4.2 Constitution Proposal

Universally applicable in lightweight form.

Every project should define mission, scope, non-scope, authority boundaries, and success criteria before implementation.

### 4.3 Architectural Review

Universally applicable, but scale should vary.

Every project benefits from at least a boundary and feasibility review. Large or uncertain projects need deeper review.

### 4.4 Architectural Revision

Universally applicable when review finds material issues.

If review passes cleanly, revision can be folded into the proposal.

### 4.5 Constitution Freeze

Universally applicable in concept.

Before implementation begins, the project should know which constitutional assumptions are stable and what kind of evidence is required to change them.

### 4.6 Implementation Constitution

Universally applicable for projects with meaningful architecture-to-implementation risk.

For trivial projects, this can be a short section in the freeze decision. For complex projects, it should be a separate report.

## 5. Optional stages

These stages should be optional, triggered by uncertainty or risk:

### 5.1 Adversarial Review

Optional but recommended when:

- the project may not deserve independent existence;
- responsibilities could belong to sibling projects;
- scope creep risk is high;
- deleting or merging the project is plausible.

Not required for simple self-contained tools.

### 5.2 Canonical Object Discovery

Optional but recommended when:

- project independence depends on owning a distinct artifact;
- the project could otherwise become an abstract capability or service;
- implementation might start before the core owned object is clear.

Not required when the owned artifact is obvious.

### 5.3 Expressiveness Proof

Optional but recommended when:

- the canonical object must remain stable for many future use cases;
- future implementation targets are unknown;
- freezing too narrow a concept would cause later constitutional churn;
- the project has broad domain classes to support.

Not required for narrow, single-purpose projects.

### 5.4 Final Semantic Investigation

Optional and rare.

Recommended only when a single term or concept is known to control lifetime stability.

Not useful as a ritual stage.

## 6. Stages dependent on maturity or architectural uncertainty

### 6.1 High architectural uncertainty

Use the full track:

```text
Instantiation
-> Constitution Proposal
-> Architectural Review
-> Architectural Revision
-> Adversarial Review
-> Canonical Object Discovery
-> Expressiveness Proof
-> Constitution Freeze
-> Implementation Constitution
-> Implementation
```

Suitable for projects that define new platform capabilities, cross-project boundaries, or long-lived contracts.

### 6.2 Medium architectural uncertainty

Use a shortened track:

```text
Instantiation
-> Constitution Proposal
-> Architectural Review
-> Architectural Revision if needed
-> Constitution Freeze
-> Implementation Constitution or freeze-section mapping
-> Implementation
```

Suitable for projects with known ownership but non-trivial implementation consequences.

### 6.3 Low architectural uncertainty

Use a minimal track:

```text
Instantiation
-> Lightweight Constitution
-> Readiness Review
-> Implementation
```

Suitable for small utilities, narrow scripts, or projects with obvious boundaries.

## 7. Trigger criteria for the full constitutional track

ProjectForge should consider recommending the full track when at least two of the following are true:

1. The project might be merged into an existing project.
2. The project owns a long-lived contract or canonical artifact.
3. The project interfaces with multiple sibling projects.
4. The project has high scope-creep gravity.
5. Future implementation targets are unknown.
6. A wrong constitution would cause expensive later migration.
7. The project's name or domain invites misleading responsibilities.
8. External architectural evidence materially affects the design.
9. Implementation convenience is likely to distort responsibility boundaries.

## 8. Anti-patterns to avoid if ProjectForge adopts this

1. Do not force every project through the full process.
2. Do not let adversarial review become performative criticism.
3. Do not create implementation tasks during constitutional phases.
4. Do not confuse expressiveness proof with feature planning.
5. Do not treat implementation convenience as constitutional evidence.
6. Do not let semantic investigations become naming bikesheds.
7. Do not make ProjectForge the authority over generated-project architecture after instantiation.

## 9. Recommended ProjectForge artifact model

If ProjectForge later adopts this methodology, it should treat the following as candidate artifact types:

- Constitution Proposal.
- Architectural Review.
- Architectural Revision.
- Adversarial Review.
- Canonical Object Discovery.
- Expressiveness Proof.
- Constitution Freeze.
- Implementation Constitution.

These should be available as optional templates or guidance, not mandatory scaffolding for every project.

## 10. Final recommendation

BriefForge's process should become a reusable ProjectForge methodology only as a risk-scaled constitutional track.

The universal principle is:

> Freeze the constitution before implementation when project identity, ownership boundaries, or canonical objects are uncertain.

The full BriefForge sequence should be reserved for projects whose long-term architectural cost of getting the constitution wrong is materially higher than the governance cost of the process.
