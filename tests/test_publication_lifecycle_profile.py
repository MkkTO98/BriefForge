from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import tempfile
import unittest

from briefforge.bcrp import BCRPBundle, BCRPRecord, fingerprint_bundle, load_bundle as load_bcrp_bundle, validate_bundle
from briefforge.publication_lifecycle import (
    BUNDLE_FORMAT,
    CANONICALIZATION_ID,
    PROFILE_ID,
    PROFILE_VERSION,
    LifecycleBundle,
    LifecyclePolicy,
    ReleaseBinding,
    canonical_event_bytes,
    derive_current_state,
    event_from_document,
    fingerprint_event,
    load_bundle,
    validate_lifecycle,
)
from briefforge.publication_lifecycle.loader import LifecycleLoadError

ROOT = Path(__file__).resolve().parent
CORPUS_PATH = ROOT / "fixtures" / "publication_lifecycle" / "corpus.json"


def release(
    identity: str,
    digest: str,
    *,
    publication: str = "publication:orchard-climate-brief",
    version: str = "1.0.0",
    time: str = "2026-01-10T09:00:00Z",
) -> ReleaseBinding:
    return ReleaseBinding(
        identity=identity,
        fingerprint=digest,
        fingerprint_domain="release-semantic",
        fingerprint_profile_identity="briefforge-core-representation-profile",
        fingerprint_profile_version="1.0.0",
        fingerprint_canonicalization="bcrp-semantic-canonicalization:1.0.0",
        fingerprint_algorithm="sha256",
        fingerprint_root_identity=identity,
        publication_identity=publication,
        semantic_publication_version=version,
        publication_time=time,
    )


def event_document(
    identity: str = "lifecycle-event:orchard-correction",
    *,
    event_type: str = "supersession",
    target_identity: str = "release:orchard-v1",
    target_fingerprint: str = "a" * 64,
    predecessor_identity: str | None = "release:orchard-v1",
    predecessor_fingerprint: str | None = "a" * 64,
    successor_identity: str | None = "release:orchard-v2",
    successor_fingerprint: str | None = "b" * 64,
    reason: str = "correction",
    time: str = "2026-02-10T10:00:00+01:00",
    predecessor_events: list[str] | None = None,
) -> dict:
    semantic = {
        "publication_identity": "publication:orchard-climate-brief",
        "event_type": event_type,
        "target_release": {"identity": target_identity, "fingerprint": target_fingerprint},
        "reason_classification": reason,
        "reason_detail": "A governed evidence correction required a new semantic release.",
        "authority": {
            "identity": "authority-assertion:publication-council",
            "owner": "authority-owner:publication-council",
            "role": "publication-lifecycle-authority",
        },
        "policy_identity": "lifecycle-policy:editorial-2026",
        "event_time": time,
        "predecessor_event_refs": predecessor_events or [],
        "distribution_consequence": "predecessor-ineligible-successor-current",
    }
    if predecessor_identity is not None:
        semantic["predecessor_release"] = {"identity": predecessor_identity, "fingerprint": predecessor_fingerprint}
    if successor_identity is not None:
        semantic["successor_release"] = {"identity": successor_identity, "fingerprint": successor_fingerprint}
    return {
        "record_kind": "PublicationLifecycleEventRecord",
        "identity": identity,
        "profile": {"identity": PROFILE_ID, "version": PROFILE_VERSION},
        "semantic": semantic,
        "extensions": [],
    }


def withdrawal_document(
    identity: str = "lifecycle-event:orchard-withdrawal",
    *,
    target_identity: str = "release:orchard-v2",
    target_fingerprint: str = "b" * 64,
    time: str = "2026-03-01T10:00:00Z",
    predecessor_events: list[str] | None = None,
) -> dict:
    document = event_document(
        identity,
        event_type="withdrawal",
        target_identity=target_identity,
        target_fingerprint=target_fingerprint,
        predecessor_identity=None,
        predecessor_fingerprint=None,
        successor_identity=None,
        successor_fingerprint=None,
        reason="authority-withdrawal",
        time=time,
        predecessor_events=predecessor_events,
    )
    document["semantic"]["reason_detail"] = "Publication authority withdrew future active use."
    document["semantic"]["distribution_consequence"] = "target-ineligible-withdrawn"
    return document


def policy() -> LifecyclePolicy:
    return LifecyclePolicy(
        identity="lifecycle-policy:editorial-2026",
        allowed_authorities=(("authority-assertion:publication-council", "authority-owner:publication-council", "publication-lifecycle-authority"),),
        allowed_event_types=("staleness-declaration", "supersession", "withdrawal"),
        allowed_reason_classifications=("authority-withdrawal", "correction", "currency-concern", "replacement"),
        distribution_consequences=(
            ("staleness-declaration", "target-ineligible-stale"),
            ("supersession", "predecessor-ineligible-successor-current"),
            ("withdrawal", "target-ineligible-withdrawn"),
        ),
    )


def validate_documents(documents: list[dict], releases: list[ReleaseBinding]):
    bundle = LifecycleBundle(PROFILE_ID, PROFILE_VERSION, tuple(event_from_document(document) for document in documents))
    return validate_lifecycle(bundle, tuple(releases), (policy(),))


class CompanionProfileDecisionTests(unittest.TestCase):
    def test_profile_is_explicitly_distinct_from_bcrp(self) -> None:
        self.assertEqual(PROFILE_ID, "briefforge-publication-lifecycle-event-profile")
        self.assertEqual(PROFILE_VERSION, "1.0.0")
        self.assertEqual(CANONICALIZATION_ID, "publication-lifecycle-event-canonicalization:1.0.0")
        self.assertEqual(BUNDLE_FORMAT, "briefforge-publication-lifecycle-event-json-bundle-v1")

    def test_event_model_is_frozen(self) -> None:
        event = event_from_document(event_document())
        with self.assertRaises(FrozenInstanceError):
            event.identity = "lifecycle-event:mutated"  # type: ignore[misc]

    def test_unknown_profile_version_fails_closed_at_parser_and_loader(self) -> None:
        document = event_document()
        document["profile"]["version"] = "1.1.0"
        with self.assertRaises(ValueError):
            event_from_document(document)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "events").mkdir()
            (root / "events" / "event.json").write_text(json.dumps(event_document()), encoding="utf-8")
            (root / "bundle.json").write_text(
                json.dumps(
                    {
                        "format": BUNDLE_FORMAT,
                        "profile": {"identity": PROFILE_ID, "version": "2.0.0"},
                        "events": [{"identity": "lifecycle-event:orchard-correction", "location": "events/event.json"}],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(LifecycleLoadError):
                load_bundle(root)


class CanonicalizationAndAppendOnlyTests(unittest.TestCase):
    def test_event_canonicalization_is_stable_under_order_unicode_offset_and_line_endings(self) -> None:
        left = event_document()
        left["semantic"]["reason_detail"] = "Cafe\u0301\r\ncorrection"
        left["semantic"]["predecessor_event_refs"] = ["lifecycle-event:zeta", "lifecycle-event:alpha"]
        right = json.loads(json.dumps(left, ensure_ascii=False))
        right["semantic"] = dict(reversed(list(right["semantic"].items())))
        right["semantic"]["reason_detail"] = "Café\ncorrection"
        right["semantic"]["event_time"] = "2026-02-10T09:00:00Z"
        right["semantic"]["predecessor_event_refs"] = ["lifecycle-event:alpha", "lifecycle-event:zeta"]
        self.assertEqual(canonical_event_bytes(event_from_document(left)), canonical_event_bytes(event_from_document(right)))
        self.assertEqual(fingerprint_event(event_from_document(left)), fingerprint_event(event_from_document(right)))

    def test_appending_events_changes_no_release_or_earlier_event_fingerprint(self) -> None:
        release_record = BCRPRecord(
            kind="PublicationReleaseRecord",
            identity="release:independent-v1",
            profile_version="1.0.0",
            semantic={
                "publication_lineage_id": "publication:independent",
                "semantic_publication_version": "1.0.0",
                "ready_ref": "ready:independent-v1",
                "ready_fingerprint": "f" * 64,
                "evidence_snapshot_refs": ["snapshot:fixed"],
                "release_authority_ref": "authority:publisher",
                "lifecycle_status": "active",
                "publication_time": "2026-01-01T00:00:00Z",
            },
        )
        bcrp = BCRPBundle("briefforge-core-representation-profile", "1.0.0", (release_record,))
        release_before = fingerprint_bundle(bcrp, domain="release-semantic", require_valid=False).digest
        first = event_from_document(event_document())
        event_before = fingerprint_event(first).digest
        lifecycle = LifecycleBundle(PROFILE_ID, PROFILE_VERSION, (first, event_from_document(withdrawal_document(predecessor_events=[first.identity]))))
        self.assertEqual(release_before, fingerprint_bundle(bcrp, domain="release-semantic", require_valid=False).digest)
        self.assertEqual(event_before, fingerprint_event(lifecycle.events[0]).digest)
        self.assertNotIn("lifecycle", release_record.semantic)

    def test_event_fingerprint_changes_on_authoritative_payload_tampering(self) -> None:
        original = event_from_document(withdrawal_document())
        tampered = withdrawal_document()
        tampered["semantic"]["reason_detail"] = "Different governance reason."
        self.assertNotEqual(fingerprint_event(original).digest, fingerprint_event(event_from_document(tampered)).digest)

    def test_ordered_extension_payloads_remain_semantically_distinct(self) -> None:
        left = event_document()
        left["extensions"] = [{
            "owner_namespace": "sequence.example", "name": "review-sequence", "version": "1.0.0",
            "authority_ref": "authority-assertion:publication-council", "scope": "event",
            "target_refs": [left["identity"]], "criticality": "optional", "character": "semantic",
            "validation_contract": "publication-lifecycle:core-extension-envelope:1.0.0",
            "preservation": "must-preserve", "payload": {"target_refs": ["first", "second"]},
        }]
        right = deepcopy(left)
        right["extensions"][0]["payload"]["target_refs"] = ["second", "first"]
        self.assertNotEqual(fingerprint_event(event_from_document(left)), fingerprint_event(event_from_document(right)))

    def test_unicode_normalized_key_collision_is_rejected(self) -> None:
        document = event_document()
        document["extensions"] = [{
            "owner_namespace": "collision.example", "name": "collision", "version": "1.0.0",
            "authority_ref": "authority-assertion:publication-council", "scope": "event",
            "target_refs": [document["identity"]], "criticality": "optional", "character": "semantic",
            "validation_contract": "publication-lifecycle:core-extension-envelope:1.0.0",
            "preservation": "must-preserve", "payload": {"é": "one", "é": "two"},
        }]
        with self.assertRaises(ValueError):
            canonical_event_bytes(event_from_document(document))

    def test_direct_unsupported_profile_event_cannot_be_fingerprinted(self) -> None:
        event = event_from_document(event_document())
        object.__setattr__(event, "profile_version", "1.1.0")
        with self.assertRaises(ValueError):
            fingerprint_event(event)


class ValidationAndStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.r1 = release("release:orchard-v1", "a" * 64)
        self.r2 = release("release:orchard-v2", "b" * 64, version="2.0.0", time="2026-02-10T08:30:00Z")

    def assertInvalid(self, documents: list[dict], releases: list[ReleaseBinding], code: str) -> None:
        result = validate_documents(documents, releases)
        self.assertTrue(result.blocking)
        self.assertIn(code, {finding.code for finding in result.findings})
        with self.assertRaises(ValueError):
            derive_current_state(
                LifecycleBundle(PROFILE_ID, PROFILE_VERSION, tuple(event_from_document(item) for item in documents)),
                tuple(releases),
                (policy(),),
            )

    def test_initial_release_without_event_is_current(self) -> None:
        bundle = LifecycleBundle(PROFILE_ID, PROFILE_VERSION, ())
        validation = validate_lifecycle(bundle, (self.r1,), (policy(),))
        self.assertFalse(validation.blocking)
        state = derive_current_state(bundle, (self.r1,), (policy(),))
        self.assertEqual(state.current_release_identity, self.r1.identity)
        self.assertEqual(dict(state.release_states), {self.r1.identity: "current"})

    def test_correction_is_supersession_to_a_new_release(self) -> None:
        document = event_document()
        bundle = LifecycleBundle(PROFILE_ID, PROFILE_VERSION, (event_from_document(document),))
        validation = validate_lifecycle(bundle, (self.r1, self.r2), (policy(),))
        self.assertFalse(validation.blocking, validation.findings)
        state = derive_current_state(bundle, (self.r1, self.r2), (policy(),))
        self.assertEqual(state.current_release_identity, self.r2.identity)
        self.assertEqual(dict(state.release_states)[self.r1.identity], "superseded")

    def test_successor_can_be_withdrawn_without_mutating_releases(self) -> None:
        first = event_document()
        second = withdrawal_document(predecessor_events=[first["identity"]])
        before = (self.r1, self.r2)
        bundle = LifecycleBundle(PROFILE_ID, PROFILE_VERSION, (event_from_document(second), event_from_document(first)))
        self.assertFalse(validate_lifecycle(bundle, before, (policy(),)).blocking)
        state = derive_current_state(bundle, before, (policy(),))
        self.assertIsNone(state.current_release_identity)
        self.assertEqual(dict(state.release_states)[self.r2.identity], "withdrawn")
        self.assertEqual(before, (self.r1, self.r2))

    def test_required_fail_closed_variants(self) -> None:
        variants: list[tuple[str, list[dict], list[ReleaseBinding], str]] = []

        unknown_type = event_document(); unknown_type["semantic"]["event_type"] = "expiration"
        variants.append(("unknown type", [unknown_type], [self.r1, self.r2], "unsupported-event-type"))
        missing_id = event_document(); missing_id["identity"] = ""
        variants.append(("missing identity", [missing_id], [self.r1, self.r2], "invalid-event-identity"))
        for field, code in (("authority", "missing-authority"), ("policy_identity", "missing-policy"), ("event_time", "invalid-event-time"), ("target_release", "missing-target-release")):
            item = event_document(); del item["semantic"][field]
            variants.append((f"missing {field}", [item], [self.r1, self.r2], code))
        missing_role = event_document(); del missing_role["semantic"]["authority"]["role"]
        variants.append(("missing role", [missing_role], [self.r1, self.r2], "missing-authority"))
        wrong_digest = event_document(); wrong_digest["semantic"]["target_release"]["fingerprint"] = "c" * 64
        variants.append(("fingerprint mismatch", [wrong_digest], [self.r1, self.r2], "release-fingerprint-mismatch"))
        unknown_release = withdrawal_document(target_identity="release:absent", target_fingerprint="c" * 64)
        variants.append(("unknown withdrawal", [unknown_release], [self.r1], "unknown-release"))
        no_successor = event_document(successor_identity=None, successor_fingerprint=None)
        variants.append(("correction without release", [no_successor], [self.r1], "missing-successor-release"))
        self_edge = event_document(successor_identity=self.r1.identity, successor_fingerprint=self.r1.fingerprint)
        variants.append(("self supersession", [self_edge], [self.r1], "self-supersession"))
        duplicate = event_document()
        variants.append(("duplicate event identity", [duplicate, deepcopy(duplicate)], [self.r1, self.r2], "duplicate-event-identity"))
        required_ext = event_document(); required_ext["extensions"] = [{
            "owner_namespace": "example.invalid", "name": "unknown-authority", "version": "1.0.0",
            "authority_ref": "authority-assertion:publication-council", "scope": "event",
            "target_refs": [required_ext["identity"]], "criticality": "required", "character": "semantic",
            "validation_contract": "example:unknown:1.0.0", "preservation": "must-preserve", "payload": {"grant": True},
        }]
        variants.append(("required extension", [required_ext], [self.r1, self.r2], "unknown-required-extension"))
        unauthorized = event_document(); unauthorized["semantic"]["authority"]["owner"] = "authority-owner:intruder"
        variants.append(("unauthorized", [unauthorized], [self.r1, self.r2], "unauthorized-event-authority"))
        time_bad = event_document(time="2026-01-01T00:00:00Z")
        variants.append(("time before successor", [time_bad], [self.r1, self.r2], "event-before-release"))

        for label, documents, bindings, code in variants:
            with self.subTest(label=label):
                self.assertInvalid(documents, bindings, code)

    def test_cross_publication_cycle_competition_conflict_and_ambiguity_fail_closed(self) -> None:
        foreign = release("release:foreign-v2", "c" * 64, publication="publication:foreign", version="2.0.0")
        cross = event_document(successor_identity=foreign.identity, successor_fingerprint=foreign.fingerprint)
        self.assertInvalid([cross], [self.r1, foreign], "cross-publication-release")

        reverse = event_document(
            "lifecycle-event:reverse",
            target_identity=self.r2.identity,
            target_fingerprint=self.r2.fingerprint,
            predecessor_identity=self.r2.identity,
            predecessor_fingerprint=self.r2.fingerprint,
            successor_identity=self.r1.identity,
            successor_fingerprint=self.r1.fingerprint,
            reason="replacement",
            time="2026-03-01T00:00:00Z",
            predecessor_events=["lifecycle-event:orchard-correction"],
        )
        self.assertInvalid([event_document(), reverse], [self.r1, self.r2], "supersession-cycle")

        r3 = release("release:orchard-v3", "c" * 64, version="3.0.0", time="2026-02-11T08:30:00Z")
        competitor = event_document(
            "lifecycle-event:competitor", successor_identity=r3.identity, successor_fingerprint=r3.fingerprint,
            reason="replacement", time="2026-02-12T09:00:00Z",
        )
        self.assertInvalid([event_document(), competitor], [self.r1, self.r2, r3], "competing-successor")

        withdrawal = withdrawal_document(target_identity=self.r1.identity, target_fingerprint=self.r1.fingerprint)
        self.assertInvalid([event_document(), withdrawal], [self.r1, self.r2], "conflicting-terminal-events")

        self.assertInvalid([], [self.r1, self.r2], "ambiguous-current-release")

    def test_causal_time_and_position_contradictions_fail_closed(self) -> None:
        first = event_document()
        early = withdrawal_document(time="2026-02-10T08:59:59Z", predecessor_events=[first["identity"]])
        self.assertInvalid([first, early], [self.r1, self.r2], "event-time-contradiction")

        a = withdrawal_document("lifecycle-event:a", target_identity=self.r2.identity, target_fingerprint=self.r2.fingerprint, predecessor_events=[first["identity"]])
        b = withdrawal_document("lifecycle-event:b", target_identity=self.r2.identity, target_fingerprint=self.r2.fingerprint, predecessor_events=[first["identity"]])
        self.assertInvalid([first, a, b], [self.r1, self.r2], "ambiguous-event-position")

    def test_optional_extension_is_preserved_but_grants_no_authority(self) -> None:
        document = event_document()
        document["extensions"] = [{
            "owner_namespace": "notes.example", "name": "review-note", "version": "1.0.0",
            "authority_ref": "authority-assertion:publication-council", "scope": "event",
            "target_refs": [document["identity"]], "criticality": "optional", "character": "semantic",
            "validation_contract": "publication-lifecycle:core-extension-envelope:1.0.0",
            "preservation": "must-preserve", "payload": {"note": "Retained, not authoritative."},
        }]
        self.assertFalse(validate_documents([document], [self.r1, self.r2]).blocking)
        altered = deepcopy(document); altered["extensions"][0]["payload"]["note"] = "Changed note."
        self.assertNotEqual(fingerprint_event(event_from_document(document)), fingerprint_event(event_from_document(altered)))
        no_authority = deepcopy(document); del no_authority["semantic"]["authority"]
        self.assertInvalid([no_authority], [self.r1, self.r2], "missing-authority")

    def test_version_labels_do_not_infer_supersession(self) -> None:
        older_label_later_time = release("release:orchard-v0-label", "d" * 64, version="0.1.0", time="2026-04-01T00:00:00Z")
        self.assertInvalid([], [self.r1, older_label_later_time], "ambiguous-current-release")

    def test_mutated_predecessor_binding_is_rejected(self) -> None:
        mutated = release(self.r1.identity, "d" * 64)
        self.assertInvalid([event_document()], [mutated, self.r2], "release-fingerprint-mismatch")

    def test_multihop_state_is_invariant_under_all_input_permutations(self) -> None:
        import itertools

        r3 = release("release:orchard-v3", "c" * 64, version="3.0.0", time="2026-03-01T08:30:00Z")
        first = event_document()
        second = event_document(
            "lifecycle-event:orchard-second-replacement",
            target_identity=self.r2.identity,
            target_fingerprint=self.r2.fingerprint,
            predecessor_identity=self.r2.identity,
            predecessor_fingerprint=self.r2.fingerprint,
            successor_identity=r3.identity,
            successor_fingerprint=r3.fingerprint,
            reason="replacement",
            time="2026-03-01T09:00:00Z",
            predecessor_events=[first["identity"]],
        )
        for events in itertools.permutations((first, second)):
            for bindings in itertools.permutations((self.r1, self.r2, r3)):
                with self.subTest(events=[item["identity"] for item in events], releases=[item.identity for item in bindings]):
                    bundle = LifecycleBundle(PROFILE_ID, PROFILE_VERSION, tuple(event_from_document(item) for item in events))
                    result = validate_lifecycle(bundle, bindings, (policy(),))
                    self.assertFalse(result.blocking, result.findings)
                    self.assertEqual(derive_current_state(bundle, bindings, (policy(),)).current_release_identity, r3.identity)

    def test_release_catalog_cannot_manufacture_unlinked_current_authority(self) -> None:
        withdrawal = withdrawal_document(target_identity=self.r1.identity, target_fingerprint=self.r1.fingerprint)
        self.assertInvalid([withdrawal], [self.r1, self.r2], "release-graph-root-cardinality")
        self.assertInvalid([], [], "empty-release-catalog")

    def test_authority_identity_and_reason_matrix_fail_closed(self) -> None:
        unknown_identity = event_document()
        unknown_identity["semantic"]["authority"]["identity"] = "authority-assertion:attacker"
        self.assertInvalid([unknown_identity], [self.r1, self.r2], "unauthorized-event-authority")
        wrong_reason = event_document(reason="authority-withdrawal")
        self.assertInvalid([wrong_reason], [self.r1, self.r2], "invalid-event-reason")

    def test_cross_publication_causal_event_is_rejected(self) -> None:
        foreign_publication = "publication:foreign-causal"
        foreign_release = release("release:foreign-causal", "c" * 64, publication=foreign_publication)
        foreign_event = withdrawal_document("lifecycle-event:foreign-withdrawal", target_identity=foreign_release.identity, target_fingerprint=foreign_release.fingerprint)
        foreign_event["semantic"]["publication_identity"] = foreign_publication
        local_event = event_document(predecessor_events=[foreign_event["identity"]])
        self.assertInvalid([foreign_event, local_event], [foreign_release, self.r1, self.r2], "cross-publication-event")

    def test_malformed_and_undeclared_input_is_rejected_at_admission(self) -> None:
        malformed: list[dict] = []
        item = event_document(); item["extensions"] = {"not": "a-list"}; malformed.append(item)
        item = event_document(); item["extensions"] = ["not-an-object"]; malformed.append(item)
        item = event_document(); item["semantic"]["predecessor_event_refs"] = "not-a-list"; malformed.append(item)
        item = event_document(); item["semantic"]["undeclared_authority"] = True; malformed.append(item)
        item = event_document(); item["unexpected"] = "discard-me"; malformed.append(item)
        item = event_document(); item["semantic"]["target_release"]["identity"] = 17; malformed.append(item)
        for document in malformed:
            with self.subTest(document=document):
                with self.assertRaises(ValueError):
                    event_from_document(document)

    def test_release_binding_version_and_semantic_version_fail_closed(self) -> None:
        unsupported = ReleaseBinding(**{**self.r1.__dict__, "fingerprint_profile_version": "1.99.0"})
        self.assertInvalid([], [unsupported], "invalid-release-binding")
        missing_semantic_version = ReleaseBinding(**{**self.r1.__dict__, "semantic_publication_version": ""})
        self.assertInvalid([], [missing_semantic_version], "invalid-release-binding")

    def test_required_extension_needs_an_understood_semantic_contract(self) -> None:
        document = event_document()
        document["extensions"] = [{
            "owner_namespace": "unknown.example", "name": "authority-override", "version": "1.0.0",
            "authority_ref": "authority-assertion:publication-council", "scope": "event",
            "target_refs": [document["identity"]], "criticality": "required", "character": "semantic",
            "validation_contract": "publication-lifecycle:core-extension-envelope:1.0.0",
            "preservation": "must-preserve", "payload": {"grant": True},
        }]
        self.assertInvalid([document], [self.r1, self.r2], "unknown-required-extension")

    def test_withdrawal_and_staleness_cannot_compete_by_input_order(self) -> None:
        withdrawal = withdrawal_document(target_identity=self.r1.identity, target_fingerprint=self.r1.fingerprint)
        stale = withdrawal_document("lifecycle-event:orchard-stale", target_identity=self.r1.identity, target_fingerprint=self.r1.fingerprint, time="2026-03-02T10:00:00Z")
        stale["semantic"]["event_type"] = "staleness-declaration"
        stale["semantic"]["reason_classification"] = "currency-concern"
        stale["semantic"]["distribution_consequence"] = "target-ineligible-stale"
        self.assertInvalid([withdrawal, stale], [self.r1], "conflicting-terminal-events")


class BCRPConformanceCorrectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = load_bcrp_bundle(ROOT / "fixtures" / "bcrp" / "case-1-demographic-correlation-publication")

    def mutated_bundle(self, records: tuple[BCRPRecord, ...]) -> BCRPBundle:
        return BCRPBundle(
            self.bundle.profile_identity,
            self.bundle.profile_version,
            records,
            index=self.bundle.index,
            source_root=self.bundle.source_root,
        )

    def test_unknown_release_lifecycle_state_is_rejected_even_if_manifest_agrees(self) -> None:
        records = []
        for source in self.bundle.records:
            record = BCRPRecord.from_document(source.to_document())
            if record.kind in {"PublicationReleaseRecord", "PublicationManifestRecord"}:
                record.semantic["lifecycle_status"] = "future-mystery-state"
            records.append(record)
        result = validate_bundle(self.mutated_bundle(tuple(records)))
        self.assertIn("Unsupported core Release lifecycle state", " ".join(f.message for f in result.findings))

    def test_undeclared_embedded_lifecycle_events_are_rejected(self) -> None:
        records = []
        for source in self.bundle.records:
            record = BCRPRecord.from_document(source.to_document())
            if record.kind == "PublicationReleaseRecord":
                record.semantic["lifecycle_events"] = [{"event_type": "withdrawal"}]
            records.append(record)
        result = validate_bundle(self.mutated_bundle(tuple(records)))
        self.assertIn("cannot grant lifecycle authority", " ".join(f.message for f in result.findings))

    def test_multiple_release_roots_receive_explicit_l3_and_l4_findings(self) -> None:
        release_record = self.bundle.one("PublicationReleaseRecord")
        duplicate = BCRPRecord.from_document(release_record.to_document())
        duplicate.identity = "release:second-root"
        result = validate_bundle(self.mutated_bundle(self.bundle.records + (duplicate,)))
        layers = {finding.layer for finding in result.findings if finding.family == "lifecycle-release-cardinality"}
        self.assertEqual(layers, {"L3", "L4"})

    def test_optional_extension_is_preserved_but_does_not_set_governed_state(self) -> None:
        release_record = self.bundle.one("PublicationReleaseRecord")
        record = BCRPRecord.from_document(release_record.to_document())
        record.extensions.append({
            "owner_namespace": "notes.example", "name": "lifecycle-note", "version": "1.0.0",
            "authority_ref": "authority:publication", "scope": "release", "target_refs": [record.identity],
            "criticality": "optional", "character": "semantic",
            "validation_contract": "bcrp:core-extension-envelope:1.0.0", "preservation": "must-preserve",
            "payload": {"claimed_status": "withdrawn"},
        })
        records = tuple(record if item.identity == release_record.identity else item for item in self.bundle.records)
        result = validate_bundle(self.mutated_bundle(records))
        self.assertFalse(any("claimed_status" in finding.location for finding in result.findings))
        self.assertEqual(record.semantic["lifecycle_status"], "active")


class CorpusProofTests(unittest.TestCase):
    REQUIRED_VALID = {"initial-release-only", "correction-supersession", "successor-withdrawn", "multi-hop-supersession"}
    REQUIRED_INVALID = {
        "unknown-profile-version", "unknown-event-type", "missing-event-identity", "missing-authority",
        "missing-policy", "missing-role", "missing-event-time", "missing-target-release", "target-fingerprint-mismatch",
        "cross-publication-successor", "correction-without-new-release", "self-supersession", "supersession-cycle",
        "competing-successors", "conflicting-events", "withdrawal-unknown-release", "withdrawal-payload-tampering",
        "event-time-contradiction", "predecessor-event-contradiction", "version-order-not-authority",
        "mutated-predecessor-release", "duplicate-event-identity", "unknown-required-extension", "ambiguous-current-state",
        "unknown-authority-identity", "wrong-supersession-reason", "disconnected-release-catalog",
        "cross-publication-predecessor-event", "withdrawal-and-staleness-conflict", "malformed-extension-list",
        "undeclared-semantic-key", "unsupported-bcrp-profile-version", "empty-release-catalog",
    }

    def test_generalized_corpus_declares_independent_expectations(self) -> None:
        corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
        valid_ids = {case["id"] for case in corpus["cases"] if case["expected_valid"]}
        invalid_ids = {case["id"] for case in corpus["cases"] if not case["expected_valid"]}
        self.assertTrue(self.REQUIRED_VALID.issubset(valid_ids))
        self.assertTrue(self.REQUIRED_INVALID.issubset(invalid_ids))
        self.assertTrue(all("expected_finding_codes" in case for case in corpus["cases"]))

    def test_every_corpus_case_matches_declared_validity_and_state(self) -> None:
        corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
        for case in corpus["cases"]:
            with self.subTest(case=case["id"]):
                try:
                    documents = case["events"]
                    events = tuple(event_from_document(item) for item in documents)
                    bundle = LifecycleBundle(PROFILE_ID, PROFILE_VERSION, events)
                    bindings = tuple(ReleaseBinding(**item) for item in case["releases"])
                    result = validate_lifecycle(bundle, bindings, (policy(),))
                    codes = {finding.code for finding in result.findings}
                except (ValueError, TypeError) as exc:
                    result = None
                    codes = {"admission-error"}
                    self.assertFalse(case["expected_valid"], f"valid case raised {exc}")
                self.assertEqual(case["expected_valid"], result is not None and not result.blocking)
                self.assertTrue(set(case["expected_finding_codes"]).issubset(codes))
                if case["expected_valid"]:
                    state = derive_current_state(bundle, bindings, (policy(),))
                    self.assertEqual(case["expected_current_release"], state.current_release_identity)

    def test_independent_renamed_graphs_and_reordered_inputs(self) -> None:
        corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
        valid = [case for case in corpus["cases"] if case["expected_valid"]]
        self.assertGreaterEqual(len({case["publication_domain"] for case in valid}), 3)
        self.assertGreaterEqual(len({tuple(item["semantic_publication_version"] for item in case["releases"]) for case in valid}), 3)
        for case in valid:
            events = tuple(event_from_document(item) for item in reversed(case["events"]))
            releases = tuple(ReleaseBinding(**item) for item in reversed(case["releases"]))
            result = validate_lifecycle(LifecycleBundle(PROFILE_ID, PROFILE_VERSION, events), releases, (policy(),))
            self.assertFalse(result.blocking, (case["id"], result.findings))


if __name__ == "__main__":
    unittest.main()
