# TASK-057 — Bounded Browser-Render Verification Authority Boundary Proof

Date: 2026-07-31
Status: completed — BLOCKED / NOT RECONCILED

## Objective

Implement one fail-closed downstream boundary that may establish only `bounded_browser_render_observed`: one exact admitted Brave/Chromium runtime, under one exact consumed browser authorization and isolated profile, historically navigated and rendered one exact fresh current-eligible TASK-056 loopback deployment during one bounded interval, with canonical independently reloadable evidence and verified cleanup.

## Preconditions confirmed

- TASK-056 remains completed and authoritative; it was not reactivated or modified during preflight.
- No task was active and TASK-057 was unused before activation.
- `/tmp/briefforge-before-task057-20260731.json` predates every TASK-057 repository mutation.
- Repository matched `/tmp/briefforge-after-task056-20260731.json` exactly: 713 paths; helper digest `a6f6adeadcf6b1b3c3b08e784a1cab496a617166062c9ab63aad86d572b1766a`.
- Preflight complete suite: 457 tests passed with bytecode disabled.
- BCRP retains exactly eleven core record kinds and no governed browser authority or observation existed.
- No BriefForge service, browser session, profile, lock, worker, thread or socket residue existed.
- TASK-054, TASK-055 and TASK-056 authoritative repository evidence was byte-identical by exact manifest equality.

## Runtime admission assessment

The existing fixed runtime is admissible under the trusted-process model:

- canonical executable: `/snap/brave/661/opt/brave.com/brave/brave`;
- executable size: `307363056` bytes;
- executable SHA-256: `2e2d5d8f9e8df01d3ac12d4e5fb4f3208eb84f0d77cc163597b0a4ea7003994b`;
- Brave version: `150.1.92.144`;
- CDP product: `Chrome/150.0.7871.186`;
- CDP protocol: `1.3`;
- Chromium revision: `aeb45b6bbb1c16e67ba195ef74d7222a30dce16`;
- no dependency installation or browser download is required.

The runtime is admitted only through a fixed implementation. Caller-supplied executable paths, versions, arguments, profiles, origins, routes or success criteria remain prohibited.

## Bounded implementation slice

### Objective

Add the smallest specialized browser-launch, navigation, observation, evidence and cleanup leaf outside BCRP, using fresh TASK-056 deployment and raw-transport evidence.

### Architectural uncertainty resolved

The current TASK-056 service parser intentionally accepts only an exact request line and `Host`. Actual Brave navigation necessarily synthesizes additional inert browser metadata headers. CDP cannot remove them completely and rejects caller replacement of `Host` as unsafe. Therefore one tightly bounded browser-compatible parser is necessary for actual navigation.

The repair must preserve the strict raw parser and all TASK-056 response, route, byte, authority and evidence semantics. It may accept only unique, size-bounded, syntactically strict inert browser headers; it must continue rejecting bodies, transfer encodings, ranges, conditionals, redirects, traversal and representation-affecting ambiguity. This compatibility repair is part of TASK-057 and does not reactivate TASK-056 or rewrite historical evidence.

A positive multi-artifact HTML+CSS publication is not authorized by the current single-artifact standalone-HTML TASK-052–055 profile. The second materially different case will therefore be a governed negative multi-resource attempt proving that an extra CSS route/resource fails closed. No synthetic fixture may manufacture Manifest authority.

### Implementation boundary

Expected production changes:

- one specialized `briefforge.browser_render_verification` leaf;
- one bounded browser-compatible request parser used by the existing fixed loopback server while retaining the strict raw parser;
- focused TASK-057 tests plus narrowly necessary TASK-056 parser regression tests;
- task specification, decision, implementation report and closeout continuity artifacts.

### Non-goals

No public reachability, current availability after shutdown, cross-browser authority, visual-quality approval, visual-regression oracle, JavaScript/interaction certification, accessibility, reader/editorial/factual authority, redesign, second output format, AtlasForge, database, dependency installation, upstream evidence mutation, Git, DNS, TLS, proxy, cloud or externally routable network.

### Success criteria

- Complete TASK-047–056 authority chain and current eligibility are independently reverified.
- Fresh deployment and fresh raw-socket technical verification succeed before browser authority.
- One exact browser authorization is issued, persisted, committed and consumed before browser launch/navigation.
- Actual Brave networking reaches only the exact numeric-loopback origin/routes.
- Document commitment, route/resource closure, DOM observation, bounded PNG observation and stabilization reconcile.
- Canonical historical evidence and commitment independently reload and detect tampering.
- Failed/indeterminate attempts create no usable success evidence and leave no reusable authorization.
- Browser, profile, lock, cache, storage, service worker, screenshot temporary, process, thread, listener and service residue are absent after shutdown.
- Historical browser observation remains explicitly distinct from current availability and every excluded authority.
- Eleven BCRP kinds/import isolation and all repository mutation boundaries remain intact.

## Gate

Report `CLEAR TO PROCEED` only after adversarial tests, actual installed-browser execution, independent browser/authority review, full verification, audits, bounded recovery and exact pre/post manifest reconciliation all pass.

Otherwise report `BLOCKED / NOT RECONCILED` without weakening browser independence or substituting parser, HTTP-client, filesystem, mock or self-report evidence.

## Execution outcome

The positive gate did not pass.

Actual fixed-Brave navigation reached and committed the exact governed standalone HTML after a bounded live-header compatibility prototype. Brave then emitted an implicit undeclared `GET /favicon.ico`. Interception denied it before service delivery, and preinstalled blocking prevented wire bytes, but CDP continued to record the request. `Page.stopLoading` did not suppress it, and no installed supported switch disabled favicon discovery.

A blocked request remains a request. Ignoring it, treating it as absent, rewriting HTML/response bytes, injecting DOM/script, or inventing a favicon route would violate the explicit authority and resource-closure boundary. Independent browser/authority review confirmed `BLOCK / NOT RECONCILED`.

All unaccepted production and test changes were rolled back. `src/briefforge/bounded_loopback_deployment.py` is byte-identical to the pre-task manifest (`48209` bytes; SHA-256 `50b78984eda7f39632bf4f68b65b043404c98f639e734156a8f702fc41cbe6ee`). No browser-observation evidence or successor authority exists.

## Verification

- preflight complete suite: 457/457 passed;
- restored TASK-056 focused suite: 74/74 passed;
- restored complete suite: 457/457 passed;
- no TASK-057 browser/profile/service/listener residue;
- BCRP remains exactly eleven accepted core kinds through the restored regression suite;
- independent review: BLOCK / NOT RECONCILED.

## Durable links

- Specification: `artifacts/specifications/bounded-browser-render-observation.md`
- Decision: `artifacts/decisions/D-20260731-preblocked-browser-metadata-request-resource-closure.md`
- Report: `artifacts/reports/R-20260731-task-057-bounded-browser-render-verification-blocker.md`

## Reopening condition

Reopen only with explicit authority for a new immutable upstream publication whose governed closure prevents/includes the favicon request, or a separately admitted runtime that demonstrably emits no undeclared request. Do not rewrite this blocked result. No successor task is activated or recommended.
