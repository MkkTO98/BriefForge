# TASK-077 Phase 3 — Paused-Byte Inspection and Interpretation/Envelope Implementation

Status: **PASS FOR PHASE-3 SCOPE / NOT TASK-077 ACCEPTANCE**
Date: 2026-08-11

## Recovery after command denial

The human explicitly authorized resumption without authorizing any boundary bypass. `python3 tools/recover_session.py --project . --json` confirmed TASK-077 remains the sole active task and no successor exists. Process inspection found no overlapping BriefForge/TASK-077 operation. `tools/validate_task076_contracts.py` passed before mutation and the frozen manifest, TASK-071 profile, and paired initializer hashes remained exact.

The four delegated module bytes had no recorded pre-denial hash, so byte-for-byte comparison to the paused instant was not independently possible. No write occurred between the denial and resumed inspection, and the full module contents observed at the paused handoff matched the resumed inspection. Initial resumed hashes were:

- `task076_contracts.py`: `c9f39e871afd9d37fcd13cd5264c2a4686d6ca21f1117ad686ae017a7277f37d`;
- `bcrp/registry.py`: `ba1257635d64d38867310b814bdfd81f07b12e91e13958727c4c01698ecec97d`;
- `bcrp_paired_semantic_interpretation_v2.py`: `aa40cf25364b95527a685f02c9a167949477a096847e33609bb403ef2a167e52`;
- `bcrp_paired_derivation_evidence_v2.py`: `02e5714dfaf6f7b5eea30bfee425f1c375090989c0f7e07730201d9874476e0f`.

## Inspection classification

### `src/briefforge/task076_contracts.py`

Initial classification: **retainable core, incomplete authority boundary**.

Correct/retainable:

- one checkout-owned root with no caller/environment override;
- exact manifest SHA-256, generation, contract, count, ordered entries digest, path, length, and SHA-256 checks;
- exact TASK-071 bytes/canonical BCRP/fingerprint authentication;
- recursively immutable manifest/documents;
- domain-separated digest helper.

Defects remediated:

- generic `document()` exposed fixture/evidence documents as if production contract authority;
- exact contract-directory inventory was not closed.

Current behavior exposes only registry/schema/validation-rule documents through the production document API while retaining all 23 authenticated bytes as opaque byte evidence. Missing/extra/symlinked contract-directory inventory rejects.

### `src/briefforge/bcrp/registry.py`

Initial classification: **correct output, incomplete immutability, production logic partially misplaced**.

Correct/retainable:

- authenticated 37-entry registry;
- exact profile dispatch and record-kind rejection;
- exact registry-driven 165-node extraction;
- exact 722-edge reconstruction;
- duplicate/dangling/misplaced identity and unknown/kind-mismatched locator rejection;
- digests reproduce frozen values.

Defects remediated:

- fragments were shallowly immutable;
- paired interpretation bypassed the existing `bcrp.graph` public owner.

The extraction engine remains registry-owned, while `bcrp.graph.reconstruct_generation8_core_graph` is the existing graph-owner entry point consumed by paired interpretation. Historical graph APIs remain unchanged.

### `src/briefforge/bcrp_paired_semantic_interpretation_v2.py`

Initial classification: **semantically correct and retainable, incomplete immutability/owner routing**.

Correct/retainable:

- reuses the existing exact paired decoder rather than creating a semantic shadow;
- exact 144-object inventory and 590-edge paired graph;
- exact six requirements and seven authored mappings;
- exact 144 unique counterpart proofs, zero mismatch, sole `Section.order` exclusion;
- `Provenance.source_snapshot_identity` edge classification;
- nontraversable counterpart evidence and separated effective graph;
- every frozen graph/inventory digest matched independently.

Defects remediated:

- object fragments and semantic documents were only shallowly immutable;
- core graph was called from registry internals instead of the existing graph owner;
- deep immutability initially changed comparison container types; comparisons now convert immutable views to plain canonical values without changing any frozen digest.

No test-only expected count or fixture finding became production authority.

### `src/briefforge/bcrp_paired_derivation_evidence_v2.py`

Initial classification: **retainable construction/verification, unsafe/incomplete persistence**.

Correct/retainable:

- exact closed v2 envelope;
- independent reconstruction from authenticated Candidate, registry, decoder, graphs, proofs, and coverage;
- exact field/digest reconstruction; only production implementation digest and resulting fingerprint differ from the non-authority fixture;
- correlated self-reclosure rejects against reconstructed authority.

Defects remediated:

- construction now reassigns the independently reauthenticated Candidate object;
- persistence now uses canonical absolute directory checks, no-follow descriptor opening, inode binding, empty-inventory gate, exclusive create, bounded write, fsync, exact inventory check, two descriptor-bound rereads, and owned-file cleanup on failure;
- reload now authenticates exact singleton inventory, bounded regular-file bytes, stable inode/size, repeated reread, Candidate/run bindings, and exact reconstructed envelope.

No schema, fixture label, expected finding, or derived evidence is admitted as semantic authority.

## TDD and command record

Initial RED run: 10 tests produced two failures and one test-selection error:

- fixture/evidence document was improperly exposed;
- nonempty persistence inventory was accepted;
- immutability test selected a scalar-only node.

After correction, deep freezing exposed a real tuple/list comparison defect in counterpart validation; this was fixed by canonical plain-value comparison. A final test-selection defect selected a non-Section paired node and was corrected.

Final focused suite:

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest -v tests.test_task077_interpretation_envelope`
- result: **12/12 PASS in 5.418s**.

Actual production entry points exercised include contract/Candidate loading, registry execution, graph owner, paired decoder/graph/counterparts/effective graph, envelope construction/verification/serialization, persistence, and reload. Negative tests cover equal-length Candidate substitution, fixture-as-authority exposure, unknown/kind-mismatched locators, symlinked governed input, correlated outer-fingerprint reclosure, nonempty persistence inventory, and stale cross-run binding.

Relevant regressions:

- `tests.test_bcrp_vertical_slice`: **29/29 PASS**;
- `tests.test_task067_schema_projection`: **19/19 PASS**;
- TASK-076 validator: **PASS**, including 16 deterministic artifacts, four schemas, 63 invalid fixtures, 10 valid fixtures, and generic N=0/1/7/16 contract checks.

## Exact production/frozen comparison

Production results:

- registry: 37;
- core graph: 165 nodes / 722 edges;
- paired graph: 144 nodes / 590 edges;
- counterparts: 144, nontraversable, zero mismatch;
- requirements/mappings: 6 / 7;
- core, paired, counterpart, effective, requirement, and mapping digests: all exact frozen matches.

Envelope construction with the normative fixture’s independent metadata differed only at `implementation_digest` and the resulting final `fingerprint`, as required for the real production implementation rather than the non-production fixture builder.

## Current implementation-byte hashes

- `task076_contracts.py`: `18bfad39289aaf86320ce72d2f96c7b6e69ca1b96f7e50bb1a4587d61b6ef0e7`;
- `bcrp/registry.py`: `651f5465c49da789d952a835e74aa4490ae4b94e8aeb57a280eca5a42acb4074`;
- `bcrp/graph.py`: `af9306355dda8d0addd8da6788920fa66e4ce709475aeabfdfd67675993fb2be`;
- paired interpretation: `4f1c5866d4d9efb9ac2d28fa14f4341f31b36bd0ff2f1b9fb1f60f85bf9dbd75`;
- derivation envelope: `7d51ee3c98b3ad760b509baeb324727c4bc525de401cdd3fa6cc33b8532c5e0f`;
- focused tests: `a8789499170df6abf45231be655b63993a7e53c3d135032557a37418e25ba0ed`.

These are phase evidence, not the final reviewed implementation-byte freeze.

## Residue observation

49 `.pyc` files were observed. Four correspond to the new modules and were created by the timed-out delegated attempt before the denial; the remainder pre-existed or came from earlier repository activity. Subsequent commands used `PYTHONDONTWRITEBYTECODE=1`. No cache or bytecode was deleted.

## Preservation and phase ruling

Frozen generation-8 manifest SHA-256 remains `b393b7fbdddbcb03792a01ba7ee25056e86a0f70a316b41c036de5314458d0a6`; TASK-071 and paired initializer remain exact. No real lifecycle or prohibited operation occurred.

Phase-3 scope passes focused production verification. This does not accept TASK-077: Capability-v2, Plan-v2, closures, native integration, full adversarial port, final byte freeze, independent review, and complete closeout remain pending.
