export const OPS_SITE_URL = "https://ops-site-pi.vercel.app";
export const OPS_SITE_NAME = "介護業務改善";

type PublicPageMetadataInput = {
  path: string;
  title: string;
  description: string;
  type: "website" | "article";
};

export function buildPublicPageMetadata({
  path,
  title,
  description,
  type,
}: PublicPageMetadataInput) {
  return {
    title,
    description,
    alternates: {
      canonical: path,
    },
    openGraph: {
      title,
      description,
      url: path,
      siteName: OPS_SITE_NAME,
      locale: "ja_JP",
      type,
    },
    twitter: {
      card: "summary" as const,
      title,
      description,
    },
  };
}
