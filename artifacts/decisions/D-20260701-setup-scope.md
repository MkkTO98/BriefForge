# Decision: Setup - scope

Date: 2026-07-01
Status: Accepted
Severity: L2
Section: identity
Scope: local project
Owner: project-owned

## Question
What work is explicitly in scope for v1?

## Decision
Initial scope is constitutional architecture only: mission, owned and excluded responsibilities, interfaces to MacroForge, InsightForge, MetaHarvest, ProjectForge, and future portals, input/output boundaries, data/rendering/presentation ownership, browser-first versus document-first alternatives, HTML canonical target assessment, component/template/presentation primitive philosophy, candidate report archetypes, risks, tradeoffs, and open evidence questions.

## Rationale
Captured during project initialization so future humans and agents do not need hidden chat history to understand the setup choice.

## Alternatives considered
- Defer: allowed when the answer is not required for bootstrap.
- Record now: used when the setup answer affects current scaffolding, safety, scope, architecture, or operating behavior.

## Consequences
Agents must consult this artifact before asking the same setup question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/` or a superseding decision artifact.

## Approval boundary
This setup decision does not grant authority for destructive actions, external publication, remote pushes, paid resources, credential/production-data handling, major scope changes, or architecture changes beyond existing project doctrine.
