# TASK-006: Validation Policy Identity

Date: 2026-07-02
Status: Complete

## Objective

Track which validation policy produced a Validation Judgment, so a Ready Presentation Package preserves candidate id, semantic fingerprint, and validation policy identity.

## Scope implemented

Implemented only:

- minimal fixed validation policy identity;
- Validation Judgment linkage to policy identity;
- Ready Presentation Package preservation of policy identity;
- downstream read-only exposure of policy identity;
- promotion rejection for absent or blank policy identity.

## Explicit non-scope preserved

No configurable policies, multiple validators, rule engines, renderer adapters, rendering, browser output, templates, serialization, persistence, APIs, visualization, exports, portal behavior, dashboards, search, or maps were implemented.

## Files changed

Implementation:

- `src/briefforge/validation.py`
- `src/briefforge/promotion.py`
- `src/briefforge/downstream.py`
- `src/briefforge/__init__.py`

Tests:

- `tests/test_validation_policy_identity.py`

Documentation / continuity:

- `docs/validation-policy-identity.md`
- `artifacts/tasks/TASK-006-validation-policy-identity.md`
- `state/project_state.md`
- `state/architecture.md`
- `state/active_goal.md`
- `state/recent_changes.md`
- `context/latest_handoff.md`

## RED evidence

Command:

```bash
python3 -m unittest tests.test_validation_policy_identity -v
```

Observed before implementation:

```text
Ran 6 tests in 0.005s
FAILED (errors=5)
```

Expected missing behavior included:

- `ImportError: cannot import name 'CURRENT_VALIDATION_POLICY_ID' from 'briefforge.validation'`
- `AttributeError: 'ReadyPresentationPackage' object has no attribute 'validation_policy_id'`
- `AttributeError: 'DownstreamSemanticPackage' object has no attribute 'validation_policy_id'`
- `TypeError: ValidationJudgment.__init__() got an unexpected keyword argument 'validation_policy_id'`

## GREEN evidence

Command:

```bash
python3 -m unittest tests.test_validation_policy_identity -v
```

Observed after implementation:

```text
Ran 6 tests in 0.001s
OK
```

## Final verification plan

Run after documentation and continuity updates:

```bash
python3 -m unittest tests.test_validation_policy_identity -v
python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests
python3 tools/update_context_summaries.py --project . --max-depth 3
python3 tools/check_coherence.py --project . --json
python3 tools/context_health.py --project . --json
```

## Architectural observations

- Semantic fingerprint proves what substance was validated, not which validation policy accepted it.
- Policy identity is audit metadata, not a rule engine or configurable validation architecture.
- Promotion remains a boundary check and does not re-run validation.
- No contradiction in the frozen constitution was exposed.

## Implementation Readiness Assessment

Validated:

- Validation policy identity exists on Validation Judgment.
- Ready packages preserve policy identity.
- Downstream semantic access exposes immutable policy identity metadata.
- Promotion rejects absent or malformed policy identity.
- Existing validation behavior remains unchanged.

Still unvalidated:

- Policy migration semantics.
- Multiple validation policies.
- Configurable validation architecture.
- Durable Rejected Package representation.
- Renderer-adapter boundary.
