# Initial Representation Profile and Golden Corpus Acceptance Report

Date: 2026-07-16
Task: TASK-044
Status: complete
Gate: **CLEAR TO IMPLEMENT**

## 1. Recovery and TASK-043 completion reconciliation

The required first command ran before repository mutation:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -B tools/recover_session.py --project . --json
exit 0
```

All applicable instructions were then inspected: root `AGENTS.md`, `CONSTITUTION.md`, all eight Markdown instruction files, state pointers, and latest handoff.

TASK-043 is operationally complete:

- `artifacts/tasks/TASK-043-semantic-representation-contract-and-layered-validation-specification-planning.md` says `Status: complete` and records accepted outputs and `CLEAR TO PROCEED`;
- its specification says `Status: accepted specification`;
- all three TASK-043 decisions say `Status: accepted`;
- its report says `Status: complete` and recommends TASK-044;
- `state/active_goal.md` says TASK-043 is complete and no implementation task is active;
- `state/project_state.md` says `Status: active; TASK-043 ... complete; no implementation task active`.

The word `active` modifies **BriefForge Project State**, not TASK-043. The same sentence explicitly marks TASK-043 complete; no task artifact or state pointer contradicted that result. TASK-044 activation was therefore safe.

## 2. Fresh non-Git baseline and identifier

Read-only Git probes returned:

```text
git rev-parse --is-inside-work-tree
fatal: not a git repository (or any of the parent directories): .git

git status --porcelain=v2 --branch
fatal: not a git repository (or any of the parent directories): .git
```

No Git repository was initialized.

TASK-044 was checked by task filename and repository content search. No TASK-044 task artifact existed; references only identified the proposed successor. The identifier was unused and accepted as proposed.

Fresh pre-mutation manifest:

- path: `/tmp/briefforge-before-task044-20260716.json`;
- format: `briefforge-filesystem-manifest-v1`;
- root: `/home/mkkto/srv/EIP/projects/BriefForge`;
- included-path count: 571;
- excluded directory names: `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `__pycache__`;
- excluded suffixes: `.pyc`, `.pyo`;
- created by the authorized `/tmp/briefforge_manifest.py`;
- no `sha256sum` command was run on manifest files;
- baseline contained no TASK-044 artifact.

No prior-task manifest was accessed or reverified.

## 3. Authoritative evidence inspected

### TASK-038 and ADPM

- `artifacts/decisions/D-20260708-adpm-representation-architecture.md`;
- `artifacts/reports/R-20260708-adpm-representation-architecture-evaluation.md`;
- `artifacts/reports/R-20260708-adpm-representation-recommendations.md`;
- `artifacts/specifications/architectural-decision-package-model.md`;
- ADPM integration/validation/versioning decisions.

Binding result: semantics precede representation; lossless mapping and independent ADPM/profile versions are mandatory; no schema, format, renderer input, Markdown, or current dataclass shape may become ontology authority.

### TASK-040 through TASK-043

All named tasks, specifications, reports, and accepted decisions were inspected. The controlling result is TASK-043's accepted semantic graph, stable-reference authority, seven validation layers, 17 cross-layer invariants, profile boundary, and golden-corpus gate. TASK-041 publication and TASK-042 semantic-authority/state/selection/fallback meanings were treated as fixed inputs rather than reopened.

### Implementation and operational evidence

Read-only evidence included:

- `src/briefforge/runtime.py`: Candidate records and current semantic fingerprint;
- `src/briefforge/validation.py`: current Judgment and constitutional checks;
- `src/briefforge/promotion.py`: exact Candidate/Judgment/Ready binding;
- `src/briefforge/downstream.py`: Ready-only downstream access;
- `src/briefforge/renderer_adapter.py`: renderer identity/capability/request/invocation and current narrow conformance;
- lifecycle, adapter, conformance, static renderer, integration, and source-preservation tests as evidence only;
- TASK-039 InsightForge source fixture and BriefForge Candidate/Judgment/Ready/HTML/audit/conformance/inspection chain;
- Presentation Grammar, Communication Intent experimental status, renderer backlog/policy, decision-support backlog, project state, architecture, and latest handoff.

Known pressure retained, not repaired: TASK-039 renderer audit says no table exhibit while HTML/inspection contain a table; current statement modes mix semantic posture/function/encounter; current obligation links are duplicated in two directions; current audit-link conformance does not prove semantic output fidelity.

## 4. Accepted profile

Profile name: **BriefForge Core Representation Profile**.

- identity: `briefforge-core-representation-profile`;
- version: `1.0.0`;
- short name: BCRP 1.0;
- authority: renderer-independent profile subordinate to the Constitution, ADPM, and TASK-041 through TASK-043.

The binding specification is `artifacts/specifications/briefforge-core-representation-profile.md`.

BCRP is one profile with multiple independently addressable root record kinds. It is not a monolithic document and does not select a transport in TASK-044.

## 5. Root-record and bundle topology

BCRP accepts:

1. Presentation Brief Record;
2. Portable Presentation Material Record;
3. Candidate Presentation Package Record;
4. Validation Judgment Record;
5. Ready Presentation Package Record;
6. Publication Release Record;
7. Renderer Capability Declaration Record;
8. Renderer Compatibility/Expression Plan Record;
9. Generated-Artifact Audit Record;
10. Semantic Artifact-Conformance Record;
11. derivative Publication Manifest Record;
12. a non-semantic Profile Bundle Index for bounded inventory/relative transport lookup.

The profile specification section 2 binds, for every record: owner, identity/version, canonical/derivative status, dependencies, offline retention, semantic-fingerprint participation, regeneration, and event ordering. Candidate semantic fingerprinting covers the Candidate's transitive canonical semantic closure only. Judgment, Ready, release, renderer, artifact and manifest records have independent identity/fingerprint domains.

## 6. Semantic coverage

The complete binding matrix is in `artifacts/specifications/briefforge-core-representation-profile.md`, section 4. It maps 37 mandatory responsibilities to one owning record, representation form/cardinality/scope, required/optional status, validation layer, and fallback/failure consequence.

Coverage includes purpose, audience, generic subjects, authority, provenance, snapshots, values/types/units/states, lifecycle, multidimensional statements, relations, caveats, uncertainty, annotations, obligations, navigation, exhibits, distribution, transformation, renderer/fallback, finite selections, lifecycle links, manifest, renderer/artifact identity, traceability, and semantic conformance. Reverse indexes are explicitly non-canonical and excluded from fingerprints.

## 7. Canonical relationship directions

BCRP selects one canonical direction per relationship:

- statement -> upstream reference;
- statement -> scoped authority assertion;
- statement -> organizing purpose;
- caveat/uncertainty -> limited target;
- obligation -> target;
- composition parent -> ordered children;
- exhibit -> value bindings;
- complete selection-state projection -> every applicable statement/exhibit/label/caveat/uncertainty/evidence/obligation/requirement/fallback;
- renderer requirement -> admitted fallback;
- Judgment -> assessed Candidate and Ready -> exact Candidate + successful Judgment;
- Release -> Ready + evidence snapshots;
- artifact audit -> request/plan/release/Ready/renderer/artifact;
- Manifest -> authoritative release and accepted artifact records.

Separate relationship records are mandatory when the edge itself has authority, provenance, scope, state, time, or obligations. Consumers derive reverse traversal in memory. Orphans, dangling/kind-mismatched targets, duplicate contradictory edges, position/path/DOM/CSS identity, and manifest override are rejected.

## 8. State representation

BCRP uses explicit scoped state assertions. Transport null and property absence carry no semantic meaning.

Value state is exactly one of: present, explicit zero, missing/not provided, unavailable, not applicable, suppressed/withheld, unresolved, or invalid. Exact zero requires a zero payload and remains distinct from absence. Present/zero values may coexist with independent uncertainty, evidence, distribution, display-rounding, and consistency qualifiers.

Consistency is independent: consistent, conflicting, unresolved, invalid under contract, or not checked. Conflict points to every disagreeing source and names detection/resolution authority. Suppression is a value-disclosure state; distribution restriction is a governance obligation.

Stale, withdrawn and superseded references point to authoritative upstream/publication events and never erase history. Unknown core states reject under an unsupported profile; no silent `unknown` coercion is permitted.

## 9. Selection representation

Finite selection uses complete materialized state projections. Every state explicitly enumerates all applicable purpose/scope, titles/labels, statements, relations, exhibits/values, evidence/provenance, caveats, uncertainty, obligations, renderer requirements, static expression and print expression. Invariant statements are still repeated in every projection and validated.

Deltas, inheritance, wildcard states, intervals, arbitrary parameters, implied products, live queries, computed values, rankings and new comparisons are prohibited. Missing complete content or misleading narrative blocks selector publication; a fixed-state publication requires its own valid Candidate/Ready/release path.

## 10. Canonicalization, equality and fingerprints

BCRP canonicalization:

- preserves explicitly semantic order and sorts unordered sets by stable kind/scope/identity/version keys;
- rejects duplicate identities/edges;
- uses Unicode NFC and LF while preserving remaining prose whitespace;
- keeps identifiers case-sensitive and rejects noncanonical forms;
- normalizes admitted timestamps to explicit UTC;
- treats integers exactly and decimals as coefficient/scale, normalizing negative zero;
- preserves units, exact state, authored narrative labels, and semantic extensions;
- excludes transport locators/order, comments, reverse indexes, derivative manifests, renderer bytes/mechanics, display rounding, and explicitly non-semantic display extensions from Candidate semantic canonicalization.

The specification distinguishes:

A. semantic equality—same authoritative semantic graph;
B. profile-instance equality—same graph plus same canonical profile-level semantic information;
C. artifact equality—identical bytes/files under artifact inventory rules;
D. presentation equivalence—validated preservation of required meaning across derivative expressions.

Fingerprints declare domain: Candidate semantic, profile instance, release semantic, artifact bytes, or manifest instance. Equal fingerprints establish equality only within that domain/rule; never truth, authority, analytical validity, approval, or presentation equivalence.

## 11. Numeric and temporal discipline

Exact integers and decimals are preserved without silent binary-floating approximation. Approximate values require an exact represented center plus explicit approximation semantics. Units remain semantic; display conversion/rounding is separate. A small non-zero value cannot become semantic zero through rendering.

BriefForge interprets only generic owned timestamps for intake, validation, readiness, release/lifecycle, rendering, conformance, and manifest generation. Explicit offsets are mandatory and canonical form is UTC. Evidence-snapshot identity remains distinct from time. Upstream temporal material stays a generic typed reference/value; deferred fiscal/reporting/corporate-action semantics remain undefined.

## 12. Extension and version model

Every extension declares owner namespace, name/version, authority, scope, criticality, semantic/display-only character, validation policy, preservation requirement, and canonical generic payload.

Unknown required semantic meaning rejects. Unknown optional semantic content proceeds only when losslessly preserved and irrelevant to the attempted operation. Required presentation meaning fails renderer compatibility when unknown. Optional display-only content can be ignored only if explicitly non-semantic and discardable. Core meaning, identities, states, relations, validation and DSB-007 cannot be overridden.

BCRP uses independent semantic versioning. Patch is non-semantic clarification; minor is safely preservable optional addition; major covers required structure, identity/relationship, core-state, canonicalization/equality or fingerprint changes and requires a migration specification. ADPM semantic, transport, validation-policy, renderer, artifact and manifest versions remain separate.

## 13. Golden corpus

Binding specification: `artifacts/specifications/bcrp-golden-corpus-acceptance.md`.

Exactly three primary future cases are accepted:

1. reduced TASK-039 demographic/correlation fixed-evidence publication;
2. synthetic fictional-company comparison/decision publication using generic external refs and ADPM responsibilities;
3. synthetic company–macro relationship with three complete finite selection states.

Each has one expected-valid instance and minimal invalid mutations. The 30 specified mutations cover missing purpose, dangling references, ambiguous authority, orphan caveat, zero-as-missing, omitted suppression, silent conflict resolution, invalid state combinations, cycles, incomplete selections, incompatible conclusions, missing defaults, undeclared transformations, unsupported capabilities, missing caveats/print fallback, manifest/release contradiction, wrong Ready linkage, audit-link misreported as semantic conformance, unknown required extensions, and speculative financial fields.

The corpus coverage matrices prove positive/negative coverage for all 37 mandatory responsibilities, L0–L6, all 17 TASK-043 invariants, lifecycle boundaries, renderer modes, fallback, standalone operation, and optional AtlasForge catalogue consumption. No fourth case is needed.

## 14. Fixture safety and TASK-039 handling

Future fixtures prohibit secrets, credentials, personal/proprietary/raw sensitive data, live API/database/network/AtlasForge dependencies, mutable upstream paths, and absolute machine paths. They require deterministic offline reproduction, bounded retained attribution, conspicuously fictional company identities, and synthetic sensitivity labels without sensitive payload.

TASK-039 values/method/caveat/attribution may be copied only when safe and permitted; overloaded statements/paths/tables may be transformed into BCRP semantics; task/publication evidence may be referenced historically; material must be reduced. Current JSON shape/fingerprint/absolute paths and incorrect table-audit assertion cannot become canonical. TASK-039 and InsightForge source files remain untouched.

## 15. Initial serialization recommendation

Exactly one direction is recommended for TASK-045: **deterministic canonical JSON documents in a multi-record BCRP bundle**.

It faithfully maps independent records/references, supports deterministic ordering and schemas/validators, keeps states/extensions explicit, permits exact decimals as canonical strings or coefficient/scale records, remains readable/offline with stable Python tooling, and resists renderer coupling. Markdown is not canonical. No YAML/XML/TOML/database/converter work is recommended.

## 16. Implementation gate and next task

**CLEAR TO IMPLEMENT**

All gate conditions pass:

- one profile is fully specified;
- every accepted responsibility maps without gaps or duplicate authority;
- relationship direction and state encoding are settled;
- equality/canonicalization/fingerprint prerequisites are deterministic enough to implement;
- unknown meaning fails safely;
- three cases cover all layers/invariants/lifecycle/fallback boundaries;
- no company-specific field or DSB-007 breach is needed;
- no unresolved decision forces immediate schema migration.

Exact next task, not activated:

`TASK-045 — Initial Representation Profile, Layered Validator, and Golden Corpus Vertical Slice`

Scope must remain: one selected JSON serialization; BCRP 1.0; deterministic loader/canonicalizer; structural and core semantic validation; materialization of the three valid cases and invalid variants; round-trip and expected-finding tests. No current runtime migration, renderer integration, selector implementation, AtlasForge integration, or second format.

Another architecture-planning task is rejected because no concrete blocker remains.

## 17. Decisions and duplication avoidance

Accepted decisions:

- `D-20260716-bcrp-topology-relationship-and-state-profile.md`;
- `D-20260716-bcrp-canonicalization-equality-extension-and-versioning.md`;
- `D-20260716-bcrp-golden-corpus-serialization-and-implementation-gate.md`.

Avoided duplications:

- no new Presentation Request beside Presentation Brief;
- no new Resolved Input beside Portable Presentation Material;
- no second Candidate/readiness or publication lifecycle;
- no reverse-link authority for traversal convenience;
- no universal type/status/null;
- no renderer-owned semantic requirement;
- no canonical manifest/AtlasForge field;
- no company ontology or financial extension;
- no multiple transport formats.

## 18. Verification and mutation proof

Executed with `PYTHONDONTWRITEBYTECODE=1` and without compileall:

- recovery: exit 0;
- TASK-044 artifact consistency: `137/137 passed`;
- `tools/update_context_summaries.py --project . --max-depth 3`: exit 0;
- `tools/build_context.py ... TASK-044 ...`: exit 0, 5,740 estimated tokens / 10,000 budget;
- `tools/context_health.py --project . --json`: exit 0, zero blocks and zero warnings;
- `tools/check_coherence.py --project . --json`: exit 0, zero blocks; two classified warnings (the expected EIP path ownership interpretation and retained MetaHarvest historical/advisory references);
- `tools/architecture_reality_audit.py --project . --write-report --json`: exit 0, zero blocks; one known warning for the missing historical `templates/` reference, which this task was prohibited from fixing.

The authorized pre-task manifest is `/tmp/briefforge-before-task044-20260716.json`: format `briefforge-filesystem-manifest-v1`, root `/home/mkkto/srv/EIP/projects/BriefForge`, 571 included paths, exclusions `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `__pycache__`, `.pyc`, and `.pyo`, and no TASK-044/BCRP artifact.

The post-task manifest and exact comparison are intentionally produced after this report is frozen so the report cannot invalidate its own mutation proof. Their exact counts and path classification belong in the external closeout response.

Runtime tests were not run because no executable source, tests, validators, schemas, runtime records, or fixtures changed.

## 19. Scope confirmation

No source, tests, validators, runtime records, renderers, publications, fixtures, profile instances, schemas, serialization, TASK-039 artifacts, AtlasForge artifacts, upstream projects, Constitution, missing `templates/` reference, financial-domain semantics, or Git repository are modified by TASK-044. Compileall is not run. No commit or push occurs.
