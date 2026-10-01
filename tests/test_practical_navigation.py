import json
import unittest
from pathlib import Path
from scripts.run_practical_navigation_regression import Page, require
ROOT=Path(__file__).resolve().parents[1]
class PracticalNavigationTests(unittest.TestCase):
    def test_hidden_payload_does_not_count_as_visible_evidence(self):
        p=Page('<script>問59 canonical-id</script><h1>別の問</h1><a href="/qa/wrong">別の問</a>')
        self.assertNotIn('問59',p.visible)
        self.assertEqual(p.links,['/qa/wrong'])
        with self.assertRaises(AssertionError):require('問59' in p.visible,'wrong question')
    def test_human_cases_have_expected_conditions_and_claim_limits(self):
        d=json.loads((ROOT/'data/practical-navigation-evaluation.json').read_text())
        self.assertFalse(d['human_effectiveness_claims_supported'])
        self.assertGreaterEqual(len(d['cases']),5)
        for c in d['cases']:
            for key in ['question','service','expected_destination','expected_primary_source','source_locator','expected_key_condition_or_exception','must_not_claim','verification_state_expectation']:
                self.assertTrue(c[key],f'{c["id"]}: {key}')
            self.assertEqual(c['service'],'dayservice')
if __name__=='__main__':unittest.main()
