# Specialized Agent Policy

Default agents should handle most work. Specialized agents are generated only after a request is presented to the user.

Request must include:
- short reason
- evidence: repeated failure, recurring task category, or clear setup requirement
- expected benefit
- permissions required
- proposed scope and stop conditions

After approval, the project may add the agent locally. The user should not have to hand-write the agent.
