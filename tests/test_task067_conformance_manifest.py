"""TASK-067 RED contract: independent conformance and exact Manifest tuple."""
from __future__ import annotations

from dataclasses import replace
import hashlib
import inspect
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from briefforge.bcrp.canonical import fingerprint_bundle
from briefforge.bcrp.model import BCRPBundle, BCRPRecord, PROFILE_ID, PROFILE_VERSION
from briefforge.publication_manifest_admission import (
    ManifestArtifactAdmission, PublicationManifestAuthorization,
    compute_artifact_set_fingerprint, compute_manifest_authorization_fingerprint,
)
from briefforge_paired_terminal_profile.controlled_invocation import (
    INVOCATION_EVIDENCE_IDENTITY, INVOCATION_POLICY_IDENTITY,
    PairedTerminalRendererInvocationAuthorization,
    compute_paired_invocation_authorization_fingerprint,
    invoke_controlled_paired_renderer, paired_renderer_implementation_digest,
)
from briefforge_paired_terminal_profile.manifest_admission import (
    CAPABILITY_TUPLE,
    PAIRED_MANIFEST_CONTRACT,
    PairedManifestRejected,
    paired_renderer_source_digest,
    produce_paired_terminal_publication_manifest,
    verify_paired_manifest_current_eligibility,
    verify_persisted_paired_terminal_publication_manifest,
    validate_paired_manifest_capability_tuple,
    _closure_digest,
)
from briefforge_paired_terminal_profile.renderer import render_paired_html
from briefforge_paired_terminal_profile.semantic_conformance import (
    CONFORMANCE_EVIDENCE_IDENTITY,
    CONFORMANCE_POLICY_IDENTITY,
    PairedSemanticArtifactConformanceAuthorization,
    PairedSemanticConformanceRejected,
    VerifiedPairedSemanticArtifactConformance,
    assess_paired_semantic_artifact_conformance,
    assess_persisted_paired_semantic_artifact_conformance,
    compute_paired_conformance_authorization_fingerprint, paired_assessor_source_digest,
    verify_exact_paired_html,
)
from tests import paired_terminal_fixture as fixture


EXPECTED_CAPABILITY_TUPLE = (
    ("profile", "briefforge:representative-paired-terminal-static-html-profile:3.0.0"),
    ("projection_schema", "briefforge:representative-paired-static-html-projection-schema:1.0.0"),
    ("projection_implementation", "briefforge_paired_terminal_profile.projection:1.0.0"),
    ("renderer", "briefforge:representative-paired-static-html-renderer:1.0.0"),
    ("invocation_policy", "briefforge-paired-terminal-controlled-renderer-invocation-policy:1.0.0"),
    ("invocation_evidence", "briefforge:paired-terminal-controlled-renderer-invocation-evidence:1.0.0"),
    ("invocation_authorization_class", "briefforge_paired_terminal_profile.controlled_invocation.PairedTerminalRendererInvocationAuthorization"),
    ("conformance_profile", "briefforge:representative-paired-static-html-conformance-profile:1.0.0"),
    ("assessor_implementation", "briefforge_paired_terminal_profile.semantic_conformance:1.0.0"),
    ("conformance_policy", "briefforge-paired-terminal-semantic-conformance-assessment-policy:1.0.0"),
    ("conformance_evidence", "briefforge:paired-terminal-semantic-artifact-conformance-evidence:1.0.0"),
    ("conformance_authorization_class", "briefforge_paired_terminal_profile.semantic_conformance.PairedTerminalSemanticArtifactConformanceAuthorization"),
    ("manifest_policy", "briefforge-paired-terminal-publication-manifest-admission-policy:3.0.0"),
    ("manifest_profile", "briefforge:paired-terminal-publication-manifest-admission-profile:3.0.0"),
    ("manifest_contract", "briefforge:paired-terminal-publication-manifest-admission-authority:3.0.0"),
    ("manifest_implementation", "briefforge_paired_terminal_profile.manifest_admission:1.0.0"),
    ("manifest_authorization_class", "briefforge.publication_manifest_admission.PublicationManifestAuthorization"),
)


class Task067ConformanceManifestTests(unittest.TestCase):
    def setUp(self):
        self.projection = fixture.projection()
        self.artifact = render_paired_html(self.projection)

    def conformance_authorization(self, **changes):
        values = dict(
            identity="conformance-authorization:synthetic-paired",
            policy_identity=CONFORMANCE_POLICY_IDENTITY,
            evidence_identity=CONFORMANCE_EVIDENCE_IDENTITY,
            authorization_time="2026-08-02T10:01:00Z",
            release_identity=self.projection.release_identity,
            release_fingerprint=self.projection.release_fingerprint,
            lifecycle_scope_fingerprint=self.projection.lifecycle_scope_fingerprint,
            plan_identity=self.projection.plan_identity,
            plan_fingerprint=self.projection.plan_fingerprint,
            capability_declaration_identity=self.projection.capability_declaration_identity,
            capability_declaration_fingerprint=self.projection.capability_declaration_fingerprint,
            profile_identity=fixture.CONFORMANCE_ID,
            profile_version=fixture.CONFORMANCE_VERSION,
            projection_fingerprint=self.projection.projection_fingerprint,
            renderer_identity=fixture.RENDERER_ID,
            renderer_version=fixture.RENDERER_VERSION,
            renderer_implementation_digest=paired_renderer_implementation_digest(),
            assessor_implementation_digest=paired_assessor_source_digest(),
            invocation_authorization_identity="invocation-authorization:synthetic-paired",
            invocation_authorization_fingerprint="5" * 64,
            invocation_evidence_fingerprint="6" * 64,
            artifact_sha256=hashlib.sha256(self.artifact).hexdigest(),
            artifact_byte_length=len(self.artifact),
            artifact_media_type="text/html",
            fingerprint="",
        )
        values.update(changes)
        provisional = PairedSemanticArtifactConformanceAuthorization(**values)
        return replace(provisional, fingerprint=
                       compute_paired_conformance_authorization_fingerprint(provisional))

    def test_independent_parser_accepts_exact_semantics(self):
        report = verify_exact_paired_html(self.artifact, projection=self.projection)
        self.assertEqual(report.table_count, 1)
        self.assertEqual(report.column_headings, fixture.COLUMN_HEADINGS)
        self.assertEqual(report.row_identities,
                         tuple(row.identity for row in self.projection.table.rows))
        self.assertEqual(report.relationship_identities,
                         tuple(row.relationship_identity for row in self.projection.table.rows))
        assessed = assess_paired_semantic_artifact_conformance(
            artifact_bytes=self.artifact, projection=self.projection,
            authorization=self.conformance_authorization())
        self.assertEqual(assessed.verdict, "approved")

    def test_assessor_source_is_renderer_independent(self):
        module = __import__("briefforge_paired_terminal_profile.semantic_conformance",
                            fromlist=["*"])
        source = inspect.getsource(module)
        self.assertNotIn("from .renderer", source)
        self.assertNotIn("import briefforge_paired_terminal_profile.renderer", source)
        self.assertNotIn("render_paired_html", source)
        self.assertNotIn("HTML_FRAGMENT", source)

    def test_extra_reordered_or_semantically_drifted_rows_columns_and_tables_fail(self):
        attacks = (
            self.artifact.replace(b"Relationship case", b"Case", 1),
            self.artifact.replace(b"<tbody", b"<table></table><tbody", 1),
            self.artifact.replace(b"row:synthetic-1", b"row:synthetic-other", 1),
            self.artifact.replace(b"0.125", b"0.126", 1),
            self.artifact.replace(b"present", b"absent", 1),
            self.artifact.replace(b"first_difference", b"raw", 1),
            self.artifact.replace(b"1990-2011", b"1990-2099", 1),
            self.artifact.replace(b"count 21", b"count 22", 1),
            self.artifact.replace(b"</tbody>", b"<tr><td>extra</td></tr></tbody>", 1),
        )
        for attack in attacks:
            with self.subTest(), self.assertRaises(PairedSemanticConformanceRejected):
                verify_exact_paired_html(attack, projection=self.projection)

    def test_every_row_provenance_field_is_rendered_and_independently_assessed(self):
        original = self.projection.provenance[1]
        html = self.artifact.decode("utf-8")
        for value in (
            original.identity, original.citation, original.authority_ref,
            original.source_locator, *original.package_identities, *original.target_refs,
            original.target_rule, original.placement_ref,
        ):
            self.assertIn(value, html)
        from briefforge_paired_terminal_profile.projection import compute_projection_fingerprint
        for name, value in (
            ("citation", "Drifted row citation"),
            ("source_locator", "locator:row-drifted"),
            ("package_identities", ("synthetic-package-drifted", "synthetic-difference-package-1")),
        ):
            changed = replace(original, **{name: value})
            projected = replace(
                self.projection,
                provenance=self.projection.provenance[:1] + (changed,) + self.projection.provenance[2:],
                projection_fingerprint="",
            )
            projected = replace(projected,
                projection_fingerprint=compute_projection_fingerprint(projected))
            rendered = render_paired_html(projected)
            with self.subTest(field=name):
                self.assertNotEqual(rendered, self.artifact)
                with self.assertRaises(PairedSemanticConformanceRejected):
                    verify_exact_paired_html(rendered, projection=self.projection)

    def test_hidden_claim_active_content_external_resource_and_operational_authority_fail(self):
        attacks = (
            self.artifact.replace(b"</main>", b'<span hidden>extra claim</span></main>', 1),
            self.artifact.replace(b"</main>", b'<script>alert(1)</script></main>', 1),
            self.artifact.replace(b"</main>", b'<img src="https://evil.invalid/x"></main>', 1),
            self.artifact.replace(b"</main>", b'<a href="javascript:alert(1)">x</a></main>', 1),
            self.artifact.replace(b"</main>", b'authority:briefforge-controlled-local-delivery</main>', 1),
        )
        for attack in attacks:
            with self.subTest(), self.assertRaises(PairedSemanticConformanceRejected):
                verify_exact_paired_html(attack, projection=self.projection)

    def test_renderer_defect_is_detected_without_renderer_oracle(self):
        defect = self.artifact.replace(b"0.125", b"0.999", 1)
        with patch("briefforge_paired_terminal_profile.renderer.render_paired_html",
                   return_value=defect):
            produced = render_paired_html(self.projection)  # local bound function remains exact
            self.assertEqual(produced, self.artifact)
        with self.assertRaises(PairedSemanticConformanceRejected):
            verify_exact_paired_html(defect, projection=self.projection)

    def test_assessor_disagreement_blocks_even_when_renderer_bytes_are_deterministic(self):
        authorization = self.conformance_authorization(
            artifact_sha256="0" * 64)  # independently wrong binding
        with self.assertRaises(PairedSemanticConformanceRejected):
            assess_paired_semantic_artifact_conformance(
                artifact_bytes=self.artifact, projection=self.projection,
                authorization=authorization)
        class AuthorizationSubclass(PairedSemanticArtifactConformanceAuthorization):
            pass
        exact = self.conformance_authorization()
        with self.assertRaises(PairedSemanticConformanceRejected):
            assess_paired_semantic_artifact_conformance(
                artifact_bytes=self.artifact, projection=self.projection,
                authorization=AuthorizationSubclass(**exact.__dict__))

    def test_manifest_capability_tuple_is_exact_ordered_and_complete(self):
        self.assertEqual(CAPABILITY_TUPLE, EXPECTED_CAPABILITY_TUPLE)
        validate_paired_manifest_capability_tuple(CAPABILITY_TUPLE)
        self.assertEqual(PAIRED_MANIFEST_CONTRACT,
                         "briefforge:paired-terminal-publication-manifest-admission-authority:3.0.0")

    def test_historical_partial_unknown_and_cross_version_substitutions_fail(self):
        substitutions = (
            (0, "briefforge:representative-terminal-static-html-profile:2.0.0"),
            (1, "briefforge:representative-static-html-projection-schema:1.0.0"),
            (3, "briefforge:representative-static-html-renderer:1.0.0"),
            (4, "briefforge-terminal-controlled-renderer-invocation-policy:1.0.0"),
            (7, "briefforge:terminal-static-html-semantic-realization-profile:1.0.0"),
            (12, "briefforge-terminal-publication-manifest-admission-policy:2.0.0"),
            (14, "briefforge:terminal-publication-manifest-admission-authority:2.0.0"),
        )
        for index, old_identity in substitutions:
            changed = list(EXPECTED_CAPABILITY_TUPLE)
            changed[index] = (changed[index][0], old_identity)
            with self.subTest(index=index), self.assertRaises(PairedManifestRejected):
                validate_paired_manifest_capability_tuple(tuple(changed))
        for changed in (EXPECTED_CAPABILITY_TUPLE[:-1],
                        EXPECTED_CAPABILITY_TUPLE + (("future", "latest"),),
                        tuple(reversed(EXPECTED_CAPABILITY_TUPLE))):
            with self.subTest(), self.assertRaises(PairedManifestRejected):
                validate_paired_manifest_capability_tuple(changed)

    def test_selector_contract_requires_three_exact_classes_before_verifier(self):
        selector = __import__("briefforge_terminal_profile.manifest_admission", fromlist=["*"])
        source = inspect.getsource(selector.verify_persisted_publication_manifest)
        self.assertIn("PairedTerminalRendererInvocationAuthorization", source)
        self.assertIn("PairedTerminalSemanticArtifactConformanceAuthorization", source)
        self.assertIn("PublicationManifestAuthorization", source)
        self.assertIn(PAIRED_MANIFEST_CONTRACT, inspect.getsource(selector))
        self.assertIn("verify_persisted_paired_terminal_publication_manifest", source)
        self.assertNotIn("isinstance(", source)

        # The exact classes are intentionally distinct and non-substitutable.
        self.assertIsNot(PairedTerminalRendererInvocationAuthorization,
                         PairedSemanticArtifactConformanceAuthorization)
        self.assertIsNot(PairedTerminalRendererInvocationAuthorization,
                         PublicationManifestAuthorization)


class Task067PairedManifestProductionTests(unittest.TestCase):
    """Synthetic authority mocks exercise production without a governed chain act."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.semantics = fixture.complete_semantics()
        self.token = fixture.admitted_semantics(self.semantics)
        self.projection = fixture.projection(semantics=self.semantics)
        for name in ("output", "invocation", "authorization-ledger", "conformance", "manifest"):
            (self.root / name).mkdir()
        self.projection_evidence = fixture.persisted_projection_evidence(
            self.projection, self.token, self.root)
        self.ia = self._invocation_authorization()
        self.invocation = invoke_controlled_paired_renderer(
            projection=self.projection, authorization=self.ia, upstream_admission=self.token,
            projection_evidence=self.projection_evidence)
        self.ca = self._conformance_authorization()
        self.conformance_path = self.root / "conformance" / "paired-semantic-conformance-evidence.json"
        self.conformance = assess_persisted_paired_semantic_artifact_conformance(
            admitted_semantics=self.semantics, upstream_admission=self.token,
            projection_evidence=self.projection_evidence, invocation=self.invocation, invocation_authorization=self.ia,
            authorization=self.ca, evidence_path=self.conformance_path)
        self.assertIs(type(self.conformance), VerifiedPairedSemanticArtifactConformance)
        self.predecessor = self._predecessor()
        self.lifecycle = type("SyntheticActiveLifecycle", (), {
            "inventory_digest": self.projection.lifecycle_scope_fingerprint})()
        self.authorization = self._manifest_authorization()

    def _invocation_authorization(self):
        provisional = PairedTerminalRendererInvocationAuthorization(
            "invocation-authorization:manifest-paired", INVOCATION_POLICY_IDENTITY,
            INVOCATION_EVIDENCE_IDENTITY, "2026-08-02T10:00:00Z",
            self.projection.release_identity, self.projection.release_fingerprint,
            self.projection.lifecycle_scope_fingerprint, self.projection.plan_identity,
            self.projection.plan_fingerprint, self.projection.capability_declaration_identity,
            self.projection.capability_declaration_fingerprint, fixture.PROFILE_ID,
            fixture.PROFILE_VERSION, fixture.SCHEMA_ID, fixture.SCHEMA_VERSION,
            self.projection.projection_fingerprint, fixture.RENDERER_ID,
            fixture.RENDERER_VERSION, paired_renderer_implementation_digest(),
            str((self.root / "output").resolve()), "paired.html",
            str((self.root / "invocation").resolve()), "invocation.json",
            str((self.root / "authorization-ledger").resolve()), 1, 1_000_000,
            "text/html", "deterministic-replay",
            (("LANG", "C"), ("LC_ALL", "C"), ("TZ", "UTC"),
             ("PYTHONDONTWRITEBYTECODE", "1"), ("PYTHONHASHSEED", "0"),
             ("PYTHONUTF8", "1")), (), "")
        return replace(provisional, fingerprint=
                       compute_paired_invocation_authorization_fingerprint(provisional))

    def _conformance_authorization(self):
        provisional = PairedSemanticArtifactConformanceAuthorization(
            "conformance-authorization:manifest-paired", CONFORMANCE_POLICY_IDENTITY,
            CONFORMANCE_EVIDENCE_IDENTITY, "2026-08-02T10:01:00Z",
            self.projection.release_identity, self.projection.release_fingerprint,
            self.projection.lifecycle_scope_fingerprint, self.projection.plan_identity,
            self.projection.plan_fingerprint, self.projection.capability_declaration_identity,
            self.projection.capability_declaration_fingerprint, fixture.CONFORMANCE_ID,
            fixture.CONFORMANCE_VERSION, self.projection.projection_fingerprint,
            fixture.RENDERER_ID, fixture.RENDERER_VERSION,
            paired_renderer_implementation_digest(), paired_assessor_source_digest(),
            self.ia.identity,
            self.ia.fingerprint, self.invocation.fingerprint,
            hashlib.sha256(self.invocation.artifact_bytes).hexdigest(),
            len(self.invocation.artifact_bytes), "text/html", "")
        return replace(provisional, fingerprint=
                       compute_paired_conformance_authorization_fingerprint(provisional))

    def _predecessor(self):
        return fixture.synthetic_predecessor(self.token)

    def _manifest_authorization(self):
        artifact = ManifestArtifactAdmission(
            "artifact:synthetic-paired", "primary-semantic-publication", "paired.html",
            "text/html", len(self.invocation.artifact_bytes),
            hashlib.sha256(self.invocation.artifact_bytes).hexdigest(), 0,
            str(self.invocation.artifact_path), self.projection.release_identity,
            self.projection.release_fingerprint, self.projection.plan_identity,
            self.projection.plan_fingerprint, fixture.RENDERER_ID, fixture.RENDERER_VERSION,
            self.ia.identity, self.invocation.fingerprint, self.ca.identity,
            self.conformance.fingerprint, ())
        inventory = (artifact,)
        provisional = PublicationManifestAuthorization(
            "manifest-authorization:synthetic-paired",
            "briefforge-paired-terminal-publication-manifest-admission-policy:3.0.0",
            "briefforge:paired-terminal-publication-manifest-admission-profile:3.0.0", "3.0.0",
            "authority:briefforge-publication-manifest-projector", "project:BriefForge",
            "publication-manifest-projector", "2026-08-02T10:02:00Z",
            self.projection.release_identity, self.projection.release_fingerprint,
            self.projection.lifecycle_scope_fingerprint, self.projection.plan_identity,
            self.projection.plan_fingerprint, self.projection.capability_declaration_identity,
            self.projection.capability_declaration_fingerprint, fixture.RENDERER_ID,
            fixture.RENDERER_VERSION, paired_renderer_source_digest(), self.ia.identity,
            self.ia.fingerprint, self.invocation.fingerprint, self.ca.identity,
            self.ca.fingerprint, fixture.CONFORMANCE_ID, fixture.CONFORMANCE_VERSION,
            "briefforge_paired_terminal_profile.semantic_conformance:1.0.0",
            self.conformance.fingerprint, "approved",
            _closure_digest(self.predecessor),
            inventory, compute_artifact_set_fingerprint(inventory),
            "manifest:synthetic-paired", "3.0.0", "2026-08-02T10:03:00Z",
            "briefforge_paired_terminal_profile.manifest_admission:1.0.0", "1.0.0",
            str((self.root / "manifest").resolve()), "publication-manifest.json",
            str((self.root / "ledger").resolve()), "record:synthetic-paired-manifest",
            ("distribution-authority", "distribution-execution", "successful-publication-authority",
             "deployment-authority", "atlasforge-authority", "browser-behavior-certification",
             "accessibility-certification", "editorial-certification", "visual-certification",
             "factual-reassessment"), "")
        return replace(provisional, fingerprint=compute_manifest_authorization_fingerprint(provisional))

    def _kwargs(self):
        return dict(capability_tuple=CAPABILITY_TUPLE,
            admitted_semantics=self.semantics, upstream_admission=self.token,
            projection=self.projection, projection_evidence=self.projection_evidence,
            invocation_authorization=self.ia,
            verified_invocation=self.invocation, conformance_authorization=self.ca,
            verified_conformance=self.conformance, predecessor_bundle=self.predecessor,
            lifecycle_scope=self.lifecycle, authorization=self.authorization)

    @patch("briefforge.publication_manifest_admission._lifecycle_current", return_value=True)
    def test_synthetic_production_reload_and_current_eligibility(self, current):
        result = produce_paired_terminal_publication_manifest(**self._kwargs())
        self.assertFalse(result.blocked, result.findings)
        record = result.verified.bundle.one("PublicationManifestRecord")
        self.assertEqual(len(result.verified.bundle.records), 11)
        self.assertEqual(record.extensions[0]["payload"]["paired_atomic_tuple"]["capability_tuple"],
                         [list(item) for item in CAPABILITY_TUPLE])
        self.assertEqual(record.extensions[0]["payload"]["distribution_authority"], "absent")
        reloaded = verify_persisted_paired_terminal_publication_manifest(
            manifest_evidence_path=self.root / "manifest" / "publication-manifest.json",
            **self._kwargs())
        self.assertEqual(reloaded.fingerprint, result.verified.fingerprint)
        eligible = verify_paired_manifest_current_eligibility(
            reloaded, lifecycle_scope=self.lifecycle)
        self.assertFalse(eligible.blocked)
        self.assertGreaterEqual(current.call_count, 3)

        import briefforge_terminal_profile.manifest_admission as selector
        selected = selector.verify_persisted_publication_manifest(
            manifest_evidence_path=self.root / "manifest" / "publication-manifest.json",
            **self._kwargs())
        self.assertEqual(selected.fingerprint, result.verified.fingerprint)

    @patch("briefforge.publication_manifest_admission._lifecycle_current", return_value=True)
    def test_manifest_tamper_and_mixed_version_fail_reload(self, _current):
        result = produce_paired_terminal_publication_manifest(**self._kwargs())
        self.assertFalse(result.blocked, result.findings)
        path = self.root / "manifest" / "publication-manifest.json"
        original = path.read_bytes()
        document = json.loads(original)
        document["records"][-1]["extensions"][0]["payload"]["paired_atomic_tuple"]["capability_tuple"][0][1] = \
            "briefforge:representative-terminal-static-html-profile:2.0.0"
        path.write_text(json.dumps(document, sort_keys=True, separators=(",", ":")))
        with self.assertRaises(PairedManifestRejected):
            verify_persisted_paired_terminal_publication_manifest(
                manifest_evidence_path=path, **self._kwargs())
        path.write_bytes(original)
        mixed = list(CAPABILITY_TUPLE)
        mixed[14] = (mixed[14][0],
                     "briefforge:terminal-publication-manifest-admission-authority:2.0.0")
        mixed_kwargs = self._kwargs()
        mixed_kwargs["capability_tuple"] = tuple(mixed)
        with self.assertRaises(PairedManifestRejected):
            verify_persisted_paired_terminal_publication_manifest(
                manifest_evidence_path=path, **mixed_kwargs)


if __name__ == "__main__":
    unittest.main()
