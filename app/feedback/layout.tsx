import type { ReactNode } from "react";
import { pageMetadata } from "../../lib/site-metadata";

export const metadata = pageMetadata(
  "ご意見・お問い合わせ",
  "介護ルールへのご意見・お問い合わせの案内です。",
  "/feedback",
  false,
);

export default function FeedbackLayout({ children }: { children: ReactNode }) {
  return children;
}
