"""Synthetic, offline regression tests for fail-closed Kaigo Ops deploy verification."""
import unittest
from unittest.mock import patch

from scripts import verify_kaigo_ops_production as gate


SHA = "a" * 40
OTHER = "b" * 40
START = 1_791_400_000_000


def row(sha=SHA, state="READY", created=START + 1000, **changes):
    result = {
        "id": "dpl_Expected123", "created": created,
        "state": state, "target": "production",
        "meta": {
            "githubCommitSha": sha, "githubRepo": gate.EXPECTED_REPO,
            "githubOrg": gate.EXPECTED_ORG,
        },
    }
    result.update(changes)
    return result


def detail(sha=SHA, state="READY", **changes):
    result = {
        "id": "dpl_Expected123", "readyState": state, "target": "production",
        "project": {"id": gate.PROJECT_ID},
        "meta": {
            "githubCommitSha": sha, "githubRepo": gate.EXPECTED_REPO,
            "githubOrg": gate.EXPECTED_ORG,
        },
    }
    result.update(changes)
    return result


def replies(*, deployments=None, deployment_detail=None, alias_id="dpl_Expected123"):
    return [
        {"deployments": deployments if deployments is not None else [row()]},
        deployment_detail if deployment_detail is not None else detail(),
        {"projectId": gate.PROJECT_ID, "deploymentId": alias_id},
    ]


class ProductionDeployGateTests(unittest.TestCase):
    def test_all_11_routes_are_unique_and_include_expected_journeys(self):
        self.assertEqual(len(gate.ROUTES), 11)
        self.assertEqual(len(set(gate.ROUTES)), 11)
        self.assertIn("/issues/communication-collaboration", gate.ROUTES)
        self.assertIn("/issues/productivity-utilization", gate.ROUTES)
        self.assertIn("/tools/documentation-review", gate.ROUTES)

    def test_only_new_exact_sha_production_commit_matches(self):
        candidates = [
            row(sha=OTHER, created=START + 5000),
            row(created=START - 10000),
            row(created=START + 2000, target="preview"),
            row(created=START + 3000, meta={
                "githubCommitSha": SHA, "githubRepo": "other", "githubOrg": "other"}),
        ]
        self.assertIsNone(gate.matching_deployment(candidates, SHA, START))
        self.assertEqual(
            gate.matching_deployment(candidates + [row()], SHA, START)["id"],
            "dpl_Expected123",
        )

    def test_expected_deployment_error_or_cancel_fails_closed(self):
        for state in ("ERROR", "CANCELED", "BLOCKED"):
            with self.subTest(state=state):
                with self.assertRaisesRegex(gate.VerificationError, state):
                    gate.matching_deployment([row(state=state)], SHA, START)

    def test_pending_deployment_does_not_pass(self):
        self.assertIsNone(gate.matching_deployment([row(state="BUILDING")], SHA, START))

    @patch.object(gate, "route_ok")
    @patch.object(gate, "api_json")
    def test_ready_sha_alias_and_every_route_required(self, fake_api, fake_route):
        fake_api.side_effect = replies()
        deployment_id, message = gate.verify_once(SHA, START, "placeholder-token")
        self.assertEqual(deployment_id, "dpl_Expected123")
        self.assertEqual(message, "verified")
        self.assertEqual([call.args[0] for call in fake_route.call_args_list],
                         list(gate.ROUTES))
        self.assertEqual(fake_api.call_count, 3)
        self.assertIn("projectId=", fake_api.call_args_list[0].args[0])
        self.assertIn("teamId=", fake_api.call_args_list[0].args[0])
        self.assertEqual(fake_api.call_args_list[0].args[1], "placeholder-token")

    @patch.object(gate, "route_ok")
    @patch.object(gate, "api_json")
    def test_alias_on_previous_deployment_blocks_routes(self, fake_api, fake_route):
        fake_api.side_effect = replies(alias_id="dpl_Older123")
        result, message = gate.verify_once(SHA, START, "test")
        self.assertIsNone(result)
        self.assertIn("alias", message)
        fake_route.assert_not_called()

    @patch.object(gate, "route_ok")
    @patch.object(gate, "api_json")
    def test_detail_sha_mismatch_blocks_alias_and_routes(self, fake_api, fake_route):
        fake_api.side_effect = replies(deployment_detail=detail(sha=OTHER))
        with self.assertRaisesRegex(gate.VerificationError, "mismatch"):
            gate.verify_once(SHA, START, "test")
        self.assertEqual(fake_api.call_count, 2)
        fake_route.assert_not_called()

    @patch.object(gate, "route_ok")
    @patch.object(gate, "api_json")
    def test_wrong_project_blocks_marker(self, fake_api, fake_route):
        fake_api.side_effect = replies(deployment_detail=detail(project={"id": "prj_OTHER"}))
        with self.assertRaisesRegex(gate.VerificationError, "mismatch"):
            gate.verify_once(SHA, START, "test")
        fake_route.assert_not_called()

    @patch.object(gate, "route_ok")
    @patch.object(gate, "api_json")
    def test_route_failure_never_passes(self, fake_api, fake_route):
        fake_api.side_effect = replies()
        fake_route.side_effect = gate.VerificationError("production route / returned HTTP 404")
        with self.assertRaisesRegex(gate.VerificationError, "HTTP 404"):
            gate.verify_once(SHA, START, "test")

    @patch.object(gate.time, "monotonic", side_effect=[0.0, 0.0])
    @patch.object(gate, "verify_once", return_value=(None, "still pending"))
    def test_timeout_fails_closed(self, _verify, _clock):
        with self.assertRaisesRegex(gate.VerificationError, "timed out"):
            gate.wait_for_verified(SHA, START, "not-logged", 0, 15)

    @patch.object(gate, "api_json")
    def test_wrong_api_list_shape_fails_closed(self, fake_api):
        fake_api.return_value = {"deployments": {"wrong": "shape"}}
        with self.assertRaisesRegex(gate.VerificationError, "invalid shape"):
            gate.verify_once(SHA, START, "test")


if __name__ == "__main__":
    unittest.main()
