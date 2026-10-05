import copy
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


BATCHES = load_module(
    "relation_human_review_batches",
    SCRIPTS / "build_relation_human_review_batches.py",
)
DECISIONS = load_module(
    "relation_human_review_decisions",
    SCRIPTS / "validate_relation_human_review_decisions.py",
)
EFFECTS = load_module(
    "relation_human_review_decision_effects",
    SCRIPTS / "build_relation_human_review_decision_effects.py",
)


class HumanReviewExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = DECISIONS.load_json(DECISIONS.EVIDENCE_PATH)
        cls.registry = DECISIONS.load_json(DECISIONS.BATCH_REGISTRY_PATH)
        cls.ledger = DECISIONS.load_json(DECISIONS.DECISIONS_PATH)
        cls.active = DECISIONS.active_batch_items(cls.registry)
        cls.first_key = sorted(cls.active)[0]
        cls.first_item = cls.active[cls.first_key]
        cls.evidence_by_key = {
            row["relation_key"]: row for row in cls.evidence["items"]
        }

    def valid_decision(self, **overrides):
        evidence = self.evidence_by_key[self.first_key]
        row = {
            "decision_id": "DECISION-TEST-001",
            "batch_id": self.first_item["batch_id"],
            "review_id": self.first_item["review_id"],
            "relation_key": self.first_key,
            "reviewer_identity": "Human Reviewer",
            "reviewer_decision": "CONFIRM_RELATION",
            "reviewer_rationale": "Primary-source text and the asserted semantics were reviewed.",
            "reviewed_at": "2026-10-06T06:30:00+09:00",
            "evidence_fingerprint_sha256": evidence[
                "evidence_fingerprint_sha256"
            ],
            "reviewer_attestation": "HUMAN_REVIEW_COMPLETED",
            "decision_state": "CURRENT",
        }
        row.update(overrides)
        return row

    def ledger_with(self, *rows):
        ledger = copy.deepcopy(self.ledger)
        ledger["decisions"] = list(rows)
        return ledger

    def test_batch_2_is_bounded_reproducible_and_evidence_complete(self):
        registry, batch2 = BATCHES.build()
        self.assertEqual(batch2["summary"]["items_total"], 10)
        self.assertEqual(batch2["summary"]["ready_for_human_review"], 10)
        self.assertEqual(
            [row["review_id"] for row in batch2["items"]],
            [
                "REL-020",
                "REL-027",
                "REL-031",
                "REL-034",
                "REL-035",
                "REL-036",
                "REL-037",
                "REL-038",
                "REL-042",
                "REL-043",
            ],
        )
        self.assertEqual(registry["summary"]["pilot_items"], 8)
        self.assertEqual(registry["summary"]["batch_2_items"], 10)
        self.assertEqual(registry["summary"]["active_review_items"], 18)
        self.assertEqual(registry["summary"]["stale_evidence_items"], 0)
        for row in batch2["items"]:
            self.assertNotEqual(
                row["source_pointer_status"], "PRIMARY_TEXT_POINTER_INCOMPLETE"
            )
            self.assertNotEqual(
                row["target_pointer_status"], "PRIMARY_TEXT_POINTER_INCOMPLETE"
            )

    def test_existing_pilot_immutable_reference_is_enforced(self):
        pilot = BATCHES.load(BATCHES.PILOT_PATH)
        BATCHES.validate_pilot_immutable(pilot)
        changed = copy.deepcopy(pilot)
        changed["items"][0]["evidence_fingerprint_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            BATCHES.validate_pilot_immutable(changed)

    def test_ai_only_decision_is_rejected(self):
        row = self.valid_decision(reviewer_identity="ChatGPT")
        with self.assertRaises(DECISIONS.ReviewContractError):
            DECISIONS.validate_decisions(
                ledger=self.ledger_with(row),
                evidence_pack=self.evidence,
                batch_registry=self.registry,
            )

    def test_missing_reviewer_identity_is_rejected(self):
        row = self.valid_decision()
        row.pop("reviewer_identity")
        with self.assertRaises(DECISIONS.ReviewContractError):
            DECISIONS.validate_decisions(
                ledger=self.ledger_with(row),
                evidence_pack=self.evidence,
                batch_registry=self.registry,
            )

    def test_missing_rationale_is_rejected(self):
        row = self.valid_decision(reviewer_rationale="")
        with self.assertRaises(DECISIONS.ReviewContractError):
            DECISIONS.validate_decisions(
                ledger=self.ledger_with(row),
                evidence_pack=self.evidence,
                batch_registry=self.registry,
            )

    def test_fingerprint_mismatch_cannot_be_current(self):
        row = self.valid_decision(evidence_fingerprint_sha256="0" * 64)
        with self.assertRaises(DECISIONS.ReviewContractError):
            DECISIONS.validate_decisions(
                ledger=self.ledger_with(row),
                evidence_pack=self.evidence,
                batch_registry=self.registry,
            )

        stale = self.valid_decision(
            evidence_fingerprint_sha256="0" * 64,
            decision_state="STALE_EVIDENCE",
        )
        result = DECISIONS.validate_decisions(
            ledger=self.ledger_with(stale),
            evidence_pack=self.evidence,
            batch_registry=self.registry,
        )
        self.assertEqual(result["current_human_decisions"], 0)
        self.assertEqual(result["stale_evidence_decisions"], 1)

    def test_needs_more_evidence_does_not_create_closure(self):
        row = self.valid_decision(reviewer_decision="NEEDS_MORE_EVIDENCE")
        report = EFFECTS.build(
            ledger=self.ledger_with(row),
            evidence_pack=self.evidence,
            batch_registry=self.registry,
        )
        self.assertEqual(report["summary"]["current_human_decisions"], 1)
        self.assertEqual(report["summary"]["current_needs_more_evidence"], 1)
        self.assertEqual(report["summary"]["closure_candidates"], 0)
        self.assertEqual(
            report["effects"][0]["decision_effect"],
            "KEEP_OPEN_NEEDS_MORE_EVIDENCE",
        )
        self.assertFalse(report["effects"][0]["closes_relation_review"])

    def test_out_of_batch_decision_injection_is_rejected(self):
        active_keys = set(self.active)
        outside = next(
            row
            for row in self.evidence["items"]
            if row["relation_key"] not in active_keys
        )
        row = self.valid_decision(
            batch_id="batch-2",
            review_id=outside["review_id"],
            relation_key=outside["relation_key"],
            evidence_fingerprint_sha256=outside[
                "evidence_fingerprint_sha256"
            ],
        )
        with self.assertRaises(DECISIONS.ReviewContractError):
            DECISIONS.validate_decisions(
                ledger=self.ledger_with(row),
                evidence_pack=self.evidence,
                batch_registry=self.registry,
            )

    def test_actual_ledger_contains_no_ai_or_human_decisions(self):
        result = DECISIONS.validate_decisions(
            ledger=self.ledger,
            evidence_pack=self.evidence,
            batch_registry=self.registry,
        )
        self.assertEqual(result["decision_records"], 0)
        self.assertEqual(result["current_human_decisions"], 0)
        self.assertEqual(result["stale_evidence_decisions"], 0)
        self.assertEqual(result["superseded_decisions"], 0)
        self.assertEqual(result["unreviewed_active_items"], 18)


if __name__ == "__main__":
    unittest.main()
