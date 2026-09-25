import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const response = NextResponse.json({
    service: "kaigo-rules",
    commit_sha: process.env.VERCEL_GIT_COMMIT_SHA ?? null,
    commit_ref: process.env.VERCEL_GIT_COMMIT_REF ?? null,
  });

  response.headers.set("Cache-Control", "no-store, max-age=0");
  return response;
}
