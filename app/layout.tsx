import ServiceNavigation from "../components/service-navigation";
import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/next";
import Link from "next/link";
import SiteFeedbackLink from "../components/site-feedback-link";
import "./globals.css";

export const metadata: Metadata = {
  title: "介護ルール | 制度の根拠と実務をつなぐ",
  description: "介護保険法、基準省令、解釈通知、報酬、厚生労働省Q&Aを関係付け、実務上の疑問から公式の根拠へたどれるように整理します。",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ja">
      <body>
        <header className="site-header">
          <Link className="brand" href="/">介護ルール</Link>
          <ServiceNavigation />
        </header>
        <main>{children}</main>
        <Analytics />
        <footer className="site-footer">
          <p>
            厚生労働省・e-Gov等の公開資料をもとに整理しています。公式な解釈や個別案件への判断を示すものではありません。
            重要な判断は原典と所管行政庁等で確認してください。
          </p>
          <div className="footer-links">
            <Link href="/about">利用上の注意・免責事項</Link>
            <SiteFeedbackLink />
          </div>
        </footer>
      </body>
    </html>
  );
}

