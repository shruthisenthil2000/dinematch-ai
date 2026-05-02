"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import type { RecommendRequest, RecommendResponse } from "../../lib/types";
import { checkRecommendationIntegrity } from "../../lib/checks";

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
        if (!r.ok) {
          lines.push(`${e.id}: API error (${r.status})`);
        } else if (errors.length > 0) {
          lines.push(`${e.id}: FAIL - ${errors.map((x) => x.message).join("; ")}`);
        } else {
          lines.push(`${e.id}: PASS`);
        }
      } catch (err) {
        lines.push(`${e.id}: ERROR - ${String(err)}`);
      }
    }

    setResults(lines);
    setRunning(false);
  }

  return (
    <main>
      <section className="panel">
        <h1>Phase 7 Golden-query evaluation</h1>
        <p>Runs checks over <code>public/golden-queries.json</code> and reports pass/fail by query ID.</p>
        <p><Link href="/">Back to main app</Link></p>
      </section>

      <section className="panel">
        <button onClick={runEval} disabled={running || examples.length === 0}>
          {running ? "Running..." : `Run evaluation (${examples.length} queries)`}
        </button>
      </section>

      <section className="panel">
        <h2>Results</h2>
        {results.length === 0 ? <p className="meta">No results yet.</p> : (
          <ul>
            {results.map((r) => <li key={r}>{r}</li>)}
          </ul>
        )}
      </section>
    </main>
  );
}
