export const qaDetailHref = (id: string) => `/qa/${encodeURIComponent(id)}`;
export const noticeDetailHref = (id: string) => `/notices/${encodeURIComponent(id)}`;
export const officialRuleHref = (url: string, id: string) => {
  const article = id.match(/article([0-9-]+)/)?.[1];
  if (article && url.includes("mhlw.go.jp/web/t_doc")) {
    const digits = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九"];
    const kanji = (n: number): string => n >= 100 ? (n >= 200 ? digits[Math.floor(n / 100)] : "") + "百" + kanji(n % 100) : n >= 10 ? (n >= 20 ? digits[Math.floor(n / 10)] : "") + "十" + digits[n % 10] : digits[n];
    const parts = article.split("-").map(Number);
    const title = `第${kanji(parts[0])}条${parts.slice(1).map(n => "の" + kanji(n)).join("")}`;
    return `${url.split("#")[0]}#:~:text=${encodeURIComponent(title)}`;
  }
  return article && url.includes("laws.e-gov.go.jp") ? `${url.split("#")[0]}#Mp-At_${article.replaceAll("-", "_")}` : url;
};
