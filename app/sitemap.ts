import type { MetadataRoute } from "next";
import { INDEXABLE_ROUTES, canonicalUrl } from "../lib/site-metadata";

export default function sitemap(): MetadataRoute.Sitemap {
  const paths = new Set<string>(INDEXABLE_ROUTES);
  return [...paths].map((path) => ({
    url: canonicalUrl(path),
    changeFrequency: "weekly" as const,
    priority: path === "/" ? 1 : 0.6,
  }));
}
