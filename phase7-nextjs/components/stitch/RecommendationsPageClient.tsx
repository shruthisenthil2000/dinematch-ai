"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { checkRecommendationIntegrity } from "../../lib/checks";
import {
  clearStoredRecommend,
  readStoredRecommend,
  writeStoredRecommend,
  type StoredRecommendResult,
} from "../../lib/recommendSession";
import type { Recommendation, RecommendResponse } from "../../lib/types";
import { InsightsAside, SiteChrome } from "./SiteChrome";

function rankBadge(rank: number): string {
  if (rank === 1) return "Top pick";
  if (rank === 2) return "Strong match";
  if (rank === 3) return "Great fit";
  return `Rank #${rank}`;
}

function RecommendationCard({ rec }: { rec: Recommendation }) {
  const initial = (rec.name || "?").slice(0, 1).toUpperCase();
  return (
    <article className="group glass-card relative cursor-pointer overflow-hidden rounded-2xl transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl hover:shadow-[#E23744]/10">
      <div className="relative aspect-[16/10] overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[#E23744]/30 via-zinc-900 to-black" />
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-5xl font-black text-white/20">{initial}</span>
        </div>
        <div className="absolute right-4 top-4 rounded-full bg-[#E23744] px-3 py-1 text-xs font-bold text-white shadow-lg ai-glow">
          {rankBadge(rec.rank)}
        </div>
      </div>
      <div className="p-5 sm:p-6">
        <div className="mb-2 flex items-start justify-between gap-2">
          <h3 className="text-lg font-semibold leading-snug text-white sm:text-xl">{rec.name}</h3>
          <div className="flex shrink-0 items-center text-[#ffb3b1]">
            <span
              className="material-symbols-outlined text-sm"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              star
            </span>
            <span className="ml-1 text-sm font-bold">{rec.rating}</span>
          </div>
        </div>
        <p className="mb-4 text-sm text-zinc-400">
          {rec.cuisine} · {rec.estimated_cost}
        </p>
        <div className="mb-4 flex flex-wrap gap-2">
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-zinc-300">
            Listing {rec.restaurant_id}
          </span>
        </div>
        <div className="flex gap-3 rounded-xl border-l-2 border-[#E23744] bg-white/5 p-4">
          <span className="material-symbols-outlined text-xl text-[#E23744]">auto_awesome</span>
          <p className="text-xs leading-relaxed text-zinc-300">{rec.ai_rationale || "—"}</p>
        </div>
      </div>
    </article>
  );
}

export function RecommendationsPageClient() {
  const router = useRouter();
  const [stored, setStored] = useState<StoredRecommendResult | null>(null);
  const [hydrated, setHydrated] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadFromSession = useCallback(() => {
    setStored(readStoredRecommend());
    setHydrated(true);
  }, []);

  useEffect(() => {
    loadFromSession();
  }, [loadFromSession]);

  async function refreshFromApi() {
    if (!stored?.request) return;
    setBusy(true);
    setError(null);
    try {
      const r = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(stored.request),
      });
      const data: RecommendResponse = await r.json();
      if (!r.ok) {
        setError(data.errors?.join("\n") || data.detail || data.error || `Request failed (${r.status})`);
        return;
      }
      const issues = checkRecommendationIntegrity(stored.request.preferences, stored.request.top_n, data);
      const errCount = issues.filter((i) => i.level === "error").length;
      const warnCount = issues.filter((i) => i.level === "warn").length;
      const issueText = issues.map((i) => `${i.level.toUpperCase()}: ${i.message}`).join("\n");
      let statusKind: "ok" | "warn" | "error" = "ok";
      let statusText = "All set — your personalized matches look consistent with your preferences.";
      if (errCount > 0) {
        statusKind = "error";
        statusText = `We spotted an issue with these results.\n${issueText}`;
      } else if (warnCount > 0) {
        statusKind = "warn";
        statusText = `Your matches are ready, with a few notes to review.\n${issueText}`;
      }
      const next: StoredRecommendResult = {
        request: stored.request,
        response: data,
        integrityIssues: issues,
        statusKind,
        statusText,
        fetchedAt: new Date().toISOString(),
      };
      writeStoredRecommend(next);
      setStored(next);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  const recs = stored?.response?.response?.recommendations ?? [];
  const summary = stored?.response?.response?.comparative_summary;
  const obs = stored?.response?.observability;
  const candidateLine =
    typeof obs?.candidate_count === "number"
      ? `We reviewed ${obs.candidate_count} place${obs.candidate_count === 1 ? "" : "s"} before choosing these picks.`
      : "Personalized dining matches from your latest search.";

  if (!hydrated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0F0F0F] pt-16 text-zinc-400">
        <span className="material-symbols-outlined animate-spin text-3xl text-[#E23744]">progress_activity</span>
      </div>
    );
  }

  if (!stored) {
    return (
      <SiteChrome activeNav="recommendations" mainClassName="bg-[#0F0F0F]">
        <div className="mx-auto flex min-h-[60vh] max-w-lg flex-col items-center justify-center px-6 py-24 text-center">
          <span className="material-symbols-outlined mb-4 text-5xl text-zinc-600">travel_explore</span>
          <h1 className="mb-3 text-2xl font-bold text-white">No recommendations yet</h1>
          <p className="mb-8 text-zinc-400">
            Run a search from the home preferences screen. Your curated matches appear here after each successful
            search.
          </p>
          <Link
            href="/"
            className="accent-gradient rounded-2xl px-8 py-3 text-sm font-bold text-white shadow-lg shadow-red-900/30"
          >
            Set preferences
          </Link>
        </div>
      </SiteChrome>
    );
  }

  return (
    <SiteChrome
      activeNav="recommendations"
      aside={
        <InsightsAside>
          <div className="rounded-lg border-l-2 border-[#E23744] bg-[#E23744]/10 p-3 font-medium text-[#E23744]">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined">psychology</span>
              <span className="text-sm">Fresh results</span>
            </div>
          </div>
          {summary && (
            <p className="rounded-xl border border-white/10 bg-white/5 p-3 text-sm leading-relaxed text-zinc-300">
              {summary}
            </p>
          )}
          {!summary && recs[0]?.ai_rationale && (
            <p className="rounded-xl border border-white/10 bg-white/5 p-3 text-sm leading-relaxed text-zinc-300">
              {recs[0].ai_rationale}
            </p>
          )}
        </InsightsAside>
      }
      mainClassName="bg-[#0F0F0F]"
    >
      <main className="mx-auto max-w-[1600px] px-4 pb-16 pt-8 md:px-8 md:pt-10">
        <header className="mb-10 flex flex-col gap-4 sm:mb-12 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="mb-2 text-3xl font-bold tracking-tight text-white sm:text-4xl md:text-5xl">Curated matches</h1>
            <p className="max-w-2xl text-sm text-zinc-400 sm:text-base">{candidateLine}</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={refreshFromApi}
              disabled={busy}
              className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-white/10 disabled:opacity-50"
            >
              <span className={`material-symbols-outlined text-lg ${busy ? "animate-spin" : ""}`}>
                {busy ? "progress_activity" : "refresh"}
              </span>
              Refresh
            </button>
            <Link
              href="/"
              className="flex items-center gap-2 rounded-xl border border-[#E23744]/40 bg-[#E23744]/10 px-4 py-2.5 text-sm font-semibold text-[#ffb3b1] transition-colors hover:bg-[#E23744]/20"
            >
              <span className="material-symbols-outlined text-lg">edit</span>
              New search
            </Link>
            <button
              type="button"
              onClick={() => {
                clearStoredRecommend();
                router.push("/");
              }}
              className="rounded-xl border border-white/10 px-4 py-2.5 text-sm text-zinc-400 hover:text-white"
            >
              Clear saved results
            </button>
          </div>
        </header>

        {stored.statusKind !== "ok" && (
          <div
            className={`mb-6 rounded-2xl border px-4 py-3 text-sm whitespace-pre-wrap ${
              stored.statusKind === "error"
                ? "border-red-500/40 bg-red-950/50 text-red-100"
                : "border-amber-500/40 bg-amber-950/40 text-amber-100"
            }`}
            role="status"
          >
            {stored.statusText}
          </div>
        )}

        {error && (
          <div className="mb-6 rounded-2xl border border-red-500/40 bg-red-950/50 px-4 py-3 text-sm text-red-100" role="alert">
            {error}
          </div>
        )}

        {busy && (
          <div className="mb-6 flex items-center gap-2 text-sm text-zinc-400">
            <span className="material-symbols-outlined animate-spin text-[#E23744]">progress_activity</span>
            Refreshing recommendations…
          </div>
        )}

        {summary && (
          <div className="glass-panel mb-10 rounded-2xl border border-[#E23744]/20 p-5 sm:p-6">
            <h2 className="mb-2 text-sm font-bold uppercase tracking-wider text-[#E23744]">At a glance</h2>
            <p className="text-sm leading-relaxed text-zinc-200 sm:text-base">{summary}</p>
          </div>
        )}

        {!busy && recs.length === 0 && (
          <div className="glass-panel mb-10 rounded-2xl border border-white/10 p-8 text-center">
            <span className="material-symbols-outlined mb-3 text-4xl text-zinc-500">restaurant</span>
            <p className="text-lg font-semibold text-white">No venues matched these filters</p>
            <p className="mt-2 text-sm text-zinc-400">
              Try lowering minimum rating, broadening cuisines, or switching budget on the home screen.
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2 xl:grid-cols-3">
          {recs.map((rec) => (
            <RecommendationCard key={`${rec.rank}-${rec.restaurant_id}`} rec={rec} />
          ))}
        </div>

        {obs && (
          <div className="mt-12 rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-4 text-xs text-zinc-500 sm:text-sm">
            <span className="font-semibold text-zinc-400">How this match was built</span>
            <span className="mx-2 text-zinc-700">·</span>
            <span>
              {[
                typeof obs.candidate_count === "number" ? `${obs.candidate_count} places considered` : null,
                `${obs.recommendation_count ?? recs.length} picks shown`,
                typeof obs.latency_ms === "number" ? `Ready in about ${(obs.latency_ms / 1000).toFixed(1)}s` : null,
              ]
                .filter(Boolean)
                .join(" · ")}
            </span>
          </div>
        )}
      </main>
    </SiteChrome>
  );
}
