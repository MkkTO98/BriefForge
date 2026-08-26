# Presentation Package Builder

Date: 2026-07-02
Status: Implemented as TASK-015 authoring convenience

## Purpose

`PresentationPackageBuilder` is a narrow authoring helper for constructing the existing `CandidatePresentationPackage` runtime dataclasses.

It exists because TASK-014 showed that the architecture can carry a realistic economic presentation, but manual package construction is verbose and mechanically error-prone.

## What it is

The builder is a fluent convenience interface over existing runtime records:

- `PackageIdentity`
- `OrganizingPurpose`
- `PresentationStatement`
- `EncounterSemantics`
- `UpstreamReference`
- `PresentationObligation`
- `CandidatePresentationPackage`

It returns exactly a `CandidatePresentationPackage` from `build()`.

## What it is not

The builder is not:

- a new semantic model;
- a validator replacement;
- a promotion boundary;
- a renderer boundary;
- a template system;
- a component system;
- a serialization layer;
- an API;
- persistence;
- an AI-generation interface;
- InsightForge integration;
- browser/report/dashboard/portal infrastructure.

## Required-field behavior

The builder rejects missing or blank required fields before producing a candidate package.

It requires:

- package identity fields;
- organizing purpose fields;
- at least one statement;
- required statement and encounter-semantics fields;
- required upstream-reference fields when a reference is added;
- required obligation fields when an obligation is added.

Optional tuple fields remain empty tuples when omitted. The builder does not invent semantic defaults.

## Constitutional posture

The builder introduces no new constitutional concept because it does not alter the canonical object. The canonical object remains the structured semantic Presentation Package represented by `CandidatePresentationPackage`.

The builder is upstream of constitutional validation. Its output still must pass the existing validation, promotion, renderer-adapter, rendering, and conformance workflow.

## TASK-014 migration result

The Denmark Country Profile from TASK-014 was recreated using only the builder.

Result:

- the builder-produced candidate equals the manually constructed TASK-014 candidate;
- semantic fingerprint remains `90d4651099df06afcaf1f531c887b03ae551475096dfa3ad163c44db04c089ff`;
- the existing workflow continues unchanged through validation, promotion, renderer invocation, HTML rendering, and rendered artifact conformance.

## Authoring impact

The builder materially reduces mechanical authoring pressure:

- authors no longer manually nest dataclass constructors;
- encounter semantics are supplied inline with each statement;
- optional tuples can be omitted safely;
- required fields fail early with explicit builder errors.

Remaining pressure:

- authors still need to choose stable ids;
- relationships remain hand-maintained;
- obligations/references are still authored manually;
- the builder does not solve obligation visibility in rendered output.

## Implementation Readiness Assessment

GREEN for the first authoring capability.

The builder is safe to keep because it improves package authoring without changing BriefForge's runtime model or constitutional boundaries.

Recommended next slice remains bounded:

- obligation/reference visibility in downstream HTML, or
- relationship-id ergonomics evidence, if repeated authoring shows id maintenance dominates remaining friction.
