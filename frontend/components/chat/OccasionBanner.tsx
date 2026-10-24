"use client";

/**
 * "Christmas is in 62 days — Find a Christmas gift": a gentle nudge on the
 * welcome screen for the next Sri Lankan gifting occasion.
 *
 * The date is read in the browser after the first render (the page itself
 * is pre-built, so it can't know today's date).
 */

import { useEffect, useState } from "react";
import { CalendarHeart } from "lucide-react";
import { useLanguage } from "@/components/LanguageProvider";
import { sriLankaToday } from "@/lib/format";
import { nextOccasion, type UpcomingOccasion } from "@/lib/occasions";

export function OccasionBanner({ onPick }: { onPick: (message: string) => void }) {
  const { lang, t } = useLanguage();
  const [occasion, setOccasion] = useState<UpcomingOccasion | null>(null);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- today's date is only known in the browser
    setOccasion(nextOccasion(sriLankaToday(), lang));
  }, [lang]);

  if (!occasion) return null;

  return (
    <div className="mt-6 flex w-full flex-wrap items-center justify-center gap-x-3 gap-y-2 rounded-2xl bg-brand px-4 py-3 text-sm text-white shadow-md">
      <span className="flex items-center gap-2">
        <span aria-hidden className="text-lg">{occasion.emoji}</span>
        {occasion.daysAway === 0
          ? t.occasionToday(occasion.name)
          : t.occasionSoon(occasion.name, occasion.daysAway)}
      </span>
      <button
        type="button"
        onClick={() => onPick(t.occasionMessage(occasion.name))}
        className="flex items-center gap-1.5 rounded-full bg-sun px-3 py-1 font-semibold text-brand transition hover:brightness-95"
      >
        <CalendarHeart className="size-4" aria-hidden />
        {t.occasionCta(occasion.name)}
      </button>
    </div>
  );
}
