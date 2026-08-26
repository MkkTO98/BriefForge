# D-20260801 — TASK-060 Exact Bounds and Cardinalities

Date: 2026-08-01
Status: accepted, implemented and verified
Task: TASK-060

## Decision

| Element | Minimum | Maximum | Positive proof |
|---|---:|---:|---:|
| sections | 2 | 8 | 3 |
| hierarchy depth | 2 | 2 | 2 |
| statements total | 2 | 32 | 4 |
| statements per leaf | 1 | 16 | 2 |
| statement-targeted qualifications | 1 | 16 | 2 |
| paired quantitative cases | 1 | 16 | 7 |
| table rows | 2 | 32 | 14 |
| fixed table columns | 5 | 5 | 5 |
| tables | 1 | 1 | 1 |
| sources/provenance/snapshots/units/types | 1 each | 16 each | 1 each |
| obligations | 1 | 16 | 1 |
| content authorities | 1 | 8 | 1 |
| operational pipeline authorities | 5 | 5 | 5 |
| total Material authorities | 6 | 13 | 6 |
| requirement and Plan mappings | 7 | 7 | 7 |
| output artifacts | 1 | 1 | 1 |

Operational validation compatibility, Release, invocation, conformance and Manifest authorities remain in the immutable Material authority inventory because existing executable policies require them there. Capability-declaration and planning authorizations remain outside Material. The five Material pipeline authorities are exactly classified and conformance-accounted as audit-only with planned/realized HTML cardinality zero. Only the separately derived 1–8 content authorities are included in displayed projection cardinality.

Every case has exactly two authored slots. Table rows therefore equal twice the admitted case count. Every qualification has one statement target. Object definitions and directed edges have separate exact cardinality accounting.

## Resource bounds

- verified content closure: 2,000,000 bytes;
- HTML artifact: 1,000,000 bytes and never above the smaller authorization limit;
- identity: 200 UTF-8 bytes under existing syntax;
- title/label/designation: 200 UTF-8 bytes;
- other admitted semantic text: 4,096 UTF-8 bytes;
- all nested collections and target/reference sets: at most 16 except statements/values at 32 and exact seven requirements.

## Justification

Seven pairs are the TASK-059 representative floor. Sixteen is a deliberately small two-times-plus-two ceiling, not a claimed power-of-two derivation. It allows one bounded expansion beyond seven while remaining below existing BCRP transport ceilings. Eight sections and 32 statements match the same small representative scale. No BCRP limit is enlarged.

Any cardinality/resource violation, duplicate or ambiguous membership, unplanned object/edge, malformed value, unknown field or incomplete closure blocks before rendering. Proven semantic mismatch is non-conforming; incomplete/unparseable evidence is indeterminate. Neither emits a record.
