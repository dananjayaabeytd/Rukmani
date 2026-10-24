"use client";

/**
 * "What Rukmani remembers about you": the long-term facts kept for this
 * visitor, each with a Forget button, plus "Forget everything". Customers
 * stay in control of what's remembered.
 */

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Brain, Trash2, X } from "lucide-react";
import { useLanguage } from "@/components/LanguageProvider";
import { forgetEverything, forgetFact, listMemory } from "@/lib/api";
import type { RememberedFact } from "@/lib/types";

interface MemoryPanelProps {
  open: boolean;
  onClose: () => void;
}

export function MemoryPanel({ open, onClose }: MemoryPanelProps) {
  const { t } = useLanguage();
  const [facts, setFacts] = useState<RememberedFact[] | null>(null);
  const [confirmingAll, setConfirmingAll] = useState(false);

  // Load fresh each time the panel opens (memory grows as you chat).
  useEffect(() => {
    if (!open) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect -- reset while loading
    setFacts(null);
    setConfirmingAll(false);
    listMemory().then(setFacts, () => setFacts([]));
  }, [open]);

  async function forget(id: string) {
    setFacts((all) => all?.filter((f) => f.id !== id) ?? null);
    await forgetFact(id).catch(() => undefined);
  }

  async function forgetAll() {
    setFacts([]);
    setConfirmingAll(false);
    await forgetEverything().catch(() => undefined);
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-end justify-center bg-ink/40 sm:items-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.section
            role="dialog"
            aria-label={t.memoryTitle}
            onClick={(event) => event.stopPropagation()}
            className="flex max-h-[85dvh] w-full max-w-lg flex-col overflow-hidden rounded-t-3xl bg-white shadow-2xl sm:rounded-3xl"
            initial={{ y: 40 }}
            animate={{ y: 0 }}
            exit={{ y: 40 }}
          >
            <header className="flex items-start gap-3 bg-brand-logo px-5 py-4 text-white">
              <Brain className="mt-0.5 size-5 shrink-0 text-sun" aria-hidden />
              <div className="flex-1">
                <h2 className="font-semibold">{t.memoryTitle}</h2>
                <p className="mt-1 text-xs text-white/75">{t.memoryIntro}</p>
              </div>
              <button type="button" onClick={onClose} aria-label={t.cancel} className="rounded-full p-1 hover:bg-white/10">
                <X className="size-5" aria-hidden />
              </button>
            </header>

            <div className="flex-1 overflow-y-auto px-5 py-3">
              {facts === null ? (
                <div className="space-y-2 py-2" aria-busy>
                  {[0, 1, 2].map((i) => (
                    <div key={i} className="h-9 animate-pulse rounded-lg bg-brand-mist" />
                  ))}
                </div>
              ) : facts.length === 0 ? (
                <p className="py-6 text-center text-sm text-ink-soft">{t.memoryEmpty}</p>
              ) : (
                <ul className="divide-y divide-brand-mist">
                  {facts.map((fact) => (
                    <li key={fact.id} className="flex items-center gap-3 py-2.5 text-sm text-ink">
                      <span className="flex-1">{fact.text}</span>
                      <button
                        type="button"
                        onClick={() => forget(fact.id)}
                        className="flex shrink-0 items-center gap-1 rounded-full px-2 py-1 text-xs text-ink-soft hover:bg-red-50 hover:text-red-700"
                      >
                        <Trash2 className="size-3.5" aria-hidden />
                        {t.forget}
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {facts && facts.length > 0 && (
              <footer className="border-t border-brand-mist px-5 py-3">
                {confirmingAll ? (
                  <div className="flex items-center gap-2 text-sm">
                    <span className="flex-1 text-red-800">{t.confirmForgetAll}</span>
                    <button type="button" onClick={forgetAll} className="rounded-lg bg-red-600 px-3 py-1 text-xs font-semibold text-white">
                      {t.yes}
                    </button>
                    <button type="button" onClick={() => setConfirmingAll(false)} className="rounded-lg px-3 py-1 text-xs font-semibold">
                      {t.no}
                    </button>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => setConfirmingAll(true)}
                    className="text-sm text-red-700 hover:underline"
                  >
                    {t.forgetAll}
                  </button>
                )}
              </footer>
            )}
          </motion.section>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
