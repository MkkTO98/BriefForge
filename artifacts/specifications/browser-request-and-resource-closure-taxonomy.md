# Browser Request and Resource-Closure Taxonomy

Date: 2026-08-01
Status: accepted architecture specification
Task: TASK-058
Scope: semantic distinctions and decision criteria only; no browser authority or implementation

## 1. Purpose

This specification separates browser request, transport, response and rendering events that earlier work grouped under “resource closure.” It preserves TASK-057 as historically correct under its strict criterion while determining what a future browser-observation claim would logically require.

The accepted BriefForge architecture nevertheless stops at TASK-056. These definitions do not authorize browser verification, an auxiliary-request exception, publication mutation or a successor task.

## 2. Atomic event taxonomy

Each event is distinct. Occurrence or absence of one does not automatically establish another.

### 2.1 Request discovery

The admitted runtime recognizes a candidate fetch target or implicit resource name. Discovery may arise from document parsing, browser convention, speculation or internal policy. It need not construct or dispatch a request and may be unobservable through the admitted control protocol.

### 2.2 Request construction

The runtime materializes a request object with method, URL, headers, destination/resource class, initiator, frame, loader, credentials/cache policy and redirect ancestry. Construction does not establish dispatch, interception or transport.

### 2.3 Request attempt

A constructed request crosses the defined fetch-dispatch boundary and is submitted for handling. A preblocked attempt remains an attempt. TASK-057’s `/favicon.ico` event reached this stage.

### 2.4 Control-layer interception

An admitted control layer observes an attempt and records one exact disposition: terminal failure, unchanged continuation, modified continuation, redirect or synthetic fulfillment. Installing a rule is not proof that interception occurred; terminal interception does not erase the request attempt.

### 2.5 Network emission

Request-attributable bytes cross the browser/network observation boundary toward transport. Socket creation is not equivalent to HTTP-byte emission, and connection reuse means absence of a new connection is not proof of non-emission.

### 2.6 Service arrival

Request-attributable bytes enter the governed service boundary. Raw connection/byte arrival, complete HTTP request arrival, parser acceptance and route dispatch are distinct subevents. An accepted-route log does not prove that no malformed, rejected or partial request arrived.

### 2.7 Response production

A service, cache, service worker, extension, proxy, interceptor or browser facility constructs response metadata or body bytes. Synthetic fulfillment is response production even without service arrival. A terminal network error is not an HTTP response.

### 2.8 Response receipt

Response metadata or body bytes enter the browser loading boundary. Receipt does not establish parser, decoder or rendering consumption.

### 2.9 Response consumption

A browser consumer reads response metadata or bytes as input to navigation, HTML/CSS parsing, image/font decoding, script execution or another loader. Receipt and consumption are not equivalent.

### 2.10 Document or resource commitment

The browser selects an exact response as the active document or accepted subresource for an exact frame/loader. Commitment binds identity and bytes but does not prove completed parsing, stable layout, paint or raster correctness.

### 2.11 Render-input admission

Bytes or state enter the active document’s DOM/style/layout/paint pipeline. Possible inputs include network/cache/service-worker responses, injected DOM/CSS, extensions, user styles and runtime-owned defaults. Runtime-owned behavior must be bound to the admitted runtime; it is not silently recast as Manifest content.

### 2.12 Render influence

An admitted input changes DOM, computed style, layout, paint, compositing or the bounded raster. Admission and influence remain distinct. “No response-derived render influence” is narrower and more provable than the counterfactual claim that a request attempt caused no timing or scheduling effect whatsoever.

## 3. Closure taxonomy

### 3.1 Attempted-request closure

Every request attempt is completely inventoried and classified by a fixed verifier-owned profile. Two variants are distinct:

- strict attempted-request closure: every attempt maps to an exact governed route/request;
- layered attempted-request closure: every attempt maps either to an exact governed request or to a closed, exact, terminally pre-network auxiliary-attempt signature.

TASK-057 required the strict variant. Layered closure is not accepted by this task.

### 3.2 Network-effect closure

Every request-attributable emitted byte, connection effect and externally visible transport action is inventoried and authorized. A pre-network terminal attempt has no network effect only if the selected observation boundary proves non-emission; CDP self-report alone is not independent packet or syscall evidence.

### 3.3 Service-arrival closure

Every connection and byte arriving at the exact governed service is inventoried, including malformed, partial, rejected and accepted traffic. The inventory reconciles with browser/transport evidence and exact service instance identity.

### 3.4 Response-consumption closure

Every response metadata item and body byte consumed by any active-document loader is exactly authorized and bound to admitted artifact bytes. No cache, worker, extension, proxy, interceptor or synthetic response may evade the inventory.

### 3.5 Render-input closure

Every resource-derived input admitted to the active document’s rendering pipeline traces to the exact Manifest, delivery, deployment and response bytes. Runtime-owned algorithms/defaults trace to the exact admitted runtime profile. No observation-time rewriting, injection, fallback or undeclared response is admitted.

### 3.6 Governed route closure

Every service-arriving and dispatched request maps one-to-one to an authorized method, origin and route, and every produced service response maps to exact delivered artifact bytes. No alias, fallback, directory behavior, redirect, invented route or parser ambiguity exists.

### 3.7 Complete resource accounting

A canonical cross-layer inventory reconciles all observed attempts, interception outcomes, emissions, arrivals, responses, receipts, consumption, commitments and render inputs across exact request/frame/loader/service identities and one bounded interval. It includes unknown, rejected and terminal events rather than reporting only successful resources.

Complete accounting also requires:

- observers active before navigation and losslessly drained after target/browser termination;
- no unknown, duplicate, orphaned, pending or ambiguously correlated event;
- explicit buffer/drop/error status;
- exact runtime, profile, policy and authority bindings;
- canonical persistence, commitment and independent reload;
- deterministic cleanup and residue reconciliation.

## 4. Non-equivalence rules

The following implications are invalid unless separately proven:

- discovery ⇒ construction;
- construction ⇒ attempt;
- attempt ⇒ network emission;
- interception configuration ⇒ actual interception;
- no accepted route log ⇒ no service arrival;
- no service arrival ⇒ no response production, because caches/interceptors may respond;
- response receipt ⇒ response consumption;
- response consumption ⇒ render influence;
- screenshot or DOM existence ⇒ complete request or render-input closure;
- HTTP 200 ⇒ document commitment;
- document commitment ⇒ stable or correct rendering;
- blocked request ⇒ request never happened;
- network idle ⇒ complete accounting or deterministic stabilization.

## 5. Requirements for `bounded_browser_render_observed`

This section distinguishes truth conditions, evidence conditions and BriefForge governance conditions. None is current implementation authority.

### 5.1 Semantic truth conditions

For the narrow historical proposition to be true:

1. one exact admitted browser/runtime must commit one exact governed document;
2. every response byte consumed by the active document must be an exact governed byte;
3. no undeclared response or injected/fallback state may be admitted as publication render input;
4. the browser must reach one bounded observation point at which the exact committed document has an observable DOM and raster;
5. the claim must identify the exact runtime, document, observation interval, DOM and raster and remain limited to that historical act.

These conditions do not by themselves say how an independent verifier proves the proposition.

### 5.2 Evidentiary acceptance conditions

For independent acceptance rather than mere assertion:

1. exact runtime/profile identity and one-use browser authority;
2. complete attempted-request and interception accounting;
3. strict network-effect, service-arrival, response-production, response-receipt and response-consumption closure;
4. exact governed-route, response-byte and document/resource commitment reconciliation;
5. strict render-input closure and no undeclared response-derived render influence;
6. cross-layer request/frame/loader/service identities and lossless event chronology;
7. exact DOM and raster commitments bound to the committed frame/loader;
8. an exact stabilization predicate;
9. canonical evidence, commitment and independent reload with no observer gap or ambiguous correlation.

### 5.3 BriefForge governance and safety conditions

BriefForge would additionally require the complete current TASK-047–056 authority/lifecycle chain, fresh exact deployment, bounded authorization consumption, fail-closed persistence rules, deterministic shutdown, complete residue cleanup, trusted-process limitation disclosure and all authority exclusions. These are governance and operational acceptance requirements, not bare logical necessities of the historical proposition.

### 5.4 Non-authorizing hypothetical sufficient predicate

A future profile would establish `bounded_browser_render_observed` if and only if all of the following held:

1. the semantic truth conditions in §5.1 were evidenced under §§5.2–5.3;
2. every request attempt belonged to a complete inventory;
3. each governed request followed the exact authorized attempt → emission → service arrival → exact response production → receipt → consumption/commitment chain;
4. each permitted auxiliary attempt, if a future architecture authorized any, remained disclosed and terminally followed attempt → interception with independently established zero emission, arrival, response production, receipt, consumption and render-input admission;
5. no unknown, duplicate, orphaned, redirected, modified, fulfilled, pending or ambiguously correlated event existed;
6. every resource-derived render input reconciled to exact Manifest and delivered bytes;
7. the stabilization predicate below passed;
8. canonical evidence and cleanup passed.

For this hypothetical predicate, stabilization would require all expected governed loads and every other attempt to be terminal, `document.readyState` complete, no pending admitted target/loader/request, and two exact canonical DOM observations plus two exact raster captures for the same frame/loader to be byte-identical across a fixed profile-bound quiet interval during which no relevant DOM/layout/paint/network event occurred. A delay, network-idle signal, screenshot or DOM snapshot alone would be insufficient.

Canonical success evidence would bind exact DOM bytes/digest, raster bytes/digest, dimensions, frame/loader, runtime/profile, event sequence and interval. A known unauthorized deviation would be failure. Any observer loss, unknown target/event, dropped buffer, incomplete service inventory, ambiguous correlation or inability to establish a required negative would be indeterminate. Failure and indeterminacy would produce no usable success evidence.

Strict zero-undeclared-attempt closure is one sufficient component of request-attempt provenance, but not a substitute for response, commitment or render-input closure. Layered attempted-request closure could likewise be only one component of the complete predicate above; it is not independently sufficient.

## 6. The favicon question

It is false to claim that TASK-057’s favicon request did not happen. It was an observed request attempt and therefore violated TASK-057’s strict attempted-request closure.

At the level of logic, that exact recorded occurrence need not invalidate every conceivable browser-render claim. It invalidates the stronger claim that no undeclared attempt occurred. A differently authorized layered profile could in principle coexist with the attempt if it proved all downstream zero-effect properties and disclosed the attempt canonically.

BriefForge does not adopt that profile because:

- current evidence does not independently prove all required negative properties;
- current TASK-056 ingress evidence is not a complete all-connection arrival inventory;
- broad causal zero influence is not provable and must be narrowed to response-derived render input;
- maintaining runtime-specific auxiliary signatures and browser-compatible serving authority is disproportionate to the narrow claim’s value.

## 7. Required exclusions

Neither these definitions nor any future `bounded_browser_render_observed` claim imply visual correctness, design quality, accessibility, interaction correctness, semantic comprehension, factual/editorial approval, public reachability, continuing availability, production readiness, reader success or AtlasForge authority.

## 8. Accepted architecture consequence

BriefForge stops at TASK-056’s exact bounded technical-publication boundary. Browser request closure and browser-render observation are not current BriefForge responsibilities. No auxiliary-attempt class, browser evidence profile or implementation successor is authorized.
