# Bounded Browser-Render Observation Specification

Date: 2026-07-31
Status: blocked; no accepted implementation
Task: TASK-057

## Purpose

Define the minimum downstream authority capable of asserting only `bounded_browser_render_observed` for one exact current-eligible TASK-056 publication under one exact admitted Brave/Chromium runtime.

## Required positive closure

A successful observation must independently bind and reverify:

- the complete TASK-047–056 authority chain and current lifecycle state;
- one fresh exact-byte TASK-056 deployment and raw-transport verification;
- one exact executable identity, browser/CDP versions, fixed launch profile, isolated storage and one-use authorization;
- the exact numeric-loopback origin and complete governed route inventory;
- every browser request, response, redirect, body, route, DOM observation and bounded raster observation;
- deterministic stabilization and complete process/profile/service cleanup;
- canonical evidence that independently reloads without claiming current availability, public reachability, visual quality, accessibility, reader, editorial, factual, production or AtlasForge authority.

Any redirect, fallback, alternate origin, undeclared request/resource, indeterminate event, browser exception, stale authority, incomplete inventory or cleanup failure blocks success evidence.

## Installed-runtime finding

The admitted candidate was fixed Brave `150.1.92.144`, CDP product `Chrome/150.0.7871.186`, protocol `1.3`, executable `/snap/brave/661/opt/brave.com/brave/brave`.

Actual navigation proved:

1. Brave necessarily adds browser metadata headers; a strict bounded parser can admit a finite exact profile without changing response bytes.
2. Brave automatically emits `GET /favicon.ico` after committing the governed standalone HTML, even though the artifact declares no favicon or subresource.
3. CDP request interception can deny the favicon before service delivery, and `Network.setBlockedURLs` can ensure no bytes leave the browser, but both still expose the request in the browser event inventory.
4. `Page.stopLoading` does not suppress the request.
5. The installed runtime exposes no supported favicon-disable switch.

## Blocking boundary

A preblocked request is still an observed request. Treating it as absent would violate the exact request/resource-closure requirement. The permitted alternatives do not solve the boundary:

- changing HTML or renderer output mutates authoritative upstream artifact bytes;
- rewriting the response changes exact TASK-056 response semantics;
- inventing or serving a favicon route creates undeclared resource authority;
- ignoring the event weakens fail-closed observation;
- injecting script or DOM content violates the no-JavaScript/no-rewriting boundary.

Therefore no positive TASK-057 implementation is accepted for the current upstream artifact/runtime pair.

## Reopening condition

Reopen only with explicit authority for one of:

- a new immutable upstream publication whose governed route closure includes a declared favicon or suppresses the probe without runtime rewriting; or
- a separately admitted browser/runtime profile that demonstrably performs no undeclared request.

Any reopening must use a new task or explicit human reopening of TASK-057; it must not rewrite this blocked result.
