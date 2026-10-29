import { readerTextParagraphs } from "../lib/handbook/dayservice-reader-editorial";

/** Sentence breaks only; this component never edits legal wording or metadata. */
export default function HandbookProse({ text, readable = false }: { text: string; readable?: boolean }) {
  if (!readable) return <p>{text}</p>;
  const example = text.startsWith("計算例：");
  const paragraphs = readerTextParagraphs(text, example ? 1 : 110);
  return <div className={example ? "handbook-prose handbook-calculation-example" : "handbook-prose"}>
    {paragraphs.map((paragraph, index) => <p key={index}>{paragraph}</p>)}
  </div>;
}
