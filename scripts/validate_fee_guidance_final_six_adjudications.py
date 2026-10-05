#!/usr/bin/env python3
"""Validate Worker A final-six Fee Guidance scope adjudications."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADJUDICATIONS = ROOT / "data/shared/fee-guidance/final-six-scope-adjudications.json"
CORPUS = ROOT / "data/shared/fee-guidance/national-corpus.json"
RELATIONS = ROOT / "data/shared/fee-guidance/service-relations.json"

EXPECTED = {
    "preventive-dementia-dayservice": ("SCOPE_DEFINED", "MAPPED"),
    "preventive-small-scale-multifunctional": ("SCOPE_DEFINED", "MAPPED"),
    "preventive-dementia-group-home": ("SCOPE_DEFINED", "MAPPED"),
    "specific-welfare-equipment-sale": ("SCOPE_DEFINED", "NOT_APPLICABLE"),
    "specific-preventive-welfare-equipment-sale": ("SCOPE_DEFINED", "NOT_APPLICABLE"),
    "preventive-support": ("SCOPE_DEFINED", "MAPPED"),
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(root: Path = ROOT) -> dict:
    adjudications = load(root / ADJUDICATIONS.relative_to(ROOT))
    corpus = load(root / CORPUS.relative_to(ROOT))
    relations = load(root / RELATIONS.relative_to(ROOT))

    rows = adjudications["adjudications"]
    by_service = {row["service_id"]: row for row in rows}
    assert len(by_service) == len(rows), "duplicate service adjudication"
    assert set(by_service) == set(EXPECTED), "final-six service set mismatch"

    nodes = {row["id"] for row in corpus["nodes"]}
    relation_map = {row["id"]: row for row in relations["relations"]}

    for service_id, (decision, applicability_state) in EXPECTED.items():
        row = by_service[service_id]
        assert row["decision"] == decision
        assert row["applicability_state"] == applicability_state
        assert row["evidence"], f"{service_id}: evidence required"
        for evidence in row["evidence"]:
            assert evidence["issuer"] == "厚生労働省"
            assert evidence["url"].startswith("https://www.mhlw.go.jp/")
            assert evidence["locator"]

        assurance = row["assurance"]
        assert assurance["item_body_verification"] == "NOT_ESTABLISHED"
        assert assurance["currentness"] == "NOT_ESTABLISHED"
        assert assurance["human_review"] == "NOT_REVIEWED"
        assert assurance["publication"] == "BLOCKED"
        assert assurance["route_exposure"] == "BLOCKED"
        assert assurance["automatic_promotion_allowed"] is False

        if applicability_state == "MAPPED":
            assert len(row["node_ids"]) == 1
            assert len(row["relation_ids"]) == 1
            assert set(row["node_ids"]) <= nodes
            relation = relation_map[row["relation_ids"][0]]
            assert relation["service_id"] == service_id
            assert relation["node_id"] == row["node_ids"][0]
            assert relation["verification"] == "NOT_ESTABLISHED"
            scope = load(root / f"data/services/{service_id}/fee-guidance-scope.json")
            assert scope["node_ids"] == row["node_ids"]
            assert scope["relation_ids"] == row["relation_ids"]
            assert scope["assurance"]["item_body_verification"] == "NOT_ESTABLISHED"
            assert scope["assurance"]["currentness"] == "NOT_ESTABLISHED"

        elif applicability_state == "NOT_APPLICABLE":
            assert row["node_ids"] == []
            assert row["relation_ids"] == []
            assert row.get("rationale")
            assert assurance["service_relation_verification"] == "NOT_APPLICABLE"
            scope = load(root / f"data/services/{service_id}/fee-guidance-scope.json")
            assert scope["applicability_state"] == "NOT_APPLICABLE"
            assert scope["node_ids"] == []
            assert scope["relation_ids"] == []

        else:
            raise AssertionError(f"{service_id}: unsupported applicability state {applicability_state}")

    counts = Counter(row["applicability_state"] for row in rows)
    assert counts == Counter({"MAPPED": 4, "NOT_APPLICABLE": 2})
    return {
        "services": len(rows),
        "mapped": counts["MAPPED"],
        "not_applicable": counts["NOT_APPLICABLE"],
        "unresolved": counts["NOT_ESTABLISHED"],
    }


if __name__ == "__main__":
    result = validate()
    print("Fee Guidance final-six adjudication validation PASS:", result)
