# Deterministic Authoring Identifiers

Date: 2026-07-02
Status: Implemented as TASK-016 builder-side authoring behavior

## Purpose

TASK-015 reduced manual package construction pressure, but stable identifier choice remained a source of authoring friction and avoidable churn.

TASK-016 adds deterministic identifier generation to `PresentationPackageBuilder` only.

The objective is reproducibility: equivalent semantic builder inputs should produce identical generated identifiers without requiring a registry, database, persistence layer, API, or runtime model change.

## Strategy

Identifiers are generated only when the author omits the corresponding id.

Explicit identifiers remain authoritative and are preserved unchanged.

Generated ids use:

```text
<prefix>-<first 12 hex chars of sha256(canonical semantic payload)>
```

Prefixes:

- `pkg-` for package identity ids;
- `stmt-` for statement ids;
- `ref-` for upstream reference ids;
- `obl-` for obligation ids.

The hash input is JSON with sorted keys and compact separators. It is local and deterministic.

## Stability guarantees

Equivalent builder inputs generate identical ids.

Unchanged references retain generated reference ids when unrelated statements change.

Unchanged obligations retain generated obligation ids when unrelated statements change.

Changing a statement's own semantic content changes that statement's generated id without changing unchanged statement, reference, or obligation ids.

Explicit ids override generation and preserve existing TASK-014/TASK-015 behavior.

## Churn minimization

Statement ids are generated from statement-local semantic fields:

- encounter meaning;
- belongs-to-purpose text;
- encounter mode;
- encounter description.

Statement relationship tuples are not included in statement-id generation. This minimizes churn when relationship attachments change but the statement's own meaning remains stable.

Reference ids are generated from source-ownership fields:

- owning project;
- reference kind;
- locator;
- owned meaning.

Obligation ids are generated from obligation fields:

- category;
- requirement;
- applies-to tuple.

## Relationship identifiers

BriefForge currently has no separate relationship runtime object. Relationship surfaces are tuples of statement/reference/obligation ids on existing runtime records.

TASK-016 therefore does not introduce relationship-id records or symbolic relationship handles. It preserves explicit relationship tuples exactly and generates identifiers for the objects that relationships can point to when those object ids are omitted.

This avoids introducing a new semantic concept.

## Interaction with semantic fingerprints

Generated ids become fields on the existing `CandidatePresentationPackage`, so they are part of the existing semantic fingerprint surface.

This is intentional: the canonical runtime object remains unchanged, and reproducible authoring ensures equivalent generated packages produce stable fingerprints.

TASK-014 continues to use explicit ids, so its semantic fingerprint remains unchanged:

```text
90d4651099df06afcaf1f531c887b03ae551475096dfa3ad163c44db04c089ff
```

## Remaining manual authoring pressure

Reduced:

- stable id naming;
- id churn from independent equivalent authoring;
- manual reference id naming;
- manual obligation id naming;
- manual package id naming when desired.

Remaining:

- authors still choose presentation substance;
- authors still choose which objects relate;
- authors still need explicit ids when they want stable human-readable handles or when relationships must refer to specific generated objects before build;
- relationship authoring remains manual because there is no separate relationship object in the frozen runtime model.

## Implementation Readiness Assessment

GREEN.

Deterministic id generation is safe to keep because it is confined to the builder, produces existing runtime objects, respects explicit ids, avoids persistence/registry allocation, and does not alter validation, promotion, readiness, renderer boundaries, HTML rendering, or conformance.
