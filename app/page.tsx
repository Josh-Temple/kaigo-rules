import type { Metadata } from "next";

export const metadata: Metadata = { alternates: { canonical: "/" } };

import Link from "next/link";
import QuestionSearch from "../components/question-search";

const foundationLayers = [
  { label: "介護保険法", detail: "制度の定義・指定・給付" },
  { label: "基準省令", detail: "人員・設備・運営" },
  { label: "解釈通知", detail: "基準の具体的な読み方" },
  { label: "報酬", detail: "単位・加算減算・算定" },
  { label: "国Q&A", detail: "個別論点の行政解釈" },
];

export default function HomePage() {
  return (
    <>
      <section className="hero foundation-hero">
        <p className="eyebrow">介護事業所のための制度の手引</p>
        <h1>必要な基準を見つけ、<br />条件と根拠を確かめる。</h1>
        <p className="lead">
          サービスを選ぶと、人員配置、設備、日々の運営、報酬の手引を読めます。
          説明と確認項目から、国の法令・通知・Q&Aへ進めます。確認中の内容は各項目に表示しています。
        </p>
        <div className="entry-links foundation-entry-links">
          <Link className="entry-row reader-main-entry" href="/services">
            <span>サービスを選んで手引を読む</span>
            <small>人員・設備・運営・報酬 →</small>
          </Link>
          <Link className="entry-row" href="/databases/search">
            <span>キーワードから制度資料を探す</span>
            <small>法令・通知・Q&Aをまとめて検索 →</small>
          </Link>
          <Link className="entry-row" href="/legislation">
            <span>法令・通知・報酬を条文順で読む</span>
            <small>サービス別に絞り込み →</small>
          </Link>
          <Link className="entry-row" href="/start">
            <span>実務の流れから確認する</span>
            <small>開設・運営ガイド →</small>
          </Link>
        </div>
      </section>

      <section className="home-section">
        <h2>よく使う手引</h2>
        <div className="reader-featured-services">
          <Link href="/services/dayservice"><strong>通所介護</strong><span>生活相談員・看護職員・介護職員など</span></Link>
          <Link href="/services/dayrehab"><strong>通所リハビリテーション</strong><span>施設の種類と職種ごとの条件</span></Link>
          <Link href="/services/homevisit"><strong>訪問介護</strong><span>管理者・サービス提供責任者・訪問介護員等</span></Link>
        </div>
        <p><Link href="/services">39サービスから選ぶ →</Link></p>
      </section>

      <section className="home-section">
        <p className="eyebrow">制度資料</p>
        <h2>説明の根拠を確かめる</h2>
        <p className="lead">
          一つの資料だけで判断せず、法令から通知・報酬・Q&Aまで、出典へ戻れる形で整理します。
        </p>
        <div className="foundation-list">
          {foundationLayers.map((item, index) => (
            <div className="foundation-row foundation-row-static" key={item.label}>
              <span className="foundation-number">{String(index + 1).padStart(2, "0")}</span>
              <span className="foundation-main">
                <strong>{item.label}</strong>
                <small>{item.detail}</small>
              </span>
              <span className="foundation-state"><small>原典と確認状況を確認</small></span>
            </div>
          ))}
        </div>
        <p className="home-more-link"><Link href="/databases">資料の種類を選んで探す →</Link></p>
      </section>

      <section className="home-section practical-entry">
        <p className="eyebrow">実務から探す</p>
        <h2>よくある疑問から公式の根拠へ</h2>
        <p className="lead">
          実務上の質問から、関連する制度資料へ戻れるページを公開しています。
          現在の質問集は通所介護を中心に整備しており、対象範囲は各ページで確認できます。
        </p>
        <QuestionSearch initialLimit={6} />
        <p className="home-more-link"><Link href="/databases/search">制度DBを直接検索する →</Link></p>
      </section>

      <section className="home-section">
        <p className="eyebrow">出典と使い方</p>
        <h2>必要なときに確認情報へ戻れる</h2>
        <p className="lead">
          各DBでは出典、対象範囲、現行性などの確認情報を必要なときに開ける形で表示します。
          未確認の範囲は確認済みとして扱いません。
        </p>
        <p className="home-more-link"><Link href="/sources">根拠資料を見る →</Link></p>
      </section>
    </>
  );
}
