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
import { SiteChrome } from "./SiteChrome";

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
  const isNearby = rec.location_tier === "nearby";
  return (
    <article className="group glass-card relative cursor-pointer overflow-hidden rounded-2xl transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-[#E23744]/10">
      <div className="flex flex-col gap-3 p-4 sm:gap-3.5 sm:p-5">
        <header className="flex items-center justify-between gap-3">
          <span className="flex flex-wrap items-center gap-1.5">
            <span className="rounded-full bg-[#E23744] px-2.5 py-1 text-[11px] font-bold leading-none text-white shadow-lg shadow-black/30 ai-glow sm:px-3 sm:text-xs">
              {rankBadge(rec.rank)}
            </span>
            {isNearby ? (
              <span className="rounded-full border border-amber-500/35 bg-amber-500/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-amber-100/95 sm:text-[11px]">
                Nearby
              </span>
            ) : null}
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
          <h3 className="text-lg font-semibold leading-snug themed-text sm:text-xl">{rec.name}</h3>
          <div className="themed-text-secondary space-y-1 text-sm leading-snug">
            <p className="break-words">{rec.cuisine}</p>
            <p className="themed-text-muted break-words">
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

        <div className="flex gap-2.5 rounded-xl border-l-2 border-[#E23744] bg-black/5 p-3 dark:bg-white/5 sm:p-3.5">
          <span className="material-symbols-outlined mt-0.5 shrink-0 text-lg text-[#E23744]" aria-hidden>
            auto_awesome
          </span>
          <div className="min-w-0 space-y-1">
            <p className="text-[10px] font-bold uppercase tracking-wider text-[#E23744] sm:text-[11px]">
              Why it matches
            </p>
            <p className="themed-text-secondary text-xs leading-relaxed">{friendlyRationale(rec.ai_rationale)}</p>
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
  const meta = stored?.response?.response?.meta;
  const selectedArea =
    (typeof meta?.selected_area === "string" && meta.selected_area.trim()) ||
    stored?.request?.preferences?.location?.trim() ||
    "your area";
  const primaryRecs = recs.filter((r) => r.location_tier !== "nearby");
  const nearbyRecs = recs.filter((r) => r.location_tier === "nearby");
  const hasOnlyNearby = nearbyRecs.length > 0 && primaryRecs.length === 0;
  const primaryHeadline = hasOnlyNearby
    ? `No strict matches in ${selectedArea} — see nearby alternatives below.`
    : `Top matches in ${selectedArea}`;
  const candidateLine = [primaryHeadline, matchHint || null].filter(Boolean).join(" · ");

  if (!hydrated) {
    return (
      <div className="themed-bg flex min-h-screen items-center justify-center pt-14 text-zinc-600 dark:text-zinc-400 sm:pt-16">
        <span className="material-symbols-outlined animate-spin text-3xl text-[#E23744]">progress_activity</span>
      </div>
    );
  }

  if (!stored) {
    return (
      <SiteChrome activeNav="recommendations" mainClassName="themed-bg">
        <div className="mx-auto flex min-h-[60vh] max-w-md flex-col items-center justify-center px-6 py-24 text-center sm:max-w-lg">
          <span className="material-symbols-outlined mb-4 text-5xl text-zinc-600">travel_explore</span>
          <h1 className="mb-3 text-2xl font-bold themed-text">No recommendations yet</h1>
          <p className="themed-text-secondary mb-8">
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
    <SiteChrome activeNav="recommendations" mainClassName="themed-bg">
      <main className="mx-auto max-w-5xl px-4 pb-20 pt-8 sm:px-6 sm:pt-10 md:pb-24">
        <header className="mb-10 flex flex-col items-center gap-6 text-center sm:mb-12">
          <div className="max-w-2xl space-y-2">
            <h1 className="text-3xl font-bold tracking-tight themed-text sm:text-4xl md:text-5xl">Curated matches</h1>
            <p className="themed-text-secondary text-sm leading-relaxed sm:text-base">{candidateLine}</p>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-3">
            <button
              type="button"
              onClick={refreshFromApi}
              disabled={busy}
              className="flex items-center gap-2 rounded-xl border themed-border bg-black/5 px-4 py-2.5 text-sm font-semibold themed-text transition-colors hover:bg-black/10 dark:bg-white/5 dark:hover:bg-white/10 disabled:opacity-50"
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
              className="themed-text-secondary rounded-xl border themed-border px-4 py-2.5 text-sm hover:text-zinc-900 dark:hover:text-white"
            >
              Clear saved results
            </button>
          </div>
        </header>

        {stored.statusKind !== "ok" && (
          <div
            className={`mx-auto mb-6 max-w-3xl rounded-2xl border px-4 py-3 text-left text-sm whitespace-pre-wrap ${
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
          <div
            className="mx-auto mb-6 max-w-3xl rounded-2xl border border-red-500/40 bg-red-950/50 px-4 py-3 text-left text-sm text-red-100"
            role="alert"
          >
            {error}
          </div>
        )}

        {busy && (
          <div className="themed-text-secondary mx-auto mb-6 flex max-w-3xl items-center justify-center gap-2 text-sm">
            <span className="material-symbols-outlined animate-spin text-[#E23744]">progress_activity</span>
            Refreshing recommendations…
          </div>
        )}

        {summary && (
          <div className="glass-panel mx-auto mb-10 max-w-3xl rounded-2xl border border-[#E23744]/20 p-5 text-center sm:p-6">
            <h2 className="mb-2 text-sm font-bold uppercase tracking-wider text-[#E23744]">At a glance</h2>
            <p className="text-left text-sm leading-relaxed text-zinc-200 sm:text-base">{summary}</p>
          </div>
        )}

        {!busy && recs.length === 0 && (
          <div className="glass-panel mx-auto mb-10 max-w-xl rounded-2xl border themed-border p-8 text-center">
            <span className="material-symbols-outlined mb-3 text-4xl text-zinc-500">restaurant</span>
            <p className="text-lg font-semibold themed-text">No venues matched these filters</p>
            <p className="themed-text-secondary mt-2 text-sm">
              Try lowering minimum rating, broadening cuisines, or switching budget on the home screen.
            </p>
          </div>
        )}

        {primaryRecs.length > 0 && (
          <div className="mx-auto mb-8 max-w-4xl md:max-w-5xl lg:max-w-6xl">
            <h2 className="themed-text-label mb-4 text-center text-xs font-bold uppercase tracking-wider">
              In {selectedArea}
            </h2>
            <div className="grid grid-cols-1 gap-5 sm:gap-6 md:grid-cols-2 md:gap-6 lg:grid-cols-3">
              {primaryRecs.map((rec) => (
                <RecommendationCard key={`${rec.rank}-${rec.restaurant_id}`} rec={rec} />
              ))}
            </div>
          </div>
        )}

        {nearbyRecs.length > 0 && (
          <div className="mx-auto max-w-4xl md:max-w-5xl lg:max-w-6xl">
            <h2 className="mb-2 text-center text-sm font-bold uppercase tracking-wider text-amber-200/90">
              Nearby alternatives
            </h2>
            <p className="themed-text-muted mb-4 text-center text-xs leading-relaxed">
              Just outside {selectedArea} — same filters, shown because picks in your area were limited.
            </p>
            <div className="grid grid-cols-1 gap-5 sm:gap-6 md:grid-cols-2 md:gap-6 lg:grid-cols-3">
              {nearbyRecs.map((rec) => (
                <RecommendationCard key={`${rec.rank}-${rec.restaurant_id}`} rec={rec} />
              ))}
            </div>
          </div>
        )}
      </main>
    </SiteChrome>
  );
}
