#!/usr/bin/env python3
"""Build conservative notice -> Ordinance 37 relation coverage from explicit citations.

This is derived coverage, not a new primary-source parse. A relation is covered
only when:
1. the exact relation identity is on the fixed allowlist below;
2. the notice candidate is independently verified PASS in the review packet;
3. that verified candidate text explicitly cites the target Ordinance article.

Currentness and human-review state remain separate and are not promoted.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "notice-ordinance-explicit-reference-derived-audit.json"

EXPECTED = [
    ("notice.dayservice.personnel.staffing", "ordinance37.article.93"),
    ("notice.dayservice.operation.fees", "ordinance37.article.96"),
    ("notice.dayservice.operation.policy", "ordinance37.article.97"),
    ("notice.dayservice.operation.policy", "ordinance37.article.98"),
    ("notice.dayservice.operation.plan", "ordinance37.article.99"),
    ("notice.dayservice.operation.rules", "ordinance37.article.100"),
    ("notice.dayservice.operation.staffing", "ordinance37.article.101"),
    ("notice.dayservice.operation.bcp", "ordinance37.article.105"),
    ("notice.dayservice.operation.bcp", "ordinance37.article.30-2"),
    ("notice.dayservice.operation.disaster", "ordinance37.article.103"),
    ("notice.dayservice.operation.hygiene", "ordinance37.article.104"),
    ("notice.dayservice.operation.community", "ordinance37.article.104-2"),
    ("notice.dayservice.operation.accident", "ordinance37.article.104-3"),
    ("notice.dayservice.operation.abuse", "ordinance37.article.105"),
    ("notice.dayservice.operation.abuse", "ordinance37.article.37-2"),
    ("notice.dayservice.operation.records", "ordinance37.article.104-4"),
    ("notice.dayservice.operation.incorporation", "ordinance37.article.105"),
]


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def normalize(value: str) -> str:
    return unicodedata.normalize("NFKC", value or "")


def article_marker(target_id: str) -> str:
    match = re.fullmatch(r"ordinance37\.article\.(\d+)(?:-(\d+))?", target_id)
    if not match:
        raise ValueError(f"unsupported target id: {target_id}")
    base, branch = match.groups()
    marker = f"第{base}条"
    if branch:
        marker += f"の{branch}"
    return marker


def build() -> dict:
    relations = load("notice-ordinance-relations.json")
    packet = load("notice-review-packet.json")
    candidates = {
        row["notice_id"]: row
        for row in packet.get("items", [])
        if isinstance(row, dict) and row.get("notice_id")
    }
    relation_rows = {
        (
            str(row.get("from_notice_id") or ""),
            str(row.get("relation") or ""),
            str(row.get("to_ordinance_id") or ""),
        ): row
        for row in relations
    }

    checks = []
    for notice_id, target_id in EXPECTED:
        differences = []
        identity = (notice_id, "interprets_or_explains", target_id)
        if identity not in relation_rows:
            differences.append("committed relation identity missing")

        candidate = candidates.get(notice_id)
        if not candidate:
            differences.append("notice candidate missing from review packet")
            candidate_text = ""
            candidate_sha = None
            independent = None
        else:
            candidate_text = str(candidate.get("candidate_text") or "")
            candidate_sha = candidate.get("candidate_text_sha256")
            independent = candidate.get("independent_verification", {}).get("result")
            if independent != "PASS":
                differences.append("notice candidate independent verification is not PASS")
            recorded_sha = candidate.get("independent_verification", {}).get(
                "recorded_candidate_sha256"
            )
            if not candidate_sha or recorded_sha != candidate_sha:
                differences.append("notice candidate hash is not pinned by independent verification")

        marker = article_marker(target_id)
        if normalize(marker) not in normalize(candidate_text):
            differences.append(f"explicit target citation missing: {marker}")

        checks.append(
            {
                "id": f"{notice_id}-to-{target_id}",
                "from_notice_id": notice_id,
                "relation": "interprets_or_explains",
                "to_ordinance_id": target_id,
                "explicit_citation": marker,
                "candidate_text_sha256": candidate_sha,
                "basis_independent_verification": independent,
                "result": "PASS" if not differences else "FAIL",
                "differences": differences,
            }
        )

    result = "PASS" if all(row["result"] == "PASS" for row in checks) else "FAIL"
    return {
        "format_version": 1,
        "audit_kind": "DERIVED_FROM_INDEPENDENT_NOTICE_TEXT_EXPLICIT_REFERENCE",
        "audit_result": result,
        "basis": {
            "notice_review_packet": "data/notice-review-packet.json",
            "notice_relation_file": "data/notice-ordinance-relations.json",
            "independent_verifier": "scripts/verify_notice_rouki25_independent.py",
        },
        "method": (
            "Only fixed allowlisted relation identities are covered. Each source notice "
            "candidate must have independent PASS with a pinned candidate hash, and that "
            "same candidate text must explicitly cite the target Ordinance 37 article."
        ),
        "checks": checks,
        "coverage": {
            "relations_in_this_lane": len(checks),
            "relations_passed": sum(row["result"] == "PASS" for row in checks),
        },
        "limitations": [
            "This is derived coverage from previously independently verified notice candidate text; it is not a second live-source parse.",
            "Only explicit article-number citations are covered; structurally plausible or semantically related mappings without explicit citations remain unverified.",
            "rouki25-dayservice currentness remains HOLD and is not changed by this relation audit.",
            "No HUMAN_VERIFIED or VERIFIED_CURRENT state is promoted.",
        ],
        "safety": {
            "human_verified": False,
            "verified_current": False,
            "automatic_promotion_allowed": False,
            "promotes_unlisted_relations": False,
            "promotes_notice_currentness": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("notice explicit-reference derived audit is stale; run builder")
        print("notice explicit-reference derived audit: current")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
