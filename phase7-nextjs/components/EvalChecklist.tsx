export function EvalChecklist() {
  return (
    <div className="themed-text-secondary glass-panel rounded-2xl border themed-border p-6 text-sm">
      <h2 className="mb-3 text-lg font-semibold themed-text">What we verify for you</h2>
      <ul className="list-inside list-disc space-y-2">
        <li>Your shortlist respects the number of picks you asked for, without repeats, and honors your minimum rating.</li>
        <li>Each explanation reflects your preferences and avoids invented details.</li>
        <li>Unusual or off-topic wording in your notes is flagged gently before you search.</li>
      </ul>
      <p className="themed-text-muted mt-4 text-xs leading-relaxed">
        We keep improving how personalized dining matches are ranked and explained—your feedback shapes what we build
        next.
      </p>
    </div>
  );
}
