# D-20260731 — Accept bounded loopback deployment and technical-publication verification

Status: accepted
Date: 2026-07-31

## Decision

Accept one specialized downstream authority boundary outside BCRP for exact numeric-IPv4 loopback static-HTTP deployment and separately authorized transport verification.

The boundary may establish only:

- one exact governed deployment target and one consumed deployment act;
- exact byte-preserving loopback service execution;
- separately authorized observation of every admitted route over actual HTTP transport;
- immutable historical deployment, observation and shutdown evidence.

It may not establish public reachability, continuing availability, browser renderability, accessibility, reader access or comprehension, editorial/factual approval, production readiness or AtlasForge authority.

## Rationale

TASK-054 Manifest admission and TASK-055 controlled delivery are necessary but insufficient for serving or observed reachability. Deployment authority must be released and consumed independently. Service readiness is still insufficient: technical publication success requires separate verifier authority and real transport observation. A bounded loopback profile proves this separation without importing public-hosting responsibility into BriefForge.

## Rejected alternatives

- Treat filesystem placement, port binding, process state or readiness as publication success.
- Infer target authority from caller URLs, ports, functions or status labels.
- Place deployment authority in an existing BCRP, Release, Manifest or delivery record.
- Use deployment self-report or direct filesystem comparison as reachability evidence.
- Generalize to public internet, DNS, TLS, browser or cloud deployment.

## Consequences

- Exactly eleven BCRP core kinds remain.
- `bounded_loopback_deployment.py` and `technical_publication_verification.py` are specialized leaf companions.
- One-act authorizations are persisted, committed and identity-consumed before side effects.
- Current eligibility is replayed at each authority/use boundary.
- Active instance continuity uses an unpersisted random token within the cooperative same-process model; it is not hostile-process authentication.
- Historical success remains immutable while current availability after shutdown is not established.
- The next justified boundary is bounded browser-render verification, not public deployment.
