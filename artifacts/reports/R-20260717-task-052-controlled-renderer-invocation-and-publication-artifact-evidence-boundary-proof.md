# TASK-052 Controlled Renderer Invocation and Publication Artifact-Evidence Boundary Proof

Date: 2026-07-17
Status: completed
Gate: **CLEAR TO PROCEED UNDER DOCUMENTED CLOSEOUT-EVIDENCE EXCEPTION**

## Conclusion

The implementation and authority boundary pass their functional, security and independent-review gates. The original mechanical closeout was **BLOCKED / NOT RECONCILED** because the required pre-task filesystem manifest was captured after five TASK-052 paths had already been created. On 2026-07-30, the human project owner accepted the exact count-and-path reconstruction as sufficient closeout evidence under a bounded documented exception. TASK-052 is therefore **COMPLETED — CLEAR TO PROCEED UNDER DOCUMENTED CLOSEOUT-EVIDENCE EXCEPTION**.

This result does not assert semantic conformance, Manifest authority, distribution authority or successful publication. No `SemanticArtifactConformanceRecord` or `PublicationManifestRecord` is created or accepted.

## Human closeout disposition

`artifacts/decisions/D-20260730-task-052-closeout-evidence-exception-acceptance.md` preserves four distinct facts:

1. Functional and security outcome: completed and independently approved.
2. Original mechanical closeout outcome: blocked by late pre-manifest capture.
3. Human disposition: the exact 678 -> 683 five-path identity reconstruction is accepted as sufficient historical mutation-accounting evidence.
4. Final current status: clear to proceed under the documented exception.

The original 678-path byte state remains unavailable and is not reconstructed or represented as available. The exception waives no technical or semantic validation and does not weaken future pre-task manifest sequencing requirements.

## Context and authority used

- `CONSTITUTION.md`, project execution methodology and continuity policy;
- TASK-047 governed Candidate/Judgment/Ready authority;
- TASK-049 append-only lifecycle scope and current-state derivation;
- TASK-050 immutable Publication Release production/verification;
- TASK-051 deterministic renderer compatibility Plan production/verification;
- BCRP eleven-kind model and layered validation;
- existing `renderer:minimal-html` / `minimal-html-renderer` implementation.

TASK-051 remained completed and unchanged.

## Implementation

### Exact input and mapping closure

`src/briefforge/controlled_renderer_invocation.py` independently reverifies the exact Release, evidence snapshot, complete lifecycle inventory/current state, Plan bundle/mapping bytes/fingerprint, capability declaration and governed invocation authority immediately before execution. Plan mappings must cover exactly the projected purpose, statements and obligations; external references are admitted only as the resolved linkage closure of mapped statements. Missing, duplicate, stale, fallback, contradictory, unconsumed or unplanned material blocks.

The projection is constructed only from released BCRP semantic records and reproduced Plan mappings. It never accepts or reconstructs legacy Ready renderer input.

### Exact renderer and isolated execution

The only renderer is fixed as `renderer:minimal-html`, adapter `minimal-html-renderer`, media type `text/html`, logical filename `publication.html` and one output. The implementation digest binds renderer source, the loaded function closure, same-module callable classes, fixed worker source and projection-loader code. Unsupported executable dependency shapes fail closed.

`src/briefforge/_controlled_renderer_worker.py` is launched twice with no caller-selected executable/module/template/callable/command. Each child receives only the fixed minimal environment and fixed flags `-B -s -S -X utf8`. Before accepting bytes, the parent verifies the child's exact effective environment plus bytecode, hash-randomization, environment-ignore and UTF-8 flags. Parent CWD and environment are unchanged. Two independent temporary directories must return byte-identical output; there is no retry or fallback.

### Output and HTML safety

The boundary admits only one bounded UTF-8/LF standalone HTML byte string. Parser-based policy rejects active/resource-bearing elements, event handlers, executable or external URI attributes, inline style attributes, meta refresh, CSS imports/URLs/expressions, malformed document structure, non-UTF-8, CRLF, empty output and oversized output. Same-document bounded fragment links are the only URI-bearing exception.

Renderer exceptions, timeouts, nondeterminism, auxiliary files, wrong count/media type, symlinks, traversal, non-regular files, staged mutation and directory substitution produce no usable success evidence.

### Atomic persistence and independent verification

One successful transaction writes exactly `publication.html` and canonical `invocation-evidence.json` into descriptor-relative staging, rereads and verifies both, writes an external admission commitment, then commits through one inode-checked Linux `renameat2(RENAME_EXCHANGE)`. Rollback verifies both exchange sides and safely restores the authorized destination. Persisted verification pins the directory descriptor through complete verification, rechecks the authorized pathname, inventory and bytes before return, and verifies the external commitment.

The nine-record closure contains the TASK-050 six-record Release closure, TASK-051 capability/Plan records and one `GeneratedArtifactAuditRecord`. Its extension records:

- artifact existence: `verified`;
- invocation/audit links: `verified`;
- semantic conformance: `unassessed`;
- Manifest authority: `absent`;
- distribution authority: `absent`;
- successful publication: `not-asserted`.

## Adversarial coverage

Focused tests prove:

- one real accepted renderer succeeds;
- exactly two independent executions and identical bytes;
- effective child interpreter/environment controls;
- exact Release/lifecycle/Plan/capability/renderer/projection/authorization binding;
- authorization non-reuse;
- digest/length and persisted-evidence verification;
- input immutability and coordinated artifact/evidence forgery detection;
- stale/blocked/mutated Plan and withdrawn/superseded/incomplete lifecycle rejection;
- missing/duplicate/unconsumed/fallback mapping rejection;
- renderer source/helper/callable drift rejection;
- actual timeout, exception, nondeterminism, empty/auxiliary/excessive/oversized output rejection;
- traversal/symlink/directory/staging/exchange/tamper failures;
- strict HTML escaping and external-resource prohibition;
- no conformance, Manifest, distribution or publication authority;
- valid required BCRP extension envelope.

Existing TASK-047/049/050/051, renderer and BCRP suites provide the neighboring lifecycle ambiguity, malformed policy/event, renderer security and generic profile regression matrix.

## Independent review

Independent authority-critical reviews found and drove correction of:

- coordinated artifact/evidence rewrite without an external commitment;
- loaded renderer helper substitution;
- unsafe parent-global environment mutation;
- ineffective Python environment controls under isolated mode;
- incomplete renderer dependency closure;
- dangling invocation authority links;
- broad generic-extension suppression;
- parent/path and rollback identity races;
- persisted-verification pathname/byte TOCTOU;
- malformed runtime authorization types;
- incomplete mapping-to-projected-material closure.

The final re-review independently probed the exact effective child controls and returned **APPROVED** with no unresolved blocker.

## Verification

- Focused TASK-052 suite: `22` tests, OK.
- Complete suite: `296` tests, OK.
- BCRP core record kinds: exactly `11`.
- Fresh BCRP import: no renderer invocation, renderer adapter, Release, lifecycle, planning or downstream modules imported.
- Dangerous-call/dynamic-import/domain-specialization scan of TASK-052 production files: clean.
- Staging/admission-residue scan: clean.
- Bytecode/cache residue is removed before final manifest capture.
- Coherence, context health, architecture-to-reality audit, bounded recovery and final manifest comparison are recorded below after final execution.

## Explicit limitations

Authorization construction, authorization-ledger retention and output-parent integrity remain trusted BriefForge process/local-writer assumptions. Hashes and admission commitments provide consistency and tamper detection; they do not provide human authentication, digital signatures, hostile-code kernel sandboxing, external attestation or WORM storage. No such stronger claim is made.

## Filesystem accounting

The required helper reported the fresh file `/tmp/briefforge-before-task052-20260717.json` with 683 included paths. It contains five TASK-052 paths that the user-supplied 678-path baseline said did not yet exist:

- `artifacts/decisions/D-20260717-controlled-renderer-invocation-and-artifact-evidence-boundary.md` — expected TASK-052 decision;
- `artifacts/specifications/controlled-renderer-invocation-and-artifact-evidence.md` — expected TASK-052 specification;
- `artifacts/tasks/TASK-052-controlled-renderer-invocation-and-publication-artifact-evidence-boundary-proof.md` — expected TASK-052 task;
- `src/briefforge/controlled_renderer_invocation.py` — expected TASK-052 production implementation;
- `tests/test_controlled_renderer_invocation.py` — expected TASK-052 tests.

This exactly explains the count difference 678 -> 683, but no authorized byte manifest exists for the missing 678-path instant. These five paths are expected in scope, not evidence of unrelated mutation; the defect is manifest sequencing and loss of exact pre-creation byte evidence.

Direct comparison of the actual 683-path pre-manifest to the final 686-path post-manifest reports:

Added (3):

- `artifacts/reports/R-20260717-task-052-controlled-renderer-invocation-and-publication-artifact-evidence-boundary-proof.md` — required TASK-052 outcome report;
- `artifacts/reports/R-20260730-architecture-reality-audit.md` — required architecture-to-reality audit;
- `src/briefforge/_controlled_renderer_worker.py` — required fixed isolated worker.

Modified (19):

- governance summaries: `artifacts/decisions/_SUMMARY.md`, `artifacts/reports/_SUMMARY.md`, `artifacts/specifications/_SUMMARY.md`, `artifacts/tasks/_SUMMARY.md`;
- TASK-052 governance: `artifacts/specifications/controlled-renderer-invocation-and-artifact-evidence.md`, `artifacts/tasks/TASK-052-controlled-renderer-invocation-and-publication-artifact-evidence-boundary-proof.md`;
- generated context/continuity: `context/active_context.md`, `context/context_audit.json`, `context/context_audit.md`, `context/context_manifest.json`, `context/latest_handoff.md`;
- production: `src/briefforge/controlled_renderer_invocation.py`;
- source/test summaries: `src/briefforge/_SUMMARY.md`, `tests/_SUMMARY.md`;
- current-state pointers: `state/active_goal.md`, `state/architecture.md`, `state/project_state.md`, `state/recent_changes.md`;
- tests: `tests/test_controlled_renderer_invocation.py`.

Deleted: 0. Type changes: 0. Symlink changes: 0. Differences outside the expected implementation, test, governance, context and audit scope: 0.

The helper-reported final post-manifest digest is recorded in the final response. The manifest itself is `/tmp/briefforge-after-task052-20260717.json`.

## Stop and next task

TASK-052 stops at artifact existence and invocation/audit-link evidence. It does not perform semantic-conformance approval, audit-link promotion, Manifest production, distribution, AtlasForge integration or visual redesign.

TASK-053 is the one recommended next task but remains unactivated: `TASK-053 — Publication Artifact Semantic-Conformance and Audit-Link Proof`.
