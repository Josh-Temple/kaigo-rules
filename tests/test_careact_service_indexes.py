import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('careact_indexes', ROOT / 'scripts/build_careact_service_indexes.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class CareActServiceIndexTest(unittest.TestCase):
    def test_connected_indexes_are_current_and_fail_closed(self):
        connected = 0
        for path in (ROOT / 'data/services').glob('*.json'):
            config = builder.load(str(path.relative_to(ROOT)))
            index = config.get('ingestion_indexes', {}).get('care_insurance_act', '')
            if not index.endswith('/care-insurance-act-index.json'):
                continue
            connected += 1
            expected = builder.build(config['service_id'], config)
            self.assertEqual(builder.load(index), expected)
            self.assertEqual(config['ingestion_layers']['care_insurance_act']['selected_nodes'], len(expected['node_ids']['all']))
            self.assertFalse(expected['assurance']['automatic_verification_promotion_allowed'])
            for key in ('item_body_verification', 'service_applicability', 'relation_verification', 'currentness'):
                self.assertEqual(expected['assurance'][key], 'NOT_ESTABLISHED')
            for group in expected['scope_references']:
                self.assertEqual(group['relation_verification'], 'NOT_ESTABLISHED')
            self.assertNotIn('official_text', builder.render(expected))
            self.assertNotIn('text', expected)
        self.assertGreater(connected, 0)

    def test_definition_paragraph_does_not_select_other_services(self):
        config = builder.load('data/services/care-management.json')
        result = builder.build('care-management', config)
        group = next(g for g in result['scope_references'] if g['scope_role'] == 'service_definition_scope')
        self.assertEqual(group['selector_node_ids'], ['careact.article.8.p.24'])
        self.assertNotIn('careact.article.8.p.7', group['node_ids'])

    def test_range_numeric_order_and_interstitial_articles(self):
        order = ['78-4', '78-5', '78-6', '78-6-2', '78-7', '78-8', '78-9', '78-10', '78-11', '78-12']
        found = builder.selectors({'article_range': {'from': '78-5', 'through': '78-11'}}, order)
        self.assertIn('careact.article.78-6-2', found)
        self.assertIn('careact.article.78-10', found)
        self.assertNotIn('careact.article.78-12', found)

    def test_external_instrument_article_is_not_care_act_selector(self):
        found = builder.selectors({'node_ids': ['careact.article.71'], 'implementing_rule': {'article': '127'}, 'technical_read_as_source': {'article': '35-12'}}, [])
        self.assertEqual(found, {'careact.article.71'})

    def test_unresolved_range_and_wrong_service_fail_closed(self):
        with self.assertRaises(ValueError):
            builder.selectors({'article_range': {'from': '999', 'through': '1000'}}, [])
        config = builder.load('data/services/care-management.json')
        with self.assertRaises(ValueError):
            builder.build('another-service', copy.deepcopy(config))

    def test_special_and_incorporation_references_remain_distinct(self):
        result = builder.build('preventive-homerehab', builder.load('data/services/preventive-homerehab.json'))
        group = next(g for g in result['scope_references'] if g['scope_role'] == 'provider_governance')
        self.assertIn('careact.article.115-11', group['selector_node_ids'])
        self.assertIn('careact.article.70-2', group['selector_node_ids'])
        self.assertEqual(group['applicability'], 'NOT_ESTABLISHED')
        self.assertTrue(result['assurance']['conditional_scope_is_not_unconditional_applicability'])


if __name__ == '__main__':
    unittest.main()
