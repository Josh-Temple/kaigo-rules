"""Offline synthetic-only checks for the PUBLIC_SCOPE_HOLD production boundary.

No committed approval receipts, private signing keys or real content.
These synthetic fixtures NEVER authorize Kaigo Rules publication.
"""
from __future__ import annotations

import copy
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_github_pages_scoped_candidate as gate
import build_github_pages_reviewed_scope as scoped


class SignedScopeBoundary(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.inputs = {key: self.root / (key + ".json") for key in gate.INPUTS}
        self.receipt = self.root / "synthetic-receipt.json"
        self.signature = self.root / "synthetic-receipt.sig"
        self.key = self.root / "synthetic-public.pem"
        self.private_key = self.root / "synthetic-private.pem"
        self.output = self.root / "candidate"
        self.source_sha = "a" * 40
        self.month = "2026-11"
        self.legal_id = "dayservice"
        self.qa_code = "16"
        legal_row = {
            "id": "legal:test", "document_id": "doc-test", "title": "Synthetic law",
            "label": "Article 93", "text": "SYNTHETIC_ALLOWED_LEGAL_TEXT",
            "url": "https://www.mhlw.go.jp/synthetic.pdf", "state": "REVIEWED_CURRENT",
            "service_ids": [self.legal_id], "period_start": self.month,
            "period_end": self.month,
        }
        qa_row = {
            "id": "qa.synthetic", "question": "Synthetic question",
            "answer": "SYNTHETIC_ALLOWED_QA_TEXT", "issued_source": "synthetic source",
            "service_code": self.qa_code, "review_state": "REVIEWED_CURRENT",
            "period_start": self.month, "period_end": self.month,
        }
        base = {
            "state": scoped.APPROVED, "publish_approved": True,
            "approved_by": "synthetic-reviewer-only", "approved_at": "2026-11-05",
            "approval_reference": "SYNTHETIC-NOT-A-REAL-APPROVAL",
            "evidence_reference": "SYNTHETIC-EVIDENCE-ONLY",
            "period_start": self.month, "period_end": self.month,
        }
        self.manifest = {
            "schema": scoped.SCHEMA, "purpose": "PRIVATE_ACCEPTANCE_ONLY",
            "approvals": [
                {**base, "kind": "legal", "id": legal_row["id"],
                 "document_id": "doc-test", "service_ids": [self.legal_id],
                 "source_url": legal_row["url"], "row_sha256": scoped.digest(legal_row)},
                {**base, "kind": "qa", "id": qa_row["id"],
                 "service_code": self.qa_code,
                 "source_url": "https://www.mhlw.go.jp/synthetic.xlsx",
                 "row_sha256": scoped.digest(qa_row)},
            ],
        }
        self.legal = {"documents": [{"id": "doc-test", "title": "Synthetic document"}],
                      "records": [legal_row, {**legal_row, "id": "UNAPPROVED",
                                             "text": "PRIVATE_UNAPPROVED_LEGAL"}]}
        self.qa = [qa_row, {**qa_row, "id": "qa.unapproved", "answer": "PRIVATE_UNAPPROVED_QA"}]
        self.meta = {"source_workbook": "https://www.mhlw.go.jp/synthetic.xlsx",
                     "review_status": "REVIEWED_SCOPE_ONLY"}
        self.write_inputs()
        if shutil.which("openssl") is None:
            self.skipTest("OpenSSL not available: cryptographic path NOT_RUN")
        subprocess.run(["openssl", "genpkey", "-algorithm", "RSA",
                        "-pkeyopt", "rsa_keygen_bits:2048", "-out", str(self.private_key)],
                       capture_output=True, check=True, timeout=20)
        subprocess.run(["openssl", "pkey", "-in", str(self.private_key), "-pubout",
                        "-out", str(self.key)], capture_output=True, check=True, timeout=10)
        self.key_hash = gate.sha256(self.key.read_bytes())
        self.sign()

    def write_inputs(self):
        for key, obj in zip(gate.INPUTS, (self.manifest, self.legal, self.qa, self.meta)):
            self.inputs[key].write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")

    def sign(self):
        ids = sorted((a["kind"], a["id"]) for a in self.manifest["approvals"])
        today = date.today()
        payload = {
            "schema": gate.RECEIPT_SCHEMA, "decision": "APPROVED_FOR_DISTRIBUTION",
            "source_sha": self.source_sha, "target_month": self.month,
            "service_id": self.legal_id, "qa_service_code": self.qa_code,
            "source_sha256": {key: gate.sha256(path.read_bytes())
                              for key, path in self.inputs.items()},
            "approved_ids_sha256": gate.sha256(json.dumps(
                ids, ensure_ascii=False, separators=(",", ":")).encode("utf-8")),
            "reviewer_id": "synthetic-reviewer-only",
            "authority_reference": "SYNTHETIC-NOT-REAL-AUTHORITY",
            "independent_review": True,
            "valid_from": (today - timedelta(days=1)).isoformat(),
            "expires_on": (today + timedelta(days=1)).isoformat(),
        }
        self.receipt.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        subprocess.run(["openssl", "dgst", "-sha256", "-sign",
                        str(self.private_key), "-out", str(self.signature),
                        str(self.receipt)], capture_output=True, check=True, timeout=10)

    def preflight(self, **changes):
        options = dict(
            source_sha=self.source_sha, target_month=self.month,
            service_id=self.legal_id, qa_service_code=self.qa_code,
            inputs=self.inputs, receipt_file=self.receipt,
            signature_file=self.signature, trusted_key_file=self.key,
            trusted_key_sha256=self.key_hash)
        options.update(changes)
        return gate.approve_preflight(**options)

    def test_synthetic_signed_scope_can_generate_only_private_details(self):
        report = self.preflight()
        self.assertEqual(report["approved_ids"], 2)
        result = scoped.build(self.inputs["approvals"], self.inputs["legal"],
                              self.inputs["qa"], self.inputs["qa_meta"], self.output,
                              target_month=self.month, target_service=self.legal_id,
                              target_qa_service=self.qa_code)
        self.assertEqual((result["records"], result["html"]), (2, 4))
        self.assertFalse(result["deploy_approved"])
        self.assertEqual((self.output / "search/rows.json").read_bytes(),
                         gzip.decompress((self.output / "search/rows.json.gz").read_bytes()))
        combined = b"".join(p.read_bytes() for p in self.output.rglob("*") if p.is_file())
        self.assertNotIn(b"PRIVATE_UNAPPROVED", combined)
        self.assertEqual(len(list(self.output.rglob("*.html"))), 4)
        self.assertEqual(len(list(self.output.rglob("*.mjs"))), 1)
        self.assertEqual(len(list(self.output.rglob("*.gz"))), 1)

    def test_missing_signature_and_untrusted_key_fail_before_output(self):
        self.signature.unlink()
        with self.assertRaisesRegex(RuntimeError, "missing or linked"):
            self.preflight()
        self.assertFalse(self.output.exists())
        self.sign()
        with self.assertRaisesRegex(RuntimeError, "untrusted signer"):
            self.preflight(trusted_key_sha256="0" * 64)
        self.assertFalse(self.output.exists())

    def test_receipt_tamper_invalidates_signature(self):
        obj = json.loads(self.receipt.read_text())
        obj["authority_reference"] = "forged-independent-claim"
        self.receipt.write_text(json.dumps(obj), encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "signature"):
            self.preflight()
        self.assertFalse(self.output.exists())

    def test_empty_pending_unknown_duplicate_and_period_rejected(self):
        changes = (
            lambda: self.manifest.update(approvals=[]),
            lambda: self.manifest["approvals"][0].update(publish_approved=False),
            lambda: self.manifest["approvals"][0].update(state="UNKNOWN"),
            lambda: self.manifest["approvals"].append(copy.deepcopy(self.manifest["approvals"][0])),
            lambda: self.manifest["approvals"][0].update(period_end="2026-10"),
            lambda: self.manifest["approvals"][1].update(service_code="99"),
            lambda: self.manifest["approvals"][0].update(row_sha256="0" * 64),
        )
        for change in changes:
            with self.subTest(change=changes.index(change)):
                # Reset with the original good fixture between cases.
                orig = copy.deepcopy(self.manifest)
                change()
                self.write_inputs()
                self.sign()
                with self.assertRaises(RuntimeError):
                    self.preflight()
                self.assertFalse(self.output.exists())
                self.manifest = orig
                self.write_inputs()

    def test_changed_source_rejected_even_with_genuine_old_signature(self):
        self.legal["records"][0]["text"] = "TAMPERED_ROW"
        self.write_inputs()
        with self.assertRaisesRegex(RuntimeError, "exact source"):
            self.preflight()
        self.assertFalse(self.output.exists())

    def test_qa_meta_unreviewed_rejected_before_generation(self):
        self.meta["review_status"] = "INGESTED_UNREVIEWED"
        self.write_inputs()
        self.sign()
        with self.assertRaisesRegex(RuntimeError, "unreviewed Q&A"):
            self.preflight()
        self.assertFalse(self.output.exists())

    def test_invalid_json_denied(self):
        self.inputs["approvals"].write_text("{bad-json", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "invalid approval JSON"):
            self.preflight()
        self.assertFalse(self.output.exists())

    def test_historical_full_generator_refuses_public_actions(self):
        env = dict(os.environ, GITHUB_ACTIONS="true")
        run = subprocess.run([sys.executable,
                              str(ROOT / "scripts/build_github_pages_integrated_pilot.py"),
                              "--with-details"], cwd=ROOT, env=env, capture_output=True,
                             text=True, timeout=15)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("PRIVATE_FULL_BUILD_FORBIDDEN_IN_PUBLIC_ACTIONS", run.stderr)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
