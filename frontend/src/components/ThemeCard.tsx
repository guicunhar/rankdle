import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

import type { Theme } from "../api/types";
import { iconForTheme } from "../lib/themeIcons";

export default function ThemeCard({ theme }: { theme: Theme }) {
  const Icon = iconForTheme(theme.slug);

  return (
    <Link
      to={`/jogar/${theme.slug}`}
      className="group flex items-center gap-4 rounded-lg border border-ink-800 bg-ink-900 p-4 transition hover:border-accent-500/60 hover:bg-ink-850"
    >
      <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-md bg-ink-800 text-accent-400 group-hover:bg-accent-500/10">
        <Icon size={22} strokeWidth={2} />
      </span>
      <div className="min-w-0 flex-1">
        <div className="font-display text-base font-semibold text-ink-50">{theme.name}</div>
        <div className="text-sm text-ink-400">Desafio de hoje</div>
      </div>
      <ArrowRight
        size={18}
        className="shrink-0 text-ink-600 transition group-hover:translate-x-0.5 group-hover:text-accent-400"
      />
    </Link>
  );
}
