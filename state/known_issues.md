# Known Issues

Project: BriefForge
Updated: 2026-08-25T02:34:44+02:00

## TASK-082 upstream blocker

- Admitted TASK-229/T-042 evidence does not authenticate issuer-native statement hierarchy: no presentation arcs, role URIs, parent-child IDs, preferred labels, calculation weights, issuer order, abstract headings, or subtotal spans.
- TASK-082 is therefore bound as `PARTIAL`; its qualified peer-row sections must not be represented as issuer presentation hierarchy.

## Wider test-suite observation

- Final full `python3 -W error -m unittest discover -s tests -v` ran 794 tests and exited 1 with 2 failures and 31 errors in TASK-070/TASK-077 artifact-state and fixture-authority tests.
- The failure identities are outside the bounded TASK-082 implementation. No authenticated clean pre-task baseline is available for the intentionally non-Git BriefForge tree, so inherited-versus-new repository-wide failure identity remains unproven.
- The bounded TASK-079 through TASK-082 suite passed 40/40; TASK-082 source verification, replay, browser, print, focus, and final binding gates passed.
- Do not repair the wider failures under TASK-082 authority.
