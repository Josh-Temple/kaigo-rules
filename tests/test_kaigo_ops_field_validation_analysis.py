import unittest

from scripts.analyze_kaigo_ops_field_validation import build_report


class FieldValidationAnalysisTest(unittest.TestCase):
    def setUp(self):
        self.pilot = {
            "pilot_id": "test-pilot",
            "questions": [
                {"id": "FV-01", "slug": "q1", "complexity": "single-source"},
                {"id": "FV-02", "slug": "q2", "complexity": "multi-source"},
            ],
        }
        sha = "a" * 40
        self.run = [
            {
                "attempt_id": "P1-FV-01", "participant_id": "P1", "assignment_pattern": "P1",
                "question_id": "FV-01", "question_slug": "q1", "condition": "A",
                "time_to_first_authoritative_source_sec": "100", "time_to_answer_submission_sec": "150",
                "answer_text": "a1", "source_url": "https://example.test/1", "source_locator": "第1条",
                "clicks": "4", "query_reformulations": "1", "confidence_1_5": "4",
                "observer_notes": f"production_sha={sha}",
            },
            {
                "attempt_id": "P2-FV-01", "participant_id": "P2", "assignment_pattern": "P2",
                "question_id": "FV-01", "question_slug": "q1", "condition": "B",
                "time_to_first_authoritative_source_sec": "50", "time_to_answer_submission_sec": "90",
                "answer_text": "b1", "source_url": "https://example.test/1", "source_locator": "第1条",
                "clicks": "2", "query_reformulations": "0", "confidence_1_5": "5",
                "observer_notes": f"production_sha={sha}",
            },
            {
                "attempt_id": "P1-FV-02", "participant_id": "P1", "assignment_pattern": "P1",
                "question_id": "FV-02", "question_slug": "q2", "condition": "B",
                "time_to_first_authoritative_source_sec": "", "time_to_answer_submission_sec": "600",
                "answer_text": "b2", "source_url": "", "source_locator": "",
                "clicks": "8", "query_reformulations": "3", "confidence_1_5": "2",
                "observer_notes": f"production_sha={sha} TIMEOUT_NO_SOURCE",
            },
            {
                "attempt_id": "P2-FV-02", "participant_id": "P2", "assignment_pattern": "P2",
                "question_id": "FV-02", "question_slug": "q2", "condition": "A",
                "time_to_first_authoritative_source_sec": "200", "time_to_answer_submission_sec": "240",
                "answer_text": "a2", "source_url": "https://example.test/2", "source_locator": "p.2",
                "clicks": "6", "query_reformulations": "2", "confidence_1_5": "3",
                "observer_notes": f"production_sha={sha}",
            },
        ]

        judged = {
            "P1-FV-01": ("TRUE", "TRUE", "TRUE", "TRUE", "0"),
            "P2-FV-01": ("TRUE", "TRUE", "TRUE", "TRUE", "0"),
            "P1-FV-02": ("FALSE", "FALSE", "FALSE", "FALSE", "20"),
            "P2-FV-02": ("TRUE", "TRUE", "TRUE", "TRUE", "0"),
        }
        run_by_id = {row["attempt_id"]: row for row in self.run}
        self.adj = []
        for attempt_id, values in judged.items():
            run = run_by_id[attempt_id]
            self.adj.append(
                {
                    "attempt_id": attempt_id,
                    "question_id": run["question_id"],
                    "question_slug": run["question_slug"],
                    "answer_text": run["answer_text"],
                    "source_url": run["source_url"],
                    "source_locator": run["source_locator"],
                    "authoritative_source_reached": values[0],
                    "answer_correct": values[1],
                    "conditions_preserved": values[2],
                    "source_correct": values[3],
                    "human_correction_sec": values[4],
                    "adjudicator_id": "J1",
                    "adjudication_notes": "",
                }
            )

    def test_build_report_uses_reached_attempts_for_source_time(self):
        report = build_report(self.run, self.adj, self.pilot)
        self.assertEqual(report["attempt_count"], 4)
        self.assertEqual(report["production_sha"], "a" * 40)
        self.assertEqual(
            report["by_condition"]["A"]["median_first_source_sec_among_reached"],
            150.0,
        )
        self.assertEqual(
            report["by_condition"]["B"]["median_first_source_sec_among_reached"],
            50.0,
        )
        self.assertEqual(
            report["by_condition"]["B"]["authoritative_source_reach_rate"],
            0.5,
        )

    def test_rejects_source_correct_without_authoritative_source(self):
        bad = [dict(row) for row in self.adj]
        for row in bad:
            if row["attempt_id"] == "P1-FV-02":
                row["source_correct"] = "TRUE"
                break
        with self.assertRaises(ValueError):
            build_report(self.run, bad, self.pilot)

    def test_rejects_mixed_production_sha(self):
        bad_run = [dict(row) for row in self.run]
        bad_run[0]["observer_notes"] = "production_sha=" + "b" * 40
        with self.assertRaises(ValueError):
            build_report(bad_run, self.adj, self.pilot)


if __name__ == "__main__":
    unittest.main()
