# Representative Projection Content Admission Matrix

Date: 2026-08-01
Status: architecture-fixed after second review remediation; final re-review pending
Task: TASK-060
Profile: `briefforge:representative-static-html-projection-profile:1.0.0`

## Rule

The profile consumes the exact six-record verified Publication Release closure plus the separately verified eight-record capability/Plan closure. HTML content is derived only from the Brief, Material and Candidate semantic records. Lifecycle and operational authorities remain audit bindings and are never presented as content.

Every admitted content field below has an exact key set and fixed realization rule. Unknown fields, unknown nested fields, nonempty prohibited inventories and optional fields outside the explicit state rules fail closed.

## Global bounds

- serialized verified content closure: at most 2,000,000 UTF-8 bytes;
- artifact: at most 1,000,000 bytes and the smaller authorization limit;
- identities: existing canonical identity syntax, at most 200 UTF-8 bytes;
- title, label, role, scope and designation text: 1–200 UTF-8 bytes;
- statement, purpose, description, citation, reason and obligation-kind text: 1–4,096 UTF-8 bytes;
- exact decimal is `{coefficient: integer-string, scale: non-negative integer 0..18}`;
- no null, float, NaN, infinity, empty required text or malformed decimal.

## PresentationBriefRecord

Exact semantic keys: `organizing_purpose`, `audiences`, `scope`, `non_scope`.

- `organizing_purpose`: exactly `{id, statement}`; realize both.
- `audiences`: 1–8 objects, each exactly `{id, description}`; realize all in canonical identity order.
- `scope`: one nonempty string; realize exactly.
- `non_scope`: one nonempty string; realize exactly.

The Brief record identity is itself a realized metadata identity.

## PortablePresentationMaterialRecord

Exact semantic keys: `authorities`, `provenance`, `evidence_snapshots`, `external_references`, `units`, `semantic_types`, `values`, `required_value_ids`, `consistency_assertions`, `state_validations`.

- `authorities`: exactly 5 operational authority objects plus 1–8 content authority objects; every object is exactly `{id, owner_identity, role, scope}`.

Operational authorities are exactly:

1. `{id=authority:briefforge-bcrp-validation, owner_identity=project:BriefForge, role=validation-authority, scope=BCRP-L0-L6}`;
2. `{id=authority:briefforge-publication-release, owner_identity=project:BriefForge, role=publication-release-authority, scope=fixed-evidence-publication-release}`;
3. `{id=authority:briefforge-controlled-renderer-invocation, owner_identity=project:BriefForge, role=renderer-invocation-authority, scope=one-controlled-renderer-invocation-act}`;
4. `{id=authority:briefforge-semantic-artifact-conformance, owner_identity=project:BriefForge, role=semantic-artifact-conformance-assessor, scope=one-semantic-artifact-conformance-assessment}`;
5. `{id=authority:briefforge-publication-manifest-projector, owner_identity=project:BriefForge, role=publication-manifest-projector, scope=one-publication-manifest-production}`.

No other operational role or identity is admitted. Capability-declaration and planning authorities remain separate authorization acts and are not Material authority objects. The five admitted operational objects remain immutable Release semantics and receive explicit conformance entries under rule `operational-authority-exclusion`, role `audit-only`, with planned and realized HTML cardinality zero.

Content authorities are the remaining 1–8 entries and must be transitively referenced by a displayed statement, value, provenance, source, obligation or distribution edge. Each content authority definition is realized once in HTML. An authority classified both operational and content, an unreferenced content authority, an unknown operational authority or any unclassified authority fails closed.
- `provenance`: 1–16 objects, each exactly `{id, citation, authority_ref}`; realize all fields and authority edge.
- `evidence_snapshots`: 1–16 objects, each exactly `{id, version, content_fingerprint, provenance_ref}`; realize all fields and provenance edge.
- `external_references`: 1–16 objects, each exactly `{id, reference_kind, upstream_object_identity, snapshot_ref, provenance_ref, authority_ref}`; realize every field/edge. `upstream_object_identity` is displayed as the governed source locator. No network dereference or verification is asserted.
- `units`: 1–16 objects, each exactly `{id, description}`; realize each definition.
- `semantic_types`: 1–16 objects, each exactly `{id, description}`; realize each definition.
- `values`: 2–32 exact value objects under the state rules below; one table row each.
- `required_value_ids`: exact set of all value identities; realize inventory edges, never infer ordering.
- `consistency_assertions`: exactly empty.
- `state_validations`: exactly empty.

The Material record identity is realized metadata. Every authority/unit/type/source/provenance/snapshot object must be referenced. Unconsumed definitions fail closed.

### Exact value shapes

Common required keys: `{id, value_state, unit_ref, semantic_type_ref, source_ref, authority_ref}`.

Accepted state-specific shapes:

- `present` or `explicit-zero`: common keys plus `payload`; payload exactly `{coefficient, scale}`. Present coefficient is nonzero. Explicit-zero canonicalizes to coefficient `0`, scale `0`.
- `missing-not-provided`, `unavailable` or `not-applicable`: common keys plus nonempty `reason`; payload prohibited.
- approximation is allowed only on `present` or `explicit-zero`: add `approximate=true` and `approximation` exactly `{method, bound}` with nonempty strings. `approximate=false`, an orphan approximation, or other optional keys are prohibited.

Unsupported states (`suppressed-withheld`, `unresolved`, `invalid`) fail at this profile boundary. Exact coefficient/scale are rendered separately; no float conversion, rounding, locale formatting, normalization, unit conversion or inference.

## CandidatePresentationPackageRecord

Exact semantic keys: `brief_ref`, `material_refs`, `organizing_purpose`, `audiences`, `scope`, `non_scope`, `statements`, `sections`, `obligations`, `renderer_requirements`, `fallbacks`, `exhibits`, `relations`, `distribution`, `comparison_universes`, `selection_sets`.

- `brief_ref`: exact Brief identity.
- `material_refs`: one-element list containing exact Material identity.
- `organizing_purpose`: exactly `{id, statement, brief_purpose_ref}`; realize every field/edge; statement equals Brief purpose statement.
- `audiences`: 1–8 objects exactly `{id, description}`; realize separately and require equality to Brief audience semantics.
- `scope` and `non_scope`: one nonempty string each; realize separately and require equality to Brief.
- `statements`: 2–32 under exact shape below.
- `sections`: 2–8 under exact hierarchy below.
- `obligations`: 1–16 objects exactly `{id, kind, authority_ref, target_refs}`; kind is one of `label|qualification-required|source-display`; target refs contain 1–16 unique admitted content identities. Realize definition and every target/authority edge in canonical identity order. BCRP does not preserve authored `target_refs` transport order.
- `renderer_requirements`: exactly seven complete planner documents defined by the projection profile; planning-only and not displayed.
- `fallbacks`: exactly empty.
- `exhibits`: exactly one fixed exhibit below.
- `relations`: 1–16 exact qualification relations below.
- `distribution`: exactly `{id, designation, authority_ref}`; realize all fields/authority edge as content metadata. Display does not grant transfer authority.
- `comparison_universes`: exactly empty.
- `selection_sets`: exactly empty.

The Candidate record identity is realized metadata. No other Candidate field or nested field is admitted.

### Exact statements

Each statement has exactly:

`{id, text, posture, communication_functions, attention, purpose_ref, authority_ref, upstream_refs, requires_comparison_universe}`

and may have `value_ref` only when it resolves to one admitted value. Requirements:

- posture is `observation|caveat|uncertainty`;
- `communication_functions` is 1–4 nonempty fixed strings;
- `attention` is one nonempty fixed string;
- `purpose_ref` equals Candidate organizing-purpose ID;
- `upstream_refs` contains 1–16 unique external-reference identities;
- `requires_comparison_universe=false` exactly;
- `comparison_universe_ref` and every undeclared key are prohibited;
- all fields and edges are realized; full text is never truncated.

Every caveat/uncertainty is source of exactly one relation object exactly `{id, kind, source_ref, target_ref, authority_ref}` with `kind=limits-target`; target is one observation statement. Every relation and edge is realized exactly once. Value-only qualification targets are prohibited by existing BCRP validation.

## Section closure

Each section is exactly `{id, title, children}`.

- sections = exactly `{root} ∪ root.children`;
- root contains 1–7 leaf-section identities and no statement/exhibit;
- every leaf contains 1–17 ordered child identities, each a statement or the table exhibit, and at least one child is a statement;
- every leaf contains 1–16 statements; the one table may add one further child without changing the statement bound;
- every statement appears in exactly one leaf child list;
- the table exhibit appears in exactly one leaf child list;
- no unknown child, duplicate membership, multiple parent, cycle or third level;
- section encounter order is root child order;
- element encounter order is each leaf child order;
- section list transport order is non-semantic.

Every title, object definition and ordered parent-child edge is realized.

## Keyed fixed-table exhibit

The exhibit is exactly `{id, kind, purpose_ref, case_bindings, value_ids}`:

- `kind=fixed-static-table`;
- `purpose_ref` equals Candidate organizing-purpose ID;
- `case_bindings`: 1–16 authored objects, each exactly `{id, order, primary_ref, comparison_ref}`;
- explicit integer orders are unique and contiguous `1..N`;
- primary and comparison differ;
- every slot ref is globally unique;
- `value_ids`, `required_value_ids`, all slot refs and complete Material value IDs are equal as sets.

The explicit order field—not list transport order—is authoritative. Pairing, slot role and order are immutable Candidate semantics. Every exhibit/case field and edge is realized; no downstream component creates them.

## Exact projection identity closure, audit-exclusion closure and Plan partition

The displayed projection identity closure contains the Brief/Material/Candidate record identities plus every admitted nested content-object identity. The separate audit-exclusion closure contains exactly the five operational-authority identities. Plain text fields, canonical edges and planned-zero operational exclusions are separately bound by `(source identity, projection rule, role/field)` entries because Plan target refs accept identities only.

The seven exact mapping target sets are:

1. hierarchy: Brief record, Candidate record, both organizing-purpose IDs, all audience IDs, all section IDs, and distribution ID;
2. statements: all statement IDs;
3. values: all case-binding IDs, value IDs, unit IDs and semantic-type IDs;
4. qualifications: all caveat/uncertainty statement IDs and all relation IDs;
5. provenance: Material record, all content-authority IDs, provenance IDs, snapshot IDs and external-reference IDs;
6. obligations: all obligation IDs;
7. table: exhibit ID, all case-binding IDs and all value IDs.

Expected overlaps are exactly qualification-statement IDs between 2/4, and case/value IDs between 3/7. The union must equal the complete displayed projection identity closure; no displayed identity is absent or outside closure. The disjoint audit-exclusion closure is not a Plan/HTML target and is instead reconciled by planned-zero conformance entries. Requirement identities are planning-only and excluded from both closures.

## Role accounting

- each object-definition role exactly once;
- each governed directed edge role exactly once;
- each value exactly once as a table row;
- identity text may recur only as endpoints of separately accounted edges;
- conformance keys are `(source_identity, projection_rule, role_or_field)`, never identity alone;
- an omitted, duplicated, extra, reordered, changed or unparseable role blocks accepted conformance.
