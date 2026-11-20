#!/usr/bin/env python3
"""Keep explicitly quarantined handbook requirements out of the public build.

The historical input data is never edited. The renderer enforces the boundary
in ordinary builds; this script also verifies it and audits generated sites.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import html
import json
import re
from collections import Counter
from pathlib import Path

COMPONENT_HASH = '7e79c66f82de6f5866b57441ca8efb6cd19c1f7f146b5a29703c0d79411c9298'
FILTERED_COMPONENT_HASH = '522eded81593401ec3fe87d8a1a8f6dbdc36b60c6ecec274740624d3d108100c'
DATA_HASH = '47a0ed8e1837e6f76ee0a6230f7bc0dcb0d5f5a62529bdb346ac3f4dc592a2f4'
EXPECTED_WITHHELD = 522
OLD_ROLES = '  const roles = staffing ? chapter.role_sections : chapter.rule_sections;'
NEW_ROLES = '''  const candidates = staffing ? chapter.role_sections : chapter.rule_sections;
  // Research candidates are retained in source data but need acceptance before publication.
  const isWithheld = (requirement: HandbookRoleSection["requirements"][number]) =>
    requirement.id.startsWith("mesh-") ||
    (requirement.description.includes("Research Mesh") && requirement.description.includes("隔離候補"));
  const withheld = Boolean(candidates?.some(role => role.requirements.some(isWithheld)));
  const roles = candidates?.map(role => ({
    ...role, requirements: role.requirements.filter(requirement => !isWithheld(requirement)),
  })).filter(role => role.requirements.length > 0);'''
OLD_GUARD = '  if (!allowed || !roles?.length) return null;'
NEW_GUARD = '''  if (!allowed) return null;
  if (!roles?.length) return withheld
    ? <p className="handbook-role-warning">一部の説明は原典との照合が済むまで掲載を控えています。関連する条文・資料も確認してください。</p>
    : null;'''
HEADING = '    <GroupHeading>{groupHeading}</GroupHeading>'
NOTICE = ('{withheld ? <p className="handbook-role-warning">一部の説明は原典との照合が済むまで'
          '掲載を控えています。関連する条文・資料も確認してください。</p> : null}')


def digest(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError('Missing or unsafe publication input: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quarantined(requirement: dict) -> bool:
    identifier, description = requirement.get('id'), requirement.get('description')
    if not isinstance(identifier, str) or not isinstance(description, str):
        raise RuntimeError('Invalid handbook requirement')
    return identifier.startswith('mesh-') or ('Research Mesh' in description and '隔離候補' in description)


def inventory(source: Path) -> list[tuple[str, str, str, str]]:
    data = source / 'data/handbook-content.json'
    if digest(data) != DATA_HASH:
        raise RuntimeError('Handbook source data changed; review publication boundary')
    services = json.loads(data.read_text(encoding='utf-8'))['services']
    result = []
    for service_id, service in services.items():
        for chapter_id, chapter in service.get('chapters', {}).items():
            for field in ('role_sections', 'rule_sections'):
                for role in chapter.get(field, []) or []:
                    for requirement in role.get('requirements', []) or []:
                        if quarantined(requirement):
                            result.append((service_id, chapter_id, role['id'], requirement['id']))
    if len(result) != EXPECTED_WITHHELD or len(set(result)) != len(result):
        raise RuntimeError('Unexpected quarantined handbook inventory')
    return result


def apply(source: Path) -> int:
    withheld = inventory(source)
    component = source / 'components/service-handbook.tsx'
    component_hash = digest(component)
    if component_hash == FILTERED_COMPONENT_HASH:
        return len(withheld)
    if component_hash != COMPONENT_HASH:
        raise RuntimeError('Handbook renderer changed; review publication boundary')
    old = component.read_text(encoding='utf-8')
    if old.count(OLD_ROLES) != 1 or old.count(OLD_GUARD) != 1 or old.count(HEADING) != 2:
        raise RuntimeError('Unexpected handbook renderer structure')
    new = old.replace(OLD_ROLES, NEW_ROLES, 1).replace(OLD_GUARD, NEW_GUARD, 1)
    new = new.replace(HEADING, HEADING + '\n    ' + NOTICE)
    component.write_text(new, encoding='utf-8')
    return len(withheld)


def audit(source: Path, output: Path) -> dict:
    withheld = inventory(source)
    if output.is_symlink() or not output.is_dir():
        raise RuntimeError('Unsafe publication output')
    pages: dict[Path, str] = {}
    for service, chapter, role, requirement in withheld:
        page = output / 'handbook' / service / (chapter.replace('_', '-') + '.html')
        if page not in pages:
            if page.is_symlink() or not page.is_file():
                raise RuntimeError('Missing handbook page: ' + str(page))
            pages[page] = page.read_text(encoding='utf-8')
        anchor = 'staffing-role' if chapter == 'staffing' else f'chapter-{chapter}-rule'
        blocked_id = f'id="{anchor}-{role}-requirement-{requirement}"'
        if blocked_id in pages[page]:
            raise RuntimeError('Quarantined requirement present in publication: ' + blocked_id)
    totals: Counter[tuple[str, str, str]] = Counter()
    descriptions = {}
    data = json.loads((source / 'data/handbook-content.json').read_text(encoding='utf-8'))
    for service, details in data['services'].items():
        for chapter, info in details.get('chapters', {}).items():
            for field in ('role_sections', 'rule_sections'):
                for role in info.get(field, []) or []:
                    totals[(service, chapter, role['id'])] += len(role.get('requirements', []) or [])
                    for requirement in role.get('requirements', []) or []:
                        if quarantined(requirement):
                            descriptions[(service, chapter, role['id'], requirement['id'])] = requirement['description']
    text_pages = {page: html.unescape(re.sub(r'<[^>]+>', ' ', content)) for page, content in pages.items()}
    distinctive_lines = set()
    for service, chapter, role, requirement in withheld:
        page = output / 'handbook' / service / (chapter.replace('_', '-') + '.html')
        description = descriptions[(service, chapter, role, requirement)]
        for line in description.splitlines():
            line = re.sub(r'^【Research Mesh隔離候補・法令適合未審査】', '', line.strip())
            line = re.sub(r'^Research Meshの隔離候補：\s*', '', line).strip()
            if len(line) >= 30 and line in text_pages[page]:
                raise RuntimeError('Quarantined text present in publication: ' + requirement)
            if len(line) >= 35:
                distinctive_lines.add(line)
    scanned = 0
    for path in output.rglob('*'):
        if path.is_symlink():
            raise RuntimeError('Unsafe symbolic link in publication: ' + str(path))
        if not path.is_file() or path.suffix not in ('.html', '.json', '.mjs', '.js', '.css', '.txt', '.xml', '.gz'):
            continue
        if path.suffix == '.gz':
            with gzip.open(path, 'rt', encoding='utf-8') as stream:
                content = stream.read()
        else:
            content = path.read_text(encoding='utf-8')
        content = html.unescape(content)
        scanned += 1
        if any(line in content for line in distinctive_lines):
            raise RuntimeError('Quarantined text found in distribution: ' + str(path.relative_to(output)))
    blocked = Counter((service, chapter, role) for service, chapter, role, _ in withheld)
    fully_withheld = [group for group, count in blocked.items() if totals[group] == count]
    for service, chapter, role in fully_withheld:
        anchor = 'staffing-role' if chapter == 'staffing' else f'chapter-{chapter}-rule'
        target = f'{anchor}-{role}'
        page = output / 'handbook' / service / (chapter.replace('_', '-') + '.html')
        overview = output / 'services' / service / 'index.html'
        if (f'id="{target}"' in pages[page] or f'#{target}"' in pages[page] or
                (overview.is_file() and f'#{target}"' in overview.read_text(encoding='utf-8'))):
            raise RuntimeError('Quarantined role or navigation present in publication: ' + target)
    return {'quarantined_requirements': len(withheld), 'fully_withheld_roles': len(fully_withheld),
            'handbook_pages_checked': len(pages), 'distinctive_lines_checked': len(distinctive_lines),
            'distribution_files_checked': scanned}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('apply', 'audit'))
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path, nargs='?')
    args = parser.parse_args()
    if args.mode == 'apply' and args.output is None:
        print(json.dumps({'quarantined_requirements': apply(args.source)}, ensure_ascii=False))
    elif args.mode == 'audit' and args.output is not None:
        print(json.dumps(audit(args.source, args.output), ensure_ascii=False))
    else:
        parser.error('audit requires output; apply does not accept it')


if __name__ == '__main__':
    main()
