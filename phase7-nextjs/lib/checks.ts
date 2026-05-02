import type { PreferencePayload, Recommendation, RecommendResponse } from "./types";

export type EvalIssue = { level: "error" | "warn"; message: string };

export function checkRecommendationIntegrity(
  prefs: PreferencePayload,
  topN: number,
  data: RecommendResponse
): EvalIssue[] {
  const issues: EvalIssue[] = [];
  const recs: Recommendation[] = data.response?.recommendations ?? [];
  const candidateCount = data.observability?.candidate_count;

  if (recs.length > topN) {
    issues.push({ level: "error", message: `Returned ${recs.length} recommendations, above top_n=${topN}.` });
  }
  if (typeof candidateCount === "number" && recs.length > candidateCount) {
    issues.push({ level: "error", message: `Returned ${recs.length} recommendations, above candidate_count=${candidateCount}.` });
  }

  const ids = new Set<string>();
  recs.forEach((r, idx) => {
    if (r.rank !== idx + 1) {
      issues.push({ level: "warn", message: `Rank sequence mismatch near item ${idx + 1}.` });
    }
    if (ids.has(r.restaurant_id)) {
      issues.push({ level: "error", message: `Duplicate restaurant_id found: ${r.restaurant_id}` });
    }
    ids.add(r.restaurant_id);
    if (r.rating < prefs.min_rating) {
      issues.push({ level: "error", message: `${r.name} rating ${r.rating} below min_rating ${prefs.min_rating}.` });
    }
  });

  if (!recs.length) {
    issues.push({ level: "warn", message: "No recommendations returned. This may be valid for strict filters." });
  }

  return issues;
}
