/** 令和8年度・通所介護の介護職員等処遇改善加算。数値の出典は老発0313第6号・PDF物理18ページの別紙1表1-1／表1-2。
 * これは数値表との照合であり、加算区分の届出・個別の算定要件・後続訂正までを認定したものではない。
 */
export const dayserviceTreatment2026 = {
  amendment: "令和8年厚生労働省告示第87号",
  amendmentUrl: "https://www.mhlw.go.jp/content/12404000/001675895.pdf#page=7",
  noticeUrl: "https://www.mhlw.go.jp/content/12404000/001675724.pdf#page=3",
  ratesUrl: "https://www.mhlw.go.jp/content/12404000/001675724.pdf#page=18",
  qaUrl: "https://www.mhlw.go.jp/content/12404000/001675711.pdf",
  updateIndexUrl: "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000188411_00073.html",
  may: {
    label: "令和8年4月・5月のサービス提供分",
    sourceTable: "別紙1 表1-1",
    rows: [
      { category: "Ⅰ", perThousand: 92 },
      { category: "Ⅱ", perThousand: 90 },
      { category: "Ⅲ", perThousand: 80 },
      { category: "Ⅳ", perThousand: 64 },
    ],
  },
  june: {
    label: "令和8年6月以降のサービス提供分",
    sourceTable: "別紙1 表1-2",
    rows: [
      { category: "Ⅰイ", perThousand: 111 },
      { category: "Ⅰロ", perThousand: 120 },
      { category: "Ⅱイ", perThousand: 109 },
      { category: "Ⅱロ", perThousand: 118 },
      { category: "Ⅲ", perThousand: 99 },
      { category: "Ⅳ", perThousand: 83 },
    ],
  },
} as const;

export function percentOf(perThousand: number): string {
  return (perThousand / 10).toFixed(1) + "%";
}
