import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

const load = path => JSON.parse(fs.readFileSync(path, "utf8"));
const handbook = load("data/handbook-content.json");
const fixture = load("tests/fixtures/research-mesh-four-staffing-original.json");
const eligible = fs.readFileSync("components/service-handbook.tsx", "utf8");

test("Research Mesh four staffing drafts add only role sections and preserve all original chapter fields", () => {
  const targets = fixture.service_chapters;
  assert.equal(Object.keys(targets).length, 4);
  const total = Object.values(handbook.services).reduce((n, service) => n + Object.keys(service.chapters).length, 0);
  assert.equal(total, 585);
  let count = 0;
  for (const [serviceId, record] of Object.entries(targets)) {
    const current = handbook.services[serviceId].chapters.staffing;
    const { role_sections: sections, ...rest } = current;
    assert.deepEqual(rest, record.chapter_before, serviceId + ": existing material changed");
    assert.equal(sections.length, record.role_groups, serviceId + ": role group count changed");
    const ids = new Set();
    let requirementCount = 0;
    for (const section of sections) {
      assert.ok(section.id.startsWith("mesh-"));
      assert.ok(!ids.has(section.id), "duplicate role id: " + section.id);
      ids.add(section.id);
      assert.ok(section.title.includes("未審査"), serviceId + ": needs candidate warning");
      assert.ok(section.requirements.length > 0);
      for (const requirement of section.requirements) {
        assert.ok(!ids.has(requirement.id), "duplicate requirement id: " + requirement.id);
        ids.add(requirement.id);
        assert.equal(requirement.verification_state, "EVIDENCE_GAP");
        assert.ok(requirement.description.includes("隔離候補"), "source not shown as candidate");
        assert.ok(requirement.applicability.includes("未完了"), "currentness disclaimer absent");
        assert.ok(requirement.evidence.length > 0);
        assert.ok(requirement.evidence.every(e => e.verification_state === "SOURCE_CANDIDATE_UNVERIFIED"));
        assert.ok(requirement.evidence.every(e => e.checked_at_jst === ""));
        assert.ok(requirement.practical_checks.length > 0);
        requirementCount++;
      }
    }
    assert.equal(requirementCount, record.requirements);
    assert.ok(eligible.includes('"' + serviceId + '"'), serviceId + ": renderer does not allow roles");
    count += requirementCount;
  }
  assert.equal(count, 34);
});

test("Research Mesh source versions cannot grant legal review or project release flags", () => {
  const text = fs.readFileSync("data/handbook-content.json", "utf8");
  const fixture = load("tests/fixtures/research-mesh-four-staffing-original.json");
  for (const sid of Object.keys(fixture.service_chapters)) {
    const roleJson = JSON.stringify(handbook.services[sid].chapters.staffing.role_sections);
    assert.ok(!roleJson.includes("PRIMARY_TEXT_CHECKED_SCOPED"));
    assert.ok(!roleJson.includes("PUBLICATION_READY"));
    assert.ok(!roleJson.includes("VERIFIED_CURRENT"));
    assert.ok(!roleJson.includes("human_review_complete"));
    assert.ok(!roleJson.includes("real_project_work_enabled"));
    assert.ok(text.includes('"' + sid + '"'));
  }
});
