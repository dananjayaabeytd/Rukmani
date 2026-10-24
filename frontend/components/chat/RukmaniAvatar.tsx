"use client";

import { RukmaniFace } from "./RukmaniFace";

interface RukmaniAvatarProps {
  size?: "sm" | "lg";
}

/**
 * Rukmani's avatar: her cartoon face, ringed in the logo's yellow.
 * The large one (welcome screen) has a slowly turning gold glow around it.
 */
export function RukmaniAvatar({ size = "sm" }: RukmaniAvatarProps) {
  if (size === "lg") {
    return (
      <div aria-hidden className="relative size-24">
        <div className="animate-spin-slow absolute -inset-1.5 rounded-full bg-[conic-gradient(from_0deg,var(--color-sun),var(--color-brand-light),var(--color-gold),var(--color-brand-light),var(--color-sun))] opacity-80 blur-md" />
        <RukmaniFace className="relative size-24 rounded-full ring-4 ring-sun" />
      </div>
    );
  }

  return (
    <RukmaniFace className="size-9 shrink-0 rounded-full shadow-md shadow-brand/30 ring-2 ring-sun" />
  );
}
