# Validation Policy Identity

Status: TASK-006 complete.

## Purpose

TASK-006 tracks which validation policy produced a Validation Judgment.

A Ready Presentation Package now knows:

- which candidate was validated;
- what semantic substance was validated;
- under which validation policy identity it was accepted.

## Why semantic fingerprint alone is insufficient for auditability

The semantic fingerprint proves that the candidate substance being promoted is the same semantic substance that validation judged.

It does not prove which validation policy judged that substance. If validation obligations evolve later, two judgments could refer to the same candidate id and same semantic fingerprint while being produced under different validation policies.

Policy identity therefore answers a separate audit question:

> Which constitutional validation policy accepted this candidate substance?

## What was implemented

The implementation adds one fixed metadata identity:

- `CURRENT_VALIDATION_POLICY_ID = "briefforge-constitutional-validation-policy:v1"`

Validation produces `ValidationJudgment.validation_policy_id`.

Promotion rejects a judgment whose required policy identity is absent or blank, then preserves the accepted identity on `ReadyPresentationPackage.validation_policy_id`.

Downstream semantic access exposes `DownstreamSemanticPackage.validation_policy_id` as read-only metadata.

## Why this is not a rule engine

The policy identity is a label for the currently implemented constitutional validation behavior. It does not select rules, evaluate dynamic rule definitions, load policy files, order rule sets, or interpret policy logic.

Validation behavior remains the same pure validator from prior tasks.

## Why this does not introduce configurable validation architecture

TASK-006 intentionally does not add:

- configurable policies;
- multiple validators;
- rule engines;
- plugin loading;
- policy registries;
- migration machinery;
- runtime policy selection;
- policy serialization or persistence.

The fixed policy id is audit metadata only. Future configurable validation, if ever needed, requires a separate architecture decision and implementation task.

## Constitutional contradiction assessment

No contradiction in the frozen constitution was exposed.

Validation policy identity strengthens Presentation Validation Obligations by preserving audit context for the judgment. It does not add delivery ownership, upstream economic/analytical ownership, renderer ownership, storage ownership, API ownership, template ownership, visualization ownership, or portal/dashboard/search/map behavior.

## Implementation Readiness Assessment

Validated:

- Validation Judgments include validation policy identity.
- Ready Presentation Packages preserve validation policy identity.
- Downstream semantic access exposes policy identity as read-only metadata.
- Promotion rejects absent or malformed policy identity.
- Existing validation behavior remains unchanged.

Still unvalidated:

- Policy migration semantics.
- Multiple validation policies.
- Configurable validation architecture.
- Durable Rejected Package representation.
- Renderer-adapter boundary.
- Real downstream consumer behavior.

Recommended next architectural investigation:

- Durable Rejected Package representation if failed validation/promotion outcomes need first-class audit handling.
- Otherwise, renderer-adapter boundary investigation without implementing rendering.
