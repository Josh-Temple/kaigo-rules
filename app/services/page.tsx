import Link from "next/link";
import { DEFAULT_SERVICE_ID, listServices, servicePath } from "../../lib/service-catalog";

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

export default function ServicesPage() {
  return (
    <article className="answer-page foundation-page">
      <p className="eyebrow">SERVICES</p>
      <h1>サービス別に制度を見る</h1>
      <p className="lead">
        サービスごとに公開範囲と確認状態を分離しています。あるサービスで確認済みの内容を、別サービスへ自動的に引き継ぎません。
      </p>

      <div className="foundation-list">
        {publicServices.map((service, index) => {
          const href =
            service.service_id === "dayrehab"
              ? servicePath(service.service_id, "/rules")
              : servicePath(service.service_id, "/rules");
          const detail =
            service.service_id === "dayrehab"
              ? "基準省令11条の本文を公開中"
              : "介護保険法・基準・通知・報酬・Q&Aを公開中";
          return (
            <Link className="foundation-row" href={href} key={service.service_id}>
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
        <h2>未公開のサービス</h2>
        <p className="meta">
          データ収集やcanonical統合が進んでいても、公開route・service scope・確認状態の条件を満たすまでは一覧に出しません。
        </p>
      </section>
    </article>
  );
}
