export function EvalChecklist() {
  return (
    <div className="glass-panel rounded-2xl border border-white/10 p-6 text-sm text-zinc-300">
      <h2 className="mb-3 text-lg font-semibold text-white">What we verify for you</h2>
      <ul className="list-inside list-disc space-y-2 text-zinc-400">
        <li>Your shortlist respects the number of picks you asked for, without repeats, and honors your minimum rating.</li>
        <li>Each explanation reflects your preferences and avoids invented details.</li>
        <li>Unusual or off-topic wording in your notes is flagged gently before you search.</li>
      </ul>
      <p className="mt-4 text-xs leading-relaxed text-zinc-500">
        We keep improving how personalized dining matches are ranked and explained—your feedback shapes what we build
        next.
      </p>
    </div>
  );
}
