# Model Routing


Use `models/registry.yaml`, `models/routing.yaml`, and `models/selection_policy.yaml` before selecting a model.

Rules:
- Do not default to the largest model.
- Use the smallest sufficient local model.
- Escalate to Codex/OpenAI only for repeated failure, architecture review, security-sensitive design, or high-value supervisory checkpoints.
- If available local models are unknown, ask an L2 clarification or run the hardware/model detection task if available.

