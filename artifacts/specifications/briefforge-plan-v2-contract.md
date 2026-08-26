# BriefForge Plan-v2 Contract Bytes

Status: frozen TASK-076 implementation contract
Normative BCRP record: `artifacts/contracts/task076/plan-v2-record.json`
Exact extension: `artifacts/contracts/task076/plan-v2-extension.json`
Completeness object: `artifacts/contracts/task076/planning-completeness-evidence.json`
Contract: `briefforge:renderer-compatibility-plan:2.0.0`

Plan-v2 retains the BCRP 1.0 `RendererCompatibilityPlanRecord` and existing planner ownership. Exactly one v2 extension is admitted: owner `briefforge-renderer-compatibility-planning`, name `renderer-compatibility-plan`, version `2.0.0`, exact planning authority, exact ordered Plan/Candidate/Release/capability targets, required/semantic/must-preserve character, and exact validation contract. V1 and v2 cannot coexist.

The payload binds Plan, Candidate, Judgment, Ready, native-v2 Release and closure, Capability-v2, exact resolver/derivation implementation, derivation envelope, core/paired/counterpart/effective graph digests, paired closure, requirement/mapping inventories, every requirement and mapping outcome, completeness digest, mode, findings, support result, operation/authorization, and Plan fingerprint. It also commits the complete core `semantic` object through `semantic_digest`. Admission recomputes that digest and independently rebinds every predecessor commitment against authenticated bytes; recomputing the Plan's self-fingerprint cannot cure a foreign predecessor digest. Structural schema validity alone never admits a record.

References crossing authority boundaries are durable graph-scoped arrays `[candidate_profile_instance_fingerprint,effective_graph_digest,DQI]`. Core requirements, paired requirements, effective graph objects, and owner mappings resolve only through exact domain/kind identity. Counterpart proofs are digest-bound consistency evidence and cannot be referenced or traversed. Renderer/output bindings use exact identities and fingerprints, never paths or resemblance.

Coverage is exactly six profile-owned requirements plus every owner-authored row mapping. For paired-v3, `N == len(decoded.table.rows)`, each row appears once in authored order, and each relationship token is exact. TASK-071 therefore produces seven Plan mapping rows—not a synthetic-fixture count and not 144 per-object outcomes. No invented, omitted, duplicated, reordered, dangling, wrong-domain, or foreign mapping is admitted. Zero mappings fail whenever decoded rows are nonempty.

The completeness object binds inventories separately from outcomes. `supported` is true iff all six plus N outcomes are supported and findings are empty. Foreign Candidate/capability/registry/envelope/graph/Release/profile/rendering/conformance chains, historical TASK-067 authority, or substituted evidence reject.

The governed valid-fixture index freezes independently traversable non-authority predecessor closures of exactly eight records and ten records. The eight-record closure is the six core records plus Capability and Plan and terminates at Plan. The ten-record publication predecessor closure is those same eight records plus Audit and Conformance and terminates at Conformance. Starting at each exact terminal root, every declared predecessor is reachable, every reference resolves, the complete canonical predecessor-record bytes and exact ordered record array are authenticated, exact kind/topology/fingerprint bytes match, and no extra record is present. These closure fixtures test shape and binding only; they are not issued lifecycle records and do not consume or re-admit the TASK-071 Candidate.

Plan-v2 authorizes only the compatibility determination and listed expression prerequisites. It does not authorize renderer invocation, artifact acceptance, conformance, Manifest, publication, or distribution. Normative bytes are non-authority fixtures; later production issuance must reconstruct all commitments and persist/reload exact bytes under exclusive planner authority.
