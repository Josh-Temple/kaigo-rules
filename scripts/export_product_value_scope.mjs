#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { filterRecordsForService } from "../lib/service-scope.ts";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

const load = (relativePath) =>
  JSON.parse(fs.readFileSync(path.join(ROOT, relativePath), "utf8"));

const argIndex = process.argv.indexOf("--service-id");
const serviceId = argIndex >= 0 ? process.argv[argIndex + 1] : "dayservice";
if (!serviceId) {
  throw new Error("--service-id requires a value");
}

const ordinance = load("data/ordinance37-nodes.json");
const careAct = load("data/care-insurance-act-nodes.json");

const scopedOrdinance = filterRecordsForService(
  serviceId,
  "ordinance37",
  ordinance,
  (record) => record.id,
);
const scopedCareAct = filterRecordsForService(
  serviceId,
  "care_insurance_act",
  careAct,
  (record) => record.id,
);

const result = {
  format_version: 1,
  generated_by: "scripts/export_product_value_scope.mjs",
  contract: "lib/service-scope.ts",
  service_id: serviceId,
  ordinance37: {
    node_ids: scopedOrdinance.map((record) => record.id).sort(),
    article_ids: scopedOrdinance
      .filter((record) => record.node_type === "article")
      .map((record) => record.id)
      .sort(),
  },
  care_insurance_act: {
    node_ids: scopedCareAct.map((record) => record.id).sort(),
    article_ids: scopedCareAct
      .filter((record) => record.node_type === "article")
      .map((record) => record.id)
      .sort(),
  },
};

process.stdout.write(JSON.stringify(result));
