#!/usr/bin/env python3
"""Build deterministic AI-ready context packages for curated practical questions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from relation_verification_coverage import build_relation_coverage, make_identity

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "context-packages" / "dayservice-questions.generated.json"


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def index_by_id(rows: list[dict]) -> dict[str, dict]:
    return {row["id"]: row for row in rows}


def evidence_item(node: dict, kind: str) -> dict:
    base = {
        "id": node["id"],
        "kind": kind,
    }
    for field in (
        "path",
        "official_text",
        "editorial_summary",
        "question_summary",
        "answer_summary",
        "verification_status",
        "status",
        "source_id",
        "source_ids",
        "source_document",
        "source_number",
        "verified_at",
        "text_form",
    ):
        if field in node:
            base[field] = node[field]
    return base


def build() -> dict:
    questions = load("questions.json")
    relationships = load("relationships.json")
    rule_nodes = index_by_id(load("rule-nodes.json"))
    notice_nodes = index_by_id(load("notice-nodes.json"))
    qa_items = index_by_id(load("qa-items.json"))
    sources = index_by_id(load("sources.json"))

    coverage = build_relation_coverage()
    verified_edges = coverage["verified"]

    packages = []
    for question in sorted(questions, key=lambda item: item["slug"]):
        if question.get("status") != "verified":
            continue

        slug = question["slug"]
        question_id = f"question:{slug}"
        direct_edges = [
            row for row in relationships
            if row.get("from") == question_id
        ]

        edge_rows = []
        for row in sorted(
            direct_edges,
            key=lambda item: (item.get("relation", ""), item.get("to", "")),
        ):
            identity = make_identity(row["from"], row["relation"], row["to"])
            edge_rows.append(
                {
                    "source_id": row["from"],
                    "relation": row["relation"],
                    "target_id": row["to"],
                    "independent_verification": (
                        "PASS" if identity in verified_edges else "NOT_AUDITED"
                    ),
                }
            )

        rule_ids = question.get("rule_node_ids", [])
        notice_ids = question.get("notice_node_ids", [])
        qa_ids = question.get("qa_item_ids", [])

        missing = {
            "rule_node_ids": [item for item in rule_ids if item not in rule_nodes],
            "notice_node_ids": [item for item in notice_ids if item not in notice_nodes],
            "qa_item_ids": [item for item in qa_ids if item not in qa_items],
        }
        missing = {key: value for key, value in missing.items() if value}
        if missing:
            raise ValueError(f"{slug}: unresolved evidence references: {missing}")

        source_refs = []
        for ref in question.get("source_refs", []):
            source_id = ref["source_id"]
            source = sources.get(source_id)
            if source is None:
                raise ValueError(f"{slug}: unresolved source_ref {source_id}")
            source_refs.append(
                {
                    "source_id": source_id,
                    "locator": ref.get("locator"),
                    "layer": source.get("layer"),
                    "title": source.get("title"),
                    "publisher": source.get("publisher"),
                    "url": source.get("url"),
                    "source_status": source.get("status"),
                    "source_note": source.get("note"),
                }
            )

        evidence = {
            "rules": [evidence_item(rule_nodes[item], "ordinance37") for item in rule_ids],
            "notices": [evidence_item(notice_nodes[item], "interpretation_notice") for item in notice_ids],
            "qa_items": [evidence_item(qa_items[item], "mhlw_qa") for item in qa_ids],
            "sources": source_refs,
        }

        evidence_count = (
            len(evidence["rules"])
            + len(evidence["notices"])
            + len(evidence["qa_items"])
            + len(evidence["sources"])
        )
        if evidence_count == 0:
            raise ValueError(f"{slug}: verified question has no evidence")

        independently_verified_edges = sum(
            1 for edge in edge_rows
            if edge["independent_verification"] == "PASS"
        )

        packages.append(
            {
                "package_id": f"dayservice.question.{slug}",
                "service_id": "dayservice",
                "question": {
                    "slug": slug,
                    "category": question.get("category"),
                    "title": question["title"],
                    "aliases": question.get("aliases", []),
                    "status": question["status"],
                    "last_verified": question.get("last_verified"),
                    "verification_note": question.get("verification_note"),
                },
                "answer": {
                    "short_answer": question.get("short_answer"),
                    "practical_steps": question.get("practical_steps", []),
                    "cautions": question.get("cautions", []),
                },
                "evidence": evidence,
                "relations": edge_rows,
                "assurance": {
                    "question_content_status": question["status"],
                    "relation_edges_total": len(edge_rows),
                    "relation_edges_independently_verified": independently_verified_edges,
                    "relation_edges_not_independently_audited": (
                        len(edge_rows) - independently_verified_edges
                    ),
                    "policy": "Direct evidence and relation-edge assurance are separate. Do not treat an unaudited relation as independently verified.",
                },
                "retrieval": {
                    "terms": list(dict.fromkeys(
                        [question["title"], question.get("category", "")]
                        + question.get("aliases", [])
                    )),
                    "preferred_scope": "curated_direct_evidence_first",
                },
            }
        )

    return {
        "format_version": 1,
        "generated_by": "scripts/build_question_context_packages.py",
        "service_id": "dayservice",
        "package_kind": "CURATED_PRACTICAL_QUESTION_CONTEXT",
        "policy": {
            "faq_is_navigation_layer": True,
            "direct_evidence_preferred": True,
            "relation_verification_kept_separate": True,
            "automatic_legal_conclusion_expansion_allowed": False,
            "unverified_relation_promotion_allowed": False,
        },
        "counts": {
            "packages": len(packages),
            "packages_with_direct_evidence": sum(
                1 for item in packages
                if sum(len(rows) for rows in item["evidence"].values()) > 0
            ),
            "relation_edges": sum(len(item["relations"]) for item in packages),
            "independently_verified_relation_edges": sum(
                item["assurance"]["relation_edges_independently_verified"]
                for item in packages
            ),
        },
        "packages": packages,
    }


def render(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rendered = render(build())
    if args.check:
        if not OUTPUT.exists():
            raise SystemExit("question context packages missing; run builder")
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("question context packages are stale; run builder")
        print("question context packages: current")
        return

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
