"""Six-chapter staffing role contract: bounded regressions and hostile inputs.

Source truth is the authored handbook; these tests never attest legal accuracy.
"""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_handbook_site", ROOT / "scripts/build_handbook_site.py")
handbook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handbook)

SIX = {
    "homevisit", "small-scale-multifunctional", "dayservice",
    "dayrehab", "care-management", "dementia-group-home"
}
FOUR = {"dayservice", "dayrehab", "care-management", "dementia-group-home"}


def draft_requirement():
    return {
        "id": "placement", "title": "要件（未確認）", "aspect": "placement",
        "description": "配置数・資格・兼務の原典照合は未了です。",
        "applicability": "対象、指定権者と施行時点は未確認です。",
        "verification_state": "EVIDENCE_GAP", "evidence": [],
        "practical_checks": ["勤務形態一覧表と勤務実績を照合する。"]
    }


def draft_role():
    return [{"id": "manager", "title": "管理者",
             "requirements": [draft_requirement()]}]


def checked_qa():
    return {
        "kind": "national_qa", "title": "国Q&A（試験用）",
        "issuer": "厚生労働省", "locator": "問番号未特定",
        "version": "版未確認", "scope": "当該サービス",
        "checked_at_jst": "2026-10-22 17:00 JST",
        "verification_state": "PRIMARY_TEXT_CHECKED_SCOPED",
        "url": "https://www.mhlw.go.jp/content/example.pdf"
    }


class TestSixStaffingRoleSections(unittest.TestCase):
    def test_fixed_scope_and_data_projection(self):
        self.assertEqual(handbook.ROLE_TARGETS, SIX)
        authored = json.loads((ROOT / "data/handbook-content.json").read_text())
        self.assertEqual(authored["schema_version"], 1)
        for sid, obj in authored["services"].items():
            for section, entry in obj["chapters"].items():
                if "role_sections" in entry:
                    self.assertEqual(section, "staffing")
                    self.assertIn(sid, SIX)
                    handbook.validate_role_sections(sid, section, entry["role_sections"])
        # Preserve the two prior pilots, including the 3+5 roles and 10+16 requirements.
        for sid, expected_roles, expected_reqs in [
            ("homevisit", 3, 10), ("small-scale-multifunctional", 5, 16)
        ]:
            roles = authored["services"][sid]["chapters"]["staffing"]["role_sections"]
            self.assertEqual(len(roles), expected_roles, sid)
            self.assertEqual(sum(len(r["requirements"]) for r in roles), expected_reqs, sid)

    def test_generated_chapters_and_seo_contract(self):
        generated_path = ROOT / "data/handbook.generated.json"
        if generated_path.exists():
            generated = json.loads(generated_path.read_text())
            self.assertEqual(generated["schema_version"], 1)
            self.assertEqual(len(generated["services"]), 39)
            chapters = [c for s in generated["services"] for c in s["chapters"]]
            self.assertEqual(len(chapters), 585)
            for svc in generated["services"]:
                self.assertEqual(len(svc["chapters"]), 15, svc["service_id"])
                self.assertEqual([c["number"] for c in svc["chapters"]], list(range(1, 16)))
                for chapter in svc["chapters"]:
                    if chapter.get("role_sections"):
                        self.assertEqual(chapter["section_id"], "staffing")
                        self.assertIn(svc["service_id"], SIX)
                    self.assertEqual(chapter["editorial_state"], "作成中・未確認")
        route = (ROOT / "app/handbook/[serviceId]/[chapter]/page.tsx").read_text()
        self.assertIn("pageMetadata(", route)
        self.assertIn("false", route)
        self.assertIn("作成中・未確認の内容を含みます", route)

    def test_six_allowed_services_and_four_new_role_id_sets(self):
        for sid in SIX:
            handbook.validate_role_sections(sid, "staffing", draft_role())
        for sid in FOUR:
            self.assertIn("manager", handbook.NEW_ROLE_IDS[sid])

    def test_negative_inputs_are_rejected(self):
        # Every row is an executed negative case, not merely an example.
        cases = [
            ("wrong service", "preventive-dayrehab", "staffing", lambda roles: None),
            ("wrong chapter", "dayservice", "equipment", lambda roles: None),
            ("unknown role id", "dayservice", "staffing", lambda roles: roles[0].update(id="not-a-role")),
            ("malformed role id", "homevisit", "staffing", lambda roles: roles[0].update(id="Manager!")),
            ("duplicate role id", "dayservice", "staffing", lambda roles: roles.append(copy.deepcopy(roles[0]))),
            ("extra role key", "dayservice", "staffing", lambda roles: roles[0].update(unexpected="x")),
            ("extra requirement key", "dayservice", "staffing", lambda roles: roles[0]["requirements"][0].update(unexpected="x")),
            ("wrong aspect", "dayservice", "staffing", lambda roles: roles[0]["requirements"][0].update(aspect="salary")),
            ("unknown status", "dayservice", "staffing", lambda roles: roles[0]["requirements"][0].update(verification_state="VERIFIED")),
            ("script injection", "dayservice", "staffing", lambda roles: roles[0]["requirements"][0].update(description="<script>alert(1)</script>")),
            ("svg injection", "dayservice", "staffing", lambda roles: roles[0].update(title="<svg onload=alert(1)>")),
            ("proofless promotion", "dayservice", "staffing", lambda roles: roles[0]["requirements"][0].update(verification_state="PRIMARY_TEXT_CHECKED_SCOPED")),
            ("ambiguous checked national qa", "dayservice", "staffing", lambda roles: roles[0]["requirements"][0].update(evidence=[checked_qa()], verification_state="PRIMARY_TEXT_CHECKED_SCOPED")),
            ("candidate link", "dayservice", "staffing", lambda roles: roles[0]["requirements"][0].update(evidence=[{**checked_qa(), "verification_state": "SOURCE_CANDIDATE_UNVERIFIED", "checked_at_jst": ""}])),
            ("candidate checked timestamp", "dayservice", "staffing", lambda roles: roles[0]["requirements"][0].update(evidence=[{**checked_qa(), "verification_state": "SOURCE_CANDIDATE_UNVERIFIED", "url": "https://www.mhlw.go.jp/content/example.pdf"}])),
        ]
        for label, sid, section, mutate in cases:
            with self.subTest(label=label), self.assertRaises(ValueError):
                roles = draft_role()
                mutate(roles)
                handbook.validate_role_sections(sid, section, roles)

    def test_hostile_source_urls_are_rejected(self):
        examples = [
            ("javascript", "javascript:alert(1)"),
            ("data", "data:text/html,x"),
            ("plain http", "http://www.mhlw.go.jp/test"),
            ("userinfo", "https://user@www.mhlw.go.jp/test"),
            ("host spoof", "https://www.mhlw.go.jp.attacker.test/test"),
            ("lookalike", "https://www.mhlw.go.jp.evil.test/test"),
            ("nonstandard port", "https://www.mhlw.go.jp:8443/test"),
            ("malicious fragment", "https://www.mhlw.go.jp/test#javascript:alert(1)"),
            ("encoded slash", "https://www.mhlw.go.jp/%2F%2Fattacker"),
            ("encoded traversal", "https://www.mhlw.go.jp/%2e%2e/test"),
            ("encoded at sign", "https://www.mhlw.go.jp/%40evil"),
            ("query redirect", "https://www.mhlw.go.jp/test?redirect=https%3A%2F%2Fevil.test"),
            ("query next", "https://www.mhlw.go.jp/test?next=%2F%2Fevil.test"),
            ("newline", "https://www.mhlw.go.jp/test%0aHeader"),
            ("raw backslash", "https://www.mhlw.go.jp/\\evil.test"),
            ("external host", "https://example.com/test"),
        ]
        for label, url in examples:
            with self.subTest(label=label), self.assertRaises(ValueError):
                handbook.role_url(url)
        self.assertEqual(
            handbook.role_url("https://www.mhlw.go.jp/content/example.pdf#page=2"),
            "https://www.mhlw.go.jp/content/example.pdf#page=2")


if __name__ == "__main__":
    unittest.main()
