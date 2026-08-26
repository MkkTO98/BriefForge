# TASK-077 — Paired Interpretation and Planner-v2 Production Implementation

Status: **CLOSED — IMPLEMENTATION ACCEPTED AND RECONCILED**
Activated: 2026-08-11
Task class: bounded production implementation, actual-entry-point verification, adversarial testing, byte freeze, independent review, and readiness adjudication

## Objective

Implement the accepted generation-8 TASK-076 contract family in BriefForge’s existing production architecture, including authenticated contract loading; exact registry/core/paired graph interpretation; derivation-evidence-envelope v2; Capability-v2 and Plan-v2 construction, serialization, validation, admission, persistence/reload; native planner integration; exact predecessor/cross-layer binding; and fail-closed unsupported-case handling.

The implementation must prove that real production entry points implement the frozen contracts. It must not execute a complete Candidate-to-Manifest lifecycle, perform real TASK-071 governance, or alter frozen generation-8 bytes for implementation convenience.

## Authenticated predecessor

TASK-076 is closed `CONTRACT BYTES ACCEPTED — READY FOR SEPARATELY AUTHORIZED IMPLEMENTATION`. Before activation, no task/successor or overlapping BriefForge process was active. The generation-8 manifest authenticated exactly:

- canonical manifest: `artifacts/contracts/task076/final-contract-byte-manifest.json`;
- governed entries: `23`;
- manifest SHA-256: `b393b7fbdddbcb03792a01ba7ee25056e86a0f70a316b41c036de5314458d0a6`;
- entries digest: `c16ef31551cac6ebf794691461f507013cf52e9bbf07cde8fddaa436f3d2a39a`.

Protected anchors authenticated:

- TASK-071 profile SHA-256: `62cbe5294b123c9b4043e9f721a1b2585c70a5380e2121a39e8558b5c73b1898`;
- paired initializer SHA-256: `b2bd66bf3b9deb346b708348fcd7220d159bcc6df4d44e43e7d0adb5a3ee842e`;
- retained TASK-074 opaque process-local native-handle implementation and TASK-073 native authority-family constraints;
- TASK-060, TASK-062, TASK-067, TASK-069, TASK-071, and TASK-051 states.

Pre-task baseline:

- path: `artifacts/reports/R-20260811-task-077-pre-task-filesystem-manifest.json`;
- entries excluding self: `1084`;
- entries digest: `1e95e18a709caeafe3b86a83083c08406da3b8e3dcae0753cb78adfc39df69f5`.

## Frozen invariants

- All 23 generation-8 governed bytes remain byte-identical; any mismatch is a hard stop.
- Exact TASK-071 Candidate/profile bytes remain sole serialized semantic authority.
- Core and paired interpretation remain separately owned; exact profile/version dispatch precedes decoding.
- Effective graph and counterpart proofs are deterministic non-authority evidence; counterpart proofs are nontraversable.
- Exact results: 37 kinds; 165 core nodes; 722 core edges; 144 paired objects; 590 paired edges; 144 unique counterparts; zero mismatches; explicit `Section.order` exclusion; six requirements; seven owner mappings/Plan rows; `N == decoded row count`.
- Historical TASK-067 authority cannot satisfy native-v2 authority. TASK-074’s opaque process-local handle remains preserved.
- No parallel planner, graph authority, lifecycle, projection, renderer, conformance, or Manifest authority.

## Implementation phases

1. Recovery, protected-byte authentication, and baseline.
2. Contract-to-production owner map before production mutation.
3. One canonical immutable authenticated contract loader.
4. Exact registry, core graph, paired interpretation, counterpart, and effective-graph implementation.
5. Derivation-envelope v2 construction, validation, deterministic persistence, and reload.
6. Exact Capability-v2 production construction and admission.
7. Exact Plan-v2 construction/admission, native planner integration, and 8/10-record closure verification.
8. Actual production-path verification using read-only TASK-071 derivation in temporary non-governed storage only.
9. Port all 63 frozen invalid fixtures and all 36 independent complete-record attacks plus enumerated correlated substitutions to production entry points.
10. Freeze one implementation candidate and obtain fresh unanimous independent reviews over identical bytes.
11. Full verification, final adjudication, governance closeout, and content-sensitive reconciliation.

## Required production ownership map

Before production code, map manifest authentication, registry, core graph, paired decoder/graph/counterparts, envelope, Capability-v2, Plan-v2, planner discovery/coverage, record fingerprints, predecessor closure, persistence/reload, native-handle admission, and projection-facing outputs to governing frozen artifact, existing production owner, additive change, current validator authority, prohibited parallel implementation, tests, and downstream consumer.

If implementation requires missing semantics or conflicts with a frozen contract, stop and report the exact architectural blocker. Do not modify TASK-076 governed bytes.

## Verification boundaries

Positive tests must exercise actual production entry points, not mocks or test-only replicas, including deterministic 16-artifact reconstruction, four schemas, generic `N=0/1/7/16`, exact 8/10 closures, persistence/reload, and native-handle compatibility.

Adversarial tests must reject all frozen invalid fixtures, all independently reviewed reclosure attacks, correlated Capability/Plan substitutions, every underbound Plan field, reordered/foreign/missing manifest families, equal-length and correlated population substitutions, semantic shadows, unsupported profiles/versions, collisions, unknown kinds/locators, counterpart traversal, zero nonempty-obligation coverage, stale/cross-run persistence, and frozen issuer-family bypass. Expected findings must come from independent authenticated inputs, never the mutated subject.

## Prohibitions

No Candidate reauthoring or additional authoring attempt; no real Judgment, Ready, Release, operational Plan, token, projection, rendering, Audit, conformance, Manifest, lifecycle act, external delivery/deployment/HTTP/AtlasForge/network/database/dependency installation/Git/successor action. TASK-069 remains consumed/unavailable/unaccepted; TASK-051 remains unchanged/inactive.

## Closeout gate

Close only after implementation, actual-production-path verification, adversarial tests, unanimous final identical-byte review, full suite/audits/scans/residue/process checks, governance updates, and exact filesystem reconciliation.

Final ruling must be exactly one of:

- `IMPLEMENTATION ACCEPTED — READY FOR SEPARATELY AUTHORIZED ISOLATED CANDIDATE-TO-MANIFEST PROOF`;
- `CONDITIONALLY ACCEPTED`, with every unmet condition;
- `IMPLEMENTATION NOT ACCEPTED`, with exact blockers.

The ruling cannot declare TASK-071 or real Candidate-to-Manifest execution ready. No successor may be created or activated automatically.

## Final closeout disposition

Ruling: **IMPLEMENTATION ACCEPTED — READY ONLY FOR SEPARATELY AUTHORIZED ISOLATED CANDIDATE-TO-MANIFEST PROOF**.

- Historical candidate v6 is the unanimously reviewed implementation candidate: 37 records, aggregate SHA-256 `198c8d2d7a3630cea68c0bf8d73afa4c26e68a2c60a1878ed15a471a25e7adf1`.
- The immutable 34-record implementation/evidence subset remains bound to aggregate SHA-256 `9c1f4cb497caea82101e21e63ad431add61fb4d9899c999a505f0992c6930fe0`.
- Focused validation passed 123/123; complete discovery passed 739/739; TASK-076 validation passed.
- The frozen matrix reconciled 63/63 fixtures: 43 representable, 17 authority-blocked, and 3 non-input/production-computed.
- Structured derivation routes passed 9/9. Cleanup ownership and structured filesystem-error adversarial coverage passed without `ResourceWarning`, bytecode/cache residue, or TASK-052 residue.
- Reviewers C, D, and E independently returned PASS over identical v6 bytes.
- Pre-closeout immutable-subset and protected-identity drift was zero. Final closeout reconciliation is recorded in `artifacts/reports/R-20260821-task-077-governance-closeout.md`.
- No real lifecycle execution, installation, deployment, publication, staging, commit, push, or merge occurred.
- No successor was created, recommended, or activated. TASK-071 and real Candidate-to-Manifest execution remain deferred and unauthorized.
