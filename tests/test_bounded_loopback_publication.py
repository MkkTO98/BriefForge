"""TASK-056 bounded loopback deployment and separately authorized verification."""
from __future__ import annotations

from dataclasses import asdict, fields, replace
import ast
import hashlib
import inspect
import json
import os
from pathlib import Path
import socket
import tempfile
import threading
import unittest
from unittest.mock import patch

from briefforge.bcrp.model import BCRPBundle, BCRPRecord, RECORD_KINDS
from briefforge.bounded_loopback_deployment import (
    DeploymentTarget, DeploymentRouteItem, LoopbackDeploymentAuthorization,
    LoopbackDeploymentEvidence, LoopbackDeploymentResult, VerifiedLoopbackDeployment,
    compute_deployment_authorization_fingerprint, issue_loopback_deployment_authorization,
    start_bounded_loopback_deployment, stop_bounded_loopback_deployment,
    verify_persisted_loopback_deployment, verify_deployment_current_availability,
    verify_persisted_deployment_stop, reconcile_loopback_deployment_commitment, parse_bounded_request,
    load_persisted_loopback_deployment,
    _released_loopback_deployment_scope, validate_bounded_route_mechanics,
)
from briefforge.technical_publication_verification import (
    TechnicalVerificationAuthorization, TechnicalPublicationEvidence,
    TechnicalVerificationResult, VerifiedTechnicalPublication,
    compute_verification_authorization_fingerprint,
    issue_technical_verification_authorization, verify_technical_publication,
    verify_persisted_technical_publication, verify_technical_publication_current_availability,
    reconcile_technical_observation_commitment, _released_technical_verification_scope,
    verify_technical_publication_and_shutdown, load_persisted_technical_publication,
)
from briefforge.publication_distribution_delivery import (
    ControlledLocalDeliveryAuthorization, ControlledLocalDestination, DeliveryInventoryItem,
    compute_delivery_authorization_fingerprint, compute_delivery_inventory_fingerprint,
    issue_controlled_local_delivery_authorization, perform_controlled_local_delivery,
)
import briefforge.bounded_loopback_deployment as deployment_module
import briefforge.technical_publication_verification as verification_module
import briefforge.publication_distribution_delivery as delivery_module
from tests import test_publication_manifest_admission as manifest_tests


class BoundedLoopbackPublicationTests(unittest.TestCase):
    setUp = manifest_tests.PublicationManifestAdmissionTests.setUp
    _ledger_directory = manifest_tests.PublicationManifestAdmissionTests._ledger_directory
    _inputs = manifest_tests.PublicationManifestAdmissionTests._inputs
    _authorization = manifest_tests.PublicationManifestAdmissionTests._authorization
    _invoke = manifest_tests.PublicationManifestAdmissionTests._invoke
    _conformance_authorization = manifest_tests.PublicationManifestAdmissionTests._conformance_authorization
    _real_predecessor = manifest_tests.PublicationManifestAdmissionTests._real_predecessor
    _admission = manifest_tests.PublicationManifestAdmissionTests._admission
    _manifest_authorization = manifest_tests.PublicationManifestAdmissionTests._manifest_authorization
    _manifest_call = manifest_tests.PublicationManifestAdmissionTests._call

    def _candidate(self, snapshot):
        base = manifest_tests.PublicationManifestAdmissionTests._candidate(self, snapshot)
        records=[]
        for record in base.records:
            doc=record.to_document()
            if record.kind == "PortablePresentationMaterialRecord":
                doc["semantic"]["authorities"].extend((
                    {"id":"authority:briefforge-controlled-local-delivery","owner_identity":"project:BriefForge","role":"controlled-local-delivery-authority","scope":delivery_module._released_destination_scope(self.dp,"task056-delivery",self.dl)},
                    {"id":"authority:briefforge-bounded-loopback-deployment","owner_identity":"project:BriefForge","role":"bounded-loopback-deployment-authority","scope":_released_loopback_deployment_scope(self.target,self.routes,self.xl)},
                    {"id":"authority:briefforge-technical-publication-verifier","owner_identity":"project:BriefForge","role":"technical-publication-verification-authority","scope":_released_technical_verification_scope(self.target,self.routes,self.vl)},
                ))
            records.append(BCRPRecord.from_document(doc))
        return BCRPBundle(base.profile_identity,base.profile_version,tuple(records))

    def _case(self, root):
        self.dp=root/"delivery-parent"; self.dl=root/"delivery-ledger"; self.xl=root/"deployment-ledger"; self.vl=root/"verification-ledger"
        for p in (self.dp,self.dl,self.xl,self.vl): p.mkdir(mode=0o700); p.chmod(0o700)
        probe=socket.socket(socket.AF_INET,socket.SOCK_STREAM); probe.bind(("127.0.0.1",0)); port=probe.getsockname()[1]; probe.close()
        self.target=DeploymentTarget("127.0.0.1",port,f"http://127.0.0.1:{port}")
        self.routes=(DeploymentRouteItem("/publication.html","publication.html","text/html"),)
        predecessor=self._real_predecessor(root)
        md=root/"manifest"; md.mkdir(); ma=self._manifest_authorization(predecessor,md); manifest=self._manifest_call(predecessor,ma)
        item=ma.artifact_inventory[0]
        inv=(DeliveryInventoryItem(item.identity,item.role,item.logical_filename,item.media_type,item.byte_length,item.sha256,item.order),)
        di=os.stat(self.dp); li=os.stat(self.dl)
        da=ControlledLocalDeliveryAuthorization(
            "delivery-auth:056","briefforge-controlled-local-delivery-policy:1.0.0","briefforge-controlled-local-directory-delivery-profile:1.0.0","1.0.0",
            "authority:briefforge-controlled-local-delivery","project:BriefForge","controlled-local-delivery-authority",
            "2026-07-31T12:02:00Z","2026-07-31T12:03:00Z","2026-07-31T12:04:00Z",ma.fingerprint,manifest.verified.fingerprint.digest,
            ma.manifest_identity,ma.record_identity,ma.release_identity,ma.release_fingerprint,predecessor[0][2].inventory_digest,ma.artifact_set_fingerprint,
            inv,compute_delivery_inventory_fingerprint(inv),ControlledLocalDestination(str(self.dp.resolve()),"task056-delivery",di.st_dev,di.st_ino),
            "delivery-attempt:056","delivery-evidence:056","controlled-local-delivery-evidence.json","briefforge.publication_distribution_delivery","1.0.0",
            str(self.dl.resolve()),li.st_dev,li.st_ino,("network-distribution","remote-receipt","deployment-authority","hosting-authority","successful-publication-authority","public-reachability","browser-behavior-certification","reader-access-certification","accessibility-certification","editorial-certification","visual-certification","factual-reassessment","atlasforge-authority"),
            delivery_module._released_destination_scope(self.dp,"task056-delivery",self.dl),"")
        da=replace(da,fingerprint=compute_delivery_authorization_fingerprint(da))
        inputs,invocation,conformance,_=predecessor
        upstream=dict(manifest_evidence_path=Path(ma.evidence_directory)/ma.evidence_filename,manifest_authorization=ma,evidence_snapshot=inputs[0],verified_release=inputs[1],lifecycle_scope=inputs[2],declaration=inputs[3],planning_authorization=inputs[4],verified_plan=inputs[5],invocation_authorization=invocation,conformance_authorization=conformance,artifact_paths=(Path(invocation.output_directory)/invocation.output_filename,))
        dm=issue_controlled_local_delivery_authorization(**upstream,authorization=da)
        delivered=perform_controlled_local_delivery(**upstream,authorization=dm)
        self.assertEqual(delivered.state,"completed")
        return predecessor,upstream,dm,delivered.verified

    def _deployment_auth(self, case, **changes):
        predecessor,upstream,dm,dv=case; e=dv.evidence; li=os.stat(self.xl)
        values=dict(identity="deploy-auth:056",policy_identity="briefforge-bounded-loopback-deployment-policy:1.0.0",profile_identity="briefforge-bounded-loopback-static-http-profile:1.0.0",profile_version="1.0.0",authority_identity="authority:briefforge-bounded-loopback-deployment",authority_owner="project:BriefForge",authority_role="bounded-loopback-deployment-authority",authorization_time="2026-07-31T12:05:00Z",attempt_time="2026-07-31T12:06:00Z",completion_time="2026-07-31T12:07:00Z",delivery_fingerprint=dv.fingerprint,release_identity=e.release_identity,release_fingerprint=e.release_fingerprint,lifecycle_inventory_digest=e.lifecycle_inventory_digest,target=self.target,routes=self.routes,attempt_identity="deploy-attempt:056",evidence_identity="deploy-evidence:056",implementation_identity="briefforge.bounded_loopback_deployment",implementation_version="1.0.0",ledger_directory=str(self.xl.resolve()),ledger_device=li.st_dev,ledger_inode=li.st_ino,request_budget=4,time_budget_seconds=10,exclusions=("public-internet","continuing-availability","browser","javascript","accessibility","reader","editorial","production","atlasforge-authority","hostile-process-authentication"),released_authority_scope=_released_loopback_deployment_scope(self.target,self.routes,self.xl))
        values.update(changes); a=LoopbackDeploymentAuthorization(**values,fingerprint=""); return replace(a,fingerprint=compute_deployment_authorization_fingerprint(a))

    def _start(self, case, auth=None):
        auth=auth or self._deployment_auth(case); chain=self._lifecycle_chain(case)
        marker=issue_loopback_deployment_authorization(delivery_arguments=case[1],delivery_authorization=case[2],authorization=auth,**chain)
        return auth,marker,start_bounded_loopback_deployment(delivery_arguments=case[1],delivery_authorization=case[2],authorization=marker,**chain)

    def _lifecycle_chain(self, case, *, current=None):
        historical=case[1]["lifecycle_scope"]
        return dict(historical_lifecycle_scope=historical,
                    current_lifecycle_scope=historical if current is None else current)

    def _deployment_chain(self, case, marker, deployment=None):
        result=dict(delivery_arguments=case[1],delivery_authorization=case[2],
                    authorization=marker,**self._lifecycle_chain(case))
        if deployment is not None: result["running"]=deployment.service
        return result

    def _verification_chain(self, case, deployment, deployment_marker):
        return dict(delivery_arguments=case[1],delivery_authorization=case[2],
                    running=deployment.service,deployment_authorization=deployment_marker,
                    historical_lifecycle_scope=case[1]["lifecycle_scope"],
                    current_lifecycle_scope=case[1]["lifecycle_scope"])

    def _verification_auth(self, deployment, **changes):
        li=os.stat(self.vl); e=deployment.verified.evidence
        values=dict(identity="verify-auth:056",policy_identity="briefforge-technical-publication-verification-policy:1.0.0",profile_identity="briefforge-raw-http-technical-publication-profile:1.0.0",profile_version="1.0.0",authority_identity="authority:briefforge-technical-publication-verifier",authority_owner="project:BriefForge",authority_role="technical-publication-verification-authority",authorization_time="2026-07-31T12:08:00Z",attempt_time="2026-07-31T12:09:00Z",completion_time="2026-07-31T12:10:00Z",deployment_fingerprint=deployment.verified.fingerprint,service_instance_identity=e.service_instance_identity,service_token_digest=e.service_token_digest,target=self.target,routes=self.routes,attempt_identity="verify-attempt:056",evidence_identity="verification-evidence:056",implementation_identity="briefforge.technical_publication_verification",implementation_version="1.0.0",ledger_directory=str(self.vl.resolve()),ledger_device=li.st_dev,ledger_inode=li.st_ino,exclusions=("public-internet","continuing-availability","browser","javascript","accessibility","reader","editorial","production","atlasforge-authority","hostile-process-authentication"),released_authority_scope=_released_technical_verification_scope(self.target,self.routes,self.vl))
        values.update(changes); a=TechnicalVerificationAuthorization(**values,fingerprint=""); return replace(a,fingerprint=compute_verification_authorization_fingerprint(a))

    @staticmethod
    def _byte_inventory(directory):
        return tuple((path.name,path.read_bytes()) for path in sorted(directory.iterdir()))

    def test_real_chain_actual_http_exact_bytes_and_historical_reload(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); da,dm,deployment=self._start(case); self.assertEqual(deployment.state,"active")
            chain=self._verification_chain(case,deployment,dm); va=self._verification_auth(deployment); vm=issue_technical_verification_authorization(deployment=deployment.verified,authorization=va,**chain)
            result=verify_technical_publication(deployment=deployment.verified,authorization=vm,**chain)
            self.assertEqual(result.state,"bounded-observation-succeeded"); self.assertIsInstance(result.verified,VerifiedTechnicalPublication)
            self.assertEqual(result.verified.evidence.observations[0].body_sha256,case[3].evidence.inventory[0].sha256)
            persisted_chain={k:v for k,v in chain.items() if k!="running"}
            reloaded=verify_persisted_technical_publication(deployment=deployment.verified,authorization=vm,verified=result.verified,**persisted_chain)
            self.assertEqual(reloaded.fingerprint,result.verified.fingerprint)
            self.assertEqual(verify_technical_publication_current_availability(
                reloaded,deployment=deployment.verified,authorization=vm,**chain).state,
                "current-availability-established")
            stopped=stop_bounded_loopback_deployment(deployment,**self._deployment_chain(case,dm)); self.assertEqual(stopped.state,"shutdown-verified")
            self.assertEqual(verify_technical_publication_current_availability(reloaded,deployment=deployment.verified,authorization=vm,**chain).state,"not-established")

    def test_exact_response_headers_and_service_identity(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); _,dm,d=self._start(case)
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.settimeout(2); s.connect((self.target.address,self.target.port)); s.sendall(f"GET /publication.html HTTP/1.1\r\nHost: 127.0.0.1:{self.target.port}\r\n\r\n".encode()); raw=b""
            while True:
                part=s.recv(65536)
                if not part: break
                raw+=part
            s.close(); head,body=raw.split(b"\r\n\r\n",1)
            self.assertEqual(head.split(b"\r\n")[:3],[b"HTTP/1.1 200 OK",b"Content-Type: text/html",f"Content-Length: {len(body)}".encode()])
            self.assertIn(b"X-BriefForge-Service-Token: ",head); self.assertNotIn(b"Date:",head); self.assertNotIn(b"Server:",head)
            stop_bounded_loopback_deployment(d,**self._deployment_chain(case,dm))

    def test_replay_consumption_and_bind_collision_fail_closed(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); auth=self._deployment_auth(case); lifecycle=self._lifecycle_chain(case)
            marker=issue_loopback_deployment_authorization(delivery_arguments=case[1],delivery_authorization=case[2],authorization=auth,**lifecycle)
            blocker=socket.socket(socket.AF_INET,socket.SOCK_STREAM); blocker.bind((self.target.address,self.target.port)); blocker.listen(1)
            failed=start_bounded_loopback_deployment(delivery_arguments=case[1],delivery_authorization=case[2],authorization=marker,**lifecycle); blocker.close()
            self.assertEqual(failed.state,"deployment-failed-consumed-service-rollback-verified")
            replay=start_bounded_loopback_deployment(delivery_arguments=case[1],delivery_authorization=case[2],authorization=marker,**lifecycle)
            self.assertIn("deployment-authorization-consumed",{x.code for x in replay.findings})

    def test_authority_separation_and_caller_dataclass_cannot_execute(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); auth=self._deployment_auth(case)
            result=start_bounded_loopback_deployment(delivery_arguments=case[1],delivery_authorization=case[2],authorization=auth,**self._lifecycle_chain(case))
            self.assertTrue(result.blocked)
            self.assertNotEqual(auth.authority_identity,"authority:briefforge-technical-publication-verifier")

    def test_service_substitution_wrong_instance_fails_verification(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); _,dm,d=self._start(case); chain=self._verification_chain(case,d,dm); va=self._verification_auth(d); vm=issue_technical_verification_authorization(deployment=d.verified,authorization=va,**chain)
            stop_bounded_loopback_deployment(d,**self._deployment_chain(case,dm))
            self.assertTrue(verify_technical_publication(deployment=d.verified,authorization=vm,**chain).blocked)

    def test_deployment_evidence_tamper_detected(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); _,dm,d=self._start(case); p=Path(d.verified.evidence.evidence_path); p.write_bytes(p.read_bytes()+b" ")
            with self.assertRaises(ValueError): verify_persisted_loopback_deployment(d.verified,**self._deployment_chain(case,dm))
            stop_bounded_loopback_deployment(d,**self._deployment_chain(case,dm))

    def test_current_availability_true_only_while_exact_listener_active(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); _,dm,d=self._start(case); current=self._deployment_chain(case,dm,d)
            self.assertEqual(verify_deployment_current_availability(d.verified,**current).state,"current-availability-established")
            stop_bounded_loopback_deployment(d,**self._deployment_chain(case,dm))
            self.assertEqual(verify_deployment_current_availability(d.verified,**current).state,"not-established")

    def test_deployment_commitment_failure_is_reconcilable_historical_truth(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); auth=self._deployment_auth(case)
            lifecycle=self._lifecycle_chain(case)
            marker=issue_loopback_deployment_authorization(delivery_arguments=case[1],delivery_authorization=case[2],authorization=auth,**lifecycle)
            original=deployment_module._write_exclusive
            def fail_commitment(directory,name,data):
                if name.endswith("deployment-evidence.commitment"): raise OSError("injected")
                return original(directory,name,data)
            with patch.object(deployment_module,"_write_exclusive",side_effect=fail_commitment):
                pending=start_bounded_loopback_deployment(delivery_arguments=case[1],delivery_authorization=case[2],authorization=marker,**lifecycle)
            self.assertEqual(pending.state,"completion-pending")
            self.assertIsNotNone(pending.verified); self.assertIsNone(pending.service)
            reconciled=reconcile_loopback_deployment_commitment(
                authorization_evidence_path=self.xl/marker.issuance_filename,
                deployment_evidence_path=pending.verified.evidence.evidence_path,
                delivery_arguments=case[1],delivery_authorization=case[2],**lifecycle)
            self.assertEqual(reconciled.state,"historical-deployment-observed")
            probe=socket.socket(); self.assertNotEqual(probe.connect_ex((self.target.address,self.target.port)),0); probe.close()

    def test_deployment_reconciliation_prevalidates_before_missing_commitment_write(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); auth=self._deployment_auth(case); lifecycle=self._lifecycle_chain(case)
            marker=issue_loopback_deployment_authorization(delivery_arguments=case[1],delivery_authorization=case[2],authorization=auth,**lifecycle)
            original=deployment_module._write_exclusive
            def fail_commitment(directory,name,data):
                if name.endswith("deployment-evidence.commitment"): raise OSError("injected")
                return original(directory,name,data)
            with patch.object(deployment_module,"_write_exclusive",side_effect=fail_commitment):
                pending=start_bounded_loopback_deployment(delivery_arguments=case[1],delivery_authorization=case[2],authorization=marker,**lifecycle)
            ep=Path(pending.verified.evidence.evidence_path); doc=json.loads(ep.read_bytes())
            doc["outcome"]="forged"; doc["fingerprint"]=""
            forged=deployment_module._evidence(doc); doc["fingerprint"]=deployment_module.compute_deployment_evidence_fingerprint(forged); ep.write_bytes(deployment_module._canonical(doc))
            result=reconcile_loopback_deployment_commitment(authorization_evidence_path=self.xl/marker.issuance_filename,
                deployment_evidence_path=ep,delivery_arguments=case[1],delivery_authorization=case[2],**lifecycle)
            self.assertTrue(result.blocked)
            self.assertFalse(Path(pending.verified.evidence.commitment_path).exists())

    def test_technical_reconciliation_prevalidates_before_missing_commitment_write(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); _,dm,d=self._start(case); chain=self._verification_chain(case,d,dm)
            va=self._verification_auth(d); vm=issue_technical_verification_authorization(deployment=d.verified,authorization=va,**chain)
            original=verification_module._write_exclusive
            def fail_commitment(directory,name,data):
                if name.endswith("technical-observation-evidence.commitment"): raise OSError("injected")
                return original(directory,name,data)
            with patch.object(verification_module,"_write_exclusive",side_effect=fail_commitment):
                pending=verify_technical_publication(deployment=d.verified,authorization=vm,**chain)
            ep=Path(pending.verified.evidence.evidence_path); doc=json.loads(ep.read_bytes())
            doc["outcome"]="forged"; doc["fingerprint"]=""
            forged=verification_module._evidence(doc); doc["fingerprint"]=verification_module.compute_technical_publication_evidence_fingerprint(forged); ep.write_bytes(verification_module._canonical(doc))
            lifecycle=self._lifecycle_chain(case)
            result=reconcile_technical_observation_commitment(
                deployment_authorization_evidence_path=self.xl/dm.issuance_filename,
                deployment_evidence_path=d.verified.evidence.evidence_path,
                verification_authorization_evidence_path=self.vl/vm.issuance_filename,
                verification_evidence_path=ep,delivery_arguments=case[1],delivery_authorization=case[2],**lifecycle)
            self.assertTrue(result.blocked)
            self.assertFalse(Path(pending.verified.evidence.commitment_path).exists())
            stop_bounded_loopback_deployment(d,**self._deployment_chain(case,dm))

    def test_fixed_coordinator_always_shuts_down_service(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); _,dm,d=self._start(case); chain=self._verification_chain(case,d,dm)
            va=self._verification_auth(d); vm=issue_technical_verification_authorization(deployment=d.verified,authorization=va,**chain)
            coordinated=verify_technical_publication_and_shutdown(deployment_result=d,authorization=vm,**chain)
            self.assertEqual(coordinated.verification.state,"bounded-observation-succeeded")
            self.assertEqual(coordinated.shutdown.state,"shutdown-verified")
            self.assertFalse(any(x.name=="briefforge-bounded-loopback" and x.is_alive() for x in threading.enumerate()))

    def test_technical_lifecycle_is_replayed_before_request_and_drift_writes_no_success(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); _,dm,d=self._start(case); chain=self._verification_chain(case,d,dm)
            va=self._verification_auth(d); vm=issue_technical_verification_authorization(deployment=d.verified,authorization=va,**chain)
            real=verification_module._reload_deployment_chain; calls=0
            def mutate(*args,**kwargs):
                nonlocal calls
                calls+=1
                if calls==1: return real(*args,**kwargs)
                raise ValueError("current lifecycle drift")
            with patch.object(verification_module,"_reload_deployment_chain",side_effect=mutate):
                coordinated=verify_technical_publication_and_shutdown(deployment_result=d,authorization=vm,**chain)
            self.assertIn("technical-lifecycle-drift",{x.code for x in coordinated.verification.findings})
            self.assertEqual(coordinated.shutdown.state,"shutdown-verified")
            self.assertFalse(any(self.vl.glob("*.technical-observation-evidence.json")))
            self.assertFalse(any(self.vl.glob("*.technical-observation-evidence.commitment")))

    def test_final_post_response_lifecycle_drift_is_consumed_without_success_residue(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); _,dm,d=self._start(case); chain=self._verification_chain(case,d,dm)
            va=self._verification_auth(d); vm=issue_technical_verification_authorization(
                deployment=d.verified,authorization=va,**chain)
            real_reload=verification_module._reload_deployment_chain
            real_observe=verification_module._raw_observe
            reload_calls=0; response_completed=False
            def reload_until_final_gate(*args,**kwargs):
                nonlocal reload_calls
                reload_calls+=1
                if reload_calls==3:
                    self.assertTrue(response_completed)
                    raise ValueError("injected final current-chain drift")
                return real_reload(*args,**kwargs)
            def observe_response(*args,**kwargs):
                nonlocal response_completed
                observed=real_observe(*args,**kwargs)
                response_completed=True
                return observed
            with patch.object(verification_module,"_reload_deployment_chain",side_effect=reload_until_final_gate), \
                 patch.object(verification_module,"_raw_observe",side_effect=observe_response):
                coordinated=verify_technical_publication_and_shutdown(
                    deployment_result=d,authorization=vm,**chain)
            self.assertTrue(response_completed)
            self.assertEqual(reload_calls,3)
            self.assertEqual(coordinated.verification.state,
                             "deployment-completed-verification-failed-consumed-lifecycle-drift")
            self.assertEqual([x.code for x in coordinated.verification.findings],["technical-lifecycle-drift"])
            self.assertIsNone(coordinated.verification.verified)
            self.assertFalse(any(self.vl.glob("*.technical-observation-evidence.json")))
            self.assertFalse(any(self.vl.glob("*.technical-observation-evidence.commitment")))
            independently_loaded=load_persisted_loopback_deployment(
                authorization_evidence_path=self.xl/dm.issuance_filename,
                deployment_evidence_path=d.verified.evidence.evidence_path,
                delivery_arguments=case[1],delivery_authorization=case[2],**self._lifecycle_chain(case))
            self.assertEqual(independently_loaded.fingerprint,d.verified.fingerprint)
            self.assertEqual(coordinated.shutdown.state,"shutdown-verified")
            self.assertFalse(any(x.name=="briefforge-bounded-loopback" and x.is_alive()
                                 for x in threading.enumerate()))
            probe=socket.socket(); self.assertNotEqual(
                probe.connect_ex((self.target.address,self.target.port)),0); probe.close()

    def test_reconciliation_malformed_complete_upstream_never_changes_ledgers(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); lifecycle=self._lifecycle_chain(case)
            malformed_arguments={**case[1],"artifact_paths":(Path(t)/"wrong-publication.html",)}
            auth=self._deployment_auth(case)
            dm=issue_loopback_deployment_authorization(
                delivery_arguments=case[1],delivery_authorization=case[2],authorization=auth,**lifecycle)
            deployment_write=deployment_module._write_exclusive
            def fail_deployment_commitment(directory,name,data):
                if name.endswith("deployment-evidence.commitment"): raise OSError("injected")
                return deployment_write(directory,name,data)
            with patch.object(deployment_module,"_write_exclusive",side_effect=fail_deployment_commitment):
                pending=start_bounded_loopback_deployment(
                    delivery_arguments=case[1],delivery_authorization=case[2],authorization=dm,**lifecycle)
            self.assertEqual(pending.state,"completion-pending")
            deployment_before=self._byte_inventory(self.xl)
            blocked=reconcile_loopback_deployment_commitment(
                authorization_evidence_path=self.xl/dm.issuance_filename,
                deployment_evidence_path=pending.verified.evidence.evidence_path,
                delivery_arguments=malformed_arguments,delivery_authorization=case[2],**lifecycle)
            self.assertEqual([x.code for x in blocked.findings],["reconciliation-blocked"])
            self.assertEqual(self._byte_inventory(self.xl),deployment_before)
            self.assertFalse(Path(pending.verified.evidence.commitment_path).exists())

            auth2=self._deployment_auth(case,identity="deploy-auth:056-technical",
                                        attempt_identity="deploy-attempt:056-technical",
                                        evidence_identity="deploy-evidence:056-technical")
            dm2=issue_loopback_deployment_authorization(
                delivery_arguments=case[1],delivery_authorization=case[2],authorization=auth2,**lifecycle)
            d2=start_bounded_loopback_deployment(
                delivery_arguments=case[1],delivery_authorization=case[2],authorization=dm2,**lifecycle)
            chain=self._verification_chain(case,d2,dm2); va=self._verification_auth(d2)
            vm=issue_technical_verification_authorization(deployment=d2.verified,authorization=va,**chain)
            technical_write=verification_module._write_exclusive
            def fail_technical_commitment(directory,name,data):
                if name.endswith("technical-observation-evidence.commitment"): raise OSError("injected")
                return technical_write(directory,name,data)
            with patch.object(verification_module,"_write_exclusive",side_effect=fail_technical_commitment):
                technical_pending=verify_technical_publication(
                    deployment=d2.verified,authorization=vm,**chain)
            self.assertEqual(technical_pending.state,"completion-pending")
            technical_before=self._byte_inventory(self.vl)
            blocked=reconcile_technical_observation_commitment(
                deployment_authorization_evidence_path=self.xl/dm2.issuance_filename,
                deployment_evidence_path=d2.verified.evidence.evidence_path,
                verification_authorization_evidence_path=self.vl/vm.issuance_filename,
                verification_evidence_path=technical_pending.verified.evidence.evidence_path,
                delivery_arguments=malformed_arguments,delivery_authorization=case[2],**lifecycle)
            self.assertEqual([x.code for x in blocked.findings],["technical-reconciliation-blocked"])
            self.assertEqual(self._byte_inventory(self.vl),technical_before)
            self.assertFalse(Path(technical_pending.verified.evidence.commitment_path).exists())
            stop_bounded_loopback_deployment(d2,**self._deployment_chain(case,dm2))

    def test_restart_loader_independently_recomputes_rewritten_service_identity(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); _,dm,d=self._start(case)
            evidence_path=Path(d.verified.evidence.evidence_path)
            commitment_path=Path(d.verified.evidence.commitment_path)
            stop_bounded_loopback_deployment(d,**self._deployment_chain(case,dm))
            del d  # exercise the path-only public restart loader, not a process marker
            document=json.loads(evidence_path.read_bytes())
            document["service_instance_identity"]="service-instance:coordinated-forgery"
            unsigned={key:value for key,value in document.items() if key!="fingerprint"}
            canonical=lambda value: json.dumps(
                value,sort_keys=True,separators=(",",":"),ensure_ascii=False,
                allow_nan=False).encode()
            document["fingerprint"]=hashlib.sha256(canonical(unsigned)).hexdigest()
            evidence_bytes=canonical(document); evidence_path.write_bytes(evidence_bytes)
            commitment_path.write_bytes(canonical({
                "evidence_sha256":hashlib.sha256(evidence_bytes).hexdigest(),
                "fingerprint":document["fingerprint"],
                "service_instance_identity":document["service_instance_identity"],
                "service_token_digest":document["service_token_digest"],
            }))
            with self.assertRaisesRegex(
                    ValueError,"deployment evidence differs from independent reproduction"):
                load_persisted_loopback_deployment(
                    authorization_evidence_path=self.xl/dm.issuance_filename,
                    deployment_evidence_path=evidence_path,delivery_arguments=case[1],
                    delivery_authorization=case[2],**self._lifecycle_chain(case))

    def test_restart_loaders_need_no_task056_process_local_markers(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); _,dm,d=self._start(case); chain=self._verification_chain(case,d,dm)
            va=self._verification_auth(d); vm=issue_technical_verification_authorization(deployment=d.verified,authorization=va,**chain)
            result=verify_technical_publication(deployment=d.verified,authorization=vm,**chain)
            lifecycle=self._lifecycle_chain(case)
            deployment=load_persisted_loopback_deployment(
                authorization_evidence_path=self.xl/dm.issuance_filename,
                deployment_evidence_path=d.verified.evidence.evidence_path,
                delivery_arguments=case[1],delivery_authorization=case[2],**lifecycle)
            technical=load_persisted_technical_publication(
                deployment_authorization_evidence_path=self.xl/dm.issuance_filename,
                deployment_evidence_path=d.verified.evidence.evidence_path,
                verification_authorization_evidence_path=self.vl/vm.issuance_filename,
                verification_evidence_path=result.verified.evidence.evidence_path,
                delivery_arguments=case[1],delivery_authorization=case[2],**lifecycle)
            self.assertEqual(deployment.fingerprint,d.verified.fingerprint)
            self.assertEqual(technical.fingerprint,result.verified.fingerprint)
            stop_bounded_loopback_deployment(d,**self._deployment_chain(case,dm))

    def test_forged_persisted_deployment_and_incomplete_upstream_are_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); _,dm,d=self._start(case)
            forged=object.__new__(VerifiedLoopbackDeployment)
            with self.assertRaises(ValueError):
                verify_persisted_loopback_deployment(forged,**self._deployment_chain(case,dm))
            with self.assertRaises(TypeError):
                verify_persisted_loopback_deployment(d.verified)
            stop_bounded_loopback_deployment(d,**self._deployment_chain(case,dm))

    def test_lifecycle_change_after_byte_pin_blocks_before_bind(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); auth=self._deployment_auth(case); lifecycle=self._lifecycle_chain(case)
            marker=issue_loopback_deployment_authorization(delivery_arguments=case[1],delivery_authorization=case[2],authorization=auth,**lifecycle)
            eligible=deployment_module._delivery_current(case[1],case[2],case[3],lifecycle["historical_lifecycle_scope"],lifecycle["current_lifecycle_scope"])
            blocked=type("Blocked",(),{"blocked":True})()
            with patch.object(deployment_module,"_delivery_current",side_effect=(eligible,blocked)), \
                 patch.object(deployment_module,"_load_bytes",wraps=deployment_module._load_bytes) as load:
                result=start_bounded_loopback_deployment(delivery_arguments=case[1],delivery_authorization=case[2],authorization=marker,**lifecycle)
            self.assertTrue(load.called); self.assertEqual(result.state,"deployment-failed-consumed-service-rollback-verified")
            probe=socket.socket(); self.assertNotEqual(probe.connect_ex((self.target.address,self.target.port)),0); probe.close()

    def test_copied_service_identity_without_raw_active_token_cannot_substitute(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); _,dm,d=self._start(case); chain=self._verification_chain(case,d,dm)
            va=self._verification_auth(d); vm=issue_technical_verification_authorization(deployment=d.verified,authorization=va,**chain)
            copied=object.__new__(type(d.service))
            for name in ("_listener","_thread","_stop_event","_verified","_target","_marker"):
                object.__setattr__(copied,name,getattr(d.service,name))
            object.__setattr__(copied,"_service_token",d.verified.evidence.service_token_digest)
            self.assertTrue(verify_technical_publication(deployment=d.verified,authorization=vm,**{**chain,"running":copied}).blocked)
            stop_bounded_loopback_deployment(d,**self._deployment_chain(case,dm))

    def test_exact_current_availability_requires_running_receipt(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); _,dm,d=self._start(case)
            with self.assertRaises(TypeError):
                verify_deployment_current_availability(d.verified,**self._deployment_chain(case,dm))
            stop_bounded_loopback_deployment(d,**self._deployment_chain(case,dm))

    def test_stop_evidence_reloads_and_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); _,dm,d=self._start(case); chain=self._deployment_chain(case,dm)
            stopped=stop_bounded_loopback_deployment(d,**chain); self.assertEqual(stopped.state,"shutdown-verified")
            evidence=verify_persisted_deployment_stop(deployment=d.verified,**chain)
            self.assertEqual(evidence.state,"shutdown-verified")
            path=next(self.xl.glob("*.deployment-stop-evidence.json")); path.write_bytes(path.read_bytes()+b" ")
            with self.assertRaises(ValueError): verify_persisted_deployment_stop(deployment=d.verified,**chain)

    def test_technical_authorization_sequential_replay_is_consumed(self):
        with tempfile.TemporaryDirectory() as t:
            case=self._case(Path(t)); _,dm,d=self._start(case); chain=self._verification_chain(case,d,dm)
            va=self._verification_auth(d); vm=issue_technical_verification_authorization(deployment=d.verified,authorization=va,**chain)
            first=verify_technical_publication(deployment=d.verified,authorization=vm,**chain)
            self.assertEqual(first.state,"bounded-observation-succeeded")
            replay=verify_technical_publication(deployment=d.verified,authorization=vm,**chain)
            self.assertIn("verification-authorization-consumed",{x.code for x in replay.findings})
            stop_bounded_loopback_deployment(d,**self._deployment_chain(case,dm))

    def test_records_frozen_bcrp_isolation_and_truthful_exclusions(self):
        self.assertEqual(len(RECORD_KINDS),11); self.assertEqual(DeploymentTarget.__dataclass_params__.frozen,True)
        import briefforge.bcrp.model as model
        self.assertNotIn("bounded_loopback",inspect.getsource(model)); self.assertNotIn("successful_publication",{f.name for f in fields(LoopbackDeploymentEvidence)})

    def test_forbidden_imports_and_calls(self):
        for module in (deployment_module,verification_module):
            tree=ast.parse(inspect.getsource(module)); imported={n.names[0].name.split('.')[0] if isinstance(n,ast.Import) else (n.module or '').split('.')[0] for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))}
            self.assertFalse(imported & {"subprocess","requests","urllib","http","ssl","sqlite3","importlib"})
            self.assertFalse(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in {"eval","exec","__import__"} for n in ast.walk(tree)))

    def test_verifier_does_not_import_server_private_helpers(self):
        source=inspect.getsource(verification_module)
        self.assertNotIn("from .bounded_loopback_deployment import _",source)
        self.assertNotIn("._server",source); self.assertNotIn("._thread",source)

    def test_fixed_profile_rejects_invalid_targets(self):
        with tempfile.TemporaryDirectory() as t:
            ledger=Path(t); ledger.chmod(0o700); routes=(DeploymentRouteItem("/publication.html","publication.html","text/html"),)
            for target in (DeploymentTarget("0.0.0.0",8080,"http://0.0.0.0:8080"),DeploymentTarget("localhost",8080,"http://localhost:8080"),DeploymentTarget("127.0.0.1",0,"http://127.0.0.1:0"),DeploymentTarget("127.0.0.1",65536,"http://127.0.0.1:65536")):
                with self.assertRaises(ValueError): _released_loopback_deployment_scope(target,routes,ledger)


# Pure parser vectors make ambiguity handling explicit and cheap.
_BAD_REQUESTS=(
 b"POST /publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n", b"GET /publication.html?x HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n",
 b"GET /publication.html#x HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n", b"GET /%70ublication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n",
 b"GET /a\\b HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n", b"GET /publication.html HTTP/1.0\r\nHost: 127.0.0.1:8080\r\n\r\n",
 b"GET /publication.html HTTP/1.1\r\n\r\n", b"GET /publication.html HTTP/1.1\r\nHost: wrong\r\n\r\n",
 b"GET /publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\nHost: 127.0.0.1:8080\r\n\r\n",
 b"GET /publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\nContent-Length: 0\r\n\r\n",
 b"GET /publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\nTransfer-Encoding: chunked\r\n\r\n",
 b"GET  /publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n", b"GET /publication.html  HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n",
 b"get /publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n", b"HEAD /publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n",
 b"GET //publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n", b"GET /./publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n",
 b"GET /../publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n", b"GET /publication.html/ HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n",
 b"GET /publication.html HTTP/1.1\nHost: 127.0.0.1:8080\n\n", b"\xff /publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n",
 b"GET /publication.html HTTP/1.1\r\nhost: 127.0.0.1:8080\r\n\r\n", b"GET /publication.html HTTP/1.1\r\nHost : 127.0.0.1:8080\r\n\r\n",
 b"GET /publication.html HTTP/1.1\r\nHost:127.0.0.1:8080\r\n\r\n", b"GET /publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080 \r\n\r\n",
 b"GET /publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\nConnection: keep-alive\r\n\r\n",
 b"GET /publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\nRange: bytes=0-1\r\n\r\n",
 b"GET /publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\nIf-None-Match: x\r\n\r\n",
 b"GET /publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\nAccept-Encoding: gzip\r\n\r\n",
 b"GET /publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\nX: y\r\n\r\n",
 b"GET /publication.html HTTP/2\r\nHost: 127.0.0.1:8080\r\n\r\n",
 b"OPTIONS /publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n",
 b"GET * HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n",
 b"GET publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n",
 b"GET /PUBLICATION.HTML HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n",
 b"GET /publication.html%00 HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n",
 b"GET /missing.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n",
)

def _make_parser_test(index, raw):
    def test(self):
        with self.assertRaises(ValueError): parse_bounded_request(raw,"127.0.0.1:8080",("/publication.html",))
    test.__name__=f"test_parser_rejects_vector_{index:02d}"; return test
for _i,_raw in enumerate(_BAD_REQUESTS): setattr(BoundedLoopbackPublicationTests,f"test_parser_rejects_vector_{_i:02d}",_make_parser_test(_i,_raw))

class MorePureProfileTests(unittest.TestCase):
    def test_parser_accepts_exact_request(self): self.assertEqual(parse_bounded_request(b"GET /publication.html HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n","127.0.0.1:8080",("/publication.html",)),"/publication.html")
    def test_parser_rejects_oversize(self):
        with self.assertRaises(ValueError): parse_bounded_request(b"G"*9000,"127.0.0.1:8080",("/publication.html",))
    def test_route_records_are_specialized(self): self.assertEqual({f.name for f in fields(DeploymentRouteItem)},{"path","logical_filename","media_type"})
    def test_result_truth_states_are_not_public_claims(self): self.assertNotIn("published",{"active","rollback-verified","rollback-indeterminate","shutdown-verified","shutdown-indeterminate","bounded-observation-succeeded"})
    def test_origins_are_numeric_plain_http(self): self.assertEqual(DeploymentTarget("127.0.0.1",1024,"http://127.0.0.1:1024").origin,"http://127.0.0.1:1024")
    def test_sealed_types_cannot_be_constructed(self):
        with self.assertRaises(TypeError): VerifiedLoopbackDeployment()
        with self.assertRaises(TypeError): VerifiedTechnicalPublication()
    def test_no_unqualified_publication_claim_in_module_docs(self):
        self.assertNotIn("successfully published",inspect.getsource(deployment_module).lower())
        self.assertNotIn("publicly available",inspect.getsource(verification_module).lower())

    def test_two_route_mechanics_requires_closure_order_and_budget(self):
        """Mechanics-only: this deliberately manufactures no Manifest authority."""
        routes=(DeploymentRouteItem("/a","a","text/plain"),DeploymentRouteItem("/b","b","text/plain"))
        self.assertEqual(validate_bounded_route_mechanics(routes,2),routes)
        with self.assertRaises(ValueError): validate_bounded_route_mechanics(routes,1)
        with self.assertRaises(ValueError): validate_bounded_route_mechanics(routes+(routes[0],),3)

    def test_route_tab_and_media_type_crlf_are_rejected(self):
        for route in (DeploymentRouteItem("/a\tb","a","text/plain"),
                      DeploymentRouteItem("/a","a","text/plain\r\nX: forged")):
            with self.assertRaises(ValueError): validate_bounded_route_mechanics((route,),1)

    def test_current_probe_never_returns_active_without_handle(self):
        source=inspect.getsource(deployment_module.verify_deployment_current_availability)
        self.assertNotIn('"active",verified,None',source.replace(" ",""))

    def test_public_entrypoints_require_complete_chain_arguments_without_defaults(self):
        lifecycle={"delivery_arguments","delivery_authorization",
                   "historical_lifecycle_scope","current_lifecycle_scope"}
        contracts={
            deployment_module.issue_loopback_deployment_authorization:lifecycle|{"authorization"},
            deployment_module.start_bounded_loopback_deployment:lifecycle|{"authorization"},
            deployment_module.verify_persisted_loopback_deployment:lifecycle|{"authorization"},
            deployment_module.verify_deployment_current_availability:lifecycle|{"authorization","running"},
            deployment_module.verify_persisted_deployment_stop:lifecycle|{"authorization","deployment"},
            deployment_module.stop_bounded_loopback_deployment:lifecycle|{"authorization"},
            deployment_module.load_persisted_loopback_deployment:lifecycle|{
                "authorization_evidence_path","deployment_evidence_path"},
            deployment_module.reconcile_loopback_deployment_commitment:lifecycle|{
                "authorization_evidence_path","deployment_evidence_path"},
            verification_module.issue_technical_verification_authorization:lifecycle|{
                "deployment","running","deployment_authorization","authorization"},
            verification_module.verify_technical_publication:lifecycle|{
                "deployment","running","deployment_authorization","authorization"},
            verification_module.verify_persisted_technical_publication:lifecycle|{
                "deployment","deployment_authorization","authorization","verified"},
            verification_module.verify_technical_publication_current_availability:lifecycle|{
                "deployment","running","deployment_authorization","authorization"},
            verification_module.verify_technical_publication_and_shutdown:lifecycle|{
                "deployment_result","running","deployment_authorization","authorization"},
            verification_module.load_persisted_technical_publication:lifecycle|{
                "deployment_authorization_evidence_path","deployment_evidence_path",
                "verification_authorization_evidence_path","verification_evidence_path"},
            verification_module.reconcile_technical_observation_commitment:lifecycle|{
                "deployment_authorization_evidence_path","deployment_evidence_path",
                "verification_authorization_evidence_path","verification_evidence_path"},
        }
        for function,required in contracts.items():
            signature=inspect.signature(function)
            self.assertTrue(required <= set(signature.parameters),function.__name__)
            for name in required:
                self.assertIs(signature.parameters[name].default,inspect.Parameter.empty,
                              f"{function.__name__}.{name}")

if __name__ == "__main__": unittest.main()
