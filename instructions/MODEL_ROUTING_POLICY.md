# Model Routing Policy

Agents should not always use the largest model.

Default principle:
Use the smallest sufficient local model, escalate only when the task requires stronger reasoning, larger context, or repeated failures show local models are insufficient.

Routing considers:
- Agent role.
- Task type.
- Complexity.
- Context length.
- Hardware availability.
- Failure count.
- Project policy.

Codex/OpenAI is a supervisory escalation layer, not the default worker.
