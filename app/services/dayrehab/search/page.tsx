import Link from "next/link";
import nodes from "../../../../data/ordinance37-nodes.json";
import { filterRecordsForService } from "../../../../lib/service-scope";
export default async function Search({searchParams}: {searchParams: Promise<{q?:string}>}) {
 const {q=""} = await searchParams;
 const scoped = filterRecordsForService("dayrehab", "ordinance37", nodes, node => node.id);
 const terms = q.normalize("NFKC").split(/\s+/).filter(Boolean);
 const hits = scoped.filter((node:any) => node.node_type === "article" && terms.every(term => JSON.stringify(node).normalize("NFKC").includes(term)));
 return <article className="answer-page"><p className="eyebrow">通所リハビリテーション</p><h1>通所リハビリテーションを検索</h1>
 <p className="scope-note">この検索は通所リハの基準省令に限定しています。通所介護のFAQ・Q&Aは混ぜていません。通知・報酬・算定留意事項は以下の出典別一覧へ進んでください。</p>
 <form action="/services/dayrehab/search"><label>キーワード<input name="q" defaultValue={q}/></label><button>検索する</button></form>
 <div className="rules-list">{hits.map((node:any) => <Link className="rule-row" key={node.id} href={`/services/dayrehab/rules/${node.article_num}`}>{node.article_title} {node.caption} / {node.id}</Link>)}</div>
 <p><Link href="/services/dayrehab/notices">通所リハの解釈通知</Link></p><p><Link href="/services/dayrehab/remuneration">通所リハの報酬基準</Link></p><p><Link href="/services/dayrehab/remuneration/guidance">通所リハの算定上の留意事項</Link></p></article>;
}
