# Work Execution Methodology

Artifact role: methodology guidance for how implementation work should be approached.

This file defines how work is performed. It does not define project identity, context loading, governance record lifecycles, validation policy, test strategy, or deterministic validators.

## Core posture

Prefer the smallest useful implementation that advances the current objective while preserving future optionality.

Architecture should evolve through implementation evidence, not speculation. Repeated implementation pain is stronger evidence than repeated code. Generalize only when doing so measurably reduces future maintenance or removes recurring friction already observed in real work.

Avoid:

- speculative abstraction;
- framework-first development;
- broad redesign during local implementation tasks;
- automatic task generation from ideas or recommendations;
- adding process machinery when a concise file-backed note is enough.

## Bounded implementation slice

When work is non-trivial, frame it as a bounded implementation slice before editing broadly.

A slice should contain, where appropriate:

- objective: the concrete outcome this slice should produce;
- expected architectural uncertainty: what might be learned or disproven;
- explicit non-goals: what this slice must not attempt;
- implementation boundary: files, interfaces, systems, or behaviors expected to change;
- readiness: required context, decisions, permissions, or prerequisites before starting;
- success criteria: what would make the slice useful;
- verification expectations: what kind of checks should be run, without defining project-wide validation policy;
- expected evidence: what observations would justify accepting, rejecting, deferring, or expanding the approach;
- post-slice decision: keep, revise, revert, defer, or propose an architecture/governance decision.

Use a lighter version for small changes. Do not create bureaucracy merely to satisfy the template.

## Implementation restraint

During a local implementation task:

1. Preserve the existing architecture unless the slice exposes a direct contradiction or repeated pain.
2. Prefer targeted changes over subsystem rewrites.
3. Keep new abstractions private until at least two real uses justify making them general.
4. Do not redesign neighboring systems just because you noticed possible improvements.
5. Do not convert advisory recommendations into tasks without a human or accepted local decision.
6. If the slice starts requiring unrelated changes, stop and record the boundary issue instead of silently expanding scope.

## Evidence-gated architectural evolution

Architecture may evolve when implementation evidence shows one or more of:

- the current design repeatedly blocks bounded implementation;
- the same coordination problem recurs across slices;
- repeated implementation pain is caused by the architecture rather than by a one-off bug;
- a small abstraction would measurably reduce future maintenance;
- the current design contradicts the project identity, accepted decisions, or observed reality.

Architecture should not evolve merely because:

- a cleaner abstraction is imaginable;
- a framework exists;
- a future use case might appear;
- a broad redesign feels more elegant than a targeted fix;
- similar-looking code appears once or twice without recurring maintenance pain.

When architectural evolution appears justified, keep the implementation slice bounded and use governance artifacts to record the proposed or accepted architecture decision.

For project-wide reusable capabilities, add an ownership-and-evidence review before generalizing: identify the exact owner, who maintains the capability, whether it is minimum autonomy or optional convenience, whether it has emerged in more than one real use, whether it reduces architectural attention, and whether it belongs in identity, architecture, templates, optional features, runtime, local implementation, or nowhere. If ownership or evidence is unclear, keep the capability local and bounded instead of promoting it.

## Post-implementation review posture

After a slice, ask:

- Did the slice meet its objective?
- Which non-goals were preserved?
- What implementation pain appeared?
- Is the pain one-off, recurring, or architecture-caused?
- Should the result be kept, revised, reverted, deferred, or escalated to a decision/report?

This review posture informs future work. It is not a mandatory approval ceremony and does not define validation policy.
