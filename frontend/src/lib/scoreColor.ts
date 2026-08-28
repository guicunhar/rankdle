// Mesmas faixas dos emojis em lib/share.ts (✅/🟩 ≥90, 🟨 75-89, 🟥/💀 <75).
export function scoreColor(score: number): string {
  if (score >= 90) return "text-good";
  if (score >= 75) return "text-accent-400";
  return "text-bad";
}
