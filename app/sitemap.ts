import type { MetadataRoute } from "next";
import { INDEXABLE_ROUTES, SITE_ORIGIN } from "../lib/site-metadata";
import { serviceHandbooks } from "../lib/working-handbook";

export default function sitemap(): MetadataRoute.Sitemap {
  const paths = new Set<string>([...INDEXABLE_ROUTES, ...serviceHandbooks.map(s => `/services/${s.service_id}`)]);
  return [...paths].map((path) => ({
    url: new URL(path, SITE_ORIGIN).toString(),
    changeFrequency: "weekly" as const,
    priority: path === "/" ? 1 : 0.6,
  }));
}
