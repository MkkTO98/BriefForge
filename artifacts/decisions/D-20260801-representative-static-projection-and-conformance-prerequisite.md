# D-20260801 — Representative Static Projection and Conformance Prerequisite

Date: 2026-08-01
Status: accepted
Task: TASK-059

## Decision

Recommend exactly one unactivated next workstream:

`TASK-060 — Representative Static-HTML Projection and Semantic-Conformance Capability`

Select Alternative C as an exact prerequisite to any representative pilot. Do not activate TASK-060 during TASK-059.

## Hard repository fact

A representative pilot cannot currently succeed through accepted TASK-053–056 operations.

The accepted conformance profile requires exactly one observation statement, no more than 140 characters, and no multiline or structured-text semantic fields. The controlled projection also omits structured values, units, exhibits, relation semantics and all section titles except the first.

TASK-059’s representative standard requires multiple sections/claims, explicit qualifications, structured quantitative content, provenance and coherent hierarchy. Collapsing such material into one short observation would falsify or omit source meaning. A pilot that requires full preservation is therefore predetermined to block.

## Exact next capability

TASK-060 may implement only the smallest fixed non-browser extension of the existing static-HTML projection and semantic-conformance profile needed to represent and verify:

1. bounded multiple sections with exact title, parent/order and statement membership;
2. bounded multiple statements with posture, authority, references and encounter order;
3. exact structured quantitative values with unit, semantic type and source/value linkage;
4. one bounded static table expression for those values;
5. explicit qualification/uncertainty attachment to target claims;
6. complete provenance and obligation requirements rather than kind-only reduction;
7. deterministic standalone HTML in the existing one-output media type;
8. exact artifact conformance against every admitted projected element.

The capability must use the existing BCRP kinds, Release/Plan/invocation/conformance boundaries and fixed renderer identity/versioning discipline. It may introduce the necessary new capability/profile/implementation versions but no new authority kind.

## Scope limits

TASK-060 must not:

- author or publish the T-039 brief;
- modify any sibling project;
- create a generic external adapter or native BCRP lifecycle;
- change Release, Manifest, delivery or TASK-056 authority semantics;
- add browser work, JavaScript, interaction, a second output format or public deployment;
- claim visual quality, accessibility, reader success or production readiness;
- perform broad renderer refactoring or visual redesign;
- add arbitrary chart behavior; the only quantitative expression is one fixed static table class.

## Why this precedes authoring improvement

Low-level parallel legacy/BCRP authoring is real friction, but accepted operations can construct the required evidence. The projection/conformance restriction is a deterministic impossibility, not merely burden. Remove the hard semantic-output blocker first; measure authoring burden in the subsequent representative pilot rather than generalizing an orchestration layer now.

## Why not run a failure-only pilot

A bounded preflight would merely rediscover known source constraints. It would not change the decision and would create another governance artifact without user-visible capability. The exact prerequisite is already evidenced and BriefForge-owned.

## Why not pause

Pause was evaluated genuinely. A concrete external candidate exists and the missing capability directly concerns BriefForge’s presentation mission. The correction is bounded, independently testable, reusable across representative briefs and lower-risk than a generic adapter or broader renderer redesign. It has higher expected value than waiting.

## Alternatives compared

| Alternative | Information/value | Cost/risk | Decision |
|---|---|---|---|
| A representative pilot now | Low new information; success impossible under TASK-053 | High manual effort; predetermined block | Reject |
| B authoring/composition | Removes burden but not semantic-output impossibility | Medium; abstraction risk before pilot evidence | Defer |
| C exact projection/conformance prerequisite | Removes known mission-critical hard block | Medium, bounded and reversible | Select |
| D cross-project contract | Manual sovereign intake already works | High generalization/sovereignty risk | Reject |
| E lifecycle hardening | No demonstrated operational defect | High governance-without-use risk | Reject |
| F pause | Zero cost but leaves a bounded mission-owned hard gap | Reversible but lower current value | Reject now |

## TASK-060 success boundary

TASK-060 succeeds only if newly constructed representative BCRP evidence proves exact deterministic projection and static-HTML conformance for every listed semantic class, while all existing TASK-052–056 authority and isolation invariants remain intact.

It must not execute a real external pilot. If the fixed renderer cannot support the bounded capability without broad redesign or authority inflation, TASK-060 must block and recommend pause rather than expand scope.

## Consequences

- TASK-059 assessment result: `RECONCILED`.
- Project disposition: `ONE NEXT WORKSTREAM RECOMMENDED — UNACTIVATED`.
- TASK-056 remains authoritative.
- TASK-057/058 remain historically unchanged; browser work remains stopped.
- No implementation authority is granted until TASK-060 is explicitly activated.
