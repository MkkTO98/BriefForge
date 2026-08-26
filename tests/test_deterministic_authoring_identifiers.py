"""Tests for deterministic authoring identifier generation.

Identifier generation is a builder-only authoring convenience. It must produce
existing Candidate Presentation Package runtime objects without changing
validation, promotion, ready packages, renderer boundaries, rendered output, or
conformance.
"""

from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
TESTS = PROJECT_ROOT / "tests"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(TESTS))

from test_presentation_package_builder import (  # noqa: E402
    EXPECTED_TASK_014_FINGERPRINT,
    denmark_country_profile_candidate_built_with_builder,
)


def deterministic_package(*, changed_statement: bool = False):
    from briefforge.builder import PresentationPackageBuilder

    second_statement = (
        "A changed statement about the same authoring proof."
        if changed_statement
        else "A second stable statement about the same authoring proof."
    )

    return (
        PresentationPackageBuilder()
        .identity(
            package_id="deterministic-authoring-proof",
            title="Deterministic Authoring Proof",
            purpose_summary="Prove generated identifier reproducibility.",
            scope="Builder-only deterministic ids.",
            non_scope="No runtime model change.",
        )
        .organizing_purpose(
            statement="Prove equivalent semantic authoring inputs generate stable ids.",
            scope="Statements, references, and obligations.",
            non_scope="No persistence or registry allocation.",
        )
        .add_upstream_reference(
            owning_project="Manual proof source",
            reference_kind="source-note",
            locator="manual://deterministic-authoring-proof",
            owned_meaning="The source owns the proof context.",
        )
        .add_obligation(
            category="scope-control",
            requirement="Generated ids must not change runtime semantics.",
        )
        .add_statement(
            encounter_meaning="A stable statement about generated identifiers.",
            belongs_to_purpose="Deterministic authoring proof",
            encounter_mode="orientation",
            encounter_description="Introduce the deterministic id proof.",
        )
        .add_statement(
            encounter_meaning=second_statement,
            belongs_to_purpose="Deterministic authoring proof",
            encounter_mode="supporting-context",
            encounter_description="Exercise localized identifier churn.",
        )
        .build()
    )


class DeterministicAuthoringIdentifierTests(unittest.TestCase):
    def test_equivalent_packages_generate_identical_identifiers(self):
        first = deterministic_package()
        second = deterministic_package()

        self.assertEqual(first, second)
        self.assertEqual(
            [statement.statement_id for statement in first.statements],
            [statement.statement_id for statement in second.statements],
        )
        self.assertEqual(first.upstream_references[0].reference_id, second.upstream_references[0].reference_id)
        self.assertEqual(first.obligations[0].obligation_id, second.obligations[0].obligation_id)

    def test_explicit_identifiers_override_generated_identifiers(self):
        from briefforge.builder import PresentationPackageBuilder

        candidate = (
            PresentationPackageBuilder()
            .identity(
                package_id="explicit-package-id",
                title="Explicit Identifier Proof",
                purpose_summary="Prove explicit ids are respected.",
                scope="Explicit ids only.",
                non_scope="No generated override.",
            )
            .organizing_purpose(
                statement="Explicit ids remain authoritative authoring choices.",
                scope="Builder authoring.",
                non_scope="No runtime changes.",
            )
            .add_upstream_reference(
                reference_id="explicit-reference-id",
                owning_project="Manual proof source",
                reference_kind="source-note",
                locator="manual://explicit-id-proof",
                owned_meaning="The explicit reference id must remain intact.",
            )
            .add_obligation(
                obligation_id="explicit-obligation-id",
                category="scope-control",
                requirement="The explicit obligation id must remain intact.",
                applies_to=("explicit-statement-id", "explicit-reference-id"),
            )
            .add_statement(
                statement_id="explicit-statement-id",
                encounter_meaning="The explicit statement id must remain intact.",
                belongs_to_purpose="Explicit id proof",
                encounter_mode="orientation",
                encounter_description="Show explicit ids override generation.",
                upstream_reference_ids=("explicit-reference-id",),
                obligation_ids=("explicit-obligation-id",),
            )
            .build()
        )

        self.assertEqual(candidate.identity.package_id, "explicit-package-id")
        self.assertEqual(candidate.statements[0].statement_id, "explicit-statement-id")
        self.assertEqual(candidate.upstream_references[0].reference_id, "explicit-reference-id")
        self.assertEqual(candidate.obligations[0].obligation_id, "explicit-obligation-id")

    def test_changing_statement_changes_only_that_statement_generated_identifier(self):
        baseline = deterministic_package()
        changed = deterministic_package(changed_statement=True)

        self.assertEqual(baseline.identity.package_id, changed.identity.package_id)
        self.assertEqual(baseline.statements[0].statement_id, changed.statements[0].statement_id)
        self.assertNotEqual(baseline.statements[1].statement_id, changed.statements[1].statement_id)
        self.assertEqual(baseline.upstream_references[0].reference_id, changed.upstream_references[0].reference_id)
        self.assertEqual(baseline.obligations[0].obligation_id, changed.obligations[0].obligation_id)

    def test_unchanged_references_retain_generated_identifiers(self):
        baseline = deterministic_package()
        changed_statement = deterministic_package(changed_statement=True)

        self.assertEqual(
            baseline.upstream_references[0].reference_id,
            changed_statement.upstream_references[0].reference_id,
        )

    def test_unchanged_obligations_retain_generated_identifiers(self):
        baseline = deterministic_package()
        changed_statement = deterministic_package(changed_statement=True)

        self.assertEqual(
            baseline.obligations[0].obligation_id,
            changed_statement.obligations[0].obligation_id,
        )

    def test_semantic_fingerprints_remain_stable_when_generated_semantics_are_unchanged(self):
        from briefforge.runtime import semantic_fingerprint

        self.assertEqual(semantic_fingerprint(deterministic_package()), semantic_fingerprint(deterministic_package()))

    def test_task_014_end_to_end_workflow_remains_unchanged_with_explicit_ids(self):
        from briefforge.promotion import promote_candidate_presentation_package
        from briefforge.renderer_adapter import (
            check_rendered_artifact_conformance,
            check_renderer_adapter_compatibility,
            html_renderer_contract,
            invoke_renderer_adapter,
            render_minimal_html,
        )
        from briefforge.runtime import semantic_fingerprint
        from briefforge.validation import validate_candidate_presentation_package

        candidate = denmark_country_profile_candidate_built_with_builder()
        judgment = validate_candidate_presentation_package(candidate)
        ready = promote_candidate_presentation_package(candidate, judgment)
        contract = html_renderer_contract()
        compatibility = check_renderer_adapter_compatibility(ready, contract)
        invocation = invoke_renderer_adapter(ready, contract)
        artifact = render_minimal_html(ready, contract)
        conformance = check_rendered_artifact_conformance(ready, artifact)

        self.assertEqual(semantic_fingerprint(candidate), EXPECTED_TASK_014_FINGERPRINT)
        self.assertTrue(judgment.valid, judgment.findings)
        self.assertTrue(compatibility.compatible)
        self.assertTrue(invocation.accepted)
        self.assertTrue(conformance.conforms, conformance.findings)


if __name__ == "__main__":
    unittest.main()
