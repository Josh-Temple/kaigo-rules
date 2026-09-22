import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "介護業務改善",
  description: "介護現場の困りごとから、事例・根拠・改善の選択肢を探すためのサイト。",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
