"""Downstream consumption boundary for Ready Presentation Packages.

The boundary exposes semantic package substance from a Ready Presentation Package
without granting downstream authority. It does not render, serialize, persist,
export, network, template, visualize, search, map, route, or serve packages.
"""

from dataclasses import dataclass

from .promotion import ReadyPresentationPackage


@dataclass(frozen=True)
class DownstreamSemanticPackage:
    """Read-only semantic access to an already-ready presentation package."""

    ready_package: ReadyPresentationPackage

    @property
    def identity(self):
        return self.ready_package.candidate.identity

    @property
    def organizing_purpose(self):
        return self.ready_package.candidate.organizing_purpose

    @property
    def statements(self):
        return self.ready_package.candidate.statements

    @property
    def upstream_references(self):
        return self.ready_package.candidate.upstream_references

    @property
    def obligations(self):
        return self.ready_package.candidate.obligations

    @property
    def validation_judgment(self):
        return self.ready_package.validation_judgment

    @property
    def semantic_fingerprint(self):
        return self.ready_package.semantic_fingerprint

    @property
    def validation_policy_id(self):
        return self.ready_package.validation_policy_id


class DownstreamBoundaryRejected(TypeError):
    """Raised when a non-ready object attempts to cross the boundary."""


def prepare_downstream_semantic_package(ready_package: ReadyPresentationPackage) -> DownstreamSemanticPackage:
    """Expose semantic access only for Ready Presentation Packages."""

    if not isinstance(ready_package, ReadyPresentationPackage):
        raise DownstreamBoundaryRejected("Only Ready Presentation Packages may cross the downstream boundary.")

    return DownstreamSemanticPackage(ready_package=ready_package)
