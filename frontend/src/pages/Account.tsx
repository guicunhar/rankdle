import { useQuery, useQueryClient } from "@tanstack/react-query";
import { LogOut } from "lucide-react";
import { FormEvent, useState } from "react";

import { fetchMe, login, register } from "../api/endpoints";
import { clearAuthToken, getDeviceId, isLoggedIn, setAuthToken } from "../api/identity";

export default function Account() {
  const queryClient = useQueryClient();
  const loggedIn = isLoggedIn();

  const meQuery = useQuery({ queryKey: ["me"], queryFn: fetchMe, enabled: loggedIn });

  const [mode, setMode] = useState<"login" | "register">("register");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function handleLogout() {
    clearAuthToken();
    queryClient.invalidateQueries();
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const { access_token } =
        mode === "register" ? await register(email, password, getDeviceId()) : await login(email, password);
      setAuthToken(access_token);
      await queryClient.invalidateQueries();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Algo deu errado.");
    } finally {
      setBusy(false);
    }
  }

  if (loggedIn) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="font-display text-xl font-bold text-ink-50">Minha conta</h1>
        {meQuery.isLoading && <p className="text-sm text-ink-400">Carregando...</p>}
        {meQuery.data && (
          <div className="flex flex-col gap-3 rounded-lg border border-ink-800 bg-ink-900 p-5">
            <Row label="E-mail" value={meQuery.data.email ?? "—"} />
            <Row label="Jogos completos" value={meQuery.data.games_played} />
            <Row label="Cravadas" value={meQuery.data.exact_hits} />
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 self-start rounded-md border border-ink-700 px-4 py-2 text-sm font-semibold text-ink-200 hover:bg-ink-900"
        >
          <LogOut size={15} strokeWidth={2.5} />
          Sair
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="font-display text-xl font-bold text-ink-50">
        {mode === "register" ? "Criar conta" : "Entrar"}
      </h1>
      <p className="text-sm text-ink-400">
        Você já pode jogar sem conta — seu progresso fica salvo neste navegador. Crie uma conta para
        sincronizar seu histórico entre dispositivos.
      </p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <input
          type="email"
          required
          placeholder="E-mail"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="rounded-lg border border-ink-700 bg-ink-900 px-4 py-3 text-ink-50 outline-none placeholder:text-ink-500 focus:border-accent-500"
        />
        <input
          type="password"
          required
          minLength={6}
          placeholder="Senha"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="rounded-lg border border-ink-700 bg-ink-900 px-4 py-3 text-ink-50 outline-none placeholder:text-ink-500 focus:border-accent-500"
        />
        {error && <p className="text-sm font-medium text-bad">{error}</p>}
        <button
          type="submit"
          disabled={busy}
          className="rounded-lg bg-accent-500 px-4 py-3 font-display font-bold text-ink-950 hover:bg-accent-400 disabled:opacity-60"
        >
          {mode === "register" ? "Criar conta" : "Entrar"}
        </button>
      </form>

      <button
        onClick={() => setMode(mode === "register" ? "login" : "register")}
        className="text-sm font-semibold text-accent-400 hover:underline"
      >
        {mode === "register" ? "Já tenho conta" : "Criar uma conta nova"}
      </button>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-ink-400">{label}</span>
      <span className="font-mono font-semibold text-ink-50">{value}</span>
    </div>
  );
}
