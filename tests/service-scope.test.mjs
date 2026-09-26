import test from "node:test";
import assert from "node:assert/strict";

import {
  filterRecordsForService,
  isRecordApplicableToService,
  resolveServiceScope,
  serviceApplicability,
} from "../lib/service-scope.ts";

test("homevisit-only Ordinance 37 nodes are exclusive to homevisit", () => {
  const scope = resolveServiceScope(
    "ordinance37",
    "ordinance37.article.18",
  );

  assert.deepEqual(scope.service_ids, ["homevisit"]);
  assert.equal(scope.sharing, "EXCLUSIVE");
  assert.equal(
    isRecordApplicableToService(
      "dayservice",
      "ordinance37",
      "ordinance37.article.18",
    ),
    false,
  );
  assert.equal(
    isRecordApplicableToService(
      "homevisit",
      "ordinance37",
      "ordinance37.article.18",
    ),
    true,
  );
});

test("shared Ordinance 37 nodes keep per-service legal applicability", () => {
  const scope = resolveServiceScope(
    "ordinance37",
    "ordinance37.article.10.p.1",
  );

  assert.deepEqual(scope.service_ids, ["dayservice", "homevisit"]);
  assert.equal(scope.sharing, "SHARED");
  assert.deepEqual(scope.memberships, [
    { service_id: "dayservice", basis: "INCORPORATED_SCOPE" },
    { service_id: "homevisit", basis: "DIRECT_SCOPE" },
  ]);
});

test("dayservice direct Ordinance 37 nodes remain dayservice-only", () => {
  assert.deepEqual(
    resolveServiceScope(
      "ordinance37",
      "ordinance37.article.100",
    ).service_ids,
    ["dayservice"],
  );
});

test("shared Care Insurance Act core is explicit for both services", () => {
  const scope = resolveServiceScope(
    "care_insurance_act",
    "careact.article.74.p.1",
  );

  assert.equal(scope.sharing, "SHARED");
  assert.deepEqual(scope.memberships, [
    { service_id: "dayservice", basis: "SERVICE_SCOPE" },
    { service_id: "homevisit", basis: "SHARED_CORE_INDEX" },
  ]);
});

test("mixed-scope Care Insurance Act Article 8 keeps node-level service isolation", () => {
  assert.equal(
    isRecordApplicableToService(
      "dayservice",
      "care_insurance_act",
      "careact.article.8",
    ),
    true,
  );
  assert.equal(
    isRecordApplicableToService(
      "dayservice",
      "care_insurance_act",
      "careact.article.8.p.7",
    ),
    true,
  );
  assert.equal(
    isRecordApplicableToService(
      "dayservice",
      "care_insurance_act",
      "careact.article.8.p.2",
    ),
    false,
  );
  assert.equal(
    isRecordApplicableToService(
      "homevisit",
      "care_insurance_act",
      "careact.article.8.p.2",
    ),
    true,
  );
  assert.equal(
    isRecordApplicableToService(
      "homevisit",
      "care_insurance_act",
      "careact.article.8.p.7",
    ),
    false,
  );
});

test("unknown services and records fail closed", () => {
  assert.equal(
    serviceApplicability(
      "unknown-service",
      "ordinance37",
      "ordinance37.article.100",
    ).reason,
    "UNKNOWN_SERVICE",
  );
  const unresolved = serviceApplicability(
    "dayservice",
    "ordinance37",
    "ordinance37.article.9999",
  );
  assert.equal(unresolved.applicable, false);
  assert.equal(unresolved.reason, "NO_COMMITTED_SCOPE_EVIDENCE");
});

test("the same contract can filter service-facing collections", () => {
  const records = [
    { id: "ordinance37.article.10", label: "shared" },
    { id: "ordinance37.article.18", label: "homevisit only" },
    { id: "ordinance37.article.100", label: "dayservice only" },
  ];

  assert.deepEqual(
    filterRecordsForService(
      "dayservice",
      "ordinance37",
      records,
      (record) => record.id,
    ).map((record) => record.label),
    ["shared", "dayservice only"],
  );

  assert.deepEqual(
    filterRecordsForService(
      "homevisit",
      "ordinance37",
      records,
      (record) => record.id,
    ).map((record) => record.label),
    ["shared", "homevisit only"],
  );
});
