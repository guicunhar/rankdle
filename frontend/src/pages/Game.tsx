import { useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, ArrowRight, PartyPopper } from "lucide-react";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import { fetchDaily, fetchResult, submitGuess } from "../api/endpoints";
import type { SearchItem } from "../api/types";
import GuessHistory from "../components/GuessHistory";
import LivesIndicator from "../components/LivesIndicator";
import SearchBar from "../components/SearchBar";
import ShareCard from "../components/ShareCard";
import { ordinal } from "../lib/ordinal";
import { iconForTheme } from "../lib/themeIcons";

export default function Game() {
  const { themeSlug, date } = useParams<{ themeSlug: string; date?: string }>();
  const queryClient = useQueryClient();
  const [selected, setSelected] = useState<SearchItem | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const dailyQuery = useQuery({
    queryKey: ["daily", themeSlug, date],
    queryFn: () => fetchDaily(themeSlug!, date),
    enabled: !!themeSlug,
  });

  const challenge = dailyQuery.data;

  const resultQuery = useQuery({
    queryKey: ["result", challenge?.id],
    queryFn: () => fetchResult(challenge!.id),
    enabled: !!challenge?.is_over,
  });

  async function handleConfirm() {
    if (!challenge || !selected) return;
    setError(null);
    setSubmitting(true);
    try {
      await submitGuess(challenge.id, selected.id);
      setSelected(null);
      await queryClient.invalidateQueries({ queryKey: ["daily", themeSlug, date] });
      await queryClient.invalidateQueries({ queryKey: ["result", challenge.id] });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível registrar o palpite.");
    } finally {
      setSubmitting(false);
    }
  }

  if (dailyQuery.isLoading) return <p className="text-sm text-ink-400">Carregando desafio...</p>;
  if (dailyQuery.isError || !challenge) {
    return (
      <div className="flex flex-col gap-3">
        <p className="rounded-lg border border-bad/30 bg-bad/10 px-4 py-3 text-sm text-bad">
          Não há desafio disponível para esse tema/data.
        </p>
        <Link to={`/arquivo/${themeSlug}`} className="text-sm font-semibold text-accent-400 hover:underline">
          Ver dias anteriores
        </Link>
      </div>
    );
  }

  const ThemeIcon = iconForTheme(themeSlug!);

  return (
    <div className="flex flex-col gap-5">
      <div className="rounded-lg border border-ink-800 bg-ink-900 px-5 py-6">
        <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-accent-400">
          <ThemeIcon size={14} strokeWidth={2.5} />
          {challenge.theme} · {challenge.date}
        </div>
        <h1 className="mt-2 font-display text-lg font-semibold text-ink-50">{challenge.subtheme_title}</h1>
        <p className="mt-3 text-lg text-ink-200">
          Qual é a{" "}
          <strong className="font-mono font-bold text-accent-400">{ordinal(challenge.target_rank)}</strong>{" "}
          posição desse ranking?
        </p>
      </div>

      <div className="flex items-center justify-between">
        <LivesIndicator total={challenge.lives_total} remaining={challenge.lives_remaining} />
        <span className="font-mono text-sm text-ink-400">
          melhor: <strong className="text-ink-100">{challenge.best_score}</strong>
        </span>
      </div>

      {!challenge.is_over && (
        <div className="flex flex-col gap-3">
          <SearchBar
            challengeId={challenge.id}
            disabled={submitting}
            value={selected}
            onChange={setSelected}
          />
          <button
            type="button"
            onClick={handleConfirm}
            disabled={!selected || submitting}
            className="flex items-center justify-center gap-2 rounded-lg bg-accent-500 px-6 py-3 font-display font-bold text-ink-950 transition hover:bg-accent-400 disabled:cursor-not-allowed disabled:bg-ink-800 disabled:text-ink-500"
          >
            Conferir
            <ArrowRight size={18} strokeWidth={2.5} />
          </button>
        </div>
      )}
      {error && (
        <p className="flex items-center gap-2 text-sm font-medium text-bad">
          <AlertTriangle size={16} /> {error}
        </p>
      )}

      <GuessHistory guesses={challenge.guesses} />

      {challenge.is_over && (
        <div className="flex flex-col gap-4 rounded-lg border border-accent-500/40 bg-accent-500/[0.06] p-5">
          <div>
            <h2 className="flex items-center gap-2 font-display text-lg font-bold text-ink-50">
              <PartyPopper size={20} className="text-accent-400" />
              Fim de jogo!
            </h2>
            {resultQuery.data && (
              <p className="mt-1.5 text-sm text-ink-300">
                A resposta era <strong className="text-ink-50">{resultQuery.data.answer.name}</strong> (
                {ordinal(resultQuery.data.answer.rank)} posição).{" "}
                {resultQuery.data.players_count > 0 && (
                  <>
                    {resultQuery.data.exact_hit_count} de {resultQuery.data.players_count} jogadores
                    cravaram hoje
                    {resultQuery.data.closest_score !== null &&
                      ` · pontuação mais próxima: ${resultQuery.data.closest_score}`}
                    .
                  </>
                )}
              </p>
            )}
          </div>
          {resultQuery.data && <ShareCard challenge={challenge} result={resultQuery.data} />}
          <Link to={`/arquivo/${themeSlug}`} className="text-sm font-semibold text-accent-400 hover:underline">
            Jogar um dia anterior
          </Link>
        </div>
      )}
    </div>
  );
}
