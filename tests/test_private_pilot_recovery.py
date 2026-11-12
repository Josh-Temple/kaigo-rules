"""Failure and recovery tests for the private site and its audit CSV."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.build_full_private_pilot as pilot
from scripts.verify_link_localization_truth import equivalent_query


class PrivatePilotRecoveryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.stage = self.root / "stage"
        self.stage.mkdir()
        (self.stage / "index.html").write_text("new site", encoding="utf-8")
        self.staged_csv = self.root / "staged.csv"
        self.staged_csv.write_text("new audit", encoding="utf-8")
        manifest = {
            "status": "COMPLETE",
            "files": {"index.html": {"sha256": pilot.compute_file_sha256(self.stage / "index.html"), "size": 8}},
            "audit_csv": {"sha256": pilot.compute_file_sha256(self.staged_csv), "size": 9},
        }
        (self.stage / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        self.dest = self.root / "site"
        self.dest.mkdir()
        (self.dest / "original.txt").write_text("old site", encoding="utf-8")
        self.csv = self.root / "audit.csv"
        self.csv.write_text("old audit", encoding="utf-8")

    def assert_original_outputs(self):
        self.assertEqual((self.dest / "original.txt").read_text(), "old site")
        self.assertEqual(self.csv.read_text(), "old audit")

    def test_success_binds_csv_to_site_and_detects_a_different_csv(self):
        result, warnings = pilot.promote_outputs(self.stage, self.dest, self.staged_csv, self.csv)
        self.assertEqual(result, self.dest)
        self.assertEqual(warnings, [])
        self.assertTrue(pilot.verify_manifest(self.dest, audit_csv_path=self.csv)["ok"])
        self.csv.write_text("different", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "does not match"):
            pilot.verify_manifest(self.dest, audit_csv_path=self.csv)

    def test_cross_filesystem_copy_is_verified_before_replacing_old_output(self):
        with patch.object(pilot, "is_same_filesystem", return_value=False):
            with patch.object(pilot.shutil, "copytree", side_effect=OSError("disk full")):
                with self.assertRaisesRegex(RuntimeError, "rolled back"):
                    pilot.promote_outputs(self.stage, self.dest, self.staged_csv, self.csv)
        self.assert_original_outputs()

    def test_csv_copy_failure_rolls_back_site_and_csv(self):
        with patch.object(pilot.shutil, "copy2", side_effect=OSError("disk full")):
            with self.assertRaisesRegex(RuntimeError, "rolled back"):
                pilot.promote_outputs(self.stage, self.dest, self.staged_csv, self.csv)
        self.assert_original_outputs()
        self.assertFalse(list(self.root.glob(".kaigo_bak_site_*")))
        self.assertFalse(list(self.root.glob(".kaigo_csv_bak_audit.csv_*")))

    def test_csv_replace_failure_restores_both_originals(self):
        with patch.object(pilot.os, "replace", side_effect=OSError("CSV replace failed")):
            with self.assertRaisesRegex(RuntimeError, "rolled back"):
                pilot.promote_outputs(self.stage, self.dest, self.staged_csv, self.csv)
        self.assert_original_outputs()

    def test_site_created_by_failed_run_is_removed(self):
        (self.dest / "original.txt").unlink()
        self.dest.rmdir()
        with patch.object(pilot.os, "replace", side_effect=OSError("CSV replace failed")):
            with self.assertRaisesRegex(RuntimeError, "rolled back"):
                pilot.promote_outputs(self.stage, self.dest, self.staged_csv, self.csv)
        self.assertFalse(self.dest.exists())
        self.assertEqual(self.csv.read_text(), "old audit")

    def test_failed_rollback_preserves_only_backup_and_blocks_next_run(self):
        real_rename = os.rename

        def fail_restore(src, dst):
            if Path(src).name.startswith(".kaigo_bak_site_"):
                raise OSError("restore failed")
            return real_rename(src, dst)

        with patch.object(pilot.os, "rename", side_effect=fail_restore):
            with patch.object(pilot.os, "replace", side_effect=OSError("CSV failed")):
                with self.assertRaisesRegex(RuntimeError, "rollback failed"):
                    pilot.promote_outputs(self.stage, self.dest, self.staged_csv, self.csv)
        backups = list(self.root.glob(".kaigo_bak_site_*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "original.txt").read_text(), "old site")
        with self.assertRaisesRegex(RuntimeError, "Unresolved backup"):
            pilot.cleanup_stale_artifacts(self.root, "site")
        self.assertTrue((backups[0] / "original.txt").exists())

    def test_unresolved_csv_backup_is_not_deleted(self):
        backup = self.root / ".kaigo_csv_bak_audit.csv_interrupted"
        backup.write_text("only copy", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "Unresolved backup"):
            pilot.promote_outputs(self.stage, self.dest, self.staged_csv, self.csv)
        self.assertEqual(backup.read_text(), "only copy")
        self.assert_original_outputs()

    def test_interrupted_first_publication_pair_is_detected_on_retry(self):
        # Simulates a process kill after the new site is renamed but before
        # its CSV is replaced, with no old site available to back up.
        (self.dest / "original.txt").unlink()
        self.dest.rmdir()
        os.rename(self.stage, self.dest)
        with self.assertRaisesRegex(RuntimeError, "do not match"):
            pilot.check_existing_csv_pair(self.dest, self.csv)
        with self.assertRaisesRegex(RuntimeError, "must be supplied"):
            pilot.check_existing_csv_pair(self.dest, None)
        self.assertTrue((self.dest / "index.html").is_file())
        self.assertEqual(self.csv.read_text(), "old audit")

    def test_locks_exclude_a_second_writer(self):
        with pilot.output_locks([self.dest]):
            with self.assertRaisesRegex(RuntimeError, "Another builder"):
                with pilot.output_locks([self.dest]):
                    pass

    def test_overlapping_outputs_and_repository_ancestor_are_rejected(self):
        for csv_path in (self.dest, self.dest / "audit.csv", self.root):
            with self.subTest(csv_path=csv_path):
                with self.assertRaisesRegex(RuntimeError, "must not contain"):
                    pilot.validate_output_relationship(self.dest, csv_path)
        with self.assertRaisesRegex(RuntimeError, "ancestor"):
            pilot.validate_safety_and_dest(pilot.ROOT.parent)

    def test_implicit_destination_is_removed_on_generation_failure(self):
        new_stage = self.root / "generated"
        new_stage.mkdir()
        with patch.object(pilot, "get_safe_staging_dir", return_value=new_stage):
            with patch.object(pilot.legislation, "build", side_effect=RuntimeError("injected")):
                with self.assertRaisesRegex(RuntimeError, "injected"):
                    pilot.build_full_pilot(None)
        self.assertFalse(new_stage.exists())


class LinkQueryAuditTest(unittest.TestCase):
    def test_only_documented_scoped_migrations_are_accepted(self):
        cases = [
            ("/rules?service=dayrehab", "index.html?service=dayrehab&category=standards", True),
            ("/notices?service=dayrehab", "index.html?category=notices&service=dayrehab", True),
            ("/services/dayrehab/remuneration/guidance", "index.html?service=dayrehab&category=guidance", True),
            ("/rules?service=dayrehab", "index.html?service=homevisit&category=standards", False),
            ("/rules?service=dayrehab", "index.html?service=dayrehab&category=notices", False),
            ("/legislation?category=standards", "index.html?category=notices", False),
            ("/services/dayservice/remuneration/guidance", "index.html?service=dayservice&category=guidance", False),
        ]
        for original, localized, expected in cases:
            with self.subTest(original=original, localized=localized):
                self.assertEqual(equivalent_query(original, localized), expected)


if __name__ == "__main__":
    unittest.main()
