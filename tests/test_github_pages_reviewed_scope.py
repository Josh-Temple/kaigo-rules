"""Synthetic, no-Action fail-closed test for the isolated reviewed-scope builder."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("reviewed", ROOT / "scripts/build_github_pages_reviewed_scope.py")
reviewed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reviewed)


class ReviewedScopeTest(unittest.TestCase):
    def fixture(self):
        legal_row = {"id": "notice:第九十三条", "document_id": "doc-1", "label": "第93条", "title": "人員基準",
                     "text": "公開確認した法令本文", "url": "https://www.mhlw.go.jp/doc.pdf", "state": "REVIEWED_CURRENT",
                     "service_ids": ["dayservice"], "period_start": "2026-04", "period_end": "2026-05"}
        qa_row = {"id": "qa.reviewed", "question": "公開確認した質問", "answer": "公開確認した回答", "issued_source": "問1",
                  "service_code": "16", "review_state": "REVIEWED_CURRENT", "period_start": "2026-06", "period_end": "2026-12"}
        unapproved = {**legal_row, "id": "not-allowed", "text": "PRIVATE_UNAPPROVED_RECORD"}
        legal = {"documents": [{"id": "doc-1", "title": "国の法令"}], "records": [legal_row, unapproved]}
        qa = [qa_row, {**qa_row, "id": "qa.not-allowed", "answer": "PRIVATE_UNAPPROVED_QA"}]
        meta = {"source_workbook": "https://www.mhlw.go.jp/qa.xlsx", "review_status": "REVIEWED_SCOPE_ONLY"}
        common = {"state": reviewed.APPROVED, "publish_approved": True, "approved_by": "independent-reviewer",
                  "approved_at": "2026-11-04", "approval_reference": "review-record-1234", "evidence_reference": "original-doc-page-6"}
        legal_approval = {**common, "kind": "legal", "id": legal_row["id"], "document_id": "doc-1",
                          "service_ids": ["dayservice"], "source_url": legal_row["url"],
                          "row_sha256": reviewed.digest(legal_row), "period_start": "2026-04", "period_end": "2026-05"}
        qa_approval = {**common, "kind": "qa", "id": qa_row["id"], "service_code": "16",
                       "source_url": meta["source_workbook"], "row_sha256": reviewed.digest(qa_row),
                       "period_start": "2026-06", "period_end": "2026-12"}
        return {"schema": reviewed.SCHEMA, "purpose": "PRIVATE_ACCEPTANCE_ONLY",
                "approvals": [legal_approval, qa_approval]}, legal, qa, meta

    def generate(self, root, values):
        paths = []
        for name, data in zip(("manifest", "legal", "qa", "meta"), values):
            path = root / (name + ".json")
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            paths.append(path)
        return reviewed.build(*paths, root / "reviewed-output")

    def test_exact_allowed_only_in_html_json_and_gzip(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            report = self.generate(root, self.fixture())
            self.assertEqual((report["legal"], report["qa"], report["html"]), (1, 1, 4))
            self.assertFalse(report["deploy_approved"])
            output = root / "reviewed-output"
            import gzip
            self.assertEqual(gzip.decompress((output / "search/rows.json.gz").read_bytes()),
                             (output / "search/rows.json").read_bytes())
            rows = json.loads((output / "search/rows.json").read_text())["rows"]
            self.assertEqual({r["id"] for r in rows}, {"notice:第九十三条", "qa.reviewed"})
            self.assertEqual({r["href"].split('/')[0] for r in rows}, {".."})
            body = "\n".join(p.read_text() for p in output.rglob("*") if p.is_file() and p.suffix != ".gz")
            self.assertNotIn("PRIVATE_UNAPPROVED", body)
            self.assertNotIn("kaigo-rules.vercel.app", body)
            self.assertIn("noindex", body)
            self.assertIn(reviewed.WARNING, body)
            self.assertIn("popstate", body)
            self.assertEqual(len(list(output.rglob("*.html"))), 4)

    def test_rejects_empty_unknown_pending_duplicate_bad_evidence_and_period(self):
        cases = (
            (lambda a, l, q, m: a.update(approvals=[]), "Empty approval"),
            (lambda a, l, q, m: a["approvals"][0].update(publish_approved=False), "unreviewed"),
            (lambda a, l, q, m: a["approvals"][0].update(state="CANDIDATE_SOURCE_MATCH"), "unreviewed"),
            (lambda a, l, q, m: a["approvals"][0].update(period_end="2026-06"), "period mismatch"),
            (lambda a, l, q, m: a["approvals"][0].update(row_sha256="0" * 64), "changed source"),
            (lambda a, l, q, m: a["approvals"].append(copy.deepcopy(a["approvals"][0])), "duplicate approval"),
            (lambda a, l, q, m: a["approvals"][1].update(source_url="https://example.com/qa.xlsx"), "official source"),
            (lambda a, l, q, m: m.update(review_status="INGESTED_UNREVIEWED"), "unreviewed"),
            (lambda a, l, q, m: l["records"][0].update(state="PENDING"), "changed source"),
            (lambda a, l, q, m: a["approvals"][0].update(approval_reference=""), "approval evidence"),
            (lambda a, l, q, m: a["approvals"][1].update(service_code="17"), "service"),
        )
        for mutate, pattern in cases:
            with self.subTest(pattern=pattern), tempfile.TemporaryDirectory() as td:
                values = self.fixture()
                mutate(*values)
                with self.assertRaisesRegex(RuntimeError, pattern):
                    self.generate(Path(td), values)
                self.assertFalse((Path(td) / "reviewed-output").exists())

    def test_refuses_overwriting_an_existing_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.generate(root, self.fixture())
            with self.assertRaisesRegex(RuntimeError, "new, non-symlink"):
                self.generate(root, self.fixture())


if __name__ == "__main__":
    unittest.main()
