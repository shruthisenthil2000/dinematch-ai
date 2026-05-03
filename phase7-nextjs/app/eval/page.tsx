"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { checkRecommendationIntegrity } from "../../lib/checks";
import type { RecommendRequest, RecommendResponse } from "../../lib/types";
import { EvalChecklist } from "../../components/EvalChecklist";
import { SiteChrome } from "../../components/stitch/SiteChrome";

type GoldenExample = {
  id: string;
  label: string;
  preferences: RecommendRequest["preferences"];
};

type GoldenFile = { examples: GoldenExample[] };

export default function EvalPage() {
  const [examples, setExamples] = useState<GoldenExample[]>([]);
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<string[]>([]);

  useEffect(() => {
    fetch("/golden-queries.json")
      .then((r) => r.json())
      .then((data: GoldenFile) => setExamples(data.examples || []))
      .catch(() => setExamples([]));
  }, []);

  async function runEval() {
    setRunning(true);
    setResults([]);
    const lines: string[] = [];

    for (const e of examples) {
      const body: RecommendRequest = {
        preferences: e.preferences,
        cap: 25,
        top_n: 5,
        use_llm: true,
      };

      try {
        const r = await fetch("/api/recommend", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        const data: RecommendResponse = await r.json();
        const issues = checkRecommendationIntegrity(body.preferences, body.top_n, data);
        const errors = issues.filter((x) => x.level === "error");
        const label = e.label?.trim() || e.id;
        if (!r.ok) {
          lines.push(`${label}: Couldn’t complete this scenario right now.`);
        } else if (errors.length > 0) {
          lines.push(`${label}: Needs attention — ${errors.map((x) => x.message).join("; ")}`);
        } else {
          lines.push(`${label}: Looks good`);
        }
      } catch {
        lines.push(`${e.label?.trim() || e.id}: Something went wrong — please try again.`);
      }
    }

    setResults(lines);
    setRunning(false);
  }

  return (
    <SiteChrome activeNav="eval" mainClassName="bg-[#0F0F0F]">
      <main className="mx-auto max-w-3xl px-4 py-10 md:px-8 md:py-14">
        <div className="glass-panel mb-8 rounded-2xl border border-white/10 p-6 sm:p-8">
          <h1 className="mb-2 text-2xl font-bold text-white md:text-3xl">Try saved sample searches</h1>
          <p className="text-sm leading-relaxed text-zinc-400">
            Run a quick batch of example preference sets to see how consistent your personalized dining matches feel
            across common requests. Results use the same experience as the main app—no extra setup required.
          </p>
          <Link href="/" className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-[#E23744] hover:underline">
            <span className="material-symbols-outlined text-base">arrow_back</span>
            Back to preferences
          </Link>
        </div>

        <div className="glass-panel mb-8 rounded-2xl border border-white/10 p-6">
          <button
            type="button"
            onClick={runEval}
            disabled={running || examples.length === 0}
            className="accent-gradient flex items-center justify-center gap-2 rounded-xl px-6 py-3 text-sm font-bold text-white shadow-lg disabled:cursor-not-allowed disabled:opacity-50"
          >
            {running ? (
              <>
                <span className="material-symbols-outlined animate-spin">progress_activity</span>
                Running…
              </>
            ) : (
              <>
                <span className="material-symbols-outlined">fact_check</span>
                Run sample batch ({examples.length} scenarios)
              </>
            )}
          </button>
          {examples.length === 0 && (
            <p className="mt-4 text-sm text-amber-200/90">No sample scenarios are available to run yet.</p>
          )}
        </div>

        <div className="mb-8">
          <EvalChecklist />
        </div>

        <div className="glass-panel rounded-2xl border border-white/10 p-6">
          <h2 className="mb-4 text-lg font-semibold text-white">Outcomes</h2>
          {results.length === 0 ? (
            <p className="text-sm text-zinc-500">No results yet.</p>
          ) : (
            <ul className="space-y-2 font-mono text-sm text-zinc-300">
              {results.map((r) => (
                <li
                  key={r}
                  className={
                    r.includes("Looks good")
                      ? "text-emerald-400"
                      : r.includes("Needs attention") || r.includes("Something went wrong") || r.includes("Couldn’t")
                        ? "text-red-400"
                        : ""
                  }
                >
                  {r}
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
    </SiteChrome>
  );
}
