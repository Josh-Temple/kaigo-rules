#!/usr/bin/env python3
"""Strict quality audit across all 39 services and 585 chapters.

Uses standard library html.parser.HTMLParser for structural analysis:
- Headings hierarchy (exactly 1 h1, at least 1 h2)
- Table container validation (.handbook-table-scroll for mobile responsiveness)
- Anchor verification (every #hash link points to an existing id on the same page)
- Intra-site relative link verification (every relative link points to an existing file)
- Structured warning banner detection (.handbook-roles-pending, .handbook-working-note)
- Duplicate ID detection
- TOC matching between service index and chapter pages
- Tri-state classification:
  1. Mechanically passed (機械的合格)
  2. Issues detected (問題検出)
  3. Non-mechanically verifiable (機械判定不能・人手/専門的確認事項)
"""
from __future__ import annotations

import csv
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = Path("/workspace/build_kaigo_private_site")

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr"
}

class ChapterHTMLAuditor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.headings = {"h1": [], "h2": [], "h3": [], "h4": [], "h5": []}
        self.current_tag = None
        self.current_heading = None
        self.heading_text_acc = []
        self.links = []
        self.has_table_scroll = False
        self.in_table_scroll = False
        self.table_count = 0
        self.tables_in_scroll = 0
        self.has_roles_pending_section = False
        self.has_working_note = False
        self.has_checklist = False
        self.checkbox_print_count = 0
        self.tag_stack = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        classes = set(attrs_dict.get("class", "").split())
        
        if tag not in VOID_ELEMENTS:
            self.tag_stack.append((tag, classes))
            
        ident = attrs_dict.get("id")
        if ident:
            self.ids.append(ident)
            
        if tag in self.headings:
            self.current_heading = tag
            self.heading_text_acc = []
            
        if tag == "div" and "handbook-table-scroll" in classes:
            self.in_table_scroll = True
            self.has_table_scroll = True
            
        if tag == "table":
            self.table_count += 1
            if self.in_table_scroll or any("handbook-table-scroll" in c for _, c in self.tag_stack):
                self.tables_in_scroll += 1
                
        if tag == "section" and "handbook-roles-pending" in classes:
            self.has_roles_pending_section = True
            
        if "handbook-working-note" in classes:
            self.has_working_note = True
            
        if tag == "div" and "handbook-checklist" in classes:
            self.has_checklist = True
            
        if tag == "input" and attrs_dict.get("data-handbook-print") == "true":
            self.checkbox_print_count += 1
            
        href = attrs_dict.get("href")
        if href:
            self.links.append(href)

    def handle_endtag(self, tag):
        if self.current_heading == tag:
            text = "".join(self.heading_text_acc).strip()
            self.headings[tag].append(text)
            self.current_heading = None
            self.heading_text_acc = []
            
        if tag not in VOID_ELEMENTS and self.tag_stack:
            while self.tag_stack and self.tag_stack[-1][0] != tag:
                self.tag_stack.pop()
            if self.tag_stack and self.tag_stack[-1][0] == tag:
                popped_tag, popped_classes = self.tag_stack.pop()
                if popped_tag == "div" and "handbook-table-scroll" in popped_classes:
                    self.in_table_scroll = False

    def handle_data(self, data):
        if self.current_heading:
            self.heading_text_acc.append(data)


def run_audit(csv_out_path: Path = Path("/workspace/04_all_handbook_quality.csv")) -> dict:
    master_path = ROOT / "data/handbook.generated.json"
    hb_data = json.loads(master_path.read_text(encoding="utf-8"))
    services = hb_data["services"]
    
    expected_services = len(services)
    expected_chapters = expected_services * 15
    
    csv_file = open(csv_out_path, "w", encoding="utf-8", newline="")
    writer = csv.writer(csv_file)
    writer.writerow([
        "service_id", "service_label", "chapter_id", "chapter_number", "chapter_title",
        "file_path", "file_bytes",
        "h1_count", "h2_count", "h3_count", "h4_count", "h5_count",
        "heading_hierarchy_valid", "toc_matched", "duplicate_ids_count",
        "broken_internal_links_count", "broken_anchor_links_count",
        "table_count", "tables_in_scroll_count", "table_overflow_risk",
        "has_roles_pending_section", "has_working_note", "has_checklist", "print_checkbox_count",
        "mechanical_audit_status", "issue_details", "non_mechanical_review_items"
    ])
    
    inspected_count = 0
    passed_mechanical_count = 0
    issues_count = 0
    missing_files_count = 0
    
    services_with_pending_roles = set()
    all_issues = []
    
    for service in services:
        sid = service["service_id"]
        slabel = service.get("label", sid)
        chapters = service["chapters"]
        
        # Service TOC check
        svc_file = SITE_DIR / "services" / sid / "index.html"
        svc_html = svc_file.read_text(encoding="utf-8") if svc_file.is_file() else ""
        
        for chapter in chapters:
            cid = chapter["section_id"]
            slug = cid.replace("_", "-")
            cnum = chapter["number"]
            ctitle = chapter["title"]
            
            ch_file = SITE_DIR / "handbook" / sid / f"{slug}.html"
            if not ch_file.is_file():
                missing_files_count += 1
                issues_count += 1
                writer.writerow([
                    sid, slabel, cid, cnum, ctitle, "", 0,
                    0, 0, 0, 0, 0, False, False, 0, 1, 0,
                    0, 0, False, False, False, False, 0,
                    "FAIL_MISSING_FILE", f"File not found: handbook/{sid}/{slug}.html", "ファイル欠落のため点検不能"
                ])
                continue
                
            inspected_count += 1
            content = ch_file.read_text(encoding="utf-8")
            file_bytes = ch_file.stat().st_size
            
            # Run HTML structural parser
            auditor = ChapterHTMLAuditor()
            try:
                auditor.feed(content)
            except Exception as e:
                issues_count += 1
                writer.writerow([
                    sid, slabel, cid, cnum, ctitle, f"handbook/{sid}/{slug}.html", file_bytes,
                    0, 0, 0, 0, 0, False, False, 0, 1, 0,
                    0, 0, False, False, False, False, 0,
                    "FAIL_HTML_PARSE_ERROR", str(e), "HTML構文エラーのため点検中断"
                ])
                continue
                
            h1s = len(auditor.headings["h1"])
            h2s = len(auditor.headings["h2"])
            h3s = len(auditor.headings["h3"])
            h4s = len(auditor.headings["h4"])
            h5s = len(auditor.headings["h5"])
            
            # Heading hierarchy: exactly 1 h1, at least 1 h2
            h_valid = (h1s == 1 and h2s >= 1)
            
            # TOC correspondence
            toc_matched = (f'href="../../handbook/{sid}/{slug}.html"' in svc_html)
            
            # Duplicate ID detection
            id_counts = {}
            for ident in auditor.ids:
                id_counts[ident] = id_counts.get(ident, 0) + 1
            dup_ids = sum(1 for ident, cnt in id_counts.items() if cnt > 1)
            
            # Check anchors and relative links
            page_ids_set = set(auditor.ids)
            broken_anchors = 0
            broken_rel_links = 0
            
            for href in auditor.links:
                if href.startswith("#"):
                    anchor = href[1:]
                    if anchor and anchor not in page_ids_set:
                        broken_anchors += 1
                elif href.startswith("http://") or href.startswith("https://") or href.startswith("mailto:") or href.startswith("javascript:"):
                    continue
                else:
                    clean_href = href.split("?")[0].split("#")[0]
                    target_path = (ch_file.parent / clean_href).resolve()
                    if not target_path.exists():
                        broken_rel_links += 1
                        
            # Table responsiveness check
            table_overflow_risk = (auditor.table_count > auditor.tables_in_scroll)
            
            # Staffing pending detection
            if auditor.has_roles_pending_section:
                services_with_pending_roles.add(sid)
                
            # Non-mechanical review items documentation
            non_mechanical = []
            if cid == "staffing" and auditor.has_roles_pending_section:
                non_mechanical.append("人員基準：職種別員数・兼務解釈の制度的確定待ち（未確認を創作せず待機枠維持中）")
            elif cid == "staffing":
                non_mechanical.append("人員基準：職種別員数要件（自治体条例上乗せ基準との照合要）")
            if cid == "remuneration":
                non_mechanical.append("報酬：算定単位数・加算要件（最新告示・通知の施行日・経過措置との照合要）")
            if cid == "national_qa":
                non_mechanical.append("国Q&A：発出時と現行取扱いの適合性（未確認回答の最新性照合要）")
            if not non_mechanical:
                non_mechanical.append("制度解釈・自治体指導方針との最終適合性")
                
            non_mechanical_str = "；".join(non_mechanical)
            
            issue_list = []
            if not h_valid:
                issue_list.append(f"Heading invalid (h1={h1s}, h2={h2s})")
            if not toc_matched:
                issue_list.append("TOC link not found in service index")
            if dup_ids > 0:
                issue_list.append(f"Duplicate IDs: {dup_ids}")
            if broken_anchors > 0:
                issue_list.append(f"Broken in-page anchors: {broken_anchors}")
            if broken_rel_links > 0:
                issue_list.append(f"Broken relative links: {broken_rel_links}")
            if table_overflow_risk:
                issue_list.append(f"Table not wrapped in scroll container: {auditor.table_count} tables")
                
            if issue_list:
                status = "ISSUE_DETECTED"
                issues_count += 1
                all_issues.append({"service": sid, "chapter": cid, "issues": issue_list})
            else:
                status = "MECHANICALLY_PASSED"
                passed_mechanical_count += 1
                
            writer.writerow([
                sid, slabel, cid, cnum, ctitle,
                f"handbook/{sid}/{slug}.html", file_bytes,
                h1s, h2s, h3s, h4s, h5s,
                h_valid, toc_matched, dup_ids,
                broken_rel_links, broken_anchors,
                auditor.table_count, auditor.tables_in_scroll, table_overflow_risk,
                auditor.has_roles_pending_section, auditor.has_working_note,
                auditor.has_checklist, auditor.checkbox_print_count,
                status, " | ".join(issue_list) if issue_list else "None", non_mechanical_str
            ])
            
    csv_file.close()
    
    return {
        "expected_services": expected_services,
        "expected_chapters": expected_chapters,
        "inspected_chapters": inspected_count,
        "missing_files": missing_files_count,
        "mechanically_passed": passed_mechanical_count,
        "issues_detected": issues_count,
        "services_with_pending_roles": sorted(list(services_with_pending_roles)),
        "all_issues": all_issues,
        "csv_path": str(csv_out_path)
    }

if __name__ == "__main__":
    res = run_audit()
    print(json.dumps(res, ensure_ascii=False, indent=2))
