import { useEffect, useRef } from "react";

const ADS_ENABLED = import.meta.env.VITE_ENABLE_ADS === "true";
const ADSENSE_CLIENT = import.meta.env.VITE_ADSENSE_CLIENT_ID;

// Each placement in the page can be its own AdSense "Display ad" unit, with
// its own slot id from the AdSense dashboard (Ads -> By ad unit -> Display ads).
const AD_SLOTS: Record<"top" | "bottom", string | undefined> = {
  top: import.meta.env.VITE_ADSENSE_SLOT_TOP,
  bottom: import.meta.env.VITE_ADSENSE_SLOT_BOTTOM,
};

declare global {
  interface Window {
    adsbygoogle?: unknown[];
  }
}

/**
 * Reserved ad slot. Renders nothing until VITE_ENABLE_ADS=true, a real
 * VITE_ADSENSE_CLIENT_ID, and a slot id for this placement are all set
 * (AdSense only approves a live domain, so this stays off during local dev /
 * before the site is approved — see README.md for the full setup steps).
 */
export default function AdSlot({ slot }: { slot: "top" | "bottom" }) {
  const slotId = AD_SLOTS[slot];
  const ref = useRef<HTMLModElement>(null);

  useEffect(() => {
    if (!ADS_ENABLED || !ADSENSE_CLIENT || !slotId) return;
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch {
      // AdSense script not loaded yet or blocked (ad blocker); fail silently.
    }
  }, [slotId]);

  if (!ADS_ENABLED || !ADSENSE_CLIENT || !slotId) return null;

  return (
    <div className="mx-auto my-2 w-full max-w-2xl px-4" data-ad-slot-position={slot}>
      <ins
        ref={ref}
        className="adsbygoogle block"
        style={{ display: "block" }}
        data-ad-client={ADSENSE_CLIENT}
        data-ad-slot={slotId}
        data-ad-format="auto"
        data-full-width-responsive="true"
      />
    </div>
  );
}
