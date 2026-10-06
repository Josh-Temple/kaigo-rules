import Link from "next/link";
import { DEFAULT_SERVICE_ID, listServices, publishedLayerLabels } from "../../lib/service-catalog";

const publicServices = listServices().filter(
  (service) =>
    service.service_id === DEFAULT_SERVICE_ID ||
    service.routing.future_service_base_enabled,
);

const statusLabel = (status: string) => {
  if (status === "ACTIVE_MVP") return "公開中";
  if (status === "ACTIVE_PREVIEW") return "一部公開";
  return "公開情報あり";
};

const serviceLandingHref = (serviceId: string) => "/services/" + serviceId;

export default function ServicesPage() {
  return (
    <article className="answer-page foundation-page">
      <p className="eyebrow">サービス別</p>
      <h1>サービス別に制度を見る</h1>
      <p className="lead">
        特定サービスの制度情報だけを見たいときの入口です。
        サービスを決めずに調べたい場合は、制度DBの横断検索から始められます。
      </p>

      <p><Link href="/databases/search">サービスを選ばずDB全体から検索する →</Link></p>

      <div className="foundation-list">
        {publicServices.map((service, index) => {
          const detail = publishedLayerLabels(service.service_id).join("・") + "を公開中";
          return (
            <Link className="foundation-row" href={serviceLandingHref(service.service_id)} key={service.service_id}>
              <span className="foundation-number">{String(index + 1).padStart(2, "0")}</span>
              <span className="foundation-main">
                <strong>{service.label}</strong>
                <small>{detail}</small>
              </span>
              <span className="foundation-state"><small>{statusLabel(service.status)}</small></span>
            </Link>
          );
        })}
      </div>

      <section className="section">
        <h2>この一覧にないサービス</h2>
        <p className="meta">
          サービス別ページをまだ公開していない場合でも、法令・基準省令・国Q&AなどはDB全体から確認できるものがあります。
          個別サービスとして公開できる範囲は順次増やします。
        </p>
      </section>
    </article>
  );
}
