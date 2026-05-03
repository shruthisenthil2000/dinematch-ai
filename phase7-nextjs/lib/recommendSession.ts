import type { EvalIssue } from "./checks";
import type { RecommendRequest, RecommendResponse } from "./types";

export const RECOMMEND_SESSION_KEY = "dinematch.recommend.v1";

export type StoredRecommendResult = {
  request: RecommendRequest;
  response: RecommendResponse;
  integrityIssues: EvalIssue[];
  statusKind: "ok" | "warn" | "error";
  statusText: string;
  fetchedAt: string;
};

export function readStoredRecommend(): StoredRecommendResult | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(RECOMMEND_SESSION_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as StoredRecommendResult;
    if (!parsed?.request || !parsed?.response) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function writeStoredRecommend(data: StoredRecommendResult): void {
  sessionStorage.setItem(RECOMMEND_SESSION_KEY, JSON.stringify(data));
}

export function clearStoredRecommend(): void {
  sessionStorage.removeItem(RECOMMEND_SESSION_KEY);
}
