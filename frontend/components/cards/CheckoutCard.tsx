"use client";

/**
 * The checkout summary the customer must confirm before any order exists.
 *
 * Shows who gets what, where and when, the gift card, and the exact total.
 * "Confirm" places the real order (POST /api/checkout) and swaps this card
 * for the pay link. Only the newest summary in the chat can be confirmed;
 * older ones are out of date.
 */

import { useState } from "react";
import { CalendarDays, Globe, LoaderCircle, MapPin, Phone, Truck, User } from "lucide-react";
import { useChatActions } from "@/components/chat/ChatActions";
import { formatDate, formatMoney } from "@/lib/format";
import { useLanguage } from "@/components/LanguageProvider";
import type { CheckoutQuote, Order } from "@/lib/types";
import { CartLines } from "./CartLines";
import { GiftCardPreview } from "./GiftCardPreview";
import { GiftUnboxing } from "./GiftUnboxing";
import { PayCard } from "./PayCard";

interface CheckoutCardProps {
  quote: CheckoutQuote;
  isLatest: boolean;
}

export function CheckoutCard({ quote, isLatest }: CheckoutCardProps) {
  const { confirmCheckout, isReplying } = useChatActions();
  const { t } = useLanguage();
  const [order, setOrder] = useState<Order | null>(null);
  const [placing, setPlacing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (order) {
    return (
      <GiftUnboxing>
        <PayCard order={order} />
      </GiftUnboxing>
    );
  }

  const { details } = quote;
  const sender = details.anonymous ? t.anonymous : details.sender_name;
  // Overseas addresses also show the zone, postcode and country. A Set drops
  // repeats such as city "Dubai" + zone "Dubai".
  const addressParts = [details.address, details.city, details.zone, details.postcode, details.country];
  const fullAddress = [...new Set(addressParts.filter(Boolean))].join(", ");

  async function confirm() {
    setPlacing(true);
    setError(null);
    try {
      setOrder(await confirmCheckout());
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setPlacing(false);
    }
  }

  return (
    <div className="w-full max-w-md overflow-hidden rounded-2xl bg-white shadow-md ring-1 ring-brand-muted/30">
      <div className="bg-brand px-4 py-2.5 text-sm font-semibold text-white">
        {t.checkYourOrder}
      </div>

      <div className="flex flex-col gap-4 p-4 text-sm">
        <section className="flex flex-col gap-1.5 text-ink">
          <Line icon={<User className="size-4" />}>{details.recipient_name}</Line>
          <Line icon={<Phone className="size-4" />}>{details.recipient_phone}</Line>
          <Line icon={<MapPin className="size-4" />}>{fullAddress}</Line>
          <Line icon={<CalendarDays className="size-4" />}>
            {formatDate(details.delivery_date, t.locale)}
          </Line>
          {details.delivery_type === "economy" && (
            <Line icon={<Truck className="size-4" />}>
              {t.economyDelivery}
              {quote.delivery_promise && ` · ${quote.delivery_promise}`}
            </Line>
          )}
          {details.delivery_type === "international_gift" && details.country && (
            <Line icon={<Globe className="size-4" />}>{t.deliveredAbroad(details.country)}</Line>
          )}
        </section>

        {details.gift_message && (
          <GiftCardPreview message={details.gift_message} to={details.recipient_name} from={sender} />
        )}

        <CartLines items={quote.cart.items} />

        <dl className="grid grid-cols-2 gap-y-1 border-t border-brand-mist pt-3">
          <dt className="text-ink-soft">{t.items}</dt>
          <dd className="text-right">{formatMoney(quote.items_total)}</dd>
          <dt className="text-ink-soft">{t.delivery}</dt>
          <dd className="text-right">{formatMoney(quote.delivery_fee)}</dd>
          <dt className="font-semibold text-ink">{t.total}</dt>
          <dd className="text-right text-base font-bold text-brand">
            {formatMoney(quote.grand_total)}
          </dd>
        </dl>

        {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-red-800">{error}</p>}

        {isLatest ? (
          <button
            type="button"
            onClick={confirm}
            disabled={placing || isReplying}
            className="flex items-center justify-center gap-2 rounded-full bg-sun py-2.5 font-semibold text-brand transition hover:brightness-95 disabled:opacity-60"
          >
            {placing && <LoaderCircle className="size-4 animate-spin" aria-hidden />}
            {placing ? t.placing : t.confirm}
          </button>
        ) : (
          <p className="text-center text-xs text-ink-soft">
            {t.outdated}
          </p>
        )}
      </div>
    </div>
  );
}

function Line({ icon, children }: { icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <p className="flex items-start gap-2">
      <span className="mt-0.5 text-brand-light" aria-hidden>
        {icon}
      </span>
      <span>{children}</span>
    </p>
  );
}
