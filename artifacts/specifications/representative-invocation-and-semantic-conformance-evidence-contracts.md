# Representative Invocation and Semantic-Conformance Evidence Contracts

Date: 2026-08-01
Status: architecture-fixed; implementation pending
Task: TASK-060

## Purpose

Define the exact v2 record/payload seam required by TASK-054. These are versioned downstream extensions on existing BCRP record kinds, not new core kinds.

## Ten-record predecessor topology

The accepted representative conformance closure is the unchanged eight-record verified Plan closure followed by exactly:

9. one `GeneratedArtifactAuditRecord` under the representative invocation contract;
10. one `SemanticArtifactConformanceRecord` under the v2 conformance contract.

Record order and predecessor bytes are exact.

## Representative GeneratedArtifactAuditRecord

Top-level semantic keys are exactly the historical audit topology:

- `release_ref`;
- `ready_ref`;
- `ready_fingerprint`;
- `plan_ref`;
- `renderer_capability_ref`;
- `artifact` exactly `{id, filename, media_type, sha256, byte_length}`;
- `audit_links_pass=true`;
- `invocation_time`.

The one required extension has the existing envelope keys, with:

- owner `briefforge-representative-controlled-renderer-invocation`;
- name `invocation-and-artifact-evidence`;
- version `1.0.0`;
- scope `artifact-existence-and-invocation-audit-links-only`;
- validation contract `briefforge:representative-controlled-renderer-invocation-evidence:1.0.0`.

Its payload keys are exactly:

`contract_identity`, `policy_identity`, `authorization_identity`, `authorization_fingerprint`, `authorization_ledger_directory`, `admission_commitment_identity`, `lifecycle_inventory_digest`, `plan_fingerprint`, `capability_fingerprint`, `renderer_identity`, `renderer_adapter_id`, `renderer_version`, `renderer_implementation_digest`, `projection_profile_identity`, `projection_profile_version`, `projection_fingerprint`, `projection_closure_fingerprint`, `consumed_mapping_ids`, `selected_expression_modes`, `invocation_mode`, `environment`, `environment_policy`, `interpreter_flags`, `effective_interpreter_controls`, `external_assets`, `output_directory`, `output_inventory`, `execution_digests`, `execution_byte_lengths`, `invocation_outcome`, `artifact_existence`, `audit_links`, `semantic_conformance`, `manifest_authority`, `distribution_authority`, `successful_publication`.

Fixed outcomes remain: one output; two equal execution digests/lengths; `completed-deterministically`; artifact/audit verified; semantic conformance unassessed; all later authorities absent/not asserted.

## Representative SemanticArtifactConformanceRecord

Top-level semantic is exactly:

- `audit_ref`;
- `ready_ref`;
- `audit_link_pass=true`;
- `semantic_pass=true`;
- `evidence` exactly `{profile, aggregate_verdict, requirement_count, evidence_sha256}` where profile is `briefforge-static-html-semantic-realization-profile:2.0.0`, aggregate verdict is `approved`, and requirement count is exactly 7.

`approved` is the stable BCRP/TASK-054 admission vocabulary. The extension payload separately records `assessment_status=conforming`. A non-conforming or indeterminate result emits no record.

The one required extension has the existing envelope keys, with:

- owner `briefforge-representative-semantic-artifact-conformance`;
- name `semantic-realization-evidence`;
- version `2.0.0`;
- scope `semantic-artifact-conformance-only`;
- validation contract `briefforge:semantic-artifact-conformance-evidence:2.0.0`.

Its payload keys are exactly:

`contract_identity`, `policy_identity`, `profile_identity`, `profile_version`, `assessor`, `authorization_identity`, `authorization_fingerprint`, `release_fingerprint`, `lifecycle_inventory_digest`, `plan_fingerprint`, `capability_fingerprint`, `invocation_authorization_identity`, `invocation_authorization_fingerprint`, `invocation_evidence_fingerprint`, `artifact_identity`, `artifact_sha256`, `assessment_status`, `requirement_accounting`, `authority_scope`, `manifest_authority`, `distribution_authority`, `successful_publication`.

`assessor` is exactly `{identity, owner, role}` and binds `briefforge.representative_semantic_artifact_conformance:2.0.0` through separately bound authorization fields.

## Exact requirement accounting

`requirement_accounting` is exactly:

- `profile_identity` and `profile_version`;
- `projection_closure_fingerprint`;
- `requirement_ids`: the seven canonical requirement IDs in the profile’s fixed order;
- `expected_requirements`: seven objects in fixed order, each exactly `{id, outcome, planned_count, realized_count, element_evidence_sha256}` with `outcome=conformant` and equal positive counts;
- `element_entries`: one canonical object per planned field/edge realization or planned-zero operational exclusion;
- `unplanned_realization_count=0`.

Every element entry has exactly:

`key`, `requirement_ids`, `source_identity`, `projection_rule`, `role`, `planned_count`, `realized_count`, `order`, `parent_identity`, `text_sha256`, `value_state`, `coefficient`, `scale`, `unit_identity`, `qualification_target_identity`, `provenance_identity`, `obligation_target_identities`, `duplication_policy`.

`requirement_ids` is the canonical profile-order list of every requirement whose derived target/role closure contains that entry. Entries may therefore belong to both statements/qualifications or values/table without duplicating an HTML realization. Operational-authority exclusion entries have the exact empty requirement list and planned/realized count zero.

For each requirement, its evidence subset is all element entries containing that requirement ID, sorted by `key`. `planned_count` and `realized_count` are respectively the sums of those entry counts. `element_evidence_sha256` is SHA-256 over UTF-8 canonical JSON of that exact sorted subset (`sort_keys=true`, separators `(',', ':')`, `ensure_ascii=false`, `allow_nan=false`). This is the only accepted overlap and digest algorithm.

Inapplicable scalar values are exact empty strings; inapplicable order is `-1`; target inventory is an exact list. Applicable values are exact admitted values. This fixed schema prevents evidence omission behind optional keys.

## TASK-054 atomic dispatch

Before calling a persisted verifier, TASK-054 parses only the exact ten-record shape and extracts:

1. audit extension validation contract;
2. audit payload renderer identity/version/adapter/digest;
3. conformance extension validation contract;
4. conformance payload profile identity/version;
5. conformance payload assessor identity;
6. conformance top-level aggregate verdict and record topology.

That complete tuple must equal the historical v1 tuple or the representative tuple. Mixed, partial, malformed, duplicated or unknown tuples fail before verifier dispatch.

Both verifiers return the same narrow runtime interface: verified ten-record closure with `bundle` and `fingerprint`, or rejection. After dispatch, TASK-054’s existing authorization, inventory, artifact, lifecycle and persistence checks remain common.

The representative payload deliberately preserves the exact downstream paths TASK-054 consumes:

- audit semantic artifact and release/Plan references;
- audit payload output directory, Plan fingerprint and renderer identity/version;
- conformance payload invocation/conformance authorization bindings;
- `requirement_accounting.expected_requirements[*].id` and `.outcome`;
- BCRP evidence aggregate verdict `approved`.

No normalization callback, registry, dynamic import or caller-selected verifier is admitted.
