import {
  buildOpsFeedbackHref,
  issueFollowThrough,
  type IssuePath,
} from "../../../lib/issue-follow-through";

export default function ToolFollowThrough({
  issuePath,
  toolPath,
}: {
  issuePath: IssuePath;
  toolPath: string;
}) {
  const config = issueFollowThrough[issuePath];
  const feedbackHref = buildOpsFeedbackHref(issuePath, toolPath);

  return (
    <section className="section boundary">
      <p className="eyebrow">記入後の次の1手</p>
      <h2>一つだけ小さく試し、制度確認と振り返りを分けます。</h2>
      <ol>
        <li>シートから変えることを一つ選び、対象と期間を小さく決めます。</li>
        <li>制度要件に関わる場合は、Kaigo Rulesと一次資料で確認します。</li>
        <li>試した後は、必要なら「何を試したか」「どこで止まったか」「何が足りなかったか」の3点だけ共有します。</li>
      </ol>
      <div className="issueFollowThroughLinks">
        <a className="primaryLink" href={config.rulesHref} target="_blank" rel="noreferrer">
          {config.rulesLabel} →
        </a>
        <a className="textLink" href={`${issuePath}#evidence`}>
          課題ページの根拠へ戻る →
        </a>
        <a className="textLink" href={feedbackHref} target="_blank" rel="noreferrer">
          GitHub Issuesでフィードバックする →
        </a>
      </div>
      <p className="issueFeedbackNote">
        このシートへの記入だけで改善効果や制度適合を確認したことにはなりません。
        フィードバックを送らなくても、上の根拠や制度確認へ進めます。
        GitHub Issuesへの投稿にはGitHubアカウントでのサインインが必要で、投稿内容は公開・保存されます。
        氏名、利用者情報、介護記録、事業所の非公開情報は入力しないでください。
      </p>
    </section>
  );
}
