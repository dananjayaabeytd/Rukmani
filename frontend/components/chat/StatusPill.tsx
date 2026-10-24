"use client";

import { LoaderCircle } from "lucide-react";
import { statusKeyFor } from "@/lib/i18n";
import { useLanguage } from "@/components/LanguageProvider";

/**
 * Shows what Rukmani is doing right now, e.g. "Searching Kapruka for gifts…",
 * in the chosen language. `status` is "thinking" or the running tool's name.
 */
export function StatusPill({ status }: { status: string }) {
  const { t } = useLanguage();
  const label = status === "thinking" ? t.status.thinking : t.status[statusKeyFor(status)];

  return (
    <div
      role="status"
      className="relative flex w-fit items-center gap-2 overflow-hidden rounded-full bg-white/80 px-3 py-1.5 text-sm text-brand shadow-md shadow-brand/10 ring-1 ring-brand-muted/30 backdrop-blur-xl"
    >
      <span aria-hidden className="animate-shimmer absolute inset-0" />
      <LoaderCircle className="relative size-4 animate-spin text-brand-light" aria-hidden />
      <span className="relative">{label}…</span>
    </div>
  );
}
