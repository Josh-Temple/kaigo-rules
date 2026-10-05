from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_unit_price_item_body_assurance import validate_payload


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class UnitPriceItemBodyAssuranceTest(unittest.TestCase):
    def setUp(self):
        self.artifact = load("data/unit-price-item-body-assurance.json")
        self.index = load("data/unit-price-service-multipliers.json")
        self.manifest = load("data/services/manifest.json")
        self.day_meta = load("data/unit-price-dayservice-meta.json")
        self.region_meta = load("data/unit-price-region-assignments-meta.json")

    def validate(self, artifact=None):
        validate_payload(
            artifact or self.artifact,
            self.index,
            self.manifest,
            self.day_meta,
            self.region_meta,
        )

    def test_canonical_assurance_is_valid(self):
        self.validate()

    def test_pass_fails_closed_when_profile_is_not_verified(self):
        mutated = copy.deepcopy(self.artifact)
        mutated["profile_verification"][0]["verification_state"] = "NOT_ESTABLISHED"
        with self.assertRaises(ValueError):
            self.validate(mutated)

    def test_pass_fails_closed_when_mapped_item_is_missing(self):
        mutated = copy.deepcopy(self.artifact)
        row = next(
            item for item in mutated["service_projections"]
            if item["service_id"] == "homevisit"
        )
        row["mapped_item_count"] = 7
        with self.assertRaises(ValueError):
            self.validate(mutated)

    def test_item_body_must_not_promote_currentness(self):
        mutated = copy.deepcopy(self.artifact)
        row = next(
            item for item in mutated["service_projections"]
            if item["service_id"] == "homevisit"
        )
        row["assurance"]["currentness"] = "CURRENT"
        with self.assertRaises(ValueError):
            self.validate(mutated)

    def test_not_applicable_requires_statutory_basis(self):
        mutated = copy.deepcopy(self.artifact)
        row = next(
            item for item in mutated["service_projections"]
            if item["service_id"] == "specific-welfare-equipment-sale"
        )
        row["evidence"] = ["data/unit-price-item-body-assurance.json"]
        with self.assertRaises(ValueError):
            self.validate(mutated)


if __name__ == "__main__":
    unittest.main()
