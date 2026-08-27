import { Search, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { searchItems } from "../api/endpoints";
import type { SearchItem } from "../api/types";

interface Props {
  challengeId: number;
  disabled?: boolean;
  value: SearchItem | null;
  onChange: (item: SearchItem | null) => void;
}

// With no query typed yet, fetch (almost) the whole list so people can browse
// for a name they recognize instead of having to know what to type; a typed
// query only needs a handful of matching suggestions.
const BROWSE_LIMIT = 200;
const SUGGEST_LIMIT = 8;

export default function SearchBar({ challengeId, disabled, value, onChange }: Props) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchItem[]>([]);
  const [open, setOpen] = useState(false);
  const [focused, setFocused] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Always fetch — an empty query browses the full (shuffled) option list,
  // a typed query narrows it down.
  useEffect(() => {
    const trimmed = query.trim();
    const handle = setTimeout(() => {
      searchItems(challengeId, trimmed, trimmed ? SUGGEST_LIMIT : BROWSE_LIMIT)
        .then(setResults)
        .catch(() => setResults([]));
    }, 200);
    return () => clearTimeout(handle);
  }, [query, challengeId]);

  // Only pop the dropdown open once the field is actually focused, so the
  // background browse-list fetch on mount doesn't surprise-open it.
  useEffect(() => {
    if (focused && results.length > 0) setOpen(true);
  }, [focused, results]);

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
        setFocused(false);
      }
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  function handlePick(item: SearchItem) {
    onChange(item);
    setQuery("");
    setOpen(false);
    setFocused(false);
  }

  if (value) {
    return (
      <div className="flex items-center justify-between gap-3 rounded-lg border border-accent-500/50 bg-ink-900 px-4 py-3">
        <div className="flex items-center gap-3 min-w-0">
          {value.image_url && (
            <img src={value.image_url} alt="" className="h-8 w-8 rounded object-cover" />
          )}
          <span className="truncate font-medium text-ink-50">{value.name}</span>
        </div>
        <button
          type="button"
          onClick={() => onChange(null)}
          disabled={disabled}
          aria-label="Trocar palpite"
          className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-ink-400 hover:bg-ink-800 hover:text-ink-50 disabled:opacity-40"
        >
          <X size={16} strokeWidth={2.5} />
        </button>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="relative">
      <div className="relative">
        <Search
          size={16}
          strokeWidth={2.5}
          className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-500"
        />
        <input
          type="text"
          inputMode="search"
          disabled={disabled}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setFocused(true)}
          placeholder={disabled ? "Jogo encerrado" : "Digite ou toque para ver as opções"}
          className="w-full rounded-lg border border-ink-700 bg-ink-900 py-3 pl-10 pr-4 text-base text-ink-50 outline-none placeholder:text-ink-500 focus:border-accent-500 disabled:bg-ink-950 disabled:text-ink-600"
        />
      </div>
      {open && results.length > 0 && (
        <ul className="absolute z-10 mt-1.5 max-h-64 w-full overflow-y-auto rounded-lg border border-ink-700 bg-ink-900 shadow-xl shadow-black/40">
          {results.map((item) => (
            <li key={item.id}>
              <button
                type="button"
                onClick={() => handlePick(item)}
                className="flex w-full items-center gap-3 px-4 py-2.5 text-left text-ink-100 hover:bg-ink-800"
              >
                {item.image_url && (
                  <img src={item.image_url} alt="" className="h-8 w-8 rounded object-cover" />
                )}
                <span>{item.name}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
