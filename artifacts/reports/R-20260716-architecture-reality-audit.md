# Architecture-to-Reality Audit

Date: 2026-07-16T21:17:15+00:00
Project: /home/mkkto/srv/EIP/projects/BriefForge
Mode: generated
Latest previous audit: artifacts/reports/R-20260716-architecture-reality-audit.md
Completed tasks since latest audit: 1

## Scope

This audit checks documented architecture, governance rules, operating procedures, state artifacts, templates, automation, logging/context systems, and available implementation for drift.

## Categories

- architecture_vs_implementation
- state_files_vs_reality
- agent_instructions_vs_behavior
- logging_systems
- context_management_systems
- governance_processes
- automation_workflows
- templates_vs_generated_projects
- subsystem_responsibility_boundaries
- validator_ownership_boundaries

## Drift types

- drift
- obsolete_documentation
- duplicated_systems
- unused_systems
- missing_implementation
- implementation_without_documentation
- documentation_without_implementation

## Blocks

None.

## Warnings

None.

## Remediation workflow

1. Fix blocks before major architecture/governance work continues.
2. Convert durable policy or architecture changes into decision artifacts.
3. Update implementation, templates, docs, and state together so future projects inherit the correction.
4. Refresh affected folder summaries and latest handoff.
5. Rerun `tools/architecture_reality_audit.py`, `tools/check_coherence.py`, and relevant tests.
