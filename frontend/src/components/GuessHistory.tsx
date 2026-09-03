import { Check, ChevronDown, ChevronUp } from "lucide-react";
import { useEffect, useRef } from "react";

import type { GuessResult } from "../api/types";
import { ordinal } from "../lib/ordinal";
import { scoreColor } from "../lib/scoreColor";

// "lower"/"higher" describe the GUESS's rank relative to the answer's rank
// (backend's direction_for_guess): guess rank lower than the target means the
// real answer sits further down the list (bigger rank number), and vice-versa.
const directionCopy: Record<GuessResult["direction"], { label: string; icon: typeof ChevronDown | null }> = {
  correct: { label: "Na mosca", icon: Check },
  lower: { label: "A resposta está mais abaixo", icon: ChevronDown },
  higher: { label: "A resposta está mais acima", icon: ChevronUp },
};

export default function GuessHistory({
  guesses,
  limitHeight = false,
}: {
  guesses: GuessResult[];
  // Modo infinito: a lista cresce sem limite, então prendemos a altura em ~5
  // linhas e deixamos rolar por dentro, mantendo os últimos palpites à vista.
  limitHeight?: boolean;
}) {
  const listRef = useRef<HTMLUListElement>(null);

  useEffect(() => {
    if (limitHeight && listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [guesses.length, limitHeight]);

  if (guesses.length === 0) return null;

  return (
    <ul
      ref={listRef}
      className={`flex flex-col gap-1.5 ${
        limitHeight ? "max-h-[26rem] overflow-y-auto pr-1" : ""
      }`}
    >
      {guesses.map((g, i) => {
        const { label, icon: Icon } = directionCopy[g.direction];
        return (
          <li
            key={i}
            className="flex items-center justify-between gap-3 rounded-lg border border-ink-800 bg-ink-900 px-4 py-3"
          >
            <div className="flex min-w-0 items-center gap-3">
              <span className="shrink-0 font-mono text-xl font-bold tabular-nums text-ink-50">
                {ordinal(g.rank_guessed)}
              </span>
              <div className="min-w-0">
                <span className="block truncate font-medium text-ink-100">{g.item_name}</span>
                <div className="mt-0.5 flex items-center gap-1 text-xs text-ink-400">
                  {Icon && <Icon size={13} strokeWidth={2.5} />}
                  {label}
                </div>
              </div>
            </div>
            <div className="shrink-0 text-right">
              <span className="block text-[10px] font-semibold uppercase tracking-wider text-ink-500">
                Sua pontuação
              </span>
              <span className={`font-mono text-sm font-bold tabular-nums ${scoreColor(g.score)}`}>
                {g.score}
              </span>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
