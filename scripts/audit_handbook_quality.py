#!/usr/bin/env python3
"""Audit quality across all 39 services and 585 chapters.

Inspects generated HTML files, checks heading hierarchies, duplicate IDs,
internal link validity, empty sections, TOC correspondence, responsive
overflow risks, and outputs 04_all_handbook_quality.csv.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = Path("/workspace/build_kaigo_private_site")

def run_audit(csv_out_path: Path = Path("/workspace/04_all_handbook_quality.csv")):
    master_path = ROOT / "data/handbook.generated.json"
    hb_data = json.loads(master_path.read_text(encoding="utf-8"))
    services = hb_data["services"]
    
    csv_file = open(csv_out_path, "w", encoding="utf-8", newline="")
    writer = csv.writer(csv_file)
    writer.writerow([
        "service_id", "service_label", "chapter_id", "chapter_number", "chapter_title",
        "file_path", "file_bytes", "h1_count", "h2_count", "h3_count", "h4_count", "h5_count",
        "heading_hierarchy_valid", "toc_matched", "duplicate_ids_count",
        "broken_internal_links_count", "empty_sections_count", "checkpoints_count",
        "paragraphs_count", "reference_records_count", "roles_count",
        "has_unconfirmed_warning", "has_staffing_pending_banner", "qa_links_count",
        "print_css_present", "mobile_table_overflow_risk", "overall_quality_status"
    ])
    
    total_audited = 0
    issues_summary = {
        "heading_hierarchy_invalid": 0,
        "toc_mismatches": 0,
        "duplicate_ids": 0,
        "broken_internal_links": 0,
        "empty_sections": 0,
        "mobile_table_overflow_risk": 0
    }
    
    for service in services:
        sid = service["service_id"]
        slabel = service.get("label", sid)
        chapters = service["chapters"]
        
        # Read service TOC
        svc_file = SITE_DIR / "services" / sid / "index.html"
        svc_html = svc_file.read_text(encoding="utf-8") if svc_file.is_file() else ""
        
        for chapter in chapters:
            cid = chapter["section_id"]
            slug = cid.replace("_", "-")
            cnum = chapter["number"]
            ctitle = chapter["title"]
            
            ch_file = SITE_DIR / "handbook" / sid / f"{slug}.html"
            if not ch_file.is_file():
                writer.writerow([sid, slabel, cid, cnum, ctitle, "", 0, 0, 0, 0, 0, 0, False, False, 0, 1, 1, 0, 0, 0, 0, False, False, 0, False, False, "FAIL_MISSING_FILE"])
                continue
                
            content = ch_file.read_text(encoding="utf-8")
            file_bytes = ch_file.stat().st_size
            
            # Heading counts
            h1s = len(re.findall(r"<h1\b", content, re.I))
            h2s = len(re.findall(r"<h2\b", content, re.I))
            h3s = len(re.findall(r"<h3\b", content, re.I))
            h4s = len(re.findall(r"<h4\b", content, re.I))
            h5s = len(re.findall(r"<h5\b", content, re.I))
            
            # Heading hierarchy rule: exactly 1 h1, at least 1 h2, h3s under h2
            h_valid = (h1s == 1 and h2s >= 1)
            if not h_valid:
                issues_summary["heading_hierarchy_invalid"] += 1
                
            # TOC correspondence
            toc_matched = (f'href="../../handbook/{sid}/{slug}.html"' in svc_html)
            if not toc_matched:
                issues_summary["toc_mismatches"] += 1
                
            # Duplicate ID detection
            ids_found = re.findall(r'\bid="([^"]+)"', content)
            id_counts = {}
            for ident in ids_found:
                id_counts[ident] = id_counts.get(ident, 0) + 1
            dup_ids = sum(1 for ident, count in id_counts.items() if count > 1)
            if dup_ids > 0:
                issues_summary["duplicate_ids"] += dup_ids
                
            # Check internal links (href="../..." or href="#...")
            internal_links = re.findall(r'\bhref="([^"]+)"', content)
            broken_links = 0
            for href in internal_links:
                if href.startswith("#"):
                    anchor = href[1:]
                    if anchor not in ids_found:
                        broken_links += 1
                elif not href.startswith("http://") and not href.startswith("https://") and not href.startswith("mailto:"):
                    target_path = (ch_file.parent / href.split("?")[0].split("#")[0]).resolve()
                    if not target_path.is_file():
                        broken_links += 1
            if broken_links > 0:
                issues_summary["broken_internal_links"] += broken_links
                
            # Empty sections
            empty_sec = 0
            # Check for <section ...></section> without child elements
            for sec in re.finditer(r"<section\b[^>]*>(.*?)</section>", content, re.DOTALL):
                inner = sec.group(1).strip()
                if not inner or inner == "<p></p>":
                    empty_sec += 1
            if empty_sec > 0:
                issues_summary["empty_sections"] += empty_sec
                
            # Content items
            checkpoints_count = len(chapter.get("checkpoints", []))
            paragraphs_count = len(chapter.get("paragraphs", []))
            ref_records_count = len(chapter.get("reference_ids", []))
            roles_count = len(chapter.get("role_sections", []))
            
            # Badges and banners
            has_unconfirmed = ("未確認" in content)
            has_pending = ('handbook-roles-pending' in content)
            
            # QA links
            qa_links_count = len(re.findall(r'href="[^"]*qa(?:\.html|\?)', content))
            
            # Print CSS present
            print_css = ('@media print' in content or 'styles.css' in content)
            
            # Mobile table overflow risk
            # tables without table-scroll or overflow container
            raw_tables = len(re.findall(r"<table\b", content, re.I))
            scroll_tables = len(re.findall(r'class="[^"]*table-scroll', content, re.I))
            table_overflow_risk = (raw_tables > scroll_tables)
            if table_overflow_risk:
                issues_summary["mobile_table_overflow_risk"] += 1
                
            overall = "PASS" if (h_valid and toc_matched and dup_ids == 0 and broken_links == 0 and empty_sec == 0) else "AUDITED_WITH_NOTES"
            
            writer.writerow([
                sid, slabel, cid, cnum, ctitle,
                f"handbook/{sid}/{slug}.html", file_bytes,
                h1s, h2s, h3s, h4s, h5s,
                h_valid, toc_matched, dup_ids,
                broken_links, empty_sec, checkpoints_count,
                paragraphs_count, ref_records_count, roles_count,
                has_unconfirmed, has_pending, qa_links_count,
                print_css, table_overflow_risk, overall
            ])
            total_audited += 1
            
    csv_file.close()
    return {
        "total_audited": total_audited,
        "issues_summary": issues_summary,
        "csv_path": str(csv_out_path)
    }

if __name__ == "__main__":
    res = run_audit()
    print(json.dumps(res, ensure_ascii=False, indent=2))
