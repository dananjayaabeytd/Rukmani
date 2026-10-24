"use client";

import { CalendarCheck, CalendarClock, CircleAlert, Truck } from "lucide-react";
import { formatDate, formatMoney } from "@/lib/format";
import { useLanguage } from "@/components/LanguageProvider";
import type { DeliveryCheck } from "@/lib/types";
import { DateStrip } from "./DateStrip";

interface DeliveryCardProps {
  delivery: DeliveryCheck;
  productId: string | null;
}

/**
 * The result of a delivery check: can it arrive on the date asked for,
 * and if not, the next date that works. Plus the fee, any warning, and a
 * strip of upcoming days to check another date with one tap.
 */
export function DeliveryCard({ delivery, productId }: DeliveryCardProps) {
  const { t } = useLanguage();
  // This card comes from Sri Lanka delivery checks, which always name a city.
  const city = delivery.city ?? "";
  const notDeliverable = delivery.item_deliverable === false;
  const deliveryDate = delivery.available
    ? delivery.checked_date
    : delivery.next_available_date;

  // Without a cart Kapruka only knows the maximum fee, so say "Up to".
  const fee =
    delivery.delivery_fee === null
      ? null
      : `${delivery.fee_basis === "max" ? t.upTo : ""}${formatMoney({
          amount: delivery.delivery_fee,
          currency: delivery.fee_currency,
        })}`;

  return (
    <div className="w-full max-w-md overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-brand-muted/20">
      <div className="flex items-center gap-2 bg-brand px-4 py-2 text-sm font-medium text-white">
        <Truck className="size-4 text-sun" aria-hidden />
        {t.deliveryTo(city)}
      </div>

      <div className="flex flex-col gap-2 p-4 text-sm">
        {notDeliverable ? (
          <Row icon={<CircleAlert className="size-5 text-red-600" />}>
            {t.notDelivered(city)}
          </Row>
        ) : delivery.available ? (
          <Row icon={<CalendarCheck className="size-5 text-success" />}>
            {t.canArrive} <strong>{formatDate(delivery.checked_date, t.locale)}</strong>
          </Row>
        ) : (
          <Row icon={<CalendarClock className="size-5 text-gold" />}>
            {t.dateFull(formatDate(delivery.checked_date, t.locale))}
            {deliveryDate && (
              <>
                {" "}
                {t.earliest} <strong>{formatDate(deliveryDate, t.locale)}</strong>
              </>
            )}
          </Row>
        )}

        {fee && !notDeliverable && (
          <p className="text-ink-soft">
            {t.deliveryFee} <span className="font-semibold text-brand">{fee}</span>
          </p>
        )}

        {!notDeliverable && (
          <DateStrip
            city={city}
            productId={productId}
            checkedDate={delivery.checked_date}
            available={delivery.available}
            nextAvailableDate={delivery.next_available_date}
          />
        )}

        {notDeliverable && delivery.deliverable_cities.length > 0 && (
          <p className="text-ink-soft">
            {t.canGoTo} {delivery.deliverable_cities.slice(0, 8).join(", ")}
            {delivery.deliverable_cities.length > 8 && t.andMore}
          </p>
        )}

        {delivery.perishable_warning && (
          <p className="rounded-lg bg-sun/20 px-3 py-2 text-xs text-ink">
            {delivery.perishable_warning}
          </p>
        )}
      </div>
    </div>
  );
}

function Row({ icon, children }: { icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <p className="flex items-center gap-2 text-ink">
      <span aria-hidden>{icon}</span>
      <span>{children}</span>
    </p>
  );
}
