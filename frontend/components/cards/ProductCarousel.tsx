import type { Product } from "@/lib/types";
import { ProductCard } from "./ProductCard";

/** Search results as a row of cards that scrolls sideways (swipe on mobile). */
export function ProductCarousel({ products }: { products: Product[] }) {
  return (
    <div className="no-scrollbar -mx-1 flex snap-x snap-mandatory gap-3 overflow-x-auto px-1 pb-2">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
