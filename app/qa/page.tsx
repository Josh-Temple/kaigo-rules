import VerificationSummary from "../../components/verification-summary";
import Link from "next/link";
import qaCorpusData from "../../data/qa-corpus.json";
import qaMetaData from "../../data/qa-corpus-meta.json";
import sourcesData from "../../data/sources.json";

type QaItem = {
  id: string;
  service_code: string;
  service_label: string;
  scope: string;
  standard_code: string;
  standard_label: string;
  topic: string;
  question: string;
  answer: string;
  issued_source: string;
  number: string;
  source_id: string;
  ingestion_status: string;
};

type SearchParams = Promise<{
  q?: string;
  service?: string;
  standard?: string;
  page?: string;
}>;

const qaCorpus = qaCorpusData as QaItem[];
const qaMeta = qaMetaData as any;
const sources = sourcesData as Array<any>;
const PAGE_SIZE = 30;

const normalize = (value: string) =>
  value.normalize("NFKC").toLowerCase().replace(/\s+/g, " ").trim();

const synonymGroups = [
  ["看護師", "看護職員", "准看護師"],
  ["生活相談員", "相談員"],
  ["ハンコ", "判子", "押印", "捺印", "印鑑"],
  ["サイン", "署名", "自署"],
  ["bcp", "業務継続計画"],
  ["デイサービス", "通所介護"],
  ["計画書", "通所介護計画", "計画"],
  ["機能訓練室", "機能訓練"],
  ["常勤換算", "常勤換算方法"],
] as const;

const expandTerm = (term: string) => {
  const normalized = normalize(term);
  const group = synonymGroups.find((items) =>
    items.some((item) => normalize(item) === normalized)
  );
  return group ? group.map((item) => normalize(item)) : [normalized];
};

const serviceOptions = [
  ["", "すべて"],
  ["16", "通所介護"],
  ["06", "通所系共通"],
  ["02", "居宅サービス共通"],
  ["01", "全サービス共通"],
] as const;

export default async function QaPage({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const q = (params.q || "").trim();
  const service = params.service || "";
  const standard = params.standard || "";
  const requestedPage = Math.max(1, Number.parseInt(params.page || "1", 10) || 1);

  const standards = Array.from(
    new Set(qaCorpus.map((item) => item.standard_label).filter(Boolean))
  ).sort((a, b) => a.localeCompare(b, "ja"));

  const terms = normalize(q).split(" ").filter(Boolean);
  const expandedTerms = terms.map(expandTerm);
  const appliedSynonyms = expandedTerms
    .filter((group, index) => group.length > 1 && !group.every((term) => term === terms[index]))
    .flatMap((group) => group)
    .filter((term, index, all) => all.indexOf(term) === index);

  const filtered = qaCorpus.filter((item) => {
    if (service && item.service_code !== service) return false;
    if (standard && item.standard_label !== standard) return false;
    if (!terms.length) return true;

    const haystack = normalize([
      item.scope,
      item.service_label,
      item.standard_label,
      item.topic,
      item.question,
      item.answer,
      item.issued_source,
      item.number,
    ].join(" "));

    return expandedTerms.every((alternatives) =>
      alternatives.some((term) => haystack.includes(term))
    );
  });

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const page = Math.min(requestedPage, totalPages);
  const start = (page - 1) * PAGE_SIZE;
  const visible = filtered.slice(start, start + PAGE_SIZE);
  const officialSource = sources.find((source) => source.id === "mhlw-qa");

  const pageHref = (nextPage: number) => {
    const sp = new URLSearchParams();
    if (q) sp.set("q", q);
    if (service) sp.set("service", service);
    if (standard) sp.set("standard", standard);
    sp.set("page", String(nextPage));
    return `/qa?${sp.toString()}`;
  };

  return (
    <article className="answer-page wide-page qa-corpus-page">
      <p className="eyebrow">MHLW Q&A CORPUS</p>
      <h1>国Q&Aを検索</h1>
      <p className="lead">
        厚生労働省の介護サービス関係Q&Aから、通所介護に関係する範囲を構造化して検索できます。
        現在 {qaMeta.rows_included?.toLocaleString("ja-JP")} 件を収載しています。
      </p>

      <div className="notice">
        <strong>Q&Aの「収載」と「現行性確認」は別です。</strong>
        <br />
        この検索結果は公式Q&A集から取り込んだ内容ですが、個々のQ&Aが現在の法令・通知でも有効かは未確認のものを含みます。
        回答ページの根拠として使うのは、別途確認したものだけです。
      </div>

      <VerificationSummary layerId="qa-corpus" />

      <form className="qa-search-form" method="get" action="/qa">
        <label className="qa-search-main">
          <span>キーワード</span>
          <input name="q" defaultValue={q} placeholder="例：看護職員、送迎、計画、署名" />
        </label>
        <label>
          <span>対象範囲</span>
          <select name="service" defaultValue={service}>
            {serviceOptions.map(([value, label]) => (
              <option key={value || "all"} value={value}>{label}</option>
            ))}
          </select>
        </label>
        <label>
          <span>基準種別</span>
          <select name="standard" defaultValue={standard}>
            <option value="">すべて</option>
            {standards.map((value) => <option key={value} value={value}>{value}</option>)}
          </select>
        </label>
        <button type="submit">検索する</button>
      </form>

      <div className="qa-search-summary">
        <div>
          <p><strong>{filtered.length.toLocaleString("ja-JP")}件</strong> 見つかりました</p>
          {q && appliedSynonyms.length ? (
            <p className="meta">関連語も検索：{appliedSynonyms.join(" / ")}</p>
          ) : null}
        </div>
        {(q || service || standard) ? <Link href="/qa">条件をクリア</Link> : null}
      </div>

      <div className="qa-list">
        {visible.map((item) => (
          <section className="qa-row" key={item.id}>
            <div className="qa-row-head">
              <p className="meta">{item.scope} ・ {item.standard_label || "基準種別なし"}</p>
              <span className="corpus-status">収載済み・現行性未確認</span>
            </div>
            {item.topic ? <p className="qa-topic">{item.topic}</p> : null}
            <h2>{item.question}</h2>
            <p className="qa-answer">{item.answer}</p>
            <p className="meta">{[item.issued_source, item.number].filter(Boolean).join(" / ")}</p>
          </section>
        ))}
        {!visible.length ? (
          <section className="qa-empty">
            <h2>該当するQ&Aが見つかりませんでした</h2>
            <p>語を短くするか、対象範囲・基準種別を「すべて」に戻して検索してください。</p>
          </section>
        ) : null}
      </div>

      {totalPages > 1 ? (
        <nav className="qa-pagination" aria-label="Q&A検索結果のページ">
          {page > 1 ? <Link href={pageHref(page - 1)}>← 前へ</Link> : <span />}
          <span>{page} / {totalPages}ページ</span>
          {page < totalPages ? <Link href={pageHref(page + 1)}>次へ →</Link> : <span />}
        </nav>
      ) : null}

      <section className="section qa-corpus-meta">
        <h2>このデータについて</h2>
        <p>
          公式XLSXの {qaMeta.rows_scanned?.toLocaleString("ja-JP")} 行を走査し、
          「全サービス共通」「居宅サービス共通」「通所系共通」「通所介護」を抽出しています。
        </p>
        <dl>
          {serviceOptions.filter(([code]) => code).map(([code, label]) => (
            <div key={code}><dt>{label}</dt><dd>{qaMeta.counts_by_service?.[code]?.toLocaleString("ja-JP") || 0}件</dd></div>
          ))}
        </dl>
        {officialSource ? (
          <p><a href={officialSource.url} target="_blank" rel="noreferrer">厚生労働省の介護サービス関係Q&Aを確認</a></p>
        ) : null}
        <p className="meta">取得元ファイルのSHA-256も保存し、更新時に同じファイルか確認できるようにしています。</p>
      </section>
    </article>
  );
}
