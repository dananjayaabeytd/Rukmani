"use client";

import { motion } from "motion/react";
import { useLanguage } from "@/components/LanguageProvider";
import { OccasionBanner } from "./OccasionBanner";
import { RukmaniAvatar } from "./RukmaniAvatar";

interface WelcomeProps {
  onPick: (suggestion: string) => void;
}

/** First screen: a greeting and one-tap suggestions, in the chosen language. */
export function Welcome({ onPick }: WelcomeProps) {
  const { t } = useLanguage();

  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="mx-auto flex max-w-2xl flex-col items-center px-4 pt-12 pb-8 text-center sm:pt-16"
    >
      <RukmaniAvatar size="lg" />
      <h1 className="mt-5 text-2xl font-bold text-brand sm:text-3xl">{t.welcomeTitle}</h1>
      <p className="mt-2 text-base text-brand-light">{t.welcomeLanguages}</p>
      <p className="mt-4 max-w-md text-ink-soft">{t.welcomeIntro}</p>

      <OccasionBanner onPick={onPick} />

      <div className="mt-6 grid w-full gap-3 sm:grid-cols-2">
        {t.suggestions.map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            onClick={() => onPick(suggestion)}
            className="rounded-2xl border border-brand-muted/40 bg-white px-4 py-3 text-left text-sm text-ink shadow-sm transition hover:-translate-y-0.5 hover:border-brand hover:shadow-md"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </motion.section>
  );
}
