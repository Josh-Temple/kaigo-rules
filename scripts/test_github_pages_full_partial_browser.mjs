// Browser test for the unpublished combined handbook, search and details.
import { chromePath, chromeSmoke } from "../experiments/github-pages-db/chrome-smoke.mjs";
const dir = process.argv[2];
if (!dir || !chromePath) throw new Error("Private output directory and Chrome are required");
for (const width of [360, 390]) {
  const result = await chromeSmoke(dir, width, {
    base: "/databases/search/", handbook: "/handbook/dayservice/staffing.html",
    qaLocal: true, legalLocal: true,
  });
  console.log("FULL_PARTIAL_CHROME: " + JSON.stringify(result));
}
