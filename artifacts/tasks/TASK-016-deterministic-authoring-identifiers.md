# TASK-016: Deterministic Authoring and Stable Identifier Generation

Date: 2026-07-02
Status: Complete

## Objective

Implement deterministic identifier generation for Presentation Package authoring while preserving the frozen BriefForge constitution.

The goal is reproducibility: equivalent semantic packages authored independently through the builder should receive identical generated identifiers where constitutionally appropriate.

## Scope implemented

Implemented in `PresentationPackageBuilder` only:

- deterministic package id generation when `package_id` is omitted;
- deterministic statement id generation when `statement_id` is omitted;
- deterministic upstream reference id generation when `reference_id` is omitted;
- deterministic obligation id generation when `obligation_id` is omitted;
- explicit id preservation for package, statement, reference, and obligation ids;
- localized statement-id churn when statement-local semantic content changes.

## Scope explicitly excluded

No changes were made to:

- `CandidatePresentationPackage`;
- validation;
- promotion;
- `ReadyPresentationPackage`;
- downstream boundary;
- renderer boundaries;
- HTML renderer;
- conformance;
- serialization.

Not introduced:

- databases;
- persistence;
- APIs;
- templates;
- browser applications;
- AI generation;
- InsightForge integration;
- registry allocation;
- relationship runtime objects;
- symbolic relationship handles.

## Files changed

Source:

- `src/briefforge/builder.py`

Tests:

- `tests/test_deterministic_authoring_identifiers.py`

Docs/state:

- `docs/deterministic-authoring-identifiers.md`
- `artifacts/tasks/TASK-016-deterministic-authoring-identifiers.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `state/recent_changes.md`
- `context/latest_handoff.md`

## RED evidence

Targeted RED command:

```bash
python3 -m unittest tests.test_deterministic_authoring_identifiers -v
```

Result before implementation:

```text
Ran 7 tests
FAILED (errors=5)
TypeError: PresentationPackageBuilder.add_upstream_reference() missing 1 required keyword-only argument: 'reference_id'
```

This proved the builder did not yet support omitted ids/generation while explicit-id TASK-014 behavior still passed.

## GREEN evidence

Targeted GREEN command:

```bash
python3 -m unittest tests.test_deterministic_authoring_identifiers -v
```

Result after implementation:

```text
Ran 7 tests in 0.021s
OK
```

TASK-014 regression:

```bash
python3 -m unittest tests.test_real_presentation_end_to_end -v
```

Result:

```text
Ran 2 tests in 0.019s
OK
```

TASK-015 regression:

```bash
python3 -m unittest tests.test_presentation_package_builder -v
```

Result:

```text
Ran 6 tests in 0.023s
OK
```

Full unit discovery:

```bash
python3 -m unittest discover -s tests -v
```

Result:

```text
Ran 85 tests in 0.014s
OK
```

Compile check:

```bash
python3 -m compileall -q src tests
```

Result: passed with no output.

## Required proof coverage

1. Equivalent packages generate identical identifiers.
   - Covered by `test_equivalent_packages_generate_identical_identifiers`.

2. Explicit identifiers override generated identifiers.
   - Covered by `test_explicit_identifiers_override_generated_identifiers`.

3. Changing a statement changes only that statement's generated identifier.
   - Covered by `test_changing_statement_changes_only_that_statement_generated_identifier`.

4. Unchanged references retain identifiers.
   - Covered by `test_unchanged_references_retain_generated_identifiers`.

5. Unchanged obligations retain identifiers.
   - Covered by `test_unchanged_obligations_retain_generated_identifiers`.

6. Existing semantic fingerprints remain stable when semantics are unchanged.
   - Covered by `test_semantic_fingerprints_remain_stable_when_generated_semantics_are_unchanged`.

7. TASK-014 end-to-end workflow remains unchanged.
   - Covered by `test_task_014_end_to_end_workflow_remains_unchanged_with_explicit_ids` and TASK-014 regression.

## Deterministic strategy

Generated ids use:

```text
<prefix>-<first 12 hex chars of sha256(canonical semantic payload)>
```

Canonical payloads are JSON encoded with sorted keys and compact separators.

Prefixes:

- `pkg-`
- `stmt-`
- `ref-`
- `obl-`

Explicit ids are never replaced.

## Relationship-id interpretation

BriefForge has no separate relationship runtime object. Relationships are existing id tuples on runtime records.

TASK-016 therefore generates deterministic ids for objects that relationship tuples can reference, but does not introduce relationship objects, handles, aliases, registries, or symbolic resolution.

This preserves the frozen runtime model.

## Interaction with semantic fingerprints

Generated ids are normal fields on the existing candidate package. They are therefore part of the existing semantic fingerprint surface.

Equivalent generated packages produce identical fingerprints because their generated ids are deterministic.

TASK-014 explicit ids remain unchanged, preserving the known fingerprint:

```text
90d4651099df06afcaf1f531c887b03ae551475096dfa3ad163c44db04c089ff
```

## Architectural observations

Deterministic authoring is still builder-side authoring convenience, not a runtime abstraction:

- it returns existing `CandidatePresentationPackage` objects;
- it introduces no new dataclasses;
- it introduces no validation/promotion/rendering/conformance behavior;
- it uses no persistence, database, API, registry, or serialization boundary;
- it respects explicit ids for existing packages and hand-authored relationship surfaces.

## Did deterministic authoring remove identifier-management burden?

Partially and significantly.

Removed/reduced:

- routine manual naming for package, statement, reference, and obligation ids;
- independent-author reproducibility concerns;
- avoidable id churn for unchanged references and obligations;
- avoidable id churn for unchanged statements.

Remaining:

- authors must still decide semantic relationships;
- authors still need explicit ids when they want human-readable handles;
- authors still need explicit ids when relationship tuples must point to ids before a generated build result is inspected;
- larger package authoring may still need relationship ergonomics, but that would be a separate evidence-backed task.

## Implementation Readiness Assessment

GREEN.

The deterministic identifier behavior is safe to keep because it is confined to the builder, respects explicit authoring choices, supports reproducible package construction, and leaves the frozen runtime architecture unchanged.

Recommended next capability if approved:

- relationship authoring ergonomics evidence, if generated-id workflows still make cross-statement relationships awkward; or
- obligation/reference visibility in downstream HTML if human-readable audit obligations remain the dominant pressure.
