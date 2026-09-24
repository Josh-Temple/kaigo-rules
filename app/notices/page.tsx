import VerificationSummary from "../../components/verification-summary";
import Link from "next/link";
import nodesData from "../../data/notice-current-skeleton.json";
import metaData from "../../data/notice-current-meta.json";
import chainData from "../../data/notice-source-chain.json";
import sourcesData from "../../data/sources.json";
import reviewPacketData from "../../data/notice-review-packet.json";
import currentnessLedgerData from "../../data/notice-rouki25-currentness-ledger.json";

type NoticeNode = {
  id: string;
  parent_id: string | null;
  depth: number;
  number_path: string[];
  title: string;
  service_scope: string;
  verification_status: string;
  structure_status: string;
  official_text: string | null;
  related_ordinance_ids: string[];
  evidence: Array<{ source_id: string; locator: string; evidence_type: string }>;
};

const nodes = nodesData as NoticeNode[];
const meta = metaData as any;
const chain = chainData as Array<any>;
const sources = sourcesData as Array<any>;
const reviewPacket = reviewPacketData as any;
const currentnessLedger = currentnessLedgerData as any;

const statusLabel: Record<string, string> = {
  VERIFIED_CURRENT: "現行確認済み",
  KNOWN_AFTER_TEXT: "改正後文を確認",
  INHERITED_UNVERIFIED: "継承候補・要再生",
  UNKNOWN: "未確認",
  DELETED: "削除確認",
  NOT_APPLICABLE: "対象外",
};

const statusClass: Record<string, string> = {
  VERIFIED_CURRENT: "notice-status-verified",
  KNOWN_AFTER_TEXT: "notice-status-known",
  INHERITED_UNVERIFIED: "notice-status-inherited",
  UNKNOWN: "notice-status-unknown",
};

const childrenOf = (parentId: string | null) =>
  nodes.filter((node) => node.parent_id === parentId);

const ordinanceHref = (id: string) => {
  const match = id.match(/^ordinance37\.article\.([0-9-]+)/);
  return match ? `/rules/${match[1]}` : "/rules";
};

function NoticeTree({ parentId }: { parentId: string | null }) {
  const children = childrenOf(parentId);
  if (!children.length) return null;

  return (
    <div className={parentId ? "notice-tree notice-tree-nested" : "notice-tree"}>
      {children.map((node) => (
        <section id={node.id} className={`notice-node notice-depth-${node.depth}`} key={node.id}>
          <div className="notice-node-head">
            <div>
              <p className="meta">{node.number_path.join(" / ")}</p>
              <h2>{node.title}</h2>
            </div>
            <span className={`notice-db-status ${statusClass[node.verification_status] || ""}`}>
              {statusLabel[node.verification_status] || node.verification_status}
            </span>
          </div>

          {node.official_text ? (
            <p>{node.official_text}</p>
          ) : (
            <p className="notice-hole">本文はまだ統合していません。</p>
          )}

          {node.related_ordinance_ids.length ? (
            <p className="notice-related">
              対応する基準：
              {node.related_ordinance_ids.map((id, index) => (
                <span key={id}>
                  {index > 0 ? " / " : ""}
                  <Link href={ordinanceHref(id)}>{id.replace("ordinance37.article.", "第")}条</Link>
                </span>
              ))}
            </p>
          ) : null}

          <details>
            <summary>根拠状態を見る</summary>
            <p className="meta">構造状態：{node.structure_status}</p>
            {node.evidence.map((evidence) => {
              const source = sources.find((item) => item.id === evidence.source_id);
              return (
                <p className="meta" key={`${evidence.source_id}-${evidence.locator}`}>
                  {source ? <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a> : evidence.source_id}
                  {" / "}{evidence.locator} / {evidence.evidence_type}
                </p>
              );
            })}
          </details>

          <NoticeTree parentId={node.id} />
        </section>
      ))}
    </div>
  );
}

export default function NoticesPage() {
  const machineCandidates = (reviewPacket.items || []).length;
  const independentPass = (reviewPacket.items || []).filter((item: any) => item.independent_verification?.result === "PASS").length;
  const verified = (reviewPacket.items || []).filter((item: any) => item.reviewer_decision && item.reviewed_candidate_sha256 === item.candidate_text_sha256).length;
  const currentnessHold = currentnessLedger.final_audit_classification?.counts?.HOLD || 0;
  const mismatch = currentnessLedger.final_audit_classification?.counts?.MISMATCH || 0;
  return (
    <article className="answer-page notice-db-page">
      <p className="eyebrow">INTERPRETATION NOTICE DATABASE</p>
      <h1>通所介護の解釈通知DB</h1>
      <p className="lead">
        老企第25号「指定居宅サービス等及び指定介護予防サービス等に関する基準について」を、
        通所介護に必要な範囲から現行構造へ再構成しています。
      </p>

      <div className="notice">
        <strong>これは厚生労働省が公開した「現行統合版」ではありません。</strong><br />
        新旧対照表・過去資料から現行の骨格を組み立てている途中です。
        未確認部分は空欄のまま残し、推測で本文を補いません。
      </div>

      <VerificationSummary layerId="rouki25-dayservice" />

      <section className="rules-stats notice-stats">
        <div><strong>{machineCandidates}</strong><span>本文候補</span></div>
        <div><strong>{independentPass}</strong><span>独立機械照合PASS</span></div>
        <div><strong>{currentnessHold}</strong><span>現行性coverage未完了</span></div>
        <div><strong>{mismatch}</strong><span>具体的不一致</span></div>
      </section>

      <div className="notice">
        <strong>本文再構成の整合性と、現在有効な本文であることの証明は分けて扱っています。</strong><br />
        22項目は機械再構成・独立機械照合で具体的不一致を確認していません。
        一方、厚生労働省の後続改正を網羅できる公式経路が閉じていないため、現行性は22項目とも未確定です。
      </div>

      <div className="notice-review-entry">
        <div>
          <strong>22項目の人手確認用packetを用意しています。</strong>
          <p>本文候補、一次資料の該当ページ、改正適用順、hash、独立照合結果を1項目ずつ確認できます。</p>
        </div>
        <Link href="/notices/review">レビュー画面を開く →</Link>
      </div>

      <section className="section">
        <h2>再構成の進め方</h2>
        <div className="reconstruction-flow">
          <span>1 最新の骨格</span><b>→</b><span>2 過去資料で穴埋め</span><b>→</b>
          <span>3 改正を順方向に再生</span><b>→</b><span>4 人手確認</span>
        </div>
        <p className="meta">
          骨格データの状態：{meta.current_state}。本文候補22項目は機械再構成と独立機械照合まで完了しています。
          ただし、後続改正coverageが未完了のため「現行統合版」とは表示しません。
        </p>
      </section>

      <section className="section">
        <h2>資料チェーン</h2>
        <div className="source-chain">
          {chain.map((entry) => {
            const source = sources.find((item) => item.id === entry.source_id);
            return (
              <div className="source-chain-row" key={entry.source_id}>
                <span className="meta">{entry.issued_period}</span>
                <div>
                  <strong>{source?.title || entry.source_id}</strong>
                  <p>{entry.use}</p>
                  {entry.warning ? <p className="meta">注意：{entry.warning}</p> : null}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <section className="section">
        <h2>現在の骨格</h2>
        <p>
          「改正後文を確認」は新旧対照表の新欄等で現在側の断片を確認できたもの、
          「継承候補・要再生」は過去資料の見出し等を候補として保持しているものです。
        </p>
        <NoticeTree parentId={null} />
      </section>

      <section className="section">
        <h2>次の工程</h2>
        <p>
          同じ22項目を繰り返し再監査するのではなく、新しい一次資料・改正通知・統合本文が確認できたときに
          currentness ledgerを更新します。人による確認は、具体的な不一致や疑義が出た箇所を中心に行います。
        </p>
        <p><Link href="/notices/review">22項目の根拠と監査状態を見る →</Link></p>
      </section>
    </article>
  );
}
