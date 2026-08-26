# Renderer Output Conformance Boundary

Date: 2026-07-02
Task: TASK-011 Renderer Output Conformance Boundary
Status: Implemented as a downstream audit-link conformance proof.

## Purpose

TASK-011 proves that rendered artifacts can be checked as downstream outputs without becoming semantic authority.

The boundary verifies that a rendered artifact's audit metadata still links to the Ready Presentation Package that authorized downstream rendering.

## Implemented objects

Implemented in `src/briefforge/renderer_adapter.py`:

- `RenderedArtifactConformance`
- `RenderedArtifactConformanceRejected`
- `check_rendered_artifact_conformance(ready_package, artifact)`

The conformance boundary checks:

- package identity;
- semantic fingerprint;
- validation policy identity;
- rendered artifact shape.

## Why rendered artifact conformance is downstream validation, not constitutional validation

Constitutional validation evaluates Candidate Presentation Package substance before readiness. It determines whether a candidate can become a Ready Presentation Package.

Rendered artifact conformance is different. It occurs after readiness and after rendering. It does not inspect or validate presentation substance. It only checks whether downstream rendered output still carries audit metadata consistent with the Ready package.

The ordering remains:

```text
Candidate Presentation Package
-> Constitutional Validation Judgment
-> Ready Presentation Package
-> Renderer Adapter Boundary
-> Renderer Adapter Invocation
-> Rendered Artifact
-> Rendered Artifact Conformance
```

Conformance therefore answers: "Is this downstream artifact still audit-linked to this Ready package?" It does not answer: "Is this package constitutionally valid?"

## Why rendered output remains non-canonical

Rendered output remains non-canonical because the canonical BriefForge object is still the structured semantic Presentation Package.

`RenderedArtifactConformance` does not expose:

- candidate package substance;
- statements;
- organizing purpose;
- upstream references;
- obligations;
- validation judgment;
- promotion authority;
- semantic authority.

It records only conformance status, findings, and audit metadata. A conforming rendered artifact is therefore allowed to be trusted as downstream output of a Ready package, but it does not replace the Ready package.

## Why audit-link consistency matters before richer renderers

Richer renderers will create more distance between package substance and output surface. Before HTML, PDF, browser interfaces, templates, charts, maps, exports, or UI components exist, BriefForge needs a small invariant: every rendered artifact must remain linked to the Ready package identity, semantic fingerprint, and validation policy identity that authorized it.

TASK-011 establishes that invariant while the renderer is still deliberately trivial. This reduces architectural risk before any richer rendering target is considered.

## Rejection and mismatch behavior

Malformed rendered artifacts are rejected with `RenderedArtifactConformanceRejected`.

Well-formed rendered artifacts with mismatched audit metadata return a non-conforming `RenderedArtifactConformance` with findings naming the mismatched fields:

- `package_identity`
- `semantic_fingerprint`
- `validation_policy_id`

Conformance checking does not mutate Ready packages or rendered artifacts.

## Constitutional contradiction assessment

No contradiction in the frozen constitution was exposed.

TASK-011 reinforces the constitution: rendered artifacts can be checked downstream for audit consistency without becoming semantic authorities and without moving BriefForge into renderer-engine, browser, template, API, persistence, visualization, portal, dashboard, or UI ownership.

## Implementation Readiness Assessment

Validated by TASK-011:

- A toy rendered artifact conforming to its Ready package passes conformance.
- Wrong package identity fails conformance.
- Wrong semantic fingerprint fails conformance.
- Wrong validation policy identity fails conformance.
- Malformed artifacts are rejected.
- Conformance checking does not mutate Ready packages or rendered artifacts.
- Conformance result does not become semantic authority.

Still intentionally unimplemented:

- HTML;
- PDF;
- browser output;
- templates;
- charts, maps, visualization;
- exports;
- persistence;
- APIs and networking;
- portal, dashboard, search, or UI behavior;
- renderer registry or plugin architecture;
- production renderer conformance framework.

Recommended next investigation:

If further implementation is approved, the next minimal step should strengthen audit/event representation around rendered outputs or rejected conformance checks. Do not proceed directly to HTML, browser reports, dashboards, or renderer registries.
