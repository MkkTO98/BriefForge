"""Adversarial proofs required by the frozen TASK-067 acceptance contract.

These tests deliberately establish a valid exact frontier before applying each
N+1 mutation.  A rejection caused by an unrelated dangling reference is not a
cardinality proof.
"""
from __future__ import annotations

from dataclasses import replace
import itertools
import json
import unittest
from unittest.mock import patch

from briefforge.bcrp.model import BCRPBundle, BCRPRecord
from briefforge.controlled_renderer_invocation import RendererInvocationAuthorization
from briefforge.publication_manifest_admission import PublicationManifestAuthorization
from briefforge.renderer_compatibility_planning import (
    CapabilityClaim,
    RendererCapabilityDeclaration,
    VerifiedRendererCompatibilityPlan,
    compute_capability_declaration_fingerprint,
)
from briefforge.representative_controlled_invocation import (
    RepresentativeRendererInvocationAuthorization,
)
from briefforge.representative_semantic_conformance import (
    RepresentativeSemanticArtifactConformanceAuthorization,
)
from briefforge.semantic_artifact_conformance import SemanticArtifactConformanceAuthorization
from briefforge_terminal_profile.controlled_invocation import (
    TerminalRendererInvocationAuthorization,
)
from briefforge_terminal_profile.semantic_conformance import (
    TerminalSemanticArtifactConformanceAuthorization,
)
from briefforge_paired_terminal_profile.controlled_invocation import (
    PairedTerminalRendererInvocationAuthorization,
)
from briefforge_paired_terminal_profile.renderer import render_paired_html
from briefforge_paired_terminal_profile.profile import (
    PairedProfileRejected,
    consume_paired_upstream_admission,
    _verify_exact_paired_declaration,
    _verify_exact_paired_plan,
)
from briefforge_paired_terminal_profile.schema import (
    Obligation,
    PairedSchemaRejected,
    Provenance,
    QualificationEdge,
    SectionChild,
    Statement,
    validate_paired_semantics,
)
from briefforge_paired_terminal_profile.semantic_conformance import (
    PairedSemanticConformanceRejected,
    PairedTerminalSemanticArtifactConformanceAuthorization,
    verify_exact_paired_html,
)
from tests import paired_terminal_fixture as fixture


class Task067IndependentBoundaryProofs(unittest.TestCase):
    def setUp(self):
        self.semantic = fixture.complete_semantics()

    def assert_frontier_then_n_plus_one(self, frontier, overflow, message):
        validate_paired_semantics(frontier)
        with self.assertRaisesRegex(PairedSchemaRejected, message):
            validate_paired_semantics(overflow)

    def test_children_frontier_32_accepts_and_33_alone_rejects(self):
        base = self.semantic
        support = base.sections[2]
        statement_children = tuple(child for child in support.children
                                   if child.kind == "statement")
        attachment_children = tuple(child for child in support.children
                                    if child.kind != "statement")
        additions = tuple(
            Statement(f"statement:child-frontier-{index}", "context", "Synthetic text.",
                      "authority:synthetic-content", None)
            for index in range(32 - len(support.children))
        )
        support32 = replace(
            support,
            children=statement_children
            + tuple(SectionChild("statement", item.identity) for item in additions)
            + attachment_children,
        )
        frontier = replace(base, statements=base.statements + additions,
                           sections=base.sections[:2] + (support32,))
        extra = Statement("statement:child-overflow", "context", "Synthetic text.",
                          "authority:synthetic-content", None)
        support33 = replace(
            support32,
            children=statement_children
            + tuple(SectionChild("statement", item.identity)
                    for item in additions + (extra,))
            + attachment_children,
        )
        self.assertEqual(len(support32.children), 32)
        self.assertEqual(len(support33.children), 33)
        self.assert_frontier_then_n_plus_one(
            frontier,
            replace(frontier, statements=frontier.statements + (extra,),
                    sections=frontier.sections[:2] + (support33,)),
            "children per section",
        )

    def test_section_frontier_8_accepts_and_9_alone_rejects(self):
        base = self.semantic
        additions = tuple(
            Statement(f"statement:section-frontier-{index}", "context", "Synthetic text.",
                      "authority:synthetic-content", None)
            for index in range(5)
        )
        leaves = tuple(
            replace(base.sections[1], identity=f"section:frontier-{index}",
                    title="Synthetic section", order=index + 4,
                    children=(SectionChild("statement", additions[index].identity),))
            for index in range(5)
        )
        root8 = replace(
            base.sections[0], children=base.sections[0].children
            + tuple(SectionChild("section", leaf.identity) for leaf in leaves))
        frontier = replace(base, statements=base.statements + additions,
                           sections=(root8,) + base.sections[1:] + leaves)
        extra_statement = Statement("statement:section-overflow", "context", "Synthetic text.",
                                    "authority:synthetic-content", None)
        extra_leaf = replace(base.sections[1], identity="section:overflow-9",
                             title="Synthetic section", order=9,
                             children=(SectionChild("statement", extra_statement.identity),))
        root9 = replace(root8, children=root8.children
                        + (SectionChild("section", extra_leaf.identity),))
        self.assertEqual(len(frontier.sections), 8)
        self.assert_frontier_then_n_plus_one(
            frontier,
            replace(frontier, statements=frontier.statements + (extra_statement,),
                    sections=(root9,) + frontier.sections[1:] + (extra_leaf,)),
            "section or statement cardinality",
        )

    def test_qualification_frontier_27_accepts_and_28_alone_rejects(self):
        base = self.semantic
        prototype = base.qualifications[0]
        additions = tuple(
            replace(
                prototype,
                identity=f"qualification:frontier-{source}-{order}",
                source_ref=f"statement:row-{source}",
                target_ref=base.values[(source * 3 + order) % len(base.values)].identity,
                target_order=order,
            )
            for source in (1, 2) for order in range(3)
        )
        qualifications27 = base.qualifications + additions
        frontier = replace(base, qualifications=qualifications27)
        edge28 = QualificationEdge(
            "qualification:overflow-28", "limits-target", "statement:introduction",
            base.table.identity, 0, "authority:synthetic-content",
        )
        self.assertEqual(len(qualifications27), 27)
        self.assert_frontier_then_n_plus_one(
            frontier, replace(frontier, qualifications=qualifications27 + (edge28,)),
            "relation, provenance, or obligation cardinality",
        )

    def test_qualification_fanout_3_accepts_and_4_alone_rejects(self):
        base = self.semantic
        targets = (base.statements[0].identity, base.values[0].identity,
                   base.table.identity, base.values[1].identity)
        edges = tuple(QualificationEdge(
            f"qualification:fanout-{order}", "limits-target", "statement:introduction",
            target, order, "authority:synthetic-content",
        ) for order, target in enumerate(targets))
        frontier = replace(base, qualifications=base.qualifications + edges[:3])
        validate_paired_semantics(frontier)
        with self.assertRaisesRegex(
                PairedSchemaRejected,
                "qualification targets must be bounded and contiguously ordered per source"):
            validate_paired_semantics(replace(
                frontier, qualifications=frontier.qualifications + edges[3:]))

    def test_obligation_object_frontier_16_accepts_and_17_alone_rejects(self):
        base = self.semantic
        additions = tuple(
            Obligation(f"obligation:frontier-{index}", "source-display",
                       (base.statements[index % len(base.statements)].identity,),
                       "authority:synthetic-content", "section:support")
            for index in range(14)
        )
        support = replace(
            base.sections[2],
            children=base.sections[2].children
            + tuple(SectionChild("obligation", item.identity) for item in additions),
        )
        frontier = replace(base, obligations=base.obligations + additions,
                           sections=base.sections[:2] + (support,))
        extra = Obligation("obligation:overflow-17", "source-display",
                           (base.statements[0].identity,),
                           "authority:synthetic-content", "section:support")
        overflow_support = replace(
            support, children=support.children + (SectionChild("obligation", extra.identity),))
        self.assertEqual(len(frontier.obligations), 16)
        self.assert_frontier_then_n_plus_one(
            frontier,
            replace(frontier, obligations=frontier.obligations + (extra,),
                    sections=frontier.sections[:2] + (overflow_support,)),
            "relation, provenance, or obligation cardinality",
        )

    def test_provenance_object_frontier_16_accepts_and_17_alone_rejects(self):
        base = self.semantic
        additions = tuple(
            Provenance(
                f"provenance:frontier-{index}", "Synthetic source.",
                "authority:synthetic-content", None, None,
                f"locator:frontier-{index}", (), (base.statements[0].identity,),
                "exact-targets", "section:support",
            )
            for index in range(8)
        )
        support = replace(
            base.sections[2],
            children=base.sections[2].children
            + tuple(SectionChild("provenance", item.identity) for item in additions),
        )
        frontier = replace(base, provenance=base.provenance + additions,
                           sections=base.sections[:2] + (support,))
        extra = Provenance(
            "provenance:overflow-17", "Synthetic source.",
            "authority:synthetic-content", None, None, "locator:overflow", (),
            (base.statements[0].identity,), "exact-targets", "section:support",
        )
        overflow_support = replace(
            support, children=support.children + (SectionChild("provenance", extra.identity),))
        self.assertEqual(len(frontier.provenance), 16)
        self.assert_frontier_then_n_plus_one(
            frontier,
            replace(frontier, provenance=frontier.provenance + (extra,),
                    sections=frontier.sections[:2] + (overflow_support,)),
            "relation, provenance, or obligation cardinality",
        )

    def test_target_and_package_frontiers_accept_before_their_n_plus_one(self):
        frontier = fixture.task064_topology_semantics()
        validate_paired_semantics(frontier)

        obligation = frontier.obligations[0]
        self.assertEqual(len(obligation.target_refs), 82)
        absent_resolving_target = frontier.table.identity
        self.assertNotIn(absent_resolving_target, obligation.target_refs)
        self.assertIn(absent_resolving_target, {frontier.table.identity})
        obligation_overflow = replace(
            obligation, target_refs=obligation.target_refs + (absent_resolving_target,))
        self.assertEqual(len(set(obligation_overflow.target_refs)), 83)
        with self.assertRaisesRegex(PairedSchemaRejected, "obligation targets cardinality"):
            validate_paired_semantics(replace(
                frontier, obligations=(obligation_overflow,) + frontier.obligations[1:]))

        provenance = frontier.provenance[0]
        self.assertEqual(len(provenance.target_refs), 92)
        self.assertNotIn(absent_resolving_target, provenance.target_refs)
        provenance_overflow = replace(
            provenance, target_refs=provenance.target_refs + (absent_resolving_target,))
        self.assertEqual(len(set(provenance_overflow.target_refs)), 93)
        with self.assertRaisesRegex(PairedSchemaRejected, "provenance targets cardinality"):
            validate_paired_semantics(replace(
                frontier, provenance=(provenance_overflow,) + frontier.provenance[1:]))

        row_provenance = frontier.provenance[1]
        self.assertEqual(len(row_provenance.package_identities), 2)
        package_overflow = replace(
            row_provenance,
            package_identities=row_provenance.package_identities + ("synthetic-package-overflow",),
        )
        with self.assertRaisesRegex(PairedSchemaRejected,
                                    "provenance package identities cardinality"):
            validate_paired_semantics(replace(
                frontier, provenance=(frontier.provenance[0], package_overflow)
                + frontier.provenance[2:]))


class Task067DispatchCrossProductProofs(unittest.TestCase):
    def test_only_four_exact_historical_terminal_and_paired_tuples_enter_verifiers(self):
        import briefforge_terminal_profile.manifest_admission as selector

        class PairedInvocationSubclass(PairedTerminalRendererInvocationAuthorization):
            pass

        class PairedConformanceSubclass(PairedTerminalSemanticArtifactConformanceAuthorization):
            pass

        class ManifestSubclass(PublicationManifestAuthorization):
            pass

        def blank(cls):
            return object.__new__(cls)

        invocation_choices = (
            blank(RendererInvocationAuthorization),
            blank(RepresentativeRendererInvocationAuthorization),
            blank(TerminalRendererInvocationAuthorization),
            blank(PairedTerminalRendererInvocationAuthorization),
            blank(PairedInvocationSubclass),
            object(),
        )
        conformance_choices = (
            blank(SemanticArtifactConformanceAuthorization),
            blank(RepresentativeSemanticArtifactConformanceAuthorization),
            blank(TerminalSemanticArtifactConformanceAuthorization),
            blank(PairedTerminalSemanticArtifactConformanceAuthorization),
            blank(PairedConformanceSubclass),
            object(),
        )
        authorization_choices = (
            blank(PublicationManifestAuthorization), blank(ManifestSubclass), object())
        contracts = (
            selector.historical._EXTENSION_CONTRACT,
            selector.MANIFEST_CONTRACT,
            "briefforge:paired-terminal-publication-manifest-admission-authority:3.0.0",
            "briefforge:unknown-future-manifest-authority:4.0.0",
        )
        accepted = {
            (RendererInvocationAuthorization, SemanticArtifactConformanceAuthorization,
             PublicationManifestAuthorization, selector.historical._EXTENSION_CONTRACT): "historical",
            (RepresentativeRendererInvocationAuthorization,
             RepresentativeSemanticArtifactConformanceAuthorization,
             PublicationManifestAuthorization, selector.historical._EXTENSION_CONTRACT): "historical",
            (TerminalRendererInvocationAuthorization,
             TerminalSemanticArtifactConformanceAuthorization,
             PublicationManifestAuthorization, selector.MANIFEST_CONTRACT): "terminal",
            (PairedTerminalRendererInvocationAuthorization,
             PairedTerminalSemanticArtifactConformanceAuthorization,
             PublicationManifestAuthorization,
             "briefforge:paired-terminal-publication-manifest-admission-authority:3.0.0"): "paired",
        }

        with patch.object(selector, "_manifest_contract") as contract_reader, \
             patch.object(selector, "_verify_archived_historical_closure"), \
             patch.object(selector.historical, "verify_persisted_publication_manifest",
                          return_value="historical") as historical, \
             patch.object(selector, "verify_persisted_terminal_publication_manifest",
                          return_value="terminal") as terminal, \
             patch("briefforge_paired_terminal_profile.manifest_admission."
                   "verify_persisted_paired_terminal_publication_manifest",
                   return_value="paired") as paired:
            for ia, ca, authorization, contract in itertools.product(
                    invocation_choices, conformance_choices, authorization_choices, contracts):
                contract_reader.return_value = contract
                for mock in (historical, terminal, paired):
                    mock.reset_mock()
                key = (type(ia), type(ca), type(authorization), contract)
                expected = accepted.get(key)
                kwargs = dict(
                    manifest_evidence_path="synthetic-manifest.json",
                    invocation_authorization=ia,
                    conformance_authorization=ca,
                    authorization=authorization,
                )
                with self.subTest(key=key):
                    if expected is None:
                        with self.assertRaisesRegex(ValueError, "mixed or unknown tuple"):
                            selector.verify_persisted_publication_manifest(**kwargs)
                        self.assertFalse(historical.called or terminal.called or paired.called)
                    else:
                        self.assertEqual(
                            selector.verify_persisted_publication_manifest(**kwargs), expected)
                        selected = {"historical": historical, "terminal": terminal,
                                    "paired": paired}[expected]
                        selected.assert_called_once_with(**kwargs)
                        self.assertEqual(sum(mock.call_count for mock in
                                             (historical, terminal, paired)), 1)


class Task067AssessorMutationIndependenceProofs(unittest.TestCase):
    def test_assessor_defect_rejects_unchanged_renderer_output_without_affecting_renderer(self):
        import briefforge_paired_terminal_profile.semantic_conformance as assessor

        projection = fixture.projection()
        artifact = render_paired_html(projection)
        verify_exact_paired_html(artifact, projection=projection)
        original_expected = assessor._expected_events

        def defect(projected):
            events = list(original_expected(projected))
            events.insert(-4, ("data", "assessor-only invented claim"))
            return tuple(events)

        with patch.object(assessor, "_expected_events", side_effect=defect):
            self.assertEqual(render_paired_html(projection), artifact)
            with self.assertRaises(PairedSemanticConformanceRejected):
                assessor.verify_exact_paired_html(artifact, projection=projection)

    def test_attachment_exclusion_and_conditional_semantic_drift_is_parsed_and_rejected(self):
        projection = fixture.projection()
        artifact = render_paired_html(projection)
        attacks = (
            artifact.replace(b"qualification:synthetic-1-0",
                             b"qualification:synthetic-1-x", 1),
            artifact.replace(b"Synthetic row source 1", b"Invented row source 1", 1),
            artifact.replace(b"preserve-source-meaning", b"future-work-language", 1),
            artifact.replace(b"classification:synthetic-1", b"classification:invented-1", 1),
        )
        for attack in attacks:
            with self.subTest(), self.assertRaises(PairedSemanticConformanceRejected):
                verify_exact_paired_html(attack, projection=projection)


class Task067CorrectedBlockerRegressionProofs(unittest.TestCase):
    """Adversarial locks for the corrected upstream and predecessor blockers."""

    @staticmethod
    def _refingerprint(declaration):
        return replace(
            declaration,
            fingerprint=compute_capability_declaration_fingerprint(declaration),
        )

    def test_declaration_rejects_subclasses_and_refingerprinted_substitutions(self):
        declaration = fixture._paired_declaration()
        self.assertIs(_verify_exact_paired_declaration(declaration), declaration)

        class DeclarationSubclass(RendererCapabilityDeclaration):
            pass

        extra_claim = CapabilityClaim(
            "capability:invented-fallback", "static", ("invented",), True)
        attacks = (
            DeclarationSubclass(**declaration.__dict__),
            replace(declaration, renderer_identity="renderer:historical-substitute"),
            replace(declaration, inventory_complete=False),
            replace(declaration, capabilities=declaration.capabilities + (extra_claim,)),
            replace(declaration,
                    unsupported_capabilities=("capability:paired-static-html",)),
            replace(declaration, declared_constraints=("deterministic", "bounded")),
            replace(declaration, extensions=(("future", "accepted"),)),
        )
        for attack in attacks:
            if type(attack) is RendererCapabilityDeclaration:
                attack = self._refingerprint(attack)
            with self.subTest(attack=attack), self.assertRaises(PairedProfileRejected):
                _verify_exact_paired_declaration(attack)

    def test_plan_rejects_subclass_wrong_cardinality_and_semantic_substitution(self):
        semantics = fixture.complete_semantics()
        declaration = fixture._paired_declaration()
        binding = fixture.admission_envelope(
            capability_declaration_identity=declaration.identity,
            capability_declaration_fingerprint=declaration.fingerprint,
        )
        token = fixture.admitted_semantics(semantics, envelope=binding)
        _, plan = fixture._synthetic_chain(
            semantics, binding, [dict(item) for item in token._authority_inventory],
            declaration)
        self.assertIs(_verify_exact_paired_plan(plan, declaration), plan)

        class PlanSubclass(VerifiedRendererCompatibilityPlan):
            pass

        attacks = [PlanSubclass(
            plan._bundle_document, plan.fingerprint, plan.mappings_document)]
        documents = [record.to_document() for record in plan.bundle.records]
        for index, change in (
            (6, {"renderer_id": "renderer:substitute"}),
            (6, {"capabilities": ["capability:paired-static-html", "capability:extra"]}),
            (7, {"supported": False}),
            (7, {"renderer_capability_ref": "renderer-capability:substitute"}),
        ):
            changed = json.loads(json.dumps(documents))
            changed[index]["semantic"].update(change)
            attacks.append(VerifiedRendererCompatibilityPlan(
                json.dumps({"profile_identity": plan.bundle.profile_identity,
                            "profile_version": plan.bundle.profile_version,
                            "records": changed}, sort_keys=True, separators=(",", ":")),
                plan.fingerprint, plan.mappings_document))
        attacks.append(VerifiedRendererCompatibilityPlan(
            json.dumps({"profile_identity": plan.bundle.profile_identity,
                        "profile_version": plan.bundle.profile_version,
                        "records": documents[:-1]}, sort_keys=True, separators=(",", ":")),
            plan.fingerprint, plan.mappings_document))

        for attack in attacks:
            with self.subTest(attack=type(attack)), self.assertRaises(PairedProfileRejected):
                _verify_exact_paired_plan(attack, declaration)

    def test_manifest_rejects_same_identity_predecessor_not_from_admitted_prefix(self):
        from briefforge_paired_terminal_profile.manifest_admission import (
            PairedManifestRejected, _predecessor,
        )

        token = fixture.admitted_semantics()
        predecessor = fixture.synthetic_predecessor(token)
        release_identity = token._admission.release_identity
        self.assertIs(_predecessor(predecessor, release_identity, token), predecessor)

        # Preserve all record identities and ordinary lineage while changing one
        # document in each important portion of the admitted eight-record prefix.
        for index, semantic_change in (
            (0, {"apparently_harmless": True}),
            (2, {"substituted_candidate": True}),
            (6, {"capabilities": ["capability:paired-static-html", "capability:extra"]}),
            (7, {"mode": "apparently-compatible-static"}),
        ):
            records = list(predecessor.records)
            original = records[index]
            document = original.to_document()
            document["semantic"] = dict(document["semantic"]) | semantic_change
            records[index] = BCRPRecord.from_document(document)
            attack = BCRPBundle(
                predecessor.profile_identity, predecessor.profile_version, tuple(records))
            with self.subTest(index=index), self.assertRaisesRegex(
                    PairedManifestRejected, "exact admitted Plan closure"):
                _predecessor(attack, release_identity, token)

    def test_every_private_token_field_is_issuer_sealed(self):
        names = (
            "_bindings", "_content_closure_fingerprint", "_semantics", "_admission",
            "_authority_inventory", "_profile_admission_fingerprint", "_plan_documents",
            "_predecessor_prefix_fingerprint", "_capability_tuple", "_nonce",
        )
        for name in names:
            token = fixture.admitted_semantics()
            original = getattr(token, name)
            replacement = b"x" if name == "_nonce" else ("substituted",)
            if replacement == original:
                replacement = object()
            object.__setattr__(token, name, replacement)
            with self.subTest(name=name), self.assertRaisesRegex(
                    PairedProfileRejected, "altered"):
                consume_paired_upstream_admission(token)


if __name__ == "__main__":
    unittest.main()
