"use client";

/**
 * A row of the next 7 days under a delivery check. The checked day is
 * coloured by the result (green = can deliver, amber = full), and the next
 * available day is marked. Tapping another day asks Rukmani to check it.
 */

import { useChatActions } from "@/components/chat/ChatActions";
import { addDays, sriLankaToday } from "@/lib/format";

interface DateStripProps {
  city: string;
  productId: string | null;
  checkedDate: string;
  available: boolean;
  nextAvailableDate: string | null;
}

const DAYS_SHOWN = 7;

export function DateStrip({ city, productId, checkedDate, available, nextAvailableDate }: DateStripProps) {
  const { send, isReplying } = useChatActions();
  const today = sriLankaToday();
  const days = Array.from({ length: DAYS_SHOWN }, (_, i) => addDays(today, i));

  function check(date: string) {
    const item = productId ? ` for ${productId}` : "";
    send(`Can you deliver to ${city} on ${date}${item}?`);
  }

  return (
    <div className="no-scrollbar -mx-1 flex gap-1.5 overflow-x-auto px-1" role="group" aria-label="Pick a delivery date">
      {days.map((date) => {
        const isChecked = date === checkedDate;
        const isNext = date === nextAvailableDate;
        const style = isChecked
          ? available
            ? "bg-success text-white"
            : "bg-gold/25 text-ink ring-1 ring-gold"
          : isNext
            ? "bg-success/15 text-success ring-1 ring-success"
            : "bg-brand-mist text-ink-soft hover:bg-brand-muted/30";
        const [, , dayOfMonth] = date.split("-");
        const weekday = new Date(`${date}T00:00:00`).toLocaleDateString("en-GB", { weekday: "short" });

        return (
          <button
            key={date}
            type="button"
            onClick={() => check(date)}
            disabled={isReplying || isChecked}
            aria-label={`Check delivery on ${date}`}
            className={`flex w-12 shrink-0 flex-col items-center rounded-xl py-1.5 text-xs transition disabled:cursor-default ${style}`}
          >
            <span>{weekday}</span>
            <span className="text-base font-semibold">{Number(dayOfMonth)}</span>
          </button>
        );
      })}
    </div>
  );
}
