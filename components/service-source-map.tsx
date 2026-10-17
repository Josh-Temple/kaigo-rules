"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

export type SourceLink = {
  source_family: string;
  label: string;
  short_label: string;
  description: string;
  href: string;
};

export type SourceMapService = {
  service_id: string;
  label: string;
  public_sources: SourceLink[];
  detail_href: string | null;
  handbook_href: string | null;
};

export type SourceMapGroup = {
  id: string;
  label: string;
  description: string;
  units: {
    service_ids: string[];
    services: SourceMapService[];
  }[];
};

export default function ServiceSourceMap({
  groups,
}: {
  groups: SourceMapGroup[];
}) {
  const [query, setQuery] = useState("");
  const [family, setFamily] = useState("all");

  // Filter only already-public routes supplied by the server publication policy.
  // Never infer publication from a catalog entry or an ingested source record.
  const families = useMemo(() => {
    const unique = new Map<string, string>();
    for (const group of groups) {
      for (const unit of group.units) {
        for (const service of unit.services) {
          for (const source of service.public_sources) {
            unique.set(source.source_family, source.short_label);
          }
        }
      }
    }
    return Array.from(unique, ([id, label]) => ({ id, label }));
  }, [groups]);

  const filtered = useMemo(() => {
    const text = query.trim().toLocaleLowerCase("ja-JP");
    return groups
      .map((group) => ({
        ...group,
        units: group.units
          .map((unit) => ({
            ...unit,
            services: unit.services.filter((service) => {
              if (
                family !== "all" &&
                !service.public_sources.some((s) => s.source_family === family)
              ) return false;
              if (!text) return true;
              return [
                service.label,
                service.service_id,
                ...service.public_sources.flatMap((s) => [s.label, s.description]),
              ].some((value) => value.toLocaleLowerCase("ja-JP").includes(text));
            }),
          }))
          .filter((unit) => unit.services.length > 0),
      }))
      .filter((group) => group.units.length > 0);
  }, [groups, family, query]);

  const count = filtered.reduce(
    (total, group) => total + group.units.reduce((n, unit) => n + unit.services.length, 0),
    0,
  );

  return (
    <>
      <div className="section" style={{ display: "flex", flexWrap: "wrap", gap: "1rem", alignItems: "flex-end" }}>
        <div>
          <label htmlFor="service-source-query"><strong>サービス名・資料名で検索</strong></label>
          <input
            id="service-source-query"
            type="search"
            autoComplete="off"
            placeholder="例：訪問介護、基準省令"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            style={{ display: "block", maxWidth: "100%", padding: "0.6rem", marginTop: "0.4rem" }}
          />
        </div>
        <div>
          <label htmlFor="service-source-family"><strong>公開資料の種類</strong></label>
          <select
            id="service-source-family"
            value={family}
            onChange={(event) => setFamily(event.target.value)}
            style={{ display: "block", maxWidth: "100%", padding: "0.6rem", marginTop: "0.4rem" }}
          >
            <option value="all">すべてのサービス</option>
            {families.map((source) => (
              <option key={source.id} value={source.id}>{source.label}</option>
            ))}
          </select>
        </div>
        <button type="button" onClick={() => { setQuery(""); setFamily("all"); }}>
          条件をクリア
        </button>
      </div>

      <p className="meta" aria-live="polite">
        {count}サービスを表示しています。資料リンクは公開済みの範囲のみです。
      </p>

      {filtered.length === 0 ? (
        <p role="status">該当するサービスがありません。条件を変更するか、DB全体から検索してください。</p>
      ) : filtered.map((group) => (
        <section className="section" key={group.id}>
          <h2>{group.label}</h2>
          <p className="meta">{group.description}</p>
          <div className="foundation-list">
            {group.units.map((unit) => (
              <div key={unit.service_ids.join("|")} className="foundation-row foundation-row-static">
                <span className="foundation-main">
                  {unit.services.map((service) => (
                    <span key={service.service_id} style={{ display: "block", marginBottom: "0.9rem" }}>
                      <strong>{service.label}</strong>
                      <small>公開資料への入口：{service.public_sources.length}種類</small>
                      <span style={{ display: "flex", flexWrap: "wrap", gap: "0.55rem", marginTop: "0.35rem" }}>
                        {service.public_sources.map((source) => (
                          <Link key={source.source_family} href={source.href}>
                            {source.short_label} →
                          </Link>
                        ))}
                        <Link href={`/databases/search?service=${encodeURIComponent(service.service_id)}`}>
                          公開DBを検索 →
                        </Link>
                        {service.detail_href ? (
                          <Link href={service.detail_href}>サービス別ページ →</Link>
                        ) : null}
                        {service.handbook_href ? (
                          <Link href={service.handbook_href}>15章の出典案内（未レビュー） →</Link>
                        ) : null}
                      </span>
                      {service.public_sources.length === 0 ? (
                        <small>個別の公開資料リンクは未設定です。資料が存在しないという意味ではありません。</small>
                      ) : null}
                    </span>
                  ))}
                </span>
              </div>
            ))}
          </div>
        </section>
      ))}
    </>
  );
}
