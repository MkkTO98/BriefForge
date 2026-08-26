# BriefForge Capability-v2 Contract Bytes

Status: frozen TASK-076 implementation contract
Normative BCRP record: `artifacts/contracts/task076/capability-v2-record.json`
Exact extension: `artifacts/contracts/task076/capability-v2-extension.json`
Contract: `briefforge:renderer-capability-declaration:2.0.0`

Capability-v2 retains the BCRP 1.0 `RendererCapabilityDeclarationRecord` kind and exact core fields. It requires exactly one extension with the 11-field envelope: owner `briefforge-renderer-capability`, name `renderer-capability-declaration`, version `2.0.0`, exact declaration authority, exact scope/ordered target, required/semantic/must-preserve character, and the v2 validation contract.

The closed payload records declaration, renderer, implementation identity/digest, renderer owner and role, one exact paired profile, ordered unique media types, exact output/asset/table/column integers, exact paired-row mapping capability, operation/authorization/storage identity, canonical issuance time, and domain-separated fingerprint. It also commits the complete core `semantic` object through `semantic_digest`; admission recomputes that digest and verifies record/declaration/target identity, renderer identity, and declaration-time equality. Structural schema validity alone never admits a record. Unknown, partial, duplicate, missing, mixed, reordered, copied, stale, structurally equivalent foreign, or unsupported declarations reject.

Core-only Candidates dispatch to the frozen core capability/Plan family. Paired-v3 requires this exact v2 family. Unknown paired profiles and mixed versions reject. A v1/TASK-067 declaration remains historical and cannot satisfy v2. Missing or duplicated extension families reject. Altering extension bytes changes canonical record bytes and fingerprint verification fails. Capability-v2 grants only renderer-owner support claims; it does not grant selection, invocation, output, conformance, Manifest, publication, or distribution authority.

The normative bytes are a non-authority fixture. Production issuance later requires exclusive canonical persistence plus issuer provenance and authorization reauthentication; naming an owner is never authorization.
