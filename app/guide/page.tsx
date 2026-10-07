import { pageMetadata } from "../../lib/site-metadata";

export const metadata = pageMetadata("介護制度の使い方ガイド", "介護ルールで制度資料を探し、根拠や確認状態を読み取るための案内です。", "/guide");

import Link from "next/link";
import sourcesData from "../../data/sources.json";
import {
  practicalGuideJourneys,
  practicalGuidePolicy,
  practicalGuideServiceGroups,
} from "../../lib/practical-guide";
import { DEFAULT_SERVICE_ID, getService } from "../../lib/service-catalog";
import { publicSourceFamiliesForService } from "../../lib/public-source-navigation";

type SourceRecord = {
  id: string;
  title: string;
  url: string;
};

const sources = sourcesData as SourceRecord[];
const sourcesById = new Map(sources.map((source) => [source.id, source]));

export default function GuidePage() {
  const serviceDestination = (serviceId: string) => {
    const service = getService(serviceId);
    const publicFamilies = publicSourceFamiliesForService(serviceId);
    if (publicFamilies.length > 0) {
      return {
        href: `/databases/search?service=${encodeURIComponent(serviceId)}`,
        detail:
          "現在公開している" +
          publicFamilies.map((item) => item.short_label).join("・") +
          "を、このサービスの文脈で確認します。",
      };
    }
    if (
      serviceId === DEFAULT_SERVICE_ID ||
      service.routing.future_service_base_enabled
    ) {
      return {
        href: `/services/${encodeURIComponent(serviceId)}`,
        detail: "サービス別に公開している制度情報を確認します。",
      };
    }
    return {
      href: `/databases/search?q=${encodeURIComponent(service.label)}`,
      detail: "サービス名をキーワードに、現在公開している制度DBから関連情報を探します。",
    };
  };

  return (
    <article className="answer-page wide-page">
      <p className="eyebrow">PRACTICAL GUIDE</p>
      <h1>{practicalGuidePolicy.workingLabel}</h1>
      <p className="lead">{practicalGuidePolicy.purpose}</p>

      <div className="notice">
        <strong>このページは、公式な解釈や個別案件の判断を示すものではありません。</strong>
        <br />
        {practicalGuidePolicy.safety}
      </div>

      <section className="section">
        <h2>目的から選ぶ</h2>
        <p>
          サービスを先に決めなくても、確認したい実務テーマから公開済みDBへ進めます。
          表示先で出典・適用範囲・現行性に関する注意を確認してください。
        </p>
        <div className="entry-links">
          {practicalGuideJourneys.map((journey, index) => (
            <Link
              className="entry-row"
              href={`#${journey.id}`}
              key={journey.id}
            >
              <span>
                {String(index + 1).padStart(2, "0")}　{journey.title}
              </span>
              <small>確認する →</small>
            </Link>
          ))}
        </div>
      </section>

      <section className="section">
        <h2>サービスから探す</h2>
        <p>
          通常サービスと対応する介護予防サービスは同じまとまりで表示します。
          利用できるサービス別の公開資料がある場合は横断検索へ進み、それ以外はサービス名で公開DBを検索します。
          介護予防支援は独立したサービスとして扱います。
        </p>
        {practicalGuideServiceGroups.map((group) => (
          <div key={group.id} style={{ marginTop: "24px" }}>
            <h3>{group.title}</h3>
            {group.note ? <p className="meta">{group.note}</p> : null}
            <div className="entry-links">
              {group.serviceIds.map((serviceId) => {
                const service = getService(serviceId);
                const destination = serviceDestination(serviceId);
                return (
                  <Link
                    className="entry-row"
                    href={destination.href}
                    key={serviceId}
                  >
                    <span>
                      {service.label}
                      <small style={{ display: "block", marginTop: "4px" }}>
                        {destination.detail}
                      </small>
                    </span>
                    <small>開く →</small>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </section>

      {practicalGuideJourneys.map((journey, index) => (
        <section className="section" id={journey.id} key={journey.id}>
          <p className="eyebrow">
            GUIDE {String(index + 1).padStart(2, "0")}
          </p>
          <h2>{journey.title}</h2>
          <p>{journey.summary}</p>

          {journey.subJourneys?.length ? (
            <>
              <h3>具体的な確認ルート</h3>
              <div className="entry-links">
                {journey.subJourneys.map((subJourney) => (
                  <Link
                    className="entry-row"
                    href={`#${subJourney.id}`}
                    key={subJourney.id}
                  >
                    <span>
                      {subJourney.title}
                      <small style={{ display: "block", marginTop: "4px" }}>
                        {subJourney.summary}
                      </small>
                    </span>
                    <small>確認する →</small>
                  </Link>
                ))}
              </div>
            </>
          ) : null}

          <h3>まず確認すること</h3>
          <ol className="steps">
            {journey.firstChecks.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ol>

          <h3>DB内で確認する</h3>
          <div className="entry-links">
            {journey.databaseLinks.map((link) => (
              <Link className="entry-row" href={link.href} key={link.href}>
                <span>
                  {link.label}
                  <small style={{ display: "block", marginTop: "4px" }}>
                    {link.detail}
                  </small>
                </span>
                <small>開く →</small>
              </Link>
            ))}
          </div>

          <h3>公式資料へ戻る</h3>
          <ul className="source-list">
            {journey.officialSourceIds.map((sourceId) => {
              const source = sourcesById.get(sourceId);
              if (!source) return null;
              return (
                <li key={sourceId}>
                  <a href={source.url} target="_blank" rel="noreferrer">
                    {source.title}
                  </a>
                </li>
              );
            })}
          </ul>

          {journey.caution ? (
            <div className="notice">{journey.caution}</div>
          ) : null}

          {journey.subJourneys?.map((subJourney) => (
            <section
              className="section"
              id={subJourney.id}
              key={subJourney.id}
              style={{ marginTop: "40px" }}
            >
              <p className="eyebrow">PRACTICAL PATH</p>
              <h3>{subJourney.title}</h3>
              <p>{subJourney.summary}</p>

              <h4>まず確認すること</h4>
              <ol className="steps">
                {subJourney.firstChecks.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ol>

              <h4>DB内で確認する</h4>
              <div className="entry-links">
                {subJourney.databaseLinks.map((link) => (
                  <Link className="entry-row" href={link.href} key={link.href}>
                    <span>
                      {link.label}
                      <small style={{ display: "block", marginTop: "4px" }}>
                        {link.detail}
                      </small>
                    </span>
                    <small>開く →</small>
                  </Link>
                ))}
              </div>

              <h4>公式資料へ戻る</h4>
              <ul className="source-list">
                {subJourney.officialSourceIds.map((sourceId) => {
                  const source = sourcesById.get(sourceId);
                  if (!source) return null;
                  return (
                    <li key={sourceId}>
                      <a href={source.url} target="_blank" rel="noreferrer">
                        {source.title}
                      </a>
                    </li>
                  );
                })}
              </ul>

              {subJourney.caution ? (
                <div className="notice">{subJourney.caution}</div>
              ) : null}
            </section>
          ))}
        </section>
      ))}

      <section className="section">
        <h2>特定サービスから探す場合</h2>
        <p>
          対象サービスが決まっている場合は、サービス別ページから、そのサービスで公開している法令・基準・通知・報酬・Q&Aへ進めます。
        </p>
        <p>
          <Link href="/services">サービス別の公開情報を見る →</Link>
        </p>
      </section>
    </article>
  );
}
