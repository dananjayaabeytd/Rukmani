import Image from "next/image";
import { RotateCcw, ShoppingBag } from "lucide-react";

interface HeaderProps {
  onNewChat: () => void;
  canReset: boolean;
  cartCount: number;
  onOpenCart: () => void;
}

/** Kapruka-purple top bar: logo, Rukmani's name, the cart and a "New chat" button. */
export function Header({ onNewChat, canReset, cartCount, onOpenCart }: HeaderProps) {
  return (
    <header className="bg-brand-logo text-white shadow-md">
      <div className="mx-auto flex h-16 max-w-4xl items-center gap-3 px-4">
        {/* The logo file has its own purple background; the bar uses the same colour. */}
        <Image
          src="/kapruka-logo.webp"
          alt="Kapruka"
          width={2000}
          height={557}
          priority
          className="h-7 w-auto sm:h-9"
        />
        <div className="h-7 w-px bg-white/25" aria-hidden />
        <div className="leading-tight whitespace-nowrap">
          <p className="font-semibold">Rukmani</p>
          <p className="text-xs text-white/70">Your gift concierge</p>
        </div>

        <div className="ml-auto flex items-center gap-2">
          <button
            type="button"
            onClick={onOpenCart}
            aria-label={`Cart, ${cartCount} items`}
            className="relative rounded-full p-2 transition hover:bg-white/10"
          >
            <ShoppingBag className="size-5" aria-hidden />
            {cartCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 flex size-5 items-center justify-center rounded-full bg-sun text-xs font-bold text-brand">
                {cartCount}
              </span>
            )}
          </button>

          <button
            type="button"
            onClick={onNewChat}
            disabled={!canReset}
            aria-label="New chat"
            className="flex items-center gap-1.5 rounded-full border border-white/30 p-2 text-sm transition hover:bg-white/10 disabled:hidden sm:px-3 sm:py-1.5"
          >
            <RotateCcw className="size-4" aria-hidden />
            {/* Icon only on phones, to keep the bar on one line. */}
            <span className="hidden sm:inline">New chat</span>
          </button>
        </div>
      </div>
    </header>
  );
}
