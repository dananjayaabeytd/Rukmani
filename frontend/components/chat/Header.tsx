"use client";

import Image from "next/image";
import { Menu, ShoppingBag } from "lucide-react";
import { LANGUAGES } from "@/lib/i18n";
import { useLanguage } from "@/components/LanguageProvider";

interface HeaderProps {
  /** Phones: open the chat list (on desktop it's always visible). */
  onOpenChats: () => void;
  cartCount: number;
  onOpenCart: () => void;
}

/** Kapruka-purple top bar: chat-list button (phones), logo, Rukmani's name, language and cart. */
export function Header({ onOpenChats, cartCount, onOpenCart }: HeaderProps) {
  const { lang, setLang, t } = useLanguage();

  return (
    <header className="bg-brand-logo text-white shadow-md">
      <div className="mx-auto flex h-16 max-w-4xl items-center gap-2 px-3 sm:gap-3 sm:px-4">
        <button
          type="button"
          onClick={onOpenChats}
          aria-label={t.openChats}
          className="-ml-1 rounded-full p-2 transition hover:bg-white/10 md:hidden"
        >
          <Menu className="size-5" aria-hidden />
        </button>

        {/* The logo file has its own purple background; the bar uses the same colour. */}
        <Image
          src="/kapruka-logo.webp"
          alt="Kapruka"
          width={2000}
          height={557}
          priority
          className="h-6 w-auto sm:h-9"
        />
        <div className="hidden h-7 w-px bg-white/25 sm:block" aria-hidden />
        <div className="hidden leading-tight whitespace-nowrap sm:block">
          <p className="font-semibold">{t.name}</p>
          <p className="text-xs text-white/70">{t.tagline}</p>
        </div>

        <div className="ml-auto flex items-center gap-1.5 sm:gap-2">
          {/* Interface language */}
          <div className="flex rounded-full bg-white/10 p-0.5 text-xs" role="group" aria-label="Language">
            {LANGUAGES.map(({ code, label }) => (
              <button
                key={code}
                type="button"
                onClick={() => setLang(code)}
                aria-pressed={lang === code}
                className={`rounded-full px-2 py-1 transition ${
                  lang === code ? "bg-sun font-semibold text-brand" : "text-white/80 hover:text-white"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          <button
            type="button"
            onClick={onOpenCart}
            aria-label={t.cartLabel(cartCount)}
            className="relative rounded-full p-2 transition hover:bg-white/10"
          >
            <ShoppingBag className="size-5" aria-hidden />
            {cartCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 flex size-5 items-center justify-center rounded-full bg-sun text-xs font-bold text-brand">
                {cartCount}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
