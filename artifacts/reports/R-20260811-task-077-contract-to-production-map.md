# TASK-077 Contract-to-Production Implementation Map

Status: **PASS — IMPLEMENTABLE BY BOUNDED ADDITIVE OWNERSHIP**
Date: 2026-08-11

## Architectural ruling

No frozen-contract contradiction or missing semantic rule blocks implementation. Generation-8 production behavior is absent but can be added through existing owners without creating a second planner, graph authority, lifecycle, projection, renderer, conformance system, or Manifest authority.

Two conflicts must be corrected additively:

1. `src/briefforge/bcrp_renderer_compatibility_planning_v2.py` is historically named v2 but its accepted production family is still Capability/Plan `1.0.0`. TASK-077 will preserve that historical family and add exact closed generation-8 dispatch in the same planner owner; unknown and mixed families fail closed.
2. The native paired path currently passes native planning through `_legacy_paired_profile_views`. The paired-v3/generation-8 branch must consume verified v2 state directly while historical routes remain unchanged.

The repository checkout is the established production runtime boundary: there is no packaging metadata or installed-resource mechanism. The canonical loader will resolve the project-owned frozen root from the source checkout and will permit no caller-selected root or environment override. Installed-wheel support is not claimed.

## Ownership map

| Frozen requirement | Governing generation-8 artifact | Existing owner / entry point | Required additive implementation | Existing validator authority | Prohibited parallel implementation | Positive/negative tests | Downstream consumer |
|---|---|---|---|---|---|---|---|
| Manifest authentication | `final-contract-byte-manifest.json` | none | `src/briefforge/task076_contracts.py`: authenticate exact manifest identity, ordered 23-entry path/role/profile/length/digest closure, immutable detached documents, domain digests | `tools/validate_task076_contracts.py` remains non-production oracle | direct per-module reads, alternate roots, fixture/report authority | `tests/test_task077_contract_loader.py` | every generation-8 owner |
| Core registry | registry JSON/schema | native BCRP structures plus no registry runtime | `src/briefforge/bcrp/registry.py`: exact 37-kind closed locator dispatcher from authenticated bytes | native BCRP structures and frozen registry | recursive discovery, caller indexes, copied registry | registry/unknown-kind/locator/collision tests | core graph/counterparts/envelope |
| Core graph | derived populations, registry | `bcrp.graph` | add registry-driven generation-8 extraction while preserving generic historical graph API | native graph comparison | second graph module/extension identities as core | exact 165/722 plus substitutions | envelope/Plan |
| Paired decoder | paired Candidate extension and frozen populations | `briefforge_paired_terminal_profile.profile.validate_candidate_paired_semantics` / `_reconstruct_semantics` | exact profile tuple dispatch and immutable ordered decoded inventory reusing existing decoder | paired schema/profile validator | second decoder, arbitrary opaque extension parsing, DTO authority | exact/unknown/mixed/duplicate tests | paired graph/planner |
| Paired graph/effective graph | populations/envelope | no graph emission owner | `src/briefforge/bcrp_paired_semantic_interpretation_v2.py`: 144/590 graph, separated effective graph, exact digests | paired schema topology | core namespace merge, caller effective graph | exact counts, equal-length/foreign substitutions | envelope/Plan |
| Counterpart consistency | populations/envelope | none | same interpretation owner: 144 unique proofs, zero mismatch, only `Section.order` exclusion, nontraversable proof type | authenticated registry + exact Candidate bytes | aliases/nodes/edges/planner references, extra exclusions | field mutations, collision, traversal tests | envelope only |
| Envelope v2 | envelope/schema/validation rules | none | `src/briefforge/bcrp_paired_derivation_evidence_v2.py`: construct, independently verify, serialize, persist, reload from exact authority inputs | authenticated Candidate, decoder, registry, regenerated graphs | schema-shaped/self-consistent envelope admission | frozen 63 fixtures, stale/cross-run persistence | Capability/Plan |
| Capability-v2 | capability record/extension/schema | `bcrp_renderer_compatibility_planning_v2.py` | exact v2 constructor/serializer/admission in existing planner owner with strict family dispatch and independent contract/predecessor rebinding | frozen contract loader + independently generated envelope | second capability module, v1/native conflation, structural-only acceptance | exact bytes and correlated renderer substitutions | Plan/native admission |
| Plan-v2/native planner | Plan record/extension/schema/completeness | same planner module production entry points | exact paired-v3 branch: six requirements, all N owner rows, N equality, graph-scoped refs, independent cross-layer/predecessor rebinding | existing lifecycle/release verifiers plus generation-8 owners | second planner, caller inventories, counterpart traversal | N=0/1/7/16, omissions/duplicates/foreign mappings | native paired admission/projection |
| Fingerprints | all digest-bearing artifacts | BCRP canonical helpers | one generation-8 ASCII-domain-tag/NUL/canonical-byte helper in canonical loader; keep historical domains unchanged | frozen vectors | ad hoc hashes or cross-domain reuse | frozen fingerprint vectors/correlated reclosure | all v2 layers |
| 8-record closure | valid fixtures/Plan contract | paired profile `_verify_exact_paired_plan` and token prefix | exact ordered complete-record rebind to authoritative Candidate/Release/Capability/Plan inputs and fingerprints | release/plan/envelope/capability verifiers | kind-count-only or mutable expected oracle | every record-position foreign/minimal/reorder/topology/root attack | native handle/token |
| 10-record closure | valid fixtures/Plan contract | existing paired Manifest `_predecessor` | retain sole owner; add generation-8 exact prefix/family/fingerprint checks only | existing Audit/Conformance/Manifest verifier | second Manifest/closure authority | complete 10-record foreign/minimal attacks | existing Manifest boundary, not executed here |
| Persistence/reload | envelope/Capability/Plan contracts | projection safe descriptor-based persistence pattern | bounded exclusive-create/fsync/reread/byte-compare APIs in envelope and existing planner owner, using common safe-I/O helper only if extraction reduces duplication | exact authority reconstruction on reload | trusting deserialized DTO/digest/path or projection as Plan authority | residue, symlink, stale, second-write, cross-run tests | native admission |
| Native handle | v2 family/bindings | `bcrp_paired_terminal_admission.NativeBCRPPairedTerminalAdmissionHandle` | exact v2 dispatch and issuer-held v2 state; preserve fieldless/noncopyable/nonserializable one-use handle and historical dispatch | TASK-073/TASK-074 verifiers | second registry/token, raw TASK-067 token exposure | issuer family, replay, expiry, copy, pickle, mixed closure | existing controlled invocation |
| Projection-facing output | Plan bindings | existing paired `projection.py` | no second projection; only revalidate issuer-held v2 commitments before existing projection construction | existing projection verifier | direct projection from Candidate/envelope or new DTO authority | compatibility/binding tests without rendering | existing renderer/conformance chain |

## Bounded implementation slices

1. Loader and immutable contract data.
2. Registry-driven core graph.
3. Paired interpretation, counterpart proof, effective graph.
4. Envelope construction/verification/persistence.
5. Capability-v2 construction/admission/persistence.
6. Plan-v2 planner/admission/closure/persistence.
7. Native-handle exact v2 integration without projection execution.
8. Production-path and adversarial suite, implementation freeze, review, closeout.

Each slice follows RED → observed failure → minimal GREEN → adjacent regression tests. Generation-8 contract bytes are read-only inputs and never regenerated.

## Non-authority boundary

Schemas, valid/invalid fixtures, expected findings, derived populations, envelope examples, reports, and builder/validator tooling remain frozen contract/test material. Production authority derives only from exact TASK-071 Candidate/profile bytes plus independently authenticated project-owned contract definitions and accepted predecessor authorities.

## Phase ruling

PASS. Proceed to TDD implementation. A discovered need to change any generation-8 byte is an immediate architectural stop, not a remediation opportunity.
