"""TASK-060 semantic-completeness/admission adversarial RED contract.

These tests intentionally measure the rendered artifact independently.  Projection
objects and conformance evidence are expectations to verify, never realization
count oracles.
"""
from __future__ import annotations

from copy import deepcopy
from html.parser import HTMLParser
import unittest

from briefforge.representative_projection import (
    RepresentativeProjectionRejected,
    admit_representative_release_content,
    build_representative_projection,
)
from briefforge.representative_renderer import render_representative_html
from briefforge.representative_semantic_conformance import verify_exact_representative_html
from tests.representative_fixture import representative_chain


class _ArtifactMeasurement(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.semantic_keys: dict[str, int] = {}
        self.tables: list[dict] = []
        self._table = None
        self._capture = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        key = attributes.get("data-semantic-key")
        if key:
            self.semantic_keys[key] = self.semantic_keys.get(key, 0) + 1
        if tag == "table":
            self._table = {"headers": [], "rows": []}
            self.tables.append(self._table)
        # The thead tr is a header container, not a measured body row. Start a
        # data row when its first td is encountered so row shape is measured
        # independently and faithfully against the five-column contract.
        elif tag == "th" and self._table is not None:
            self._capture = self._table["headers"], ""
        elif tag == "td" and self._table is not None:
            if not self._table["rows"] or len(self._table["rows"][-1]) == 5:
                self._table["rows"].append([])
            self._capture = self._table["rows"][-1], ""

    def handle_data(self, data):
        if self._capture is not None:
            target, text = self._capture
            self._capture = target, text + data

    def handle_endtag(self, tag):
        if tag in {"th", "td"} and self._capture is not None:
            target, text = self._capture
            target.append(text.strip())
            self._capture = None
        elif tag == "table":
            self._table = None


def _measure(html: bytes) -> _ArtifactMeasurement:
    measured = _ArtifactMeasurement()
    measured.feed(html.decode("utf-8"))
    measured.close()
    return measured


class RepresentativeSemanticCompletenessRedTests(unittest.TestCase):
    def setUp(self):
        self.inputs = representative_chain(self, "task060-semantic-red")

    def _bundle(self):
        return self.inputs[1].bundle

    @staticmethod
    def _candidate(bundle):
        return bundle.one("CandidatePresentationPackageRecord").semantic

    @staticmethod
    def _material(bundle):
        return bundle.one("PortablePresentationMaterialRecord").semantic

    def _projection(self, inputs=None):
        values = inputs or self.inputs
        return build_representative_projection(
            verified_release=values[1], evidence_snapshot=values[0], lifecycle_scope=values[2],
            declaration=values[3], planning_authorization=values[4], verified_plan=values[5],
        )

    def assert_rejected(self, mutation):
        bundle = self._bundle()
        mutation(bundle)
        with self.assertRaises(RepresentativeProjectionRejected):
            admit_representative_release_content(bundle)

    def _refresh_cardinality_targets(self, bundle):
        candidate = self._candidate(bundle)
        brief = bundle.one("PresentationBriefRecord").semantic
        requirements = {item["id"]: item for item in candidate["renderer_requirements"]}
        requirements["requirement:representative-section-hierarchy"]["target_refs"] = sorted({
            "brief:representative", "candidate:representative",
            brief["organizing_purpose"]["id"], candidate["organizing_purpose"]["id"],
            candidate["distribution"]["id"],
            *(item["id"] for item in brief["audiences"]),
            *(item["id"] for item in candidate["audiences"]),
            *(item["id"] for item in candidate["sections"]),
        })
        requirements["requirement:representative-ordered-statements"]["target_refs"] = sorted(
            item["id"] for item in candidate["statements"]
        )

    def test_nonempty_consistency_and_state_lists_reject(self):
        for field in ("consistency_assertions", "state_validations"):
            with self.subTest(field=field):
                self.assert_rejected(lambda b, name=field: self._material(b)[name].append(
                    {"id": f"{name}:not-admitted"}))

    def test_independent_parse_requires_one_measured_realization_per_field_and_edge(self):
        projection = self._projection()
        html = render_representative_html(projection)
        measured = _measure(html)
        required = {
            "field:material:representative:identity",
            "edge:candidate:representative:brief_ref:0000",
            "field:statement:representative-alpha:requires_comparison_universe",
            "field:relation:representative-alpha-limit:kind",
            "edge:relation:representative-alpha-limit:target_ref:0000",
            *(f"edge:material:representative:required_value_ids:{index:04d}"
              for index in range(14)),
        }
        self.assertEqual({key: measured.semantic_keys.get(key, 0) for key in required},
                         {key: 1 for key in required})
        accounting = verify_exact_representative_html(html, projection)["requirement_accounting"]
        expected_keys = {
            *(f"field:{item['identity']}:{item['field_role']}"
              for item in accounting["field_entries"]),
            *(f"edge:{item['source_identity']}:{item['edge_role']}:{item['ordinal']:04d}"
              for item in accounting["edge_entries"]),
        }
        self.assertEqual(measured.semantic_keys, {key: 1 for key in expected_keys})
        reported = sum(item["realized_count"] for item in accounting["element_entries"])
        self.assertEqual(reported, sum(measured.semantic_keys.values()),
                         "conformance must not synthesize realized counts from the projection")

    def test_table_is_exactly_five_atomic_columns(self):
        table = _measure(render_representative_html(self._projection())).tables
        self.assertEqual(len(table), 1)
        self.assertEqual(table[0]["headers"],
                         ["case + slot", "value/state", "unit", "type", "source"])
        self.assertTrue(table[0]["rows"])
        self.assertTrue(all(len(row) == 5 for row in table[0]["rows"]))

    def test_optional_absence_is_omitted_not_invented_as_none(self):
        html = render_representative_html(self._projection()).decode("utf-8").lower()
        self.assertNotIn(">none<", html)
        self.assertNotIn("=none<", html)

    def test_brief_candidate_purpose_audience_scope_and_non_scope_equality(self):
        attacks = (
            lambda b: self._candidate(b)["organizing_purpose"].update(statement="Different purpose."),
            lambda b: self._candidate(b)["audiences"][0].update(description="Different audience."),
            lambda b: self._candidate(b).update(scope="Different scope."),
            lambda b: self._candidate(b).update(non_scope="Different non-scope."),
        )
        for attack in attacks:
            with self.subTest(attack=attack):
                self.assert_rejected(attack)

    def test_qualification_target_is_an_observation(self):
        self.assert_rejected(lambda b: self._candidate(b)["relations"][0].update(
            target_ref="statement:representative-beta-limit"))

    def test_exact_audience_and_communication_function_upper_bounds(self):
        bundle = self._bundle()
        brief = bundle.one("PresentationBriefRecord").semantic
        candidate = self._candidate(bundle)
        for index in range(2, 9):
            description = f"Bounded reader {index}."
            brief["audiences"].append({"id": f"audience:brief-{index:02d}", "description": description})
            candidate["audiences"].append(
                {"id": f"audience:candidate-{index:02d}", "description": description})
        self._refresh_cardinality_targets(bundle)
        admit_representative_release_content(bundle)
        brief["audiences"].append({"id": "audience:brief-09", "description": "Bounded reader 9."})
        candidate["audiences"].append(
            {"id": "audience:candidate-09", "description": "Bounded reader 9."})
        self._refresh_cardinality_targets(bundle)
        with self.assertRaises(RepresentativeProjectionRejected):
            admit_representative_release_content(bundle)

        bundle = self._bundle()
        self._candidate(bundle)["statements"][0]["communication_functions"] = [
            "orient", "summarize", "compare", "trace"
        ]
        admit_representative_release_content(bundle)
        self.assert_rejected(lambda b: self._candidate(b)["statements"][0].update(
            communication_functions=["orient", "summarize", "compare", "qualify", "trace"]))

    def test_leaf_may_have_sixteen_statements_plus_exhibit_seventeen_children(self):
        bundle = self._bundle()
        candidate = self._candidate(bundle)
        alpha = next(item for item in candidate["sections"]
                     if item["id"] == "section:representative-alpha")
        prototype = deepcopy(candidate["statements"][0])
        for index in range(1, 15):
            statement = deepcopy(prototype)
            statement["id"] = f"statement:boundary-{index:02d}"
            statement.pop("value_ref", None)
            candidate["statements"].append(statement)
            alpha["children"].insert(-1, statement["id"])
        self._refresh_cardinality_targets(bundle)
        self.assertEqual(len(alpha["children"]), 17)
        admit_representative_release_content(bundle)

    def test_short_text_limit_is_200_utf8_bytes(self):
        attacks = (
            lambda b: (self._candidate(b).update(scope="é" * 101),
                       b.one("PresentationBriefRecord").semantic.update(scope="é" * 101)),
            lambda b: next(item for item in self._candidate(b)["sections"]
                           if item["id"] == "section:representative-alpha").update(title="x" * 201),
            lambda b: self._candidate(b)["distribution"].update(designation="x" * 201),
            lambda b: self._material(b)["authorities"][-1].update(role="x" * 201),
        )
        for attack in attacks:
            with self.subTest(attack=attack):
                self.assert_rejected(attack)

    def test_all_admitted_value_states_and_obligation_kinds(self):
        for state in ("present", "explicit-zero", "missing-not-provided", "unavailable", "not-applicable"):
            bundle = self._bundle()
            value = self._material(bundle)["values"][0]
            for key in ("payload", "reason", "approximate", "approximation"):
                value.pop(key, None)
            value["value_state"] = state
            if state == "present":
                value["payload"] = {"coefficient": "7", "scale": 2}
            elif state == "explicit-zero":
                value["payload"] = {"coefficient": "0", "scale": 0}
            else:
                value["reason"] = f"Authored {state} reason."
            with self.subTest(state=state):
                admit_representative_release_content(bundle)
        bundle = self._bundle()
        value = self._material(bundle)["values"][0]
        value.update(value_state="explicit-zero", payload={"coefficient": "0", "scale": 0},
                     approximate=True, approximation={"method": "bounded", "bound": "exactly zero"})
        value.pop("reason", None)
        admit_representative_release_content(bundle)
        for kind in ("label", "qualification-required", "source-display"):
            bundle = self._bundle()
            self._candidate(bundle)["obligations"][0]["kind"] = kind
            with self.subTest(kind=kind):
                admit_representative_release_content(bundle)

    def test_present_negative_zero_and_operational_obligation_target_reject(self):
        self.assert_rejected(lambda b: self._material(b)["values"][0].update(
            value_state="present", payload={"coefficient": "-0", "scale": 0}))
        self.assert_rejected(lambda b: self._candidate(b)["obligations"][0].update(
            target_refs=["authority:briefforge-publication-release"]))

    def test_detached_provenance_snapshot_and_source_island_rejects(self):
        def attack(bundle):
            material = self._material(bundle)
            authority = material["authorities"][-1]["id"]
            material["provenance"].append({"id": "provenance:detached", "citation": "Detached.",
                                           "authority_ref": authority})
            material["evidence_snapshots"].append({"id": "snapshot:detached", "version": "1",
                "content_fingerprint": "detached", "provenance_ref": "provenance:detached"})
            material["external_references"].append({"id": "external-reference:detached",
                "reference_kind": "offline", "upstream_object_identity": "object:detached",
                "snapshot_ref": "snapshot:detached", "provenance_ref": "provenance:detached",
                "authority_ref": authority})
        self.assert_rejected(attack)

    def test_profile_has_no_fixture_domain_text_constants(self):
        bundle = self._bundle()
        self._material(bundle)["external_references"][0]["reference_kind"] = "offline-authored-reference"
        self._candidate(bundle)["distribution"]["designation"] = "internal-review"
        admit_representative_release_content(bundle)

    def test_obligation_targets_unique_and_canonical(self):
        self.assert_rejected(lambda b: self._candidate(b)["obligations"][0]["target_refs"].append(
            self._candidate(b)["obligations"][0]["target_refs"][0]))
        projection = self._projection()
        self.assertEqual(projection.obligations[0].target_refs,
                         tuple(sorted(projection.obligations[0].target_refs)))

    def test_audience_exact_schema_prohibits_synthesized_edge(self):
        self.assert_rejected(lambda b: self._candidate(b)["audiences"][0].update(
            brief_audience_ref="audience:brief-representative"))
        self.assertTrue(all(item.brief_audience_ref is None for item in self._projection().audiences))

    def test_set_inventories_are_canonicalized_not_transport_ordered(self):
        bundle = self._bundle()
        self._material(bundle)["required_value_ids"].reverse()
        admitted = admit_representative_release_content(bundle)
        self.assertEqual(admitted.case_order,
                         tuple(f"case:representative-{index:02d}" for index in range(1, 8)))

    def test_separate_content_closure_fingerprint_stable_across_plan_changes(self):
        first = self._projection()
        second = self._projection(representative_chain(self, "task060-plan-variant"))
        self.assertNotEqual(first.plan_fingerprint, second.plan_fingerprint)
        self.assertEqual(first.content_closure_fingerprint, second.content_closure_fingerprint)


if __name__ == "__main__":
    unittest.main()
