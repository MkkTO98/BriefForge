"""Promotion boundary for Ready Presentation Packages.

Promotion consumes a Candidate Presentation Package and a successful Validation
Judgment for that same candidate. It does not validate, mutate, render,
serialize, persist, export, network, template, visualize, or serve packages.
"""

from dataclasses import dataclass

from .runtime import CandidatePresentationPackage, semantic_fingerprint
from .validation import ValidationJudgment


@dataclass(frozen=True)
class ReadyPresentationPackage:
    """A candidate package accepted as ready by a matching validation judgment."""

    candidate: CandidatePresentationPackage
    validation_judgment: ValidationJudgment
    semantic_fingerprint: str
    validation_policy_id: str


class PromotionRejected(ValueError):
    """Raised when a candidate cannot cross the readiness boundary."""


def promote_candidate_presentation_package(
    candidate: CandidatePresentationPackage,
    judgment: ValidationJudgment,
) -> ReadyPresentationPackage:
    """Promote a candidate only when an existing judgment authorizes readiness."""

    if not judgment.valid:
        raise PromotionRejected("Cannot promote candidate with an invalid Validation Judgment.")

    if not isinstance(judgment.validation_policy_id, str) or not judgment.validation_policy_id.strip():
        raise PromotionRejected("Validation Judgment requires a validation policy identity.")

    candidate_package_id = None
    if candidate.identity is not None:
        candidate_package_id = candidate.identity.package_id

    if judgment.candidate_package_id != candidate_package_id:
        raise PromotionRejected("Validation Judgment does not belong to this Candidate Presentation Package.")

    candidate_semantic_fingerprint = semantic_fingerprint(candidate)
    if judgment.candidate_semantic_fingerprint != candidate_semantic_fingerprint:
        raise PromotionRejected("Validation Judgment does not match this candidate's current semantic substance.")

    return ReadyPresentationPackage(
        candidate=candidate,
        validation_judgment=judgment,
        semantic_fingerprint=judgment.candidate_semantic_fingerprint,
        validation_policy_id=judgment.validation_policy_id,
    )
