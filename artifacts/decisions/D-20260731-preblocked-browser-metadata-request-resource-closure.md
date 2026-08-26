# D-20260731 — Preblocked Browser Metadata Requests Do Not Satisfy Exact Resource Closure

Date: 2026-07-31
Status: accepted
Task: TASK-057

## Decision

An actual browser request remains part of the observation inventory even when CDP blocks it before any bytes leave the browser. TASK-057 must not omit, relabel or tolerate Brave's implicit `/favicon.ico` request to manufacture `bounded_browser_render_observed`.

TASK-057 is therefore `BLOCKED / NOT RECONCILED` for the current immutable standalone-HTML publication and fixed installed Brave runtime. No browser success evidence is accepted and no successor is activated.

## Evidence

- The exact governed HTML and response were reached successfully after binding the live Brave request-header profile.
- Brave then emitted an undeclared `GET /favicon.ico` request.
- Fetch interception failed it before service delivery.
- `Network.setBlockedURLs` prevented wire delivery but did not suppress `Network.requestWillBeSent`.
- `Page.stopLoading` did not suppress it.
- Local installed-runtime inspection found no supported favicon-disable feature or switch.
- Independent read-only browser/authority review classified the gate BLOCK / NOT RECONCILED.

## Rejected alternatives

1. Ignore the event: rejected because it falsifies exact request closure.
2. Treat preblocking as no request: rejected because CDP records the request act.
3. Rewrite HTML/response or inject DOM/script: rejected as upstream mutation or observation-time rewriting.
4. Serve a synthetic favicon/204: rejected as undeclared route and resource authority.
5. Relax the gate for browser-internal requests: rejected because the user explicitly required extra disallowed requests/resources to fail closed.

## Consequences

- TASK-056 remains byte-identical, completed and authoritative.
- Unaccepted TASK-057 production and test changes are removed.
- The accepted architecture ends at TASK-056.
- TASK-057 remains durable blocked evidence and creates no browser, current-availability, public, visual, reader or downstream authority.
