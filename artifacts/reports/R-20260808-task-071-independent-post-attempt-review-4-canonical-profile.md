# R-20260808 — TASK-071 Independent Post-Attempt Review 4: Canonical Candidate Profile

Status: **PASS**
Mode: strictly read-only static inspection; no coordinator, constructor, recovery, test, script, command, or mutation.

## Findings

- Exact physical canonical record order is Candidate, Material, Brief, sorted by `(record_kind, identity)`, not authored role order.
- Exact record identities are `candidate:task071-cross-inquiry`, `material:task071-t039`, and `brief:task071-cross-inquiry`.
- Only outer lifecycle identities and Candidate references/extension target changed; frozen internal semantic identities, sections, statements, order, rows, values, qualifications, provenance, obligations, sources, and authorities remain exact.
- Profile canonical bytes round-trip exactly. Candidate-semantic bytes reproduce exactly from the reloaded profile.
- Fingerprint domain is `candidate-semantic`, rooted at the new Candidate, and includes canonical Brief/Material dependencies while excluding derivative lifecycle/renderer/artifact/Manifest records.
- Profile contains exactly three Candidate-stage records. Candidate alone has exactly one paired semantic extension; Brief and Material have none.
- No Judgment, Ready, Release, Plan, token, projection, rendering, conformance, Manifest, or artifact-audit record exists.
- No missing, duplicate, surplus, or undeclared profile content exists; reconciliation is 109/109 treatments and 7/7 rows.

Minor reporting clarification: adjudication field `technical_layers` reports the BCRP technical subset L0/L1/L2; immutable validation evidence separately and authoritatively reports paired semantic as the fourth executed layer. `canonical_candidate_semantic_roundtrip` means exact candidate-semantic reproduction after canonical profile reload, not direct candidate-domain loading. See the adjudication clarification report.

Disposition: PASS. Canonical serialization, identity lineage, fingerprint scope, and Candidate-stage boundaries are exact.
