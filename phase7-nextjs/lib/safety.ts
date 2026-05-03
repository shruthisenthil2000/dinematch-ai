const PROMPT_INJECTION_HINTS = [
  "ignore all prior instructions",
  "ignore previous instructions",
  "system prompt",
  "jailbreak",
  "bypass",
  "override"
];

const HARMFUL_HINTS = [
  "illegal",
  "explosive",
  "weapon",
  "kill",
  "hate",
  "self-harm"
];

export function safetyWarnings(optionalConstraints: string): string[] {
  const text = optionalConstraints.trim().toLowerCase();
  if (!text) return [];

  const warnings: string[] = [];
  if (PROMPT_INJECTION_HINTS.some((k) => text.includes(k))) {
    warnings.push("That wording looks unusual for a dining request. We’ll still apply your preferences safely.");
  }
  if (HARMFUL_HINTS.some((k) => text.includes(k))) {
    warnings.push("Potential harmful/abusive content detected. Please keep constraints restaurant-focused.");
  }
  if (text.length > 300) {
    warnings.push("Very long optional constraints may reduce relevance. Keep it concise when possible.");
  }
  return warnings;
}
