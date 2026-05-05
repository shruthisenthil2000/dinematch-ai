export type PreferencePayload = {
  location: string;
  budget: "low" | "medium" | "high";
  cuisines: string[];
  min_rating: number;
  optional_constraints?: string;
};

export type RecommendRequest = {
  preferences: PreferencePayload;
  cap: number;
  top_n: number;
  use_llm: boolean;
};

export type Recommendation = {
  restaurant_id: string;
  name: string;
  cuisine: string;
  rating: number;
  estimated_cost: string;
  ai_rationale: string;
  rank: number;
  /** Neighborhood / locality for display when provided by the service */
  area?: string;
  /** From retrieval: exact selected area vs adjacent-cluster supplement */
  location_tier?: "primary" | "nearby";
};

export type RecommendResponse = {
  valid: boolean;
  response?: {
    recommendations: Recommendation[];
    comparative_summary?: string;
    meta?: Record<string, unknown>;
  };
  observability?: {
    latency_ms?: number;
    candidate_count?: number;
    recommendation_count?: number;
    outcome_notes?: string;
    cache_hit?: boolean;
  };
  errors?: string[];
  error?: string;
  detail?: string;
};
