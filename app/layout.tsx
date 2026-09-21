import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "介護ルール | 通所介護の実務確認",
  description: "通所介護の実務上の疑問を、公式資料へ戻れる形で整理するMVPです。",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ja">
      <body>
        <header className="site-header">
          <Link className="brand" href="/">介護ルール</Link>
          <nav>
            <Link href="/">質問</Link>
            <Link href="/start">これから始める</Link>
            <Link href="/qa">国Q&A</Link>
            <Link href="/rules">基準DB</Link>
            <Link href="/sources">根拠資料</Link>
          </nav>
        </header>
        <main>{children}</main>
        <footer>厚生労働省等の公開資料をもとに構造化しています。未確認事項は推測して回答しません。</footer>
      </body>
    </html>
  );
}
