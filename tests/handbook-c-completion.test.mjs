import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const readJson = path => JSON.parse(fs.readFileSync(path, "utf8"));
const content = readJson("data/handbook-content.json");

const cManifest = {
  "welfare-equipment-rental": [
    "safeguarding", "business_continuity", "remuneration", "deductions",
    "additions", "notifications", "national_qa", "sources_and_history",
  ],
  "preventive-welfare-equipment-rental": [
    "incident_and_infection", "business_continuity", "remuneration", "deductions",
    "additions", "notifications", "national_qa", "sources_and_history",
  ],
  "specific-welfare-equipment-sale": [
    "incident_and_infection", "business_continuity", "remuneration", "deductions",
    "additions", "notifications", "national_qa", "sources_and_history",
  ],
  "specific-preventive-welfare-equipment-sale": [
    "incident_and_infection", "business_continuity", "remuneration", "deductions",
    "additions", "notifications", "national_qa", "sources_and_history",
  ],
  "care-management": [
    "equipment", "incident_and_infection", "business_continuity", "remuneration",
    "deductions", "additions", "national_qa", "sources_and_history",
  ],
  "preventive-support": [
    "equipment", "incident_and_infection", "business_continuity", "remuneration",
    "deductions", "additions", "national_qa", "sources_and_history",
  ],
};

test("C manifest chapters remain present with substantive paragraphs and checkpoints", () => {
  assert.equal(content.schema_version, 1);
  assert.equal(Object.keys(content.services).length, 39);
  assert.equal(Object.keys(cManifest).length, 6);

  let chapterCount = 0;
  for (const [serviceId, chapterIds] of Object.entries(cManifest)) {
    const chapters = content.services[serviceId]?.chapters;
    assert.ok(chapters, `missing C service ${serviceId}`);

    for (const chapterId of chapterIds) {
      const chapter = chapters[chapterId];
      assert.ok(chapter, `missing ${serviceId}/${chapterId}`);
      assert.equal(chapter.paragraphs.length, 3, `${serviceId}/${chapterId} paragraphs`);
      assert.equal(chapter.checkpoints.length, 3, `${serviceId}/${chapterId} checkpoints`);
      assert.ok(chapter.paragraphs.every(value => typeof value === "string" && value.trim().length > 0));
      assert.ok(chapter.checkpoints.every(value => typeof value === "string" && value.trim().length > 0));
      chapterCount += 1;
    }
  }

  assert.equal(chapterCount, 48);
});
