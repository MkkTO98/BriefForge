"""Authority-aware production disposition of all 63 frozen TASK-076 invalid fixtures.

The frozen document is test data, never production authority.  Every row is accounted
before execution as exactly one of: 43 semantically representable attacks, 17 attacks
blocked at an authenticated authority boundary, or 3 production-computed/non-input
states.  Plan rows use only the public data-only closure comparator against an
independently deserialized canonical TASK-076 closure.  TASK-071 issued no Release;
this module therefore never constructs or verifies a full Plan lifecycle.
"""
from __future__ import annotations

import copy
from dataclasses import replace
import inspect
import json
from pathlib import Path
import traceback
import unittest
from unittest.mock import patch

import briefforge.bcrp_paired_derivation_evidence_v2 as derivation_module
from briefforge.bcrp.model import BCRPBundle, BCRPRecord
from briefforge.bcrp.registry import (
    CoreRegistryError, execute_core_registry, resolve_core_locator,
)
from briefforge.bcrp_paired_derivation_evidence_v2 import (
    DerivationEvidenceError, construct_envelope, verify_envelope,
)
from briefforge.bcrp_paired_semantic_interpretation_v2 import (
    CounterpartProof, decode_paired_inventory, interpret_paired_candidate,
)
from briefforge.bcrp_renderer_compatibility_planning_v2 import (
    PlanV2Rejected, plan_paired_v3_inventory, verify_plan_v2_predecessor_closure,
)
from briefforge.task076_contracts import (
    ContractAuthenticationError, authenticate_generation8_candidate, canonical_json,
    domain_digest, load_generation8_candidate,
)

ROOT = Path(__file__).resolve().parents[1]
FROZEN_PATH = ROOT / "artifacts/contracts/task076/invalid-fixtures.json"
VALID_PATH = ROOT / "artifacts/contracts/task076/valid-fixtures.json"
ENVELOPE_PATH = ROOT / "artifacts/contracts/task076/task071-derivation-evidence-envelope.json"
CAPABILITY_PATH = ROOT / "artifacts/contracts/task076/capability-v2-record.json"

AUTHORITY_BLOCKED = frozenset("""
 unknown-extension-profile partial-extension-profile omitted-paired-object
 duplicated-paired-object row-count-mismatch reordered-authoritative-records
 namespace-collision duplicated-extension missing-extension
 unknown-extension-data-semantic correlated-order-oracle-substitution
 equal-length-decoded-substitution same-length-source-row-substitution
 correlated-candidate-substitution correlated-candidate-digest-oracle-substitution
 correlated-registry-digest-oracle-substitution
 correlated-effective-graph-oracle-substitution
""".split())

NON_INPUT = frozenset("""
 paired-capability-no-decoder traversable-counterpart-proof ambiguous-core-locator
""".split())

ENVELOPE_ROWS = frozenset("""
 candidate-a-evidence-b registry-a-declares-b
 same-registry-identity-different-bytes foreign-structural-identity
 substituted-effective-graph altered-candidate-after-derivation
 correlated-authority-digest-oracle-substitution
 correlated-requirement-substitution correlated-mapping-inventory-substitution
""".split())

# D-20260817 lines 23-28 require exact structured rejection evidence for the
# nine rows whose lawful route is independent derivation-envelope
# reconstruction. The locator is the frozen TASK-076 source locator; the field
# is the precise production-owned semantic location.
DERIVATION_ROUTE_EVIDENCE = {
    "candidate-a-evidence-b": ("/fixtures/0", "candidate_identity"),
    "registry-a-declares-b": ("/fixtures/1", "registry_identity"),
    "same-registry-identity-different-bytes": ("/fixtures/2", "registry_digest"),
    "foreign-structural-identity": ("/fixtures/16", "authorization_fingerprint"),
    "substituted-effective-graph": ("/fixtures/17", "effective_graph_digest"),
    "altered-candidate-after-derivation": ("/fixtures/19", "candidate_profile_byte_digest"),
    "correlated-authority-digest-oracle-substitution": (
        "/correlated_fixtures/3", "authorization_fingerprint",
    ),
    "correlated-requirement-substitution": (
        "/correlated_fixtures/7", "requirement_inventory_digest",
    ),
    "correlated-mapping-inventory-substitution": (
        "/correlated_fixtures/8", "mapping_inventory_digest",
    ),
}

ABSTRACT_CLOSURE_ROWS = frozenset("""
 capability-a-plan-b release-a-plan-b core-only-capability-paired-coverage
 omitted-mandatory-requirement omitted-owner-mapping invented-mapping
 zero-mappings-nonempty-obligations task067-authority-as-native-v2
 foreign-rendering-conformance-chain mapping-reordered
""".split())

CANDIDATE_BYTE_ROWS = AUTHORITY_BLOCKED - frozenset("""
 correlated-candidate-substitution correlated-candidate-digest-oracle-substitution
 correlated-registry-digest-oracle-substitution
 correlated-effective-graph-oracle-substitution
""".split())

WRAPPER_ONLY_CLOSURE_ROWS = frozenset({
    "plan-v2-predecessor-closure-unreachable-extra",
    "plan-v2-predecessor-closure-altered-fingerprint",
})

CLOSURE_RECORD_MISMATCH = (
    "Closure complete records or independently bound metadata differ."
)
CLOSURE_ROOT_MISMATCH = "Closure terminal root is absent or substituted."

MUTATION_DESCRIPTOR_BY_ID = {
    "candidate-a-evidence-b": ("set", "candidate_binding"),
    "registry-a-declares-b": ("set", "registry_identity"),
    "same-registry-identity-different-bytes": ("set", "registry_digest"),
    "capability-a-plan-b": ("set", "plan_capability"),
    "release-a-plan-b": ("set", "plan_release"),
    "core-only-capability-paired-coverage": ("set", "dispatch"),
    "paired-capability-no-decoder": ("set", "decoder"),
    "unknown-extension-profile": ("set", "extension_family"),
    "partial-extension-profile": ("set", "extension_family"),
    "omitted-paired-object": ("remove", "decoded_objects"),
    "duplicated-paired-object": ("append", "decoded_objects"),
    "omitted-mandatory-requirement": ("remove", "requirement_outcomes"),
    "omitted-owner-mapping": ("remove", "mapping_outcomes"),
    "invented-mapping": ("append", "mapping_outcomes"),
    "zero-mappings-nonempty-obligations": ("set", "mapping_outcomes"),
    "row-count-mismatch": ("append", "rows"),
    "foreign-structural-identity": ("set", "authority_digest"),
    "substituted-effective-graph": ("set", "effective_graph_digest"),
    "traversable-counterpart-proof": ("set", "counterpart_traversable"),
    "altered-candidate-after-derivation": ("set", "candidate_byte_digest"),
    "reordered-authoritative-records": ("reorder", "authoritative_order"),
    "ambiguous-core-locator": ("append", "core_locations"),
    "namespace-collision": ("append", "core_identities"),
    "task067-authority-as-native-v2": ("set", "capability_version"),
    "foreign-rendering-conformance-chain": ("set", "rendering_plan"),
    "duplicated-extension": ("append", "extensions"),
    "missing-extension": ("set", "extensions"),
    "mapping-reordered": ("reorder", "mapping_outcomes"),
    "unknown-extension-data-semantic": ("set", "unknown_extension_semantic"),
}

REQUIREMENTS = tuple(
    (index, kind, value)
    for index, (kind, value) in enumerate((
        ("renderer", "briefforge:representative-paired-static-html-renderer:1.0.0"),
        ("media-type", "text/html;charset=utf-8"),
        ("output-count", "1"), ("asset-count", "0"),
        ("table-count", "1"), ("column-count", "5"),
    ))
)


def _set_path(document, path, value):
    cursor = document
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = value


def _reclose_envelope(document):
    document["fingerprint"] = domain_digest(
        "briefforge.task076.derivation-evidence.v2",
        {key: value for key, value in document.items() if key != "fingerprint"},
    )


def _reclose_record(document, fixture):
    payload = document["extensions"][0]["payload"]
    if fixture.get("recompute_semantic_digest"):
        payload["semantic_digest"] = domain_digest(
            "briefforge.task076.capability-core-semantic.v1"
            if fixture["artifact"] == "capability-v2-record.json"
            else "briefforge.task076.plan-core-semantic.v1",
            document["semantic"],
        )
    if fixture.get("recompute_fingerprint"):
        payload.pop("fingerprint", None)
        payload["fingerprint"] = domain_digest(
            "briefforge.task075.capability-declaration.v2"
            if fixture["artifact"] == "capability-v2-record.json"
            else "briefforge.task075.plan-extension.v2",
            payload,
        )


class Task077FrozenFixtureProductionMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = json.loads(FROZEN_PATH.read_text(encoding="utf-8"))
        cls.valid = json.loads(VALID_PATH.read_text(encoding="utf-8"))
        cls.frozen_envelope = json.loads(ENVELOPE_PATH.read_text(encoding="utf-8"))
        cls.capability = json.loads(CAPABILITY_PATH.read_text(encoding="utf-8"))

    def fixtures(self):
        return [
            item
            for family in ("fixtures", "record_fixtures", "structural_fixtures",
                           "correlated_fixtures")
            for item in self.frozen[family]
        ]

    def fixture_family(self, identity):
        return next(
            family
            for family in ("fixtures", "record_fixtures", "structural_fixtures",
                           "correlated_fixtures")
            if any(item["id"] == identity for item in self.frozen[family])
        )

    def canonical_envelope(self, candidate):
        frozen = self.frozen_envelope
        return construct_envelope(
            evidence_identity=frozen["evidence_identity"],
            operation_identity=frozen["operation_identity"],
            authorization_fingerprint=frozen["authorization_fingerprint"],
            issued_at_utc=frozen["issued_at_utc"],
            source_locator_identity=frozen["source_locator_identity"],
            candidate=candidate,
        )

    def closure(self, size):
        fixture = next(
            item for item in self.valid["fixtures"]
            if item.get("id") == f"plan-v2-predecessor-closure-{size}-record"
        )
        bundle = BCRPBundle(
            "briefforge-core-representation-profile", "1.0.0",
            tuple(BCRPRecord.from_document(copy.deepcopy(item["record"]))
                  for item in fixture["records"]),
        )
        return fixture, bundle

    def verify_control_closure(self, size):
        fixture, subject = self.closure(size)
        _, expected = self.closure(size)
        result = verify_plan_v2_predecessor_closure(
            subject, expected_bundle=expected, root_identity=fixture["root"],
            allow_publication_successors=size == 10,
        )
        self.assertEqual(result, tuple(record.identity for record in subject.records))
        return result

    def assert_plan_rejection(self, call, expected_reason):
        with self.assertRaises(PlanV2Rejected) as caught:
            call()
        error = caught.exception
        self.assertEqual(error.code, "PLAN_V2_REJECTED")
        self.assertEqual(error.owner, "renderer-compatibility-planning-v2")
        self.assertEqual(error.location, "plan-v2")
        self.assertEqual(error.reason, expected_reason)
        return error.reason

    def assert_derivation_rejection(self, call, *, code, location, reason):
        with self.assertRaises(DerivationEvidenceError) as caught:
            call()
        error = caught.exception
        self.assertEqual(error.code, code)
        self.assertEqual(error.owner, "paired-derivation-evidence-v2")
        self.assertEqual(error.location, location)
        self.assertEqual(error.reason, reason)
        self.assertEqual(error.message, reason)
        self.assertEqual(error.args, (reason,))
        self.assertEqual(str(error), reason)
        self.assertEqual(repr(error), f"DerivationEvidenceError({reason!r})")
        for attribute in ("args", "message", "code", "owner", "location", "reason"):
            with self.assertRaises(AttributeError):
                setattr(error, attribute, "forged")
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        self.assertTrue(error.__suppress_context__)
        for attribute in ("__cause__", "__context__", "__suppress_context__"):
            with self.assertRaises(AttributeError):
                setattr(error, attribute, OSError("forged"))
            with self.assertRaises(AttributeError):
                delattr(error, attribute)
        for attribute in ("_sealed", "_message", "_code", "_owner", "_location", "_reason"):
            with self.assertRaises(AttributeError):
                setattr(error, attribute, "forged")
            with self.assertRaises(AttributeError):
                delattr(error, attribute)
        # BaseException initialization bypasses ordinary __setattr__. The
        # public exception surface must still remain byte-for-byte stable.
        ValueError.__init__(error, "forged through inherited initializer")
        self.assertEqual(error.args, (reason,))
        self.assertEqual(error.message, reason)
        self.assertEqual(str(error), reason)
        self.assertEqual(repr(error), f"DerivationEvidenceError({reason!r})")
        return error.reason

    def hostile_candidate_bytes(self, fixture, control):
        document = json.loads(control.profile_bytes)
        candidate = next(record for record in document["records"]
                         if record["record_kind"] == "CandidatePresentationPackageRecord")
        extension = candidate["extensions"][0]
        semantics = json.loads(extension["payload"]["canonical_semantics"])
        identity = fixture["id"]
        mutation = fixture.get("mutation")
        sets = fixture.get("sets", {})
        consumed = set()

        if identity == "unknown-extension-profile":
            extension["name"] = mutation["value"]
            consumed.add("mutation")
        elif identity == "partial-extension-profile":
            extension["name"] = mutation["value"]
            consumed.add("mutation")
        elif identity == "omitted-paired-object":
            semantics["statements"].pop(mutation["value"])
            extension["payload"]["canonical_semantics"] = json.dumps(
                semantics, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            consumed.add("mutation")
        elif identity == "duplicated-paired-object":
            duplicate = copy.deepcopy(semantics["statements"][0])
            duplicate["identity"] = mutation["value"]
            semantics["statements"].append(duplicate)
            extension["payload"]["canonical_semantics"] = json.dumps(
                semantics, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            consumed.add("mutation")
        elif identity == "row-count-mismatch":
            extra = copy.deepcopy(semantics["table"]["rows"][0])
            extra["identity"] = mutation["value"]
            semantics["table"]["rows"].append(extra)
            extension["payload"]["canonical_semantics"] = json.dumps(
                semantics, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            consumed.add("mutation")
        elif identity == "reordered-authoritative-records":
            left, right = mutation["value"]
            document["records"][left], document["records"][right] = (
                document["records"][right], document["records"][left])
            consumed.add("mutation")
        elif identity == "namespace-collision":
            document["records"][0]["identity"] = mutation["value"]
            document["records"][1]["identity"] = mutation["value"]
            consumed.add("mutation")
        elif identity == "duplicated-extension":
            duplicate = copy.deepcopy(extension)
            duplicate["name"] = mutation["value"]
            candidate["extensions"].append(duplicate)
            consumed.add("mutation")
        elif identity == "missing-extension":
            candidate["extensions"] = mutation["value"]
            consumed.add("mutation")
        elif identity == "unknown-extension-data-semantic":
            extension["payload"][mutation["path"]] = mutation["value"]
            consumed.add("mutation")
        elif identity == "correlated-order-oracle-substitution":
            self.assertEqual(sets["authoritative_order"], sets["expected_authoritative_order"])
            document["records"][0]["identity"] = sets["authoritative_order"][0]
            document["records"][1]["identity"] = sets["authoritative_order"][1]
            consumed.update(sets)
        elif identity == "equal-length-decoded-substitution":
            values = sets["decoded_objects"]
            self.assertEqual(len(values), 2)
            semantics["statements"][0]["identity"] = values[0]
            semantics["statements"][1]["identity"] = values[1]
            extension["payload"]["canonical_semantics"] = json.dumps(
                semantics, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            consumed.update(sets)
        elif identity == "same-length-source-row-substitution":
            values = sets["rows"]
            self.assertEqual(len(values), 2)
            semantics["table"]["rows"][0]["identity"] = values[0]
            semantics["table"]["rows"][1]["identity"] = values[1]
            extension["payload"]["canonical_semantics"] = json.dumps(
                semantics, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            consumed.update(sets)
        else:
            self.fail(f"no exact Candidate-byte adapter for {identity}")

        self.assertEqual(consumed, set(key for key in ("mutation",) if fixture.get(key)) | set(sets))
        attacked = canonical_json(document)
        self.assertNotEqual(attacked, control.profile_bytes)
        return attacked

    def authority_blocked(self, fixture):
        control = load_generation8_candidate()
        authenticate_generation8_candidate(control)
        identity = fixture["id"]
        if identity in CANDIDATE_BYTE_ROWS:
            attacked = self.hostile_candidate_bytes(fixture, control)
            forged = replace(control, profile_bytes=attacked)
            with self.assertRaisesRegex(
                    ContractAuthenticationError,
                    "^generation-8 Candidate was not issued in this process$"):
                authenticate_generation8_candidate(forged)
            authenticate_generation8_candidate(control)
            return "Candidate exact bytes lack opaque predecessor authority"

        envelope = self.canonical_envelope(control)
        verify_envelope(envelope, candidate=control)
        document = envelope.to_document()
        sets = fixture["sets"]
        if identity == "correlated-candidate-substitution":
            self.assertEqual(sets["candidate_binding"], sets["candidate_identity"])
            document["candidate_identity"] = sets["candidate_identity"]
            expected_key = "candidate_identity"
        elif identity == "correlated-candidate-digest-oracle-substitution":
            self.assertEqual(sets["candidate_byte_digest"], sets["expected_candidate_byte_digest"])
            document["candidate_profile_byte_digest"] = sets["candidate_byte_digest"]
            expected_key = "candidate_profile_byte_digest"
        elif identity == "correlated-registry-digest-oracle-substitution":
            self.assertEqual(sets["registry_digest"], sets["expected_registry_digest"])
            document["registry_digest"] = sets["registry_digest"]
            expected_key = "registry_digest"
        elif identity == "correlated-effective-graph-oracle-substitution":
            self.assertEqual(sets["effective_graph_digest"], sets["expected_effective_graph_digest"])
            document["effective_graph_digest"] = sets["effective_graph_digest"]
            expected_key = "effective_graph_digest"
        else:
            self.fail(f"no correlated authority adapter for {identity}")
        _reclose_envelope(document)
        with self.assertRaisesRegex(
                DerivationEvidenceError,
                f"^independently reconstructed envelope differs at {expected_key}$"):
            verify_envelope(document, candidate=control)
        verify_envelope(envelope, candidate=control)
        authenticate_generation8_candidate(control)
        return f"independent Candidate reconstruction seals {expected_key}"

    def envelope_attack(self, fixture):
        candidate = load_generation8_candidate()
        control = self.canonical_envelope(candidate)
        verify_envelope(control, candidate=candidate)
        document = control.to_document()
        identity = fixture["id"]
        mutation = fixture.get("mutation")
        sets = fixture.get("sets", {})
        expected_key = None
        accepted_authority = None

        field_map = {
            "candidate-a-evidence-b": "candidate_identity",
            "registry-a-declares-b": "registry_identity",
            "same-registry-identity-different-bytes": "registry_digest",
            "foreign-structural-identity": "authorization_fingerprint",
            "substituted-effective-graph": "effective_graph_digest",
            "altered-candidate-after-derivation": "candidate_profile_byte_digest",
        }
        if identity in field_map:
            expected_key = field_map[identity]
            document[expected_key] = mutation["value"]
            if identity == "foreign-structural-identity":
                accepted_authority = control["authorization_fingerprint"]
        elif identity == "correlated-authority-digest-oracle-substitution":
            self.assertEqual(sets["authority_digest"], sets["expected_authority_digest"])
            expected_key = "authorization_fingerprint"
            document[expected_key] = sets["authority_digest"]
            accepted_authority = control["authorization_fingerprint"]
        elif identity == "correlated-requirement-substitution":
            self.assertEqual(sets["requirement_inventory"], sets["requirement_outcomes"])
            expected_key = "requirement_inventory_digest"
            document[expected_key] = domain_digest(
                "briefforge.task077.attacker-requirement-inventory.v1",
                sets["requirement_inventory"],
            )
        elif identity == "correlated-mapping-inventory-substitution":
            self.assertEqual(sets["mapping_inventory"], sets["mapping_outcomes"])
            expected_key = "mapping_inventory_digest"
            document[expected_key] = domain_digest(
                "briefforge.task077.attacker-mapping-inventory.v1",
                sets["mapping_inventory"],
            )
        else:
            self.fail(f"no envelope adapter for {identity}")

        _reclose_envelope(document)
        if accepted_authority is not None:
            expected = "envelope authorization_fingerprint differs from accepted authority"
            reason = self.assert_derivation_rejection(
                lambda: verify_envelope(
                    document, candidate=candidate,
                    expected_authorization_fingerprint=accepted_authority,
                ),
                code="DERIVATION_AUTHORITY_BINDING_MISMATCH",
                location="/authorization_fingerprint",
                reason=expected,
            )
        else:
            expected = f"independently reconstructed envelope differs at {expected_key}"
            reason = self.assert_derivation_rejection(
                lambda: verify_envelope(document, candidate=candidate),
                code="DERIVATION_RECONSTRUCTION_MISMATCH",
                location=f"/{expected_key}",
                reason=expected,
            )
        verify_envelope(control, candidate=candidate)
        authenticate_generation8_candidate(candidate)
        locator, recorded_field = DERIVATION_ROUTE_EVIDENCE[identity]
        self.assertEqual(recorded_field, expected_key)
        family = self.fixture_family(identity)
        index = next(index for index, item in enumerate(self.frozen[family])
                     if item["id"] == identity)
        self.assertEqual(locator, f"/{family}/{index}")
        return reason

    def abstract_closure_attack(self, fixture):
        identity = fixture["id"]
        size = 10 if identity == "foreign-rendering-conformance-chain" else 8
        self.verify_control_closure(size)
        valid_fixture, expected = self.closure(size)
        _, subject = self.closure(size)
        documents = [record.to_document() for record in subject.records]
        plan = next(record for record in documents
                    if record["record_kind"] == "RendererCompatibilityPlanRecord")
        capability = next(record for record in documents
                          if record["record_kind"] == "RendererCapabilityDeclarationRecord")
        payload = plan["extensions"][0]["payload"]
        mutation = fixture["mutation"]
        value = mutation["value"]

        if identity == "capability-a-plan-b":
            payload["capability_identity"] = value
            plan["semantic"]["renderer_capability_ref"] = value
            plan["extensions"][0]["target_refs"][3] = value
        elif identity == "release-a-plan-b":
            payload["release_identity"] = value
            plan["extensions"][0]["target_refs"][2] = value
        elif identity == "core-only-capability-paired-coverage":
            self.assertEqual(value, "core-only")
            capability["extensions"][0]["version"] = "1.0.0"
            capability["semantic"]["capability_profile_version"] = "1.0.0"
        elif identity == "omitted-mandatory-requirement":
            payload["requirement_outcomes"].pop(value)
        elif identity == "omitted-owner-mapping":
            payload["mapping_outcomes"].pop(value)
        elif identity == "invented-mapping":
            invented = copy.deepcopy(payload["mapping_outcomes"][0])
            invented[1][2][3] = value
            invented[2] = value
            payload["mapping_outcomes"].append(invented)
        elif identity == "zero-mappings-nonempty-obligations":
            payload["mapping_outcomes"] = value
        elif identity == "task067-authority-as-native-v2":
            capability["extensions"][0]["version"] = value
            capability["semantic"]["capability_profile_version"] = value
        elif identity == "foreign-rendering-conformance-chain":
            plan["identity"] = value
            payload["plan_identity"] = value
            plan["extensions"][0]["target_refs"][0] = value
            conformance = next(record for record in documents
                               if record["record_kind"] == "SemanticArtifactConformanceRecord")
            conformance.setdefault("metadata", {})[mutation["path"]] = value
        elif identity == "mapping-reordered":
            left, right = value
            outcomes = payload["mapping_outcomes"]
            outcomes[left], outcomes[right] = outcomes[right], outcomes[left]
        else:
            self.fail(f"no abstract closure adapter for {identity}")

        attacked = BCRPBundle(
            subject.profile_identity, subject.profile_version,
            tuple(BCRPRecord.from_document(document) for document in documents),
        )
        self.assertNotEqual(
            [record.to_document() for record in attacked.records],
            [record.to_document() for record in expected.records],
        )
        reason = self.assert_plan_rejection(lambda: verify_plan_v2_predecessor_closure(
            attacked, expected_bundle=expected, root_identity=valid_fixture["root"],
            allow_publication_successors=size == 10,
        ), CLOSURE_RECORD_MISMATCH)
        self.verify_control_closure(size)
        return reason

    def record_closure_attack(self, fixture):
        self.verify_control_closure(8)
        valid_fixture, expected = self.closure(8)
        _, subject = self.closure(8)
        documents = [record.to_document() for record in subject.records]
        kind = ("RendererCapabilityDeclarationRecord"
                if fixture["artifact"] == "capability-v2-record.json"
                else "RendererCompatibilityPlanRecord")
        index = next(i for i, record in enumerate(documents) if record["record_kind"] == kind)
        attacked_record = documents[index]
        mutations = fixture.get("mutations", [fixture.get("mutation")])
        self.assertTrue(mutations)
        for mutation in mutations:
            _set_path(attacked_record, mutation["path"], mutation["value"])
        _reclose_record(attacked_record, fixture)
        attacked = BCRPBundle(
            subject.profile_identity, subject.profile_version,
            tuple(BCRPRecord.from_document(document) for document in documents),
        )
        reason = self.assert_plan_rejection(lambda: verify_plan_v2_predecessor_closure(
            attacked, expected_bundle=expected, root_identity=valid_fixture["root"],
            allow_publication_successors=False,
        ), CLOSURE_RECORD_MISMATCH)
        self.verify_control_closure(8)
        return reason

    def structural_closure_attack(self, fixture):
        size = len(fixture["records"])
        self.assertIn(size, (8, 10))
        self.assertEqual(fixture["kind"], "predecessor-closure")
        self.assertEqual(fixture["expected"], "FAIL")
        self.assertEqual(fixture["expected_findings"], ["incomplete-predecessor-closure"])
        self.verify_control_closure(size)
        valid_fixture, expected = self.closure(size)

        # Account for every frozen wrapper field before selecting the lawful route.
        # The production comparator accepts complete records; TASK-076's wrapper
        # refs/fingerprint remain data-only evidence and must never be replaced by
        # an invented record mutation.
        self.assertEqual(len(fixture["records"]), len(valid_fixture["records"]))
        mismatch_locators = set()
        wrapper_keys = {"kind", "identity", "refs", "record", "fingerprint"}
        for index, (item, valid_item) in enumerate(
                zip(fixture["records"], valid_fixture["records"])):
            self.assertEqual(set(item), wrapper_keys)
            for field in wrapper_keys:
                if item[field] != valid_item[field]:
                    mismatch_locators.add(f"/records/{index}/{field}")
            self.assertEqual(item["kind"], item["record"]["record_kind"])
            self.assertEqual(item["identity"], item["record"]["identity"])
            computed = domain_digest(
                "briefforge.task076.predecessor-closure-record-bytes.v2",
                item["record"],
            )
            if fixture["id"] == "plan-v2-predecessor-closure-altered-fingerprint" and index == 0:
                self.assertNotEqual(item["fingerprint"], computed)
            else:
                self.assertEqual(item["fingerprint"], computed)
        for field in ("root", "record_order", "expected_reachable"):
            if fixture[field] != valid_fixture[field]:
                mismatch_locators.add(f"/{field}")

        attacked = BCRPBundle(
            "briefforge-core-representation-profile", "1.0.0",
            tuple(BCRPRecord.from_document(copy.deepcopy(item["record"]))
                  for item in fixture["records"]),
        )
        identity = fixture["id"]
        if identity in WRAPPER_ONLY_CLOSURE_ROWS:
            expected_locator = (
                "/records/7/refs"
                if identity == "plan-v2-predecessor-closure-unreachable-extra"
                else "/records/0/fingerprint"
            )
            self.assertEqual(mismatch_locators, {expected_locator})
            result = verify_plan_v2_predecessor_closure(
                attacked, expected_bundle=expected, root_identity=fixture["root"],
                allow_publication_successors=False,
            )
            self.assertEqual(result, tuple(record.identity for record in attacked.records))
            self.verify_control_closure(size)
            return f"data-only TASK-076 wrapper mismatch at {expected_locator}"

        expected_reason = (
            CLOSURE_ROOT_MISMATCH
            if identity == "plan-v2-predecessor-closure-nonplan-root"
            else CLOSURE_RECORD_MISMATCH
        )
        reason = self.assert_plan_rejection(lambda: verify_plan_v2_predecessor_closure(
            attacked, expected_bundle=expected, root_identity=fixture["root"],
            allow_publication_successors=size == 10,
        ), expected_reason)
        self.verify_control_closure(size)
        return reason

    def generic_attack(self, fixture):
        source = fixture["input"]
        self.assertEqual(fixture["kind"], "planner-cardinality")
        self.assertEqual(fixture["N"], 7)
        self.assertEqual(fixture["expected"], "FAIL")
        self.assertEqual(fixture["expected_findings"], ["duplicate-generic-row-identity"])
        self.assertEqual(source["rows"], source["mapping_inventory"])
        self.assertEqual(source["rows"], source["mapping_outcomes"])
        self.assertEqual(source["obligations"], ["obligation:generic"])
        requirements = REQUIREMENTS if source["obligations"] else ()
        self.assertTrue(requirements)
        capability = self.capability["extensions"][0]["payload"]

        def mappings(rows):
            return tuple(
                (index, ("candidate-fingerprint", "effective-graph-digest",
                         ("briefforge:paired-terminal", "3.0.0", "Row", row)), row)
                for index, row in enumerate(rows)
            )

        control_rows = [f"row:control-{index}" for index in range(fixture["N"])]
        self.assertEqual(len(plan_paired_v3_inventory(
            requirements, mappings(control_rows), capability,
            capability_fingerprint=capability["fingerprint"],
        )[1]), fixture["N"])
        reason = self.assert_plan_rejection(lambda: plan_paired_v3_inventory(
            requirements, mappings(source["rows"]), capability,
            capability_fingerprint=capability["fingerprint"],
        ), "Mapping inventory contains duplicate rows.")
        self.assertEqual(len(plan_paired_v3_inventory(
            requirements, mappings(control_rows), capability,
            capability_fingerprint=capability["fingerprint"],
        )[1]), fixture["N"])
        return reason

    def non_input_proof(self, fixture):
        candidate = load_generation8_candidate()
        identity = fixture["id"]
        mutation = fixture["mutation"]
        if identity == "paired-capability-no-decoder":
            self.assertEqual((mutation["path"], mutation["value"]), ("decoder", False))
            self.assertNotIn("decoder", inspect.signature(decode_paired_inventory).parameters)
            decoded = decode_paired_inventory(candidate)
            self.assertEqual(len(decoded), 4)
            self.assertTrue(decoded[2])
            self.assertIsInstance(decoded[2], tuple)
            self.assertEqual(decode_paired_inventory(candidate), decoded)
            return "typed canonical decode has no caller decoder input"

        if identity == "traversable-counterpart-proof":
            self.assertEqual((mutation["path"], mutation["value"]),
                             ("counterpart_traversable", True))
            interpretation = interpret_paired_candidate(candidate)
            self.assertTrue(interpretation.counterparts)
            self.assertTrue(all(isinstance(item, CounterpartProof)
                                for item in interpretation.counterparts))
            self.assertTrue(all(item.traversable is False
                                for item in interpretation.counterparts))
            hostile = replace(interpretation.counterparts[0], traversable=mutation["value"])
            self.assertTrue(hostile.traversable)
            for owner in (interpret_paired_candidate, construct_envelope, verify_envelope,
                          plan_paired_v3_inventory, verify_plan_v2_predecessor_closure):
                parameters = inspect.signature(owner).parameters
                self.assertFalse({"counterpart", "counterparts", "counterpart_proof",
                                  "traversable"} & set(parameters))
            self.assertEqual(interpret_paired_candidate(candidate), interpretation)
            return "public DTO switch exists but no accepted owner consumes caller proof"

        if identity == "ambiguous-core-locator":
            self.assertEqual((mutation["operation"], mutation["path"]),
                             ("append", "core_locations"))
            self.assertNotIn("registry", inspect.signature(resolve_core_locator).parameters)
            nodes, _ = execute_core_registry(candidate)
            pointers = [node.pointer for node in nodes]
            identities = [node.dqi for node in nodes]
            self.assertEqual(len(pointers), len(set(pointers)))
            self.assertEqual(len(identities), len(set(identities)))
            matches = [node for node in nodes if node.pointer == mutation["value"]]
            self.assertLessEqual(len(matches), 1)
            if matches:
                resolved = resolve_core_locator(
                    mutation["value"], expected_kind=matches[0].dqi[2], candidate=candidate)
                self.assertEqual(resolved.dqi, matches[0].dqi)
            else:
                with self.assertRaises(CoreRegistryError):
                    resolve_core_locator(
                        mutation["value"], expected_kind="CandidatePresentationPackageRecord",
                        candidate=candidate,
                    )
            repeated_nodes, _ = execute_core_registry(candidate)
            self.assertEqual(repeated_nodes, nodes)
            return "immutable authenticated registry has unique pointer and identity inventories"

        self.fail(f"no typed non-input proof for {identity}")

    def test_exact_63_fixture_authority_aware_production_matrix(self):
        # Filesystem failures are represented only by stable production-owned
        # metadata. Raw errno, path, cause, and context text must not escape.
        filesystem_failures = []
        with patch.object(
            derivation_module.Path, "read_bytes",
            side_effect=OSError("host-specific-implementation-path"),
        ), self.assertRaises(DerivationEvidenceError) as implementation_failure:
            derivation_module._implementation_digest()
        filesystem_failures.append(implementation_failure.exception)
        with patch.object(
            derivation_module.os, "open",
            side_effect=OSError("host-specific-reload-path"),
        ), self.assertRaises(DerivationEvidenceError) as reload_failure:
            derivation_module._read_bound_file(7, "evidence.json")
        filesystem_failures.append(reload_failure.exception)
        for error in filesystem_failures:
            self.assertIsNone(error.__cause__)
            self.assertIsNone(error.__context__)
            rendered = "".join(traceback.format_exception(error))
            self.assertNotIn("host-specific", rendered)

        fixtures = self.fixtures()
        ids = [fixture["id"] for fixture in fixtures]
        self.assertEqual(len(ids), 63)
        self.assertEqual(len(ids), len(set(ids)))
        descriptor_rows = {
            fixture["id"]: (fixture["mutation"]["operation"],
                            fixture["mutation"]["path"])
            for fixture in fixtures
            if isinstance(fixture.get("mutation"), dict)
            and "operation" in fixture["mutation"]
        }
        self.assertEqual(descriptor_rows, MUTATION_DESCRIPTOR_BY_ID)
        for fixture in self.frozen["record_fixtures"]:
            mutations = fixture.get("mutations", [fixture.get("mutation")])
            self.assertTrue(mutations)
            self.assertTrue(all(isinstance(item.get("path"), list) and item["path"]
                                and "value" in item for item in mutations))
        self.assertEqual(len(AUTHORITY_BLOCKED), 17)
        self.assertEqual(len(NON_INPUT), 3)
        self.assertEqual(set(DERIVATION_ROUTE_EVIDENCE), ENVELOPE_ROWS)
        self.assertEqual(len(DERIVATION_ROUTE_EVIDENCE), 9)
        self.assertFalse(AUTHORITY_BLOCKED & NON_INPUT)
        self.assertEqual(len(set(ids) - AUTHORITY_BLOCKED - NON_INPUT), 43)
        self.assertEqual(
            set(ids) - AUTHORITY_BLOCKED - NON_INPUT,
            ENVELOPE_ROWS | ABSTRACT_CLOSURE_ROWS |
            {item["id"] for item in self.frozen["record_fixtures"]} |
            {item["id"] for item in self.frozen["structural_fixtures"]},
        )

        outcomes = {}
        self.verify_control_closure(8)
        self.verify_control_closure(10)
        for fixture in fixtures:
            identity = fixture["id"]
            family = self.fixture_family(identity)
            with self.subTest(id=identity, family=family):
                if identity in AUTHORITY_BLOCKED:
                    category = "authority-blocked"
                    evidence = self.authority_blocked(fixture)
                elif identity in NON_INPUT:
                    category = "production-computed-or-non-input"
                    evidence = self.non_input_proof(fixture)
                elif identity in ENVELOPE_ROWS:
                    category = "semantically-representable"
                    evidence = self.envelope_attack(fixture)
                elif identity in ABSTRACT_CLOSURE_ROWS:
                    category = "semantically-representable"
                    evidence = self.abstract_closure_attack(fixture)
                elif family == "record_fixtures":
                    category = "semantically-representable"
                    evidence = self.record_closure_attack(fixture)
                elif identity == "generic-cardinality-duplicate-row":
                    category = "semantically-representable"
                    evidence = self.generic_attack(fixture)
                elif family == "structural_fixtures":
                    category = "semantically-representable"
                    evidence = self.structural_closure_attack(fixture)
                else:
                    self.fail(f"unrouted frozen fixture {identity}")
                self.assertTrue(fixture["expected_findings"])
                self.assertTrue(evidence)
                outcomes[identity] = (category, tuple(fixture["expected_findings"]), evidence)

        self.assertEqual(set(outcomes), set(ids))
        self.assertEqual(sum(value[0] == "semantically-representable"
                             for value in outcomes.values()), 43)
        self.assertEqual(sum(value[0] == "authority-blocked"
                             for value in outcomes.values()), 17)
        self.assertEqual(sum(value[0] == "production-computed-or-non-input"
                             for value in outcomes.values()), 3)
        self.verify_control_closure(8)
        self.verify_control_closure(10)


if __name__ == "__main__":
    unittest.main()
