"use client";

import Image from "next/image";
import { ExternalLink, MapPin } from "lucide-react";
import { formatMoney } from "@/lib/format";
import { useLanguage } from "@/components/LanguageProvider";
import type { ProductDetail } from "@/lib/types";

/** A closer look at one product, including where it can be delivered. */
export function ProductDetailCard({ product }: { product: ProductDetail }) {
  const { t } = useLanguage();
  const limitedDelivery = product.delivery && !product.delivery.island_wide;
  // Kapruka descriptions contain long runs of spaces; tidy them for display.
  const description = product.description.replace(/\s+/g, " ").trim();

  return (
    <div className="flex max-w-xl gap-4 rounded-2xl bg-white p-3 shadow-sm ring-1 ring-brand-muted/20">
      {product.image_url && (
        <div className="relative size-28 shrink-0 overflow-hidden rounded-xl bg-brand-mist sm:size-36">
          <Image src={product.image_url} alt={product.name} fill sizes="144px" className="object-cover" />
        </div>
      )}

      <div className="flex min-w-0 flex-col gap-1.5">
        <h3 className="font-semibold text-ink">{product.name}</h3>
        <p className="font-bold text-brand">{formatMoney(product.price)}</p>
        <p className="line-clamp-3 text-sm text-ink-soft">{description}</p>

        <p className="flex items-center gap-1 text-xs text-ink-soft">
          <MapPin className="size-3.5 text-brand-light" aria-hidden />
          {limitedDelivery
            ? t.limitedCities(product.delivery?.deliverable_city_count ?? "")
            : t.islandWide}
        </p>

        <a
          href={product.url}
          target="_blank"
          rel="noreferrer"
          className="mt-1 flex w-fit items-center gap-1 rounded-full bg-brand px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-deep"
        >
          {t.openOnKapruka} <ExternalLink className="size-3" aria-hidden />
        </a>
      </div>
    </div>
  );
}
