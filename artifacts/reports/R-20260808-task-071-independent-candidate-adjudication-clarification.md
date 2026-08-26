# R-20260808 — TASK-071 Independent Candidate Adjudication Field Clarification

Status: **PASS — reporting clarification only**

The immutable adjudication JSON at `artifacts/reports/R-20260808-task-071-independent-candidate-adjudication.json` remains unchanged.

Two field meanings are clarified after independent post-attempt review:

1. `technical_layers: ["L0", "L1", "L2"]` reports the BCRP technical-validation result returned by `validate_bundle(..., through_layer="L2")`. It is not the complete governed validator layer list. Immutable `validation-evidence-04.json` authoritatively records the full governed execution as `L0`, `L1`, `L2`, and `PAIRED-SEMANTIC`, with zero findings and `passed: true`.
2. `canonical_candidate_semantic_roundtrip: true` means the staged profile was canonically loaded and the Candidate-semantic domain bytes were then reproduced exactly from that reloaded profile. Candidate-semantic domain bytes are not themselves used as the canonical profile-loading format.

These clarifications do not modify Candidate bytes, authority, stage inventory, receipt, validation evidence, ledger, terminal state, fingerprint, acceptance, or attempt accounting.
