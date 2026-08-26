"""TASK-055 controlled local delivery leaf-companion tests (stdlib only)."""
from __future__ import annotations

from dataclasses import asdict, fields, replace
import hashlib
import inspect
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from briefforge.bcrp.model import BCRPBundle, BCRPRecord, RECORD_KINDS
from briefforge.publication_distribution_delivery import (
    ControlledLocalDeliveryAuthorization, ControlledLocalDestination,
    DeliveryFinding, DeliveryInventoryItem, ControlledLocalDeliveryEvidence,
    ControlledLocalDeliveryResult, VerifiedControlledLocalDelivery,
    VerifiedControlledLocalDeliveryAuthorization,
    compute_delivery_inventory_fingerprint, compute_delivery_authorization_fingerprint,
    compute_delivery_evidence_fingerprint, validate_delivery_inventory,
    perform_controlled_local_delivery, verify_persisted_controlled_local_delivery,
    issue_controlled_local_delivery_authorization, reconcile_pending_controlled_local_delivery,
    verify_controlled_local_delivery_current_eligibility,
)
from briefforge.publication_manifest_admission import compute_artifact_set_fingerprint
import briefforge.publication_distribution_delivery as delivery_module
from tests import test_publication_manifest_admission as manifest_tests

POLICY = "briefforge-controlled-local-delivery-policy:1.0.0"
PROFILE = "briefforge-controlled-local-directory-delivery-profile:1.0.0"
AUTHORITY_ID = "authority:briefforge-controlled-local-delivery"
AUTHORITY_OWNER = "project:BriefForge"
AUTHORITY_ROLE = "controlled-local-delivery-authority"
AUTHORITY_SCOPE = "one-fixed-controlled-local-directory-delivery"
IMPLEMENTATION = "briefforge.publication_distribution_delivery"
EXCLUSIONS = (
    "network-distribution", "remote-receipt", "deployment-authority", "hosting-authority",
    "successful-publication-authority", "public-reachability", "browser-behavior-certification",
    "reader-access-certification", "accessibility-certification", "editorial-certification",
    "visual-certification", "factual-reassessment", "atlasforge-authority",
)


class ControlledLocalDeliveryTests(unittest.TestCase):
    # Composition/aliasing deliberately avoids subclassing another TestCase.
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
        records = []
        for record in base.records:
            doc = record.to_document()
            if record.kind == "PortablePresentationMaterialRecord":
                scope = delivery_module._released_destination_scope(
                    self._delivery_parent, "published-task055", self._delivery_ledger)
                doc["semantic"]["authorities"].append({
                    "id": AUTHORITY_ID, "owner_identity": AUTHORITY_OWNER,
                    "role": AUTHORITY_ROLE, "scope": scope,
                })
            records.append(BCRPRecord.from_document(doc))
        return BCRPBundle(base.profile_identity, base.profile_version, tuple(records))

    def _case(self, root: Path):
        self._delivery_parent = root / "deliveries"; self._delivery_parent.mkdir(mode=0o700); self._delivery_parent.chmod(0o700)
        self._delivery_ledger = root / "delivery-ledger"; self._delivery_ledger.mkdir(mode=0o700); self._delivery_ledger.chmod(0o700)
        predecessor = self._real_predecessor(root)
        manifest_dir = root / "manifest"; manifest_dir.mkdir()
        manifest_auth = self._manifest_authorization(predecessor, manifest_dir)
        manifest = self._manifest_call(predecessor, manifest_auth)
        self.assertFalse(manifest.blocked, manifest.findings)
        parent = self._delivery_parent
        ledger = self._delivery_ledger
        auth = self._delivery_authorization(predecessor, manifest_auth, manifest.verified, parent, ledger)
        if not hasattr(self,"_issued_delivery"): self._issued_delivery={}
        issue_args=self._args(predecessor,manifest_auth,auth)
        marker=issue_controlled_local_delivery_authorization(**issue_args)
        self._issued_delivery[auth.fingerprint]=marker
        return predecessor, manifest_auth, manifest, auth

    def _delivery_authorization(self, case, manifest_auth, verified_manifest, parent, ledger, **changes):
        item = manifest_auth.artifact_inventory[0]
        inventory = (DeliveryInventoryItem(item.identity, item.role, item.logical_filename,
                                           item.media_type, item.byte_length, item.sha256, item.order),)
        values = dict(
            identity="delivery-authorization:task055-real", policy_identity=POLICY,
            profile_identity=PROFILE, profile_version="1.0.0",
            authority_identity=AUTHORITY_ID, authority_owner=AUTHORITY_OWNER,
            authority_role=AUTHORITY_ROLE, authorization_time="2026-07-31T12:02:00Z",
            attempt_time="2026-07-31T12:03:00Z", completion_time="2026-07-31T12:04:00Z",
            manifest_authorization_fingerprint=manifest_auth.fingerprint,
            manifest_fingerprint=verified_manifest.fingerprint.digest,
            manifest_identity=manifest_auth.manifest_identity,
            manifest_record_identity=manifest_auth.record_identity,
            release_identity=manifest_auth.release_identity,
            release_fingerprint=manifest_auth.release_fingerprint,
            lifecycle_inventory_digest=case[0][2].inventory_digest,
            artifact_set_fingerprint=manifest_auth.artifact_set_fingerprint,
            delivery_inventory=inventory,
            delivery_inventory_fingerprint=compute_delivery_inventory_fingerprint(inventory),
            destination=ControlledLocalDestination(str(parent.resolve()), "published-task055",
                os.stat(parent,follow_symlinks=False).st_dev,os.stat(parent,follow_symlinks=False).st_ino),
            attempt_identity="delivery-attempt:task055-real",
            evidence_identity="delivery-evidence:task055-real",
            evidence_filename="controlled-local-delivery-evidence.json",
            implementation_identity=IMPLEMENTATION, implementation_version="1.0.0",
            commitment_ledger_directory=str(ledger.resolve()),
            commitment_ledger_device=os.stat(ledger,follow_symlinks=False).st_dev,
            commitment_ledger_inode=os.stat(ledger,follow_symlinks=False).st_ino, exclusions=EXCLUSIONS,
            released_authority_scope=delivery_module._released_destination_scope(parent, "published-task055", ledger),
        )
        values.update(changes)
        provisional = ControlledLocalDeliveryAuthorization(**values, fingerprint="")
        return replace(provisional, fingerprint=compute_delivery_authorization_fingerprint(provisional))

    def _args(self, case, manifest_auth, auth):
        inputs, invocation, conformance, _ = case
        return dict(
            manifest_evidence_path=Path(manifest_auth.evidence_directory) / manifest_auth.evidence_filename,
            manifest_authorization=manifest_auth, evidence_snapshot=inputs[0],
            verified_release=inputs[1], lifecycle_scope=inputs[2], declaration=inputs[3],
            planning_authorization=inputs[4], verified_plan=inputs[5],
            invocation_authorization=invocation, conformance_authorization=conformance,
            artifact_paths=(Path(invocation.output_directory) / invocation.output_filename,),
            authorization=getattr(self,"_issued_delivery",{}).get(auth.fingerprint,auth),
        )

    def _perform(self, packed, **changes):
        case, manifest_auth, _, auth = packed
        args = self._args(case, manifest_auth, auth); args.update(changes)
        return perform_controlled_local_delivery(**args)

    def test_real_minimal_html_chain_delivers_exact_bytes_and_reloads(self):
        with tempfile.TemporaryDirectory() as t:
            packed = self._case(Path(t)); case, manifest_auth, manifest, auth = packed
            source = Path(auth.destination.parent_directory).parent / "renderer" / "publication.html"
            original = source.read_bytes(); manifest_bytes = Path(manifest_auth.evidence_directory, manifest_auth.evidence_filename).read_bytes()
            result = self._perform(packed)
            self.assertEqual(result.state, "completed"); self.assertFalse(result.blocked, result.findings)
            self.assertIsInstance(result.verified, VerifiedControlledLocalDelivery)
            final = Path(auth.destination.parent_directory, auth.destination.basename)
            self.assertEqual((final / "publication.html").read_bytes(), original)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(Path(manifest_auth.evidence_directory, manifest_auth.evidence_filename).read_bytes(), manifest_bytes)
            reloaded = verify_persisted_controlled_local_delivery(**self._args(case, manifest_auth, auth))
            self.assertEqual(reloaded.fingerprint, result.verified.fingerprint)
            self.assertEqual(len(reloaded.evidence.inventory), 1)

    def test_production_calls_both_manifest_verifiers(self):
        with tempfile.TemporaryDirectory() as t:
            packed = self._case(Path(t))
            with patch("briefforge.publication_distribution_delivery.verify_persisted_publication_manifest", wraps=manifest_tests.verify_persisted_publication_manifest) as persisted, patch("briefforge.publication_distribution_delivery.verify_manifest_current_eligibility", wraps=manifest_tests.verify_manifest_current_eligibility) as current:
                result = self._perform(packed)
            self.assertFalse(result.blocked); self.assertGreaterEqual(persisted.call_count, 2); self.assertGreaterEqual(current.call_count, 2)

    def test_replay_and_same_identity_drift_are_consumed(self):
        with tempfile.TemporaryDirectory() as t:
            packed = self._case(Path(t)); self.assertFalse(self._perform(packed).blocked)
            self.assertEqual({f.code for f in self._perform(packed).findings}, {"delivery-authorization-consumed"})
            case, ma, mv, auth = packed
            other = replace(auth, attempt_identity="delivery-attempt:drift", fingerprint="")
            other = replace(other, fingerprint=compute_delivery_authorization_fingerprint(other))
            self.assertEqual({f.code for f in perform_controlled_local_delivery(**self._args(case, ma, other)).findings}, {"delivery-authorization-not-issued"})

    def test_concurrent_reuse_has_exactly_one_winner(self):
        with tempfile.TemporaryDirectory() as t:
            packed = self._case(Path(t)); barrier = threading.Barrier(2); results=[]
            def run(): barrier.wait(); results.append(self._perform(packed))
            threads=[threading.Thread(target=run) for _ in range(2)]
            [x.start() for x in threads]; [x.join() for x in threads]
            self.assertEqual(sum(r.state == "completed" for r in results), 1)

    def test_precommit_eligibility_toctou_blocks_and_consumes(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); calls=0
            real=manifest_tests.verify_manifest_current_eligibility
            def gate(verified, *, lifecycle_scope):
                nonlocal calls; calls += 1
                if calls == 2: return manifest_tests.PublicationManifestResult((manifest_tests.ManifestFinding("manifest-not-currently-eligible","/lifecycle","changed"),), None)
                return real(verified, lifecycle_scope=lifecycle_scope)
            with patch("briefforge.publication_distribution_delivery.verify_manifest_current_eligibility", side_effect=gate): result=self._perform(packed)
            self.assertTrue(result.blocked); self.assertIn("delivery-no-longer-eligible", {f.code for f in result.findings})
            self.assertFalse(Path(packed[3].destination.parent_directory, packed[3].destination.basename).exists())
            self.assertEqual({f.code for f in self._perform(packed).findings}, {"delivery-authorization-consumed"})

    def test_failure_after_durable_rename_is_explicit_pending_and_keeps_bytes(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t))
            with patch("briefforge.publication_distribution_delivery._write_completed_commitment", side_effect=OSError("disk")):
                result=self._perform(packed)
            self.assertEqual(result.state, "completion-pending"); self.assertIsNone(result.verified)
            self.assertTrue(Path(packed[3].destination.parent_directory, packed[3].destination.basename).is_dir())

    def test_pre_rename_fault_rolls_stage_back_but_consumption_remains(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t))
            with patch("briefforge.publication_distribution_delivery._atomic_install_noreplace", side_effect=OSError("unsupported")):
                result=self._perform(packed)
            self.assertTrue(result.blocked); parent=Path(packed[3].destination.parent_directory)
            self.assertEqual(tuple(parent.iterdir()), ()); self.assertEqual(len(tuple(Path(packed[3].commitment_ledger_directory).glob("*.consumed"))),1)

    def test_final_evidence_has_complete_links_and_no_forbidden_claims(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); result=self._perform(packed); evidence=result.verified.evidence
            self.assertEqual(evidence.exclusions, EXCLUSIONS)
            source_paths=tuple(Path(p) for p in evidence.source_paths)
            self.assertEqual(evidence.audit_links,delivery_module._audit_links(packed[3],self._issued_delivery[packed[3].fingerprint],source_paths))
            self.assertEqual(len(evidence.audit_links),len(set(evidence.audit_links)))
            self.assertEqual(evidence.artifact_count,1)
            self.assertEqual(evidence.aggregate_byte_length,sum(x.byte_length for x in evidence.inventory))
            text=json.dumps(asdict(evidence), sort_keys=True)
            for value in (packed[3].identity, packed[3].manifest_identity, packed[3].release_identity, packed[3].attempt_identity): self.assertIn(value, text)
            self.assertNotIn('"deployment_authority": true', text); self.assertNotIn("successful_publication", {f.name for f in fields(ControlledLocalDeliveryEvidence)})

    def test_exactly_eleven_bcrp_kinds_and_import_isolation(self):
        self.assertEqual(len(RECORD_KINDS),11)
        import briefforge.bcrp.model as model
        self.assertFalse(hasattr(model,"ControlledLocalDeliveryAuthorization"))
        self.assertNotIn("publication_distribution_delivery", inspect.getsource(model))

    def test_public_api_has_no_callback_or_status_bypass(self):
        names=set(inspect.signature(perform_controlled_local_delivery).parameters)
        self.assertFalse(names & {"callback","fault","status","verified_manifest","eligibility_status"})

    def test_records_are_frozen_and_typed(self):
        item=self._synthetic_item()
        with self.assertRaises((AttributeError,TypeError)): item.sha256="0"*64
        self.assertEqual({f.name for f in fields(DeliveryFinding)}, {"code","location","message"})

    def _synthetic_item(self, **changes):
        values=dict(identity="artifact:a",role="primary",logical_filename="index.html",media_type="text/html",byte_length=1,sha256=hashlib.sha256(b"x").hexdigest(),order=0)
        values.update(changes); return DeliveryInventoryItem(**values)

    def test_pure_multi_artifact_inventory_is_closed_and_distinct(self):
        items=(self._synthetic_item(),self._synthetic_item(identity="artifact:b",role="notice",logical_filename="NOTICE.txt",media_type="text/plain",byte_length=2,sha256=hashlib.sha256(b"y\n").hexdigest(),order=1),self._synthetic_item(identity="artifact:c",role="exhibit",logical_filename="chart.svg",media_type="image/svg+xml",byte_length=7,sha256=hashlib.sha256(b"<svg/>").hexdigest(),order=2))
        self.assertEqual(validate_delivery_inventory(items),())
        self.assertEqual(len({x.sha256 for x in items}),3); self.assertEqual(compute_delivery_inventory_fingerprint(items),compute_delivery_inventory_fingerprint(tuple(items)))

    def test_production_rejects_caller_manufactured_multi_inventory(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); case,ma,mv,auth=packed
            extra=self._synthetic_item(identity="artifact:invented",role="notice",logical_filename="NOTICE.txt",order=1)
            inventory=auth.delivery_inventory+(extra,)
            bad=replace(auth,delivery_inventory=inventory,delivery_inventory_fingerprint=compute_delivery_inventory_fingerprint(inventory),fingerprint="")
            bad=replace(bad,fingerprint=compute_delivery_authorization_fingerprint(bad))
            result=perform_controlled_local_delivery(**self._args(case,ma,bad)); self.assertTrue(result.blocked)
            self.assertIn("delivery-authorization-not-issued",{f.code for f in result.findings})

    def test_source_tamper_after_validation_blocks_after_consumption(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); source=Path(packed[1].artifact_inventory[0].source_path); original=source.read_bytes()
            real=delivery_module._reserve_authorization
            def reserve_then_tamper(*args):
                real(*args); source.write_bytes(b"tamper")
            with patch("briefforge.publication_distribution_delivery._reserve_authorization",side_effect=reserve_then_tamper):
                self.assertTrue(self._perform(packed).blocked)
            self.assertEqual(len(tuple(Path(packed[3].commitment_ledger_directory).glob("*.consumed"))), 1)
            source.write_bytes(original)
            self.assertEqual({f.code for f in self._perform(packed).findings}, {"delivery-authorization-consumed"})
    def test_source_symlink_blocks(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); p=Path(packed[1].artifact_inventory[0].source_path); q=p.with_suffix(".real"); p.rename(q); p.symlink_to(q)
            self.assertTrue(self._perform(packed).blocked)
    def test_source_hardlink_blocks(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); p=Path(packed[1].artifact_inventory[0].source_path); os.link(p,p.with_suffix(".link"))
            self.assertTrue(self._perform(packed).blocked)
    def test_preexisting_destination_blocks_without_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); final=Path(packed[3].destination.parent_directory,packed[3].destination.basename); final.mkdir(); marker=final/"keep"; marker.write_bytes(b"keep")
            self.assertTrue(self._perform(packed).blocked); self.assertEqual(marker.read_bytes(),b"keep")

    def _inventory_codes(self, *items): return {x.code for x in validate_delivery_inventory(tuple(items))}
    def test_rejects_slash(self): self.assertIn("unsafe-delivery-basename",self._inventory_codes(self._synthetic_item(logical_filename="a/b")))
    def test_rejects_backslash(self): self.assertIn("unsafe-delivery-basename",self._inventory_codes(self._synthetic_item(logical_filename="a\\b")))
    def test_rejects_nul(self): self.assertIn("unsafe-delivery-basename",self._inventory_codes(self._synthetic_item(logical_filename="a\0b")))
    def test_rejects_dot(self): self.assertIn("unsafe-delivery-basename",self._inventory_codes(self._synthetic_item(logical_filename=".")))
    def test_rejects_dotdot(self): self.assertIn("unsafe-delivery-basename",self._inventory_codes(self._synthetic_item(logical_filename="..")))
    def test_rejects_non_nfc(self): self.assertIn("unsafe-delivery-basename",self._inventory_codes(self._synthetic_item(logical_filename="cafe\u0301.html")))
    def test_rejects_casefold_collision(self): self.assertIn("delivery-basename-collision",self._inventory_codes(self._synthetic_item(),self._synthetic_item(identity="artifact:b",role="b",logical_filename="INDEX.HTML",order=1)))
    def test_rejects_nfc_collision(self): self.assertIn("unsafe-delivery-basename",self._inventory_codes(self._synthetic_item(logical_filename="cafe\u0301.html"),self._synthetic_item(identity="artifact:b",role="b",logical_filename="caf\u00e9.html",order=1)))
    def test_rejects_duplicate_identity(self): self.assertIn("duplicate-delivery-identity",self._inventory_codes(self._synthetic_item(),self._synthetic_item(role="b",logical_filename="b",order=1)))
    def test_rejects_duplicate_role(self): self.assertIn("duplicate-delivery-role",self._inventory_codes(self._synthetic_item(),self._synthetic_item(identity="artifact:b",logical_filename="b",order=1)))
    def test_rejects_duplicate_order(self): self.assertIn("duplicate-delivery-order",self._inventory_codes(self._synthetic_item(),self._synthetic_item(identity="artifact:b",role="b",logical_filename="b")))
    def test_rejects_noncontiguous_order(self): self.assertIn("delivery-order-mismatch",self._inventory_codes(self._synthetic_item(order=2)))
    def test_rejects_bad_digest(self): self.assertIn("invalid-delivery-digest",self._inventory_codes(self._synthetic_item(sha256="x")))
    def test_rejects_bad_length(self): self.assertIn("invalid-delivery-length",self._inventory_codes(self._synthetic_item(byte_length=-1)))

    def test_authority_binding_drift_blocks(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); case,ma,mv,auth=packed
            for field,value in (("authority_owner","other"),("authority_role","other"),("policy_identity","other"),("profile_identity","other"),("implementation_identity","other"),("manifest_fingerprint","0"*64),("release_fingerprint","0"*64),("exclusions",())):
                bad=replace(auth,**{field:value},identity=f"delivery-authorization:{field}",fingerprint=""); bad=replace(bad,fingerprint=compute_delivery_authorization_fingerprint(bad))
                result=perform_controlled_local_delivery(**self._args(case,ma,bad)); self.assertTrue(result.blocked,field)

    def test_caller_cannot_manufacture_authority_for_arbitrary_destination(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); case,ma,mv,auth=packed
            other=Path(t)/"other"; other.mkdir(mode=0o700); other.chmod(0o700)
            info=os.stat(other,follow_symlinks=False)
            bad=replace(auth,destination=ControlledLocalDestination(str(other.resolve()),auth.destination.basename,info.st_dev,info.st_ino),
                        released_authority_scope=delivery_module._released_destination_scope(other,auth.destination.basename,Path(auth.commitment_ledger_directory)),fingerprint="")
            bad=replace(bad,fingerprint=compute_delivery_authorization_fingerprint(bad))
            result=perform_controlled_local_delivery(**self._args(case,ma,bad))
            self.assertEqual({f.code for f in result.findings},{"delivery-authorization-not-issued"})

    def test_authority_scope_binds_inode_and_contract(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); auth=packed[3]; scope=json.loads(auth.released_authority_scope)
            self.assertEqual(scope["destination_parent"]["inode"],os.stat(auth.destination.parent_directory).st_ino)
            self.assertEqual(scope["ledger"]["inode"],os.stat(auth.commitment_ledger_directory).st_ino)
            self.assertEqual(scope["contract"],{"atomic":"renameat2-noreplace","collision":"nfc-casefold-no-alias","no_overwrite":True,"rollback":"verified-or-indeterminate"})

    def test_group_or_world_writable_boundaries_are_rejected_without_consumption(self):
        for which in ("parent","ledger"):
            with self.subTest(which=which), tempfile.TemporaryDirectory() as t:
                packed=self._case(Path(t)); auth=packed[3]
                target=Path(auth.destination.parent_directory if which=="parent" else auth.commitment_ledger_directory); target.chmod(0o770)
                result=self._perform(packed)
                self.assertIn("invalid-delivery-persistence-boundary",{f.code for f in result.findings})
                self.assertEqual(tuple(Path(auth.commitment_ledger_directory).glob("*.consumed")),())

    def test_chronology_and_identity_separation_are_strict(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); case,ma,mv,auth=packed
            for changes in ({"attempt_time":auth.authorization_time},{"completion_time":auth.attempt_time},
                            {"attempt_identity":auth.identity},{"authorization_time":"2026-07-31T12:02:00+00:00"}):
                bad=replace(auth,**changes,fingerprint=""); bad=replace(bad,fingerprint=compute_delivery_authorization_fingerprint(bad))
                self.assertIn("delivery-authorization-not-issued",{f.code for f in perform_controlled_local_delivery(**self._args(case,ma,bad)).findings})

    def test_historical_verification_does_not_require_current_eligibility(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); self.assertFalse(self._perform(packed).blocked)
            with patch("briefforge.publication_distribution_delivery.verify_manifest_current_eligibility",side_effect=AssertionError("historical verifier called current gate")):
                verified=verify_persisted_controlled_local_delivery(**self._args(packed[0],packed[1],packed[3]))
            self.assertIsInstance(verified,VerifiedControlledLocalDelivery)

    def test_destination_parent_symlink_and_noncanonical_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); case,ma,mv,auth=packed; actual=Path(t)/"actual"; actual.mkdir(); link=Path(t)/"link"; link.symlink_to(actual,target_is_directory=True)
            info=os.stat(actual,follow_symlinks=False)
            bad=replace(auth,destination=ControlledLocalDestination(str(link),"x",info.st_dev,info.st_ino),identity="delivery-authorization:link",fingerprint=""); bad=replace(bad,fingerprint=compute_delivery_authorization_fingerprint(bad))
            self.assertTrue(perform_controlled_local_delivery(**self._args(case,ma,bad)).blocked)

    def test_portable_destination_collision_blocks_without_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); parent=Path(packed[3].destination.parent_directory)
            collision=parent/packed[3].destination.basename.upper(); collision.mkdir(); marker=collision/"keep"; marker.write_bytes(b"keep")
            result=self._perform(packed)
            self.assertTrue(result.blocked); self.assertEqual(marker.read_bytes(),b"keep")
            self.assertFalse(any(path.name.endswith(".stage") for path in parent.iterdir()))

    def test_prepared_commitment_failure_rolls_back_stage_and_consumes(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); auth=packed[3]
            with patch("briefforge.publication_distribution_delivery._write_prepared_commitment",side_effect=OSError("ledger fsync")):
                result=self._perform(packed)
            self.assertTrue(result.blocked); self.assertEqual(tuple(Path(auth.destination.parent_directory).iterdir()),())
            self.assertEqual(len(tuple(Path(auth.commitment_ledger_directory).glob("*.consumed"))),1)

    def test_missing_prepared_or_completed_commitment_is_detected(self):
        for suffix in ("prepared","completed"):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as t:
                packed=self._case(Path(t)); self.assertFalse(self._perform(packed).blocked)
                auth=packed[3]; next(Path(auth.commitment_ledger_directory).glob(f"*.{suffix}")).unlink()
                with self.assertRaises(ValueError):
                    verify_persisted_controlled_local_delivery(**self._args(packed[0],packed[1],auth))

    def test_stage_write_failure_has_no_residue_and_cannot_reuse(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); auth=packed[3]
            import briefforge.publication_distribution_delivery as module
            real=module._write_exclusive; calls=0
            def fail_stage(*args,**kwargs):
                nonlocal calls; calls += 1
                if calls == 2: raise OSError("short write")
                return real(*args,**kwargs)
            with patch("briefforge.publication_distribution_delivery._write_exclusive",side_effect=fail_stage):
                result=self._perform(packed)
            self.assertTrue(result.blocked); self.assertEqual(tuple(Path(auth.destination.parent_directory).iterdir()),())
            self.assertTrue(self._perform(packed).blocked)

    def test_persisted_artifact_or_evidence_tamper_detected(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); self._perform(packed); case,ma,mv,auth=packed; args=self._args(case,ma,auth); final=Path(auth.destination.parent_directory,auth.destination.basename)
            (final/auth.delivery_inventory[0].logical_filename).write_bytes(b"tamper")
            with self.assertRaises(ValueError): verify_persisted_controlled_local_delivery(**args)

    def test_coordinated_evidence_and_completed_rewrite_detected(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); self._perform(packed); case,ma,mv,auth=packed; final=Path(auth.destination.parent_directory,auth.destination.basename); evidence=final/auth.evidence_filename
            evidence.write_bytes(evidence.read_bytes()+b" ")
            for p in Path(auth.commitment_ledger_directory).glob("*.completed"): p.write_bytes(hashlib.sha256(evidence.read_bytes()).hexdigest().encode())
            with self.assertRaises(ValueError): verify_persisted_controlled_local_delivery(**self._args(case,ma,auth))

    def test_no_network_database_or_dynamic_imports(self):
        import ast
        import briefforge.publication_distribution_delivery as module
        tree=ast.parse(inspect.getsource(module))
        imported={alias.name.split(".")[0] for node in ast.walk(tree)
                  if isinstance(node,(ast.Import,ast.ImportFrom))
                  for alias in (node.names if isinstance(node,ast.Import) else [ast.alias(node.module or "")])}
        self.assertFalse(imported & {"socket","requests","urllib","http","ftplib","sqlite3","subprocess","importlib"})
        self.assertFalse(any(isinstance(node,ast.Call) and isinstance(node.func,ast.Name)
                             and node.func.id in {"eval","exec","__import__"} for node in ast.walk(tree)))

    def test_issued_authorization_evidence_tamper_blocks_execution(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); auth=packed[3]; marker=self._issued_delivery[auth.fingerprint]
            issuance=Path(auth.commitment_ledger_directory)/marker.issuance_evidence_filename
            issuance.write_bytes(issuance.read_bytes()+b" ")
            result=self._perform(packed)
            self.assertEqual({f.code for f in result.findings},{"delivery-authorization-not-issued"})
            self.assertFalse(Path(auth.destination.parent_directory,auth.destination.basename).exists())

    def test_preexisting_deterministic_stage_is_never_deleted(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); auth=packed[3]
            stage="."+auth.destination.basename+"."+hashlib.sha256(auth.attempt_identity.encode()).hexdigest()[:20]+".stage"
            stage_path=Path(auth.destination.parent_directory)/stage
            stage_path.mkdir(); victim=stage_path/"victim"; victim.write_bytes(b"preserve")
            result=self._perform(packed)
            self.assertEqual(result.state,"rollback-verified")
            self.assertEqual(victim.read_bytes(),b"preserve")
            self.assertFalse(Path(auth.destination.parent_directory,auth.destination.basename).exists())

    def test_unknown_stage_entry_makes_rollback_indeterminate(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); auth=packed[3]
            def contaminate(parent_fd,stage,destination):
                stage_fd=os.open(stage,os.O_RDONLY|os.O_DIRECTORY,dir_fd=parent_fd)
                try:
                    fd=os.open("alien",os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600,dir_fd=stage_fd)
                    os.write(fd,b"alien"); os.close(fd)
                finally: os.close(stage_fd)
                raise OSError("commit fault")
            with patch("briefforge.publication_distribution_delivery._atomic_install_noreplace",side_effect=contaminate):
                result=self._perform(packed)
            self.assertEqual(result.state,"rollback-indeterminate")
            self.assertEqual({f.code for f in result.findings},{"delivery-rollback-indeterminate"})
            self.assertFalse(Path(auth.destination.parent_directory,auth.destination.basename).exists())

    def test_completion_pending_can_be_reconciled_without_reusing_authorization(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); case,ma,_,auth=packed
            with patch("briefforge.publication_distribution_delivery._write_completed_commitment",side_effect=OSError("disk")):
                pending=self._perform(packed)
            self.assertEqual(pending.state,"completion-pending")
            reconciled=reconcile_pending_controlled_local_delivery(**self._args(case,ma,auth))
            self.assertEqual(reconciled.state,"completed"); self.assertIsNotNone(reconciled.verified)
            self.assertEqual({f.code for f in self._perform(packed).findings},{"delivery-authorization-consumed"})

    def test_reconciliation_rejects_tampered_final_bytes(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); case,ma,_,auth=packed
            with patch("briefforge.publication_distribution_delivery._write_completed_commitment",side_effect=OSError("disk")):
                self.assertEqual(self._perform(packed).state,"completion-pending")
            final=Path(auth.destination.parent_directory,auth.destination.basename)
            (final/auth.delivery_inventory[0].logical_filename).write_bytes(b"tamper")
            result=reconcile_pending_controlled_local_delivery(**self._args(case,ma,auth))
            self.assertEqual({f.code for f in result.findings},{"delivery-reconciliation-blocked"})

    def test_persisted_verifier_rejects_final_path_detachment_race(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); case,ma,_,auth=packed
            self.assertFalse(self._perform(packed).blocked)
            final=Path(auth.destination.parent_directory,auth.destination.basename)
            detached=final.with_name(final.name+"-detached")
            def detach():
                final.rename(detached); final.mkdir()
            with patch("briefforge.publication_distribution_delivery._after_final_open_before_return",side_effect=detach):
                with self.assertRaises(ValueError):
                    verify_persisted_controlled_local_delivery(**self._args(case,ma,auth))

    def test_bounded_multi_artifact_transaction_primitive_writes_and_reloads_exact_closure(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); stage=root/"stage"; stage.mkdir(); fd=os.open(stage,os.O_RDONLY|os.O_DIRECTORY)
            try:
                contents=(b"<p>x</p>",b"notice\n")
                items=(self._synthetic_item(identity="artifact:page",role="primary",logical_filename="index.html",byte_length=len(contents[0]),sha256=hashlib.sha256(contents[0]).hexdigest(),order=0),
                       self._synthetic_item(identity="artifact:notice",role="notice",logical_filename="NOTICE.txt",media_type="text/plain",byte_length=len(contents[1]),sha256=hashlib.sha256(contents[1]).hexdigest(),order=1))
                identity=(os.fstat(fd).st_dev,os.fstat(fd).st_ino); evidence=b'{"bounded":"synthetic-two-artifact-transaction"}'
                delivery_module._execute_inventory_transaction(fd,items,contents,"delivery-evidence.json",evidence,identity)
                delivery_module._verify_inventory_transaction(fd,items,"delivery-evidence.json",evidence,identity)
                self.assertEqual(tuple((stage/x.logical_filename).read_bytes() for x in items),contents)
                self.assertEqual(sorted(p.name for p in stage.iterdir()),["NOTICE.txt","delivery-evidence.json","index.html"])
            finally: os.close(fd)

    def test_issuance_commitment_fault_rolls_back_both_issuance_files(self):
        with tempfile.TemporaryDirectory() as t:
            packed=self._case(Path(t)); case,ma,_,base=packed
            fresh=replace(base,identity="delivery-authorization:issuance-fault",attempt_identity="delivery-attempt:issuance-fault",evidence_identity="delivery-evidence:issuance-fault",fingerprint="")
            fresh=replace(fresh,fingerprint=compute_delivery_authorization_fingerprint(fresh))
            real=delivery_module._write_exclusive
            def write_then_fail(fd,name,data,mode=0o600):
                real(fd,name,data,mode)
                if name.endswith(".authorization.commitment"): raise OSError("post-write fault")
            with patch("briefforge.publication_distribution_delivery._write_exclusive",side_effect=write_then_fail):
                with self.assertRaisesRegex(ValueError,"rollback was verified"):
                    issue_controlled_local_delivery_authorization(**self._args(case,ma,fresh))
            evidence_name,commitment_name=delivery_module._issuance_names(fresh)
            ledger=Path(fresh.commitment_ledger_directory)
            self.assertFalse((ledger/evidence_name).exists()); self.assertFalse((ledger/commitment_name).exists())

    def test_current_eligibility_rejects_cross_manifest_substitution(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); first_root=root/"first"; second_root=root/"second"
            first_root.mkdir(); second_root.mkdir()
            first=self._case(first_root); first_result=self._perform(first)
            self.assertEqual(first_result.state,"completed")
            second=self._case(second_root)
            args=self._args(second[0],second[1],second[3]); args.pop("authorization")
            historical_scope=args.pop("lifecycle_scope")
            args["historical_lifecycle_scope"]=historical_scope
            args["current_lifecycle_scope"]=historical_scope
            result=verify_controlled_local_delivery_current_eligibility(first_result.verified,**args)
            self.assertEqual({f.code for f in result.findings},{"current-eligibility-cross-authority-mismatch"})


if __name__ == "__main__": unittest.main()
