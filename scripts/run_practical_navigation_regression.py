#!/usr/bin/env python3
"""Follow rendered links from five practical searches to specific primary sources.

No data-layer assurance promotion or human-effectiveness inference is permitted.
"""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self, body):
        super().__init__(); self.text = []; self.links = []; self.skip = 0
        self.feed(body)
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
        if tag == 'a': self.links.extend(v for k,v in attrs if k=='href' and v)
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip = max(0,self.skip-1)
    def handle_data(self, data):
        if not self.skip: self.text.append(data)
    @property
    def visible(self): return re.sub(r'\s+', ' ', ' '.join(self.text))

def require(condition, reason):
    if not condition: raise AssertionError(reason)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--base-url',required=True);ap.add_argument('--expected-sha',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    cache={}
    def raw(url):
        url=urllib.parse.urldefrag(url)[0]
        if url not in cache:
            req=urllib.request.Request(url,headers={'User-Agent':'kaigo-rules-practical-regression/1','Cache-Control':'no-cache'})
            with urllib.request.urlopen(req,timeout=60) as response:
                require(response.status==200, f'HTTP {response.status}: {url}');cache[url]=response.read()
        return cache[url]
    def page(path):
        url=urllib.parse.urljoin(args.base_url,path)
        return Page(raw(url).decode('utf-8',errors='replace'))
    def follow(p, href):
        require(href in p.links, f'Not a rendered link: {href}')
        return page(href)
    def pdf(url,number,needles):
        data=raw(url)
        require(data.startswith(b'%PDF'), 'not a PDF primary source')
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'source.pdf';src.write_bytes(data)
            text=subprocess.check_output(['pdftotext','-f',str(number),'-l',str(number),'-layout',str(src),'-']).decode()
        for needle in needles:require(needle in text,f'Primary PDF page {number} missing {needle}')
        return hashlib.sha256(data).hexdigest()
    results=[]
    try:
        require(json.loads(raw(args.base_url+'/api/version'))['commit_sha']==args.expected_sha,'exact SHA mismatch')
        fixture=json.loads((ROOT/'data/practical-navigation-evaluation.json').read_text())
        for case in fixture['cases']:
            try:
                search=page('/search?'+urllib.parse.urlencode({'q':case['question']}))
                faq_links=[x for x in search.links if x.startswith('/questions/')]
                require(faq_links and faq_links[0]==case['expected_destination'],'expected FAQ not first')
                faq=follow(search,case['expected_destination'])
                require('FAQ根拠対応を確認済み' in faq.visible,'FAQ evidence scope missing')
                require('根拠資料全体の確認状態は別です' in faq.visible,'assurance scope missing')
                rule=follow(faq,case['rule_destination'])
                require(case['canonical_id'] in rule.visible,'wrong canonical article')
                require(case['article_title'] in rule.visible,'wrong article number')
                require(case['source_locator'].split(' / ')[0] in rule.visible,'source locator not displayed')
                primary=case['expected_primary_source']
                primary_href = next((x for x in faq.links if x.split('#')[0]==primary), None)
                require(primary_href is not None,'FAQ primary source link missing')
                require(urllib.parse.quote(case['article_title']) in primary_href,'official article text locator missing')
                official=Page(raw(primary).decode('utf-8',errors='replace'))
                require(case['article_title'] in official.visible,'official article missing')
                require('通所介護' in official.visible,'official service missing')
                # Article section, not unrelated occurrences elsewhere in the whole source.
                section=official.visible.split(case['article_title'],1)[1]
                section=re.split(r'第[一二三四五六七八九十百]+条',section,1)[0]
                require(case.get('primary_article_condition',case['expected_key_condition_or_exception']) in section,'condition not in target official article')
                require(not any(x.startswith('/services/dayrehab') for x in faq.links),'service scope leak')
                if case['slug']=='nurse-staffing':
                    qa=follow(faq,'/qa/qa.dayservice.nurse.external.2015.50')
                    require('問50' in qa.visible and '旧資料・修正あり' in qa.visible,'old QA masquerades as current')
                    corrected=follow(qa,'/qa/qa.mhlw.d9a7f5b49c1ba8a9326e')
                    require('問59' in corrected.visible and '問 50 の修正' in corrected.visible,'wrong correction destination')
                    qurl='https://www.mhlw.go.jp/content/12300000/001246407.pdf#page=36'
                    require(qurl in corrected.links,'correction locator missing')
                    qhash=pdf(qurl,36,['問 59','問 50','健康状態'])
                    notice=follow(faq,'/notices/notice.dayservice.nurse.external-linkage')
                    require('現行性は確認中' in notice.visible and '人手確認は未実施' in notice.visible,'notice confirmation state missing')
                    nurl='https://www.mhlw.go.jp/content/12300000/000869798.pdf#page=30'
                    require(nurl in notice.links and nurl in search.links,'different canonical notice sources')
                    require(not any('/qa/index.html' in x for x in notice.links),'notice misroutes to QA index')
                    nhash=pdf(nurl,30,['看護職員','六','通所介護'])
                    pdf(nurl,31,['営業日','密接かつ適切'])
                    results.append({'id':'nurse-primary-locators','status':'PASS','audit_kind':'INDEPENDENT_PRIMARY_SOURCE_LOCATOR_MATCH_ONLY','qa_pdf_sha256':qhash,'notice_pdf_sha256':nhash,'currentness_promoted':False,'human_review_promoted':False})
                    require('/qa/qa.dayservice.nurse.external.2015.50' in search.links,'search QA relation differs from FAQ')
                    require(faq_links==['/questions/nurse-staffing'],'weak unrelated FAQs still expanded')
                results.append({'id':case['id'],'status':'PASS','question':case['question'],'destination':case['expected_destination'],'canonical_id':case['canonical_id'],'primary_source':primary,'primary_sha256':hashlib.sha256(raw(primary)).hexdigest()})
            except Exception as exc:results.append({'id':case['id'],'status':'FAIL','error':str(exc)})
        for route in ['/services/dayrehab','/rules?service=dayrehab','/notices?service=dayrehab','/services/dayrehab/remuneration','/services/dayrehab/remuneration/guidance']:
            try:
                p=page(route)
                for destination in ['/services/dayrehab/search','/rules?service=dayrehab','/notices?service=dayrehab','/services/dayrehab/remuneration']:
                    require(destination in p.links,'service nav context lost: '+destination)
                if 'remuneration' in route:require('確認中' in p.visible and '人手確認' in p.visible,'bounded publication caution missing')
                results.append({'id':route,'status':'PASS'})
            except Exception as exc:results.append({'id':route,'status':'FAIL','error':str(exc)})
        require(json.loads(raw(args.base_url+'/api/version'))['commit_sha']==args.expected_sha,'SHA changed during run')
    except Exception as exc:results.append({'id':'run','status':'FAIL','error':str(exc)})
    report={'format_version':1,'sha':args.expected_sha,'status':'PASS' if results and all(x['status']=='PASS' for x in results) else 'FAIL','human_effectiveness_claims_supported':False,'cases':results}
    Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
