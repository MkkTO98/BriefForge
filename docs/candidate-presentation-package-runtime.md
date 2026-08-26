# Candidate Presentation Package Runtime Mapping

Date: 2026-07-02
Status: Initial production implementation documentation for TASK-001

## Purpose

This document explains how the first production implementation maps BriefForge's frozen constitutional concepts onto ordinary runtime objects.

The implementation is intentionally small. It proves that a Candidate Presentation Package can exist as a runtime object without rendering, browser, template, HTML, visualization, export, persistence, API, networking, validation, or downstream-consumer assumptions.

## Runtime mapping

| Frozen constitutional concept | Runtime object | Notes |
|---|---|---|
| Package Identity | `PackageIdentity` | Bounded self-identification: package id, title, purpose summary, scope, and non-scope. |
| Organizing Purpose | `OrganizingPurpose` | Target-independent reason binding statements into one package. |
| Organized Presentation Statement | `PresentationStatement` | Smallest BriefForge-owned unit of presentation meaning. |
| Target-independent encounter semantics | `EncounterSemantics` | Relationship or encounter meaning independent of medium or delivery target. |
| Upstream-owned Reference | `UpstreamReference` | Identifies upstream-owned material while preserving upstream ownership of economic, analytical, evidential, caveat, confidence, freshness, and provenance meaning. |
| Presentation Obligation | `PresentationObligation` | Presentation-local requirement that must remain attached to relevant meaning. |
| Candidate Presentation Package | `CandidatePresentationPackage` | Bounded package-shaped semantic object before validation or downstream consumption. |

## Boundary statement

The implementation deliberately does not include:

- validation;
- rendering;
- templates;
- serialization formats;
- HTML;
- browser support;
- visualization;
- export;
- persistence;
- APIs;
- networking;
- downstream consumers.

The Python dataclasses are implementation records only. They are not architectural authority and do not replace `CONSTITUTION.md` or the approved architecture reports.

## Architectural observation

The frozen constitutional concepts mapped directly to seven small records without requiring delivery concepts. That is positive evidence that the constitutional architecture can exist naturally as runtime substance before validation and before any rendering technology is selected.

The implementation also clarified one practical point: references and obligations are represented both as package-level collections and as statement-level identifier attachments. This preserves the constitutional attachment idea without implementing validation. Whether future validation requires stronger attachment mechanics remains a later task.
