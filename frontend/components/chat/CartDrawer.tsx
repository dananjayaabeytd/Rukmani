"use client";

/** Slide-in panel with the current cart, opened from the bag icon in the header. */

import { AnimatePresence, motion } from "motion/react";
import { ShoppingBag, X } from "lucide-react";
import { CartLines } from "@/components/cards/CartLines";
import { formatMoney } from "@/lib/format";
import { useLanguage } from "@/components/LanguageProvider";
import type { Cart } from "@/lib/types";
import { useChatActions } from "./ChatActions";

interface CartDrawerProps {
  open: boolean;
  cart: Cart;
  onClose: () => void;
}

export function CartDrawer({ open, cart, onClose }: CartDrawerProps) {
  const { send, isReplying } = useChatActions();
  const { t } = useLanguage();
  const total = cart.items.reduce((sum, i) => sum + (i.price.amount ?? 0) * i.quantity, 0);

  // Cart changes go through Rukmani, so she always knows what's in the cart.
  function ask(text: string) {
    send(text);
    onClose();
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 z-40 bg-ink/40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.aside
            role="dialog"
            aria-label={t.yourCart}
            className="fixed inset-y-0 right-0 z-50 flex w-full max-w-sm flex-col bg-white shadow-2xl"
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
          >
            <div className="flex items-center justify-between bg-brand-logo px-4 py-4 text-white">
              <p className="flex items-center gap-2 font-semibold">
                <ShoppingBag className="size-5" aria-hidden /> {t.yourCart}
              </p>
              <button type="button" onClick={onClose} aria-label={t.closeCart} className="rounded-full p-1 hover:bg-white/10">
                <X className="size-5" aria-hidden />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto px-4">
              {cart.items.length === 0 ? (
                <p className="py-10 text-center text-ink-soft">
                  {t.drawerEmpty}
                </p>
              ) : (
                <CartLines
                  items={cart.items}
                  disabled={isReplying}
                  onRemove={(item) => ask(t.msgRemove(item.name, item.product_id))}
                />
              )}
            </div>

            {cart.items.length > 0 && (
              <div className="border-t border-brand-mist p-4">
                <p className="mb-3 flex justify-between text-sm">
                  <span className="text-ink-soft">{t.itemsTotal}</span>
                  <strong className="text-brand">{formatMoney({ amount: total, currency: "LKR" })}</strong>
                </p>
                <button
                  type="button"
                  onClick={() => ask(t.msgCheckout)}
                  disabled={isReplying}
                  className="w-full rounded-full bg-sun py-2.5 font-semibold text-brand transition hover:brightness-95 disabled:opacity-50"
                >
                  {t.checkoutWithRukmani}
                </button>
              </div>
            )}
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
