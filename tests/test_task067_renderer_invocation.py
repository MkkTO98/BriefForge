"""TASK-067 RED contract: fixed renderer and controlled invocation boundary."""
from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from briefforge_paired_terminal_profile.controlled_invocation import (
    INVOCATION_EVIDENCE_IDENTITY,
    INVOCATION_POLICY_IDENTITY,
    PairedRendererInvocationRejected,
    PairedTerminalRendererInvocationAuthorization,
    compute_paired_invocation_authorization_fingerprint,
    invoke_controlled_paired_renderer, paired_renderer_implementation_digest,
    verify_persisted_paired_renderer_invocation,
)
from briefforge_paired_terminal_profile.renderer import (
    PairedRendererRejected, render_paired_html,
)
from briefforge_paired_terminal_profile.projection import (
    build_paired_editorial_projection, persist_paired_profile_projection_evidence,
)
from briefforge_paired_terminal_profile.profile import (
    PairedUpstreamAdmissionToken,
    verify_full_upstream_paired_terminal_admission,
)
from tests import paired_terminal_fixture as fixture


class Task067RendererInvocationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        semantics = fixture.complete_semantics()
        self.upstream_admission = fixture.admitted_semantics(semantics)
        self.projection = build_paired_editorial_projection(
            admitted=self.upstream_admission)
        projection_evidence_directory = self.root / "projection-evidence"
        projection_evidence_directory.mkdir()
        self.projection_evidence = persist_paired_profile_projection_evidence(
            projection=self.projection, upstream_admission=self.upstream_admission,
            evidence_directory=projection_evidence_directory.resolve(),
            evidence_filename="profile-projection.json")

    def authorization(self, **changes):
        output = self.root / f"output-{len(tuple(self.root.glob('output-*')))}"
        evidence = self.root / f"evidence-{len(tuple(self.root.glob('evidence-*')))}"
        ledger = self.root / f"ledger-{len(tuple(self.root.glob('ledger-*')))}"
        output.mkdir(); evidence.mkdir(); ledger.mkdir()
        values = dict(
            identity="invocation-authorization:synthetic-paired",
            policy_identity=INVOCATION_POLICY_IDENTITY,
            evidence_identity=INVOCATION_EVIDENCE_IDENTITY,
            authorization_time="2026-08-02T10:00:00Z",
            release_identity=self.projection.release_identity,
            release_fingerprint=self.projection.release_fingerprint,
            lifecycle_scope_fingerprint=self.projection.lifecycle_scope_fingerprint,
            plan_identity=self.projection.plan_identity,
            plan_fingerprint=self.projection.plan_fingerprint,
            capability_declaration_identity=self.projection.capability_declaration_identity,
            capability_declaration_fingerprint=self.projection.capability_declaration_fingerprint,
            profile_identity=fixture.PROFILE_ID,
            profile_version=fixture.PROFILE_VERSION,
            schema_identity=fixture.SCHEMA_ID,
            schema_version=fixture.SCHEMA_VERSION,
            projection_fingerprint=self.projection.projection_fingerprint,
            renderer_identity=fixture.RENDERER_ID,
            renderer_version=fixture.RENDERER_VERSION,
            renderer_implementation_digest=paired_renderer_implementation_digest(),
            output_directory=str(output.resolve()), output_filename="paired.html",
            evidence_directory=str(evidence.resolve()), evidence_filename="invocation.json",
            authorization_ledger_directory=str(ledger.resolve()),
            output_count=1, maximum_output_bytes=1_000_000,
            media_type="text/html", invocation_mode="deterministic-replay",
            environment=(("LANG", "C"), ("LC_ALL", "C"), ("TZ", "UTC"),
                         ("PYTHONDONTWRITEBYTECODE", "1"), ("PYTHONHASHSEED", "0"),
                         ("PYTHONUTF8", "1")),
            external_assets=(), fingerprint="",
        )
        values.update(changes)
        provisional = PairedTerminalRendererInvocationAuthorization(**values)
        return replace(provisional, fingerprint=
                       compute_paired_invocation_authorization_fingerprint(provisional))

    def test_renderer_bytes_are_deterministic_one_table_seven_owned_rows(self):
        first = render_paired_html(self.projection)
        second = render_paired_html(self.projection)
        self.assertIs(type(first), bytes)
        self.assertEqual(first, second)
        text = first.decode("utf-8")
        self.assertEqual(text.count("<table"), 1)
        self.assertEqual(text.count("<thead"), 1)
        self.assertEqual(text.count("<tbody"), 1)
        self.assertEqual(text.count("<th"), 5)
        self.assertEqual(text.count("<tbody") and text.split("<tbody", 1)[1].count("<tr"), 7)
        for heading in fixture.COLUMN_HEADINGS:
            self.assertIn(heading, text)
        for row in self.projection.table.rows:
            self.assertEqual(text.count(f'<tr id="{row.identity}"'), 1)
            self.assertIn(row.relationship_identity, text)

    def test_exact_lexicals_states_periods_counts_and_pair_slot_ownership_render(self):
        html = render_paired_html(self.projection).decode("utf-8")
        by_id = {value.identity: value for value in self.projection.values}
        for row in self.projection.table.rows:
            raw, difference = by_id[row.raw_value_ref], by_id[row.first_difference_value_ref]
            start = html.index(row.identity)
            end = html.index("</tr>", start)
            fragment = html[start:end]
            for expected in (raw.lexical_representation, difference.lexical_representation,
                             "present", "raw", "first_difference", raw.aligned_period,
                             str(raw.aligned_count), difference.aligned_period,
                             str(difference.aligned_count)):
                self.assertIn(expected, fragment)
            self.assertLess(fragment.index(raw.lexical_representation),
                            fragment.index(difference.lexical_representation))

    def test_all_semantic_text_and_identifiers_are_html_escaped(self):
        html = render_paired_html(self.projection).decode("utf-8")
        self.assertNotIn("Synthetic relationship 1 <literal>", html)
        self.assertIn("Synthetic relationship 1 &lt;literal&gt;", html)
        self.assertIn("Authored synthetic statement 1 &amp; retained.", html)
        attack = replace(self.projection.table.rows[0],
                         relationship_label='<script src="https://evil.invalid/x"></script>')
        semantics = fixture.complete_semantics()
        semantics = replace(semantics, table=replace(
            semantics.table, rows=(attack,) + semantics.table.rows[1:]))
        projection = fixture.projection(semantics=semantics)
        attacked_html = render_paired_html(projection).decode("utf-8")
        self.assertNotIn("<script", attacked_html)
        self.assertIn("&lt;script src=&quot;https://evil.invalid/x&quot;&gt;", attacked_html)

    def test_public_renderer_and_invocation_accept_no_callable_template_or_selector(self):
        renderer_parameters = set(inspect.signature(render_paired_html).parameters)
        invocation_parameters = set(inspect.signature(invoke_controlled_paired_renderer).parameters)
        forbidden = {"renderer", "callable", "template", "module", "module_path",
                     "executable", "registry", "plugin", "fallback", "selector"}
        self.assertTrue(forbidden.isdisjoint(renderer_parameters))
        self.assertTrue(forbidden.isdisjoint(invocation_parameters))
        source = inspect.getsource(__import__(
            "briefforge_paired_terminal_profile.controlled_invocation", fromlist=["*"]))
        for token in ("importlib", "entry_points", "eval(", "exec(", "__import__(",
                      "os.environ", "subprocess", "fallback"):
            self.assertNotIn(token, source)

    def test_exact_invocation_authorization_and_versions_required_before_write(self):
        class Subclass(PairedTerminalRendererInvocationAuthorization):
            pass
        valid = self.authorization()
        attacks = (
            object(), Subclass(**valid.__dict__),
            replace(valid, policy_identity="policy:other"),
            replace(valid, renderer_version="latest"),
            replace(valid, schema_version=""),
            replace(valid, projection_fingerprint="0" * 64),
            replace(valid, external_assets=("https://example.invalid/a.css",)),
            replace(valid, output_count=2),
        )
        for attack in attacks:
            before = set(self.root.rglob("*"))
            with self.subTest(attack=type(attack)), self.assertRaises(PairedRendererInvocationRejected):
                invoke_controlled_paired_renderer(
                    projection=self.projection, authorization=attack,
                    upstream_admission=self.upstream_admission,
                    projection_evidence=self.projection_evidence)
            self.assertEqual(set(self.root.rglob("*")), before)

    def test_upstream_token_is_mandatory_opaque_and_fail_closed_before_write(self):
        authorization = self.authorization()
        before = set(self.root.rglob("*"))
        with self.assertRaises(TypeError):
            PairedUpstreamAdmissionToken(
                object(), tuple(fixture.admission_envelope().__dict__.values()),
                self.projection.content_closure_fingerprint,
            )
        forged = object.__new__(PairedUpstreamAdmissionToken)
        object.__setattr__(forged, "_bindings", tuple(fixture.admission_envelope().__dict__.values()))
        object.__setattr__(forged, "_content_closure_fingerprint",
                           self.projection.content_closure_fingerprint)
        object.__setattr__(forged, "_nonce", b"x" * 32)
        for token in (None, fixture.admission_envelope(), forged):
            with self.subTest(token=type(token)), self.assertRaises(PairedRendererInvocationRejected):
                invoke_controlled_paired_renderer(
                    projection=self.projection, authorization=authorization,
                    upstream_admission=token,
                    projection_evidence=self.projection_evidence,
                )
            self.assertEqual(set(self.root.rglob("*")), before)

    def test_success_writes_one_regular_bounded_file_and_reload_verifies_bytes(self):
        authorization = self.authorization()
        import briefforge_paired_terminal_profile.controlled_invocation as controlled
        with patch.object(controlled, "render_paired_html", wraps=render_paired_html) as renderer:
            invoked = invoke_controlled_paired_renderer(
                projection=self.projection, authorization=authorization,
                upstream_admission=self.upstream_admission,
                projection_evidence=self.projection_evidence)
        self.assertEqual(renderer.call_count, 2)
        self.assertEqual(invoked.artifact_bytes, render_paired_html(self.projection))
        self.assertTrue(invoked.artifact_path.is_file())
        self.assertFalse(invoked.artifact_path.is_symlink())
        self.assertEqual(invoked.artifact_path.parent, Path(authorization.output_directory))
        self.assertEqual(tuple(Path(authorization.output_directory).iterdir()),
                         (invoked.artifact_path,))
        reloaded = verify_persisted_paired_renderer_invocation(
            projection=self.projection, authorization=authorization,
            upstream_admission=self.upstream_admission,
            projection_evidence=self.projection_evidence,
            artifact_path=invoked.artifact_path, evidence_path=invoked.evidence_path)
        self.assertEqual(reloaded.fingerprint, invoked.fingerprint)

    def test_directory_swap_after_admission_rejects_before_renderer_or_write(self):
        import briefforge_paired_terminal_profile.controlled_invocation as controlled
        for directory_name in ("output_directory", "evidence_directory"):
            authorization = self.authorization()
            admitted = Path(getattr(authorization, directory_name))
            displaced = admitted.with_name(admitted.name + "-displaced")
            real_open = controlled._open_directory
            swapped = False

            def swap_then_open(path):
                nonlocal swapped
                if path == admitted and not swapped:
                    admitted.rename(displaced)
                    admitted.mkdir()
                    swapped = True
                return real_open(path)

            with self.subTest(directory=directory_name), patch.object(
                    controlled, "_open_directory", side_effect=swap_then_open), patch.object(
                    controlled, "render_paired_html", wraps=render_paired_html) as renderer, patch.object(
                    controlled, "_write_exclusive_at", wraps=controlled._write_exclusive_at) as writer:
                with self.assertRaisesRegex(PairedRendererInvocationRejected, "changed while opening"):
                    invoke_controlled_paired_renderer(
                        projection=self.projection, authorization=authorization,
                        upstream_admission=self.upstream_admission,
                        projection_evidence=self.projection_evidence)
                self.assertEqual(renderer.call_count, 0)
                self.assertEqual(writer.call_count, 0)

    def test_directory_swap_after_open_rejects_instead_of_returning_stale_paths(self):
        import briefforge_paired_terminal_profile.controlled_invocation as controlled
        authorization = self.authorization()
        output = Path(authorization.output_directory)
        evidence = Path(authorization.evidence_directory)
        displaced_output = output.with_name(output.name + "-displaced")
        displaced_evidence = evidence.with_name(evidence.name + "-displaced")
        swapped = False

        def swap_then_render(projection):
            nonlocal swapped
            if not swapped:
                output.rename(displaced_output)
                evidence.rename(displaced_evidence)
                output.mkdir()
                evidence.mkdir()
                swapped = True
            return render_paired_html(projection)

        with patch.object(controlled, "render_paired_html", side_effect=swap_then_render):
            with self.assertRaisesRegex(
                    PairedRendererInvocationRejected, "pathname changed during invocation"):
                invoke_controlled_paired_renderer(
                    projection=self.projection, authorization=authorization,
                    upstream_admission=self.upstream_admission,
                    projection_evidence=self.projection_evidence)
        self.assertEqual(tuple(output.iterdir()), ())
        self.assertEqual(tuple(evidence.iterdir()), ())
        self.assertEqual(tuple(displaced_output.iterdir()), ())
        self.assertEqual(tuple(displaced_evidence.iterdir()), ())

    def test_traversal_symlink_collision_and_auxiliary_output_are_rejected(self):
        outside = self.root / "outside.html"
        for changes in (
            {"output_filename": "../outside.html"},
            {"output_filename": "/tmp/outside.html"},
            {"evidence_filename": "../evidence.json"},
        ):
            authorization = self.authorization(**changes)
            with self.subTest(changes=changes), self.assertRaises(PairedRendererInvocationRejected):
                invoke_controlled_paired_renderer(
                    projection=self.projection, authorization=authorization,
                    upstream_admission=self.upstream_admission,
                    projection_evidence=self.projection_evidence)
        authorization = self.authorization()
        path = Path(authorization.output_directory) / authorization.output_filename
        path.symlink_to(outside)
        with self.assertRaises(PairedRendererInvocationRejected):
            invoke_controlled_paired_renderer(
                projection=self.projection, authorization=authorization,
                upstream_admission=self.upstream_admission,
                    projection_evidence=self.projection_evidence)
        self.assertFalse(outside.exists())

    def test_renderer_exception_or_nondeterminism_emits_no_artifact_or_evidence(self):
        for side_effect in ((RuntimeError("synthetic renderer failure"),),
                            (b"first", b"second")):
            authorization = self.authorization()
            with self.subTest(side_effect=side_effect), patch(
                "briefforge_paired_terminal_profile.controlled_invocation.render_paired_html",
                side_effect=side_effect,
            ), self.assertRaises(PairedRendererInvocationRejected):
                invoke_controlled_paired_renderer(projection=self.projection,
                                                   authorization=authorization,
                                                   upstream_admission=self.upstream_admission,
                    projection_evidence=self.projection_evidence)
            self.assertEqual(tuple(Path(authorization.output_directory).iterdir()), ())
            self.assertEqual(tuple(Path(authorization.evidence_directory).iterdir()), ())

    def test_authorization_is_consumed_once_even_if_outputs_are_deleted(self):
        authorization = self.authorization()
        invoked = invoke_controlled_paired_renderer(
            projection=self.projection, authorization=authorization,
            upstream_admission=self.upstream_admission,
            projection_evidence=self.projection_evidence)
        invoked.artifact_path.unlink(); invoked.evidence_path.unlink()
        import briefforge_paired_terminal_profile.controlled_invocation as controlled
        with patch.object(controlled, "render_paired_html", wraps=render_paired_html) as renderer:
            with self.assertRaises(PairedRendererInvocationRejected):
                invoke_controlled_paired_renderer(
                    projection=self.projection, authorization=authorization,
                    upstream_admission=self.upstream_admission,
                    projection_evidence=self.projection_evidence)
        self.assertEqual(renderer.call_count, 0)
        self.assertEqual(len(tuple(Path(authorization.authorization_ledger_directory).iterdir())), 1)

    def test_copied_matching_bytes_in_replacement_directories_are_rejected(self):
        import shutil
        authorization = self.authorization()
        invoked = invoke_controlled_paired_renderer(
            projection=self.projection, authorization=authorization,
            upstream_admission=self.upstream_admission,
            projection_evidence=self.projection_evidence)
        for value in (authorization.output_directory, authorization.evidence_directory):
            original = Path(value)
            replacement = original.with_name(original.name + "-replacement")
            displaced = original.with_name(original.name + "-displaced")
            shutil.copytree(original, replacement)
            original.rename(displaced); replacement.rename(original)
        with self.assertRaises(PairedRendererInvocationRejected):
            verify_persisted_paired_renderer_invocation(
                projection=self.projection, authorization=authorization,
                upstream_admission=self.upstream_admission,
                projection_evidence=self.projection_evidence,
                artifact_path=invoked.artifact_path, evidence_path=invoked.evidence_path)

    def test_partial_owned_file_is_removed_after_post_create_failure(self):
        import briefforge_paired_terminal_profile.controlled_invocation as controlled
        authorization = self.authorization()
        real_write = controlled._write_exclusive_at
        def write_then_fail(directory, name, data, created):
            real_write(directory, name, data, created)
            if name == authorization.output_filename:
                raise OSError("injected post-create failure")
        with patch.object(controlled, "_write_exclusive_at", side_effect=write_then_fail), \
                self.assertRaises(PairedRendererInvocationRejected):
            invoke_controlled_paired_renderer(
                projection=self.projection, authorization=authorization,
                upstream_admission=self.upstream_admission,
                projection_evidence=self.projection_evidence)
        self.assertEqual(tuple(Path(authorization.output_directory).iterdir()), ())

    def test_cleanup_preserves_foreign_inode_replacing_owned_partial_file(self):
        import briefforge_paired_terminal_profile.controlled_invocation as controlled
        authorization = self.authorization()
        real_write = controlled._write_exclusive_at
        foreign = b"foreign inode must survive"
        def replace_then_fail(directory, name, data, created):
            real_write(directory, name, data, created)
            if name == authorization.output_filename:
                path = Path(authorization.output_directory) / name
                replacement = self.root / "precreated-foreign-inode"
                replacement.write_bytes(foreign)
                replacement.replace(path)
                raise OSError("injected foreign replacement")
        with patch.object(controlled, "_write_exclusive_at", side_effect=replace_then_fail), \
                self.assertRaises(PairedRendererInvocationRejected):
            invoke_controlled_paired_renderer(
                projection=self.projection, authorization=authorization,
                upstream_admission=self.upstream_admission,
                projection_evidence=self.projection_evidence)
        self.assertEqual((Path(authorization.output_directory) /
                          authorization.output_filename).read_bytes(), foreign)


if __name__ == "__main__":
    unittest.main()
