"""TASK-053 strict semantic realization conformance boundary.

This boundary independently reloads TASK-052 evidence, derives the required
realization from the persisted governed Release and Plan closure, parses the
exact standalone HTML bytes, and emits only semantic-conformance authority.
It grants no Manifest, distribution, or successful-publication authority.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import stat
from typing import Any

from .bcrp.canonical import canonicalize_timestamp, fingerprint_bundle
from .bcrp.model import BCRPBundle, BCRPRecord, Fingerprint, PROFILE_VERSION
from .bcrp.validation import validate_bundle
from .controlled_renderer_invocation import (
    RendererInvocationAuthorization,
    VerifiedRendererInvocation,
    build_minimal_html_projection,
    renderer_implementation_digest,
    verify_persisted_renderer_invocation,
)
from .publication_release import EvidenceSnapshot, VerifiedPublicationRelease
from .renderer_adapter import MinimalHtmlRendererProjection
from .renderer_compatibility_planning import (
    LifecyclePlanningScope,
    PlanningAuthorization,
    RendererCapabilityDeclaration,
    VerifiedRendererCompatibilityPlan,
)

CONFORMANCE_POLICY_ID = "briefforge-semantic-conformance-assessment-policy:1.0.0"
CONFORMANCE_EVIDENCE_CONTRACT = "briefforge:semantic-artifact-conformance-evidence:1.0.0"
SEMANTIC_REALIZATION_PROFILE_ID = "briefforge-static-html-semantic-realization-profile"
SEMANTIC_REALIZATION_PROFILE_VERSION = "1.0.0"
ASSESSOR_IMPLEMENTATION_ID = "briefforge.semantic_artifact_conformance"
ASSESSOR_IMPLEMENTATION_VERSION = "1.0.0"
OUTPUT_CLASS = "standalone-static-html-semantic-realization"
ACCEPTED_ASSESSOR_IDENTITY = "authority:briefforge-semantic-artifact-conformance"
ACCEPTED_ASSESSOR_OWNER = "project:BriefForge"
ACCEPTED_ASSESSOR_ROLE = "semantic-artifact-conformance-assessor"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_AUTHORIZED_CSS_SHA256 = "26a80ab7cc58198794d665a8b1054422f4f47ae210aa25f5f46fcc523aa37812"
_IDENTITY = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._:-]*$")
_VERIFIED_ADMISSION_MARKER = object()


@dataclass(frozen=True, order=True)
class ConformanceFinding:
    code: str
    location: str
    message: str


@dataclass(frozen=True)
class SemanticArtifactConformanceAuthorization:
    identity: str
    policy_identity: str
    authority_identity: str
    authority_owner: str
    authority_role: str
    authorization_time: str
    profile_identity: str
    profile_version: str
    assessor_identity: str
    release_identity: str
    release_fingerprint: str
    lifecycle_inventory_digest: str
    plan_identity: str
    plan_fingerprint: str
    capability_identity: str
    capability_fingerprint: str
    invocation_authorization_identity: str
    invocation_authorization_fingerprint: str
    invocation_evidence_fingerprint: str
    artifact_identity: str
    artifact_sha256: str
    artifact_filename: str
    artifact_media_type: str
    artifact_byte_length: int
    renderer_identity: str
    renderer_version: str
    renderer_implementation_digest: str
    assessor_implementation: str
    assessor_version: str
    output_class: str
    maximum_artifact_bytes: int
    exclusions: tuple[str, ...]
    artifact_destination: str
    invocation_evidence_destination: str
    evidence_directory: str
    evidence_filename: str
    commitment_ledger_directory: str
    record_identity: str
    fingerprint: str


@dataclass(frozen=True, init=False)
class VerifiedSemanticArtifactConformance:
    _bundle_document: str
    fingerprint: Fingerprint
    _admission_marker: object

    @classmethod
    def _admitted(cls, document: str, fingerprint: Fingerprint) -> "VerifiedSemanticArtifactConformance":
        value = object.__new__(cls)
        object.__setattr__(value, "_bundle_document", document)
        object.__setattr__(value, "fingerprint", fingerprint)
        object.__setattr__(value, "_admission_marker", _VERIFIED_ADMISSION_MARKER)
        return value

    @property
    def bundle(self) -> BCRPBundle:
        return _deserialize_bundle(self._bundle_document)


@dataclass(frozen=True)
class SemanticArtifactConformanceResult:
    findings: tuple[ConformanceFinding, ...]
    verified: VerifiedSemanticArtifactConformance | None

    @property
    def blocked(self) -> bool:
        return self.verified is None


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _serialize_bundle(bundle: BCRPBundle) -> str:
    return _canonical_bytes({
        "profile_identity": bundle.profile_identity,
        "profile_version": bundle.profile_version,
        "records": [record.to_document() for record in bundle.records],
    }).decode("utf-8")


def _deserialize_bundle(text: str) -> BCRPBundle:
    document = json.loads(text)
    if not isinstance(document, dict) or set(document) != {"profile_identity", "profile_version", "records"}:
        raise ValueError("Conformance evidence envelope is malformed.")
    if not isinstance(document["records"], list):
        raise ValueError("Conformance record inventory is malformed.")
    return BCRPBundle(document["profile_identity"], document["profile_version"],
                      tuple(BCRPRecord.from_document(item) for item in document["records"]))


def _authorization_document(value: SemanticArtifactConformanceAuthorization) -> dict[str, Any]:
    document = asdict(value)
    document.pop("fingerprint", None)
    return document


def compute_conformance_authorization_fingerprint(authorization: SemanticArtifactConformanceAuthorization) -> str:
    """Fingerprint every exact authorization and evidence-output binding."""
    return hashlib.sha256(_canonical_bytes(_authorization_document(authorization))).hexdigest()


@dataclass
class _HtmlNode:
    tag: str
    attrs: dict[str, str]
    parent: "_HtmlNode | None"
    text: list[str]
    children: list["_HtmlNode"]
    content: list[Any]

    def all_text(self) -> str:
        parts = [item.all_text() if isinstance(item, _HtmlNode) else item for item in self.content]
        return " ".join("".join(parts).split())


class _StrictStructuralHTMLParser(HTMLParser):
    _VOID = frozenset({"meta"})
    _ALLOWED = frozenset({"html", "head", "meta", "title", "style", "body", "main", "header", "section", "h1", "h2", "h3", "h4", "p", "strong", "div", "article", "span", "ul", "ol", "li", "a", "details", "summary"})
    _URI = frozenset({"src", "srcset", "action", "formaction", "poster", "ping", "background", "cite", "data", "manifest", "xlink:href"})

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[_HtmlNode] = []
        self.nodes: list[_HtmlNode] = []
        self.doctypes = 0
        self.raw_text: list[str] = []

    def handle_decl(self, decl: str) -> None:
        if decl != "doctype html" or self.doctypes:
            raise ValueError("HTML declaration is absent, duplicated, or unauthorized.")
        self.doctypes += 1

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in self._ALLOWED:
            raise ValueError(f"HTML contains active, external, or unsupported element <{tag}>.")
        names = [name.lower() for name, _ in attrs]
        if len(names) != len(set(names)):
            raise ValueError("HTML contains a duplicate attribute.")
        attributes = {name.lower(): value or "" for name, value in attrs}
        allowed = {
            "lang", "charset", "name", "content", "id", "href",
            "data-attention", "data-exhibit-region", "data-grammar",
            "data-grammar-stage", "data-obligation-id", "data-reader-experience",
            "data-reference-id", "data-source-block", "data-source-structure",
            "data-source-tables", "data-statement-id",
        }
        if any(name not in allowed for name in attributes):
            raise ValueError("HTML contains an unsupported attribute.")
        if any(name.startswith("on") for name in attributes) or any(name in self._URI for name in attributes):
            raise ValueError("HTML contains an active or external URI attribute.")
        if "href" in attributes and not re.fullmatch(r"#(?:reference|obligation)-[A-Za-z0-9:._-]+", attributes["href"]):
            raise ValueError("HTML contains an external or spoofed href.")
        if ("hidden" in attributes or "inert" in attributes or attributes.get("aria-hidden", "").lower() == "true"):
            raise ValueError("HTML contains hidden or inert semantic content.")
        parent = self.stack[-1] if self.stack else None
        if parent is None and (tag != "html" or any(node.parent is None for node in self.nodes)):
            raise ValueError("HTML contains a detached or duplicate top-level element.")
        node = _HtmlNode(tag, attributes, parent, [], [], [])
        if parent:
            parent.children.append(node)
            parent.content.append(node)
        self.nodes.append(node)
        if tag not in self._VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in self._VOID:
            raise ValueError("Non-void self-closing HTML is not accepted.")
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if not self.stack or self.stack[-1].tag != tag:
            raise ValueError("HTML element nesting or encounter order is malformed.")
        self.stack.pop()

    def handle_data(self, data: str) -> None:
        if not self.stack and data.strip():
            raise ValueError("HTML contains raw text outside the root element.")
        if self.stack:
            self.stack[-1].text.append(data)
            self.stack[-1].content.append(data)
            if self.stack[-1].tag == "style":
                self.raw_text.append(data)

    def handle_comment(self, data: str) -> None:
        raise ValueError("Comments are unauthorized semantic hiding channels.")

    handle_pi = handle_comment
    unknown_decl = handle_comment

    def finish(self) -> "_StrictStructuralHTMLParser":
        self.close()
        if self.doctypes != 1 or self.stack:
            raise ValueError("HTML is not one complete structurally balanced document.")
        roots = [node for node in self.nodes if node.parent is None]
        if len(roots) != 1 or roots[0].tag != "html":
            raise ValueError("HTML requires exactly one root element.")
        root = roots[0]
        if [node.tag for node in root.children] != ["head", "body"]:
            raise ValueError("HTML requires one ordered head and body under the root.")
        body = root.children[1]
        if len(body.children) != 1 or body.children[0].tag != "main":
            raise ValueError("HTML body requires exactly one bounded main element.")
        ids = [node.attrs["id"] for node in self.nodes if "id" in node.attrs]
        if len(ids) != len(set(ids)):
            raise ValueError("HTML contains duplicate IDs.")
        for attribute in ("data-statement-id", "data-reference-id", "data-obligation-id", "data-long-document-region"):
            values = [node.attrs[attribute] for node in self.nodes if attribute in node.attrs]
            if len(values) != len(set(values)):
                raise ValueError("HTML contains duplicate data identities.")
        css = "".join(self.raw_text)
        if len([node for node in self.nodes if node.tag == "style"]) != 1 or hashlib.sha256(css.encode("utf-8")).hexdigest() != _AUTHORIZED_CSS_SHA256:
            raise ValueError("HTML CSS differs from the bounded supported profile.")
        if re.search(r"@import|url\s*\(|expression\s*\(|display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0(?:\D|$)", css, re.I):
            raise ValueError("HTML CSS is external, active, or hides content.")
        return self


def _parse_exact_html(artifact_bytes: bytes) -> _StrictStructuralHTMLParser:
    if type(artifact_bytes) is not bytes:
        raise ValueError("Exact immutable HTML bytes are required.")
    try:
        text = artifact_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("HTML must be strict UTF-8.") from exc
    if text.encode("utf-8") != artifact_bytes or "\r" in text or "\x00" in text:
        raise ValueError("HTML encoding is not exact canonical UTF-8 with LF line endings.")
    if not text.startswith("<!doctype html>\n") or not text.endswith("</html>"):
        raise ValueError("HTML is not the exact standalone document envelope.")
    parser = _StrictStructuralHTMLParser()
    parser.feed(text)
    return parser.finish()


def _source_block_role(label: str) -> str:
    normalized = label.lower()
    if any(term in normalized for term in ("why not accepted", "missing evidence", "risk", "failure mode", "caveat", "alternative explanation")):
        return "caveat"
    if any(term in normalized for term in ("method", "assumption", "controlled pressure test", "evidence requirement", "activation path")):
        return "methodology"
    if any(term in normalized for term in ("recommendation", "preferred choice", "conclusion", "assessment")):
        return "recommendation"
    return "section"


def _requirement_inventory(projection: MinimalHtmlRendererProjection) -> list[dict[str, str]]:
    """Build stable field requirements without invoking or importing the renderer."""
    requirements: list[dict[str, str]] = []

    def add(source: str, role: str, field: str, value: str) -> None:
        key = {"source": source, "role": role, "field": field}
        requirements.append({
            "id": "semantic-requirement:" + hashlib.sha256(_canonical_bytes(key)).hexdigest(),
            **key,
            "expected": value,
            "outcome": "conformant",
        })

    add(projection.identity.package_id, "meta-package", "content", projection.identity.package_id)
    add(projection.identity.package_id, "title", "text", projection.identity.title)
    add(projection.identity.package_id, "purpose", "statement", projection.organizing_purpose.statement)
    add(projection.identity.package_id, "scope", "purpose_summary", projection.identity.purpose_summary)
    add(projection.identity.package_id, "non-scope", "non_scope", projection.organizing_purpose.non_scope)
    add(projection.identity.package_id, "meta-semantic-fingerprint", "content", projection.semantic_fingerprint)
    add(projection.identity.package_id, "meta-validation-policy", "content", projection.validation_policy_id)
    for item in projection.statements:
        mode = item.encounter_semantics.mode
        normalized = mode.lower()
        stage = (
            "state-main-point" if normalized == "orientation" else
            "close" if normalized == "synthesis" or "conclusion" in normalized else
            "qualify" if any(term in normalized for term in ("risk", "caveat", "counter")) else
            "elaborate"
        )
        attention = (
            "primary" if normalized in {"orientation", "synthesis", "thesis", "conclusion"} else
            "supporting" if any(term in normalized for term in ("risk", "caveat", "counter")) else
            "secondary"
        )
        for field, value in (
            ("data_statement_id", item.statement_id),
            ("encounter_mode_display", mode.replace("-", " ").title()),
            ("data_grammar_stage", stage), ("data_attention", attention),
            ("source_block_role", _source_block_role(item.encounter_meaning)),
            ("encounter_meaning", item.encounter_meaning),
            ("description", item.encounter_semantics.description), ("authority_ref", item.authority_ref),
        ):
            add(item.statement_id, f"statement:{item.statement_id}", field, value)
        add(item.statement_id, f"statement:{item.statement_id}", "upstream_reference_ids", json.dumps(list(item.upstream_reference_ids), separators=(",", ":")))
        add(item.statement_id, f"statement:{item.statement_id}", "obligation_ids", json.dumps(list(item.obligation_ids), separators=(",", ":")))
    for item in projection.upstream_references:
        add(item.reference_id, f"reference:{item.reference_id}", "data_reference_id", item.reference_id)
        for field in ("owning_project", "reference_kind", "locator", "owned_meaning", "provenance_ref", "provenance_citation"):
            add(item.reference_id, f"reference:{item.reference_id}", field, str(getattr(item, field)))
    for item in projection.obligations:
        add(item.obligation_id, f"obligation:{item.obligation_id}", "data_obligation_id", item.obligation_id)
        for field in ("category", "requirement", "authority_ref"):
            add(item.obligation_id, f"obligation:{item.obligation_id}", field, str(getattr(item, field)))
        add(item.obligation_id, f"obligation:{item.obligation_id}", "applies_to", json.dumps(list(item.applies_to), separators=(",", ":")))
    identities = [item["id"] for item in requirements]
    if len(identities) != len(set(identities)):
        raise ValueError("Expected semantic requirement identities are duplicated.")
    return requirements


def _admit_bounded_profile(projection: MinimalHtmlRendererProjection) -> None:
    """Constrain assessment to the exact plain-text TASK-052 renderer subset proved here."""
    if len(projection.statements) != 1:
        raise ValueError("The conformance profile requires exactly one statement and excludes long-document output.")
    if not projection.selected_expression_modes or any(mode != "native" for mode in projection.selected_expression_modes):
        raise ValueError("The conformance profile accepts only Plan-authorized native expression mappings.")
    values = [projection.identity.title, projection.identity.purpose_summary,
              projection.organizing_purpose.statement, projection.organizing_purpose.non_scope]
    for statement in projection.statements:
        if statement.encounter_semantics.mode != "observation":
            raise ValueError("The conformance profile accepts only the proved observation encounter mode.")
        values.extend((statement.encounter_meaning, statement.encounter_semantics.description))
        if len(statement.encounter_meaning) > 140 or re.search(r"[`*_\[\]]", statement.encounter_meaning) or re.match(r"^(?:#{1,6}|>|[-+])\s", statement.encounter_meaning):
            raise ValueError("The conformance profile accepts only one bounded plain-text heading realization per statement.")
    for reference in projection.upstream_references:
        values.extend((reference.owned_meaning, reference.provenance_citation))
    for obligation in projection.obligations:
        values.append(obligation.requirement)
    if any(type(value) is not str or not value or "\n" in value or "\r" in value or "`" in value for value in values):
        raise ValueError("The conformance profile excludes empty, multiline, inline-code, and structured-text semantic fields.")


def _validate_exact_node_inventory(parser: _StrictStructuralHTMLParser, projection: MinimalHtmlRendererProjection) -> tuple[str, ...]:
    """Close every element and attribute in the one proved native HTML shape."""
    expected: list[tuple[str, tuple[tuple[str, str], ...]]] = []

    def add(tag: str, **attrs: str) -> None:
        expected.append((tag, tuple(sorted(attrs.items()))))

    statement = projection.statements[0]
    add("html", lang="en"); add("head")
    add("meta", charset="utf-8")
    add("meta", name="briefforge-adapter-id", content="minimal-html-renderer")
    add("meta", name="briefforge-package-id", content=projection.identity.package_id)
    add("meta", name="briefforge-semantic-fingerprint", content=projection.semantic_fingerprint)
    add("meta", name="briefforge-validation-policy-id", content=projection.validation_policy_id)
    add("title"); add("style")
    add("body", **{"data-grammar": "presentation-grammar-v1", "data-reader-experience": "static-v0.3"})
    add("main")
    add("header", **{"data-grammar-stage": "orient", "data-attention": "primary"})
    add("h1"); add("p"); add("strong"); add("p", **{"data-attention": "secondary"})
    add("section", **{"data-grammar-stage": "state-main-point", "data-attention": "primary"})
    add("h2"); add("div", **{"data-source-structure": "preserved-v0.1", "data-source-tables": "absent"})
    add("h4", **{"data-source-block": _source_block_role(statement.encounter_meaning)})
    add("section", **{"data-exhibit-region": "none-detected", "data-attention": "supporting"}); add("h2"); add("p")
    add("section", **{"data-grammar-stage": "elaborate", "data-attention": "secondary"}); add("h2")
    add("article", id=f"statement-{statement.statement_id}", **{
        "data-statement-id": statement.statement_id,
        "data-grammar-stage": "elaborate", "data-attention": "secondary",
    })
    add("h3")
    add("div", **{"data-source-structure": "preserved-v0.1", "data-source-tables": "absent"})
    add("h4", **{"data-source-block": _source_block_role(statement.encounter_meaning)})
    add("p", **{"data-attention": "supporting"}); add("p", **{"data-attention": "supporting"})
    if statement.upstream_reference_ids:
        add("div", **{"data-attention": "supporting"}); add("p"); add("ul")
        for identity in statement.upstream_reference_ids:
            add("li"); add("a", href=f"#reference-{identity}"); add("span"); add("span")
    if statement.obligation_ids:
        add("div", **{"data-attention": "supporting"}); add("p"); add("ul")
        for identity in statement.obligation_ids:
            add("li"); add("a", href=f"#obligation-{identity}"); add("span")
    add("section", **{"data-grammar-stage": "qualify", "data-attention": "supporting"}); add("h2"); add("p"); add("ul")
    add("section", **{"data-grammar-stage": "trace", "data-attention": "supporting"}); add("h2"); add("ol")
    for reference in projection.upstream_references:
        add("li", id=f"reference-{reference.reference_id}", **{"data-reference-id": reference.reference_id})
        add("p"); add("strong")
        for _ in range(5): add("p")
    add("section", **{"data-grammar-stage": "trace", "data-attention": "supporting"}); add("h2"); add("p"); add("ol")
    for obligation in projection.obligations:
        add("li", id=f"obligation-{obligation.obligation_id}", **{"data-obligation-id": obligation.obligation_id})
        add("p"); add("strong"); add("p"); add("p")
    add("details", **{"data-grammar-stage": "trace", "data-attention": "discoverable"}); add("summary")
    for _ in range(4): add("p")

    errors: list[str] = []
    actual = Counter((node.tag, tuple(sorted(node.attrs.items()))) for node in parser.nodes)
    if actual != Counter(expected):
        missing = sorted((Counter(expected) - actual).elements())
        extra = sorted((actual - Counter(expected)).elements())
        errors.append(f"HTML element/attribute inventory differs from the exact profile: missing={missing!r}; extra={extra!r}.")

    main_nodes = [node for node in parser.nodes if node.tag == "main"]
    if len(main_nodes) != 1:
        errors.append("Main semantic root cardinality differs from the exact profile.")
        return tuple(errors)
    main = main_nodes[0]
    ordered_regions: list[tuple[str, str]] = []
    for region in main.children:
        labels = [child.all_text() for child in region.children if child.tag in {"h1", "h2", "summary"}]
        ordered_regions.append((region.tag, labels[0] if labels else ""))
    expected_regions = [
        ("header", projection.identity.title), ("section", "Primary message"),
        ("section", "Evidence exhibits"), ("section", "Supporting details"),
        ("section", "Uncertainty and caveats"), ("section", "Reference inventory"),
        ("section", "Obligation inventory"), ("details", "Validation and audit metadata"),
    ]
    if ordered_regions != expected_regions:
        errors.append("Global semantic-region order differs from the exact profile.")

    def tags(node: _HtmlNode) -> list[str]:
        return [child.tag for child in node.children]

    if len(main.children) == 8:
        header, primary, exhibit, supporting, caveat, references, obligations, details = main.children
        direct_expectations = (
            (header, ["h1", "p", "p"], "header"),
            (primary, ["h2", "div"], "primary-message"),
            (exhibit, ["h2", "p"], "exhibit"),
            (supporting, ["h2", "article"], "supporting-details"),
            (caveat, ["h2", "p", "ul"], "caveat"),
            (references, ["h2", "ol"], "reference-inventory"),
            (obligations, ["h2", "p", "ol"], "obligation-inventory"),
            (details, ["summary", "p", "p", "p", "p"], "audit-details"),
        )
        for node, expected_tags, label in direct_expectations:
            if tags(node) != expected_tags:
                errors.append(f"Exact {label} child hierarchy differs from the profile.")
        if tags(header) == ["h1", "p", "p"] and tags(header.children[1]) != ["strong"]:
            errors.append("Purpose emphasis hierarchy differs from the profile.")
        if tags(primary) == ["h2", "div"] and tags(primary.children[1]) != ["h4"]:
            errors.append("Primary-message realization hierarchy differs from the profile.")
        if tags(supporting) == ["h2", "article"]:
            article = supporting.children[1]
            expected_article = ["h3", "div", "p", "p"]
            if statement.upstream_reference_ids: expected_article.append("div")
            if statement.obligation_ids: expected_article.append("div")
            if tags(article) != expected_article:
                errors.append("Statement article hierarchy differs from the profile.")
            elif tags(article.children[1]) != ["h4"]:
                errors.append("Statement meaning hierarchy differs from the profile.")
            else:
                offset = 4
                if statement.upstream_reference_ids:
                    ref_links = article.children[offset]; offset += 1
                    if tags(ref_links) != ["p", "ul"] or len(ref_links.children[1].children) != len(statement.upstream_reference_ids) or any(tags(item) != ["a", "span", "span"] for item in ref_links.children[1].children):
                        errors.append("Statement reference-link hierarchy differs from the profile.")
                if statement.obligation_ids:
                    obligation_links = article.children[offset]
                    if tags(obligation_links) != ["p", "ul"] or len(obligation_links.children[1].children) != len(statement.obligation_ids) or any(tags(item) != ["a", "span"] for item in obligation_links.children[1].children):
                        errors.append("Statement obligation-link hierarchy differs from the profile.")
        if tags(references) == ["h2", "ol"]:
            items = references.children[1].children
            if len(items) != len(projection.upstream_references) or any(tags(item) != ["p"] * 6 or tags(item.children[0]) != ["strong"] for item in items):
                errors.append("Reference inventory hierarchy differs from the profile.")
        if tags(obligations) == ["h2", "p", "ol"]:
            items = obligations.children[2].children
            if len(items) != len(projection.obligations) or any(tags(item) != ["p"] * 3 or tags(item.children[0]) != ["strong"] for item in items):
                errors.append("Obligation inventory hierarchy differs from the profile.")
    else:
        errors.append("Main semantic-region cardinality differs from the exact profile.")
    return tuple(errors)


def verify_exact_semantic_html(artifact_bytes: bytes, projection: MinimalHtmlRendererProjection) -> dict[str, Any]:
    """Independently extract supported HTML and reconcile field requirements."""
    if type(projection) is not MinimalHtmlRendererProjection:
        raise ValueError("An exact governed renderer projection is required.")
    _admit_bounded_profile(projection)
    parser = _parse_exact_html(artifact_bytes)
    structure_errors = _validate_exact_node_inventory(parser, projection)
    if structure_errors:
        raise ValueError(" ".join(structure_errors))
    statement_ids = [item.statement_id for item in projection.statements]
    reference_ids = [item.reference_id for item in projection.upstream_references]
    obligation_ids = [item.obligation_id for item in projection.obligations]
    for label, identities in (("statement", statement_ids), ("reference", reference_ids), ("obligation", obligation_ids)):
        if len(identities) != len(set(identities)):
            raise ValueError(f"Governed {label} inventory is duplicated or ambiguous.")
    mappings = list(projection.consumed_mapping_ids)
    modes = list(projection.selected_expression_modes)
    if len(mappings) != len(set(mappings)) or len(mappings) != len(modes):
        raise ValueError("Plan requirement accounting is omitted, duplicated, or contradictory.")
    if any(mode in {"unsupported", "blocked"} for mode in modes):
        raise ValueError("Plan realization mode is explicitly unsupported or blocked.")
    if any(mode not in {"native", "static-fallback"} for mode in modes):
        raise ValueError("Plan realization mode is unknown and blocked.")

    def nodes(**attrs: str) -> list[_HtmlNode]:
        return [node for node in parser.nodes if all(node.attrs.get(k) == v for k, v in attrs.items())]

    actual_values: dict[tuple[str, str, str], str] = {}

    def capture(source: str, role: str, field: str, value: str) -> None:
        key = (source, role, field)
        if key in actual_values:
            raise ValueError(f"Actual semantic requirement {key!r} is duplicated.")
        actual_values[key] = value

    meta_requirements = {
        "briefforge-package-id": ("meta-package", projection.identity.package_id),
        "briefforge-semantic-fingerprint": ("meta-semantic-fingerprint", projection.semantic_fingerprint),
        "briefforge-validation-policy-id": ("meta-validation-policy", projection.validation_policy_id),
    }
    for name, (role, expected_value) in meta_requirements.items():
        found = [node for node in parser.nodes if node.tag == "meta" and node.attrs.get("name") == name]
        if len(found) != 1:
            raise ValueError(f"Required metadata field {name} is omitted or duplicated.")
        capture(projection.identity.package_id, role, "content", found[0].attrs.get("content", ""))
        if found[0].attrs.get("content") != expected_value:
            raise ValueError(f"Required metadata field {name} is altered.")
    title_nodes = [n for n in parser.nodes if n.tag == "title"]
    if len(title_nodes) != 1 or title_nodes[0].all_text() != projection.identity.title:
        raise ValueError("Governed title is omitted, duplicated, or altered.")
    capture(projection.identity.package_id, "title", "text", title_nodes[0].all_text())
    def descendants(node: _HtmlNode) -> list[_HtmlNode]:
        result: list[_HtmlNode] = []
        pending = list(node.children)
        while pending:
            child = pending.pop(0)
            result.append(child)
            pending[0:0] = child.children
        return result

    headers = [n for n in parser.nodes if n.tag == "header" and n.parent and n.parent.tag == "main"]
    if len(headers) != 1:
        raise ValueError("The supported document requires exactly one semantic header.")
    header_text = [(n.tag, n.all_text()) for n in descendants(headers[0]) if n.tag in {"h1", "p"}]
    if header_text != [
        ("h1", projection.identity.title),
        ("p", "Purpose: " + projection.organizing_purpose.statement),
        ("p", projection.identity.purpose_summary),
    ]:
        raise ValueError("Governed title, purpose, scope, or header hierarchy is altered.")
    capture(projection.identity.package_id, "purpose", "statement", header_text[1][1].removeprefix("Purpose: "))
    capture(projection.identity.package_id, "scope", "purpose_summary", header_text[2][1])

    caveat_sections = [
        n for n in parser.nodes
        if n.tag == "section" and n.attrs.get("data-grammar-stage") == "qualify"
    ]
    if len(caveat_sections) != 1:
        raise ValueError("The supported document requires exactly one non-scope section.")
    caveat_paragraphs = [n.all_text() for n in descendants(caveat_sections[0]) if n.tag == "p"]
    if caveat_paragraphs != [projection.organizing_purpose.non_scope]:
        raise ValueError("Governed non-scope is omitted, duplicated, or altered.")
    capture(projection.identity.package_id, "non-scope", "non_scope", caveat_paragraphs[0])

    for index, statement in enumerate(projection.statements):
        found = nodes(**{"data-statement-id": statement.statement_id})
        if len(found) != 1 or found[0].tag != "article" or not found[0].parent or found[0].parent.tag != "section":
            raise ValueError(f"Statement {statement.statement_id} is omitted, duplicated, or structurally spoofed.")
        statement_nodes = descendants(found[0])
        exact_text = [(node.tag, node.all_text()) for node in statement_nodes]
        required_nodes = (
            ("h4", statement.encounter_meaning),
            ("p", f"Authority: {statement.authority_ref}"),
            ("p", f"Reader role: {statement.encounter_semantics.description}"),
        )
        if any(exact_text.count(item) != 1 for item in required_nodes):
            raise ValueError(f"Statement {statement.statement_id} has altered field realization or hierarchy.")
        mode_display = statement.encounter_semantics.mode.replace("-", " ").title()
        mode_nodes = [node for node in statement_nodes if node.tag == "h3"]
        if len(mode_nodes) != 1 or mode_nodes[0].all_text() != mode_display:
            raise ValueError(f"Statement {statement.statement_id} encounter mode is altered.")
        role = f"statement:{statement.statement_id}"
        capture(statement.statement_id, role, "data_statement_id", found[0].attrs.get("data-statement-id", ""))
        capture(statement.statement_id, role, "encounter_mode_display", mode_nodes[0].all_text())
        capture(statement.statement_id, role, "data_grammar_stage", found[0].attrs.get("data-grammar-stage", ""))
        capture(statement.statement_id, role, "data_attention", found[0].attrs.get("data-attention", ""))
        meaning_node = next(node for node in statement_nodes if node.tag == "h4")
        capture(statement.statement_id, role, "source_block_role", meaning_node.attrs.get("data-source-block", ""))
        capture(statement.statement_id, role, "encounter_meaning", meaning_node.all_text())
        capture(statement.statement_id, role, "description", next(node.all_text().removeprefix("Reader role: ") for node in statement_nodes if node.tag == "p" and node.all_text().startswith("Reader role: ")))
        capture(statement.statement_id, role, "authority_ref", next(node.all_text().removeprefix("Authority: ") for node in statement_nodes if node.tag == "p" and node.all_text().startswith("Authority: ")))
        statement_anchors = [node for node in statement_nodes if node.tag == "a"]
        capture(statement.statement_id, role, "upstream_reference_ids", json.dumps([
            node.all_text() for node in statement_anchors if node.attrs.get("href", "").startswith("#reference-")
        ], separators=(",", ":")))
        capture(statement.statement_id, role, "obligation_ids", json.dumps([
            node.all_text() for node in statement_anchors if node.attrs.get("href", "").startswith("#obligation-")
        ], separators=(",", ":")))
        visible_occurrences = sum(
            1 for node in parser.nodes if node.tag != "style"
            for piece in node.text if " ".join(piece.split()) == statement.encounter_meaning
        )
        expected_occurrences = 2 if index == 0 else 1
        if visible_occurrences != expected_occurrences:
            raise ValueError(f"Statement {statement.statement_id} is not realized in its authorized roles exactly once each.")
    actual_statement_order = [n.attrs["data-statement-id"] for n in parser.nodes if "data-statement-id" in n.attrs]
    if actual_statement_order != statement_ids:
        raise ValueError("Meaning-bearing statement encounter order differs from the governed order.")
    for reference in projection.upstream_references:
        found = nodes(**{"data-reference-id": reference.reference_id})
        expected_paragraphs = [
            reference.reference_id,
            f"Source owner: {reference.owning_project}",
            f"Kind: {reference.reference_kind}",
            f"Locator: {reference.locator}",
            f"Owned meaning: {reference.owned_meaning}",
            f"Provenance: {reference.provenance_ref} — {reference.provenance_citation}",
        ]
        if len(found) != 1 or found[0].tag != "li" or not found[0].parent or found[0].parent.tag != "ol":
            raise ValueError(f"Reference {reference.reference_id} is omitted, duplicated, or structurally altered.")
        paragraphs = [n.all_text() for n in descendants(found[0]) if n.tag == "p"]
        if paragraphs != expected_paragraphs:
            raise ValueError(f"Reference {reference.reference_id} fields, provenance, or hierarchy are altered.")
        role = f"reference:{reference.reference_id}"
        capture(reference.reference_id, role, "data_reference_id", found[0].attrs.get("data-reference-id", ""))
        capture(reference.reference_id, role, "owning_project", paragraphs[1].removeprefix("Source owner: "))
        capture(reference.reference_id, role, "reference_kind", paragraphs[2].removeprefix("Kind: "))
        capture(reference.reference_id, role, "locator", paragraphs[3].removeprefix("Locator: "))
        capture(reference.reference_id, role, "owned_meaning", paragraphs[4].removeprefix("Owned meaning: "))
        provenance = paragraphs[5].removeprefix("Provenance: ")
        provenance_ref, separator, citation = provenance.partition(" — ")
        if not separator:
            raise ValueError(f"Reference {reference.reference_id} provenance composition is malformed.")
        capture(reference.reference_id, role, "provenance_ref", provenance_ref)
        capture(reference.reference_id, role, "provenance_citation", citation)
    if [n.attrs["data-reference-id"] for n in parser.nodes if "data-reference-id" in n.attrs] != reference_ids:
        raise ValueError("Meaning-bearing reference encounter order differs from the governed order.")
    for obligation in projection.obligations:
        found = nodes(**{"data-obligation-id": obligation.obligation_id})
        applies = ", ".join(obligation.applies_to) if obligation.applies_to else "whole package"
        expected_paragraphs = [
            f"{obligation.category}: {obligation.requirement}",
            f"Authority: {obligation.authority_ref}",
            f"Applies to: {applies}",
        ]
        if len(found) != 1 or found[0].tag != "li" or not found[0].parent or found[0].parent.tag != "ol":
            raise ValueError(f"Obligation {obligation.obligation_id} is omitted, duplicated, or structurally altered.")
        paragraphs = [n.all_text() for n in descendants(found[0]) if n.tag == "p"]
        if paragraphs != expected_paragraphs:
            raise ValueError(f"Obligation {obligation.obligation_id} fields or hierarchy are altered.")
        role = f"obligation:{obligation.obligation_id}"
        capture(obligation.obligation_id, role, "data_obligation_id", found[0].attrs.get("data-obligation-id", ""))
        category, separator, requirement = paragraphs[0].partition(": ")
        if not separator:
            raise ValueError(f"Obligation {obligation.obligation_id} category composition is malformed.")
        capture(obligation.obligation_id, role, "category", category)
        capture(obligation.obligation_id, role, "requirement", requirement)
        capture(obligation.obligation_id, role, "authority_ref", paragraphs[1].removeprefix("Authority: "))
        applies = paragraphs[2].removeprefix("Applies to: ")
        actual_applies = [] if applies == "whole package" else applies.split(", ")
        capture(obligation.obligation_id, role, "applies_to", json.dumps(actual_applies, separators=(",", ":")))
    if [n.attrs["data-obligation-id"] for n in parser.nodes if "data-obligation-id" in n.attrs] != obligation_ids:
        raise ValueError("Meaning-bearing obligation encounter order differs from the governed order.")
    expected_links = sorted(
        [(s.statement_id, "reference", target) for s in projection.statements for target in s.upstream_reference_ids]
        + [(s.statement_id, "obligation", target) for s in projection.statements for target in s.obligation_ids]
    )
    actual_links: list[tuple[str, str, str]] = []
    for statement in projection.statements:
        article = nodes(**{"data-statement-id": statement.statement_id})[0]
        descendants = set(id(n) for n in article.children)
        pending = list(article.children)
        while pending:
            child = pending.pop(); descendants.add(id(child)); pending.extend(child.children)
        for anchor in (n for n in parser.nodes if n.tag == "a" and id(n) in descendants):
            match = re.fullmatch(r"#(reference|obligation)-(.+)", anchor.attrs.get("href", ""))
            if not match or anchor.all_text() != match.group(2):
                raise ValueError("Audit href/text identity spoof detected.")
            actual_links.append((statement.statement_id, match.group(1), match.group(2)))
    if sorted(actual_links) != expected_links:
        raise ValueError("Directed audit-link inventory has wrong identity, cardinality, or direction.")

    # Raw text and arbitrary extra prose are not evidence channels.  Every visible
    # text node must be either fixed profile chrome or an independently derived
    # governed field/composition.
    fixed_text = {
        "Purpose:", "Primary message", "Evidence exhibits", "No renderer-visible exhibit candidates detected in existing source evidence.",
        "Supporting details", "Uncertainty and caveats", "Reference inventory", "Obligation inventory",
        "Validation and audit metadata", "Observation", "Recommendation", "Caveat", "Methodology",
        "Evidence-linked references", "Contextual obligations", "Source owner:", "Kind:", "Locator:",
    }
    governed_text = {
        projection.identity.title, projection.organizing_purpose.statement, projection.identity.purpose_summary,
        projection.organizing_purpose.non_scope, projection.identity.package_id, projection.semantic_fingerprint,
        projection.validation_policy_id, "minimal-html-renderer",
    }
    for s in projection.statements:
        governed_text.update({s.statement_id, s.encounter_meaning, s.authority_ref, s.encounter_semantics.mode.title(),
                              f"Authority: {s.authority_ref}", f"Reader role: {s.encounter_semantics.description}"})
    for r in projection.upstream_references:
        governed_text.update({r.reference_id, r.owning_project, r.reference_kind, r.locator, r.owned_meaning, r.provenance_ref,
                              f"Source owner: {r.owning_project}", f"Kind: {r.reference_kind}", f"Locator: {r.locator}",
                              f"Owned meaning: {r.owned_meaning}", f"Provenance: {r.provenance_ref} — {r.provenance_citation}",
                              f"Source owner: {r.owning_project} Kind: {r.reference_kind}"})
    for o in projection.obligations:
        applies = ", ".join(o.applies_to) if o.applies_to else "whole package"
        governed_text.update({o.obligation_id, o.category, o.requirement, o.authority_ref,
                              f"{o.category}: {o.requirement}", f": {o.requirement}", f"Authority: {o.authority_ref}", f"Applies to: {applies}"})
    governed_text.update({f"Adapter: minimal-html-renderer", f"Package: {projection.identity.package_id}",
                          f"Semantic fingerprint: {projection.semantic_fingerprint}", f"Validation policy: {projection.validation_policy_id}"})
    for node in parser.nodes:
        if node.tag == "style":
            continue
        for piece in node.text:
            value = " ".join(piece.split())
            if value and value not in fixed_text and value not in governed_text:
                raise ValueError("HTML contains unauthorized visible or raw-text content.")
    details = [node for node in parser.nodes if node.tag == "details"]
    if len(details) != 1 or details[0].all_text() != "Validation and audit metadata Adapter: minimal-html-renderer Package: " + projection.identity.package_id + " Semantic fingerprint: " + projection.semantic_fingerprint + " Validation policy: " + projection.validation_policy_id:
        raise ValueError("Closed details are unauthorized except for the exact redundant audit panel.")

    requirements = _requirement_inventory(projection)
    expected_keys = {(item["source"], item["role"], item["field"]) for item in requirements}
    if set(actual_values) != expected_keys:
        missing = sorted(expected_keys - set(actual_values))
        extra = sorted(set(actual_values) - expected_keys)
        raise ValueError(f"Actual semantic inventory is incomplete or excessive: missing={missing!r}; extra={extra!r}.")
    requirement_by_key = {
        (item["source"], item["role"], item["field"]): item for item in requirements
    }
    actual_inventory = []
    for key in sorted(actual_values):
        requirement = requirement_by_key[key]
        actual = actual_values[key]
        if actual != requirement["expected"]:
            raise ValueError(f"Actual semantic requirement {key!r} differs from the governed expectation.")
        actual_inventory.append({
            "requirement_ref": requirement["id"], "source": key[0], "role": key[1],
            "field": key[2], "actual": actual, "extraction": "strict-structural-field",
        })
    return {
        "comparison": "independent-field-requirement-reconciliation",
        "artifact_sha256": hashlib.sha256(artifact_bytes).hexdigest(),
        "projection_fingerprint": projection.fingerprint,
        "expected_requirements": requirements,
        "actual_inventory": actual_inventory,
        "requirement_ids": [item["id"] for item in requirements],
        "requirement_outcomes": [item["outcome"] for item in requirements],
        "expression_modes": [{"mapping_identity": mapping, "selected_mode": mode, "outcome": "conformant"} for mapping, mode in zip(mappings, modes)],
        "semantic_relation_links": [{"source": a, "role": b, "target": c} for a, b, c in expected_links],
        "statement_ids": statement_ids, "reference_ids": reference_ids, "obligation_ids": obligation_ids,
        "aggregate_verdict": "approved",
        "hidden_content": "absent", "unauthorized_content": "absent",
    }


def _complete_semantic_findings(artifact_bytes: bytes, projection: MinimalHtmlRendererProjection) -> tuple[ConformanceFinding, ...]:
    """Return all independently assessable requirement failures for a rejected artifact."""
    try:
        _admit_bounded_profile(projection)
        parser = _parse_exact_html(artifact_bytes)
    except Exception as exc:
        return (_finding("semantic-structure-indeterminate", "/artifact", str(exc)),)

    findings: list[ConformanceFinding] = []
    for index, message in enumerate(_validate_exact_node_inventory(parser, projection), start=1):
        findings.append(_finding(f"unauthorized-or-misordered-structure-{index}", "/artifact/structure", message))

    def descendants(node: _HtmlNode) -> list[_HtmlNode]:
        result: list[_HtmlNode] = []
        pending = list(node.children)
        while pending:
            child = pending.pop(0); result.append(child); pending[0:0] = child.children
        return result

    def one(items: list[_HtmlNode]) -> _HtmlNode | None:
        return items[0] if len(items) == 1 else None

    def actual_for(requirement: dict[str, str]) -> str | None:
        source, role, field = requirement["source"], requirement["role"], requirement["field"]
        if role.startswith("meta-"):
            name = {
                "meta-package": "briefforge-package-id",
                "meta-semantic-fingerprint": "briefforge-semantic-fingerprint",
                "meta-validation-policy": "briefforge-validation-policy-id",
            }[role]
            node = one([n for n in parser.nodes if n.tag == "meta" and n.attrs.get("name") == name])
            return node.attrs.get("content", "") if node else None
        if role == "title":
            node = one([n for n in parser.nodes if n.tag == "title"]); return node.all_text() if node else None
        if role in {"purpose", "scope"}:
            header = one([n for n in parser.nodes if n.tag == "header" and n.parent and n.parent.tag == "main"])
            paragraphs = [n.all_text() for n in descendants(header) if n.tag == "p"] if header else []
            if role == "purpose": return paragraphs[0].removeprefix("Purpose: ") if len(paragraphs) == 2 else None
            return paragraphs[1] if len(paragraphs) == 2 else None
        if role == "non-scope":
            section = one([n for n in parser.nodes if n.tag == "section" and n.attrs.get("data-grammar-stage") == "qualify"])
            paragraphs = [n.all_text() for n in descendants(section) if n.tag == "p"] if section else []
            return paragraphs[0] if len(paragraphs) == 1 else None
        if role.startswith("statement:"):
            article = one([n for n in parser.nodes if n.attrs.get("data-statement-id") == source])
            if not article: return None
            nodes = descendants(article)
            if field == "data_statement_id": return article.attrs.get("data-statement-id")
            if field == "data_grammar_stage": return article.attrs.get("data-grammar-stage")
            if field == "data_attention": return article.attrs.get("data-attention")
            if field == "encounter_mode_display":
                node = one([n for n in nodes if n.tag == "h3"]); return node.all_text() if node else None
            if field in {"encounter_meaning", "source_block_role"}:
                node = one([n for n in nodes if n.tag == "h4"])
                return (node.all_text() if field == "encounter_meaning" else node.attrs.get("data-source-block")) if node else None
            if field in {"description", "authority_ref"}:
                prefix = "Reader role: " if field == "description" else "Authority: "
                values = [n.all_text().removeprefix(prefix) for n in nodes if n.tag == "p" and n.all_text().startswith(prefix)]
                return values[0] if len(values) == 1 else None
            if field in {"upstream_reference_ids", "obligation_ids"}:
                prefix = "#reference-" if field == "upstream_reference_ids" else "#obligation-"
                return json.dumps([n.all_text() for n in nodes if n.tag == "a" and n.attrs.get("href", "").startswith(prefix)], separators=(",", ":"))
        if role.startswith("reference:"):
            item = one([n for n in parser.nodes if n.attrs.get("data-reference-id") == source])
            if not item: return None
            paragraphs = [n.all_text() for n in descendants(item) if n.tag == "p"]
            if field == "data_reference_id": return item.attrs.get("data-reference-id")
            indexes = {"owning_project": (1, "Source owner: "), "reference_kind": (2, "Kind: "), "locator": (3, "Locator: "), "owned_meaning": (4, "Owned meaning: ")}
            if field in indexes and len(paragraphs) == 6:
                index, prefix = indexes[field]; return paragraphs[index].removeprefix(prefix)
            if field in {"provenance_ref", "provenance_citation"} and len(paragraphs) == 6:
                left, separator, right = paragraphs[5].removeprefix("Provenance: ").partition(" — ")
                return (left if field == "provenance_ref" else right) if separator else None
        if role.startswith("obligation:"):
            item = one([n for n in parser.nodes if n.attrs.get("data-obligation-id") == source])
            if not item: return None
            paragraphs = [n.all_text() for n in descendants(item) if n.tag == "p"]
            if field == "data_obligation_id": return item.attrs.get("data-obligation-id")
            if len(paragraphs) != 3: return None
            category, separator, requirement = paragraphs[0].partition(": ")
            if field == "category": return category if separator else None
            if field == "requirement": return requirement if separator else None
            if field == "authority_ref": return paragraphs[1].removeprefix("Authority: ")
            if field == "applies_to":
                applies = paragraphs[2].removeprefix("Applies to: ")
                return json.dumps([] if applies == "whole package" else applies.split(", "), separators=(",", ":"))
        return None

    for requirement in _requirement_inventory(projection):
        try:
            actual = actual_for(requirement)
        except Exception:
            actual = None
        if actual != requirement["expected"]:
            state = "indeterminate" if actual is None else "nonconformant"
            findings.append(_finding(
                f"semantic-requirement-{state}", f"/requirements/{requirement['id']}",
                f"{requirement['role']} {requirement['field']} is {state}.",
            ))
    if not findings:
        findings.append(_finding("semantic-assessment-inconsistency", "/artifact", "Artifact rejection produced no reproducible negative finding."))
    return tuple(sorted(set(findings)))


def _finding(code: str, location: str, message: str) -> ConformanceFinding:
    return ConformanceFinding(code, location, message)


def _bind_authority_audit_links(
    semantic_evidence: dict[str, Any],
    invocation: VerifiedRendererInvocation,
    authorization: SemanticArtifactConformanceAuthorization,
) -> dict[str, Any]:
    """Bind a complete, directed dependency inventory without treating links as proof."""
    audit_identity = invocation.bundle.one("GeneratedArtifactAuditRecord").identity
    expected_digest = hashlib.sha256(_canonical_bytes(semantic_evidence["expected_requirements"])).hexdigest()
    actual_digest = hashlib.sha256(_canonical_bytes(semantic_evidence["actual_inventory"])).hexdigest()
    outcome_digest = hashlib.sha256(_canonical_bytes(semantic_evidence["requirement_outcomes"])).hexdigest()
    profile_digest = hashlib.sha256(
        _canonical_bytes([authorization.profile_identity, authorization.profile_version])
    ).hexdigest()
    assessor_digest = hashlib.sha256(
        _canonical_bytes([authorization.assessor_implementation, authorization.assessor_version])
    ).hexdigest()
    dependencies = (
        ("release", authorization.release_identity, authorization.release_fingerprint),
        ("complete-lifecycle-scope", authorization.release_identity, authorization.lifecycle_inventory_digest),
        ("compatibility-plan", authorization.plan_identity, authorization.plan_fingerprint),
        ("capability-declaration", authorization.capability_identity, authorization.capability_fingerprint),
        ("invocation-authorization", authorization.invocation_authorization_identity, authorization.invocation_authorization_fingerprint),
        ("invocation-evidence", audit_identity, authorization.invocation_evidence_fingerprint),
        ("artifact-bytes", authorization.artifact_identity, authorization.artifact_sha256),
        ("conformance-authorization", authorization.identity, authorization.fingerprint),
        ("conformance-profile", authorization.profile_identity, profile_digest),
        ("renderer-implementation", authorization.renderer_identity, authorization.renderer_implementation_digest),
        ("assessor-implementation", authorization.assessor_identity, assessor_digest),
        ("expected-requirement-inventory", authorization.record_identity, expected_digest),
        ("actual-semantic-inventory", authorization.record_identity, actual_digest),
        ("per-requirement-outcomes", authorization.record_identity, outcome_digest),
    )
    roles = [item[0] for item in dependencies]
    if len(roles) != len(set(roles)):
        raise ValueError("Authority audit-link roles are duplicated.")
    return {
        **semantic_evidence,
        "authority_audit_links": [
            {
                "source": authorization.record_identity,
                "direction": "depends-on",
                "role": role,
                "target": target,
                "target_fingerprint": fingerprint,
                "outcome": "binding-verified",
            }
            for role, target, fingerprint in dependencies
        ],
        "audit_link_character": "traceable-binding-not-independent-conformance-proof",
    }


def _authorization_findings(
    authorization: SemanticArtifactConformanceAuthorization,
    *, invocation: VerifiedRendererInvocation, release: VerifiedPublicationRelease,
    lifecycle: LifecyclePlanningScope, declaration: RendererCapabilityDeclaration,
    plan: VerifiedRendererCompatibilityPlan, invocation_authorization: RendererInvocationAuthorization,
    artifact_bytes: bytes,
) -> tuple[ConformanceFinding, ...]:
    if type(authorization) is not SemanticArtifactConformanceAuthorization:
        return (_finding("missing-authorization", "/authorization", "Exact immutable conformance authorization is required."),)
    findings: list[ConformanceFinding] = []
    audit_artifact = invocation.bundle.one("GeneratedArtifactAuditRecord").semantic["artifact"]
    released_authorities = [
        item for item in release.bundle.one("PortablePresentationMaterialRecord").semantic.get("authorities", [])
        if item.get("id") == ACCEPTED_ASSESSOR_IDENTITY
    ]
    expected_assessor_authority = {
        "id": ACCEPTED_ASSESSOR_IDENTITY,
        "owner_identity": ACCEPTED_ASSESSOR_OWNER,
        "role": ACCEPTED_ASSESSOR_ROLE,
        "scope": "one-semantic-artifact-conformance-assessment",
    }
    if released_authorities != [expected_assessor_authority]:
        findings.append(_finding(
            "unreleased-assessor-authority", "/release/authorities",
            "The independently verified Release does not carry exactly one accepted assessor authority.",
        ))
    expected = {
        "policy_identity": CONFORMANCE_POLICY_ID,
        "authority_identity": ACCEPTED_ASSESSOR_IDENTITY,
        "authority_owner": ACCEPTED_ASSESSOR_OWNER,
        "authority_role": ACCEPTED_ASSESSOR_ROLE,
        "profile_identity": SEMANTIC_REALIZATION_PROFILE_ID,
        "profile_version": SEMANTIC_REALIZATION_PROFILE_VERSION,
        "assessor_identity": ACCEPTED_ASSESSOR_IDENTITY,
        "release_identity": release.release.identity,
        "release_fingerprint": release.fingerprint.digest,
        "lifecycle_inventory_digest": lifecycle.inventory_digest,
        "plan_identity": plan.plan.identity,
        "plan_fingerprint": plan.fingerprint.digest,
        "capability_identity": declaration.identity,
        "capability_fingerprint": declaration.fingerprint,
        "invocation_authorization_identity": invocation_authorization.identity,
        "invocation_authorization_fingerprint": invocation_authorization.fingerprint,
        "invocation_evidence_fingerprint": invocation.fingerprint.digest,
        "artifact_identity": audit_artifact["id"],
        "artifact_sha256": hashlib.sha256(artifact_bytes).hexdigest(),
        "artifact_filename": audit_artifact["filename"],
        "artifact_media_type": audit_artifact["media_type"],
        "artifact_byte_length": len(artifact_bytes),
        "renderer_identity": invocation_authorization.renderer_identity,
        "renderer_version": invocation_authorization.renderer_version,
        "renderer_implementation_digest": renderer_implementation_digest(),
        "assessor_implementation": ASSESSOR_IMPLEMENTATION_ID,
        "assessor_version": ASSESSOR_IMPLEMENTATION_VERSION,
        "output_class": OUTPUT_CLASS,
        "maximum_artifact_bytes": invocation_authorization.maximum_output_bytes,
        "exclusions": ("manifest-authority", "distribution-authority", "successful-publication-authority", "external-assets", "active-content"),
        "artifact_destination": str(Path(invocation_authorization.output_directory) / invocation_authorization.output_filename),
        "invocation_evidence_destination": str(Path(invocation_authorization.output_directory) / invocation_authorization.evidence_filename),
    }
    for name, value in expected.items():
        if getattr(authorization, name, None) != value:
            findings.append(_finding("authorization-binding-mismatch", f"/authorization/{name}", f"Authorization binds stale or different {name}."))
    document = asdict(authorization)
    scalar_names = set(document) - {"artifact_byte_length", "maximum_artifact_bytes", "exclusions"}
    if any(type(document[name]) is not str for name in scalar_names) or type(authorization.artifact_byte_length) is not int or type(authorization.maximum_artifact_bytes) is not int or type(authorization.exclusions) is not tuple or any(type(item) is not str for item in authorization.exclusions):
        findings.append(_finding("invalid-authorization-type", "/authorization", "Authorization fields have invalid exact types."))
        return tuple(sorted(set(findings)))
    for name in ("identity", "record_identity", "artifact_identity"):
        if not _IDENTITY.fullmatch(getattr(authorization, name)):
            findings.append(_finding("invalid-authorization-identity", f"/authorization/{name}", "Identity syntax is invalid."))
    try:
        canonicalize_timestamp(authorization.authorization_time)
    except (TypeError, ValueError):
        findings.append(_finding("invalid-authorization-time", "/authorization/authorization_time", "Authorization time is invalid."))
    if authorization.fingerprint != compute_conformance_authorization_fingerprint(authorization) or not _DIGEST.fullmatch(authorization.fingerprint):
        findings.append(_finding("authorization-fingerprint-mismatch", "/authorization/fingerprint", "Authorization fingerprint is stale or malformed."))
    evidence_directory = Path(authorization.evidence_directory)
    ledger_directory = Path(authorization.commitment_ledger_directory)
    if (not evidence_directory.is_absolute() or str(evidence_directory.resolve()) != authorization.evidence_directory
            or evidence_directory.is_symlink() or not evidence_directory.is_dir()):
        findings.append(_finding("invalid-evidence-directory", "/authorization/evidence_directory", "Evidence directory is absent or unsafe."))
    if (not ledger_directory.is_absolute() or str(ledger_directory.resolve()) != authorization.commitment_ledger_directory
            or ledger_directory.is_symlink() or not ledger_directory.is_dir()):
        findings.append(_finding("invalid-commitment-ledger", "/authorization/commitment_ledger_directory", "Commitment ledger is absent or unsafe."))
    if authorization.evidence_filename != "semantic-conformance-evidence.json":
        findings.append(_finding("unauthorized-evidence-filename", "/authorization/evidence_filename", "Evidence filename differs from policy."))
    return tuple(sorted(set(findings)))


def _conformance_record(
    invocation: VerifiedRendererInvocation, authorization: SemanticArtifactConformanceAuthorization,
    semantic_evidence: dict[str, Any],
) -> BCRPRecord:
    bundle = invocation.bundle
    audit = bundle.one("GeneratedArtifactAuditRecord")
    ready = bundle.one("ReadyPresentationPackageRecord")
    release = bundle.one("PublicationReleaseRecord")
    payload = {
        "contract_identity": CONFORMANCE_EVIDENCE_CONTRACT,
        "policy_identity": CONFORMANCE_POLICY_ID,
        "profile_identity": authorization.profile_identity,
        "profile_version": authorization.profile_version,
        "assessor": {"identity": authorization.assessor_identity, "owner": authorization.authority_owner, "role": authorization.authority_role},
        "authorization_identity": authorization.identity,
        "authorization_fingerprint": authorization.fingerprint,
        "release_fingerprint": authorization.release_fingerprint,
        "lifecycle_inventory_digest": authorization.lifecycle_inventory_digest,
        "plan_fingerprint": authorization.plan_fingerprint,
        "capability_fingerprint": authorization.capability_fingerprint,
        "invocation_authorization_identity": authorization.invocation_authorization_identity,
        "invocation_authorization_fingerprint": authorization.invocation_authorization_fingerprint,
        "invocation_evidence_fingerprint": authorization.invocation_evidence_fingerprint,
        "artifact_identity": authorization.artifact_identity,
        "artifact_sha256": authorization.artifact_sha256,
        "requirement_accounting": semantic_evidence,
        "authority_scope": "semantic-artifact-conformance-only",
        "manifest_authority": "absent",
        "distribution_authority": "absent",
        "successful_publication": "not-asserted",
    }
    return BCRPRecord(
        kind="SemanticArtifactConformanceRecord", identity=authorization.record_identity,
        profile_version=PROFILE_VERSION,
        semantic={"audit_ref": audit.identity, "ready_ref": ready.identity,
                  "audit_link_pass": True, "semantic_pass": True,
                  "evidence": {
                      "profile": authorization.profile_identity + ":" + authorization.profile_version,
                      "aggregate_verdict": "approved",
                      "requirement_count": len(semantic_evidence["requirement_ids"]),
                      "evidence_sha256": hashlib.sha256(_canonical_bytes(semantic_evidence)).hexdigest(),
                  }},
        extensions=[{
            "owner_namespace": "briefforge-semantic-artifact-conformance", "name": "semantic-realization-evidence",
            "version": "1.0.0", "authority_ref": authorization.authority_identity,
            "scope": "semantic-artifact-conformance-only",
            "target_refs": [release.identity, ready.identity, audit.identity,
                            bundle.one("RendererCompatibilityPlanRecord").identity,
                            bundle.one("RendererCapabilityDeclarationRecord").identity,
                            authorization.artifact_identity],
            "criticality": "required", "character": "semantic",
            "validation_contract": CONFORMANCE_EVIDENCE_CONTRACT, "preservation": "must-preserve",
            "payload": payload,
        }],
    )


def _consumption_name(authorization: SemanticArtifactConformanceAuthorization) -> str:
    return f"{authorization.fingerprint}.conformance-assessment-consumed"


def _consumption_bytes(authorization: SemanticArtifactConformanceAuthorization) -> bytes:
    return _canonical_bytes({
        "contract_identity": "briefforge:semantic-conformance-assessment-consumption:1.0.0",
        "authorization_identity": authorization.identity,
        "authorization_fingerprint": authorization.fingerprint,
        "assessment_scope": "exactly-one-semantic-assessment-act",
    })


def _reserve_assessment(authorization: SemanticArtifactConformanceAuthorization) -> None:
    ledger_fd, ledger_identity = _open_directory(Path(authorization.commitment_ledger_directory))
    try:
        _write_exclusive_at(ledger_fd, _consumption_name(authorization), _consumption_bytes(authorization))
        os.fsync(ledger_fd)
        if (os.fstat(ledger_fd).st_dev, os.fstat(ledger_fd).st_ino) != ledger_identity:
            raise ValueError("Authorized commitment-ledger identity changed during assessment reservation.")
    finally:
        os.close(ledger_fd)


def _commitment_name(authorization: SemanticArtifactConformanceAuthorization) -> str:
    return f"{authorization.fingerprint}.conformance-admitted"


def _commitment_bytes(authorization: SemanticArtifactConformanceAuthorization, evidence_bytes: bytes) -> bytes:
    return _canonical_bytes({
        "contract_identity": "briefforge:semantic-conformance-admission-commitment:1.0.0",
        "authorization_fingerprint": authorization.fingerprint,
        "artifact_sha256": authorization.artifact_sha256,
        "invocation_evidence_fingerprint": authorization.invocation_evidence_fingerprint,
        "conformance_evidence_sha256": hashlib.sha256(evidence_bytes).hexdigest(),
        "conformance_evidence_byte_length": len(evidence_bytes),
    })


def _open_directory(path: Path) -> tuple[int, tuple[int, int]]:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    info = os.fstat(descriptor)
    if not stat.S_ISDIR(info.st_mode):
        os.close(descriptor)
        raise ValueError("Authorized persistence destination is not a directory.")
    return descriptor, (info.st_dev, info.st_ino)


def _write_exclusive_at(directory_fd: int, filename: str, content: bytes) -> None:
    if not filename or filename in {".", ".."} or "/" in filename or os.sep in filename:
        raise ValueError("Persistence filename is not descriptor-relative.")
    descriptor = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=directory_fd)
    try:
        view = memoryview(content)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("Short write made no progress.")
            view = view[written:]
        os.fsync(descriptor)
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_size != len(content):
            raise ValueError("Persisted evidence is not one complete regular file.")
    except BaseException:
        try:
            os.unlink(filename, dir_fd=directory_fd)
            os.fsync(directory_fd)
        except OSError:
            pass
        raise
    finally:
        os.close(descriptor)


def _read_regular_at(directory_fd: int, filename: str, maximum: int) -> bytes:
    descriptor = os.open(filename, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory_fd)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_size > maximum:
            raise ValueError("Persisted evidence is non-regular or exceeds its bound.")
        chunks: list[bytes] = []
        remaining = info.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 65536))
            if not chunk:
                raise ValueError("Persisted evidence was truncated during verification.")
            chunks.append(chunk); remaining -= len(chunk)
        if os.fstat(descriptor)[:3] != info[:3] or os.fstat(descriptor).st_size != info.st_size:
            raise ValueError("Persisted evidence changed during verification.")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _verify_conformance_bundle(
    bundle: BCRPBundle, invocation: VerifiedRendererInvocation,
    authorization: SemanticArtifactConformanceAuthorization, semantic_evidence: dict[str, Any],
) -> VerifiedSemanticArtifactConformance:
    expected_kinds = (
        "PresentationBriefRecord", "PortablePresentationMaterialRecord", "CandidatePresentationPackageRecord",
        "ValidationJudgmentRecord", "ReadyPresentationPackageRecord", "PublicationReleaseRecord",
        "RendererCapabilityDeclarationRecord", "RendererCompatibilityPlanRecord", "GeneratedArtifactAuditRecord",
        "SemanticArtifactConformanceRecord",
    )
    if len(bundle.records) != 10 or any(len(bundle.records_of_kind(kind)) != 1 for kind in expected_kinds):
        raise ValueError("Conformance closure requires the nine-record invocation plus one conformance record.")
    if any(record.kind not in expected_kinds for record in bundle.records):
        raise ValueError("Conformance evidence contains Manifest, distribution, or unknown authority.")
    if tuple(item.to_document() for item in bundle.records[:9]) != tuple(item.to_document() for item in invocation.bundle.records):
        raise ValueError("Conformance evidence does not preserve exact invocation evidence.")
    expected = _conformance_record(invocation, authorization, semantic_evidence)
    if bundle.records[-1].to_document() != expected.to_document():
        raise ValueError("Persisted conformance record differs from independently reproduced evidence.")
    generic = validate_bundle(bundle, through_layer="L5")
    accepted_specialized_extensions = {
        "ValidationJudgmentRecord": "briefforge:legacy-lifecycle-compatibility:1.0.0",
        "ReadyPresentationPackageRecord": "briefforge:legacy-lifecycle-compatibility:1.0.0",
        "PublicationReleaseRecord": "briefforge:publication-release-authorization:1.0.0",
        "RendererCapabilityDeclarationRecord": "briefforge:renderer-capability-declaration:1.0.0",
        "RendererCompatibilityPlanRecord": "briefforge:renderer-compatibility-plan:1.0.0",
        "GeneratedArtifactAuditRecord": "briefforge:controlled-renderer-invocation-evidence:1.0.0",
        "SemanticArtifactConformanceRecord": CONFORMANCE_EVIDENCE_CONTRACT,
    }
    allowed_extension_identities = {
        record.identity
        for record in bundle.records
        if record.kind in accepted_specialized_extensions
        and len(record.extensions) == 1
        and record.extensions[0].get("criticality") == "required"
        and record.extensions[0].get("preservation") == "must-preserve"
        and record.extensions[0].get("validation_contract") == accepted_specialized_extensions[record.kind]
    }
    unexpected = [item for item in generic.findings if not (
        item.layer == "L1"
        and item.family == "extension-boundary"
        and item.severity == "blocking"
        and item.blocking_consequence == "all dependent processing"
        and item.semantic_identity in allowed_extension_identities
        and item.location == "/extensions/0"
        and item.message == "Unknown required semantic extension cannot be processed."
        and item.referenced_identities == ()
    )]
    if unexpected:
        details = "; ".join(f"{item.semantic_identity}{item.location}:{item.message}" for item in unexpected)
        raise ValueError(f"Conformance closure fails generic BCRP validation: {details}")
    fingerprint = fingerprint_bundle(bundle, domain="profile-instance", require_valid=False)
    return VerifiedSemanticArtifactConformance._admitted(_serialize_bundle(bundle), fingerprint)


def _independent_inputs(
    *, artifact_path: Path, invocation_evidence_path: Path, evidence_snapshot: EvidenceSnapshot,
    verified_release: VerifiedPublicationRelease, lifecycle_scope: LifecyclePlanningScope,
    declaration: RendererCapabilityDeclaration, planning_authorization: PlanningAuthorization,
    verified_plan: VerifiedRendererCompatibilityPlan, invocation_authorization: RendererInvocationAuthorization,
) -> tuple[VerifiedRendererInvocation, MinimalHtmlRendererProjection, bytes]:
    invocation = verify_persisted_renderer_invocation(
        artifact_path=artifact_path, evidence_path=invocation_evidence_path,
        evidence_snapshot=evidence_snapshot, lifecycle_scope=lifecycle_scope, declaration=declaration,
        planning_authorization=planning_authorization, authorization=invocation_authorization,
    )
    projection = build_minimal_html_projection(
        verified_release=verified_release, evidence_snapshot=evidence_snapshot, lifecycle_scope=lifecycle_scope,
        declaration=declaration, planning_authorization=planning_authorization, verified_plan=verified_plan,
    )
    if tuple(item.to_document() for item in invocation.bundle.records[:8]) != tuple(item.to_document() for item in verified_plan.bundle.records):
        raise ValueError("Invocation evidence and governed persisted Plan closure differ.")
    return invocation, projection, invocation.artifact_bytes


def assess_semantic_artifact_conformance(
    *, artifact_path: Path, invocation_evidence_path: Path, evidence_snapshot: EvidenceSnapshot,
    verified_release: VerifiedPublicationRelease, lifecycle_scope: LifecyclePlanningScope,
    declaration: RendererCapabilityDeclaration, planning_authorization: PlanningAuthorization,
    verified_plan: VerifiedRendererCompatibilityPlan, invocation_authorization: RendererInvocationAuthorization,
    authorization: SemanticArtifactConformanceAuthorization,
) -> SemanticArtifactConformanceResult:
    """Assess, persist, externally commit, and return one approval only on pass."""
    try:
        invocation, projection, artifact_bytes = _independent_inputs(
            artifact_path=artifact_path, invocation_evidence_path=invocation_evidence_path,
            evidence_snapshot=evidence_snapshot, verified_release=verified_release, lifecycle_scope=lifecycle_scope,
            declaration=declaration, planning_authorization=planning_authorization, verified_plan=verified_plan,
            invocation_authorization=invocation_authorization,
        )
    except Exception as exc:
        return SemanticArtifactConformanceResult((_finding("upstream-reverification-failed", "/inputs", str(exc)),), None)
    findings = _authorization_findings(
        authorization, invocation=invocation, release=verified_release, lifecycle=lifecycle_scope,
        declaration=declaration, plan=verified_plan, invocation_authorization=invocation_authorization,
        artifact_bytes=artifact_bytes,
    )
    if findings:
        return SemanticArtifactConformanceResult(findings, None)
    try:
        _reserve_assessment(authorization)
    except Exception as exc:
        return SemanticArtifactConformanceResult((_finding("assessment-authorization-consumed", "/authorization/fingerprint", str(exc)),), None)
    try:
        semantic_evidence = verify_exact_semantic_html(artifact_bytes, projection)
        semantic_evidence = _bind_authority_audit_links(semantic_evidence, invocation, authorization)
    except Exception:
        return SemanticArtifactConformanceResult(_complete_semantic_findings(artifact_bytes, projection), None)
    try:
        bundle = BCRPBundle(invocation.bundle.profile_identity, invocation.bundle.profile_version,
                            invocation.bundle.records + (_conformance_record(invocation, authorization, semantic_evidence),))
        verified = _verify_conformance_bundle(bundle, invocation, authorization, semantic_evidence)
    except Exception as exc:
        return SemanticArtifactConformanceResult((_finding("conformance-closure-failed", "/closure", str(exc)),), None)
    evidence_bytes = verified._bundle_document.encode("utf-8")
    evidence_path = Path(authorization.evidence_directory) / authorization.evidence_filename
    commitment_path = Path(authorization.commitment_ledger_directory) / _commitment_name(authorization)
    evidence_created = False
    commitment_created = False
    evidence_fd = ledger_fd = -1
    try:
        evidence_fd, evidence_identity = _open_directory(Path(authorization.evidence_directory))
        ledger_fd, ledger_identity = _open_directory(Path(authorization.commitment_ledger_directory))
        _write_exclusive_at(evidence_fd, authorization.evidence_filename, evidence_bytes)
        evidence_created = True
        os.fsync(evidence_fd)
        try:
            _write_exclusive_at(ledger_fd, _commitment_name(authorization), _commitment_bytes(authorization, evidence_bytes))
            commitment_created = True
            os.fsync(ledger_fd)
        except Exception:
            os.unlink(authorization.evidence_filename, dir_fd=evidence_fd)
            os.fsync(evidence_fd)
            evidence_created = False
            raise
        if (os.fstat(evidence_fd).st_dev, os.fstat(evidence_fd).st_ino) != evidence_identity or (os.fstat(ledger_fd).st_dev, os.fstat(ledger_fd).st_ino) != ledger_identity:
            raise ValueError("Authorized directory identity changed during persistence.")
        reloaded = verify_persisted_semantic_artifact_conformance(
            artifact_path=artifact_path, invocation_evidence_path=invocation_evidence_path,
            conformance_evidence_path=evidence_path, evidence_snapshot=evidence_snapshot,
            verified_release=verified_release, lifecycle_scope=lifecycle_scope, declaration=declaration,
            planning_authorization=planning_authorization, verified_plan=verified_plan,
            invocation_authorization=invocation_authorization, authorization=authorization,
        )
        return SemanticArtifactConformanceResult((), reloaded)
    except Exception as exc:
        if commitment_created:
            try:
                os.unlink(_commitment_name(authorization), dir_fd=ledger_fd)
                os.fsync(ledger_fd)
            except OSError: pass
        if evidence_created:
            try:
                os.unlink(authorization.evidence_filename, dir_fd=evidence_fd)
                os.fsync(evidence_fd)
            except OSError: pass
        return SemanticArtifactConformanceResult((_finding("conformance-persistence-failed", "/evidence", str(exc)),), None)
    finally:
        if evidence_fd >= 0: os.close(evidence_fd)
        if ledger_fd >= 0: os.close(ledger_fd)


def verify_persisted_semantic_artifact_conformance(
    *, artifact_path: Path, invocation_evidence_path: Path, conformance_evidence_path: Path,
    evidence_snapshot: EvidenceSnapshot, verified_release: VerifiedPublicationRelease,
    lifecycle_scope: LifecyclePlanningScope, declaration: RendererCapabilityDeclaration,
    planning_authorization: PlanningAuthorization, verified_plan: VerifiedRendererCompatibilityPlan,
    invocation_authorization: RendererInvocationAuthorization,
    authorization: SemanticArtifactConformanceAuthorization,
) -> VerifiedSemanticArtifactConformance:
    """Independently reload and reproduce canonical conformance and commitment."""
    expected_path = Path(authorization.evidence_directory) / authorization.evidence_filename
    if conformance_evidence_path != expected_path:
        raise ValueError("Conformance evidence path differs from authorization.")
    invocation, projection, artifact_bytes = _independent_inputs(
        artifact_path=artifact_path, invocation_evidence_path=invocation_evidence_path,
        evidence_snapshot=evidence_snapshot, verified_release=verified_release, lifecycle_scope=lifecycle_scope,
        declaration=declaration, planning_authorization=planning_authorization, verified_plan=verified_plan,
        invocation_authorization=invocation_authorization,
    )
    findings = _authorization_findings(
        authorization, invocation=invocation, release=verified_release, lifecycle=lifecycle_scope,
        declaration=declaration, plan=verified_plan, invocation_authorization=invocation_authorization,
        artifact_bytes=artifact_bytes,
    )
    if findings:
        raise ValueError("Persisted conformance authorization is stale or contradictory.")
    semantic_evidence = verify_exact_semantic_html(artifact_bytes, projection)
    semantic_evidence = _bind_authority_audit_links(semantic_evidence, invocation, authorization)
    evidence_fd, evidence_identity = _open_directory(Path(authorization.evidence_directory))
    ledger_fd, ledger_identity = _open_directory(Path(authorization.commitment_ledger_directory))
    try:
        evidence_bytes = _read_regular_at(evidence_fd, authorization.evidence_filename, 4 * 1024 * 1024)
        consumption_bytes = _read_regular_at(ledger_fd, _consumption_name(authorization), 4096)
        commitment_bytes = _read_regular_at(ledger_fd, _commitment_name(authorization), 4096)
        if (os.fstat(evidence_fd).st_dev, os.fstat(evidence_fd).st_ino) != evidence_identity or (os.fstat(ledger_fd).st_dev, os.fstat(ledger_fd).st_ino) != ledger_identity:
            raise ValueError("Authorized directory identity changed during verification.")
    finally:
        os.close(evidence_fd); os.close(ledger_fd)
    try:
        evidence_text = evidence_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Conformance evidence is not UTF-8.") from exc
    bundle = _deserialize_bundle(evidence_text)
    if evidence_text != _serialize_bundle(bundle):
        raise ValueError("Conformance evidence bytes are not canonical.")
    verified = _verify_conformance_bundle(bundle, invocation, authorization, semantic_evidence)
    if consumption_bytes != _consumption_bytes(authorization):
        raise ValueError("One-assessment authorization consumption evidence is absent or mismatched.")
    if commitment_bytes != _commitment_bytes(authorization, evidence_bytes):
        raise ValueError("External conformance admission commitment is absent or mismatched.")
    return verified
