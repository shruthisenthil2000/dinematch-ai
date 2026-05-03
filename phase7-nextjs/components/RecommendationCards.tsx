/**
 * Legacy list layout for recommendations (plain CSS era).
 * The Stitch dark UI uses `RecommendationCard` in `components/stitch/RecommendationsPageClient.tsx`.
 */
import type { Recommendation } from "../lib/types";

export function RecommendationCards({ recs }: { recs: Recommendation[] }) {
  if (!recs.length) {
    return <div className="msg warn">No matches for current filters. Try lowering min rating or broadening cuisines.</div>;
  }

  return (
    <div className="cards">
      {recs.map((r) => (
        <article key={`${r.rank}-${r.restaurant_id}`} className="card">
          <h3>#{r.rank} {r.name}</h3>
          <div className="meta">{r.cuisine} | Rating {r.rating} | {r.estimated_cost}</div>
          <p>{r.ai_rationale}</p>
          <div className="meta">Listing: {r.restaurant_id}</div>
        </article>
      ))}
    </div>
  );
}
