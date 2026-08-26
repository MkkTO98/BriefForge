# Renderer Backlog Specification

Date: 2026-07-03
Status: Active operational governance
Owner: BriefForge

## Purpose

The Renderer Backlog is the evidence ledger for future BriefForge renderer evolution.

It records recurring reader friction discovered while publishing real analytical reports. It is not a feature wishlist and not an implementation queue. Its function is to prevent speculative renderer work by requiring repeated operational evidence before implementation.

## Scope

In scope:
- reader friction discovered during real BriefForge publications;
- human review observations tied to a concrete publication artifact;
- repeated issues across different reports;
- renderer-only improvement candidates that preserve the frozen constitution, runtime, validation lifecycle, promotion lifecycle, Ready Presentation Package, and Presentation Grammar.

Out of scope:
- runtime changes;
- constitutional changes;
- Presentation Package or Presentation Grammar changes;
- browser applications;
- dashboards or portals;
- visualization engines;
- templates or component frameworks;
- speculative improvements not tied to real publications.

## Backlog location

The active ledger is:

`artifacts/renderer_backlog.md`

Task-specific publication evidence may live under:

`artifacts/presentations/<task-or-publication-id>/reader_evaluation.md`

The backlog should reference evidence, not duplicate every review detail.

## Required entry fields

Each backlog entry must contain:

| Field | Meaning |
| --- | --- |
| Identifier | Stable id using `RB-###`. |
| Title | Short reader-friction title. |
| First observed publication | First concrete BriefForge publication where the friction appeared. |
| Subsequent occurrences | Other concrete publications where the same friction recurred. |
| Category | Renderer readability, traceability, source structure, obligation disclosure, long-document navigation, quantitative/table display, uncertainty communication, or other explicit category. |
| Severity | Low, Medium, High, or Critical. Severity reflects reader harm, not implementation desirability. |
| Evidence | Paths and specific observations from reader evaluations or comparison reports. |
| Proposed renderer improvement | Communication-level improvement, stated without prescribing implementation details unless already proven safe. |
| Implementation status | Observation, Candidate, Approved, Implemented, Rejected, or Superseded. |
| Boundary assessment | Whether the improvement appears renderer-only and whether it threatens frozen surfaces. |
| Threshold status | Below threshold, Meets recurrence threshold, or Approved by separate implementation task. |

## Status definitions

Observation:
- friction has been observed but is not implementation work.

Candidate:
- friction has recurred across different reports and appears renderer-only.

Approved:
- a separate task explicitly approves implementation after evidence review.

Implemented:
- implementation completed and verification linked.

Rejected:
- evidence or implementation trial showed the improvement is not worth doing.

Superseded:
- the entry was absorbed into a better-scoped backlog entry or policy.

## Severity definitions

Low:
- minor reading annoyance; does not materially block comprehension.

Medium:
- repeated friction that slows reading or weakens professional presentation.

High:
- repeated friction that materially harms comprehension, trust, or audit usability.

Critical:
- recurring friction that causes serious misreading, loss of source fidelity, or governance failure. Critical issues may trigger emergency review, but still must preserve constitutional boundaries unless strong evidence justifies a separate architecture task.

## Recurrence rule

A single observation remains an observation.

An entry may move from Observation to Candidate only when the same reader friction appears in at least two different real publications or one publication plus a later independent renderer experiment that exercises a materially different report shape.

The recurrence evidence must be publication evidence, not imagined future demand.

## Evidence quality rule

Acceptable evidence:
- reader evaluation files;
- cross-publication comparison files;
- rendered artifact conformance reports;
- task reports;
- human review notes attached to a concrete publication;
- screenshots or captures if future workflows create them.

Weak evidence:
- abstract preference;
- isolated design taste;
- a single attractive external example;
- unverified assumptions about future users.

Weak evidence can inform research, but not implementation approval.

## Update procedure

After each real BriefForge publication:

1. Review the rendered output as a human reader.
2. Record reader friction in the publication's `reader_evaluation.md` or equivalent review artifact.
3. Compare new friction against existing `RB-###` entries.
4. Add the publication to `Subsequent occurrences` if it is the same friction.
5. Create a new `Observation` entry only when no existing entry fits.
6. Reassess severity and threshold status.
7. Do not implement renderer changes during backlog update.

## Promotion to implementation

Moving from Candidate to Approved requires a separate implementation task that cites:
- affected backlog entries;
- recurrence evidence;
- why the improvement is renderer-only;
- why no runtime, constitution, Presentation Package, validation, promotion, or Presentation Grammar change is required;
- how communication improvement will be measured after implementation.

## Anti-patterns

Do not:
- convert every reader complaint into work;
- add abstractions before repeated publication pressure exists;
- use MetaHarvest communication patterns as automatic implementation authority;
- treat visual polish desire as permission for CSS/framework/template architecture;
- solve table, map, chart, navigation, dashboard, or portal needs speculatively.
