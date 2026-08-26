"""Fail-closed lifecycle-event validation and deterministic state projection."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import json
import re
from typing import Iterable

from .canonical import canonicalize_timestamp
from .model import (
    BCRP_CANONICALIZATION_ID,
    BCRP_PROFILE_ID,
    PROFILE_ID,
    PROFILE_VERSION,
    DerivedLifecycleState,
    LifecycleBundle,
    LifecycleFinding,
    LifecyclePolicy,
    LifecycleValidationResult,
    PublicationLifecycleEvent,
    ReleaseBinding,
    ReleaseReference,
)

_IDENTITY_RE = re.compile(r"^[a-z][a-z0-9-]*:[A-Za-z0-9._:-]+$")
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_EVENT_TYPES = {"staleness-declaration", "supersession", "withdrawal"}
_EVENT_REASON_MATRIX = {
    "supersession": {"correction", "replacement"},
    "withdrawal": {"authority-withdrawal"},
    "staleness-declaration": {"currency-concern"},
}
_EVENT_CONSEQUENCE = {
    "supersession": "predecessor-ineligible-successor-current",
    "withdrawal": "target-ineligible-withdrawn",
    "staleness-declaration": "target-ineligible-stale",
}
_EXTENSION_KEYS = {
    "owner_namespace", "name", "version", "authority_ref", "scope", "target_refs", "criticality",
    "character", "validation_contract", "preservation", "payload",
}
_EXTENSION_ENVELOPE_CONTRACT = "publication-lifecycle:core-extension-envelope:1.0.0"
_SUPPORTED_REQUIRED_EXTENSIONS: frozenset[tuple[str, str, str, str]] = frozenset()


def _finding(code: str, identity: str, location: str, message: str) -> LifecycleFinding:
    return LifecycleFinding(code, identity or "bundle", location, message, True)


def _parse_time(value: str) -> datetime | None:
    try:
        normalized = canonicalize_timestamp(value)
        return datetime.fromisoformat(normalized[:-1] + "+00:00")
    except (TypeError, ValueError):
        return None


def _valid_identity(value: str) -> bool:
    return isinstance(value, str) and bool(_IDENTITY_RE.fullmatch(value))


def _release_binding_findings(binding: ReleaseBinding) -> list[LifecycleFinding]:
    invalid = (
        not _valid_identity(binding.identity)
        or not _valid_identity(binding.publication_identity)
        or not isinstance(binding.semantic_publication_version, str)
        or not binding.semantic_publication_version
        or binding.fingerprint_domain != "release-semantic"
        or binding.fingerprint_profile_identity != BCRP_PROFILE_ID
        or binding.fingerprint_profile_version != "1.0.0"
        or binding.fingerprint_canonicalization != BCRP_CANONICALIZATION_ID
        or binding.fingerprint_algorithm != "sha256"
        or binding.fingerprint_root_identity != binding.identity
        or not _DIGEST_RE.fullmatch(binding.fingerprint)
        or _parse_time(binding.publication_time) is None
    )
    return [_finding("invalid-release-binding", binding.identity, "/release-binding", "Release binding is not an exact negotiated BCRP 1.0 release-semantic fingerprint binding.")] if invalid else []


def _check_reference(
    event: PublicationLifecycleEvent,
    reference: ReleaseReference,
    release_by_id: dict[str, ReleaseBinding],
    location: str,
) -> list[LifecycleFinding]:
    findings: list[LifecycleFinding] = []
    if not reference.identity:
        return [_finding("missing-target-release" if location == "/semantic/target_release" else "missing-release-reference", event.identity, location, "Required exact Release reference is absent.")]
    release = release_by_id.get(reference.identity)
    if release is None:
        return [_finding("unknown-release", event.identity, location, "Referenced Release is absent from the explicitly bounded trusted catalog.")]
    if reference.fingerprint != release.fingerprint:
        findings.append(_finding("release-fingerprint-mismatch", event.identity, location + "/fingerprint", "Release identity exists but the exact release-semantic fingerprint does not match."))
    if event.publication_identity != release.publication_identity:
        findings.append(_finding("cross-publication-release", event.identity, location, "Lifecycle event and referenced Release have different publication identities."))
    return findings


def _extension_findings(event: PublicationLifecycleEvent) -> list[LifecycleFinding]:
    findings: list[LifecycleFinding] = []
    seen: set[tuple[str, str, str, str]] = set()
    for index, encoded in enumerate(event.extension_documents):
        location = f"/extensions/{index}"
        try:
            extension = json.loads(encoded)
        except (TypeError, ValueError):
            findings.append(_finding("invalid-extension-envelope", event.identity, location, "Extension is not canonical JSON transport material."))
            continue
        if not isinstance(extension, dict) or set(extension) != _EXTENSION_KEYS:
            findings.append(_finding("invalid-extension-envelope", event.identity, location, "Extension must contain exactly the declared envelope fields."))
            continue
        string_keys = _EXTENSION_KEYS - {"target_refs", "payload"}
        if any(not isinstance(extension[key], str) or not extension[key] for key in string_keys):
            findings.append(_finding("invalid-extension-envelope", event.identity, location, "Extension envelope string fields must be non-empty strings."))
            continue
        refs = extension["target_refs"]
        if not isinstance(refs, list) or refs != [event.identity]:
            findings.append(_finding("invalid-extension-envelope", event.identity, location + "/target_refs", "Event extension must target exactly its containing event."))
        if extension["authority_ref"] != event.authority.identity or extension["scope"] != "event":
            findings.append(_finding("invalid-extension-envelope", event.identity, location, "Extension authority and scope must bind the containing event authority."))
        if extension["character"] != "semantic" or extension["preservation"] != "must-preserve":
            findings.append(_finding("invalid-extension-envelope", event.identity, location, "Lifecycle extensions must be semantic and must-preserve."))
        if extension["validation_contract"] != _EXTENSION_ENVELOPE_CONTRACT:
            findings.append(_finding("unknown-required-extension" if extension["criticality"] == "required" else "invalid-extension-envelope", event.identity, location, "Extension contract is not understood by this exact profile."))
        key = (extension["owner_namespace"], extension["name"], extension["version"], extension["validation_contract"])
        if key in seen:
            findings.append(_finding("duplicate-extension", event.identity, location, "Duplicate extension identity is ambiguous."))
        seen.add(key)
        if extension["criticality"] not in {"optional", "required"}:
            findings.append(_finding("invalid-extension-envelope", event.identity, location + "/criticality", "Extension criticality must be optional or required."))
        elif extension["criticality"] == "required" and key not in _SUPPORTED_REQUIRED_EXTENSIONS:
            findings.append(_finding("unknown-required-extension", event.identity, location, "Required extension semantics are not registered as understood."))
    return findings


def _has_cycle(graph: dict[str, set[str]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(child) for child in graph.get(node, set())):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def _project_states(
    releases: tuple[ReleaseBinding, ...], events: tuple[PublicationLifecycleEvent, ...]
) -> tuple[dict[str, str], list[str]]:
    outgoing: set[str] = {
        event.predecessor_release.identity
        for event in events
        if event.event_type == "supersession" and event.predecessor_release is not None and event.successor_release is not None
    }
    states = {release.identity: ("superseded" if release.identity in outgoing else "current") for release in releases}
    for event in events:
        if event.event_type == "withdrawal" and event.target_release.identity in states:
            states[event.target_release.identity] = "withdrawn"
        elif event.event_type == "staleness-declaration" and event.target_release.identity in states:
            states[event.target_release.identity] = "stale-by-declaration"
    current = sorted(identity for identity, state in states.items() if state == "current")
    return states, current


def validate_lifecycle(
    bundle: LifecycleBundle,
    releases: Iterable[ReleaseBinding],
    policies: Iterable[LifecyclePolicy],
) -> LifecycleValidationResult:
    findings: list[LifecycleFinding] = []
    release_tuple = tuple(releases)
    policy_tuple = tuple(policies)
    if bundle.profile_identity != PROFILE_ID or bundle.profile_version != PROFILE_VERSION:
        findings.append(_finding("unsupported-profile-version", "bundle", "/profile", "Exact lifecycle profile negotiation failed."))

    release_by_id: dict[str, ReleaseBinding] = {}
    for release in release_tuple:
        if release.identity in release_by_id:
            findings.append(_finding("duplicate-release-identity", release.identity, "/releases", "Release identities must be unique."))
        release_by_id[release.identity] = release
        findings.extend(_release_binding_findings(release))
    if not release_tuple:
        findings.append(_finding("empty-release-catalog", "bundle", "/releases", "Lifecycle derivation requires at least one exact immutable Release binding."))
    release_publications = {release.publication_identity for release in release_tuple}
    if len(release_publications) > 1:
        findings.append(_finding("cross-publication-release", "bundle", "/releases", "One lifecycle projection cannot combine Release bindings from multiple publications."))

    policy_by_id: dict[str, LifecyclePolicy] = {}
    for item in policy_tuple:
        if item.identity in policy_by_id:
            findings.append(_finding("duplicate-policy-identity", item.identity, "/policies", "Policy identities must be unique."))
        policy_by_id[item.identity] = item

    event_by_id: dict[str, PublicationLifecycleEvent] = {}
    for event in bundle.events:
        if event.identity in event_by_id:
            findings.append(_finding("duplicate-event-identity", event.identity, "/events", "Event identities must be unique."))
        event_by_id[event.identity] = event

    supersession_events: list[PublicationLifecycleEvent] = []
    terminal_by_target: dict[str, list[PublicationLifecycleEvent]] = defaultdict(list)
    position_groups: dict[tuple[tuple[str, ...], str], list[str]] = defaultdict(list)

    for event in bundle.events:
        if not _valid_identity(event.identity):
            findings.append(_finding("invalid-event-identity", event.identity, "/identity", "Event identity must be explicit and canonical."))
        if event.profile_identity != PROFILE_ID or event.profile_version != PROFILE_VERSION:
            findings.append(_finding("unsupported-profile-version", event.identity, "/profile", "Event uses an unsupported profile identity or version."))
        if not _valid_identity(event.publication_identity):
            findings.append(_finding("invalid-publication-identity", event.identity, "/semantic/publication_identity", "Publication identity must be explicit and canonical."))
        if event.event_type not in _EVENT_TYPES:
            findings.append(_finding("unsupported-event-type", event.identity, "/semantic/event_type", "Event type is not understood by this exact profile."))
        if event.reason_classification not in _EVENT_REASON_MATRIX.get(event.event_type, set()):
            findings.append(_finding("invalid-event-reason", event.identity, "/semantic/reason_classification", "Reason classification is not valid for this event type."))
        if not event.reason_detail:
            findings.append(_finding("missing-reason-detail", event.identity, "/semantic/reason_detail", "Governed lifecycle actions require an explicit reason detail."))
        if not all((_valid_identity(event.authority.identity), _valid_identity(event.authority.owner), bool(event.authority.role))):
            findings.append(_finding("missing-authority", event.identity, "/semantic/authority", "Authority identity, owner, and role are required."))
        if not _valid_identity(event.policy_identity):
            findings.append(_finding("missing-policy", event.identity, "/semantic/policy_identity", "A canonical explicit policy identity is required."))
        event_time = _parse_time(event.event_time)
        if event_time is None:
            findings.append(_finding("invalid-event-time", event.identity, "/semantic/event_time", "Event time must be explicit and canonicalizable."))
        if len(set(event.predecessor_event_refs)) != len(event.predecessor_event_refs):
            findings.append(_finding("duplicate-predecessor-event", event.identity, "/semantic/predecessor_event_refs", "Causal predecessor identities must be unique."))
        if event.distribution_consequence != _EVENT_CONSEQUENCE.get(event.event_type):
            findings.append(_finding("invalid-distribution-consequence", event.identity, "/semantic/distribution_consequence", "Distribution consequence does not match the event type."))
        policy = policy_by_id.get(event.policy_identity)
        if policy is None:
            findings.append(_finding("unknown-policy", event.identity, "/semantic/policy_identity", "Named lifecycle policy was not supplied at the trusted boundary."))
        else:
            authority_key = (event.authority.identity, event.authority.owner, event.authority.role)
            if authority_key not in policy.allowed_authorities:
                findings.append(_finding("unauthorized-event-authority", event.identity, "/semantic/authority", "Event authority identity, owner, and role are outside the named policy."))
            if event.event_type not in policy.allowed_event_types or event.reason_classification not in policy.allowed_reason_classifications:
                findings.append(_finding("unauthorized-policy-action", event.identity, "/semantic", "Policy does not authorize this event type or reason."))
            if (event.event_type, event.distribution_consequence) not in policy.distribution_consequences:
                findings.append(_finding("unauthorized-distribution-consequence", event.identity, "/semantic/distribution_consequence", "Policy does not authorize the declared consequence."))

        findings.extend(_check_reference(event, event.target_release, release_by_id, "/semantic/target_release"))
        if event.event_type == "supersession":
            supersession_events.append(event)
            if event.predecessor_release is None:
                findings.append(_finding("missing-predecessor-release", event.identity, "/semantic/predecessor_release", "Supersession requires an exact predecessor Release."))
            else:
                findings.extend(_check_reference(event, event.predecessor_release, release_by_id, "/semantic/predecessor_release"))
                if event.predecessor_release != event.target_release:
                    findings.append(_finding("target-predecessor-mismatch", event.identity, "/semantic/predecessor_release", "Supersession target and predecessor must be the same exact Release."))
            if event.successor_release is None:
                findings.append(_finding("missing-successor-release", event.identity, "/semantic/successor_release", "Supersession requires a distinct exact successor Release."))
            else:
                findings.extend(_check_reference(event, event.successor_release, release_by_id, "/semantic/successor_release"))
                if event.successor_release.identity == event.target_release.identity:
                    findings.append(_finding("self-supersession", event.identity, "/semantic/successor_release", "A Release cannot supersede itself."))
        elif event.predecessor_release is not None or event.successor_release is not None:
            findings.append(_finding("invalid-release-relationship", event.identity, "/semantic", "Only supersession carries predecessor and successor Release relationships."))

        target_time = release_by_id.get(event.target_release.identity)
        if event_time is not None and target_time is not None:
            release_time = _parse_time(target_time.publication_time)
            if release_time is not None and event_time <= release_time:
                findings.append(_finding("event-before-release", event.identity, "/semantic/event_time", "Lifecycle event must occur after its target Release publication time."))
                findings.append(_finding("event-time-contradiction", event.identity, "/semantic/event_time", "Lifecycle event time contradicts the target Release publication time."))
        if event.event_type == "supersession" and event.successor_release is not None and event_time is not None:
            successor = release_by_id.get(event.successor_release.identity)
            successor_time = _parse_time(successor.publication_time) if successor is not None else None
            if successor_time is not None and event_time <= successor_time:
                findings.append(_finding("event-time-contradiction", event.identity, "/semantic/event_time", "Supersession event must occur after successor Release publication time."))

        terminal_by_target[event.target_release.identity].append(event)
        position_groups[(tuple(sorted(event.predecessor_event_refs)), event.target_release.identity)].append(event.identity)
        findings.extend(_extension_findings(event))

    supersession_graph: dict[str, set[str]] = defaultdict(set)
    incoming: dict[str, list[str]] = defaultdict(list)
    outgoing: dict[str, list[str]] = defaultdict(list)
    introduction_event: dict[str, str] = {}
    for event in supersession_events:
        if event.predecessor_release is None or event.successor_release is None:
            continue
        predecessor = event.predecessor_release.identity
        successor = event.successor_release.identity
        supersession_graph[predecessor].add(successor)
        outgoing[predecessor].append(successor)
        incoming[successor].append(predecessor)
        introduction_event[successor] = event.identity
    for predecessor, successors in outgoing.items():
        if len(successors) > 1:
            findings.append(_finding("competing-successor", predecessor, "/events", "One predecessor has multiple declared successors."))
    for successor, predecessors in incoming.items():
        if len(predecessors) > 1:
            findings.append(_finding("competing-predecessor", successor, "/events", "One successor has multiple declared predecessors."))
    if _has_cycle(supersession_graph):
        findings.append(_finding("supersession-cycle", "bundle", "/events", "Supersession graph contains a cycle."))

    if release_tuple and len(release_publications) == 1:
        roots = sorted(set(release_by_id) - set(incoming))
        if len(roots) != 1:
            findings.append(_finding("release-graph-root-cardinality", "bundle", "/releases", "Lifecycle projection requires exactly one explicitly connected initial Release root."))
        elif len(release_by_id) > 1:
            reached: set[str] = set()
            stack = [roots[0]]
            while stack:
                node = stack.pop()
                if node in reached:
                    continue
                reached.add(node)
                stack.extend(supersession_graph.get(node, set()))
            if reached != set(release_by_id):
                findings.append(_finding("orphan-release", "bundle", "/releases", "Every non-root Release must be introduced by one explicit supersession edge."))

    event_graph: dict[str, set[str]] = defaultdict(set)
    for event in bundle.events:
        expected_introduction = introduction_event.get(event.target_release.identity)
        if expected_introduction is not None and event.identity != expected_introduction and expected_introduction not in event.predecessor_event_refs:
            findings.append(_finding("predecessor-event-contradiction", event.identity, "/semantic/predecessor_event_refs", "Event targeting an introduced Release must cite the event that introduced it."))
        for predecessor_identity in event.predecessor_event_refs:
            predecessor = event_by_id.get(predecessor_identity)
            if predecessor is None:
                findings.append(_finding("unknown-predecessor-event", event.identity, "/semantic/predecessor_event_refs", "Causal predecessor event is absent."))
                continue
            event_graph[predecessor_identity].add(event.identity)
            if predecessor.publication_identity != event.publication_identity:
                findings.append(_finding("cross-publication-event", event.identity, "/semantic/predecessor_event_refs", "Causal event references cannot cross publication identity."))
            predecessor_output = predecessor.successor_release.identity if predecessor.event_type == "supersession" and predecessor.successor_release is not None else predecessor.target_release.identity
            if predecessor_output != event.target_release.identity:
                findings.append(_finding("predecessor-event-contradiction", event.identity, "/semantic/predecessor_event_refs", "Causal predecessor does not establish or govern this event target Release."))
            earlier = _parse_time(predecessor.event_time)
            later = _parse_time(event.event_time)
            if earlier is not None and later is not None and earlier >= later:
                findings.append(_finding("event-time-contradiction", event.identity, "/semantic/predecessor_event_refs", "Causal predecessor event must be earlier than the referencing event."))
    if _has_cycle(event_graph):
        findings.append(_finding("event-order-cycle", "bundle", "/events", "Predecessor-event graph contains a cycle."))

    for target, events in terminal_by_target.items():
        if len(events) > 1:
            findings.append(_finding("conflicting-terminal-events", target, "/events", "More than one lifecycle action competes for the same Release target."))
        withdrawals = [event for event in events if event.event_type == "withdrawal"]
        if len(withdrawals) > 1:
            findings.append(_finding("conflicting-withdrawals", target, "/events", "Multiple withdrawal declarations target one Release."))
    for (predecessors, target), identities in position_groups.items():
        if len(identities) > 1:
            findings.append(_finding("ambiguous-event-position", target, "/events", "Multiple events occupy the same causal predecessor position for one Release."))

    states, current = _project_states(release_tuple, bundle.events)
    if len(current) > 1:
        findings.append(_finding("ambiguous-current-release", "bundle", "/releases", "More than one Release remains eligible; version or time ordering cannot select authority."))

    unique = {(item.code, item.event_identity, item.location, item.message): item for item in findings}
    ordered = tuple(unique[key] for key in sorted(unique))
    return LifecycleValidationResult(ordered)


def derive_current_state(
    bundle: LifecycleBundle,
    releases: Iterable[ReleaseBinding],
    policies: Iterable[LifecyclePolicy],
) -> DerivedLifecycleState:
    release_tuple = tuple(releases)
    result = validate_lifecycle(bundle, release_tuple, policies)
    if result.blocking:
        codes = ", ".join(sorted({finding.code for finding in result.findings}))
        raise ValueError(f"lifecycle state derivation blocked: {codes}")
    states, current = _project_states(release_tuple, bundle.events)
    publication_identity = next(iter({release.publication_identity for release in release_tuple}))
    return DerivedLifecycleState(
        publication_identity=publication_identity,
        current_release_identity=current[0] if current else None,
        release_states=tuple(sorted(states.items())),
        applied_event_identities=tuple(sorted(event.identity for event in bundle.events)),
    )
