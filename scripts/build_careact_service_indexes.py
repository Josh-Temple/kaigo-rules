#!/usr/bin/env python3
"""Resolve existing Care Act service declarations into reference-only local indexes.

Selection is a structural projection, never independent legal applicability evidence.
No global artifacts or other source families are written.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = 'INDEXED_FROM_SHARED_CORPUS_NOT_SERVICE_VERIFIED'

def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()

def render(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'

def selectors(value, article_order):
    """Read explicit Care Act selectors only, retaining conditional roles upstream."""
    found = set()
    if isinstance(value, list):
        for item in value:
            found.update(selectors(item, article_order))
    elif isinstance(value, dict):
        for key in ('node_ids', 'source_node_ids', 'direct_node_ids', 'target_node_ids'):
            found.update(value.get(key, []))
        for key in ('source_node_id', 'paragraph_node_id', 'regional_service_class_paragraph_node_id', 'via_node_id'):
            if value.get(key):
                found.add(value[key])
        if 'article' in value:
            article = str(value['article'])
            if 'paragraphs' in value:
                found.update(f'careact.article.{article}.p.{p}' for p in value['paragraphs'])
            else:
                found.add(f'careact.article.{article}')
        if 'article_range' in value:
            span = value['article_range']
            first, last = str(span['from']), str(span['through'])
            if first not in article_order or last not in article_order:
                raise ValueError(f'Unresolved article range: {span}')
            start, end = article_order.index(first), article_order.index(last)
            if start > end:
                raise ValueError(f'Reversed article range: {span}')
            found.update(f'careact.article.{a}' for a in article_order[start:end + 1])
        for key, item in value.items():
            if key not in {'article_range', 'implementing_rule', 'technical_read_as_source', 'read_as', 'source_corpus', 'shared_corpus'} and isinstance(item, (dict, list)):
                found.update(selectors(item, article_order))
    if any(not node.startswith('careact.article.') for node in found):
        raise ValueError('Non-Care Act node selector')
    return found

def build(service_id, config):
    scope_path = config['scope_files']['care_insurance_act']
    declaration = load(scope_path)
    if declaration['service_id'] != service_id:
        raise ValueError('Scope service identity mismatch')
    scope = declaration.get('care_insurance_act', declaration)
    nodes_path = 'data/care-insurance-act-nodes.json'
    meta_path = 'data/care-insurance-act-meta.json'
    nodes, meta = load(nodes_path), load(meta_path)
    order = sorted([str(n['article_num']) for n in nodes if n['node_type'] == 'article'], key=lambda a: tuple(map(int, a.split('-'))))
    ids = {n['id'] for n in nodes}
    groups = []
    excluded = {'source_corpus', 'shared_corpus', 'evidence', 'source_evidence', 'assurance', 'policy', 'states', 'verification', 'currentness', 'human_review'}
    for role, value in scope.items():
        if role in excluded or not isinstance(value, (dict, list)):
            continue
        roots = selectors(value, order)
        if not roots:
            continue
        missing = roots - ids
        if missing:
            raise ValueError(f'{service_id}/{role}: missing nodes {sorted(missing)}')
        selected = [n['id'] for n in nodes if any(n['id'] == r or n['id'].startswith(r + '.') for r in roots)]
        groups.append({'scope_role': role, 'selector_node_ids': sorted(roots), 'node_ids': selected, 'scope_relation': 'DECLARED_SCOPE_REFERENCE', 'applicability': 'NOT_ESTABLISHED', 'relation_verification': 'NOT_ESTABLISHED'})
    if not groups:
        raise ValueError(f'{service_id}: empty service scope')
    all_ids = {n for g in groups for n in g['node_ids']}
    return {'format_version': 1, 'generated_by': 'scripts/build_careact_service_indexes.py', 'service_id': service_id, 'layer': 'care_insurance_act', 'status': STATUS,
            'source_corpus': {'law_id': meta['law_id'], 'nodes_file': nodes_path, 'meta_file': meta_path, 'current_revision_id': meta['current_revision']['law_revision_id'], 'xml_sha256': meta['xml_sha256'], 'nodes_sha256': digest(nodes_path), 'meta_sha256': digest(meta_path), 'official_source_url': 'https://laws.e-gov.go.jp/law/409AC0000000123'},
            'scope_source': {'file': scope_path, 'sha256': digest(scope_path)}, 'scope_references': groups,
            'node_ids': {'all': [n['id'] for n in nodes if n['id'] in all_ids]}, 'counts': {'selected_nodes_total': len(all_ids)},
            'assurance': {'legal_text_duplicated': False, 'item_body_verification': 'NOT_ESTABLISHED', 'service_applicability': 'NOT_ESTABLISHED', 'relation_verification': 'NOT_ESTABLISHED', 'currentness': 'NOT_ESTABLISHED', 'human_review': 'NOT_REVIEWED', 'publication': 'BLOCKED', 'route_exposure': 'BLOCKED', 'automatic_verification_promotion_allowed': False, 'conditional_scope_is_not_unconditional_applicability': True}}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--connect', action='store_true', help='Connect only freshly unresolved coverage cells')
    args = parser.parse_args()
    if args.check and args.connect:
        parser.error('--check and --connect are mutually exclusive')
    targets = []
    if args.connect:
        matrix = load('data/database-coverage-matrix.generated.json')
        for service in matrix['services']:
            cell = next(c for c in service['source_families'] if c['source_family'] == 'care_insurance_act')
            if (cell['corpus_availability']['state'], cell['service_scope']['state'], cell['ingestion']['state']) == ('AVAILABLE', 'SCOPE_DEFINED', 'NOT_INGESTED'):
                targets.append(service['service_id'])
    else:
        targets = [p.stem for p in sorted((ROOT / 'data/services').glob('*.json')) if p.stem not in {'manifest', 'catalog.generated'} and load(str(p.relative_to(ROOT))).get('ingestion_indexes', {}).get('care_insurance_act', '').endswith('/care-insurance-act-index.json')]
    for sid in targets:
        config_path = f'data/services/{sid}.json'
        config = load(config_path)
        result = build(sid, config)
        output = f'data/services/{sid}/care-insurance-act-index.json'
        if args.check:
            if (ROOT / output).read_text(encoding='utf-8') != render(result):
                raise SystemExit(f'{output}: stale')
            if config['ingestion_layers']['care_insurance_act']['selected_nodes'] != result['counts']['selected_nodes_total']:
                raise SystemExit(f'{sid}: stale ingestion count')
        else:
            (ROOT / output).write_text(render(result), encoding='utf-8')
            if args.connect:
                config.setdefault('ingestion_indexes', {})['care_insurance_act'] = output
                config.setdefault('ingestion_layers', {})['care_insurance_act'] = {'status': STATUS, 'selected_nodes': result['counts']['selected_nodes_total'], 'currentness': 'NOT_ESTABLISHED', 'human_review': 'NOT_REVIEWED', 'note': '既存service scopeを共有介護保険法への参照索引として収載。条件付き規定・準用先はscope参照であり、適用・relation・item-body verification・現行性・公開の証明には用いない。'}
                (ROOT / config_path).write_text(render(config), encoding='utf-8')
    print(f'Care Act reference indexes: {len(targets)} services; ' + ('current' if args.check else 'written'))

if __name__ == '__main__':
    main()
