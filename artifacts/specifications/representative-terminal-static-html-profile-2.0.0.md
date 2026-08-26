# Representative Terminal Static-HTML Profile 2.0.0

Status: accepted
Date: 2026-08-01
Owning task: TASK-062

## Purpose

Define the closed successor boundary that allows one immutable representative Publication Release to carry every operational declaration required through controlled local delivery and bounded technical-publication verification without treating operational authority as displayed semantic content.

## Profile identity

- Identity: `briefforge:representative-terminal-static-html-profile:2.0.0`
- Version: `2.0.0`
- Projection: `briefforge:representative-terminal-static-html-projection:2.0.0`
- Output: exactly one standalone `text/html` artifact named `brief.html`
- Renderer: unchanged real `renderer:representative-static-html` version `1.0.0`
- Adapter: fixed `adapter:briefforge-terminal-to-representative-static-html` version `1.0.0`

Selection is explicit. Cardinality, unknown metadata, caller registration, dynamic import, callable injection and fallback selection never select this profile.

## Closed Release authority inventory

Material authorities are ordered exactly:

1. `authority:briefforge-bcrp-validation`
2. `authority:briefforge-publication-release`
3. `authority:briefforge-controlled-renderer-invocation`
4. `authority:briefforge-semantic-artifact-conformance`
5. `authority:briefforge-publication-manifest-projector`
6. `authority:briefforge-controlled-local-delivery`
7. `authority:briefforge-bounded-loopback-deployment`
8. `authority:briefforge-technical-publication-verifier`
9–16. one to eight content authorities with exact role `presentation-content-authority`, in canonical identity order.

The eight operational identities have exact owner, role and scope schemas. Delivery, deployment and technical-verification scopes are produced by the accepted TASK-055/056 canonical constructors and validated as exact canonical JSON with closed role-specific schemas. Omission, duplication, reordering, cross-role binding, reserved role/identity reuse, unknown keys, broadening and residual classification fail closed.

All eight operational authorities are planned-zero exclusions. They cannot appear in displayed statement, value, provenance, relation, obligation, distribution, requirement-label or HTML semantic-marker realization.

## Projection and renderer adapter

The successor projection is independently rebuilt from the exact persisted Release, complete lifecycle scope, active current state, deterministic Plan and exact authority profile.

The fixed adapter translates only routing metadata to the legacy DTO accepted by the unchanged real renderer. It preserves all displayed semantic fields and all eight operational exclusions. Invocation and conformance evidence bind:

- successor projection fingerprint;
- translated projection fingerprint;
- adapter identity, version and active source digest;
- renderer identity, version and active implementation digest.

Direct successor DTO routing, adapter substitution, digest drift, projection loss and mixed old/new tuples fail.

## Invocation and semantic conformance

Controlled invocation retains the accepted isolated fixed-renderer execution, filesystem boundary, deterministic replay, immutable artifact capture and persisted evidence rules. No network, database, arbitrary executable, callable or fallback surface is introduced.

The successor assessor independently reconstructs the governed projection and parses supplied HTML through the pinned historical independent parsed-semantics core. Its dependency-aware digest binds the reused parser source and transitive assessor closure. It requires exact displayed realization and exact planned-zero/realized-zero accounting for all eight operational objects.

## Manifest and terminal dispatch

The successor Manifest facade produces one existing `PublicationManifestRecord`, preserving the eleven-kind BCRP. It independently verifies the exact successor invocation/conformance tuple, chronology, identity uniqueness, artifact closure, Release/lifecycle/Plan binding, byte digest and persistence commitments.

TASK-055 contains one fixed, source-defined selector with exactly three accepted atomic branches:

- historical minimal v1 authorization pair;
- historical representative v2 authorization pair;
- terminal successor authorization pair.

These are two historical variants of one historical verifier plus one successor verifier. There is no mutable registry, callback, import string, profile fallback or fourth branch. Unknown and mixed tuples fail before verifier entry. TASK-056 remains unchanged and terminal.

## Historical preservation

The complete 39-file pre-mutation TASK-060 Python source closure is archived byte-for-byte under `artifacts/source-closures/task060-v1/`. Its canonical manifest reproduces the historical renderer and assessor implementation digests. Runtime historical verification checks the pinned archive root, exact path inventory, interpreter descriptor, file bytes, both closure digests, unchanged active historical files and the exact sole additive TASK-055 dispatch file digest. Archived digests are never assigned to changed active bytes.

## Explicit non-authority

This profile grants no browser authority, public distribution infrastructure, external hosting, continued availability, successful-publication assertion, AtlasForge authority, analytical authority, visual redesign, network access beyond bounded loopback verification or change to TASK-056's terminal boundary.
