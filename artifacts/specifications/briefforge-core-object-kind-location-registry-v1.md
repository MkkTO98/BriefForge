# BriefForge Core Object-Kind/Location Registry 1.0

Status: frozen TASK-076 implementation contract
Machine authority: `artifacts/contracts/task076/core-object-kind-location-registry.json`
Contract: `briefforge:core-object-kind-location-registry:1.0.0`

## Scope

The registry closes BCRP 1.0 identity resolution for paired-to-core consistency validation. Its 37 entries cover all 11 BCRP record kinds and 26 admitted nested identity-bearing kinds. No unlisted path, arbitrary dictionary member, embedded string, locator, structural resemblance, extension payload, or unknown version can create a core object.

Dispatch is exact `["briefforge-core-representation-profile","1.0.0"]`. Unknown profile versions, record kinds, nested kinds, locations, duplicates, missing targets, ambiguity, and misplaced identities block. Core local identity is ASCII, case-sensitive, profile-instance unique, and loaded only from each entry's exact identity field at an enumerated location.

## Location and order

A source locator contains Candidate identity, exact profile-byte digest, record identity, and an RFC 6901 pointer with decimal array positions. The pointer diagnoses and reproduces source extraction; it is never object identity or Plan reference syntax. Mapping keys and array positions locate bytes; stable semantic identity resolves the object. Reordering an identity-keyed array does not create a new semantic object but does alter authoritative profile bytes and therefore requires full byte reauthentication. Reordering owner-authored semantic order rejects.

Document order is meaningful only where an entry explicitly says so. Records are identity-keyed; their array positions are not semantic. Section child order and renderer/fallback preference order are semantic. `CaseBinding.order`, not its container position, is the authoritative order value.

## Counterparts

Only Section, PresentationStatement, Exhibit, CaseBinding, MaterializedValue, TypedRelation, MaterialProvenance, and Obligation may be TASK-071 counterpart targets. Matching requires exact local identity plus expected kind and the closed field rules from D-20260809. Structural resemblance never substitutes for identity resolution.

Paired `Section.order` is the sole counterpart-field exclusion. It is paired-owned composition order; the core sections-array position is nonauthoritative. No other counterpart field is excluded. Exclusions are the exact `counterpart_exclusions` and `other_counterpart_exclusions` arrays in the registry, never inferred.

Counterpart records are consistency proof only: nontraversable, not graph nodes/edges, not aliases, not reference targets, and not planner coverage.

## Namespace and extensions

Uniqueness is within the core graph domain. Equal local strings in core and paired domains are neither collisions nor equality. A duplicate within the core domain rejects. Unknown extension bytes receive no semantic meaning; only exact profile dispatch can interpret them, and applicable preservation policy still governs bytes.

## Rejection taxonomy

Every entry freezes missing, duplicate, ambiguous, unknown, and misplaced rejection behavior. Unsupported profile/version fails before object discovery. Identity scanning of arbitrary JSON strings is prohibited. A caller-supplied kind, locator, index, or normalization never overrides the registry.
