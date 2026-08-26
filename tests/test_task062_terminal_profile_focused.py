"""Focused adversarial tests for the bounded TASK-062 GREEN slice."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from briefforge.bounded_loopback_deployment import DeploymentRouteItem, DeploymentTarget
from briefforge.representative_projection import (
    RepresentativeProjectionRejected,
    admit_representative_release_content,
)
from briefforge.representative_renderer import render_representative_html
from briefforge_terminal_profile.profile import (
    CONTENT_AUTHORITY_ROLE_ALLOWLIST,
    PROFILE_IDENTITY,
    PROFILE_VERSION,
    TERMINAL_OPERATIONAL_IDENTITIES,
    TerminalAuthorityProfile,
    TerminalAuthorityProfileRejected,
    build_terminal_authority_profile,
    verify_material_authority_profile,
    verify_terminal_authority_profile,
)
from briefforge_terminal_profile.projection import (
    ADAPTER_IDENTITY,
    ADAPTER_VERSION,
    PROJECTION_IDENTITY,
    TerminalProjectionRejected,
    build_terminal_representative_projection,
    verify_terminal_projection,
)
from briefforge_terminal_profile.renderer_adapter import (
    adapt_terminal_projection,
    adapter_source_digest,
)
from tests import representative_fixture


class Task062FocusedSliceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        directories = [root / name for name in ("destination", "delivery", "deployment", "verification")]
        for directory in directories:
            directory.mkdir(); directory.chmod(0o700)
        self.target = DeploymentTarget("127.0.0.1", 38127, "http://127.0.0.1:38127")
        self.routes = (DeploymentRouteItem("/brief.html", "brief.html", "text/html"),)
        self.content = dict(
            representative_fixture.CONTENT_AUTHORITY,
            role="presentation-content-authority",
            scope="released-presentation-semantic-content",
        )
        self.profile = build_terminal_authority_profile(
            destination_parent=directories[0], destination_basename="brief.html",
            delivery_ledger=directories[1], target=self.target, routes=self.routes,
            deployment_ledger=directories[2], verification_ledger=directories[3],
            content_authorities=(self.content,),
        )

    def _changed_profile(self, mutate):
        operational = [dict(item) for item in self.profile.operational_authorities]
        content = [dict(item) for item in self.profile.content_authorities]
        mutate(operational, content)
        return TerminalAuthorityProfile(PROFILE_IDENTITY, PROFILE_VERSION,
                                        tuple(operational), tuple(content))

    def assertProfileRejected(self, mutate):
        with self.assertRaises(TerminalAuthorityProfileRejected):
            verify_terminal_authority_profile(self._changed_profile(mutate))

    def test_closed_sets_order_schema_owner_role_scope_and_duplicates_fail(self):
        attacks = (
            lambda o,c: o.pop(),
            lambda o,c: o.append(dict(o[-1])),
            lambda o,c: o.reverse(),
            lambda o,c: o[0].update(id="authority:unknown-operational"),
            lambda o,c: o[0].update(role="unknown-operational-role"),
            lambda o,c: o[0].update(owner_identity="project:Other"),
            lambda o,c: o[0].update(scope="broadened"),
            lambda o,c: o[0].update(extra="extension-bag"),
            lambda o,c: o[0].update(id=o[1]["id"]),
            lambda o,c: o[0].update(role=o[1]["role"]),
            lambda o,c: c[0].update(id=TERMINAL_OPERATIONAL_IDENTITIES[0]),
            lambda o,c: c[0].update(role=o[0]["role"]),
            lambda o,c: c[0].update(role="content"),
            lambda o,c: c.append({**c[0], "id":"authority:aaa"}),
        )
        for attack in attacks:
            with self.subTest(attack=attack): self.assertProfileRejected(attack)
        self.assertEqual(CONTENT_AUTHORITY_ROLE_ALLOWLIST, {"presentation-content-authority"})

    def test_content_cardinality_is_closed_not_residual_minmax(self):
        with self.assertRaises(TerminalAuthorityProfileRejected):
            verify_terminal_authority_profile(TerminalAuthorityProfile(
                PROFILE_IDENTITY, PROFILE_VERSION, self.profile.operational_authorities, ()))
        for count in (8, 17):
            authorities=[dict(x) for x in self.profile.authorities]
            if count == 8:
                authorities = authorities[:8]
            while len(authorities)<count:
                authorities.append({**self.content,"id":f"authority:synthetic-{len(authorities):02d}"})
            with self.subTest(count=count), self.assertRaises(TerminalAuthorityProfileRejected):
                verify_material_authority_profile(authorities, self.profile)
        with self.assertRaises(TerminalAuthorityProfileRejected):
            verify_material_authority_profile([dict(x) for x in self.profile.operational_authorities], self.profile)

    def _chain(self):
        original = representative_fixture.candidate_bundle
        def terminal_candidate(snapshot, *, complete_audience_edge=False):
            bundle=original(snapshot, complete_audience_edge=complete_audience_edge)
            bundle.one("PortablePresentationMaterialRecord").semantic["authorities"] = [
                dict(x) for x in self.profile.authorities
            ]
            return bundle
        with patch.object(representative_fixture, "candidate_bundle", terminal_candidate):
            return representative_fixture.representative_chain(self, "task062-focused")

    def _projection(self):
        inputs=self._chain()
        projection=build_terminal_representative_projection(
            verified_release=inputs[1], evidence_snapshot=inputs[0], lifecycle_scope=inputs[2],
            declaration=inputs[3], planning_authorization=inputs[4], verified_plan=inputs[5],
            authority_profile=self.profile,
        )
        return inputs,projection

    def test_old_profile_rejects_eight_new_rejects_five(self):
        inputs,projection=self._projection()
        with self.assertRaises(RepresentativeProjectionRejected):
            admit_representative_release_content(inputs[1].bundle)
        old=representative_fixture.representative_chain(self,"task062-old")
        with self.assertRaises((TerminalAuthorityProfileRejected,TerminalProjectionRejected)):
            build_terminal_representative_projection(
                verified_release=old[1],evidence_snapshot=old[0],lifecycle_scope=old[2],
                declaration=old[3],planning_authorization=old[4],verified_plan=old[5],
                authority_profile=self.profile)
        self.assertEqual(len(projection.operational_authority_exclusions),8)

    def test_operational_authorities_cannot_appear_on_any_displayed_semantic_edge(self):
        attacks=(
            lambda c,m: c["statements"][0].update(authority_ref=TERMINAL_OPERATIONAL_IDENTITIES[5]),
            lambda c,m: m["values"][0].update(authority_ref=TERMINAL_OPERATIONAL_IDENTITIES[6]),
            lambda c,m: m["provenance"][0].update(authority_ref=TERMINAL_OPERATIONAL_IDENTITIES[7]),
            lambda c,m: c["relations"][0].update(authority_ref=TERMINAL_OPERATIONAL_IDENTITIES[0]),
            lambda c,m: c["obligations"][0].update(authority_ref=TERMINAL_OPERATIONAL_IDENTITIES[1]),
            lambda c,m: c["distribution"].update(authority_ref=TERMINAL_OPERATIONAL_IDENTITIES[2]),
            lambda c,m: c["renderer_requirements"][0]["authority_label_refs"].append(TERMINAL_OPERATIONAL_IDENTITIES[3]),
        )
        for attack in attacks:
            inputs,_=self._projection()
            bundle=deepcopy(inputs[1].bundle)
            candidate=bundle.one("CandidatePresentationPackageRecord").semantic
            material=bundle.one("PortablePresentationMaterialRecord").semantic
            attack(candidate,material)
            with self.subTest(attack=attack), self.assertRaises(Exception):
                from briefforge_terminal_profile.projection import admit_terminal_representative_release_content
                admit_terminal_representative_release_content(bundle,self.profile)

    def test_direct_successor_routing_fails_adapter_is_fixed_deterministic_and_lossless(self):
        _,projection=self._projection()
        self.assertEqual((projection.profile_identity,projection.adapter_identity,projection.adapter_version),
                         (PROJECTION_IDENTITY,ADAPTER_IDENTITY,ADAPTER_VERSION))
        self.assertEqual(projection.adapter_source_digest,adapter_source_digest())
        with self.assertRaises(RepresentativeProjectionRejected):
            render_representative_html(projection)
        first=adapt_terminal_projection(projection); second=adapt_terminal_projection(projection)
        self.assertEqual(first,second)
        self.assertEqual(first.operational_authority_exclusions,projection.operational_authority_exclusions)
        self.assertEqual(len(first.operational_authority_exclusions),8)
        route_fields={"profile_identity","profile_version","renderer_adapter_id","fingerprint"}
        for name in projection.__dataclass_fields__:
            if name not in route_fields and name not in {"adapter_identity","adapter_version","adapter_source_digest"}:
                self.assertEqual(getattr(first,name),getattr(projection,name),name)
        self.assertEqual(render_representative_html(first),render_representative_html(second))

    def test_projection_routing_fingerprint_and_exclusions_fail_closed(self):
        _,projection=self._projection()
        attacks=(
            replace(projection,adapter_identity="adapter:unknown"),
            replace(projection,adapter_version="9.0.0"),
            replace(projection,adapter_source_digest="0"*64),
            replace(projection,fingerprint="0"*64),
            replace(projection,operational_authority_exclusions=projection.operational_authority_exclusions[:5]),
        )
        for attack in attacks:
            with self.subTest(),self.assertRaises(TerminalProjectionRejected):
                verify_terminal_projection(attack)


if __name__ == "__main__": unittest.main()
