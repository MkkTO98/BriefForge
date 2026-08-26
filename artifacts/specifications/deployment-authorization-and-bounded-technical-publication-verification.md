# Deployment Target, Authorization, and Technical-Publication Verification

Status: accepted
Date: 2026-07-31
Applies to: one bounded numeric-IPv4 loopback static-HTTP profile

## Claim taxonomy

1. Manifest admission admits one exact governed artifact inventory.
2. Controlled delivery installs those exact bytes at one authorized local destination.
3. Deployment authorization permits one exact loopback exposure act.
4. Deployment execution binds one exact implementation and service instance to the delivered inventory.
5. Technical publication success means a separate verifier observed every authorized response over actual loopback HTTP during a bounded interval.
6. Public and reader-facing success concerns durable public reachability, browser behavior, accessibility, discovery, comprehension and editorial quality; this specification grants none of it.

Authorization is not execution. Execution is not readiness. Readiness is not independent reachability. One observation is not continuing availability. Loopback is not public reachability. HTTP correctness is not browser correctness; browser correctness is not accessibility; accessibility is not comprehension; comprehension is not editorial or factual approval.

## Target profile

The only accepted target is:

- scheme `http`;
- numeric IPv4 address `127.0.0.1` only;
- one exact governed port in `1024..65535`;
- exact origin `http://127.0.0.1:<port>`;
- exact route-to-artifact map, with visible ASCII normalized paths and no percent encoding, query, fragment, backslash, traversal, alias, duplicate or collision;
- exact conservative media-type grammar;
- `GET` and HTTP/1.1 only;
- no redirects, directory listing, fallback, transformation, compression, cache, DNS, TLS, proxy or external resource;
- exact status and ordered response headers;
- fixed in-process implementation and deterministic shutdown policy.

The target authority is an exact released semantic authority scope. A caller URL, port, path, role, status or function grants no authority.

## Deployment authorization

One immutable authorization binds the exact controlled-delivery fingerprint; Release and lifecycle binding; target, origin and ordered routes; artifact inventory; implementation and profile; attempt and evidence identities; ledger path/device/inode; request/time bounds; rollback/shutdown policy; and exclusions. Canonical issuance and commitment must independently verify. Identity-keyed exclusive consumption occurs before bind and makes replay, concurrent use and reuse after failure fail closed.

Current controlled-delivery eligibility is independently replayed at issuance, at execution, after exact bytes are pinned immediately before bind, and during subsequent current-state derivation.

## Controlled execution and evidence

The server reopens only exact TASK-055 destination files with no-follow descriptor-relative checks, verifies regular-file identity, length and digest, and serves exact bytes without rewriting. It binds only the governed loopback origin and exact routes.

An internally generated 256-bit per-instance token remains unpersisted; only its digest is evidence. A sealed same-process active receipt and exact token response prove cooperative local instance continuity. This is not authentication against hostile local administrators or processes.

Canonical deployment evidence binds issuance, consumption, delivery, Manifest, Release, lifecycle, target, inventory, implementation, service instance/token digest, observed startup interval, findings, directed links and exclusions. Persisted restart loaders independently reconstruct the chain. Deployment evidence does not assert independent reachability.

## Separate technical verification

A distinct released authority issues and consumes one exact verification authorization. The verifier:

- requires the exact active receipt but derives success only from its own AF_INET/SOCK_STREAM exchange;
- replays current eligibility before every request and after all responses immediately before persistence;
- rejects redirects, partial route closure, wrong status/header/media type/length/body/digest/token or additional data;
- binds every observation to exact route, artifact and service instance;
- persists canonical historical evidence and commitment;
- independently reloads it from paths plus the complete authority chain;
- shuts the controlled service down through the fixed coordinator and persists independently verifiable stop evidence.

The successful state is `bounded-observation-succeeded`: exact governed responses were observed through one exact loopback origin during one bounded historical interval. Current availability after shutdown is explicitly not established.

## Failure and reconciliation

Failures preserve consumed authority and return precise blocked, consumed-failure, completion-pending, persistence-indeterminate or shutdown-indeterminate states. They create no usable technical-success evidence. Failed verification preserves truthful deployment evidence. Reconciliation validates the complete chain and missing-commitment evidence before any write, writes no observation or deployment act, and cannot broaden or replay authorization.

## Exclusions and trust

No public internet, DNS, TLS, proxy, CDN, cloud, browser, JavaScript, accessibility, reader, editorial, factual, production, AtlasForge, database or hosting-provider authority exists. Evidence is historical and immutable; current eligibility and availability are fresh derivations. The trust model remains cooperative process/local writer with canonical commitments and tamper detection—not human authentication, signatures, hostile-administrator resistance, external attestation or WORM storage.

BCRP remains exactly eleven core record kinds; deployment and technical-verification records are specialized downstream companions.
