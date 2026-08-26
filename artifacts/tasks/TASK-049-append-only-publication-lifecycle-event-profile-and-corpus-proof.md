# TASK-049 — Append-Only Publication Lifecycle-Event Profile and Corpus Proof

Status: completed — CLEAR TO PROCEED
Type: bounded representation-profile implementation and conformance correction
Date: 2026-07-16

## Objective

Resolve TASK-048's honest representation blocker by defining and proving immutable append-only publication lifecycle events that reference exact BCRP 1.0 `PublicationReleaseRecord` identities and `release-semantic` fingerprints without mutating Releases or changing their fingerprints.

## Accepted starting state

- TASK-047 is completed and reconciled.
- TASK-048 is an honest **BLOCKED / NOT RECONCILED** architectural result; it was not reconciled or implemented.
- BCRP 1.0 has eleven root kinds and can represent one immutable initial Release.
- BCRP 1.0 has no independently addressable append-only lifecycle-event carrier.
- Baseline recovery passed; TASK-049 was unused before activation; the intentionally non-Git repository had 650 included paths and 206 passing tests.

## Accepted implementation boundary

Implement one separately versioned companion profile:

`briefforge-publication-lifecycle-event-profile` version `1.0.0`

It references, but does not modify or absorb, immutable BCRP 1.0 Releases. It owns:

- immutable lifecycle-event records;
- exact Release identity/fingerprint binding;
- explicit event authority and policy;
- event canonicalization and domain-separated fingerprints;
- append-only history validation;
- deterministic current-state derivation that fails closed on ambiguity;
- generalized valid and invalid corpus proof.

Correct only BCRP 1.0 conformance defects already prohibited by its accepted specification: unsupported core Release lifecycle state, silent multi-Release complete-publication ambiguity, and undeclared embedded lifecycle-event keys. Preserve properly enveloped optional extensions without granting lifecycle authority.

## Semantic decisions

- Initial publication remains solely the immutable BCRP `PublicationReleaseRecord`; no duplicate initial-release event is created.
- Correction is a reason for a new governed Ready and Release, represented by an explicit `supersession` event whose reason is `correction`.
- Supersession binds exact predecessor and successor Release identities and fingerprints; it is never inferred from version ordering.
- Withdrawal is a terminal authoritative event targeting an exact Release; it does not mutate Release status or erase history.
- Rerender is derivative artifact work and creates no lifecycle event.
- Staleness has two non-equivalent forms: a derived validation condition and an authoritative `staleness-declaration` event. This task implements only the declaration event; no polling or elapsed-time inference is added.
- Reinstatement, expiration, replacement without explicit supersession, and distribution suspension are deferred because current evidence does not require them.

## Success criteria

1. The companion-profile choice is accepted against BCRP 1.x and 2.0 alternatives.
2. BCRP 1.0 Releases and `release-semantic` fingerprints remain byte/semantic stable as events append.
3. Earlier event fingerprints remain stable as later events append.
4. Unknown profile versions, event kinds, required extensions, Releases, fingerprints, policies and authorities fail closed.
5. Cycles, self-supersession, competing successors, duplicate identities, time contradictions, cross-publication links and ambiguous current state fail closed.
6. Four generalized valid corpus cases and all required invalid variants pass independent expectations.
7. Core BCRP imports do not import the companion profile.
8. Existing BCRP, TASK-047 and full-suite tests remain green.
9. No Release producer, renderer, artifact, manifest producer, distribution, AtlasForge, database, network, financial semantics or broad migration is added.

## Mandatory stop

Stop before Publication Release production and all renderer work.

## Closeout

### Outcome

- Accepted the separately negotiated companion profile in `D-20260716-publication-lifecycle-event-companion-profile.md` and `publication-lifecycle-event-profile.md`.
- Implemented immutable model/parser, bounded loader, path-scoped canonicalization, independent event fingerprints, fail-closed policy/authority/Release/topology/causality validation, and deterministic graph-derived state.
- Corrected the three bounded BCRP 1.0 conformance gaps without adding companion records to BCRP.
- Materialized 38 static corpus cases: four valid and 34 invalid.
- Proved multi-hop order invariance, Release/event fingerprint append-only stability, explicit negotiation, and BCRP import independence.
- Two adversarial review cycles produced focused RED failures before state/topology/authority/parser/extension hardening and path-aware canonicalization corrections.
- No Release producer, renderer, artifact, manifest, distribution, AtlasForge, upstream, database, network or financial-domain capability was added.

### Verification evidence

- Pre-mutation full suite: 206 tests passed.
- Focused companion/BCRP/TASK-047 suite: 85 tests passed.
- Companion focused suite: 33 tests passed.
- Full implementation suite before closeout: 239 tests passed.
- Static/independence scan: five companion source files; four valid and 34 invalid corpus cases; zero forbidden specialization/import/dynamic-call hits; fresh `briefforge.bcrp` import loaded zero companion modules.
- Final governance verification: architecture audit 0 blocks/0 warnings; coherence, context health and recovery rerun after final compaction.
- Preliminary manifest comparison: baseline 650 paths; after 663 paths; 13 added paths (11 files plus two directories), 14 changed files, no deletion/type/symlink-target change; matching format/root/exclusions. The authoritative final snapshot follows the last check and permits no later repository write.

### Gate

**CLEAR TO PROCEED**.

Exactly one next task is recommended but not activated: `TASK-050 — BCRP Publication Release Authority, Production, and Lifecycle Proof`.
