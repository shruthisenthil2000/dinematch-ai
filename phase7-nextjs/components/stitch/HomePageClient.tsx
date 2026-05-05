"use client";

import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { checkRecommendationIntegrity } from "../../lib/checks";
import { writeStoredRecommend } from "../../lib/recommendSession";
import { safetyWarnings } from "../../lib/safety";
import type { RecommendRequest, RecommendResponse } from "../../lib/types";
import { SiteChrome } from "./SiteChrome";

const LOCATION_OPTIONS = [
  "Bellandur",
  "Koramangala",
  "Indiranagar",
  "Whitefield",
  "HSR Layout",
  "Marathahalli",
  "Electronic City",
  "MG Road",
  "Jayanagar",
] as const;

const BUDGET_OPTIONS: {
  value: "low" | "medium" | "high";
  title: string;
  range: string;
}[] = [
  { value: "low", title: "Budget Friendly", range: "₹500–₹1500" },
  { value: "medium", title: "Mid Range", range: "₹1500–₹3000" },
  { value: "high", title: "Premium", range: "₹3000+" },
];

/** Shown as the notes field placeholder only; value stays empty until the user types. */
const DINING_NOTES_PLACEHOLDER =
  "Choose your preferred dining budget for two. Add occasion, dietary needs, or vibe if you like.";

export function HomePageClient() {
  const router = useRouter();
  const [location, setLocation] = useState("Bellandur");
  const [budget, setBudget] = useState<"low" | "medium" | "high">("high");
  const [cuisines, setCuisines] = useState("");
  const [minRating, setMinRating] = useState(4);
  const [optionalConstraints, setOptionalConstraints] = useState("");
  const [cap, setCap] = useState(25);
  const [topN, setTopN] = useState(5);
  const [useLlm, setUseLlm] = useState(true);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [busy, setBusy] = useState(false);
  const [inlineError, setInlineError] = useState<string | null>(null);

  const warnings = useMemo(() => safetyWarnings(optionalConstraints), [optionalConstraints]);

  async function submitRecommendation() {
    setBusy(true);
    setInlineError(null);

    const reqBody: RecommendRequest = {
      preferences: {
        location: location,
        budget,
        cuisines: cuisines
          .split(",")
          .map((x) => x.trim())
          .filter(Boolean),
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
        const txt = data.errors?.join("\n") || data.detail || data.error || `Request failed (${r.status})`;
        setInlineError(txt);
        return;
      }

      const issues = checkRecommendationIntegrity(reqBody.preferences, reqBody.top_n, data);
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

      writeStoredRecommend({
        request: reqBody,
        response: data,
        integrityIssues: issues,
        statusKind,
        statusText,
        fetchedAt: new Date().toISOString(),
      });
      router.push("/recommendations");
    } catch (err) {
      setInlineError("We couldn’t reach the recommendation service. Please try again in a moment.");
    } finally {
      setBusy(false);
    }
  }

  const filledStars = Math.min(5, Math.round(minRating));

  return (
    <SiteChrome activeNav="home" showFooter={false} mainClassName="bg-[#0F0F0F] md:flex md:flex-col">
      <main className="flex w-full flex-1 flex-col max-md:min-h-0 max-md:overflow-y-auto md:min-h-0 md:max-h-[calc(100dvh-4rem)] md:justify-center md:gap-1 md:overflow-y-auto md:overflow-x-hidden md:px-4 lg:px-6">
        <section className="relative flex w-full shrink-0 flex-col items-center justify-center px-4 pb-3 pt-5 hero-bg sm:pb-4 sm:pt-6 md:min-h-0 md:py-2 md:pb-1">
          <div className="hero-overlay absolute inset-0" />
          <div className="relative z-10 mx-auto w-full max-w-2xl px-2 text-center">
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 backdrop-blur-md sm:mb-3.5 sm:px-3.5">
              <span className="material-symbols-outlined text-sm text-[#E23744]">verified</span>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-400 sm:text-[11px]">
                AI-powered dining
              </span>
            </div>
            <h1 className="mb-2 text-2xl font-bold leading-[1.12] tracking-tight text-white sm:text-3xl md:mb-2 md:text-4xl">
              Find your perfect meal
              <br />
              <span className="text-[#ffb3b1]">with AI precision</span>
            </h1>
            <p className="mx-auto max-w-md text-xs leading-relaxed text-zinc-400 sm:text-sm md:text-sm">
              Tell us where, your budget, and what you crave — we match you to places worth the reservation.
            </p>
          </div>
        </section>

        <section className="relative z-20 -mt-6 px-4 pb-8 sm:-mt-8 sm:px-5 sm:pb-10 md:-mt-7 md:mt-0 md:shrink md:px-0 md:pb-4">
          <div className="mx-auto w-full max-w-3xl">
            <div className="glass-panel rounded-2xl border-white/[0.08] p-4 shadow-[0_20px_60px_rgba(0,0,0,0.42)] sm:rounded-3xl sm:p-5 md:p-5">
            {warnings.length > 0 && (
              <div className="mb-4 rounded-xl border border-amber-500/25 bg-amber-500/[0.08] p-3 text-left text-xs text-amber-100/95 sm:p-4 sm:text-sm">
                <p className="mb-1.5 font-semibold text-amber-200">Safety note</p>
                <ul className="list-inside list-disc space-y-1 text-amber-100/90">
                  {warnings.map((w) => (
                    <li key={w}>{w}</li>
                  ))}
                </ul>
              </div>
            )}
            <div className="relative mb-5 sm:mb-6">
              <div className="absolute -left-0.5 -top-1.5 sm:-left-2 sm:-top-2 md:hidden">
                <span className="relative flex h-5 w-5">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#E23744] opacity-20" />
                  <span className="relative inline-flex h-5 w-5 items-center justify-center rounded-full bg-[#E23744]">
                    <span className="material-symbols-outlined text-[12px] text-white">auto_awesome</span>
                  </span>
                </span>
              </div>
              <div className="absolute -left-0.5 -top-1.5 hidden sm:-left-2 sm:-top-2 md:block">
                <span className="relative inline-flex h-5 w-5 items-center justify-center rounded-full bg-[#E23744]">
                  <span className="material-symbols-outlined text-[12px] text-white">auto_awesome</span>
                </span>
              </div>
              <span id="optional-constraints-desc" className="sr-only">
                Optional free-text dining preferences. Leave blank or describe budget for two, dietary needs,
                occasion, or vibe.
              </span>
              <label className="sr-only" htmlFor="optional-constraints">
                Dining notes
              </label>
              <input
                id="optional-constraints"
                type="text"
                autoComplete="off"
                aria-describedby="optional-constraints-desc"
                className="h-12 w-full rounded-2xl border border-white/10 bg-white/5 px-4 pb-5 pt-2 text-sm text-white placeholder:text-zinc-500 focus:border-[#E23744]/50 focus:outline-none focus:ring-2 focus:ring-[#E23744]/30 sm:h-[52px] sm:px-5 sm:pb-5 sm:pt-2 sm:text-base"
                placeholder={DINING_NOTES_PLACEHOLDER}
                value={optionalConstraints}
                onChange={(e) => setOptionalConstraints(e.target.value)}
              />
              <p className="pointer-events-none absolute bottom-2 right-3 text-[10px] font-medium uppercase tracking-widest text-zinc-500 sm:bottom-2.5 sm:right-4">
                Your notes
              </p>
            </div>

            <div className="mb-5 grid grid-cols-1 gap-3 md:mb-5 md:grid-cols-3 md:gap-3">
              <div className="group rounded-2xl border border-white/5 bg-white/5 p-3 transition-all hover:border-white/10 sm:p-3.5">
                <div className="mb-2 flex items-center gap-2">
                  <span className="material-symbols-outlined text-xl text-[#E23744]">location_on</span>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-500">Area</span>
                </div>
                <div className="relative">
                  <select
                    id="dining-location"
                    className="w-full cursor-pointer appearance-none rounded-xl border border-white/10 bg-[#141414] py-2.5 pl-3 pr-10 text-sm font-semibold text-white shadow-inner focus:border-[#E23744]/50 focus:outline-none focus:ring-2 focus:ring-[#E23744]/25 sm:text-base"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    aria-label="Neighborhood or area"
                  >
                    {LOCATION_OPTIONS.map((opt) => (
                      <option key={opt} value={opt} className="bg-[#141414] text-white">
                        {opt}
                      </option>
                    ))}
                  </select>
                  <span className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-400">
                    <span className="material-symbols-outlined text-[22px]">expand_more</span>
                  </span>
                </div>
                <p className="mt-2 text-[10px] text-zinc-500">Pick where you’d like to dine in Bengaluru.</p>
              </div>

              <div className="group rounded-2xl border border-white/5 bg-white/5 p-3.5 transition-all hover:border-white/10 sm:p-3.5">
                <div className="mb-2 flex items-center gap-2">
                  <span className="material-symbols-outlined text-xl text-[#E23744]">payments</span>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-500">Budget for two</span>
                </div>
                <div className="flex flex-col gap-2">
                  {BUDGET_OPTIONS.map((b) => (
                    <button
                      key={b.value}
                      type="button"
                      onClick={() => setBudget(b.value)}
                      className={`flex w-full flex-col items-start rounded-xl border px-3 py-2.5 text-left transition-all ${
                        budget === b.value
                          ? "border-[#E23744]/60 bg-[#E23744]/15 shadow-[0_0_0_1px_rgba(226,55,68,0.25)]"
                          : "border-white/10 bg-white/[0.04] hover:border-white/15 hover:bg-white/[0.07]"
                      }`}
                      aria-pressed={budget === b.value}
                    >
                      <span className="text-xs font-bold text-white sm:text-sm">{b.title}</span>
                      <span className="text-[10px] font-medium text-zinc-400 sm:text-[11px]">{b.range}</span>
                    </button>
                  ))}
                </div>
                <p className="mt-2 text-[10px] text-zinc-500">
                  Approximate meal spend for two (drinks and taxes extra).
                </p>
              </div>

              <div className="group rounded-2xl border border-white/5 bg-white/5 p-3.5 transition-all hover:border-white/10 sm:p-3.5">
                <div className="mb-2 flex items-center gap-2">
                  <span className="material-symbols-outlined text-xl text-[#E23744]">grade</span>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-500">Min. rating</span>
                </div>
                <div className="flex flex-wrap items-center gap-3">
                  <span className="text-lg font-bold text-white">{minRating.toFixed(1)}+</span>
                  <div className="flex text-amber-400">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <span
                        key={i}
                        className="material-symbols-outlined text-sm"
                        style={{
                          fontVariationSettings: i < filledStars ? "'FILL' 1" : "'FILL' 0",
                        }}
                      >
                        star
                      </span>
                    ))}
                  </div>
                </div>
                <input
                  type="range"
                  min={0}
                  max={5}
                  step={0.1}
                  value={minRating}
                  onChange={(e) => setMinRating(Number(e.target.value))}
                  className="mt-3 w-full accent-[#E23744]"
                  aria-label="Minimum rating"
                />
              </div>

              <div className="group rounded-2xl border border-white/5 bg-white/5 p-3.5 transition-all hover:border-white/10 md:col-span-2 sm:p-3.5">
                <div className="mb-2 flex items-center gap-2">
                  <span className="material-symbols-outlined text-xl text-[#E23744]">restaurant_menu</span>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-500">Cuisines</span>
                </div>
                <input
                  className="w-full border-none bg-transparent p-0 text-sm font-medium text-white placeholder:text-zinc-600 focus:outline-none focus:ring-0"
                  placeholder="Italian, Chinese, North Indian…"
                  value={cuisines}
                  onChange={(e) => setCuisines(e.target.value)}
                  aria-label="Cuisines, comma separated"
                />
                <p className="mt-2 text-[10px] text-zinc-500">Comma-separated list; empty means any cuisine.</p>
              </div>

              <div className="group flex flex-col justify-between rounded-2xl border border-white/5 bg-white/5 p-3.5 transition-all hover:border-white/10 sm:p-3.5">
                <div className="mb-2 flex items-center gap-2">
                  <span className="material-symbols-outlined text-xl text-[#E23744]">tune</span>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-500">Advanced</span>
                </div>
                <button
                  type="button"
                  onClick={() => setShowAdvanced((v) => !v)}
                  className="text-left text-sm font-semibold text-[#E23744] hover:underline"
                >
                  {showAdvanced ? "Hide" : "Show"} advanced matching options
                </button>
              </div>
            </div>

            {showAdvanced && (
              <div className="mb-4 grid grid-cols-1 gap-3 border-t border-white/10 pt-4 sm:grid-cols-3">
                <label className="text-xs text-zinc-400">
                  How many places to consider
                  <input
                    type="number"
                    min={1}
                    max={100}
                    value={cap}
                    onChange={(e) => setCap(Number(e.target.value))}
                    className="mt-1 w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
                  />
                </label>
                <label className="text-xs text-zinc-400">
                  How many picks to show
                  <input
                    type="number"
                    min={1}
                    max={20}
                    value={topN}
                    onChange={(e) => setTopN(Number(e.target.value))}
                    className="mt-1 w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
                  />
                </label>
                <label className="flex cursor-pointer items-center gap-2 pt-4 text-sm text-zinc-300 sm:pt-5">
                  <input
                    type="checkbox"
                    checked={useLlm}
                    onChange={(e) => setUseLlm(e.target.checked)}
                    className="h-4 w-4 accent-[#E23744]"
                  />
                  Richer AI explanations
                </label>
              </div>
            )}

            {inlineError && (
              <div
                className="mb-4 rounded-xl border border-red-500/40 bg-red-950/40 px-4 py-3 text-sm text-red-100"
                role="alert"
              >
                {inlineError}
              </div>
            )}

            <button
              type="button"
              onClick={submitRecommendation}
              disabled={busy}
              className="accent-gradient flex h-12 w-full items-center justify-center gap-2 rounded-2xl text-sm font-bold text-white shadow-lg shadow-red-900/20 transition-all duration-300 hover:scale-[1.01] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60 sm:h-[52px] sm:gap-2.5 sm:text-base"
            >
              {busy ? (
                <>
                  <span className="material-symbols-outlined animate-spin">progress_activity</span>
                  Curating matches…
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined">flare</span>
                  Get recommendations
                </>
              )}
            </button>
          </div>
        </div>
        </section>
      </main>
    </SiteChrome>
  );
}
