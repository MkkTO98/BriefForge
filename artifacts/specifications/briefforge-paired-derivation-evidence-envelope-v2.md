# BriefForge Paired Interpretation and Derivation-Evidence Envelope 2.0

Status: frozen TASK-076 implementation contract
Schema: `artifacts/contracts/task076/derivation-evidence-envelope.schema.json`
Normative fixture: `artifacts/contracts/task076/task071-derivation-evidence-envelope.json`
Population proof: `artifacts/contracts/task076/task071-derived-populations.json`
Contract: `briefforge:paired-semantic-derivation-evidence:2.0.0`

## Authority boundary

Exact authenticated Candidate/profile bytes remain the sole serialized semantic authority. The paired decoder deterministically interprets only the exact paired-v3 extension tuple. Decoded objects are interpretations of those bytes; the core graph, paired graph, effective graph, counterpart proof, coverage inventories, and persisted envelope are derived evidence. None can independently authorize semantics, replace the Candidate, or be serialized back into it.

A planner may rely on the envelope only after exact profile dispatch, reload of the governed Candidate bytes, reconstruction of every population and digest, exact registry authentication, and canonical-byte equality. A fingerprint alone is insufficient.

## Why v2

TASK-075's architectural v1 field sketch omitted the exact registry identity/digest and explicit decoded object/row commitments required by its own implementation blocker. TASK-076 therefore freezes additive envelope v2 rather than silently overloading v1. V2 preserves every v1 authority separation and commitment while adding: `implementation_contract`, `registry_identity`, `registry_digest`, `decoded_paired_population_digest`, `decoded_paired_object_count`, `decoded_row_count`, exact `counterpart_exclusions`, separate `graph_emission_classifications`, and `rejection_state`. V1 remains an architecture artifact and is not production-schema exact.

## Populations

The schema is closed: no additional fields. Every digest is lowercase SHA-256 using the named domain-separated canonical JSON rule. Every population has one canonical ordering and unique identity scope:

- core nodes/edges: complete registry-constrained BCRP graph, lexicographically sorted by DQI/edge wire; TASK-071 contains 165 core nodes and the frozen BCRP inspector's exact 722 edges, including the paired extension envelope's authority and target edges;
- paired nodes/edges: exact owner decoder output, 8 kinds, canonical DQI/edge order;
- counterpart records: paired-DQI order, exact 144-record bijection for TASK-071, never traversable;
- effective graph: exact concatenation of verified core then paired populations, counterpart digest only;
- requirements: six owner arrays in fixed ordinal order;
- mappings: every decoded table row exactly once in authored order; `mapping_count == decoded_row_count`.

The normative TASK-071 fixture proves `6/76/1/7/14/27/8/5 = 144` paired objects, 144 unique core counterparts, zero mismatches, six requirements, seven owner mappings, and seven Plan rows.

## Counterpart exclusion and graph-emission classification

Paired `Section.order` is the only counterpart exclusion. It is excluded only from counterpart comparison because core array position is nonauthoritative. The paired field remains fully authoritative and byte-committed.

Separately, exact paired-v3 `Provenance.source_snapshot_identity` is classified for graph emission as an owner-typed source token. TASK-071's token does not equal its core EvidenceSnapshot identity, so it remains paired node content and is not promoted into an edge by resemblance. A future value emits a snapshot edge only when exact registry resolution proves an EvidenceSnapshot target. This corrects the overbroad TASK-075 graph-table wording without changing Candidate bytes or counterpart counts; it is not a counterpart-field exclusion.

No other source field is omitted: every field is consumed into a node, edge, attribute, requirement, mapping, or one of these explicit classifications.

## Persistence, chronology, and completeness

The envelope binds exact Candidate identity/fingerprint/profile-byte digest, a closed 12-member extension decomposition (owner, name, version, authority, scope, complete ordered targets, criticality, character, validation contract, preservation, payload contract identity, payload contract version), exact envelope/payload/closure digests, decoder implementation contract/digest, registry identity/digest, all graph and proof populations, all coverage inventories, exact counts, the sole counterpart exclusion, the separate graph-emission classification, complete ordered invariants, operation identity, authorization fingerprint, canonical UTC issuance, and final fingerprint. Canonical bytes have no trailing newline.

Reload must reproduce all fields from governed source bytes. Persistence must be exclusive-create, fsync, reread, byte-compare, and inventory authenticated in a later implementation task. The normative fixture is explicitly non-authority contract test material and cannot issue a verified handle. Governed executable fixtures apply 29 single-field mutations, eleven structural mutations, ten correlated/oracle-substitution mutations, and thirteen schema-shaped record mutations, then run independent invariant checks against immutable fixture authority; generic coverage fixtures exercise N=0 with no obligations and N=1, 7, and 16 with obligations. Structural checks require unique row identities with exact once-only authored-order coverage. The eight-record closure terminates at Plan; the ten-record publication predecessor closure contains the same six core records plus Capability, Plan, Audit, and Conformance and terminates at Conformance. Both require exact ordered record arrays, exact complete canonical record bytes, exact kinds, topology, per-record byte fingerprints, complete reachability from the exact terminal root, and no oracle-hidden extras.

## Rejection

Reject altered Candidate/profile bytes; wrong decoder, implementation, registry identity, registry bytes, profile, or extension family; incomplete/duplicate/omitted paired objects; counterpart mismatch or duplicate target; unexpected exclusion; stale/foreign evidence; authoritative reordering; substituted graph/coverage; unsupported/mixed extension families; mapping/count disagreement; zero mapping with nonempty owner rows; unknown semantic extension data; or noncanonical bytes.
