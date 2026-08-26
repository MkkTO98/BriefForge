"""BCRP 1.0 representation, validation, and golden-corpus vertical slice.

These tests deliberately do not import or invoke the existing runtime or renderer.
"""

from __future__ import annotations

from copy import deepcopy
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
FIXTURES = PROJECT_ROOT / "tests" / "fixtures" / "bcrp"
sys.path.insert(0, str(SRC))

from briefforge.bcrp import (  # noqa: E402
    PROFILE_ID,
    PROFILE_VERSION,
    BundleLoadError,
    artifact_equal,
    bundle_from_canonical_json,
    canonical_json_bytes,
    canonicalize_exact_decimal,
    canonicalize_timestamp,
    fingerprint_bundle,
    load_bundle,
    presentation_equivalent,
    profile_instance_equal,
    reconstruct_graph,
    semantic_equal,
    validate_bundle,
)
from briefforge.bcrp.corpus import (  # noqa: E402
    CASE_IDS,
    INVALID_VARIANT_IDS,
    load_case,
    materialize_invalid_variant,
)


class BCRPGoldenCorpusTests(unittest.TestCase):
    maxDiff = None

    def test_profile_identity_and_exact_case_inventory(self):
        self.assertEqual(PROFILE_ID, "briefforge-core-representation-profile")
        self.assertEqual(PROFILE_VERSION, "1.0.0")
        self.assertEqual(
            CASE_IDS,
            (
                "case-1-demographic-correlation-publication",
                "case-2-synthetic-company-comparison",
                "case-3-synthetic-company-macro-selection",
            ),
        )
        self.assertEqual(len(INVALID_VARIANT_IDS), 30)

    def test_all_valid_cases_pass_every_applicable_layer(self):
        for case_id in CASE_IDS:
            with self.subTest(case_id=case_id):
                bundle = load_case(case_id)
                result = validate_bundle(bundle)
                self.assertFalse(result.blocking, result.findings)
                self.assertEqual(result.findings, ())
                self.assertEqual(result.executed_layers, tuple(f"L{i}" for i in range(7)))

    def test_all_invalid_variants_emit_every_declared_primary_finding(self):
        expectations = json.loads((FIXTURES / "expectations.json").read_text(encoding="utf-8"))
        observed = set()
        for case_id, variants in expectations["invalid_variants"].items():
            for variant_id, expectation in variants.items():
                observed.add(variant_id)
                with self.subTest(case_id=case_id, variant_id=variant_id):
                    bundle = materialize_invalid_variant(case_id, variant_id)
                    first = validate_bundle(bundle)
                    second = validate_bundle(bundle)
                    self.assertEqual(first, second)
                    self.assertTrue(first.blocking)
                    actual = {
                        (finding.layer, finding.family, finding.severity, finding.blocking_consequence)
                        for finding in first.findings
                    }
                    for required in expectation["required_findings"]:
                        required_tuple = (
                            required["layer"],
                            required["family"],
                            required["severity"],
                            required["blocked_transition"],
                        )
                        self.assertIn(required_tuple, actual, first.findings)
        self.assertEqual(observed, set(INVALID_VARIANT_IDS))

    def test_valid_cases_round_trip_with_stable_equality_and_fingerprints(self):
        for case_id in CASE_IDS:
            with self.subTest(case_id=case_id):
                original = load_case(case_id)
                reconstruct_graph(original)
                first_bytes = canonical_json_bytes(original, domain="profile-instance")
                second_bytes = canonical_json_bytes(original, domain="profile-instance")
                self.assertEqual(first_bytes, second_bytes)
                reloaded = bundle_from_canonical_json(first_bytes)
                self.assertFalse(validate_bundle(reloaded).blocking)
                self.assertTrue(semantic_equal(original, reloaded))
                self.assertTrue(profile_instance_equal(original, reloaded))
                for domain in ("candidate-semantic", "profile-instance", "release-semantic", "manifest-instance"):
                    self.assertEqual(
                        fingerprint_bundle(original, domain=domain),
                        fingerprint_bundle(reloaded, domain=domain),
                    )

    def test_bundle_relocation_does_not_change_semantic_fingerprint(self):
        source = FIXTURES / CASE_IDS[0]
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_path = Path(first) / "alpha"
            second_path = Path(second) / "deep" / "beta"
            shutil.copytree(source, first_path)
            shutil.copytree(source, second_path)
            self.assertEqual(
                fingerprint_bundle(load_bundle(first_path), domain="candidate-semantic"),
                fingerprint_bundle(load_bundle(second_path), domain="candidate-semantic"),
            )

    def test_independence_from_runtime_renderer_upstream_network_and_database(self):
        forbidden_import_prefixes = (
            "briefforge.runtime",
            "briefforge.renderer_adapter",
            "sqlite3",
            "urllib",
            "http",
            "requests",
            "AtlasForge",
            "MacroForge",
            "KnowledgeForge",
            "InsightForge",
        )
        before = set(sys.modules)
        for case_id in CASE_IDS:
            bundle = load_case(case_id)
            self.assertFalse(validate_bundle(bundle).blocking)
            canonical_json_bytes(bundle, domain="profile-instance")
        newly_loaded = set(sys.modules) - before
        self.assertFalse(
            any(name == prefix or name.startswith(prefix + ".") for name in newly_loaded for prefix in forbidden_import_prefixes),
            sorted(newly_loaded),
        )

    def test_fresh_bcrp_import_does_not_import_runtime_or_renderer_modules(self):
        code = (
            "import json,sys; import briefforge.bcrp; "
            "print(json.dumps(sorted(n for n in sys.modules if n in "
            "{'briefforge.runtime','briefforge.renderer_adapter','briefforge.presentation_models'})))"
        )
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(SRC)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, "-B", "-c", code],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
            cwd=PROJECT_ROOT,
        )
        self.assertEqual(json.loads(completed.stdout), [])


class BCRPLoaderSafetyTests(unittest.TestCase):
    def _minimal_record(self, identity: str = "brief:test"):
        return {
            "record_kind": "PresentationBriefRecord",
            "identity": identity,
            "profile": {"identity": PROFILE_ID, "version": PROFILE_VERSION},
            "semantic": {
                "organizing_purpose": {"id": "purpose:test", "statement": "Test purpose"},
                "audiences": [{"id": "audience:test", "description": "Test reader"}],
            },
            "extensions": [],
        }

    def _write_minimal_bundle(self, root: Path, *, location: str = "records/brief.json", record=None):
        record = record or self._minimal_record()
        target = root / location
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
        index = {
            "format": "briefforge-bcrp-json-bundle-v1",
            "profile": {"identity": PROFILE_ID, "version": PROFILE_VERSION},
            "records": [{"record_kind": record["record_kind"], "identity": record["identity"], "profile_version": PROFILE_VERSION, "location": location}],
        }
        (root / "bundle.json").write_text(json.dumps(index), encoding="utf-8")

    def test_rejects_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            root.mkdir(exist_ok=True)
            (root / "bundle.json").write_text(
                '{"format":"briefforge-bcrp-json-bundle-v1","format":"duplicate","profile":{"identity":"briefforge-core-representation-profile","version":"1.0.0"},"records":[]}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(BundleLoadError, "duplicate JSON object key"):
                load_bundle(root)

    def test_rejects_absolute_and_parent_traversal_locations(self):
        for unsafe in ("/tmp/record.json", "../record.json", "records/../../record.json"):
            with self.subTest(unsafe=unsafe), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                index = {
                    "format": "briefforge-bcrp-json-bundle-v1",
                    "profile": {"identity": PROFILE_ID, "version": PROFILE_VERSION},
                    "records": [{"record_kind": "PresentationBriefRecord", "identity": "brief:test", "profile_version": PROFILE_VERSION, "location": unsafe}],
                }
                (root / "bundle.json").write_text(json.dumps(index), encoding="utf-8")
                with self.assertRaisesRegex(BundleLoadError, "bundle-relative"):
                    load_bundle(root)

    def test_rejects_duplicate_transport_locations_and_semantic_identities(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_minimal_bundle(root)
            index = json.loads((root / "bundle.json").read_text(encoding="utf-8"))
            index["records"].append(dict(index["records"][0]))
            (root / "bundle.json").write_text(json.dumps(index), encoding="utf-8")
            with self.assertRaisesRegex(BundleLoadError, "duplicate transport location"):
                load_bundle(root)

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_minimal_bundle(root)
            second = self._minimal_record()
            (root / "records" / "second.json").write_text(json.dumps(second), encoding="utf-8")
            index = json.loads((root / "bundle.json").read_text(encoding="utf-8"))
            duplicate = dict(index["records"][0])
            duplicate["location"] = "records/second.json"
            index["records"].append(duplicate)
            (root / "bundle.json").write_text(json.dumps(index), encoding="utf-8")
            with self.assertRaisesRegex(BundleLoadError, "duplicate semantic identity"):
                load_bundle(root)

    def test_rejects_nonstandard_constants_floats_nulls_and_unsupported_major(self):
        bad_fragments = (
            ('{"x":NaN}', "non-standard JSON constant"),
            ('{"x":Infinity}', "non-standard JSON constant"),
            ('{"x":1.5}', "floating-point JSON number"),
            ('{"x":null}', "transport null"),
        )
        for fragment, message in bad_fragments:
            with self.subTest(fragment=fragment), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                self._write_minimal_bundle(root)
                (root / "records" / "brief.json").write_text(fragment, encoding="utf-8")
                with self.assertRaisesRegex(BundleLoadError, message):
                    load_bundle(root)

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_minimal_bundle(root)
            index = json.loads((root / "bundle.json").read_text(encoding="utf-8"))
            index["profile"]["version"] = "2.0.0"
            index["records"][0]["profile_version"] = "2.0.0"
            (root / "bundle.json").write_text(json.dumps(index), encoding="utf-8")
            with self.assertRaisesRegex(BundleLoadError, "unsupported profile major version"):
                load_bundle(root)

    def test_rejects_excessive_nesting_and_malformed_unicode(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_minimal_bundle(root)
            nested = "{}"
            for _ in range(70):
                nested = '{"x":' + nested + "}"
            (root / "records" / "brief.json").write_text(nested, encoding="utf-8")
            with self.assertRaisesRegex(BundleLoadError, "nesting"):
                load_bundle(root)

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_minimal_bundle(root)
            data = (root / "records" / "brief.json").read_bytes()
            (root / "records" / "brief.json").write_bytes(data[:-1] + b'\xff}')
            with self.assertRaisesRegex(BundleLoadError, "UTF-8"):
                load_bundle(root)

    def test_external_references_are_opaque_and_never_followed(self):
        bundle = load_case(CASE_IDS[0])
        material = next(record for record in bundle.records if record.kind == "PortablePresentationMaterialRecord")
        external = deepcopy(material.semantic["external_references"][0])
        external["locator"] = "https://example.invalid/never-fetch"
        material.semantic["external_references"][0].update(external)
        self.assertFalse(validate_bundle(bundle).blocking)


class BCRPCanonicalizationAndEqualityTests(unittest.TestCase):
    def test_exact_decimal_normalization(self):
        equivalent = (
            {"coefficient": "100", "scale": 2},
            {"coefficient": "10", "scale": 1},
            {"coefficient": "1", "scale": 0},
        )
        normalized = [canonicalize_exact_decimal(value) for value in equivalent]
        self.assertEqual(normalized, [{"coefficient": "1", "scale": 0}] * 3)
        self.assertEqual(canonicalize_exact_decimal({"coefficient": "-0", "scale": 200}), {"coefficient": "0", "scale": 0})
        huge = {"coefficient": "9" * 500, "scale": 0}
        self.assertEqual(canonicalize_exact_decimal(huge), huge)

    def test_approximate_values_require_an_explicit_approximation_qualifier(self):
        bundle = load_case(CASE_IDS[1])
        material = next(record for record in bundle.records if record.kind == "PortablePresentationMaterialRecord")
        value = next(item for item in material.semantic["values"] if item["id"] == "value:aster-small-nonzero")
        value["approximate"] = True
        result = validate_bundle(bundle, through_layer="L2")
        self.assertIn("semantic-state-integrity", {finding.family for finding in result.findings})

    def test_timestamp_normalization_and_implicit_local_rejection(self):
        self.assertEqual(canonicalize_timestamp("2026-07-16T12:30:00+02:00"), "2026-07-16T10:30:00Z")
        self.assertEqual(canonicalize_timestamp("2026-07-16T10:30:00.120000Z"), "2026-07-16T10:30:00.12Z")
        with self.assertRaisesRegex(ValueError, "explicit offset"):
            canonicalize_timestamp("2026-07-16T10:30:00")

    def test_object_order_record_order_unicode_and_line_endings_do_not_change_semantics(self):
        original = load_case(CASE_IDS[0])
        changed = deepcopy(original)
        changed.records = tuple(reversed(changed.records))
        candidate = next(record for record in changed.records if record.kind == "CandidatePresentationPackageRecord")
        purpose = candidate.semantic["organizing_purpose"]
        purpose["statement"] = purpose["statement"].replace("é", "e\u0301").replace("\n", "\r\n")
        candidate.semantic = dict(reversed(tuple(candidate.semantic.items())))
        self.assertTrue(semantic_equal(original, changed))
        self.assertEqual(
            fingerprint_bundle(original, domain="candidate-semantic"),
            fingerprint_bundle(changed, domain="candidate-semantic"),
        )

    def test_ordered_composition_children_and_meaningful_whitespace_are_preserved(self):
        original = load_case(CASE_IDS[0])
        changed = deepcopy(original)
        candidate = next(record for record in changed.records if record.kind == "CandidatePresentationPackageRecord")
        candidate.semantic["sections"][0]["children"] = list(reversed(candidate.semantic["sections"][0]["children"]))
        self.assertFalse(semantic_equal(original, changed))

        changed = deepcopy(original)
        candidate = next(record for record in changed.records if record.kind == "CandidatePresentationPackageRecord")
        candidate.semantic["statements"][0]["text"] += " "
        self.assertFalse(semantic_equal(original, changed))

    def test_transport_metadata_reverse_indexes_and_renderer_artifacts_are_outside_candidate_scope(self):
        original = load_case(CASE_IDS[0])
        changed = deepcopy(original)
        changed.index["comment"] = "transport-only"
        changed.derived_reverse_index["anything"] = ["disposable"]
        audit = next(record for record in changed.records if record.kind == "GeneratedArtifactAuditRecord")
        audit.semantic["artifact"]["digest"] = "sha256:" + "f" * 64
        manifest = next(record for record in changed.records if record.kind == "PublicationManifestRecord")
        manifest.semantic["generated_label"] = "different derivative label"
        self.assertTrue(semantic_equal(original, changed))
        self.assertEqual(
            fingerprint_bundle(original, domain="candidate-semantic"),
            fingerprint_bundle(changed, domain="candidate-semantic"),
        )
        self.assertFalse(profile_instance_equal(original, changed))

    def test_semantic_change_changes_candidate_fingerprint_and_display_only_extension_does_not(self):
        original = load_case(CASE_IDS[1])
        changed = deepcopy(original)
        candidate = next(record for record in changed.records if record.kind == "CandidatePresentationPackageRecord")
        candidate.semantic["statements"][0]["text"] += " changed"
        self.assertNotEqual(
            fingerprint_bundle(original, domain="candidate-semantic"),
            fingerprint_bundle(changed, domain="candidate-semantic"),
        )

        changed = deepcopy(original)
        candidate = next(record for record in changed.records if record.kind == "CandidatePresentationPackageRecord")
        candidate.extensions.append(
            {
                "owner_namespace": "example:display",
                "name": "hint",
                "version": "1.0.0",
                "authority_ref": "authority:presentation",
                "scope": "record",
                "target_refs": [candidate.identity],
                "criticality": "optional",
                "character": "display-only",
                "validation_contract": "example:display:v1",
                "preservation": "discardable",
                "payload": {"color": "blue"},
            }
        )
        self.assertTrue(semantic_equal(original, changed))
        self.assertFalse(profile_instance_equal(original, changed))

    def test_missing_is_distinct_from_explicit_zero_and_rounded_display_zero(self):
        bundle = load_case(CASE_IDS[1])
        material = next(record for record in bundle.records if record.kind == "PortablePresentationMaterialRecord")
        values = {value["id"]: value for value in material.semantic["values"]}
        zero = values["value:aster-zero"]
        missing = values["value:boreal-missing"]
        small = values["value:aster-small-nonzero"]
        self.assertEqual(zero["value_state"], "explicit-zero")
        self.assertEqual(zero["payload"], {"coefficient": "0", "scale": 0})
        self.assertEqual(missing["value_state"], "missing-not-provided")
        self.assertNotIn("payload", missing)
        self.assertEqual(small["value_state"], "present")
        self.assertNotEqual(canonicalize_exact_decimal(small["payload"]), {"coefficient": "0", "scale": 0})
        self.assertEqual(small["display"]["rounded_text"], "0.0")

    def test_artifact_equality_and_presentation_equivalence_are_distinct(self):
        self.assertTrue(artifact_equal({"a.html": b"same"}, {"a.html": b"same"}))
        self.assertFalse(artifact_equal({"a.html": b"same"}, {"a.html": b"different"}))
        bundle = load_case(CASE_IDS[0])
        conformance = next(record for record in bundle.records if record.kind == "SemanticArtifactConformanceRecord")
        self.assertTrue(presentation_equivalent(bundle, conformance.identity))
        changed = deepcopy(bundle)
        conformance = next(record for record in changed.records if record.kind == "SemanticArtifactConformanceRecord")
        conformance.semantic["semantic_pass"] = False
        self.assertFalse(presentation_equivalent(changed, conformance.identity))

    def test_fingerprint_declares_domain_root_profile_algorithm_and_scope(self):
        bundle = load_case(CASE_IDS[0])
        result = fingerprint_bundle(bundle, domain="candidate-semantic")
        self.assertEqual(result.domain, "candidate-semantic")
        self.assertEqual(result.profile_identity, PROFILE_ID)
        self.assertEqual(result.profile_version, PROFILE_VERSION)
        self.assertEqual(result.algorithm, "sha256")
        self.assertEqual(result.canonicalization, "bcrp-semantic-canonicalization:1.0.0")
        self.assertTrue(result.root_identity.startswith("candidate:"))
        self.assertEqual(len(result.digest), 64)

    def test_no_authoritative_fingerprint_when_validation_prerequisites_fail(self):
        invalid = materialize_invalid_variant(CASE_IDS[0], "C1-I02")
        with self.assertRaisesRegex(ValueError, "fingerprint prerequisites"):
            fingerprint_bundle(invalid, domain="candidate-semantic")


class BCRPStructuralAndLayeringTests(unittest.TestCase):
    def test_standard_library_native_validator_is_the_executed_structure_authority(self):
        module = importlib.import_module("briefforge.bcrp.structure")
        self.assertEqual(module.STRUCTURE_AUTHORITY_ID, "bcrp-native-structure-authority:1.0.0")
        bundle = load_case(CASE_IDS[0])
        self.assertEqual(module.validate_structure(bundle), ())

    def test_unknown_optional_semantic_extension_is_preserved_but_unknown_required_rejects(self):
        original = load_case(CASE_IDS[1])
        optional = deepcopy(original)
        candidate = next(record for record in optional.records if record.kind == "CandidatePresentationPackageRecord")
        extension = {
            "owner_namespace": "example:optional",
            "name": "opaque-semantic-note",
            "version": "1.0.0",
            "authority_ref": "authority:presentation",
            "scope": "record",
            "target_refs": [candidate.identity],
            "criticality": "optional",
            "character": "semantic",
            "validation_contract": "example:unknown:v1",
            "preservation": "must-preserve",
            "payload": {"opaque": ["kept", {"exact": 7}]},
        }
        candidate.extensions.append(extension)
        round_tripped = bundle_from_canonical_json(canonical_json_bytes(optional, domain="profile-instance"))
        candidate_after = next(record for record in round_tripped.records if record.identity == candidate.identity)
        self.assertIn(extension, candidate_after.extensions)
        self.assertFalse(validate_bundle(optional, through_layer="L2").blocking)

        required = deepcopy(original)
        candidate = next(record for record in required.records if record.kind == "CandidatePresentationPackageRecord")
        extension["criticality"] = "required"
        candidate.extensions.append(deepcopy(extension))
        findings = validate_bundle(required).findings
        self.assertTrue(any(f.family == "extension-boundary" and f.layer == "L1" for f in findings))

    def test_findings_have_complete_fields_and_deterministic_order(self):
        invalid = materialize_invalid_variant(CASE_IDS[2], "C3-I06")
        result = validate_bundle(invalid)
        self.assertGreaterEqual(len(result.findings), 3)
        self.assertEqual(result.findings, tuple(sorted(result.findings)))
        for finding in result.findings:
            self.assertTrue(finding.family)
            self.assertIn(finding.layer, {f"L{i}" for i in range(7)})
            self.assertIn(finding.severity, {"warning", "blocking"})
            self.assertTrue(finding.blocking_consequence)
            self.assertTrue(finding.location or finding.semantic_identity)
            self.assertTrue(finding.message)
            self.assertIsInstance(finding.referenced_identities, tuple)

    def test_validator_never_auto_repairs_semantic_content(self):
        invalid = materialize_invalid_variant(CASE_IDS[1], "C2-I04")
        before = canonical_json_bytes(invalid, domain="profile-instance", require_valid=False)
        validate_bundle(invalid)
        after = canonical_json_bytes(invalid, domain="profile-instance", require_valid=False)
        self.assertEqual(before, after)

    def test_graph_has_derived_reverse_index_but_serialization_excludes_it(self):
        bundle = load_case(CASE_IDS[0])
        graph = reconstruct_graph(bundle)
        self.assertTrue(graph.reverse_index)
        bundle.derived_reverse_index = deepcopy(graph.reverse_index)
        serialized = canonical_json_bytes(bundle, domain="profile-instance")
        self.assertNotIn(b"derived_reverse_index", serialized)


if __name__ == "__main__":
    unittest.main()
