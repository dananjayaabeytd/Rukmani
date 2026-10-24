import Image from "next/image";
import { ExternalLink, Gift } from "lucide-react";
import { formatMoney } from "@/lib/format";
import type { Product } from "@/lib/types";

/** One product: photo, name, price (with the old price when on sale), and a link to Kapruka. */
export function ProductCard({ product }: { product: Product }) {
  const onSale = product.compare_at_price !== null;

  return (
    <a
      href={product.url}
      target="_blank"
      rel="noreferrer"
      className="group flex w-44 shrink-0 snap-start flex-col overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-brand-muted/20 transition hover:-translate-y-1 hover:shadow-lg sm:w-52"
    >
      <div className="relative aspect-square bg-brand-mist">
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
      </div>

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
        <span className="flex items-center gap-1 text-xs text-brand-light opacity-80 group-hover:opacity-100">
          View on Kapruka <ExternalLink className="size-3" aria-hidden />
        </span>
      </div>
    </a>
  );
}
