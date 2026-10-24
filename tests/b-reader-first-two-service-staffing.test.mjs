import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const content = JSON.parse(fs.readFileSync("data/handbook-content.json", "utf8"));
const component = fs.readFileSync("components/service-handbook.tsx", "utf8");
const generator = fs.readFileSync("scripts/build_handbook_site.py", "utf8");
const chapter = id => content.services[id].chapters.staffing;

test("only eligible two-service staffing is rendered ahead of legacy paragraphs", () => {
  assert.match(component, /\["homevisit", "dayrehab"\]\.includes\(service\.service_id\)/);
  assert.match(component, /<StaffingRoles service=\{service\} chapter=\{chapter\} full=\{full\} \/>/);
  assert.match(component, /<h4>\{role\.title\}<\/h4>/);
  assert.match(component, /<h5>\{requirement\.title\}<\/h5>/);
  assert.match(component, /requirement\.verification_state === "EVIDENCE_GAP"/);
  assert.match(component, /evidence\.verification_state === "PRIMARY_TEXT_CHECKED_SCOPED"/);
  assert.ok(generator.includes('ROLE_TARGETS = {"homevisit", "dayrehab",'));
});

test("39 services 585 chapters remain and two staffing chapters preserve original paragraphs", () => {
  assert.equal(Object.keys(content.services).length, 39);
  assert.equal(Object.values(content.services).reduce((n,s)=>n+Object.keys(s.chapters).length,0), 585);
  assert.ok(chapter("dayrehab").paragraphs.some(p=>p.includes("第111条")));
  assert.ok(chapter("homevisit").paragraphs.some(p=>p.includes("第5条")));
  assert.equal(chapter("homevisit").role_sections.length, 3);
  assert.equal(chapter("homevisit").role_sections.reduce((n,r)=>n+r.requirements.length,0),10);
});

test("dayrehab roles separate specialist, care and management, without certifying currentness", () => {
  const roles=chapter("dayrehab").role_sections;
  assert.deepEqual(roles.map(r=>r.title), ["医師","理学療法士・作業療法士・言語聴覚士","看護職員・介護職員","管理者"]);
  assert.equal(roles.reduce((n,r)=>n+r.requirements.length,0),7);
  for (const role of roles) for (const requirement of role.requirements) {
    assert.equal(requirement.verification_state,"EVIDENCE_GAP");
    assert.ok(requirement.description.length>0 && requirement.applicability.length>0);
    assert.ok(requirement.practical_checks.length);
    for (const evidence of requirement.evidence) {
      assert.ok(evidence.verification_state!=="PRIMARY_TEXT_CHECKED_SCOPED" || evidence.checked_at_jst.endsWith("JST"));
      if (evidence.url) assert.match(evidence.url,/^https:\/\/(www\.mhlw\.go\.jp|www\.city\.yokohama\.lg\.jp)\//);
    }
  }
  assert.match(JSON.stringify(roles), /診療所/);
  assert.match(JSON.stringify(roles), /一体的/);
  assert.match(JSON.stringify(roles), /常勤換算/);
  assert.doesNotMatch(JSON.stringify(roles), /PUBLICATION_READY|VERIFIED_CURRENT/);
});
