"use client";

import { CircleCheck, CircleX, Package } from "lucide-react";
import type { OrderStatus } from "@/lib/types";
import { useLanguage } from "@/components/LanguageProvider";

/** Where a paid order is: status badge, delivery date, items and a progress timeline. */
export function TrackingCard({ order }: { order: OrderStatus }) {
  const { t } = useLanguage();
  const cancelled = order.status === "cancelled";
  const delivered = order.status === "delivered";
  const badge = cancelled
    ? "bg-red-100 text-red-800"
    : delivered
      ? "bg-success/15 text-success"
      : "bg-sun/30 text-brand";

  return (
    <div className="w-full max-w-md overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-brand-muted/20">
      <div className="flex items-center justify-between gap-2 bg-brand px-4 py-2.5 text-sm text-white">
        <span className="flex items-center gap-2 font-semibold">
          <Package className="size-4 text-sun" aria-hidden /> {t.orderNumber(order.order_number)}
        </span>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${badge}`}>
          {order.status_display}
        </span>
      </div>

      <div className="flex flex-col gap-4 p-4 text-sm">
        <p className="text-ink-soft">
          {order.recipient_name && <>{t.forRecipient(order.recipient_name, order.recipient_city)} · </>}
          {t.deliveryLabel} <strong className="text-ink">{order.delivery_date ?? t.toBeConfirmed}</strong>
        </p>

        {order.progress.length > 0 && (
          <ol className="relative ml-2 border-l-2 border-brand-mist">
            {order.progress.map((step, index) => {
              const isLatest = index === order.progress.length - 1;
              return (
                <li key={index} className="relative mb-3 pl-5 last:mb-0">
                  <span
                    aria-hidden
                    className={`absolute top-1 -left-[7px] size-3 rounded-full ring-2 ring-white ${
                      isLatest ? "bg-sun" : "bg-brand-muted"
                    }`}
                  />
                  <p className={isLatest ? "font-semibold text-ink" : "text-ink-soft"}>
                    {step.step}
                  </p>
                  {step.timestamp && <p className="text-xs text-ink-soft">{step.timestamp}</p>}
                </li>
              );
            })}
          </ol>
        )}

        {order.items.length > 0 && (
          <ul className="border-t border-brand-mist pt-3 text-ink-soft">
            {order.items.map((item, index) => (
              <li key={index}>
                {item.quantity} × {item.name}
              </li>
            ))}
          </ul>
        )}

        {(delivered || cancelled) && (
          <p className="flex items-center gap-1.5 text-xs text-ink-soft">
            {delivered ? (
              <CircleCheck className="size-4 text-success" aria-hidden />
            ) : (
              <CircleX className="size-4 text-red-600" aria-hidden />
            )}
            {delivered ? t.delivered : t.cancelled}
          </p>
        )}
      </div>
    </div>
  );
}
