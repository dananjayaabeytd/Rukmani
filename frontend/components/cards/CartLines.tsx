"use client";

import Image from "next/image";
import { Gift, X } from "lucide-react";
import { formatMoney } from "@/lib/format";
import { useLanguage } from "@/components/LanguageProvider";
import type { CartItem } from "@/lib/types";

interface CartLinesProps {
  items: CartItem[];
  /** When given, each line gets a remove button. */
  onRemove?: (item: CartItem) => void;
  disabled?: boolean;
}

/** The list of items in a cart: photo, name, quantity, icing text and line price. */
export function CartLines({ items, onRemove, disabled }: CartLinesProps) {
  const { t } = useLanguage();
  return (
    <ul className="divide-y divide-brand-mist">
      {items.map((item) => (
        <li key={item.product_id} className="flex items-center gap-3 py-2.5">
          <div className="relative size-12 shrink-0 overflow-hidden rounded-lg bg-brand-mist">
            {item.image_url ? (
              <Image src={item.image_url} alt="" fill sizes="48px" className="object-cover" />
            ) : (
              <Gift className="absolute inset-0 m-auto size-5 text-brand-muted" aria-hidden />
            )}
          </div>

          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-ink">{item.name}</p>
            <p className="text-xs text-ink-soft">
              {item.quantity} × {formatMoney(item.price)}
              {item.icing_text && <> · {t.icing}: “{item.icing_text}”</>}
            </p>
          </div>

          <span className="text-sm font-semibold text-brand">
            {formatMoney({
              amount: (item.price.amount ?? 0) * item.quantity,
              currency: item.price.currency,
            })}
          </span>

          {onRemove && (
            <button
              type="button"
              onClick={() => onRemove(item)}
              disabled={disabled}
              aria-label={t.remove(item.name)}
              className="rounded-full p-1 text-ink-soft transition hover:bg-brand-mist hover:text-brand disabled:opacity-40"
            >
              <X className="size-4" aria-hidden />
            </button>
          )}
        </li>
      ))}
    </ul>
  );
}
