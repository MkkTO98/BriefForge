# Decision: Setup - specialized_agents

Date: 2026-07-01
Status: Accepted
Severity: L2
Section: operating_model
Scope: local project
Owner: project-owned

## Question
Which project-specialized agents seem useful, if any?

## Decision
None approved for initial phase. Consultation may use existing MetaHarvest artifacts, but no new specialized agents should be created.

## Rationale
Captured during project initialization so future humans and agents do not need hidden chat history to understand the setup choice.

## Alternatives considered
- Defer: allowed when the answer is not required for bootstrap.
- Record now: used when the setup answer affects current scaffolding, safety, scope, architecture, or operating behavior.

## Consequences
Agents must consult this artifact before asking the same setup question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/` or a superseding decision artifact.

## Approval boundary
This setup decision does not grant authority for destructive actions, external publication, remote pushes, paid resources, credential/production-data handling, major scope changes, or architecture changes beyond existing project doctrine.
