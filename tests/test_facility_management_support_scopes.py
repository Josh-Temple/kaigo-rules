from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_facility_management_support_scopes.py"
SPEC = importlib.util.spec_from_file_location("scope_validator", MODULE_PATH)
scope_validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(scope_validator)

class FacilityManagementSupportScopeTest(unittest.TestCase):
    def test_scope_wave_is_fail_closed_and_referentially_valid(self):
        self.assertEqual(scope_validator.validate_all(), [])

    def test_target_set_is_exactly_chat_e_classes(self):
        self.assertEqual(set(scope_validator.TARGETS), {"elderly-welfare-facility","elderly-health-facility","care-medical-institution","care-management","preventive-support"})

    def test_each_target_has_five_scope_lanes(self):
        self.assertEqual(len(scope_validator.SCOPE_KEYS), 5)

if __name__ == "__main__":
    unittest.main()
