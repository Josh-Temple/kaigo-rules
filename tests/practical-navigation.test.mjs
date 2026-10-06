import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {rankQuestionMatches} from "../lib/question-search.ts";
import {qaDetailHref, noticeDetailHref} from "../lib/evidence-navigation.ts";
import {resolveNoticeSourceLinks} from "../lib/question-authority-expansion.ts";
import {practicalGuideJourneys, practicalGuidePolicy} from "../lib/practical-guide.ts";
const load = file => JSON.parse(fs.readFileSync(file));
const questions=load("data/questions.json");
test("natural nurse query suppresses generic irrelevant FAQ matches",()=>{
 assert.deepEqual(rankQuestionMatches(questions,"看護師は常駐する必要がありますか").map(q=>q.slug),["nurse-staffing"]);
});
test("evaluation cases preserve expected first destination",()=>{
 for(const c of load("data/practical-navigation-evaluation.json").cases) assert.equal(rankQuestionMatches(questions,c.question)[0]?.slug,c.slug,c.id);
});
test("Q&A direct relation resolves distinct original and corrected corpus IDs",()=>{
 const evidence=load("data/qa-direct-evidence.json"), corpus=load("data/qa-corpus.json");
 for(const [id,row] of Object.entries(evidence)){
  assert.ok(corpus.find(x=>x.id===row.corpus_id));
  assert.equal(qaDetailHref(id),`/qa/${id}`);assert.ok(!qaDetailHref(id).includes("?q="));
 }
 assert.equal(evidence["qa.dayservice.nurse.external.2015.50"].revised_by,"qa.mhlw.d9a7f5b49c1ba8a9326e");
 assert.match(corpus.find(x=>x.id==="qa.mhlw.d9a7f5b49c1ba8a9326e").answer,/問 50 の修正/);
});
test("notice direct source cannot include Q&A registry",()=>{
 const notices=load("data/notice-nodes.json"),sources=load("data/sources.json");
 const node=notices.find(x=>x.id==="notice.dayservice.nurse.external-linkage");
 const links=resolveNoticeSourceLinks(node,sources);
 assert.equal(links.length,1);assert.equal(links[0].sourceId,"mhlw-interpretation-nurse-linkage");assert.match(links[0].url,/#page=30$/);assert.match(links[0].locator,/⑥/);
 assert.equal(noticeDetailHref(node.id),`/notices/${node.id}`);
});

test("practical guide exposes multiple bounded source-navigation journeys",()=>{
 assert.equal(practicalGuidePolicy.workingLabel,"実務ガイド");
 assert.ok(practicalGuideJourneys.length>=4);
 assert.equal(new Set(practicalGuideJourneys.map(x=>x.id)).size,practicalGuideJourneys.length);
 for(const journey of practicalGuideJourneys){
  assert.ok(journey.firstChecks.length>=2,journey.id);
  assert.ok(journey.databaseLinks.length>=2,journey.id);
  for(const link of journey.databaseLinks) assert.match(link.href,/^\//,journey.id);
  assert.ok(journey.officialSourceIds.length>=1,journey.id);
 }
});
test("practical guide official source references resolve to canonical source registry",()=>{
 const sourceIds=new Set(load("data/sources.json").map(x=>x.id));
 for(const journey of practicalGuideJourneys){
  for(const sourceId of journey.officialSourceIds) assert.ok(sourceIds.has(sourceId),`${journey.id}: ${sourceId}`);
 }
});


test("practical guide retains four main journeys and adds concrete sub-journeys",()=>{
 const ids=practicalGuideJourneys.map(x=>x.id);
 assert.deepEqual(ids,["standards","designation","remuneration","qa"]);
 const subJourneys=practicalGuideJourneys.flatMap(x=>x.subJourneys||[]);
 const subIds=new Set(subJourneys.map(x=>x.id));
 for(const id of ["staffing","equipment","operations","fee-guidance","unit-price"]) assert.ok(subIds.has(id),id);
 assert.equal(subJourneys.length,5);
 for(const journey of subJourneys){
  assert.ok(journey.firstChecks.length>=2,journey.id);
  assert.ok(journey.databaseLinks.length>=2,journey.id);
  for(const link of journey.databaseLinks) assert.match(link.href,/^\//,journey.id);
  assert.ok(journey.officialSourceIds.length>=1,journey.id);
 }
});

test("service-aware guide groups regular and preventive services without collapsing canonical ids",async()=>{
 const {practicalGuideServiceGroups}=await import("../lib/practical-guide.ts");
 const manifest=load("data/services/manifest.json");
 const currentServiceIds=new Set(manifest.services.map(x=>x.service_id));
 const groupedIds=[];
 for(const group of practicalGuideServiceGroups){
  assert.ok(group.serviceIds.length>=1,group.id);
  for(const serviceId of group.serviceIds){
   assert.ok(currentServiceIds.has(serviceId),`${group.id}: ${serviceId}`);
   groupedIds.push(serviceId);
  }
 }
 assert.equal(new Set(groupedIds).size,groupedIds.length);
 assert.equal(groupedIds.length,manifest.services.length);
 assert.deepEqual(new Set(groupedIds),currentServiceIds);
 const expectedPairs=[
  ["homebath","preventive-homebath"],
  ["homenursing","preventive-homenursing"],
  ["homerehab","preventive-homerehab"],
  ["homecaremanagement","preventive-homecaremanagement"],
  ["dayrehab","preventive-dayrehab"],
  ["shortstay-life","preventive-shortstay-life"],
  ["shortstay-medical","preventive-shortstay-medical"],
  ["specific-facility","preventive-specific-facility"],
  ["welfare-equipment-rental","preventive-welfare-equipment-rental"],
  ["specific-welfare-equipment-sale","specific-preventive-welfare-equipment-sale"],
  ["dementia-dayservice","preventive-dementia-dayservice"],
  ["small-scale-multifunctional","preventive-small-scale-multifunctional"],
  ["dementia-group-home","preventive-dementia-group-home"],
 ];
 for(const [regular,preventive] of expectedPairs){
  const group=practicalGuideServiceGroups.find(x=>x.serviceIds.includes(regular));
  assert.ok(group,`missing group for ${regular}`);
  assert.ok(group.serviceIds.includes(preventive),`${regular} must pair with ${preventive}`);
 }
 const preventiveSupport=practicalGuideServiceGroups.find(x=>x.serviceIds.includes("preventive-support"));
 assert.deepEqual(preventiveSupport?.serviceIds,["preventive-support"]);
});

test("new practical guide sub-journeys preserve primary-source return paths",()=>{
 const sources=new Set(load("data/sources.json").map(x=>x.id));
 const subJourneys=practicalGuideJourneys.flatMap(x=>x.subJourneys||[]);
 for(const id of ["staffing","equipment","operations","fee-guidance","unit-price"]){
  const journey=subJourneys.find(x=>x.id===id);
  assert.ok(journey,id);
  assert.ok(journey.officialSourceIds.length>=1,id);
  for(const sourceId of journey.officialSourceIds) assert.ok(sources.has(sourceId),`${id}: ${sourceId}`);
 }
});
