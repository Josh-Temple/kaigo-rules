#!/usr/bin/env python3
"""Fail-closed validation for the independent 老企第25号 audit record."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
import build_notice_rouki25_audit_report as builder

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"data/notice-rouki25-independent-audit.json"
PACKET=ROOT/"data/notice-review-packet.json"
REVIEW=ROOT/"data/notice-current-review.json"
VALID={"AUDIT_PASS","AUDIT_PASS_WITH_LIMITATION","HOLD","MISMATCH"}
def digest(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()
def fail(message): raise SystemExit("notice rouki25 audit validation failed: "+message)
def main():
 if not REPORT.exists(): fail("machine audit report is missing")
 try: report=json.loads(REPORT.read_text(encoding="utf-8"))
 except Exception as exc: fail("invalid JSON: "+str(exc))
 packet=json.loads(PACKET.read_text(encoding="utf-8"))
 review=json.loads(REVIEW.read_text(encoding="utf-8"))
 rows=report.get("items",[])
 if len(rows)!=22 or len({x.get("notice_id") for x in rows})!=22: fail("expected 22 unique item records")
 source_items={x["notice_id"]:x for x in packet.get("items",[])}
 if set(source_items)!={x["notice_id"] for x in rows}: fail("item set differs from packet")
 counts={key:0 for key in VALID}
 for row in rows:
  nid=row["notice_id"]; decision=row.get("decision")
  if decision not in VALID: fail(nid+": invalid decision")
  counts[decision]+=1
  candidate=source_items[nid]
  if row.get("candidate_sha256")!=candidate.get("candidate_text_sha256"): fail(nid+": candidate hash is stale")
  if digest(candidate.get("candidate_text",""))!=candidate.get("candidate_text_sha256"): fail(nid+": candidate SHA-256 does not verify")
  if len(row.get("candidate_sha256",""))!=64 or not re.fullmatch(r"[0-9a-f]{64}",row["candidate_sha256"]): fail(nid+": malformed candidate SHA-256")
  if row.get("number_path")!=candidate.get("number_path"): fail(nid+": number_path differs")
  baseline=row.get("baseline",{})
  if not baseline.get("source_url","").startswith("https://www.mhlw.go.jp/"): fail(nid+": baseline is not a direct MHLW source")
  if not re.fullmatch(r"[0-9a-f]{64}",baseline.get("pdf_sha256","")): fail(nid+": missing baseline PDF SHA-256")
  if not baseline.get("pdf_pages") or not baseline.get("text_start_boundary") or not baseline.get("text_end_boundary"): fail(nid+": baseline locator/boundary evidence missing")
  if digest(row.get("independently_reconstructed_text",""))!=row.get("independently_reconstructed_text_sha256"): fail(nid+": reconstruction SHA-256 does not verify")
  comparison=row.get("candidate_comparison",{})
  if comparison.get("result")=="EXACT_AFTER_WHITESPACE_REMOVAL":
   if comparison.get("candidate_semantic_sha256_after_whitespace_removal")!=comparison.get("independent_semantic_sha256_after_whitespace_removal"): fail(nid+": semantic hashes differ despite exact result")
   if comparison.get("independent_semantic_sha256_after_whitespace_removal")!=row.get("independently_reconstructed_text_sha256"): fail(nid+": reconstruction hashes differ")
   if row.get("currentness",{}).get("status")=="UNRESOLVED_EXHAUSTIVE_COVERAGE" and decision!="HOLD": fail(nid+": unresolved later-amendment coverage must be HOLD")
  elif comparison.get("result")=="MISMATCH":
   if decision!="MISMATCH" or not comparison.get("difference") or comparison.get("candidate_text_if_mismatch") is None: fail(nid+": mismatch evidence incomplete")
  else: fail(nid+": invalid candidate comparison state")
  chain=row.get("amendment_chain",[])
  if not chain or chain[0].get("operation")!="baseline": fail(nid+": baseline missing from amendment chain")
  last=""
  for expected_step,entry in enumerate(chain):
   if entry.get("step")!=expected_step: fail(nid+": amendment replay steps are not ordered")
   period=entry.get("issued_period","")
   if last and period<last: fail(nid+": amendment chain runs backwards")
   last=period
   if not re.fullmatch(r"[0-9a-f]{64}",entry.get("source_pdf_sha256","")): fail(nid+": amendment PDF SHA-256 missing")
   if not entry.get("source_url","").startswith("https://www.mhlw.go.jp/"): fail(nid+": amendment source is not MHLW")
  if not row.get("currentness",{}).get("routes") or not row.get("residual_risks"): fail(nid+": currentness routes or residual risks missing")
  if not row.get("reviewer_should_check"): fail(nid+": reviewer follow-up missing")
 if counts!=report.get("summary",{}).get("counts"): fail("summary counts differ from item decisions")
 if sum(counts.values())!=22: fail("summary does not cover all items")
 # Human review is a separate state and must not be promoted by this machine audit.
 if review.get("review_status")!="NOT_STARTED" or review.get("reviewed_nodes"): fail("human review state changed")
 if report.get("human_verification_state",{}).get("changed_by_this_audit") is not False: fail("audit claims a human-review mutation")
 if report.get("human_verification_state",{}).get("automatic_promotion") is not False: fail("automatic promotion flag must remain false")
 if report.get("human_verification_state",{}).get("notice_current_review_status")!="NOT_STARTED": fail("audit did not preserve recorded review state")
 # Rebuild in memory and require deterministic, committed JSON and Markdown.
 expected_json=json.dumps(builder.build(),ensure_ascii=False,indent=2)+"\n"
 expected_md=builder.markdown(builder.build())
 if REPORT.read_text(encoding="utf-8")!=expected_json: fail("machine report differs from deterministic replay")
 if not builder.OUT_MD.exists() or builder.OUT_MD.read_text(encoding="utf-8")!=expected_md: fail("Markdown report differs from deterministic output")
 print("notice rouki25 independent audit: OK (22 items; human review state unchanged)")
if __name__=="__main__": main()
