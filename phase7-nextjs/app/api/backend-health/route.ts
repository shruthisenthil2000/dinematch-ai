import { NextResponse } from "next/server";

const PHASE5_API_BASE = process.env.PHASE5_API_BASE ?? "http://127.0.0.1:5055";

export async function GET() {
  try {
    const r = await fetch(`${PHASE5_API_BASE}/health`, { cache: "no-store" });
    const payload = await r.json().catch(() => ({ status: "unknown" }));
    return NextResponse.json(payload, { status: r.status });
  } catch (err) {
    return NextResponse.json(
      { status: "down", detail: err instanceof Error ? err.message : String(err) },
      { status: 503 }
    );
  }
}
