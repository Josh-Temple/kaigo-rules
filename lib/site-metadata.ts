import type { Metadata } from "next";

/** Stable public origin (GitHub Pages); preview deployment hosts must never become canonicals. */
export const SITE_ORIGIN = "https://josh-temple.github.io/kaigo-rules";

/** Join a normalized route path onto SITE_ORIGIN without dropping the repository base path. */
export function canonicalUrl(canonicalPath: string): string {
  if (!/^\/(?:[a-z0-9-]+(?:\/[a-z0-9-]+)*)?$/.test(canonicalPath)) {
    throw new Error("Canonical must be a normalized route path without query or hash");
  }
  return canonicalPath === "/" ? `${SITE_ORIGIN}/` : `${SITE_ORIGIN}${canonicalPath}`;
}

/** Curated entry pages only, not unreviewed dynamic source records. */
export const INDEXABLE_ROUTES = [
  "/", "/about", "/databases", "/services", "/law", "/rules",
  "/notices", "/qa", "/fees", "/fees/criteria", "/fees/unit-price",
  "/guide", "/start", "/opening-guide", "/sources", "/overview",
  "/legislation",
] as const;

export function pageMetadata(
  title: string,
  description: string,
  canonicalPath: string,
  index = true,
): Metadata {
  return {
    title,
    description,
    alternates: { canonical: canonicalUrl(canonicalPath) },
    ...(index ? {} : { robots: { index: false, follow: true } }),
  };
}
