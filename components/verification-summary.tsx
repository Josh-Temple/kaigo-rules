import registryData from "../data/verification-registry.json";
import { publicVerificationLabel } from "../lib/public-verification";

type VerificationLayer = {
  id: string;
  content_verification?: { status?: string; evidence?: string };
  currentness?: { status?: string; coverage_end?: string };
  human_review?: { status?: string };
};

const registry = registryData as { layers?: VerificationLayer[] };

export default function VerificationSummary({ layerId }: { layerId: string }) {
  const layer = (registry.layers || []).find((item) => item.id === layerId);
  if (!layer) {
    throw new Error("Unknown verification layer: " + layerId);
  }

  return (
    <details className="verification-summary">
      <summary>出典・確認情報</summary>
      <div className="verification-summary-body">
        <dl className="rule-meta">
          <div>
            <dt>本文</dt>
            <dd>{publicVerificationLabel(layer.content_verification?.status, "content")}</dd>
          </div>
          <div>
            <dt>現行性</dt>
            <dd>{publicVerificationLabel(layer.currentness?.status, "currentness")}</dd>
          </div>
          <div>
            <dt>人手確認</dt>
            <dd>{publicVerificationLabel(layer.human_review?.status, "human")}</dd>
          </div>
        </dl>
        <p className="meta">
          現行性確認の対象末日：{layer.currentness?.coverage_end || "各ページの出典情報を参照"}
        </p>
        <p className="meta">
          本文の独立確認、現行性の確認、人手確認は別々に管理しています。未確認の項目を確認済みとして表示しません。
        </p>
      </div>
    </details>
  );
}
