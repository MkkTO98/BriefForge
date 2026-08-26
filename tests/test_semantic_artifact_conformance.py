"""TASK-053 semantic-artifact conformance boundary tests."""
from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from briefforge.bcrp.validation import validate_bundle
from briefforge.bcrp.model import BCRPBundle, BCRPRecord
from briefforge.controlled_renderer_invocation import build_minimal_html_projection
from briefforge.renderer_adapter import render_minimal_html_projection
from briefforge.semantic_artifact_conformance import (
    ACCEPTED_ASSESSOR_IDENTITY,
    ACCEPTED_ASSESSOR_OWNER,
    ACCEPTED_ASSESSOR_ROLE,
    CONFORMANCE_POLICY_ID,
    SEMANTIC_REALIZATION_PROFILE_ID,
    SEMANTIC_REALIZATION_PROFILE_VERSION,
    SemanticArtifactConformanceAuthorization,
    _complete_semantic_findings,
    assess_semantic_artifact_conformance,
    compute_conformance_authorization_fingerprint,
    verify_exact_semantic_html,
    verify_persisted_semantic_artifact_conformance,
)
from tests import test_controlled_renderer_invocation as controlled_tests


class SemanticArtifactConformanceTests(unittest.TestCase):
    # Reuse TASK-052's real governed construction path without inheriting and
    # rediscovering its test cases in this focused module.
    setUp = controlled_tests.ControlledRendererInvocationTests.setUp
    _ledger_directory = controlled_tests.ControlledRendererInvocationTests._ledger_directory
    def _candidate(self, snapshot):
        base = controlled_tests.ControlledRendererInvocationTests._candidate(self, snapshot)
        records = []
        for record in base.records:
            document = record.to_document()
            if record.kind == "PortablePresentationMaterialRecord":
                document["semantic"]["authorities"].append({
                    "id": ACCEPTED_ASSESSOR_IDENTITY,
                    "owner_identity": ACCEPTED_ASSESSOR_OWNER,
                    "role": ACCEPTED_ASSESSOR_ROLE,
                    "scope": "one-semantic-artifact-conformance-assessment",
                })
            records.append(BCRPRecord.from_document(document))
        return BCRPBundle(base.profile_identity, base.profile_version, tuple(records))
    _inputs = controlled_tests.ControlledRendererInvocationTests._inputs
    _authorization = controlled_tests.ControlledRendererInvocationTests._authorization
    _invoke = controlled_tests.ControlledRendererInvocationTests._invoke

    def _conformance_authorization(self, inputs, invocation_authorization, evidence_directory, **changes):
        snapshot, release, scope, declaration, _planning_authorization, plan = inputs
        artifact = Path(invocation_authorization.output_directory) / invocation_authorization.output_filename
        import hashlib
        base = dict(
            identity="semantic-conformance-authorization:task053",
            policy_identity=CONFORMANCE_POLICY_ID,
            authority_identity=ACCEPTED_ASSESSOR_IDENTITY,
            authority_owner=ACCEPTED_ASSESSOR_OWNER,
            authority_role=ACCEPTED_ASSESSOR_ROLE,
            authorization_time="2026-07-17T11:00:00Z",
            profile_identity=SEMANTIC_REALIZATION_PROFILE_ID,
            profile_version=SEMANTIC_REALIZATION_PROFILE_VERSION,
            assessor_identity=ACCEPTED_ASSESSOR_IDENTITY,
            release_identity=release.release.identity,
            release_fingerprint=release.fingerprint.digest,
            lifecycle_inventory_digest=scope.inventory_digest,
            plan_identity=plan.plan.identity,
            plan_fingerprint=plan.fingerprint.digest,
            capability_identity=declaration.identity,
            capability_fingerprint=declaration.fingerprint,
            invocation_authorization_identity=invocation_authorization.identity,
            invocation_authorization_fingerprint=invocation_authorization.fingerprint,
            invocation_evidence_fingerprint="", # filled after persisted TASK-052 verification
            artifact_identity=f"artifact:{invocation_authorization.identity.split(':', 1)[-1]}",
            artifact_sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),
            artifact_filename=invocation_authorization.output_filename,
            artifact_media_type=invocation_authorization.media_type,
            artifact_byte_length=len(artifact.read_bytes()),
            renderer_identity=invocation_authorization.renderer_identity,
            renderer_version=invocation_authorization.renderer_version,
            renderer_implementation_digest=invocation_authorization.renderer_implementation_digest,
            assessor_implementation="briefforge.semantic_artifact_conformance",
            assessor_version="1.0.0",
            output_class="standalone-static-html-semantic-realization",
            maximum_artifact_bytes=invocation_authorization.maximum_output_bytes,
            exclusions=("manifest-authority", "distribution-authority", "successful-publication-authority", "external-assets", "active-content"),
            artifact_destination=str(artifact),
            invocation_evidence_destination=str(Path(invocation_authorization.output_directory) / invocation_authorization.evidence_filename),
            evidence_directory=str(Path(evidence_directory).resolve()),
            evidence_filename="semantic-conformance-evidence.json",
            commitment_ledger_directory=invocation_authorization.authorization_ledger_directory,
            record_identity="semantic-conformance:task053",
        )
        from briefforge.controlled_renderer_invocation import verify_persisted_renderer_invocation
        verified = verify_persisted_renderer_invocation(
            artifact_path=artifact,
            evidence_path=Path(invocation_authorization.output_directory) / invocation_authorization.evidence_filename,
            evidence_snapshot=snapshot, lifecycle_scope=scope, declaration=declaration,
            planning_authorization=inputs[4], authorization=invocation_authorization,
        )
        base["invocation_evidence_fingerprint"] = verified.fingerprint.digest
        base.update(changes)
        provisional = SemanticArtifactConformanceAuthorization(**base, fingerprint="")
        return replace(provisional, fingerprint=compute_conformance_authorization_fingerprint(provisional))

    def test_real_task052_path_passes_persists_one_record_and_independently_reloads(self):
        inputs = self._inputs()
        with tempfile.TemporaryDirectory() as output, tempfile.TemporaryDirectory() as evidence:
            invocation_authorization = self._authorization(inputs, output)
            invoked = self._invoke(inputs, output, invocation_authorization)
            self.assertFalse(invoked.blocked)
            authorization = self._conformance_authorization(inputs, invocation_authorization, evidence)
            before = (inputs, invocation_authorization, invoked.verified.artifact_bytes)
            result = assess_semantic_artifact_conformance(
                artifact_path=Path(output) / "publication.html",
                invocation_evidence_path=Path(output) / "invocation-evidence.json",
                evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2],
                declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
                invocation_authorization=invocation_authorization, authorization=authorization,
            )
            self.assertFalse(result.blocked, result.findings)
            self.assertEqual(result.findings, ())
            self.assertEqual(len(result.verified.bundle.records), 10)
            self.assertEqual(len(result.verified.bundle.records_of_kind("SemanticArtifactConformanceRecord")), 1)
            self.assertFalse(result.verified.bundle.records_of_kind("PublicationManifestRecord"))
            record = result.verified.bundle.one("SemanticArtifactConformanceRecord")
            self.assertTrue(record.semantic["semantic_pass"])
            self.assertEqual(record.semantic["audit_ref"], invoked.verified.bundle.one("GeneratedArtifactAuditRecord").identity)
            self.assertEqual(record.extensions[0]["payload"]["profile_identity"], SEMANTIC_REALIZATION_PROFILE_ID)
            payload = record.extensions[0]["payload"]
            accounting = payload["requirement_accounting"]
            self.assertEqual(set(accounting["requirement_outcomes"]), {"conformant"})
            self.assertEqual(len(accounting["expected_requirements"]), len(accounting["actual_inventory"]))
            self.assertEqual(
                {item["id"] for item in accounting["expected_requirements"]},
                {item["requirement_ref"] for item in accounting["actual_inventory"]},
            )
            expected_by_id = {item["id"]: item["expected"] for item in accounting["expected_requirements"]}
            self.assertTrue(all(
                item["actual"] == expected_by_id[item["requirement_ref"]]
                and item["extraction"] == "strict-structural-field"
                for item in accounting["actual_inventory"]
            ))
            self.assertEqual(len(accounting["authority_audit_links"]), 14)
            self.assertEqual(len({item["role"] for item in accounting["authority_audit_links"]}), 14)
            self.assertEqual(accounting["audit_link_character"], "traceable-binding-not-independent-conformance-proof")
            self.assertEqual(payload["manifest_authority"], "absent")
            self.assertEqual(payload["distribution_authority"], "absent")
            self.assertEqual(payload["successful_publication"], "not-asserted")
            self.assertEqual(before[2], (Path(output) / "publication.html").read_bytes())
            reloaded = verify_persisted_semantic_artifact_conformance(
                artifact_path=Path(output) / "publication.html",
                invocation_evidence_path=Path(output) / "invocation-evidence.json",
                conformance_evidence_path=Path(evidence) / authorization.evidence_filename,
                evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2],
                declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
                invocation_authorization=invocation_authorization, authorization=authorization,
            )
            self.assertEqual(reloaded.fingerprint, result.verified.fingerprint)
            generic = validate_bundle(reloaded.bundle, through_layer="L5")
            self.assertTrue(generic.findings)
            self.assertTrue(all(
                f.layer == "L1"
                and f.family == "extension-boundary"
                and f.location == "/extensions/0"
                and f.message == "Unknown required semantic extension cannot be processed."
                for f in generic.findings
            ))

    def test_two_materially_different_governed_semantic_shapes_are_checked_structurally(self):
        inputs = self._inputs()
        projection = build_minimal_html_projection(
            verified_release=inputs[1], evidence_snapshot=inputs[0], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
        )
        artifact = render_minimal_html_projection(projection).html.encode("utf-8")
        evidence = verify_exact_semantic_html(artifact, projection)
        self.assertEqual(evidence["statement_ids"], ["statement:task052-observation"])

        second = replace(
            projection,
            identity=replace(projection.identity, title="Distinct & governed case"),
            organizing_purpose=replace(projection.organizing_purpose, statement="Assess a separate bounded transport constraint."),
            statements=(replace(
                projection.statements[0], statement_id="statement:distinct", encounter_meaning="Do not exceed 12.5 kg in region B.",
                authority_ref="authority:distinct", upstream_reference_ids=(), obligation_ids=(),
            ),),
            upstream_references=(), obligations=(),
        )
        second_artifact = render_minimal_html_projection(second).html.encode("utf-8")
        second_evidence = verify_exact_semantic_html(second_artifact, second)
        self.assertEqual(second_evidence["statement_ids"], ["statement:distinct"])
        for old, new in ((b"Do not", b"Do"), (b"12.5", b"21.5"), (b"kg", b"lb"), (b"region B", b"region C")):
            with self.subTest(second_case_change=old), self.assertRaises(ValueError):
                verify_exact_semantic_html(second_artifact.replace(old, new, 1), second)

    def test_omission_duplication_reordering_hidden_raw_spoof_and_unauthorized_additions_fail(self):
        inputs = self._inputs()
        projection = build_minimal_html_projection(
            verified_release=inputs[1], evidence_snapshot=inputs[0], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
        )
        valid = render_minimal_html_projection(projection).html.encode()
        text = projection.statements[0].encounter_meaning.encode()
        attacks = (
            valid.replace(text, b"", 1),
            valid.replace(b"</article>", text + b"</article>", 1),
            valid.replace(b"<h1>Synthetic observation</h1>", b"<h1>Injected</h1>"),
            valid.replace(b"<article ", b'<article hidden="hidden" ', 1),
            valid.replace(b"<main>", b"<main>&lt;p&gt;" + text + b"&lt;/p&gt;", 1),
            valid.replace(b"</main>", b"<p>Unauthorized addition</p></main>", 1),
            valid.replace(b"<html lang=\"en\">", b"detached<html lang=\"en\">", 1),
        )
        for attack in attacks:
            with self.subTest(attack=attack[:80]), self.assertRaises(ValueError):
                verify_exact_semantic_html(attack, projection)

    def test_extra_metadata_semantic_attributes_global_reordering_and_multi_defect_findings_fail(self):
        inputs = self._inputs()
        projection = build_minimal_html_projection(
            verified_release=inputs[1], evidence_snapshot=inputs[0], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
        )
        valid = render_minimal_html_projection(projection).html.encode("utf-8")
        attacks = (
            valid.replace(b"</head>", b'<meta name="invented-authority" content="claim:unauthorized">\n</head>', 1),
            valid.replace(b"<main>", b'<main data-reader-experience="invented-authoritative-meaning">', 1),
            valid.replace(b"<main>", b'<main id="unauthorized-semantic-region">', 1),
        )
        for attack in attacks:
            with self.subTest(attack=attack[:100]), self.assertRaises(ValueError):
                verify_exact_semantic_html(attack, projection)
        reference_start = valid.index(b'<section data-grammar-stage="trace" data-attention="supporting"><h2>Reference inventory</h2>')
        obligation_start = valid.index(b'<section data-grammar-stage="trace" data-attention="supporting"><h2>Obligation inventory</h2>')
        details_start = valid.index(b'<details data-grammar-stage="trace"')
        swapped = valid[:reference_start] + valid[obligation_start:details_start] + valid[reference_start:obligation_start] + valid[details_start:]
        with self.assertRaises(ValueError):
            verify_exact_semantic_html(swapped, projection)
        exhibit_payload = b"<p>No renderer-visible exhibit candidates detected in existing source evidence.</p>"
        article_start = valid.index(b"<article ")
        article_end = valid.index(b"</article>", article_start) + len(b"</article>")
        article = valid[article_start:article_end]
        relocated = valid.replace(exhibit_payload, b"__EXHIBIT_PAYLOAD__", 1).replace(article, exhibit_payload, 1).replace(b"__EXHIBIT_PAYLOAD__", article, 1)
        with self.assertRaises(ValueError):
            verify_exact_semantic_html(relocated, projection)

        attacked = attacks[0]
        combined_reference_start = attacked.index(b'<section data-grammar-stage="trace" data-attention="supporting"><h2>Reference inventory</h2>')
        combined_obligation_start = attacked.index(b'<section data-grammar-stage="trace" data-attention="supporting"><h2>Obligation inventory</h2>')
        combined_details_start = attacked.index(b'<details data-grammar-stage="trace"')
        combined = attacked[:combined_reference_start] + attacked[combined_obligation_start:combined_details_start] + attacked[combined_reference_start:combined_obligation_start] + attacked[combined_details_start:]
        structural_findings = [item for item in _complete_semantic_findings(combined, projection) if item.code.startswith("unauthorized-or-misordered-structure-")]
        self.assertGreaterEqual(len(structural_findings), 2)

        altered = valid.replace(b"<title>Synthetic observation</title>", b"<title>Altered title</title>", 1)
        altered = altered.replace(b"No analysis, live data, discovery, or distribution.", b"Altered non-scope.", 1)
        findings = _complete_semantic_findings(altered, projection)
        requirement_findings = [item for item in findings if item.code == "semantic-requirement-nonconformant"]
        self.assertGreaterEqual(len(requirement_findings), 2)
        self.assertTrue(any("title text" in item.message for item in requirement_findings))
        self.assertTrue(any("non-scope non_scope" in item.message for item in requirement_findings))

    def test_altered_wording_polarity_number_unit_scope_reference_provenance_and_links_fail(self):
        inputs = self._inputs()
        projection = build_minimal_html_projection(
            verified_release=inputs[1], evidence_snapshot=inputs[0], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
        )
        valid = render_minimal_html_projection(projection).html.encode()
        replacements = (
            (b"explicitly bounded", b"not bounded"), (b"observation", b"recommendation"),
            (b"One static synthetic presentation.", b"Two static synthetic presentations."),
            (b"external:task052", b"external:stale"),
            (b"provenance:task052", b"provenance:stale"),
            (b"authority:synthetic-upstream", b"authority:other"),
        )
        for old, new in replacements:
            attack = valid.replace(old, new, 1)
            self.assertNotEqual(attack, valid)
            with self.subTest(old=old), self.assertRaises(ValueError):
                verify_exact_semantic_html(attack, projection)

    def test_stale_bindings_or_failed_semantics_return_findings_and_no_approval_or_evidence(self):
        inputs = self._inputs()
        with tempfile.TemporaryDirectory() as output, tempfile.TemporaryDirectory() as evidence:
            invocation_authorization = self._authorization(inputs, output)
            self._invoke(inputs, output, invocation_authorization)
            valid = self._conformance_authorization(inputs, invocation_authorization, evidence)
            stale_changes = (
                {"release_fingerprint": "0" * 64}, {"lifecycle_inventory_digest": "0" * 64},
                {"plan_fingerprint": "0" * 64}, {"capability_fingerprint": "0" * 64},
                {"invocation_authorization_fingerprint": "0" * 64},
                {"invocation_evidence_fingerprint": "0" * 64}, {"artifact_sha256": "0" * 64},
                {"assessor_identity": "authority:stale-assessor"},
                {"profile_identity": "profile:stale"}, {"profile_version": "2.0.0"},
            )
            for changes in stale_changes:
                stale = replace(valid, **changes)
                stale = replace(stale, fingerprint=compute_conformance_authorization_fingerprint(replace(stale, fingerprint="")))
                result = assess_semantic_artifact_conformance(
                    artifact_path=Path(output) / "publication.html", invocation_evidence_path=Path(output) / "invocation-evidence.json",
                    evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2], declaration=inputs[3],
                    planning_authorization=inputs[4], verified_plan=inputs[5], invocation_authorization=invocation_authorization,
                    authorization=stale,
                )
                with self.subTest(changes=changes):
                    self.assertTrue(result.blocked)
                    self.assertIsNone(result.verified)
                    self.assertTrue(result.findings)
                    self.assertEqual(tuple(Path(evidence).iterdir()), ())

    def test_independent_expectation_does_not_invoke_renderer_and_modes_are_explicit(self):
        inputs = self._inputs()
        projection = build_minimal_html_projection(
            verified_release=inputs[1], evidence_snapshot=inputs[0], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
        )
        artifact = render_minimal_html_projection(projection).html.encode("utf-8")
        with patch("briefforge.renderer_adapter.render_minimal_html_projection", side_effect=AssertionError("renderer must not run")):
            evidence = verify_exact_semantic_html(artifact, projection)
        self.assertEqual(evidence["aggregate_verdict"], "approved")
        for mode in ("static-fallback", "unsupported", "blocked", "unknown"):
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                verify_exact_semantic_html(artifact, replace(projection, selected_expression_modes=(mode,)))
        for meaning in ("x" * 141, "# hidden heading", "*emphasized*"):
            narrowed = replace(
                projection,
                statements=(replace(projection.statements[0], encounter_meaning=meaning),),
            )
            with self.subTest(meaning=meaning[:20]), self.assertRaises(ValueError):
                verify_exact_semantic_html(render_minimal_html_projection(narrowed).html.encode("utf-8"), narrowed)

    def test_assessor_authority_must_be_carried_by_independently_verified_release(self):
        def ledger_residue():
            return {
                path.resolve()
                for path in Path("/tmp").iterdir()
                if path.name.startswith("briefforge-task052-ledger-")
            }

        baseline = ledger_residue()
        base = controlled_tests.ControlledRendererInvocationTests()
        # The outer TestCase owns helper cleanup before any helper operation can
        # allocate resources. This remains effective on success or exception.
        self.addCleanup(base.doCleanups)
        base.setUp()
        inputs = base._inputs()

        # Interruption inside mkdtemp after allocation but before return is the
        # narrowest ownership gap. Prefix cleanup is registered before that
        # allocation-capable call and deterministically removes the directory.
        interrupted = controlled_tests.ControlledRendererInvocationTests()
        self.addCleanup(interrupted.doCleanups)
        interrupted.setUp()
        allocated = []
        real_mkdtemp = controlled_tests.tempfile.mkdtemp

        def allocate_then_interrupt(*args, **kwargs):
            path = real_mkdtemp(*args, **kwargs)
            allocated.append(Path(path).resolve())
            raise RuntimeError("interrupt inside mkdtemp after allocation")

        with tempfile.TemporaryDirectory() as interrupted_output:
            with patch(
                "tests.test_controlled_renderer_invocation.tempfile.mkdtemp",
                side_effect=allocate_then_interrupt,
            ), self.assertRaisesRegex(
                RuntimeError, "^interrupt inside mkdtemp after allocation$"
            ):
                interrupted._ledger_directory(interrupted_output)
            self.assertEqual(len(ledger_residue() - baseline), 1)
        interrupted.doCleanups()
        self.assertEqual(ledger_residue(), baseline)
        self.assertTrue(allocated)
        self.assertTrue(all(not path.exists() for path in allocated))

        with tempfile.TemporaryDirectory() as output, tempfile.TemporaryDirectory() as evidence:
            invocation_authorization = base._authorization(inputs, output)
            repeated_authorization = base._authorization(inputs, output)
            self.assertEqual(repeated_authorization, invocation_authorization)
            self.assertEqual(len(ledger_residue() - baseline), 1)
            invoked = base._invoke(inputs, output, invocation_authorization)
            self.assertFalse(invoked.blocked)
            authorization = self._conformance_authorization(inputs, invocation_authorization, evidence)
            result = assess_semantic_artifact_conformance(
                artifact_path=Path(output) / "publication.html",
                invocation_evidence_path=Path(output) / "invocation-evidence.json",
                evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2],
                declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
                invocation_authorization=invocation_authorization, authorization=authorization,
            )
            self.assertTrue(result.blocked)
            self.assertIn("unreleased-assessor-authority", {item.code for item in result.findings})
            self.assertEqual(tuple(Path(evidence).iterdir()), ())
        base.doCleanups()
        self.assertEqual(ledger_residue(), baseline)

    def test_active_external_hidden_duplicate_and_attribute_channels_fail(self):
        inputs = self._inputs()
        projection = build_minimal_html_projection(
            verified_release=inputs[1], evidence_snapshot=inputs[0], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
        )
        valid = render_minimal_html_projection(projection).html.encode("utf-8")
        attacks = (
            valid.replace(b"</main>", b"<script>alert(1)</script></main>"),
            valid.replace(b"<main>", b'<main><a href="https://example.invalid">x</a>'),
            valid.replace(b"<body ", b'<body onclick="x" ', 1),
            valid.replace(b"<article ", b'<article aria-hidden="true" ', 1),
            valid.replace(b"<article ", b'<article class="offscreen" ', 1),
            valid.replace(b"<article ", b'<article data-unknown="invented" ', 1),
            valid.replace(b'<article id="', b'<article id="duplicate" id="', 1),
            valid.replace(b"</main>", b'<iframe srcdoc="x"></iframe></main>'),
        )
        for attack in attacks:
            with self.subTest(attack=attack[-100:]), self.assertRaises(ValueError):
                verify_exact_semantic_html(attack, projection)

    def test_authorization_is_one_act_complete_and_replay_is_blocked(self):
        inputs = self._inputs()
        with tempfile.TemporaryDirectory() as output, tempfile.TemporaryDirectory() as evidence:
            invocation_authorization = self._authorization(inputs, output)
            self._invoke(inputs, output, invocation_authorization)
            valid = self._conformance_authorization(inputs, invocation_authorization, evidence)
            critical_changes = (
                {"policy_identity": "policy:other"}, {"authority_identity": "authority:other"},
                {"artifact_filename": "other.html"}, {"artifact_media_type": "application/xhtml+xml"},
                {"artifact_byte_length": valid.artifact_byte_length + 1}, {"renderer_version": "9.9.9"},
                {"renderer_implementation_digest": "0" * 64}, {"assessor_implementation": "other.assessor"},
                {"assessor_version": "9.9.9"}, {"output_class": "manifest"},
                {"maximum_artifact_bytes": valid.maximum_artifact_bytes + 1}, {"exclusions": ()},
            )
            for changes in critical_changes:
                altered = replace(valid, **changes, fingerprint="")
                altered = replace(altered, fingerprint=compute_conformance_authorization_fingerprint(altered))
                result = assess_semantic_artifact_conformance(
                    artifact_path=Path(output) / "publication.html", invocation_evidence_path=Path(output) / "invocation-evidence.json",
                    evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2], declaration=inputs[3],
                    planning_authorization=inputs[4], verified_plan=inputs[5], invocation_authorization=invocation_authorization,
                    authorization=altered,
                )
                with self.subTest(changes=changes):
                    self.assertTrue(result.blocked)
                    self.assertIsNone(result.verified)
            collision = replace(valid, record_identity="release:task052", fingerprint="")
            collision = replace(collision, fingerprint=compute_conformance_authorization_fingerprint(collision))
            collision_result = assess_semantic_artifact_conformance(
                artifact_path=Path(output) / "publication.html", invocation_evidence_path=Path(output) / "invocation-evidence.json",
                evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2], declaration=inputs[3],
                planning_authorization=inputs[4], verified_plan=inputs[5], invocation_authorization=invocation_authorization,
                authorization=collision,
            )
            self.assertTrue(collision_result.blocked)
            self.assertEqual({item.code for item in collision_result.findings}, {"conformance-closure-failed"})
            first = assess_semantic_artifact_conformance(
                artifact_path=Path(output) / "publication.html", invocation_evidence_path=Path(output) / "invocation-evidence.json",
                evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2], declaration=inputs[3],
                planning_authorization=inputs[4], verified_plan=inputs[5], invocation_authorization=invocation_authorization,
                authorization=valid,
            )
            self.assertFalse(first.blocked)
            with patch("briefforge.semantic_artifact_conformance.verify_exact_semantic_html") as semantic_assessment:
                replay = assess_semantic_artifact_conformance(
                    artifact_path=Path(output) / "publication.html", invocation_evidence_path=Path(output) / "invocation-evidence.json",
                    evidence_snapshot=inputs[0], verified_release=inputs[1], lifecycle_scope=inputs[2], declaration=inputs[3],
                    planning_authorization=inputs[4], verified_plan=inputs[5], invocation_authorization=invocation_authorization,
                    authorization=valid,
                )
                semantic_assessment.assert_not_called()
            self.assertTrue(replay.blocked)
            self.assertIsNone(replay.verified)
            self.assertEqual({item.code for item in replay.findings}, {"assessment-authorization-consumed"})


if __name__ == "__main__":
    unittest.main()
