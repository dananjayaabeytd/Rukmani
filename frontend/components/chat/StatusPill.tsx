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
      className="flex w-fit items-center gap-2 rounded-full bg-brand-mist px-3 py-1.5 text-sm text-brand"
    >
      <LoaderCircle className="size-4 animate-spin" aria-hidden />
      {label}…
    </div>
  );
}
