import { pageMetadata } from "../../lib/site-metadata";

export const metadata = pageMetadata("サービスから探す", "介護サービスの種類から公開中の制度資料と検索ページを探せます。", "/services");

import Link from "next/link";
import { DEFAULT_SERVICE_ID, listServices } from "../../lib/service-catalog";
import { publicServiceNavigationGroups } from "../../lib/service-navigation-groups";
import { publicSourceFamiliesForService } from "../../lib/public-source-navigation";

const dedicatedServiceIds = new Set(
  listServices()
    .filter(
      (service) =>
        service.service_id === DEFAULT_SERVICE_ID ||
        service.routing.future_service_base_enabled,
    )
    .map((service) => service.service_id),
);

const serviceAccess = (serviceId: string, label: string) => {
  if (dedicatedServiceIds.has(serviceId)) {
    return {
      href: "/services/" + serviceId,
      label: "サービス別ページ",
    };
  }
  const publicFamilies = publicSourceFamiliesForService(serviceId);
  if (publicFamilies.length > 0) {
    return {
      href: "/databases/search?service=" + encodeURIComponent(serviceId),
      label:
        publicFamilies.length > 1
          ? "公開中の一次資料を横断"
          : publicFamilies[0].short_label + "を確認",
    };
  }
  return {
    href: "/databases/search?q=" + encodeURIComponent(label),
    label: "DB全体から名称検索",
  };
};

export default function ServicesPage() {
  const groups = publicServiceNavigationGroups();

  return (
    <article className="answer-page foundation-page">
      <p className="eyebrow">サービス別</p>
      <h1>サービスから制度情報を探す</h1>
      <p className="lead">
        行政内部のID順ではなく、利用場面が近いサービスをまとめています。
        対応する介護予防サービスは通常サービスと同じ行からたどれます。
        介護予防支援は独立したサービスとして表示します。
      </p>

      <div className="notice">
        <strong>このまとまりは、探しやすくするための案内上の分類です。</strong><br />
        法令上の新しいサービス分類を示すものではありません。
        サービス別ページや公開済み資料の絞り込みがある場合はそこへ進み、まだない場合も名称を使って公開中のDB全体を検索できます。
      </div>

      <p><Link href="/databases/search">サービスを選ばずDB全体から検索する →</Link></p>

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
        <h2>個別ページがまだない場合</h2>
        <p className="meta">
          「DB全体から名称検索」は、サービス固有の公開範囲が完成したことを意味しません。
          検索結果が少ない場合も、制度資料そのものが存在しないとは限りません。
          必要に応じてDB一覧や公式の一次資料も確認してください。
        </p>
        <p>
          <Link href="/databases">制度DB一覧を見る →</Link>
          {" / "}
          <Link href="/sources">公式の根拠資料を見る →</Link>
        </p>
      </section>
    </article>
  );
}
