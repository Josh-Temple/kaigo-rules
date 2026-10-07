import type { MetadataRoute } from "next";
import { OPS_SITE_URL } from "../lib/site-metadata";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
    },
    sitemap: `${OPS_SITE_URL}/sitemap.xml`,
    host: OPS_SITE_URL,
  };
}
