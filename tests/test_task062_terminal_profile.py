from pathlib import Path
import tempfile
import unittest

from briefforge.bounded_loopback_deployment import DeploymentRouteItem, DeploymentTarget
from briefforge.publication_distribution_delivery import _released_destination_scope
from briefforge.bounded_loopback_deployment import _released_loopback_deployment_scope
from briefforge.technical_publication_verification import _released_technical_verification_scope
from briefforge_terminal_profile.profile import (
    PROFILE_IDENTITY,
    PROFILE_VERSION,
    TERMINAL_OPERATIONAL_IDENTITIES,
    build_terminal_authority_profile,
    verify_terminal_authority_profile,
)


class Task062ClosedTerminalAuthorityProfileTests(unittest.TestCase):
    def test_exact_eight_release_resident_operational_authorities_and_scope_parity(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            destination = root / "destination"
            delivery_ledger = root / "delivery-ledger"
            deployment_ledger = root / "deployment-ledger"
            verification_ledger = root / "verification-ledger"
            for path in (destination, delivery_ledger, deployment_ledger, verification_ledger):
                path.mkdir()
                path.chmod(0o700)
            target = DeploymentTarget("127.0.0.1", 38127, "http://127.0.0.1:38127")
            routes = (DeploymentRouteItem("/brief.html", "brief.html", "text/html"),)
            profile = build_terminal_authority_profile(
                destination_parent=destination,
                destination_basename="brief.html",
                delivery_ledger=delivery_ledger,
                target=target,
                routes=routes,
                deployment_ledger=deployment_ledger,
                verification_ledger=verification_ledger,
                content_authorities=({"id":"authority:synthetic-content", "owner_identity":"project:BriefForge",
                                      "role":"presentation-content-authority",
                                      "scope":"released-presentation-semantic-content"},),
            )
            verify_terminal_authority_profile(profile)
            self.assertEqual(PROFILE_IDENTITY, profile.profile_identity)
            self.assertEqual(PROFILE_VERSION, profile.profile_version)
            self.assertEqual(TERMINAL_OPERATIONAL_IDENTITIES, tuple(item["id"] for item in profile.operational_authorities))
            self.assertEqual(8, len(profile.operational_authorities))
            by_id = {item["id"]: item for item in profile.operational_authorities}
            self.assertEqual(_released_destination_scope(destination, "brief.html", delivery_ledger),
                             by_id["authority:briefforge-controlled-local-delivery"]["scope"])
            self.assertEqual(_released_loopback_deployment_scope(target, routes, deployment_ledger),
                             by_id["authority:briefforge-bounded-loopback-deployment"]["scope"])
            self.assertEqual(_released_technical_verification_scope(target, routes, verification_ledger),
                             by_id["authority:briefforge-technical-publication-verifier"]["scope"])


if __name__ == "__main__":
    unittest.main()
