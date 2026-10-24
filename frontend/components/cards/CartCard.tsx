"use client";

import { ShoppingBag } from "lucide-react";
import { useChatActions } from "@/components/chat/ChatActions";
import { formatMoney } from "@/lib/format";
import { useLanguage } from "@/components/LanguageProvider";
import type { Cart, Money } from "@/lib/types";
import { CartLines } from "./CartLines";

/** The cart after a change, shown in the conversation, with a checkout shortcut. */
export function CartCard({ cart, total }: { cart: Cart; total: Money }) {
  const { send, isReplying } = useChatActions();
  const { t } = useLanguage();

  if (cart.items.length === 0) {
    return (
      <p className="flex w-fit items-center gap-2 rounded-2xl bg-white px-4 py-2.5 text-sm text-ink-soft shadow-sm">
        <ShoppingBag className="size-4" aria-hidden /> {t.cartEmpty}
      </p>
    );
  }

  return (
    <div className="w-full max-w-md rounded-2xl bg-white p-4 shadow-sm ring-1 ring-brand-muted/20">
      <p className="flex items-center gap-2 text-sm font-semibold text-brand">
        <ShoppingBag className="size-4" aria-hidden /> {t.yourCart}
      </p>
      <CartLines items={cart.items} />
      <div className="mt-2 flex items-center justify-between border-t border-brand-mist pt-3">
        <span className="text-sm text-ink-soft">
          {t.itemsTotal} <strong className="text-brand">{formatMoney(total)}</strong>
        </span>
        <button
          type="button"
          onClick={() => send(t.msgCheckout)}
          disabled={isReplying}
          className="rounded-full bg-sun px-4 py-1.5 text-sm font-semibold text-brand transition hover:brightness-95 disabled:opacity-50"
        >
          {t.checkout}
        </button>
      </div>
    </div>
  );
}
