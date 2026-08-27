import { useEffect, useRef } from "react";

const ADS_ENABLED = import.meta.env.VITE_ENABLE_ADS === "true";
const ADSENSE_CLIENT = import.meta.env.VITE_ADSENSE_CLIENT_ID as string | undefined;

declare global {
  interface Window {
    adsbygoogle?: unknown[];
  }
}

/**
 * Reserved ad slot. Renders nothing until VITE_ENABLE_ADS=true and a real
 * VITE_ADSENSE_CLIENT_ID are set (AdSense only approves a live domain, so this
 * stays off during local dev / before the domain is approved).
 */
export default function AdSlot({ slot }: { slot: "top" | "bottom" | "inline" }) {
  const ref = useRef<HTMLModElement>(null);

  useEffect(() => {
    if (!ADS_ENABLED || !ADSENSE_CLIENT) return;
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch {
      // AdSense script not loaded yet or blocked (ad blocker); fail silently.
    }
  }, []);

  if (!ADS_ENABLED || !ADSENSE_CLIENT) return null;

  return (
    <div className="mx-auto my-2 w-full max-w-2xl px-4" data-ad-slot-position={slot}>
      <ins
        ref={ref}
        className="adsbygoogle block"
        style={{ display: "block" }}
        data-ad-client={ADSENSE_CLIENT}
        data-ad-format="auto"
        data-full-width-responsive="true"
      />
    </div>
  );
}
