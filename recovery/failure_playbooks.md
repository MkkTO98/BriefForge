# Failure Playbooks

## Repeated test failure

Trigger:
- same test suite fails three times
- same error category appears twice
- agent changes unrelated files while trying to fix the error

Required response:
1. Stop editing.
2. Re-read exact failing output.
3. Classify failure: syntax, import/path, dependency, logic, fixture, environment, contract, flaky.
4. Inspect only directly relevant files.
5. Produce a short failure report.
6. Apply one minimal fix or escalate according to `recovery/escalation_policy.yaml`.

Forbidden:
- deleting tests
- broad refactors to pass one failure
- changing public contracts without decision artifact
- retrying the same fix

## Permission blocked

Trigger:
- command classified as review/dangerous/forbidden
- agent needs unavailable permission

Required response:
1. Create a pending question with severity L3 or L4.
2. Include exact command, reason, risk, and safer alternatives.
3. Pause execution unless policy permits dry-run only.

## Unclear requirement

Trigger:
- task requires policy not present in state or decisions
- two existing decisions conflict

Required response:
1. Search `artifacts/decisions/` first.
2. If unresolved, create deferred specification question.
3. If nonblocking, continue with conservative default and mark assumption.
4. If blocking, pause.

## Dependency install failure

Trigger:
- package install fails
- package manager unavailable
- version conflict

Required response:
1. Do not repeatedly reinstall.
2. Record package, command, output, and environment.
3. Try one minimal correction.
4. Escalate to stronger model after second failure.

## Model low confidence

Trigger:
- agent self-reports low confidence
- output contradicts state/decisions
- repeated failed validation

Required response:
1. Route to reviewer.
2. If unresolved, route to stronger local model.
3. If unresolved, route to Codex/premium model.
4. Human only if specification or permission is required.
