import Link from "next/link";
import { DEFAULT_SERVICE_ID, listServices, publishedLayerLabels } from "../../lib/service-catalog";

const publicServices = listServices().filter(
  (service) =>
    service.service_id === DEFAULT_SERVICE_ID ||
    service.routing.future_service_base_enabled,
);

const statusLabel = (status: string) => {
  if (status === "ACTIVE_MVP") return "公開中";
  if (status === "ACTIVE_PREVIEW") return "プレビュー";
  return status;
};

const serviceLandingHref = (serviceId: string) => `/services/${serviceId}`;

export default function ServicesPage() {
  return (
    <article className="answer-page foundation-page">
      <p className="eyebrow">SERVICES</p>
      <h1>サービス別に制度を見る</h1>
      <p className="lead">
        まず対象サービスを選び、そのサービスで公開している法令・基準・通知・報酬・Q&Aへ進みます。
        公開範囲と確認状態はサービスごとに分離し、別サービスの確認結果を自動的に引き継ぎません。
      </p>

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
        <h2>整備中のサービス</h2>
        <p className="meta">
          資料の収集や構造化が進んでいても、サービス固有の公開範囲と確認状態が整うまでは公開サービス一覧に出しません。
          新しいサービスを追加するときも、この一覧を共通の入口にします。
        </p>
      </section>
    </article>
  );
}
