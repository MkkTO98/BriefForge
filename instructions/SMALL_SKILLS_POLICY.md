# Small Skills Policy

This project prefers small composable skills.

Good skill size:
- one workflow
- one tool family
- one decision pattern
- one failure mode

Avoid broad monolithic playbooks unless a project domain is complex enough to justify them. Large playbooks rot faster and are harder for agents to apply precisely.

## Loading behavior

Skills are optional procedural references, not universal startup context. Agents should load or read a skill only when the current task matches its trigger, when a file explicitly references it, or when a prior attempt shows the procedure is needed. Do not inject every project skill into every agent/session by default. Keep agent files focused on role, responsibility, and retrieval rules; keep procedures in skills and load them on demand.
