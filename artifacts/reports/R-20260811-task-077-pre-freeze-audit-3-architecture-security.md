# TASK-077 Pre-Freeze Audit 3 — Architecture and Security

Status: **FAIL — REMEDIATION BASELINE**
Date: 2026-08-11
Subject: pre-remediation TASK-077 production/test bytes recorded in `R-20260811-task-077-pre-remediation-path-manifest.json`

## Exact blockers

1. Candidate authentication accepted caller-supplied raw bytes plus mutually consistent caller-supplied digest, fingerprint, identity, and extension-family assertions. Self-consistency was treated as process-issued authority rather than structural verification.
2. `NativeVerifiedPlanV2Handle` and its registry created a prohibited parallel native authority instead of extending `NativeBCRPPairedTerminalAdmissionHandle`.
3. Every generic Plan verification/reload constructed a fresh handle, so identical persisted bytes could remint nominally one-use authority after consumption.
4. The public closure verifier accepted fabricated minimal records because complete canonical bytes and independently authenticated record bindings were absent.
5. The verified Plan exposed a custom exact-eight-record JSON hash using metadata that called it BCRP `profile-instance`, although it was not produced by the canonical BCRP profile-instance algorithm.
6. Capability/Plan issuer-input dataclasses were caller-constructible data and did not by themselves prove owner authorization.

## Authorization clarification

The audit initially classified the bounded synthetic lifecycle as prohibited under stale task wording. The human subsequently and explicitly authorized one isolated temporary generation-8-conforming synthetic lifecycle. That authorization does not cure the six production defects above and does not authorize TASK-071 execution or canonical lifecycle state.

## Verified strengths

- Deep immutability probes passed.
- Descriptor-based persistence used canonical roots, no-follow opens, inode checks, exclusive creation, fsync, inventory closure, and repeated rereads.
- Generation-8 governed bytes and protected predecessor hashes remained exact.

## Required architecture direction

- Keep `NativeBCRPPairedTerminalAdmissionHandle` as sole native authority owner.
- Separate immutable data verification/reload from live authority issuance.
- Require independent Candidate admission provenance.
- Bind Capability use through independently authenticated predecessor context without changing frozen Capability bytes.
- Authenticate complete closure records against independent authority.
- Use the contract’s actual Plan payload fingerprint domain; do not mislabel a custom outer byte hash as BCRP profile-instance.

## Ruling

Freeze blocked pending correction and direct adversarial evidence.