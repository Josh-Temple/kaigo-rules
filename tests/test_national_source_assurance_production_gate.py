from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

EXPECTED_SHA = "e3a6c3f038293d962562429e5056f3e36c603191"
BASE_URL = "https://kaigo-rules.vercel.app"


class NationalSourceAssuranceProductionGateTest(unittest.TestCase):
    def run_checked(self, *args: str) -> None:
        subprocess.run([sys.executable, *args], check=True)

    def test_exact_sha_production_and_release_regressions(self) -> None:
        self.run_checked(
            "scripts/verify_field_validation_production.py",
            "--base-url", BASE_URL,
            "--expected-sha", EXPECTED_SHA,
            "--wait-seconds", "120",
            "--interval-seconds", "10",
        )
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.run_checked(
                "scripts/run_machine_retrieval_benchmark.py",
                "--base-url", BASE_URL,
                "--expected-sha", EXPECTED_SHA,
                "--output", str(root / "machine-retrieval-v0.1.json"),
            )
            self.run_checked(
                "scripts/run_integration_sprint_release_regression.py",
                "--base-url", BASE_URL,
                "--expected-sha", EXPECTED_SHA,
                "--output", str(root / "integration-release-regression.json"),
            )


if __name__ == "__main__":
    unittest.main()
