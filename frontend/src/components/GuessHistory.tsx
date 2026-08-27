import { Check, ChevronDown, ChevronUp } from "lucide-react";

import type { GuessResult } from "../api/types";

// "lower"/"higher" describe the GUESS's rank relative to the answer's rank
// (backend's direction_for_guess): guess rank lower than the target means the
// real answer sits further down the list (bigger rank number), and vice-versa.
const directionCopy: Record<GuessResult["direction"], { label: string; icon: typeof ChevronDown | null }> = {
  correct: { label: "Na mosca", icon: Check },
  lower: { label: "A resposta está mais abaixo", icon: ChevronDown },
  higher: { label: "A resposta está mais acima", icon: ChevronUp },
};

function scoreColor(score: number): string {
  if (score >= 100) return "text-good";
  if (score >= 50) return "text-accent-400";
  return "text-bad";
}

export default function GuessHistory({ guesses }: { guesses: GuessResult[] }) {
  if (guesses.length === 0) return null;

  return (
    <ul className="flex flex-col gap-1.5">
      {guesses.map((g, i) => {
        const { label, icon: Icon } = directionCopy[g.direction];
        return (
          <li
            key={i}
            className="flex items-center justify-between gap-3 rounded-lg border border-ink-800 bg-ink-900 px-4 py-3"
          >
            <div className="min-w-0">
              <div className="truncate font-medium text-ink-100">{g.item_name}</div>
              <div className="mt-0.5 flex items-center gap-1 text-xs text-ink-400">
                {Icon && <Icon size={13} strokeWidth={2.5} />}
                {label}
              </div>
            </div>
            <span className={`shrink-0 font-mono text-sm font-bold tabular-nums ${scoreColor(g.score)}`}>
              {g.score}
            </span>
          </li>
        );
      })}
    </ul>
  );
}
