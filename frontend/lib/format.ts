/** Small display helpers for prices and dates. */

import type { Money } from "./types";

/** "LKR 5,950" — or a dash when Kapruka has no price. */
export function formatMoney(money: Money | null | undefined): string {
  if (!money || money.amount === null) return "—";
  return `${money.currency} ${Math.round(money.amount).toLocaleString("en-LK")}`;
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
