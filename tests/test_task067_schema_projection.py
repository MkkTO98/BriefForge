"""TASK-067 RED contract: strict schema, admission, and lossless projection."""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import inspect
import json
from pathlib import Path
import unittest

from briefforge_paired_terminal_profile.schema import (
    Obligation, PairedAdmissionEnvelope, PairedRow, PairedSchemaRejected,
    PairedSemanticInput, PairedTable, PairedValue, Provenance,
    QualificationEdge, RENDERER_REQUIREMENTS, Section, SectionChild, Statement,
    validate_paired_projection, validate_paired_semantics,
)
from briefforge_paired_terminal_profile.profile import (
    PairedProfileRejected, admit_paired_terminal_semantics,
    build_paired_semantic_extension,
    verify_full_upstream_paired_terminal_admission,
)
from briefforge_paired_terminal_profile.projection import (
    PairedProjectionRejected, build_paired_editorial_projection,
    verify_paired_editorial_projection,
)
from tests import paired_terminal_fixture as fixture


class Task067SchemaProjectionTests(unittest.TestCase):
    def setUp(self):
        self.semantic = fixture.complete_semantics()
        self.admitted = fixture.admitted_semantics(self.semantic)
        self.admission = self.admitted._admission
        self.projection = fixture.projection()

    def assertSemanticRejected(self, **changes):
        with self.assertRaises(PairedSchemaRejected):
            validate_paired_semantics(replace(self.semantic, **changes))

    def test_exact_frozen_identity_literals_and_complete_core_shape(self):
        p = self.projection
        self.assertEqual((p.schema_identity, p.schema_version),
                         (fixture.SCHEMA_ID, fixture.SCHEMA_VERSION))
        self.assertEqual((p.profile_identity, p.profile_version),
                         (fixture.PROFILE_ID, fixture.PROFILE_VERSION))
        self.assertEqual(p.projection_implementation, fixture.PROJECTION_IMPLEMENTATION)
        self.assertEqual((p.table.column_identities, p.table.column_headings),
                         (fixture.COLUMN_IDS, fixture.COLUMN_HEADINGS))
        self.assertEqual(len(p.table.rows), 7)
        self.assertEqual(len(p.values), 14)
        validate_paired_projection(p)
        verify_paired_editorial_projection(p, admission=self.admission)

    def test_paired_extension_uses_exact_core_envelope_and_candidate_binding(self):
        candidate = "candidate:synthetic-paired"
        extension = build_paired_semantic_extension(
            self.semantic, candidate_identity=candidate)
        self.assertEqual(set(extension), {
            "owner_namespace", "name", "version", "authority_ref", "scope",
            "target_refs", "criticality", "character", "validation_contract",
            "preservation", "payload",
        })
        self.assertEqual(extension["validation_contract"],
                         "bcrp:core-extension-envelope:1.0.0")
        self.assertEqual(extension["target_refs"], [candidate])
        self.assertEqual(extension["character"], "semantic")
        self.assertEqual(extension["authority_ref"], "authority:synthetic-content")
        self.assertEqual(extension["payload"]["contract_identity"],
                         "briefforge:representative-paired-terminal-semantic-input:3.0.0")
        self.assertEqual(extension["payload"]["contract_version"], "3.0.0")
        self.assertIs(type(extension["payload"]["canonical_semantics"]), str)

    def test_dtos_are_exact_field_and_immutable(self):
        with self.assertRaises(TypeError):
            PairedAdmissionEnvelope(**{**self.admission.__dict__, "extension": "forbidden"})
        with self.assertRaises(FrozenInstanceError):
            self.admission.profile_version = "9.0.0"
        with self.assertRaises(TypeError):
            Statement("s", "context", "text", "authority:x", None, "unknown")

    def test_wrong_missing_or_aliased_versions_are_rejected(self):
        attacks = (
            replace(self.admission, profile_version="3"),
            replace(self.admission, profile_version="latest"),
            replace(self.admission, profile_identity=""),
            replace(self.admission, plan_fingerprint=""),
            replace(self.admission, capability_declaration_identity="capability:other"),
        )
        for attack in attacks:
            with self.subTest(attack=attack), self.assertRaises(PairedProfileRejected):
                admit_paired_terminal_semantics(self.semantic, admission=attack)

    def test_profile_delegates_upstream_checks_and_requires_exact_envelope(self):
        source = inspect.getsource(__import__(
            "briefforge_paired_terminal_profile.profile", fromlist=["*"]))
        self.assertIn("verify_publication_release", source)
        self.assertIn("verify_renderer_compatibility_plan", source)
        self.assertNotIn("isinstance(admission, PairedAdmissionEnvelope)", source)
        class EnvelopeSubclass(PairedAdmissionEnvelope):
            pass
        subclassed = EnvelopeSubclass(**self.admission.__dict__)
        for value in (object(), self.admission.__dict__, subclassed):
            with self.subTest(value=type(value)), self.assertRaises(PairedProfileRejected):
                admit_paired_terminal_semantics(self.semantic, admission=value)

    def test_all_values_are_present_exact_decimal_metadata_without_float(self):
        for value in self.semantic.values:
            self.assertEqual(value.value_state, "present")
            self.assertIn(value.transformation_state, ("raw", "first_difference"))
            self.assertIs(type(value.coefficient), int)
            self.assertIs(type(value.scale), int)
        base = self.semantic.values[0]
        attacks = (
            replace(base, value_state="absent"), replace(base, value_state=""),
            replace(base, lexical_representation="NaN"),
            replace(base, lexical_representation="0.1250"),
            replace(base, coefficient=-base.coefficient), replace(base, scale=19),
            replace(base, aligned_period=""), replace(base, aligned_count=0),
            replace(base, method_ref=""), replace(base, package_identity=""),
            replace(base, source_ref=""), replace(base, authority_ref=""),
        )
        for attack in attacks:
            values = (attack,) + self.semantic.values[1:]
            with self.subTest(attack=attack), self.assertRaises(PairedSchemaRejected):
                validate_paired_semantics(replace(self.semantic, values=values))
        scale18 = replace(base, coefficient=123456789012345678,
                          scale=18, lexical_representation="0.123456789012345678")
        validate_paired_semantics(replace(
            self.semantic, values=(scale18,) + self.semantic.values[1:]))

    def test_row_ownership_order_pair_swaps_and_all_value_consumption(self):
        row = self.semantic.table.rows[0]
        other = self.semantic.table.rows[1]
        attacks = (
            replace(row, order=2),
            replace(row, identity=other.identity),
            replace(row, relationship_identity=other.relationship_identity),
            replace(row, raw_value_ref=other.raw_value_ref),
            replace(row, raw_value_ref=row.first_difference_value_ref),
            replace(row, first_difference_value_ref=row.raw_value_ref),
        )
        for attack in attacks:
            rows = (attack,) + self.semantic.table.rows[1:]
            with self.subTest(attack=attack), self.assertRaises(PairedSchemaRejected):
                validate_paired_semantics(replace(
                    self.semantic, table=replace(self.semantic.table, rows=rows)))
        with self.assertRaises(PairedSchemaRejected):
            validate_paired_semantics(replace(self.semantic, values=self.semantic.values[:-1]))
        with self.assertRaises(PairedSchemaRejected):
            validate_paired_semantics(replace(self.semantic, values=self.semantic.values + (self.semantic.values[0],)))

    def test_authored_row_statement_encounter_order_must_equal_table_row_order(self):
        statements = list(self.semantic.statements)
        statements[1], statements[2] = statements[2], statements[1]
        table_section = self.semantic.sections[1]
        children = list(table_section.children)
        children[2], children[3] = children[3], children[2]
        mutated = replace(
            self.semantic, statements=tuple(statements),
            sections=(self.semantic.sections[0], replace(table_section, children=tuple(children)),
                      self.semantic.sections[2]),
        )
        with self.assertRaisesRegex(PairedSchemaRejected, "authored row statement order"):
            validate_paired_semantics(mutated)

    def test_row_qualification_reference_cardinality_is_generic_one_to_three(self):
        row = self.semantic.table.rows[0]
        one = replace(row, qualification_refs=row.qualification_refs[:1])
        validate_paired_semantics(replace(
            self.semantic, table=replace(self.semantic.table,
                                         rows=(one,) + self.semantic.table.rows[1:])))
        too_many = row.qualification_refs + (
            self.semantic.table.rows[1].qualification_refs[0],)
        for refs in ((), too_many):
            with self.subTest(count=len(refs)), self.assertRaises(PairedSchemaRejected):
                changed = replace(row, qualification_refs=refs)
                validate_paired_semantics(replace(
                    self.semantic, table=replace(self.semantic.table,
                                                 rows=(changed,) + self.semantic.table.rows[1:])))

    def test_attachment_topology_reassignment_and_section_target_resolution(self):
        edge = self.semantic.qualifications[0]
        provenance = self.semantic.provenance[1]
        obligation = self.semantic.obligations[0]
        attacks = (
            dict(qualifications=(replace(edge, target_ref="section:root"),) + self.semantic.qualifications[1:]),
            dict(qualifications=(replace(edge, target_order=4),) + self.semantic.qualifications[1:]),
            dict(provenance=(self.semantic.provenance[0], replace(
                provenance, target_refs=("statement:row-2",))) + self.semantic.provenance[2:]),
            dict(obligations=(replace(obligation, target_refs=("missing:target",)),) + self.semantic.obligations[1:]),
        )
        for attack in attacks:
            with self.subTest(attack=attack), self.assertRaises(PairedSchemaRejected):
                validate_paired_semantics(replace(self.semantic, **attack))
        # Sections, including the root, are exact semantic destinations.
        validate_paired_semantics(replace(
            self.semantic,
            obligations=(replace(obligation, target_refs=("section:root",)),)
            + self.semantic.obligations[1:],
        ))

    def test_exact_frontier_cardinalities_accept_and_n_plus_one_reject(self):
        # Hand-authored numeric frontiers from the frozen specification.
        base = self.semantic
        extra = tuple(Statement(f"statement:extra-{i}", "context", f"Text {i}",
                                "authority:synthetic-content", None)
                      for i in range(76 - len(base.statements)))
        leaves = tuple(
            replace(
                base.sections[1], identity=f"section:extra-{index}",
                title=f"Extra {index}", order=index + 4,
                children=tuple(SectionChild("statement", item.identity)
                               for item in extra[index::5]),
            )
            for index in range(5)
        )
        root = replace(
            base.sections[0],
            children=base.sections[0].children
            + tuple(SectionChild("section", leaf.identity) for leaf in leaves),
        )
        frontier_statements = base.statements + tuple(
            item for leaf in leaves for child in leaf.children
            for item in extra if item.identity == child.target_ref
        )
        frontier = replace(base, statements=frontier_statements,
                           sections=(root,) + base.sections[1:] + leaves)
        validate_paired_semantics(frontier)  # sections=8, statements=76
        statement77 = Statement("statement:77", "context", "x",
                                "authority:synthetic-content", None)
        leaf77 = replace(frontier.sections[-1],
                         children=frontier.sections[-1].children
                         + (SectionChild("statement", statement77.identity),))
        with self.assertRaisesRegex(PairedSchemaRejected, "section or statement cardinality"):
            validate_paired_semantics(replace(
                frontier, statements=frontier.statements + (statement77,),
                sections=frontier.sections[:-1] + (leaf77,)))
        oversized = replace(frontier.sections[-1], children=frontier.sections[-1].children
                            + (frontier.sections[-1].children[0],) * 32)
        with self.assertRaises(PairedSchemaRejected):
            validate_paired_semantics(replace(
                frontier, sections=frontier.sections[:-1] + (oversized,)))
        validate_paired_semantics(fixture.complete_semantics(row_count=9))

    def test_row_frontier_accepts_16_and_rejects_17(self):
        frontier = fixture.complete_semantics(row_count=16)
        validate_paired_semantics(frontier)
        self.assertEqual(len(frontier.table.rows), 16)
        row17 = replace(frontier.table.rows[-1], identity="row:synthetic-17", order=17)
        with self.assertRaisesRegex(PairedSchemaRejected, "paired row/value cardinality"):
            validate_paired_semantics(replace(
                frontier, table=replace(frontier.table,
                                        rows=frontier.table.rows + (row17,))))

    def test_value_frontier_accepts_32_and_rejects_33(self):
        frontier = fixture.complete_semantics(row_count=16)
        validate_paired_semantics(frontier)
        self.assertEqual(len(frontier.values), 32)
        value33 = replace(frontier.values[-1], identity="value:synthetic-17:raw")
        with self.assertRaisesRegex(PairedSchemaRejected, "paired row/value cardinality"):
            validate_paired_semantics(replace(frontier, values=frontier.values + (value33,)))

    def test_relation_obligation_and_provenance_exact_frontiers(self):
        # N+1 boundaries are independent of the seven-row fixture's business topology.
        edge = self.semantic.qualifications[0]
        with self.assertRaises(PairedSchemaRejected):
            validate_paired_semantics(replace(self.semantic, qualifications=tuple(
                replace(edge, identity=f"qualification:n-{i}", target_ref=self.semantic.values[i % 14].identity,
                        source_ref=f"statement:source-{i // 3}", target_order=i % 3)
                for i in range(28))))
        obligation = self.semantic.obligations[0]
        with self.assertRaises(PairedSchemaRejected):
            validate_paired_semantics(replace(self.semantic, obligations=(replace(
                obligation, target_refs=tuple(f"unresolved:target-{i}" for i in range(83))),)))
        provenance = self.semantic.provenance[0]
        for changed in (
            replace(provenance, target_refs=tuple(f"unresolved:target-{i}" for i in range(93))),
            replace(provenance, package_identities=("package:a", "package:b", "package:c")),
        ):
            with self.subTest(changed=changed), self.assertRaises(PairedSchemaRejected):
                validate_paired_semantics(replace(self.semantic, provenance=(changed,) + self.semantic.provenance[1:]))
        four = tuple(replace(edge, identity=f"qualification:fan-{i}", target_order=i,
                             target_ref=self.semantic.values[i].identity) for i in range(4))
        with self.assertRaises(PairedSchemaRejected):
            validate_paired_semantics(replace(self.semantic, qualifications=four))

        edges27 = self.semantic.qualifications + tuple(
            replace(
                edge,
                identity=f"qualification:frontier-{source}-{order}",
                source_ref=f"statement:row-{source}",
                target_ref=self.semantic.values[(source * 3 + order) % len(self.semantic.values)].identity,
                target_order=order,
            )
            for source in (1, 2) for order in range(3)
        )
        self.assertEqual(len(edges27), 27)
        validate_paired_semantics(replace(self.semantic, qualifications=edges27))

    def test_closed_five_kind_obligation_vocabulary_and_unknown_rejection(self):
        kinds = ("preserve-source-meaning", "source-display",
                 "qualification-display", "exclusion-display",
                 "future-work-language")
        obligations = tuple(Obligation(
            f"obligation:kind-{index}", kind,
            (self.semantic.statements[index].identity,),
            "authority:synthetic-content", "section:support")
            for index, kind in enumerate(kinds))
        support = replace(
            self.semantic.sections[2],
            children=tuple(child for child in self.semantic.sections[2].children
                           if child.kind != "obligation")
            + tuple(SectionChild("obligation", item.identity) for item in obligations),
        )
        changed = replace(self.semantic, obligations=obligations,
                          sections=self.semantic.sections[:2] + (support,))
        validate_paired_semantics(changed)
        with self.assertRaises(PairedSchemaRejected):
            validate_paired_semantics(replace(
                changed, obligations=(replace(obligations[0], kind="other"),)
                + obligations[1:]))

    def test_task064_authoritative_topology_is_representable_without_source_specific_production_logic(self):
        semantic = fixture.task064_topology_semantics()
        validate_paired_semantics(semantic)
        projected = fixture.projection(semantics=semantic)
        self.assertEqual(
            (len(projected.sections), len(projected.statements),
             len(projected.qualifications), len(projected.obligations),
             len(projected.provenance), len(projected.table.rows), len(projected.values)),
            (6, 76, 27, 5, 8, 7, 14),
        )
        self.assertEqual(tuple(section.order for section in projected.sections),
                         (1, 2, 3, 4, 5, 6))
        self.assertEqual(tuple(row.order for row in projected.table.rows),
                         (1, 2, 3, 4, 5, 6, 7))
        self.assertTrue(all(len(row.qualification_refs) == 3
                            for row in projected.table.rows))
        self.assertEqual(len(projected.provenance[0].target_refs), 92)
        self.assertEqual(len(projected.obligations[0].target_refs), 82)
        self.assertIn("section:task065-root", projected.obligations[0].target_refs)
        self.assertTrue(all(len(item.package_identities) == 2
                            for item in projected.provenance[1:]))
        verify_paired_editorial_projection(projected, admission=self.admission)

    def test_attachment_row_ownership_relationship_and_reference_attacks_fail(self):
        unresolved = replace(
            self.semantic.obligations[0], target_refs=("statement:does-not-exist",))
        with self.assertRaises(PairedSchemaRejected):
            validate_paired_semantics(replace(
                self.semantic, obligations=(unresolved,) + self.semantic.obligations[1:]))

        rows = self.semantic.table.rows
        borrowed = replace(rows[0], qualification_refs=rows[1].qualification_refs)
        with self.assertRaises(PairedSchemaRejected):
            validate_paired_semantics(replace(
                self.semantic, table=replace(self.semantic.table,
                                             rows=(borrowed,) + rows[1:])))

        wrong_value = replace(
            self.semantic.values[0], relationship_identity="another-relationship")
        with self.assertRaises(PairedSchemaRejected):
            validate_paired_semantics(replace(
                self.semantic, values=(wrong_value,) + self.semantic.values[1:]))

        misplaced = replace(self.semantic.provenance[0], placement_ref="section:table")
        with self.assertRaises(PairedSchemaRejected):
            validate_paired_semantics(replace(
                self.semantic, provenance=(misplaced,) + self.semantic.provenance[1:]))

    def test_projection_is_lossless_ordered_and_detects_tampering(self):
        projected = build_paired_editorial_projection(admitted=self.admitted)
        self.assertEqual(projected.statements, self.semantic.statements)
        self.assertEqual(projected.sections, self.semantic.sections)
        self.assertEqual(projected.table, self.semantic.table)
        self.assertEqual(projected.values, self.semantic.values)
        self.assertEqual(projected.qualifications, self.semantic.qualifications)
        self.assertEqual(projected.provenance, self.semantic.provenance)
        self.assertEqual(projected.obligations, self.semantic.obligations)
        for attack in (
            replace(projected, projection_fingerprint="0" * 64),
            replace(projected, content_closure_fingerprint="0" * 64),
            replace(projected, statements=tuple(reversed(projected.statements))),
            replace(projected, renderer_mappings=projected.renderer_mappings[:-1]),
        ):
            with self.subTest(), self.assertRaises(PairedProjectionRejected):
                verify_paired_editorial_projection(attack, admission=self.admission)

    def test_public_projection_requires_verified_release_admission_not_digest_strings(self):
        parameters = set(inspect.signature(build_paired_editorial_projection).parameters)
        self.assertEqual(parameters, {"admitted"})
        upstream_parameters = set(inspect.signature(
            verify_full_upstream_paired_terminal_admission).parameters)
        self.assertNotIn("semantics", upstream_parameters)
        self.assertNotIn("admission", upstream_parameters)
        for forged in (None, object(), self.admission, self.semantic):
            with self.subTest(forged=type(forged)), self.assertRaises(PairedProjectionRejected):
                build_paired_editorial_projection(admitted=forged)


if __name__ == "__main__":
    unittest.main()
