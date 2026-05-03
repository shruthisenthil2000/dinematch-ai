"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { checkRecommendationIntegrity } from "../../lib/checks";
import { writeStoredRecommend } from "../../lib/recommendSession";
import { safetyWarnings } from "../../lib/safety";
import type { RecommendRequest, RecommendResponse } from "../../lib/types";
import { InsightsAside, SiteChrome } from "./SiteChrome";

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

export function HomePageClient() {
  const router = useRouter();
  const [location, setLocation] = useState("Bellandur");
  const [budget, setBudget] = useState<"low" | "medium" | "high">("high");
  const [cuisines, setCuisines] = useState("");
  const [minRating, setMinRating] = useState(4);
  const [optionalConstraints, setOptionalConstraints] = useState("Choose your preferred dining budget for two.");
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
    <SiteChrome
      activeNav="home"
      aside={
        <InsightsAside>
          <div className="rounded-lg border-l-2 border-[#E23744] bg-[#E23744]/10 p-3 font-medium text-[#E23744]">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined">psychology</span>
              <span className="text-sm">Match analysis</span>
            </div>
          </div>
          <div className="rounded-lg p-3 text-zinc-500 transition-all hover:bg-white/5 hover:text-zinc-300">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined">settings_heart</span>
              <span className="text-sm">Preferences</span>
            </div>
          </div>
          <Link
            href="/eval"
            className="rounded-lg p-3 text-zinc-500 transition-all hover:bg-white/5 hover:text-zinc-300"
          >
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined">history</span>
              <span className="text-sm">Sample scenarios</span>
            </div>
          </Link>
          {warnings.length > 0 && (
            <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-100">
              <p className="mb-1 font-semibold text-amber-200">Safety soft-check</p>
              <ul className="list-inside list-disc space-y-1 text-amber-100/90">
                {warnings.map((w) => (
                  <li key={w}>{w}</li>
                ))}
              </ul>
            </div>
          )}
        </InsightsAside>
      }
    >
      <main>
      <section className="relative flex h-[420px] items-center justify-center px-4 hero-bg sm:h-[520px] md:h-[614px] md:px-8">
        <div className="hero-overlay absolute inset-0" />
        <div className="relative z-10 max-w-3xl px-2 text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 backdrop-blur-md">
            <span className="material-symbols-outlined text-sm text-[#E23744]">verified</span>
            <span className="text-xs font-semibold uppercase tracking-wider text-zinc-300">
              AI-powered gastronomy
            </span>
          </div>
          <h1 className="mb-4 text-3xl font-bold leading-tight tracking-[-0.02em] text-white sm:text-4xl md:text-5xl lg:text-[48px] lg:leading-[1.1]">
            Find your perfect meal
            <br />
            <span className="text-[#ffb3b1]">with AI precision</span>
          </h1>
          <p className="mx-auto mb-6 max-w-xl text-base text-zinc-400 sm:text-lg">
            Personalized dining matches from your location, budget, cuisines, and notes — refined by AI around what you
            care about most.
          </p>
        </div>
      </section>

      <section className="relative z-20 -mt-16 px-4 pb-16 sm:-mt-20 md:-mt-24 md:px-8 md:pb-20">
        <div className="mx-auto max-w-4xl">
          <div className="glass-panel rounded-[28px] border-white/10 p-6 shadow-2xl sm:rounded-[32px] sm:p-8">
            <div className="relative mb-8 sm:mb-10">
              <div className="absolute -left-1 -top-2 sm:-left-3 sm:-top-3">
                <span className="relative flex h-6 w-6">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#E23744] opacity-20" />
                  <span className="relative inline-flex h-6 w-6 items-center justify-center rounded-full bg-[#E23744]">
                    <span className="material-symbols-outlined text-[14px] text-white">auto_awesome</span>
                  </span>
                </span>
              </div>
              <label className="sr-only" htmlFor="optional-constraints">
                Dining notes
              </label>
              <input
                id="optional-constraints"
                className="h-14 w-full rounded-2xl border border-white/10 bg-white/5 px-4 pb-6 pt-2 text-base text-white placeholder:text-zinc-600 focus:border-[#E23744]/50 focus:outline-none focus:ring-2 focus:ring-[#E23744]/30 sm:h-16 sm:px-6 sm:text-lg"
                placeholder="I'm looking for a quiet Japanese spot for a date night…"
                value={optionalConstraints}
                onChange={(e) => setOptionalConstraints(e.target.value)}
              />
              <p className="pointer-events-none absolute bottom-3 right-4 text-[10px] font-medium uppercase tracking-widest text-zinc-500">
                Your notes
              </p>
            </div>

            <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-3">
              <div className="group rounded-2xl border border-white/5 bg-white/5 p-4 transition-all hover:border-white/10">
                <div className="mb-3 flex items-center gap-2">
                  <span className="material-symbols-outlined text-xl text-[#E23744]">location_on</span>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-500">Area</span>
                </div>
                <div className="relative">
                  <select
                    id="dining-location"
                    className="w-full cursor-pointer appearance-none rounded-xl border border-white/10 bg-[#141414] py-3 pl-3 pr-10 text-sm font-semibold text-white shadow-inner focus:border-[#E23744]/50 focus:outline-none focus:ring-2 focus:ring-[#E23744]/25 sm:text-base"
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

              <div className="group rounded-2xl border border-white/5 bg-white/5 p-4 transition-all hover:border-white/10">
                <div className="mb-3 flex items-center gap-2">
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

              <div className="group rounded-2xl border border-white/5 bg-white/5 p-4 transition-all hover:border-white/10">
                <div className="mb-3 flex items-center gap-2">
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

              <div className="group rounded-2xl border border-white/5 bg-white/5 p-4 transition-all hover:border-white/10 md:col-span-2">
                <div className="mb-3 flex items-center gap-2">
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

              <div className="group flex flex-col justify-between rounded-2xl border border-white/5 bg-white/5 p-4 transition-all hover:border-white/10">
                <div className="mb-3 flex items-center gap-2">
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
              <div className="mb-8 grid grid-cols-1 gap-4 border-t border-white/10 pt-6 sm:grid-cols-3">
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
                <label className="flex cursor-pointer items-center gap-2 pt-6 text-sm text-zinc-300">
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
              className="accent-gradient flex h-14 w-full items-center justify-center gap-3 rounded-2xl text-base font-bold text-white shadow-xl shadow-red-900/20 transition-all duration-300 hover:scale-[1.01] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60 sm:h-16 sm:text-lg"
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

      <section className="mx-auto max-w-[1200px] px-4 py-12 md:px-8 md:py-20">
        <h2 className="mb-8 flex items-center gap-4 text-xl font-semibold text-white md:mb-12 md:text-2xl">
          <span className="h-px flex-grow bg-white/10" />
          Curated experiences
          <span className="h-px flex-grow bg-white/10" />
        </h2>
        <div className="grid h-auto grid-cols-1 gap-6 md:h-[480px] lg:h-[600px] lg:grid-cols-12">
          <div className="group relative min-h-[240px] overflow-hidden rounded-3xl lg:col-span-8 lg:min-h-0">
            {/* eslint-disable-next-line @next/next/no-img-element -- static Stitch mood imagery */}
            <img
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuAx2bBZJ7ZODGKPCHWaAaZu2q_J18Bdggc1jUdNWhktvwoE0dw1YpZGLW2Pxis-A346dA59pZHgWkJbyQ0YOJ_isMLHzOQmYmx0WOo4HOCkAnpVbTzdCJ4k0CGzxOabKg48BEOmgnLTkVHmo2BJUpds3C1ZhTqRYMQE8elywLOYMJOD5_wDWOxH-C0zds2AW8EB5JDnVsWzd1EKbcrluwKg1KTO-AL6Dxn1SSsRPTQFcejT8lxP5MlsYI4Z7iHQgjrwckiRaLKjTbC5"
              alt="Moody upscale restaurant interior"
              className="h-full min-h-[240px] w-full object-cover transition-transform duration-700 group-hover:scale-110 lg:min-h-0"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
            <div className="absolute bottom-6 left-6 md:bottom-8 md:left-8">
              <span className="mb-2 inline-block rounded-full bg-[#E23744] px-3 py-1 text-[10px] font-bold text-white">
                Editorial
              </span>
              <h3 className="text-2xl font-bold text-white md:text-3xl">The Obsidian Lounge</h3>
              <p className="text-sm text-zinc-300 md:text-base">Molecular gastronomy • mood-led discovery</p>
            </div>
          </div>
          <div className="grid min-h-[200px] grid-rows-2 gap-6 lg:col-span-4 lg:min-h-0">
            <div className="group relative min-h-[140px] overflow-hidden rounded-3xl lg:min-h-0">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuBZ094qYCv2mEwDzTyEauMibDnYfM5rXns1A2sZqylHcFZ08hlRK-mSHEe6tXNa-n5Yw2IqpLzH4TCkKhgIwlzS0OfVH34GTYk9WWK6pN_ue1SQ2rz8npsrcegzTs4hdME59KiAlwbNeVBiPb7dmKeNSLprgYCrzrXk_Zm_YstNBTE9KyUUkHa6TQqH51WPEBVlgvDU6bzrLAS69hzrOhHuOZXKF3yVMDNaZ9FsaZtXh34hxPftxyR-h9o9FmF9mQTk1fqHscGIGavV"
                alt="Gourmet plated dish"
                className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
              />
              <div className="absolute inset-0 flex items-center justify-center bg-black/40">
                <span className="border-b-2 border-[#E23744] font-bold text-white">Artisanal fusion</span>
              </div>
            </div>
            <div className="group relative min-h-[140px] overflow-hidden rounded-3xl lg:min-h-0">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuCnC-mVlq-KkPsVNUk8oQouIAswAo-v3f0OJ0BKnthxi7eUgal2aRaRIwlrDRDLqDsQhXUBs6nWLRZsuAFhEVCDe9oi_J4jhe58WIO4Jy4dra-SuNFAwicm5WKtyoq6UbOKsd9H7Bd_G0LOKT78yOLmrQDQgpJM6y-NT8LfuYrc1czVTTULsHsqWXNHzECCCvCrrjvo_S2x2CHSiaShaW-R-Gm0LhpVJPWj9h8hDKHX9cakqGH3mx1wbzwqjJq0_9B1oSTpxWUHI9RR"
                alt="Signature cocktails"
                className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
              />
              <div className="absolute inset-0 flex items-center justify-center bg-black/40">
                <span className="border-b-2 border-[#E23744] font-bold text-white">Mixology masters</span>
              </div>
            </div>
          </div>
        </div>
      </section>
      </main>
    </SiteChrome>
  );
}
