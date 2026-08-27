import { Check, Copy, Share2 } from "lucide-react";
import { useState } from "react";

import type { DailyChallenge, DailyResult } from "../api/types";
import { buildShareText, copyToClipboard, shareUrls } from "../lib/share";

export default function ShareCard({
  challenge,
  result,
}: {
  challenge: DailyChallenge;
  result: DailyResult;
}) {
  const [copied, setCopied] = useState(false);
  const text = buildShareText(challenge, result);
  const urls = shareUrls(text);

  async function handleCopy() {
    const ok = await copyToClipboard(text);
    setCopied(ok);
    if (ok) setTimeout(() => setCopied(false), 2000);
  }

  async function handleNativeShare() {
    if (navigator.share) {
      try {
        await navigator.share({ text });
      } catch {
        // user cancelled the share sheet; nothing to do
      }
    } else {
      handleCopy();
    }
  }

  return (
    <div className="rounded-lg border border-ink-800 bg-ink-950 p-4">
      <pre className="mb-3 whitespace-pre-wrap font-mono text-xs leading-relaxed text-ink-200">{text}</pre>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={handleNativeShare}
          className="flex items-center gap-1.5 rounded-md bg-accent-500 px-3.5 py-2 text-sm font-bold text-ink-950 hover:bg-accent-400"
        >
          <Share2 size={15} strokeWidth={2.5} />
          Compartilhar
        </button>
        <a
          href={urls.whatsapp}
          target="_blank"
          rel="noreferrer"
          className="rounded-md border border-ink-700 px-3.5 py-2 text-sm font-semibold text-ink-100 hover:bg-ink-800"
        >
          WhatsApp
        </a>
        <a
          href={urls.x}
          target="_blank"
          rel="noreferrer"
          className="rounded-md border border-ink-700 px-3.5 py-2 text-sm font-semibold text-ink-100 hover:bg-ink-800"
        >
          X
        </a>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 rounded-md border border-ink-700 px-3.5 py-2 text-sm font-semibold text-ink-100 hover:bg-ink-800"
        >
          {copied ? <Check size={15} strokeWidth={2.5} /> : <Copy size={15} strokeWidth={2.5} />}
          {copied ? "Copiado" : "Copiar"}
        </button>
      </div>
    </div>
  );
}
