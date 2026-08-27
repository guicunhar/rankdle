import { useQuery } from "@tanstack/react-query";

import { fetchThemes } from "../api/endpoints";
import ThemeCard from "../components/ThemeCard";

export default function Home() {
  const { data: themes, isLoading, isError } = useQuery({
    queryKey: ["themes"],
    queryFn: fetchThemes,
  });

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-ink-50">Escolha um tema</h1>
        <p className="mt-1 text-sm text-ink-400">
          Todo dia um novo ranking em cada tema. Acerte a posição exata ou chegue perto.
        </p>
      </div>

      {isLoading && <p className="text-sm text-ink-400">Carregando temas...</p>}
      {isError && (
        <p className="rounded-lg border border-bad/30 bg-bad/10 px-4 py-3 text-sm text-bad">
          Não foi possível carregar os temas agora.
        </p>
      )}

      <div className="flex flex-col gap-2.5">
        {themes?.map((theme) => (
          <ThemeCard key={theme.id} theme={theme} />
        ))}
      </div>
    </div>
  );
}
