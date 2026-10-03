from __future__ import annotations
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_home_service_scope_wave import validation_errors

class HomeServiceScopeWaveTest(unittest.TestCase):
    def test_home_service_scope_wave(self):
        self.assertEqual([], validation_errors(ROOT))

if __name__=="__main__":
    unittest.main()
