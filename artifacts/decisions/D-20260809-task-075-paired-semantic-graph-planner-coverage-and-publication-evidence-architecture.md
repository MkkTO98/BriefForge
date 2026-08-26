# D-20260809 — TASK-075 Paired Semantic Graph, Planner Coverage, and Publication-Evidence Architecture

Status: **CONDITIONALLY ACCEPTED — ARCHITECTURE SELECTED / IMPLEMENTATION NOT READY**
Date: 2026-08-09
Decision owner: BriefForge
Applies to: separately authorized implementation after TASK-075
Does not authorize: production implementation, lifecycle execution, TASK-071 operation, or successor activation

## Decision

Adopt one versioned, profile-dispatched semantic-resolution architecture with:

1. one authoritative serialized Candidate closure with separate core and paired interpretation/validation ownership partitions;
2. an extension-owned paired subgraph reconstructed only by the exact paired profile decoder;
3. a deterministic verified effective graph as a non-authoritative derived view;
4. one existing compatibility planner consuming owner-verified planning material through exact dispatch;
5. a required Plan coverage contract v2 with graph-scoped domain-qualified references, six global outcomes, the complete ordered mapping inventory of cardinality N, and exact paired-closure completeness evidence;
6. persisted graph-derivation evidence that is always reauthenticated against authoritative Candidate bytes;
7. transitive graph and coverage bindings through projection, rendering, Audit, conformance, Manifest, persistence, and reload;
8. a future profile successor for newly authored first-class paired semantics, while preserving the exact paired v3 and TASK-071 bytes.

The effective graph is not a new semantic authority. It is a verified union/index over core and paired source assertions under a named derivation contract.

## Corrected factual basis

Exact TASK-071 contains:

- 0 core renderer requirements;
- 0 core fallbacks;
- 6 paired renderer requirements;
- 7 paired row/relationship mappings;
- 144 paired object identities;
- all 144 local identities mirrored in the traversable core graph;
- 0 dangling identities, 0 L1 findings, and 0 L2 findings when those exact identities are referenced from core objects.

The historical 71 identities and 142 L1 plus 142 L2 findings are valid only for the synthetic nonmirroring fixture. This decision corrects their provenance without rewriting TASK-074 history.

The operative defect is incomplete semantic authority dispatch and Plan coverage, not absence of TASK-071 local identity strings.

## 1. Serialized authority and semantic graph ownership

The exact authenticated canonical `profile.json` bytes are the sole complete serialized Candidate authority. `candidate-semantic.json` is reproducible equality evidence and never an independent authority. Core and paired are disjoint interpretation and validation ownership partitions inside that one Candidate closure; they are not independently admissible serialized authorities. A detached extension payload, decoded DTO, core graph, persisted graph evidence, or derived view cannot independently authorize semantics or publication.

### Core domain

Identity: `briefforge-core-representation-profile@1.0.0`.

Owns BCRP records, traversable core objects, canonical core edges, structural validation, and core canonical bytes/fingerprints. BCRP 1.0 remains frozen.

### Paired domain

Identity: exact paired semantic profile and version, currently `briefforge:representative-paired-terminal-static-html-profile:3.0.0` and its exact semantic-input contract.

Owns paired DTO forms, internal identity/reference validation, authored ordering, semantic attributes, six renderer requirements, an ordered row/relationship mapping for every row, and paired closure fingerprint. Lexical overlap does not transfer ownership to core.

### Verified effective graph

A new `VerifiedEffectiveSemanticGraph` is constructed by one versioned derivation issuer/verifier. It combines independently verified core and paired domain views. Cross-domain counterpart results remain consistency-proof records outside both source graphs; they are not traversable semantic edges.

It is:

- immutable;
- derived;
- bound to exact source bytes and contract versions;
- independently reproducible;
- non-authoritative as a semantic source;
- never serialized back into the Candidate;
- never caller-editable;
- invalid without source reauthentication.

The exact authenticated Candidate/profile bytes remain sole serialized authority. Core and paired decoders retain interpretation sovereignty over their partitions. The derivation issuer is not a semantic authority.

## 2. Identity model

Graph-local identities and durable references are distinct. Literal domains are:

- core: namespace `briefforge:bcrp-core`, version `1.0.0`;
- paired: namespace `briefforge:paired-terminal`, version `3.0.0`.

A DQI canonical value is the four-element JSON array:

```json
["<domain_namespace>","<domain_version>","<object_kind>","<local_identity>"]
```

A durable graph-scoped reference canonical value is:

```json
["<candidate_profile_instance_fingerprint>","<effective_graph_digest>",["<domain_namespace>","<domain_version>","<object_kind>","<local_identity>"]]
```

Canonical JSON everywhere in this decision means UTF-8 bytes from `json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`, with no trailing newline; schemas prohibit non-finite numbers. Text values are exact NFC-normalized Unicode at construction and are never renormalized during verification.

Rules:

- namespace, version, local identity, and kind use exact UTF-8/ASCII byte equality as their owning contracts specify; no Unicode normalization, case folding, or aliases are permitted;
- graph-local uniqueness is over `(domain_namespace, domain_version, local_identity)`;
- internal core/paired graph-construction edges use pre-effective-digest DQIs only and are the sole exemption from durable graph-scoped references, preventing cryptographic self-reference;
- every Plan, coverage, persisted graph handle, and publication-evidence reference is graph-scoped and domain-qualified;
- every unqualified reference crossing an authority boundary rejects; ambiguity is only a diagnostic subtype;
- equal DQI fields in distinct Candidate closures do not establish durable identity equality;
- foreign-Candidate and foreign-graph checks compare the exact Candidate profile-instance fingerprint and effective graph digest before DQI resolution;
- duplicate local identity inside one domain rejects;
- same local identity across domains is neither collision nor equality;
- target kind is loaded from the verified node and compared to the reference; caller-declared kind never overrides it;
- locators, array positions, JSON Pointers, paths, DOM paths, CSS selectors, renderer names, and relationship tokens are never object identities;
- identities embedded in strings become paired-domain graph-local identities only after exact owner/version decoding; the raw string never becomes core-traversable.

### Counterpart consistency proofs

For TASK-071, a counterpart verifier must reproduce exactly 144 one-to-one consistency records:

`CounterpartProof(paired DQI, core DQI, rule_id, result)`

The records are derivation-contract-owned proof data outside both source graph domains. They are not authored semantic edges, aliases, substitutions, reference targets, coverage relations, or traversable paths. They cannot satisfy any semantic reference or planner outcome.

Issuance requires a bijection from all 144 paired objects to 144 distinct eligible core objects under the closed TASK-071 correspondence table below. Matching by local identity is permitted only because this exact derivation contract names it as its candidate key; it is never generic identity equality. The verifier checks owner-defined kind and field rules, authored order, target relations, authority/provenance where mirrored, and rejects missing, extra, duplicated, wrong-kind, nonbijective, or disagreeing candidates as `paired-counterpart-conflict`. A core reference never substitutes for a paired reference.

The counterpart proof policy identity/version and exact inventory digest are bound into derivation evidence.

## 3. Extension decoding

Resolver dispatch requires the exact tuple:

- core extension envelope contract;
- owner namespace;
- extension name;
- extension version;
- scope;
- criticality;
- character;
- preservation policy;
- payload contract identity/version;
- Candidate target and authority references.

The paired decoder must:

1. verify the complete envelope;
2. select one exact supported profile/version;
3. parse bounded canonical JSON with duplicate-member and non-finite-number rejection;
4. require exact root/DTO fields and accepted order semantics;
5. instantiate exact paired types;
6. run all paired invariants;
7. re-encode and prove canonical source equality;
8. reject unknown, ambiguous, duplicate, reordered where order is semantic, surplus, omitted, partially supported, or mixed families;
9. prove every semantic source field is consumed into a node, edge, attribute, requirement, mapping, or explicitly non-semantic field;
10. prove arbitrary opaque extension data cannot enter the graph.

Only the profile owner decoder gives semantic meaning. Generic JSON walking is forbidden.

## 4. Graph construction contract

The exact additive derivation contract is `briefforge:effective-semantic-graph-derivation:1.0.0`. Its graph contract literals are `briefforge:verified-core-semantic-graph:1.0.0`, `briefforge:verified-paired-semantic-graph:1.0.0`, and `briefforge:verified-effective-semantic-graph:1.0.0`. Core graph `domain` is `["briefforge:bcrp-core","1.0.0"]`; paired graph `domain` is `["briefforge:paired-terminal","3.0.0"]`.

### Paired nodes

Required classes:

- section;
- statement;
- table;
- row;
- value;
- qualification;
- provenance;
- obligation.

Each node contains domain-qualified identity, exact kind, owner-governed payload, authority/provenance, collection-order semantics, non-authoritative source locator, and exact extension closure digest.

### Closed paired graph emission

Only owner-authored object references become edges. Typed vocabulary values—classification, evidence role, relationship identity, method, package, transformation, and state—remain committed node attributes and never receive fabricated DQIs.

For each field below, the source pointer is the exact containing-object JSON Pointer, `source_field` is the literal field path shown, `target_kind` is loaded from the verified target, and the emitted edge kind/ordinal are exact:

| Source kind/field | Edge kind | Target domain/kind | Ordinal |
|---|---|---|---|
| Section `children` | `ordered-child` | paired / exact declared child kind | zero-based child index |
| Table `purpose_ref` | `purpose` | paired / Statement | 0 |
| Table `authority_ref` | `authority` | core / ContentAuthority | 0 |
| Table `rows` | `ordered-row` | paired / Row | zero-based row index |
| Statement `authority_ref` | `authority` | core / ContentAuthority | 0 |
| Row `row_statement_ref` | `row-statement` | paired / Statement | 0 |
| Row `raw_value_ref` | `raw-value` | paired / Value | 0 |
| Row `first_difference_value_ref` | `first-difference-value` | paired / Value | 0 |
| Row `qualification_refs` | `qualification` | paired / Qualification | zero-based list index |
| Row `provenance_refs` | `provenance` | paired / Provenance | zero-based list index |
| Value `unit_ref` | `unit` | core / Unit | 0 |
| Value `semantic_type_ref` | `semantic-type` | core / SemanticType | 0 |
| Value `source_ref` | `source` | core / ExternalReference | 0 |
| Value `authority_ref` | `authority` | core / ContentAuthority | 0 |
| Qualification `source_ref` | `qualification-source` | paired / Statement | 0 |
| Qualification `target_ref` | `qualification-target` | paired / verified target kind | 0 |
| Qualification `authority_ref` | `authority` | core / ContentAuthority | 0 |
| Provenance `target_refs` | `provenance-target` | paired / verified target kind | zero-based authored index |
| Provenance `placement_ref` | `placement` | paired / Row or Section | 0 |
| Provenance `source_snapshot_identity` when non-null | `snapshot` | core / EvidenceSnapshot | 0 |
| Provenance `authority_ref` | `authority` | core / ContentAuthority | 0 |
| Obligation `target_refs` | `obligation-target` | paired / verified target kind | zero-based authored index |
| Obligation `placement_ref` | `placement` | paired / Section | 0 |
| Obligation `authority_ref` | `authority` | core / ContentAuthority | 0 |

No other paired edge may be emitted under v1. The Candidate/extension relationship is committed by Candidate fingerprint, extension-envelope digest, and paired graph `source_digest`; it is not an edge because the extension has no semantic node identity. Cross-domain counterpart consistency records are never graph edges. Derived reverse indexes are disposable and non-authoritative.

### Source locators

Locators include Candidate identity, exact extension tuple, SHA-256 of exact canonical paired source bytes, canonical JSON Pointer, and optional source record locator. Locators support diagnostics and reconstruction only. They never resolve Plan references.

### Required companion derivation evidence

Contract: `briefforge:paired-semantic-derivation-evidence:1.0.0`. This is a canonical JSON evidence envelope, not a BCRP record or semantic authority. It is one flat object with exactly these fields and types:

```text
contract: exact contract string
evidence_identity: canonical identity string
issuer_identity: exact `briefforge:paired-semantic-derivation-issuer:1.0.0`
verifier_identity: exact `briefforge:paired-semantic-derivation-verifier:1.0.0`
implementation_digest: lowercase SHA-256
bcrp_profile: [identity_string, version_string]
paired_profile: [identity_string, version_string]
candidate_identity: canonical identity string
candidate_profile_instance_fingerprint: lowercase SHA-256
candidate_profile_byte_digest: lowercase SHA-256
source_locator_identity: canonical storage identity, not a path
extension_tuple: [envelope_contract, owner_namespace, name, version, scope, criticality, character, preservation_policy, payload_contract, target_ref, authority_ref]
extension_envelope_digest: lowercase SHA-256
paired_payload_digest: lowercase SHA-256
paired_closure_digest: lowercase SHA-256
core_graph_digest: lowercase SHA-256
paired_graph_digest: lowercase SHA-256
counterpart_proof_digest: lowercase SHA-256
effective_graph_digest: lowercase SHA-256
requirement_inventory_digest: lowercase SHA-256
mapping_inventory_digest: lowercase SHA-256
mapping_count: nonnegative integer
counts: {core_nodes, core_edges, paired_nodes, paired_edges, counterparts, sections, statements, tables, rows, values, qualifications, provenance, obligations}; every value a nonnegative integer; no other keys
invariant_results: ordered arrays [rule_identity, "pass"] with one entry for every closed invariant in contract order
findings: [] only
operation_identity: canonical identity string
authorization_fingerprint: lowercase SHA-256
issued_at_utc: canonical UTC RFC3339 `YYYY-MM-DDTHH:MM:SSZ`
fingerprint: lowercase SHA-256
```

No nesting or fields beyond those shown are admitted. `fingerprint` is `H("briefforge.task075.derivation-evidence.v1", complete_object_with_fingerprint_member_omitted)`.

Only `briefforge:paired-semantic-derivation-issuer:1.0.0`, using issuer-held verified Candidate closure and exact dispatch registry, may construct it. Callers cannot supply fields, graphs, proofs, counts, or digests. The independent verifier reloads the exact Candidate authority bytes from the bound expected source, reconstructs every commitment, and compares canonical bytes/fingerprint. A copied, caller-created, structurally equivalent, stale, foreign, partially reproduced, wrong-path, or implementation-mismatched envelope rejects. Judgment and Plan may consume its fingerprint only after this independent reproduction; the fingerprint alone is never admissible.

The evidence binds:

- derivation/resolver identity, version, and implementation digest;
- BCRP and paired profile identities/versions;
- Candidate identity and exact fingerprint;
- exact Candidate/profile source-closure fingerprint;
- extension envelope tuple and source digest;
- core graph digest;
- paired graph digest;
- counterpart-map digest;
- global-requirement inventory digest;
- row-mapping inventory digest;
- effective graph digest;
- node, edge, identity, requirement, and mapping counts;
- complete invariant results and zero findings.

Reload must reconstruct from authoritative source bytes and compare. Persisted evidence cannot authorize processing when source bytes, versions, implementation digest, Candidate fingerprint, or any derived digest differs.

### Construction boundary

Only one issuer-controlled function may derive the graph. It accepts exact admitted Candidate bytes or an issuer-held verified closure and an exact dispatch registry. It never accepts caller-supplied nodes, edges, mappings, indexes, or digests. It returns an immutable process-local verified handle plus canonical persisted derivation evidence.

For TASK-071 migration/revalidation, construction occurs before a new Judgment under the successor validation policy. Historical validation is not retroactively changed.

### Binding responsibility split

| Component | Sole responsibility | Explicit prohibition |
|---|---|---|
| Core verifier | Interpret and validate BCRP core bytes | May not decode paired payload or issue Plan conclusions |
| Paired owner decoder/validator | Interpret exact paired bytes; emit paired nodes, owner-authored edges, six requirements, and N ordered mappings where N equals decoded row count | May not issue Plan, capability, or publication authority |
| Counterpart verifier | Evaluate only the closed consistency table below | May not create traversable edges, aliases, substitutions, or coverage |
| Effective-view issuer | Combine already verified outputs into an immutable disposable lookup view | May not add semantics or accept caller graph data |
| Existing compatibility planner | Evaluate renderer capability and issue the one Plan authority | May not reinterpret opaque bytes or invent coverage relations |

No consumer accepts a caller-supplied graph, counterpart map, reverse/coverage index, graph digest, or persisted derivation evidence as authority. Every authority-bearing operation reconstructs or independently verifies the view from exact authenticated Candidate bytes and the exact dispatch registry. A graph digest is only an integrity commitment to reproducible derivation. Persisted evidence can accelerate comparison but cannot by itself reissue a verified handle. Reverse indexes and merged lookup tables are disposable and have no stable source identity.

### Domain-separated byte commitments

All new commitments are lowercase hexadecimal SHA-256 over `ASCII-domain-tag || 0x00 || canonical-bytes`. Literal tags are:

- `briefforge.task075.source-fragment.v1`;
- `briefforge.task075.edge-attributes.v1`;
- `briefforge.task075.requirement-inventory.v1`;
- `briefforge.task075.mapping-inventory.v1`;
- `briefforge.task075.requirement-outcomes.v1`;
- `briefforge.task075.mapping-outcomes.v1`;
- `briefforge.task075.extension-envelope.v1`;
- `briefforge.task075.paired-payload.v1`;
- `briefforge.task075.paired-closure.v1`;
- `briefforge.task075.core-graph.v1`;
- `briefforge.task075.paired-graph.v1`;
- `briefforge.task075.counterpart-proof.v1`;
- `briefforge.task075.effective-graph.v1`;
- `briefforge.task075.planning-completeness.v1`;
- `briefforge.task075.derivation-evidence.v1`;
- `briefforge.task075.capability-declaration.v2`;
- `briefforge.task075.plan-extension.v2`.

Let `H(tag,value)` mean the domain-separated lowercase digest rule above over the canonical JSON bytes of `value`, except paired payload uses exact UTF-8 payload bytes as stated. A `canonical_source_fragment` is the exact JSON value at the bound JSON Pointer in the authoritative canonical `profile.json` object for core, or in the parsed canonical-semantics object for paired; no reconstructed DTO serialization substitutes for it. Edge attributes are the closed object `{"source_pointer": <exact pointer>, "source_field": <literal owning field name>, "target_kind": <literal verified kind>}`.

Exact wire structures:

- core node: `[DQI, record_identity, json_pointer, H("briefforge.task075.source-fragment.v1", canonical_source_fragment)]`;
- paired node: `[DQI, canonical_semantics_json_pointer, H("briefforge.task075.source-fragment.v1", canonical_source_fragment)]`;
- edge: `[source_DQI, edge_kind, ordinal, target_DQI, H("briefforge.task075.edge-attributes.v1", canonical_edge_attributes)]`; `ordinal` is the zero-based owner-authored list position or `0` for singleton fields;
- counterpart field result: `[rule_ordinal, paired_json_pointer, core_json_pointer, normalization_rule_id, paired_canonical_value, core_canonical_value, true]`;
- counterpart record: `[paired_DQI, core_DQI, object_kind, rule_set_identity, H("briefforge.task075.source-fragment.v1", paired_fragment), H("briefforge.task075.source-fragment.v1", core_fragment), [field_results...]]`.

Node inventories sort lexicographically by canonical DQI bytes. Edge inventories sort by `(canonical source DQI bytes, UTF-8 edge_kind bytes, ordinal, canonical target DQI bytes, attributes digest)`. Field results follow the closed correspondence-table row and field order. Counterpart records sort lexicographically by canonical paired DQI bytes. No insertion order, filesystem order, dictionary order, locator path spelling, or display text affects ordering except where an exact owner-authored ordinal is explicitly encoded.

The core graph canonical object has exactly: `contract`, `candidate_profile_instance_fingerprint`, `domain`, `nodes`, `edges`, `source_digest`. Core `source_digest` is `H("briefforge.task075.source-fragment.v1", parsed_complete_profile_json_object)`. Core nodes/edges are the complete DQI-lifted output of frozen `briefforge:bcrp-graph:1.0.0` reference discovery: one node for every identity-bearing core object and one edge for every exact reference occurrence returned by that frozen contract; no additional inference is permitted. Its source pointer, field, kind, and ordinal are the exact occurrence locator and list position returned/reproduced by the frozen inspector.

The paired graph has the same six fields. Paired `source_digest` is SHA-256 over `briefforge.task075.paired-payload.v1 || 0x00 || exact payload.canonical_semantics UTF-8 bytes`; its nodes and edges are exactly the closed emission contract above. The effective graph object has exactly: `contract`, `candidate_profile_instance_fingerprint`, `core_graph_digest`, `paired_graph_digest`, `counterpart_proof_digest`, `nodes` (concatenated core then paired sorted inventories), and `edges` (concatenated core then paired sorted inventories). Counterpart records are committed by digest but never inserted as nodes/edges.

| Commitment | Exact canonical bytes |
|---|---|
| Candidate serialized authority | exact canonical `profile.json` bytes under the existing profile-instance fingerprint contract |
| Candidate profile instance | existing profile fingerprint input; not redefined |
| Extension envelope | complete extension-envelope subdocument |
| Paired payload | exact UTF-8 bytes of `payload.canonical_semantics`, not JSON reserialization |
| Paired decoded closure | paired-owner canonical re-encoding |
| Core graph | canonical core graph object above |
| Paired graph | canonical paired graph object above |
| Counterpart proof | ordered counterpart-record JSON array above |
| Effective graph | canonical effective graph object above |
| Planning completeness | canonical planning-completeness object above |
| Derivation evidence | closed evidence envelope with its final fingerprint field omitted |

`candidate-semantic.json` is excluded from Candidate authority. Authored provenance remains paired/core semantic data; source locators and evidence filenames remain diagnostic only and grant no authority.

### Closed paired-reference resolution table

| Paired source field | Resolution class | Exact target rule |
|---|---|---|
| `Section.children[].target_ref` | paired graph | target kind is exactly `child.kind`; section/statement/table/provenance/obligation only; exact ordered resolution |
| `Statement.authority_ref` | core partition | exact content-authority object |
| `Statement.display_classification` | typed external vocabulary or null | never inferred as object identity |
| `PairedTable.purpose_ref` | paired graph | exact statement |
| `PairedTable.authority_ref` | core partition | exact content authority |
| column identities/headings | paired profile tokens | fixed ordered vocabulary, not object refs |
| `PairedRow.row_statement_ref` | paired graph | exact statement |
| row raw/first-difference refs | paired graph | exact values with required transformation states and row relationship |
| row qualification/provenance refs | paired graph | exact qualification/provenance objects, ordered and nonborrowed |
| row classification/evidence-role refs | governed external vocabulary | exact typed identifiers; not paired/core object refs |
| row relationship identity | paired profile token | unique typed token; not object identity |
| `QualificationEdge.source_ref` | paired graph | exact statement |
| qualification target | paired graph | exact statement, value, or table; kind/order contract enforced |
| qualification authority | core partition | exact content authority |
| `Obligation.target_refs` | paired graph | exact paired identity set under authored order |
| obligation placement | paired graph | exact section that consumes the obligation |
| obligation authority | core partition | exact content authority |
| provenance targets | paired graph | exact paired identities under `exact-targets` |
| provenance placement | paired graph | exact consuming row or section |
| provenance snapshot | core partition or null | exact evidence snapshot when snapshot form is used |
| provenance source locator | diagnostic text or null | never an identity |
| provenance package identities | governed external package tokens | never inferred as graph identities |
| provenance authority | core partition | exact content authority |
| value unit/semantic-type/source/authority refs | core partition | exact unit, semantic type, external reference, and content authority respectively |
| value method/package/relationship/transformation | paired/external typed tokens | exact owner vocabulary; not graph identities unless a future version says so |
| root evidence/external/content-authority inventories | core partition anchors | each exact identifier resolves to its required core kind |

Every missing, ambiguous, foreign, wrong-kind, wrong-domain, surplus, duplicated, or lexically inferred target rejects. Owner-authored intra-domain references remain intra-domain. Paired-owner assertions that exactly name core authorities, units, semantic types, external references, or evidence snapshots become typed cross-domain effective-view edges whose semantic ownership remains with the paired source assertion and whose target interpretation remains with the core verifier. They never transfer authority or permit reverse substitution. Counterpart consistency records remain nontraversable and are not edges.

### Closed TASK-071 counterpart consistency table

The candidate key is exact local identity plus expected kind. Extra core fields are permitted only where this table does not claim equality; paired-only fields retain paired authority and are never backfilled from core.

| Paired kind | Eligible core object | Required mirrored equality/transform | Explicit paired-only semantics |
|---|---|---|---|
| Section | Candidate `sections[]` | id, title, ordered child target refs | paired `order`, child kinds, and exact composition validation remain paired-owned; core canonical section-array position is not a counterpart field |
| Statement | Candidate `statements[]` | id, text, `role == posture`, authority ref | display classification and paired role policy; core communication/purpose/upstream fields remain core-only |
| Table | Candidate `exhibits[]` | id; paired columns/headings equal core columns/headings after exact paired-to-core index permutation `(4, 2, 3, 0, 1)` | paired purpose resolves to its paired Statement/core-Statement counterpart; core Exhibit purpose remains separately core-owned; authority and paired table profile remain paired-only |
| Row | table `case_bindings[]` | id, order, relationship id/label, raw ref == primary ref, first-difference ref == comparison ref | row statement, classification/evidence role, qualification/provenance refs |
| Value | Material `values[]` | id, state, coefficient string/int equivalence, scale, lexical form, unit/type/source/authority, method, transformation/state, aligned period/count, package id | relationship identity and paired decimal/row ownership rules |
| Qualification | Candidate `relations[]` | id, kind, source, target, authority, target order == declared target order | paired closure/order validation |
| Provenance | Material `provenance[]` | id, citation, authority, exact target set; core canonical order may differ | paired target order, commit/snapshot/locator/package/target-rule/placement closure |
| Obligation | Candidate `obligations[]` | id, kind, exact target set, authority; core canonical order may differ | paired target order, placement, and paired consumption closure |

The corrected rules were executed read-only against the exact TASK-071 bytes and produced `6/76/1/7/14/27/8/5`, total 144, with zero mismatches and exact table permutation `(4,2,3,0,1)`.

#### Executable counterpart rule-set `briefforge:paired-core-counterpart-proof:1.0.0`

Let `rC` and `rM` be the unique `/records/{index}` positions whose exact identities are the Candidate and Material records. Let `i` be the zero-based owner-authored index in the named array. Paired bases are `/sections/{i}`, `/statements/{i}`, `/table`, `/table/rows/{i}`, `/values/{i}`, `/qualifications/{i}`, `/provenance/{i}`, `/obligations/{i}`. Core bases are `/records/{rC}/semantic/sections/{i}`, `/records/{rC}/semantic/statements/{i}`, `/records/{rC}/semantic/exhibits/0`, `/records/{rC}/semantic/exhibits/0/case_bindings/{i}`, `/records/{rM}/semantic/values/{i}`, `/records/{rC}/semantic/relations/{i}`, `/records/{rM}/semantic/provenance/{i}`, `/records/{rC}/semantic/obligations/{i}`. Objects are paired by exact identity and expected kind; the core index in a base is the matched object's actual unique index, not assumed equal to the paired index.

Normalization rule literals:

- `EXACT_JSON_V1`: compare canonical JSON values byte-for-byte;
- `ORDERED_REF_ARRAY_V1`: compare exact arrays in authored order;
- `SORTED_UTF8_SET_V1`: require uniqueness, sort strings by UTF-8 bytes, compare arrays;
- `SCALED_INTEGER_DECIMAL_V1`: read paired aggregate `{coefficient,scale}` and core aggregate `payload.{coefficient,scale}`; require paired coefficient/scale integers and core coefficient a canonical integer string plus core scale an integer; require equal scales and equal integer coefficient values; emit the same closed object `{"coefficient":"<canonical integer string>","scale":<integer>}` for both canonical outputs; no float or JSON-number conversion is permitted;
- `TABLE_COLUMN_ID_PERMUTE_4_2_3_0_1_V1`: project the core `column_ids` string array in index order `(4,2,3,0,1)` and compare with exact paired `column_identities`;
- `TABLE_HEADING_PERMUTE_4_2_3_0_1_V1`: project the core `headings` string array in index order `(4,2,3,0,1)` and compare with exact paired `column_headings`.

Closed field rules (the listed order is the `rule_ordinal`; gaps are forbidden):

| Ordinals | Kind | Paired relative pointer → core relative pointer | Normalization |
|---|---|---|---|
| 0–2 | Section | `identity→id`; `title→title`; aggregate `children→children` | `EXACT_JSON_V1`; `EXACT_JSON_V1`; `ORDERED_REF_ARRAY_V1` after projecting the complete core children array to strings |
| 3–6 | Statement | `identity→id`; `text→text`; `role→posture`; `authority_ref→authority_ref` | `EXACT_JSON_V1` each |
| 7–9 | Table | `identity→id`; `column_identities→column_ids`; `column_headings→headings` | rule 7 `EXACT_JSON_V1`; rule 8 `TABLE_COLUMN_ID_PERMUTE_4_2_3_0_1_V1`, with paired canonical value the complete `column_identities` array and core canonical value the complete permuted `column_ids` array; rule 9 `TABLE_HEADING_PERMUTE_4_2_3_0_1_V1`, with paired canonical value the complete `column_headings` array and core canonical value the complete permuted `headings` array |
| 10–15 | Row | `identity→id`; `order→order`; `relationship_identity→relationship_identity`; `relationship_label→relationship_label`; `raw_value_ref→primary_ref`; `first_difference_value_ref→comparison_ref` | `EXACT_JSON_V1` each |
| 16–30 | Value | `identity→id`; `value_state→value_state`; aggregate `{coefficient,scale}→payload`; `scale→payload.scale`; `lexical_representation→lexical_representation`; `unit_ref→unit_ref`; `semantic_type_ref→semantic_type_ref`; `source_ref→source_ref`; `authority_ref→authority_ref`; `method_ref→method`; `transformation_identity→transformation`; `transformation_state→transformation_state`; `aligned_period→aligned_period`; `aligned_count→aligned_count`; `package_identity→package_id` | ordinal 18 uses `SCALED_INTEGER_DECIMAL_V1`; all others `EXACT_JSON_V1` |
| 31–36 | Qualification | `identity→id`; `kind→kind`; `source_ref→source_ref`; `target_ref→target_ref`; `authority_ref→authority_ref`; `target_order→declared_target_order` | `EXACT_JSON_V1` each |
| 37–40 | Provenance | `identity→id`; `citation→citation`; `authority_ref→authority_ref`; aggregate `target_refs→target_refs` | first three `EXACT_JSON_V1`; final `SORTED_UTF8_SET_V1`; paired authored target order remains paired-owned and is separately committed by the source-fragment digest |
| 41–44 | Obligation | `identity→id`; `kind→kind`; aggregate `target_refs→target_refs`; `authority_ref→authority_ref` | identity/kind/authority `EXACT_JSON_V1`; targets `SORTED_UTF8_SET_V1`; paired authored target order remains paired-owned |

For each field result, actual full JSON Pointers replace the relative paths above. An `aggregate` rule uses the exact containing-object base pointer as its paired pointer and names the closed member selection in its literal normalization rule; its paired canonical value is the normalized aggregate output. Paired/core canonical values are the exact normalized outputs. Fragment digests commit every paired-only/core-only field not compared. Any missing/surplus compared field, duplicate identity, invalid decimal token, nonunique set member, noncanonical source, unmatched object, or extra counterpart record rejects.

The proof must establish exactly `6 section + 76 statement + 1 table + 7 row + 14 value + 27 qualification + 8 provenance + 5 obligation = 144` bijective records for TASK-071. This is a TASK-071 migration fact, not a universal paired-v3 cardinality invariant.

## 5. Planner behavior

There remains one public compatibility planner and one Plan authority.

### Closed pre-planning dispatch

Classification occurs before the current core material extractor may interpret empty arrays:

| Class | Exact condition | Dispatch |
|---|---|---|
| Core-only | no recognized renderer-semantic extension authority; core requirements/fallbacks remain sole inventory | frozen core planner/verifier behavior |
| Paired-v3 | exactly one exact required paired-v3 envelope; empty core renderer requirements/fallbacks; no second renderer-semantic family | paired owner decoder, effective-view verifier, capability v2, Plan v2 |
| Unknown semantic | any unknown required or optional extension that claims or may carry renderer semantics | block `unknown-renderer-semantic-family` |
| Mixed | paired-v3 plus nonempty core renderer authority, duplicate/multiple paired versions, or any second renderer-semantic family | reject `mixed-requirement-authority` |
| Unknown nonsemantic | exact classifier proves no semantic role and an exact named byte-preservation contract applies | preserve under that contract; otherwise block |

Empty core arrays do not mean no renderer requirements after paired dispatch. Future composition requires an explicit new versioned contract.

### Six global requirement outcomes

The exact paired inventory is:

1. renderer identity = `briefforge:representative-paired-static-html-renderer:1.0.0`;
2. media type = `text/html;charset=utf-8`;
3. output count = `1`;
4. asset count = `0`;
5. table count = `1`;
6. column count = `5`.

These are profile-owned requirement keys, not fabricated Candidate object identities. Requirements and capability declarations remain separate authorities.

The frozen TASK-067 capability declaration v1 is historically preserved but cannot truthfully express all six outcomes or typed mapping support. New paired planning therefore requires an additive renderer-owner declaration `briefforge:renderer-capability-declaration:2.0.0`, under exact extension version `2.0.0`.

Its canonical payload is one object with exactly: `contract` (the exact declaration contract); `declaration_identity`; `renderer_identity`; `implementation_identity`; `implementation_digest`; `owner_identity`; `owner_role`; `profile` as `[identity,version]`; `media_types` as a nonempty unique ordered string array; integer `output_count`, `asset_count`, `table_count`, and `column_count`; `mapping_capability` as the closed object `{"contract":"briefforge:paired-row-relationship-static-table:1.0.0","profiles":[[profile_identity,profile_version]],"mode":"static"}`; `operation_identity`; `authorization_fingerprint`; `storage_identity`; `issued_at_utc`; and `fingerprint`. Identity/digest/time types follow the derivation-evidence rules above; counts are nonnegative exact integers. No other field or nested key is admitted. `fingerprint` is `H("briefforge.task075.capability-declaration.v2", complete_payload_with_fingerprint_member_omitted)`.

Only `briefforge:renderer-capability-declaration-issuer:2.0.0`, under an exact BriefForge renderer-owner authorization tuple and exclusive canonical persistence boundary, may construct the record and extension. Its verifier independently reloads canonical bytes, authenticates issuer provenance/authorization, implementation digest, storage identity, and fingerprint, and rejects caller-created, copied, stale, foreign, substituted, structurally equivalent, or unsupported declarations. A field naming the owner is never authorization.

Closed evaluation table:

| Requirement | Required renderer-owner v2 claim | Planner comparison | Failure |
|---|---|---|---|
| renderer | exact renderer identity | byte equality | `renderer-identity-unsupported` |
| media-type | ordered supported media type contains exact value | exact token membership | `media-type-unsupported` |
| output-count | exact output count claim `1` | exact integer equality | `output-count-unsupported` |
| asset-count | exact asset count claim `0` | exact integer equality | `asset-count-unsupported` |
| table-count | exact table count claim `1` | exact integer equality | `table-count-unsupported` |
| column-count | exact column count claim `5` | exact integer equality | `column-count-unsupported` |
| each paired row mapping | exact supported mapping contract `briefforge:paired-row-relationship-static-table:1.0.0`, exact paired profile support, and static mode | row DQI resolves; relationship token is owner-decoded; contract/profile/mode equal | `mapping-expression-unsupported` |

A requirement, successful render, renderer name, projection profile, or paired-owner assertion can never stand in for renderer-owner capability evidence. The planner alone compares requirement and support authorities and records each outcome.

### Complete ordered mapping outcomes; TASK-071 has seven

For every paired-v3 Candidate, `N == len(decoded.table.rows)`, `1 <= N <= 16`, and the authoritative mapping inventory is exactly `tuple((row.identity, row.relationship_identity) for row in decoded.table.rows)` in authored order. TASK-071 has N=7, and its exact inventory is:

1. `row:T031-DNK-private-credit-broad-money` → `T031-DNK-private-credit-broad-money`;
2. `row:T033-NOR-fossil-nonhydro-renewables` → `T033-NOR-fossil-nonhydro-renewables`;
3. `row:T035-C1-NOR-life-expectancy-under5-mortality` → `T035-C1-NOR-life-expectancy-under5-mortality`;
4. `row:T035-C1-NOR-nonhydro-renewables-under5-mortality` → `T035-C1-NOR-nonhydro-renewables-under5-mortality`;
5. `row:T035-C1-NOR-fossil-under5-mortality` → `T035-C1-NOR-fossil-under5-mortality`;
6. `row:T036-SWE-private-credit-mobile-subscriptions` → `T036-SWE-private-credit-mobile-subscriptions`;
7. `row:T038-DNK-agricultural-land-private-credit` → `T038-DNK-agricultural-land-private-credit`.

Exact outcome wires under `briefforge:renderer-compatibility-plan:2.0.0` use zero-based ordinals:

- requirement outcome: `[ordinal, requirement_key, expected_owner_value, capability_contract, capability_fingerprint, capability_claim_key, actual_capability_claim_value, policy_rule_id, status, failure_code]`;
- mapping outcome: `[ordinal, row_GraphScopedReference, relationship_identity, "briefforge:paired-row-relationship-static-table:1.0.0", capability_contract, capability_fingerprint, actual_mapping_capability_claim, "mapping-expression-exact-v1", status, failure_code]`.

`status` is exactly `"supported"` or `"unsupported"`. `failure_code` is `null` for supported outcomes and the exact failure code from the closed evaluation table for unsupported outcomes. `actual_capability_claim_value` is always the complete canonical claim value: renderer string, complete ordered media-type array, or integer cardinality. `actual_mapping_capability_claim` is the closed object with exactly `contract`, `profiles`, and `mode`; it is never reduced to a caller-selected match.

The six requirement key/claim key/policy id/expected owner value tuples in ordinal order are exactly: `["renderer","renderer_identity","renderer-exact-v1","briefforge:representative-paired-static-html-renderer:1.0.0"]`; `["media-type","media_types","media-type-member-v1","text/html;charset=utf-8"]`; `["output-count","output_count","integer-text-equality-v1","1"]`; `["asset-count","asset_count","integer-text-equality-v1","0"]`; `["table-count","table_count","integer-text-equality-v1","1"]`; `["column-count","column_count","integer-text-equality-v1","5"]`. The owner values are exact strings from `RENDERER_REQUIREMENTS`; count policies parse those canonical decimal-integer strings and compare to capability integers.

Owner inventory commitments and planner outcome commitments are distinct. Requirement inventory bytes are the exact six owner arrays `[ordinal, requirement_key, expected_owner_value]`; mapping inventory bytes are the exact N owner arrays `[ordinal, row_DQI, relationship_identity]`. Derivation evidence uses only `requirement-inventory.v1` and `mapping-inventory.v1`. Planning uses `requirement-outcomes.v1` and `mapping-outcomes.v1` over the complete outcome arrays.

The canonical planning-completeness object contract is exactly `briefforge:planning-completeness-evidence:1.0.0` and has exactly these field names: `contract`, `candidate_profile_instance_fingerprint`, `release_fingerprint`, `capability_fingerprint`, `derivation_evidence_fingerprint`, `effective_graph_digest`, `paired_closure_digest`, `requirement_inventory_digest`, `mapping_inventory_digest`, `requirement_outcomes_digest`, `mapping_outcomes_digest`, `requirement_outcomes`, `mapping_outcomes`, `mapping_count`, `findings`, `supported`. Inventory digests bind owner arrays; outcome digests bind outcome arrays under their distinct literal tags. `mapping_count` equals N.

A finding wire is `[scope_ordinal, outcome_ordinal, scope, subject, failure_code]`, where requirement scope is `0`, mapping scope is `1`, `scope` is exactly `"requirement"` or `"mapping"`, and `subject` is the requirement key or row GraphScopedReference. Findings contain exactly one entry for each unsupported outcome, ordered by `(scope_ordinal, outcome_ordinal)`, with no extra entries. `supported` is true exactly when every outcome is supported and `findings == []`; otherwise it is false.

The row is a paired-domain identity. The relationship value remains a typed paired-profile token unless a future profile makes it an object identity. Each outcome binds row closure, typed relationship, order, capability evidence, expression rule, and effective graph digest.

### Complete planning coverage

The paired-v3 owner contract already defines the complete planning inventory: six exact global renderer requirements and N exact ordered row/relationship mappings, where N equals the decoded row count. The new planner must reproduce those inventories from exact decoded source bytes and bind them to the paired semantic closure, graph, Candidate, capability evidence, and Plan. For TASK-071 N=7. No implementation may invent a per-object relation between the 144 TASK-071 semantic objects and its 13 planning outcomes; paired v3 does not author such a relation, and manufacturing one would create a shadow ontology.

Completeness is proved jointly and without weakening:

1. paired-owner decode consumes every accepted source field and validates the complete decoded semantic closure; TASK-071 has 144 objects;
2. counterpart consistency proves the TASK-071 mirrored representation under the closed table but supplies no coverage;
3. the requirement inventory equals the exact six owner-authored pairs;
4. the mapping inventory equals the exact N owner-authored pairs in authored order and consumes every paired row exactly once;
5. every mapping row is resolved by a graph-scoped paired-domain reference and its relationship is the exact owner-typed token;
6. the renderer capability declaration supports every required outcome;
7. Plan completeness evidence binds the full paired closure digest, graph digest, six outcomes, all N mapping outcomes, and zero findings.

Compatibility fails for any omitted, surplus, duplicated, reordered, dangling, wrong-domain, foreign, unsupported, or substituted inventory item. Paired v3 has no admitted degraded fallback. Zero mappings fail because the exact paired owner inventory is nonempty.

## 6. Plan-reference behavior and versioning

Do not reinterpret Plan v1. Retain the existing `RendererCompatibilityPlanRecord` kind and its place in the eight-record bundle, but require exactly one additive successor extension tuple for new paired admissions:

- owner namespace `briefforge-renderer-compatibility-planning`;
- name `renderer-compatibility-plan`;
- version `2.0.0`;
- validation contract `briefforge:renderer-compatibility-plan:2.0.0`;
- required, semantic, verbatim-preserved character;
- exact planning authority reference and exact Candidate/Release/capability targets;
- no v1 Plan extension and no second Plan-family extension in the same record.

The v2 extension payload is one canonical object with exactly these field names and shapes:

```text
contract: exact `briefforge:renderer-compatibility-plan:2.0.0`
plan_identity: canonical identity
candidate_profile_instance_fingerprint: SHA-256
judgment_fingerprint: SHA-256
ready_fingerprint: SHA-256
release_identity: canonical identity
release_fingerprint: SHA-256
release_closure_digest: SHA-256
capability_identity: canonical identity
capability_fingerprint: SHA-256
capability_contract: exact v2 contract
resolver: [identity,version,implementation_digest]
derivation: [identity,version,implementation_digest]
derivation_evidence_fingerprint: SHA-256
core_graph_digest: SHA-256
paired_graph_digest: SHA-256
counterpart_proof_digest: SHA-256
effective_graph_digest: SHA-256
paired_closure_digest: SHA-256
requirement_inventory_digest: SHA-256
mapping_inventory_digest: SHA-256
requirement_outcomes_digest: SHA-256
mapping_outcomes_digest: SHA-256
requirement_outcomes: exact ordered arrays defined above
mapping_outcomes: exact ordered arrays defined above
planning_completeness_digest: SHA-256
mode: exact `paired-v3-static`
supported: boolean
findings: exact ordered finding arrays defined above
operation_identity: canonical identity
authorization_fingerprint: SHA-256
fingerprint: SHA-256
```

No other field or nested key is admitted. `planning_completeness_digest` is `H("briefforge.task075.planning-completeness.v1", exact planning-completeness object)`. `fingerprint` is `H("briefforge.task075.plan-extension.v2", complete_payload_with_fingerprint_member_omitted)`. The enclosing extension tuple is the exact tuple stated above; historical v1 dispatches only to the frozen v1 verifier and new paired admission requires v2.

Only the exact versioned successor entry point of the existing compatibility planner may construct the entire Plan record, v2 extension, outcome inventories, completeness evidence, and fingerprint. Callers cannot attach, replace, precompute, or supply outcomes, graph/evidence digests, completeness claims, or extension bytes. The independent Plan-v2 verifier reloads authenticated Candidate, Release, capability-v2, and companion derivation bytes and reproduces all six plus N outcomes and every commitment before accepting the canonical Plan bytes.

It binds:

- Candidate, Judgment/Ready, Release, and capability identities/fingerprints;
- exact Release closure bytes;
- paired profile/resolver/derivation identities and versions;
- graph derivation evidence fingerprint;
- core, paired, counterpart, and effective graph digests;
- source closure fingerprint;
- six global outcomes;
- complete ordered mapping outcomes of cardinality N; for TASK-071, N=7;
- exact paired semantic closure digest and exact inventory-completeness proof;
- zero unresolved findings;
- final compatibility result and Plan fingerprint.

Verification rejects unqualified, wrong-domain, wrong-kind, dangling, foreign-Candidate, stale-graph, stale-evidence, substituted, structurally equivalent but differently authoritative, locator-based, reordered, missing, surplus, or duplicated references and outcomes. Release A/Plan B remains rejected.

Historical Plan v1 may remain historically verifiable but cannot authorize a new paired admission, projection, rendering, conformance, or Manifest under the successor policy.

## 7. Publication-evidence continuity

Required chain:

Candidate exact bytes/fingerprint → graph derivation/revalidation → independently authorized Judgment → Ready → native-v2 Release → Plan coverage v2 → paired admission → projection → rendering → derived Audit → actual conformance → derived Conformance record → Manifest → persisted reload and full reauthentication.

Each transition binds the effective graph and coverage directly or through a fingerprint whose domain covers them.

Every changed persisted evidence envelope, fingerprint domain, authorization tuple, or admission verifier uses an exact additive successor identity/version and exact dispatch. Frozen BCRP/TASK-067 record and DTO bytes, projection, renderer, conformance record, Manifest record, and their historical fingerprints remain byte-identical and verifiable only under their original tuples. No successor requirement is read back into a frozen object.

### Exact successor dispatch and binding matrix

| Boundary | Frozen object treatment | Required successor companion/entry point | Mixed/unknown behavior |
|---|---|---|---|
| Candidate | exact TASK-071 bytes unchanged | derivation evidence 1.0 | mismatch blocks |
| Judgment | existing `ValidationJudgmentRecord` shape and verifier unchanged | `judgment-graph-assessment-evidence:1.0.0`, exclusively issued by independent Judgment authority, binds exact Judgment bytes/fingerprint plus derivation evidence | predecessor/successor evidence mixing blocks |
| Ready | existing `ReadyPresentationPackageRecord` shape/verifier unchanged | `ready-graph-continuity-evidence:1.0.0` binds exact Ready, Candidate, Judgment-assessment, and derivation evidence | missing/duplicate/foreign blocks |
| Release | native-v2 Release record/verification unchanged | `native-v2-release-graph-continuity-evidence:1.0.0` binds exact Release closure and Ready continuity evidence | no mutation of native-v2 semantics |
| Capability | frozen v1 historical only | capability declaration/issuer/verifier 2.0 | v1 cannot satisfy v2; coexistence blocks |
| Plan | existing Plan record kind, v1 historical only | exact Plan extension/planner/verifier 2.0 | exactly one Plan family; mixed blocks |
| Native admission | frozen v1 issuer rejects v2 | successor admission issuer/verifier/registry/wrappers 2.0 reusing the retained opaque-handle design | exclusive tuple dispatch |
| Projection | frozen paired projection bytes remain verifiable | `projection-graph-binding-evidence:1.0.0` binds Plan v2, derivation, source closure, exact projection bytes/fingerprint | foreign/stale blocks |
| Invocation/Audit | frozen renderer and record shapes remain | invocation evidence 2.0 and sole Audit derivation evidence/issuer 2.0 bind graph/Plan/projection/artifact | predecessor evidence blocks |
| Conformance | frozen assessor/record historical path remains | actual assessment evidence 2.0 and sole Conformance-record derivation issuer 2.0 bind decisive rendering, graph, Plan, projection, Audit | cross-render/graph blocks |
| Manifest | frozen record shape remains historical | Manifest admission/verifier/evidence/persistence 2.0 requires exact ten-record closure plus all successor companion evidence | old verifier cannot admit successor chain |

The successor admission issuer/verifier/registry/wrapper tuple is additive but exclusive for Plan v2. Frozen issuers reject successor tuples and never mint or validate successor handles. There remains one admitted publication authority route per exact version family, never two interchangeable routes.

### Secure authoring-to-governance bootstrap

The sole bootstrap is `briefforge:accepted-candidate-bootstrap:2.0.0`. It accepts no caller-created `GovernedCandidateAdmission`. Its issuer independently reloads exact canonical Candidate/profile bytes, Candidate semantic equality evidence, fingerprint/inventory, accepted terminal validation and closure evidence, authoring receipt, campaign/attempt ledger, TASK-071 acceptance authority, and derivation evidence from their fixed authenticated locations. It authenticates Candidate identity/fingerprint, accepted attempt identity/status, source hashes, authority tuple, no prior bootstrap operation for the named execution identity, and exact preservation state.

The issuer writes one canonical bootstrap-admission evidence envelope under an authorized execution identity using exclusive create, fsync, reread, and fingerprint verification before returning a process-local fieldless handle. Caller-supplied bytes, paths, hashes, decisions, or semantic fields cannot replace reloaded evidence. The durable ledger records operation identity, authorization fingerprint/scope, source closure, state, timestamps, evidence locator/digest, consumption owner, and recovery classification. Replay or a second operation for the same execution identity rejects.

### Durable state and restart contract

Each authority-bearing boundary—bootstrap, Judgment, Ready, Release, capability, Plan/admission, projection, invocation, Audit, assessment, Conformance record, and Manifest—has a durable operation identity and exact state machine:

`available → reserved → committed → consumed`, with `indeterminate` for interrupted transitions.

- precommit interruption may retry only the same operation identity after proving no commit;
- committed evidence is reread and independently reproduced before consumption;
- postcommit interruption never recreates invocation or publication authority;
- a fresh process-local handle is reconstructed only from durable evidence proving the same unconsumed resumable state;
- consumed state is terminal;
- partial writes, orphan artifacts/evidence, conflicting ledgers, missing fsync proof, stale reservation, duplicate operation, and uncertain commit classify indeterminate and block;
- each stage defines exclusive-create destination, atomic commit point, source/target digest set, orphan cleanup authority, and exact resume command/evidence.

Crash tests are required immediately before and after every commit and consume point, including cross-run replay and postcommit restart.

### Candidate/Judgment/Ready

Companion persisted graph-derivation evidence binds the unchanged Candidate and effective graph. It is not a new BCRP record kind, Candidate authority, or lifecycle stage. The independently authorized Judgment authority consumes the exact reauthenticated evidence under `judgment-graph-assessment-evidence:1.0.0`, issues the existing exact `ValidationJudgmentRecord`, then exclusively persists companion assessment evidence binding the Judgment bytes/fingerprint to the derivation evidence and authorization. Ready remains the existing record and is accompanied by exact continuity evidence. No frozen verifier semantics are mutated.

### Release/Plan/admission

Release remains the exact native-v2 object and gains only independently verified continuity evidence outside the record. Plan embeds exact Release closure and complete graph/coverage evidence. The exact successor admission issuer/verifier/registry/wrappers 2.0 verifies Plan v2 and all continuity evidence before creating a fresh process-local handle under the retained opaque-handle architecture. No prior handle is reused. The handle remains fieldless, noncopyable, nonserializable, registry-bound, single-use, and usable only through native wrappers. Frozen TASK-067/native-v1 tokens and issuers remain historical and cannot accept successor tuples.

### Projection/rendering

The frozen projection and renderer outputs remain byte-compatible. The sole successor projection-binding issuer independently verifies Plan v2 and graph/coverage evidence, constructs/reauthenticates the projection, and commits canonical binding evidence. Controlled invocation first reserves one operation, then commits artifact bytes plus raw invocation evidence binding exact projection, renderer/implementation digest, native authorization operation, artifact digest/length/type/path, graph, coverage, and Plan. Commit occurs before consumption is acknowledged; uncertain commit blocks.

### Audit

Invocation evidence cannot contain an Audit. After artifact and raw invocation evidence commit, the sole `audit-derivation-issuer:2.0.0` independently reloads them, exact projection/Plan/graph/coverage, renderer implementation, Release/Ready, paths, and filesystem facts and derives the unchanged `GeneratedArtifactAuditRecord` plus successor Audit-binding evidence. Caller-authored or precomputed Audit semantics reject.

### Conformance

Conformance evidence cannot contain a Conformance record. A separately authorized assessor independently reparses committed decisive HTML against a reauthenticated exact paired projection and commits raw assessment evidence. Only after that commit may the sole `conformance-record-derivation-issuer:2.0.0` reload assessment evidence and exact Audit and derive the unchanged `SemanticArtifactConformanceRecord` plus successor binding evidence. Artifact, graph, coverage, Plan, projection, invocation, assessor implementation, authorization, and semantic report all cross-bind.

### Ten-record assembly and Manifest

The sole `publication-predecessor-assembler:2.0.0` accepts no caller-provided bundle. It starts from the authenticated Candidate-scoped bootstrap/execution identity, follows fixed persisted stage locators in the durable ledger, independently reloads/reproduces all six core records plus capability, Plan, Audit, and Conformance, and reproduces all companion-evidence bindings. It emits the exact ten-record predecessor closure only after unique identity/kind/order and byte/fingerprint closure verification.

Manifest successor admission accepts only that assembler output, all independently reloaded companion evidence, exact artifact inventory, and external commitments. The sole Manifest issuer/verifier/persistence path commits the unchanged Manifest record plus successor admission evidence. Coverage substitution, graph substitution, conformance from another rendering, caller-manufactured predecessor evidence, alternate paths, or partial predecessor selection rejects.

### Persistence/reload/recovery

All persisted evidence is canonical, exclusively created, fsynced, reread, independently reproduced, and bound to fixed Candidate/execution-scoped locators. Valid canonical reload must succeed; stale, altered, foreign, unsupported-version, wrong-path, partially written, or nonreproducible reload fails. The stage-specific durable state/restart contract above governs all handles and commits.

## 8. Compatibility and frozen history

Remain frozen and unchanged:

- BCRP 1.0 model, graph, structure, canonicalization, and historical fingerprints;
- TASK-060 and TASK-062 production contracts and objects;
- paired v3 semantic input, frozen TASK-067 capability, projection, renderer, conformance, and Manifest contracts except through explicit versioned successors;
- exact TASK-071 Candidate/profile/inventory/receipt/fingerprint bytes;
- historical Release/Plan objects and their historical verification meaning;
- TASK-069 consumed/unavailable/unaccepted evidence;
- TASK-051 inactive historical state;
- retained TASK-074 opaque native-handle containment.

Historical compatibility cannot become native authority. Legacy/frozen objects may be interpreted only under their historical contracts and cannot satisfy successor coverage without new, exact, versioned evidence.

## 9. TASK-071 migration and eligibility ruling

The exact authenticated TASK-071 Candidate contains sufficient authoritative information for byte-preserving derivation. It does not require reauthoring.

Required before any new lifecycle:

- exact paired-v3 resolver implementation;
- complete 144-object subgraph and counterpart proof;
- six requirement and seven mapping inventories;
- effective graph and derivation evidence;
- fresh validation/admission under the successor policy;
- independent new Judgment;
- nonvacuous Plan coverage v2.

Ruling:

- Candidate identity remains unchanged;
- Candidate fingerprint remains `b1c29473241648c68dfb7bb737715645b396c149094eeb70cef34feb52fb95b2`;
- existing terminal validation remains historically valid but is insufficient for new paired publication;
- a new governed graph derivation and validation/admission record is required;
- no new Candidate-authoring attempt is consumed;
- TASK-069 remains consumed, unavailable, and unaccepted;
- TASK-071 historical acceptance evidence remains unchanged;
- parsing opaque JSON alone never establishes eligibility;
- TASK-071 remains operationally `NOT READY` until implementation and isolated integration successors pass.

The derivation is lawful only if implementation proves deterministic canonical decode, complete source consumption, profile governance, exact byte/digest binding, provenance, non-loss, collision/omission/substitution resistance, and exact counterpart agreement. Otherwise TASK-071 remains immutable and ineligible. Fallback requires explicit human authorization for a new successor Candidate with fresh Candidate and attempt identities, explicit lineage from TASK-071, a new fingerprint, and exactly one newly consumed cumulative campaign attempt—presumptively attempt 3 if the same campaign accounting continues. It cannot mutate/reconstruct TASK-069 or TASK-071 and creates no automatic publication entitlement.

## 10. Rejected alternatives

Rejected:

- core promotion as the selected fix;
- automatic aliases from same-spelled identities;
- effective graph as source authority;
- derived index as independent authority;
- opportunistic parsing;
- weakened, hidden, or vacuous coverage;
- structural resemblance;
- caller-selected correspondence/mapping/coverage;
- independent second planner or downstream authority;
- silent frozen-contract mutation;
- TASK-071 reauthoring as a presumed necessity.

## 11. Remaining TASK-074 blockers

Addressability/coverage implementation does not establish real execution readiness. Still required:

1. secure accepted-Candidate to governed-publication-subject bootstrap;
2. independently authorized, durable, Candidate-bound Judgment;
3. Ready interruption/recovery semantics;
4. sole secure Audit derivation from reloaded invocation evidence;
5. sole secure Conformance-record derivation from reloaded conformance evidence;
6. actual conformance over decisive rendering;
7. actual Manifest admission;
8. Manifest persistence/reload;
9. complete Candidate-to-Manifest restart reauthentication;
10. interruption/recovery at every durable boundary.

## 12. Ordered successor recommendation

No successor is created or activated by this decision.

### Successor 1 — semantic resolver/effective graph/derivation implementation

Implement exact paired decoder integration, paired/effective graph, nontraversable counterpart proof, canonical companion derivation evidence, persistence/reload, and generic adversarial tests. Do not implement Plan authority or execute TASK-071 lifecycle.

Acceptance: generic paired-v3 cardinalities including `N == decoded row count`; valid canonical reload succeeds; stale/altered/foreign/version/path/nonreproducible reloads fail; byte/order/collision/duplicate/omission/foreign/substitution vectors fail; core-only and frozen history remain unchanged. A read-only TASK-071 compatibility proof separately establishes exact `6/76/1/7/14/27/8/5 = 144`, 144 counterpart proofs, six requirements, and N=7 without creating authority.

### Successor 2 — capability v2, one-planner dispatch, Plan v2, and native admission

Implement sole capability-v2 issuer/verifier/persistence, closed pre-planning dispatch, sole Plan-v2 planner/verifier, successor native admission issuer/verifier/registry/wrappers, and exact Release/Ready/graph continuity evidence. Do not project, render, or execute TASK-071.

Acceptance: exact authorized capability reload; six positive outcomes and N mappings; zero/omitted/surplus/duplicate/reordered inventories reject; counterfeit capability/graph/evidence, second planner, mixed/v1+v2, Release-A/Plan-B, frozen-issuer, replay, copy/serialization, expiry, interruption, and cross-process vectors reject; native-v2 Release bytes remain unchanged.

### Successor 3 — downstream publication-evidence and recovery implementation

Implement secure bootstrap; independent Judgment assessment and Ready/Release continuity evidence; projection binding; controlled invocation evidence; sole Audit derivation; actual conformance assessment; sole Conformance-record derivation; fixed-locator ten-record assembly; successor Manifest admission/persistence; and stage-specific durable recovery. Do not execute TASK-071.

Acceptance: exact positive Candidate→Judgment→Ready→Release→Plan/admission→projection→artifact/invocation→Audit→assessment→Conformance→ten-record closure→Manifest chain on synthetic inputs; independent authorization at required boundaries; exact graph/coverage propagation; valid reload success; crash injection before/after every commit and consume point; cross-run/Candidate/Plan/graph/rendering/path/version substitution, caller-manufactured semantics, orphan/partial write, replay, stale reservation, and postcommit restart vectors reject.

### Successor 4 — isolated representative synthetic Candidate-to-Manifest integration proof

Exercise every production boundary with an isolated filesystem-backed governed fixture containing every paired source and cross-domain resolution class, six requirements, and nonzero ordered mappings. Include unknown/mixed/duplicate/foreign/reordered/omitted/surplus/wrong-kind/wrong-domain cases, actual conformance, derived predecessor records, Manifest, persistence, valid reload, tampered reload rejection, crash points, restart with fresh process-local handles, cleanup, and exact reconciliation. Do not use TASK-071.

Acceptance: full actual chain succeeds and independently reauthenticates; no substantive mocks; all adversarial boundaries fail; no residue.

### Successor 5 — read-only exact TASK-071 readiness adjudication

After successors 1-4 are accepted, verified, reconciled, and freshly reviewed, reauthenticate exact TASK-071 closure, derive graph/coverage read-only, authenticate implementation/version and environment, inspect authority/bootstrap availability and residue, prove interruption/recovery readiness and protected bytes, and issue `READY` or `NOT READY`. It creates no governed lifecycle object and consumes no authority or authoring attempt.

### Successor 6 — separately authorized real TASK-071 execution

Only an accepted Successor-5 `READY` ruling plus a new explicit human authorization may permit one named governed execution identity. The authorization must bind Candidate fingerprint, paths, implementation digests, authority scope, output locations, stop conditions, and operation limits. Recovery may resume only that same execution identity; a second fresh attempt requires new authorization. Post-run preservation, full reauthentication, residue reconciliation, and outcome adjudication are mandatory. No Candidate-authoring attempt is consumed.

## 13. Implementation acceptance criteria

Generic implementation must prove at minimum:

- exact profile dispatch, canonical source equality, all supported cardinalities, and `N == decoded row count`;
- complete source consumption, paired closure, six global requirements, and exact N owner-authored mappings without a fabricated per-object coverage ontology;
- graph-scoped identity, wrong-domain/kind/collision/alteration/order/omission/duplicate/foreign rejection;
- structurally equivalent but wrong-authority, cross-Candidate graph/Plan, Release-A/Plan-B, conformance cross-rendering/graph, and Manifest substitution rejection;
- sole authorized capability, planner, admission, Audit, Conformance, assembler, and Manifest paths;
- exact independent persistence/reload reproduction and stage-specific crash recovery;
- valid reload success and invalid reload rejection;
- frozen-history byte preservation, no parallel authority, and exact process/filesystem reconciliation.

The TASK-071-specific proof separately requires 144 exact class-counted nodes, 144 unique nontraversable counterpart proofs under the closed table, six requirements, and seven mappings.

## 14. Conditional-acceptance boundary and unmet conditions

The architecture direction, authority partition, migration ruling, and ordered successor sequence are accepted. Implementation readiness is not accepted. The candidate wire schemas in this decision are design constraints, not executable authority contracts, until all of the following are closed by separately authorized successor work and fresh independent byte-level review:

1. define and verify a closed core JSON-location/record-kind to `object_kind` registry for every identity-bearing core object, including exact target-kind validation and deterministic node/edge bytes;
2. replace the provisional derivation-evidence envelope with a production-schema-exact contract, including the exact extension envelope decomposition (`payload.contract_identity`, `payload.contract_version`, ordered `target_refs`, and all envelope fields), a closed ordered invariant-identity inventory, exact persistence wire, and independent reproduction;
3. replace the provisional capability-v2 design with exact `RendererCapabilityDeclarationRecord` semantic bytes and an exact BCRP extension tuple containing literal owner/name/version/authority/scope/ordered targets/criticality/character/validation/preservation/payload fields;
4. replace the provisional Plan-v2 design with exact `RendererCompatibilityPlanRecord` semantic bytes and exact extension literals, ordered dynamic authority/target binding rules, `preservation: "must-preserve"`, and independently reproducible eight/ten-record closure bytes;
5. rerun the corrected TASK-071 counterpart model with section order excluded from cross-domain comparison, proving 144 unique object counterpart records and zero mismatches under the final table;
6. obtain a fresh independent PASS on the identical final implementation-contract bytes before any implementation-readiness or successor-readiness claim.

Failure of any condition leaves TASK-071 immutable and `NOT READY`; it does not trigger reauthoring, consume an attempt, or authorize a successor.

## Consequences

Ruling: **CONDITIONALLY ACCEPTED**. The selected architecture may guide separately authorized contract-closing work in the stated order, but it is not yet ready for production implementation. This decision does not accept TASK-074, authorize implementation now, make TASK-071 operationally ready, create or activate a successor, or authorize real lifecycle/publication activity.