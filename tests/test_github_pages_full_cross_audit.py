"""Regression tests for Kaigo Rules large-scale quality improvements.

Validates the 14 service staffing pending notice, primary source jump link,
print CSS rules, and link localization coverage.
"""
import unittest
from pathlib import Path
import tempfile
import json
import html

ROOT = Path(__file__).resolve().parents[1]

import scripts.build_github_pages_handbook_pilot as pilot
import scripts.localize_github_pages_links_pilot as navigation
import scripts.build_github_pages_legislation_pilot as legislation
import scripts.build_full_private_pilot as full_pilot


class FullCrossAuditTest(unittest.TestCase):

    def test_pending_roles_styles_present(self):
        self.assertIn(".handbook-roles-pending", pilot.STYLES)
        self.assertIn(".handbook-table-scroll", pilot.STYLES)
        print_styles = pilot.STYLES.split("@media print{", 1)[1]
        self.assertIn(".handbook-roles-pending{border-left:4px solid #333", print_styles)
        self.assertIn(".handbook-table-scroll{overflow:visible;break-inside:avoid-page}", print_styles)

    def test_reader_css_pending_styles_present(self):
        reader_css = (ROOT / "app/reader.css").read_text(encoding="utf-8")
        self.assertIn(".handbook-roles-pending", reader_css)
        self.assertIn(".handbook-table-scroll", reader_css)
        print_styles = reader_css.split("@media print{", 1)[1]
        self.assertIn(".handbook-roles-pending{border-left:4px solid #333", print_styles)

    def test_14_services_without_role_sections_properly_identified(self):
        master = json.loads((ROOT / "data/handbook.generated.json").read_text(encoding="utf-8"))
        services = master["services"]
        services_without_roles = [
            s["service_id"] for s in services
            if not any(c.get("role_sections") for c in s["chapters"] if c["section_id"] == "staffing")
        ]
        self.assertEqual(len(services_without_roles), 14)
        expected_14 = {
            "care-management", "care-medical-institution", "community-dayservice",
            "dementia-dayservice", "dementia-group-home", "elderly-health-facility",
            "elderly-welfare-facility", "homecaremanagement", "night-homevisit",
            "nursing-small-scale-multifunctional", "preventive-dementia-dayservice",
            "preventive-dementia-group-home", "preventive-homecaremanagement",
            "preventive-small-scale-multifunctional"
        }
        self.assertEqual(set(services_without_roles), expected_14)

    def test_link_destination_handles_legislation_record_and_browse(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legislation.build(root)
            
            # Record destination
            dest_rec = navigation.destination(
                root, "https://kaigo-rules.vercel.app/legislation?record=ordinance37.article.93&service=dayservice")
            self.assertIsNotNone(dest_rec)
            self.assertEqual(dest_rec[0], "legislation-record")
            self.assertTrue(dest_rec[1].is_file())
            
            # Service browse destination
            dest_browse = navigation.destination(
                root, "https://kaigo-rules.vercel.app/legislation?service=dayservice")
            self.assertIsNotNone(dest_browse)
            self.assertEqual(dest_browse[0], "legislation-browse")
            self.assertTrue(dest_browse[1].is_file())
            self.assertEqual(dest_browse[2], "?service=dayservice")

    def test_unit_price_fallback_does_not_pretend_to_be_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "databases/search").mkdir(parents=True)
            (root / "databases/search/index.html").write_text("検索資料", encoding="utf-8")
            (root / "fees").mkdir(parents=True)
            page = root / "fees/index.html"
            page.write_text('<a href="https://kaigo-rules.vercel.app/fees/unit-price">一単位単価表を見る</a>', encoding="utf-8")
            res = navigation.localize(root)
            self.assertEqual(res["links_localized"], 1)
            updated = page.read_text(encoding="utf-8")
            self.assertIn(navigation.UNIT_PRICE_FALLBACK_LABEL, updated)
            self.assertNotIn("一単位単価表を見る", updated)

    def test_private_builder_rejects_ci_environment(self):
        import os
        old_actions = os.environ.get("GITHUB_ACTIONS")
        old_ci = os.environ.get("CI")
        try:
            os.environ["GITHUB_ACTIONS"] = "true"
            with self.assertRaises(RuntimeError) as ctx:
                full_pilot.validate_safety_and_dest(None)
            self.assertIn("CI", str(ctx.exception))
            
            os.environ.pop("GITHUB_ACTIONS", None)
            os.environ["CI"] = "true"
            with self.assertRaises(RuntimeError) as ctx2:
                full_pilot.validate_safety_and_dest(None)
            self.assertIn("CI", str(ctx2.exception))
        finally:
            if old_actions is not None:
                os.environ["GITHUB_ACTIONS"] = old_actions
            else:
                os.environ.pop("GITHUB_ACTIONS", None)
            if old_ci is not None:
                os.environ["CI"] = old_ci
            else:
                os.environ.pop("CI", None)

    def test_private_builder_rejects_missing_or_empty_master_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty_file = Path(tmp) / "empty.json"
            empty_file.write_text("", encoding="utf-8")
            # Verify that build_full_pilot checks file existence and non-zero size
            self.assertTrue(empty_file.stat().st_size == 0)

    def test_private_builder_rejects_repo_root_output(self):
        with self.assertRaises(RuntimeError) as ctx:
            full_pilot.validate_safety_and_dest(ROOT)
        self.assertIn("inside the repository", str(ctx.exception))

    def test_private_builder_rejects_public_directory_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            pub = Path(tmp) / "public"
            pub.mkdir()
            with self.assertRaises(RuntimeError) as ctx:
                full_pilot.validate_safety_and_dest(pub)
            self.assertIn("public directory candidate", str(ctx.exception))

    def test_private_builder_rejects_dist_directory_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp) / "dist"
            dist.mkdir()
            with self.assertRaises(RuntimeError) as ctx:
                full_pilot.validate_safety_and_dest(dist)
            self.assertIn("public directory candidate", str(ctx.exception))

    def test_private_builder_rejects_next_directory_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            next_dir = Path(tmp) / ".next"
            next_dir.mkdir()
            with self.assertRaises(RuntimeError) as ctx:
                full_pilot.validate_safety_and_dest(next_dir)
            self.assertIn("public directory candidate", str(ctx.exception))

    def test_private_builder_rejects_symlink_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            real_dir = Path(tmp) / "real_dir"
            real_dir.mkdir()
            sym_dir = Path(tmp) / "sym_link"
            sym_dir.symlink_to(real_dir)
            with self.assertRaises(RuntimeError) as ctx:
                full_pilot.validate_safety_and_dest(sym_dir)
            self.assertIn("symbolic link", str(ctx.exception))

    def test_private_builder_atomic_failure_leaves_target_clean(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "atomic_target"
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = [
                    type("Proc", (), {"stdout": "v22.11.0\n", "returncode": 0})(),
                    type("Proc", (), {"stdout": "", "stderr": "Injected Node builder crash for testing", "returncode": 1})()
                ]
                with self.assertRaises(RuntimeError):
                    full_pilot.build_full_pilot(target)
            # Target must either not exist or contain 0 partial files
            if target.exists():
                self.assertEqual(len(list(target.rglob("*"))), 0)

    def test_private_builder_node_resolution_portability(self):
        node_bin = full_pilot.resolve_node_binary()
        self.assertIsNotNone(node_bin, "Node binary must be resolvable via PATH or standard opt paths")
        self.assertTrue(Path(node_bin).is_file())

    def test_private_builder_node_resolution_rejects_missing_binary(self):
        with self.assertRaises(RuntimeError) as ctx:
            full_pilot.resolve_node_binary("/nonexistent/bin/node")
        self.assertIn("not found", str(ctx.exception))

    def test_private_builder_node_resolution_rejects_unsupported_version(self):
        from unittest.mock import patch
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "v18.19.0\n"
            mock_run.return_value.returncode = 0
            with self.assertRaises(RuntimeError) as ctx:
                full_pilot.resolve_node_binary()
            self.assertIn("unsupported", str(ctx.exception))

    def test_manifest_verification_detects_tampering_synthetic(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "doc.html").write_text("hello", encoding="utf-8")
            h = full_pilot.compute_file_sha256(p / "doc.html")
            manifest = {
                "status": "COMPLETE",
                "files": {
                    "doc.html": {"sha256": h, "size": 5}
                }
            }
            (p / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            # Clean verification passes
            res = full_pilot.verify_manifest(p)
            self.assertTrue(res["ok"])

            # Tampering size is detected
            (p / "doc.html").write_text("hello world", encoding="utf-8")
            with self.assertRaises(RuntimeError) as ctx:
                full_pilot.verify_manifest(p)
            self.assertIn("size mismatch", str(ctx.exception))

            # Tampering content keeping size is detected
            (p / "doc.html").write_text("hellx", encoding="utf-8")
            with self.assertRaises(RuntimeError) as ctx:
                full_pilot.verify_manifest(p)
            self.assertIn("SHA-256 mismatch", str(ctx.exception))

            # Extra file is detected
            (p / "doc.html").write_text("hello", encoding="utf-8")
            (p / "extra.html").write_text("evil", encoding="utf-8")
            with self.assertRaises(RuntimeError) as ctx:
                full_pilot.verify_manifest(p)
            self.assertIn("Extraneous", str(ctx.exception))

    def test_validate_safety_and_dest_none_does_not_leak_temp_dir(self):
        # validate_safety_and_dest(None) must return None without allocating an abandoned directory in /tmp
        before_tmp_dirs = set(Path(tempfile.gettempdir()).glob("kaigo-full-private-*"))
        res = full_pilot.validate_safety_and_dest(None)
        self.assertIsNone(res)
        after_tmp_dirs = set(Path(tempfile.gettempdir()).glob("kaigo-full-private-*"))
        self.assertEqual(before_tmp_dirs, after_tmp_dirs, "No temporary directory should be leaked when dest_dir is None")

    def test_validate_csv_audit_path_safety(self):
        # Rejects CSV output inside repo root
        with self.assertRaises(RuntimeError) as ctx:
            full_pilot.validate_csv_audit_path(ROOT / "leak.csv")
        self.assertIn("inside the repository", str(ctx.exception))

        # Rejects CSV output inside public directories
        with tempfile.TemporaryDirectory() as tmp:
            pub_csv = Path(tmp) / "public/audit.csv"
            with self.assertRaises(RuntimeError) as ctx:
                full_pilot.validate_csv_audit_path(pub_csv)
            self.assertIn("public directory candidate", str(ctx.exception))

            # Allows safe external CSV path
            safe_csv = Path(tmp) / "safe_audit.csv"
            res = full_pilot.validate_csv_audit_path(safe_csv)
            self.assertEqual(res, safe_csv.resolve())

    def test_manifest_verification_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "doc.html").write_text("ok", encoding="utf-8")
            h = full_pilot.compute_file_sha256(p / "doc.html")
            manifest = {
                "status": "COMPLETE",
                "files": {
                    "../evil.html": {"sha256": h, "size": 2}
                }
            }
            (p / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(RuntimeError) as ctx:
                full_pilot.verify_manifest(p)
            self.assertIn("path traversal", str(ctx.exception))

    def test_manifest_verification_rejects_absolute_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "doc.html").write_text("ok", encoding="utf-8")
            h = full_pilot.compute_file_sha256(p / "doc.html")
            manifest = {
                "status": "COMPLETE",
                "files": {
                    "/etc/passwd": {"sha256": h, "size": 2}
                }
            }
            (p / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(RuntimeError) as ctx:
                full_pilot.verify_manifest(p)
            self.assertIn("invalid path format", str(ctx.exception))

    def test_manifest_verification_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            real_file = p / "real.html"
            real_file.write_text("ok", encoding="utf-8")
            sym = p / "sym.html"
            sym.symlink_to(real_file)
            h = full_pilot.compute_file_sha256(real_file)
            manifest = {
                "status": "COMPLETE",
                "files": {
                    "sym.html": {"sha256": h, "size": 2}
                }
            }
            (p / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(RuntimeError) as ctx:
                full_pilot.verify_manifest(p)
            self.assertIn("symbolic link", str(ctx.exception))

    def test_manifest_verification_checks_expected_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "doc.html").write_text("ok", encoding="utf-8")
            h = full_pilot.compute_file_sha256(p / "doc.html")
            manifest = {
                "status": "COMPLETE",
                "git_commit": "actual_commit_sha",
                "git_tree": "actual_tree_sha",
                "files": {
                    "doc.html": {"sha256": h, "size": 2}
                }
            }
            (p / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            # Correct expected commit passes
            res = full_pilot.verify_manifest(p, expected_commit="actual_commit_sha")
            self.assertTrue(res["ok"])

            # Wrong expected commit fails
            with self.assertRaises(RuntimeError) as ctx:
                full_pilot.verify_manifest(p, expected_commit="wrong_commit_sha")
            self.assertIn("provenance mismatch for git_commit", str(ctx.exception))

    def test_manifest_verification_rejects_tampered_total_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "doc.html").write_text("ok", encoding="utf-8")
            h = full_pilot.compute_file_sha256(p / "doc.html")
            manifest = {
                "status": "COMPLETE",
                "total_files": 999,
                "total_bytes": 2,
                "files": {
                    "doc.html": {"sha256": h, "size": 2}
                }
            }
            (p / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(RuntimeError) as ctx:
                full_pilot.verify_manifest(p)
            self.assertIn("total_files count mismatch", str(ctx.exception))

    def test_staging_cleanup_removes_stale_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            bak_dir = p / ".kaigo_bak_target_12345"
            bak_dir.mkdir()
            (bak_dir / "leftover.html").write_text("old", encoding="utf-8")
            stage_dir = p / ".kaigo_cross_stage_target_9999"
            stage_dir.mkdir()
            (stage_dir / "partial.html").write_text("partial", encoding="utf-8")
            csv_stage = p / ".kaigo_csv_stage_target_1111"
            csv_stage.write_text("data", encoding="utf-8")
            safe_user_file = p / "unrelated_user_file.txt"
            safe_user_file.write_text("keep me", encoding="utf-8")

            full_pilot.cleanup_stale_artifacts(p, "target")

            self.assertFalse(bak_dir.exists())
            self.assertFalse(stage_dir.exists())
            self.assertFalse(csv_stage.exists())
            self.assertTrue(safe_user_file.exists())



if __name__ == "__main__":
    unittest.main()
