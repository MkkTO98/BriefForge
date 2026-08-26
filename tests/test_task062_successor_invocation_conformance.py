"""Focused adversarial proof for TASK-062 successor invocation/conformance."""
from __future__ import annotations
from dataclasses import replace
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from briefforge.bounded_loopback_deployment import DeploymentRouteItem, DeploymentTarget
from briefforge_terminal_profile.profile import build_terminal_authority_profile, TERMINAL_OPERATIONAL_IDENTITIES
from briefforge_terminal_profile.projection import build_terminal_representative_projection
from briefforge_terminal_profile.renderer_adapter import adapt_terminal_projection, adapter_source_digest
from briefforge_terminal_profile.controlled_invocation import (
    TerminalRendererInvocationAuthorization, compute_terminal_invocation_authorization_fingerprint,
    invoke_controlled_terminal_renderer, verify_persisted_terminal_renderer_invocation,
)
from briefforge_terminal_profile.semantic_conformance import (
    TerminalSemanticArtifactConformanceAuthorization,
    compute_terminal_conformance_authorization_fingerprint,
    assess_terminal_semantic_artifact_conformance,
    verify_persisted_terminal_semantic_artifact_conformance,
    verify_exact_terminal_html, terminal_assessor_implementation_digest,
)
from briefforge.representative_controlled_invocation import representative_renderer_implementation_digest
from tests import representative_fixture


class Task062SuccessorInvocationConformanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        dirs=[self.root/x for x in ("destination","delivery","deployment","verification")]
        for x in dirs: x.mkdir(); x.chmod(0o700)
        self.profile=build_terminal_authority_profile(destination_parent=dirs[0],destination_basename="brief.html",
            delivery_ledger=dirs[1],target=DeploymentTarget("127.0.0.1",38127,"http://127.0.0.1:38127"),
            routes=(DeploymentRouteItem("/brief.html","brief.html","text/html"),),deployment_ledger=dirs[2],
            verification_ledger=dirs[3],content_authorities=(dict(
                representative_fixture.CONTENT_AUTHORITY,
                role="presentation-content-authority",
                scope="released-presentation-semantic-content",
            ),))
        original=representative_fixture.candidate_bundle
        def candidate(snapshot,*,complete_audience_edge=False):
            bundle=original(snapshot,complete_audience_edge=complete_audience_edge)
            bundle.one("PortablePresentationMaterialRecord").semantic["authorities"]=[dict(x) for x in self.profile.authorities]
            return bundle
        with patch.object(representative_fixture,"candidate_bundle",candidate):
            self.inputs=representative_fixture.representative_chain(self,"task062-successor")
        self.projection=build_terminal_representative_projection(verified_release=self.inputs[1],evidence_snapshot=self.inputs[0],
            lifecycle_scope=self.inputs[2],declaration=self.inputs[3],planning_authorization=self.inputs[4],
            verified_plan=self.inputs[5],authority_profile=self.profile)

    def invocation_authorization(self,**changes):
        root=self.root/("output-"+str(len(tuple(self.root.glob("output-*")))))
        ledger=self.root/("ledger-"+str(len(tuple(self.root.glob("ledger-*")))))
        root.mkdir(); ledger.mkdir(); translated=adapt_terminal_projection(self.projection)
        values=dict(identity="terminal-invocation-authorization:focused",policy_identity="briefforge-terminal-controlled-renderer-invocation-policy:1.0.0",
            authority_identity="authority:briefforge-controlled-renderer-invocation",authority_owner="project:BriefForge",
            authority_role="renderer-invocation-authority",authorization_time="2026-08-01T09:03:00Z",
            release_identity=self.inputs[1].release.identity,release_fingerprint=self.inputs[1].fingerprint.digest,
            lifecycle_inventory_digest=self.inputs[2].inventory_digest,plan_identity=self.inputs[5].plan.identity,
            plan_fingerprint=self.inputs[5].fingerprint.digest,capability_identity=self.inputs[3].identity,
            capability_fingerprint=self.inputs[3].fingerprint,successor_projection_fingerprint=self.projection.fingerprint,
            translated_projection_fingerprint=translated.fingerprint,adapter_identity=self.projection.adapter_identity,
            adapter_version=self.projection.adapter_version,adapter_implementation_digest=adapter_source_digest(),
            renderer_identity=self.projection.renderer_identity,renderer_version=self.projection.renderer_version,
            renderer_implementation_digest=representative_renderer_implementation_digest(),authorization_ledger_directory=str(ledger.resolve()),
            output_directory=str(root.resolve()),output_filename="artifact/brief.html",output_count=1,maximum_output_bytes=1_000_000,
            media_type="text/html",environment=(("LANG","C"),("LC_ALL","C"),("TZ","UTC"),("PYTHONDONTWRITEBYTECODE","1"),("PYTHONHASHSEED","0"),("PYTHONUTF8","1")),
            external_assets=(),invocation_mode="one-artifact-with-determinism-replay",timeout_seconds=2,
            evidence_filename="evidence/terminal-invocation-evidence.json")
        values.update(changes); provisional=TerminalRendererInvocationAuthorization(**values,fingerprint="")
        return replace(provisional,fingerprint=compute_terminal_invocation_authorization_fingerprint(provisional))

    def invoke(self,a):
        return invoke_controlled_terminal_renderer(verified_release=self.inputs[1],evidence_snapshot=self.inputs[0],
            lifecycle_scope=self.inputs[2],declaration=self.inputs[3],planning_authorization=self.inputs[4],
            verified_plan=self.inputs[5],authority_profile=self.profile,authorization=a)

    def conform_authorization(self,ia,invoked,**changes):
        directory=self.root/("conform-"+str(len(tuple(self.root.glob("conform-*"))))); directory.mkdir()
        audit=invoked.bundle.one("GeneratedArtifactAuditRecord").semantic["artifact"]
        values=dict(identity="terminal-conformance-authorization:focused",policy_identity="briefforge-terminal-semantic-conformance-assessment-policy:1.0.0",
            authority_identity="authority:briefforge-semantic-artifact-conformance",authority_owner="project:BriefForge",
            authority_role="semantic-artifact-conformance-assessor",authorization_time="2026-08-01T09:04:00Z",
            profile_identity="briefforge:terminal-static-html-semantic-realization-profile:1.0.0",profile_version="1.0.0",
            assessor_implementation="briefforge_terminal_profile.semantic_conformance",assessor_version="1.0.0",
            assessor_implementation_digest=terminal_assessor_implementation_digest(),release_identity=self.inputs[1].release.identity,
            release_fingerprint=self.inputs[1].fingerprint.digest,lifecycle_inventory_digest=self.inputs[2].inventory_digest,
            plan_identity=self.inputs[5].plan.identity,plan_fingerprint=self.inputs[5].fingerprint.digest,
            capability_identity=self.inputs[3].identity,capability_fingerprint=self.inputs[3].fingerprint,
            invocation_authorization_identity=ia.identity,invocation_authorization_fingerprint=ia.fingerprint,
            invocation_evidence_fingerprint=invoked.fingerprint.digest,artifact_identity=audit["id"],
            artifact_sha256=hashlib.sha256(invoked.artifact_bytes).hexdigest(),artifact_filename="brief.html",artifact_media_type="text/html",
            artifact_byte_length=len(invoked.artifact_bytes),successor_projection_fingerprint=self.projection.fingerprint,
            translated_projection_fingerprint=adapt_terminal_projection(self.projection).fingerprint,adapter_identity=self.projection.adapter_identity,
            adapter_version=self.projection.adapter_version,adapter_implementation_digest=adapter_source_digest(),
            renderer_identity=self.projection.renderer_identity,renderer_version=self.projection.renderer_version,
            renderer_implementation_digest=representative_renderer_implementation_digest(),maximum_artifact_bytes=1_000_000,
            output_class="standalone-terminal-representative-static-html-semantic-realization",
            exclusions=("manifest-authority","distribution-authority","delivery-authority","deployment-authority",
                "technical-publication-authority","successful-publication-authority","external-assets","active-content"),
            artifact_destination=str(invoked.artifact_path),invocation_evidence_destination=str(invoked.evidence_path),
            evidence_directory=str(directory.resolve()),evidence_filename="terminal-semantic-conformance-evidence.json",
            commitment_ledger_directory=ia.authorization_ledger_directory,record_identity="terminal-semantic-conformance:focused")
        values.update(changes); provisional=TerminalSemanticArtifactConformanceAuthorization(**values,fingerprint="")
        return replace(provisional,fingerprint=compute_terminal_conformance_authorization_fingerprint(provisional))

    def assess(self,ia,invoked,ca):
        return assess_terminal_semantic_artifact_conformance(artifact_path=invoked.artifact_path,
            invocation_evidence_path=invoked.evidence_path,evidence_snapshot=self.inputs[0],verified_release=self.inputs[1],
            lifecycle_scope=self.inputs[2],declaration=self.inputs[3],planning_authorization=self.inputs[4],verified_plan=self.inputs[5],
            authority_profile=self.profile,invocation_authorization=ia,authorization=ca,projection=self.projection)

    def test_deterministic_real_invocation_binds_both_projections_adapter_renderer_and_reloads(self):
        a=self.invocation_authorization(); result=self.invoke(a)
        self.assertFalse(result.blocked,result.findings); invoked=result.verified
        payload=invoked.bundle.one("GeneratedArtifactAuditRecord").extensions[0]["payload"]
        self.assertEqual(payload["successor_projection_fingerprint"],self.projection.fingerprint)
        self.assertEqual(payload["translated_projection_fingerprint"],adapt_terminal_projection(self.projection).fingerprint)
        self.assertEqual([x["identity"] for x in payload["operational_authority_exclusions"]],list(TERMINAL_OPERATIONAL_IDENTITIES))
        self.assertTrue(all(x["planned_count"]==x["realized_count"]==0 for x in payload["operational_authority_exclusions"]))
        loaded=verify_persisted_terminal_renderer_invocation(artifact_path=invoked.artifact_path,evidence_path=invoked.evidence_path,
            verified_release=self.inputs[1],evidence_snapshot=self.inputs[0],lifecycle_scope=self.inputs[2],declaration=self.inputs[3],
            planning_authorization=self.inputs[4],verified_plan=self.inputs[5],authority_profile=self.profile,authorization=a)
        self.assertEqual(loaded.fingerprint,invoked.fingerprint)

    def test_stale_mixed_adapter_substitution_and_active_renderer_drift_rejected(self):
        attacks=(dict(successor_projection_fingerprint="0"*64),dict(translated_projection_fingerprint="1"*64),
                 dict(adapter_identity="adapter:substitute"),dict(adapter_implementation_digest="2"*64),
                 dict(renderer_implementation_digest="3"*64))
        for attack in attacks:
            with self.subTest(attack=attack): self.assertTrue(self.invoke(self.invocation_authorization(**attack)).blocked)
        with patch("briefforge_terminal_profile.controlled_invocation.representative_renderer_implementation_digest",return_value="4"*64):
            self.assertTrue(self.invoke(self.invocation_authorization(renderer_implementation_digest="5"*64)).blocked)

    def test_artifact_evidence_tamper_and_direct_successor_routing_are_rejected(self):
        from briefforge.representative_renderer import render_representative_html
        with self.assertRaises(Exception): render_representative_html(self.projection)
        for target in ("artifact","evidence"):
            a=self.invocation_authorization(); invoked=self.invoke(a).verified
            path=invoked.artifact_path if target=="artifact" else invoked.evidence_path
            path.write_bytes(path.read_bytes()+b"x")
            with self.assertRaises(Exception):
                verify_persisted_terminal_renderer_invocation(artifact_path=invoked.artifact_path,evidence_path=invoked.evidence_path,
                    verified_release=self.inputs[1],evidence_snapshot=self.inputs[0],lifecycle_scope=self.inputs[2],declaration=self.inputs[3],
                    planning_authorization=self.inputs[4],verified_plan=self.inputs[5],authority_profile=self.profile,authorization=a)

    def test_independent_parser_rejects_visible_and_marker_operational_leakage(self):
        a=self.invocation_authorization(); artifact=self.invoke(a).verified.artifact_bytes
        verify_exact_terminal_html(artifact,self.projection)
        attacks=(artifact.replace(b"</main>",TERMINAL_OPERATIONAL_IDENTITIES[0].encode()+b"</main>",1),
            artifact.replace(b"</main>",b'<span data-semantic-key="field:leak:id" data-semantic-role="field">"authority:briefforge-controlled-local-delivery"</span></main>',1))
        for attack in attacks:
            with self.assertRaises(Exception): verify_exact_terminal_html(attack,self.projection)

    def test_conformance_reconstructs_truth_accounts_eight_and_persists_independently(self):
        ia=self.invocation_authorization(); invoked=self.invoke(ia).verified; ca=self.conform_authorization(ia,invoked)
        result=self.assess(ia,invoked,ca); self.assertFalse(result.blocked,result.findings)
        entries=result.verified.evidence["requirement_accounting"]["element_entries"]
        excluded=[x for x in entries if x["projection_rule"]=="operational-authority-exclusion"]
        self.assertEqual(len(excluded),8); self.assertTrue(all(x["planned_count"]==x["realized_count"]==0 for x in excluded))
        loaded=verify_persisted_terminal_semantic_artifact_conformance(artifact_path=invoked.artifact_path,
            invocation_evidence_path=invoked.evidence_path,evidence_snapshot=self.inputs[0],verified_release=self.inputs[1],
            lifecycle_scope=self.inputs[2],declaration=self.inputs[3],planning_authorization=self.inputs[4],verified_plan=self.inputs[5],
            authority_profile=self.profile,invocation_authorization=ia,authorization=ca,projection=self.projection)
        self.assertEqual(loaded.fingerprint,result.verified.fingerprint)
        path=Path(ca.evidence_directory)/ca.evidence_filename; path.write_bytes(path.read_bytes()+b"x")
        with self.assertRaises(Exception):
            verify_persisted_terminal_semantic_artifact_conformance(artifact_path=invoked.artifact_path,
                invocation_evidence_path=invoked.evidence_path,evidence_snapshot=self.inputs[0],verified_release=self.inputs[1],
                lifecycle_scope=self.inputs[2],declaration=self.inputs[3],planning_authorization=self.inputs[4],verified_plan=self.inputs[5],
                authority_profile=self.profile,invocation_authorization=ia,authorization=ca,projection=self.projection)

    def test_conformance_mixed_binding_and_projection_substitution_fail(self):
        ia=self.invocation_authorization(); invoked=self.invoke(ia).verified
        ca=self.conform_authorization(ia,invoked,translated_projection_fingerprint="0"*64)
        self.assertTrue(self.assess(ia,invoked,ca).blocked)
        forged=replace(self.projection,fingerprint="f"*64)
        valid=self.conform_authorization(ia,invoked)
        result=assess_terminal_semantic_artifact_conformance(artifact_path=invoked.artifact_path,invocation_evidence_path=invoked.evidence_path,
            evidence_snapshot=self.inputs[0],verified_release=self.inputs[1],lifecycle_scope=self.inputs[2],declaration=self.inputs[3],
            planning_authorization=self.inputs[4],verified_plan=self.inputs[5],authority_profile=self.profile,
            invocation_authorization=ia,authorization=valid,projection=forged)
        self.assertTrue(result.blocked)


if __name__=="__main__": unittest.main()
