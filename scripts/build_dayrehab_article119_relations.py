#!/usr/bin/env python3
"""Build service-specific Article 119 incorporation relations for dayrehab."""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCOPE=ROOT/"data/services/dayrehab/ordinance37-scope.json"
OUTPUT=ROOT/"data/services/dayrehab/ordinance37-relations.generated.json"

def build():
    scope=json.loads(SCOPE.read_text(encoding="utf-8"))
    inc=scope["incorporated_scope"]
    if inc.get("via_article")!="119":
        raise ValueError("dayrehab incorporated scope must be via Article 119")
    articles=[str(x) for x in inc.get("article_numbers",[])]
    if len(articles)!=25 or len(set(articles))!=25:
        raise ValueError(f"expected 25 unique Article 119 targets, got {len(articles)}")
    return [
      {
        "from":"ordinance37.article.119",
        "relation":"incorporates_by_reference",
        "to":f"ordinance37.article.{article}",
        "service_id":"dayrehab",
        "declared_basis":"ARTICLE_119_CURRENT_TEXT",
        "verification_status":"INDEPENDENT_AUDIT_REQUIRED"
      }
      for article in articles
    ]

def render():
    return json.dumps(build(),ensure_ascii=False,indent=2)+"\n"

def main():
    p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); a=p.parse_args()
    expected=render()
    if a.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8")!=expected:
            raise SystemExit("dayrehab Article 119 relations are stale; run builder")
        print("dayrehab Article 119 relations: current")
        return
    OUTPUT.write_text(expected,encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
if __name__=="__main__": main()
