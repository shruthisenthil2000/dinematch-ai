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
    issues.push({
      level: "error",
      message: `We received ${recs.length} picks, but you asked for up to ${topN}.`,
    });
  }
  if (typeof candidateCount === "number" && recs.length > candidateCount) {
    issues.push({
      level: "error",
      message: `We received ${recs.length} picks, which is more than the ${candidateCount} places we reviewed.`,
    });
  }

  const ids = new Set<string>();
  recs.forEach((r, idx) => {
    if (r.rank !== idx + 1) {
      issues.push({ level: "warn", message: `The ordering looks off around pick ${idx + 1}.` });
    }
    if (ids.has(r.restaurant_id)) {
      issues.push({ level: "error", message: `The same listing appeared twice (${r.restaurant_id}).` });
    }
    ids.add(r.restaurant_id);
    if (r.rating < prefs.min_rating) {
      issues.push({
        level: "error",
        message: `${r.name} is rated ${r.rating}, below your minimum of ${prefs.min_rating}.`,
      });
    }
  });

  if (!recs.length) {
    issues.push({
      level: "warn",
      message: "No picks came back — your filters may be very tight. Try relaxing them and search again.",
    });
  }

  return issues;
}
