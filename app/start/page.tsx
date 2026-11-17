import Link from "next/link";
import { pageMetadata } from "../../lib/site-metadata";

export const metadata = pageMetadata("はじめての方へ", "Kaigo Rulesの目的と、手引・検索・原典の使い方を紹介します。", "/start");

export default function StartPage() {
  return (
    <article className="answer-page wide-page">
      <p className="eyebrow">はじめての方へ</p>
      <h1>Kaigo Rulesについて</h1>
      <p className="lead">
        Kaigo Rulesは、介護事業所で働く方が、サービスごとの基準や報酬を調べ、
        その条件と根拠になる国の資料をたどるための手引です。
        人員配置、設備、日々の運営など、確認したいことから必要な資料を探せます。
      </p>
      <section className="section">
        <h2>まずは、調べ方を選ぶ</h2>
        <div className="entry-links">
          <Link className="entry-row" href="/services"><span>サービスから手引を読む</span><small>サービスを選び、人員・設備・運営などの章へ →</small></Link>
          <Link className="entry-row" href="/databases/search"><span>キーワードで資料を探す</span><small>法令・通知・国Q&Aなどを横断検索 →</small></Link>
          <Link className="entry-row" href="/qa"><span>国Q&Aを探す</span><small>国が示した質問と回答を検索 →</small></Link>
        </div>
      </section>
      <section className="section">
        <h2>手引の読み方</h2>
        <ol>
          <li>対象のサービスと、知りたい章を選びます。</li>
          <li>説明や確認項目を読み、人数、資格、例外などの条件を確認します。</li>
          <li>関連する法令・通知・国Q&Aを開き、原典と適用される時点を確認します。</li>
        </ol>
        <p>チェック欄は確認事項の整理に使えます。チェックしたことだけで法令への適合が証明されるものではありません。</p>
        <p><Link href="/guide">調べ方を詳しく見る →</Link></p>
      </section>
      <section className="section">
        <h2>利用するときの注意</h2>
        <p>資料や説明の確認状況は項目によって異なります。過去の資料や、現行性・適用条件を確認中の内容もあるため、各ページの注意を確認してください。</p>
        <p>このサイトは公式な解釈や個別の判断に代わるものではありません。重要な判断の前に最新の国の原典と、所在地を所管する指定権者の条例・取扱いを確認してください。</p>
        <p><Link href="/sources">公式資料と出典について →</Link> ／ <Link href="/overview">制度資料の種類を見る →</Link></p>
      </section>
      <section className="section">
        <h2>事業所の開設を考えている方へ</h2>
        <p>通所介護を例に、開設前の相談から人員・設備、申請までの確認順を案内しています。</p>
        <p><Link href="/opening-guide">通所介護の開設・運営ガイドを見る →</Link></p>
      </section>
    </article>
  );
}
