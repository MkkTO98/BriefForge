"""TASK-047 lifecycle-authority correction and fail-closed compatibility proof."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

from briefforge.bcrp import (  # noqa: E402
    BCRPBundle,
    BCRPPromotionRejected,
    BCRPRecord,
    RecordDraft,
    TechnicalValidationResult,
    author_candidate_bundle,
    fingerprint_bundle,
    promote_validated_candidate,
    record_candidate_validation,
    validate_bundle,
)
from briefforge.bcrp.corpus import CASE_IDS, load_case  # noqa: E402
from briefforge.bcrp_legacy_compatibility import (  # noqa: E402
    CompatibilityRejected,
    EvidenceIdentityAndTime,
    FingerprintLineage,
    IdentityMapping,
    LegacyCompatibilityMapping,
    PolicyTranslation,
    lifecycle_evidence_inventory_digest,
    map_legacy_ready_to_bcrp,
    verify_mapped_legacy_ready,
)
from briefforge.promotion import ReadyPresentationPackage, promote_candidate_presentation_package  # noqa: E402
from briefforge.runtime import (  # noqa: E402
    CandidatePresentationPackage,
    EncounterSemantics,
    OrganizingPurpose,
    PackageIdentity,
    PresentationObligation,
    PresentationStatement,
    UpstreamReference,
    semantic_fingerprint,
)
from briefforge.validation import (  # noqa: E402
    CURRENT_VALIDATION_POLICY_ID,
    ValidationJudgment,
    validate_candidate_presentation_package,
)


class LifecycleAuthorityCorrectionTests(unittest.TestCase):
    def _bcrp_candidate(self, case_index: int = 0) -> BCRPBundle:
        source = load_case(CASE_IDS[case_index])
        draft = lambda kind: RecordDraft(  # noqa: E731
            identity=source.one(kind).identity,
            semantic=deepcopy(source.one(kind).semantic),
            extensions=deepcopy(source.one(kind).extensions),
        )
        return author_candidate_bundle(
            brief=draft("PresentationBriefRecord"),
            material=draft("PortablePresentationMaterialRecord"),
            candidate=draft("CandidatePresentationPackageRecord"),
        )

    def test_technically_valid_native_candidate_cannot_self_approve(self):
        candidate = self._bcrp_candidate()
        result = record_candidate_validation(candidate)
        self.assertIsInstance(result, TechnicalValidationResult)
        self.assertTrue(result.passed)
        self.assertEqual(result.executed_layers, ("L0", "L1", "L2"))
        self.assertEqual(result.findings, ())
        self.assertEqual(len(candidate.records_of_kind("ValidationJudgmentRecord")), 0)

    def test_technically_valid_native_candidate_cannot_self_promote(self):
        candidate = self._bcrp_candidate()
        digest = fingerprint_bundle(candidate, domain="candidate-semantic").digest
        forged = deepcopy(candidate)
        forged.records += (
            BCRPRecord(
                kind="ValidationJudgmentRecord",
                identity="judgment:authority-free",
                profile_version="1.0.0",
                semantic={
                    "candidate_ref": candidate.one("CandidatePresentationPackageRecord").identity,
                    "candidate_fingerprint": digest,
                    "policy_id": "policy:authority-free",
                    "executed_layers": ["L0", "L1", "L2"],
                    "valid": True,
                    "findings": [],
                },
            ),
        )
        with self.assertRaisesRegex(BCRPPromotionRejected, "sole operational|compatibility"):
            promote_validated_candidate(
                forged,
                ready_identity="ready:authority-free",
                readiness_time="2026-07-16T12:01:00Z",
            )

    def test_negative_technical_findings_remain_complete_without_becoming_judgment(self):
        candidate = self._bcrp_candidate()
        candidate.one("CandidatePresentationPackageRecord").semantic["statements"][0].pop("authority_ref")
        result = record_candidate_validation(candidate)
        self.assertFalse(result.passed)
        self.assertTrue(result.findings)
        self.assertTrue(any(finding.family == "authority-or-provenance" for finding in result.findings))
        self.assertEqual(candidate.records_of_kind("ValidationJudgmentRecord"), ())


class LegacyCompatibilityContractTests(unittest.TestCase):
    def _legacy_candidate(self, suffix: str = "alpha", statement_count: int = 1) -> CandidatePresentationPackage:
        statements = tuple(
            PresentationStatement(
                statement_id=f"claim-{suffix}-{index}",
                encounter_meaning=f"Explicitly authored statement {index} for {suffix}.",
                belongs_to_purpose=f"purpose-{suffix}",
                encounter_semantics=EncounterSemantics(
                    mode="sequence",
                    description=f"Encounter step {index}.",
                ),
            )
            for index in range(statement_count)
        )
        return CandidatePresentationPackage(
            identity=PackageIdentity(
                package_id=f"legacy-package-{suffix}",
                title=f"Synthetic package {suffix}",
                purpose_summary=f"Exercise governed lifecycle {suffix}.",
                scope="One explicit synthetic presentation.",
                non_scope="No renderer, release, or publication authority.",
            ),
            organizing_purpose=OrganizingPurpose(
                statement=f"purpose-{suffix}",
                scope="Explicit synthetic scope.",
                non_scope="No inferred semantics.",
            ),
            statements=statements,
        )

    def _legacy_closure(self, suffix: str = "alpha", statement_count: int = 1):
        candidate = self._legacy_candidate(suffix, statement_count)
        judgment = validate_candidate_presentation_package(candidate)
        ready = promote_candidate_presentation_package(candidate, judgment)
        return candidate, judgment, ready

    def _bcrp_candidate(self, case_index: int = 0) -> BCRPBundle:
        source = load_case(CASE_IDS[case_index])
        return BCRPBundle(
            profile_identity=source.profile_identity,
            profile_version=source.profile_version,
            records=tuple(
                deepcopy(source.one(kind))
                for kind in (
                    "PresentationBriefRecord",
                    "PortablePresentationMaterialRecord",
                    "CandidatePresentationPackageRecord",
                )
            ),
            index={"authored_in_memory": True},
        )

    def _mapping(
        self,
        legacy_candidate: CandidatePresentationPackage,
        bcrp: BCRPBundle,
        *,
        suffix: str = "alpha",
    ) -> LegacyCompatibilityMapping:
        validation_authority = next(
            authority["id"]
            for authority in bcrp.one("PortablePresentationMaterialRecord").semantic["authorities"]
            if authority.get("role") == "validation-authority"
        )
        scope_identity = f"legacy-lifecycle-scope:{suffix}"
        candidate_evidence_identity = f"legacy-evidence:candidate-{suffix}"
        judgment_evidence_identity = f"legacy-evidence:judgment-{suffix}"
        ready_evidence_identity = f"legacy-evidence:ready-{suffix}"
        validation_time = "2026-07-16T12:00:00Z"
        readiness_time = "2026-07-16T12:01:00Z"
        legacy_digest = semantic_fingerprint(legacy_candidate)
        inventory_digest = lifecycle_evidence_inventory_digest(
            scope_identity=scope_identity,
            candidate_evidence_identity=candidate_evidence_identity,
            judgment_evidence_identity=judgment_evidence_identity,
            ready_evidence_identity=ready_evidence_identity,
            validation_time=validation_time,
            readiness_time=readiness_time,
            legacy_candidate_digest=legacy_digest,
            legacy_policy_identity=CURRENT_VALIDATION_POLICY_ID,
            competing_lifecycle_evidence_identities=(),
        )
        return LegacyCompatibilityMapping(
            evidence=EvidenceIdentityAndTime(
                scope_identity=scope_identity,
                legacy_candidate_evidence_identity=candidate_evidence_identity,
                legacy_judgment_evidence_identity=judgment_evidence_identity,
                legacy_ready_evidence_identity=ready_evidence_identity,
                validation_time=validation_time,
                readiness_time=readiness_time,
                inventory_complete=True,
                competing_lifecycle_evidence_identities=(),
                inventory_digest=inventory_digest,
                mapping_attestation_identity=f"mapping-attestation:{suffix}",
                mapping_attestation_time="2026-07-16T12:02:00Z",
                mapping_attested_by_authority_identity=validation_authority,
            ),
            identities=IdentityMapping(
                legacy_candidate_identity=legacy_candidate.identity.package_id,
                bcrp_candidate_identity=bcrp.one("CandidatePresentationPackageRecord").identity,
                bcrp_judgment_identity=f"judgment:mapped-{suffix}",
                bcrp_ready_identity=f"ready:mapped-{suffix}",
            ),
            policy=PolicyTranslation(
                legacy_policy_identity=CURRENT_VALIDATION_POLICY_ID,
                bcrp_policy_identity="bcrp-legacy-compatibility-policy:1.0.0",
                authority_basis="policy-backed-system",
                bcrp_authority_identity=validation_authority,
            ),
            fingerprints=FingerprintLineage(
                legacy_domain="legacy-candidate-semantic",
                legacy_digest=semantic_fingerprint(legacy_candidate),
                bcrp_domain="candidate-semantic",
                bcrp_digest=fingerprint_bundle(bcrp, domain="candidate-semantic").digest,
                relationship="explicit-governed-mapping",
            ),
            all_bcrp_semantic_material_explicit=True,
        )

    def _map(self, suffix: str = "alpha", case_index: int = 0, statement_count: int = 1):
        candidate, judgment, ready = self._legacy_closure(suffix, statement_count)
        bcrp = self._bcrp_candidate(case_index)
        mapping = self._mapping(candidate, bcrp, suffix=suffix)
        mapped = map_legacy_ready_to_bcrp(
            legacy_candidate=candidate,
            legacy_judgment=judgment,
            legacy_ready=ready,
            bcrp_candidate_bundle=bcrp,
            mapping=mapping,
        )
        return candidate, judgment, ready, bcrp, mapping, mapped

    def test_complete_synthetic_legacy_closure_maps_successfully(self):
        _, _, _, _, _, mapped = self._map("renamed-orchid", case_index=1, statement_count=3)
        verified = verify_mapped_legacy_ready(mapped)
        self.assertEqual(verified.one("ReadyPresentationPackageRecord").identity, "ready:mapped-renamed-orchid")
        candidate = verified.one("CandidatePresentationPackageRecord")
        self.assertEqual(len(candidate.semantic["statements"]), 7)
        self.assertTrue(any(statement["posture"] == "recommendation" for statement in candidate.semantic["statements"]))

    def test_missing_authority_evidence_and_unknown_policy_translation_fail_closed(self):
        candidate, judgment, ready = self._legacy_closure()
        bcrp = self._bcrp_candidate()
        mapping = self._mapping(candidate, bcrp)
        missing = replace(mapping, policy=replace(mapping.policy, bcrp_authority_identity=""))
        with self.assertRaisesRegex(CompatibilityRejected, "authority"):
            map_legacy_ready_to_bcrp(
                legacy_candidate=candidate,
                legacy_judgment=judgment,
                legacy_ready=ready,
                bcrp_candidate_bundle=bcrp,
                mapping=missing,
            )
        unknown = replace(mapping, policy=replace(mapping.policy, legacy_policy_identity="policy:unknown"))
        with self.assertRaisesRegex(CompatibilityRejected, "policy"):
            map_legacy_ready_to_bcrp(
                legacy_candidate=candidate,
                legacy_judgment=judgment,
                legacy_ready=ready,
                bcrp_candidate_bundle=bcrp,
                mapping=unknown,
            )

    def test_unsuccessful_legacy_judgment_cannot_produce_ready(self):
        candidate, judgment, ready = self._legacy_closure()
        failed = replace(judgment, valid=False)
        failed_ready = replace(ready, validation_judgment=failed)
        bcrp = self._bcrp_candidate()
        with self.assertRaisesRegex(CompatibilityRejected, "successful"):
            map_legacy_ready_to_bcrp(
                legacy_candidate=candidate,
                legacy_judgment=failed,
                legacy_ready=failed_ready,
                bcrp_candidate_bundle=bcrp,
                mapping=self._mapping(candidate, bcrp),
            )

    def test_stale_legacy_closure_fails(self):
        candidate, judgment, ready = self._legacy_closure()
        changed = replace(candidate, organizing_purpose=replace(candidate.organizing_purpose, statement="changed"))
        bcrp = self._bcrp_candidate()
        with self.assertRaisesRegex(CompatibilityRejected, "closure|drift|fingerprint"):
            map_legacy_ready_to_bcrp(
                legacy_candidate=changed,
                legacy_judgment=judgment,
                legacy_ready=ready,
                bcrp_candidate_bundle=bcrp,
                mapping=self._mapping(changed, bcrp),
            )

    def test_mutated_bcrp_candidate_after_mapping_fails_verification(self):
        *_, mapped = self._map()
        mapped.one("CandidatePresentationPackageRecord").semantic["statements"][0]["text"] += " altered"
        with self.assertRaisesRegex(CompatibilityRejected, "fingerprint|drift"):
            verify_mapped_legacy_ready(mapped)

    def test_wrong_identity_mapping_and_competing_records_fail(self):
        candidate, judgment, ready = self._legacy_closure()
        bcrp = self._bcrp_candidate()
        mapping = self._mapping(candidate, bcrp)
        wrong = replace(
            mapping,
            identities=replace(mapping.identities, legacy_candidate_identity="legacy-package:wrong"),
        )
        with self.assertRaisesRegex(CompatibilityRejected, "identity"):
            map_legacy_ready_to_bcrp(
                legacy_candidate=candidate,
                legacy_judgment=judgment,
                legacy_ready=ready,
                bcrp_candidate_bundle=bcrp,
                mapping=wrong,
            )
        competing_mapping = replace(
            mapping,
            evidence=replace(
                mapping.evidence,
                competing_lifecycle_evidence_identities=("legacy-evidence:competing",),
            ),
        )
        with self.assertRaisesRegex(CompatibilityRejected, "[Cc]ompeting"):
            map_legacy_ready_to_bcrp(
                legacy_candidate=candidate,
                legacy_judgment=judgment,
                legacy_ready=ready,
                bcrp_candidate_bundle=bcrp,
                mapping=competing_mapping,
            )

    def test_generic_bcrp_validation_blocks_mapped_authority_until_compatibility_verified(self):
        *_, mapped = self._map()
        generic = validate_bundle(mapped)
        unsupported = [
            finding
            for finding in generic.findings
            if finding.message == "Unknown required semantic extension cannot be processed."
        ]
        self.assertTrue(generic.blocking)
        self.assertEqual(len(unsupported), 2)
        self.assertIs(verify_mapped_legacy_ready(mapped), mapped)

    def test_unregistered_bcrp_policy_and_wrong_authority_role_fail_closed(self):
        candidate, judgment, ready = self._legacy_closure()
        bcrp = self._bcrp_candidate()
        mapping = self._mapping(candidate, bcrp)
        unregistered = replace(mapping, policy=replace(mapping.policy, bcrp_policy_identity="policy:unregistered"))
        with self.assertRaisesRegex(CompatibilityRejected, "policy"):
            map_legacy_ready_to_bcrp(
                legacy_candidate=candidate,
                legacy_judgment=judgment,
                legacy_ready=ready,
                bcrp_candidate_bundle=bcrp,
                mapping=unregistered,
            )
        wrong_authority = next(
            authority["id"]
            for authority in bcrp.one("PortablePresentationMaterialRecord").semantic["authorities"]
            if authority.get("role") == "upstream-semantic-authority"
        )
        wrong_role = replace(
            mapping,
            policy=replace(mapping.policy, bcrp_authority_identity=wrong_authority),
            evidence=replace(mapping.evidence, mapping_attested_by_authority_identity=wrong_authority),
        )
        with self.assertRaisesRegex(CompatibilityRejected, "validation authority role"):
            map_legacy_ready_to_bcrp(
                legacy_candidate=candidate,
                legacy_judgment=judgment,
                legacy_ready=ready,
                bcrp_candidate_bundle=bcrp,
                mapping=wrong_role,
            )

    def test_persisted_compatibility_payload_is_exact_and_cross_record_consistent(self):
        *_, mapped = self._map()
        tampered = deepcopy(mapped)
        for record in (
            tampered.one("ValidationJudgmentRecord"),
            tampered.one("ReadyPresentationPackageRecord"),
        ):
            record.extensions[0]["payload"]["undeclared"] = True
        with self.assertRaisesRegex(CompatibilityRejected, "undeclared"):
            verify_mapped_legacy_ready(tampered)

        contradictory = deepcopy(mapped)
        contradictory.one("ReadyPresentationPackageRecord").extensions[0]["payload"]["legacy_evidence_identities"]["candidate"] = "legacy-evidence:contradiction"
        with self.assertRaisesRegex(CompatibilityRejected, "contradictory"):
            verify_mapped_legacy_ready(contradictory)

        wrong_policy = deepcopy(mapped)
        wrong_policy.one("ValidationJudgmentRecord").semantic["policy_id"] = "policy:unregistered"
        for record in (
            wrong_policy.one("ValidationJudgmentRecord"),
            wrong_policy.one("ReadyPresentationPackageRecord"),
        ):
            record.extensions[0]["payload"]["policy_translation"]["bcrp_policy_identity"] = "policy:unregistered"
        with self.assertRaisesRegex(CompatibilityRejected, "policy"):
            verify_mapped_legacy_ready(wrong_policy)

    def test_fingerprint_domains_remain_separate_with_explicit_lineage(self):
        *_, mapped = self._map()
        judgment = mapped.one("ValidationJudgmentRecord")
        extension = judgment.extensions[0]
        lineage = extension["payload"]["fingerprint_lineage"]
        self.assertEqual(lineage["legacy_domain"], "legacy-candidate-semantic")
        self.assertEqual(lineage["bcrp_domain"], "candidate-semantic")
        self.assertEqual(lineage["relationship"], "explicit-governed-mapping")
        self.assertNotEqual(lineage["legacy_digest"], lineage["bcrp_digest"])

    def test_missing_bcrp_semantic_material_is_rejected_not_inferred(self):
        candidate, judgment, ready = self._legacy_closure()
        bcrp = self._bcrp_candidate()
        mapping = replace(self._mapping(candidate, bcrp), all_bcrp_semantic_material_explicit=False)
        with self.assertRaisesRegex(CompatibilityRejected, "semantic material"):
            map_legacy_ready_to_bcrp(
                legacy_candidate=candidate,
                legacy_judgment=judgment,
                legacy_ready=ready,
                bcrp_candidate_bundle=bcrp,
                mapping=mapping,
            )

    def test_mapped_ready_grants_no_release_renderer_artifact_or_manifest_authority(self):
        *_, mapped = self._map()
        prohibited = (
            "PublicationReleaseRecord",
            "RendererCapabilityDeclarationRecord",
            "RendererCompatibilityPlanRecord",
            "GeneratedArtifactAuditRecord",
            "SemanticArtifactConformanceRecord",
            "PublicationManifestRecord",
        )
        self.assertTrue(all(not mapped.records_of_kind(kind) for kind in prohibited))
        payload = mapped.one("ReadyPresentationPackageRecord").extensions[0]["payload"]
        self.assertEqual(payload["status"], "mapped-governed-ready-representation")
        self.assertEqual(payload["downstream_eligibility"], "explicit-compatibility-verifiers-only")
        self.assertEqual(payload["excluded_authorities"], ["publication-release", "renderer", "artifact", "manifest"])

    def test_actual_task039_evidence_fails_closed_without_historical_lifecycle_times(self):
        root = PROJECT_ROOT / "artifacts/presentations/TASK-039-demographic-correlation-browser-report"
        candidate_doc = json.loads((root / "candidate_presentation_package.json").read_text())
        judgment_doc = json.loads((root / "validation_judgment.json").read_text())
        ready_doc = json.loads((root / "ready_presentation_package.json").read_text())

        candidate = CandidatePresentationPackage(
            identity=PackageIdentity(**candidate_doc["identity"]),
            organizing_purpose=OrganizingPurpose(**candidate_doc["organizing_purpose"]),
            statements=tuple(
                PresentationStatement(
                    statement_id=item["statement_id"],
                    encounter_meaning=item["encounter_meaning"],
                    belongs_to_purpose=item["belongs_to_purpose"],
                    encounter_semantics=EncounterSemantics(**item["encounter_semantics"]),
                    upstream_reference_ids=tuple(item["upstream_reference_ids"]),
                    obligation_ids=tuple(item["obligation_ids"]),
                )
                for item in candidate_doc["statements"]
            ),
            upstream_references=tuple(UpstreamReference(**item) for item in candidate_doc["upstream_references"]),
            obligations=tuple(
                PresentationObligation(
                    obligation_id=item["obligation_id"],
                    category=item["category"],
                    requirement=item["requirement"],
                    applies_to=tuple(item["applies_to"]),
                )
                for item in candidate_doc["obligations"]
            ),
        )
        judgment = ValidationJudgment(
            valid=judgment_doc["valid"],
            candidate_package_id=judgment_doc["candidate_package_id"],
            candidate_semantic_fingerprint=judgment_doc["candidate_semantic_fingerprint"],
            validation_policy_id=judgment_doc["validation_policy_id"],
            findings=(),
        )
        ready = ReadyPresentationPackage(
            candidate=candidate,
            validation_judgment=judgment,
            semantic_fingerprint=ready_doc["semantic_fingerprint"],
            validation_policy_id=ready_doc["validation_policy_id"],
        )

        source = load_case(CASE_IDS[0])
        draft = lambda kind: RecordDraft(  # noqa: E731
            identity=source.one(kind).identity,
            semantic=deepcopy(source.one(kind).semantic),
            extensions=deepcopy(source.one(kind).extensions),
        )
        bcrp = author_candidate_bundle(
            brief=draft("PresentationBriefRecord"),
            material=draft("PortablePresentationMaterialRecord"),
            candidate=draft("CandidatePresentationPackageRecord"),
        )
        mapping = self._mapping(candidate, bcrp, suffix="historical-evidence")
        mapping = replace(
            mapping,
            evidence=replace(
                mapping.evidence,
                legacy_candidate_evidence_identity="artifact:TASK-039-candidate",
                legacy_judgment_evidence_identity="artifact:TASK-039-judgment",
                legacy_ready_evidence_identity="artifact:TASK-039-ready",
                validation_time="",
                readiness_time="",
            ),
        )

        self.assertNotIn("validation_time", judgment_doc)
        self.assertNotIn("readiness_time", ready_doc)
        self.assertNotIn("judgment_identity", judgment_doc)
        self.assertNotIn("ready_identity", ready_doc)
        with self.assertRaisesRegex(CompatibilityRejected, "timestamps"):
            map_legacy_ready_to_bcrp(
                legacy_candidate=candidate,
                legacy_judgment=judgment,
                legacy_ready=ready,
                bcrp_candidate_bundle=bcrp,
                mapping=mapping,
            )

    def test_bcrp_core_import_remains_independent_of_legacy_and_renderer_modules(self):
        script = """
import sys
import briefforge.bcrp
forbidden = ('briefforge.runtime', 'briefforge.validation', 'briefforge.promotion',
             'briefforge.downstream', 'briefforge.renderer', 'briefforge.bcrp_legacy_compatibility')
print([name for name in forbidden if name in sys.modules])
"""
        result = subprocess.run(
            [sys.executable, "-B", "-c", script],
            cwd=PROJECT_ROOT,
            env={"PYTHONPATH": str(SRC), "PYTHONDONTWRITEBYTECODE": "1"},
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "[]")


if __name__ == "__main__":
    unittest.main()
