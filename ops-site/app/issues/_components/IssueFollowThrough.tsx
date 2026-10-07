import {
  buildOpsFeedbackHref,
  issueFollowThrough,
  RULES_HOME_HREF,
  type IssuePath,
} from "../../../lib/issue-follow-through";

export default function IssueFollowThrough({ issuePath }: { issuePath: IssuePath }) {
  const config = issueFollowThrough[issuePath];
  const feedbackHref = buildOpsFeedbackHref(issuePath);

  return (
    <div className="issueFollowThrough">
      <p className="issueFollowThroughLabel">次に確認する</p>
      <p>
        改善を始める前に、制度上必要な範囲を確認してください。
        Kaigo Opsでは制度上の適否を自動判定せず、サービス種別に応じて、
        介護ルールに表示される検証状態と該当する一次資料を確認します。
      </p>
      <div className="issueFollowThroughLinks">
        <a className="primaryLink" href={config.rulesHref} target="_blank" rel="noreferrer">
          {config.rulesLabel} →
        </a>
        <a className="textLink" href={RULES_HOME_HREF} target="_blank" rel="noreferrer">
          介護ルールのトップを見る →
        </a>
      </div>

      <div className="issueFeedback">
        <strong>試した結果を返す</strong>
        <p>
          「何を試したか」「どこで止まったか」「何が足りなかったか」の3点だけでも構いません。
        </p>
        <a className="textLink" href={feedbackHref} target="_blank" rel="noreferrer">
          GitHub Issuesでフィードバックする →
        </a>
        <p className="issueFeedbackNote">
          リンク先はGitHub Issuesです。投稿するとGitHub上で公開・保存され、サインインが必要です。
          Kaigo Ops内では入力・自動保存しません。氏名、利用者情報、介護記録、事業所の非公開情報は入力しないでください。
        </p>
      </div>
    </div>
  );
}
