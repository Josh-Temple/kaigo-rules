import type { MetadataRoute } from "next";
import { OPS_SITE_URL } from "../lib/site-metadata";
import { issueRegistry } from "./issues/registry";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: `${OPS_SITE_URL}/`,
      changeFrequency: "weekly",
      priority: 1,
    },
    ...issueRegistry.map((issue) => ({
      url: `${OPS_SITE_URL}${issue.href}`,
      changeFrequency: "monthly" as const,
      priority: 0.8,
    })),
    {
      url: `${OPS_SITE_URL}/guides/medication-incident-sources`,
      changeFrequency: "monthly",
      priority: 0.6,
    },
  ];
}
