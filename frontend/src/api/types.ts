export interface Theme {
  id: number;
  slug: string;
  name: string;
  icon: string;
}

export interface GuessResult {
  rank_guessed: number;
  item_name: string;
  score: number;
  diff: number;
  direction: "correct" | "higher" | "lower";
}

export interface DailyChallenge {
  id: number;
  date: string;
  theme: string;
  theme_icon: string;
  subtheme_title: string;
  target_rank: number;
  total_items: number;
  lives_total: number;
  lives_remaining: number;
  attempts_used: number;
  guesses: GuessResult[];
  is_over: boolean;
  best_score: number;
}

export interface SearchItem {
  id: number;
  name: string;
  image_url: string | null;
}

export interface GuessResponse {
  guess: GuessResult;
  lives_remaining: number;
  best_score: number;
  is_over: boolean;
  exact_hit: boolean;
}

export interface RevealItem {
  rank: number;
  name: string;
  image_url: string | null;
}

export interface DailyResult {
  daily_challenge_id: number;
  target_rank: number;
  answer: RevealItem;
  player_best_score: number;
  player_exact_hit: boolean;
  player_guesses: GuessResult[];
  players_count: number;
  exact_hit_count: number;
  closest_score: number | null;
  average_score: number | null;
}

export interface ArchiveEntry {
  id: number;
  date: string;
  subtheme_title: string;
  played: boolean;
  best_score: number | null;
}

export interface MeInfo {
  id: number;
  email: string | null;
  is_guest: boolean;
  games_played: number;
  exact_hits: number;
}
