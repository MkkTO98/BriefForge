# Decision: Setup - users

Date: 2026-07-01
Status: Accepted
Severity: L2
Section: identity
Scope: local project
Owner: project-owned

## Question
Who uses this project: only you, agents, public users, clients, or another group?

## Decision
Primary users are Mikkel and Hermes agents operating the EIP. Future downstream consumers may include EIP portal/navigation systems and user-facing intelligence surfaces, but no public users or production consumers are in scope during the architecture-first phase.

## Rationale
Captured during project initialization so future humans and agents do not need hidden chat history to understand the setup choice.

## Alternatives considered
- Defer: allowed when the answer is not required for bootstrap.
- Record now: used when the setup answer affects current scaffolding, safety, scope, architecture, or operating behavior.

## Consequences
Agents must consult this artifact before asking the same setup question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/` or a superseding decision artifact.

## Approval boundary
This setup decision does not grant authority for destructive actions, external publication, remote pushes, paid resources, credential/production-data handling, major scope changes, or architecture changes beyond existing project doctrine.
