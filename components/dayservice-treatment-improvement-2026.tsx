import { dayserviceTreatment2026, percentOf } from "../lib/handbook/dayservice-treatment-improvement-2026";

export default function DayserviceTreatmentImprovement2026({ headingLevel = 3 }: { headingLevel?: 2 | 3 }) {
  const Heading = headingLevel === 2 ? "h2" : "h3";
  return <section className="dayservice-treatment-periods" aria-label="令和8年度の通所介護・処遇改善加算の適用月">
    <Heading>令和8年度の加算率：算定する月を確認</Heading>
    <p>通所介護の介護職員等処遇改善加算は、<strong>4月・5月</strong>と<strong>6月以降</strong>で区分・率が異なります。下記は国の通知の率表から通所介護の行だけを抜き出した参考表示です。</p>
    <div className="dayservice-treatment-period-tables">
      {[dayserviceTreatment2026.may, dayserviceTreatment2026.june].map(period =>
        <div key={period.sourceTable}>
          <table>
            <caption>{period.label}（{period.sourceTable}）</caption>
            <thead><tr><th scope="col">加算区分</th><th scope="col">加算率</th></tr></thead>
            <tbody>{period.rows.map(row =>
              <tr key={row.category}><th scope="row">{row.category}</th><td>{percentOf(row.perThousand)}</td></tr>
            )}</tbody>
          </table>
        </div>
      )}
    </div>
    <div className="dayservice-treatment-eligibility" role="note" aria-label="加算区分と算定要件の確認事項">
      <p><strong>区分を選ぶ前の確認事項</strong></p>
      <ul>
        <li>加算は、原則として処遇改善加算自体を除いた<strong>1か月の総単位数</strong>に、サービス種類・区分に応じた率を乗じて算定します。日ごとの単位数に率を掛けて判定する説明ではありません。</li>
        <li>6月以降の<strong>Ⅰロ・Ⅱロ</strong>は、それぞれ<strong>Ⅰイ・Ⅱイの算定要件に加えて、令和8年度特例要件⑧</strong>を満たす必要があります。数字が高いという理由だけでは選べません。</li>
        <li>通所介護に関係する特例要件⑧には、ケアプランデータ連携システムの利用（所定の誓約による取扱いを含む）や、社会福祉連携推進法人への所属があります。<strong>対象サービス・誓約後の実施期限・報告義務</strong>を含め、適用条件を確認してください。</li>
      </ul>
      <p>根拠：
        <a href="https://www.mhlw.go.jp/content/12404000/001675724.pdf#page=3" target="_blank" rel="noreferrer">国通知・単位数の算定</a>、
        <a href="https://www.mhlw.go.jp/content/12404000/001675724.pdf#page=4" target="_blank" rel="noreferrer">区分別の基本要件</a>、
        <a href="https://www.mhlw.go.jp/content/12404000/001675724.pdf#page=8" target="_blank" rel="noreferrer">特例要件⑧</a>。
      </p>
    </div>
    <p className="dayservice-source-caution"><strong>算定前に確認：</strong>率の一致だけで算定できるとは限りません。届出・加算区分の要件、附則、後続の訂正・Q&Aは未照合の部分があります。サービス提供月に対応する
      <a href={dayserviceTreatment2026.ratesUrl} target="_blank" rel="noreferrer">厚生労働省の加算率表</a>、
      <a href={dayserviceTreatment2026.noticeUrl} target="_blank" rel="noreferrer">通知・届出手順</a>、
      <a href="https://www.mhlw.go.jp/shogu-kaizen/apply.html" target="_blank" rel="noreferrer">厚生労働省の令和8年度申請様式案内</a>と所在地の指定権者の案内を確認してください。
    </p>
    <p className="dayservice-source-caution">なお、厚生労働省の改定資料一覧にある「介護給付費算定に係る体制等に関する届出」の別紙様式は、<strong>令和8年6月以降の加算算定用</strong>と案内されています。4月・5月分の届出にそのまま流用せず、<a href={dayserviceTreatment2026.updateIndexUrl} target="_blank" rel="noreferrer">厚生労働省の資料一覧</a>と指定権者の案内で対象月を確認してください。</p>
  </section>;
}
