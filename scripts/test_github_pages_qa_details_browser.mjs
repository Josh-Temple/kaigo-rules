// Only serves the unpublished temporary experiment on loopback.
import { chromePath, chromeSmoke } from "../experiments/github-pages-db/chrome-smoke.mjs";
const dir = process.argv[2];
if (!dir || !chromePath) throw new Error("Private output directory and Chrome are required");
for (const width of [360, 390]) {
  const result = await chromeSmoke(dir, width, { qaLocal: true });
  console.log("QA_DETAILS_CHROME: " + JSON.stringify(result));
}
