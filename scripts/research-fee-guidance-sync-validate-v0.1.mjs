import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const readJson = (p) => JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));

const meta=readJson("data/fee-guidance-current-meta.json");
const assembly=readJson("data/fee-guidance-current-assembly.json");
const candidates=readJson("data/fee-guidance-current-text-candidates.json");
const replay=readJson("data/fee-guidance-replay-coverage.json");
const manifest=readJson("data/fee-guidance-source-manifest.json");
const supplements=readJson("data/fee-guidance-verified-text-supplements.json");

const errors=[];
const expectedIds=[
 "fee-guidance.dayservice.4",
 "fee-guidance.dayservice.5",
 "fee-guidance.dayservice.6",
 "fee-guidance.dayservice.7",
 "fee-guidance.dayservice.7-2",
 "fee-guidance.dayservice.18",
 "fee-guidance.dayservice.24",
 "fee-guidance.dayservice.25",
];
const sameSet=(a,b)=>{
 const aa=[...new Set(a)].sort(), bb=[...new Set(b)].sort();
 return aa.length===bb.length && aa.every((x,i)=>x===bb[i]);
};

if(meta.current_state!=="MACHINE_CURRENT_TEXT_CANDIDATES_BUILT_HUMAN_CHECK_PENDING") {
 errors.push("unexpected current_state");
}
if(meta.counts?.total!==29 || meta.counts?.KNOWN_AFTER_TEXT!==22 || meta.counts?.INHERITED_UNVERIFIED!==7 || meta.counts?.UNKNOWN!==0){
 errors.push("unexpected fee-guidance meta counts");
}
const assemblyIds=(assembly.items??[]).map(x=>x.guidance_id);
const candidateIds=(candidates.items??[]).map(x=>x.guidance_id);
const replayIds=(replay??[]).map(x=>x.guidance_id);
if(!sameSet(assemblyIds,expectedIds)) errors.push("assembly IDs mismatch");
if(!sameSet(candidateIds,expectedIds)) errors.push("candidate IDs mismatch");
if(!sameSet(replayIds,expectedIds)) errors.push("replay IDs mismatch");

for(const item of candidates.items??[]){
 if(item.human_verification_status!=="NOT_REVIEWED") errors.push("unexpected candidate review status: "+item.guidance_id);
 if(!item.candidate_text_sha256 || !item.candidate_text) errors.push("missing candidate text/hash: "+item.guidance_id);
}
const replayReviewAllowed=new Set(["HUMAN_REVIEW_COMPLETE"]);
for(const item of replay??[]){
 if(!String(item.replay_status||"").startsWith("CHECKPOINT_CHAIN_COMPLETE")) errors.push("incomplete replay: "+item.guidance_id);
 if(!replayReviewAllowed.has(item.human_verification_status)) errors.push("fee-guidance replay is not human reviewed: "+item.guidance_id);
}

const byId=new Map((candidates.items??[]).map(x=>[x.guidance_id,x]));
const compact=(v)=>String(v||"").normalize("NFKC").replace(/\s+/g,"");
const scale=compact(byId.get("fee-guidance.dayservice.6")?.candidate_text);
if(!scale.includes(compact("⑤ 感染症又は災害の発生を理由とする利用者数の減少が一定以上生じている場合の事業所規模別の報酬区分の決定に係る特例については、別途通知を参照すること。"))) {
 errors.push("item 6 verified paragraph ⑤ missing");
}
const disaster=compact(byId.get("fee-guidance.dayservice.7")?.candidate_text);
if(disaster.includes(compact("災害時等の取扱い、災害その他"))) errors.push("item 7 spurious comma");
if(!disaster.includes(compact("場合は翌月も含む。）の翌月から所定単位数の減算を行う"))) errors.push("item 7 closing parenthesis missing");
const capacity=compact(byId.get("fee-guidance.dayservice.24")?.candidate_text);
if(!capacity.includes(compact("第27号。以下「通所介護費等の算定方法」という。）において、"))) errors.push("item 24 citation parenthesis missing");
if(!capacity.includes(compact("場合は翌月も含む。）の翌月から所定単位数の減算を行う"))) errors.push("item 24 transition parenthesis missing");
const staffing=byId.get("fee-guidance.dayservice.25");
if(!(staffing?.patch_snapshot_ids??[]).includes("dayservice-25-r8-patch")) errors.push("item 25 R8 patch citation missing");
if(!/別紙様式[７7]/.test(staffing?.candidate_text??"")) errors.push("item 25 R8 report form missing");

if(manifest.format_version!==3 || !manifest.image_correction_policy) errors.push("snapshot manifest corrections policy missing");
const supplementIds=new Set((supplements.supplements??[]).map(x=>x.id));
for(const id of [
 "dayservice-5-h27-full-body-supplement",
 "dayservice-6-h27-items-3-4-supplement",
 "dayservice-18-h27-unchanged-text-supplement"
]){
 if(!supplementIds.has(id)) errors.push("missing verified supplement: "+id);
}
for(const item of candidates.items??[]){
 if(/略/.test(item.candidate_text??"")) errors.push("current candidate still contains omission marker: "+item.guidance_id);
}

console.log(JSON.stringify({
 current_state:meta.current_state,
 candidates:(candidates.items??[]).length,
 replay_items:(replay??[]).length,
 human_review:"COMPLETE",
 errors,
 valid:errors.length===0
},null,2));
if(errors.length) process.exitCode=1;
