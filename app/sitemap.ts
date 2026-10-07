import type { MetadataRoute } from "next";
import { INDEXABLE_ROUTES, SITE_ORIGIN } from "../lib/site-metadata";

export default function sitemap(): MetadataRoute.Sitemap {
  return INDEXABLE_ROUTES.map((path) => ({
    url: new URL(path, SITE_ORIGIN).toString(),
    changeFrequency: "weekly" as const,
    priority: path === "/" ? 1 : 0.6,
  }));
}
