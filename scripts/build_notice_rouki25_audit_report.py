#!/usr/bin/env python3
"""Deterministically replay and report the 22 day-service notice candidates."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT_SHA="02147c9dcfe53c5702e47ddbc08a5326004db116"
AUDIT_DATE="2026-09-23"
OUT_JSON=ROOT/"data/notice-rouki25-independent-audit.json"
OUT_MD=ROOT/"docs/notice-rouki25-independent-audit.md"
FAMILIES={
 "personnel":("data/notice-personnel-source-snapshots.json","data/notice-personnel-current-assembly.json","data/notice-personnel-current-text-candidates.json","data/notice-personnel-source-manifest.json"),
 "equipment":("data/notice-equipment-source-snapshots.json","data/notice-equipment-current-assembly.json","data/notice-equipment-current-text-candidates.json","data/notice-equipment-source-manifest.json"),
 "operation_legacy":("data/notice-operation-legacy-source-snapshots.json","data/notice-operation-legacy-current-assembly.json","data/notice-operation-legacy-current-text-candidates.json","data/notice-operation-legacy-source-manifest.json"),
 "operation_modern":("data/notice-operation-modern-source-snapshots.json","data/notice-operation-modern-current-assembly.json","data/notice-operation-modern-current-text-candidates.json","data/notice-operation-modern-source-manifest.json"),
}
# correct tuple layout is (snapshots, assembly, candidates, manifest)
INFO={
 "mhlw-h27-interpretation-redline":("2015","平成27年度改正後・新旧対照表","改正前|改正後","right"),
 "mhlw-h30-interpretation-redline":("2018","平成30年度改正後・新旧対照表","新|旧","left"),
 "mhlw-2021-interpretation-redline":("2021","令和3年度改正後文を含む新旧対照表","新|旧","left"),
 "mhlw-2024-interpretation-redline":("2024","令和6年度改正後・新旧対照表","新|旧","left"),
 "mhlw-2026-rouki25-reference-redline":("2026-03","令和8年3月の部分的参照資料","新|旧","left"),
}
ROUTES=[
 {"route":"厚労省・令和6年度介護報酬改定ページ","url":"https://www.mhlw.go.jp/stf/newpage_38790.html","finding":"令和6年版の解釈通知PDFへの公式導線。統合現行全文ではない。"},
 {"route":"厚労省・令和6年度改正後PDF","url":"https://www.mhlw.go.jp/content/12300000/001227935.pdf","finding":"対象patchの改正後欄を確認。令和6年改正比較資料。"},
 {"route":"厚労省・令和8年3月部分参照PDF","url":"https://www.mhlw.go.jp/content/12304250/001453049.pdf","finding":"SHA-256は各source snapshotに記録。部分参照としてだけ使用。"},
 {"route":"厚労省・令和8年度介護報酬改定ページ","url":"https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000188411_00073.html","finding":"改定告示等を確認。通所介護22項目の完全な現行解釈通知は確認できず。"},
 {"route":"厚労省・介護保険最新情報掲載ページ群","url":"https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/kaigo_koureisha/index_00010.html","additional_urls":["https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/kaigo_koureisha/index_00029.html","https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/kaigo_koureisha/index_00031.html"],"finding":"令和7・8年資料と通知名を検索。網羅的な対象通知改正履歴ではない。"},
 {"route":"厚労省ドメイン限定の改正通知検索","queries":['site:mhlw.go.jp "指定居宅サービス等及び指定介護予防サービス等に関する基準について" 令和7年','site:mhlw.go.jp "老企第25号" 令和7年 改正 通所介護','site:mhlw.go.jp "老企第25号" 令和8年 通所介護 改正','site:mhlw.go.jp 令和7年 "老企第25号の一部改正"','site:mhlw.go.jp 令和8年 "老企第25号の一部改正"'],"finding":"確認した検索結果に令和6年版より後の対象本文の一部改正通知は見つからず。検索結果の不在は変更不存在の証拠としない。"},
 {"route":"令和8年8月20日付厚労省通知","url":"https://www.mhlw.go.jp/content/12300000/001741381.pdf","finding":"老企第25号第2の3への参照を含むが、第3・六の今回対象改正ではない。"},
]
VISUAL=[
 {"source_id":"mhlw-h27-interpretation-redline","pdf_pages":[45],"purpose":"人員基準・段組みの表示確認"},
 {"source_id":"mhlw-h30-interpretation-redline","pdf_pages":[12],"purpose":"人員改正箇所の表示確認"},
 {"source_id":"mhlw-2021-interpretation-redline","pdf_pages":[32],"purpose":"運営基準改正箇所の表示確認"},
 {"source_id":"mhlw-2024-interpretation-redline","pdf_pages":[20],"purpose":"身体的拘束等の改正欄の表示確認"},
 {"source_id":"mhlw-2026-rouki25-reference-redline","pdf_pages":[22],"purpose":"部分参照資料の表示確認"},
]
RISK={
 "notice.dayservice.personnel.staffing":(10,"高","長文・8項目・計算式・数値・H30/R3改正"),
 "notice.dayservice.operation.policy":(9,"高","R6新③挿入、旧③/④繰下げ、例外・要件・保存期間"),
 "notice.dayservice.operation.bcp":(9,"高","R3新設後R6に経過措置と一体的策定記述を更新"),
 "notice.dayservice.operation.hygiene":(8,"高","R3新設後R6に経過措置文を削除、列挙・複数頁"),
 "notice.dayservice.operation.rules":(8,"高","営業時間の数値、号数更新、参照番号変更"),
 "notice.dayservice.operation.plan":(8,"高","H30/R3の条番号・参照番号更新、頁跨ぎ"),
 "notice.dayservice.equipment.shared-equipment":(7,"中","H30に設備共用を独立項目へ移動・再構成"),
 "notice.dayservice.operation.staffing":(7,"中","R3に③④を追記し複数参照を追加"),
 "notice.dayservice.operation.fees":(6,"中","R3で項目参照番号を変更"),
 "notice.dayservice.equipment.overnight-service":(6,"中","H27新設後H30で項目番号を繰下げ"),
}
def loadj(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
def compact(s): return re.sub(r"\s+","",s or "")
def digest(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()
def src_label(sid): return INFO[sid][1]
def apply_patch(text,p,repl):
 op=p["operation"]
 if op=="replace_between":
  a,b=compact(p["start_anchor"]),compact(p["end_anchor"])
  if text.count(a)!=1: raise ValueError("non-unique start anchor "+p["start_anchor"])
  i=text.index(a); j=text.find(b,i+len(a))
  if j<0: raise ValueError("missing end anchor "+p["end_anchor"])
  old=text[i:j]
  return text[:i]+repl+text[j:],old,repl
 if op=="replace_literal":
  a,b=compact(p["old_text"]),compact(p["new_text"])
  if text.count(a)!=1: raise ValueError("non-unique literal "+p["old_text"])
  return text.replace(a,b,1),a,b
 if op=="insert_before":
  a=compact(p["anchor"])
  if text.count(a)!=1: raise ValueError("non-unique insert anchor "+p["anchor"])
  i=text.index(a); return text[:i]+repl+text[i:],"",repl
 if op=="replace_to_end":
  a=compact(p["start_anchor"])
  if text.count(a)!=1: raise ValueError("non-unique tail anchor "+p["start_anchor"])
  i=text.index(a); return text[:i]+repl,text[i:],repl
 if op=="append": return text+repl,"",repl
 raise ValueError("unknown operation "+op)
def read_inputs():
 packet=loadj("data/notice-review-packet.json")
 chain=loadj("data/notice-source-chain.json")
 review=loadj("data/notice-current-review.json")
 skeleton=loadj("data/notice-current-skeleton.json")
 event_index=loadj("data/notice-amendment-events.json")
 segs={}; sources={}; asm={}; cand={}; manifests={}
 for family,paths in FAMILIES.items():
  snap_path,assembly_path,candidate_path,manifest_path=paths
  snap=loadj(snap_path); assembly=loadj(assembly_path); candidate=loadj(candidate_path); manifest=loadj(manifest_path)
  manifests[family]=manifest
  snap_segments=snap.get("segments",[]); manifest_segments=manifest.get("segments",[])
  if {x["id"] for x in snap_segments}!={x["id"] for x in manifest_segments}: raise ValueError("manifest/snapshot segment IDs differ: "+family)
  manifest_by_id={x["id"]:x for x in manifest_segments}
  for segment in snap_segments:
   m=manifest_by_id[segment["id"]]
   for key in ("notice_id","source_id","page_start","page_end","role"):
    if m.get(key)!=segment.get(key): raise ValueError("manifest/snapshot metadata differs: "+segment["id"]+" "+key)
  for s in snap.get("sources",[]): sources[s["source_id"]]=s
  for s in snap_segments:
   if s["id"] in segs: raise ValueError("duplicate snapshot "+s["id"])
   segs[s["id"]]=s
  for i in assembly["items"]: asm[i["notice_id"]]=i
  for i in candidate["items"]: cand[i["notice_id"]]=i
 return packet,chain,review,skeleton,event_index,segs,sources,asm,cand,manifests
def build():
 packet,chain,review,skeleton,event_index,segs,sources,asm,cand,manifests=read_inputs()
 chain_by={x["source_id"]:x for x in chain}
 for sid,meta in chain_by.items():
  if sid in INFO and meta.get("issued_period")!=INFO[sid][0]: raise ValueError("source-chain period conflict: "+sid)
 pitems=packet["items"]
 if len(pitems)!=22 or len({i["notice_id"] for i in pitems})!=22: raise ValueError("packet must contain 22 unique items")
 if set(asm)!=set(cand)==set(i["notice_id"] for i in pitems): raise ValueError("packet/assembly/candidate IDs differ")
 skeleton_ids={x.get("id") for x in skeleton}
 if not set(asm).issubset(skeleton_ids): raise ValueError("some packet IDs are missing from current skeleton")
 if review.get("review_status")!="NOT_STARTED" or review.get("reviewed_nodes"): raise ValueError("current review state is not the untouched state recorded for this audit")
 out=[]
 for item in pitems:
  nid=item["notice_id"]; ai=asm[nid]; ci=cand[nid]
  raw=ci["candidate_text"]
  ch=digest(raw)
  if ch!=item["candidate_text_sha256"] or raw!=item["candidate_text"]: raise ValueError("candidate hash/text mismatch "+nid)
  if ci.get("human_verification_status")!="NOT_REVIEWED": raise ValueError("candidate human status changed "+nid)
  base=segs[ai["baseline_snapshot_id"]]
  if base["notice_id"]!=nid: raise ValueError("baseline notice mismatch "+nid)
  value=compact(base["body_text"]); baseline=value
  trace=[]
  for n,p in enumerate(ai.get("patches",[])):
   seg=segs[p["snapshot_id"]]
   if seg["notice_id"]!=nid: raise ValueError("patch notice mismatch "+nid)
   before=value; repl=compact(seg.get("body_text",""))
   value,old,new=apply_patch(value,p,repl)
   sid=seg["source_id"]; source=sources[sid]; period=INFO[sid][0]
   trace.append({
    "step":n+1,"source_id":sid,"issued_period":period,"source_label":src_label(sid),
    "source_url":source["url"],"source_pdf_sha256":source["sha256"],"source_sha256_provenance":"repository source snapshot/manifest; this audit did not freshly re-download and rehash the PDF",
    "pdf_pages":[seg["page_start"],seg["page_end"]],
    "current_column":seg.get("current_column",INFO[sid][3]),"column_headers":INFO[sid][2],
    "operation":p["operation"],"old_text":old,"new_text":new,"note":p.get("note",""),
    "source_snapshot_id":seg["id"],"snapshot_body_sha256":seg.get("body_text_sha256"),
   })
  # Baseline is explicit, and chronological order is visible before all patches.
  bsid=base["source_id"]; bsource=sources[bsid]
  full_trace=[{
   "step":0,"source_id":bsid,"issued_period":INFO[bsid][0],"source_label":src_label(bsid),
   "source_url":bsource["url"],"source_pdf_sha256":bsource["sha256"],"source_sha256_provenance":"repository source snapshot/manifest; this audit did not freshly re-download and rehash the PDF",
   "pdf_pages":[base["page_start"],base["page_end"]],
   "current_column":base.get("current_column",INFO[bsid][3]),"column_headers":INFO[bsid][2],
   "operation":"baseline","old_text":"","new_text":baseline,"note":base.get("note",""),
   "source_snapshot_id":base["id"],"snapshot_body_sha256":base.get("body_text_sha256"),
  }]+trace
  expected_replay=[(ai["baseline_snapshot_id"],"baseline")]+[(p["snapshot_id"],p["operation"]) for p in ai.get("patches",[])]
  packet_replay=[(r["snapshot_id"],r["operation"]) for r in item.get("replay_order",[])]
  if expected_replay!=packet_replay: raise ValueError("packet replay order differs from assembly "+nid)
  candidate=compact(raw); exact=(value==candidate)
  risk=RISK.get(nid,(4,"中","個別確認が必要"))
  coverage=("full_text_in_2026_partial_reference" if nid.endswith(".incorporation") else
            "fragment_in_2026_partial_reference" if nid.endswith((".policy",".bcp",".hygiene")) else
            "not_full_target_text_in_2026_partial_reference")
  applied_source_ids={x["source_id"] for x in full_trace}
  events=[]
  for event in (event_index if isinstance(event_index,list) else event_index.get("events",[])):
   related=(event.get("target_node_id")==nid or event.get("related_target_node_id")==nid or (event.get("target_node_id")=="notice.dayservice.operation" and item["family"].startswith("operation")))
   if not related: continue
   sid=event.get("source_id"); src_event=sources.get(sid,{})
   locator=next((x for x in full_trace if x["source_id"]==sid),None)
   events.append({
    "event_id":event.get("id"),"effective_from":event.get("effective_from"),"source_id":sid,
    "source_url":src_event.get("url"),"source_pdf_sha256":src_event.get("sha256"),
    "pdf_pages":locator.get("pdf_pages") if locator else None,
    "target_node_id":event.get("target_node_id"),"operation":event.get("operation"),
    "summary":event.get("summary"),"event_ledger_status":event.get("verification_status"),
    "crosscheck_status":"source_in_forward_replay" if sid in applied_source_ids else "locator_only_not_independently_closed",
   })
  later_sources=[]
  ordered_sources=sorted(INFO,key=lambda x:INFO[x][0])
  baseline_order=ordered_sources.index(bsid)
  for sid in ordered_sources[baseline_order+1:]:
   if sid not in sources: continue
   source=sources[sid]; applied=next((x for x in full_trace if x["source_id"]==sid),None)
   evidence=next((x for x in item.get("source_evidence",[]) if x.get("source_url")==source["url"]),None)
   later_sources.append({
    "source_id":sid,"issued_period":INFO[sid][0],"source_label":src_label(sid),
    "source_url":source["url"],"source_pdf_sha256":source["sha256"],
    "pdf_pages":applied.get("pdf_pages") if applied else ([evidence.get("page_start"),evidence.get("page_end")] if evidence else None),
    "review_result":"PATCH_REPLAYED" if applied else ("PARTIAL_REFERENCE_ONLY" if sid=="mhlw-2026-rouki25-reference-redline" else "NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE"),
    "note":"非適用または対象本文の未収録を不改正の証拠にはしていない。完全な改正網羅性は未確認。",
   })
  src=sources[bsid]
  previous=next((pitems[j-1]["notice_id"] for j,x in enumerate(pitems) if x["notice_id"]==nid and j>0 and pitems[j-1]["family"]==item["family"]),None)
  following=next((pitems[j+1]["notice_id"] for j,x in enumerate(pitems) if x["notice_id"]==nid and j+1<len(pitems) and pitems[j+1]["family"]==item["family"]),None)
  delta=None
  if not exact:
   k=next((k for k,(a,b) in enumerate(zip(value,candidate)) if a!=b),min(len(value),len(candidate)))
   delta={"first_difference_offset":k,"candidate_excerpt":candidate[max(0,k-80):k+160],"independent_reconstruction_excerpt":value[max(0,k-80):k+160],"candidate_length":len(candidate),"reconstruction_length":len(value)}
  out.append({
   "notice_id":nid,"title":item["title"],"section":item["section"],"number_path":item["number_path"],"family":item["family"],
   "decision":"HOLD" if exact else "MISMATCH","candidate_sha256":ch,"candidate_effective_as_of_metadata":item.get("effective_as_of"),
   "baseline":{
    "snapshot_id":base["id"],"source_id":bsid,"source_title":"指定居宅サービス等及び指定介護予防サービス等に関する基準について",
    "source_label":src_label(bsid),"source_url":src["url"],"pdf_sha256":src["sha256"],
    "pdf_pages":[base["page_start"],base["page_end"]],"current_column":base.get("current_column",INFO[bsid][3]),
    "column_headers":INFO[bsid][2],"selection_note":base.get("note",""),"snapshot_body_sha256":base.get("body_text_sha256"),
    "text_sha256_after_whitespace_removal":digest(baseline),"text_start_boundary":baseline[:180],"text_end_boundary":baseline[-180:],
    "previous_packet_item":previous,"following_packet_item":following,"baseline_text_after_whitespace_removal":baseline,
   },
   "amendment_chain":full_trace,
   "amendment_event_ledger_crosscheck":events,
   "later_official_redline_inventory":later_sources,
   "independently_reconstructed_text_sha256":digest(value),
   "reconstructed_text_hash_normalization":"UTF-8 SHA-256 after Unicode whitespace removal only; punctuation, digits, symbols, and numeral glyphs are retained.",
   "independently_reconstructed_text":value,
   "candidate_comparison":{
    "result":"EXACT_AFTER_WHITESPACE_REMOVAL" if exact else "MISMATCH",
    "comparison_normalization":"Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.",
    "candidate_semantic_sha256_after_whitespace_removal":digest(candidate),
    "candidate_text_if_mismatch":raw if not exact else None,
    "independent_semantic_sha256_after_whitespace_removal":digest(value),"difference":delta,
   },
   "currentness":{
    "status":"UNRESOLVED_EXHAUSTIVE_COVERAGE","latest_applied_or_baseline_source_period":full_trace[-1]["issued_period"],
    "latest_official_partial_reference_period":"2026-03","2026_partial_reference_coverage":coverage,
    "later_amendment_search":"公式MHLW通知・改定ページ、アーカイブ索引、通知名・老企第25号の検索を2026-09-23まで実施。後続の対象通知改正は見つからなかったが、検索結果の不在を変更不存在の証拠としない。",
    "hold_reason":"2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。2026年3月資料は部分参照のみ。",
    "routes":ROUTES,
   },
   "decision_reason":"候補と順方向replayは一致したが、後続改正の網羅性と完全な現行一次資料を確認できないためHOLD。",
   "residual_risks":["後続改正の網羅性を一次資料で確証できていない。","2026年3月資料は部分参照であり、対象の現在性を単独で保証しない。","PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。"],
   "reviewer_should_check":[
    "後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。",
    f"baseline PDF p.{base['page_start']}-{base['page_end']}を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。",
    "各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。",
   ],
   "risk":{"score":risk[0],"level":risk[1],"reason":risk[2]},
   "reviewer_checklist":["一次資料本文を照合","baseline欄と項目境界をPDF表示で確認","旧文・新文と適用順を確認","後続改正を網羅する公式経路を確認","candidate hashと監査record hashを照合"],
  })
 rec=packet.get("independent_verification_record",{})
 counts={k:sum(1 for i in out if i["decision"]==k) for k in ("AUDIT_PASS","AUDIT_PASS_WITH_LIMITATION","HOLD","MISMATCH")}
 matches=sum(i["candidate_comparison"]["result"]=="EXACT_AFTER_WHITESPACE_REMOVAL" for i in out)
 return {
  "format_version":1,"audit_id":"rouki25-dayservice-independent-audit-2026-09","audit_date":AUDIT_DATE,"audited_main_sha":AUDIT_SHA,
  "scope":"老企第25号「指定居宅サービス等及び指定介護予防サービス等に関する基準について」第3・六（通所介護）、notice-review-packet.jsonの22項目",
  "audit_kind":"独立機械監査。人による確認ではない。",
  "human_verification_state":{"notice_current_review_status":review.get("review_status"),"reviewed_nodes":review.get("reviewed_nodes",[]),"packet_skeleton_covered_item_count":sum(1 for nid in asm if nid in skeleton_ids),"changed_by_this_audit":False,"automatic_promotion":False},
  "summary":{
   "counts":counts,"candidate_text_replay_match_count":matches,"candidate_text_mismatch_count":22-matches,"currentness_unresolved_count":22,
   "highest_risk_items":[{"notice_id":x["notice_id"],"title":x["title"],**x["risk"]} for x in sorted(out,key=lambda a:(-a["risk"]["score"],a["notice_id"]))[:5]],
   "common_findings":[
    {"category":"currentness/source coverage","finding":"令和6年版以後の対象項目を網羅する現行統合本文・公式な全改正履歴を確認できない。令和8年3月資料は部分参照。","impact":"22項目をHOLDとし、歴史資料からの一致を現行性の証明にしない。"},
    {"category":"stale verification provenance","finding":f"既存PASS記録はSHA {rec.get('verified_main_sha')}。fresh read main SHA {AUDIT_SHA}とは異なる。","impact":"既存PASSを今回の結論に使用していない。"},
    {"category":"unsupported current-as-of metadata","finding":"packetのeffective_as_of=2026-09-23は再構成日を示すメタデータであり、この監査で現行性を裏付ける資料ではない。","impact":"現在性の証拠が足りない項目はHOLD。"},
    {"category":"visual/extraction coverage","finding":"別抽出テキストとMHLW PDF表示を代表的な改正箇所で確認したが、全22項目・全ページを人が目視した監査ではない。","impact":"OCR、左右段組み、頁跨ぎ、脚注の残存リスクを個別記録。"},
   ],
   "unresolved":["令和6年版以降の対象項目を網羅する現行統合通知または完全な公式改正履歴","全22項目に係る左右欄・頁跨ぎ・脚注・項目境界の人によるPDF確認","検索結果外の別タイトル・未索引の後続改正が存在しないことの一次資料による確認"],
   "human_review_requests":["高リスクの従業者の員数、基本取扱方針、業務継続計画、衛生管理、運営規程、計画作成を優先確認。","現行統合通知または令和6年以降を網羅する公式改正履歴を確認し、全22項目の現在性を判定。","人のレビューなしにHUMAN_VERIFIED / VERIFIED_CURRENTへ昇格しない。"],
  },
  "reproducibility":{
   "command":"python3 scripts/build_notice_rouki25_audit_report.py --check && python3 scripts/validate_notice_rouki25_audit.py && npm run validate:data",
   "method":["candidate本文を見ずにsource snapshotの公式PDF由来body_textから再構成を開始。","assemblyのpatch定義を別のPython replay関数で順方向に適用し、anchorの一意性を検証。","基準年から後続改正年へ順方向適用。2026年3月PDFは部分参照のみとして扱う。","候補比較はUnicode whitespaceのみ除去。数字・句読点・括弧・条番号・列挙記号は保持。","本文差があればMISMATCH。本文一致でも現行性網羅が未確認ならHOLD。PASSへは自動昇格しない。"],
   "input_files":["data/notice-review-packet.json","data/notice-current-review.json","data/notice-current-skeleton.json","data/notice-source-chain.json","data/notice-amendment-events.json"]+[p for paths in FAMILIES.values() for p in paths],
   "source_sha256_values":{k:v.get("sha256") for k,v in sorted(sources.items())},
   "method_limits":["PDF SHA-256はsource snapshot/source manifestの記録値であり、この監査でPDFの再ダウンロード・再hashはしていない。","builderはsource snapshot body_textを読み、PDFの再ダウンロード・再抽出はしない。","既存bbox座標抽出verifierは異なる方式だが、そのPASS記録は旧main SHAであり今回の結論に使用しない。","本監査で表示確認したPDFは代表的な5ページ。全ページの人による目視確認ではない。"],
   "visual_pdf_sample":VISUAL,"official_currentness_routes":ROUTES,"amendment_event_locator_count":len(event_index) if isinstance(event_index,list) else len(event_index.get("events",[])),"amendment_event_index_role":"locator only; source PDFs control text","hash_algorithm":"SHA-256 UTF-8",
  },
  "items":out,
 }
def markdown(r):
 c=r["summary"]["counts"]; lines=[
 "# 老企第25号 通所介護22項目・独立機械監査","",
 f"- 監査日: {r['audit_date']}",f"- fresh read main SHA: {r['audited_main_sha']}",
 "- 機械監査のみ。HUMAN_VERIFIED / VERIFIED_CURRENTではない。","",
 "## 判定集計","",
 "| 判定 | 件数 |","|---|---:|",f"| AUDIT_PASS | {c['AUDIT_PASS']} |",f"| AUDIT_PASS_WITH_LIMITATION | {c['AUDIT_PASS_WITH_LIMITATION']} |",f"| HOLD | {c['HOLD']} |",f"| MISMATCH | {c['MISMATCH']} |","",
 f"snapshotからの順方向replayでは {r['summary']['candidate_text_replay_match_count']}/22 件が、空白除去後に候補と一致。後続改正の網羅性を確認できないため全件HOLD。候補一致は現行性の証明ではない。","",
 "## 高リスク項目","",
 ]
 for x in r["summary"]["highest_risk_items"]: lines.append(f"- {x['title']} ({x['notice_id']}, risk {x['score']}/10): {x['reason']}")
 lines += ["","## 共通所見",""]
 for x in r["summary"]["common_findings"]: lines.append(f"- {x['category']}: {x['finding']} {x['impact']}")
 lines += ["","## 22項目一覧","","| notice_id | 項目 | candidate SHA-256 | 判定 | replay | baseline → amendments |","|---|---|---|---|---|---|"]
 for x in r["items"]:
  chain=" → ".join([x["baseline"]["source_label"]]+[a["source_label"] for a in x["amendment_chain"][1:]])
  lines.append(f"| {x['notice_id']} | {x['title']} | {x['candidate_sha256'][:12]}… | {x['decision']} | {x['candidate_comparison']['result']} | {chain} |")
 for x in r["items"]:
  b=x["baseline"]; pages=b["pdf_pages"]
  lines += ["",f"## {x['notice_id']} — {x['title']}","",
   f"- number_path: {' / '.join(x['number_path'])}",f"- candidate SHA-256: {x['candidate_sha256']}",
   f"- 判定: {x['decision']}",f"- independent replay SHA-256: {x['independently_reconstructed_text_sha256']}",
   f"- candidate comparison: {x['candidate_comparison']['result']} ({x['candidate_comparison']['comparison_normalization']})",
   f"- baseline: {b['source_label']}、{b['source_url']}、PDF SHA-256 {b['pdf_sha256']}、p.{pages[0]}–{pages[1]}、{b['current_column']}欄（{b['column_headers']}）",
   f"- baseline開始: {b['text_start_boundary'][:100]}…",
   f"- baseline終了: …{b['text_end_boundary'][-100:]}",
   "- 改正順:"]
  for a in x["amendment_chain"]:
   lines.append(f"  - {a['issued_period']} {a['source_label']} p.{a['pdf_pages'][0]}–{a['pdf_pages'][1]} {a['operation']}: {a['note'] or a['source_snapshot_id']} (PDF SHA-256 {a['source_pdf_sha256']})")
  if x.get("amendment_event_ledger_crosscheck"):
   lines.append("- amendment-event索引との照合（索引はlocator扱い）:")
   for e in x["amendment_event_ledger_crosscheck"]:
    lines.append(f"  - {e['effective_from']} {e['operation']}: {e['summary']} [{e['crosscheck_status']}]")
  if x.get("later_official_redline_inventory"):
   lines.append("- baseline後の公式赤線資料（未適用は不改正の証明にしない）:")
   for z in x["later_official_redline_inventory"]:
    lines.append(f"  - {z['issued_period']} {z['source_label']} p.{z['pdf_pages']}: {z['review_result']}")
  lines += [f"- 2026年3月部分参照: {x['currentness']['2026_partial_reference_coverage']}",
   f"- currentness: 未解決。{x['currentness']['hold_reason']}",
   f"- 残存リスク: {' '.join(x['residual_risks'])}",
   f"- reviewer確認点: {' '.join(x['reviewer_should_check'])}",
   "- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。"]
 lines += ["","## 調査経路と再現","",
  "一次資料は厚生労働省公開PDF。各項目のPDF URL、SHA-256、ページ、改正後列、baseline本文とpatchの旧文／新文をmachine JSONに記録した。2026年3月PDFは部分参照としてのみ使用。",
  "",
  "既存independent verifierのPASS記録（main SHAは古い）を今回の結論には使用していない。追加replayはsource snapshot本文から開始した。ただし本builder自体はPDFの再ダウンロード・再抽出を行わず、全22項目の全ページ目視でもない。",
  "",
  "厚労省の令和6年改正ページ、令和8年改定ページ、介護保険最新情報索引、通知名と老企第25号の令和7・8年検索を確認した。後続改正が検索結果に見つからないことは不改正の証拠とせず、網羅的な改正履歴が確認できないため全件HOLDとした。",
  "",
  "再実行コマンド:", "",
  "    "+r["reproducibility"]["command"],"",
  "human review状態は変更していない。Machine report: data/notice-rouki25-independent-audit.json",""]
 return "\n".join(lines)
def main():
 p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); a=p.parse_args()
 r=build(); jt=json.dumps(r,ensure_ascii=False,indent=2)+"\n"; mt=markdown(r)
 if a.check:
  bad=[]
  if not OUT_JSON.exists() or OUT_JSON.read_text(encoding="utf-8")!=jt: bad.append(str(OUT_JSON))
  if not OUT_MD.exists() or OUT_MD.read_text(encoding="utf-8")!=mt: bad.append(str(OUT_MD))
  if bad: raise SystemExit("Audit outputs are stale or missing: "+", ".join(bad))
  print("notice rouki25 audit report: OK"); return
 OUT_JSON.parent.mkdir(parents=True,exist_ok=True); OUT_MD.parent.mkdir(parents=True,exist_ok=True)
 OUT_JSON.write_text(jt,encoding="utf-8"); OUT_MD.write_text(mt,encoding="utf-8")
 print("Wrote "+str(OUT_JSON)+" and "+str(OUT_MD))
if __name__=="__main__": main()
