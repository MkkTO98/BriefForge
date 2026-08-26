# TASK-067 Implementation Contract — Versioned Terminal Profile and Paired-Table Capability

Date: 2026-08-01
Status: recommended, unactivated
Authority source: TASK-066 decision and specification

## Objective

Implement exactly the additive versioned capability frozen by TASK-066 while preserving TASK-062 and all historical behavior unchanged.

## Authorized implementation scope

### Additive production modules

Create only this new package inventory:

- `src/briefforge_paired_terminal_profile/__init__.py` — exact public identities only;
- `src/briefforge_paired_terminal_profile/schema.py` — frozen immutable DTOs and exact-field validation;
- `src/briefforge_paired_terminal_profile/profile.py` — authority/profile admission;
- `src/briefforge_paired_terminal_profile/projection.py` — lossless projector and fingerprint verification;
- `src/briefforge_paired_terminal_profile/renderer.py` — fixed static HTML paired renderer;
- `src/briefforge_paired_terminal_profile/controlled_invocation.py` — exact invocation authorization/evidence and deterministic replay;
- `src/briefforge_paired_terminal_profile/semantic_conformance.py` — independent parser/assessor and conformance authorization/evidence;
- `src/briefforge_paired_terminal_profile/manifest_admission.py` — v3 Manifest production/verification only.

The only existing production file permitted an additive edit is:

- `src/briefforge_terminal_profile/manifest_admission.py` — add one deferred v3 tuple branch and one exact eligibility-contract branch; all historical branches remain unchanged.

No other existing production file may change. In particular `src/briefforge/publication_distribution_delivery.py`, all TASK-062 profile/schema/projector/renderer/invocation/conformance modules and every `src/briefforge/bcrp/**` file remain byte-identical.

### Exact selector tuple

- invocation class: `briefforge_paired_terminal_profile.controlled_invocation.PairedTerminalRendererInvocationAuthorization`;
- conformance class: `briefforge_paired_terminal_profile.semantic_conformance.PairedTerminalSemanticArtifactConformanceAuthorization`;
- Manifest class: existing exact `briefforge.publication_manifest_admission.PublicationManifestAuthorization`;
- Manifest validation contract: `briefforge:paired-terminal-publication-manifest-admission-authority:3.0.0`;
- target verifier: `briefforge_paired_terminal_profile.manifest_admission.verify_persisted_paired_terminal_publication_manifest`.

All other exact policy/profile/evidence/implementation identities are frozen in specification §2.

### Source-closure procedure

Before editing the selector, archive and content-address its exact pre-change bytes, length and SHA-256. Record a fresh active digest after editing. Preserve historical labeling and never attribute the old digest to new bytes. The delivery facade remains unchanged, so TASK-062's active-delivery digest remains truthful.

### Test groups

Add focused test modules grouped by:

1. strict schema/boundary N+1 rejection;
2. profile and authority admission;
3. projection consumption, identity/edge/order closure and tampering;
4. paired renderer structure, determinism and HTML security;
5. controlled invocation and no-evidence-on-failure;
6. independent parsed conformance and renderer/assessor mutation independence;
7. exact v3 Manifest tuple and exhaustive mixed/subclass/unknown dispatch rejection;
8. historical source closure, persisted-evidence reload and byte-identical golden outputs;
9. BCRP eleven-kind/import independence and no production special-casing.

TASK-067 may add only synthetic new focused fixtures needed by those groups. Historical fixtures are immutable.

## Required boundaries

- Reuse all eleven existing BCRP kinds; do not change core record-kind closure.
- Preserve existing source closures, accepted profiles, strict schemas, projections, renderers, fixtures, persisted evidence and dispatch tuples unchanged except for the minimum additive dispatch cases explicitly required.
- No registry, plugin, dynamic import, callable injection, version range, alias, fallback or environment-selected capability.
- No generic table DSL, template system, runtime conditional-composition engine or analytical recomputation.
- No T-039/TASK-064/TASK-065 identities, values, periods, counts or domain terms in production modules.
- Keep operational authorities non-displayed and lifecycle/distribution authority unchanged.

## Mandatory acceptance proof

- profile/schema/projection/renderer/conformance layers remain separately testable;
- exact pair ownership, metadata, attachment topology and the five frozen governed column identities survive projection;
- renderer emits one relationship-owned row per projection row and fixed five-column output;
- assessor independently parses and rejects semantic drift;
- all bounds fail at N+1;
- all mixed/unknown/subclass dispatch tuples fail before verifier entry;
- historical golden projections/artifacts and persisted evidence remain byte-identical and reloadable;
- BCRP import independence and eleven-kind invariant pass;
- no sibling-project mutation or excluded authority.

## Stop line

Stop after implementation, tests, independent review and reconciliation. Do not create a representative Candidate, consume TASK-065's unused attempt, promote records, construct a Release, project governed pilot evidence, render a representative artifact, or enter the TASK-056 chain.

A representative retry is a later separately authorized task.
