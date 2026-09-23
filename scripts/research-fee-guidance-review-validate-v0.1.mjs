import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const readJson = (p) => JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));

const review = readJson("data/fee-guidance-review.json");
const candidates = readJson("data/fee-guidance-current-text-candidates.json");
const remuneration = readJson("data/remuneration-review.json");

const errors=[];
const completeExpected=[
  "fee-guidance.dayservice.4",
  "fee-guidance.dayservice.7",
  "fee-guidance.dayservice.7-2",
  "fee-guidance.dayservice.24",
  "fee-guidance.dayservice.25",
];
const blockedExpected=[
  "fee-guidance.dayservice.5",
  "fee-guidance.dayservice.6",
  "fee-guidance.dayservice.18",
];
const sameSet=(a,b)=>{
  const aa=[...new Set(a)].sort(), bb=[...new Set(b)].sort();
  return aa.length===bb.length && aa.every((x,i)=>x===bb[i]);
};

if(review.review_status!=="IN_PROGRESS") errors.push("fee-guidance overall review must remain IN_PROGRESS");
if(!sameSet(review.reviewed_nodes??[],completeExpected)) errors.push("reviewed_nodes mismatch");
if(!sameSet(review.blocked_nodes??[],blockedExpected)) errors.push("blocked_nodes mismatch");
if(review.currentness_review?.latest_relevant_text_amendment_source_id!=="mhlw-r8-fee-guidance-may-amendment"){
  errors.push("latest relevant amendment source mismatch");
}

const candidateById=new Map((candidates.items??[]).map(x=>[x.guidance_id,x]));
const itemById=new Map((review.items??[]).map(x=>[x.guidance_id,x]));
if(itemById.size!==(candidates.items??[]).length) errors.push("review item count mismatch");

for(const candidate of candidates.items??[]){
  const item=itemById.get(candidate.guidance_id);
  if(!item){ errors.push("missing review item: "+candidate.guidance_id); continue; }
  if(item.candidate_text_sha256!==candidate.candidate_text_sha256){
    errors.push("candidate hash drift: "+candidate.guidance_id);
  }
  if(item.baseline_snapshot_id!==candidate.baseline_snapshot_id){
    errors.push("baseline drift: "+candidate.guidance_id);
  }
  const a=[...(item.patch_snapshot_ids??[])].sort();
  const b=[...(candidate.patch_snapshot_ids??[])].sort();
  if(a.length!==b.length || a.some((x,i)=>x!==b[i])){
    errors.push("patch set drift: "+candidate.guidance_id);
  }
  const expectedStatus=completeExpected.includes(candidate.guidance_id)?"COMPLETE":"REVIEW_REQUIRED";
  if(item.human_review_status!==expectedStatus){
    errors.push("human review status mismatch: "+candidate.guidance_id);
  }
}

for(const id of completeExpected){
  const candidate=candidateById.get(id);
  if(!candidate) errors.push("missing complete candidate: "+id);
  else if(/（略）|\(略\)|（略/.test(candidate.candidate_text??"")){
    errors.push("complete candidate still contains omitted text marker: "+id);
  }
}
for(const id of [
  "fee-guidance.dayservice.5",
  "fee-guidance.dayservice.6",
  "fee-guidance.dayservice.18",
]){
  const candidate=candidateById.get(id);
  if(!candidate || !/略/.test(candidate.candidate_text??"")){
    errors.push("expected omitted-text blocker missing: "+id);
  }
}
const staffing=candidateById.get("fee-guidance.dayservice.25");
if(!(staffing?.patch_snapshot_ids??[]).includes("dayservice-25-r8-patch")){
  errors.push("staffing R8 patch missing");
}
if(!sameSet(remuneration.fee_guidance_review?.current_text_complete_ids??[],completeExpected)){
  errors.push("remuneration complete IDs mismatch");
}
if(!sameSet(remuneration.fee_guidance_review?.review_required_ids??[],blockedExpected)){
  errors.push("remuneration blocked IDs mismatch");
}
if(remuneration.review_status!=="IN_PROGRESS"){
  errors.push("overall remuneration review must remain IN_PROGRESS");
}

console.log(JSON.stringify({
  fee_guidance_review_status:review.review_status,
  human_complete:completeExpected.length,
  review_required:blockedExpected.length,
  latest_relevant_text_amendment:review.currentness_review?.latest_relevant_text_amendment??null,
  errors,
  valid:errors.length===0
},null,2));
if(errors.length) process.exitCode=1;
