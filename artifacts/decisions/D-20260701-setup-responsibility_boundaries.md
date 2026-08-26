# Decision: Setup - responsibility_boundaries

Date: 2026-07-01
Status: Accepted
Severity: L2
Section: identity
Scope: local project
Owner: project-owned

## Question
What responsibilities, external systems, or neighboring projects should this project explicitly not own?

## Decision
BriefForge must not own MacroForge ingestion/canonical data, InsightForge analytical conclusions, MetaHarvest reusable architectural knowledge, ProjectForge scaffolding/governance doctrine, EIP root governance, future portal navigation/routing, or investment/domain judgment. It may consume structured, reviewed outputs from owning projects through explicit contracts once those contracts are designed and approved.

## Rationale
Captured during project initialization so future humans and agents do not need hidden chat history to understand the setup choice.

## Alternatives considered
- Defer: allowed when the answer is not required for bootstrap.
- Record now: used when the setup answer affects current scaffolding, safety, scope, architecture, or operating behavior.

## Consequences
Agents must consult this artifact before asking the same setup question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/` or a superseding decision artifact.

## Approval boundary
This setup decision does not grant authority for destructive actions, external publication, remote pushes, paid resources, credential/production-data handling, major scope changes, or architecture changes beyond existing project doctrine.
