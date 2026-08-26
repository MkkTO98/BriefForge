# Skill: Structured Setup Coverage

Use this when deciding what to ask before rendering or revising local project structure.

## Principle
The setup questionnaire is a coverage map, not a rigid interview script. Hermes should ask the smallest useful set of questions, reuse known context, explain tradeoffs when helpful, and record unknowns explicitly.

## Workflow
1. Read `config/setup_questionnaire.yaml` for topic coverage and `config/sufficiency_policy.yaml` for stop/pause rules.
2. Ask one focused topic at a time only when it changes architecture, safety, dependencies, scope, cost, or the first milestone.
3. Infer low-risk defaults and label them as assumptions.
4. Record accepted answers and deferred nonblocking items under `artifacts/decisions/`.
5. Use `tools/new_project.py --answers-json ...` to render the scaffold once operationally sufficient.

## Do not
- Do not paste every setup question at the user.
- Do not silently skip must-pause topics.
- Do not keep setup decisions only in chat.
