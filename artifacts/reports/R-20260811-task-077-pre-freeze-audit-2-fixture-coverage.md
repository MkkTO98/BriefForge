# TASK-077 Pre-Freeze Audit 2 — Frozen Invalid-Fixture Production Coverage

Status: **FAIL — REMEDIATION BASELINE**
Date: 2026-08-11
Subject: pre-remediation TASK-077 production/test bytes recorded in `R-20260811-task-077-pre-remediation-path-manifest.json`

## Exact accounting

- Frozen invalid fixtures executed by TASK-076 validator: 63/63 rejected.
- Frozen invalid fixtures directly executed through TASK-077 production tests: 0/63.
- Fixture-semantic classification against existing TASK-077 tests:
  - 22 decisive production rejection tests;
  - 22 analogous-only tests;
  - 13 missing production tests;
  - 6 frozen structural fixtures accepted by the standalone closure verifier.
- Finding-code semantic classification:
  - 18/37 decisively exercised;
  - 9/37 analogous only;
  - 10/37 not decisively exercised.

## Ten finding semantics lacking decisive production evidence

- `counterpart-proof-nontraversable`
- `duplicate-core-identity`
- `duplicate-paired-identity`
- `foreign-registry-identity`
- `mapping-inventory-mismatch`
- `missing-requirement-outcome`
- `registry-digest-mismatch`
- `requirement-inventory-mismatch`
- `source-row-population-mismatch`
- `substituted-paired-decoding`

## Frozen structural-fixture probe

Accepted incorrectly by the standalone production closure verifier:

- `plan-v2-predecessor-closure-unreachable-extra`
- `plan-v2-predecessor-closure-altered-fingerprint`
- `plan-v2-predecessor-closure-8-minimal-record-reclosure`
- `plan-v2-predecessor-closure-8-foreign-record-reclosure`
- `plan-v2-predecessor-closure-10-minimal-record-reclosure`
- `plan-v2-predecessor-closure-10-foreign-record-reclosure`

Rejected structurally:

- substituted kind;
- non-Plan root;
- altered topology;
- altered order.

The frozen wrapper’s `fingerprint` and `refs` claims were not production inputs. Complete records were therefore able to authenticate themselves through kind/order/topology resemblance.

## Minimum decisive matrices identified

1. Every frozen structural closure fixture through an independently bound production closure authority.
2. Recomputed persisted-Plan mutation matrix, including missing/surplus outcomes, correlated inventory reclosure, semantic shadows, and every foreign predecessor commitment.
3. Authenticated Candidate/interpreter substitution matrix for duplicate identities, equal-length decoded substitutions, source-row substitutions, unknown semantics, and cardinality mismatch.
4. Governed registry and correlated-envelope matrix against the fixed manifest boundary.

## Ruling

Analogous coverage is not acceptance evidence. Freeze remains blocked until 63/63 direct production-path outcomes and the separate 36-attack closure matrix pass.