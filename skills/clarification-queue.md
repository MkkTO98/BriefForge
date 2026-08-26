# Skill: Clarification Queue

When the agent needs human input, create a JSON question file in `question_queue/pending/`.

## Required fields
- id
- timestamp
- severity
- project
- question
- options
- recommended_default
- consequence_if_unanswered
- related_files

L3 and L4 questions must pause execution.
