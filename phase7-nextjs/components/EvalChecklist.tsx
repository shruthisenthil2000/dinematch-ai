export function EvalChecklist() {
  return (
    <div className="panel">
      <h2>Phase 7 eval checklist</h2>
      <ul>
        <li>Correctness: rankings obey top_n, no duplicate IDs, and rating threshold is not violated.</li>
        <li>Relevance: rationales mention user preferences and avoid invented facts.</li>
        <li>Safety: constraints with injection-like or harmful terms are soft-flagged before submit.</li>
        <li>Ops: API base URL and runtime model behavior controlled by environment config.</li>
      </ul>
      <p className="meta">
        Known limitation: strict proof that all recommendations are subset of candidate IDs requires backend exposing candidate IDs in evaluation mode.
      </p>
    </div>
  );
}
