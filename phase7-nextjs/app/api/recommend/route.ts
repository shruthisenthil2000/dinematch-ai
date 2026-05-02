import { NextRequest, NextResponse } from "next/server";

const PHASE5_API_BASE = process.env.PHASE5_API_BASE ?? "http://127.0.0.1:5055";

export async function POST(req: NextRequest) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "invalid_json" }, { status: 400 });
  }

  try {
    const r = await fetch(`${PHASE5_API_BASE}/api/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });

    const payload = await r.json().catch(() => ({ error: "invalid_backend_json" }));
    return NextResponse.json(payload, { status: r.status });
  } catch (err) {
    return NextResponse.json(
      { error: "phase5_unreachable", detail: err instanceof Error ? err.message : String(err) },
      { status: 503 }
    );
  }
}
