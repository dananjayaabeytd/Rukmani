"use client";

/**
 * The order was created: show the total and a big "Pay now" button that
 * opens Kapruka's secure checkout. Kapruka holds the price for 60 minutes,
 * so a countdown shows how long the link still works.
 */

import { useEffect, useState } from "react";
import { CircleCheck, ExternalLink, Timer } from "lucide-react";
import { formatDate, formatMoney } from "@/lib/format";
import type { Order } from "@/lib/types";

export function PayCard({ order }: { order: Order }) {
  const minutesLeft = useMinutesUntil(order.expires_at);
  const expired = minutesLeft <= 0;

  return (
    <div className="w-full max-w-md overflow-hidden rounded-2xl bg-white shadow-md ring-1 ring-success/30">
      <div className="flex items-center gap-2 bg-success px-4 py-2.5 text-sm font-semibold text-white">
        <CircleCheck className="size-4" aria-hidden />
        Order ready · {order.order_ref}
      </div>

      <div className="flex flex-col gap-3 p-4 text-sm">
        <p className="text-ink-soft">
          Delivery on <strong className="text-ink">{formatDate(order.delivery_date)}</strong>. Pay
          on Kapruka&apos;s secure page to complete it — no account needed.
        </p>

        <a
          href={expired ? undefined : order.checkout_url}
          target="_blank"
          rel="noreferrer"
          aria-disabled={expired}
          className={`flex items-center justify-center gap-2 rounded-full py-3 text-base font-bold transition ${
            expired
              ? "pointer-events-none bg-brand-mist text-brand-muted"
              : "bg-brand text-white hover:bg-brand-deep"
          }`}
        >
          Pay {formatMoney(order.grand_total)} now <ExternalLink className="size-4" aria-hidden />
        </a>

        <p className="flex items-center justify-center gap-1.5 text-xs text-ink-soft">
          <Timer className="size-3.5" aria-hidden />
          {expired
            ? "This link has expired. Ask Rukmani to prepare the checkout again."
            : `Price held for ${minutesLeft} more minute${minutesLeft === 1 ? "" : "s"}`}
        </p>
      </div>
    </div>
  );
}

/** Whole minutes left until an ISO time, refreshed every 30 seconds. */
function useMinutesUntil(isoTime: string): number {
  const deadline = new Date(isoTime).getTime();
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 30_000);
    return () => clearInterval(timer);
  }, []);

  return Math.max(0, Math.ceil((deadline - now) / 60_000));
}
