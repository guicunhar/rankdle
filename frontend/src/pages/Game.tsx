import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle,
  ArrowRight,
  ExternalLink,
  Flag,
  Infinity as InfinityIcon,
  PartyPopper,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";

import { fetchDaily, fetchResult, fetchThemes, giveUp, submitGuess } from "../api/endpoints";
import type { GameMode, SearchItem } from "../api/types";
import GuessHistory from "../components/GuessHistory";
import LivesIndicator from "../components/LivesIndicator";
import SearchBar from "../components/SearchBar";
import ShareCard from "../components/ShareCard";
import { formatDateBR } from "../lib/date";
import { ordinal } from "../lib/ordinal";
import { scoreColor } from "../lib/scoreColor";
import { iconForTheme } from "../lib/themeIcons";

export default function Game() {
  const { themeSlug, date } = useParams<{ themeSlug: string; date?: string }>();
  const [searchParams] = useSearchParams();
  const mode: GameMode = searchParams.get("mode") === "infinite" ? "infinite" : "lives";

  const queryClient = useQueryClient();
  const [selected, setSelected] = useState<SearchItem | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // null = ainda não decidiu; "answer" = pediu para ver a resposta;
  // "infinite" = seguiu para o modo infinito (também libera o resultado das 5
  // vidas, já que a partida vira uma continuação da mesma resposta).
  const [reveal, setReveal] = useState<null | "answer" | "infinite">(null);

  const basePath = date ? `/jogar/${themeSlug}/${date}` : `/jogar/${themeSlug}`;

  const dailyKey = ["daily", themeSlug, date, mode];
  const dailyQuery = useQuery({
    queryKey: dailyKey,
    queryFn: () => fetchDaily(themeSlug!, date, mode),
    enabled: !!themeSlug,
  });

  const challenge = dailyQuery.data;

  // Only worth offering "play another theme" when there actually is another
  // one active. Shares React Query's cache with the Home picker.
  const { data: themes } = useQuery({ queryKey: ["themes"], queryFn: fetchThemes });
  const hasOtherThemes = (themes?.length ?? 0) > 1;

  const exactHit = challenge?.guesses.some((g) => g.direction === "correct") ?? false;

  // No modo 5 vidas quem não cravou a posição precisa escolher entre seguir no
  // modo infinito ou ver a resposta — a resposta não pode aparecer antes dessa
  // escolha. Quem cravou (ou já está no modo infinito) vê o resultado direto.
  const canSeeResult =
    !!challenge?.is_over && (mode === "infinite" || exactHit || reveal !== null);
  const startedInfinite = reveal === "infinite";

  // Voltar do modo infinito para a tela das 5 vidas não deve pedir a decisão de
  // novo: quem foi para o infinito já topou a resposta de um jeito ou de outro.
  const revealStorageKey = challenge ? `rankdle:reveal:${challenge.id}` : null;
  useEffect(() => {
    if (!revealStorageKey) return;
    try {
      const stored = sessionStorage.getItem(revealStorageKey);
      if (stored === "answer" || stored === "infinite") setReveal(stored);
    } catch {
      /* sessionStorage indisponível: sem problema, o gate continua aparecendo */
    }
  }, [revealStorageKey]);

  function rememberReveal(choice: "answer" | "infinite") {
    setReveal(choice);
    try {
      if (revealStorageKey) sessionStorage.setItem(revealStorageKey, choice);
    } catch {
      /* ignore */
    }
  }

  const resultQuery = useQuery({
    queryKey: ["result", challenge?.id, mode],
    queryFn: () => fetchResult(challenge!.id, mode),
    enabled: canSeeResult,
  });

  async function refreshGame() {
    await queryClient.invalidateQueries({ queryKey: dailyKey });
    if (challenge) {
      await queryClient.invalidateQueries({ queryKey: ["result", challenge.id, mode] });
    }
  }

  async function handleConfirm() {
    if (!challenge || !selected) return;
    setError(null);
    setSubmitting(true);
    try {
      await submitGuess(challenge.id, selected.id, mode);
      setSelected(null);
      await refreshGame();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível registrar o palpite.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleGiveUp() {
    if (!challenge) return;
    if (!window.confirm("Desistir e revelar a resposta?")) return;
    setError(null);
    setSubmitting(true);
    try {
      await giveUp(challenge.id);
      setSelected(null);
      await refreshGame();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível encerrar o jogo.");
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
  const isInfinite = mode === "infinite";

  return (
    <div className="flex flex-col gap-5">
      <div className="rounded-lg border border-ink-800 bg-ink-900 px-5 py-6">
        <div className="flex flex-wrap items-center gap-x-2 gap-y-1.5 text-xs font-semibold uppercase tracking-wider text-accent-400">
          <span className="flex items-center gap-1.5">
            <ThemeIcon size={14} strokeWidth={2.5} />
            {challenge.theme} · {formatDateBR(challenge.date)}
          </span>
          {isInfinite && (
            <span className="inline-flex items-center gap-1 rounded-md border border-accent-500/40 bg-accent-500/10 px-2 py-0.5 text-[11px] text-accent-300">
              <InfinityIcon size={12} strokeWidth={2.75} />
              Modo infinito
            </span>
          )}
        </div>
        <h1 className="mt-2 font-display text-lg font-semibold text-ink-50">{challenge.subtheme_title}</h1>
        <p className="mt-3 text-lg text-ink-200">
          Qual é a{" "}
          <strong className="font-mono font-bold text-accent-400">{ordinal(challenge.target_rank)}</strong>{" "}
          posição desse ranking?
        </p>
      </div>

      <div className="flex items-center justify-between">
        {isInfinite ? (
          <span className="flex items-center gap-2 text-sm">
            <InfinityIcon size={18} strokeWidth={2.25} className="text-accent-400" />
            <span className="font-mono text-ink-300">
              tentativas: <strong className="text-ink-50">{challenge.attempts_used}</strong>
            </span>
          </span>
        ) : (
          <LivesIndicator total={challenge.lives_total} remaining={challenge.lives_remaining} />
        )}
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
          {isInfinite && challenge.attempts_used > 0 && (
            <button
              type="button"
              onClick={handleGiveUp}
              disabled={submitting}
              className="flex items-center justify-center gap-2 rounded-lg border border-ink-700 px-6 py-2.5 text-sm font-semibold text-ink-300 transition hover:border-bad/50 hover:text-bad disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Flag size={15} strokeWidth={2.5} />
              Desistir e ver a resposta
            </button>
          )}
        </div>
      )}
      {error && (
        <p className="flex items-center gap-2 text-sm font-medium text-bad">
          <AlertTriangle size={16} /> {error}
        </p>
      )}

      <GuessHistory guesses={challenge.guesses} limitHeight={isInfinite} />

      {challenge.is_over && mode === "lives" && !exactHit && reveal === null && (
        <div className="flex flex-col gap-4 rounded-lg border border-accent-500/40 bg-accent-500/[0.06] p-5">
          <div>
            <h2 className="flex items-center gap-2 font-display text-lg font-bold text-ink-50">
              <Flag size={20} className="text-accent-400" />
              Fim das 5 vidas
            </h2>
            <p className="mt-1.5 text-sm text-ink-300">
              Você ainda não cravou a posição. Dá para continuar tentando sem
              limite no modo infinito — ou ver a resposta agora e encerrar.
            </p>
          </div>
          <div className="flex flex-col gap-2 sm:flex-row">
            <Link
              to={`${basePath}?mode=infinite`}
              onClick={() => rememberReveal("infinite")}
              className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-accent-500 px-5 py-3 font-display font-bold text-ink-950 transition hover:bg-accent-400"
            >
              <InfinityIcon size={16} strokeWidth={2.75} />
              Continuar no modo infinito
            </Link>
            <button
              type="button"
              onClick={() => rememberReveal("answer")}
              className="flex flex-1 items-center justify-center rounded-lg border border-ink-700 px-5 py-3 text-sm font-semibold text-ink-300 transition hover:border-ink-500 hover:text-ink-100"
            >
              Ver a resposta
            </button>
          </div>
        </div>
      )}

      {challenge.is_over && canSeeResult && (
        <div className="flex flex-col gap-4 rounded-lg border border-accent-500/40 bg-accent-500/[0.06] p-5">
          <div>
            <h2 className="flex items-center gap-2 font-display text-lg font-bold text-ink-50">
              <PartyPopper size={20} className="text-accent-400" />
              {isInfinite ? "Fim do modo infinito!" : "Fim de jogo!"}
            </h2>
            {resultQuery.data && (
              <p className="mt-1.5 text-sm text-ink-300">
                A resposta era <strong className="text-ink-50">{resultQuery.data.answer.name}</strong> (
                {ordinal(resultQuery.data.answer.rank)} posição).
              </p>
            )}
            {resultQuery.data?.source_url && (
              <a
                href={resultQuery.data.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-2 inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-accent-400 hover:underline"
              >
                <ExternalLink size={13} strokeWidth={2.5} />
                Fonte dos dados
              </a>
            )}
          </div>
          <div className="flex items-baseline justify-center gap-2 rounded-lg border border-ink-800 bg-ink-950 px-4 py-3 text-center">
            <span className="text-xs font-semibold uppercase tracking-wider text-ink-400">
              Sua melhor pontuação
            </span>
            <span className={`font-mono text-2xl font-bold tabular-nums ${scoreColor(challenge.best_score)}`}>
              {challenge.best_score}
            </span>
            {isInfinite && (
              <span className="text-xs text-ink-500">em {challenge.attempts_used} tentativas</span>
            )}
          </div>
          {mode === "lives" && resultQuery.data && resultQuery.data.players_count > 0 && (
            <dl className="grid grid-cols-3 divide-x divide-ink-800 overflow-hidden rounded-lg border border-ink-800 bg-ink-950 text-center">
              <StatCell label="Jogaram hoje" value={resultQuery.data.players_count} />
              <StatCell label="Melhor pontuação" value={resultQuery.data.closest_score ?? challenge.best_score} />
              <StatCell label="Média" value={Math.round(resultQuery.data.average_score ?? 0)} />
            </dl>
          )}
          {resultQuery.data && <ShareCard challenge={challenge} result={resultQuery.data} />}
          <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-center text-sm font-semibold">
            {mode === "lives" ? (
              <>
                {hasOtherThemes && (
                  <>
                    <Link to="/" className="text-accent-400 hover:underline">
                      Jogar outro tema hoje
                    </Link>
                    <span className="text-ink-700">·</span>
                  </>
                )}
                <Link to={`/arquivo/${themeSlug}`} className="text-accent-400 hover:underline">
                  Jogar um dia anterior
                </Link>
                {startedInfinite && (
                  <>
                    <span className="text-ink-700">·</span>
                    <Link
                      to={`${basePath}?mode=infinite`}
                      className="inline-flex items-center gap-1 text-accent-400 hover:underline"
                    >
                      <InfinityIcon size={14} strokeWidth={2.75} />
                      Voltar ao modo infinito
                    </Link>
                  </>
                )}
              </>
            ) : (
              <>
                <Link to={basePath} className="text-accent-400 hover:underline">
                  Ver resultado do modo 5 vidas
                </Link>
                <span className="text-ink-700">·</span>
                <Link to={`/arquivo/${themeSlug}`} className="text-accent-400 hover:underline">
                  Jogar um dia anterior
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function StatCell({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex flex-col items-center px-2 py-3">
      <dt className="flex min-h-[2.4em] items-start text-[11px] font-medium leading-tight text-ink-400">
        {label}
      </dt>
      <dd className="mt-0.5 font-mono text-lg font-bold tabular-nums text-ink-50">{value}</dd>
    </div>
  );
}
