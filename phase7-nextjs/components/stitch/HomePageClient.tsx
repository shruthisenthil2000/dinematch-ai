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
const DINING_NOTES_PLACEHOLDER = "Add cuisine, occasion, or vibe...";

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
    <SiteChrome activeNav="home" showFooter={false} mainClassName="themed-bg md:flex md:flex-col">
      <main className="flex w-full flex-1 flex-col max-md:min-h-0 max-md:overflow-y-auto md:min-h-0 md:max-h-[calc(100dvh-4rem)] md:overflow-y-auto md:overflow-x-hidden md:px-8 md:pb-6 md:pt-4 lg:px-12 lg:pb-7 lg:pt-5 xl:px-16">
        <section className="relative flex w-full shrink-0 flex-col items-center justify-center px-4 pb-3 pt-7 hero-bg sm:pb-4 sm:pt-8 md:min-h-0 md:pb-4 md:pt-7 lg:pt-8">
          <div className="hero-overlay absolute inset-0" />
          <div className="relative z-10 mx-auto w-full max-w-2xl px-3 text-center sm:px-5">
            <div className="mb-2.5 inline-flex items-center gap-2 rounded-full border themed-border bg-black/5 px-3 py-1.5 backdrop-blur-md dark:bg-white/5 sm:mb-3 sm:px-3.5 sm:py-1.5">
              <span className="material-symbols-outlined text-sm text-[#E23744]">verified</span>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-600 dark:text-zinc-400 sm:text-[11px]">
                AI-powered dining
              </span>
            </div>
            <h1 className="hero-title-ink mb-2.5 text-3xl font-bold leading-[1.1] tracking-[-0.02em] themed-text sm:mb-3 sm:text-4xl md:mb-3 md:text-5xl md:leading-[1.08]">
              Find your perfect meal
              <br />
              <span className="hero-gradient-ink">with AI precision</span>
            </h1>
            <p className="hero-subtitle-ink mx-auto mb-6 max-w-xl text-sm leading-relaxed sm:mb-7 sm:text-base md:mb-8 md:text-[1.0625rem] md:leading-relaxed">
              Tell us where, your budget, and what you crave — we match you to places worth the reservation.
            </p>
          </div>
        </section>

        <section className="relative z-20 w-full shrink-0 px-4 pb-8 pt-0 sm:px-6 sm:pb-10 md:px-0 md:pb-6">
          <div className="mx-auto mb-4 flex max-w-2xl justify-center sm:mb-5 md:mb-6 lg:max-w-[42rem]" aria-hidden>
            <div className="h-px w-14 rounded-full bg-gradient-to-r from-transparent via-white/25 to-transparent sm:w-20 md:w-24" />
          </div>
          <div className="mx-auto w-full max-w-2xl lg:max-w-[42rem]">
            <div className="glass-panel rounded-[1.35rem] border themed-border p-5 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.24),0_22px_64px_rgba(88,69,46,0.16)] dark:shadow-[inset_0_1px_0_0_rgba(255,255,255,0.05),0_22px_64px_rgba(0,0,0,0.44)] sm:rounded-[1.65rem] sm:p-6 md:p-6">
            {warnings.length > 0 && (
              <div className="mb-4 rounded-xl border border-amber-500/25 bg-amber-500/[0.08] p-3.5 text-left text-xs text-amber-100/95 sm:p-4 sm:text-sm">
                <p className="mb-1.5 font-semibold text-amber-200">Safety note</p>
                <ul className="list-inside list-disc space-y-1 text-amber-100/90">
                  {warnings.map((w) => (
                    <li key={w}>{w}</li>
                  ))}
                </ul>
              </div>
            )}
            <div className="mb-5 space-y-1.5 sm:mb-5">
              <span id="optional-constraints-desc" className="sr-only">
                Optional. Short hint in the placeholder: cuisine, occasion, or vibe. Leave blank if you prefer.
              </span>
              <div className="flex items-center gap-2 px-0.5">
                <span className="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-black/[0.05] ring-1 ring-black/[0.08] dark:bg-white/[0.05] dark:ring-white/[0.08]" aria-hidden>
                  <span className="material-symbols-outlined text-sm text-[#E23744]">edit_note</span>
                </span>
                <label htmlFor="optional-constraints" className="themed-text-label text-[12px] font-medium">
                  Notes <span className="themed-text-muted font-normal">· optional</span>
                </label>
              </div>
              <input
                id="optional-constraints"
                type="text"
                autoComplete="off"
                aria-describedby="optional-constraints-desc"
                className="themed-text-placeholder h-11 w-full rounded-xl border themed-border bg-black/[0.03] px-3.5 py-2.5 text-sm themed-text shadow-inner focus:border-[#E23744]/45 focus:outline-none focus:ring-2 focus:ring-[#E23744]/22 dark:bg-white/[0.04] sm:h-12 sm:px-4 sm:text-base"
                placeholder={DINING_NOTES_PLACEHOLDER}
                value={optionalConstraints}
                onChange={(e) => setOptionalConstraints(e.target.value)}
              />
            </div>

            <div className="mb-5 grid grid-cols-1 gap-3 md:mb-5 md:grid-cols-3 md:gap-3">
              <div className="group rounded-xl border themed-border bg-black/[0.02] p-3.5 transition-colors hover:border-zinc-400/50 dark:bg-white/[0.03] dark:hover:border-white/10 sm:p-4">
                <div className="mb-2 flex items-center gap-2">
                  <span className="material-symbols-outlined text-xl text-[#E23744]">location_on</span>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-500 dark:text-zinc-500">Area</span>
                </div>
                <div className="relative">
                  <select
                    id="dining-location"
                    className="w-full cursor-pointer appearance-none rounded-xl border themed-border bg-white/70 py-2.5 pl-3 pr-10 text-sm font-semibold text-zinc-800 shadow-inner focus:border-[#E23744]/50 focus:outline-none focus:ring-2 focus:ring-[#E23744]/25 dark:bg-[#141414] dark:text-white sm:text-base"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    aria-label="Neighborhood or area"
                  >
                    {LOCATION_OPTIONS.map((opt) => (
                      <option key={opt} value={opt} className="bg-white text-zinc-900 dark:bg-[#141414] dark:text-white">
                        {opt}
                      </option>
                    ))}
                  </select>
                  <span className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-400">
                    <span className="material-symbols-outlined text-[22px]">expand_more</span>
                  </span>
                </div>
                <p className="themed-text-muted mt-2 text-[10px]">Pick where you’d like to dine in Bengaluru.</p>
              </div>

              <div className="group rounded-xl border themed-border bg-black/[0.02] p-3.5 transition-colors hover:border-zinc-400/50 dark:bg-white/[0.03] dark:hover:border-white/10 sm:p-4">
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
                          : "border-zinc-300/70 bg-black/[0.03] hover:border-zinc-400 hover:bg-black/[0.05] dark:border-white/10 dark:bg-white/[0.04] dark:hover:border-white/15 dark:hover:bg-white/[0.07]"
                      }`}
                      aria-pressed={budget === b.value}
                    >
                      <span className="text-xs font-bold themed-text sm:text-sm">{b.title}</span>
                      <span className="themed-text-muted text-[10px] font-medium sm:text-[11px]">{b.range}</span>
                    </button>
                  ))}
                </div>
                <p className="themed-text-muted mt-2 text-[10px]">
                  Approximate meal spend for two (drinks and taxes extra).
                </p>
              </div>

              <div className="group rounded-xl border themed-border bg-black/[0.02] p-3.5 transition-colors hover:border-zinc-400/50 dark:bg-white/[0.03] dark:hover:border-white/10 sm:p-4">
                <div className="mb-2 flex items-center gap-2">
                  <span className="material-symbols-outlined text-xl text-[#E23744]">grade</span>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-500">Min. rating</span>
                </div>
                <div className="flex flex-wrap items-center gap-3">
                  <span className="text-lg font-bold themed-text">{minRating.toFixed(1)}+</span>
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

              <div className="group rounded-xl border themed-border bg-black/[0.02] p-3.5 transition-colors hover:border-zinc-400/50 dark:bg-white/[0.03] dark:hover:border-white/10 md:col-span-2 sm:p-4">
                <div className="mb-2 flex items-center gap-2">
                  <span className="material-symbols-outlined text-xl text-[#E23744]">restaurant_menu</span>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-500">Cuisines</span>
                </div>
                <input
                  className="w-full border-none bg-transparent p-0 text-sm font-medium themed-text placeholder:text-zinc-500 focus:outline-none focus:ring-0 dark:placeholder:text-zinc-600"
                  placeholder="Italian, Chinese, North Indian…"
                  value={cuisines}
                  onChange={(e) => setCuisines(e.target.value)}
                  aria-label="Cuisines, comma separated"
                />
                <p className="themed-text-muted mt-2 text-[10px]">Comma-separated list; empty means any cuisine.</p>
              </div>

              <div className="group flex flex-col justify-between rounded-xl border themed-border bg-black/[0.02] p-3.5 transition-colors hover:border-zinc-400/50 dark:bg-white/[0.03] dark:hover:border-white/10 sm:p-4">
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
              <div className="mb-5 grid grid-cols-1 gap-3 border-t themed-border pt-4 sm:grid-cols-3 sm:pt-4">
                <label className="themed-text-label text-xs">
                  How many places to consider
                  <input
                    type="number"
                    min={1}
                    max={100}
                    value={cap}
                    onChange={(e) => setCap(Number(e.target.value))}
                    className="mt-1 w-full rounded-lg border themed-border bg-black/5 px-3 py-2 text-sm themed-text dark:bg-white/5"
                  />
                </label>
                <label className="themed-text-label text-xs">
                  How many picks to show
                  <input
                    type="number"
                    min={1}
                    max={20}
                    value={topN}
                    onChange={(e) => setTopN(Number(e.target.value))}
                    className="mt-1 w-full rounded-lg border themed-border bg-black/5 px-3 py-2 text-sm themed-text dark:bg-white/5"
                  />
                </label>
                <label className="themed-text-secondary flex cursor-pointer items-center gap-2 pt-4 text-sm sm:pt-4">
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
              className="accent-gradient flex min-h-[3rem] w-full items-center justify-center gap-2 rounded-2xl px-4 py-3 text-sm font-bold text-white shadow-lg shadow-red-900/25 transition-all duration-300 hover:opacity-[0.96] active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60 sm:min-h-12 sm:text-base"
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
