import type { Metadata } from "next";

/** Stable public origin; preview deployment hosts must never become canonicals. */
export const SITE_ORIGIN = "https://kaigo-rules.vercel.app";

/** Curated entry pages only, not unreviewed dynamic source records. */
export const INDEXABLE_ROUTES = [
  "/", "/about", "/databases", "/services", "/law", "/rules",
  "/notices", "/qa", "/fees", "/fees/criteria", "/fees/unit-price",
  "/guide", "/start", "/sources", "/overview", "/services/dayservice",
] as const;

export function pageMetadata(
  title: string,
  description: string,
  canonicalPath: string,
  index = true,
): Metadata {
  if (!/^\/(?:[a-z0-9-]+(?:\/[a-z0-9-]+)*)?$/.test(canonicalPath)) {
    throw new Error("Canonical must be a normalized route path without query or hash");
  }
  return {
    title,
    description,
    alternates: { canonical: canonicalPath },
    ...(index ? {} : { robots: { index: false, follow: true } }),
  };
}
