"use client";

import { useLanguage } from "@/components/LanguageProvider";

interface RukmaniAvatarProps {
  size?: "sm" | "lg";
}

/**
 * Rukmani's avatar: her initial on Kapruka purple, ringed in the logo's yellow.
 * The initial is in Tamil script when the interface is Tamil, otherwise Sinhala.
 */
export function RukmaniAvatar({ size = "sm" }: RukmaniAvatarProps) {
  const { lang } = useLanguage();
  const sizes = size === "lg" ? "size-20 text-3xl ring-4" : "size-9 text-base ring-2";
  return (
    <div
      aria-hidden
      className={`${sizes} flex shrink-0 items-center justify-center rounded-full bg-brand font-bold text-sun ring-sun`}
    >
      {lang === "ta" ? "ரு" : "රු"}
    </div>
  );
}
