import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_full_private_pilot as pilot
import run_fault_injection_tests as faults


class PrivatePilotIntegrityRegressionTest(unittest.TestCase):
    @patch.dict(os.environ, {"CI": "false", "GITHUB_ACTIONS": "false"})
    def test_malformed_json_removes_staging_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_repo = root / "repo"
            (fake_repo / "data").mkdir(parents=True)
            (fake_repo / "data/handbook.generated.json").write_text("{broken", encoding="utf-8")
            (fake_repo / "data/legal-browser.generated.json").write_text("{}", encoding="utf-8")
            with patch.object(pilot, "ROOT", fake_repo), patch.object(pilot, "resolve_node_binary", return_value="node"):
                with self.assertRaises(json.JSONDecodeError):
                    pilot.build_full_pilot(root / "output")
            self.assertFalse((root / "output").exists())
            self.assertEqual(list(root.glob("kaigo_pilot_stage_*")), [])

    def test_fault_scenarios_do_not_pass_for_unrelated_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(faults, "WS_TMP", Path(tmp)), patch.object(
                faults.pilot, "build_full_pilot", side_effect=RuntimeError("unrelated early failure")
            ):
                rows = faults.test_d02_failure_scenarios(Path(tmp))
            self.assertEqual(len(rows), 14)
            self.assertFalse(any(row["passed"] for row in rows))

    def test_unparseable_node_version_is_rejected(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is unavailable")
        with patch("build_full_private_pilot.subprocess.run") as process:
            process.return_value.stdout = "not a version\n"
            with self.assertRaisesRegex(RuntimeError, "Cannot determine Node.js version"):
                pilot.resolve_node_binary(node)

    @patch.dict(os.environ, {"CI": "false", "GITHUB_ACTIONS": "false"})
    def test_audit_csv_cannot_be_inside_the_output_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "output"
            output.mkdir()
            with self.assertRaisesRegex(RuntimeError, "cannot be inside"):
                pilot.build_full_pilot(output, output / "audit.csv")

    def test_manifest_requires_trusted_digest_to_detect_manifest_rewrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            page = output / "index.html"
            page.write_text("original", encoding="utf-8")
            manifest = {"status": "COMPLETE", "files": {"index.html": {
                "size": page.stat().st_size, "sha256": hashlib.sha256(page.read_bytes()).hexdigest()
            }}}
            manifest_path = output / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            trusted_hash = pilot.compute_file_sha256(manifest_path)
            result = pilot.verify_manifest(output, expected_manifest_sha256=trusted_hash, require_source_binding=False)
            self.assertTrue(result["manifest_digest_matched"])
            page.write_text("changed", encoding="utf-8")
            manifest["files"]["index.html"] = {"size": page.stat().st_size, "sha256": hashlib.sha256(page.read_bytes()).hexdigest()}
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "independently supplied digest"):
                pilot.verify_manifest(output, expected_manifest_sha256=trusted_hash, require_source_binding=False)

    def test_verify_only_requires_a_separately_recorded_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, str(ROOT / "scripts/build_full_private_pilot.py"), tmp, "--verify-only"], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--expected-manifest-sha256", result.stderr)

    def test_manifest_rejects_input_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_repo = Path(tmp) / "repo"
            (fake_repo / "data").mkdir(parents=True)
            (fake_repo / "scripts").mkdir()
            names = ("build_full_private_pilot.py", "build_github_pages_legislation_pilot.py",
                     "localize_github_pages_links_pilot.py", "build_github_pages_handbook_pilot.py")
            for name in names:
                (fake_repo / "scripts" / name).write_text(name, encoding="utf-8")
            for name in ("handbook.generated.json", "legal-browser.generated.json"):
                (fake_repo / "data" / name).write_text(name, encoding="utf-8")
            output = Path(tmp) / "output"
            output.mkdir()
            page = output / "index.html"
            page.write_text("ok", encoding="utf-8")
            manifest = {
                "status": "COMPLETE", "git_commit": "commit", "git_tree": "tree",
                "master_data_hashes": {name: pilot.compute_file_sha256(fake_repo / "data" / name)
                                       for name in ("handbook.generated.json", "legal-browser.generated.json")},
                "builder_hashes": {name: pilot.compute_file_sha256(fake_repo / "scripts" / name) for name in names},
                "total_files": 1, "total_bytes": 2,
                "files": {"index.html": {"size": 2, "sha256": pilot.compute_file_sha256(page)}},
            }
            (output / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with patch.object(pilot, "ROOT", fake_repo), patch.object(pilot, "get_git_info", return_value=("commit", "tree")):
                self.assertTrue(pilot.verify_manifest(output)["source_binding_checked"])
                (fake_repo / "data/legal-browser.generated.json").write_text("changed", encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError, "master_data_hashes mismatch"):
                    pilot.verify_manifest(output)
                (fake_repo / "data/legal-browser.generated.json").write_text("legal-browser.generated.json", encoding="utf-8")
                manifest["master_data_hashes"]["legal-browser.generated.json"] = "0" * 64
                (output / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError, "master_data_hashes mismatch"):
                    pilot.verify_manifest(output)

    def test_manifest_rejects_path_outside_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "output"
            output.mkdir()
            outside = root / "outside.html"
            outside.write_text("outside", encoding="utf-8")
            manifest = {"status": "COMPLETE", "files": {"../outside.html": {
                "size": outside.stat().st_size, "sha256": pilot.compute_file_sha256(outside)
            }}}
            (output / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "Unsafe path"):
                pilot.verify_manifest(output, require_source_binding=False)


if __name__ == "__main__":
    unittest.main()
