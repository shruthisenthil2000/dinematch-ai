"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { EvalChecklist } from "../components/EvalChecklist";
import { RecommendationCards } from "../components/RecommendationCards";
import { checkRecommendationIntegrity } from "../lib/checks";
import { safetyWarnings } from "../lib/safety";
import type { RecommendRequest, RecommendResponse } from "../lib/types";

export default function HomePage() {
  const [location, setLocation] = useState("Bellandur");
  const [budget, setBudget] = useState<"low" | "medium" | "high">("high");
  const [cuisines, setCuisines] = useState("");
  const [minRating, setMinRating] = useState("4.0");
  const [optionalConstraints, setOptionalConstraints] = useState("Approximate budget around INR 2000 for two.");
  const [cap, setCap] = useState("25");
  const [topN, setTopN] = useState("5");
  const [useLlm, setUseLlm] = useState(true);

  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ kind: "ok" | "warn" | "error"; text: string } | null>(null);
  const [payload, setPayload] = useState<RecommendResponse | null>(null);

  const warnings = useMemo(() => safetyWarnings(optionalConstraints), [optionalConstraints]);

  async function submitRecommendation() {
    setBusy(true);
    setMsg({ kind: "ok", text: "Running recommendation request..." });
    setPayload(null);

    const reqBody: RecommendRequest = {
      preferences: {
        location: location.trim(),
        budget,
        cuisines: cuisines.split(",").map((x) => x.trim()).filter(Boolean),
        min_rating: Number(minRating),
        optional_constraints: optionalConstraints.trim() || undefined,
      },
      cap: Number(cap),
      top_n: Number(topN),
      use_llm: useLlm,
    };

    try {
      const r = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(reqBody),
      });
      const data: RecommendResponse = await r.json();
      if (!r.ok) {
        const txt = data.errors?.join("\n") || data.detail || data.error || `request failed (${r.status})`;
        setMsg({ kind: "error", text: txt });
        return;
      }

      const issues = checkRecommendationIntegrity(reqBody.preferences, reqBody.top_n, data);
      const errCount = issues.filter((i) => i.level === "error").length;
      const warnCount = issues.filter((i) => i.level === "warn").length;

      const issueText = issues.map((i) => `${i.level.toUpperCase()}: ${i.message}`).join("\n");
      if (errCount > 0) {
        setMsg({ kind: "error", text: `Integrity checks failed.\n${issueText}` });
      } else if (warnCount > 0) {
        setMsg({ kind: "warn", text: `Completed with warnings.\n${issueText}` });
      } else {
        setMsg({ kind: "ok", text: "Completed. All implemented integrity checks passed." });
      }
      setPayload(data);
    } catch (err) {
      setMsg({ kind: "error", text: `Unable to reach Phase 7 API proxy. ${String(err)}` });
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <section className="panel">
        <h1>Phase 7 - Evaluation, Safety, and Hardening (Next.js)</h1>
        <p>
          Frontend hardening layer over Phase 5 API. Includes soft safety warnings, correctness/relevance checks,
          and ops-driven runtime config.
        </p>
        <p>
          <Link href="/eval">Open golden-query evaluation page</Link>
        </p>
      </section>

      <section className="panel">
        <div className="grid">
          <div>
            <label>Location</label>
            <input value={location} onChange={(e) => setLocation(e.target.value)} />
          </div>
          <div>
            <label>Budget</label>
            <select value={budget} onChange={(e) => setBudget(e.target.value as "low" | "medium" | "high")}>
              <option value="low">low</option>
              <option value="medium">medium</option>
              <option value="high">high</option>
            </select>
          </div>
          <div>
            <label>Min rating</label>
            <input type="number" min={0} max={5} step={0.1} value={minRating} onChange={(e) => setMinRating(e.target.value)} />
          </div>
          <div>
            <label>Cuisines (comma-separated)</label>
            <input value={cuisines} onChange={(e) => setCuisines(e.target.value)} />
          </div>
          <div>
            <label>Top N</label>
            <input type="number" min={1} value={topN} onChange={(e) => setTopN(e.target.value)} />
          </div>
          <div>
            <label>Candidate cap</label>
            <input type="number" min={1} value={cap} onChange={(e) => setCap(e.target.value)} />
          </div>
        </div>
        <div style={{ marginTop: 12 }}>
          <label>Optional constraints</label>
          <textarea rows={3} value={optionalConstraints} onChange={(e) => setOptionalConstraints(e.target.value)} />
        </div>

        {warnings.length > 0 && (
          <div className="msg warn" style={{ marginTop: 10 }}>
            <strong>Safety soft-check:</strong>
            <ul>
              {warnings.map((w) => <li key={w}>{w}</li>)}
            </ul>
          </div>
        )}

        <div className="row" style={{ marginTop: 12 }}>
          <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input type="checkbox" checked={useLlm} onChange={(e) => setUseLlm(e.target.checked)} style={{ width: 16 }} />
            Use live LLM
          </label>
          <button onClick={submitRecommendation} disabled={busy}>{busy ? "Running..." : "Get recommendations"}</button>
        </div>
      </section>

      {msg && <section className={`msg ${msg.kind}`}>{msg.text}</section>}

      {payload?.response?.comparative_summary && (
        <section className="panel">
          <h2>Comparative summary</h2>
          <p>{payload.response.comparative_summary}</p>
        </section>
      )}

      <section className="panel">
        <h2>Recommendations</h2>
        <RecommendationCards recs={payload?.response?.recommendations ?? []} />
      </section>

      {payload?.observability && (
        <section className="panel">
          <h2>Observability</h2>
          <p className="meta">
            candidates={payload.observability.candidate_count ?? "n/a"} | recommendations={payload.observability.recommendation_count ?? "n/a"} |
            latency={payload.observability.latency_ms?.toFixed?.(1) ?? "n/a"}ms | notes={payload.observability.outcome_notes ?? "n/a"} |
            cache_hit={String(payload.observability.cache_hit ?? "n/a")}
          </p>
        </section>
      )}

      <EvalChecklist />
    </main>
  );
}
