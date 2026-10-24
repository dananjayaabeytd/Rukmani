/**
 * Sri Lankan gifting occasions, for the "coming up soon" banner.
 *
 * Only occasions with a predictable date are listed: fixed calendar days,
 * plus Mother's Day (2nd Sunday of May) and Father's Day (3rd Sunday of
 * June). Festivals on the lunar calendar (Vesak, Deepavali, ...) move every
 * year, so they're left out rather than risk showing a wrong date.
 */

import type { Lang } from "./i18n";

interface Occasion {
  emoji: string;
  name: Record<Lang, string>;
  /** The occasion's date in a given year (month is 1–12). */
  dateIn: (year: number) => { month: number; day: number };
}

const fixed = (month: number, day: number) => () => ({ month, day });

/** The day of the month of the nth Sunday (n = 1, 2, 3...) in a month. */
function nthSunday(year: number, month: number, n: number): number {
  const firstWeekday = new Date(Date.UTC(year, month - 1, 1)).getUTCDay(); // 0 = Sunday
  return 1 + ((7 - firstWeekday) % 7) + (n - 1) * 7;
}

const OCCASIONS: Occasion[] = [
  { emoji: "🎆", name: { en: "New Year", si: "නව වසර", ta: "புத்தாண்டு" }, dateIn: fixed(1, 1) },
  { emoji: "🌾", name: { en: "Thai Pongal", si: "තෛපොංගල්", ta: "தைப்பொங்கல்" }, dateIn: fixed(1, 14) },
  { emoji: "💝", name: { en: "Valentine's Day", si: "වැලන්ටයින් දිනය", ta: "காதலர் தினம்" }, dateIn: fixed(2, 14) },
  { emoji: "🌷", name: { en: "Women's Day", si: "කාන්තා දිනය", ta: "மகளிர் தினம்" }, dateIn: fixed(3, 8) },
  {
    emoji: "🪔",
    name: { en: "Sinhala & Tamil New Year", si: "සිංහල හා දෙමළ අලුත් අවුරුද්ද", ta: "சித்திரைப் புத்தாண்டு" },
    dateIn: fixed(4, 13),
  },
  {
    emoji: "💐",
    name: { en: "Mother's Day", si: "මව්වරුන්ගේ දිනය", ta: "அன்னையர் தினம்" },
    dateIn: (year) => ({ month: 5, day: nthSunday(year, 5, 2) }),
  },
  {
    emoji: "👔",
    name: { en: "Father's Day", si: "පියවරුන්ගේ දිනය", ta: "தந்தையர் தினம்" },
    dateIn: (year) => ({ month: 6, day: nthSunday(year, 6, 3) }),
  },
  { emoji: "🎈", name: { en: "Children's Day", si: "ළමා දිනය", ta: "சிறுவர் தினம்" }, dateIn: fixed(10, 1) },
  { emoji: "🍎", name: { en: "Teachers' Day", si: "ගුරු දිනය", ta: "ஆசிரியர் தினம்" }, dateIn: fixed(10, 6) },
  { emoji: "🎄", name: { en: "Christmas", si: "නත්තල", ta: "கிறிஸ்துமஸ்" }, dateIn: fixed(12, 25) },
];

export interface UpcomingOccasion {
  emoji: string;
  name: string;
  daysAway: number; // 0 = today
}

/**
 * The next occasion within `withinDays` of `today` (YYYY-MM-DD, Sri Lanka),
 * named in the given language — or null if nothing is coming up.
 */
export function nextOccasion(today: string, lang: Lang, withinDays = 75): UpcomingOccasion | null {
  const [year, month, day] = today.split("-").map(Number);
  const todayUtc = Date.UTC(year, month - 1, day);
  const msPerDay = 86_400_000;

  const upcoming = OCCASIONS.flatMap((occasion) =>
    // Check this year and next, so late-December dates still find January ones.
    [year, year + 1].map((y) => {
      const date = occasion.dateIn(y);
      const daysAway = Math.round((Date.UTC(y, date.month - 1, date.day) - todayUtc) / msPerDay);
      return { emoji: occasion.emoji, name: occasion.name[lang], daysAway };
    }),
  ).filter((o) => o.daysAway >= 0 && o.daysAway <= withinDays);

  upcoming.sort((a, b) => a.daysAway - b.daysAway);
  return upcoming[0] ?? null;
}
