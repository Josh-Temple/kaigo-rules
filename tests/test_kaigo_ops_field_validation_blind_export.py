import unittest

from scripts.prepare_kaigo_ops_field_adjudication import (
    ADJUDICATION_HEADERS,
    RUN_HEADERS,
    build_blinded_rows,
)


class FieldValidationBlindExportTest(unittest.TestCase):
    def setUp(self):
        self.run_rows = [
            {
                "attempt_id": "P1-FV-01",
                "participant_id": "P1",
                "assignment_pattern": "P1",
                "question_id": "FV-01",
                "question_slug": "manager-concurrent-role",
                "condition": "A",
                "time_to_first_authoritative_source_sec": "120",
                "time_to_answer_submission_sec": "180",
                "answer_text": "回答",
                "source_url": "https://example.test/source",
                "source_locator": "第1条",
                "clicks": "3",
                "query_reformulations": "1",
                "confidence_1_5": "4",
                "observer_notes": "production_sha=" + "a" * 40,
            }
        ]
        self.template_rows = [
            {
                "attempt_id": "P1-FV-01",
                "question_id": "FV-01",
                "question_slug": "manager-concurrent-role",
                "answer_text": "",
                "source_url": "",
                "source_locator": "",
                "authoritative_source_reached": "",
                "answer_correct": "",
                "conditions_preserved": "",
                "source_correct": "",
                "human_correction_sec": "",
                "adjudicator_id": "",
                "adjudication_notes": "",
            }
        ]

    def test_builds_blinded_row_without_measurement_fields(self):
        rows = build_blinded_rows(
            RUN_HEADERS,
            self.run_rows,
            ADJUDICATION_HEADERS,
            self.template_rows,
        )
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(list(row.keys()), ADJUDICATION_HEADERS)
        self.assertEqual(row["answer_text"], "回答")
        self.assertEqual(row["source_url"], "https://example.test/source")
        self.assertEqual(row["source_locator"], "第1条")
        self.assertNotIn("condition", row)
        self.assertNotIn("time_to_first_authoritative_source_sec", row)
        self.assertNotIn("clicks", row)
        self.assertNotIn("confidence_1_5", row)
        self.assertEqual(row["answer_correct"], "")
        self.assertEqual(row["adjudicator_id"], "")

    def test_rejects_blank_answer(self):
        bad = [dict(self.run_rows[0])]
        bad[0]["answer_text"] = ""
        with self.assertRaises(ValueError):
            build_blinded_rows(
                RUN_HEADERS,
                bad,
                ADJUDICATION_HEADERS,
                self.template_rows,
            )

    def test_rejects_attempt_mismatch(self):
        bad = [dict(self.run_rows[0])]
        bad[0]["attempt_id"] = "P2-FV-01"
        with self.assertRaises(ValueError):
            build_blinded_rows(
                RUN_HEADERS,
                bad,
                ADJUDICATION_HEADERS,
                self.template_rows,
            )

    def test_rejects_question_slug_mismatch(self):
        bad = [dict(self.run_rows[0])]
        bad[0]["question_slug"] = "other"
        with self.assertRaises(ValueError):
            build_blinded_rows(
                RUN_HEADERS,
                bad,
                ADJUDICATION_HEADERS,
                self.template_rows,
            )

    def test_rejects_run_header_drift(self):
        bad_headers = list(RUN_HEADERS)
        bad_headers.append("condition_leak")
        with self.assertRaises(ValueError):
            build_blinded_rows(
                bad_headers,
                self.run_rows,
                ADJUDICATION_HEADERS,
                self.template_rows,
            )


if __name__ == "__main__":
    unittest.main()
