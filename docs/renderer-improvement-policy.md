# Renderer Improvement Policy

Date: 2026-07-03
Status: Active governance
Owner: BriefForge

## Policy statement

BriefForge Core is feature-frozen except where repeated operational publication evidence demonstrates a renderer-only communication need.

Renderer improvements should be implemented only when all of the following are true:

1. The same reader friction appears repeatedly across different real reports.
2. The proposed improvement does not require runtime, constitutional, Presentation Package, validation, promotion, or Presentation Grammar changes.
3. The proposed improvement demonstrably improves communication rather than adding features.
4. The evidence is recorded in the Renderer Backlog.
5. A separate implementation task explicitly approves the change.

Single observations remain observations. They do not automatically become implementation work.

## Frozen surfaces

The following remain frozen unless contradicted by strong implementation evidence and a separate architecture task:

- `CONSTITUTION.md`;
- runtime model;
- validation lifecycle;
- promotion lifecycle;
- Ready Presentation Package;
- Presentation Grammar;
- renderer-adapter/conformance boundary.

TASK-029 authorizes no changes to these surfaces.

## Default future posture

Default answer to new renderer ideas:

```text
Record evidence first. Do not implement yet.
```

The burden of proof is on the proposed change.

## Evidence threshold

An improvement can be considered for implementation when:

- at least two different real publications show the same friction; or
- one real publication plus a later independent experiment shows the same friction under a materially different report shape; and
- the improvement can be expressed as a renderer-only communication improvement.

Repeated occurrence is necessary but not sufficient. It only makes the issue a candidate.

## Approval gate

Before implementation, create or update a task artifact that states:

- backlog entry ids;
- publications affected;
- exact reader friction;
- proposed renderer-only change;
- non-goals;
- forbidden surfaces preserved;
- measurement plan;
- rollback/rejection criteria.

Do not combine backlog recording and implementation in the same task unless the user explicitly authorizes implementation.

## Communication improvement test

A renderer change is communication-improving only if it makes at least one of these better without weakening auditability:

- reader orientation;
- main-point discovery;
- evidence placement;
- uncertainty/caveat proximity;
- source fidelity;
- comparison clarity;
- quantitative scanability;
- traceability without noise;
- methodology/obligation disclosure;
- long-document navigation.

A change is not justified merely because it:

- looks modern;
- resembles a mature external site;
- adds a new feature;
- makes implementation more interesting;
- anticipates a hypothetical future renderer.

## Explicitly disallowed as default evolution

Future BriefForge work should not drift into:

- browser application architecture;
- dashboards;
- portals;
- JavaScript interaction;
- CSS/framework accumulation;
- visualization engines;
- map/chart systems;
- persistence/API/server architecture;
- renderer registry architecture;
- template systems;
- speculative Communication Intent adoption.

These require separate evidence and approval.

## MetaHarvest relationship

MetaHarvest's Presentation Architecture domain is advisory evidence.

It can suggest communication patterns and evaluation lenses, but it cannot override BriefForge implementation evidence. Mature external systems may inform what to look for; repeated BriefForge publication evidence decides what BriefForge should change.

## Communication Intent policy

Communication Intent status: KEEP EXPERIMENTAL.

Do not adopt it into the renderer or canonical lifecycle. Do not reject it. Future adoption requires repeated operational evidence showing that Communication Intent improves renderer decisions without duplicated renderer assembly and without frozen-surface changes.
