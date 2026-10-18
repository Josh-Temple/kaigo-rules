import { pageMetadata } from "../../lib/site-metadata";

export const metadata = pageMetadata("サービス別手引", "介護サービスの種類から公開中の制度資料と検索ページを探せます。", "/services");

import Link from "next/link";
import { publicServiceNavigationGroups } from "../../lib/service-navigation-groups";

const serviceAccess = (serviceId: string, _label: string) => ({
  href: "/services/" + serviceId,
  label: "全15章の手引を読む →",
});

export default function ServicesPage() {
  const groups = publicServiceNavigationGroups();

  return (
    <article className="answer-page foundation-page">
      <p className="eyebrow">サービス別</p>
      <h1>サービス別の手引</h1>
      <p className="lead">
        行政内部のID順ではなく、利用場面が近いサービスをまとめています。
        39サービスすべてに、開設・人員・設備・運営・報酬など15章の手引があります。対応する介護予防サービスは通常サービスと同じ行からたどれます。
        介護予防支援は独立したサービスとして表示します。
      </p>

      <div className="notice">
        <strong>このまとまりは、探しやすくするための案内上の分類です。</strong><br />
        法令上の新しいサービス分類を示すものではありません。
        各手引には概要・確認項目・関連資料を用意しています。確認前の内容も掲載し、順次追記・調整しています。
      </div>

      <p><Link href="/legislation">法令等を条文順で読み、サービス別に絞り込む →</Link></p>
      <p><Link href="/services/source-map">39サービスの公開資料を種類別に探す →</Link></p>

      {groups.map((group) => (
        <section className="section" key={group.id}>
          <h2>{group.label}</h2>
          <p className="meta">{group.description}</p>
          <div className="foundation-list">
            {group.units.map((unit, unitIndex) => (
              <div
                className="foundation-row foundation-row-static"
                key={unit.service_ids.join("|")}
              >
                <span className="foundation-number">
                  {String(unitIndex + 1).padStart(2, "0")}
                </span>
                <span className="foundation-main">
                  {unit.services.map((service, serviceIndex) => {
                    const access = serviceAccess(service.service_id, service.label);
                    return (
                      <span key={service.service_id}>
                        {serviceIndex > 0 ? <small>介護予防：</small> : null}
                        <strong>
                          <Link href={access.href}>{service.label}</Link>
                        </strong>
                        <small>{access.label}</small>
                      </span>
                    );
                  })}
                </span>
                <span className="foundation-state">
                  <small>{unit.services.length > 1 ? "通常・予防を同じ入口で表示" : "個別に確認"}</small>
                </span>
              </div>
            ))}
          </div>
        </section>
      ))}

      <section className="section">
        <h2>手引の読み方</h2>
        <p>各サービスの目次から章を選び、概要と確認項目を読んでから条文・通知を開けます。法令等の画面では資料の種類・原典・キーワードでも絞り込めます。</p>
        <p><Link href="/legislation">法令等を開く →</Link> ／ <Link href="/qa">国Q&Aを開く →</Link></p>
      </section>
    </article>
  );
}
