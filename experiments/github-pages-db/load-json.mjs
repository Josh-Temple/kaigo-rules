// Prefer the losslessly compressed global index; keep an uncompressed fallback
// for browsers without DecompressionStream or hosts with unusual gzip handling.
export async function loadJson(file, { fetcher = (...args) => globalThis.fetch(...args), decompress = globalThis.DecompressionStream } = {}) {
  if (file.endsWith("/global.json") && typeof decompress === "function") {
    try {
      const compressed = await fetcher(file + ".gz");
      if (!compressed.ok || !compressed.body) throw new Error("compressed data unavailable");
      return await new Response(compressed.body.pipeThrough(new decompress("gzip"))).json();
    } catch {
      // Do not weaken search or drop records when compression is unavailable.
    }
  }
  const response = await fetcher(file);
  if (!response.ok) throw new Error("データを読み込めませんでした。");
  return await response.json();
}
