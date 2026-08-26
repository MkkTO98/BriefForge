# Skill: Command Permissions

Use `permissions/allowlist.yaml`, `permissions/denylist.yaml`, and `permissions/escalation_rules.yaml`.

## Rules
- Read-only commands usually fit `safe`.
- Project-local file modifications usually fit `review`.
- Dependency installation, networking, service changes, git push, and destructive operations fit `dangerous`.
- Forbidden patterns stop execution.

When in doubt, escalate rather than inventing permission.
