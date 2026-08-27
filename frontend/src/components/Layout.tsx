import { ListOrdered } from "lucide-react";
import type { ReactNode } from "react";
import { Link } from "react-router-dom";

import AdSlot from "./AdSlot";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-full flex-col">
      <header className="border-b border-ink-800">
        <div className="mx-auto flex max-w-2xl items-center px-4 py-4">
          <Link to="/" className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-md bg-accent-500 text-ink-950">
              <ListOrdered size={18} strokeWidth={2.5} />
            </span>
            <span className="font-display text-lg font-bold tracking-tight text-ink-50">
              rankdle
            </span>
          </Link>
        </div>
      </header>

      <AdSlot slot="top" />

      <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-6">{children}</main>

      <AdSlot slot="bottom" />

      <footer className="flex items-center justify-between border-t border-ink-800 px-4 py-5 text-xs text-ink-500">
        <span>© {new Date().getFullYear()} Rankdle</span>
        <span>Um jogo diário de rankings</span>
      </footer>
    </div>
  );
}
