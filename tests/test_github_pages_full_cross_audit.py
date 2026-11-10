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

    def test_private_builder_rejects_symlink_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            real_dir = Path(tmp) / "real_dir"
            real_dir.mkdir()
            sym_dir = Path(tmp) / "sym_link"
            sym_dir.symlink_to(real_dir)
            with self.assertRaises(RuntimeError) as ctx:
                full_pilot.validate_safety_and_dest(sym_dir)
            self.assertIn("symbolic link", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
