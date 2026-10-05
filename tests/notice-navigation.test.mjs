import test from "node:test";
import assert from "node:assert/strict";
import {
  buildNoticeDisplayGroups,
  buildNoticeDisplaySections,
  filterNoticeRecordsByQuery,
  findNoticeDisplayGroup,
} from "../lib/notice-navigation.ts";

const service = (
  service_id,
  label,
  service_class,
  record_count = 0,
) => ({
  service_id,
  label,
  service_class,
  service_status: "TEST",
  route_enabled: false,
  record_count,
  notice_status: "TEST",
});

test("preventive services share the primary service entry", () => {
  const groups = buildNoticeDisplayGroups([
    service("homebath", "訪問入浴介護", "HOME_SERVICE", 13),
    service(
      "preventive-homebath",
      "介護予防訪問入浴介護",
      "PREVENTIVE_SERVICE",
      4,
    ),
    service("preventive-support", "介護予防支援", "PREVENTIVE_SUPPORT", 34),
  ]);

  assert.equal(groups.length, 2);

  const homebath = groups.find((group) => group.id === "homebath");
  assert.ok(homebath);
  assert.deepEqual(homebath.member_ids, [
    "homebath",
    "preventive-homebath",
  ]);
  assert.equal(homebath.companion_label, "介護予防訪問入浴介護");
  assert.equal(homebath.record_count, 17);
  assert.equal(
    groups.some((group) => group.id === "preventive-homebath"),
    false,
  );

  const resolvedFromPreventive = findNoticeDisplayGroup(
    groups,
    "preventive-homebath",
  );
  assert.equal(resolvedFromPreventive?.id, "homebath");

  const preventiveSupport = groups.find(
    (group) => group.id === "preventive-support",
  );
  assert.ok(preventiveSupport);
  assert.deepEqual(preventiveSupport.member_ids, ["preventive-support"]);
  assert.equal(preventiveSupport.service_class, "PREVENTIVE_SUPPORT");
});

test("display sections keep preventive support independent", () => {
  const groups = buildNoticeDisplayGroups([
    service("care-management", "居宅介護支援", "CARE_MANAGEMENT", 32),
    service("preventive-support", "介護予防支援", "PREVENTIVE_SUPPORT", 34),
  ]);
  const sections = buildNoticeDisplaySections(groups);

  assert.equal(
    sections.find((section) => section.serviceClass === "CARE_MANAGEMENT")
      ?.groups[0].id,
    "care-management",
  );
  assert.equal(
    sections.find((section) => section.serviceClass === "PREVENTIVE_SUPPORT")
      ?.groups[0].id,
    "preventive-support",
  );
});

test("notice query matches normalized text and requires every term", () => {
  const records = [
    {
      id: "one",
      service_id: "homevisit",
      service_label: "訪問介護",
      section: "運営に関する基準",
      number_path: ["第三", "運営"],
      title: "管理者の責務",
      body_text: "管理者は従業者及び業務の管理を一元的に行う。",
    },
    {
      id: "two",
      service_id: "homevisit",
      service_label: "訪問介護",
      section: "設備に関する基準",
      number_path: ["第三", "設備"],
      title: "設備及び備品等",
      body_text: "必要な設備及び備品等を備える。",
    },
  ];

  assert.deepEqual(
    filterNoticeRecordsByQuery(records, "管理者　業務").map(
      (record) => record.id,
    ),
    ["one"],
  );
  assert.deepEqual(filterNoticeRecordsByQuery(records, "管理者 設備"), []);
});
