/** Small display helpers for prices and dates. */

import type { Money } from "./types";

/** "LKR 5,950" — or a dash when Kapruka has no price. */
export function formatMoney(money: Money | null | undefined): string {
  if (!money || money.amount === null) return "—";
  return `${money.currency} ${Math.round(money.amount).toLocaleString("en-LK")}`;
}

/** Today's date in Sri Lanka as YYYY-MM-DD (Kapruka's dates are Sri Lanka dates). */
export function sriLankaToday(): string {
  // The "en-CA" locale formats dates as YYYY-MM-DD.
  return new Date().toLocaleDateString("en-CA", { timeZone: "Asia/Colombo" });
}

/** A YYYY-MM-DD date plus some days, as YYYY-MM-DD. */
export function addDays(isoDate: string, days: number): string {
  const [year, month, day] = isoDate.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day + days));
  return date.toISOString().slice(0, 10);
}

/** "Sat, 25 Oct" from "2026-10-25". Parsed as a plain date so no time zone shifts it. */
export function formatDate(isoDate: string): string {
  const [year, month, day] = isoDate.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString("en-GB", {
    weekday: "short",
    day: "numeric",
    month: "short",
  });
}
