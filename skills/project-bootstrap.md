# Skill: Project Bootstrap

Use this when creating or revising this project's local scaffold.

## Procedure
1. Let Hermes lead an adaptive setup conversation. Do not dump a full questionnaire.
2. Treat `config/setup_questionnaire.yaml` as a coverage map for topics that should be resolved, inferred, or explicitly deferred.
3. Stop asking once `config/sufficiency_policy.yaml` says bootstrap is operationally sufficient and no must-pause item is unresolved.
4. Save accepted and deferred answers as file-backed artifacts.
5. Generate the scaffold noninteractively with `tools/new_project.py --answers-json ...`.
6. Run generated-project coherence and any template-specific smoke checks.

## Required outputs
- Project path.
- Accepted decisions.
- Deferred decisions and why they are nonblocking.
- Verification commands and real output.

## Safety
Secrets, production access, billing risk, destructive operations, and command-policy uncertainty are must-pause topics unless the operator explicitly allows a deferred bootstrap.
