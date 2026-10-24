"use client";

import Image from "next/image";
import { ExternalLink, Gift, Plus } from "lucide-react";
import { useChatActions } from "@/components/chat/ChatActions";
import { formatMoney } from "@/lib/format";
import type { Product } from "@/lib/types";

/**
 * One product: photo, name, price (with the old price when on sale),
 * an "Add to cart" button and a link to the product on Kapruka.
 */
export function ProductCard({ product }: { product: Product }) {
  const { send, isReplying } = useChatActions();
  const onSale = product.compare_at_price !== null;

  // Adding goes through Rukmani (as a message), so she knows the cart and can
  // ask about icing text for cakes. The id makes it unambiguous for her.
  function addToCart() {
    send(`Add "${product.name}" (${product.id}) to my cart`);
  }

  return (
    <div className="group flex w-44 shrink-0 snap-start flex-col overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-brand-muted/20 transition hover:-translate-y-1 hover:shadow-lg sm:w-52">
      <a href={product.url} target="_blank" rel="noreferrer" className="relative aspect-square bg-brand-mist">
        {product.image_url ? (
          <Image
            src={product.image_url}
            alt={product.name}
            fill
            sizes="(min-width: 640px) 208px, 176px"
            className="object-cover transition duration-300 group-hover:scale-105"
          />
        ) : (
          <Gift className="absolute inset-0 m-auto size-10 text-brand-muted" aria-hidden />
        )}
        {/* No low-stock badge: Kapruka reports almost every item as "low", so it would be noise. */}
        {onSale && (
          <span className="absolute top-2 right-2 rounded-full bg-sun px-2 py-0.5 text-xs font-bold text-brand">
            Sale
          </span>
        )}
      </a>

      <div className="flex flex-1 flex-col gap-1 p-3">
        <h3 className="line-clamp-2 text-sm font-medium text-ink">{product.name}</h3>
        <div className="mt-auto flex items-baseline gap-2 pt-1">
          <span className="font-bold text-brand">{formatMoney(product.price)}</span>
          {onSale && (
            <span className="text-xs text-ink-soft line-through">
              {formatMoney(product.compare_at_price)}
            </span>
          )}
        </div>

        <button
          type="button"
          onClick={addToCart}
          disabled={isReplying}
          className="mt-1 flex items-center justify-center gap-1 rounded-full bg-brand py-1.5 text-xs font-semibold text-white transition hover:bg-brand-deep disabled:opacity-50"
        >
          <Plus className="size-3.5" aria-hidden /> Add to cart
        </button>
        <a
          href={product.url}
          target="_blank"
          rel="noreferrer"
          className="flex items-center justify-center gap-1 text-xs text-brand-light hover:underline"
        >
          View on Kapruka <ExternalLink className="size-3" aria-hidden />
        </a>
      </div>
    </div>
  );
}
