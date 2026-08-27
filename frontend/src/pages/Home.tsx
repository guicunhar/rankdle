import { useQuery } from "@tanstack/react-query";
import { Gamepad2, Target, type LucideIcon } from "lucide-react";
import { Navigate } from "react-router-dom";

import { fetchMe, fetchThemes } from "../api/endpoints";
import ThemeCard from "../components/ThemeCard";

export default function Home() {
  const { data: themes, isLoading, isError } = useQuery({
    queryKey: ["themes"],
    queryFn: fetchThemes,
  });

  // Performance is tied to a device id kept in this browser's localStorage
  // (see api/identity.ts) — no account needed, it just stays on this device.
  const { data: me } = useQuery({ queryKey: ["me"], queryFn: fetchMe });

  // With a single active theme there's nothing to choose — skip straight to
  // it. The picker comes back on its own the moment a second theme is active.
  if (themes && themes.length === 1) {
    return <Navigate to={`/jogar/${themes[0].slug}`} replace />;
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-ink-50">Escolha um tema</h1>
        <p className="mt-1 text-sm text-ink-400">
          Todo dia um novo ranking em cada tema. Acerte a posição exata ou chegue perto.
        </p>
      </div>

      {me && (
        <div className="flex items-center gap-6 rounded-lg border border-ink-800 bg-ink-900 px-4 py-3">
          <Stat icon={Gamepad2} label="jogos" value={me.games_played} />
          <Stat icon={Target} label="cravadas" value={me.exact_hits} />
        </div>
      )}

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

function Stat({ icon: Icon, label, value }: { icon: LucideIcon; label: string; value: number }) {
  return (
    <div className="flex items-center gap-2">
      <Icon size={16} strokeWidth={2.25} className="text-accent-400" />
      <span className="font-mono font-bold text-ink-50">{value}</span>
      <span className="text-xs text-ink-400">{label}</span>
    </div>
  );
}
