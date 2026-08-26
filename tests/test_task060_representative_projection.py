"""TASK-060 RED contract for the versioned representative HTML capability.

Production modules imported here deliberately do not exist at the RED gate.
The corpus is BriefForge-owned, synthetic, deterministic, and stdlib-only.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import hashlib
import inspect
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from briefforge.bcrp.model import RECORD_KINDS
from briefforge.controlled_renderer_invocation import build_minimal_html_projection
from briefforge.renderer_adapter import render_minimal_html_projection
from briefforge.representative_projection import (
    PROJECTION_PROFILE_ID,
    PROJECTION_PROFILE_VERSION,
    RepresentativeProjectionRejected,
    admit_representative_release_content,
    build_representative_projection,
)
from briefforge.representative_renderer import (
    RENDERER_ADAPTER_ID,
    RENDERER_IDENTITY,
    RENDERER_VERSION,
    render_representative_html,
)
from briefforge.representative_controlled_invocation import (
    INVOCATION_EVIDENCE_CONTRACT,
    RepresentativeInvocationRejected,
    RepresentativeRendererInvocationAuthorization,
    compute_representative_invocation_authorization_fingerprint,
    invoke_controlled_representative_renderer,
    representative_renderer_implementation_digest,
    render_representative_in_isolation,
    verify_persisted_representative_renderer_invocation,
)
from briefforge.representative_semantic_conformance import (
    ASSESSOR_IMPLEMENTATION,
    ASSESSOR_VERSION,
    CONFORMANCE_EVIDENCE_CONTRACT,
    SEMANTIC_PROFILE_ID,
    SEMANTIC_PROFILE_VERSION,
    RepresentativeConformanceRejected,
    RepresentativeSemanticArtifactConformanceAuthorization,
    assess_exact_representative_html,
    assess_representative_semantic_artifact_conformance,
    compute_representative_conformance_authorization_fingerprint,
    verify_exact_representative_html,
    verify_persisted_representative_semantic_artifact_conformance,
)
from tests.representative_fixture import (
    OPERATIONAL_AUTHORITIES,
    PROJECTION_PROFILE_ID as FIXTURE_PROFILE,
    REQUIREMENTS,
    RENDERER_ADAPTER_ID as FIXTURE_ADAPTER,
    RENDERER_IDENTITY as FIXTURE_RENDERER,
    RENDERER_VERSION as FIXTURE_RENDERER_VERSION,
    SEMANTIC_PROFILE_ID as FIXTURE_SEMANTIC_PROFILE,
    representative_chain,
)
from tests import test_controlled_renderer_invocation as legacy_controlled_tests

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RepresentativeProjectionTests(unittest.TestCase):
    def setUp(self):
        self.inputs = representative_chain(self)

    def _projection(self):
        snapshot, release, scope, declaration, planning_authorization, plan = self.inputs
        return build_representative_projection(
            verified_release=release, evidence_snapshot=snapshot, lifecycle_scope=scope,
            declaration=declaration, planning_authorization=planning_authorization,
            verified_plan=plan,
        )

    def _acceptance_projection(self):
        inputs = representative_chain(self, "task060-complete", complete_audience_edge=True)
        snapshot, release, scope, declaration, planning_authorization, plan = inputs
        return build_representative_projection(
            verified_release=release, evidence_snapshot=snapshot, lifecycle_scope=scope,
            declaration=declaration, planning_authorization=planning_authorization,
            verified_plan=plan,
        )

    def _bundle(self):
        return self.inputs[1].bundle

    def _legacy_projection(self):
        helper = legacy_controlled_tests.ControlledRendererInvocationTests(
            "test_projection_uses_no_legacy_ready_and_consumes_all_plan_mappings_once"
        )
        helper.setUp()
        self.addCleanup(helper.doCleanups)
        inputs = helper._inputs()
        return build_minimal_html_projection(
            verified_release=inputs[1], evidence_snapshot=inputs[0], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
        )

    def _candidate(self, bundle):
        return bundle.one("CandidatePresentationPackageRecord").semantic

    def _material(self, bundle):
        return bundle.one("PortablePresentationMaterialRecord").semantic

    def assertAdmissionRejected(self, mutate):
        bundle = self._bundle()
        mutate(bundle)
        with self.assertRaises(RepresentativeProjectionRejected):
            admit_representative_release_content(bundle)

    def test_fixed_identities_and_positive_inventory_are_exact(self):
        self.assertEqual((PROJECTION_PROFILE_ID, PROJECTION_PROFILE_VERSION), (FIXTURE_PROFILE, "1.0.0"))
        self.assertEqual((RENDERER_IDENTITY, RENDERER_VERSION, RENDERER_ADAPTER_ID),
                         (FIXTURE_RENDERER, FIXTURE_RENDERER_VERSION, FIXTURE_ADAPTER))
        self.assertEqual((SEMANTIC_PROFILE_ID, SEMANTIC_PROFILE_VERSION),
                         (FIXTURE_SEMANTIC_PROFILE, "2.0.0"))
        self.assertEqual((ASSESSOR_IMPLEMENTATION, ASSESSOR_VERSION),
                         ("briefforge.representative_semantic_artifact_conformance", "2.0.0"))
        self.assertEqual(CONFORMANCE_EVIDENCE_CONTRACT,
                         "briefforge:semantic-artifact-conformance-evidence:2.0.0")
        self.assertEqual(INVOCATION_EVIDENCE_CONTRACT,
                         "briefforge:representative-controlled-renderer-invocation-evidence:1.0.0")
        projection = self._projection()
        self.assertEqual(len(projection.sections), 3)
        self.assertEqual(len(projection.statements), 4)
        self.assertEqual(len(projection.qualifications), 2)
        self.assertEqual(len(projection.case_bindings), 7)
        self.assertEqual(len(projection.values), 14)
        self.assertEqual(len(projection.content_authorities), 1)
        self.assertEqual(tuple(item.identity for item in projection.operational_authority_exclusions),
                         tuple(item["id"] for item in OPERATIONAL_AUTHORITIES))
        self.assertEqual(len(projection.requirement_mappings), 7)
        self.assertEqual({item.expression_mode for item in projection.requirement_mappings}, {"native"})
        self.assertEqual(projection.output_filename, "brief.html")
        self.assertEqual(projection.media_type, "text/html")

    def test_projection_freezes_every_admitted_record_field_and_directed_edge(self):
        """The projection is a semantic closure, not a renderer convenience DTO."""
        projection = self._acceptance_projection()
        self.assertEqual(projection.brief_identity, "brief:representative")
        self.assertEqual(projection.material_identities, ("material:representative",))
        self.assertEqual(projection.package_identity, "candidate:representative")
        self.assertEqual(projection.brief_purpose.identity, "purpose:brief-representative")
        self.assertEqual(projection.candidate_purpose.identity, "purpose:candidate-representative")
        self.assertEqual(projection.candidate_purpose.brief_purpose_ref, "purpose:brief-representative")
        self.assertEqual(
            tuple((a.identity, a.brief_audience_ref) for a in projection.audiences),
            (("audience:brief-representative", None),
             ("audience:candidate-representative", None)),
        )
        self.assertEqual(projection.brief_scope, "A fixed offline representative shape.")
        self.assertEqual(projection.candidate_scope, projection.brief_scope)
        self.assertEqual(projection.brief_non_scope, projection.candidate_non_scope)
        self.assertEqual(projection.required_value_ids,
                         tuple(f"value:representative-{i:02d}" for i in range(1, 15)))
        self.assertEqual(projection.exhibit.identity, "exhibit:representative-table")
        self.assertEqual(projection.exhibit.kind, "fixed-static-table")
        self.assertEqual(projection.exhibit.purpose_ref, "purpose:candidate-representative")
        self.assertEqual(projection.exhibit.value_ids, projection.required_value_ids)
        self.assertEqual(projection.distribution.identity, "distribution:representative")
        self.assertEqual(projection.distribution.designation, "fixture-only")
        self.assertEqual(projection.distribution.authority_ref,
                         "authority:synthetic-representative-content")

    def test_projection_freezes_snapshots_units_types_and_their_descriptions(self):
        projection = self._acceptance_projection()
        self.assertEqual(
            tuple((x.identity, x.version, x.provenance_ref) for x in projection.evidence_snapshots),
            (("snapshot:representative", "1", "provenance:representative"),),
        )
        self.assertRegex(projection.evidence_snapshots[0].content_fingerprint,
                         r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(tuple((x.identity, x.description) for x in projection.units), (
            ("unit:count", "exact authored count"), ("unit:ratio", "exact authored ratio"),
        ))
        self.assertEqual(tuple((x.identity, x.description) for x in projection.semantic_types), (
            ("semantic-type:index", "synthetic index"),
            ("semantic-type:quantity", "synthetic quantity"),
        ))

    def test_html_realizes_complete_frozen_semantics_and_exactly_five_columns(self):
        html = render_representative_html(self._acceptance_projection())
        required = (
            b"brief:representative", b"material:representative", b"candidate:representative",
            b"purpose:brief-representative", b"purpose:candidate-representative",
            b"audience:brief-representative", b"audience:candidate-representative",
            b"snapshot:representative", b"exact authored count", b"exact authored ratio",
            b"synthetic quantity", b"synthetic index", b"distribution:representative",
            b"fixture-only", b"fixed-static-table", b"exhibit:representative-table",
        )
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, html)
        self.assertEqual(html.count(b"<table>"), 1)
        head = html[html.index(b"<thead>"):html.index(b"</thead>")]
        self.assertEqual(head.count(b"<th>"), 5)
        self.assertEqual(
            tuple(part.split(b"</th>", 1)[0] for part in head.split(b"<th>")[1:]),
            (b"case + slot", b"value/state", b"unit", b"type", b"source"),
        )

    def test_exhibit_is_referenced_by_exactly_one_section_child_edge(self):
        self.assertAdmissionRejected(lambda b: self._candidate(b)["sections"][2]["children"].remove(
            "exhibit:representative-table"))
        self.assertAdmissionRejected(lambda b: self._candidate(b)["sections"][0]["children"].append(
            "exhibit:representative-table"))

    def test_projection_fingerprint_is_recomputed_at_every_renderer_and_assessor_boundary(self):
        projection = self._projection()
        artifact = render_representative_html(projection)
        forged = replace(projection, fingerprint="0" * 64)
        stale = replace(projection, purpose="stale projection purpose")
        for changed in (forged, stale):
            with self.subTest(changed=changed), self.assertRaises(RepresentativeProjectionRejected):
                render_representative_html(changed)
            with self.subTest(changed=changed), self.assertRaises(RepresentativeConformanceRejected):
                verify_exact_representative_html(artifact, changed)

    def test_field_and_edge_accounting_has_exact_schema_and_per_requirement_digest(self):
        projection = self._acceptance_projection()
        evidence = verify_exact_representative_html(render_representative_html(projection), projection)
        accounting = evidence["requirement_accounting"]
        self.assertEqual(set(accounting), {
            "schema_identity", "requirement_ids", "expected_requirements", "element_entries",
            "field_entries", "edge_entries", "unplanned_realization_count", "accounting_digest",
        })
        self.assertEqual(accounting["schema_identity"],
                         "briefforge:representative-field-edge-accounting:1.0.0")
        requirement_ids = tuple(f"requirement:representative-{stem}" for stem, _ in REQUIREMENTS)
        self.assertEqual(tuple(accounting["requirement_ids"]), requirement_ids)
        by_requirement = {item["requirement_id"]: item for item in accounting["expected_requirements"]}
        self.assertEqual(set(by_requirement), set(requirement_ids))
        for requirement_id in requirement_ids:
            item = by_requirement[requirement_id]
            self.assertEqual(set(item), {
                "requirement_id", "outcome", "planned_field_count", "realized_field_count",
                "planned_edge_count", "realized_edge_count", "accounting_digest",
            })
            digest_input = {key: value for key, value in item.items() if key != "accounting_digest"}
            expected = hashlib.sha256(json.dumps(
                digest_input, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            ).encode("utf-8")).hexdigest()
            self.assertEqual(item["accounting_digest"], expected)
            self.assertEqual(item["planned_field_count"], item["realized_field_count"])
            self.assertEqual(item["planned_edge_count"], item["realized_edge_count"])

    def test_hierarchy_and_authored_case_order_ignore_transport_order(self):
        projection = self._projection()
        self.assertEqual([item.identity for item in projection.sections], [
            "section:representative-root", "section:representative-alpha", "section:representative-beta",
        ])
        self.assertEqual([item.order for item in projection.case_bindings], list(range(1, 8)))
        self.assertEqual(projection.case_bindings[0].primary_ref, "value:representative-01")
        self.assertEqual(projection.case_bindings[0].comparison_ref, "value:representative-02")
        bundle = self._bundle()
        candidate = self._candidate(bundle)
        candidate["sections"].reverse()
        candidate["exhibits"][0]["case_bindings"].reverse()
        admitted = admit_representative_release_content(bundle)
        self.assertEqual(admitted.section_preorder, projection.section_preorder)
        self.assertEqual(admitted.case_order, projection.case_order)

    def test_projection_render_and_independent_conformance_are_deterministic(self):
        projection = self._projection()
        first = render_representative_html(projection)
        second = render_representative_html(projection)
        self.assertIs(type(first), bytes)
        self.assertEqual(first, second)
        self.assertTrue(first.startswith(b"<!doctype html>"))
        evidence = verify_exact_representative_html(first, projection)
        assessed = assess_exact_representative_html(first, projection)
        self.assertEqual(assessed.status, "conforming")
        self.assertEqual(assessed.evidence, evidence)
        self.assertEqual(evidence["assessment_status"], "conforming")
        self.assertEqual(evidence["aggregate_verdict"], "approved")
        accounting = evidence["requirement_accounting"]
        self.assertEqual(len(accounting["requirement_ids"]), 7)
        self.assertEqual(len(accounting["expected_requirements"]), 7)
        self.assertEqual(accounting["unplanned_realization_count"], 0)
        self.assertTrue(all(item["outcome"] == "conformant" for item in accounting["expected_requirements"]))
        self.assertTrue(all(item["planned_field_count"] == item["realized_field_count"] and
                            item["planned_edge_count"] == item["realized_edge_count"] and
                            item["planned_field_count"] + item["planned_edge_count"] > 0
                            for item in accounting["expected_requirements"]))
        operational = [item for item in accounting["element_entries"]
                       if item["projection_rule"] == "operational-authority-exclusion"]
        self.assertEqual(len(operational), 5)
        self.assertTrue(all(item["requirement_ids"] == [] and
                            item["planned_count"] == item["realized_count"] == 0
                            for item in operational))

    def test_full_text_is_escaped_plain_text_and_no_active_or_external_content_exists(self):
        html = render_representative_html(self._projection())
        self.assertIn(b"Alpha &lt;leaf&gt;", html)
        self.assertIn(b"reader &lt;&amp;&gt;", html)
        self.assertIn(b"&lt;script&gt;not markup&lt;/script&gt;", html)
        lowered = html.lower()
        for token in (b"<script", b"javascript:", b"http://", b"https://", b"onload=", b"onclick=", b"srcdoc=", b"@import"):
            self.assertNotIn(token, lowered)

    def test_omission_duplicate_reorder_hierarchy_and_extra_html_are_nonconforming(self):
        projection = self._projection()
        valid = render_representative_html(projection)
        alpha = b"Alpha preserves exact authored values &amp; source identity."
        beta = b"Beta keeps explicit zero and absent states distinct."
        attacks = (
            valid.replace(alpha, b"", 1),
            valid.replace(alpha, alpha + alpha, 1),
            valid.replace(alpha, b"__ALPHA__", 1).replace(beta, alpha, 1).replace(b"__ALPHA__", beta, 1),
            valid.replace(b"Alpha &lt;leaf&gt;", b"Representative root", 1),
            valid.replace(b"</main>", b"<p>unauthorized semantic addition</p></main>", 1),
        )
        for attack in attacks:
            with self.subTest(attack=attack[-100:]):
                result = assess_exact_representative_html(attack, projection)
                self.assertEqual(result.status, "non-conforming")
                self.assertIsNone(result.record)
                self.assertTrue(result.findings)

    def test_value_unit_type_exact_decimal_state_and_no_rounding_are_conformed(self):
        projection = self._projection()
        html = render_representative_html(projection)
        for exact in (b"10000000000000000001", b"10000000000000000011", b"explicit-zero", b"missing-not-provided", b"not-applicable"):
            self.assertIn(exact, html)
        attacks = (
            html.replace(b"10000000000000000001", b"10000000000000000000", 1),
            html.replace(b"10000000000000000011", b"1.0e19", 1),
            html.replace(b"unit:count", b"unit:ratio", 1),
            html.replace(b"semantic-type:index", b"semantic-type:quantity", 1),
            html.replace(b"explicit-zero", b"present", 1),
        )
        for attack in attacks:
            with self.subTest():
                with self.assertRaises(RepresentativeConformanceRejected):
                    verify_exact_representative_html(attack, projection)

    def test_provenance_qualification_obligation_and_authority_tampering_fails(self):
        projection = self._projection()
        valid = render_representative_html(projection)
        replacements = (
            (b"external:representative-source", b"external:omitted"),
            (b"provenance:representative", b"provenance:other"),
            (b"relation:representative-alpha-limit", b"relation:other"),
            (b"statement:representative-alpha-limit", b"statement:representative-beta-limit"),
            (b"obligation:representative-source-display", b"obligation:other"),
            (b"authority:synthetic-representative-content", b"authority:other"),
        )
        for old, new in replacements:
            attack = valid.replace(old, new, 1)
            self.assertNotEqual(valid, attack)
            with self.subTest(old=old), self.assertRaises(RepresentativeConformanceRejected):
                verify_exact_representative_html(attack, projection)

    def test_malformed_unparseable_artifacts_are_indeterminate_and_emit_no_record(self):
        projection = self._projection()
        for artifact in (b"", b"not html", b"\xff\xfe", b"<!doctype html><html><body>"):
            with self.subTest(artifact=artifact):
                result = assess_exact_representative_html(artifact, projection)
                self.assertEqual(result.status, "indeterminate")
                self.assertIsNone(result.record)
                self.assertTrue(result.findings)

    def test_all_profile_enums_and_value_state_invariants_fail_closed(self):
        attacks = (
            lambda b: self._candidate(b)["statements"][0].update(posture="recommendation"),
            lambda b: self._candidate(b)["statements"][0].update(attention="hidden"),
            lambda b: self._candidate(b)["statements"][0].update(communication_functions=["invent"]),
            lambda b: self._candidate(b)["obligations"][0].update(kind="invented"),
            # designation and reference_kind are bounded authored text, not
            # profile enums. Treating fixture strings as enums contradicts the
            # domain-neutral admission contract in semantic-completeness.
            lambda b: self._material(b)["values"][0].update(
                value_state="present", payload={"coefficient": "0", "scale": 0}),
            lambda b: self._material(b)["values"][11]["payload"].update(scale=1),
            lambda b: self._material(b)["values"][10]["approximation"].update(method=""),
            lambda b: self._material(b)["values"][10]["approximation"].update(bound="x" * 4097),
        )
        for attack in attacks:
            with self.subTest(attack=attack):
                self.assertAdmissionRejected(attack)

    def test_every_bounded_collection_rejects_overflow_and_orphan_definitions(self):
        def copies(item, count, stem):
            result = []
            for index in range(count):
                changed = deepcopy(item)
                changed["id"] = f"{stem}:{index:02d}"
                result.append(changed)
            return result

        attacks = (
            lambda b: self._candidate(b).update(sections=[]),
            lambda b: self._candidate(b).update(sections=copies(
                self._candidate(b)["sections"][0], 9, "section:overflow")),
            lambda b: self._candidate(b).update(statements=[]),
            lambda b: self._candidate(b).update(audiences=copies(
                self._candidate(b)["audiences"][0], 17, "audience:overflow")),
            lambda b: self._candidate(b).update(statements=copies(
                self._candidate(b)["statements"][0], 33, "statement:overflow")),
            lambda b: self._candidate(b)["exhibits"][0].update(case_bindings=[]),
            lambda b: self._candidate(b)["exhibits"][0].update(case_bindings=copies(
                self._candidate(b)["exhibits"][0]["case_bindings"][0], 17, "case:overflow")),
            lambda b: self._material(b).update(values=[]),
            lambda b: self._material(b).update(values=copies(
                self._material(b)["values"][0], 33, "value:overflow")),
            lambda b: self._candidate(b).update(relations=[]),
            lambda b: self._candidate(b).update(relations=copies(
                self._candidate(b)["relations"][0], 17, "relation:overflow")),
            lambda b: self._candidate(b).update(obligations=[]),
            lambda b: self._candidate(b)["obligations"].extend(copies(
                self._candidate(b)["obligations"][0], 16, "obligation:overflow")),
            lambda b: self._material(b).update(provenance=[]),
            lambda b: self._material(b)["provenance"].extend(copies(
                self._material(b)["provenance"][0], 16, "provenance:overflow")),
            lambda b: self._material(b).update(evidence_snapshots=[]),
            lambda b: self._material(b)["evidence_snapshots"].extend(copies(
                self._material(b)["evidence_snapshots"][0], 16, "snapshot:overflow")),
            lambda b: self._material(b).update(external_references=[]),
            lambda b: self._material(b)["external_references"].extend(copies(
                self._material(b)["external_references"][0], 16, "external:overflow")),
            lambda b: self._material(b).update(units=copies(
                self._material(b)["units"][0], 17, "unit:overflow")),
            lambda b: self._material(b).update(semantic_types=copies(
                self._material(b)["semantic_types"][0], 17, "semantic-type:overflow")),
            lambda b: self._material(b).update(authorities=copies(
                self._material(b)["authorities"][-1], 14, "authority:overflow")),
            lambda b: self._material(b)["units"].append(
                {"id": "unit:orphan", "description": "not referenced"}),
            lambda b: self._material(b)["semantic_types"].append(
                {"id": "semantic-type:orphan", "description": "not referenced"}),
            lambda b: self._material(b)["authorities"].append(
                {"id": "authority:orphan", "owner_identity": "project:BriefForge",
                 "role": "content", "scope": "not referenced"}),
        )
        for attack in attacks:
            with self.subTest(attack=attack):
                self.assertAdmissionRejected(attack)

    def test_ids_refs_cardinality_unknown_fields_and_malformed_values_fail_admission(self):
        attacks = (
            lambda b: self._candidate(b)["statements"].append(deepcopy(self._candidate(b)["statements"][0])),
            lambda b: self._candidate(b)["sections"][1]["children"].append("statement:representative-beta"),
            lambda b: self._candidate(b)["sections"][0]["children"].append("section:unknown"),
            lambda b: self._candidate(b)["exhibits"][0]["case_bindings"].pop(),
            lambda b: self._candidate(b)["exhibits"][0]["case_bindings"][1].update(order=1),
            lambda b: self._candidate(b)["exhibits"][0]["case_bindings"][0].update(primary_ref="value:unknown"),
            lambda b: self._candidate(b)["renderer_requirements"].pop(),
            lambda b: self._candidate(b).update(unknown_profile_field=True),
            lambda b: self._material(b)["values"][0]["payload"].update(coefficient="1.2"),
            lambda b: self._material(b)["values"][0]["payload"].update(scale=19),
            lambda b: self._material(b)["values"][0].update(value_state="unresolved"),
            lambda b: self._material(b)["values"][0].update(extra="not admitted"),
        )
        for attack in attacks:
            with self.subTest(attack=attack):
                self.assertAdmissionRejected(attack)

    def test_nan_infinity_float_bool_and_malformed_runtime_types_fail_closed(self):
        values = (math.nan, math.inf, -math.inf, 1.25, True, None, [], {})
        for value in values:
            with self.subTest(value=value):
                self.assertAdmissionRejected(
                    lambda b, item=value: self._material(b)["values"][0]["payload"].update(coefficient=item)
                )

    def test_wrong_profile_renderer_plan_and_cross_routing_are_rejected(self):
        projection = self._projection()
        html = render_representative_html(projection)
        for changed in (
            replace(projection, profile_identity="briefforge:representative-static-html-projection-profile:9.0.0"),
            replace(projection, renderer_identity="renderer:minimal-html"),
            replace(projection, renderer_version="0.2.0"),
        ):
            with self.subTest(changed=changed), self.assertRaises((RepresentativeProjectionRejected, RepresentativeConformanceRejected)):
                render_representative_html(changed)
        legacy = self._legacy_projection()
        with self.assertRaises(Exception):
            verify_exact_representative_html(render_minimal_html_projection(legacy).html.encode(), projection)
        with self.assertRaises(Exception):
            render_minimal_html_projection(projection)
        self.assertEqual(assess_exact_representative_html(html, projection).status, "conforming")

    def test_controlled_worker_replays_in_isolation_and_rejects_nondeterminism(self):
        projection = self._projection()
        first = render_representative_in_isolation(projection, timeout_seconds=2)
        second = render_representative_in_isolation(projection, timeout_seconds=2)
        self.assertEqual(first, second)
        self.assertEqual(first, render_representative_html(projection))
        from briefforge import representative_controlled_invocation as module
        real = module._render_in_subprocess
        calls = 0
        def varying(*args, **kwargs):
            nonlocal calls
            calls += 1
            return real(*args, **kwargs) + (b"x" if calls % 2 == 0 else b"")
        with patch.object(module, "_render_in_subprocess", side_effect=varying):
            with self.assertRaises(RepresentativeInvocationRejected):
                render_representative_in_isolation(projection, timeout_seconds=2)

    def test_renderer_digest_is_stable_explicit_and_not_legacy_digest(self):
        first = representative_renderer_implementation_digest()
        second = representative_renderer_implementation_digest()
        self.assertEqual(first, second)
        self.assertRegex(first, r"^[0-9a-f]{64}$")
        from briefforge.controlled_renderer_invocation import renderer_implementation_digest
        self.assertNotEqual(first, renderer_implementation_digest())

    def test_exactly_eleven_bcrp_kinds_and_canonical_import_isolation_remain(self):
        self.assertEqual(len(RECORD_KINDS), 11)
        script = """
import json, sys
import briefforge.bcrp
blocked = ('representative_projection', 'representative_renderer',
           'representative_controlled_invocation', 'representative_semantic_conformance')
print(json.dumps(sorted(name for name in sys.modules if any(name.endswith(x) for x in blocked))))
"""
        result = subprocess.run(
            [sys.executable, "-B", "-c", script], cwd=PROJECT_ROOT,
            env={"PYTHONPATH": str(PROJECT_ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"},
            text=True, capture_output=True, check=True,
        )
        self.assertEqual(result.stdout.strip(), "[]")

    def test_public_boundaries_have_no_caller_schema_pairing_order_or_html_bypass(self):
        projection_parameters = set(inspect.signature(build_representative_projection).parameters)
        render_parameters = set(inspect.signature(render_representative_html).parameters)
        conform_parameters = set(inspect.signature(verify_exact_representative_html).parameters)
        forbidden = {"schema", "columns", "case_bindings", "sort_key", "html", "css", "template", "network", "browser", "database", "fallback"}
        self.assertFalse(projection_parameters & forbidden)
        self.assertEqual(render_parameters, {"projection"})
        self.assertEqual(conform_parameters, {"artifact_bytes", "projection"})
        self.assertTrue(hasattr(RepresentativeRendererInvocationAuthorization, "__dataclass_fields__"))
        self.assertTrue(hasattr(RepresentativeSemanticArtifactConformanceAuthorization, "__dataclass_fields__"))
        self.assertIn("authorization", inspect.signature(invoke_controlled_representative_renderer).parameters)
        self.assertIn("authorization", inspect.signature(assess_representative_semantic_artifact_conformance).parameters)
        self.assertIn("authorization", inspect.signature(verify_persisted_representative_renderer_invocation).parameters)
        self.assertIn("authorization", inspect.signature(verify_persisted_representative_semantic_artifact_conformance).parameters)
        self.assertEqual(len(inspect.signature(compute_representative_invocation_authorization_fingerprint).parameters), 1)
        self.assertEqual(len(inspect.signature(compute_representative_conformance_authorization_fingerprint).parameters), 1)

    def test_v1_sources_and_rendered_bytes_are_unchanged_by_parallel_v2_imports(self):
        controlled_source = (PROJECT_ROOT / "src/briefforge/controlled_renderer_invocation.py").read_bytes()
        conformance_source = (PROJECT_ROOT / "src/briefforge/semantic_artifact_conformance.py").read_bytes()
        projection = self._legacy_projection()
        before = render_minimal_html_projection(projection).html.encode("utf-8")
        _ = self._projection(), render_representative_html(self._projection())
        after = render_minimal_html_projection(projection).html.encode("utf-8")
        self.assertEqual(before, after)
        self.assertEqual(controlled_source, (PROJECT_ROOT / "src/briefforge/controlled_renderer_invocation.py").read_bytes())
        self.assertEqual(conformance_source, (PROJECT_ROOT / "src/briefforge/semantic_artifact_conformance.py").read_bytes())


if __name__ == "__main__":
    unittest.main()
