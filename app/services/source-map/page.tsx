import Link from "next/link";
import { notFound } from "next/navigation";
import { pageMetadata } from "../../../lib/site-metadata";
import { listServices } from "../../../lib/service-catalog";
import {
  publicServiceNavigationGroups,
  validatePublicServiceNavigation,
} from "../../../lib/service-navigation-groups";
import { publicSourceFamiliesForService } from "../../../lib/public-source-navigation";
import ServiceSourceMap, { type SourceMapGroup } from "../../../components/service-source-map";

export const metadata = pageMetadata(
  "39サービスの公開資料案内",
  "既存のサービス一覧と公開済み資料の対応を検索できます。未公開データや法令解説は表示しません。",
  "/services/source-map",
  false,
);

export default function ServiceSourceMapPage() {
  const services = listServices();
  const validated = validatePublicServiceNavigation();

  // Stay aligned with the complete, current catalog and navigation universe.
  // A catalog mismatch must not silently drop or invent a service.
  if (validated.service_entries !== 39 || services.length !== 39) notFound();

  const byId = new Map(services.map((service) => [service.service_id, service]));
  const groups: SourceMapGroup[] = publicServiceNavigationGroups().map((group) => ({
    id: group.id,
    label: group.label,
    description: group.description,
    units: group.units.map((unit) => ({
      service_ids: unit.service_ids,
      services: unit.services.map((entry) => {
        const service = byId.get(entry.service_id);
        if (!service) throw new Error("Service catalog/navigation mismatch");
        return {
          service_id: entry.service_id,
          label: entry.label,
          // Only this policy-filtered helper grants individual published links.
          public_sources: publicSourceFamiliesForService(entry.service_id),
          detail_href:
            entry.service_id === "dayservice" || entry.service_id === "dayrehab"
              ? `/services/${entry.service_id}`
              : service.routing.future_service_base_enabled
                ? service.routing.future_service_base_path
                : null,
          handbook_href:
            entry.service_id === "dayservice" || entry.service_id === "dayrehab"
              ? `/handbook-sources#${entry.service_id}`
              : null,
        };
      }),
    })),
  }));

  return (
    <article className="answer-page foundation-page">
      <p className="eyebrow">SERVICE SOURCE FINDER</p>
      <h1>39サービスの公開資料を探す</h1>
      <p className="lead">
        既存のサービス一覧と、公開が許可された資料ページを組み合わせた検索画面です。
        サービス名・資料名で絞り込み、公開済みの資料や横断検索へ直接移動できます。
      </p>
      <div className="notice" role="note">
        <strong>資料の所在を探すための入口です。</strong>
        <p>
          掲載数は、そのサービスについて個別の公開リンクが設定された資料の種類数です。
          法令上の適用範囲、最新施行版、算定可否、掲載資料の網羅性や人手レビュー完了を示しません。
          公開リンクのないサービスも一覧から除外しません。
        </p>
        <p>通所介護・通所リハの15章の出典案内は未レビューであり、法令解説の公開ではありません。</p>
      </div>

      <ServiceSourceMap groups={groups} />

      <section className="section">
        <h2>原典の確認について</h2>
        <p>
          サービス別の指定基準、準用・読替え、自治体条例、報酬告示やQ&Aの現行性は、
          リンク先の資料と改正・施行情報で個別に確認してください。
          非公開の草稿本文や未承認の判定結果は、この一覧に表示しません。
        </p>
        <p><Link href="/services">サービス一覧に戻る →</Link></p>
      </section>
    </article>
  );
}
