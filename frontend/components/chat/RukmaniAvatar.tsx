"use client";

import { useLanguage } from "@/components/LanguageProvider";

interface RukmaniAvatarProps {
  size?: "sm" | "lg";
}

/**
 * Rukmani's avatar: her initial on Kapruka purple, ringed in the logo's yellow.
 * The large one (welcome screen) has a slowly turning gold glow around it.
 * The initial is in Tamil script when the interface is Tamil, otherwise Sinhala.
 */
export function RukmaniAvatar({ size = "sm" }: RukmaniAvatarProps) {
  const { lang } = useLanguage();
  const initial = lang === "ta" ? "ரு" : "රු";

  if (size === "lg") {
    return (
      <div aria-hidden className="relative size-24">
        <div className="animate-spin-slow absolute -inset-1.5 rounded-full bg-[conic-gradient(from_0deg,var(--color-sun),var(--color-brand-light),var(--color-gold),var(--color-brand-light),var(--color-sun))] opacity-80 blur-md" />
        <div className="relative flex size-24 items-center justify-center rounded-full bg-linear-to-br from-brand-light to-brand-deep text-4xl font-bold text-sun ring-4 ring-sun">
          {initial}
        </div>
      </div>
    );
  }

  return (
    <div
      aria-hidden
      className="flex size-9 shrink-0 items-center justify-center rounded-full bg-linear-to-br from-brand-light to-brand-deep text-base font-bold text-sun shadow-md shadow-brand/30 ring-2 ring-sun"
    >
      {initial}
    </div>
  );
}
