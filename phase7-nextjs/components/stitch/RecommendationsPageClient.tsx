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

function friendlyRationale(text: string | undefined): string {
  const s = (text || "").trim();
  if (!s) return "—";
  if (/structured shortlist|automated fallback|llm_disabled|groq_error/i.test(s)) {
    return "Chosen based on your preferences and what’s available in this shortlist.";
  }
  return s;
}

function rankBadge(rank: number): string {
  if (rank === 1) return "Top pick";
  if (rank === 2) return "Strong match";
  if (rank === 3) return "Great fit";
  return `Rank #${rank}`;
}

function RecommendationCard({ rec }: { rec: Recommendation }) {
  return (
    <article className="group glass-card relative cursor-pointer overflow-hidden rounded-2xl transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-[#E23744]/10">
      <div className="flex flex-col gap-3 p-4 sm:gap-3.5 sm:p-5">
        <header className="flex items-center justify-between gap-3">
          <span className="rounded-full bg-[#E23744] px-2.5 py-1 text-[11px] font-bold leading-none text-white shadow-lg shadow-black/30 ai-glow sm:px-3 sm:text-xs">
            {rankBadge(rec.rank)}
          </span>
          <div
            className="flex shrink-0 items-center gap-0.5 text-[#ffb3b1]"
            aria-label={`Rating ${rec.rating} out of 5`}
          >
            <span
              className="material-symbols-outlined text-base"
              style={{ fontVariationSettings: "'FILL' 1" }}
              aria-hidden
            >
              star
            </span>
            <span className="text-sm font-bold tabular-nums">{rec.rating}</span>
          </div>
        </header>

        <div className="min-w-0 space-y-2">
          <h3 className="text-lg font-semibold leading-snug text-white sm:text-xl">{rec.name}</h3>
          <div className="space-y-1 text-sm leading-snug text-zinc-400">
            <p className="break-words">{rec.cuisine}</p>
            <p className="break-words text-zinc-500">
              {rec.estimated_cost}
              {rec.area ? (
                <>
                  <span className="mx-1.5 text-zinc-600" aria-hidden>
                    ·
                  </span>
                  {rec.area}
                </>
              ) : null}
            </p>
          </div>
        </div>

        <div className="flex gap-2.5 rounded-xl border-l-2 border-[#E23744] bg-white/5 p-3 sm:p-3.5">
          <span className="material-symbols-outlined mt-0.5 shrink-0 text-lg text-[#E23744]" aria-hidden>
            auto_awesome
          </span>
          <div className="min-w-0 space-y-1">
            <p className="text-[10px] font-bold uppercase tracking-wider text-[#E23744] sm:text-[11px]">
              Why it matches
            </p>
            <p className="text-xs leading-relaxed text-zinc-300">{friendlyRationale(rec.ai_rationale)}</p>
          </div>
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
  const matchHint =
    typeof stored?.response?.response?.meta?.dining_match_note === "string"
      ? stored.response.response.meta.dining_match_note.trim()
      : "";
  const candidateLine = matchHint || "Personalized dining matches from your latest search.";

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

        <div className="grid grid-cols-1 gap-4 sm:gap-5 lg:grid-cols-2 lg:gap-5 xl:grid-cols-3 xl:gap-6">
          {recs.map((rec) => (
            <RecommendationCard key={`${rec.rank}-${rec.restaurant_id}`} rec={rec} />
          ))}
        </div>

      </main>
    </SiteChrome>
  );
}
