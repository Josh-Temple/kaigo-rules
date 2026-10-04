#!/usr/bin/env python3
"""Validate source-versioned shared guidance without promoting legal assurance."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'data/shared/fee-guidance/'


def validate(root=ROOT):
    def read(path):
        return json.loads((root / path).read_text())
    manifest = read(BASE + 'manifest.json')
    nodes = read(manifest['canonical_node_store'])['nodes']
    sources = read(manifest['source_registry'])['sources']
    apps = read(manifest['service_applicability'])['services']
    relations = read(manifest['service_relations'])['relations']
    def unique(rows, key):
        result = {r[key]: r for r in rows}
        assert len(result) == len(rows), 'duplicate ' + key
        return result
    node_map = unique(nodes, 'id')
    source_map = unique(sources, 'id')
    relation_map = unique(relations, 'id')
    unique(apps, 'service_id')
    identities = read(manifest['identity_map'])['identities']
    assert set(unique(identities, 'node_id')) == set(node_map), 'identity coverage'
    def closed(a):
        assert a['automatic_promotion_allowed'] is False
        for key in ('item_body_verification', 'currentness', 'service_applicability_verification', 'service_relation_verification'):
            assert a[key] == 'NOT_ESTABLISHED', key
        assert a['human_review'] == 'NOT_REVIEWED'
        assert a['publication'] == a['route_exposure'] == 'BLOCKED'
    closed(manifest['assurance'])
    for source in sources:
        payload = (root / source['snapshot_path']).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == source['snapshot_sha256'], 'source snapshot hash'
        assert source['url'].startswith('https://www.mhlw.go.jp/')
        assert source['currentness'] == 'NOT_ESTABLISHED'
    ranges = []
    legacy_targets = set()
    for node in nodes:
        closed(node['assurance'])
        assert not node.get('official_text'), 'duplicated/promoted official body'
        if node['content_kind'] == 'LEGACY_CANONICAL_REFERENCE':
            ref = node['legacy_ref']
            target = (ref['path'], ref['collection'], ref['id'])
            assert target not in legacy_targets, 'duplicate legacy target'
            legacy_targets.add(target)
            data = read(ref['path'])
            items = data if ref['collection'] is None else data[ref['collection']]
            assert sum(i['id'] == ref['id'] for i in items) == 1, 'dangling legacy reference'
        else:
            source = source_map[node['source_id']]
            ref = node['text_ref']
            assert ref['path'] == source['snapshot_path']
            lines = (root / ref['path']).read_text().splitlines()
            a, b = ref['start_line'], ref['end_line']
            assert 1 <= a <= b <= len(lines), 'invalid range'
            assert hashlib.sha256('\n'.join(lines[a-1:b]).encode()).hexdigest() == ref['sha256'], 'section hash'
            assert node['omissions_preserved'] is True
            assert node['columns'] == 'NEW_LEFT_OLD_RIGHT_UNSEPARATED'
            for path, x, y in ranges:
                assert path != ref['path'] or b < x or a > y, 'overlapping duplicate sections'
            ranges.append((ref['path'], a, b))
    for app in apps:
        closed(app['assurance'])
        assert app['state'] == 'MAPPED'
        assert set(app['node_ids']) <= set(node_map)
        if app.get('relation_ids'):
            assert app['ingestion_state'] == 'INGESTED_PARTIAL'
            scope = read(f"data/services/{app['service_id']}/fee-guidance-scope.json")
            assert scope['node_ids'] == app['node_ids']
            assert scope['relation_ids'] == app['relation_ids']
            cfg = read(f"data/services/{app['service_id']}.json")
            assert cfg['scope_files']['fee_guidance'].endswith('/fee-guidance-scope.json')
            for rid in app['relation_ids']:
                r = relation_map[rid]
                assert r['service_id'] == app['service_id'] and r['node_id'] in app['node_ids']
    for r in relations:
        assert r['node_id'] in node_map and r['source_id'] in source_map
        assert r['relation_type'] == 'SOURCE_SECTION_SCOPE' and r['verification'] == 'NOT_ESTABLISHED'
    return len(nodes), len(apps)


if __name__ == '__main__':
    print('Shared fee guidance validation PASS:', validate())
