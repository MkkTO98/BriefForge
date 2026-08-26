# Autonomy Levels

## Conservative
Agents inspect, propose, and ask often. Good for fragile or high-stakes projects.

## Balanced
Agents may modify project-local files, run tests, prepare commits, and ask when architecture, secrets, external systems, or destructive operations are involved.

## Aggressive
Agents may run longer loops, repair failures, prepare commits, and continue through L1/L2 ambiguity. L3/L4 still pause.

## Project-local Default
Balanced-to-aggressive:
- Balanced for permissions.
- Aggressive for local iteration and testing.
- Blocking escalation for L3/L4.
