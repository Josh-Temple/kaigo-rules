import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { splitDayserviceRegionalText } from "../lib/handbook/reader-content.ts";

const n = (text, authority = "national_standard") => ({ text, authority, source_ref: "national-ordinance-37-art93" });
const o = (text, jurisdiction = "横浜市") => ({ text, authority: "municipal_ordinance", jurisdiction, source_ref: "local-ordinance" });
const h = (text, jurisdiction = "横浜市") => ({ text, authority: "municipal_handbook", jurisdiction, source_ref: "local-handbook" });
const classify = (value, segments) => splitDayserviceRegionalText(value, segments);

test("a municipality's first mention never shifts later national law to local category", () => {
  const original = "省令第93条の基準。横浜市の条例。省令第94条の管理者。";
  const segments = [n("省令第93条の基準。"), o("横浜市の条例。"), n("省令第94条の管理者。")];
  assert.deepEqual(classify(original, segments), { segments, classified: true });
});

test("mixed sentence needs authored boundaries, not string searching", () => {
  const original = "国の基準は一人以上、横浜市の資格条件は地域のみ。";
  assert.deepEqual(classify(original).segments, [{text: original, authority: "unclassified"}]);
  const segments = [n("国の基準は一人以上、"), h("横浜市の資格条件は地域のみ。")];
  assert.deepEqual(classify(original, segments).segments, segments);
});

test("another municipality stays independent of Yokohama", () => {
  const original = "名古屋市の条例に係る条件。";
  const segments = [o(original, "名古屋市")];
  assert.deepEqual(classify(original, segments), { segments, classified: true });
});

test("a guide is reference material, never reclassified as binding local ordinance", () => {
  const original = "横浜市の運営手引を参照する。";
  const segments = [h(original)];
  assert.equal(classify(original, segments).segments[0].authority, "municipal_handbook");
});

test("an ordinance remains a local rule, not an optional guide", () => {
  const original = "条例に定める配置。";
  assert.equal(classify(original, [o(original)]).segments[0].authority, "municipal_ordinance");
});

test("national-only and no regional information retain the national source classification", () => {
  const original = "省令第93条。国の解釈通知。";
  const segments = [n("省令第93条。"), n("国の解釈通知。", "national_interpretation")];
  assert.deepEqual(classify(original, segments).segments, segments);
});

test("missing, unverified, malformed source identity or loss of a clause must fail closed", () => {
  const original = "国の要件。横浜市の例外。国の条件。";
  for (const bad of [
    undefined, [],
    [n("国の要件。"), o("横浜市の例外。")],
    [n(original.slice(1))],
    [{text: original, authority: "national_standard", source_ref: ""}],
    [{text: original, authority: "municipal_ordinance", source_ref: "x"}],
    [{text: original, authority: "national_standard", source_ref: "x", jurisdiction: "横浜市"}],
    [{text: original, authority: "unverified", source_ref: "x"}],
  ]) {
    const result = classify(original, bad);
    assert.equal(result.classified, false);
    assert.deepEqual(result.segments, [{text: original, authority: "unclassified"}]);
  }
});

test("all five current dayservice staffing roles preserve original prose and verification state", () => {
  const data = JSON.parse(fs.readFileSync("data/handbook-content.json", "utf8"));
  const roles = data.services.dayservice.chapters.staffing.role_sections;
  assert.deepEqual(roles.map(r => r.title), ["生活相談員", "看護職員", "介護職員", "機能訓練指導員", "管理者"]);
  for (const role of roles) for (const requirement of role.requirements) {
    const original = requirement.description;
    const result = classify(original, requirement.authority_segments);
    assert.equal(result.segments.map(s => s.text).join(""), original);
    assert.equal(requirement.verification_state, "EVIDENCE_GAP");
    if (!requirement.authority_segments?.length) {
      assert.equal(result.classified, false);
      assert.equal(result.segments[0].authority, "unclassified");
    }
  }
});

test("reader never labels an unreviewed mixed fragment as confirmed national or local law", () => {
  const source = fs.readFileSync("components/service-handbook.tsx", "utf8");
  assert.match(source, /splitDayserviceRegionalText\(copy, requirement\.authority_segments, requirement\.evidence\)/);
  assert.match(source, /根拠区分を確認中/);
  assert.doesNotMatch(source, /parts\.national|parts\.regional/);
  const helper = fs.readFileSync("lib/handbook/reader-content.ts", "utf8");
  assert.doesNotMatch(helper, /indexOf\("横浜市"\)/);
});

test("reader classification requires the exact checked evidence URL and matching authority category", () => {
  const phrase = "第93条の必要数を確認する。";
  const url = "https://www.mhlw.go.jp/web/t_doc?dataId=82999404";
  const fragments = [{ text: phrase, authority: "national_standard", source_ref: url }];
  const evidence = (kind, verification_state, evidenceUrl = url) =>
    [{ kind, verification_state, url: evidenceUrl }];
  const verify = candidates => splitDayserviceRegionalText(phrase, fragments, candidates);
  assert.equal(verify(evidence("national_standard", "PRIMARY_TEXT_CHECKED_SCOPED")).classified, true);
  for (const candidates of [
    [], evidence("national_standard", "SOURCE_CANDIDATE_UNVERIFIED"),
    evidence("national_standard", "EVIDENCE_GAP"),
    evidence("national_qa", "PRIMARY_TEXT_CHECKED_SCOPED"),
    evidence("national_standard", "PRIMARY_TEXT_CHECKED_SCOPED", "https://unrelated.example/"),
    [{kind:"national_standard", verification_state:"PRIMARY_TEXT_CHECKED_SCOPED"}],
  ]) {
    assert.equal(verify(candidates).classified, false);
    assert.deepEqual(verify(candidates).segments, [{text:phrase, authority:"unclassified"}]);
  }
});

test("checked Yokohama ordinance cannot support other jurisdictions or be called a municipal handbook", () => {
  const phrase = "横浜市条例の特例。";
  const source = "https://cgi.city.yokohama.lg.jp/somu/reiki/reiki_honbun/g202RG00001746.html";
  const checked = [{kind:"yokohama_ordinance", url:source, verification_state:"PRIMARY_TEXT_CHECKED_SCOPED"}];
  const segment = {text:phrase, authority:"municipal_ordinance", source_ref:source, jurisdiction:"横浜市"};
  assert.equal(splitDayserviceRegionalText(phrase,[segment],checked).classified,true);
  assert.equal(splitDayserviceRegionalText(phrase,[{...segment,jurisdiction:"名古屋市"}],checked).classified,false);
  assert.equal(splitDayserviceRegionalText(phrase,[{...segment,authority:"municipal_handbook"}],checked).classified,false);
  assert.equal(splitDayserviceRegionalText(phrase,[segment],[{...checked[0],verification_state:"SOURCE_CANDIDATE_UNVERIFIED"}]).classified,false);
});

test("production renderer passes actual requirement evidence, never only authored source text", () => {
  const source = fs.readFileSync("components/service-handbook.tsx", "utf8");
  assert.match(source, /splitDayserviceRegionalText\(copy, requirement\.authority_segments, requirement\.evidence\)/);
  const code = fs.readFileSync("lib/handbook/reader-content.ts", "utf8");
  assert.match(code, /PRIMARY_TEXT_CHECKED_SCOPED/);
  assert.match(code, /evidence\.url\.trim\(\) === segment\.source_ref\.trim\(\)/);
});
