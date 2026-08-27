import type { DailyChallenge, DailyResult } from "../api/types";

function emojiForScore(score: number): string {
  if (score >= 100) return "🟩";
  if (score >= 50) return "🟨";
  return "🟥";
}

export function buildShareText(challenge: DailyChallenge, result: DailyResult): string {
  const guessEmojis = result.player_guesses.map((g) => emojiForScore(g.score));
  const blanks = "⬜".repeat(Math.max(0, challenge.lives_total - guessEmojis.length));
  const grid = guessEmojis.join("") + blanks;

  const lines = [
    `Rankdle ${challenge.theme_icon} ${challenge.theme} — ${challenge.date}`,
    challenge.subtheme_title,
    grid,
    `Pontuação: ${result.player_best_score}/100${result.player_exact_hit ? " 🎯" : ""}`,
  ];

  if (result.players_count > 0) {
    const pct = Math.round((result.exact_hit_count / result.players_count) * 100);
    lines.push(`Só ${pct}% cravaram hoje!`);
  }

  lines.push(window.location.origin);

  return lines.join("\n");
}

export function shareUrls(text: string) {
  const encoded = encodeURIComponent(text);
  return {
    whatsapp: `https://wa.me/?text=${encoded}`,
    x: `https://twitter.com/intent/tweet?text=${encoded}`,
  };
}

export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}
