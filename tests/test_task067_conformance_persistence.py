"""TASK-067 paired conformance persistence and provenance boundary tests."""
from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from briefforge_paired_terminal_profile.controlled_invocation import (
    INVOCATION_EVIDENCE_IDENTITY, INVOCATION_POLICY_IDENTITY,
    PairedTerminalRendererInvocationAuthorization,
    compute_paired_invocation_authorization_fingerprint,
    invoke_controlled_paired_renderer, paired_renderer_implementation_digest,
)
from briefforge_paired_terminal_profile.profile import verify_full_upstream_paired_terminal_admission
from briefforge_paired_terminal_profile.semantic_conformance import (
    CONFORMANCE_EVIDENCE_IDENTITY, CONFORMANCE_POLICY_IDENTITY,
    PairedSemanticConformanceRejected,
    PairedTerminalSemanticArtifactConformanceAuthorization,
    VerifiedPairedSemanticArtifactConformance,
    assess_persisted_paired_semantic_artifact_conformance,
    compute_paired_conformance_authorization_fingerprint, paired_assessor_source_digest,
    verify_persisted_paired_semantic_artifact_conformance,
)
from tests import paired_terminal_fixture as fixture


class Task067ConformancePersistenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.semantics = fixture.complete_semantics()
        self.token = fixture.admitted_semantics(self.semantics)
        self.projection = fixture.projection(semantics=self.semantics)
        self.output = self.root / "output"; self.inv_evidence = self.root / "invocation"
        self.conf_evidence = self.root / "conformance"; self.ledger = self.root / "ledger"
        for directory in (self.output, self.inv_evidence, self.conf_evidence, self.ledger): directory.mkdir()
        self.projection_evidence = fixture.persisted_projection_evidence(
            self.projection, self.token, self.root)
        self.ia = self._invocation_authorization()
        self.invocation = invoke_controlled_paired_renderer(
            projection=self.projection, authorization=self.ia, upstream_admission=self.token,
            projection_evidence=self.projection_evidence)
        self.ca = self._conformance_authorization()
        self.path = self.conf_evidence / "paired-semantic-conformance-evidence.json"

    def _invocation_authorization(self):
        values = dict(
            identity="invocation-authorization:persistence-paired", policy_identity=INVOCATION_POLICY_IDENTITY,
            evidence_identity=INVOCATION_EVIDENCE_IDENTITY, authorization_time="2026-08-02T10:00:00Z",
            release_identity=self.projection.release_identity, release_fingerprint=self.projection.release_fingerprint,
            lifecycle_scope_fingerprint=self.projection.lifecycle_scope_fingerprint,
            plan_identity=self.projection.plan_identity, plan_fingerprint=self.projection.plan_fingerprint,
            capability_declaration_identity=self.projection.capability_declaration_identity,
            capability_declaration_fingerprint=self.projection.capability_declaration_fingerprint,
            profile_identity=fixture.PROFILE_ID, profile_version=fixture.PROFILE_VERSION,
            schema_identity=fixture.SCHEMA_ID, schema_version=fixture.SCHEMA_VERSION,
            projection_fingerprint=self.projection.projection_fingerprint,
            renderer_identity=fixture.RENDERER_ID, renderer_version=fixture.RENDERER_VERSION,
            renderer_implementation_digest=paired_renderer_implementation_digest(),
            output_directory=str(self.output.resolve()), output_filename="paired.html",
            evidence_directory=str(self.inv_evidence.resolve()), evidence_filename="invocation.json",
            authorization_ledger_directory=str(self.ledger.resolve()),
            output_count=1, maximum_output_bytes=1_000_000, media_type="text/html",
            invocation_mode="deterministic-replay",
            environment=(("LANG", "C"), ("LC_ALL", "C"), ("TZ", "UTC"),
                         ("PYTHONDONTWRITEBYTECODE", "1"), ("PYTHONHASHSEED", "0"),
                         ("PYTHONUTF8", "1")), external_assets=(), fingerprint="")
        provisional = PairedTerminalRendererInvocationAuthorization(**values)
        return replace(provisional, fingerprint=compute_paired_invocation_authorization_fingerprint(provisional))

    def _conformance_authorization(self, **changes):
        artifact = self.invocation.artifact_bytes
        import hashlib
        values = dict(
            identity="conformance-authorization:persistence-paired",
            policy_identity=CONFORMANCE_POLICY_IDENTITY, evidence_identity=CONFORMANCE_EVIDENCE_IDENTITY,
            authorization_time="2026-08-02T10:01:00Z",
            release_identity=self.projection.release_identity, release_fingerprint=self.projection.release_fingerprint,
            lifecycle_scope_fingerprint=self.projection.lifecycle_scope_fingerprint,
            plan_identity=self.projection.plan_identity, plan_fingerprint=self.projection.plan_fingerprint,
            capability_declaration_identity=self.projection.capability_declaration_identity,
            capability_declaration_fingerprint=self.projection.capability_declaration_fingerprint,
            profile_identity=fixture.CONFORMANCE_ID, profile_version=fixture.CONFORMANCE_VERSION,
            projection_fingerprint=self.projection.projection_fingerprint,
            renderer_identity=fixture.RENDERER_ID, renderer_version=fixture.RENDERER_VERSION,
            renderer_implementation_digest=paired_renderer_implementation_digest(),
            assessor_implementation_digest=paired_assessor_source_digest(),
            invocation_authorization_identity=self.ia.identity,
            invocation_authorization_fingerprint=self.ia.fingerprint,
            invocation_evidence_fingerprint=self.invocation.fingerprint,
            artifact_sha256=hashlib.sha256(artifact).hexdigest(), artifact_byte_length=len(artifact),
            artifact_media_type="text/html", fingerprint="")
        values.update(changes)
        provisional = PairedTerminalSemanticArtifactConformanceAuthorization(**values)
        return replace(provisional, fingerprint=compute_paired_conformance_authorization_fingerprint(provisional))

    def _assess(self):
        return assess_persisted_paired_semantic_artifact_conformance(
            admitted_semantics=self.semantics, upstream_admission=self.token,
            projection_evidence=self.projection_evidence, invocation=self.invocation, invocation_authorization=self.ia,
            authorization=self.ca, evidence_path=self.path)

    def test_persists_canonical_bounded_evidence_and_independently_reloads(self):
        assessed = self._assess()
        self.assertIs(type(assessed), VerifiedPairedSemanticArtifactConformance)
        self.assertEqual(assessed.evidence_bytes, self.path.read_bytes())
        document = json.loads(assessed.evidence_bytes)
        self.assertEqual(document["invocation"]["evidence_fingerprint"], self.invocation.fingerprint)
        self.assertEqual(document["release_closure"]["projection_fingerprint"],
                         self.projection.projection_fingerprint)
        self.assertIn("hostile interpreter", document["trusted_process_limitation"])
        reloaded = verify_persisted_paired_semantic_artifact_conformance(
            admitted_semantics=self.semantics, upstream_admission=self.token,
            projection_evidence=self.projection_evidence, invocation=self.invocation, invocation_authorization=self.ia,
            authorization=self.ca, evidence_path=self.path)
        self.assertEqual(reloaded, assessed)

    def test_caller_asserted_or_lookalike_invocation_provenance_fails(self):
        forged_ca = self._conformance_authorization(invocation_evidence_fingerprint="f" * 64)
        with self.assertRaises(PairedSemanticConformanceRejected):
            assess_persisted_paired_semantic_artifact_conformance(
                admitted_semantics=self.semantics, upstream_admission=self.token,
                projection_evidence=self.projection_evidence, invocation=self.invocation, invocation_authorization=self.ia,
                authorization=forged_ca, evidence_path=self.path)
        class Lookalike(type(self.invocation)): pass
        lookalike = Lookalike(**self.invocation.__dict__)
        with self.assertRaises(PairedSemanticConformanceRejected):
            assess_persisted_paired_semantic_artifact_conformance(
                admitted_semantics=self.semantics, upstream_admission=self.token,
                projection_evidence=self.projection_evidence, invocation=lookalike, invocation_authorization=self.ia,
                authorization=self.ca, evidence_path=self.path)

    def test_tampered_artifact_invocation_or_conformance_evidence_fails_reload(self):
        self._assess()
        document = json.loads(self.path.read_bytes())
        document["verdict"] = "approved-ish"
        self.path.write_text(json.dumps(document, sort_keys=True, separators=(",", ":")))
        with self.assertRaises(PairedSemanticConformanceRejected):
            verify_persisted_paired_semantic_artifact_conformance(
                admitted_semantics=self.semantics, upstream_admission=self.token,
                projection_evidence=self.projection_evidence, invocation=self.invocation, invocation_authorization=self.ia,
                authorization=self.ca, evidence_path=self.path)


if __name__ == "__main__": unittest.main()
