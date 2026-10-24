import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

const read = path => JSON.parse(fs.readFileSync(path, "utf8"));
const source = read("data/handbook-content.json");
const baseline = read("tests/fixtures/research-mesh-next-four-staffing-original.json");
const ids = Object.keys(baseline.service_chapters);
const component = fs.readFileSync("components/service-handbook.tsx", "utf8");

test("four next-wave Research Mesh staffing chapters preserve original content and expose only 29 selected candidates", () => {
  assert.equal(ids.length, 4);
  assert.equal(Object.values(source.services).reduce((n, service) => n + Object.keys(service.chapters).length, 0), 585);
  let total = 0;
  let sourceCount = 0;
  for (const sid of ids) {
    const prior = baseline.service_chapters[sid];
    const current = source.services[sid].chapters.staffing;
    const { role_sections: roles, ...unchanged } = current;
    assert.deepEqual(unchanged, prior.chapter_before, sid + ": old handbook content changed");
    assert.ok(Array.isArray(roles) && roles.length >= 1 && roles.length <= 3, sid + ": group count");
    assert.ok(component.includes('"' + sid + '"'), sid + ": role display is disabled");
    let perService = 0;
    for (const role of roles) {
      assert.ok(role.id.startsWith("mesh-"));
      assert.ok(role.title.includes("未審査"));
      for (const rule of role.requirements) {
        assert.ok(rule.id.startsWith("mesh-"));
        assert.equal(rule.verification_state, "EVIDENCE_GAP");
        assert.ok(rule.description.includes("Research Mesh隔離候補"));
        assert.ok(rule.description.includes("未完了"));
        assert.ok(rule.applicability.includes("未完了"));
        assert.ok(rule.evidence.length === 1);
        for (const evidence of rule.evidence) {
          assert.equal(evidence.verification_state, "SOURCE_CANDIDATE_UNVERIFIED");
          assert.equal(evidence.checked_at_jst, "");
          assert.ok(evidence.locator.includes("#第"));
          assert.ok(!evidence.url, "unreviewed source URL must not be displayed");
        }
        assert.ok(rule.practical_checks.length >= 1);
        perService++;
      }
    }
    assert.equal(perService, prior.selected_rules, sid + ": missing or duplicated rule");
    assert.ok(prior.original_candidate_rules >= perService);
    assert.match(prior.source_zip_sha256, /^[a-f0-9]{64}$/);
    total += perService;
    sourceCount += prior.original_candidate_rules;
  }
  assert.equal(total, 29);
  assert.equal(sourceCount, 47);
});

test("four next-wave role candidates do not silently gain legal assurance", () => {
  for (const sid of ids) {
    const roles = JSON.stringify(source.services[sid].chapters.staffing.role_sections);
    for (const forbidden of ["PRIMARY_TEXT_CHECKED_SCOPED", "PUBLICATION_READY", "VERIFIED_CURRENT", "real_project_work_enabled", "human_review_complete"]) {
      assert.ok(!roles.includes(forbidden), sid + ": forbidden confidence state " + forbidden);
    }
  }
});
