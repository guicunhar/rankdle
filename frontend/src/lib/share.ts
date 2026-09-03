import type { DailyChallenge, DailyResult } from "../api/types";
import { formatDateBR } from "./date";

function emojiForScore(score: number): string {
  if (score >= 100) return "✅"; // cravou a posição
  if (score >= 90) return "🟩";
  if (score >= 75) return "🟨";
  if (score >= 50) return "🟥";
  return "💀";
}

export function buildShareText(challenge: DailyChallenge, result: DailyResult): string {
  const header = `Rankdle ${challenge.theme_icon} ${challenge.theme} — ${formatDateBR(challenge.date)}`;

  const lines =
    result.mode === "infinite"
      ? buildInfiniteLines(header, challenge, result)
      : buildLivesLines(header, challenge, result);

  lines.push(window.location.origin);

  return lines.join("\n");
}

function buildLivesLines(
  header: string,
  challenge: DailyChallenge,
  result: DailyResult,
): string[] {
  const guessEmojis = result.player_guesses.map((g) => emojiForScore(g.score));
  const blanks = "⬜".repeat(Math.max(0, challenge.lives_total - guessEmojis.length));
  const grid = guessEmojis.join("") + blanks;

  return [
    header,
    challenge.subtheme_title,
    grid,
    `Pontuação: ${result.player_best_score}/100${result.player_exact_hit ? " 🎯" : ""}`,
  ];
}

function buildInfiniteLines(
  header: string,
  challenge: DailyChallenge,
  result: DailyResult,
): string[] {
  const n = result.player_attempts;
  const tries = `${n} ${n === 1 ? "tentativa" : "tentativas"}`;
  const summary = result.player_exact_hit
    ? `♾️ Cravei em ${tries}! 🎯`
    : `♾️ Maior pontuação: ${result.player_best_score}/100 após ${tries}`;

  return [header, challenge.subtheme_title, "Modo Infinito", summary];
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
