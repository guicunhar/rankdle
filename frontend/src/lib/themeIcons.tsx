import { Clapperboard, Dices, Music, Sparkles, Trophy, type LucideIcon } from "lucide-react";

const THEME_ICONS: Record<string, LucideIcon> = {
  musica: Music,
  filmes: Clapperboard,
  esportes: Trophy,
  aleatorio: Dices,
};

export function iconForTheme(slug: string): LucideIcon {
  return THEME_ICONS[slug] ?? Sparkles;
}
