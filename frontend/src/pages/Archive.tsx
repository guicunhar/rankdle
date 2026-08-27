import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { fetchArchive } from "../api/endpoints";
import { formatDateBR } from "../lib/date";

export default function Archive() {
  const { themeSlug } = useParams<{ themeSlug: string }>();

  const { data: entries, isLoading, isError } = useQuery({
    queryKey: ["archive", themeSlug],
    queryFn: () => fetchArchive(themeSlug!),
    enabled: !!themeSlug,
  });

  return (
    <div className="flex flex-col gap-4">
      <h1 className="font-display text-xl font-bold text-ink-50">Dias anteriores</h1>

      {isLoading && <p className="text-sm text-ink-400">Carregando...</p>}
      {isError && (
        <p className="rounded-lg border border-bad/30 bg-bad/10 px-4 py-3 text-sm text-bad">
          Não foi possível carregar o arquivo.
        </p>
      )}
      {entries && entries.length === 0 && (
        <p className="text-sm text-ink-500">Nenhum desafio anterior ainda.</p>
      )}

      <ul className="flex flex-col gap-2">
        {entries?.map((entry) => (
          <li key={entry.id}>
            <Link
              to={`/jogar/${themeSlug}/${entry.date}`}
              className="flex items-center justify-between gap-3 rounded-lg border border-ink-800 bg-ink-900 px-4 py-3 hover:border-accent-500/50"
            >
              <div className="min-w-0">
                <div className="truncate font-medium text-ink-100">{entry.subtheme_title}</div>
                <div className="font-mono text-xs text-ink-500">{formatDateBR(entry.date)}</div>
              </div>
              {entry.played ? (
                <span className="shrink-0 rounded-md bg-accent-500 px-2.5 py-1 font-mono text-xs font-bold text-ink-950">
                  {entry.best_score}
                </span>
              ) : (
                <span className="shrink-0 rounded-md border border-ink-700 px-2.5 py-1 text-xs font-semibold text-ink-300">
                  Jogar
                </span>
              )}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
